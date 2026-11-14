# Architecture profile: north-ai-skills

Verified at: `4269c3bef594` on 2026-11-14 by n-arch · Enforced by: `.ndev.toml` (numbers and globs live there, not here)
Shape: a skills repository (instruction files) with four small command-line programs, each functional core + thin shell · Intended = actual: yes for the four programs — see Known debt for `skills/design-atlas/scripts/`

## Map

- `skills/<name>/` → one skill each: `SKILL.md` (what an agent reads), `references/`, `templates/`, `scripts/`, `evals/`. The source of truth for every skill.
- `skills/n-dev/scripts/` → the structure check (`structure_check.py` + package `ndev_check/`) and the gate hook (`finish_gate.py` + `gate_session.py`).
- `skills/workflow/scripts/` → the tracker door: `tracker.sh` and `jira-*.sh` (shell), `local_board*.py` (cards as markdown files), `jira_*.py` and `md2adf.py` (Jira text and payloads); and `ledger.sh`, the one way a ledger row is written.
- `plugins/90north-develop/` → the plugin: manifest, `agents/`, `hooks/` (session-start line, command guard), `evals/`, and `skills/` as symlinks into `skills/`.
- `tools/` → this repo's own checkers: `check_repo.py` + package `repo_check/`, `validate_skill.py`, `quality.sh` (types and coverage), `consistency-review.md`.
- `.claude-plugin/marketplace.json` → what `/plugin marketplace add` reads.
- Outside the layering: every `*.md` (instructions, not code), `*.sh`, `skills/*/evals/**` and `plugins/*/evals/**` (fixtures an agent edits during a run), `skills/design-atlas/**` (a design skill with its own scripts), `research/`.

## Layers and dependency direction

| Layer | Holds | May import | Why this boundary | Violations at verified-at |
|---|---|---|---|---|
| check-core | the check's rules: classify, budgets, baseline, duplicates, functions, imports, layers, deps, testguard, literals, tomlsubset, model, report | nothing | a rule that reads no file and runs no process can be tested with plain values | 0 |
| check-io | `fileio`, `gitdiff`, `config`: read files, git and `.ndev.toml` | check-core | the only place a path the caller named is opened | 0 |
| check-app | `runner`, `structure_check.py`, `finish_gate.py`, `gate_session.py`: entry points | check-core, check-io | exit codes and output live here, so a rule never prints | 0 |
| board-core | card and Jira rules: `local_board_card/change/query/core`, `jira_read`, `jira_write` | nothing | card text and Jira payloads are data in, data out | 0 |
| board-app | `local_board.py`, `local_board_files`, `jira_fmt`, `md2adf`: files and command lines | board-core | one place writes a card file, atomically | 0 |
| tools-rules | `tools/repo_check/*` except the runner | nothing | each check is one module with one job | 0 |
| tools-app | `repo_check/runner`, `check_repo.py`, `validate_skill.py` | tools-rules | the command lines stay thin | 0 |
| guard-core | `guard_rules`, `guard_shell`: what is forbidden, and how a shell line is read | nothing | the rules are tested without a hook event | 0 |
| guard-app | `guard.py`: reads the hook event on stdin | guard-core | the hook stays a few lines | 0 |

Status of each rule: enforced on new code by `.ndev.toml`. Each was proven to fire on 2026-11-14 by planting a forbidden import in a scratch copy (fourteen forbidden imports found, five allowed ones passed).
No program imports another program's modules: the check, the tracker scripts, the tools and the guard share nothing but the standard library.
Also enforced by: `tools/quality.sh` (mypy `--strict` for Python 3.8, branch coverage with a floor) and `tools/check_repo.py` (versions, registered agents, plugin links, paths and `§` references).

## Extension recipes

| To add | Create | Wire in (the only edit to an existing file) | Example commit |
|---|---|---|---|
| a structure-check rule | `skills/n-dev/scripts/ndev_check/<rule>.py` (pure: files in, findings out) and `tests/test_<rule>.py` | one call in `ndev_check/runner.py`, one section in `ndev_check/report.py` | `b311168` (added `deps.py`) |
| a repo check | `tools/repo_check/<name>.py` and `tools/tests/test_<name>.py` | one line in `tools/repo_check/runner.py` | `4269c3bef594` |
| a tracker action | `skills/workflow/scripts/jira-<verb>.sh` and the matching `local_board.py` command | one case in `tracker.sh`, one row in `references/trackers.md` | `5a06e50` |
| a plugin agent | `plugins/90north-develop/agents/<name>.md` | its line in `plugin.json` `agents`, its rule set in `hooks/guard_rules.py` | `b311168` (risk-reviewer) |
| a skill | `skills/<name>/` with `SKILL.md` | a symlink under `plugins/90north-develop/skills/` when it belongs to the plugin, a row in both READMEs | `c269288` (n-arch) |
| an eval case | `skills/n-dev/evals/<NN>-<name>/` or `plugins/90north-develop/evals/<NN>-<name>/` | a row in that folder's `README.md` | `4269c3bef594` |

## State owners

| Kind of fact | Owner | Read through | Written through |
|---|---|---|---|
| a skill's rules | its `SKILL.md` and `references/` | other skills link to the section; they do not restate it | an edit there, then the consistency review |
| the ask-once rule | `skills/n-dev/SKILL.md` § Questions | the loops, through `skills/workflow/references/stages.md` § Decision round | n-dev only |
| which request goes to which skill | each skill's `description`, plus `plugins/90north-develop/hooks/session-start.txt` for a plain code request | the skill list an agent sees | those two places; `skills/workflow/SKILL.md` § Route the work sorts loop work only |
| budgets and layer rules | `.ndev.toml` | `structure_check.py` | the n-arch skill, with the user's yes |
| the plugin version | `plugins/90north-develop/.claude-plugin/plugin.json` | `.claude-plugin/marketplace.json` repeats it; `tools/check_repo.py` fails when they differ | both files in one commit |
| what a subagent may not run | `plugins/90north-develop/hooks/guard_rules.py` | `guard.py` | a rule set per agent, with a test |
| a project's loop settings | `<project>/.claude/90north-develop/config.md` and `tracker.env` | `_state.sh`, which parses them as text and never runs them | develop-init |
| a work item's state in a loop | `<project>/.claude/90north-develop/<flow>-ledger.md`, one row per change | the loop's S0 | `skills/workflow/scripts/ledger.sh` only |
| Jira credentials | a file outside every repo, named by the user's own environment | `_env.sh`, which reads it without exporting | `jira-login.sh` |

## Contracts

| Contract | Defined in | Consumers | Compatibility rule |
|---|---|---|---|
| `.ndev.toml` keys | `skills/n-dev/scripts/ndev_check/config.py`, template in `skills/n-arch/templates/ndev.toml` | every repo that runs the check | additive only; an unknown key is an error, so a removed key breaks old files |
| structure check output | `ndev_check/report.py` (`RESULT:` line, `--json`) and exit codes 0 / 1 / 2 | n-dev's step 5, the loops' verifier, eval graders | the `RESULT:` line and the exit codes do not change meaning |
| `tracker.sh <verb>` | `skills/workflow/scripts/tracker.sh`, `references/trackers.md` | both loops, on Jira and on the local board | a verb behaves the same on both backends |
| card file format | `local_board_card.py` | cards in users' repos | read old cards forever; write additive fields only |
| hook events | `plugins/90north-develop/hooks/hooks.json`, n-dev's frontmatter `hooks` | Claude Code | a hook that fails lets the session go on, except the guard's deliberate blocks |
| skill names and descriptions | each `SKILL.md` frontmatter | users' slash commands and schedules | a rename is a breaking change: bump the minor version and say so |

## Commands

| Purpose | Command |
|---|---|
| Types and coverage | `tools/quality.sh` (`--types` for mypy only) |
| One test file | `python3 -m unittest discover -s skills/n-dev/scripts/tests -p 'test_layers.py'` |
| Full suites | the four `python3 -m unittest discover …` lines in `README.md` § Check the repo |
| Repo consistency | `python3 tools/check_repo.py` |
| One skill | `python3 tools/validate_skill.py skills/<name>` |
| Plugin manifest | `claude plugin validate .` |
| Shell lint | `shellcheck skills/workflow/scripts/*.sh tools/quality.sh` |
| Structure check | `python3 skills/n-dev/scripts/structure_check.py --base main` (reads `.ndev.toml`) |
| Evals | `skills/n-dev/evals/README.md` and `plugins/90north-develop/evals/README.md` |

## Conventions and practice packs

- Python: standard library only, Python 3.8 syntax, `from __future__ import annotations`, every function typed and documented in one line (`skills/n-dev/scripts/ndev_check/layers.py`).
- A program fails closed on a setup error (exit 2 with the reason) and never guesses a path (`ndev_check/fileio.py`).
- Shell: `set -euo pipefail`, every argument validated before it reaches `curl` or `jq` (`skills/workflow/scripts/_env.sh`).
- Tests start the real program as a child process and assert on exit code and output (`plugins/90north-develop/hooks/tests/test_guard.py`); no test is skipped to pass.
- Skill text: plain words, one owner per rule, a gate names one concrete action (`skills/n-dev/evals/README.md` has the run that showed why).
- A description says what the skill is and when to use it, in a few hundred characters; how it works belongs in the body (`plugins/90north-develop/README.md` § Session-start line).

## Known debt and hot spots (audit on 2026-11-14)

| Kind | Count | Worst files |
|---|---|---|
| file-size | 2 | `skills/design-atlas/scripts/palette.py` (1002), `skills/design-atlas/scripts/shoot.mjs` (302) |
| function-size | 4 | `palette.py` `cmd_build` (128), `shoot.mjs` `probe` (79), `palette.py` `theme_tokens` (69), `read_raster_colors` (65) |
| line width | 3 files | `shoot.mjs`, `scrollfilm.mjs`, `palette.py` |
| layer | 0 | — |

All nine findings are in `skills/design-atlas/scripts/`, a design skill outside the development skills. They were there before this profile and do not fail a diff check; split `palette.py` by command when a task next touches it.

## Gaps and TBD

- The shell scripts (`*.sh`) are outside the layer rules: the check reads imports, and a shell script has none. `shellcheck` and the tests in `skills/workflow/scripts/tests/` cover them.
- The guard reads command text. It is a second lock behind the agents' instructions, not a sandbox.
- TBD — whether `skills/design-atlas/scripts/` gets its own layers — settled when that skill is next worked on.
