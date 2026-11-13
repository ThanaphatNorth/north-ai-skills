---
name: n-develop-loop
description: Development loop of the 90north-develop plugin — takes a story, task, improvement, change request or spec (a Jira or local-board key, a spec file, a plain request, or --next) through 9 steps, from the board to a PR in the review lane: acceptance specs red, the n-dev design note and work packages, a test-first build by dev-builder subagents, code, security and performance review plus QA, a demo video. Attended, it asks every question in one round before anything is built, then runs to the end; --auto runs it unattended and parks a card that needs a person. Only a low- or no-impact change inside a standing approval merges on its own. Use when the user says "develop loop", "build <KEY>", "implement this story/spec", "new feature", "change requirement", "pick the next story", or a schedule fires it. Defects go to n-defect-loop.
argument-hint: "<KEY | spec path | request | --next> [--auto] [--dry-run]"
---

# 90north-develop · n-develop-loop

You are the **orchestrator** (the main conversation): you decide, design, dispatch and check, and `dev-builder`
subagents write the code.
- **Shared parts** live in the workflow skill (`W = ../workflow/` from this skill's base directory): the stages
  S0–S6, the dispatch safety block, the tracker (`W/scripts/tracker.sh`, Jira or the local board) and the auto
  mode. Read `W/references/stages.md` once per run.
- **Code:** every line follows n-dev (`../n-dev/`).

## Calls and modes

| Call | Does |
|---|---|
| `/90north-develop:n-develop-loop <KEY>` | attended: one tracker item |
| `/90north-develop:n-develop-loop <spec path \| request>` | attended: one untracked item. Its id is `LOCAL-<slug>`; tracker steps are skipped and the ledger is kept |
| `/90north-develop:n-develop-loop --next` | attended: the top item of config § Dev flow's ready query that no ledger row owns |
| `/90north-develop:n-develop-loop --auto [--dry-run] [<KEY>]` | unattended: one pass per `W/references/auto-mode.md` |
| `/loop 60m /90north-develop:n-develop-loop --next`, or `… --auto` on a schedule (`W/templates/auto-scheduled-task.md`) | attended: resume items whose gate was answered, else take the next one. Unattended: one pass per tick |

The two modes differ in who answers:
- **Attended:** every question comes in one decision round, before anything is isolated or built
  (`W/references/stages.md` § Decision round). After it the run goes to the end: an item that still needs a person
  parks, and the rest goes on.
- **`--auto`:** nobody answers. A gate parks the card with a question on it, and the pass goes on. In auto mode a
  Large item never builds: its design note is posted as the solution.

## Step 0 · Before the run
Run S0 in `stages.md` with flow `dev`. Config needs § Dev flow (legacy `.claude/defect-loop/` → run
`/90north-develop:develop-init` first). In auto mode, run A0 as well.

## 1 · Read the board
- **Attended.** Take the item named in the call, or `--next`.
- **Auto.** Run A1 follow-ups, then A2 scout and lock on this loop's queue.

Then:
1. `W/scripts/tracker.sh get <KEY>`: the description, every comment and the attachments. Download the designs and
   screenshots (`W/scripts/tracker.sh download`) and **look** at them.
2. Open the linked spec, decision log and design files that config § Spec sources names.
3. A structural defect handed over on a person's yes: ledger `from-n-defect-loop KEY`. Steps 2–3 and the decision
   round run as usual. Step 4 then isolates a new `feat/<KEY>-<slug>` worktree and copies the defect's red spec in
   as WP-0, with no new spec to write.

Attachments may hold personal data: describe them, never copy them.

## 2 · Triage
1. **Route** it (`W/SKILL.md` § Route the work). If it is really a defect, hand it to **n-defect-loop**: ledger
   `handed-to-n-defect-loop`, or the hand-off label in auto mode. Then stop.
2. **Ready** means a goal, acceptance criteria that can each become a check, the screens or API it touches, the
   roles, and no open dependency. A missing piece the user in chat can supply goes to the decision round. One only
   the reporter or PO knows → comment once asking exactly for it, ledger `needs-info`, and go on with the next item.
3. **Size** it with n-dev's scope dial. It is **Large** when it:
   - adds a module or package;
   - changes state shape, a DB schema or a public interface (API↔client contract, events, exported types);
   - crosses repos;
   - or passes config § Dev flow's fence (default more than 8 files or 400 lines).

   In attended mode every size runs step 3, then the decision round, before anything is isolated or built; steps
   4 and 6 follow. In auto mode, Large work is need-dev (`W/references/auto-triage.md`).

## 3 · Check the spec
1. Write the criteria as a numbered list `AC-1 … AC-n`. Take them from the ticket's own list when it has one; mark
   any you derive `(derived)`.
2. Read every comment newest first, the decision log, and the area's feature doc when config § Docs is on
   (`W/references/feature-docs.md`). When a comment, a linked spec or an existing rule `R-n` disagrees with the
   ticket and nobody settled it, which one wins is a decision: never pick yourself. It goes to the decision round,
   or onto the ticket (`needs-info`) when only the reporter or PO can say.
3. Write the **AC → test** table: each criterion → the test level (e2e for user-visible criteria, API or integration
   for the rest) and the spec file.

## Decision round (attended) · ask once, then build
Run `W/references/stages.md` § Decision round with this loop's inputs:
1. Draft step 5's design note now, for every size. Orient and the note are read-only and need only the base
   checkout.
2. This loop's decisions: readiness gaps and source conflicts the user can settle (steps 2–3), the design gate
   (step 5.3), and the push of `feat/<KEY>-<slug>` when no standing approval covers it.
3. One message. An approval given here covers the note as shown, so steps 4–9 run with no second stop.

## 4 · Pin the goal: acceptance specs go red
1. S1 Isolate (`stages.md`): a worktree on `feat/<KEY>-<slug>`, an anchor commit, the stack.
2. Dispatch `90north-develop:dev-builder` with **WP-0 acceptance**. It writes the specs from the AC → test table,
   runs them against the stack, and sees each go **red because the feature is missing**. A locator timeout, a login
   error or missing data does not count as red. Before existing behaviour is extended, the same WP adds
   characterization tests that pass now.
3. Keep the red output: it is the "before" of the story.

## 5 · Design: the note and the work packages (n-dev steps 1–3)
Attended mode drafted this note for the decision round; here it gains WP-0's red runs and is saved. Auto mode
writes it now.
1. **Orient** (n-dev step 1) in the base checkout: commands, extension points, state owners, reuse inventory, and
   the architecture profile.
2. **Design note** from `../n-dev/templates/design-note.md`: module map, state ownership, extension plan, test seams,
   the AC → test table, each feature doc and the rules `R-n` it will add or change, and the **work packages**
   (WP-1 … WP-n). Each WP names:
   - its files and a one-sentence responsibility;
   - its success criteria and test seam;
   - the WPs it depends on.

   Standard work: the note goes to `<scratchpad>/<KEY>/design-note.md` (`DL/runs/<date>/<KEY>/` in auto mode).
   Large work: the repo's docs folder per config, with the interface designed two ways and compared.
3. **Gate.** What config § Dev flow › Design gate names is a decision: by default Large work, a trade-off the
   user would care about, and anything on its always-ask list.
   - **Attended:** it was asked in the decision round, with the note shown short (the AC table, the WPs, the
     decision asked). Approved → build. No answer → ledger `awaiting-design-approval`, and the run takes the next
     item.
   - **Auto:** need-dev, with the note posted as the solution.

   This gate is the team's rule and may be stricter than n-dev § Questions: an additive schema or interface change
   still asks here unless config says otherwise. Standard work with no such point continues, and the report says
   so.

## 6 · Test-first build
1. Dispatch `90north-develop:dev-builder` once per WP, in dependency order: core first, wiring last. WPs run in
   parallel only when the design note shows they touch disjoint files. Never put two builders in one worktree at
   once.
2. Each brief carries:
   - the safety block, the design note path, and the WP (files, responsibility, criteria, seam);
   - the worktree and branch, the stack, and the config § Checks and § Team lines;
   - n-dev's absolute path.

   Each builder returns tests seen red → green, the checks, the structure-check result and a local commit.
3. Check every report against its WP before the next dispatch:
   - every criterion is covered;
   - every pre-existing file changed only by a wiring diff or a cited reason;
   - nothing changed outside the WP.

   A builder reporting `NEEDS-DECISION`:
   - **Attended:** settle it with `stages.md` § Decision round › a decision that appears later. Decide it when the
     design note already settles it, or take a reversible option inside the criteria and record it. Otherwise park
     the item (ledger `blocked-needs-human`) and go on.
   - **Auto:** always the stopped path.
4. A bug found in code that existed before this story is not fixed here: note it as a defect for n-defect-loop
   (`W/SKILL.md` § Handoffs).
5. **Feature doc** (config § Docs on): write it yourself in the worktree, per `W/references/feature-docs.md`, as a
   local commit `docs(<area>): … (<KEY>)`. Each rule added or changed gets its source and its test. Builders
   never write it. No rule changed → no doc change; the report says so.
6. Done when every WP is committed, WP-0's acceptance specs are **green** against the stack, and the feature doc
   (if config § Docs is on and a rule changed) is committed.

## 7 · Verify and record
1. S2 Verify (`stages.md`). The reviewer gets the diff, the ticket, the design note and the AC table. Two
   `risk-reviewer` runs read the same diff for security and for performance. QA runs every acceptance spec twice
   and n-dev's structure check (`../n-dev/scripts/structure_check.py --base <base>`). Fix rounds go back to step 6
   with all findings, with a budget of 2.
2. S3 Evidence: the `demo` clip walks AC-1 … AC-n in order. Add `before` when an existing screen changed.
3. Auto mode adds A6 PROOF and the A7 verifier gate: nothing the verifier refutes is published.

## 8 · Open the PR
In auto mode, pick the ship class (step 9) first: it decides the lane.

S4 Ship with `templates/jira-comment.md`, whose §2 carries the `Docs:` line. In auto mode, adjust it as
`W/templates/auto-comments.md` § Proof comment says.
- Push per config § Push policy, or the decision round's yes for this branch, and open the PR.
- Move the item to config § Dev flow's review lane (usually Code Review). In auto mode, an auto-merged item goes to
  the after-merge lane after step 9 instead (ledger `merged`).
- Ledger `in-review` after the PR, or `awaiting-push` when not pushed.

## 9 · Merge, or a person approves
The ship class decides. `W/references/auto-evidence-and-ship.md` § Ship classes owns the gates:
- **Auto-merge** happens only in `--auto`, because it needs the verifier, only for a low- or no-impact change that
  passes every gate there, and only with a standing approval in config § Push policy that names merge.
- **Everything else** waits for a person. They review the PR and merge it, or tell you in chat to merge that one
  PR. Attended mode never auto-merges.

A new feature with a schema, contract or public-interface change never reaches the auto-merge class.

## After · Clean up and learn
S5 Clean up, then S6 Learn (tag lessons `[dev]`). Auto mode runs A9: outcomes, then the learner.

## Gates — where an item waits for a person

| Gate | Ledger state | Attended | Auto |
|---|---|---|---|
| not ready, or sources conflict | `needs-info` | the decision round when you can settle it; else a comment on the ticket | question on the card |
| really a defect | `handed-to-n-defect-loop` | hand-off row | hand-off label |
| design approval (config § Dev flow › Design gate) | `awaiting-design-approval` / `solution-posted` | the decision round: you approve or pick an option | the design note on the card; a person takes it |
| builder decision | `blocked-needs-human` / `stopped` | settled by the note or a reversible option; else parked | what was found, on the card |
| push | `awaiting-push` | the decision round's yes, or a standing approval | a standing approval, else it waits for your yes |
| 2 fix rounds used | `blocked-needs-human` / `stopped` | parked | on the card |

## Never (on top of `stages.md` § Never)
- Write production code before the design note exists and its gate is passed.
- Widen scope beyond the acceptance criteria: an extra option, flag or screen becomes a proposal in the comment.
- Change a pre-existing file beyond a wiring diff without a cited reason in the design note.
- Fix an unrelated pre-existing bug on a feature branch.
- Merge a PR outside the auto-merge class without a person's explicit yes for that PR.
