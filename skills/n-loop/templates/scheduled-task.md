# n-loop — scheduled task

Register once per repo, after `/90north-develop:develop-init` has written config § AI loop and a few hand runs look right.

| Where | How |
|---|---|
| Claude desktop scheduled task | ask Claude to create a scheduled task with the prompt below and the cron from config § AI loop › Schedule (default `*/30 * * * *`, local time). It runs only while the app is open on that machine. |
| A session that stays open | `/loop 30m /90north-develop:n-loop` |

Start with `--dry-run`. Remove it after 2–3 dry passes read well on the board.

```text
Working directory: <absolute repo root, the folder that holds .claude/90north-develop/>
The 90north-develop plugin is installed. Run /90north-develop:n-loop --dry-run
Each run starts fresh: read .claude/90north-develop/config.md, lessons.md and knowledge/ as the skill instructs;
do not rely on memory of earlier runs. Append the pass report to .claude/90north-develop/runs/<YYYY-MM-DD>/run.md.
Reply in <the user's language>. Push or merge only inside the standing approval written in config § Push policy;
anything else waits for the user.
```

Only one schedule may run per board. Before registering, check that no other loop locks the same queue (`CronList`, or the desktop app's scheduled-task list).
