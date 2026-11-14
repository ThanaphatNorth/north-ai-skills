---
name: workflow
description: Map and router of the 90north-develop plugin — which loop a piece of work belongs to (n-defect-loop for defects, n-develop-loop for new development and changed requirements, develop-init when the repo is not set up), and what both loops share - the 9 steps, the one decision round, the shared stages, auto mode, the safety block and the tracker. Use when the user asks "which loop", "what's the workflow", "start work on <KEY>" without saying feature or bug, wants the whole picture of the plugin, or a loop skill points here for a shared stage.
argument-hint: "[<KEY> | <what you want to do>]"
---

# 90north-develop · workflow

Two loops, split by type of work, on one discipline and one set of per-repo facts. Report in the user's language;
keep code, identifiers and commit messages in the repo's language.

```
                     develop-init  (once per repo)  →  .claude/90north-develop/ + .90north-develop/
                                      │
     n-defect-loop  (defects)                       n-develop-loop  (features, changes)
  1 Read the board ── 2 Triage ── 3 Check the spec           (the same three steps)
  4 Reproduce: red e2e + video  (defect-repro)    4 Pin the goal: acceptance spec red  (dev-builder WP-0)
  5 Root cause at path:line                       5 Design note + work packages ── gate for Large
  6 Test-first fix  (defect-fixer)                6 Test-first build per WP  (dev-builder)
  7 Verify + record ── 8 Open the PR ── 9 Merge (low impact, standing approval) or a person approves
       └──────────── shared stages (references/stages.md) ────────────┘
         S1 Isolate · S2 Verify (review, security + performance review, QA) · S3 Evidence video
         S4 Ship (comment → push per policy → PR → lane) · S5 Clean up · S6 Learn
                                      │
   attended (default): one decision round before anything is built, then it runs to the end
   --auto (references/auto-mode.md): queue + lock, triage matrix, verifier gate, ship classes, learner;
                                     a gate parks the card with a question
                                      │
                n-dev — how every line of code is written, in both loops
                n-arch — the repo's architecture profile both loops read
```

Both loops start with a red test that states what "done" means: the defect's red e2e, or the story's acceptance
spec. Both end with a green run of that same test in this session, review (code, security, performance) and QA,
evidence, and a tracker update.
What differs is the middle: a defect needs a cause, a feature needs a design. Both keep each area's **feature doc**
true in the same PR: its rules with their sources, rule → test, and decisions with reasons
(`references/feature-docs.md`).

Each loop runs **attended** by default: it asks every question in one decision round, before anything is isolated
or built, and then runs to the end (`references/stages.md` § Decision round). With `--auto` it runs **unattended**
(`references/auto-mode.md`): it builds only what needs no gate, puts an adversarial verifier before anything is
published, and ships by a written policy.

Only a low- or no-impact change inside a standing approval merges on its own (`references/auto-evidence-and-ship.md`
§ Ship classes). Everything else waits for a person.

## Route the work

This table sorts work the user wants taken through a loop: they named a loop or a board item, or asked which
loop. A code change asked for with none of those is n-dev's, whatever its size; the plugin's session-start line
(`hooks/session-start.txt` in the plugin) sends it there, and no loop starts on its own. A board key or a loop's
name always wins over n-dev's own description, which also lists tickets and specs.

| Signal | Loop | Command |
|---|---|---|
| No `.claude/90north-develop/config.md` (or only the legacy `.claude/defect-loop/`) | set up first | `/90north-develop:develop-init` |
| A board item of type Bug / defect, or one that says "it used to work / it doesn't do what the spec says" | defects | `/90north-develop:n-defect-loop [KEY] [--auto]` |
| A board item that is a Story, Task, Improvement or change request; or a spec file or an "add / change / build …" request the user asks to take through the loop | development | `/90north-develop:n-develop-loop <KEY \| spec path \| request \| --next> [--auto]` |
| An unattended pass over the board, on a schedule or `/loop`, or "AI loop / autopilot" | either loop with `--auto` (one schedule per loop) | `references/auto-mode.md` |
| A code change asked for with no board item and no loop named, whatever its size | discipline only | `/90north-develop:n-dev` |
| "Map / document / audit the architecture", layer rules, or n-dev says the profile is missing or stale | architecture profile | `/90north-develop:n-arch [refresh \| audit]` |
| Unclear | read the ticket: behaviour that **exists and is wrong** against the current spec is a defect; behaviour that **does not exist yet**, or that the spec now asks to change, is development | — |

A ticket's type is a hint, not the answer. A "Bug" asking for a new screen is a change request: n-defect-loop
triages it `by-design / change request` and hands it off. A "Task" saying "the total is wrong" is a defect.

## Handoffs between the loops

| From | When | To |
|---|---|---|
| n-defect-loop triage | `structural` (schema, auth, contract, > fence) and a person says yes to build it | n-develop-loop, row `from-n-defect-loop KEY`: a new `feat/` worktree with the defect's red spec as WP-0, then its steps 5–6; the defect ticket keeps its key |
| n-defect-loop triage | `by-design / change request` | n-develop-loop: attended, once the PO re-scopes it; auto, through the hand-off label `ai-to-develop` |
| n-develop-loop triage | the item is really a defect | n-defect-loop: a hand-off row, or the hand-off label `ai-to-defect` in auto mode |
| n-develop-loop step 6 / S2 | a bug found in code that existed **before** this story | never fixed on the feature branch: report it as a separate defect proposal (key or draft) for n-defect-loop |
| n-develop-loop after PR | QA bounces the story before Done | stays in n-develop-loop: a fix round on the same branch, not a defect |
| either loop, auto mode | `need-dev`: Large, a gate case, a forbidden area, or stopped; the solution is on the card | a person may take it in the attended mode; that run's row says `from-auto KEY` and starts from the posted solution and spec |
| either loop | an item with an open row in another loop's ledger (or in a legacy `ai-ledger.md`) | skipped: one owner at a time |

A handoff writes one ledger row in each loop's ledger (`handed-to-n-develop-loop` / `from-n-defect-loop KEY`), so
no ticket is owned by two loops at once.

## Per-repo state: settings in `DC`, working state in `DL`

`DC` = `<repo-root>/.claude/90north-develop/` holds the settings. Claude Code asks a person before it writes under
`.claude/`, which is right for the file that holds the push approval and the tracker's address.
`DL` = `<repo-root>/.90north-develop/` holds what a loop writes as it works. It sits outside `.claude/` so that a
session that can ask nobody can still record its work.

`scripts/where.sh` prints both folders for the project it is run in. A loop takes `DC` and `DL` from it and never
builds the paths by hand: in a project that has not moved yet they are one folder, and a file written to the other
place would split the state in two.

| File | Owner of | Written by |
|---|---|---|
| `DC/config.md` | every project fact: tracker, board ids, lanes, push policy, repo/worktree recipe, stack recipe, accounts, checks, team, spec sources, § Dev flow, § Defect flow, § Auto mode | develop-init; the loops add facts they verify (in auto mode they only propose) |
| `DC/tracker.env` | `TRACKER` and the backend's settings (`JIRA_SITE`, `JIRA_ENV_FILE`, or `LOCAL_BOARD`, `LOCAL_STATUSES`) — no secrets | develop-init |
| `DL/board/` (local tracker only) | one markdown file per card, attachments in `board/<KEY>/`; committed when config says so | people add cards; `tracker.sh` writes them, always in the main checkout. The loops never commit them: the run report lists changed cards for a person to commit |
| `DL/dev-ledger.md` / `DL/defect-ledger.md` | one row per state change of a work item, per loop, both modes, written with `scripts/ledger.sh` (a legacy `ai-ledger.md` stays as history and is read for ownership while it has open rows) | the loop that owns the item |
| `DL/lessons.md` | project lessons, tagged `[dev]`, `[defect]`, `[ai]` or `[both]` | S6 Learn, `loop-learner` |
| `DL/knowledge/` | what auto mode learned: code map, selectors, calibration, outcomes, proposals | `loop-learner` |
| `DL/runs/<date>/<KEY>/`, `DL/runs/.pass.lock` | auto mode's hand-off files between passes, and the pass lock both loops share; git-ignored | either loop with `--auto` |

A project set up before 0.12 has its working state in `DC` as well: `where.sh` then prints the same folder twice, with a note. The scripts read and write it there (a ledger decides which place is in use; with no ledger anywhere, cards on the board do; a README, a keep file, an empty file, an empty folder or folders that hold only empty folders are leftovers and decide nothing), and `scripts/move-state.sh` moves it (develop-init offers it; `--dry-run` shows what would move; the ledgers move last, so a move that stopped half way is finished by running it again). Until it is moved, a session that can ask nobody cannot write every run file or remove the pass lock there, so an unattended pass does not start: `where.sh --auto`, its first command, refuses it (exit 3) before a lock or a card is taken.

The state is in two places when it is read beside the project while a ledger, cards, lessons or knowledge are still under `.claude/` (run files are hand-offs, not records, and do not count). The scripts read the new place, `where.sh` names both in its note, and no run takes a work item until a person has put each file in one place: `where.sh --auto` exits 3, and an attended run stops at S0.

An unattended pass also needs the working state folder to be there: `ledger.sh` only appends to a ledger develop-init wrote. With no such folder (a project that has its settings only, or a `DEVELOP_STATE_DIR` that names nothing) `where.sh --auto` exits 2 and the pass does not start.

Legacy repos keep `.claude/defect-loop/` (its `ledger.md` is the defect ledger) until develop-init migrates them, and an unattended pass does not start there either; the scripts find either settings folder. Set `DEVELOP_DIR` (settings) and `DEVELOP_STATE_DIR` (working state) to point at the folders explicitly. Both are read as absolute, physical paths: a relative name is taken from the folder the script runs in, a link is followed, and `where.sh` prints the result. A working state that leads under `.claude/` by a name or a link is refused for an unattended pass like the old layout, and so is a project that itself sits under a folder named `.claude`: there, `DEVELOP_STATE_DIR` names a folder outside it.

## Tracker (`scripts/tracker.sh <verb>` — used by every loop)

Every loop reaches the tracker through one door, `scripts/tracker.sh <verb> …`. Run it from inside the project; it
finds `DL` by walking up. `TRACKER` in `tracker.env` picks the backend:
- `jira` (the default): Jira REST v3 through the `jira-<verb>.sh` scripts. The credentials file is read by the
  scripts only; never cat it. The user creates it in their own terminal with `scripts/jira-login.sh [--force] [path]`:
  it asks for the email and the API token (not echoed), writes the file with mode 600 and prints `OK <name>` or
  `FAILED HTTP <code>`. The file holds only `JIRA_EMAIL=` and `JIRA_TOKEN=` lines; it is parsed, never run.
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
| `edit KEY --add-label L --remove-label L --field F=V --field-md F=file.md` | labels and field values (auto mode's lock, verdict, class and hand-off labels, summary field); `--dry-run` changes nothing |
| `attach KEY files…` | upload; prints what goes on the `::video` line (Jira: media uuid; local: `KEY/<name>`) |
| `comment KEY comment.md [id]` | the loop's markdown dialect, `::video <uuid \| path>` players (Jira: → ADF); reads it back (Jira warns on a missing player; local exits 1 on a missing file) |

## Reference map

| Open | When |
|---|---|
| `references/stages.md` | a loop reaches a shared stage (S0–S6) or its decision round, or writes a dispatch brief |
| `references/core-lessons.md` | before every run of any loop, in full |
| `references/feature-docs.md` | step 2 by-design (cite or propose the rule), step 3 (read the area's rules), steps 5–6 (plan and write the doc in the same PR), step 8 (the `Docs:` line), verifier V10 |
| `references/trackers.md` | setting up a repo, writing a query or lane into config, or a verb's arguments for this repo's backend (Jira or the local board) |
| `../n-dev/SKILL.md` | the discipline every builder and fixer follows; pass its absolute path in each brief |
| `../n-arch/SKILL.md` | the repo has no `docs/architecture/profile.md` yet, or it is stale; pass the profile's path in each brief once it exists |
| `references/auto-mode.md` | a loop runs with `--auto`: the pass, its stages A0–A9 mapped to the 9 steps, parked states, hard limits |
| `references/auto-triage.md` | auto mode A2–A3: queue score, check the spec, route and hand-off, locate, size, decision table, class |
| `references/auto-evidence-and-ship.md` | step 9 in either mode (§ Ship classes: what may merge on its own); auto mode A4, A6–A8 |
| `references/auto-tracker-record.md` | auto mode: every tracker write, the lock and labels, follow-ups |
| `references/auto-knowledge.md` | auto mode A0 and A9: what the learner reads and writes |
| `references/auto-project-pack.md` | putting a repo on auto mode for the first time |
| `templates/auto-comments.md`, `templates/auto-scheduled-task.md` | auto mode's comments; registering a schedule per loop |
| `../n-defect-loop/SKILL.md`, `../n-develop-loop/SKILL.md` | the loop itself |
