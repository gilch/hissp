<!--
Copyright 2023 Matthew Egan Odendahl
SPDX-License-Identifier: Apache-2.0
-->
# Hissp Tests
This directory contains Hissp's test suite.

Hissp proper has no dependencies beyond Python's standard library,
but the test suite requires additional packages.
Install them from the repository root using
```
pip install -r requirements-dev.txt
```

A significant additional portion of Hissp's test coverage is derived from
REPL examples (via Sybil) found in the reStructuredText files in `docs/`
and in docstrings in the source code.
Find the setup for that in `conftest.py`.

The test runner for Hissp's suite is `pytest`.
See the `.github/workflows/test-package.yml`
for the full automated build and test process,
including the `pytest` command used.
