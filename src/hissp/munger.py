# Copyright 2019, 2020, 2021, 2024 Matthew Egan Odendahl
# SPDX-License-Identifier: Apache-2.0
"""
Lissp's `symbol token` munger.

Encodes Lissp symbol tokens with special characters into valid,
human-readable (if unpythonic) Python identifiers,
using NFKC normalization and `Quotez`.

E.g. ``*FOO-BAR*`` becomes ``QzSTAR_FOOQzH_BARQzSTAR_``.

Quotez are written in upper case and wrapped in a ``Qz`` and ``_``.
This format was chosen because it contains an underscore
and both upper-case and lower-case letters,
which makes it distinct from
`standard Python naming conventions`__:
``lower_case_with_underscores``,
``UPPER_CASE_WITH_UNDERSCORES``,
and ``CapWords``,
as well as an extremely rare bigram, "Qz",
which makes the Quotez (but not the normalization)
reversible in the usual cases,
and also cannot introduce a leading underscore,
which can have special meaning in Python.

__ https://www.python.org/dev/peps/pep-0008/#naming-conventions

Characters can be encoded in one of three ways:
Short names, Unicode names, and ordinals.

The :func:`demunge` function will accept any of these encodings,
while the :func:`munge` function will prioritize short names,
then fall back to Unicode names, then fall back to ordinals.

Short names are given in the `TO_NAME` table in this module.

Any spaces in the Unicode names are replaced with an ``x`` and
any hyphens are replaced with an ``h``.
(Unicode names are in all caps and these substitutions are lower-case.)

Ordinals are given in a hexadecimal format like ``0XF00``.
"""

import re
import unicodedata
from collections.abc import Hashable, Mapping
from contextlib import suppress
from typing import TypeVar


def munge(s: str) -> str:
    """
    Lissp's symbol munger.

    Encodes Lissp symbols with special characters into valid,
    human-readable (if unpythonic) Python identifiers,
    using NFKC normalization and `Quotez`.

    Full stops are handled separately, as those are meaningful to Hissp.
    """
    # Always normalize identifiers:
    # >>> 𝐀 = 'MATHEMATICAL BOLD CAPITAL A'
    # >>> 'A' in globals()
    # True
    s = unicodedata.normalize("NFKC", s)
    if s.isidentifier():
        return s  # Nothing to munge.
    return ".".join(_munge_part(part) for part in s.split("."))


def _munge_part(part):
    if part:
        part = "".join(map(qz_encode, part))
        if not part.isidentifier():
            part = force_qz_encode(part[0]) + part[1:]
            assert part.isidentifier(), f"{part!r} is not identifier"
    return part


QUOTEZ = "Qz{}_"
"""Format string for creating `Quotez`."""

FIND_QUOTEZ = re.compile(QUOTEZ.format("([0-9A-Z][0-9A-Zhx]*?)"))
"""Regex pattern to find `Quotez`. Used by `demunge`."""

TO_NAME = {
    k: QUOTEZ.format(v)
    for k, v in {
        # ASCII control characters don't munge to names.
        "!": "BANG",
        '"': "QUOT",
        "#": "HASH",
        "$": "DOLR",
        "%": "PCENT",
        "&": "ET",
        "'": "APOS",
        "(": "LPAR",
        ")": "RPAR",
        "*": "STAR",
        "+": "PLUS",
        # COMMA is fine.
        "-": "H",  # Hyphen-minus
        ".": "DOT",  # Doesn't munge by default.
        "/": "SOL",
        # Digits only munge if first character.
        # COLON is fine.
        ";": "SEMI",
        "<": "LT",  # Less Than or LefT.
        "=": "EQ",
        ">": "GT",  # Greater Than or riGhT.
        "?": "QUERY",
        "@": "AT",
        # Capital letters are always valid in Python identifiers.
        "[": "LSQB",
        "\\": "BSOL",
        "]": "RSQB",
        "^": "HAT",
        # Underscore is valid in Python identifiers.
        "`": "GRAVE",
        # Small letters are also always valid.
        "{": "LCUB",
        "|": "VERT",
        "}": "RCUB",
        # TILDE is fine.
    }.items()
}
"""Shorter names for `Quotez`."""

_QZ_NAME = {ord(k): ord(v) for k, v in {" ": "x", "-": "h"}.items()}


def qz_encode(c: str) -> str:
    """
    Converts a character to its `Quotez` encoding,
    unless it's already valid in a Python identifier.
    """
    if ("x" + c).isidentifier():
        return c
    return force_qz_encode(c)


def force_qz_encode(c: str) -> str:
    """
    Converts a character to its `Quotez` encoding,
    even if it's valid in a Python identifier.
    """
    with suppress(LookupError):
        return TO_NAME[c]
    with suppress(ValueError):
        return QUOTEZ.format(unicodedata.name(c).translate(_QZ_NAME))
    return QUOTEZ.format(f"{ord(c):#X}")


K = TypeVar("K", bound=Hashable)
V = TypeVar("V")


def _inverse_1to1(mapping: Mapping[K, V]) -> dict[V, K]:
    result = {v: k for k, v in mapping.items()}
    assert len(mapping) == len(result)
    return result


LOOKUP_NAME = _inverse_1to1(TO_NAME)
"""The inverse of `TO_NAME`."""

_UN_QZ_NAME = _inverse_1to1(_QZ_NAME)


def _qz_decode(match: re.Match[str]) -> str:
    with suppress(KeyError):
        return LOOKUP_NAME[match.group()]
    with suppress(KeyError):
        return unicodedata.lookup(match.group(1).translate(_UN_QZ_NAME))
    with suppress(ValueError):
        if match.group(1).startswith("0X"):
            return chr(int(match.group(1), 16))
    return match.group()


def demunge(s: str) -> str:
    """The inverse of :func:`munge`. Decodes any `Quotez` into characters.

    Characters can be encoded in one of three ways:
    Short names, Unicode names, and ordinals.
    ``demunge`` will decode any of these. Even though :func:`munge` will
    consistently pick only one of these for any given character,
    which Unicode characters have names depends on the Python version.

    ``demunge`` will also leave the remaining text as-is, along with any
    invalid Quotez.

    >>> demunge("QzFOO_QzGT_QzHYPHENhMINUS_Qz0X3E_bar")
    'QzFOO_>->bar'
    """
    return FIND_QUOTEZ.sub(_qz_decode, s)
