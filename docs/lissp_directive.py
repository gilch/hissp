# Copyright 2021, 2022 Matthew Egan Odendahl
# SPDX-License-Identifier: Apache-2.0

import re

from sphinx.directives.code import CodeBlock

STRIP_OUTPUT = re.compile(
    r"""(?x)
    ((?m:^)[ ]* [#]>(?:[ ] .*)?\n
       (?: [ ]* [#]\.\. .*\n)*)
           [ ]* >>>(?:[ ].*)?\n
       (?: [ ]* \.\.\.(:?[ ].*)\n)*
       (?:.+\n)*
       (?:\n|$)
    """
)
STRIP_PROMPTS = re.compile(r"(?m)^ *#(?:> ?|\.\.)")


class LisspDirective(CodeBlock):
    def run(self):
        code = "\n".join(self.content) + "\n"
        code = STRIP_OUTPUT.sub(lambda m: STRIP_PROMPTS.sub("", m[1]), code)
        self.content = code.split("\n")
        self.arguments.insert(0, "Lissp")
        return super().run()


def setup(app):
    app.add_directive("lissp", LisspDirective)

    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
