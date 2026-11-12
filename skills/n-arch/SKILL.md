---
name: n-arch
description: Capture how a repository is built as rules people, agents and a checker can all use — architecture shape, layers and allowed import directions, extension recipes, state owners, contracts, commands and size budgets — in docs/architecture/profile.md plus a .ndev.toml the n-dev structure check enforces; refresh it when the code moves; audit the whole repo for structural debt and hot spots. Use when a repo has no architecture profile, when n-dev reports the profile missing or stale, when the user asks to map, document or audit the architecture or set layer/boundary rules, or when setting up n-dev or the 90north-develop loops in a repo.
---

# n-arch

One job: write down how *this* repository is built, once, so every later change starts from it instead of
rediscovering it. `n-dev` reads the profile in its Orient step; its structure check enforces `.ndev.toml` on every
change. Report in the user's language; write the files in the repo's language.

## What it writes

| File | Reader | Owns |
|---|---|---|
| `docs/architecture/profile.md` (or the repo's existing architecture docs folder) | people and agents | the shape, the *why* of each layer, extension recipes, state owners, contracts, commands, known debt, `verified-at` |
| `.ndev.toml` at the repo root | `n-dev/scripts/structure_check.py` | budgets, excludes, layer globs, import prefixes, allowed directions |

One owner per fact: numbers and globs live only in `.ndev.toml`; the profile gives the reasons and points to it.
Nothing else is written: no application code, no lint config, no CI. Start no servers and install nothing.

## Modes

| Mode | When | Run |
|---|---|---|
| **create** | no profile yet | steps 1–6 |
| **refresh** | n-dev found the profile stale, or the user asks | step 1 limited to what changed since `verified-at` (below), then 3–6 |
| **audit** | the user wants a debt map, or before a large refactor | step 3's audit and the hot-spot list only; writes nothing unless asked |

Refresh scope: `git diff --stat <verified-at>..HEAD -- <layer paths> <manifests> <boundary configs>` plus new top-level
folders (`git ls-tree -d --name-only HEAD`). Rows those paths touch are re-checked; the rest stay.

## Steps

1. **Collect evidence** (read only; for a large or multi-repo tree, fan the reading out to subagents and keep their
   conclusions):
   - Docs: README, CLAUDE.md / AGENTS.md, CONTRIBUTING, ADRs, any architecture or design folder.
   - Shape: `git ls-files | cut -d/ -f1-3 | sort | uniq -c | sort -rn | head -40`; manifests and workspace files.
   - Rules the repo already enforces: lint boundary rules (`import/no-restricted-paths`, `eslint-plugin-boundaries`,
     Nx tags), dependency-cruiser, import-linter, Deptrac, ArchUnit, `go vet` package rules. These win over anything you infer.
   - Extension recipes: three recent commits that added a feature (`git log --diff-filter=A --name-only --format='%h %s' -n 60`),
     each read as "new files + small edits = the recipe".
   - State owners, contract surfaces (OpenAPI, proto, event topics, shared tables, migration folders), commands.
   - Practice packs the repo already has (`*-practices` skills, house-rule docs): link them, do not copy them.
   *Done when* every fact you will write has a path, `path:line` or commit behind it.
2. **Classify.** Pick the archetype, or the combination, from `references/archetypes.md` by its signals. Record the
   **intended** shape (what docs and ADRs say) and the **actual** one (what imports and folders show); where they
   differ, keep both and carry the gap to step 5. *Done when* each top-level folder belongs to a layer or is named as
   outside the layering (scripts, tooling, generated).
3. **Measure before you prescribe.** Draft `.ndev.toml` from `templates/ndev.toml` in your scratch folder (not the
   repo yet) and audit the repo against it:
   ```bash
   python3 <n-dev-dir>/scripts/structure_check.py --repo <repo> --all --config <draft>.toml --json
   ```
   (`<n-dev-dir>` is the `n-dev` skill beside this one: `../n-dev` from this skill's base directory. Save the JSON
   in the scratch folder too.)
   - Prove each rule can fire before trusting a zero: in a scratch copy, plant one import that breaks it and see the
     `layer` finding (`references/archetypes.md` § Measuring a candidate rule). Aliases, packages and namespaces need
     an `imports` prefix, or nothing resolves to the layer.
   - Count `layer` findings per rule. Few: the rule describes the code. Many: the globs are wrong, or the rule is a
     **target** the code does not meet yet — keep it, and record its current violation count in the profile.
   - Budgets: keep the defaults unless the repo's lint config says otherwise or most files are over; then set the
     budget the team actually holds and write the reason in the profile.
   - Hot spots: churn × size. `git log --since=6.months --name-only --format= | sort | uniq -c | sort -rn | head -30`,
     crossed with the audit's over-budget files. These are where debt costs the most.
   *Done when* every layer rule has a violation count and every budget a reason.
4. **Write the drafts** from `templates/profile.md` and `templates/ndev.toml`. Every row carries its evidence; an
   unknown is `TBD — <what would settle it>`, never a guess. Keep the profile short (about 150 lines): link ADRs and
   docs rather than restating them.
5. **Confirm what only the user can decide** — one question each, at most four, with the evidence:
   - intended vs actual shape, where they differ;
   - each target rule: enforce it on new code now (the check judges added lines only, so old violations do not fail
     it) or keep it documented only;
   - a budget looser than the defaults.
   Everything else is settled by evidence; do not ask about it. *Done when* each open choice has an answer.
6. **Verify and hand over.** Run the structure check with the final file (`--all`, then once without `--all` to see it
   is quiet on the current branch) and the repo's own boundary tool if it has one. Set `verified-at` to `git rev-parse
   HEAD` and today's date. Report: archetype, the layer table, violation counts per rule, top hot spots, TBDs, and the
   files written. Commit only if the user asks, following the repo's conventions.

## Rules

- **Describe, then prescribe.** A rule nobody follows today is a target with a count, never a silent "should".
- **Shapes, not stacks.** Archetypes are structural; the stack facts come from the repo itself.
- **Evidence or TBD.** No row from memory or from what "projects like this usually do".
- **The repo's existing rules win.** If lint or a boundary tool already enforces layers, mirror it in `.ndev.toml`
  and say which one is authoritative.
- **Reads only**, plus the two files. Debt found is reported, not fixed: that is a task of its own.

## Works with

| Skill | How |
|---|---|
| `n-dev` | reads the profile in step 1; its structure check reads `.ndev.toml`; it suggests n-arch when the profile is missing |
| `develop-init` (90north-develop) | runs n-arch when a repo has no profile, before writing the loop config |
| `n-defect-loop`, `n-develop-loop` with `--auto` (90north-develop) | auto-mode triage locates code through the Map and Extension recipes and builds its forbidden areas from Contracts and State owners; without a current profile no card reaches its auto-merge class. It never writes the profile: its learner proposes `refresh` when a locate finds drift, and proposes enforcing a target rule that has reached 0 violations |
| `improve-codebase-architecture` | after an audit, finds deepening opportunities in the hot spots; n-arch only records rules and debt |
| `domain-modeling` | records the decisions from step 5 as ADRs, if the repo keeps them |

## Reference map

| Open | When |
|---|---|
| `references/archetypes.md` | step 2: signals, layers, extension points, state owners and contracts per architecture shape, with a `.ndev.toml` sketch |
| `templates/profile.md` | step 4 |
| `templates/ndev.toml` | steps 3–4; the format is a strict TOML subset (tables, strings, integers, booleans, arrays) |
