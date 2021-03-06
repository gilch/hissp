.. Copyright 2020 Matthew Egan Odendahl
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

::

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
               "ifxH_else",
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
       ('ifxH_else',('operator..le','n',2,),
         'n',
         ('operator..add',('fib',('operator..sub','n',1,),),
                          ('fib',('operator..sub','n',2,),),),),),)
   # fmt: on

Note also that tuple commas are used as terminators,
not separators,
even on the same line.
This is to prevent the common error of forgetting the required trailing comma for a single.
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
   There are arguments to be made for using tab indents in other langauges,
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
Exactly what rules *implement* that consistency matters much less
than the consistency itself.
This is not always black and white,
but that doesn't mean all shades of gray are the same.
There may be better and worse approaches,
while other differences are merely taste.

Lisp is one of the oldest programming languages in common use.
It has splintered into many dialects (Lissp among them),
with a common culture, but without perfect agreement in all details.
Lissp's recommended style is based on these,
with some small modifications for its own unique features.

Tuples
------

Separate *top level* forms from each other by a single blank like,
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
Treat siblings groups equally:
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
     data1                                ; Probably only worth it if there's a lot more than 3.
     data2                                ; or it changes frequently. Use this style sparingly.
     data3
     _#_)                                 ;Trails NEVER get their own line.
                                          ; But you can hold it open with a discarded item.

   (function arg1 arg2 arg3)

   ;; The function name is separate from the arguments.
   (function arg1                         ;Break for one, break for all.
             arg2                         ;Args start on the same column.
             arg3)

   ;; The previous alignment is preferred, but this is OK.
   (function
     arg1                                 ;Indented one space past the (, unlike data.
     arg2
     arg3)

   ((lambda (a b c)
      (reticulate a)
      (frobnicate a b c))
    arg1                                  ;The "not past the sibling" rule is absolute.
    arg2                                  ; Not even one space past the (lambda.
    arg3)

   ((lambda (a b c)
      (print c b a))
    arg1 arg2 arg3)                       ;Break for all args or for none.

   ;; One extra space between pairs.
   (function arg1 arg2 : kw1 kwarg1  kw2 kwarg2  kw3 kwarg3)

   (function arg1 arg2
             : kw1 kwarg1  kw2 kwarg2)    ;Breaking groups, not args.

   (function arg1
             arg2
             : kw1 kwarg1                 ;The : starts the line.
             kw2 kwarg2)                  ;Break for args, but pairs stay together.

   (function : kw1 kwarg1                 ;The : starts the "line". Sort of.
             kw2 kwarg2)

   (function
     arg1
     arg2
     :
     kw1
     kwarg1
                                          ;Break for everything, and extra space to separate pairs.
     kw2
     kwarg2)

   (macro special1 special2 special3      ;Macros can have their own alignment rules.
     body1                                ; Simpler macros may look the same as functions.
     body2                                ; Special/body is common. Lambda is also like this.
     body3)

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

Strings
-------

Multiline strings can mess with alignment styles.
Strings are atoms, so this won't affect Parinfer,
but it can impact legibility.
For short strings in simple forms,
don't worry too much, but consider using ``\n``.

For deeply nested multiline strings,
use a dedent string, which can be safely indented:

.. code-block:: REPL

   #> (print (.upper 'textwrap..dedent##"\
   #..               These lines
   #..               Don't interrupt
   #..               the flow."))
   >>> print(
   ...   "These lines\nDon't interrupt\nthe flow.".upper())
   THESE LINES
   DON'T INTERRUPT
   THE FLOW.

Don't forget the quote ``'``.

Long multiline strings should be declared at the `top level`_ and referenced by name.

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
Put the closing quotes for any multiline docstring on its own line.
(Pydoc automatically strips indents.)

Comments
--------

Headings are capitalized, and begin with four semicolons and a space ``;;;; X``.
Subheadings begin with three semicolons and a space ``;;; X``.

These are for the `top level`_ only; they aren't nested in forms;
they get their own line and start at the beginning of it.
They have a blank line before (unless it's the first line) and after.
They organize the code into sections.

Comments about the next form (or group) begin with two semicolons and a space ``;; x``,
and are indented to align as if they were forms,
and are not followed by a blank line.

Comments about a line begin with one semicolon and a space ``; x``,
starting one space after the code. They never get their own line.

Margin comments begin with one semicolon ``;x`` and are aligned to column 40,
or one space after the code, whichever is greater.
The semicolon is not followed by a space unless it continues a
comment from the previous line.
Margin comment continuations may have their own line.

**Never** put a single-semicolon comment on its own line unless
it's a continuation aligned to the margin!
Experience Lispers set their editors to automatically indent these.
You will make them angry when they have to fix all your comments.

Use the drop macro ``_#`` on a string for long block comments.

Commented-out code does not belong in version control,
but it can be helpful to turn things off during development.
You can use the drop macro to comment out code structurally.
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

   ;;; subheading

   ;; Comment about macro
   (macro special1
          ;; Comment about special2 group
          : special2a special2b
          special3 ; Comment about special3 line
          special4 ; Entirely separate comment about special4 line
     body1
     ;; Comment about body2
     body2                                ;Margin comment
     body3)                               ; continuation thereof,
                                          ; and more continuation on its own line.

Docstrings can use some other markup format if the whole team can agree on one,
and it's done for the entire project.
But reStructuredText is the default in the Python ecosystem.
You can automatically generate API documentation with these.

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
but it munges to ``xSTAR_FOOxH_BARxSTAR_``,
which is awkward to use from the Python side.

Even in private areas,
let the munger do the munging for you.
Avoid writing anything in the x-encoded style yourself.
This can confuse the demunger and cause collisions with gensyms.

Docstrings use reStructuredText markup, like Python.
Any docstring for something with a munged name
should start with the demunged name in doubled backticks
(this includes anything with a hyphen),
followed by the pronunciation in single quotes,
if it's not obvious from the identifier::

  "``&&`` 'and'. Like Python's ``and`` operator, but for any number of arguments."

The End of the Line
===================

Any closing bracket should also end the line.
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

   (print (/ (sum xs) (len xs)) "on average.") ;Bad.

   (print (+ (sum xs) (len xs))           ;OK.
          "on average.")

   (print (+ (sum xs)                     ;Preferred.
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

   (define compare                        ;OK, but the blank lines smell.
     (lambda (xs ys)
       (cond (eq (len xs)
                 (len ys))
             (print "0")

             (lt (len xs)
                 (len ys))
             (print "<")

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

