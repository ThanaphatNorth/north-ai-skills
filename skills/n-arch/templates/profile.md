# Architecture profile: <repo name>

Verified at: `<git rev-parse HEAD>` on <YYYY-MM-DD> by n-arch · Enforced by: `.ndev.toml` (numbers and globs live there, not here)
Shape: <archetype(s) from n-arch references/archetypes.md> · Intended = actual: <yes | no — see Gaps>

## Map

<5–10 lines. Each top-level folder or package: path → one sentence on what it holds. Name the folders that sit
outside the layering (scripts, tooling, generated code) as such.>

## Layers and dependency direction

| Layer | Holds | May import | Why this boundary | Violations at verified-at |
|---|---|---|---|---|
| <domain> | <business rules, pure> | nothing | <rules must not depend on delivery or storage> | <0> |
| <application> | <use cases> | domain | <...> | <n> |

Status of each rule: enforced on new code by `.ndev.toml` | target (documented only) — <decided by the user on date>.
Also enforced by: <eslint boundaries / dependency-cruiser / import-linter / ArchUnit — which is authoritative> | nothing else.

## Extension recipes

How this repo adds things, taken from its own history. A new feature follows the recipe; editing a central file
beyond the wiring line is an exception that needs a reason (n-dev `references/extension.md`).

| To add | Create | Wire in (the only edit to an existing file) | Example commit |
|---|---|---|---|
| <an endpoint> | <files> | <route table / module registration> | `<sha> <subject>` |
| <a screen> | <...> | <...> | `<sha>` |
| <a job / consumer> | <...> | <...> | `<sha>` |

## State owners

| Kind of fact | Owner | Read through | Written through |
|---|---|---|---|
| <server data on the client> | <query cache> | <hooks in ...> | <mutations in ...> |
| <configuration> | <config module path> | <...> | <env at start-up> |

## Contracts

What other processes depend on. Changes follow n-dev `references/change-safety.md`.

| Contract | Defined in | Consumers | Compatibility rule |
|---|---|---|---|
| <public HTTP API> | <openapi.yaml / controllers> | <web app, partner X> | <additive only; versions under /v2> |
| <events> | <topic names, schemas> | <services> | <...> |
| <shared tables> | <migrations folder> | <...> | <expand and contract> |

## Commands

| Purpose | Command |
|---|---|
| Typecheck | <...> |
| One test file | <...> |
| Full suite | <...> |
| Lint | <...> |
| E2E | <...> |
| Structure check | `python3 <n-dev>/scripts/structure_check.py` (reads `.ndev.toml`) |

## Conventions and practice packs

- <house rules, naming, error style, logging — one line each, with the file that shows it>
- <`*-practices` skill or docs folder the team keeps; ADR index>

## Known debt and hot spots (audit on <YYYY-MM-DD>)

| Kind | Count | Worst files |
|---|---|---|
| file-size | <n> | <path (lines)> |
| function-size | <n> | <...> |
| layer | <n> | <...> |

Hot spots (changed most in 6 months and over budget): <path — commits — lines>. Pay these first, when a task
touches them; refactoring them is a task of its own.

## Gaps and TBD

- <intended vs actual, with the evidence for each>
- TBD — <fact> — <what would settle it>
