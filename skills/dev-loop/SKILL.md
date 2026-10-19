---
name: dev-loop
description: Development flow of the 90north-develop plugin — take one story, task, improvement or spec (a Jira key, a spec file, a plain request, or --next from the board) from ready to reviewed PR. Checks it is ready, sizes it, writes the n-dev design note and stops for the user's approval when it is Large or changes schema, state shape or a public interface, writes an acceptance spec that goes red, builds work packages test-first through dev-builder subagents on an isolated worktree and stack, verifies with code review + QA in parallel, records a demo video that plays inline in Jira, writes the 3-part comment (1. What was built 2. How it works 3. Verification), pushes per policy and moves the item to the review lane, then learns. Can run on a loop (/loop 60m /90north-develop:dev-loop --next) but never passes a design gate by itself. Use when the user says "dev loop", "build <KEY>", "implement this story/spec", "pick the next story", or a loop fires this skill. Defects go to defect-loop.
---

# 90north-develop · dev-loop

You are the **orchestrator** (the main conversation): you decide, design, dispatch and check; `dev-builder` subagents write the code. The shared stages S0–S6, the dispatch safety block and the Jira scripts live in the workflow skill (`W = ../workflow/` from this skill's base directory): read `W/references/stages.md` once per run. The discipline every line follows is n-dev (`../n-dev/`).

## Input

| Call | Does |
|---|---|
| `/90north-develop:dev-loop <KEY>` | one tracker item |
| `/90north-develop:dev-loop <spec path \| request>` | one untracked item: id `LOCAL-<slug>`, tracker steps skipped, ledger kept |
| `/90north-develop:dev-loop --next` | the top item of config § Dev flow's ready query that no ledger row owns |
| `/loop 60m /90north-develop:dev-loop --next` | resume items whose gate was answered, else take the next one; one item in flight at a time unless config allows more |

## D0 · Before the run
S0 in `stages.md` with flow `dev`. Config needs § Dev flow (legacy `.claude/defect-loop/` → run `/90north-develop:develop-init` first).

## D1 · Pull and ready check
1. `W/scripts/jira-get.sh <KEY>` — description, every comment, attachments; download and **look** at designs and screenshots (`W/scripts/jira-download.sh`). Open the linked spec, decision log and design files config § Spec sources names. Attachments may hold personal data: describe, never copy.
2. Classify (`W/SKILL.md` § Route the work). It is really a defect → hand to defect-loop (ledger `handed-to-defect-loop`), stop.
3. **Ready** means: a goal, acceptance criteria that can each become a check, the screens or API it touches, the roles, and no open dependency. Write the criteria as a numbered list `AC-1 … AC-n` (from the ticket's own list when it has one; when you derive them, mark them derived). Missing a piece → comment once asking exactly for it, ledger `needs-info`, stop.

## D2 · Size and design (n-dev steps 1–3)
1. **Orient** (n-dev step 1) in the base checkout: commands, extension points, state owners, reuse inventory.
2. **Size** with n-dev's scope dial. It is **Large** when it adds a module or package, changes state shape, DB schema or a public interface (API↔client contract, events, exported types), crosses repos, or passes config § Dev flow's fence (default > 8 files or > 400 lines).
3. **Design note** from `../n-dev/templates/design-note.md`: module map, state ownership, extension plan, test seams, plus an **AC → test** table (each criterion → test level and file) and the **work packages** (WP-1 … WP-n): each one names its files, one-sentence responsibility, success criteria, test seam and the WPs it depends on. Standard: the note goes to `<scratchpad>/<KEY>/design-note.md`. Large: in the repo's docs folder per config, with the interface designed two ways and compared.
4. **Gate.** Large, a trade-off the user would care about, or anything config § Dev flow lists as always-ask → show the note (short: AC table, WPs, the decision asked) and stop with ledger `awaiting-design-approval`. On a loop, take the next item meanwhile. Standard with no such point → continue and say so in the report.

## D3 · Isolate and pin the goal
1. S1 Isolate (`stages.md`): worktree on `feat/<KEY>-<slug>`, anchor commit, stack.
2. Dispatch `90north-develop:dev-builder` with **WP-0 acceptance**: write the acceptance spec(s) from the AC → test table — e2e for user-visible criteria, API or integration tests for the rest — run them against the stack and see each go **red because the feature is missing** (not a locator timeout, login error or missing data). Before extending existing behaviour, the same WP adds characterization tests that pass now.
3. Keep the red output; it is the "before" of the story.

## D4 · Build
1. Dispatch `90north-develop:dev-builder` once per WP, in dependency order, core first and wiring last. WPs run in parallel only when the design note shows they touch disjoint files; never two builders in one worktree at once.
2. Each brief: the safety block, the design note path, the WP (files, responsibility, criteria, seam), worktree and branch, stack, config § Checks and § Team lines, n-dev's absolute path. Each builder returns tests seen red → green, checks, structure-check result and a local commit.
3. Check every report against the WP before the next dispatch: criteria covered, every pre-existing file changed only by a wiring diff or a cited reason, nothing outside the WP. A builder reporting `NEEDS-DECISION` → decide it if the design note already settles it, else ask the user (ledger `blocked-needs-human`).
4. A bug found in code that existed before this story → not fixed here: note it for a defect proposal (`W/SKILL.md` § Handoffs).
5. Done when every WP is committed and WP-0's acceptance specs are **green** against the stack.

## D5 · Verify, evidence, ship
1. S2 Verify (`stages.md`). The reviewer gets the diff, the ticket, the design note and the AC table; QA runs every acceptance spec twice and n-dev's structure check (`../n-dev/scripts/structure_check.py --base <base>`). Fix rounds go back to D4 with all findings, budget 2.
2. S3 Evidence: the `demo` clip walks AC-1 … AC-n in order; add `before` when an existing screen changed.
3. S4 Ship with `templates/jira-comment.md`, target lane = config § Dev flow (usually Code Review). Ledger `in-review` after the PR, `awaiting-push` when not pushed.
4. S5 Clean up, S6 Learn (tag lessons `[dev]`).

## Gates — where the loop stops for a person

| Gate | Ledger state | Resumes when |
|---|---|---|
| not ready | `needs-info` | the ticket gets the missing piece |
| design approval | `awaiting-design-approval` | the user approves or picks an option in chat |
| builder decision | `blocked-needs-human` | the user answers |
| push | `awaiting-push` | the user says yes for that branch, or a standing approval covers it |
| 2 fix rounds used | `blocked-needs-human` | the user decides |

## Never (on top of `stages.md` § Never)
- Write production code before the design note exists and its gate is passed.
- Widen scope beyond the acceptance criteria: an extra option, flag or screen becomes a proposal in the comment.
- Change a pre-existing file beyond a wiring diff without a cited reason in the design note.
- Fix an unrelated pre-existing bug on a feature branch.
