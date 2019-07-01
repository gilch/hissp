<!--
Copyright 2019 Matthew Egan Odendahl
SPDX-License-Identifier: Apache-2.0
-->
[![Gitter](https://badges.gitter.im/hissp-lang/community.svg)](https://gitter.im/hissp-lang/community?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge)
[![Documentation Status](https://readthedocs.org/projects/hissp/badge/?version=latest)](https://hissp.readthedocs.io/en/latest/?badge=latest)
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

Hissp is a Lisp that compiles to a functional subset of Python.
It's the Python you know and love, with a powerful, streamlined skin.


<!-- markdown-toc start - Don't edit this section. Run M-x markdown-toc-refresh-toc -->
**Table of Contents**

- [Hissp](#hissp)
    - [Philosophy and Goals](#philosophy-and-goals)
        - [Minimal implementation](#minimal-implementation)
        - [Interoperability](#interoperability)
        - [Useful error messages](#useful-error-messages)
        - [Syntax compatible with Emacs' `lisp-mode` and Parlinter](#syntax-compatible-with-emacs-lisp-mode-and-parlinter)
        - [Standalone output](#standalone-output)
        - [REPL](#repl)
        - [Same-module macro helpers](#same-module-macro-helpers)
        - [Modularity](#modularity)
    - [Show me some Code!](#show-me-some-code)
        - [The obligatory Hello, World!](#the-obligatory-hello-world)
        - [Calls. Hissp is literally all calls.](#calls-hissp-is-literally-all-calls)
            - [Literals and the Reader](#literals-and-the-reader)
            - [Calls and the compiler](#calls-and-the-compiler)
    - [FAQ (Frequently Anticipated Questions (and complaints))](#faq-frequently-anticipated-questions-and-complaints)
    - [Contributing](#contributing)
        - [Patches](#patches)
        - [Conduct](#conduct)
            - [good faith](#good-faith)
            - [professional detachment](#professional-detachment)
            - [disputes](#disputes)

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

Lisp is a programmable programming language,
extensible though its renowned macro system
which hooks into the compiler itself.
Macros are Lisp's secret weapon.
And Hissp brings this power to Python.

Adding features that historically required a new version of the Python language,
like `with` statements, would be almost as easy as writing a new function in Lisp.

#### Minimal implementation
The Hissp compiler includes what it needs to achieve its goals,
but no more. Bloat is not allowed.
A goal of Hissp is to be as small as reasonably possible, but no smaller.
We're not code golfing here; readability still counts.
But this project has *limited scope*.

Hissp compiles to an upythonic *functional subset* of Python.
This subset has a direct and easy-to-understand correspondence to the Hissp code,
which makes it straightforward to debug, once you understand Hissp.
But it is definitely not meant to be idiomatic Python.
That would require a much more complex compiler,
because idiomatic Python is not simple.

#### Interoperability
Why base a Lisp on Python when there are already lots of other Lisps?

Python has a rich selection of libraries for a variety of domains
and Hissp can use most of them as easily as the standard library.
This gives Hissp a massive advantage over other Lisps with less selection.
If you don't care to work with the Python ecosystem,
perhaps Hissp is not the Lisp for you.

Note that the Hissp compiler is written in Python 3.7.
(Supporting older versions is not a goal,
because that would complicate the compiler.
This may limit the available libraries.)
But because the compiler's target functional subset is so small,
the compiled output should still run fine on Python 3.5,
provided you aren't using any newer library features.
Running on even older versions (even Python 2)
may be possible if you avoid using certain newer Python language features.
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
(Translating those to Hissp is not a goal. Hissp is still Python.)

#### Same-module macro helpers
Not all Lisps support this, but Clojure is a notable exception.
Functions are generally preferable to macros when functions can do the job.
They're more reusable and composable.
Therefore it makes sense for macros to delegate to functions where possible.
But such a macro should work in the same module.
This requires incremental compilation and evaluation of forms, like the REPL.

#### Modularity
The Hissp language is made of tuples (and values), not text.
The basic reader included with the project just implements convenient
way to write them.
It's possible to write Hissp in "readerless mode"
by writing these tuples in Python.

Batteries are not included because Python already has them.
Hissp's standard library is Python's.
There are only two special forms: quote and lambda.
Hissp does include a few basic macros and reader macros,
just enough to write native unit tests,
but you are not obligated to use them when writing Hissp.

It's possible for an external project to provide an alternative
reader with different syntax, as long as the output is Hissp code (tuples).

Because Hissp produces standalone output, it's not locked into any one Lisp paradigm.
It could work with a Clojure-like, Scheme-like, or Common-Lisp-like, etc.,
reader, function, and macro libraries.

It is a goal of the project to support a more Clojure-like reader and
a complete function/macro library.
But while this informs the design of the compiler,
it will be an external project in another repository.

## Show me some Code!
Or, the Hissp tutorial.

### The obligatory Hello, World!
```lisp
(print "Hello, World!")
```
Honestly, that is 80% of Lisp right there. I told you it was simple.
And the Python translation, as if you couldn't guess.
```python
print("Hello, World!")
```
Yeah, we moved a parenthesis.
Lisp is so arcane, isn't it?

Here's a more involved demonstration to whet you appetite.
For someone experienced in both Python and Lisp,
this may be enough to get you started,
but don't worry if you don't understand it all yet.
This will all be explained in more detail later on.
```
$ python -m hissp
```
```python
#> (builtins..print 1 2j 3.0 [4,'5',6] : sep ":")
#..
>>> __import__('builtins').print(
...   (1),
...   (2j),
...   (3.0),
...   [4, '5', 6],
...   sep=':')
1:2j:3.0:[4, '5', 6]

#> (hissp.basic.._macro_.define tuple* (lambda (: :* xs) xs))
#..
>>> # hissp.basic.._macro_.define
... __import__('operator').setitem(
...   __import__('builtins').globals(),
...   'tuplexSTAR_',
...   (lambda *xs:xs))

```

### Calls. Hissp is literally all calls.
Hissp has only two types of expressions or forms: literals, and calls.

#### Literals and the Reader
Literals are handled at the reader level.

"The reader" refer's to Hissp's basic parser.
It's the reader's job to translate the `.lissp` code files into Hissp code.

It's important to distinguish these two things,
because they each have their own type of macro:

* *Lissp* code is made of text, and the basic reader parses it into Hissp.
You can hook into this process with a *reader macro*,
which can embed arbitrary Python objects into the Hissp.

* *Hissp* code is made of tuples (and values), not text.
Lissp is to Hissp as the written word is to the spoken word.
It's ephemeral; it only lives in memory.
The compiler compiles Hissp to a *functional subset of Python*.
You can hook into this process with a *compiler macro*.
Without context suggesting otherwise,
the term *macro* refers to a *compiler macro*.

Lissp is a fairly direct *representation* of Hissp, but it's not the only one.
One could skip the reader altogether and write the Hissp in Python directly as tuples.
This is called "readerless mode".
Reader macros are an artifact of the reader and don't exist in readerless mode at all,
but compiler macros do work.
It's also possible to use alternative readers with alternate syntax,
but it must *represent* the same underlying tuples to be Hissp.

Using the basic reader,
any valid Python literal (as defined by `ast..literal_eval`)
is a valid Hissp literal,
provided it does not contain `"`, `(`, `)`, or spaces
(because then it would be read as multiple items) 
or start with a `'`.

In addition to the Python literals,
the basic reader has symbol literals, string literals,
and is extensible with more literal types via reader macros.

String literals begin and end with `"` and may contain literal newlines,
but otherwise behave the same as Python's do.

Anything else is a symbol.
Symbols are allowed to contain many special characters, but because
symbols are meant to be used as Python identifiers,
the reader automatically munges invalid identifier characters to x-quoted words,
like `/` to `xSLASH_`.
This format was chosen because it contains an underscore
and both lower-case and upper-case letters,
which makes it distinct from standard Python naming conventions:
`lower_case_with_underscores`, `UPPER_CASE_WITH_UNDERSCORES`. and `CapWords`.
This makes it easy to tell if an identifier contains munged characters.
It also cannot introduce a leading underscore,
which can have special meaning in Python.

A symbol that begins with a `:` is a "keyword".
Keywords are never interpreted as identifiers,
so they don't need to be quoted or munged.

The basic reader's macro syntax is limited to tagged forms,
like EDN and Clojure, but unlike Common Lisp
(which could dispatch on any character),
because it's meant to be compatible with existing tooling for syntax
highlighting and structural editing,
which wouldn't work if you change the grammar.
(An alternate reader for Hissp need not have this limitation.)

Reader macros in Lissp consist of a symbol ending with a `#`
followed by another form.
The function named by the symbol is invoked on the form,
and the reader embeds the resulting object into the output Hissp.

For example,
```python
#> builtins..float#inf
>>> __import__('pickle').loads(  # inf
...     b'\x80\x03G\x7f\xf0\x00\x00\x00\x00\x00\x00.'
... )
inf

```
This inserts an actual `inf` object at read time into the Hissp code.
Since this isn't a valid literal, it has to compile to a pickle.
You should normally try to avoid emitting pickles
(e.g. use `(float 'inf)` or `math..inf` instead),
but note that a macro would get the original object,
since the code hasn't been compiled yet, which may be useful.
While unpickling does have some overhead,
it may be worth it if constructing the object normally has even more.
Naturally, the object must be picklable to emit a pickle.

Unqualified reader macros are reserved for the basic Hissp reader.
There are currently three of them: `.#`, `_#`, and `$#`.

If you need more than one argument for a reader macro, use the built in
`.#` macro, which evaluates a form at read time. For example,
```python
#> .#(fractions..Fraction 1 2)
#..
>>> __import__('pickle').loads(  # Fraction(1, 2)
...     b'\x80\x03cfractions\nFraction\nX\x03\x00\x00\x001/2\x85R.'
... )
Fraction(1, 2)

```

The `_#` macro omits the next form.
It's a way to comment out code,
even if it takes multiple lines.

There are also four more built-in reader macros that don't end with `#`:
* ``` ` ``` template quote
* `,` unquote
* `,@` splice unquote
* `'` quote

The final builtin `$#` creates a gensym based on the given symbol.
Within a template, the same gensym literal always makes the same
gensym.
```python
#> `($#hiss $#hiss)
#..
>>> (lambda *xAUTO0_:xAUTO0_)(
...   '_hissxAUTO..._',
...   '_hissxAUTO..._')
('_hissxAUTO..._', '_hissxAUTO..._')

```

In readerless mode, these reader macros correspond to functions used to
make the Hissp itself.
For example, one could make a quoting "readerless macro" like this

```python
>>> def q(form):
...     return 'quote', form
>>> from hissp.compiler import readerless
>>> readerless(
...     ('print', q('hi'),),
... )
"print(\n  'hi')"
>>> print(_)
print(
  'hi')
>>> eval(_)
hi

```
Which is equivalent to
```python
#> (print 'hi)
#..
>>> print(
...   'hi')
hi

```

#### Calls and the compiler

Here's a little more Hissp-specific example.
Note the lack of commas between arguments.
```
$ python -m hissp
```
```python
#> (builtins..print 1 2j 3.0 [4,'5',6] : sep ":")
#..
>>> __import__('builtins').print(
...   (1),
...   (2j),
...   (3.0),
...   [4, '5', 6],
...   sep=':')
1:2j:3.0:[4, '5', 6]

```
This is the basic Hissp REPL.
It shows the Python compilation and its result.

That `[4,'5',6]` is read as a single literal. Note the lack of spaces.
The double-quoted string literal is an exception. It may have spaces.
And unlike Python, it is allowed to contain literal newlines.

The `builtins..print` is an example of a *qualified symbol*,
which is a kind of implicit import.
These are of the form `<package>..<item>`, and are important to make
macros work properly across modules.
You don't have to qualify builtins normally, but in a macroexpansion,
this allows the macro to work even if the builtin name has been
shadowed by a local variable in that context.
Note that package names may contain dots, as in Python.

The `:` separates the single arguments from the paired arguments,
which either pair a value with a unique key like `sep ":"` or with the
special unpacking keywords `:*` and `:**`, like `:* args` or `:** kwargs`,
which, like Python, can be repeated.

Hissp's two special forms deserve special consideration.
These are calls that are built into the compiler.
Unlike a normal function call, special forms are evaluated at compile time.

The first special form is `quote`. It returns its argument unevaluated.
```python
#> (quote builtins..print)
#..
>>> 'builtins..print'
'builtins..print'

```
The distinction between symbols and strings only applies to the reader.
Hissp has no separate symbol type.
A quoted symbol just emits a string.

Here's the earlier example quoted.
```python
#> (quote (builtins..print 1 2j 3.0 [4,'5',6] : sep ":"))
#..
>>> ('builtins..print', 1, 2j, 3.0, [4, '5', 6], ':', 'sep', ('quote', ':', {':str': True}))
('builtins..print', 1, 2j, 3.0, [4, '5', 6], ':', 'sep', ('quote', ':', {':str': True}))

```
This reveals how to write the example in readerless mode.
Notice the reader adds some metadata ``{':str': True}``
to quoted strings that were read from double-quoted strings.
Arguments to ``quote`` after the first have no effect on compilation,
but may be useful to macros and reader macros.
Many literal types simply evaluate to themselves and so are unaffected by quoting.
The exceptions are strings and tuples, which can represent identifiers and calls.

Quoting is important enough to have a special reader macro.
`'foo` is the same as `(quote foo)`.

The second special form is `lambda`
The first argument of a lambda is the pararmeters tuple.
Like calls, the `:` separates the single from the paired (if any).
After the parameters tuple, the rest of the arguments are the function body.

```python
#> (lambda (a b  ; single/positional
#..         : e 1  f 2  ; paired/kwargs
#..         :* args  h 4  i :?  j 1  ; *args and kwonly
#..         :** kwargs)
#.. 42)
#..
>>> (lambda a,b,e=(1),f=(2),*args,h=(4),i,j=(1),**kwargs:(42))
<function <lambda> at ...>

#> (lambda (: :* :?  x :?))  ; Only kwonly. Empty body returns ().
#..
>>> (lambda *,x:())
<function <lambda> at ...>

#> (lambda (a b c)
#.. (print a)
#.. (print b)
#.. c)
#..
>>> (lambda a,b,c:(
...   print(
...     a),
...   print(
...     b),
...   c)[-1])
<function <lambda> at ...>

```

Normal call forms evaluate their arguments before calling the function,
as Python does.
Special forms are different&mdash;`quote`'s argument is not evaluated at all.
The body of a lambda is not evaluated until the function is invoked,
and its parameter tuple is partly evaluated (if there are defaults) and
partly quoted.
While there are only two special forms, the compiler is extensible via macros.
Like special forms, macro calls do not have to evaluate their arguments.

Macros are simply functions that take Hissp code, and return Hissp code.
When an unqualified symbol is in the function position of a tuple about
to be evaluated, the compiler checks if the module's `_macro_` namespace
has that symbol. If it does, it is called at compile time as a macro and
the result is inserted into the code in its place.

Qualified symbols can also be macros if looked up directly from their module's `_macro_`.
E.g. `(hissp.basic.._macro_.define FOO 0xf00)`

The `hissp.basic.._macro_.defmacro` macro defines a function in the module's macro space,
creating `_macro_` if it doesn't exist yet.
But the compiler doesn't care how it gets there:
`_macro_` functions are macros regardless. This means "importing" a macro is as simple
as adding it to the current module's macro space.

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
But, like a SQL injection attack,
the string *could* contain almost arbitrary Python code instead.

Howerver, the whole point of Hissp is syntactic macros.
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

Also recall that (reader) macros can return arbitrary Python snippets
and the compiler will emit them verbatim.
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

> But there's no `macroexpand`. How do I look at expansions?

Invoke the macro indirectly so the compiler sees it as a normal function.
`((getattr hissp.basic.._macro_ "define") 'foo '"bar")`
One could, of course, write a function or macro to automate this.

But you can just look at the compiled output.
It's indented, so it's not that hard to read.
The compiler also helpfully includes a comment in the compiled output
whenever it expands a macro.

> There's no `for`? What about loops?

Try recursion. `list()`, `map()` and `filter()` plus lambda can do
anything list comprehensions can. Ditch the `list()` for lazy generators.
Replace `list()` with `set()` for set comps. Dict comps are a little trickier.
Use `dict()` on an iterable of pairs. `zip()` is an easy way to make them,
or just have the map's lambda return pairs.

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
lambda: print('no')
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
Like most things, it's really only an issue in a bottleneck.
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
But you can increase the recursion limit with `sys..setrecursionlimit`.
Better not increase it too much if you don't like segfaults, but
you can trampoline instead. See Drython's `loop()` function. Or use it.
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

> How do I raise exceptions?

`(operator..truediv 1 0)` seems to work.
Exceptions tend to raise themselves if you're not careful.

> But I need a raise statement for a specific exception message.

Exceptions are not good functional style.
You probably don't need them.
If you must, you can still use `exec()`.
(Or use Drython's `Raise()`.) 

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

`suppress` work with these restrictions, but point taken.
You can certainly call `.__enter__()` yourself, but you have to call
`.__exit__()` too. Even if there was an exception.

> But I need to handle the exception if and only if it was raised,
 for multiple exception types, or I need to get the exception object.

Use `exec()` with callbacks in its locals.

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

> Isn't Hissp slower than Python? Isn't Python slow enough already?

"Slow" only matters if it's in a bottleneck.
Hissp will often be slower than Python,
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

Assign a string to the `__doc__` attribute of the module/class/function object.
That means defining a global in the module,
or a key in the dict argument to `type()` also works.

> The REPL is nice and all, but how do I compile a module?

```lisp
(hissp.reader..transpile "hissp" "basic")
```
or
```python
from hissp.reader import transpile

transpile(__package__, "spam", "eggs")
```
Consider putting the above in `__init__.py` to auto-compile
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

## Contributing
There are many ways to contribute to an open-source project,
even without writing code.

Questions are allowed on the issue tracker,
they help illustrate deficiencies in our documentation,
but do check there first!

Bug reports are welcome.

PRs to help improve documentation,
structure, or compatibility will also be considered.

### Patches
PRs must be aligned with the philosophy and goals of the project to be
considered for inclusion.

PRs do not have to be *perfect* to be submitted,
but must be perfect enough to pass peer review before they are merged in.
Small, focused changes are more likely to be reviewed.

Changes to the source code must be properly formatted and have full test
coverage before the PR can be accepted.
Manual tests may suffice for configuration files.
Our Python source uses Black formatting.
Disable this using `# fmt: off` tags for "readerless mode" Hissp snippets
which should be formatted Lisp-style (play with Parinfer until you get it),
or anywhere the extra effort of manual formatting is worth it.
In readerless mode, Hissp tuples shall always include the trailing `,`.
Follow PEP 8 even when Black has no opinion.
Our .lissp source uses Emacs lisp-mode for indentation.
It must also pass Parlinter.

Documentation is expected to have correct (American English) spelling
and grammar. All Doctests must pass.

You can use pytest to run unittests and doctests at the same time.
Make sure you install the dev requirements first.
Hissp has no dependencies, but its test suite does.
```
$ pip install -r requirements-dev.txt
```
```
$ pytest --doctest-modules --cov=hissp
```

We merge to master without squashing.
Commits must be small enough to be reviewable.
We don't accept PRs on faith.

Note section 5 of the LICENSE.
You must have the legal rights to the patch to submit them under those terms:
either you own the copyright
(e.g. because you are the author of the patch and it was not a work for hire)
or have appropriate license to do it.

The git repository itself will normally suffice as a record of
authorship for copyright purposes.
Don't update the original boilerplate notices on each file.
But commits authored by or owned by someone else must be clearly labeled as such.
No plagiarism will be permitted,
even if you're copying something from the public domain.
We may maintain a NOTICE file per section 4.(d) of the LICENSE if needed.

### Conduct
To encourage participation,
we strive to maintain an environment conducive to cooperation and
collaborative effort. To that end, note that
GitHub's acceptable use and conduct restrictions apply to this repo as well.
Spamming, doxing, harassment, etc. will not be tolerated.
Belligerent users may be blocked at the discretion of the project
maintainer, even on the first offense.
Issues that become heated or veer too far off topic may be closed or locked.
#### good faith
Software Engineers are an eccentric bunch who come from various
generational and world cultures.
Tone is notoriously hard to convey in writing and for many English is
not their first language.
Therefore, before you reply in anger, please
[assume good faith](https://en.wikipedia.org/wiki/Wikipedia:Assume_good_faith)
until there is very obvious evidence to the contrary.
#### professional detachment
You are free to criticize code, documentation, PRs, philosophy, ideas,
and so on, if relevant to the project, but not each other.
Discussion here should be focused on the work, not the people doing it.
This is not the forum for status games.
Contributions alone demonstrate competence.
Issue posts stereotyping, psychoanalyzing, or otherwise categorizing people 
beyond legitimate project roles
(or other such veiled insults, even if spun in a "positive" light)
including similar attempts to aggrandize oneself
(even if spun as self-deprecating)
are, at the very least, off-topic, and subject to moderator action.
#### disputes
While consensus based on stated project goals is usually preferable,
the maintainer is the final arbiter for the project.
He may reinterpret goals, instate rules, and reject contributions.
Even if you disagree with his decision,
you may always make a fork as permitted by the LICENSE.
Just don't call it Hissp (see section 6 of the LICENSE).

