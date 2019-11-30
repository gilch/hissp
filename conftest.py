import re
from collections.abc import Container
from doctest import ELLIPSIS
from fnmatch import fnmatch
from textwrap import dedent, indent

from sybil import Sybil
from sybil.parsers.doctest import DocTestParser

from hissp.reader import Parser

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

    def lissp(self, source):
        lissp = LISSP.match(source)
        if not lissp:
            return
        assert lissp, "\n" + source
        lissp = STRIP_LISSP.sub("", lissp.group())
        return lissp

    def evaluate(self, example, parser=Parser()):
        lissp = self.lissp(example.document.text[example.start : example.end])
        if lissp:
            python = example.parsed.source
            parser.compiler.ns = example.namespace
            hissp = parser.reads(lissp)
            compiled = parser.compiler.compile(hissp) + "\n"
            assert norm_gensym_eq(compiled, python), dedent(
                f"""
                EXPECTED PYTHON:
                {indent(python, "  ")}
                ACTUALLY COMPILED TO:
                {indent(compiled, "  ")}
                .
                """
            )
        return super().evaluate(example)


def norm_gensym_eq(compiled, python):
    """The special gensym suffix ``xAUTO..._`` will match any number."""
    return re.fullmatch(
        re.sub(r"xAUTO\\\.\\\.\\\._", r"xAUTO\\d+_", re.escape(python)), compiled
    )


class Globs(Container):
    def __init__(self, *globs):
        self.globs = globs

    def __contains__(self, item):
        return any(fnmatch(item, glob) for glob in self.globs)


pytest_collect_file = Sybil(
    parsers=[ParseLissp(optionflags=ELLIPSIS)], filenames=Globs("*.md", "*.rst")
).pytest()
