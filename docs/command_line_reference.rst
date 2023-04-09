.. Copyright 2020, 2021, 2022 Matthew Egan Odendahl
   SPDX-License-Identifier: CC-BY-SA-4.0

Command Line Reference
######################

.. _lissp command:

Lissp Command
=============

A normal install of the ``hissp`` package will
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
==================

The recommended way to compile Lissp modules is with
`transpile <hissp.reader.transpile>` calls in ``__init__.py`` files
for packaged modules,
or in the main module for any modules not in a package.

One-offs are easy to do manually in the REPL,
but an external build system may need to use shell commands.
It is possible to run transpile commands in the shell via ``python -c`` or ``lissp -c``.

For example, using `hissp.reader.transpile`, a package name, and module names,

.. code-block:: shell

   $ alias lisspt="lissp -c '(hissp..transpile : :* ([#1:] sys..argv))'"
   $ lisspt pkg foo # Transpiles pkg/foo.lissp to pkg/foo.py in a package context.
   $ lisspt pkg.sub foo # Transpiles pkg/sub/foo.lissp to .py in subpackage context.
   $ lisspt "" foo bar # foo.lissp, bar.lissp to foo.py, bar.py without a package.

or using `hissp.reader.transpile_file`, a file name, and a package name,

.. code-block:: shell

   $ alias lissptf="lissp -c '(hissp.reader..transpile_file : :* ([#1:] sys..argv))'"
   $ lissptf spam.lissp # Transpile a single file without a package.
   $ cd pkg
   $ lissptf eggs.lissp pkg # must declare the package name
   $ cd sub
   $ lissptf ham.lissp pkg.sub # separate subpackage name with dot
