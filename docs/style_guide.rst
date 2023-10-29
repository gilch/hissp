.. Copyright 2020, 2021, 2022, 2023 Matthew Egan Odendahl
   SPDX-License-Identifier: CC-BY-SA-4.0

Style Guide
###########

Why have a style guide?

Code was made for the human, not only for the machine,
otherwise we'd all still be writing programs in binary.
Style is not merely a matter of aesthetics.
Consistency lifts a burden from the mind, and,
with experience, improves human performance.
Style is a practical matter.

Code is written once, and rewritten many times.
It is *read* much more than it is written,
and often by multiple individuals,
so making code easy to read and edit is that much more important than making it easy to write.
Learning style is as much about learning to *read* code as it is about learning to write it.

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

Given code like this, ::

   (define fib
     (lambda (n)
       (if-else (le n 2)
         n
         (add (fib (sub n 1))
              (fib (sub n 2))))))

this is what the experienced human sees. ::

   (define fib
     (lambda (n
       (if-else (le n 2
         n
         (add (fib (sub n 1
              (fib (sub n 2

Learn to see it that way.
There is no missing information.

While the following will compile fine,
if you write it this way, ::

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
in a supported editor, like `Pulsar <https://web.pulsar-edit.dev/packages/parinfer>`_.
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
:::::::::::::::::::::

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

Unambiguous Indentation
:::::::::::::::::::::::

A new line's indentation level determines which tuple it starts in.
Go past the parent's opening bracket, not the sibling's.

.. code-block:: Lissp

   (a (b c))
   x                                      ;(a (b c)) is sibling

   (a (b c)
      x)                                  ;(a is parent, (b c) is sibling

   (a (b c
         x))                              ;(b is parent, c is sibling

Even after deleting the trails, you can tell where the ``x`` belongs. ::

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

We can still unambiguously reconstruct the trails from the indent. ::

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
But don't make the worse mistake of thinking there's only one shade of gray ;)

Lisp is one of the oldest programming languages in common use.
It has splintered into many dialects (Lissp among them),
with a common culture, but without perfect agreement in all details.
Lissp's recommended style is based on these,
with some small modifications for its own unique features.

Tuples
::::::

By default, separate *top level* forms from each other with a single blank like.
Don't use multiple blank lines in succession.
When greater separation is required, use comments.

.. _top level:

Top Level
  Not nested inside another form.
  "Top" here means the top of the syntax tree,
  not the top of the file.

Small and closely-related forms may be semantically "attached" to the next
or previous form by omitting the usual blank line.
E.g., several one-line "constant" `define` forms making up a conceptual group need not be separated;
one only used by the following definition may be attached to it;
a form modifying the previous (e.g. decorating, attaching attributes),
or adding it to a collection may be attached to it.

However, in many of these cases,
the groups could be written as a single top-level form insead,
given the appropriate functions or macros.
E.g. `dict.update` (on `globals`), `let`, `@#!<QzAT_QzHASH_>`, `attach`, `doto`.

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
The main idea here is that you can imply groups with whitespace
and should not imply groupings that are not meaningful.

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
                                          ; The / is the usual choice in Lissp, reminiscent of XML.

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
    ;;                                    ;Break for everything, and ;; line to separate pairs.
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

   ;; Group control words with the things they label.
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

   ('function','arg1','arg2'
              ,':','kw1','kwarg1', 'kw2','kwarg2',)

Note the space between 'kwarg1' and 'kw2' used to imply groups,
which is absent after the other commas in the tuple.

If you're using a full-file formatter that isn't aware of Hissp,
you may have to turn it off in places.

.. code-block:: Python

   # fmt: off
   ('define','fib'
    ,('lambda',('n',)
      ,('ifQz_else',('operator..le','n',2,)
        ,'n'
        ,('operator..add',('fib',('operator..sub','n',1,),)
                         ,('fib',('operator..sub','n',2,),),),),),)
   # fmt: on

There are a few things to note about tuple commas in readerless.
The last element always ends with one (commas are used as terminators,
not separators),
even on the same line.
This is to prevent the common error of forgetting the required trailing comma for a monuple.
If your syntax highlighter can distinguish ``(x)`` from ``(x,)``, you may be OK without it.
But this had better be the case for the whole team and project.
Be consistent.

Also note that in this example the tuple commas did not end the line,
but rather started the next one.
In the case of the ``ifQz_else`` macro,
this gave the body the proper one-column indent it would have had in Lissp.
In the case of the ``operator..add`` function,
this aligned the arguments.
Linewise edits and indentation are also more consistent this way.

Commas are not followed by a space except to imply groups (when an extra space would be used in Lissp).
In cases where there wouldn't be any whitespace groupings in Lissp,
the commas would end the line in readerless Hissp as well.

.. code-block:: Python

   ('quote'
    ,('some rather excessively long data',
      'and some more',
      'and a little more after that making the data tuple too long to fit on one line',),)

.. _enjoin:

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
    enter (wrap 'B)                       ; Note pairs.
    enter (wrap 'C)                       ; `enter` is from the prelude.
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
:::::::

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
or the compiler will assume the string contents are Python code to be inlined.

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

Comment Styles
::::::::::::::

Avoid adding superfluous "what"-comments that are obvious from looking at the code.
(Except perhaps when writing beginner documentation ;)

Prefer "why"-comments that describe rationale or intent.

.. code-block:: Lissp

   "Comments Example

   Prefer to use docstrings like this one over comments when applicable.
   Docstrings are indented with their containing form, including their
   contents, wrap at column 72, and, if multiline, their closing quote
   has its own line. Use reStructuredText markup in docstrings.
   "

   ;;;; ** Decorated Major Section Heading **
   ;;;  ***

   ;;; Long Exposition about this section. Wrap at column 72.

   ;;; This example has the more typical two-level heading scheme.
   ;;; The major heading above is made emphatic with stars around and
   ;;; underlining. The minor heading below is undecorated. (The whole-
   ;;; file title is in the module docstring in this case, not a comment.)

   ;;;; Undecorated Minor Subsection Heading

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

Complete sentences should start with a capital letter and end with
a punctuation mark (typically a full stop or question mark).
Separate sentences with a single space.
Short comments need not be complete sentences.

Inline Comments ; X
+++++++++++++++++++

Comments about a line begin with one semicolon and a space ``; x``,
starting **one** space after the code.
They never get their own line,
but follow code on the same line.

This acceptable in Lissp, and closer to the Python style
(which would start *two* spaces after the code.
This also goes for readerless mode,
where, aside from occasionally being used to imply groups,
comment styles follow the same rules as normal Python.)
Lisp traditionally uses margin comments instead (as described below),
but this inline style is also common in Clojure.

Margin Comments ;X
++++++++++++++++++

Margin comments begin with one semicolon ``;x``.
The semicolon must be aligned with spaces to rest on column 40,
or one space after the code, whichever is greater.
(That's if you're using zero-based column indexing, like Emacs.
The semicolon goes on column 41 if you're counting columns starting from 1.)
The semicolon is not followed by a space unless it continues a margin
comment from the previous line.
Unlike inline comments,
margin comment continuation lines need not have code on their line.

Be careful with comments around detached reader tags!.
Comment tokens are normally discarded by the reader in Lissp,
but they are a valid target for reader macros,
in which case they may be treated as literal values.
Avoid using inline or margin comments as commentary between a tag and its target,
as this can cause errors when they are instead treated as arguments.
(Usually, tags are attached to their primary, so this doesn't come up,
but e.g. the bundled decorator macro `@#!<QzAT_QzHASH_>` typically is not.)
You may use a discarded string instead ``_#"NB foo"``.
A good syntax highlighter specialized for Lissp may be able to indicate when a comment token is not discarded,
but a traditional Lisp editor like Emacs ``lisp-mode`` would not.

In rare cases, a margin comment may occupy the same line as some other comment form.
This is usually acceptable style,
but a ``;`` following a ``;;`` is still tokenized as part of the ``;;`` block,
which can matter for reader macros like `<\<#<QzLT_QzLT_QzHASH_>`.

**Never** put a single-semicolon comment on its own line unless
it's a continuation aligned to the margin!
This one is about established tooling, not just taste.
Traditional Lisp editors automatically indent these to column 40,
and Lissp was designed to work with Emacs ``lisp-mode``.
If you break this rule, others will have to fix all your comments,
or reconfigure their editors to collaborate at all,
and then change them back when working on Lissp files with normal style.
That's not nice.

This includes comment tokens meant as arguments for reader macros!
Lissp parses comments in blocks,
so multiline comments used as reader arguments nearly always
use a form/group comment starting with two semicolons and a space as described below.
But with a single ``;``, they must follow code on the same line,
typically the reader tag itself, or an `Extra` macro ``!``.
In the rare case neither is valid,
precede with a discarded item ``_#: ;foo``.

Avoid using either margin or inline comments in any situation that would result in a dangling bracket.
It's not acceptable for the comment to follow the bracket either,
if the comment isn't about the whole tuple.
You may instead hold open the bracket with ``_#/)``,
convert the comment to a discarded string ``_#"NB foo")``,
or (if appropriate) use a form/group ``;;`` comment above the item, as described below.

;; Form/Group Comments
++++++++++++++++++++++

Comments about the next form (or group) begin with two semicolons and a space ``;; x``,
and are indented to align as if they were forms,
and are not followed by a blank line.

Commented-out code does not belong in version control,
but disabling code without deleting it can be helpful during development.
Use ``;;`` at the start of each line,
or use the discard macro ``_#`` to comment out code structurally.

Prefer class and function docstrings over ``;;`` comments where applicable.

;;; Top-Level Comments
++++++++++++++++++++++

Top-level commentary lines not attached to any form in particular
begin with three semicolons and a space ``;;; Foo Bar``.
Top-level comments are separated from code with a blank line.
They are not indented.

Standard usage for more than two semicolons varies with Lisp dialect,
but they are consistently ony for the `top level`_ and have no indent.

Some Lisp styles use triple and quadruple semicolons for headings and subheadings,
but differ on which is which.
To avoid confusion,
do not use triple-semicolon comments as headings at all.

Prefer module docstrings over top-level comments where applicable

;;;; Headings
+++++++++++++

Headings begin with four semicolons and a space ``;;;; Foo Bar``,
fit on one line,
and are written in ``Title Case`` by default.

Headings are for the `top level`_ only; they aren't nested in forms;
they get their own line and start at the beginning of it.
They have a blank line before (unless it's the first line) and after.
They organize the code into sections.

Headings can be decorated with symbol characters to make them more emphatic.

A Lissp file would typically be broken up into smaller modules before you need more than one or two heading levels.

But for a project distributed as a single large file,
you may want to develop a project style with more levels than that,
especially if you don't use classes to group functions.

Avoid using

- semicolons as underlines or other header decoration.
- more than four semicolons in a row.
  (This is sometimes seen in Emacs Lisp to indicate heading levels,
  but more than four semicolons in a row is too difficult to distinguish at a glance and must be counted.)
- overlines for emphasis.
  (An overline is commonly seen in reStructuredText headings.
  but it can obscure the heading text when folding code in some editors.)
- different underlining styles alone to distinguish levels.
  (Underlines are indistinguishable when folded.)
- inconsistent decorations.

Many levels are probably too rare to require a community (rather than project-level) standard,
but here's an example scheme with six levels.
(Six is enough for HTML, with H1-H6 tags.)

.. code-block:: Lissp

   ;;;; ## WHOLE FILE TITLE ##
   ;;;  ###

   ;;;; ** I. Heading Two **
   ;;;  ***

   ;;;; ++ I.A. Heading Three ++

   ;;;; -- I.A.1. Heading Four --

   ;;;; .. I.A.1.a. Heading Five ..

   ;;;; I.A.1.a.i. Heading Six

   ;;;; ** II. Folded H2 **...

The mnemonic here is that symbol characters that have more points (and use more ink) are more emphatic:
``#`` (8, H1); ``*`` (5 or 6, H2); ``+`` (4, H3); ``-`` (2, H4); ``.`` (1, H5); and H6 is undecorated.

Note that the underline decoration itself is not a heading,
and should not use four semicolons (but note the extra space).
This rule makes headings easier to find and count with a text search,
and makes it possible for tooling to display or manipulate them programmatically.
Three characters are sufficient to suggest an underline;
there is no need to match the length of the heading text
(but that is also a possible style).

The alphanumeric section outline numbering is not required,
but if you number sections at all,
it must be absolutely consistent with the heading level and position.
Tooling can help you here, even if it's just grep-and-check.
If you use outline numbering at all,
the decorations are not required to distinguish levels and may be omitted instead.

Start at the top and work your way down:
there should be only one H1 in a file (the title);
keep the H2's for your major sections;
and proceed in numerical order H3, H4, etc., without skipping any heading levels.
This will minimize the number of heading style changes you need to make if you later find that you need another level.
(This means that if you do not use all six levels, you will not have any undecorated H6's at all.)

_#_#_#The Discard Macro
+++++++++++++++++++++++

The discard macro ``_#`` applied to a string literal is acceptable for long block comments.

Several discard macros may be used in a row to comment out that many forms following them.

A discarded tuple may be used to contain scratch code during development
(but beware that discarded code is still *read*,
executing any reader macros).

As with line comments,
commented-out code does not belong in shared version control;
old versions should be in old commits.
Move the functionality you need to keep out of the comments or into scripts.
Move the experiments you want to keep running to assertions
(See `assure`, `unittest`, and `doctest`).

A discarded string with code following it in line is acceptable as commentary,
but use this style sparingly.
Include an arrow or NB (nota bene) in the string to make it clear this is a comment and not just disabled code.

.. code-block:: Lissp

   (print 1 2 _#"<- even number" 3 _#"also even ->" 4
          : sep : _#"NB Control words compile to strings!")

An extra space is typically used to imply separation between groups on the same line.
Where one level of grouping is not sufficient,
typically newlines,
then single ``;;`` lines indicate increasing levels of separation.
Avoid more than two spaces in a row for implying separation between groups in a line,
or more than one ``;;`` separator line in succession.
In rare cases where those aren't enough levels,
or newlines and ``;;`` lines would spread things out too much,
it is acceptable to additionally use discarded symbols like ``_#,``
within a line to indicate greater separation than the extra spaces.

"Docstrings"
++++++++++++

Prefer docstrings over comments where applicable.

Docstrings describe interface and usage;
they are not for irrelevant implementation details internal to their containing object.

"Private" helper functions/classes/modules (conventionally named with a leading underscore)
need not have docstrings at all,
but again prefer docstrings over comments when applicable,
in which case they describe an interface internal to their object's container,
but still do not their describe their object's implementation details.

The first expression of a module (if it compiles to a string literal) is its docstring.
Prefer this form over assigning the ``__doc__`` global directly.

The ``lambda`` special form does not create docstrings.
However, you can attach a ``.__doc__`` attribute to the lambda object after creating it,
e.g. using the `attach` macro.

The bundled `deftype` macro does not have any special case for docstrings.
Instead add a ``__doc__`` as its first key.

Indent docstrings to the same column as their opening ``"``
(or to the ``#`` in an opening ``#"``),
even when using something like the attach macro.
This does put the leading whitespace inside the string itself,
but Python tooling expects this in docstrings,
and can strip it out when rendering help.

If the docstring contains any newlines,
the closing ``"`` gets its own line.

It is acceptable to use reader macros that resolve to a string literal like `<\<# <QzLT_QzLT_QzHASH_>`
(which is useful for doctests),
as long as the documentation text is also legible in the source code.

Follow Python style on docstring contents.

While reStructuredText is currently the default in the Python ecosystem,
docstrings can use some other markup format if the whole team can agree on one,
and it's done for the entire project.
MyST Markdown also has pretty good support now.
You can automatically generate API documentation with these.

Anaphoric or code string–injection macros are potential gotchas.
Docstrings for them should include the word "Anaphoric" or "Injection" up front.
Anaphoric macro docstrings should also state what the anaphors are,
named in doubled backticks.

Any docstring for something with a munged name
should start with the demunged name in doubled backticks
(this includes anything with a hyphen).

.. code-block:: Lissp

   "``my#`` Anaphoric. Let ``my`` be a fresh `types.SimpleNamespace`
   in a lexical scope surrounding ``e``.
   "

The demunged names should be followed by the pronunciation in single quotes,
if it's not obvious from the identifier.

.. code-block:: Lissp

   "``&&`` 'and'. Like Python's ``and`` operator, but for any number of arguments."

This way, all three name versions (munged, demunged, and pronounced)
will appear in generated docs.

Reader Macros
:::::::::::::

Reader macros should not be separated from each other
or from their primary argument with whitespace.

.. code-block:: Lissp

   ' builtins..repr# .# (lambda :)        ;Bad.
   'builtins..repr#.#(lambda :)           ;Preferred.

Separating the tag with a space is acceptable when the primary starts with a ``|`` character,
because ``#|`` starts a block comment in other Lisp dialects.
Any editor not specialized for Lissp may get confused.
``#\|`` is an alternative.

If a primary argument spans multiple lines,
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

Extras may always be separated from the tag,
but only imply groups of extras with whitespace if they are semantically grouped.

.. code-block:: Lissp

   builtins..int#!6 .#"21"                ;Preferred. Spacing not required.
   builtins..int# !6 "21"                 ;OK. Extras may always be separated.

   'foo#!(spam)!(eggs)bar                 ;Preferred. Spacing not required.
   'foo# !(spam) !(eggs) bar              ;OK. Extras may always be separated.
   'foo# !(spam)!(eggs) bar               ;Bad if grouping not meaningful.
   'foo#!(spam) !(eggs) bar               ;Bad for the same reason.

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
   foo#!spam
       !eggs
       !ham
   bar                                    ;Primary isn't an extra. Aligned with tag.

   ;; Extras aligned with the first extra.
   foo#
   !spam
   !eggs
   !ham
   bar

   ;; Indent recursively.
   foo#!spam
       !bar#!sausage
            !bacon
       :tomato
       !eggs
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
Python naming conventions are still acceptable,
but the munger opens up more characters.
Something like ``+FOO-BAR+`` is a perfectly valid Lissp identifier,
but it munges to ``QzPLUS_FOOQz_BARQzPLUS_``,
which is awkward to use from the Python side.

Even in private areas,
let the munger do the munging for you.
Avoid writing anything in the Quotez style yourself.
(This can confuse the demunger and risks collision with compiler-generated names like gensyms.)

Method Syntax vs Attribute Calls
::::::::::::::::::::::::::::::::

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

   ;;;; Arguments

   (.upper "hi")                          ;Preferred.
   ("hi".upper)                           ;SyntaxError

   (.upper greeting)                      ;Preferred.
   (greeting.upper)                       ;Bad.

   ;;;; Namespaces

   (tkinter..Tk)                          ;Preferred.
   (.Tk tkinter.)                         ;Bad.

   ;;;; Kind of Both

   (self.foo spam eggs)                   ;Preferred.
   (.foo self spam eggs)                  ;OK.

   (cls.foo spam eggs)                    ;Preferred.
   (.foo cls spam eggs)                   ;OK.

   ;; self as namespace, self.accumulator as argument
   (.append self.accumulator x)           ;Good use of both.

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

A train of ``)``'s within a line is almost never acceptable.
A rare exception might be in something like an `enjoin`_,
because the structure of the string is more important for readability than the structure of the tree,
but even then, limit it to three ``)))``.

Semantic groups should be kept together.
Closing brackets inside a pair can happen in `cond`,
for example.

.. code-block:: Lissp

   (lambda (x)                            ;Preferred.
     (cond (lt x 0) (print "negative")
           (eq x 0) (print "zero")
           (gt x 0) (print "positive")
           :else (print "not a number")))

However, a train of ``)``'s must not appear inside of a line,
even in an implied group.

.. code-block:: Lissp

   (define compare                        ;Bad. Internal ))'s are hard to read.
     (lambda (xs ys)
       (cond (lt (len xs) (len ys)) (print "<")
             (gt (len xs) (len ys)) (print ">")
             :else (print "0"))))

   (define compare                        ;Bad. No groups. Can't tell if from then.
     (lambda (xs ys)
       (cond (lt (len xs) (len ys))
             (print "<")
             (gt (len xs) (len ys))
             (print ">")
             :else
             (print "0"))))

   (define compare                        ;OK. The ;; smells though.
     (lambda (xs ys)
       (cond (lt (len xs) (len ys))
             (print "<")
             ;;                           ;Separator comments can be empty,
             (gt (len xs) (len ys))       ; (unless there's something to say.)
             (print ">")
             ;; No internal ), so 1 line is OK. Still grouped.
             :else (print "0"))))

   (define compare                        ;Preferred. Keep cond simple.
     (lambda (xs ys)
       (let (lxs (len xs)
             lys (len ys))
         (cond (lt lxs lys) (print "<")
               (gt lxs lys) (print ">")
               :else (print "0")))))

The Limits of Length
::::::::::::::::::::

Readability is mainly laid out on the page.

The optimal length for a line in a block of English text is thought to be around 50-75 characters,
given the limitations of the human eye.
More than that, and it gets difficult to find the next line in the return sweep.
Excessively long lines are intimidating and may not get read as carefully.

Lines under about 10 characters can be read vertically with no lateral eye motion,
but lines of 10-50 characters require rapid-eye movements that become tiresome after too many lines,
which is really only a concern when the ratio of small lines becomes excessive.
The last line in a paragraph may (of course) be well under 50 characters as it runs out of words.

When your code contains flowing prose (e.g., docstrings), the rules for prose apply,
and one should try to keep most lines within these limits.

But the code itself is a different language.
Lisp's tree structure is read by indentation, and this is paramount for legibility.
It's not justified to the left like a typical block of English.
This can make finding the next line easier on the return sweep,
making longer lines somewhat more acceptable than for prose.

Regardless, the code must still fit on your screen.
Use an absolute limit of 120 characters.
(A smaller house limit of 100 is not unreasonable, if the team agrees.)

Horizontal scrolling is even more of a pain than eye movements.
Wrapped code lines are even worse as they disrupt the indent,
although an occasional string literal containing a newline is acceptable,
even in deeply nested code.
If it's more than occasional, consider alternatives.
Remember you can use ``\n``, constants, `<\<#<QzLT_QzLT_QzHASH_>`,
or `textwrap.dedent` (even at read time).

In rare instances (e.g., URLs), a constant definition containing a one-line string
literal may exceed even the 120-character limit.
Horizontal scrolling or wrapping is perhaps acceptable for the occasional top-level definition,
but Lissp does give you the option of building constant strings programmatically at read time.
Use your best judgement on which is more readable.
Multiline strings exceeding the limit are perhaps best read from a separate text file,
although one could perhaps justify embedding resources when the expected distribution is a single Python file.
Recall that macros can read files at compile time too.

For code lines (that are under the absolute limit of 120),
length should be counted relative to the indent, i.e., the leading spaces don't count,
and neither do the trailing brackets, because we ignore those.
Those are only there for the computer.

Margin comments are like a separate column of text,
so they don't count against the code's line length either,
but they do get their own relative limit starting from the first word after the semicolon.
They do count against the absolute line limit of 120, however.

Inline comments do count against the line, but are typically very brief.
If you're tempted to exceed limits with an inline comment,
consider using a margin comment or form/group comment instead.

Relative length is a concern secondary to proper indentation.
Follow the `Alignment Styles`_ given earlier in this guide.
Within those constraints (given the choice),
prefer relative line lengths either between 50-75 characters,
or less than about 10.
Sometimes that means joining short lines, not just splitting long ones.
An occasional line between 10-50 is preferable to a line over 75,
like the end of a paragraph in prose.
