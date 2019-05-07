# Copyright 2019 Matthew Egan Odendahl
# SPDX-License-Identifier: Apache-2.0

import ast
import re
from pprint import pprint

from typing import NewType, Tuple, Iterator

TOKENS = re.compile(
    r"""(?x)
 (?P<open>\()
|(?P<close>\))
|(?P<string>"(?:\\.|\\\n|[^"]|\\")*")
|(?P<comment>;.*)
|(?P<whitespace>[\n ]+)
|(?P<macro>[#][^ \n"()]*(?=[\n ("]))
|(?P<symbol>[^ \n"()#]+)
"""
)

Token = NewType("Token", Tuple[str, str])


def lex(code: str) -> Iterator[Token]:
    pos = 0
    while pos < len(code):
        match = TOKENS.match(code, pos)
        if match is None:
            lines = code.split("\n")
            good = code[0:pos].split("\n")
            line = len(good)
            column = len(good[-1])
            raise SyntaxError(
                f"""\
Unexpected token at {line}:{column}
{lines[line-1]}
{" "*column}^
"""
            )
        assert match.end() > pos, match.groups()
        pos = match.end()
        yield Token((match.lastgroup, match.group()))


def parse(tokens: Iterator[Token], depth=0) -> Iterator[tuple]:
    for k, v in tokens:
        if k == "open":
            yield (*parse(tokens, depth + 1),)
        elif k == "close":
            return
        elif k == "string":
            yield 'quote', ast.literal_eval(v.replace("\n", r"\n"))
        elif k in {"comment", "whitespace"}:
            continue
        elif k == "macro":
            form = next(parse(tokens))
            yield parse_macro(v, form)
        elif k == "symbol":
            try:
                yield ast.literal_eval(v)
            except (ValueError, SyntaxError):
                yield v
        else:
            assert False, "unknown token: " + repr(k)
    if depth:
        SyntaxError("Ran out of tokens before completing form.")


def parse_macro(tag: str, form) -> Iterator[tuple]:
    if tag == "#'":
        return ("quote", form)
    # elif tag == "#`":
    #     if isinstance(form, tuple):
    #         yield (("quote", e) for e in form),
    #     else:
    #         yield ("quote", form)
    # elif tag == "#,":
    #     assert form[0] == "quote"
    #     yield form[1],
    # elif tag == "#,@":
    #     assert form[0] == "quote"
    #     yield form[1]
    else:
        raise ValueError(f"Unknown reader macro {tag}")


def reads(code, verbose=False):
    res = parse(lex(code))
    if verbose:
        res = list(res)
        pprint(res)
    return res


def read(file, verbose=False):
    with open(file) as f:
        return reads(f.read(), verbose)
