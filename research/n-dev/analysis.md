# n-dev: source analysis and design decisions

Provenance for `skills/n-dev/`. Not loaded by the skill. Written 2026-10-16.

## Inputs

| Source | What it contributes | What it lacks |
|---|---|---|
| `karpathy-guidelines` (andrej-karpathy-skills plugin 1.0.0) | Think before coding; simplicity first; surgical changes; goal-driven execution with verifiable criteria | No structure guidance; its "no abstractions for single-use code" pushes toward the one-long-file outcome the user wants to avoid |
| `/implement` (`~/.agents/skills/implement`) | TDD at pre-agreed seams; typecheck and single test files often; full suite once; `/code-review`; commit | Five lines: no design step, no structure, no state, no completion criteria |
| User requirements (2026-10-16) | 1 quality and structure over the easiest path, functional and modular, reusable, no large single files; 2 extension files instead of editing existing files; 3 state with a single source of truth; 4 research what else to add | — |
| Neighbouring skills | `codebase-design` (deep modules, seams, design it twice), `tdd`, `code-review`, `writing-great-skills` (leading words, completion criteria, single source of truth for skill text) | — |

## Conflicts and how they were resolved

1. **Simplicity first vs "never the easiest way".** Resolved with Hickey's *simple vs easy*: easy (near at hand: one file, copy-paste) is ruled out; simple (unentangled: one responsibility per module) is required. Karpathy's *scope* discipline is kept whole — no speculative features, options or config. Effort goes into shape, not scope.
2. **Over-modularisation risk.** A rule that says "as modular and reusable as possible" invites pass-through wrappers and wrong abstractions. Guards: deletion test and deep modules (Ousterhout, `codebase-design`), extract on evidence (second real caller or a named domain concept), Metz's "wrong abstraction" for inlining back.
3. **Extension files vs surgical changes.** Compatible once the extension rule is stated as a *wiring diff* budget on pre-existing files (open–closed). Exceptions where in-place is right: bugs, a rule that changed for everyone, a fork that would copy most of the original, preparatory refactors to create a missing seam. Monkey-patching and shadow files are named anti-patterns.
4. **Stack-specific vs stack-agnostic.** The user asked whether the skill should avoid binding to a stack. Decision: the core is agnostic; Orient discovers the repo's own extension points and state owners (its git history is the recipe); one translation table gives cross-ecosystem examples. No per-stack reference files.
5. **Autonomy vs approval.** User choice: write the design note and continue; stop only for a material trade-off or a change to state shape, DB schema or a public interface.

## Evidence notes

- **Duplication with AI assistants.** GitClear 2025 report (211M changed lines, 2020–2024): page headline "4x growth in code clones"; 2024 the first year copy/paste exceeded moved lines. Secondary write-ups (DevClass, LeadDev) quote an eightfold rise in duplicated 5+-line blocks — the two figures differ by metric, so the skill cites the headline. GitClear 2026 "Maintainability Gap" (623M changes, 2023–2026): cross-file function calls down 35 %, refactoring moves down 70 % vs 2022. Pages return 403 to scripts; figures taken from search-indexed titles and summaries on 2026-10-16. Vendor data, non-random sample: direction, not precision. https://www.gitclear.com/ai_assistant_code_quality_2025_research · https://www.gitclear.com/the_ai_code_quality_maintainability_gap
- **File size and agents.** No study found that isolates file length as a cause of agent errors (searches 2026-10-16: repository-level benchmarks such as LoCoBench-Agent study context strategies, not file length). Budgets are therefore labelled heuristics, justified by review size (Google small CLs) and locality, and overridable per repo.
- **Skill authoring.** Anthropic's skill best practices: keep `SKILL.md` under 500 lines, disclose detail into linked files. https://platform.claude.com/docs/agents-and-tools/agent-skills/best-practices

## Additions beyond the two source skills (user item 4)

| Addition | Why |
|---|---|
| Scope dial (Tiny / Standard / Large) | Keeps the process from becoming ceremony on one-line fixes |
| Orient's four facts, incl. reuse inventory | Counters the duplication trend; makes extension and state rules concrete per repo |
| Design note template (module map, state ownership, extension plan, test seams) | Turns rules 1–3 into checkable artefacts with completion criteria |
| Functional core, imperative shell | The most direct route to modules that are both functional and testable |
| Make impossible states impossible; parse, don't validate | Structural state design beyond "one owner" |
| Characterization tests and preparatory refactor | Safe path when the seam an extension needs does not exist yet |
| `scripts/structure_check.py` | Rules 1–2 become an observable gate: wiring budget, file and function budgets, copied blocks |
| Precedence section | `karpathy-guidelines` and `inv-code-craft` also auto-load; their simplicity rule needs an explicit tie-break |

## Validation log

- Script unit + end-to-end tests: `python3 -m unittest discover -s skills/n-dev/scripts/tests -p 'test_*.py'`.
- Real-repo dry runs (read-only, `--base HEAD~10`) on two local projects found three false-positive patterns, each fixed test-first: tests appended to an existing test file counted as wiring; moving code out of a file counted as wiring; multi-line `import { … }` blocks matched as duplicates. Remaining findings spot-checked as genuine (e.g. a crop-mark drawing loop copied between two print scripts).
- With/without eval (2026-10-16, one run per arm, Sonnet subagents, same coupon task on a toy Python shop repo — n=1, indicative only):

  | | without skill | with n-dev |
  |---|---|---|
  | Pre-existing `orders.py` | +30 lines (coupon field on `Order`, discount + apply logic inside) | untouched |
  | Pre-existing `app.py` | +15 lines | +8 / -2: wiring + one in-place edit with a recorded reason (total rule changed for every handler) |
  | Applied-coupon owner | `Order.coupon` field (state shape changed) | `coupon_service.APPLIED`, documented as the only record |
  | Total | derived | derived |
  | Core / shell split | rules + seeds in one module | pure `coupons.py` + `coupon_service.py` shell, clock and catalog injected |
  | Scope extras | case-insensitive codes, status check, constructor validation | none (listed as kept out) |
  | Tests | 27 pass, red not shown | 20 pass, red shown (but as `ModuleNotFoundError`) |
  | Structure check | 1 finding (wiring) | clean |

  Change made from it: step 4 now requires red for the right reason (an assertion, not an import error).
