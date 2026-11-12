# Design note: two loops, by type of work (90north-develop 0.7.0)

Status: **approved 2026-11-12** ("เริ่มเลย"). The change builds on the no-Jira tracker (commit 5a06e50).

## Request

Every card goes through the same 9 steps:
1. Read the board
2. Triage
3. Check the spec
4. Reproduce
5. Root cause
6. Test-first fix
7. Verify and record
8. Open the PR
9. A person approves

The loops are split by type of work, into two skills:
- `n-defect-loop` handles defects;
- `n-develop-loop` handles new development, new features and changed requirements.

A change with low or no impact may merge on its own; every other change waits for a person. Both loops work with
Jira or with the local board, and every code change follows n-dev.

## Today, and the shape after the change

| Today | After |
|---|---|
| `defect-loop` (attended) | `n-defect-loop`: 9 steps, attended by default, `--auto` for scheduled passes |
| `dev-loop` (attended) | `n-develop-loop`: 9 steps, attended by default, `--auto` |
| `n-loop` (unattended, any card type) | removed. Its machinery moves into `workflow` as the shared auto mode: queue and lock, triage matrix, verifier gate, ship classes, learning, tracker record, comments, schedule |
| `workflow`, `develop-init`, `n-dev`, `n-arch` | kept; their names and references are updated |

## The 9 steps per loop

| Step | n-defect-loop | n-develop-loop | Shared (workflow) |
|---|---|---|---|
| 0 | before the run | before the run | S0; in auto mode also A0: pass lock, profile, knowledge |
| 1 Read the board | open defects, or one key | ready items, or one key, spec or request | auto mode: A1 follow-ups, A2 scout and lock |
| 2 Triage | fix now / a person decides / ask | build now / a person decides / ask | auto mode: A3 decision table and class |
| 3 Check the spec | expected results + latest decisions → AC list | acceptance criteria + latest decisions → AC list | auto: `auto-triage.md` § Check the spec |
| 4 | **Reproduce**: red e2e and the before video | **Pin the goal**: acceptance spec red (WP-0); in attended mode Large work passes step 5's gate first | auto mode: A4 |
| 5 | **Root cause** at `path:line` | **Design**: note, AC → test, work packages, gate | |
| 6 | **Test-first fix** (`defect-fixer`, n-dev) | **Test-first build** per WP (`dev-builder`, n-dev) | auto mode: A5 |
| 7 Verify + record | review + QA run the spec twice; before/after video | review + QA; demo video | S2, S3; in auto mode A6 PROOF and A7 verifier |
| 8 Open the PR | proof comment, push per policy, PR → QA lane | the same → review lane | S4; auto mode: A8 |
| 9 Merge or approve | auto-merge class only (low impact + standing approval), else a person reviews | the same | `auto-evidence-and-ship.md` § Ship classes |
| after | clean up, learn | clean up, learn | S5, S6; auto mode: A9 learner |

The auto pass keeps its A0–A9 labels inside `workflow/references/auto-mode.md`. The table above maps them to the
9 steps.

## Two designs

| | **A. Each loop owns its steps, sharing one auto mode** (chosen) | **B. Two attended loops plus one auto runner** |
|---|---|---|
| Skills people call | 2 | 3 (the runner dispatches to either loop) |
| Where the middle steps live | one place per loop | the runner duplicates or calls into the loops' middles |
| Fits the request | yes ("2 skills") | no |

A wins: one door per kind of work, and the auto machinery is shared, not copied.

## Handoffs in auto mode

Each loop's auto queue is its own query. By default:
- `n-defect-loop`: `ai-queue` on defect types;
- `n-develop-loop`: `ai-queue` on every other type.

When triage routes a card to the other kind of work, the loop does not build it. Instead it:
- swaps `ai-queue` for that loop's hand-off label (`ai-to-develop` / `ai-to-defect`). A card is handed off at
  most once; a card that came by hand-off and still looks wrong is need-info. Never in a dry run;
- comments the reason;
- writes `handed-to-<loop>` in its ledger.

Each loop's queue is a list of queries: its own query, plus `labels=<its hand-off label>`. This works the same in
JQL and in the local query form, which has no OR.

## State and compatibility

- Ledgers: `defect-ledger.md` and `dev-ledger.md`, holding both modes. An existing `ai-ledger.md` stays as
  history. S0 still reads it for ownership while it has open rows.
- config: `§ AI loop` becomes `§ Auto mode`, shared by both loops, with one queue line per loop. develop-init
  migrates an existing `§ AI loop` with the user's yes.
- Commands change name. Old schedules (`/loop … dev-loop`, `defect-loop`, `n-loop`) must be re-registered. The
  READMEs carry a migration table. Version 0.6.0 → 0.7.0.
- Agents are unchanged in what they do; only their texts name the new loops.

## Success criteria

1. No tracked file outside `research/` names `dev-loop`, `defect-loop` or `n-loop`, apart from:
   - the legacy folder `.claude/defect-loop/`;
   - the migration tables;
   - the provenance line in `auto-mode.md` § Sources.

   Check: `git grep`, red at 128 lines before the change.
2. Each loop's `SKILL.md` lays out steps 1–9 and both modes.
3. Every reference path resolves to a file:
   - `references/…`, `templates/…`, `W/…` and `../<skill>/…` paths in the plugin's skills and agents;
   - checked with a one-off script.
4. The checks pass:
   - `validate_skill.py` reports 0 errors on every skill;
   - `claude plugin validate` passes;
   - the script tests (58) and the n-dev tests (135) stay green.
5. A fresh review finds no open issue.

## Progress

- [x] Approved; branch `two-loops-defect-develop` from 5a06e50
- [x] Red check: 128 tracked lines name an old loop
- [x] Moves: loops renamed, n-loop parts → workflow
- [x] n-defect-loop and n-develop-loop rewritten as 9 steps with both modes
- [x] Router, develop-init, config, agents, n-dev, n-arch, READMEs, manifests
- [x] Checks: old names 128 → 5 lines (migration tables and one provenance line); every path resolves; validate 0 errors;
      plugin validate; 58 script and 135 n-dev tests; structure check clean
- [x] Fresh review: 1 blocker (hand-off label lifecycle), 5 should-fix and 7 nits, all fixed.
  - Each card now carries one queue label. A hand-off happens at most once, its query is status-filtered, and it
    never happens in a dry run.
  - Auto lanes follow the ship class.
  - The Jira develop queue covers every non-defect type.
  - Attended Large work stops at the design gate before isolating anything.
  - The step 9 wording is fixed, and so are the stale § AI loop lines.
- [ ] Local commit
