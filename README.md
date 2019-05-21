(rough draft)

# TODOs before public release?
* reader macros
  * implement customizable reader macros
  * `\.` eval at read time
  * `\_` drop form
  * ```\` ``` template quote
  * `\,` unquote
  * `\,@` splice
  * `\#` gensym
* set up Sphinx docs/tests.
  * can we doctest using the Hissp REPL?
* setup.py for PyPI
* automated tests?

# Hissp

It's Python with a *Lissp*.

Hissp is a Lisp that compiles to a functional subset of Python.

## Philosophy and Goals
#### Radical Extensibility
Python is already a really nice language, so why do we need Hissp?

The answer is *metaprogramming*: code that writes code.
When you can shape the language itself to fit your problem domain,
the inexpressible becomes ordinary.

Lisp is a programmable programming language,
extensible though its legendary macro system which hooks into the compiler itself.

Adding features that historically require a new version of the Python language,
like `with` statements, would be almost as easy as writing a new function in Lisp.

Python can certainly do metaprogramming.
But it's more difficult than necessary.
Python AST manipulation is certainly a powerful technique,
but not for the faint of heart.
Python AST is not simple, because Python isn't.
Even `eval()` sees use in the standard library.
It's easy enough to understand,
but may be even harder to get right.

Hissp makes metaprogramming much easier.
Hissp code is made of specially formatted tuples:
a simplified kind of AST that is easier to manipulate,
but still more reliable than text manipulation.
Hissp code is just another kind of data.

#### Simplicity
Be as simple as possible, but no simpler.
Hissp includes what it needs to achieve its goals, but no more.
There are only two special forms: quote and lambda.

Hissp compiles to a *functional subset* of Python.
This subset has a direct and easy-to-understand correspondence to the Hissp code,
which makes it straightforward to debug, once you understand Hissp.
But it is definitely not meant to be idiomatic Python.
That would require a much more complex compiler,
because idiomatic Python is not simple.

#### Interoperability
OK, but there are lots of other Lisps.
Why not use one of them? Why base one on Python?

Python has a rich selection of libraries for a variety of domains
and Hissp can use most of them as easily as the standard library.
This gives Hissp a massive advantage over other Lisps with less selection.
If you don't care to work with the Python ecosystem,
perhaps Hissp is not the Lisp for you.

Note that Hissp is written in Python 3.7.
(Supporting older versions is not a goal,
because that would complicate the compiler.
This may limit the available libraries.)

Python can also use packages written in Hissp,
because they compile to Python.

#### Useful error messages
One of Python's best features.
Any errors that prevent compilation should be easy to find.

#### Syntax compatible with Emacs' `lisp-mode` and Parlinter
A language is not very usable without tools.
Hissp's basic reader should work with Emacs.

#### Standalone output
Batteries not included because Python already has them.
One can, of course, write Hissp code that depends on any Python library.
But the compiler does not depend on embedding calls out to any special
Hissp helper functions to work.
You do not need Hissp installed to run the final compiled Python output,
only Python itself.

Hissp includes some very basic Lisp macros to get you started.
Their expansions have no external requirements either.

#### REPL
A Lisp tradition, and Hissp is no exception.
Even though it's a compiled language,
Hissp has an interactive shell like Python does.
The REPL displays the compiled Python and evaluates it.
Printed values use the normal Python reprs.
(Translating those to Hissp is not a goal.)

#### Same-module macro helpers
Not all Lisps support this, but Clojure is a notable exception.
Functions are generally preferable to macros when functions can do the job.
They're more reusable and composable.
Therefore it makes sense for macros to delegate to functions where possible.
But such a macro should work in the same module.
This requires incremental compilation of forms, like the REPL.

#### Modularity
The Hissp language is made of tuples, not text.
The basic reader included with the project just implements convenient way to write them.
It's possible to write Hissp in "readerless mode" by writing the tuples in Python.

It's also possible for an external project to provide an alternative
reader with different syntax, as long as the output is Hissp tuples.

Because Hissp produces standalone output, it's not locked into any one Lisp paradigm.
It could work with a Clojure-like, Scheme-like, or Common-Lisp-like
reader, function, and macro libraries.

It is a goal of the project to support a more Clojure-like reader and
function/macro library.
But this will be an external project in another repository.

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
## (builtins..print 1 2j 3.0 [4,'5',6] : sep ":")

>>>  __import__('builtins').print((1),(2j),(3.0),[(4),'5',(6)],sep=':')
1:2j:3.0:[4, '5', 6]

## (hissp.basic.._macro_.define tuple* (lambda (: :* xs) xs))

>>>  __import__('operator').setitem(__import__('builtins').globals(),'tuplexSTAR_',(lambda *xs:xs))
```

### Calls. Hissp is literally all calls.
Hissp has only two types of expressions or forms: literals, and calls.

#### Literals and the Reader
Literals are handled at the reader level.

Hissp code is made of tuples, not text.
"The reader" refer's to Hissp's basic parser.
It's the reader's job to translate the `.lissp` code files into Hissp tuples.
One could skip the reader altogether and write the tuples in Python directly.
This is called "readerless mode".
It's also possible to use alternative readers with alternate syntax,
but it must represent the same underlying tuples to be Hissp.

Using the basic reader, any valid Python literal is a valid Hissp literal,
provided it does not contain `"`, `(`, `)`, or spaces,
because then it would be read as multiple items.

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
This format was chosen because it contains both lower-case, upper-case,
and an underscore.
This makes it distinct from standard Python naming conventions:
`lower_case_with_underscores`, `UPPER_CASE_WITH_UNDERSCORES`. and `CapWords`,
which makes it easy to tell if an identifier contains munged characters.
It also cannot introduce a leading underscore,
which can have special meaning in Python.

Reader macros consist of a symbol beginning with a `\ ` followed by another form.
The function named by the symbol is invoked on the form,
and the reader inserts the resulting object into the output code.

#### Calls and the compiler

Here's a little more Hissp-specific example.
Note the lack of commas between arguments.
```
$ python -m hissp
## (builtins..print 1 2j 3.0 [4,'5',6] : sep ":")

>>>  __import__('builtins').print((1),(2j),(3.0),[(4),'5',(6)],sep=':')
1:2j:3.0:[4, '5', 6]
```
This is the basic Hissp REPL.
It shows the Python compilation and its result.

That `[4,'5',6]` is read as a single literal. Note the lack of spaces.
The double-quoted string literal is an exception. It may have spaces.
And unlike Python, it is allowed to contain literal newlines.

The `builtins..print` is an example of a *qualified symbol*.
These are of the form `<package>..<item>`, and are important to make
macros work properly across modules.
Note that package names may contain dots, as in Python.

The `:` separates the single arguments from the paired arguments,
which either pair a value with a unique key like `sep ":"` or with the
special unpacking keywords `:*` and `:**`, like `:* args` or `:** kwargs`,
which, like Python, can be repeated.

Hissp's two special forms deserve special consideration.
These are calls that are built into the compiler.
Unlike a normal function call, special forms are evaluated at compile time.

The first special form is `quote`. It returns its argument unevaluated.
```
## (quote builtins..print)

>>>  'builtinsxSLASH_print'
'builtinsxSLASH_print'
```
The distinction between symbols and strings only applies to the reader.
Hissp has no separate symbol type. A quoted symbol is just a string.

Here's the earlier example quoted.
```
## (quote (builtins..print 1 2j 3.0 [4,'5',6] : sep ":"))

>>>  ('builtinsxSLASH_print',(1),(2j),(3.0),[(4),'5',(6)],'xET_','sep',('quote',':',),)
('builtinsxSLASH_print', 1, 2j, 3.0, [4, '5', 6], 'xET_', 'sep', ('quote', ':'))
```
This reveals how to write the example in readerless mode.
Many literal types simply evaluate to themselves and so are unaffected by quoting.
The exceptions are strings and tuples, which can represent identifiers and calls.

Quoting is important enough to have a special reader macro.
`\' foo` is the same as `(quote foo)`.

The second special form is `lambda`
The first argument of a lambda is the pararmeters tuple.
Like calls, the `:` separates the single from the paired (if any).
After the paramters tuple, the rest of the arguments are the function body.

```
## (lambda (a b
            : e 1  f 2
            :* args  h 4  i :  j 1
            :** kwargs)
    42)

>>>  (lambda a,b,e=(1),f=(2),*args,h=(4),i,j=(1),**kwargs:(42))
<function <lambda> at 0x0000019D826B38C8>

## (lambda (: :* :  x :))

>>>  (lambda *,x:())
<function <lambda> at 0x0000019D8269FD08>

## (lambda (a b c)
    (print a)
    (print b)
    c)

>>>  (lambda a,b,c:(print(a),print(b),c)[-1])
<function <lambda> at 0x0000019D8269F0D0>
```

Normal call forms evaluate their arguments before calling the function,
as Python does.
Special forms are different.
Quote arguments are not evaluated at all.
The body of a lambda is not evaluated until the function is invoked,
and its parameter tuple is partly evaluated (if there are defaults) and
partly quoted.
While there are only two special forms, the compiler is extensible via macros.
Like special forms, macro calls do not have to evaluate their arguments.

Macros are simply functions that take Hissp code, and return Hissp code.
When an unqualified symbol is in the function position of a tuple about
to be evaluated, the compiler checks if the module's `_macro_` namespace
has that symbol. If it does it is called at compile time as a macro.

Qualified symbols can also be macros if looked up directly from their module's `_macro_`.
E.g. `(hissp.basic.._macro_.define FOO 0xf00)`

The `hissp.basic.._macro_.defmacro` macro defines a function in the module's macro space,
creating `_macro_` if it doesn't exist yet.
But the compiler doesn't care how it gets there:
`_macro_` functions are macros regardless. This means "importing" a macro is as simple
as adding it to the current module's macro space.

## FAQ (Frequently Anticipated Questions)

> Anticipated? Didn't you mean "asked"?

Well, this project is still pretty new.

> Can Hissp really do anything Python can when it only compiles to a subset of it?

Yes.

Short proof: Hissp has strings and can call `exec()`.

But you usually won't need it because you can import anything written in Python.

> What's 1 + 1?

Two.

> I mean how do you write it in Hissp without operators? Please don't say `eval()`.

We have all the operators because we have all the standard library functions.
```
(operator..add 1 1)
```
You can, of course, abbreviate these, E.g.
```
(hissp.basic.._macro_.define + operator..add)
(+ 1 1)
```
Yes, `+` is a valid symbol. It gets munged to `xPLUS_`.

> There are no statements?! How can you get anything done?

There are expression statements only (each top-level form). That's plenty.

> But there's no assignment statement!

That's not a question.
Use the `hissp.basic.._macro_.define` and `hissp.basic.._macro_.let` macros for globals
and locals, respectively.
Look at their expansions and you'll see they don't use assignment statements either.

> But there's no `macroexpand`.

Invoke the macro indirectly so the compiler sees it as a normal function.
`((getattr hissp.basic.._macro_ "define") \' foo \' "bar")`
One could, of course, write a function or macro to automate this.

> There's no `for`? What about loops?

Try recursion. `list()`, `map()` and `filter()` plus lambda can do
anything list comprehensions can. Ditch the `list()` for lazy generators.
Replace `list()` with `set()` for set comps. Dict comps are a little trickier.
Use `dict()` on an iterable of pairs. `zip()` is an easy way to make them,
or just have the map's lambda return pairs.

> That's comprehensions, but what about `for` statements?
You don't really think I should build a list just to throw it away?

Side effects are not good functional style.
Avoid them for as long as possible.
Still, you do need them eventually if you want your program to do anything.

Use `any()` for side-effects to avoid building a list.
Usually, you'd combine with `map()`, just like the comprehensions.
Make sure the lambda returns `None`s (or something false),
because a true value acts like `break` in `any()`.
Obviously, you can use this to your advantage if you *want* a break.
Also see `itertools`, `iter`.

> There's no if statement. Branching is fundamental!

No it's not. You already learned how to for loop above.
Isn't looping zero or one times like skipping a branch or not?
Note that `False` and `True` are special cases of `0` and `1` in Python.
`range(False)` is zero times, but `range(True)` is one time.

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

> Does Hissp have tail-call optimization?

No, but you can increase the recursion limit with `sys..setrecursionlimit`.
Better not increase it too much if you don't like segfaults, but
you can trampoline instead. See Drython's `loop()` function. Or use it.
Clojure does it about the same way.

> How do I make a tuple?

Use `tuple()`.

> But I have to already have an iterable, which is why I wanted a tuple in the first place!

`lambda *a:a`

You can also make an empty list with `[]` or `(list)`, and then `.append` to it.
Finally, the template syntax makes tuples. Unquote calls/symbols if needed.

> How do I make a class?

Use `type()`. (Or whatever metaclass.)

> Very funny. That just tells me what type something is.

No, seriously, you have to give it all three arguments. Look it up.

> How do I use a decorator?

You apply it to the function (or class)--call it with the function as its argument.
Decorators are just higher-order functions.

> How do I raise exceptions?

`(operator..truediv 1 0)` seems to work.
Exceptions tend to raise themselves if you're not careful.

> But I need a raise statement for a specific exception message.

 Exceptions are not good functional style.
 You probably don't need them.
 If you must, you can still use `exec()`
 
> Isn't that slow? 

If the exceptions are only for exceptional cases, then does it matter?
Early optimization is the root of all evil.

> What about catching them?

Try not raising them in the first place?
Or `contextlib..suppress`.
 
> But there's no `with` statement either!

Use `contextlib..ContextDecorator`
as a mixin and any context manager works as a decorator.

> Any context manager? But you don't get the return value of `__enter__()`!
And what if it's not re-entrant?

`suppress` work with these restrictions, but point taken.
You can certainly call `.__enter__` yourself, but you have to call
`.__exit__` too. Even if there was an exception.

> But I need to handle the exception if and only if it was raised,
 for multiple exception types, or I need to get the exception object.

Use `exec()` with callbacks in its locals.

> Isn't this slow?! You can't get away with calling this an "exceptional case" this time.
The happy path would still require compiling an exec() string!

Not if you define it as a function in advance.
Then it only happens once on module import.
Something like,
```
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
See Drython for how to do it. Or just use Drython.

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

We've got itertools. Compose generators functional-style. You don't need yield.

> But I need it for co-routines. Or async/await stuff. How do I accept a send?

Make a `collections.abc..Geneartor` subclass with a `send()` method.

Generator-based coroutines have been deprecated.
Don't implement them with generators anymore.
Note there are `collections.abc..Awaitable` and `collections.abc..Coroutine`
abstract base classes too.

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

Changes to the source code must be properly formatted and have full test
coverage before the PR can be accepted.
Manual tests may suffice for configuration files.
Our Python source uses Black formatting.
Disable this using `# fmt: off` tags for "readerless mode" Hissp snippets
which should be formatted lisp-style (play with parinfer until you get it),
or anywhere the extra effort of manual formatting is worth it.
In readerless mode, Hissp tuples shall always include the trailing `,`.
Follow PEP 8 even when Black has no opinion.
Our .lissp source uses Emacs lisp-mode for indentation.
It must also pass Parlinter.

Documentation is expected to have correct (American English) spelling
and grammar. All Doctests must pass.

We merge to master without squashing.
Commits must be small enough to be reviewable.
We don't accept PRs on faith.

PRs do not have to be *perfect* to be submitted,
but must be perfect enough to pass peer review before they are merged in.

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

