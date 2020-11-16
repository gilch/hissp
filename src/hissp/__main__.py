# Copyright 2020 Matthew Egan Odendahl
# SPDX-License-Identifier: Apache-2.0

ns = globals().copy()

import sys
from argparse import ArgumentParser, FileType

from hissp.reader import Parser
from hissp.repl import repl

del ns["__package__"], ns["__file__"]


def parse_args(argv):
    p = ArgumentParser()
    p.add_argument('-i', action='store_true', help="drop into interactive mode afterwards")
    source = p.add_mutually_exclusive_group().add_argument
    # TODO: include basic macros for -c?
    # TODO: allow changing basic macros via env variable or .hissprc?
    source("-c", metavar="command", help="string evaluated as lissp program")
    source(
        "file",
        nargs="?",
        help="program read from .lissp file. Use `-` for stdin.",
    )
    p.add_argument("args", nargs="*")
    args = p.parse_args(argv[1:])
    # TODO: stream from file? `-` arg?
    argv.clear()
    argv.extend(_rebuild_argv(args))
    code = _get_code(args)
    return code, args.i or not code


def _rebuild_argv(args):
    if args.c:
        base = '-c'
    elif args.file:
        base = args.file
    else:
        base = ''
    return [base, *args.args]


def _get_code(args):
    if args.c:
        code = args.c
    elif args.file and not (f := FileType("r")(args.file)).isatty():
        ns["__file__"] = args.file.name
        code = f.read()
    else:
        code = None
    return code


def main():
    # TODO: test CLI
    # TODO: document CLI
    if '' != sys.path[0]:
        sys.path.insert(0, '')
    code, interact = parse_args(sys.argv)
    if code:
        # TODO: ignore shebang
        Parser(ns=ns, filename=ns.get("__file__", "<?>"), evaluate=True).compile(code)
    else:
        del ns["__cached__"]
        ns["__spec__"] = None
    if interact:
        repl(ns=ns)


if __name__ == "__main__":
    main()

