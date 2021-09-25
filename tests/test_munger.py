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
            "QzTILDE_QzBANG_QzAT_QzHASH_QzDOLR_QzPCENT_QzCARET_QzET_QzSTAR_QzLPAR_QzRPAR_"
            "_QzPLUS_QzLCUB_QzRCUB_QzBAR_QzCOLON_QzQUOT_QzLT_QzGT_QzQUERY_QzGRAVE_Qz_QzEQ_"
            "QzLSQB_QzRSQB_QzBSOL_QzSEMI_QzAPOS_QzCOMMA_.QzSOL_"
        )

    @given(st.text(st.characters(["Sm"]), min_size=1))
    def test_munge_symbol(self, s):
        self.assertTrue(munger.munge(s).isidentifier())
