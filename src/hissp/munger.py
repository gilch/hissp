# Copyright 2019 Matthew Egan Odendahl
# SPDX-License-Identifier: Apache-2.0

import re
import unicodedata
from contextlib import suppress
from typing import Dict, Hashable, Mapping, Match, TypeVar

def munge(s: str) -> str:
    if s.startswith(":"):
        return s  # control word
    # Always normalize identifiers:
    # >>> 𝐀 = 'MATHEMATICAL BOLD CAPITAL A'
    # >>> 'A' in globals()
    # True
    s = unicodedata.normalize("NFKC", s)
    if s.isidentifier():
        return s  # Nothing to munge.
    return ".".join(munge_part(part) for part in s.split('.'))


def munge_part(part):
    if part:
        part = "".join(map(x_quote, part))
        if not part.isidentifier():
            part = force_x_quote(part[0]) + part[1:]
            assert part.isidentifier(), f"{part!r} is not identifier"
    return part


# Shorter munging names for some ASCII characters.
TO_NAME = {
    # ASCII control characters don't munge to names.
    "!": "xBANG_",
    "\"": "x2QUOTE_",
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
X_NAME = {ord(k): ord(v) for k, v in {" ": "x", "-": "h"}.items()}


def x_quote(c: str) -> str:
    with suppress(LookupError):
        return TO_NAME[c]
    if ('x'+c).isidentifier():
        return c
    return force_x_quote(c)

def force_x_quote(c: str) -> str:
    with suppress(ValueError):
        return f"x{unicodedata.name(c).translate(X_NAME)}_"
    return f"x{ord(c)}_"

K = TypeVar("K", bound=Hashable)
V = TypeVar("V")


def reversed_1to1(mapping: Mapping[K, V]) -> Dict[V, K]:
    result = {v: k for k, v in mapping.items()}
    assert len(mapping) == len(result)
    return result


LOOKUP_NAME = reversed_1to1(TO_NAME)
UN_X_NAME = reversed_1to1(X_NAME)


def un_x_quote(match: Match[str]) -> str:
    with suppress(KeyError):
        return LOOKUP_NAME[match.group()]
    with suppress(KeyError):
        return unicodedata.lookup(match.group(1).translate(UN_X_NAME))
    with suppress(ValueError):
        return chr(int(match.group(1)))
    return match.group()


def demunge(s: str) -> str:
    return re.sub("x([0-9A-Zhx]+?)_", un_x_quote, s)
