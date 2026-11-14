# north-ai-skills

Agent skills by North. Each skill lives in `skills/<name>/` with a `SKILL.md` entry point.

| Skill | What it does |
|---|---|
| [`design-atlas`](skills/design-atlas/SKILL.md) | UX/UI design hub for web, mobile and desktop apps: user research and design psychology, creative direction (concept → storyboard → signature effect), style and theme selection, palettes matched to a logo, design systems with an expression layer and `light-dark()` theming, designing from the subject's own material so the result does not read as AI-made (tells, the replacement trap, a four-test audit), a visual-craft finish pass (light, type, optical detail, the beauty bar), multi-script typography, motion, scroll and parallax with a job, 3D (three.js), tested cinematic effect demos and AI-generated (Higgsfield) hero media. Language- and market-neutral. |
| [`n-dev`](skills/n-dev/SKILL.md) | Structured development: design before code, modular and functional modules, reuse before writing, new behaviour in extension files beside existing code, state with one owner, test-first, at most one question round before the first edit and a finish gate before the report, plus a git-based structure check (wiring budget, file/function budgets, copied blocks, layer rules, weakened tests, new dependencies) for any language, and an eval suite. |
| [`n-arch`](skills/n-arch/SKILL.md) | Architecture profile: maps how a repo is built (shape, layers and import directions, extension recipes, state owners, contracts, commands, budgets) into `docs/architecture/profile.md` and the `.ndev.toml` the n-dev check enforces; refreshes it as the code moves; audits structural debt and hot spots. |
| [`workflow`](skills/workflow/SKILL.md) | Map and router of the 90north-develop plugin: which loop a piece of work belongs to, the 9 steps and the shared stages both loops run (isolate, review + QA, evidence video, ship, learn), the auto mode both loops run with `--auto`, core lessons and the tracker (Jira or a local board). |
| [`n-defect-loop`](skills/n-defect-loop/SKILL.md) | Defect loop: 9 steps per defect — read the board, triage, check the spec, reproduce (red e2e + before video), root cause at `path:line`, test-first fix with n-dev, verify + record (review + QA, after video), open the PR into the QA lane, then merge only a low-impact change inside a standing approval, else a person approves. Attended, or unattended with `--auto`. Needs the plugin. |
| [`n-develop-loop`](skills/n-develop-loop/SKILL.md) | Development loop for new features and changed requirements: the same 9 steps, with the middle being acceptance spec red, the n-dev design note and work packages (a gate for Large or schema/interface changes), and a test-first build by subagents; the PR goes to the review lane. Attended, or unattended with `--auto`. Needs the plugin. |
| [`develop-init`](skills/develop-init/SKILL.md) | Once per repo: discovers the stack, reads the board's ids and lanes for stories and defects (or sets up a local board when there is no Jira), writes `.claude/90north-develop/` for both loops. |

## Install

Pick a path. **A** for the development loops, **B** for the standalone skills (`design-atlas`, `n-dev`), or both.

| You want | Use |
|---|---|
| n-defect-loop, n-develop-loop, develop-init, workflow, n-dev and n-arch, plus the loops' agents | **A. Plugin** |
| design-atlas, n-dev and/or n-arch in every project | **B. Personal skills** |
| a skill in one repo only, shared with that repo's team | **C. Project skills** |

Then restart Claude Code (or start a new session) and type `/`. The skills show up as slash commands.

### A. Plugin: 90north-develop (recommended for the loops)

Inside Claude Code:

```
/plugin marketplace add ThanaphatNorth/north-ai-skills
/plugin install 90north-develop@north-ai-skills
```

Or from a terminal:

```bash
claude plugin marketplace add ThanaphatNorth/north-ai-skills
```

```bash
claude plugin install 90north-develop@north-ai-skills
```

The commands are namespaced: `/90north-develop:workflow`, `/90north-develop:develop-init`, `/90north-develop:n-defect-loop`, `/90north-develop:n-develop-loop`, `/90north-develop:n-dev`, `/90north-develop:n-arch`. In each repo where you use the loops, run `/90north-develop:develop-init` once. See the [plugin README](plugins/90north-develop/README.md) for what each loop does and where it stops for you.

| Task | Command |
|---|---|
| Update | `claude plugin marketplace update north-ai-skills`, then `claude plugin update 90north-develop@north-ai-skills` |
| Check what's installed | `claude plugin list` |
| Remove | `claude plugin uninstall 90north-develop@north-ai-skills` |

Install the whole plugin. Linking `n-defect-loop` or `n-develop-loop` on its own leaves out the agents and the sibling skills the loops depend on. Moving from 0.6 or earlier (`dev-loop`, `defect-loop`, `n-loop`): see the plugin README's migration table.

### B. Personal skills: every project on this machine

Clone once, then link the skills you want into `~/.claude/skills/`:

```bash
git clone https://github.com/ThanaphatNorth/north-ai-skills.git ~/north-ai-skills
```

```bash
mkdir -p ~/.claude/skills && for s in design-atlas n-dev n-arch; do ln -sn ~/north-ai-skills/skills/$s ~/.claude/skills/$s; done
```

Drop any name from `design-atlas n-dev n-arch` you don't want; n-arch's audit uses n-dev's script, so link both. The commands are `/design-atlas`, `/n-dev` and `/n-arch`. `ln -sn` refuses to overwrite: if it says `File exists`, that name is already taken in `~/.claude/skills/`. An earlier install of this repo is fine to leave; anything else, rename or remove it first.

| Task | Command |
|---|---|
| Update (the links pick it up at once) | `git -C ~/north-ai-skills pull` |
| Check the links | `ls -l ~/.claude/skills/` |
| Remove one skill (deletes only the link) | `rm ~/.claude/skills/n-dev` |

If you have the plugin (A) and a personal `n-dev` (B), both load as `/90north-develop:n-dev` and `/n-dev`. Keep one.

### C. Project skills: one repo, committed with it

Copy the folder into the project, so teammates get it from git without installing anything:

```bash
mkdir -p .claude/skills && cp -R ~/north-ai-skills/skills/n-dev .claude/skills/
```

A copy does not update itself. Copy it again after a `git pull` here.

### Requirements

The skills are Markdown and load with no extra setup. Only their helper scripts need tools:

| Skill | Script | Needs |
|---|---|---|
| n-dev | `scripts/structure_check.py` | Python 3.8+ and git (stdlib only) |
| n-dev | `evals/` | Claude Code with `claude plugin eval`, Node 22+ for the JS fixtures |
| n-arch | (uses n-dev's script) | n-dev linked beside it |
| design-atlas | `scripts/palette.py` | Python 3.8+, plus Pillow for PNG/JPG logos (`pip install pillow`) |
| design-atlas | `scripts/shoot.mjs`, `scripts/scrollfilm.mjs` | Node 22+ and Google Chrome (ffmpeg for `--mp4`) |
| plugin loops | `skills/workflow/scripts/tracker.sh` (+ `jira-*.sh`, `local_board.py`) | bash, python3; for Jira also curl and an API token in `~/.config/<project>-jira.env`, created with `skills/workflow/scripts/jira-login.sh` in your own terminal (`develop-init` tells you when); a local board needs nothing else; `gh` for PRs, and an e2e runner (Playwright or Cypress) in the target repo for repros and videos |

## Layout

```
skills/design-atlas/
  SKILL.md            process + routing (loaded when the skill fires)
  references/*.md     knowledge, loaded on demand
  templates/          brief, persona/JTBD, usability script, starter tokens (themed roles + expression layer), Tailwind v4 mapping
  scripts/palette.py  logo or hex -> OKLCH scales, light-dark() tokens, contrast report
  scripts/shoot.mjs   headless-Chrome screenshots + layout/a11y probes for design QA
  scripts/scrollfilm.mjs  scroll-through film (mp4) + frame scan for scroll stories
  examples/<slug>/    tested cinematic effects (light trail, spotlight, particles, shader...) to adapt,
                      plus craft-finish: a page designed from its subject (an invoice book), with scroll and parallax that have a job
skills/n-dev/
  SKILL.md            four rules, scope dial, one question round, seven steps with completion criteria
  references/*.md     structure, extension, state (single source of truth), security, performance
  templates/design-note.md  module map, state ownership, extension plan, test seams
  references/change-safety.md  contracts, migrations, rollout, failure modes, signals (Large work)
  scripts/structure_check.py  git-based structure gate (stdlib only), reads .ndev.toml, --all audits
  evals/              fixed tasks graded with and without the skill (claude plugin eval)
skills/n-arch/
  SKILL.md            create / refresh / audit a repo's architecture profile
  references/archetypes.md  11 architecture shapes: signals, layers, seams, state, contracts
  templates/          profile.md, ndev.toml
skills/workflow/
  SKILL.md            flow map, router, handoffs, per-repo state
  references/stages.md        shared stages S0-S6 + dispatch safety block
  references/auto-*.md        the auto mode both loops run with --auto (pass, triage, ship classes, record, knowledge)
  references/core-lessons.md  rules from real runs, both loops
  references/trackers.md      the tracker verbs, Jira vs local board, card format, query form
  references/feature-docs.md  feature docs: one per area, rules + sources, rule → test, decisions; kept true in every PR
  templates/card.md           a local-board card
  templates/feature-doc.md    a feature doc
  scripts/tracker.sh, _state.sh  one door to the tracker: TRACKER=jira | local
  scripts/jira-*.sh, md2adf.py  Jira backend (REST v3)
  scripts/local_board*.py     local board backend (markdown cards)
skills/n-develop-loop/
  SKILL.md            development loop: 9 steps, attended and --auto, and its gates
  templates/jira-comment.md   3-section comment: what was built, how it works, verification
skills/n-defect-loop/
  SKILL.md            defect loop: 9 steps, attended and --auto
  references/core-lessons.md  triage and reproduction rules from real sweeps
  templates/jira-comment.md   3-section comment: reproduced?, root cause, solution
skills/develop-init/
  SKILL.md            per-repo setup for both loops; templates/config.md, templates/tracker.env
plugins/90north-develop/  plugin manifest, agents, hooks (the session-start line, the command guard), evals, symlinks to the skills above
.claude-plugin/marketplace.json  this repo as a plugin marketplace
research/<skill>/     raw research notes with sources (provenance, not loaded by the skill)
tools/validate_skill.py   one skill: frontmatter, referenced files, reference shape, source URLs
tools/check_repo.py       the whole repo: versions, registered agents, plugin links, README table,
                          paths and § references that must resolve, ledger states, agent names
tools/repo_check/         the checks behind check_repo.py, one module per concern
tools/consistency-review.md  the brief for the review a machine cannot do: files that now disagree
tools/tests/              tests for both tools
```

## Check a skill

```bash
python3 tools/validate_skill.py skills/design-atlas --urls --report .logs/urls.tsv
```

## Check the repo

One command for what used to be kept in sync by hand. It exits 1 when a version, a registered agent, a plugin link,
a path or a `§` reference no longer matches:

```bash
python3 tools/check_repo.py
```

The script tests, each from the repo root:

```bash
python3 -m unittest discover -s skills/n-dev/scripts/tests -p 'test_*.py'
```

```bash
python3 -m unittest discover -s skills/workflow/scripts/tests -p 'test_*.py'
```

```bash
python3 -m unittest discover -s tools/tests -p 'test_*.py'
```

```bash
python3 -m unittest discover -s plugins/90north-develop/hooks/tests -p 'test_*.py'
```

Two files that now say different things are not something a script can see. After a change to a skill, an agent or
a shared reference, run the brief in `tools/consistency-review.md` with a fresh-context reviewer.

## Structure check (n-dev)

```bash
python3 skills/n-dev/scripts/structure_check.py --repo path/to/repo --base main
```

Reports pre-existing files that gained more than a wiring diff, new or grown files and touched functions over budget, and added blocks that repeat existing code. Files and functions already over budget at the base ref are listed apart as existing debt and do not fail the check. Exit 0 clean, 1 findings, 2 error. Tests: `python3 -m unittest discover -s skills/n-dev/scripts/tests -p 'test_*.py'`.

## Palette from a logo

```bash
python3 skills/design-atlas/scripts/palette.py build --logo path/to/logo.png --out palette-out
```

Writes `tokens.css`, `tailwind-theme.css`, `tokens.json` (DTCG), `palette-report.md` and `preview.html`. Needs Python 3.8+ and Pillow for raster logos.

## Screenshots and layout probes (design QA)

```bash
node skills/design-atlas/scripts/shoot.mjs http://127.0.0.1:8000/ shots --widths 320,390,768,1280
```

Full-page PNGs per width plus JSON probes (overflow, content invisible after scrolling, small targets, lang, h1, alt, console errors). Add `--dark` / `--reduced` for the other modes. Needs Node 22+ and Google Chrome.

## Cinematic examples and scroll films

```bash
python3 -m http.server 8000
```

Then open `http://127.0.0.1:8000/skills/design-atlas/examples/light-trail/` (each example is one standalone `index.html`). To render a scroll-through film of a scroll story:

```bash
node skills/design-atlas/scripts/scrollfilm.mjs "http://127.0.0.1:8000/skills/design-atlas/examples/light-trail/?capture" film --story "#story" --mp4 film.mp4 --scan scan.png
```
