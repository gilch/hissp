import subprocess as sp
from functools import partial

REPL_CMD = "replissp"


def cmd(cmd, input=""):
    return sp.Popen(
        cmd, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE, text=True, shell=False
    ).communicate(input=input)


repl = partial(cmd, REPL_CMD)


def test_repl_prompt():
    out, err = repl()
    assert out == "#> "
    assert "now exiting REPL..." in err


def test_repl_atom():
    out, err = repl("1\n2\n3\n")
    assert out == """\
#> 1
#> 2
#> 3
#> """
    assert """
>>> (1)
>>> (2)
>>> (3)

now exiting REPL...
""" in err


def test_repl_exit():
    out, err = repl('(exit)\n')
    assert out == "#> "
    assert """
>>> exit()
""" in err

#TODO: test repl continuation, abort.