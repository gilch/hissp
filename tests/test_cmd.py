# Copyright 2020 Matthew Egan Odendahl
# SPDX-License-Identifier: Apache-2.0

import subprocess as sp


def cmd(cmd, input=""):
    return sp.Popen(
        cmd, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE, text=True, shell=False
    ).communicate(input=input)


EXIT_MSG = "\nnow exiting REPL...\n"
BANNER_LEN = len(cmd("lissp")[1]) - len(EXIT_MSG)


def test_c_args():
    out, err = cmd(["lissp", "-c", "(print sys..argv)", "1", "2", "3"])
    assert out == "['-c', '1', '2', '3']\n"
    assert err == ""


def test_ic_args():
    out, err = cmd(
        ["lissp", "-i", "-c", "(print sys..argv)(define answer 42)", "1", "2", "3"],
        "answer\n"
    )
    assert out == "['-c', '1', '2', '3']\n#> 42\n#> "
    assert err[BANNER_LEN:] == ">>> answer\n" + EXIT_MSG


def test_file_args():
    out, err = cmd(["lissp", "tests/argv.lissp", "1", "2", "3"])
    assert out == """\
['tests/argv.lissp', '1', '2', '3']
__name__='__main__' __package__=None
"""
    assert err == ""


def test_i_file_args():
    out, err = cmd(["lissp", "-i", "tests/argv.lissp", "1", "2", "3"], "answer\n")
    assert out == """\
['tests/argv.lissp', '1', '2', '3']
__name__='__main__' __package__=None
#> 42
#> """
    assert err[BANNER_LEN:] == ">>> answer\n" + EXIT_MSG


def repl(input, out: str = '#> '*2, err: str = "", exitmsg=EXIT_MSG):
    actual_out, actual_err = cmd("lissp", input)
    assert actual_out == out
    assert actual_err[BANNER_LEN:] == err + exitmsg


def test_repl_prompt():
    repl("", "#> ")


def test_repl_atom():
    repl(
        "1\n2\n3\n",
        "#> 1\n#> 2\n#> 3\n#> ",
        ">>> (1)\n>>> (2)\n>>> (3)\n",
    )


def test_repl_exit():
    repl("(exit)\n", "#> ", ">>> exit()\n", "")


def test_repl_unqoute_error():
    err = """\
  File "<console>", line 1
    ,
    ^
SyntaxError: Unquote outside of template.
"""
    repl(",\n", err=err)


def test_repl_splice_error():
    err = """\
  File "<console>", line 1
    ,@
     ^
SyntaxError: Unquote outside of template.
"""
    repl(",@\n", err=err)


def test_repl_empty_template_error():
    err = """\
  File "<console>", line 1
    `
    ^
SyntaxError: Reader macro '`' missing argument.
"""
    repl("`\n", err=err)


def test_repl_gensym_error():
    err = """\
  File "<console>", line 1
    $#x
      ^
SyntaxError: Gensym outside of template.
"""
    repl("$#x\n", err=err)


def test_repl_empty_reader_macro_error():
    err = """\
  File "<console>", line 1
    builtins..float#
                   ^
SyntaxError: Reader macro 'builtins..float#' missing argument.
"""
    repl("builtins..float#\n", err=err)


def test_repl_read_error():
    err = """\
  File "<console>", line 1
    \\
    ^
SyntaxError: Can't read this.
"""
    repl("\\\n", err=err)


def test_repl_unopened_error():
    err = """\
  File "<console>", line 1
    )
    ^
SyntaxError: Unopened ')'.
"""
    repl(")\n", err=err)


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
        r""">>> ('')
>>> ('foo bar')
>>> ('\n\n')
>>> ('\n\nx\n')
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
