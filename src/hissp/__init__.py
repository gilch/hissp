# Copyright 2020, 2022 Matthew Egan Odendahl
# SPDX-License-Identifier: Apache-2.0

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this package except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""It's Python with a `Lissp`.

See the GitHub project for complete documentation and tests.

https://github.com/gilch/hissp

``__init__.py`` imports several convenience utilities,
including `readerless`, `demunge`, `transpile`, and `interact`,
as well as the `hissp.macros._macro_` namespace,
making all of the bundled macros available with the shorter ``hissp.._macro_`` qualifier.
"""
from hissp.compiler import readerless
from hissp.munger import demunge
from hissp.reader import transpile
from hissp.repl import interact

from contextlib import suppress

# Hissp must be importable to compile macros.lissp in the first place.
with suppress(ImportError):
    # noinspection PyUnresolvedReferences
    from hissp.macros import _macro_
del suppress


__version__ = "0.4.dev"
