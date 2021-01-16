# Copyright 2020 Matthew Egan Odendahl
# SPDX-License-Identifier: Apache-2.0
"""
Hissp's command-line interface.
"""

import argparse
import sys

import hissp.repl
from hissp.reader import Lissp


def main():
    """
    Entry point for the `lissp command`.
    """
    ns = _arg_parser().parse_args()
    sys.argv = [""]
    if ns.c is not None:
        _cmd(ns)
    elif ns.file is not None:
        _with_args(ns)
    else:
        hissp.repl.main()


def _cmd(ns):
    sys.argv = ["-c"]
    if ns.file is not None:
        sys.argv.extend([ns.file, *ns.args])
    ns.i("(hissp.basic.._macro_.prelude)\n" + ns.c)


def _with_args(ns):
    with argparse.FileType("r")(ns.file) as file:
        sys.argv = [file.name, *ns.args]
        code = file.read()
    ns.i(code)


def _interact(code):
    repl = hissp.repl.REPL()
    repl.lissp.compiler.evaluate = True
    try:
        repl.lissp.compile(code)
    finally:
        repl.lissp.compiler.evaluate = False
        repl.interact()


def _no_interact(code):
    Lissp(evaluate=True).compile(code)


def _arg_parser():
    root = argparse.ArgumentParser(
        description="Starts the REPL if there are no arguments."
    )
    _ = root.add_argument
    _(
        "-i",
        action="store_const",
        const=_interact,
        default=_no_interact,
        help="Drop into REPL after the script.",
    )
    _("-c", help="Run main script (with prelude) from this string.", metavar="cmd")
    _("file", nargs="?", help="Run main script from this file. (- for stdin.)")
    _("args", nargs="*", help="Arguments for the script.")
    return root


if __name__ == "__main__":
    main()
