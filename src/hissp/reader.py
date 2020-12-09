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

ENTUPLE = ("lambda", (":", ":*", "xAUTO0_"), "xAUTO0_")

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

Token = NewType("Token", Tuple[str, str, int])

DROP = object()

class SoftSyntaxError(SyntaxError):
    """A syntax error that could be corrected with more lines of input."""

class Lexer(Iterator):
    def __init__(self, code: str, file: str = "<?>"):
        self.code = code
        self.file = file
        self.it = self._it()

    def __iter__(self) -> Iterator[Token]:
        return self

    def __next__(self):
        return next(self.it)

    def _it(self):
        pos = 0
        while pos < len(self.code):
            match = TOKENS.match(self.code, pos)
            assert match is not None
            assert match.lastgroup
            assert match.end() > pos, match.groups()
            pos = match.end()
            yield Token((match.lastgroup, match.group(), pos))

    def position(self, pos: int) -> Tuple[str, int, int, str]:
        good = self.code[0:pos].split("\n")
        line = len(good)
        column = len(good[-1])
        return self.file, line, column, self.code


class _Unquote(tuple):
    def __repr__(self):
        return f"_Unquote{super().__repr__()}"


def gensym_counter(count=[0]):
    count[0] += 1
    return count[0]


class Lissp:
    def __init__(
        self, qualname="__main__", ns=None, verbose=False, evaluate=False, filename="<?>"
    ):
        self.qualname = qualname
        self.compiler = Compiler(self.qualname, ns, evaluate)
        self.ns = self.compiler.ns
        self.verbose = verbose
        self.filename = filename
        self.reinit()

    def reinit(self):
        self.gensym_stack = []
        self.depth = 0
        self._p = 0

    def position(self):
        return self.tokens.position(self._p)

    def parse(self, tokens: Lexer) -> Iterator:
        self.tokens = tokens
        return (form for form in self._parse() if form is not DROP)

    def _parse(self) -> Iterator:
        for k, v, self._p in self.tokens:
            if k == "open":
                yield from self._open()
            elif k == "close":
                self._close()
                return
            elif k == "string":
                yield from self._string(v)
            elif k in {"comment", "whitespace"}:
                continue
            elif k == "macro":
                yield from self._macro(v)
            elif k == "atom":
                yield self._atom(v)
            elif k == "badspace":
                raise SyntaxError("Bad space: " + repr(v), self.position())
            elif k == "continue":
                raise SoftSyntaxError("Incomplete token.", self.position())
            elif k == "error":
                raise SyntaxError("Can't read this.", self.position())
            else:
                assert False, "unknown token: " + repr(k)
        if self.depth:
            raise SoftSyntaxError("Ran out of tokens before completing form.", self.position())

    def _open(self):
        depth = self.depth
        self.depth += 1
        yield (*self.parse(self.tokens),)
        if self.depth != depth:
            raise SoftSyntaxError("Unclosed '('.", self.position())

    def _close(self):
        self.depth -= 1
        if self.depth < 0:
            raise SyntaxError("Unopened ')'.", self.position())

    @staticmethod
    def _string(v):
        v = v.replace("\\\n", "").replace("\n", r"\n")
        val = ast.literal_eval(v)
        if v[0] == 'b':  # bytes
            yield val
        else:
            yield "quote", val, {":str": True}

    def _macro(self, v):
        with {
            "`": self.gensym_context,
            ",": self.unquote_context,
            ",@": self.unquote_context,
        }.get(v, nullcontext)():
            try:
                form = next(self.parse(self.tokens))
            except StopIteration:
                raise SyntaxError(f"Reader macro {v!r} missing argument.", self.position()) from None
            yield self.parse_macro(v, form)

    @staticmethod
    def _atom(v):
        is_symbol = '\\' == v[0]
        v = Lissp.escape(v)
        if is_symbol:
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
        return self.parse_tag(tag[:-1], form)

    def parse_tag(self, tag, form):
        if tag == "_":
            return DROP
        if tag == "$":
            return self.gensym(form)
        if tag == ".":
            return eval(readerless(form), {})
        if is_string(form):
            form = form[1]
        tag = munge(self.escape(tag))
        if ".." in tag and not tag.startswith(".."):
            module, function = tag.split("..", 1)
            return reduce(getattr, function.split("."), import_module(module))(form)
        try:
            m = getattr(self.ns["_macro_"], tag)
        except (AttributeError, KeyError):
            raise SyntaxError(f"Unknown reader macro {tag}", self.position())
        return m(form)

    @staticmethod
    def escape(atom):
        atom = atom.replace(r'\.', 'xFULLxSTOP_')
        return re.sub(r'\\(.)', lambda m: m[1], atom)

    def template(self, form):
        case = type(form)
        if case is tuple and form:
            if is_string(form):
                return "quote", form
            return (
                ENTUPLE,
                ":",
                *chain(*self._template(form)),
            )
        if case is str and not form.startswith(":"):
            return "quote", self.qualify(form)
        if case is _Unquote and form[0] == ":?":
            return form[1]
        return form

    def _template(self, forms: Iterable) -> Iterable[Tuple[str, Any]]:
        invocation = True
        for form in forms:
            case = type(form)
            if case is str and not form.startswith(":"):
                yield ":?", ("quote", self.qualify(form, invocation))
            elif case is _Unquote:
                yield form
            elif case is tuple:
                yield ":?", self.template(form)
            else:
                yield ":?", form
            invocation = False

    def qualify(self, symbol: str, invocation=False) -> str:
        if re.search(r"^\.|\.$|^quote$|^lambda$|^__import__$|xAUTO\d+_$|\.\.", symbol):
            return symbol  # Not qualifiable.
        if symbol in vars(self.ns.get("_macro_", lambda: ())):
            return f"{self.qualname}.._macro_.{symbol}"
        if symbol in dir(builtins) and not self._has(symbol):
            return f"builtins..{symbol}"  # Globals shadow builtins.
        if not invocation or self._has(symbol):
            return f"{self.qualname}..{symbol}"
        # Name wasn't found, but might be a macro. Decide at compile time.
        return f"{self.qualname}..xAUTO_.{symbol}"

    def _has(self, symbol):
        try:
            getattr(self.ns, symbol)
        except AttributeError:
            return False
        return True

    def reads(self, code: str) -> Iterable:
        res: Iterable[object] = self.parse(Lexer(code, self.filename))
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
            raise SyntaxError("Gensym outside of template.", self.position()) from None

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
            raise SyntaxError("Unquote outside of template.", self.position()) from None
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
        f.write(Lissp(qualname, evaluate=True, filename=str(out)).compile(code))

def main():
    transpile(*sys.argv[1:])

if __name__ == "__main__":
    # TODO: test CLI
    # TODO: document CLI
    main()
