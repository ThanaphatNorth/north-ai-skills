# 90north-develop evals

Fixed tasks that show whether a change to the plugin's skills makes an agent's work better or worse. Each case runs
twice, with the plugin and without it, and the headline number is **Δ = score with − score without**. n-dev has its
own, older suite in `skills/n-dev/evals/`; the plugin target picks those cases up too, through the `skills/n-dev`
link. Run both after editing a skill, an agent or a shared reference, and before bumping the plugin version.

## Run

From the repo root, with a real git first in PATH on macOS (`skills/n-dev/evals/README.md` says why):

```bash
PATH=/opt/homebrew/bin:$PATH claude plugin eval plugins/90north-develop --scaffold --allow-tools Bash Write Edit Task Agent --no-publish --max-cost-usd 15
```

One case, one run per arm:

```bash
PATH=/opt/homebrew/bin:$PATH claude plugin eval plugins/90north-develop --scaffold --allow-tools Bash Write Edit Task Agent --no-publish --runs 1 --case '04-develop*'
```

`--case` is a glob on the case name, and names repeat across the two suites (`01-workflow-route`, `01-coupon-js`):
write enough of the name to pick one. Results land in `evals/results/<timestamp>/` (git-ignored).

Two things a first run trips on:

- **Trust.** The command asks once, in a terminal, whether you trust the plugin folder. A run with no terminal
  (a script, CI) stops there: add `--trust-plugin` when the plugin is yours.
- **Where the plugin lives.** Each run is sandboxed, and on macOS the sandbox cannot read `~/Desktop`,
  `~/Documents` or `~/Downloads`. A plugin kept there loads, but the agent's shell cannot open its scripts
  (`Operation not permitted`), so the structure check and the tracker scripts never run and the cases fail for
  the wrong reason. Run from a copy outside those folders, with the skill links followed:

  ```bash
  rsync -aL --exclude evals/results plugins/90north-develop/ /tmp/90north-develop-eval/
  ```

  then pass `/tmp/90north-develop-eval` as the target. The plugin's hooks run inside the eval, so the session-start
  line and n-dev's gate hook are part of what is measured.

## Routing

Which skill a request reaches first is not something a case scores well, so it has its own probe: start a
one-turn session with the plugin, give it one request, and read the first tool it calls.

```bash
cd <a repo with the board fixture>; printf '%s' '<request>' | claude -p --plugin-dir <plugin> --setting-sources project \
  --model sonnet --allowedTools Skill Read Glob Grep --max-turns 1 --strict-mcp-config --output-format stream-json --verbose
```

`--setting-sources project` keeps your own skills and settings out of the session. About $0.03 a probe on Sonnet.
Run every request three times after a change to any skill's `description` or to `hooks/session-start.txt`.
The last column adds up the runs made for 0.11.0: three per request (four for the first row), and every request a
late description edit could move was run three more times.

| Request | Must reach first | 0.11.0 |
|---|---|---|
| a feature asked for directly (n-dev case 01's prompt) | n-dev | 7/7 |
| a bug described directly, no key | n-dev | 6/6 |
| "Implement this spec: …", no loop named | n-dev | 3/3 |
| "Take this spec through the develop loop: …" | n-develop-loop | 3/3 |
| "Build TASK-1." · "Pick the next story and take it through the develop loop." | n-develop-loop | 12/12 |
| "Run the defect loop on TASK-2." · "Sweep the board and clear the bugs to Ready for QA." | n-defect-loop | 9/9 |
| "Start work on TASK-3. Which loop is that?" | workflow | 6/6 |
| "Set up the dev loop and the defect loop in this repo." | develop-init | 3/3 |
| "Map the architecture of this repo and set its layer rules." | n-arch | 3/3 |
| "What does formatPrice do? Just explain it; change nothing." | no skill | 3/3 |

Why the probe exists. With all six skills loaded and no session-start line, a plain coding request reached no
skill at all: 0 of 4 first calls, and 0 of 3 whole sessions. The same request reached n-dev 3 of 3 times when the
plugin held only n-dev, and when it held n-dev with `workflow` or with `n-develop-loop`; beside the long
`n-defect-loop` description alone it was reached 1 time in 7. The cause was the weight of the sibling descriptions, not
their routing words: with every sibling description cut to one sentence n-dev was reached 3 of 3 times, and with
their routing words aligned but their length kept, 0 of 4. Two changes followed: descriptions say what the skill
is and when to use it (4,766 characters for the six became 2,783), and the plugin adds one line at session start
(`hooks/session-start.txt`, 375 characters). With the line, n-dev was reached 5 of 5 times even with the long
descriptions, so the line is what carries the routing; the shorter descriptions are what every session saves.

## Cases

| Case | Skill | Task | What it checks |
|---|---|---|---|
| `01-workflow-route` | workflow | a ticket typed Bug that asks for behaviour the spec never had | routed to the development loop: the type is a hint, not the answer |
| `02-init-local-board` | develop-init | set the loops up in a repo with no Jira, nobody to answer | config, ledgers and a local board written; defaults and TBDs marked; no placeholder left; no question |
| `03-arch-create` | n-arch | map a layered repo whose README states a rule one file breaks | profile and `.ndev.toml` written; measured with the structure check; the real violation recorded, not hidden; no question |
| `04-develop-asks-once` | n-develop-loop | a ready story, no standing approval to push, the user at the keyboard | steps 1–3 and the design draft, then one question round with the push in it; nothing isolated or built before the answer |
| `05-defect-asks-once` | n-defect-loop | two defects on the board, one clear, one with nothing to reproduce | both triaged, then one question round for the whole sweep; nothing fixed before the answer; the vague card is not guessed |

`_shared/board-repo/` is the fixture the two loop cases start from: a small library with a filled
`.claude/90north-develop/config.md`, and in `.90north-develop/` a local board with three cards and the ledgers. Its base suite passes, and `formatPrice` really
has the bug card TASK-2 describes.

Cases 04 and 05 end where an attended run waits for its answer, so they check that the round comes first and comes
once. Their prompts say that someone is at the keyboard; a plain request is checked in § Whole runs, which also
covers what happens after the answer.

## Whole runs

The cases stop at the question round. What comes after it (isolate, build, verify, ship, learn) is checked by
running a loop in a real session on a copy of `_shared/board-repo/`, with a plain request and no hint that someone
is at the keyboard, and reading the session's transcript, git and the board afterwards. No push: the fixture has no
remote and no standing approval, so a finished item parks at `awaiting-push`.

```bash
cp -R plugins/90north-develop/evals/_shared/board-repo /tmp/run/pricing && cd /tmp/run/pricing && git init -q -b main && git add -A && git commit -q -m base
printf 'Run the defect loop on TASK-2.' | claude -p --plugin-dir <plugin> --setting-sources project --model sonnet --permission-mode acceptEdits \
  --allowedTools Bash Write Edit Read Glob Grep Skill Agent Task --strict-mcp-config --output-format stream-json --verbose > run.jsonl
```

Answer a question round with `claude -p --resume <session id>` and the same flags. For auto mode the copy also needs
config § Auto mode, `knowledge/`, `runs/` and a card labelled `ai-queue`; the request is
`/90north-develop:n-defect-loop --auto [--dry-run]`.

Runs on 0.11.0, when the working state was still under `.claude/` (2026-11-14, Sonnet, one each; the cost is what
the session reported):

| Run | What happened | Ended |
|---|---|---|
| n-defect-loop TASK-2 | worktree, `defect-repro` red, `defect-fixer`, `risk-reviewer` beside QA, comment, ledger through `ledger.sh` | fixed, 3 of 3 tests, `awaiting-push`, nothing pushed · $0.55 |
| n-develop-loop TASK-1 | one question (the push), then after "no": worktree, `dev-builder` red specs, `dev-builder` build, `risk-reviewer` beside QA, comment, ledger | built, 11 of 11 tests, `awaiting-push`, no second stop · $0.71 |
| n-defect-loop `--auto --dry-run` | triage, lock, `defect-repro` red, BEFORE comment, lock released, ledger `dry-run`, six run files | card still queued · the learner was not dispatched · $0.42 |
| n-defect-loop `--auto` | triage, repro, fixer, review beside QA, `loop-verifier` CONFIRMED, comment, `loop-learner` | `awaiting-push` · run files kept outside `DL`, V8 not read, pass lock left behind (below) · $0.99 |
| n-arch `audit` | structure check over the whole repo, two planted imports to prove the rules fire | report only, no file written · $0.12 |

What the first runs showed, and what was changed because of it:

- **A ledger row could not be written.** A shell redirect into `.claude/90north-develop/` is refused in a session
  that asks nobody, like the Write tool; one run stopped there with the fix done and nothing recorded. Ledger rows
  now go through `skills/workflow/scripts/ledger.sh`.
- **One run built first and asked about the push at the end**, and ran no separate QA. `stages.md` § Decision round
  now says what a run does when nobody can be asked, and § S2 makes QA's report a condition for shipping.
- **The cause behind the first point: the working state was under `.claude/`.** In the live auto pass the Write
  tool was refused for the run files, so the conductor kept them in its scratch folder, where the next pass cannot
  find them; the verifier ran before the comment draft existed; and the pass lock could not be removed. In 0.12.0
  the working state lives in `.90north-develop/` beside the project and only the settings stay under `.claude/`.
  `auto-mode.md` § A7 puts the draft before the verifier.

Runs on 0.12.0, the two-folder layout (2026-11-14, Sonnet, one each):

| Run | What happened | Ended |
|---|---|---|
| n-defect-loop `--auto` | triage, repro, fixer, review beside QA, comment draft, `loop-verifier` CONFIRMED, comment, `loop-learner` | run files, the draft, `verify.md` and the learner's files all under `.90north-develop/runs/`; no write refused; lock removed; `awaiting-push` · $1.04 |
| n-defect-loop TASK-2 | one question (the push), then after "no": repro, fixer, review beside QA, comment, ledger | fixed, 2 of 2 tests, `awaiting-push`; card and ledger in `.90north-develop/`; no write refused · $0.76 |
| `move-state.sh` on an old project | `--dry-run` listed four entries; the run moved both ledgers, the lessons and the board with `git mv` | uncommitted edits kept, settings in place, a second run moved nothing |

In a session that asks nobody, a file under `.90north-develop/` can be written with the Write tool and the pass
lock removed; under `.claude/90north-develop/` both are refused.

A project that has not moved yet, same day (a copy of the fixture with everything back under `.claude/`):

| Run | What happened | Ended |
|---|---|---|
| n-defect-loop `--auto`, before the door | the pass tested its write with a shell variable, which went through, wrote the lock and took the card; later the Write tool was refused for `review.md` and `verify.md`, and so were the ledger row and the removal of the lock | fix on a local branch, verifier refuted two claims, no ledger row, pass lock left in place, the learner not run · $0.78 |
| n-defect-loop `--auto`, with `where.sh --auto` | the first command exits 3 | the reply names `move-state.sh`; no lock, no card, no file, the card still queued · $0.15 |

So a write that succeeds once proves nothing under `.claude/`: which writes pass depends on how the path is spelled.
An unattended pass now asks `where.sh --auto` first, and the script refuses a working state under `.claude/`: a
project that has not moved, or a legacy `.claude/defect-loop/`.

## Reading the result

- Look at Δ per case, not only the total.
- The `tool_used: Skill` grader shows whether the skill fired; it is not part of the score.
- LLM judges return votes without a reason and are noisy: three runs per case is the floor. Read the final message
  of any run that failed a judge (`--keep-temp` keeps the run folder and its `trace.jsonl`).
- A case that scores 0 without the plugin is expected when the task is about the plugin itself (01).

## Results

See the table at the end of `skills/n-dev/evals/README.md` for n-dev's own cases. Plugin cases, 0.11.0, Sonnet, run
from a copy outside `~/Desktop`:

| Case | With the plugin | Without | Graders lost with the plugin |
|---|---|---|---|
| `01-workflow-route` | 1.00 (1 run) | 0.00 (1 run) | all passed (run before the routing line existed) |
| `02-init-local-board` | 0.75 (3 runs) | 0.00 (1 run) | config-written 1/3; no-jira-placeholders-left 1/3; config-holds-facts-defaults-and-tbd 1/3 |
| `03-arch-create` | 1.00 (1 run) | 0.00 (1 run) | all passed |
| `04-develop-asks-once` | 1.00 (1 run) | 0.50 (1 run) | all passed |
| `05-defect-asks-once` | 1.00 (1 run) | 0.40 (1 run) | all passed |

One run per arm is a first look, not a measurement: cases 03 to 05 need three runs before their numbers mean much.

Case 02 and the `.claude/` folder. The eval runs with nobody to approve a permission, and in such a session the
Write tool is refused for a path under `.claude/`. That is where develop-init writes `config.md`, on purpose: the
file holds the push approval, so a person should see it written. In 3 of the 5 runs made on 0.11 the agent tried
Write for `config.md`, was refused, did not write it another way (which is right) and handed over an unfinished
setup; in the other 2 it wrote the file with a shell command from the start: the first of those lost three graders
(the two corrections below came from it), the second passed every one. The graders were left as they are, so the
case's score shows this: `config-written` passes only when a person could have approved the write, or when the
agent's first attempt was a shell command. Two things were corrected after the first two runs: develop-init's rule
for `default` and `TBD` lines (a judge named a TBD line that did not say what would settle it), and this case's own
placeholder pattern, which flagged `fix/<KEY>-<slug>`, the branch pattern the config template prescribes. The case
has not been run again on 0.12.0, where the ledgers and the board template are written to `.90north-develop/`.
