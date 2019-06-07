import re
from doctest import ELLIPSIS
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
        self._EXAMPLE_RE = _EXAMPLE_RE = re.compile(
            r"""
        (?P<lissp>
             (?:^   [ ]* [#]>[ ] .*)
             (?:\n  [ ]* [#]\.\. .*)*)
             \n?
         """
            + self._EXAMPLE_RE.pattern,
            re.MULTILINE | re.VERBOSE,
        )

    def lissp(self, source):
        lissp = LISSP.match(source)
        assert lissp, "\n" + source
        lissp = STRIP_LISSP.sub("", lissp.group())
        return lissp

    def evaluate(self, example, parser=Parser()):
        lissp = self.lissp(example.document.text[example.start : example.end])
        python = example.parsed.source
        parser.compiler.ns = example.namespace
        hissp = parser.reads(lissp)
        compiled = parser.compiler.compile(hissp) + "\n"
        assert compiled == python, dedent(
            f"""
            EXPECTED PYTHON:
            {indent(python, "  ")}
            ACTUALLY COMPILED TO:
            {indent(compiled, "  ")}
            .
            """
        )
        return super().evaluate(example)


pytest_collect_file = Sybil(
    parsers=[ParseLissp(optionflags=ELLIPSIS)], pattern="*.rst", filenames={"README.md"}
).pytest()
