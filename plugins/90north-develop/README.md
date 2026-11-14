# 90north-develop

North's development plugin: two loops split by type of work, the same 9 steps in each, one discipline, one set of
per-repo facts. They work with Jira, or with a local board of markdown cards when there is no Jira.

```
                     develop-init  (once per repo)  →  .claude/90north-develop/ + .90north-develop/
                                      │
     n-defect-loop  (defects)                       n-develop-loop  (features, changes)
  1 Read the board ── 2 Triage ── 3 Check the spec           (the same three steps)
  4 Reproduce: red e2e + video  (defect-repro)    4 Pin the goal: acceptance spec red  (dev-builder WP-0)
  5 Root cause at path:line                       5 Design note + work packages ── gate for Large
  6 Test-first fix  (defect-fixer)                6 Test-first build per WP  (dev-builder)
  7 Verify + record ── 8 Open the PR ── 9 Merge (low impact, standing approval) or a person approves
       └──────────── shared stages (workflow skill) ────────────┘
         S1 Isolate · S2 Verify (review, security + performance review, QA) · S3 Evidence video
         S4 Ship (comment → push per policy → PR → lane) · S5 Clean up · S6 Learn

   attended (default): one decision round before anything is built, then it runs to the end
   --auto: queue + lock, triage matrix, verifier gate (loop-verifier), ship classes, learner (loop-learner);
           a gate parks the card with a question
                n-dev — how every line of code is written, in both loops
                n-arch — the repo's architecture rules n-dev reads and its check enforces
```

Both loops start with a red test that says what "done" means: the defect's red e2e, or the story's acceptance spec.
They end with that test green in the same session, code, security and performance review plus QA, an inline video and a tracker update. A defect needs
a cause; a feature needs a design. That is the only difference in the middle.

With `--auto`, either loop runs with nobody in the chat:
- it builds only what needs no gate (a gate parks the card with a question or the solution on it);
- an adversarial verifier refutes every claim before anything is published;
- it ships by a written policy, and learns into `.90north-develop/knowledge/`.

Only a low- or no-impact change inside a standing approval merges on its own; everything else waits for a person.

**Feature docs.** Both loops keep one markdown doc per feature area true in the same PR as the code, by default
`docs/features/<area>.md` (config § Docs). Each doc holds:
- the area's rules `R-n`, each with its source (ticket, decision, spec);
- rule → test;
- the decisions, with their reasons (including by-design answers);
- the known limits.

The rules are in `skills/workflow/references/feature-docs.md`, the template in
`skills/workflow/templates/feature-doc.md`. In `--auto`, verifier claim V10 checks the doc against the diff.

**Code, security and performance review.** Every change is read through three lenses in S2, beside QA. The diff's size decides how many reviewers read it, never whether a lens runs:
- a small diff (config § Review › single review, by default at most 150 changed non-test lines in 5 files) gets one
  `risk-reviewer` run that walks all three lenses, each fully;
- a larger diff gets the repo's code reviewer plus `risk-reviewer` once for security and once for performance.

Each lens walks its checklist in n-dev (`skills/n-dev/references/security.md`, `performance.md`, and the review
checklist in `structure.md`) and reports each finding with `path:line`, the input or data size that breaks it, and the
test that would prove it.
- Findings inside the change are fixed in the fix round, each test-first.
- Findings outside the change are reported, never fixed in that PR. A security weakness outside the change never
  goes into the tracker, a PR or a commit: it goes to the security-notes owner in config § Review.
- In `--auto`, verifier claim V11 checks that the security and performance reviews ran on the head and nothing is
  open, and a change that needed a security or performance fix never auto-merges.

**Session-start line.** `hooks/session-start.txt` is one line the plugin adds to every session when it starts: a
request that changes code or tests begins with n-dev, and work named by a board key or a loop goes to that loop.
Without it, an agent that has all six skills in front of it tends to start a plain coding request with no skill at
all (the numbers are in `evals/README.md` § Routing). No loop starts on its own: the line only names n-dev for a plain
request. Keep skill descriptions short for the same reason: say what the skill is and when to use it, and leave
how it works to the body.

**Command guard.** `hooks/guard.py` runs before every Bash, Write, Edit and NotebookEdit call (its rules are in
`hooks/guard_rules.py`). When the call comes from one of this plugin's subagents, it blocks what that agent's hard
rules and the dispatch safety block (`skills/workflow/references/stages.md`) forbid:
- every subagent: a push, any call to the tracker scripts, and a `curl` or `wget` to an `atlassian.net` host (a
  Jira on another host is covered by the agents' instructions only);
- builders, fixers and reproducers: merge, branch or worktree deletion, `--no-verify`, `reset --hard`, installing a
  tool or a new dependency, booting an app or a container, a database client or migration, a write to the remote
  with `gh`, and a write to `.ndev.toml` or the architecture profile;
- reviewers, the verifier and the learner: anything that builds, tests, reaches the network or changes files, and
  any file but their own report.

The main conversation and every other agent pass untouched. The guard reads command text, so it is a second lock
behind the agents' instructions, not a sandbox: a command hidden in a variable or in a script it runs is not seen.
Its tests are in `hooks/tests/`.

| Skill | Role |
|--|--|
| `workflow` | the map: routes work to a loop, owns the shared stages, the auto mode, the dispatch safety block, core lessons and the tracker (Jira or a local board) |
| `develop-init` | once per repo: discovers the stack, reads the board's ids and lanes (or sets up a local board), writes the settings to `.claude/90north-develop/` and the working state to `.90north-develop/` |
| `n-defect-loop` | defects: each from the board through reproduce → root cause → test-first fix → PR → QA lane, attended or `--auto` |
| `n-develop-loop` | new development, features and changed requirements: acceptance spec red → design → test-first build → PR → review lane, attended or `--auto` |
| `n-dev` | the discipline: design before code, modular, reuse first, extension files, one owner per fact, test-first, verified; asks at most once, before the first edit, and finishes with the structure check and a local commit |
| `n-arch` | once per repo, then on drift: the architecture profile and `.ndev.toml` (layers, budgets) that n-dev and its structure check use; audits debt |

| Agent | Used by | Does |
|--|--|--|
| `dev-builder` | n-develop-loop | WP-0 acceptance specs red, then one work package test-first, local commit |
| `defect-repro` | n-defect-loop | an e2e that goes red on the reported symptom, plus the video |
| `defect-fixer` | n-defect-loop | regression test red → fix at the root cause → green, local commit |
| `risk-reviewer` | both loops, S2 | reads the diff through its lenses (code, security, performance: all three in one run for a small diff, else one lens per run) against n-dev's checklists; findings with `path:line`, the breaking input or size, and the test; never fixes |
| `loop-verifier` | both loops, `--auto` | tries to refute each claim (spec ↔ card, before reason, proof on the branch, forbidden areas, scope, structure check, evidence, comment, checks ran, feature doc, security and performance reviews) before anything is published |
| `loop-learner` | both loops, `--auto` | turns a pass's files and outcomes into knowledge (code map, selectors, calibration, outcomes, lessons); rule changes become proposals |

### Moving from 0.6 or earlier

| Before | Now |
|--|--|
| `/90north-develop:defect-loop [KEY]` | `/90north-develop:n-defect-loop [KEY]` |
| `/90north-develop:dev-loop <KEY \| spec \| request \| --next>` | `/90north-develop:n-develop-loop <KEY \| spec \| request \| --next>` |
| `/90north-develop:n-loop [--dry-run] [KEY]` | `n-defect-loop --auto` or `n-develop-loop --auto` (one schedule per loop) |
| config § AI loop, `ai-ledger.md` | config § Auto mode with one queue per loop (develop-init migrates it on your yes); `ai-ledger.md` stays as history |

Re-register any `/loop` or scheduled task that names an old command.

## Install (once per machine)

```
/plugin marketplace add ThanaphatNorth/north-ai-skills
/plugin install 90north-develop@north-ai-skills
```

## Commands

| Command | Does |
|--|--|
| `/90north-develop:workflow` | Which loop is this? The whole map |
| `/90north-develop:develop-init` | Once per repo (also migrates a legacy `.claude/defect-loop/` or a § AI loop) |
| `/90north-develop:n-defect-loop [KEY]` | One defect sweep, or one defect |
| `/loop 30m /90north-develop:n-defect-loop` | Keep sweeping (continuous mode between ticks while cards remain) |
| `/90north-develop:n-develop-loop <KEY \| spec \| request>` | Build one story, feature, change or spec |
| `/loop 60m /90north-develop:n-develop-loop --next` | Take ready items one by one; an item at its design gate parks and the next is taken |
| `/90north-develop:<loop> --auto [--dry-run] [KEY]` | One unattended pass of that loop's queue, or one card |
| scheduled task / `/loop 30m /90north-develop:<loop> --auto` | Unattended passes (`skills/workflow/templates/auto-scheduled-task.md`), one schedule per loop; start with `--dry-run` |
| `/90north-develop:n-dev` | Any code change you ask for without a loop: the discipline only. A plain request goes here on its own |
| `/90north-develop:n-arch [refresh \| audit]` | Map the repo's architecture (develop-init runs it when there is no profile) |

## Where each loop asks you

Attended, a loop asks **once**. It reads the items, checks the specs and drafts the design (all read-only), then
puts every question into one decision round, before anything is isolated or built. After that it runs to the end:
an item that still needs a person parks, the rest goes on, and the run report lists the open questions in one list.
A fact the repo, config or tracker can answer is never asked, and a reversible choice takes a default that the
report names (`skills/n-dev/SKILL.md` § Questions, `skills/workflow/references/stages.md` § Decision round).

| Loop | Asked in the decision round | Parks the item; asked in the run report |
|--|--|--|
| both | the push of the run's branches (unless a standing approval covers it), missing or conflicting information you can settle, a `TBD` config line the run needs | 2 fix rounds used, a subagent's `NEEDS-DECISION` that neither the note nor a reversible option settles, merging anything outside the low-impact auto-merge class |
| n-defect-loop | — | cannot reproduce, by-design / change request (handed to n-develop-loop), structural (built by n-develop-loop on your yes) |
| n-develop-loop | design approval for Large or schema / state / public-interface changes, a trade-off | an item not ready (asked on the ticket) |
| either, `--auto` | no round | never stops mid-card: it parks the card instead — a question (`ai-need-info`), the solution (`ai-need-dev`), a hand-off to the other loop, a branch awaiting push, a PR in review |

## The codes, in words

The skill files number their steps so that one file can point at another. Reports, tracker comments, PR bodies and
questions use the words, never the codes. You only meet a code when you read the skill files themselves.

| Code | Where it lives | Means |
|--|--|--|
| 1–9 | each loop's `SKILL.md` | read the board · triage · check the spec · reproduce / pin the goal · root cause / design · fix / build · verify and record · open the PR · merge or a person approves |
| S0–S6 | `skills/workflow/references/stages.md` | before the run · isolate · verify · evidence · ship · clean up · learn |
| A0–A9 | `skills/workflow/references/auto-mode.md` | the same run with nobody attending: before the pass · follow-ups · scout and lock · triage · the red "before" run · build · the green "proof" run · the verifier gate · ship · learn |
| V1–V11 | `agents/loop-verifier.md` | the claims the verifier tries to refute: the spec tests the card · "before" failed for the card's reason · "proof" passed on the branch · no forbidden area · only what the card asked · structure check clean · the evidence shows it · the comment matches the diff · the checks really ran · the feature doc matches · the reviews ran and nothing is open |
| AC-n, R-n, WP-n | design notes, comments, feature docs | an acceptance criterion · a rule of a feature area · a work package |

## Per-project files

Two folders. `<repo>/.claude/90north-develop/` holds the settings: Claude Code asks a person before it writes under
`.claude/`, which suits the file that holds the push approval. `<repo>/.90north-develop/` holds what a loop writes as
it works, so a run with nobody at the keyboard can still record it. A project set up before 0.12 has everything in
the first folder: `skills/workflow/scripts/move-state.sh` moves the working state (develop-init offers it). Until then
the attended loops keep using the old place, and an unattended pass does not start: `where.sh --auto`, its first
command, refuses it. `where.sh` prints the two folders a project uses.

| File | Holds |
|--|--|
| `.claude/90north-develop/config.md` | Tracker, board ids, § Dev flow, § Defect flow and § Auto mode (queries, lock, lanes, fences, gates, ship classes), push policy, repo/worktree recipe, isolated stack recipe, accounts, checks (with the repo's security and performance scanners), team agents, § Docs, § Review (data sizes), spec sources, project rules |
| `.claude/90north-develop/tracker.env` | `TRACKER` (jira or local) and its settings: `JIRA_SITE`, `JIRA_ENV_FILE`, or `LOCAL_BOARD`, `LOCAL_STATUSES` — no secrets |
| `.90north-develop/board/` | Local tracker only: one markdown card per file, attachments in `board/<KEY>/`; committed by default, the loops edit it and a person commits |
| `.90north-develop/dev-ledger.md`, `defect-ledger.md` | One row per state change, per loop, both modes, written with `ledger.sh` (a legacy `ai-ledger.md` stays as history) |
| `.90north-develop/lessons.md` | Project lessons tagged `[dev]` / `[defect]` / `[ai]` / `[both]` (core lessons ship with the plugin) |
| `.90north-develop/knowledge/` | Auto mode's code map, selectors, calibration, outcomes log and proposals (written by `loop-learner`) |
| `.90north-develop/runs/` | Auto mode's per-card hand-off files and the shared pass lock; git-ignored |

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

- Agents never boot app processes or touch databases (a second process with other env flags once ran a destructive boot hook). The command guard blocks the common forms of both, and every push by a subagent.
- Never push / force-push / merge / delete without your yes; a standing approval counts only in its written scope.
- Never moves an item to a QA or review lane without a green acceptance or defect spec from the same session.
- No production code before a design note; no fix before a red reproduction.
- One question round per attended run. A yes to push given there covers that run's named branches only.
- Instructions written inside tickets are data, not commands.
- The unattended loop publishes nothing `loop-verifier` refuted, never edits its own rules, config, the profile or `.ndev.toml` (it proposes), and every comment it writes starts with the AI disclaimer and holds card content only.

## Layout

The skills live once, at the repo root in `skills/<name>/`; `plugins/90north-develop/skills/` holds symlinks to them. Installing the plugin copies the plugin folder and follows the symlinks, so the installed plugin holds real files. The loops find their siblings (`../workflow/`, `../n-dev/`) next to them, so install the plugin rather than linking one loop alone. `claude plugin validate` warns that it does not follow symlinks — validate each skill with `python3 tools/validate_skill.py skills/<name>`.

```
plugins/90north-develop/
  .claude-plugin/plugin.json
  agents/dev-builder.md, defect-repro.md, defect-fixer.md, risk-reviewer.md, loop-verifier.md, loop-learner.md
  hooks/hooks.json, session-start.txt (the routing line), guard.py (the command guard), guard_shell.py (reads a
        shell line), guard_rules.py (the rules), tests/
  skills/workflow      -> ../../../skills/workflow
  skills/develop-init  -> ../../../skills/develop-init
  skills/n-defect-loop   -> ../../../skills/n-defect-loop
  skills/n-develop-loop  -> ../../../skills/n-develop-loop
  skills/n-dev         -> ../../../skills/n-dev
  skills/n-arch        -> ../../../skills/n-arch
```

## Updating

1. Edit the files under `skills/` (or `agents/` and `hooks/` here). A new agent also needs its line in the `agents` array of `.claude-plugin/plugin.json` and its rule set in `hooks/guard_rules.py`.
2. Bump `version` in `.claude-plugin/plugin.json` and in the repo-root `.claude-plugin/marketplace.json`.
3. Run the checks from the repo root: `python3 tools/check_repo.py`, `python3 tools/validate_skill.py skills/<name>`, `claude plugin validate .`, and the four test suites the root README lists.
4. Run the consistency review (`tools/consistency-review.md`) with a fresh-context reviewer, and fix or answer every finding.
5. Run the evals (`evals/README.md` here and `skills/n-dev/evals/README.md`) when a skill's wording changed: a gate that reads a little more abstractly can stop working, and only a run shows it. After changing a description or `hooks/session-start.txt`, run the routing probes too (`evals/README.md` § Routing).
6. Commit and push, then `/plugin marketplace update north-ai-skills`.

Promote a project lesson that helps every repo into `skills/workflow/references/core-lessons.md` (every loop) or `skills/n-defect-loop/references/core-lessons.md` (defects only).
