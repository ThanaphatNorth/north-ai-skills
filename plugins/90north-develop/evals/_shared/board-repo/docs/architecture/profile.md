# Architecture profile — pricing

verified-at: fixture base · a single-package library

| Layer | Path | May import | Why |
|---|---|---|---|
| core | `src/**` | nothing outside `src/` | pure functions, no I/O |

Extension recipe: a new formatter is a new file in `src/` with its test in `test/`; no central file to edit.
State owners: none (no state). Contracts: the exported functions of `src/*.js`.
Commands: full suite `node --test` · one file `node --test test/<name>.test.js` · no typecheck, no lint.
Numbers and globs: `.ndev.toml`.
