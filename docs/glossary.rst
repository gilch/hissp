.. Copyright 2024 Matthew Egan Odendahl
   SPDX-License-Identifier: CC-BY-SA-4.0

Glossary
########

.. glossary::
   :sorted:

   atom
      Objects of `Hissp (code)` that are not tuples. May appear inside
      tuples. The empty tuple is also considered an atom for most purposes.

   control word
      an :term:`atom` of type `str` that begins with a colon (``:``)
      character, or a literal that evaluates to one. Similar to the concept
      of a "keyword" in other Lisps, but that means something else in
      Python. They have special meaning in certain contexts, but otherwise
      compile to a string literal.

   form
      An object meant for evaluation; a Hissp expression.

   fragment (atom)
      An :term:`atom` of type `str` that does not begin with a colon,
      or a literal that evaluates to one.
      These are interpreted as Python code in most contexts,
      with some preprocessing for imports.
      Imports, identifiers,
      and their attributes are usually represented using fragments.
      Compiled string literals usually also come from fragments, either
      quoted with `quote (special form)`, or from a fragment containing the
      string literal.

   fragment
   fragment (token)
      One of several token types that read as `str` atoms,
      resulting in either a `fragment (atom)` (usually)
      or possibly a control word if the first character is a colon.

   fully-qualified symbol
      a `fragment` beginning with a module handle and
      accessing a `qualname` in the module.
      Looks like ``foo..bar`` or ``foo.bar.baz..spam.eggs.bacon``, etc.

   hissp (code)
      Python data meant for the Hissp compiler,
      which transpiles it into Python code.
      The tuple and str objects have special evaluation rules,
      but other object types are allowed.

   invocation
      A :term:`form` that looks like a function call.
      May also be a special form or macro form,
      which have different evaluation rules.

   lambda (special form)
      A `special form` that represents and compiles to a Python lambda expression.

   Lissp
      A text language that reads into memory as `Hissp (code)`,
      or the reader which does this.
      Lissp is one way of representing Hissp code.

   macro (form)
      A :term:`form` that invokes a `macro (function)` at Hissp compile time,
      expanding to some replacement form,
      called an `expansion`.

   macro (function)
      A Hissp `metaprogram` meant to run at Hissp compile time.

   expansion
   (macro) expansion
      The :term:`form` returned by a `macro (function)`,
      or the process of invoking a `macro (function)`.

   macroexpand
      A function `hissp.compiler.macroexpand` that invokes a `macro (function)`,
      or one of several related functions.

   metaprogram
      A program that writes code.

   metaprogramming
      Writing code that writes code.

   module handle
      A special fragment that gets preprocessed by the Hissp compiler into
      an absolute import. Looks like ``foo.`` or (with packages) ``foo.bar.baz.``, etc.

   munge
   munges
   munging
   demunging
      The process of making a `symbol (token)`
      a valid Python identifier by replacing invalid characters with "Quotez" words.
      The reverse is called "demunging".
      For example, ``-<>>`` munges as ``Qz_QzLT_QzGT_QzGT_``.
      Also `hissp.munger.munge` (available as :mod:`hissp.munge <hissp>`)
      or related functions that do the munging process.

   params (tuple)
      The first argument to a `lambda (special form)`,
      representing the lambda expression's parameters.
      Usually a tuple, but can be any appropriate iterable.
      Idiomatically a simple symbol when normal parameters would be a single letter,
      or the empty `control word` for no parameters.

   qualname
      ("qualified name") a path of attribute access from the object's containing module.
      Python classes and functions can have a ``__qualname__``
      attribute containing (a canonical) one.
      Can be a single segment for the module's globals.

   quote (special form)
      A one-argument `special form` that suppresses evaluation of its argument,
      instead interpreting it as data.
      A quoted fragment results in a string.
      `Module handle`\ s aren't processed.
      A quoted tuple results in a tuple,
      not the result of an invocation.
      This does not suppress tags,
      because that happens at read time,
      before the compiler gets to it.

   reader
   (Lissp) reader
      A component used early in the compilation or interpretation of a Lisp,
      which translates text into data structures representing the abstract
      syntax trees of the language (such as `Hissp (code)`).
      Lissp and Hebigo are examples.

   read time
      The pre-compile phase that translates Lissp to Hissp:
      when the :term:`reader` runs.
      An early phase in compilation when the reader translates textual code
      (such as `Lissp`) into `Hissp (code)`.

   readerless (function)
      The function `hissp.compiler.readerless`
      that transpiles Hissp code into Python without evaluating it.

   readerless (mode)
      A representation of `Hissp (code)` in the Python Language using mostly literals.
      May be passed to the `readerless (function)`
      or directly to an instance of the Hissp compiler.

   special form
      Any type of invocation special-cased in a Lisp compiler.
      Hissp has only two: `quote (special form)` and `lambda (special form)`.
      They look like function calls,
      but act more like `macro (form)`\ s.
      While `control word`\ s are :term:`form`\ s and can have special
      interpretations in certain contexts (including the two `special form`\ s),
      they are not considered special forms in their own right.
      `module handle`\ s also have a preprocessing rule in the compiler
      but aren't considered special forms.

   special tag
      The built-in reader macros ``'``, :literal:`\``, ``,``, and ``,@``,
      which act like `tag`\ s in most respects,
      and the remaining three (``.#``, ``_#``, and ``$#``),
      which look like `tag`\ s as well.

   symbol (atom)
      A `fragment` that would evaluate to a Python identifier,
      or a chain of attribute access separated by dots
      and possibly starting with a module handle,
      or a literal that evaluates to one of these.

   symbol (token)
      A type of Lissp `token` that is subject to `munging` and would normally
      read as a `symbol (atom)`.

   template
   template quote
      The :literal:`\`` `special tag`
      (the equivalent is called "quasiquote" or "syntax quote" in other Lisps)
      and the template expressions made from them:
      a :term:`reader` syntax for building `Hissp (code)`.
      Usually used by `macro (function)` definitions.

   tag
      Lissp syntax ending in a ``#`` that can do extra processing at read time.
      Tag names munge like `symbol (token)`\ s do.
      Reader macros are not the same thing as `macro (function)`\ s,
      which run at Hissp compile time rather than `read time`.
      Tags are more like Clojure/EDN tags than Common Lisp reader macros in
      that they get the next parsed object as input,
      rather than the raw character stream.
      Unlike Clojure/EDN tags,
      Lissp tags with additional trailing ``#``\ s
      can take a corresponding number of additional parsed objects
      (without wrapping them in a collection first).

   text macro
      A `macro (function)` that `expand <expansion>`\ s to a `fragment (atom)`
      (usually not counting `symbol (atom)`\ s
      or `fragment`\ s containing simple literals)
      instead of some other :term:`form`. Effectively, they return Python, rather
      than Hissp, which makes them opaque to Hissp `metaprogramming`,
      like pre-expanding, code-walking macros.
