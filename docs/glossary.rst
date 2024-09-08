.. Copyright 2024 Matthew Egan Odendahl
   SPDX-License-Identifier: CC-BY-SA-4.0

Glossary
########

.. glossary::
   :sorted:

   token
      A lexical unit of Lissp.
      This is how the `reader` chunks Lissp in preparation for parsing.
      Some are considered implementation details,
      but a Lissp programmer should be able to mentally parse the language.

   object token
      A type of `token` which by itself results in a `parsed object`
      when passed to the Lissp parser.
      These are what the reader considers nouns.
      Typically emitted as `atom`\ s,
      but may instead be arguments to a `tagging token`.

   parsed object
      The result of parsing an `object token`;
      or a `tagging token` with its arguments;
      or a balanced pair of parentheses (open ``(`` and close ``)`` tokens),
      with their contents (if any).
      Typically emitted as `form`\ s,
      but may instead be arguments to a `tagging token`.

   tagging token
      A type of `token` that, when read,
      consumes one or more `parsed object`\ s and results in a `parsed object`.
      These can be thought of as reader adjectives.

   special tag
      One of the built-in unary `tagging token`\ s
      treated as a special case in the reader.

   comment token
      An `object token` consisting of one or more lines,
      possibly indented with spaces,
      each starting with a semicolon (``;``) character.
      Comment tokens read as `hissp.reader.Comment` instances,
      a type that is normally discarded by the reader.
      However, they can still be arguments for `tagging token`\ s

   unicode token
      An `object token` that begins and ends with a quotation mark (``"``) character.
      They may contain newline characters like Python's triple-quoted string literals,
      as is typical of Lisps.
      Internal quotation marks must be escaped with a preceding reverse solidus
      (``\``) character. These read as `str atom`\ s containing
      a Python string literal wrapped in parentheses.

   str atom
      An `atom` of type `str`. Usually represents a `fragment` of Python code.
      If it starts with a colon (``:``), it is a `control word`.
      May contain a `module handle`.

   string literal fragment
      A `fragment` which `ast.literal_eval` would evaluate to an object of type `str`.
      Not all `str atom`\ s are string literal fragments;
      It must contain a Python string literal expression.
      `hissp.reader.is_string_literal` tests for string literal fragments.

   hissp string
      A `form` or `parsed object` which would directly represents a string in Hissp,
      if evaluated on its own.
      All `string literal fragment`\ s are Hissp strings.
      A `quote`\ d `str atom` is also a Hissp string.
      `hissp.reader.is_hissp_string` tests for Hissp strings.

   atom
      A `form` that is not an instance of `tuple`.
      (Exception: the empty tuple ``()`` can be considered an atom for most purposes,
      even though it is an instance of `tuple`.)

   form
      An object meant for evaluation;
      a Hissp expression for passing to the Hissp compiler.

   special form
      A `form` special-cased `in the compiler <hissp.compiler.Compiler.special>`.
      These are tuples beginning with either a ``quote`` or ``lambda`` `str atom`.
      They look like function calls but act more like macros,
      in that arguments are not all evaluated first.
      While `control word`\ s are `form`\ s
      and can have special interpretations in certain contexts,
      they are not considered special forms.
      `module handle`\ s also have a processing rule in the compiler,
      but aren't considered special forms.

   injection
      Either a `Python injection` or a `Hissp injection`, depending on context.

   python injection
      The technique of writing `Python fragment`\ s
      rather than allowing the Hissp machinery to do it for you,
      or the `fragment`\ s themselves or the `fragment atom`\ s
      containing them.
      `text macro`\ s work via Python injection.
      Injection is discouraged because it bypasses a lot of Hissp's machinery,
      and is opaque to code-walking macros,
      making them less useful or risking errors.
      However, the compiler only targets a subset of Python expressions.
      Injection transcends that limitation.
      Injection of identifiers is considered standard in Hissp,
      so is not discourarged.
      Lissp's `Unicode token`\ s read as `string literal fragment`\ s,
      rather than as `quote`\ d `str atom`\ s,
      making them an example of injection as well.
      This usage is standard in Lissp.

   hissp injection
      Any `atom` of non-standard type (or the use thereof),
      i.e., anything the compiler doesn't have a literal notation for,
      which it would have to attempt to emit as a `pickle expression`.
      This includes instances of standard types without a literal notation,
      e.g., `math.nan` or collections containing nonstandard elements or cycles.
      In readerless mode, this almost always requires the use of non-literal notation,
      (i.e., notation not accepted by `ast.literal_eval`).
      In Lissp, this almost always requires the use of a `tagging token`.
      (a notable exception is a float literal big enough in magnitude to overflow to ``inf`` or ``-inf``,
      e.g., ``1e999``.
      The compiler still considers this nonstandard because that's not its `repr`,
      and would emit a `pickle expression` for it.)

   pickle expression
      The compiler's final fallback emission when it doesn't have a literal notation for an `atom`.
      It's an import of `pickle.loads` passed a `bytes` literal containing a serialization of the object.
      Evaluating it should result in an equivalent object.

   fragment
   python fragment
      A piece of Python code, especially one emitted by the compiler.
      Typically a Python expression, but not necessarily anything complete.
      The compiler assembles and emits fragments to produce compiled output.

   fragment atom
      A `str atom` that is not a `control word`,
      especially if it does not simply contain an identifier or literal.
      So called because the compiler's usual interpretation is to emit the contents directly,
      although there is a preprocessing step for `module handle`\ s.

   fragment token
      An `object token` that begins and ends with a vertical line (``|``) character.
      Internal vertical lines must be escaped as two vertical lines (``||``).
      These read directly as `str atom`\ s,
      which typically become a `fragment atom`, hence the name.
      Can become a `control word` in the case that the fragment token begins with ``|:``.

   control token
      An `object token` that begins with a colon ``:`` character.
      These read as `control word`\ s.

   control word
      A `str atom` that begins with a colon ``:`` character.
      These normally compile directly to Python string literals
      with the same contents (including the leading colon),
      but may have special interpretation in some contexts.

   bare token
      An `object token` without the delimiters marking it as a
      `comment token` (``;``), `Unicode token` (``"``), `fragment token` (``|``),
      or `control token` (``:``).
      These are either `literal token`\ s, or failing that, `symbol token`\ s.

   literal token
      A `bare token` that is a valid Python literal,
      as determined by `ast.literal_eval`, but not of a container type.
      These read as `atom`\ s of that type.

   symbol token
      A `bare token` that is not a `literal token`.
      These are subject to `munging` and read as `str atom`\ s.

   munging
      The process of replacing characters invalid in a Python identifier
      with "Quotez" equivalents.
      Primarily used to make a `symbol token` into a `str atom`
      containing a valid Python identifier.
      The munging machinery is in :mod:`hissp.munger`.

   kwarg token
      A single-argument `tagging token` ending in an equals sign (``=``)
      and read as a `hissp.reader.Kwarg` instance.

   stararg token
      One of ``*=`` or ``**=``. A `special tag` which read as a
      `hissp.reader.Kwarg` instance.

   tag
   tag token
   hash tag
   module-local tag
   fully-qualified tag
      A `tagging token` that ends in one or more number sign (``#``) characters
      (also known called "hash" characters,
      making these "hash tags" when distinguishing them from other `tagging token`\ s.)
      If it includes a `module handle` part, it's a fully-qualified tag.
      Any callable accessible this way can be applied as a tag.
      E.g. ``builtins..str.format##``, ``fractions..Fraction#``,
      ``textwrap..dedent#``, etc.
      If it doesn't,
      it refers to a module-local `metaprogram` stored in the module's
      ``_macro_`` namespace.

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
      a domain-specific language (DSL) for creating `form`\ s,
      supporting tuple interpolation, `gensym`\ s,
      and automatic `full qualification`.
      Can also be used for data, not just code.
      Typically used in the definition of a `macro function`.

   qualifier
   qualification
   partial qualification
   partially qualified identifier
      A `str atom` containing a dot-separated identifier path
      prepended to an identifier is a qualified identifier.
      Compiles to Python attribute access syntax.
      If this is the path from the containing module, the result is a `qualified name`.
      If this includes a `module handle`, it's `full qualification`,
      if qualification is not full, it's partial.
      A `qualified name` is partial qualification,
      but partial qualification is not necessarily a `qualified name`,
      since the path may start from some namespace other than the module globals.
      The qualifier part is everything but the last segment.
      Qualification is the process of adding a qualifier
      or the state of having a qualifier.

   module handle
      A `str atom` containing a dot-separated path ending in a dot,
      representing an import path for a module.
      Any segments before the module name are package names.
      E.g., ``foo.bar.baz.`` or ``foo.``.
      The compiler processes it into a `__import__` expression before emission.

   full qualifier
   full qualification
   fully-qualified identifier
      A `module handle` prepended to a `qualified name` and separated with a dot
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

   quote
   hard quote
      ``'``. A `special tag` abbreviating the ``quote`` `special form`.
      Sometimes called a "hard quote" to distinguish it from the `template quote`.

   inject tag
      ``.#``. A `special tag` which evaluates the next `parsed object`.
      So named because it's typically used to make a `hissp injection`.

   discard tag
      ``_#``. A `special tag` that consumes the next `parsed object`,
      but doesn't return one.
      Used to structurally disable parts of code during development,
      or for commentary.

   gensym tag
      ``$#``. A `special tag` only valid in a `template` for creating a `gensym`.
      Prepends a gensym hash to its argument, or replaces ``$`` characters with it.
      A gensym hash is unique to the template it was created in.
      This prevents accidental name collisions in `macro expansion`\ s.

   gensym
      A generated symbol, produced by the `gensym tag`.

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
      when the reader runs and when `tagging token`\ s are activated.

   text macro
      A `macro` that `expands <expansion>` to a `str atom`.
      instead of some other `form`,
      especially the `str atom` doesn't simply contain a string literal
      or (possibly qualified) identifier.
      Effectively, they return Python code,
      rather than Hissp,
      which makes them opaque to Hissp `metaprogramming`,
      like pre-expanding, code-walking macros.

..  LocalWords:  Lissp str Hissp gensym readerless
