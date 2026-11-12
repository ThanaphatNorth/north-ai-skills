# Knowledge — how the loop gets better between passes

> Read when: n-loop A0 reads what earlier passes learned, A9 collects outcomes and dispatches `loop-learner`, or the weekly review runs. The learner's own rules are in the plugin's `loop-learner` agent; this file is the map of the files and of who may change what.

The loop improves only through files. Rules (this skill's references and `DL/config.md`) say what to do. Knowledge (`DL/knowledge/`) says what was true last time. Agents read knowledge **before** the rules apply, and the learner is the only writer.

## Files (`DL/knowledge/`, plain files; once a person commits them, the whole team's passes share them)

| File | Holds | Read by | Written when |
|---|---|---|---|
| `code-map.md` | card vocabulary (screen, menu, feature name) → repo, folder, files, extension recipe; newest entry wins | A3 locate, builders | a locate took > 2 minutes or found an area the map lacked |
| `selectors.md` | locators and labels that worked or broke on the stack, with date | `defect-repro`, `dev-builder` WP-0 | a spec's locator worked after a miss, or broke |
| `calibration.md` | estimate vs actual table (files, non-test lines, repos) and the current correction factor | A3 size, A2 score | every built card |
| `outcomes.jsonl` | one line per card per pass: key, route, verdict, class predicted / shipped, verified, PR, outcome, minutes | the learner, the weekly review | every pass |
| `proposals/<date>-<slug>.md` | a change a person must approve | people | a lesson needs a rule, config, agent or skill change |

Lessons are not here: they go in `DL/lessons.md` with the `[ai]` tag and the agent or step they belong to, in the format S6 already uses (`W/references/stages.md`), so all three flows read one lessons file.

**One owner per fact.** The architecture (folders, layers, extension recipes, contracts, state owners) belongs to the n-arch profile. `code-map.md` only maps the **card's words** to places, which the profile has no reason to hold. When the learner finds the profile wrong or stale, it writes a proposal to run `/90north-develop:n-arch refresh` and never edits the profile.

## Read order (A0)

1. `DL/lessons.md` in full (S0 already does this).
2. `calibration.md` (the factor), the last `DL/runs/*/learn.md` for `requeue:` flags.
3. Per card, at A3: `code-map.md` for its area; at A4: `selectors.md`.

## Signals (A9 — the conductor collects, the learner reads)

The learner has no tracker access. Before dispatching it, you write `DL/runs/<date>/outcomes.md` with the facts below, gathered since the last `outcomes.jsonl` line:

| Signal | Collect with | Means |
|---|---|---|
| triage verdict vs what happened | `triage.md` vs `build.md`, `verify.md` | a do-now that ended stopped = the table was too loose; a need-dev a person then fixed in ≤ 50 lines = too strict |
| estimate vs actual | `triage.md` vs `git diff --numstat` minus size excludes | calibration |
| locate time and misses | `triage.md` | a code-map entry; a profile row that pointed to the wrong place |
| locators that worked or broke | the spec, `before.md`, `proof.md` | selectors |
| verifier refutations | `verify.md` | what the builder or recorder got wrong, and the fix |
| structure findings | `build.md`, QA's structure-check output | a repeated finding = a builder lesson; a target layer rule with 0 violations = a proposal to enforce it in `.ndev.toml` (through n-arch) |
| PR outcome | `gh pr view <n> --json state,reviews,comments` | merged = good; changes requested = read the review, that is a lesson; closed unmerged = wrong fix |
| card after the review lane | `W/scripts/tracker.sh get <KEY>`: status, comments newer than the loop's | reopened = the fix did not hold → lesson + re-queue flag |
| reply on a need-info card | the same | answered → A1 re-queues; the answer was already on the card → triage lesson |
| need-dev card closed by a person | the same, plus that PR's diff size | the rule that sent it to need-dev, checked against what it took |
| auto-merge reverted or reopened | the same | two on the same change kind → proposal to drop that kind from the auto-merge paths |

## What the learner may change itself

Auto-applied as file edits. The learner never commits: the main checkout may be on the base branch, and an unattended commit there would never be reviewed. When config says knowledge is committed, the weekly review lists the uncommitted knowledge changes and a person commits them on a branch of their own:

- `code-map.md`, `selectors.md`, `calibration.md`, `outcomes.jsonl`, and `[ai]` entries in `DL/lessons.md` (bump `seen:` on a repeat instead of duplicating; mark retired ones `retired: <reason>`, never delete).

## What it may only propose

Changes to `DL/config.md`, any skill (`skills/**`), agent, template, the profile or `.ndev.toml`. Write `DL/knowledge/proposals/<date>-<slug>.md` with: the evidence quoted from the files, the exact edit as a diff, the expected effect, and how to tell it worked. A lesson with `seen ≥ 2` that still needs a rule change becomes a proposal automatically. A proposal that would help every repo (a skill or agent of this plugin) also names the plugin file, so the user can move it into the plugin repo. Rules that hold for any project go in `W/references/core-lessons.md`.

## Weekly review

On the first pass of the week, before A1, run `loop-learner` in review mode over the last 7 days of `outcomes.jsonl`. It reports the trend: do-now accuracy, the auto-merge class's revert or reopen rate, time per card, the most-refuted claim, and open proposals older than 7 days. It writes `DL/runs/<date>/weekly.md` and may propose a change to any number in config (limits, fences, the factor).

## Sources

- Distilled from a production Jira AI loop's learner (outcomes → auto-applied knowledge, rule changes as proposals a person approves; 2026).
- Lesson format and promotion: `W/references/stages.md` S6 and the user's global learning protocol.
- n-arch owns the profile and `.ndev.toml`: `../n-arch/SKILL.md` § Works with.
