# Copyright 2026 Matthew Egan Odendahl
# SPDX-License-Identifier: Apache-2.0
from unittest.mock import patch

# Ensures we're testing the current version.
with patch.dict("sys.modules"):
    import hissp

    hissp.transpile(hissp.__package__, "macros")

import hissp

hissp.transpile(__package__, "test_macros")
