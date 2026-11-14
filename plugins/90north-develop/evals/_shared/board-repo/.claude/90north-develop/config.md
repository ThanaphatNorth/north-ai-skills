# 90north-develop — project config

Written by `/90north-develop:develop-init`. Facts only; each fact lives on one line here and nowhere else.

## Tracker
- Backend: local — board `.90north-develop/board`, prefix `TASK`, committed yes.

## Board facts
- Issue types: defects `bug`; development `story`, `task`, `improvement`.
- Statuses: todo, in-progress, need-info, review, ready-for-qa, reopened, done — `done` is never used by the loops.

## Defect flow (n-defect-loop)
- Open-defect query: `type=bug status=todo,reopened`. Sanity query: `type=bug -status=done`.
- Lane to QA: `in-progress → review → ready-for-qa`.
- Branch: `fix/<KEY>-<slug>`. Batch: up to 3 tickets in parallel.
- Structural fence: a change to an exported function's signature, or more than 5 files or 200 lines.

## Dev flow (n-develop-loop)
- Ready-for-dev query: `type=story,task,improvement status=todo`. Sanity query: `-type=bug -status=done`.
- Acceptance criteria live in: the card's `## Acceptance criteria` section.
- Lane to review: `in-progress → review`.
- Branch: `feat/<KEY>-<slug>`. Items in flight at once: 1.
- Large fence: a new package, a change to an exported function's signature, more than 8 files or 400 lines.
- Design gate: stop for Large and for a change to an exported function's signature (default). Always-ask: none. Post design notes to the tracker: no.

## Comments
- Language: match the ticket.

## Push policy
- Default: never push without the user's yes. An attended run asks once, in its decision round, for the branches it will create.
- Standing approval: none.
- PR: base `main`, created with `gh pr create`.

## Repo
- Path: this repository's root · base branch `main`.
- Worktree per item: a sibling folder `<repo>-<key-lower>` on the flow's branch; commit an empty anchor right after creating it.
- Dependency bootstrap in a new worktree: none (no dependencies).

## Stack recipe
- No app, API, database or web server: the library is exercised by its tests only.

## Accounts and login
- None: there is no login.

## Checks (QA runs all; builders and fixers run the relevant ones)
- Unit tests: `node --test`. One file: `node --test test/<name>.test.js`. No typecheck, no lint.
- Structure check: n-dev's `scripts/structure_check.py --base main`.
- Security and performance scanners: none.

## Team (agents)
- Plugin agents: `90north-develop:dev-builder` · `90north-develop:defect-repro` + `90north-develop:defect-fixer` · `90north-develop:risk-reviewer`.
- Repo agents to use as role files: none.

## Docs
- Feature docs: off.

## Review
- Data sizes the performance review assumes: a formatter call handles one amount; no stored data.
- Single review: on (default).
- Security notes: the person running the loop.

## Spec sources
- Spec: the card itself. No decision log.

## Evidence
- No UI: the evidence is the spec's own output (red before, green after). No video.

## Project rules
- Amounts are integers in cents; never floats in the public API.
