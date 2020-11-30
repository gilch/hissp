import subprocess as sp

REPL_CMD = "replissp"
EXIT_MSG = "\nnow exiting REPL...\n"


def cmd(cmd, input=""):
    return sp.Popen(
        cmd, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE, text=True, shell=False
    ).communicate(input=input)


BANNER_LEN = len(cmd(REPL_CMD)[1]) - len(EXIT_MSG)


def repl(input, out: str, err: str, exitmsg=EXIT_MSG):
    actual_out, actual_err = cmd(REPL_CMD, input)
    assert actual_out == out
    assert actual_err[BANNER_LEN:] == err + exitmsg


def test_repl_prompt():
    repl("", "#> ", "")


def test_repl_atom():
    repl(
        "1\n2\n3\n",
        "#> 1\n#> 2\n#> 3\n#> ",
        ">>> (1)\n>>> (2)\n>>> (3)\n",
    )


def test_repl_exit():
    repl(
        "(exit)\n",
        "#> ",
        ">>> exit()\n",
        "",
    )

def test_repl_read_error():
    repl(
        ",\n,@\n`\n$#x\nbuiltins..float#\n\\\n)\n",
        "#> "*8,
r"""Unquote outside of template.
Unquote outside of template.
Reader macro '`' missing argument.
Gensym outside of template.
Reader macro 'builtins..float#' missing argument.
Read error: '\\'
Unopened ')'.
""",
    )


def test_repl_str_continue():
    repl(
        """\
""
"foo bar"
"

"
"

x
"
b""
b"foo bar"
b"


"
b"

x"
""",
        r"""#> ''
#> 'foo bar'
#> #..#..'\n\n'
#> #..#..#..'\n\nx\n'
#> b''
#> b'foo bar'
#> #..#..#..b'\n\n\n'
#> #..#..b'\n\nx'
#> """,
        r""">>> ''
>>> 'foo bar'
>>> '\n\n'
>>> '\n\nx\n'
>>> b''
>>> b'foo bar'
>>> b'\n\n\n'
>>> b'\n\nx'
""",
    )


def test_repl_paren_continue():
    repl(
        """\
()
(
)
(

)
(


)
'(1 2)
'(1
2
)
'(1


2)""",
        """\
#> ()
#> #..()
#> #..#..()
#> #..#..#..()
#> (1, 2)
#> #..#..(1, 2)
#> #..#..#..(1, 2)
#> """,
        ">>> ()\n"*4 + ">>> (1, 2)\n"*3,
    )
