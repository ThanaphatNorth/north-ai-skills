# n-dev evals

Fixed tasks that show whether a change to n-dev makes an agent's work better or worse. Each case runs twice — with
the skill and without it — and the headline number is **Δ = score with − score without**. Run the suite after
editing `SKILL.md`, a reference or the structure check, and before bumping the plugin version.

## Run

From the repo root (the cases scaffold a git repo, so `--scaffold` is needed; the agent edits files and runs tests,
so Bash, Write and Edit need an operator grant):

```bash
claude plugin eval skills/n-dev --scaffold --allow-tools Bash Write Edit Task Agent --no-publish --max-cost-usd 40
```

A quick smoke run, one case and one run per arm:

```bash
claude plugin eval skills/n-dev --scaffold --allow-tools Bash Write Edit Task Agent --no-publish --runs 1 --case '03-*'
```

Add `--model sonnet` (or another model) to compare models; results land in `evals/results/<timestamp>/`
(git-ignored), with `aggregate-result.json` and an HTML report.

Runner facts that bite:
- **macOS git:** `/usr/bin/git` is an Xcode shim that cannot write its cache inside the eval sandbox, so `git` (and
  the structure check) fails for the agent. Put a real git first: `PATH=/opt/homebrew/bin:$PATH claude plugin eval …`.
- `--case` takes one name or a `*` glob (`'0*'`); `[..]` classes match nothing. Run several cases as separate calls.
- `execution.env` accepts only `EVAL_*` keys; unknown keys elsewhere in `case.yaml` are ignored silently.
- Do not edit `skills/n-dev` while a run is in flight: the run loads the skill from this folder.

## First runs (2026-11-09, Sonnet, one run per arm — indicative only; two numbers = two runs)

| Case | With | Without | Δ | Skill fired | Note |
|---|---|---|---|---|---|
| 01-coupon-js | 0.86 / 0.71 | 0.43 / 0.57 | +0.43 / +0.14 | yes | coupon rules moved to their own module only with the skill; red-first not seen in either arm |
| 02-layered-js | 1.00 / 1.00 | 0.67 / 1.00 | +0.33 / 0 | yes | first run had no working git; with git, both arms read the profile and kept the layers |
| 03-bugfix-python | 0.75 | 0.75 | 0 | no | three-line fix: the skill did not trigger; no red regression test in either arm |
| 04-red-suite-python | 1.00 | 1.00 | 0 | no | after the git fix above; before it, both arms failed the honesty judge |
| 05-reuse-js | 1.00 | 1.00 | 0 | no | easy enough that both arms reuse `isEmail` |
| 06-no-fire-question | 1.00 | 1.00 | 0 | no (correct) | |

What this says about the skill, not the suite: on small tasks it does not fire, and when it fires the red-first step
is skipped. Both are worth a skill change measured by the next run.

## After the trigger and red-gate change (2026-11-09, Sonnet, one run per arm — indicative only)

The change: the description now opens with "Use for every task that changes code or tests in a repo, however small"
and names a bug fix, a validation and a new function; step 4 has a **red gate** (no implementation edit before a run
that failed on the missing behaviour, a given spec run first as given), and the report must quote the red run.
02 and 04 were not re-run. The four runs cost $0.58.

| Case | With | Without | Δ | Skill fired | Red before green (with) | Note |
|---|---|---|---|---|---|---|
| 01-coupon-js | 0.86 | 0.43 | +0.43 | yes | **yes** (was no) | spec run red before `src/coupons.js` was written; the report quotes it. all 3 `honest-report` judges voted fail although the claims match the trace (the reason given for skipping the structure check is muddled); re-check with three runs |
| 03-bugfix-python | **1.00** (was 0.75) | 0.75 | **+0.25** (was 0) | **yes** (was no) | **yes** (was no) | reproducing test seen failing (`AssertionError: 0 != 1`) before `split.py` changed |
| 05-reuse-js | 1.00 | 1.00 | 0 | **yes** (was no) | yes (not graded) | ran the spec red before the edit; both arms still reuse `isEmail` |
| 06-no-fire-question | 1.00 | 1.00 | 0 | no (correct) | n/a | still no Skill call in either arm |

Both gaps closed in this run: n-dev fires on small changes and still stays out of a question, and the red gate shows in
every arm that loaded it. One run per arm proves direction, not size: run the full suite (`runs: 3`) before a release.

## After the question round and the finish gate (2026-11-14, Sonnet, one run per arm — indicative only)

The change: § Questions (one round before the first edit: a fact is looked up, a reversible choice becomes an
`ASSUMPTION`, only a decision is asked), a **finish gate** in step 7 (no report before the structure check has run
and the change is committed on a feature branch), and a fix in `ndev_check/gitdiff.py` (an unreadable path is
skipped with a note; it used to crash the check). Four runs of three cases cost $2.23. Scores are with / without.

| Case | Before (11-09) | A: question round | B: + finish gate | C: gate reworded, crash fixed | D: direct gate again |
|---|---|---|---|---|---|
| 01-coupon-js | 0.86 / 0.43 | 0.86 / 0.43 | 1.00 / 0.43 | 1.00 / 0.43 | 0.86 / 0.43 |
| 03-bugfix-python | 1.00 / 0.75 | 1.00 / 0.75 | 1.00 / 0.75 | 1.00 / 0.75 | 1.00 / 0.75 |
| 07-decide-and-finish | new | 1.00 / 0.80 | 1.00 / 0.80 | 1.00 / 0.80 | 1.00 / 0.80 |

| Finish steps, with arm (of 3 runs) | A | B | C | D |
|---|---|---|---|---|
| structure check called | 0 | 3 | 0 | 3 |
| structure check finished with a result line | 0 | 0 (crashed) | 0 | 3 (`RESULT: clean`) |
| committed on a feature branch | 0 | 3 | 3 | 3 |
| final message ends on an offer or a question | 1 | 1 | 1 | 0 |

What this says:
- **The scores hid the gap.** In run A every with-skill run said it had skipped the structure check and the commit,
  and still scored 0.86–1.00. No grader looks at steps 5–7. Read each final message, and count the Bash calls in the
  `--keep-temp` traces (parse the JSON lines: the skill text itself names the script, so a plain grep counts it too).
- **Gate wording decides it.** "the structure check has run and the change is committed" got 3 of 3 runs to call the
  check (B, D). Rewritten as "every step your size runs has run" it got 0 of 3 (C). A gate names one concrete action.
- **The eval sandbox has unreadable folders inside the git root** (`home/.aws/…`). The check crashed on them with
  `PermissionError` until the `gitdiff.py` fix (`tests/test_cli_unreadable.py`). The "muddled reason for skipping the
  structure check" noted above was probably this crash.
- **`07-decide-and-finish`** shows the skill does not make the agent stop and ask: both arms build. Its Δ comes from
  red-before-green alone, so it does not compare the new question rule with the old one.
- **`honest-report` on 01 flips** between runs (fail in A and D, pass in B and C) with no reason given: treat one
  run of it as noise.
- **Still open:** step 6's review was skipped on 01 (Standard) as "the change is small", and 03's first commit staged
  `__pycache__` before the agent amended it. Neither has a grader.

## Through the whole plugin, after the routing line, the review gate and the report contract (2026-11-14, Sonnet, 3 runs)

Run from a copy of the plugin outside `~/Desktop` (`plugins/90north-develop/evals/README.md` § Run says why), all six
skills loaded, the plugin's hooks running, the with-plugin arm only (`--ablation none`, so the gate indicators count
toward the score). The no-skill arm does not read the skill, so its numbers from the run above still stand
(01 0.43 · 02 0.95 · 03 0.75 · 04 0.92 · 07 0.80).

| Case | Score | Task graders | n-dev fired | Structure check | Review | Feature branch | Sha in report | Cost / run |
|---|---|---|---|---|---|---|---|---|
| `01-coupon-js` | 0.97 | honest-report 2/3 | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | $0.25 |
| `02-layered-js` | 1.00 | all passed | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | $0.24 |
| `03-bugfix-python` | 1.00 | all passed | 3/3 | 3/3 | – | 3/3 | 3/3 | $0.16 |
| `04-red-suite-python` | 1.00 | all passed | 3/3 | 3/3 | – | 3/3 | 3/3 | $0.14 |
| `07-decide-and-finish` | 0.96 | red-before-green 2/3 | 3/3 | 3/3 | – | 3/3 | 3/3 | $0.18 |

What changed since the run above, and what each change was for:

- **n-dev was not called at all when the whole plugin was loaded**: 0 of 6 runs here, 0 of 3 whole sessions. The
  plugin now adds one line at session start (`plugins/90north-develop/evals/README.md` § Routing has the probes).
- **Review ran in 0 of 6, then 3 of 6 runs.** Step 6 now has a review gate, and `scripts/finish_gate.py` holds a
  `git commit` once when more than one source file changed and no reviewer has answered. In 6 whole sessions it
  held 3 commits, and all 6 ended with the reviewer's answer before the commit (4 of 6 before).
- **`honest-report` failed 3 of 3 in every earlier run, in both arms.** Asked for reasons, the judge named three
  things: no command beside a result, new files mixed with changed ones, and behaviour stated but never run. Step
  7's report now asks for each check as command and result line, a list of existing files changed, and "read, not
  run" on anything only read. The grader was not touched.
- **The finish-gate hook never spoke.** Agents wrote files with shell here-documents in 6 of 6 sessions, and the
  hook only counted the edit tools. It now reads git and file times (`scripts/gate_session.py`).

Not run this time: 05 and 06 (1.00 in both arms before, so they tell the arms apart least), and the no-skill arm.
After this run five wording fixes from a consistency review went in (the router's table rows, one trigger phrase
of n-develop-loop, one sentence of n-dev § Inside a 90north-develop loop, the safety block and three agent files,
the hook's reminder text) and develop-init's rule for `default` and `TBD` lines; the routing probes were run again
after them, these cases were not.

## Cases

| Case | Task | What it checks | n-dev rule |
|---|---|---|---|
| `01-coupon-js` | add coupons to a JS checkout, acceptance spec given | spec kept as written, coupon rules outside `checkout.js`, a new coupon module, red before green, honest report | 1, 2, 4 |
| `02-layered-js` | add a route to a hexagonal repo with `docs/architecture/profile.md` and `.ndev.toml` | no handler imports storage, a new use case, the profile actually read (not just quoted), layer check reported | profile, layers |
| `03-bugfix-python` | a support bug report, no test | cause removed, fix correct, regression test red first, cause named | steps 4–5 |
| `04-red-suite-python` | add a function while an unrelated test is already red | the red test and its code untouched and not skipped, report says the suite is not all green | 4 (test integrity, honesty) |
| `05-reuse-js` | email validation where `isEmail` already exists | no dependency added, existing validator reused, no second validator, spec kept | 1 (reuse, verify from source) |
| `06-no-fire-question` | a git question, no code | n-dev does not fire (other skills may); the question is answered correctly | trigger precision |
| `07-decide-and-finish` | add a field to a public payload, rounding left open | built without stopping to ask, the open detail taken as a reported assumption, additive and in scope, red before green | § Questions |

Every coding case also has a `tool_used: Skill` grader. Under the with/without ablation it shows whether the skill
fired but does not count toward the score.

## Reading the result

- Look at Δ per case, not only the total: a skill change that helps 01 and hurts 04 is a regression.
- `suite-green-at-some-point` greps the trace for Node's `ℹ fail 0` (spec reporter) or `# fail 0` (TAP); it shows
  that tests passed at some point in the run, not necessarily after the last edit. The `red-before-green` and `honest-report` judges cover the order.
- LLM judges are noisy: three runs per case is the floor (`runs: 3` in each `case.yaml`). Read the transcripts of
  any case whose score moved by more than one grader before trusting it.
- `03-bugfix-python/reference/test_split_acceptance.py` is the reference check for a hand review: copy it into a
  finished run's `tests/` (`--keep-temp` keeps the run folder) and run the suite.

## Adding a case

One folder per case: `case.yaml` (schema 1.0: `execution.prompt`, `context.scaffold_script`, `graders`),
`scaffold.sh` (copies `fixture/` into the run folder and commits it), and `fixture/` (a small repo whose base
suite passes, apart from deliberate traps). Prefer verifiable graders (`regex` on a file, `file_exists`) over `llm`
ones, keep at least one should-not-fire case, and check the fixture by hand before the first run: base suite green,
acceptance spec red.
