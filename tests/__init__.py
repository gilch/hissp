# Copyright 2019 Matthew Egan Odendahl
# SPDX-License-Identifier: Apache-2.0
from hissp import transpile

transpile("hissp", "macros")
transpile(__package__, "test_macros")
