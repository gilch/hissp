# Copyright 2020, 2021, 2022 Matthew Egan Odendahl
# SPDX-License-Identifier: Apache-2.0
"""
The Lissp Read-Evaluate-Print Loop. For interactive use.
"""

import sys
from code import InteractiveConsole
from contextlib import suppress
from types import ModuleType, SimpleNamespace

from hissp.compiler import CompileError
from hissp.reader import Lissp, SoftSyntaxError


ps1 = "#> "
"""String specifying the primary prompt of the `LisspREPL`."""


ps2 = "#.."
"""String specifying the secondary (continuation) prompt of the `LisspREPL`."""


class LisspREPL(InteractiveConsole):
    """Lissp's Read-Evaluate-Print Loop, layered on Python's.

    You can initialize the REPL with a locals dict,
    which is useful for debugging other modules.
    Call interact() to start.
    """

    # locals shadows the builtin, but that's the name in the superclass.
    def __init__(self, locals=None, filename="<console>"):
        super().__init__(locals, filename)
        self.lissp = Lissp(locals.get("__name__", "__main__"), locals)
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
        fn = f"<Compiled Hissp of {filename}:\n{self.lissp.compiler.linenos(source)}\n>"
        return super().runsource(source, fn, symbol)

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


def interact(locals=None):
    """Convenience function to start a `LisspREPL`.

    Uses the calling frame's globals and locals as ``locals`` if not
    provided.

    Unlike `hissp.repl.main`, no ``_macros_`` are added to the locals to
    avoid clobbering an existing namespace.
    """
    if locals is None:
        import inspect

        frame = inspect.currentframe().f_back
        locals = {**frame.f_globals, **frame.f_locals}
    LisspREPL(locals=locals).interact()


def force_main():
    """:meta private:"""
    # Creates a new ``__main__`` to take the place of the current
    # ``__main__`` module.
    __main__ = ModuleType("__main__")
    sys.modules["__main__"] = __main__
    sys.path.insert(0, "")
    return __main__


def main(__main__):
    """REPL command-line entry point.

    `hissp.macros._macro_` is copied into the module namespace,
    making the bundled macros immediately available unqualified.
    """
    repl = LisspREPL(locals=__main__.__dict__)
    import hissp.macros  # Here so repl can import before compilation.

    repl.locals["_macro_"] = SimpleNamespace(**vars(hissp.macros._macro_))
    repl.interact()
