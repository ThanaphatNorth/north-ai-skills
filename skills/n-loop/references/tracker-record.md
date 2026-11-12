# Tracker record — the lock, the labels, what every step leaves on the card

> Read when: n-loop writes anything to the tracker, runs A1 follow-ups, or releases stale locks. Field ids, label names, queries and transition ids live in `DL/config.md` § AI loop; this file says *what* gets written and *when*.

Jira is the system of record. People read the card, never `DL/runs/`. When the run files and the card disagree, the card wins, and the learner writes a lesson. Every step leaves a field, a label, a comment or a transition. A step that cannot write its row stops and reports why.

## How to write

| Write | Tool |
|---|---|
| labels add / remove, a field value | `W/scripts/jira-edit.sh <KEY> --add-label x --remove-label y --field <id>=<json>` (or the Atlassian MCP `editJiraIssue` when config's access line names a working connector) |
| transition | `W/scripts/jira-transition.sh <KEY> <id>`; ids from config, re-read with `--list` when a move fails |
| comment, with inline video | `W/scripts/jira-attach.sh` then `W/scripts/jira-comment.sh <KEY> comment.md [commentId]`; it reads the comment back |
| search, read | `W/scripts/jira-search.sh '<JQL>'` (keys and status), `W/scripts/jira-get.sh <KEY>` (text, comments, attachments), `W/scripts/jira-card.sh <KEY> <field ids>` (labels, priority, parent, links, config's fields) — or the Atlassian MCP `getJiraIssue` when config's access line names a working connector |

Never change Priority, Rank, Sprint, Assignee or any field config does not list for the loop.

## The lock

A card is in the AI queue when it matches config's queue query. The default is a label people add, `ai-queue`, on cards in a ready status, and the query leaves out locked cards (`AND labels not in (ai-processing)`); A2 drops any locked card the query still returns. A project may use a custom field instead (for example a select field "AI status": queued / processing / done), and config says which.

| State | Default (labels) | Set by |
|---|---|---|
| queued | `ai-queue` | a person, or A1 re-queue |
| locked | `ai-processing` (added at A2) | the loop |
| released | `ai-processing` removed, plus `ai-queue` removed when the verdict is final | the loop at the end of the card |

A lock older than config's lock hours (default 2) is stale. At A2, the stale-lock query finds them: remove the lock, post § stale-lock, and leave the card queued. Only the loop removes `ai-processing`.

## Labels: plain words, one per group

| Group | Label | Meaning for a reader |
|---|---|---|
| verdict | `ai-do-now` | the AI is taking this card |
| | `ai-need-dev` | a developer must take it; the AI's analysis is on the card |
| | `ai-need-info` | the AI asked a question and is waiting |
| class | `ai-auto-merge` | a small, safe change; the AI merges it once checks pass, then QA tests it |
| | `ai-needs-review` | a person reviews the PR; **a person may add this at any time to force a review** |

The loop removes only labels it set. A person's `ai-needs-review` is never removed. Projects may rename the labels in config. Keep them plain words.

## Per step

| Step | Field | Label | Comment (`templates/comments.md`) | Transition |
|---|---|---|---|---|
| A2 lock | lock field, if config uses one | `ai-processing` | — | — |
| A3 triage | AI summary field, if config names one: type / files / approach / risk / verdict | one verdict label; predicted class for do-now | § triage | need-info → config's need-info lane |
| A3 need-dev | AI summary = the solution | `ai-need-dev` | § solution-only | none |
| A4 not as expected | — | `ai-need-info` | § not-reproduced or § already-done, with the evidence inline | need-info lane |
| A4 red | — | — | — (the BEFORE evidence waits for the proof comment) | — |
| A4 dry run | `ai-processing` removed, `ai-queue` kept | — | § dry-run-before, with the evidence inline | — |
| A5 start | — | — | — | → In Progress |
| A5–A7 | — | — | § build and § verify only when config › step comments is on | — |
| A5/A7 stopped | — | `ai-need-dev` | § stopped | none |
| A8 needs-review | — | class confirmed or swapped | proof comment (`templates/comments.md` § Proof comment) | → config's review lane (both routes) |
| A8 auto-merge | — | `ai-auto-merge` | proof comment, then § auto-merged | → after-merge lane |
| A8 no push approval | — | — | § waiting-for-push | none |
| post-deploy failure | — | `ai-needs-review` | § auto-merge-reverted | → In Progress |
| A1 answered | — | `ai-need-info` removed, `ai-queue` added | — | → ready status |
| stale lock | — | `ai-processing` removed | § stale-lock | — |

## Wording rule

Every comment, and the AI summary, describes **the card only**: the problem, what was found, what changed, how it was checked, the PR, and what QA should look at. Loop internals never appear in tracker text: rule or row numbers, verdict or class names, labels, the verifier and its claims, gates, pass or attempt counts, agent names, run folders. The labels and `DL/runs/` carry those.

- Every comment starts with config's disclaimer, bold, then its step: `**<disclaimer>** · triage`. The comment script renders only bold, `code`, lists, links and `::video` lines (`templates/comments.md`), so there are no blockquotes or code blocks.
- Language: config § Comments. Prose names no functions; each path is one `code` span in a list.
- Before posting, grep the draft, except pasted command output, for whole internal terms: the label names, `do-now`, `need-dev`, `need-info`, `auto-merge class`, `verdict`, `verifier`, `\bV[1-9]\b`, `rule [0-9]`, `row [0-9]`, the agent names, `runs/`. Ordinary words ("checks pass", "attempted") are fine. Grep also for secrets and personal data. A hit → rewrite.
- Function and component names appear only inside a `code` span next to their path, never in a sentence.

## Follow-ups (A1)

Run these before taking a new card. They are the loop's active work.

| Query (config) | Finds | Action |
|---|---|---|
| need-info answered | cards labelled `ai-need-info` with a comment newer than the loop's question that does not start with the disclaimer (the loop posts as the operator's account, so the author cannot tell them apart) | remove `ai-need-info`, re-queue, move back to the ready status, `card.md` gets `followup: answered` so triage reads the answer first. If the answer was already on the card, the learner writes a triage lesson |
| reopened after AI | cards labelled `ai-do-now` back in Reopened (or the project's equivalent) | re-queue with score +5 and `previousRun: DL/runs/<date>/<KEY>/`; the class is needs-review at best |
| PR feedback | `gh pr list --author <loop login> --state open --json number,reviewDecision,headRefName` in config's repos | `CHANGES_REQUESTED` → `DL/runs/<date>/feedback/<KEY>.md` (PR, branch, each review point quoted, `previousRun` from `DL/ai-ledger.md`); then `evidence-and-ship.md` § Feedback rounds |
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
