<!--
This documentation is part of the Hissp project repository.
https://github.com/gilch/hissp
(C) 2026 Matthew Egan Odendahl
SPDX-License-Identifier: Apache-2.0
-->
# Changes
## [0.5.dev1]
### Add
- `cxl#` alias for `contextlib`.
### Fix
- kwarg token escape handling [#277](https://github.com/gilch/hissp/issues/277)
- REPL fragment continuation issue (e.g., `#> |if 1:|` errors and `#> |if 1:1|` completes now).