# Copyright 2019, 2020, 2021, 2022 Matthew Egan Odendahl
# SPDX-License-Identifier: Apache-2.0
import re
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
            munger.munge(R"""~!@#$%^&*()_+{}|:"<>?`-=[]\;',./"""),
            "Tilde_Bang_At_Hash_Dolr_Pcent_Hat_Et_Star_Lpar_"
            "Rpar__Plus_Lcub_Rcub_Vert_Colon_Quot_Lt_Gt_Eh_"
            "Grave____Eq_Lsqb_Rsqb_Bsol_Scoln_Apos_Comma_.Fsol_",
        )

    @given(st.text(st.characters(whitelist_categories=["Sm"]), min_size=1))
    def test_munge_symbol(self, s):
        self.assertTrue(munger.munge(s).isidentifier())

    @given(st.characters(whitelist_categories=["Lu", "Ll", "Lt", "Nl", "Sm"]))
    def test_decode(self, char):
        x = munger.encode(char)
        self.assertTrue(("x" + x).isidentifier())
        match = re.fullmatch("x(.*?)_", x)
        if match:
            self.assertEqual(char, munger._decode(match))
