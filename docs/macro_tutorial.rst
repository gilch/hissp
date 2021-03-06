.. Copyright 2020, 2021 Matthew Egan Odendahl
   SPDX-License-Identifier: CC-BY-SA-4.0

Macro Tutorial
==============

.. TODO: be sure to demonstrate hissp.compiler..NS and hissp.compiler..readerless somewhere
.. TODO: be sure to demonstrate a recursive macro somewhere

Lisp is a higher-level language than Python,
in the same sense that Python is a higher-level language than C,
and C is a higher-level language than assembly.

In C, abstractions like for-loops and the function call stack are
*primitives*—features built into the language.
But in assembly, those are *design patterns* built with lower-level jumps/GOTOs
that have to be repeated each time they're needed.
Things like call stacks had to be discovered and developed and learned as best practice
in the more primitive assembly languages.
Before the development of the structured programming paradigm,
the industry standard was GOTO spaghetti.

Similarly, in Python, abstractions like iterators, classes, higher-order functions,
and garbage collection are *primitives*,
but in C, those are *design patterns*,
discovered and developed over time as best practice,
and built with lower-level parts like structs and pointers,
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
but certain repeated patterns can't be abstracted away.
You're stuck with a certain amount of boilerplate and ceremony.

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
you're forgoing much of Lisp's power.
This is a tutorial,
not a reference,
and I'll be explaining not just how to write macros,
but why you need them.

----

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
That also means that it's more difficult the more different the new language is
from those you already know.

Fortunately, Lissp's syntax is very minimal,
so there's not that much to remember,
and most of the vocabulary you know from Python already.
You can skim over the Python in this tutorial,
but resist the urge to skim the Lissp.
`S-expressions <https://en.wikipedia.org/wiki/S-expression>`_
are a very direct representation of the same kind of syntax trees that
you mentally generate when reading any other programming language.
Take your time and comprehend each subexpression instead of taking it in all at once.

The previous tutorial was mostly about learning how to program with
a subset of Python in a new skin.
This one is about using that knowledge to reprogram the skin itself.

If you don't know the basics from the `previous tutorial <tutorial>`,
go back and read that now, or at least read the `quick start <lissp_quickstart>`.

In the previous tutorial we mostly used the REPL,
but it can become tedious to type long forms into the REPL,
and it doesn't save your work.
S-expressions are awkward to edit without editor support for them,
and the included Lissp REPL is layered on Python's interactive console,
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
It's probably easiest to set up in `Atom <https://atom.io/packages/parinfer>`_.

Shorter Lambdas
---------------

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
almost any way you can.
Fewer slightly less-readable lines are much more readable
than too many slightly more-readable lines.

Consider Python's humble ``lambda``.
It's important to programming in the functional style,
and central to the way Hissp works,
as a compilation target for one of its two special forms.
It's actually really powerful.

But the overhead of typing out a six-letter word might make you a little too reluctant to use it,
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
It's a reserved word, but at runtime, that's not an object.
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
~~~~~~~

Create a Lissp file (perhaps ``macros.lissp``),
and open it in your Lisp editor of choice.

Fire up the Lissp REPL in a terminal,
or in your editor if it does that.

Add the prelude to the top of the file:

.. code-block:: Lissp

   (hissp.basic.._macro_.prelude)

And push it to the REPL as well:

.. code-block:: REPL

   #> (hissp.basic.._macro_.prelude)
   >>> # hissp.basic.._macro_.prelude
   ... __import__('builtins').exec(
   ...   ('from operator import *\n'
   ...    'from itertools import *\n'
   ...    'try:\n'
   ...    '    from hissp.basic import _macro_\n'
   ...    "    _macro_ = __import__('types').SimpleNamespace(**vars(_macro_))\n"
   ...    'except ModuleNotFoundError:\n'
   ...    '    pass'))

.. caution::

   The `prelude` macro overwrites your ``_macro_`` namespace with a copy of the basic one.
   Any macros you've defined in there are lost.
   In Lissp files, the prelude is meant to be used before any definitions,
   when it is used at all.
   Likewise, in the REPL, enter it first, or be prepared to re-enter your definitions.
   The REPL already comes with the `basic` macros,
   but not the `itertools` or `operator`\ s.

I'll mostly be showing the REPL from here on.
Remember, compose in your Lissp file,
then push to the REPL.
We'll be modifying these definitions through several iterations.

Let's try the same idea in Lissp:

.. code-block:: REPL

   #> (define L lambda)
   >>> # define
   ... __import__('operator').setitem(
   ...   __import__('builtins').globals(),
   ...   'L',
   ...   lambda)
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
   ... __import__('operator').setitem(
   ...   __import__('builtins').globals(),
   ...   'L',
   ...   'lambda')

OK, but that just turned it into a string.
We could have done that much in Python:

.. code-block:: Python

   >>> L = 'lambda'

That worked, but can we use it?

.. code-block:: Python

   >>> squares = map(L x: x * x, range(10))
   Traceback (most recent call last):
     ...
     squares = map(L x: x * x, range(10))
                    ^
   SyntaxError: invalid syntax

Another syntax error.
No surprise.

Write the equivalent example in your Lissp file
and push it to the REPL:

.. code-block:: REPL

   #> (define squares (map (L (x)
   #..                       (mul x x))
   #..                     (range 10)))
   >>> # define
   ... __import__('operator').setitem(
   ...   __import__('builtins').globals(),
   ...   'squares',
   ...   map(
   ...     L(
   ...       x(),
   ...       mul(
   ...         x,
   ...         x)),
   ...     range(
   ...       (10))))
   Traceback (most recent call last):
     File "<console>", line 7, in <module>
   NameError: name 'x' is not defined

Not a syntax error, but it's not working either.
Why not?
Quote the whole thing to see the Hissp tuples.

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
   ... __import__('operator').setitem(
   ...   __import__('builtins').globals(),
   ...   'squares',
   ...   map(
   ...     (lambda x:
   ...       mul(
   ...         x,
   ...         x)),
   ...     range(
   ...       (10))))

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
*What do you think Lissp is?!*

The C preprocessor is pretty limited.
Lissp is a transplier.
That's *much* more powerful.

But since Python is supposed to be such a marvelously high-level language compared to C,
can't it do that too?

No, it really can't:

>>> squares = map(eval(f"{L} x: x * x"), range(10))
>>> list(squares)
[0, 1, 4, 9, 16, 25, 36, 49, 64, 81]

Sometimes higher-level tools cut you off from the lower level.
You can get pretty close to the same idea,
but that's about the best Python can do.
Compare:

.. code-block:: Python

   eval(f"{L} x: x * x")
   lambda x: x * x

It didn't help, did it?
It got longer!
Can we do better?

>>> e = eval

.. code-block:: Python

   e(f"{L} x:x*x")
   lambda x:x*x

Nope.
And there are good reasons to avoid `eval` in Python:
We have to compile code at runtime,
and put more than we wanted to in a string,
and deal with separate namespaces. Ick.
Lissp had none of those problems.

This simple substitution metaprogramming task that was so easy in Lissp
was so awkward in Python.

But Lissp does more than substitutions.

Simple Compiler Macros
~~~~~~~~~~~~~~~~~~~~~~

Despite my recent boasting,
our Lissp version is not actually shorter than Python's yet:

.. code-block:: Text

   (.#L (x)
     (mul x x))
   lambda x: x * x

If you like, we can give `mul <operator.mul>` a shorter name:

.. code-block:: REPL

   #> (define * mul)
   >>> # define
   ... __import__('operator').setitem(
   ...   __import__('builtins').globals(),
   ...   'xSTAR_',
   ...   mul)

And the params tuple doesn't technically have to be a tuple:

.. code-block:: Text

   (.#L x (* x x))
   lambda x: x * x

Symbols become strings at the Hissp level,
which are iterables containing character strings.
This only works because the variable name is a single character.
Now we're at the same length as Python.
Let's make it even shorter.

Given a tuple containing the *minimum* amount of information,
we want expand that into the necessary code using a macro.

Isn't there something extra here we could get rid of?
With a compiler macro, we won't need the inject.

The template needs to look something like
``(lambda <params> <body>)``.
Try this definition.

.. Lissp::

   #> (defmacro L (params : :* body)
   #..  `(lambda ,params ,@body))
   >>> # defmacro
   ... # hissp.basic.._macro_.let
   ... (lambda _fnxAUTO7_=(lambda params,*body:
   ...   (lambda *xAUTO0_:xAUTO0_)(
   ...     'lambda',
   ...     params,
   ...     *body)):(
   ...   __import__('builtins').setattr(
   ...     _fnxAUTO7_,
   ...     '__qualname__',
   ...     ('.').join(
   ...       ('_macro_',
   ...        'L',))),
   ...   __import__('builtins').setattr(
   ...     _macro_,
   ...     'L',
   ...     _fnxAUTO7_))[-1])()


.. code-block:: REPL

   #> (list (map (L x (* x x))
   #..           (range 10)))
   >>> list(
   ...   map(
   ...     # L
   ...     (lambda x:
   ...       xSTAR_(
   ...         x,
   ...         x)),
   ...     range(
   ...       (10))))
   [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]

Success.
Now compare:

.. code-block:: Text

   (L x (* x x))
   lambda x: x * x

Are we doing better?
Barely.
If we remove the spaces that aren't required:

.. code-block:: Text

   (L x(* x x))
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

So the template would looks something like this::

   (lambda (X)
     (<expr>))

Remember this is basically the same as
that anaphoric macro we did in the previous tutorial.

.. Lissp::

   #> (defmacro L (: :* expr)
   #..  `(lambda (,'X)  ; Interpolate anaphors to prevent qualification!
   #..     ,expr))
   >>> # defmacro
   ... # hissp.basic.._macro_.let
   ... (lambda _fnxAUTO7_=(lambda *expr:
   ...   (lambda *xAUTO0_:xAUTO0_)(
   ...     'lambda',
   ...     (lambda *xAUTO0_:xAUTO0_)(
   ...       'X'),
   ...     expr)):(
   ...   __import__('builtins').setattr(
   ...     _fnxAUTO7_,
   ...     '__qualname__',
   ...     ('.').join(
   ...       ('_macro_',
   ...        'L',))),
   ...   __import__('builtins').setattr(
   ...     _macro_,
   ...     'L',
   ...     _fnxAUTO7_))[-1])()


.. code-block:: REPL

   #> (list (map (L * X X) (range 10)))
   >>> list(
   ...   map(
   ...     # L
   ...     (lambda X:
   ...       xSTAR_(
   ...         X,
   ...         X)),
   ...     range(
   ...       (10))))
   [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]

Now we're shorter than Python:

.. code-block:: Text

   (L * X X)
   lambda x: x*x

But we're also less general.
We can change the expression,
but we've hardcoded the parameters to it.
The fixed name is fine as long as we don't have to nest them,
but what if needed two parameters?
Seriously, close your eyes and think about it for at least fifteen seconds
before moving on to the next paragraph.
Don't generalize before we have examples to work with.

You might already guess how we might do this:

.. Lissp::

   #> (defmacro L2 (: :* expr)
   #..  `(lambda (,'X ,'Y)
   #..     ,expr))
   >>> # defmacro
   ... # hissp.basic.._macro_.let
   ... (lambda _fnxAUTO7_=(lambda *expr:
   ...   (lambda *xAUTO0_:xAUTO0_)(
   ...     'lambda',
   ...     (lambda *xAUTO0_:xAUTO0_)(
   ...       'X',
   ...       'Y'),
   ...     expr)):(
   ...   __import__('builtins').setattr(
   ...     _fnxAUTO7_,
   ...     '__qualname__',
   ...     ('.').join(
   ...       ('_macro_',
   ...        'L2',))),
   ...   __import__('builtins').setattr(
   ...     _macro_,
   ...     'L2',
   ...     _fnxAUTO7_))[-1])()


.. code-block:: REPL

   #> (L2 * X Y)
   >>> # L2
   ... (lambda X,Y:
   ...   xSTAR_(
   ...     X,
   ...     Y))
   <function <lambda> at ...>

That's another easy template.
Between ``L`` and ``L2``,
we've probably covered 80% of short-lambda use cases.
But you can see the pattern now.
We could continue to an ``L3`` with a ``Z`` parameter,
and then we've run out of alphabet.

When you see a "design pattern" in Lissp,
you don't keep repeating it.

Nothing Is Above Abstraction
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Are you ready for this?
You've seen all these pieces before,
even if you haven't realized they could be used this way.

Don't panic.

.. code-block:: REPL

   #> .#`(progn ,@(map (lambda (i)
   #..                   `(defmacro ,(.format "L{}" i)
   #..                              (: :* $#expr)
   #..                      `(lambda ,',(getitem "ABCDEFGHIJKLMNOPQRSTUVWXYZ" (slice i))
   #..                         ,$#expr)))
   #..                 (range 27)))
   >>> # __main__.._macro_.progn
   ... (lambda :(
   ...   # __main__.._macro_.defmacro
   ...   # hissp.basic.._macro_.let
   ...   (lambda _fnxAUTO7_=(lambda *_exprxAUTO36_:
   ...     (lambda *xAUTO0_:xAUTO0_)(
   ...       'lambda',
   ...       '',
   ...       _exprxAUTO36_)):(
   ...     __import__('builtins').setattr(
   ...       _fnxAUTO7_,
   ...       '__qualname__',
   ...       ('.').join(
   ...         ('_macro_',
   ...          'L0',))),
   ...     __import__('builtins').setattr(
   ...       _macro_,
   ...       'L0',
   ...       _fnxAUTO7_))[-1])(),
   ...   # __main__.._macro_.defmacro
   ...   # hissp.basic.._macro_.let
   ...   (lambda _fnxAUTO7_=(lambda *_exprxAUTO36_:
   ...     (lambda *xAUTO0_:xAUTO0_)(
   ...       'lambda',
   ...       'A',
   ...       _exprxAUTO36_)):(
   ...     __import__('builtins').setattr(
   ...       _fnxAUTO7_,
   ...       '__qualname__',
   ...       ('.').join(
   ...         ('_macro_',
   ...          'L1',))),
   ...     __import__('builtins').setattr(
   ...       _macro_,
   ...       'L1',
   ...       _fnxAUTO7_))[-1])(),
   ...   # __main__.._macro_.defmacro
   ...   # hissp.basic.._macro_.let
   ...   (lambda _fnxAUTO7_=(lambda *_exprxAUTO36_:
   ...     (lambda *xAUTO0_:xAUTO0_)(
   ...       'lambda',
   ...       'AB',
   ...       _exprxAUTO36_)):(
   ...     __import__('builtins').setattr(
   ...       _fnxAUTO7_,
   ...       '__qualname__',
   ...       ('.').join(
   ...         ('_macro_',
   ...          'L2',))),
   ...     __import__('builtins').setattr(
   ...       _macro_,
   ...       'L2',
   ...       _fnxAUTO7_))[-1])(),
   ...   # __main__.._macro_.defmacro
   ...   # hissp.basic.._macro_.let
   ...   (lambda _fnxAUTO7_=(lambda *_exprxAUTO36_:
   ...     (lambda *xAUTO0_:xAUTO0_)(
   ...       'lambda',
   ...       'ABC',
   ...       _exprxAUTO36_)):(
   ...     __import__('builtins').setattr(
   ...       _fnxAUTO7_,
   ...       '__qualname__',
   ...       ('.').join(
   ...         ('_macro_',
   ...          'L3',))),
   ...     __import__('builtins').setattr(
   ...       _macro_,
   ...       'L3',
   ...       _fnxAUTO7_))[-1])(),
   ...   # __main__.._macro_.defmacro
   ...   # hissp.basic.._macro_.let
   ...   (lambda _fnxAUTO7_=(lambda *_exprxAUTO36_:
   ...     (lambda *xAUTO0_:xAUTO0_)(
   ...       'lambda',
   ...       'ABCD',
   ...       _exprxAUTO36_)):(
   ...     __import__('builtins').setattr(
   ...       _fnxAUTO7_,
   ...       '__qualname__',
   ...       ('.').join(
   ...         ('_macro_',
   ...          'L4',))),
   ...     __import__('builtins').setattr(
   ...       _macro_,
   ...       'L4',
   ...       _fnxAUTO7_))[-1])(),
   ...   # __main__.._macro_.defmacro
   ...   # hissp.basic.._macro_.let
   ...   (lambda _fnxAUTO7_=(lambda *_exprxAUTO36_:
   ...     (lambda *xAUTO0_:xAUTO0_)(
   ...       'lambda',
   ...       'ABCDE',
   ...       _exprxAUTO36_)):(
   ...     __import__('builtins').setattr(
   ...       _fnxAUTO7_,
   ...       '__qualname__',
   ...       ('.').join(
   ...         ('_macro_',
   ...          'L5',))),
   ...     __import__('builtins').setattr(
   ...       _macro_,
   ...       'L5',
   ...       _fnxAUTO7_))[-1])(),
   ...   # __main__.._macro_.defmacro
   ...   # hissp.basic.._macro_.let
   ...   (lambda _fnxAUTO7_=(lambda *_exprxAUTO36_:
   ...     (lambda *xAUTO0_:xAUTO0_)(
   ...       'lambda',
   ...       'ABCDEF',
   ...       _exprxAUTO36_)):(
   ...     __import__('builtins').setattr(
   ...       _fnxAUTO7_,
   ...       '__qualname__',
   ...       ('.').join(
   ...         ('_macro_',
   ...          'L6',))),
   ...     __import__('builtins').setattr(
   ...       _macro_,
   ...       'L6',
   ...       _fnxAUTO7_))[-1])(),
   ...   # __main__.._macro_.defmacro
   ...   # hissp.basic.._macro_.let
   ...   (lambda _fnxAUTO7_=(lambda *_exprxAUTO36_:
   ...     (lambda *xAUTO0_:xAUTO0_)(
   ...       'lambda',
   ...       'ABCDEFG',
   ...       _exprxAUTO36_)):(
   ...     __import__('builtins').setattr(
   ...       _fnxAUTO7_,
   ...       '__qualname__',
   ...       ('.').join(
   ...         ('_macro_',
   ...          'L7',))),
   ...     __import__('builtins').setattr(
   ...       _macro_,
   ...       'L7',
   ...       _fnxAUTO7_))[-1])(),
   ...   # __main__.._macro_.defmacro
   ...   # hissp.basic.._macro_.let
   ...   (lambda _fnxAUTO7_=(lambda *_exprxAUTO36_:
   ...     (lambda *xAUTO0_:xAUTO0_)(
   ...       'lambda',
   ...       'ABCDEFGH',
   ...       _exprxAUTO36_)):(
   ...     __import__('builtins').setattr(
   ...       _fnxAUTO7_,
   ...       '__qualname__',
   ...       ('.').join(
   ...         ('_macro_',
   ...          'L8',))),
   ...     __import__('builtins').setattr(
   ...       _macro_,
   ...       'L8',
   ...       _fnxAUTO7_))[-1])(),
   ...   # __main__.._macro_.defmacro
   ...   # hissp.basic.._macro_.let
   ...   (lambda _fnxAUTO7_=(lambda *_exprxAUTO36_:
   ...     (lambda *xAUTO0_:xAUTO0_)(
   ...       'lambda',
   ...       'ABCDEFGHI',
   ...       _exprxAUTO36_)):(
   ...     __import__('builtins').setattr(
   ...       _fnxAUTO7_,
   ...       '__qualname__',
   ...       ('.').join(
   ...         ('_macro_',
   ...          'L9',))),
   ...     __import__('builtins').setattr(
   ...       _macro_,
   ...       'L9',
   ...       _fnxAUTO7_))[-1])(),
   ...   # __main__.._macro_.defmacro
   ...   # hissp.basic.._macro_.let
   ...   (lambda _fnxAUTO7_=(lambda *_exprxAUTO36_:
   ...     (lambda *xAUTO0_:xAUTO0_)(
   ...       'lambda',
   ...       'ABCDEFGHIJ',
   ...       _exprxAUTO36_)):(
   ...     __import__('builtins').setattr(
   ...       _fnxAUTO7_,
   ...       '__qualname__',
   ...       ('.').join(
   ...         ('_macro_',
   ...          'L10',))),
   ...     __import__('builtins').setattr(
   ...       _macro_,
   ...       'L10',
   ...       _fnxAUTO7_))[-1])(),
   ...   # __main__.._macro_.defmacro
   ...   # hissp.basic.._macro_.let
   ...   (lambda _fnxAUTO7_=(lambda *_exprxAUTO36_:
   ...     (lambda *xAUTO0_:xAUTO0_)(
   ...       'lambda',
   ...       'ABCDEFGHIJK',
   ...       _exprxAUTO36_)):(
   ...     __import__('builtins').setattr(
   ...       _fnxAUTO7_,
   ...       '__qualname__',
   ...       ('.').join(
   ...         ('_macro_',
   ...          'L11',))),
   ...     __import__('builtins').setattr(
   ...       _macro_,
   ...       'L11',
   ...       _fnxAUTO7_))[-1])(),
   ...   # __main__.._macro_.defmacro
   ...   # hissp.basic.._macro_.let
   ...   (lambda _fnxAUTO7_=(lambda *_exprxAUTO36_:
   ...     (lambda *xAUTO0_:xAUTO0_)(
   ...       'lambda',
   ...       'ABCDEFGHIJKL',
   ...       _exprxAUTO36_)):(
   ...     __import__('builtins').setattr(
   ...       _fnxAUTO7_,
   ...       '__qualname__',
   ...       ('.').join(
   ...         ('_macro_',
   ...          'L12',))),
   ...     __import__('builtins').setattr(
   ...       _macro_,
   ...       'L12',
   ...       _fnxAUTO7_))[-1])(),
   ...   # __main__.._macro_.defmacro
   ...   # hissp.basic.._macro_.let
   ...   (lambda _fnxAUTO7_=(lambda *_exprxAUTO36_:
   ...     (lambda *xAUTO0_:xAUTO0_)(
   ...       'lambda',
   ...       'ABCDEFGHIJKLM',
   ...       _exprxAUTO36_)):(
   ...     __import__('builtins').setattr(
   ...       _fnxAUTO7_,
   ...       '__qualname__',
   ...       ('.').join(
   ...         ('_macro_',
   ...          'L13',))),
   ...     __import__('builtins').setattr(
   ...       _macro_,
   ...       'L13',
   ...       _fnxAUTO7_))[-1])(),
   ...   # __main__.._macro_.defmacro
   ...   # hissp.basic.._macro_.let
   ...   (lambda _fnxAUTO7_=(lambda *_exprxAUTO36_:
   ...     (lambda *xAUTO0_:xAUTO0_)(
   ...       'lambda',
   ...       'ABCDEFGHIJKLMN',
   ...       _exprxAUTO36_)):(
   ...     __import__('builtins').setattr(
   ...       _fnxAUTO7_,
   ...       '__qualname__',
   ...       ('.').join(
   ...         ('_macro_',
   ...          'L14',))),
   ...     __import__('builtins').setattr(
   ...       _macro_,
   ...       'L14',
   ...       _fnxAUTO7_))[-1])(),
   ...   # __main__.._macro_.defmacro
   ...   # hissp.basic.._macro_.let
   ...   (lambda _fnxAUTO7_=(lambda *_exprxAUTO36_:
   ...     (lambda *xAUTO0_:xAUTO0_)(
   ...       'lambda',
   ...       'ABCDEFGHIJKLMNO',
   ...       _exprxAUTO36_)):(
   ...     __import__('builtins').setattr(
   ...       _fnxAUTO7_,
   ...       '__qualname__',
   ...       ('.').join(
   ...         ('_macro_',
   ...          'L15',))),
   ...     __import__('builtins').setattr(
   ...       _macro_,
   ...       'L15',
   ...       _fnxAUTO7_))[-1])(),
   ...   # __main__.._macro_.defmacro
   ...   # hissp.basic.._macro_.let
   ...   (lambda _fnxAUTO7_=(lambda *_exprxAUTO36_:
   ...     (lambda *xAUTO0_:xAUTO0_)(
   ...       'lambda',
   ...       'ABCDEFGHIJKLMNOP',
   ...       _exprxAUTO36_)):(
   ...     __import__('builtins').setattr(
   ...       _fnxAUTO7_,
   ...       '__qualname__',
   ...       ('.').join(
   ...         ('_macro_',
   ...          'L16',))),
   ...     __import__('builtins').setattr(
   ...       _macro_,
   ...       'L16',
   ...       _fnxAUTO7_))[-1])(),
   ...   # __main__.._macro_.defmacro
   ...   # hissp.basic.._macro_.let
   ...   (lambda _fnxAUTO7_=(lambda *_exprxAUTO36_:
   ...     (lambda *xAUTO0_:xAUTO0_)(
   ...       'lambda',
   ...       'ABCDEFGHIJKLMNOPQ',
   ...       _exprxAUTO36_)):(
   ...     __import__('builtins').setattr(
   ...       _fnxAUTO7_,
   ...       '__qualname__',
   ...       ('.').join(
   ...         ('_macro_',
   ...          'L17',))),
   ...     __import__('builtins').setattr(
   ...       _macro_,
   ...       'L17',
   ...       _fnxAUTO7_))[-1])(),
   ...   # __main__.._macro_.defmacro
   ...   # hissp.basic.._macro_.let
   ...   (lambda _fnxAUTO7_=(lambda *_exprxAUTO36_:
   ...     (lambda *xAUTO0_:xAUTO0_)(
   ...       'lambda',
   ...       'ABCDEFGHIJKLMNOPQR',
   ...       _exprxAUTO36_)):(
   ...     __import__('builtins').setattr(
   ...       _fnxAUTO7_,
   ...       '__qualname__',
   ...       ('.').join(
   ...         ('_macro_',
   ...          'L18',))),
   ...     __import__('builtins').setattr(
   ...       _macro_,
   ...       'L18',
   ...       _fnxAUTO7_))[-1])(),
   ...   # __main__.._macro_.defmacro
   ...   # hissp.basic.._macro_.let
   ...   (lambda _fnxAUTO7_=(lambda *_exprxAUTO36_:
   ...     (lambda *xAUTO0_:xAUTO0_)(
   ...       'lambda',
   ...       'ABCDEFGHIJKLMNOPQRS',
   ...       _exprxAUTO36_)):(
   ...     __import__('builtins').setattr(
   ...       _fnxAUTO7_,
   ...       '__qualname__',
   ...       ('.').join(
   ...         ('_macro_',
   ...          'L19',))),
   ...     __import__('builtins').setattr(
   ...       _macro_,
   ...       'L19',
   ...       _fnxAUTO7_))[-1])(),
   ...   # __main__.._macro_.defmacro
   ...   # hissp.basic.._macro_.let
   ...   (lambda _fnxAUTO7_=(lambda *_exprxAUTO36_:
   ...     (lambda *xAUTO0_:xAUTO0_)(
   ...       'lambda',
   ...       'ABCDEFGHIJKLMNOPQRST',
   ...       _exprxAUTO36_)):(
   ...     __import__('builtins').setattr(
   ...       _fnxAUTO7_,
   ...       '__qualname__',
   ...       ('.').join(
   ...         ('_macro_',
   ...          'L20',))),
   ...     __import__('builtins').setattr(
   ...       _macro_,
   ...       'L20',
   ...       _fnxAUTO7_))[-1])(),
   ...   # __main__.._macro_.defmacro
   ...   # hissp.basic.._macro_.let
   ...   (lambda _fnxAUTO7_=(lambda *_exprxAUTO36_:
   ...     (lambda *xAUTO0_:xAUTO0_)(
   ...       'lambda',
   ...       'ABCDEFGHIJKLMNOPQRSTU',
   ...       _exprxAUTO36_)):(
   ...     __import__('builtins').setattr(
   ...       _fnxAUTO7_,
   ...       '__qualname__',
   ...       ('.').join(
   ...         ('_macro_',
   ...          'L21',))),
   ...     __import__('builtins').setattr(
   ...       _macro_,
   ...       'L21',
   ...       _fnxAUTO7_))[-1])(),
   ...   # __main__.._macro_.defmacro
   ...   # hissp.basic.._macro_.let
   ...   (lambda _fnxAUTO7_=(lambda *_exprxAUTO36_:
   ...     (lambda *xAUTO0_:xAUTO0_)(
   ...       'lambda',
   ...       'ABCDEFGHIJKLMNOPQRSTUV',
   ...       _exprxAUTO36_)):(
   ...     __import__('builtins').setattr(
   ...       _fnxAUTO7_,
   ...       '__qualname__',
   ...       ('.').join(
   ...         ('_macro_',
   ...          'L22',))),
   ...     __import__('builtins').setattr(
   ...       _macro_,
   ...       'L22',
   ...       _fnxAUTO7_))[-1])(),
   ...   # __main__.._macro_.defmacro
   ...   # hissp.basic.._macro_.let
   ...   (lambda _fnxAUTO7_=(lambda *_exprxAUTO36_:
   ...     (lambda *xAUTO0_:xAUTO0_)(
   ...       'lambda',
   ...       'ABCDEFGHIJKLMNOPQRSTUVW',
   ...       _exprxAUTO36_)):(
   ...     __import__('builtins').setattr(
   ...       _fnxAUTO7_,
   ...       '__qualname__',
   ...       ('.').join(
   ...         ('_macro_',
   ...          'L23',))),
   ...     __import__('builtins').setattr(
   ...       _macro_,
   ...       'L23',
   ...       _fnxAUTO7_))[-1])(),
   ...   # __main__.._macro_.defmacro
   ...   # hissp.basic.._macro_.let
   ...   (lambda _fnxAUTO7_=(lambda *_exprxAUTO36_:
   ...     (lambda *xAUTO0_:xAUTO0_)(
   ...       'lambda',
   ...       'ABCDEFGHIJKLMNOPQRSTUVWX',
   ...       _exprxAUTO36_)):(
   ...     __import__('builtins').setattr(
   ...       _fnxAUTO7_,
   ...       '__qualname__',
   ...       ('.').join(
   ...         ('_macro_',
   ...          'L24',))),
   ...     __import__('builtins').setattr(
   ...       _macro_,
   ...       'L24',
   ...       _fnxAUTO7_))[-1])(),
   ...   # __main__.._macro_.defmacro
   ...   # hissp.basic.._macro_.let
   ...   (lambda _fnxAUTO7_=(lambda *_exprxAUTO36_:
   ...     (lambda *xAUTO0_:xAUTO0_)(
   ...       'lambda',
   ...       'ABCDEFGHIJKLMNOPQRSTUVWXY',
   ...       _exprxAUTO36_)):(
   ...     __import__('builtins').setattr(
   ...       _fnxAUTO7_,
   ...       '__qualname__',
   ...       ('.').join(
   ...         ('_macro_',
   ...          'L25',))),
   ...     __import__('builtins').setattr(
   ...       _macro_,
   ...       'L25',
   ...       _fnxAUTO7_))[-1])(),
   ...   # __main__.._macro_.defmacro
   ...   # hissp.basic.._macro_.let
   ...   (lambda _fnxAUTO7_=(lambda *_exprxAUTO36_:
   ...     (lambda *xAUTO0_:xAUTO0_)(
   ...       'lambda',
   ...       'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
   ...       _exprxAUTO36_)):(
   ...     __import__('builtins').setattr(
   ...       _fnxAUTO7_,
   ...       '__qualname__',
   ...       ('.').join(
   ...         ('_macro_',
   ...          'L26',))),
   ...     __import__('builtins').setattr(
   ...       _macro_,
   ...       'L26',
   ...       _fnxAUTO7_))[-1])())[-1])()

Whoa.

That little bit of Lissp expanded into *that much Python*.
It totally works too.

.. code-block:: REPL

   #> ((L3 add C (add A B))
   #.. "A" "B" "C")
   >>> # L3
   ... (lambda A,B,C:
   ...   add(
   ...     C,
   ...     add(
   ...       A,
   ...       B)))(
   ...   ('A'),
   ...   ('B'),
   ...   ('C'))
   'CAB'

   #> (L26)
   >>> # L26
   ... (lambda A,B,C,D,E,F,G,H,I,J,K,L,M,N,O,P,Q,R,S,T,U,V,W,X,Y,Z:())
   <function <lambda> at ...>

   #> (L13)
   >>> # L13
   ... (lambda A,B,C,D,E,F,G,H,I,J,K,L,M:())
   <function <lambda> at ...>

   #> ((L0 print "Hello, World!"))
   >>> # L0
   ... (lambda :
   ...   print(
   ...     ('Hello, World!')))()
   Hello, World!

How does this work?
I don't blame you for glossing over the Python output.
It's pretty big this time.
I mostly ignore it when it gets longer than a few lines,
unless there's something in particular I'm looking for.

But let's look at this Lissp snippet again, more carefully.

.. code-block:: Lissp

   .#`(progn ,@(map (lambda (i)
                      `(defmacro ,(.format "L{}" i)
                                 (: :* $#expr)
                         `(lambda ,',(getitem "ABCDEFGHIJKLMNOPQRSTUVWXYZ" (slice i))
                            ,$#expr)))
                    (range 27)))

It's injecting some Hissp we generated with a template.
That's the first two reader macros ``.#`` and :literal:`\``.
The `progn` sequences multiple expressions for their side effects.
It's like having multiple "statements" in a single expression.
We splice in multiple expressions generated with a `map`.
The `map` generates a code tuple for each integer from the `range`.

The lambda takes the int ``i`` from the `range` and produces a `defmacro` *form*,
(not a *macro*, the *code for defining one*)
which, when run in the `progn` by our inject,
will define a macro.

Nothing is above abstraction in Lissp.
`defmacro` forms are *still code*,
and Hissp code is made of data structures we can manipulate programmatically.
We can make them with templates like anything else.

We need to give each one a different name,
so we combine the ``i`` with ``"L"``.

The parameters tuple for `defmacro` contains a gensym, ``$#expr``,
since it shouldn't be qualified and it doesn't need to be an anaphor.

The next part is tricky.
We've directly nested a template inside another one,
without unquoting it first,
because the defmacro also needed a template to work.
Note that you can unquote through nested templates.
This is an important capability,
but it's a little mind-bending.

Finally, we slice the params string to the appropriate number of characters.

Take a breath.
We're not done.

Macros Can Read Code Too.
~~~~~~~~~~~~~~~~~~~~~~~~~

We're still providing more information than is required.
You have to change the name of your macro based on the number of arguments you expect.
But can't the macro infer this based on which parameters your expression contains?

Also, we're kind of running out of alphabet when we start on ``X``,
You often see 4-D vectors labeled (x, y, z, w),
but beyond that, mathematicians just number them with subscripts.

We got around this by starting at ``A`` instead,
but then we're using up all of the uppercase ASCII one-character names.
We might want to save those for other things.
We're also limited to 26 parameters this way.
It's rare we'd need more than three or four,
but 26 seems kind of arbitrary.

So a better approach might be with numbered parameters, like ``X1``, ``X2``, ``X3``, etc.
Then, if you macro is smart enough,
it can look for the highest X-number in your expression
and automatically provide that many parameters for you.

We can create numbered X's the same way we created the numbered L's.

.. Lissp::

   #> (defmacro L (number : :* expr)
   #..  `(lambda ,(map (lambda (i)
   #..                   (.format "X{}" i))
   #..                 (range 1 (add 1 number)))
   #..     ,expr))
   >>> # defmacro
   ... # hissp.basic.._macro_.let
   ... (lambda _fnxAUTO7_=(lambda number,*expr:
   ...   (lambda *xAUTO0_:xAUTO0_)(
   ...     'lambda',
   ...     map(
   ...       (lambda i:
   ...         ('X{}').format(
   ...           i)),
   ...       range(
   ...         (1),
   ...         add(
   ...           (1),
   ...           number))),
   ...     expr)):(
   ...   __import__('builtins').setattr(
   ...     _fnxAUTO7_,
   ...     '__qualname__',
   ...     ('.').join(
   ...       ('_macro_',
   ...        'L',))),
   ...   __import__('builtins').setattr(
   ...     _macro_,
   ...     'L',
   ...     _fnxAUTO7_))[-1])()


.. code-block:: REPL

   #> (L 10)
   >>> # L
   ... (lambda X1,X2,X3,X4,X5,X6,X7,X8,X9,X10:())
   <function <lambda> at ...>

   #> ((L 2 add X1 X2) "A" "B")
   >>> # L
   ... (lambda X1,X2:
   ...   add(
   ...     X1,
   ...     X2))(
   ...   ('A'),
   ...   ('B'))
   'AB'

This version uses a number as the first argument instead of baking them into the macro names.
We're using numbered parameters now, so there's no limit.
That takes care of *generating* the parameters,
but we're still providing an expected a number for them.

Let's make a slight tweak.

.. Lissp::

   #> (defmacro L (: :* expr)
   #..  `(lambda ,(map (lambda (i)
   #..                   (.format "X{}" i))
   #..                 (range 1 (add 1 (max-X expr))))
   #..     ,expr))
   >>> # defmacro
   ... # hissp.basic.._macro_.let
   ... (lambda _fnxAUTO7_=(lambda *expr:
   ...   (lambda *xAUTO0_:xAUTO0_)(
   ...     'lambda',
   ...     map(
   ...       (lambda i:
   ...         ('X{}').format(
   ...           i)),
   ...       range(
   ...         (1),
   ...         add(
   ...           (1),
   ...           maxxH_X(
   ...             expr)))),
   ...     expr)):(
   ...   __import__('builtins').setattr(
   ...     _fnxAUTO7_,
   ...     '__qualname__',
   ...     ('.').join(
   ...       ('_macro_',
   ...        'L',))),
   ...   __import__('builtins').setattr(
   ...     _macro_,
   ...     'L',
   ...     _fnxAUTO7_))[-1])()


What is this ``max-X``?
It's a venerable design technique known as *wishful thinking*.
We haven't implemented it yet.
This doesn't work.
But we *wish* it would find the maximum X number in the expression.

Can we just iterate through the expression and check?

.. Lissp::

   #> (define max-X
   #..  (lambda (expr)
   #..    (max (map (lambda (x)
   #..                (|| (when (is_ str (type x))
   #..                      (let (match (re..fullmatch "X([1-9][0-9]*)" x))
   #..                        (when match
   #..                          (int (.group match 1)))))
   #..                    0))
   #..              expr))))
   >>> # define
   ... __import__('operator').setitem(
   ...   __import__('builtins').globals(),
   ...   'maxxH_X',
   ...   (lambda expr:
   ...     max(
   ...       map(
   ...         (lambda x:
   ...           # xBAR_xBAR_
   ...           # hissp.basic.._macro_.let
   ...           (lambda _firstxAUTO33_=# when
   ...           # hissp.basic.._macro_.ifxH_else
   ...           (lambda test,*thenxH_else:
   ...             __import__('operator').getitem(
   ...               thenxH_else,
   ...               __import__('operator').not_(
   ...                 test))())(
   ...             is_(
   ...               str,
   ...               type(
   ...                 x)),
   ...             (lambda :
   ...               # hissp.basic.._macro_.progn
   ...               (lambda :
   ...                 # let
   ...                 (lambda match=__import__('re').fullmatch(
   ...                   ('X([1-9][0-9]*)'),
   ...                   x):
   ...                   # when
   ...                   # hissp.basic.._macro_.ifxH_else
   ...                   (lambda test,*thenxH_else:
   ...                     __import__('operator').getitem(
   ...                       thenxH_else,
   ...                       __import__('operator').not_(
   ...                         test))())(
   ...                     match,
   ...                     (lambda :
   ...                       # hissp.basic.._macro_.progn
   ...                       (lambda :
   ...                         int(
   ...                           match.group(
   ...                             (1))))()),
   ...                     (lambda :())))())()),
   ...             (lambda :())):
   ...             # hissp.basic.._macro_.ifxH_else
   ...             (lambda test,*thenxH_else:
   ...               __import__('operator').getitem(
   ...                 thenxH_else,
   ...                 __import__('operator').not_(
   ...                   test))())(
   ...               _firstxAUTO33_,
   ...               (lambda :_firstxAUTO33_),
   ...               (lambda :
   ...                 # hissp.basic..xAUTO_.xBAR_xBAR_
   ...                 (0))))()),
   ...         expr))))


You can experiment with macros you don't recognize in the REPL.
All the basic macros,
including the `|| <xBAR_xBAR_>`
and `when` were covered in the `quick start <lissp_quickstart>`.
We're using them to coalesce Python's awkward regex matches,
which can return ``None``, into a ``0``,
unless it's a string with a match.

It gets the parameters right:

.. code-block:: REPL

   #> ((L add X2 X1) : :* "AB")
   >>> # L
   ... (lambda X1,X2:
   ...   add(
   ...     X2,
   ...     X1))(
   ...   *('AB'))
   'BA'

Pretty cool.

.. code-block:: REPL

   #> ((L add X1 (add X2 X3))
   #.. : :* "BAR")
   >>> # L
   ... (lambda X1:
   ...   add(
   ...     X1,
   ...     add(
   ...       X2,
   ...       X3)))(
   ...   *('BAR'))
   Traceback (most recent call last):
     File "<console>", line 2, in <module>
   TypeError: <lambda>() takes 1 positional argument but 3 were given

Oh. Not that easy.
What happened?
The lambda only took one parameter,
even though the expression contained an ``X3``.

We need to be able to check for symbols nested in tuples.
This sounds like a job for recursion.
Lissp can do that with a class.

.. Lissp::

   #> (deftype Flattener ()
   #..  __init__ (lambda (self)
   #..             (setattr self 'accumulator []))
   #..  flatten (lambda (self form)
   #..            (any-for x form
   #..              (if-else (is_ (type x) tuple)
   #..                (self.flatten x)
   #..                (.append self.accumulator x))
   #..              False)
   #..            self.accumulator))
   >>> # deftype
   ... # hissp.basic.._macro_.define
   ... __import__('operator').setitem(
   ...   __import__('builtins').globals(),
   ...   'Flattener',
   ...   __import__('builtins').type(
   ...     'Flattener',
   ...     (lambda *xAUTO0_:xAUTO0_)(),
   ...     __import__('builtins').dict(
   ...       __init__=(lambda self:
   ...                  setattr(
   ...                    self,
   ...                    'accumulator',
   ...                    [])),
   ...       flatten=(lambda self,form:(
   ...                 # anyxH_for
   ...                 __import__('builtins').any(
   ...                   __import__('builtins').map(
   ...                     (lambda x:(
   ...                       # ifxH_else
   ...                       (lambda test,*thenxH_else:
   ...                         __import__('operator').getitem(
   ...                           thenxH_else,
   ...                           __import__('operator').not_(
   ...                             test))())(
   ...                         is_(
   ...                           type(
   ...                             x),
   ...                           tuple),
   ...                         (lambda :
   ...                           self.flatten(
   ...                             x)),
   ...                         (lambda :
   ...                           self.accumulator.append(
   ...                             x))),
   ...                       False)[-1]),
   ...                     form)),
   ...                 self.accumulator)[-1]))))


More basic macros here.
Search Hissp's docs if you can't figure out what they do.

``Flatten`` is a good utility to have for macros that have to read code.
Let's give it a nicer interface.

.. Lissp::

   #> (define flatten
   #..  (lambda (form)
   #..    (.flatten (Flattener) form)))
   >>> # define
   ... __import__('operator').setitem(
   ...   __import__('builtins').globals(),
   ...   'flatten',
   ...   (lambda form:
   ...     Flattener().flatten(
   ...       form)))


Now we can fix ``max-X``.

.. Lissp::

   #> (define max-X
   #..  (lambda (expr)
   #..    (max (map (lambda (x)
   #..                (|| (when (is_ str (type x))
   #..                      (let (match (re..fullmatch "X([1-9][0-9]*)" x))
   #..                        (when match
   #..                          (int (.group match 1)))))
   #..                    0))
   #..              (flatten expr)))))
   >>> # define
   ... __import__('operator').setitem(
   ...   __import__('builtins').globals(),
   ...   'maxxH_X',
   ...   (lambda expr:
   ...     max(
   ...       map(
   ...         (lambda x:
   ...           # xBAR_xBAR_
   ...           # hissp.basic.._macro_.let
   ...           (lambda _firstxAUTO33_=# when
   ...           # hissp.basic.._macro_.ifxH_else
   ...           (lambda test,*thenxH_else:
   ...             __import__('operator').getitem(
   ...               thenxH_else,
   ...               __import__('operator').not_(
   ...                 test))())(
   ...             is_(
   ...               str,
   ...               type(
   ...                 x)),
   ...             (lambda :
   ...               # hissp.basic.._macro_.progn
   ...               (lambda :
   ...                 # let
   ...                 (lambda match=__import__('re').fullmatch(
   ...                   ('X([1-9][0-9]*)'),
   ...                   x):
   ...                   # when
   ...                   # hissp.basic.._macro_.ifxH_else
   ...                   (lambda test,*thenxH_else:
   ...                     __import__('operator').getitem(
   ...                       thenxH_else,
   ...                       __import__('operator').not_(
   ...                         test))())(
   ...                     match,
   ...                     (lambda :
   ...                       # hissp.basic.._macro_.progn
   ...                       (lambda :
   ...                         int(
   ...                           match.group(
   ...                             (1))))()),
   ...                     (lambda :())))())()),
   ...             (lambda :())):
   ...             # hissp.basic.._macro_.ifxH_else
   ...             (lambda test,*thenxH_else:
   ...               __import__('operator').getitem(
   ...                 thenxH_else,
   ...                 __import__('operator').not_(
   ...                   test))())(
   ...               _firstxAUTO33_,
   ...               (lambda :_firstxAUTO33_),
   ...               (lambda :
   ...                 # hissp.basic..xAUTO_.xBAR_xBAR_
   ...                 (0))))()),
   ...         flatten(
   ...           expr)))))


Let's try again.

.. code-block:: REPL

   #> ((L add X1 (add X2 X3))
   #.. : :* "BAR")
   >>> # L
   ... (lambda X1,X2,X3:
   ...   add(
   ...     X1,
   ...     add(
   ...       X2,
   ...       X3)))(
   ...   *('BAR'))
   'BAR'

Try doing that with the C preprocessor!

Function Literals
~~~~~~~~~~~~~~~~~

Let's review. The code you need to make the version we have so far is

.. code-block:: Lissp

   (hissp.basic.._macro_.prelude)

   (defmacro L (: :* expr)
     `(lambda ,(map (lambda (i)
                      (.format "X{}" i))
                    (range 1 (add 1 (max-X expr))))
        ,expr))

   (define max-X
     (lambda (expr)
       (max (map (lambda (x)
                   (|| (when (is_ str (type x))
                         (let (match (re..fullmatch "X([1-9][0-9]*)" x))
                           (when match
                             (int (.group match 1)))))
                       0))
                 (flatten expr)))))

   (define flatten
     (lambda (form)
       (.flatten (Flattener) form)))

   (deftype Flattener ()
     __init__ (lambda (self)
                (setattr self 'accumulator []))
     flatten (lambda (self form)
               (any-for x form
                 (if-else (is_ (type x) tuple)
                   (self.flatten x)
                   (.append self.accumulator x))
                 False)
               self.accumulator))

Given all of this in a file named ``macros.lissp``,
you can start the REPL with these already loaded using the command

.. code-block:: Text

   $ lissp -i macros.lissp

rather than pasting them in.

You can use the resulting macro as a shorter lambda for higher-order functions:

.. code-block:: REPL

   #> (list (map (L add X1 X1) (range 10)))
   >>> list(
   ...   map(
   ...     # L
   ...     (lambda X1:
   ...       add(
   ...         X1,
   ...         X1)),
   ...     range(
   ...       (10))))
   [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]

It's still a little awkward.
It feels like the ``add`` should be in the first position,
but that's taken by the ``L``.
We can fix that with a reader macro.

Reader Syntax
`````````````

To use reader macros unqualified,
you must define them in ``_macro_`` with a name ending in a ``#``.

.. Lissp::

   #> (defmacro X\# (expr)
   #..  `(L ,@expr))
   >>> # defmacro
   ... # hissp.basic.._macro_.let
   ... (lambda _fnxAUTO7_=(lambda expr:
   ...   (lambda *xAUTO0_:xAUTO0_)(
   ...     '__main__.._macro_.L',
   ...     *expr)):(
   ...   __import__('builtins').setattr(
   ...     _fnxAUTO7_,
   ...     '__qualname__',
   ...     ('.').join(
   ...       ('_macro_',
   ...        'XxHASH_',))),
   ...   __import__('builtins').setattr(
   ...     _macro_,
   ...     'XxHASH_',
   ...     _fnxAUTO7_))[-1])()

We have to escape the ``#`` with a backslash
or the reader will recognize the name as a macro rather than a symbol
and immediately try to apply it to ``(expr)``, which is not what we want.
Notice that we still used a `defmacro`,
like we do for compiler macros.
It's the way you invoke it that makes it happen at read time:

.. code-block:: REPL

   #> (list (map X#(add X1 X1) ; Read-time expansion.
   #..           (range 10)))
   >>> list(
   ...   map(
   ...     # __main__.._macro_.L
   ...     (lambda X1:
   ...       add(
   ...         X1,
   ...         X1)),
   ...     range(
   ...       (10))))
   [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]

   #> (list (map (X\# (add X1 X1)) ; Compile-time expansion.
   #..           (range 10)))
   >>> list(
   ...   map(
   ...     # XxHASH_
   ...     # __main__.._macro_.L
   ...     (lambda X1:
   ...       add(
   ...         X1,
   ...         X1)),
   ...     range(
   ...       (10))))
   [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]


Reader macros like this effectively create new read syntax
by reinterpreting existing read syntax.

So now we have function literals.

These are very similar to the function literals in Clojure,
and we implemented them from scratch in about a page of code.
That's the power of metaprogramming.
You can copy features from other languages,
tweak them, and experiment with your own.

Clojure's version still has a couple more features.
Let's add them.

Catch-All Parameter
```````````````````

.. Lissp::

   #> (defmacro L (: :* expr)
   #..  `(lambda (,@(map (lambda (i)
   #..                     (.format "X{}" i))
   #..                   (range 1 (add 1 (max-X expr))))
   #..            :
   #..            ,@(when (contains (flatten expr)
   #..                              'Xi)
   #..                `(:* ,'Xi)))
   #..     ,expr))
   >>> # defmacro
   ... # hissp.basic.._macro_.let
   ... (lambda _fnxAUTO7_=(lambda *expr:
   ...   (lambda *xAUTO0_:xAUTO0_)(
   ...     'lambda',
   ...     (lambda *xAUTO0_:xAUTO0_)(
   ...       *map(
   ...          (lambda i:
   ...            ('X{}').format(
   ...              i)),
   ...          range(
   ...            (1),
   ...            add(
   ...              (1),
   ...              maxxH_X(
   ...                expr)))),
   ...       ':',
   ...       *# when
   ...        # hissp.basic.._macro_.ifxH_else
   ...        (lambda test,*thenxH_else:
   ...          __import__('operator').getitem(
   ...            thenxH_else,
   ...            __import__('operator').not_(
   ...              test))())(
   ...          contains(
   ...            flatten(
   ...              expr),
   ...            'Xi'),
   ...          (lambda :
   ...            # hissp.basic.._macro_.progn
   ...            (lambda :
   ...              (lambda *xAUTO0_:xAUTO0_)(
   ...                ':*',
   ...                'Xi'))()),
   ...          (lambda :()))),
   ...     expr)):(
   ...   __import__('builtins').setattr(
   ...     _fnxAUTO7_,
   ...     '__qualname__',
   ...     ('.').join(
   ...       ('_macro_',
   ...        'L',))),
   ...   __import__('builtins').setattr(
   ...     _macro_,
   ...     'L',
   ...     _fnxAUTO7_))[-1])()

.. code-block:: REPL

   #> (X#(print X1 X2 Xi) 1 2 3 4 5)
   >>> # __main__.._macro_.L
   ... (lambda X1,X2,*Xi:
   ...   print(
   ...     X1,
   ...     X2,
   ...     Xi))(
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
                                 'Xi)
                   `(:* ,'Xi)))
        ,expr))

We splice the logic that makes the numbered parameters into the new parameters tuple.
Following that is the colon separator.
Remember that it's always allowed in Hissp's lambda forms,
even if you don't need it,
which makes this kind of metaprogramming easier.

Following that is the code for a star arg.
The ``Xi`` is an anaphor,
so it must be interpolated into the template to prevent automatic qualification.
The `when` macro will return an empty tuple when its condition is false.
Attempting to splice in an empty tuple conveniently doesn't do anything
(like "nil punning" in other Lisps),
so the ``Xi`` anaphor is only present in the parameters tuple when the
(flattened) ``expr`` `contains <operator.contains>` it.

It would be nice for Python interoperability if we also had an anaphor for the kwargs.
Clojure doesn't have these.
Adding this is left as an exercise.
Can you figure out how to do it?

Implied Number 1
````````````````

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
   #..                   (range 1 (add 1 (|| (max-X expr)
   #..                                       (contains (flatten expr)
   #..                                                 'X)))))
   #..            :
   #..            ,@(when (contains (flatten expr)
   #..                              'Xi)
   #..                `(:* ,'Xi)))
   #..     ,(if-else (contains (flatten expr)
   #..                         'X)
   #..        `(let (,'X ,'X1)
   #..           ,expr)
   #..        expr)))
   >>> # defmacro
   ... # hissp.basic.._macro_.let
   ... (lambda _fnxAUTO7_=(lambda *expr:
   ...   (lambda *xAUTO0_:xAUTO0_)(
   ...     'lambda',
   ...     (lambda *xAUTO0_:xAUTO0_)(
   ...       *map(
   ...          (lambda i:
   ...            ('X{}').format(
   ...              i)),
   ...          range(
   ...            (1),
   ...            add(
   ...              (1),
   ...              # xBAR_xBAR_
   ...              # hissp.basic.._macro_.let
   ...              (lambda _firstxAUTO28_=maxxH_X(
   ...                expr):
   ...                # hissp.basic.._macro_.ifxH_else
   ...                (lambda test,*thenxH_else:
   ...                  __import__('operator').getitem(
   ...                    thenxH_else,
   ...                    __import__('operator').not_(
   ...                      test))())(
   ...                  _firstxAUTO28_,
   ...                  (lambda :_firstxAUTO28_),
   ...                  (lambda :
   ...                    # hissp.basic..xAUTO_.xBAR_xBAR_
   ...                    contains(
   ...                      flatten(
   ...                        expr),
   ...                      'X'))))()))),
   ...       ':',
   ...       *# when
   ...        # hissp.basic.._macro_.ifxH_else
   ...        (lambda test,*thenxH_else:
   ...          __import__('operator').getitem(
   ...            thenxH_else,
   ...            __import__('operator').not_(
   ...              test))())(
   ...          contains(
   ...            flatten(
   ...              expr),
   ...            'Xi'),
   ...          (lambda :
   ...            # hissp.basic.._macro_.progn
   ...            (lambda :
   ...              (lambda *xAUTO0_:xAUTO0_)(
   ...                ':*',
   ...                'Xi'))()),
   ...          (lambda :()))),
   ...     # ifxH_else
   ...     (lambda test,*thenxH_else:
   ...       __import__('operator').getitem(
   ...         thenxH_else,
   ...         __import__('operator').not_(
   ...           test))())(
   ...       contains(
   ...         flatten(
   ...           expr),
   ...         'X'),
   ...       (lambda :
   ...         (lambda *xAUTO0_:xAUTO0_)(
   ...           '__main__.._macro_.let',
   ...           (lambda *xAUTO0_:xAUTO0_)(
   ...             'X',
   ...             'X1'),
   ...           expr)),
   ...       (lambda :expr)))):(
   ...   __import__('builtins').setattr(
   ...     _fnxAUTO7_,
   ...     '__qualname__',
   ...     ('.').join(
   ...       ('_macro_',
   ...        'L',))),
   ...   __import__('builtins').setattr(
   ...     _macro_,
   ...     'L',
   ...     _fnxAUTO7_))[-1])()

.. code-block:: REPL

   #> (list (map X#(add X X1) (range 10)))
   >>> list(
   ...   map(
   ...     # __main__.._macro_.L
   ...     (lambda X1:
   ...       # __main__.._macro_.let
   ...       (lambda X=X1:
   ...         add(
   ...           X,
   ...           X1))()),
   ...     range(
   ...       (10))))
   [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]

Now both ``X`` and ``X1`` refer to the same value,
even if you mix them.

Read the macro and its outputs carefully.
This version uses a bool pun.
Recall that ``False`` is a special case of ``0``
and ``True`` is a special case of ``1`` in Python.

The design could be improved a bit.
You'll probably want some automated test cases before refactoring.
Writing tests is a little beyond the scope of this lesson,
but you can use the standard library unit test class in Lissp, just like Python.

There are several repetitions of ``flatten`` and `contains <operator.contains>`.
Don't worry too much about the efficiency of code that only runs once at compile time.
What matters is what comes out in the expansions.

You could factor these out using a `let` and local variable.
But sometimes a terse implementation is the clearest name.
You might also consider flattening before passing to ``max-X``
instead of letting ``max-X`` do it,
because then you can give it the same local variable.

Another thing to consider is that you might change the ``X``'s to ``%``'s,
and then it would really look like Clojure.
This should not be hard.
It would require munging,
with the tradeoffs that entails for Python interop or other Hissp readers.
Python already has an operator named ``%``.
If you want to give `mod <operator.mod>` that name,
then you might want to stick with the ``X``,
or remove the special case aliasing ``%1`` to ``%``.
Also, rather than ``%&`` for the catch-all as in Clojure,
a ``%*`` might be more consistent if you've also got a kwargs parameter,
which you could call ``%**``.

Results
```````

Are we shorter than Python now?

.. code-block:: Text

   lambda x:x*x
   %#(* % %)

Did we lose generality?
Yes, but not much.
You can't really nest these.
The parameters get generated even if the only occurrence in the expression is quoted.
This is the kind of thing to be mindful of.
If you're not sure about something,
try it in the REPL.
But Clojure's version has the same problems,
and it gets used quite a lot.

Why You Should Be Reluctant to Use Python Injections
````````````````````````````````````````````````````

Suppose we wanted to use Python infix notation for a complex formula.

Do you see the problem with this?

.. code-block:: Lissp

   %#(.#"(-%2 + (%2**2 - 4*%1*%3)**0.5)/(2*%1)")

This was supposed to be the quadratic formula.
The ``%`` is an operator in Python,
and it can't be unary.
In an injection you would have to spell it using the munged name ``xPCENT_``.
But what if we had kept the ``X``?

.. code-block:: REPL

   #> X#(.#"(-X2 + (X2**2 - 4*X1*X3)**0.5)/(2*X1)")
   >>> # __main__.._macro_.L
   ... (lambda :(-X2 + (X2**2 - 4*X1*X3)**0.5)/(2*X1)())
   <function <lambda> at ...>

It looks like we're trying to invoke the formula itself,
which would evaluate to a number, not a callable,
so this doesn't really make sense.

The macro is expecting at least one function in prefix notation.
Sure, the macro could be modified, but
maybe we can do the divide in prefix and keep the others infix?
This doesn't look too bad if you think of it like a fraction bar.

.. code-block:: REPL

   #> X#(truediv .#"(-X2 + (X2**2 - 4*X1*X3)**0.5)"
   #..           .#"(2*X1)")
   >>> # __main__.._macro_.L
   ... (lambda :
   ...   truediv(
   ...     (-X2 + (X2**2 - 4*X1*X3)**0.5),
   ...     (2*X1)))
   <function <lambda> at ...>

Now the formula looks right,
but look at the compiled Python output.
This lambda takes no parameters!
Python injections hide information that code-reading macros need to work.
A macro that doesn't have to read the code,
like our ``L3``, would have worked fine.

The code-reading macro was unable to detect any matching symbols
because it doesn't look inside the injected strings.
In principle it *could have*,
but it might be a lot more work if you want it to be reliable.
It could function if the highest parameter also appeared outside the string,
but at that point, you might as well use a normal lambda.

Regex might be good enough for a simple case like this,
but even if you write it very carefully,
are you sure you're catching all the edge cases?
To really do it right,
you'd have to *parse the AST*.
The whole point of using Hissp tuples instead is so you don't have to do this.
Hissp is a kind of AST with lower complexity.

Arguably, we didn't do it right either since it still detects anaphors even if they're quoted,
but this level is good enough for Clojure.
A simple basic syntax means there are relatively few edge cases.

Hissp is so simple that a full code-walking macro would only have to pre-expand all macros,
and handle atoms, calls, ``quote``, and ``lambda``.

.. TODO: Which we will be demonstrating later!

If you add injections to the list,
then you also have to handle the entirety of all Python expressions.
Don't expect Hissp macros to do this.
Be reluctant to use Python injections,
and be aware of where they might break things.
They're mainly useful as performance optimizations.
In principle,
you should be able to do everything else without them.

Attach
------

.. TODO: attach
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

.. TODO: base 6, tau

.. TODO: defmacro/g defmacro!
.. TODO: destructuring bind (iterable only?)
.. TODO: destructuring lambda (iterable only?)

.. TODO: one-shot self-referential using reader macros
         multiary reader macros via stack
         reader macro namespacing via custom _macro_ class

.. TODO: Lisp-2 via custom _macro_ class
.. TODO: yield and code-walking
