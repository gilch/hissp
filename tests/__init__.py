# Copyright 2026 Matthew Egan Odendahl
# SPDX-License-Identifier: Apache-2.0
import hissp

# Ensures we're testing the current version.
hissp.transpile(hissp.__package__, "macros")
hissp.transpile(__package__, "test_macros")
