from collections import Counter
from unittest import TestCase
from unittest.mock import ANY

import hypothesis.strategies as st
from hypothesis import given

from hissp import reader

STRING_ANY_ = [("string", ANY)]


class TestReader(TestCase):
    def setUp(self) -> None:
        self.parser = reader.Parser()

    @given(st.text("(1)", max_size=20))
    def test_balance(self, lissp):
        tally = Counter(lissp)
        if tally["("] != tally[")"]:
            self.assertRaisesRegex(
                SyntaxError, r"^Un(?:opened|closed)", list, self.parser.reads(lissp)
            )

    @given(st.text(max_size=5))
    def test_string(self, lissp):
        lissp = lissp.replace("\\", "\\\\").replace('"', r"\"")
        lissp = f'"{lissp}"'
        self.assertEqual([*reader.lex(lissp)], STRING_ANY_)
