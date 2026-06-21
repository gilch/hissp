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

### Breaking: Replace
- `let-from` with `let-call`.
- `let*from` with `let*call`.
- `loop-from` with `let-again`.

See updated API docs. Use `(:*`-`)` for the old behavior, e.g.,
```lisp
(let-from (a b : :* cs) 'abcdefg
  (print a b cs))
;; becomes
(let-call (a b : :* cs) (:* 'abcdefg)
  (print a b cs))
```

`let-again` takes pairs like `let` instead of an initial iterable.
The `recur-from` anaphor has been replaced with `again-with`,
but works the same.

### Fix
- kwarg token escape handling [#277](https://github.com/gilch/hissp/issues/277).
- REPL fragment continuation issue (e.g., `#> |if 1:|` errors and `#> |if 1:1|` completes now).