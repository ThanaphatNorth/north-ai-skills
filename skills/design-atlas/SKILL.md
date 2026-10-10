---
name: design-atlas
description: UX/UI design hub for web, mobile and desktop apps — research the target users, structure flows, choose a style/theme, build a palette that matches a logo, set up a design system, and craft motion, scroll/parallax, 3D (three.js) and AI-generated (Higgsfield) hero effects. Use when the user wants to design, redesign or critique an app/site/screen, asks for UX or UI advice (layout, color, typography, design psychology, user behaviour), wants colors matched to a logo, wants a "wow", creative or cinematic experience (parallax, scroll story, 3D, light/particle effects, animation) or says a design looks ordinary, or needs design tokens/a design system.
---

# Design Atlas

The hub for designing products people can use and want to come back to. `SKILL.md` holds the process and the routing; the knowledge lives in `references/`, the fill-in forms in `templates/`, and the palette tool in `scripts/`. Reply in the user's language (Thai users get Thai, with design terms in English where that is the common usage).

## Good UX, in one screen

Good UX = **the intended people can reach their goal, in their real context, easily and with confidence — and choose to come back.** Judge every decision against this ladder, bottom first; a higher rung never pays for a broken lower one:

1. **Useful** — it solves a job the audience actually has (evidence, not assumption).
2. **Usable** — they can do it without help: clear signifiers, feedback, forgiving errors, few steps.
3. **Accessible** — it works for people with low vision, motor limits, slow phones, Thai or English, one hand on a bus.
4. **Trustworthy** — honest copy, no deceptive patterns, visible security/privacy cues where money, health or data is involved.
5. **Desirable** — a visual identity and moments of craft that make it memorable ("สวยอลัง") — earned only after 1–4 hold.

The user, not the designer, is the reference point: design starts from **who** uses it, **what job** they hire it for, and **where/how** they use it (device, attention, connectivity, skill, emotion). Psychology (`references/psychology.md`) explains *why* a pattern works; research (`references/user-research.md`) tells you *whether* it works for this audience.

## Pick the branch

| The user wants… | Branch | Start with |
|---|---|---|
| A new product/screen/site designed end to end | **Full design** | Steps 1–7 below |
| Advice on one question (color, layout, why conversions are low…) | **Advise** | Diagnose → principle → recommendation → example; open the one matching reference |
| A review of an existing UI (screenshot, URL, code) | **Critique** | Step 7 checklist + `references/ux-foundations.md` heuristics |
| Colors that match their logo | **Palette** | `scripts/palette.py`, then `references/color.md` |
| Something creative / wow / อลัง / award-level, or "it looks ordinary" | **Creative** | `references/creative-direction.md` (ambition dial + context gate → concept → storyboard) alongside Steps 1–7 (lean 1–3 for a single page) |
| One specific effect: parallax, scroll story, 3D, light, particles | **Signature** | Step 6 + `references/cinematic-recipes.md` and `examples/` |
| Design tokens / a design system / theming | **System** | Step 5 + `references/design-systems.md` |

In **Advise**, name the principle behind each recommendation (e.g. "Hick's law: 9 equal-weight options → group into 3") and give concrete values (sizes, hex/OKLCH, ms), not adjectives.

## Full design process

Each step ends on a completion criterion. When the user is unavailable, fill gaps with sensible defaults and label each one **ASSUMPTION** so it can be checked later; never present an assumption as research. Write deliverables (spec, critique) in the user's language; keep design terms, token names and code in English. References are long: open the sections named in each step (`grep -n '^## ' file` lists them).

**Scope the effort.** A single landing page or screen: lean versions of steps 1–3 (brief, 3 competitor pages, one proto-persona, the states that apply) and the full care on steps 4–7. A product or multi-screen app: every step in full.

### 1. Brief
Run the intake in `templates/design-brief.md` (ask only what you can't infer; batch the questions).
**Done when** a brief of about 20 lines (the template's summary block) names: product & business goal, audience segments + context of use, top 3 jobs as job stories, platform(s), brand assets (logo, colors, fonts), 3 tone words + 1 anti-goal, **ambition dial** (calm / bold / cinematic) and whether users arrive worried or in a hurry (`creative-direction.md` §1), constraints (stack, deadline, a11y level, languages), success metric — each filled or marked ASSUMPTION.

### 2. Understand behaviour
Pick the leanest method that answers the riskiest unknown — `user-research.md` §1 (method choice), §2 (desk-only research when there are no users), §13–14 (synthesis, traceability), §15 (Thailand). Minimum: a competitor/analog teardown of their public pages (3 for a landing page, 5 for a product), a proto-persona + JTBD (`templates/persona-jtbd.md`), and the journey's moments that matter. Product norms: `product-patterns.md` (your product type's section + the summary table; hybrids take the stricter motion level).
**Done when** you have a list of insights, each written "We saw/believe X → so the design will Y", and every planned core screen traces to at least one insight.

### 3. Structure
Information architecture, primary flows, screen inventory, and the states of each screen (`ux-foundations.md` §7, §10, §12). App screens: ideal, empty, loading, partial, error, offline/permission-denied. Landing/marketing pages: states belong to the live parts — forms (validation, submitting, success, error), live-data widgets (loading, empty, error), embeds and media (loading, failed, reduced-motion). Write real copy first — layout follows content. Platform patterns: `platform-web.md` (Landing-page anatomy, Navigation patterns, CTA design, Web forms), `platform-mobile.md`, `platform-desktop.md`.
**Done when** each core job has a flow with no dead ends, every screen lists the states that apply to it, and each key decision cites the principle it relies on (`psychology.md` — Laws of UX catalog, Trust and credibility, Goal → principle → tactic map).

### 4. Concept and direction
Concept before style: write the five lines of `creative-direction.md` §2 (brand truth → change → metaphor → signature mechanic → payoff). Then propose **three directions on the safe / bold / wild ladder** (§3) — never three variants of one style — each with: the concept line, base style (`styles-catalog.md` §1–2, §5 escaping the generic AI look), palette (from the logo when there is one — `scripts/palette.py build`, then `color.md` "Logo → palette method"), type pairing (`typography-layout.md` Pairings catalog; Thai typography for Thai text), the mechanic, and motion level. Recommend by the ambition dial and the context gate; then commit to it everywhere.
**Done when** one direction is chosen and written down as decisions (not adjectives), its concept fits in five lines a stranger could sketch, and it states what it deliberately avoids.

### 5. System
Start from `templates/tokens-starter.css`. When `palette.py` ran, its `tokens.css` replaces the template's color section (primitive ramps + semantic colors use the same names); keep the rest of the template (type, space, radius, elevation, motion, `:lang(th)`). Then define components with every state (default, hover, focus-visible, active, disabled, loading, error, selected) — `design-systems.md` §8 (foundation scales), §9 (component spec and states), §13 (bootstrap a minimal system). Respect platform conventions.
**Done when** no UI element uses a raw value that isn't a token — translucent colours are derived from tokens (`oklch(from var(--primary) l c h / .35)`, `color.md`), illustration and decorative SVG internals are exempt — and every interactive component has all its states defined.

### 6. Signature experience
The "อลัง" layer: one concept carried through the page, with every effect serving it — not effects sprinkled everywhere. For **cinematic**, storyboard the scroll in acts first (`creative-direction.md` §4: hook, rise, turn, payoff, aftermath; one row per beat) and start from a tested demo in `examples/` (`cinematic-recipes.md`). For **bold**, one or two set pieces. For **calm**, craft in micro-interactions only. Techniques by level:
- **subtle** — micro-interactions, reveal-on-scroll, view transitions, scroll-linked progress indicators and step tracks (`motion.md` §6–8; `scroll-parallax.md` §5.1, §5.8)
- **expressive** — pinned scroll storytelling, parallax layers, kinetic type, horizontal sections (`scroll-parallax.md` §5.2–5.4, §5.7, §5.10–5.11)
- **immersive** — WebGL/three.js scenes, scroll-linked 3D camera, shaders (`3d-webgl.md` "Does 3D earn its place?", Recipes, Performance budgets); AI-generated hero video, product shots, layered "fake 3D" (`ai-assets-higgsfield.md` "When to generate", Asset recipes)

Imagery is part of the signature: every real-world object is photographic (brand photos → photoreal renders → photoreal generation via `ai-assets-higgsfield.md`, quoting the cost and asking first); drawn placeholders are never final (`creative-direction.md` §5). Use the motion tokens from the template (`motion.md` §14) so recipes resolve. Every signature effect ships with a performance budget, a `prefers-reduced-motion` version that keeps the meaning (`motion.md` §12), a portrait storyboard, and the usability non-negotiables in `creative-direction.md` §8 (real DOM text, native scroll, exits, CTA reachable).
**Done when** the effect enacts the concept, the copy stays readable at every beat, it runs smoothly on a mid-range phone, and the reduced-motion composition is implemented.

### 7. Validate
Look at real renders, not at the code: `node scripts/shoot.mjs <url> <outDir> --widths 320,390,768,1280 --sheet sheet.png` (then again with `--dark` and `--reduced`; add a short phone with a `--jobs` entry of 320×568) saves screenshots, a contact sheet, and prints probes — horizontal overflow, content still invisible, text clipped by an overflow box, Thai words split across lines, targets under 24×24, missing `lang`/alt, h1 count, console errors. Open the sheet and look: probes pass on pages that are visibly broken. Full-page shots paint fixed elements (tab bars, sticky CTAs) mid-page and show a pinned story as a frozen stage over an empty runway — check stories with viewport shots instead: mark the story container `data-story` and run `node scripts/shoot.mjs "<url>?capture" <dir> --story "#story" --at 0,.1,.2,…,1 --widths 390,1280 --sheet sheet.png`. Then render a film and look at its frame scan: `node scripts/scrollfilm.mjs "<url>?capture" <dir> --story "#story" --mp4 film.mp4 --scan scan.png` (`creative-direction.md` §9).
- UX quality bar and Nielsen heuristics — `ux-foundations.md` §3, §12
- WCAG 2.2 AA: contrast (`python3 scripts/palette.py contrast FG BG … --need 4.5`), focus visible, target size, keyboard, labels, reduced motion — `accessibility.md` (Defaults to apply without asking, WCAG 2.2 AA checklist)
- Visual: one clear focal point per view, consistent spacing rhythm, type hierarchy readable in 3 levels, alignment, no orphan styles — `typography-layout.md` (Visual hierarchy & composition)
- Thai text: every heading, lead and button label at 320 and 390 px for mid-word breaks and clipped tone marks — `typography-layout.md` (Thai typography)
- Content: real copy and real data lengths (long Thai strings, empty lists, 1 vs 1,000 items)
- Performance: Core Web Vitals budgets, media weights, 3D budgets — `platform-web.md` (Performance as UX)
- Ethics: no deceptive patterns — `psychology.md` (Deceptive patterns and the law)
**Done when** every item is PASS or listed as a known gap with its fix.

## References

| File | Open when you need… |
|---|---|
| `references/ux-foundations.md` | what good UX is, heuristics, states, forms, UX writing, UX metrics, the UX quality bar |
| `references/user-research.md` | how to study the target group: method choice, lean/desk research, interviews, JTBD, journeys, testing, synthesis |
| `references/psychology.md` | laws of UX, Gestalt, cognitive load, reading patterns, motivation, persuasion ethics, deceptive patterns, trust |
| `references/accessibility.md` | WCAG 2.2 AA checklist, APCA, ARIA patterns, reduced motion, legal landscape, testing |
| `references/color.md` | color theory, OKLCH scales, harmony, logo → palette method, dark mode, color meaning and culture |
| `references/typography-layout.md` | type scales, font pairings, Thai typography, grids, spacing, hierarchy, composition |
| `references/creative-direction.md` | ambition dial + context-of-use gate, concept (truth → metaphor → mechanic), safe/bold/wild ladder, scroll storyboards, cinematic art direction, why a page looks ordinary |
| `references/mechanics-catalog.md` | 70 signature mechanics from award sites by feeling, story fit, cost and static state; 12 worked concept examples |
| `references/cinematic-recipes.md` | tested signature-effect demos in `examples/`: light trail, spotlight, lit text, intro iris, word-swap hero, zoom-through, particles, aurora shader, velocity gallery, glow CTA, mask transitions |
| `references/styles-catalog.md` | choosing a visual style; ~40 styles with tokens and CSS recipes; trends; escaping generic AI look |
| `references/design-systems.md` | tokens (DTCG), component specs and states, theming, libraries, reference design systems |
| `references/motion.md` | motion purpose, durations, easing/springs, micro-interactions, view transitions, tool choice |
| `references/scroll-parallax.md` | scroll effects catalog with recipes: parallax, pinning, scrollytelling, image sequences, Lenis |
| `references/3d-webgl.md` | three.js / R3F / Spline / WebGPU decisions, recipes, asset pipeline, performance budgets |
| `references/ai-assets-higgsfield.md` | AI-generated hero media with Higgsfield and other tools; loops, layers, encoding |
| `references/platform-web.md` | responsive web, navigation, landing-page anatomy, Core Web Vitals, Baseline CSS |
| `references/platform-mobile.md` | iOS (Liquid Glass) and Android (Material 3 Expressive) conventions, thumb zone, mobile patterns |
| `references/platform-desktop.md` | macOS, Windows (Fluent), cross-platform desktop, density, keyboard-first patterns |
| `references/product-patterns.md` | what each product type/industry needs (SaaS, e-commerce, fintech, health, AI…), motion level per type |
| `references/inspiration.md` | where to find references, a curated catalog of award-winning sites by technique, how to study one |

## Tools

- **Palette from a logo:** `python3 scripts/palette.py build --logo <file> --out <dir>` (or `--brand "#hex"`; optional `--accent`, `--ink`, `--harmony`). It suggests a role for every logo color (brand, ink = dark wordmark used as text, accent = the most vivid remaining hue), keeps status colors recognizable and away from brand/accent hues, and picks button fills that pass WCAG 4.5:1 and APCA Lc 60. Writes `tokens.css` (same token names as the template), `tailwind-theme.css`, `tokens.json` (DTCG 2025.10), `palette-report.md`, `preview.html`. Read the report's warnings, open the preview, then explain the choices to the user. `python3 scripts/palette.py contrast FG BG [FG BG…] [--need 4.5]` checks any pair (hex or `oklch()`).
- **Screenshots + probes:** `node scripts/shoot.mjs <url> <outDir> [--widths …] [--dark] [--reduced] [--jobs file]` (Node ≥ 22 and Google Chrome; serve the page over http first). Exit code 1 when a probe fails.
- **Scroll-story film:** `node scripts/scrollfilm.mjs <url> <outDir> [--story sel] [--mp4 f] [--scan f]` renders an eased scroll-through (deterministic when the page has a `window.__frame(dt)` capture hook) and a 1-fps contact sheet.
- **Examples:** `examples/<slug>/index.html` — standalone, tested cinematic effects to adapt (see `cinematic-recipes.md`).
- **Templates:** `templates/design-brief.md`, `templates/persona-jtbd.md`, `templates/usability-test-script.md`, `templates/tokens-starter.css`, `templates/tailwind-theme.css`.
- **When these are connected, use them:** Figma MCP (push/read designs), Higgsfield MCP (generate hero media — check cost and confirm spend with the user first), the `dataviz` skill for charts, `frontend-design` for build-time aesthetics, `web-design-guidelines` for a code-level audit.

## Deliverable shapes

- **Design spec** (when no code is wanted): brief → insights → flows + screen inventory with states → direction → tokens → component notes → signature moment spec (timing, easing, triggers, fallback) → validation results.
- **Built UI** (when code is wanted): the same decisions, expressed as tokens + components + pages; then the Step 7 checklist run on screenshots.
- **Critique**: findings ranked by user impact (blocker / major / minor / polish), each with evidence (screenshot region or selector), the principle it breaks, and a concrete fix.
