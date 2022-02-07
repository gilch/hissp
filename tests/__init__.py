# Copyright 2019 Matthew Egan Odendahl
# SPDX-License-Identifier: Apache-2.0
from hissp.reader import transpile

transpile("hissp", "basic")
transpile(__package__, "test_basic")
