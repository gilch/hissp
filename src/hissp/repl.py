# Copyright 2020, 2021 Matthew Egan Odendahl
# SPDX-License-Identifier: Apache-2.0
"""
The Lissp Read-Evaluate-Print Loop. For interactive use.
"""

import sys
import traceback
from code import InteractiveConsole
from types import ModuleType, SimpleNamespace

import hissp.basic
from hissp.compiler import CompileError
from hissp.reader import Lissp, SoftSyntaxError


class LisspREPL(InteractiveConsole):
    """Lissp's Read-Evaluate-Print Loop, layered on Python's.

    You can initialize the REPL with a locals dict,
    which is useful for debugging other modules.
    Call interact() to start.
    """

    def __init__(self, locals=None, filename="<console>"):
        super().__init__(locals, filename)
        sys.ps1 = "#> "
        sys.ps2 = "#.."
        self.lissp = Lissp(ns=locals)
        self.locals = self.lissp.ns

    def runsource(self, source, filename="<input>", symbol="single"):
        """:meta private:"""
        try:
            self.lissp.filename = filename
            source = self.lissp.compile(source)
        except SoftSyntaxError:
            return True
        except CompileError as e:
            print('>>> # CompileError', file=sys.stderr)
            print(e, file=sys.stderr)
            return False
        except SyntaxError:
            self.showsyntaxerror()
            return False
        except BaseException:
            print('>>> # Compilation failed!', file=sys.stderr)
            self.showtraceback()
            return False
        print(">>>", source.replace("\n", "\n... "), file=sys.stderr)
        super().runsource(source, filename, symbol)

    def interact(self, banner=None, exitmsg=None):
        """Imports readline if available, then super().interact()."""
        try:
            import readline
        except ImportError:
            pass
        super().interact(banner, exitmsg)


def force_main():
    """:meta private:"""
    __main__ = ModuleType("__main__")
    sys.modules["__main__"] = __main__
    sys.path.insert(0, "")
    return __main__


def main(__main__=None):
    """REPL command-line entry point."""
    if not __main__:
        __main__ = force_main()
    repl = LisspREPL(locals=__main__.__dict__)
    repl.locals["_macro_"] = SimpleNamespace(**vars(hissp.basic._macro_))
    repl.interact()


if __name__ == "__main__":
    main()
