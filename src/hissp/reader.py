# Copyright 2019, 2020 Matthew Egan Odendahl
# SPDX-License-Identifier: Apache-2.0

import ast
import builtins
import os
import re
import sys
from contextlib import contextmanager, nullcontext
from functools import reduce
from importlib import import_module, resources
from itertools import chain
from pathlib import Path, PurePath
from pprint import pprint
from types import ModuleType
from typing import Any, Iterable, Iterator, NewType, Optional, Tuple, Union
from unittest.mock import ANY

from hissp.compiler import Compiler, readerless
from hissp.munger import munge

TOKENS = re.compile(
    r"""(?x)
 (?P<open>\()
|(?P<close>\))
|(?P<string>
  b?  # bytes?
  "  # Open quote.
    (?:[^"\\]  # Any non-magic character.
       |\\(?:.|\n)  # Backslash only if paired, including with newline.
    )*  # Zero or more times.
  "  # Close quote.
 )
|(?P<comment>;.*)
|(?P<whitespace>[\n ]+)
|(?P<badspace>\s)  # Other whitespace not allowed.
|(?P<macro>
   ,@
  |['`,]
   # Any atom that ends in (an unescaped) ``#``
  |(?:[^\\ \n"();#]|\\.)+[#]
 )
|(?P<atom>(?:[^\\ \n"();]|\\.)+)  # Let Python deal with it.
|(?P<continue>")
|(?P<error>.)
"""
)

Token = NewType("Token", Tuple[str, str])

DROP = object()


def lex(code: str, file: str = "<?>") -> Iterator[Token]:
    pos = 0
    while pos < len(code):
        match = TOKENS.match(code, pos)
        if match is None:
            good = code[0:pos].split("\n")
            line = len(good)
            column = len(good[-1])
            raise SyntaxError("Unexpected token", (file, line, column, code))
        assert match.lastgroup
        assert match.end() > pos, match.groups()
        pos = match.end()
        yield Token((match.lastgroup, match.group()))


class _Unquote(tuple):
    def __repr__(self):
        return f"_Unquote{super().__repr__()}"


def gensym_counter(count=[0]):
    count[0] += 1
    return count[0]


class Parser:
    def __init__(
        self, qualname="__main__", ns=..., verbose=False, evaluate=False, filename="<?>"
    ):
        self.qualname = qualname
        self.ns = {"__name__": qualname} if ns is ... else ns
        self.compiler = Compiler(self.qualname, self.ns, evaluate)
        self.verbose = verbose
        self.filename = filename
        self.reinit()

    def reinit(self):
        self.gensym_stack = []
        self.depth = 0

    def parse(self, tokens: Iterator[Token]) -> Iterator:
        return (form for form in self._parse(tokens) if form is not DROP)

    def _parse(self, tokens: Iterator[Token]) -> Iterator:
        for k, v in tokens:
            if k == "open":
                yield from self._open(tokens)
            elif k == "close":
                self._close()
                return
            elif k == "string":
                yield from self._string(v)
            elif k in {"comment", "whitespace"}:
                continue
            elif k == "macro":
                yield from self._macro(tokens, v)
            elif k == "atom":
                yield self._atom(v)
            elif k == "badspace":
                raise ValueError("Bad space: " + repr(v))
            elif k == "continue":
                raise SyntaxError("Incomplete token.")
            elif k == "error":
                raise ValueError("Read error: " + repr(v))
            else:
                assert False, "unknown token: " + repr(k)
        if self.depth:
            raise SyntaxError("Ran out of tokens before completing form.")

    def _open(self, tokens):
        depth = self.depth
        self.depth += 1
        yield (*self.parse(tokens),)
        if self.depth != depth:
            raise SyntaxError("Unclosed '('.")

    def _close(self):
        self.depth -= 1
        if self.depth < 0:
            raise ValueError("Unopened ')'.")

    @staticmethod
    def _string(v):
        v = v.replace("\\\n", "").replace("\n", r"\n")
        val = ast.literal_eval(v)
        if v[0] == 'b':  # bytes
            yield val
        else:
            yield "quote", val, {":str": True}

    def _macro(self, tokens, v):
        with {
            "`": self.gensym_context,
            ",": self.unquote_context,
            ",@": self.unquote_context,
        }.get(v, nullcontext)():
            try:
                form = next(self.parse(tokens))
            except StopIteration:
                raise ValueError(f"Reader macro {v!r} missing argument.") from None
            yield self.parse_macro(v, form)

    @staticmethod
    def _atom(v):
        symbol = v[0] == '\\'
        v = v.replace(r'\.', 'xFULLxSTOP_')
        v = re.sub(r'\\(.)', lambda m: m[1], v)
        if symbol:
            return munge(v)
        try:
            val = ast.literal_eval(v)
            if isinstance(val, bytes):  # bytes have their own literals.
                return munge(v)
            return val
        except (ValueError, SyntaxError):
            return munge(v)

    def parse_macro(self, tag: str, form):
        if tag == "'":
            return "quote", form
        if tag == "`":
            return self.template(form)
        if tag == ",":
            return _Unquote([":?", form])
        if tag == ",@":
            return _Unquote([":*", form])

        assert tag.endswith("#")
        tag = tag[:-1]
        if tag == "_":
            return DROP
        if tag == "$":
            return self.gensym(form)
        if tag == ".":
            return eval(readerless(form), {})
        if ".." in tag and not tag.startswith(".."):
            module, function = tag.split("..", 1)
            function = munge(function)
            if is_string(form):
                form = form[1]
            return reduce(getattr, function.split("."), import_module(module))(form)
        # TODO: consider unqualified reader macros.
        raise ValueError(f"Unknown reader macro {tag}")

    def template(self, form):
        case = type(form)
        if case is tuple and form:
            if is_string(form):
                return "quote", form
            return (
                ("lambda", (":", ":*", "xAUTO0_"), "xAUTO0_"),
                ":",
                *chain(*self._template(form)),
            )
        if case is str and not form.startswith(":"):
            return "quote", self.qualify(form)
        if case is _Unquote and form[0] == ":?":
            return form[1]
        return form

    def _template(self, forms: Iterable) -> Iterable[Tuple[str, Any]]:
        for form in forms:
            case = type(form)
            if case is str and not form.startswith(":"):
                yield ":?", ("quote", self.qualify(form))
            elif case is _Unquote:
                yield form
            elif case is tuple:
                yield ":?", self.template(form)
            else:
                yield ":?", form

    def qualify(self, symbol: str) -> str:
        if re.search(r"^\.|\.$|^quote$|^lambda$|^__import__$|xAUTO\d+_$|\.\.", symbol):
            return symbol  # Not qualifiable.
        if symbol in vars(self.ns.get("_macro_", lambda: ())):
            return f"{self.qualname}.._macro_.{symbol}"
        if symbol in dir(builtins) and symbol not in self.ns:
            return f"builtins..{symbol}"  # Globals shadow builtins.
        return f"{self.qualname}..{symbol}"

    def reads(self, code: str) -> Iterable:
        res: Iterable[object] = self.parse(lex(code, self.filename))
        self.reinit()
        if self.verbose:
            res = list(res)
            pprint(res)
        return res

    def compile(self, code: str) -> str:
        hissp = self.reads(code)
        return self.compiler.compile(hissp)

    def gensym(self, form: str):
        try:
            return f"_{munge(form)}xAUTO{self.gensym_stack[-1]}_"
        except IndexError:
            raise ValueError("Gensym outside of template.") from None

    @contextmanager
    def gensym_context(self):
        self.gensym_stack.append(gensym_counter())
        try:
            yield
        finally:
            self.gensym_stack.pop()

    @contextmanager
    def unquote_context(self):
        try:
            gensym_number = self.gensym_stack.pop()
        except IndexError:
            raise ValueError("Unquote outside of template.") from None
        try:
            yield
        finally:
            self.gensym_stack.append(gensym_number)


def is_string(form):
    return form == ("quote", ANY, ANY) and form[2].get(":str")


def transpile(package: Optional[resources.Package], *modules: Union[str, PurePath]):
    # TODO: allow pathname without + ".lissp"?
    if package:
        for module in modules:
            transpile_module(package, module + ".lissp")
    else:
        for module in modules:
            with open(module+'.lissp') as f:
                code = f.read()
            out = module + '.py'
            _write_py(out, module, code)


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
        _write_py(out, f"{package}.{resource.split('.')[0]}", code)


def _write_py(out, qualname, code):
    with open(out, "w") as f:
        print(f"compiling {qualname} as", out, file=sys.stderr)
        if code.startswith('#!'):  # ignore shebang line
            _, _, code = code.partition('\n')
        f.write(Parser(qualname, evaluate=True, filename=str(out)).compile(code))

def main():
    transpile(*sys.argv[1:])

if __name__ == "__main__":
    # TODO: test CLI
    # TODO: document CLI
    main()
