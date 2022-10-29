.. Copyright 2020, 2021, 2022 Matthew Egan Odendahl
   SPDX-License-Identifier: CC-BY-SA-4.0

===========
Style Guide
===========

Why have a style guide?

Code was made for the human, not only for the machine,
otherwise we'd all be writing programs in binary.
Style is not merely a matter of aesthetics.
Consistency lifts a burden from the mind, and,
with experience, improves human performance.
Style is a practical matter.

Code is written once, and rewritten many times.
It is *read* much more than it is written,
and often by multiple individuals,
so it is that much more important to make code easy to read and edit than to write.

To the uninitiated, Lisp is an unreadable homogenous ball of mud.
Lots of Irritating Superfluous Parentheses. That's L.I.S.P.
*How can anyone even read that?*

Consistency. Experience.
I'll let you in on the secret:

   *Real Lispers don't count the brackets.*

It's true.

Don't Count the Brackets
========================

It is impossible for the human to comprehend the code of a nontrivial program in totality;
working memory is too small.
We handle complexity by chunking it into hierarchies of labeled black boxes within boxes within boxes.
Mental recursive trees.

But syntax trees are the very essence of Lisp,
and you understand them in the same hierarchical way.
There are, of course, many more layers of abstractions below Hissp,
but at the bottom of Hissp's hierarchy are tuples of atoms.
Conceptually, it's a box with a label and contents.

.. code-block:: Text

   LABEL item1 item2 ...

Order matters in Hissp,
and repeats are allowed.
Mathematically speaking, these boxes are *tuples*,
not just sets.
The first element is the label.
The rest are contents.

When it gets complicated is when the items are themselves boxes.
How do we keep that readable?

Why, the same way we do in Python, of course: indentation.

If your code is properly formatted,
you will be able to delete all the trailing brackets
and unambiguously reconstruct them from indentation alone.

Given code like this,

::

   (define fib
     (lambda (n)
       (if-else (le n 2)
         n
         (add (fib (sub n 1))
              (fib (sub n 2))))))

this is what the experienced human sees.

::

   (define fib
     (lambda (n
       (if-else (le n 2
         n
         (add (fib (sub n 1
              (fib (sub n 2

Learn to see it that way.
There is no missing information.

While the following will compile fine,
if you write it this way,

::

   (define fib(lambda(n)(if-else(
   le n 2)n(add(fib(
   sub n 1))(fib(sub n 2)))))

the uninitiated might not care
(because it took them great effort to read it anyway),
but you will make the experienced humans angry.
It's like trying to read minified JavaScript.
You can maybe do it, but it's tedious.

Just kidding!
This doesn't really compile because the parentheses are not balanced.
You didn't notice, did you?
You didn't count them.
I left one off to prove a point:
The bracket trails are there for the computer, not the human.
It's much easier to program a parser to read brackets than indentation.

While surprisingly controversial,
I feel that making the computer read the structure via indentation like the human does,
instead of via a parallel language written with brackets,
is one of the things that Python got right.
With a bracketed language,
on the other hand,
these two delimiters can get out of sync,
and the human and computer no longer agree on the meaning of the code.

To some extent, this is a criticism that applies to any language with bracketed code blocks,
but it's especially bad for Lisp,
which is so syntactically regular
that it has almost no other cues that could compensate for bad indentation.
That's the "ball of mud".
For Lisp, proper indentation is not just best practice,
it's an absolute necessity for legibility.

Unlike Python,
with Lisp,
you have to take on the extra responsibility to keep these two block delimiters in sync.
This is hard to do consistently without good editor support.
But *because* the brackets make it easy to parse (for a computer),
editor support for Lisp is really very good.
Emacs can do it, but it's got a bit of a learning curve.
For a beginner, try installing `Parinfer <https://shaunlebron.github.io/parinfer/>`_
in a supported editor, like `Atom <https://atom.io/packages/parinfer>`_.
If you get the indent right, Parinfer will manage the trails for you.
Parinfer makes editing Lisp feel more like editing Python.

Lisp style guides are hard to find online,
because most Lispers will simply tell you to let Emacs handle it.
While I strongly recommend using editor support for Lissp files,
Hissp is a modular system.
You might need to format raw Hissp in readerless mode,
or Lissp embedded in a string
or notebook cell
or documentation
or comment on some web forum,
or maybe you're one of those people who insists on programming in Notepad.
Or maybe you want to write one of these editor tools in the first place.
For these reasons,
I feel the need to spell out what good indentation looks like
well enough that you could do it by hand.

The only absolute rules are

- Don't Dangle Brackets
- Unambiguous Indentation

If you break these rules,
Parinfer can't be used.
Team projects with any Lissp files should be running
`Parlinter <https://github.com/shaunlebron/parlinter>`_
along with their tests to enforce this.
Basic legibility is not negotiable. Use it.

Don't Dangle Brackets
---------------------

Trailing brackets are something we try to ignore.
Trailing brackets come in trains.
They do not get their own line;
that's more emphasis than they deserve.
They don't get extra spaces either.

.. code-block:: Lissp

   ;; Wrong.
   (define fib
     (lambda (n)
       (if-else (le n 2)
         n
         (add (fib (sub n 1)
               )
              (fib (sub n 2)
               )
         )
       )
     )
   )

   ;; Still wrong.
   ( define fib
     ( lambda ( n )
       ( if-else ( le n 2 )
         n
         ( ..add ( fib ( sub n 1 ) )
                 ( fib ( sub n 2 ) ) ) ) ) )

This also goes for readerless mode.

.. code-block:: Python

   # Very wrong.
   (
       "define",
       "fib",
       (
           "lambda",
           ("n",),
           (
               "ifQz_else",
               ("operator..le", "n", 2),
               "n",
               (
                   "operator..add",
                   ("fib", ("operator..sub", "n", 1)),
                   ("fib", ("operator..sub", "n", 2)),
               ),
           ),
       ),
   )

If you're using an auto formatter that isn't aware of Hissp,
you may have to turn it off.

.. code-block:: Python

   # Right.
   # fmt: off
   ('define','fib',
     ('lambda',('n',),
       ('ifQz_else',('operator..le','n',2,),
         'n',
         ('operator..add',('fib',('operator..sub','n',1,),),
                          ('fib',('operator..sub','n',2,),),),),),)
   # fmt: on

Note also that tuple commas are used as terminators,
not separators,
even on the same line.
This is to prevent the common error of forgetting the required trailing comma for a monuple.
If your syntax highlighter can distinguish ``(x)`` from ``(x,)``, you may be OK without it.
But this had better be the case for the whole team.

Unambiguous Indentation
-----------------------

A new line's indentation level determines which tuple it starts in.
Go past the parent's opening bracket, not the sibling's.

.. code-block:: Lissp

   (a (b c))
   x                                      ;(a (b c)) is sibling

   (a (b c)
      x)                                  ;(a is parent, (b c) is sibling

   (a (b c
         x))                              ;(b is parent, c is sibling

Even after deleting the trails, you can tell where the ``x`` belongs.

::

   (a (b c
   x

   (a (b c
      x

   (a (b c
         x


.. Caution::

   **Indent with spaces only.**
   Because indents have to be between parent and sibling brackets,
   lines in Lisp may have to start on *any column*, therefore,
   *Lisp cannot be indented properly with tabs alone.*
   There are arguments to be made for using tab indents in other languages,
   but they mostly don't apply to Lisp.
   You *have to* use spaces.
   It's possible to reach any column using an invisible mix of tabs and spaces,
   but indentation can't be called "unambiguous"
   if no-one can agree on the width of their tab stops!
   Tab indents are already considered bad practice in Python and in other Lisps,
   but to pre-empt this kind of problem,
   it's not just a matter of style in Lissp—**it's a syntax error.**
   If you run into these, check your editor's configuration.

The rule is to pass the parent *bracket*.
You might not pass the head *atom* in some alignment styles.

.. code-block:: Lissp

   (foo (bar x)
     body)                                ;(foo is parent, (bar x) is special sibling

   (foo (bar x
          body))                          ;(bar is parent, x is special sibling

We can still unambiguously reconstruct the trails from the indent.

::

   (foo (bar y
     body

   (foo (bar y
          body

Note that a multiline string is still an atom.

.. code-block:: Lissp

   (foo (bar "abc
   xyz"))

   (foo (bar)
        "abc
   xyz")

   (foo (bar #"\
   abc
   xyz"))

   (foo (bar)
        #"\
   abc
   xyz")

We can still unambiguously reconstruct the trails.

.. code-block:: Lissp

   (foo (bar "abc
   xyz"

   (foo (bar
        "abc
   xyz"

   (foo (bar #"\
   abc
   xyz"

   (foo (bar
        #"\
   abc
   xyz"

The ``"`` is not a bracket,
so we don't delete it or ignore it.

Alignment Styles
================

The remaining rules are more a matter of that *practical consistency*.
Exactly what rules *implement* that consistency matter much less
than the consistency itself.
Know what the rules are for
so you know when to break them.
Sometimes differences of opinion come down to taste.
Use your best judgement;
it's not always black and white.
But not all shades of gray are the same either.

Lisp is one of the oldest programming languages in common use.
It has splintered into many dialects (Lissp among them),
with a common culture, but without perfect agreement in all details.
Lissp's recommended style is based on these,
with some small modifications for its own unique features.

Tuples
------

Separate *top level* forms from each other with a single blank like,
unless they are very closely related.

.. _top level:

Top Level
  Not nested inside another form.
  "Top" here means the top of the syntax tree,
  not the top of the file.

Try to avoid blank lines within forms.
You may need them for separating groups whose elements span lines
or to separate methods in long classes.
This is a code smell indicating your form may be too complex.
You can use comment lines to separate internal groups instead,
but consider refactoring.
Blank lines are OK in docstrings.

Keep the elements in a tuple aligned to start on the same column.
Treat sibling groups equally:
If you add a line break for one group,
then put all of its sibling groups on their own line as well.
Keep items within implied groups (like kwargs) together.
Control words used as labels should be grouped with what they label.
Your code should look like these examples, recursively applied to subforms:

.. code-block:: Lissp

   '(data1 data2 data3)                   ;Treat all data items the same.

   '(data1                                ;Line break for one, break for all.
     data2                                ;Items start on the same column.
     data3)

   '(                                     ;This is better for linewise version control.
     data1                                ; Probably only worth it if there's a lot more than 3,
     data2                                ; or it changes frequently. Use this style sparingly.
     data3
     _#/)                                 ;Trails NEVER get their own line.
                                          ; But you can hold it open with a discarded item.

   (function arg1 arg2 arg3)              ;Typical for calls that fit on one line.

   ;; Also common. The function name is separate from the arguments in this style.
   (function arg1                         ;Break for one, break for all.
             arg2                         ;Args start on the same column.
             arg3)

   ;; The previous alignment is preferred, but this is OK if a line would be too long.
   (function
    arg1                                  ;Just like data.
    arg2
    arg3)

   ((lambda (a b c)
      (reticulate a)
      (frobnicate a b c))
    arg1                                  ;The "not past the sibling" rule is absolute.
    arg2                                  ; Not even one space past the (lambda.
    arg3)

   (function                              ;Acceptable, but unusual.
    arg1 arg2 arg3)

   ((lambda (a b c)
      (print c b a))
    arg1 arg2 arg3)                       ;Break for all args or for none.

   ;; One extra space between pairs.
   (function arg1 arg2 : kw1 kwarg1  kw2 kwarg2  kw3 kwarg3)

   ;; This might make the reason a bit more obvious:
   (% 1 0 2 9 3 8 4 7 5 6)                ;Bad. Can't tell keys from values.

   (% 1 0  2 9  3 8  4 7  5 6)            ;Preferred. Group implied pairs.

   (% 1 0                                 ;OK, but could have fit on one line.
      2 9
      3 8
      4 7
      5 6)

   (%                                     ;Also OK.
    1 0
    2 9
    3 8
    4 7
    5 6)

   (function arg1 arg2
             : kw1 kwarg1  kw2 kwarg2)    ;Breaking groups, not args.

   (function arg1
             arg2
             : kw1 kwarg1                 ;The : starts the line.
             kw2 kwarg2)                  ;Break for args, but pairs stay together.

   (function : kw1 kwarg1                 ;The : starts the "line". Sort of.
             kw2 kwarg2)

   ;; The previous alignment is preferred, but this is OK if the line would be too long.
   (function
    arg1
    arg2
    :
    kw1
    kwarg1
                                          ;Break for everything, and extra line to separate pairs.
    kw2
    kwarg2)

   (macro special1 special2 special3      ;Macros can have their own alignment rules.
     body1                                ; Simpler macros may look the same as functions.
     body2                                ; Special/body is common. Lambda is also like this.
     body3)                               ; Body is indented 1 extra space.

   (macro special1 body1)

   (macro special1
          special2
          special3
     body1
     body2
     body3)

   ;; Without any positional-only parameters, there's no need for :/ at all, so it groups left.
   (lambda (pos1 :/
            param1
            param2
            ;; Without any pairs, there's no need for : at all, so it groups right.
            : default value1
            default2 value2)
     body)

   ;; Same structure as above, but written with only pairs.
   (lambda (: pos1 :?
            :/ :?
            param1 :?
            param2 :?
            default value1
            default2 value2)
     body)

   ;; Parameter groups are separated by lines. Pairs are separated by extra space.
   (lambda (a b :/                        ;positional-only group
            c d                           ;normal group
            : e 1  f 2                    ;colon group
            :* args  h 4  i :?  j 1       ;star group
            :** kwargs)                   ;kwargs
     body)

Readerless style is similar:

.. code-block:: Python

   ('function','arg1','arg2',
               ':','kw1','kwarg1', 'kw2','kwarg2',)

Alignment styles can be bent a little in the interest of readability,
especially for macros, but even for calls,
as long as the two absolute rules are respected.

For example, this ``enjoin`` function

.. code-block:: Lissp

   (define enjoin en#X#(.join "" (map str X)))

builds a string from multiple arguments.

Omitting spaces between atoms and having a variable number per line is acceptable here,
because the string's structure is more important for readability than the tuple's.

.. code-block:: Lissp

   (enjoin                                ;Preferred.
     "Weather in "location" for "date" will be "weather"
    with a "percent"% chance of rain.")

   (enjoin "Weather in "                  ;OK.
           location
           " for "
           date
           " will be "
           weather
           "
     with a "                             ;OK, but would look better with \n.
           percent
           "% chance of rain.")

Exactly where the implied groups are can depend on the function's semantics,
not just the fact that it's a call.

.. code-block:: Lissp

   (enter (wrap 'A)                       ;Stacked context managers.
    enter (wrap 'B)                       ; enter is from the prelude.
    enter (wrap 'C)
    (lambda abc (print a b c)))

   (engarde `(,FloatingPointError ,ZeroDivisionError) ; engarde from prelude
            print
            truediv 6 0)                  ;(truediv 6 0) is a deferred call, so groups.

   (.update (globals) :                   ;OK. Easier for linewise version control.
    + operator..add
    - operator..sub
    * operator..mul
    / operator..truediv
    _#/)

   (.update (globals)                     ;Preferred. Standard style.
            : + operator..add
            - operator..sub
            * operator..mul
            / operator..truediv)

Strings
-------

Multiline strings can mess with alignment styles.
Strings are atoms, so this won't affect Parinfer,
but it can impact legibility.
For short strings in simple forms,
don't worry too much, but consider using ``\n``.

For deeply nested multiline string literals,
consider indenting the string contents in combination with `textwrap.dedent`.
The run-time overhead is usually negligible,
but in case it matters,
this can be done at read time instead:

.. code-block:: REPL

   #> (print (.upper '.#(textwrap..dedent #"\
   #..                   These lines
   #..                   Don't interrupt
   #..                   the flow.")))
   >>> print(
   ...   "These lines\nDon't interrupt\nthe flow.".upper())
   THESE LINES
   DON'T INTERRUPT
   THE FLOW.

Because the string was injected (``.#``),
don't forget to quote it (``'``),
or the compiler will inject the string contents as Python code.

With the principal exception of docstrings,
long multiline strings should be declared at the `top level`_ and referenced by name.

.. code-block:: Lissp

   (define MESSAGE #"\
   These lines
   don't interrupt
   the flow either.
   But, a really long string would be
   longer than this one.
   ")

   (deftype MessagePrinter ()
     __doc__ "It is safe
             to align docstrings.
             "
     display (lambda (self)
               (print MESSAGE)))

Indent any multiline docstring to match its opening quote,
including the closing quote.
Put the closing quote for any multiline docstring on its own line.
(Pydoc automatically strips indents.)

Comments
--------

Headings are in ``Title Case``,
and begin with four semicolons and a space ``;;;; Foo Bar``.
Subheadings begin with three semicolons and a space ``;;; Foo Bar``.

Headings are for the `top level`_ only; they aren't nested in forms;
they get their own line and start at the beginning of it.
They have a blank line before (unless it's the first line) and after.
They organize the code into sections.

Comments about the next form (or group) begin with two semicolons and a space ``;; x``,
and are indented to align as if they were forms,
and are not followed by a blank line.

Comments about a line begin with one semicolon and a space ``; x``,
starting one space after the code. They never get their own line.

Margin comments begin with one semicolon ``;x``.
The semicolon must be aligned with spaces to rest on column 40,
or one space after the code, whichever is greater.
The semicolon is not followed by a space unless it continues a margin
comment from the previous line.
Margin comment continuations may have their own line.

**Never** put a single-semicolon comment on its own line unless
it's a continuation aligned to the margin!
Experienced Lispers set their editors to automatically indent these to column 40.
You will make them angry when they have to fix all your comments.

Complete sentences should start with a capital letter and end with
a punctuation mark (typically a full stop or question mark).
Short comments need not be complete sentences.
Use the discard macro ``_#`` on a string for long block comments.

Commented-out code does not belong in version control,
but it can be helpful to turn things off during development.
You can use the discard macro to comment out code structurally.
You can use ``;;`` at the start of each line to comment out multiple forms at once.

.. code-block:: Lissp

   "Comments example.

   Prefer to use docstrings like this one over comments when applicable.
   Docstrings are always indented with their containing form, including
   their contents, wrap at column 72, and, if multiline, their closing
   quote has its own line. Use reStructuredText markup in docstrings.
   "

   ;;;; Heading

   _#"Long Exposition about this section. Wrap at column 72.

   Lorem ipsum dolor sit amet, consectetuer adipiscing elit.  Donec
   hendrerit tempor tellus.  Donec pretium posuere tellus.  Proin quam
   nisl, tincidunt et, mattis eget, convallis nec, purus.  Cum sociis
   natoque penatibus et magnis dis parturient montes, nascetur ridiculus
   mus.
   "

   ;;; Subheading

   ;; comment about macro
   (macro special1
          ;; comment about special2 group
          : special2a special2b
          special3 ; comment about special3 line
          special4 ; entirely separate comment about special4 line
     body1
     ;; comment about body2
     body2                                ;Margin comment
     body3)                               ; continuation thereof,
                                          ; and more continuation on its own line.

Docstrings can use some other markup format if the whole team can agree on one,
and it's done for the entire project.
But reStructuredText is the default in the Python ecosystem.
You can automatically generate API documentation with these.

Reader Macros
-------------

Reader macros should not be separated from each other
or from their primary argument with whitespace.

.. code-block:: Lissp

   ' builtins..repr# .# (lambda :)        ;Bad.
   'builtins..repr#.#(lambda :)           ;Preferred.

However, if a primary argument spans multiple lines,
it's acceptable to separate with a newline,
but be careful not to accidentally put a comment in between,
unless you explicitly discard it.

.. code-block:: Lissp

   _# ; Bad. Comments are valid reader macro arguments!
   ((lambda abc                           ;This wasn't discarded!
      (frobnicate a b c))
    arg)

   _#
   ;; Bad. This comment would have been discarded anyway.
   ((lambda abc                           ;But this wasn't discarded!
      (frobnicate a b c))
    arg)

   _#_#
   ;; OK. This actually works.
   ((lambda abc                           ;This was discarded too.
      (frobnicate a b c))
    arg)

   ;; OK. Put the tag after the comment on its own line.
   _#
   ((lambda abc
      (frobnicate a b c))
    arg)

   _#((lambda abc
      (frobnicate a b c))                 ;Bad. Wrong indentation!
    arg)

   _#((lambda abc                         ;Preferred. No separation, good indents.
        (frobnicate a b c))
      arg)

   ;; OK. Composed macros can group. Primary spanned multiple lines.
   `',
   ((lambda abc
      (frobnicate a b c))
    arg)

   `',((lambda abc                        ;Preferred. No separation.
         (frobnicate a b c))
       arg)

Extras may always be separated,
but only imply groups of extras with whitespace if they are semantically grouped.

.. code-block:: Lissp

   builtins..int#!6 .#"21"                ;Preferred. Spacing not required.
   builtins..int# !6 "21"                 ;OK. Extras may always be separated.

   'foo#!(spam)!(eggs)bar                 ;Preferred. Spacing not required.
   'foo# !(spam) !(eggs) bar              ;OK. Extras may always be separated.
   'foo# !(spam)!(eggs) bar               ;Bad if grouping not meaningful.
   'foo#!(spam) !(eggs) bar               ;Same.

You can also imply groups by stacking bangs,
but no more than three in a row.

.. code-block:: Lissp

   builtins..dict# !: !foo !2  !bar !4 () ;OK. Grouped by extra space.
   builtins..dict#!: !foo!2 !bar!4()      ;Bad. {'fooQzBANG_2': 'barQzBANG_4'}
   builtins..dict# !!!: foo 2 !! bar 4 () ;OK. Meaningful breaks, no more than !!!.
   builtins..dict#!: !!foo 2 !!bar 4()    ;Preferred. Pairs grouped by stacking.
   builtins..dict#!!!!!: foo 2  bar 4  () ;Bad. Have to count bangs.

Align extras spanning lines like tuple contents.

.. code-block:: Lissp

   ;; Extras aligned with the first extra.
   <<#!;C:\bin
      !;C:\Users\ME\Documents
      !;C:\Users\ME\Pictures
   ";"                                    ;Primary isn't an extra. Aligned with tag.

   ;; Extras aligned with the first extra.
   (exec
     <<#
     !;for i in 'abc':
     !;    for j in 'xyz':
     !;        print(i+j, end=" ")
     !;print('.')
     !;
     #"\n")

   ;; Indent recursively.
   foo#!;spam
       !bar#!;sausage
            !;bacon
       :tomato
       !;eggs
   :beans

   ;; Don't dangle brackets!
   (print <<#;Hello, World!
          _#/)

Identifiers
===========

If you're writing an API that's exposed to the Python side,
avoid unpythonic identifiers
(including package and module names)
in the public interface.
Use the `naming conventions from PEP 8. <https://www.python.org/dev/peps/pep-0008/#naming-conventions>`_

``CapWords`` for class names.

``snake_case`` for functions,
and that or single letters like ``A`` or ``b``
(but never ``l`` ``O`` or ``I``) for locals,
including kwargs.

``UPPER_CASE`` for "constants".

Name the first method argument ``self``
and the first classmethod argument ``cls``.
Python does not enforce this,
but it's a very strong convention.

For internal Lissp code,
Python conventions are fine,
but the munger opens up more characters.
Something like ``*FOO-BAR*`` is a perfectly valid Lissp identifier,
but it munges to ``QzSTAR_FOOQz_BARQzSTAR_``,
which is awkward to use from the Python side.

Even in private areas,
let the munger do the munging for you.
Avoid writing anything in the Quotez style yourself.
(This can confuse the demunger and risks collision with compiler-generated names like gensyms.)

Docstrings use reStructuredText markup, like Python.

Anaphoric or code string–injection macros are potential gotchas if you don't know this,
so docstrings for them should include the word "Anaphoric" or "Injection" up front.
Anaphoric macro docstrings should also state what the anaphors are,
named in doubled backticks.

Any docstring for something with a munged name
should start with the demunged name in doubled backticks
(this includes anything with a hyphen).

.. code-block:: Lissp

   "``the#`` Anaphoric. Let ``the`` be a fresh `types.SimpleNamespace`
   in a lexical scope surrounding ``e``.
   "

The demunged names should be followed by the pronunciation in single quotes,
if it's not obvious from the identifier.

.. code-block:: Lissp

   "``&&`` 'and'. Like Python's ``and`` operator, but for any number of arguments."

This way, all three name versions (munged, demunged, and pronounced)
will appear in generated docs.

Method Syntax vs Attribute Calls
--------------------------------

Often, code like ``(.foo bar spam eggs)``
could also be written like ``(bar.foo spam eggs)``.
In some cases, the choice is clear,
because they compile differently,
but in others, these would compile exactly the same way.
Which is preferred then depends on whether ``bar`` is a namespace or an argument.

For a namespace, prefer ``bar.foo``.
Internal use of ``self`` in methods and ``cls`` in classmethods,
is also more namespace than argument.
For an argument, i.e. other method calls, prefer ``.foo bar``.

.. code-block:: Lissp

   (_macro_.define greeting "hi")         ;Compiler Macro
   (.define _macro_ 'greeting '"hi")      ;Run-time expansion.

   ;;; Arguments

   (.upper "hi")                          ;Preferred.
   ("hi".upper)                           ;SyntaxError

   (.upper greeting)                      ;Preferred.
   (greeting.upper)                       ;Bad.

   ;;; Namespaces

   (tkinter..Tk)                          ;Preferred.
   (.Tk tkinter.)                         ;Bad.

   ;;; Kind of Both

   (self.foo spam eggs)                   ;Preferred.
   (.foo self spam eggs)                  ;OK.

   (cls.foo spam eggs)                    ;Preferred.
   (.foo cls spam eggs)                   ;OK.

   ;; self as namespace, self.accumulator as argument
   (.append self.accumulator x)

The End of the Line
===================

Ending brackets should also end the line.
That's what lets us indent and see the tree structure clearly.
It's OK to have single ``)``'s inside the line,
but don't overdo it.

.. code-block:: Lissp

   (lambda (x) (print "Hi" x) (print "Bye" x)) ;OK.

   (lambda (x)                            ;Preferred.
     (print "Hi" x)
     (print "Bye" x))

Don't put a train of ``)``'s inside the line,
because then we'd have to count brackets!

If the train is trailing at the end of the line,
then the tree structure is clear from the indents.

.. code-block:: Lissp

   (print (/ (sum xs) (len xs)) "on average.") ;Bad. Internal ))'s.

   (print (/ (sum xs) (len xs))           ;OK. One internal ) though.
          "on average.")

   (print (/ (sum xs)                     ;Preferred. )'s end the line.
             (len xs))
          "on average.")

Implied groups should be kept together.
Closing brackets inside a pair can happen in `cond`,
for example.

.. code-block:: Lissp

   (lambda (x)                            ;Preferred.
     (cond (lt x 0) (print "negative")
           (eq x 0) (print "zero")
           (gt x 0) (print "positive")
           :else (print "not a number")))

A train of ``)``'s must not appear inside of a line,
even in an implied group.

.. code-block:: Lissp

   (define compare                        ;Bad. Internal ))'s.
     (lambda (xs ys)
       (cond (eq (len xs) (len ys)) (print "0")
             (lt (len xs) (len ys)) (print "<")
             (gt (len xs) (len ys)) (print ">"))))

   (define compare                        ;Bad. Pairs not grouped.
     (lambda (xs ys)
       (cond (eq (len xs) (len ys))
             (print "0")
             (lt (len xs) (len ys))
             (print "<")
             (gt (len xs) (len ys))
             (print ">"))))

   (define compare                        ;OK, but the empty lines smell.
     (lambda (xs ys)
       (cond (eq (len xs)
                 (len ys))
             (print "0")
             ;;
             (lt (len xs)
                 (len ys))
             (print "<")
             ;;
             (gt (len xs)
                 (len ys))
             (print ">"))))

   (define compare                        ;Preferred. Keep cond simple.
     (lambda (xs ys)
       (let (lxs (len xs)
             lys (len ys))
         (cond (eq lxs lys) (print "0")
               (lt lxs lys) (print "<")
               (gt lxs lys) (print ">"))))))

