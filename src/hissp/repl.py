# Copyright 2019 Matthew Egan Odendahl
# SPDX-License-Identifier: Apache-2.0
import traceback
from contextlib import suppress
from functools import partial
from types import SimpleNamespace

from hissp.reader import Parser
from hissp.reader import transpile


def repl(macros=None):
    parser = Parser()
    if not macros:
        with suppress():
            transpile("hissp", "basic")
        from hissp import basic

        macros = basic
    parser.compiler.ns["_macro_"] = SimpleNamespace(**vars(macros._macro_))
    while True:
        try:
            try:
                line = input("\n#> ")
            except EOFError:
                print("Ssss.")
                break
            buffer = _get_more(line)
            forms = parser.reads("\n".join(buffer))
            evaluate(forms, parser)
        except SystemExit:
            print("Lissp REPL Exit.")
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
    if "(" in line or '"' in line or ";" in line:
        buffer.extend(iter(partial(input, "#.."), ""))
    return buffer
