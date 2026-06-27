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
        part = re.sub("(?<![-_])(?<!^)-(?![-_]|$)", "___", part)
        part = "".join(map(encode, part))
        if not part.isidentifier():
            part = force_encode(part[0]) + part[1:]
            assert part.isidentifier(), f"{part!r} is not identifier"
    return part


FIND_MUNGED = re.compile("(Ox[A-F0-9]+|[A-Z][a-z0-9]+|[A-Z][XHa-z0-9]+X)_")
"""Regex pattern to find munged characters. Used by `demunge`."""

TO_NAME = {
    # ASCII control characters don't munge to names.
    # Space_ is fine.
    "!": "Bang_",
    '"': "Quot_",
    "#": "Hash_",
    "$": "Dolr_",
    "%": "Pcent_",
    "&": "Et_",
    "'": "Apos_",
    "(": "Lpar_",
    ")": "Rpar_",
    "*": "Star_",
    "+": "Plus_",
    # Comma_ is fine.
    "-": "Dash_",
    ".": "Stop_",  # Doesn't munge by default.
    "/": "Fsol_",
    # Digits only munge if first character.
    # Colon_ is fine.
    ";": "Scoln_",
    "<": "Lt_",  # Less Than or LefT.
    "=": "Eq_",
    ">": "Gt_",  # Greater Than or riGhT.
    "?": "Eh_",  # Nice day, eh?
    "@": "At_",
    # Capital letters are always valid in Python identifiers.
    "[": "Lsqb_",
    "\\": "Bsol_",
    "]": "Rsqb_",
    "^": "Hat_",
    # Underscore is valid in Python identifiers.
    "`": "Grave_",
    # Small letters are also always valid.
    "{": "Lcub_",
    "|": "Vert_",
    "}": "Rcub_",
    # Tilde_ is fine.
}
"""Shorter names for `Quotez`."""

_XH = {ord(k): ord(v) for k, v in {" ": "X", "-": "H"}.items()}


def encode(c: str) -> str:
    """
    Converts a character to its munged encoding,
    unless it's already valid in a Python identifier.
    """
    if ("x" + c).isidentifier():
        return c
    return force_encode(c)


def force_encode(c: str) -> str:
    """
    Converts a character to its munged encoding,
    even if it's valid in a Python identifier.
    """
    with suppress(LookupError):
        return TO_NAME[c]
    with suppress(ValueError):
        name = unicodedata.name(c)
        tail = re.sub("^(.*[XH].*)$", R"\1X", name[1:].lower().translate(_XH))
        return f"{name[0]}{tail}_"
    return f"Ox{ord(c):X}_"


K = TypeVar("K", bound=Hashable)
V = TypeVar("V")


def _inverse_1to1(mapping: Mapping[K, V]) -> dict[V, K]:
    result = {v: k for k, v in mapping.items()}
    assert len(mapping) == len(result)
    return result


LOOKUP_NAME = _inverse_1to1(TO_NAME)
"""The inverse of `TO_NAME`."""

_UN_XH = _inverse_1to1(_XH)


def _decode(match: re.Match[str]) -> str:
    with suppress(KeyError):
        return LOOKUP_NAME[match[0]]
    name = match[1][0] + match[1][1:].translate(_UN_XH)
    with suppress(KeyError):
        return unicodedata.lookup(name.upper().removesuffix(" "))
    with suppress(ValueError):
        if match[1].startswith("Ox"):
            return chr(int(match[1][2:], 16))
    return match[0]


def demunge(s: str) -> str:
    """The inverse of :func:`munge`. Decodes any `Quotez` into characters.

    Characters can be encoded in one of three ways:
    Short names, Unicode names, and ordinals.
    ``demunge`` will decode any of these. Even though :func:`munge` will
    consistently pick only one of these for any given character,
    which Unicode characters have names depends on the Python version.

    ``demunge`` will also leave the remaining text as-is, along with any
    invalid Quotez.

    >>> demunge("Foo_Gt_HyphenHminusX_Ox3E_bar")
    'Foo_>->bar'
    """
    return re.sub("(?<!_)(?<!^)___(?!_|$)", "-", FIND_MUNGED.sub(_decode, s))
