from unittest import TestCase

import hypothesis.strategies as st
from hypothesis import given

from hissp import munger


class TestMunger(TestCase):
    @given(st.text(min_size=1))
    def test_demunge(self, s: str):
        x = munger.munge(s)
        self.assertEqual(x, munger.munge(munger.demunge(x)))
        if "x" not in s:
            self.assertEqual(s, munger.demunge(x))

    def test_munge_basic(self):
        self.assertEqual(
            munger.munge("~!@#$%^&*+`-=|\:'<>?,/"),
            "xTILDE_xBANG_xAT_xHASH_xDOLLAR_xPERCENT_xCARET_xET_xSTAR_xPLUS_xGRAVE_xH_"
            "xEQ_xBAR_xBSLASH_xCOLON_xQUOTE_xLT_xGT_xQUERY_xCOMMA_xSLASH_",
        )

    @given(st.text(st.characters(["Sm"]), min_size=1))
    def test_munge_symbol(self, s):
        self.assertTrue(munger.munge(s).isidentifier())
