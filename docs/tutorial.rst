.. Copyright 2019, 2020 Matthew Egan Odendahl
   SPDX-License-Identifier: Apache-2.0

..  Hidden doctest requires basic macros for REPL-consistent behavior.
    #> (operator..setitem (globals) '_macro_ (types..SimpleNamespace : :** (vars hissp.basic.._macro_)))
    >>> __import__('operator').setitem(
    ...   globals(),
    ...   '_macro_',
    ...   __import__('types').SimpleNamespace(
    ...     **vars(
    ...       __import__('hissp.basic',fromlist='?')._macro_)))

========
Tutorial
========

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
(the `ast` module)
which is accessible to Python programs,
but because it represents all of the possible Python syntax,
which is considerable, it difficult to use effectively for metaprogramming.

The Hissp compiler, in contrast, compiles Hissp code to a simplified
*functional subset* of Python.
This sacrifice ultimately gives Hissp greater expressive power,
because it makes Hissp a simpler language that is easier to manipulate
programmatically.

In Hissp, you write in this parsed form far more directly:
*Hissp code is AST.*

Hello World
===========

A Hissp program is made of Python objects composed together with tuples
which represent the syntax tree structure.

You can invoke the Hissp compiler directly from Python.

>>> from hissp.compiler import readerless
>>> readerless(
...     ('lambda',('name',),
...      ('print',('quote','Hello'),'name',),)
... )
"(lambda name:\n  print(\n    'Hello',\n    name))"
>>> print(_)
(lambda name:
  print(
    'Hello',
    name))
>>> eval(_)('World')
Hello World

The `readerless()` function takes a Hissp program as input,
and returns its Python translation as a string.

Let's break this down.
Notice that the first element of each tuple designates its function.

In the case of ``('print',('quote','Hello'),'name',)``,
the first element represents a call to the `print()<print>` function.
The remaining elements are the arguments.

The interpretation of the ``lambda`` form is different.
It represents a lambda expression, rather than a function call.
``('name',)`` is its parameters tuple.
The remainder is its body.

Note that ``'name'`` was used as an identifier,
but the ``('quote','Hello')`` expression was translated to a string.
That's the interpretation of ``quote``:
its argument is seen as "data" rather than code by the compiler.

Together, ``lambda`` and ``quote`` are the only "special forms"
(forms with a "special" interpretation) known to the compiler.
There are ways to define more forms with special interpretations,
called "macros". This is how Hissp gets much of its expressive power.

``('quote','Hello')`` seems a little verbose compared to its Python
translation.
This could get tedious every time we need a string.
Isn't there something we can do?

Let's try it.

>>> def q(data):
...     return 'quote', data
...
>>> q('Hello')
('quote', 'Hello')

You may not have noticed, but congratulations.
This is metaprogramming:
We just wrote code that writes code.
It output Hissp code, which changes based on an input.

And, in fact, this ``q()`` function takes the place of a "reader macro",
which I'll explain shortly.

Let's use it.

>>> readerless(
...     ('lambda',('name'),
...      ('print',q('Hello'),'name',),)
... )
"(lambda n,a,m,e:\n  print(\n    'Hello',\n    name))"
>>> print(_)
(lambda n,a,m,e:
  print(
    'Hello',
    name))
>>> eval(_)('World')
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
TypeError: <lambda>() missing 3 required positional arguments: 'a', 'm', and 'e'

What happened?

Look at the compiled Python.
Our ``q()`` worked, but we forgot the comma in ``('name')``.
(Yes, I did that on purpose.)

.. Caution::
   When writing Hissp tuples,
   it's best to think of commas as *terminators*,
   rather than *separators*, to avoid this kind of problem.
   In Python, (except for the empty tuple ``()``)
   it is the *comma* that creates a tuple, **not** the parentheses.
   The parentheses only control evaluation order.
   There are some contexts where tuples don't require parentheses at all.

Let's try that again.

>>> readerless(
...     ('lambda',('name',),
...      ('print',q('Hello'),'name',),)
... )
"(lambda name:\n  print(\n    'Hello',\n    name))"

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
And to "speak" the written word back into Hissp, we need a "reader".
Hissp comes with a :mod:`hissp.reader` module that interprets a lightweight
language called *Lissp* as Hissp code.

Lissp is made of text.
Lissp is to the written word as Hissp is to the spoken word.
When you are writing Lissp, you are still writing Hissp.

Lissp
  A lightweight textual language representing Hissp,
  as defined by Hissp's basic reader.

Lissp also includes "reader macros",
that act like the ``q()`` example:
metaprogramming abbreviations.

Reader macro
  An abbreviation used by the reader.
  These are not part of the Hissp langauge proper,
  but rather are functions that *expand* to Hissp;
  They run at *read time* and return Hissp code.

Read time
  The pre-compile phase that translates Lissp to Hissp:
  when the reader runs.

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
--------

Hissp comes with its own interactive shell, called the basic REPL.

REPL
  Acronym for Read, Evaluate, Print, Loop.
  The interactive shell.

You can launch the REPL from Python code (which is useful for debugging,
like `code.interact`),
But let's start it from the command line using an appropriate Python interpreter::

    $ python -m hissp

Or, if you installed the hissp package using pip,
you can use the installed entry point script::

    $ lissp

You should see the Lissp prompt ``#>`` appear.

You can quit with ``(exit)`` or EOF [#EOF]_, same as Python's shell.

The basic REPL shows the Python translation of the read Lissp
and evaluates it.

Literals
--------

Most literals work just like Python:

.. code-block:: Lissp

    #> 1 ; Lissp comments use ';' instead of '#'.
    >>> (1)
    1

    #> ;; Use two ';'s if it starts the line.
    #..-1.0  ; float
    >>> (-1.0)
    -1.0

    #> 1e10  ; exponent notation
    >>> (10000000000.0)
    10000000000.0

    #> 2+3j  ; complex
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

Comments, as one might expect, are ignored by the reader,
and do not appear in the Hissp output.

Strings
#######

Double-quoted strings may contain newlines,
but otherwise behave as Python's and respect the same escape codes:

.. code-block:: Lissp

    #> "Three
    #..lines\ntotal"
    >>> 'Three\nlines\ntotal'
    'Three\nlines\ntotal'

There are no triple double-quoted strings in Lissp.

Strings are implicitly quoted:

.. code-block:: Lissp

    #> (quote
    #.. (lambda (name)
    #..  (print "Hello" name)))
    >>> ('lambda', ('name',), ('print', ('quote', 'Hello', {':str': True}), 'name'))
    ('lambda', ('name',), ('print', ('quote', 'Hello', {':str': True}), 'name'))

The reader also adds a little *metadata* [#meta]_ in the quote form
(the ``{':str': True}`` bit)
indicating that it was read from a double-quoted string literal,
rather than a symbol.
Metadata has no effect on how a ``quote`` form is compiled,
but may be used macros and reader macros.

Symbols
#######

In our basic example:

.. code-block:: Lissp

    (lambda (name)
     (print 'Hello name))

``lambda``, ``name``, ``print``, ``Hello``, and
``name`` are read as *symbols*.

Symbols should be used for *identifiers* (variable names and the like).

The distinction between a quoted symbol and a double-quoted string
exists only in Lissp a the reader level.
It's two ways of writing the same thing in Hissp.
Recall that the argument of the ``quote`` special form is seen as data:

.. code-block:: Lissp

    #> (quote
    #.. (lambda (name)
    #..  (print 'Hello name)))
    >>> ('lambda', ('name',), ('print', ('quote', 'Hello'), 'name'))
    ('lambda', ('name',), ('print', ('quote', 'Hello'), 'name'))

This shows us how that Lissp would get translated to Hissp.
Notice that symbols become strings in Hissp.

Symbols with an internal ``.`` can access attributes:

.. code-block:: Lissp

    #> int.__name__
    >>> int.__name__
    'int'

Munging
~~~~~~~

Symbols have another important difference from double-quoted strings:

.. code-block:: Lissp

    #> 'foo->bar?  ; xH_ is for "Hyphen"; xGT_ for "Greater Than/riGhT".
    >>> 'fooxH_xGT_barxQUERY_'
    'fooxH_xGT_barxQUERY_'

    #> "foo->bar?"
    >>> 'foo->bar?'
    'foo->bar?'

Symbols may contain special characters,
but the Python identifiers they represent cannot.
Therefore, the reader *munges* symbols with forbidden characters
to valid identifier strings by using ``xQUOTEDxWORDS_``.

This format was chosen because it contains an underscore
and both lower-case and upper-case letters,
which makes it distinct from standard Python naming conventions:
``lower_case_with_underscores``, ``UPPER_CASE_WITH_UNDERSCORES``. and ``CapWords``.
This makes it easy to tell if an identifier contains munged characters,
which makes demunging possible in the normal case.
It also cannot introduce a leading underscore,
which can have special meaning in Python.
It might have been simpler to use the character's `ord()<ord>`,
but it's important that the munged symbols still be human-readable.

Munging happens at *read time*, which means you can use a munged symbol both
as an identifier and as a string representing that identifier:

.. code-block:: Lissp

    #> (define spam (lambda ()))
    >>> # define
    ... __import__('operator').setitem(
    ...   __import__('builtins').globals(),
    ...   'spam',
    ...   (lambda :()))

    #> (setattr spam '!@%$ 'eggs)
    >>> setattr(
    ...   spam,
    ...   'xBANG_xAT_xPCENT_xDOLR_',
    ...   'eggs')

    #> spam.!@%$
    >>> spam.xBANG_xAT_xPCENT_xDOLR_
    'eggs'


Spaces, double quotes, parentheses, and semicolons are allowed in symbols,
but they must each be escaped with a backslash to prevent it from terminating the symbol.
(Escape a backslash with another backslash.)

.. code-block:: Lissp

    #> 'embedded\ space
    >>> 'embeddedxSPACE_space'
    'embeddedxSPACE_space'

Python does not allow some characters to start an identifier that it allows inside identifiers,
such as digits.
You also have to escape these if they begin a symbol to distinguish them from numbers.

.. code-block:: Lissp

    #> '\108
    >>> 'xDIGITxONE_08'
    'xDIGITxONE_08'

Notice that only the first digit had to be munged to make it a valid Python identifier.

The munger also normalizes unicode symbols to NFKC,
because Python already does this when converting identifiers to strings:

>>> ascii_a = 'A'
>>> unicode_a = '𝐀'
>>> ascii_a == unicode_a
False
>>> import unicodedata
>>> ascii_a == unicodedata.normalize('NFKC', unicode_a)
True
>>> 𝐀 = unicodedata.name(unicode_a)
>>> globals()[ascii_a]
'MATHEMATICAL BOLD CAPITAL A'

Control Words
~~~~~~~~~~~~~

Symbols that begin with a ``:`` are called *control words* [#key]_.
These are for when you want a symbol but it's not meant to be used as
an identifier. Thus, they do not get munged:

.. code-block:: Lissp

    #> :foo->bar?
    >>> ':foo->bar?'
    ':foo->bar?'

Control words evaluate to strings,
so you usually don't need to quote them,
but you can:

.. code-block:: Lissp

    #> ':foo->bar?
    >>> ':foo->bar?'
    ':foo->bar?'

Note that double quotes do the same thing:

.. code-block:: Lissp

    #> ":foo->bar?"
    >>> ':foo->bar?'
    ':foo->bar?'

The lambda special form,
as well as certain macros,
use certain "active"
control words as syntactic elements to control the interpretation of other elements,
hence the name.

Some control words are also "active" in normal function calls.
The single/paired argument separator ``:``
and after that, the unpacking control words ``:*``/``:**``, for example.
You must quote these like ``':`` or ``":"`` to pass them as data in that context.

Macros operate on code before evaluation,
so they can also distinguish a raw control word from a quoted one.

.. _qualified identifiers:

Qualified Identifiers
~~~~~~~~~~~~~~~~~~~~~

You can refer to variables defined in any module by using a
*qualified identifier*:

.. code-block:: Lissp

    #> operator.  ; Module identifiers end in a dot and automatically import.
    >>> __import__('operator')
    <module 'operator' from '...operator.py'>

    #> (operator..add 40 2)  ; Qualified identifiers include their module.
    >>> __import__('operator').add(
    ...   (40),
    ...   (2))
    42

Notice the part before the ``..`` is imported and the part after is
looked up in the imported module.

This capability is important for macros that are defined in one module,
but used in another.

Compound Expressions
--------------------

Literals are just the basic building blocks.
To do anything interesting with them, you have to combine them.

Empty
#####

The empty tuple ``()`` might as well be a literal:

.. code-block:: Lissp

    #> ()
    >>> ()
    ()

Lambdas
#######

The anonymous function special form::

    (lambda (<parameters>)
      <body>)

The parameters tuple is divided into ``(<single> : <paired>)``

Parameter types are the same as Python's.
For example:

.. code-block:: Lissp

    #> (lambda (a :/  ; positional only
    #..         b  ; positional
    #..         : e 1  f 2  ; default
    #..         :* args  h 4  i :?  j 1  ; kwonly
    #..         :** kwargs)
    #..  42)
    >>> (lambda a,/,b,e=(1),f=(2),*args,h=(4),i,j=(1),**kwargs:(42))
    <function <lambda> at ...>

The special control words ``:*`` and ``:**`` designate the remainder of the
positional and keyword parameters, respectively:

.. code-block:: Lissp

    #> (lambda (: :* args :** kwargs)
    #..  (print args)
    #..  (print kwargs)  ; Body expressions evaluate in order.
    #..  :return-value)  ; The last one is returned.
    >>> (lambda *args,**kwargs:(
    ...   print(
    ...     args),
    ...   print(
    ...     kwargs),
    ...   ':return-value')[-1])
    <function <lambda> at ...>

    #> (_ 1 : b :c)
    >>> _(
    ...   (1),
    ...   b=':c')
    (1,)
    {'b': ':c'}
    ':return-value'

You can omit the right of a pair with ``:?``
(except the final ``**kwargs``).
Also note that the body can be empty:

.. code-block:: Lissp

    #> (lambda (: a 1  :/ :?  :* :?  b :?  c 2))
    >>> (lambda a=(1),/,*,b,c=(2):())
    <function <lambda> at ...>

Note that positional-only arguments with defaults must appear after the ``:``,
which forces the ``:/`` into the paired side.
Everything on the paired side must be paired, no exceptions.
(Even though ``:/`` can only be paired with ``:?``,
special casing that to not require the ``:?``
would make macro writing more difficult.)

The ``:`` may be omitted if there are no paired parameters:

.. code-block:: Lissp

    #> (lambda (a b c :))  ; No pairs after ':'.
    >>> (lambda a,b,c:())
    <function <lambda> at ...>

    #> (lambda (a b c))  ; The ':' was omitted.
    >>> (lambda a,b,c:())
    <function <lambda> at ...>

    #> (lambda (:))  ; Colon isn't doing anything.
    >>> (lambda :())
    <function <lambda> at ...>

    #> (lambda ())  ; You can omit it.
    >>> (lambda :())
    <function <lambda> at ...>

The ``:`` is required if there are any paired parameters, even if
there are no single parameters:

.. code-block:: Lissp

    #> (lambda (: :** kwargs))
    >>> (lambda **kwargs:())
    <function <lambda> at ...>

Calls
#####

Any tuple that is not quoted, empty, or a special form or macro is
a runtime call.

Like Python, it has three parts::

    (<callable> <args> : <kwargs>)

For example:

.. code-block:: Lissp

    #> (print 1 2 3 : sep ":"  end "\n.")
    >>> print(
    ...   (1),
    ...   (2),
    ...   (3),
    ...   sep=':',
    ...   end='\n.')
    1:2:3
    .

Either ``<args>`` or ``<kwargs>`` may be empty:

.. code-block:: Lissp

    #> (int :)
    >>> int()
    0

    #> (print :foo :bar :)
    >>> print(
    ...   ':foo',
    ...   ':bar')
    :foo :bar

    #> (print : end "X")
    >>> print(
    ...   end='X')
    X

The ``:`` is optional if the ``<kwargs>`` part is empty:

.. code-block:: Lissp

    #> (int)
    >>> int()
    0

    #> (float "inf")
    >>> float(
    ...   'inf')
    inf

The ``<kwargs>`` part has implicit pairs; there must be an even number.

Use the special control words ``:*`` for iterable unpacking,
``:?`` to pass by position and ``:**`` for mapping unpacking:

.. code-block:: Lissp

    #> (print : :* '(1 2)  :? 3  :* '(4)  :** (dict : sep :  end "\n."))
    >>> print(
    ...   *(1, 2),
    ...   (3),
    ...   *(4,),
    ...   **dict(
    ...     sep=':',
    ...     end='\n.'))
    1:2:3:4
    .

Unlike other control words, these can be repeated,
but (as in Python) a '*' is not allowed to follow '**'.

Method calls are similar to function calls::

    (.<method name> <self> <args> : <kwargs>)

Like Clojure, a method on the first "argument" (``<self>``) is assumed if the
function name starts with a dot:

.. code-block:: Lissp

    #> (.conjugate 1j)
    >>> (1j).conjugate()
    -1j

    #> (.decode b"\xfffoo" : errors 'ignore)
    >>> b'\xfffoo'.decode(
    ...   errors='ignore')
    'foo'

Reader Macros
=============

Reader macros in Lissp consist of a symbol ending with a ``#``
followed by another form.
The function named by the qualified identifier is invoked on the form,
and the reader embeds the resulting object into the output Hissp:

.. code-block:: Lissp

    #> builtins..float#inf
    >>> __import__('pickle').loads(  # inf
    ...     b'Finf\n.'
    ... )
    inf

This inserts an actual ``inf`` object at read time into the Hissp code.
Since this isn't a valid literal, it has to compile to a pickle.
You should normally try to avoid emitting pickles
(e.g. use ``(float 'inf)`` or `math..inf <math.inf>` instead),
but note that another macro would get the original object,
since the code hasn't been compiled yet, which may be useful.
While unpickling does have some overhead,
it may be worth it if constructing the object normally has even more.
Naturally, the object must be picklable to emit a pickle.

Reader macros can also be unqualified.
These three macros are built into the reader:
Inject ``.#``, discard ``_#``, and gensym ``$#``.
The reader also will check the current module's ``_macro_`` namespace (if it has one)
when it encounters and unqualified macro name.

If you need more than one argument for a reader macro, use the built-in
inject ``.#`` macro, which evaluates a form at read time:

.. code-block:: Lissp

    #> .#(fractions..Fraction 1 2)
    >>> __import__('pickle').loads(  # Fraction(1, 2)
    ...     b'cfractions\nFraction\n(V1/2\ntR.'
    ... )
    Fraction(1, 2)

And can inject arbitrary text into the compiled output:

.. code-block:: Lissp

    #> .#"{(1, 2): \"\"\"buckle my shoe\"\"\"}  # This is Python!"
    >>> {(1, 2): """buckle my shoe"""}  # This is Python!
    {(1, 2): 'buckle my shoe'}

Reader macros compose:

.. code-block:: Lissp

    #> '.#"{(3, 4): 'shut the door'}" ; this quoted inject is a string
    >>> "{(3, 4): 'shut the door'}"
    "{(3, 4): 'shut the door'}"

    #> '.#.#"{(5, 6): 'pick up sticks'}" ; even quoted, this double inject is a dict
    >>> {(5, 6): 'pick up sticks'}
    {(5, 6): 'pick up sticks'}

The discard ``_#`` macro omits the next expression.
It's a way to comment out code structurally:

.. code-block:: Lissp

    #> (print 1 _#2 3)
    >>> print(
    ...   (1),
    ...   (3))
    1 3

Templates
---------

Besides ``'``, which we've already seen,
Lissp has three other built-in reader macros that don't require a ``#``:

* ````` template quote
* ``,`` unquote
* ``,@`` splice unquote

The template quote works much like a normal quote:

.. code-block:: Lissp

    #> '(1 2 3)  ; quote
    >>> (1, 2, 3)
    (1, 2, 3)

    #> `(1 2 3)  ; template quote
    >>> (lambda *xAUTO0_:xAUTO0_)(
    ...   (1),
    ...   (2),
    ...   (3))
    (1, 2, 3)

Notice the results are the same,
but the template quote becomes the code that evaluates to the result,
instead of the quoted result itself.

This gives you the ability to *interpolate*
data into the tuple at the time it is evaluated,
much like a template or format string:

.. code-block:: Lissp

    #> '(1 2 (operator..add 1 2))  ; normal quote
    >>> (1, 2, ('operator..add', 1, 2))
    (1, 2, ('operator..add', 1, 2))

    #> `(1 2 ,(operator..add 1 2))  ; template and unquote
    >>> (lambda *xAUTO0_:xAUTO0_)(
    ...   (1),
    ...   (2),
    ...   __import__('operator').add(
    ...     (1),
    ...     (2)))
    (1, 2, 3)

The splice unquote is similar, but unpacks its result:

.. code-block:: Lissp

    #> `(:a ,@"bcd" :e)
    >>> (lambda *xAUTO0_:xAUTO0_)(
    ...   ':a',
    ...   *'bcd',
    ...   ':e')
    (':a', 'b', 'c', 'd', ':e')

Templates are *reader syntax*: because they're reader macros,
they only exist in Lissp, not Hissp.
They are abbreviations for the Hissp that they return.

If you quote an example, you can see that intermediate step:

.. code-block:: Lissp

    #> '`(:a ,@"bcd" ,(opearator..mul 2 3))
    >>> (('lambda', (':', ':*', 'xAUTO0_'), 'xAUTO0_'),
    ...  ':',
    ...  ':?',
    ...  ':a',
    ...  ':*',
    ...  ('quote', 'bcd', {':str': True}),
    ...  ':?',
    ...  ('opearator..mul', 2, 3))
    (('lambda', (':', ':*', 'xAUTO0_'), 'xAUTO0_'), ':', ':?', ':a', ':*', ('quote', 'bcd', {':str': True}), ':?', ('opearator..mul', 2, 3))

Templates are Lissp syntactic sugar based on what Hissp already has.

Judicious use of sugar can make code much easier to read and write.
While all Turing-complete languages have the same theoretical *power*,
they are not equally *expressive*.
Metaprogramming makes a language more expressive.
Reader macros are a kind of metaprogramming.
Because you can make your own reader macros, you can make your own sugar.

Templates are extremely valuable tools for metaprogramming.
Most macros will use at least one internally.

Gensyms
#######
The final builtin reader macro ``$#`` creates a *generated symbol*
(gensym) based on the given symbol.
Within a template, the same gensym name always makes the same gensym:

.. code-block:: Lissp

    #> `($#hiss $#hiss)
    >>> (lambda *xAUTO0_:xAUTO0_)(
    ...   '_hissxAUTO..._',
    ...   '_hissxAUTO..._')
    ('_hissxAUTO..._', '_hissxAUTO..._')

But each new template increments the counter.
(The numbers have been elided to make the doctests work, but they're the same
as well. E.g. ``_hissxAUTO42_``. Try it.)
Gensyms are mainly used to prevent accidental name collisions in generated code,
which is very important for reliable macros.

Collection Atoms
----------------

A subset of Python's data structure notation works in Lissp as well:

.. code-block:: Lissp

    #> [1,2,3]
    >>> [1, 2, 3]
    [1, 2, 3]

    #> {'foo':2}
    >>> {'foo': 2}
    {'foo': 2}

You can nest these to create small, JSON-like data structures
which can be very useful as inputs to macros,
(especially reader macros, which can only take one argument).

.. sidebar:: Except for the empty tuple.

   You can quote it if you want, it doesn't change the result:

   .. code-block:: Lissp

       #> '()
       >>> ()
       ()

       #> ()
       >>> ()
       ()

   However, macros could distinguish these cases,
   because they act before evaluation.

Tuples are different.
Since they normally represent code,
you must quote them to use them as data.

.. Caution::
   To keep the grammar simple, spaces, double quotes, parentheses, and semicolons
   in collection atoms must be escaped with a backslash, even in nested strings.

   While a significantly more complex reader could distinguish these cases without escapes
   (as Python does),
   Lissp doesn't really need this capability because it can already read in arbitrary
   Python expressions using the inject macro ``.#``.
   The collection atoms are just a convenience notation for simple cases.

Unlike Python's notation,
because these collections are read in as a *single atom*,
they may contain only static values discernible at read time.
If you want to interpolate runtime data,
use function calls and templates instead:

.. code-block:: Lissp

    #> (list `(,@(.upper "abc") ,@[1,2,3] ,(.title "zed")))
    >>> list(
    ...   (lambda *xAUTO0_:xAUTO0_)(
    ...     *'abc'.upper(),
    ...     *[1, 2, 3],
    ...     'zed'.title()))
    ['A', 'B', 'C', 1, 2, 3, 'Zed']

If this is still too verbose for your taste,
remember that you can use helper functions or metaprogramming to simplify:

.. code-block:: Lissp

    #> (define enlist  ; use instead of []
    #.. (lambda (: :* args)
    #..  (list args)))
    >>> # define
    ... __import__('operator').setitem(
    ...   __import__('builtins').globals(),
    ...   'enlist',
    ...   (lambda *args:
    ...     list(
    ...       args)))

    #> (enlist 'A 'B 'C (enlist 1 2 3) (.title "zed"))
    >>> enlist(
    ...   'A',
    ...   'B',
    ...   'C',
    ...   enlist(
    ...     (1),
    ...     (2),
    ...     (3)),
    ...   'zed'.title())
    ['A', 'B', 'C', [1, 2, 3], 'Zed']

You can also use the unpacking control words in these:

.. code-block:: Lissp

    #> (enlist : :*(.upper "abc")  :? [1,2,3]  :? (.title "zed"))
    >>> enlist(
    ...   *'abc'.upper(),
    ...   [1, 2, 3],
    ...   'zed'.title())
    ['A', 'B', 'C', [1, 2, 3], 'Zed']

Macros
======

Hissp macros are callables that are evaluated by the compiler at
*compile time*.

They take the Hissp code itself as arguments (they're all quoted)
and return Hissp code as a result,
called a *macroexpansion* (even if it gets smaller).
The compiler inserts the expansion in the macro invocation's place in the code,
and then continues as normal.
If another macro invocation appears in the expansion,
it is expanded as well (this pattern is known as a *recursive macro*),
which is an ability that the reader macros lack.

The compiler recognizes a callable as a macro if it is invoked directly
from a ``_macro_`` namespace:

.. code-block:: Lissp

    #> (hissp.basic.._macro_.define spam :eggs) ; qualified macro
    >>> # hissp.basic.._macro_.define
    ... __import__('operator').setitem(
    ...   __import__('builtins').globals(),
    ...   'spam',
    ...   ':eggs')

    #> spam
    >>> spam
    ':eggs'

The compiler will also check the current module's ``_macro_`` namespace
(if present)
for matching macro names when compiling an unqualified invocation.

The REPL automatically includes a ``_macro_``
namespace with all of the basic macros:

.. code-block:: Lissp

    #> _macro_.define
    >>> _macro_.define
    <function _macro_.define at ...>

    #> (define eggs :spam)  ; unqualified macro
    >>> # define
    ... __import__('operator').setitem(
    ...   __import__('builtins').globals(),
    ...   'eggs',
    ...   ':spam')

    #> eggs
    >>> eggs
    ':spam'

The compiler helpfully includes a comment whenever it expands a macro.
Note the shorter comment emitted by the unqualified expansion.

You can define your own macro by putting a callable into the ``_macro_`` namespace.
Let's try it:

.. code-block:: Lissp

    #> (setattr _macro_ 'hello (lambda () '(print 'hello)))
    >>> setattr(
    ...   _macro_,
    ...   'hello',
    ...   (lambda :('print', ('quote', 'hello'))))

    #> (hello)
    >>> # hello
    ... print(
    ...   'hello')
    hello

A zero-argument macro isn't that useful.
We can do better. Let's use a template:

.. code-block:: Lissp

    #> (setattr _macro_ 'greet (lambda (name) `(print 'Hello ,name)))
    >>> setattr(
    ...   _macro_,
    ...   'greet',
    ...   (lambda name:
    ...     (lambda *xAUTO0_:xAUTO0_)(
    ...       'builtins..print',
    ...       (lambda *xAUTO0_:xAUTO0_)(
    ...         'quote',
    ...         '__main__..Hello'),
    ...       name)))

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

.. code-block:: Lissp

    #> `int  ; Works directly on symbols too.
    >>> 'builtins..int'
    'builtins..int'

    #> `(int spam)
    >>> (lambda *xAUTO0_:xAUTO0_)(
    ...   'builtins..int',
    ...   '__main__..spam')
    ('builtins..int', '__main__..spam')

Qualified symbols are especially important
when a macro expands in a module it was not defined in.
This prevents accidental name collisions
when the unqualified name was already in use.
And the qualified symbol automatically imports any required helpers.

You can force an import from a particular location by using
a qualified symbol in the template in the first place.
Usually if you want an unqualified symbol in the template,
it's a sign that you need to use a gensym instead.
Gensyms are never qualified.
If you don't think it needs to be a gensym,
that's a sign that the macro could maybe be an ordinary function
instead.

If you *want* to *capture* [#capture]_ a symbol (collide on purpose),
you can still put unqualified symbols into templates
by interpolating in an expression that evaluates to an unqualified
symbol. (Like a quoted symbol):

.. code-block:: Lissp

    #> `(float inf)
    >>> (lambda *xAUTO0_:xAUTO0_)(
    ...   'builtins..float',
    ...   '__main__..inf')
    ('builtins..float', '__main__..inf')

    #> `(float ,'inf)
    >>> (lambda *xAUTO0_:xAUTO0_)(
    ...   'builtins..float',
    ...   'inf')
    ('builtins..float', 'inf')

Let's try again. (Yes, reader macros compose like that.):

.. code-block:: Lissp

    #> (setattr _macro_ 'greet (lambda (name) `(print ','Hello ,name)))
    >>> setattr(
    ...   _macro_,
    ...   'greet',
    ...   (lambda name:
    ...     (lambda *xAUTO0_:xAUTO0_)(
    ...       'builtins..print',
    ...       (lambda *xAUTO0_:xAUTO0_)(
    ...         'quote',
    ...         'Hello'),
    ...       name)))

    #> (greet 'Bob)
    >>> # greet
    ... __import__('builtins').print(
    ...   'Hello',
    ...   'Bob')
    Hello Bob

Using a symbol here is a bit sloppy.
If you really meant it to be text, rather than an identifier,
a double-quoted string might have been a better idea:

.. code-block:: Lissp

    #> (setattr _macro_ 'greet (lambda (name) `(print "Hello" ,name)))
    >>> setattr(
    ...   _macro_,
    ...   'greet',
    ...   (lambda name:
    ...     (lambda *xAUTO0_:xAUTO0_)(
    ...       'builtins..print',
    ...       ('quote', 'Hello', {':str': True}),
    ...       name)))

    #> (greet 'Bob)
    >>> # greet
    ... __import__('builtins').print(
    ...   'Hello',
    ...   'Bob')
    Hello Bob

While the ``{':str': True}`` means nothing to the compiler,
it does prevent the template reader macro from qualifying it like a symbol.

There's really no need to use a macro when a function will do.
The above are for illustrative purposes only.
But there are times when a function will not do:

.. code-block:: Lissp

    #> (setattr _macro_ '# (lambda (: :* body) `(lambda (,'#) (,@body))))
    >>> setattr(
    ...   _macro_,
    ...   'xHASH_',
    ...   (lambda *body:
    ...     (lambda *xAUTO0_:xAUTO0_)(
    ...       'lambda',
    ...       (lambda *xAUTO0_:xAUTO0_)(
    ...         'xHASH_'),
    ...       (lambda *xAUTO0_:xAUTO0_)(
    ...         *body))))

    #> (any (map (# print (.upper #) ":" #)
    #..          "abc"))
    >>> any(
    ...   map(
    ...     # xHASH_
    ...     (lambda xHASH_:
    ...       print(
    ...         xHASH_.upper(),
    ...         ':',
    ...         xHASH_)),
    ...     'abc'))
    A : a
    B : b
    C : c
    False

This macro is a metaprogram that creates a one-argument lambda.
This is an example of intentional capture.
The anaphor [#capture]_ is ``#``.
Try doing that in Python.
You can get pretty close with higher-order functions,
but you can't delay the evaluation of the `.upper()<str.upper>`
without a lambda,
which really negates the whole point of creating a shorter lambda.

One of the main uses of macros is delaying evaluation.
You can do that much with a lambda in Python.
But advanced macros can inject anaphors,
delay evaluation,
and do a find-and-replace on symbols in code all at once.
You have full programmatic control over the *code itself*,
with the full power of Python's ecosystem.

Compiling Packages
==================

It isn't always necessary to create a compiled file.
You can run a ``.lissp`` file directly as the main module using hissp::

    $ python -m hissp foo.lissp

Or::

    $ lissp foo.lissp

But you'll probably want to break a larger project up into smaller modules.
And those must be compiled for import.

The recommended way to compile a Lissp project is to put a call to
`transpile()` in the main module and in each ``__init__.py``—
with the name of each top-level ``.lissp`` file,
or ``.lissp`` file in the corresponding package,
respectively::

    from hissp.reader import transpile

    transpile(__package__, "spam", "eggs", "etc")

Or equivalently in Lissp, used either at the REPL or if the main module is written in Lissp:

.. code-block:: Lissp

    (hissp.reader..transpile __package__ 'spam 'eggs 'etc)

This will automatically compile each named Lissp module.
This approach gives you fine-grained control over what gets compiled when.
If desired, you can remove a name passed to the `transpile()`
call to stop recompiling that file.
Then you can compile the file manually at the REPL as needed using `transpile()`.

Note that you usually *would* want to recompile the whole project
rather than only the changed files on import like Python does for ``.pyc`` files,
because macros run at compile time.
Changing a macro in one file normally doesn't affect the code that uses
it in other files until they are recompiled.
That is why transpile will recompile the named files unconditionally.
Even if the corresponding source has not changed,
the compiled output may be different due to an updated macro in another file.

.. rubric:: Footnotes

.. [#EOF] End Of File. Usually Ctrl-D, but enter Ctrl-Z on Windows.
          This doesn't quit Python if the REPL was launched from Python,
          unlike ``(exit)``.

.. [#meta] Data about data.

.. [#key] The equivalent concept is called a *keyword* in other Lisps,
          but that means something else in Python.

.. [#capture] When symbol capture is done on purpose, these are known as *anaphoric macros*.
   (When it's done on accident, these are known as *bugs*.)
