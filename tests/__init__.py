# Copyright 2026 Matthew Egan Odendahl
# SPDX-License-Identifier: Apache-2.0
import hissp

hissp.transpile(hissp.__package__, 'macros')  # Ensures we're testing the current version.
hissp.transpile(__package__, "test_macros")
