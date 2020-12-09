# Copyright 2019, 2020 Matthew Egan Odendahl
# SPDX-License-Identifier: Apache-2.0

from unittest import TestCase

import hypothesis.strategies as st
import unicodedata
from hypothesis import given

from hissp import munger


class TestMunger(TestCase):
    @given(st.text(min_size=1))
    def test_demunge(self, s: str):
        x = munger.munge(s)
        self.assertEqual(x, munger.munge(munger.demunge(x)))
        if not s.startswith(":") and "x" not in s:
            self.assertEqual(unicodedata.normalize("NFKC", s), munger.demunge(x))

    def test_munge_basic(self):
        self.assertEqual(
            munger.munge(r"""~!@#$%^&*()_+{}|:"<>?`-=[]\;',./"""),
            "xTILDE_xBANG_xAT_xHASH_xDOLR_xPCENT_xCARET_xET_xSTAR_xPAREN_xTHESES_"
            "_xPLUS_xCURLY_xBRACES_xBAR_xCOLON_x2QUOTE_xLT_xGT_xQUERY_xGRAVE_xH_xEQ_"
            "xSQUARE_xBRACKETS_xBSLASH_xSCOLON_x1QUOTE_xCOMMA_.xSLASH_"
        )

    @given(st.text(st.characters(["Sm"]), min_size=1))
    def test_munge_symbol(self, s):
        self.assertTrue(munger.munge(s).isidentifier())
