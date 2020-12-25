Command Line Reference
======================

A normal install of the ``hissp`` package with ``pip`` and ``setuptools`` will
also install the ``lissp`` command-line tool for running Lissp code.
This is a convenience executable for starting ``python -m hissp``.
Its options were modeled after Python's:

.. code-block::

   usage: lissp [-h] [-i] [-c cmd] [file] [args [args ...]]

   Starts the REPL if there are no arguments.

   positional arguments:
     file        Run main script from this file. (- for stdin.)
     args        Arguments for the script.

   optional arguments:
     -h, --help  show this help message and exit
     -i          Drop into REPL after the script.
     -c cmd      Run main script (with prelude) from this string.
