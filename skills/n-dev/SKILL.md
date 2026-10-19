---
name: n-dev
description: Structured development discipline — design before code, modular and functional modules, reuse before writing, new behaviour in extension files beside existing code, state with one owner (single source of truth), test-first, verified. Use when implementing a feature, spec or ticket; building or adding to a module, API, screen or job; refactoring; or fixing a bug that needs more than a one-line change.
---

# n-dev

How to build software that stays easy to change: think first, design the structure, build test-first at the seams, verify with evidence. It merges the Karpathy guidelines (think before coding, no speculative scope, surgical changes, goal-driven execution) with the `/implement` loop (TDD at seams, typecheck often, full suite at the end, review, commit) and adds three structural rules. Report in the user's language; keep code, identifiers and commit messages in the repo's language.

## The four rules

1. **Simple, not easy.** *Simple* means each module does one thing and is not entangled with the others. *Easy* means whatever is nearest: one long file, a copy of a similar block, everything inline. Choose simple even when easy is shorter.
   - Split by responsibility into small modules with a small interface (a **deep module**), with a **functional core**: pure functions that decide and transform, and a thin shell that does the I/O and passes dependencies in.
   - **Reuse before you write.** Search for an existing function, hook, service or library before adding one; extend what exists.
   - Extract a shared module when a second real caller exists or the code names a domain concept; a module that only forwards calls fails the deletion test and is merged back.
   - Structure is where effort goes; **scope** stays exactly what was asked — no extra feature, option, flag or config.
2. **Extend beside, not inside.** New behaviour lives in new files. A file that existed before the task receives only a **wiring diff**: the import plus the line that registers, composes or delegates to the new module. Edit in place only for a bug in that code, or when extending would copy most of it; then every changed line traces to the request. Details and the decision table: `references/extension.md`.
3. **One owner per fact.** Every piece of state (UI, server data, URL, form, cache, config, database row) has exactly one owner. Others read it through a selector or query, write it through one module, and compute derived values instead of storing them. A copy exists only as a cache with a named invalidation rule. Details: `references/state.md`.
4. **Verified, not claimed.** Each success criterion becomes a check — a test seen red then green, a command, an observable result. Work is done when the checks pass in this session, and the report shows the evidence.

## Scope dial

Pick the size first; it decides how much of the process runs.

| Size | Looks like | Run |
|---|---|---|
| **Tiny** | typo, config value, one-line fix | Steps 1, 4–5, 7. Rules 2–3 still hold. |
| **Standard** | a feature, endpoint, screen, job, or a bug touching more than one file | Every step; the design note goes in chat, short. |
| **Large** | a new module or package, a change to state shape, DB schema or a public interface, several repos | Every step; the design note is saved as a file beside the work (the repo's docs folder, else the scratchpad), and the interface is designed twice. |

## Steps

1. **Orient.** Read the repo's agent and contributor docs (CLAUDE.md, AGENTS.md, CONTRIBUTING), lint and formatter config, and how the most recent similar feature was added (`git log` on a sibling feature, then read that commit's diff — it is the repo's own recipe). Record four facts:
   - **Commands** for typecheck, one test file, the full suite, and lint.
   - **Extension points**: how this codebase adds a route, handler, screen, command or listener without editing a central file (`references/extension.md` § Finding the repo's extension points).
   - **State owners** already in use: server cache, store, URL, forms, database, config module.
   - **Reuse inventory**: existing code the task can use, found by searching the task's verbs and nouns; "none found" is a valid answer when the search terms are listed.
   *Done when* all four facts are written down.
2. **Think.** State assumptions; when the request reads two ways, show both and pick only when the context settles it. Turn the goal into success criteria, each one a test, a command or an observable result. *Done when* every criterion can be checked by something other than opinion.
3. **Design note.** Fill `templates/design-note.md`: module map, state ownership table, extension plan, test seams. For Large work, design the interface two radically different ways and compare them on depth, locality and seam placement (the `codebase-design` skill, if installed, has the method). Then continue without waiting, except in two cases, where you show the note and stop for the user's decision:
   - two designs trade off in a way the user would care about;
   - the change alters state shape, a DB schema, or a public interface.
   *Done when* every new file has a one-sentence responsibility, every fact has exactly one owner, and every pre-existing file in the plan has a reason.
4. **Build test-first, inside out.** Before extending existing behaviour, pin it with a characterization test. Then for each module, core first: write the test at its interface and see it fail (**red**) for the right reason — an assertion about the missing behaviour, not an import or syntax error (add a stub first if needed) — then implement until it passes (**green**), and tidy. Order: pure core, then adapters, then the wiring diff last. Run typecheck and that test file after each module. Use the `tdd` skill if installed. *Done when* every success criterion has a test that was seen red and then green.
5. **Verify.** Run the full suite, lint, typecheck, and the structure check:
   ```bash
   python3 <skill-dir>/scripts/structure_check.py --base <base-ref>
   ```
   It reports pre-existing files that changed beyond a wiring diff, files and functions over budget, and blocks copied from code that already exists. Set the budgets to the repo's norms (`--help` lists the flags). *Done when* everything is green, and each structure finding is fixed or carries a one-line reason in the report.
6. **Review.** Run the `code-review` skill if installed; otherwise review the diff against the checklist in `references/structure.md`, reading every changed line of a pre-existing file. Fix the findings and re-run step 5. *Done when* no finding is open.
7. **Commit and report.** Commit on a feature branch (create one if on the default branch), following the repo's commit convention and the user's rules on commit messages; stage only files this task changed. Push only when the user asks. Report: what was built, the checks and their results, the structure-check result, each pre-existing file touched and why, and anything left unverified.

## When skills disagree

- **karpathy-guidelines / inv-code-craft:** keep their think-before-coding, no-speculative-scope, surgical and goal-driven rules; the wiring diff is how n-dev stays surgical. On structure, n-dev wins: "no abstraction for single-use code" and "fewest lines" give way to rule 1 when a module gives one responsibility a name, a seam and a test. A wrapper that only forwards calls stays out under both.
- **The repo's own conventions** win over this skill on style, layout and patterns. Follow them, and mention the disagreement in the report when one blocks a rule.
- **Bugs:** diagnose first (the `diagnosing-bugs` skill if installed), then fix through steps 4–7.

## Inside a 90north-develop flow

When this skill ships in the 90north-develop plugin, the loops split its steps between two roles. A tracked story runs in `dev-loop`, a tracked defect in `defect-loop`; an untracked change uses this skill alone.

| Role | Steps it owns |
|---|---|
| Orchestrator (dev-loop, defect-loop) | 1–3: orient, success criteria, design note and its gate; 6: review (as review + QA in parallel); 7: push, PR and the tracker |
| Builder or fixer subagent (`dev-builder`, `defect-fixer`) | 4–5 inside one work package or one root cause, and a local commit — never a push |

## Reference map

| Open | When |
|---|---|
| `references/structure.md` | deciding the split into files and modules, reuse vs extract, size budgets, dependency direction; the review checklist |
| `references/extension.md` | any change that touches a file that existed before the task |
| `references/state.md` | adding, moving or caching any state |
| `templates/design-note.md` | step 3 |
| `scripts/structure_check.py` | step 5; `--json` for machine-readable output |
