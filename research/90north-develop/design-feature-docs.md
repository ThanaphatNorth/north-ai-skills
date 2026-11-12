# Design note: living feature docs (90north-develop 0.8.0)

Status: **approved 2026-11-12** ("ทำเลย").

## Request

The loops should leave markdown docs that say how the system works: its logic, its requirements and why it is the
way it is.

## The gap today

| What exists | What it covers | What it misses |
|---|---|---|
| n-arch profile | how the repo is layered | an area's business rules and their reasons |
| design notes | Large work: a repo file | Standard work: the note sits in a scratch or run folder and is gone after the run |
| tracker comments | each ticket's story | no single current picture; outside the repo |

## Decision

One **feature doc** per area, in the repo (default `docs/features/<area>.md`), changed in the **same PR** as the
code. Per-ticket reports and changelogs were rejected, because they pile up and contradict each other.

It holds:
- the purpose;
- the rules, `R-n`, each with its source;
- the behaviour a reader cannot see quickly in the code;
- rule → test;
- the decisions, with reasons;
- the known limits.

It never copies values that live in code or config, the requirement text, or the architecture (the n-arch profile
owns that).

## Who writes, when

| Who / when | What happens |
|---|---|
| orchestrator (or conductor), after the last build or fix and before S2 | writes the doc as a local commit `docs(<area>): … (<KEY>)`; builders and fixers never write it (they do not see the ticket) |
| n-develop-loop | every added or changed rule or behaviour |
| n-defect-loop, rule changed or clarified | changes the rule |
| n-defect-loop, any fix | adds the regression test to its rule's row |
| n-defect-loop, by-design, attended | a docs-only branch |
| n-defect-loop, by-design, `--auto` | the line goes in the solution comment |
| n-dev | keeps an existing doc true |

## Reading

- **Step 3:** the rules are read before the AC list. A ticket that contradicts a rule without a settling decision
  is `needs-info`.
- **Freshness:** `verified-at` works like the profile's: rules that newer commits touch are re-checked.

## Guards

- Stable `R-n` ids; retired rules are marked and kept.
- About 150 lines per doc at most; past that, the doc is split.
- An index line per doc.
- Config § Docs can turn it all off.
- Verifier claim **V10** (auto mode): the doc matches the diff, claims nothing the diff and tests do not show, and
  `verified-at` was updated.

## Where it lives in the plugin

- **Rules (one owner):** `workflow/references/feature-docs.md`.
- **Template:** `workflow/templates/feature-doc.md`.
- **Wiring:**
  - n-develop-loop steps 3, 5, 6 and 8;
  - n-defect-loop steps 2, 3, 6 and 8;
  - auto mode A5;
  - n-dev steps 3 and 7, self-contained, because n-dev is also installed alone;
  - loop-verifier V10 and the verifier outcomes table;
  - config § Docs and develop-init;
  - READMEs, version 0.8.0.

## Changes after the fresh review (3 blockers, 6 should-fix, nits)

- **Builders and fixers** carry a hard rule never to edit a feature doc. n-dev says a loop's builder leaves the doc to
  its orchestrator.
- **The verifier verdict** needs every claim CONFIRMED; V10 reads `N/A` when docs are off. V10's criteria live only
  in `feature-docs.md`. V5 counts the doc as in scope. V8's term list covers V1–V10, and the record grep matches
  `V[0-9]+`.
- **By-design** has no docs-only branch. The comment cites the existing rule or proposes one, and the doc changes
  once the PO confirms (the hand-off and by-design comment templates carry the slot).
- **`verified-at`** names the merge-base, so the sha survives squash and merge.
- **Auto A3** reads the rules.
- **Auto-merge gates** count the feature doc as an allowed path, and exclude it from the size and file counts.
- **Coverage.** A new doc is `coverage: partial`, so an unlisted rule is unknown, not absent. A plain defect fix
  creates no doc.
- **Single owner.** The config list of areas is dropped (the index is the only list), and the max lines live in
  config only. A change across several docs, test names instead of line numbers, a design-note slot, and a
  standalone n-dev rule for stable ids are all covered.

## Success criteria

1. The template and the reference exist.
2. Both loops, develop-init and loop-verifier name `feature-docs.md`, and n-dev names the feature doc. Check: grep,
   red at 0 of 5 before the change.
3. config has § Docs. Check: red at 0 before the change.
4. The checks pass:
   - `validate_skill.py` reports 0 errors on every skill;
   - `claude plugin validate` passes;
   - the script tests (58) and the n-dev tests (135) stay green;
   - every referenced path resolves.
5. A fresh review finds no open issue.
