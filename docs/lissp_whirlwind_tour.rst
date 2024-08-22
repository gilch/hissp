.. Copyright 2020, 2021, 2022, 2023, 2024 Matthew Egan Odendahl
   SPDX-License-Identifier: Apache-2.0

.. This hidden doctest adds bundled macros for REPL-consistent behavior.
   #> (.update (globals) : _macro_ (types..SimpleNamespace : :** (vars hissp.._macro_)))
   >>> globals().update(
   ...   _macro_=__import__('types').SimpleNamespace(
   ...             **vars(
   ...                 __import__('hissp')._macro_)))

.. TODO: Interactive via web repl?

Lissp Whirlwind Tour
====================

.. raw:: html

   (<a href="_sources/lissp_whirlwind_tour.rst.txt">Outputs</a> hidden for brevity.)

.. Lissp::

   "Lissp is a lightweight text language representing the Hissp
   intermediate language. The Lissp reader parses the Lissp language's
   symbolic expressions as Python objects. The Hissp compiler
   then translates these syntax trees to Python expressions.

   This document is written like a .lissp file, thoroughly demonstrating
   Lissp's (and thereby Hissp's) features from the bottom up with
   minimal exposition. This element enclosed in double quotes is a
   docstring for the module.

   To fully understand these examples, you must see their Python
   compilation and output. Some familiarity with Python is assumed.
   Install the Hissp version matching this document. Follow along by
   entering these examples in the REPL. It will show you the compiled
   Python and evaluate it. Try variations that occur to you.

   Familiarity with another Lisp dialect is not assumed, but helpful. If
   you get confused or stuck, look for the Hissp community chat or try the
   more expository Hissp Primer.

   You are expected to read through the sections in order. New concepts
   will be presented incrementally. Examples of a new concept will
   otherwise be limited to what has been demonstrated so far, which may
   not be their most natural expression.
   "

   ;;;; 1 Installation

   ;;; These docs are for the latest development version of Hissp.
   ;;; Install the latest Hissp version with
   ;;; $ pip install git+https://github.com/gilch/hissp
   ;;; Uninstall any old versions first,
   ;;; or start in a fresh virtual environment.
   ;;; Start the REPL with
   ;;; $ lissp
   ;;; You can quit with EOF or (exit).

   ;;; Most examples are tested automatically, but details may be dated.
   ;;; Report issues or try the current release version instead.

   ;;;; 2 Simple Atoms

   ;;; To a first approximation, the Hissp intermediate language is made
   ;;; of Python data representing syntax trees. The nodes are tuples
   ;;; and the leaves are called "atoms". Simple atoms in Lissp are
   ;;; written the same way as Python. Skim if you've seen these before.

   ;;;; 2.1 Singleton

   #> None
   >>> None

   #> ...                                 ;Ellipsis
   >>> ...
   Ellipsis


   ;;;; 2.2 Boolean

   #> False                               ;False == 0
   >>> False
   False

   #> True                                ;True == 1
   >>> True
   True


   ;;;; 2.3 Integer

   #> 42
   >>> (42)
   42

   #> -10_000
   >>> (-10000)
   -10000

   #> 0x10
   >>> (16)
   16

   #> 0o10
   >>> (8)
   8

   #> 0b10
   >>> (2)
   2

   #> 0b1111_0000_0000
   >>> (3840)
   3840

   #> 0xF00
   >>> (3840)
   3840


   ;;;; 2.4 Floating-Point

   #> 3.
   >>> (3.0)
   3.0

   #> -4.2
   >>> (-4.2)
   -4.2

   #> 4e2
   >>> (400.0)
   400.0

   #> -1.6e-2
   >>> (-0.016)
   -0.016


   ;;;; 2.5 Complex

   #> 5j                                  ;imaginary
   >>> (5j)
   5j

   #> 4+2j                                ;complex
   >>> ((4+2j))
   (4+2j)

   #> -1_2.3_4e-5_6-7_8.9_8e-7_6j         ;Very complex!
   >>> ((-1.234e-55-7.898e-75j))
   (-1.234e-55-7.898e-75j)


   ;;;; 3 Simple Tuples

   ;; Tuples can group any atoms with (). Data tuples start with an apostrophe.
   #> '(None 2 3)
   >>> (None,
   ...  (2),
   ...  (3),)
   (None, 2, 3)

   #> '(True
   #..  False)
   >>> (True,
   ...  False,)
   (True, False)


   ;;;; 4 Symbolic Atoms

   ;;;; 4.1 Identifiers

   #> object                              ;Python identifiers work in Lissp.
   >>> object
   <class 'object'>

   #> object.__class__                    ;Attribute identifier with dot, as Python.
   >>> object.__class__
   <class 'type'>

   #> object.__class__.__name__           ;Attributes chain.
   >>> object.__class__.__name__
   'type'


   ;;;; 4.2 Imports

   #> math.                               ;Module handles import!
   >>> __import__('math')
   <module 'math' ...>

   #> math..tau                           ;Fully-qualified identifier. (Module attribute.)
   >>> __import__('math').tau
   6.283185307179586

   #> collections.abc.                    ;Submodule handle. Has package name.
   >>> __import__('collections.abc',fromlist='?')
   <module 'collections.abc' from '...abc.py'>


   #> builtins..object.__class__          ;Qualified attribute identifier.
   >>> __import__('builtins').object.__class__
   <class 'type'>

   #> collections.abc..Sequence.__class__.__name__ ;Chaining.
   >>> __import__('collections.abc',fromlist='?').Sequence.__class__.__name__
   'ABCMeta'


   ;;;; 5 Simple Forms and Calls

   ;;; "Forms" are any data structures that can be evaluated as a Hissp program.
   ;;; Simple atoms are forms. They simply evaluate to an equivalent object.

   #> 0x2a
   >>> (42)
   42


   ;;; Tuples can also be forms, but their evaluation rules are more complex.
   ;;; The common case is a function call. For that, the first element must
   ;;; be a callable. The remainder are arguments.

   #> (print 1 2 3)                       ;This one compiles to a function call.
   >>> print(
   ...   (1),
   ...   (2),
   ...   (3))
   1 2 3

   #> '(print 1 2 3)                      ;This one is a data tuple.
   >>> ('print',
   ...  (1),
   ...  (2),
   ...  (3),)
   ('print', 1, 2, 3)


   ;;; Data tuples and calls are enough to make simple collections.

   #> '(1 2 3)                            ;tuple
   >>> ((1),
   ...  (2),
   ...  (3),)
   (1, 2, 3)

   #> (list '(1 2 3))
   >>> list(
   ...   ((1),
   ...    (2),
   ...    (3),))
   [1, 2, 3]

   #> (set '(1 2 3))
   >>> set(
   ...   ((1),
   ...    (2),
   ...    (3),))
   {1, 2, 3}

   #> (dict '((1 2) (3 4)))               ;Note the nested tuples!
   >>> dict(
   ...   (((1),
   ...     (2),),
   ...    ((3),
   ...     (4),),))
   {1: 2, 3: 4}

   #> (bytes '(98 121 116 101 115))
   >>> bytes(
   ...   ((98),
   ...    (121),
   ...    (116),
   ...    (101),
   ...    (115),))
   b'bytes'


   #> (help sum)                          ;Python's online help function still works.
   >>> help(
   ...   sum)
   Help on built-in function sum in module builtins:
   <BLANKLINE>
   sum(iterable, /, start=0)
       Return the sum of a 'start' value (default: 0) plus an iterable of numbers
   <BLANKLINE>
       When the iterable is empty, return the start value.
       This function is intended specifically for use with numeric values and may
       reject non-numeric types.
   <BLANKLINE>


   ;;;; 6 Fragments

   ;;; To a first approximation, fragments can stand in for any other
   ;;; type of atom, because they compile as Python expressions.

   #> |1+1|                               ;Any Python expression. (Addition)
   >>> 1+1
   2

   #> |1||2|                              ;Escape | by doubling it. (Bitwise OR)
   >>> 1|2
   3


   ;;; At the top level, even non-expression lines can work.

   ;; Shebang line.
   #> |#!usr/bin/python -m hissp|
   >>> #!usr/bin/python -m hissp

   ;; A star import statement. It's just Python. But with more ||s.
   #> |from operator import *|            ;All your operator are belong to us.
   >>> from operator import *


   ;;; Data fragments compile to string literals.

   #> '|1+1|                              ;Make data fragments with an apostrophe.
   >>> '1+1'
   '1+1'

   #> '|Hello, World!|
   >>> 'Hello, World!'
   'Hello, World!'

   #> '|No\nEscape|                       ;Backslash is taken literally. (Raw string.)
   >>> 'No\\nEscape'
   'No\\nEscape'


   #> |:control word|                     ;Colon prefix. Similar to Lisp ":keywords".
   >>> ':control word'
   ':control word'


   #> :control-word                       ;You can drop the || in this case.
   >>> ':control-word'
   ':control-word'

   #> |dict|                              ;Any Python expression. (Identifier)
   >>> dict
   <class 'dict'>

   #> dict                                ;You can drop the || in this case too.
   >>> dict
   <class 'dict'>


   ;;;; 6.1 Munging

   #> '+                                  ;Read-time munging of invalid identifiers.
   >>> 'QzPLUS_'
   'QzPLUS_'

   #> 'Also-a-symbol!                     ;Alias for 'AlsoQz_aQz_symbolQzBANG_
   >>> 'AlsoQz_aQz_symbolQzBANG_'
   'AlsoQz_aQz_symbolQzBANG_'

   #> '𝐀                                  ;Alias for 'A (unicode normal form KC)
   >>> 'A'
   'A'

   #> '-<>>
   >>> 'Qz_QzLT_QzGT_QzGT_'
   'Qz_QzLT_QzGT_QzGT_'

   #> :-<>>                               ;Doesn't represent identifier; doesn't munge.
   >>> ':-<>>'
   ':-<>>'

   #> :                                   ;Shortest a control word.
   >>> ':'
   ':'


   ;;;; 6.2 Escaping with \

   #> 'SPAM\ \"\(\)\;EGGS                 ;These would terminate a symbol if not escaped.
   >>> 'SPAMQzSPACE_QzQUOT_QzLPAR_QzRPAR_QzSEMI_EGGS'
   'SPAMQzSPACE_QzQUOT_QzLPAR_QzRPAR_QzSEMI_EGGS'

   #> '\42                                ;Digits can't start identifiers.
   >>> 'QzDIGITxFOUR_2'
   'QzDIGITxFOUR_2'

   #> '\.
   >>> 'QzFULLxSTOP_'
   'QzFULLxSTOP_'

   #> '\\
   >>> 'QzBSOL_'
   'QzBSOL_'

   #> '\a\b\c                             ;Escapes allowed, but not required here.
   >>> 'abc'
   'abc'

   #> 1\2                                 ;Backslashes work in other atoms.
   >>> (12)
   12

   #> N\one
   >>> None


   #> |:control word|                     ;Remember this?
   >>> ':control word'
   ':control word'

   #> :control\ word                      ;This also works.
   >>> ':control word'
   ':control word'


   ;;;; 6.3 String Literals

   #> |"a string"|                        ;Any Python expression. (String literal)
   >>> "a string"
   'a string'


   #> "a string"                          ;You can also drop the || in this case.
   >>> ('a string')
   'a string'

   #> 'not-string'                        ;Symbol
   >>> 'notQz_stringQzAPOS_'
   'notQz_stringQzAPOS_'


   #> '|"a string"|
   >>> '"a string"'
   '"a string"'

   #> '"a string"                         ;What did you expect?
   >>> "('a string')"
   "('a string')"

   #> "Say \"Cheese!\" \u263a"            ;Python escape sequences.
   >>> ('Say "Cheese!" ☺')
   'Say "Cheese!" ☺'


   ;; || tokens can't have newlines, by the way. But "" tokens can.
   #> "string
   #..with
   #..newlines
   #.."                                   ;Same as "string\nwith\nnewlines\n".
   >>> ('string\nwith\nnewlines\n')
   'string\nwith\nnewlines\n'


   ;;;; 7 Advanced Calls

   #> (dict :)                            ;Left paren before function! Notice the :.
   >>> dict()
   {}


   ;; All arguments pair with a target! No commas!
   #> (dict : spam "foo"  eggs "bar"  ham "baz")
   >>> dict(
   ...   spam=('foo'),
   ...   eggs=('bar'),
   ...   ham=('baz'))
   {'spam': 'foo', 'eggs': 'bar', 'ham': 'baz'}


   #> (print : :? 1  :? 2  :? 3  sep "-") ;:? is a positional target.
   >>> print(
   ...   (1),
   ...   (2),
   ...   (3),
   ...   sep=('-'))
   1-2-3

   #> (print 1 : :? 2  :? 3  sep "-")     ;Arguments before : implicitly pair with :?.
   >>> print(
   ...   (1),
   ...   (2),
   ...   (3),
   ...   sep=('-'))
   1-2-3

   #> (print 1 2 : :? 3  sep "-")         ;Keep sliding : over. It's shorter.
   >>> print(
   ...   (1),
   ...   (2),
   ...   (3),
   ...   sep=('-'))
   1-2-3

   #> (print 1 2 3 : sep "-")             ;Next isn't a :?. The : stops here.
   >>> print(
   ...   (1),
   ...   (2),
   ...   (3),
   ...   sep=('-'))
   1-2-3


   #> (print 1                            ;Implicitly a positional :? target.
   #..       : :* "abc"                   ;Target :* to unpack iterable.
   #..       :? 2                         ;:? is still allowed after :*.
   #..       :* "xyz"                     ;:* is a repeatable positional target.
   #..       :** (dict : sep "-")         ;Target :** to unpack mapping.
   #..       flush True                   ;Kwargs still allowed after :**.
   #..       :** (dict : end "!?\n"))     ;Multiple :** allowed too.
   >>> print(
   ...   (1),
   ...   *('abc'),
   ...   (2),
   ...   *('xyz'),
   ...   **dict(
   ...       sep=('-')),
   ...   flush=True,
   ...   **dict(
   ...       end=('!?\n')))
   1-a-b-c-2-x-y-z!?


   #> (print : :? "Hello, World!")
   >>> print(
   ...   ('Hello, World!'))
   Hello, World!

   #> (print "Hello, World!" :)           ;Same. Slid : over. Compare.
   >>> print(
   ...   ('Hello, World!'))
   Hello, World!

   #> (print "Hello, World!")             ;No : is the same as putting it last!
   >>> print(
   ...   ('Hello, World!'))
   Hello, World!


   #> (.upper "shout!")                   ;Method calls need a . and a "self".
   >>> ('shout!').upper()
   'SHOUT!'

   #> (.float builtins. 'inf)             ;Method call syntax, though not a method.
   >>> __import__('builtins').float(
   ...   'inf')
   inf

   #> (builtins..float 'inf)              ;Same effect, but not method syntax.
   >>> __import__('builtins').float(
   ...   'inf')
   inf


   ;;;; 7.1 Operators

   ;;; Hissp is simpler than Python. No operators! Use calls instead.

   #> (operator..add 40 2)
   >>> __import__('operator').add(
   ...   (40),
   ...   (2))
   42


   ;; We'll be reusing this one in later sections.
   #> (.update (globals) : + operator..add) ;Assignment. Identifier munged.
   >>> globals().update(
   ...   QzPLUS_=__import__('operator').add)


   #> (+ 40 2)                            ;No operators. This is still a function call!
   >>> QzPLUS_(
   ...   (40),
   ...   (2))
   42


   ;;;; 8 Simple Lambdas

   ;;; Lambdas are one of Hissp's two "special forms".
   ;;; They look like calls, but are special-cased in the Hissp compiler
   ;;; to work differently. The first element must be 'lambda', the second
   ;;; is the parameters, and finally the body.

   #> (.update (globals)
   #..         : greet
   #..         (lambda (salutation name)
   #..           (print (.format "{}, {}!"
   #..                           (.title salutation)
   #..                           name))))
   >>> globals().update(
   ...   greet=(lambda salutation, name:
   ...             print(
   ...               ('{}, {}!').format(
   ...                 salutation.title(),
   ...                 name))
   ...         ))

   #> (greet "hello" "World")
   >>> greet(
   ...   ('hello'),
   ...   ('World'))
   Hello, World!

   #> (greet "hi" "Bob")
   >>> greet(
   ...   ('hi'),
   ...   ('Bob'))
   Hi, Bob!


   ;;;; 8.1 Obligatory Factorial I

   ;;; We now have just enough to make more interesting programs.

   #> (.update (globals)
   #..         : factorial_I
   #..         (lambda (i)
   #..           (functools..reduce operator..mul
   #..                              (range i 0 -1)
   #..                              1)))
   >>> globals().update(
   ...   factorial_I=(lambda i:
   ...                   __import__('functools').reduce(
   ...                     __import__('operator').mul,
   ...                     range(
   ...                       i,
   ...                       (0),
   ...                       (-1)),
   ...                     (1))
   ...               ))

   #> (factorial_I 0)
   >>> factorial_I(
   ...   (0))
   1

   #> (factorial_I 3)
   >>> factorial_I(
   ...   (3))
   6

   #> (factorial_I 5)
   >>> factorial_I(
   ...   (5))
   120


   ;;;; 8.2 Control Flow

   ;;; Hissp is simpler than Python. No control flow! Use higher-order functions instead.

   #> (any (map print "abc"))               ;Loops!
   >>> any(
   ...   map(
   ...     print,
   ...     ('abc')))
   a
   b
   c
   False


   ((.get (dict : y (lambda () (print "Yes!")) ;Branches!
                n (lambda () (print "Canceled.")))
          (input "enter y/n> ")
          (lambda () (print "Unrecognized input."))))

   ;;; Don't worry, Hissp metaprogramming will make this much easier
   ;;; (and Hissp comes bundled with macros for these things), but our
   ;;; limited tools so far are enough for a ternary operator.

   #> (.update (globals) : bool->caller (dict))
   >>> globals().update(
   ...   boolQz_QzGT_caller=dict())


   ;; True calls left.
   #> (operator..setitem bool->caller True (lambda (L R) (L)))
   >>> __import__('operator').setitem(
   ...   boolQz_QzGT_caller,
   ...   True,
   ...   (lambda L, R: L()))


   ;; False calls right.
   #> (operator..setitem bool->caller False (lambda (L R) (R)))
   >>> __import__('operator').setitem(
   ...   boolQz_QzGT_caller,
   ...   False,
   ...   (lambda L, R: R()))


   #> (.update (globals)
   #..         : ternary
   #..         (lambda (condition then_thunk else_thunk)
   #..           ((operator..getitem bool->caller (bool condition))
   #..            then_thunk else_thunk)))
   >>> globals().update(
   ...   ternary=(lambda condition, then_thunk, else_thunk:
   ...               __import__('operator').getitem(
   ...                 boolQz_QzGT_caller,
   ...                 bool(
   ...                   condition))(
   ...                 then_thunk,
   ...                 else_thunk)
   ...           ))


   ;;;; 8.3 Obligatory Factorial II

   ;; Now we have enough for a recursive version.
   #> (.update (globals)
   #..         : factorial_II
   #..         (lambda (i)
   #..           (ternary (operator..le i 1)
   #..                    (lambda () 1)
   #..                    (lambda ()
   #..                      (operator..mul i (factorial_II (operator..sub i 1)))))))
   >>> globals().update(
   ...   factorial_II=(lambda i:
   ...                    ternary(
   ...                      __import__('operator').le(
   ...                        i,
   ...                        (1)),
   ...                      (lambda : (1)),
   ...                      (lambda :
   ...                          __import__('operator').mul(
   ...                            i,
   ...                            factorial_II(
   ...                              __import__('operator').sub(
   ...                                i,
   ...                                (1))))
   ...                      ))
   ...                ))

   #> (factorial_II 5)
   >>> factorial_II(
   ...   (5))
   120


   ;;;; 9 Advanced Lambdas

   ;; Python parameter types are rather involved. Lambda does all of them.
   ;; Like calls, they are all pairs. :? means no default.
   #> (lambda (: a :?  b :?  :/ :?        ;positional only
   #..         c :?  d :?                 ;normal
   #..         e 1  f 2                   ;default
   #..         :* args  h 4  i :?  j 1    ;star args, key word
   #..         :** kwargs)
   #..  ;; Body. (Lambdas return empty tuple when body is empty.)
   #..  (print (globals))
   #..  (print (locals))                  ;side effects
   #..  b)                                ;last value is returned
   >>> (
   ...  lambda a,
   ...         b,
   ...         /,
   ...         c,
   ...         d,
   ...         e=(1),
   ...         f=(2),
   ...         *args,
   ...         h=(4),
   ...         i,
   ...         j=(1),
   ...         **kwargs:
   ...    (print(
   ...       globals()),
   ...     print(
   ...       locals()),
   ...     b)  [-1]
   ... )
   <function <lambda> at 0x...>


   #> (lambda (: a :?  b :?  c 1))        ;Note the : separator like calls.
   >>> (
   ...  lambda a,
   ...         b,
   ...         c=(1):
   ...     ())
   <function <lambda> at 0x...>

   #> (lambda (a : b :?  c 1))            ;`a` now implicitly paired with :?.
   >>> (
   ...  lambda a,
   ...         b,
   ...         c=(1):
   ...     ())
   <function <lambda> at 0x...>

   #> (lambda (a b : c 1))                ;Next isn't paired with :?. The : stops here.
   >>> (
   ...  lambda a,
   ...         b,
   ...         c=(1):
   ...     ())
   <function <lambda> at 0x...>


   #> (lambda (: :* a))                   ;Star arg must pair with star, as Python.
   >>> (lambda *a: ())
   <function <lambda> at 0x...>

   #> (lambda (: :* :?  x :?))            ;Empty star arg, so x is keyword only.
   >>> (lambda *, x: ())
   <function <lambda> at 0x...>

   #> (lambda (:* : x :?))                ;Slid : over one. Still a kwonly.
   >>> (lambda *, x: ())
   <function <lambda> at 0x...>

   #> (lambda (:* x :))                   ;Implicit :? is the same. Compare.
   >>> (lambda *, x: ())
   <function <lambda> at 0x...>

   #> (lambda (:* a))                     ;Kwonly! Not star arg! Final : implied.
   >>> (lambda *, a: ())
   <function <lambda> at 0x...>


   #> (lambda (a b : x None  y None))     ;Normal, then positional defaults.
   >>> (
   ...  lambda a,
   ...         b,
   ...         x=None,
   ...         y=None:
   ...     ())
   <function <lambda> at 0x...>

   #> (lambda (:* a b : x None  y None))  ;Keyword only, then keyword defaults.
   >>> (
   ...  lambda *,
   ...         a,
   ...         b,
   ...         x=None,
   ...         y=None:
   ...     ())
   <function <lambda> at 0x...>


   #> (lambda (spam eggs) eggs)           ;Simple cases look like other Lisps, but
   >>> (lambda spam, eggs: eggs)
   <function <lambda> at 0x...>

   #> ((lambda abc                        ; params not strictly required to be a tuple.
   #..   (print c b a))                   ;There are three parameters.
   #.. 3 2 1)
   >>> (lambda a, b, c:
   ...     print(
   ...       c,
   ...       b,
   ...       a)
   ... )(
   ...   (3),
   ...   (2),
   ...   (1))
   1 2 3


   #> (lambda (:))                        ;Explicit : still allowed with no params.
   >>> (lambda : ())
   <function <lambda> at 0x...>

   #> (lambda : (print "oops"))           ;Thunk resembles Python.
   >>> (lambda :
   ...     print(
   ...       ('oops'))
   ... )
   <function <lambda> at 0x...>

   #> ((lambda :x1 x))                    ;Control words are strings are iterable.
   >>> (lambda x=1: x)()
   1


   ;;;; 10 Quote

   ;;; Quote is the only other special form. Looks like a call, but isn't.

   ;;; A "form" is any Hissp data that can be evaluated.
   ;;; Not all data is a valid program in Hissp. E.g., ``(7 42)`` is a
   ;;; tuple, containing the integers 7 in the function position, and 42
   ;;; after in the first argument position. It would compile to a
   ;;; syntactically-valid Python program, but evaluation would crash,
   ;;; because ints are not callable in Python. Try it.

   ;;; Quotation suppresses evaluation of Hissp data.
   ;;; Treating the code itself as data is the key concept in metaprogramming.

   #> (quote (7 42))
   >>> ((7),
   ...  (42),)
   (7, 42)


   ;;; Other objects evaluate to themselves, but str atoms and tuples have
   ;;; special evaluation rules in Hissp. Tuples represent invocations of
   ;;; functions, macros, and special forms.

   #> (quote (print 1 2 3 : sep "-"))     ;Just a tuple.
   >>> ('print',
   ...  (1),
   ...  (2),
   ...  (3),
   ...  ':',
   ...  'sep',
   ...  "('-')",)
   ('print', 1, 2, 3, ':', 'sep', "('-')")


   ;;; Notice how the atom read from "-" gets an extra layer of quotes vs
   ;;; the identifiers. This particular tuple happens to be a valid form.

   ;; The readerless function runs the Hissp compiler without the Lissp reader.
   ;; (Remember, _ is the last result that wasn't None in the Python REPL.)
   #> (hissp.compiler..readerless _)      ;It compiles to Python
   >>> __import__('hissp.compiler',fromlist='?').readerless(
   ...   _)
   "print(\n  (1),\n  (2),\n  (3),\n  sep=('-'))"

   #> (eval _)                            ; and Python can evaluate that.
   >>> eval(
   ...   _)
   1-2-3


   ;;; Programmatically modifying the data before compiling it is when
   ;;; things start to get interesting, but more on that later.

   ;;; Hissp-level str atoms contain Python code to include in the compiled
   ;;; output. These often contain identifiers, but can be anything.
   ;;; Thus, Lissp identifiers (and fragments in general) read as str
   ;;; atoms at the Hissp level.

   #> (quote identifier)                  ;Just a string.
   >>> 'identifier'
   'identifier'


   ;;; The "" tokens in Lissp also read as str atoms at the Hissp level,
   ;;; but they contain a Python string literal instead of an identifier.

   #> (quote "a string")
   >>> "('a string')"
   "('a string')"

   #> (eval (quote "a string"))           ;Python code. For a string.
   >>> eval(
   ...   "('a string')")
   'a string'


   ;;; Quoting does not suppress munging, however. That happens at read
   ;;; time. Quoting doesn't happen until compile time.

   #> (quote +)
   >>> 'QzPLUS_'
   'QzPLUS_'


   ;; Quoting works on any Hissp data.
   #> (quote 42)                          ;Just a number. It was before though.
   >>> (42)
   42


   ;;; Strings in Hissp are also used for module handles and control
   ;;; words. The compiler does some extra processing before emitting these
   ;;; as Python code. Quoting suppresses this processing too.

   #> math.                               ;Compiler coverts this to an import.
   >>> __import__('math')
   <module 'math' ...>

   #> (quote math.)                       ;Quoting suppresses. No __import__.
   >>> 'math.'
   'math.'

   #> (quote :?)                          ;Just a string. It was before though?
   >>> ':?'
   ':?'

   #> :?                                  ;Just a string?
   >>> ':?'
   ':?'

   #> ((lambda (: a :?) a))               ;Oops, not quite! Contextual meaning here.
   >>> (lambda a: a)()
   Traceback (most recent call last):
     ...
   TypeError: <lambda>() missing 1 required positional argument: 'a'

   #> ((lambda (: a (quote :?)) a))       ;Just a string. Even in context.
   >>> (lambda a=':?': a)()
   ':?'


   ;;;; 11 Simple Reader Macros

   ;;; Reader macros are metaprograms to abbreviate Hissp and don't
   ;;; represent it directly. Tags apply to the next parsed Hissp object
   ;;; at read time, before the Hissp compiler sees it, and thus before
   ;;; they are compiled and evaluated. Tags end in # except for a few
   ;;; builtins-- ' ` , ,@

   ;;;; 11.1 Quote

   ;;; The ' reader macro is simply an abbreviation for the quote special form.

   #> 'x                                  ;(quote x). Symbols are just quoted identifiers!
   >>> 'x'
   'x'

   #> '(print "Hi")                       ;Quote to reveal the Hissp syntax tree.
   >>> ('print',
   ...  "('Hi')",)
   ('print', "('Hi')")


   ;;;; 11.2 Template Quote

   ;;; (Like quasiquote, backquote, or syntax-quote from other Lisps.)
   ;;; This is a DSL for making Hissp trees programmatically.
   ;;; They're very useful for metaprogramming.

   #> `print                              ;Automatic full qualification!
   >>> 'builtins..print'
   'builtins..print'

   #> `foo+2                              ;Not builtin. Still munges.
   >>> '__main__..fooQzPLUS_2'
   '__main__..fooQzPLUS_2'


   #> `(print "Hi")                       ;Code as data. Seems to act like quote.
   >>> (lambda * _:  _)(
   ...   'builtins..print',
   ...   "('Hi')")
   ('builtins..print', "('Hi')")

   #> '`(print "Hi")                      ;But it's making a program to create the data.
   >>> (('lambda',
   ...   (':',
   ...    ':*',
   ...    ' _',),
   ...   ' _',),
   ...  ':',
   ...  ':?',
   ...  ('quote',
   ...   'builtins..print',),
   ...  ':?',
   ...  ('quote',
   ...   "('Hi')",),)
   (('lambda', (':', ':*', ' _'), ' _'), ':', ':?', ('quote', 'builtins..print'), ':?', ('quote', "('Hi')"))

   #> `(print ,(.upper "Hi"))             ;Unquote (,) interpolates.
   >>> (lambda * _:  _)(
   ...   'builtins..print',
   ...   ('Hi').upper())
   ('builtins..print', 'HI')


   #> `(,'foo+2 foo+2)                    ;Interpolations not auto-qualified!
   >>> (lambda * _:  _)(
   ...   'fooQzPLUS_2',
   ...   '__main__..fooQzPLUS_2')
   ('fooQzPLUS_2', '__main__..fooQzPLUS_2')

   #> `(print ,@"abc")                    ;Splice unquote (,@) interpolates and unpacks.
   >>> (lambda * _:  _)(
   ...   'builtins..print',
   ...   *('abc'))
   ('builtins..print', 'a', 'b', 'c')

   #> `(print (.upper "abc"))             ;Template quoting is recursive
   >>> (lambda * _:  _)(
   ...   'builtins..print',
   ...   (lambda * _:  _)(
   ...     '.upper',
   ...     "('abc')"))
   ('builtins..print', ('.upper', "('abc')"))

   #> `(print ,@(.upper "abc"))           ; unless suppressed by an unquote.
   >>> (lambda * _:  _)(
   ...   'builtins..print',
   ...   *('abc').upper())
   ('builtins..print', 'A', 'B', 'C')


   ;;; Full qualification prevents accidental name collisions in
   ;;; programmatically generated code. But full qualification doesn't work
   ;;; on local variables, which can't be imported. For these, we use a $#
   ;;; (gensym) which (instead of a qualifier) adds a prefix to ensure a
   ;;; variable can only be used in the same template it was defined in. It
   ;;; contains a hash of three things: the code being read, __name__, and
   ;;; a count of the templates the reader has seen so far.

   #> `($#eggs $#spam $#bacon $#spam)
   >>> (lambda * _:  _)(
   ...   '_QzIWMX5OB2z___eggs',
   ...   '_QzIWMX5OB2z___spam',
   ...   '_QzIWMX5OB2z___bacon',
   ...   '_QzIWMX5OB2z___spam')
   ('_QzIWMX5OB2z___eggs', '_QzIWMX5OB2z___spam', '_QzIWMX5OB2z___bacon', '_QzIWMX5OB2z___spam')

   ;; Each new template increases the count, so it results in a new hash,
   #> `$#spam
   >>> '_QzIOSOZAXYz___spam'
   '_QzIOSOZAXYz___spam'

   ;; even if the code is identical.
   #> `$#spam
   >>> '_QzY6OWMZS7z___spam'
   '_QzY6OWMZS7z___spam'

   ;;; However, the hashing procedure is fully deterministic, so builds are
   ;;; reproducible even when they contain generated symbols.

   ;; If you don't specify, by default, the gensym hash is a prefix,
   ;; but you can put them anywhere in the symbol; $ marks the positions.
   ;; Lacking a gensym prefix, it gets fully qualified by the template.
   #> `$#spam$.$eggs$
   >>> '__main__..spam_QzA4IBV7J7z___._QzA4IBV7J7z___eggs_QzA4IBV7J7z___'
   '__main__..spam_QzA4IBV7J7z___._QzA4IBV7J7z___eggs_QzA4IBV7J7z___'


   ;; This is typically used for partially-qualified variables,
   ;; i.e., with an explicit namespace that is not a module handle.
   ;; The interpolation suppressed auto-qualification.
   #> `,'$#self.$foo
   >>> 'self._Qz7UU6WAD6z___foo'
   'self._Qz7UU6WAD6z___foo'


   ;;; You can use templates to make collections with interpolated values.
   ;;; When your intent is to create data rather than code, unquote
   ;;; each element.

   ;; (Uses `+` from §7.1.)
   #> (list `(,@"abc"
   #..        ,1
   #..        ,(+ 1 1)
   #..        ,(+ 1 2)))
   >>> list(
   ...   (lambda * _:  _)(
   ...     *('abc'),
   ...     (1),
   ...     QzPLUS_(
   ...       (1),
   ...       (1)),
   ...     QzPLUS_(
   ...       (1),
   ...       (2))))
   ['a', 'b', 'c', 1, 2, 3]


   #> `(0 "a" 'b)                         ;Beware of "" tokens and symbols.
   >>> (lambda * _:  _)(
   ...   (0),
   ...   "('a')",
   ...   (lambda * _:  _)(
   ...     'quote',
   ...     '__main__..b'))
   (0, "('a')", ('quote', '__main__..b'))

   #> `(,0 ,"a" ,'b)                      ;Just unquote everything in data templates.
   >>> (lambda * _:  _)(
   ...   (0),
   ...   ('a'),
   ...   'b')
   (0, 'a', 'b')


   #> (dict `((,0 ,1)
   #..        ,@(.items (dict : spam "eggs"  foo 2)) ;dict unpacking
   #..        (,3 ,4)))
   >>> dict(
   ...   (lambda * _:  _)(
   ...     (lambda * _:  _)(
   ...       (0),
   ...       (1)),
   ...     *dict(
   ...        spam=('eggs'),
   ...        foo=(2)).items(),
   ...     (lambda * _:  _)(
   ...       (3),
   ...       (4))))
   {0: 1, 'spam': 'eggs', 'foo': 2, 3: 4}


   ;;;; 12 Compiler Macros

   ;;; We can use functions to to create forms for evaluation.
   ;;; This is metaprogramming: code that writes code.

   #> (.update (globals)                  ;assign fills in a template to make a form.
   #..         : assign
   #..         (lambda (key value)
   #..           `(.update (globals) : ,key ,value)))
   >>> globals().update(
   ...   assign=(lambda key, value:
   ...              (lambda * _:  _)(
   ...                '.update',
   ...                (lambda * _:  _)(
   ...                  'builtins..globals'),
   ...                ':',
   ...                key,
   ...                value)
   ...          ))


   ;; Notice the arguments to it are quoted.
   #> (assign 'SPAM '"eggs")              ;The result is a valid Hissp form.
   >>> assign(
   ...   'SPAM',
   ...   "('eggs')")
   ('.update', ('builtins..globals',), ':', 'SPAM', "('eggs')")

   #> (hissp.compiler..readerless _)      ;Hissp can compile it,
   >>> __import__('hissp.compiler',fromlist='?').readerless(
   ...   _)
   "__import__('builtins').globals().update(\n  SPAM=('eggs'))"

   #> (eval _)                            ; and Python can evaluate that.
   >>> eval(
   ...   _)

   #> SPAM                                ;'eggs'
   >>> SPAM
   'eggs'


   ;;; We can accomplish this more easily with a macro invocation.

   ;;; Unqualified invocations are macro invocations if the identifier is in
   ;;; the current module's _macro_ namespace. The REPL includes one, but
   ;;; .lissp files don't have one until you create it.

   (dir)
   (dir _macro_)

   ;;; Macros run at compile time, so they get all of their arguments
   ;;; unevaluated. The compiler inserts the resulting Hissp
   ;;; (the expansion) at that point in the program. Like special forms,
   ;;; macro invocations look like ordinary function calls, but aren't.

   #> (setattr _macro_ 'assign assign)    ;We can use our assign function as a macro!
   >>> setattr(
   ...   _macro_,
   ...   'assign',
   ...   assign)


   ;; Macro invocations look like ordinary function calls, but they aren't.
   #> (assign SPAM "ham")                 ;This runs a metaprogram!
   >>> # assign
   ... __import__('builtins').globals().update(
   ...   SPAM=('ham'))

   #> SPAM                                ;'ham'
   >>> SPAM
   'ham'


   ;;; We almost could have accomplished this one with a function, but we'd
   ;;; have to either quote the variable name or use a : to pass it in as a
   ;;; keyword. The macro invocation is a little shorter. Furthermore, the
   ;;; globals function gets the globals dict for the current module. Thus,
   ;;; an assign function would assign globals to the module it is defined
   ;;; in, not the one where it is used! You could get around this by
   ;;; walking up a stack frame with inspect, but that's brittle. The macro
   ;;; version just works because it writes the code in line for you, so
   ;;; the globals call appears in the right module.

   ;;; Macros are a feature of the Hissp compiler. Macroexpansion happens at
   ;;; compile time, after the reader, so macros also work in readerless
   ;;; mode, or with Hissp readers other than Lissp, like Hebigo.

   ;; Hissp already comes with a define macro for global assignment.
   ;; Our assign macro just re-implemented this.
   (help hissp.._macro_.define)

   ;; An invocation fully qualified with _macro_ is a macro invocation.
   #> (hissp.._macro_.define SPAM "eggs") ;Note SPAM is not quoted.
   >>> # hissp.._macro_.define
   ... __import__('builtins').globals().update(
   ...   SPAM=('eggs'))

   #> SPAM                                ;'eggs'
   >>> SPAM
   'eggs'


   ;; See the macro expansion by calling it like a method with all arguments quoted.
   ;; This way, the callable isn't qualified with _macro_, so it's a normal call.
   #> (.define hissp.._macro_ 'SPAM '"eggs") ;Method syntax is never macro invocation.
   >>> __import__('hissp')._macro_.define(
   ...   'SPAM',
   ...   "('eggs')")
   ('.update', ('builtins..globals',), ':', 'SPAM', "('eggs')")

   #> (_macro_.define 'SPAM '"eggs") ;Partial qualification also works, when available.
   >>> _macro_.define(
   ...   'SPAM',
   ...   "('eggs')")
   ('.update', ('builtins..globals',), ':', 'SPAM', "('eggs')")


   ;; The REPL's default _macro_ namespace already has the bundled macros.
   (help _macro_.define)

   ;;;; 12.1 Macro Technique

   ;;; (Examples here use `+` from §7.1.)

   #> (setattr _macro_
   #..         'triple
   #..         (lambda (x)
   #..           `(+ ,x (+ ,x ,x))))      ;Use a template to make Hissp.
   >>> setattr(
   ...   _macro_,
   ...   'triple',
   ...   (lambda x:
   ...       (lambda * _:  _)(
   ...         '__main__..QzMaybe_.QzPLUS_',
   ...         x,
   ...         (lambda * _:  _)(
   ...           '__main__..QzMaybe_.QzPLUS_',
   ...           x,
   ...           x))
   ...   ))

   #> (triple 4)                          ;12
   >>> # triple
   ... __import__('builtins').globals()['QzPLUS_'](
   ...   (4),
   ...   __import__('builtins').globals()['QzPLUS_'](
   ...     (4),
   ...     (4)))
   12


   #> (define loud-number
   #..  (lambda x
   #..    (print x)
   #..    x))
   >>> # define
   ... __import__('builtins').globals().update(
   ...   loudQz_number=(lambda x:
   ...                    (print(
   ...                       x),
   ...                     x)  [-1]
   ...                 ))

   #> (triple (loud-number 14))           ;Triples the *code*, not just the *value*.
   >>> # triple
   ... __import__('builtins').globals()['QzPLUS_'](
   ...   loudQz_number(
   ...     (14)),
   ...   __import__('builtins').globals()['QzPLUS_'](
   ...     loudQz_number(
   ...       (14)),
   ...     loudQz_number(
   ...       (14))))
   14
   14
   14
   42


   ;; But what if we want the expanded code to only run it once?
   ;; We can use a lambda to make a local variable and immediately call it.
   #> ((lambda (x)
   #..   (+ x (+ x x)))
   #.. (loud-number 14))
   >>> (lambda x:
   ...     QzPLUS_(
   ...       x,
   ...       QzPLUS_(
   ...         x,
   ...         x))
   ... )(
   ...   loudQz_number(
   ...     (14)))
   14
   42


   ;; Python also allows us to use a default argument up front.
   #> ((lambda (: x (loud-number 14))
   #..   (+ x (+ x x))))
   >>> (
   ...  lambda x=loudQz_number(
   ...           (14)):
   ...     QzPLUS_(
   ...       x,
   ...       QzPLUS_(
   ...         x,
   ...         x))
   ... )()
   14
   42


   ;; Let's try making a template to produce code like that.
   #> (setattr _macro_
   #..         'oops-triple
   #..         (lambda (expression)
   #..           `((lambda (: x ,expression) ;Expand to lambda call for a local.
   #..               (+ x (+ x x))))))
   >>> setattr(
   ...   _macro_,
   ...   'oopsQz_triple',
   ...   (lambda expression:
   ...       (lambda * _:  _)(
   ...         (lambda * _:  _)(
   ...           'lambda',
   ...           (lambda * _:  _)(
   ...             ':',
   ...             '__main__..x',
   ...             expression),
   ...           (lambda * _:  _)(
   ...             '__main__..QzMaybe_.QzPLUS_',
   ...             '__main__..x',
   ...             (lambda * _:  _)(
   ...               '__main__..QzMaybe_.QzPLUS_',
   ...               '__main__..x',
   ...               '__main__..x'))))
   ...   ))

   #> (oops-triple 14)                    ;Oops. Templates qualify symbols!
   >>> # oopsQz_triple
   ... (lambda __main__..x=(14):
   ...     __import__('builtins').globals()['QzPLUS_'](
   ...       __import__('builtins').globals()['x'],
   ...       __import__('builtins').globals()['QzPLUS_'](
   ...         __import__('builtins').globals()['x'],
   ...         __import__('builtins').globals()['x']))
   ... )()
   Traceback (most recent call last):
     ...
       (lambda __main__..x=(14):
                       ^
   SyntaxError: invalid syntax


   ;; Remember, a gensym hash prefix is an alternative to qualification
   ;; for locals. (Thus, templates don't qualify them.)
   #> (setattr _macro_
   #..         'once-triple
   #..         (lambda x
   #..           `((lambda (: $#x ,x)
   #..               (+ $#x (+ $#x $#x))))))
   >>> setattr(
   ...   _macro_,
   ...   'onceQz_triple',
   ...   (lambda x:
   ...       (lambda * _:  _)(
   ...         (lambda * _:  _)(
   ...           'lambda',
   ...           (lambda * _:  _)(
   ...             ':',
   ...             '_QzIF7WPGTUz___x',
   ...             x),
   ...           (lambda * _:  _)(
   ...             '__main__..QzMaybe_.QzPLUS_',
   ...             '_QzIF7WPGTUz___x',
   ...             (lambda * _:  _)(
   ...               '__main__..QzMaybe_.QzPLUS_',
   ...               '_QzIF7WPGTUz___x',
   ...               '_QzIF7WPGTUz___x'))))
   ...   ))

   #> (once-triple (loud-number 14))
   >>> # onceQz_triple
   ... (
   ...  lambda _QzIF7WPGTUz___x=loudQz_number(
   ...           (14)):
   ...     __import__('builtins').globals()['QzPLUS_'](
   ...       _QzIF7WPGTUz___x,
   ...       __import__('builtins').globals()['QzPLUS_'](
   ...         _QzIF7WPGTUz___x,
   ...         _QzIF7WPGTUz___x))
   ... )()
   14
   42


   ;;; Notice the special QzMaybe_ qualifier generated by this template.
   ;;; Templates create these for symbols in the invocation position when
   ;;; they can't tell if _macro_ would work. The compiler replaces a
   ;;; QzMaybe_ with _macro_ if it can resolve the resulting symbol,
   ;;; and omits it otherwise.

   #> `(+ 1 2 3 4)
   >>> (lambda * _:  _)(
   ...   '__main__..QzMaybe_.QzPLUS_',
   ...   (1),
   ...   (2),
   ...   (3),
   ...   (4))
   ('__main__..QzMaybe_.QzPLUS_', 1, 2, 3, 4)


   ;; Outside-in recursive macro. (A multiary +). Note the QzMaybe_.
   ;; If this had been qualified like a global instead, the recursion
   ;; wouldn't work.
   #> (setattr _macro_
   #..         '+
   #..         (lambda (: first 0  :* args) ; 0 with no args. Try it!
   #..           (.__getitem__ ; Tuple method. Templates produce tuples.
   #..             `(,first ; Result when no args left.
   #..               (operator..add ,first (+ ,@args))) ; Otherwise recur.
   #..             (bool args))))        ;Bools are ints, remember?
   >>> setattr(
   ...   _macro_,
   ...   'QzPLUS_',
   ...   (
   ...    lambda first=(0),
   ...           *args:
   ...       (lambda * _:  _)(
   ...         first,
   ...         (lambda * _:  _)(
   ...           'operator..add',
   ...           first,
   ...           (lambda * _:  _)(
   ...             '__main__..QzMaybe_.QzPLUS_',
   ...             *args))).__getitem__(
   ...         bool(
   ...           args))
   ...   ))

   #> (+ 1 2 3 4)
   >>> # QzPLUS_
   ... __import__('operator').add(
   ...   (1),
   ...   # __main__..QzMaybe_.QzPLUS_
   ...   __import__('operator').add(
   ...     (2),
   ...     # __main__..QzMaybe_.QzPLUS_
   ...     __import__('operator').add(
   ...       (3),
   ...       # __main__..QzMaybe_.QzPLUS_
   ...       (4))))
   10


   ;; Notice that a new template doesn't qualify + with QzMaybe_ now that
   ;; it detects a macro with that name.
   #> `(+ 1 2 3 4)
   >>> (lambda * _:  _)(
   ...   '__main__.._macro_.QzPLUS_',
   ...   (1),
   ...   (2),
   ...   (3),
   ...   (4))
   ('__main__.._macro_.QzPLUS_', 1, 2, 3, 4)


   ;; Recursive macros can also expand from the inside outwards, although
   ;; it's less natural in this case.
   #> (setattr _macro_
   #..         '*
   #..         (lambda (: first 1  second 1  :* args)
   #..           (.__getitem__
   #..             `((operator..mul ,first ,second)
   #..               (* (operator..mul ,first ,second) ,@args))
   #..             (bool args))))
   >>> setattr(
   ...   _macro_,
   ...   'QzSTAR_',
   ...   (
   ...    lambda first=(1),
   ...           second=(1),
   ...           *args:
   ...       (lambda * _:  _)(
   ...         (lambda * _:  _)(
   ...           'operator..mul',
   ...           first,
   ...           second),
   ...         (lambda * _:  _)(
   ...           '__main__..QzMaybe_.QzSTAR_',
   ...           (lambda * _:  _)(
   ...             'operator..mul',
   ...             first,
   ...             second),
   ...           *args)).__getitem__(
   ...         bool(
   ...           args))
   ...   ))


   ;; Notice that the stacked expansion comments left by the compiler
   ;; have been squashed together. You can count the #s to see how many.
   ;; 4 of them were recursive invocations and had to use the QzMaybe.
   ;; The 5th didn't, and that accounts for all 5 calls in the expansion.
   #> (* 1 2 3 4 5 6)
   >>> # QzSTAR_
   ... #### __main__..QzMaybe_.QzSTAR_
   ... __import__('operator').mul(
   ...   __import__('operator').mul(
   ...     __import__('operator').mul(
   ...       __import__('operator').mul(
   ...         __import__('operator').mul(
   ...           (1),
   ...           (2)),
   ...         (3)),
   ...       (4)),
   ...     (5)),
   ...   (6))
   720


   ;; Macros only work as invocations, not arguments!
   #> (functools..reduce * '(1 2 3 4))    ;Oops.
   >>> __import__('functools').reduce(
   ...   QzSTAR_,
   ...   ((1),
   ...    (2),
   ...    (3),
   ...    (4),))
   Traceback (most recent call last):
     ...
   NameError: name 'QzSTAR_' is not defined

   #> (functools..reduce (lambda xy (* x y)) ;Invocation, not argument.
   #..                   '(1 2 3 4))
   >>> __import__('functools').reduce(
   ...   (lambda x, y:
   ...       # QzSTAR_
   ...       __import__('operator').mul(
   ...         x,
   ...         y)
   ...   ),
   ...   ((1),
   ...    (2),
   ...    (3),
   ...    (4),))
   24


   ;;; Sometimes you actually do want a name collision (or "capture"),
   ;;; when the macro user should expect an implicit new local binding
   ;;; (an "anaphor"). Don't qualify and don't gensym in that case.
   ;;; Unquoting suppresses the recursive template quoting of tuples,
   ;;; while the normal quote doesn't qualify symbols, so this combination
   ;;; suppresses auto-qualification.

   #> (setattr _macro_
   #..         'XY
   #..         (lambda (: :* body)
   #..           `(lambda (,'X ,'Y)       ;,'X instead of $#X
   #..              ,body)))
   >>> setattr(
   ...   _macro_,
   ...   'XY',
   ...   (lambda *body:
   ...       (lambda * _:  _)(
   ...         'lambda',
   ...         (lambda * _:  _)(
   ...           'X',
   ...           'Y'),
   ...         body)
   ...   ))


   #> (functools..reduce (XY * X Y)       ;Invocation, not argument!
   #..                   '(1 2 3 4))
   >>> __import__('functools').reduce(
   ...   # XY
   ...   (lambda X, Y:
   ...       # QzSTAR_
   ...       __import__('operator').mul(
   ...         X,
   ...         Y)
   ...   ),
   ...   ((1),
   ...    (2),
   ...    (3),
   ...    (4),))
   24

   #> ((XY + Y X) "Eggs" "Spam")
   >>> # XY
   ... (lambda X, Y:
   ...     # QzPLUS_
   ...     __import__('operator').add(
   ...       Y,
   ...       # __main__..QzMaybe_.QzPLUS_
   ...       X)
   ... )(
   ...   ('Eggs'),
   ...   ('Spam'))
   'SpamEggs'


   ;; It's possible for a macro to shadow a global. They live in different namespaces.
   #> (+ 1 2 3 4)                         ;_macro_.+, not the global.
   >>> # QzPLUS_
   ... __import__('operator').add(
   ...   (1),
   ...   # __main__..QzMaybe_.QzPLUS_
   ...   __import__('operator').add(
   ...     (2),
   ...     # __main__..QzMaybe_.QzPLUS_
   ...     __import__('operator').add(
   ...       (3),
   ...       # __main__..QzMaybe_.QzPLUS_
   ...       (4))))
   10

   #> (functools..reduce + '(1 2 3 4))    ;Global function, not the macro!
   >>> __import__('functools').reduce(
   ...   QzPLUS_,
   ...   ((1),
   ...    (2),
   ...    (3),
   ...    (4),))
   10


   (dir)                               ;Has QzPLUS_, but not QzSTAR_.
   (dir _macro_)                       ;Has both.

   ;; Notice the qualifier on sep. Qualifying a keyword doesn't make sense.
   #> (setattr _macro_
   #..         'p123
   #..         (lambda (sep)
   #..           `(print 1 2 3 : sep ,sep)))
   >>> setattr(
   ...   _macro_,
   ...   'p123',
   ...   (lambda sep:
   ...       (lambda * _:  _)(
   ...         'builtins..print',
   ...         (1),
   ...         (2),
   ...         (3),
   ...         ':',
   ...         '__main__..sep',
   ...         sep)
   ...   ))


   ;; Note the : didn't have to be quoted here, because it's in a macro
   ;; invocation, not a call. The compiler also ignored the qualifier
   ;; on sep, because it's a kwarg.
   #> (p123 :)
   >>> # p123
   ... __import__('builtins').print(
   ...   (1),
   ...   (2),
   ...   (3),
   ...   sep=':')
   1:2:3


   ;;;; 13 Compiling and Running Files

   ;;; The ``lissp`` shell command can run a .lissp file as __main__.
   ;;; You cannot import .lissp directly. Compile it to .py first.

   ;; Finds spam.lissp & eggs.lissp in the current package & compile to spam.py & eggs.py
   #> (.write_text (pathlib..Path "eggs.lissp")
   #..             "(print \"Hello World!\")")
   >>> __import__('pathlib').Path(
   ...   ('eggs.lissp')).write_text(
   ...   ('(print "Hello World!")'))
   22

   #> (.write_text (pathlib..Path "spam.lissp")
   #..             "(print \"Hello from spam!\")
   #..(.update (globals) : x 42)")
   >>> __import__('pathlib').Path(
   ...   ('spam.lissp')).write_text(
   ...   ('(print "Hello from spam!")\n(.update (globals) : x 42)'))
   53

   #> (hissp.reader..transpile __package__ 'spam 'eggs) ;Side effects on compilation.
   >>> __import__('hissp.reader',fromlist='?').transpile(
   ...   __package__,
   ...   'spam',
   ...   'eggs')
   Hello from spam!
   Hello World!


   #> spam..x                             ;Compiled modules are cached.
   >>> __import__('spam').x
   42

   #> eggs.
   >>> __import__('eggs')
   <module 'eggs' from ...>

   #> (importlib..reload spam.)           ;Side effects again on .py reload.
   >>> __import__('importlib').reload(
   ...   __import__('spam'))
   Hello from spam!
   <module 'spam' from ...>


   #> (any (map (lambda f (os..remove f)) ;Cleanup.
   #..     '(eggs.lissp spam.lissp spam.py eggs.py)))
   >>> any(
   ...   map(
   ...     (lambda f:
   ...         __import__('os').remove(
   ...           f)
   ...     ),
   ...     ('eggs.lissp',
   ...      'spam.lissp',
   ...      'spam.py',
   ...      'eggs.py',)))
   False


   ;;;; 14 The Bundled Macros

   ;;; As a convenience, the REPL comes with the bundled macros
   ;;; already defined at start up. They're in the _macro_ namespace.

   (dir _macro_)

   ;;; This is a copy of of the following namespace.

   hissp.macros.._macro_

   (dir hissp.macros.._macro_)

   ;;; Notice its containing module. Take a minute to read its docstring.

   (help hissp.macros.)

   ;;; As a convenience, hissp.__init__ imports it as well:

   hissp.._macro_

   ;;; The macros will still be available from there even if you clobber
   ;;; your _macro_ copy. Recall that you can invoke macros using their
   ;;; fully-qualified names.

   ;;; The bundled macros have individual docstrings with usage examples.
   ;;; At this point in the tour, you should be able to understand them.

   (help _macro_.define)

   ;;; Two particularly important ones to know are alias and the prelude.
   ;;; Unlike the REPL, Lissp modules do not have a _macro_ namespace by
   ;;; default. A typical Lissp module will start with a fully-qualified
   ;;; invocation of something like one of these to create the _macro_
   ;;; namespace for the module.

   ;;; Aliases can give you access to macros defined elsewhere using
   ;;; abbreviated qualifiers, as well as attributes of ordinary modules.

   (help _macro_.alias)

   ;;; The prelude copies _macro_ from hissp._macro_ like the REPL, defines
   ;;; some Python interop helper functions, and imports Python's standard-library
   ;;; functional utilities.

   (help _macro_.prelude)

   ;;; The docstrings use reStructuredText markup. While readable as plain
   ;;; text in the help console, they're also rendered as HTML using Sphinx
   ;;; in Hissp's online API docs. Find them at https://hissp.rtfd.io

   ;;; Familiarize yourself with a macro suite, such as the bundled macros.
   ;;; It makes Hissp that much more usable.

   ;;;; 15 Advanced Reader Tags

   ;;;; 15.1 The Discard Macro

   #> _#"The discard reader macro _# omits the next form.
   #..It's a way to comment out code structurally.
   #..It can also make block comments like this one.
   #..(But the need to escape double quotes might make ;; comments easier.)
   #..This would show up when compiled if not for _#.
   #..Of course, a string expression like this one wouldn't do anything
   #..in Python, even if it were compiled in.
   #.."
   >>>

   #> (print 1 _#(I'm not here!) 2 3)
   >>> print(
   ...   (1),
   ...   (2),
   ...   (3))
   1 2 3


   ;;;; 15.2 Fully-Qualified Reader Macros

   ;; Invoke any fully-qualified callable on the next parsed object at read time.
   #> builtins..hex#3840                  ;Fully-Qualified name ending in # is a reader macro.
   >>> 0xf00
   3840

   #> builtins..ord#Q                     ;Reader macros make literal notation extensible.
   >>> (81)
   81

   #> math..exp#1                         ;e^1. Or to whatever number. At read time.
   >>> (2.718281828459045)
   2.718281828459045


   #> builtins..bytes##bytes ascii        ;Add more #s for more arguments.
   >>> b'bytes'
   b'bytes'

   #> builtins..bytes##encoding=ascii|moar bytes| ;Convert to a Kwarg via foo=.
   >>> b'moar bytes'
   b'moar bytes'


   ;; Yes, these are a type of object special-cased in the reader. They're
   ;; only meant for use at read time, but they're allowed to survive to
   ;; run time for debugging purposes.
   #> spam=eggs
   >>> __import__('pickle').loads(  # Kwarg('spam', 'eggs')
   ...     b'ccopyreg\n'
   ...     b'_reconstructor\n'
   ...     b'(chissp.reader\n'
   ...     b'Kwarg\n'
   ...     b'cbuiltins\n'
   ...     b'object\n'
   ...     b'NtR(dVk\n'
   ...     b'Vspam\n'
   ...     b'sVv\n'
   ...     b'Veggs\n'
   ...     b'sb.'
   ... )
   Kwarg('spam', 'eggs')


   ;; Reader macros compose like functions.
   #> 'hissp.munger..demunge#Qz_QzLT_QzGT_QzGT_   ;Note the starting '.
   >>> '-<>>'
   '-<>>'

   #> ''x
   >>> ('quote',
   ...  'x',)
   ('quote', 'x')

   #> '\'x
   >>> 'QzAPOS_x'
   'QzAPOS_x'


   ;; The reader normally discards them, but
   #> 'builtins..repr#;comments are parsed objects too!
   >>> "Comment(';comments are parsed objects too!\\n')"
   "Comment(';comments are parsed objects too!\\n')"


   ;;; Except for str atoms and tuples, objects in Hissp should evaluate
   ;;; to themselves. But when the object lacks a Python literal notation,
   ;;; the compiler is in a pickle!

   #> builtins..float#inf
   >>> __import__('pickle').loads(  # inf
   ...     b'Finf\n'
   ...     b'.'
   ... )
   inf


   ;;;; 15.3 Inject

   ;;; The 'inject' reader macro compiles and evaluates the next form at
   ;;; read time and injects the resulting object directly into the Hissp
   ;;; tree, like a fully-qualified reader macro does.

   #> '(1 2 (operator..add 1 2))          ;Quoting happens at compile time.
   >>> ((1),
   ...  (2),
   ...  ('operator..add',
   ...   (1),
   ...   (2),),)
   (1, 2, ('operator..add', 1, 2))

   #> '(1 2 .#(operator..add 1 2))        ;Inject happens at read time.
   >>> ((1),
   ...  (2),
   ...  (3),)
   (1, 2, 3)


   #> (fractions..Fraction 1 2)           ;Run time eval. Compiles to equivalent code.
   >>> __import__('fractions').Fraction(
   ...   (1),
   ...   (2))
   Fraction(1, 2)

   #> .#(fractions..Fraction 1 2)         ;Read time eval. Compiles to equivalent object.
   >>> __import__('pickle').loads(  # Fraction(1, 2)
   ...     b'cfractions\n'
   ...     b'Fraction\n'
   ...     b'(V1/2\n'
   ...     b'tR.'
   ... )
   Fraction(1, 2)


   ;;; Recall that Hissp-level str atoms can represent arbitrary Python
   ;;; code. It's usually used for identifiers, but can be anything, even
   ;;; complex formulas.

   ;; Hissp may not have operators, but Python does.
   #> (lambda abc |(-b + (b**2 - 4*a*c)**0.5)/(2*a)|)
   >>> (lambda a, b, c: (-b + (b**2 - 4*a*c)**0.5)/(2*a))
   <function <lambda> at 0x...>


   ;; An injected "" token acts like a || fragment, but can have things
   ;; like newlines and string escape codes.
   #> (lambda abc
   #..  .#"(-b + (b**2 - 4*a*c)**0.5)
   #..    /(2*a)")
   >>> (lambda a, b, c:
   ...     (-b + (b**2 - 4*a*c)**0.5)
   ...         /(2*a)
   ... )
   <function <lambda> at 0x...>


   ;;; Remember, the Lissp-level "" tokens compile down to Python-level
   ;;; string literals via a Hissp-level fragment (i.e., a Hissp atom of
   ;;; the str type) whose text contains the Python string literal. A Lissp
   ;;; "" token does NOT read as a general-purpose Hissp fragment, even
   ;;; though fragments usually look similar in readerless mode (i.e., the
   ;;; text making up any Lissp "" token without a newline would also be a
   ;;; valid spelling of a Python string literal, even though these are
   ;;; different languages, and fragments at the Hissp level are str
   ;;; objects). Remember, Hissp is made of data, rather than text, unlike
   ;;; Lissp, which is a text representation of it. Data can be represented
   ;;; in different ways. If you need a fragment in Lissp, you can use the
   ;;; raw || tokens, or use .# (i.e., an injection to the Hissp level) on
   ;;; any Lissp expression that evaluates to an instance of str like Hissp
   ;;; expects for fragments (and yes, that includes the "" tokens, among
   ;;; other expressions).

   ;; Objects without literals don't pickle until the compiler has to emit
   ;; them as Python code. That may never happen if another macro gets it.
   #> 'builtins..repr#(re..compile#.#"[1-9][0-9]*" builtins..float#inf)
   >>> "(re.compile('[1-9][0-9]*'), inf)"
   "(re.compile('[1-9][0-9]*'), inf)"

   #> re..compile#.#"[1-9][0-9]*"
   >>> __import__('pickle').loads(  # re.compile('[1-9][0-9]*')
   ...     b'cre\n'
   ...     b'_compile\n'
   ...     b'(V[1-9][0-9]*\n'
   ...     b'I32\n'
   ...     b'tR.'
   ... )
   re.compile('[1-9][0-9]*')
