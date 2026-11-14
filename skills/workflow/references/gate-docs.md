# Gate documents — every step ends in a file

> Read when: either loop runs, in either mode. Each step ends by writing its gate document, and the next step starts
> by reading it. This file owns the chain: which file each step writes, what it holds, where it lives, and when the
> chain is also committed into the pull request.

A loop step has passed when its document exists, not when the conversation remembers it. The chain of documents is
the item's audit trail: who asked, what the agents produced, what was decided, by whom, on which sha. A resumed run,
the verifier, the learner and a reviewer all read it, so none of them depends on a chat that may be gone.

## The run folder `R`

`R` = `DL/runs/<YYYY-MM-DD>/<KEY>/`, the same folder in the attended mode and in `--auto`. An untracked item uses its
`LOCAL-<slug>` id as `<KEY>`. When today's `<KEY>/` already exists (the other loop's, or an earlier round of the
same item), the new folder is `<KEY>-<flow>-<n>/`, with `n` the smallest of 2, 3 … not taken.

- **Which folder.** A new item opens `R` on the day its first step runs. A resumed item keeps its folder: of
  `ls -d DL/runs/*/<KEY>/ DL/runs/*/<KEY>-<flow>-*/ 2>/dev/null`, take those whose `card.md` says `item: "<KEY>"` and
  this loop's `flow`, and of those the one whose `card.md` `at` is newest (never the list order: `-` sorts before `/`
  and `10` before `2`). No such folder → the item starts again from step 1.
- **A new folder for a new round.** A hand-off into this loop (`from-n-defect-loop`, a handed-over card), a feedback
  round (changes requested on the PR, or QA bouncing the item before Done) and a reopen each open a new `R` and name
  the earlier folder in `card.md` as `previousRun`. Documents from `previousRun` are read there, never copied and
  never edited: the old trail stays as it was. They stand for this run's steps only where a rule says so:
  - **Feedback round:** `triage.md`, `decisions.md`, `before.md` and `root-cause.md` or `design-note.md` stand from
    `previousRun` (`auto-evidence-and-ship.md` § Feedback rounds). The round writes its own `card.md` (the review
    points quoted), `build.md` (whose Plan vs diff section lists the round's changes after approval), the S2 files,
    `proof.md` and `verify.md` in auto mode, and `ship.md`. A review point that changes what the spec asserts is a new
    criterion: the round writes its own `triage.md` and `before.md`.
  - **Reopen:** only `card.md` of `previousRun` is context; the item runs every step again.
  - **Structural defect handed to n-develop-loop:** it re-runs its spec red on the new worktree and writes its own
    `before.md`; its design note reads the defect's `root-cause.md` in `previousRun`.
- **Git-ignored.** `DL/runs/` holds its own `.gitignore` (`*` and `!.gitignore`). develop-init writes it, and a run
  that finds it missing writes it before the first gate document. So `R` holds raw evidence too (videos, frame
  sheets, attachments), in sub-folders named after the stage. Wherever an older text says `<scratchpad>/<KEY>/`, read
  `R`.
- **A refused write stops the run.** Before taking the first item, create `DL/runs/<YYYY-MM-DD>/` and check
  `DL/runs/.gitignore` as a probe. When that or a later gate-document write is refused (the working state is still
  under `.claude/` and nobody can approve it), stop before taking an item, or at once when one is in flight. Say which write was refused and recommend moving
  the working state (`W/scripts/move-state.sh`, offered by develop-init). Never keep gate documents anywhere else:
  a chain split across two places is not a trail.

`DL/runs/<YYYY-MM-DD>/run.md` is that day's run log for both loops and both modes. Each run or pass appends one
section (the S6 report, or auto mode's pass log) and never rewrites an earlier one.

## The header every gate document starts with

YAML front matter, one key per line, every value in double quotes, so the file still renders when the chain is
committed into a docs tree. Inside a value write a double quote as `'` and a backslash as `/`: these two are the only
changes allowed to a person's exact words.

```
---
gate: "<the step, in words: card, triage, decision round, reproduce, root cause, design, build, ship>"
item: "<KEY>"
flow: "<dev | defect>"
mode: "<attended | auto>"
read: "<the gate documents this one started from, by file name; previousRun: <folder> when there is one>"
decision: "<passed | parked: <ledger state> | handed to <loop> | not reproduced | n/a>"
decided-by: "<person: <name or the user in chat> — '<their words>' | rule: <file § row> | agent: <name>, checked by the orchestrator>"
base: "<sha>"
head: "<sha | none yet>"
at: "<YYYY-MM-DD HH:MM>"
---
```

- `decided-by` quotes a person's words exactly and never paraphrases an approval. No secret, token or personal data
  goes into any gate document. An approver's name, as config § Team writes it, is fine.
- A document that is appended to (`decisions.md`, `build.md`, `ship.md`) gives each later section its own heading
  line: `## <what> — <YYYY-MM-DD HH:MM> @ <head sha>`. The metrics read those times.
- The agents' own files (`review.md`, `review-security.md`, `review-performance.md`, `qa.md`, `verify.md`) keep the
  format their agent writes, with no header. The orchestrator records that it checked them in `build.md`'s Plan vs
  diff section and in the ship gate table.

## The chain

| Step | Document in `R` | Written by | Holds (after the header) | Read next by |
|---|---|---|---|---|
| 1 Read the board | `card.md` | orchestrator | every field and label, links, comments newest first, all minus personal data; attachments described (never copied); a spec path or request for an untracked item; `previousRun` when there is one | step 2 |
| 2–3 Triage, check the spec | `triage.md` | orchestrator | route and verdict with the reason (defect: actionable / needs-info / by-design / structural, with the cited line, decision id or commit; dev: ready or the gap, and the size); `AC-1 … AC-n` with `(derived)` marked; every source read, newest first, with each conflict and who settles it; the **AC → test table**; the branch name; each tracker comment posted at this step (a question, a by-design or structural variant). In auto mode it also holds what `auto-triage.md` § What triage writes lists | the decision round, step 4 |
| Decision round | `decisions.md` | orchestrator | **Attended:** the questions about this item, each as asked, with its options and the recommendation, and the answer word for word with who gave it. A question shared by several items (the push of every `fix/*` branch) is copied into each. A question left out over the 4-question limit reads `not asked: over the limit`, followed by the recommended option taken or `parked`. Then each `ASSUMPTION`; the push yes and the branches it names; on the dev route, **files shown**: the file list of the design note draft the round showed. **Auto:** written at A3 every time, starting with `no decision round (auto)` and the assumptions, then each gate that parked the card, with the question as posted. In both modes, later answers and `DECIDED` lines are appended | step 4, S4 (push), the verifier |
| 4 Reproduce / pin the goal | `before.md` | orchestrator, from the agent's report | spec path and `shasum -a 256`, base sha, the red command and its failing line, why that line is the card's symptom, evidence paths; not reproduced: what was tried and what is needed | steps 5–6, PROOF |
| 5 Root cause (defect) | `root-cause.md` | orchestrator | the hypotheses ranked, the one confirmed at `path:line`, the guards checked, why it explains the red run exactly, the scope fence (the files the fix may touch); its Changes after approval section | step 6, review, the verifier |
| 5 Design (dev) | `design-note.md` | orchestrator | n-dev's design note with the work packages and its Changes after approval section. Attended mode writes the draft at the decision round. For Large work the repo copy is the note, and `R/design-note.md` is one line pointing to it | step 6, review, the verifier |
| 6 Build / fix | `build.md` | orchestrator, from each builder's or fixer's report | one section per WP or fix round: tests red → green with the pasted lines, checks with pasted lines, the structure check's `RESULT` line, commit sha, files, each `DECIDED` line; then the Plan vs diff section (§ Plan vs diff) | step 7 |
| 7 Verify | `review.md`, `review-security.md`, `review-performance.md`, `qa.md`; the Plan vs diff section of `build.md` | the S2 agents; you | as `stages.md` § S2 says | the fix round, S4, the verifier |
| 7 Verify (auto) | `proof.md`, `verify.md` | you, from QA's report; `loop-verifier` | as `auto-mode.md` § Run files says | A8 |
| 8 Open the PR | `comment.md`, `ship.md` | orchestrator | the comment as posted (and its id); the ship gate table, each gate with its command and result line; push: who approved it (the `decisions.md` line, or the standing approval's date and words), the PR, the lane; every evidence clip's path; the plan-vs-diff result line quoted from `build.md`; the Metrics section | step 9, S6 |
| 9 Merge or approve | the Merge section of `ship.md` | orchestrator | the class, who merged or approved (their words), the merge sha; or `waits for a person — PR #N` | S6 |
| After | `DL/runs/<YYYY-MM-DD>/run.md` | orchestrator (auto: also `loop-learner`, in `learn.md`) | the S6 report: items and their states, open questions with recommendations, lessons, the eval proposals (attended), the metrics of each item | the next run's S0 |

A document that would hold nothing is still written when its step runs, so a missing file always means the step did
not run. A dev item has no root cause, a defect has no design note, and an item with no question writes
`decisions.md` with `no decision: nothing to ask` and the assumptions taken.

**Reproduce and fix in one dispatch** (a small, certain web or CSS defect, n-defect-loop step 5): before the dispatch,
write `root-cause.md` with the suspected `path:line`, marked `suspected — confirmed by the fixer's red run`, and the
fence. Write `before.md` from the fixer's red run before `build.md`.

### No file, no pass

- A step starts by reading the documents its row names. A missing one means the earlier step did not pass: go back
  and run that step (or write its document from the step's real output, never from memory), then go on.
- A parked item's last gate document says where and why it parked, and the ledger row's evidence field names `R`.
- S0's resume reads `R`, not the conversation.

## Plan vs diff

The plan is the design note (dev) or the root cause's scope fence (defect). The code may depart from it only when the
plan is updated too.

1. **During the build.** When a builder's or fixer's report touches a file outside its work package or fence, with a
   cited reason the orchestrator accepts, write the file into the plan's Changes after approval section (file,
   reason, which report) before the next dispatch. For Large work, the repo copy of the note gets the same change, in
   the same local commit as the code that needed it.
   - A change that needs a decision is not accepted here: see `stages.md` § Decision round › a decision that appears
     later.
   - Accepting a file does not widen the push yes. On the dev route a file that is not in `decisions.md` under files
     shown needs a fresh yes at S4 (`awaiting-push`), unless a standing approval covers it. For Large work the files
     shown always include the note's repo path. On the defect route the round's yes is bounded by the item's criteria
     and by a schema, contract or dependency change (`stages.md` § S4, item 3), since the round runs before the root
     cause exists.
2. **At verify** (S2, after the reviewers and QA report): compare `git diff --name-only <base>...<branch>` with the
   files the plan names, including its changes after approval. Leave the test globs, the feature docs, the repo copy
   of a Large design note and the gate-doc copy out of the diff side. Write the Plan vs diff section of `build.md`: `match`, or each file outside the
   plan and each planned file not changed. End it with one result line, `plan vs diff: match | drift <n> files`.
3. **Drift** is a finding for the fix round, and the orchestrator owns it. Either the plan gains the file with its
   reason (a change after approval, under item 1's push rule) or the code comes back inside the plan. Drift never
   ships unexplained.

## Metrics

The Metrics section of `ship.md` records the item's leading indicators, one line each. They are computed from the
headers, the section headings and the ledger, never estimated:

| Metric | From |
|---|---|
| read → spec | `card.md` at → `triage.md` at |
| spec → red | `triage.md` at → `before.md` at |
| red → green | `before.md` at → the last green section of `build.md` |
| fix rounds used | 0, 1 or 2 (S2) |
| first-pass verify | yes when the first S2 round had no finding at blocker or should-fix and QA was green |
| review findings | per lens: blocker / should-fix / note, and how many were closed |
| plan vs diff | the result line from `build.md` |
| decisions | asked / assumed / decided later (`decisions.md`) |

S6 copies each item's metrics into `run.md`. In auto mode, the learner's weekly review adds the first-pass verify
rate and the plan-drift rate to its trend.

## Eval proposals — a mistake becomes a test of the loop

A lesson tells the next run what to do; an eval proves the plugin still does it. Each of these gets an eval proposal:

- the user corrected what the loop did, and the correction is about the procedure, not this product's code;
- a card the loop shipped was reopened, or its PR got changes requested, for a reason the procedure should have
  caught;
- the verifier refuted a claim for a reason a rule should have prevented.

There is one writer per mode. In attended mode, the orchestrator writes the proposal in S6 under Eval proposals in
`run.md`. With `--auto`, only the learner writes it, as `DL/knowledge/proposals/<date>-eval-<slug>.md`.

A proposal holds four things, in the shape of the plugin's `evals/*/case.yaml`:
- the situation, as a short prompt with no product names and no personal data;
- what the loop did;
- what it should have done;
- the grader that would tell the two apart: a file that must or must not exist, a pattern in the trace or the last
  message, or an LLM criterion.

A person adds it to the plugin's `evals/`; the loop never edits the plugin.

## Commit the chain into the PR (config § Docs › gate docs)

`R` is local and git-ignored. When config § Docs › gate docs is `on`, the readable part of the chain also goes into
the pull request, so the reviewer and git history hold the trail. With no such line, or `off` (the default), nothing
is committed: the chain stays in `R`, and `ship.md` is the place to look.

1. **Copy.** In S4, before the squash, copy `triage.md`, `decisions.md`, `root-cause.md` or `design-note.md`, and
   `build.md` into `<worktree>/<path>/<KEY>/` (default path `docs/changes/`). Never copy the review files, `qa.md`,
   `verify.md`, videos, `card.md` or anything that holds raw attachments. A feedback round refreshes the copies in
   its own commit.
2. **Scrub.** Rewrite absolute paths, ports and worktree names as repo-relative paths or `<local>`. Grep the copies
   for secrets and personal data; a hit is removed. Then the security pass:
   - list every finding in `review-security.md` whose state is not `closed` (open, not reproduced, note, outside the
     change);
   - remove from the copies every line that names its id, its `path:line` or its input;
   - grep the copies again for those paths. A hit still there → copy nothing, keep the chain in `R`, and say so in
     `ship.md`.

   This fails closed on purpose: an open finding in a file the item also changed always matches the copies' file
   lists, so such an item commits no copy. A line that describes a weakness only in words is not caught by the grep,
   which is why the copy leaves out the review files and `card.md` altogether.
3. **Commit.** The copies ride in the item's one squashed commit. The builder shas inside them name local commits
   that the squash replaced; `ship.md` names the squashed sha. The copies are left out of every size count (the
   single-review size, the fences, the auto-merge class, whose Safe kind row allows the path). They need no fresh push
   yes, and neither the comment nor V8 lists them.

## Sources

- Louis Claxton, "The AI-native SDLC playbook", Claude, 21 August 2026 —
  https://claude.com/resources/articles/the-ai-native-sdlc-playbook: each stage ends by committing an artifact the
  next stage reads; the chain is the audit trail; the plan is updated in the same commit when the build departs from
  it; leading and lagging indicators per stage; each incident becomes a permanent regression eval.
