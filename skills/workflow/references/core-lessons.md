# Core lessons — both loops (every project)

> Read when: S0 of either loop (`stages.md`), in full, together with the flow's own core lessons and the project's `.claude/90north-develop/lessons.md`; and when a project lesson might belong to every repo.

Distilled from real runs. A project lesson that would help any repo in both flows is promoted here; one that only concerns defects goes to `defect-loop/references/core-lessons.md` (edit the plugin source, bump the plugin version, `/plugin update`).

## Finding the work
- Query statuses and issue types **by id**, never by name — the name form once returned 1 of 17 open bugs with no error. Sanity-check the count against `statusCategory != Done`.
- Every tick runs the **full** open-work query of its flow — board **and backlog** (no sprint filter) — and diffs the keys against the ledger. A `created/updated >= -Nm` window is never the whole check (3 new defect cards sat ~2 h unseen that way).
- A ticket parked "until PR #N merges" is re-checked every tick (`gh pr view N --json state`); MERGED → resume it.
- Reporters rewrite tickets. Before commenting or shipping, re-read summary + description, map each fix to the ticket's **current** points, and never cite a ticket for points it no longer contains.
- Atlassian MCP connectors can lose access mid-session (403 "app is not installed", or only one of two connectors sees the site) → the bundled REST scripts with the token file always work.

## Building and fixing
- Builders and fixers never install tools or browsers; a missing tool is a reported gap.
- Builders and fixers never start, restart or boot app processes and never point anything at a DB. One analysis agent booted a second API with different env flags and its boot hook deleted shared data. Every brief says this.
- Linters that run `--fix` rewrite files → `git diff` must be clean after lint.
- Data migrations: prove they apply on an **empty** DB (migration folders may sort as text: `19_` before `2_`), and run them on a QA **copy** of a shared DB, never the shared DB itself. No DELETE/TRUNCATE.

## Verifying
- Run review and QA in parallel, but never edit a worktree while another agent is testing it — queue the fix round until both report.
- A 5 s unit-test timeout in a file the branch doesn't touch, while several agents run suites, is machine load → rerun that file alone and the suite once idle; report both runs.
- When a claim looks too good, send it to an adversarial verifier.

## Evidence and Jira
- Videos must play **inline** in the comment (user correction): H.264 MP4 (`-pix_fmt yuv420p -movflags +faststart -an`), upload, take the media uuid from the attachment content redirect, embed as ADF mediaSingle, verify via renderedBody. Attachments alone are not enough.
- The "after" clip must hold each proving state ~1.5 s; a fast spec run ends before the screencast catches it. Re-record when a later fix round changes the behaviour shown.
- Write comment files with a quoted heredoc or the Write tool; an unquoted heredoc ran every `backtick path` as a command and posted the comment with blanks. `jira-comment.sh` warns when a code span is missing.
- Credentials file: chmod 600, never cat or print it; the token goes to curl on stdin.

## Environment
- Preview servers: `sh -c "… && node app"` can orphan the child on stop and keep the port → use `exec node …` in launch configs; after stopping, check the port with `lsof` and kill only an exact PID whose cwd is our worktree.
- The preview tool caps servers per folder (5, shared with other chats) → budget: one stack shared by reproductions on unchanged code, one per ticket under QA; stop a ticket's servers as soon as its QA ends.
- zsh: `"${R}:path"` (not `$R:path`, a history modifier); `${V}[a]` (not `$V[a]`, an array subscript).
- Other sessions may clean up worktrees whose branch has no commits → commit an empty anchor right after creating one and squash it before pushing (`git reset --soft <merge-base>` + one commit — local, unpushed only).
- Squash or reword only local, unpushed commits; never force-push.

## Sources

- Distilled from the author's own sweeps of a production Jira defect board (2026): each line is a rule that cost a retry, a wrong write or a user correction.
- Jira Cloud REST v3, issue search (`/rest/api/3/search/jql`, `nextPageToken` paging): https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-search/
- Jira Cloud REST v3, issue attachments (`X-Atlassian-Token: no-check`): https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-attachments/
- Atlassian Document Format, structure and the `mediaSingle` node: https://developer.atlassian.com/cloud/jira/platform/apis/document/structure/
