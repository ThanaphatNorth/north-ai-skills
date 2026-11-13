---
name: n-defect-loop
description: Defect loop of the 90north-develop plugin — takes defects from the board (Jira, or a local board when there is no Jira; one by key, or a sweep of the open-defect query) through 9 steps. Read the board, triage, check the spec, reproduce with a red e2e and a before video, find the root cause at path:line, fix test-first with n-dev, verify and record (code, security and performance review + QA, spec green twice, after video), open the PR with the 3-part comment and move the ticket to the QA lane. It merges on its own only a low- or no-impact change inside a standing approval; everything else waits for a person. Attended by default; --auto runs it unattended on a schedule or /loop, where a gate parks the card with a question. Reads project facts from .claude/90north-develop/config.md (run /90north-develop:develop-init first). Use when the user says "defect loop", "sweep the board", "fix bug <KEY>", "clear the bugs to Ready for QA", or a schedule runs it. New features and changed requirements go to n-develop-loop.
argument-hint: "[<KEY>] [--auto] [--dry-run]"
---

# 90north-develop · n-defect-loop

You are the **orchestrator** (the main conversation): you read the tracker, decide, dispatch subagents, check what they
return and write to the tracker (Jira or the local board, through `W/scripts/tracker.sh`).
- **Shared parts** live in the workflow skill (`W = ../workflow/` from this skill's base directory): the stages
  S0–S6, the dispatch safety block, the tracker and the auto mode. Read `W/references/stages.md` once per run.
- **Code:** every fix follows n-dev (`../n-dev/`).

## Calls and modes

| Call | Does |
|---|---|
| `/90north-develop:n-defect-loop` | attended: one sweep of the open-defect query |
| `/90north-develop:n-defect-loop <KEY>` | attended: one defect |
| `/90north-develop:n-defect-loop --auto [--dry-run] [<KEY>]` | unattended: one pass per `W/references/auto-mode.md` |
| `/loop 30m /90north-develop:n-defect-loop [--auto]`, or a scheduled task (`W/templates/auto-scheduled-task.md`) | keep sweeping; attended mode keeps going between ticks while cards remain |

The two modes differ first in who answers a gate:
- **Attended:** a gate stops and asks you in chat.
- **`--auto`:** a gate parks the card with a question on it, and the pass goes on. Auto mode adds the queue lock,
  the triage matrix (`W/references/auto-triage.md`), the verifier and the learner.

## Step 0 · Before every run
Run S0 in `stages.md` with flow `defect`, and read this skill's `references/core-lessons.md` in full. In auto mode,
run A0 as well. A legacy `.claude/defect-loop/` folder works as `DL` (its `ledger.md` is the defect ledger) until
develop-init migrates it.

## 1 · Read the board
- **Attended.** Pull config § Defect flow's open-defect query (board + backlog, ids or local statuses) with
  `W/scripts/tracker.sh search '<query>'`, run its sanity query, and diff the keys against the ledger. Never
  shortcut to a time window.
- **Auto.** Run A1 follow-ups first, then A2 scout and lock on this loop's queue.

For each ticket not skipped:
1. `W/scripts/tracker.sh get <KEY>`.
2. `W/scripts/tracker.sh download <KEY> <scratchpad>/<KEY>/attachments`, then **look** at the screenshots and videos.

Attachments may hold personal data: describe them, never copy them into the repo or a comment.

## 2 · Triage
Attended mode puts each ticket in one of these. Auto mode uses the decision table in `W/references/auto-triage.md`
instead.
- `actionable`: symptom, screen, role and expected result are clear enough to script.
- `needs-info`: comment once asking for the missing piece (steps, role, data, screenshot); ledger `needs-info`.
- `change request / by-design`: the ticket is not a defect against the current spec. Any of these counts:
  - the code already does what the current spec says. Cite the line or decision id, after checking "Revised by /
    Reversed by".
  - a merged change removed the feature. Cite the commit.
  - the ticket asks for behaviour that never existed.

  Record current behaviour with a GREEN verification spec and comment with the by-design variant. Hand it to
  **n-develop-loop** (`W/SKILL.md` § Handoffs; in auto mode, the hand-off label). Name the stale document when
  there is one. With config § Docs on, the comment cites the rule that already says so (`R-n` in the area's
  feature doc) or proposes the rule line. There is no branch and no doc edit until the PO confirms it
  (`W/references/feature-docs.md` § By-design answers).
- `structural`: a defect inside config § Defect flow's fence: schema or migration, auth, reported figures, the
  API↔web contract, deploy, or more than 5 files or 200 lines.
  - Run steps 4–5, then comment with the structural variant and the options.
  - No build without a person's yes. On a yes, n-develop-loop takes it, with the ledger row
    `from-n-defect-loop KEY`. It works on a new `feat/<KEY>-<slug>` worktree (S1) with this red spec copied in as WP-0,
    then runs its steps 5–6.

Batching (attended mode):
- Process actionable tickets in batches of up to 3 in parallel, each on its own worktree and stack, within the
  preview-server cap.
- When a batch finishes and open, unhandled cards remain, start the next batch at once.
- A card is handled once it is in the QA lane with our fix, or commented with evidence and ledgered in a parked
  state. Stop only when every card is handled.

## 3 · Check the spec
Turn the ticket into the criteria you will test, numbered `AC-1 … AC-n` in the ticket's own words:
- each step to reproduce becomes an action;
- each expected-result sentence becomes a criterion;
- a sentence that names two screens is two criteria.

Read every comment newest first, any linked spec or decision log (config § Spec sources), and the area's feature
doc when config § Docs is on (`W/references/feature-docs.md`): its rules `R-n` say what the area should do. When
the latest comment, a linked spec or an existing rule disagrees with the ticket and nobody settled it, ask which
one wins. That question is `needs-info`; never pick yourself.

## 4 · Reproduce: a failing test, on video
1. S1 Isolate (`stages.md`), branch `fix/<KEY>-<slug>`. Ticket data from the reporter's files goes into a **copy**
   of the test DB.
2. Dispatch `90north-develop:defect-repro` with:
   - the safety block, the ticket text verbatim (minus personal data), the comments and the attachment paths;
   - the worktree, web URL and login (role → test account, how to log in);
   - the config § Checks e2e lines, and the output folder `<scratchpad>/<KEY>/repro`.

   It returns a spec, the **red** output and the raw video.
   - Red for the reported reason → reproduced; keep the video as `before`.
   - Not red after an honest attempt (it lists what it tried) → try once yourself in the browser pane, and on the
     reporter's environment if one is named. Still nothing → comment what was tried and what is needed, ledger
     `cannot-reproduce`, and leave the ticket in its lane.

   Never fix an unreproduced defect.

## 5 · Root cause: the exact file and line
1. Rank 3–5 falsifiable hypotheses (the `diagnosing-bugs` skill, when installed).
2. Confirm one at `path:line` and name the guards you checked. It must explain the red run exactly.

Small, certain web or CSS defects may be reproduced and fixed in one fixer dispatch, which writes the measuring spec
red first.

## 6 · Test-first fix
Dispatch `90north-develop:defect-fixer` with:
- the safety block, the ticket, the red spec and its failing line, and the root cause at `path:line`;
- the worktree, the scope fence, the config § Checks and § Team lines, and the output folder;
- n-dev's absolute path, with its structure check `../n-dev/scripts/structure_check.py --base <base>`.

It writes a regression test red → fix → green, runs the checks and commits locally:
`fix(<area>): <summary> (<KEY>)`.

**Feature doc** (config § Docs on). Write it yourself, never the fixer, per `W/references/feature-docs.md`:
- the fix changed a rule or made one clearer → change that `R-n`, with the regression test in its row, and create
  the doc (partial) when the area has none;
- a plain fix and the doc states the right rule → add the regression test to that rule's row;
- a plain fix and the area has no doc → no doc.

Commit it locally as `docs(<area>): … (<KEY>)`.

## 7 · Verify and record
1. S2 Verify (`stages.md`): the reviewer's spec is the ticket plus the root cause. Two `risk-reviewer` runs read
   the same diff for security and for performance. QA runs the defect spec twice. Fix rounds go back to step 6,
   with a budget of 2.
2. S3 Evidence: `before` (red) and `after`.
3. Auto mode adds A6 PROOF and the A7 verifier gate: nothing the verifier refutes is published.

## 8 · Open the PR
In auto mode, pick the ship class (step 9) first: it decides the lane.

S4 Ship with `templates/jira-comment.md`: the before video goes under §1, the after video and the `Docs:` line
under §3. In auto mode,
adjust it as `W/templates/auto-comments.md` § Proof comment says.
- Push per config § Push policy and open the PR.
- Lane, by mode and class:
  - attended: config § Defect flow's QA lane; ledger `ready-for-qa`.
  - auto, needs-review: config § Auto mode's review lane; ledger `in-review`.
  - auto, auto-merge: merged at step 9, then the after-merge lane; ledger `merged`.
- A partial fix (the rest needs a decision) takes the partial variant, and the ticket stays in its lane.

## 9 · Merge, or a person approves
The ship class decides (`W/references/auto-evidence-and-ship.md` § Ship classes):
- **Auto-merge** happens only in `--auto`, because it needs the verifier, and only for a low- or no-impact change.
  Every gate in § Ship classes must hold: size, safe kind and paths, blast radius, no forbidden area, a current
  profile, a clean structure check, security and performance reviews that found nothing at blocker or
  should-fix, a confirmed verifier, green CI, the grace window, and a base that has not moved.
  It also needs a standing approval in config § Push policy that names merge.
- **Everything else** waits for a person. They review the PR and merge it, or tell you in chat to merge that one
  PR. Attended mode never auto-merges.

## After · Clean up and learn
S5 Clean up, then S6 Learn: tag lessons `[defect]`, promote defect-only rules into `references/core-lessons.md` and
shared ones into the workflow skill's. Auto mode runs A9: outcomes, then the learner.

## Gates — where the loop stops for a person

| Gate | Ledger state | Attended | Auto |
|---|---|---|---|
| missing information or conflicting sources | `needs-info` | comment, ask in chat | question on the card |
| not reproduced | `cannot-reproduce` (auto: `needs-info`) | comment what was tried | what was tried, on the card |
| change request / by-design | `handed-to-n-develop-loop` | hand-off row, tell the PO | hand-off label |
| structural | `blocked-needs-human` / `solution-posted` | options in chat | solution on the card |
| 2 fix rounds used, or a decision | `blocked-needs-human` / `stopped` | ask in chat | what was tried, on the card |
| push | `awaiting-push` | your yes for that branch, or a standing approval | the same |
| PR open | `ready-for-qa` (auto: `in-review`) | a person reviews the PR | the same |

## Never (on top of `stages.md` § Never)
- Fix a defect that was not reproduced red in this session.
- Build a structural change inside this loop: it goes through n-develop-loop's design gate.
- Edit the defect spec to make it pass.
- Merge a PR outside the auto-merge class without a person's explicit yes for that PR.
