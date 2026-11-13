# Design note: security and performance review (90north-develop 0.9.0)

Status: **requested 2026-11-13** ("เพิ่มเรื่อง review performance และ security ด้วย"). The defaults below are mine;
each one is listed under Decisions so it can be changed.

## Request

The loops should review every change for security and for performance, not only for structure and the spec.

## The gap today

| What exists | What it covers | What it misses |
|---|---|---|
| n-dev `references/security.md` | input from outside the process: paths, archives, shell, state files, secrets, sessions, size | who may see which record (IDOR), injection into queries and HTML, data exposure in responses and logs, outbound URLs (SSRF), new dependencies, randomness |
| n-dev step 6 review | structure (`references/structure.md`), plus security only when the change reads outside input | performance: nothing anywhere |
| S2 Verify | one code reviewer (structure + spec) and QA, in parallel | no reviewer looks for attacks or for cost that grows with data |
| auto-merge gates | kind, size, blast radius, structure, proof, CI | a change that needed a security or performance fix can still auto-merge |

## Decision

Two **lenses**, each with one checklist owned by n-dev (so n-dev alone gets them too), and one read-only agent that
reviews a diff through one lens at a time.

| Piece | Owner | What it holds |
|---|---|---|
| Security checklist | `skills/n-dev/references/security.md` (extended) | the existing boundary rows, plus object access, injection, output encoding, data exposure, outbound requests, dependencies, randomness and secret comparison, rate limits |
| Performance checklist | `skills/n-dev/references/performance.md` (new) | queries per request, unbounded reads, indexes, work in loops, blocking the hot path, outbound calls, caches, payload size, client bundle and renders, migrations and backfills |
| n-dev step 6 | `skills/n-dev/SKILL.md` | the review covers three lenses: structure, security, performance; the finding format |
| Reviewer | `plugins/90north-develop/agents/risk-reviewer.md` (new) | dispatched once per lens; static and read-only; trace before claiming; severity; output file |
| When and how the loops use it | `skills/workflow/references/stages.md` § S2 | dispatch, skip rule, fix round, findings outside the change, disclosure |
| Auto-mode proof | `loop-verifier` claim **V11** | both reviews ran on the head and nothing they found is open |
| Auto-merge | `auto-evidence-and-ship.md` § Ship classes | a new gate: the reviews found nothing at blocker or should-fix |

## How a change is reviewed (S2, both loops, both modes)

1. One message dispatches the code reviewer, `risk-reviewer` with lens security, `risk-reviewer` with lens
   performance, and QA. A repo role file for a security or performance reviewer (config § Team) goes into the
   agent's brief as house rules; the agent and its output format stay, because V11 and the ship gate read it.
2. Each reviewer writes `review-security.md` or `review-performance.md`: the rows it walked, then findings with
   `path:line`, the input or data size that breaks it, the test that would prove it, and a fix direction.
3. Both lenses run on every change. A change with nothing for a lens still gets its file, listing the rows checked.
4. Fix round (the same budget of 2): every blocker and should-fix inside the change. Each fix starts with a test
   that is red for that input or size; a static check (an index, the random source, a pinned dependency) is proven
   by its line. A finding the builder cannot turn red comes back as not reproduced, with the test it tried; the
   reviewer checks that the test used the finding's input or size before turning it into a note.
5. Findings in code the change did not touch are reported, not fixed. A security weakness outside the change never
   goes into the tracker, a PR, a commit or a committed file (a local board is committed): the comment says only
   that a note went to config § Review › security notes, and the note goes to that owner in the chat or the pass
   report.
6. Every later run of a reviewer on the item gets its previous file, so findings and states carry over and a change
   that needed a fix can never look clean to the auto-merge gate.

## Severity

| Severity | Security | Performance | Handling |
|---|---|---|---|
| blocker | a concrete input reaches data or an action it must not, or exposes a secret or personal data | cost grows with data or users on a path the change adds or changes, at a size the project reaches | fixed in this change |
| should-fix | a real weakness that needs an unusual condition | a cost visible only beyond today's sizes | fixed when it is inside the item's scope, else recorded |
| note | hardening | a measurement worth adding | recorded in the review file |

A performance finding must name the size where it hurts (from config § Review, the profile, seed data or the
ticket). "Could be slow" with no size is not a finding; with no size known it is marked `size unknown` and is at
most a should-fix. Tests measure what scales (query count, calls, items, bytes),
not wall-clock time, unless the repo has a benchmark harness.

## Auto mode

- **V11** (verifier): both review files exist and name the branch head; every blocker and should-fix inside the
  change has its test (or static line) in the diff, or is recorded as not reproduced with a test that used its input,
  or is an out-of-scope should-fix in the comment; no security weakness outside the change and no exploit input in
  the comment.
- **V5** accepts the fix and test of a `closed` finding as in scope.
- **Auto-merge gate "Risk review"**: both reviews found nothing at blocker or should-fix, before or after a fix
  round. A change that needed a security or performance fix is not low-impact, so a person reviews it.
- Auth, permissions, secrets, personal data and money are already forbidden areas, so they never auto-merge; no new
  "sensitive paths" list is added.

## Config

- § Team: role-file slots for a security reviewer and a performance reviewer; the plugin agent list names
  `risk-reviewer`.
- § Checks: the repo's own scanners, which QA runs (dependency audit, secret scan, SAST, bundle size, benchmark). The
  loop adds none.
- § Review (new): the data sizes the performance lens assumes, and who gets security notes (the person running
  the loop by default; never the tracker or a PR).
- develop-init finds the repo's scanners and reviewer agents, and asks for the data sizes.

## Decisions (defaults; change any of them)

1. One agent with a lens parameter, not two agents, so the finding format and rules have one owner.
2. The reviewer is static: it never runs the app, tests, builds or the network. Scanners belong to QA, and a secret
   scanner runs with its redact option.
3. Both lenses run on every change, with no skip rule (lockfiles, CI, containers and infra config are reviewed too).
4. Any blocker or should-fix, even fixed, takes a change out of auto-merge.
5. No new sensitive-paths list: the forbidden areas already cover it.

## Success criteria

1. `performance.md` exists; `security.md` has the new rows; n-dev step 6 names three lenses. Check: grep, red before.
2. `risk-reviewer` exists; S2, both loops, auto mode, the verifier (V11), the ship gates, both comment templates,
   config and develop-init name it or its files. Check: grep count, red before.
3. The checks pass:
   - `validate_skill.py` reports 0 errors on every skill (it also fetches every source URL);
   - `claude plugin validate` passes;
   - the script tests (58) and the n-dev tests (135) stay green;
   - the structure check against `main` is clean;
   - every referenced path resolves.
4. A fresh review finds no open issue.

## Changes after the fresh review (2 blockers, 10 should-fix, nits)

- **The agent was not registered:** `plugin.json` lists agents by path; `risk-reviewer` is added.
- **V5 refuted fix-round hunks:** it now accepts the fix and test of a `closed` finding.
- **Gate lists in both loops' step 9**, the pre-post grep (finding ids), the PR body and the "review + QA" mentions
  now name the security and performance review.
- **Not reproduced:** static checks are proven by their line; the reviewer judges the tried test; the comment has a
  slot; standalone n-dev lists them in the report.
- **No skip rule** (lockfile, CI, container and infra changes were neither code nor docs), and a repo role file is
  house rules, not a replacement, so the output format V11 reads stays.
- **Carry-over:** every later reviewer run gets its previous file, so `found in all rounds` cannot reset; builders
  report `FINDINGS:`.
- **Disclosure:** security weaknesses outside the change go to a named owner, never to a committed board, the
  tracker or a PR; the learner keeps only the kind and fix pattern.
- **Checklists:** the index check reads the schema (EXPLAIN on small seed data proves nothing); the dependency check
  reads QA's audit; new rows for mass assignment, secrets in the client, tokens on the device, and deploy and CI
  config; redirects moved to outbound requests; an unknown size makes a finding `size unknown`, at most should-fix.
