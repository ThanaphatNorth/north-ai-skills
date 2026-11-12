# Auto mode — comment templates (both loops)

<!-- The loop's markdown dialect, posted with W/scripts/tracker.sh comment (Jira: → ADF; a local board keeps the
     markdown): **bold**, `code`, "1. " and "- " lists, bare URLs, and `::video <uuid | KEY/name>` for an inline player
     (what W/scripts/tracker.sh attach prints). Nothing else renders: no headings,
     no fenced code blocks, no blockquotes, no single-asterisk italics.
     Write each file with the Write tool or a QUOTED heredoc (<<'EOF'), never <<EOF.
     Language: config § Comments; translate the labels, keep the structure. `{…}` are fills.
     Card content only (W/references/auto-tracker-record.md § Wording rule): no rule numbers, verdict or class names,
     labels, verifier, gates, pass or attempt counts, agent names, run folders.
     Paths and code: one `code` span each, in a "- " list. Function names never appear in prose.
     The proof comment is the flow's own 3-part template, adjusted as § Proof comment says. -->

## Proof comment

Use `../n-defect-loop/templates/jira-comment.md` (n-defect-loop) or `../n-develop-loop/templates/jira-comment.md` (n-develop-loop) with these changes, so it passes the wording rule:

- First line: `**{disclaimer}** · ship`.
- Defect §2 `Where:` keeps the `path:line` and puts any function or component name inside the same `code` span, never in the sentence.
- Dev §2 `Decisions:` lists the decisions in plain words and drops "who approved it (design gate date)": an unattended pass has no design gate.
- Dev §3 `Review + QA:` says what the review and QA changed, with no count of rounds.
- The evidence is the BEFORE and AFTER pair (`W/references/auto-evidence-and-ship.md` § Picture or video) in both loops; in n-develop-loop the AFTER clip walks the criteria in order, as the attended mode's demo does.
- Needs-review adds one line in card language on why a person reviews it. An auto-merge PR gets § auto-merged after the merge.

## triage

```
**{disclaimer}** · triage
**Result:** {the AI will make this change | a developer needs to take this | more information needed}
**Problem / request:** {one or two sentences in the card's own words}
**Where the change goes:** {plain words: the screen, the form, the rule}
**Planned change:** {what the user will see differently}
**Risk:** {none | what could break}
**Needed from a person:** {nothing | the exact question | why a developer must take it}
Files:
- `{repo}/{path}:{line}`
```

## need-info

```
**{disclaimer}** · triage
To work on this card, please add:
1. {the missing piece: steps, expected result, role, data, design, which of two sources wins}
2. {…}
{When two sources disagree, quote both, one line each, with where each is written.}
```

## hand-off

```
**{disclaimer}** · triage
This card is {a defect: the behaviour exists and is wrong | new or changed behaviour: it does not exist yet or the spec now asks to change it}, so it moves to the {defect | development} queue.
**Why:** {one sentence in the card's own words, citing the spec or decision when one settles it}
{Only when config § Docs is on: **Rule:** {`R-n` in `<doc path>` that already says so | proposed rule line, for a person to confirm}}
```

## solution-only

```
**{disclaimer}** · analysis
**Why a developer should take this:** {one line in card terms, e.g. "it changes the shared API"}
**Cause / where the change goes:** {plain words}
- `{repo}/{path}:{line}`
**Proposed change:**
1. {in `{path}`: what to change, with the old and new value as `code` spans}
2. {… ≤ 10 steps; a longer change gets a draft branch or a linked gist instead}
**Also touches:** {schema, API, other repos or teams | nothing else}
**How to test it:** {the spec the AI would have written: steps and expected results, ready to reuse}
```

## not-reproduced

```
**{disclaimer}** · reproduce
Followed the card's steps on {environment | the local stack at base {short sha}} and the problem did not appear.
**Recording:**
::video {uuid}
**What was used:** {account role, data, browser, anything different from the card}
**Please add:** {what would let it be reproduced: exact data, role, environment, a recording}
```

## already-done

```
**{disclaimer}** · reproduce
Checked the card's acceptance criteria on {environment | the local stack at base {short sha}}: the behaviour already matches.
- {criterion: what was seen}
**Recording:**
::video {uuid}
**Question for the owner:** is something else meant, or can this card be closed?
```

## dry-run-before

```
**{disclaimer}** · reproduce
Followed the card's steps on the local stack at base `{short sha}`; the problem shows as described.
**Recording:**
::video {uuid}
**Failing check:** `{pasted failing line}`
No change has been made yet.
```

## stopped

```
**{disclaimer}** · build
Work on this card started and then stopped, because {the area it needs to change | the fix could not be proven | a decision is needed}.
**What was found:** {root cause or design point in plain words}
**What was tried:**
- {one line per attempt}
**Suggested next step for a developer:** {what to do}
{Branch `{branch}` @ `{short sha}`: local only | pushed for reference: {link}}
```

## build (only when config › step comments is on)

```
**{disclaimer}** · build
**Cause:** {plain words}
**Change:** {what changed, for a QA reader}
**Tests:** `{command}` → `{pasted summary line}`
Files:
- `{path}`
```

## verify (only when config › step comments is on)

```
**{disclaimer}** · check
Before publishing, the evidence was checked again: {in card terms: the test covers every expected result, the before recording shows the problem, the after recording shows the fix, the change stays inside {area}}.
{Anything that had to be redone, in card terms.}
```

## waiting-for-push

```
**{disclaimer}** · build
The change is made and its checks pass on branch `{branch}` (commit `{short sha}`), but it is not pushed yet: pushing needs approval.
{One line on what the change does.}
```

## auto-merged

```
**{disclaimer}** · ship
The change was small and inside the agreed safe kinds, so it was merged: {PR link} → `{base}`.
Checks: {CI result line | "no PR CI in this repo — local checks and commit hooks passed"}.
Ready for QA on {environment} after deploy:
1. {the 1–3 things to look at}
```

## auto-merge-reverted

```
**{disclaimer}** · ship
After deploy, the card's check failed on {environment}, so a revert was opened for a person to merge: {revert PR link}.
**What failed:** {plain words} — `{pasted failing line}`
The card is back In Progress.
```

## stale-lock

```
**{disclaimer}**
The AI started on this card at {time} and did not finish within {lock hours} h. The card is back in the AI queue.
```
