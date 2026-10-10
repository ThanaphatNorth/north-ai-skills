# north-ai-skills

Agent skills by North. Each skill lives in `skills/<name>/` with a `SKILL.md` entry point.

| Skill | What it does |
|---|---|
| [`design-atlas`](skills/design-atlas/SKILL.md) | UX/UI design hub for web, mobile and desktop apps: user research and design psychology, creative direction (concept → storyboard → signature effect), style and theme selection, palettes matched to a logo, design systems, motion, scroll/parallax, 3D (three.js), tested cinematic effect demos and AI-generated (Higgsfield) hero media. |

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
research/design-atlas/  raw research notes with sources (provenance, not loaded by the skill)
tools/validate_skill.py structure, cross-link and source-URL checks
```

## Check a skill

```bash
python3 tools/validate_skill.py skills/design-atlas --urls --report .logs/urls.tsv
```

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
