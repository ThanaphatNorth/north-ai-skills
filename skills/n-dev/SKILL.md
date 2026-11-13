---
name: n-dev
description: Use for every task that changes code or tests in a repo, however small — a bug fix, a validation, a new function, a feature, spec or ticket, a module, API, screen or job, a refactor. Development discipline — a failing test shown before the fix, reuse before writing, new behaviour beside existing code, one owner per fact (single source of truth), verified with evidence and reviewed for structure, security and performance. Not for questions or explanations that change no code.
---

# n-dev

How to build software that stays easy to change: think first, design the structure, build test-first at the seams, verify with evidence. It merges the Karpathy guidelines (think before coding, no speculative scope, surgical changes, goal-driven execution) with the `/implement` loop (TDD at seams, typecheck often, full suite at the end, review, commit) and adds three structural rules. Report in the user's language; keep code, identifiers and commit messages in the repo's language.

## The four rules

1. **Simple, not easy.** *Simple* means each module does one thing and is not entangled with the others. *Easy* means whatever is nearest: one long file, a copy of a similar block, everything inline. Choose simple even when easy is shorter.
   - Split by responsibility into small modules with a small interface (a **deep module**), with a **functional core**: pure functions that decide and transform, and a thin shell that does the I/O and passes dependencies in.
   - **Reuse before you write.** Search for an existing function, hook, service or library before adding one; extend what exists.
   - **Verify, don't recall.** Read a library's signature in the installed source, or the docs of the locked version, before calling it. A new dependency needs a reason no installed one meets, and its exact name checked in the registry (the structure check lists each as `new-dependency`).
   - Extract a shared module when a second real caller exists or the code names a domain concept; a module that only forwards calls fails the deletion test and is merged back.
   - Structure is where effort goes; **scope** stays exactly what was asked — no extra feature, option, flag or config.
2. **Extend beside, not inside.** New behaviour lives in new files. A file that existed before the task receives only a **wiring diff**: the import plus the line that registers, composes or delegates to the new module. Edit in place only for a bug in that code, or when extending would copy most of it; then every changed line traces to the request. Details and the decision table: `references/extension.md`.
3. **One owner per fact.** Every piece of state (UI, server data, URL, form, cache, config, database row) has exactly one owner. Others read it through a selector or query, write it through one module, and compute derived values instead of storing them. A copy exists only as a cache with a named invalidation rule. Details: `references/state.md`.
4. **Verified, not claimed.** Each success criterion becomes a check — a test seen red then green, a command, an observable result. Work is done when the checks pass in this session, and the report shows the evidence. Never reach green by asking less of a test: no removed or loosened assertion, skip or focus marker, regenerated snapshot or lowered coverage gate unless the request changed that behaviour. The structure check lists each as `test-weakened`, and each one carries its reason in the report.

## Scope dial

Pick the size first; it decides how much of the process runs.

| Size | Looks like | Run |
|---|---|---|
| **Tiny** | typo, config value, a few-line bug fix or small function | Steps 1, 4–5, 7, red gate included. Rules 2–3 still hold. |
| **Standard** | a feature, endpoint, screen, job, or a bug touching more than one file | Every step; the design note goes in chat, short. |
| **Large** | a new module or package, a change to state shape, DB schema or a public interface, several repos | Every step; the design note is saved as a file beside the work (the repo's docs folder, else the scratchpad), the interface is designed twice, and the note's Progress list stays current so another session can resume from it. |

## Steps

1. **Orient.** If the repo has an architecture profile (`docs/architecture/profile.md`, or the `[profile] path` in `.ndev.toml`), read it first. It already holds the four facts below plus the layer rules, so check it is current (`git log --oneline <its verified-at sha>..HEAD -- <the paths it names>`) and re-verify only the facts this task touches. Without a profile, read the repo's agent and contributor docs (CLAUDE.md, AGENTS.md, CONTRIBUTING), lint and formatter config, and how the most recent similar feature was added (`git log` on a sibling feature, then read that commit's diff — it is the repo's own recipe); on Standard or Large work, suggest the `n-arch` skill in the report. Hand the reuse search to a subagent on Standard or Large work and keep only its list. Record four facts:
   - **Commands** for typecheck, one test file, the full suite, and lint.
   - **Extension points**: how this codebase adds a route, handler, screen, command or listener without editing a central file (`references/extension.md` § Finding the repo's extension points).
   - **State owners** already in use: server cache, store, URL, forms, database, config module.
   - **Reuse inventory**: existing code the task can use, found by searching the task's verbs and nouns; "none found" is a valid answer when the search terms are listed.
   *Done when* all four facts are written down.
2. **Think.** State assumptions; when the request reads two ways, show both and pick only when the context settles it. Turn the goal into success criteria, each one a test, a command or an observable result. *Done when* every criterion can be checked by something other than opinion.
3. **Design note.** Fill `templates/design-note.md`: module map, state ownership table, extension plan, test seams. When the area has a feature doc (for example `docs/features/<area>.md`), the note names the rules it will add or change. For Large work, design the interface two radically different ways and compare them on depth, locality and seam placement (the `codebase-design` skill, if installed, has the method). When the change touches a contract, schema, migration, outbound call or the deploy, answer the checklist in `references/change-safety.md` in the note. Walk `references/security.md` and `references/performance.md` for the boundaries, records and data paths the note lists. Then continue without waiting, except in two cases, where you show the note and stop for the user's decision:
   - two designs trade off in a way the user would care about;
   - the change alters state shape, a DB schema, or a public interface.
   *Done when* every new file has a one-sentence responsibility, every fact has exactly one owner, and every pre-existing file in the plan has a reason.
4. **Build test-first, inside out.** Before extending existing behaviour, pin it with a characterization test. Then for each module, core first: write the test at its interface and see it fail (**red**) for the right reason — an assertion about the missing behaviour, not an import or syntax error (add a stub first if needed) — then implement until it passes (**green**), and tidy. Order: pure core, then adapters, then the wiring diff last. Run typecheck and that test file after each module. Use the `tdd` skill if installed.
   - **Red gate.** Make no implementation edit until a test run in this session has failed on the missing behaviour. An acceptance spec the user gave is that test: run it first, as given. A bug fix starts with a test that reproduces the report. Keep the red run's command and failing line for the report; when no red run is possible (a refactor under green tests, a config or docs change), write down why instead.
   *Done when* every success criterion has a test that was seen red and then green, and the red evidence (or its reason) is written down.
5. **Verify.** Run the full suite, lint, typecheck, and the structure check:
   ```bash
   python3 <skill-dir>/scripts/structure_check.py --base <base-ref>
   ```
   It reports pre-existing files that changed beyond a wiring diff, files and functions over budget, added lines wider than the width budget, blocks copied from code that already exists, added imports that break the repo's layer rules, changes that weaken tests, and new dependencies. A file or function that was already over budget at the base ref is listed apart as existing debt and does not fail the check: mention it in the report, and refactor it only when the task asks. Budgets, excludes and layers come from `.ndev.toml` when the repo has one; otherwise set the budgets to the repo's norms with flags (`--help` lists them). *Done when* everything is green, and each structure finding is fixed or carries a one-line reason in the report.
6. **Review** through three lenses, each read fresh: the reviewer gets the diff, the request and the success criteria but not your design reasoning (a subagent with a new context by default; for Standard and Large work, one per lens, in parallel).
   - **Structure:** the `code-review` skill if installed; otherwise the checklist in `references/structure.md`, reading every changed line of a pre-existing file.
   - **Security:** every row of `references/security.md` the diff touches.
   - **Performance:** every row of `references/performance.md` the diff touches, at the data sizes the project reaches.
   Each finding names `path:line`, the input or data size that breaks it, and the test that would prove it; trace it to the failing line and look for an existing guard before calling it a finding. Fix each one test-first (that test red, then green) and re-run step 5. A lens the diff gives nothing to look at says so in one line. A finding whose test will not go red (with the test you tried), one with a static check (an index, the random source: the line is the proof), and one in code the change did not touch are listed in the report instead. *Done when* no finding is open in any lens.
7. **Commit and report.** When the area has a feature doc and the change adds or changes a rule, keep the doc true in the same commit: each rule with its source and the test that proves it, values named by file rather than copied, rule ids kept stable (a rule that no longer holds is marked retired, not deleted). A builder or fixer subagent inside a 90north-develop loop leaves the doc to its orchestrator. Commit on a feature branch (create one if on the default branch), following the repo's commit convention and the user's rules on commit messages; stage only files this task changed. Push only when the user asks. Report: what was built, the red run (its command and failing line, or why there was none) then the green run, the other checks and their results, the structure-check result, each pre-existing file touched and why, and anything left unverified.

## When skills disagree

- **karpathy-guidelines / inv-code-craft:** keep their think-before-coding, no-speculative-scope, surgical and goal-driven rules; the wiring diff is how n-dev stays surgical. On structure, n-dev wins: "no abstraction for single-use code" and "fewest lines" give way to rule 1 when a module gives one responsibility a name, a seam and a test. A wrapper that only forwards calls stays out under both.
- **The repo's own conventions** win over this skill on style, layout and patterns. Follow them, and mention the disagreement in the report when one blocks a rule.
- **n-arch** owns the architecture profile and `.ndev.toml`; n-dev reads them and never writes them. A practice pack the repo already has (a `*-practices` skill, house rules) is part of the repo's conventions.
- **Bugs:** diagnose first (the `diagnosing-bugs` skill if installed), then fix through steps 4–7.

## Inside a 90north-develop flow

When this skill ships in the 90north-develop plugin, the loops split its steps between two roles. A defect runs in `n-defect-loop`, a story, feature or change request in `n-develop-loop`, each attended or unattended (`--auto`); an untracked change uses this skill alone.

| Role | Steps it owns |
|---|---|
| Orchestrator (either loop, attended) | 1–3: orient, success criteria, design note and its gate; 6: review (code, security and performance reviewers plus QA, in parallel); 7: push, PR and the tracker |
| Conductor (either loop with `--auto`) | the same 1–3, 6–7, but with no one to answer the step-3 gate: a Large card or a gate case found mid-build parks the card with the design note posted as the solution; 6 adds an adversarial verifier that treats the structure check's findings as a claim to refute |
| Builder or fixer subagent (`dev-builder`, `defect-fixer`) | 4–5 inside one work package or one root cause, and a local commit — never a push |

## Reference map

| Open | When |
|---|---|
| `references/structure.md` | deciding the split into files and modules, reuse vs extract, size budgets, dependency direction; the review checklist |
| `references/extension.md` | any change that touches a file that existed before the task |
| `references/state.md` | adding, moving or caching any state |
| `references/security.md` | the change reads outside input (file, archive, network response, request, env var, argument, user-typed path), changes who may see or do what, returns or logs stored data, calls another service or adds a dependency; also the step 6 security lens |
| `references/performance.md` | the change reads or writes stored data, loops over input, calls the network, adds a cache, changes a payload or the client bundle, or migrates data; also the step 6 performance lens |
| `references/change-safety.md` | Large work, or any change to a contract, schema, migration, outbound call or the deploy: compatibility, rollout, failure modes, signals |
| `templates/design-note.md` | step 3 |
| `scripts/structure_check.py` | step 5; `--json` for machine-readable output, `--all` to audit the whole repo, reads `.ndev.toml` |
| `evals/README.md` | changing this skill: the eval suite compares runs with and without it (`claude plugin eval skills/n-dev --scaffold --allow-tools Bash Write Edit Task Agent`, with a real git first in PATH on macOS) |
