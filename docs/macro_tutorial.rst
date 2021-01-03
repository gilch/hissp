.. Copyright 2020, 2021 Matthew Egan Odendahl

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
and have to be repeated each time they're needed.

To someone who started out in assembly or BASIC, or C, or even Java,
Python seems marvelously high-level, once mastered.
Python makes everything that was so tedious before `seem *so easy* <https://xkcd.com/353/>`_.

But the advanced Python developer eventually starts to notice the cracks.
You can get a lot further in Python, but like the old GOTO spaghetti code,
large enough projects start to collapse under their own weight.
Python seemed so easy before,
but certain repeated patterns can't be abstracted away.
You're stuck with a certain amount of boilerplate and ceremony.

Programmers comfortable with C,
but unfamiliar with Python,
will tend to write C idioms in Python,
like using explicit indexes into lists in for loops over a `range`,
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

****

If you're new to Lisp,
go back and read the style guide if you haven't already.
Understanding how Lisp is *formatted* helps you to read it,
not just write it.
And you will need to read it.

The previous tutorial was mostly about learning how to program with
a subset of Python in a new skin.
This one is about using that knowledge to reprogram the skin itself.

If you don't know the basics from the `previous tutorial <tutorial>`,
go back and read that now, or at least skim the `quick start <lissp_quickstart>`.

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
You might already develop Python that way.
A good editor can be configured to send selected text to another process
with a simple keyboard command,
but copy-and-paste into a terminal window will do.

Setting up your editor for Lissp is beyond the scope of this tutorial.
If you're not already comfortable with Emacs and Paredit,
give Parinfer a try.
It's probably easiest to set up in Atom.

Shorter Lambdas
---------------
.. TODO: xi / %#

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

Wouldn't it be nice if we could give lambda a shorter name?

.. code-block:: Python

   L = lambda

Could we then use ``L`` in place of ``lambda``?
Maybe like this?

.. code-block:: Python

   squares = map(L x: x * x, range(10))

Alas, this doesn't work.
The ``L = lambda`` is a syntax error.
(Of course, I'd probably just use a generator expression here.
It's only an example.)

They say that in Python everything is an object.
but it's still not quite true, is it?
``lambda`` isn't an object in Python.
It's not anything.
If you're rolling your eyes and thinking,
"Why would I even expect this to work?"
Then you're still thinking inside the Python box.

You can store class and function objects in variables
and pass them as arguments to functions in Python.
To someone who came from a language without higher-order functions,
this feels like breaking the rules.
Using it effectively feels like amazing out-of-the-box thinking.

Let's begin.

Warm-up
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
   ...   ('\n'
   ...    'from operator import *\n'
   ...    'from itertools import *\n'
   ...    'try:\n'
   ...    '    from hissp.basic import _macro_\n'
   ...    "    _macro_ = __import__('types').SimpleNamespace(**vars(_macro_))\n"
   ...    'except ModuleNotFoundError:\n'
   ...    '    pass'))

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
   File "<input>", line 1
     squares = map(L x: x * x, range(10))
                    ^
   SyntaxError: invalid syntax

That's still a syntax error.
It just happened later.

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
   ...       x,
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
   >>> ('define', 'squares', ('map', ('L', 'x', ('mul', 'x', 'x')), ('range', 10)))
   ('define', 'squares', ('map', ('L', 'x', ('mul', 'x', 'x')), ('range', 10)))


Hissp isn't compiling it like a special form.
We don't want that ``'L'`` string in the Hissp, but ``'lambda'``.
Is that possible? It is with one more step.
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

But Python is such a marvelously high-level language can't it do that too?
No, it really can't:

>>> squares = map(eval(f"{L} x: x * x"), range(10))
>>> list(squares)
[0, 1, 4, 9, 16, 25, 36, 49, 64, 81]

You can get pretty close to the same idea,
but that's about the best Python can do.
It didn't help, did it? Compare:

.. code-block:: Python

    eval(f"{L} x: x * x")
    lambda x: x * x

It got longer!
This was so easy in Lissp,
but so awkward in Python.

It gets better.

Simple compiler macros
~~~~~~~~~~~~~~~~~~~~~~

We're not actually shorter yet:

.. code-block:: Text

   (.#L (x)
     (mul x x))
   lambda x: x * x

If you like, we can assign a shorter name for `mul <operator.mul>`:

.. code-block:: REPL

   #> (define * mul)
   >>> # define
   ... __import__('operator').setitem(
   ...   __import__('builtins').globals(),
   ...   'xSTAR_',
   ...   mul)

And the params tuple doesn't actually have to be a tuple:

.. code-block:: Text

   (.#L x (* x x))
   lambda x: x * x

Symbols become strings which are iterables containing character strings.
This only works because the variable name is a single character.
Now we're the same length as Python.

Given a tuple containing the *minimum* amount of information,
we expand that into the necessary code using a macro.
Isn't there something extra here?
With a compiler macro, we won't need the inject.

The template needs to look something like
``(lambda <params> <body>)``.

.. code-block:: REPL

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
   ...       ('_macro_', 'L'))),
   ...   __import__('builtins').setattr(
   ...     _macro_,
   ...     'L',
   ...     _fnxAUTO7_))[-1])()
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

.. code-block:: REPL

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
   ...       ('_macro_', 'L'))),
   ...   __import__('builtins').setattr(
   ...     _macro_,
   ...     'L',
   ...     _fnxAUTO7_))[-1])()

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
but what if needed two?

You might already guess how we might do this:

.. code-block:: REPL

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
   ...       ('_macro_', 'L2'))),
   ...   __import__('builtins').setattr(
   ...     _macro_,
   ...     'L2',
   ...     _fnxAUTO7_))[-1])()
   #> (L2 * X Y)
   >>> # L2
   ... (lambda X,Y:
   ...   xSTAR_(
   ...     X,
   ...     Y))

That wasn't hard,
and between ``L`` and ``L2``,
we've probably covered 80% of short-lambda use cases.
But you can see the pattern here.
We could generalize to an ``L3`` with a ``Z`` parameter,
and then we've run out of alphabet.

When you see a "design pattern" in Lissp,
you don't keep repeating it.

Nothing is above abstraction
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Are you ready for this?
You've seen all these pieces before,
even if you haven't realized they could be used this way.

Don't panic.

.. code-block:: REPL

   #> .#`(progn ,@(map (lambda (i)
   #..                   `(defmacro ,(.format "L{}" i)
   #..                              (: :* $#expr)
   #..                      `(lambda ,',(getitem "XYZ" (slice i))
   #..                         ,$#expr)))
   #..                 (range 1 4)))
   >>> # __main__.._macro_.progn
   ... (lambda :(
   ...   # __main__.._macro_.defmacro
   ...   # hissp.basic.._macro_.let
   ...   (lambda _fnxAUTO7_=(lambda *_exprxAUTO151_:
   ...     (lambda *xAUTO0_:xAUTO0_)(
   ...       'lambda',
   ...       'X',
   ...       _exprxAUTO151_)):(
   ...     __import__('builtins').setattr(
   ...       _fnxAUTO7_,
   ...       '__qualname__',
   ...       ('.').join(
   ...         ('_macro_', 'L1'))),
   ...     __import__('builtins').setattr(
   ...       _macro_,
   ...       'L1',
   ...       _fnxAUTO7_))[-1])(),
   ...   # __main__.._macro_.defmacro
   ...   # hissp.basic.._macro_.let
   ...   (lambda _fnxAUTO7_=(lambda *_exprxAUTO151_:
   ...     (lambda *xAUTO0_:xAUTO0_)(
   ...       'lambda',
   ...       'XY',
   ...       _exprxAUTO151_)):(
   ...     __import__('builtins').setattr(
   ...       _fnxAUTO7_,
   ...       '__qualname__',
   ...       ('.').join(
   ...         ('_macro_', 'L2'))),
   ...     __import__('builtins').setattr(
   ...       _macro_,
   ...       'L2',
   ...       _fnxAUTO7_))[-1])(),
   ...   # __main__.._macro_.defmacro
   ...   # hissp.basic.._macro_.let
   ...   (lambda _fnxAUTO7_=(lambda *_exprxAUTO151_:
   ...     (lambda *xAUTO0_:xAUTO0_)(
   ...       'lambda',
   ...       'XYZ',
   ...       _exprxAUTO151_)):(
   ...     __import__('builtins').setattr(
   ...       _fnxAUTO7_,
   ...       '__qualname__',
   ...       ('.').join(
   ...         ('_macro_', 'L3'))),
   ...     __import__('builtins').setattr(
   ...       _macro_,
   ...       'L3',
   ...       _fnxAUTO7_))[-1])())[-1])()

That little bit of Lissp expanded into *that much Python*.
And we only went up to ``L3``.
We could have just as easily gone up to ``L26`` by changing a single number
and using the whole alphabet in the string of parameter names.
The expansion would have been about ten times bigger.

Whoa.

It totally works too.

.. code-block:: REPL

   #> ((L3 add Z (add X Y))
   #.. "A" "B" "C")
   >>> # L3
   ... (lambda X,Y,Z:
   ...   add(
   ...     Z,
   ...     add(
   ...       X,
   ...       Y)))(
   ...   ('A'),
   ...   ('B'),
   ...   ('C'))
   'CAB'
   #> (L2)
   >>> # L2
   ... (lambda X,Y:())
   <function <lambda> at 0x000001A70E80EAF0>
   #> (L1)
   >>> # L1
   ... (lambda X:())
   <function <lambda> at 0x000001A70E81A4C0>

How does this work?
I don't blame you for glossing over the Python output.
It's pretty big this time.
I mostly ignore it when it gets very long,
unless there's something in particular I'm looking for.

But let's look at this Lissp snippet again, more carefully.

.. code-block:: Lissp

   .#`(progn ,@(map (lambda (i)
                      `(defmacro ,(.format "L{}" i)
                                 (: :* $#expr)
                         `(lambda ,',(getitem "XYZ" (slice i))
                            ,$#expr)))
                    (range 1 4)))

It's injecting some Hissp we generated with a template.
That's the first two reader macros ``.#`` and :literal:`\``.
The `progn` sequences multiple expressions for their side effects.
It's like having multiple "statements" in a single expression.
We splice in multiple expressions generated with a `map`.
The `map` uses a lambda to translate all the integers from the `range` into `defmacro` forms.

The lambda takes the int ``i`` from the `range` and produces a `defmacro`,
which, when run in the `progn` by our inject,
will define a macro.

Nothing is above abstraction in Lissp.
`defmacro` forms are *still code*.
We can make them with templates like anything else.

We need to give each one a different name,
so we combine the ``i`` with ``"L"``.

The parameters tuple for `defmacro` contains a gensym,
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

Macros can read code too.
~~~~~~~~~~~~~~~~~~~~~~~~~

We're still providing more information than is required.
You have to change the name of your macro based on the number of arguments you expect.
But can't the macro infer this based on which parameters your expression contains?

Also, we're kind of running out of alphabet when we start on ``X``,
You often see 4-D vectors labeled (x, y, z, w),
but beyond that, mathematicians just number them with subscripts.

So a better approach might be with numbered parameters, like ``X1``, ``X2``, ``X3``, etc.
Then, if you macro is smart enough,
it can look for the highest X-number in your expression
and automatically provide that many parameters for you.

We can create numbered X's the same way we created the numbered L's.

.. code-block:: REPL

   #> (defmacro L (no : :* expr)
   #..  `(lambda ,(map (lambda (i)
   #..                   (.format "X{}" i))
   #..                 (range 1 (add 1 no)))
   #..     ,expr))
   >>> # defmacro
   ... # hissp.basic.._macro_.let
   ... (lambda _fnxAUTO7_=(lambda no,*expr:
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
   ...           no))),
   ...     expr)):(
   ...   __import__('builtins').setattr(
   ...     _fnxAUTO7_,
   ...     '__qualname__',
   ...     ('.').join(
   ...       ('_macro_', 'L'))),
   ...   __import__('builtins').setattr(
   ...     _macro_,
   ...     'L',
   ...     _fnxAUTO7_))[-1])()
   #> (L 10)
   >>> # L
   ... (lambda X1,X2,X3,X4,X5,X6,X7,X8,X9,X10:())
   <function <lambda> at 0x000001A70E879C10>
   #> ((L 2 add X1 X2) "A" "B")
   >>> # L
   ... (lambda X1,X2:
   ...   add(
   ...     X1,
   ...     X2))(
   ...   ('A'),
   ...   ('B'))
   'AB'

This version pulls the number argument out of the macro name and makes it the first argument.
We're using numbered parameters now, so there's no limit.
That takes care of the parameters,
but we're still passing in a number for them.

Let's make a slight tweak.

.. code-block:: REPL

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
   ...       ('_macro_', 'L'))),
   ...   __import__('builtins').setattr(
   ...     _macro_,
   ...     'L',
   ...     _fnxAUTO7_))[-1])()

What is ``max-X``?
It's a venerable design technique known as *wishful thinking*.
We haven't implemented it yet.
This doesn't work.
But we *wish* it would find the maximum X number in the expression.

Can we just iterate through the expression and check?

.. code-block:: REPL

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

   #> ((L add X1 (add X2 X3)) : :* "BAR")
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

Not so cool.
What happened?
The lambda only took one parameter,
even though the expression contained an ``X3``.

We need to be able to check for symbols nested in tuples.
This sounds like a job for recursion.
Lissp can do it with a class.

.. code-block:: REPL

   #> (deftype Flattener ()
   #..  __init__
   #..  (lambda (self)
   #..    (setattr self 'acc []))
   #..  flatten
   #..  (lambda (self form)
   #..    (any-for x form
   #..      (if-else (is_ (type x) tuple)
   #..        (self.flatten x)
   #..        (.append self.acc x))
   #..      False)
   #..    self.acc))
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
   ...         setattr(
   ...           self,
   ...           'acc',
   ...           [])),
   ...       flatten=(lambda self,form:(
   ...         # anyxH_for
   ...         __import__('builtins').any(
   ...           __import__('builtins').map(
   ...             (lambda x:(
   ...               # ifxH_else
   ...               (lambda test,*thenxH_else:
   ...                 __import__('operator').getitem(
   ...                   thenxH_else,
   ...                   __import__('operator').not_(
   ...                     test))())(
   ...                 is_(
   ...                   type(
   ...                     x),
   ...                   tuple),
   ...                 (lambda :
   ...                   self.flatten(
   ...                     x)),
   ...                 (lambda :
   ...                   self.acc.append(
   ...                     x))),
   ...               False)[-1]),
   ...             form)),
   ...         self.acc)[-1]))))

This is a good utility to have for macros that have to read code.
Let's give it a nicer interface.

.. code-block:: REPL

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

.. code-block:: REPL

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

   #> ((L add X1 (add X2 X3)) : :* "BAR")
   >>> # L
   ... (lambda X1,X2,X3:
   ...   add(
   ...     X1,
   ...     add(
   ...       X2,
   ...       X3)))(
   ...   *('BAR'))
   'BAR'

That's better.

.. (defmacro % (: :* expr)
     `(lambda ,params (,@expr))

   #%(* % %)

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

.. TODO: regex literals
   '' == '
   '\\ == \
   'x == \x
   s.replace(
   re.sub("'([^'])", "\\\1")

.. TODO: defmacro/g defmacro!
.. TODO: destructuring bind (iterable only?)
.. TODO: destructuring lambda (iterable only?)
.. TODO: yield and code-walking
