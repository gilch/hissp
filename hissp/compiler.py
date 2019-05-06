# Copyright 2019 Matthew Egan Odendahl
# SPDX-License-Identifier: Apache-2.0

import ast
import pickle
import pickletools
from contextlib import suppress
from functools import wraps
from itertools import chain, takewhile
from typing import TypeVar, Iterable, Tuple

from hissp.munger import munge

BASIC = frozenset((type(None), bool, int, float, complex, bytes, str))


class CompileError(SyntaxError):
    pass


def trace(method):
    @wraps(method)
    def tracer(self, form):
        try:
            return method(self, form)
        except CompileError as e:
            e.msg = f"\n{method.__name__}:\n{form!r}" + e.msg
            raise e
        except Exception as e:
            raise CompileError(f"\n{method.__name__}:\n{form!r}") from e

    return tracer


class Compiler:
    """
    The Hissp compiler.
    """

    def __init__(self, ns=None, evaluate=True):
        self.ns = ns or {"__name__": "<compiler>", munge("?"): {}}
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
            raise CompileError("\n" + form) from e

    def form(self, form) -> str:
        """
        Translate Hissp form to the equivalent Python code as a string.
        """
        if type(form) is tuple and form:
            return self.tuple(form)
        if type(form) is str:
            return self.symbol(form)
        return self.quoted(form)

    def tuple(self, form: tuple) -> str:
        """Calls, macros, special forms."""
        head, *tail = form
        if type(head) is str:
            head = self.alias(head)
            if head == "quote":
                if len(form) != 2:
                    raise SyntaxError
                return self.quoted(form[1])
            if head == "\\":
                return self.fn(form)
            if "/!." in head or head.startswith("!."):
                return self.macro(head, tail)
        return self.call(form)

    def quoted(self, form) -> str:
        """Compile forms that evaluate to themselves."""
        case = type(form)
        if case is list:
            return f"[{self._elements(form)}]"
        if case is set:
            return f"""{{{self._elements(form) or "*''"}}}"""
        if case is tuple:
            return f"({self._elements(form)},)" if form else "()"
        if case is dict:
            return "{%s}" % ",".join(
                f"{self.quoted(k)}:{self.quoted(v)}" for k, v in form.items()
            )
        if case in BASIC:
            with suppress(ValueError):  # Some repr()s don't round-trip.
                return self.basic(form)
        return self.pickle(form)

    def _elements(self, form) -> str:
        return ",".join(map(self.quoted, form))

    def basic(self, form) -> str:
        result = repr(form)
        ast.literal_eval(result)  # Does it round-trip?
        return result

    @trace
    def pickle(self, form) -> str:
        """The final fallback for self.quoted()."""
        dumps = pickletools.optimize(pickle.dumps(form, -1))
        return f"__import__('pickle').loads(  # {form!r}\n{dumps})"

    def fn(self, form: tuple) -> str:
        r"""
        Function definition special form.

        (\ (<parameters>)
          <body>)

        The parameter tuple is further divided into (<single> & <paired>)

        Parameter types are the same as Python's.
        For example,
        >>> transpile(
        ... ('\\', ('a','b',
        ...         '&', 'e',1, 'f',2,
        ...         '*','args', 'h',4, 'i','?', 'j',1,
        ...         '**','kwargs'),
        ...   42)
        ... )
        '(lambda a,b,e=(1),f=(2),*args,h=(4),i,j=(1),**kwargs:42)'

        The special names * and ** designate the remainder of the positional
        and keyword parameters, respectively.
        Note this body has an implicit PROGN.
        >>> transpile(
        ... ('\\', ('&','*','args','**','kwargs'),
        ...   ('print','args'),
        ...   ('print','kwargs'))
        ... )
        '(lambda *args,**kwargs:((print)(args),(print)(kwargs))[-1])'

        You can omit the right of a pair with ? (except the final **kwargs).
        Also note that the body can be empty.
        >>> transpile(
        ... ('\\', ('&','a',1, '*','?', 'b','?', 'c',2))
        ... )
        '(lambda a=(1),*,b,c=(2):())'

        The '&' may be omitted if there are no paired parameters.
        >>> transpile(('\\', ('a','b','c','&')))
        '(lambda a,b,c:())'
        >>> transpile(('\\', ('a','b','c')))
        '(lambda a,b,c:())'
        >>> transpile(('\\', ('&')))
        '(lambda :())'
        >>> transpile(('\\', ()))
        '(lambda :())'

        & is required if there are any paired parameters, even if there
        are no single parameters.
        >>> transpile(('\\', ('&','**','kwargs')))
        '(lambda **kwargs:())'
        """
        fn, parameters, *body = form
        assert fn == "\\"
        return f"(lambda {','.join(self.parameters(parameters))}:{self.body(body)})"

    @trace
    def parameters(self, parameters: tuple) -> Iterable[str]:
        parameters = iter(parameters)
        yield from (munge(a) for a in takewhile(lambda a: a != "&", parameters))
        for k, v in pairs(parameters):
            if k == "*":
                yield "*" if v == "?" else f"*{munge(v)}"
            elif k == "**":
                yield f"**{munge(v)}"
            elif v == "?":
                yield munge(k)
            else:
                yield f"{munge(k)}={self.form(v)}"

    @trace
    def body(self, body: list) -> str:
        if len(body) > 1:
            return f"({','.join(map(self.form, body))})[-1]"
        if not body:
            return "()"
        return self.form(body[0])

    def macro(self, head: str, tail: tuple) -> str:
        expansion = f"{self.symbol(head)}({(','.join(map(self.quoted, tail)))})"
        try:
            expansion = eval(compile(expansion, f"<macro {head}>", "eval"), self.ns)
        except Exception as e:
            raise CompileError(f"\nexpand:\n{expansion}") from e
        return self.form(expansion)

    @trace
    def call(self, form: tuple) -> str:
        r"""
        Call form.

        Any tuple that is not quoted, empty, or a special form or macro is
        a call.

        Like Python, it has three parts.
        (<callable> <args> & <kwargs>)
        For example,
        >>> transpile(
        ... ('print',1,2,3,'&','sep',('quote',":"), 'end',('quote',"\n\n"))
        ... )
        "(print)(1,2,3,sep=(':'),end=('\\n\\n'))"

        Either <args> or <kwargs> may be empty.
        >>> transpile(('foo','&'))
        '(foo)()'
        >>> transpile(('foo','bar','&'))
        '(foo)(bar)'
        >>> transpile(('foo','&','bar','baz'))
        '(foo)(bar=(baz))'

        The & is optional if the <kwargs> part is empty.
        >>> transpile(('foo',))
        '(foo)()'
        >>> transpile(('foo','bar'))
        '(foo)(bar)'

        The <kwargs> part has implicit pairs; there must be an even number.

        Use the special keywords * and ** for iterable and mapping unpacking
        >>> transpile(
        ... ('print','&','*',[1,2], 'a',3, '*',[4], '**',{'sep':':','end':'\n\n'})
        ... )
        "(print)(*([1,2]),a=(3),*([4]),**({'sep':':','end':'\\n\\n'}))"

        Unlike other keywords, these can be repeated, but a '*' is not
        allowed to follow '**', as in Python.

        Method calls are similar to function calls.
        (.<method name> <object> <args> & <kwargs>)
        Like Clojure, a method on the first object is assumed if the
        function name starts with a dot.
        >>> transpile(('.conjugate', 1j))
        '(1j).conjugate()'
        >>> eval(_)
        -1j
        >>> transpile(('.decode', b'\xfffoo', '&', 'errors',('quote','ignore')))
        "(b'\\xfffoo').decode(errors=('ignore'))"
        >>> eval(_)
        'foo'
        """
        form = iter(form)
        head = next(form)
        args = chain(
            map(self.form, takewhile(lambda a: a != "&", form)),
            (
                f"{k}({self.form(v)})"
                if k in "**" and k
                else f"{munge(k)}=({self.form(v)})"
                for k, v in pairs(form)
            ),
        )
        if type(head) is str and head.startswith("."):
            return f"{next(args)}.{munge(head[1:])}({','.join(args)})"
        return f"{self.form(head)}({','.join(args)})"

    @trace
    def symbol(self, symbol: str) -> str:
        symbol = self.alias(symbol)
        if "/" in symbol and not symbol.startswith("/"):
            parts = symbol.split("/", 1)
            return "__import__({0!r}{fromlist}).{1}".format(
                parts[0],
                munge(parts[1]),
                fromlist=",fromlist='?'" if "." in parts[0] else "",
            )
        return munge(symbol)

    def alias(self, symbol: str) -> str:
        return self.ns[munge("?")].get(symbol, symbol)


T = TypeVar("T")


def pairs(it: Iterable[T]) -> Iterable[Tuple[T, T]]:
    it = iter(it)
    for k in it:
        yield k, next(it)


def transpile(*forms):
    return Compiler().compile(forms)
