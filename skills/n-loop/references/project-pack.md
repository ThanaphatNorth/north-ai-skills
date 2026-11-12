# Project pack — putting a project on the loop, or moving a project-specific loop onto it

> Read when: a repo will run n-loop for the first time, or a team already runs its own Jira AI loop (its own plugin, agents and rules with the project baked in) and wants to move onto this framework.

The framework holds the procedure; the **project pack** holds the facts. A pack is not a separate folder or plugin. It is the set of places the plugin already reads, each owning one kind of fact:

| Kind of fact | Owner | Written by |
|---|---|---|
| tracker ids, queue and lock, labels, lanes, limits, fences, never-touch list, ship gates, schedule | `DL/config.md` § AI loop (plus § Tracker, § Push policy, § Comments, § Evidence) | `/90north-develop:develop-init` |
| architecture: map, layers, extension recipes, state owners, contracts, commands | `docs/architecture/profile.md` | `/90north-develop:n-arch` |
| budgets, layer globs, allowed import directions | `.ndev.toml` | `/90north-develop:n-arch` |
| house rules, reusable component lists, coding conventions | the repo's practice pack (a `*-practices` skill or docs folder), linked from the profile's Conventions and from config § Team | the team |
| how to bring up the stack and record on it | config § Stack recipe, § Accounts and login, § Evidence | develop-init, then the loops |
| what the loop learned | `DL/knowledge/`, `DL/lessons.md` `[ai]` | `loop-learner` |

Nothing project-specific goes in the plugin. When you are about to write a repo name, a field id, a host, a component name or a label text into a skill or agent, it belongs in one of the owners above.

## New project, step by step

1. **Profile.** Run `/90north-develop:n-arch` (create mode) in each repo the board touches. Without a profile the loop still runs, but nothing can reach the auto-merge class, and every locate starts from search.
2. **Config.** Run `/90north-develop:develop-init`; answer yes to the AI loop step. It reads the board's ids (issue types, statuses, transitions, custom fields) and writes § AI loop with every line checked or `TBD`.
3. **Never-touch list.** Start from the profile's Contracts and State owners, then add the domain risks the profile cannot know: money and tax, personal or health data, permissions, ids minted by another system, infra. Give each a glob or a marker the verifier can grep.
4. **Stack and evidence.** Prove once by hand that the stack recipe comes up and that one spec records with the cursor, the focus box and the caption band. Write what worked into config § Evidence.
5. **Dry runs.** Register the schedule with `--dry-run` (`templates/scheduled-task.md`) and read 2–3 passes' `run.md` and the triage comments on the board.
6. **Real runs.** Remove `--dry-run`. Keep config › cards per pass at 1, and leave auto-merge off, until about 10 cards have shipped through needs-review with no reopen. Then the owner decides on the standing approval for merges, in their own words, dated, in config § Push policy.
7. **Tune.** After 10 cards, review the decision table and the fences against `DL/knowledge/outcomes.jsonl`; the weekly review proposes the numbers.

## Moving a project-specific loop onto the framework

Map each piece of the old loop to its owner. Move facts, not procedure: the old procedure is replaced by this skill's, and anything it did that this skill does not becomes a proposal against the plugin instead of a project patch.

| Old loop piece | Goes to |
|---|---|
| board, project key, field ids, option names, label names, JQL, transition ids (a lane reached in several hops is written as its whole path) | config § Tracker and § AI loop |
| "AI status" style custom field used as the queue and the lock | config § AI loop › Queue and Lock (field mode) |
| limits (cards per run, minutes, attempts, lock hours) | config § AI loop › Limits |
| shipping block (auto-merge on/off, repos, paths, sizes, grace, CI rule) | config § AI loop › Auto-merge and › Fences; the owner's decision as a dated quote in § Push policy |
| forbidden-areas table | profile Contracts and State owners (structure), plus config › never-touch (domain risk) |
| practice card (components to reuse, house rules, commit and branch rules) | the repo's practice pack, linked from the profile's Conventions; branch rules in config § Dev flow and § Defect flow, commit conventions in the profile's Conventions |
| code map | `DL/knowledge/code-map.md` (card words → places); anything structural goes to the profile through an n-arch refresh |
| working selectors | `DL/knowledge/selectors.md` |
| calibration, outcomes | `DL/knowledge/calibration.md`, `outcomes.jsonl` |
| lessons | `DL/lessons.md` with `[ai]` and the step; dedupe against the plugin's core lessons |
| environments and the local shell recipe | config § Stack recipe and § Accounts and login (test accounts by role, never their secrets) |
| recording helper (overlay, upload script) | config § Evidence names the repo's helper; uploads go through `W/scripts/tracker.sh attach` + `tracker.sh comment` |
| comment templates in the team's language | config § Comments language; the framework's templates are filled in that language |
| decisions the owner answered (push, merge, schedule, scope) | config lines with the date and the owner's words |
| run folders | `DL/runs/` (git-ignored) |
| scheduled-task prompt | `templates/scheduled-task.md`, with the repo root as working directory |

Checklist before switching the schedule:

1. A `--dry-run` pass on the new setup triages the same cards the old loop would, to the same verdicts. Compare the last 5 cards' verdicts.
2. Labels and the lock behave as before on one real card (the lock field or label is set and released).
3. One BEFORE recording on the new stack recipe shows the symptom.
4. The old schedule is disabled before the new one runs (two loops must never lock the same board). Keep the old plugin installed but unscheduled until 10 cards have shipped on the new one.
5. Nothing in the move deletes the old loop's knowledge or runs; copy, then archive.

## What stays out of a pack

- Secrets: tokens and passwords live in the credentials file outside the repo (config § Tracker) or the OS keychain. Never in config, knowledge or a run file.
- Personal data from cards, described in run files, never copied.
- Procedure. If a project needs a step the framework does not have, propose it for the plugin, so the next project gets it too.

## Sources

- Derived from moving one production Jira AI loop's project facts out of its agents into config, profile and knowledge files (2026).
- Config template: `../develop-init/templates/config.md` § AI loop.
- Profile template: `../n-arch/templates/profile.md`.
