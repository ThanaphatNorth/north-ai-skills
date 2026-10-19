# defect-loop — project config

Written by `/90north-develop:defect-loop-init`, kept up to date by the loop. Facts only; every value here was checked, not guessed.
Lines marked `TBD` are asked of the user before the first sweep that needs them.

## Tracker
- Site: `https://<site>.atlassian.net` · project key `<KEY>` · board `<id>` (URL: <board url>)
- Access: <MCP connector id that works | REST only> — the REST scripts (tracker.env + credentials file) are the fallback and the only way to upload videos.
- Credentials file: `<~/.config/<project>-jira.env>` (JIRA_EMAIL, JIRA_TOKEN, chmod 600) — never print it.

## Board facts (ids, never names)
- Defect issue type: `<Bug>` (id <n>). Not defects: <Task (id), Story (id)>.
- Statuses: <To Do (id)>, <In Progress (id)>, <Blocked (id)>, <Code Review (id)>, <Ready for QA (id)>, Done-category: <FIXED/UAT/Done (ids)> — the loop never uses Done-category transitions.
- Open-defect query: `project = <KEY> AND issuetype = <id> AND status in (<ids>) ORDER BY priority DESC, created ASC` (board + backlog; no sprint filter).
- Sanity query: `project = <KEY> AND issuetype = <id> AND statusCategory != Done`.
- Transitions to the QA lane: <To Do →(id) In Progress →(id, screen: field …) Code Review →(id) Ready for QA>.
- Required fields on transitions: <e.g. Root Cause customfield_x = {id: parent, child: {id: child}}>.

## Comments
- Language: <match the ticket | Thai | English>. Reporter conventions: <test case ids, requirement ids>.

## Push policy
- Default: never push without the user's yes in chat, per branch.
- Standing approval: <none | date + the user's exact words + scope, e.g. "push fix/<KEY>-* and open PRs to develop; never force-push, merge, push to develop/main or delete branches">.
- PR: base `<develop>`, created with `<gh … | GH_TOKEN=$(gh auth token --user <account>) gh …>`.

## Repo
- Path: `<abs path to repo>` · remote `<owner/repo>` · base branch `origin/<develop>`.
- Worktree per ticket: `<abs parent>/<repo>-<key-lower>` on `fix/<KEY>-<slug>`; commit an empty anchor right after creating it.
- Dependency bootstrap in a new worktree: <e.g. `cp -Rc web/node_modules …` (APFS clone) / `npm ci` / `pnpm i --frozen-lockfile`>, plus <codegen, e.g. `npx prisma generate`>.

## Stack recipe (isolated, never the shared one)
- DB: <engine, container, port, user — never root in configs>; per ticket or per batch a fresh DB or a **copy** of the shared test DB (`<dump | restore command>`).
- Migrations: <command>. Seed / fixtures: <command>.
- API: <command, env flags — read the boot hooks first; every process on a DB must use the SAME flags>.
- Web: <command with API url and a free port, --strictPort>.
- Preview configs: `<abs path>/.claude/launch.json`, names `<project>-<key>-api|web`, commands use `exec`.
- Free ports to use: <range>. Taken: <list>.

## Accounts and login
- Login method: <password | email + OTP (dev code via env) | SSO>; how the e2e helper logs in: <helper + env overrides>.
- Roles and test accounts: <role → account> (test accounts only; create one per parallel agent if logins rate-limit).

## Checks (QA runs all; fixer runs the relevant ones)
- API: <typecheck>, <unit tests>, <lint — note if it runs --fix>, <domain suites that must show 0 skipped>.
- Web: <typecheck>, <unit tests>.
- e2e: <how to run one spec by file path>, browser: <bundled | channel: 'chrome' wrapper config>, output folder outside the repo: <yes/no + why>.
- Structure check: n-dev's `scripts/structure_check.py --base origin/<base>` (bundled); extra: <command | none>.

## Team (agents)
- Repro: `90north-develop:defect-repro` · Fixer: `90north-develop:defect-fixer`.
- Repo agents to use as role files (dispatch general-purpose with "Read <worktree>/<path> and follow it as your role"): code review `<path>`, QA `<path>`, verifier `<path>`, house rules for devs `<paths>` (+ any rule known to be stale).
- Development discipline: the bundled `n-dev` skill (always). Extra skills the fixer follows: <e.g. a TDD skill | none>.

## Spec and triage sources
- Spec / decision log: `<path>` (check "Revised by / Reversed by" before calling something a bug).
- Requirements docs / QA pack (may lag the spec): `<paths>`.
- Structural = <schema/migration, auth, figures users report on, API↔web contract, deploy/, >5 files or >200 lines> — repro + root cause + proposal, no build without a yes.

## Evidence
- Video: Playwright `video: on` for raw runs; viewer-friendly film via <repo skill, e.g. record-demo | plain hold script>; MP4 for Jira.
- Captions language: <Thai | English>.

## Project rules (things that will bite you here)
- <e.g. never cleanup in specs; teardown removes "ZZ E2E…" data; product language is Thai; thresholds come from config>
