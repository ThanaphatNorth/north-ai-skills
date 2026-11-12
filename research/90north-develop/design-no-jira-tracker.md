# Design note — the loops without Jira (90north-develop 0.6.0)

Status: **approved 2026-11-12**. Decisions: backend **local files**, board **committed to git**, design **A**
(tracker seam). The other backends (GitHub Issues) stay out of this change.

Consequences of the decisions:
- **Who commits the board.** A committed board means every loop pass leaves card edits uncommitted in the main
  checkout. The loop never commits them, the same rule as `knowledge/`. The pass report lists the changed card
  files, and a person commits them.
- **Worktrees.** Each worktree carries its own copy of the board. `_state.sh` therefore maps a state folder found
  inside a linked worktree to the same path in the main checkout (when that path has `tracker.env`), so every
  read and write hits one board.

## Request

Repos with no Jira still get the loops: `n-loop` on a schedule or `/loop`, `dev-loop --next`, the `defect-loop`
sweep. Every code change still goes through n-dev.

Today:
- `dev-loop <spec | request>` already runs one untracked item (`LOCAL-<slug>`, tracker steps skipped). But
  `--next` and `/loop` need config's ready query, which is JQL.
- `defect-loop` and `n-loop` are Jira-only.
- The loops reach the tracker through 8 verbs, each a `jira-*.sh` script: `search`, `get`, `card`, `edit`,
  `transition`, `comment`, `attach` and `download`. The docs name those scripts about 50 times.

n-dev is unchanged and already in every loop, as files rather than a `/n-dev` call:
- The orchestrator or conductor runs n-dev steps 1–3 and 6–7 itself.
- Each `dev-builder` or `defect-fixer` brief carries n-dev's absolute path. The agent reads `SKILL.md` and its
  references, then runs steps 4–5 with the red gate.

## Success criteria (each one a check)

1. When tracker.env says `TRACKER=local`, all 8 verbs work on a temp board with no Jira credentials.
   - Check: unit tests per verb.
   - Check: one end-to-end script test walks a card through queued → locked → verdict label → in-progress →
     review lane → comment with a video link → unlocked.
2. When tracker.env has no `TRACKER` line, everything behaves as before (Jira).
   - Check: `tracker.sh <verb> …` hands the same arguments to `jira-<verb>.sh` (a fake-backend test).
   - Check: the 18 existing script tests stay green.
3. No loop doc calls `jira-*.sh` directly.
   - Check: `grep` finds no match outside `workflow/scripts/` and the Jira row of the backend table.
4. Every builder or fixer brief still passes n-dev's absolute path.
   - Check: `grep` in dev-loop, defect-loop, n-loop and stages.
5. The usual checks pass:
   - `validate_skill.py` reports 0 errors on all 8 skills;
   - `claude plugin validate` passes;
   - `shellcheck -x` is clean;
   - the n-dev tests (135) stay green.

## Two designs

| | **A. Tracker seam** (recommended) | **B. Local board as a fake Jira site** |
|---|---|---|
| Shape | `W/scripts/tracker.sh <verb> …` picks a backend from `TRACKER` in tracker.env. The `jira-*.sh` scripts stay exactly as they are, as the Jira backend. A new `local_board.py` is the local backend. | `JIRA_SITE=file:<dir>`, and each `jira-*.sh` branches to a local emulator. |
| Depth | Small interface (8 verbs) that hides which tracker is behind it. | The emulator must accept a JQL subset, transition ids, `customfield_*` ids and ADF: a large surface that does little. |
| Locality | A new tracker means one new backend file plus one case in `tracker.sh`. | Every script carries a local branch. |
| Seam for tests | Verb level, with a fake backend. | HTTP-shaped emulation. |
| Docs churn | About 50 mechanical renames (`jira-get.sh KEY` → `tracker.sh get KEY`). | None, but every script name would say "jira" for something that is not Jira. |
| A third tracker later (GitHub Issues) | One more backend. | Does not fit. |

**A** wins on depth, locality and the seam. The cost is a mechanical rename, done with one script.

## Local board (backend `local`)

- **Where.** `DL/board/` by default; `LOCAL_BOARD=<path>` in tracker.env can move it (absolute, or relative to
  `DL`). Committed to git (decided above).
- **One card per file,** `<PREFIX>-<n>.md`. The prefix is a convention config § Tracker records; no script needs
  it, because there is no `new` verb.
  - Header lines: `type:`, `status:`, `labels:`, `priority:`, `rank:`, `created:`, `updated:`, `links:`, plus
    any named field (`severity:`, `environment:` …).
  - Body: `## Description`, `## Acceptance criteria`, `## Steps`, `## Expected`.
  - Then `## Comments`, with entries `### c<n> · <date time> · <author>`. The loop writes as `90north-develop` and
    replaces only its own entries; a person answers with a new entry (the card template says how).
  - Template: `workflow/templates/card.md`. People add cards by copying it.
- **Statuses** live in `LOCAL_STATUSES` in tracker.env, because the script reads them there. The default is
  `todo,in-progress,need-info,review,ready-for-qa,reopened,done` (`reopened` so the follow-up after a failed AI
  fix has a status to find). config § Board facts names the lanes and marks the
  Done-category statuses never-use, as today. `tracker.sh transition KEY <status>` accepts a listed status only;
  `--list` prints them.
- **Query** is a small grammar, tested as a pure function:
  - Example: `status=todo,ready labels=ai-queue -labels=ai-processing type=bug,story age>2h sort=rank`.
  - `field=a,b` matches any of the values; `-field=…` matches none of them.
  - `age>2h` / `age<30m` compare against `updated` (units `m`, `h`, `d`).
  - `sort=<field>` or `sort=-<field>`; the default order is rank, then key.
  - config.md holds each query in its backend's form, the same as JQL today.
- **The n-loop lock** keeps the same labels. A lock is stale when its card matches
  `labels=ai-processing age>2h`.
- **Evidence.**
  - `attach` copies the file into `DL/board/<KEY>/` and prints its relative path.
  - In a comment, `::video <path>` becomes a link to that path.
  - `comment` appends a new entry, or replaces entry `c<n>` when given its id, then reads the card back as
    `jira-comment.sh` does.

## Module map

| File | New / changed | Responsibility (one sentence) |
|---|---|---|
| `workflow/scripts/_state.sh` | new | Finds the state folder (DL) and reads tracker.env: the one owner of "where DL is". |
| `workflow/scripts/_env.sh` | changed (move) | Sources `_state.sh` instead of its own walk up; keeps the Jira credential loading. |
| `workflow/scripts/tracker.sh` | new | Maps a verb to the backend `TRACKER` names. |
| `workflow/scripts/local_board_core.py` | new | The pure core: parse and render a card, parse and match a query, apply an edit or a transition, add or replace a comment. |
| `workflow/scripts/local_board.py` | new | The file shell and CLI for the 8 verbs: finds the board, reads the clock and the files, writes atomically. |
| `workflow/scripts/tests/test_local_board_core.py`, `test_tracker.py` | new | The success criteria above. |
| `workflow/templates/card.md` | new | Local card template. |
| `workflow/references/trackers.md` | new | The verbs, the backends, the query form per backend, the local board format. |
| Loop docs: workflow `SKILL.md`, `stages.md`, `core-lessons.md`; dev-loop and defect-loop `SKILL.md`; n-loop `SKILL.md`, its references and `comments.md`; develop-init `SKILL.md` and its config and tracker.env templates | wiring | Script names → verbs. develop-init gains a "no Jira" branch: board folder, statuses, local queries. |
| `README.md`, plugin `README.md`, `plugin.json`, `marketplace.json` | wiring | 0.6.0 and one line on tracker choice. |

The comment templates keep their names (`templates/jira-comment.md`). A rename would only add churn.

## State ownership

| Fact | Owner | Others read it through |
|---|---|---|
| Which tracker | `TRACKER` in tracker.env (absent = `jira`) | `_state.sh` |
| Where DL is | `_state.sh` | `_env.sh`, `tracker.sh`, and `local_board.py` (via `DEVELOP_DIR`) |
| A local card's status, labels and fields | its card file | `tracker.sh get`, `tracker.sh card` |
| Queries, lanes, statuses | `config.md` (as today) | the loops |

## Change safety

- **Compatibility.** A tracker.env without `TRACKER` keeps today's behaviour. The `jira-*.sh` scripts are
  unchanged and still callable. Version bump 0.5.0 → 0.6.0. No data migration. Two changes reach Jira repos too,
  neither of which alters a request: the state-folder path is resolved (symlinks) and a linked worktree's folder
  maps to the main checkout's; `TRACKER` and the `LOCAL_*` settings come from tracker.env only, never the shell.
- **Failure modes.** An unknown `TRACKER` or verb exits 2 with the list of valid values. A local write goes to a
  fresh temp file in the board folder, keeps the card's mode, then renames it, so a crash never leaves a
  half-written card. An edit that would not read back the same card is refused before anything is written. An
  unreadable card is skipped by `search` with a warning, so one bad file never stops a queue.

## Not in this change

- A GitHub Issues backend, unless the user picks it below. With it:
  - status would be a `status:<x>` label;
  - `gh` cannot upload attachments to an issue, so the evidence would go in the PR or the repo.
- A `tracker.sh new` verb. Cards are added by copying the template.

## Progress

- [x] User decision: backend, board location, design A (2026-11-12)
- [x] Baseline: the 18 script tests green before any edit
- [x] `_state.sh` split, pinned by the 18 existing tests
- [x] `local_board_core.py`, red (10 failures, 5 errors) → green
- [x] `tracker.sh` + `local_board.py`, red (13 failures, 1 error) → green
- [x] Doc wiring (one rename script), develop-init no-Jira branch, templates
- [x] Fresh review (standards + spec): 12 findings fixed, red (4 failures, 11 errors) → green; 58 script tests
- [ ] Final checks and a local commit
