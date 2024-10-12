.. Copyright 2020, 2021, 2022, 2023, 2024 Matthew Egan Odendahl
   SPDX-License-Identifier: CC-BY-SA-4.0

.. Hidden doctest adds bundled macros for REPL-consistent behavior.
   #> (.update (globals) : _macro_ (types..SimpleNamespace : :** (vars hissp.._macro_)))
   >>> globals().update(
   ...   _macro_=__import__('types').SimpleNamespace(
   ...             **vars(
   ...                 __import__('hissp')._macro_)))

Style Guide
###########

Why have a style guide?

Code was made for the human, not only for the machine,
otherwise we'd all still be writing programs in binary.
Style is not merely a matter of aesthetics.
Inconsistent code is a mental burden.

Code is written once, but rewritten many times.
Code is *read* more than it is written,
and often by multiple individuals.
Therefore,
making code easy to read and edit is much more important than making it easy to write.
Learning style is as much about learning to
*read* code as it is about learning to write it.

Style is the starting point for readability,
but good style doesn't excuse bad design.
Good style is consistent, but good design is elegant.
The more elegant designs often employ concepts novices would consider arcane.
Choose elegance anyway,
because the alternative is bloat.
Bloat does not scale; it collapses under its own weight.
There is no substitute for understanding your code.

Demand simplicity.
Assume a competent audience.
Learn the concepts yourself.
Mentor your juniors so they become competent too.
Don't stoop to their level.
Consider your design.
Refactor your code.
Doing all of that well is an art, but beyond the scope of a style guide.

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
our working memory is too small.
We handle complexity by chunking it into hierarchies of
labeled black boxes within boxes within boxes.
Mental recursive trees.

But syntax trees are the very essence of Lisp,
and you understand them in the same hierarchical way.
There are, of course, many more layers of abstractions below Hissp,
but at the bottom of Hissp's hierarchy are tuples of atoms.
Conceptually, it's a box with a label and contents:

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

To some extent,
this is a criticism that applies to any language with bracketed code blocks,
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
Lisp has structural editing tools that few other languages can match.
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
They don't get extra spaces either:

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

This also goes for readerless mode:

.. code-block:: Python

   # Very wrong.
   (
       "define",
       "fib",
       (
           "lambda",
           ("n",),
           (
               "ifQzH_else",
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
Go past the parent's opening bracket, not the sibling's:

.. code-block:: Lissp

   (a (b c))
   x                                       ;(a (b c)) is sibling

   (a (b c)
      x)                                   ;(a is parent, (b c) is sibling

   (a (b c
         x))                               ;(b is parent, c is sibling

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
You might not pass the head *atom* in some alignment styles:

.. code-block:: Lissp

   (foo (bar x)
     body)                                 ;(foo is parent, (bar x) is special sibling

   (foo (bar x
          body))                           ;(bar is parent, x is special sibling

We can still unambiguously reconstruct the trails from the indent. ::

   (foo (bar y
     body

   (foo (bar y
          body

Note that a multiline string is still an atom:

.. code-block:: Lissp

   (foo (bar "abc
   xyz"))

   (foo (bar)
        "abc
   xyz")

   (foo (bar "\
   abc
   xyz"))

   (foo (bar)
        "\
   abc
   xyz")

We can still unambiguously reconstruct the trails:

.. code-block:: Lissp

   (foo (bar "abc
   xyz"

   (foo (bar
        "abc
   xyz"

   (foo (bar "\
   abc
   xyz"

   (foo (bar
        "\
   abc
   xyz"

The closing ``"`` is not a bracket,
so we don't delete it or ignore it.

Alignment Styles
================

The remaining rules are more a matter of that *practical consistency*.
A good style guide must be *opinionated* to achieve that consistency,
but (with `one exception <#margin-comments-x>`_)
they are *suggestions*, not obligations,
because exactly what rules *implement* that consistency matter much less
than the consistency itself.
It's better if the rules are thorough enough to answer your uncertainty,
but not so complicated that no-one reads them.

Consistency with a widely-adopted style guide is good for the community,
but consistency within a project is a higher priority.
When they conflict with this guide, project rules rule.
Readability is paramount.

When there are gray areas,
don't forget there are better and worse options among the shades.
Cooperate with your team.
Use your best judgement.
This guide often includes a rationale for its recommendations.
Understand what the rules are for so you know when to break them.
This guide may be updated from time to time to better reflect community best practice.
If you're reading this guide, you are in that community.

Lisp is one of the oldest programming languages in common use.
It has splintered into many dialects (Lissp among them),
with a common culture, but without perfect agreement in all details.
Lissp's recommended style is based on these,
with some small modifications for its own unique features.

With proper indent style,
deep nesting is far more acceptable in a Lisp than in Python,
especially considering how operators work in each language.

Some rules pertain to the use of Hissp's bundled macros.
The use of the bundled macros is completely optional.

Tuples
::::::

By default, separate :term:`top level` forms from each other with a single blank like.
Don't use multiple blank lines in succession.
When greater separation is required, use comments.

Small and closely-related forms may be semantically "attached" to the next
or previous form by omitting the usual blank line.
E.g., several one-line "constant"
`define` forms making up a conceptual group need not be separated;
one only used by the following definition may be attached to it;
a form configuring the previous one (e.g. decorating, attaching attributes),
or adding it to a collection may be attached to it.

However, in many of these cases,
the groups could be better written as a single top-level form instead,
given the appropriate functions or macros.
E.g. `dict.update` (on `globals`), `let`,
`:@##<QzCOLON_QzAT_QzHASH_>`, `attach`, `doto`.

Try to avoid blank lines within forms.
You may need them for separating groups whose elements span lines
or to separate methods in long classes.
This desire for "paragraphs" is a code smell indicating your form may be too complex.
You can use comment lines to separate internal groups instead,
but consider refactoring into smaller parts.
Longer imperative entry-point scripts (main and the like)
should be segmented by `let` indentation or similar lambda-body forms
without resorting to blank lines.

Blank lines are OK in docstrings,
but comment strings (`<# <QzLT_QzHASH_>`) instead of :term:`Unicode token`\ s
are preferred for docstrings when they have more than a single paragraph.

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

   '(data1 data2 data3)                    ;Treat all data items the same.

   '(data1                                 ;Line break for one, break for all.
     data2                                 ;Items start on the same column.
     data3)                                ;Could've all fit on 1 line. (Just an example.)

   '(                                      ;This is better for linewise version control.
     data1                                 ; Probably only worth it for a lot more than 3,
     data2                                 ; or if it changes frequently.
     data3                                 ; Use this style sparingly.
     _#/)                                  ;Trails NEVER get their own line.
                                           ; But you can hold it open with a discarded item.
                                           ; This XML-style / doorstop is the norm in Lissp.

   (function arg1 arg2 arg3)               ;Typical for calls that fit on one line.

   ;; Also common. The function name is separate from the arguments in this style.
   (function arg1                          ;Break for one, break for all.
             arg2                          ;Args start on the same column.
             arg3)

   ;; The previous alignment is preferred, but this is OK if a line would be too long.
   (function
    arg1                                   ;Just like data.
    arg2
    arg3)

   ((lambda (a b c)
      (reticulate a)
      (frobnicate a b c))
    arg1                                   ;The "not past the sibling" rule is absolute.
    arg2                                   ; Not even one space past the (lambda.
    arg3)

   (function                               ;Acceptable, but unusual.
    arg1 arg2 arg3)

   ((lambda (a b c)
      (print c b a))
    arg1 arg2 arg3)                        ;Break for all args or for none.

   ;; One extra space between pairs.
   (function arg1 arg2 : kw1 kwarg1  kw2 kwarg2  kw3 kwarg3)

   ;; This might make the reason a bit more obvious:
   (% 1 0 2 9 3 8 4 7 5 6)                 ;Bad. Can't tell keys from values.

   (% 1 0  2 9  3 8  4 7  5 6)             ;Preferred. Group implied pairs.

   (% 1 0                                  ;OK, but could have fit on one line.
      2 9
      3 8
      4 7
      5 6)

   (%                                      ;Also OK.
    1 0
    2 9
    3 8
    4 7
    5 6)

   (function arg1 arg2
             : kw1 kwarg1  kw2 kwarg2)     ;Breaking groups, not args.

   (function arg1
             arg2
             : kw1 kwarg1                  ;The : starts the line.
             kw2 kwarg2)                   ;Break for args, but pairs stay together.

   (function : kw1 kwarg1                  ;The : starts the "line". Sort of.
             kw2 kwarg2)

   ;; The previous alignment is preferred, but this is OK if the line would be too long.
   (function
    arg1
    arg2
    :
    kw1
    kwarg1
    ;;                                     ;Break for everything, and ;; line to separate pairs.
    kw2
    kwarg2)

   (dict : a 1  b 2  c 3)                  ;Preferred

   (dict : a 1                             ;Standard, but could have fit on one line.
         b 2
         c 3)

   (dict : a 1                             ;Acceptable if : is first, but be consistent.
           b 2                             ;Note the alignment with the previous line.
           c 3)

   (dict :                                 ;Acceptable, especially for data.
    a 1                                    ; May be better for linewise version control.
    b 2                                    ; Use this style sparingly.
    c 3
    _#/)

   (function arg1                          ;Bad. : not first. Weird extra levels.
             arg2
             : kw1 kwarg1
               kw2 kwarg2

   (function arg1 arg2                     ;Bad. : not first. Weird extra levels.
             : kw1 kwarg1
               kw2 kwarg2

   (macro special1 special2 special3       ;Macros can have their own alignment rules.
     body1                                 ; Simpler macros may look the same as functions.
     body2                                 ; Special/body is common. Lambda is also like this.
     body3)                                ; Body is indented 1 extra space.

   (macro special1 body1)

   (macro special1
          special2
          special3
     body1
     body2
     body3)

   ;; Acceptable, but unusual body.
   (macro special1 special2 special3
     body1 body2 body3)

   ;; Also acceptable, but unusual body.
   (macro special1
          special2
          special3
     body1 body2 body3)

   ;; Group control words with the things they label.
   ;; Without any positional-only parameters, there's no need for :/ at all,
   ;; so it labels the group on its left.
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

   ;; Parameter groups are separated by lines. Pairs are separated by an extra space.
   (lambda (a b :/                         ;positional-only group
            c d                            ;normal group
            : e 1  f 2                     ;colon group
            :* args  h 4  i :?  j 1        ;star group
            :** kwargs)                    ;kwargs
     body)

Readerless style is similar:

.. code-block:: Python

   ('function','arg1','arg2'
              ,':','kw1','kwarg1', 'kw2','kwarg2',)

Note the space between 'kwarg1' and 'kw2' used to imply groups,
which is absent after the other commas in the tuple.

If you're using a full-file formatter that isn't aware of Hissp,
you may have to turn it off in places:

.. code-block:: Python

   ('define','fib'
    ,('lambda',('n',)
      ,('ifQzH_else',('operator..le','n',2,)
        ,'n'
        ,('operator..add',('fib',('operator..sub','n',1,),)
                         ,('fib',('operator..sub','n',2,),),),),),)  # fmt: skip

There are a few things to note about tuple commas in readerless.
The last element always ends with one (commas are used as terminators,
not separators),
even on the same line.
This is to prevent the common error of forgetting the required trailing comma for a monuple.
Or think of ``,)`` as how you spell the closing braket.
If your syntax highlighter can distinguish ``(x)`` from ``(x,)``, you may be OK without it.
But this had better be the case for the whole team and project.
Be consistent.

Also note that in this example the tuple commas did not end the line,
but rather started the next one.
In the case of the ``ifQzH_else`` macro,
this gave the body the proper additional column indent it would have had in Lissp.
In the case of the ``operator..add`` function,
this aligned the arguments.
Linewise edits and indentation are also more consistent this way.

Commas are not followed by a space except to imply groups
(when an extra space would be used in Lissp).
In cases where there wouldn't be any whitespace groupings in Lissp,
the commas would end the line in readerless Hissp as well:

.. code-block:: Python

   ('lambda',()
    ,('quote',('data1',  # Notice how a , both begins and ends this line.
               'data2',
               'data3',),),)

.. _enjoin:

Alignment styles can be bent a little in the interest of legibility,
especially for macros, but even for calls,
as long as the two absolute rules are respected.

For example, this ``enjoin`` function

.. code-block:: Lissp

   (define enjoin en#X#(.join "" (map str X)))

builds a string from multiple arguments.

Omitting spaces between atoms and having a variable number per line is acceptable here,
because the string's structure is more important for legibility than the tuple's:

.. code-block:: Lissp

   (enjoin                                 ;Preferred.
     "Weather in "location" for "date" will be "weather"
    with a "percent"% chance of rain.")

   (enjoin "Weather in "                   ;OK.
           location
           " for "
           date
           " will be "
           weather
           "
     with a "                              ;OK, but would look better with \n.
           percent
           "% chance of rain.")

Exactly where the implied groups are can depend on the function's semantics,
not just the fact that it's a call:

.. code-block:: Lissp

   (enter (wrap 'A)                        ;Stacked context managers.
    enter (wrap 'B)                        ; Note pairs.
    enter (wrap 'C)                        ; `enter` is from the prelude.
    (lambda abc (print a b c)))

   (engarde `(,FloatingPointError ,ZeroDivisionError) ; engarde from prelude
            print
            truediv 6 0)                   ;(truediv 6 0) is a deferred call, so groups.

   (.update (globals) :                    ;OK. : on wrong side, but easier
    + operator..add                        ; for linewise version control.
    - operator..sub                        ; Sometimes worth it, but
    * operator..mul                        ; use this style sparingly.
    / operator..truediv
    _#/)                                   ;Doorstop holding ) on this line.

   (.update (globals)                      ;Preferred. Standard style.
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

   #> (print (.upper '.#(textwrap..dedent "\
   #..                   These lines
   #..                   don't interrupt
   #..                   the flow.")))
   >>> print(
   ...   "These lines\ndon't interrupt\nthe flow.".upper())
   THESE LINES
   DON'T INTERRUPT
   THE FLOW.

Notice the escaped initial newline.
This is optional,
but allows the first line to be aligned with the rest.
Because the string was injected (``.#``),
don't forget to quote it (``'``),
or the compiler will assume the string contents are Python code to be inlined.

Remember that `<# <QzLT_QzHASH_>` can also make multiline strings:

.. code-block:: REPL

   #> (print (.upper <#;These lines
   #..               ;; don't interrupt
   #..               ;; the flow.
   #..               _#/))
   >>> print(
   ...   "These lines\ndon't interrupt\nthe flow.".upper())
   THESE LINES
   DON'T INTERRUPT
   THE FLOW.

Notice the required :term:`doorstop` and identical compilation.
You can avoid the doorstop in this case by using the `-><QzH_QzGT_>` macro:

.. code-block:: REPL

   #> (print (-> <#;These lines
   #..           ;; don't interrupt
   #..           ;; the flow.
   #..           .upper))
   >>> print(
   ...   # QzH_QzGT_
   ...   "These lines\ndon't interrupt\nthe flow.".upper())
   THESE LINES
   DON'T INTERRUPT
   THE FLOW.

With the principal exception of docstrings,
long multiline :term:`Unicode token`\ s
should be declared at the :term:`top level`
and referenced by name:

.. code-block:: Lissp

   (define MESSAGE "\
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

Remember, readability counts.
You are writing for a human audience, not just a compiler.
Commentary should create clarity, not confusion.

Your code is probably not as "self-documenting" as you think it is.
Beware the
`curse of knowledge <https://en.wikipedia.org/wiki/Curse_of_knowledge#Computer_programming>`_.
Understanding code requires the programmer to maintain a lot of mental context.
Commentary can reduce that burden considerably.
Assume your audience is competent, but lacks some of that context.
That could describe *you* in six months.
Your audience should be able to understand the language
and read library documentation.

Avoid adding superfluous "what"-comments that are obvious from looking at the code.
(Except perhaps when writing language documentation for beginners ;)
These are the most likely type to suffer from rot and mislead as implementation changes.
Styling separator comments used to imply groups are exempt.

Prefer "why"-comments that describe rationale or intent at a higher level.
These are less likely to rot and mislead.
Even as implementation changes, the reasons for it often do not,
and when they do, it's easier to tell.

If "what"-comments still seem necessary,
consider how to make the code itself clearer,
so the "what"-comments would become obvious by looking at the code.
This is not a prohibition.
Sometimes, in cases of difficult mathematics, complicated algorithms,
or performance-optimized code,
more thorough commentary is necessary,
including comments about what the code is doing.

Software development is fundamentally research, not manufacturing or construction.
URLs citing sources used can be appropriate,
especially for copied/adapted code, but also for rationale or technique.
Don't just drop in a URL; say what it's for.
URLs are not the only type of citation.

Comments are appropriate for pointing out issues that cannot be fixed yet,
perhaps awaiting a library update.
Code that is only needed temporarily
(perhaps working around issues that cannot be fixed yet)
should have a comment with removal criteria.
Comments can be appropriate for pointing out non-obvious coupling between files,
(preferably on both sides),
and should be positioned close to likely changes,
so they'll be noticed when changes happen.

Some programmers these days are so afraid of stale comments that they
refuse to document their code at all,
and remove what comments they can find.
This is agile culture taken too far.
Good names are important, but they aren't enough,
and don't excuse neglect of commentary.
Names can become stale too; they're not immune just because they're code.

"Working software over comprehensive documentation"
doesn't mean literally zero documentation.
It doesn't even mean asymptotically zero documentation as an ideal to strive for.
It means that the documentation is not what delivers the bulk of the value,
and that thorough documentation does not excuse software that doesn't work
(or doesn't work yet).

Version control commit messages are also documentation.
Those are attached to particular versions, so they can't become stale,
and aren't a burden to maintain, but they're still valuable history.
You can write more than a single line.
Take the opportunity to explain what you were thinking.
A few sentences don't take that much time, but can save a lot later.

Documentation is a burden, just as code is a liability.
Don't accept more of either than delivers value.
Quality over quantity.
Remove or fix bad comments, as appropriate.
Be careful not to remove styling comments that are still required to imply groups.
Check the version control history for more clues.
Consider if updating or clarifying a comment is more appropriate than removal.

Prefer documentation that is located as close as possible to what it documents,
so it doesn't get out of sync as easily,
and then actually read the nearby commentary before modifying existing code.

Don't manually write separate API docs.
Generate it from your docstrings with something like Sphinx.
A docstring in a script, with doctests,
is better than a manually-written separate README file
with the same information.
Prefer scripts with commentary over complicated README instructions.

Prefer assertions over comments documenting assumptions.
These don't go stale, or you'd notice.
Of the assertion types, prefer `avow` over `assure` over `doctest` over `unittest`,
the last of which is best for more thorough tests of edge cases that would otherwise
bloat the more local documentation too much.
Functional tests are also a kind of documentation.
Readability counts, even there, and commentary there can be especially valuable.
Functional tests make good debugging entry points.

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
     body2                                 ;Margin comment
     body3)                                ; continuation thereof,
                                           ; and more continuation on its own line.

Complete sentences should start with a capital letter and end with
a punctuation mark (typically a full stop or question mark).
Separate sentences with a single space.
Short comments need not be complete sentences.

``Inline ; comments``
+++++++++++++++++++++

Comments about a line begin with one semicolon and a space ``; x``,
starting **one** space after the code.
They never get their own line,
but follow code on the same line.

This acceptable in Lissp, and closer to the Python style
(which would start *two* spaces after the code.
It's also two spaces for readerless mode,
where, aside from occasionally being used to imply groups,
comment styles follow the same rules as normal Python.)
Lisp traditionally uses margin comments instead (as described below),
but this inline style is also common in Clojure.

Avoid obtuse abbreviations just to make a comment fit in line.
When a comment needs to be longer to be clear,
use a different comment style instead.

``Margin          ;comments``
+++++++++++++++++++++++++++++

Margin comments begin with one semicolon ``;x``.
The semicolon must be aligned with spaces to rest on column 40,
or one space after the code, whichever is greater.
(That's if you're using zero-based column indexing, like Emacs.
The semicolon goes on column 41 if you're counting columns starting from 1,
like Vim.)
The semicolon is not followed by a space unless it continues a margin
comment from the previous line.
Unlike inline comments,
margin comment continuation lines need not have code on their line.

**Never** put a single-semicolon comment on its own line unless
it's a continuation aligned to the margin!
*This one is not a suggestion.*
It's about established tooling.
Traditional Lisp editors automatically indent these to column 40,
and Lissp was designed to work with Emacs ``lisp-mode``.
If you break this rule, others will have to fix all your comments,
or reconfigure their editors to collaborate at all,
and then change them back when working on Lissp files with normal style.
That's not nice.

This includes comment tokens meant as arguments for reader macros!
Lissp tokenizes comments in blocks,
so multiline comments used as reader arguments nearly always
use a form/group comment starting with two semicolons and a space as described below.
But with a single ``;``, they must follow code on the same line,
typically the reader tag itself.
In the rare case neither is valid (if the macro is counting the semicolons),
then it's a margin comment. Indent it to the margin.

Be careful with comments around detached :term:`tagging token`\ s!
:term:`Comment token`\ s are normally discarded by the reader in Lissp,
but they are a valid target for :term:`tagging token`\ s,
in which case they may be treated as literal values.
Avoid using inline or margin comments as commentary between a tag and its target,
as this can cause errors when they are instead treated as arguments.
(Usually, tags are attached to one argument, so this doesn't come up,
but e.g. the bundled decorator macro `:@##<QzCOLON_QzAT_QzHASH_>` typically is not.)
You may use a discarded string instead ``_#"NB foo"``.
A good syntax highlighter specialized for Lissp may be able
to indicate when a comment token is not discarded,
but a traditional Lisp editor like Emacs ``lisp-mode`` would not.

In rare cases, a margin comment may occupy the same line as some other comment form.
This is usually acceptable style,
but a ``;`` following a ``;;`` is still tokenized as part of the ``;;`` block,
which can matter for reader macros like `<# <QzLT_QzHASH_>`.

Avoid using either margin or inline comments
in any situation that would result in a dangling bracket.
It's not acceptable for the comment to follow the bracket either,
if the comment isn't about the whole tuple.
You may instead hold open the bracket with a :term:`doorstop`,
convert the comment to a discarded string ``_#"NB foo")``,
or (if appropriate) use a form/group ``;;`` comment above the item, as described below.

``;; form/group comments``
++++++++++++++++++++++++++

Comments about the next :term:`form` (or group)
begin with two semicolons and a space ``;; x``,
and are indented to align as if they were forms,
and are not followed by a blank line.
These comments can be continued with additional lines with the same indent and beginning,
forming a comment block.

Commented-out code does not belong in version control,
but disabling code without deleting it can be helpful during development.
Use ``;;`` at the start of each line,
or use the discard macro ``_#`` to comment out code structurally.

Prefer class and function docstrings over ``;;`` comments where applicable.

*;;; top-level comments*
++++++++++++++++++++++++

Top-level commentary lines not attached to any :term:`form` in particular
begin with three semicolons and a space ``;;; Foo Bar``.
Top-level comments are separated from code with a blank line.
They are never indented.
These comments can be continued with additional lines with the same beginning,
forming a comment block.

Standard usage for more than two semicolons varies with Lisp dialect,
but they are consistently ony for the :term:`top level` and have no indent.

Some Lisp styles use triple and quadruple semicolons for headings and subheadings,
but differ on which is which.
To avoid confusion,
do not use triple-semicolon comments as headings at all.

Prefer a module docstring over top-level comments where applicable.
Remember that a `<# <QzLT_QzHASH_>`
applied to a comment block compiles to a string literal,
which can be a docstring.

**;;;; Headings**
+++++++++++++++++

Headings begin with four semicolons and a space ``;;;; Foo Bar``,
fit on one line,
and are written in ``Title Case`` by default.

Other Lisp dialects may use quadruple-semicolon comments for module-level comments,
as a category distinct from top-level commentary.
In Lissp,
module-level commentary should instead appear in the module's docstring,
or, in the case of implementation details,
in triple-semicolon comments near the top of the file,
usually immediately before or after the module docstring.
(E.g., license boilerplate.)
Quadruple semicolon comments are exclusively for headings.

Headings are for the :term:`top level` only;
they aren't nested in :term:`form`\ s;
they get their own line and start at the beginning of it.
They have a blank line before (unless it's the first line) and after.
They should not have additional continuation lines.
They organize the code into sections.

Headings can be decorated with symbol characters to make them more emphatic.

A Lissp file would typically be broken up into smaller modules
before you need more than one or two heading levels.

But for a project distributed as a single large file,
you may want to develop a project style with more levels than that,
especially if you don't use classes to group functions.

Avoid using

- semicolons as underlines or other header decoration.
- more than four semicolons in a row.
  (This is sometimes seen in Emacs Lisp to indicate heading levels,
  but more than four semicolons in a row is too difficult to distinguish at a glance
  and must be counted.)
- overlines for emphasis.
  (An overline is commonly seen in reStructuredText headings.
  but it can obscure the heading text when folding code in some editors.)
- different underlining styles alone to distinguish levels.
  (Underlines are indistinguishable when folded.)
- inconsistent decorations.

Many levels are probably too rare to require a community
(rather than project-level) standard,
but here's an example scheme with six levels
(Six is enough for HTML, with H1-H6 tags.):

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

The mnemonic here is that symbol characters that have more points
(and use more ink) are more emphatic:
``#`` (8, H1); ``*`` (5 or 6, H2); ``+`` (4, H3); ``-`` (2, H4); ``.`` (1, H5);
and H6 is undecorated.

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
This will minimize the number of heading style changes you need to make
if you later find that you need another level.
(This means that if you do not use all six levels,
you will not have any undecorated H6's at all.)
Multiple H1s might be acceptable for large projects distributed as a single concatenated
Lissp file, where they'd head what would normally be modules in separate files.

``_#_#_#The Discard Macro``
+++++++++++++++++++++++++++

The discard macro ``_#`` applied to a :term:`Unicode token`
is acceptable for long block comments at the top level.

Several discard macros may be used in a row to comment out that many forms following them.

A discarded tuple may be used to contain scratch code during development.
But beware that discarded code is still *read*,
executing any :term:`tag`\ s.

(This is one of several reasons why :term:`tag`
:term:`metaprogram`\ s should avoid side effects,
or at least be idempotent.
Of course,
such a metaprogram indented to be well-behaved may
still raise errors while it's being developed,
preventing a normal file reload.
Try using ``;;`` form comments on the affected lines instead when this happens.)

As with line comments,
commented-out code does not belong in shared version control;
old versions should be in old commits.
Move the manually-executed functionality you need to keep out of the comments
and into functions run by a `name_equals_main` guard or separate scripts.
Move the experiments you want to keep running to assertions.
(See `assure`, `unittest`, and `doctest`.)

A discarded :term:`Unicode token`, :term:`control token`,
or :term:`fragment token` with code following it in line is acceptable as commentary,
but use this style sparingly.
Include an arrow or "NB" (*nota bene*) in the string to make it clear this is a comment
and not just disabled code:

.. code-block:: Lissp

   (print 1 2 _#:<-even 3 _#|also even ->| 4
          : sep : _#"NB Control words compile to strings!")

An extra space is typically used to imply separation between groups on the same line.
Where one level of grouping is not sufficient,
typically newlines,
then single ``;;`` lines indicate increasing levels of separation.
Avoid more than two spaces in a row for implying separation between groups in a line,
or more than one ``;;`` separator line in succession.
In rare cases where those aren't enough levels,
or newlines and ``;;`` lines would spread things out too much,
it is acceptable to additionally use discarded punctuation
(like ``_#:``, ``_#:,``, or ``_#\;``, etc.)
within a line, to indicate greater separation than the extra spaces.

These are also used in the :term:`doorstop`
``_#/`` used to "hold open" a trail of brackets.

``<#;Docstrings``
+++++++++++++++++

Prefer docstrings over semicolon comments where applicable.
Quality over quantity,
but it's OK if a function docstring is longer than the function its documenting,
especially if it's for doctests.
A competent editor can fold comments.

Docstrings describe interface and usage;
they are not for irrelevant implementation details internal to their containing object.

"Private" helper functions/classes/modules
(conventionally named with a leading underscore)
need not have docstrings at all,
but still, prefer docstrings over comments when applicable,
in which case they describe an interface internal to their object's container,
but still do not describe their object's implementation details.

The first expression of a module (if it compiles to a string literal) is its docstring.
Prefer this form over assigning the ``__doc__`` global directly.

The ``lambda`` :term:`special form` does not create docstrings.
However, you can attach a ``.__doc__`` attribute to the lambda object after creating it,
e.g., using the `attach` macro. The `defun` macro does this for you.

The bundled `deftypeonce` macro does not have any special case for docstrings.
Instead add a ``__doc__`` attribute.

Indent docstrings to the same column as their opening ``"``
even when using something like the `attach` macro.
This does put the leading whitespace inside the string itself,
but Python tooling expects this in docstrings,
and can strip it out when rendering help.

If the docstring contains any newlines,
the closing ``"`` gets its own line.

It is acceptable to use reader macros that resolve to a string literal like
`<# <QzLT_QzHASH_>` (which is useful for doctests)
as long as the documentation text is also legible in the source code.
A comment string is preferred over a :term:`Unicode token` when it would
contain a blank line.

Follow Python style on docstring contents.

While reStructuredText is currently the default in the Python ecosystem,
docstrings can use some other markup format if the whole team can agree on one,
and it's done for the entire project.
E.g., MyST Markdown also has pretty good support now.
You can automatically generate API documentation with either of these.

:term:`Anaphoric <anaphoric macro>` or :term:`injection` macros are potential gotchas.
Docstrings for these should include the word "Anaphoric" or "Injection" up front.
Anaphoric macro docstrings should also state what the anaphors are,
named in doubled backticks.

Any docstring for something with a munged name
should start with the `demunge`\ d name in doubled backticks
(this includes anything with a hyphen):

.. code-block:: Lissp

   <#;``my#`` Anaphoric. Let ``my`` be a fresh `types.SimpleNamespace`
   ;; in a lexical scope surrounding ``e``.
   ;; ...

For `tag`\ s, use the number of hashes required for its minimum arity.
The demunged names should be followed by the pronunciation in single quotes,
if it's not obvious from the identifier:

.. code-block:: Lissp

   "``:@##`` 'decorator' applies ``decoration`` to a definition & reassigns."

This way, all three name versions (`munge`\ d, `demunge`\ d, and pronounced)
will appear in generated docs.

Identifiers
===========

If you're writing an API that's exposed to the Python side,
avoid unpythonic identifiers
(including package and module names)
in the public interface.
Use the
`naming conventions from PEP 8. <https://www.python.org/dev/peps/pep-0008/#naming-conventions>`_

``CapWords`` for class names.

``snake_case`` for functions,
and that or single letters like ``A`` or ``b``
(but never ``l`` ``O`` or ``I``) for locals,
including kwargs.

``UPPER_CASE`` for "constants".

For internal Lissp code,
Python naming conventions are still acceptable,
but the munger opens up more characters.
Something like ``+FOO-BAR+`` is a perfectly valid Lissp identifier,
but it munges to ``QzPLUS_FOOQzH_BARQzPLUS_``,
which is awkward to use from the Python side.

Even in private areas,
let the munger do the munging for you.
Avoid writing anything in the Quotez style yourself.
(This can confuse the demunger
and risks collision with compiler-generated names like gensyms.)

Abbreviated Names
:::::::::::::::::

Abbreviated (even single-character)
local identifiers are acceptable if their lexical scope is very small,
preferably within the same line or the next few,
especially if their initial binding makes their meaning clear.
(This includes `X#<XQzHASH_>` and friends.)
Parameter names of public-facing functions are considered part of their interface,
since they can be passed as kwargs,
and should be more descriptive in most cases.
Single-letter names following a strong mathematical or coding convention
may be clear enough even over wider scopes.

It's idiomatic in Lissp to use a :term:`symbol`
as the :term:`params` when they'd each be one (non-munging) character:

.. code-block:: Lissp

   (lambda abc (print c b a))              ;Preferred

   (lambda (a b c)                         ;OK
     (print c b a))

   ;;; This goes for macro arguments directly used as params too.

   (let-from abc 'XYZ (print c b a))       ;Preferred

   (let-from (a b c)                       ;OK
             'XYZ
     (print c b a))

   (any*map kv (.items (dict : a 1  b 2))  ;Preferred
     (print k v))

   (any*map (k v)                          ;OK
            (.items (dict : a 1  b 2))
     (print k v))

Name the first method argument ``self``
and the first classmethod argument ``cls``.
Python does not enforce this,
but it's a very strong convention.

For very terse code, ``s`` and ``c`` may be acceptable alternatives,
but the conventional names are preferred.
Macros or tags may need to use :term:`gensym`\ s or
:term:`anaphor`\ s for these,
and that is also acceptable.

Avoid abbreviating local identifiers otherwise.
Remember to optimize for readability rather than writability.
Don't make the programmer guess,
but assume a competent audience.
Avoid excessively long names.
Bloat is not readable either.
Descriptive names do not excuse bad design.

Conventional short names include, but are not limited to,

* ``i`` and ``j``, in that order, for integer indexes,
* ``k`` and ``v`` for "key" and "value" when iterating over a mapping,
* ``kvs`` for a mapping (or other iterable of key-value pairs).
* ``ks`` for iterables of keys.
* ``vs`` for iterables of values.
* ``xss`` or ``yss`` for iterables of iterables.
* ``xs`` or ``ys`` for iterables, especially if pulled from ``xss`` or ``yss``.
* ``x`` or ``y`` for elements pulled, especially from ``xs`` or ``ys``.
* ``f``, or ``g`` for callable parameters or locals.
* ``n`` for an integer parameter, especially if it's a size.
* ``ns`` for a namespace. (Something used for assignable attributes. [#ns]_)
* ``s`` for a string parameter or local.
* ``cs`` for an iterable of characters
  (often a `str`, but prefer ``s`` if you're not actually iterating over the characters).
* ``c`` for characters (`len`-1 `str`\ s), especially if pulled from ``cs``.
* ``b`` for a boolean parameter.
* ``e`` for an exception.
* ``items`` for collections supporting at least ``__getitem__``,
  (Usually `Sequence` or `Mapping` protocols, but you don't care which.)
  May need to be mutable, depending on context.
* ``seq`` for random-access sequences.
  (This is very different from the Clojure meaning! See `collections.abc.Sequence`.)
  May need to be mutable, depending on context.
* ``expr`` for an expression.
* ``args`` for the ``*`` parameter collecting positional arguments.
  Prefer a more meaningful name if possible,
  but this is acceptable for decorator implementations that pass them through.
* ``kwargs`` for the ``**`` parameter collecting keyword arguments.
  Prefer a more meaningful name, as ``args``.

Prepend an ``i`` to the variable name for once-through iterators,
especially when you call :func:`iter` on a variable with otherwise the same name:

.. code-block:: Lissp

   (let (ixs (iter xs))
     ...)

Throwaway Names
:::::::::::::::

Some macros
or higher-order functions require you to create a binding even when it's useless.
Throwaway (unused) locals should begin with an underscore.
For example, :ref:`engarde <engarde>`'s exception handler must accept an exception.
If you're going to use it, you can call it ``e``,
but if you're not, call it ``_e`` instead.
Don't let this stop you from using `X#<XQzHASH_>` to make a handler,
or when otherwise appropriate.
Avoid assigning to ``_``
except in very terse code when its lexical scope is within the same line,
in which case it's a throwaway local.
This variable is used by the REPL and debugger for the last value.
Shadowing it can make interactive development and debugging more difficult.

In rare cases, a function may have a mutable parameter default used as a cache.
Often it's better to put this cache somewhere else,
but sometimes definition time is the right level.
Use an argument name starting with an underscore to indicate this is a "private"
implementation detail not meant to be part of the function's interface.
These parameters should not be passed in, except perhaps by tests.
This doesn't conflict with the throwaway case because the presence of the default
argument distinguishes them.

Shadowing
:::::::::

While frowned upon in Python with its relatively small number of builtins,
using a built-in function name as a local is more acceptable in a Lisp-2
which typically has a lot more built-in functions and separate
function and variable namespaces anyway.

Although Hissp is dynamic enough to change this, it is a Lisp-1 by default,
because Python also uses a common namespace for both.
Lisp-1s often avoid shadowed function names by using awkward workaround abbreviations,
like ``lst`` for ``list``.
One can get used to these, but they do impair legibility.
Python's convention is to append an underscore to unavailable names (``list_``).
This is acceptable in Hissp,
but occasionally the appended name is also taken.
A modified Smalltalk-like convention like ``a-list`` is also acceptable,
or ``a_list``, especially for a parameter that might be called with keyword syntax like
``a_list=foo`` from Python code, to avoid munging.

Shadowing locals is acceptable,
and can be thought of as a reassignment.
Local binding forms have a restricted lexical scope
which makes them easier to reason about than Python's local (re)assignment statements.
Hissp functions often immediately convert parameters to a more useful form in a `let`
and shadow them with the same names.
Be more careful in imperative scripts where lexical scopes can be larger.
Consider if multiple smaller scopes are more readable.
A `let` often contains the entire function body,
but can be a smaller section or nested much more deeply.

Shadowing of builtins is a source of potential errors,
so it is preferable that you do not,
but lexical scoping handles this acceptably.
This preference should be extended to a module's globals, including the
`prelude<hissp.macros._macro_.prelude>`'s star-imports of `operator` and `itertools`.
Python's naming conventions for classes (``CapWords``) and "constants"
(``UPPER_CASE_WITH_UNDERSCORES``) usually prevents local collisions with those,
but function and module names can be a problem.
Prefer `aliases<_macro_.alias>` over defining globals of module type.

Name top-level definitions (like helper functions)
that are only being used inside your module
(or by tests, internal or not) with a leading underscore.
This is the Python convention for a "private" global,
although not much enforces it.
You can always rename these later if you need to.
You'll only have to update usages in the module.
(The reverse is harder, but shouldn't be done while there are any external usages left.)
This aids in readability, because it makes it easy to tell
what definitions are interface and what's implementation detail.
It also narrows the space of possible local collisions to the public interface functions.

However, memorizing which names are off-limits puts an undue burden on the writer,
especially for a REPL-driven rather than IDE-driven language like Lissp.
For reasonably short functions, it's clear what the locals are from their binding forms.
Macro definitions should be robust enough to handle a shadowed builtin.
Lissp's template syntax makes this fairly easy as it qualifies symbols by default.
You have to go out of your way to turn this off for anaphors.

You are free to use the fully-qualified names in handwritten code as well.
Using a fully-qualified name is preferred over
changing a shadowing parameter name in an established public-facing function.
Parameter names are considered part of the interface,
especially when they can be passed as kwargs
(includes normal positional parameters,
not just the `kwonlies<keyword-only_parameter>`).
Changing positional-only parameter names is more acceptable,
but beware that this change does show up in `help`,
automated API documentation, and the like.

For these reasons, shadowing a global or builtins isn't considered unacceptable in Lissp
like it is in other languages you might know.
It's better to avoid it, but don't worry about it too much,
and don't go out of your way to correct it either,
especially for small functions.

Aliasing and Imports
::::::::::::::::::::

Avoid repeating the name of the containing module or package when writing definitions,
because they may be accessed through an alias or as a module attribute.

The programmer should not have to guess
what an `alias<_macro_.alias>` means when jumping into an unfamiliar file.
Use consistent aliases within a project.
Usually, this means the alias is the module name, but not its containing packages,
unless there is a shorter well-known name in the community
(like ``np#`` for NumPy or ``op#`` for operators)
or for an internal module well-known within your project.

Avoid reassigning attributes from other modules as globals
without a very good reason.
Yes, Python does this all the time.
It's how `from` works at the :term:`top level`.
Just access them as attributes from the module they belong to.
This improves readability,
and for internal project modules,
improves reloadability during REPL-driven development.
Otherwise, instead of just refreshing the module with the updated definition,
every module reassigning it would have to be reloaded as well.

Aliases are also preferred over assigning modules as globals
(although this is less of a problem).
They have the advantage of never colliding
with your locals or global function names,
although they would use up a tag name instead,
you probably won't have as many of those.
Symbols in templates can only be automatically qualified with the defining module's
`__name__` or `builtins`.
Using a name with a fully-qualifying alias in a template is like using
the fully-qualified name,
so it will be probably be imported from its canonical location
(assuming you're aliasing that location),
rather than from wherever the template happens to be defined.

Sometimes separate packages use the same module name internally.
Aliases are allowed to contain a dot.
(Fully-qualified tags have a double dot.)
Usually, you'd alias as the library's root package name followed by a dot,
followed by the module name.
Given Python's "flat is better than nested" culture,
many library packages have no subpackages,
so this may not be any shorter than using the fully-qualified name.
For example, ``foo.bar.baz.`` could be aliased as
``foo.baz#`` if ``baz#`` alone would be ambiguous.
A well-known name is also acceptable,
e.g., ``numpy.random.`` could be aliased as ``np.random#`` instead of ``random#``,
which is the same name as the standard library `random` module.
Of course, there's no need to alias `random` as ``random#`` in the first place:
``(random..random)`` isn't really worse than ``(random#random)``.
The fully-qualified names are only one character longer.
So this case is not really a conflict,
although ``np.random#`` is potentially less confusing.

Prefer using aliases over attaching a macro or tag from other modules to `_macro_`,
because that's expecting everyone to have it memorized.
Using tags or macros without aliases is acceptable
when originally defined in the same module.
It's also acceptable for the bundled tags and macros,
or some other core library serving a similar function for the project,
because everyone needs to be familiar with those.
You need a very good reason for attaching anything else.
This is usually more acceptable for tags than for macros.
Be aware of the readability costs and benefits involved,
and consider carefully if it's worth it
in the context of all the other names the programmer needs to be familiar with
in your codebase.
A similar argument can be made against importing non-module attributes of other modules.

Method Syntax vs Attribute Calls
::::::::::::::::::::::::::::::::

Often, code like ``(.foo bar spam eggs)``
could also be written like ``(bar.foo spam eggs)``.
In some cases, the choice is clear,
because they compile differently,
but in others, these would compile exactly the same way.

For those cases, consider that sometimes macros rewrite the code first.
Which is preferred then depends on whether ``bar`` is a namespace or an argument.

For a namespace, prefer ``bar.foo``.
Internal use of ``self`` in methods and ``cls`` in classmethods,
is also more namespace than argument.
For an argument, i.e., other method calls, prefer ``.foo bar``:

.. code-block:: Lissp

   (hissp.._macro_.define greeting "hi")   ;Compile-time macroexpansion
   (.define hissp.._macro_ 'greeting '"hi") ;Run-time expansion.

   ;;;; Arguments

   (.upper "hi")                           ;Preferred.
   ("hi".upper)                            ;SyntaxError.
   (-> "hi".upper)                         ;Works, but overcomplicating it.

   (.upper greeting)                       ;Preferred.
   (greeting.upper)                        ;Usually bad. Hides first argument from macros,
                                           ; but you may want that sometimes.

   ;;;; Namespaces

   (tkinter..Tk)                           ;Preferred. Fully-qualified name.
   (.Tk tkinter.)                          ;Bad. Not really a method call.

   ;;;; Kind of Both

   (self.foo spam eggs)                    ;Preferred.
   (.foo self spam eggs)                   ;OK. Consider for doto, ->, etc.

   (cls.foo spam eggs)                     ;Preferred.
   (.foo cls spam eggs)                    ;OK.

   ;; `self` as namespace, `self.accumulator` as first argument.
   (.append self.accumulator x)            ;Preferred. Good use of both.

   (self.accumulator.append x)             ;Usually bad. Hides first argument.

   ;; Bad. This does happen to be valid syntactically, but is probably
   ;; confusing in most cases. The namespace is `self`, but that looks
   ;; like the first argument. (The first argument is actually
   ;; `self.accumulator`.) The method name looks like it might be
   ;; `accumulator` but it's actually `append`.
   (.accumulator.append self x)

.. TODO: consider usage recommendations for individual bundled macros.

The End of the Line
===================

Ending brackets should also end the line.
That's what lets us indent and see the tree structure clearly.
It's OK to have single ``)``'s inside the line,
but don't overdo it:

.. code-block:: Lissp

   (lambda (x) (print "Hi" x) (print "Bye" x)) ;OK.

   (lambda (x)                             ;Preferred.
     (print "Hi" x)
     (print "Bye" x))

Don't put a train of ``)``'s inside the line,
because then we'd have to count brackets!

If the train is trailing at the end of the line,
then the tree structure is clear from the indents:

.. code-block:: Lissp

   (print (/ (sum xs) (len xs)) "on average.") ;Bad. Internal ))'s.

   (print (/ (sum xs) (len xs))            ;OK. One internal ) though.
          "on average.")

   (print (/ (sum xs)                      ;Preferred. )'s end the line.
             (len xs))
          "on average.")

A train of ``)``'s within a line is almost never acceptable.
A rare exception might be in something like an `enjoin`_,
because the structure of the string is more important for readability
than the structure of the tree,
but even then, limit it to three ``)))``.

Semantic groups should be kept together.
Closing brackets inside a pair can happen in `cond`,
for example:

.. code-block:: Lissp

   (lambda (x)                             ;Preferred.
     (cond (lt x 0) (print "negative")
           (eq x 0) (print "zero")
           (gt x 0) (print "positive")
           :else (print "not a number")))

However, a train of ``)``'s must not appear inside of a line,
even in an implied group:

.. code-block:: Lissp

   (defun compare (xs ys)                  ;Bad. Internal ))'s are hard to read.
     (cond (lt (len xs) (len ys)) (print "<")
           (gt (len xs) (len ys)) (print ">")
           :else (print "0"))))

   (defun compare (xs ys)                  ;Bad. No groups. Can't tell if from then.
     (cond (lt (len xs) (len ys))
           (print "<")
           (gt (len xs) (len ys))
           (print ">")
           :else
           (print "0"))))

   (defun compare (xs ys)                  ;OK. Use discard comments sparingly.
     (cond (lt (len xs) (len ys))
           (print "<")
           _#:elif->(gt (len xs) (len ys)) ;Unambiguous, but unaligned.
           (print ">")
           :else (print "0")))) ; No internal ), so 1 line is OK. Still grouped.

   (defun compare (xs ys)                  ;OK. Better.
     (cond (lt (len xs) (len ys))
           (print "<")
           ;; else if                      ;The styling comment is not optional;
           (gt (len xs) (len ys))          ; it's needed for separating groups.
           (print ">")
           :else (print "0"))))

   (defun compare (xs ys)                  ;Preferred. Keep cond simple.
     (let (lxs (len xs)
           lys (len ys))
       (cond (lt lxs lys) (print "<")
             (gt lxs lys) (print ">")
             :else (print "0")))))

Prefer Shorter Definitions
::::::::::::::::::::::::::

Pure functions and especially methods of a class should be kept very short,
implementing a single easily-testable concept
or perhaps a few very closely related ones.
Build up a vocabulary of definitions
so the requisite function becomes easily expressible.
Function definition bodies should be no more than 10 lines,
and usually no more than 5.
That's not counting docstrings, comments, or assertions.
(:term:`Params` aren't in the body.)

This rule doesn't apply to imperative scripts used near the top of the call stack
(main, or similar entry points)
once the pure functional bits have been factored out.
At that point, lexical locality is more important for readability,
so it's better to leave them long than to break them up.

Don't break up a single concept just to get under the line quota,
but consider if it could be refactored into a data structure,
or expressed with a more concise macro or tag notation.

Avoid more than four heterogeneous positional parameters without a very good reason,
and preferably no more than three.
This limit doesn't apply to homogeneous star args
(effectively a single tuple arg, positioned last)
or to `kwonly<keyword-only_parameter>` arguments
(effectively a single dict arg),
although that isn't license to overcomplicate functions.
The order of arguments is often meaningless,
and imposing any particular permutation becomes harder to justify the more there are.

Zero or one positional parameters have one obvious answer. Two only has two to consider.
These are fine. Three has six. Are you sure you picked the best one? Did you check?
Four already has 24 permutations, which, realistically,
you're not likely to consider exhaustively,
so you need a good reason to nail down at least one of them.
It just gets worse from there. The factorial sequence grows pretty quickly.
Why not make it easy and use meaningful names instead of meaningless positions?
Sort the kwonly parameters and (argument pairs) lexicographically by default.
You may have a good reason for some other order. E.g.,
if arguments or defaults need to be evaluated in a certain order due to side effects.
Document this kind of thing with a comment when it's not obvious,
or your team might sort them anyway.

Remember that macro definitions can use helper functions.
Some macros are effectively a convenience wrapper over
what could otherwise be a function.
It's best to implement and provide that function as well,
because functions can be easier to compose and pass as arguments.

Newlines
::::::::

Prefer Unix-style LF over the DOS/Windows CRLF for files in version control
that might be used on non-Windows systems.
(Macintosh CR files are obsolete. Modern MacOS and Linux use LF.)
Even on Windows, most code editors can handle LF files.
When in doubt, pick LF.

A file that does not end in a newline is not (strictly speaking) a text file;
they're line *terminators*, not separators.
Although some tooling can handle this particular malformation gracefully,
the Lissp reader cannot in all cases.

`transpile_file` (used by `transpile` and `transpile_packaged`)
always produces LF ``.py`` files, even on Windows.
Python doesn't mind.

Avoid Trailing Whitespace
:::::::::::::::::::::::::

Trailing whitespace is usually a mistake.
For small project with a single author, it's a fairly harmless one.
But for a team project under version control,
it may be the cause of pointless diffs and blames,
reducing the clarity of the history.

It is best practice to at least configure your editor
to make trailing whitespace visible,
although there are many cases you might be viewing code outside your primary editor.

Failing that, automation to automatically strip it is also common practice.
However, trailing whitespace can be significant in multiline :term:`Unicode token`\ s,
and similarly in `Comment`\ s that are not discarded.

Trailing spaces are significant in certain languages you may sometimes
want to embed in your code, such as Markdown.

In the case of :term:`Unicode token`\ s,
it's usually preferable to use explicit escape sequences,
like ``\N{space}``
to clearly indicate to humans that those trailing spaces are intentional,
and so automation does not remove them.
The alternative spellings ``\40`` and ``\x20`` are acceptable (especially for `bytes`),
but not as clear (``\u0020`` and ``\u00000020`` should be avoided in most cases):

.. code-block:: REPL

   #> "\
   #..foobar  \N{space}
   #..spameggs "
   >>> ('foobar   \nspameggs ')
   'foobar   \nspameggs '

Notice that only the last space of a line has to be replaced
in order to make the rest apparent.
Also notice that the last line does not have a trailing space,
even thought the string does,
because the final character for the line is not a space but a ``"``.

`Comment`\ s are raw, but preprocessing can be done at read time, e.g.,

.. code-block:: REPL

   #> '.#
   #..(.format <#
   #.. ;; foobar  {space}
   #.. ;; spameggs{space}
   #.. : space " ")
   >>> 'foobar   \nspameggs '
   'foobar   \nspameggs '

If, for some reason,
you judge that explicitly showing trailing whitespace
in code like this isn't worth it for your case,
you should still at least add a comment indicating it's meant to be there.
It's still up to your team how to deal with automation, if any.
It may be possible to suppress its effect with a special comment
(which would also suffice as notice for programmers familiar with it),
or it may be possible to configure it to ignore violations in strings or comments.

The Limits of Length
::::::::::::::::::::

Readability is mainly laid out on the page.

The optimal length for a line in a block of English text is thought to be around
50-75 characters, given the limitations of the human eye.
More than that, and it gets difficult to find the next line in the return sweep.
Excessively long lines are intimidating and may not get read as carefully.

Lines under about 10 characters can be read vertically with no lateral eye motion,
but lines of 10-50 characters require rapid-eye movements
that become tiresome after too many lines,
which is really only a concern when the ratio of small lines becomes excessive.
The last line in a paragraph may (of course)
be well under 50 characters as it runs out of words.

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
Remember you can use ``\n``, constants, `<# <QzLT_QzHASH_>`,
or `textwrap.dedent` (even at read time).

In rare instances (e.g., URLs), a constant definition containing a one-line string
literal may exceed even the 120-character limit.
Horizontal scrolling or wrapping is perhaps acceptable
for the occasional top-level definition,
but Lissp does give you the option of building constant strings programmatically
at read time.
Use your best judgement on which is more readable.
Multiline strings exceeding the limit are perhaps best read from a separate text file,
although one could perhaps justify embedding resources
when the expected distribution is a single Python file.
Recall that macros can read files at compile time too.

For code lines (that are under the absolute limit of 120),
length should be counted relative to the indent, i.e., the leading spaces don't count,
and neither do the trailing brackets, because we ignore those.
Those are only there for the computer.

Margin comments are like a separate column of text,
so they don't count against the code's line length either,
but they do get their own relative limit starting
from the first word after the semicolon.
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

When choosing where to break a long line of code,
prioritize breaking on closing brackets.
If that's not enough,
convert the outermost affected linear-style form to function style
(or linear macro bodies to block style),
then the next outermost, and so forth, until the lines are short enough.
If that's still not enough,
convert the outermost function-style form to data style,
then the next outermost, and so forth.
Then convert macros with bodies to data style as a last resort
(costs at least a couple of lines and only saves one column).
You need only modify forms containing long lines (or contained in long lines).

.. code-block:: Lissp

   ;; Linear Style
   (function arg1 arg2 arg3)

   ;; Function Style
   (function arg1
             arg2
             arg3)

   ;; Data Style
   (function
    arg1
    arg2
    arg3)

   ;; Macros can be both linear and block style.
   (macro special1 special2 special3 ; Linear arguments.
     body1 ; macro block
     body2
     body3)

   ;; Unusual linear body.
   ;; Convert to block style when converting linear forms to function style.
   (macro special1
     body1 body2 body3)

   ;;; Consider groups like special and body separately.
   ;;; E.g., there's no need to break a linear special group if the long
   ;;; lines are only in the body (and vice-versa).

   ;; Or both function and block style.
   (macro special1
          special2
          special3
     body1
     body2
     body3)

   ;; (macro) data style. Special needs to be data style when body is.
   (macro
    special1
    special2
    special3
    ;; Same indent. Use a body group separator comment. Can be just ;;.
    body1
    body2
    body3)

   ;; OK. All linear, but contains a `)`.
   (function1 arg1 (function2 arg1 arg2) arg2 (function3 arg1 arg2))

   ;; Bad. Break on `)` first.
   (function1 arg1 (function2 arg1 arg2) arg2 (function3 arg1
                                                         arg2))

   ;; OK, but breaking outermost form first is preferable.
   (function1 arg1 arg2 (function2 arg1
                                   arg2))

   ;; Very bad! Confusing style. Break on `)` first!
   (function1 arg1 (function2 arg1
                              arg2) arg2 (function3 arg1 arg2))

   ;; OK. Meaningful groups, even though ``)`` not broken first.
   (cond (test1 x) (function1 arg1 arg2)
         (test2 x) (function2 arg1
                              arg2
                              arg3
                              arg4)
         :else (function3 arg1 arg2))

   ;; Bad. Confusing style.
   (cond (test1 x) (function1 arg1 arg2)
         (test2 argument1
                argument2
                argument3) (function2 arg1
                                      arg2
                                      arg3
                                      arg4)
         :else (function3 arg1 arg2))

   ;; OK.
   (cond (test1 x) (function1 arg1 arg2)
         ;; else if
         (test2 argument1
                argument2
                argument3)
         (function2 arg1
                    arg2
                    arg3
                    arg4)
         :else (function3 arg1 arg2))

   ;; Bad. Meaningless implied groupings.
   (function1 arg1 arg2 (function2 arg1 arg2)
              (function3 arg1 arg2))

   ;; Preferred. Break on `)` first. Groups treated equally.
   ;; Outermost form is function style.
   (function1 arg1
              ;; Inner form in linear style.
              (function2 arg1 arg2 arg3 arg4)
              arg2
              (function3 arg1 arg2))

   ;; Preferred, if above style is too long.
   (function1 arg1
              ;; Function style in function style.
              (function2 arg1
                         arg2
                         arg3
                         arg4)
              arg2
              ;; Short enough to be linear. Linear siblings are OK.
              (function3 arg1 arg2))

   ;; Data style is a last resort. Outermost first.
   (function1
    arg1
    ;; Function style. Linear siblings and data parent are OK.
    (function2 arg1
               arg2
               arg3
               arg4)
    arg2 ; Not a tuple, but technically linear as well: it fits on one line.
    ;; Short enough to be linear.
    (function3 arg1 arg2))

Data style only adds a single column of indentation.
If that's still not enough, you must be doing something crazy, like
a super long atom or about a hundred levels of nesting.
Use your best judgement to find a workaround.

.. rubric:: Footnotes

.. [#ns] Usually a `types.ModuleType` or `types.SimpleNamespace`,
   but most types work, including a simple lambda.
   A namespace can be anything supporting the
   `getattr`/`setattr`/`delattr` protocol.
   Python classes support this by default for their instances
   (in order to support instance variables),
   although, notably, many basic builtin types,
   including any produced by `ast.literal_eval`, do not.
