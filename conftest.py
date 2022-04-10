# Copyright 2019, 2020, 2022 Matthew Egan Odendahl
# SPDX-License-Identifier: Apache-2.0

import re
from collections.abc import Container
from difflib import context_diff
from doctest import ELLIPSIS
from fnmatch import fnmatch
from textwrap import indent

from sybil import Sybil
from sybil.parsers.doctest import DocTestParser

from hissp.reader import Lissp

LISSP = re.compile(r" *#> .*\n(?: *#\.\..*\n)*")
STRIP_LISSP = re.compile(r"(?m)^ *#(?:> |\.\.)")


class ParseLissp(DocTestParser):
    """
    Like Sybil's DocTestParser, but also checks the Lissp compilation.
    """

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self._EXAMPLE_RE = re.compile(
            r"""
            (?P<lissp>
                 (?:^   [ ]* [#]>[ ] .*)
                 (?:\n  [ ]* [#]\.\. .*)*)?
                 \n?
            """
            + self._EXAMPLE_RE.pattern,
            re.MULTILINE | re.VERBOSE,
        )

    def __call__(self, document, *a, **kw):
        assert type(document.text) is str
        if document.path.endswith(".lissp"):
            document.text = re.sub(
                r"(?m)(^ *! *;)", lambda m: " " * len(m[1]), document.text
            )
        return super().__call__(document, *a, **kw)

    def lissp(self, source):
        lissp = LISSP.match(source)
        if not lissp:
            return
        assert lissp, "\n" + source
        lissp = STRIP_LISSP.sub("", lissp.group())
        return lissp

    def evaluate(self, example, parser=Lissp()):
        lissp = self.lissp(example.document.text[example.start : example.end])
        if lissp:
            python = example.parsed.source
            parser.compiler.ns = example.namespace
            hissp = parser.reads(lissp)
            compiled = parser.compiler.compile(hissp) + "\n"
            assert norm_gensym_eq(compiled, python), "  \n" + "".join(
                context_diff(
                    norm_gensyms(python),
                    norm_gensyms(compiled),
                    fromfile="expected in doc",
                    tofile="actually compiled to",
                )
            )
        return super().evaluate(example)


def norm_gensym_eq(compiled, python):
    """The special gensym prefix ``_QzNo..._`` will match regardless of number."""
    return re.fullmatch(
        re.sub(r"_QzNo\d+_", r"_QzNo\\d+_", re.escape(python)), compiled
    )


def norm_gensyms(s):
    s = re.sub(r"_QzNo\d+_", r"_QzNo000_", s)
    return indent(s, " " * 2).splitlines(True)


class Globs(Container):
    def __init__(self, *globs):
        self.globs = globs

    def __contains__(self, item):
        return any(fnmatch(item, glob) for glob in self.globs)


pytest_collect_file = Sybil(
    parsers=[ParseLissp(optionflags=ELLIPSIS)],
    filenames=Globs("*.md", "*.rst", "*.lissp"),
).pytest()
