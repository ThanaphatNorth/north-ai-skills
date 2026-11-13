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
- Profile: `<docs/architecture/profile.md>` verified at `<sha>`, current for this task's paths | none (n-arch suggested)
- New dependencies: <name — why nothing installed does the job — registry checked> | none

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

| Module | Test at | Red run (command → failing line, filled in at step 4) | Fakes needed |
|---|---|---|---|
| `<core module>` | its exported function | `<cmd>` → `<assertion that failed>` | none |
| `<shell module>` | its interface | `<cmd>` → `<assertion that failed>` | <in-memory adapter> |
| <existing behaviour being extended> | characterization test in `<file>` | n/a (must pass before and after) | <...> |

## Feature docs (only when the area has one)

| Doc | Rules added / changed / retired | Test for each |
|---|---|---|
| `<docs/features/<area>.md>` | <R-n: the rule in plain words — source> | <test name> |

Or the one line "no feature doc, or no rule changed".

## Security and performance (the rows the change touches)

From `references/security.md` and `references/performance.md`, or the one line "no security- or
performance-relevant path".

| Lens | Row | Answer: the line or test that settles it |
|---|---|---|
| security | <e.g. Access to each record> | <owner check in `path`; test `name`: another user's id → 404> |
| performance | <e.g. Queries per request> | <one query with a join; test `name` counts queries for 1 and 20 rows> |

## Change safety (Large, or any contract / schema / migration / outbound call / deploy change)

From `references/change-safety.md`, or the one line "no contract, data or rollout impact".

| Area | Answer |
|---|---|
| Contracts touched and their consumers | <API / event / table — consumers — additive or versioned> |
| Migration | <additive, idempotent, online, tested on a copy; rollback runs on the new schema> |
| Rollout and off switch | <first audience, flag + removal date or redeploy> |
| Failure modes at new seams | <timeouts, retries, idempotency, second delivery> |
| Signals | <works: ...; roll back: ...> |

## Alternatives (Large only)

| Design | Interface sketch | Depth | Locality | Seam placement | Verdict |
|---|---|---|---|---|---|
| A | <...> | <...> | <...> | <...> | chosen / rejected because <...> |
| B | <...> | <...> | <...> | <...> | <...> |

## Decisions (one round, before the first edit — `SKILL.md` § Questions)

| # | Decision | Options, recommended first | Answer |
|---|---|---|---|
| 1 | <two readings · a trade-off the user would care about · a breaking or unrequested change to state shape, schema or a public interface> | <A — leads to …> · <B — leads to …> | <the user's answer \| ASSUMPTION: A, nobody to answer> |

Or the one line "no decision: every unknown was a fact or a reversible choice".

Decided mid-build: <DECIDED: what — undo by how> | none

## Progress (Large: keep current so another session can resume)

- [ ] <module or step> — <red seen / green / verified, with the command>
