# Copyright 2020, 2021 Matthew Egan Odendahl
# SPDX-License-Identifier: Apache-2.0
"""
Hissp's command-line interface.
"""

import argparse
import re
import sys
import traceback
from typing import Any

import hissp.repl
from hissp import VERSION
from hissp.reader import Lissp


def main():
    """
    Entry point for the `lissp command`.
    """
    args = _arg_parser().parse_args()
    sys.argv = [""]
    __main__ = hissp.repl.force_main()
    if args.c is not None:
        _cmd(args, __main__.__dict__)
    elif args.file is not None:
        _with_args(args, __main__.__dict__)
    else:
        hissp.repl.main(__main__)


def _cmd(args, env: dict[str, Any]):
    sys.argv = ["-c"]
    sys.argv.extend([args.file, *args.args])
    args.i("(hissp.._macro_.prelude)\n" + args.c, env)


def _with_args(args, env: dict[str, Any]):
    with argparse.FileType("r", encoding="utf8")(args.file) as file:
        sys.argv = [file.name, *args.args]
        code = file.read()
    args.i(re.sub("^#!.*\n", "\n", code), env)


def _interact(code: str, env: dict[str, Any]):
    repl = hissp.repl.LisspREPL(locals=env)
    repl.lissp.compiler.evaluate = True
    try:
        repl.lissp.compile(code)
    except:
        traceback.print_exc()
    finally:
        repl.lissp.compiler.evaluate = False
        repl.interact()


def _no_interact(code: str, env: dict[str, Any]):
    Lissp(env=env, evaluate=True).compile(code)


def _arg_parser():
    root = argparse.ArgumentParser(
        description=f"(Hissp {VERSION}) Starts a LisspREPL if there are no arguments."
    )
    _ = root.add_argument
    _(
        "-i",
        action="store_const",
        const=_interact,
        default=_no_interact,
        help="Drop into REPL after the script.",
    )
    _("-c", help="Run this string as main script (with prelude).", metavar="cmd")
    _("file", nargs="?", help="Run this file as main script. (- for stdin.)")
    _("args", nargs="*", help="Arguments for the script.")
    return root


if __name__ == "__main__":
    main()
