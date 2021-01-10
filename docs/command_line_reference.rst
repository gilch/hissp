.. Copyright 2020, 2021 Matthew Egan Odendahl
   SPDX-License-Identifier: CC-BY-SA-4.0

Command Line Reference
======================

Lissp
-----

A normal install of the ``hissp`` package with ``pip`` and ``setuptools`` will
also install the ``lissp`` command-line tool for running Lissp code.
This is a convenience executable for starting ``python -m hissp``.
Its options were modeled after Python's:

.. code-block:: Text

   usage: lissp [-h] [-i] [-c cmd] [file] [args [args ...]]

   Starts the REPL if there are no arguments.

   positional arguments:
     file        Run main script from this file. (- for stdin.)
     args        Arguments for the script.

   optional arguments:
     -h, --help  show this help message and exit
     -i          Drop into REPL after the script.
     -c cmd      Run main script (with prelude) from this string.

The Lissp Compiler
------------------

While the recommended way to compile Lissp modules is with
`transpile <hissp.reader.transpile>`
calls in the REPL, the main module, and the package ``__init__.py`` files,
there is also a command-line interface in case that is needed by an external build system.

The command usage is ``python -m hissp.reader package [module [module ...]]``,
and it takes the same arguments as ``transpile``.

The package can be an empty string for top-level modules.
Remember to use the *module* names, not the *file* names.
E.g. ``python -m hissp.reader "" spam eggs``, not ``python -m hissp.reader "" spam.lissp eggs.lissp``.
