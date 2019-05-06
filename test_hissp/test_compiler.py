# Copyright 2019 Matthew Egan Odendahl
# SPDX-License-Identifier: Apache-2.0

import re
from unittest import TestCase

import hypothesis.strategies as st
from hypothesis import given

from hissp import compiler
from hissp import munger

quoted = (
    st.none()
    | st.booleans()
    | st.integers()
    | st.floats(allow_nan=False)
    | st.complex_numbers(allow_nan=False)
    | st.binary()  # bytes
)
literals = st.recursive(
    # strings, bytes, numbers, tuples, lists, dicts, sets, booleans, and None
    quoted,
    lambda children: st.lists(children)
    | st.sets(quoted)
    | st.builds(tuple, st.lists(children))
    | st.dictionaries(quoted, children),
)


class TestCompileGeneral(TestCase):
    @given(
        literals
        | st.dates()
        | st.datetimes()
        | st.decimals(allow_nan=False)
        | st.fractions()
        | st.timedeltas()
        | st.times()
        | st.uuids()
    )
    def test_compile_pickle(self, form):
        self.assertEqual(form, eval(compiler.Compiler().pickle(form)))

    @given(literals)
    def test_compile_literal(self, form):
        self.assertEqual(form, eval(compiler.Compiler().quoted(form)))

    @given(
        st.characters(
            blacklist_characters='(){}[];".',
            whitelist_categories=["Lu", "Ll", "Lt", "Lm", "Lo", "Nl", "Sm"],
        )
    )
    def test_un_x_quote(self, char):
        x = munger.x_quote(char)
        self.assertTrue(("x" + x).isidentifier())
        match = re.fullmatch("x(.*?)_", x)
        if match:
            self.assertEqual(char, munger.un_x_quote(match))

    @given(st.text(min_size=1))
    def test_demunge(self, s: str):
        x = compiler.munge(s)
        self.assertEqual(x, munger.munge(munger.demunge(x)))
        if "x" not in s:
            self.assertEqual(s, munger.demunge(x))

    def test_munge_basic(self):
        self.assertEqual(
            munger.munge("~!@#$%^&*+`-=|\:'<>?,/"),
            "xTILDE_xBANG_xAT_xHASH_xDOLLAR_xPERCENT_xCARET_xET_xSTAR_xPLUS_xGRAVE_xH_"
            "xEQ_xBAR_xBSLASH_xCOLON_xQUOTE_xLT_xGT_xQUERY_xCOMMA_xSLASH_",
        )

    @given(
        st.text(st.characters(["Lu", "Ll", "Lt", "Lm", "Lo", "Nl", "Sm"]), min_size=1)
    )
    def test_munge_symbol(self, s):
        self.assertTrue(munger.munge(s).isidentifier())
