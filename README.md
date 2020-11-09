<!--
Copyright 2019, 2020 Matthew Egan Odendahl
SPDX-License-Identifier: Apache-2.0
-->
[![Gitter](https://badges.gitter.im/hissp-lang/community.svg)](https://gitter.im/hissp-lang/community?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge)
[![Documentation Status](https://readthedocs.org/projects/hissp/badge/?version=latest)](https://hissp.readthedocs.io/en/latest/?badge=latest)
[![codecov](https://codecov.io/gh/gilch/hissp/branch/master/graph/badge.svg)](https://codecov.io/gh/gilch/hissp)
<!-- Hidden doctest requires basic macros for REPL-consistent behavior.
#> (operator..setitem (globals) '_macro_ (types..SimpleNamespace : :** (vars hissp.basic.._macro_)))
#..
>>> __import__('operator').setitem(
...   globals(),
...   '_macro_',
...   __import__('types').SimpleNamespace(
...     **vars(
...       __import__('hissp.basic',fromlist='?')._macro_)))

-->
# Hissp

It's Python with a *Lissp*.

Hissp is a modular Lisp implementation that compiles to a functional subset of
Python&mdash;Syntactic macro metaprogramming with full access to the Python ecosystem.

<!-- markdown-toc start - Don't edit this section. Run M-x markdown-toc-refresh-toc -->
**Table of Contents**

- [Hissp](#hissp)
    - [Philosophy and Goals](#philosophy-and-goals)
        - [Radical Extensibility](#radical-extensibility)
        - [Minimal implementation](#minimal-implementation)
        - [Interoperability](#interoperability)
        - [Useful error messages](#useful-error-messages)
        - [Syntax compatible with Emacs' `lisp-mode` and Parlinter](#syntax-compatible-with-emacs-lisp-mode-and-parlinter)
        - [Standalone output](#standalone-output)
        - [REPL](#repl)
        - [Same-module macro helpers](#same-module-macro-helpers)
        - [Modularity](#modularity)
    - [Show me some Code!](#show-me-some-code)
    - [FAQ (Frequently Anticipated Questions (and complaints))](#faq-frequently-anticipated-questions-and-complaints)

<!-- markdown-toc end -->

## Philosophy and Goals

#### Radical Extensibility
Python is already a really nice language, so why do we need Hissp?

The answer is *metaprogramming*: code that writes code.
When you can shape the language itself to fit your problem domain,
the incomprehensible becomes obvious.

Python really is a great language to work with.
"Executable pseudocode" is not far off.
But it is too complex to be good at metaprogramming.
The use of `exec()` is frowned upon.
It's easy enough to understand, but hard to get right.
Python Abstract Syntax Tree (AST)
manipulation is a somewhat more reliable technique,
but not for the faint of heart.
Python AST is not simple, because Python isn't.

Hissp is a streamlined skin on Python:
a simplified AST that you can program in directly.
Hissp code is made of specially formatted tuples&mdash;easier
to manipulate than Python AST,
but still more reliable than text manipulation.
In Hissp, code is just another kind of data.

Lisp is renowned as the "programmable programming language",
extensible through its powerful macro system
which hooks into the compiler itself.
Macros are Lisp's secret weapon.
And Hissp brings their power to Python.

Adding features that historically required a new version of the Python language,
like `with` statements, are almost as easy as writing a new function in Lisp.

#### Minimal implementation
Hissp serves as a modular component for other projects.
The language and its implementation are meant to be small and comprehensible
by a single individual.

The Hissp compiler should include what it needs to achieve its goals,
but no more. Bloat is not allowed.
A goal of Hissp is to be as small as reasonably possible, but no smaller.
We're not code golfing here; readability still counts.
But this project has *limited scope*.
Hissp's powerful macro system means that additions to the compiler are
rarely needed.
Feature creep belongs in external libraries,
not in the compiler proper.

Hissp compiles to an unpythonic *functional subset* of Python.
This subset has a direct and easy-to-understand correspondence to the Hissp code,
which makes it straightforward to debug, once you understand Hissp.
But it is definitely not meant to be idiomatic Python.
That would require a much more complex compiler,
because idiomatic Python is not simple.

Hissp's basic macros are meant to be just enough to bootstrap native unit tests
and demonstrate the macro system.
They may suffice for small embedded Lissp projects,
but you will probably want a more comprehensive macro suite for general use.
[Hebigo](https://github.com/gilch/hebigo)
has macro equivalents of most Python statements.
The Hebigo project includes an alternative indentation-based Hissp reader,
but the macros are written in readerless mode and are also compatible with Lissp.

#### Interoperability
Why base a Lisp on Python when there are already lots of other Lisps?

Python has a rich selection of libraries for a variety of domains
and Hissp can mostly use them as easily as the standard library.
This gives Hissp a massive advantage over other Lisps with less selection.
If you don't care to work with the Python ecosystem,
perhaps Hissp is not the Lisp for you.

Note that the Hissp compiler is written in Python 3.8.
(Supporting older versions is not a goal,
because that would complicate the compiler.
This may limit the available libraries.)
But because the compiler's target functional Python subset is so small,
the compiled output can usually run on Python 3.5 without too much difficulty.
Watch out for positional-only arguments (new to 3.8)
and changes to the standard library.
Running on versions even older than 3.5 is not recommended,
but may likewise be possible (even for Python 2) if you carefully avoid using newer Python features.
(Keyword-only arguments, for example.)

Python code can also import and use packages written in Hissp,
because they compile to Python.

#### Useful error messages
One of Python's best features.
Any errors that prevent compilation should be easy to find.

#### Syntax compatible with Emacs' `lisp-mode` and Parlinter
A language is not very usable without tools.
Hissp's basic reader syntax (Lissp) should work with Emacs.

#### Standalone output
This is part of Hissp's commitment to modularity.

One can, of course, write Hissp code that depends on any Python library.
But the compiler does not depend on emitting calls out to any special
Hissp helper functions to work.
You do not need Hissp installed to run the final compiled Python output,
only Python itself.

Hissp includes some very basic Lisp macros to get you started.
Their expansions have no external requirements either.

Libraries built on Hissp need not have this limitation.

#### REPL
A Lisp tradition, and Hissp is no exception.
Even though it's a compiled language,
Hissp has an interactive shell like Python does.
The REPL displays the compiled Python and evaluates it.
Printed values use the normal Python reprs.
(Translating those to back to Lissp is not a goal.)

#### Same-module macro helpers
Not all Lisps support this, but Clojure is a notable exception.
Functions are generally preferable to macros when functions can do the job.
They're more reusable and composable.
Therefore it makes sense for macros to delegate to functions where possible.
But such a macro should work in the same module.
This requires incremental compilation and evaluation of forms, like the REPL.

#### Modularity
The Hissp language is made of tuples (and values), not text.
The basic reader included with the project just implements a convenient
way to write them.
It's possible to write Hissp in "readerless mode"
by writing these tuples in Python.

Batteries are not included because Python already has them.
Hissp's standard library is Python's.
There are only two special forms: ``quote`` and ``lambda``.
Hissp does include a few basic macros and reader macros,
just enough to write native unit tests,
but you are not obligated to use them when writing Hissp.

It's possible for an external project to provide an alternative
reader with different syntax, as long as the output is Hissp code (tuples).
One example of this is [Hebigo](https://github.com/gilch/hebigo),
which has a more Python-like indentation-based syntax.

Because Hissp produces standalone output, it's not locked into any one Lisp paradigm.
It could work with a Clojure-like, Scheme-like, or Common-Lisp-like, etc.,
reader, function, and macro libraries.

It is a goal of the project to support a more Clojure-like reader and
a complete function/macro library.
But while this informs the design of the compiler,
it will be an external project in another repository.

## Show me some Code!
Hissp is a language written as Python data and compiled to Python code:
```python
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
```
Hissp's utility as a metaprogramming language is the ease of manipulating simple data structures representing executable code.

Hissp can be written directly in Python using the "readerless mode" demonstrated above,
or it can be read in from a lightweight textual language called *Lissp* that represents these data structures.
```python
>>> from hissp.reader import Parser
>>> next(Parser().reads("""
... (lambda (name)
...   (print 'Hello name))
... """))
('lambda', ('name',), ('print', ('quote', 'Hello'), 'name'))
```
As you can see, this results in exactly the same Python data structure as the previous example,
and can by compiled to executable Python code the same way.

Hissp comes with a basic REPL (read-eval-print-loop, or interactive shell)
which compiles Hissp (read from Lissp) to Python and passes it to the Python REPL for execution.

Lissp can also be read from ``.lissp`` files.

The reader and compiler are both extensible with macros.

See the tutorial in the [![Documentation Status](https://readthedocs.org/projects/hissp/badge/?version=latest)](https://hissp.readthedocs.io/en/latest/?badge=latest)
for more details.


## FAQ (Frequently Anticipated Questions (and complaints))

> Anticipated? Didn't you mean "asked"?

Well, this project is still pretty new.

> Can Hissp really do anything Python can when it only compiles to a subset of it?

Yes.

Short proof: Hissp has strings and can call `exec()`.

But you usually won't need it because you can import anything written in Python
by using qualified symbols.

Hissp macros and reader macros can return any type of object.
If you return a string the compiler will assume it's either a qualified symbol
or plain identifier (and emit it verbatim).
But, the string *could* contain almost arbitrary Python code instead.
The compiler actually checks for parentheses and spaces in strings,
and if it finds any,
it will assume it's a Python injection and will avoid processing them like symbols.

However, the main point of Hissp is syntactic macros.
If you wanted to do string metaprogramming you could have just used `exec()`,
so you're giving up a lot of Hissp's power.
Expressions are relatively safe if you're careful,
but note that statements would only work at the top level.

In principle, you never *need* to do this.
It's dirty. It's risky.
It's worse than `eval()`/`exec()`, which are at least explicit about it.
Even if you think you need it, you still probably don't.
But it can be very useful as an optimization.

> What's 1 + 1?

Two.

> I mean how do you write it in Hissp without operators? Please don't say `eval()`.

We have all the operators because we have all the standard library functions.
```lisp
(operator..add 1 1)
```

> That's really verbose though.

You can, of course, abbreviate these.
```python
#> (define + operator..add)
#..
>>> # define
... __import__('operator').setitem(
...   __import__('builtins').globals(),
...   'xPLUS_',
...   __import__('operator').add)

#> (+ 1 1)
#..
>>> xPLUS_(
...   (1),
...   (1))
2

```
Yes, `+` is a valid symbol. It gets munged to `xPLUS_`.
The result is all of the operators you might want,
using the same prefix notation used by all the calls.

> I want infix notation!

Hissp is a Lisp. It's all calls! Get used to it.

Fully parenthesized prefix notation is explicit and consistent.
It's very readable if properly indented.
Don't confuse "easy" with "familiar".
Also, you don't have to be restricted to one or two arguments.

> ...

Fine. You can write macros for any syntax you please.

Also consider using Hebigo, which keeps all Python expressions, instead of Lissp.

Also recall that both reader and compiler macros can return arbitrary Python snippets
and the compiler will emit them verbatim if it contains a space or parentheses.
You should generally avoid doing this,
because then you're metaprogramming with strings instead of AST.
You're giving up a lot of Hissp's power.
But optimizing complex formulas is maybe one of the few times it's OK to do that.

Recall the `.#` reader macro executes a form and embeds its result into the Hissp.

```python
#> (define quadratic
#.. (lambda (a b c)
#..   .#"(-b + (b**2 - 4*a*c)**0.5)/(2*a)"))
#..
>>> # define
... __import__('operator').setitem(
...   __import__('builtins').globals(),
...   'quadratic',
...   (lambda a,b,c:(-b + (b**2 - 4*a*c)**0.5)/(2*a)))

```

But for a top-level `define` like this, you could have just used `exec()`.

> How do I start the REPL again?

If you installed the distribution using pip,
you can use the provided `hissp` console script.
```
$ hissp
```
You can also launch the Hissp package directly
using an appropriate Python interpreter from the command line
```
$ python3 -m hissp
```

> There are no statements?! How can you get anything done?

There are expression statements only (each top-level form). That's plenty.

> But there's no assignment statement!

That's not a question.

For any complaint of the form "Hissp doesn't have feature X",
the answer is usually "Write a macro to implement X."

Use the `hissp.basic.._macro_.define` and `hissp.basic.._macro_.let` macros for globals
and locals, respectively.
Look at their expansions and you'll see they don't use assignment statements either.

See also `builtins..setattr` and `operator..setitem`.

Also, Python 3.8 added assignment expressions.
Those are expressions.
A macro could expand to a string containing `:=`,
but as with text-substitution macros generally,
this approach is not recommended.

> But there's no `macroexpand`. How do I look at expansions?

Invoke the macro indirectly somehow so the compiler sees it as a normal function.
`((getattr hissp.basic.._macro_ "define") 'foo '"bar")`
One could, of course, write a function or macro to automate this.

You can also use the method call syntax for this purpose,
which is never interpreted as a macro invocation.
This syntax isn't restricted solely to methods on objects.
Due to certain regularities in Python syntax,
it also works on callable attributes in any kind of namespace.

`(.define hissp.basic.._macro_ : :* '(foo "bar"))`

But you can also just look at the compiled Python output.
It's indented, so it's not that hard to read.
The compiler also helpfully includes a comment in the compiled output
whenever it expands a macro.

> There's no `for`? What about loops?

Sometimes recursion is good enough. Try it.
`list()`, `map()` and `filter()` plus lambda can do
anything list comprehensions can. Ditch the `list()` for lazy generators.
Replace `list()` with `set()` for set comprehensions.
Dict comprehensions are a little trickier.
Use `dict()` on an iterable of pairs. `zip()` is an easy way to make them,
or just have the map's lambda return pairs.
Remember, you can make data tuples with template quotes.

> This is so much harder than comprehensions!

Not really. But you can always write a macro if you want different syntax.
You can pretty easily implement comprehensions this way.

> That's comprehensions, but what about `for` statements?
You don't really think I should build a list just to throw it away?

Side effects are not good functional style.
Avoid them for as long as possible.
Still, you do need them eventually if you want your program to do anything.

Use `any()` for side-effects to avoid building a list.
Usually, you'd combine with `map()`, just like the comprehensions.
Make sure the lambda returns `None`s (or something false),
because a true value acts like `break` in `any()`.
Obviously, you can use this to your advantage if you *want* a break,
which seems to happen pretty often when writing imperative loops.

See also `itertools`, `builtins..iter`.

> There's no `if` statement. Branching is fundamental!

No it's not. You already learned how to `for` loop above.
Isn't looping zero or one times like skipping a branch or not?
Note that `False` and `True` are special cases of `0` and `1` in Python.
`range(False)` would loop zero times, but `range(True)` loops one time.

> What about if/else ternary expressions?

```python
(lambda b, *then_else: then_else[not b]())(
    1 < 2,
    lambda: print('yes'),
    lambda: print('no'),
)
```
There's a `hissp.basic.._macro_.if-else` macro that basically expands to this.
I know it's a special form in other Lisps (or `cond` is),
but Hissp doesn't need it. Smalltalk pretty much does it this way.
Once you have `if` you can make a `cond`. Lisps actually differ on which
is the special form and which is the macro.

> You have to define three lambdas just for an `if`?!
  isn't this really slow? It really ought to be a special form.

It's not *that* slow.
Like most things, performance is really only an issue in a bottleneck.
If you find one, there's no runtime overhead for using `.#` to inject some Python.

Also recall that macros are allowed to return strings of Python code.
All the usual caveats for text-substitution macros apply.
Use parentheses.
```lisp
(defmacro !if (test then otherwise)
  "Compiles to if/else expression."
  (.format "(({}) if ({}) else ({}))"
           : :* (map hissp.compiler..readerless
                     `(,then ,test ,otherwise))))
```
Early optimization is the root of all evil.
Don't use text macros unless you really need them.
Even if you think you need one, you probably don't.

Syntactic macros are powerful not just because they can delay evaluation,
but because they can read and re-write code.
Using a text macro like the above can hide information that a syntactic
rewriting macro needs to work properly.

> Does Hissp have tail-call optimization?

No, because CPython doesn't.
If a Python implementation has it, Hissp will too,
when run on that implementation.

You can increase the recursion limit with `sys..setrecursionlimit`.
Better not increase it too much if you don't like segfaults, but
you can trampoline instead.
See Drython's `loop()` function. Or use it.
Or Hebigo's equivalent macro.
Clojure does it about the same way.

> How do I make a tuple?

Use `tuple()`.

> But I have to already have an iterable, which is why I wanted a tuple in the first place!

`lambda *a:a`

You can also make an empty list with `[]` or `(list)`, and then `.append` to it.
(Try the `cascade` macro.)
Finally, the template syntax ``` `()``` makes tuples. Unquote `,` calls/symbols if needed.

> How do I make a class?

Use `type()`. (Or whatever metaclass.)

> Very funny. That just tells me what type something is.

No, seriously, you have to give it all three arguments. Look it up.

> Well now I need a dict!

Use `dict()`. Obviously.
You don't even need to make pairs if the keys are identifiers.
Just use kwargs.

> That seems too verbose. In Python it's easier.

You mostly don't need classes though.
Classes conflate data structures with the functions that act on them,
and tend to encourage fragmented mutable state which doesn't scale well.
They're most useful for their magic methods to overload operators and such.
But Hissp mostly doesn't need that since it has no operators to speak of.

As always, you can write a function or macro to reduce boilerplate.
There's actually a `hissp.basic.._macro_.deftype` macro for making a top-level type.

> I've got some weird metaclass magic from a library. `type()` isn't working!

Try `types..new_class` instead.

> How do I raise exceptions?

`(operator..truediv 1 0)` seems to work.
Exceptions tend to raise themselves if you're not careful.

> But I need a raise statement for a specific exception message.

Exceptions are not good functional style.
Haskell uses the Maybe monad instead, so you don't need them.
If you must, you can still use a `raise` in `exec()`.
(Or use Drython's `Raise()`, or Hebigo's equivalent macro.) 

> Use exec? Isn't that slow? 

If the exceptions are only for exceptional cases, then does it matter?
Early optimization is the root of all evil.

> What about catching them?

Try not raising them in the first place?
Or `contextlib..suppress`.
 
> But there's no `with` statement either!

Use `contextlib..ContextDecorator`
as a mixin and any context manager works as a decorator.
Or use Drython's `With()`.

> How do I use a decorator?

You apply it to the function (or class):
call it with the function as its argument.
Decorators are just higher-order functions.

> Any context manager? But you don't get the return value of `__enter__()`!
And what if it's not re-entrant?

`suppress` works with these restrictions, but point taken.
You can certainly call `.__enter__()` yourself, but you have to call
`.__exit__()` too. Even if there was an exception.

> But I need to handle the exception if and only if it was raised,
 for multiple exception types, or I need to get the exception object.

Context managers can do all of that!
```python
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
```
You can translate all of that to Hissp.

> How?

Like this
```lisp
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
```

> That is *so* much harder than a `try` statement.

The definition of the context manager is, sure.
but it's not THAT hard.
And you only have to do that part once.
Using the decorator once you have it is really not that bad.

Or, to make things easy, use `exec()` to compile a `try` with callbacks.

> Isn't this slow?! You can't get away with calling this an "exceptional case" this time.
The happy path would still require compiling an exec() string!

Not if you define it as a function in advance.
Then it only happens once on module import.
Something like,
```lisp
(exec "
def try_statement(block, target, handler):
    try:
        block()
    except target as ex:
        handler(ex)")
```
Once on import is honestly not bad. Even the standard library does it,
like for named tuples.
But at this point,
unless you really want a single-file script with no dependencies,
you're better off defining the helper function in Python and importing it.
You could handle the finally/else blocks similarly.
See Drython's `Try()` for how to do it. Or just use Drython.
Hebigo also implements one.
If Hebigo is installed, you can import and use Hebigo's macros, even in Lissp,
because they also take and return Hissp.

> Isn't Hissp slower than Python? Isn't Python slow enough already?

"Slow" usually only matters if it's in a bottleneck.
Hissp will often be slower than Python
because it compiles to a functional subset of Python that relies on
defining and calling functions more.
Because Python is a multiparadigm language,
it is not fully optimized for the functional style,
though some implementations may do better than CPython here.

Early optimization is the root of all evil.
As always don't fix it until it matters,
then profile to find the bottleneck and fix only that part.
You can always re-write that part in Python (or C).

> Yield?

We've got itertools.
Compose iterators functional-style.
You don't need yield.

> But I need it for co-routines. Or async/await stuff. How do I accept a send?

Make a `collections.abc..Geneartor` subclass with a `send()` method.

Or use Drython's `Yield()`.

Generator-based coroutines have been deprecated.
Don't implement them with generators anymore.
Note there are `collections.abc..Awaitable` and `collections.abc..Coroutine`
abstract base classes too.

> How do I add a docstring to a module/class/function?

Assign a string to the `__doc__` attribute of the class or function object.
That key in the dict argument to `type()` also works.
For a module, `__doc__` works
(make a `__doc__` global)
but you should just use a string at the top, same as Python.

> The REPL is nice and all, but how do I run a ``.lissp`` module?

You can use ``hissp`` to launch a ``.lissp`` file as the main module directly.

If you have the entry point script installed that's:
```shell script
$ hissp foo.lissp
```
To be able to import a ``.lissp`` module, you must compile it to Python first.

At the REPL (or main module if it's written in Lissp) use:
```lisp
(hissp.reader..transpile __package__ 'spam 'eggs 'etc)
```
Where spam, eggs, etc. are the module names you want compiled.
(If the package argument is ``None`` or ``''``,
 it will use the current working directory.)

Or equivalently, in Python:
```python
from hissp.reader import transpile

transpile(__package__, "sausage", "bacon")
```
Consider putting the above in each package's `__init__.py` to auto-compile
each Hissp module in the package on package import during development.
You can disable it again on release, if desired,
but this gives you fine-grained control over what gets compiled when.
Note that you usually would want to recompile the whole project
rather than only the changed files like Python does,
because macros run at compile time.
Changing a macro in one file normally doesn't affect the code that uses
it in other files until they are recompiled.

> How do I import things?

Just use a qualified symbol. You don't need imports.

> But it's in a deeply nested package with a long name. It's tedious!

So assign it to a global.
Just don't do this in the macroexpansions where it might end up in another module.

> But I need the module object itself!
The package `__init__.py` doesn't import it or it's not in a package.

Use `importlib..import_module`.
```python
#> (importlib..import_module 'collections.abc)
#..
>>> __import__('importlib').import_module(
...   'collections.abc')
<module 'collections.abc' from ...>

```

> How do I import a macro?

The same way you import anything else.
Put it in the `_macro_`
namespace if you want it to be an active module-local macro.
The compiler doesn't care how it gets there, but
there's a nice `hissp.basic.._macro_.from-require`
macro if you want to use that.

> How do I write a macro?

Make a function that accepts the syntax you want as parameters and
returns its transformation as Hissp code
(the template reader syntax makes this easy).
Put it in the `_macro_` namespace.
There's a nice `hissp.basic.._macro_.defmacro` to do this for you.
It will even create the namespace if it doesn't exist yet.

Some tips:
* Hissp macros are very similar to Clojure or Common Lisp macros.
  * Tutorals on writing macros in these languages are mostly applicable to Hissp.
* Output qualified symbols so it works in other modules.
  * The template reader syntax does this for you automatically.
  * You have to do this yourself in readerless mode.
  * You can interpolate an unqualified symbol into a template by unquoting it,
    same as any other value.
* Use gensyms (`$#spam`) to avoid accidental capture of identifiers.

> How do I write a reader macro?

Make a function that accepts the syntax you want as its parameter and
returns its transformation as Hissp code.

> Why the weird prompts at the REPL?

The REPL is designed so that you can copy/paste it into doctests
or Jupyter notebook cells running an IPython kernel and it should just work.
IPython will ignore the Lissp because its `#>`/`#..`
prompts makes it look like a Python comment,
and it's already set up to ignore the initial `>>> `/`...`.
But doctest expects these,
because that's what the Python shell looks like.

> How do I add a shebang line?

Same as for any executable text file, use a line starting with `#!`
followed by a command to run hissp. (E.g. `/usr/bin/env hissp`)
The transpiler will ignore it if it's the first line.
If you set the executable bit,
like `chmod foo.lissp +x`,
then you can run the file directly.

> I mean how do I add a shebang line to the compiled file?

A text editor works. It's just a Python file.

> I don't want to have to do that manually every time I recompile!

You can use the `.#` reader macro to inject arbitrary text in the compiled output.
Use e.g. `.#"#/usr/bin/env python"` as the first compiled line.

> Is Hissp stable?

Not exactly.
This project is still pretty new.
The compiler seems pretty settled.
(It's stable enough for Hebigo.)
But the basic macros aren't right yet.

There's probably no need to ever change the basic language,
except perhaps to keep up with Python,
since the macro system makes it so flexible.
But Hissp is still unproven in any major project, so who knows?
The only way it will get proven is if some early adopter like you
tries it out and lets me know how it goes.
