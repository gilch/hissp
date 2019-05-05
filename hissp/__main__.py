import sys
import traceback

from hissp.compiler import Compiler
from hissp.reader import reads, read


def repl():
    compiler = Compiler(evaluate=False)
    while True:
        try:
            try:
                line = input("\n## ")
            except EOFError:
                raise SystemExit
            buffer = _get_more(line)
            forms = reads("\n".join(buffer))
            code = compiler.compile(forms)
            print(">>> ", code.replace("\n", "\n... "))
            bytecode = compile(code, "<repl>", "single")
            exec(bytecode, compiler.ns)
        except SystemExit:
            print("Exit Hissp.")
            raise
        except BaseException as be:
            traceback.print_exception(type(be), be, be.__traceback__.tb_next)


def _get_more(line):
    buffer = [line]
    if "(" in line:
        buffer.extend(iter(input, ""))
    return buffer


if __name__ == "__main__":
    if len(sys.argv) < 2:
        repl()
    elif len(sys.argv) == 2:
        with open(sys.argv[1].rstrip(".lisp") + ".py", "w") as f:
            f.write(Compiler().compile(read(sys.argv[1])))
