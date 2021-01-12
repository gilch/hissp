.. Copyright 2020, 2021 Matthew Egan Odendahl
   SPDX-License-Identifier: Apache-2.0

.. This hidden doctest adds basic macros for REPL-consistent behavior.
   #> (operator..setitem (globals) '_macro_ (types..SimpleNamespace : :** (vars hissp.basic.._macro_)))
   >>> __import__('operator').setitem(
   ...   globals(),
   ...   '_macro_',
   ...   __import__('types').SimpleNamespace(
   ...     **vars(
   ...       __import__('hissp.basic',fromlist='?')._macro_)))

.. TODO: Interactive via web repl?

Lissp Quick Start
=================

.. raw:: html

   (<a href="_sources/lissp_quickstart.rst.txt">Outputs</a> hidden for brevity.)

.. Lissp::

   ;;;; LISSP QUICK START

   "Lissp is a lightweight text language representing the Hissp data-
   structure language. The Lissp reader converts Lissp's symbolic
   expressions to Hissp's syntax trees. The Hissp compiler then translates
   Hissp to a functional subset of Python.

   This document is written like a .lissp file, demonstrating Lissp's (and
   thereby Hissp's) features with minimal exposition. Some familiarity with
   Python is assumed. Familiarity with another Lisp dialect is not assumed,
   but helpful. See the Hissp tutorial for more detailed explanations.

   To fully understand these examples, you must see their output. Install
   the Hissp version matching this document. Follow along by entering these
   examples in the REPL. It will show you the compiled Python and evaluate
   it. Try variations that occur to you.

   Some examples depend on state set by previous examples to work.
   Prerequisites for examples not in the same section are marked with
   '(!)'. Don't skip these.
   "

   ;;;; INSTALLATION

   ;; Install Hissp with
   ;; $ pip install hissp==0.2.0
   ;; Start the REPL with
   ;; $ lissp
   ;; You can quit with EOF or (exit).

   ;;;; ATOMS

   ;;; singleton

   #> None
   >>> None

   #> ...                                    ;Ellipsis
   >>> ...
   Ellipsis


   ;;; boolean

   #> False                                  ;0
   >>> False
   False

   #> True                                   ;1
   >>> True
   True


   ;;; integer

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


   ;;; floating-point

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


   ;;; complex

   #> 5j                                     ;imaginary
   >>> (5j)
   5j

   #> 4+2j                                   ;complex
   >>> ((4+2j))
   (4+2j)

   #> -1_2.3_4e-5_6-7_8.9_8e-7_6j            ;Very complex!
   >>> ((-1.234e-55-7.898e-75j))
   (-1.234e-55-7.898e-75j)


   ;;; symbols and strings

   #> object                                 ;Normal identifier.
   >>> object
   <class 'object'>

   #> object.__class__                       ;Attribute identifier with dot, as Python.
   >>> object.__class__
   <class 'type'>


   #> math.                                  ;Module literals import!
   >>> __import__('math')
   <module 'math' ...>

   #> math..tau                              ;Qualified identifier. Attribute of a module.
   >>> __import__('math').tau
   6.283185307179586

   #> collections.abc.                       ;Submodule literal. Has package name.
   >>> __import__('collections.abc',fromlist='?')
   <module 'collections.abc' from '...abc.py'>


   #> builtins..object.__class__             ;Qualified attribute identifier.
   >>> __import__('builtins').object.__class__
   <class 'type'>

   #> object.__class__.__name__              ;Attributes chain.
   >>> object.__class__.__name__
   'type'

   #> collections.abc..Sequence.__class__.__name__ ;All together now.
   >>> __import__('collections.abc',fromlist='?').Sequence.__class__.__name__
   'ABCMeta'


   #> :control-word                          ;Colon prefix. Similar to Lisp ":keywords".
   >>> ':control-word'
   ':control-word'

   #> 'symbol                                ;Apostrophe prefix. Represents identifier.
   >>> 'symbol'
   'symbol'


   #> '+                                     ;Read-time munging of invalid identifiers.
   >>> 'xPLUS_'
   'xPLUS_'

   #> 'Also-a-symbol!                        ;Alias for 'AlsoxH_axH_symbolxBANG_
   >>> 'AlsoxH_axH_symbolxBANG_'
   'AlsoxH_axH_symbolxBANG_'

   #> '𝐀                                     ;Alias for 'A (munges to unicode normal form KC)
   >>> 'A'
   'A'

   #> '->>
   >>> 'xH_xGT_xGT_'
   'xH_xGT_xGT_'

   #> :->>                                   ;These don't represent identifiers, don't munge.
   >>> ':->>'
   ':->>'


   #> 'SPAM\ \"\(\)\;EGGS                    ;These would terminate a symbol if not escaped.
   >>> 'SPAMxSPACE_x2QUOTE_xPAREN_xTHESES_xSCOLON_EGGS'
   'SPAMxSPACE_x2QUOTE_xPAREN_xTHESES_xSCOLON_EGGS'

   #> '\42                                   ;Digits can't start identifiers.
   >>> 'xDIGITxFOUR_2'
   'xDIGITxFOUR_2'

   #> '\.
   >>> 'xFULLxSTOP_'
   'xFULLxSTOP_'

   #> '\\
   >>> 'xBSLASH_'
   'xBSLASH_'

   #> '\a\b\c                                ;Escapes allowed, but not required here.
   >>> 'abc'
   'abc'

   #> 1\2                                    ;Backslashes work in other atoms.
   >>> (12)
   12

   #> N\one
   >>> None


   #> "raw string"
   >>> ('raw string')
   'raw string'

   #> 'not-string'                           ;symbol
   >>> 'notxH_stringx1QUOTE_'
   'notxH_stringx1QUOTE_'

   #> #"Say \"Cheese!\" \u263a"              ;Hash strings use Python escapes.
   >>> ('Say "Cheese!" ☺')
   'Say "Cheese!" ☺'


   #> "string
   #..with
   #..newlines
   #.."                                      ;Same as #"string\nwith\nnewlines\n".
   >>> ('string\nwith\nnewlines\n')
   'string\nwith\nnewlines\n'


   #> "one\"
   #..string\\"                              ;Tokenizer expects paired \'s, even raw.
   >>> ('one\\"\nstring\\\\')
   'one\\"\nstring\\\\'


   ;;;; CALLS

   #> (print :)                              ;Paren before function! Note the colon.
   >>> print()
   <BLANKLINE>

   #> (print : :? 1  :? 2  :? 3  sep "-")    ;Arguments pair with a parameter name. No commas!
   >>> print(
   ...   (1),
   ...   (2),
   ...   (3),
   ...   sep=('-'))
   1-2-3

   #> (print 1 2 3 : sep "-")                ;Arguments left of the : implicitly pair with :?.
   >>> print(
   ...   (1),
   ...   (2),
   ...   (3),
   ...   sep=('-'))
   1-2-3

   #> (print 1 : :* "abc"  :? 2  :** (dict : sep "-")) ;Unpacking!
   >>> print(
   ...   (1),
   ...   *('abc'),
   ...   (2),
   ...   **dict(
   ...     sep=('-')))
   1-a-b-c-2

   #> (print "Hello, World!")                ;No : is the same as putting it last.
   >>> print(
   ...   ('Hello, World!'))
   Hello, World!

   #> (print "Hello, World!" :)              ;Compare.
   >>> print(
   ...   ('Hello, World!'))
   Hello, World!


   #> (.upper "shout!")                      ;Method calls require a "self".
   >>> ('shout!').upper()
   'SHOUT!'

   #> (.float builtins. 'inf)                ;Method call syntax, though not a method.
   >>> __import__('builtins').float(
   ...   'inf')
   inf

   #> (builtins..float 'inf)                 ;Same effect, but not method syntax.
   >>> __import__('builtins').float(
   ...   'inf')
   inf


   #> (help sum)                             ;Python's online help function is still available.
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


   ;;;; LAMBDA

   ;; Lambda is one of only two special forms--looks like a call, but isn't.

   ;; Python parameter types are rather involved. Lambda does all of them.
   #> (lambda (: a :?  b :?  :/ :?           ;positional only
   #..         c :?  d :?                    ;normal
   #..         e 1  f 2                      ;default
   #..         :* args  h 4  i :?  j 1       ;star args, key word
   #..         :** kwargs)
   #..  ;; Body. (Lambdas returns empty tuple if body is empty.)
   #..  (print (globals))
   #..  (print (locals))                     ;side effects
   #..  b)                                   ;last value is returned
   >>> (lambda a,b,/,c,d,e=(1),f=(2),*args,h=(4),i,j=(1),**kwargs:(
   ...   print(
   ...     globals()),
   ...   print(
   ...     locals()),
   ...   b)[-1])
   <function <lambda> at 0x...>


   ;; Parameters left of the : are paired with placeholder (:?), parallels calls.
   #> (lambda (: :* a))                      ;Star arg must pair with star, as Python.
   >>> (lambda *a:())
   <function <lambda> at 0x...>

   #> (lambda (:* a))                        ;Kwonly! Not star arg! Final : implied.
   >>> (lambda *,a:())
   <function <lambda> at 0x...>

   #> (lambda (:* a :))                      ;Compare.
   >>> (lambda *,a:())
   <function <lambda> at 0x...>

   #> (lambda (: :* :?  a :?))
   >>> (lambda *,a:())
   <function <lambda> at 0x...>

   #> (lambda (a b : x None  y None))        ;Normal, then positional defaults.
   >>> (lambda a,b,x=None,y=None:())
   <function <lambda> at 0x...>

   #> (lambda (:* a b : x None  y None))     ;Keyword only, then keyword defaults.
   >>> (lambda *,a,b,x=None,y=None:())
   <function <lambda> at 0x...>


   #> (lambda (spam eggs) eggs)              ;Simple cases look like other Lisps, but
   >>> (lambda spam,eggs:eggs)
   <function <lambda> at 0x...>

   #> ((lambda abc                           ; parameters are not strictly required to be a tuple.
   #..   (print c b a))                      ;There are three parameters.
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


   #> (lambda (:))                           ;Explicit : is still allowed with no parameters.
   >>> (lambda :())
   <function <lambda> at 0x...>

   #> (lambda : (print "oops"))              ;Thunk resembles Python.
   >>> (lambda :
   ...   print(
   ...     ('oops')))
   <function <lambda> at 0x...>

   #> ((lambda :x1 x))                       ;Control words are strings are iterable.
   >>> (lambda x=1:x)()
   1


   ;;;; OPERATORS

   ;; Hissp is simpler than Python. No operators! Use calls instead.

   #> (operator..add 40 2)
   >>> __import__('operator').add(
   ...   (40),
   ...   (2))
   42

   #> (.__setitem__ (globals) '+ operator..add) ;(!) Assignment. Symbols munge.
   >>> globals().__setitem__(
   ...   'xPLUS_',
   ...   __import__('operator').add)

   #> (+ 40 2)                               ;No operators. This is still a function call!
   >>> xPLUS_(
   ...   (40),
   ...   (2))
   42


   ;;;; CONTROL FLOW

   ;; Hissp is simpler than Python. No control flow! Use higher-order functions instead.

   #> (any (map (lambda c (print c))         ;Loops!
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


   ((.get (dict :                         ;Branches!
                y (lambda : (print "Yes!"))
                n (lambda : (print "Canceled.")))
          (input "enter y/n> ")
          (lambda : (print "Unrecognized input."))))

   ;; Don't worry, macros make this much easier.

   ;;;; QUOTE

   ;; Quote is the only other special form. Looks like a call, but isn't.

   ;; Quotation prevents evaluation.
   ;; Treating the code itself as data is the key concept in metaprogramming.

   #> (quote (print 1 2 3 : sep "-"))        ;Just a tuple.
   >>> ('print', 1, 2, 3, ':', 'sep', "('-')")
   ('print', 1, 2, 3, ':', 'sep', "('-')")

   #> (quote identifier)                     ;Just a string.
   >>> 'identifier'
   'identifier'

   #> (quote 42)                             ;Just a number. It was before though.
   >>> (42)
   42

   #> (quote "string")                       ;Not what you expected? Eval it.
   >>> "('string')"
   "('string')"

   #> (eval (quote "string"))                ;It's a string of Python code. For a string.
   >>> eval(
   ...   "('string')")
   'string'


   #> :?                                     ;Just a string?
   >>> ':?'
   ':?'

   #> ((lambda (: a :?) a))                  ;Not that simple!
   >>> (lambda a:a)()
   Traceback (most recent call last):
     ...
   TypeError: <lambda>() missing 1 required positional argument: 'a'

   #> ((lambda (: a (quote :?)) a))          ;Just a string.
   >>> (lambda a=':?':a)()
   ':?'


   ;;;; READER MACROS

   #> 'x                                     ;Same as (quote x). Symbols are just quoted identifiers!
   >>> 'x'
   'x'

   #> '(print "Hi")                          ;Reveal the Hissp.
   >>> ('print', "('Hi')")
   ('print', "('Hi')")


   ;; Reader macros are metaprograms to abbreviate Hissp instead of representing it directly.

   ;;; template quote
   ;; (Like quasiquote, backquote, or syntax-quote from other Lisps.)

   #> `print                                 ;Automatic qualification!
   >>> 'builtins..print'
   'builtins..print'

   #> `foo                                   ;Compare.
   >>> '__main__..foo'
   '__main__..foo'


   #> `(print "Hi")                          ;Code as data. Seems to act like quote.
   >>> (lambda *xAUTO0_:xAUTO0_)(
   ...   'builtins..print',
   ...   "('Hi')")
   ('builtins..print', "('Hi')")

   #> '`(print "Hi")                         ;But it's making a program to create the data.
   >>> (('lambda', (':', ':*', 'xAUTO0_'), 'xAUTO0_'),
   ...  ':',
   ...  ':?',
   ...  ('quote', 'builtins..print'),
   ...  ':?',
   ...  ('quote', "('Hi')"))
   (('lambda', (':', ':*', 'xAUTO0_'), 'xAUTO0_'), ':', ':?', ('quote', 'builtins..print'), ':?', ('quote', "('Hi')"))

   #> `(print ,(.upper "Hi"))                ;Unquote (,) interpolates.
   >>> (lambda *xAUTO0_:xAUTO0_)(
   ...   'builtins..print',
   ...   ('Hi').upper())
   ('builtins..print', 'HI')


   #> `,'foo                                 ;Interpolations not auto-qualified!
   >>> 'foo'
   'foo'

   #> `(print ,@"abc")                       ;Splice unquote (,@) interpolates and unpacks.
   >>> (lambda *xAUTO0_:xAUTO0_)(
   ...   'builtins..print',
   ...   *('abc'))
   ('builtins..print', 'a', 'b', 'c')

   #> `(print ,@(.upper "abc"))
   >>> (lambda *xAUTO0_:xAUTO0_)(
   ...   'builtins..print',
   ...   *('abc').upper())
   ('builtins..print', 'A', 'B', 'C')

   #> `($#eggs $#spam $#bacon $#spam)        ;Generated symbols for macros.
   >>> (lambda *xAUTO0_:xAUTO0_)(
   ...   '_eggsxAUTO9_',
   ...   '_spamxAUTO9_',
   ...   '_baconxAUTO9_',
   ...   '_spamxAUTO9_')
   ('_eggsxAUTO9_', '_spamxAUTO9_', '_baconxAUTO9_', '_spamxAUTO9_')

   #> `$#spam                                ;Gensym counter prevents name collisions.
   >>> '_spamxAUTO10_'
   '_spamxAUTO10_'


   #> _#"
   #..The discard reader macro _# omits the next form.
   #..It's a way to comment out code structurally.
   #..It can also make comments like this one.
   #..This would show up when compiled if not for _#.
   #.."
   >>>

   #> (print 1 _#(I'm not here!) 2 3)
   >>> print(
   ...   (1),
   ...   (2),
   ...   (3))
   1 2 3


   ;; Invoke any importable unary callable at read time.
   #> builtins..float#inf                    ;Extensible literals!
   >>> __import__('pickle').loads(  # inf
   ...     b'Finf\n.'
   ... )
   inf


   ;; Reader macros compose. Note the quote.
   #> 'hissp.munger..demunge#xH_xGT_xGT_
   >>> '->>'
   '->>'

   #> ''x
   >>> ('quote', 'x')
   ('quote', 'x')

   #> '\'x
   >>> 'x1QUOTE_x'
   'x1QUOTE_x'


   #> (print (.upper 'textwrap..dedent##"\
   #..               These lines
   #..               Don't interrupt
   #..               the flow."))
   >>> print(
   ...   "These lines\nDon't interrupt\nthe flow.".upper())
   THESE LINES
   DON'T INTERRUPT
   THE FLOW.


   ;; The "inject" reader macro evaluates the next form
   ;; and puts the result directly in the Hissp.
   #> .#(fractions..Fraction 1 2)            ;Fraction() is multiary.
   >>> __import__('pickle').loads(  # Fraction(1, 2)
   ...     b'cfractions\nFraction\n(V1/2\ntR.'
   ... )
   Fraction(1, 2)


   ;; Use a string to inject Python into the compiled output.
   #> (lambda (a b c)
   #..  ;; Hissp may not have operators, but Python does.
   #..  .#"(-b + (b**2 - 4*a*c)**0.5)/(2*a)")
   >>> (lambda a,b,c:(-b + (b**2 - 4*a*c)**0.5)/(2*a))
   <function <lambda> at 0x...>


   ;; Statement injections work at the top level only.
   #> .#"from operator import *"             ;(!) All your operator are belong to us.
   >>> from operator import *


   ;;;; COLLECTIONS

   ;;; templates and tuples

   #> '(1 2 3)                               ;tuple
   >>> (1, 2, 3)
   (1, 2, 3)

   #> `(,(pow 42 0) ,(+ 1 1) 3)              ;Interpolate with templates.
   >>> (lambda *xAUTO0_:xAUTO0_)(
   ...   pow(
   ...     (42),
   ...     (0)),
   ...   xPLUS_(
   ...     (1),
   ...     (1)),
   ...   (3))
   (1, 2, 3)

   #> `("a" 'b c ,'d ,"e")                   ;Remember what happens when you quote strings?
   >>> (lambda *xAUTO0_:xAUTO0_)(
   ...   "('a')",
   ...   (lambda *xAUTO0_:xAUTO0_)(
   ...     'quote',
   ...     '__main__..b'),
   ...   '__main__..c',
   ...   'd',
   ...   ('e'))
   ("('a')", ('quote', '__main__..b'), '__main__..c', 'd', 'e')

   #> '(1 "a")                               ;Recursive quoting.
   >>> (1, "('a')")
   (1, "('a')")

   #> `(1 ,"a")
   >>> (lambda *xAUTO0_:xAUTO0_)(
   ...   (1),
   ...   ('a'))
   (1, 'a')


   ;; Helper functions may be easier than templates.
   #> ((lambda (: :* xs) xs) 0 "a" 'b :c)
   >>> (lambda *xs:xs)(
   ...   (0),
   ...   ('a'),
   ...   'b',
   ...   ':c')
   (0, 'a', 'b', ':c')

   #> (.__setitem__ (globals) 'entuple (lambda (: :* xs) xs))
   >>> globals().__setitem__(
   ...   'entuple',
   ...   (lambda *xs:xs))

   #> (entuple 0 "a" 'b :c)
   >>> entuple(
   ...   (0),
   ...   ('a'),
   ...   'b',
   ...   ':c')
   (0, 'a', 'b', ':c')


   ;;; other collection types

   #> (list `(1 ,(+ 1 1) 3))
   >>> list(
   ...   (lambda *xAUTO0_:xAUTO0_)(
   ...     (1),
   ...     xPLUS_(
   ...       (1),
   ...       (1)),
   ...     (3)))
   [1, 2, 3]

   #> (set '(1 2 3))
   >>> set(
   ...   (1, 2, 3))
   {1, 2, 3}


   #> (bytes '(98 121 116 101 115))
   >>> bytes(
   ...   (98, 121, 116, 101, 115))
   b'bytes'

   #> (bytes.fromhex "6279746573")
   >>> bytes.fromhex(
   ...   ('6279746573'))
   b'bytes'

   #> .#"b'bytes'"                           ;bytes literal Python injection
   >>> b'bytes'
   b'bytes'


   #> (dict : + 0  a 1  b 2)                 ;Symbol keys are easy. The common case.
   >>> dict(
   ...   xPLUS_=(0),
   ...   a=(1),
   ...   b=(2))
   {'xPLUS_': 0, 'a': 1, 'b': 2}

   #> (.__getitem__ _ '+)                    ;In the REPL, _ is the last result that wasn't None.
   >>> _.__getitem__(
   ...   'xPLUS_')
   0

   #> (dict (zip '(1 2 3) "abc"))            ;Non-symbol keys are possible.
   >>> dict(
   ...   zip(
   ...     (1, 2, 3),
   ...     ('abc')))
   {1: 'a', 2: 'b', 3: 'c'}

   #> (dict '((a 1) (2 b)))                  ;Mixed key types. Beware of strings.
   >>> dict(
   ...   (('a', 1), (2, 'b')))
   {'a': 1, 2: 'b'}

   #> (dict `((,'+ 42)
   #..        (,(+ 1 1) ,'b)))               ;Runtime interpolation with a template.
   >>> dict(
   ...   (lambda *xAUTO0_:xAUTO0_)(
   ...     (lambda *xAUTO0_:xAUTO0_)(
   ...       'xPLUS_',
   ...       (42)),
   ...     (lambda *xAUTO0_:xAUTO0_)(
   ...       xPLUS_(
   ...         (1),
   ...         (1)),
   ...       'b')))
   {'xPLUS_': 42, 2: 'b'}

   #> (.__getitem__ _ '+)
   >>> _.__getitem__(
   ...   'xPLUS_')
   42


   #> (.__setitem__ (globals)
   #..              'endict                  ;dict helper function
   #..              (lambda (: :* pairs)
   #..                ;; Injections work on any Python expression, even comprehensions!
   #..                .#"{k: next(it) for it in [iter(pairs)] for k in it}"))
   >>> globals().__setitem__(
   ...   'endict',
   ...   (lambda *pairs:{k: next(it) for it in [iter(pairs)] for k in it}))

   #> (endict 1 2  'a 'b)
   >>> endict(
   ...   (1),
   ...   (2),
   ...   'a',
   ...   'b')
   {1: 2, 'a': 'b'}


   ;;; collection atoms

   #> .#"[]"                                 ;List from a Python injection.
   >>> []
   []

   #> .#[]                                   ;As a convenience, you can drop the quotes in some cases.
   >>> []
   []

   #> []                                     ; And the reader macro!
   >>> []
   []


   #> [1,2,3]                                ;List, set, and dict atoms are a special case
   >>> [1, 2, 3]
   [1, 2, 3]

   #> {1,2,3}                                ; of Python injection. They read in as a single atom, so
   >>> {1, 2, 3}
   {1, 2, 3}

   #> {'a':1,2:b'b'}                         ; they have compile-time literals only--No interpolation!
   >>> {'a': 1, 2: b'b'}
   {'a': 1, 2: b'b'}

   #> [1,{2},{3:[4,5]},'six']                ;Nesting is allowed.
   >>> [1, {2}, {3: [4, 5]}, 'six']
   [1, {2}, {3: [4, 5]}, 'six']


   ;; Collection atoms are a convenience for simple cases only.
   #> .#"['1 2','3',(4,5),r'6;7\8']"
   >>> ['1 2','3',(4,5),r'6;7\8']
   ['1 2', '3', (4, 5), '6;7\\8']

   ;; After dropping quotes, these tokenize like other atoms, so you need escapes.
   #> ['1\ 2',\"3\",\(4,5\),r'6\;7\\8']      ;Not so convenient now. Simple cases only!
   >>> ['1 2', '3', (4, 5), '6;7\\8']
   ['1 2', '3', (4, 5), '6;7\\8']


   ;; Constructors or helpers also work. (And can interpolate runtime data.)
   #> (list `(,"1 2" ,"3" (4 5) ,"6;7\8"))
   >>> list(
   ...   (lambda *xAUTO0_:xAUTO0_)(
   ...     ('1 2'),
   ...     ('3'),
   ...     (lambda *xAUTO0_:xAUTO0_)(
   ...       (4),
   ...       (5)),
   ...     ('6;7\\8')))
   ['1 2', '3', (4, 5), '6;7\\8']


   #> (.__setitem__ (globals) 'enlist (lambda (: :* xs) (list xs))) ;helper function
   >>> globals().__setitem__(
   ...   'enlist',
   ...   (lambda *xs:
   ...     list(
   ...       xs)))

   #> (enlist "1 2" "3" '(4 5) "6;7\8")
   >>> enlist(
   ...   ('1 2'),
   ...   ('3'),
   ...   (4, 5),
   ...   ('6;7\\8'))
   ['1 2', '3', (4, 5), '6;7\\8']


   _#"Even though they evaluate the same, there's a subtle compile-time difference
   between a collection atom and a string injection. This can matter because
   macros get all their arguments unevaluated."

   #> '[1,'''2\ 3''']                        ;[1, '2 3']
   >>> [1, '2 3']
   [1, '2 3']

   #> '.#"[1,'''2 3''']"                     ;"[1,'''2 3''']"
   >>> "[1,'''2 3''']"
   "[1,'''2 3''']"


   ;; But you can still get a real collection at compile time.
   #> '.#(eval "[1,'''2 3''']")              ;[1, '2 3']
   >>> [1, '2 3']
   [1, '2 3']

   #> '.#.#"[1,'''2 3''']"                   ;[1, '2 3']
   >>> [1, '2 3']
   [1, '2 3']


   #> (lambda ['a','b','c'])                 ;I don't recommend this, but it works.
   >>> (lambda a,b,c:())
   <function <lambda> at 0x...>

   #> (lambda .#"['a','b','c']")             ;Oops. Compare.
   >>> (lambda [,',a,',,,',b,',,,',c,',]:())
   Traceback (most recent call last):
     ...
       (lambda [,',a,',,,',b,',,,',c,',]:())
               ^
   SyntaxError: invalid syntax

   #> (lambda .#.#"['a','b','c']")           ;Another inject fixes it.
   >>> (lambda a,b,c:())
   <function <lambda> at 0x...>

   #> (lambda "abc")                         ;Oops.
   >>> (lambda (,',a,b,c,',):())
   Traceback (most recent call last):
     ...
       (lambda (,',a,b,c,',):())
               ^
   SyntaxError: invalid syntax

   #> (lambda .#"abc")                       ;Inject fixes it.
   >>> (lambda a,b,c:())
   <function <lambda> at 0x...>

   #> (lambda abc)                           ;Identifiers are also a special case of injection!
   >>> (lambda a,b,c:())
   <function <lambda> at 0x...>


   ;;;; COMPILER MACROS

   _#"Macroexpansion happens at compile time, after the reader, so macros also
   work in readerless mode, or with alternative Hissp readers other than Lissp.
   Macros get all of their arguments unevaluated and the compiler
   inserts the resulting Hissp into that point in the program.
   Like special forms, macro invocations look like function calls, but aren't."

   ;; An invocation using an identifier qualified with ``_macro_`` is a macro invocation.
   #> (hissp.basic.._macro_.define SPAM "eggs") ;Note SPAM is not quoted.
   >>> # hissp.basic.._macro_.define
   ... __import__('operator').setitem(
   ...   __import__('builtins').globals(),
   ...   'SPAM',
   ...   ('eggs'))

   #> SPAM                                   ;'eggs'
   >>> SPAM
   'eggs'


   ;; See the macro expansion by calling it like a method with all arguments quoted.
   #> (.define hissp.basic.._macro_ 'SPAM '"eggs") ;Method syntax is never a macro invocation.
   >>> __import__('hissp.basic',fromlist='?')._macro_.define(
   ...   'SPAM',
   ...   "('eggs')")
   ('operator..setitem', ('builtins..globals',), ('quote', 'SPAM'), "('eggs')")


   ;; Unqualified invocations are macro invocations if the identifier is in
   ;; the current module's _macro_ namespace. The REPL includes one, but
   ;; .lissp files don't have one until you create it.
   (dir)
   (dir _macro_)
   (help _macro_.define)

   ;; Unqualified macro invocations really look like function calls, but aren't.
   #> (define EGGS "spam")
   >>> # define
   ... __import__('operator').setitem(
   ...   __import__('builtins').globals(),
   ...   'EGGS',
   ...   ('spam'))

   #> EGGS
   >>> EGGS
   'spam'


   #> (setattr _macro_
   #..         'triple
   #..         (lambda (x)
   #..           `(+ ,x (+ ,x ,x))))         ;Use a template to make Hissp.
   >>> setattr(
   ...   _macro_,
   ...   'triple',
   ...   (lambda x:
   ...     (lambda *xAUTO0_:xAUTO0_)(
   ...       '__main__..xAUTO_.xPLUS_',
   ...       x,
   ...       (lambda *xAUTO0_:xAUTO0_)(
   ...         '__main__..xAUTO_.xPLUS_',
   ...         x,
   ...         x))))

   #> (triple 4)                             ;12
   >>> # triple
   ... __import__('builtins').globals()['xPLUS_'](
   ...   (4),
   ...   __import__('builtins').globals()['xPLUS_'](
   ...     (4),
   ...     (4)))
   12


   #> (define loud-number
   #..  (lambda x
   #..    (print x)
   #..    x))
   >>> # define
   ... __import__('operator').setitem(
   ...   __import__('builtins').globals(),
   ...   'loudxH_number',
   ...   (lambda x:(
   ...     print(
   ...       x),
   ...     x)[-1]))

   #> (triple (loud-number 14))              ;Triples the *code*, not just the *value*.
   >>> # triple
   ... __import__('builtins').globals()['xPLUS_'](
   ...   loudxH_number(
   ...     (14)),
   ...   __import__('builtins').globals()['xPLUS_'](
   ...     loudxH_number(
   ...       (14)),
   ...     loudxH_number(
   ...       (14))))
   14
   14
   14
   42


   ;; Maybe the expanded code could only run it once?
   #> (setattr _macro_
   #..         'oops-triple
   #..         (lambda x
   #..           `((lambda (: x ,x)          ;Expand to lambda to make a local variable.
   #..               (+ x (+ x x))))))
   >>> setattr(
   ...   _macro_,
   ...   'oopsxH_triple',
   ...   (lambda x:
   ...     (lambda *xAUTO0_:xAUTO0_)(
   ...       (lambda *xAUTO0_:xAUTO0_)(
   ...         'lambda',
   ...         (lambda *xAUTO0_:xAUTO0_)(
   ...           ':',
   ...           '__main__..x',
   ...           x),
   ...         (lambda *xAUTO0_:xAUTO0_)(
   ...           '__main__..xAUTO_.xPLUS_',
   ...           '__main__..x',
   ...           (lambda *xAUTO0_:xAUTO0_)(
   ...             '__main__..xAUTO_.xPLUS_',
   ...             '__main__..x',
   ...             '__main__..x'))))))

   #> (oops-triple 14)                       ;Don't forget that templates qualify symbols!
   >>> # oopsxH_triple
   ... (lambda __main__..x=(14):
   ...   __import__('builtins').globals()['xPLUS_'](
   ...     __import__('builtins').globals()['x'],
   ...     __import__('builtins').globals()['xPLUS_'](
   ...       __import__('builtins').globals()['x'],
   ...       __import__('builtins').globals()['x'])))()
   Traceback (most recent call last):
     ...
       (lambda __main__..x=(14):
                       ^
   SyntaxError: invalid syntax


   ;; If you didn't want it qualified, that's a sign you should use a gensym instead:
   #> (setattr _macro_
   #..         'once-triple
   #..         (lambda x
   #..           `((lambda (: $#x ,x)
   #..               (+ $#x (+ $#x $#x))))))
   >>> setattr(
   ...   _macro_,
   ...   'oncexH_triple',
   ...   (lambda x:
   ...     (lambda *xAUTO0_:xAUTO0_)(
   ...       (lambda *xAUTO0_:xAUTO0_)(
   ...         'lambda',
   ...         (lambda *xAUTO0_:xAUTO0_)(
   ...           ':',
   ...           '_xxAUTO22_',
   ...           x),
   ...         (lambda *xAUTO0_:xAUTO0_)(
   ...           '__main__..xAUTO_.xPLUS_',
   ...           '_xxAUTO22_',
   ...           (lambda *xAUTO0_:xAUTO0_)(
   ...             '__main__..xAUTO_.xPLUS_',
   ...             '_xxAUTO22_',
   ...             '_xxAUTO22_'))))))

   #> (once-triple (loud-number 14))
   >>> # oncexH_triple
   ... (lambda _xxAUTO22_=loudxH_number(
   ...   (14)):
   ...   __import__('builtins').globals()['xPLUS_'](
   ...     _xxAUTO22_,
   ...     __import__('builtins').globals()['xPLUS_'](
   ...       _xxAUTO22_,
   ...       _xxAUTO22_)))()
   14
   42


   ;; Sometimes you really want a name captured, so don't qualify and don't generate a new symbol:
   #> (setattr _macro_
   #..         'fnx
   #..         (lambda (: :* body)
   #..           `(lambda (,'X)              ;,'X instead of $#X
   #..              (,@body))))
   >>> setattr(
   ...   _macro_,
   ...   'fnx',
   ...   (lambda *body:
   ...     (lambda *xAUTO0_:xAUTO0_)(
   ...       'lambda',
   ...       (lambda *xAUTO0_:xAUTO0_)(
   ...         'X'),
   ...       (lambda *xAUTO0_:xAUTO0_)(
   ...         *body))))

   #> (list (map (fnx mul X X) (range 6)))   ;Shorter lambda! Don't nest them.
   >>> list(
   ...   map(
   ...     # fnx
   ...     (lambda X:
   ...       mul(
   ...         X,
   ...         X)),
   ...     range(
   ...       (6))))
   [0, 1, 4, 9, 16, 25]


   ;; Recursive macro. (Multiary +)
   #> (setattr _macro_
   #..         '+
   #..          (lambda (first : :* args)
   #..            (.__getitem__
   #..              `(,first (add ,first (+ ,@args)))
   #..              (bool args))))
   >>> setattr(
   ...   _macro_,
   ...   'xPLUS_',
   ...   (lambda first,*args:
   ...     (lambda *xAUTO0_:xAUTO0_)(
   ...       first,
   ...       (lambda *xAUTO0_:xAUTO0_)(
   ...         '__main__..xAUTO_.add',
   ...         first,
   ...         (lambda *xAUTO0_:xAUTO0_)(
   ...           '__main__..xAUTO_.xPLUS_',
   ...           *args))).__getitem__(
   ...       bool(
   ...         args))))

   #> (+ 1 2 3 4)
   >>> # xPLUS_
   ... __import__('builtins').globals()['add'](
   ...   (1),
   ...   # __main__..xAUTO_.xPLUS_
   ...   __import__('builtins').globals()['add'](
   ...     (2),
   ...     # __main__..xAUTO_.xPLUS_
   ...     __import__('builtins').globals()['add'](
   ...       (3),
   ...       # __main__..xAUTO_.xPLUS_
   ...       (4))))
   10


   #> (setattr _macro_
   #..         '*
   #..          (lambda (first : :* args)
   #..            (.__getitem__
   #..              `(,first (mul ,first (* ,@args)))
   #..              (bool args))))
   >>> setattr(
   ...   _macro_,
   ...   'xSTAR_',
   ...   (lambda first,*args:
   ...     (lambda *xAUTO0_:xAUTO0_)(
   ...       first,
   ...       (lambda *xAUTO0_:xAUTO0_)(
   ...         '__main__..xAUTO_.mul',
   ...         first,
   ...         (lambda *xAUTO0_:xAUTO0_)(
   ...           '__main__..xAUTO_.xSTAR_',
   ...           *args))).__getitem__(
   ...       bool(
   ...         args))))

   #> (* 1 2 3 4)
   >>> # xSTAR_
   ... __import__('builtins').globals()['mul'](
   ...   (1),
   ...   # __main__..xAUTO_.xSTAR_
   ...   __import__('builtins').globals()['mul'](
   ...     (2),
   ...     # __main__..xAUTO_.xSTAR_
   ...     __import__('builtins').globals()['mul'](
   ...       (3),
   ...       # __main__..xAUTO_.xSTAR_
   ...       (4))))
   24


   ;; Macros only work as invocations, not arguments!
   #> (functools..reduce * '(1 2 3 4))       ;Oops.
   >>> __import__('functools').reduce(
   ...   xSTAR_,
   ...   (1, 2, 3, 4))
   Traceback (most recent call last):
     ...
   NameError: name 'xSTAR_' is not defined

   #> (functools..reduce (lambda xy
   #..                     (* x y))          ;Invocation.
   #..                   '(1 2 3 4))
   >>> __import__('functools').reduce(
   ...   (lambda x,y:
   ...     # xSTAR_
   ...     __import__('builtins').globals()['mul'](
   ...       x,
   ...       # __main__..xAUTO_.xSTAR_
   ...       y)),
   ...   (1, 2, 3, 4))
   24


   ;; It's possible for a macro to shadow a global. They live in different namespaces.
   #> (+ 1 2 3 4)                            ;_macro_.+, not the global.
   >>> # xPLUS_
   ... __import__('builtins').globals()['add'](
   ...   (1),
   ...   # __main__..xAUTO_.xPLUS_
   ...   __import__('builtins').globals()['add'](
   ...     (2),
   ...     # __main__..xAUTO_.xPLUS_
   ...     __import__('builtins').globals()['add'](
   ...       (3),
   ...       # __main__..xAUTO_.xPLUS_
   ...       (4))))
   10

   #> (functools..reduce + '(1 2 3 4))       ;Global function, not the macro!
   >>> __import__('functools').reduce(
   ...   xPLUS_,
   ...   (1, 2, 3, 4))
   10

   (dir)                                  ;Has xPLUS_, but not xSTAR_.
   (dir _macro_)                          ;Has both.

   ;; ``$ lissp`` can run a .lissp file as __main__.
   ;; You cannot import .lissp directly. Compile it to .py first.

   ;; Finds spam.lissp & eggs.lissp in the current package and compile them to spam.py & eggs.py
   (os..system #"echo (print \"Hello World!\") > eggs.lissp")
   (os..system #"echo (print \"Hello from spam!\") (.__setitem__ (globals) 'x 42) > spam.lissp")
   (hissp.reader..transpile __package__ 'spam 'eggs)

   spam..x                                ;Side effects happen upon both compilation and import!
   ;; Hello from spam!
   ;; 42

   spam..x                                ;42
   eggs.                                  ;Hello, World!

   ;;;; BASIC MACROS

   _#" The REPL comes with some basic macros defined in hissp.basic. By default,
   they don't work in .lissp files unqualified. The compiled output from these
   does not require hissp to be installed."

   #> (help _macro_.->>)                     ;Macros have docstrings and live in _macro_.
   >>> help(
   ...   _macro_.xH_xGT_xGT_)
   Help on function <lambda> in module hissp.basic:
   <BLANKLINE>
   <lambda> lambda expr, *forms
       ``->>`` 'Thread-last'...


   ;; Makes a new reader macro to abbreviate a qualifier.
   #> (hissp.basic.._macro_.alias b/ hissp.basic.._macro_.)
   >>> # hissp.basic.._macro_.alias
   ... # hissp.basic.._macro_.defmacro
   ... # hissp.basic.._macro_.let
   ... (lambda _fnxAUTO7_=(lambda _GxAUTO37_:(
   ...   'Aliases hissp.basic.._macro_. as bxSLASH_#',
   ...   ('{}{}').format(
   ...     'hissp.basic.._macro_.',
   ...     _GxAUTO37_))[-1]):(
   ...   __import__('builtins').setattr(
   ...     _fnxAUTO7_,
   ...     '__qualname__',
   ...     ('.').join(
   ...       ('_macro_', 'bxSLASH_'))),
   ...   __import__('builtins').setattr(
   ...     _macro_,
   ...     'bxSLASH_',
   ...     _fnxAUTO7_))[-1])()

   #> 'b/#alias                              ;Now short for 'hissp.basic.._macro_.alias'.
   >>> 'hissp.basic.._macro_.alias'
   'hissp.basic.._macro_.alias'


   ;; Imports a copy of hissp.basic.._macro_ (if available)
   ;; and star imports from operator and itertools.
   #> (b/#prelude)
   >>> # hissp.basic.._macro_.prelude
   ... __import__('builtins').exec(
   ...   ('from operator import *\n'
   ...    'from itertools import *\n'
   ...    'try:\n'
   ...    '    from hissp.basic import _macro_\n'
   ...    "    _macro_ = __import__('types').SimpleNamespace(**vars(_macro_))\n"
   ...    'except ModuleNotFoundError:\n'
   ...    '    pass'))


   ;;; reader

   #> b#"bytes"                               ;Bytes reader macro.
   >>> b'bytes'
   b'bytes'

   #> b'bytes'                                ;NameError: name 'bx1QUOTE_bytesx1QUOTE_' is not defined
   >>> bx1QUOTE_bytesx1QUOTE_
   Traceback (most recent call last):
     File "<console>", line 1, in <module>
   NameError: name 'bx1QUOTE_bytesx1QUOTE_' is not defined


   #> b#"bytes
   #..with
   #..newlines
   #.."                                      ;Same as b#"bytes\nwith\nnewlines\n".
   >>> b'bytes\nwith\nnewlines\n'
   b'bytes\nwith\nnewlines\n'


   ;;; definition

   #> (define answer 42)                     ;Add a global.
   >>> # define
   ... __import__('operator').setitem(
   ...   __import__('builtins').globals(),
   ...   'answer',
   ...   (42))

   #> (deftype Point2D (tuple)
   #..  __doc__ "Simple pair."
   #..  __new__
   #..  (lambda (cls x y)
   #..    (.__new__ tuple cls `(,x ,y))))
   >>> # deftype
   ... # hissp.basic.._macro_.define
   ... __import__('operator').setitem(
   ...   __import__('builtins').globals(),
   ...   'Point2D',
   ...   __import__('builtins').type(
   ...     'Point2D',
   ...     (lambda *xAUTO0_:xAUTO0_)(
   ...       tuple),
   ...     __import__('builtins').dict(
   ...       __doc__=('Simple pair.'),
   ...       __new__=(lambda cls,x,y:
   ...         tuple.__new__(
   ...           cls,
   ...           (lambda *xAUTO0_:xAUTO0_)(
   ...             x,
   ...             y))))))

   #> (Point2D 1 2)                          ;(1, 2)
   >>> Point2D(
   ...   (1),
   ...   (2))
   (1, 2)


   ;; Define a function in the _macro_ namespace.
   ;; Creates the _macro_ namespace if absent.
   #> (defmacro triple (x)
   #..  `(+ ,x ,x ,x))
   >>> # defmacro
   ... # hissp.basic.._macro_.let
   ... (lambda _fnxAUTO7_=(lambda x:
   ...   (lambda *xAUTO0_:xAUTO0_)(
   ...     '__main__..xAUTO_.xPLUS_',
   ...     x,
   ...     x,
   ...     x)):(
   ...   __import__('builtins').setattr(
   ...     _fnxAUTO7_,
   ...     '__qualname__',
   ...     ('.').join(
   ...       ('_macro_', 'triple'))),
   ...   __import__('builtins').setattr(
   ...     _macro_,
   ...     'triple',
   ...     _fnxAUTO7_))[-1])()


   #> (let (x "a"                            ;Create locals.
   #..      y "b")                           ;Any number of pairs.
   #..  (print x y)
   #..  (let (x "x"
   #..        y (+ x x))                     ;Not in scope until body.
   #..    (print x y))
   #..  (print x y))
   >>> # let
   ... (lambda x=('a'),y=('b'):(
   ...   print(
   ...     x,
   ...     y),
   ...   # let
   ...   (lambda x=('x'),y=xPLUS_(
   ...     x,
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


   ;;; configuration

   #> (define ns (types..SimpleNamespace))
   >>> # define
   ... __import__('operator').setitem(
   ...   __import__('builtins').globals(),
   ...   'ns',
   ...   __import__('types').SimpleNamespace())

   #> (attach ns + : x 1  y 5)
   >>> # attach
   ... # hissp.basic.._macro_.let
   ... (lambda _targetxAUTO22_=ns:(
   ...   __import__('builtins').setattr(
   ...     _targetxAUTO22_,
   ...     'xPLUS_',
   ...     xPLUS_),
   ...   __import__('builtins').setattr(
   ...     _targetxAUTO22_,
   ...     'x',
   ...     (1)),
   ...   __import__('builtins').setattr(
   ...     _targetxAUTO22_,
   ...     'y',
   ...     (5)),
   ...   _targetxAUTO22_)[-1])()
   namespace(x=1, xPLUS_=<built-in function add>, y=5)

   #> ns
   >>> ns
   namespace(x=1, xPLUS_=<built-in function add>, y=5)


   #> (cascade []
   #..  (.append 1)
   #..  (.append 2)
   #..  (.append 3))
   >>> # cascade
   ... (lambda _thingxAUTO26_=[]:(
   ...   _thingxAUTO26_.append(
   ...     (1)),
   ...   _thingxAUTO26_.append(
   ...     (2)),
   ...   _thingxAUTO26_.append(
   ...     (3)),
   ...   _thingxAUTO26_)[-1])()
   [1, 2, 3]


   ;;; threading

   #> (-> "world!"                           ;Thread-first
   #..    (.title)
   #..    (->> (print "Hello")))             ;Thread-last
   >>> # xH_xGT_
   ... # hissp.basic..xAUTO_.xH_xGT_
   ... # hissp.basic..xAUTO_.xH_xGT_
   ... # xH_xGT_xGT_
   ... # hissp.basic..xAUTO_.xH_xGT_xGT_
   ... print(
   ...   ('Hello'),
   ...   ('world!').title())
   Hello World!


   ;;; control flow

   ;; Hissp has no control flow, but you can build them with macros.

   #> (any-for i (range 1 11)                ;Imperative loop with break.
   #..  (print i : end " ")
   #..  (not_ (mod i 7)))
   >>> # anyxH_for
   ... __import__('builtins').any(
   ...   __import__('builtins').map(
   ...     (lambda i:(
   ...       print(
   ...         i,
   ...         end=(' ')),
   ...       not_(
   ...         mod(
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

   (let (x (ast..literal_eval (input "? ")))
     ;; Multi-way branch.
     (cond (lt x 0) (print "Negative")
           (eq x 0) (print "Zero")
           (gt x 0) (print "Positive")
           :else (print "Not a number"))
     (when (eq x 0)                       ;Conditional with side-effects, but no alternative.
       (print "In when")
       (print "was zero"))
     (unless (eq x 0)
       (print "In unless")
       (print "wasn't zero")))

   ;; Shortcutting logical and.
   #> (&& True True False)
   >>> # xET_xET_
   ... # hissp.basic.._macro_.let
   ... (lambda _GxAUTO33_=True:
   ...   # hissp.basic.._macro_.ifxH_else
   ...   (lambda test,*thenxH_else:
   ...     __import__('operator').getitem(
   ...       thenxH_else,
   ...       __import__('operator').not_(
   ...         test))())(
   ...     _GxAUTO33_,
   ...     (lambda :
   ...       # hissp.basic..xAUTO_.xET_xET_
   ...       # hissp.basic.._macro_.let
   ...       (lambda _GxAUTO33_=True:
   ...         # hissp.basic.._macro_.ifxH_else
   ...         (lambda test,*thenxH_else:
   ...           __import__('operator').getitem(
   ...             thenxH_else,
   ...             __import__('operator').not_(
   ...               test))())(
   ...           _GxAUTO33_,
   ...           (lambda :
   ...             # hissp.basic..xAUTO_.xET_xET_
   ...             False),
   ...           (lambda :_GxAUTO33_)))()),
   ...     (lambda :_GxAUTO33_)))()
   False

   #> (&& False (print "oops"))
   >>> # xET_xET_
   ... # hissp.basic.._macro_.let
   ... (lambda _GxAUTO33_=False:
   ...   # hissp.basic.._macro_.ifxH_else
   ...   (lambda test,*thenxH_else:
   ...     __import__('operator').getitem(
   ...       thenxH_else,
   ...       __import__('operator').not_(
   ...         test))())(
   ...     _GxAUTO33_,
   ...     (lambda :
   ...       # hissp.basic..xAUTO_.xET_xET_
   ...       print(
   ...         ('oops'))),
   ...     (lambda :_GxAUTO33_)))()
   False


   ;; Shortcutting logical or.
   #> (|| True (print "oops"))
   >>> # xBAR_xBAR_
   ... # hissp.basic.._macro_.let
   ... (lambda _firstxAUTO34_=True:
   ...   # hissp.basic.._macro_.ifxH_else
   ...   (lambda test,*thenxH_else:
   ...     __import__('operator').getitem(
   ...       thenxH_else,
   ...       __import__('operator').not_(
   ...         test))())(
   ...     _firstxAUTO34_,
   ...     (lambda :_firstxAUTO34_),
   ...     (lambda :
   ...       # hissp.basic..xAUTO_.xBAR_xBAR_
   ...       print(
   ...         ('oops')))))()
   True


   ;;; side effect

   #> (prog1                                 ;Sequence for side effects, evaluating to the first.
   #..  (progn (print 1)                     ;Sequence for side effects, evaluating to the last.
   #..         3)
   #..  (print 2))
   >>> # prog1
   ... # hissp.basic.._macro_.let
   ... (lambda _value1xAUTO35_=# progn
   ... (lambda :(
   ...   print(
   ...     (1)),
   ...   (3))[-1])():(
   ...   print(
   ...     (2)),
   ...   _value1xAUTO35_)[-1])()
   1
   2
   3

