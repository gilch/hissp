# Copyright 2020, 2021 Matthew Egan Odendahl
# SPDX-License-Identifier: Apache-2.0
import ast
import re
from contextlib import suppress

import pygments.token as pt
from pygments.lexer import RegexLexer, bygroups, using
from pygments.lexers.python import Python3Lexer, PythonConsoleLexer


# TODO: rename file?
class LisspLexer(RegexLexer):
    name = 'Lissp'
    aliases = ['lissp']
    filenames = ['*.lissp']

    def python_atom_callback(lexer, match):
        value: str = match[0]
        index = match.start()
        token_type = pt.Name
        v = value.replace('\\', '')
        with suppress(ValueError, SyntaxError):
            lit = ast.literal_eval(v)
            if isinstance(lit, bytes):
                raise ValueError
            if isinstance(lit, complex):
                token_type = pt.Number.Float
            else:  # Ask Python's lexer. Last one is probably it.
                m = re.match('.*', v)
                [*_, [_, token_type, _]] = using(Python3Lexer)(lexer, m)
        if value.startswith('\\') and not token_type.split()[1] == pt.Name:
            token_type = pt.Name
        yield index, token_type, value

    tokens = {
        'root': [
            (r';;;;.*', pt.Generic.Heading),
            (r';;;.*', pt.Generic.Subheading),
            (r';.*', pt.Comment),
            (r'[\n ]+', pt.Text),
            (r'\s|\r', pt.Error),
            (r'([(])(lambda|quote)', bygroups(pt.Punctuation, pt.Keyword)),
            (r'[()]', pt.Punctuation),
            (r''',@|['`,!]|$#|.#|_#''', pt.Operator),
            (r'#?"(?:[^"\\]|\\(?:.|\n))*"', pt.String),
            (r'''(?:[^\\ \n"();#]|\\.)+[#]''', pt.Operator.Word),
            (r'"', pt.Error),
            (r'\.\.\.', pt.Keyword.Constant),
            (r':(?:[^\\ \n"();]|\\.)*', pt.String.Symbol),  # :control-words
            (r'(?:[^\\ \n"();]|\\.)+', python_atom_callback),
            (r'.', pt.Error),
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
