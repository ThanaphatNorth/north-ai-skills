---
name: develop-init
description: Set up the 90north-develop loops in a project — discover the stack, test commands and e2e setup, read the board from Jira (or set up a local board of markdown cards), and write the settings to .claude/90north-develop/ (config, tracker) and the working state to .90north-develop/ (ledgers, lessons, a local board). Asks one round of at most 4 questions. Use when the user says "set up the dev loop / defect loop here", "init 90north-develop", or a loop finds no config.
---

# 90north-develop · develop-init

Goal: one `config.md` where every value was checked, so neither loop guesses. Both loops read the same file; each fact has one line in it. Write nothing outside `<repo-root>/.claude/90north-develop/` (settings) and `<repo-root>/.90north-develop/` (working state). If a `config.md` already exists, update it in place and list what changed; never overwrite it blind. The tracker scripts are in the workflow skill: `W = ../workflow/` from this skill's base directory.

Order: discover (steps 1–3, read-only) → **one question round** (step 4) → read the tracker → write → hand over. Nothing is asked outside the round, and a step that cannot finish writes `TBD — <what's needed>` and goes on.

## 1. Find the project
- Repo root and remote: `git rev-parse --show-toplevel`, `git remote -v`. Base branch: `git symbolic-ref refs/remotes/origin/HEAD`, else the branch most merged PRs target (`gh pr list --state merged -L 20 --json baseRefName`), else `main` marked `default`.
- `DC=<root>/.claude/90north-develop` holds the settings (`config.md`, `tracker.env`); `DL=<root>/.90north-develop` holds the working state (ledgers, lessons, the board, knowledge, runs), outside `.claude/` so a session that can ask nobody can still write it. When the session root holds several repos, both go in the session root; which repo the board belongs to is a round question only if step 3's evidence does not name one.
- A project that is already set up: run `W/scripts/where.sh` and use the two folders it prints. A `NOTE=` line means the working state has not moved out of `.claude/` yet, or is in two places: run `W/scripts/move-state.sh --dry-run` and keep what it prints for the round (in two places it names what is in both, and which copy to keep is the user's answer, never this skill's). Until the user says yes, every file this skill writes goes to the folders as printed, never to a new `.90north-develop/`.
- Legacy folder: `<root>/.claude/defect-loop/` is the old single-loop setup. Note it for the round, and leave it until the user says yes — n-defect-loop and the scripts still read it.

## 2. Discover the stack (read, don't run servers)
- Packages and scripts: `package.json` files (typecheck, test, lint — note if lint runs `--fix`), `pyproject`/`go.mod`/etc.
- e2e: Playwright/Cypress config (baseURL env, output folder, globalSetup/teardown, video setting), helpers for login and test users, naming convention for test data and how teardown cleans it, whether browsers are installed (`ls ~/Library/Caches/ms-playwright` or `npx playwright --version`; if headless chromium is missing, plan a `channel: 'chrome'` wrapper config).
- How the app boots locally: docker-compose, README, `.env.example`, launch configs; DB engine/port; **boot hooks** that seed or clean data and the env flags that switch them; dev login (password / OTP dev code / SSO).
- Agents and skills in the repo (`.claude/agents/*.md`, `.claude/skills/*`) usable as code reviewer, security or performance reviewer, QA, verifier, house rules, demo recorder; spec / decision log, requirements docs, design files and where design notes for Large work belong (docs folder, ADRs).
- Security and performance scanners the repo already runs (package scripts, CI workflows, `.gitleaks.toml`, `.semgrep.yml`, CodeQL, Dependabot, `size-limit`, `lighthouserc`, k6 or benchmark scripts): put their commands in config § Checks; add none. Data sizes for config § Review: from the profile, seed data, or `TBD — <who can give the sizes>`; a repo with no data store gets `none (no data store)`, which is a finding and not a TBD.
- Project memory files and CLAUDE.md for ports, DB and rules already learned.
- Architecture profile: if `docs/architecture/profile.md` (or `.ndev.toml`'s `[profile] path`) exists, read it and link it in `config.md` instead of re-deriving extension points and state owners; if it does not, run `../n-arch/SKILL.md` (create mode) before step 6, and link what it writes. It settles its choices by rule there and asks nothing.
- Feature docs: find the repo's docs system (a `docs/` folder, Docusaurus or another site, a handbook, ADRs) and any existing per-feature docs. Fill config § Docs: on by default, in `docs/features/` unless the repo already has a home for them; follow that system's conventions (`W/references/feature-docs.md`). Docs are created by the first change in each area, never in bulk here. Two homes fit → the one that already holds per-feature pages, marked `default`.

## 3. Find the tracker from evidence
Look for what the project already uses before asking about it:
- an existing `DC/tracker.env`, or the legacy folder's config;
- issue keys in recent work: `git log -200 --format='%s %D' | grep -oE '[A-Z][A-Z0-9]+-[0-9]+' | sed 's/-[0-9]*$//' | sort | uniq -c | sort -rn | head -3`;
- a credentials file, by name only (`ls ~/.config/*-jira.env`): never read it;
- an Atlassian MCP connector in the session: its visible projects name the site and the key;
- a board link in README, CONTRIBUTING or the PR template.

A site and key found → the round's recommended tracker. Nothing found → recommend the local board.

## 4. The one question round (one AskUserQuestion, at most 4 questions)
Ask only what steps 1–3 could not settle: the recommended option first, each option saying what it sets. Take the questions in this order until 4 are used. Whatever is not asked takes its default and goes into config marked `default`.

1. **Tracker.** The Jira site and project key found (or typed in: site URL, project key, board URL) / a local board in the repo. The credentials file is `~/.config/<project>-jira.env` (`JIRA_EMAIL`, `JIRA_TOKEN`) unless the user names another. The user creates it in their own terminal with `W/scripts/jira-login.sh`, which asks for the token without echoing it; never ask for the token in chat.
2. **Push policy.** Ask once per run, in its decision round (default) / a standing OK to push `fix/<KEY>-*` and `feat/<KEY>-*` and open PRs — never force-push, merge, push to base or delete branches. Record the user's exact words.
3. **Auto mode.** Not now (default) / on, queue by label / on, with auto-merge for low- or no-impact changes, which needs the user's exact words for a standing approval that names merge. The rest of § Auto mode keeps its defaults.
4. **Only when it applies**, taking the place of the last question above: move the working state out of `.claude/` (on a yes run `W/scripts/move-state.sh`: nothing is copied, overwritten or deleted, and tracked files move with `git mv`; without a yes leave it, the scripts still read the old place) · move the legacy folder, or turn a 0.5–0.6 config § AI loop into § Auto mode (plan below) · which repo the board belongs to · a fact discovery found two equal answers for where a wrong pick costs a run (the DB to copy for isolated runs, which of two agents reviews).

Nobody to answer (a headless run, or the user said not to ask): take the recommended option of every question, mark each `default`, and name them first in the hand-over. A move of the user's files (the working state out of `.claude/`, the legacy folder) is never taken without a yes: the hand-over names it first, with what `move-state.sh --dry-run` listed.

Not asked, written as `default`: comment language = match the ticket · design gate = Large and schema/state/interface changes, design notes not posted to the tracker · reviewer and QA = the repo agent whose description names the role, else the plugin's fallback · ledgers left untracked.

Legacy move, on a yes (nothing is deleted; `git mv` when the folder is tracked, else `mv`):
- `config.md` → `.claude/90north-develop/config.md`, then add § Dev flow and move the defect query, sanity query, QA-lane path and structural fence under § Defect flow;
- `ledger.md` → `DL/defect-ledger.md`; `lessons.md` → `DL/lessons.md` (tag old lessons `[defect]`); `tracker.env` → `DC/tracker.env`.

## 5. Read the tracker
`W/references/trackers.md` has the verbs, the card format and the query form for both backends.

### 5a. Jira
- Write `DC/tracker.env` from `templates/tracker.env`. Check access with `W/scripts/tracker.sh search 'project = <KEY> ORDER BY created DESC'` (the script tightens the credentials file to 600 and never prints it). If an Atlassian MCP connector is available, test it too and record which one works.
- No credentials file, or access fails → write the board lines as `TBD — run W/scripts/jira-login.sh <path> in your terminal (API token: id.atlassian.com → Security → API tokens), then run develop-init again`, finish every other step, and put it first in the hand-over. Do not wait here.
- Read the board facts **by id**: issue types (`/rest/api/3/issue/createmeta/<KEY>/issuetypes` or from a search) — which are defects, which are stories/tasks/improvements; statuses of open issues; the transitions offered from each open status (`W/scripts/tracker.sh transition <KEY> --list` on a real ticket in each status). Record the path to the QA lane for defects and to the review lane for stories, and any screen fields (e.g. a root-cause cascading field). Mark Done-category transitions as never-use.
- Build both queries with ids — the open-defect query and the ready-for-dev query — run each with its sanity query; the counts must agree.
- Auto mode (only when the round chose it): read the custom fields by id (`/rest/api/3/field`: severity, environment, steps, expected result, acceptance criteria, any "AI status" or "AI summary" field and its type), the option ids of a select field used as the lock, and the transitions for need-info, start, review, after-merge and back-to-ready. Build each loop's queue (its own query plus its hand-off label `ai-to-defect` / `ai-to-develop`), the stale-lock and the follow-up queries with ids and run each. Fill § Auto mode per `W/references/auto-project-pack.md` § New project, step by step; the never-touch list starts from the profile's Contracts and State owners.

### 5b. No Jira: a local board
- Write `DC/tracker.env` from `templates/tracker.env` with `TRACKER=local`; keep `LOCAL_STATUSES` at the default (`todo,in-progress,need-info,review,ready-for-qa,reopened,done`) unless the team names other lanes, and set `LOCAL_BOARD` (absolute, or relative to `DL`) only to move the board out of `DL/board/`.
- Create the board folder, copy `W/templates/card.md` into it as `_template.md` (no key, so search skips it), and pick one key prefix for the repo (`TASK-1.md`, `TASK-2.md` …). Check with `W/scripts/tracker.sh search 'status=todo'` (`# 0 issue(s)` on an empty board).
- Board facts are the `LOCAL_STATUSES` names; there are no ids. Mark `done` (and any other closing status) never-use, as with Jira's Done category. Defects are `type: bug`, development is `type: story | task | improvement`.
- Queries in the local form, each with its sanity query: open defects `type=bug status=todo,reopened`, ready for dev `type=story,task,improvement status=todo`, and for auto mode the queues `labels=ai-queue -labels=ai-processing type=bug status=todo,reopened` (defects) and `labels=ai-queue -labels=ai-processing -type=bug status=todo,reopened` (development), each with its hand-off query (`labels=ai-to-defect` / `labels=ai-to-develop`, minus the lock, ready statuses only), and stale locks `labels=ai-processing age>2h`. Lanes are status names (to QA: `in-progress → review → ready-for-qa`). Fields are header names or section headings (`severity`, `acceptance-criteria`); the AI summary goes to a `## AI summary` section through `--field-md`.
- The board is committed by default, so the team shares it. The loops edit cards in the main checkout and never commit them; each run report lists the changed cards for a person to commit. Git-ignore the folder only if the user asks.

## 6. Write the files
- `DC/config.md` from `templates/config.md`, every line filled, marked `default` (not asked; the value taken), or marked `TBD — <what's needed>`. Before the hand-over, read the written file once from top to bottom: every value that came from neither the repo, the tracker nor an answer carries `(default)`, every `TBD` names what would settle it, and no `<a | b>` choice of the template is left. If the session refuses the write of `DC/config.md` or `DC/tracker.env` (Claude Code asks a person before it writes under `.claude/`, and a session that can ask nobody refuses), do not write the file another way: finish the other files, say first in the hand-over that the write was refused, and put the whole drafted `config.md` there so the user can save it or allow the write and run develop-init again.
- `DL/dev-ledger.md` and `DL/defect-ledger.md`: `# <flow>-loop — ledger` + header `| date time | KEY | state | branch @ sha | worktree · ports · DB | evidence | next |` and `|--|--|--|--|--|--|--|`.
- Auto mode: `DL/knowledge/` with empty `code-map.md`, `selectors.md`, `calibration.md` (factor 1.0), `outcomes.jsonl` and `proposals/`, and `DL/runs/` with a `.gitignore` holding `*` and `!.gitignore`. Both loops write their auto-mode rows into their own ledger. A repo set up with 0.5–0.6 keeps its `ai-ledger.md` as history, and its config § AI loop becomes § Auto mode when the round said yes: the old queue line splits into one queue per loop, everything else moves as it is.
- `DL/lessons.md`: `# 90north-develop — project lessons` + one line on the entry format (`- [date] [dev|defect|ai|both] <tag> seen:N — symptom → cause → rule.`). Do not copy core lessons; the loops read them from the plugin.
- `tracker.env` holds no secrets and may be committed; the credentials file stays outside the repo. The ledgers are left untracked: the hand-over says the user may commit or ignore them.

## 7. Hand over
Tell the user in a few lines: anything `TBD` and the one step that settles it, first; what was found; each `default` taken, as one line with the config line that changes it; and the commands:
- which flow: `/90north-develop:workflow`
- a story, feature or change: `/90north-develop:n-develop-loop <KEY>` · the next ready one on a loop: `/loop 60m /90north-develop:n-develop-loop --next`
- defects: `/90north-develop:n-defect-loop` · on a loop: `/loop 30m /90north-develop:n-defect-loop`
- local board: add cards by copying `board/_template.md` to `board/<PREFIX>-<n>.md`; commit card changes after a run
- unattended: `/90north-develop:n-defect-loop --auto --dry-run` (or `n-develop-loop`) by hand first, then one schedule per loop from `W/templates/auto-scheduled-task.md`
