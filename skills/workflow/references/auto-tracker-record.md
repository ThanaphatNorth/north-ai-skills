# Tracker record — the lock, the labels, what every step leaves on the card

> Read when: auto mode writes anything to the tracker, runs A1 follow-ups, or releases stale locks. Field ids, label names, queries and transition ids live in `DL/config.md` § Auto mode; this file says *what* gets written and *when*.

The tracker (Jira, or the local board — `W/references/trackers.md`) is the system of record. People read the card, never `DL/runs/`. When the run files and the card disagree, the card wins, and the learner writes a lesson. Every step leaves a field, a label, a comment or a transition. A step that cannot write its row stops and reports why.

## How to write

| Write | Tool |
|---|---|
| labels add / remove, a field value | `W/scripts/tracker.sh edit <KEY> --add-label x --remove-label y --field <id>=<json>` (local board: `--field <name>=<value>` for one line, `--field-md <heading>=file.md` for longer text such as the AI summary) (or the Atlassian MCP `editJiraIssue` when config's access line names a working connector) |
| transition | `W/scripts/tracker.sh transition <KEY> <id | status>`; ids or statuses from config, re-read with `--list` when a move fails |
| comment, with inline video | `W/scripts/tracker.sh attach` then `W/scripts/tracker.sh comment <KEY> comment.md [commentId]`; it reads the comment back |
| search, read | `W/scripts/tracker.sh search '<query>'` (keys and status; JQL or the local query form), `W/scripts/tracker.sh get <KEY>` (text, comments, attachments), `W/scripts/tracker.sh card <KEY> <field ids>` (labels, priority, parent, links, config's fields) — or the Atlassian MCP `getJiraIssue` when config's access line names a working connector |

Never change Priority, Rank, Sprint, Assignee or any field config does not list for the loop.

## The lock

A card is in the AI queue when it matches config's queue query. The default is a label people add, `ai-queue`, on cards in a ready status, and the query leaves out locked cards (`AND labels not in (ai-processing)`); A2 drops any locked card the query still returns. A project may use a custom field instead (for example a select field "AI status": queued / processing / done), and config says which.

Each queued card carries exactly one **queue label**:
- `ai-queue`, put there by a person. The loop takes it by the card's type: defect types go to n-defect-loop, every other type to n-develop-loop.
- A hand-off label, `ai-to-defect` or `ai-to-develop`, put there by the other loop. Only the loop it names takes it, whatever the type.

Every row below that adds, keeps or removes "the queue label" acts on the label the card carries. A card's hand-off label is never swapped again: a card that arrived by hand-off is never handed back (`auto-triage.md` § Route).

| State | Default (labels) | Set by |
|---|---|---|
| queued | the queue label (`ai-queue` or a hand-off label) | a person, the other loop's hand-off, or A1 re-queue |
| locked | `ai-processing` (added at A2) | the loop |
| released | `ai-processing` removed, plus the queue label removed when the verdict is final | the loop at the end of the card |

A lock older than config's lock hours (default 2) is stale. At A2, the stale-lock query finds them: remove the lock, post § stale-lock, and leave the card queued. Only the loop removes `ai-processing`.

## Labels: plain words, one per group

| Group | Label | Meaning for a reader |
|---|---|---|
| verdict | `ai-do-now` | the AI is taking this card |
| | `ai-need-dev` | a developer must take it; the AI's analysis is on the card |
| | `ai-need-info` | the AI asked a question and is waiting |
| class | `ai-auto-merge` | a small, safe change; the AI merges it once checks pass, then QA tests it |
| | `ai-needs-review` | a person reviews the PR; **a person may add this at any time to force a review** |
| hand-off | `ai-to-defect` / `ai-to-develop` | the AI found this card belongs to the other kind of work; that loop's queue takes it next |

The loop removes only labels it set. A person's `ai-needs-review` is never removed. Projects may rename the labels in config. Keep them plain words.

## Per step

| Step | Field | Label | Comment (`W/templates/auto-comments.md`) | Transition |
|---|---|---|---|---|
| A2 lock | lock field, if config uses one | `ai-processing` (a card with a hand-off label also gets a `from-<other loop> KEY` ledger row) | — | — |
| A3 triage | AI summary field, if config names one: type / files / approach / risk / verdict | one verdict label; predicted class for do-now | § triage | need-info → config's need-info lane |
| A3 need-dev | AI summary = the solution | `ai-need-dev` | § solution-only | none |
| A3 hand-off (only a card whose queue label is `ai-queue`; never in `--dry-run`) | — | `ai-queue` swapped for the other loop's hand-off label, `ai-processing` removed | § hand-off | none |
| A4 not as expected | — | `ai-need-info` | § not-reproduced or § already-done, with the evidence inline | need-info lane |
| A4 red | — | — | — (the BEFORE evidence waits for the proof comment) | — |
| A4 dry run | `ai-processing` removed, the queue label kept | — | § dry-run-before, with the evidence inline | — |
| A5 start | — | — | — | → In Progress |
| A5–A7 | — | — | § build and § verify only when config › step comments is on | — |
| A5/A7 stopped | — | `ai-need-dev` | § stopped | none |
| A8 needs-review | — | class confirmed or swapped | proof comment (`W/templates/auto-comments.md` § Proof comment) | → config's review lane (both loops) |
| A8 auto-merge | — | `ai-auto-merge` | proof comment, then § auto-merged | → after-merge lane |
| A8 no push approval | — | — | § waiting-for-push | none |
| post-deploy failure | — | `ai-needs-review` | § auto-merge-reverted | → In Progress |
| A1 answered | — | `ai-need-info` removed, the card's queue label added back | — | → ready status |
| stale lock | — | `ai-processing` removed | § stale-lock | — |

## Wording rule

Every comment, and the AI summary, describes **the card only**: the problem, what was found, what changed, how it was checked, the PR, and what QA should look at. Loop internals never appear in tracker text: rule or row numbers, verdict or class names, labels, the verifier and its claims, gates, pass or attempt counts, agent names, run folders. The labels and `DL/runs/` carry those.

- Every comment starts with config's disclaimer, bold, then its step: `**<disclaimer>** · triage`. The comment script renders only bold, `code`, lists, links and `::video` lines (`W/templates/auto-comments.md`), so there are no blockquotes or code blocks.
- Language: config § Comments. Prose names no functions; each path is one `code` span in a list.
- Before posting, grep the draft, except pasted command output, for whole internal terms: the label names, `do-now`, `need-dev`, `need-info`, `auto-merge class`, `verdict`, `verifier`, `\bV[0-9]+\b`, `rule [0-9]`, `row [0-9]`, the agent names, `runs/`. Ordinary words ("checks pass", "attempted") are fine. Grep also for secrets and personal data. A hit → rewrite.
- Function and component names appear only inside a `code` span next to their path, never in a sentence.

## Follow-ups (A1)

Run these before taking a new card. They are the loop's active work.

| Query (config) | Finds | Action |
|---|---|---|
| need-info answered | cards labelled `ai-need-info` with a comment newer than the loop's question that does not start with the disclaimer (the loop posts as the operator's account, so the author cannot tell them apart) | remove `ai-need-info`, re-queue, move back to the ready status, `card.md` gets `followup: answered` so triage reads the answer first. If the answer was already on the card, the learner writes a triage lesson |
| reopened after AI | cards labelled `ai-do-now` back in Reopened (or the project's equivalent; on a local board `labels=ai-do-now status=reopened`) | re-queue with score +5 and `previousRun: DL/runs/<date>/<KEY>/`; the class is needs-review at best |
| PR feedback | `gh pr list --author <loop login> --state open --json number,reviewDecision,headRefName` in config's repos | `CHANGES_REQUESTED` → `DL/runs/<date>/feedback/<KEY>.md` (PR, branch, each review point quoted, `previousRun` from the loop's ledger); then `auto-evidence-and-ship.md` § Feedback rounds |
| PR merged by a person | the same list, `state: MERGED` since the last pass | ledger `merged`; outcome for the learner |

At most config › feedback rounds per pass.

## Reading a card at a glance

- The status column shows where the card is in the flow.
- The lock shows whether the AI holds it.
- The labels say what the AI decided, in words.
- The AI summary is the plan; the comments are the evidence, newest last, each tagged with its step.

## Sources

- Distilled from a production Jira AI loop's record contract and wording rule, set by its owner after comments leaked loop internals (2026).
- Jira Cloud REST v3, edit issue (labels `update` operations, `fields`): https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issues/
- Atlassian Document Format: https://developer.atlassian.com/cloud/jira/platform/apis/document/structure/
