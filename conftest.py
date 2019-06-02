import re
from textwrap import dedent, indent

from sybil import Region, Sybil

from hissp.__main__ import evaluate
from hissp.reader import Parser

LISSP_START = re.compile(r"(?=#> )")
LISSP_END = re.compile(r"\n\n")
LISSP = re.compile(r"#> .*\n(?:#\.\..*\n)*")
PYTHON = re.compile(r">>> .*(?:\n\.\.\..*)*")
STRIP_LISSP = re.compile(r"(?m)^#(?:> |\.\.)")
STRIP_PYTHON = re.compile(r"(?m)^(?:>>> |\.\.\. )")


def parse_markdown_lisp(document):
    for start_match, end_match, source in document.find_region_sources(
        LISSP_START, LISSP_END
    ):
        lissp = LISSP.match(source)
        python = PYTHON.match(source[lissp.end() :])
        assert lissp, "\n" + source
        assert python, "\n" + source
        lissp = STRIP_LISSP.sub("", lissp.group())
        python = STRIP_PYTHON.sub("", python.group())
        parsed = lissp, python
        yield Region(
            start_match.start(), end_match.end(), parsed, evaluate_lissp_region
        )


def evaluate_lissp_region(example, parser=Parser()):
    lissp, python = example.parsed
    parser.compiler.ns = example.namespace
    lissp = parser.reads(lissp)
    got = evaluate(lissp, parser)
    assert got == python, dedent(
        f"""
        EXPECTED:
        {indent(python, "  ")}
        GOT:
        {indent(got, "  ")}
        .
        """
    )


pytest_collect_file = Sybil(parsers=[parse_markdown_lisp], pattern="*.md").pytest()
