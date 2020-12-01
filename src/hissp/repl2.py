# Copyright 2020 Matthew Egan Odendahl
# SPDX-License-Identifier: Apache-2.0

import sys
from code import InteractiveConsole
from types import SimpleNamespace

import hissp.basic
from hissp.reader import Parser, SoftSyntaxError


class REPL(InteractiveConsole):
    def __init__(self):
        super().__init__()
        self.lissp = Parser(ns=self.locals)

    def runsource(self, source, filename="<input>", symbol="single"):
        try:
            self.lissp.filename = filename
            source = self.lissp.compile(source)
        except SoftSyntaxError:
            return True
        except SyntaxError:
            self.showsyntaxerror()
            return False
        except BaseException:
            import traceback
            traceback.print_exc()
            return False
        print(">>>", source.replace("\n", "\n... "), file=sys.stderr)
        super().runsource(source, filename, symbol)


def main():
    sys.ps1 = "#> "
    sys.ps2 = "#.."
    repl = REPL()
    repl.runsource(
        "(.__setitem__(globals)'_macro_(types..SimpleNamespace : :**(vars hissp.basic.._macro_)))"
    )
    repl.interact()

if __name__ == "__main__":
    main()