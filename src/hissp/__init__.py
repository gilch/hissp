# Copyright 2020 Matthew Egan Odendahl
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
from hissp.compiler import readerless
from hissp.munger import demunge
from hissp.reader import transpile

# The try allows the transpiler to be used on macros.lissp even when
# macros.py doesn't exist yet.
try:
    # noinspection PyUnresolvedReferences
    from hissp.macros import _macro_
except ImportError:
    from warnings import warn

    warn("Failed to import macros. They may not have compiled.")

__version__ = "0.4.dev"


def interact(locals=None):
    """Convenience function to start a LisspREPL.
    Uses the calling frame's locals if not provided."""
    from hissp.repl import LisspREPL

    if locals is None:
        import inspect

        frame = inspect.currentframe().f_back
        locals = {**frame.f_globals, **frame.f_locals}
    LisspREPL(locals=locals).interact()
