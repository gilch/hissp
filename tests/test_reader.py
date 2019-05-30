from collections import Counter
from unittest import TestCase

import hypothesis.strategies as st
from hypothesis import given

from hissp import reader


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
