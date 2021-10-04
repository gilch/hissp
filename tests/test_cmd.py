# Copyright 2020, 2021 Matthew Egan Odendahl
# SPDX-License-Identifier: Apache-2.0

import subprocess as sp


def cmd(cmd, input=""):
    return sp.Popen(
        cmd, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE, text=True, shell=True
    ).communicate(input=input)


EXIT_MSG = "\nnow exiting LisspREPL...\n"
BANNER_LEN = len(cmd("lissp")[1]) - len(EXIT_MSG)


def test_c_args():
    out, err = cmd('python -m hissp -c "(print sys..argv)" 1 2 3')
    assert out == "['-c', '1', '2', '3']\n"
    assert err == ""


def test_ic_args():
    out, err = cmd(
        'lissp -i -c "(print sys..argv)(define answer 42)" 1 2 3',
        "answer\n"
    )
    assert out == "['-c', '1', '2', '3']\n#> 42\n#> "
    assert err[BANNER_LEN:] == ">>> answer\n" + EXIT_MSG


def test_file_args():
    out, err = cmd("lissp tests/argv.lissp 1 2 3")
    assert out == """\
['tests/argv.lissp', '1', '2', '3']
__name__='__main__' __package__=None
"""
    assert err == ""


def test_i_file_args():
    out, err = cmd("lissp -i tests/argv.lissp 1 2 3", "answer\n")
    assert out == """\
['tests/argv.lissp', '1', '2', '3']
__name__='__main__' __package__=None
#> 42
#> """
    assert err[BANNER_LEN:] == ">>> answer\n" + EXIT_MSG


def test_repl_read_exception():
    out, err = cmd("python -m hissp.repl", ".#(operator..truediv 1 0)\n")
    assert ">>> # Compilation failed!\nTraceback (most recent call last):\n  F" in err
    assert "\nZeroDivisionError: division by zero" in err
    assert out.count("#> ") == 2


def test_ic_error():
    out, err = cmd('lissp -i -c "(define answer 42)(truediv 1 0)"', "answer\n")
    assert "# Traceback (most" in err
    assert "# ZeroDivisionError: division by zero\n" in err
    assert ">>> answer\n" in err
    assert out.count("#> ") == 2
    assert "42" in out


def repl(input, out: str = '#> '*2, err: str = "", exitmsg=EXIT_MSG):
    actual_out, actual_err = cmd("lissp", input)
    assert actual_out.split('\n') == out.split('\n')
    assert actual_err[BANNER_LEN:].split('\n') == (err + exitmsg).split('\n')


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


def call_response(*session):
    stream = {k: [] for k in '<>!'}
    for line in session:
        stream[line[0]].append(line[2:])
    repl(*(''.join(stream[k]) for k in '<>!'))


def test_repl_empty_template_error():
    call_response(
        "> #> ", "< `\n",
        "> #..", "< x\n",
        "! >>> '__main__..x'\n",
        "> '__main__..x'\n",
        "> #> ", "< (`)\n",
        '!   File "<console>", line 1\n',
        "!     (`)\n",
        "!       ^\n",
        "! SyntaxError: Reader macro '`' missing argument.\n",
        "> #> ",
    )


def test_repl_gensym_error():
    err = """\
  File "<console>", line 1
    $#x
      ^
SyntaxError: Gensym outside of template.
"""
    repl("$#x\n", err=err)


def test_repl_empty_reader_macro_error():
    call_response(
        "> #> ", "< builtins..float#\n",
        "> #..", "< inf\n",
        "! >>> __import__('pickle').loads(  # inf\n",
        "! ...     b'Finf\\n.'\n",
        "! ... )\n",
        "> inf\n",
        "> #> ", "< (builtins..float#)\n",
        '!   File "<console>", line 1\n',
        "!     (builtins..float#)\n",
        "!                      ^\n",
        "! SyntaxError: Reader macro 'builtins..float#' missing argument.\n",
        "> #> ",
    )


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
b#""
b#"foo bar"
b#"


"
b#"

x"
(.decode b#"\\xff
foo" : errors 'ignore)
""",
        r"""#> ''
#> 'foo bar'
#> #..#..'\n\n'
#> #..#..#..'\n\nx\n'
#> b''
#> b'foo bar'
#> #..#..#..b'\n\n\n'
#> #..#..b'\n\nx'
#> #..'\nfoo'
#> """,
        r""">>> ('')
>>> ('foo bar')
>>> ('\n\n')
>>> ('\n\nx\n')
>>> b''
>>> b'foo bar'
>>> b'\n\n\n'
>>> b'\n\nx'
>>> b'\xff\nfoo'.decode(
...   errors='ignore')
""",
    )


def test_repl_paren_continue():
    call_response(
        '> #> ','< ()\n',
        '! >>> ()\n',
        '> ()\n',
        '> #> ', "< (\n",
        '> #..', "< )\n",
        '! >>> ()\n',
        '> ()\n',
        '> #> ', "< (\n",
        '> #..', "< \n",
        '> #..', "< )\n",
        '! >>> ()\n',
        '> ()\n',
        '> #> ', "< (\n",
        '> #..', "< \n",
        '> #..', "< \n",
        '> #..', "< )\n",
        '! >>> ()\n',
        '> ()\n',
        '> #> ',"< '(1 2)\n",
        '! >>> ((1),\n',
        '! ...  (2),)\n',
        '> (1, 2)\n',
        '> #> ',"< '(1\n",
        '> #..','< 2\n',
        '> #..','< )\n',
        '! >>> ((1),\n',
        '! ...  (2),)\n',
        '> (1, 2)\n',
        '> #> ',"< '(1\n",
        '> #..','< \n',
        '> #..','< \n',
        '> #..','< 2)\n',
        '! >>> ((1),\n',
        '! ...  (2),)\n',
        '> (1, 2)\n',
        '> #> ',
    )


def test_compile_error():
    call_response(
        '> #> ','< (lambda :x)',
        """! \
>>> # CompileError

(>   >  > >>('lambda', ':x')<< <  <   <)
# Compiler.function() CompileError:
#  Incomplete pair.
""",
        '> #> ',
    )
