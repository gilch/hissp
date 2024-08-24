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
      A type of `token` that results in a parsed object when passed to the Lissp parser.
      These are what the parser considers nouns,
      and typically emits as `atom`\ s.

   tagging token
      A type of `token` that modifies one or more subsequent tokes.
      These can be thought of as parser adjectives.

   special tag
      One of the built-in tags treated as a special case in the reader.

   comment token
      An `object token` consisting of one or more lines,
      possibly indented with spaces,
      each starting with a semicolon (``;``) character.
      Comment tokens parse as `hissp.reader.Comment` instances,
      a type that is normally discarded by the reader.
      However, they can be arguments for `tagging token`\ s

   Unicode token
      An `object token` that begins and ends with a quotation mark (``"``) character.
      They may contain newline characters like Python's triple-quoted string literals,
      as is typical of Lisps.
      Internal quotation marks must be escaped with a preceding reverse solidus
      (``\``) character. These parse as `str atom`\ s containing
      a Python string literal wrapped in parentheses.

   str atom
      an `atom` of type `str`.

   atom
      a `form` that is not an instance of `tuple`.
      Exception: the empty tuple ``()`` can be considered an atom for most purposes,
      even though it is an instance of `tuple`.

   form
      an object meant for evaluation;
      a Hissp expression for passing to the Hissp compiler.

   fragment token
      An `object token` that begins and ends with a vertical line (``|``) character.
      Internal vertical lines must be escaped as two vertical lines (``||``).
      These parse directly as `str atom`\ s.

   bare token
      An `object token` without the delimiters marking it as a
      `comment token` (``;``), `Unicode token` (``"``), `fragment token` (``|``),
      or `control token` (``:``).
      These are either `literal token`\ s, or failing that, `symbol token`\ s.

   literal token
      A `bare token` that is a valid Python literal,
      as determined by `ast.literal_eval`, but not of a container type.
      These parse as `atom`\ s of that type.

   symbol token
      A `bare token` that is not a `literal token`.
      These are subject to `munging` and parse as `str atom`\ s.

   munging
      The process of replacing characters invalid in a Python identifier with their
      `Quotez` equivalents.
      Primarily used to make a `symbol token` into a `str atom`
      containing a valid Python identifier.
      The munging machinery is in `hissp.munger`.
