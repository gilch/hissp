# Copyright 2019, 2020 Matthew Egan Odendahl
# SPDX-License-Identifier: Apache-2.0
"""
Lissp's symbol munger.

Encodes Lissp symbols with special characters into valid,
human-readable (if ugly) Python identifiers,
using NFKC normalization and *x-codes*.

E.g. ``*FOO-BAR*`` becomes ``xSTAR_FOOxH_BARxSTAR_``.

X-codes are written in upper case and wrapped in an ``x`` and ``_``.
This format was chosen because it contains an underscore
and both lower-case and upper-case letters,
which makes it distinct from
`standard Python naming conventions`__:
``lower_case_with_underscores``,
``UPPER_CASE_WITH_UNDERSCORES``,
and ``CapWords``,
which makes the x-encoding (but not the normalization)
reversible in the usual cases,
and also cannot introduce a leading underscore,
which can have special meaning in Python.

__ https://www.python.org/dev/peps/pep-0008/#naming-conventions

Characters can be encoded in one of three ways:
Short names, Unicode names, and ordinals.

The `demunge` function will accept any of these encodings,
while the `munge` function will prioritize short names,
then fall back to Unicode names, then fall back to ordinals.

Short names are given in the `TO_NAME` table in this module.

Any spaces in the Unicode names are replaced with an ``x`` and
any hyphens are replaced with an ``h``.
(Unicode names are in all caps and these substitutions are lower-case.)

Ordinals are given in base 10.
"""

import re
import unicodedata
from contextlib import suppress
from typing import Dict, Hashable, Mapping, Match, TypeVar


def munge(s: str) -> str:
    """
    Lissp's symbol munger.

    Encodes Lissp symbols with special characters into valid,
    human-readable (if ugly) Python identifiers,
    using NFKC normalization and *x-codes*.

    Inputs that begin with ``:`` are assumed to be control words
    and returned unmodified.
    Full stops are handled separately, as those are meaningful to Hissp.
    """
    if s.startswith(":"):
        return s  # control word
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
        part = "".join(map(x_encode, part))
        if not part.isidentifier():
            part = force_x_encode(part[0]) + part[1:]
            assert part.isidentifier(), f"{part!r} is not identifier"
    return part


TO_NAME = {
    # ASCII control characters don't munge to names.
    "!": "xBANG_",
    '"': "x2QUOTE_",
    "#": "xHASH_",
    "$": "xDOLR_",
    "%": "xPCENT_",
    "&": "xET_",
    "'": "x1QUOTE_",
    "(": "xPAREN_",
    ")": "xTHESES_",
    "*": "xSTAR_",
    "+": "xPLUS_",
    # xCOMMA_ is fine.
    "-": "xH_",  # Hyphen-minus
    # Full stop reserved for imports and attributes.
    "/": "xSLASH_",
    # Digits only munge if first character.
    ";": "xSCOLON_",
    "<": "xLT_",  # Less Than or LefT.
    "=": "xEQ_",
    ">": "xGT_",  # Greater Than or riGhT.
    "?": "xQUERY_",
    "@": "xAT_",
    # Capital letters are always valid in Python identifiers.
    "[": "xSQUARE_",
    "\\": "xBSLASH_",
    "]": "xBRACKETS_",
    "^": "xCARET_",
    # Underscore is valid in Python identifiers.
    "`": "xGRAVE_",
    # Small letters are also always valid.
    "{": "xCURLY_",
    "|": "xBAR_",
    "}": "xBRACES_",
    # xTILDE_ is fine.
}
"""Shorter names for X-encoding."""

X_NAME = {ord(k): ord(v) for k, v in {" ": "x", "-": "h"}.items()}


def x_encode(c: str) -> str:
    """
    Converts a character to its short x-encoding,
    unless it's already valid in a Python identifier.
    """
    if ("x" + c).isidentifier():
        return c
    return force_x_encode(c)


def force_x_encode(c: str) -> str:
    """
    Converts a character to its x-encoding,
    even if it's valid in a Python identifier.
    """
    with suppress(LookupError):
        return TO_NAME[c]
    with suppress(ValueError):
        return f"x{unicodedata.name(c).translate(X_NAME)}_"
    return f"x{ord(c)}_"


K = TypeVar("K", bound=Hashable)
V = TypeVar("V")


def _reversed_1to1(mapping: Mapping[K, V]) -> Dict[V, K]:
    result = {v: k for k, v in mapping.items()}
    assert len(mapping) == len(result)
    return result


LOOKUP_NAME = _reversed_1to1(TO_NAME)
"""The inverse of `TO_NAME`."""

UN_X_NAME = _reversed_1to1(X_NAME)


def _x_decode(match: Match[str]) -> str:
    with suppress(KeyError):
        return LOOKUP_NAME[match.group()]
    with suppress(KeyError):
        return unicodedata.lookup(match.group(1).translate(UN_X_NAME))
    with suppress(ValueError):
        return chr(int(match.group(1)))
    return match.group()


def demunge(s: str) -> str:
    """The inverse of `munge`. Decodes any x-codes into characters."""
    return re.sub("x([0-9A-Zhx]+?)_", _x_decode, s)
