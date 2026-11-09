# Design note: architecture profile, AI guards and evals for n-dev

Size: Large  ·  Base ref: 9e9894a (`n-dev-split-existing-debt`)  ·  Date: 2026-11-09  ·  Branch: `n-dev-arch-profile`

## Goal and success criteria

n-dev fits each repo's own architecture without re-discovering it on every task, catches the two AI failure modes it
missed (weakened tests, invented dependencies), covers contract/migration/rollout risk on Large work, and has an eval
suite that shows whether a change to the skill helps.

| # | Criterion | Checked by |
|---|---|---|
| 1 | `structure_check.py` reads budgets, excludes and layers from `.ndev.toml`; CLI flags win over the file | `tests/test_config.py`, `test_cli.py::test_config_*` |
| 2 | The config parses on Python 3.8–3.10 (no `tomllib`) and gives the same result as `tomllib` where present | `tests/test_tomlsubset.py` (compares when `tomllib` imports) |
| 3 | An added import that breaks a declared layer rule is a `layer` finding; relative and prefix imports both resolve | `tests/test_layers.py`, `test_cli.py::test_layer_*` |
| 4 | Removed assertions in a pre-existing test, added skip/focus markers, a deleted test file, a rewritten snapshot, a lowered coverage threshold are `test-weakened` findings | `tests/test_testguard.py`, `test_cli.py::test_test_weakened_*` |
| 5 | A dependency added to a manifest is a `new-dependency` finding, naming the package | `tests/test_deps.py`, `test_cli.py::test_new_dependency_*` |
| 6 | `--all` audits the whole repo (debt map) and skips change-only checks | `test_cli.py::test_audit_*` |
| 7 | The existing 45 tests stay green | `python3 -m unittest discover -s skills/n-dev/scripts/tests` |
| 8 | n-arch exists, passes the validator, ships in the plugin, and develop-init points to it | `tools/validate_skill.py skills/n-arch --urls`; `ls -la plugins/90north-develop/skills` |
| 9 | n-dev reads the profile in Orient, has a test-integrity rule, a verify-from-source rule, change-safety for Large, fresh-context review | validator + reading the diff |
| 10 | An eval suite runs under `claude plugin eval` and a smoke run completes | the smoke run's result file |

Assumptions:
- ASSUMPTION: the config lives at the repo root as `.ndev.toml` (the profile names it; `--config` overrides).
- ASSUMPTION: the human-readable profile lives at `docs/architecture/profile.md` unless the repo already has an architecture docs folder.
- ASSUMPTION: n-dev never writes the profile itself (that is a side effect beyond the task); it reads it, and suggests n-arch when it is missing.

## Orient facts

- Commands: tests `python3 -m unittest discover -s skills/n-dev/scripts/tests -p 'test_*.py'` · validator `python3 tools/validate_skill.py skills/<name> --urls` · no lint/typecheck configured; system `python3` is 3.9 (no `tomllib`).
- Extension points used: `runner.run` is the composition root of the check; `report._TITLES` maps kinds to sections; `gitdiff` is the only module that talks to git; plugin skills are symlinks in `plugins/90north-develop/skills/`.
- State owners in use: `Budgets` (built only by the CLI); git (owner of "what changed"); `plugin.json` + `marketplace.json` (plugin version — two copies today, kept equal by hand).
- Reuse inventory: `classify` (path kinds, noise), `gitdiff.text_at` (base text), `Finding` model, `baseline.split` (debt split), test helpers in `test_cli.py` (throwaway repo). Neighbour skills: `codebase-design`, `improve-codebase-architecture` (finds deepening opportunities — n-arch records rules, it does not search for refactors), `domain-modeling` (ADRs, glossary), `inv-nfr` (full non-functional pass).

## Module map

| New file | Responsibility | Interface | Layer | Depends on |
|---|---|---|---|---|
| `ndev_check/tomlsubset.py` | Parses the TOML subset the config uses when `tomllib` is missing | `loads(text) -> dict`, `TomlError` | core | — |
| `ndev_check/config.py` | Turns a config dict into budgets, excludes and layer rules | `load(root, path) -> Config`, `from_dict(d) -> Config` | core + one read | `tomlsubset`, `model` |
| `ndev_check/imports.py` | Finds import specifiers and their line numbers in source text | `find_imports(path, text) -> [(line, spec)]` | core | `classify` |
| `ndev_check/layers.py` | Judges added imports against declared layer rules | `check_layers(files, layers) -> [Finding]` | core | `imports`, `model` |
| `ndev_check/testguard.py` | Finds changes that weaken tests | `check_tests(changes, deleted) -> [Finding]` | core | `classify`, `model` |
| `ndev_check/deps.py` | Finds dependencies a manifest gained | `new_dependencies(path, before, after) -> [str]`, `check_deps(...)` | core | `model` |
| `skills/n-dev/references/change-safety.md` | Contracts, migrations, rollout, failure modes, observability for Large work | reference | doc | — |
| `skills/n-arch/` | Captures a repo's architecture as a profile + `.ndev.toml`; audits debt; refreshes | skill | skill | n-dev's script |
| `skills/n-dev/evals/` | Fixed tasks graded with and without the skill | `claude plugin eval skills/n-dev` | eval | fixtures |

Dependency direction: `structure_check` (shell) → `runner` (wiring) → checks (pure) → `model`; only `gitdiff` and `config.load` read the outside world. No cycle.

## State ownership

| Fact | Owner | Writer | Readers | Derived | Copies + invalidation |
|---|---|---|---|---|---|
| Repo's budgets, excludes, layers | `.ndev.toml` in the repo | n-arch (or the human) | `config.load` | effective `Budgets` = defaults ← file ← CLI | none |
| Repo's architecture narrative | `docs/architecture/profile.md` | n-arch | n-dev Orient, dev-loop | — | the profile records `verified-at <sha>`; stale when key paths changed since |
| Plugin version | `plugin.json` | release edit | marketplace | — | `marketplace.json` copy, bumped in the same commit |
| Removed lines of a diff | git | — | `gitdiff.changed_files` → `ChangedFile.removed` | — | none |

## Extension plan (pre-existing files)

| File | Change | Kind | Reason |
|---|---|---|---|
| `scripts/structure_check.py` | `--config`, `--no-config`, `--all`; flags default to None so the file can fill them | in-place | the CLI is the only place that builds `Budgets` (its documented owner) |
| `ndev_check/model.py` | `ChangedFile.removed` (base line, text) with an empty default | in-place | the value type every check shares |
| `ndev_check/gitdiff.py` | parse removed lines from the `-U0` diff; `deleted_paths()` | in-place | the only module that talks to git owns every git fact |
| `ndev_check/runner.py` | call the three new checks; skip `new-dependency` in audit | wiring | composition root |
| `ndev_check/report.py` | three titles; header names the config | wiring | kind → section map |
| `ndev_check/classify.py` | `matches_any(path, globs)` so test-guard sees snapshots the noise list hides | in-place | one owner of path rules |
| `skills/n-dev/SKILL.md`, `templates/design-note.md`, `references/structure.md` | profile in Orient, verify-from-source, test integrity, change safety, fresh review, progress | in-place | the skill's own text |
| `skills/develop-init/SKILL.md` | step 2 points to n-arch when no profile exists | wiring | |
| `plugins/90north-develop/{skills/n-arch, .claude-plugin/plugin.json}`, `.claude-plugin/marketplace.json`, READMEs | symlink, version 0.4.0, rows | wiring | |

## Test seams

- Pure modules tested directly with strings (`tomlsubset`, `config.from_dict`, `imports`, `layers`, `testguard`, `deps`).
- End to end through the real CLI in a throwaway repo (`test_cli.py` helpers), one case per new finding kind and for audit and config precedence.
- Eval suite: whole-skill behaviour, with/without arms.

## Rejected

- Per-stack reference files: the user chose stack-agnostic content (2026-10-16); project fit comes from the repo's own profile.
- JSON config: no comments, and the profile wants a reason beside each budget. INI: unfamiliar for layer tables.
- n-dev writing the profile: a side effect beyond the task; n-arch asks first.

## Progress

- [x] Config + TOML subset parser, layer rules, `--all` audit — tests red first, green on Python 3.9 and 3.13
- [x] Layer target choice: most specific glob / longest prefix (bug found while writing archetypes; two tests red first)
- [x] `test-weakened` (string-literal blanking added after the dogfood run flagged test data) and `new-dependency`
- [x] n-dev SKILL.md, template, structure.md checklist, `references/change-safety.md`
- [x] n-arch skill (SKILL, archetypes reference, profile + ndev.toml templates), plugin 0.4.0 wiring, READMEs, workflow, develop-init
- [x] Eval suite: six cases; schema read from the CLI (no exit-code grader, so acceptance specs ship as files and are graded unchanged)
- [x] Eval smoke runs, all six cases, Sonnet, one run per arm (~$1.3 in all): the harness works; results in
      `skills/n-dev/evals/README.md` § First runs. Two runner facts found: macOS `/usr/bin/git` fails inside the
      sandbox (put Homebrew git first), and `execution.env` takes only `EVAL_*` keys.
- [x] Fresh-context review (16 findings): code fixes test-first — deleted coverage gates, anchored coverage keys,
      narrower assertion pattern, `expectedFailure` / `skipIf`, pyproject extras, case-folded namespace paths,
      `from pkg import mod`, base-ref imports are debt, renames are not deletions, audit skips the test guard,
      `--config` relative to cwd, stricter TOML strings/comments; docs: prove a layer rule fires before trusting a zero,
      namespace prefixes in the layered sketch, eval command in SKILL.md; graders: profile actually read, TAP output,
      handler-wide storage check, `expectedFailure`, 06 judged answer and `input_match`.

Dogfood structure check on this change: wiring in `gitdiff.py`, `runner.py`, `structure_check.py` (in-place reasons above);
`test_tomlsubset.py` `skipTest` is environment-conditional (tomllib needs 3.11+).
