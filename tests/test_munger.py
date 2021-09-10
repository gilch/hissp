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
            "QzTILDE_QzBANG_QzAT_QzHASH_QzDOLR_QzPCENT_QzCARET_QzET_QzSTAR_QzPAREN_QzTHESES_"
            "_QzPLUS_QzCURLY_QzBRACES_QzBAR_QzCOLON_Qz2QUOTE_QzLT_QzGT_QzQUERY_QzGRAVE_Qz_QzEQ_"
            "QzSQUARE_QzBRACKETS_QzBSLASH_QzSCOLON_Qz1QUOTE_QzCOMMA_.QzSLASH_"
        )

    @given(st.text(st.characters(["Sm"]), min_size=1))
    def test_munge_symbol(self, s):
        self.assertTrue(munger.munge(s).isidentifier())
