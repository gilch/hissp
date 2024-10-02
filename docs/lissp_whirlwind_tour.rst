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

   "Follow along by entering the following examples in the Lissp REPL.
   It will show you the compiled Python and evaluate it. Try variations
   that occur to you. To fully understand the examples, you must see
   their Python compilation and output. Make sure you install the Hissp
   version matching this document.

   This document is written like a .lissp file, thoroughly demonstrating
   Lissp's (and thereby Hissp's) features from the bottom up with
   minimal exposition. This element enclosed in double quotes is a
   *Unicode token* serving as the docstring for the module.

   Lissp is a lightweight text language representing the Hissp
   intermediate language. The Lissp reader parses the Lissp language's
   symbolic expressions as Python objects. The Hissp compiler
   then translates and assembles these syntax trees into Python code.

   Some familiarity with Python is assumed for this tour. Familiarity with
   another Lisp dialect is not assumed, but helpful. If you get confused or
   stuck, look for the Hissp community chat or try the more expository
   Hissp Primer.

   You are expected to read through the sections in order. New concepts
   will be presented incrementally. Examples of a new concept will
   otherwise be limited to what has been demonstrated so far, which may
   not be their most natural expression.
   "

   ;;;; Installation

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

   ;;;; Fragment Tokens

   ;;; To understand Lissp, let's start with some lexical analysis,
   ;;; so you can recognize the pieces you're looking at.

   ;; This is a FRAGMENT TOKEN.
   ;; You can put Python code inside and the compiler passes it through:
   #> |print('Hello, World!')|            ;note surrounding ||
   >>> print('Hello, World!')
   Hello, World!


   ;;; That's all you need! Now you can write anything in Lissp.
   ;;; In Python. In a fragment token. Just that easy.
   ;;; Yeah, we're not done.

   ;; Escape a | by doubling it:
   #> |bin(0b101_101 || 0b111_000)|       ;bitwise OR operator
   >>> bin(0b101_101 | 0b111_000)
   '0b111101'


   ;;; There are a few special cases that don't simply pass through.

   ;; A MODULE HANDLE abbreviates an import expression:
   #> |collections.abc.|                  ;note the .|
   >>> __import__('collections.abc',fromlist='*')
   <module 'collections.abc' from '...'>


   ;; A FULLY-QUALIFIED IDENTIFIER can be thought of as getting
   ;; attributes from a module handle:
   #> |math..tau.__class__|               ;note the ..
   >>> __import__('math').tau.__class__
   <class 'float'>


   ;; This is a CONTROL WORD. It compiles to a string literal:
   #> |:word|                             ;note the |:
   >>> ':word'
   ':word'


   ;;; Control words control interpretation of other things in some contexts.

   ;;;; Tuples

   ;;; To a first approximation, the Hissp intermediate language is made
   ;;; of Python data representing syntax trees. The nodes are tuples
   ;;; and the leaves are called ATOMS. Collectively, FORMS, are
   ;;; evaluable objects.

   ;;; Pair a `(` (open token) with a `)` (close token) to make a tuple.
   ;;; The compiler assembles fragments according to simple rules.
   ;;; Tuples normally compile to function calls.

   #> (|frozenset|)                       ;call a builtin
   >>> frozenset()
   frozenset()

   #> (|print| |1| |2| |3|)               ;call with arguments
   >>> print(
   ...   1,
   ...   2,
   ...   3)
   1 2 3

   #> (|print| (|set|) (|list|) (|dict|)) ;nested calls
   >>> print(
   ...   set(),
   ...   list(),
   ...   dict())
   set() [] {}

   #> (|print| |*'abc'| |sep='-'|)        ;Python unpacking and keyword arg.
   >>> print(
   ...   *'abc',
   ...   sep='-')
   a-b-c

   #> (|'wow'.upper|)                     ;Method call.
   >>> 'wow'.upper()
   'WOW'


   ;; Method calls have a special case so you can separate them.
   #> (|.upper| |'amazing'|)              ;note the |.
   >>> 'amazing'.upper()
   'AMAZING'


   ;; What happens if you call an "empty name" in Python?
   #> (|| |1| |*'abc'| |3|)               ;That's right, it makes a tuple!
   >>> (
   ...   1,
   ...   *'abc',
   ...   3)
   (1, 'a', 'b', 'c', 3)

   #> (|dict| (|| (|| |1| |2|) (|| |3| |4|))) ;That's enough to make other collections.
   >>> dict(
   ...   (
   ...     (
   ...       1,
   ...       2),
   ...     (
   ...       3,
   ...       4)))
   {1: 2, 3: 4}

   #> (|| |1|)                            ;Be careful with single arguments.
   >>> (
   ...   1)
   1

   #> (|| |1| ||)                         ;You forgot the comma before. Get it?
   >>> (
   ...   1,
   ...   )
   (1,)


   ;;;; Lambda Special Forms

   ;; This looks like a function call, but it's a special case.
   #> (|lambda| (|*xs|) |[*xs]|)          ; list-making lambda expression
   >>> (lambda *xs: [*xs])
   <function <lambda> at 0x...>

   #> (_ |1| |2| |3|) ; _ is previous result that wasn't None in Python shell.
   >>> _(
   ...   1,
   ...   2,
   ...   3)
   [1, 2, 3]


   #> (|lambda| (|i|) (|functools..reduce| |operator..mul| (|range| |i| |0| |-1|) |1|))
   >>> (lambda i:
   ...     __import__('functools').reduce(
   ...       __import__('operator').mul,
   ...       range(
   ...         i,
   ...         0,
   ...         -1),
   ...       1)
   ... )
   <function <lambda> at 0x...>

   #> (|.update| (|globals|) |factorial=_|) ; _ trick doesn't work in modules though
   >>> globals().update(
   ...   factorial=_)

   #> (|factorial| |3|)
   >>> factorial(
   ...   3)
   6

   #> (|factorial| |4|)
   >>> factorial(
   ...   4)
   24


   ;;;; Quote Special Forms

   ;;; Looks like a function call, but it's a special case.
   ;;; Quote forms suppress evaluation and just return the argument form.

   #> (|quote| |math..tau|)
   >>> 'math..tau'
   'math..tau'

   #> |math..tau|
   >>> __import__('math').tau
   6.283185307179586

   #> (|quote| (|print| |42|))
   >>> ('print',
   ...  '42',)
   ('print', '42')

   #> (|print| |42|)
   >>> print(
   ...   42)
   42


   ;;;; Object Tokens

   ;;; Fragment tokens read as str atoms, but they're not the only kind
   ;;; of OBJECT TOKEN. In many cases, you can drop the ||.

   #> |"I'm a string."|                   ;use | for a FRAGMENT TOKEN
   >>> "I'm a string."
   "I'm a string."

   #> "I'm a string."                     ;use " for a UNICODE TOKEN
   >>> ("I'm a string.")
   "I'm a string."

   #> (|quote| |"I'm a string."|)         ;makes sense
   >>> '"I\'m a string."'
   '"I\'m a string."'

   #> (|quote| "I'm a string")            ;What did you expect?
   >>> '("I\'m a string")'
   '("I\'m a string")'


   #> |:control word|
   >>> ':control word'
   ':control word'

   #> :control\ word                      ;use : for a CONTROL TOKEN (note \ )
   >>> ':control word'
   ':control word'

   #> (|quote| :control\ word)            ;same result
   >>> ':control word'
   ':control word'


   ;;; BARE TOKENS don't have a special delimiting character.

   #> |0x_F00|
   >>> 0x_F00
   3840

   #> 0xF00                               ;LITERAL TOKEN (note compilation changed!)
   >>> (3840)
   3840


   #> (|quote| (|None| |False| |...| |42| |4e2| |4+2j|)) ; all str atoms
   >>> ('None',
   ...  'False',
   ...  '...',
   ...  '42',
   ...  '4e2',
   ...  '4+2j',)
   ('None', 'False', '...', '42', '4e2', '4+2j')

   #> (|quote| (None False ... 42 4e2 4+2j)) ;six literal tokens (note compilation!)
   >>> (None,
   ...  False,
   ...  ...,
   ...  (42),
   ...  (400.0),
   ...  ((4+2j)),)
   (None, False, Ellipsis, 42, 400.0, (4+2j))


   #> |object|
   >>> object
   <class 'object'>

   #> object                              ;SYMBOL TOKEN (compiles to identifier)
   >>> object
   <class 'object'>

   #> (quote object)                      ;both symbol tokens (still a str atom)
   >>> 'object'
   'object'


   #> |math.|
   >>> __import__('math')
   <module 'math' (built-in)>

   #> math.                               ;symbol token (module handle)
   >>> __import__('math')
   <module 'math' (built-in)>

   #> math..tau                           ;symbol token (fully-qualified identifier)
   >>> __import__('math').tau
   6.283185307179586

   #> (quote math..tau)                   ;it's still a str atom
   >>> 'math..tau'
   'math..tau'


   ;;;; Tagging Tokens

   ;; Invoke any fully-qualified callable on the next parsed object at READ TIME.
   #> builtins..hex#3840                  ;fully-qualified name ending in # is a TAG
   >>> 0xf00
   3840

   #> builtins..ord#Q                     ;tags make literal notation extensible
   >>> (81)
   81

   #> math..exp#1                         ;e^1. Or to whatever number. At read time.
   >>> (2.718281828459045)
   2.718281828459045

   #> builtins..dict#((1 2) (3 4))        ;no quote or || (note compilation!)
   >>> {1: 2, 3: 4}
   {1: 2, 3: 4}


   ;;; Except for str atoms, atoms in Hissp should evaluate to themselves.
   ;;; But when the atom lacks a Python literal notation, the compiler is
   ;;; in a pickle!

   #> builtins..float#inf                 ;compiler had to fall back to a pickle expression
   >>> # inf
   ... __import__('pickle').loads(b'Finf\n.')
   inf

   #> fractions..Fraction## 2 3           ;add more #s for more arguments (note ##)
   >>> # Fraction(2, 3)
   ... __import__('pickle').loads(b'cfractions\nFraction\n(V2/3\ntR.')
   Fraction(2, 3)


   ;;; Fully-qualified tags are not the only type of tagging token.

   #> builtins..complex# imag=2           ;keyword argument via KWARG TOKEN
   >>> (2j)
   2j

   #> builtins..bytes##encoding=ascii|bytes| ; kwarg can be first (passed by name)
   >>> b'bytes'
   b'bytes'


   ;; Yes, Kwargs are a type of object special-cased in the reader. They're
   ;; only meant for use at read time, but they're allowed to survive to
   ;; run time for debugging purposes.
   #> spam=eggs
   >>> # Kwarg('spam', 'eggs')
   ... __import__('pickle').loads(b'ccopy_reg\n_reconstructor\n(chissp.reader\nKwarg\nc__builtin__\nobject\nNtR(dVk\nVspam\nsVv\nVeggs\nsb.')
   Kwarg('spam', 'eggs')


   ;; use ; for a COMMENT TOKEN (like this one)
   ;; We've seen these a lot. They are, in fact, a type of object token!
   ;; The reader normally discards them, but here it's a tag argument.
   ;; Tagging tokens compose like functions.
   #> builtins..repr# builtins..repr# ; I'm a Comment and
   #..;; I'm another line in the same block!
   >>> 'Comment("; I\'m a Comment and\\n;; I\'m another line in the same block!\\n")'
   'Comment("; I\'m a Comment and\\n;; I\'m another line in the same block!\\n")'


   ;;;; Special Tags

   ;; HARD QUOTE (') is a SPECIAL TAG which abbreviates the quote special form
   #> (quote ''1)
   >>> ('quote',
   ...  ('quote',
   ...   (1),),)
   ('quote', ('quote', 1))

   #> ''x
   >>> ('quote',
   ...  'x',)
   ('quote', 'x')

   #> '\'x'
   >>> 'QzAPOS_xQzAPOS_'
   'QzAPOS_xQzAPOS_'


   #> builtins..complex# *=(4 2) ; unpacking via STARARG TOKEN (special tag Kwarg)
   >>> ((4+2j))
   (4+2j)


   #> _#"The DISCARD TAG (_#) is a special tag that omits the next form.
   #..It's a way to comment out code structurally.
   #..It can also make Unicode token comments like this one.
   #..(But the need to escape double quotes might make ;; comments easier.)
   #..This would show up when compiled if not for _#.
   #..Of course, a string statement like this one wouldn't do anything
   #..in Python, even if it were compiled in.
   #.."
   >>>

   #> (print 1 _#(I'm not here!) 2 3)
   >>> print(
   ...   (1),
   ...   (2),
   ...   (3))
   1 2 3


   ;;; The INJECT special tag compiles and evaluates the next form at
   ;;; read time and injects the resulting object directly into the Hissp
   ;;; tree, like a fully-qualified tag does.

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

   #> .#(fractions..Fraction 1 2)         ;Read time eval. Reads as equivalent object.
   >>> # Fraction(1, 2)
   ... __import__('pickle').loads(b'cfractions\nFraction\n(V1/2\ntR.')
   Fraction(1, 2)


   ;; An injected Unicode token acts like a fragment token, but can have
   ;; things like newlines and string escape codes.
   #> (lambda (a b c)
   #..  .#"(-b + (b**2 - 4*a*c)**0.5)
   #..    /(2*a)") ; quadratic formula
   >>> (lambda a, b, c:
   ...     (-b + (b**2 - 4*a*c)**0.5)
   ...         /(2*a)
   ... )
   <function <lambda> at 0x...>


   ;;;; Symbol Token Munging

   #> '+                                  ;Read-time munging of invalid identifiers.
   >>> 'QzPLUS_'
   'QzPLUS_'

   #> 'Also-a-symbol!                     ;Alias for 'AlsoQzH_aQzH_symbolQzBANG_
   >>> 'AlsoQzH_aQzH_symbolQzBANG_'
   'AlsoQzH_aQzH_symbolQzBANG_'

   #> '𝐀                                  ;Alias for 'A (Unicode normal form KC)
   >>> 'A'
   'A'

   #> '-<>>
   >>> 'QzH_QzLT_QzGT_QzGT_'
   'QzH_QzLT_QzGT_QzGT_'

   #> :-<>>                               ;Doesn't represent identifier; doesn't munge.
   >>> ':-<>>'
   ':-<>>'

   #> :                                   ;Shortest control word.
   >>> ':'
   ':'


   ;;;; Escaping with \

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

   #> 1\2                                 ;Backslashes work in other tokens.
   >>> (12)
   12

   #> N\one
   >>> None


   ;;;; Advanced Call Arguments

   #> (dict |spam="foo"| |eggs="bar"| |ham="baz"|) ; kwargs via fragment tokens
   >>> dict(
   ...   spam="foo",
   ...   eggs="bar",
   ...   ham="baz")
   {'spam': 'foo', 'eggs': 'bar', 'ham': 'baz'}

   #> (dict : spam "foo"  eggs "bar"  ham "baz") ; no || here (note the :)
   >>> dict(
   ...   spam=('foo'),
   ...   eggs=('bar'),
   ...   ham=('baz'))
   {'spam': 'foo', 'eggs': 'bar', 'ham': 'baz'}


   #> (print 1 2 3 |sep="-"|)
   >>> print(
   ...   (1),
   ...   (2),
   ...   (3),
   ...   sep="-")
   1-2-3

   #> (print : :? 1  :? 2  :? 3  sep "-") ;:? is a positional target.
   >>> print(
   ...   (1),
   ...   (2),
   ...   (3),
   ...   sep=('-'))
   1-2-3

   #> (print 1 2 3 : sep "-")             ;Arguments before : implicitly pair with :?.
   >>> print(
   ...   (1),
   ...   (2),
   ...   (3),
   ...   sep=('-'))
   1-2-3


   ;; Python unpacking, positional, and keyword arguments.
   #> (print 1 |*"abc"| 2 |*"xyz"| |**{"sep": "-"}| |flush=True| |**{"end": "!?\n"}|)
   >>> print(
   ...   (1),
   ...   *"abc",
   ...   (2),
   ...   *"xyz",
   ...   **{"sep": "-"},
   ...   flush=True,
   ...   **{"end": "!?\n"})
   1-a-b-c-2-x-y-z!?


   ;; You can do the same things without || using control words.
   #> (print 1                            ;Implicitly a positional :? target.
   #..       : :* "abc"                   ;Target :* to unpack iterable.
   #..       :? 2                         ;:? is still allowed after :*.
   #..       :* "xyz"                     ;:* is a repeatable positional target.
   #..       :** |{"sep": "-"}|           ;Target :** to unpack mapping.
   #..       flush True                   ;Kwargs still allowed after :**.
   #..       :** |{"end": "!?\n"}|)       ;Multiple :** allowed too.
   >>> print(
   ...   (1),
   ...   *('abc'),
   ...   (2),
   ...   *('xyz'),
   ...   **{"sep": "-"},
   ...   flush=True,
   ...   **{"end": "!?\n"})
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


   ;;;; Advanced Lambda Parameters

   ;; Python parameter types are rather involved.
   #> (lambda (a b |/| c d |e=1| |f=2| |*args| |h=4| i |j=1| |**kwargs|)
   #..  (print (locals)))
   >>> (lambda a, b, /, c, d, e=1, f=2, *args, h=4, i, j=1, **kwargs:
   ...     print(
   ...       locals())
   ... )
   <function <lambda> at 0x...>

   ;; Lambda control words can do all of them.
   ;; Like calls, they are all pairs. :? means no default.
   #> (lambda (: a :?  b :?  :/ :?        ;positional only
   #..         c :?  d :?                 ;normal
   #..         e 1  f 2                   ;default
   #..         :* args  h 4  i :?  j 1    ;star args, keyword
   #..         :** kwargs)
   #..  ;; Body.
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


   #> (lambda (|*xs|))                    ;star arg
   >>> (lambda *xs: ())
   <function <lambda> at 0x...>

   #> (lambda (|*| |kw|))                 ;keyword only (note comma)
   >>> (lambda *, kw: ())
   <function <lambda> at 0x...>


   #> (lambda (: :* xs))                  ;Star arg must pair with star, as Python.
   >>> (lambda *xs: ())
   <function <lambda> at 0x...>

   #> (lambda (: :* :?  kw :?))           ;Empty star arg, so kw is keyword only.
   >>> (lambda *, kw: ())
   <function <lambda> at 0x...>

   #> (lambda (:* : kw :?))               ;Slid : right one pair. Still a kwonly.
   >>> (lambda *, kw: ())
   <function <lambda> at 0x...>

   #> (lambda (:* kw :))                  ;Implicit :? is the same. Compare.
   >>> (lambda *, kw: ())
   <function <lambda> at 0x...>

   #> (lambda (:* kw))                    ;Kwonly! Not star arg! Final : implied.
   >>> (lambda *, kw: ())
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


   #> (lambda (:))                        ;Explicit : still allowed with nothing.
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


   ;;;; Operators

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

   #> |40+2|                              ;Of course, this always worked. Just Python.
   >>> 40+2
   42


   ;;;; Control Flow

   ;;; Hissp is simpler than Python. No control flow! Use higher-order functions instead.

   #> (any (map print "abc")) ; Loops!
   >>> any(
   ...   map(
   ...     print,
   ...     ('abc')))
   a
   b
   c
   False


   ((.get (dict : y (lambda : (print "Yes!"))
                n (lambda : (print "Canceled.")))
          (input "enter y/n> ")
          (lambda : (print "Unrecognized input.")))) ; Branches!

   ;;; Don't worry, Hissp metaprogramming will make this much easier
   ;;; (and Hissp comes bundled with macros for these things), but our
   ;;; limited tools so far are enough for a ternary operator.

   ;; boolean, consequent, alternate
   #> (.update (globals) : if_else (lambda bca ((.__getitem__ (|| c a) (not b)))))
   >>> globals().update(
   ...   if_else=(lambda b, c, a:
   ...               (
   ...                 c,
   ...                 a).__getitem__(
   ...                 not(
   ...                   b))()
   ...           ))


   #> (any (map (lambda x (if_else |x%2|
   #..                             (lambda : (print x 'odd))
   #..                             (lambda : (print x 'even))))
   #..          (range 4))) ; Both!
   >>> any(
   ...   map(
   ...     (lambda x:
   ...         if_else(
   ...           x%2,
   ...           (lambda :
   ...               print(
   ...                 x,
   ...                 'odd')
   ...           ),
   ...           (lambda :
   ...               print(
   ...                 x,
   ...                 'even')
   ...           ))
   ...     ),
   ...     range(
   ...       (4))))
   0 even
   1 odd
   2 even
   3 odd
   False


   ;;;; Templates

   ;; SOFT QUOTE special tag (`) starts a template
   #> `print                              ;Automatic full qualification!
   >>> 'builtins..print'
   'builtins..print'

   #> `foo+2                              ;Not builtin. Still munges.
   >>> '__main__..fooQzPLUS_2'
   '__main__..fooQzPLUS_2'


   #> `(print "Hi")                       ;Code as data. Seems to act like quote.
   >>> (
   ...   'builtins..print',
   ...   "('Hi')",
   ...   )
   ('builtins..print', "('Hi')")

   #> '`(print "Hi")                      ;But it's calling the "empty name".
   >>> ('',
   ...  ':',
   ...  ':?',
   ...  ('quote',
   ...   'builtins..print',),
   ...  ':?',
   ...  ('quote',
   ...   "('Hi')",),
   ...  ':?',
   ...  '',)
   ('', ':', ':?', ('quote', 'builtins..print'), ':?', ('quote', "('Hi')"), ':?', '')


   ;; UNQUOTE special tag (,) interpolates. Only valid in a template.
   #> `(print ,(.upper "Hi"))
   >>> (
   ...   'builtins..print',
   ...   ('Hi').upper(),
   ...   )
   ('builtins..print', 'HI')

   #> `(,'foo+2 foo+2)                    ;Interpolations not auto-qualified!
   >>> (
   ...   'fooQzPLUS_2',
   ...   '__main__..fooQzPLUS_2',
   ...   )
   ('fooQzPLUS_2', '__main__..fooQzPLUS_2')


   ;; SPLICE special tag (,@) interpolates and unpacks. Only valid in a tuple in a template.
   #> `(print ,@"abc")
   >>> (
   ...   'builtins..print',
   ...   *('abc'),
   ...   )
   ('builtins..print', 'a', 'b', 'c')

   #> `(print (.upper "abc"))             ;Template quoting is recursive
   >>> (
   ...   'builtins..print',
   ...   (
   ...     '.upper',
   ...     "('abc')",
   ...     ),
   ...   )
   ('builtins..print', ('.upper', "('abc')"))

   #> `(print ,@(.upper "abc"))           ; unless suppressed by an unquote.
   >>> (
   ...   'builtins..print',
   ...   *('abc').upper(),
   ...   )
   ('builtins..print', 'A', 'B', 'C')


   ;;; Full qualification prevents accidental name collisions in
   ;;; programmatically generated code. But full qualification doesn't work
   ;;; on local variables, which can't be imported. For these, we use a
   ;;; GENSYM special tag ($#) which (instead of a qualifier) adds a prefix
   ;;; to ensure a variable can only be used in the same template it was
   ;;; defined in. It contains a hash of three things: the code being read,
   ;;; __name__, and a count of the templates the reader has seen so far.

   #> `($#eggs $#spam $#bacon $#spam)
   >>> (
   ...   '_Qziwmx5ob2__eggs',
   ...   '_Qziwmx5ob2__spam',
   ...   '_Qziwmx5ob2__bacon',
   ...   '_Qziwmx5ob2__spam',
   ...   )
   ('_Qziwmx5ob2__eggs', '_Qziwmx5ob2__spam', '_Qziwmx5ob2__bacon', '_Qziwmx5ob2__spam')

   ;; Each new template increases the count, so it results in a new hash,
   #> `$#spam
   >>> '_Qziosozaxy__spam'
   '_Qziosozaxy__spam'

   ;; even if the code is identical.
   #> `$#spam
   >>> '_Qzy6owmzs7__spam'
   '_Qzy6owmzs7__spam'


   ;;; However, the hashing procedure is fully deterministic, so builds are
   ;;; reproducible even when they contain generated symbols.

   ;; If you don't specify, by default, the gensym hash is a prefix,
   ;; but you can put them anywhere in the symbol. $ marks the positions.
   ;; Lacking a gensym prefix, it gets fully qualified by the template.
   #> `$#spam$.$eggs$
   >>> '__main__..spam_Qza4ibv7j7__._Qza4ibv7j7__eggs_Qza4ibv7j7__'
   '__main__..spam_Qza4ibv7j7__._Qza4ibv7j7__eggs_Qza4ibv7j7__'


   ;; This is typically used for partially-qualified variables,
   ;; i.e., with an explicit namespace that is not a module handle.
   ;; The interpolation suppressed auto-qualification.
   #> `,'$#self.$foo
   >>> 'self._Qz7uu6wad6__foo'
   'self._Qz7uu6wad6__foo'


   ;;; You can use templates to make collections with interpolated values.
   ;;; When your intent is to create data rather than code, unquote
   ;;; each element.

   ;; (Uses `+` from ;;;; Operators)
   #> (list `(,@"abc"
   #..        ,1
   #..        ,(+ 1 1)
   #..        ,(+ 1 2)))
   >>> list(
   ...   (
   ...     *('abc'),
   ...     (1),
   ...     QzPLUS_(
   ...       (1),
   ...       (1)),
   ...     QzPLUS_(
   ...       (1),
   ...       (2)),
   ...     ))
   ['a', 'b', 'c', 1, 2, 3]


   #> `(0 "a" 'b)                         ;Beware of Unicode tokens and symbols.
   >>> (
   ...   (0),
   ...   "('a')",
   ...   (
   ...     'quote',
   ...     '__main__..b',
   ...     ),
   ...   )
   (0, "('a')", ('quote', '__main__..b'))

   #> `(,0 ,"a" ,'b)                      ;Just unquote everything in data templates.
   >>> (
   ...   (0),
   ...   ('a'),
   ...   'b',
   ...   )
   (0, 'a', 'b')


   #> (dict `((,0 ,1)
   #..        ,@(.items (dict : spam "eggs"  foo 2)) ;dict unpacking
   #..        (,3 ,4)))
   >>> dict(
   ...   (
   ...     (
   ...       (0),
   ...       (1),
   ...       ),
   ...     *dict(
   ...        spam=('eggs'),
   ...        foo=(2)).items(),
   ...     (
   ...       (3),
   ...       (4),
   ...       ),
   ...     ))
   {0: 1, 'spam': 'eggs', 'foo': 2, 3: 4}


   ;;;; Macros

   ;;; We can use functions to to create forms for evaluation.
   ;;; This is metaprogramming: code that writes code.

   #> (.update (globals)                  ;assign fills in a template to make a form.
   #..         : assign
   #..         (lambda (key value)
   #..           `(.update (globals) : ,key ,value)))
   >>> globals().update(
   ...   assign=(lambda key, value:
   ...              (
   ...                '.update',
   ...                (
   ...                  'builtins..globals',
   ...                  ),
   ...                ':',
   ...                key,
   ...                value,
   ...                )
   ...          ))


   ;; Notice the arguments to it are quoted.
   #> (assign 'SPAM '"eggs")              ;The result is a valid Hissp form.
   >>> assign(
   ...   'SPAM',
   ...   "('eggs')")
   ('.update', ('builtins..globals',), ':', 'SPAM', "('eggs')")

   #> (hissp.compiler..readerless _)      ;Hissp can compile it,
   >>> __import__('hissp.compiler',fromlist='*').readerless(
   ...   _)
   "__import__('builtins').globals().update(\n  SPAM=('eggs'))"

   #> (eval _)                            ; and Python can evaluate that.
   >>> eval(
   ...   _)

   #> SPAM                                ;'eggs'
   >>> SPAM
   'eggs'


   ;;; We can accomplish this more easily with a MACRO FORM.

   ;;; Unqualified invocations are macro forms if the identifier is in
   ;;; the current module's _macro_ namespace. The REPL includes one, but
   ;;; .lissp files don't have one until you create it.

   (dir)                                  ;note _macro_
   (dir _macro_)

   ;;; Macros run at compile time, so they get all of their arguments
   ;;; unevaluated. The compiler inserts the resulting Hissp
   ;;; (the EXPANSION) at that point in the program.

   #> (setattr _macro_ 'assign assign)    ;we can use assign as a MACRO FUNCTION
   >>> setattr(
   ...   _macro_,
   ...   'assign',
   ...   assign)


   ;; Like special forms, macro forms look like ordinary function calls.
   #> (assign SPAM "ham")                 ;This runs a metaprogram!
   >>> # assign
   ... __import__('builtins').globals().update(
   ...   SPAM=('ham'))

   #> SPAM                                ;'ham'
   >>> SPAM
   'ham'


   ;;; We almost could have accomplished this one with a function, but we'd
   ;;; have to either quote the variable name or use a : to pass it in as a
   ;;; keyword. The macro form is a little shorter. Furthermore, the
   ;;; globals function gets the globals dict for the current module. Thus,
   ;;; an assign function would assign globals to the module it is defined
   ;;; in, not the one where it is used! You could get around this by
   ;;; walking up a stack frame with inspect, but that's brittle. The macro
   ;;; version just works because it writes the code in line for you, so
   ;;; the globals call appears in the right module.

   ;;; Macros are a feature of the Hissp compiler. Macro expansion happens
   ;;; at compile time, after the reader, so macros also work in readerless
   ;;; mode, or with Hissp readers other than Lissp, like Hebigo.

   ;;; UNQUALIFIED TAGS work if there's a corresponding name ending in #
   ;;; (i.e. QzHASH_) in _macro_. Metaprograms for tagging tokens run at
   ;;; read time, but (like ') may simply return code that runs later.

   #> (setattr _macro_ 'chr\# chr)        ;note \# (would be a tag token otherwise)
   >>> setattr(
   ...   _macro_,
   ...   'chrQzHASH_',
   ...   chr)

   #> 'chr#42                             ;note hard quote
   >>> '*'
   '*'


   ;; Hissp already comes with a define macro for attribute assignment.
   (help hissp.._macro_.define)

   ;; An invocation fully qualified with _macro_ is a macro form.
   #> (hissp.._macro_.define SPAM "eggs") ;Note SPAM is not quoted.
   >>> # hissp.._macro_.define
   ... __import__('builtins').globals().update(
   ...   SPAM=('eggs'))

   #> SPAM                                ;'eggs'
   >>> SPAM
   'eggs'


   ;; The REPL's default _macro_ namespace already has the bundled macros.
   (help _macro_.define)

   ;;;; Macro Technique

   ;;; (Examples here use `+` from ;;;; Operators)

   ;; Use a template to make Hissp.
   #> (define _macro_.triple (lambda x `(+ ,x (+ ,x ,x))))
   >>> # define
   ... __import__('builtins').setattr(
   ...   _macro_,
   ...   'triple',
   ...   (lambda x:
   ...       (
   ...         '__main__..QzMaybe_.QzPLUS_',
   ...         x,
   ...         (
   ...           '__main__..QzMaybe_.QzPLUS_',
   ...           x,
   ...           x,
   ...           ),
   ...         )
   ...   ))

   #> (triple 4)                          ;12
   >>> # triple
   ... __import__('builtins').globals()['QzPLUS_'](
   ...   (4),
   ...   __import__('builtins').globals()['QzPLUS_'](
   ...     (4),
   ...     (4)))
   12


   #> (define loud-number (lambda x (print x) x))
   >>> # define
   ... __import__('builtins').globals().update(
   ...   loudQzH_number=(lambda x:
   ...                     (print(
   ...                        x),
   ...                      x)  [-1]
   ...                  ))

   #> (triple (loud-number 14))           ;Triples the *code*, not just the *value*.
   >>> # triple
   ... __import__('builtins').globals()['QzPLUS_'](
   ...   loudQzH_number(
   ...     (14)),
   ...   __import__('builtins').globals()['QzPLUS_'](
   ...     loudQzH_number(
   ...       (14)),
   ...     loudQzH_number(
   ...       (14))))
   14
   14
   14
   42


   ;; But what if we want the expanded code to only run it once?
   ;; We can use a lambda to make a local variable and immediately call it.
   #> ((lambda x (+ x (+ x x)))
   #.. (loud-number 14))
   >>> (lambda x:
   ...     QzPLUS_(
   ...       x,
   ...       QzPLUS_(
   ...         x,
   ...         x))
   ... )(
   ...   loudQzH_number(
   ...     (14)))
   14
   42


   ;; Python also allows us to use a default argument up front.
   #> ((lambda (: x (loud-number 14))
   #..   (+ x (+ x x))))
   >>> (
   ...  lambda x=loudQzH_number(
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
   #> (define _macro_.oops-triple
   #..  (lambda (expression)
   #..    `((lambda (: x ,expression) ;Expand to lambda call for a local.
   #..        (+ x (+ x x))))))
   >>> # define
   ... __import__('builtins').setattr(
   ...   _macro_,
   ...   'oopsQzH_triple',
   ...   (lambda expression:
   ...       (
   ...         (
   ...           'lambda',
   ...           (
   ...             ':',
   ...             '__main__..x',
   ...             expression,
   ...             ),
   ...           (
   ...             '__main__..QzMaybe_.QzPLUS_',
   ...             '__main__..x',
   ...             (
   ...               '__main__..QzMaybe_.QzPLUS_',
   ...               '__main__..x',
   ...               '__main__..x',
   ...               ),
   ...             ),
   ...           ),
   ...         )
   ...   ))

   #> (oops-triple 14)                    ;Oops. Templates qualify symbols!
   >>> # oopsQzH_triple
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
   #> (define _macro_.once-triple
   #..  (lambda x
   #..    `((lambda (: $#x ,x)
   #..        (+ $#x (+ $#x $#x))))))
   >>> # define
   ... __import__('builtins').setattr(
   ...   _macro_,
   ...   'onceQzH_triple',
   ...   (lambda x:
   ...       (
   ...         (
   ...           'lambda',
   ...           (
   ...             ':',
   ...             '_Qziingj4sl__x',
   ...             x,
   ...             ),
   ...           (
   ...             '__main__..QzMaybe_.QzPLUS_',
   ...             '_Qziingj4sl__x',
   ...             (
   ...               '__main__..QzMaybe_.QzPLUS_',
   ...               '_Qziingj4sl__x',
   ...               '_Qziingj4sl__x',
   ...               ),
   ...             ),
   ...           ),
   ...         )
   ...   ))

   #> (once-triple (loud-number 14))
   >>> # onceQzH_triple
   ... (
   ...  lambda _Qzif7wpgtu__x=loudQzH_number(
   ...           (14)):
   ...     __import__('builtins').globals()['QzPLUS_'](
   ...       _Qzif7wpgtu__x,
   ...       __import__('builtins').globals()['QzPLUS_'](
   ...         _Qzif7wpgtu__x,
   ...         _Qzif7wpgtu__x))
   ... )()
   14
   42


   ;;; Notice the special QzMaybe_ qualifier generated by this template.
   ;;; Templates create these for symbols in the invocation position (first
   ;;; tuple element) when they can't tell if _macro_ would work. The
   ;;; compiler replaces a QzMaybe_ with _macro_ if it can resolve the
   ;;; resulting symbol, and omits it otherwise.

   #> `(+ 1 2 3 4)
   >>> (
   ...   '__main__..QzMaybe_.QzPLUS_',
   ...   (1),
   ...   (2),
   ...   (3),
   ...   (4),
   ...   )
   ('__main__..QzMaybe_.QzPLUS_', 1, 2, 3, 4)


   ;; Outside-in recursive macro. (A multiary +). Note the QzMaybe_.
   ;; If this had been qualified like a global instead, the recursion
   ;; wouldn't work.
   #> (define _macro_.+
   #..  (lambda (: first 0  :* args) ; 0 with no args. Try it!
   #..    (.__getitem__ ; Tuple method. Templates produce tuples.
   #..      `(,first ; Result when no args left.
   #..        (operator..add ,first (+ ,@args))) ; Otherwise recur.
   #..      (bool args))))        ;Bools are ints, remember?
   >>> # define
   ... __import__('builtins').setattr(
   ...   _macro_,
   ...   'QzPLUS_',
   ...   (
   ...    lambda first=(0),
   ...           *args:
   ...       (
   ...         first,
   ...         (
   ...           'operator..add',
   ...           first,
   ...           (
   ...             '__main__..QzMaybe_.QzPLUS_',
   ...             *args,
   ...             ),
   ...           ),
   ...         ).__getitem__(
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
   >>> (
   ...   '__main__.._macro_.QzPLUS_',
   ...   (1),
   ...   (2),
   ...   (3),
   ...   (4),
   ...   )
   ('__main__.._macro_.QzPLUS_', 1, 2, 3, 4)


   ;; Recursive macros can also expand from the inside outwards, although
   ;; it's less natural in this case.
   #> (define _macro_.*
   #..  (lambda (: first 1  second 1  :* args)
   #..    (.__getitem__
   #..      `((operator..mul ,first ,second)
   #..        (* (operator..mul ,first ,second) ,@args))
   #..      (bool args))))
   >>> # define
   ... __import__('builtins').setattr(
   ...   _macro_,
   ...   'QzSTAR_',
   ...   (
   ...    lambda first=(1),
   ...           second=(1),
   ...           *args:
   ...       (
   ...         (
   ...           'operator..mul',
   ...           first,
   ...           second,
   ...           ),
   ...         (
   ...           '__main__..QzMaybe_.QzSTAR_',
   ...           (
   ...             'operator..mul',
   ...             first,
   ...             second,
   ...             ),
   ...           *args,
   ...           ),
   ...         ).__getitem__(
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


   ;;; Hissp comes with some helper functions meant only for use
   ;;; interactively or in metaprograms. The compiled output isn't
   ;;; dependent on Hissp when these are used correctly.

   ;; Three of the helpers expand macros.
   #> (hissp..macroexpand1 '(print 1 2 3)) ;not a macro form (no change)
   >>> __import__('hissp').macroexpand1(
   ...   ('print',
   ...    (1),
   ...    (2),
   ...    (3),))
   ('print', 1, 2, 3)

   #> (hissp..macroexpand1 '(* 1 2 3))    ;expanded (but still a macro form)
   >>> __import__('hissp').macroexpand1(
   ...   ('QzSTAR_',
   ...    (1),
   ...    (2),
   ...    (3),))
   ('__main__..QzMaybe_.QzSTAR_', ('operator..mul', 1, 2), 3)

   #> (hissp..macroexpand '(* 1 2 3))     ;repeats while it's a macro form
   >>> __import__('hissp').macroexpand(
   ...   ('QzSTAR_',
   ...    (1),
   ...    (2),
   ...    (3),))
   ('operator..mul', ('operator..mul', 1, 2), 3)

   #> (hissp..macroexpand '(+ 1 2 3))     ;but doesn't check subforms
   >>> __import__('hissp').macroexpand(
   ...   ('QzPLUS_',
   ...    (1),
   ...    (2),
   ...    (3),))
   ('operator..add', 1, ('__main__..QzMaybe_.QzPLUS_', 2, 3))

   #> (hissp..macroexpand_all '(+ 1 2 3)) ;expands all macro subforms
   >>> __import__('hissp').macroexpand_all(
   ...   ('QzPLUS_',
   ...    (1),
   ...    (2),
   ...    (3),))
   ('operator..add', 1, ('operator..add', 2, 3))


   ;; Five of the helpers are predicates for inspecting code.
   #> (pprint..pp
   #.. (list
   #..  (itertools..starmap
   #..   (lambda xy (|| x y.__name__))
   #..   (filter (lambda x (|x[1]| |x[0]|))
   #..           (itertools..product '(:control symbol "string" 'quoted () 1 '2)
   #..                               (|| hissp..is_atomic
   #..                                   hissp..is_control
   #..                                   hissp..is_symbol
   #..                                   hissp..is_hissp_string
   #..                                   hissp..is_string_literal))))))
   >>> __import__('pprint').pp(
   ...   list(
   ...     __import__('itertools').starmap(
   ...       (lambda x, y:
   ...           (
   ...             x,
   ...             y.__name__)
   ...       ),
   ...       filter(
   ...         (lambda x:
   ...             x[1](
   ...               x[0])
   ...         ),
   ...         __import__('itertools').product(
   ...           (':control',
   ...            'symbol',
   ...            "('string')",
   ...            ('quote',
   ...             'quoted',),
   ...            (),
   ...            (1),
   ...            ('quote',
   ...             (2),),),
   ...           (
   ...             __import__('hissp').is_atomic,
   ...             __import__('hissp').is_control,
   ...             __import__('hissp').is_symbol,
   ...             __import__('hissp').is_hissp_string,
   ...             __import__('hissp').is_string_literal))))))
   [(':control', 'is_atomic'),
    (':control', 'is_control'),
    ('symbol', 'is_atomic'),
    ('symbol', 'is_symbol'),
    ("('string')", 'is_atomic'),
    ("('string')", 'is_hissp_string'),
    ("('string')", 'is_string_literal'),
    (('quote', 'quoted'), 'is_hissp_string'),
    ((), 'is_atomic'),
    (1, 'is_atomic')]


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
   ;;; (an ANAPHOR). Don't qualify and don't gensym in that case.
   ;;; Unquoting suppresses the recursive template quoting of tuples,
   ;;; while the hard quote doesn't qualify symbols, so this combination
   ;;; suppresses auto-qualification.

   #> (define _macro_.XY
   #..  (lambda (: :* body)
   #..    `(lambda (,'X ,'Y)       ;,'X instead of $#X
   #..       ,body)))
   >>> # define
   ... __import__('builtins').setattr(
   ...   _macro_,
   ...   'XY',
   ...   (lambda *body:
   ...       (
   ...         'lambda',
   ...         (
   ...           'X',
   ...           'Y',
   ...           ),
   ...         body,
   ...         )
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
   #> (define _macro_.p123
   #..  (lambda (sep)
   #..    `(print 1 2 3 : sep ,sep)))
   >>> # define
   ... __import__('builtins').setattr(
   ...   _macro_,
   ...   'p123',
   ...   (lambda sep:
   ...       (
   ...         'builtins..print',
   ...         (1),
   ...         (2),
   ...         (3),
   ...         ':',
   ...         '__main__..sep',
   ...         sep,
   ...         )
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


   ;;;; Compiling and Running Files

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
   #..             'hissp.reader..Comment.contents#
   #..             ;; (print "Hello from spam!")
   #..             ;; (.update (globals) : x 42)
   #..             _#"<- A string from a comment. Doesn't need \" escape.")
   >>> __import__('pathlib').Path(
   ...   ('spam.lissp')).write_text(
   ...   '(print "Hello from spam!")\n(.update (globals) : x 42)')
   53

   #> (hissp.reader..transpile __package__ 'spam 'eggs) ;Side effects on compilation.
   >>> __import__('hissp.reader',fromlist='*').transpile(
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


   ;;;; The Bundled Macros and Tags

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
   ;;; short qualifying tags, as well as attributes of ordinary modules.

   (help _macro_.alias)

   ;;; The prelude copies _macro_ from hissp._macro_ like the REPL, defines
   ;;; some Python interop helper functions, and imports Python's standard-library
   ;;; functional programming utilities from operator and itertools.

   (help _macro_.prelude)

   ;;; The docstrings use reStructuredText markup. While readable as plain
   ;;; text in the help console, they're also rendered as HTML using Sphinx
   ;;; in Hissp's online API docs. Find them at https://hissp.rtfd.io

   ;;; Familiarize yourself with a macro suite, such as the bundled macros.
   ;;; It makes Hissp that much more usable.
