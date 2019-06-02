# Copyright 2019 Matthew Egan Odendahl
# SPDX-License-Identifier: Apache-2.0
import traceback
from functools import partial
from types import SimpleNamespace

import hissp.basic
from hissp.reader import Parser


def repl():
    parser = Parser()
    parser.compiler.ns['_macro_'] = SimpleNamespace(**vars(hissp.basic._macro_))
    while True:
        try:
            try:
                line = input("\n#> ")
            except EOFError:
                raise SystemExit
            buffer = _get_more(line)
            forms = parser.reads("\n".join(buffer))
            evaluate(forms, parser)
        except SystemExit:
            print("Exit Hissp.")
            raise
        except BaseException as be:
            traceback.print_exception(type(be), be, be.__traceback__.tb_next)


def evaluate(forms, parser):
    code = parser.compiler.compile(forms)
    print(">>>", code.replace("\n", "\n... "))
    bytecode = compile(code, "<repl>", "single")
    exec(bytecode, parser.compiler.ns)
    return code


def _get_more(line):
    buffer = [line]
    if "(" in line or '"' in line:
        buffer.extend(iter(partial(input, "#.."), ""))
    return buffer


if __name__ == "__main__":
    repl()
