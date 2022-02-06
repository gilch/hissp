# Copyright 2019, 2020, 2021, 2022 Matthew Egan Odendahl
# SPDX-License-Identifier: Apache-2.0

"""
The Hissp data-structure language compiler and associated helper functions.
"""

import ast
import builtins
import pickle
import pickletools
import re
import sys
from contextlib import contextmanager, suppress
from contextvars import ContextVar
from functools import wraps
from itertools import chain, takewhile, starmap
from pprint import pformat
from traceback import format_exc
from types import ModuleType
from typing import Iterable, List, NewType, Tuple, TypeVar, Union
from warnings import warn

PAIR_WORDS = {":*": "*", ":**": "**", ":?": ""}
# Module Macro container
MACROS = "_macro_"
# Macro from foreign module foo.bar.._macro_.baz
MACRO = f"..{MACROS}."
MAYBE = "..QzMaybe_."
RE_MACRO = re.compile(rf"({re.escape(MACRO)}|{re.escape(MAYBE)})")

NS = ContextVar("NS", default=())
"""
Sometimes macros need the current namespace when expanding,
instead of its defining namespace.
Rather than pass in an implicit argument to all macros,
it's available here.
`readerless` uses this automatically.
"""

Sentinel = NewType("Sentinel", object)
_SENTINEL = Sentinel(object())


class CompileError(SyntaxError):
    """Catch-all exception for compilation failures."""


def _trace(method):
    @wraps(method)
    def tracer(self, expr):
        try:
            return method(self, expr)
        except Exception as e:
            self.error = e
            message = (
                f"\nCompiler.{method.__name__}() {type(e).__name__}:\n {e}".replace(
                    "\n", "\n# "
                )
            )
            return f"(>   >  > >>{pformat(expr)}<< <  <   <){message}"

    return tracer


class PostCompileWarning(Warning):
    """Form compiled to Python, but execution of it failed."""


class Compiler:
    """
    The Hissp recursive-descent compiler.

    Translates the Hissp data-structure language into a functional
    subset of Python.
    """

    def __init__(self, qualname="__main__", ns=None, evaluate=True):
        self.qualname = qualname
        self.ns = self.new_ns(qualname) if ns is None else ns
        self.evaluate = evaluate
        self.error = False
        self.abort = False

    @staticmethod
    def new_ns(name, doc=None, package=None):
        """Creates and initializes a dict namespace like a module,
        with the given `__name__`, ``__doc__``, and `__package__`;
        ``__builtins__``; an empty ``__annotations__``; and whatever
        else Python currently adds to new module objects.
        """
        mod = ModuleType(name, doc)
        mod.__annotations__ = {}
        mod.__package__ = package
        mod.__builtins__ = builtins
        return vars(mod)

    def compile(self, forms: Iterable) -> str:
        """
        Compile multiple forms, and execute them if evaluate mode enabled.
        """
        result: List[str] = []
        for form in forms:
            form = self.form(form)
            if self.error:
                e = self.error
                self.error = False
                raise CompileError("\n" + form) from e
            result.extend(self.eval(form))
            if self.abort:
                print("\n\n".join(result), file=sys.stderr)
                self.abort = False  # To allow REPL debugging.
                sys.exit(1)
        return "\n\n".join(result)

    @_trace
    def form(self, form) -> str:
        """
        Compile Hissp form to the equivalent Python code in a string.
        `tuple` and `str` have special evaluation rules,
        otherwise it's an `atom` that represents itself.
        """
        if type(form) is tuple and form:
            return self.tuple(form)
        if type(form) is str and not form.startswith(":"):
            return self.str(form)
        return self.atom(form)

    @_trace
    def tuple(self, form: Tuple) -> str:
        """Compile `call`, `macro`, or `special` forms."""
        head, *tail = form
        if type(head) is str:
            return self.special(form)
        return self.call(form)

    @_trace
    def special(self, form: Tuple) -> str:
        """Try to compile as special form, else `invocation`."""
        if form[0] == "quote":
            return self.atom(*form[1:])
        if form[0] == "lambda":
            return self.function(form)
        return self.invocation(form)

    @_trace
    def function(self, form: Tuple) -> str:
        R"""
        Compile the anonymous function special form.

        (lambda (<parameters>)
          <body>)

        The parameters tuple is divided into (<single> : <paired>)

        Parameter types are the same as Python's.
        For example,

        >>> readerless(
        ... ('lambda', ('a',':/','b',
        ...             ':', 'e',1, 'f',2,
        ...             ':*','args', 'h',4, 'i',':?', 'j',1,
        ...             ':**','kwargs',),
        ...   42,),
        ... )
        '(lambda a,/,b,e=(1),f=(2),*args,h=(4),i,j=(1),**kwargs:(42))'

        The special control words ``:*`` and ``:**`` designate the
        remainder of the positional and keyword parameters, respectively.
        Note this body evaluates expressions in sequence, for side
        effects.

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

        You can omit the right of a pair with ``:?``
        (except the final ``**kwargs``).
        Also note that the body can be empty.

        >>> readerless(
        ... ('lambda', (':','a',1, ':/',':?', ':*',':?', 'b',':?', 'c',2,),),
        ... )
        '(lambda a=(1),/,*,b,c=(2):())'

        The ``:`` may be omitted if there are no paired parameters.

        >>> readerless(('lambda', ('a','b','c',':',),),)
        '(lambda a,b,c:())'
        >>> readerless(('lambda', ('a','b','c',),),)
        '(lambda a,b,c:())'
        >>> readerless(('lambda', (':',),),)
        '(lambda :())'
        >>> readerless(('lambda', (),),)
        '(lambda :())'

        The ``:`` is required if there are any paired parameters, even
        if there are no single parameters:

        >>> readerless(('lambda', (':',':**','kwargs',),),)
        '(lambda **kwargs:())'

        """
        fn, parameters, *body = form
        assert fn == "lambda"
        return f"(lambda {','.join(self.parameters(parameters))}:{self.body(body)})"

    @_trace
    def parameters(self, parameters: Iterable) -> Iterable[str]:
        """Process parameters to compile `function`."""
        parameters = iter(parameters)
        yield from (
            {":/": "/", ":*": "*"}.get(a, a)
            for a in takewhile(lambda a: a != ":", parameters)
        )
        for k, v in _pairs(parameters):
            if k == ":*":
                yield "*" if v == ":?" else f"*{v}"
            elif k == ":/":
                yield "/"
            elif k == ":**":
                yield f"**{v}"
            elif v == ":?":
                yield k
            else:
                yield f"{k}={self.form(v)}"

    @_trace
    def body(self, body: list) -> str:
        """Compile body of `function`."""
        if len(body) > 1:
            return f"({_join_args(*map(self.form, body))})[-1]"
        if not body:
            return "()"
        result = self.form(body[0])
        return ("\n" * ("\n" in result) + result).replace("\n", "\n  ")

    @_trace
    def invocation(self, form: Tuple) -> str:
        """Try to compile as `macro`, else normal `call`."""
        if (result := self.macro(form)) is not _SENTINEL:
            return f"# {form[0]}\n{result}"
        form = form[0].replace(MAYBE, "..", 1), *form[1:]
        return self.call(form)

    @_trace
    def macro(self, form: Tuple) -> Union[str, Sentinel]:
        """Macroexpand and start over with `form`, if it's a macro."""
        head, *tail = form
        if (macro := self._get_macro(head)) is not None:
            with self.macro_context():
                return self.form(macro(*tail))
        return _SENTINEL

    def _get_macro(self, head):
        parts = RE_MACRO.split(head, 1)
        head = head.replace(MAYBE, MACRO, 1)
        if len(parts) > 1:
            return self._qualified_macro(head, parts)
        return self._unqualified_macro(head)

    def _qualified_macro(self, head, parts):
        try:
            if parts[0] == self.qualname:  # Internal?
                return vars(self.ns[MACROS])[parts[2]]
            return eval(self.str(head))
        except (KeyError, AttributeError):
            if parts[1] != MAYBE:
                raise

    def _unqualified_macro(self, head):
        try:
            return vars(self.ns[MACROS])[head]
        except KeyError:
            pass

    @contextmanager
    def macro_context(self):
        """Sets `NS` during macroexpansions."""
        token = NS.set(self.ns)
        try:
            yield
        finally:
            NS.reset(token)

    @_trace
    def call(self, form: Iterable) -> str:
        R"""
        Compile call form.

        Any tuple that is not quoted, ``()``, or a `special` form or
        `macro` is a run-time call.

        Like Python, it has three parts:
        (<callable> <args> : <kwargs>).
        For example:

        >>> print(readerless(
        ... ('print',1,2,3,
        ...          ':','sep',('quote',":",), 'end',('quote',"\n\n",),)
        ... ))
        print(
          (1),
          (2),
          (3),
          sep=':',
          end='\n\n')

        Either <args> or <kwargs> may be empty:

        >>> readerless(('foo',':',),)
        'foo()'
        >>> print(readerless(('foo','bar',':',),))
        foo(
          bar)
        >>> print(readerless(('foo',':','bar','baz',),))
        foo(
          bar=baz)

        The ``:`` is optional if the <kwargs> part is empty:

        >>> readerless(('foo',),)
        'foo()'
        >>> print(readerless(('foo','bar',),),)
        foo(
          bar)

        The <kwargs> part has implicit pairs; there must be an even number.

        Use the control words ``:*`` and ``:**`` for iterable and
        mapping unpacking:

        >>> print(readerless(
        ... ('print',':',':*',[1,2], 'a',3, ':*',[4], ':**',{'sep':':','end':'\n\n'},),
        ... ))
        print(
          *[1, 2],
          a=(3),
          *[4],
          **{'sep': ':', 'end': '\n\n'})

        Unlike other control words, these can be repeated,
        but (as in Python) a '*' is not allowed to follow '**'.

        Method calls are similar to function calls:
        (.<method name> <object> <args> : <kwargs>)
        Like Clojure, a method on the first object is assumed if the
        function name starts with a dot:

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
            starmap(self._pair_arg, _pairs(form)),
        )
        if type(head) is str and head.startswith("."):
            return "{}.{}({})".format(next(args), head[1:], _join_args(*args))
        return "{}({})".format(self.form(head), _join_args(*args))

    def _pair_arg(self, k, v):
        k = PAIR_WORDS.get(k, k + "=")
        if ".." in k:
            k = k.split(".")[-1]
        return k + self.form(v).replace("\n", "\n" + " " * len(k))

    @_trace
    def str(self, code: str) -> str:
        """Compile code strings.
        Expands qualified identifiers and module literals into imports.
        Otherwise, injects as raw Python directly into the output.
        """
        if not all(s.isidentifier() for s in code.split(".") if s):
            return code
        if ".." in code:
            return self.qualified_identifier(code)
        elif code.endswith("."):
            return self.module_identifier(code)
        return code

    def qualified_identifier(self, code):
        """Compile qualified identifier into import and attribute."""
        parts = code.split("..", 1)
        if parts[0] == self.qualname:  # This module. No import required.
            chain = parts[1].split(".", 1)
            # Avoid local shadowing.
            chain[0] = f"__import__('builtins').globals()[{self.atom(chain[0])}]"
            return ".".join(chain)
        return "__import__({0!r}{fromlist}).{1}".format(
            parts[0], parts[1], fromlist=",fromlist='?'" if "." in parts[0] else ""
        )

    def module_identifier(self, code):
        """Compile module identifier to import."""
        module = code[:-1]
        return f"""__import__({module !r}{",fromlist='?'" if "." in module else ""})"""

    @_trace
    def atom(self, form) -> str:
        R"""
        Compile forms that evaluate to themselves.

        Emits a literal if possible, otherwise falls back to `pickle`:

        >>> readerless(-4.2j)
        '((-0-4.2j))'
        >>> print(readerless(float('nan')))
        __import__('pickle').loads(  # nan
            b'Fnan\n.'
        )
        >>> readerless([{'foo':2},(),1j,2.0,{3}])
        "[{'foo': 2}, (), 1j, 2.0, {3}]"
        >>> spam = []
        >>> spam.append(spam)  # ref cycle can't be a literal
        >>> print(readerless(spam))
        __import__('pickle').loads(  # [[...]]
            b'(lp0\ng0\na.'
        )
        >>> spam = [[]] * 3  # duplicated refs
        >>> print(readerless(spam))
        __import__('pickle').loads(  # [[], [], []]
            b'(l(lp0\nag0\nag0\na.'
        )

        """
        if form is Ellipsis:
            return "..."
        case = type(form)
        if case is tuple and form:
            return self._lisp_normal_form(form)
        if case in {dict, list, set}:
            return self._collection(form)
        literal = self._format_repr(case, form)
        if self._try_eval(literal) == form:
            return literal
        # literal failed to round trip. Fall back to pickle.
        return self.pickle(form)

    def _lisp_normal_form(self, form):
        return "({},)".format(",\n".join(map(self.atom, form)).replace("\n", "\n "))

    def _collection(self, form):  # Use literal if it reproduces the object graph.
        pickled = self.pickle(form)
        pretty = pformat(form, sort_dicts=False)
        evaled = self._try_eval(pretty)
        if evaled == form and pickled == self.pickle(evaled):
            return pretty
        return pickled

    @staticmethod
    def _format_repr(case, form):
        if case in {int, float, complex}:
            return f"({form!r})"  # Number literals may need (). E.g. (1).real
        return pformat(form)  # Pretty print for multiline strings.

    @staticmethod
    def _try_eval(literal):
        with suppress(ValueError, SyntaxError):
            return ast.literal_eval(literal)

    @_trace
    def pickle(self, form) -> str:
        """Compile to `pickle.loads`. The final fallback for `atom`."""
        # 0 is the "human-readable" backwards-compatible text protocol.
        dumps = pickletools.optimize(pickle.dumps(form, 0, fix_imports=False))
        r = repr(form).replace("\n", "\n  # ")
        nl = "\n" if "\n" in r else ""
        return f"__import__('pickle').loads({nl}  # {r}\n    {dumps!r}\n)"

    def eval(self, form: str) -> Tuple[str, ...]:
        """Execute compiled form, but only if evaluate mode is enabled."""
        try:
            if self.evaluate:
                exec(compile(form, "<Hissp>", "exec"), self.ns)
        except Exception as e:
            exc = format_exc()
            if self.ns.get("__name__") == "__main__":
                self.abort = True
            else:
                warn(
                    f"\n {e} when evaluating form:\n{form}\n\n{exc}", PostCompileWarning
                )
            return form, "# " + exc.replace("\n", "\n# ")
        return (form,)


def _join_args(*args):
    return (("\n" if args else "") + ",\n".join(args)).replace("\n", "\n  ")


T = TypeVar("T")


def _pairs(it: Iterable[T]) -> Iterable[Tuple[T, T]]:
    it = iter(it)
    for k in it:
        try:
            yield k, next(it)
        except StopIteration:
            raise CompileError("Incomplete pair.") from None


def readerless(form, ns=None):
    """Compile a Hissp form to Python without evaluating it.
    Uses the current `NS` for context, unless an alternative is provided.
    (Creates a temporary namespace if neither is available.)
    Returns the Python in a string.
    """
    ns = ns or NS.get() or {"__name__": "__main__"}
    return Compiler(evaluate=False, ns=ns).compile([form])
