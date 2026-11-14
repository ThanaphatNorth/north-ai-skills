# Auto mode — scheduled task

Register once per loop and repo. Do it only after `/90north-develop:develop-init` has written config § Auto mode
and a few hand runs look right. `<loop>` is `n-defect-loop` or `n-develop-loop`.

| Where | How |
|---|---|
| Claude desktop scheduled task | ask Claude to create a scheduled task with the prompt below and the cron from config § Auto mode › Schedule for that loop (default `*/30 * * * *` for defects, `15,45 * * * *` for development, local time). It runs only while the app is open on that machine. |
| A session that stays open | `/loop 30m /90north-develop:<loop> --auto` |

Start with `--dry-run`. Remove it after 2–3 dry passes read well on the board.

```text
Working directory: <absolute repo root, the folder that holds .claude/90north-develop/ and .90north-develop/>
The 90north-develop plugin is installed. Run /90north-develop:<loop> --auto --dry-run
Each run starts fresh: read the config, lessons.md and knowledge/ from the two folders the skill's where.sh prints;
do not rely on memory of earlier runs. Append the pass report to runs/<YYYY-MM-DD>/run.md in the working-state folder.
Reply in <the user's language>. Push or merge only inside the standing approval written in config § Push policy;
anything else waits for the user.
```

One schedule per loop per board. Before registering, check two things (`CronList`, or the desktop app's
scheduled-task list):
- no other schedule runs the same loop on the same board;
- no other tool locks the same queue.

The two loops may both be scheduled. Their passes never overlap, because they share the pass lock
(`DL/runs/.pass.lock`). Offset their crons so neither always waits.
