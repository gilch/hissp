# Copyright 2020 Matthew Egan Odendahl
# SPDX-License-Identifier: Apache-2.0

import argparse
import sys

import hissp.repl
from hissp.reader import Lissp


def main():
    ns = parse_args()
    code, arg0 = file_group(ns)
    if code is not None:
        sys.argv = [arg0, *ns.args]
        if ns.i:
            repl = hissp.repl.REPL()
            try:
                repl.lissp.compile(code)
            finally:
                repl.interact()
        else:
            exec(Lissp().compile(code))
    elif ns.compile:
        hissp.reader.transpile(ns.package, *ns.files)
    else:
        hissp.repl.main()


def parse_args():
    root = argparse.ArgumentParser()
    _ = root.add_subparsers().add_parser("compile").add_argument
    _("-p", "--package", default="", help="used to qualify compiled symbols")
    _("files", nargs="+", help=".lissp files to compile to .py")

    root.add_argument(
        "-i",
        action='store_true',
        help="inspect interactively after running script (even if it crashes)"
    )

    _ = root.add_mutually_exclusive_group().add_argument
    _("-c", help="Program passed in as a string.", metavar='cmd')
    _("file", nargs="?", type=argparse.FileType('r'), help="Script file. (- is stdin.)")

    root.add_argument("args", nargs="*")

    return root.parse_args()


def file_group(ns):
    if ns.file:
        return ns.file.read(), ns.file.name
    elif 'c' in ns:
        return ns.c, '-c'
    return None, None


if __name__ == "__main__":
    main()