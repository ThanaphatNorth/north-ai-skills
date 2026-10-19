# north-ai-skills

Agent skills by North. Each skill lives in `skills/<name>/` with a `SKILL.md` entry point.

| Skill | What it does |
|---|---|
| [`design-atlas`](skills/design-atlas/SKILL.md) | UX/UI design hub for web, mobile and desktop apps: user research and design psychology, creative direction (concept → storyboard → signature effect), style and theme selection, palettes matched to a logo, design systems, motion, scroll/parallax, 3D (three.js), tested cinematic effect demos and AI-generated (Higgsfield) hero media. |
| [`n-dev`](skills/n-dev/SKILL.md) | Structured development: design before code, modular and functional modules, reuse before writing, new behaviour in extension files beside existing code, state with one owner, test-first, plus a git-based structure check (wiring budget, file/function budgets, copied blocks) for any language. |
| [`defect-loop`](skills/defect-loop/SKILL.md) | Runs a Jira defect board end-to-end in any repo: pull every open defect (board and backlog), triage, reproduce with a red e2e, root cause at `path:line`, test-first fix with n-dev, code review + QA, before/after videos inline in the Jira comment, PR, move to the QA lane, learn. Needs the plugin's agents. |
| [`defect-loop-init`](skills/defect-loop-init/SKILL.md) | Once per repo: discovers the stack, reads the board's ids and transitions, writes `.claude/defect-loop/` for `defect-loop`. |

## Install as a Claude Code plugin

`90north-develop` bundles `n-dev`, `defect-loop`, `defect-loop-init` and the loop's two agents ([plugin README](plugins/90north-develop/README.md)):

```
/plugin marketplace add ThanaphatNorth/north-ai-skills
/plugin install 90north-develop@north-ai-skills
```

Skills are then `/90north-develop:n-dev`, `/90north-develop:defect-loop-init`, `/90north-develop:defect-loop`.

## Install a skill into Claude Code

Link it into your personal skills folder so every project can use it:

```bash
ln -s "$(pwd)/skills/design-atlas" ~/.claude/skills/design-atlas
```

Or copy it into one project's `.claude/skills/` folder to scope it to that repo.

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
skills/defect-loop/
  SKILL.md            orchestrator playbook (before sweep, per ticket A-H, learn, never)
  references/core-lessons.md  rules from real sweeps, read before every sweep
  templates/jira-comment.md   3-section Jira comment (markdown dialect -> ADF)
  scripts/jira-*.sh, md2adf.py  Jira REST v3: search, get, download, transition, attach, comment
skills/defect-loop-init/
  SKILL.md            per-repo setup; templates/config.md, templates/tracker.env
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
