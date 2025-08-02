.. Copyright 2020, 2021, 2022, 2023, 2024 Matthew Egan Odendahl
   SPDX-License-Identifier: CC-BY-SA-4.0

.. All Source Code Examples in this file are licensed "Apache-2.0 OR CC-BY-SA-4.0"
   and may be copied under the terms of either, Your choice.
   (Source Code Examples are designated with the ".. code-block::" or ".. Lissp::"
   reStructuredText markup.) The remainder of this file is licensed under
   CC-BY-SA-4.0 only.

Macro Tutorial
##############

.. TODO: be sure to demonstrate hissp.compiler..ENV and hissp.compiler..readerless somewhere

Lisp is a higher-level language than Python,
in the same sense that Python is a higher-level language than C,
and C is a higher-level language than assembly.

In C, abstractions like for-loops and the function call stack are
*primitives*—features built into the language.
But in assembly,
those are *design patterns*
built with lower-level primitives like jump instructions
that have to be repeated each time they're needed.
Things like call stacks had to be discovered and developed and learned as best practice
in the more primitive assembly languages.
Before the development of the structured programming paradigm,
the industry standard was GOTO spaghetti.

Similarly, in Python, abstractions like iterators, classes, higher-order functions, hash tables,
and garbage collection are *primitive*,
but in C, those are *design patterns*,
discovered and developed over time as best practice,
and built with lower-level parts like arrays, structs, and pointers,
which have to be repeated each time they're needed.

To someone who started out in assembly or BASIC, or C, or even Java,
Python seems marvelously high-level, once mastered.
Python makes everything that was so tedious before |seem *so easy*|__

.. |seem *so easy*| replace:: seem *so easy*.
__ https://xkcd.com/353/

But the advanced Python developer eventually starts to notice the cracks.
You can get a lot further in Python, but like the old GOTO spaghetti code,
large enough projects start to collapse under their own weight.
Python seemed so easy before,
but some patterns can't be abstracted away.
You're stuck with a certain amount of boilerplate and ceremony.
Just to take off some of the load,
you lean on tooling you barely understand and can't easily customize or modify
*enough*,
straitjacketing yourself into less-capable subsets of the language
that keep your IDE happy, but bloat the codebase.

There is a better way.

Programmers comfortable with C,
but unfamiliar with Python,
will tend to write C idioms in Python,
like using explicit indexes into lists in for-loops over a `range`,
instead of using the list's iterator directly.
Their code is said to be *unpythonic*.
They forgo much of Python's power,
because they don't know the right idioms.

"Design patterns" and "idioms" in low-level languages
are language-level built-in features of higher-level ones.
Lisp is even higher-level than that.
In Lisp, you don't have "design patterns" for long,
because they are a thing you can abstract to avoid repeating.
You can create your own *language-level* features,
because macros give you hooks into the compiler itself.

Lisp can do things you might not have realized were possible.
Until you understand what Lisp can do,
you're forgoing much of its power.
This is a tutorial,
not a reference,
and I'll be explaining not just how to write macros,
but why you need them.

####

If you're new to Lisp,
go back and read the `style guide <style_guide>` if you haven't already.
Understanding how Lisp is *formatted* helps you to read it,
not just write it.
And you will need to read it.
Learning to read a new programming language can be difficult,
because you're using up working memory that would otherwise
be helping with the meaning of the code on the syntax itself.
This does get better with familiarity,
because you can offload that part to your long-term memory.
That also means that reading code in an unfamiliar language is more
difficult the more different the new language is
from those you already know.

Fortunately, Lissp's syntax is very minimal,
so there's not that much to remember,
and most of the vocabulary you know from Python already.
You can skim over the Python in this tutorial,
but resist the urge to skim the Lissp.
`S-expressions <https://en.wikipedia.org/wiki/S-expression>`_
are a very direct representation of the same kind of syntax trees that
you mentally generate when reading any other high-level programming language.
Take your time and comprehend each subexpression instead of taking it in all at once.

The `primer` was mostly about learning how to program with
a subset of Python in a new skin.
This one is about using that knowledge to reprogram the skin itself.

If you don't know the basics from the Primer,
go back and read that now, or at least read the `lissp_whirlwind_tour`.

In the Primer we mostly used the :term:`REPL`,
but it can become tedious to type in long forms,
and it doesn't save your work.
S-expressions are awkward to edit without editor support for them,
and the included `LisspREPL` is layered on Python's `code.InteractiveConsole`,
which has only basic line editing support.

The usual workflow when developing Lissp is to create a ``.lissp``
file and work in there.
Then you can save as you go
and send fragments of it to the REPL for evaluation and experimentation.
You might already develop Python this way.
A good editor can be configured to send selected text to the REPL
with a simple keyboard command,
but copy-and-paste into a terminal window will do.

Setting up your editor for Lissp is beyond the scope of this tutorial.
If you're not already comfortable with Emacs and Paredit,
give `Parinfer <https://shaunlebron.github.io/parinfer/>`_ a try.

Shorter Lambdas
===============

The defect rate in computer programs seems to be a near-constant fraction
of the number of kilobytes of source code.
For reasonable line length,
it doesn't seem to matter how much those lines are doing,
or what language it's written in.
Code is a *liability*.
It's that much more space for bugs to hide
— that much more you have to read to understand the system.
The less code you have, the better,
as long as it still gets the job done.

Perhaps this can be taken too far.
Code golf is good exercise, not good practice.
Eventually, there are diminishing returns,
and other costs to consider.
But as a rule of thumb,
one of the best things you can do to improve a codebase is to make it *shorter*,
`almost any way you can <https://blog.codinghorror.com/the-best-code-is-no-code-at-all/>`_.
Fewer slightly less-readable lines are much more readable
than too many slightly more-readable lines.

Consider Python's humble ``lambda``.
It's important to programming in the functional style,
and central to the way Hissp works,
as a compilation target for one of its two special forms.
It's actually really powerful.

But the overhead of typing out a six-letter word might make you a little
too reluctant to use it,
unlike in Smalltalk where it's just square brackets,
and it's used all the time in control flow methods.

Wouldn't it be nice if we could give ``lambda`` a shorter name?

.. code-block:: Python

   L = lambda

Could we then use ``L`` in place of ``lambda``?
Maybe like this?

.. code-block:: Python

   squares = map(L x: x * x, range(10))

Alas, this doesn't work.
The ``L = lambda`` is a syntax error.

To be fair to Python, I'd use a generator expression here,
which is the same length:

.. code-block:: Python

   squares = map(L x: x * x, range(10))
   squares = (x * x for x in range(10))

But I need a simple example,
and lambdas are a lot more general:

.. code-block:: Python

   product = reduce(L a, x: a * x, range(1, 7))

A genexpr doesn't really help us in a `reduce <functools.reduce>`.

They say that in Python everything is an object.
But it's not quite true, is it?
``lambda`` isn't an object in Python.
It's a reserved word, but at run time, that's not an object.
It's not anything.
If you're rolling your eyes and thinking,
"Why would I even expect this to work?"
then you're still thinking inside the Python box.

You can store class and function objects in variables
and pass them as arguments to functions in Python.
To someone who came from a language without higher-order functions,
this feels like breaking the rules.
Using it effectively feels like amazing out-of-the-box thinking.

Let's begin.

Warm-Up
:::::::

Create a Lissp file (perhaps ``tutorial.lissp``),
and open it in your Lisp editor of choice.

Fire up the Lissp REPL in a terminal,
or in your editor if it does that,
in the same directory as your Lissp file.

Add the `prelude<hissp.prelude>` shorthand to the top of the file:

.. code-block:: Lissp

   hissp..prelude#:

And push it to the REPL as well:

.. code-block:: REPL

   #> hissp..prelude#:
   >>> # hissp.macros.._macro_.prelude
   ... __import__('builtins').exec(
   ...   ('from itertools import *;from operator import *\n'
   ...    'def engarde(xs,h,f,/,*a,**kw):\n'
   ...    ' try:return f(*a,**kw)\n'
   ...    ' except xs as e:return h(e)\n'
   ...    'def enter(c,f,/,*a):\n'
   ...    ' with c as C:return f(*a,C)\n'
   ...    "class Ensue(__import__('collections.abc').abc.Generator):\n"
   ...    ' send=lambda s,v:s.g.send(v);throw=lambda s,*x:s.g.throw(*x);F=0;X=();Y=[]\n'
   ...    ' def __init__(s,p):s.p,s.g,s.n=p,s._(s),s.Y\n'
   ...    ' def _(s,k,v=None):\n'
   ...    "  while isinstance(s:=k,__class__) and not setattr(s,'sent',v):\n"
   ...    '   try:k,y=s.p(s),s.Y;v=(yield from y)if s.F or y is s.n else(yield y)\n'
   ...    '   except s.X as e:v=e\n'
   ...    '  return k\n'
   ...    "_macro_=__import__('types').SimpleNamespace()\n"
   ...    "try: vars(_macro_).update(vars(__import__('hissp')._macro_))\n"
   ...    'except ModuleNotFoundError: pass'))

.. caution::

   The ``:`` directs it to dump into the module's global namespace.
   The `prelude<hissp.macros._macro_.prelude>`
   macro overwrites your ``_macro_`` namespace (if any) with a copy of the bundled one.
   Any references you've defined in there will be lost.
   In Lissp files, the prelude is meant to be used before any definitions,
   when it is used at all.
   Likewise, in the REPL, enter it first, or be prepared to re-enter your definitions.
   The REPL already comes with the bundled macros loaded,
   but not the en- group or imports.

.. sidebar::

   What? You never use a Python shell in any module but ``__main__``?
   Goodness, whyever not?
   Do you also eschew ``cd`` in the shell, you masochist?
   `code.interact`. Any ``local`` you want. Try it!

Compile to Python using

.. code-block:: Lissp

   #> H##refresh 'foo

where ``'foo`` is the name of your module
(so, ``'tutorial`` if your Lissp file was named that).

Start a subREPL in the new Python module it returned:

.. code-block:: Lissp

   #> H##subrepl _

By the way, we have the `H#<HQzHASH_>` alias because of the prelude.
It's one of the bundled tags.
The above is equivalent to

.. code-block:: Lissp

   #> hissp..subrepl#_

The :term:`fully-qualified tag` will work anywhere,
but the alias only works in modules that have it in their ``_macro_`` namespace.
That's why the prelude had to use the fully-qualified version.

Confirm that `__name__` resolves to your foo
(think of it like a ``pwd`` in Bash).
If you need to, you can quit the subREPL and return to main with `EOF`.
It's just a subREPL, so this doesn't exit Python.
Any globals you defined in the module will still be there.

I'll mostly be showing the REPL from here on.
Remember, compose forms in your Lissp file first,
*then* push to the REPL,
not the other way around.
Your editor is for editing.
The REPL isn't good at that.
We'll be modifying these definitions through several iterations.

Now, let's try that shorter lambda idea in Lissp:

.. code-block:: REPL

   #> (define L lambda)
   >>> # define
   ... __import__('builtins').globals().update(
   ...   L=lambda)
   Traceback (most recent call last):
     ...
     File "<console>", line 5
       lambda)
             ^
   SyntaxError: invalid syntax

Still a syntax error.
The problem is that we tried to evaluate the ``lambda`` before the assignment.
You can use Hissp's other special form, ``quote``, to prevent evaluation.

.. code-block:: REPL

   #> (define L 'lambda)
   >>> # define
   ... __import__('builtins').globals().update(
   ...   L='lambda')

OK, but that just turned it into a string.
We could have done that much in Python:

.. code-block:: pycon

   >>> L = 'lambda'

That worked, but can we use it?

.. code-block:: pycon

   >>> squares = map(L x: x * x, range(10))
   Traceback (most recent call last):
     ...
     squares = map(L x: x * x, range(10))
                   ^^^
   SyntaxError: invalid syntax. Perhaps you forgot a comma?

Another syntax error.
No surprise.

Write the equivalent example in your Lissp file
and push it to the REPL:

.. code-block:: REPL

   #> (define squares (map (L (x)
   #..                       (mul x x))
   #..                     (range 10)))
   >>> # define
   ... __import__('builtins').globals().update(
   ...   squares=map(
   ...             L(
   ...               x(),
   ...               mul(
   ...                 x,
   ...                 x)),
   ...             range(
   ...               (10))))
   Traceback (most recent call last):
     File "<console>", line 7, in <module>
   NameError: name 'x' is not defined

Not a syntax error, but it's not working either.
Why not?
Quote the whole thing to see the Hissp code.

.. code-block:: REPL

   #> '(define squares (map (L (x)
   #..                        (mul x x))
   #..                      (range 10)))
   >>> ('define',
   ...  'squares',
   ...  ('map',
   ...   ('L',
   ...    ('x',),
   ...    ('mul',
   ...     'x',
   ...     'x',),),
   ...   ('range',
   ...    (10),),),)
   ('define', 'squares', ('map', ('L', ('x',), ('mul', 'x', 'x')), ('range', 10)))

We don't want that ``'L'`` string in the Hissp, but ``'lambda'``.
Hissp isn't compiling it like a special form.
Is that possible?

It is with one more step.
We want to dereference this at read time.
Inject:

.. code-block:: REPL

   #> (define squares (map (.#L (x)
   #..                       (mul x x))
   #..                     (range 10)))
   >>> # define
   ... __import__('builtins').globals().update(
   ...   squares=map(
   ...             (lambda x:
   ...                 mul(
   ...                   x,
   ...                   x)
   ...             ),
   ...             range(
   ...               (10))))

   #> (list squares)
   >>> list(
   ...   squares)
   [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]

Amazing.

Those of you who started with Python might be a little impressed,
but you C people are thinking,
"Yeah, that's just a macro.
We can do that much in C with the preprocessor.
I bet we could preprocess Python too somehow."
To which I'd reply,
*What do you think Lissp is?*

.. topic:: Preprocessing Python like C

   The C preprocessor actually can be used on other languages.
   Python is close enough to C to be compatible with it,
   unless you have any comment lines (although there are workarounds).

   Most flavors of Unix have one. For example, given a file ``hello.py.cp``

   .. code-block:: python

      #define L lambda
      print(*map(L x: x * x, range(10)))

   You could try something like

   .. code-block:: console

      $ cpp -P hello.py.cp -o hello.py && python3 hello.py
      0 1 4 9 16 25 36 49 64 81

   which you could also add to your build scripts.

   On Windows, you'd need a C preprocessor to be installed first.
   Any C compiler should have one.
   If you're using Microsoft's, usually you'd start a "Developer Command Prompt",
   and then the command would be something like

   .. code-block:: doscon

      > cl hello.py.cp /EP > hello.py && py hello.py

   While the C preprocessor is useful,
   it's pretty much limited to just a few flavors of find-and-replace.
   On the other hand,
   this also makes it fairly tame compared to the more powerful general-purpose preprocessors,
   like m4, which can get really confusing if you're not careful.

Lissp is a *transpiler*.
It's much more powerful than the C preprocessor,
but despite that, it is also less error prone,
because it mostly operates on the more structured Hissp, rather than text.

Since Python is supposed to be such a marvelously high-level language compared to C
that it doesn't need a preprocessor,
can't it do that too?

No, it really can't:

>>> squares = map(eval(f"{L} x: x * x"), range(10))
>>> list(squares)
[0, 1, 4, 9, 16, 25, 36, 49, 64, 81]

You can get pretty close to the same idea,
but that's about the best Python can do.
Sometimes higher-level tools cut you off from the lower level.
This shouldn't be too surprising.
More restrictions mean less to keep track of—greater predictability
and thus (theoretically) better comprehensibility.
Most of us don't miss ``GOTO`` anymore.
On the other hand, poorly chosen restrictions force us into bloated workarounds.
It's an underappreciated problem.

Compare:

.. code-block:: Python

   eval(f"{L} x: x * x")
   lambda x: x * x

It didn't help, did it?
It got *longer*.
Can we do better?

>>> e = eval

.. code-block:: Python

   e(f"{L} x:x*x")
   lambda x:x*x

Nope.
And there are good reasons to avoid `eval` in Python:
We have to compile code at run time,
and put more than we wanted to in a string,
and deal with separate namespaces. Ick.
Lissp had none of those problems.

This simple substitution metaprogramming task that was so easy in Lissp
was so awkward in Python.

But Lissp does more than substitutions.

Simple Macros
:::::::::::::

Despite my recent boasting,
our Lissp version is not actually shorter than Python's yet:

.. Lissp::

   (.#L (x)
     (mul x x))

.. code-block:: Python

   lambda x: x * x

If you like, we can give `mul <operator.mul>` a shorter name:

.. code-block:: REPL

   #> (define * mul)
   >>> # define
   ... __import__('builtins').globals().update(
   ...   QzSTAR_=mul)

And the :term:`params tuple` doesn't technically have to be a tuple:

.. Lissp::

   (.#L x (* x x))

.. code-block:: Python

   lambda x: x * x

Lissp :term:`symbol token`\ s become :term:`str atom`\ s at the Hissp level,
which are `Iterable`\ s containing character strings.
This only works because the variable name is a single character.
Now we're at the same length as Python.

Let's make it even shorter.

Given a tuple containing the *minimum* amount of information,
we want expand that into the necessary code using a macro.

Isn't there something extra here we could get rid of?
With a macro, we won't need the inject.

The :term:`template` needs to look something like
``(lambda <params> <body>)``.
Try this definition.

.. Lissp::

   #> (defmacro L (params : :* body)
   #..  `(lambda ,params ,@body))
   >>> # defmacro
   ... __import__('builtins').setattr(
   ...   __import__('builtins').globals().get(
   ...     ('_macro_')),
   ...   'L',
   ...   # hissp.macros.._macro_.fun
   ...   # hissp.macros.._macro_.let
   ...   (
   ...    lambda _Qzwin5lyqx__lambda=(lambda params, *body:
   ...               (
   ...                 'lambda',
   ...                 params,
   ...                 *body,
   ...                 )
   ...           ):
   ...      ((
   ...         *__import__('itertools').starmap(
   ...            _Qzwin5lyqx__lambda.__setattr__,
   ...            __import__('builtins').dict(
   ...              __name__='L',
   ...              __qualname__='_macro_.L',
   ...              __code__=_Qzwin5lyqx__lambda.__code__.replace(
   ...                         co_name='L')).items()),
   ...         ),
   ...       _Qzwin5lyqx__lambda)  [-1]
   ...   )())


.. code-block:: REPL

   #> (list (map (L x (* x x))
   #..           (range 10)))
   >>> list(
   ...   map(
   ...     # L
   ...     (lambda x:
   ...         QzSTAR_(
   ...           x,
   ...           x)
   ...     ),
   ...     range(
   ...       (10))))
   [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]

Success.
Now compare:

.. Lissp::

   (L x (* x x))

.. code-block:: Python

   lambda x: x * x

Are we doing better?
Barely.
If we remove the spaces that aren't required:

.. Lissp::

   (L x(* x x))

.. code-block:: Python

   lambda x:x*x

We've caught up to where Python started.
But is this really the *minimum* amount of information required?
It depends on how general you need to be,
but wouldn't this be enough?

.. code-block:: Lissp

   (L * X X)

We need to expand that into this:

.. code-block:: Lissp

   (lambda (X)
     (* X X))

So the template would look something like this::

   (lambda (X)
     (<expr>))

Remember this is basically the same as
that `anaphoric macro <anaphoric>` we did in the `primer`.

.. Lissp::

   #> (defmacro L (: :* expr)
   #..  `(lambda (,'X) ; Interpolate anaphors to prevent qualification!
   #..     ,expr))
   >>> # defmacro
   ... __import__('builtins').setattr(
   ...   __import__('builtins').globals().get(
   ...     ('_macro_')),
   ...   'L',
   ...   # hissp.macros.._macro_.fun
   ...   # hissp.macros.._macro_.let
   ...   (
   ...    lambda _Qzwin5lyqx__lambda=(lambda *expr:
   ...               (
   ...                 'lambda',
   ...                 (
   ...                   'X',
   ...                   ),
   ...                 expr,
   ...                 )
   ...           ):
   ...      ((
   ...         *__import__('itertools').starmap(
   ...            _Qzwin5lyqx__lambda.__setattr__,
   ...            __import__('builtins').dict(
   ...              __name__='L',
   ...              __qualname__='_macro_.L',
   ...              __code__=_Qzwin5lyqx__lambda.__code__.replace(
   ...                         co_name='L')).items()),
   ...         ),
   ...       _Qzwin5lyqx__lambda)  [-1]
   ...   )())


.. code-block:: REPL

   #> (list (map (L * X X) (range 10)))
   >>> list(
   ...   map(
   ...     # L
   ...     (lambda X:
   ...         QzSTAR_(
   ...           X,
   ...           X)
   ...     ),
   ...     range(
   ...       (10))))
   [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]

Now we're shorter than Python:

.. Lissp::

   (L * X X)

.. code-block:: Python

   lambda x:x*x

But we're also less general.
We can change the expression,
but we've hardcoded the parameters to it.
The fixed parameter name is fine unless it shadows a `nonlocal <nonlocal>` we need,
but what if we needed two parameters?
Could we make a macro for that?

Think about it.

\...

\...

\...

Seriously, close your eyes and think about it for at least fifteen seconds
before moving on.

Don't generalize before we have examples to work with.

I'll wait.

\...

\...

\...

\...

\...

\...

\...

\...

\...

\...

\...

\...

\...

\...

\...

Ready?

.. Lissp::

   #> (defmacro L2 (: :* expr)
   #..  `(lambda (,'X ,'Y)
   #..     ,expr))
   >>> # defmacro
   ... __import__('builtins').setattr(
   ...   __import__('builtins').globals().get(
   ...     ('_macro_')),
   ...   'L2',
   ...   # hissp.macros.._macro_.fun
   ...   # hissp.macros.._macro_.let
   ...   (
   ...    lambda _Qzwin5lyqx__lambda=(lambda *expr:
   ...               (
   ...                 'lambda',
   ...                 (
   ...                   'X',
   ...                   'Y',
   ...                   ),
   ...                 expr,
   ...                 )
   ...           ):
   ...      ((
   ...         *__import__('itertools').starmap(
   ...            _Qzwin5lyqx__lambda.__setattr__,
   ...            __import__('builtins').dict(
   ...              __name__='L2',
   ...              __qualname__='_macro_.L2',
   ...              __code__=_Qzwin5lyqx__lambda.__code__.replace(
   ...                         co_name='L2')).items()),
   ...         ),
   ...       _Qzwin5lyqx__lambda)  [-1]
   ...   )())


.. code-block:: REPL

   #> (L2 * X Y)
   >>> # L2
   ... (lambda X, Y:
   ...     QzSTAR_(
   ...       X,
   ...       Y)
   ... )
   <function <lambda> at ...>

That's another easy template.
Between ``L`` and ``L2``,
we've probably covered the Pareto 80% majority of short-lambda use cases.
But you can see the pattern now.
We could continue to an ``L3`` with a ``Z`` parameter,
and then we've run out of alphabet.

When you see a "design pattern" in Lissp,
you don't keep repeating it.

Nothing Is Above Abstraction
::::::::::::::::::::::::::::

Are you ready for this?
You've seen all these pieces before,
even if you haven't realized they could be used this way.

Don't panic.

.. code-block:: REPL

   #> .#`(progn ,@(map (lambda i `(defmacro ,(.format "L{}" i)
   #..                                      (: :* $#expr)
   #..                              `(lambda ,',(getitem "ABCDEFGHIJKLMNOPQRSTUVWXYZ" (slice i))
   #..                                 ,$#expr)))
   #..                 (range 27)))
   >>> # __main__.._macro_.progn
   ... (# __main__.._macro_.defmacro
   ...  __import__('builtins').setattr(
   ...    __import__('builtins').globals().get(
   ...      ('_macro_')),
   ...    'L0',
   ...    # hissp.macros.._macro_.fun
   ...    # hissp.macros.._macro_.let
   ...    (
   ...     lambda _Qzwin5lyqx__lambda=(lambda *_Qzbhcx5hhq__expr:
   ...                (
   ...                  'lambda',
   ...                  '',
   ...                  _Qzbhcx5hhq__expr,
   ...                  )
   ...            ):
   ...       ((
   ...          *__import__('itertools').starmap(
   ...             _Qzwin5lyqx__lambda.__setattr__,
   ...             __import__('builtins').dict(
   ...               __name__='L0',
   ...               __qualname__='_macro_.L0',
   ...               __code__=_Qzwin5lyqx__lambda.__code__.replace(
   ...                          co_name='L0')).items()),
   ...          ),
   ...        _Qzwin5lyqx__lambda)  [-1]
   ...    )()),
   ...  # __main__.._macro_.defmacro
   ...  __import__('builtins').setattr(
   ...    __import__('builtins').globals().get(
   ...      ('_macro_')),
   ...    'L1',
   ...    # hissp.macros.._macro_.fun
   ...    # hissp.macros.._macro_.let
   ...    (
   ...     lambda _Qzwin5lyqx__lambda=(lambda *_Qzbhcx5hhq__expr:
   ...                (
   ...                  'lambda',
   ...                  'A',
   ...                  _Qzbhcx5hhq__expr,
   ...                  )
   ...            ):
   ...       ((
   ...          *__import__('itertools').starmap(
   ...             _Qzwin5lyqx__lambda.__setattr__,
   ...             __import__('builtins').dict(
   ...               __name__='L1',
   ...               __qualname__='_macro_.L1',
   ...               __code__=_Qzwin5lyqx__lambda.__code__.replace(
   ...                          co_name='L1')).items()),
   ...          ),
   ...        _Qzwin5lyqx__lambda)  [-1]
   ...    )()),
   ...  # __main__.._macro_.defmacro
   ...  __import__('builtins').setattr(
   ...    __import__('builtins').globals().get(
   ...      ('_macro_')),
   ...    'L2',
   ...    # hissp.macros.._macro_.fun
   ...    # hissp.macros.._macro_.let
   ...    (
   ...     lambda _Qzwin5lyqx__lambda=(lambda *_Qzbhcx5hhq__expr:
   ...                (
   ...                  'lambda',
   ...                  'AB',
   ...                  _Qzbhcx5hhq__expr,
   ...                  )
   ...            ):
   ...       ((
   ...          *__import__('itertools').starmap(
   ...             _Qzwin5lyqx__lambda.__setattr__,
   ...             __import__('builtins').dict(
   ...               __name__='L2',
   ...               __qualname__='_macro_.L2',
   ...               __code__=_Qzwin5lyqx__lambda.__code__.replace(
   ...                          co_name='L2')).items()),
   ...          ),
   ...        _Qzwin5lyqx__lambda)  [-1]
   ...    )()),
   ...  # __main__.._macro_.defmacro
   ...  __import__('builtins').setattr(
   ...    __import__('builtins').globals().get(
   ...      ('_macro_')),
   ...    'L3',
   ...    # hissp.macros.._macro_.fun
   ...    # hissp.macros.._macro_.let
   ...    (
   ...     lambda _Qzwin5lyqx__lambda=(lambda *_Qzbhcx5hhq__expr:
   ...                (
   ...                  'lambda',
   ...                  'ABC',
   ...                  _Qzbhcx5hhq__expr,
   ...                  )
   ...            ):
   ...       ((
   ...          *__import__('itertools').starmap(
   ...             _Qzwin5lyqx__lambda.__setattr__,
   ...             __import__('builtins').dict(
   ...               __name__='L3',
   ...               __qualname__='_macro_.L3',
   ...               __code__=_Qzwin5lyqx__lambda.__code__.replace(
   ...                          co_name='L3')).items()),
   ...          ),
   ...        _Qzwin5lyqx__lambda)  [-1]
   ...    )()),
   ...  # __main__.._macro_.defmacro
   ...  __import__('builtins').setattr(
   ...    __import__('builtins').globals().get(
   ...      ('_macro_')),
   ...    'L4',
   ...    # hissp.macros.._macro_.fun
   ...    # hissp.macros.._macro_.let
   ...    (
   ...     lambda _Qzwin5lyqx__lambda=(lambda *_Qzbhcx5hhq__expr:
   ...                (
   ...                  'lambda',
   ...                  'ABCD',
   ...                  _Qzbhcx5hhq__expr,
   ...                  )
   ...            ):
   ...       ((
   ...          *__import__('itertools').starmap(
   ...             _Qzwin5lyqx__lambda.__setattr__,
   ...             __import__('builtins').dict(
   ...               __name__='L4',
   ...               __qualname__='_macro_.L4',
   ...               __code__=_Qzwin5lyqx__lambda.__code__.replace(
   ...                          co_name='L4')).items()),
   ...          ),
   ...        _Qzwin5lyqx__lambda)  [-1]
   ...    )()),
   ...  # __main__.._macro_.defmacro
   ...  __import__('builtins').setattr(
   ...    __import__('builtins').globals().get(
   ...      ('_macro_')),
   ...    'L5',
   ...    # hissp.macros.._macro_.fun
   ...    # hissp.macros.._macro_.let
   ...    (
   ...     lambda _Qzwin5lyqx__lambda=(lambda *_Qzbhcx5hhq__expr:
   ...                (
   ...                  'lambda',
   ...                  'ABCDE',
   ...                  _Qzbhcx5hhq__expr,
   ...                  )
   ...            ):
   ...       ((
   ...          *__import__('itertools').starmap(
   ...             _Qzwin5lyqx__lambda.__setattr__,
   ...             __import__('builtins').dict(
   ...               __name__='L5',
   ...               __qualname__='_macro_.L5',
   ...               __code__=_Qzwin5lyqx__lambda.__code__.replace(
   ...                          co_name='L5')).items()),
   ...          ),
   ...        _Qzwin5lyqx__lambda)  [-1]
   ...    )()),
   ...  # __main__.._macro_.defmacro
   ...  __import__('builtins').setattr(
   ...    __import__('builtins').globals().get(
   ...      ('_macro_')),
   ...    'L6',
   ...    # hissp.macros.._macro_.fun
   ...    # hissp.macros.._macro_.let
   ...    (
   ...     lambda _Qzwin5lyqx__lambda=(lambda *_Qzbhcx5hhq__expr:
   ...                (
   ...                  'lambda',
   ...                  'ABCDEF',
   ...                  _Qzbhcx5hhq__expr,
   ...                  )
   ...            ):
   ...       ((
   ...          *__import__('itertools').starmap(
   ...             _Qzwin5lyqx__lambda.__setattr__,
   ...             __import__('builtins').dict(
   ...               __name__='L6',
   ...               __qualname__='_macro_.L6',
   ...               __code__=_Qzwin5lyqx__lambda.__code__.replace(
   ...                          co_name='L6')).items()),
   ...          ),
   ...        _Qzwin5lyqx__lambda)  [-1]
   ...    )()),
   ...  # __main__.._macro_.defmacro
   ...  __import__('builtins').setattr(
   ...    __import__('builtins').globals().get(
   ...      ('_macro_')),
   ...    'L7',
   ...    # hissp.macros.._macro_.fun
   ...    # hissp.macros.._macro_.let
   ...    (
   ...     lambda _Qzwin5lyqx__lambda=(lambda *_Qzbhcx5hhq__expr:
   ...                (
   ...                  'lambda',
   ...                  'ABCDEFG',
   ...                  _Qzbhcx5hhq__expr,
   ...                  )
   ...            ):
   ...       ((
   ...          *__import__('itertools').starmap(
   ...             _Qzwin5lyqx__lambda.__setattr__,
   ...             __import__('builtins').dict(
   ...               __name__='L7',
   ...               __qualname__='_macro_.L7',
   ...               __code__=_Qzwin5lyqx__lambda.__code__.replace(
   ...                          co_name='L7')).items()),
   ...          ),
   ...        _Qzwin5lyqx__lambda)  [-1]
   ...    )()),
   ...  # __main__.._macro_.defmacro
   ...  __import__('builtins').setattr(
   ...    __import__('builtins').globals().get(
   ...      ('_macro_')),
   ...    'L8',
   ...    # hissp.macros.._macro_.fun
   ...    # hissp.macros.._macro_.let
   ...    (
   ...     lambda _Qzwin5lyqx__lambda=(lambda *_Qzbhcx5hhq__expr:
   ...                (
   ...                  'lambda',
   ...                  'ABCDEFGH',
   ...                  _Qzbhcx5hhq__expr,
   ...                  )
   ...            ):
   ...       ((
   ...          *__import__('itertools').starmap(
   ...             _Qzwin5lyqx__lambda.__setattr__,
   ...             __import__('builtins').dict(
   ...               __name__='L8',
   ...               __qualname__='_macro_.L8',
   ...               __code__=_Qzwin5lyqx__lambda.__code__.replace(
   ...                          co_name='L8')).items()),
   ...          ),
   ...        _Qzwin5lyqx__lambda)  [-1]
   ...    )()),
   ...  # __main__.._macro_.defmacro
   ...  __import__('builtins').setattr(
   ...    __import__('builtins').globals().get(
   ...      ('_macro_')),
   ...    'L9',
   ...    # hissp.macros.._macro_.fun
   ...    # hissp.macros.._macro_.let
   ...    (
   ...     lambda _Qzwin5lyqx__lambda=(lambda *_Qzbhcx5hhq__expr:
   ...                (
   ...                  'lambda',
   ...                  'ABCDEFGHI',
   ...                  _Qzbhcx5hhq__expr,
   ...                  )
   ...            ):
   ...       ((
   ...          *__import__('itertools').starmap(
   ...             _Qzwin5lyqx__lambda.__setattr__,
   ...             __import__('builtins').dict(
   ...               __name__='L9',
   ...               __qualname__='_macro_.L9',
   ...               __code__=_Qzwin5lyqx__lambda.__code__.replace(
   ...                          co_name='L9')).items()),
   ...          ),
   ...        _Qzwin5lyqx__lambda)  [-1]
   ...    )()),
   ...  # __main__.._macro_.defmacro
   ...  __import__('builtins').setattr(
   ...    __import__('builtins').globals().get(
   ...      ('_macro_')),
   ...    'L10',
   ...    # hissp.macros.._macro_.fun
   ...    # hissp.macros.._macro_.let
   ...    (
   ...     lambda _Qzwin5lyqx__lambda=(lambda *_Qzbhcx5hhq__expr:
   ...                (
   ...                  'lambda',
   ...                  'ABCDEFGHIJ',
   ...                  _Qzbhcx5hhq__expr,
   ...                  )
   ...            ):
   ...       ((
   ...          *__import__('itertools').starmap(
   ...             _Qzwin5lyqx__lambda.__setattr__,
   ...             __import__('builtins').dict(
   ...               __name__='L10',
   ...               __qualname__='_macro_.L10',
   ...               __code__=_Qzwin5lyqx__lambda.__code__.replace(
   ...                          co_name='L10')).items()),
   ...          ),
   ...        _Qzwin5lyqx__lambda)  [-1]
   ...    )()),
   ...  # __main__.._macro_.defmacro
   ...  __import__('builtins').setattr(
   ...    __import__('builtins').globals().get(
   ...      ('_macro_')),
   ...    'L11',
   ...    # hissp.macros.._macro_.fun
   ...    # hissp.macros.._macro_.let
   ...    (
   ...     lambda _Qzwin5lyqx__lambda=(lambda *_Qzbhcx5hhq__expr:
   ...                (
   ...                  'lambda',
   ...                  'ABCDEFGHIJK',
   ...                  _Qzbhcx5hhq__expr,
   ...                  )
   ...            ):
   ...       ((
   ...          *__import__('itertools').starmap(
   ...             _Qzwin5lyqx__lambda.__setattr__,
   ...             __import__('builtins').dict(
   ...               __name__='L11',
   ...               __qualname__='_macro_.L11',
   ...               __code__=_Qzwin5lyqx__lambda.__code__.replace(
   ...                          co_name='L11')).items()),
   ...          ),
   ...        _Qzwin5lyqx__lambda)  [-1]
   ...    )()),
   ...  # __main__.._macro_.defmacro
   ...  __import__('builtins').setattr(
   ...    __import__('builtins').globals().get(
   ...      ('_macro_')),
   ...    'L12',
   ...    # hissp.macros.._macro_.fun
   ...    # hissp.macros.._macro_.let
   ...    (
   ...     lambda _Qzwin5lyqx__lambda=(lambda *_Qzbhcx5hhq__expr:
   ...                (
   ...                  'lambda',
   ...                  'ABCDEFGHIJKL',
   ...                  _Qzbhcx5hhq__expr,
   ...                  )
   ...            ):
   ...       ((
   ...          *__import__('itertools').starmap(
   ...             _Qzwin5lyqx__lambda.__setattr__,
   ...             __import__('builtins').dict(
   ...               __name__='L12',
   ...               __qualname__='_macro_.L12',
   ...               __code__=_Qzwin5lyqx__lambda.__code__.replace(
   ...                          co_name='L12')).items()),
   ...          ),
   ...        _Qzwin5lyqx__lambda)  [-1]
   ...    )()),
   ...  # __main__.._macro_.defmacro
   ...  __import__('builtins').setattr(
   ...    __import__('builtins').globals().get(
   ...      ('_macro_')),
   ...    'L13',
   ...    # hissp.macros.._macro_.fun
   ...    # hissp.macros.._macro_.let
   ...    (
   ...     lambda _Qzwin5lyqx__lambda=(lambda *_Qzbhcx5hhq__expr:
   ...                (
   ...                  'lambda',
   ...                  'ABCDEFGHIJKLM',
   ...                  _Qzbhcx5hhq__expr,
   ...                  )
   ...            ):
   ...       ((
   ...          *__import__('itertools').starmap(
   ...             _Qzwin5lyqx__lambda.__setattr__,
   ...             __import__('builtins').dict(
   ...               __name__='L13',
   ...               __qualname__='_macro_.L13',
   ...               __code__=_Qzwin5lyqx__lambda.__code__.replace(
   ...                          co_name='L13')).items()),
   ...          ),
   ...        _Qzwin5lyqx__lambda)  [-1]
   ...    )()),
   ...  # __main__.._macro_.defmacro
   ...  __import__('builtins').setattr(
   ...    __import__('builtins').globals().get(
   ...      ('_macro_')),
   ...    'L14',
   ...    # hissp.macros.._macro_.fun
   ...    # hissp.macros.._macro_.let
   ...    (
   ...     lambda _Qzwin5lyqx__lambda=(lambda *_Qzbhcx5hhq__expr:
   ...                (
   ...                  'lambda',
   ...                  'ABCDEFGHIJKLMN',
   ...                  _Qzbhcx5hhq__expr,
   ...                  )
   ...            ):
   ...       ((
   ...          *__import__('itertools').starmap(
   ...             _Qzwin5lyqx__lambda.__setattr__,
   ...             __import__('builtins').dict(
   ...               __name__='L14',
   ...               __qualname__='_macro_.L14',
   ...               __code__=_Qzwin5lyqx__lambda.__code__.replace(
   ...                          co_name='L14')).items()),
   ...          ),
   ...        _Qzwin5lyqx__lambda)  [-1]
   ...    )()),
   ...  # __main__.._macro_.defmacro
   ...  __import__('builtins').setattr(
   ...    __import__('builtins').globals().get(
   ...      ('_macro_')),
   ...    'L15',
   ...    # hissp.macros.._macro_.fun
   ...    # hissp.macros.._macro_.let
   ...    (
   ...     lambda _Qzwin5lyqx__lambda=(lambda *_Qzbhcx5hhq__expr:
   ...                (
   ...                  'lambda',
   ...                  'ABCDEFGHIJKLMNO',
   ...                  _Qzbhcx5hhq__expr,
   ...                  )
   ...            ):
   ...       ((
   ...          *__import__('itertools').starmap(
   ...             _Qzwin5lyqx__lambda.__setattr__,
   ...             __import__('builtins').dict(
   ...               __name__='L15',
   ...               __qualname__='_macro_.L15',
   ...               __code__=_Qzwin5lyqx__lambda.__code__.replace(
   ...                          co_name='L15')).items()),
   ...          ),
   ...        _Qzwin5lyqx__lambda)  [-1]
   ...    )()),
   ...  # __main__.._macro_.defmacro
   ...  __import__('builtins').setattr(
   ...    __import__('builtins').globals().get(
   ...      ('_macro_')),
   ...    'L16',
   ...    # hissp.macros.._macro_.fun
   ...    # hissp.macros.._macro_.let
   ...    (
   ...     lambda _Qzwin5lyqx__lambda=(lambda *_Qzbhcx5hhq__expr:
   ...                (
   ...                  'lambda',
   ...                  'ABCDEFGHIJKLMNOP',
   ...                  _Qzbhcx5hhq__expr,
   ...                  )
   ...            ):
   ...       ((
   ...          *__import__('itertools').starmap(
   ...             _Qzwin5lyqx__lambda.__setattr__,
   ...             __import__('builtins').dict(
   ...               __name__='L16',
   ...               __qualname__='_macro_.L16',
   ...               __code__=_Qzwin5lyqx__lambda.__code__.replace(
   ...                          co_name='L16')).items()),
   ...          ),
   ...        _Qzwin5lyqx__lambda)  [-1]
   ...    )()),
   ...  # __main__.._macro_.defmacro
   ...  __import__('builtins').setattr(
   ...    __import__('builtins').globals().get(
   ...      ('_macro_')),
   ...    'L17',
   ...    # hissp.macros.._macro_.fun
   ...    # hissp.macros.._macro_.let
   ...    (
   ...     lambda _Qzwin5lyqx__lambda=(lambda *_Qzbhcx5hhq__expr:
   ...                (
   ...                  'lambda',
   ...                  'ABCDEFGHIJKLMNOPQ',
   ...                  _Qzbhcx5hhq__expr,
   ...                  )
   ...            ):
   ...       ((
   ...          *__import__('itertools').starmap(
   ...             _Qzwin5lyqx__lambda.__setattr__,
   ...             __import__('builtins').dict(
   ...               __name__='L17',
   ...               __qualname__='_macro_.L17',
   ...               __code__=_Qzwin5lyqx__lambda.__code__.replace(
   ...                          co_name='L17')).items()),
   ...          ),
   ...        _Qzwin5lyqx__lambda)  [-1]
   ...    )()),
   ...  # __main__.._macro_.defmacro
   ...  __import__('builtins').setattr(
   ...    __import__('builtins').globals().get(
   ...      ('_macro_')),
   ...    'L18',
   ...    # hissp.macros.._macro_.fun
   ...    # hissp.macros.._macro_.let
   ...    (
   ...     lambda _Qzwin5lyqx__lambda=(lambda *_Qzbhcx5hhq__expr:
   ...                (
   ...                  'lambda',
   ...                  'ABCDEFGHIJKLMNOPQR',
   ...                  _Qzbhcx5hhq__expr,
   ...                  )
   ...            ):
   ...       ((
   ...          *__import__('itertools').starmap(
   ...             _Qzwin5lyqx__lambda.__setattr__,
   ...             __import__('builtins').dict(
   ...               __name__='L18',
   ...               __qualname__='_macro_.L18',
   ...               __code__=_Qzwin5lyqx__lambda.__code__.replace(
   ...                          co_name='L18')).items()),
   ...          ),
   ...        _Qzwin5lyqx__lambda)  [-1]
   ...    )()),
   ...  # __main__.._macro_.defmacro
   ...  __import__('builtins').setattr(
   ...    __import__('builtins').globals().get(
   ...      ('_macro_')),
   ...    'L19',
   ...    # hissp.macros.._macro_.fun
   ...    # hissp.macros.._macro_.let
   ...    (
   ...     lambda _Qzwin5lyqx__lambda=(lambda *_Qzbhcx5hhq__expr:
   ...                (
   ...                  'lambda',
   ...                  'ABCDEFGHIJKLMNOPQRS',
   ...                  _Qzbhcx5hhq__expr,
   ...                  )
   ...            ):
   ...       ((
   ...          *__import__('itertools').starmap(
   ...             _Qzwin5lyqx__lambda.__setattr__,
   ...             __import__('builtins').dict(
   ...               __name__='L19',
   ...               __qualname__='_macro_.L19',
   ...               __code__=_Qzwin5lyqx__lambda.__code__.replace(
   ...                          co_name='L19')).items()),
   ...          ),
   ...        _Qzwin5lyqx__lambda)  [-1]
   ...    )()),
   ...  # __main__.._macro_.defmacro
   ...  __import__('builtins').setattr(
   ...    __import__('builtins').globals().get(
   ...      ('_macro_')),
   ...    'L20',
   ...    # hissp.macros.._macro_.fun
   ...    # hissp.macros.._macro_.let
   ...    (
   ...     lambda _Qzwin5lyqx__lambda=(lambda *_Qzbhcx5hhq__expr:
   ...                (
   ...                  'lambda',
   ...                  'ABCDEFGHIJKLMNOPQRST',
   ...                  _Qzbhcx5hhq__expr,
   ...                  )
   ...            ):
   ...       ((
   ...          *__import__('itertools').starmap(
   ...             _Qzwin5lyqx__lambda.__setattr__,
   ...             __import__('builtins').dict(
   ...               __name__='L20',
   ...               __qualname__='_macro_.L20',
   ...               __code__=_Qzwin5lyqx__lambda.__code__.replace(
   ...                          co_name='L20')).items()),
   ...          ),
   ...        _Qzwin5lyqx__lambda)  [-1]
   ...    )()),
   ...  # __main__.._macro_.defmacro
   ...  __import__('builtins').setattr(
   ...    __import__('builtins').globals().get(
   ...      ('_macro_')),
   ...    'L21',
   ...    # hissp.macros.._macro_.fun
   ...    # hissp.macros.._macro_.let
   ...    (
   ...     lambda _Qzwin5lyqx__lambda=(lambda *_Qzbhcx5hhq__expr:
   ...                (
   ...                  'lambda',
   ...                  'ABCDEFGHIJKLMNOPQRSTU',
   ...                  _Qzbhcx5hhq__expr,
   ...                  )
   ...            ):
   ...       ((
   ...          *__import__('itertools').starmap(
   ...             _Qzwin5lyqx__lambda.__setattr__,
   ...             __import__('builtins').dict(
   ...               __name__='L21',
   ...               __qualname__='_macro_.L21',
   ...               __code__=_Qzwin5lyqx__lambda.__code__.replace(
   ...                          co_name='L21')).items()),
   ...          ),
   ...        _Qzwin5lyqx__lambda)  [-1]
   ...    )()),
   ...  # __main__.._macro_.defmacro
   ...  __import__('builtins').setattr(
   ...    __import__('builtins').globals().get(
   ...      ('_macro_')),
   ...    'L22',
   ...    # hissp.macros.._macro_.fun
   ...    # hissp.macros.._macro_.let
   ...    (
   ...     lambda _Qzwin5lyqx__lambda=(lambda *_Qzbhcx5hhq__expr:
   ...                (
   ...                  'lambda',
   ...                  'ABCDEFGHIJKLMNOPQRSTUV',
   ...                  _Qzbhcx5hhq__expr,
   ...                  )
   ...            ):
   ...       ((
   ...          *__import__('itertools').starmap(
   ...             _Qzwin5lyqx__lambda.__setattr__,
   ...             __import__('builtins').dict(
   ...               __name__='L22',
   ...               __qualname__='_macro_.L22',
   ...               __code__=_Qzwin5lyqx__lambda.__code__.replace(
   ...                          co_name='L22')).items()),
   ...          ),
   ...        _Qzwin5lyqx__lambda)  [-1]
   ...    )()),
   ...  # __main__.._macro_.defmacro
   ...  __import__('builtins').setattr(
   ...    __import__('builtins').globals().get(
   ...      ('_macro_')),
   ...    'L23',
   ...    # hissp.macros.._macro_.fun
   ...    # hissp.macros.._macro_.let
   ...    (
   ...     lambda _Qzwin5lyqx__lambda=(lambda *_Qzbhcx5hhq__expr:
   ...                (
   ...                  'lambda',
   ...                  'ABCDEFGHIJKLMNOPQRSTUVW',
   ...                  _Qzbhcx5hhq__expr,
   ...                  )
   ...            ):
   ...       ((
   ...          *__import__('itertools').starmap(
   ...             _Qzwin5lyqx__lambda.__setattr__,
   ...             __import__('builtins').dict(
   ...               __name__='L23',
   ...               __qualname__='_macro_.L23',
   ...               __code__=_Qzwin5lyqx__lambda.__code__.replace(
   ...                          co_name='L23')).items()),
   ...          ),
   ...        _Qzwin5lyqx__lambda)  [-1]
   ...    )()),
   ...  # __main__.._macro_.defmacro
   ...  __import__('builtins').setattr(
   ...    __import__('builtins').globals().get(
   ...      ('_macro_')),
   ...    'L24',
   ...    # hissp.macros.._macro_.fun
   ...    # hissp.macros.._macro_.let
   ...    (
   ...     lambda _Qzwin5lyqx__lambda=(lambda *_Qzbhcx5hhq__expr:
   ...                (
   ...                  'lambda',
   ...                  'ABCDEFGHIJKLMNOPQRSTUVWX',
   ...                  _Qzbhcx5hhq__expr,
   ...                  )
   ...            ):
   ...       ((
   ...          *__import__('itertools').starmap(
   ...             _Qzwin5lyqx__lambda.__setattr__,
   ...             __import__('builtins').dict(
   ...               __name__='L24',
   ...               __qualname__='_macro_.L24',
   ...               __code__=_Qzwin5lyqx__lambda.__code__.replace(
   ...                          co_name='L24')).items()),
   ...          ),
   ...        _Qzwin5lyqx__lambda)  [-1]
   ...    )()),
   ...  # __main__.._macro_.defmacro
   ...  __import__('builtins').setattr(
   ...    __import__('builtins').globals().get(
   ...      ('_macro_')),
   ...    'L25',
   ...    # hissp.macros.._macro_.fun
   ...    # hissp.macros.._macro_.let
   ...    (
   ...     lambda _Qzwin5lyqx__lambda=(lambda *_Qzbhcx5hhq__expr:
   ...                (
   ...                  'lambda',
   ...                  'ABCDEFGHIJKLMNOPQRSTUVWXY',
   ...                  _Qzbhcx5hhq__expr,
   ...                  )
   ...            ):
   ...       ((
   ...          *__import__('itertools').starmap(
   ...             _Qzwin5lyqx__lambda.__setattr__,
   ...             __import__('builtins').dict(
   ...               __name__='L25',
   ...               __qualname__='_macro_.L25',
   ...               __code__=_Qzwin5lyqx__lambda.__code__.replace(
   ...                          co_name='L25')).items()),
   ...          ),
   ...        _Qzwin5lyqx__lambda)  [-1]
   ...    )()),
   ...  # __main__.._macro_.defmacro
   ...  __import__('builtins').setattr(
   ...    __import__('builtins').globals().get(
   ...      ('_macro_')),
   ...    'L26',
   ...    # hissp.macros.._macro_.fun
   ...    # hissp.macros.._macro_.let
   ...    (
   ...     lambda _Qzwin5lyqx__lambda=(lambda *_Qzbhcx5hhq__expr:
   ...                (
   ...                  'lambda',
   ...                  'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
   ...                  _Qzbhcx5hhq__expr,
   ...                  )
   ...            ):
   ...       ((
   ...          *__import__('itertools').starmap(
   ...             _Qzwin5lyqx__lambda.__setattr__,
   ...             __import__('builtins').dict(
   ...               __name__='L26',
   ...               __qualname__='_macro_.L26',
   ...               __code__=_Qzwin5lyqx__lambda.__code__.replace(
   ...                          co_name='L26')).items()),
   ...          ),
   ...        _Qzwin5lyqx__lambda)  [-1]
   ...    )()))  [-1]

Whoa.

That little bit of Lissp expanded into *that much Python*.
It totally works too.

.. code-block:: REPL

   #> ((L3 add C (add A B))
   #.. "A" "B" "C")
   >>> # L3
   ... (lambda A, B, C:
   ...     add(
   ...       C,
   ...       add(
   ...         A,
   ...         B))
   ... )(
   ...   ('A'),
   ...   ('B'),
   ...   ('C'))
   'CAB'

   #> (L26)
   >>> # L26
   ... (lambda A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S, T, U, V, W, X, Y, Z: ())
   <function <lambda> at ...>

   #> (L13)
   >>> # L13
   ... (lambda A, B, C, D, E, F, G, H, I, J, K, L, M: ())
   <function <lambda> at ...>

   #> ((L0 print "Hello, World!"))
   >>> # L0
   ... (lambda :
   ...     print(
   ...       ('Hello, World!'))
   ... )()
   Hello, World!

How does this work?
I don't blame you for glossing over the Python output.
It's pretty big this time.
I mostly ignore it when it gets longer than a few lines,
unless there's something in particular I'm looking for.

But let's look at this Lissp snippet again, more carefully.

.. code-block:: Lissp

   .#`(progn ,@(map (lambda i `(defmacro ,(.format "L{}" i)
                                         (: :* $#expr)
                                 `(lambda ,',(getitem "ABCDEFGHIJKLMNOPQRSTUVWXYZ" (slice i))
                                    ,$#expr)))
                    (range 27)))

It's injecting some Hissp we generated with a template.
Those are the first two :term:`tag`\ s: :term:`inject` (``.#``),
and :term:`template quote` (:literal:`\``).
The `progn` sequences multiple expressions for their side effects.
It's like having multiple "statements" in a single expression.
We :term:`splice` (``,@``) in multiple expressions generated with a `map`.
The `map` uses a lambda to generate a code tuple for each integer from the `range`.

The lambda takes the `int` ``i`` from the `range` and produces a `defmacro` :term:`form`,
(not a :term:`macro function`, the *code for defining one*)
which, when run in the `progn` by our inject,
will define a macro.

Nothing is above abstraction in Lissp.
`defmacro` forms are *still code*,
and Hissp code is made of data structures we can manipulate programmatically.
We can make them with templates like anything else.

We need to give each `defmacro` form a different name,
so we combine the ``i`` with ``"L"`` using `str.format`.
Remember, :term:`symbol`\ s are just a special case of :term:`str atom`.

The :term:`params tuple` for `defmacro` contains a local variable name
(``expr``) which shouldn't be qualified,
and doesn't need to be an anaphor.
Thus, it's most appropriate to default to using a :term:`gensym tag` (``$#``),
to prevent the template's automatic :term:`full qualification` of symbols.

The next part is tricky.
We've directly nested a template inside another one,
without unquoting it first,
because the `defmacro` also needed a template to work.
Note that you can unquote through nested templates,
as demonstrated by the two :term:`unquote`\ s (and a :term:`quote`, ``,',``)
in front of the expression calling `getitem<operator.getitem>`.
This is an important capability,
but it can be a little mind-bending until you get used to it.
If you're not sure what something does, remember to ask the REPL.

Finally, we slice the string to the appropriate number of characters for a
:term:`params symbol`.

.. topic:: Exercise: eliminate the magic literals

   This version could be improved a bit.
   That particular string is already in the standard library,
   as `string.ascii_uppercase`.
   The `range` is using a magic number (27),
   which is a bit of a code smell.
   It should instead be derived from the `len` of the string.
   There are only 26 letters in the alphabet,
   but we also generated an ``L0`` not using any,
   hence 27 `defmacro`\ s.
   Fixing this is left as an exercise for the reader.

Take a breath.
We're not done.

Macros Can Read Code Too
::::::::::::::::::::::::

We're still providing more information than is required.
You have to change the name of your macro based on the number of arguments you expect.
But can't the macro infer this based on which parameters your expression contains?

Also, we're kind of running out of alphabet when we start on ``X``,
You often see 4-D vectors labeled :math:`\langle x, y, z, w \rangle`,
but beyond that, mathematicians just number them with subscripts.

We got around this by starting at ``A`` instead,
but then we're using up all of the uppercase ASCII one-character names.
We might want to save those for other things.
We're also limited to 26 parameters this way.
It's rare that we'd need more than three or four,
but 26 seems kind of arbitrary.

So a better approach might be with numbered parameters, like ``X₁``, ``X₂``, ``X₃``, etc.
Then, if you macro is smart enough,
it can look for the highest X-number in your expression
and automatically provide that many parameters for you.

Oh, don't worry about typing in those Unicode subscripts.
`Symbol token`\ s are NFKC normalized when they get munged.
Try copying one from this document and paste it in the REPL:

.. code-block:: REPL

   #> 'X₃
   >>> 'X3'
   'X3'

An ``X3`` would have worked just the same.
The subscript just makes it pretty.
Python doesn't allow this particular character in identifiers,
but it does also NFKC normalize what is.

We can create numbered X's the same way we created the numbered L's.

.. Lissp::

   #> (defmacro L (number : :* expr)
   #..  `(lambda ,(map (lambda i (.format "X{}" i))
   #..                 (range 1 (add 1 number)))
   #..     ,expr))
   >>> # defmacro
   ... __import__('builtins').setattr(
   ...   __import__('builtins').globals().get(
   ...     ('_macro_')),
   ...   'L',
   ...   # hissp.macros.._macro_.fun
   ...   # hissp.macros.._macro_.let
   ...   (
   ...    lambda _Qzwin5lyqx__lambda=(lambda number, *expr:
   ...               (
   ...                 'lambda',
   ...                 map(
   ...                   (lambda i:
   ...                       ('X{}').format(
   ...                         i)
   ...                   ),
   ...                   range(
   ...                     (1),
   ...                     add(
   ...                       (1),
   ...                       number))),
   ...                 expr,
   ...                 )
   ...           ):
   ...      ((
   ...         *__import__('itertools').starmap(
   ...            _Qzwin5lyqx__lambda.__setattr__,
   ...            __import__('builtins').dict(
   ...              __name__='L',
   ...              __qualname__='_macro_.L',
   ...              __code__=_Qzwin5lyqx__lambda.__code__.replace(
   ...                         co_name='L')).items()),
   ...         ),
   ...       _Qzwin5lyqx__lambda)  [-1]
   ...   )())

.. tip::

   Oh, by the way, we've been pushing individual forms to the subREPL up till now,
   but it's sometimes more convenient to save, recompile,
   and reload the whole module.
   Comment out anything you don't want loaded.
   You can still push them later.
   A `_#<discard tag>` can discard a tuple and everything in it.
   (Although it still gets *read*.)
   No, you don't have to restart the REPL!

   You already know how to compile.
   The `refresh` :term:`tag` also reloads the module.
   There's a shorthand to refresh the current module from a subREPL.
   Use a ``:`` instead of the module name:

   .. code-block:: Lissp

      #> H##refresh :

   Refreshing is appropriate after updating definitions.
   Pushing smaller selections can be better for causing side effects,
   testing, or inspecting things.

   The caveats described in `importlib.reload` still apply.
   The environment is not discarded on a reload.
   Definitions with the same name get overwritten,
   but beware that bindings from removed (or renamed) definitions persist
   until explicitly deleted.

   See also: `hissp.reader.transpile`, `defonce`, `del`.

.. code-block:: REPL

   #> (L 10)
   >>> # L
   ... (lambda X1, X2, X3, X4, X5, X6, X7, X8, X9, X10: ())
   <function <lambda> at ...>

   #> ((L 2 add X₁ X₂) "A" "B")
   >>> # L
   ... (lambda X1, X2:
   ...     add(
   ...       X1,
   ...       X2)
   ... )(
   ...   ('A'),
   ...   ('B'))
   'AB'

This version uses a number as the first argument instead of baking them into the macro names.
We're using numbered parameters now, so there's no limit.
That takes care of *generating* the parameters,
but we're still providing a redundant expected number for them.

Let's make a slight tweak.

.. Lissp::

   #> (defmacro L (: :* expr)
   #..  `(lambda ,(map (lambda i (.format "X{}" i))
   #..                 (range 1 (add 1 (max-X expr))))
   #..     ,expr))
   >>> # defmacro
   ... __import__('builtins').setattr(
   ...   __import__('builtins').globals().get(
   ...     ('_macro_')),
   ...   'L',
   ...   # hissp.macros.._macro_.fun
   ...   # hissp.macros.._macro_.let
   ...   (
   ...    lambda _Qzwin5lyqx__lambda=(lambda *expr:
   ...               (
   ...                 'lambda',
   ...                 map(
   ...                   (lambda i:
   ...                       ('X{}').format(
   ...                         i)
   ...                   ),
   ...                   range(
   ...                     (1),
   ...                     add(
   ...                       (1),
   ...                       maxQzH_X(
   ...                         expr)))),
   ...                 expr,
   ...                 )
   ...           ):
   ...      ((
   ...         *__import__('itertools').starmap(
   ...            _Qzwin5lyqx__lambda.__setattr__,
   ...            __import__('builtins').dict(
   ...              __name__='L',
   ...              __qualname__='_macro_.L',
   ...              __code__=_Qzwin5lyqx__lambda.__code__.replace(
   ...                         co_name='L')).items()),
   ...         ),
   ...       _Qzwin5lyqx__lambda)  [-1]
   ...   )())


What is this ``max-X``?
It's a venerable design technique known as *wishful thinking*.
We haven't implemented it yet.
This doesn't work.
But we *wish* it would find the maximum X number in the expression.

Can we just iterate through the expression and check?

.. Lissp::

   #> (defun max-X (expr)
   #..  (max (map (lambda x (ors (when (is_ str (type x))
   #..                             (let (match (re..fullmatch "X([1-9][0-9]*)" x))
   #..                               (when match (int (.group match 1)))))
   #..                           0))
   #..            expr)))
   >>> # defun
   ... # hissp.macros.._macro_.define
   ... __import__('builtins').globals().update(
   ...   maxQzH_X=# hissp.macros.._macro_.fun
   ...            # hissp.macros.._macro_.let
   ...            (
   ...             lambda _Qzwin5lyqx__lambda=(lambda expr:
   ...                        max(
   ...                          map(
   ...                            (lambda x:
   ...                                # ors
   ...                                (lambda x0, x1: x0 or x1())(
   ...                                  # when
   ...                                  (lambda b, c: c()if b else())(
   ...                                    is_(
   ...                                      str,
   ...                                      type(
   ...                                        x)),
   ...                                    (lambda :
   ...                                        # let
   ...                                        (
   ...                                         lambda match=__import__('re').fullmatch(
   ...                                                  ('X([1-9][0-9]*)'),
   ...                                                  x):
   ...                                            # when
   ...                                            (lambda b, c: c()if b else())(
   ...                                              match,
   ...                                              (lambda :
   ...                                                  int(
   ...                                                    match.group(
   ...                                                      (1)))
   ...                                              ))
   ...                                        )()
   ...                                    )),
   ...                                  (lambda : (0)))
   ...                            ),
   ...                            expr))
   ...                    ):
   ...               ((
   ...                  *__import__('itertools').starmap(
   ...                     _Qzwin5lyqx__lambda.__setattr__,
   ...                     __import__('builtins').dict(
   ...                       __name__='maxQzH_X',
   ...                       __qualname__='maxQzH_X',
   ...                       __code__=_Qzwin5lyqx__lambda.__code__.replace(
   ...                                  co_name='maxQzH_X')).items()),
   ...                  ),
   ...                _Qzwin5lyqx__lambda)  [-1]
   ...            )())


Does that make sense?
Read the definition carefully.
You can view the docs for any bundled macro
you don't recognize in the REPL like ``(help _macro_.foo)``,
but you might prefer searching the rendered version in the `API docs <hissp.macro>`.
Most have documented usage examples you can experiment with in the REPL.
We're using them to coalesce Python's awkward regex matches,
which can return ``None``, into a ``0``,
unless it's a string with a match.

It gets the parameters right:

.. code-block:: REPL

   #> ((L add X₂ X₁) : :* "AB")
   >>> # L
   ... (lambda X1, X2:
   ...     add(
   ...       X2,
   ...       X1)
   ... )(
   ...   *('AB'))
   'BA'

Pretty cool.

.. code-block:: REPL

   #> ((L add X₁ (add X₂ X₃))
   #.. : :* "BAR")
   >>> # L
   ... (lambda X1:
   ...     add(
   ...       X1,
   ...       add(
   ...         X2,
   ...         X3))
   ... )(
   ...   *('BAR'))
   Traceback (most recent call last):
     File "<console>", line 2, in <module>
   TypeError: <lambda>() takes 1 positional argument but 3 were given

Oh. Not that easy.
What happened?
The error message says that lambda only took one parameter,
even though the expression contained an ``X₃``.

We need to be able to check for symbols nested in tuples.
This sounds like a job for recursion.

.. Lissp::

   #> (defun flatten (form)
   #..  chain#(map (lambda x (if-else (is_ (type x) tuple)
   #..                         (flatten x)
   #..                         `(,x)))
   #..             form))
   >>> # defun
   ... # hissp.macros.._macro_.define
   ... __import__('builtins').globals().update(
   ...   flatten=# hissp.macros.._macro_.fun
   ...           # hissp.macros.._macro_.let
   ...           (
   ...            lambda _Qzwin5lyqx__lambda=(lambda form:
   ...                       __import__('itertools').chain.from_iterable(
   ...                         map(
   ...                           (lambda x:
   ...                               # ifQzH_else
   ...                               (lambda b, c, a: c()if b else a())(
   ...                                 is_(
   ...                                   type(
   ...                                     x),
   ...                                   tuple),
   ...                                 (lambda :
   ...                                     flatten(
   ...                                       x)
   ...                                 ),
   ...                                 (lambda :
   ...                                     (
   ...                                       x,
   ...                                       )
   ...                                 ))
   ...                           ),
   ...                           form))
   ...                   ):
   ...              ((
   ...                 *__import__('itertools').starmap(
   ...                    _Qzwin5lyqx__lambda.__setattr__,
   ...                    __import__('builtins').dict(
   ...                      __name__='flatten',
   ...                      __qualname__='flatten',
   ...                      __code__=_Qzwin5lyqx__lambda.__code__.replace(
   ...                                 co_name='flatten')).items()),
   ...                 ),
   ...               _Qzwin5lyqx__lambda)  [-1]
   ...           )())


More bundled macros here.
Search Hissp's docs if you can't figure out what they do.

``Flatten`` is a good utility to have for macros that have to read code.

Now we can fix ``max-X``.

.. Lissp::

   #> (defun max-X (expr)
   #..  (max (map (lambda x (ors (when (is_ str (type x))
   #..                             (let (match (re..fullmatch "X([1-9][0-9]*)" x))
   #..                               (when match (int (.group match 1)))))
   #..                           0))
   #..            (flatten expr))))
   >>> # defun
   ... # hissp.macros.._macro_.define
   ... __import__('builtins').globals().update(
   ...   maxQzH_X=# hissp.macros.._macro_.fun
   ...            # hissp.macros.._macro_.let
   ...            (
   ...             lambda _Qzwin5lyqx__lambda=(lambda expr:
   ...                        max(
   ...                          map(
   ...                            (lambda x:
   ...                                # ors
   ...                                (lambda x0, x1: x0 or x1())(
   ...                                  # when
   ...                                  (lambda b, c: c()if b else())(
   ...                                    is_(
   ...                                      str,
   ...                                      type(
   ...                                        x)),
   ...                                    (lambda :
   ...                                        # let
   ...                                        (
   ...                                         lambda match=__import__('re').fullmatch(
   ...                                                  ('X([1-9][0-9]*)'),
   ...                                                  x):
   ...                                            # when
   ...                                            (lambda b, c: c()if b else())(
   ...                                              match,
   ...                                              (lambda :
   ...                                                  int(
   ...                                                    match.group(
   ...                                                      (1)))
   ...                                              ))
   ...                                        )()
   ...                                    )),
   ...                                  (lambda : (0)))
   ...                            ),
   ...                            flatten(
   ...                              expr)))
   ...                    ):
   ...               ((
   ...                  *__import__('itertools').starmap(
   ...                     _Qzwin5lyqx__lambda.__setattr__,
   ...                     __import__('builtins').dict(
   ...                       __name__='maxQzH_X',
   ...                       __qualname__='maxQzH_X',
   ...                       __code__=_Qzwin5lyqx__lambda.__code__.replace(
   ...                                  co_name='maxQzH_X')).items()),
   ...                  ),
   ...                _Qzwin5lyqx__lambda)  [-1]
   ...            )())


Let's try again.

.. code-block:: REPL

   #> ((L add X₁ (add X₂ X₃))
   #.. : :* "BAR")
   >>> # L
   ... (lambda X1, X2, X3:
   ...     add(
   ...       X1,
   ...       add(
   ...         X2,
   ...         X3))
   ... )(
   ...   *('BAR'))
   'BAR'

Try doing that with the C preprocessor!

Function Literals
:::::::::::::::::

Let's review. The code you need to make the version we have so far is:

.. code-block:: Lissp

   hissp..prelude#:

   (defmacro L (: :* expr)
     `(lambda ,(map (lambda i (.format "X{}" i))
                    (range 1 (add 1 (max-X expr))))
        ,expr))

   (defun max-X (expr)
     (max (map (lambda x (ors (when (is_ str (type x))
                                (let (match (re..fullmatch "X([1-9][0-9]*)" x))
                                  (when match (int (.group match 1)))))
                              0))
               (flatten expr))))

   (defun flatten (form)
     chain#(map (lambda x (if-else (is_ (type x) tuple)
                            (flatten x)
                            `(,x)))
                form))

.. tip::

   Is there more than that in your file?
   If you've been composing in your editor (rather than directly in the REPL)
   like you're supposed to,
   you've probably accumulated some junk from experiments.
   Don't delete it yet!
   Experiments often make excellent test cases.
   Wrap the ones you used for manual testing in top-level `assure` forms
   to make them automatic.
   In a larger project, you might move them to separate modules using `unittest`.
   Additionally, the Lissp REPL was designed for compatibility with `doctest`,
   although that won't test the compilation from Lissp to Python
   (making it less useful for testing macros).
   In some cases, experiments can be made into scripts.
   You can add a ``(when (eq __name__ '__main__) ... )`` form or move them
   to separate modules.

Given all of this in a file named ``tutorial.lissp``,
you can start a subREPL with these already loaded using the shell command

.. code-block:: console

   $ lissp -ic "H##subrepl tutorial."

rather than pasting them all in again.

To use your macros from other Lissp modules,
use their fully-qualified names,
abbreviate the qualifier with `alias<hissp.macros._macro_.alias>`,
or (if you must) `attach` them to your current module's ``_macro_`` object.
That last one would require that your macros also be available at run time,
although there are ways to avoid that if you need to.
See the `prelude<hissp.macros._macro_.prelude>` expansion for a hint.

You can use the resulting macro as a shorter lambda for higher-order functions:

.. code-block:: REPL

   #> (list (map (L add X₁ X₁) (range 10)))
   >>> list(
   ...   map(
   ...     # L
   ...     (lambda X1:
   ...         add(
   ...           X1,
   ...           X1)
   ...     ),
   ...     range(
   ...       (10))))
   [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]

It's still a little awkward.
It feels like the ``add`` should be in the first position,
but that's taken by the ``L``.
We can fix that with a :term:`tag`.

Reader Syntax
+++++++++++++

To use :term:`tag`\ s unqualified,
you must define them in ``_macro_`` with a name ending in a ``#``.

.. Lissp::

   #> (defmacro Xᵢ\# (expr)
   #..  `(L ,@expr))
   >>> # defmacro
   ... __import__('builtins').setattr(
   ...   __import__('builtins').globals().get(
   ...     ('_macro_')),
   ...   'XiQzHASH_',
   ...   # hissp.macros.._macro_.fun
   ...   # hissp.macros.._macro_.let
   ...   (
   ...    lambda _Qzwin5lyqx__lambda=(lambda expr:
   ...               (
   ...                 '__main__.._macro_.L',
   ...                 *expr,
   ...                 )
   ...           ):
   ...      ((
   ...         *__import__('itertools').starmap(
   ...            _Qzwin5lyqx__lambda.__setattr__,
   ...            __import__('builtins').dict(
   ...              __name__='XiQzHASH_',
   ...              __qualname__='_macro_.XiQzHASH_',
   ...              __code__=_Qzwin5lyqx__lambda.__code__.replace(
   ...                         co_name='XiQzHASH_')).items()),
   ...         ),
   ...       _Qzwin5lyqx__lambda)  [-1]
   ...   )())

We have to escape the ``#`` with a backslash
or the reader will parse the name as a tag rather than a symbol
and immediately try to apply it to ``(expr)``, which is not what we want.
(Similarly, use ``(help _macro_.foo\#)``
with a ``\#`` to get help for a tag ``foo#``.)

Notice that we still used a `defmacro`,
like we do for :term:`macro function` definitions,
because this will attach a callable to the ``_macro_`` namespace,
which is also where the reader looks for :term:`unqualified` tags.
It's the way you invoke it that makes it happen at read time:

.. code-block:: REPL

   #> (list (map Xᵢ#(add X₁ X₁) ; Read-time tagging.
   #..           (range 10)))
   >>> list(
   ...   map(
   ...     # __main__.._macro_.L
   ...     (lambda X1:
   ...         add(
   ...           X1,
   ...           X1)
   ...     ),
   ...     range(
   ...       (10))))
   [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]

   #> (list (map (Xᵢ\# (add X₁ X₁)) ; Compile-time expansion.
   #..           (range 10)))
   >>> list(
   ...   map(
   ...     # XiQzHASH_
   ...     # __main__.._macro_.L
   ...     (lambda X1:
   ...         add(
   ...           X1,
   ...           X1)
   ...     ),
   ...     range(
   ...       (10))))
   [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]


.. Caution:: Avoid side effects in tag metaprograms.

   Well-written tag functions should not have side effects at read time,
   or at least make them idempotent.
   Tooling that reads Lissp may have to backtrack
   or restart reading of an invalid form.
   E.g., before compiling a form,
   the bundled `LisspREPL` attempts to read it to see if it is complete.
   If it isn't, it will ask for another line and attempt to read it again.
   Thus, a tag (and arguments)
   on the first line will get evaluated again for each line input after,
   until the form is completed or aborted.

Tags like this effectively create new reader syntax
by reinterpreting existing reader syntax.

So now we have function literals.

These are very similar to the function literals in Clojure,
and we implemented them from scratch in half a page of Lissp code.
That's the power of metaprogramming.
You can copy features from other languages,
tweak them, and experiment with your own.

Clojure's version still has a couple more features.
Let's add them.

Catch-All Parameter
+++++++++++++++++++

.. Lissp::

   #> (defmacro L (: :* expr)
   #..  `(lambda (,@(map (lambda (i)
   #..                     (.format "X{}" i))
   #..                   (range 1 (add 1 (max-X expr))))
   #..            :
   #..            ,@(when (contains (flatten expr)
   #..                              'Xᵢ)
   #..                `(:* ,'Xᵢ)))
   #..     ,expr))
   >>> # defmacro
   ... __import__('builtins').setattr(
   ...   __import__('builtins').globals().get(
   ...     ('_macro_')),
   ...   'L',
   ...   # hissp.macros.._macro_.fun
   ...   # hissp.macros.._macro_.let
   ...   (
   ...    lambda _Qzwin5lyqx__lambda=(lambda *expr:
   ...               (
   ...                 'lambda',
   ...                 (
   ...                   *map(
   ...                      (lambda i:
   ...                          ('X{}').format(
   ...                            i)
   ...                      ),
   ...                      range(
   ...                        (1),
   ...                        add(
   ...                          (1),
   ...                          maxQzH_X(
   ...                            expr)))),
   ...                   ':',
   ...                   *# when
   ...                    (lambda b, c: c()if b else())(
   ...                      contains(
   ...                        flatten(
   ...                          expr),
   ...                        'Xi'),
   ...                      (lambda :
   ...                          (
   ...                            ':*',
   ...                            'Xi',
   ...                            )
   ...                      )),
   ...                   ),
   ...                 expr,
   ...                 )
   ...           ):
   ...      ((
   ...         *__import__('itertools').starmap(
   ...            _Qzwin5lyqx__lambda.__setattr__,
   ...            __import__('builtins').dict(
   ...              __name__='L',
   ...              __qualname__='_macro_.L',
   ...              __code__=_Qzwin5lyqx__lambda.__code__.replace(
   ...                         co_name='L')).items()),
   ...         ),
   ...       _Qzwin5lyqx__lambda)  [-1]
   ...   )())

.. code-block:: REPL

   #> (Xᵢ#(print X₁ X₂ Xᵢ) 1 2 3 4 5)
   >>> # __main__.._macro_.L
   ... (lambda X1, X2, *Xi:
   ...     print(
   ...       X1,
   ...       X2,
   ...       Xi)
   ... )(
   ...   (1),
   ...   (2),
   ...   (3),
   ...   (4),
   ...   (5))
   1 2 (3, 4, 5)

How does it work? Look at what's changed. Here they are again.

.. code-block:: Lissp

   ;; old version
   (defmacro L (: :* expr)
     `(lambda ,(map (lambda (i)
                      (.format "X{}" i))
                    (range 1 (add 1 (max-X expr))))
        ,expr))

   ;; new version
   (defmacro L (: :* expr)
     `(lambda (,@(map (lambda (i)
                        (.format "X{}" i))
                      (range 1 (add 1 (max-X expr))))
               :
               ,@(when (contains (flatten expr)
                                 'Xᵢ)
                   `(:* ,'Xᵢ)))
        ,expr))

We :term:`splice`
the result of the logic that made the numbered parameters from the old version
into the new :term:`params tuple`.
Following that is the colon separator.
Remember that it's always allowed in Hissp's lambda forms,
even if you don't need it,
which makes this kind of metaprogramming easier.

Following that is the code for a star arg.
The ``Xᵢ`` is an anaphor,
so it must be interpolated into the template to prevent automatic qualification.
The `when` macro will return an empty tuple when its condition is false.
Attempting to splice in an empty tuple conveniently doesn't do anything
(like "nil punning" in other Lisps),
so the ``Xᵢ`` anaphor is only present in the parameters tuple when the
(flattened) ``expr`` `contains <operator.contains>` it.

.. topic:: Exercise: add a kwargs anahpor

   It would be nice for Python interoperability if we also had an anaphor for the kwargs.
   Clojure doesn't have these.
   Adding this is left as an exercise.
   Can you figure out how to do it?

Implied Number 1
++++++++++++++++

Clojure's version has one more feature:
the name of the first parameter doesn't need the ``1``,
but it's allowed.

The more special cases you have to add,
the more complex the macro might get.

Here you go:

.. Lissp::

   #> (defmacro L (: :* expr)
   #..  `(lambda (,@(map (lambda (i)
   #..                     (.format "X{}" i))
   #..                   (range 1 (add 1 (ors (max-X expr)
   #..                                        (contains (flatten expr)
   #..                                                  'X)))))
   #..            :
   #..            ,@(when (contains (flatten expr)
   #..                              'Xᵢ)
   #..                `(:* ,'Xᵢ)))
   #..     ,(if-else (contains (flatten expr)
   #..                         'X)
   #..        `(let (,'X ,'X₁)
   #..           ,expr)
   #..        expr)))
   >>> # defmacro
   ... __import__('builtins').setattr(
   ...   __import__('builtins').globals().get(
   ...     ('_macro_')),
   ...   'L',
   ...   # hissp.macros.._macro_.fun
   ...   # hissp.macros.._macro_.let
   ...   (
   ...    lambda _Qzwin5lyqx__lambda=(lambda *expr:
   ...               (
   ...                 'lambda',
   ...                 (
   ...                   *map(
   ...                      (lambda i:
   ...                          ('X{}').format(
   ...                            i)
   ...                      ),
   ...                      range(
   ...                        (1),
   ...                        add(
   ...                          (1),
   ...                          # ors
   ...                          (lambda x0, x1: x0 or x1())(
   ...                            maxQzH_X(
   ...                              expr),
   ...                            (lambda :
   ...                                contains(
   ...                                  flatten(
   ...                                    expr),
   ...                                  'X')
   ...                            ))))),
   ...                   ':',
   ...                   *# when
   ...                    (lambda b, c: c()if b else())(
   ...                      contains(
   ...                        flatten(
   ...                          expr),
   ...                        'Xi'),
   ...                      (lambda :
   ...                          (
   ...                            ':*',
   ...                            'Xi',
   ...                            )
   ...                      )),
   ...                   ),
   ...                 # ifQzH_else
   ...                 (lambda b, c, a: c()if b else a())(
   ...                   contains(
   ...                     flatten(
   ...                       expr),
   ...                     'X'),
   ...                   (lambda :
   ...                       (
   ...                         '__main__.._macro_.let',
   ...                         (
   ...                           'X',
   ...                           'X1',
   ...                           ),
   ...                         expr,
   ...                         )
   ...                   ),
   ...                   (lambda : expr)),
   ...                 )
   ...           ):
   ...      ((
   ...         *__import__('itertools').starmap(
   ...            _Qzwin5lyqx__lambda.__setattr__,
   ...            __import__('builtins').dict(
   ...              __name__='L',
   ...              __qualname__='_macro_.L',
   ...              __code__=_Qzwin5lyqx__lambda.__code__.replace(
   ...                         co_name='L')).items()),
   ...         ),
   ...       _Qzwin5lyqx__lambda)  [-1]
   ...   )())

.. code-block:: REPL

   #> (list (map Xᵢ#(add X X₁) (range 10)))
   >>> list(
   ...   map(
   ...     # __main__.._macro_.L
   ...     (lambda X1:
   ...         # __main__.._macro_.let
   ...         (lambda X=X1:
   ...             add(
   ...               X,
   ...               X1)
   ...         )()
   ...     ),
   ...     range(
   ...       (10))))
   [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]

Now both ``X`` and ``X₁`` refer to the same value,
even if you mix them.

Read the macro and its outputs carefully.
This version uses a bool pun.
Recall that ``False`` is a special case of ``0``
and ``True`` is a special case of ``1`` in Python.

.. topic:: Exercise: tests

   The design could be improved a bit.
   You'll probably want some automated test cases before refactoring.
   Writing tests is a little beyond the scope of this lesson,
   but you can use `assure` forms at the top level
   or subclass the standard library
   `unittest.TestCase` class in Lissp (with a `deftypeonce` and `defun`\ s),
   just like Python.

.. topic:: Exercise: refactoring

   There are several repetitions of ``flatten`` and `contains <operator.contains>`.
   Don't worry too much about the efficiency of code that only runs once at compile time.
   What matters is what comes out in the expansions.

   You could factor these out using a `let` and local variable.
   But sometimes a terse implementation is the clearest name.
   You might also consider flattening before passing to ``max-X``
   instead of letting ``max-X`` do it,
   because then you can give it the same local variable.

.. topic:: Exercise: % anaphors

   Another thing to consider is that you might change the ``X``'s to ``%``'s,
   and then it would really look like Clojure.
   This should not be hard.
   It would require munging,
   with the tradeoffs that entails for Python interop or other Hissp readers.
   Use ``%#`` as the tag name instead.
   We'll still need the ``Xᵢ#`` version for later.

   While ``%`` is a standard anaphor in Clojure,
   `%<QzPCENT_>` (but not ``%#``) is one of the bundled macro names,
   and Python already has a `%<operator-summary>` operator.
   This would only collide in the invocation position.
   (And macros get priority there.
   Bonus round: how do you force an invocation of ``%`` to use the local instead?
   With no run-time overhead?)

   If you want to give `mod <operator.mod>` that name,
   or use the `%<QzPCENT_>` macro unqualified without renaming it,
   then you might want to stick with the ``X`` naming,
   or at least remove the special case aliasing ``%1`` to ``%``.
   Also, rather than ``%&`` for the catch-all as in Clojure,
   a ``%*`` might be more consistent if you've also got a kwargs parameter,
   which you could call ``%**``.

   `X#<XQzHASH_>` is already a bundled tag name.
   Ours might seem like a drop-in replacement,
   but the bundled `X#<XQzHASH_>` has less trouble nesting,
   isn't required to use its parameter,
   and can be applied to any expression, not just tuple forms.
   If you want to use both,
   I suggest naming the subscript one either ``Xᵢ#`` or ``%#``,
   not `X#<XQzHASH_>`.

Results
+++++++

Are we shorter than Python now?

.. code-block:: Python

   lambda x:x*x

.. Lissp::

   %#(* % %)

Did we lose generality?
Yes, but not much.
You can't really nest these.
The parameters get generated even if the only occurrence in the expression is quoted.
This is the kind of thing to be aware of.
If you're not sure about something,
try it in the REPL.
But Clojure's version has the same problems,
and it gets used quite a lot.

Why You Should Be Reluctant to Inject Python Fragments
++++++++++++++++++++++++++++++++++++++++++++++++++++++

Suppose we wanted to use Python infix notation for a complex formula.

Do you see the problem with this?

.. code-block:: Lissp

   %#(|(-%2 + (%2**2 - 4*%1*%3)**0.5)/(2*%1)|)

This was supposed to be the quadratic formula.
The ``%`` is an operator in Python,
and it can't be unary.
In an injection you would have to spell it using the munged name ``QzPCENT_``.
But what if we had kept the ``X``?

.. code-block:: REPL

   #> Xᵢ#(|(-X2 + (X2**2 - 4*X1*X3)**0.5)/(2*X1)|)
   >>> # __main__.._macro_.L
   ... (lambda : (-X2 + (X2**2 - 4*X1*X3)**0.5)/(2*X1)())
   <function <lambda> at ...>

Look at the Python compilation.
It looks like we're trying to invoke the formula itself,
which would evaluate to a number, not a callable,
so this doesn't really make sense.

The tag is expecting at least one function in prefix notation.
Sure, the tag could be modified to handle this case (Try it!),
but maybe we can do the divide in prefix and keep the others infix?
This doesn't look too bad if you think of it like a fraction bar.

.. code-block:: REPL

   #> Xᵢ#(truediv |(-X2 + (X2**2 - 4*X1*X3)**0.5)|
   #..            |(2*X1)|)
   >>> # __main__.._macro_.L
   ... (lambda :
   ...     truediv(
   ...       (-X2 + (X2**2 - 4*X1*X3)**0.5),
   ...       (2*X1))
   ... )
   <function <lambda> at ...>

Now the formula looks right,
but look at the compiled Python output.
This lambda has no parameters!
Python injections hide information that code-reading
:term:`metaprogram`\ s need to work.
A metaprogram that doesn't have to read the code,
like our ``L3`` (or the bundled `XYZ#<XYZQzHASH_>` tag),
would have worked fine.

The code-reading metaprogram was unable to detect any matching symbols
because it doesn't look inside the injected strings.
In principle, it *could have*,
but it might be a lot more work if you want it to be reliable.
It could function if the highest parameter also appeared outside the string
(in a `progn`, say),
but at that point, you might as well use a normal lambda.

Regex might be good enough for a simple case like this,
but even if you write it very carefully,
are you sure you're catching all the edge cases?
To really do it right,
you'd have to *parse the Python to AST*,
understand the structure (not exactly trivial), search it, and then keep it up to date with new versions of Python,
since it's not an especially stable API.

The whole point of using Hissp instead is so you don't have to do all this.
Hissp is a kind of AST with lower complexity.
It's just tuples.
Stay out of parsing text.

Arguably, our final ``%#`` or ``Xᵢ#`` macro didn't do it right either,
since it still detects the anaphors even if they're quoted,
but this level of correctness is good enough for Clojure's function literals,
which have the same issue.
A simple basic syntax means there are relatively few edge cases you have to be aware of.

Hissp is so simple that a full code-walking macro would only have to pre-expand all macros,
and handle atoms, calls, ``quote``, and ``lambda``,
which we will be demonstrating later!

If you add Python injections to the list,
then you also have to handle the entirety of all Python expressions.
Don't expect Hissp macros to do this.
Be reluctant to use Python injections,
and be aware of where they might break things.
They're mainly useful as performance optimizations
(but can be convenient when used judiciously).
In principle,
you should be able to do everything else without them.

Python Injection is Really Powerful Though
------------------------------------------

:term:`Standard` Hissp compiles to a restricted subset of Python.
Python expressions have a lot of features that standard Hissp lacks.
(The infix operators we just saw, for example.)
These are all still available via injection.
On the other hand, Hissp has module handles and macros;
and Lissp has munging and tags,
none of which can simply be injected.

What if you want both?
You could write the whole expression in Python.
Hissp's and Lissp's features do ultimately have to compile to Python,
so you could write out the compilation yourself,
but this can be quite verbose in some cases:

.. code-block:: REPL

   #> |__import__('string').ascii_uppercase[::2]|
   >>> __import__('string').ascii_uppercase[::2]
   'ACEGIKMOQSUWY'

On the other hand, you could write the whole thing in Lissp,
since it has alternatives to everything Python can do:

.. code-block:: REPL

   #> (operator..getitem string..ascii_uppercase (slice None None 2))
   >>> __import__('operator').getitem(
   ...   __import__('string').ascii_uppercase,
   ...   slice(
   ...     None,
   ...     None,
   ...     (2)))
   'ACEGIKMOQSUWY'

This is *usually* the right answer,
and it works better with metaprograms,
but sometimes the Python expression is a lot more concise.

Mixing a Python subexpression in Lissp code is usually pretty easy with a fragment token,
but there are a few things to watch out for.
You can usually avoid writing munged names
or `__import__` in the injection yourself
by using `let` to rename things
or by using names invariant under munging in the first place:

.. code-block:: REPL

   #> (let (ABCs string..ascii_uppercase) |ABCs[::2]|)
   >>> # let
   ... (lambda ABCs=__import__('string').ascii_uppercase: ABCs[::2])()
   'ACEGIKMOQSUWY'

In more difficult cases,
you could make a lambda in the `let` and call it inside the fragment.

Mixing a Lissp subexpression in a fragment token doesn't work.
But that doesn't mean you need to compile it by hand.
Use a :term:`text macro`:

.. Lissp::

   #> (defmacro mix (: :* args)
   #..  (.join "" (map hissp..readerless args)))
   >>> # defmacro
   ... __import__('builtins').setattr(
   ...   __import__('builtins').globals().get(
   ...     ('_macro_')),
   ...   'mix',
   ...   # hissp.macros.._macro_.fun
   ...   # hissp.macros.._macro_.let
   ...   (
   ...    lambda _Qzdoxkbke4__lambda=(lambda *args:
   ...               ('').join(
   ...                 map(
   ...                   __import__('hissp').readerless,
   ...                   args))
   ...           ):
   ...      ((
   ...         *__import__('itertools').starmap(
   ...            _Qzdoxkbke4__lambda.__setattr__,
   ...            __import__('builtins').dict(
   ...              __name__='mix',
   ...              __qualname__='_macro_.mix',
   ...              __code__=_Qzdoxkbke4__lambda.__code__.replace(
   ...                         co_name='mix')).items()),
   ...         ),
   ...       _Qzdoxkbke4__lambda)  [-1]
   ...   )())

.. code-block:: REPL

   #> (mix string..ascii_uppercase|[::2]|)
   >>> # mix
   ... __import__('string').ascii_uppercase[::2]
   'ACEGIKMOQSUWY'

You usually want to run Hissp objects through `readerless`
before embedding them in a code string.
This lets the compiler do the conversion to Python.
When run in a macro, the compiler will use the appropriate namespace:
its expansion context, not (necessarily) its definition context.

Text macros are almost like defining a new :term:`special form`.
Rather than transforming AST to AST (the Hissp forms),
you're playing the role of the compiler and transforming AST to Python.
Don't expect other macros to handle your :term:`nonstandard` special forms.
But, in principle, you could write macros that can handle your own.
At least if you don't have too many.

.. TODO: optimize macro

`mix` is a bundled macro.
You don't need it for slices.
We have the `[#<QzLSQB_QzHASH_>` tag for that,
and it does use injection.
But ``mix`` is a lot more general.

----

Tags can similarly return Python fragments.

A single star parameter using control words
is noticeably more verbose in Lissp than in Python:

.. code-block:: REPL

   #> ((lambda (: :* a-tuple) a-tuple) 1 2)
   >>> (lambda *aQzH_tuple: aQzH_tuple)(
   ...   (1),
   ...   (2))
   (1, 2)

You have to say ``: :* foo`` instead of just ``*foo``.
Of course, we don't have to write the commas in Hissp,
but that doesn't help when there's only one parameter.

Injection can help us in this case.
Remember from the `lissp_whirlwind_tour` that we can use a fragment instead,
but notice we've lost munging and have to use an underscore:

.. code-block:: REPL

   #> ((lambda (|*a_tuple|) a_tuple) 1 2)
   >>> (lambda *a_tuple: a_tuple)(
   ...   (1),
   ...   (2))
   (1, 2)

We do have `en#<enQzHASH_>` for this case,
but it can't handle any other argument types.

.. code-block:: REPL

   #> (en#(lambda (a-tuple) a-tuple) 1 2)
   >>> (lambda *_Qz73ccdf3e__xs:
   ...     (lambda aQzH_tuple: aQzH_tuple)(
   ...       _Qz73ccdf3e__xs)
   ... )(
   ...   (1),
   ...   (2))
   (1, 2)

This sounds like a job for `mix` again,
but it doesn't work.
``lambda`` is a :term:`special form`,
and the compiler won't expand macros where it expects a parameter name.
The macro would have to expand to the lambda instead.

But that doesn't prevent us from using a tag that reads as a Python fragment.
Remember, read time happens before compile time.

.. Lissp::

   #> (defmacro *\# a (.format "*{}" a))
   >>> # defmacro
   ... __import__('builtins').setattr(
   ...   __import__('builtins').globals().get(
   ...     ('_macro_')),
   ...   'QzSTAR_QzHASH_',
   ...   # hissp.macros.._macro_.fun
   ...   # hissp.macros.._macro_.let
   ...   (
   ...    lambda _Qzdoxkbke4__lambda=(lambda a:
   ...               ('*{}').format(
   ...                 a)
   ...           ):
   ...      ((
   ...         *__import__('itertools').starmap(
   ...            _Qzdoxkbke4__lambda.__setattr__,
   ...            __import__('builtins').dict(
   ...              __name__='QzSTAR_QzHASH_',
   ...              __qualname__='_macro_.QzSTAR_QzHASH_',
   ...              __code__=_Qzdoxkbke4__lambda.__code__.replace(
   ...                         co_name='QzSTAR_QzHASH_')).items()),
   ...         ),
   ...       _Qzdoxkbke4__lambda)  [-1]
   ...   )())

.. code-block:: REPL

   #> ((lambda (*#a-tuple *#*#a-dict)
   #..   (print a-tuple a-dict))
   #.. 1 2 : foo 2)
   >>> (lambda *aQzH_tuple, **aQzH_dict:
   ...     print(
   ...       aQzH_tuple,
   ...       aQzH_dict)
   ... )(
   ...   (1),
   ...   (2),
   ...   foo=(2))
   (1, 2) {'foo': 2}

We didn't bother running the symbol through `readerless` in this case.
:term:`Unqualified` symbols are already valid :term:`Python fragment`\ s,
so it wouldn't do anything, but wouldn't hurt either.
The munging happens regardless, since that's done by the reader.

``*#`` isn't bundled.
It's not buying us much.
But the implementation is trivial if you want it.

More Literals
=============

While other data types in code must be built up from the primitive notation,
Python has built-in notation for certain common ones.
(And Lissp inherits most of these.)

This can be very convenient compared to the alternative.
Imagine if you had to represent text as lists of numbers.
That's closer to what the machine uses in memory.
Many common programming tasks would become very tedious that way.
Thus, the need for string literal notation.

But the available notations are somewhat arbitrary.
Many languages in common use lack Python's notation for complex numbers,
for example.
Python, on the other hand, currently lacks built-in notation for exact fractions,
which many Lisps include.
Other languages made other selections,
which may make them more or less convenient for certain problem domains.

What notations would an ideal language have?
Every conceivable "primitive"?
Or at least all of those in common use?
(Mathematica?)
Such a language would be more difficult to learn,
and perhaps difficult to write and debug.
It's much easier to familiarize oneself with a small set of primitive notations,
and the means of combination.
And in any case,
many desirable notations would collide and then be ambiguous.

Hissp has a better way: extensibility through simplicity.

In Lissp, we can create new notation as-needed,
with an overhead of just a few characters for a tag to disambiguate from the built-ins
(and each other).
You only have to learn a new notation when it's worth your while.

Hexadecimal
:::::::::::

You can use Python's `int` builtin to convert a string containing a hexadecimal
number to the corresponding integer value.

.. code-block:: pycon

   >>> int("FF", 16)
   255

Of course, Python already has a built-in notation for this,
disambiguated from normal base-ten ints using the ``0x`` "tag".

.. code-block:: pycon

   >>> 0xFF
   255

But what if it didn't?

About the best Python could do would be something like this.

.. code-block:: pycon

   >>> def b16(x):
   ...     return int(x, 16)
   ...
   >>> b16("FF")
   255

Lissp gives us a better option.

.. Lissp::

   #> (defmacro \16\# (x)
   #..  (int x 16))
   >>> # defmacro
   ... __import__('builtins').setattr(
   ...   __import__('builtins').globals().get(
   ...     ('_macro_')),
   ...   'QzDIGITxONE_6QzHASH_',
   ...   # hissp.macros.._macro_.fun
   ...   # hissp.macros.._macro_.let
   ...   (
   ...    lambda _Qzwin5lyqx__lambda=(lambda x:
   ...               int(
   ...                 x,
   ...                 (16))
   ...           ):
   ...      ((
   ...         *__import__('itertools').starmap(
   ...            _Qzwin5lyqx__lambda.__setattr__,
   ...            __import__('builtins').dict(
   ...              __name__='QzDIGITxONE_6QzHASH_',
   ...              __qualname__='_macro_.QzDIGITxONE_6QzHASH_',
   ...              __code__=_Qzwin5lyqx__lambda.__code__.replace(
   ...                         co_name='QzDIGITxONE_6QzHASH_')).items()),
   ...         ),
   ...       _Qzwin5lyqx__lambda)  [-1]
   ...   )())

We've defined a tag that turns hexadecimal strings into ints.
And it does it so at *read time*.
There's no run-time overhead for the conversion;
the result is compiled in line.

This works,

.. code-block:: REPL

   #> 16#FF
   >>> (255)
   255

however, this doesn't.

.. code-block:: REPL

   #> 16#12
   Traceback (most recent call last):
     ...
   TypeError: int() can't convert non-string with explicit base

What's going on?
Well, ``FF`` is a valid identifier,
so it reads as a Hissp `str` atom containing that identifier,
but ``12`` is a valid base-ten int,
so it's read as an `int` atom.
Python's `int` builtin doesn't do base conversions for those.

.. code-block:: pycon

   >>> int(12, 16)
   Traceback (most recent call last):
     ...
   TypeError: int() can't convert non-string with explicit base

No matter, this is an easy fix.
Convert it to a string,
and it works regardless of which type you start with.

.. code-block:: pycon

   >>> int(str(12), 16)
   18
   >>> int(str("FF"), 16)
   255

New version.

.. Lissp::

   #> (defmacro \16\# (x)
   #..  (int (str x) 16))
   >>> # defmacro
   ... __import__('builtins').setattr(
   ...   __import__('builtins').globals().get(
   ...     ('_macro_')),
   ...   'QzDIGITxONE_6QzHASH_',
   ...   # hissp.macros.._macro_.fun
   ...   # hissp.macros.._macro_.let
   ...   (
   ...    lambda _Qzwin5lyqx__lambda=(lambda x:
   ...               int(
   ...                 str(
   ...                   x),
   ...                 (16))
   ...           ):
   ...      ((
   ...         *__import__('itertools').starmap(
   ...            _Qzwin5lyqx__lambda.__setattr__,
   ...            __import__('builtins').dict(
   ...              __name__='QzDIGITxONE_6QzHASH_',
   ...              __qualname__='_macro_.QzDIGITxONE_6QzHASH_',
   ...              __code__=_Qzwin5lyqx__lambda.__code__.replace(
   ...                         co_name='QzDIGITxONE_6QzHASH_')).items()),
   ...         ),
   ...       _Qzwin5lyqx__lambda)  [-1]
   ...   )())

And now it works as well as the built-in notation.

.. code-block:: REPL

   #> '(16#ff 0xff 16#12 0x12 16#FEED_FACE 0xFEED_FACE)
   >>> ((255),
   ...  (255),
   ...  (18),
   ...  (18),
   ...  (4277009102),
   ...  (4277009102),)
   (255, 255, 18, 18, 4277009102, 4277009102)

Or does it?

.. code-block:: REPL

   #> -16#1
     File "<console>", line 1
       -16#1
           ^
   SyntaxError: Unknown reader macro QzH_16

The minus sign changed the tag!
If we don't want to define a new ``-16#`` tag
(which is one option),
we'd have to put the sign after.

.. code-block:: REPL

   #> 16#-1
   >>> (-1)
   -1

That worked. Not.

.. code-block:: REPL

   #> 16#-FF
   Traceback (most recent call last):
     ...
   ValueError: invalid literal for int() with base 16: 'QzH_FF'

But this is fine.

.. code-block:: REPL

   #> 16#|-FF|
   >>> (-255)
   -255

.. sidebar:: Lissp's tags are a feature of Lissp itself, not of the Hissp compiler.

   Tags serve similar roles as reader macros do in other Lisps.
   An alternate Hissp reader could do that,
   but Lissp's lexer is *intentionally* not extensible,
   for the same reasons that Clojure does not give the programmer access to its read table:
   your tooling would no longer be able to tokenize your code.

What's going on?
:term:`Symbol token`\ s do read as Hissp :term:`str atom`\ s like the
:term:`fragment token`\ s do, but special characters get munged!

Remember, tags are applied to the next *parsed object*,
not to the next token from the lexer,
and certainly not to the raw character stream.
This makes them more like Clojure's tagged literals
than like Common Lisp's reader macros.

The ``16#`` tag was very easy to implement when you only applied it to
:term:`str atom`\ s,
but since it can take multiple types,
you have to be sure to handle each of them.

Fortunately, we can fix this too,
because munging is (mostly) reversible.

.. Lissp::

   #> (defmacro \16\# (x)
   #..  "hexadecimal"
   #..  (int (H#demunge (str x))
   #..       16))
   >>> # defmacro
   ... __import__('builtins').setattr(
   ...   __import__('builtins').globals().get(
   ...     ('_macro_')),
   ...   'QzDIGITxONE_6QzHASH_',
   ...   # hissp.macros.._macro_.fun
   ...   # hissp.macros.._macro_.let
   ...   (
   ...    lambda _Qzwin5lyqx__lambda=(lambda x:
   ...               int(
   ...                 __import__('hissp').demunge(
   ...                   str(
   ...                     x)),
   ...                 (16))
   ...           ):
   ...      ((
   ...         *__import__('itertools').starmap(
   ...            _Qzwin5lyqx__lambda.__setattr__,
   ...            __import__('builtins').dict(
   ...              __doc__=('hexadecimal'),
   ...              __name__='QzDIGITxONE_6QzHASH_',
   ...              __qualname__='_macro_.QzDIGITxONE_6QzHASH_',
   ...              __code__=_Qzwin5lyqx__lambda.__code__.replace(
   ...                         co_name='QzDIGITxONE_6QzHASH_')).items()),
   ...         ),
   ...       _Qzwin5lyqx__lambda)  [-1]
   ...   )())

.. code-block:: REPL

   #> 16#-FF
   >>> (-255)
   -255

But what's the point of all of this when we already have hexadecimal notation built in?

Well, with tags, you can implement any base you want.

.. Lissp::

   #> (defmacro \6\# (x)
   #..  "seximal"
   #..  (int (str x) 6))
   >>> # defmacro
   ... __import__('builtins').setattr(
   ...   __import__('builtins').globals().get(
   ...     ('_macro_')),
   ...   'QzDIGITxSIX_QzHASH_',
   ...   # hissp.macros.._macro_.fun
   ...   # hissp.macros.._macro_.let
   ...   (
   ...    lambda _Qzwin5lyqx__lambda=(lambda x:
   ...               int(
   ...                 str(
   ...                   x),
   ...                 (6))
   ...           ):
   ...      ((
   ...         *__import__('itertools').starmap(
   ...            _Qzwin5lyqx__lambda.__setattr__,
   ...            __import__('builtins').dict(
   ...              __doc__=('seximal'),
   ...              __name__='QzDIGITxSIX_QzHASH_',
   ...              __qualname__='_macro_.QzDIGITxSIX_QzHASH_',
   ...              __code__=_Qzwin5lyqx__lambda.__code__.replace(
   ...                         co_name='QzDIGITxSIX_QzHASH_')).items()),
   ...         ),
   ...       _Qzwin5lyqx__lambda)  [-1]
   ...   )())

.. code-block:: REPL

   #> '(6#5 6#10 6#11 6#12)
   >>> ((5),
   ...  (6),
   ...  (7),
   ...  (8),)
   (5, 6, 7, 8)

   #> 6#543210
   >>> (44790)
   44790

Or you can add floating-point. Python's literal notation can't do that.

.. Lissp::

   #> (defmacro \16\# (x)
   #..  (let (x (H#demunge (str x)))
   #..    (if-else (re..search "[.Pp]" x)
   #..      (float.fromhex x)
   #..      (int x 16))))
   >>> # defmacro
   ... __import__('builtins').setattr(
   ...   __import__('builtins').globals().get(
   ...     ('_macro_')),
   ...   'QzDIGITxONE_6QzHASH_',
   ...   # hissp.macros.._macro_.fun
   ...   # hissp.macros.._macro_.let
   ...   (
   ...    lambda _Qzwin5lyqx__lambda=(lambda x:
   ...               # let
   ...               (
   ...                lambda x=__import__('hissp').demunge(
   ...                         str(
   ...                           x)):
   ...                   # ifQzH_else
   ...                   (lambda b, c, a: c()if b else a())(
   ...                     __import__('re').search(
   ...                       ('[.Pp]'),
   ...                       x),
   ...                     (lambda :
   ...                         float.fromhex(
   ...                           x)
   ...                     ),
   ...                     (lambda :
   ...                         int(
   ...                           x,
   ...                           (16))
   ...                     ))
   ...               )()
   ...           ):
   ...      ((
   ...         *__import__('itertools').starmap(
   ...            _Qzwin5lyqx__lambda.__setattr__,
   ...            __import__('builtins').dict(
   ...              __name__='QzDIGITxONE_6QzHASH_',
   ...              __qualname__='_macro_.QzDIGITxONE_6QzHASH_',
   ...              __code__=_Qzwin5lyqx__lambda.__code__.replace(
   ...                         co_name='QzDIGITxONE_6QzHASH_')).items()),
   ...         ),
   ...       _Qzwin5lyqx__lambda)  [-1]
   ...   )())

.. code-block:: REPL

   #> '(16#FEED_FACE 16#-FEED.FACE 16#0.1 16#-.2 16#.4 16#-.8)
   >>> ((4277009102),
   ...  (-65261.97970581055),
   ...  (0.0625),
   ...  (-0.125),
   ...  (0.25),
   ...  (-0.5),)
   (4277009102, -65261.97970581055, 0.0625, -0.125, 0.25, -0.5)

   #> 16#Cp-2 ; 12.*2**-2
   >>> (3.0)
   3.0

See `float.fromhex` for an explanation of the exponent notation.

Decimal
:::::::

Floating-point numbers are very useful,
but they have some important limitations.

.. code-block:: pycon

   >>> 0.2 * 3
   0.6000000000000001

Not quite what you expected?
Binary floating-point can't represent exact fifths like decimal can.
For exact decimals, you need decimal floating-point.

.. code-block:: REPL

   #> (mul (decimal..Decimal "0.2") 3)
   >>> mul(
   ...   __import__('decimal').Decimal(
   ...     ('0.2')),
   ...   (3))
   Decimal('0.6')

Because it takes a single string argument,
you can already use `decimal.Decimal` as a :term:`fully-qualified tag`:

.. code-block:: REPL

   #> (mul decimal..Decimal#|.2| 3)
   >>> mul(
   ...   # Decimal('0.2')
   ...   __import__('pickle').loads(b'cdecimal\nDecimal\n(V0.2\ntR.'),
   ...   (3))
   Decimal('0.6')

It's kind of long though.

Fully-qualified tags like this are fine for occasional one-offs
or ``lissp -c`` commands when it's not worth the overhead to implement something better,
but it's going to get tedious for the human to type
(and probably to read) if it gets used a lot.

You can attach it to the ``_macro_`` namespace using a name ending in ``#``
to use it :term:`unqualified`:

.. code-block:: REPL

   #> (define _macro_.10\# decimal..Decimal)
   >>> # define
   ... __import__('builtins').setattr(
   ...   _macro_,
   ...   'QzDIGITxONE_0QzHASH_',
   ...   __import__('decimal').Decimal)

   #> (mul 10#|0.2| 3)
   >>> mul(
   ...   # Decimal('0.2')
   ...   __import__('pickle').loads(b'cdecimal\nDecimal\n(V0.2\ntR.'),
   ...   (3))
   Decimal('0.6')

Unqualified tags like this can be a bit cryptic.
The fully-qualified version was much clearer.
Consider carefully if it's worth making the next programmer learn a new notation.

Notice that Hissp had to use a pickle here,
because it had to emit code for the object,
but Python has no literal notation for Decimal objects.

The reader didn't emit the Hissp code for making a Decimal,
but an actual Decimal atom, at read time.
The pickling isn't done by the reader.
It doesn't happen until the compiler has to emit something
that it doesn't have a round-tripping representation for.

Something like this never goes through a pickle.

.. code-block:: REPL

   #> 'builtins..repr#10#|.2|
   >>> "Decimal('0.2')"
   "Decimal('0.2')"

It changed to a string before the compiler had to emit it.

Decimal can also take float objects,
but this isn't always a good idea.

.. code-block:: REPL

   #> decimal..Decimal#.2
   >>> # Decimal('0.200000000000000011102230246251565404236316680908203125')
   ... __import__('pickle').loads(b'cdecimal\nDecimal\n(V0.200000000000000011102230246251565404236316680908203125\ntR.')
   Decimal('0.200000000000000011102230246251565404236316680908203125')

There's no bug in Decimal.
That's just the exact binary fraction closest to one-fifth,
given the available precision in a float,
when represented as a decimal.

Maybe we could work around this if we converted to a string first?
We can improve this a lot with a custom defmacro.

.. Lissp::

   #> (defmacro \10\# x `(decimal..Decimal ',(str x)))
   >>> # defmacro
   ... __import__('builtins').setattr(
   ...   __import__('builtins').globals().get(
   ...     ('_macro_')),
   ...   'QzDIGITxONE_0QzHASH_',
   ...   # hissp.macros.._macro_.fun
   ...   # hissp.macros.._macro_.let
   ...   (
   ...    lambda _Qzwin5lyqx__lambda=(lambda x:
   ...               (
   ...                 'decimal..Decimal',
   ...                 (
   ...                   'quote',
   ...                   str(
   ...                     x),
   ...                   ),
   ...                 )
   ...           ):
   ...      ((
   ...         *__import__('itertools').starmap(
   ...            _Qzwin5lyqx__lambda.__setattr__,
   ...            __import__('builtins').dict(
   ...              __name__='QzDIGITxONE_0QzHASH_',
   ...              __qualname__='_macro_.QzDIGITxONE_0QzHASH_',
   ...              __code__=_Qzwin5lyqx__lambda.__code__.replace(
   ...                         co_name='QzDIGITxONE_0QzHASH_')).items()),
   ...         ),
   ...       _Qzwin5lyqx__lambda)  [-1]
   ...   )())

.. code-block:: REPL

   #> 10#.2
   >>> __import__('decimal').Decimal(
   ...   '0.2')
   Decimal('0.2')

This is better.
It's a much shorter notation;
there are no extra digits after the 2;
and (because we used a template)
it compiled to the straightforward code for a Decimal,
rather than a pickle.
This makes the compiled output a bit easier to read,
but using code like this, rather than the Decimal object itself,
may make it less useful as input to other macros.
Which approach is better depends on your needs.

As a rule of thumb,
for simple, atomic, immutable values (like Decimals)
a pickle is probably OK.
For data structures, it's better not to hide the contents,
which may not even be picklable in some cases.

But there's still a subtle problem:

.. code-block:: REPL

   #> 10#.1234567890_1234567890_000 ; Look at how many digits get lost.
   >>> __import__('decimal').Decimal(
   ...   '0.12345678901234568')
   Decimal('0.12345678901234568')

   #> 10#|.1234567890_1234567890_000| ; Decimal can even keep the trailing 0000.
   >>> __import__('decimal').Decimal(
   ...   '.1234567890_1234567890_000')
   Decimal('0.12345678901234567890000')

We have limited precision when tagging a float instead of a string.
If you don't need the precision, it's fine.
If you do, you can still use a string,
but you have to be aware of this.
Decimal also keeps trailing zeros to represent significant figures.
But floats never do this, even when the precision is available.

It would be nice if the macro could deal with it for us,
but there's just no getting around these issues when using a float.
Tags get the parsed object,
and by then, some information has been lost.
One could argue that a float literal written with more precision than is
available should be a syntax error,
but Python doesn't care.
Fragment tokens are often a good choice of argument type for reader tags.

In cases like this,
it's best to not use a float at all,
but a fragment token is not the only alternative available:

.. Lissp::

   #> (defmacro \10\# d (decimal..Decimal (H#demunge (str d))))
   >>> # defmacro
   ... __import__('builtins').setattr(
   ...   __import__('builtins').globals().get(
   ...     ('_macro_')),
   ...   'QzDIGITxONE_0QzHASH_',
   ...   # hissp.macros.._macro_.fun
   ...   # hissp.macros.._macro_.let
   ...   (
   ...    lambda _Qzwin5lyqx__lambda=(lambda d:
   ...               __import__('decimal').Decimal(
   ...                 __import__('hissp').demunge(
   ...                   str(
   ...                     d)))
   ...           ):
   ...      ((
   ...         *__import__('itertools').starmap(
   ...            _Qzwin5lyqx__lambda.__setattr__,
   ...            __import__('builtins').dict(
   ...              __name__='QzDIGITxONE_0QzHASH_',
   ...              __qualname__='_macro_.QzDIGITxONE_0QzHASH_',
   ...              __code__=_Qzwin5lyqx__lambda.__code__.replace(
   ...                         co_name='QzDIGITxONE_0QzHASH_')).items()),
   ...         ),
   ...       _Qzwin5lyqx__lambda)  [-1]
   ...   )())

.. code-block:: REPL

   #> 10#.1234567890_1234567890_000_ ; No || required. _ though.
   >>> # Decimal('0.12345678901234567890000')
   ... __import__('pickle').loads(b'cdecimal\nDecimal\n(V0.12345678901234567890000\ntR.')
   Decimal('0.12345678901234567890000')

   #> 10#.200 ; Floats still work.
   >>> # Decimal('0.2')
   ... __import__('pickle').loads(b'cdecimal\nDecimal\n(V0.2\ntR.')
   Decimal('0.2')

   #> 10#.200_ ; But you can control precision.
   >>> # Decimal('0.200')
   ... __import__('pickle').loads(b'cdecimal\nDecimal\n(V0.200\ntR.')
   Decimal('0.200')

Floats aren't allowed to have a trailing underscore,
so that makes it a symbol.
Decimal, on the other hand, removes all underscores when processing.
Even if it didn't, that's the kind of thing a tag metaprogram could do.

If you're worried about accidentally using a float
(by leaving off the underscore)
when you need more precision,
you could skip the `str` conversion,
and then a float wouldn't be a valid argument anymore.
That's how the bundled `M#<MQzHASH_>` works.

Binding Conditions
==================

Say you want to find the first word containing a lowercase "z" in some strings:

.. Lissp::

   #> (defun find-z-word (text)
   #..  (print "found:" (-> '|\b\w*z\w*\b| (re..search text) (.group 0))))
   >>> # defun
   ... # hissp.macros.._macro_.define
   ... __import__('builtins').globals().update(
   ...   findQzH_zQzH_word=# hissp.macros.._macro_.fun
   ...                     # hissp.macros.._macro_.let
   ...                     (
   ...                      lambda _Qztbhvvkna__lambda=(lambda text:
   ...                                 print(
   ...                                   ('found:'),
   ...                                   # QzH_QzGT_
   ...                                   __import__('re').search(
   ...                                     '\\b\\w*z\\w*\\b',
   ...                                     text).group(
   ...                                     (0)))
   ...                             ):
   ...                        ((
   ...                           *__import__('itertools').starmap(
   ...                              _Qztbhvvkna__lambda.__setattr__,
   ...                              __import__('builtins').dict(
   ...                                __name__='findQzH_zQzH_word',
   ...                                __qualname__='findQzH_zQzH_word',
   ...                                __code__=_Qztbhvvkna__lambda.__code__.replace(
   ...                                           co_name='findQzH_zQzH_word')).items()),
   ...                           ),
   ...                         _Qztbhvvkna__lambda)  [-1]
   ...                     )())

.. code-block:: REPL

   #> (find-z-word "The quick brown fox jumps over the lazy dog!")
   >>> findQzH_zQzH_word(
   ...   ('The quick brown fox jumps over the lazy dog!'))
   found: lazy

A simple regex worked. Not.

.. code-block:: REPL

   #> (find-z-word "The quick brown fox jumps over the sleeping dog!")
   >>> findQzH_zQzH_word(
   ...   ('The quick brown fox jumps over the sleeping dog!'))
   Traceback (most recent call last):
     ...
   AttributeError: 'NoneType' object has no attribute 'group'

We've already found a problem.
Python's regex functions return ``None`` instead of a useful empty match object when no match was found,
and the ``NoneType`` has no such method.
Some questionable design decisions there.
On several levels.
We need to check if a match exists before we know it's safe to print what it found.
Let's fix that:

.. Lissp::

   #> (defun find-z-word (text)
   #..  (when (re..search '|\b\w*z\w*\b| text)
   #..    (print "found:" (-> '|\b\w*z\w*\b| (re..search text) (.group 0)))))
   >>> # defun
   ... # hissp.macros.._macro_.define
   ... __import__('builtins').globals().update(
   ...   findQzH_zQzH_word=# hissp.macros.._macro_.fun
   ...                     # hissp.macros.._macro_.let
   ...                     (
   ...                      lambda _Qztbhvvkna__lambda=(lambda text:
   ...                                 # when
   ...                                 (lambda b, c: c()if b else())(
   ...                                   __import__('re').search(
   ...                                     '\\b\\w*z\\w*\\b',
   ...                                     text),
   ...                                   (lambda :
   ...                                       print(
   ...                                         ('found:'),
   ...                                         # QzH_QzGT_
   ...                                         __import__('re').search(
   ...                                           '\\b\\w*z\\w*\\b',
   ...                                           text).group(
   ...                                           (0)))
   ...                                   ))
   ...                             ):
   ...                        ((
   ...                           *__import__('itertools').starmap(
   ...                              _Qztbhvvkna__lambda.__setattr__,
   ...                              __import__('builtins').dict(
   ...                                __name__='findQzH_zQzH_word',
   ...                                __qualname__='findQzH_zQzH_word',
   ...                                __code__=_Qztbhvvkna__lambda.__code__.replace(
   ...                                           co_name='findQzH_zQzH_word')).items()),
   ...                           ),
   ...                         _Qztbhvvkna__lambda)  [-1]
   ...                     )())

.. code-block:: REPL

   #> (find-z-word "The quick brown fox jumps over the lazy dog!")
   >>> findQzH_zQzH_word(
   ...   ('The quick brown fox jumps over the lazy dog!'))
   found: lazy

   #> (find-z-word "The quick brown fox jumps over the sleeping dog!")
   >>> findQzH_zQzH_word(
   ...   ('The quick brown fox jumps over the sleeping dog!'))
   ()

Well, at least it's not an error this time.
But this definition duplicates the code for the search; it's not DRY.
It's also duplicating the work of searching when run.
If the search function was pure and memoized
calling it again would actually be OK, performance-wise.
That would be the norm in Haskell,
but in Python you'd have to ask for memoization explicitly
(using `functools.cache`, say).

Performance often isn't that big of a deal.
Unless you're being really egregiously wasteful,
it usually only matters in bottlenecks,
which usually means inside nested loops.
One can get a sense for these things,
but it's easy to waste a lot of programmer time on pointless micro-optimizations not on the critical path.
Programmer time is a lot more expensive than CPU time.
This wasn't always the case, but modern computers are pretty fast.
When it matters, profile first.

The more important consideration here is *readability*.
Sometimes a terse implementation is the clearest name,
but in this case, it's hard to tell if both expressions really are the same.
It's easy to gloss over the regex pattern.
These are fairly short and
it's not too bad when they're on adjacent lines like this,
but if you extract it to a local, you won't have to check:

.. Lissp::

   #> (defun find-z-word (text)
   #..  (let (match (re..search '|\b\w*z\w*\b| text))
   #..    (when match (print "found:" (.group match 0)))))
   >>> # defun
   ... # hissp.macros.._macro_.define
   ... __import__('builtins').globals().update(
   ...   findQzH_zQzH_word=# hissp.macros.._macro_.fun
   ...                     # hissp.macros.._macro_.let
   ...                     (
   ...                      lambda _Qztbhvvkna__lambda=(lambda text:
   ...                                 # let
   ...                                 (
   ...                                  lambda match=__import__('re').search(
   ...                                           '\\b\\w*z\\w*\\b',
   ...                                           text):
   ...                                     # when
   ...                                     (lambda b, c: c()if b else())(
   ...                                       match,
   ...                                       (lambda :
   ...                                           print(
   ...                                             ('found:'),
   ...                                             match.group(
   ...                                               (0)))
   ...                                       ))
   ...                                 )()
   ...                             ):
   ...                        ((
   ...                           *__import__('itertools').starmap(
   ...                              _Qztbhvvkna__lambda.__setattr__,
   ...                              __import__('builtins').dict(
   ...                                __name__='findQzH_zQzH_word',
   ...                                __qualname__='findQzH_zQzH_word',
   ...                                __code__=_Qztbhvvkna__lambda.__code__.replace(
   ...                                           co_name='findQzH_zQzH_word')).items()),
   ...                           ),
   ...                         _Qztbhvvkna__lambda)  [-1]
   ...                     )())

.. code-block:: REPL

   #> (progn (find-z-word "The lazy dog.") (find-z-word "The sleeping dog."))
   >>> # progn
   ... (findQzH_zQzH_word(
   ...    ('The lazy dog.')),
   ...  findQzH_zQzH_word(
   ...    ('The sleeping dog.')))  [-1]
   found: lazy
   ()

Sometimes you want to check if something exists,
and only act in that case.
Short examples like these may feel contrived,
but this pattern does come up enough that languages have special ways of dealing with it.

Hissp, of course, can copy such ways with metaprogramming.

``let-when``
::::::::::::

Let's try one of Clojure's ways.
We want a macro to expand to the previous code.

.. Lissp::

   #> (defmacro let-when (binding : :* body)
   #..  `(let ,binding (when ,!##0 binding ,@body)))
   >>> # defmacro
   ... __import__('builtins').setattr(
   ...   __import__('builtins').globals().get(
   ...     ('_macro_')),
   ...   'letQzH_when',
   ...   # hissp.macros.._macro_.fun
   ...   # hissp.macros.._macro_.let
   ...   (
   ...    lambda _Qztbhvvkna__lambda=(lambda binding, *body:
   ...               (
   ...                 '__main__.._macro_.let',
   ...                 binding,
   ...                 (
   ...                   '__main__.._macro_.when',
   ...                   __import__('operator').itemgetter(
   ...                     (0))(
   ...                     binding),
   ...                   *body,
   ...                   ),
   ...                 )
   ...           ):
   ...      ((
   ...         *__import__('itertools').starmap(
   ...            _Qztbhvvkna__lambda.__setattr__,
   ...            __import__('builtins').dict(
   ...              __name__='letQzH_when',
   ...              __qualname__='_macro_.letQzH_when',
   ...              __code__=_Qztbhvvkna__lambda.__code__.replace(
   ...                         co_name='letQzH_when')).items()),
   ...         ),
   ...       _Qztbhvvkna__lambda)  [-1]
   ...   )())

The Lissp definition of ``find-z-word`` will be a bit nicer this way than before, but just a bit.
Clojure's equivalent is called ``when-let``,
which is, of course, obviously backwards now that we've seen the implementation.
But it does perhaps roll of the tongue a little better,
and may be more consistent with the names of other macros that aren't so simple.

We can confirm the expansion is as expected by examining the Python compilation,
but this macro was defined in terms of two others: `let` and `when`,
and they have expanded too.
The compiler includes comments when it expands a macro so you can tell where this is happening:

.. code-block:: REPL

   #> (defun find-z-word (text)
   #..  (let-when (match (re..search '|\b\w*z\w*\b| text))
   #..    (print "found:" (.group match 0))))
   >>> # defun
   ... # hissp.macros.._macro_.define
   ... __import__('builtins').globals().update(
   ...   findQzH_zQzH_word=# hissp.macros.._macro_.fun
   ...                     # hissp.macros.._macro_.let
   ...                     (
   ...                      lambda _Qztbhvvkna__lambda=(lambda text:
   ...                                 # letQzH_when
   ...                                 # __main__.._macro_.let
   ...                                 (
   ...                                  lambda match=__import__('re').search(
   ...                                           '\\b\\w*z\\w*\\b',
   ...                                           text):
   ...                                     # __main__.._macro_.when
   ...                                     (lambda b, c: c()if b else())(
   ...                                       match,
   ...                                       (lambda :
   ...                                           print(
   ...                                             ('found:'),
   ...                                             match.group(
   ...                                               (0)))
   ...                                       ))
   ...                                 )()
   ...                             ):
   ...                        ((
   ...                           *__import__('itertools').starmap(
   ...                              _Qztbhvvkna__lambda.__setattr__,
   ...                              __import__('builtins').dict(
   ...                                __name__='findQzH_zQzH_word',
   ...                                __qualname__='findQzH_zQzH_word',
   ...                                __code__=_Qztbhvvkna__lambda.__code__.replace(
   ...                                           co_name='findQzH_zQzH_word')).items()),
   ...                           ),
   ...                         _Qztbhvvkna__lambda)  [-1]
   ...                     )())

But the verbosity of the compiled output means there is a lot of code to sort through.
When examining expansions of macros defined in terms of other macros,
it can be helpful to expand only one step.
We can do this using `macroexpand1`:

.. code-block:: REPL

   #> (pprint..pp
   #.. (H#macroexpand1
   #..  '(let-when (match (re..search '|\b\w*z\w*\b| text))
   #..     (print "found:" (.group match 0)))))
   >>> __import__('pprint').pp(
   ...   __import__('hissp').macroexpand1(
   ...     ('letQzH_when',
   ...      ('match',
   ...       ('re..search',
   ...        ('quote',
   ...         '\\b\\w*z\\w*\\b',),
   ...        'text',),),
   ...      ('print',
   ...       "('found:')",
   ...       ('.group',
   ...        'match',
   ...        (0),),),)))
   ('__main__.._macro_.let',
    ('match', ('re..search', ('quote', '\\b\\w*z\\w*\\b'), 'text')),
    ('__main__.._macro_.when',
     'match',
     ('print', "('found:')", ('.group', 'match', 0))))

The pretty-printing makes it a lot easier to read.
This is what we want: a `let` containing a `when`.
It's close to what we wrote ourselves,
plus the :term:`fully-qualified identifier`\ s for extra robustness.
If you're still in a subREPL of some other module,
its `__name__` will appear as the qualifier here instead of ``__main__``.

A `macroexpand` would continue expanding the form as long as it is a macro form,
so the `let` would get expanded as well:

.. code-block:: REPL

   #> (pprint..pp
   #.. (H#macroexpand
   #..  '(let-when (match (re..search '|\b\w*z\w*\b| text))
   #..     (print "found:" (.group match 0)))))
   >>> __import__('pprint').pp(
   ...   __import__('hissp').macroexpand(
   ...     ('letQzH_when',
   ...      ('match',
   ...       ('re..search',
   ...        ('quote',
   ...         '\\b\\w*z\\w*\\b',),
   ...        'text',),),
   ...      ('print',
   ...       "('found:')",
   ...       ('.group',
   ...        'match',
   ...        (0),),),)))
   (('lambda',
     (':', 'match', ('re..search', ('quote', '\\b\\w*z\\w*\\b'), 'text')),
     ('__main__.._macro_.when',
      'match',
      ('print', "('found:')", ('.group', 'match', 0)))),)

The resulting form is no longer a :term:`macro form`,
but it does contain one (the `when`) as a subform.
`macroexpand_all` will expand subforms as well:

.. code-block:: REPL

   #> (pprint..pp
   #.. (H#macroexpand_all
   #..  '(let-when (match (re..search '|\b\w*z\w*\b| text))
   #..     (print "found:" (.group match 0)))))
   >>> __import__('pprint').pp(
   ...   __import__('hissp').macroexpand_all(
   ...     ('letQzH_when',
   ...      ('match',
   ...       ('re..search',
   ...        ('quote',
   ...         '\\b\\w*z\\w*\\b',),
   ...        'text',),),
   ...      ('print',
   ...       "('found:')",
   ...       ('.group',
   ...        'match',
   ...        (0),),),)))
   (('lambda',
     (':', 'match', ('re..search', ('quote', '\\b\\w*z\\w*\\b'), 'text')),
     (('lambda', 'bc', 'c()if b else()'),
      'match',
      ('lambda', ':', ('print', "('found:')", ('.group', 'match', 0))))),)

And now we see the inner `when` has been expanded too.
The resulting Hissp is now defined entirely in terms of `quote` and `lambda` :term:`special form`\ s,
plus ordinary function calls,
and closely corresponds to the compiled Python output we saw before.

We can confirm the new function behaves as before:

.. code-block:: REPL

   #> (progn (find-z-word "The lazy dog.") (find-z-word "The sleeping dog."))
   >>> # progn
   ... (findQzH_zQzH_word(
   ...    ('The lazy dog.')),
   ...  findQzH_zQzH_word(
   ...    ('The sleeping dog.')))  [-1]
   found: lazy
   ()

Anaphors
::::::::

An anaphoric macro can make this even more concise:

.. Lissp::

   #> (defmacro awhen (condition : :* body)
   #..  `(let (,'it ,condition)
   #..     (when ,'it ,@body)))
   >>> # defmacro
   ... __import__('builtins').setattr(
   ...   __import__('builtins').globals().get(
   ...     ('_macro_')),
   ...   'awhen',
   ...   # hissp.macros.._macro_.fun
   ...   # hissp.macros.._macro_.let
   ...   (
   ...    lambda _Qztbhvvkna__lambda=(lambda condition, *body:
   ...               (
   ...                 '__main__.._macro_.let',
   ...                 (
   ...                   'it',
   ...                   condition,
   ...                   ),
   ...                 (
   ...                   '__main__.._macro_.when',
   ...                   'it',
   ...                   *body,
   ...                   ),
   ...                 )
   ...           ):
   ...      ((
   ...         *__import__('itertools').starmap(
   ...            _Qztbhvvkna__lambda.__setattr__,
   ...            __import__('builtins').dict(
   ...              __name__='awhen',
   ...              __qualname__='_macro_.awhen',
   ...              __code__=_Qztbhvvkna__lambda.__code__.replace(
   ...                         co_name='awhen')).items()),
   ...         ),
   ...       _Qztbhvvkna__lambda)  [-1]
   ...   )())


   #> (defun find-z-word (text)
   #..  (awhen (re..search '|\b\w*z\w*\b| text)
   #..    (print "found:" (.group it 0))))
   >>> # defun
   ... # hissp.macros.._macro_.define
   ... __import__('builtins').globals().update(
   ...   findQzH_zQzH_word=# hissp.macros.._macro_.fun
   ...                     # hissp.macros.._macro_.let
   ...                     (
   ...                      lambda _Qztbhvvkna__lambda=(lambda text:
   ...                                 # awhen
   ...                                 # __main__.._macro_.let
   ...                                 (
   ...                                  lambda it=__import__('re').search(
   ...                                           '\\b\\w*z\\w*\\b',
   ...                                           text):
   ...                                     # __main__.._macro_.when
   ...                                     (lambda b, c: c()if b else())(
   ...                                       it,
   ...                                       (lambda :
   ...                                           print(
   ...                                             ('found:'),
   ...                                             it.group(
   ...                                               (0)))
   ...                                       ))
   ...                                 )()
   ...                             ):
   ...                        ((
   ...                           *__import__('itertools').starmap(
   ...                              _Qztbhvvkna__lambda.__setattr__,
   ...                              __import__('builtins').dict(
   ...                                __name__='findQzH_zQzH_word',
   ...                                __qualname__='findQzH_zQzH_word',
   ...                                __code__=_Qztbhvvkna__lambda.__code__.replace(
   ...                                           co_name='findQzH_zQzH_word')).items()),
   ...                           ),
   ...                         _Qztbhvvkna__lambda)  [-1]
   ...                     )())

.. code-block:: REPL

   #> (progn (find-z-word "The lazy dog.") (find-z-word "The sleeping dog."))
   >>> # progn
   ... (findQzH_zQzH_word(
   ...    ('The lazy dog.')),
   ...  findQzH_zQzH_word(
   ...    ('The sleeping dog.')))  [-1]
   found: lazy
   ()

But now you have no choice about the name.
What if you already had an ``it`` in scope?
The way lexical scoping works, the innermost one will shadow the outer,
making the outer one inaccessible.

Can we rename the outer ``it``?
If the outer ``it`` came from another anaphoric macro (like another ``awhen``),
then it's not as simple as changing a symbol.
Being insulated from the details isn't always a good thing!
You'd have to use a ``let`` or something like that to rename the outer ``it`` and avoid the conflict,
but at that point, you might as well use ``let-when`` instead.

Explicit Scoping
::::::::::::::::

Suppose we want to do something else if a match isn't found.
We'd want to use `if-else<ifQzH_else>` instead of `when`.
But we don't have a ``let-if-else`` or an ``aif-else``.
They're not too hard to implement,
but there are many other macros that could use a ``let-`` or anaphoric variant.
Python has a more general solution: the "walrus" operator `:= <python-grammar:assignment_expression>`.

While it's possible to use that in Hissp (like any Python expression),
it would require a :term:`Python injection`,
which is not recommended.
In :term:`standard` Hissp, locals can be considered single assignment;
you can shadow them, but can't reassign.
A walrus operator used inside a lambda creates a local lexically scoped to that lambda.
Nonlocal reads can work, but not nonlocal assignments.
Lambdas are common in macroexpansions,
which makes the walrus hard to use in Hissp.

No matter.
Python didn't have `nonlocal` until version 3.0,
and didn't have the walrus until 3.8.
If you needed nonlocal semantics in Python 2,
the usual workaround would be to use an explicit scope.
We can do the same thing in Hissp:

.. Lissp::

   #> (defun find-z-word (text)
   #..  (let (scope (types..SimpleNamespace))
   #..    (if-else (set@ scope.match (re..search '|\b\w*z\w*\b| text))
   #..      (print "found:" (.group scope.match 0))
   #..      (print "not found"))))
   >>> # defun
   ... # hissp.macros.._macro_.define
   ... __import__('builtins').globals().update(
   ...   findQzH_zQzH_word=# hissp.macros.._macro_.fun
   ...                     # hissp.macros.._macro_.let
   ...                     (
   ...                      lambda _Qztbhvvkna__lambda=(lambda text:
   ...                                 # let
   ...                                 (lambda scope=__import__('types').SimpleNamespace():
   ...                                     # ifQzH_else
   ...                                     (lambda b, c, a: c()if b else a())(
   ...                                       # setQzAT_
   ...                                       # hissp.macros.._macro_.let
   ...                                       (
   ...                                        lambda _Qzald6dagb__value=__import__('re').search(
   ...                                                 '\\b\\w*z\\w*\\b',
   ...                                                 text):
   ...                                          (# hissp.macros.._macro_.define
   ...                                           __import__('builtins').setattr(
   ...                                             scope,
   ...                                             'match',
   ...                                             _Qzald6dagb__value),
   ...                                           _Qzald6dagb__value)  [-1]
   ...                                       )(),
   ...                                       (lambda :
   ...                                           print(
   ...                                             ('found:'),
   ...                                             scope.match.group(
   ...                                               (0)))
   ...                                       ),
   ...                                       (lambda :
   ...                                           print(
   ...                                             ('not found'))
   ...                                       ))
   ...                                 )()
   ...                             ):
   ...                        ((
   ...                           *__import__('itertools').starmap(
   ...                              _Qztbhvvkna__lambda.__setattr__,
   ...                              __import__('builtins').dict(
   ...                                __name__='findQzH_zQzH_word',
   ...                                __qualname__='findQzH_zQzH_word',
   ...                                __code__=_Qztbhvvkna__lambda.__code__.replace(
   ...                                           co_name='findQzH_zQzH_word')).items()),
   ...                           ),
   ...                         _Qztbhvvkna__lambda)  [-1]
   ...                     )())

.. code-block:: REPL

   #> (progn (find-z-word "The lazy dog.") (find-z-word "The sleeping dog."))
   >>> # progn
   ... (findQzH_zQzH_word(
   ...    ('The lazy dog.')),
   ...  findQzH_zQzH_word(
   ...    ('The sleeping dog.')))  [-1]
   found: lazy
   not found

The ``scope`` variable is a normal local with lexical scope,
but its ``.match`` attribute lives in a `types.SimpleNamespace` object,
which is an explicit scope.
Assignments can be written anywhere that has access to that namespace
(including any nested lexical scopes that might appear in a macroexpansion)
and reassignment is possible, unlike locals in standard Hissp.
This is more powerful,
but also potentially more confusing.
Even the Python community discourages the overuse of its walrus operator.
The explicit scope isn't really better than using a local directly here,
but it gives us a more general pattern which we can expand to.

For example:

.. Lissp::

   #> (defmacro it-is\# x `(set@ ,'scope.it ,x))
   >>> # defmacro
   ... __import__('builtins').setattr(
   ...   __import__('builtins').globals().get(
   ...     ('_macro_')),
   ...   'itQzH_isQzHASH_',
   ...   # hissp.macros.._macro_.fun
   ...   # hissp.macros.._macro_.let
   ...   (
   ...    lambda _Qztbhvvkna__lambda=(lambda x:
   ...               (
   ...                 '__main__.._macro_.setQzAT_',
   ...                 'scope.it',
   ...                 x,
   ...                 )
   ...           ):
   ...      ((
   ...         *__import__('itertools').starmap(
   ...            _Qztbhvvkna__lambda.__setattr__,
   ...            __import__('builtins').dict(
   ...              __name__='itQzH_isQzHASH_',
   ...              __qualname__='_macro_.itQzH_isQzHASH_',
   ...              __code__=_Qztbhvvkna__lambda.__code__.replace(
   ...                         co_name='itQzH_isQzHASH_')).items()),
   ...         ),
   ...       _Qztbhvvkna__lambda)  [-1]
   ...   )())


   #> (defun find-z-word (text)
   #..  (let (scope (types..SimpleNamespace))
   #..    (if-else it-is#(re..search '|\b\w*z\w*\b| text)
   #..      (print "found:" (.group scope.it 0))
   #..      (print "not found"))))
   >>> # defun
   ... # hissp.macros.._macro_.define
   ... __import__('builtins').globals().update(
   ...   findQzH_zQzH_word=# hissp.macros.._macro_.fun
   ...                     # hissp.macros.._macro_.let
   ...                     (
   ...                      lambda _Qztbhvvkna__lambda=(lambda text:
   ...                                 # let
   ...                                 (lambda scope=__import__('types').SimpleNamespace():
   ...                                     # ifQzH_else
   ...                                     (lambda b, c, a: c()if b else a())(
   ...                                       # __main__.._macro_.setQzAT_
   ...                                       # hissp.macros.._macro_.let
   ...                                       (
   ...                                        lambda _Qzald6dagb__value=__import__('re').search(
   ...                                                 '\\b\\w*z\\w*\\b',
   ...                                                 text):
   ...                                          (# hissp.macros.._macro_.define
   ...                                           __import__('builtins').setattr(
   ...                                             scope,
   ...                                             'it',
   ...                                             _Qzald6dagb__value),
   ...                                           _Qzald6dagb__value)  [-1]
   ...                                       )(),
   ...                                       (lambda :
   ...                                           print(
   ...                                             ('found:'),
   ...                                             scope.it.group(
   ...                                               (0)))
   ...                                       ),
   ...                                       (lambda :
   ...                                           print(
   ...                                             ('not found'))
   ...                                       ))
   ...                                 )()
   ...                             ):
   ...                        ((
   ...                           *__import__('itertools').starmap(
   ...                              _Qztbhvvkna__lambda.__setattr__,
   ...                              __import__('builtins').dict(
   ...                                __name__='findQzH_zQzH_word',
   ...                                __qualname__='findQzH_zQzH_word',
   ...                                __code__=_Qztbhvvkna__lambda.__code__.replace(
   ...                                           co_name='findQzH_zQzH_word')).items()),
   ...                           ),
   ...                         _Qztbhvvkna__lambda)  [-1]
   ...                     )())

.. code-block:: REPL

   #> (progn (find-z-word "The lazy dog.") (find-z-word "The sleeping dog."))
   >>> # progn
   ... (findQzH_zQzH_word(
   ...    ('The lazy dog.')),
   ...  findQzH_zQzH_word(
   ...    ('The sleeping dog.')))  [-1]
   found: lazy
   not found

We hardcoded the ``scope`` anaphor in the ``it-is#`` definition above.


Because the name ``scope`` is always the same,
we could also reduce the `let` form to a tag with a single argument (its body):

.. Lissp::

   #> (defmacro scope\# (expr)
   #..  `(let (,'scope (types..SimpleNamespace))
   #..     ,expr))
   >>> # defmacro
   ... __import__('builtins').setattr(
   ...   __import__('builtins').globals().get(
   ...     ('_macro_')),
   ...   'scopeQzHASH_',
   ...   # hissp.macros.._macro_.fun
   ...   # hissp.macros.._macro_.let
   ...   (
   ...    lambda _Qztbhvvkna__lambda=(lambda expr:
   ...               (
   ...                 '__main__.._macro_.let',
   ...                 (
   ...                   'scope',
   ...                   (
   ...                     'types..SimpleNamespace',
   ...                     ),
   ...                   ),
   ...                 expr,
   ...                 )
   ...           ):
   ...      ((
   ...         *__import__('itertools').starmap(
   ...            _Qztbhvvkna__lambda.__setattr__,
   ...            __import__('builtins').dict(
   ...              __name__='scopeQzHASH_',
   ...              __qualname__='_macro_.scopeQzHASH_',
   ...              __code__=_Qztbhvvkna__lambda.__code__.replace(
   ...                         co_name='scopeQzHASH_')).items()),
   ...         ),
   ...       _Qztbhvvkna__lambda)  [-1]
   ...   )())


   #> (defun find-z-word (text)
   #..  scope#(if-else it-is#(re..search '|\b\w*z\w*\b| text)
   #..          (print "found:" (.group scope.it 0))
   #..          (print "not found")))
   >>> # defun
   ... # hissp.macros.._macro_.define
   ... __import__('builtins').globals().update(
   ...   findQzH_zQzH_word=# hissp.macros.._macro_.fun
   ...                     # hissp.macros.._macro_.let
   ...                     (
   ...                      lambda _Qztbhvvkna__lambda=(lambda text:
   ...                                 # __main__.._macro_.let
   ...                                 (lambda scope=__import__('types').SimpleNamespace():
   ...                                     # ifQzH_else
   ...                                     (lambda b, c, a: c()if b else a())(
   ...                                       # __main__.._macro_.setQzAT_
   ...                                       # hissp.macros.._macro_.let
   ...                                       (
   ...                                        lambda _Qzald6dagb__value=__import__('re').search(
   ...                                                 '\\b\\w*z\\w*\\b',
   ...                                                 text):
   ...                                          (# hissp.macros.._macro_.define
   ...                                           __import__('builtins').setattr(
   ...                                             scope,
   ...                                             'it',
   ...                                             _Qzald6dagb__value),
   ...                                           _Qzald6dagb__value)  [-1]
   ...                                       )(),
   ...                                       (lambda :
   ...                                           print(
   ...                                             ('found:'),
   ...                                             scope.it.group(
   ...                                               (0)))
   ...                                       ),
   ...                                       (lambda :
   ...                                           print(
   ...                                             ('not found'))
   ...                                       ))
   ...                                 )()
   ...                             ):
   ...                        ((
   ...                           *__import__('itertools').starmap(
   ...                              _Qztbhvvkna__lambda.__setattr__,
   ...                              __import__('builtins').dict(
   ...                                __name__='findQzH_zQzH_word',
   ...                                __qualname__='findQzH_zQzH_word',
   ...                                __code__=_Qztbhvvkna__lambda.__code__.replace(
   ...                                           co_name='findQzH_zQzH_word')).items()),
   ...                           ),
   ...                         _Qztbhvvkna__lambda)  [-1]
   ...                     )())

.. code-block:: REPL

   #> (progn (find-z-word "The lazy dog.") (find-z-word "The sleeping dog."))
   >>> # progn
   ... (findQzH_zQzH_word(
   ...    ('The lazy dog.')),
   ...  findQzH_zQzH_word(
   ...    ('The sleeping dog.')))  [-1]
   found: lazy
   not found

This pair of tags can function as many common anaphoric-variant macros
that only need a single anaphor,
including ``awhen``, ``acond``, ``aand``, etc.

``the#``
::::::::

The ``it-is#`` tag above only assigns to ``scope.it``,
which is still not as general as Python's walrus.
Rather than creating a new tag for each name we might want,
we could generalize this to any name with a binary tag that takes the identifier as its first argument.

But we have an even better option.
``it-is#`` only makes sense inside of ``scope#``'s first argument,
which means we can use a code-walking metaprogram to rewrite the expression.
We could use control words instead of tags, for example.
Many other other macros use control words (not to mention lambdas and normal call syntax),
and so we'd want to avoid interfering with those uses.
Perhaps by using a naming convention
(ending in an ``=`` character, say).

This suggests an even better alternative,
at least in Lissp: :term:`kwarg token`\ s.
They're already paired with an argument,
so we won't have to figure that part out while code walking.
They have a name we can use for the assignment.
They won't interfere with control words.
`Kwarg` objects are really only meant for use at :term:`read time`,
but we can write tag metaprograms, which run at read time.
Nested tags using them directly will be evaluated first,
so those won't interfere either.
Let's try that.

.. Lissp::

   #> (defmacro the\# (expr)
   #..  `(let (,'the (types..SimpleNamespace))
   #..     ,(kwarg->set@ expr)))
   >>> # defmacro
   ... __import__('builtins').setattr(
   ...   __import__('builtins').globals().get(
   ...     ('_macro_')),
   ...   'theQzHASH_',
   ...   # hissp.macros.._macro_.fun
   ...   # hissp.macros.._macro_.let
   ...   (
   ...    lambda _Qztbhvvkna__lambda=(lambda expr:
   ...               (
   ...                 '__main__.._macro_.let',
   ...                 (
   ...                   'the',
   ...                   (
   ...                     'types..SimpleNamespace',
   ...                     ),
   ...                   ),
   ...                 kwargQzH_QzGT_setQzAT_(
   ...                   expr),
   ...                 )
   ...           ):
   ...      ((
   ...         *__import__('itertools').starmap(
   ...            _Qztbhvvkna__lambda.__setattr__,
   ...            __import__('builtins').dict(
   ...              __name__='theQzHASH_',
   ...              __qualname__='_macro_.theQzHASH_',
   ...              __code__=_Qztbhvvkna__lambda.__code__.replace(
   ...                         co_name='theQzHASH_')).items()),
   ...         ),
   ...       _Qztbhvvkna__lambda)  [-1]
   ...   )())

This is basically our ``scope#`` tag,
plus some design by wishful thinking again.
We still need to define the helper function to do the actual rewrite:

.. Lissp::

   #> (defun kwarg->set@ (expr)
   #..  (cond (isinstance expr hissp.reader..Kwarg) `(set@ ,(.format "the.{}" (H#munge expr.k))
   #..                                                     ,expr.v)
   #..        (H#is_node expr) `(,@(map kwarg->set@ expr))
   #..        :else expr))
   >>> # defun
   ... # hissp.macros.._macro_.define
   ... __import__('builtins').globals().update(
   ...   kwargQzH_QzGT_setQzAT_=# hissp.macros.._macro_.fun
   ...                          # hissp.macros.._macro_.let
   ...                          (
   ...                           lambda _Qztbhvvkna__lambda=(lambda expr:
   ...                                      # cond
   ...                                      (lambda x0, x1, x2, x3, x4, x5:
   ...                                               x1() if x0
   ...                                          else x3() if x2()
   ...                                          else x5() if x4()
   ...                                          else ()
   ...                                      )(
   ...                                        isinstance(
   ...                                          expr,
   ...                                          __import__('hissp.reader',fromlist='*').Kwarg),
   ...                                        (lambda :
   ...                                            (
   ...                                              '__main__.._macro_.setQzAT_',
   ...                                              ('the.{}').format(
   ...                                                __import__('hissp').munge(
   ...                                                  expr.k)),
   ...                                              expr.v,
   ...                                              )
   ...                                        ),
   ...                                        (lambda :
   ...                                            __import__('hissp').is_node(
   ...                                              expr)
   ...                                        ),
   ...                                        (lambda :
   ...                                            (
   ...                                              *map(
   ...                                                 kwargQzH_QzGT_setQzAT_,
   ...                                                 expr),
   ...                                              )
   ...                                        ),
   ...                                        (lambda : ':else'),
   ...                                        (lambda : expr))
   ...                                  ):
   ...                             ((
   ...                                *__import__('itertools').starmap(
   ...                                   _Qztbhvvkna__lambda.__setattr__,
   ...                                   __import__('builtins').dict(
   ...                                     __name__='kwargQzH_QzGT_setQzAT_',
   ...                                     __qualname__='kwargQzH_QzGT_setQzAT_',
   ...                                     __code__=_Qztbhvvkna__lambda.__code__.replace(
   ...                                                co_name='kwargQzH_QzGT_setQzAT_')).items()),
   ...                                ),
   ...                              _Qztbhvvkna__lambda)  [-1]
   ...                          )())

Syntax trees are recursive data structures.
We saw this kind of recursive approach before with ``flatten``.
But this isn't just for reading the tree. It rebuilds it.
There are only three cases to worry about:
if it's a `Kwarg` object, we substitute the `set@<setQzAT_>` expression;
if it `is_node`, we recurse and reconstruct the tuple;
else it's just an atom and we give it back.

.. Lissp::

   #> (defun find-z-word (text)
   #..  the#(if-else match=(re..search '|\b\w*z\w*\b| text)
   #..        (print "found:" (.group the.match 0))
   #..        (print "not found")))
   >>> # defun
   ... # hissp.macros.._macro_.define
   ... __import__('builtins').globals().update(
   ...   findQzH_zQzH_word=# hissp.macros.._macro_.fun
   ...                     # hissp.macros.._macro_.let
   ...                     (
   ...                      lambda _Qztbhvvkna__lambda=(lambda text:
   ...                                 # __main__.._macro_.let
   ...                                 (lambda the=__import__('types').SimpleNamespace():
   ...                                     # ifQzH_else
   ...                                     (lambda b, c, a: c()if b else a())(
   ...                                       # __main__.._macro_.setQzAT_
   ...                                       # hissp.macros.._macro_.let
   ...                                       (
   ...                                        lambda _Qzald6dagb__value=__import__('re').search(
   ...                                                 '\\b\\w*z\\w*\\b',
   ...                                                 text):
   ...                                          (# hissp.macros.._macro_.define
   ...                                           __import__('builtins').setattr(
   ...                                             the,
   ...                                             'match',
   ...                                             _Qzald6dagb__value),
   ...                                           _Qzald6dagb__value)  [-1]
   ...                                       )(),
   ...                                       (lambda :
   ...                                           print(
   ...                                             ('found:'),
   ...                                             the.match.group(
   ...                                               (0)))
   ...                                       ),
   ...                                       (lambda :
   ...                                           print(
   ...                                             ('not found'))
   ...                                       ))
   ...                                 )()
   ...                             ):
   ...                        ((
   ...                           *__import__('itertools').starmap(
   ...                              _Qztbhvvkna__lambda.__setattr__,
   ...                              __import__('builtins').dict(
   ...                                __name__='findQzH_zQzH_word',
   ...                                __qualname__='findQzH_zQzH_word',
   ...                                __code__=_Qztbhvvkna__lambda.__code__.replace(
   ...                                           co_name='findQzH_zQzH_word')).items()),
   ...                           ),
   ...                         _Qztbhvvkna__lambda)  [-1]
   ...                     )())

.. code-block:: REPL

   #> (progn (find-z-word "The lazy dog.") (find-z-word "The sleeping dog."))
   >>> # progn
   ... (findQzH_zQzH_word(
   ...    ('The lazy dog.')),
   ...  findQzH_zQzH_word(
   ...    ('The sleeping dog.')))  [-1]
   found: lazy
   not found

Very powerful.
Also easy to (ab)use.
You can save the result of any subexpression to the namespace.
You can reassign names you've already used.
It's a lot like the walrus, but the tag (``the#``) explicitly delimits the scope.

There was some reluctance around adding the walrus to Python.
But it obviates the need for many anaphoric macros by itself.
And now Hissp has that capability too.

Actually, the bundled `my#<myQzHASH_>` tag does what ``the#`` can and more,
but the implementation is a bit more involved because of the additional features.

Pre-Expansion
=============

We saw a simple example of recursive code walking in `Macros Can Read Code Too`_,
using ``flatten``,
which ignores the tree structure and only looks for a particular kind of atom.
We saw a less simple example in `the#`_,
which replaced a kind of atom with something else,
while keeping the tree structure.

More advanced code-walking macros pre-expand macros in their body
in order to operate on the resulting :term:`special form`\ s.
This works even when the macros in the body are not known beforehand.

Lazy Polar Coordinates
::::::::::::::::::::::

Suppose we want to express a complex number in polar form.
We could easily make a separate function that computes the cartesian form from polar inputs.
(For custom classes,
one could similarly make an alternate constructor using `classmethod`.)

>>> import math
>>> def polar(r, theta):
...    return complex(r * math.cos(theta), r * math.sin(theta))
>>> print(*[polar(1, math.tau/4 * quarters) for quarters in range(4)])
(1+0j) (6.123233995736766e-17+1j) (-1+1.2246467991473532e-16j) (-1.8369701987210297e-16-1j)

There's some unavoidable imprecision in the float calculations approximating irrational numbers,
but notice the noisy-looking numbers are close to zero.
I'll be using `round` liberally to make the remaining examples easier to read.

.. TODO: kwarg "alone"? kwonly? kwargs alone? kwarg names alone?

But kwarg alone names should be enough to disambiguate the cases;
we don't need separate functions.
Suppose we want a Python signature like ::

   >>> import builtins
   >>> def complex(real=r*math.cos(theta), imag=r*math.sin(theta), *, r, theta):
   ...     return builtins.complex(real, imag)
   Traceback (most recent call last):
      ...
   NameError: name 'r' is not defined

Alas, this doesn't work.
Function parameters can have default values in Python,
but they are computed at *definition time*, not call time.
Although it would be useful in cases where there is more than one way to express a value,
default expressions cannot depend on the values of the other arguments.
One would instead have to use some other default value (`None` being a common choice)
and figure out what to do in the function body.

Doing this kind of thing imperatively can be pretty tricky (Try it!),
but there is a fairly straightforward approach that can work in general and that's *laziness*.
Pull. Don't push:

>>> class ComplexArgs:
...     def real(self):
...         return self.r() * math.cos(self.theta())
...     def imag(self):
...         return self.r() * math.sin(self.theta())
>>> def complex(**kwargs):
...     args = ComplexArgs()
...     # The v=v is a workaround for Python's late-binding closures.
...     # Remember, defaults are computed at definition time.
...     vars(args).update({k: lambda v=v: v for k, v in kwargs.items()})
...     # Rounding to 4 so your eyes don't glaze over.
...     return builtins.complex(round(args.real(), 4), round(args.imag(), 4))
>>> complex(real=3, imag=4)
(3+4j)
>>> complex(r=2**.5, theta=math.radians(45))
(1+1j)
>>> complex(r=1, theta=math.radians(60))
(0.5+0.866j)

Not a single `if <if>`! It just works.
It's not a drop-in replacement though,
which makes shadowing the builtin name like this inadvisable.
Unlike the builtin,
args here can only be passed in by name,
and the valid ones don't even show up in the signature.
We could put that in the docstring.
A name like ``**real_imag_r_theta`` instead of ``**kwargs`` is also a possibility.

This pattern generalizes.
We could compute both directions given either coordinate pair in basically the same way:

>>> def r4(x): return round(x(), 4)  # Note the x() call.
>>> class CoordinatesArgs:
...     def x(self):
...         return self.r() * math.cos(self.theta())
...     def y(self):
...         return self.r() * math.sin(self.theta())
...     def r(self):
...         return (self.x()**2 + self.y()**2)**.5
...     def theta(self):
...         return math.atan2(self.y(), self.x())
>>> def coordinates(**kwargs):
...     args = CoordinatesArgs()
...     vars(args).update({k: lambda v=v: v for k, v in kwargs.items()})
...     return dict(Cartesian=(r4(args.x), r4(args.y)), polar=(r4(args.r), r4(args.theta)))
>>> coordinates(x=3, y=4)  # 3-4-5 Pythagorean triple.
{'Cartesian': (3, 4), 'polar': (5.0, 0.9273)}
>>> coordinates(r=5, theta=0.9273)  # Other direction.
{'Cartesian': (3.0, 4.0), 'polar': (5, 0.9273)}
>>> coordinates(x=1, y=1)
{'Cartesian': (1, 1), 'polar': (1.4142, 0.7854)}
>>> coordinates(r=2**.5, theta=math.radians(45))  # Right isosceles.
{'Cartesian': (1.0, 1.0), 'polar': (1.4142, 0.7854)}
>>> coordinates(x=.5, y=3**.5/2)
{'Cartesian': (0.5, 0.866), 'polar': (1.0, 1.0472)}
>>> coordinates(r=1, theta=math.radians(60))  # 30-60-90 triangle.
{'Cartesian': (0.5, 0.866), 'polar': (1, 1.0472)}

In Python, one might be inclined to put the ``.update`` line in a ``def __init__(**kwargs):``
method in a common ``Args`` base class.

One potential issue with lazy arguments like this is (for example)
what happens if you accidentally pass in ``r`` and ``y`` instead of ``x`` and ``y``?
You know how to keyboard interrupt, right?

>>> coordinates(r=1, y=1)
Traceback (most recent call last):
   ...
RecursionError: maximum recursion depth exceeded

Never mind. We blew the stack.

Using an arguments class was convenient in Python,
and it's not a *bad* design when using mutable namespaces,
but a single namespace only populated inside the body would suffice,
and this allows us to use a lexical closure rather than an explicit
``self`` argument.
In the next example,
notice how ``self`` is replaced with the ``my`` anaphor.

There's an additional name this time:
``theta`` is defined in terms of ``θ``, so they refer to the same thing.
The lookup chain means you can pass it in with either name and it will still work.

.. Lissp::

   #> (defun coordinates (: :** kwargs)
   #..  my#(progn
   #..      x=O#(mul (my.r) (math..cos (my.theta)))
   #..      y=O#(mul (my.r) (math..sin (my.theta)))
   #..      r=O#|(my.x()**2 + my.y()**2)**.5|
   #..      θ=O#(math..atan2 (my.y) (my.x))
   #..      theta=O#(my.θ)
   #..      (-> my vars (.update (i#starmap XY#(@ X (lambda (: v Y) v))
   #..                                      (.items kwargs))))
   #..      (dict : cartesian `(,(r4 my.x) ,(r4 my.y))
   #..              polar `(,(r4 my.r) ,(r4 my.theta)))))
   >>> # defun
   ... # hissp.macros.._macro_.define
   ... __import__('builtins').globals().update(
   ...   coordinates=# hissp.macros.._macro_.fun
   ...               # hissp.macros.._macro_.let
   ...               (
   ...                lambda _Qzg4t3gdjc__lambda=(lambda **kwargs:
   ...                           # hissp.macros.._macro_.let
   ...                           (lambda my=__import__('types').SimpleNamespace():
   ...                               # progn
   ...                               (# hissp.macros.._macro_.setQzAT_
   ...                                # hissp.macros.._macro_.let
   ...                                (
   ...                                 lambda _Qzfww2t2f4__value=(lambda :
   ...                                            mul(
   ...                                              my.r(),
   ...                                              __import__('math').cos(
   ...                                                my.theta()))
   ...                                        ):
   ...                                   (# hissp.macros.._macro_.define
   ...                                    __import__('builtins').setattr(
   ...                                      my,
   ...                                      'x',
   ...                                      _Qzfww2t2f4__value),
   ...                                    _Qzfww2t2f4__value)  [-1]
   ...                                )(),
   ...                                # hissp.macros.._macro_.setQzAT_
   ...                                # hissp.macros.._macro_.let
   ...                                (
   ...                                 lambda _Qzfww2t2f4__value=(lambda :
   ...                                            mul(
   ...                                              my.r(),
   ...                                              __import__('math').sin(
   ...                                                my.theta()))
   ...                                        ):
   ...                                   (# hissp.macros.._macro_.define
   ...                                    __import__('builtins').setattr(
   ...                                      my,
   ...                                      'y',
   ...                                      _Qzfww2t2f4__value),
   ...                                    _Qzfww2t2f4__value)  [-1]
   ...                                )(),
   ...                                # hissp.macros.._macro_.setQzAT_
   ...                                # hissp.macros.._macro_.let
   ...                                (lambda _Qzfww2t2f4__value=(lambda : (my.x()**2 + my.y()**2)**.5):
   ...                                   (# hissp.macros.._macro_.define
   ...                                    __import__('builtins').setattr(
   ...                                      my,
   ...                                      'r',
   ...                                      _Qzfww2t2f4__value),
   ...                                    _Qzfww2t2f4__value)  [-1]
   ...                                )(),
   ...                                # hissp.macros.._macro_.setQzAT_
   ...                                # hissp.macros.._macro_.let
   ...                                (
   ...                                 lambda _Qzfww2t2f4__value=(lambda :
   ...                                            __import__('math').atan2(
   ...                                              my.y(),
   ...                                              my.x())
   ...                                        ):
   ...                                   (# hissp.macros.._macro_.define
   ...                                    __import__('builtins').setattr(
   ...                                      my,
   ...                                      'θ',
   ...                                      _Qzfww2t2f4__value),
   ...                                    _Qzfww2t2f4__value)  [-1]
   ...                                )(),
   ...                                # hissp.macros.._macro_.setQzAT_
   ...                                # hissp.macros.._macro_.let
   ...                                (lambda _Qzfww2t2f4__value=(lambda : my.θ()):
   ...                                   (# hissp.macros.._macro_.define
   ...                                    __import__('builtins').setattr(
   ...                                      my,
   ...                                      'theta',
   ...                                      _Qzfww2t2f4__value),
   ...                                    _Qzfww2t2f4__value)  [-1]
   ...                                )(),
   ...                                # QzH_QzGT_
   ...                                vars(
   ...                                  my).update(
   ...                                  __import__('itertools').starmap(
   ...                                    (lambda X, Y:
   ...                                        # QzAT_
   ...                                        (lambda *xs: [*xs])(
   ...                                          X,
   ...                                          (lambda v=Y: v))
   ...                                    ),
   ...                                    kwargs.items())),
   ...                                dict(
   ...                                  cartesian=(
   ...                                              r4(
   ...                                                my.x),
   ...                                              r4(
   ...                                                my.y),
   ...                                              ),
   ...                                  polar=(
   ...                                          r4(
   ...                                            my.r),
   ...                                          r4(
   ...                                            my.theta),
   ...                                          )))  [-1]
   ...                           )()
   ...                       ):
   ...                  ((
   ...                     *__import__('itertools').starmap(
   ...                        _Qzg4t3gdjc__lambda.__setattr__,
   ...                        __import__('builtins').dict(
   ...                          __name__='coordinates',
   ...                          __qualname__='coordinates',
   ...                          __code__=_Qzg4t3gdjc__lambda.__code__.replace(
   ...                                     co_name='coordinates')).items()),
   ...                     ),
   ...                   _Qzg4t3gdjc__lambda)  [-1]
   ...               )())

Notice we're using ``r4`` again.
Remember, it's possible to inject Python in a Lissp REPL,
not that this one is hard to translate.
But you don't need to round at all to follow along.
Don't forget to call the thunks though.

.. code-block:: REPL

   #> (coordinates : r |2**.5|  θ math..radians#45)
   >>> coordinates(
   ...   r=2**.5,
   ...   θ=(0.7853981633974483))
   {'cartesian': (1.0, 1.0), 'polar': (1.4142, 0.7854)}

   #> (coordinates : x 1  y 1)
   >>> coordinates(
   ...   x=(1),
   ...   y=(1))
   {'cartesian': (1, 1), 'polar': (1.4142, 0.7854)}

   #> (coordinates : r 1  theta math..radians#60)
   >>> coordinates(
   ...   r=(1),
   ...   theta=(1.0471975511965976))
   {'cartesian': (0.5, 0.866), 'polar': (1, 1.0472)}

Now that we have a design pattern,
we should be able to make it a macro.
There's a lot of tag magic here,
but remember those run at :term:`read time`,
so macros can't have tags in their expansions,
but they can expand to the same results
(which you can sometimes produce using tags).

The syntax we're going for would be something like this:

.. Lissp::

   (defun-lazy complex (real (mul (lazy.r) (math..cos (lazy.theta))
                        imag (mul (lazy.r) (math..sin (lazy.theta))))
     (builtins..complex real imag)

We can implement the macro for it like this:

.. Lissp::

   (defmacro defun-lazy (qualname params : :* body)
     `(defun ,qualname (: :** ,'kwargs)
        (let (,'lazy (types..SimpleNamespace))
          (doto (vars ,'lazy)
            (.update : ,@chain#(let (iparams (iter params))
                                 (zip iparams (map X#`O#,X iparams) : strict 1)))
            (.update (i#starmap (lambda ($#k $#v)
                                  (@ $#k (lambda (: $#v $#v) $#v)))
                                (.items ,'kwargs))))
          ,@body)))

That's a relatively long one.
Let's break it down.
The new ``defun-lazy`` macro will write a `defun`.
The ``qualname`` arg passes through unchanged.
``defun``'s params are hardcoded to just ``**kwargs``,
which is an :term:`anaphor`.
(We haven't seen the ``params`` argument used yet.)

Next is our second anaphor: the ``lazy`` namespace.
With ``lazy`` in the lexical scope (of the `let` body)
we ``.update`` the namespace, first with the ``params`` argument.
Its defaults need to be wrapped in a `lambda` :term:`special form` to delay evaluation
(but not their names).
That's the laziness.

The second ``.update`` is with the ``kwargs``,
so keyword arguments can override the defaults.
These also need to be wrapped in lambdas so we can call them regardless
of overrides in the body,
but because the wrapping happens at run time,
it has to be written differently.
Notice the late-binding closure workaround again.

For simplicity,
I didn't include docstring handling.
Let's add that now.

.. Lissp::

   #> (defmacro defun-lazy (qualname params : maybe_docstring ()  :* body)
   #..  `(defun ,qualname (: :** ,'kwargs)
   #..     ,@(when (H#is_hissp_string maybe_docstring)
   #..         `(,maybe_docstring))
   #..     (let (,'lazy (types..SimpleNamespace))
   #..       (doto (vars ,'lazy)
   #..         (.update : ,@chain#(let (iparams (iter params))
   #..                              (zip iparams (map X#`O#,X iparams) : strict 1)))
   #..         (.update (i#starmap (lambda ($#k $#v)
   #..                               (@ $#k (lambda (: $#v $#v) $#v)))
   #..                             (.items ,'kwargs))))
   #..       ,@(unless (H#is_hissp_string maybe_docstring)
   #..           `(,maybe_docstring))
   #..       ,@body)))
   >>> # defmacro
   ... __import__('builtins').setattr(
   ...   __import__('builtins').globals().get(
   ...     ('_macro_')),
   ...   'defunQzH_lazy',
   ...   # hissp.macros.._macro_.fun
   ...   # hissp.macros.._macro_.let
   ...   (
   ...    lambda _Qzgibeefhr__lambda=(
   ...            lambda qualname,
   ...                   params,
   ...                   maybe_docstring=(),
   ...                   *body:
   ...               (
   ...                 '__main__.._macro_.defun',
   ...                 qualname,
   ...                 (
   ...                   ':',
   ...                   ':**',
   ...                   'kwargs',
   ...                   ),
   ...                 *# when
   ...                  (lambda b, c: c()if b else())(
   ...                    __import__('hissp').is_hissp_string(
   ...                      maybe_docstring),
   ...                    (lambda :
   ...                        (
   ...                          maybe_docstring,
   ...                          )
   ...                    )),
   ...                 (
   ...                   '__main__.._macro_.let',
   ...                   (
   ...                     'lazy',
   ...                     (
   ...                       'types..SimpleNamespace',
   ...                       ),
   ...                     ),
   ...                   (
   ...                     '__main__.._macro_.doto',
   ...                     (
   ...                       'builtins..vars',
   ...                       'lazy',
   ...                       ),
   ...                     (
   ...                       '.update',
   ...                       ':',
   ...                       *__import__('itertools').chain.from_iterable(
   ...                          # let
   ...                          (
   ...                           lambda iparams=iter(
   ...                                    params):
   ...                              zip(
   ...                                iparams,
   ...                                map(
   ...                                  (lambda X:
   ...                                      (
   ...                                        'lambda',
   ...                                        ':',
   ...                                        X,
   ...                                        )
   ...                                  ),
   ...                                  iparams),
   ...                                strict=(1))
   ...                          )()),
   ...                       ),
   ...                     (
   ...                       '.update',
   ...                       (
   ...                         'itertools..starmap',
   ...                         (
   ...                           'lambda',
   ...                           (
   ...                             '_Qz6xuvarhd__k',
   ...                             '_Qz6xuvarhd__v',
   ...                             ),
   ...                           (
   ...                             '__main__.._macro_.QzAT_',
   ...                             '_Qz6xuvarhd__k',
   ...                             (
   ...                               'lambda',
   ...                               (
   ...                                 ':',
   ...                                 '_Qz6xuvarhd__v',
   ...                                 '_Qz6xuvarhd__v',
   ...                                 ),
   ...                               '_Qz6xuvarhd__v',
   ...                               ),
   ...                             ),
   ...                           ),
   ...                         (
   ...                           '.items',
   ...                           'kwargs',
   ...                           ),
   ...                         ),
   ...                       ),
   ...                     ),
   ...                   *# unless
   ...                    (lambda b, a: ()if b else a())(
   ...                      __import__('hissp').is_hissp_string(
   ...                        maybe_docstring),
   ...                      (lambda :
   ...                          (
   ...                            maybe_docstring,
   ...                            )
   ...                      )),
   ...                   *body,
   ...                   ),
   ...                 )
   ...           ):
   ...      ((
   ...         *__import__('itertools').starmap(
   ...            _Qzgibeefhr__lambda.__setattr__,
   ...            __import__('builtins').dict(
   ...              __name__='defunQzH_lazy',
   ...              __qualname__='_macro_.defunQzH_lazy',
   ...              __code__=_Qzgibeefhr__lambda.__code__.replace(
   ...                         co_name='defunQzH_lazy')).items()),
   ...         ),
   ...       _Qzgibeefhr__lambda)  [-1]
   ...   )())

``maybe-docstring`` is our first optional argument.
It could be the docstring,
in which case, ``defun`` expects it immediately after its params.
`is_hissp_string` is a metaprogramming helper function.
Using it in a macro definition doesn't violate the :term:`standalone property`,
because it will only be used at compile time.
``maybe-docstring`` appears once again before ``,@body``.
The remaining ``,@body`` could be empty,
so ``maybe-docstring`` could be the whole thing.
If nothing optional was provided,
the `defun` return value will default to ``()``,
which is consistent with the ``lambda`` :term:`special form`.
If ``maybe-docstring`` was provided and it's not a :term:`Hissp string`,
then it's treated as the first body form.

Lisps differ on what to do if the only body form is a string literal.
In Emacs Lisp, it's both the docstring and the return value.
(We'd get that behavior without the `unless`,
but the expansion would have the string written twice.)
In Common Lisp, it's the return value, and there is no docstring.
Clojure puts the docstring before the params
(which makes more sense in Clojure because of arity overloads)
so it would have to be the return value.
Python must disambiguate with `return`.
The way we've written it here,
the string would be the docstring and
the return value would be the default ``()``,
which is the same way `fun` and its derivatives work.
If you want to return a string literal for some reason,
you could add a single body form before it,
and it need not be the docstring (could be `None` or `... <Ellipsis>` etc.)
Wrapping it in an `ors` so it isn't recognized as a string literal would also work.

.. Lissp::

   #> (defun-lazy coordinates (x (mul (lazy.r) (math..cos (lazy.theta)))
   #..                         y (mul (lazy.r) (math..sin (lazy.theta)))
   #..                         r |(lazy.x()**2 + lazy.y()**2)**.5|
   #..                         θ (math..atan2 (lazy.y) (lazy.x))
   #..                         theta (lazy.θ))
   #..  (dict : cartesian `(,(r4 lazy.x) ,(r4 lazy.y))
   #..        polar `(,(r4 lazy.r) ,(r4 lazy.theta))))
   >>> # defunQzH_lazy
   ... # __main__.._macro_.defun
   ... # hissp.macros.._macro_.define
   ... __import__('builtins').globals().update(
   ...   coordinates=# hissp.macros.._macro_.fun
   ...               # hissp.macros.._macro_.let
   ...               (
   ...                lambda _Qzg4t3gdjc__lambda=(lambda **kwargs:
   ...                           # __main__.._macro_.let
   ...                           (lambda lazy=__import__('types').SimpleNamespace():
   ...                              (# __main__.._macro_.doto
   ...                               (
   ...                                lambda _Qzqinvrqwa__self=__import__('builtins').vars(
   ...                                         lazy):
   ...                                  (_Qzqinvrqwa__self.update(
   ...                                     x=(lambda :
   ...                                           mul(
   ...                                             lazy.r(),
   ...                                             __import__('math').cos(
   ...                                               lazy.theta()))
   ...                                       ),
   ...                                     y=(lambda :
   ...                                           mul(
   ...                                             lazy.r(),
   ...                                             __import__('math').sin(
   ...                                               lazy.theta()))
   ...                                       ),
   ...                                     r=(lambda : (lazy.x()**2 + lazy.y()**2)**.5),
   ...                                     θ=(lambda :
   ...                                           __import__('math').atan2(
   ...                                             lazy.y(),
   ...                                             lazy.x())
   ...                                       ),
   ...                                     theta=(lambda : lazy.θ())),
   ...                                   _Qzqinvrqwa__self.update(
   ...                                     __import__('itertools').starmap(
   ...                                       (lambda _Qz6xuvarhd__k, _Qz6xuvarhd__v:
   ...                                           # __main__.._macro_.QzAT_
   ...                                           (lambda *xs: [*xs])(
   ...                                             _Qz6xuvarhd__k,
   ...                                             (lambda _Qz6xuvarhd__v=_Qz6xuvarhd__v: _Qz6xuvarhd__v))
   ...                                       ),
   ...                                       kwargs.items())),
   ...                                   _Qzqinvrqwa__self)  [-1]
   ...                               )(),
   ...                               dict(
   ...                                 cartesian=(
   ...                                             r4(
   ...                                               lazy.x),
   ...                                             r4(
   ...                                               lazy.y),
   ...                                             ),
   ...                                 polar=(
   ...                                         r4(
   ...                                           lazy.r),
   ...                                         r4(
   ...                                           lazy.theta),
   ...                                         )))  [-1]
   ...                           )()
   ...                       ):
   ...                  ((
   ...                     *__import__('itertools').starmap(
   ...                        _Qzg4t3gdjc__lambda.__setattr__,
   ...                        __import__('builtins').dict(
   ...                          __name__='coordinates',
   ...                          __qualname__='coordinates',
   ...                          __code__=_Qzg4t3gdjc__lambda.__code__.replace(
   ...                                     co_name='coordinates')).items()),
   ...                     ),
   ...                   _Qzg4t3gdjc__lambda)  [-1]
   ...               )())

.. code-block:: REPL

   #> (coordinates : r |2**.5|  θ math..radians#45)
   >>> coordinates(
   ...   r=2**.5,
   ...   θ=(0.7853981633974483))
   {'cartesian': (1.0, 1.0), 'polar': (1.4142, 0.7854)}

   #> (coordinates : x 1  y 1)
   >>> coordinates(
   ...   x=(1),
   ...   y=(1))
   {'cartesian': (1, 1), 'polar': (1.4142, 0.7854)}

   #> (coordinates : r 1  theta math..radians#60)
   >>> coordinates(
   ...   r=(1),
   ...   theta=(1.0471975511965976))
   {'cartesian': (0.5, 0.866), 'polar': (1, 1.0472)}

Our examples work the same as before,
but the definition is so much simpler.

Symbol Macros
:::::::::::::

It might be nice if we didn't need the ``lazy.`` prefix and anaphor,
and the parentheses to call the thunk.
Something like this:

.. Lissp::

   (defun-lazy complex (real (mul r (math..cos theta))
                        imag (mul r (math..sin theta)))
     (builtins..complex real imag))

However, a local variable read in Python doesn't have any hooks we can
exploit to add new behaviors.
This was a sensible design decision, since locals are supposed to be fast.

But in Lissp, a symbol is just another kind of data.
Want to "expand" a symbol like a macro?
We can do that.
We can rewrite anything, to any form.
This is a recursive find-and-replace task again.
We just have to be careful to allow local shadowing,
and our symbol macros will behave a lot like local variables.
By using pre-expansion,
we only have to worry about lambdas introducing them,
because in :term:`standard` Hissp,
that's the only way it can happen.

`macroexpand_all` will expand all macros in a form,
recursively (including its subforms).
The ``preprocess`` and ``postprocess`` callbacks
run before it attempts to expand a form,
and after it's done expanding,
respectively.

Let's try a small example.

.. code-block:: REPL

   #> (H#macroexpand_all
   #.. '(let (a (add '(ands) '(b)))
   #..    (ors a))
   #.. : preprocess X#(progn (print " in:" X) X)
   #..   postprocess X#(progn (print "out:" X) X))
   >>> __import__('hissp').macroexpand_all(
   ...   ('let',
   ...    ('a',
   ...     ('add',
   ...      ('quote',
   ...       ('ands',),),
   ...      ('quote',
   ...       ('b',),),),),
   ...    ('ors',
   ...     'a',),),
   ...   preprocess=(lambda X:
   ...                  # progn
   ...                  (print(
   ...                     (' in:'),
   ...                     X),
   ...                   X)  [-1]
   ...              ),
   ...   postprocess=(lambda X:
   ...                   # progn
   ...                   (print(
   ...                      ('out:'),
   ...                      X),
   ...                    X)  [-1]
   ...               ))
    in: ('let', ('a', ('add', ('quote', ('ands',)), ('quote', ('b',)))), ('ors', 'a'))
    in: (('lambda', (':', 'a', ('add', ('quote', ('ands',)), ('quote', ('b',)))), ('ors', 'a')),)
    in: ('lambda', (':', 'a', ('add', ('quote', ('ands',)), ('quote', ('b',)))), ('ors', 'a'))
    in: ('add', ('quote', ('ands',)), ('quote', ('b',)))
    in: add
   out: add
    in: ('quote', ('ands',))
   out: ('quote', ('ands',))
    in: ('quote', ('b',))
   out: ('quote', ('b',))
   out: ('add', ('quote', ('ands',)), ('quote', ('b',)))
    in: ('ors', 'a')
    in: a
   out: a
   out: ('lambda', (':', 'a', ('add', ('quote', ('ands',)), ('quote', ('b',)))), 'a')
   out: (('lambda', (':', 'a', ('add', ('quote', ('ands',)), ('quote', ('b',)))), 'a'),)
   (('lambda', (':', 'a', ('add', ('quote', ('ands',)), ('quote', ('b',)))), 'a'),)

Traversal is basically depth-first:
the same order the compiler would process code.
Notice that ``preprocess`` can get called more than once in the same "location" in the code tree.
This happens whenever an expansion replaces that node.
The :term:`special form`\ s are special cased.
We don't process the ``lambda`` atom or the parts of the :term:`params` that can't expand,
like ``:`` or parameter names.
We don't recurse into ``quote`` forms at all,
even if one contains what would otherwise be a :term:`macro form`.
When we hit maximum depth,
right before popping the call stack,
``postprocess`` gets called.
Notice the final ``out:`` line and the first two ``in:`` lines are the same "location"
in the code tree,
but with all the expansions done by the end.

The result is the fully-expanded code.
Try more examples in the REPL if you're unsure about the process.

We can use this to implement "symbol macros":

.. Lissp::

   #> (let (Sentinel (type "Sentinel" () (dict)))
   #..  (defmacro smacrolet (name expansion : :* body)
   #..    (H#macroexpand_all `(progn ,@body)
   #..                       : preprocess X#(if-else (_shadows? X name)
   #..                                        `(lambda ,!##1 X ,@(map X#(attach (Sentinel) X)
   #..                                                                [##2:] X))
   #..                                        X)
   #..                       postprocess X#(cond (eq X name) expansion
   #..                                           (isinstance X Sentinel) X.X
   #..                                           :else X))))
   >>> # let
   ... (
   ...  lambda Sentinel=type(
   ...           ('Sentinel'),
   ...           (),
   ...           dict()):
   ...     # defmacro
   ...     __import__('builtins').setattr(
   ...       __import__('builtins').globals().get(
   ...         ('_macro_')),
   ...       'smacrolet',
   ...       # hissp.macros.._macro_.fun
   ...       # hissp.macros.._macro_.let
   ...       (
   ...        lambda _Qz3murjnbw__lambda=(lambda name, expansion, *body:
   ...                   __import__('hissp').macroexpand_all(
   ...                     (
   ...                       '__main__.._macro_.progn',
   ...                       *body,
   ...                       ),
   ...                     preprocess=(lambda X:
   ...                                    # ifQzH_else
   ...                                    (lambda b, c, a: c()if b else a())(
   ...                                      _shadowsQzQUERY_(
   ...                                        X,
   ...                                        name),
   ...                                      (lambda :
   ...                                          (
   ...                                            'lambda',
   ...                                            __import__('operator').itemgetter(
   ...                                              (1))(
   ...                                              X),
   ...                                            *map(
   ...                                               (lambda X:
   ...                                                   # attach
   ...                                                   # hissp.macros.._macro_.let
   ...                                                   (lambda _Qzxfyq2daa__target=Sentinel():
   ...                                                      (__import__('builtins').setattr(
   ...                                                         _Qzxfyq2daa__target,
   ...                                                         'X',
   ...                                                         X),
   ...                                                       _Qzxfyq2daa__target)  [-1]
   ...                                                   )()
   ...                                               ),
   ...                                               (lambda _Qzskdzewct__items: (_Qzskdzewct__items[2:]))(
   ...                                                 X)),
   ...                                            )
   ...                                      ),
   ...                                      (lambda : X))
   ...                                ),
   ...                     postprocess=(lambda X:
   ...                                     # cond
   ...                                     (lambda x0, x1, x2, x3, x4, x5:
   ...                                              x1() if x0
   ...                                         else x3() if x2()
   ...                                         else x5() if x4()
   ...                                         else ()
   ...                                     )(
   ...                                       eq(
   ...                                         X,
   ...                                         name),
   ...                                       (lambda : expansion),
   ...                                       (lambda :
   ...                                           isinstance(
   ...                                             X,
   ...                                             Sentinel)
   ...                                       ),
   ...                                       (lambda : X.X),
   ...                                       (lambda : ':else'),
   ...                                       (lambda : X))
   ...                                 ))
   ...               ):
   ...          ((
   ...             *__import__('itertools').starmap(
   ...                _Qz3murjnbw__lambda.__setattr__,
   ...                __import__('builtins').dict(
   ...                  __name__='smacrolet',
   ...                  __qualname__='_macro_.smacrolet',
   ...                  __code__=_Qz3murjnbw__lambda.__code__.replace(
   ...                             co_name='smacrolet')).items()),
   ...             ),
   ...           _Qz3murjnbw__lambda)  [-1]
   ...       )())
   ... )()

Our ``postprocess`` is doing the replacement:
when the form is the ``name``, return the ``expansion``.
(Otherwise give the form back.)
This much almost does what we want.
The rest is to implement the shadowing.

Now what's a ``Sentinel``?
It's a new (empty) type unique to this macro,
so we don't ever have to worry about one appearing in the body unless ``smacrolet`` put it there.
The ``preprocess`` function is using it to stop further processing in any lambda bodies that shadow our ``name``.
(No pre-expansion will happen,
but the compiler will still get around to expanding any macros left over.)
See how it reconstructs the lambda form?
Importantly, it allows the :term:`params` to have further processing,
because any appearances of the ``name`` in a default expression haven't been shadowed yet.
But each body form is replaced with a ``Sentinel`` instance with the form attached.
As far as `macroexpand_all` (or ``preprocess``) is concerned,
a ``Sentinel`` instance is just an atom.
But ``postprocess`` will retrieve the attached code from it afterward.

What's ``_shadows?``
It's wishful thinking again.
We haven't implemented it yet,
but we *wish* it would return true only when given a ``lambda``
form which shadows our ``name``.
Let's implement that as well.

.. Lissp::

   #> (defun _shadows? (form name)
   #..  (ands (H#is_node form)
   #..        (eq !##0 form 'lambda)
   #..        (let-from (singles pairs)
   #..                  (H#compiler.parse_params !##1 form)
   #..          (ors (contains singles name)
   #..               (contains (.keys pairs) name)))))
   >>> # defun
   ... # hissp.macros.._macro_.define
   ... __import__('builtins').globals().update(
   ...   _shadowsQzQUERY_=# hissp.macros.._macro_.fun
   ...                    # hissp.macros.._macro_.let
   ...                    (
   ...                     lambda _Qz3murjnbw__lambda=(lambda form, name:
   ...                                # ands
   ...                                (lambda x0, x1, x2: x0 and x1()and x2())(
   ...                                  __import__('hissp').is_node(
   ...                                    form),
   ...                                  (lambda :
   ...                                      eq(
   ...                                        __import__('operator').itemgetter(
   ...                                          (0))(
   ...                                          form),
   ...                                        'lambda')
   ...                                  ),
   ...                                  (lambda :
   ...                                      # letQzH_from
   ...                                      (lambda singles, pairs:
   ...                                          # ors
   ...                                          (lambda x0, x1: x0 or x1())(
   ...                                            contains(
   ...                                              singles,
   ...                                              name),
   ...                                            (lambda :
   ...                                                contains(
   ...                                                  pairs.keys(),
   ...                                                  name)
   ...                                            ))
   ...                                      )(
   ...                                        *__import__('hissp').compiler.parse_params(
   ...                                           __import__('operator').itemgetter(
   ...                                             (1))(
   ...                                             form)))
   ...                                  ))
   ...                            ):
   ...                       ((
   ...                          *__import__('itertools').starmap(
   ...                             _Qz3murjnbw__lambda.__setattr__,
   ...                             __import__('builtins').dict(
   ...                               __name__='_shadowsQzQUERY_',
   ...                               __qualname__='_shadowsQzQUERY_',
   ...                               __code__=_Qz3murjnbw__lambda.__code__.replace(
   ...                                          co_name='_shadowsQzQUERY_')).items()),
   ...                          ),
   ...                        _Qz3murjnbw__lambda)  [-1]
   ...                    )())

Check if it's a node, so we can safely check if it's a lambda.
If so, check the parameter names.
`parse_params` makes it a little easier to get those.
This function uses metaprogramming helpers from the ``hissp`` package.
Importing anything from ``hissp``
at run time violates the :term:`standalone property`,
but this will only be called inside of a macro,
which runs at compile time.
The underscore prefix emphasizes that it isn't meant to be used outside its module.
(Except perhaps by unit tests.)
Definition time doesn't create problems even if ``hissp`` is not installed.
Unlike Python's convention of almost always importing at the top of the file,
imports in Lissp are usually just in time, and this is why.
If you don't call the function, the imports never happen.

Let's try it.

.. code-block:: REPL

   #> (smacrolet a 'A
   #..  (let () (print a))
   #..  (let (a (add a a))
   #..    (ors (print a a.__class__)))
   #..  (print a)
   #..  (print (type a)))
   >>> # smacrolet
   ... (print(
   ...    'A'),
   ...  (
   ...   lambda a=add(
   ...            'A',
   ...            'A'):
   ...      # ors
   ...      print(
   ...        a,
   ...        a.__class__)
   ...  )(),
   ...  print(
   ...    'A'),
   ...  print(
   ...    type(
   ...      'A')))  [-1]
   A
   AA <class 'str'>
   A
   <class 'str'>

We can see ``smacrolet`` works a lot like a `let` (hence the name),
but, as you can see from the compiled Python output,
it does a compile-time substitution instead of an assignment.
The compiler adds a comment whenever it expands a macro,
but `macroexpand_all` does not.
The first `let` disappears without a trace,
and the ``a`` in its body was replaced.
The second `let` expands to a lambda with a default argument,
and the name in the default expression gets substituted as well,
but the body isn't processed,
because it introduces a local with the target name,
which "shadows" our symbol macro.
Note from the comment that the compiler expanded the `ors`,
not the pre-expansion from the ``smacrolet``.

Just one problem:

.. code-block:: REPL

   #> (smacrolet a 'A
   #..  (print a.__class__))
   >>> # smacrolet
   ... print(
   ...   a.__class__)
   Traceback (most recent call last):
     ...
   NameError: name 'a' is not defined

Attribute access.
This was a little contrived to demonstrate an issue.
Normally one would use `type` instead of getting the ``.__class__`` attribute,
which I also demonstrated doesn't show the problem.
The symbols don't match, so the substitution didn't happen.

That's the problem with *injecting Python*.
Had we spelled out the attribute access using a `getattr` call,
it would have been fine.

But attribute access is a :term:`standard` usage of symbols.
A macro ought to be able to handle that case,
even if it's unreasonable to expect it to handle Python expressions in general.

We can check for exactly that, and rewrite it to a let expression.

.. Lissp::

   #> (let (Sentinel (type "Sentinel" () (dict)))
   #..  (defmacro smacrolet (name expansion : :* body)
   #..    (H#macroexpand_all
   #..     `(progn ,@body)
   #..     : preprocess X#(if-else (_shadows? X name)
   #..                      `(lambda ,!##1 X ,@(map X#(attach (Sentinel) X)
   #..                                              [##2:] X))
   #..                      X)
   #..     postprocess X#(cond (eq X name) expansion
   #..                         (isinstance X Sentinel) X.X
   #..                         (eq (_root-name X) name) `(let ($#name ,expansion)
   #..                                                     ,(.format "{}.{}"
   #..                                                               '$#name
   #..                                                               !##-1(.partition X ".")))
   #..                         :else X))))
   >>> # let
   ... (
   ...  lambda Sentinel=type(
   ...           ('Sentinel'),
   ...           (),
   ...           dict()):
   ...     # defmacro
   ...     __import__('builtins').setattr(
   ...       __import__('builtins').globals().get(
   ...         ('_macro_')),
   ...       'smacrolet',
   ...       # hissp.macros.._macro_.fun
   ...       # hissp.macros.._macro_.let
   ...       (
   ...        lambda _Qz3murjnbw__lambda=(lambda name, expansion, *body:
   ...                   __import__('hissp').macroexpand_all(
   ...                     (
   ...                       '__main__.._macro_.progn',
   ...                       *body,
   ...                       ),
   ...                     preprocess=(lambda X:
   ...                                    # ifQzH_else
   ...                                    (lambda b, c, a: c()if b else a())(
   ...                                      _shadowsQzQUERY_(
   ...                                        X,
   ...                                        name),
   ...                                      (lambda :
   ...                                          (
   ...                                            'lambda',
   ...                                            __import__('operator').itemgetter(
   ...                                              (1))(
   ...                                              X),
   ...                                            *map(
   ...                                               (lambda X:
   ...                                                   # attach
   ...                                                   # hissp.macros.._macro_.let
   ...                                                   (lambda _Qzxfyq2daa__target=Sentinel():
   ...                                                      (__import__('builtins').setattr(
   ...                                                         _Qzxfyq2daa__target,
   ...                                                         'X',
   ...                                                         X),
   ...                                                       _Qzxfyq2daa__target)  [-1]
   ...                                                   )()
   ...                                               ),
   ...                                               (lambda _Qzskdzewct__items: (_Qzskdzewct__items[2:]))(
   ...                                                 X)),
   ...                                            )
   ...                                      ),
   ...                                      (lambda : X))
   ...                                ),
   ...                     postprocess=(lambda X:
   ...                                     # cond
   ...                                     (lambda x0, x1, x2, x3, x4, x5, x6, x7:
   ...                                              x1() if x0
   ...                                         else x3() if x2()
   ...                                         else x5() if x4()
   ...                                         else x7() if x6()
   ...                                         else ()
   ...                                     )(
   ...                                       eq(
   ...                                         X,
   ...                                         name),
   ...                                       (lambda : expansion),
   ...                                       (lambda :
   ...                                           isinstance(
   ...                                             X,
   ...                                             Sentinel)
   ...                                       ),
   ...                                       (lambda : X.X),
   ...                                       (lambda :
   ...                                           eq(
   ...                                             _rootQzH_name(
   ...                                               X),
   ...                                             name)
   ...                                       ),
   ...                                       (lambda :
   ...                                           (
   ...                                             '__main__.._macro_.let',
   ...                                             (
   ...                                               '_Qz6feg5spl__name',
   ...                                               expansion,
   ...                                               ),
   ...                                             ('{}.{}').format(
   ...                                               '_Qz6feg5spl__name',
   ...                                               __import__('operator').itemgetter(
   ...                                                 (-1))(
   ...                                                 X.partition(
   ...                                                   ('.')))),
   ...                                             )
   ...                                       ),
   ...                                       (lambda : ':else'),
   ...                                       (lambda : X))
   ...                                 ))
   ...               ):
   ...          ((
   ...             *__import__('itertools').starmap(
   ...                _Qz3murjnbw__lambda.__setattr__,
   ...                __import__('builtins').dict(
   ...                  __name__='smacrolet',
   ...                  __qualname__='_macro_.smacrolet',
   ...                  __code__=_Qz3murjnbw__lambda.__code__.replace(
   ...                             co_name='smacrolet')).items()),
   ...             ),
   ...           _Qz3murjnbw__lambda)  [-1]
   ...       )())
   ... )()

Here we're wishful thinking a helper function again.
This one gets the name we're accessing the attribute from,
using a short regex.
(If the symbol were fully qualified, it would get the module handle part.)
This should work even for a chain of attributes.

.. Lissp::

   #> (defun _root-name (form)
   #..  my#(ands (H#is_symbol form)
   #..           match=(re..match '|(.+?\.||[^.]+)\.| form)
   #..           !##1 my.match))
   >>> # defun
   ... # hissp.macros.._macro_.define
   ... __import__('builtins').globals().update(
   ...   _rootQzH_name=# hissp.macros.._macro_.fun
   ...                 # hissp.macros.._macro_.let
   ...                 (
   ...                  lambda _Qz3murjnbw__lambda=(lambda form:
   ...                             # hissp.macros.._macro_.let
   ...                             (lambda my=__import__('types').SimpleNamespace():
   ...                                 # ands
   ...                                 (lambda x0, x1, x2: x0 and x1()and x2())(
   ...                                   __import__('hissp').is_symbol(
   ...                                     form),
   ...                                   (lambda :
   ...                                       # hissp.macros.._macro_.setQzAT_
   ...                                       # hissp.macros.._macro_.let
   ...                                       (
   ...                                        lambda _Qz56kt2vyy__value=__import__('re').match(
   ...                                                 '(.+?\\.|[^.]+)\\.',
   ...                                                 form):
   ...                                          (# hissp.macros.._macro_.define
   ...                                           __import__('builtins').setattr(
   ...                                             my,
   ...                                             'match',
   ...                                             _Qz56kt2vyy__value),
   ...                                           _Qz56kt2vyy__value)  [-1]
   ...                                       )()
   ...                                   ),
   ...                                   (lambda :
   ...                                       __import__('operator').itemgetter(
   ...                                         (1))(
   ...                                         my.match)
   ...                                   ))
   ...                             )()
   ...                         ):
   ...                    ((
   ...                       *__import__('itertools').starmap(
   ...                          _Qz3murjnbw__lambda.__setattr__,
   ...                          __import__('builtins').dict(
   ...                            __name__='_rootQzH_name',
   ...                            __qualname__='_rootQzH_name',
   ...                            __code__=_Qz3murjnbw__lambda.__code__.replace(
   ...                                       co_name='_rootQzH_name')).items()),
   ...                       ),
   ...                     _Qz3murjnbw__lambda)  [-1]
   ...                 )())

And now we don't get an error from attribute access:

.. code-block:: REPL

   #> (smacrolet a 'A
   #..  (let () (print a))
   #..  (let (a (add a a))
   #..    (ors (print a a.__class__)))
   #..  (print a a.__class__ a.__class__.__mro__))
   >>> # smacrolet
   ... (print(
   ...    'A'),
   ...  (
   ...   lambda a=add(
   ...            'A',
   ...            'A'):
   ...      # ors
   ...      print(
   ...        a,
   ...        a.__class__)
   ...  )(),
   ...  print(
   ...    'A',
   ...    # __main__.._macro_.let
   ...    (lambda _Qz6feg5spl__name='A': _Qz6feg5spl__name.__class__)(),
   ...    # __main__.._macro_.let
   ...    (lambda _Qz6feg5spl__name='A': _Qz6feg5spl__name.__class__.__mro__)()))  [-1]
   A
   AA <class 'str'>
   A <class 'str'> (<class 'str'>, <class 'object'>)

There's more room for improvement.
A more advanced ``smacrolet`` could perhaps handle multiple replacements,
but then we run into the issue of what to do when the replacements themselves contain symbol macros.
This complicates what is otherwise a simple find and replace operation.
To enable mutually-recursive symbol macros,
any replacement must be processed as well,
and the search process should check if any symbol macro matches before moving on.
Hissp's compiler does something similar for normal macros,
as does `macroexpand`.

We won't be needing this kind of recursion for lazy functions.
Application of single-symbol replacements will do.

``defun-lazy``
::::::::::::::

Now we can add a ``smacrolet`` to our ``defun-lazy``.
I will again omit the docstring handling for simplicity.

.. Lissp::

   #> (defmacro defun-lazy (qualname params : :* body)
   #..  `(defun ,qualname (: :** ,'kwargs)
   #..     (-<>>
   #..      (let ($#lazy (types..SimpleNamespace))
   #..        (doto (vars $#lazy)
   #..          (.update (zip ,(list [##::2] params)
   #..                        (|| ,@(map X#`O#,X [##1::2] params) ||)
   #..                        : strict 1))
   #..          (.update (i#starmap (lambda ($#k $#v)
   #..                                (@ $#k (lambda (: $#v $#v) $#v)))
   #..                              (.items ,'kwargs))))
   #..        ,@body)
   #..      ,@(map X#`(smacrolet ,X (,(.format "{}.{}" '$#lazy X)))
   #..             [##::2] params))))
   >>> # defmacro
   ... __import__('builtins').setattr(
   ...   __import__('builtins').globals().get(
   ...     ('_macro_')),
   ...   'defunQzH_lazy',
   ...   # hissp.macros.._macro_.fun
   ...   # hissp.macros.._macro_.let
   ...   (
   ...    lambda _Qz3murjnbw__lambda=(lambda qualname, params, *body:
   ...               (
   ...                 '__main__.._macro_.defun',
   ...                 qualname,
   ...                 (
   ...                   ':',
   ...                   ':**',
   ...                   'kwargs',
   ...                   ),
   ...                 (
   ...                   '__main__.._macro_.QzH_QzLT_QzGT_QzGT_',
   ...                   (
   ...                     '__main__.._macro_.let',
   ...                     (
   ...                       '_Qzgqgc4a3y__lazy',
   ...                       (
   ...                         'types..SimpleNamespace',
   ...                         ),
   ...                       ),
   ...                     (
   ...                       '__main__.._macro_.doto',
   ...                       (
   ...                         'builtins..vars',
   ...                         '_Qzgqgc4a3y__lazy',
   ...                         ),
   ...                       (
   ...                         '.update',
   ...                         (
   ...                           'builtins..zip',
   ...                           list(
   ...                             (lambda _Qzskdzewct__items: (_Qzskdzewct__items[::2]))(
   ...                               params)),
   ...                           (
   ...                             '',
   ...                             *map(
   ...                                (lambda X:
   ...                                    (
   ...                                      'lambda',
   ...                                      ':',
   ...                                      X,
   ...                                      )
   ...                                ),
   ...                                (lambda _Qzskdzewct__items: (_Qzskdzewct__items[1::2]))(
   ...                                  params)),
   ...                             '',
   ...                             ),
   ...                           ':',
   ...                           '__main__..strict',
   ...                           (1),
   ...                           ),
   ...                         ),
   ...                       (
   ...                         '.update',
   ...                         (
   ...                           'itertools..starmap',
   ...                           (
   ...                             'lambda',
   ...                             (
   ...                               '_Qzgqgc4a3y__k',
   ...                               '_Qzgqgc4a3y__v',
   ...                               ),
   ...                             (
   ...                               '__main__.._macro_.QzAT_',
   ...                               '_Qzgqgc4a3y__k',
   ...                               (
   ...                                 'lambda',
   ...                                 (
   ...                                   ':',
   ...                                   '_Qzgqgc4a3y__v',
   ...                                   '_Qzgqgc4a3y__v',
   ...                                   ),
   ...                                 '_Qzgqgc4a3y__v',
   ...                                 ),
   ...                               ),
   ...                             ),
   ...                           (
   ...                             '.items',
   ...                             'kwargs',
   ...                             ),
   ...                           ),
   ...                         ),
   ...                       ),
   ...                     *body,
   ...                     ),
   ...                   *map(
   ...                      (lambda X:
   ...                          (
   ...                            '__main__.._macro_.smacrolet',
   ...                            X,
   ...                            (
   ...                              ('{}.{}').format(
   ...                                '_Qzgqgc4a3y__lazy',
   ...                                X),
   ...                              ),
   ...                            )
   ...                      ),
   ...                      (lambda _Qzskdzewct__items: (_Qzskdzewct__items[::2]))(
   ...                        params)),
   ...                   ),
   ...                 )
   ...           ):
   ...      ((
   ...         *__import__('itertools').starmap(
   ...            _Qz3murjnbw__lambda.__setattr__,
   ...            __import__('builtins').dict(
   ...              __name__='defunQzH_lazy',
   ...              __qualname__='_macro_.defunQzH_lazy',
   ...              __code__=_Qz3murjnbw__lambda.__code__.replace(
   ...                         co_name='defunQzH_lazy')).items()),
   ...         ),
   ...       _Qz3murjnbw__lambda)  [-1]
   ...   )())

Because they can only handle one name each,
we need one ``smacrolet`` per lazy default parameter.
We're leveraging `-\<>> <QzH_QzLT_QzGT_QzGT_>` to do the nesting for us.
The replacements follow a simple pattern we're computing from the keyword.
``lazy`` is now a gensym, not an anaphor.

Notice the first ``.update`` form has changed.
It's important that symbol macros in the lazy default expressions get expanded,
but the parameter names themselves must not be.
While `zip` will accept either,
``smacrolet`` treats a `list` as single atom,
but will recurse into tuples.
A ``list`` of `str` doesn't even pickle.
It has a literal notation so the compiler can emit it.

You've seen the rest before.

Let's try it!

.. Lissp::

   #> (define r4 &#(round : ndigits 4)) ; Just a partial now.
   >>> # define
   ... __import__('builtins').globals().update(
   ...   r4=__import__('functools').partial(
   ...        round,
   ...        ndigits=(4)))

   #> (defun-lazy coordinates (x (mul r (math..cos theta))
   #..                         y (mul r (math..sin theta))
   #..                         r (XY#|(X**2 + Y**2)**.5| x y)
   #..                         θ (math..atan2 y x)
   #..                         theta θ)
   #..   ;; If you're not rounding, it's just
   #..   ;; (dict : cartesian `(,x ,y)  polar `(,r ,theta)))
   #..   (dict : cartesian `(,(r4 x) ,(r4 y))
   #..         polar `(,(r4 r) ,(r4 theta))))
   >>> # defunQzH_lazy
   ... # __main__.._macro_.defun
   ... # hissp.macros.._macro_.define
   ... __import__('builtins').globals().update(
   ...   coordinates=# hissp.macros.._macro_.fun
   ...               # hissp.macros.._macro_.let
   ...               (
   ...                lambda _Qzg4t3gdjc__lambda=(lambda **kwargs:
   ...                           # __main__.._macro_.QzH_QzLT_QzGT_QzGT_
   ...                           # __main__.._macro_.smacrolet
   ...                           (lambda _Qzgqgc4a3y__lazy=__import__('types').SimpleNamespace():
   ...                              ((
   ...                                lambda _Qzqinvrqwa__self=__import__('builtins').vars(
   ...                                         _Qzgqgc4a3y__lazy):
   ...                                  (_Qzqinvrqwa__self.update(
   ...                                     __import__('builtins').zip(
   ...                                       ['x', 'y', 'r', 'θ', 'theta'],
   ...                                       (
   ...                                         (lambda :
   ...                                             mul(
   ...                                               _Qzgqgc4a3y__lazy.r(),
   ...                                               __import__('math').cos(
   ...                                                 _Qzgqgc4a3y__lazy.theta()))
   ...                                         ),
   ...                                         (lambda :
   ...                                             mul(
   ...                                               _Qzgqgc4a3y__lazy.r(),
   ...                                               __import__('math').sin(
   ...                                                 _Qzgqgc4a3y__lazy.theta()))
   ...                                         ),
   ...                                         (lambda :
   ...                                             (lambda X, Y: (X**2 + Y**2)**.5)(
   ...                                               _Qzgqgc4a3y__lazy.x(),
   ...                                               _Qzgqgc4a3y__lazy.y())
   ...                                         ),
   ...                                         (lambda :
   ...                                             __import__('math').atan2(
   ...                                               _Qzgqgc4a3y__lazy.y(),
   ...                                               _Qzgqgc4a3y__lazy.x())
   ...                                         ),
   ...                                         (lambda : _Qzgqgc4a3y__lazy.θ()),
   ...                                         ),
   ...                                       strict=(1))),
   ...                                   _Qzqinvrqwa__self.update(
   ...                                     __import__('itertools').starmap(
   ...                                       (lambda _Qzgqgc4a3y__k, _Qzgqgc4a3y__v:
   ...                                           (lambda *xs: [*xs])(
   ...                                             _Qzgqgc4a3y__k,
   ...                                             (lambda _Qzgqgc4a3y__v=_Qzgqgc4a3y__v: _Qzgqgc4a3y__v))
   ...                                       ),
   ...                                       kwargs.items())),
   ...                                   _Qzqinvrqwa__self)  [-1]
   ...                               )(),
   ...                               dict(
   ...                                 cartesian=(
   ...                                             r4(
   ...                                               _Qzgqgc4a3y__lazy.x()),
   ...                                             r4(
   ...                                               _Qzgqgc4a3y__lazy.y()),
   ...                                             ),
   ...                                 polar=(
   ...                                         r4(
   ...                                           _Qzgqgc4a3y__lazy.r()),
   ...                                         r4(
   ...                                           _Qzgqgc4a3y__lazy.theta()),
   ...                                         )))  [-1]
   ...                           )()
   ...                       ):
   ...                  ((
   ...                     *__import__('itertools').starmap(
   ...                        _Qzg4t3gdjc__lambda.__setattr__,
   ...                        __import__('builtins').dict(
   ...                          __name__='coordinates',
   ...                          __qualname__='coordinates',
   ...                          __code__=_Qzg4t3gdjc__lambda.__code__.replace(
   ...                                     co_name='coordinates')).items()),
   ...                     ),
   ...                   _Qzg4t3gdjc__lambda)  [-1]
   ...               )())

Notice the ``r`` default injection can't use ``x`` and ``y`` directly,
because symbol macros don't work in Python fragments,
which are single atoms as far as ``smacrolet`` is concerned.
We used `XY# <XYQzHASH_>` here (and the names happen to line up)
but a `let` would work as well.
We don't *need* to inject a Python fragment here.
Were the formula expressed in standard Lissp like the other defaults,
the symbol macros would work fine.

Our examples work just like before:

.. code-block:: REPL

   #> (coordinates : r |2**.5|  θ math..radians#45)
   >>> coordinates(
   ...   r=2**.5,
   ...   θ=(0.7853981633974483))
   {'cartesian': (1.0, 1.0), 'polar': (1.4142, 0.7854)}

   #> (coordinates : x 1  y 1)
   >>> coordinates(
   ...   x=(1),
   ...   y=(1))
   {'cartesian': (1, 1), 'polar': (1.4142, 0.7854)}

   #> (coordinates : r 1  theta math..radians#60)
   >>> coordinates(
   ...   r=(1),
   ...   theta=(1.0471975511965976))
   {'cartesian': (0.5, 0.866), 'polar': (1, 1.0472)}


Isn't that cool?
Yes that is awesome.
How close can we get to that in Python?
Yeah, Python is powerful. But not as powerful as a Lisp.
If we're willing to use eval we could pass in the formulas as strings.
But it's frowned upon for good reasons.
If we're willing to rewrite AST?
It's possible, but so much harder than in Lissp that it rarely seems worth the effort.
It'll also confuse that heavyweight IDE you're so reliant upon.
Static analysis can be really confining, especially when the tooling is not readily extensible.

.. topic:: Exercise: special-casing non-special forms

   Modify ``smacrolet`` to avoid pre-expanding `mix`
   and use ``mix`` to interpolate symbol macros in the formula for ``r``.
   Are you pre-expanding its arguments? Should you?

``destruct->``
::::::::::::::

Python can unpack in assignment statements.
And actually, the `my#<myQzHASH_>` tag gives Lissp access to that capability.
But we're restricted to Python identifiers that way.

We have a more powerful bundled `destruct-> <destructQzH_QzGT_>`.
Read through its usage examples.

Here it is, sans docstring:

.. Lissp::

   (defmacro destruct-> (data bindings : :* body)
     my### names=(list) $data=`$#data
     (progn walk=(lambda (bindings)
                   (let (pairs (X#(zip X X : strict True) (iter bindings)))
                     `(|| : ,@chain#(i#starmap XY#(if-else (H#is_node Y)
                                                    `(:* (let (,my.$data (-> ,my.$data ,X))
                                                           ,(my.walk Y)))
                                                    (progn (.append my.names Y)
                                                           `(:? (-> ,my.$data ,X))))
                                               pairs)
                          :? ||)))
            values=`(let (,my.$data ,data) ,(my.walk bindings))
            `(let-from (,@my.names) ,my.values ,@body)))

Starting from the bottom,
the basic idea is to produce a single tuple of values
that can be bound to a tuple of local names all at once using a `let-from<letQzH_from>`.

To do that, it needs to remember each target name it finds (``my.names``).
The tuple of values (``my.values``)
is made using ``my.walk`` for (internal) recursion.

That idea is similar to ``flatten``.
It works via :term:`splicing unquote` of nested `let` forms for each layer.
Each transform is applied via `-> <QzH_QzGT_>`.

``my.$data`` is just a gensym.
The reason to save it in advance like this is
so we can use the same one in multiple templates that aren't nested in a parent template
(which would be another way to do it).
This is bending the rules a little bit,
because gensyms are supposed to be scoped to their template,
but this is internal to a single macro function,
and all uses of it end up inside one template in the end.

This construction doesn't work without shadowing the gensym name.
Some styles (and some compilers, internally) avoid shadowing names at all,
but it's an important capability for metaprogramming.

Try examples until you get it.
You can use `macroexpand` to see the Hissp code it produces.
`pprint.pp` may make it easier to read.
You can see the Python compilation in the REPL.
You can run that through your favorite Python formatter if it helps.

``defun->``
:::::::::::

Python used to allow destructuring of arguments, back in version 2.

Sadly, this was removed in Python 3 (`PEP 3113 <https://peps.python.org/pep-3113/>`_),
and the suggested replacement (`assignment`)
don't really work in lambdas,
which is what Hissp needs.
But macros are powerful enough to make a replacement.
Combine `destruct-> <destructQzH_QzGT_>` and `defun`:

.. Lissp::

   #> (defmacro defun-> (qualname bindings : :* body)
   #..  `(defun ,qualname (: :* $#args  :** $#kwargs)
   #..     (destruct-> (dict (enumerate $#args) : :** $#kwargs) ,bindings
   #..       ,@body)))
   >>> # defmacro
   ... __import__('builtins').setattr(
   ...   __import__('builtins').globals().get(
   ...     ('_macro_')),
   ...   'defunQzH_QzGT_',
   ...   # hissp.macros.._macro_.fun
   ...   # hissp.macros.._macro_.let
   ...   (
   ...    lambda _Qz3murjnbw__lambda=(lambda qualname, bindings, *body:
   ...               (
   ...                 '__main__.._macro_.defun',
   ...                 qualname,
   ...                 (
   ...                   ':',
   ...                   ':*',
   ...                   '_Qzdrlaw3u7__args',
   ...                   ':**',
   ...                   '_Qzdrlaw3u7__kwargs',
   ...                   ),
   ...                 (
   ...                   '__main__.._macro_.destructQzH_QzGT_',
   ...                   (
   ...                     'builtins..dict',
   ...                     (
   ...                       'builtins..enumerate',
   ...                       '_Qzdrlaw3u7__args',
   ...                       ),
   ...                     ':',
   ...                     ':**',
   ...                     '_Qzdrlaw3u7__kwargs',
   ...                     ),
   ...                   bindings,
   ...                   *body,
   ...                   ),
   ...                 )
   ...           ):
   ...      ((
   ...         *__import__('itertools').starmap(
   ...            _Qz3murjnbw__lambda.__setattr__,
   ...            __import__('builtins').dict(
   ...              __name__='defunQzH_QzGT_',
   ...              __qualname__='_macro_.defunQzH_QzGT_',
   ...              __code__=_Qz3murjnbw__lambda.__code__.replace(
   ...                         co_name='defunQzH_QzGT_')).items()),
   ...         ),
   ...       _Qz3murjnbw__lambda)  [-1]
   ...   )())

That's all.

`destruct-> <destructQzH_QzGT_>`
is already powerful enough to bind multiple names,
do lookups via keyword or position index,
and have defaults.
The ``bindings`` can use any transforms you want:
`itertools`, constructors, slicing, methods, custom helper functions, etc.
They can also have side effects,
like `next` or `dict.pop`.

It just needs a data structure to work on.
Rather than writing a single-parameter `defun` (which would also be an option),
we accept any arguments
and combine all the ``*args`` and ``**kwargs`` into one dict.
Positional args will be keyed by number (from `enumerate`).
This makes destructuring via direct lookup just work.
It's also possible to get positional args with `next`.
Recall that dicts remember their insertion order,
and that includes iterating `dict.values`.

Although somewhat awkward,
it is possible to reconstruct an args tuple and kwargs dict because
their keys have different types.
But in that situation,
it may be a better idea to write the `defun` yourself,
possibly with some internal use of
`destruct-> <destructQzH_QzGT_>`.

To prove it's possible, here's how you could implement the signature of `print`:

.. Lissp::

   #> (defun-> my-print ((.pop 'sep " ") sep
   #..                   (.pop 'end "\n") end
   #..                   (.pop 'file sys..stdout) file
   #..                   (.pop 'flush False) flush
   #..                   (.values) values)
   #..  (print : :* values  sep sep  end end  file file  flush flush))
   >>> # defunQzH_QzGT_
   ... # __main__.._macro_.defun
   ... # hissp.macros.._macro_.define
   ... __import__('builtins').globals().update(
   ...   myQzH_print=# hissp.macros.._macro_.fun
   ...               # hissp.macros.._macro_.let
   ...               (
   ...                lambda _Qz3murjnbw__lambda=(lambda *_Qzdrlaw3u7__args, **_Qzdrlaw3u7__kwargs:
   ...                           # __main__.._macro_.destructQzH_QzGT_
   ...                           # hissp.macros.._macro_.letQzH_from
   ...                           (lambda sep, end, file, flush, values:
   ...                               print(
   ...                                 *values,
   ...                                 sep=sep,
   ...                                 end=end,
   ...                                 file=file,
   ...                                 flush=flush)
   ...                           )(
   ...                             *# hissp.macros.._macro_.let
   ...                              (
   ...                               lambda _Qzduavqad3__data=__import__('builtins').dict(
   ...                                        __import__('builtins').enumerate(
   ...                                          _Qzdrlaw3u7__args),
   ...                                        **_Qzdrlaw3u7__kwargs):
   ...                                  (
   ...                                    # hissp.macros.._macro_.QzH_QzGT_
   ...                                    _Qzduavqad3__data.pop(
   ...                                      'sep',
   ...                                      (' ')),
   ...                                    # hissp.macros.._macro_.QzH_QzGT_
   ...                                    _Qzduavqad3__data.pop(
   ...                                      'end',
   ...                                      ('\n')),
   ...                                    # hissp.macros.._macro_.QzH_QzGT_
   ...                                    _Qzduavqad3__data.pop(
   ...                                      'file',
   ...                                      __import__('sys').stdout),
   ...                                    # hissp.macros.._macro_.QzH_QzGT_
   ...                                    _Qzduavqad3__data.pop(
   ...                                      'flush',
   ...                                      False),
   ...                                    # hissp.macros.._macro_.QzH_QzGT_
   ...                                    _Qzduavqad3__data.values(),
   ...                                    )
   ...                              )())
   ...                       ):
   ...                  ((
   ...                     *__import__('itertools').starmap(
   ...                        _Qz3murjnbw__lambda.__setattr__,
   ...                        __import__('builtins').dict(
   ...                          __name__='myQzH_print',
   ...                          __qualname__='myQzH_print',
   ...                          __code__=_Qz3murjnbw__lambda.__code__.replace(
   ...                                     co_name='myQzH_print')).items()),
   ...                     ),
   ...                   _Qz3murjnbw__lambda)  [-1]
   ...               )())

This demonstrates keyword defaults and a variable number of positional arguments.

.. code-block:: REPL

   #> (my-print 1 2 3 : sep :)
   >>> myQzH_print(
   ...   (1),
   ...   (2),
   ...   (3),
   ...   sep=':')
   1:2:3

There's one notable difference though:

.. code-block:: REPL

   #> (my-print 1 2 3 : sep :  foo 4)
   >>> myQzH_print(
   ...   (1),
   ...   (2),
   ...   (3),
   ...   sep=':',
   ...   foo=(4))
   1:2:3:4

We assumed everything left over after popping off the keywords was positional.
But what if one of the keywords was accidentally misspelled?
There are various ways to check for errors if you want to be strict about it:

.. Lissp::

   #> (defun-> my-print ((.pop 'sep " ") sep
   #..                   (.pop 'end "\n") end
   #..                   (.pop 'file sys..stdout) file
   #..                   (.pop 'flush False) flush
   #..                   (.values) values
   #..                   (-> .keys list !#-1) (ors last-key
   #..                                         type last-key-type))
   #..  (unless (is_ last-key-type int)
   #..    (throw (TypeError (.format "{!r} is an invalid keyword argument" last-key))))
   #..  (print : :* values  sep sep  end end  file file  flush flush))
   >>> # defunQzH_QzGT_
   ... # __main__.._macro_.defun
   ... # hissp.macros.._macro_.define
   ... __import__('builtins').globals().update(
   ...   myQzH_print=# hissp.macros.._macro_.fun
   ...               # hissp.macros.._macro_.let
   ...               (
   ...                lambda _Qz3murjnbw__lambda=(lambda *_Qzdrlaw3u7__args, **_Qzdrlaw3u7__kwargs:
   ...                           # __main__.._macro_.destructQzH_QzGT_
   ...                           # hissp.macros.._macro_.letQzH_from
   ...                           (lambda sep, end, file, flush, values, lastQzH_key, lastQzH_keyQzH_type:
   ...                              (# unless
   ...                               (lambda b, a: ()if b else a())(
   ...                                 is_(
   ...                                   lastQzH_keyQzH_type,
   ...                                   int),
   ...                                 (lambda :
   ...                                     # throw
   ...                                     # hissp.macros.._macro_.throwQzSTAR_
   ...                                     (lambda g:g.close()or g.throw)(c for c in'')(
   ...                                       TypeError(
   ...                                         ('{!r} is an invalid keyword argument').format(
   ...                                           lastQzH_key)))
   ...                                 )),
   ...                               print(
   ...                                 *values,
   ...                                 sep=sep,
   ...                                 end=end,
   ...                                 file=file,
   ...                                 flush=flush))  [-1]
   ...                           )(
   ...                             *# hissp.macros.._macro_.let
   ...                              (
   ...                               lambda _Qzduavqad3__data=__import__('builtins').dict(
   ...                                        __import__('builtins').enumerate(
   ...                                          _Qzdrlaw3u7__args),
   ...                                        **_Qzdrlaw3u7__kwargs):
   ...                                  (
   ...                                    # hissp.macros.._macro_.QzH_QzGT_
   ...                                    _Qzduavqad3__data.pop(
   ...                                      'sep',
   ...                                      (' ')),
   ...                                    # hissp.macros.._macro_.QzH_QzGT_
   ...                                    _Qzduavqad3__data.pop(
   ...                                      'end',
   ...                                      ('\n')),
   ...                                    # hissp.macros.._macro_.QzH_QzGT_
   ...                                    _Qzduavqad3__data.pop(
   ...                                      'file',
   ...                                      __import__('sys').stdout),
   ...                                    # hissp.macros.._macro_.QzH_QzGT_
   ...                                    _Qzduavqad3__data.pop(
   ...                                      'flush',
   ...                                      False),
   ...                                    # hissp.macros.._macro_.QzH_QzGT_
   ...                                    _Qzduavqad3__data.values(),
   ...                                    *# hissp.macros.._macro_.let
   ...                                     (
   ...                                      lambda _Qzduavqad3__data=# hissp.macros.._macro_.QzH_QzGT_
   ...                                             # QzH_QzGT_
   ...                                             __import__('operator').itemgetter(
   ...                                               (-1))(
   ...                                               list(
   ...                                                 _Qzduavqad3__data.keys()),
   ...                                               ):
   ...                                         (
   ...                                           # hissp.macros.._macro_.QzH_QzGT_
   ...                                           # ors
   ...                                           _Qzduavqad3__data,
   ...                                           # hissp.macros.._macro_.QzH_QzGT_
   ...                                           type(
   ...                                             _Qzduavqad3__data),
   ...                                           )
   ...                                     )(),
   ...                                    )
   ...                              )())
   ...                       ):
   ...                  ((
   ...                     *__import__('itertools').starmap(
   ...                        _Qz3murjnbw__lambda.__setattr__,
   ...                        __import__('builtins').dict(
   ...                          __name__='myQzH_print',
   ...                          __qualname__='myQzH_print',
   ...                          __code__=_Qz3murjnbw__lambda.__code__.replace(
   ...                                     co_name='myQzH_print')).items()),
   ...                     ),
   ...                   _Qz3murjnbw__lambda)  [-1]
   ...               )())

.. code-block:: REPL

   #> (my-print 1 2 3 : zep :)
   >>> myQzH_print(
   ...   (1),
   ...   (2),
   ...   (3),
   ...   zep=':')
   Traceback (most recent call last):
     ...
   TypeError: 'zep' is an invalid keyword argument

Of course, in a simple case like this,
it would be *much easier* to use a normal `defun`.
But ``defun->`` can destructure complicated data
in addition to replicating Python's capabilities:

.. Lissp::

   #> (defun-> coordinates->complex pos#((!#'cartesian pos#(x y)))
   #..  (builtins..complex x y))
   >>> # defunQzH_QzGT_
   ... # __main__.._macro_.defun
   ... # hissp.macros.._macro_.define
   ... __import__('builtins').globals().update(
   ...   coordinatesQzH_QzGT_complex=# hissp.macros.._macro_.fun
   ...                               # hissp.macros.._macro_.let
   ...                               (
   ...                                lambda _Qzg4t3gdjc__lambda=(lambda *_Qzdrlaw3u7__args, **_Qzdrlaw3u7__kwargs:
   ...                                           # __main__.._macro_.destructQzH_QzGT_
   ...                                           # hissp.macros.._macro_.letQzH_from
   ...                                           (lambda x, y:
   ...                                               __import__('builtins').complex(
   ...                                                 x,
   ...                                                 y)
   ...                                           )(
   ...                                             *# hissp.macros.._macro_.let
   ...                                              (
   ...                                               lambda _Qz4d7tjywl__data=__import__('builtins').dict(
   ...                                                        __import__('builtins').enumerate(
   ...                                                          _Qzdrlaw3u7__args),
   ...                                                        **_Qzdrlaw3u7__kwargs):
   ...                                                  (
   ...                                                    *# hissp.macros.._macro_.let
   ...                                                     (
   ...                                                      lambda _Qz4d7tjywl__data=# hissp.macros.._macro_.QzH_QzGT_
   ...                                                             __import__('operator').itemgetter(
   ...                                                               (0))(
   ...                                                               _Qz4d7tjywl__data,
   ...                                                               ):
   ...                                                         (
   ...                                                           *# hissp.macros.._macro_.let
   ...                                                            (
   ...                                                             lambda _Qz4d7tjywl__data=# hissp.macros.._macro_.QzH_QzGT_
   ...                                                                    __import__('operator').itemgetter(
   ...                                                                      'cartesian')(
   ...                                                                      _Qz4d7tjywl__data,
   ...                                                                      ):
   ...                                                                (
   ...                                                                  # hissp.macros.._macro_.QzH_QzGT_
   ...                                                                  __import__('operator').itemgetter(
   ...                                                                    (0))(
   ...                                                                    _Qz4d7tjywl__data,
   ...                                                                    ),
   ...                                                                  # hissp.macros.._macro_.QzH_QzGT_
   ...                                                                  __import__('operator').itemgetter(
   ...                                                                    (1))(
   ...                                                                    _Qz4d7tjywl__data,
   ...                                                                    ),
   ...                                                                  )
   ...                                                            )(),
   ...                                                           )
   ...                                                     )(),
   ...                                                    )
   ...                                              )())
   ...                                       ):
   ...                                  ((
   ...                                     *__import__('itertools').starmap(
   ...                                        _Qzg4t3gdjc__lambda.__setattr__,
   ...                                        __import__('builtins').dict(
   ...                                          __name__='coordinatesQzH_QzGT_complex',
   ...                                          __qualname__='coordinatesQzH_QzGT_complex',
   ...                                          __code__=_Qzg4t3gdjc__lambda.__code__.replace(
   ...                                                     co_name='coordinatesQzH_QzGT_complex')).items()),
   ...                                     ),
   ...                                   _Qzg4t3gdjc__lambda)  [-1]
   ...                               )())

.. code-block:: REPL

   #> (coordinates : r 1.4142  theta 0.7854)
   >>> coordinates(
   ...   r=(1.4142),
   ...   theta=(0.7854))
   {'cartesian': (1.0, 1.0), 'polar': (1.4142, 0.7854)}

   #> (coordinates->complex _)
   >>> coordinatesQzH_QzGT_complex(
   ...   _)
   (1+1j)

A lot of programming comes down to restructuring data like this.

.. topic:: Exercise: Add doctring handling to ``defun-lazy`` and ``defun->``.

   We've done this before. Generalize what you've seen.

.. topic:: Exercise: make a ``fun->``

   ``fun->`` is to ``defun->`` as ``fun`` is to ``defun``.
   It should work the same as ``defun->``, but without the `define`.

   Can you rewrite ``defun->`` in terms of your ``fun->`` and `define`
   without duplicating code?

.. topic:: Exercise: Your Final Exam

   Make a function definition macro that can have both

   * destructuring binding forms on the left of the pair,
   * and lazy defaults on the right.

   For bonus points,
   support all of Python's parameter types as well:
   positional only,
   normal,
   ``*arg``,
   keyword only,
   and ``**kwarg``.

If you've made it this far,
show off your solutions in the Hissp Community Chat!

.. TODO: advanced techniques from A Slice of Python?
   Let's review. This section covered a number of advanced techniques:
   - Brackets in symbols.
   - A code string macro leveraging partial Python syntax.
   - The need for parentheses in injections.
   - Demunging.
   - Calls to run time helpers, even in other modules.
   - Qualifying symbols with template quote.
   - Compiling in macros using `readerless`.

.. TODO: continue explanation up to bundled [#.

.. TODO: fractions
   (defmacro F\# (x)
     "fraction"
     `(fractions..Fraction ',(hissp.munger..demunge x)))

.. TODO: stack?
   (defmacro <\# (x)
     "push"
     (.append _macro_.<\#.stack x)
     hissp.reader..DROP)
   (setattr _macro_.<\# 'stack [])
   (defmacro -\# (x)
     `(sub ,(.pop _macro_.<\#.stack) ,x))

.. TODO: attach macro
   (defmacro attach (target : :* args)
     (let (iargs (iter args)
                 $target `$#target)
       (let (args (itertools..takewhile (lambda (a)
                                          (operator..ne a ':))
                                        iargs))
         `(let (,$target ,target)
            ,@(map %#`(setattr ,$target ',% ,%))
                   args)
            ,@(map %#`(setattr ,$target ',% ,(next iargs)))
                   iargs)
            ,$target))))
   promote local variable to instance variable
   Python can get closer than you might think:
   def attach(target, name):
       import inspect
       setattr(target, name, inspect.currentframe().f_back.f_locals[name])
       return target
   (show how this doesn't work on nonlocals)

.. TODO: preconditions?

.. TODO: defmacro/g defmacro!

.. TODO: one-shot self-referential data structure using reader macros
             See http://www.lispworks.com/documentation/HyperSpec/Body/02_dho.htm
             for the Common Lisp approach.
         multiary reader macros via stack
         reader macro namespacing via custom _macro_ class

.. TODO: Lisp-2 via custom _macro_ class
.. TODO: yield and code-walking
