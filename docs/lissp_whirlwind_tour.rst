.. Copyright 2020, 2021, 2022, 2023 Matthew Egan Odendahl
   SPDX-License-Identifier: Apache-2.0

.. This hidden doctest adds bundled macros for REPL-consistent behavior.
   #> (operator..setitem (globals) '_macro_ (types..SimpleNamespace : :** (vars hissp.._macro_)))
   >>> __import__('operator').setitem(
   ...   globals(),
   ...   '_macro_',
   ...   __import__('types').SimpleNamespace(
   ...     **vars(
   ...         __import__('hissp')._macro_)))

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
   Hissp Primer.
   "

   ;;;; 1 Installation

   ;;; These docs are for the latest development version of Hissp.
   ;;; Install the latest Hissp version with
   ;;; $ pip install git+https://github.com/gilch/hissp
   ;;; Start the REPL with
   ;;; $ lissp
   ;;; You can quit with EOF or (exit).

   ;;; Most examples are tested automatically, but details may be dated.
   ;;; Report issues or try the current release version instead.

   ;;;; 2 Simple Atoms

   ;;; To a first approximation, the Hissp intermediate language is made
   ;;; of Python tuples representing syntax trees. The nodes are tuples
   ;;; and the leaves are called "atoms". Simple atoms in Lissp are
   ;;; written the same way as Python.

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

   ;; Tuples group any atoms with (). Data tuples start with '.
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

   #> (dict '((1 2) (3 4)))               ;Uses nested tuples.
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


   ;;;; 6 String Atoms

   #> :control-word                       ;Colon prefix. Similar to Lisp ":keywords".
   >>> ':control-word'
   ':control-word'

   #> 'symbol                             ;Apostrophe prefix. Represents identifier.
   >>> 'symbol'
   'symbol'


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

   #> :-<>>                                ;Don't represent identifiers, don't munge.
   >>> ':-<>>'
   ':-<>>'

   #> :                                   ;Still a control word.
   >>> ':'
   ':'


   ;;;; 6.2 Escaping

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


   ;;;; 6.3 String Literals

   #> "raw string"
   >>> ('raw string')
   'raw string'

   #> 'not-string'                        ;symbol
   >>> 'notQz_stringQzAPOS_'
   'notQz_stringQzAPOS_'

   #> #"Say \"Cheese!\" \u263a"           ;Hash strings process Python escapes.
   >>> ('Say "Cheese!" ☺')
   'Say "Cheese!" ☺'

   #> "Say \"Cheese!\" \u263a"            ;Raw strings don't.
   >>> ('Say \\"Cheese!\\" \\u263a')
   'Say \\"Cheese!\\" \\u263a'


   #> "string
   #..with
   #..newlines
   #.."                                   ;Same as #"string\nwith\nnewlines\n".
   >>> ('string\nwith\nnewlines\n')
   'string\nwith\nnewlines\n'


   #> "one\"
   #..string\\"                           ;Tokenizer expects paired \'s, even raw.
   >>> ('one\\"\nstring\\\\')
   'one\\"\nstring\\\\'


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
   #..       :** (dict : end #"!?\n"))    ;Multiple :** allowed too.
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
   ...   greet=(lambda salutation,name:
   ...           print(
   ...             ('{}, {}!').format(
   ...               salutation.title(),
   ...               name))))

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
   ...                 __import__('functools').reduce(
   ...                   __import__('operator').mul,
   ...                   range(
   ...                     i,
   ...                     (0),
   ...                     (-1)),
   ...                   (1))))

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

   #> (any (map (lambda (c) (print c))      ;Loops!
   #..          "abc"))
   >>> any(
   ...   map(
   ...     (lambda c:
   ...       print(
   ...         c)),
   ...     ('abc')))
   a
   b
   c
   False


   ((.get (dict : y (lambda () (print "Yes!")) ;Branches!
                n (lambda () (print "Canceled.")))
          (input "enter y/n> ")
          (lambda () (print "Unrecognized input."))))

   ;;; Don't worry, Hissp metaprogramming will make this much easier,
   ;;; but our limited tools so far are enough for a ternary operator.

   #> (.update (globals) : bool->caller (dict))
   >>> globals().update(
   ...   boolQz_QzGT_caller=dict())


   ;; True calls left.
   #> (operator..setitem bool->caller True (lambda (L R) (L)))
   >>> __import__('operator').setitem(
   ...   boolQz_QzGT_caller,
   ...   True,
   ...   (lambda L,R:L()))


   ;; False calls right.
   #> (operator..setitem bool->caller False (lambda (L R) (R)))
   >>> __import__('operator').setitem(
   ...   boolQz_QzGT_caller,
   ...   False,
   ...   (lambda L,R:R()))


   #> (.update (globals)
   #..         : ternary
   #..         (lambda (condition then_thunk else_thunk)
   #..           ((operator..getitem bool->caller (bool condition))
   #..            then_thunk else_thunk)))
   >>> globals().update(
   ...   ternary=(lambda condition,then_thunk,else_thunk:
   ...             __import__('operator').getitem(
   ...               boolQz_QzGT_caller,
   ...               bool(
   ...                 condition))(
   ...               then_thunk,
   ...               else_thunk)))


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
   ...                  ternary(
   ...                    __import__('operator').le(
   ...                      i,
   ...                      (1)),
   ...                    (lambda :(1)),
   ...                    (lambda :
   ...                      __import__('operator').mul(
   ...                        i,
   ...                        factorial_II(
   ...                          __import__('operator').sub(
   ...                            i,
   ...                            (1))))))))

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
   >>> (lambda a,b,/,c,d,e=(1),f=(2),*args,h=(4),i,j=(1),**kwargs:(
   ...   print(
   ...     globals()),
   ...   print(
   ...     locals()),
   ...   b)[-1])
   <function <lambda> at 0x...>


   #> (lambda (: a :?  b :?  c 1))        ;Note the : separator like calls.
   >>> (lambda a,b,c=(1):())
   <function <lambda> at 0x...>

   #> (lambda (a : b :?  c 1))            ;`a` now implicitly paired with :?.
   >>> (lambda a,b,c=(1):())
   <function <lambda> at 0x...>

   #> (lambda (a b : c 1))                ;Next isn't paired with :?. The : stops here.
   >>> (lambda a,b,c=(1):())
   <function <lambda> at 0x...>


   #> (lambda (: :* a))                   ;Star arg must pair with star, as Python.
   >>> (lambda *a:())
   <function <lambda> at 0x...>

   #> (lambda (: :* :?  x :?))            ;Empty star arg, so x is keyword only.
   >>> (lambda *,x:())
   <function <lambda> at 0x...>

   #> (lambda (:* : x :?))                ;Slid : over one. Still a kwonly.
   >>> (lambda *,x:())
   <function <lambda> at 0x...>

   #> (lambda (:* x :))                   ;Implicit :? is the same. Compare.
   >>> (lambda *,x:())
   <function <lambda> at 0x...>

   #> (lambda (:* a))                     ;Kwonly! Not star arg! Final : implied.
   >>> (lambda *,a:())
   <function <lambda> at 0x...>


   #> (lambda (a b : x None  y None))     ;Normal, then positional defaults.
   >>> (lambda a,b,x=None,y=None:())
   <function <lambda> at 0x...>

   #> (lambda (:* a b : x None  y None))  ;Keyword only, then keyword defaults.
   >>> (lambda *,a,b,x=None,y=None:())
   <function <lambda> at 0x...>


   #> (lambda (spam eggs) eggs)           ;Simple cases look like other Lisps, but
   >>> (lambda spam,eggs:eggs)
   <function <lambda> at 0x...>

   #> ((lambda abc                        ; params not strictly required to be a tuple.
   #..   (print c b a))                   ;There are three parameters.
   #.. 3 2 1)
   >>> (lambda a,b,c:
   ...   print(
   ...     c,
   ...     b,
   ...     a))(
   ...   (3),
   ...   (2),
   ...   (1))
   1 2 3


   #> (lambda (:))                        ;Explicit : still allowed with no params.
   >>> (lambda :())
   <function <lambda> at 0x...>

   #> (lambda : (print "oops"))           ;Thunk resembles Python.
   >>> (lambda :
   ...   print(
   ...     ('oops')))
   <function <lambda> at 0x...>

   #> ((lambda :x1 x))                    ;Control words are strings are iterable.
   >>> (lambda x=1:x)()
   1


   ;;;; 10 Quote

   ;;; Quote is the only other special form. Looks like a call, but isn't.

   ;;; A "form" is any Hissp data that can be evaluated.
   ;;; Not all data is a valid program in Hissp. E.g. ``(7 42)`` is a
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


   ;;; Other objects evaluate to themselves, but strings and tuples have
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


   ;;; Notice how the string gets an extra layer of quotes vs identifiers.
   ;;; This particular tuple happens to be a valid form.

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

   ;;; Hissp-level strings contain Python code to include in the compiled
   ;;; output. These usually contain identifiers, but can be anything.
   ;;; Thus, Lissp identifiers read as strings at the Hissp level.

   #> (quote identifier)                  ;Just a string.
   >>> 'identifier'
   'identifier'


   ;;; The raw strings and hash strings in Lissp ("..."/#"..." syntax)
   ;;; also read as strings at the Hissp level, but they contain a Python
   ;;; string literal instead of a Python identifier.

   #> (quote "a string")                  ;"..."/#"..." is reader syntax!
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
   >>> (lambda a:a)()
   Traceback (most recent call last):
     ...
   TypeError: <lambda>() missing 1 required positional argument: 'a'

   #> ((lambda (: a (quote :?)) a))       ;Just a string. Even in context.
   >>> (lambda a=':?':a)()
   ':?'


   ;;;; 11 Simple Reader Macros

   ;;; Reader macros are metaprograms to abbreviate Hissp and don't
   ;;; represent it directly. They apply to the next parsed Hissp object
   ;;; at read time, before the Hissp compiler sees it, and thus before
   ;;; they are compiled and evaluated. They end in # except for a few
   ;;; builtins-- ' ! ` , ,@

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
   >>> (lambda * _: _)(
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
   >>> (lambda * _: _)(
   ...   'builtins..print',
   ...   ('Hi').upper())
   ('builtins..print', 'HI')


   #> `(,'foo+2 foo+2)                    ;Interpolations not auto-qualified!
   >>> (lambda * _: _)(
   ...   'fooQzPLUS_2',
   ...   '__main__..fooQzPLUS_2')
   ('fooQzPLUS_2', '__main__..fooQzPLUS_2')

   #> `(print ,@"abc")                    ;Splice unquote (,@) interpolates and unpacks.
   >>> (lambda * _: _)(
   ...   'builtins..print',
   ...   *('abc'))
   ('builtins..print', 'a', 'b', 'c')

   #> `(print (.upper "abc"))             ;Template quoting is recursive
   >>> (lambda * _: _)(
   ...   'builtins..print',
   ...   (lambda * _: _)(
   ...     '.upper',
   ...     "('abc')"))
   ('builtins..print', ('.upper', "('abc')"))

   #> `(print ,@(.upper "abc"))           ; unless suppressed by an unquote.
   >>> (lambda * _: _)(
   ...   'builtins..print',
   ...   *('abc').upper())
   ('builtins..print', 'A', 'B', 'C')


   ;;; Full qualification prevents accidental name collisions in
   ;;; programmatically generated code. But full qualification doesn't work on
   ;;; local variables, which can't be imported. For these, we use a template
   ;;; count prefix instead of a qualifier to ensure a variable can only
   ;;; be used in the same template it was defined in. The gensym reader
   ;;; macro ($#) generates a symbol with the current template's number.

   #> `($#eggs $#spam $#bacon $#spam)     ;Generated symbols for macro hygiene.
   >>> (lambda * _: _)(
   ...   '_QzNo9_eggs',
   ...   '_QzNo9_spam',
   ...   '_QzNo9_bacon',
   ...   '_QzNo9_spam')
   ('_QzNo9_eggs', '_QzNo9_spam', '_QzNo9_bacon', '_QzNo9_spam')

   #> `$#spam                             ;Template number in name prevents collisions.
   >>> '_QzNo10_spam'
   '_QzNo10_spam'


   ;; If you don't specify, by default, the template number is a prefix,
   ;; but you can put them anywhere in the symbol; $ marks the positions.
   #> `$#spam$.$eggs$                     ;Lacking a gensym prefix, it gets fully qualified.
   >>> '__main__..spam_QzNo8_._QzNo8_eggs_QzNo8_'
   '__main__..spam_QzNo8_._QzNo8_eggs_QzNo8_'


   ;; This is typically used for partially-qualified variables.
   #> `,'$#self.$foo                      ;Interpolation suppressed auto-qualification.
   >>> 'self._QzNo9_foo'
   'self._QzNo9_foo'


   ;;; You can use templates to make collections with interpolated values.
   ;;; When your intent is to create data rather than code, unquote
   ;;; each element.

   ;; (Uses `+` from §7.1.)
   #> (list `(,@"abc"
   #..        ,1
   #..        ,(+ 1 1)
   #..        ,(+ 1 2)))
   >>> list(
   ...   (lambda * _: _)(
   ...     *('abc'),
   ...     (1),
   ...     QzPLUS_(
   ...       (1),
   ...       (1)),
   ...     QzPLUS_(
   ...       (1),
   ...       (2))))
   ['a', 'b', 'c', 1, 2, 3]


   #> `(0 "a" 'b)                         ;Beware of strings and symbols.
   >>> (lambda * _: _)(
   ...   (0),
   ...   "('a')",
   ...   (lambda * _: _)(
   ...     'quote',
   ...     '__main__..b'))
   (0, "('a')", ('quote', '__main__..b'))

   #> `(,0 ,"a" ,'b)                      ;Just unquote everything in data templates.
   >>> (lambda * _: _)(
   ...   (0),
   ...   ('a'),
   ...   'b')
   (0, 'a', 'b')


   #> (dict `((,0 ,1)
   #..        ,@(.items (dict : spam "eggs"  foo 2)) ;dict unpacking
   #..        (,3 ,4)))
   >>> dict(
   ...   (lambda * _: _)(
   ...     (lambda * _: _)(
   ...       (0),
   ...       (1)),
   ...     *dict(
   ...        spam=('eggs'),
   ...        foo=(2)).items(),
   ...     (lambda * _: _)(
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
   ...   assign=(lambda key,value:
   ...            (lambda * _: _)(
   ...              '.update',
   ...              (lambda * _: _)(
   ...                'builtins..globals'),
   ...              ':',
   ...              key,
   ...              value)))


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
   ;;; unevaluated. The compiler inserts the resulting Hissp at that point
   ;;; in the program. Like special forms, macro invocations look like
   ;;; function calls, but aren't.

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

   ;; An invocation qualified with _macro_ is a macro invocation.
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
   ...     (lambda * _: _)(
   ...       '__main__..QzMaybe_.QzPLUS_',
   ...       x,
   ...       (lambda * _: _)(
   ...         '__main__..QzMaybe_.QzPLUS_',
   ...         x,
   ...         x))))

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
   ...   loudQz_number=(lambda x:(
   ...                   print(
   ...                     x),
   ...                   x)[-1]))

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
   ...   QzPLUS_(
   ...     x,
   ...     QzPLUS_(
   ...       x,
   ...       x)))(
   ...   loudQz_number(
   ...     (14)))
   14
   42


   ;; Python also allows us to use a default argument up front.
   #> ((lambda (: x (loud-number 14))
   #..   (+ x (+ x x))))
   >>> (lambda x=loudQz_number(
   ...   (14)):
   ...   QzPLUS_(
   ...     x,
   ...     QzPLUS_(
   ...       x,
   ...       x)))()
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
   ...     (lambda * _: _)(
   ...       (lambda * _: _)(
   ...         'lambda',
   ...         (lambda * _: _)(
   ...           ':',
   ...           '__main__..x',
   ...           expression),
   ...         (lambda * _: _)(
   ...           '__main__..QzMaybe_.QzPLUS_',
   ...           '__main__..x',
   ...           (lambda * _: _)(
   ...             '__main__..QzMaybe_.QzPLUS_',
   ...             '__main__..x',
   ...             '__main__..x'))))))

   #> (oops-triple 14)                    ;Oops. Templates qualify symbols!
   >>> # oopsQz_triple
   ... (lambda __main__..x=(14):
   ...   __import__('builtins').globals()['QzPLUS_'](
   ...     __import__('builtins').globals()['x'],
   ...     __import__('builtins').globals()['QzPLUS_'](
   ...       __import__('builtins').globals()['x'],
   ...       __import__('builtins').globals()['x'])))()
   Traceback (most recent call last):
     ...
       (lambda __main__..x=(14):
                       ^
   SyntaxError: invalid syntax


   ;; Remember, gensyms are an alternative to qualification for locals.
   ;; (Thus, gensyms are never auto-qualified by templates.)
   #> (setattr _macro_
   #..         'once-triple
   #..         (lambda x
   #..           `((lambda (: $#x ,x)
   #..               (+ $#x (+ $#x $#x))))))
   >>> setattr(
   ...   _macro_,
   ...   'onceQz_triple',
   ...   (lambda x:
   ...     (lambda * _: _)(
   ...       (lambda * _: _)(
   ...         'lambda',
   ...         (lambda * _: _)(
   ...           ':',
   ...           '_QzNo22_x',
   ...           x),
   ...         (lambda * _: _)(
   ...           '__main__..QzMaybe_.QzPLUS_',
   ...           '_QzNo22_x',
   ...           (lambda * _: _)(
   ...             '__main__..QzMaybe_.QzPLUS_',
   ...             '_QzNo22_x',
   ...             '_QzNo22_x'))))))

   #> (once-triple (loud-number 14))
   >>> # onceQz_triple
   ... (lambda _QzNo22_x=loudQz_number(
   ...   (14)):
   ...   __import__('builtins').globals()['QzPLUS_'](
   ...     _QzNo22_x,
   ...     __import__('builtins').globals()['QzPLUS_'](
   ...       _QzNo22_x,
   ...       _QzNo22_x)))()
   14
   42


   ;;; Notice the special QzMaybe_ qualifier generated by this template.
   ;;; Templates create these for symbols in the invocation position when
   ;;; they can't tell if _macro_ would work. The compiler skips QzMaybe_
   ;;; unless it can resolve the symbol with QzMaybe_ as _macro_.

   #> `(+ 1 2 3 4)
   >>> (lambda * _: _)(
   ...   '__main__..QzMaybe_.QzPLUS_',
   ...   (1),
   ...   (2),
   ...   (3),
   ...   (4))
   ('__main__..QzMaybe_.QzPLUS_', 1, 2, 3, 4)


   ;; Recursive macro. (A multiary +). Note the QzMaybe_. If this had
   ;; been qualified like a global instead, the recursion wouldn't work.
   #> (setattr _macro_
   #..         '+
   #..         (lambda (first : :* args)
   #..           (.__getitem__ ; Tuple method. Templates produce tuples.
   #..             `(,first ; Result when no args left.
   #..               (operator..add ,first (+ ,@args))) ; Otherwise recur.
   #..             (bool args))))        ;Bools are ints, remember?
   >>> setattr(
   ...   _macro_,
   ...   'QzPLUS_',
   ...   (lambda first,*args:
   ...     (lambda * _: _)(
   ...       first,
   ...       (lambda * _: _)(
   ...         'operator..add',
   ...         first,
   ...         (lambda * _: _)(
   ...           '__main__..QzMaybe_.QzPLUS_',
   ...           *args))).__getitem__(
   ...       bool(
   ...         args))))

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
   >>> (lambda * _: _)(
   ...   '__main__.._macro_.QzPLUS_',
   ...   (1),
   ...   (2),
   ...   (3),
   ...   (4))
   ('__main__.._macro_.QzPLUS_', 1, 2, 3, 4)


   #> (setattr _macro_
   #..         '*
   #..         (lambda (first : :* args)
   #..           (.__getitem__
   #..             `(,first
   #..               (operator..mul ,first (* ,@args)))
   #..             (bool args))))
   >>> setattr(
   ...   _macro_,
   ...   'QzSTAR_',
   ...   (lambda first,*args:
   ...     (lambda * _: _)(
   ...       first,
   ...       (lambda * _: _)(
   ...         'operator..mul',
   ...         first,
   ...         (lambda * _: _)(
   ...           '__main__..QzMaybe_.QzSTAR_',
   ...           *args))).__getitem__(
   ...       bool(
   ...         args))))

   #> (* 1 2 3 4)
   >>> # QzSTAR_
   ... __import__('operator').mul(
   ...   (1),
   ...   # __main__..QzMaybe_.QzSTAR_
   ...   __import__('operator').mul(
   ...     (2),
   ...     # __main__..QzMaybe_.QzSTAR_
   ...     __import__('operator').mul(
   ...       (3),
   ...       # __main__..QzMaybe_.QzSTAR_
   ...       (4))))
   24


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
   ...   (lambda x,y:
   ...     # QzSTAR_
   ...     __import__('operator').mul(
   ...       x,
   ...       # __main__..QzMaybe_.QzSTAR_
   ...       y)),
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
   ...     (lambda * _: _)(
   ...       'lambda',
   ...       (lambda * _: _)(
   ...         'X',
   ...         'Y'),
   ...       body)))


   #> (functools..reduce (XY * X Y)       ;Invocation, not argument!
   #..                   '(1 2 3 4))
   >>> __import__('functools').reduce(
   ...   # XY
   ...   (lambda X,Y:
   ...     # QzSTAR_
   ...     __import__('operator').mul(
   ...       X,
   ...       # __main__..QzMaybe_.QzSTAR_
   ...       Y)),
   ...   ((1),
   ...    (2),
   ...    (3),
   ...    (4),))
   24

   #> ((XY + Y X) "Eggs" "Spam")
   >>> # XY
   ... (lambda X,Y:
   ...   # QzPLUS_
   ...   __import__('operator').add(
   ...     Y,
   ...     # __main__..QzMaybe_.QzPLUS_
   ...     X))(
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
   ...     (lambda * _: _)(
   ...       'builtins..print',
   ...       (1),
   ...       (2),
   ...       (3),
   ...       ':',
   ...       '__main__..sep',
   ...       sep)))


   ;; Note the : didn't have to be quoted here, because it's in a macro
   ;; invocation, not a call. The compiler also discarded the qualifier
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

   ;;; ``$ lissp`` can run a .lissp file as __main__.
   ;;; You cannot import .lissp directly. Compile it to .py first.

   ;; Finds spam.lissp & eggs.lissp in the current package & compile to spam.py & eggs.py
   #> (.write_text (pathlib..Path "eggs.lissp")
   #..             #"(print \"Hello World!\")")
   >>> __import__('pathlib').Path(
   ...   ('eggs.lissp')).write_text(
   ...   ('(print "Hello World!")'))
   22

   #> (.write_text (pathlib..Path "spam.lissp")
   #..             #"(print \"Hello from spam!\")
   #..(.update (globals) : x 42)")
   >>> __import__('pathlib').Path(
   ...   ('spam.lissp')).write_text(
   ...   ('(print "Hello from spam!")\n(.update (globals) : x 42)'))
   53

   #> (hissp.reader..transpile __package__ 'spam 'eggs) ; Side effects on compilation
   >>> __import__('hissp.reader',fromlist='?').transpile(
   ...   __package__,
   ...   'spam',
   ...   'eggs')
   Hello from spam!
   Hello World!


   #> spam..x                             ; and import!
   >>> __import__('spam').x
   Hello from spam!
   42

   #> spam..x                             ;Python caches imports.
   >>> __import__('spam').x
   42

   #> eggs.
   >>> __import__('eggs')
   Hello World!
   <module 'eggs' from ...>


   #> (any (map (lambda f (os..remove f)) ;Cleanup.
   #..     '(eggs.lissp spam.lissp spam.py eggs.py)))
   >>> any(
   ...   map(
   ...     (lambda f:
   ...       __import__('os').remove(
   ...         f)),
   ...     ('eggs.lissp',
   ...      'spam.lissp',
   ...      'spam.py',
   ...      'eggs.py',)))
   False


   ;;;; 14 The Bundled Macros

   ;;; To make it more usable, the REPL comes with the bundled macros
   ;;; already defined at start up. They're in the _macro_ namespace.

   (dir _macro_)

   ;;; This is a copy of of the following module.

   #> hissp.._macro_
   >>> __import__('hissp')._macro_
   <module 'hissp.macros._macro_'>

   (dir hissp.._macro_)

   ;;; Notice its containing module. Take a minute to read its docstring.

   (help hissp.macros.)

   ;;; The macros will still be available from there even if you clobber
   ;;; your _macro_ copy. Recall that you can invoke macros using their
   ;;; fully-qualified names.

   ;;; The bundled macros have individual docstrings with usage examples.

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

   ;;; The dosctrings use reStructuredText markup. While readable as plain
   ;;; text in the help console, they're also rendered as HTML using Sphinx
   ;;; in Hissp's online API docs. Find them at https://hissp.rtfd.io

   ;;; Familiarize yourself with a macro suite, such as the bundled macros.
   ;;; It makes Hissp that much more usable.

   ;;;; 15 Advanced Reader Macros

   ;;;; 15.1 The Discard Macro

   #> _#"The discard reader macro _# omits the next form.
   #..It's a way to comment out code structurally.
   #..It can also make block comments like this one.
   #..This would show up when compiled if not for _#.
   #..Of course, a string expression like this one wouldn't do anything
   #..in Python, even if it were compiled in. But the need to escape double
   #..quotes might make ;; comments easier.
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
   >>> "Comment(content='comments are parsed objects too!')"
   "Comment(content='comments are parsed objects too!')"


   ;;; Except for strings and tuples, objects in Hissp should evaluate
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


   ;;; Recall that Hissp-level string objects can represent
   ;;; arbitrary Python code. It's usually used for identifiers,
   ;;; but can be anything, even complex formulas.

   #> (lambda abc
   #..  ;; Hissp may not have operators, but Python does.
   #..  .#"(-b + (b**2 - 4*a*c)**0.5)/(2*a)")
   >>> (lambda a,b,c:(-b + (b**2 - 4*a*c)**0.5)/(2*a))
   <function <lambda> at 0x...>


   ;;; Remember the raw string and hash string reader syntax makes Python-
   ;;; level strings, via a Hissp-level string containing a Python string
   ;;; literal. It is NOT for creating a Hissp-level string, which would
   ;;; normally contain Python code. Use inject for that.

   #> '"a string"                         ;Python code for a string. In a string.
   >>> "('a string')"
   "('a string')"

   ;; Injection of an object to the Hissp level. In this case, a string object.
   #> '.#"a string"                       ;Quoting renders a Hissp-level string as data.
   >>> 'a string'
   'a string'


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


   ;; Statement injections work at the top level only.
   #> .#"from operator import *"          ;All your operator are belong to us.
   >>> from operator import *


   ;;;; 15.4 Extra (!), the Final Builtin Reader Macro

   ;;; Reader macros take one primary argument, but additional arguments
   ;;; can be passed in with the extra macro !. A reader macro consumes the
   ;;; next parsed object, and if it's an Extra, consumes one again. Thus,
   ;;; extras must be written between the # and primary argument, but
   ;;; because they're often optional refinements, which are easier to
   ;;; define as trailing optional parameters in Python functions, they get
   ;;; passed in after the primary argument.

   #> (setattr _macro_ 'L\# en#list) ; (help _macro_.en\#)
   >>> setattr(
   ...   _macro_,
   ...   'LQzHASH_',
   ...   (lambda *_QzNo84_xs:
   ...     list(
   ...       _QzNo84_xs)))


   #> L#primary
   >>> ['primary']
   ['primary']

   #> L#!1 primary
   >>> ['primary', 1]
   ['primary', 1]


   ;; Alias can work on reader macros too!
   #> (hissp.._macro_.alias M: hissp.._macro_) ; prelude alternative
   >>> # hissp.._macro_.alias
   ... # hissp.macros.._macro_.defmacro
   ... # hissp.macros.._macro_.let
   ... (lambda _QzNo7_fn=(lambda _QzNo27_prime,_QzNo27_reader=None,*_QzNo27_args:(
   ...   'Aliases ``hissp.._macro_`` as ``MQzCOLON_#``.',
   ...   # hissp.macros.._macro_.ifQz_else
   ...   (lambda b,c,a:c()if b else a())(
   ...     _QzNo27_reader,
   ...     (lambda :
   ...       __import__('builtins').getattr(
   ...         __import__('hissp')._macro_,
   ...         ('{}{}').format(
   ...           _QzNo27_reader,
   ...           # hissp.macros.._macro_.ifQz_else
   ...           (lambda b,c,a:c()if b else a())(
   ...             'hissp.._macro_'.endswith(
   ...               '._macro_'),
   ...             (lambda :'QzHASH_'),
   ...             (lambda :('')))))(
   ...         _QzNo27_prime,
   ...         *_QzNo27_args)),
   ...     (lambda :
   ...       ('{}.{}').format(
   ...         'hissp.._macro_',
   ...         _QzNo27_prime))))[-1]):(
   ...   __import__('builtins').setattr(
   ...     _QzNo7_fn,
   ...     '__doc__',
   ...     'Aliases ``hissp.._macro_`` as ``MQzCOLON_#``.'),
   ...   __import__('builtins').setattr(
   ...     _QzNo7_fn,
   ...     '__qualname__',
   ...     ('.').join(
   ...       ('_macro_',
   ...        'MQzCOLON_QzHASH_',))),
   ...   __import__('builtins').setattr(
   ...     __import__('operator').getitem(
   ...       __import__('builtins').globals(),
   ...       '_macro_'),
   ...     'MQzCOLON_QzHASH_',
   ...     _QzNo7_fn))[-1])()

   #> M:#!b"Read-time b# via alias."      ;Extra arg for alias with (!)
   >>> b'Read-time b# via alias.'
   b'Read-time b# via alias.'


   #> L# !1 !2 primary                    ;Note the order!
   >>> ['primary', 1, 2]
   ['primary', 1, 2]

   #> .#(en#list "primary" 1 2)           ;Inject. Note the order.
   >>> ['primary', 1, 2]
   ['primary', 1, 2]


   #> !1                                  ;! is for a single Extra.
   >>> __import__('pickle').loads(  # Extra([1])
   ...     b'ccopyreg\n'
   ...     b'_reconstructor\n'
   ...     b'(chissp.reader\n'
   ...     b'Extra\n'
   ...     b'cbuiltins\n'
   ...     b'tuple\n'
   ...     b'(I1\n'
   ...     b'ttR.'
   ... )
   Extra([1])

   #> hissp.reader..Extra#(: :? 0 :* (1 2 3)) ; but Extra can have multiple elements.
   >>> __import__('pickle').loads(  # Extra([':', ':?', 0, ':*', (1, 2, 3)])
   ...     b'ccopyreg\n'
   ...     b'_reconstructor\n'
   ...     b'(chissp.reader\n'
   ...     b'Extra\n'
   ...     b'cbuiltins\n'
   ...     b'tuple\n'
   ...     b'(V:\n'
   ...     b'V:?\n'
   ...     b'I0\n'
   ...     b'V:*\n'
   ...     b'(I1\n'
   ...     b'I2\n'
   ...     b'I3\n'
   ...     b'tttR.'
   ... )
   Extra([':', ':?', 0, ':*', (1, 2, 3)])

   #> !!!1 2 3                            ;Extras can have extras. They stack.
   >>> __import__('pickle').loads(  # Extra([1, 2, 3])
   ...     b'ccopyreg\n'
   ...     b'_reconstructor\n'
   ...     b'(chissp.reader\n'
   ...     b'Extra\n'
   ...     b'cbuiltins\n'
   ...     b'tuple\n'
   ...     b'(I1\n'
   ...     b'I2\n'
   ...     b'I3\n'
   ...     b'ttR.'
   ... )
   Extra([1, 2, 3])


   #> L#!: !:* !(0 1 2) !:? !3 primary    ;Unpacking works like calls.
   >>> ['primary', 0, 1, 2, 3]
   ['primary', 0, 1, 2, 3]

   #> L#!0 !: !:* !(1 2 3)primary         ;Same effect.
   >>> ['primary', 0, 1, 2, 3]
   ['primary', 0, 1, 2, 3]

   #> L#hissp.reader..Extra#(0 : :* (1 2 3))primary ;Same effect.
   >>> ['primary', 0, 1, 2, 3]
   ['primary', 0, 1, 2, 3]


   #> (setattr _macro_ 'E\# hissp.reader..Extra)
   >>> setattr(
   ...   _macro_,
   ...   'EQzHASH_',
   ...   __import__('hissp.reader',fromlist='?').Extra)


   #> L# !0 E#(1 2) !3 primary            ;Same effect.
   >>> ['primary', 0, 1, 2, 3]
   ['primary', 0, 1, 2, 3]

   #> L#E#(0 : :* (1 2 3))primary         ;Same effect.
   >>> ['primary', 0, 1, 2, 3]
   ['primary', 0, 1, 2, 3]


   ;; Kwargs also work like calls.
   #> builtins..dict#()
   >>> {}
   {}

   #> builtins..dict#!: !spam !1  !foo !2  !:** !.#(dict : eggs 3  bar 4)()
   >>> {'spam': 1, 'foo': 2, 'eggs': 3, 'bar': 4}
   {'spam': 1, 'foo': 2, 'eggs': 3, 'bar': 4}

   #> builtins..dict#E#(: spam 1  foo 2  :** .#(dict : eggs 3  bar 4))()
   >>> {'spam': 1, 'foo': 2, 'eggs': 3, 'bar': 4}
   {'spam': 1, 'foo': 2, 'eggs': 3, 'bar': 4}

   #> builtins..dict#!: !!spam 1 !!foo 2 !!:** .#(dict : eggs 3  bar 4)()
   >>> {'spam': 1, 'foo': 2, 'eggs': 3, 'bar': 4}
   {'spam': 1, 'foo': 2, 'eggs': 3, 'bar': 4}


   ;; Yeah, you can nest these if you have to.
   #> L# !x
   #..   !L# !1 L# !A
   #..          inner
   #..   !y
   #..outer
   >>> ['outer', 'x', [['inner', 'A'], 1], 'y']
   ['outer', 'x', [['inner', 'A'], 1], 'y']


   ;; The compiler will evaluate tuples no matter how the reader produces them.
   #> builtins..tuple#L# !"Hello" !"World!" print
   >>> print(
   ...   ('Hello'),
   ...   ('World!'))
   Hello World!


.. admonition:: Pardon our dust.

   You've reached the end of the Tour.
   Sections after this point may be incomplete or missing.
   (This is the bleeding-edge master branch version of the docs.)
   The remainder of the old Whirlwind Tour is in the process of being migrated to the API docs.
   Parts that haven't been migrated yet are included below for completeness.

.. Lissp::

   ;;;; 14 The Bundled Macros

   ;;;; 14.1 Collections

   ;;;; 14.2 Side Effect

   ;;;; 14.3 Definition

   ;;;; 14.4 Locals

   ;;;; 14.5 Configuration

   ;;;; 14.6 Threading

   ;;;; 14.7 The Prelude

   ;;; An inline convenience micro-prelude for Hissp.
   ;;; Imports partial and reduce; star imports from operator and itertools;
   ;;; defines Python interop utilities engarde, enter, and Ensue; and
   ;;; imports a copy of hissp.macros.._macro_ (if available). Usually the
   ;;; first form in a file, because it overwrites _macro_, but completely
   ;;; optional. Implied for $ lissp -c commands.

   ;; N.B. Sections after this one may require the prelude to work!
   #> (hissp.._macro_.prelude)            ;Or just (prelude) in the REPL.
   >>> # hissp.._macro_.prelude
   ... __import__('builtins').exec(
   ...   ('from functools import partial,reduce\n'
   ...    'from itertools import *;from operator import *\n'
   ...    'def engarde(xs,h,f,/,*a,**kw):\n'
   ...    ' try:return f(*a,**kw)\n'
   ...    ' except xs as e:return h(e)\n'
   ...    'def enter(c,f,/,*a):\n'
   ...    ' with c as C:return f(*a,C)\n'
   ...    "class Ensue(__import__('collections.abc').abc.Generator):\n"
   ...    ' send=lambda s,v:s.g.send(v);throw=lambda s,*x:s.g.throw(*x);F=0;X=();Y=[]\n'
   ...    ' def __init__(s,p):s.p,s.g,s.n=p,s._(s),s.Y\n'
   ...    ' def _(s,k,v=None):\n'
   ...    "  while isinstance(s:=k,__class__) and not setattr(s,'sent',v):\n"
   ...    '   try:k,y=s.p(s),s.Y;v=(yield from y)if s.F or y is s.n else(yield y)\n'
   ...    '   except s.X as e:v=e\n'
   ...    '  return k\n'
   ...    "_macro_=__import__('types').SimpleNamespace()\n"
   ...    "try:exec('from hissp.macros._macro_ import *',vars(_macro_))\n"
   ...    'except ModuleNotFoundError:pass'),
   ...   __import__('builtins').globals())


   ;;;; 14.8 Control Flow

   ;;; Hissp has no innate control flow, but you can build them with macros.

   ;; 1 2 3 4 5 6 7 True

   ;;;; 14.9 Raising Exceptions

   #> (throw Exception)                   ;Raise exception objects or classes.
   >>> # throw
   ... # hissp.macros.._macro_.throwQzSTAR_
   ... (lambda g=(c for c in''):g.close()or g.throw)()(
   ...   Exception)
   Traceback (most recent call last):
     ...
   Exception

   #> (throw (TypeError "message"))
   >>> # throw
   ... # hissp.macros.._macro_.throwQzSTAR_
   ... (lambda g=(c for c in''):g.close()or g.throw)()(
   ...   TypeError(
   ...     ('message')))
   Traceback (most recent call last):
     ...
   TypeError: message


   #> (throw-from Exception (Exception "message")) ;Explicit chaining.
   >>> # throwQz_from
   ... # hissp.macros.._macro_.throwQzSTAR_
   ... (lambda g=(c for c in''):g.close()or g.throw)()(
   ...   # hissp.macros.._macro_.let
   ...   (lambda _QzNo47_G=(lambda _QzNo47_x:
   ...     # hissp.macros.._macro_.ifQz_else
   ...     (lambda b,c,a:c()if b else a())(
   ...       # hissp.macros.._macro_.QzET_QzET_
   ...       # hissp.macros.._macro_.let
   ...       (lambda _QzNo44_G=__import__('builtins').isinstance(
   ...         _QzNo47_x,
   ...         __import__('builtins').type):
   ...         # hissp.macros.._macro_.ifQz_else
   ...         (lambda b,c,a:c()if b else a())(
   ...           _QzNo44_G,
   ...           (lambda :
   ...             # hissp.macros..QzMaybe_.QzET_QzET_
   ...             __import__('builtins').issubclass(
   ...               _QzNo47_x,
   ...               __import__('builtins').BaseException)),
   ...           (lambda :_QzNo44_G)))(),
   ...       (lambda :_QzNo47_x()),
   ...       (lambda :_QzNo47_x))):
   ...     # hissp.macros.._macro_.attach
   ...     # hissp.macros.._macro_.let
   ...     (lambda _QzNo31_target=_QzNo47_G(
   ...       Exception):(
   ...       __import__('builtins').setattr(
   ...         _QzNo31_target,
   ...         '__cause__',
   ...         _QzNo47_G(
   ...           Exception(
   ...             ('message')))),
   ...       _QzNo31_target)[-1])())())
   Traceback (most recent call last):
     ...
   Exception


   ;;; There's also a throw* you normally shouldn't use. See API doc.

   ;;; Assertions. They're always about something, which is
   ;;; threaded-first into the predicate expression, and is the result of
   ;;; the form. The message expressions are optional. In this context,
   ;;; the `it` refers to the something.
   ;;; Try turning off __debug__ in a new REPL: $ python -Om hissp

   #> (ensure 7 (-> (mod 2) (eq 0))
   #..  it "That's odd.")
   >>> # ensure
   ... # hissp.macros.._macro_.let
   ... (lambda it=(7):(
   ...   # hissp.macros.._macro_.unless
   ...   (lambda b,a:()if b else a())(
   ...     # hissp.macros.._macro_.Qz_QzGT_
   ...     # Qz_QzGT_
   ...     eq(
   ...       mod(
   ...         it,
   ...         (2)),
   ...       (0)),
   ...     (lambda :
   ...       # hissp.macros.._macro_.throw
   ...       # hissp.macros.._macro_.throwQzSTAR_
   ...       (lambda g=(c for c in''):g.close()or g.throw)()(
   ...         __import__('builtins').AssertionError(
   ...           it,
   ...           ("That's odd."))))),
   ...   it)[-1])()
   Traceback (most recent call last):
     ...
   AssertionError: (7, "That's odd.")


   ;;; Note that for pre-compiled code, it's the __debug__ state at
   ;;; compile time, not at run time, that determines if ensure
   ;;; assertions are turned on.

   ;;;; 14.10 Obligatory Factorial III

   ;; With the prelude (§14.7), we can define a nicer-looking version.
   #> (define factorial-III
   #..  (lambda i
   #..    (if-else (le i 1)
   #..      1
   #..      (mul i (factorial-III (sub i 1))))))
   >>> # define
   ... __import__('builtins').globals().update(
   ...   factorialQz_III=(lambda i:
   ...                     # ifQz_else
   ...                     (lambda b,c,a:c()if b else a())(
   ...                       le(
   ...                         i,
   ...                         (1)),
   ...                       (lambda :(1)),
   ...                       (lambda :
   ...                         mul(
   ...                           i,
   ...                           factorialQz_III(
   ...                             sub(
   ...                               i,
   ...                               (1))))))))

   #> (factorial-III 7)
   >>> factorialQz_III(
   ...   (7))
   5040


   ;;;; 15 Exception Handling

   ;; Defined by the prelude (§14.7). Guards against targeted exceptions.
   #> (engarde `(,FloatingPointError ,ZeroDivisionError)               ;two targets
   #..         (lambda e (print "Oops!") e)                            ;handler (returns exception)
   #..         truediv 6 0)                                            ;calls it on your behalf
   >>> engarde(
   ...   (lambda * _: _)(
   ...     FloatingPointError,
   ...     ZeroDivisionError),
   ...   (lambda e:(
   ...     print(
   ...       ('Oops!')),
   ...     e)[-1]),
   ...   truediv,
   ...   (6),
   ...   (0))
   Oops!
   ZeroDivisionError('division by zero')


   #> (engarde ArithmeticError repr truediv 6 0)                       ;superclass target
   >>> engarde(
   ...   ArithmeticError,
   ...   repr,
   ...   truediv,
   ...   (6),
   ...   (0))
   "ZeroDivisionError('division by zero')"

   #> (engarde ArithmeticError repr truediv 6 2)                       ;returned answer
   >>> engarde(
   ...   ArithmeticError,
   ...   repr,
   ...   truediv,
   ...   (6),
   ...   (2))
   3.0


   ;; You can stack them.
   #> (engarde Exception                                               ;The outer engarde
   #.. print
   #.. engarde ZeroDivisionError                                       ; calls the inner.
   #.. (lambda e (print "It means what you want it to mean."))
   #.. truediv "6" 0)                                                  ;Try variations.
   >>> engarde(
   ...   Exception,
   ...   print,
   ...   engarde,
   ...   ZeroDivisionError,
   ...   (lambda e:
   ...     print(
   ...       ('It means what you want it to mean.'))),
   ...   truediv,
   ...   ('6'),
   ...   (0))
   unsupported operand type(s) for /: 'str' and 'int'


   #> (engarde Exception
   #..         (lambda x x.__cause__)
   #..         (lambda : (throw-from Exception (Exception "msg"))))
   >>> engarde(
   ...   Exception,
   ...   (lambda x:x.__cause__),
   ...   (lambda :
   ...     # throwQz_from
   ...     # hissp.macros.._macro_.throwQzSTAR_
   ...     (lambda g=(c for c in''):g.close()or g.throw)()(
   ...       # hissp.macros.._macro_.let
   ...       (lambda _QzNo47_G=(lambda _QzNo47_x:
   ...         # hissp.macros.._macro_.ifQz_else
   ...         (lambda b,c,a:c()if b else a())(
   ...           # hissp.macros.._macro_.QzET_QzET_
   ...           # hissp.macros.._macro_.let
   ...           (lambda _QzNo44_G=__import__('builtins').isinstance(
   ...             _QzNo47_x,
   ...             __import__('builtins').type):
   ...             # hissp.macros.._macro_.ifQz_else
   ...             (lambda b,c,a:c()if b else a())(
   ...               _QzNo44_G,
   ...               (lambda :
   ...                 # hissp.macros..QzMaybe_.QzET_QzET_
   ...                 __import__('builtins').issubclass(
   ...                   _QzNo47_x,
   ...                   __import__('builtins').BaseException)),
   ...               (lambda :_QzNo44_G)))(),
   ...           (lambda :_QzNo47_x()),
   ...           (lambda :_QzNo47_x))):
   ...         # hissp.macros.._macro_.attach
   ...         # hissp.macros.._macro_.let
   ...         (lambda _QzNo31_target=_QzNo47_G(
   ...           Exception):(
   ...           __import__('builtins').setattr(
   ...             _QzNo31_target,
   ...             '__cause__',
   ...             _QzNo47_G(
   ...               Exception(
   ...                 ('msg')))),
   ...           _QzNo31_target)[-1])())())))
   Exception('msg')


   ;;;; 16 Generators

   ;; Defined by the prelude (§14.7), Ensue gives you infinite lazy
   ;; iterables, easy as recursion. Compare to loop-from (§14.8).
   #> (define fibonacci
   #..  (lambda (: a 1  b 1)
   #..    (Ensue (lambda (step)
   #..             (set@ step.Y a)        ;Y for yield.
   #..             (fibonacci b (add a b))))))
   >>> # define
   ... __import__('builtins').globals().update(
   ...   fibonacci=(lambda a=(1),b=(1):
   ...               Ensue(
   ...                 (lambda step:(
   ...                   # setQzAT_
   ...                   # hissp.macros.._macro_.let
   ...                   (lambda _QzNo29_val=a:(
   ...                     __import__('builtins').setattr(
   ...                       step,
   ...                       'Y',
   ...                       _QzNo29_val),
   ...                     _QzNo29_val)[-1])(),
   ...                   fibonacci(
   ...                     b,
   ...                     add(
   ...                       a,
   ...                       b)))[-1]))))

   #> (list (itertools..islice (fibonacci) 7))
   >>> list(
   ...   __import__('itertools').islice(
   ...     fibonacci(),
   ...     (7)))
   [1, 1, 2, 3, 5, 8, 13]



   #> (define my-range                    ;Terminate by not returning an Ensue.
   #..  (lambda in
   #..    (Ensue (lambda (step)
   #..             (when (lt i n)         ;Acts like a while loop.
   #..               (set@ step.Y i)
   #..               (my-range (add i 1) n)))))) ;Conditional recursion.
   >>> # define
   ... __import__('builtins').globals().update(
   ...   myQz_range=(lambda i,n:
   ...                Ensue(
   ...                  (lambda step:
   ...                    # when
   ...                    (lambda b,c:c()if b else())(
   ...                      lt(
   ...                        i,
   ...                        n),
   ...                      (lambda :(
   ...                        # setQzAT_
   ...                        # hissp.macros.._macro_.let
   ...                        (lambda _QzNo108_val=i:(
   ...                          __import__('builtins').setattr(
   ...                            step,
   ...                            'Y',
   ...                            _QzNo108_val),
   ...                          _QzNo108_val)[-1])(),
   ...                        myQz_range(
   ...                          add(
   ...                            i,
   ...                            (1)),
   ...                          n))[-1]))))))

   #> (list (my-range 1 6))
   >>> list(
   ...   myQz_range(
   ...     (1),
   ...     (6)))
   [1, 2, 3, 4, 5]


   ;; Set F to yield-From mode.
   #> (Ensue (lambda (step)
   #..         (attach step :
   #..           Y '(1 2 3 4 5)
   #..           F True)
   #..         None))
   >>> Ensue(
   ...   (lambda step:(
   ...     # attach
   ...     # hissp.macros.._macro_.let
   ...     (lambda _QzNo31_target=step:(
   ...       __import__('builtins').setattr(
   ...         _QzNo31_target,
   ...         'Y',
   ...         ((1),
   ...          (2),
   ...          (3),
   ...          (4),
   ...          (5),)),
   ...       __import__('builtins').setattr(
   ...         _QzNo31_target,
   ...         'F',
   ...         True),
   ...       _QzNo31_target)[-1])(),
   ...     None)[-1]))
   <...Ensue object at ...>

   #> (list _)
   >>> list(
   ...   _)
   [1, 2, 3, 4, 5]


   #> (define recycle
   #..  (lambda (itr)
   #..    (Ensue (lambda (step)
   #..             (attach step :         ;Implicit continuation.
   #..               Y itr
   #..               F 1)))))             ;The step is an Ensue instance.
   >>> # define
   ... __import__('builtins').globals().update(
   ...   recycle=(lambda itr:
   ...             Ensue(
   ...               (lambda step:
   ...                 # attach
   ...                 # hissp.macros.._macro_.let
   ...                 (lambda _QzNo31_target=step:(
   ...                   __import__('builtins').setattr(
   ...                     _QzNo31_target,
   ...                     'Y',
   ...                     itr),
   ...                   __import__('builtins').setattr(
   ...                     _QzNo31_target,
   ...                     'F',
   ...                     (1)),
   ...                   _QzNo31_target)[-1])()))))

   #> (-> '(1 2 3) recycle (islice 7) list)
   >>> # Qz_QzGT_
   ... list(
   ...   islice(
   ...     recycle(
   ...       ((1),
   ...        (2),
   ...        (3),)),
   ...     (7)))
   [1, 2, 3, 1, 2, 3, 1]


   #> (define echo
   #..  (Ensue (lambda (step)
   #..           (set@ step.Y step.sent)
   #..           step)))
   >>> # define
   ... __import__('builtins').globals().update(
   ...   echo=Ensue(
   ...          (lambda step:(
   ...            # setQzAT_
   ...            # hissp.macros.._macro_.let
   ...            (lambda _QzNo29_val=step.sent:(
   ...              __import__('builtins').setattr(
   ...                step,
   ...                'Y',
   ...                _QzNo29_val),
   ...              _QzNo29_val)[-1])(),
   ...            step)[-1])))

   #> (.send echo None)                   ;Always send a None first. Same as Python.
   >>> echo.send(
   ...   None)

   #> (.send echo "Yodle!")               ;Generators are two-way.
   >>> echo.send(
   ...   ('Yodle!'))
   'Yodle!'

   #> (.send echo 42)
   >>> echo.send(
   ...   (42))
   42


   ;;;; 17 Context Managers

   #> (define wrap
   #..  (contextlib..contextmanager
   #..   (lambda (msg)
   #..     (print "enter" msg)
   #..     (Ensue (lambda (step)
   #..              (set@ step.Y msg)
   #..              (Ensue (lambda (step)
   #..                       (print "exit" msg))))))))
   >>> # define
   ... __import__('builtins').globals().update(
   ...   wrap=__import__('contextlib').contextmanager(
   ...          (lambda msg:(
   ...            print(
   ...              ('enter'),
   ...              msg),
   ...            Ensue(
   ...              (lambda step:(
   ...                # setQzAT_
   ...                # hissp.macros.._macro_.let
   ...                (lambda _QzNo33_val=msg:(
   ...                  __import__('builtins').setattr(
   ...                    step,
   ...                    'Y',
   ...                    _QzNo33_val),
   ...                  _QzNo33_val)[-1])(),
   ...                Ensue(
   ...                  (lambda step:
   ...                    print(
   ...                      ('exit'),
   ...                      msg))))[-1])))[-1])))


   ;; Defined by the prelude. Like a with statement.
   #> (enter (wrap 'A)
   #..       (lambda a (print a)))
   >>> enter(
   ...   wrap(
   ...     'A'),
   ...   (lambda a:
   ...     print(
   ...       a)))
   enter A
   A
   exit A


   #> (enter (wrap 'A)
   #.. enter (wrap 'B)
   #.. enter (wrap 'C)                    ;You can stack them.
   #.. (lambda abc (print a b c)))
   >>> enter(
   ...   wrap(
   ...     'A'),
   ...   enter,
   ...   wrap(
   ...     'B'),
   ...   enter,
   ...   wrap(
   ...     'C'),
   ...   (lambda a,b,c:
   ...     print(
   ...       a,
   ...       b,
   ...       c)))
   enter A
   enter B
   enter C
   A B C
   exit C
   exit B
   exit A


   #> (define suppress-zde
   #..  (contextlib..contextmanager
   #..   (lambda :
   #..     (Ensue (lambda (step)
   #..              (attach step :
   #..                Y None
   #..                X ZeroDivisionError) ;X for eXcept (can be a tuple).
   #..              (Ensue (lambda (step)
   #..                       (print "Caught a" step.sent))))))))
   >>> # define
   ... __import__('builtins').globals().update(
   ...   suppressQz_zde=__import__('contextlib').contextmanager(
   ...                    (lambda :
   ...                      Ensue(
   ...                        (lambda step:(
   ...                          # attach
   ...                          # hissp.macros.._macro_.let
   ...                          (lambda _QzNo35_target=step:(
   ...                            __import__('builtins').setattr(
   ...                              _QzNo35_target,
   ...                              'Y',
   ...                              None),
   ...                            __import__('builtins').setattr(
   ...                              _QzNo35_target,
   ...                              'X',
   ...                              ZeroDivisionError),
   ...                            _QzNo35_target)[-1])(),
   ...                          Ensue(
   ...                            (lambda step:
   ...                              print(
   ...                                ('Caught a'),
   ...                                step.sent))))[-1])))))

   #> (enter (suppress-zde)
   #..  (lambda _ (truediv 1 0)))
   >>> enter(
   ...   suppressQz_zde(),
   ...   (lambda _:
   ...     truediv(
   ...       (1),
   ...       (0))))
   Caught a division by zero

   #> (enter (suppress-zde)
   #..  (lambda _ (truediv 4 2)))         ;No exception, so step.sent was .send() value.
   >>> enter(
   ...   suppressQz_zde(),
   ...   (lambda _:
   ...     truediv(
   ...       (4),
   ...       (2))))
   Caught a None
   2.0

   #> (enter (suppress-zde)
   #..  (lambda _ (throw Exception)))
   >>> enter(
   ...   suppressQz_zde(),
   ...   (lambda _:
   ...     # throw
   ...     # hissp.macros.._macro_.throwQzSTAR_
   ...     (lambda g=(c for c in''):g.close()or g.throw)()(
   ...       Exception)))
   Traceback (most recent call last):
     ...
   Exception


   ;;;; 19 The Bundled Reader Macros

   ;;; Like the other bundled macros, these are available in the REPL by
   ;;; default, but most other contexts, like .lissp files, require fully-
   ;;; qualified names. The prelude (§14.7) is the easiest way to add the
   ;;; bundled macros to a module.

   #> (reduce XY#(add Y X) "abcd")        ;Binary anaphoric lambda.
   >>> reduce(
   ...   (lambda X,Y:
   ...     add(
   ...       Y,
   ...       X)),
   ...   ('abcd'))
   'dcba'


   #> (engarde Exception
   #..         X#(print X.__cause__)      ;Unary again.
   #..         O#(throw-from Exception (Exception "msg"))) ;Nullary/thunk.
   >>> engarde(
   ...   Exception,
   ...   (lambda X:
   ...     print(
   ...       X.__cause__)),
   ...   (lambda :
   ...     # throwQz_from
   ...     # hissp.macros.._macro_.throwQzSTAR_
   ...     (lambda g=(c for c in''):g.close()or g.throw)()(
   ...       # hissp.macros.._macro_.let
   ...       (lambda _QzNo48_G=(lambda _QzNo48_x:
   ...         # hissp.macros.._macro_.ifQz_else
   ...         (lambda b,c,a:c()if b else a())(
   ...           # hissp.macros.._macro_.QzET_QzET_
   ...           # hissp.macros.._macro_.let
   ...           (lambda _QzNo44_G=__import__('builtins').isinstance(
   ...             _QzNo48_x,
   ...             __import__('builtins').type):
   ...             # hissp.macros.._macro_.ifQz_else
   ...             (lambda b,c,a:c()if b else a())(
   ...               _QzNo44_G,
   ...               (lambda :
   ...                 # hissp.macros..QzMaybe_.QzET_QzET_
   ...                 __import__('builtins').issubclass(
   ...                   _QzNo48_x,
   ...                   __import__('builtins').BaseException)),
   ...               (lambda :_QzNo44_G)))(),
   ...           (lambda :_QzNo48_x()),
   ...           (lambda :_QzNo48_x))):
   ...         # hissp.macros.._macro_.attach
   ...         # hissp.macros.._macro_.let
   ...         (lambda _QzNo31_target=_QzNo48_G(
   ...           Exception):(
   ...           __import__('builtins').setattr(
   ...             _QzNo31_target,
   ...             '__cause__',
   ...             _QzNo48_G(
   ...               Exception(
   ...                 ('msg')))),
   ...           _QzNo31_target)[-1])())())))
   msg


   ;;; Ternary anaphoric lambda, applied to an injected code string.
   ;;; The imports would have been harder if the whole expression were
   ;;; injected Python. Get the best of both worlds.

   #> (XYZ#.#"X*Y == Z" : X math..pi  Y 2  Z math..tau) ;Or inject the 2.
   >>> (lambda X,Y,Z:X*Y == Z)(
   ...   X=__import__('math').pi,
   ...   Y=(2),
   ...   Z=__import__('math').tau)
   True


   ;;; Slicing is important enough for a shorthand.
   ;;; This variant works best on simple cases. The slice indexes are all
   ;;; injected Python here.

   #> ([#-2:1:-2] "QuaoblcldefHg")
   >>> (lambda _QzNo32_G:(_QzNo32_G[-2:1:-2]))(
   ...   ('QuaoblcldefHg'))
   'Hello'


   #> b#"bytes"                           ;Bytes reader macro.
   >>> b'bytes'
   b'bytes'

   #> b'bytes'                            ;NameError about 'bQzAPOS_bytesQzAPOS_'
   >>> bQzAPOS_bytesQzAPOS_
   Traceback (most recent call last):
     ...
   NameError: name 'bQzAPOS_bytesQzAPOS_' is not defined


   #> b#"bytes
   #..with
   #..newlines
   #.."                                   ;Same as b#"bytes\nwith\nnewlines\n".
   >>> b'bytes\nwith\nnewlines\n'
   b'bytes\nwith\nnewlines\n'


   #> (help _macro_.b\#)                  ;Unqualified reader macros live in _macro_ too.
   >>> help(
   ...   _macro_.bQzHASH_)
   Help on function <lambda> in module hissp.macros:
   <BLANKLINE>
   <lambda> lambda raw
       ``b#`` `bytes` literal reader macro
   <BLANKLINE>


   ;; The en# reader macro converts a function applicable to one tuple
   ;; to a function of its elements.
   #> (en#list 1 2 3)
   >>> (lambda *_QzNo31_xs:
   ...   list(
   ...     _QzNo31_xs))(
   ...   (1),
   ...   (2),
   ...   (3))
   [1, 2, 3]

   #> (en#.extend _ 4 5 6)                ;Methods too.
   >>> (lambda _QzNo31_self,*_QzNo31_xs:
   ...   _QzNo31_self.extend(
   ...     _QzNo31_xs))(
   ...   _,
   ...   (4),
   ...   (5),
   ...   (6))

   #> _
   >>> _
   [1, 2, 3, 4, 5, 6]


   #> (en#collections..deque 1 2 3)
   >>> (lambda *_QzNo31_xs:
   ...   __import__('collections').deque(
   ...     _QzNo31_xs))(
   ...   (1),
   ...   (2),
   ...   (3))
   deque([1, 2, 3])


   ;; Applying en# to X# results in a variadic anaphoric lambda.
   #> (define enjoin en#X#(.join "" (map str X)))
   >>> # define
   ... __import__('builtins').globals().update(
   ...   enjoin=(lambda *_QzNo55_xs:
   ...            (lambda X:
   ...              ('').join(
   ...                map(
   ...                  str,
   ...                  X)))(
   ...              _QzNo55_xs)))

   #> (enjoin "Sum: "(add 2 3)". Product: "(mul 2 3)".")
   >>> enjoin(
   ...   ('Sum: '),
   ...   add(
   ...     (2),
   ...     (3)),
   ...   ('. Product: '),
   ...   mul(
   ...     (2),
   ...     (3)),
   ...   ('.'))
   'Sum: 5. Product: 6.'


   ;;; There are no bundled reader macros for a quinary, senary, etc. but
   ;;; the en#X# variadic or a normal lambda form can be used.

   ;;; Not technically a reader macro, but a bundled macro for defining them.
   ;;; Alias makes a new reader macro to abbreviate a qualifier.
   ;;; This is an alternative to adding an import to _macro_ or globals.

   #> (hissp.._macro_.alias M: hissp.._macro_)
   >>> # hissp.._macro_.alias
   ... # hissp.macros.._macro_.defmacro
   ... # hissp.macros.._macro_.let
   ... (lambda _QzNo7_fn=(lambda _QzNo27_prime,_QzNo27_reader=None,*_QzNo27_args:(
   ...   'Aliases ``hissp.._macro_`` as ``MQzCOLON_#``.',
   ...   # hissp.macros.._macro_.ifQz_else
   ...   (lambda b,c,a:c()if b else a())(
   ...     _QzNo27_reader,
   ...     (lambda :
   ...       __import__('builtins').getattr(
   ...         __import__('hissp')._macro_,
   ...         ('{}{}').format(
   ...           _QzNo27_reader,
   ...           # hissp.macros.._macro_.ifQz_else
   ...           (lambda b,c,a:c()if b else a())(
   ...             'hissp.._macro_'.endswith(
   ...               '._macro_'),
   ...             (lambda :'QzHASH_'),
   ...             (lambda :('')))))(
   ...         _QzNo27_prime,
   ...         *_QzNo27_args)),
   ...     (lambda :
   ...       ('{}.{}').format(
   ...         'hissp.._macro_',
   ...         _QzNo27_prime))))[-1]):(
   ...   __import__('builtins').setattr(
   ...     _QzNo7_fn,
   ...     '__doc__',
   ...     'Aliases ``hissp.._macro_`` as ``MQzCOLON_#``.'),
   ...   __import__('builtins').setattr(
   ...     _QzNo7_fn,
   ...     '__qualname__',
   ...     ('.').join(
   ...       ('_macro_',
   ...        'MQzCOLON_QzHASH_',))),
   ...   __import__('builtins').setattr(
   ...     __import__('operator').getitem(
   ...       __import__('builtins').globals(),
   ...       '_macro_'),
   ...     'MQzCOLON_QzHASH_',
   ...     _QzNo7_fn))[-1])()

   #> 'M:#alias
   >>> 'hissp.._macro_.alias'
   'hissp.._macro_.alias'

   #> M:#b\#                              ;b# macro callable
   >>> __import__('hissp')._macro_.bQzHASH_
   <function _macro_.bQzHASH_ at ...>

   #> (M:#b\# "b# macro at compile time")
   >>> # hissp.._macro_.bQzHASH_
   ... b'b# macro at compile time'
   b'b# macro at compile time'

   #> hissp.._macro_.b#"Fully-qualified b# macro at read time."
   >>> b'Fully-qualified b# macro at read time.'
   b'Fully-qualified b# macro at read time.'


   ;; A couple of aliases are bundled:
   #> op#add
   >>> __import__('operator').add
   <built-in function add>

   #> i#chain
   >>> __import__('itertools').chain
   <class 'itertools.chain'>


   ;; A bundled abbreviation
   #> (list chain#(.items (dict : a 1  b 2  c 3)))
   >>> list(
   ...   __import__('itertools').chain.from_iterable(
   ...     dict(
   ...       a=(1),
   ...       b=(2),
   ...       c=(3)).items()))
   ['a', 1, 'b', 2, 'c', 3]



