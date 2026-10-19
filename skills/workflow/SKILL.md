---
name: workflow
description: Map and router of the 90north-develop plugin — decides which flow a piece of work belongs to (dev-loop for stories, tasks and changes; defect-loop for defects; n-dev alone for a small untracked change; develop-init when the repo isn't set up), and holds what both flows share - the per-repo state folder, the shared stages (isolate, verify, evidence, ship, clean up, learn), the dispatch safety block, core lessons and the Jira REST scripts. Use when the user asks "which flow", "what's the workflow", "start work on <KEY>" without saying feature or bug, wants the whole picture of the plugin, or when a loop skill points here for a shared stage.
---

# 90north-develop · workflow

Two loops, one discipline, one set of per-repo facts. Report in the user's language; keep code, identifiers and commit messages in the repo's language.

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
                 n-dev — how every line of code is written, in both loops
```

Both loops start with a red test that states what "done" means: the defect's red e2e, or the story's acceptance spec. Both end with a green run of that same test in this session, review and QA, evidence, and a tracker update. What differs is the middle: a defect needs a cause, a feature needs a design.

## Route the work

| Signal | Flow | Command |
|---|---|---|
| No `.claude/90north-develop/config.md` (or only the legacy `.claude/defect-loop/`) | set up first | `/90north-develop:develop-init` |
| Jira **Bug** / defect type, or "it used to work / it doesn't do what the spec says" | defect flow | `/90north-develop:defect-loop [KEY]` |
| Story, Task, Improvement, a spec file, or "add / change / build …" | development flow | `/90north-develop:dev-loop <KEY \| spec path \| request>` |
| Small change with no ticket (one file, one rule, no new module) | discipline only | `/90north-develop:n-dev` |
| Unclear | read the ticket; behaviour that **exists and is wrong** against the current spec is a defect, behaviour that **does not exist yet** or that the spec now asks to change is development | — |

A ticket's type in Jira is a hint, not the answer: a "Bug" asking for a new screen is a change request (defect-loop triages it `by-design / change`), and a "Task" saying "the total is wrong" is a defect.

## Handoffs between the loops

| From | When | To |
|---|---|---|
| defect-loop triage | `structural` (schema, auth, contract, > fence) and the user says yes to build it | dev-loop from D2, with the defect's red spec as the acceptance spec; the defect ticket keeps its key |
| defect-loop triage | `by-design / change request` and the PO re-scopes it into a story | dev-loop on the new story |
| dev-loop D4 / S2 | a bug found in code that existed **before** this story | never fixed on the feature branch: report it as a separate defect proposal (key or draft) for defect-loop |
| dev-loop after PR | QA bounces the story before Done | stays in dev-loop: a fix round on the same branch, not a defect |

A handoff writes one ledger row in each loop's ledger (`handed-to-dev-loop` / `from-defect-loop KEY`), so no ticket is owned by two loops at once.

## Per-repo state (`DL` = `<repo-root>/.claude/90north-develop/`)

| File | Owner of | Written by |
|---|---|---|
| `config.md` | every project fact: tracker, board ids, lanes, push policy, repo/worktree recipe, stack recipe, accounts, checks, team, spec sources, § Dev flow, § Defect flow | develop-init; the loops add facts they verify |
| `tracker.env` | `JIRA_SITE`, `JIRA_ENV_FILE` — no secrets | develop-init |
| `dev-ledger.md` / `defect-ledger.md` | one row per state change of a work item, per loop | the loop that owns the item |
| `lessons.md` | project lessons, tagged `[dev]`, `[defect]` or `[both]` | S6 Learn |

Legacy repos keep `.claude/defect-loop/` (its `ledger.md` is the defect ledger) until develop-init migrates them; the scripts find either folder. Set `DEVELOP_DIR` to point at the folder explicitly.

## Scripts (`scripts/`, Jira REST v3 — used by both loops)

Run them from inside the project (they find `DL` by walking up). The credentials file is read by the scripts only; never cat it.

| Script | Does |
|---|---|
| `scripts/jira-search.sh '<JQL>'` | issues: key, type, status id, sprint or BACKLOG, updated, summary — all pages |
| `scripts/jira-get.sh KEY` | description, every comment, attachments as plain text |
| `scripts/jira-download.sh KEY dir [ids]` | download attachments |
| `scripts/jira-transition.sh KEY id [fields-json]` / `--list` | move through the workflow / list offered transitions |
| `scripts/jira-attach.sh KEY files…` | upload; prints each file's media uuid |
| `scripts/jira-comment.sh KEY comment.md [commentId]` | the loop's markdown dialect → ADF, `::video <uuid>` inline players; reads back and warns on missing players or code spans |

## Reference map

| Open | When |
|---|---|
| `references/stages.md` | a loop reaches a shared stage (S0–S6), or writes a dispatch brief |
| `references/core-lessons.md` | before every run of either loop, in full |
| `../n-dev/SKILL.md` | the discipline every builder and fixer follows; pass its absolute path in each brief |
| `../dev-loop/SKILL.md`, `../defect-loop/SKILL.md` | the flow itself |
