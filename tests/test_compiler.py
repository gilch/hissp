# Copyright 2019, 2020, 2021, 2022 Matthew Egan Odendahl
# SPDX-License-Identifier: Apache-2.0

from unittest import TestCase

import hypothesis.strategies as st
from hypothesis import given

from hissp import compiler
from .util import dedented

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
    max_leaves=5,
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
        self.assertEqual(form, eval(compiler.Compiler().atomic(form)))

    def test_maybe_macro_error(self):
        with self.assertRaises(compiler.CompileError):
            compiler.readerless(("hissp.macros.._macro_.foobar",))

    def test_compile_method(self):
        msg = r"self must be paired with :\?"
        with self.assertRaisesRegex(compiler.CompileError, msg):
            compiler.readerless(('.hex',':','self',2.0))  # fmt: skip

    def test_post_compile_warn(self):
        c = compiler.Compiler("oops")
        with self.assertWarns(compiler.PostCompileWarning):
            python = c.compile([
                ('operator..truediv',0,0,),
                ('print',('quote','oops',),),
            ])  # fmt: skip
        self.assertIn(
            """\
            __import__('operator').truediv(
              (0),
              (0))

            # Traceback (most recent call last):"""
            // dedented,
            python,
        )
        self.assertIn(
            """\
            # ZeroDivisionError: division by zero
            #\N{space}

            print(
              'oops')"""
            // dedented,
            python,
        )
