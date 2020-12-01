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
            repl.lissp.compile(code)
            repl.interact()
        else:
            exec(Lissp().compile(code))
    elif ns.compile:
        hissp.reader.transpile(ns.package, *ns.files)
    else:
        hissp.repl.main()


def parse_args():
    parser = argparse.ArgumentParser()

    c = parser.add_subparsers().add_parser("compile").add_argument
    c("-p", "--package", default="")
    c("files", nargs="+")

    s = parser.add_mutually_exclusive_group().add_argument
    s("-c", help="Program passed in as a string.", metavar='cmd')
    s("file", nargs="?", type=argparse.FileType('r'))

    parser.add_argument("-i", action='store_true')
    parser.add_argument("args", nargs="*")

    return parser.parse_args()


def file_group(ns):
    if ns.file:
        return ns.file.read(), ns.file.name
    elif 'c' in ns:
        return ns.c, '-c'
    return None, None


if __name__ == "__main__":
    main()