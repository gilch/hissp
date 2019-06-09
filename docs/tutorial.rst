.. Copyright 2019 Matthew Egan Odendahl
   SPDX-License-Identifier: Apache-2.0

..  Hidden doctest requires basic macros for REPL-consistent behavior.
    #> (operator..setitem (globals) '_macro_ (types..SimpleNamespace : :** (vars hissp.basic.._macro_)))
    #..
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
  An type of intermediate tree data structure used by most compilers
  after parsing a programming language.

You've been writing AST all along, albeit indirectly.
To understand code at all, in any programming language,
you must have an understanding of how to *parse* it, mentally.
At least on an intuitive, subconscious level.

Python itself has an AST representation used by its compiler
which is accessible to Python programs.
(See the :py:module`ast` module.)
but, because it represents all of the possible Python syntax,
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

The ``readerless()`` function takes a Hissp program as input,
and returns its Python translation as a string.

Let's break this down.

Notice that the first element of each tuple designates its function.
In the case of ``('print',('quote','Hello'),'name',)``,
it's just representing an ordinary function call.
The remaining elements are the arguments.

The interpretation of the ``lambda`` form is different.
It represents a lambda expression, rather than a function call.
``('name',)`` is its parameters tuple.
The remainder is its body.

Note that ``'name'`` was used as an identifier,
but the ``('quote','Hello')`` expression was translated to a string.
That's the interpretation of ``quote``:
its argument is seen as "data" rather than code by the compiler.

Together ``lambda`` and ``quote`` are the only "special forms"
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
We just wrote code that writes code. That wasn't so bad, right?
It output Hissp code, which changes based on an input.

And, in fact, this ``q`` function takes the place of a "reader macro",
which I'll explain shortly.

Let's use it.

>>> readerless(
...     ('lambda',('name'),
...      ('print',q('Hello'),'name',),)
... )
"(lambda n,a,m,e:\n  print(\n    'Hello',\n    name))"
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
   it is the *comma* that creates a tuple. *Not* the parentheses!
   The parentheses just control evaluation order.
   There are some contexts where tuples don't require parentheses at all.

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

Hissp comes with a `hissp.reader` module that interprets a lightweight
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

>>> from hissp.reader import Parser
>>> next(Parser().reads("""
... (lambda (name)
...   (print 'Hello name))
... """))
('lambda', ('name',), ('print', ('quote', 'Hello'), 'name'))

There are no commas to miss, because there are no commas at all.
Much easier, yes?

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

You can launch the REPL from Python code (which is useful for debugging),
But let's just start it from the command line::

    $ python -m hissp

You should see the Lissp prompt ``#>`` appear.

The basic REPL shows the Python translation of the read Lissp
and evaluates it.

Literals
--------

Most literals work just like Python::

    #> 1 ; Lissp comments use ';' instead of '#'.
    >>> (1)
    1

    #> ;; Use two ';'s if it starts the line.
    #..-1.0
    #..
    >>> (-1.0)
    -1.0

    #> 1e10
    >>> (10000000000.0)
    10000000000.0

    #> 2+3j  ; complex
    >>> ((2+3j))
    (2+3j)

    #> True
    >>> True
    True

    #> None
    >>> None

Comments, as one might expect, are ignored by the reader,
and do not appear in the Hissp output.

Strings
#######

Double-quoted strings may contain newlines,
but otherwise behave as Python's and respect the same escape codes::

    #> "Three
    #..lines\ntotal"
    #..
    >>> 'Three\nlines\ntotal'
    'Three\nlines\ntotal'

There are no triple double-quoted strings in Lissp.

Strings are implicitly quoted::

    #> (quote
    #.. (lambda (name)
    #..  (print "Hello" name)))
    #..
    >>> ('lambda', ('name',), ('print', ('quote', 'Hello'), 'name'))
    ('lambda', ('name',), ('print', ('quote', 'Hello'), 'name'))



Symbols
#######

In our basic example::

    (lambda (name)
     (print 'Hello name))

``lambda``, ``name``, ``print``, ``Hello``, and
``name`` are read as *symbols*.

Symbols should be used for *identifiers* (variable names and the like).

The distinction between a quoted symbol and a double-quoted string
exists only in Lissp a the reader level.
It's two ways of writing the same thing in Hissp
Recall that the argument of the ``quote`` special form is seen as data::

    #> (quote
    #.. (lambda (name)
    #..  (print 'Hello name)))
    #..
    >>> ('lambda', ('name',), ('print', ('quote', 'Hello'), 'name'))
    ('lambda', ('name',), ('print', ('quote', 'Hello'), 'name'))

This shows us how that Lissp would get translated to Hissp.
Notice that symbols become strings in Hissp.

Munging
~~~~~~~

Symbols have another important difference from double-quoted strings::

    #> 'foo->bar?  ; xH_ stands for "Hyphen"
    >>> 'fooxH_xGT_barxQUERY_'
    'fooxH_xGT_barxQUERY_'

    #> "foo->bar?"
    #..
    >>> 'foo->bar?'
    'foo->bar?'

Symbols may contain symbol characters,
but the Python identifiers they represent cannot.
Therefore, the reader *munges* symbols with symbol characters into
valid identifier strings by using ``xQUOTEDxWORDS_``.

This format was chosen because it contains an underscore
and both lower-case and upper-case letters,
which makes it distinct from standard Python naming conventions:
``lower_case_with_underscores``, ``UPPER_CASE_WITH_UNDERSCORES``. and ``CapWords``.
This makes it easy to tell if an identifier contains munged characters,
which makes demunging possible in the normal case.
It also cannot introduce a leading underscore,
which can have special meaning in Python.

Key Symbols
~~~~~~~~~~~

Symbols that begin with a ``:`` are called *key symbols* [#key]_.
These are for when you want a symbol but it's not meant to be used as
an identifier. Thus, they do not get munged::

    #> :foo->bar?
    >>> ':foo->bar?'
    ':foo->bar?'

Nor do you have to quote them (usually), but you can::

    #> ':foo->bar?
    >>> ':foo->bar?'
    ':foo->bar?'


Qualified Symbols
~~~~~~~~~~~~~~~~~

You can refer to variables defined in any module by using a
qualified symbol::

    #> (operator..add 40 2)
    #..
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

lambda
######
The anonymous function special form::

    (lambda (<parameters>)
      <body>)

The parameters tuple is divided into ``(<single> : <paired>)``

Parameter types are the same as Python's.
For example::

    #> (lambda (a b  ; positional
    #..         : e 1  f 2  ; default
    #..         :* args  h 4  i :_  j 1  ; kwonly
    #..         :** kwargs)
    #..  42)
    #..
    >>> (lambda a,b,e=(1),f=(2),*args,h=(4),i,j=(1),**kwargs:(42))
    <function <lambda> at ...>

The special keywords ``:*`` and ``:**`` designate the remainder of the
positional and keyword parameters, respectively.
Note this body has multiple expressions::

    #> (lambda (: :* args :** kwargs)
    #..  (print args)
    #..  (print kwargs)  ; Body expressions evaluate in order.
    #..  :return-value)  ; The last one is returned.
    #..
    >>> (lambda *args,**kwargs:(
    ...   print(
    ...     args),
    ...   print(
    ...     kwargs),
    ...   ':return-value')[-1])
    <function <lambda> at ...>

    #> (_ 1 : b :c)  ; The ``_`` works in the Python shell too.
    #..
    >>> _(
    ...   (1),
    ...   b=':c')
    (1,)
    {'b': ':c'}
    ':return-value'

You can omit the right of a pair with ``:_``
(except the final ``**kwargs``).
Also note that the body can be empty::

    #> (lambda (: a 1 :* :_  b :_  c 2))
    #..
    >>> (lambda a=(1),*,b,c=(2):())
    <function <lambda> at ...>

The ``:`` may be omitted if there are no paired parameters::

    #> (lambda (a b c :))  ; No pairs after ':'.
    #..
    >>> (lambda a,b,c:())
    <function <lambda> at ...>

    #> (lambda (a b c))  ; The ':' was omitted.
    #..
    >>> (lambda a,b,c:())
    <function <lambda> at ...>

    #> (lambda (:))
    #..
    >>> (lambda :())
    <function <lambda> at ...>

    #> (lambda ())
    #..
    >>> (lambda :())
    <function <lambda> at ...>

The ``:`` is required if there are any paired parameters, even if
there are no single parameters::

    #> (lambda (: :** kwargs))
    #..
    >>> (lambda **kwargs:())
    <function <lambda> at ...>

calls
#####
  ! nil
    @ star stars single kwarg method

- literal
  ! comment
  ! string
    # symbol. (Quote macro again?)
    # key symbol
    # qualified symbol
    # double-quoted
  ! python literal
    # simple
- tuple
  ! nil
  ! lambda
    @ kwparam/kwonly
  ! call
    @ star stars single kwarg method
- reader_macro
  ! template
    @ unquote
    @ splice
  ! built-in
    @ gensym
    @ drop
    @ eval
  ! qualified tag
      # compound literals
- macro
  ! examples from basic macros


Structured Literals
###################

.. TODO explain?

::

    #> [1,2,3]
    >>> [1, 2, 3]
    [1, 2, 3]

    #> {'foo':2}
    >>> {'foo': 2}
    {'foo': 2}


.. Caution::
   Unlike Python's *displays*,
   spaces are **not** allowed in Lissp's literal data structures,
   nor are double quotes,
   because this causes them to be read as multiple forms.
   It's better to avoid them,
   but if you must have them in an inner string, use the escape codes ``\40``,
   or ``\42`` instead, respectively.

   Triple single-quoted strings may appear in literal data structures,
   but newlines are not allowed for the same reason. Use ``\n`` instead.

   Parentheses are reserved for Hissp forms and may not appear in
   literal data structures, even in nested strings
   (Use ``\50\51`` if you must).
   Literal data structures may not contain tuples.

Literal data structures can be very useful as inputs to

 * macros, especially reader macros, which can only take one argument,
 * and arrays, which contain only simple types.

.. Caution::
   Unlike Python, literal data structures may contain only static data
   discernible at read time. They are each read as a *single object*.
   If you want to interpolate runtime data, use function calls
   and templates instead::

        #> (list `(,@(.upper "abc") ,@[1,2,3] ,(.title "zed")))
        #..
        >>> list(
        ...   (lambda *xAUTO0_:xAUTO0_)(
        ...     *'abc'.upper(),
        ...     *[1, 2, 3],
        ...     'zed'.title()))
        ['A', 'B', 'C', 1, 2, 3, 'Zed']

   If this is still too verbose for your taste,
   remember you can use helper functions or metaprogramming to simplify::

        #> (define enlist
        #.. (lambda (: :* args)
        #..  (list args)))
        #..
        >>> # define
        ... __import__('operator').setitem(
        ...   __import__('builtins').globals(),
        ...   'enlist',
        ...   (lambda *args:
        ...     list(
        ...       args)))

        #> (enlist : :*(.upper "abc")  :_ [1,2,3]  :_ (.title "zed"))
        #..
        >>> enlist(
        ...   *'abc'.upper(),
        ...   [1, 2, 3],
        ...   'zed'.title())
        ['A', 'B', 'C', [1, 2, 3], 'Zed']

        #> (enlist 'A 'B 'C 1 2 3 (.title "zed"))
        #..
        >>> enlist(
        ...   'A',
        ...   'B',
        ...   'C',
        ...   (1),
        ...   (2),
        ...   (3),
        ...   'zed'.title())
        ['A', 'B', 'C', 1, 2, 3, 'Zed']


Only single-quoted or triple single-quoted strings are allowed
inside of literal data structures.
(And only double-quoted strings outside.)

Reader Macros
=============

Reader macros in Lissp consist of a symbol ending with a ``\``
followed by another form.
The function named by the symbol is invoked on the form,
and the reader embeds the resulting object into the output Hissp.

For example::

    #> builtins..float\inf
    >>> __import__('pickle').loads(  # inf
    ...     b'\x80\x03G\x7f\xf0\x00\x00\x00\x00\x00\x00.'
    ... )
    inf

This inserts an actual ``inf`` object at read time into the Hissp code.
Since this isn't a valid literal, it has to compile to a pickle.
You should normally try to avoid emitting pickles
(e.g. use ``(float 'inf)`` or ``math..inf`` instead),
but note that a macro would get the original object,
since the code hasn't been compiled yet, which may be useful.
While unpickling does have some overhead,
it may be worth it if constructing the object normally has even more.
Naturally, the object must be picklable to emit a pickle.

Unqualified reader macros are reserved for the basic Hissp reader.
There are currently three of them: `.\ `, `_\ `, and `#\ `.

If you need more than one argument for a reader macro, use the built in
`.\ ` macro, which evaluates a form at read time. For example,
```python
#> .\(fractions..Fraction 1 2)
#..
>>> __import__('pickle').loads(  # Fraction(1, 2)
...     b'\x80\x03cfractions\nFraction\nX\x03\x00\x00\x001/2\x85R.'
... )
Fraction(1, 2)

```

The `_\ ` macro omits the next form.
It's a way to comment out code,
even if it takes multiple lines.

Templates
---------

* ````` template quote
* `,` unquote
* `,@` splice unquote
* `'` quote

The final builtin reader macro ``#\`` creates a gensym based on the given symbol.
Within a template, the same gensym literal always makes the same
gensym::

    #> `(#\hiss #\hiss)
    #..
    >>> (lambda *xAUTO0_:xAUTO0_)(
    ...   '_hissxAUTO17_',
    ...   '_hissxAUTO17_')
    ('_hissxAUTO17_', '_hissxAUTO17_')

Macros
======

.. rubric:: Footnotes

.. [#key] The equivalent concept is called a *keyword* in other Lisps,
          but that means something else in Python.
