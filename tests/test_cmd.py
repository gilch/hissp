# Copyright 2020, 2021, 2022, 2024 Matthew Egan Odendahl
# SPDX-License-Identifier: Apache-2.0
import os
import pathlib
import subprocess as sp
from sys import executable as python
from textwrap import dedent


def cmd(cmd, input="", shell=True):
    return sp.Popen(
        cmd, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE, text=True, shell=shell
    ).communicate(input=input)


EXIT_MSG = "\nnow exiting LisspREPL...\n"
BANNER = cmd("lissp")[1][: -len(EXIT_MSG)]
HISSP_C = (python, "-m", "hissp", "-c")


def test_c_args():
    out, err = cmd('python -m hissp -c "(print sys..argv)" 1 2 3')
    assert [out, err] == ["['-c', '1', '2', '3']\n", ""]


def test_reproducible_gensym():
    args = HISSP_C + ("(print `$#G `($#G $#G))",)
    out, err = once = cmd(args, shell=False)
    again = cmd(args, shell=False)
    assert once == again
    assert err == ""
    assert "_Qz" in out


def test_unique_gensyms():
    err = [None] * 2
    arg = "(print `$#G `($#G $#G))"
    once, err[0] = cmd(HISSP_C + (arg,), shell=False)
    again, err[1] = cmd(HISSP_C + ("0 " + arg,), shell=False)
    assert err == ["", ""]
    assert once != again
    assert "_Qz" in once
    assert "_Qz" in again


def test_ic_args():
    out, err = cmd(
        'lissp -i -c "(print sys..argv)(define answer 42)" 1 2 3', "answer\n"
    )
    assert [out, err[len(BANNER) :]] == [
        "['-c', '1', '2', '3']\n#> 42\n#> ",
        ">>> answer\n" + EXIT_MSG,
    ]


def test_file_args():
    out, err = cmd("lissp tests/argv.lissp 1 2 3")
    expected = """\
['tests/argv.lissp', '1', '2', '3']
__name__='__main__' __package__=None
"""
    assert [out, err] == [expected, ""]


def test_i_file_args():
    out, err = cmd("lissp -i tests/argv.lissp 1 2 3", "answer\n")
    expected = """\
['tests/argv.lissp', '1', '2', '3']
__name__='__main__' __package__=None
#> 42
#> """
    assert [out, err[len(BANNER) :]] == [
        expected,
        ">>> answer\n" + EXIT_MSG,
    ]


def test_repl_read_exception():
    out, err = cmd("python -m hissp", ".#(operator..truediv 1 0)\n")
    assert ">>> # Compilation failed!\nTraceback (most recent call last):\n  F" in err
    assert "\nZeroDivisionError: division by zero" in err
    assert out.count("#> ") == 2


def test_ic_error():
    out, err = cmd('lissp -i -c "(define answer 42)(truediv 1 0)"', "answer\n")
    assert "Hissp abort!" in err
    assert "Traceback (most" in err
    assert 'File "<Compiled Hissp #3 of __main__:\n1 truediv(' in err
    assert "ZeroDivisionError: division by zero\n" in err
    assert ">>> answer\n" in err
    assert out.count("#> ") == 2
    assert "42" in out


def repl(input, out: str = "#> " * 2, err: str = "", exitmsg=EXIT_MSG):
    actual_out, actual_err = cmd("lissp", dedent(input))
    assert dict(
        out=actual_out.split("\n"), err=actual_err[len(BANNER) :].split("\n")
    ) == dict(
        out=dedent(out).split("\n"),
        err=(dedent(err) + exitmsg).split("\n"),
    )


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
    SyntaxError: unquote outside of template
    """
    repl(",\n", err=err)


def test_repl_splice_error():
    err = """\
      File "<console>", line 1
        ,@
         ^
    SyntaxError: unquote outside of template
    """
    repl(",@\n", err=err)


def call_response(*session):
    stream = {k: [] for k in "<>!"}
    for line in session:
        stream[line[0]].append(line[2:])
    repl(*("".join(stream[k]) for k in "<>!"))


def test_repl_empty_template_error():
    call_response(
        "> #> ", "< `\n",
        "> #..", "< x\n",
        "! >>> '__main__..x'\n",
        "> '__main__..x'\n",
        "> #> ", "< (`)\n",
        '!   File "<console>", line 1\n',
        "!     (`)\n",
        "!      ^\n",
        "! SyntaxError: tag '`' missing argument\n",
        "> #> ",
    )  # fmt: skip


def test_repl_gensym_error():
    err = """\
      File "<console>", line 1
        $#x
          ^
    SyntaxError: gensym outside of template
    """
    repl("$#x\n", err=err)


def test_repl_empty_reader_macro_error():
    call_response(
        "> #> ", "< builtins..float#\n",
        "> #..", "< inf\n",
        "! >>> # inf\n",
        "! ... __import__('pickle').loads(b'Finf\\n.')\n",
        "> inf\n",
        "> #> ", "< (builtins..float#)\n",
        '!   File "<console>", line 1\n',
        "!     (builtins..float#)\n",
        "!                     ^\n",
        "! SyntaxError: tag 'builtins..float#' missing argument\n",
        "> #> ",
    )  # fmt: skip


def test_repl_read_error():
    err = """\
      File "<console>", line 1
        \\
        ^
    SyntaxError: can't read this
    """
    repl("\\\n", err=err)


def test_repl_unopened_error():
    err = """\
      File "<console>", line 1
        )
        ^
    SyntaxError: too many `)`s
    """
    repl(")\n", err=err)


def test_repl_str_continue():
    repl(
        input="""\
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
        (.decode b#<#;\\xff
        ;; foo
                 : errors 'ignore)
        """,
        out="""\
        """
        R"""#> ''
        #> 'foo bar'
        #> #..#..'\n\n'
        #> #..#..#..'\n\nx\n'
        #> b''
        #> b'foo bar'
        #> #..#..#..b'\n\n\n'
        #> #..#..b'\n\nx'
        #> #..#..'\nfoo'
        #> """,
        err="""\
        """
        R""">>> ('')
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
        "> #> ", "< ()\n",
        "! >>> ()\n",
        "> ()\n",
        "> #> ", "< (\n",
        "> #..", "< )\n",
        "! >>> ()\n",
        "> ()\n",
        "> #> ", "< (\n",
        "> #..", "< \n",
        "> #..", "< )\n",
        "! >>> ()\n",
        "> ()\n",
        "> #> ", "< (\n",
        "> #..", "< \n",
        "> #..", "< \n",
        "> #..", "< )\n",
        "! >>> ()\n",
        "> ()\n",
        "> #> ", "< '(1 2)\n",
        "! >>> ((1),\n",
        "! ...  (2),)\n",
        "> (1, 2)\n",
        "> #> ", "< '(1\n",
        "> #..", "< 2\n",
        "> #..", "< )\n",
        "! >>> ((1),\n",
        "! ...  (2),)\n",
        "> (1, 2)\n",
        "> #> ", "< '(1\n",
        "> #..", "< \n",
        "> #..", "< \n",
        "> #..", "< 2)\n",
        "! >>> ((1),\n",
        "! ...  (2),)\n",
        "> (1, 2)\n",
        "> #> ",
    )  # fmt: skip


def test_compile_error():
    call_response(
        "> #> ", "< (lambda :x)",
        "! >>> # CompileError\n",
        "! \n",
        "! (\n",
        "!  lambda (>   >  > >>':x'<< <  <   <)\n",
        "! # Compiler.parameters() CompileError:\n",
        "! #  incomplete pair\n",
        "! :\n",
        "!     ())\n",
        "> #> ",
    )  # fmt: skip


def test_interact():
    call_response(
        "> #> ", "< (.update (globals) : x 1  y 2)\n",
        "! >>> globals().update(\n",
        "! ...   x=(1),\n",
        "! ...   y=(2))\n",
        "> #> ", "< (let (x 42) (hissp..interact))\n",
        "! >>> # let\n",
        "! ... (lambda x=(42): __import__('hissp').interact())()\n",
        f"! {BANNER}",
        "> #> ", "< x\n",
        "! >>> x\n",
        "> 42\n",
        "> #> ", "< y\n",
        "! >>> y\n",
        "> 2\n",
        "> #> ",  # EOF
        f"! {EXIT_MSG}",
        "> #> ",
    )  # fmt: skip


def test_interact_locals():
    call_response(
        "> #> ", "< (hissp..interact (dict : x 7))\n",
        "! >>> __import__('hissp').interact(\n",
        "! ...   dict(\n",
        "! ...     x=(7)))\n",
        f"! {BANNER}",
        "> #> ", "< x\n",
        "! >>> x\n",
        "> 7\n",
        "> #> ",  # EOF
        f"! {EXIT_MSG}",
        "> #> ",
    )  # fmt: skip


def test_subrepl():
    call_response(
        "> #> ", "< hissp..subrepl#sys.\n",
        "! >>> (lambda module=__import__('sys'):\n",
        "! ...     # hissp.._macro_.unless\n",
        "! ...     (lambda b, a: ()if b else a())(\n",
        "! ...       __name__==module.__name__,\n",
        "! ...       (lambda :\n",
        "! ...          (print(\n",
        "! ...             'Entering',\n",
        "! ...             module.__name__),\n",
        "! ...           __import__('hissp').interact(\n",
        "! ...             __import__('builtins').vars(\n",
        "! ...               module)),\n",
        "! ...           print(\n",
        "! ...             'back in',\n",
        "! ...             __name__))  [-1]\n",
        "! ...       ))\n",
        "! ... )()\n",
        "> Entering sys\n",
        f"! {BANNER}",
        "> #> ", "< (operator..is_ (vars) (vars sys.))\n",
        "! >>> __import__('operator').is_(\n",
        "! ...   vars(),\n",
        "! ...   vars(\n",
        "! ...     __import__('sys')))\n",
        "> True\n",
        "> #> ",
        f"! {EXIT_MSG}",
        "> back in __main__\n",
        "> #> ",
    )  # fmt: skip


def test_refresh():
    try:
        pathlib.Path("__refresh.lissp").write_text("")
        pathlib.Path("__refresh.py").write_text("foo=1\n")
        import __refresh

        call_response(
            "> #> ", "< hissp..subrepl#__refresh.\n",
            "! >>> (lambda module=__import__('__refresh'):\n",
            "! ...     # hissp.._macro_.unless\n",
            "! ...     (lambda b, a: ()if b else a())(\n",
            "! ...       __name__==module.__name__,\n",
            "! ...       (lambda :\n",
            "! ...          (print(\n",
            "! ...             'Entering',\n",
            "! ...             module.__name__),\n",
            "! ...           __import__('hissp').interact(\n",
            "! ...             __import__('builtins').vars(\n",
            "! ...               module)),\n",
            "! ...           print(\n",
            "! ...             'back in',\n",
            "! ...             __name__))  [-1]\n",
            "! ...       ))\n",
            "! ... )()\n",
            "> Entering __refresh\n",
            f"! {BANNER}",
            "> #> ", "< foo\n",
            "! >>> foo\n",
            "> 1\n",
            "> #> ", """< (.write_text (pathlib..Path '__refresh.lissp) "|foo=2|")\n""",
            "! >>> __import__('pathlib').Path(\n",
            "! ...   '__refresh.lissp').write_text(\n",
            "! ...   ('|foo=2|'))\n",
            "> 7\n",
            "> #> ", "< hissp..refresh#:\n",
            "! >>> (lambda name=__name__:\n",
            "! ...    (__import__('hissp.reader',fromlist='*').transpile(\n",
            '! ...       *name.rpartition(".")[::2]),\n',
            "! ...     __import__('importlib').reload(\n",
            "! ...       __import__('importlib').import_module(\n",
            "! ...         name)))  [-1]\n",
            "! ... )()\n",
            f"> {__refresh!r}\n",
            "> #> ", "< foo\n",
            "! >>> foo\n",
            "> 2\n",
            "> #> ",
            f"! {EXIT_MSG}",
            "> back in __main__\n",
            "> #> ",
        )  # fmt: skip
    finally:
        os.remove("__refresh.py")
        os.remove("__refresh.lissp")
