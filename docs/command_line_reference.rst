.. Copyright 2020, 2021 Matthew Egan Odendahl
   SPDX-License-Identifier: CC-BY-SA-4.0

Command Line Reference
======================

.. _lissp command:

Lissp Command
-------------

A normal install of the ``hissp`` package with ``pip`` and ``setuptools`` will
also install the ``lissp`` command-line tool for running Lissp code.
This is a convenience executable for starting ``python -m hissp``,
whose minimal options were modeled after Python's most commonly used:

.. code-block:: Text

   usage: lissp [-h] [-i] [-c cmd] [file] [args [args ...]]

   (Hissp X.X.X) Starts the REPL if there are no arguments.

   positional arguments:
     file        Run this file as main script. (- for stdin.)
     args        Arguments for the script.

   optional arguments:
     -h, --help  show this help message and exit
     -i          Drop into REPL after the script.
     -c cmd      Run this string as main script (with prelude).

The Lissp Compiler
------------------

The recommended way to compile Lissp modules is with
`transpile <hissp.reader.transpile>` calls in ``__init__.py`` files (or the main module).

This can be done manually in the REPL.
However, an external build system may need to use shell commands.
It is possible to run transpile commands in the shell via ``python -c`` or ``lissp -c``.

For example, using `hissp.reader.transpile_file`,

.. code-block:: shell

   $ alias lisspc="lissp -c '(hissp.reader..transpile_file : :* (getitem sys..argv (slice 1 None)))'"
   $ lisspc spam.lissp
   $ cd foopackage
   $ lisspc eggs.lissp foopackage
