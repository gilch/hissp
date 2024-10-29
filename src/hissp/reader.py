# Copyright 2019, 2020, 2021, 2022, 2023, 2024 Matthew Egan Odendahl
# SPDX-License-Identifier: Apache-2.0
R"""
The Lissp language reader and associated helper functions.

The reader is organized as a lexer and parser.
The parser is extensible with Lissp `tag`\ s.
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
from collections.abc import Iterable, Iterator
from contextlib import contextmanager, suppress
from functools import reduce
from importlib import import_module, resources
from itertools import chain
from keyword import iskeyword as _iskeyword
from pathlib import Path, PurePath
from pprint import pformat
from typing import (
    Any,
    Callable as Fn,
    Literal,
    NamedTuple,
    NewType,
    NoReturn,
    TypeGuard,
    cast,
)

import hissp.compiler as C
from hissp.compiler import Env
from hissp.munger import force_qz_encode, munge

GENSYM_BYTES = 5
"""
The number of bytes `gensym` hashes have.

The default 5 bytes (40 bits) should be more than sufficient space to
eliminate collisions with typical usage: dozens of gensyms in the same
scope would have a less than a one-in-a-billion chance of collision,
even assuming they all have the same suffix. (Even 3 bytes gets that
number down to around one in ten thousand.)

For unusual applications (if more than dozens of gensyms are expected in
a shared scope, or one in a billion is still too high), hash length can
be increased, up to a maximum of 32 bytes.

Even 8 bytes is enough space for a hundred thousand gensyms in the
same scope with similar collision probability, or dozens with a
one-in-quadrillion chance, which is probably lower than the risk of a
hardware failure. It's unlikely you'll ever need more than 16 bytes,
which has more space than `uuid.uuid4`.

Each hash character encodes 5 bits (`Base32 <base64.b32encode>`),
so a multiple of 5 is recommended, although 3, 8, or 13 bytes are also
fairly efficient for their size:

===== ===== ====== ===================================
bytes bits  chars  example
===== ===== ====== ===================================
3     24    5      ``Qzthink__G``
5     40    8      ``Qzthinking__G``
8     64    13     ``Qzinvestigation__G``
10    80    16     ``Qzincomprehensible__G``
13    104   21     ``Qzelectroencephalograph__G``
15    120   24     ``Qzmagneticresonanceimaging__G``
16    128   26     ``Qzpositronemissiontomography__G``
===== ===== ====== ===================================
"""

TOKENS = re.compile(
    r"""(?x)
     (?P<whitespace>[\n ]+)
    |(?P<comment>(?:[ ]*;.*\n)+)
    |(?P<badspace>\s)  # Other whitespace not allowed.
    |(?P<open> [(])
    |(?P<close>[)])
    |(?P<template>`)
    |(?P<unquote>,@?)
    |(?P<quote>')
    |(?P<inject>[.][#])
    |(?P<discard> _[#])
    |(?P<gensym>[$][#])
    |(?P<stararg>[*][*]?=)
    |(?P<kwarg>(?:\\.|[^\\ \n"|();#])*
               (?:\\.|\w)  # Character before = must be alnum, or escaped.
               =)
    |(?P<tag>  (?:\\.|[^\\ \n"|();#])*
               (?:\\.|[^\\ \n"|();#.])
               [#]+)
    |(?P<unicode>
      "  # Open quote.
        (?:[^"\\]  # Any non-magic character.
           |\\(?:.|\n)  # Backslash only if paired, including with newline.
        )*  # Zero or more times.
      "  # Close quote.
     )
    |(?P<fragment>
      [|]  # open
        (?:[^|\n]  # No newlines or unpaired |.
           |[|][|]  # | only if paired.
        )*
      [|]  # close
     )
    |(?P<continue>
       "  # String not closed.
      |;.*  # Comment may need another line.
     )
    |(?P<badfrag>[|])  # No multiline fragments.
    |(?P<control>:(?:\\.|[^\\ \n"|();])*)
    |(?P<bare>    (?:\\.|[^\\ \n"|();])+)
    |(?P<error>.)
    """
)

Token = NewType("Token", tuple[str, str, int])


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

    def __init__(self, code: str, file: str = "<?>") -> None:
        self.code = code
        self.file = file
        self.it = self._it()

    def __iter__(self) -> Iterator[Token]:
        return self

    def __next__(self) -> Token:
        return next(self.it)

    def _it(self) -> Iterator[Token]:
        pos = 0
        while pos < len(self.code):
            match = TOKENS.match(self.code, pos)
            assert match is not None
            assert match.lastgroup
            assert match.end() > pos, match.groups()
            pos = match.end()
            yield Token((match.lastgroup, match.group(), pos))

    def position(self, pos: int) -> tuple[str, int, int, str]:
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
    """`Parsed object` class for a `comment token` (line comment block).

    The reader normally discards these, but they can be `tag` arguments.
    """

    def __init__(self, token: str):
        self.token = token

    def contents(self) -> str:
        """Gets the comment text inside the comment token.

        Strips any leading indent, the ``;`` character(s), and up to one
        following space for each line in the comment block.
        """
        return re.sub(r"(?m)\n$|^ *;+ ?", "", self.token)

    def __repr__(self) -> str:
        return f"Comment({self.token!r})"


class Kwarg(NamedTuple):
    """Contains a read-time keyword argument for a `tag`.

    Normally made with a `kwarg token`, but can be constructed directly.
    """

    k: str
    v: Any


class Lissp:
    """The Lissp Reader

    Wraps around a Hissp compiler instance and creates a Lissp parser.
    """

    def __init__(
        self,
        qualname: str = "__main__",
        env: Env | None = None,
        evaluate: bool = False,
        filename: str = "<?>",
    ):
        self._template_count = 0
        self.qualname = qualname
        self.compiler = C.Compiler(self.qualname, env, evaluate)
        self.filename = filename

    def template_count(self):
        self._template_count += 1
        return self._template_count

    @property
    def env(self) -> Env:
        """The wrapped `Compiler`'s ``env``."""
        return self.compiler.env

    @env.setter
    def env(self, env: Env) -> None:
        self.compiler.env = env

    def compile(self, code: str) -> str:
        """Read Lissp code and pass it on to the Hissp compiler."""
        hissp = self.reads(code)
        return self.compiler.compile(hissp)

    def reads(self, code: str) -> "Parser":
        """Read Hissp forms from code string."""
        return self.parse(Lexer(code, self.filename))

    def parse(self, tokens: Lexer) -> "Parser":
        """Read Hissp forms from a Lexer instance."""
        return Parser(self, tokens)


class Parser(Iterator):
    R"""
    The parser for the Lissp language.

    Parses Lissp tokens into Hissp syntax trees.

    The `special tag`\ s are handled here. They are

    .. list-table::

       * - ``'``
         - `quote<special>`
       * - :literal:`\`` (backtick)
         - `template quote` (starts a `template`)
       * - ``_#``
         - `discard tag`
       * - ``.#``
         - `inject tag` (evaluate at read time)

    Plus the three built-in template helpers, which are only
    valid inside a template.

    .. list-table::

       * - ``,``
         - `unquote`
       * - ``,@``
         - `splice`
       * - ``$#``
         - `gensym tag`

    And finally, the `stararg token` special tags ``*=`` and ``**=``.

    Special tags are reserved by the reader and cannot be reassigned.
    """

    def __init__(self, lissp: Lissp, tokens: Lexer) -> None:
        """Reset hasher, position, nesting depth, and gensym stacks."""
        self.lissp = lissp
        self.tokens = tokens
        self.counters: list[int] = []
        self.context: list[str] = []
        self.depth: list[int] = []
        self._pos = 0
        self.blake = hashlib.blake2s(digest_size=GENSYM_BYTES)
        self.blake.update(tokens.code.encode())
        self.blake.update(self.lissp.env.get("__name__", "__main__").encode())

    def __next__(self):
        return next(self._no_comment())

    def _no_comment(self) -> Iterator:
        return (x for x in self._parse() if not isinstance(x, Comment))

    def _parse(self) -> Iterator:
        for k, v, self._pos in self.tokens:
            # fmt: off
            if k == "whitespace": continue
            elif k == "comment":  yield Comment(v)
            elif k == "badspace": raise self._badspace(v)
            elif k == "open":     yield self._open()
            elif k == "close":    return self._close()
            elif k == "template": yield self._template(v)
            elif k == "unquote":  yield self._unquote(v)
            elif k == "quote":    yield "quote", self._pull(v)
            elif k == "inject":   yield self._inject(v)
            elif k == "discard":  self._pull(v)
            elif k == "gensym":   yield self._gensym(self._pull(v))
            elif k == "tag":      yield self._tag(self._pull(v), v)
            elif k == "unicode":  yield self._unicode(v)
            elif k == "fragment": yield self._fragment(v)
            elif k == "continue": raise self._continue()
            elif k == "badfrag":  raise SyntaxError("unpaired |", self.position())
            elif k == "control":  yield self.escape(v)
            elif k == "bare":     yield self.bare(v)
            elif k == "error":    raise self._error(k)
            else:                 yield Kwarg(v[:-1], self._pull(v))  # kwarg, stararg
            # fmt: on
        self._check_depth()

    def _badspace(self, v: str) -> SyntaxError:
        return SyntaxError(
            f"{v!r} is not whitespace in Lissp. Indent with spaces only.",
            self.position(),
        )

    def position(self, index: int | None = None) -> tuple[str, int, int, str]:
        """
        Get the ``filename``, ``lineno``, ``offset`` and ``text``
        for a `SyntaxError`, from the `Lexer` given to `parse`.
        """
        return self.tokens.position(self._pos if index is None else index)

    def _open(self) -> tuple:
        self.depth.append(self._pos)
        return (*self._no_comment(),)

    def _close(self) -> None:
        if not self.depth:
            raise SyntaxError("too many `)`s", self.position())
        self.depth.pop()

    @contextmanager
    def gensym_context(self):
        """Start a new gensym context for the current template."""
        self.counters.append(self.lissp.template_count())
        self.context.append("`")
        try:
            yield
        finally:
            self.counters.pop()
            self.context.pop()

    def _unquote(self, v: Literal[",@", ","]) -> _Unquote:
        with self.unquote_context():
            return _Unquote({",@": ":*", ",": ":?"}[v], self._pull(v, self._pos))

    @contextmanager
    def unquote_context(self):
        """Start a new unquote context for the current template."""
        self.context.append(",")
        if self.context.count(",") > self.context.count("`"):
            raise SyntaxError("unquote outside of template", self.position()) from None
        try:
            yield
        finally:
            self.context.pop()

    def _inject(self, v: str):
        with C.macro_context(self.lissp.env):
            return eval(
                C.readerless(self._pull(v, self._pos), self.lissp.env), self.lissp.env
            )

    def _pull(self, v: str, p: int | None = None):
        if p is None:
            p = self._pos
        depth = len(self.depth)
        try:
            return next(self._parse())
        except StopIteration:
            e = SoftSyntaxError if len(self.depth) == depth else SyntaxError
            raise e(f"tag {v!r} missing argument", self.position(p)) from None

    def _template(self, v: str):
        with self.gensym_context():
            return self._template_form(self._pull(v))

    def _template_form(self, form):
        """Process form as template."""
        case = type(form)
        if is_lissp_unicode(form):
            return "quote", form
        if C.is_node(form):
            return ("",":", *chain(*self._template_forms(form)), ":?", "")  # fmt: skip
        if C.is_str(form) and not form.startswith(":"):
            return "quote", self.qualify(form)
        if case is _Unquote:
            if form.target == ":?":
                return form.value
            raise SyntaxError("splice not in tuple", self.position())
        return form

    def _template_forms(self, forms: Iterable) -> Iterable[tuple[str, Any]]:
        invocation = True
        for form in forms:
            case = type(form)
            if C.is_str(form) and not form.startswith(":"):
                yield ":?", ("quote", self.qualify(form, invocation))
            elif case is _Unquote:
                yield form
            elif C.is_node(form):
                yield ":?", self._template_form(form)
            else:
                yield ":?", form
            invocation = False

    def qualify(self, symbol: str, invocation=False) -> str:
        """Qualify symbol based on current context."""
        if not is_qualifiable(symbol):
            return symbol
        env = self.lissp.env
        if invocation and C.MACROS in env and hasattr(env[C.MACROS], symbol):
            return f"{self.lissp.qualname}..{C.MACROS}.{symbol}"  # Known macro.
        if symbol in dir(builtins) and symbol.split(".", 1)[0] not in env:
            return f"builtins..{symbol}"  # Known builtin, not shadowed (yet).
        if invocation and "." not in symbol:  # Could still be a recursive macro.
            return f"{self.lissp.qualname}{C.MAYBE}{symbol}"
        return f"{self.lissp.qualname}..{symbol}"

    def _gensym(self, form: str) -> str:
        """Generate a symbol unique to the current template.
        Re-munges any $'s as a gensym hash, or adds it as a prefix if
        there aren't any. Gensym hashes are deterministic for
        reproducible builds. Inputs are the code string being read,
        the current `__name__` (defaults to "__main__" if not found)
        and a count of templates read so far.
        """
        blk = self.blake.copy()
        blk.update((c := self._get_counter()).to_bytes(1 + c.bit_length() // 8, "big"))
        prefix = f"_Qz{b32encode(blk.digest()).rstrip(b'=').lower().decode()}__"
        marker = munge("$")
        if marker not in form:
            return f"{prefix}{form}"
        # TODO: escape $'s somehow? $$? \$?
        return form.replace(marker, prefix)

    def _get_counter(self) -> int:
        index = self.context.count("`") - self.context.count(",")
        if not self.context or index < 0:
            raise SyntaxError("gensym outside of template", self.position()) from None
        if self.context[-1] == "`":
            return self.counters[-1]
        return self.counters[index]

    def _tag(self, form, tag: str):
        assert tag.endswith("#")
        arity = re.sub(r"\\.", "", tag).count("#")
        assert arity >= 1
        depth_pos = len(self.depth), self._pos
        args, kwargs = [], {}
        for i, x in enumerate(chain([form], self._parse()), 1):
            self._collect(args, kwargs, x)
            if i == arity:
                break
        else:
            self._tag_error(tag, *depth_pos)
        label = self._label(arity, tag)
        fn = self._fully_qualified if ".." in label else self._local
        with C.macro_context(self.lissp.env):
            return fn(label)(*args, **kwargs)

    @classmethod
    def _label(cls, arity: int, tag: str) -> str:
        label = munge(cls.escape(tag[:-arity]))
        return re.sub(r"(^\.)", lambda m: force_qz_encode(m[1]), label)

    @classmethod
    def _collect(cls, args: list, kwargs: dict, x) -> None:
        if type(x) is Kwarg:
            k, v = x
            if k == "*":
                args.extend(v)
            elif k == "**":
                kwargs.update(dict(v))
            else:
                kwargs[munge(cls.escape(k))] = v
        else:
            args.append(x)

    def _tag_error(self, tag: str, depth: int, pos: int) -> NoReturn:
        e = SoftSyntaxError if len(self.depth) == depth else SyntaxError
        msg = f"reader tag {tag!r} missing argument"
        raise e(msg, self.position(pos)) from None

    @staticmethod
    def _fully_qualified(tag: str):
        module, function = tag.split("..", 1)
        if re.match(rf"{C.MACROS}\.[^.]+$", function):
            function += munge("#")
        return cast(Fn, reduce(getattr, function.split("."), import_module(module)))

    def _local(self, tag: str):
        tag = tag.replace(".", force_qz_encode("."))
        try:
            return getattr(self.lissp.env[C.MACROS], tag + munge("#"))
        except (AttributeError, KeyError):
            raise SyntaxError(f"unknown tag {tag!r}", self.position())

    @staticmethod
    def escape(atom: str) -> str:
        """Process the backslashes in a token."""
        return re.sub(
            r"\\(.)", lambda m: force_qz_encode(m[1]) if m[1] in ".:" else m[1], atom
        )

    @staticmethod
    def _unicode(v: str) -> str:
        v = v.replace("\\\n", "").replace("\n", R"\n")
        val = ast.literal_eval(v)
        return v if (v := pformat(val)).startswith("(") else f"({v})"

    def _fragment(self, v: str) -> str:
        return v[1:-1].replace("||", "|")

    def _continue(self) -> SoftSyntaxError:
        return SoftSyntaxError("Incomplete string token.", self.position())

    @staticmethod
    def bare(v: str):
        """Preprocesses a `bare token`. Handles escapes and munging."""
        if not v.startswith("\\"):
            with suppress(ValueError, SyntaxError):
                if not hasattr(x := ast.literal_eval(Parser.escape(v)), "__contains__"):
                    return x
        return munge(Parser.escape(v))

    def _error(self, k: str) -> SyntaxError:
        assert k == "error", f"unknown token: {k!r}"
        return SyntaxError("can't read this", self.position())

    def _check_depth(self) -> None:
        if self.depth:
            raise SoftSyntaxError("form missing a `)`", self.position(self.depth.pop()))


def is_hissp_string(form: object) -> TypeGuard[str | tuple[Literal["quote"], str]]:
    """Determines if form would directly represent a string in Hissp.
    (A `Hissp string`.)

    Allows `readerless mode`-style strings: ``('quote','foo',)``
    and any `string literal fragment`: ``'"foo"'``
    (including the ``"('foo')"`` form produced by the Lissp reader).

    Macros often produce strings in one of these forms, via `quote` or
    `repr` on a string object.
    """
    match form:
        case ["quote", x] if C.is_node(form) and C.is_str(x):
            return True
    return bool(is_string_literal(form))


def is_lissp_unicode(form: object) -> TypeGuard[str]:
    """
    Determines if form could have been read from a Lissp `Unicode token`.

    It's not enough to check if the form has a string type.
    Several token types such as a `control token`, `symbol token`, or
    `fragment token`, read in as a `str atom`. Macros may need to
    distinguish these cases.
    """
    return C.is_str(form) and form.startswith("(") and bool(is_string_literal(form))


def is_string_literal(form: object) -> TypeGuard[str]:
    """Determines if `ast.literal_eval` on form produces a string.
    (A `string literal fragment`.)
    """
    with suppress(Exception):
        return C.is_str(ast.literal_eval(form))
    return False


def is_qualifiable(symbol: str) -> bool:
    """Determines if symbol can be qualified with a module.

    Can't be ``quote``, ``__import__``, any Python reserved word, a
    prefix auto-`gensym`, fully qualified, method syntax, or a `module
    handle`; and must be a valid identifier or attribute identifier.
    """
    return (
        symbol not in {"quote", "__import__"}
        and not _iskeyword(symbol)
        and not re.match(r"_Qz[a-z2-7]+__", symbol)
        and all(map(str.isidentifier, symbol.split(".")))
    )


def transpile(package: str | None, *modules: str) -> None:
    """Transpiles the named Python modules from Lissp.

    A ``.lissp`` file of the same name must be present in the module's
    location. The Python modules are overwritten. Missing modules are
    created. If the package is "" or ``None``, `transpile` writes non-
    packaged modules to the current working directory instead.
    """
    t = transpile_packaged if package else transpile_file
    for m in modules:
        t(f"{m}.lissp", package)


def transpile_packaged(resource: str, package: str) -> None:
    """Locates & transpiles a packaged ``.lissp`` resource file to ``.py``."""
    with resources.path(package, resource) as path:
        transpile_file(path, package)


def transpile_file(path: Path | str, package: str | None = None) -> None:
    """Transpiles a single ``.lissp`` file to ``.py`` in the same location.

    Code in ``.lissp`` files is executed upon compilation. This is
    necessary because macro definitions can alter the compilation of
    subsequent top-level forms. A packaged Lissp file must know its
    package at compile time to handle templates and macros correctly.

    After the ``.py`` file is written, `__file__` will be set to it, if
    it doesn't exist already.
    """
    path = Path(path).resolve(strict=True)
    qualname = f"{package or ''}{'.' if package else ''}{PurePath(path.name).stem}"
    L = Lissp(qualname=qualname, evaluate=True, filename=str(path))
    python = L.compile(re.sub(r"^#!.*\n", "", path.read_text("utf8")))
    (py := path.with_suffix(".py")).write_text(python, "utf8")
    L.env.setdefault("__file__", str(py))
