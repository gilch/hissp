.. Copyright 2019, 2020, 2021, 2022, 2023, 2024 Matthew Egan Odendahl
   SPDX-License-Identifier: CC-BY-SA-4.0

.. Hidden doctest adds bundled macros for REPL-consistent behavior.
   #> (.update (globals) : _macro_ (types..SimpleNamespace : :** (vars hissp.._macro_)))
   >>> globals().update(
   ...   _macro_=__import__('types').SimpleNamespace(
   ...             **vars(
   ...                 __import__('hissp')._macro_)))

Hissp Primer
############

Metaprogramming
  Writing code that writes code.

Hissp is designed with metaprogramming in mind.
Unlike most programming languages,
Hissp is not made of text, but data: Abstract Syntax Trees (AST).

Abstract Syntax Tree
  A type of intermediate tree data structure used by most compilers
  after parsing a programming language.

You've been writing AST all along, albeit indirectly.
To understand code at all, in any programming language,
you must have an understanding of how to *parse* it, mentally.

Python itself has an AST representation used by its compiler
(see the `ast` module)
which is accessible to Python programs,
but because it represents all of the possible Python syntax,
`which is considerable <https://docs.python.org/3/reference/grammar.html>`_,
it is difficult to use effectively for metaprogramming.

:doc:`The Hissp compiler <hissp.compiler>`,
in contrast, compiles Hissp code to a simplified
*functional subset* of Python.
This sacrifice ultimately gives Hissp greater expressive power,
because it makes Hissp a simpler language that is easier to manipulate
programmatically.

In Hissp, you write in this parsed form far more directly:
*Hissp code is AST.*

Some familiarity with Python is assumed for the primer.
If you get confused or stuck,
see the `discussions page <https://github.com/gilch/hissp/discussions>`_
or find the chat.

Installation
============

Hissp requires Python 3.8+ and has no other dependencies.

Confirm your Python version with

.. code-block:: console

   $ python -V

(Re-)install the Hissp version matching this document with

.. code-block:: console

   $ python -m pip install --upgrade --force-reinstall git+https://github.com/gilch/hissp

These docs are for the latest development version of Hissp.
Most examples are tested automatically,
but details may be dated.

Report issues or try the current release version instead.
More details about Pip, Python versions, and virtual environments may be helpful,
but are beyond the scope of this document.

Hello World
===========

A Hissp program is made of Python objects in tuples
which represent the syntax tree structure.

>>> hissp_program = (
...     ('lambda',('name',)
...      ,('print',('quote','Hello',),'name',),)
... )

You can invoke the Hissp compiler directly from Python.
The `readerless()` function takes a Hissp program as input,
and returns its Python translation as a string.

>>> from hissp import readerless
>>> python_translation = readerless(hissp_program)
>>> print(python_translation)
(lambda name:
    print(
      'Hello',
      name)
)

Python can then run this program as normal.

>>> eval(python_translation)('World')
Hello World

Let's break this Hissp program down.
Notice that the first element of each tuple designates its function.

In the case of ``('print',('quote','Hello',),'name',)``,
the first element represents a call to the `print()<print>` function.
The remaining elements are the arguments.

The interpretation of the `lambda form <lambda_>` is a special case.
It represents a lambda expression, rather than a function call.
``('name',)`` is its parameters tuple.
The remainder is its body.

Note that ``'name'`` became an identifier in the Python translation,
but the ``('quote','Hello',)`` expression became a string.
That's the interpretation of ``quote``:
its argument is seen as "data" rather than code by the compiler.

Together, ``lambda`` and ``quote`` are the only `special forms <hissp.compiler.Compiler.special>`
known to the compiler.
There are ways to define more forms with special interpretations,
called "macros", which is how Hissp gets much of its expressive power.

``('quote','Hello',)`` seems a little verbose compared to its Python
translation.
This could get tedious every time we need a string.
Isn't there something we can do?

Let's try it.

>>> def q(data):
...     return 'quote', data
...
>>> q('Hello')
('quote', 'Hello')

You may not have noticed, but congratulations!
We've just written our first metaprogram:
``q()`` is a Python function that writes Hissp code.
Code is writing code!

Let's use it.

>>> readerless(
...     ('lambda',('name')
...      ,('print',q('Hello'),'name',),)
... )
"(lambda n, a, m, e:\n    print(\n      'Hello',\n      name)\n)"
>>> print(_)  # Remember, _ is the last result that wasn't None.
(lambda n, a, m, e:
    print(
      'Hello',
      name)
)
>>> eval(_)('World')
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
TypeError: <lambda>() missing 3 required positional arguments: 'a', 'm', and 'e'

What happened?

Look at the compiled Python.
Our ``q()`` worked as expected,
but there are too many parameters in the lambda because we forgot the comma in ``('name')``.
Lambda doesn't care what kind of iterable you use for its parameters,
as long as it yields appropriate elements in appropriate order.
We could have used a list, for example.
This flexibility can make metaprogramming easier,
but mutable collections are not recommended.
Python strings are iterables yielding their characters,
so the characters ``n``, ``a``, ``m``, and ``e`` got compiled to the parameters.

.. Caution::
   When writing Hissp tuples,
   it's best to think of commas as *terminators*,
   rather than *separators*, to avoid this kind of problem.
   In Python, (except for the empty tuple ``()``)
   it is the *comma* that creates a tuple, **not** the parentheses.
   The parentheses only control evaluation order.
   There are some contexts where tuples don't require parentheses at all.

Let's try that again,
with the comma this time.

>>> readerless(
...     ('lambda',('name',)
...      ,('print',q('Hello'),'name',),)
... )
"(lambda name:\n    print(\n      'Hello',\n      name)\n)"
>>> print(_)
(lambda name:
    print(
      'Hello',
      name)
)

That's better.

Lissp
=====

It can feel a little tedious writing significant amounts of Hissp code in Python.
You have to quote every identifier and ``'quote'`` every string,
and it's easy to miss a comma in a tuple.

Naturally, the way to make this easier is by metaprogramming.
We already saw a simple example with the ``q()`` function above.

But we can do much better than that.

Hissp is made of data structures.
They're ephemeral; they only live in memory.
If Hissp is the spoken word, we need a written word.
And to "speak" the written word back into Hissp, we need a *reader*.
Hissp comes with a :mod:`hissp.reader` module that interprets a lightweight
language called *Lissp* as Hissp code.

Lissp is made of text.
Lissp is to the written word as Hissp is to the spoken word.
When you are writing Lissp, you are still writing Hissp.

Lissp
  A lightweight textual language representing Hissp,
  as defined by :mod:`hissp.reader`.

Lissp also includes *reader macros*,
that act like the ``q()`` example:
metaprogramming abbreviations.

Reader macro
  An abbreviation used by the reader.
  These are not part of the Hissp language proper,
  but rather are functions that *expand* to Hissp;
  They run at *read time* and return Hissp code.

Let's see our "Hello World" example in Lissp:

>>> from hissp.reader import Lissp
>>> next(Lissp().reads("""
... (lambda (name)
...   (print 'Hello name))
... """))
('lambda', ('name',), ('print', ('quote', 'Hello'), 'name'))

There are no commas to miss, because there are no commas at all.

As you can see, the Hissp structure is exactly the same as before.
But now you don't have to quote identifiers either.

The ``'`` is a built-in reader macro that acts just like the ``q()``
function we defined earlier: it wraps the next expression in a ``quote`` form.

The REPL
::::::::

Hissp comes with its own interactive command-line interface,
called the Lissp REPL.

REPL
  Read-Evaluate-Print Loop.

You can launch the REPL from Python code (which is useful for debugging,
like `code.interact`),
but let's start it from the command line using an appropriate Python interpreter::

   $ python -m hissp

Or, if you installed the ``hissp`` package using ``pip``,
you can use the installed entry point script::

   $ lissp

You should see the Lissp prompt ``#>`` appear.

You can quit with ``(exit)`` or EOF [#EOF]_.

Follow along with the examples by typing them into the Lissp REPL.
Try variations that occur to you.

The REPL is layered on top of the Python interpreter.
You type in the part at the Lissp prompt ``#>``,
and then Lissp will compile it to Python,
which it will enter into the Python interpreter ``>>>`` for you.
Then Python will evaluate it and print a result as normal.

Data Elements of Lissp
::::::::::::::::::::::

Hissp has special behaviors for Python's `tuple` and `str` types.
Everything else is just data,
and Hissp does its best to compile it that way.

In Lissp, the Hissp `tuple` and `str` elements
are written with ``()`` and ``||``, respectively.
The `str`\ s represent text fragments,
so the ``||`` tokens in Lissp are called "fragments".

Lissp has full generality with just these two elements,
although some things would be awkward.
Here's our first Hissp program again written that way:

.. code-block:: REPL

   #> (|lambda| (|name|)
   #..  (|print| (|quote| |Hello|) |name|))
   >>> (lambda name:
   ...     print(
   ...       'Hello',
   ...       name)
   ... )
   <function <lambda> at 0x...>

   #> (|_| (|quote| |World|))
   >>> _(
   ...   'World')
   Hello World

Notice that the fragments are interpreted in different ways depending on the context.
``|lambda|`` is a special instruction to the Hissp compiler.
``|print|`` is a fragment of Python code, an identifier in this case,
but basically any Python expression works.
``|Hello|`` is a string.

In addition to the special behaviors from the Hissp level for tuple
and string lexical elements,
the Lissp level has special behavior for *reader macros*.
(And ignores things like whitespace and comments.)
Everything else is an *atom*,
which is passed through to the Hissp level with minimal processing.

Basic Atoms
+++++++++++

Most data literals work just like Python:

.. code-block:: REPL

   #> 1 ; Lissp comments use ';' instead of '#'.
   >>> (1)
   1

   #> -1.0 ; float
   >>> (-1.0)
   -1.0

   #> 1e10 ; exponent notation
   >>> (10000000000.0)
   10000000000.0

   #> 2+3j ; complex
   >>> ((2+3j))
   (2+3j)

   #> ...
   >>> ...
   Ellipsis

   #> True
   >>> True
   True

   #> None ; These don't print.
   >>> None

Comments, as one might expect, are discarded by the reader,
and do not appear in the output.

.. code-block:: REPL

   #> ;; Use two ';'s when it's positioned like a form.
   #..;;; Use three for top-level commentary not attached to anything.
   #..;;;; Four for headers. See the style guide for details.
   #..
   >>>


Strings
+++++++

You've already seen how to make strings from fragments: you quote them.

.. code-block:: REPL

   #> (|quote| |Hello|)
   >>> 'Hello'
   'Hello'

We've already seen that the reader has a shorthand for quotation.

.. code-block:: REPL

   #> '|Hello|
   >>> 'Hello'
   'Hello'

If that particular fragment weren't quoted in this context,
it would be interpreted as a Python identifier instead.

Although you can escape a ``|`` by doubling it,
fragment text is otherwise raw;
you can't use Python's escape sequences for special characters.

.. code-block:: REPL

   #> '|Say "Cheese!"\n\u263a|
   >>> 'Say "Cheese!"\\n\\u263a'
   'Say "Cheese!"\\n\\u263a'

If you do want the escapes,
the solution, of course,
is to put a Python string literal in the fragment
(making it a fragment of Python code)
and then not quote it.
This is another way to make strings from fragments.

.. code-block:: REPL

   #> |"Say \"Cheese!\"\n\u263a"| ; There is a reason we used double quotes.
   >>> "Say \"Cheese!\"\n\u263a"
   'Say "Cheese!"\n☺'

   #> (|print| |_|)
   >>> print(
   ...   _)
   Say "Cheese!"
   ☺

And, in fact, the reader has a shorthand for this already.
If you've got a fragment surrounded by double quotes (``"``), you can drop the ``||``.

.. code-block:: REPL

   #> "Say \"Cheese!\"
   #..\u263a" ; Note the parentheses.
   >>> ('Say "Cheese!"\n☺')
   'Say "Cheese!"\n☺'

This doesn't work for single quotes,
because those are reserved for the reader's quotation shorthand.
Also notice that you're allowed a literal newline
(and the ``\n`` escape sequence also works),
like in Python's triple-quoted strings.
This is a convenience not currently allowed in the ``||``-delimited tokens.

These are not direct representations like the other atoms!
They're reader shorthand for a fragment of Python *containing* a string literal.
If you expect them to represent themselves in the Hissp when you quote them,
you will be confused.
``'"foo"`` is a shorthand for ``|('foo')|``. Try it.

This also applies to double-quoted (``""``) tokens quoted indirectly through a tuple.
See the difference?

.. code-block:: REPL

   #> '("foo" |bar|)
   >>> ("('foo')",
   ...  'bar',)
   ("('foo')", 'bar')

Symbol Tokens
+++++++++++++

Symbols are meant for variable names and the like.
They're another reader shorthand.
If you have a fragment containing a valid Python identifier,
you can drop the ``||``.

In our basic example:

.. code-block:: Lissp

   (lambda (name)
     (print 'Hello name))

``lambda``, ``name``, ``print``, ``Hello``, and
``name`` are *symbols*.

Quoting our example to see how Lissp would get read as Hissp,

.. code-block:: REPL

   #> (quote
   #..  (lambda (name)
   #..    (print 'Hello name)))
   >>> ('lambda',
   ...  ('name',),
   ...  ('print',
   ...   ('quote',
   ...    'Hello',),
   ...   'name',),)
   ('lambda', ('name',), ('print', ('quote', 'Hello'), 'name'))

we see that there are *no symbol objects* at the Hissp level.
The Lissp symbol tokens are read in as strings, just like fragments.

In other Lisps, symbols are a data type in their own right,
but symbols only exist as a *reader syntax* in Lissp,
where they represent the subset of Hissp-level strings that can act as identifiers.
Python has no built-in symbol type
and instead uses strings pervasively whenever it has to represent identifiers.

In summary,
symbols in Lissp become strings in Hissp which become identifiers in Python,
unless they're quoted, in which case they become string literals in Python.

Attributes
----------

Symbols can have internal ``.``\ s to access attributes, same as Python.

.. code-block:: REPL

   #> int.__name__
   >>> int.__name__
   'int'

   #> int.__name__.__class__ ; These chain.
   >>> int.__name__.__class__
   <class 'str'>

.. _qualified identifier:

Module Handles and Qualified Identifiers
----------------------------------------

You can refer to variables defined in any module by using a
*qualified identifier*:

.. code-block:: REPL

   #> operator. ; Module handles end in a dot and automatically import.
   >>> __import__('operator')
   <module 'operator' from '...operator.py'>

   #> (operator..add 40 2) ; Fully-qualified identifiers include their module.
   >>> __import__('operator').add(
   ...   (40),
   ...   (2))
   42

Notice the second dot required to access a module attribute.

The translation of module handles to ``__import__`` calls happens at compile time,
not read time, so this feature is still available in readerless mode.

>>> readerless('re.')
"__import__('re')"

Qualification is important for macros that are defined in one module,
but used in another.

Munging
-------

Symbol tokens have another important difference from other fragments.

.. code-block:: REPL

   #> 'foo->bar? ; QzH_ is for "Hyphen", QzGT_ for "Greater Than/riGhT".
   >>> 'fooQzH_QzGT_barQzQUERY_'
   'fooQzH_QzGT_barQzQUERY_'

   #> "foo->bar?"
   >>> ('foo->bar?')
   'foo->bar?'

Because symbols may contain special characters,
but the Python identifiers they represent cannot,
the reader `munge`\ s symbols with forbidden characters
to valid identifier strings by replacing them with special "Quotez"
escape sequences, like ``QzFULLxSTOP_``.

This "Quotez" format was chosen because it contains an underscore
and both lower-case and upper-case letters,
which makes it distinct from
`standard Python naming conventions <https://www.python.org/dev/peps/pep-0008/#naming-conventions>`_:
``lower_case_with_underscores``, ``UPPER_CASE_WITH_UNDERSCORES``, and ``CapWords``.
This makes it easy to tell if an identifier contains munged characters,
which makes `demunging<demunge>` possible in the normal case.
It also cannot introduce a leading underscore,
which can have special meaning in Python.
It might have been simpler to use the character's `ord()<ord>`,
but it's important that the munged symbols still be human-readable.

The "Qz" bigram is almost unheard of in English text,
and "Q" almost never ends a word (except perhaps in brand names),
making "Qz" a visually distinct escape sequence,
easy to read, and very unlikely to appear by accident.

Munging happens at `read time`, which means you can use a munged symbol both
as an identifier and as a string representing that identifier:

.. code-block:: REPL

   #> (types..SimpleNamespace)
   >>> __import__('types').SimpleNamespace()
   namespace()

   #> (setattr _ ; The namespace.
   #..         '@%$! ; Compiles to a string representing an identifier.
   #..         42)
   >>> setattr(
   ...   _,
   ...   'QzAT_QzPCENT_QzDOLR_QzBANG_',
   ...   (42))

   #> _
   >>> _
   namespace(QzAT_QzPCENT_QzDOLR_QzBANG_=42)

   #> _.@%$! ; Munges and compiles to attribute identifier.
   >>> _.QzAT_QzPCENT_QzDOLR_QzBANG_
   42

Spaces, double quotes, parentheses, and semicolons are allowed in atoms,
but they must each be escaped with a backslash to prevent it from terminating the symbol.
(Escape a backslash with another backslash.)

.. code-block:: REPL

   #> 'embedded\ space
   >>> 'embeddedQzSPACE_space'
   'embeddedQzSPACE_space'

Python does not allow some characters to start an identifier that it allows inside identifiers,
such as digits.
You may have to escape these if they begin a symbol to distinguish them from numbers.

.. code-block:: REPL

   #> '\108
   >>> 'QzDIGITxONE_08'
   'QzDIGITxONE_08'

Notice that only the first digit had to be munged to make it a valid Python identifier.

.. code-block:: REPL

   #> '1o8 ; Clearly not a number, so no escape required.
   >>> 'QzDIGITxONE_o8'
   'QzDIGITxONE_o8'

By the way, since module handles count as symbols,
special characters in them also get munged.
They will then attempt to import modules with funny names,
which only works if you have modules with said names to import. Just saying.

Control Words
-------------

Symbols that begin with a colon are called *control words* [#key]_.
(They don't need the ``||``\ s either, but they're allowed.)
These are mainly used to give internal structure to macro invocations—you
want a word distinguishable from a string at compile time,
but it's not meant to be a Python identifier.
Thus, they do not get munged like normal symbols would:

.. code-block:: REPL

   #> :foo->bar?
   >>> ':foo->bar?'
   ':foo->bar?'

Control words compile to string literals that begin with ``:``,
so you usually don't need to quote them,
but you can:

.. code-block:: REPL

   #> ':foo->bar?
   >>> ':foo->bar?'
   ':foo->bar?'

Note that you can do nearly the same thing with a ``""`` token:

.. code-block:: REPL

   #> ":foo->bar?"
   >>> (':foo->bar?')
   ':foo->bar?'

The lambda special form,
as well as certain macros,
use certain "active"
control words as syntactic elements to *control* the interpretation of other elements,
hence the name.

Some control words are also "active" in normal function calls,
(like ``:**`` for dict unpacking, covered later.)
You must quote these like ``':**`` or ``":**"`` to pass them as data in that context.

Macros operate at compile time (before evaluation),
so they can also distinguish a raw control word from a quoted one.

Compound Expressions
::::::::::::::::::::

Atoms are just the basic building blocks.
To do anything interesting with them,
you have to combine them into syntax trees using tuples.

Empty
+++++

The empty tuple ``()`` might as well be an atom:

.. code-block:: REPL

   #> ()
   >>> ()
   ()

Lambdas
+++++++

The anonymous function special form::

   (lambda <parameters>
     <body>)

Python's parameter types are rather involved.
Hissp's lambdas have a simplified format designed for metaprogramming.
When the parameters tuple [#LambdaList]_
starts with a colon,
then all parameters are pairs, implied by position.
Hissp can represent all of Python's parameter types this way.

.. code-block:: REPL

   #> (lambda (: ; starts with : separator control word.
   #..         a :? ; positional-only parameter, no default
   #..         :/ :? ; positional-only separator words
   #..         b :? ; normal parameter, no default value
   #..         e 1 ; parameter with a default value of 1
   #..         f 2 ; another one with a default value of 2
   #..         :* args ; remaining positional args packed in a tuple
   #..         h 4 ; parameters after * are keyword only
   #..         i :? ; kwonly with no default
   #..         j 1 ; another kwonly parameter with a default value
   #..         :** kwargs) ; packs keyword args into a dict
   #..  42)
   >>> (
   ...  lambda a,
   ...         /,
   ...         b,
   ...         e=(1),
   ...         f=(2),
   ...         *args,
   ...         h=(4),
   ...         i,
   ...         j=(1),
   ...         **kwargs:
   ...     (42))
   <function <lambda> at ...>

The parameter name goes on the left of the pairs, and the default goes on the right.
Notice that the ``:?`` control word indicates that the parameter has no default value.

The ``:/`` separator ending the positional-only arguments is not a parameter,
even though it gets listed like one,
thus it can't have a default
and must always be paired with ``:?``.

The ``:*`` can likewise act as a separator starting the keyword-only arguments,
and can likewise be paired with ``:?``.

The normal parameters in between these can be passed in either as positional arguments
or as keyword arguments (kwargs).

The ``:*`` can instead pair with a parameter name,
which collects the remainder of the positional arguments into a tuple.
This is one of two exceptions to the rule that the parameter name is the left of the pair.
This matches Python's ordering,
and means the rule that the ``:?`` goes on the right has no exceptions.
The other exception is the parameter name after ``:**``,
which collects the remaining keyword arguments into a dict.

The ``:`` control word that we started with is a convenience that abbreviates the common case
of a pair with a ``:?``.

.. code-block:: REPL

   #> (lambda (a :/ ; positional only
   #..         b ; normal
   #..         : e 1  f 2 ; default
   #..         :* args  h 4  i :?  j 1 ; kwonly
   #..         :** kwargs)
   #..  42)
   >>> (
   ...  lambda a,
   ...         /,
   ...         b,
   ...         e=(1),
   ...         f=(2),
   ...         *args,
   ...         h=(4),
   ...         i,
   ...         j=(1),
   ...         **kwargs:
   ...     (42))
   <function <lambda> at ...>

Each element before the ``:`` is implicitly paired with
the placeholder control word ``:?``.
Notice the Python compilation is exactly the same as before,
and that a ``:?`` was still required in the pairs section (after the ``:``)
to indicate that the ``i`` parameter has no default value.

The ``:*`` and ``:**`` control words mark their parameters as
taking the remainder of the positional and keyword arguments,
respectively:

.. code-block:: REPL

   #> (lambda (: :* args :** kwargs)
   #..  (print args)
   #..  (print kwargs) ; Body expressions evaluate in order.
   #..  42) ; The last value is returned.
   >>> (lambda *args, **kwargs:
   ...    (print(
   ...       args),
   ...     print(
   ...       kwargs),
   ...     (42))  [-1]
   ... )
   <function <lambda> at ...>

   #> (_ 1 : b :c)
   >>> _(
   ...   (1),
   ...   b=':c')
   (1,)
   {'b': ':c'}
   42

You can omit the right of any pair with ``:?`` except the final ``**kwargs``.

The lambda body can be empty,
in which case an empty tuple is implied:

.. code-block:: REPL

   #> (lambda (: a 1  :/ :?  :* :?  b :?  c 2))
   >>> (
   ...  lambda a=(1),
   ...         /,
   ...         *,
   ...         b,
   ...         c=(2):
   ...     ())
   <function <lambda> at ...>

Positional-only parameters with defaults must appear after the ``:``,
which forces the ``:/`` into the pairs side.
Everything on the pairs side must be paired, no exceptions.
(Even though ``:/`` can only pair with ``:?``,
adding another special case to not require the ``:?``
would make metaprogramming more difficult.)

The ``:`` may be omitted if there are no explicitly paired parameters.
Not having it is the same as putting it last:

.. code-block:: REPL

   #> (lambda (a b c :)) ; No pairs after ':'.
   >>> (lambda a, b, c: ())
   <function <lambda> at ...>

   #> (lambda (a b c)) ; The ':' was omitted.
   >>> (lambda a, b, c: ())
   <function <lambda> at ...>

   #> (lambda (:)) ; Colon isn't doing anything.
   >>> (lambda : ())
   <function <lambda> at ...>

   #> (lambda ()) ; You can omit it.
   >>> (lambda : ())
   <function <lambda> at ...>

   #> (lambda :) ; This also works (guess why), and is idiomatic in Lissp.
   >>> (lambda : ())
   <function <lambda> at ...>

The ``:`` is required if there are any explicit pairs,
even if there are no ``:?`` pairs:

.. code-block:: REPL

   #> (lambda (: :** kwargs))
   >>> (lambda **kwargs: ())
   <function <lambda> at ...>

Calls
+++++

Any tuple that is not quoted, empty, or a special form or macro is
a run-time call.

The first element of a call tuple is the callable.
The remaining elements are for the arguments.

Like lambda's parameters tuple,
when you start the arguments with ``:``,
the rest are pairs, implied by position.

.. code-block:: REPL

   #> (print : :? 1  :? 2  :? 3  sep ":"  end "\n.")
   >>> print(
   ...   (1),
   ...   (2),
   ...   (3),
   ...   sep=(':'),
   ...   end=('\n.'))
   1:2:3
   .

Again, the values are on the right and the names are on the left for each pair,
just like in lambda,
the same order as Python's assignment statements.

Here, the ``:?`` placeholder control word indicates that the argument is passed positionally,
rather than by a keyword.
Unlike in lambdas,
this means that the ``:?`` is always the left of a pair.

Like lambdas, the ``:`` is a convenience abbreviation for ``:?`` pairs,
giving call forms three parts::

   (<callable> <singles> : <pairs>)

For example:

.. code-block:: REPL

   #> (print 1 2 3 : sep ":"  end "\n.")
   >>> print(
   ...   (1),
   ...   (2),
   ...   (3),
   ...   sep=(':'),
   ...   end=('\n.'))
   1:2:3
   .

Notice the Python compilation is exactly the same as before.

The singles or the pairs section may be empty:

.. code-block:: REPL

   #> (int :) ; Both empty.
   >>> int()
   0

   #> (print :foo :bar :) ; No pairs.
   >>> print(
   ...   ':foo',
   ...   ':bar')
   :foo :bar

   #> (print : end "X") ; No singles.
   >>> print(
   ...   end=('X'))
   X

The ``:`` is optional if the pairs section is empty:

.. code-block:: REPL

   #> (int)
   >>> int()
   0

   #> (float "inf")
   >>> float(
   ...   ('inf'))
   inf

Again, this is like lambda.

The pairs section has implicit pairs; there must be an even number of elements.

Use the control words ``:*`` for iterable unpacking,
``:?`` to pass by position, and ``:**`` for keyword unpacking:

.. code-block:: REPL

   #> (print : :* '(1 2)  :? 3  :* '(4)  :** (dict : sep :  end "\n."))
   >>> print(
   ...   *((1),
   ...     (2),),
   ...   (3),
   ...   *((4),),
   ...   **dict(
   ...       sep=':',
   ...       end=('\n.')))
   1:2:3:4
   .

These go on the left, like a keyword.
These are the same control words used in lambdas.

Unlike parameter names, these control words can be repeated,
but (as in Python) a ``:*`` is not allowed to follow ``:**``.

Method calls are similar to function calls::

   (.<method name> <self> <singles> : <pairs>)

Like Clojure, a method on the first "argument" (``<self>``) is assumed if the
function name starts with a dot:

.. code-block:: REPL

   #> (.conjugate 1j)
   >>> (1j).conjugate()
   -1j

To make metaprogramming easier, the ``:`` can go before the ``<self>`` as well,
but must be paired with a ``:?``.

.. code-block:: REPL

   #> (.conjugate : :? 1j)
   >>> (1j).conjugate()
   -1j

Reader Macros
:::::::::::::

Up to this point, the Lissp examples have been a pretty direct representation of Hissp.
Metaprogramming changes that.

So far, all of our Hissp examples written in readerless mode
have been tuple trees with string leaves,

>>> eval(readerless(('print','1','2','3',':','sep',':')))
1:2:3

but the Hissp compiler will accept other types of atoms.

>>> eval(readerless((print,1,2,3,':','sep',':')))
1:2:3

Tuples represent invocations in Hissp.
Strings are Python fragments (and imports and control words).
Other objects simply represent themselves.
In fact,
some of the reader syntax we have already seen creates non-string atoms in the Hissp.

.. code-block:: REPL

   #> '(print 1 2 3 : sep :)
   >>> ('print',
   ...  (1),
   ...  (2),
   ...  (3),
   ...  ':',
   ...  'sep',
   ...  ':',)
   ('print', 1, 2, 3, ':', 'sep', ':')

In this case, we can see the integer objects were not read as strings.

Consider how easily you can programmatically manipulate Hissp before compiling it if you write it in Python.

>>> ('print',q('hello, world!'.title()))
('print', ('quote', 'Hello, World!'))
>>> eval(readerless(_))
Hello, World!

Here, we changed a lowercase string to title case before the compiler even saw it.

Are we giving up this kind of power by using Lissp instead?
No, that's why we have reader macros.

Inject
++++++

Remember our first metaprogram ``q()``?
You've already seen the ``'`` reader macro.
That much is doable.

Here's how you could do the rest.

.. code-block:: REPL

   #> (print '.#(.title "hello, world!"))
   >>> print(
   ...   'Hello, World!')
   Hello, World!

Let's quote the whole form to see the intermediate Hissp.

.. code-block:: REPL

   #> '(print '.#(.title "hello, world!"))
   >>> ('print',
   ...  ('quote',
   ...   'Hello, World!',),)
   ('print', ('quote', 'Hello, World!'))

Notice the `str.title` method has already been applied,
changing the "H" and "W" case.
Just like our Python example,
this ran a program to help generate the Hissp before passing it to the compiler.

The ``.#`` is another built-in reader macro called *inject*.
It compiles and evaluates the next form
and is replaced with the resulting object in the Hissp.
These reader macros are unary operators that apply inside-out,
like functions do,
at `read time`.
The ``'.#`` means the inject is applied first,
then the quote to its result.

You can use inject to modify code at read time,
to inject non-string objects that don't have their own reader syntax in Lissp,
and to inject Python code strings
by evaluating the string literal reader syntax that would normally add quotation marks.
It's pretty important.

Python injection:

.. code-block:: REPL

   #> .#"{(1, 2): \"\"\"buckle my shoe\"\"\"}  # This is Python!"
   >>> {(1, 2): """buckle my shoe"""}  # This is Python!
   {(1, 2): 'buckle my shoe'}

Reader macros compose inside-out:

.. code-block:: REPL

   #> .#"[1,2,3]*3" ; Injects the expression string.
   >>> [1,2,3]*3
   [1, 2, 3, 1, 2, 3, 1, 2, 3]

   #> .#.#"[1,2,3]*3" ; Injects the object resulting from evaluation.
   >>> [1, 2, 3, 1, 2, 3, 1, 2, 3]
   [1, 2, 3, 1, 2, 3, 1, 2, 3]

Same result, but the Python part is different.
The list multiplication didn't happen until run time in the first instance,
but happened before the Python was generated in the second.

Compare that to the equivalent readerless mode.

>>> readerless('[1,2,3]*3')  # Compile an expression string.
'[1,2,3]*3'
>>> eval(_)
[1, 2, 3, 1, 2, 3, 1, 2, 3]
>>> readerless([1,2,3]*3)  # Compile a list object.
'[1, 2, 3, 1, 2, 3, 1, 2, 3]'
>>> eval(_)
[1, 2, 3, 1, 2, 3, 1, 2, 3]

Let's look at another double-inject example.
Keeping the phases of compilation straight can be confusing.

.. code-block:: REPL

   #> '"{(1, 2): 'buckle my shoe'}" ; quoted "" token contains a Python literal
   >>> '("{(1, 2): \'buckle my shoe\'}")'
   '("{(1, 2): \'buckle my shoe\'}")'

   #> '.#"{(3, 4): 'shut the door'}" ; quoted injected "" contains a dict
   >>> "{(3, 4): 'shut the door'}"
   "{(3, 4): 'shut the door'}"

   #> '.#.#"{(5, 6): 'pick up sticks'}" ; even quoted, this double inject is a dict
   >>> {(5, 6): 'pick up sticks'}
   {(5, 6): 'pick up sticks'}

Still confused?
Remember, inject compiles the next parsed object as Hissp,
evaluates it as Python,
then is replaced with the resulting object.
Let's look at this process in readerless mode,
so we can see some intermediate values.

>>> '("{(3, 4): \'shut the door\'}")'  # next parsed object
'("{(3, 4): \'shut the door\'}")'
>>> eval(readerless(_))  # The inject. Innermost reader macro first.
"{(3, 4): 'shut the door'}"
>>> eval(readerless(q(_)))  # Then the quote.
"{(3, 4): 'shut the door'}"

With one inject the result was a string object.

>>> '("{(5, 6): \'pick up sticks\'}")'  # next parsed object
'("{(5, 6): \'pick up sticks\'}")'
>>> eval(readerless(_))  # First inject, on the right.
"{(5, 6): 'pick up sticks'}"
>>> eval(readerless(_))  # Second inject, in the middle.
{(5, 6): 'pick up sticks'}
>>> eval(readerless(q(_)))  # Finally, quote, on the left.
{(5, 6): 'pick up sticks'}

With two, it's a dict.

How about these?

.. code-block:: REPL

   #> .#"[[]]*3" ; Injects the expression string.
   >>> [[]]*3
   [[], [], []]

   #> .#.#"[[]]*3" ; Injects a list object.
   >>> # [[], [], []]
   ... __import__('pickle').loads(b'(l(lp0\nag0\nag0\na.')
   [[], [], []]

Surprised?
What's with the `pickle.loads` expression?
It seems to produce the right object.
Is this the reader's doing?
Let's check.

>>> readerless('[[]]*3')
'[[]]*3'
>>> eval(_)
[[], [], []]
>>> readerless([[]]*3)
"# [[], [], []]\n__import__('pickle').loads(b'(l(lp0\\nag0\\nag0\\na.')"
>>> eval(_)
[[], [], []]

Nope.
Not the reader;
the compiler still does this in readerless mode.
Why?

Well, what *should* it compile to?

.. code-block:: REPL

   #> .#"[[],[],[]]" ; Maybe this?
   >>> [[],[],[]]
   [[], [], []]

   #> (.append (operator..getitem _ 0) 7)
   >>> __import__('operator').getitem(
   ...   _,
   ...   (0)).append(
   ...   (7))

   #> _
   >>> _
   [[7], [], []]

   #> .#.#"[[]]*3"
   >>> # [[], [], []]
   ... __import__('pickle').loads(b'(l(lp0\nag0\nag0\na.')
   [[], [], []]

   #> (.append (operator..getitem _ 0) 7)
   >>> __import__('operator').getitem(
   ...   _,
   ...   (0)).append(
   ...   (7))

   #> _ ; Big win! Not the same, is it?
   >>> _
   [[7], [7], [7]]

It's three references to the same list, not to three lists.
The pickle expression could produce an equivalent object graph,
even though the literal notation can't.
Objects in Hissp that aren't strings or tuples are supposed to evaluate to themselves.
In theory,
there are an infinite number of Python expressions that would produce an equivalent object.
(In practice, computers do not have infinite memory.)
When the compiler must emit Python code to produce such an object,
it has to pick one of these representations.
It might not be the one you started with.

>>> readerless(('print',0b1010,0o12,--10,1_0,5*2,+10,int(10),((((10)))),0xA,))
'print(\n  (10),\n  (10),\n  (10),\n  (10),\n  (10),\n  (10),\n  (10),\n  (10),\n  (10))'

Notice that these have all compiled the same way: ``(10)``.
There were many possible aliases in code,
but by the time the compiler got to them,
they were just references to an int object in memory,
and there is no way for the compiler to know what code you started with.

When an object has a Python literal representation,
the compiler can produce one,
but when it doesn't,
the compiler falls back to emitting a pickle expression,
which covers a fairly broad range of objects in a very general way.

Remember this example?

>>> eval(readerless((print,1,2,3,':','sep',':')))
1:2:3

The ``print`` here isn't a string.
It's a function object.

>>> (print,1,2,3,':','sep',':')
(<built-in function print>, 1, 2, 3, ':', 'sep', ':')

But that repr isn't valid Python.
If you tried to run

.. code-block:: Python

   readerless((<built-in function print>, 1, 2, 3, ':', 'sep', ':'))

then you'd get a syntax error.
Try it, if you'd like.

How can the Hissp compiler generate Python code from this tuple?

Let's see what it's doing.

>>> readerless((print,1,2,3,':','sep',':'))
"# <built-in function print>\n__import__('pickle').loads(b'c__builtin__\\nprint\\n.')(\n  (1),\n  (2),\n  (3),\n  sep=':')"
>>> print(_)
# <built-in function print>
__import__('pickle').loads(b'c__builtin__\nprint\n.')(
  (1),
  (2),
  (3),
  sep=':')
>>> eval(_)
1:2:3

It's using pickle again,
and because of that, this code still works,
even though the `print` function does not have a literal notation.

When we tried this in the obvious way in Lissp,
`print` used the symbol reader syntax,
which became a string in the Hissp,
and rendered as an identifier in the compiled Python,
but if we had injected it instead,

.. code-block:: REPL

   #> (.#print 1 2 3 : sep :)
   >>> # <built-in function print>
   ... __import__('pickle').loads(b'c__builtin__\nprint\n.')(
   ...   (1),
   ...   (2),
   ...   (3),
   ...   sep=':')
   1:2:3

we get the pickle again.

Many other object types work.

.. code-block:: REPL

   #> .#(fractions..Fraction 1 2)
   >>> # Fraction(1, 2)
   ... __import__('pickle').loads(b'cfractions\nFraction\n(V1/2\ntR.')
   Fraction(1, 2)

Unfortunately, there are some objects even pickle can't handle.

.. code-block:: REPL

   #> .#(lambda ())
     File "<string>", line None
   hissp.compiler.CompileError:
   (>   >  > >><function <lambda> at ...><< <  <   <)
   # Compiler.pickle() PicklingError:
   #  Can't pickle <function <lambda> at ...>: attribute lookup <lambda> on __main__ failed

Hissp had to give up with an error this time.

.. TIP::
   The third-party `Dill <https://pypi.org/project/dill/>`_
   library can pickle more types.
   Set :mod:`hissp.compiler`'s ``pickle`` attribute to the ``dill`` module to enable.

Reader Tags
+++++++++++

Besides a few built-ins,
reader macros in Lissp consist of a special symbol ending with ``#``\ s,
called a *tag*,
followed by additional argument forms.

A function named by a `qualified identifier`_ is invoked on the form,
and the reader embeds the resulting object into the output Hissp:

.. code-block:: REPL

   #> builtins..float#inf
   >>> # inf
   ... __import__('pickle').loads(b'Finf\n.')
   inf

This inserts an actual `float` object at `read time` into the Hissp code.

It's the same as using inject like this

.. code-block:: REPL

   #> .#(float 'inf)
   >>> # inf
   ... __import__('pickle').loads(b'Finf\n.')
   inf

Or readerless mode like this

>>> readerless(float('inf'))
"# inf\n__import__('pickle').loads(b'Finf\\n.')"

A float is neither a `str` nor a `tuple`,
so Hissp tries its best to compile this as data representing itself,
but because its repr, ``inf``, isn't a valid Python literal,
it has to compile to a pickle instead.
But if it's used by something *before* compile time,
like another macro, then it won't have been serialized yet.

.. code-block:: REPL

   #> 'builtins..repr#builtins..float#inf ; No pickles here.
   >>> 'inf'
   'inf'

You should normally try to avoid emitting pickles
(e.g. use ``(float 'inf)`` or `math..inf <math.inf>` instead).
While unpickling does have some overhead,
it may be worth it if constructing the object normally has even more.
Naturally, the object must be picklable to emit a pickle.

Qualified reader macros don't always result in pickles though.

.. code-block:: REPL

   #> builtins..ord#Q
   >>> (81)
   81

In certain circumstances,
for certain purposes,
this might be a clearer way of expressing the number 81.
(In other circumstances,
other representations,
like ``0x51`` could be better.)
If you evaluate it at read time like this,
then there is no run-time overhead for the alternative notation,
because it's compiled to ``(81)``,
just like there's no run-time overhead for using a hex literal instead of decimal in Python.

Multiary Tags
+++++++++++++

Reader tags may take multiple arguments.
You indicate how many with the number of trailing ``#``\ s.

.. code-block:: REPL

   #> fractions..Fraction#|2/3| ; Two thirds.
   >>> # Fraction(2, 3)
   ... __import__('pickle').loads(b'cfractions\nFraction\n(V2/3\ntR.')
   Fraction(2, 3)

   #> fractions..Fraction## 2 3 ; Notice the extra #.
   >>> # Fraction(2, 3)
   ... __import__('pickle').loads(b'cfractions\nFraction\n(V2/3\ntR.')
   Fraction(2, 3)

Reader tags may also take keyword arguments,
made with a kwarg token ending in ``=``,
which can be helpful quick refinements for functions with optional arguments,
without the need to create a new reader macro for each specialization.

.. code-block:: REPL

   #> builtins..int#|21| ; Normal base ten
   >>> (21)
   21

   #> builtins..int## |21| base=6 ; base 6, via base= kwarg. Note ##.
   >>> (13)
   13

   #> builtins..int## base=6 |21| ; kwargs are allowed in any position
   >>> (13)
   13

A kwarg token works a lot like a tag, except it ends with a single ``=``
instead of some number of ``#``\ s, and can only take a single argument.
These do evaluate to a ``Kwarg`` object,
which is only meant for use as an argument to a tag,
but they're allowed to persist after read time for debugging purposes.
If you see one of these, make sure you used enough ``#``\ s on your tag.

.. code-block:: REPL

   #> base=6
   >>> # Kwarg('base', 6)
   ... __import__('pickle').loads(b'ccopy_reg\n_reconstructor\n(chissp.reader\nKwarg\nc__builtin__\nobject\nNtR(dVk\nVbase\nsVv\nI6\nsb.')
   Kwarg('base', 6)

The special kwarg tokens ``*=`` and ``**=`` unpack the argument at that position,
either as positional arguments or keyword arguments, respectively.

.. code-block:: REPL

   #> builtins..str.format#### "{}a{}b{}c{}:{}" *=AB C *=(1 2)
   >>> ('AaBbCc1:2')
   'AaBbCc1:2'

Tags get parsed objects from the reader. But they haven't been evaluated yet.
Notice the ``.#``\ s required here.

.. code-block:: REPL

   #> builtins..sorted### reverse=True key=.#str.lower (a B c)
   >>> ['c', 'B', 'a']
   ['c', 'B', 'a']

   ;; Tags call dict() on a **= Kwarg, so pairs work.
   ;; Equivalent to the above. Notice the .# is still required.
   #> builtins..sorted##**=((reverse True) (key .#str.lower)) (a B c)
   >>> ['c', 'B', 'a']
   ['c', 'B', 'a']

   ;; A mapping object works as well, of course.
   ;; The .# makes a read time dict object here.
   #> builtins..sorted##**=.#(dict : reverse True  key str.lower) (a B c)
   >>> ['c', 'B', 'a']
   ['c', 'B', 'a']

Unqualified Tags
++++++++++++++++

Sometimes tags have no qualifier.
Three such tags are built into the reader:
inject ``.#``, discard ``_#``, and gensym ``$#``.

The reader will also check the current module's ``_macro_`` namespace (if it has one)
for attributes ending in ``#`` (i.e. ``QzHASH_``)
when it encounters an unqualified tag.
The ``#`` is only in an attribute name to distinguish them from normal compile-time macros,
not to indicate arity.
It is possible to use a tag name containing extra ``#``\ s,
or ending in ``=`` if escaped with a ``\``.

Discard
+++++++

The discard ``_#`` macro omits the next expression,
even if it's a tuple.
It's a way to comment out code structurally:

.. code-block:: REPL

   #> (print 1 _#"I'm not here!" 3) _#(I'm not here either.)
   >>> print(
   ...   (1),
   ...   (3))
   1 3

Templates
+++++++++

Besides ``'``, which we've already seen,
Lissp has three other built-in reader macros that don't require a ``#``:

* ````` template quote
* ``,`` unquote
* ``,@`` splice unquote

The template quote works much like a normal quote:

.. code-block:: REPL

   #> '(1 2 3) ; quote
   >>> ((1),
   ...  (2),
   ...  (3),)
   (1, 2, 3)

   #> `(1 2 3) ; template quote
   >>> (
   ...   (1),
   ...   (2),
   ...   (3),
   ...   )
   (1, 2, 3)

Notice the results are the same,
but the template quote compiles to a call that evaluates to the result,
instead of a literal representation of the result itself.

This gives you the ability to *interpolate*
data into the tuple at the time it is evaluated,
much like a format string:

.. code-block:: REPL

   #> '(1 2 (operator..add 1 2)) ; normal quote
   >>> ((1),
   ...  (2),
   ...  ('operator..add',
   ...   (1),
   ...   (2),),)
   (1, 2, ('operator..add', 1, 2))

   #> `(1 2 ,(operator..add 1 2)) ; template and unquote
   >>> (
   ...   (1),
   ...   (2),
   ...   __import__('operator').add(
   ...     (1),
   ...     (2)),
   ...   )
   (1, 2, 3)

The splice unquote is similar, but unpacks its result:

.. code-block:: REPL

   #> `(:a ,@"bcd" :e)
   >>> (
   ...   ':a',
   ...   *('bcd'),
   ...   ':e',
   ...   )
   (':a', 'b', 'c', 'd', ':e')

Templates are *reader syntax*: because they're reader macros,
they only exist in Lissp, not Hissp.
They are abbreviations for the Hissp that they return.

If you quote an example, you can see that intermediate step:

.. code-block:: REPL

   #> '`(:a ,@"bcd" ,(operator..mul 2 3))
   >>> ('',
   ...  ':',
   ...  ':?',
   ...  ':a',
   ...  ':*',
   ...  "('bcd')",
   ...  ':?',
   ...  ('operator..mul',
   ...   (2),
   ...   (3),),
   ...  ':?',
   ...  '',)
   ('', ':', ':?', ':a', ':*', "('bcd')", ':?', ('operator..mul', 2, 3), ':?', '')

If we format that a little more nicely,
then it's easier to read:

>>> readerless(
...     ('',':',
...      ':?',':a',
...      ':*',"('bcd')",
...      ':?',('operator..mul', 2, 3),
...      ':?','')
... )
"(\n  ':a',\n  *('bcd'),\n  __import__('operator').mul(\n    (2),\n    (3)),\n  )"
>>> print(_)
(
  ':a',
  *('bcd'),
  __import__('operator').mul(
    (2),
    (3)),
  )

Templates are Lissp syntactic sugar based on what Hissp already has.

Templates are a domain-specific language for programmatically writing Hissp code,
making them valuable tools for metaprogramming.
Most compiler macros will use at least one internally.

Judicious use of sugar like this can make code much easier to read and write.
While all Turing-complete languages have the same theoretical *power*,
they are not equally *expressive*.
Metaprogramming makes a language more expressive.
Reader macros are a kind of metaprogramming.
Because you can make your own reader macros,
you can make your own sugar.

Gensyms
+++++++

The built-in tag ``$#`` creates a *generated symbol*
(gensym) based on the given symbol.
Within a template, the same gensym name always makes the same gensym:

.. code-block:: REPL

   #> `($#hiss $#hiss)
   >>> (
   ...   '_Qztamtdldr__hiss',
   ...   '_Qztamtdldr__hiss',
   ...   )
   ('_Qztamtdldr__hiss', '_Qztamtdldr__hiss')

But each new template changes the prefix hash.

.. code-block:: REPL

   #> `($#hiss $#hiss)
   >>> (
   ...   '_Qzzsoxd2io__hiss',
   ...   '_Qzzsoxd2io__hiss',
   ...   )
   ('_Qzzsoxd2io__hiss', '_Qzzsoxd2io__hiss')

Gensyms are mainly used to prevent accidental name collisions in generated code,
which is very important for reliable compiler macros.

The 40-bit hash is computed from the entire code string being read
(the whole ``.lissp`` file)
the module's `__name__`, and a count of the templates read so far this session.

(In the REPL, there is no ``.lissp`` file,
so "the entire code string" is the top-level form entered.)

A count alone isn't enough.
Files can be compiled individually in different sessions,
which would each start with a fresh counter.
It can ensure templates have a unique name within a file,
but not between files.

Adding the module's `__name__` isn't enough either,
since it will be re-used for multiple versions of the module.
The code string stands in for the module version,
without resorting to things like tedious manual versioning
or timestamps that would prohibit reproducible builds.
The `__name__` is still required in case different modules happen to have the same code,
which can sometimes happen when they are very short.

By default, the hash is a prefix, but you can mark some other location for it using a $.

Macros
======

Hissp macros are callables that are evaluated by the compiler at
*compile time*.

They take the Hissp code itself as arguments (unevaluated),
and return Hissp code as a result,
called a *macroexpansion* (even if it gets smaller).
The compiler inserts the expansion in the macro invocation's place in the code,
and then continues as normal.
If another macro invocation appears in the expansion,
it is expanded as well (this pattern is known as a *recursive macro*),
which is an ability that the reader macros lack.

The compiler recognizes a callable as a macro if it is invoked directly
from a fully-qualified ``_macro_`` namespace:

.. code-block:: REPL

   #> (hissp.._macro_.define spam :eggs) ; qualified macro
   >>> # hissp.._macro_.define
   ... __import__('builtins').globals().update(
   ...   spam=':eggs')

   #> spam
   >>> spam
   ':eggs'

The compiler will also check the current module's ``_macro_`` namespace
(if present)
for matching macro names when compiling an unqualified invocation.

While ``.lissp`` files don't have one until you add it,
the REPL automatically includes a ``_macro_``
namespace with all of the `bundled macros <hissp.macros>`:

.. code-block:: REPL

   #> _macro_.define
   >>> _macro_.define
   <function _macro_.define at ...>

   #> (define eggs :spam) ; unqualified macro
   >>> # define
   ... __import__('builtins').globals().update(
   ...   eggs=':spam')

   #> eggs
   >>> eggs
   ':spam'

The compiler helpfully includes a comment whenever it expands a macro.
Note the shorter Python comment emitted by the unqualified expansion.

You can define your own macro by putting a callable into the ``_macro_`` namespace.
Let's try it:

.. code-block:: REPL

   #> (setattr _macro_ 'hello (lambda () '(print 'hello)))
   >>> setattr(
   ...   _macro_,
   ...   'hello',
   ...   (lambda :
   ...       ('print',
   ...        ('quote',
   ...         'hello',),)
   ...   ))

   #> (hello)
   >>> # hello
   ... print(
   ...   'hello')
   hello

A zero-argument macro isn't that useful.

Let's give it one. Use a template:

.. code-block:: REPL

   #> (setattr _macro_ 'greet (lambda (name) `(print 'Hello ,name)))
   >>> setattr(
   ...   _macro_,
   ...   'greet',
   ...   (lambda name:
   ...       (
   ...         'builtins..print',
   ...         (
   ...           'quote',
   ...           '__main__..Hello',
   ...           ),
   ...         name,
   ...         )
   ...   ))

   #> (greet 'Bob)
   >>> # greet
   ... __import__('builtins').print(
   ...   '__main__..Hello',
   ...   'Bob')
   __main__..Hello Bob

Not what you expected?

A template quote automatically qualifies any unqualified symbols it contains
with `builtins` (if applicable) or the current ``__name__``
(which is ``__main__``):

.. code-block:: REPL

   #> `int ; Works directly on symbols too.
   >>> 'builtins..int'
   'builtins..int'

   #> `(int spam)
   >>> (
   ...   'builtins..int',
   ...   '__main__..spam',
   ...   )
   ('builtins..int', '__main__..spam')

Qualified symbols are especially important
when a macro expands in a module it was not defined in.
This prevents accidental name collisions
when the unqualified name was already in use.
Any `qualified identifier`_ in the expansion will automatically import any required module.

You can force an import from a particular location by using
a fully-qualified symbol yourself in the template in the first place.
Fully-qualified symbols in templates are not qualified again.
Usually, if you want an unqualified symbol in the template's result,
it's a sign that you need to use a gensym instead.
Symbols already "qualified" with a gensym hash prefix are considered "local" and do not get qualified with a module.
If you don't think it needs to be a gensym,
that's a sign that the macro could maybe be an ordinary function.

There are a few special cases worth pointing out here.

If the gensym hash is *not* in prefix position, it doesn't count as local, and gets qualified.

.. code-block:: REPL

   #> `$#spam.$eggs
   >>> '__main__..spam._Qz6ae4gut3__eggs'
   '__main__..spam._Qz6ae4gut3__eggs'

A ``_macro_`` namespace is not the same as its module.

.. code-block:: REPL

   #> (setattr _macro_ 'p123 (lambda () `(p 1 2 3 : sep :)))
   >>> setattr(
   ...   _macro_,
   ...   'p123',
   ...   (lambda :
   ...       (
   ...         '__main__..QzMaybe_.p',
   ...         (1),
   ...         (2),
   ...         (3),
   ...         ':',
   ...         '__main__..sep',
   ...         ':',
   ...         )
   ...   ))

Notice the ``QzMaybe_`` qualifying ``p``,
which means the reader could not determine if ``p`` should be qualified as a global or as a macro,
and the ``__main__`` qualifying ``sep``, which looks like it's going to be a problem.

The ``QzMaybe_`` means that the compiler will try to resolve this symbol as a macro,
and fall back to a global if it can't.

If we were to define a ``p`` global,

.. code-block:: REPL

   #> (define p print)
   >>> # define
   ... __import__('builtins').globals().update(
   ...   p=print)

Then the ``p123`` macro works.

.. code-block:: REPL

   #> (p123)
   >>> # p123
   ... __import__('builtins').globals()['p'](
   ...   (1),
   ...   (2),
   ...   (3),
   ...   sep=':')
   1:2:3

The compiler ignores qualifiers on kwargs in normal calls to make metaprogramming easier;
it looks like a problem, but it's not.
This is fine.
The templating system, on the other hand,
*has to* qualify symbols, even if they might be kwargs.
It can't tell if a tuple is going to be a normal call or a macro invocation,
where the qualification could be necessary.

We can resolve the ``QzMaybe_`` the other way by defining a ``p`` macro.

.. code-block:: REPL

   #> (setattr _macro_ 'p (lambda (: :* args) `(print ,@args)))
   >>> setattr(
   ...   _macro_,
   ...   'p',
   ...   (lambda *args:
   ...       (
   ...         'builtins..print',
   ...         *args,
   ...         )
   ...   ))

   #> (p123)
   >>> # p123
   ... # __main__..QzMaybe_.p
   ... __import__('builtins').print(
   ...   (1),
   ...   (2),
   ...   (3),
   ...   sep=':')
   1:2:3

Notice the comments indicating *two* compiler macroexpansions,
and the use of a builtin instead of the global like last time.

If you *want* to *capture* [#capture]_ an identifier (collide on purpose),
you can still put unqualified symbols into templates
by interpolating in an expression that evaluates to an unqualified
symbol. (Like a quoted symbol):

.. code-block:: REPL

   #> `(float inf)
   >>> (
   ...   'builtins..float',
   ...   '__main__..inf',
   ...   )
   ('builtins..float', '__main__..inf')

   #> `(float ,'inf)
   >>> (
   ...   'builtins..float',
   ...   'inf',
   ...   )
   ('builtins..float', 'inf')

Let's try the greet again with what we've learned about auto-qualification.
Note the three reader macros in a row: ``','``.

.. code-block:: REPL

   #> (setattr _macro_ 'greet (lambda (name) `(print ','Hello ,name)))
   >>> setattr(
   ...   _macro_,
   ...   'greet',
   ...   (lambda name:
   ...       (
   ...         'builtins..print',
   ...         (
   ...           'quote',
   ...           'Hello',
   ...           ),
   ...         name,
   ...         )
   ...   ))

   #> (greet 'Bob)
   >>> # greet
   ... __import__('builtins').print(
   ...   'Hello',
   ...   'Bob')
   Hello Bob

Using a symbol here is a bit sloppy.
If you really meant it to be text, rather than an identifier,
a "" token might have been a better idea:

.. code-block:: REPL

   #> (setattr _macro_ 'greet (lambda (name) `(print "Hello" ,name)))
   >>> setattr(
   ...   _macro_,
   ...   'greet',
   ...   (lambda name:
   ...       (
   ...         'builtins..print',
   ...         "('Hello')",
   ...         name,
   ...         )
   ...   ))

   #> (greet 'Bob)
   >>> # greet
   ... __import__('builtins').print(
   ...   ('Hello'),
   ...   'Bob')
   Hello Bob

While the parentheses around the 'Hello' don't change the meaning of the expression in Python,
it does prevent the template reader macro from qualifying it like a symbol.

There's really no need to use a macro when a function will do.
The above are for illustrative purposes only.
But there are times when a function will not do:

.. _anaphoric:

.. code-block:: REPL

   #> (setattr _macro_ '% (lambda (: :* body) `(lambda (,'%) ,body)))
   >>> setattr(
   ...   _macro_,
   ...   'QzPCENT_',
   ...   (lambda *body:
   ...       (
   ...         'lambda',
   ...         (
   ...           'QzPCENT_',
   ...           ),
   ...         body,
   ...         )
   ...   ))

   #> ((lambda (%)
   #..   (print (.upper %)))              ;This lambda expression
   #.. "q")
   >>> (lambda QzPCENT_:
   ...     print(
   ...       QzPCENT_.upper())
   ... )(
   ...   ('q'))
   Q

   #> ((% print (.upper %))               ; can now be abbreviated.
   #.. "q")
   >>> # QzPCENT_
   ... (lambda QzPCENT_:
   ...     print(
   ...       QzPCENT_.upper())
   ... )(
   ...   ('q'))
   Q

   #> (any (map (% print (.upper %) ":" %)
   #..          "abc"))
   >>> any(
   ...   map(
   ...     # QzPCENT_
   ...     (lambda QzPCENT_:
   ...         print(
   ...           QzPCENT_.upper(),
   ...           (':'),
   ...           QzPCENT_)
   ...     ),
   ...     ('abc')))
   A : a
   B : b
   C : c
   False

This macro is a metaprogram that creates a one-argument lambda.
This is an example of intentional capture.
The anaphor [#capture]_ is ``%``.
Try doing that in Python.
You can get pretty close with higher-order functions,
but you can't delay the evaluation of the `.upper()<str.upper>`
without a lambda,
which really negates the whole point of creating a shorter lambda.

Delaying (and then reordering, repeating or skipping)
evaluation is one of the main uses of macros.
You can do that much with a lambda in Python.
But advanced macros can do other things:
inject anaphors,
introduce new bindings,
do a find-and-replace on symbols in code,
implement whole DSLs,
or all of these at once.
You have full programmatic control over the *code itself*,
with the full power of Python's ecosystem.

These techniques will be covered in more detail in the `macro tutorial <macro_tutorial>`.

Compiling Packages
==================

It isn't always necessary to create a compiled file.
While you could compile it to Python first,
you can run a ``.lissp`` file directly as the main module using ``hissp``,

.. code-block:: console

   $ python -m hissp foo.lissp

or

.. code-block:: console

   $ lissp foo.lissp

But you'll probably want to break a larger project up into smaller modules,
and those must be compiled for import.

The recommended way to compile a Lissp project is to put a call to
`transpile()` in the main module and in each ``__init__.py``—
with the name of each top-level ``.lissp`` file,
or ``.lissp`` file in the corresponding package,
respectively::

   import hissp

   hissp.transpile(__package__, "spam", "eggs", "etc")

Or equivalently in Lissp, used either at the REPL or if the main module is written in Lissp:

.. code-block:: Lissp

   (hissp..transpile __package__ 'spam 'eggs 'etc)

This will automatically compile each named Lissp module,
which gives you fine-grained control over what gets compiled when.

.. sidebar:: The Lissp source for `hissp.macros`

   is included in the distributed Hissp package for completeness,
   but Hissp doesn't automatically recompile it on import.
   If you do make edits, don't forget to recompile!

Before distributing a Lissp project to users who won't be modifying it,
compilation could be disabled or removed altogether,
especially when not distributing the ``.lissp`` sources.
If you don't want the ``hissp`` package to be a dependency,
make sure you remove or disable imports of it as well.

.. Note::
   You normally *do* want to recompile the whole project during development.
   CPython only needs to recompile any changed ``.py`` files to ``.pyc``,
   but because macros run at compile time,
   this wouldn't work well for Lissp.

Changing a macro in one file normally doesn't affect the code that uses
it in other files until they are recompiled.
That is why `transpile()` will recompile the named files unconditionally.
Even if the corresponding source has not changed,
the compiled output may be different due to an updated macro in another file.

Fortunately, Lissp compilation is usually pretty fast,
but if desired (perhaps due to a slow macro),
you can remove a name passed to the `transpile()`
call to stop recompiling that file.
Then you can compile the file manually at the REPL as needed using `transpile()`.

Unicode Normalization
=====================

.. Note::
   If you plan on only using ASCII in symbols,
   you can skip this section.

The munger also normalizes Unicode characters to NFKC,
because Python already does this when converting identifiers to strings:

>>> ascii_a = 'A'
>>> unicode_a = '𝐀'
>>> ascii_a == unicode_a
False
>>> import unicodedata
>>> ascii_a == unicodedata.normalize('NFKC', unicode_a)
True
>>> A = unicodedata.name(ascii_a)
>>> A
'LATIN CAPITAL LETTER A'
>>> 𝐀 = unicodedata.name(unicode_a)  # A Unicode variable name.
>>> 𝐀  # Different, as expected.
'MATHEMATICAL BOLD CAPITAL A'
>>> A  # Huh?
'MATHEMATICAL BOLD CAPITAL A'
>>> globals()[unicode_a]  # The Unicode name does not work!
Traceback (most recent call last):
  ...
KeyError: '𝐀'
>>> globals()[ascii_a]  # Retrieve with the normalized name.
'MATHEMATICAL BOLD CAPITAL A'

The ASCII ``A`` and Unicode ``𝐀`` are aliases of the *same identifier*
as far as Python is concerned.
But the globals dict can only use one of them as its key,
so it uses the normalized version.

Remember our first munging example?

.. code-block:: REPL

   #> (types..SimpleNamespace)
   >>> __import__('types').SimpleNamespace()
   namespace()

   #> (setattr _ ; The namespace.
   #..         '𝐀 ; Compiles to a string representing an identifier.
   #..         42)
   >>> setattr(
   ...   _,
   ...   'A',
   ...   (42))

   #> _
   >>> _
   namespace(A=42)

   #> _.𝐀 ; Munges and compiles to attribute identifier.
   >>> _.A
   42

Notice that the compiled Python is pure ASCII in this case.
This example couldn't work if the munger didn't normalize symbols,
because ``setattr()`` would store the Unicode ``𝐀`` in ``spam``'s ``__dict__``,
but ``spam.𝐀`` would do the same thing as ``spam.A``,
and there would be no such attribute.

.. rubric:: Footnotes

.. [#EOF] End Of File. Usually Ctrl+D, but enter Ctrl+Z on Windows.
          This doesn't quit Python if the REPL was launched from Python,
          unlike ``(exit)``.

.. [#key] The equivalent concept is called a *keyword* in other Lisps,
          but that means something else in Python.

.. [#LambdaList] The equivalent concept is called the "lambda list" in Common Lisp,
   and the "params vector" in Clojure,
   but Hissp is made of tuples, not linked-lists or vectors, hence "parameters tuple".

.. [#capture] In natural language,
   anaphors are words used to avoid repetition,
   and they refer to something contextually.
   Pronouns are one example.
   When symbol capture is done on purpose in Lisp,
   these are known as *anaphoric macros*,
   and the bound name is called an *anaphor*,
   which is often chosen to be a pronoun word.
   (When it's done on accident, these are known as *bugs*.)
