# Copyright 2019, 2020 Matthew Egan Odendahl
# SPDX-License-Identifier: Apache-2.0

import math
from collections import Counter
from fractions import Fraction
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import ANY, patch

import hypothesis.strategies as st
from hypothesis import given

from hissp import reader

STRING_ANY_ = [("string", ANY, ANY)]


class TestReader(TestCase):
    def setUp(self) -> None:
        self.parser = reader.Lissp()

    @given(st.text("(\n 1)", max_size=20))
    def test_balance(self, lissp):
        tally = Counter(lissp)
        if tally["("] != tally[")"]:
            self.assertRaisesRegex(
                (SyntaxError, ValueError), r"^Un(?:opened|closed)|Ran out of tokens", list, self.parser.reads(lissp)
            )

    @given(st.text(max_size=5))
    def test_string(self, lissp):
        lissp = lissp.replace("\\", "\\\\").replace('"', r"\"")
        lissp = f'"{lissp}"'
        self.assertEqual([*reader.Lexer(lissp)], STRING_ANY_)

    def test_examples(self):
        for k, v in EXPECTED.items():
            with self.subTest(code=k, parsed=v):
                print(k)
                lex_k = [*reader.Lexer(k)]
                print(lex_k)
                parsed = [*self.parser.parse(reader.Lexer(k))]
                print(parsed)
                self.assertEqual(v, parsed)
                print('OK')

    @patch("hissp.reader.ENTUPLE", "entuple")
    def test_auto_qualification(self):
        self.assertEqual(
            [('entuple',
              ':', ':?', ('quote', '__main__..xAUTO_.x'),
              ':?', ('quote', '__main__..x'),
              ':?', ('quote', '__main__..x'),
              ':?', ('entuple',
                     ':', ':?', ('quote', '__main__..xAUTO_.y'),
                     ':?', ('quote', '__main__..y')),
              ':?', ('entuple', ':', ':?', 1, ':?', ('quote', '__main__..z')))
             ],
            [*self.parser.reads('`(x x x (y y) (1 z))')],
        )

    @patch("hissp.reader.ENTUPLE", "entuple")
    def test_module_qualification(self):
        self.parser.ns.update(x=1, y=2, z=3)
        self.assertEqual(
            [('entuple',
              ':', ':?', ('quote', '__main__..xAUTO_.x'),
              ':?', ('quote', '__main__..x'),
              ':?', ('quote', '__main__..x'),
              ':?', ('entuple',
                     ':', ':?', ('quote', '__main__..xAUTO_.y'),
                     ':?', ('quote', '__main__..y')),
              ':?', ('entuple', ':', ':?', 1, ':?', ('quote', '__main__..z')))
             ],
            [*self.parser.reads('`(x x x (y y) (1 z))')],
        )

    @patch("hissp.reader.ENTUPLE", "entuple")
    def test_macro_qualification(self):
        self.parser.ns.update(_macro_=SimpleNamespace(x=1, y=2, z=3))
        self.assertEqual(
            [('entuple',
              ':', ':?', ('quote', '__main__.._macro_.x'),
              ':?', ('quote', '__main__..x'),
              ':?', ('quote', '__main__..x'),
              ':?', ('entuple',
                     ':', ':?', ('quote', '__main__.._macro_.y'),
                     ':?', ('quote', '__main__..y')),
              ':?', ('entuple', ':', ':?', 1, ':?', ('quote', '__main__..z')))
             ],
            [*self.parser.reads('`(x x x (y y) (1 z))')],
        )

    @patch("hissp.reader.ENTUPLE", "entuple")
    def test_no_qualification(self):
        self.assertEqual(
            [('entuple', ':', ':?', ('quote', '.x')),
             ('entuple', ':', ':?', ('quote', 'quote'), ':?', 1),
             ('entuple', ':', ':?', ('quote', 'lambda'), ':?', ':'),
             ('quote', '__import__'),
             ('quote', 'xAUTO0_'),
             ('quote', 'foo..bar'),
             ('quote', 'foo.')],
            [*self.parser.reads(
                '`(.x) `(quote 1) `(lambda :) `__import__ `xAUTO0_ `foo..bar `foo.'
            )],
        )

    @patch("hissp.reader.ENTUPLE", "entuple")
    def test_auto_qualify_attr(self):
        self.parser.ns.update(x=SimpleNamespace(y=1), int=SimpleNamespace(float=1))
        self.assertEqual(
            [('entuple',
              ':',
              ':?',
              ('quote', '__main__..x.y'),
              ':?',
              ('quote', '__main__..x.y')),
             ('entuple',
              ':',
              ':?',
              ('quote', '__main__..int.x'),
              ':?',
              ('quote', '__main__..int.float')),
             ('entuple', ':', ':?', ('quote', '__main__..xAUTO_.int'), ':?', 1),
             ('entuple', ':', ':?', ('quote', 'builtins..float'), ':?', 1),
             ('entuple',
              ':',
              ':?',
              ('quote', '__main__..xAUTO_.x'),
              ':?',
              ('quote', '__main__..x'))],
            [*self.parser.reads(
                '`(x.y x.y) `(int.x int.float) `(int 1) `(float 1) `(x x)'
            )],
        )

EXPECTED = {
# Numeric
'''False True''': [False, True],
'''42 0x10 0o10 0b10 0b1111_0000_0000''': [42, 16, 8, 2, 0xF00],
'''-4.2 4e2 -1.6e-2''': [-4.2,400,-0.016],
'''5j 4+2j -1_2.3_4e-5_6-7_8.9_8e-7_6j''': [5j,4+2j,-1.234e-55-7.898e-75j],
# Singleton
'''None ...''': [None, ...],
# Symbolic
'''object math..tau''': ['object', 'math..tau'],
'''\
builtins..object ; qualified identifier
object.__class__ ; attribute identifier
builtins..object.__class__ ; qualified attribute identifier
object.__class__.__name__ ; Attributes chain.
''': [
    'builtins..object',
    'object.__class__',
    'builtins..object.__class__',
    'object.__class__.__name__',
],
''':control-word''': [':control-word'],
"'symbol": [('quote', 'symbol')],
"'Also-a-symbol! '+ '->>": [
    ('quote', 'AlsoxH_axH_symbolxBANG_'),
    ('quote', 'xPLUS_'),
    ('quote', 'xH_xGT_xGT_'),
],
'''"string" ""''': [
    "('string')",
    "('')",
],
'''b""''': ['b', "('')"],
"b''": ['bx1QUOTE_x1QUOTE_'],
"b''''''": ['bx1QUOTE_x1QUOTE_x1QUOTE_x1QUOTE_x1QUOTE_x1QUOTE_'],
'''b""""""''': [
    'b', "('')", "('')", "('')"
],
'''rb'' br'' RB'' BR'' rb"" br"" B"" ''': [
    'rbx1QUOTE_x1QUOTE_',
    'brx1QUOTE_x1QUOTE_',
    'RBx1QUOTE_x1QUOTE_',
    'BRx1QUOTE_x1QUOTE_',
    'rb',
    "('')",
    'br',
    "('')",
    'B',
    "('')"
],
'''b"not bytes"''': ['b', "('not bytes')"],
'''\
b"not bytes
with
newlines"
''': ['b', r"('not bytes\nwith\nnewlines')"],
# invocation
'''(print "Hello, World!")''': [
    ('print', "('Hello, World!')")
],
# reader
'''_#foobar''': [],
'''builtins..float#inf''': [math.inf],
'''.#(fractions..Fraction 1 2)''': [Fraction(1, 2)],
'''\
(lambda (a b c)
  .#"(-b + (b**2 - 4*a*c)**0.5)/(2*a)")
''': [('lambda', ('a', 'b', 'c'), '(-b + (b**2 - 4*a*c)**0.5)/(2*a)')],
r''''\~\!\@\#\$\%\^\&\*\(\)\_\+\{\}\|\:\"\<\>\?\`\-\=\[\]\\\;\'\,\.\/''':
    [('quote',
      'xTILDE_xBANG_xAT_xHASH_xDOLR_xPCENT_xCARET_xET_xSTAR_xPAREN_xTHESES__xPLUS'
      '_xCURLY_xBRACES_xBAR_xCOLON_x2QUOTE_xLT_xGT_xQUERY_xGRAVE_xH_xEQ_xSQUARE'
      '_xBRACKETS_xBSLASH_xSCOLON_x1QUOTE_xCOMMA_xFULLxSTOP_xSLASH_')],
r'''\1 \12 \[] \(\) \{} \[] \; \# \` \, \' \" \\ \ ''':
    ['xDIGITxONE_',
     'xDIGITxONE_2',
     'xSQUARE_xBRACKETS_',
     'xPAREN_xTHESES_',
     'xCURLY_xBRACES_',
     'xSQUARE_xBRACKETS_',
     'xSCOLON_',
     'xHASH_',
     'xGRAVE_',
     'xCOMMA_',
     'x1QUOTE_',
     'x2QUOTE_',
     'xBSLASH_',
     'xSPACE_'],
r'''\b\u\i\l\t\i\n\s..\f\l\o\a\t#\i\n\f''': [math.inf],
}


