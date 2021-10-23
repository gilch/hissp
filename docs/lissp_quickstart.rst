.. Copyright 2020, 2021 Matthew Egan Odendahl
   SPDX-License-Identifier: Apache-2.0

.. This hidden doctest adds basic macros for REPL-consistent behavior.
   #> (operator..setitem (globals) '_macro_ (types..SimpleNamespace : :** (vars hissp.basic.._macro_)))
   >>> __import__('operator').setitem(
   ...   globals(),
   ...   '_macro_',
   ...   __import__('types').SimpleNamespace(
   ...     **vars(
   ...         __import__('hissp.basic',fromlist='?')._macro_)))

.. TODO: Interactive via web repl?

Lissp Quick Start
=================

.. raw:: html

   (<a href="_sources/lissp_quickstart.rst.txt">Outputs</a> hidden for brevity.)

.. Lissp::

   ;;;; Lissp Quick Start

   "Lissp is a lightweight text language representing the Hissp
   intermediate language. The Lissp reader parses the Lissp language's
   symbolic expressions as Python objects. The Hissp compiler
   then translates these syntax trees to Python expressions.

   This document is written like a .lissp file, demonstrating Lissp's (and
   thereby Hissp's) features with minimal exposition. This element
   enclosed in double quotes is a docstring for the module.

   To fully understand these examples, you must see their Python
   compilation and output. Some familiarity with Python is assumed.
   Install the Hissp version matching this document. Follow along by
   entering these examples in the REPL. It will show you the compiled
   Python and evaluate it. Try variations that occur to you.

   Familiarity with another Lisp dialect is not assumed, but helpful. If
   you get confused or stuck, read the Hissp tutorial.

   Some examples depend on state set by previous examples to work.
   Prerequisites for examples not in the same section are marked with
   '/!\'. Don't skip these! Re-enter them if you start a new session.
   "

   ;;;; Installation

   ;; These docs are for the bleeding-edge version of Hissp.
   ;; If you run into trouble, report your issues, or try the previous 0.2.0 release.
   ;; Install Hissp with
   ;; $ pip install git+https://github.com/gilch/hissp
   ;; Start the REPL with
   ;; $ lissp
   ;; You can quit with EOF or (exit).

   ;;;; Simple Atoms

   ;; To a first approximation, the Hissp intermediate language is made
   ;; of Python tuples representing syntax trees. The nodes are tuples
   ;; and we call the leaves "atoms". Simple atoms in Lissp are written
   ;; the same way as Python.

   ;;; Singleton

   #> None
   >>> None

   #> ...                                 ;Ellipsis
   >>> ...
   Ellipsis


   ;;; Boolean

   #> False                               ;False == 0
   >>> False
   False

   #> True                                ;True == 1
   >>> True
   True


   ;;; Integer

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


   ;;; Floating-Point

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


   ;;; Complex

   #> 5j                                  ;imaginary
   >>> (5j)
   5j

   #> 4+2j                                ;complex
   >>> ((4+2j))
   (4+2j)

   #> -1_2.3_4e-5_6-7_8.9_8e-7_6j         ;Very complex!
   >>> ((-1.234e-55-7.898e-75j))
   (-1.234e-55-7.898e-75j)


   ;;;; Simple Tuples

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


   ;;;; Symbolic Atoms

   ;;; Identifiers

   #> object                              ;Python identifiers work in Lissp.
   >>> object
   <class 'object'>

   #> object.__class__                    ;Attribute identifier with dot, as Python.
   >>> object.__class__
   <class 'type'>

   #> object.__class__.__name__           ;Attributes chain.
   >>> object.__class__.__name__
   'type'


   ;;; Imports

   #> math.                               ;Module literals import!
   >>> __import__('math')
   <module 'math' ...>

   #> math..tau                           ;Qualified identifier. Attribute of a module.
   >>> __import__('math').tau
   6.283185307179586

   #> collections.abc.                    ;Submodule literal. Has package name.
   >>> __import__('collections.abc',fromlist='?')
   <module 'collections.abc' from '...abc.py'>


   #> builtins..object.__class__          ;Qualified attribute identifier.
   >>> __import__('builtins').object.__class__
   <class 'type'>

   #> collections.abc..Sequence.__class__.__name__ ;Chaining.
   >>> __import__('collections.abc',fromlist='?').Sequence.__class__.__name__
   'ABCMeta'


   ;;;; Simple Forms and Calls

   ;; "Forms" are any data structures that can be evaluated as a Hissp program.
   ;; Simple atoms are forms. They simply evaluate to an equivalent object.

   #> 0x2a
   >>> (42)
   42


   ;; Tuples can also be forms, but their evaluation rules are more complex.
   ;; The common case is a function call. For that, the first element must
   ;; be a callable. The remainder are arguments.

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


   ;;;; String Atoms

   #> :control-word                       ;Colon prefix. Similar to Lisp ":keywords".
   >>> ':control-word'
   ':control-word'

   #> 'symbol                             ;Apostrophe prefix. Represents identifier.
   >>> 'symbol'
   'symbol'


   ;;; Munging

   #> '+                                  ;Read-time munging of invalid identifiers.
   >>> 'QzPLUS_'
   'QzPLUS_'

   #> 'Also-a-symbol!                     ;Alias for 'AlsoQz_aQz_symbolQzBANG_
   >>> 'AlsoQz_aQz_symbolQzBANG_'
   'AlsoQz_aQz_symbolQzBANG_'

   #> '𝐀                                  ;Alias for 'A (unicode normal form KC)
   >>> 'A'
   'A'

   #> '->>
   >>> 'Qz_QzGT_QzGT_'
   'Qz_QzGT_QzGT_'

   #> :->>                                ;Don't represent identifiers, don't munge.
   >>> ':->>'
   ':->>'

   #> :                                   ;Still a control word.
   >>> ':'
   ':'


   ;;; Escaping

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


   ;;; String literals

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


   ;;;; Advanced Calls

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


   ;;; Operators

   ;; Hissp is simpler than Python. No operators! Use calls instead.

   #> (operator..add 40 2)
   >>> __import__('operator').add(
   ...   (40),
   ...   (2))
   42

   #> (.update (globals) : + operator..add) ;/!\ Assignment. Identifier munged.
   >>> globals().update(
   ...   QzPLUS_=__import__('operator').add)

   #> (+ 40 2)                            ;No operators. This is still a function call!
   >>> QzPLUS_(
   ...   (40),
   ...   (2))
   42


   ;;;; Simple Lambdas

   ;; Lambdas are one of Hissp's two "special forms".
   ;; They look like calls, but are special-cased in the Hissp compiler
   ;; to work differently. The first element must be 'lambda', the second
   ;; is the parameters, and finally the body.

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


   ;;; Obligatory Factorial I

   ;; We now have just enough to make more interesting programs.

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


   ;;; Control Flow

   ;; Hissp is simpler than Python. No control flow! Use higher-order functions instead.

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

   ;; Don't worry, Hissp metaprogramming will make this much easier,
   ;; but our limited tools so far are enough to implement a ternary.

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


   ;;; Obligatory Factorial II

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


   ;;;; Advanced Lambdas

   ;; Python parameter types are rather involved. Lambda does all of them.
   ;; Like calls, they are all paired. :? means no default.
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


   #> (lambda (: a :?  b :?  c 1))        ;Parameters left of : pair with :?.
   >>> (lambda a,b,c=(1):())
   <function <lambda> at 0x...>

   #> (lambda (a : b :?  c 1))            ;Implicit :? like calls. Keep sliding.
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


   ;;;; Quote

   ;; Quote is the only other special form. Looks like a call, but isn't.

   ;; A "form" is any Hissp data that can be evaluated.
   ;; Not all data is a valid program in Hissp. E.g. ``(7 42)`` is a
   ;; tuple, containing the integers 7 in the function position, and 42
   ;; after in the first argument position, but it would crash, because
   ;; ints are not callable in Python.

   ;; Quotation suppresses evaluation of Hissp data.
   ;; Treating the code itself as data is the key concept in metaprogramming.

   #> (quote (7 42))
   >>> ((7),
   ...  (42),)
   (7, 42)


   ;; Other objects evaluate to themselves, but strings and tuples have
   ;; special evaluation rules in Hissp. Tuples represent invocations of
   ;; functions, macros, and special forms.

   #> (quote (print 1 2 3 : sep "-"))     ;Just a tuple.
   >>> ('print',
   ...  (1),
   ...  (2),
   ...  (3),
   ...  ':',
   ...  'sep',
   ...  "('-')",)
   ('print', 1, 2, 3, ':', 'sep', "('-')")


   ;; Notice how the string gets an extra layer of quotes vs identifiers.
   ;; This particular tuple happens to be a valid form.
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


   ;; Programmatically modifying the data before compiling it is when
   ;; things start to get interesting, but more on that later.

   ;; Hissp-level strings contain Python code to include in the compiled
   ;; output. These usually contain identifiers, but can be anything.
   ;; Thus, Lissp identifiers read as strings at the Hissp level.
   #> (quote identifier)                  ;Just a string.
   >>> 'identifier'
   'identifier'


   ;; The raw strings and hash strings in Lissp ("..."/#"..." syntax)
   ;; also read as strings at the Hissp level, but they contain a Python
   ;; string literal instead of a Python identifier.
   #> (quote "a string")                  ;Unexpected? "..."/#"..." is reader syntax!
   >>> "('a string')"
   "('a string')"

   #> (eval (quote "a string"))           ;Python code. For a string.
   >>> eval(
   ...   "('a string')")
   'a string'


   ;; Quoting does not suppress munging, however. That happens at read
   ;; time. Quoting doesn't happen until compile time.
   #> (quote +)
   >>> 'QzPLUS_'
   'QzPLUS_'


   ;; Quoting works on any Hissp data.
   #> (quote 42)                          ;Just a number. It was before though.
   >>> (42)
   42


   ;; Strings in Hissp are also used for module literals and control
   ;; words. The compiler does some extra processing before emitting these
   ;; as Python code. Quoting suppresses this processing too.

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

   #> ((lambda (: a :?) a))               ;Not quite! Some have contextual meaning.
   >>> (lambda a:a)()
   Traceback (most recent call last):
     ...
   TypeError: <lambda>() missing 1 required positional argument: 'a'

   #> ((lambda (: a (quote :?)) a))       ;Just a string. Even in context.
   >>> (lambda a=':?':a)()
   ':?'


   ;;;; Simple Reader Macros

   ;; Reader macros are metaprograms to abbreviate Hissp and don't
   ;; represent it directly. They apply to the next parsed Hissp object
   ;; at read time, before the Hissp compiler sees it, and thus before
   ;; they are compiled and evaluated. They end in # except for a few
   ;; builtins-- ' ! ` , ,@

   ;;; Quote

   ;; The ' reader macro is simply an abbreviation for the quote special form.

   #> 'x                                  ;(quote x). Symbols are just quoted identifiers!
   >>> 'x'
   'x'

   #> '(print "Hi")                       ;Quote to reveal the Hissp syntax tree.
   >>> ('print',
   ...  "('Hi')",)
   ('print', "('Hi')")


   ;;; Template Quote

   ;; (Like quasiquote, backquote, or syntax-quote from other Lisps.)
   ;; This is a DSL for making Hissp trees programmatically.
   ;; They're very useful for metaprogramming.

   #> `print                              ;Automatic qualification!
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


   ;; Qualification prevents accidental name collisions in
   ;; programmatically generated code. But qualification doesn't work on
   ;; local variables, which can't be imported. For these, we use a template
   ;; counter suffix instead of a qualifier to ensure a variable can only
   ;; be used in the same template it was defined in. The gensym reader
   ;; macro ($#) generates a symbol with the current template's count.
   #> `($#eggs $#spam $#bacon $#spam)     ;Generated symbols for macro hygiene.
   >>> (lambda * _: _)(
   ...   '_eggs_QzNo9_',
   ...   '_spam_QzNo9_',
   ...   '_bacon_QzNo9_',
   ...   '_spam_QzNo9_')
   ('_eggs_QzNo9_', '_spam_QzNo9_', '_bacon_QzNo9_', '_spam_QzNo9_')

   #> `$#spam                             ;Template count in name prevents collisions.
   >>> '_spam_QzNo10_'
   '_spam_QzNo10_'


   ;;;; Compiler Macros

   ;; We can use functions to to create forms for evaluation.
   ;; This is metaprogramming: code that writes code.

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


   ;; We can accomplish this more easily with a macro invocation.

   ;; Unqualified invocations are macro invocations if the identifier is in
   ;; the current module's _macro_ namespace. The REPL includes one, but
   ;; .lissp files don't have one until you create it.
   (dir)
   (dir _macro_)

   ;; Macros run at compile time, so they get all of their arguments
   ;; unevaluated. The compiler inserts the resulting Hissp at that point
   ;; in the program. Like special forms, macro invocations look like
   ;; function calls, but aren't.
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


   ;; We almost could have accomplished this one with a function, but we'd
   ;; have to either quote the variable name or use a : to pass it in as a
   ;; keyword. The macro invocation is a little shorter. Furthermore, the
   ;; globals function gets the globals dict for the current module. Thus,
   ;; an assign function would assign globals to the module it is defined
   ;; in, not the one where it is used! You could get around this by
   ;; walking up a stack frame with inspect, but that's brittle. The macro
   ;; version just works because it writes the code in line for you, so
   ;; the globals call appears in the right module.

   ;; Macros are a feature of the Hissp compiler. Macroexpansion happens at
   ;; compile time, after the reader, so macros also work in readerless
   ;; mode, or with Hissp readers other than Lissp, like Hebigo.

   ;; Hissp already comes with a define macro for global assignment.
   ;; Our assign macro just re-implemented this.
   (help hissp.basic.._macro_.define)

   ;; An invocation qualified with _macro_ is a macro invocation.
   #> (hissp.basic.._macro_.define SPAM "eggs") ;Note SPAM is not quoted.
   >>> # hissp.basic.._macro_.define
   ... __import__('builtins').globals().update(
   ...   SPAM=('eggs'))

   #> SPAM                                ;'eggs'
   >>> SPAM
   'eggs'


   ;; See the macro expansion by calling it like a method with all arguments quoted.
   ;; This way, the callable isn't qualified with _macro_, so it's a normal call.
   #> (.define hissp.basic.._macro_ 'SPAM '"eggs") ;Method syntax is never macro invocation.
   >>> __import__('hissp.basic',fromlist='?')._macro_.define(
   ...   'SPAM',
   ...   "('eggs')")
   ('.update', ('builtins..globals',), ':', 'SPAM', "('eggs')")


   ;; The REPL's default _macro_ namespace already has the basic macros.
   (help _macro_.define)


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


   ;; Maybe the expanded code could only run it once?
   #> (setattr _macro_
   #..         'oops-triple
   #..         (lambda x
   #..           `((lambda (: x ,x)       ;Expand to lambda call for a local variable.
   #..               (+ x (+ x x))))))
   >>> setattr(
   ...   _macro_,
   ...   'oopsQz_triple',
   ...   (lambda x:
   ...     (lambda * _: _)(
   ...       (lambda * _: _)(
   ...         'lambda',
   ...         (lambda * _: _)(
   ...           ':',
   ...           '__main__..x',
   ...           x),
   ...         (lambda * _: _)(
   ...           '__main__..QzMaybe_.QzPLUS_',
   ...           '__main__..x',
   ...           (lambda * _: _)(
   ...             '__main__..QzMaybe_.QzPLUS_',
   ...             '__main__..x',
   ...             '__main__..x'))))))

   #> (oops-triple 14)                    ;Don't forget that templates qualify symbols!
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
   ...           '_x_QzNo22_',
   ...           x),
   ...         (lambda * _: _)(
   ...           '__main__..QzMaybe_.QzPLUS_',
   ...           '_x_QzNo22_',
   ...           (lambda * _: _)(
   ...             '__main__..QzMaybe_.QzPLUS_',
   ...             '_x_QzNo22_',
   ...             '_x_QzNo22_'))))))

   #> (once-triple (loud-number 14))
   >>> # onceQz_triple
   ... (lambda _x_QzNo22_=loudQz_number(
   ...   (14)):
   ...   __import__('builtins').globals()['QzPLUS_'](
   ...     _x_QzNo22_,
   ...     __import__('builtins').globals()['QzPLUS_'](
   ...       _x_QzNo22_,
   ...       _x_QzNo22_)))()
   14
   42


   ;; Notice the special QzMaybe_ qualifier generated by this template.
   ;; Templates creates these for symbols in the invocation position when
   ;; they can't tell if _macro_ would work. The compiler skips QzMaybe_
   ;; unless it can resolve the symbol with QzMaybe_ as _macro_.
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
   #..          (lambda (first : :* args)
   #..            (.__getitem__ ; Tuple method. Templates produce tuples.
   #..              `(,first ; Result when no args left.
   #..                (operator..add ,first (+ ,@args))) ; Otherwise recur.
   #..              (bool args))))        ;Bools are ints, remember?
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
   #..          (lambda (first : :* args)
   #..            (.__getitem__
   #..              `(,first
   #..                (operator..mul ,first (* ,@args)))
   #..              (bool args))))
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

   #> (functools..reduce (lambda xy
   #..                     (* x y))       ;Invocation, not argument.
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


   ;; Sometimes you actually do want a name collision (or "capture"),
   ;; when the macro user should expect an implicit new local binding
   ;; (an "anaphor"). Don't qualify and don't gensym in that case.
   ;; Unquoting suppresses the recursive template quoting of tuples,
   ;; while the normal quote doesn't qualify symbols, so this combination
   ;; suppresses auto-qualification.
   #> (setattr _macro_
   #..         'XY
   #..         (lambda (: :* body)
   #..           `(lambda (,'X ,'Y)       ;,'X instead of $#X
   #..              (,@body))))
   >>> setattr(
   ...   _macro_,
   ...   'XY',
   ...   (lambda *body:
   ...     (lambda * _: _)(
   ...       'lambda',
   ...       (lambda * _: _)(
   ...         'X',
   ...         'Y'),
   ...       (lambda * _: _)(
   ...         *body))))


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


   ;;;; Compiling and Running Files

   ;; ``$ lissp`` can run a .lissp file as __main__.
   ;; You cannot import .lissp directly. Compile it to .py first.

   ;; Finds spam.lissp & eggs.lissp in the current package & compile to spam.py & eggs.py
   (os..system #"echo (print \"Hello World!\") > eggs.lissp")
   (os..system #"echo (print \"Hello from spam!\") (.update (globals) : x 42) > spam.lissp")
   (hissp.reader..transpile __package__ 'spam 'eggs)

   spam..x                                ;Side effects on both compilation and import!
   ;; Hello from spam!
   ;; 42

   spam..x                                ;42
   eggs.                                  ;Hello, World!

   ;;;; The Basic Macros

   ;; To make the REPL more usable, it comes with some basic macros already
   ;; defined. Their design has been deliberately restricted so that their
   ;; compiled output does not require the Hissp package to be installed to
   ;; work. While these may suffice for small or embedded Hissp projects,
   ;; you will probably want a more capable macro suite (such as Hebigo's)
   ;; for general use. You are not required to use the basic macros at all,
   ;; so by default, they don't work in .lissp files unqualified. They're
   ;; available qualified from hissp.basic.._macro_.

   ;;; Side Effect

   #> (print (prog1 0                     ;Sequence for side effects, eval to first.
   #..         (print 1)
   #..         (print 2)))
   >>> print(
   ...   # prog1
   ...   # hissp.basic.._macro_.let
   ...   (lambda _value1_QzNo28_=(0):(
   ...     print(
   ...       (1)),
   ...     print(
   ...       (2)),
   ...     _value1_QzNo28_)[-1])())
   1
   2
   0


   #> (print (progn (print 1)             ;Sequence for side effects, eval to last.
   #..              (print 2)
   #..              3))
   >>> print(
   ...   # progn
   ...   (lambda :(
   ...     print(
   ...       (1)),
   ...     print(
   ...       (2)),
   ...     (3))[-1])())
   1
   2
   3


   #> (prog1                              ;Sequence for side effects, eval to first.
   #..  (progn (print 1)                  ;Sequence for side effects, eval to last.
   #..         3)
   #..  (print 2))
   >>> # prog1
   ... # hissp.basic.._macro_.let
   ... (lambda _value1_QzNo35_=# progn
   ... (lambda :(
   ...   print(
   ...     (1)),
   ...   (3))[-1])():(
   ...   print(
   ...     (2)),
   ...   _value1_QzNo35_)[-1])()
   1
   2
   3


   ;;; Definition

   #> (deftype Point2D (tuple)
   #..  __doc__ "Simple ordered pair."
   #..  __new__ (lambda (cls x y)
   #..            (.__new__ tuple cls `(,x ,y)))
   #..  __repr__ (lambda (self)
   #..             (.format "Point2D({!r}, {!r})" : :* self)))
   >>> # deftype
   ... # hissp.basic.._macro_.define
   ... __import__('builtins').globals().update(
   ...   Point2D=__import__('builtins').type(
   ...             'Point2D',
   ...             (lambda * _: _)(
   ...               tuple),
   ...             __import__('builtins').dict(
   ...               __doc__=('Simple ordered pair.'),
   ...               __new__=(lambda cls,x,y:
   ...                         tuple.__new__(
   ...                           cls,
   ...                           (lambda * _: _)(
   ...                             x,
   ...                             y))),
   ...               __repr__=(lambda self:
   ...                          ('Point2D({!r}, {!r})').format(
   ...                            *self)))))

   #> (Point2D 1 2)
   >>> Point2D(
   ...   (1),
   ...   (2))
   Point2D(1, 2)


   ;; Define a function in the _macro_ namespace.
   ;; Creates the _macro_ namespace if absent.
   ;; Can also have a docstring.
   #> (defmacro p123 (sep)
   #..  "Prints 1 2 3 with the given separator"
   #..  `(print 1 2 3 : sep ,sep))
   >>> # defmacro
   ... # hissp.basic.._macro_.let
   ... (lambda _fn_QzNo7_=(lambda sep:(
   ...   ('Prints 1 2 3 with the given separator'),
   ...   (lambda * _: _)(
   ...     'builtins..print',
   ...     (1),
   ...     (2),
   ...     (3),
   ...     ':',
   ...     '__main__..sep',
   ...     sep))[-1]):(
   ...   __import__('builtins').setattr(
   ...     _fn_QzNo7_,
   ...     '__doc__',
   ...     ('Prints 1 2 3 with the given separator')),
   ...   __import__('builtins').setattr(
   ...     _fn_QzNo7_,
   ...     '__qualname__',
   ...     ('.').join(
   ...       ('_macro_',
   ...        'p123',))),
   ...   __import__('builtins').setattr(
   ...     __import__('operator').getitem(
   ...       __import__('builtins').globals(),
   ...       '_macro_'),
   ...     'p123',
   ...     _fn_QzNo7_))[-1])()


   (help _macro_.p123)

   #> (define SPAM "tomato")              ;We've seen this one already.
   >>> # define
   ... __import__('builtins').globals().update(
   ...   SPAM=('tomato'))

   #> SPAM
   >>> SPAM
   'tomato'


   #> (let (x "a"                         ;Create locals.
   #..      y "b")                        ;Any number of pairs.
   #..  (print x y)
   #..  (let (x "x"
   #..        y (+ x x))                  ;Not in scope until body.
   #..    (print x y))                    ;Outer variables shadowed.
   #..  (print x y))                      ;Inner went out of scope.
   >>> # let
   ... (lambda x=('a'),y=('b'):(
   ...   print(
   ...     x,
   ...     y),
   ...   # let
   ...   (lambda x=('x'),y=# QzPLUS_
   ...   __import__('operator').add(
   ...     x,
   ...     # __main__..QzMaybe_.QzPLUS_
   ...     x):
   ...     print(
   ...       x,
   ...       y))(),
   ...   print(
   ...     x,
   ...     y))[-1])()
   a b
   x aa
   a b


   ;;; Configuration

   #> (attach (types..SimpleNamespace) + : a 1  b "Hi")
   >>> # attach
   ... # hissp.basic.._macro_.let
   ... (lambda _target_QzNo16_=__import__('types').SimpleNamespace():(
   ...   __import__('builtins').setattr(
   ...     _target_QzNo16_,
   ...     'QzPLUS_',
   ...     QzPLUS_),
   ...   __import__('builtins').setattr(
   ...     _target_QzNo16_,
   ...     'a',
   ...     (1)),
   ...   __import__('builtins').setattr(
   ...     _target_QzNo16_,
   ...     'b',
   ...     ('Hi')),
   ...   _target_QzNo16_)[-1])()
   namespace(QzPLUS_=<built-in function add>, a=1, b='Hi')

   #> (doto []
   #..  (.extend "bar")
   #..  (.sort)
   #..  (.append "foo"))
   >>> # doto
   ... (lambda _self_QzNo20_=[]:(
   ...   _self_QzNo20_.extend(
   ...     ('bar')),
   ...   _self_QzNo20_.sort(),
   ...   _self_QzNo20_.append(
   ...     ('foo')),
   ...   _self_QzNo20_)[-1])()
   ['a', 'b', 'r', 'foo']


   ;;; Threading

   #> (-> "world!"                        ;Thread-first
   #..    (.title)
   #..    (->> (print "Hello")))          ;Thread-last
   >>> # Qz_QzGT_
   ... # hissp.basic..QzMaybe_.Qz_QzGT_
   ... # hissp.basic..QzMaybe_.Qz_QzGT_
   ... # Qz_QzGT_QzGT_
   ... # hissp.basic..QzMaybe_.Qz_QzGT_QzGT_
   ... print(
   ...   ('Hello'),
   ...   ('world!').title())
   Hello World!

   (help _macro_.->)
   (help _macro_.->>)

   ;;; Control Flow

   ;; Hissp has no control flow, but you can build them with macros.

   #> (any-for i (range 1 11)             ;Imperative loop with break.
   #..  (print i : end " ")
   #..  (operator..not_ (operator..mod i 7)))
   >>> # anyQz_for
   ... __import__('builtins').any(
   ...   __import__('builtins').map(
   ...     (lambda i:(
   ...       print(
   ...         i,
   ...         end=(' ')),
   ...       __import__('operator').not_(
   ...         __import__('operator').mod(
   ...           i,
   ...           (7))))[-1]),
   ...     range(
   ...       (1),
   ...       (11))))
   1 2 3 4 5 6 7 True

   ;; 1 2 3 4 5 6 7 True

   (if-else (eq (input "? ") 't)          ;ternary conditional
     (print "Yes")
     (print "No"))

   (let (x (float (input "? ")))
     ;; Multi-way branch.
     (cond (lt x 0) (print "Negative")
           (eq x 0) (print "Zero")
           (gt x 0) (print "Positive")
           :else (print "Not a number"))
     (when (eq x 0)                       ;Conditional with side-effects & no alternative.
       (print "In when")
       (print "was zero"))
     (unless (eq x 0)
       (print "In unless")
       (print "wasn't zero")))

   ;; Shortcutting logical and.
   #> (&& True True False)
   >>> # QzET_QzET_
   ... # hissp.basic.._macro_.let
   ... (lambda _G_QzNo33_=True:
   ...   # hissp.basic.._macro_.ifQz_else
   ...   (lambda test,*thenQz_else:
   ...     __import__('operator').getitem(
   ...       thenQz_else,
   ...       __import__('operator').not_(
   ...         test))())(
   ...     _G_QzNo33_,
   ...     (lambda :
   ...       # hissp.basic..QzMaybe_.QzET_QzET_
   ...       # hissp.basic.._macro_.let
   ...       (lambda _G_QzNo33_=True:
   ...         # hissp.basic.._macro_.ifQz_else
   ...         (lambda test,*thenQz_else:
   ...           __import__('operator').getitem(
   ...             thenQz_else,
   ...             __import__('operator').not_(
   ...               test))())(
   ...           _G_QzNo33_,
   ...           (lambda :
   ...             # hissp.basic..QzMaybe_.QzET_QzET_
   ...             False),
   ...           (lambda :_G_QzNo33_)))()),
   ...     (lambda :_G_QzNo33_)))()
   False

   #> (&& False (print "oops"))
   >>> # QzET_QzET_
   ... # hissp.basic.._macro_.let
   ... (lambda _G_QzNo33_=False:
   ...   # hissp.basic.._macro_.ifQz_else
   ...   (lambda test,*thenQz_else:
   ...     __import__('operator').getitem(
   ...       thenQz_else,
   ...       __import__('operator').not_(
   ...         test))())(
   ...     _G_QzNo33_,
   ...     (lambda :
   ...       # hissp.basic..QzMaybe_.QzET_QzET_
   ...       print(
   ...         ('oops'))),
   ...     (lambda :_G_QzNo33_)))()
   False

   #> (&& True 42)
   >>> # QzET_QzET_
   ... # hissp.basic.._macro_.let
   ... (lambda _G_QzNo26_=True:
   ...   # hissp.basic.._macro_.ifQz_else
   ...   (lambda test,*thenQz_else:
   ...     __import__('operator').getitem(
   ...       thenQz_else,
   ...       __import__('operator').not_(
   ...         test))())(
   ...     _G_QzNo26_,
   ...     (lambda :
   ...       # hissp.basic..QzMaybe_.QzET_QzET_
   ...       (42)),
   ...     (lambda :_G_QzNo26_)))()
   42


   ;; Shortcutting logical or.
   #> (|| True (print "oops"))
   >>> # QzBAR_QzBAR_
   ... # hissp.basic.._macro_.let
   ... (lambda _first_QzNo34_=True:
   ...   # hissp.basic.._macro_.ifQz_else
   ...   (lambda test,*thenQz_else:
   ...     __import__('operator').getitem(
   ...       thenQz_else,
   ...       __import__('operator').not_(
   ...         test))())(
   ...     _first_QzNo34_,
   ...     (lambda :_first_QzNo34_),
   ...     (lambda :
   ...       # hissp.basic..QzMaybe_.QzBAR_QzBAR_
   ...       print(
   ...         ('oops')))))()
   True

   #> (|| 42 False)
   >>> # QzBAR_QzBAR_
   ... # hissp.basic.._macro_.let
   ... (lambda _first_QzNo27_=(42):
   ...   # hissp.basic.._macro_.ifQz_else
   ...   (lambda test,*thenQz_else:
   ...     __import__('operator').getitem(
   ...       thenQz_else,
   ...       __import__('operator').not_(
   ...         test))())(
   ...     _first_QzNo27_,
   ...     (lambda :_first_QzNo27_),
   ...     (lambda :
   ...       # hissp.basic..QzMaybe_.QzBAR_QzBAR_
   ...       False)))()
   42


   ;;; The Basic Prelude

   ;; An inline convenience micro-prelude for Hissp.
   ;; Imports partial and reduce; star imports from operator and
   ;; itertools; defines the en- group utilities; and imports a copy of
   ;; hissp.basic.._macro_ (if available). Usually the first form in a file,
   ;; because it overwrites _macro_, but completely optional.
   ;; Implied for $ lissp -c commands.
   #> (prelude)                           ;/!\ Or (hissp.basic.._macro_.prelude)
   >>> # prelude
   ... __import__('builtins').exec(
   ...   ('from functools import partial,reduce\n'
   ...    'from itertools import *;from operator import *\n'
   ...    'def entuple(*xs):return xs\n'
   ...    'def enlist(*xs):return[*xs]\n'
   ...    'def enset(*xs):return{*xs}\n'
   ...    "def enfrost(*xs):return __import__('builtins').frozenset(xs)\n"
   ...    'def endict(*kvs):return{k:i.__next__()for i in[kvs.__iter__()]for k in i}\n'
   ...    "def enstr(*xs):return''.join(''.__class__(x)for x in xs)\n"
   ...    'def engarde(xs,f,*a,**kw):\n'
   ...    ' try:return f(*a,**kw)\n'
   ...    ' except xs as e:return e\n'
   ...    "_macro_=__import__('types').SimpleNamespace()\n"
   ...    "try:exec('from hissp.basic._macro_ import *',vars(_macro_))\n"
   ...    'except ModuleNotFoundError:pass'),
   ...   __import__('builtins').globals())


   ;;; Obligatory Factorial III

   ;; With the prelude, we can define a nicer-looking version.
   #> (define factorial-III
   #..  (lambda i
   #..    (if-else (le i 1)
   #..      1
   #..      (mul i (factorial-III (sub i 1))))))
   >>> # define
   ... __import__('builtins').globals().update(
   ...   factorialQz_III=(lambda i:
   ...                     # ifQz_else
   ...                     (lambda test,*thenQz_else:
   ...                       __import__('operator').getitem(
   ...                         thenQz_else,
   ...                         __import__('operator').not_(
   ...                           test))())(
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


   ;;;; The En- Group

   ;; These are small utility functions defined by the basic prelude.
   ;; Most of them put their arguments into a collection, hence the en-.
   #> (entuple 1 2 3)
   >>> entuple(
   ...   (1),
   ...   (2),
   ...   (3))
   (1, 2, 3)

   #> (enlist 1 2 3)
   >>> enlist(
   ...   (1),
   ...   (2),
   ...   (3))
   [1, 2, 3]

   #> (enset 1 2 3)
   >>> enset(
   ...   (1),
   ...   (2),
   ...   (3))
   {1, 2, 3}


   ;; From [en]- [fro]zen [s]e[t], because "enfrozenset" is too long.
   #> (enfrost 1 2 3)
   >>> enfrost(
   ...   (1),
   ...   (2),
   ...   (3))
   frozenset({1, 2, 3})


   ;; Unlike (dict) with kwargs, keys need not be identifiers.
   #> (endict 1 2  3 4)                   ;Note the implied pairs.
   >>> endict(
   ...   (1),
   ...   (2),
   ...   (3),
   ...   (4))
   {1: 2, 3: 4}


   ;; The need for endict is apparent, considering alternatives.
   #> (dict (enlist (entuple 1 2) (entuple 3 4)))
   >>> dict(
   ...   enlist(
   ...     entuple(
   ...       (1),
   ...       (2)),
   ...     entuple(
   ...       (3),
   ...       (4))))
   {1: 2, 3: 4}


   ;; Converts to str and joins. Usually .format is good enough, but
   ;; sometimes you need interpolations inline, like f-strings. Don't forget
   ;; the format builtin can apply formatting specs.
   #> (enstr "<p>"(format 40 ".2f")" + "(add 1 1)"</p>")
   >>> enstr(
   ...   ('<p>'),
   ...   format(
   ...     (40),
   ...     ('.2f')),
   ...   (' + '),
   ...   add(
   ...     (1),
   ...     (1)),
   ...   ('</p>'))
   '<p>40.00 + 2</p>'


   ;; OK, so this one's not a collection. Guards against the targeted exception classes.
   #> (engarde (entuple FloatingPointError ZeroDivisionError)          ;two targets
   #..         truediv 6 0)                                            ;returned exception
   >>> engarde(
   ...   entuple(
   ...     FloatingPointError,
   ...     ZeroDivisionError),
   ...   truediv,
   ...   (6),
   ...   (0))
   ZeroDivisionError('division by zero')

   #> (engarde ArithmeticError truediv 6 0)                            ;superclass target
   >>> engarde(
   ...   ArithmeticError,
   ...   truediv,
   ...   (6),
   ...   (0))
   ZeroDivisionError('division by zero')

   #> (engarde ArithmeticError truediv 6 2)                            ;returned answer
   >>> engarde(
   ...   ArithmeticError,
   ...   truediv,
   ...   (6),
   ...   (2))
   3.0


   ;;;; Advanced Reader Macros

   ;;; The Discard Macro

   #> _#"The discard reader macro _# omits the next form.
   #..It's a way to comment out code structurally.
   #..It can also make block comments like this one.
   #..This would show up when compiled if not for _#.
   #.."
   >>>

   #> (print 1 _#(I'm not here!) 2 3)
   >>> print(
   ...   (1),
   ...   (2),
   ...   (3))
   1 2 3


   ;;; Qualified Reader Macros

   ;; Invoke any qualified callable on the next parsed object at read time.
   #> builtins..hex#3840                  ;Qualified name ending in # is a reader macro.
   >>> 0xf00
   3840

   #> builtins..ord#Q                     ;Reader macros make literal notation extensible.
   >>> (81)
   81

   #> math..exp#1                         ;e^1. Or to whatever number. At read time.
   >>> (2.718281828459045)
   2.718281828459045


   ;; Reader macros compose like functions.
   #> 'hissp.munger..demunge#Qz_QzGT_QzGT_   ;Note the starting '.
   >>> '->>'
   '->>'

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


   _#"Except for strings and tuples, objects in Hissp should evaluate to
   themselves. But when the object lacks a Python literal notation,
   the compiler is in a pickle!
   "
   #> builtins..float#inf
   >>> __import__('pickle').loads(  # inf
   ...     b'Finf\n.'
   ... )
   inf


   ;;; Inject

   _#"The 'inject' reader macro compiles and evaluates the next form at
   read time and injects the resulting object directly into the Hissp
   tree, like a qualified reader macro does.
   "

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
   ...     b'cfractions\nFraction\n(V1/2\ntR.'
   ... )
   Fraction(1, 2)


   _#"Recall that Hissp-level string objects can represent
   arbitrary Python code. It's usually used for identifiers,
   but can be anything, even complex formulas.
   "
   #> (lambda abc
   #..  ;; Hissp may not have operators, but Python does.
   #..  .#"(-b + (b**2 - 4*a*c)**0.5)/(2*a)")
   >>> (lambda a,b,c:(-b + (b**2 - 4*a*c)**0.5)/(2*a))
   <function <lambda> at 0x...>


   _#"Remember the raw string and hash string reader syntax makes Python-
   level strings, via a Hissp-level string containing a Python string
   literal. It is NOT for creating a Hissp-level string, which would
   normally contain Python code. Use inject for that.
   "
   #> '"a string"                         ;Python code for a string. In a string.
   >>> "('a string')"
   "('a string')"

   ;; Injection of an object to the Hissp level. In this case, a string object.
   #> '.#"a string"                       ;Quoting renders a Hissp-level string as data.
   >>> 'a string'
   'a string'


   _#"Objects without literals don't pickle until the compiler has to emit
   them as Python code. That may never happen if another macro gets there first.
   "
   #> 'builtins..repr#(re..compile#.#"[1-9][0-9]*" builtins..float#inf)
   >>> "(re.compile('[1-9][0-9]*'), inf)"
   "(re.compile('[1-9][0-9]*'), inf)"

   #> re..compile#.#"[1-9][0-9]*"
   >>> __import__('pickle').loads(  # re.compile('[1-9][0-9]*')
   ...     b'cre\n_compile\n(V[1-9][0-9]*\nI32\ntR.'
   ... )
   re.compile('[1-9][0-9]*')


   ;; Statement injections work at the top level only.
   #> .#"from operator import *"          ;All your operator are belong to us.
   >>> from operator import *


   ;;;; The Basic Reader Macros

   #> b#"bytes"                           ;Bytes reader macro.
   >>> b'bytes'
   b'bytes'

   #> b'bytes'                            ;NameError about 'bQzAPOS_bytesQzAPOS_'
   >>> bQzAPOS_bytesQzAPOS_
   Traceback (most recent call last):
     File "<console>", line 1, in <module>
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
   Help on function <lambda> in module hissp.basic:
   <BLANKLINE>
   <lambda> lambda raw
       ``b#`` bytes literal reader macro
   <BLANKLINE>


   ;; Not technically a basic reader macro, but a basic macro for defining them.
   ;; Alias makes a new reader macro to abbreviate a qualifier.
   ;; This is an alternative to adding an import to _macro_ or globals.
   #> (hissp.basic.._macro_.alias M: hissp.basic.._macro_)
   >>> # hissp.basic.._macro_.alias
   ... # hissp.basic.._macro_.defmacro
   ... # hissp.basic.._macro_.let
   ... (lambda _fn_QzNo7_=(lambda _prime_QzNo34_,_reader_QzNo34_=None,*_args_QzNo34_:(
   ...   "('Aliases hissp.basic.._macro_ as MQzCOLON_#')",
   ...   # hissp.basic.._macro_.ifQz_else
   ...   (lambda test,*thenQz_else:
   ...     __import__('operator').getitem(
   ...       thenQz_else,
   ...       __import__('operator').not_(
   ...         test))())(
   ...     _reader_QzNo34_,
   ...     (lambda :
   ...       __import__('builtins').getattr(
   ...         __import__('hissp.basic',fromlist='?')._macro_,
   ...         ('{}{}').format(
   ...           _reader_QzNo34_,
   ...           # hissp.basic.._macro_.ifQz_else
   ...           (lambda test,*thenQz_else:
   ...             __import__('operator').getitem(
   ...               thenQz_else,
   ...               __import__('operator').not_(
   ...                 test))())(
   ...             __import__('operator').contains(
   ...               'hissp.basic.._macro_',
   ...               '_macro_'),
   ...             (lambda :'QzHASH_'),
   ...             (lambda :('')))))(
   ...         _prime_QzNo34_,
   ...         *_args_QzNo34_)),
   ...     (lambda :
   ...       ('{}.{}').format(
   ...         'hissp.basic.._macro_',
   ...         _prime_QzNo34_))))[-1]):(
   ...   __import__('builtins').setattr(
   ...     _fn_QzNo7_,
   ...     '__qualname__',
   ...     ('.').join(
   ...       ('_macro_',
   ...        'MQzCOLON_QzHASH_',))),
   ...   __import__('builtins').setattr(
   ...     __import__('operator').getitem(
   ...       __import__('builtins').globals(),
   ...       '_macro_'),
   ...     'MQzCOLON_QzHASH_',
   ...     _fn_QzNo7_))[-1])()

   #> 'M:#alias                           ;Now short for 'hissp.basic.._macro_.alias'.
   >>> 'hissp.basic.._macro_.alias'
   'hissp.basic.._macro_.alias'

   #> M:#b\#                              ;b# macro callable
   >>> __import__('hissp.basic',fromlist='?')._macro_.bQzHASH_
   <function _macro_.bQzHASH_ at ...>

   #> (M:#b\# "b# macro at compile time")
   >>> # hissp.basic.._macro_.bQzHASH_
   ... b'b# macro at compile time'
   b'b# macro at compile time'

   #> hissp.basic.._macro_.b\##"Fully qualified b# macro at read time."
   >>> b'Fully qualified b# macro at read time.'
   b'Fully qualified b# macro at read time.'


   ;; Comment string.
   #> <<#;Don't worry about the "quotes".
   >>> 'Don\'t worry about the "quotes".'
   'Don\'t worry about the "quotes".'


   ;;; Aside: Extra (!), the Final Builtin Reader Macro

   _#"Reader macros take one primary argument, but additional arguments
   can be passed in with the extra macro !. A reader macro consumes the
   next parsed object, and if it's an Extra, consumes one again. Thus,
   extras must be written between the # and primary argument, but because
   they're often optional refinements, which are easier to define as
   trailing optional parameters in in Python functions, they get passed
   in after the primary argument.
   "
   #> (setattr _macro_ 'L\# enlist)
   >>> setattr(
   ...   _macro_,
   ...   'LQzHASH_',
   ...   enlist)


   #> L#primary
   >>> ['primary']
   ['primary']

   #> L#!1 primary
   >>> ['primary', 1]
   ['primary', 1]


   ;; Alias can work on reader macros too!
   #> M:#!b"Read-time b# via alias."      ;Extra arg for alias with (!)
   >>> b'Read-time b# via alias.'
   b'Read-time b# via alias.'


   #> L# !1 !2 primary                    ;Note the order!
   >>> ['primary', 1, 2]
   ['primary', 1, 2]

   #> .#(enlist "primary" 1 2)            ;Inject. Note the order.
   >>> ['primary', 1, 2]
   ['primary', 1, 2]


   #> !1                                  ;! is for a single Extra.
   >>> __import__('pickle').loads(  # Extra([1])
   ...     b'ccopyreg\n_reconstructor\n(chissp.reader\nExtra\ncbuiltins\ntuple\n(I1\nttR.'
   ... )
   Extra([1])

   #> hissp.reader..Extra#(: :? 0 :* (1 2 3)) ; but Extra can have multiple elements.
   >>> __import__('pickle').loads(  # Extra([':', ':?', 0, ':*', (1, 2, 3)])
   ...     b'ccopyreg\n_reconstructor\n(chissp.reader\nExtra\ncbuiltins\ntuple\n(V:\nV:?\nI0\nV:*\n(I1\nI2\nI3\ntttR.'
   ... )
   Extra([':', ':?', 0, ':*', (1, 2, 3)])


   #> L#!: !:* !(0 1 2) !:? !3 primary    ;Unpacking works like calls.
   >>> ['primary', 0, 1, 2, 3]
   ['primary', 0, 1, 2, 3]

   #> L#!0 !: !:* !(1 2 3)primary         ;Same effect.
   >>> ['primary', 0, 1, 2, 3]
   ['primary', 0, 1, 2, 3]

   #> L#hissp.reader..Extra#(0 : :* (1 2 3))primary ;Same effect.
   >>> ['primary', 0, 1, 2, 3]
   ['primary', 0, 1, 2, 3]


   #> (setattr _macro_ 'X\# hissp.reader..Extra)
   >>> setattr(
   ...   _macro_,
   ...   'XQzHASH_',
   ...   __import__('hissp.reader',fromlist='?').Extra)


   #> L# !0 X#(1 2) !3 primary            ;Same effect.
   >>> ['primary', 0, 1, 2, 3]
   ['primary', 0, 1, 2, 3]

   #> L#X#(0 : :* (1 2 3))primary         ;Same effect.
   >>> ['primary', 0, 1, 2, 3]
   ['primary', 0, 1, 2, 3]


   ;; Kwargs also work like calls.
   #> builtins..dict#()
   >>> {}
   {}

   #> builtins..dict#!: !spam !1  !foo !2  !:** !.#(dict : eggs 3  bar 4)()
   >>> {'spam': 1, 'foo': 2, 'eggs': 3, 'bar': 4}
   {'spam': 1, 'foo': 2, 'eggs': 3, 'bar': 4}

   #> builtins..dict#X#(: spam 1  foo 2  :** .#(dict : eggs 3  bar 4))()
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


   ;;; Joined Comment String

   #> <<#!;C:\bin
   #..   !;C:\Users\ME\Documents
   #..   !;C:\Users\ME\Pictures
   #..";"
   >>> 'C:\\bin;C:\\Users\\ME\\Documents;C:\\Users\\ME\\Pictures'
   'C:\\bin;C:\\Users\\ME\\Documents;C:\\Users\\ME\\Pictures'


   ;; Embed other languages without escapes.
   #> (exec
   #..  <<#
   #..  !;for i in 'abc':
   #..  !;    for j in 'xyz':
   #..  !;        print(i+j, end=" ")
   #..  !;print('.')
   #..  !;
   #..  #"\n")
   >>> exec(
   ...   ("for i in 'abc':\n"
   ...    "    for j in 'xyz':\n"
   ...    '        print(i+j, end=" ")\n'
   ...    "print('.')\n"))
   ax ay az bx by bz cx cy cz .


   ;;;; Collections

   ;;; Templates and Tuples

   #> '(1 2 3)                            ;tuple
   >>> ((1),
   ...  (2),
   ...  (3),)
   (1, 2, 3)

   #> `(,(pow 42 0) ,(+ 1 1) 3)           ;Interpolate with templates.
   >>> (lambda * _: _)(
   ...   pow(
   ...     (42),
   ...     (0)),
   ...   QzPLUS_(
   ...     (1),
   ...     (1)),
   ...   (3))
   (1, 2, 3)

   #> `("a" 'b c ,'d ,"e")                ;These can be tricky. Careful.
   >>> (lambda * _: _)(
   ...   "('a')",
   ...   (lambda * _: _)(
   ...     'quote',
   ...     '__main__..b'),
   ...   '__main__..c',
   ...   'd',
   ...   ('e'))
   ("('a')", ('quote', '__main__..b'), '__main__..c', 'd', 'e')

   #> '(1 "a")                            ;Recursive quoting.
   >>> ((1),
   ...  "('a')",)
   (1, "('a')")

   #> '(1 .#"a")                          ;Injected Hissp-level string.
   >>> ((1),
   ...  'a',)
   (1, 'a')

   #> `(1 ,"a")                           ;Interpolated string.
   >>> (lambda * _: _)(
   ...   (1),
   ...   ('a'))
   (1, 'a')


   ;; Helper functions may be easier than templates for data.
   #> (entuple 0 "a" 'b :c)
   >>> entuple(
   ...   (0),
   ...   ('a'),
   ...   'b',
   ...   ':c')
   (0, 'a', 'b', ':c')


   ;;; Other Collection Types

   #> (list `(1 ,(+ 1 1) 3))
   >>> list(
   ...   (lambda * _: _)(
   ...     (1),
   ...     QzPLUS_(
   ...       (1),
   ...       (1)),
   ...     (3)))
   [1, 2, 3]

   #> (set '(1 2 3))
   >>> set(
   ...   ((1),
   ...    (2),
   ...    (3),))
   {1, 2, 3}


   #> (bytes '(98 121 116 101 115))
   >>> bytes(
   ...   ((98),
   ...    (121),
   ...    (116),
   ...    (101),
   ...    (115),))
   b'bytes'

   #> (bytes.fromhex "6279746573")
   >>> bytes.fromhex(
   ...   ('6279746573'))
   b'bytes'

   ;; Read-time equivalents.
   #> builtins..bytes.fromhex#.#"6279746573"
   >>> b'bytes'
   b'bytes'

   #> builtins..bytes#(98 121 116 101 115)
   >>> b'bytes'
   b'bytes'

   #> .#"b'bytes'"                        ;bytes literal Python injection
   >>> b'bytes'
   b'bytes'


   #> (dict : + 0  a 1  b 2)              ;Symbol keys are easy. The common case.
   >>> dict(
   ...   QzPLUS_=(0),
   ...   a=(1),
   ...   b=(2))
   {'QzPLUS_': 0, 'a': 1, 'b': 2}

   #> (.__getitem__ _ '+)
   >>> _.__getitem__(
   ...   'QzPLUS_')
   0

   #> (dict (zip '(1 2 3) "abc"))         ;Non-symbol keys are possible.
   >>> dict(
   ...   zip(
   ...     ((1),
   ...      (2),
   ...      (3),),
   ...     ('abc')))
   {1: 'a', 2: 'b', 3: 'c'}

   #> (dict '((a 1) (2 b)))               ;Mixed key types. Beware of quoting strings.
   >>> dict(
   ...   (('a',
   ...     (1),),
   ...    ((2),
   ...     'b',),))
   {'a': 1, 2: 'b'}

   #> (dict `((,'+ 42)
   #..        (,(+ 1 1) ,'b)))            ;Run-time interpolation with a template.
   >>> dict(
   ...   (lambda * _: _)(
   ...     (lambda * _: _)(
   ...       'QzPLUS_',
   ...       (42)),
   ...     (lambda * _: _)(
   ...       QzPLUS_(
   ...         (1),
   ...         (1)),
   ...       'b')))
   {'QzPLUS_': 42, 2: 'b'}

   #> (.__getitem__ _ '+)
   >>> _.__getitem__(
   ...   'QzPLUS_')
   42


   #> (endict 1 2  'a 'b)
   >>> endict(
   ...   (1),
   ...   (2),
   ...   'a',
   ...   'b')
   {1: 2, 'a': 'b'}


   ;;; Collection Atoms

   #> .#"[]"                              ;List from a Python injection.
   >>> []
   []

   #> .#[]                                ;You can drop the quotes sometimes.
   >>> []
   []

   #> []                                  ; And the reader macro!
   >>> []
   []


   #> [1,2,3]                             ;List/set/dict atoms are a kind of injection.
   >>> [1, 2, 3]
   [1, 2, 3]

   #> {1,2,3}                             ; They read in as a single atom, so have
   >>> {1, 2, 3}
   {1, 2, 3}

   #> {'a':1,2:b'b'}                      ; compile-time literals only--No interpolation!
   >>> {'a': 1, 2: b'b'}
   {'a': 1, 2: b'b'}

   #> [1,{2},{3:[4,5]},'six']             ;Nesting is allowed.
   >>> [1, {2}, {3: [4, 5]}, 'six']
   [1, {2}, {3: [4, 5]}, 'six']


   ;; Collection atoms are a convenience for simple cases only.
   #> .#"['1 2','3',(4,5),r'6;7\8']"
   >>> ['1 2','3',(4,5),r'6;7\8']
   ['1 2', '3', (4, 5), '6;7\\8']

   ;; After dropping quotes, these tokenize like other atoms, so you need escapes.
   #> ['1\ 2',\"3\",\(4,5\),r'6\;7\\8']   ;Not so convenient now. Simple cases only!
   >>> ['1 2', '3', (4, 5), '6;7\\8']
   ['1 2', '3', (4, 5), '6;7\\8']


   ;; Constructors or helpers also work. (And can interpolate run-time data.)
   #> (list `(,"1 2" ,"3" (4 5) ,"6;7\8"))
   >>> list(
   ...   (lambda * _: _)(
   ...     ('1 2'),
   ...     ('3'),
   ...     (lambda * _: _)(
   ...       (4),
   ...       (5)),
   ...     ('6;7\\8')))
   ['1 2', '3', (4, 5), '6;7\\8']

   #> (enlist "1 2" "3" '(4 5) "6;7\8")
   >>> enlist(
   ...   ('1 2'),
   ...   ('3'),
   ...   ((4),
   ...    (5),),
   ...   ('6;7\\8'))
   ['1 2', '3', (4, 5), '6;7\\8']


   _#"Even though they evaluate the same, there's a subtle compile-time difference
   between a collection atom and a string injection. This can matter because
   macros get all their arguments unevaluated.
   "

   #> '[1,'''2\ 3''']                     ;[1, '2 3']
   >>> [1, '2 3']
   [1, '2 3']

   #> '.#"[1,'''2 3''']"                  ;"[1,'''2 3''']"
   >>> "[1,'''2 3''']"
   "[1,'''2 3''']"


   ;; But you can still get a real collection at compile time.
   #> '.#(eval "[1,'''2 3''']")           ;[1, '2 3']
   >>> [1, '2 3']
   [1, '2 3']

   #> '.#.#"[1,'''2 3''']"                ;[1, '2 3']
   >>> [1, '2 3']
   [1, '2 3']


   #> (lambda ['a','b','c'])              ;I don't recommend this, but it works.
   >>> (lambda a,b,c:())
   <function <lambda> at 0x...>

   #> (lambda .#"['a','b','c']")          ;Oops.
   >>> (lambda [,',a,',,,',b,',,,',c,',]:())
   Traceback (most recent call last):
     ...
       (lambda [,',a,',,,',b,',,,',c,',]:())
               ^
   SyntaxError: invalid syntax

   #> (lambda .#.#"['a','b','c']")        ;Another inject fixes it.
   >>> (lambda a,b,c:())
   <function <lambda> at 0x...>


   #> '(lambda ['a','b','c'])             ;Params is a list.
   >>> ('lambda',
   ...  ['a', 'b', 'c'],)
   ('lambda', ['a', 'b', 'c'])

   #> '(lambda .#"['a','b','c']")         ;Params is a string.
   >>> ('lambda',
   ...  "['a','b','c']",)
   ('lambda', "['a','b','c']")

   #> '(lambda .#.#"['a','b','c']")       ;Params is a list.
   >>> ('lambda',
   ...  ['a', 'b', 'c'],)
   ('lambda', ['a', 'b', 'c'])


   #> (lambda "abc")                      ;Oops.
   >>> (lambda (,',a,b,c,',):())
   Traceback (most recent call last):
     ...
       (lambda (,',a,b,c,',):())
               ^
   SyntaxError: invalid syntax

   #> (lambda .#"abc")                    ;Inject fixes it.
   >>> (lambda a,b,c:())
   <function <lambda> at 0x...>


   #> '(lambda "abc")                     ;See why? Extra characters.
   >>> ('lambda',
   ...  "('abc')",)
   ('lambda', "('abc')")

   #> '(lambda .#"abc")                   ;Evaluated object.
   >>> ('lambda',
   ...  'abc',)
   ('lambda', 'abc')


   #> (lambda abc)                        ;Compare to using a symbol.
   >>> (lambda a,b,c:())
   <function <lambda> at 0x...>

   #> '(lambda abc)
   >>> ('lambda',
   ...  'abc',)
   ('lambda', 'abc')

