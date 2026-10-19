---
name: defect-loop-init
description: Set up the defect loop in a new project — discover the repo's stack, test commands, e2e setup and agents, check Jira access, read the board's issue types, statuses and transition ids, and write .claude/defect-loop/{config.md, tracker.env, ledger.md, lessons.md}. Asks the user only for what the repo and Jira can't answer (credentials file path, push policy, comment language). Use when the user says "set up the defect loop here", "init defect-loop", or /90north-develop:defect-loop finds no config.
---

# 90north-develop · defect-loop-init

Goal: a `config.md` where every value was checked, so `/90north-develop:defect-loop` never guesses. Write nothing outside `<repo-root>/.claude/defect-loop/` (plus the project's `.claude/launch.json` if the user agrees). If a `config.md` already exists, show what you would change and update it in place; never overwrite it blind.

## 1. Find the project
- Repo root and remote: `git rev-parse --show-toplevel`, `git remote -v`, default/base branch (`git symbolic-ref refs/remotes/origin/HEAD`, or ask: develop/main?).
- The loop folder: `DL=<root>/.claude/defect-loop` (if the session root holds several repos, ask which repo the board belongs to and put `DL` in the session root's `.claude/`).

## 2. Discover the stack (read, don't run servers)
- Packages and scripts: `package.json` files (typecheck, test, lint — note if lint runs `--fix`), `pyproject`/`go.mod`/etc.
- e2e: Playwright/Cypress config (baseURL env, output folder, globalSetup/teardown, video setting), helpers for login and test users, naming convention for test data and how teardown cleans it, whether browsers are installed (`ls ~/Library/Caches/ms-playwright` or `npx playwright --version`; if headless chromium is missing, plan a `channel: 'chrome'` wrapper config).
- How the app boots locally: docker-compose, README, `.env.example`, launch configs; DB engine/port; **boot hooks** that seed or clean data and the env flags that switch them; dev login (password / OTP dev code / SSO).
- Agents and skills in the repo (`.claude/agents/*.md`, `.claude/skills/*`) usable as code reviewer, QA, verifier, house rules; spec / decision log and requirements docs.
- Project memory files and CLAUDE.md for ports, DB and rules already learned.

## 3. Jira
- Ask the user for: site URL, project key, board URL. Ask where the credentials file is (default `~/.config/<project>-jira.env` with `JIRA_EMAIL`, `JIRA_TOKEN`; tell them how to create an API token at id.atlassian.com → Security → API tokens if needed). Never ask them to paste the token in chat.
- Write `DL/tracker.env` from `templates/tracker.env`. Check access with `../defect-loop/scripts/jira-search.sh 'project = <KEY> ORDER BY created DESC'` — the scripts are in `../defect-loop/scripts/` relative to this skill's base directory (the script tightens the credentials file to 600 and never prints it). If an Atlassian MCP connector is available, test it too and record which one works.
- Read the board facts **by id**: issue types (`/rest/api/3/issue/createmeta/<KEY>/issuetypes` or from a search), statuses of open issues, and the transitions offered from each open status (`../defect-loop/scripts/jira-transition.sh <KEY> --list` on a real ticket in each status). Record the path to the QA lane and any screen fields (e.g. root-cause cascading field). Mark Done-category transitions as never-use.
- Build the open-defect query with ids and run it plus the sanity query; the counts must agree.

## 4. Ask only what's left (one AskUserQuestion, ≤4 questions)
- Push policy: ask every time (default) / standing OK to push `fix/<KEY>-*` and open PRs (never force-push, merge, push to base, delete branches).
- Comment language: match the ticket / Thai / English.
- Which repo agent is the reviewer / QA, if more than one fits.
- Anything discovery couldn't settle (e.g. the DB to copy for isolated runs).

## 5. Write the files
- `DL/config.md` from `templates/config.md`, every line filled or marked `TBD — <what's needed>`.
- `DL/ledger.md`: `# defect-loop — ledger` + header `| date time | KEY | state | branch @ sha | worktree · ports · DB | evidence | next |` and `|--|--|--|--|--|--|--|`.
- `DL/lessons.md`: `# defect-loop — project lessons` + one line on the entry format. Do not copy core lessons; the sweep reads them from the plugin.
- `tracker.env` holds no secrets and may be committed; the credentials file stays outside the repo. If `.claude/` is git-tracked, ask whether `ledger.md` should be committed or added to `.gitignore`.

## 6. Hand over
Tell the user in a few lines: what was found, what is `TBD`, and the commands:
- one sweep: `/90north-develop:defect-loop`
- on a loop: `/loop 30m /90north-develop:defect-loop` (continuous mode keeps going between ticks while cards remain).
