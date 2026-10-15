# Design note: <task name>

Size: Standard | Large  ·  Base ref: <commit or branch>  ·  Date: <YYYY-MM-DD>

## Goal and success criteria

<One sentence: what the user gets.>

| # | Criterion | Checked by |
|---|---|---|
| 1 | <observable behaviour> | <test file::name, command, or observable result> |

Assumptions: <each one, marked ASSUMPTION, or "none">

## Orient facts

- Commands: typecheck `<cmd>` · one test file `<cmd>` · full suite `<cmd>` · lint `<cmd>`
- Extension points used: <registry / DI module / route table / event / composition — with the file that holds it>
- State owners in use: <server cache, store, URL, forms, DB, config module>
- Reuse inventory: <existing functions/hooks/services this task uses, with paths> | none found (searched: <terms>)

## Module map

| New file | Responsibility (one sentence, no "and") | Interface | Layer (core / shell / UI / wiring) | Depends on |
|---|---|---|---|---|
| `<path>` | <...> | `<signature>` | core | <modules> |

Dependency direction: <UI → application → core; confirm no cycle>

## State ownership

| Fact | Owner | Writer | Readers | Derived from it | Copies + invalidation |
|---|---|---|---|---|---|
| <fact> | <one place> | <one module> | <...> | <selector / function> | <none, or trigger + conflict rule> |

## Extension plan (pre-existing files)

| File | Change | Kind | Reason |
|---|---|---|---|
| `<path>` | <import + registration line> | wiring | <why this seam> |
| `<path>` | <...> | in-place edit | <bug fix / rule changed for everyone / preparatory refactor — see extension.md decision table> |

## Test seams

| Module | Test at | Red first? | Fakes needed |
|---|---|---|---|
| `<core module>` | its exported function | yes | none |
| `<shell module>` | its interface | yes | <in-memory adapter> |
| <existing behaviour being extended> | characterization test in `<file>` | n/a (must pass before and after) | <...> |

## Alternatives (Large only)

| Design | Interface sketch | Depth | Locality | Seam placement | Verdict |
|---|---|---|---|---|---|
| A | <...> | <...> | <...> | <...> | chosen / rejected because <...> |
| B | <...> | <...> | <...> | <...> | <...> |

## Stop check

- [ ] Two designs trade off in a way the user would care about → stop and ask.
- [ ] The change alters state shape, a DB schema, or a public interface → stop and ask.
- [ ] Neither applies → continue to step 4.
