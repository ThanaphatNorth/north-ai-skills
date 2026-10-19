---
name: defect-loop
description: Defect flow of the 90north-develop plugin — run one sweep of the project's Jira defect board (or one defect by key) and close each defect end-to-end — pull every open defect (board and backlog), triage, reproduce with a red e2e on an isolated stack, find the root cause, fix test-first through subagents, verify with code review + QA in parallel, record before/after videos that play inline in the Jira comment, write the 3-part comment (1. Can it be reproduced? 2. Root cause 3. Solution) and move the ticket to the QA lane. Reads all project facts from .claude/90north-develop/config.md (run /90north-develop:develop-init first). Built to run on a loop (/loop 30m /90north-develop:defect-loop) and to improve itself from lessons after every sweep. Use when the user says "defect loop", "sweep the board", "review jira defects", "fix bug <KEY>", "clear the bugs to Ready for QA", or a loop fires this skill. Stories and changes go to dev-loop.
---

# 90north-develop · defect-loop

You are the **orchestrator** (the main conversation): you read Jira, decide, dispatch subagents, check what they return and write to Jira. The shared stages S0–S6, the dispatch safety block and the Jira scripts live in the workflow skill (`W = ../workflow/` from this skill's base directory): read `W/references/stages.md` once per sweep. Every fix follows n-dev (`../n-dev/`).

## Input

| Call | Does |
|---|---|
| `/90north-develop:defect-loop` | one sweep of the whole open-defect query |
| `/90north-develop:defect-loop <KEY>` | one defect |
| `/loop 30m /90north-develop:defect-loop` | keep sweeping; continuous mode between ticks while cards remain |

## F0 · Before every sweep
S0 in `stages.md` with flow `defect`, plus this skill's `references/core-lessons.md` in full. A legacy `.claude/defect-loop/` folder works as `DL` (its `ledger.md` is the defect ledger) until develop-init migrates it.

## F1 · Pull and triage
1. **Pull** config § Defect flow's open-defect query (board + backlog, ids not names) with `W/scripts/jira-search.sh '<query>'`, run its sanity query, and diff the keys against the ledger. Never shortcut to a time window. For each ticket not skipped: `W/scripts/jira-get.sh <KEY>`; download attachments with `W/scripts/jira-download.sh <KEY> <scratchpad>/<KEY>/attachments` and **look** at screenshots and videos. Attachments may hold personal data: describe, never copy into the repo or a comment.
2. **Triage** each ticket:
   - `actionable` — symptom, screen, role and expected result are clear enough to script.
   - `needs-info` — comment once asking for the missing piece (steps, role, data, screenshot); ledger `needs-info`.
   - `by-design / change request` — the code already does what the current spec says (cite the line / decision id, after checking "Revised by / Reversed by"), a merged change removed the feature (cite the commit), or the ticket asks for behaviour that never existed. Record current behaviour with a GREEN verification spec; comment with the by-design variant; ledger `blocked-needs-human`; the ticket stays in its lane. Name the stale document when one is. If the PO turns it into a story → dev-loop (`W/SKILL.md` § Handoffs).
   - `structural` — per config § Defect flow fence (schema/migration, auth, reported figures, API↔web contract, deploy, > 5 files or > 200 lines). Reproduce + root cause + options; comment with the structural variant; no build without the user's yes, and on a yes the build runs in **dev-loop from D2** with this red spec as its acceptance spec.
3. Process actionable tickets in batches of up to 3 in parallel, each on its own worktree and stack, within the preview-server cap.
4. **Continuous mode:** when a batch finishes and open, unhandled cards remain, start the next batch at once. Handled = in the QA lane with our fix, or commented with evidence and ledgered in a parked state. Stop only when every card is handled.

## Per ticket

### F2 · Isolate and reproduce
1. S1 Isolate (`stages.md`), branch `fix/<KEY>-<slug>`. Ticket data from the reporter's files goes into a **copy** of the test DB.
2. Dispatch `90north-develop:defect-repro` with the safety block, the ticket text verbatim (minus personal data), comments, attachment paths, worktree, web URL, login (role → test account, how to log in), the config § Checks e2e lines and output folder `<scratchpad>/<KEY>/repro`. It returns a spec, the **red** output and the raw video.
   - Red for the reported reason → reproduced; keep the video as `before`.
   - Not red after an honest attempt (it lists what it tried) → try once yourself in the browser pane, and on the reporter's environment if named. Still nothing → comment what was tried and what is needed, ledger `cannot-reproduce`, keep the lane. Never fix an unreproduced defect.

### F3 · Root cause
Rank 3–5 falsifiable hypotheses (the `diagnosing-bugs` skill when installed), confirm one at `path:line`, name the guards you checked. It must explain the red run exactly. Small and certain web/CSS defects may be reproduced and fixed by one fixer dispatch that writes the measuring spec red first.

### F4 · Fix
Dispatch `90north-develop:defect-fixer` with the safety block, ticket, red spec + failing line, root cause `path:line`, worktree, scope fence, config § Checks and § Team lines, output folder, and n-dev's absolute path with its structure check `../n-dev/scripts/structure_check.py --base <base>`. It writes a regression test red → fix → green, runs the checks and commits locally `fix(<area>): <summary> (<KEY>)`.

### F5 · Verify, evidence, ship
1. S2 Verify (`stages.md`): the reviewer's spec is the ticket + root cause; QA runs the defect spec twice. Fix rounds go back to F4, budget 2.
2. S3 Evidence: `before` (red) and `after`.
3. S4 Ship with `templates/jira-comment.md` (before video under §1, after under §3), target lane = config § Defect flow QA lane. Ledger `ready-for-qa` after the move. Partial fix (the rest needs a decision) → the partial variant; the ticket stays in its lane.
4. S5 Clean up, S6 Learn (tag lessons `[defect]`; promote defect-only rules into `references/core-lessons.md`, shared ones into the workflow skill's).

## Never (on top of `stages.md` § Never)
- Fix a defect that was not reproduced red in this session.
- Build a structural change inside this loop — it goes through dev-loop's design gate.
- Edit the defect spec to make it pass.
