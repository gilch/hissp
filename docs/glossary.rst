.. Copyright 2024 Matthew Egan Odendahl
   SPDX-License-Identifier: CC-BY-SA-4.0

Glossary
########

.. glossary::
   :sorted:

   top level
   top-level form
      A form not nested inside another form,
      or the location of such a form.
      "Top" here means the top of the syntax tree rather than the top of the file.
      Each top-level form is a compilation unit.
      A macro defined in a top-level form cannot affect any other
      `subform` in the same top-level form,
      because by the time it exists,
      the top-level form has already been compiled.
      (However, the reader must run any `tag`s, which can have arbitrary effects,
      before giving the compiler the form.)
      `Injection` of a Python statement is only valid at the top level.

   doorstop
      A `discarded item` used to "hold open" a bracket trail
      or avoid a ``))`` in line.
      Any discarded item used this way is functionally a doorstop,
      but, in Lissp, the typical style starts with ``_#/``
      and may continue with a label of what form the next ``)`` is closing,
      like ``_#/foo``, similar to XML tags.

   abstract syntax tree
   ast
      An intermediate tree data structure used by most compilers after
      parsing a programming language.
      The AST stage of Lissp is Hissp,
      and Lissp is a pretty direct representation of it.

   hissp
      The project at `<https://github.com/gilch/hissp>`_.
      The package produced by the project.
      The language of Python data structures used by the project,
      which :mod:`hissp.compiler` can transpile into executable Python code.
      The Python data structures encoding this language:
      a `form`, or a series of them.
      This is also the `AST` stage of `Lissp`,
      a programming language implemented in terms of Hissp.

   repl
   read-evaluate-print loop
   read-eval-print loop
   subrepl
      The `LisspREPL`,
      Lissp's interactive interpreter shell, layered on Python's.
      (Or a similar language shell.)
      Reads Lissp input, compiles it to Python,
      and passes it to Python's shell for evaluation and printing,
      then repeats.
      Used for inspection, online help, interactive development, and debugging.
      A subREPL is just a REPL started from within a REPL,
      analogous to a subshell.

   token
      A lexical unit of Lissp.
      This is how the `reader` chunks Lissp in preparation for parsing.
      Some are considered implementation details,
      but a Lissp programmer should be able to mentally parse the language.

   object token
      A type of `token` which by itself results in a `parsed object`
      when passed to the Lissp parser.
      These are what the reader considers nouns.
      Typically emitted as an `atom`,
      but may instead be arguments to a `tagging token`.

   parsed object
      The result of parsing an `object token`;
      or a `tagging token` with its arguments (except the `discard tag`);
      or a balanced pair of parentheses (open ``(`` and close ``)`` tokens),
      with their contents (if any).
      Typically emitted as a `form`,
      but may instead be arguments to a `tagging token`.

   tagging token
      A type of `token` that, when read,
      consumes one or more `parsed object`\ s and results in a `parsed object`.
      These can be thought of as reader adjectives.
      They serve a function similar to reader macros in other Lisps,
      but operate on the `parsed object` stream (parser level),
      not the raw character stream (lexer level).
      Think Clojure/EDN tags, not Common Lisp reader macros.

   special tag
      One of the built-in unary `tagging token`\ s
      treated as a `special case<Parser>` in the `reader`.

   comment token
      An `object token` consisting of one or more lines,
      possibly indented with spaces,
      each starting with a semicolon (``;``) character.
      Comment tokens read as `hissp.reader.Comment` instances,
      a type that is normally discarded by the reader.
      However, they can still be arguments for a `tagging token`.

   unicode token
      An `object token` that begins and ends with a quotation mark (``"``) character.
      They may contain newline characters like Python's triple-quoted string literals,
      as is typical of Lisps.
      Internal quotation marks must be escaped with a preceding reverse solidus
      (``\``) character. It reads as a `string literal fragment`, specifically,
      a `str atom` containing a Python string literal wrapped in parentheses.

   str atom
      An `atom` of type `str`. Usually represents a `Python fragment`.
      If it starts with a colon (``:``), it is a `control word`.
      May contain a `module handle`.

   string literal fragment
      A `Python fragment` which `ast.literal_eval`
      would evaluate to an object of type `str`.
      Not all `str atom`\ s are string literal fragments;
      it must contain a Python string literal expression.
      `is_string_literal` tests for string literal fragments.

   hissp string
      A `form` or `parsed object` which would directly represent a string in Hissp,
      if evaluated on its own.
      All `string literal fragment`\ s are Hissp strings.
      A `quote`\ d `str atom` is also a Hissp string.
      `is_hissp_string` tests for Hissp strings.

   atom
      A `form` that is either the empty tuple ``()`` or not of type `tuple`.
      Atoms are the leaf elements of Hissp's syntax trees,
      while non-empty tuples are the nodes.
      `is_node` tests for the non-leaves, so its negation tests for atoms.

   form
      An object meant for evaluation;
      a Hissp expression for passing to the Hissp compiler.

   subform
      A `form` nested inside a tuple form; a Hissp subexpression.
      An (e.g.) `params tuple` isn't a `form`, so it's not a subform either,
      but a default argument inside it would be.
      Similarly, macro arguments don't necessarily count as subforms.

   special form
      A `form` special-cased `in the compiler <hissp.compiler.Compiler.special>`.
      These are tuples beginning with either a ``quote`` or ``lambda`` `str atom`.
      They look like function calls but act more like macros,
      in that arguments are not all evaluated first.
      While a `control word` is a `form`
      and can have special interpretations in certain contexts,
      they are not considered special forms.
      `module handle`\ s also have a processing rule in the compiler,
      but aren't considered special forms.

   params
   params tuple
   params symbol
      The first argument to the ``lambda`` `special form`.
      It represents the lambda parameters.
      Typically either a tuple or a `str atom`,
      but other iterables can work.
      Also a `macro` argument that
      becomes the whole params argument in a lambda expansion,
      such as the first argument to `let-from<letQzH_from>`
      or `any*map<anyQzSTAR_map>`.
      The equivalent concept is called the “lambda list” in Common Lisp,
      and the “params vector” in Clojure,
      but Hissp is made of tuples,
      not linked-lists or vectors,
      hence “params tuple” when written with a tuple.

   standard
   nonstandard
      The standard language is a disciplined subset with full generality.
      Standard (`readerless mode`) Hissp uses `str atom`\ s only for
      `control word`\ s and `symbol`\ s
      (which include imports and attribute access)
      and avoids other `Python injection`\ s.
      Standard Lissp also uses `str atom`\ s for `string literal fragment`\ s.
      (Standard readerless mode instead compiles string literals exclusively
      via the quote `special form`, or nested in `set`, `dict`, or `list` `atom`\ s.)
      Other Python injections are considered nonstandard.
      Nonstandard constructions should be used sparingly and with care.
      Metaprograms are not necessarily expected to handle nonstandard Python injections,
      because that would require processing the much more complicated language
      of Python expressions, but not all nonstandard injections are problematic.
      The bundled tags and macros mostly avoid nonstandard injections in expansions,
      but (with the notable exception of `mix`)
      allow them where they would be no worse than an opaque
      `fully-qualified identifier`,
      or in a few cases where the user writes part of the injection.
      Standard Hissp also avoids importing the ``hissp`` package outside of
      metaprograms (and direct helpers not otherwise called) to preserve the
      `standalone property`.
      Standard atom types are those the compiler has a literal notation for.
      Use of nonstandard types can result in a `pickle expression` or a crash
      during compilation (if the atom is unpickleable).

   injection
      Either a `Python injection` or a `Hissp injection`, depending on context.

   python injection
      The technique of writing a `Python fragment`
      rather than allowing the Hissp machinery to do it for you,
      or the fragments so used or the `fragment atom` containing one.
      A `text macro` works via Python injection.
      Injection is discouraged because it bypasses a lot of Hissp's machinery,
      and is opaque to code-walking macros,
      making them less useful or risking errors.
      However, the compiler only targets a subset of Python expressions.
      Injection transcends that limitation.
      Injection of identifiers is considered `standard` in Hissp,
      so is not discourarged.
      A Lissp `Unicode token` reads as a `string literal fragment`,
      rather than as a `quote`\ d `str atom`,
      making them an example of injection as well.
      This usage is `standard` in Lissp.

   hissp injection
      Any `atom` of `nonstandard` type (or the use thereof),
      i.e., anything the compiler doesn't have a literal notation for,
      which it would have to attempt to emit as a `pickle expression`.
      This includes instances of standard types without a literal notation
      (e.g., `float` is a standard type, but `math.nan` has no literal)
      or collections containing nonstandard elements or cycles.
      A `macro expansion` may be an injection.
      Besides macro expansions, in readerless mode,
      this almost always requires the use of non-literal notation,
      (i.e., notation not accepted by `ast.literal_eval`).
      In Lissp, this almost always requires the use of a `tagging token`.
      (A notable exception is a float literal big enough in magnitude to overflow to
      ``inf`` or ``-inf``, e.g., ``1e999``.
      The compiler still considers this nonstandard because that's not its `repr`,
      and would emit a `pickle expression` for it.)
      Basic container types containing only standard elements do not count as injections,
      because the compiler has a notation for them,
      even though Lissp doesn't.

   pickle expression
      The compiler's final fallback emission when it doesn't have a literal notation for an `atom`.
      It's an import of `pickle.loads` passed a
      `bytes` literal containing a serialization of the object.
      Evaluating it should result in an equivalent object.

   fragment
      A `fragment token`, `fragment atom`, or `Python fragment`, depending on context.

   python fragment
      A piece of Python code, especially one emitted by the compiler.
      Typically a Python expression, but not necessarily anything complete.
      The compiler assembles and emits fragments to produce compiled output.

   fragment atom
      A `str atom` that is not a `control word`,
      especially if it does not simply contain an identifier or literal.
      So called because the compiler's usual interpretation
      is to emit the contents directly
      (making the contents a `Python fragment`),
      although there is a preprocessing step for imports (see `module handle`).

   fragment token
      An `object token` that begins and ends with a vertical line (``|``) character.
      Internal vertical lines must be escaped as two vertical lines (``||``).
      It reads directly as a `str atom`,
      which typically becomes a `fragment atom`, hence the name.
      In the case that the fragment token begins with ``|:``,
      it becomes a `control word` instead.

   control token
      An `object token` that begins with a colon ``:`` character.
      It reads as a `control word`, a type of `str atom`.

   control word
      A `str atom` that begins with a colon ``:`` character.
      These normally compile directly to Python string literals
      with the same contents (including the leading colon),
      but may have special interpretation in some contexts.
      (Both Python and other Lisps use the term "`keyword`",
      but they mean `different things<tut-keywordargs>`,
      including Lisp's equivalent concept.)
      `is_control` tests for control words.

   bare token
      An `object token` without the initial character marking it as a
      `comment token` (``;``), `Unicode token` (``"``), `fragment token` (``|``),
      or `control token` (``:``).
      It is either a `literal token`, or failing that, a `symbol token`.

   literal token
      A `bare token` that is a valid Python literal,
      as determined by `ast.literal_eval`, but not of a container type.
      It reads as an `atom` of that type.

   symbol token
      A `bare token` that is not a `literal token`.
      These are subject to `munging` and read as a `symbol`,
      a type of `str atom` used for identifiers.

   symbol
      A `module handle` or a `Python fragment` containing an
      `identifier<str.isidentifier>`.
      (Possibly with `qualification`.)
      A symbol is always a `str atom`.
      `is_symbol` tests for symbols.
      Some identifiers are `reserved<keyword.iskeyword>` in Python and
      can't be used as variable/attribute names
      (`not`, `None`, `class`, etc.) These still count as symbols.

   munging
      The process of replacing characters invalid in a Python identifier
      with `Quotez` equivalents.
      Primarily used to make a `symbol token` into a `str atom`
      containing a valid Python identifier (a `symbol`).
      The munging machinery is in :mod:`hissp.munger`.

   quotez
      The `munger`'s character replacement format.
      It's the character's Unicode name wrapped in ``Qz`` and ``_``.
      (Spaces become ``x`` and hyphens become ``h``.)
      Characters without names use their hexadecimal ordinals instead.
      Some ASCII characters use the short names from `TO_NAME` instead.
      The `gensym` hashes and ``hissp.compiler.MAYBE`` use the same
      ``Qz{}_`` wrapper.

   kwarg token
      A single-argument `tagging token` ending in an equals sign (``=``)
      and read as a `hissp.reader.Kwarg` instance.
      Used as keyword arguments for a `tag`.

   stararg token
      One of ``*=`` or ``**=``. A `special tag` which reads as a
      `hissp.reader.Kwarg` instance. Used as unpacking positional
      or keyword arguments (respectively) to a `tag`.

   tag
   tag token
   hash tag
   module-local tag
   fully-qualified tag
      A `tagging token` that ends in one or more number sign (``#``) characters
      (also known as "hash" characters,
      making these "hash tags" when distinguishing them from other `tagging token`\ s.)
      If it includes a `module handle` part, it's a fully-qualified tag.
      (Any callable accessible this way can be applied as a tag.
      E.g. ``builtins..str.format##``, ``fractions..Fraction#``,
      ``textwrap..dedent#``, etc.)
      If it doesn't include one,
      it refers to a module-local `metaprogram` stored in the module's
      ``_macro_`` namespace.
      Tags usually need to be pure or at least idempotent,
      as the `REPL` or similar tooling may have to make multiple attempts
      at applying them.

   metaprogram
   metaprogramming
      A metaprogram is a program that writes code.
      Typically, this means the callable referred to by `tag` or `macro` syntax,
      or helper functions used for abbreviations in `readerless mode`.
      But the compiler itself is also a kind of metaprogram.
      Metaprogramming is the process of writing metaprograms.

   readerless mode
      A representation of `form`\ s in the Python language using mostly literals.
      Hissp written this way does not require the use of a reader,
      hence it's the "readerless" mode of writing Hissp.

   template quote
   soft quote
      :literal:`\``. A `special tag` starting a `template`.
      The equivalent concept is called a "quasiquote" or "syntax quote" in other Lisps.

   template
      A `template quote` and its argument,
      a domain-specific language (DSL) for creating a `form`,
      supporting tuple interpolation, `gensym`\ s,
      and automatic `full qualification`.
      Can also be used for data, not just code.
      Typically used in the definition of a `macro function`.

   qualifier
   qualification
   partial qualification
   partially qualified identifier
      A `str atom` containing a ``.``-separated identifier path
      prepended to an identifier is a qualified identifier.
      Compiles to Python attribute access syntax.
      If this is the path from the containing module, the result is a `qualified name`.
      If this includes a `module handle`, it's `full qualification`,
      if qualification is not full, it's partial.
      A `qualified name` is partial qualification,
      but partial qualification is not necessarily a `qualified name`,
      because the path may start from some namespace other than the module globals.
      The qualifier part is everything but the last segment.
      Qualification is the process of adding a qualifier
      or the state of having a qualifier.
      `hissp.macros._macro_.alias` produces a `tag` to abbreviate a qualifier.

   unqualified
      An identifier without a `qualifier`. An unqualified `tag` is only
      valid if it's available as an attribute in the current module's
      ``_macro_`` namespace, and similarly for an unqualified `macro`.
      A unqualified variable is valid if it's in the `builtins` module,
      a global of the current module,
      or a variable in the current lexical scope.

   module handle
      A `str atom` containing a ``.``-separated path ending in a ``.``,
      representing an import path for a module.
      Any segments before the module name are package names.
      E.g., ``foo.bar.baz.`` or ``foo.``.
      The compiler processes it into a `__import__` expression before emission.

   full qualifier
   full qualification
   fully-qualified identifier
      A `module handle` prepended to a `qualified name` and separated with a ``.``
      is a fully-qualified identifier;
      it's the path of attribute access from the full import path of the module,
      which is enough to get a reference to the object from anywhere.
      Compiles to attribute access from an `__import__` expression.
      E.g., ``foo.bar.baz..spam.eggs.bacon``, or, with fewer segments, ``foo..spam``.
      The full qualifier part is everything but the last segment,
      commonly used as an argument to `alias<hissp.macros._macro_.alias>`.
      Full qualification is the process of adding a full qualifier
      or the state of having a full qualifier.

   unquote
      ``,``. A `special tag` only valid in a `template`.
      Its argument is directly interpolated rather than quoted first.

   splice
   splicing unquote
      ``,@``. A `special tag` only valid in a `template`.
      Its argument is interpolated and unpacked rather than quoted first.

   quote
   hard quote
      ``'``. A `special tag` abbreviating the ``quote`` `special form`.
      Sometimes called a "hard quote" to distinguish it from the `template quote`.

   inject
   inject tag
      ``.#``. A `special tag` which evaluates the next
      `parsed object` and returns its result.
      So named because it's typically used to make an `injection`,
      although it can result in an object of any type.

   discard tag
   discarded item
      ``_#``. A `special tag`
      used to structurally disable parts of code during development,
      for commentary, or as a `doorstop`.
      The argument to a discard tag is the discarded item.
      It is unique among `tagging token`\ s in that it doesn't return a
      `parsed object` at all.
      Although a `tag` could achieve a similar effect by returning a
      (normally discarded) `hissp.reader.Comment` instance
      or by consuming two `parsed object`\ s and returning the second one unchanged,
      the discard tag (like all `special tag`\ s) is unary,
      making it applicable to the last (or only) element in a tuple
      (such as a `doorstop`),
      and a discarded item cannot be an argument to another tagging token,
      unlike a `Comment` instance, which allows its use for commentary
      between a `tagging token` and one of its arguments.

   gensym tag
      ``$#``. A `special tag` for creating a `gensym`. Only valid in a `template`.
      Prepends a `gensym hash` to its argument, or replaces ``$`` characters with it.

   gensym
   gensym hash
      A generated `symbol`. These are produced by the `gensym tag`.
      A gensym hash is unique to the template it was created in.
      This prevents accidental name collisions in `macro expansion`\ s.
      A gensym hash is mostly used for local variables because
      they can't be disambiguated with a `full qualifier`.

   macro expansion
   expansion
      The process of `invoking` a `macro`, or the resulting `form`.

   macro
      A `macro function` or `macro form`, depending on context.

   macro function
      A `metaprogram` meant to run at compile time.
      A callable attribute of a ``_macro_`` namespace.

   macro form
      A `form` which represents some other `form`,
      called its `expansion`.
      Compilation `invoke`\ s a `macro` to make the substitution.

   invocation
   invoke
   invoking
      A tuple `form` that looks like a function call is an invocation.
      May actually compile to a run-time function call,
      or may instead be a `special form` or `macro form`,
      which calls a `macro` at compile time.
      Or the process of making such a call.

   read time
      The phase before compilation proper that translates Lissp to Hissp:
      when the `reader` runs and when `tagging token`\ s are activated.

   text macro
      A `macro` that `expands <expansion>` to a `str atom`
      instead of some other `form`,
      especially if the `str atom` doesn't simply contain a string literal
      or (possibly qualified) identifier.
      Effectively, they return Python code,
      rather than Hissp,
      which makes them opaque to Hissp `metaprogramming`,
      like pre-expanding, code-walking macros.

   anaphor
   anaphoric macro
      An anaphoric macro creates one or more lexical (local)
      variable bindings without explicitly naming them.
      Such a bound name is called an anaphor.

   standalone property
      When the compiled Python output of Hissp doesn't depend on the ``hissp`` package,
      it can run in a Python environment that doesn't have ``hissp`` installed.
      Hissp was designed for this,
      but it can be lost by adding a ``hissp`` import explicitly.
      Using Hissp's `metaprogramming` helpers only in metaprograms
      (or in metaprogramming helper functions only called by metaprograms)
      is fine because metaprograms only run at compile time (or `read time`),
      so they won't crash at run time even when ``hissp`` cannot be imported.
      Forgetting to remove or disable import of `transpile`
      used in main or a package ``__init__``
      is another way the standalone property can be lost.

   eof
      `End-of-file <https://en.wikipedia.org/wiki/End-of-file>`_.
      In most Unix terminals, use a :kbd:`Ctrl+D`,
      or :kbd:`Ctrl+Z Enter` in Windows.
      Quits a `subREPL` without also terminating the Python session,
      unlike ``(exit)``,
      and works similarly in most shells.

..  LocalWords:  Lissp str Hissp gensym readerless
