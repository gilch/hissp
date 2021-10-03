# Copyright 2019, 2020, 2021 Matthew Egan Odendahl
# SPDX-License-Identifier: Apache-2.0

import re
from unittest import TestCase

import hypothesis.strategies as st
from hypothesis import given

from hissp import compiler, munger

quoted = (
    st.none()
    | st.booleans()
    | st.integers()
    | st.floats(allow_nan=False)
    | st.complex_numbers(allow_nan=False)
    | st.binary(max_size=13)  # bytes
)
literals = st.recursive(
    # strings, bytes, numbers, tuples, lists, dicts, sets, booleans, and None
    quoted,
    lambda children: st.lists(children)
    | st.sets(quoted)
    | st.builds(tuple, st.lists(children))
    | st.dictionaries(quoted, children),
    max_leaves=5
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
        self.assertEqual(form, eval(compiler.Compiler().atom(form)))

    @given(
        st.characters(
            whitelist_categories=["Lu", "Ll", "Lt", "Nl", "Sm"],
        )
    )
    def test_un_x_quote(self, char):
        x = munger.qz_encode(char)
        self.assertTrue(("x" + x).isidentifier())
        match = re.fullmatch("x(.*?)_", x)
        if match:
            self.assertEqual(char, munger._qz_decode(match))

    def test_maybe_macro_error(self):
        with self.assertRaises(compiler.CompileError):
            compiler.readerless(('hissp.basic.._macro_.foobar',))
