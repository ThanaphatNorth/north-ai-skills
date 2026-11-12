# Feature docs — what the system does, its rules and why, kept true in every PR

> Read when:
> - a loop triages (step 2: by-design), checks the spec (step 3), plans or finishes a change (steps 5–6), or writes
>   the PR comment (step 8);
> - auto mode reads rules at A3 or writes the doc at A5;
> - the verifier checks claim V10;
> - develop-init sets config § Docs.
>
> This file owns every rule about feature docs. The loops, config and READMEs point here.

A **feature doc** is one markdown file per feature area of the repo. It records:
- what that area does today;
- the business rules it follows, and the requirement or decision each rule came from;
- which test proves each rule;
- why the area is built the way it is.

It is written for the next person or agent who must change the area without asking around.

The docs live in the repo (config § Docs › path, default `docs/features/<area>.md`, with an index `README.md`). A doc
changes **in the same PR as the code**, so a person reviews both together. When config § Docs is off, skip
everything here; V10 then reads `N/A`.

## What it holds, and what it does not

| It holds | It does not hold (the owner instead) |
|---|---|
| the area's purpose and who uses it | how the repo is layered (the n-arch profile) |
| every business rule, numbered `R-n`, each with its source (ticket key, decision id, spec link) | the requirement text itself (the tracker or the spec; the doc cites it) |
| behaviour a reader cannot see quickly in the code: flows, states, edge cases | a walk-through of the code, or copies of numbers and config values (point to the file instead) |
| rule → test, by test name (and file), or `no test yet` | test code, or line numbers that drift |
| decisions and their reasons, citing the decision record when one exists | per-ticket history (git, the ledger, the tracker) |
| known limits | changelogs, run reports, screenshots or anything personal from a ticket |

One owner per fact: when a value lives in code or config, the doc names the file and never repeats the value.

## Coverage

A doc created by a change records only the rules that change touched. Its header says
`coverage: partial — rules recorded as changes touch them` until a person checks the whole area and sets
`coverage: complete`. In a partial doc, a rule that is not listed is **unknown**, not absent: step 3 cannot call a
ticket a conflict because of it.

## When a loop writes it

| Situation | Doc change |
|---|---|
| n-develop-loop adds or changes a rule or user-visible behaviour | add or change the `R-n` rows, their source and their test; create the doc (partial) when the area has none |
| n-develop-loop: a refactor or internal change with no rule change | none. `build.md` and the report say "no rule changed" |
| n-defect-loop: the fix changes a rule or makes one clearer | change that rule, with the regression test in its row; create the doc (partial) when the area has none |
| n-defect-loop: a plain fix where the doc already states the right rule | only the regression test goes into that rule's row |
| n-defect-loop: a plain fix where the area has no doc | none. A plain fix creates no doc |
| n-dev on an untracked change in an area that has a doc | keep the doc true in the same commit |
| by-design (step 2 of n-defect-loop, either mode) | no branch and no doc edit; see below |

**By-design answers.** The decision is not final until the PO confirms it, so it never gets its own branch or doc
edit. The by-design comment either cites the rule that already says so (`R-n` in `<doc>`), or proposes the rule
line. The line lands in the doc with the next change in that area (n-develop-loop, if the PO re-scopes it), or a
person adds it. Cite an existing decision rather than adding one per ticket.

**Who writes it.** The orchestrator, or the conductor in auto mode, because it holds the ticket, the spec and the
design note. Builders and fixers never edit a feature doc or its index; their agent rules say so. Write it in the
worktree after the last build or fix, before S2, as a local commit `docs(<area>[, <area>]): <what changed> (<KEY>)`.
S4 squashes it with the rest. A change that spans areas updates each doc, plus their index lines.

## Reading it

- **Step 3 (and auto A3).** Before writing the `AC-n` list, read the rules of the areas the card touches. A ticket
  that contradicts a listed `R-n`, with no decision that settles it, is a conflict: ask which wins (`needs-info`).
- **Step 5.** The design note names each doc and the `R-n` rows it will add or change.
- **Freshness.** `verified-at` names the **base commit** the doc was last checked against (the branch's merge-base
  with the base branch, a sha that survives squash and merge). When `git log <sha>..HEAD -- <the area's paths>`
  shows newer changes, re-check the rules those changes touch before relying on them. Then set `verified-at` to the
  new base when the doc is checked again in a PR.

## Writing it

- **Template.** Start from the workflow skill's `templates/feature-doc.md`, or follow the repo's docs system if
  config names one (a Docusaurus site, an ADR folder, a handbook): its front matter, file layout and index come
  first.
- **Rule ids** are stable. Never renumber them. A rule that no longer holds stays, marked `retired: <date> <KEY>`,
  so old tickets and comments still point somewhere true.
- **Length.** Each doc stays within config § Docs › max lines. Past that, split it by sub-area and link the parts.
- **Index.** One line per doc in the folder's `README.md`: area, file, one-sentence purpose. The index is the only
  list of areas.
- **Language.** The repo's language, plain words, no secrets or personal data.
- **Claims.** The doc says only what the code and tests show. A rule without a test says `no test yet` instead of
  pretending.

## In the PR comment and the auto gates

- **The `Docs:` line.** The comment's §2 (n-develop-loop) or §3 (n-defect-loop) carries one `Docs:` line per doc:
  `Docs: <path> — <R-n added / changed / retired, or a test added to R-n>`. A new doc's index line counts with its
  doc. With no rule change, the line says "no rule changed".
- **Scope and size (auto mode).** The feature doc and its index lines are part of the card's scope (verifier V5).
  They count as allowed paths for the auto-merge gates, and are excluded from the size and file counts, like test
  files (`auto-evidence-and-ship.md` § Ship classes).

## Verifier claim V10 (auto mode, config § Docs on)

CONFIRMED when one of these holds:
- **The doc changed.** Every rule the code diff adds or changes has its `R-n` row, with a source and a test that
  exists in the diff or the repo. The doc states nothing the diff and tests do not show. `verified-at` names the
  branch's merge-base.
- **The doc did not change.** `build.md` says no rule changed, and the diff agrees.

Anything else refutes. A refuted V10 goes back to the conductor to fix the doc.

## Sources

- Design note: `research/90north-develop/design-feature-docs.md` in the north-ai-skills repo.
- Single owner per fact and the extension rule: `../n-dev/SKILL.md`.
- Architecture-level facts stay in the n-arch profile: `../n-arch/SKILL.md`.
