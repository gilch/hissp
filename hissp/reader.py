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
from typing import Any, Iterable, Iterator, NewType, Tuple, Union

from hissp.compiler import Compiler, readerless
from hissp.munger import munge

TOKENS = re.compile(
    r"""(?x)
 (?P<open>\()
|(?P<close>\))
|(?P<string>"(?:\\.|\\\n|[^"]|\\")*")
|(?P<comment>;.*)
|(?P<whitespace>[\n ]+)
|(?P<macro>
   ,@
  |['`,]
  |\\[^ \n"()\\]*(?=[\n ("\\]))
|(?P<symbol>[^ \n"()\\]+)
"""
)

Token = NewType("Token", Tuple[str, str])

DROP = object()


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


class _Unquote(tuple):
    def __repr__(self):
        return f"_Unquote{super().__repr__()}"


class Parser:
    def __init__(self, qualname="_repl", ns=None, verbose=False, evaluate=False):
        self.qualname = qualname
        self.ns = ns or {"__name__": "<compiler>"}
        self.compiler = Compiler(self.qualname, self.ns, evaluate)
        self.verbose = verbose

    def parse(self, tokens: Iterator[Token], depth: int = 0) -> Iterator:
        yield from (form for form in self._parse(tokens, depth) if form is not DROP)

    def _parse(self, tokens: Iterator[Token], depth: int) -> Iterator:
        for k, v in tokens:
            if k == "open":
                yield (*self.parse(tokens, depth + 1),)
            elif k == "close":
                return
            elif k == "string":
                yield "quote", ast.literal_eval(v.replace("\n", r"\n"))
            elif k in {"comment", "whitespace"}:
                continue
            elif k == "macro":
                form = next(self.parse(tokens))
                yield self.parse_macro(v, form)
            elif k == "symbol":
                try:
                    yield ast.literal_eval(v)
                except (ValueError, SyntaxError):
                    yield munge(v)
            else:
                assert False, "unknown token: " + repr(k)
        if depth:
            SyntaxError("Ran out of tokens before completing form.")

    def parse_macro(self, tag: str, form):
        if tag == "'":
            return "quote", form
        if tag == "`":
            return self.template(form)
        if tag == ",":
            return _Unquote([":_", form])
        if tag == ",@":
            return _Unquote([":*", form])

        assert tag.startswith("\\")
        tag = tag[1:]
        if tag == "_":
            return DROP
        if tag == ".":
            return eval(readerless(form), {})
        if ".." in tag and not tag.startswith(".."):
            module, function = tag.split("..", 1)
            function = munge(function)
            return reduce(getattr, function.split("."), import_module(module))(form)
        raise ValueError(f"Unknown reader macro {tag}")

    def template(self, form):
        case = type(form)
        if case is tuple and form:
            return (
                ("lambda", (":", ":*", "a"), "a"),
                ":",
                *chain(*self._template(form)),
            )
        if case is str and not form.startswith(":"):
            return "quote", self.qualify(form)
        if case is _Unquote and form[0] == ":_":
            return form[1]
        return form

    def _template(self, forms: Iterable) -> Iterable[Tuple[str, Any]]:
        for form in forms:
            case = type(form)
            if case is str and not form.startswith(":"):
                yield ":_", ("quote", self.qualify(form))
            elif case is _Unquote:
                yield form
            elif case is tuple:
                yield ":_", self.template(form)
            else:
                yield ":_", form

    def qualify(self, symbol: str) -> str:
        if ".." in symbol or symbol.startswith(".") or symbol in {"quote", "lambda"}:
            return symbol
        if symbol in vars(self.ns.get("_macro_", lambda: ())):
            return f"{self.qualname}.._macro_.{symbol}"
        return f"{self.qualname}..{symbol}"

    def reads(self, code: str) -> Iterable:
        res = self.parse(lex(code))
        if self.verbose:
            res = list(res)
            pprint(res)
        return res

    def compile(self, code: str) -> str:
        hissp = self.reads(code)
        return self.compiler.compile(hissp)


def transpile(package: resources.Package, *modules: Union[str, PurePath]):
    for module in modules:
        transpile_module(package, module + ".hissp")


def transpile_module(
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
            print('writing to', out)
            f.write(Parser(qualname, evaluate=True).compile(code))
