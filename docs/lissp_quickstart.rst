.. Copyright 2020 Matthew Egan Odendahl
   SPDX-License-Identifier: Apache-2.0

.. TODO: sybil tests? ;: ;>>> ;...

Lissp Quick Start
=================

.. code-block:: Lissp

   ;;;; Lissp Quick Start

   ;; Lissp is a lightweight textual language representing the Hissp data
   ;; language. The Lissp reader converts Lissp code to Hissp syntax trees.
   ;; The Hissp compiler translates Hissp to a functional subset of Python.

   ;; This document is written like a .lissp file, demonstrating Lissp's
   ;; features with minimal exposition. Some familiarity with Python is
   ;; assumed. Familiarity with another Lisp dialect is not assumed, but
   ;; helpful. See the Hissp tutorial for more detailed explanations.

   ;; Follow along by entering these examples in the REPL. It will show you the
   ;; compiled Python, and evaluate it. Try variations that occur to you.

   ;;;; Installation

   ;; Install hissp with $ pip install hissp
   ;; Start the REPL with $ hissp
   ;; Quit with EOF or (exit).

   ;;;; Atoms

   ;;; singleton

   None                                   ;Same as Python.
   ...                                    ;Ellipsis

   ;;; boolean

   False                                  ;bool. Remember that bools are ints:
   True                                   ; 0 and 1.

   ;;; integer

   42                                     ;int
   0x10                                   ;16
   0o10                                   ;8
   0b10                                   ;2
   0b1111_0000_0000                       ;0xF00

   ;;; floating-point

   -4.2                                   ;float
   4e2                                    ;400.0
   -1.6e-2                                ;-0.016

   ;;; complex

   5j                                     ;imaginary
   4+2j                                   ;complex
   -1_2.3_4e-5_6-7_8.9_8e-7_6j            ;Very complex!

   ;;; symbols and strings

   object                                 ;Normal identifier.
   object.__class__                       ;Attribute identifier with dot. Same as Python so far.
   math.                                  ;Module identifier ends in a dot and imports it!
   math..tau                              ;Qualified identifier. Attribute of a module.
   collections.abc.                       ;Submodule identifier. Has package name.
   builtins..object.__class__             ;Qualified attribute identifier.
   object.__class__.__name__              ;Attributes chain.
   collections.abc..Sequence.__class__.__name__ ;All together now.

   :control-word                          ;Colon prefix. Similar to ":keywords" in other Lisps.

   'symbol                                ;Apostrophe prefix. Symbols represent identifiers.

   ;; Symbols munge special characters at read-time to valid Python identifiers.

   'Also-a-symbol!                        ;Alias for 'AlsoxH_axH_symbolxBANG_
   '𝐀                                     ;Alias for 'A (munges to unicode normal form KC)
   '+                                     ;'xPLUS_
   '->>                                   ;'xH_xGT_xGT_
   :->>                                   ;Control words don't represent identifiers, don't munge.

   'SPAM\ \"\(\)\;EGGS                    ;These would terminate a symbol if not escaped.
   '\42                                   ;'xDIGITxFOUR_2 Python identifiers can't start with digits.
   '\.                                    ;'xFULLxSTOP_
   '\\                                    ;'xBSLASH_
   '\a\b\c                                ;Escapes allowed, but not required here.

   "string"                               ;Double-quotes only!
   'string'                               ;'stringxQUOTE_ symbol.

   "string
   with
   newlines
   "                                      ;Same as "string\nwith\nnewlines\n". No triple quotes.

   "Say \"Cheese!\""                      ;Same backslash escape sequences as Python.

   b"bytes"                               ;Double-quotes only! Little 'b' only!
   b'bytes'                               ;NameError: name 'bxQUOTE_bytesxQUOTE_' is not defined

   b"bytes
   with
   newlines
   "                                      ;Same as b"bytes\nwith\nnewlines\n".

   ;;;; Calls

   (print :)                              ;"(" goes before the function name! Calls have a :.
   (print : :? 1  :? 2  :? 3  sep "-")    ;Arguments pair with a parameter name. No commas!
   (print 1 2 3 : sep "-")                ;Arguments left of the : implicitly pair with :?.
   (print 1 : :* "abc"  :? 2  :** (dict : sep "-")) ;Unpacking!
   (print "Hello, World!")                ;No : is the same as putting it last.
   (print "Hello, World!" :)

   (.upper "shout!")                      ;Method calls like Clojure. A ``self`` is required.
   (.float builtins. 'inf)                ;Method call syntax, but not technically a method.
   (builtins..float 'inf)                 ;Same effect as before, but not method syntax.

   (help float)                           ;Python's online help function is still available.
   (dir)                                  ;See the _macro_?
   (dir _macro_)
   (help _macro_.->>)                     ;Macros have docstrings and live in _macro_.

   ;;;; Lambda

   (lambda (x) x)                         ;Lambda invocations create functions.

   ;; Python parameter types are rather involved. Lambda does all of them.
   (lambda (: a :?  b :? :/               ;positional only
            c :?  d :?                    ;normal
            e 1  f 2                      ;default
            :* args  h 4  i :?  j 1       ;star args, key word
            :** kwargs)
     ;; Body. (Lambda returns empty tuple if body is empty.)
     (print (globals))
     (print (locals))                     ;side effects
     b)                                   ;last value is returned

   ;; Parameters left of the : are paired with :?. Like with calls, but the other side.
   (lambda (: :* a))                      ;A star args has to pair with the star, just like Python.
   (lambda (:* a))                        ;Not a star args! This is a kwonly! Ending : is implied.
   (lambda (: :* :?  a :?))               ;Same meaning as the previous line, but explicit.
   (lambda (a b : x None  y None))        ;Normal, and then with defaults.
   (lambda (:* a b : x None  y None))     ;Keyword, and then with defaults.

   ;; Some of these are abuse. But this kind of flexibility can make macros easier.
   (lambda (:))                           ;Explicit : is still allowed with no parameters.
   (lambda :)                             ;Thunk idiom.
   (lambda :x1)                           ;Control words are strings are iterable.
   (lambda b"")                           ; Parameters are not strictly required to be a tuple.
   ((lambda abc                           ;Three parameters.
      (print c b a))
    3 2 1)

   ;;;; Operators

   ;; Hissp is simpler than Python. No operators! Use function invocations instead.

   (operator..add 40 2)                   ;Addition.
   (.__setitem__ (globals) '+ operator..add) ;Assignment. We'll be using this later.
   (+ 40 2)                               ;No operators. This is still a function call!

   ;;;; Control Flow

   ;; Hissp is simpler than Python. No control flow! Use higher-order functions instead.

   (any (map (lambda (c) (print c))       ;Loops!
             "abc"))

   ((.get (dict :                         ;Branches!
                y (lambda () (print "Yes!"))
                n (lambda () (print "Canceled.")))
          (input "enter y/n> ")
          (lambda () (print "Unrecognized input."))))

   ;; Don't worry, macros make this much easier.

   ;;;; Quote

   ;; Quotation prevents evaluation of invocations and identifiers.
   ;; Treating code as data the key concept in metaprogramming.
   (quote (print 1 2 3 : sep "-"))        ;Just a tuple.
   (quote identifier)                     ;Just a string.
   (quote 42)                             ;Atoms evaluate to themselves.

   ;;;; Reader Macros

   'x                                     ;Same as (quote x). Symbols are just quoted identifiers!
   '(print "Hi")                          ;Same as (quote (print "Hi"))
   (lambda (: a ':?))                     ;Quoted things are just data.

   ;; Reader macros are metaprograms to abbreviate Hissp instead of representing it directly.

   ;;; template quote
   ;; (Like quasiquote, backquote, or syntax-quote.)

   `print                                 ;'builtins..print. Raw identifiers get qualified.
   `foo                                   ;'__main__..foo
   `(print "Hi")                          ;Code as data. Seems to act like quote.
   '`(print "Hi")                         ;But it's making a program to create the data.
   `(print ,(.upper "Hi"))                ;Unquote interpolates.

   ;; You can interpolate without qualification.
   `,'foo                                 ;'foo
   `(print ,@"abc")                       ;Splice unquote interpolates and unpacks.
   `(print ,@(.upper "abc"))
   `($#eggs $#spam $#bacon $#spam)        ;Generated symbols
   `$#spam                                ;Gensyms help prevent name collisions in macroexpansions.

   _#"
   The discard reader macro _# omits the next form.
   It's a way to comment out code structurally.
   It's also useful for block comments like this one.
   "

   ;; Invoke any importable unary callable at read time.
   builtins..float#inf                    ;Extensible literals!

   ;; Reader macros compose. Note the quote.
   'hissp.munger..demunge#xH_xGT_xGT_     ;'->>'
   ''x                                    ;('quote', 'x')
   '\'x                                   ;'xQUOTE_x'

   (print (.upper 'textwrap..dedent#"\
                  These lines
                  Don't interrupt
                  the flow."))

   ;; The "inject" reader macro evaluates the next form
   ;; and puts the result directly in the Hissp.
   .#(fractions..Fraction 1 2)            ;Fraction() is multiary.

   ;; Use a string to inject Python into the compiled output.
   (lambda (a b c)
     ;; Hissp may not have operators, but Python does.
     .#"(-b + (b**2 - 4*a*c)**0.5)/(2*a)")

   ;; Statement injections work at the top level only.
   .#"from operator import *"             ;All your operator are belong to us.

   ;; Injections are powerful. Use responsibly!

   ;;;; Collections

   ;;; templates and tuples

   '(1 2 3)                               ;tuple
   `(,(operator..pow 42 0) ,(+ 1 1) 3)    ;Interpolate with templates.
   `("a" 'b c ,'d ,"e")                   ;Careful with quotes in templates! Try it.
   '(1 "a")                               ;Recursive quoting.
   `(1 ,"a")

   ;; Helper functions may be easier than templates.
   ((lambda (: :* xs) xs) 0 "a" 'b :c)
   (.__setitem__ (globals) 'entuple (lambda (: :* xs) xs))
   (entuple 0 "a" 'b :c)

   ;;; other collection types

   (list `(1 ,(+ 1 1) 2))
   (set '(1 2 3))
   (dict (zip '(1 2 3) "abc"))

   (dict : + 0  a 1  b 2)                 ;symbolic keys
   (.__getitem__ _ '+)                    ;In the REPL, _ is the last result that wasn't None.

   (dict '((a 1) (2 b)))                  ;Mixed key types.
   (dict `((,'+ 42)
           (,(+ 1 1) ,'b)))               ;interpolated
   (.__getitem__ _ '+)

   .#"[1, 2, 3]"                          ;List from a Python injection.
   (.__setitem__ (globals)
                 'endict                  ;dict helper function
                 (lambda (: :* pairs)
                   ;; Injections work on any Python expression, even comprehensions!
                   .#"{k: next(it) for it in [iter(pairs)] for k in it}"))
   (endict 1 2  'a 'b)

   ;;; collection atoms

   .#[]                                   ;As a convenience, you can drop the quotes in some cases.
   []                                     ; And the reader macro!

   [1,2,3]                                ;List, set, and dict atoms are a special case
   {1,2,3}                                ; of Python injection. They read in as a single atom, so
   {'a':1,2:b'b'}                         ; they have compile-time literals only--No interpolation!
   [1,{2},{3:[4,5]},'six']                ;Nesting is allowed.

   ;; To keep the grammar simple, spaces, double quotes, parentheses, and semicolons
   ;; must be escaped with a backslash, like in symbols and identifiers.
   [1,\ 2]
   [1,\(2,3\)]
   [1,'2\ 3']                             ;Escapes are required even in nested strings.
   [1,\"2\"]
   [1,'2']
   [1,'''2''']                            ;Triple quotes are allowed, but newlines are not!
   ['''1\\n2''']                          ;['1\n2'] Double backslashes in collection atoms!

   ;; You can use the inject macro instead of escapes.
   .#"[1, '2 3']"                         ;Spaces are allowed.
   .#"[1, (2, 3)]"                        ;Parentheses are also allowed.

   ;; Constructors or helpers also work, and unlike atoms, they can interpolate.
   (list `(1 ,"2 3"))                     ;Remember templates make tuples, convert to lists.
   (.__setitem__ (globals) 'enlist (lambda (: :* xs) (list xs)))
   (enlist 1 "2 3")                       ;helper function

   _#"Even though they evaluate the same, there's a subtle compile-time difference
   between a collection atom and a string injection. This can matter because
   macros get all their arguments quoted."

   '[1,'''2\ 3''']                        ;[1, '2 3']
   '.#"[1,'''2 3''']"                     ;"[1,'''2 3''']"

   ;; But you can still get a real collection at compile time.
   '.#(eval "[1,'''2 3''']")              ;[1, '2 3']
   '.#.#"[1,'''2 3''']"                   ;[1, '2 3']

   ;;;; Compiler Macros

   _#"Macroexpansion happens at compile time, after the reader, so they also
   work in readerless mode, or with alternative Hissp readers other than Lissp.
   Macros get all of their arguments unevaluated (quoted) and the compiler
   inserts the resulting Hissp into that point in the program."

   ;; A function invocation using an identifier qualified with ``_macro_`` is a macroexpansion.
   (hissp.basic.._macro_.define SPAM "eggs") ;N.B. SPAM not quoted.
   SPAM                                   ;'eggs'

   ;; See the Hissp generated by the expansion by calling it like a method with all arguments quoted.
   ;; (Method syntax is never a macroexpansion.)
   (.define hissp.basic.._macro_ 'SPAM '"eggs")
   ;; ('operator..setitem', ('builtins..globals',), ('quote', 'SPAM'), ('quote', 'eggs', {':str': True}))

   ;; Unqualified invocations are macroexpansions if the identifier is in the current module's
   ;; _macro_ namespace. The REPL includes one, but .lissp files don't have one until you create it.
   (dir)
   (dir _macro_)
   (help _macro_.define)
   (define EGGS "spam")
   EGGS

   (setattr _macro_
            'triple
            (lambda (x)
              `(+ ,x (+ ,x ,x))))         ;Use a template to make code.
   (triple 4)                             ;12

   (define loud-number
     (lambda (x)
       (print x)
       x))
   (triple (loud-number 14))              ;N.B. Triples the *code*, not just the *value*.
   ;; 14
   ;; 14
   ;; 14
   ;; 42

   ;; Maybe the expanded code could only run it once?
   (setattr _macro_
            'oops-triple
            (lambda (x)
              `((lambda (: x ,x)          ;Expand to lambda to make a local variable.
                  (+ x (+ x x))))))
   (oops-triple 14)                       ;Don't forget that templates qualify symbols!
   ;; SyntaxError: invalid syntax

   ;; If you didn't want it qualified, that's a sign you should use a gensym instead:
   (setattr _macro_
            'once-triple
            (lambda (x)
              `((lambda (: $#x ,x)
                  (+ $#x (+ $#x $#x))))))
   (once-triple (loud-number 14))
   ;; 14
   ;; 42

   ;; Sometimes you really want a name captured, so don't qualify and don't generate a new symbol:
   (setattr _macro_
            'fnx
            (lambda (: :* body)
              `(lambda (,'X)              ;,'X instead of $#X
                 (,@body))))
   (list (map (fnx operator..mul X X) (range 6))) ;Shorter lambda! Don't nest them.

   ;; Recursive macro? (Multiary +)
   (setattr _macro_
            '+
             (lambda (first : :* args)
               (.__getitem__
                 `(,first ,`(operator..add ,first (+ ,@args)))
                 (bool args))))
   (+ 1 2 3 4)                            ;TypeError

   _#"The recursive + was qualified as __main__..+, not __main__.._macro_.xPLUS_.
   Recursive macro invocations require forward declaration or explicit qualification.
   Now that we have a _macro_.+, it will qualify properly when you run it again."

   ;; Same as before.
   (setattr _macro_
            '+
             (lambda (first : :* args)
               (.__getitem__
                 `(,first ,`(operator..add ,first (+ ,@args)))
                 (bool args))))
   (+ 1 2 3 4)                            ;10

   (setattr _macro_ '* None)              ;Forward declaration.
   (setattr _macro_
            '*
             (lambda (first : :* args)
               (.__getitem__
                 `(,first ,`(operator..mul ,first (* ,@args)))
                 (bool args))))
   (* 1 2 3 4)                            ;24

   ;; Macros only work as invocations, not arguments!
   (functools..reduce * '(1 2 3 4))       ;NameError: name 'xSTAR_` is not defined.
   (functools..reduce (lambda (x y)
                        (* x y))
                      '(1 2 3 4))         ;24

   ;; It's possible to have a macro shadow a global. They live in different namespaces.
   (+ 1 2 3 4)                            ;10 (_macro_.+, not the global.)
   (functools..reduce + '(1 2 3 4))       ;10 (global function, not the macro!)
   (dir)                                  ;Has xPLUS_, but not xSTAR_.
   (dir _macro_)                          ;Has both.

   _#"hissp can run a .lissp file as __main__.
   You cannot import .lissp directly. Compile it to .py first."

   ;; Finds spam.lissp & eggs.lissp in the current package and compile them to spam.py & eggs.py
   (os..system "echo (print \"Hello World!\") > eggs.lissp")
   (os..system "echo (print \"Hello from spam!\") (.__setitem__ (globals) 'x 42) > spam.lissp")
   (hissp.reader..transpile __package__ 'spam 'eggs)

   spam..x                                ;Side effects happen upon both compilation and import!
   ;; Hello from spam!
   ;; 42

   spam..x                                ;42
   (importlib..import_module 'eggs)       ;Hello, World!

   ;;;; Basic Macros

   _#" The REPL comes with some basic macros defined in hissp.basic.
   By default, they don't work in .lissp files unqualified. But you can add
   them to the current module's _macro_ namespace. The compiled output from
   these does not require hissp to be installed."

   ;;; macro import

   (hissp.basic.._macro_.from-require
     (hissp.basic define defmacro let))   ;Add unqualified macros to the current module.
   (require-as hissp.basic.._macro_.progn begin) ;Add an unqualified macro under a new name.

   ;;; definition

   (define answer 42)                     ;Add a global.
   (deftype Point2D (tuple)
     __doc__ "Simple pair."
     __new__
     (lambda (cls x y)
       (.__new__ tuple cls `(,x ,y))))
   (Point2D 1 2)                          ;(1, 2)

   ;; Define a function in the _macro_ namespace.
   ;; Creates the _macro_ namespace if absent.
   (defmacro triple (x)
     `(+ ,x ,x ,x))

   (let (x 1                              ;Create locals.
         y 5)                             ;Any number of pairs.
     (print x y)                          ;1 5
     (let (x 10
           y (+ x x))                     ;Not in scope until body.
       (print x y))                       ;10 2
     (print x y))                         ;1 5

   ;;; configuration

   (define ns (types..SimpleNamespace))
   (attach ns + : x 1  y 5)
   ns                                     ;namespace(x=1, xPLUS_=<built-in function add>, y=5)

   (cascade []
     (.append 1)
     (.append 2)
     (.append 3))                         ;[1, 2, 3]

   ;;; threading

   (-> "world!"                           ;Thread-first
       (.title)
       (->> (print "Hello")))             ;Thread-last

   ;;; linked-list emulation

   ;; These really could be functions, but their expansion is small enough to inline.

   (car "abcd")                           ;'a'
   (cdr "abcd")                           ;'bcd'
   (cadr "abcd")                          ;'b'
   (cddr "abcd")                          ;'cd'
   (caar ['abc','xyz'])                   ;'a'
   (cdar ['abc','xyz'])                   ;'bc'

   ;;; control flow

   ;; Hissp has no control flow, but you can build them with macros.

   (any-for x (range 1 11)                 ;imperative loop with break
     (print x : end " ")
     (operator..not_ (operator..mod x 7)))
   ;; 1 2 3 4 5 6 7 True

   (if-else (operator.eq (input) 't)      ;ternary conditional
     (print "Yes")
     (print "No"))

   (let (x (ast..literal_eval (input)))
     ;; Multi-way branch.
     (cond (operator..lt x 0) (print "Negative")
           (operator..eq x 0) (print "Zero")
           (operator..gt x 0) (print "Positive")
           :else (print "Not a number"))
     (when (operator..eq x 0)             ;Conditional with side-effects, but no alternative.
       (print "In when")
       (print "was zero"))
     (when-not (operator..eq x 0)
       (print "In when-not")
       (print "wasn't zero")))

   ;; Shortcutting logical and.
   (&& True True False)                   ;False
   (&& False (print "oops"))              ;False

   ;; Shortcutting logical or.
   (|| True (print "oops"))               ;True

   ;;; side effect

   (prog1                                 ;Sequence for side effects evaluating to the first.
     (progn (print 1)                     ;Sequence for side effects evaluating to the last.
            3)
     (print 2))
   ;; 1
   ;; 2
   ;; 3

.. TODO: nested templates? Show macro not working on injection?