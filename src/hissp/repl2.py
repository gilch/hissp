import sys
from code import InteractiveConsole

from hissp.reader import Parser


class REPL(InteractiveConsole):
    def __init__(self):
        super().__init__()
        self.lissp = Parser(ns=self.locals)

    def runsource(self, source, filename="<input>", symbol="single"):
        try:
            forms = self.lissp.reads(source)
            try:
                source = self.lissp.compiler.compile(forms)
            except SyntaxError as e:
                # print(e, file=sys.stderr)
                return True
        except BaseException as e:
            print(e, file=sys.stderr)
            return False
        print(">>>", source.replace("\n", "\n... "), file=sys.stderr)
        super().runsource(source, filename, symbol)


def main():
    sys.ps1 = "#> "
    sys.ps2 = "#.."
    repl = REPL()
    repl.runsource("(hissp.basic.._macro_.prelude)")
    repl.interact()

if __name__ == "__main__":
    main()