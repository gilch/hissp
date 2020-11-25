# Copyright 2020 Matthew Egan Odendahl
# SPDX-License-Identifier: Apache-2.0

import pygments.token as pt
from pygments.lexer import RegexLexer

SN = r'[+-]?'
Ds = r'(?:\d(?:_?\d)*)'
Es = rf'(?:[Ee]{SN}{Ds})'

# TODO: rename file?
class LisspLexer(RegexLexer):
    name = 'Lissp'
    aliases = ['lissp']
    filenames = ['*.lissp']

    tokens = {
        'root': [
            (r'[()]', pt.Punctuation),
            (r'b?"(?:[^"\\]|\\(?:.|\n))*"', pt.String),
            (r';;;;.*', pt.Generic.Heading),
            (r';;;.*', pt.Generic.Subheading),
            (r';.*', pt.Comment),
            (r'[\n ]+', pt.Whitespace),
            (r'\s|\r', pt.Error),
            (r''',@|['`,]''', pt.Operator),
            (r'''(?:[^ \n"(){}[\]#]*[#])''', pt.Operator.Word),

            # Python numbers
            (r'False|True', pt.Number.Integer),
            (rf'{SN}{Ds}(?:\.{Ds}?{Es}?[Jj]?|{Es}[Jj]?|[Jj])', pt.Number.Float),
            (rf'{SN}\.{Ds}{Es}?[Jj]?', pt.Number.Float),
            (rf'{SN}?0[oO](?:_?[0-7])+', pt.Number.Oct),
            (rf'{SN}0[bB](?:_?[01])+', pt.Number.Bin),
            (rf'{SN}0[xX](?:_?[a-fA-F0-9])+', pt.Number.Hex),
            (rf'{SN}{Ds}', pt.Number.Integer),

            ('None|\.\.\.', pt.Name.Builtin),
            (r':[^ \n"()]*', pt.String.Symbol),  # :control-words

            (r'''[[{][^ \n"()]*''', pt.Literal),
            (r'''[^ \n"()]+''', pt.Name.Variable),
        ]
    }


def setup(app):
    app.add_lexer('Lissp', LisspLexer)
