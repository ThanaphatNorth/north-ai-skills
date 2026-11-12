---
name: develop-init
description: Set up the 90north-develop loops (n-defect-loop and n-develop-loop, attended and, when wanted, unattended with --auto) in a project — discover the repo's stack, test commands, e2e setup and agents, check Jira access and read the board's issue types, statuses, transition ids and custom fields (or, with no Jira, set up a local board of markdown cards in the repo), and write .claude/90north-develop/{config.md, tracker.env, dev-ledger.md, defect-ledger.md, lessons.md} (plus knowledge/ and runs/ for auto mode). Migrates a legacy .claude/defect-loop/ folder with the user's yes. Asks the user only for what the repo and Jira can't answer (credentials file path, push policy, comment language, design-gate rules). Use when the user says "set up the dev loop / defect loop here", "init 90north-develop", or a loop finds no config.
---

# 90north-develop · develop-init

Goal: one `config.md` where every value was checked, so neither loop guesses. Both loops read the same file; each fact has one line in it. Write nothing outside `<repo-root>/.claude/90north-develop/` (plus the project's `.claude/launch.json` if the user agrees). If a `config.md` already exists, show what you would change and update it in place; never overwrite it blind. The Jira scripts are in the workflow skill: `W = ../workflow/` from this skill's base directory.

## 0. Legacy folder
`<root>/.claude/defect-loop/` exists → it is the old single-loop setup. Show the user the plan and ask before moving anything:
- `config.md` → `.claude/90north-develop/config.md`, then add § Dev flow and move the defect query, sanity query, QA-lane path and structural fence under § Defect flow;
- `ledger.md` → `defect-ledger.md`; `tracker.env`, `lessons.md` move as they are (tag old lessons `[defect]`);
- use `git mv` when the folder is tracked, else `mv`; nothing is deleted. Until the user says yes, leave it — n-defect-loop and the scripts still read the legacy folder.

## 1. Find the project
- Repo root and remote: `git rev-parse --show-toplevel`, `git remote -v`, default/base branch (`git symbolic-ref refs/remotes/origin/HEAD`, or ask: develop/main?).
- `DL=<root>/.claude/90north-develop`. If the session root holds several repos, ask which repo the board belongs to and put `DL` in the session root's `.claude/`.

## 2. Discover the stack (read, don't run servers)
- Packages and scripts: `package.json` files (typecheck, test, lint — note if lint runs `--fix`), `pyproject`/`go.mod`/etc.
- e2e: Playwright/Cypress config (baseURL env, output folder, globalSetup/teardown, video setting), helpers for login and test users, naming convention for test data and how teardown cleans it, whether browsers are installed (`ls ~/Library/Caches/ms-playwright` or `npx playwright --version`; if headless chromium is missing, plan a `channel: 'chrome'` wrapper config).
- How the app boots locally: docker-compose, README, `.env.example`, launch configs; DB engine/port; **boot hooks** that seed or clean data and the env flags that switch them; dev login (password / OTP dev code / SSO).
- Agents and skills in the repo (`.claude/agents/*.md`, `.claude/skills/*`) usable as code reviewer, security or performance reviewer, QA, verifier, house rules, demo recorder; spec / decision log, requirements docs, design files and where design notes for Large work belong (docs folder, ADRs).
- Security and performance scanners the repo already runs (package scripts, CI workflows, `.gitleaks.toml`, `.semgrep.yml`, CodeQL, Dependabot, `size-limit`, `lighthouserc`, k6 or benchmark scripts): put their commands in config § Checks; add none. Data sizes for config § Review: from the profile, seed data, an admin or analytics page the user names, or `TBD`.
- Project memory files and CLAUDE.md for ports, DB and rules already learned.
- Architecture profile: if `docs/architecture/profile.md` (or `.ndev.toml`'s `[profile] path`) exists, read it and link it in `config.md` instead of re-deriving extension points and state owners; if it does not, run `../n-arch/SKILL.md` (create mode) before step 5, and link what it writes.
- Feature docs: find the repo's docs system (a `docs/` folder, Docusaurus or another site, a handbook, ADRs) and any existing per-feature docs. Fill config § Docs: on by default, in `docs/features/` unless the repo already has a home for them; follow that system's conventions (`W/references/feature-docs.md`). Docs are created by the first change in each area, never in bulk here. Ask only if two homes fit.

## 3. Tracker: Jira, or a local board
First ask whether the project uses Jira. With no Jira, take **3b** instead of the Jira steps; everything else in this skill is the same (`W/references/trackers.md` has the verbs, the card format and the query form).

### 3a. Jira
- Ask the user for: site URL, project key, board URL. Ask where the credentials file is (default `~/.config/<project>-jira.env` with `JIRA_EMAIL`, `JIRA_TOKEN`; tell them how to create an API token at id.atlassian.com → Security → API tokens if needed). Never ask them to paste the token in chat.
- Write `DL/tracker.env` from `templates/tracker.env`. Check access with `W/scripts/tracker.sh search 'project = <KEY> ORDER BY created DESC'` (the script tightens the credentials file to 600 and never prints it). If an Atlassian MCP connector is available, test it too and record which one works.
- Read the board facts **by id**: issue types (`/rest/api/3/issue/createmeta/<KEY>/issuetypes` or from a search) — which are defects, which are stories/tasks/improvements; statuses of open issues; the transitions offered from each open status (`W/scripts/tracker.sh transition <KEY> --list` on a real ticket in each status). Record the path to the QA lane for defects and to the review lane for stories, and any screen fields (e.g. a root-cause cascading field). Mark Done-category transitions as never-use.
- Build both queries with ids — the open-defect query and the ready-for-dev query — run each with its sanity query; the counts must agree.
- Auto mode (only when the user will run a loop with `--auto`): read the custom fields by id (`/rest/api/3/field`: severity, environment, steps, expected result, acceptance criteria, any "AI status" or "AI summary" field and its type), the option ids of a select field used as the lock, and the transitions for need-info, start, review, after-merge and back-to-ready. Build each loop's queue (its own query plus its hand-off label `ai-to-defect` / `ai-to-develop`), the stale-lock and the follow-up queries with ids and run each. Fill § Auto mode per `W/references/auto-project-pack.md` § New project, step by step; the never-touch list starts from the profile's Contracts and State owners.

### 3b. No Jira: a local board
- Write `DL/tracker.env` from `templates/tracker.env` with `TRACKER=local`; keep `LOCAL_STATUSES` at the default (`todo,in-progress,need-info,review,ready-for-qa,reopened,done`) unless the team names other lanes, and set `LOCAL_BOARD` (absolute, or relative to `DL`) only to move the board out of `DL/board/`.
- Create the board folder, copy `W/templates/card.md` into it as `_template.md` (no key, so search skips it), and pick one key prefix for the repo (`TASK-1.md`, `TASK-2.md` …). Check with `W/scripts/tracker.sh search 'status=todo'` (`# 0 issue(s)` on an empty board).
- Board facts are the `LOCAL_STATUSES` names; there are no ids. Mark `done` (and any other closing status) never-use, as with Jira's Done category. Defects are `type: bug`, development is `type: story | task | improvement`.
- Queries in the local form, each with its sanity query: open defects `type=bug status=todo,reopened`, ready for dev `type=story,task,improvement status=todo`, and for auto mode the queues `labels=ai-queue -labels=ai-processing type=bug status=todo,reopened` (defects) and `labels=ai-queue -labels=ai-processing -type=bug status=todo,reopened` (development), each with its hand-off query (`labels=ai-to-defect` / `labels=ai-to-develop`, minus the lock, ready statuses only), and stale locks `labels=ai-processing age>2h`. Lanes are status names (to QA: `in-progress → review → ready-for-qa`). Fields are header names or section headings (`severity`, `acceptance-criteria`); the AI summary goes to a `## AI summary` section through `--field-md`.
- The board is committed by default, so the team shares it. The loops edit cards in the main checkout and never commit them; each run report lists the changed cards for a person to commit. Git-ignore the folder only if the user asks.

## 4. Ask only what's left (one AskUserQuestion, ≤4 questions)
- Push policy: ask every time (default) / standing OK to push `fix/<KEY>-*` and `feat/<KEY>-*` and open PRs (never force-push, merge, push to base, delete branches).
- Comment language: match the ticket / Thai / English.
- Dev design gate: stop only for Large and schema/state/interface changes (default) / stop before every build / and whether to post design notes to Jira.
- Which repo agent is the reviewer / QA, if more than one fits; anything discovery couldn't settle (e.g. the DB to copy for isolated runs).
- Auto mode, when wanted: queue by label (default) or by an existing field; auto-merge for low- or no-impact changes off (default) or on, and if on, the user's exact words for the standing approval that names merge. Fold these into the same ≤4 questions; leave the rest of § Auto mode at its defaults.

## 5. Write the files
- `DL/config.md` from `templates/config.md`, every line filled or marked `TBD — <what's needed>`.
- `DL/dev-ledger.md` and `DL/defect-ledger.md`: `# <flow>-loop — ledger` + header `| date time | KEY | state | branch @ sha | worktree · ports · DB | evidence | next |` and `|--|--|--|--|--|--|--|`.
- Auto mode: `DL/knowledge/` with empty `code-map.md`, `selectors.md`, `calibration.md` (factor 1.0), `outcomes.jsonl` and `proposals/`, and `DL/runs/` with a `.gitignore` holding `*` and `!.gitignore`. Both loops write their auto-mode rows into their own ledger. A repo set up with 0.5–0.6 keeps its `ai-ledger.md` as history, and its config § AI loop becomes § Auto mode on the user's yes: the old queue line splits into one queue per loop, everything else moves as it is.
- `DL/lessons.md`: `# 90north-develop — project lessons` + one line on the entry format (`- [date] [dev|defect|ai|both] <tag> seen:N — symptom → cause → rule.`). Do not copy core lessons; the loops read them from the plugin.
- `tracker.env` holds no secrets and may be committed; the credentials file stays outside the repo. If `.claude/` is git-tracked, ask whether the ledgers should be committed or added to `.gitignore`.

## 6. Hand over
Tell the user in a few lines: what was found, what is `TBD`, and the commands:
- which flow: `/90north-develop:workflow`
- a story, feature or change: `/90north-develop:n-develop-loop <KEY>` · the next ready one on a loop: `/loop 60m /90north-develop:n-develop-loop --next`
- defects: `/90north-develop:n-defect-loop` · on a loop: `/loop 30m /90north-develop:n-defect-loop`
- local board: add cards by copying `board/_template.md` to `board/<PREFIX>-<n>.md`; commit card changes after a run
- unattended: `/90north-develop:n-defect-loop --auto --dry-run` (or `n-develop-loop`) by hand first, then one schedule per loop from `W/templates/auto-scheduled-task.md`
