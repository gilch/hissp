# Copyright 2019 Matthew Egan Odendahl
# SPDX-License-Identifier: Apache-2.0

import ast
import os
import re
from functools import reduce
from importlib import import_module, resources
from itertools import chain
from pathlib import Path, PurePath
from pprint import pprint
from types import ModuleType
from typing import Iterator, NewType, Tuple, Union

from hissp.compiler import Compiler, readerless
from hissp.munger import munge

TOKENS = re.compile(
    r"""(?x)
 (?P<open>\()
|(?P<close>\))
|(?P<string>"(?:\\.|\\\n|[^"]|\\")*")
|(?P<comment>;.*)
|(?P<whitespace>[\n ]+)
|(?P<macro>\\[^ \n"()\\]*(?=[\n ("\\]))
|(?P<symbol>[^ \n"()\\]+)
"""
)

Token = NewType("Token", Tuple[str, str])


def lex(code: str) -> Iterator[Token]:
    pos = 0
    while pos < len(code):
        match = TOKENS.match(code, pos)
        if match is None:
            lines = code.split("\n")
            good = code[0:pos].split("\n")
            line = len(good)
            column = len(good[-1])
            raise SyntaxError(
                f"""\
Unexpected token at {line}:{column}
{lines[line-1]}
{" "*column}^
"""
            )
        assert match.end() > pos, match.groups()
        pos = match.end()
        yield Token((match.lastgroup, match.group()))


def parse(tokens: Iterator[Token], depth=0) -> Iterator[tuple]:
    for k, v in tokens:
        if k == "open":
            yield (*parse(tokens, depth + 1),)
        elif k == "close":
            return
        elif k == "string":
            yield "quote", ast.literal_eval(v.replace("\n", r"\n"))
        elif k in {"comment", "whitespace"}:
            continue
        elif k == "macro":
            form = next(parse(tokens))
            yield parse_macro(v, form)
        elif k == "symbol":
            try:
                yield ast.literal_eval(v)
            except (ValueError, SyntaxError):
                yield munge(v)
        else:
            assert False, "unknown token: " + repr(k)
    if depth:
        SyntaxError("Ran out of tokens before completing form.")


class _Unquote(tuple):
    def __repr__(self):
        return f"_Unquote{super().__repr__()}"


def parse_macro(tag: str, form) -> Iterator[tuple]:
    assert tag.startswith("\\")
    tag = tag[1:]
    if tag == "'":
        return "quote", form
    if tag == ".":
        return eval(readerless(form), {})
    if tag == "`":
        return template(form)
    if tag == ",":
        return _Unquote([":_", form])
    if tag == ",@":
        return _Unquote([":*", form])
    if ".." in tag and not tag.startswith(".."):
        module, function = tag.split("..", 1)
        function = munge(function)
        return reduce(getattr, function.split("."), import_module(module))(form)
    raise ValueError(f"Unknown reader macro {tag}")


def template(form):
    case = type(form)
    if case is tuple and form:
        return (("lambda", (":", ":*", "a"), "a"), ":", *chain(*_template(form)))
    if case is str and not form.startswith(':'):
        return "quote", form
    return form


def _template(forms):
    for form in forms:
        case = type(form)
        if case is str and not form.startswith(':'):
            yield ":_", ("quote", form)
        elif case is _Unquote:
            yield form
        elif case is tuple:
            yield ":_", template(form)
        else:
            yield ":_", form


def reads(code, verbose=False):
    res = parse(lex(code))
    if verbose:
        res = list(res)
        pprint(res)
    return res


def transpile(
    package: resources.Package,
    resource: Union[str, PurePath],
    out: Union[None, str, bytes, Path] = None,
):
    code = resources.read_text(package, resource)
    path: Path
    with resources.path(package, resource) as path:
        out = out or path.with_suffix(".py")
        if isinstance(package, ModuleType):
            package = package.__package__
        if isinstance(package, os.PathLike):
            resource = resource.stem
        qualname = f"{package}.{resource.split('.')[0]}"
        with open(out, "w") as f:
            f.write(Compiler(qualname).compile(reads(code)))
