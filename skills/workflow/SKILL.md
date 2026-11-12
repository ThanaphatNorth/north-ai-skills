---
name: workflow
description: Map and router of the 90north-develop plugin — decides which flow a piece of work belongs to (dev-loop for stories, tasks and changes; defect-loop for defects; n-loop for unattended passes over an AI queue of any card type; n-dev alone for a small untracked change; develop-init when the repo isn't set up), and holds what the flows share - the per-repo state folder, the shared stages (isolate, verify, evidence, ship, clean up, learn), the dispatch safety block, core lessons and the Jira REST scripts. Use when the user asks "which flow", "what's the workflow", "start work on <KEY>" without saying feature or bug, wants the whole picture of the plugin, or when a loop skill points here for a shared stage.
---

# 90north-develop · workflow

Two attended loops and one unattended loop, one discipline, one set of per-repo facts. Report in the user's language; keep code, identifiers and commit messages in the repo's language.

```
                      develop-init  (once per repo)  →  .claude/90north-develop/
                                       │
        ┌──────────────────────────────┴──────────────────────────────┐
   dev-loop  (Story · Task · Improvement)                  defect-loop  (Bug)
   D1 Pull + ready check                                    F1 Pull + triage
   D2 Size + design note ── gate: user approves Large       F2 Reproduce: red e2e  (defect-repro)
   D3 Acceptance spec red  (dev-builder)                    F3 Root cause at path:line
   D4 Build work packages test-first  (dev-builder)         F4 Fix test-first  (defect-fixer)
        └──────────── shared stages (references/stages.md) ────────────┘
          S1 Isolate · S2 Verify (review + QA) · S3 Evidence video
          S4 Ship (comment → push per policy → PR → lane) · S5 Clean up · S6 Learn
                                       │
                 n-dev — how every line of code is written, in every loop
                 n-arch — the repo's architecture profile every loop reads

   n-loop  (unattended: any card type in the AI queue, on a schedule)
   A1 Follow-ups · A2 Scout + lock · A3 Triage (do-now / need-dev / need-info, class)
   A4 BEFORE red ─ A5 Build ─ A6 PROOF green   ← the defect or dev path above, with no gate:
   A7 Verifier gate (loop-verifier) · A8 Ship by policy · A9 Learn (loop-learner)   a gate parks the card
```

Both loops start with a red test that states what "done" means: the defect's red e2e, or the story's acceptance spec. Both end with a green run of that same test in this session, review and QA, evidence, and a tracker update. What differs is the middle: a defect needs a cause, a feature needs a design. `n-loop` runs the same two paths without a person in the chat: it builds only what needs no gate, puts an adversarial verifier before anything is published, and ships by a written policy.

## Route the work

| Signal | Flow | Command |
|---|---|---|
| No `.claude/90north-develop/config.md` (or only the legacy `.claude/defect-loop/`) | set up first | `/90north-develop:develop-init` |
| Jira **Bug** / defect type, or "it used to work / it doesn't do what the spec says" | defect flow | `/90north-develop:defect-loop [KEY]` |
| Story, Task, Improvement, a spec file, or "add / change / build …" | development flow | `/90north-develop:dev-loop <KEY \| spec path \| request>` |
| An unattended pass over the board's AI queue (any card type), on a schedule or `/loop`, or "AI loop / autopilot" | unattended flow | `/90north-develop:n-loop [--dry-run] [KEY]` |
| Small change with no ticket (one file, one rule, no new module) | discipline only | `/90north-develop:n-dev` |
| "Map / document / audit the architecture", layer rules, or n-dev says the profile is missing or stale | architecture profile | `/90north-develop:n-arch [refresh \| audit]` |
| Unclear | read the ticket; behaviour that **exists and is wrong** against the current spec is a defect, behaviour that **does not exist yet** or that the spec now asks to change is development | — |

A ticket's type in Jira is a hint, not the answer: a "Bug" asking for a new screen is a change request (defect-loop triages it `by-design / change`), and a "Task" saying "the total is wrong" is a defect.

## Handoffs between the loops

| From | When | To |
|---|---|---|
| defect-loop triage | `structural` (schema, auth, contract, > fence) and the user says yes to build it | dev-loop from D2, with the defect's red spec as the acceptance spec; the defect ticket keeps its key |
| defect-loop triage | `by-design / change request` and the PO re-scopes it into a story | dev-loop on the new story |
| dev-loop D4 / S2 | a bug found in code that existed **before** this story | never fixed on the feature branch: report it as a separate defect proposal (key or draft) for defect-loop |
| dev-loop after PR | QA bounces the story before Done | stays in dev-loop: a fix round on the same branch, not a defect |
| n-loop triage or build | `need-dev`: Large, a gate case, a forbidden area, or stopped; the solution is on the card | a person may take it in dev-loop or defect-loop; the ai-ledger row says `solution-posted`, the new loop's row says `from-n-loop KEY` and starts from the posted solution and spec |
| dev-loop or defect-loop | an item with an open row in another loop's ledger | skipped; one owner at a time, including the AI loop |

A handoff writes one ledger row in each loop's ledger (`handed-to-dev-loop` / `from-defect-loop KEY`), so no ticket is owned by two loops at once.

## Per-repo state (`DL` = `<repo-root>/.claude/90north-develop/`)

| File | Owner of | Written by |
|---|---|---|
| `config.md` | every project fact: tracker, board ids, lanes, push policy, repo/worktree recipe, stack recipe, accounts, checks, team, spec sources, § Dev flow, § Defect flow, § AI loop | develop-init; the loops add facts they verify (the unattended loop only proposes) |
| `tracker.env` | `TRACKER` and the backend's settings (`JIRA_SITE`, `JIRA_ENV_FILE`, or `LOCAL_BOARD`, `LOCAL_STATUSES`) — no secrets | develop-init |
| `board/` (local tracker only) | one markdown file per card, attachments in `board/<KEY>/`; committed when config says so | people add cards; `tracker.sh` writes them, always in the main checkout. The loops never commit them: the run report lists changed cards for a person to commit |
| `dev-ledger.md` / `defect-ledger.md` / `ai-ledger.md` | one row per state change of a work item, per loop | the loop that owns the item |
| `lessons.md` | project lessons, tagged `[dev]`, `[defect]`, `[ai]` or `[both]` | S6 Learn, `loop-learner` |
| `knowledge/` | what the AI loop learned: code map, selectors, calibration, outcomes, proposals | `loop-learner` |
| `runs/<date>/<KEY>/` | the AI loop's hand-off files between passes; git-ignored | n-loop |

Legacy repos keep `.claude/defect-loop/` (its `ledger.md` is the defect ledger) until develop-init migrates them; the scripts find either folder. Set `DEVELOP_DIR` to point at the folder explicitly.

## Tracker (`scripts/tracker.sh <verb>` — used by every loop)

Every loop reaches the tracker through one door, `scripts/tracker.sh <verb> …`. Run it from inside the project; it
finds `DL` by walking up. `TRACKER` in `tracker.env` picks the backend:
- `jira` (the default): Jira REST v3 through the `jira-<verb>.sh` scripts. The credentials file is read by the
  scripts only; never cat it.
- `local`: a board of markdown cards in the repo, for a project with no Jira.

Both backends run the same flows, with the queue, lock, lanes, comments and evidence. The verb arguments for each
backend, the card format and the query form are in `references/trackers.md`. Tests are in `scripts/tests/`.

| Verb | Does |
|---|---|
| `search '<query>'` | items: key, type, status, …; the count on stderr (Jira: JQL, all pages; local: `status=todo labels=ai-queue age>2h …`) |
| `get KEY` | description, every comment, attachments as plain text |
| `card KEY [fields]` | labels, links and the listed fields (Jira: also priority and parent; text as one line, selects as values) |
| `download KEY dir [ids]` | download attachments into a new folder |
| `transition KEY <id \| status>` / `--list` | move through the workflow / list the moves offered (Jira: transition ids; local: status names) |
| `edit KEY --add-label L --remove-label L --field F=V --field-md F=file.md` | labels and field values (the AI loop's lock, verdict and class labels, summary field); `--dry-run` changes nothing |
| `attach KEY files…` | upload; prints what goes on the `::video` line (Jira: media uuid; local: `KEY/<name>`) |
| `comment KEY comment.md [id]` | the loop's markdown dialect, `::video <uuid \| path>` players (Jira: → ADF); reads it back (Jira warns on a missing player; local exits 1 on a missing file) |

## Reference map

| Open | When |
|---|---|
| `references/stages.md` | a loop reaches a shared stage (S0–S6), or writes a dispatch brief |
| `references/core-lessons.md` | before every run of any loop, in full |
| `references/trackers.md` | setting up a repo, writing a query or lane into config, or a verb's arguments for this repo's backend (Jira or the local board) |
| `../n-dev/SKILL.md` | the discipline every builder and fixer follows; pass its absolute path in each brief |
| `../n-arch/SKILL.md` | the repo has no `docs/architecture/profile.md` yet, or it is stale; pass the profile's path in each brief once it exists |
| `../dev-loop/SKILL.md`, `../defect-loop/SKILL.md`, `../n-loop/SKILL.md` | the flow itself |
