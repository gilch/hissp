# Copyright 2019 Matthew Egan Odendahl
# SPDX-License-Identifier: Apache-2.0

import re
import unicodedata
from contextlib import suppress
from typing import Dict, Hashable, Mapping, Match, TypeVar


def munge(s: str) -> str:
    if s.startswith(":") or s.isidentifier():
        return s
    return "".join(map(x_quote, s))


TO_NAME = {
    "~": "xTILDE_",
    "`": "xGRAVE_",
    "!": "xBANG_",
    "@": "xAT_",
    "#": "xHASH_",
    "$": "xDOLR_",
    "%": "xPCENT_",
    "^": "xCARET_",
    "&": "xET_",
    "*": "xSTAR_",
    "(": "xPAREN_",
    ")": "xTHESES_",
    "-": "xH_",  # Hyphen
    "+": "xPLUS_",
    "=": "xEQ_",
    "{": "xCURLY_",
    "[": "xSQUARE_",
    "}": "xBRACES_",
    "]": "xBRACKETS_",
    "|": "xBAR_",
    "\\": "xBSLASH_",
    ":": "xCOLON_",
    ";": "xSCOLON_",
    '"': "x2QUOTE_",
    "'": "xQUOTE_",
    "<": "xLT_",  # Less Than or LefT.
    ",": "xCOMMA_",
    ">": "xGT_",  # Greater Than or riGhT.
    "?": "xQUERY_",
    "/": "xSLASH_",
    " ": "xSPACE_",
}
X_NAME = {ord(k): ord(v) for k, v in {" ": "x", "-": "h"}.items()}


def x_quote(c: str) -> str:
    return (
        TO_NAME.get(c)
        or unicodedata.category(c) == "Sm"
        and f"x{unicodedata.name(c).translate(X_NAME)}_"
        or c
    )


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
        return LOOKUP_NAME.get(match.group()) or unicodedata.lookup(
            match.group(1).translate(UN_X_NAME)
        )
    return match.group()


def demunge(s: str) -> str:
    return re.sub("x([0-9A-Zhx]+?)_", un_x_quote, s)
