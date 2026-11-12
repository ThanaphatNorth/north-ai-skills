# Evidence and ship — one spec run twice, the verifier gate, and the ship classes

> Read when: auto mode reaches A4 (BEFORE), A6 (PROOF), A7 (verifier outcome) or A8 (ship). The stage mechanics (isolate, review + QA, video conversion, comment posting) are in `W/references/stages.md`; this file adds what the unattended flow needs on top.

Every `do-now` card is proven the same way, whatever its type. The card's **own** spec fails before the change and passes after it, both runs on evidence a QA person can watch, and that evidence goes in one comment on the card.

## One spec, run twice

| Step | What | Must produce | Otherwise |
|---|---|---|---|
| BEFORE (A4) | the spec written from `triage.md`'s AC → test table (n-defect-loop: `defect-repro`; n-develop-loop: `dev-builder` WP-0), run on the isolated stack at the **base** | **red** at the step the card describes, with an assertion message that names the card's symptom; `before` evidence: the clip of the red run in n-defect-loop, and in n-develop-loop when the card changes an existing screen; for behaviour with no screen yet, the pasted red output is the BEFORE evidence | Bug not red after an honest attempt (config › reproduce minutes, one retry with the card's exact data) → `not-reproduced`. Story whose spec already passes → `already-done`. Both: comment with the evidence, `need-info`, unlock |
| BUILD (A5) | builders with n-dev; the spec is the acceptance or characterization test and must stay red until the change makes it green | unit tests red → green, repo checks green, structure check, local commit | stopped path |
| PROOF (A6) | the **same** spec file, unchanged, on the same stack recipe now serving the fix branch, after the base was merged in if it moved; QA runs it twice | **green** both times; `after` evidence; the stack's served sha equals the branch head | back to BUILD (counts as an attempt) |
| FLOW (optional) | before/after sketch of the touched code path, ≤ 12 nodes, as mermaid | PR body; the image in the comment when it helps QA | a code block |

`before.md` records the spec path and its `shasum -a 256`, the base sha, the failing assertion line and the evidence paths. `proof.md` records the same hash, the served sha and both green runs. The verifier compares them.

Red for the wrong reason (a timeout, a login failure, a selector miss, missing data) is not a reproduction. Fix the spec or the stack and run it again; never record it as BEFORE.

Never edit the spec between BEFORE and PROOF. A spec that needed a change was wrong at BEFORE, so record BEFORE again.

## Picture or video

| Card | The comment carries |
|---|---|
| Auto-merge class (copy, locale, layout, field order, validation message) | one annotated screenshot BEFORE and AFTER per screen the card names, with a focus box on the element the card is about; video optional |
| Everything else (behaviour, multi-step flows, needs-review, any reopened card) | video BEFORE and AFTER, plus screenshots of the key frames |

Recording style, so a QA or PO reader can follow without reading the spec: a visible cursor (headless browsers draw none), a focus box on the element each assertion reads, each proving state held about 1.5 s, and captions per card step in the comment language. Captions go **in a band below the frame**, composited from the raw take, never drawn into the page under test. Use the repo's demo or recording helper when config § Evidence names one, else S3's hold script. Scan the frames of every clip before use: no blank, login-only, 404 or error-toast frame may reach the card.

## Verifier outcomes (A7)

`loop-verifier` returns a verdict per claim. Each refuted claim sends the work back to the stage that owns it:

| Refuted claim | Goes back to |
|---|---|
| V1 spec ↔ card mapping, V2 BEFORE reason, V7 BEFORE frames | A4: rewrite the spec or re-record BEFORE, then re-run PROOF |
| V3 proof on the branch, V4 forbidden area, V5 scope, V6 structure, V9 checks ran | A5: the builder, with `verify.md` attached |
| V7 AFTER frames | A6: re-record AFTER |
| V8 comment ↔ diff, wording | you: rewrite the comment draft |
| V10 feature doc ↔ diff | you: fix the feature doc (`feature-docs.md`), then re-run the verifier |

One retry per pass (config › verifier retries). A second `REFUTED` takes the stopped path: the card gets `W/templates/auto-comments.md` § stopped, with the refuted points written as card facts ("the after recording did not show the saved value"), never as claim numbers.

## Ship classes (A8)

Decide after `verify.md` says CONFIRMED, from files and commands only. Write the gate table, with the command and result for each gate, into `ship.md`. When the class differs from triage's prediction, swap the label and say why in one line of the comment, in card language.

### Auto-merge: the loop merges, the card goes to the after-merge lane

All must hold:

| Gate | Check |
|---|---|
| Standing approval | config § Push policy quotes the user's words, dated, and they name **merge** for this class; config › auto-merge is on; the repo matches config's auto-merge repos. `--delete-branch` only when the words also name deleting merged branches |
| Safe kind | every changed file matches config's auto-merge paths (the feature doc path in config § Docs counts as allowed), and the diff holds only the kinds in the auto-merge column of `auto-triage.md` § Decision matrix |
| Small and local | 1 repo, ≤ config max lines counted in non-test source files only (`git diff --numstat` minus config's size excludes; feature docs and their index are excluded like tests), ≤ config max files (feature docs not counted), no new dependency, env var, route, state owner or API call |
| Low blast radius | severity and environment in the auto-merge band, no person's force-review label, not reopened, not a feedback round |
| Structure | the n-dev structure check has no finding on the branch (existing debt listed apart is fine) and the profile is current for the touched paths |
| Proven | `verify.md` all CONFIRMED, BEFORE red and PROOF green on evidence, repo checks green |
| CI | `gh pr checks <n> --watch` all passing; in a repo with no PR workflow, only when config says local checks plus the commit hooks stand in, and the comment says so |
| Base unchanged since PROOF | `git fetch`, then `git merge-base --is-ancestor origin/<base> <branch>` passes. A base that moved after PROOF means the head that would merge was never proven: fall back to needs-review, never merge the base in after the verifier |
| Nobody objected | no change request and no new comment on the PR or the card within config's grace minutes |

Then `gh pr merge <n> --merge` (or the repo's merge style per config, plus `--delete-branch` only as above), post `W/templates/auto-comments.md` § auto-merged, transition to config's after-merge lane, and ledger `merged`. Merge refused by the host (protection, a red check) → fall back to needs-review and say so.

**Post-deploy re-check** is off by default. When config turns it on: re-run the card's spec on the named environment after deploy. Green → log it. Red → open a revert PR for a person, move the card back to In Progress, comment § auto-merge-reverted, and write a lesson plus a proposal to tighten the gate that let it through.

### Needs-review: a person reviews the PR (default)

Anything that fails one auto-merge gate. Push per config § Push policy, open the PR against the base with the PR body below, post the proof comment, move the card to config § Auto mode's **review lane** (default Code Review, the same on both routes: an unmerged fix never goes to the after-merge lane), and ledger `in-review`. The comment names, in one line of card language, why a person reviews it ("changes what the save button does"). No standing push approval → keep the local commit, post § waiting-for-push, and ledger `awaiting-push`. The card stays in its lane.

### Solution-only

Decided at triage, or reached by the stopped path. There is no branch to ship: the card gets the solution (`auto-triage.md` § Solution-only), the need-dev label and an unlock.

## Feedback rounds

A PR the loop opened got changes requested (A1). The feedback file `DL/runs/<date>/feedback/<KEY>.md` holds the PR, the branch, each review point quoted, and `previousRun`, the run folder that shipped it.

1. Check out the existing branch in its worktree; never rebase or rewrite it.
2. The builder of the card's route gets every review point as one fix round: a test pins each point (red → green), and it commits **once**. The message lists the points.
3. The previous run's `before.md` stands as BEFORE: the spec hash must still match. A review point that changes what the spec asserts is a new criterion, so the spec changes, BEFORE is recorded again on the base, and the round is needs-review whatever its size.
4. A6–A7 as usual. In S4, squash only this round's unpushed commits (`git reset --soft origin/<branch>`), push, reply on the PR thread point by point, and post the proof comment's verification part again. The class is needs-review.

## PR body

```
Card: <tracker URL of KEY>

## Problem / request
<from the card, AC-1 … AC-n>

## Cause / design
<root cause at path:line, or the design note's module map in 3–6 lines>

## Change
<what changed, for a reviewer; pre-existing files and why each changed beyond wiring>

## Checks
- Spec `<path>`: red on <base sha> (before), green on <branch sha> twice (after); evidence in the card comment
- <command> → <pasted summary line>   (one line per suite)
- Structure check: <clean | findings with reasons>

## Code path
<optional before/after mermaid>
```

End the body with the attribution lines the session's instructions give.

## Sources

- Distilled from a production Jira AI loop's evidence rule (one spec, fail before and pass after, both recorded) and its two-tier ship policy (2026).
- GitHub CLI: `gh pr checks` (https://cli.github.com/manual/gh_pr_checks) and `gh pr merge` (https://cli.github.com/manual/gh_pr_merge).
- Playwright video recording: https://playwright.dev/docs/videos
- Shared stages, video conversion and inline players: `W/references/stages.md` S3–S4.
