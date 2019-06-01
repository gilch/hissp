# Copyright 2019 Matthew Egan Odendahl
# SPDX-License-Identifier: Apache-2.0

import ast
import pickle
import pickletools
import re
from contextlib import contextmanager, suppress
from contextvars import ContextVar
from functools import wraps
from itertools import chain, takewhile
from typing import Iterable, Tuple, TypeVar

PAIR_WORDS = {":*": "*", ":**": "**", ":_": ""}
# Module Macro container
MACROS = "_macro_"
# Macro from foreign module foo.bar.._macro_.baz
MACRO = f"..{MACROS}."

NUMBER = frozenset({int, float, complex})

# Sometimes macros need the current ns when expanding,
# instead of its defining ns.
# Rather than pass in an implicit argument, it's available here.
# readerless() uses this automatically.
NS = ContextVar("NS", default=None)


class CompileError(SyntaxError):
    pass


def trace(method):
    @wraps(method)
    def tracer(self, *args, **kwargs):
        try:
            return method(self, *args, **kwargs)
        except CompileError as e:
            e.msg = f"\nself.{method.__name__}(*{args},**{kwargs})\n" + e.msg
            raise e
        except Exception as e:
            raise CompileError(f"\nself.{method.__name__}(*{args},**{kwargs})\n") from e

    return tracer


class Compiler:
    """
    The Hissp compiler.
    """

    def __init__(self, qualname="_repl", ns=None, evaluate=True):
        self.qualname = qualname
        self.ns = ns or {"__name__": "<compiler>"}
        self.evaluate = evaluate

    def compile(self, forms: Iterable) -> str:
        result = []
        for form in forms:
            form = self.form(form)
            self.eval(form)
            result.append(form)
        return "\n\n".join(result)

    def eval(self, form):
        if not self.evaluate:
            return
        try:
            eval(compile(form, "<Hissp>", "eval"), self.ns)
        except Exception as e:
            print("Exception when evaluating form:")
            print(form)
            raise CompileError(f"\n{form!r}") from e

    def form(self, form) -> str:
        """
        Translate Hissp form to the equivalent Python code as a string.
        """
        if type(form) is tuple and form:
            return self.tuple(form)
        if type(form) is str and not form.startswith(":"):
            return self.symbol(form)
        return self.quoted(form)

    def tuple(self, form: tuple) -> str:
        """Calls, macros, special forms."""
        head, *tail = form
        if type(head) is str:
            return self.special(form, head, tail)
        return self.call(form)

    def special(self, form: tuple, head: str, tail: list) -> str:
        """Try to compile as special form, else self.macro()."""
        if head == "quote":
            if len(form) != 2:
                raise SyntaxError
            return self.quoted(form[1])
        if head == "lambda":
            return self.function(form)
        return self.macro(form, head, tail)

    @trace
    def macro(self, form: tuple, head: str, tail: list) -> str:
        """Try to compile as macro, else normal call."""
        parts = head.split(MACRO, 1)
        with self.macro_context():
            if parts[0] == self.qualname:
                # Local qualified macro. Recursive macros might need it.
                return f"# {head}\n" + self.form(vars(self.ns[MACROS])[parts[1]](*tail))
            try:  # Is it a local unqualified macro?
                macro = vars(self.ns[MACROS])[head]
            except LookupError:  # Nope.
                pass
            else:  # Yes.
                return f"# {head}\n" + self.form(macro(*tail))
            if MACRO in head:  # Qualified macro, not local.
                return f"# {head}\n" + self.form(eval(self.symbol(head))(*tail))
        return self.call(form)

    def quoted(self, form) -> str:
        r"""
        Compile forms that evaluate to themselves.

        Emits a literal if possible, otherwise falls back to pickle.
        >>> readerless(-4.2j)
        '((-0-4.2j))'
        >>> print(readerless(float('nan')))
        __import__('pickle').loads(  # nan
            b'\x80\x03G\x7f\xf8\x00\x00\x00\x00\x00\x00.'
        )
        >>> readerless([{'foo':2},(),1j,2.0,{3}])
        "[{'foo': 2}, (), 1j, 2.0, {3}]"
        >>> spam = []
        >>> spam.append(spam)
        >>> print(readerless(spam))
        __import__('pickle').loads(  # [[...]]
            b'\x80\x03]q\x00h\x00a.'
        )
        """
        # Number literals may need (). E.g. (1).real
        literal = f"({form!r})" if type(form) in NUMBER else repr(form)
        with suppress(ValueError):
            if ast.literal_eval(literal) == form:
                return literal
        # Wasn't made with ast.literal_eval(). Fall back to pickle.
        return self.pickle(form)

    @trace
    def pickle(self, form) -> str:
        """The final fallback for self.quoted()."""
        dumps = pickletools.optimize(pickle.dumps(form))
        return f"__import__('pickle').loads(  # {form!r}\n    {dumps}\n)"

    def function(self, form: tuple) -> str:
        r"""
        Anonymous function special form.

        (lambda (<parameters>)
          <body>)

        The parameters tuple is divided into (<single> : <paired>)

        Parameter types are the same as Python's.
        For example,
        >>> readerless(
        ... ('lambda', ('a','b',
        ...         ':', 'e',1, 'f',2,
        ...         ':*','args', 'h',4, 'i',':_', 'j',1,
        ...         ':**','kwargs',),
        ...   42,),
        ... )
        '(lambda a,b,e=(1),f=(2),*args,h=(4),i,j=(1),**kwargs:(42))'

        The special keywords :* and :** designate the remainder of the
        positional and keyword parameters, respectively.
        Note this body has an implicit PROGN.
        >>> print(readerless(
        ... ('lambda', (':',':*','args',':**','kwargs',),
        ...   ('print','args',),
        ...   ('print','kwargs',),),
        ... ))
        (lambda *args,**kwargs:(
          print(
            args),
          print(
            kwargs))[-1])

        You can omit the right of a pair with :_ (except the final **kwargs).
        Also note that the body can be empty.
        >>> readerless(
        ... ('lambda', (':','a',1, ':*',':_', 'b',':_', 'c',2,),),
        ... )
        '(lambda a=(1),*,b,c=(2):())'

        The ':' may be omitted if there are no paired parameters.
        >>> readerless(('lambda', ('a','b','c',':',),),)
        '(lambda a,b,c:())'
        >>> readerless(('lambda', ('a','b','c',),),)
        '(lambda a,b,c:())'
        >>> readerless(('lambda', (':',),),)
        '(lambda :())'
        >>> readerless(('lambda', (),),)
        '(lambda :())'

        : is required if there are any paired parameters, even if there
        are no single parameters.
        >>> readerless(('lambda', (':',':**','kwargs',),),)
        '(lambda **kwargs:())'
        """
        fn, parameters, *body = form
        assert fn == "lambda"
        return f"(lambda {','.join(self.parameters(parameters))}:{self.body(body)})"

    @trace
    def parameters(self, parameters: tuple) -> Iterable[str]:
        parameters = iter(parameters)
        yield from takewhile(lambda a: a != ":", parameters)
        for k, v in pairs(parameters):
            if k == ":*":
                yield "*" if v == ":_" else f"*{v}"
            elif k == ":**":
                yield f"**{v}"
            elif v == ":_":
                yield k
            else:
                yield f"{k}={self.form(v)}"

    @trace
    def body(self, body: list) -> str:
        if len(body) > 1:
            return f"({_join_args(*map(self.form, body))})[-1]"
        if not body:
            return "()"
        result = self.form(body[0])
        return ("\n" * ("\n" in result) + result).replace("\n", "\n  ")

    @trace
    def call(self, form: tuple) -> str:
        r"""
        Call form.

        Any tuple that is not quoted, empty, or a special form or macro is
        a runtime call.

        Like Python, it has three parts.
        (<callable> <args> : <kwargs>)
        For example,
        >>> print(readerless(
        ... ('print',1,2,3,':','sep',('quote',":",), 'end',('quote',"\n\n",),)
        ... ))
        print(
          (1),
          (2),
          (3),
          sep=':',
          end='\n\n')

        Either <args> or <kwargs> may be empty.
        >>> readerless(('foo',':',),)
        'foo()'
        >>> print(readerless(('foo','bar',':',),))
        foo(
          bar)
        >>> print(readerless(('foo',':','bar','baz',),))
        foo(
          bar=baz)

        The : is optional if the <kwargs> part is empty.
        >>> readerless(('foo',),)
        'foo()'
        >>> print(readerless(('foo','bar',),),)
        foo(
          bar)

        The <kwargs> part has implicit pairs; there must be an even number.

        Use the special keywords :* and :** for iterable and mapping unpacking.
        >>> print(readerless(
        ... ('print',':',':*',[1,2], 'a',3, ':*',[4], ':**',{'sep':':','end':'\n\n'},),
        ... ))
        print(
          *[1, 2],
          a=(3),
          *[4],
          **{'sep': ':', 'end': '\n\n'})

        Unlike other keywords, these can be repeated, but a '*' is not
        allowed to follow '**', as in Python.

        Method calls are similar to function calls.
        (.<method name> <object> <args> & <kwargs>)
        Like Clojure, a method on the first object is assumed if the
        function name starts with a dot.
        >>> readerless(('.conjugate', 1j,),)
        '(1j).conjugate()'
        >>> eval(_)
        -1j
        >>> readerless(('.decode', b'\xfffoo', ':', 'errors',('quote','ignore',),),)
        "b'\\xfffoo'.decode(\n  errors='ignore')"
        >>> eval(_)
        'foo'
        """
        form = iter(form)
        head = next(form)
        args = chain(
            map(self.form, takewhile(lambda a: a != ":", form)),
            (f"{(PAIR_WORDS.get(k, k+'='))}{self.form(v)}" for k, v in pairs(form)),
        )
        if type(head) is str and head.startswith("."):
            return "{}.{}({})".format(next(args), head[1:], _join_args(*args))
        return "{}({})".format(self.form(head), _join_args(*args))

    @trace
    def symbol(self, symbol: str) -> str:
        if re.search(r"^..|[ ()]", symbol):
            return symbol
        if ".." in symbol:
            parts = symbol.split("..", 1)
            return "__import__({0!r}{fromlist}).{1}".format(
                parts[0], parts[1], fromlist=",fromlist='?'" if "." in parts[0] else ""
            )
        return symbol

    @contextmanager
    def macro_context(self):
        token = NS.set(self.ns)
        try:
            yield
        finally:
            NS.reset(token)


def _join_args(*args):
    return (("\n" if args else "") + ",\n".join(args)).replace("\n", "\n  ")


T = TypeVar("T")


def pairs(it: Iterable[T]) -> Iterable[Tuple[T, T]]:
    it = iter(it)
    for k in it:
        yield k, next(it)


def readerless(form, ns=None):
    ns = ns or NS.get() or {"__name__": "<compiler>"}
    return Compiler(evaluate=False, ns=ns).compile([form])
