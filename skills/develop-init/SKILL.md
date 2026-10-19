---
name: develop-init
description: Set up the 90north-develop flows (dev-loop and defect-loop) in a project — discover the repo's stack, test commands, e2e setup and agents, check Jira access, read the board's issue types, statuses and transition ids for stories and defects, and write .claude/90north-develop/{config.md, tracker.env, dev-ledger.md, defect-ledger.md, lessons.md}. Migrates a legacy .claude/defect-loop/ folder with the user's yes. Asks the user only for what the repo and Jira can't answer (credentials file path, push policy, comment language, design-gate rules). Use when the user says "set up the dev loop / defect loop here", "init 90north-develop", or a loop finds no config.
---

# 90north-develop · develop-init

Goal: one `config.md` where every value was checked, so neither loop guesses. Both loops read the same file; each fact has one line in it. Write nothing outside `<repo-root>/.claude/90north-develop/` (plus the project's `.claude/launch.json` if the user agrees). If a `config.md` already exists, show what you would change and update it in place; never overwrite it blind. The Jira scripts are in the workflow skill: `W = ../workflow/` from this skill's base directory.

## 0. Legacy folder
`<root>/.claude/defect-loop/` exists → it is the old single-loop setup. Show the user the plan and ask before moving anything:
- `config.md` → `.claude/90north-develop/config.md`, then add § Dev flow and move the defect query, sanity query, QA-lane path and structural fence under § Defect flow;
- `ledger.md` → `defect-ledger.md`; `tracker.env`, `lessons.md` move as they are (tag old lessons `[defect]`);
- use `git mv` when the folder is tracked, else `mv`; nothing is deleted. Until the user says yes, leave it — defect-loop and the scripts still read the legacy folder.

## 1. Find the project
- Repo root and remote: `git rev-parse --show-toplevel`, `git remote -v`, default/base branch (`git symbolic-ref refs/remotes/origin/HEAD`, or ask: develop/main?).
- `DL=<root>/.claude/90north-develop`. If the session root holds several repos, ask which repo the board belongs to and put `DL` in the session root's `.claude/`.

## 2. Discover the stack (read, don't run servers)
- Packages and scripts: `package.json` files (typecheck, test, lint — note if lint runs `--fix`), `pyproject`/`go.mod`/etc.
- e2e: Playwright/Cypress config (baseURL env, output folder, globalSetup/teardown, video setting), helpers for login and test users, naming convention for test data and how teardown cleans it, whether browsers are installed (`ls ~/Library/Caches/ms-playwright` or `npx playwright --version`; if headless chromium is missing, plan a `channel: 'chrome'` wrapper config).
- How the app boots locally: docker-compose, README, `.env.example`, launch configs; DB engine/port; **boot hooks** that seed or clean data and the env flags that switch them; dev login (password / OTP dev code / SSO).
- Agents and skills in the repo (`.claude/agents/*.md`, `.claude/skills/*`) usable as code reviewer, QA, verifier, house rules, demo recorder; spec / decision log, requirements docs, design files and where design notes for Large work belong (docs folder, ADRs).
- Project memory files and CLAUDE.md for ports, DB and rules already learned.

## 3. Jira
- Ask the user for: site URL, project key, board URL. Ask where the credentials file is (default `~/.config/<project>-jira.env` with `JIRA_EMAIL`, `JIRA_TOKEN`; tell them how to create an API token at id.atlassian.com → Security → API tokens if needed). Never ask them to paste the token in chat.
- Write `DL/tracker.env` from `templates/tracker.env`. Check access with `W/scripts/jira-search.sh 'project = <KEY> ORDER BY created DESC'` (the script tightens the credentials file to 600 and never prints it). If an Atlassian MCP connector is available, test it too and record which one works.
- Read the board facts **by id**: issue types (`/rest/api/3/issue/createmeta/<KEY>/issuetypes` or from a search) — which are defects, which are stories/tasks/improvements; statuses of open issues; the transitions offered from each open status (`W/scripts/jira-transition.sh <KEY> --list` on a real ticket in each status). Record the path to the QA lane for defects and to the review lane for stories, and any screen fields (e.g. a root-cause cascading field). Mark Done-category transitions as never-use.
- Build both queries with ids — the open-defect query and the ready-for-dev query — run each with its sanity query; the counts must agree.

## 4. Ask only what's left (one AskUserQuestion, ≤4 questions)
- Push policy: ask every time (default) / standing OK to push `fix/<KEY>-*` and `feat/<KEY>-*` and open PRs (never force-push, merge, push to base, delete branches).
- Comment language: match the ticket / Thai / English.
- Dev design gate: stop only for Large and schema/state/interface changes (default) / stop before every build / and whether to post design notes to Jira.
- Which repo agent is the reviewer / QA, if more than one fits; anything discovery couldn't settle (e.g. the DB to copy for isolated runs).

## 5. Write the files
- `DL/config.md` from `templates/config.md`, every line filled or marked `TBD — <what's needed>`.
- `DL/dev-ledger.md` and `DL/defect-ledger.md`: `# <flow>-loop — ledger` + header `| date time | KEY | state | branch @ sha | worktree · ports · DB | evidence | next |` and `|--|--|--|--|--|--|--|`.
- `DL/lessons.md`: `# 90north-develop — project lessons` + one line on the entry format (`- [date] [dev|defect|both] <tag> seen:N — symptom → cause → rule.`). Do not copy core lessons; the loops read them from the plugin.
- `tracker.env` holds no secrets and may be committed; the credentials file stays outside the repo. If `.claude/` is git-tracked, ask whether the ledgers should be committed or added to `.gitignore`.

## 6. Hand over
Tell the user in a few lines: what was found, what is `TBD`, and the commands:
- which flow: `/90north-develop:workflow`
- a story: `/90north-develop:dev-loop <KEY>` · the next ready one on a loop: `/loop 60m /90north-develop:dev-loop --next`
- defects: `/90north-develop:defect-loop` · on a loop: `/loop 30m /90north-develop:defect-loop`
