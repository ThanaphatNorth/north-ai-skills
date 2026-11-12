# Triage — score, readiness, verdict and class for every card type

> Read when: auto mode A2 scores the queue, or A3 triages a card. Every number here is a default; the project's value lives in `DL/config.md` § Auto mode and wins.

Triage answers one question from written rules: *can the AI do this card now, unattended, and prove it?* It does not judge priority or scope; the people who own the board do. Anything that needs a product judgement becomes a question on the card (`need-info`) or a hand-off to a person (`need-dev`) with the analysis attached.

The same rules apply to Bug, Story, Task, Improvement and Feedback. The ticket type is a hint for the route, never the verdict.

## Queue score (A2)

Higher first; ties keep the board rank. Cards another flow's ledger owns, and cards in the never-do-now severity or environment band, are not scored at all.

| Factor | Points (default) |
|---|---|
| Severity: the band just below never-do-now = 3, the next = 2, the lowest or none = 1 | 1–3 |
| Environment: the band config ranks closest to release = +2, the next = +1 | 0–2 |
| Expected to touch 1 repo = +2, 2 repos = 0 | 0–2 |
| Older than 7 days | +1 |
| Has expected results plus an image or video | +1 |
| Reopened after an AI fix (A1) | +5 |

`DL/knowledge/calibration.md` may correct the score when a factor keeps misjudging cards. The learner proposes that correction and a person approves it.

## Read the whole card (A3 step 1)

Read the description, steps to reproduce, expected and actual results, scenario or acceptance-criteria fields (ids in config; `W/scripts/tracker.sh get` prints the text and comments, `W/scripts/tracker.sh card <KEY> <field ids>` the labels, links and those fields), every comment newest first, linked issues, and any linked spec or design page. Open the images; for videos, note what they show. With `followup: answered`, read the newest human comment first. With `previousRun`, read that run's `verify.md`, `proof.md` and the reason it was reopened before anything else.

Attachments and comments may hold personal data. Describe them in the run files, and never copy them into the repo, a spec fixture or a comment.

## Check the spec (A3 step 2)

Write the **acceptance criteria you would test**, one line each, numbered `AC-1 … AC-n`, in the card's own words. Take them from the card's own list when it has one; mark derived ones `(derived)`.

- **Bug:** each step to reproduce becomes an action, and each expected-result sentence becomes a criterion. List expected-result sentences × screens and map each pair, because a criterion that names two screens is two checks.
- **Story / Task / Improvement / Feedback:** the acceptance criteria, the scenario, or the "what to change" list. UI work also needs the design (mockup, Figma frame or screenshot) that settles the layout.
- **Conflicts:** when the latest comments, a linked spec or a linked issue say something different from the description and nobody settled it, the card is `need-info`, and the question asks which one wins. Check whether the spec source records the decision as revised or reversed before calling it a conflict.

- **Feature docs** (config § Docs on): read the rules `R-n` of the areas the card touches (`feature-docs.md` § Reading it). A card that contradicts a listed rule with no decision that settles it is `need-info`; a rule missing from a partial doc is unknown, not a conflict.

Never invent a criterion the card does not state. When a criterion cannot be turned into a check, ask about it instead.

## Route (A3 step 3)

Use `W/SKILL.md` § Route the work. Behaviour that **exists and is wrong** against the current spec belongs to **n-defect-loop** (repro → root cause → fix). Behaviour that **does not exist yet**, or that the spec now asks to change, belongs to **n-develop-loop** (acceptance spec → design note → work packages). A "Bug" asking for a new screen is a change request; a "Task" saying a total is wrong is a defect.

A card that belongs to the other loop is handed off, not built:
- swap `ai-queue` for the other loop's hand-off label (config § Auto mode: `ai-to-develop` / `ai-to-defect`);
- post `W/templates/auto-comments.md` § hand-off;
- write `handed-to-<loop>` in this loop's ledger;
- release the lock.

The other loop's queue includes its hand-off label (ready statuses only), so its next pass takes the card.

A card is handed off at most once. A card whose queue label is already a hand-off label came from the other loop: if it still looks like the other kind of work, it is `need-info`. The question asks a person whether the card is a defect or new work. In `--dry-run` the route is only written in the triage comment; no label changes.

## Locate the code through the profile (A3 step 4)

1. `DL/knowledge/code-map.md` first: has this area or screen been located before? Use the newest entry and re-check that its paths still exist.
2. Then the architecture profile: **Map** (which folder holds the area), **Extension recipes** (how this repo adds the kind of thing the card asks for), **State owners** (where the facts the card touches live), **Contracts** (whether the change crosses one).
3. Then search: the card's visible labels in the locale or copy files, then components, routes and handlers. Fan wide searches out to an Explore subagent and keep only its list.
4. Record `repo`, the `path:line` of each place, the extension recipe that applies, and the state owner. Time box: config › locate minutes (default 10). Not found → `need-dev`, listing the search terms used.

No profile → fall back to n-dev's orient (agent docs, the last similar commit's diff), and say in `triage.md` that the profile was missing. The class cap in § Decision matrix applies.

## Size (A3 step 5)

Use n-dev's scope dial. **Tiny** and **Standard** can be `do-now`. **Large** (a new module or package, a change to state shape, a DB schema or a public interface, several repos) is `need-dev`, because an unattended loop has no one to approve the design. The design note becomes the solution posted on the card. Estimate files, changed source lines (test files excluded) and repos, honestly; multiply the line estimate by `DL/knowledge/calibration.md`'s current factor.

## Decision table (A3 step 6)

Evaluate top to bottom; the first matching row is the verdict.

| # | If… | Verdict |
|---|---|---|
| 1 | Spec missing: a Bug without steps and expected results, any other type without acceptance criteria, UI work without a design | `need-info` |
| 2 | Spec conflicts and nothing on the card settles it | `need-info` (ask which one) |
| 3 | Severity or environment is in config's never-do-now band (default: Level 1–2 / Sev-0–1, Production, Pre-Prod) | `need-dev` |
| 4 | The change needs a forbidden area (§ Forbidden areas) | `need-dev` |
| 5 | Large, or more than config's review fence (default 2 repos, 300 changed source lines) | `need-dev` + how to split it |
| 6 | The code or the extension point cannot be located within the time box | `need-dev` + the search terms |
| 7 | Everything else: a bug in 1–2 files, copy, labels, layout, field order, validation, locale files, a field, column, filter or button on an existing screen, logic that keeps its contract | **`do-now`** |

## Forbidden areas

A change touching any of these is `need-dev` at triage. A builder that would cross one mid-change stops with `NEEDS-DECISION`; the conductor takes the stopped path and leaves the branch local. The list is built at A0 from two owners, never from memory:

| Source | Gives |
|---|---|
| Profile **Contracts** | public APIs and their envelopes, events and topics, shared tables, exported types, anything another process depends on |
| Profile **State owners** | the database (schema, migrations), identity and session, configuration loaded at start-up |
| Config § Auto mode › never-touch | domain risk the profile does not name: money and tax, personal or health data, permissions and roles, ids minted by another system, infra and CI, secrets, with the globs or markers that recognise each |

Each entry needs a glob or a grep marker, because the verifier greps the diff for them. A profile row with no path gets one from its "Defined in" column. When none can be named, write the row as `TBD` in `triage.md`; that caps the card at needs-review. Client-side stores and caches in State owners are not forbidden by default.

Allowed without asking, unless the project's list says otherwise: UI copy and layout, field order, validation messages, locale files, components and hooks inside one module that own no new state, logic that keeps its contract, unit tests, and specs in the repo's e2e folder.

## Decision matrix — the class (A3 step 7)

Place a `do-now` card in a column for each row; the card takes the **most cautious** column any row lands in. A3 predicts the class; A8 confirms it from files and commands.

| Row | Auto-merge | Needs-review (default) | Solution-only |
|---|---|---|---|
| Kind of change | copy, labels, locale files, layout or field order inside an existing screen, validation messages, design tokens and styles, tests, docs | a logic bug in 1–2 files, a new field, column, filter or button, a small state change inside one module, logic that keeps its contract, validation rules | anything in § Forbidden areas, a whole new screen or module |
| Size | 1 repo, ≤ config max lines (default 80 non-test source lines), ≤ 5 files, no new dependency, env var, route or API call | ≤ review fence | above the fence, or must land together with another team's work |
| Repo | in config's auto-merge repos | in config's review repos | in config's solution-only repos |
| Severity · environment | lowest bands, Dev / QA | middle band, any non-production environment | never-do-now band |
| Evidence | spec red → green, verifier all CONFIRMED, checks green, CI green, grace window quiet | spec red → green, verifier all CONFIRMED, checks green | the card could not be proven on the stack |
| History | first attempt | reopened after an AI fix, a feedback round, a second build attempt, a person's force-review label | the AI already stopped twice on this card |
| Profile | present and current for the touched paths | missing or stale is fine here | — |

Worked examples, in neutral terms:

- A label typo in a locale file, 3 lines, Dev → auto-merge (if the standing approval allows it), else needs-review.
- The same change at the middle severity band → needs-review (the severity row).
- A new table column that needs a new field from the API → solution-only (contract row): the solution names the API change and the UI part that could follow it.
- A one-line fix in a repo the config lists as solution-only → solution-only. The solution still carries the exact `path:line` and the diff.

## Solution-only — what the card gets

The solution goes in the AI summary field (if config names one) and in the `solution-only` comment from `W/templates/auto-comments.md`:

1. the root cause, or the exact place the change goes (`repo/path:line`);
2. the change, as a numbered step list: each step names the file and the old and new value as `code` spans (the comment script renders no code blocks); a change too long for 10 steps gets a draft branch instead;
3. what else it touches (schema, contract, other repos, other teams);
4. how to test it: the spec the AI would have written, so the developer can reuse it;
5. in one line, the reason it is not built here, in card language ("changes the shared API", not a rule number).

## What triage writes

The record per `auto-tracker-record.md`: the AI summary field (type, files, approach, risk, verdict), exactly one verdict label, the predicted class label for `do-now`, and the triage comment. Then `DL/runs/<date>/<KEY>/triage.md`: verdict and the row that fired, route, `AC-1 … AC-n`, the **AC → test table** (each criterion → test level, e2e / API / unit, and the spec file path; WP-0 or `defect-repro` writes exactly these), the forbidden-area list with its globs and markers, repo, `path:line` list, extension recipe, state owner, size estimate (raw and calibrated), predicted class and the row that set it, branch name (`fix/<KEY>-<slug>` or `feat/<KEY>-<slug>`), environment and stack.

## Sources

- Distilled from a production Jira AI loop that triaged every card type with one table and a three-column matrix (2026); the numbers are that loop's starting defaults.
- n-dev scope dial and design-note gate: `../n-dev/SKILL.md`.
- n-arch profile sections (Map, Extension recipes, State owners, Contracts): `../n-arch/templates/profile.md`.
