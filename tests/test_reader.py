# Copyright 2019, 2020, 2021, 2022 Matthew Egan Odendahl
# SPDX-License-Identifier: Apache-2.0

import math
from collections import Counter
from fractions import Fraction
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import ANY

import hypothesis.strategies as st
from hissp.reader import SoftSyntaxError
from hypothesis import given

from hissp import reader
from .util import dedented

UNICODE_ANY_ = [("unicode", ANY, ANY)]


class TestReader(TestCase):
    def setUp(self) -> None:
        self.reader = reader.Lissp()

    @given(st.text("(\n 1)", max_size=20))
    def test_balance(self, lissp):
        tally = Counter(lissp)
        if tally["("] != tally[")"]:
            self.assertRaisesRegex(
                SyntaxError,
                r"too many `\)`s|form missing a `\)`",
                list,
                self.reader.reads(lissp),
            )

    @given(st.text(max_size=5))
    def test_string(self, lissp):
        lissp = lissp.replace("\\", "\\\\").replace('"', R"\"")
        lissp = f'"{lissp}"'
        self.assertEqual([*reader.Lexer(lissp)], UNICODE_ANY_)

    def test_examples(self):
        for k, v in EXPECTED.items():
            with self.subTest(code=k, parsed=v):
                print(k)
                lex_k = [*reader.Lexer(k)]
                print(lex_k)
                parsed = [*self.reader.parse(reader.Lexer(k))]
                print(parsed)
                self.assertEqual(v, parsed)
                print("OK")

    def test_auto_qualification(self):
        self.assertEqual(
            [("",
              ":",":?",("quote","__main__..QzMaybe_.x"),
              ":?",("quote","__main__..x"),
              ":?",("quote","__main__..x"),
              ":?",("",
                    ":",":?",("quote","__main__..QzMaybe_.y"),
                    ":?",("quote", "__main__..y"),
                    ":?",""),
              ":?",("",":",":?",1, ":?",("quote","__main__..z"), ":?",""),
              ":?","")
             ],
            [*self.reader.reads("`(x x x (y y) (1 z))")],
        )  # fmt: skip

    def test_module_qualification(self):
        self.reader.env.update(x=1, y=2, z=3)
        self.assertEqual(
            [("",
              ":",":?",("quote","__main__..QzMaybe_.x"),
              ":?",("quote","__main__..x"),
              ":?",("quote","__main__..x"),
              ":?",("",
                    ":",":?",("quote","__main__..QzMaybe_.y"),
                    ":?",("quote","__main__..y"),
                    ":?",""),
              ":?",("",":",":?",1, ":?",("quote","__main__..z"), ":?",""),
              ":?","")
             ],
            [*self.reader.reads("`(x x x (y y) (1 z))")],
        )  # fmt: skip

    def test_macro_qualification(self):
        self.reader.env.update(_macro_=SimpleNamespace(x=1, y=2, z=3))
        self.assertEqual(
            [("",
              ":",":?",("quote","__main__.._macro_.x"),
              ":?",("quote","__main__..x"),
              ":?",("quote","__main__..x"),
              ":?",("",
                    ":",":?",("quote","__main__.._macro_.y"),
                    ":?",("quote","__main__..y"),
                    ":?",""),
              ":?",("",":",":?",1, ":?",("quote","__main__..z"), ":?",""),
              ":?","")
             ],
            [*self.reader.reads("`(x x x (y y) (1 z))")],
        )  # fmt: skip

    def test_no_qualification(self):
        self.assertEqual(
            [("",":",":?",("quote",".x"), ":?",""),
             ("",":",":?",("quote","quote"), ":?",1, ":?",""),
             ("",":",":?",("quote","lambda"), ":?",":", ":?",""),
             ("quote","__import__"),
             ("quote","_Qzabcdefg__"),
             ("quote","foo..bar"),
             ("quote","foo.")],
            [*self.reader.reads(
                "`(.x) `(quote 1) `(lambda :) `__import__ `_Qzabcdefg__ `foo..bar `foo."
            )],
        )  # fmt: skip

    def test_auto_qualify_attr(self):
        self.reader.env.update(x=SimpleNamespace(y=1), int=SimpleNamespace(float=1))
        self.assertEqual(
            [("",":",
              ":?",("quote","__main__..x.y"),
              ":?",("quote","__main__..x.y"),
              ":?",""),
             ("",":",
              ":?",("quote","__main__..int.x"),
              ":?",("quote","__main__..int.float"),
              ":?",""),
             ("",":",":?",("quote","__main__..QzMaybe_.int"), ":?",1, ":?",""),
             ("",":",":?",("quote","builtins..float"), ":?",1, ":?",""),
             ("",":",
              ":?",("quote","__main__..QzMaybe_.x"),
              ":?",("quote","__main__..x"),
              ":?","")],
            [*self.reader.reads(
                "`(x.y x.y) `(int.x int.float) `(int 1) `(float 1) `(x x)"
            )],
        )  # fmt: skip

    def test_swap_ns(self):
        self.reader.env = object()
        self.assertIs(self.reader.env, self.reader.compiler.env)

    def test_badspace(self):
        with self.assertRaises(SyntaxError):
            next(self.reader.reads("\t7"))

    def test_bad_token(self):
        with self.assertRaises(SyntaxError):
            next(self.reader.reads("\\"))

    def test_bad_macro(self):
        with self.assertRaises(SyntaxError):
            next(self.reader.reads("foo#bar"))

    def test_reader_missing(self):
        with self.assertRaises(SyntaxError):
            next(self.reader.reads("(x#)"))

    def test_reader_initial_dot(self):
        msg = r"unknown tag 'QzFULLxSTOP_foo'"
        with self.assertRaisesRegex(SyntaxError, msg):
            next(self.reader.reads(".foo# 0"))

    def test_template(self):
        self.assertEqual(
            [("quote", "('foo')",), 7],
            [*self.reader.reads('`"foo" `,7')]
        )  # fmt: skip

    def test_is_string_code(self):
        self.assertFalse(reader.is_lissp_unicode("(1+1)"))

    def test_gensym_equal(self):
        self.assertEqual(*next(self.reader.reads(".#`($#G $#G)")))

    def test_gensym_progression(self):
        self.assertNotEqual(*self.reader.reads("`,$#G `,$#G"))

    def test_gensym_name(self):
        code = "`,$#G"
        main = next(self.reader.reads(code))
        name_reader = reader.Lissp(__name__, globals())
        name = next(name_reader.reads(code))
        self.assertNotEqual(main, name)
        self.assertRegex(main + name, r"(?:_Qz[a-z0-7]+__G){2}")

    def test_unwrapped_splice(self):
        with self.assertRaisesRegex(SyntaxError, "splice not in tuple"):
            next(self.reader.reads("`,@()"))

    def test_bad_fragment(self):
        with self.assertRaisesRegex(SyntaxError, "unpaired |"):
            next(self.reader.reads("|foo"))

    def test_trivial_template(self):
        self.assertEqual(":foo", next(self.reader.reads("`:foo")))

    def test_tag_under_arity(self):
        msg = "reader tag 'foo##' missing argument"
        with self.assertRaisesRegex(SoftSyntaxError, msg):
            next(self.reader.reads("foo##2\n"))
        with self.assertRaisesRegex(SyntaxError, msg):
            next(self.reader.reads("(foo##2)"))


EXPECTED = {
    # Numeric
    """False True""": [False, True],
    """42 0x10 0o10 0b10 0b1111_0000_0000""": [42, 16, 8, 2, 0xF00],
    """-4.2 4e2 -1.6e-2""": [-4.2, 400, -0.016],
    """5j 4+2j -1_2.3_4e-5_6-7_8.9_8e-7_6j""": [5j, 4 + 2j, -1.234e-55 - 7.898e-75j],
    # Singleton
    """None ...""": [None, ...],
    # Symbolic
    """object math..tau""": ["object", "math..tau"],
    """\
    builtins..object ; qualified identifier
    object.__class__ ; attribute identifier
    builtins..object.__class__ ; qualified attribute identifier
    object.__class__.__name__ ; Attributes chain.
    """
    // dedented: [
        "builtins..object",
        "object.__class__",
        "builtins..object.__class__",
        "object.__class__.__name__",
    ],

    """:control-word""": [":control-word"],
    "'symbol": [("quote", "symbol",)],

    "'Also-a-symbol! '+ '-<>>": [
        ("quote", "AlsoQzH_aQzH_symbolQzBANG_",),
        ("quote", "QzPLUS_",),
        ("quote", "QzH_QzLT_QzGT_QzGT_",),
    ],

    '''"string" ""''': [
        "('string')",
        "('')",
    ],

    '''b""''': ["b", "('')"],
    "b''": ["bQzAPOS_QzAPOS_"],
    "b''''''": ["bQzAPOS_QzAPOS_QzAPOS_QzAPOS_QzAPOS_QzAPOS_"],
    '''b""""""''': ["b", "('')", "('')", "('')"],

    """rb'' br'' RB'' BR'' rb"" br"" B"" """: [
        "rbQzAPOS_QzAPOS_",
        "brQzAPOS_QzAPOS_",
        "RBQzAPOS_QzAPOS_",
        "BRQzAPOS_QzAPOS_",
        "rb",
        "('')",
        "br",
        "('')",
        "B",
        "('')",
    ],

    '''b"not bytes"''': ["b", "('not bytes')"],

    """\
    b"not bytes
    with
    newlines"
    """
    // dedented: [
        "b",
        R"('not bytes\nwith\nnewlines')",
    ],

    # invocation
    """(print "Hello, World!")""": [("print", "('Hello, World!')",)],

    # reader
    """_#foobar""": [],
    """builtins..float#inf""": [math.inf],
    """.#(fractions..Fraction 1 2)""": [Fraction(1, 2)],

    """\
    (lambda (a b c)
      .#"(-b + (b**2 - 4*a*c)**0.5)/(2*a)")
    """: [
        ("lambda", ("a", "b", "c",), "(-b + (b**2 - 4*a*c)**0.5)/(2*a)",)
    ],

    R"""'\~\!\@\#\$\%\^\&\*\(\)\_\+\{\}\|\:\"\<\>\?\`\-\=\[\]\\\;\'\,\.\/""": [
        ("quote",
         "QzTILDE_QzBANG_QzAT_QzHASH_QzDOLR_QzPCENT_QzHAT_QzET_QzSTAR_QzLPAR_QzRPAR__"
         "QzPLUS_QzLCUB_QzRCUB_QzVERT_QzCOLON_QzQUOT_QzLT_QzGT_QzQUERY_QzGRAVE_QzH_QzEQ_"
         "QzLSQB_QzRSQB_QzBSOL_QzSEMI_QzAPOS_QzCOMMA_QzFULLxSTOP_QzSOL_",)
    ],

    R"""\1 \12 \[] \(\) \{} \[] \: \; \# \` \, \' \" \\ \\. \. \ """: [
        "QzDIGITxONE_",
        "QzDIGITxONE_2",
        "QzLSQB_QzRSQB_",
        "QzLPAR_QzRPAR_",
        "QzLCUB_QzRCUB_",
        "QzLSQB_QzRSQB_",
        "QzCOLON_",
        "QzSEMI_",
        "QzHASH_",
        "QzGRAVE_",
        "QzCOMMA_",
        "QzAPOS_",
        "QzQUOT_",
        "QzBSOL_",
        'QzBSOL_.',
        'QzFULLxSTOP_',
        "QzSPACE_",
    ],

    R"""\b\u\i\l\t\i\n\s..\f\l\o\a\t#\i\n\f""": [math.inf],
}  # fmt: skip
