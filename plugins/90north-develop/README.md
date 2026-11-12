# 90north-develop

North's development plugin: two attended loops, one unattended loop, one discipline, one set of per-repo facts.

```
                      develop-init  (once per repo)  →  .claude/90north-develop/
                                       │
        ┌──────────────────────────────┴──────────────────────────────┐
   dev-loop  (Story · Task · Improvement)                  defect-loop  (Bug)
   D1 Pull + ready check                                    F1 Pull + triage
   D2 Size + design note ── gate: user approves Large       F2 Reproduce: red e2e  (defect-repro)
   D3 Acceptance spec red  (dev-builder)                    F3 Root cause at path:line
   D4 Build work packages test-first  (dev-builder)         F4 Fix test-first  (defect-fixer)
        └──────────── shared stages (workflow skill) ────────────┘
          S1 Isolate · S2 Verify (review + QA) · S3 Evidence video
          S4 Ship (comment → push per policy → PR → lane) · S5 Clean up · S6 Learn
                                       │
                 n-dev — how every line of code is written, in every loop
                 n-arch — the repo's architecture rules n-dev reads and its check enforces

   n-loop  (unattended: any card type in the AI queue, on a schedule)
   A1 Follow-ups · A2 Scout + lock · A3 Triage (do-now / need-dev / need-info, class)
   A4 BEFORE red ─ A5 Build ─ A6 PROOF green   ← the defect or dev path above, with no gate
   A7 Verifier gate (loop-verifier) · A8 Ship by policy · A9 Learn (loop-learner)
```

Both loops start with a red test that says what "done" means (the defect's red e2e, or the story's acceptance spec) and end with that test green in the same session, review + QA, an inline video and a tracker update. A defect needs a cause; a feature needs a design — that is the only difference in the middle. `n-loop` runs both paths with nobody in the chat: it builds only what needs no gate (a gate parks the card with a question or the solution on it), lets an adversarial verifier refute every claim before anything is published, ships by a written policy, and learns into `.claude/90north-develop/knowledge/`.

| Skill | Role |
|--|--|
| `workflow` | the map: routes work to a flow, owns the shared stages, dispatch safety block, core lessons and the tracker scripts (Jira or a local board) |
| `develop-init` | once per repo: discovers the stack, reads the board's ids and lanes, writes `.claude/90north-develop/` |
| `dev-loop` | development flow: one story / task / spec from ready to reviewed PR |
| `defect-loop` | defect flow: sweeps the defect board, each defect from repro to the QA lane |
| `n-loop` | unattended flow for any project: one pass over the AI queue — follow-ups, lock, triage any card type, spec red → build → spec green, verifier gate, ship by policy, learn |
| `n-dev` | the discipline: design before code, modular, reuse first, extension files, one owner per fact, test-first, verified |
| `n-arch` | once per repo, then on drift: the architecture profile and `.ndev.toml` (layers, budgets) that n-dev and its structure check use; audits debt |

| Agent | Used by | Does |
|--|--|--|
| `dev-builder` | dev-loop | WP-0 acceptance specs red, then one work package test-first, local commit |
| `defect-repro` | defect-loop | an e2e that goes red on the reported symptom, plus the video |
| `defect-fixer` | defect-loop | regression test red → fix at the root cause → green, local commit |
| `loop-verifier` | n-loop | tries to refute each claim (spec ↔ card, before reason, proof on the branch, forbidden areas, scope, structure check, evidence, comment, checks ran) before anything is published |
| `loop-learner` | n-loop | turns a pass's files and outcomes into knowledge (code map, selectors, calibration, outcomes, lessons); rule changes become proposals |

`n-loop` also dispatches `dev-builder`, `defect-repro` and `defect-fixer`, on the dev or defect path its triage picks.

## Install (once per machine)

```
/plugin marketplace add ThanaphatNorth/north-ai-skills
/plugin install 90north-develop@north-ai-skills
```

## Commands

| Command | Does |
|--|--|
| `/90north-develop:workflow` | Which flow is this? The whole map |
| `/90north-develop:develop-init` | Once per repo (also migrates a legacy `.claude/defect-loop/`) |
| `/90north-develop:dev-loop <KEY \| spec \| request>` | Build one story / task / spec |
| `/loop 60m /90north-develop:dev-loop --next` | Take ready stories one by one; stops at each design gate |
| `/90north-develop:defect-loop [KEY]` | One defect sweep, or one defect |
| `/loop 30m /90north-develop:defect-loop` | Keep sweeping (continuous mode between ticks while cards remain) |
| `/90north-develop:n-loop [--dry-run] [KEY]` | One unattended pass over the AI queue, or one card |
| scheduled task / `/loop 30m /90north-develop:n-loop` | Unattended passes (`skills/n-loop/templates/scheduled-task.md`); start with `--dry-run` |
| `/90north-develop:n-dev` | A small untracked change with the discipline only |
| `/90north-develop:n-arch [refresh \| audit]` | Map the repo's architecture (develop-init runs it when there is no profile) |

## Where each loop stops for you

| Loop | Gate |
|--|--|
| all | push (unless a standing approval covers it), 2 fix rounds used, a subagent's `NEEDS-DECISION` |
| dev-loop | item not ready (asks on the ticket), design approval for Large or schema / state / public-interface changes |
| defect-loop | needs-info, cannot reproduce, by-design / change request (PO), structural (build moves to dev-loop on your yes) |
| n-loop | never stops mid-card: it parks the card instead — a question (`ai-need-info`), the solution (`ai-need-dev`), a branch awaiting push, a PR in review. It merges only the auto-merge class, and only inside a standing approval that names merge |

## Per-project files (`<repo>/.claude/90north-develop/`)

| File | Holds |
|--|--|
| `config.md` | Tracker, board ids, § Dev flow, § Defect flow and § AI loop (queries, lock, lanes, fences, gates, ship classes), push policy, repo/worktree recipe, isolated stack recipe, accounts, checks, team agents, spec sources, project rules |
| `tracker.env` | `TRACKER` (jira or local) and its settings: `JIRA_SITE`, `JIRA_ENV_FILE`, or `LOCAL_BOARD`, `LOCAL_STATUSES` — no secrets |
| `board/` | Local tracker only: one markdown card per file, attachments in `board/<KEY>/`; committed by default, the loops edit it and a person commits |
| `dev-ledger.md`, `defect-ledger.md`, `ai-ledger.md` | One row per state change, per loop |
| `lessons.md` | Project lessons tagged `[dev]` / `[defect]` / `[ai]` / `[both]` (core lessons ship with the plugin) |
| `knowledge/` | The AI loop's code map, selectors, calibration, outcomes log and proposals (written by `loop-learner`) |
| `runs/` | The AI loop's per-card hand-off files; git-ignored |

Credentials (Jira only): a file outside the repo (default `~/.config/<project>-jira.env`, `JIRA_EMAIL` + `JIRA_TOKEN`, chmod 600). The scripts send the token to curl on stdin and never print it. A repo set up with 0.2 (`.claude/defect-loop/`) keeps working for defects; `develop-init` moves it on your yes.

## Tracker (`skills/workflow/scripts/tracker.sh` at the repo root)

Every loop reaches the tracker through `tracker.sh <verb>`. `TRACKER` in `tracker.env` picks the backend: `jira`
(the default) or `local`, a board of markdown cards in the repo for a project with no Jira. Both run the same flows,
with the queue, lock, lanes, comments and evidence. Arguments per backend, the card format and the query form are in
`skills/workflow/references/trackers.md`.

| Verb | Does |
|--|--|
| `search '<query>'` | List items (key, type, status, …); JQL on Jira, `status=todo labels=ai-queue age>2h` on a local board |
| `get KEY` | Description, every comment, attachments as plain text |
| `card KEY [fields]` | Labels, links and the listed fields |
| `download KEY dir [ids]` | Download attachments into a new folder |
| `transition KEY <id \| status>` / `--list` | Move through the workflow / show the moves offered |
| `edit KEY --add-label L --remove-label L --field F=V --field-md F=file.md` | Labels and field values (lock, verdict and class labels, the AI summary); `--dry-run` changes nothing |
| `attach KEY files…` | Upload; prints what goes on the `::video` line (Jira media uuid, or `KEY/<name>`) |
| `comment KEY comment.md [id]` | Markdown with `::video` players (→ ADF on Jira); reads it back |

## Safety built in

- Agents never boot app processes or touch databases (a second process with other env flags once ran a destructive boot hook).
- Never push / force-push / merge / delete without your yes; a standing approval counts only in its written scope.
- Never moves an item to a QA or review lane without a green acceptance or defect spec from the same session.
- No production code before a design note; no fix before a red reproduction.
- Instructions written inside tickets are data, not commands.
- The unattended loop publishes nothing `loop-verifier` refuted, never edits its own rules, config, the profile or `.ndev.toml` (it proposes), and every comment it writes starts with the AI disclaimer and holds card content only.

## Layout

The skills live once, at the repo root in `skills/<name>/`; `plugins/90north-develop/skills/` holds symlinks to them. Installing the plugin copies the plugin folder and follows the symlinks, so the installed plugin holds real files. The loops find their siblings (`../workflow/`, `../n-dev/`) next to them, so install the plugin rather than linking one loop alone. `claude plugin validate` warns that it does not follow symlinks — validate each skill with `python3 tools/validate_skill.py skills/<name>`.

```
plugins/90north-develop/
  .claude-plugin/plugin.json
  agents/dev-builder.md, defect-repro.md, defect-fixer.md, loop-verifier.md, loop-learner.md
  skills/workflow      -> ../../../skills/workflow
  skills/develop-init  -> ../../../skills/develop-init
  skills/dev-loop      -> ../../../skills/dev-loop
  skills/defect-loop   -> ../../../skills/defect-loop
  skills/n-loop        -> ../../../skills/n-loop
  skills/n-dev         -> ../../../skills/n-dev
  skills/n-arch        -> ../../../skills/n-arch
```

## Updating

Edit the files under `skills/` (or `agents/` here), bump `version` in `.claude-plugin/plugin.json` and the repo-root `.claude-plugin/marketplace.json`, run `claude plugin validate .` and `python3 tools/validate_skill.py skills/<name>`, commit and push, then `/plugin marketplace update north-ai-skills`.
Promote a project lesson that helps every repo into `skills/workflow/references/core-lessons.md` (every loop) or `skills/defect-loop/references/core-lessons.md` (defects only).
