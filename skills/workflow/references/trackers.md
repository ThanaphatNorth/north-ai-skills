# Trackers — one door, two backends

> Read when: setting up a repo (develop-init), writing a query or lane into config, or a loop calls
> `W/scripts/tracker.sh` and you need a verb's arguments for this repo's backend.

Every loop reaches the tracker through `W/scripts/tracker.sh <verb> …`. `TRACKER` in `DL/tracker.env` picks the backend:

| `TRACKER` | Backend | For |
|---|---|---|
| `jira` (the default, also when the line is missing) | the `jira-<verb>.sh` scripts, Jira REST v3, credentials file | a team board in Jira |
| `local` | `local_board.py`: one markdown file per card in the board folder | a repo with no Jira; works offline and needs no account |

Scripts find `DL` by walking up from the current folder (`_state.sh`). A state folder found inside a linked git worktree
is mapped to the same folder in the main checkout, so every worktree reads and writes one board.

## Verbs

What each verb does is in `W/SKILL.md` § Tracker; this table holds only the arguments, which differ per backend.

| Verb | Jira arguments | Local arguments |
|---|---|---|
| `search` | `'<JQL>' [fieldId,…]` | `'<query>' [name,…]` (below); an unreadable card is skipped with a `WARN` on stderr |
| `get` | `KEY` | `KEY` |
| `card` | `KEY [fieldId,…]` | `KEY [name,…]`: a header field or a body section |
| `edit` | `KEY [--dry-run] --add-label L --remove-label L --field ID=JSON --field-md ID=FILE` | `KEY [--dry-run] --add-label L --remove-label L --field NAME=VALUE --field-md HEADING=FILE`; one-line values, no `## ` heading inside a section, `status` only through `transition` |
| `transition` | `KEY <transition id> [fields-json]` / `KEY --list` | `KEY <status>` / `KEY --list` |
| `comment` | `KEY comment.md [commentId]` (→ ADF; warns on a missing player) | `KEY comment.md [cN]` (stays markdown; writes nothing and exits 1 when a video is missing or outside the board; replaces only the loop's own `cN`) |
| `attach` | `KEY FILE…` → prints the media uuid | `KEY FILE…` → prints `KEY/<name>`; never overwrites |
| `download` | `KEY NEW-DIR [ids]` | `KEY NEW-DIR [names]` |

`::video <uuid>` (Jira) or `::video <KEY/name>` (local) in a comment file becomes an inline player in Jira and a
link to the file on the local board. config.md holds every query, status and lane in its backend's own form.

## Local board

Settings in `tracker.env` (no secrets):

| Line | Default | Meaning |
|---|---|---|
| `TRACKER=local` | — | use the local board |
| `LOCAL_BOARD=` | `<DL>/board` | the board folder: absolute, or relative to `DL` |
| `LOCAL_STATUSES=` | `todo,in-progress,need-info,review,ready-for-qa,reopened,done` | the statuses `transition` accepts; `done` is never-use for the loops |

Only `tracker.env` sets these; the same names in the calling shell are ignored.

**A card** is `<board>/<KEY>.md`, for example the card `TASK-12`. The file name is the key, so keep one prefix
per repo.
Start from `W/templates/card.md`: a header of `name: value` lines between `---` lines, then `## ` sections, then
`## Comments`.
- `labels:` and `links:` hold comma-separated lists.
- `updated:` is set by every change.
- Any other `name:` is a field that `card` and `search` can read.

Attachments live in `<board>/<KEY>/`.

**Comments** are entries under `## Comments`, each starting `### c<n> · <YYYY-MM-DD HH:MM> · <author>`. The loop
writes as `90north-develop`. A person answers by adding a new entry with the next number and their name: text
written under someone else's entry belongs to that entry, so the loop could not see it as a new answer.

**Queries** are space-separated terms; quote a value that has spaces:

| Term | Matches |
|---|---|
| `status=todo,ready` | the field's value is one of these (case does not matter) |
| `labels=ai-queue` | any of the card's labels is one of these |
| `-labels=ai-processing` | none of them is |
| `severity="Level 4,Level 5"` | values with spaces |
| `age>2h`, `age<30m` | time since `updated` (`m`, `h`, `d`) |
| `sort=rank`, `sort=-updated` | order; the default is `rank` (cards without one last), then key |

Examples:
- open defects: `type=bug status=todo,reopened`
- ready for dev: `type=story,task,improvement status=todo`
- the auto-mode queues: `labels=ai-queue -labels=ai-processing type=bug status=todo,reopened` (n-defect-loop) and `labels=ai-queue -labels=ai-processing -type=bug status=todo,reopened` (n-develop-loop), each plus its hand-off query, e.g. `labels=ai-to-develop -labels=ai-processing status=todo,reopened`
- its stale locks: `labels=ai-processing age>2h`
- reopened after an AI fix: `labels=ai-do-now status=reopened`

**Committed board.** When the board is committed, every pass leaves card edits uncommitted in the main checkout.
- The loop never commits or pushes them.
- The run report (S6 step 4) lists the changed card files, and a person commits them, the same as `knowledge/`.
- Cards are never edited on a feature branch: `_state.sh` points the scripts at the main checkout.
- Writes are atomic and keep the file mode. One writer at a time, which the loops' pass lock keeps.

**Fields.** On a local board, config § Auto mode names fields by header name (`severity`) or by section heading
(`acceptance-criteria`), never by `customfield_` id.

**Refusals, both backends.** A call that cannot be done prints one line on stderr and exits 1; wrong usage exits 2.
- Every argument is checked before anything is read, written or requested: an issue key has the shape `ABC-12`, an
  id is digits, a field id is a name, and on Jira free text such as a query is URL-encoded, never joined into the
  URL. A bad value exits 2 with no request made.
- A card or an attachment that is a link leaving the board folder is refused.
- `attach` on Jira exits 1 when Jira refused any of the files; the others are still uploaded.
- `tracker.env` and the Jira credentials file are read as text, one `NAME=value` per line, and never run: a
  `$VARIABLE` or `$(command)` in a value stays text, and only a leading `~/` in a path is expanded. The Jira site
  and the credentials path come from `tracker.env` only, never from the calling shell.

## Sources

- `W/scripts/tracker.sh`, `_state.sh`, `local_board.py`, `local_board_core.py`
- Tests: `W/scripts/tests/test_tracker.py`, `test_local_board_core.py`
- Design note: `research/90north-develop/design-no-jira-tracker.md` in the north-ai-skills repo
