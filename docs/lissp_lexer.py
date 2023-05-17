# Copyright 2020, 2021, 2022 Matthew Egan Odendahl
# SPDX-License-Identifier: Apache-2.0
import re

import pygments.token as pt
from pygments.lexer import RegexLexer, bygroups, using, DelegatingLexer
from pygments.lexers.python import Python3Lexer, PythonConsoleLexer

from hissp.reader import Lissp, TOKENS


class LisspLexer(RegexLexer):
    name = "Lissp"
    aliases = ["lissp"]
    filenames = ["*.lissp"]

    class CommentSubLexer(RegexLexer):
        tokens = {
            "root": [
                (r";;;;.*\n( *;.*\n)*", pt.Generic.Heading),
                (r"(?:;;;.*\n)+", pt.Generic.Subheading),
                (r"(?: *;.*\n)+", pt.Comment),
            ]
        }

    class AtomSubLexer(RegexLexer):
        def preprocess_atom(lexer, match, ctx=None):
            value: str = match.group(0)
            index: int = match.start()
            v = Lissp.atom(value)
            if isinstance(v, (complex, float)):
                yield index, pt.Number.Float, value
                return
            if not isinstance(v, str):
                v = value.replace("\\", "")
            elif re.fullmatch(r".+\.$", v):  # module
                yield index, pt.Name.Other, value
                return
            elif m := re.fullmatch(r"((?:[^.]*[^.\\]\.)+)(\..+)", value):
                yield index, pt.Name.Other, m[1]
                index += len(m[1])
                yield index, pt.Name, m[2]
                return
            # Ask Python's lexer. Last one is probably it.
            m = re.match(r".+", v)
            [*_, [_, token_type, _]] = using(Python3Lexer)(lexer, m)
            yield index, token_type, value

        tokens = {
            "root": [
                (r"\.\.\.", pt.Keyword.Constant),  # Ellipsis
                (r"quote", pt.Keyword),
                (r"_macro_", pt.Name.Variable.Magic),
                (r"(?::|\\:).*", pt.String.Symbol),  # :control-words
                (r".+", preprocess_atom),
            ]
        }

    tokens = {
        "root": [
            (
                TOKENS.pattern,
                bygroups(
                    pt.Text,  # whitespace
                    using(CommentSubLexer),
                    pt.Error,  # badspace
                    pt.Punctuation,  # open
                    pt.Punctuation,  # close
                    pt.Operator,  # macro
                    pt.String,
                    pt.Error,  # continue
                    using(AtomSubLexer),
                    pt.Error,
                ),
            )
        ]
    }


class LisspReplLexer(RegexLexer):
    class LisspPromptLexer(DelegatingLexer):
        class PromptLexer(RegexLexer):
            tokens = {
                "root": [
                    (r"^#> |^#\.\.", pt.Generic.Prompt),
                    (r".*\n", pt.Other),
                ]
            }

        def __init__(self, **options):
            super().__init__(LisspLexer, self.PromptLexer, **options)

    tokens = {
        "root": [
            (r"^#> .*\n(?:^#\.\..*\n)*", using(LisspPromptLexer)),
            (r"^>>> .*\n(?:\.\.\. .*\n)*(.+\n)*", using(PythonConsoleLexer)),
            (r".+\n", pt.Generic.Error),
            (r"\n", pt.Whitespace),
        ]
    }


def setup(app):
    app.add_lexer("Lissp", LisspLexer)
    app.add_lexer("REPL", LisspReplLexer)
