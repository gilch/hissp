.. Copyright 2020 Matthew Egan Odendahl
   SPDX-License-Identifier: Apache-2.0

::

   ;;;; Lissp Quick Start

   ;; This is written like a .lissp file,
   ;; demonstrating Lissp's features with minimal exposition.
   ;; Some familiarity with Python is assumed.
   ;; Familiarity with another Lisp dialect is helpful.
   ;; If this is too difficult, see the tutorial.

   ;; Install hissp with $ pip install hissp
   ;; Start the REPL with $ hissp
   ;; Quit with EOF or (exit).

   ;; Follow along by entering these examples in the REPL.
   ;; It will show you the compiled Python, and evaluate it.

   ;;; Comments

   ;; Lissp comments begin with a semicolon.
   ;; Headers start with three or more.
   ;; Whole-line comments start with two and may be indented.
   ;; Inline and margin comments start with one.

   ;;; Numeric

   ;; Numeric literals are the same as Python.

   False ; bool
   True ; Yes, bools are numeric: 0 and 1.

   42 ; int
   0x10 ; 16
   0o10 ; 8
   0b10 ; 2
   0b1111_0000_0000 ; 0xF00

   -4.2 ; float
   4e2 ; 400.0
   -1.6e-2 ; -0.016

   5j ; imaginary
   4+2j ; complex
   -1_2.3_4e-5_6-7_8.9_8e-7_6j ; Very complex!

   ;;; Singleton

   ;; Also the same as Python.

   None
   ... ; Ellipsis

   ;;; Symbolic

   ;; Symbolic literals are not quite like Python.

   ;; TODO: b'''bytes''' with newlines?
   b'bytes'

   object ; identifier
   math..tau ; qualified identifiers do an import

   builtins..object ; qualified identifier
   object.__class__ ; attribute identifier
   builtins..object.__class__ ; qualified attribute identifier
   object.__class__.__name__ ; Attributes chain.

   :control-word ; Called ":keywords" in other Lisps.

   'symbol ; Symbols represent identifiers.

   ;; Read-time special-character munging.
   'Also-a-symbol! ; same as 'AlsoxH_axH_symbolxBANG_
   '+ ; 'xPLUS_
   '->> ; 'xH_xGT_xGT_

   "string" ; Double-quotes only!

   "string
   with
   newlines
   " ; same as "string\nwith\nnewlines\n"

   ;;; Empty Collections

   ;; Same as Python

   () ; empty tuple
   {} ; empty dict
   [] ; empty list

   ;;; Invocations

   (print "Hello, World!) ; "(" goes before function name!
   (print 1 2 3) ; No commas between arguments!

   ;; Paired arguments after the ":" are for Python compatibility.
   ;; This is a bit different from other Lisps.

   (print 1 2 3 : sep "-") ; Kwargs after the ":".

   ;; Control words like : :* :? normally compile to strings,
   ;; but they can have special meaning in certain contexts.

   ;; The :* is for Python's positional unpacking. Try it!
   ;; (There's also a :** for kwarg unpacking.)
   ;; The :? passes a paired argument positionally.
   ;; Pairs are conventionally separated by an extra space,
   (print 1 : :* "abc"  :? 2  sep "-")

   ;; The ``self`` is the first argument to method calls.
   (.upper "shout!") ; "SHOUT!"

   ;; Macros can rewrite code before evaluation.
   (-> "world!" (.title) (->> (print "Hello")))

   ;; Python's online help function is still available.
   (help float)
   ;; Macros have docstrings like functions do.
   ;; They live in the _macro_ namespace.
   (dir) ; See the _macro_?
   (help _macro_.->>)

   ;;; Lambda

   ;; Lambda invocations create functions.
   (lambda (x) x)

   ;; They support the same argument types as Python.
   (lambda (a b :/ ; positional only
            c d ; positional
            : e 1  f 2 ; default
            :* args  h 4  i :?  j 1 ; kwonly
            :** kwargs) ; arguments tuple
     ;; body
     (print "hi" a) ; side effect
     b) ; last value is returned

   ;;; Operators

   ;; Lissp is simpler than Python. No operators!
   ;; Use function invocations instead.

   (operator..add 40 2) ; Addition.
   (.__setitem__ (globals) '+ operator..add) ; Assignment.
   (+ 40 2) ; This is still a function call!

   ;;; Control Flow

   ;; Lissp is simpler than Python. No control flow!
   ;; Use higher-order functions instead.

   ;; Loops!
   (any (map (lambda (c) (print c))
             "abc"))

   ;; Branches!
   ((.get (dict :
                y (lambda () (print "Yes!"))
                n (lambda () (print "Canceled.")))
          (input "enter y/n> ")
          (lambda () (print "Unrecognized input."))))

   ;;; Quote

   ;; Quotation prevents evaluation of invocations and identifiers.
   ;; Treating code as data the key concept in metaprogramming.
   (quote (print 1 2 3 : sep "-")) ; Just a tuple.
   (quote identifier) ; Just a string.

   ;;; Reader Macros

   'x ; Same as (quote x). Symbols are just quoted identifiers!
   '(print "Hi") ; Same as (quote (print "Hi"))

   ;; Template quote. (Like quasiquote, backquote, or syntax-quote.)
   `print ; 'builtins..print ; Raw identifiers get qualified.
   `foo ; '__main__..foo
   `(print "Hi") ; Code as data. Seems to act like quote.
   '`(print "Hi") ; But it's making a program to create the data.
   `(print ,(.upper "Hi")) ; Unquote interpolates.
   ;; You can interpolate to prevent qualification.
   `,'foo ; 'foo
   `(print ,@"abc") ; Splice unquote interpolates and unpacks.
   `(print ,@(.upper "abc"))
   `($#eggs $#spam $#bacon $#spam) ; Generated symbols
   `$#spam ; Gensyms help prevent name collisions in macroexpansions.

   _#"
   The discard macro _# omits the next form.
   It's a way to comment out code structurally.
   It's also useful for block comments like this one.
   "

   ;; Invoke any importable unary callable at read time.
   builtins..float#inf ; Create new literals!

   ;; The injection macro evaluates the next form
   ;; and puts the result directly in the Hissp.
   .#(fractions..Fraction 1 2) ; Fraction() is multiary.

   ;; Use a string to inject Python into the compiled output.
   ;; Use responsibly!
   (lambda (a b c)
     .#"(-b + (b**2 - 4*a*c)**0.5)/(2*a)"))

   ;;; Collections

   ;; Make tuples with a quote.
   '(1 2 3) ; (1, 2, 3)

   ;; You can interpolate with templates.
   `(,(operator..pow 42 0) ,(operator..add 1 1) 3) ; (1, 2, 3)

   ;; Be careful with quotes in templates!
   `("a" 'b c ,'d ,"e")
   ;; -> (('quote', 'a', {':str': True}), ('quote', '__main__..b'), '__main__..c', 'd', 'e')
   '(1 "a") ; (1, ('quote', 'a', {':str': True}))
   `(1 ,"a") ; (1, 'a')
   ;; Helper functions may be easier.
   ((lambda (: :* xs) xs) 0 "a" 'b :c) ; (0, 'a', 'b', ':c')
   (.__setitem__ (globals) entuple (lambda (: :* xs) xs))
   (entuple 0 "a" 'b :c) ; (0, 'a', 'b', ':c')

   ;; Convert tuples to other collection types.
   (list `(1 ,(operator..add 1 1) 2)) ; [1 2 3]
   (.__setitem__ (globals) enlist (lambda (: :* xs) (list xs)))
   (set '(1 2 3)) ; {1, 2, 3}
   (dict (zip '(1 2 3) "abc")) ; {1: 'a', 2: 'b', 3: 'c'}

   ;; Symbolic-keyed dicts via kwargs.
   (dict : + 0  a 1  b 2) ; {'xPLUS_': 0, 'a': 1, 'b': 2}

   ;; Mixed key types.
   (dict '((a 1) (2 b))) ; {'a': 1, 2: 'b'}
   ;; Interpolated.
   (dict `((,'+ 42) (,(operator..add 1 1) ,'b))) ; {'xPlus_': 42, 2: 'b'}
   (.__getitem__ _ '+) ; 42
   ;; Helper function
   (.__setitem__ (globals)
                 'endict
                 (lambda (: :* pairs)
                   .#"{k: next(it) for it in [iter(pairs)] for k in it}"))
   (endict 1 2  'a 'b) ; {1: 2, 'a': 'b'}

   ;; List, set, and dict literals are read in as a unit, like strings.
   ;; They may contain compile-time literals only--No interpolation!
   [1,2,3] ; [1, 2, 3]
   {1,2,3} ; {1, 2, 3}
   {'a':1,2:'b'} ; {'a': 1, 2: 'b'}
   ;; Nesting.
   [1,{2},{3:[4,5]},'six'] ; [1, {2}, {3: [4, 5]}, 'six']

   ;; Collections literals are a convenience for simple cases only!
   ;; To keep the grammar simple, they're restricted.
   ;; No double quotes, no spaces, no newlines, and no parentheses, even in nested strings.
   [1, 2] ; SyntaxError. No Spaces!
   [1,"2"] ; SyntaxError. No double quotes!
   [1,'2'] ; [1, '2']
   [1,'''2'''] ; [1, '2']
   [1,'2 3'] ; SyntaxError. No Spaces! Not even in strings.
   ;; Escapes work, though I find this hard to read.
   [1,'2\0403'] ; [1, '2 3'].
   ;; This is a little better.
   [1,'2\N{space}3'] ; [1, '2 3']

   ;; If this is too restrictive for your use case, use injection or constructors instead.
   .#"[1, '2 3']" ; [1, '2 3']
   (list `(1 ,"2 3")) ; [1, '2 3']

   ;;; Compiler Macros

   ;;; Basic Macros

   hissp.basic.._macro_.from-require

   define
   deftype
   defmacro
   let

   attach
   cascade
   ->
   ->>

   car
   cdr
   caar
   cdar
   cadr
   cddr

   if-else
   cond
   when
   when-not
   &&
   ||
   forany

   progn
   prog1


