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

## Cases

| Case | Task | What it checks | n-dev rule |
|---|---|---|---|
| `01-coupon-js` | add coupons to a JS checkout, acceptance spec given | spec kept as written, coupon rules outside `checkout.js`, a new coupon module, red before green, honest report | 1, 2, 4 |
| `02-layered-js` | add a route to a hexagonal repo with `docs/architecture/profile.md` and `.ndev.toml` | no handler imports storage, a new use case, the profile actually read (not just quoted), layer check reported | profile, layers |
| `03-bugfix-python` | a support bug report, no test | cause removed, fix correct, regression test red first, cause named | steps 4–5 |
| `04-red-suite-python` | add a function while an unrelated test is already red | the red test and its code untouched and not skipped, report says the suite is not all green | 4 (test integrity, honesty) |
| `05-reuse-js` | email validation where `isEmail` already exists | no dependency added, existing validator reused, no second validator, spec kept | 1 (reuse, verify from source) |
| `06-no-fire-question` | a git question, no code | n-dev does not fire (other skills may); the question is answered correctly | trigger precision |

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
