.. Copyright 2020 Matthew Egan Odendahl
   SPDX-License-Identifier: Apache-2.0

===========
Style Guide
===========

Why have a style guide?

Code was made for the human, not only for the machine,
otherwise we'd all be writing programs in binary.
Code is written once, and rewritten many times.
It is *read* much more than it is written.

*Readability counts.*

To the uninitiated, Lisp is an unreadable homogenous ball of mud.
Lots of Irritating Superfluous Parentheses. That's L.I.S.P.

How can *anyone* even *read* that?

Well, I'll let you in on the secret:
Real Lispers don't actually count the brackets.
It's true.

Don't Count the Brackets
========================

It is impossible for the human to comprehend the code of a nontrivial program in totality;
working memory is too small.
We handle complexity by chunking it into hierarchies of labeled black boxes within boxes within boxes.
Mental recursive trees.

But syntax trees are the very essence of Lisp.
At the bottom of Hissp's hierarchy are tuples of atoms.
(There is, of course, a foundation outside of Hissp of many layers of abstraction even below that.)
Conceptually, it's a box with a label and contents.

::

   LABEL item1 item2 ...

Order matters in Hissp.
These are tuples, not just sets.
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
       (if-else (operator..le n 2)
         n
         (operator..add (fib (operator..sub n 1))
                        (fib (operator..sub n 2))))))

this is what the experienced human sees:

::

   (define fib
     (lambda (n
       (if-else (operator..le n 2
         n
         (operator..add (fib (operator..sub n 1
                        (fib (operator..sub n 2

The indentation is for the human, not the computer.
While this will compile fine,
if you write it this way,
you will make the humans angry:

::

   (define fib(lambda(n)(if-else(
   operator..le n 2)n(operator..add(fib(
   operator..sub n 1))(fib(operator..sub n 2)))))

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
For a beginner, try installing Parinfer in a supported editor, like Atom.
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
or comment on some web forum.
Or maybe you're one of those people who insists on programming in Notepad.
Or maybe you want to write one of these editor tools in the first place.
For these reasons,
I feel the need to spell out what good indentation looks like
well enough that you could do it by hand.

The only absolute rules are

- don't dangle brackets
- unambiguous indentation

If you break these rules,
Parinfer can't be used.
Team projects with any Lissp files should be running Parlinter along with their tests
to enforce this.
Basic legibility is not negotiable. Use it.

don't dangle brackets
---------------------

Trailing brackets are something we try to ignore.
Trailing brackets come in trains.
They do not get their own line;
that's more emphasis than they deserve.
They don't get extra spaces either.

.. code:: Lissp

   ;; Wrong.
   (define fib
     (lambda (n)
       (if-else (operator..le n 2)
         n
         (operator..add (fib (operator..sub n 1)
                         )
                        (fib (operator..sub n 2)
                         )
         )
       )
     )
   )

   ;; Still wrong.
   ( define fib
     ( lambda ( n )
       ( if-else ( operator..le n 2 )
         n
         ( operator..add ( fib ( operator..sub n 1 ) )
                         ( fib ( operator..sub n 2 ) ) ) ) ) )

This also goes for readerless mode.

.. code:: Python

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

.. code:: Python

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

unambiguous indentation
-----------------------

The indentation level indicates which tuple the next line starts in.
Go past the parent's opening bracket, not the sibling's.

.. code:: Lissp

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

The rule is to pass the parent *bracket*.
You might not pass the head *atom* in some alignment styles.

.. code:: Lissp

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

::

   (foo "abc
     xyz")

We can still unambiguously reconstruct the trail.

::

   (foo "abc
     xyz"

Note that the ``"`` is not a bracket,
so we don't delete it or ignore it.

Alignment Styles
================

Keep the elements in a tuple aligned to start on the same column.
Treat siblings groups equally:
If you add a line break for one group,
then put all of its sibling groups on their own line as well.
Keep items within implied groups (like kwargs) together.
Control words used as labels should be grouped with what they label.
Your code should look like these examples:

.. code:: Lissp

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
    arg2                                  ; Not even one space past the (, like data.
    arg3)

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

Identifiers
===========

If you're writing an API that's exposed to the Python side,
avoid unpythonic identifiers
(including package and module names)
in the public interface.
Use the naming styles from PEP 8.

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

See PEP 8 for full details.

``*FOO-BAR*`` is a perfectly valid Lissp identifier,
but it munges to ``xSTAR_FOOxH_BARxSTAR_``,
which is awkward to use from the Python side.

Even in private areas,
let the munger do the work for you.
Avoid writing anything in the x-quoted style yourself.
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

.. code:: Lissp

   (lambda (x) (print "Hi" x) (print "Bye" x)) ;OK

   (lambda (x)                            ;Preferred.
     (print "Hi" x)
     (print "Bye" x))

Implied groups should be kept together.
Closing brackets inside a pair can happen in `cond`,
for example.

.. code:: Lissp

   (lambda (x)
     (cond (operator..lt x 0) (print "negative")
           (operator..eq x 0) (print "zero")
           (operator..gt x 0) (print "positive")
           :else (print "not a number")))

But a train of ``)``'s must not appear inside of a line,
even in an implied group,
because then we'd have to count brackets!
If the train is trailing at the end of the line,
then the tree structure is clear from the indents.
How many is a train?
When you have to count them.

Always breaking at a train of two or more should be considered the default style.

Maybe you can relax this rule in special cases.
But honestly, even two or three in a row is really pushing it.
That's about the most a human can reliably count at a glance.
Consider very seriously if a line break wouldn't be more legible there.
