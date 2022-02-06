# Copyright 2020, 2021, 2022 Matthew Egan Odendahl
# SPDX-License-Identifier: Apache-2.0
"""
The Lissp Read-Evaluate-Print Loop. For interactive use.
"""

import sys
from code import InteractiveConsole
from contextlib import suppress
from types import ModuleType, SimpleNamespace

import hissp.basic
from hissp.compiler import CompileError
from hissp.reader import Lissp, SoftSyntaxError


ps1 = "#> "
"""String specifying the primary prompt of the REPL."""


ps2 = "#.."
"""String specifying the secondary (continuation) prompt of the REPL."""


class LisspREPL(InteractiveConsole):
    """Lissp's Read-Evaluate-Print Loop, layered on Python's.

    You can initialize the REPL with a locals dict,
    which is useful for debugging other modules.
    Call interact() to start.
    """

    def __init__(self, locals=None, filename="<console>"):
        super().__init__(locals, filename)
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
            print(f"{sys.ps1}# CompileError", file=sys.stderr)
            print(e, file=sys.stderr)
            return False
        except SyntaxError:
            self.showsyntaxerror()
            return False
        except BaseException:
            print(f"{sys.ps1}# Compilation failed!", file=sys.stderr)
            self.showtraceback()
            return False
        print(sys.ps1, source.replace("\n", f"\n{sys.ps2}"), sep="", file=sys.stderr)
        return super().runsource(source, filename, symbol)

    def raw_input(self, prompt=""):
        """:meta private:"""
        prompt = {sys.ps2: ps2, sys.ps1: ps1}.get(prompt, prompt)
        return super().raw_input(prompt)

    def interact(self, banner=None, exitmsg=None):
        """Imports readline if available, then super().interact()."""
        with suppress(ImportError):
            # noinspection PyUnresolvedReferences
            import readline
        return super().interact(banner, exitmsg)


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
