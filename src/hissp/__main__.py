# Copyright 2020 Matthew Egan Odendahl
# SPDX-License-Identifier: Apache-2.0

import argparse
import sys

import hissp.repl
from hissp.reader import Lissp


def main():
    ns = parse_args()
    _compile(ns) or _run_as_main(ns) or hissp.repl.main()


def _compile(ns):
    if ns.compile:
        hissp.reader.transpile(ns.package, *ns.files)
        return True


def _run_as_main(ns):
    sys.argv = ['']
    if ns.file:
        code = ns.file.read()
        sys.argv = [ns.file.name, *ns.args]
    elif 'c' in ns:
        code = ns.c
        sys.argv = ['-c', *ns.args]
    else:
        return False
    ns.i(code)


def interact(code):
    repl = hissp.repl.REPL()
    try:
        repl.lissp.compile(code)
    finally:
        repl.interact()


def no_interact(code):
    Lissp(evaluate=True).compile(code)


def parse_args():
    root = argparse.ArgumentParser()
    _ = root.add_subparsers(dest='compile').add_parser("compile").add_argument
    _("-p", "--package", default="", help="used to qualify compiled symbols")
    _("files", nargs="+", help=".lissp files to compile to .py")

    root.add_argument(
        "-i",
        action='store_const',
        const=interact,
        default=no_interact,
        help="inspect interactively after running script (even if it crashes)"
    )

    _ = root.add_mutually_exclusive_group().add_argument
    _("-c", help="Program passed in as a string.", metavar='cmd')
    _("file", nargs="?", type=argparse.FileType('r'), help="Script file. (- is stdin.)")

    root.add_argument("args", nargs="*")

    return root.parse_args()


if __name__ == "__main__":
    main()