# Copyright 2019, 2020, 2021 Matthew Egan Odendahl
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
import re
from collections import namedtuple
from contextlib import contextmanager, nullcontext
from functools import reduce
from importlib import import_module, resources
from itertools import chain
from keyword import iskeyword as _iskeyword
from pathlib import Path, PurePath
from pprint import pformat
from threading import Lock
from typing import Any, Iterable, Iterator, NewType, Optional, Tuple, Union

from hissp.compiler import Compiler, MAYBE, readerless
from hissp.munger import force_qz_encode, munge

# fmt: off
ENTUPLE = ("lambda",(":",":*"," _")," _",)
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
  |['`,!]
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


_Unquote = namedtuple('_Unquote', ['target', 'value'])
Comment = namedtuple('Comment', ['content'])
Extra = namedtuple('Extra', ['argument'])

def gensym_counter(_count=[0], _lock=Lock()):
    """
    Call to increment the gensym counter, and return the new count.
    Used by the gensym reader macro ``$#`` to ensure symbols are unique.
    """
    with _lock:
        _count[0] += 1
        return _count[0]


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
        evaluate=False,
        filename="<?>",
    ):
        self.qualname = qualname
        self.compiler = Compiler(self.qualname, ns, evaluate)
        self.filename = filename
        self.reinit()

    def reinit(self):
        """Reset position, nesting depth, and gensym stack."""
        self.gensym_stack = []
        self.depth = []
        self._p = 0

    @property
    def ns(self):
        """The wrapped `Compiler`'s ``ns``."""
        return self.compiler.ns

    @ns.setter
    def ns(self, ns):
        self.compiler.ns = ns

    def compile(self, code: str) -> str:
        """Read Lissp code and pass it on to the Hissp compiler."""
        hissp = self.reads(code)
        return self.compiler.compile(hissp)

    def reads(self, code: str) -> Iterable:
        """Read Hissp forms from code string."""
        res: Iterable[object] = self.parse(Lexer(code, self.filename))
        self.reinit()
        return res

    def parse(self, tokens: Lexer) -> Iterator:
        """Build Hissp forms from a `Lexer`."""
        self.tokens = tokens
        return (x for x in self._filter_drop() if not isinstance(x, Comment))

    def _filter_drop(self):
        return (x for x in self._parse() if x is not DROP)

    def _parse(self) -> Iterator:
        for k, v, self._p in self.tokens:
            if k == "whitespace":
                continue
            elif k == "comment":
                yield Comment(v[1:])
            elif k == "badspace":
                raise SyntaxError(
                    f"{v!r} is not whitespace in Lissp. Indent with spaces only.",
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
                raise SoftSyntaxError("Incomplete string token.", self.position())
            elif k == "atom":
                yield self.atom(v)
            else:
                assert k == "error", "unknown token: " + repr(k)
                raise SyntaxError("Can't read this.", self.position())
        if self.depth:
            raise SoftSyntaxError(
                "This form is missing a `)`.",
                self.position(self.depth.pop())
            )

    def position(self, index=None):
        """
        Get the ``filename``, ``lineno``, ``offset`` and ``text``
        for a `SyntaxError`, from the `Lexer` given to `parse`.
        """
        return self.tokens.position(self._p if index is None else index)

    def _open(self):
        self.depth.append(self._p)
        yield (*self.parse(self.tokens),)

    def _close(self):
        if not self.depth:
            raise SyntaxError("Extra `)`.", self.position())
        self.depth.pop()

    def _macro(self, v):
        p = self._p
        with {
            "`": self.gensym_context,
            ",": self.unquote_context,
            ",@": self.unquote_context,
        }.get(v, nullcontext)():
            yield self.parse_macro(v, *self._extras(p, v))

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

    def _extras(self, p, v):
        extras = []
        depth = len(self.depth)
        nondrop = self._filter_drop()
        try:
            while isinstance(form:=next(nondrop), Extra):
                extras.append(form.argument)
        except StopIteration:
            e = SoftSyntaxError if len(self.depth) == depth else SyntaxError
            raise e(f"Reader macro {v!r} missing argument.", self.position(p)) from None
        return form, extras

    def parse_macro(self, tag: str, form, extras):
        """Apply a reader macro to a form."""
        def case(s):
            if (b := tag == s) and extras:
                raise SyntaxError(f"Extra for {s!r} reader macro.")
            return b
        if case("'"): return "quote", form
        if case("!"): return Extra(_eval_if_string(form))
        if case("`"): return self.template(form)
        if case(","): return _Unquote(":?", form)
        if case(",@"): return _Unquote(":*", form)
        if case("_#"): return DROP
        if case("$#"): return self.gensym(form)
        if case(".#"): return eval(readerless(form, self.ns), self.ns)
        return self._custom_macro(form, tag, extras)

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
        if case is _Unquote and form.target == ":?":
            return form.value
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
        if not is_qualifiable(symbol):
            return symbol
        if invocation and "_macro_" in self.ns and self._macro_has(symbol):
            return f"{self.qualname}.._macro_.{symbol}"  # Known macro.
        if symbol in dir(builtins) and symbol.split(".", 1)[0] not in self.ns:
            return f"builtins..{symbol}"  # Known builtin, not shadowed (yet).
        if invocation and "." not in symbol:  # Could still be a recursive macro.
            return f"{self.qualname}{MAYBE}{symbol}"
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

    def gensym(self, form: str):
        """Generate a symbol unique to the current template."""
        try:
            return f"_{munge(form)}_QzNo{self.gensym_stack[-1]}_"
        except IndexError:
            raise SyntaxError("Gensym outside of template.", self.position()) from None

    def _custom_macro(self, form, tag, extras):
        assert tag.endswith("#")
        tag = munge(self.escape(tag[:-1]))
        form = _eval_if_string(form)
        if ".." in tag:
            module, function = tag.split("..", 1)
            m = reduce(getattr, function.split("."), import_module(module))
        else:
            try:
                m = getattr(self.ns["_macro_"], tag + munge("#"))
            except (AttributeError, KeyError):
                raise SyntaxError(f"Unknown reader macro {tag!r}.", self.position())
        with self.compiler.macro_context():
            return m(form, *extras)

    @staticmethod
    def escape(atom):
        """Process the backslashes in a token."""
        atom = atom.replace(r"\.", force_qz_encode("."))
        return re.sub(r"\\(.)", lambda m: m[1], atom)

    @staticmethod
    def _string(v):
        if v[0] == "#":  # Let Python process escapes.
            v = v.replace("\\\n", "").replace("\n", r"\n")
            val = ast.literal_eval(v[1:])
        else:  # raw
            val = v[1:-1]  # Only remove quotes.
        return v if (v := pformat(val)).startswith("(") else f"({v})"

    @staticmethod
    def atom(v):
        """Preprocesses atoms. Handles escapes and munging."""
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


def _eval_if_string(form):
    if is_string(form):
        form = ast.literal_eval(form)
    return form


def is_qualifiable(symbol):
    """Determines if symbol can be qualified with a module.

    Can't be ``quote``, ``__import__``, any Python reserved word, an
    auto-gensym, already qualified, method syntax, or a module literal;
    and must be a valid identifier or attribute identifier.
    """
    return (
            symbol not in {"quote", "__import__"}
            and not _iskeyword(symbol)
            and not re.match(r".*_QzNo\d+_$", symbol)
            and all(map(str.isidentifier, symbol.split(".")))
    )


def transpile(package: Optional[str], *modules: str):
    """Transpiles the named Python modules from Lissp.

    A .lissp file of the same name must be present in the module's
    location. The Python modules are overwritten. Missing modules are
    created. If the package is "" or ``None``, `transpile` writes non-
    packaged modules to the current working directory instead.
    """
    t = transpile_packaged if package else transpile_file
    for m in modules:
        t(f"{m}.lissp", package)


def transpile_packaged(resource: str, package: str):
    """Locates & transpiles a packaged .lissp resource file to .py."""
    with resources.path(package, resource) as path:
        transpile_file(path, package)


def transpile_file(path: Union[Path, str], package: Optional[str] = None):
    """Transpiles a single .lissp file to .py in the same location.

    Code in .lissp files is executed upon compilation. This is necessary
    because macro definitions can alter the compilation of subsequent
    top-level forms. A packaged Lissp file must know its package at
    compile time to resolve imports correctly.
    """
    path = Path(path).resolve(strict=True)
    qualname = f"{package or ''}{'.' if package else ''}{PurePath(path.name).stem}"
    python = Lissp(
        qualname=qualname, evaluate=True, filename=str(path)
    ).compile(re.sub(r'^#!.*\n', '', path.read_text()))
    path.with_suffix('.py').write_text(python, 'utf8')
