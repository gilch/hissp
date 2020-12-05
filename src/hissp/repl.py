# Copyright 2020 Matthew Egan Odendahl
# SPDX-License-Identifier: Apache-2.0
import sys
from code import InteractiveConsole
from types import SimpleNamespace

import hissp.basic
from hissp.reader import Lissp, SoftSyntaxError


class REPL(InteractiveConsole):
    def __init__(self, locals=None, filename="<console>"):
        super().__init__(locals, filename)
        sys.ps1 = "#> "
        sys.ps2 = "#.."
        self.lissp = Lissp(ns=locals)
        self.locals = self.lissp.ns

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
    repl = REPL()
    repl.locals['_macro_'] = SimpleNamespace(**vars(hissp.basic._macro_))
    repl.interact()

if __name__ == "__main__":
    main()