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
