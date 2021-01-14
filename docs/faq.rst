.. Copyright 2019, 2020, 2021 Matthew Egan Odendahl
   SPDX-License-Identifier: CC-BY-SA-4.0

.. Hidden doctest requires basic macros for REPL-consistent behavior.
   #> (operator..setitem (globals) '_macro_ (types..SimpleNamespace : :** (vars hissp.basic.._macro_)))
   >>> __import__('operator').setitem(
   ...   globals(),
   ...   '_macro_',
   ...   __import__('types').SimpleNamespace(
   ...     **vars(
   ...       __import__('hissp.basic',fromlist='?')._macro_)))

.. TODO: Sphinx update messed up my sidebars! Is there a better fix?
.. raw:: html

   <style>pre, div[class|="highlight"] {clear: left;}</style>

FAQ
===
(Frequently Anticipated Questions (and complaints))

Anticipated? Didn't you mean "asked"?
-------------------------------------

Well, this project is still pretty new.

Why should I use Hissp?
-----------------------

   Any sufficiently complicated C or Fortran program contains an ad hoc,
   informally-specified, bug-ridden, slow implementation of half of Common Lisp.

   — Greenspun's Tenth Rule

If the only programming languages you've tried are those designed to feel familiar to C programmers,
you might think they're all the same. I assure you, they are not.

At some level you already know this.
Why not use assembly language for everything?
Or why not the binary machine code?

Because you want the highest-level language you can get your hands on.
Lisp has few rivals, but many dialects, Hissp among them.

You want access to the Python ecosystem.
Python has had slow and steady growth for decades,
and now it's a top industry language.
Its ecosystem is very mature and widely used.
And Hissp can use it and participate in it as easily as Python can,
because compiled Hissp *is Python*.

But, Python's is not the only mature ecosystem.
If you're attached to a different one,
perhaps Hissp is not the Lisp for you.

Is Hissp a replacement for Python?
----------------------------------

Hissp is a modular metaprogramming *supplement* to Python.

How much Python you replace is up to you:

* Use small amounts of readerless-mode Hissp directly in your Python code.
* Compile individual Lissp modules to Python and import them in your Python projects.
* Write your entire project in Lissp, including the main module, and launch it with ``lissp``.

This also works in reverse.

* Use small amounts of Python code directly in your Lissp code via the inject macro ``.#``.
* Import Python modules and objects with qualified identifiers.
* Write the main module in Python (or compile it) and launch it with ``python``.

While the Hissp language can do anything Python can,
Hissp is compiled to Python,
so it requires Python to work.

You must be able to read Python code to understand the output of the Lissp REPL,
which shows the Python compilation, the normal Python reprs for objects,
and the same kind of tracebacks and error messages Python would.

Can Hissp really do anything Python can when it only compiles to a subset of it?
--------------------------------------------------------------------------------

Yes.

Short proof: Hissp has strings and can call `exec()<exec>`.

But you usually won't need it because you can import anything written in
Python by using `qualified identifiers`.

Hissp macros and reader macros can return any type of object. If you
return a string the compiler will assume it's either a qualified identifier
or plain identifier (and emit it verbatim). But, the string *could*
contain almost arbitrary Python code instead. The compiler actually
checks for parentheses and spaces in strings, and if it finds any, it
will assume it's a Python injection and will avoid processing them like
symbols.

However, the main point of Hissp is syntactic macros. If you wanted to
do string metaprogramming you could have just used `exec()<exec>`, so you're
giving up a lot of Hissp's power. Expressions are relatively safe if
you're careful, but note that statements would only work at the top
level.

In principle, you never *need* to do this. It's dirty. It's risky. It's
worse than `eval()<eval>`/`exec()<exec>`, which are at least explicit about it.
Even if you think you need it, you still probably don't. But it can be
very useful as an optimization.

What's 1 + 1?
-------------

Two.

I mean how do you write it in Hissp without operators? Please don't say ``eval()``.
-----------------------------------------------------------------------------------

We have all the operators because we have all the standard library
functions.

.. code-block:: Lissp

   (operator..add 1 1)

That's really verbose though.
-----------------------------

Hmm, is this better?
Top-level imports are a good use of inject.

.. sidebar:: Star imports are generally bad, but

   I daresay ``from operator import *`` would be even less verbose.
   This has the effect of making the origin of many identifiers mysterious.
   Because it dumps the entire contents into globals,
   they almost act like builtins.
   It increases the chances of name collisions,
   which can also cause weird behavior when you re-order imports.
   Like builtins, you really need to be familiar with the whole module,
   not just the parts you are using.
   Star imports are usually not worth it.
   But sometimes they are.
   The `operator` module *is* a good candidate for it.
   Also consider `itertools`.
   Use responsibly.

.. code-block:: REPL

   #> .#"import operator as op"
   >>> import operator as op

   #> (op.add 1 1)
   >>> op.add(
   ...   (1),
   ...   (1))
   2

The result is a bit less desirable in templates.
But it's not technically wrong.

.. code-block:: REPL

   #> `op.add
   >>> '__main__..op.add'
   '__main__..op.add'

And you can still qualify it yourself instead of letting the reader do it for you:

.. code-block:: REPL

   #> `operator..add
   >>> 'operator..add'
   'operator..add'

Yeah, that's better, but in Python, it's just ``+``.
----------------------------------------------------

You can, of course, abbreviate these.

.. code-block:: REPL

   #> (define + operator..add)
   >>> # define
   ... __import__('operator').setitem(
   ...   __import__('builtins').globals(),
   ...   'xPLUS_',
   ...   __import__('operator').add)

   #> (+ 1 1)
   >>> xPLUS_(
   ...   (1),
   ...   (1))
   2

Yes, ``+`` is a valid symbol. It gets munged to ``xPLUS_``. The result
is all of the operators you might want, using the same prefix notation
used by all the calls.

You can even upgrade these to use a reduce so they're multiary like other Lisps:

.. code-block:: REPL

   #> (define +
   #..  (lambda (: :* args)
   #..    (functools..reduce operator..add args)))
   >>> # define
   ... __import__('operator').setitem(
   ...   __import__('builtins').globals(),
   ...   'xPLUS_',
   ...   (lambda *args:
   ...     __import__('functools').reduce(
   ...       __import__('operator').add,
   ...       args)))

   #> (+ 1 2 3)
   >>> xPLUS_(
   ...   (1),
   ...   (2),
   ...   (3))
   6

You mean I have to do this one by one for each operator every time?
-------------------------------------------------------------------

Write it once,
then you just import it.
That's called a "library".
And no, you don't copy/paste the implementation.
That would violate the DRY principle.
Implement it once and map the names.

Why isn't that in the Hissp library already?
--------------------------------------------

It **is** in the library already!
It's called `operator`.

Hissp is a modular system.
Hissp's output is *guaranteed* to have no dependencies you don't introduce yourself.
That means Hissp's standard library *is Python's*.
All I can add to that without breaking that rule is some basic macros that have no dependencies
in their expansions,
which is arguably not the right way to write macros.
So I really don't want that collection to get bloated.
But I needed a minimal set to test and demonstrate Hissp.
A larger application with better alternatives should probably not be using the basic macros at all.

If you don't like Python's version,
then add a dependency to something else.
If some open-source Hissp libraries pop up,
I'd be happy to recommend the good ones in Hissp's documentation,
but they will remain separate packages.

I want infix notation!
----------------------

Hissp is a Lisp. It's all calls! Get used to it.

Fully parenthesized prefix notation is explicit and consistent. It's
very readable if properly indented. Don't confuse "easy" with
"familiar". Also, you don't have to be restricted to one or two
arguments.

...
---

Fine. You can write macros for any syntax you please.

Also consider using Hebigo_, which keeps all Python expressions, instead
of Lissp.

Also recall that both reader and compiler macros can return arbitrary
Python snippets and the compiler will emit them verbatim if it contains
a space or parentheses. You should generally avoid doing this, because
then you're metaprogramming with strings instead of AST. You're giving
up a lot of Hissp's power. But optimizing complex formulas is maybe one
of the few times it's OK to do that.

Recall the inject ``.#`` reader macro executes a form and embeds its result
into the Hissp.

.. code-block:: REPL

   #> (define quadratic
   #.. (lambda (a b c)
   #..   .#"(-b + (b**2 - 4*a*c)**0.5)/(2*a)"))
   >>> # define
   ... __import__('operator').setitem(
   ...   __import__('builtins').globals(),
   ...   'quadratic',
   ...   (lambda a,b,c:(-b + (b**2 - 4*a*c)**0.5)/(2*a)))

But for a top-level `define` like this, you could have just used
`exec()<exec>`.

How do I make bytes objects in Lissp?
-------------------------------------

.. code-block:: REPL

   #> (bytes '(1 2 3))
   >>> bytes(
   ...   (1, 2, 3))
   b'\x01\x02\x03'

Or, if you prefer hexadecimal,

.. code-block:: REPL

   #> (bytes.fromhex "010203")
   >>> bytes.fromhex(
   ...   ('010203'))
   b'\x01\x02\x03'

But that's just numbers. I want ASCII text.
-------------------------------------------

You do know about the `str.encode` method, don't you?

There's really no bytes literal in Lissp?
-----------------------------------------

Technically? No.

However, they do work in Python injections:

.. code-block:: REPL

   #> [b'bytes',b'in',b'collection',b'atoms']
   >>> [b'bytes', b'in', b'collection', b'atoms']
   [b'bytes', b'in', b'collection', b'atoms']

   #> .#"b'injected bytes literal'"
   >>> b'injected bytes literal'
   b'injected bytes literal'

And, if you have the basic macros loaded,
you can use the `b# <bxHASH_>` reader macro.

.. code-block:: REPL

   #> b#"bytes from reader macro"
   >>> b'bytes from reader macro'
   b'bytes from reader macro'

Bytes literals can be implemented fairly easily in terms of a raw string and reader macro.
That's close enough, right?

Why aren't any escape sequences working in Lissp strings?
---------------------------------------------------------

Lissp's strings are raw by default.
Lissp doesn't force you into any particular set of escapes.
Some kinds of metaprogramming are easier if you don't have to fight Python.
You're free to implement your own.

I like Python's, thanks. That sounds like too much work!
--------------------------------------------------------

Python's are still available in injections:

.. code-block:: REPL

   #> .#"'\u263a'"
   >>> '\u263a'
   '☺'

Or use the escape-string read syntax for short:

.. code-block:: REPL

   #> #"\u263a"
   >>> ('☺')
   '☺'

Wait, hash strings take escapes? Why are raw strings the default? In Clojure it's the other way around.
-------------------------------------------------------------------------------------------------------

Then we'd have to write byte strings like ``b##"spam"``.
Python has various other prefixes for string types.
Raw, bytes, format, unicode, and various combinations of these.
Reader macros let us handle these in a unified way in Lissp and create more as needed,
such as regex patterns, among many other types that can be initialized with a single string,
and that makes raw strings the most sensible default.
With a supporting reader macro all of these are practically literals.
It's easy to process escapes in reader macros.
It isn't easy to unprocess them.
Not to mention Python code injections,
which can contain their own strings with escapes.

Clojure's hash strings are already regexes, not raws,
and their reader macros aren't so easy to use,
so it doesn't come up as much.

This was not an easy decision.
Despite all of the above,
Python string escapes are used quite often.

Why can't I make a backslash character string?
----------------------------------------------

You can.

.. code-block:: REPL

   #> (len #"\\")
   >>> len(
   ...   ('\\'))
   1

The Lissp tokenizer assumes backslashes are paired in strings,
so you can't do it with a raw string:

.. code-block:: REPL

   #> (len "\\")
   >>> len(
   ...   ('\\\\'))
   2

   #> "\"
   #..\\"
   >>> ('\\"\n\\\\')
   '\\"\n\\\\'

Python makes the same assumption, even for raw strings.
So raw strings in Python have the same limitation.

How do I start the REPL again?
------------------------------

If you installed the distribution using pip, you can use the provided
``lissp`` console script.

::

   $ lissp

You can also launch the Hissp package directly using an appropriate
Python interpreter from the command line

::

   $ python3 -m hissp

There's no ``macroexpand``. How do I look at expansions?
------------------------------------------------------------

Invoke the macro indirectly somehow so the compiler sees it as a normal function,
and pass all arguments quoted.

.. code-block:: Lissp

   ((getattr hissp.basic.._macro_ "define") 'foo '"bar")

One could, of course, write a function or macro to automate this.

You can also use the method call syntax for this purpose, which is never
interpreted as a macro invocation. This syntax isn't restricted solely
to methods on objects. Due to certain regularities in Python syntax, it
also works on callable attributes in any kind of namespace.

.. code-block:: Lissp

   (.define hissp.basic.._macro_ : :* '(foo "bar"))

But you can also just look at the compiled Python output. It's indented,
so it's not that hard to read. The compiler also helpfully includes a
comment in the compiled output whenever it expands a macro.

There's no ``for``? What about loops?
-------------------------------------

Sometimes recursion is good enough. Try it. `list()<list>`, `map()<map>` and
`filter()<filter>` plus lambda can do anything list comprehensions can. Ditch
the `list()<list>` for lazy generators. Replace `list()<list>` with `set()<set>`
for set comprehensions. Dict comprehensions are a little trickier. Use
`dict()<dict>` on an iterable of pairs. `zip()<zip>` is an easy way to make
them, or just have the map's lambda return pairs. Remember, you can make
data tuples with template quotes.

This is so much harder than comprehensions!
-------------------------------------------

Not really. But you can always write a macro if you want different
syntax. You can pretty easily implement comprehensions this way.

That's comprehensions, but what about ``for`` statements? You don't really think I should build a list just to throw it away?
-----------------------------------------------------------------------------------------------------------------------------

Side effects are not good functional style. Avoid them for as long as
possible. Still, you do need them eventually if you want your program to
do anything.

Use `any()<any>` for side-effects to avoid building a list. Usually, you'd
combine with `map()<map>`, just like the comprehensions. Make sure the
lambda returns ``None``\ s (or something false), because a true value
acts like ``break`` in `any()<any>`. Obviously, you can use this to your
advantage if you *want* a break, which seems to happen pretty often when
writing imperative loops.

If you like, there's a `hissp.basic.._macro_.any-for<anyxH_for>` that basically does this.

See also `itertools`, `iter`.

There's no ``if`` statement. Branching is fundamental!
------------------------------------------------------

No, it's *really* not.
(I saw a working C compiler that only output mov instructions.)
You already learned how to ``for`` loop above. Isn't
looping zero or one times like skipping a branch or not? Note that
``False`` and ``True`` are special cases of ``0`` and ``1`` in Python.
``range(False)`` would loop zero times, but ``range(True)`` loops one
time.

See also `hissp.basic._macro_.when`.

What about if/else ternary expressions?
---------------------------------------

.. code-block:: python

   (lambda b, *then_else: then_else[not b]())(
       1 < 2,
       lambda: print('yes'),
       lambda: print('no'),
   )

There's a `hissp.basic.._macro_.if-else<ifxH_else>` macro that basically expands
to this. I know it's a special form in other Lisps (or ``cond`` is), but
Hissp doesn't need it. Smalltalk pretty much does it this way. Once you
have ``if`` you can make a ``cond``. Lisps actually differ on which is
the special form and which is the macro.

You have to define three lambdas just for an ``if``?! isn't this really slow? It really ought to be a special form.
-------------------------------------------------------------------------------------------------------------------

It's not *that* slow. Like most things, performance is really only an
issue in a bottleneck. If you find one, there's no runtime overhead for
using ``.#`` to inject some Python.

Also recall that macros are allowed to return strings of Python code.
All the usual caveats for text-substitution macros apply. Use
parentheses.

.. code-block:: Lissp

   (defmacro !if (test then otherwise)
     "Compiles to if/else expression."
     (.format "(({}) if ({}) else ({}))"
              : :* (map hissp.compiler..readerless
                        `(,then ,test ,otherwise))))

Take it from Knuth:
Premature optimization is the root of all evil (or at least most of it) in programming.

Don't use text macros unless
you really need them. Even if you think you need one, you probably
don't.

Syntactic macros are powerful not just because they can delay
evaluation, but because they can read and re-write code. Using a text
macro like the above can hide information that a syntactic rewriting
macro needs to work properly.

Is Hissp a Scheme, Common Lisp, or Clojure implementation?
----------------------------------------------------------

No, but if you're comfortable with any Lisp,
Lissp will feel familiar.

Of these, ClojureScript may be the most similar,
in that it transpiles to another high-level language.
But unlike JavaScript,
Python already comes with batteries included.
Hissp doesn't include a standard library.
Because Python already provides so much,
in many ways Hissp can be even more minimal than Scheme.

Hissp draws inspiration from previous Lisps,
including Scheme, Common Lisp, ClojureScript, Emacs Lisp, Arc, and Hy.

Does Hissp have tail-call optimization?
---------------------------------------

No, because CPython doesn't. If a Python implementation has it, Hissp
will too, when run on that implementation.

Isn't that required for Lisp?
-----------------------------

No, you're thinking Scheme.
The Common Lisp standard does not require TCO
(though many popular implementations have it).
Clojure and ClojureScript don't have it either.

You can increase the recursion limit with `sys.setrecursionlimit`.
Better not increase it too much if you don't like segfaults, but you can
trampoline instead. See Drython_'s ``loop()`` function. Or use it. Or
Hebigo_'s equivalent macro. Clojure does it about the same way.

Where's ``cons``? How do you add links to your lists?
-----------------------------------------------------

We don't have one.
Hissp code is not actually made of linked lists.
It uses Python tuples,
which are backed by arrays.

You can splice ``,@`` into a template though.
It should not be hard to implement if you really need it.

Heresy! It's not Lisp without list processing!
----------------------------------------------

Clojure uses vectors in its forms and I still call it a Lisp.
Python is quite capable of processing tuples.
Readerless mode also looks pretty lispy.
Creating a linked list type or cons cell would have complicated things too much.

Do you have those immutable persistent data structures like Clojure?
--------------------------------------------------------------------

No, but tuples are immutable in Python.
(Although their elements need not be.)

If you want those,
check out `Pyrsistent <https://pypi.org/project/pyrsistent/>`_
and `Immutables <https://pypi.org/project/immutables/>`_.

How do I make a tuple?
----------------------

Use `tuple()`.

But I have to already have an iterable, which is why I wanted a tuple in the first place!
-----------------------------------------------------------------------------------------

.. code-block:: Python

   lambda *a: a

You can also make an empty list with ``[]`` or ``(list)``, and then
``.append`` to it. (Try the `cascade` macro.) Finally, the template
syntax :literal:`\`()` makes tuples. Unquote ``,`` calls/symbols if
needed.

There are no statements?! How can you get anything done?
--------------------------------------------------------

There are expression statements only (each top-level form). That's
plenty.

But there's no assignment statement!
------------------------------------

That's not a question.

For any complaint of the form "Hissp doesn't have feature X", the answer
is usually "Write a macro to implement X."

Use the `hissp.basic.._macro_.define<define>` and `hissp.basic.._macro_.let<let>`
macros for globals and locals, respectively. Look at their expansions
and you'll see they don't use assignment statements either.

See also `setattr` and `operator.setitem`.

Also, Python 3.8 added assignment expressions. Those are expressions. A
macro could expand to a string containing the walrus ``:=``,
but as with text-substitution macros generally,
this approach is not recommended.

How do I reassign a local?
--------------------------

You don't. `let` is single-assignment.
This is also true for ``let`` in Scheme and Clojure.

But Scheme has ``set!`` and Clojure has atoms.
----------------------------------------------

And Python has `dict` and `types.SimpleNamespace`.

(The walrus ``:=`` also works in an injection,
but this use is discouraged in Hissp.)

Where's the ``letrec``/``letfn``?
---------------------------------

Use methods in a class. You can get the other methods from the ``self`` argument.

How do I make a class?
----------------------

Use `type()<type>`. (Or whatever metaclass.)

Very funny. That just tells me what type something is.
------------------------------------------------------

No, seriously, you have to give it all three arguments. Look it up.

Well now I need a dict!
-----------------------

Use `dict()<dict>`. Obviously. You don't even need to make pairs if the keys
are identifiers. Just use kwargs.

That seems too verbose. In Python it's easier.
----------------------------------------------

You mostly don't need classes though. Classes conflate data structures
with the functions that act on them, and tend to encourage fragmented
mutable state which doesn't scale well. They're most useful for their
magic methods to overload operators and such. But Hissp mostly doesn't
need that since it has no operators to speak of.

If you just need `single dispatch<functools.singledispatch>`,
Python's already got you covered,
no classes necessary.

As always, you can write a function or macro to reduce boilerplate.
There's actually a `hissp.basic.._macro_.deftype<deftype>` macro for making a
top-level type.

I've got some weird metaclass magic from a library. ``type()`` isn't working!
-----------------------------------------------------------------------------

Try `types.new_class` instead.

How do I raise exceptions?
--------------------------

``(operator..truediv 1 0)`` seems to work. Exceptions tend to raise
themselves if you're not careful.

But I need a raise statement for a specific exception message.
--------------------------------------------------------------

Exceptions are not good functional style. Haskell uses the Maybe monad
instead, so you don't need them. If you must, you can still use a
``raise`` in `exec()<exec>`. (Or use Drython_'s ``Raise()``, or Hebigo_'s
equivalent macro.)

If you want a Maybe in Python,
`returns <https://pypi.org/project/returns/>`_
has them.
But should you use them?
`Maybe not. <https://www.youtube.com/watch?v=YR5WdGrpoug>`_

Use exec? Isn't that slow?
--------------------------

If the exceptions are only for exceptional cases, then does it matter?
Premature optimization is the root of all evil.

What about catching them?
-------------------------

Try not raising them in the first place? Or `contextlib.suppress`.

But there's no ``with`` statement either!
-----------------------------------------

Use `contextlib.ContextDecorator` as a mixin and any context manager
works as a decorator. Or use Drython_'s ``With()``.

How do I use a decorator?
-------------------------

You apply it to the function (or class): call it with the function as
its argument. Decorators are just higher-order functions.

Any context manager? But you don't get the return value of ``__enter__()``! And what if it's not re-entrant?
------------------------------------------------------------------------------------------------------------

`suppress<contextlib.suppress>` works with these restrictions, but point taken. You can
certainly call ``.__enter__()`` yourself, but you have to call
``.__exit__()`` too. Even if there was an exception.

But I need to handle the exception if and only if it was raised, for multiple exception types, or I need to get the exception object.
-------------------------------------------------------------------------------------------------------------------------------------

Context managers can do all of that!

.. code-block:: python

   from contextlib import ContextDecorator

   class Except(ContextDecorator):
       def __init__(self, catch, handler):
           self.catch = catch
           self.handler = handler
       def __enter__(self):
           pass
       def __exit__(self, exc_type, exception, traceback):
           if isinstance(exception, self.catch):
               self.handler(exception)
               return True

   @Except((TypeError, ValueError), lambda e: print(e))
   @Except(ZeroDivisionError, lambda e: print('oops'))
   def bad_idea(x):
       return 1/x

   bad_idea(0)  # oops
   bad_idea('spam')  # unsupported operand type(s) for /: 'int' and 'str'
   bad_idea(1)  # 1.0

You can translate all of that to Hissp.

How?
----

Like this

.. code-block:: Lissp

   (deftype Except (contextlib..ContextDecorator)
     __init__
     (lambda (self catch handler)
       (attach self catch handler)
       None)
     __enter__
     (lambda (self))
     __exit__
     (lambda (self exc_type exception traceback)
       (when (isinstance exception self.catch)
         (.handler self exception)
         True)))

   (define bad_idea
     (-> (lambda (x)
           (operator..truediv 1 x))
         ((Except ZeroDivisionError
                  (lambda (e)
                    (print "oops"))))
         ((Except `(,TypeError ,ValueError)
                  (lambda (e)
                    (print e))))))

   (bad_idea 0) ; oops
   (bad_idea "spam") ; unsupported operand type(s) for /: 'int' and 'str'
   (bad_idea 1) ; 1.0

That is *so* much harder than a ``try`` statement.
--------------------------------------------------

The definition of the context manager is, sure. but it's not THAT hard.
And you only have to do that part once. Using the decorator once you
have it is really not that bad.

Or, to make things easy, use `exec()<exec>` to compile a ``try`` with
callbacks.

Isn't this slow?! You can't get away with calling this an "exceptional case" this time. The happy path would still require compiling an exec() string!
------------------------------------------------------------------------------------------------------------------------------------------------------

Not if you define it as a function in advance. Then it only happens once
on module import. Something like,

.. code-block:: Lissp

   (exec "
   def try_statement(block, target, handler):
       try:
           block()
       except target as ex:
           handler(ex)")

Once on import is honestly not bad. Even the standard library does it,
like for `named tuples <collections.namedtuple>`.
But at this point, unless you really want a
single-file script with no dependencies, you're better off defining the
helper function in Python and importing it. You could handle the
finally/else blocks similarly. See Drython_'s ``Try()`` for how to do it.
Or just use Drython. Hebigo_ also implements one. If Hebigo is installed,
you can import and use Hebigo's macros, even in Lissp, because they also
take and return Hissp.

Isn't Hissp slower than Python? Isn't Python slow enough already?
-----------------------------------------------------------------

"Slow" usually only matters if it's in a bottleneck. Hissp will often be
slower than Python because it compiles to a functional subset of Python
that relies on defining and calling functions more. Because Python is a
multiparadigm language, it is not fully optimized for the functional
style, though some implementations may do better than CPython here.

Premature optimization is the root of all evil. As always don't fix it until
it matters, then profile to find the bottleneck and fix only that part.
You can always re-write that part in Python (or C).

Yield?
------

We've got `itertools`. Compose iterators functional-style. You don't need
``yield``.

.. TODO: fill in reasoning more.
   Lazy cons is preferable to mutable iterators.
   Yield requires yield-from,
   (The "What Color Is Your Function?" problem.)
   which is inelegant compared to alternatives of similar or greater expressive power.
   such as call/cc and ?/reset.
.. TODO: implement yield macro? Will require pre-expansion like Hy's let.
   fortunately, Hissp has only two special forms (by design) so this should be easier.
   Think about code walking and alternatives.

But I need it for co-routines. Or async/await stuff. How do I accept a send?
----------------------------------------------------------------------------

`What color is your function? <https://journal.stuffwithstuff.com/2015/02/01/what-color-is-your-function/>`_
Async was probably a mistake.

Still, we want Python compatibility, don't we?

Make a `collections.abc.Generator` subclass with a ``send()`` method.

Or use Drython_'s ``Yield()``.

Generator-based coroutines have been deprecated. Don't implement them
with generators anymore. Note there are `collections.abc.Awaitable`
and `collections.abc.Coroutine` abstract base classes too.

How do I add a docstring to a module/class/function?
----------------------------------------------------

Assign a string to the ``__doc__`` attribute of the class or function
object. That key in the dict argument to `type()<type>` also works. For a
module, ``__doc__`` works (make a ``__doc__`` global) but you should
just use a string at the top, same as Python.

The REPL is nice and all, but how do I run a ``.lissp`` module?
---------------------------------------------------------------

You can launch a ``.lissp`` file as the main module directly.

If you have the entry point script installed that's:

.. code-block:: shell

   $ lissp foo.lissp

To be able to import a ``.lissp`` module, you must compile it to Python
first.

At the REPL (or main module if it's written in Lissp) use:

.. code-block:: Lissp

   (hissp.reader..transpile __package__ 'spam 'eggs 'etc)

Where spam, eggs, etc. are the module names you want compiled. (If the
package argument is ``None`` or ``''``, it will use the current working
directory.)

Or equivalently, in Python:

.. code-block:: python

   from hissp.reader import transpile

   transpile(__package__, "sausage", "bacon")

Consider putting the above in each package's ``__init__.py`` to
auto-compile each Hissp module in the package on package import during
development. You can disable it again on release, if desired, but this
gives you fine-grained control over what gets compiled when. Note that
you usually would want to recompile the whole project rather than only
the changed files like Python does, because macros run at compile time.
Changing a macro in one file normally doesn't affect the code that uses
it in other files until they are recompiled.

See `transpile`.

How do I import things?
-----------------------

Just use a `qualified identifier <qualified identifiers>`. You don't need imports.

But it's in a deeply nested package with a long name. It's tedious!
-------------------------------------------------------------------

So assign a global to it:
.. Lissp::

   #> (define Generator collections.abc..Generator)
   >>> # define
   ... __import__('operator').setitem(
   ...   __import__('builtins').globals(),
   ...   'Generator',
   ...   __import__('collections.abc',fromlist='?').Generator)

But be aware of the effects that has on qualification in templates.

But I need the module object itself! The package ``__init__.py`` doesn't import it or it's not in a package.
------------------------------------------------------------------------------------------------------------

A module literal will do it for you.

.. code-block:: REPL

   #> collections.abc.
   >>> __import__('collections.abc',fromlist='?')
   <module 'collections.abc' from '...abc.py'>

You can likewise assign a global, like any other value:

.. code-block:: Lissp

   (define np numpy.)
   (define pd pandas.)

But I want a relative import or a star import.
----------------------------------------------

`Qualified identifiers` have to use absolute imports to be reliable in macroexpansions.

But you can still import things the same way Python does.

- `importlib.import_module`
- `exec()<exec>` an ``import`` or a ``from`` ``import`` statement.
- The inject macro ``.#`` works on statements if it's at the top level.

How do I import a macro?
------------------------

The same way you import anything else: with a qualified identifier.
In Lissp, you can use a reader macro to abbreviate qualifiers.
`hissp.basic.._macro_.alias<hissp.basic._macro_.alias>` can define these for you.

Any callable in the current module's ``_macro_`` namespace will work unqualified.
Normally you create these with `hissp.basic.._macro_.defmacro<defmacro>`,
but the compiler doesn't care how they get there.

Importing the ``_macro_`` namespace from another module will work,
but then uses of `hissp.basic.._macro_.defmacro<defmacro>` will mutate
another module's ``_macro_`` namespace, which is probably not what you want,
so make a copy, or or make a new one and insert individual macros into it.

The basic macros have no dependencies on the Hissp package in their expansions,
which allows you to use their compiled output on another Python that doesn't have Hissp installed.
However, if you import a ``_macro_`` at runtime,
you're creating a runtime dependency on whatever module you import it from.

The `hissp.basic.._macro_.prelude<prelude>` macro will clone the basic macro namespace
only if available. It avoids creating a runtime dependency this way.

`hissp.basic.._macro_.prelude<prelude>` is a convenience for short scripts,
especially those used as the main module.
Larger projects should probably be more explicit in their imports,
and may need a more complete macro library anyway.

How do I write a macro?
-----------------------

Make a function that accepts the syntax you want as parameters and
returns its transformation as Hissp code (the template reader syntax
makes this easy). Put it in the ``_macro_`` namespace. There's a nice
`hissp.basic.._macro_.defmacro<defmacro>` to do this for you. It will even
create the namespace if it doesn't exist yet.

Some tips:

-  Hissp macros are very similar to Clojure or Common Lisp macros.

   -  Tutorals on writing macros in these languages are mostly
      applicable to Hissp.

-  Output qualified symbols so it works in other modules.

   -  The template reader syntax does this for you automatically.
   -  You have to do this yourself in readerless mode.
   -  You can interpolate an unqualified symbol into a template by
      unquoting it, same as any other value.

-  Use gensyms (``$#spam``) to avoid accidental capture of identifiers.

How do I define a reader macro?
-------------------------------

Make a function that accepts the syntax you want as its parameter and
returns its transformation as Hissp code.

You can use it directly as a qualified reader macro.
Or add it to the ``_macro_`` namespace to use it unqualified.

Remember `hissp.basic.._macro_.defmacro<defmacro>` can do this for you.

Why the weird prompts at the REPL?
----------------------------------

The REPL is designed so that you can copy/paste it into doctests or
Jupyter notebook cells running an IPython kernel and it should just
work. IPython will ignore the Lissp because its ``#>``/``#..`` prompts
makes it look like a Python comment, and it's already set up to ignore
the initial ``>>>``/``...``. But doctest expects these, because that's
what the Python shell looks like.

Keeping the Python prompts ``>>>``/``...``
also helps you to distinguish the compiled Python from the result of evaluating it.
The Lissp REPL could have been implemented to not display the Python at all,
but transparency into the process is super helpful when developing and debugging,
even if you ignore that part most of the time.

How do I add a shebang line?
----------------------------

Same as for any executable text file, use a line starting with ``#!``
followed by a command to run lissp. (E.g. ``/usr/bin/env lissp``) The
transpiler will ignore it if it's the first line. If you set the
executable bit, like ``chmod foo.lissp +x``, then you can run the file
directly.

I mean how do I add a shebang line to the compiled file?
--------------------------------------------------------

A text editor works. It's just a Python file.

I don't want to have to do that manually every time I recompile!
----------------------------------------------------------------

You can use the ``.#`` reader macro to inject arbitrary text in the
compiled output. Use e.g. ``.#"#/usr/bin/env python"`` as the first
compiled line.

I got here from a link in Hy's docs. What are the main differences between Hissp and Hy?
----------------------------------------------------------------------------------------

They're both Lisps that can import Python, but Hissp has a very different approach and philosophy.

I was also a major contributor to the open-source Hy project.
Hy is obviously a much older project than Hissp with more contributors and more time to develop.
While my experience with Hy informs my design of Hissp,
Hissp is not a fork of Hy's source code,
but a completely new project with a fundamentally different architecture.

The biggest difference is that Hy compiles to Python abstract syntax trees
(or "AST", an intermediate stage in the compilation of Python code to Python bytecode).
In contrast,
Lissp works more like ClojureScript:
the Lissp language uses Hissp as its AST stage instead,
and compiles *that* to Python code,
which Python then compiles normally.
Hy compiles to a moving target—Python's AST API is not stable.
This helps to make Hissp's compiler simpler than Hy's.

Hissp code is made of ordinary Python tuples that serve the same role as
linked lists in other Lisps,
or Hy's model objects.
Using these directly in Python
("readerless mode")
is much more natural than writing code using Hy's model objects,
although using the Lissp
(or Hebigo_)
language reader makes writing these tuples even easier than doing it directly in Python.

Hissp is designed to be more modular than Hy.
It supports two different readers
(Lissp and Hebigo)
with the potential for more.
These compile different languages that represent the same underlying Hissp-tuple AST.
The separate Hebigo language is indentation based,
while the included Lissp reader uses the traditional S-expressions.

Hy code requires the ``hy`` package as a dependency.
You need Hy's import hooks just to load Hy code.
But Hissp only requires ``hissp`` to compile the code.
Once that's done,
the output has no dependencies other than Python itself.
(Unless you import some other package, of course.)
This may make Hissp more suitable for integration into other projects
where Hy would not be a good fit due to its overhead.

Hy's compiler has a special form for every Python statement and operator
and has to do a lot of work to create the illusion that its statement
special forms behave like expressions.
This complicates the compiler a great deal,
and doesn't even work right in some cases,
but allows Hy to retain a very Python-like feel.
The `unparsed <ast.unparse>` AST also looks like pretty readable Python.
Not quite what a human would write,
but a good starting point if you wanted to translate a Hy project back to Python.

But after writing Drython_,
I realized that the expression subset of Python is sufficient for a compilation target.
There is no need to do the extra work to make statements act like
expressions if you only compile to expressions to begin with.
It turns out that Hissp only required two special forms: ``quote`` and ``lambda``.
(And you could almost implement lambda via a text macro.)
This makes Hissp's compiler *much* simpler than Hy's.
But the lack of statements makes it feel a bit more like Scheme and a bit less like Python.
And, of course, the expression-only output is completely unpythonic.

Another major difference is Hissp's qualified symbols.
This allows macros to easily import their requirements from other modules.
Macro dependencies are much harder to work with in Hy.

Is Hissp a Lisp-1 or a Lisp-2?
------------------------------

Hissp doesn't fit into your boxes.
Hissp variables are Python variables.
They're not implemented as cells in symbols.

Hissp can't have a function and variable with the same name at the same time in the local scope,
so if I had to pick one, I'd have to say it's *technically* a Lisp-1.

By this logic, Ruby is a Lisp-2 and Python is a Lisp-1
(although neither is a Lisp),
so Lisp-1 is the most natural fit for a Lisp based on Python.

Functional programming is more natural in a Lisp-1.
Lisp-2 tended to work better for macros in practice,
because it mostly prevents accidental name collisions between variables
and function names in macroexpansions.
But whatever advantages that had for macros were obsoleted by Clojure's syntax quote,
which qualifies symbols automatically and prevents such collisions even in a Lisp-1.
This solution is the best of both worlds.
Lissp's template quote qualifies symbols automatically,
like Clojure's syntax quote.

However, you can have a *macro* and a variable
(possibly a function) with the same name at the same time in the local scope in Hissp.
The macro will be used for direct invocations in the "invocation position"
(if it's the first element of the tuple),
and the variable will be used in the "variable position" (anywhere else).
If you want to use the macro itself as a variable
(and unlike functions, this is rare)
then you can qualify it with ``_macro_.``.
This behavior is very much like a Lisp-2.

This allows you do do things like write a macro that inlines a small function,
while still being able to pass a function object to higher-order functions
(like `map`) using the same unqualified name.
This behavior is similar to Hy, which uses this ability for its operators,
but is completely unlike Clojure.

And it does have a cost:
Unlike Clojure's syntax quote,
there are cases when the way Lissp's template quote should qualify a symbol is ambiguous.
The same symbol might refer to a builtin, a macro, and a global,
each of which would have to be qualified differently.
The template-quote qualification rules were designed to mostly just work,
but you may run into edge cases in Lissp that couldn't exist in Clojure.

If you wanted semantics more like a Lisp-2,
Lissp can do it pretty easily.
You could write a ``defun`` macro that
creates a function and put it in a
global `types.SimpleNamespace` named ``xHASH_xQUOTE_``.

Note that you can define macros that behave like functions:
maybe such a macro ``foo`` would rewrite an invocation like
``(foo bar baz)`` to ``(#'.foo bar baz)``.

If you want to import a Python function (instead of just using it qualified)
then put it in the ``#'`` namespace instead of in the globals
(you still need the associated macro).
You can even ``(define __builtins__ (dict : __import__ __import__))``
to hide all the builtins but `__import__` (which is required for qualified identifiers to work).

None of this is going to raise an error if you manage to get a function
variable in the invocation position that isn't already shadowed by a macro.
To fix that, you'd have to use a ``_macro_`` namespace object instancing
a class that overrides `object.__getattr__` to check the ``#'`` namespace for a name
and return the rewrite macro in that case, or raise an error otherwise.

.. TODO: Demonstrate in the macro tutorials and link here.

What version of Python is required?
-----------------------------------

The compiler itself currently requires Python 3.8+.
However, the *compiled output* targets such a small subset of Python
that Hissp would probably work on 3.0 if you're careful not to use unsupported features in lambda,
invocations, injections, or any parts of the standard library that didn't exist yet.
The output of Lissp's template syntax may require Python 3.5+ to work.

Qualified macros might still be able to use the 3.8+ features,
because they run at compile time,
as long as unsupported features don't appear in the compiled output.

Even more limited versions of Python (2.7?) might work with minor compiler modifications.

Is Hissp stable?
----------------

Almost.

This project is still pretty new.
Hissp is certainly usable in its current form,
though maybe some things could be nicer.

Hissp is currently *alpha-quality* software,
but is getting very close to beta.

Expect some breaking changes each release.
If you want to be an early adopter,
either pin the release version,
or keep up with the changes on the master branch as they come.

The Hissp language itself seems pretty settled,
but the implementation may change as the bugs are ironed out.
It was stable enough to prototype Hebigo_.

The basic macros are unstable.
The API may get reorganized.
Definitions may move to different modules or may change names.

There's probably no need to ever change the basic language, except
perhaps to keep up with Python, since the macro system makes it so
flexible. But Hissp is still unproven in any major project, so who
knows? The only way it will get proven is if some early adopter like you
tries it out and lets me know how it goes.

.. _Hebigo: https://github.com/gilch/hebigo
.. _Drython: https://github.com/gilch/drython