# Copyright 2020, 2021 Matthew Egan Odendahl
# SPDX-License-Identifier: Apache-2.0

import pygments.token as pt
from pygments.lexer import RegexLexer, bygroups, using
from pygments.lexers.python import PythonConsoleLexer

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
            (r';;;;.*', pt.Generic.Heading),
            (r';;;.*', pt.Generic.Subheading),
            (r';.*', pt.Comment),
            (r'[\n ]+', pt.Text),
            (r'\s|\r', pt.Error),
            (r'([(])(lambda|quote)', bygroups(pt.Punctuation, pt.Keyword)),
            (r'[()]', pt.Punctuation),
            (r''',@|['`,]|$#|.#|_#''', pt.Operator),
            (r'#?"(?:[^"\\]|\\(?:.|\n))*"', pt.String),
            (r'''(?:[^\\ \n"();#]|\\.)+[#]''', pt.Operator.Word),

            # Python numbers
            (r'False|True', pt.Name.Builtin),
            (rf'{SN}{Ds}(?:\.{Ds}?{Es}?[Jj]?|{Es}[Jj]?|[Jj])', pt.Number.Float),
            (rf'{SN}\.{Ds}{Es}?[Jj]?', pt.Number.Float),
            (rf'{SN}?0[oO](?:_?[0-7])+', pt.Number.Oct),
            (rf'{SN}0[bB](?:_?[01])+', pt.Number.Bin),
            (rf'{SN}0[xX](?:_?[a-fA-F0-9])+', pt.Number.Hex),
            (rf'{SN}{Ds}', pt.Number.Integer),

            ('None|\.\.\.', pt.Name.Builtin),
            (r':[^ \n"()]*', pt.String.Symbol),  # :control-words

            (r'''[[{](:?[^\\ \n"();]|\\.)*''', pt.Literal),
            (r'''(:?[^\\ \n"();]|\\.)+''', pt.Name),
        ]
    }

class LisspReplLexer(RegexLexer):
    tokens = {
        'root': [
            (r'^#> .*\n(?:^#\.\..*\n)*', using(LisspLexer)),
            (r'^>>> .*\n(?:\.\.\. .*\n)*', using(PythonConsoleLexer)),
            (r'.*\n', pt.Text),
        ]
    }


def setup(app):
    app.add_lexer('Lissp', LisspLexer)
    app.add_lexer('REPL', LisspReplLexer)
