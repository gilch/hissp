# Hissp

It's Python with a *Lissp*.

Hissp is a Lisp that compiles to a functional subset of Python.

## Philosophy and Goals
#### Radical Extensibility
Python is already a really nice language, so why do we need Hissp?

The answer is *Metaprogramming*: code that writes code.
When you can shape the language itself to fit your problem domain,
the inexpressible becomes mundane.

Lisp is a programmable programming language,
extensible though its legendary macro system which hooks into the compiler itself.

Adding features that historically require a new version of the Python language,
like `with` statements, would be almost as easy as writing a new function in Lisp.

Python can certainly do metaprogramming.
But it's more difficult than necessary.
Python AST manipulation is a very powerful technique,
but it's not for the faint of heart.
AST is not simple, because Python isn't.
Even `eval()` sees use in the standard library.
It's easy enough to understand,
but may be even harder to get right.

Hissp makes metaprogramming much easier.
Hissp code is made of specially formatted tuples:
a simplified kind of AST that is easier to manipulate.
Hissp code is just another kind of data.

#### Simplicity
Be as simple as possible, but no simpler.
Hissp includes what it needs to achieve its goals, but no more.
There are only two special forms: quote and lambda.

Hissp compiles to a functional *subset* of Python.
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
Supporting older versions is not a goal,
because that would complicate the compiler.
This may limit the available libraries.

Python can also use packages written in Hissp,
because they compile to Python.

#### Useful error messages
One of Python's best features.
Any errors that prevent compilation should be easy to find.

#### Syntax compatible with Emacs' `lisp-mode` and Parlinter
A language is not very usable without tools.
Hissp's basic reader should work with emacs.

#### Standalone output
Batteries not included because Python already has them.
One can, of course, write Hissp code that depends on any Python library.
But the compiler does not depend on embedding calls out to any special
Hissp helper functions to work.
You do not need Hissp installed to run the final compiled Python output,
only Python itself.

There are some very basic lisp macros to get you started.
Their expansions have no external requirements either.

#### REPL
A Lisp tradition, and Hissp is no exception.
Even though it's a compiled language,
Hissp has an interactive shell like Python does.
The REPL displays the compiled Python and evaluates it.
Printed values use the normal Python reprs.
Translating those to Hissp is not a goal.

#### Same-module macro helpers
Not all Lisps support this, but Clojure is a notable exception.
Functions are generally preferable to macros when functions can do the job.
They're more reusable and composable.
Therefore it makes sense for macros to delegate to functions where possible.
But such a macro should work in the same module.
This requires incremental compilation of forms, like the repl.

#### Modularity
The Hissp language is made of tuples, not text.
The basic reader included with the project is just a convenient way to write them.
It's possible to write Hissp in readerless mode by writing the tuples in Python.

It's also possible for an external project to provide an alternative
reader with different syntax, as long as the output is Hissp tuples.

Because Hissp produces standalone output, it's not locked into any one Lisp paradigm.
It could work with a Clojure-like, Scheme-like, or Common-Lisp-like libraries.

It is a goal of the project to support a more Clojure-like reader and standard library.
But this will be an external project in another repository.

## Show me some Code!

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
Now you can read it and impress your friends.

### Calls. Hissp is literally all calls.
Hissp has only two types of expressions: literals, and calls.

Any valid Python literal is a valid Hissp literal,
provided it does not contain `"`, `(`, `)`, or spaces,
because then it would be read as multiple items.

In addition to the Python literals,
Hissp has symbol literals, string literals, and reader macros.

Here's a little more Hissp-specific example.
Note the lack of commas between arguments.
```
## (builtins/print 1 2j 3.0 [4,'5',6] & sep ":")

>>>  __import__('builtins').print((1),(2j),(3.0),[(4),'5',(6)],sep=':')
1:2j:3.0:[4, '5', 6]
```
This is the basic Hissp REPL.
It shows the Python compilation and its result.

That `[4,'5',6]` is read as a single literal. Note the lack of spaces.
The double-quoted string literal is an exception. It may have spaces.
And unlike Python, it is allowed to contain literal newlines.

The `builtins/print` is an example of a *qualified symbol*.
These are of the form `<package>/<item>`, and are important to make
macros work properly across modules.
Note that package names may contain dots, as in Python.

The `&` separates the single arguments from the paired arguments,
which either pair a value with a unique key like `sep ":"` or with the
special unpacking names `*` and `**`, like `* args` or `** kwargs`,
which, like Python, can be repeated.

Hissp's two special forms deserve special consideration.
These are calls that are built into the compiler.
Unlike a normal function call, special forms are evaluated at compile time.

The first special form is `quote`. It returns its argument unevaluated.
```
## (quote builtins/print)

>>>  'builtinsxSLASH_print'
'builtinsxSLASH_print'
```
The distinction between symbols and strings only applies to the reader.
Hissp has no separate symbol type. A quoted symbol is just a string.

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

Munging happens at the reader level. The compiler is not aware of this at all, so
```
## (builtinsxSLASH_print (quote ?))

>>>  __import__('builtins').print('xQUERY_')
xQUERY_
```
is valid syntax, and contains a qualified symbol.



## FAQ (Frequently Anticipated Questions)

* Anticipated? Didn't you mean "asked"?

Well, this project is still pretty new.

* There's no statements?! How can you get anything done?

There are expression statements only (each top-level form). That's plenty.

* But there's no assignment statement!

That's not a question.
Use the `hissp.basic/!.define` and `hissp.basic/!.let` macros for globals
and locals, respectively.
Look at their expansions and you'll see they don't use assignment statements either.

* But there's no `macroexpand`.

Invoke the macro indirectly so the compiler sees it as a normal function.
`((getattr hissp.basic/! "define") #' foo #' "bar")`
One could, of course, write a function or macro to automate this.

* There's no `for`? What about loops?

Try recursion. `list()`, `map()` and `filter()` plus lambda can do
anything list comprehensions can. Ditch the `list()` for lazy generators.
Replace `list()` with `set()` for set comps. Dict comps are a little trickier.
Use `dict()` on an iterable of pairs. `zip()` is an easy way to make them.
Use `any()` for side-effects to avoid building a list.
Make sure the lambda returns `None`s, because a true value acts like `break`.
Also see `itertools`.

* There's no if statement. Branching is fundamental!

No it's not. You already learned how to for loop above.
Isn't looping zero or one times like skipping a branch or not?
Note that `False` and `True` are special cases of `0` and `1` in Python.
`range(False)` is zero times, but `range(True)` is one time.

* What about if/else ternary expressions?

```python
(lambda b, *then_else: then_else[not b]())(
1 < 2,
lambda: print('yes'),
lambda: print('no')
)
```
There's a `hissp.basic/!.if*` macro that basically expands to this.
I know it's a special form in other Lisps (or cond is),
but Hissp doesn't need it. Smalltalk pretty much does it this way.
Once you have `if` you can make a `cond`. Lisps actually differ on which
is the special form and which is the macro.

* Does Hissp have tail-call optimization?

No but you can increase the recursion limit with `sys/setrecursionlimit`.
Better not increase it too much if you don't like segfaults, but
you can trampoline instead. See Drython's `loop()` function. Or use it.
Clojure does it about the same way.

* How do I make a tuple?

Use `tuple()`.

* But it has to already be an iterable. There's no `cons` or `list*`.

`lambda *a:a`

You can also make an empty list with `[]` or `(list)`, and then `.append` to it.
Finally, the template syntax makes tuples. Unquote as needed.

## Contributing
There are many ways to contribute to an open-source project,
even without writing code.

Questions are allowed on the issue tracker,
they help illustrate deficiencies in our documentation,
but do check there first!

Bug reports are welcome.

PRs to help improve documentation, structure, or compatibility will also be considered.

### Disputes
To encourage participation,
we strive to maintain an environment conducive to cooperation and
collaborative effort. To that end, note that
GitHub's acceptable use and conduct restrictions apply to this repo as well.
Spamming, doxing, harrassment, etc. will not be tolerated.
Belligerent users may be blocked at the discretion of the project
maintainer, even on the first offense.
Issues that become heated or veer too far off topic may be closed or locked.

Software Engineers are an eccentric bunch who come from various
generational and world cultures.
Tone is notoriously hard to convey in writing and for many English is
not their first language.
Therefore, before you reply in anger, please
[assume good faith](https://en.wikipedia.org/wiki/Wikipedia:Assume_good_faith)
until there is very obvious evidence to the contrary.
Discussion here should be focused on the project, not on each other.

While consensus is preferable,
the maintainer is the final arbiter for the project.
If you disagree with his decision,
you may always make a fork as permitted by the LICENSE.
Just don't call it Hissp (see section 6 of the LICENSE).

### Patches
PRs must be aligned with the philosophy and goals of the project to be
considered for inclusion.

Note section 5 of the LICENSE.
You must have the legal rights to the patch to submit them under those terms:
either you own the copyright
(e.g. because you are the author of the patch and it was not a work for hire)
or have appropriate license to do it.

The git repository itself will normally suffice as a record of
authorship for copyright purposes.
Don't update the original boilerplate notices on each file.
But commits authored by or owned by someone else must be clearly labeled as such.
We may maintain a NOTICE file per section 4.(d) of the LICENSE if needed.

