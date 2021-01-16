# Copyright 2019, 2020 Matthew Egan Odendahl
# SPDX-License-Identifier: Apache-2.0
"""
The Lissp language reader and associated helper functions.

Compiles Lissp files to Python files when run as the main module.

The reader is organized as a lexer and parser.
The parser is extensible with Lissp reader macros.
The lexer is not extensible,
and doesn't do much more than pull tokens from a relatively simple regex
and track its position for error messages.
"""

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
from pprint import pformat, pprint
from types import ModuleType
from typing import Any, Iterable, Iterator, NewType, Optional, Tuple, Union

from hissp.compiler import Compiler, readerless
from hissp.munger import munge

# fmt: off
ENTUPLE = ("lambda",(":",":*","xAUTO0_"),"xAUTO0_",)
# fmt: on
"""
Used by the template macro to make tuples.

To avoid creating a dependency on Hissp, by default,
templates spell out the entuple implementation every time,
but you can override this by setting some other value here.
"""

TOKENS = re.compile(
    r"""(?x)
 (?P<comment>;.*)
|(?P<whitespace>[\n ]+)
|(?P<badspace>\s)  # Other whitespace not allowed.
|(?P<open>\()
|(?P<close>\))
|(?P<macro>
   ,@
  |['`,]
   # Any atom that ends in (an unescaped) ``#``
  |(?:[^\\ \n"();#]|\\.)+[#]
 )
|(?P<string>
  [#]?  # raw?
  "  # Open quote.
    (?:[^"\\]  # Any non-magic character.
       |\\(?:.|\n)  # Backslash only if paired, including with newline.
    )*  # Zero or more times.
  "  # Close quote.
 )
|(?P<continue>")
|(?P<atom>(?:[^\\ \n"();]|\\.)+)  # Let Python deal with it.
|(?P<error>.)
"""
)

Token = NewType("Token", Tuple[str, str, int])

DROP = object()
"""
The sentinel value returned by the discard macro ``_#``, which the 
reader skips over when parsing. Reader macros can have read-time side 
effects with no Hissp output by returning this.
"""


class SoftSyntaxError(SyntaxError):
    """A syntax error that could be corrected with more lines of input.

    When the REPL encounters this when attempting to evaluate a form,
    it will ask for more lines, rather than aborting with an error.
    """


class Lexer(Iterator):
    """The tokenizer for the Lissp language.

    Most of the actual tokenizing is done by the regex.
    The Lexer adds some position tracking to that to help with error
    messages.
    """

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
        """
        Compute the ``filename``, ``lineno``, ``offset`` and ``text``
        for a `SyntaxError`, using the current character offset in code.
        """
        good = self.code[0:pos].split("\n")
        lineno = len(good)
        offset = len(good[-1])
        return self.file, lineno, offset, self.code.split("\n")[lineno - 1]


class _Unquote(tuple):
    def __repr__(self):
        return f"_Unquote{super().__repr__()}"


def gensym_counter(count=[0]):
    """
    Call to increment the gensym counter, and return the new count.
    Used by the gensym reader macro ``$#`` to ensure symbols are unique.
    """
    count[0] += 1
    return count[0]


class Lissp:
    """
    The parser for the Lissp language.

    Wraps around a Hissp compiler instance.
    Parses Lissp tokens into Hissp syntax trees.
    """

    def __init__(
        self,
        qualname="__main__",
        ns=None,
        verbose=False,
        evaluate=False,
        filename="<?>",
    ):
        self.qualname = qualname
        self.compiler = Compiler(self.qualname, ns, evaluate)
        self.verbose = verbose
        self.filename = filename
        self.reinit()

    @property
    def ns(self):
        """The wrapped `Compiler`'s ``ns``."""
        return self.compiler.ns

    @ns.setter
    def ns(self, ns):
        self.compiler.ns = ns

    def reinit(self):
        """Reset position, nesting depth, and gensym stack."""
        self.gensym_stack = []
        self.depth = 0
        self._p = 0

    def position(self):
        """
        Get the ``filename``, ``lineno``, ``offset`` and ``text``
        for a `SyntaxError`, from the `Lexer` given to `parse`.
        """
        return self.tokens.position(self._p)

    def parse(self, tokens: Lexer) -> Iterator:
        """Build Hissp forms from a `Lexer`."""
        self.tokens = tokens
        return (form for form in self._parse() if form is not DROP)

    def _parse(self) -> Iterator:
        for k, v, self._p in self.tokens:
            if k in {"comment", "whitespace"}:
                continue
            elif k == "badspace":
                raise SyntaxError(
                    repr(v) + " is not whitespace in Lissp. Indent with spaces only.",
                    self.position(),
                )
            elif k == "open":
                yield from self._open()
            elif k == "close":
                self._close()
                return
            elif k == "macro":
                yield from self._macro(v)
            elif k == "string":
                yield self._string(v)
            elif k == "continue":
                raise SoftSyntaxError("Incomplete token.", self.position())
            elif k == "atom":
                yield self._atom(v)
            elif k == "error":
                raise SyntaxError("Can't read this.", self.position())
            else:
                assert False, "unknown token: " + repr(k)
        if self.depth:
            raise SoftSyntaxError(
                "Ran out of tokens before completing form.", self.position()
            )

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
        if v[0] == "#":  # Let Python process escapes.
            v = v.replace("\\\n", "").replace("\n", r"\n")
            val = ast.literal_eval(v[1:])
        else:  # raw
            val = v[1:-1]  # Only remove quotes.
        return v if (v := pformat(val)).startswith("(") else f"({v})"

    def _macro(self, v):
        with {
            "`": self.gensym_context,
            ",": self.unquote_context,
            ",@": self.unquote_context,
        }.get(v, nullcontext)():
            try:
                depth = self.depth
                form = next(self.parse(self.tokens))
            except StopIteration:
                if self.depth == depth:
                    raise SoftSyntaxError(
                        f"Reader macro {v!r} missing argument.", self.position()
                    ) from None
                raise SyntaxError(
                    f"Reader macro {v!r} missing argument.", self.position()
                ) from None
            yield self.parse_macro(v, form)

    @staticmethod
    def _atom(v):
        is_symbol = "\\" == v[0]
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
        """Apply a reader macro to a form."""
        if tag == "'":
            return "quote", form
        if tag == "`":
            return self.template(form)
        if tag == ",":
            return _Unquote([":?", form])
        if tag == ",@":
            return _Unquote([":*", form])
        assert tag.endswith("#")
        return self._parse_tag(tag[:-1], form)

    def _parse_tag(self, tag, form):
        if tag == "_":
            return DROP
        if tag == "$":
            return self.gensym(form)
        if tag == ".":
            return eval(readerless(form, self.ns), self.ns)
        if is_string(form):
            form = ast.literal_eval(form)
        tag = munge(self.escape(tag))
        if ".." in tag and not tag.startswith(".."):
            module, function = tag.split("..", 1)
            return reduce(getattr, function.split("."), import_module(module))(form)
        try:
            m = getattr(self.ns["_macro_"], tag + "xHASH_")
        except (AttributeError, KeyError):
            raise SyntaxError(f"Unknown reader macro {tag}", self.position())
        with self.compiler.macro_context():
            return m(form)

    @staticmethod
    def escape(atom):
        """Process the backslashes in a token."""
        atom = atom.replace(r"\.", "xFULLxSTOP_")
        return re.sub(r"\\(.)", lambda m: m[1], atom)

    def template(self, form):
        """Process form as template."""
        case = type(form)
        if is_string(form):
            return "quote", form
        if case is tuple and form:
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
        """Qualify symbol based on current context."""
        if re.search(
            r"^\(|^\.|\.$|^quote$|^lambda$|^__import__$|xAUTO\d+_$|\.\.", symbol
        ):
            return symbol  # Not qualifiable.
        if invocation and "_macro_" in self.ns and self._macro_has(symbol):
            return f"{self.qualname}.._macro_.{symbol}"  # Known macro.
        if symbol in dir(builtins) and symbol.split(".", 1)[0] not in self.ns:
            return f"builtins..{symbol}"  # Known builtin, not shadowed (yet).
        if invocation and "." not in symbol:  # Could still be a recursive macro.
            return f"{self.qualname}..xAUTO_.{symbol}"
        return f"{self.qualname}..{symbol}"

    def _macro_has(self, symbol):
        # The _macro_ interface is not required to implement
        # __contains__ or __dir__ and exotic _macro_ objects might
        # override __getattribute__. The only way to tell if _macro_ has
        # a name is getattr().
        try:
            getattr(self.ns["_macro_"], symbol)
        except AttributeError:
            return False
        return True

    def reads(self, code: str) -> Iterable:
        """Read Hissp forms from code string."""
        res: Iterable[object] = self.parse(Lexer(code, self.filename))
        self.reinit()
        if self.verbose:
            res = list(res)
            pprint(res)
        return res

    def compile(self, code: str) -> str:
        """Read Lissp code and pass it on to the Hissp compiler."""
        hissp = self.reads(code)
        return self.compiler.compile(hissp)

    def gensym(self, form: str):
        """Generate a symbol unique to the current template."""
        try:
            return f"_{munge(form)}xAUTO{self.gensym_stack[-1]}_"
        except IndexError:
            raise SyntaxError("Gensym outside of template.", self.position()) from None

    @contextmanager
    def gensym_context(self):
        """Start a new gensym context for the current template."""
        self.gensym_stack.append(gensym_counter())
        try:
            yield
        finally:
            self.gensym_stack.pop()

    @contextmanager
    def unquote_context(self):
        """Start a new unquote context for the current template."""
        try:
            gensym_number = self.gensym_stack.pop()
        except IndexError:
            raise SyntaxError("Unquote outside of template.", self.position()) from None
        try:
            yield
        finally:
            self.gensym_stack.append(gensym_number)


def is_string(form):
    """
    Determines if form could have been read from a Lissp string literal.

    It's not enough to check if the form has a string type.
    Several token types such as control words, symbols, and Python
    injections, read in as strings. Macros may need to distinguish these
    cases.
    """
    try:
        return (
            type(form) is str
            and form.startswith("(")
            and type(ast.literal_eval(form)) is str
        )
    except:
        return False


def transpile(package: Optional[resources.Package], *modules: Union[str, PurePath]):
    """
    Compiles the named modules to Python files.
    If the package is None or "", it uses the current working directory without using a package.
    Lissp files must know their package at compile time to resolve imports correctly.
    """
    # TODO: allow pathname without + ".lissp"?
    if package:
        for module in modules:
            transpile_module(package, module + ".lissp")
    else:
        for module in modules:
            with open(module + ".lissp") as f:
                code = f.read()
            out = module + ".py"
            _write_py(out, module, code)


def transpile_module(
    package: resources.Package,
    resource: Union[str, PurePath],
    out: Union[None, str, bytes, Path] = None,
):
    """Transpile a single submodule in a package."""
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
        if code.startswith("#!"):  # ignore shebang line
            _, _, code = code.partition("\n")
        f.write(Lissp(qualname, evaluate=True, filename=str(out)).compile(code))


def main():
    """Calls `transpile` with arguments from `sys.argv`."""
    transpile(*sys.argv[1:])


if __name__ == "__main__":
    # TODO: test CLI
    main()
