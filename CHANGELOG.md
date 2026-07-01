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

### Breaking

Make `hissp._macro_` a class.
(The compiler still accepts any namespace type.)
Inherit rather than copy, as was recommended for readerless mode.
Use Python's multiple inheritance to "import" multiple `_macro_` classes.
The method resolution order will determine precedence.

Eliminate the ugly `Qz_` format. Munging is prettier.
Munged names are much more usable from Python or with alternate readers.
Munged characters begin with a capital letter and end with an underscore:
- `🐍` to `Snake_`.

Words in multiword names end in `X`, but hyphens become `H`:
- `▲` to `BlackXupHpointingXtriangleX_`

Unnamed letters still use a hex code, but begin with `Ox`.
(That's not a zero, because identifiers can't start with a digit.)

Some of the ASCII short names have changed.
Kebabs munge with `___` (three underscores),
but isolated or repeated `-` use the short name `Dash_`:
- `if-else` to `if___else`
- `->` to `Dash_Gt_`

Demunging still works.
Munged names are still distinct from `UPPER_CASE` and `snake_case`.
They're less distinct from `CapWords` used by class names,
only distinguished by the trailing underscore in the case of a single-character name,
which Pythonic code sometimes uses to avoid a conflict.
The need for this is especially rare for class names, however.

Gensyms start with a prefix like `_gABCDEFGH__`.

`QzMaybe_` is gone and no longer required for recursive macros.
`(_macro_.foo)` is now a valid macro form,
and works even if `_macro_` is shadowed by a local.
To call a macro function at run time,
use an identity form like `((|| _macro_.foo))` to avoid putting the symbol in the invocation position.

Simplify `alias` macro.
It no longer expects control world arguments for `_macro_`.
In the case of an aliased macros name,
the compiler now checks that namespace anyway.
In the case of aliased tags names,
`alias` writes logic to add `_macro_` (and `#`):
- `H##b"bytes"`

Make `.#` multiary.
The interpretation is that the first argument evaluates to a callable applied to the remaining arguments.
(Similar to `pass:` in Hebigo.)
This allows non-symbol expressions to be used as tags.
For example, functions used as tags can be abbreviated with an alias:
```
.##bn#dict((1 2)(3 4))
;; same as
builtins..dict#((1 2)(3 4))
```

Replace
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