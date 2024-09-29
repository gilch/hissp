# Copyright 2019, 2020, 2021, 2022, 2023, 2024 Matthew Egan Odendahl
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
from collections.abc import Iterable
from contextlib import contextmanager, suppress
from contextvars import ContextVar
from functools import wraps
from itertools import chain, starmap, takewhile
from pprint import pformat
from traceback import format_exc
from types import MappingProxyType, ModuleType
from typing import Any, NewType, TypeVar
from warnings import warn

PAIR_WORDS = {":*": "*", ":**": "**", ":?": ""}
# Module Macro container
MACROS = "_macro_"
# Macro from foreign module foo.bar.._macro_.baz
MACRO = f"..{MACROS}."
MAYBE = "..QzMaybe_."
RE_MACRO = re.compile(rf"({re.escape(MACRO)}|{re.escape(MAYBE)})")
_PARAM_INDENT = f"\n{len('(lambda ')*' '}"

ENV: ContextVar[MappingProxyType | None] = ContextVar("ENV", default=None)
"""
Expansion environment.
 
Sometimes a macro needs the current environment when expanding,
instead of its defining environment.
Rather than pass in an implicit argument to all macros,
it's available here.
`readerless` and `macroexpand` use this automatically.
"""

MAX_PROTOCOL = pickle.HIGHEST_PROTOCOL
"""
Compiler pickle protocol limit.

When there is no known literal syntax for an `atom`,
the compiler emits a `pickle.loads` expression as a fallback.
This is the highest pickle protocol it's allowed to use.
The compiler may use Protocol 0 instead when it has a shorter `repr`,
due to the inefficient escapes required for non-printing bytes.

A lower number may be necessary if the compiled output is expected to
run on an earlier Python version than the compiler.
"""


@contextmanager
def macro_context(env: dict[str, Any] | None):
    """Sets `ENV` during macroexpansions.

    Does nothing if ``env`` is ``None`` or already the current context.
    """
    if env is None or ENV.get() is env:
        yield
    else:
        token = ENV.set(MappingProxyType(env))
        try:
            yield
        finally:
            ENV.reset(token)


Sentinel = NewType("Sentinel", object)
_SENTINEL = Sentinel(object())


class CompileError(SyntaxError):
    """Catch-all exception for compilation failures."""


def _trace(method):
    @wraps(method)
    def tracer(self, expr) -> str:
        try:
            return method(self, expr)
        except Exception as e:
            self.error = e
            message = (
                "\nCompiler.{}() {}:\n {}".format(
                    method.__name__,
                    type(e).__name__,
                    format_exc() if method.__name__ == "macro" else e,
                ).replace("\n", "\n# ")
                + "\n"
            )
            return f"(>   >  > >>{pformat(expr)}<< <  <   <){message}"

    return tracer


class PostCompileWarning(Warning):
    """Form compiled to Python, but its execution failed.

    Only possible when compiling in evaluate mode and not in ``__main__``.
    Would be a "Hissp Abort!" instead when in ``__main__``, but other
    modules can be allowed to continue compiling for debugging purposes.

    Continuing execution after a failure can be dangerous if non-main
    modules have side effects besides definitions. Warnings can be
    upgraded to errors if this is a concern. See `warnings` for how.
    """


class Compiler:
    """
    The Hissp recursive-descent compiler.

    Translates the Hissp data-structure language into a functional
    subset of Python.
    """

    def __init__(
        self, qualname="__main__", env: dict[str, Any] | None = None, evaluate=True
    ):
        self.qualname = qualname
        self.env = self.new_env(qualname) if env is None else env
        self.evaluate = evaluate
        self.error = False
        self.abort = None

    @staticmethod
    def new_env(name, doc=None, package=None) -> dict[str, Any]:
        """Imports the named module, creating it if necessary.

        Returns the module's ``__dict__``.
        """
        mod = ModuleType(name, doc)
        mod.__annotations__ = {}
        mod.__package__ = package
        mod.__builtins__ = builtins
        if name != "__main__":
            mod = sys.modules.setdefault(name, mod)
        return vars(mod)

    def compile(self, forms: Iterable) -> str:
        """
        Compile multiple forms, and execute them if evaluate mode enabled.
        """
        result: list[str] = []
        for i, form in enumerate(forms, 1):
            form = self.compile_form(form)
            if self.error:
                e = self.error
                self.error = False
                raise CompileError("\n" + form) from e
            result.extend(self.eval(form, i))
            if self.abort:
                print("Hissp abort!", self.abort, sep="\n", file=sys.stderr)
                self.abort = None  # To allow REPL debugging.
                sys.exit(1)
        return "\n\n".join(result)

    @_trace
    def compile_form(self, form) -> str:
        """
        Compile Hissp `form` to the equivalent Python code in a string.
        `tuple` and `str` have special evaluation rules,
        otherwise it's an `atom` that represents itself.
        """
        if type(form) is tuple and form:
            return self.tuple_(form)
        if type(form) is str and not form.startswith(":"):
            return self.fragment(form)
        return self.atomic(form)

    @_trace
    def tuple_(self, form: tuple) -> str:
        """Compile `call`, `macro`, or `special` forms."""
        head, *tail = form
        if (
            not tail
            and type(head) is tuple
            and head[0] == "lambda"
            and not self.parameters(head[1])
        ):  # progn optimization
            return self.body(head[2:])
        elif type(head) is str:
            return self.special(form)
        return self.call(form)

    @_trace
    def special(self, form: tuple) -> str:
        """Try to compile as a `special form`, else :meth:`invocation`.

        The two special forms are ``quote`` and `lambda <lambda_>`.

        A quote form evaluates to its argument, treated as literal data,
        not evaluated. Notice the difference in the `readerless`
        compiled output:

        >>> print(readerless(('print',42,)))  # function call
        print(
          (42))
        >>> print(readerless(('quote',('print',42,),)))  # tuple
        ('print',
         (42),)

        """
        if form[0] == "quote":
            return self.atomic(*form[1:])
        if form[0] == "lambda":
            return self.lambda_(form)
        return self.invocation(form)

    @_trace
    def lambda_(self, form: tuple) -> str:
        R"""
        Compile the anonymous function `special form`.

        (lambda (<parameters>)
          <body>)

        The ``parameters tuple`` is divided into (<singles> : <pairs>)

        Parameter types are the same as Python's.
        For example,

        >>> print(readerless(
        ... ('lambda', ('a',':/','b'
        ...            ,':', 'e',1, 'f',2
        ...            ,':*','args', 'h',4, 'i',':?', 'j',1
        ...            ,':**','kwargs',)
        ...  ,42,)
        ... ))
        (
         lambda a,
                /,
                b,
                e=(1),
                f=(2),
                *args,
                h=(4),
                i,
                j=(1),
                **kwargs:
            (42))


        The special `control word`\ s ``:*`` and ``:**`` designate the
        remainder of the positional and keyword parameters, respectively.

        Note this body evaluates expressions in sequence, for side
        effects:

        >>> print(readerless(
        ... ('lambda', (':',':*','args',':**','kwargs',)
        ...  ,('print','args',)
        ...  ,('print','kwargs',),)
        ... ))
        (lambda *args, **kwargs:
           (print(
              args),
            print(
              kwargs))  [-1]
        )

        You can omit the right of a pair with ``:?``
        (except the final ``**kwargs``).
        Also note that the body can be empty.

        >>> print(readerless(
        ... ('lambda', (':','a',1, ':/',':?', ':*',':?', 'b',':?', 'c',2,),),
        ... ))
        (
         lambda a=(1),
                /,
                *,
                b,
                c=(2):
            ())

        The ``:`` may be omitted if there are no paired parameters.

        >>> print(readerless(('lambda', ('a','b','c',':',),),))
        (lambda a, b, c: ())
        >>> print(readerless(('lambda', ('a','b','c',),),))
        (lambda a, b, c: ())
        >>> readerless(('lambda', (':',),),)
        '(lambda : ())'
        >>> readerless(('lambda', (),),)
        '(lambda : ())'

        The ``:`` is required if there are any pair parameters, even
        if there are no single parameters:

        >>> readerless(('lambda', (':',':**','kwargs',),),)
        '(lambda **kwargs: ())'

        """
        fn, parameters, *body = form
        assert fn == "lambda"
        sep = (len(body) <= 1) * " "
        parameters, body = self.parameters(parameters), self.body(body)
        param_has_nl, body_has_nl = "\n" in parameters, "\n" in body
        begin, end = param_has_nl * "\n ", body_has_nl * "\n"
        middle = (body_has_nl or param_has_nl) * f"\n{3*' '}"
        body = body.replace("\n", f"\n{3*' '}{sep}")
        return f"({begin}lambda {parameters}:{middle}{sep}{body}{end})"

    @_trace
    def parameters(self, parameters: Iterable) -> str:
        """Process `params` to compile `lambda_`."""
        parameters = iter(parameters)
        r = [
            {":/": "/", ":*": "*"}.get(a, a)
            for a in takewhile(lambda a: a != ":", parameters)
        ]
        sep = ", "
        for k, v in _pairs(parameters):
            if k == ":*":
                r.append("*" if v == ":?" else f"*{v}")
            elif k == ":/":
                r.append("/")
            elif k == ":**":
                r.append(f"**{v}")
            elif v == ":?":
                r.append(k)
            else:
                r.append(f"{k}={self.compile_form(v)}")
                sep = ",\n"
        return sep.join(r).replace("\n", _PARAM_INDENT)

    @_trace
    def body(self, body: list) -> str:
        """Compile body of `lambda_`."""
        body = tuple(map(self.compile_form, body))
        if len(body) > 1:
            result = ",\n".join(body).replace("\n", "\n ")
            return f"({result})  [-1]"
        return f"{body and body[0]}"

    @_trace
    def invocation(self, form: tuple) -> str:
        """Try to compile as `macro`, else normal `call`."""
        if (res := self.expand_macro(form)) is not _SENTINEL:
            if res.startswith("#") and res.lstrip("#").startswith(f" {form[0]}\n"):
                return f"#{res}"  # Abbreviate direct recursion.
            return f"# {form[0]}\n{res}"
        form = form[0].replace(MAYBE, "..", 1), *form[1:]
        return self.call(form)

    @_trace
    def expand_macro(self, form: tuple) -> str | Sentinel:
        """Macroexpand and start over with `compile_form`, if macro."""
        head, *tail = form
        if (macro := self._get_macro(head, self.env)) is not None:
            with macro_context(self.env):
                return self.compile_form(macro(*tail))
        return _SENTINEL

    @classmethod
    def get_macro(cls, symbol, env: dict[str, Any]):
        """Returns the macro function for ``symbol`` given the ``env``.

        Returns ``None`` if ``symbol`` isn't a macro identifier.
        """
        if type(symbol) is not str or symbol.startswith(":"):
            return None
        return cls._get_macro(symbol, env)

    @classmethod
    def _get_macro(cls, head, env: dict[str, Any]):
        parts = RE_MACRO.split(head, 1)
        head = head.replace(MAYBE, MACRO, 1)
        if len(parts) > 1:
            return cls._qualified_macro(env, head, parts)
        return cls._unqualified_macro(env, head)

    @classmethod
    def _qualified_macro(cls, env: dict[str, Any], head, parts):
        try:
            qualname = env.get("__name__", "__main__")
            if parts[0] == qualname:  # Internal?
                return getattr(env[MACROS], parts[2])
            return eval(cls._fragment(qualname, head))
        except (LookupError, AttributeError):
            if parts[1] != MAYBE:
                raise

    @staticmethod
    def _unqualified_macro(env: dict[str, Any], head):
        try:
            return getattr(env[MACROS], head)
        except (LookupError, AttributeError):
            pass

    @_trace
    def call(self, form: Iterable) -> str:
        R"""
        Compile call form.

        Any tuple that is not quoted, ``()``, or a `special` form or
        `macro` is a run-time call form.
        It has three parts:

        (<callable> <singles> : <pairs>).

        Each argument pairs with a keyword or `control word` target.
        The ``:?`` target passes positionally (implied for singles).

        For example:

        >>> print(readerless(
        ... ('print',1,2,3
        ...         ,':','sep',('quote',":",), 'end',('quote',"\n\n",),)
        ... ))
        print(
          (1),
          (2),
          (3),
          sep=':',
          end='\n\n')

        Either <singles> or <pairs> may be empty:

        >>> readerless(('foo',':',),)
        'foo()'
        >>> print(readerless(('foo','bar',':',),))
        foo(
          bar)
        >>> print(readerless(('foo',':','bar','baz',),))
        foo(
          bar=baz)

        The ``:`` is optional if the <pairs> part is empty:

        >>> readerless(('foo',),)
        'foo()'
        >>> print(readerless(('foo','bar',),),)
        foo(
          bar)

        Use the ``:*`` and ``:**`` targets for position and
        keyword unpacking, respectively:

        >>> print(readerless(
        ... ('print',':',':*',[1,2], 'a',3, ':*',[4], ':**',{'sep':':','end':'\n\n'},),
        ... ))
        print(
          *[1, 2],
          a=(3),
          *[4],
          **{'sep': ':', 'end': '\n\n'})

        Method calls are similar to function calls:

        (.<method name> <self> <args> : <kwargs>).

        A method on the first (self) argument is assumed if the function
        name starts with a dot:

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
            (singles := [*map(self.compile_form, takewhile(lambda a: a != ":", form))]),
            starmap(self._pair_arg, pairs := [*_pairs(form)]),
        )
        if type(head) is str and head.startswith("."):
            if singles or pairs[0][0] == ":?":
                return "{}.{}({})".format(next(args), head[1:], _join_args(*args))
            raise CompileError("self must be paired with :?")
        return "{}({})".format(self.compile_form(head), _join_args(*args))

    def _pair_arg(self, k, v):
        k = PAIR_WORDS.get(k, k + "=")
        if ".." in k:
            k = k.split(".")[-1]
        return k + self.compile_form(v).replace("\n", "\n" + " " * len(k))

    @_trace
    def fragment(self, code: str) -> str:
        """Compile a `fragment atom`.
        This preprocessing step converts a `fully-qualified identifier`
        or `module handle` into an import. No further compilation is
        necessary. The contents are assumed to be Python code already.
        """
        return self._fragment(self.qualname, code)

    @classmethod
    def _fragment(cls, qualname, code):
        if "..." in code:
            return code
        if not all(s.isidentifier() for s in code.split(".") if s):
            return code
        if ".." in code:
            return cls.qualified_identifier(qualname, code)
        elif code.endswith("."):
            return cls.module_identifier(code)
        return code

    @staticmethod
    def qualified_identifier(qualname, code):
        """Compile `fully-qualified identifier` into import and attribute."""
        parts = code.split("..", 1)
        if parts[0] == qualname:  # This module. No import required.
            chain = parts[1].split(".", 1)
            # Avoid local shadowing.
            chain[0] = f"__import__('builtins').globals()[{pformat(chain[0])}]"
            return ".".join(chain)
        return "__import__({0!r}{fromlist}).{1}".format(
            parts[0], parts[1], fromlist=",fromlist='*'" if "." in parts[0] else ""
        )

    @staticmethod
    def module_identifier(code: str) -> str:
        """Compile a `module handle` to an import."""
        assert code[-1] == "."
        module = code[:-1]
        return f"""__import__({module !r}{",fromlist='*'" if "." in module else ""})"""

    @_trace
    def atomic(self, form) -> str:
        R"""
        Compile forms that evaluate to themselves.

        Returns a literal if possible, otherwise falls back to `pickle`:

        >>> readerless(-4.2j)
        '((-0-4.2j))'
        >>> print(readerless(float('nan')))
        # nan
        __import__('pickle').loads(b'Fnan\n.')
        >>> readerless([{'foo':2},(),1j,2.0,{3}])
        "[{'foo': 2}, (), 1j, 2.0, {3}]"
        >>> spam = []
        >>> spam.append(spam)  # ref cycle can't be a literal
        >>> print(readerless(spam))
        # [[...]]
        __import__('pickle').loads(b'(lp0\ng0\na.')
        >>> spam = [[]] * 3  # duplicated refs
        >>> print(readerless(spam))
        # [[], [], []]
        __import__('pickle').loads(b'(l(lp0\nag0\nag0\na.')

        """
        if form is Ellipsis:
            return "..."  # "Ellipsis" could be shadowed.
        case = type(form)
        if case is set and not form:
            return "{*''}"  # "set()" could be shadowed. "{}" is a dict.
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
        return "({},)".format(",\n".join(map(self.atomic, form)).replace("\n", "\n "))

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
        """Compile to `pickle.loads`. The final fallback for `atomic`."""
        protocols = 0, MAX_PROTOCOL
        pickles = [repr(pickletools.optimize(pickle.dumps(form, p))) for p in protocols]
        code = min(pickles, key=len)
        r = repr(form).replace("\n", "\n  # ")
        return f"# {r}\n__import__({pickle.__name__!r}).loads({code})"

    @staticmethod
    def linenos(code: str):
        """Adds line numbers to code for error messages."""
        lines = code.split("\n")
        digits = len(str(len(lines)))
        return "\n".join(f"{i:0{digits}} {line}" for i, line in enumerate(lines, 1))

    def eval(self, code: str, form_number: int) -> tuple[str, ...]:
        """Execute compiled code, but only if evaluate mode is enabled."""
        try:
            if self.evaluate:
                filename = (
                    f"<Compiled Hissp #{form_number} of {self.qualname}:\n"
                    f"{self.linenos(code)}\n"
                    f">"
                )
                exec(compile(code, filename, "exec"), self.env)
        except Exception as e:
            exc = format_exc()
            if self.env.get("__name__") == "__main__":
                self.abort = exc
            else:
                warn(
                    f"\n {e} when evaluating form:\n{code}\n\n{exc}", PostCompileWarning
                )
            return code, "# " + exc.replace("\n", "\n# ")
        return (code,)


def _join_args(*args):
    return (("\n" if args else "") + ",\n".join(args)).replace("\n", "\n  ")


T = TypeVar("T")


def _pairs(it: Iterable[T]) -> Iterable[tuple[T, T]]:
    it = iter(it)
    for k in it:
        try:
            yield k, next(it)
        except StopIteration:
            raise CompileError("Incomplete pair.") from None


def readerless(form, env: dict[str, Any] | None = None):
    """Compile a Hissp form to Python without evaluating it.
    Uses the current `ENV` for context, unless an alternative is provided.
    (Creates a temporary environment if neither is available.)
    Returns the Python in a string.
    """
    if env is None and (env := ENV.get()) is None:
        env = {"__name__": "__main__"}
    return Compiler(env=env, evaluate=False).compile([form])


def macroexpand1(form, env: dict[str, Any] | None = None):
    """Macroexpand outermost form once.

    If form is not a macro form, returns it unaltered.
    Uses the current `ENV` (available in a `macro_context`), unless
    an alternative mapping (such as ``globals()``) is provided.
    """
    if type(form) is not tuple or not form or form[0] in ["quote", "lambda"]:
        return form
    head, *tail = form
    env = ENV.get() if env is None else env
    if env is None:
        raise TypeError("outside of macro context, env argument required")
    if (macro := Compiler.get_macro(form[0], env)) is None:
        return form
    with macro_context(env):
        return macro(*tail)


def is_atomic(form) -> bool:
    """Determines if form is an `atom`."""
    return type(form) is not tuple or form == ()


def is_symbol(form) -> bool:
    """Determines if form is a `symbol`."""
    return (type(form) is str and form != "") and all(
        part.isidentifier() for part in f"{form}_".replace("..", ".", 1).split(".")
    )


def is_control(form) -> bool:
    """Determines if form is a `control word`."""
    return type(form) is str and form.startswith(":")


def macroexpand(form, env: dict[str, Any] | None = None):
    """Repeatedly macroexpand outermost form until not a macro form.

    If form is not a macro form, returns it unaltered.
    Uses the current `ENV` for context, unless an alternative is provided.
    """
    while True:
        expanded = macroexpand1(form, env)
        if expanded is form:
            return form
        form = expanded


def macroexpand_all(
    form,
    env: dict[str, Any] | None = None,
    *,
    preprocess=lambda x: x,
    postprocess=lambda x: x,
):
    """Recursively macroexpand everything possible from the outside-in.

    Pipes outer form through preprocess, :func:`macroexpand`, and postprocess,
    then recurs into subforms of the resulting expansion, if applicable.

    Pre/postprocess are called with `macro_context` so, e.g.,
    `macroexpand1` may be called by preprocess to handle intermediate
    expansions.

    If expansion is not a `macro form`, returns it.
    As in the compiler, lambda parameter names are not considered
    expandable subforms, but default expressions are.
    Uses the current `ENV` for context, unless an alternative is provided.
    """
    with macro_context(env):
        exp = postprocess(macroexpand(preprocess(form)))
    if type(exp) is not tuple or not exp or exp[0] == "quote":
        return exp
    if exp[0] != "lambda":
        return tuple(
            macroexpand_all(e, env, preprocess=preprocess, postprocess=postprocess)
            for e in exp
        )
    return "lambda", _pexpand(exp[1], env), *(macroexpand_all(e, env) for e in exp[2:])


def _pexpand(params, env: dict[str, Any] | None) -> tuple:
    if ":" not in params:
        return params
    singles, pairs = parse_params(params)
    stars = {":*", ":**"}
    if not pairs.keys() - stars:
        return params
    pairs = {k: v if k in stars else macroexpand_all(v, env) for k, v in pairs.items()}
    return *singles, ":", *chain.from_iterable(pairs.items())


def parse_params(params) -> tuple[tuple, dict[str, Any]]:
    """Parses a lambda form's `params` into a tuple of singles and a dict of pairs."""
    iparams = iter(params)
    singles = tuple(takewhile(lambda x: x != ":", iparams))
    pairs = dict(zip(iparams, iparams, strict=True))
    return singles, pairs
