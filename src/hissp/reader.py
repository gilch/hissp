# Copyright 2019, 2020, 2021, 2022, 2023 Matthew Egan Odendahl
# SPDX-License-Identifier: Apache-2.0
"""
The Lissp language reader and associated helper functions.

The reader is organized as a lexer and parser.
The parser is extensible with Lissp reader macros.
The lexer is not extensible,
and doesn't do much more than pull tokens from a relatively simple regex
and track its position for error messages.
"""

import ast
import builtins
import hashlib
import re
from base64 import b32encode
from collections import namedtuple
from contextlib import contextmanager, nullcontext, suppress
from functools import reduce
from importlib import import_module, resources
from itertools import chain, takewhile
from keyword import iskeyword as _iskeyword
from pathlib import Path, PurePath
from pprint import pformat
from threading import Lock
from typing import Any, Iterable, Iterator, NewType, Optional, Tuple, Union, List

import hissp.compiler as C
from hissp.compiler import Compiler, readerless
from hissp.munger import force_munge, force_qz_encode, munge

GENSYM_BYTES = 5
"""
The number of bytes gensym `$# <parse_macro>` hashes have.

The default 5 bytes (40 bits) should be more than sufficient space to
eliminate collisions with typical usage, but for unusual applications,
hash length can be increased, up to a maximum of 32 bytes.
(16 would have more space than a `uuid.uuid4`.)

Each hash character encodes 5 bits (base32 encoding), so 40-bit hashes
typically take 8 characters.
"""

ENTUPLE = ("lambda",(":",":*"," _")," _",)  # fmt: skip
"""
Used by the template macro to make tuples.

To avoid creating a dependency on Hissp, by default,
templates spell out the entuple implementation every time,
but you can override this by setting some other value here.
"""

TOKENS = re.compile(
    r"""(?x)
     (?P<whitespace>[\n ]+)
    |(?P<comment>(?:[ ]*;.*[\n])+)
    |(?P<badspace>\s)  # Other whitespace not allowed.
    |(?P<open>\()
    |(?P<close>\))
    |(?P<macro>
       ,@
      |['`,!]
      |[.][#]
      # Any atom that ends in ``#``, but not ``.#`` or ``\#``.
      |(?:[^\\ \n"();#]|\\.)*(?:[^.\\ \n"();#]|\\.)[#]
     )
    |(?P<string>
      [#]?  # raw?
      "  # Open quote.
        (?:[^"\\]  # Any non-magic character.
           |\\(?:.|\n)  # Backslash only if paired, including with newline.
        )*  # Zero or more times.
      "  # Close quote.
     )
    |(?P<continue>
       [#]?"  # String not closed.
      |;.*  # Comment may need another line.
     )
    |(?P<atom>(?:[^\\ \n"();]|\\.)+)  # Let Python deal with it.
    |(?P<error>.)
    """
)

Token = NewType("Token", Tuple[str, str, int])

DROP = object()
"""
The sentinel value returned by the discard macro ``_#``, which the
reader skips over when parsing. Reader macros can have read-time side
effects with no Hissp output by returning this. (Not recommended.)
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


_Unquote = namedtuple("_Unquote", ["target", "value"])


class Comment:
    """Parsed object for a comment token (line comment block).

    The reader normally discards these, but reader macros can use them.
    """

    def __init__(self, token):
        self.token = token

    def contents(self):
        """Gets the comment text inside the comment token.

        Strips any leading indent, the ``;`` character(s), and up to one
        following space for each line in the comment block.
        """
        return re.sub(r"(?m)\n$|^ *;+ ?", "", self.token)

    def __repr__(self):
        return f"Comment({self.token!r})"


class Extra(tuple):
    """Designates Extra read-time arguments for reader macros.

    Normally made with the ``!`` macro, but can be constructed directly.
    """

    def __repr__(self):
        return f"Extra({list(self)!r})"


def gensym_counter(_count=[0], _lock=Lock()) -> int:
    """
    Call to increment the gensym counter, and return the new count.
    Used by the gensym reader macro ``$#`` to ensure symbols are unique.

    Uses a `threading.Lock` to ensure a number is not allocated more
    than once in a session, however builds may not be reproducible if
    templates are allocated numbers in a nondeterministic order,
    therefore reading gensyms with multiple threads is not recommended.
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
        self.counters: List[int] = []
        self.context = []
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
        self.blake = hashlib.blake2s(digest_size=GENSYM_BYTES)
        self.blake.update(code.encode())
        self.blake.update(self.ns.get("__name__", "__main__").encode())
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
            # fmt: off
            if k == "whitespace": continue
            elif k == "comment":  yield Comment(v)
            elif k == "badspace": raise self._badspace(v)
            elif k == "open":     yield from self._open()
            elif k == "close":    return self._close()
            elif k == "macro":    yield from self._macro(v)
            elif k == "string":   yield self._string(v)
            elif k == "continue": raise self._continue()
            elif k == "atom":     yield self.atom(v)
            else:                 raise self._error(k)
            # fmt: on
        self._check_depth()

    def _badspace(self, v):
        return SyntaxError(
            f"{v!r} is not whitespace in Lissp. Indent with spaces only.",
            self.position(),
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
            raise SyntaxError("Too many `)`s.", self.position())
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
        self.counters.append(gensym_counter())
        self.context.append("`")
        try:
            yield
        finally:
            self.counters.pop()
            self.context.pop()

    @contextmanager
    def unquote_context(self):
        """Start a new unquote context for the current template."""
        self.context.append(",")
        if self.context.count(",") > self.context.count("`"):
            raise SyntaxError("Unquote outside of template.", self.position()) from None
        try:
            yield
        finally:
            self.context.pop()

    def _extras(self, p, v):
        extras = []
        depth = len(self.depth)
        nondrop = self._filter_drop()
        try:
            while isinstance(form := next(nondrop), Extra):
                extras.extend(form)
        except StopIteration:
            e = SoftSyntaxError if len(self.depth) == depth else SyntaxError
            raise e(f"Reader macro {v!r} missing argument.", self.position(p)) from None
        return form, extras

    def parse_macro(self, tag: str, form, extras):
        # fmt: off
        R"""Apply a reader macro to a form.

        The built-in reader macros are handled here. They are

        .. list-table::

           * - ``'``
             - `quote<special>`
           * - ``!``
             - `Extra`
           * - :literal:`\`` (backtick)
             - template quote (starts a `template`)
           * - ``_#``
             - `discard<DROP>`
           * - ``.#``
             - inject (evaluate at read time and use resulting object)

        Plus the three built-in template helper macros, which are only
        valid inside a template.

        .. list-table::

           * - ``,``
             - unquote
           * - ``,@``
             - splice unquote
           * - ``$#``
             - `gensym`

        The built-in macros are reserved by the reader and cannot be
        reassigned.
        """
        def case(s):
            if (b := tag == s) and extras:
                raise SyntaxError(f"Extra for {s!r} reader macro.")
            return b
        if case("'"):  return "quote", form
        if tag == "!": return Extra([*extras, form])
        if case("`"):  return self.template(form)
        if case(","):  return _Unquote(":?", form)
        if case(",@"): return _Unquote(":*", form)
        if case("_#"): return DROP
        if case("$#"): return self.gensym(form)
        if case(".#"): return eval(readerless(form, self.ns), self.ns)
        return self._custom_macro(form, tag, extras)
        # fmt: on

    def template(self, form):
        """Process form as template."""
        case = type(form)
        if is_lissp_string(form):
            return "quote", form
        if case is tuple and form:
            return (ENTUPLE, ":", *chain(*self._template(form)),)  # fmt: skip
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
        if invocation and C.MACROS in self.ns and hasattr(self.ns[C.MACROS], symbol):
            return f"{self.qualname}..{C.MACROS}.{symbol}"  # Known macro.
        if symbol in dir(builtins) and symbol.split(".", 1)[0] not in self.ns:
            return f"builtins..{symbol}"  # Known builtin, not shadowed (yet).
        if invocation and "." not in symbol:  # Could still be a recursive macro.
            return f"{self.qualname}{C.MAYBE}{symbol}"
        return f"{self.qualname}..{symbol}"

    def gensym(self, form: str):
        """Generate a symbol unique to the current template.
        Re-munges any $'s as a gensym hash, or adds it as a prefix if
        there aren't any. Gensym hashes are deterministic for
        reproducible builds. Inputs are the code string being read,
        the current `__name__` (defaults to "__main__" if not found)
        and a `count<gensym_counter>` of templates read so far.
        """
        blk = self.blake.copy()
        blk.update((c := self._get_counter()).to_bytes(1 + c.bit_length() // 8, "big"))
        prefix = f"_Qz{b32encode(blk.digest()).rstrip(b'=').decode()}z_"
        marker = munge("$")
        if marker not in form:
            return f"{prefix}{(form)}"
        # TODO: escape $'s somehow? $$? \$?
        return form.replace(marker, prefix)

    def _get_counter(self) -> int:
        index = self.context.count("`") - self.context.count(",")
        if not self.context or index < 0:
            raise SyntaxError("Gensym outside of template.", self.position()) from None
        if self.context[-1] == "`":
            return self.counters[-1]
        return self.counters[index]

    def _custom_macro(self, form, tag, extras):
        assert tag.endswith("#")
        tag = force_munge(self.escape(tag[:-1]))
        tag = re.sub(r"(^\.)", lambda m: force_qz_encode(m[1]), tag)
        m = (self._fully_qualified if ".." in tag else self._local)(tag)
        with self.compiler.macro_context():
            args, kwargs = parse_extras(extras)
            return m(form, *args, **kwargs)

    def _fully_qualified(self, tag):
        module, function = tag.split("..", 1)
        if re.match(rf"{C.MACROS}\.[^.]+$", function):
            function += munge("#")
        return reduce(getattr, function.split("."), import_module(module))

    def _local(self, tag):
        try:
            return getattr(self.ns[C.MACROS], tag + munge("#"))
        except (AttributeError, KeyError):
            raise SyntaxError(f"Unknown reader macro {tag!r}.", self.position())

    @staticmethod
    def escape(atom):
        """Process the backslashes in a token."""
        return re.sub(
            r"\\(.)", lambda m: force_qz_encode(m[1]) if m[1] in ".:" else m[1], atom
        )

    @staticmethod
    def _string(v):
        if v[0] == "#":  # Let Python process escapes.
            v = v.replace("\\\n", "").replace("\n", R"\n")
            val = ast.literal_eval(v[1:])
        else:  # raw
            val = v[1:-1]  # Only remove quotes.
        return v if (v := pformat(val)).startswith("(") else f"({v})"

    def _continue(self):
        return SoftSyntaxError("Incomplete string token.", self.position())

    @staticmethod
    def atom(v):
        """Preprocesses atoms. Handles escapes and munging."""
        is_symbol = "\\" == v[0]
        v = Lissp.escape(v)
        if is_symbol:
            return munge(v)
        try:
            val = ast.literal_eval(v)
            if isinstance(val, (bytes, dict, list, set, tuple)):
                return munge(v)
            return val
        except (ValueError, SyntaxError):
            return munge(v)

    def _error(self, k):
        assert k == "error", f"unknown token: {k!r}"
        return SyntaxError("Can't read this.", self.position())

    def _check_depth(self):
        if self.depth:
            raise SoftSyntaxError(
                "This form is missing a `)`.", self.position(self.depth.pop())
            )


def is_hissp_string(form) -> bool:
    """Determines if form would directly represent a string in Hissp.

    Allows "readerless mode"-style strings: ('quote','foo',)
    and any string literal in a Hissp-level str: '"foo"'
    (including the "('foo')" form produced by the Lissp reader).

    Macros often produce strings in one of these forms, via ``'`` or
    `repr` on a string object.
    """
    return (
        type(form) is tuple
        and len(form) == 2
        and form[0] == "quote"
        and type(form[1]) is str
    ) or bool(is_string_literal(form))


def is_lissp_string(form) -> bool:
    """
    Determines if form could have been read from a Lissp string literal.

    It's not enough to check if the form has a string type.
    Several token types such as control words, symbols, and Python
    injections, read in as strings. Macros may need to distinguish these
    cases.
    """
    return type(form) is str and form.startswith("(") and bool(is_string_literal(form))


def is_string_literal(form) -> Optional[bool]:
    """Determines if `ast.literal_eval` on form produces a string.

    False if it produces something else or None if it raises Exception.
    """
    with suppress(Exception):
        return type(ast.literal_eval(form)) is str


def parse_extras(extras):
    it = iter(extras)
    args = [*takewhile(lambda x: x != ":", it)]
    kwargs = {}
    for k in it:
        # fmt: off
        v = next(it)
        if k == ":?":    args.append(v)
        elif k == ":*":  args.extend(v)
        elif k == ":**": kwargs.update(v)
        else:            kwargs[k] = v
        # fmt: on
    return args, kwargs


def is_qualifiable(symbol):
    """Determines if symbol can be qualified with a module.

    Can't be ``quote``, ``__import__``, any Python reserved word, a
    prefix auto-gensym, already qualified, method syntax, or a module
    handle; and must be a valid identifier or attribute identifier.
    """
    return (
        symbol not in {"quote", "__import__"}
        and not _iskeyword(symbol)
        and not re.match(r"_Qz[A-Z2-7]+z_", symbol)
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
    compile time to handle templates and macros correctly.
    """
    path = Path(path).resolve(strict=True)
    qualname = f"{package or ''}{'.' if package else ''}{PurePath(path.name).stem}"
    L = Lissp(qualname=qualname, evaluate=True, filename=str(path))
    python = L.compile(re.sub(r"^#!.*\n", "", path.read_text("utf8")))
    path.with_suffix(".py").write_text(python, "utf8")
