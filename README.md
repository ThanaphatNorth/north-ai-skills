# north-ai-skills

Agent skills by North. Each skill lives in `skills/<name>/` with a `SKILL.md` entry point.

| Skill | What it does |
|---|---|
| [`design-atlas`](skills/design-atlas/SKILL.md) | UX/UI design hub for web, mobile and desktop apps: user research and design psychology, creative direction (concept → storyboard → signature effect), style and theme selection, palettes matched to a logo, design systems, motion, scroll/parallax, 3D (three.js), tested cinematic effect demos and AI-generated (Higgsfield) hero media. |
| [`n-dev`](skills/n-dev/SKILL.md) | Structured development: design before code, modular and functional modules, reuse before writing, new behaviour in extension files beside existing code, state with one owner, test-first, plus a git-based structure check (wiring budget, file/function budgets, copied blocks) for any language. |
| [`workflow`](skills/workflow/SKILL.md) | Map and router of the 90north-develop plugin: which flow a piece of work belongs to, the shared stages both loops run (isolate, review + QA, evidence video, ship, learn), core lessons and the Jira REST scripts. |
| [`dev-loop`](skills/dev-loop/SKILL.md) | Development flow: one story, task or spec from ready to reviewed PR — ready check, n-dev design note with a gate for Large or schema/interface changes, acceptance spec red first, work packages built test-first by subagents, review + QA, inline demo video, 3-part Jira comment, review lane. Needs the plugin. |
| [`defect-loop`](skills/defect-loop/SKILL.md) | Defect flow: sweeps a Jira defect board end-to-end — triage, red e2e repro, root cause at `path:line`, test-first fix with n-dev, review + QA, before/after videos inline in the Jira comment, PR, QA lane, learn. Needs the plugin. |
| [`develop-init`](skills/develop-init/SKILL.md) | Once per repo: discovers the stack, reads the board's ids and lanes for stories and defects, writes `.claude/90north-develop/` for both loops. |

## Install

Pick a path. **A** for the development loops, **B** for the standalone skills (`design-atlas`, `n-dev`), or both.

| You want | Use |
|---|---|
| dev-loop, defect-loop, develop-init, workflow and n-dev, plus the loops' agents | **A. Plugin** |
| design-atlas and/or n-dev in every project | **B. Personal skills** |
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

The commands are namespaced: `/90north-develop:workflow`, `/90north-develop:develop-init`, `/90north-develop:dev-loop`, `/90north-develop:defect-loop`, `/90north-develop:n-dev`. In each repo where you use the loops, run `/90north-develop:develop-init` once. See the [plugin README](plugins/90north-develop/README.md) for what each loop does and where it stops for you.

| Task | Command |
|---|---|
| Update | `claude plugin marketplace update north-ai-skills`, then `claude plugin update 90north-develop@north-ai-skills` |
| Check what's installed | `claude plugin list` |
| Remove | `claude plugin uninstall 90north-develop@north-ai-skills` |

Install the whole plugin. Linking `dev-loop` or `defect-loop` on its own leaves out the agents and the sibling skills the loops depend on.

### B. Personal skills: every project on this machine

Clone once, then link the skills you want into `~/.claude/skills/`:

```bash
git clone https://github.com/ThanaphatNorth/north-ai-skills.git ~/north-ai-skills
```

```bash
mkdir -p ~/.claude/skills && for s in design-atlas n-dev; do ln -sn ~/north-ai-skills/skills/$s ~/.claude/skills/$s; done
```

Drop either name from `design-atlas n-dev` if you only want one. The commands are `/design-atlas` and `/n-dev`. `ln -sn` refuses to overwrite: if it says `File exists`, that name is already taken in `~/.claude/skills/`. An earlier install of this repo is fine to leave; anything else, rename or remove it first.

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
| design-atlas | `scripts/palette.py` | Python 3.8+, plus Pillow for PNG/JPG logos (`pip install pillow`) |
| design-atlas | `scripts/shoot.mjs`, `scripts/scrollfilm.mjs` | Node 22+ and Google Chrome (ffmpeg for `--mp4`) |
| plugin loops | `skills/workflow/scripts/jira-*.sh` | bash, curl, jq, python3, a Jira API token in `~/.config/<project>-jira.env` (`develop-init` walks you through it), `gh` for PRs, and an e2e runner (Playwright or Cypress) in the target repo for repros and videos |

## Layout

```
skills/design-atlas/
  SKILL.md            process + routing (loaded when the skill fires)
  references/*.md     knowledge, loaded on demand
  templates/          brief, persona/JTBD, usability script, starter tokens
  scripts/palette.py  logo or hex -> OKLCH scales, light/dark tokens, contrast report
  scripts/shoot.mjs   headless-Chrome screenshots + layout/a11y probes for design QA
  scripts/scrollfilm.mjs  scroll-through film (mp4) + frame scan for scroll stories
  examples/<slug>/    tested cinematic effects (light trail, spotlight, particles, shader...) to adapt
skills/n-dev/
  SKILL.md            four rules, scope dial, seven steps with completion criteria
  references/*.md     structure, extension, state (single source of truth)
  templates/design-note.md  module map, state ownership, extension plan, test seams
  scripts/structure_check.py  git-based structure gate (stdlib only)
skills/workflow/
  SKILL.md            flow map, router, handoffs, per-repo state
  references/stages.md        shared stages S0-S6 + dispatch safety block
  references/core-lessons.md  rules from real runs, both loops
  scripts/jira-*.sh, md2adf.py  Jira REST v3: search, get, download, transition, attach, comment
skills/dev-loop/
  SKILL.md            development flow D0-D5 and its gates
  templates/jira-comment.md   3-section comment: what was built, how it works, verification
skills/defect-loop/
  SKILL.md            defect flow F0-F5
  references/core-lessons.md  triage and reproduction rules from real sweeps
  templates/jira-comment.md   3-section comment: reproduced?, root cause, solution
skills/develop-init/
  SKILL.md            per-repo setup for both loops; templates/config.md, templates/tracker.env
plugins/90north-develop/  plugin manifest, agents, symlinks to the skills above
.claude-plugin/marketplace.json  this repo as a plugin marketplace
research/<skill>/     raw research notes with sources (provenance, not loaded by the skill)
tools/validate_skill.py structure, cross-link and source-URL checks
```

## Check a skill

```bash
python3 tools/validate_skill.py skills/design-atlas --urls --report .logs/urls.tsv
```

## Structure check (n-dev)

```bash
python3 skills/n-dev/scripts/structure_check.py --repo path/to/repo --base main
```

Reports pre-existing files that gained more than a wiring diff, new or grown files and touched functions over budget, and added blocks that repeat existing code. Exit 0 clean, 1 findings, 2 error. Tests: `python3 -m unittest discover -s skills/n-dev/scripts/tests -p 'test_*.py'`.

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
