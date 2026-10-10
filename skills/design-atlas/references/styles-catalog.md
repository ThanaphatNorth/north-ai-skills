# Styles catalog: choosing, executing and mixing a visual style

> Read when: picking a visual direction for a new product, site or redesign; a brief names a style ("glassmorphism", "neo-brutal", "Linear-style", "Liquid Glass", "Y2K"); output looks generic or "AI-made"; judging whether a 2025–2026 trend fits; combining two styles without making mush.

**Contents:** 1 Selection method · 2 Product-type matrix · 3 Catalog (A Structural · B Raw & loud · C Material & depth · D Tech & dark · E Retro · F Warm & human) · 4 Trends 2025–2026 · 5 Escaping generic AI UI · 6 Mixing rules · Pitfalls · Sources

Conventions: catalog entries are `####` headers reading `N. name — identity`; the **Tokens** line opens with `(loud N/5 · a11y risk · durability)`. Loudness = how much the style competes with content (1 quiet, 5 dominant). CSS targets evergreen browsers as of 2026-10 (OKLCH, `color-mix`, `clip-path`); fonts are Google Fonts unless marked (paid). Color math and contrast → `color.md`; type pairing → `typography-layout.md`; motion timing → `motion.md`; WebGL → `3d-webgl.md`; scroll effects → `scroll-parallax.md`; WCAG detail → `accessibility.md`.

## 1. Selection method

Run these four inputs, produce 2–3 candidate styles, score them, commit to one. Never start from a trend list.

**Step 1 — Brand personality (Aaker 1997, 5 dimensions / 15 facets).** Pick the 1–2 dominant dimensions from the brief or interviews.

| Dimension (facets) | Style candidates (catalog #) | Token tendencies |
|---|---|---|
| Sincerity (down-to-earth, honest, wholesome, cheerful) | Organic 38, Scandinavian 5, Hand-drawn 40, Soft pastel 39, Flat 2.0 7 | warm neutrals, humanist type, soft radius, real photos |
| Excitement (daring, spirited, imaginative, up-to-date) | Dopamine 42, Neo-brutal 10, Kinetic type 15, Y2K 31, Cinematic WebGL 27 | saturated palette, huge type, motion 3–5 |
| Competence (reliable, intelligent, successful) | Swiss 1, Flat 2.0 7, Dark dev 25, Editorial 3, Bento 8 | strict grid, restrained color, precise type, motion 1–2 |
| Sophistication (upper class, charming) | Quiet luxury 2, Editorial 3, Art Deco 36, Japanese minimal 4, Monochrome 6 | serif display, space, low chroma, slow motion |
| Ruggedness (outdoorsy, tough) | Raw brutal 11, Organic 38 (outdoor), Grain+duotone 41, Tactile 20, Monochrome 6 | heavy type, texture, dark earth palette |

**Archetypes (Mark & Pearson, 12)** — use when the brand team speaks in archetypes; map to styles:
- Stability: Caregiver → Soft pastel 39, Organic 38, Flat 2.0 7 · Creator → Collage 14, Bauhaus 9, Editorial 3, Hand-drawn 40 · Ruler → Quiet luxury 2, Art Deco 36, Swiss 1, Monochrome 6.
- Belonging: Everyman → Flat 2.0 7, Scandinavian 5, Hand-drawn 40 · Lover → Quiet luxury 2, Editorial 3, Soft pastel 39 · Jester → Dopamine 42, Memphis 34, Claymorphism 19, Playful 3D 24, Pixel 37.
- Mastery: Hero → Monochrome 6, Kinetic type 15, Cinematic WebGL 27 · Outlaw → Neo-brutal 10, Raw brutal 11, Anti-design 12, Cyberpunk 30 · Magician → Aurora 28, Cinematic WebGL 27, Spatial 22, AI-native 29.
- Independence: Innocent → Soft pastel 39, Scandinavian 5 · Explorer → Organic 38, Grain+duotone 41, Isometric 23 · Sage → Editorial 3, Swiss 1, Japanese minimal 4, Terminal 26.

**Step 2 — Audience modifiers.**
- Age 45+ or low digital confidence → loudness ≤3, body ≥16–18px, contrast ≥4.5:1 everywhere, no translucency behind text. Google's M3 Expressive research found larger, higher-contrast key actions let 45+ users find them about as fast as younger users.
- Age 18–24 → expressive styles test well (M3 Expressive preference up to 87% in that group), but a "strong minority" preferred calmer versions → keep a calm mode.
- Experts and daily power users → density and keyboard flow beat decoration (Dark dev 25, Swiss 1, Flat 2.0 7).
- Thai / CJK / Arabic content → styles whose signature is UPPERCASE + wide tracking (Quiet luxury labels, Art Deco, Swiss meta) need a substitute device (weight, size, color) because those scripts have no case; ultra-thin weights break Thai tone marks. See `typography-layout.md`.

**Step 3 — Product type and context of use.**
- Daily-use tool (≥1 session/day) → app shell loud ≤2; spend expression on onboarding, empty states, success moments, marketing.
- Money, health, legal, error recovery → calm, high contrast, no playful failure states, no translucency behind numbers.
- Outdoor/mobile in sunlight → key info ≥7:1, no glass, no neumorphism.
- Low-end devices or data-capped markets → no WebGL hero, ≤1 `backdrop-filter`, static texture images instead of SVG filters.
- One-off campaign or launch → loudness 4–5 allowed; it does not need to survive 1,000 visits.

**Step 4 — Score 2–3 candidates (0–2 each, max 12), pick the top, commit.**
Criteria: personality fit · audience fit · context/a11y cost (2 = low risk) · build + performance cost (2 = cheap) · differentiation (list 3 competitors' styles; 0 if you match the modal one, unless category convention is needed for trust, e.g. government) · longevity (durable 2, cyclical 1, fad 0). Ties → lower a11y risk wins.
Commit by writing a one-line **style statement** plus a token sheet before any layout: *"Editorial (3) with grain-duotone (41) photography; serif display + grotesk UI; 0px radius; no shadows; motion ≤2. We will never use gradients, glass, or emoji."* Put the statement in the project's design doc so every later page is checked against it (see `design-systems.md` for tokens).

## 2. Product-type matrix

| Product type | Primary candidates | Accent that works | Avoid | Deciding factor |
|---|---|---|---|---|
| Fintech (consumer) | Flat 2.0 7, Quiet luxury 2, Tactile 20 (cards/wallet) | Aurora 28 hero only, Bento 8 | Anti-design, Cyberpunk, glass behind balances | Competence; tabular numbers legible at a glance |
| Fintech (pro/trading) | Dark dev 25, Swiss 1, Monochrome 6 | Terminal 26 motifs | Clay, pastel, motion >2 | Density, keyboard, red/green + shape cues |
| Health / clinical | Flat 2.0 7, Scandinavian 5, Organic 38 | Soft pastel 39 surfaces only | Cyberpunk, Anti-design, glass, glitch | Sincerity + competence; older users; WCAG AA floor |
| Kids | Claymorphism 19, Playful 3D 24, Hand-drawn 40, Bauhaus 9 | Dopamine 42 | Dark dev, Quiet luxury, thin type | Big targets; parent-gate screens in calm Flat 2.0 |
| Luxury | Quiet luxury 2, Editorial 3, Japanese minimal 4, Art Deco 36 (hospitality, spirits) | Grain 41, Kinetic serif 15 | Dopamine, Clay, Corporate Memphis | Sophistication; photography leads |
| Dev tools | Dark dev 25, Terminal 26, Swiss 1, Monochrome 6 | Bento 8 (marketing), one Aurora glow | Clay, pastel, Memphis | Docs-first, code legibility, light + dark parity |
| Creative agency | Cinematic WebGL 27, Kinetic type 15, Editorial 3, Anti-design 12 | Grain 41, Collage 14 | Flat 2.0 corporate, Corporate Memphis | The site is the portfolio; craft is the proof |
| E-commerce fashion | Editorial 3, Quiet luxury 2, Monochrome 6, Y2K 31 (Gen-Z) | Kinetic type 15 on campaign pages | Glass on product grids, WebGL on listing pages | Product imagery + fast listing pages |
| B2B SaaS | Flat 2.0 7, Swiss 1, Bento 8 (marketing), Dark dev 25 (technical buyers) | Editorial 3 for content hub | Vaporwave, Cyberpunk | Competence; app shell loud ≤2 |
| Gaming | Cyberpunk 30, Pixel 37, Synthwave 32, Cinematic WebGL 27, Playful 3D 24 | Glitch, HUD frames | Quiet luxury, Flat 2.0 alone | Excitement/ruggedness; respect flash limits |
| Government / public | Flat 2.0 7 (GOV.UK-style), Swiss 1 | none | Glass, motion >1, trends | Accessibility often legally required; plain language |
| Food & drink | Organic 38, Collage 14, Hand-drawn 40, Dopamine 42 (delivery) | Editorial 3 (recipes) | Dark dev, Cyberpunk, duotone on food photos | True-color food photography |
| Wellness | Soft pastel 39, Organic 38, Japanese minimal 4, Scandinavian 5 | Aurora 28 (slow), Grain 41 | Anti-design, Cyberpunk, motion >2 | Calm; no urgency patterns |
| Crypto / web3 | Dark dev 25, Cinematic WebGL 27, Y2K chrome 31, Cyberpunk 30 | Aurora 28 | Same loudness on transaction screens | Marketing can be loud; signing/transfer screens must be Flat-calm |
| Education | Hand-drawn 40, Bauhaus 9, Flat 2.0 7, Claymorphism 19 (young) | Dopamine 42, Pixel 37 badges | Cinematic WebGL inside lessons | Clarity of progress; gamified feedback |
| AI product | AI-native 29 on a base of Editorial 3, Quiet luxury 2 or Swiss 1 | Brand character, restrained Aurora 28 | Purple-blue mesh + sparkles (the AI tell) | Trust, provenance, readable long answers |

## 3. The catalog

### A. Structural and minimal (1–9)
#### 1. Swiss / International — asymmetric grid, flush-left grotesk, objective hierarchy
**Tokens** (loud 2 · a11y Low · durable): white/black + one signal red · neo-grotesk (Archivo, Schibsted Grotesk; paid: Neue Haas Grotesk) · radius 0 · no shadows · no texture · motion 1–2. **Use** institutions, dev docs, architecture, data-dense portfolios. **Avoid** kids, warm wellness. **A11y** watch tiny captions and long ragged measures.
```css
.swiss { display:grid; grid-template-columns:repeat(12,1fr); column-gap:clamp(1rem,2vw,2rem); }
.swiss h1 { grid-column:1 / span 8; font:700 clamp(3rem,8vw,7rem)/.95 "Archivo",sans-serif; letter-spacing:-.03em; }
.swiss .meta { grid-column:9 / -1; font:500 .875rem/1.4 "Archivo",sans-serif; text-transform:uppercase; letter-spacing:.06em; }
.swiss hr { grid-column:1 / -1; border:0; border-top:2px solid currentColor; }
```
**Refs:** https://www.ibm.com/design/language/ · https://www.swissted.com/ · https://www.vitsoe.com/
#### 2. Refined minimal / quiet luxury — warm paper, serif display, vast space, almost no UI chrome
**Tokens** (loud 1 · a11y Med · durable): warm off-white `oklch(.97 .01 85)` + ink + one muted accent (taupe, olive) · serif display (Newsreader, Fraunces, Instrument Serif) + quiet sans · radius 0–2px · no shadows · texture = photography · motion slow fades 400–700ms. **Use** fashion, hospitality, skincare, architecture. **Avoid** discount retail, dense dashboards. **A11y** light-gray text, hairlines and tiny tracked labels routinely fail 4.5:1.
```css
:root { --paper:oklch(.97 .01 85); --ink:oklch(.22 .01 60); --quiet:oklch(.45 .01 60); } /* --quiet ≥4.5:1 on paper */
h1 { font:400 clamp(2.5rem,6vw,5.5rem)/1.05 "Newsreader",serif; letter-spacing:-.01em; }
.label { font:500 .75rem/1 "Hanken Grotesk",sans-serif; letter-spacing:.14em; text-transform:uppercase; color:var(--quiet); }
section { padding-block:clamp(6rem,14vw,12rem); }
```
**Refs:** https://www.therow.com/ · https://www.kinfolk.com/
#### 3. Editorial / magazine — the page reads like a well-set publication
**Tokens** (loud 2 · a11y Low · durable): paper + ink + one section color · text serif (Newsreader, Source Serif 4) + grotesk UI, display serif (Fraunces) · radius 0 · rules, drop caps, pull quotes · motion 1–2. **Use** media, content-led brands, reports, long-form, docs-as-marketing. **Avoid** transactional flows. **A11y** keep measure 45–75ch; multi-column reading order must match DOM.
```css
article { display:grid; grid-template-columns:1fr min(68ch,100% - 2rem) 1fr; }
article > * { grid-column:2; }  article > .wide { grid-column:1 / -1; }
article > p:first-of-type::first-letter { float:left; font:700 4.2em/.8 "Fraunces",serif; padding:.05em .08em 0 0; }
.pull { font:italic 400 1.75rem/1.25 "Newsreader",serif; border-block:1px solid; padding-block:1rem; }
```
**Refs:** https://pudding.cool/ · https://www.itsnicethat.com/ · https://www.theverge.com/
#### 4. Japanese minimal (ma) — negative space as an active element, natural materials, restraint
**Tokens** (loud 1 · a11y Med · durable): unbleached neutrals + sumi ink + one natural accent (indigo or vermilion) · Shippori Mincho / Noto Serif JP + light Latin grotesk · radius 0–4 · no shadows · washi-like texture at ≤4% · motion slow. **Use** craft, tea and food, ceramics, hospitality, meditation. **Avoid** dense commerce. **A11y** light weights and gray text at small sizes; vertical text only for short display lines.
```css
.ma { display:grid; grid-template-columns:1fr minmax(0,36rem) 2fr; min-height:100svh; align-content:center; }
.ma h1 { writing-mode:vertical-rl; font:500 2rem/1.8 "Shippori Mincho",serif; letter-spacing:.2em; }
.ma p { line-height:1.9; color:oklch(.32 .01 70); }   /* CJK body 1.7–2.0 */
```
**Refs:** https://hara.ndc.co.jp/
#### 5. Scandinavian — light, warm, functional, natural-light photography
**Tokens** (loud 1 · a11y Low · durable): warm white, pale wood, sage, dusty blue, terracotta + one deep ink · humanist/geometric sans (Albert Sans, Figtree) · radius 8–12 · one faint shadow level · motion 1–2. **Use** furniture/home, family services, sustainable consumer, public services. **Avoid** nightlife, gaming. **A11y** pastel text fails; text uses the ink.
```css
:root { --bg:oklch(.975 .008 80); --wood:oklch(.82 .05 70); --sage:oklch(.72 .04 150); --ink:oklch(.25 .02 250); }
body { background:var(--bg); color:var(--ink); font:400 1.0625rem/1.6 "Albert Sans",sans-serif; }
.card { background:#fff; border-radius:12px; padding:2rem; box-shadow:0 1px 2px oklch(.25 .02 250 / .06); }
```
**Refs:** https://www.hay.com/ · https://www.muuto.com/
#### 6. Monochrome high-contrast — black, white, one signal color used surgically
**Tokens** (loud 2 · a11y Low · durable): near-black `oklch(.14 0 0)` / near-white + ≤1 signal color on ≤5% of surface · grotesk or mono, extreme scale contrast · radius 0 or full pill · no shadows (use inversion and borders) · motion snappy 120–200ms. **Use** hardware, fashion, dev tools, statements. **Avoid** kids, health reassurance. **A11y** pure #fff on #000 for long body text causes halation → use off-values.
```css
:root { --fg:oklch(.98 0 0); --bg:oklch(.14 0 0); --signal:oklch(.63 .25 29); }
body { background:var(--bg); color:var(--fg); }
.btn { background:var(--fg); color:var(--bg); border-radius:999px; } .btn:hover { background:var(--signal); color:var(--bg); }
::selection { background:var(--signal); color:var(--bg); }   /* signal + near-black text ≈5.7:1; signal + white fails */
```
**Refs:** https://nothing.tech/ · https://vercel.com/
#### 7. Flat 2.0 — flat surfaces with just enough depth (one shadow level, borders) to keep affordance
**Tokens** (loud 1 · a11y Low · durable): brand primary + neutral ramp + semantic colors · clean sans · radius 4–8 · one elevation level or tonal surfaces · motion 1–2. **Use** B2B, government, enterprise, utilities, docs — the safest default. **Avoid** brands that must feel distinctive (pair with an accent, §6). **A11y** every interactive element needs fill or a ≥3:1 border; text-only buttons get underline or icon.
```css
.btn { background:var(--primary); color:var(--on-primary); border:0; border-radius:6px; padding:.625rem 1rem; box-shadow:0 1px 0 oklch(0 0 0 / .12); }
.btn:focus-visible { outline:3px solid var(--focus); outline-offset:2px; }
.card { background:var(--surface); border:1px solid var(--border); border-radius:8px; }
```
**Refs:** https://design-system.service.gov.uk/ · https://atlassian.design/
#### 8. Bento grid — modular tiles of mixed span, each tile one idea
**Tokens** (loud 2 · a11y Med · durable layout / cyclical look): neutral page, tiles carry their own color or media · radius 16–28 · gap 12–24 · depth none or faint · motion = hover reveal, video tiles. **Use** feature overviews, launches, portfolio summaries, dashboard home. **Avoid** sequential stories, long reading, step flows. **A11y** DOM order must equal reading order (don't use `grid-auto-flow:dense`); text on media tiles needs a scrim. Practitioner ceiling: 6–9 tiles per grid.
```css
.bento { display:grid; gap:16px; grid-template-columns:repeat(4,1fr); grid-auto-rows:minmax(180px,auto); }
.bento > .lg { grid-column:span 2; grid-row:span 2; }  .bento > .wide { grid-column:span 2; }
.bento > * { border-radius:24px; padding:24px; background:var(--tile, oklch(.96 .005 260)); }
@media (max-width:48rem) { .bento { grid-template-columns:1fr 1fr; } }
```
**Refs:** https://www.apple.com/iphone/ · https://bentogrids.com/
#### 9. Bauhaus / geometric — primaries, circle-square-triangle, form follows function
**Tokens** (loud 3 · a11y Med · durable): red, yellow, blue + black/white · geometric sans (Jost; paid: Futura) · radius 0 or 50% · no shadows · motion = rotation/translation of shapes. **Use** cultural institutions, education, design tools, events. **Avoid** luxury fashion, clinical health. **A11y** yellow text on white and red/blue adjacency fail or vibrate.
```css
:root { --red:oklch(.58 .21 29); --yellow:oklch(.88 .17 95); --blue:oklch(.45 .17 262); }
.disc { aspect-ratio:1; border-radius:50%; background:var(--red); }
.tri { aspect-ratio:1; background:var(--blue); clip-path:polygon(0 100%,50% 0,100% 100%); }
h1 { font:500 clamp(3rem,9vw,8rem)/.9 "Jost",sans-serif; text-transform:lowercase; }
```
**Refs:** https://bauhauskooperation.de/ (institutional, history and imagery)

### B. Raw and loud (10–15)
#### 10. Neo-brutalism — saturated flat blocks, thick black outlines, hard offset shadows
**Tokens** (loud 4 · a11y Med · cyclical): 1–3 saturated fills + pure black · chunky grotesk or mono (Archivo Black, Space Mono) · radius 0–8 · shadow `4px 4px 0 #000`, never blurred · motion: press collapses the shadow (80–120ms). **Use** creator tools, indie SaaS, youth consumer, events. **Avoid** banking, health, government, luxury. **A11y** contrast is usually high; risks are color-only meaning and noise; keep a focus ring distinct from the shadow.
```css
.nb { background:#FF90E8; color:#000; border:2px solid #000; border-radius:4px; box-shadow:4px 4px 0 #000; transition:transform .08s, box-shadow .08s; }
.nb:hover { transform:translate(-2px,-2px); box-shadow:6px 6px 0 #000; }
.nb:active { transform:translate(4px,4px); box-shadow:0 0 0 #000; }
```
**Refs:** https://gumroad.com/ (ships `shadow-[4px_4px_0_0_#000000]`, `border-black`, `#FF90E8`) · https://www.neobrutalism.dev/
#### 11. Raw brutalism — browser defaults, HTML-first, unadorned on purpose
**Tokens** (loud 2 · a11y Low if semantic · durable niche): default serif, blue/purple links, white page · radius 0 · no shadows · no motion. **Use** personal sites, manifestos, archives, art, ultra-fast pages. **Avoid** conversion funnels, mainstream consumer. **A11y** often excellent; NN/g rule: keep the rawness visual — hierarchy and navigation stay intact.
```css
body { max-width:70ch; margin:2rem auto; padding:0 1rem; font:1.125rem/1.5 "Times New Roman",Times,serif; }
a { color:#00e; } a:visited { color:#551a8b; }
pre, code { font-family:ui-monospace,monospace; }
```
**Refs:** https://www.berkshirehathaway.com/ · https://brutalistwebsites.com/
#### 12. Anti-design — deliberately ugly, clashing, disorienting
**Tokens** (loud 5 · a11y High · cyclical): clashing palette, 3+ fonts misused on purpose, broken grid, rotations, cursor gimmicks · motion erratic. **Use** only for designer/artist audiences or entertainment where discovery beats efficiency (NN/g); fashion drops, music. **Avoid** any task flow — "an antidesign UI will backfire". **A11y** high: keep real text, focus order and a reduced-motion path.
```css
.anti h1 { font:900 12vw/.8 "Times New Roman",serif; color:#fff; mix-blend-mode:difference; transform:rotate(-4deg); }
.anti .sticker { position:absolute; rotate:calc(var(--r,1) * 7deg); }
@media (prefers-reduced-motion:reduce) { .anti * { animation:none !important; transition:none !important; } }
```
**Refs:** https://mschf.com/ · https://www.nngroup.com/articles/brutalism-antidesign/
#### 13. Maximalism — more is more: pattern on pattern, layered imagery, rich color
**Tokens** (loud 5 · a11y High · cyclical): many hues governed by one family, patterns, 2–3 contrasting typefaces, layered imagery · radius mixed · hard or colored shadows · motion 3–4. **Use** fashion, beauty, music, festivals, Gen-Z campaigns (Adobe and Figma 2026 lists). **Avoid** tools and forms. **A11y** text always sits on a solid plate, never directly on pattern.
```css
.max { background:repeating-conic-gradient(from 45deg, oklch(.75 .18 350) 0 25%, oklch(.85 .15 95) 0 50%) 0 0/48px 48px; }
.max .plate { background:oklch(.98 .01 90); color:oklch(.2 .02 300); padding:1.5rem; box-shadow:12px 12px 0 oklch(.55 .2 300); }
.max h1 { font:italic 800 clamp(3rem,10vw,9rem)/.85 "Fraunces",serif; }
```
**Refs:** https://www.adobe.com/express/learn/blog/design-trends-2026 (trend evidence; no single canonical site)
#### 14. Collage / scrapbook — cut-outs, tape, stickers, handwriting, visible assembly
**Tokens** (loud 4 · a11y Med · cyclical): paper and kraft textures, cut-out photos, tape, stickers · typewriter + marker type · rotations ±2–6° · soft paper shadows · motion drag/wobble. **Use** food and drink, indie brands, events, travel, personal portfolios. **Avoid** enterprise, regulated. **A11y** no text baked into images; source order = reading order.
```css
.scrap > * { position:relative; rotate:var(--tilt,-2deg); background:#fffdf6; padding:.75rem; box-shadow:0 2px 6px oklch(.3 .03 60 / .25); }
.scrap > :nth-child(even) { --tilt:3deg; }
.tape { position:absolute; inset:-12px auto auto 40%; width:90px; height:28px; background:oklch(.92 .05 95 / .7); rotate:-6deg; }
.torn { clip-path:polygon(0 3%,8% 0,17% 4%,29% 1%,41% 5%,55% 0,68% 4%,80% 1%,92% 5%,100% 2%,100% 100%,0 100%); }
```
**Refs:** https://designmodo.com/scrapbook-website-design/
#### 15. Kinetic typography-led — type is the image; it moves, stretches, scrubs with scroll
**Tokens** (loud 4 · a11y High · durable technique): 1–2 families, variable fonts with `wght`/`wdth` axes (Roboto Flex, Anybody) · 2 colors · radius irrelevant · motion 4–5, scroll-linked. **Use** agencies, launches, events, music, manifestos. **Avoid** forms, data apps, long reading. **A11y** reduced-motion fallback mandatory; if letters are split into spans, mark the spans `aria-hidden="true"` and keep the whole string in a visually-hidden sibling (`aria-label` only works on elements with a role such as headings or links, not a plain `div`). Scroll-driven animations: Chrome 115+, Safari 26+, Firefox preview only → use `@supports`.
```css
@supports (animation-timeline: view()) {
  .kinetic { animation:stretch linear both; animation-timeline:view(); animation-range:entry 0% cover 50%; } }
@keyframes stretch { from { font-variation-settings:"wght" 200,"wdth" 75; } to { font-variation-settings:"wght" 900,"wdth" 125; } }
@media (prefers-reduced-motion:reduce) { .kinetic { animation:none; } }
```
**Refs:** https://www.awwwards.com/inspiration/type-transformation-kinetic-type-animation · https://basement.studio/

### C. Material and depth (16–24)
#### 16. Glassmorphism — frosted translucent panels over a vivid backdrop
**Tokens** (loud 3 · a11y High · cyclical): vivid photo or gradient backdrop, white fill 15–30% (light) or dark 40–60% · 1px light border for thickness · blur 16–32px (more blur for busier backdrops, NN/g) · radius 16–24 · soft shadow · motion 1–2. **Use** overlays, media controls, widgets over imagery, transient menus. **Avoid** body-text containers, tables, forms, stacked glass. **A11y** contrast changes with whatever scrolls behind; Fluent's rule applies: no accent-colored text or links on acrylic.
```css
.glass { background:oklch(1 0 0 / .2); border:1px solid oklch(1 0 0 / .35); border-radius:20px;
  -webkit-backdrop-filter:blur(20px) saturate(160%); backdrop-filter:blur(20px) saturate(160%); }
@supports not ((backdrop-filter:blur(1px)) or (-webkit-backdrop-filter:blur(1px))) { .glass { background:oklch(.98 0 0 / .94); } }
@media (prefers-reduced-transparency:reduce), (prefers-contrast:more) { .glass { background:Canvas; backdrop-filter:none; -webkit-backdrop-filter:none; } }
```
**Refs:** https://www.nngroup.com/articles/glassmorphism/ · https://learn.microsoft.com/en-us/windows/apps/design/style/acrylic
#### 17. Apple Liquid Glass (iOS/iPadOS/macOS/watchOS/tvOS 26) — and a responsible web approximation
**What it is (Apple, 2025-06-09):** a translucent material that reflects and refracts what is behind it, shows specular highlights in motion, and adapts color to content and light/dark. It is for **controls and navigation** (buttons, sliders, media controls, tab bars, sidebars, toolbars), which float as a separate layer, recede on scroll and are concentric with device/window corners.
**Status as of 2026-10:** NN/g (2025-10-10) documented legibility loss ("text on top of text"), distracting motion and weaker discoverability; Infinum measured contrast as low as 1.5:1 in betas. iOS 26.1 added Settings › Display & Brightness › Liquid Glass › Clear/Tinted. At WWDC (2026-06-08) Apple announced rebuilt readability foundations (diffusing complex content behind panels) and a slider "from ultra clear to fully tinted" for iOS 27-era releases. Lesson: even the platform owner made opacity user-adjustable.
**Tokens** (loud 2 · a11y High on web · durable on Apple platforms): content-colored translucency · system fonts on Apple, your brand sans on web · concentric radii · specular inner highlight instead of drop shadows · motion = morph and lensing, short.
**Native rule:** use system components (SwiftUI `glassEffect(_:in:)`, standard bars and sheets) instead of custom blur; do not port Liquid Glass to Android — use Material 3 there (#21).
**Web rules:**
1. Glass only on floating chrome (nav bar, tab bar, toolbar, sheet header, media controls). Never on content cards, articles, tables or forms.
2. Ship the legible default ("Tinted"): start at fill alpha ≈.7 light / ≈.6 dark, then measure text ≥4.5:1 over the worst backdrops (white photo, black photo, dense text). Offer a Clear/Tinted (or slider) setting and persist it.
3. `prefers-reduced-transparency` works only in Chrome 118+ (Firefox behind a flag, Safari unsupported as of 2026-10) → you cannot rely on it; the default must already be legible.
4. ≤3 glass surfaces per viewport, none edge-to-edge (visible seams), never animate blur radius, never on list rows. `backdrop-filter` needs `-webkit-` for Safari < 18.
5. Refraction via SVG `feDisplacementMap` in `backdrop-filter:url(#id)` renders in Chromium only (LogRocket, 2025-12); maps are size-specific. Treat it as an enhancement on one hero control; the blur-only version must already look finished.
6. Keep text labels and stable positions; NN/g's main complaints were removed labels and controls that move or vanish.
```css
.lg-bar { --r:28px; --a:.7; border-radius:var(--r); background:oklch(.99 0 0 / var(--a));
  -webkit-backdrop-filter:blur(14px) saturate(180%); backdrop-filter:blur(14px) saturate(180%);
  box-shadow:inset 0 1px 0 oklch(1 0 0 / .9), inset 0 -1px 0 oklch(0 0 0 / .08), 0 6px 24px oklch(0 0 0 / .14); }
.lg-bar > .lg-btn { margin:6px; border-radius:calc(var(--r) - 6px); }        /* concentric: inner = outer − inset */
:root[data-glass="clear"] .lg-bar { --a:.38; }                               /* user opt-in only */
@media (prefers-color-scheme:dark) { .lg-bar { --a:.6; background:oklch(.22 0 0 / var(--a)); } }
@media (prefers-reduced-transparency:reduce), (prefers-contrast:more), (forced-colors:active) {
  .lg-bar { background:Canvas; -webkit-backdrop-filter:none; backdrop-filter:none; border:1px solid CanvasText; } }
```
**Refs:** https://www.apple.com/newsroom/2025/06/apple-introduces-a-delightful-and-elegant-new-software-design/ · https://developer.apple.com/design/human-interface-guidelines/materials · https://www.nngroup.com/articles/liquid-glass/ · https://blog.logrocket.com/how-create-liquid-glass-effects-css-and-svg/
#### 18. Neumorphism (soft UI) — elements extruded from a same-colored surface by paired light/dark shadows
**Tokens** (loud 2 · a11y High · fad): one mid-light surface color (e.g. `#e0e5ec`) for page and elements · rounded sans · radius 12–24 · dual shadows light top-left, dark bottom-right · no borders · motion: inset on press. **Use** decorative dials and toggles in hardware-companion or smart-home apps, with an accent fill for active state. **Avoid** primary actions, forms, anything that must look clickable. **A11y** edges typically sit well below the 3:1 non-text minimum and states are ambiguous; adoption fell by 2021 partly for this (Wikipedia). It still appears on Figma's 2026 list — treat that as fashion, not evidence.
```css
.neu { background:#e0e5ec; border-radius:20px; box-shadow:9px 9px 16px oklch(.6 .02 260 / .5), -9px -9px 16px oklch(1 0 0 / .8); }
.neu[aria-pressed="true"], .neu:active { box-shadow:inset 6px 6px 12px oklch(.6 .02 260 / .5), inset -6px -6px 12px oklch(1 0 0 / .8); }
.neu:focus-visible { outline:3px solid oklch(.5 .2 260); outline-offset:3px; }   /* never shadow-only focus */
```
**Refs:** https://neumorphism.io/ · https://en.wikipedia.org/wiki/Neumorphism
#### 19. Claymorphism — inflated, puffy, matte "clay" objects
**Tokens** (loud 3 · a11y Med · cyclical niche): saturated pastels on light ground · rounded sans (Fredoka, Baloo 2) · radius 24–40px · one large soft outer shadow + two inner shadows (light top-left, dark bottom-right) per Malewicz · 3D clay illustrations · motion bouncy. **Use** kids, onboarding, casual games, playful consumer. **Avoid** serious or utilitarian products (the inventor notes it reads child-like). **A11y** fills can be any color independent of the background, so pick fills deep enough for text.
```css
.clay { background:oklch(.82 .1 300); border-radius:32px;
  box-shadow:16px 18px 32px oklch(.5 .08 300 / .35), inset -8px -8px 16px oklch(.55 .1 300 / .45), inset 8px 8px 16px oklch(1 0 0 / .6); }
```
**Refs:** https://hype4.academy/articles/design/claymorphism-in-user-interfaces
#### 20. Tactile / neo-skeuomorphism — controls that feel like real hardware, with modern restraint
**Tokens** (loud 3 · a11y Med · cyclical, rising): neutral body + one hardware accent (orange, signal green) · gradients only on controls · inner highlight + layered shadows · noise texture · sound/haptics · physical springs. **Use** audio and music tools, wallets, hardware companions, calculators/timers, game UI. **Avoid** content-heavy pages. **A11y** states must change more than depth (label, color or icon too).
```css
.key { border-radius:10px; background:linear-gradient(oklch(.97 0 0), oklch(.9 0 0));
  box-shadow:inset 0 1px 0 #fff, inset 0 -2px 0 oklch(.8 0 0), 0 1px 1px oklch(0 0 0 / .15), 0 4px 8px oklch(0 0 0 / .12); }
.key:active { translate:0 1px; box-shadow:inset 0 2px 4px oklch(0 0 0 / .2); }
.led[data-on] { background:oklch(.7 .2 40); box-shadow:0 0 8px oklch(.7 .2 40); }
```
**Refs:** https://teenage.engineering/ · https://family.co/
#### 21. Material 3 Expressive — Google's research-backed emphasis via color, shape, size, containment and spring motion (I/O, May 2025)
**Evidence:** 46 studies, 18,000+ participants; key elements spotted up to 4× faster; Google's own caveats: "not a one-size-fits-all solution" (banking may not suit), breaking familiar patterns or dropping labels lowered usability, "No amount of emotion can compensate for a lack of clarity."
**Tokens** (loud 3 · a11y Low–Med · durable): dynamic tonal palettes and surface containers · emphasized (larger, heavier) type for key moments · M3 shape scale (0/4/8/12/16/28dp/full) plus a 35-shape decorative library with morphing · spring motion tokens. **Use** Android apps, broad-age consumer apps. **Avoid** cloning it on iOS; regulated finance screens. **A11y** good by design; springs still need reduced-motion.
```css
.fab-xl { background:var(--md-primary-container); color:var(--md-on-primary-container); border-radius:28px; min-height:96px; padding-inline:28px;
  font:600 1.375rem/1 "Roboto Flex",sans-serif; transition:border-radius 350ms cubic-bezier(.34,1.56,.64,1); }  /* overshoot ≈ spring */
.fab-xl:active { border-radius:16px; }                     /* shape morph on press */
```
**Refs:** https://m3.material.io/ · https://design.google/library/expressive-material-design-google-research
#### 22. Spatial / visionOS — glass windows floating in depth, ornaments, gaze-and-pinch targets
**Tokens** (loud 3 · a11y Med · durable on headsets / fad as web decoration): system glass windows, layered depth, ornaments outside window edges, generous spaced targets (check HIG for the current visionOS minimum), soft lighting · motion = subtle parallax. **Use** immersive demos, 3D commerce, media. **Avoid** dense data, quick tasks. **A11y** on web keep tilt ≤6°, disable under reduced motion.
```css
.scene { perspective:1200px; }
.panel { transform:rotateX(var(--rx,0deg)) rotateY(var(--ry,0deg)); transform-style:preserve-3d; transition:transform .3s ease-out; border-radius:28px; }
.panel > .ornament { transform:translateZ(40px); }          /* JS maps pointer to --rx/--ry, clamp ±6deg */
@media (prefers-reduced-motion:reduce) { .panel { transform:none; } }
```
**Refs:** https://developer.apple.com/design/human-interface-guidelines/designing-for-visionos
#### 23. Isometric — parallel-projection illustration of systems, places and products
**Tokens** (loud 2 · a11y Low · cyclical): 3 tones per object face (top lightest), limited palette, no perspective · motion = float, assemble. **Use** infrastructure and logistics explainers, maps, games, onboarding illustration. **Avoid** as UI chrome. **A11y** alt text; never encode data only in the drawing.
```css
.iso { transform:rotateX(60deg) rotateZ(-45deg); transform-style:preserve-3d; }   /* 2:1 "game" isometric; true isometric = 54.74deg */
.iso .tile { box-shadow:1px 1px 0 oklch(.7 .05 250), 2px 2px 0 oklch(.7 .05 250), 3px 3px 0 oklch(.6 .05 250); }
```
**Refs:** https://www.monumentvalleygame.com/
#### 24. Playful 3D / toy — candy-colored rendered objects, chunky "toy" controls
**Tokens** (loud 4 · a11y Med · cyclical): soft-lit 3D objects (Spline/Blender), saturated candy palette, rounded heavy type (Fredoka) · bottom-edge "toy" shadows · motion bouncy. **Use** consumer launches, games, kids, gamified learning. **Avoid** B2B, government. Generic glossy 3D blobs read as AI default (§5) → model objects that are your product or mascot. **A11y** poster image for slow devices; motion off under reduced motion.
```css
.toy { background:oklch(.8 .17 145); color:oklch(.2 .05 145); border-radius:999px; padding:1rem 2rem; font:700 1.25rem "Fredoka",sans-serif;
  box-shadow:inset 0 -6px 0 oklch(.6 .17 145), 0 6px 0 oklch(.45 .15 145); transition:translate .1s, box-shadow .1s; }
.toy:active { translate:0 6px; box-shadow:inset 0 -2px 0 oklch(.6 .17 145), 0 0 0 oklch(.45 .15 145); }
```
**Refs:** https://spline.design/ · https://www.duolingo.com/

### D. Tech and dark (25–30)
#### 25. Dark developer / "Linear-style" — near-black, tight grays, one accent, dense and keyboard-first
**Tokens** (loud 2 · a11y Med · peaked; imitation = fad): Linear ships `#08090A` with Inter; 3–4 surface steps, 1px borders at ~8% white, one accent · mono for code · radius 6–12 · faint glow/gradient at most once · motion 150–250ms · command palette. LogRocket (2025-06): Linear itself "significantly cut back on the amount of color"; Raycast dropped its gradient; the look is oversaturated. **Use** dev tools, technical B2B, AI infrastructure. **Avoid** consumer warmth, kids, health. **A11y** muted gray text on near-black often fails; keep muted ≥ L .70.
```css
:root { --bg:#08090a; --s1:oklch(.19 .005 270); --line:oklch(1 0 0 / .08); --text:oklch(.96 0 0); --muted:oklch(.72 .01 270); --accent:oklch(.62 .16 275); }
.panel { background:var(--s1); border:1px solid var(--line); border-radius:10px; }
.hero::before { content:""; position:absolute; inset:-20% 10% auto; height:480px; pointer-events:none;
  background:radial-gradient(closest-side, oklch(.62 .16 275 / .22), transparent); filter:blur(40px); }
```
**Refs:** https://linear.app/ · https://www.raycast.com/ · https://vercel.com/
#### 26. Terminal / ASCII — monospace everything, prompts, box-drawing, blinking cursor
**Tokens** (loud 2 · a11y Med · durable niche): green or amber on black, or ink on paper · JetBrains Mono / IBM Plex Mono · radius 0 · no shadow · optional scanlines · motion = typewriter. **Use** CLIs, dev tools, security, docs. **Avoid** mainstream consumer, long body text in mono. **A11y** ASCII art gets `aria-hidden="true"` plus a text alternative; screen readers read every box character.
```css
body { background:#0c0c0c; color:oklch(.86 .18 145); font:400 15px/1.55 "JetBrains Mono",ui-monospace,monospace; }
.prompt::before { content:"$ "; color:oklch(.7 .02 145); }
.cursor::after { content:"▋"; animation:blink 1s steps(1) infinite; } @keyframes blink { 50% { opacity:0; } }
pre.ascii { line-height:1; }
```
**Refs:** https://charm.land/
#### 27. Cinematic dark WebGL (agency) — full-bleed real-time 3D, post-processing, smooth scroll, sound
**Tokens** (loud 5 · a11y High · durable in agency tier): near-black + 1–2 cinematic light colors · huge display type · bloom, grain, chromatic aberration · preloader · motion 5. **Use** agencies, launches, automotive, sports personalities, entertainment. Awwwards listings tag Igloo Inc "Site Of The Year 2024" and show SOTY 2025 badges on "Lando Norris" (OFF+BRAND.) and "Messenger" (abeto). **Avoid** repeat-use apps, SEO content, low-end markets. **A11y** real DOM text over the canvas, keyboard path, static/reduced-motion mode. Build details → `3d-webgl.md`.
```css
canvas.gl { position:fixed; inset:0; z-index:-1; }
.content { position:relative; }        /* all copy is DOM text, never baked into the scene */
@media (prefers-reduced-motion:reduce) { canvas.gl { display:none; } body { background:#000 url(poster.avif) center/cover fixed; } }
```
**Refs:** https://lusion.co/ · https://activetheory.net/ · https://www.igloo.inc/ · https://landonorris.com/ · https://messenger.abeto.co/
#### 28. Aurora / gradient mesh — soft blurred multi-hue light fields
**Tokens** (loud 3 · a11y Med · cyclical): 3–5 analogous saturated hues as radial blobs on a light or dark base · grain on top to hide banding · plain or glass cards above · slow drift 20–40s. **Use** a single hero or section in fintech, AI, SaaS, music marketing. **Avoid** as the whole identity; purple→blue mesh is the #1 AI tell (§5). **A11y** pin text to a calm zone or plate; stop drift under reduced motion.
```css
.aurora { background:
  radial-gradient(40% 50% at 20% 30%, oklch(.75 .17 160 / .9), transparent 70%),
  radial-gradient(35% 45% at 80% 20%, oklch(.7 .19 40 / .85), transparent 70%),
  radial-gradient(50% 60% at 60% 85%, oklch(.65 .2 330 / .8), transparent 70%), oklch(.97 .01 90);
  background-size:150% 150%; animation:drift 30s ease-in-out infinite alternate; }
@keyframes drift { to { background-position:100% 50%; } } @media (prefers-reduced-motion:reduce) { .aurora { animation:none; } }
```
**Refs:** https://stripe.com/
#### 29. AI-native / generative UI — conversation plus generated components; the content leads, the chrome recedes
**Tokens** (loud 1 · a11y Med · durable): calm neutral chrome + one accent · readable answer type (serif or sans, 16–18px, ≤72ch) · composer radius 16–24 · minimal shadow · motion = streaming cursor, subtle shimmer. Pattern: tool calls render real components (AI SDK: parts typed `tool-${name}` with states `input-available` → loading, `output-available` → render, `output-error` → recover). Brand characters are a 2026 way to give agents a face. **Use** assistants, copilots, AI search. **Avoid** turning every screen into chat; sparkle icons + purple gradients. **A11y** stream into a polite live region by sentence or block, not per token; move focus deliberately when a component appears. Patterns → `product-patterns.md`.
```css
.answer { max-width:72ch; font:400 1.0625rem/1.65 "Source Serif 4",serif; }
.composer { position:sticky; bottom:1rem; border:1px solid var(--line); border-radius:20px; background:var(--surface); }
.thinking { background:linear-gradient(90deg,var(--muted) 40%,var(--text) 50%,var(--muted) 60%) 0 0/200% 100%;
  -webkit-background-clip:text; background-clip:text; color:transparent; animation:shimmer 1.6s linear infinite; }
@keyframes shimmer { to { background-position:-200% 0; } } @media (prefers-reduced-motion:reduce) { .thinking { animation:none; color:var(--muted); } }
```
**Refs:** https://ai-sdk.dev/docs/ai-sdk-ui/generative-user-interfaces · https://v0.app/
#### 30. Cyberpunk — neon on black, acid yellow, clipped corners, glitch, HUD frames
**Tokens** (loud 5 · a11y High · cyclical): black + acid yellow + magenta + cyan · condensed tech display + mono · chamfered corners via `clip-path` · scanlines · motion glitch. **Use** games, esports, hackathons, music, web3 events. **Avoid** trust-critical finance, health. **A11y** WCAG 2.3.1: no more than 3 flashes per second; neon text on black halates — keep body text off-white.
```css
.cp { --cut:14px; background:oklch(.9 .19 105); color:#0a0a0a;
  clip-path:polygon(0 0,calc(100% - var(--cut)) 0,100% var(--cut),100% 100%,var(--cut) 100%,0 calc(100% - var(--cut))); }
.cp-glitch { text-shadow:2px 0 oklch(.7 .25 330), -2px 0 oklch(.8 .15 200); }
.scanlines::after { content:""; position:absolute; inset:0; pointer-events:none; background:repeating-linear-gradient(transparent 0 2px, oklch(0 0 0 / .25) 2px 3px); }
```
**Refs:** https://www.cyberpunk.net/ · https://daisyui.com/docs/themes/ ("cyberpunk", "synthwave", "retro" themes)

### E. Retro and nostalgia (31–37)
#### 31. Y2K / chrome — liquid chrome type, glossy pills, starbursts, electric blue and hot pink
**Tokens** (loud 4 · a11y Med · fad/cyclical): chrome/silver gradients, electric blue, teal, hot pink, lime · extended or chunky display (Zen Dots, Bebas Neue; paid: Monument Extended) with chrome as an effect · pill radius · glossy highlights · motion 3. **Use** fashion, beauty, music, Gen-Z drops, creator merch. **Avoid** B2B, regulated. **A11y** chrome text contrast varies along the gradient → add a dark stroke, keep it to display sizes, provide a solid `color` fallback.
```css
.chrome { color:#3a414a; }   /* fallback */
@supports (background-clip:text) or (-webkit-background-clip:text) {
  .chrome { background:linear-gradient(180deg,#fdfdfd 0%,#b9c0c8 45%,#fff 50%,#6e7782 55%,#d9dee3 100%);
    -webkit-background-clip:text; background-clip:text; color:transparent; -webkit-text-stroke:1px oklch(.35 .02 250); } }
.star { width:48px; aspect-ratio:1; background:linear-gradient(135deg,#fff,#9ad0ff); clip-path:polygon(50% 0,61% 39%,100% 50%,61% 61%,50% 100%,39% 61%,0 50%,39% 39%); }
```
**Refs:** https://webflow.com/blog/y2k-aesthetic
#### 32. Retro-futurism / synthwave — 80s-imagined future: dusk gradients, neon grid floor, striped sun
**Tokens** (loud 4 · a11y Med · cyclical): deep indigo/black, magenta→orange→yellow sun, cyan · chrome or neon display · perspective grid · glow · motion = scrolling grid. Industrial variant (Teenage Engineering, Nothing): off-white hardware, dot-matrix, orange accents. **Use** games, music, events, conference pages, campaigns. **Avoid** daily-use apps. **A11y** glow text halates; stop grid motion under reduced motion.
```css
.floor { position:absolute; inset:auto -50% 0; height:50vh; transform:perspective(300px) rotateX(60deg); transform-origin:bottom;
  background:linear-gradient(90deg,oklch(.7 .25 340) 2px,transparent 2px) 0 0/60px 60px, linear-gradient(oklch(.7 .25 340) 2px,transparent 2px) 0 0/60px 60px; }
.sun { width:240px; aspect-ratio:1; border-radius:50%; background:linear-gradient(oklch(.88 .17 90),oklch(.65 .25 350));
  mask:linear-gradient(#000 50%,transparent 0) top/100% 100% no-repeat, repeating-linear-gradient(#000 0 12px,transparent 12px 18px); }
```
**Refs:** https://trends.daisyui.com/trend/synthwave-outrun/ · https://teenage.engineering/
#### 33. Vaporwave — ironic 90s consumer-tech nostalgia: pastel gradients, Win95 chrome, statues, VHS
**Tokens** (loud 4 · a11y Med–High · fad): pastel pink, teal, lavender · serif or Win95 system type, wide letter-spacing · checkerboards, palms, VHS noise · motion 2–3. **Use** music, art projects, ironic campaigns. **Avoid** anything serious. **A11y** full-width Unicode "ＡＥＳＴＨＥＴＩＣ" is read letter by letter → use CSS `letter-spacing` on normal text; decorative Japanese text must be real, proofread language or dropped.
```css
.vapor { background:linear-gradient(oklch(.85 .1 340), oklch(.85 .08 200)); }
.vapor h1 { letter-spacing:.5em; text-transform:uppercase; font-family:"Times New Roman",serif; color:oklch(.98 .02 340); text-shadow:3px 3px 0 oklch(.65 .15 200); }
.win95 { background:#c0c0c0; border:2px solid; border-color:#fff #808080 #808080 #fff; font:12px/1.2 Tahoma,sans-serif; }
```
**Refs:** https://en.wikipedia.org/wiki/Vaporwave
#### 34. Memphis (1980s) — clashing brights, squiggles, terrazzo, primitive shapes, thick outlines
**Tokens** (loud 4 · a11y Med · cyclical): brights + pastels + black/white patterns · geometric display · zigzags, dots, confetti · motion 2–3. **Use** events, kids/edu, playful retail, music. **Avoid** trust-critical. **A11y** pattern never sits behind text.
```css
.memphis { background-color:oklch(.95 .05 95);
  background-image:radial-gradient(oklch(.2 0 0) 2px,transparent 2.5px), linear-gradient(135deg,transparent 45%,oklch(.7 .18 350) 45% 55%,transparent 55%);
  background-size:24px 24px, 80px 80px; }
.squiggle { height:12px; background:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='40' height='12'%3E%3Cpath d='M0 6 Q10 0 20 6 T40 6' fill='none' stroke='%23000' stroke-width='3'/%3E%3C/svg%3E") repeat-x; }
```
**Refs:** https://memphis.it/ · https://en.wikipedia.org/wiki/Memphis_Group
#### 35. Corporate Memphis ("Alegria") — flat figures, long limbs, tiny heads, purple/blue skin; and why it aged
Facebook's 2017 "Alegria" system by BUCK became the default tech illustration ~2017–2022. **Why it aged:** copy-paste systems made every startup look alike; recolored identical bodies read as token diversity; the utopian optimism felt sanitized; it signaled "cheap illustration bought by the yard". By 2022 brands moved back to 3D-like skeuomorphism (Fast Company via Wikipedia); by 2023 it had become "a form of parody". **Tokens** (loud 3 · a11y Low · dated). **Use** only when you need neutral inclusive figures fast — then make it yours: a distinctive line, brand palette, realistic proportions, product-specific scenes. **Better:** commissioned illustration with a recognizable hand, real product UI, real photography, a brand character.
```css
.illo { --skin-1:oklch(.62 .08 50); --cloth:var(--brand-500); color:var(--ink); }
.illo [data-fill="skin"] { fill:var(--skin-1); }  .illo [data-fill="cloth"] { fill:var(--cloth); }
.illo path { stroke:currentColor; stroke-width:1.5; vector-effect:non-scaling-stroke; }   /* a line + brand palette = not generic */
```
**Refs:** https://en.wikipedia.org/wiki/Corporate_Memphis
#### 36. Art Deco — symmetry, gold rules, sunbursts, stepped and chevron ornament
**Tokens** (loud 3 · a11y Med · cyclical): black/navy/emerald + ivory + gold `oklch(.78 .12 85)` · geometric display (Poiret One) over a sturdy text face · radius 0 with stepped corners · double rules · motion 2. **Use** hospitality, bars, galas, spirits, theater, jewelry. **Avoid** tech utility. **A11y** thin display faces only ≥24px; gold on ivory fails — gold for ornament, ivory/ink for text.
```css
.deco { background:oklch(.16 .01 260); color:oklch(.95 .02 90); border:1px solid oklch(.78 .12 85); outline:1px solid oklch(.78 .12 85); outline-offset:6px; }
.deco h1 { font:400 clamp(2.5rem,6vw,5rem)/1 "Poiret One",serif; letter-spacing:.12em; text-transform:uppercase; text-align:center; }
.sunburst { background:repeating-conic-gradient(from -90deg at 50% 100%, oklch(.78 .12 85) 0 2deg, transparent 2deg 10deg); }
```
**Refs:** https://blog.spoongraphics.co.uk/articles/showcase-30-art-deco-inspired-designs-artworks (inspiration gallery)
#### 37. Pixel / retro game — limited palettes, pixel fonts, hard edges, stepped animation
**Tokens** (loud 4 · a11y Med · cyclical): 16-color palettes (PICO-8 style) · pixel fonts (Press Start 2P, VT323, Silkscreen) for headings/labels only · radius 0, notched corners · `steps()` animation at 8–12 fps. **Use** games, gamified learning, badges, side projects. **Avoid** long text, older audiences. **A11y** body copy in a readable face; keep real text, not bitmaps.
```css
img.sprite, canvas.pixel { image-rendering:pixelated; }
.px { font:16px/1.5 "Press Start 2P",monospace; }   /* headings only; ≥16px */
.px-box { background:#fff; margin:4px; box-shadow:0 -4px #000, 0 4px #000, -4px 0 #000, 4px 0 #000; }   /* notched pixel corners */
.walk { --f:32px; width:var(--f); aspect-ratio:1; background:url(sprite.png) 0 0/auto 100%; animation:walk .6s steps(4) infinite; }  /* 4-frame strip */
@keyframes walk { to { background-position-x:calc(-4 * var(--f)); } }
```
**Refs:** https://poolsuite.net/ · https://www.lexaloffle.com/pico-8.php

### F. Warm and human (38–42)
#### 38. Organic / earthy — clay, sand, olive, bark; soft serif; blob shapes; natural light
**Tokens** (loud 2 · a11y Low–Med · durable): Mocha-Mousse-like browns (Pantone 2025), clay, olive, sand, cream · soft serif (Fraunces with `SOFT`/`WONK` axes) + humanist sans · organic radii · warm soft shadows · paper/linen texture · slow motion. **Use** food, wellness, sustainability, outdoor, skincare. **Avoid** trading, dev tools. **A11y** earthy mid-tones on sand often fail for text; text uses bark/ink.
```css
:root { --sand:oklch(.93 .03 80); --clay:oklch(.62 .11 45); --olive:oklch(.5 .07 120); --bark:oklch(.3 .03 60); }
.blob { border-radius:63% 37% 54% 46% / 55% 48% 52% 45%; background:var(--clay); }
h1 { font-family:"Fraunces",serif; font-variation-settings:"SOFT" 100,"WONK" 1; color:var(--bark); }
.card { background:var(--sand); border-radius:20px; box-shadow:0 10px 30px oklch(.45 .06 60 / .15); }
```
**Refs:** https://www.patagonia.com/ · https://www.allbirds.com/
#### 39. Soft pastel — high-lightness, low-chroma surfaces anchored by one deep color
**Tokens** (loud 2 · a11y Med · durable): pastels at L .88–.95, C .04–.08 for surfaces only + one deep anchor for text and actions · rounded sans · radius 16–24 · diffuse shadows · gentle motion. **Use** beauty, wellness, parenting, femtech, journaling. **Avoid** urgency, data-heavy. **A11y** pastel never carries text or is the only button fill.
```css
:root { --blush:oklch(.92 .04 10); --mint:oklch(.93 .05 165); --lilac:oklch(.9 .05 300); --anchor:oklch(.35 .08 300); }
.btn { background:var(--anchor); color:#fff; border-radius:999px; }
.tile { background:var(--mint); color:var(--anchor); border-radius:20px; }
```
**Refs:** https://www.glossier.com/ · https://www.headspace.com/
#### 40. Hand-drawn / doodle — sketchy strokes, marker highlights, handwritten annotations
**Tokens** (loud 3 · a11y Low–Med · durable niche): paper white, ink, highlighter yellow · handwriting (Caveat, Kalam) for annotations only · rough SVG borders (Rough.js) · arrows, circles, underlines · motion = draw-on strokes. **Use** education, whiteboards, onboarding, indie products. **Avoid** legal/finance precision. **A11y** script fonts never for body or inputs.
```css
.scribble path { stroke-dasharray:1; stroke-dashoffset:1; animation:draw .8s ease-out forwards; }   /* <path pathLength="1"> */
@keyframes draw { to { stroke-dashoffset:0; } }
.marker { background:linear-gradient(transparent 55%, oklch(.92 .16 100) 55% 90%, transparent 90%); }
.note { font:400 1.375rem/1.2 "Caveat",cursive; rotate:-2deg; }
```
**Refs:** https://excalidraw.com/ · https://www.tldraw.com/
#### 41. Grain + duotone — two-color photo treatment and film-grain noise; analog, "made by a person"
**Tokens** (loud 3 · a11y Low–Med · cyclical, rising with anti-AI crafting): shadow color + highlight color for photos · SVG noise at 4–10% opacity (>~50% reads as static) · editorial type · motion 1–2. **Use** music and culture, editorial, campaigns, brand refreshes. **Avoid** where true color matters (fashion product shots, food). **A11y** text on duotone images needs a plate or scrim.
```css
.duo { position:relative; background:oklch(.35 .15 265); }
.duo img { filter:grayscale(1) contrast(1.15); mix-blend-mode:screen; }
.duo::after { content:""; position:absolute; inset:0; background:oklch(.85 .17 90); mix-blend-mode:multiply; pointer-events:none; }
.grain::before { content:""; position:absolute; inset:0; pointer-events:none; opacity:.08; mix-blend-mode:overlay;
  background:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='200'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E"); }
```
**Refs:** https://css-tricks.com/grainy-gradients/
#### 42. Dopamine / vibrant — a full multi-hue system, color-blocked sections, big cheerful type
**Tokens** (loud 5 · a11y Med · cyclical): 4–5 saturated hues as a system (not one accent), separated by luminance · bold rounded or condensed display · playful shapes · bouncy motion. **Use** consumer apps, delivery, youth, events, edtech, lifestyle and beauty. **Avoid** medical, legal, luxury. **A11y** white on yellow/lime fails; complementary pairs vibrate; check each block's text pairing.
```css
:root { --sun:oklch(.88 .17 95); --grape:oklch(.5 .2 305); --mint:oklch(.85 .13 165); --tomato:oklch(.66 .21 30); --ink:oklch(.2 .03 280); }
section:nth-of-type(4n+1) { background:var(--sun); color:var(--ink); }  section:nth-of-type(4n+2) { background:var(--grape); color:#fff; }
section:nth-of-type(4n+3) { background:var(--mint); color:var(--ink); }  section:nth-of-type(4n) { background:var(--tomato); color:var(--ink); }
```
**Refs:** https://www.duolingo.com/ · https://trends.daisyui.com/trend/dopamine-design/

## 4. Trends 2025–2026

Verdict key: **durable** = build on it; **cyclical** = fine for a campaign or brand refresh, expect to date in 2–4 years; **fad** = only for short-lived pages.

| Trend | Evidence (date) | Verdict | Use it like this |
|---|---|---|---|
| Material translucency / Liquid Glass | Apple 2025-06-09; NN/g critique 2025-10-10; iOS 26.1 Clear/Tinted; WWDC 2026-06-08 readability rebuild + clear↔tinted slider | Durable on Apple platforms; decorative web glass cyclical | Native: system components. Web: floating chrome only, legible default, user opt-out (#17) |
| Expressive emphasis (shape, size, color, springs) | Material 3 Expressive, I/O May 2025; 46 studies, 18k+ people, key actions found up to 4× faster | Durable | Enlarge and color the one key action; keep labels and list patterns |
| Anti-AI crafting, "imperfect by design", texture | Creative Bloq 2025-12-23 (Landor); Canva 2026 report via Mediaweek 2025-12-16 (lo-fi searches +527%, DIY/collage +90%); Adobe 2025-12-12 (organic & imperfect); KOTA 2026 | Durable while AI imagery is everywhere; specific textures cyclical | Real photos, hand-made marks, grain on brand surfaces; product UI stays precise (KOTA) |
| Type as design, kinetic and variable type | Figma 2026 "bold typography"; Creative Bloq "Type as design"; Webflow 2025-12-23 "dynamic text treatments" | Durable | One display family carries identity; motion with reduced-motion fallback (#15) |
| Saturated color, full color systems | Figma 2026 vibrant palettes; Webflow "full color systems" over one accent; Adobe "high-energy" | Cyclical | Multi-hue systems with luminance-separated roles (#42) |
| Calm neutral baseline | Pantone 2026 Cloud Dancer 11-4201 (white neutral, 2025-12-04); Canva "opt-out era" (clean layouts, serifs, +54%); Creative Bloq "More from minimalism" | Durable | Quiet base + one expressive layer (§6) |
| Bento grids | Ubiquitous since ~2023; easy with CSS Grid | Durable layout; glossy-card look dates | Mixed spans, real media, 6–9 tiles (#8) |
| Linear-style dark SaaS | LogRocket 2025-06-07: Linear cut color, Raycast dropped gradient, oversaturation | Peaked; copies read as fad | Borrow density, contrast discipline, keyboard-first — not the glow (#25) |
| Neo-brutalism, anti-design, zine | Figma 2026; KOTA "controlled chaos"; Canva Zinegeist +77% (Mexico), Explorecore +85% | Cyclical (NN/g covered it in 2017) | Creator/indie/youth brands; obey NN/g's usability rule (#10–12) |
| Retro-futurism, Y2K chrome, pixel | Figma 2026 "retrofuturism"; Webflow Y2K guide | Fad/cyclical | Drops, merch, event pages — not app shells |
| Collage and layered storytelling | Figma 2026 collage; Adobe collage/layered + freeform zine layouts; Creative Bloq layered storytelling | Cyclical | Editorial and campaign sections (#14) |
| Immersive 3D / WebGL | Listed first in Figma 2026; Awwwards SOTY 2024 tag on Igloo Inc, SOTY 2025 badges on Lando Norris and Messenger | Durable in the agency tier | Brand and launch pages; never in task flows (#27) |
| Brand characters for AI agents | Creative Bloq 2026 (BUCK; Notion AI's character) | Emerging | Give the agent one consistent persona instead of sparkles (#29) |
| Neumorphism (still listed by Figma 2026) | Figma 2026 | Fad; contrast-hostile | Accent on non-critical controls only (#18) |
| Sustainable / lightweight web | Figma 2026; KOTA "slow brand" | Durable | Budget blur, WebGL and video; they cost battery and energy |

Pattern behind the list: 2025 gave AI "bold 3D forms and unapologetically digital aesthetics" (FutureBrand, in Creative Bloq); 2026 reports reward visible human craft and calm bases with one loud move. Use trends as accents on a durable base, never as the base.

## 5. Escaping generic AI-looking UI

Cause: without direction, models fall back to the statistical center of web training data ("distributional convergence", Anthropic 2025-11-12). Fix it by deciding the style in §1 *before* writing markup, then checking the output against these tells.

| Tell | Concrete move instead |
|---|---|
| Inter / Roboto / system font on everything | Take type from the chosen catalog entry. One distinctive family used decisively (e.g. Bricolage Grotesque, Newsreader, IBM Plex, JetBrains Mono, Fraunces), weight contrast 200 vs 800, hero size ≥3× body. Rotate choices across projects — models also converge on Space Grotesk |
| Purple→blue gradient on white (Tailwind `indigo-500` legacy) | Derive the palette from the subject (a material, place, era, IDE theme); dominant color 60–70%, sharp accent ≤10%. If you need a gradient: two adjacent hues interpolated `in oklch`, plus grain — or none |
| Centered hero + three icon feature cards | Pick a hero archetype: split (claim left, real product right), product-as-hero (live UI), editorial lede (headline, byline, image), statement + proof (number, quote, logo), bento with mixed spans. Give each section a different layout |
| Emoji as icons | One icon set at one stroke width sized to cap height (Lucide, Phosphor, Material Symbols), typographic markers (01, §, →), or custom glyphs for the 3–5 hero concepts |
| Uniform 8px radius | Radius scale from the style: 0 (Swiss, brutal), 2–4 (editorial), 12–28 (soft), pills for actions only; nested radius = outer − padding |
| Gray drop shadow `0 4px 6px rgba(0,0,0,.1)` on every card | Choose one depth model: none (borders, tonal surfaces) · hue-tinted layered shadows · hard offset · translucency. One elevation means one thing |
| Stock 3D blobs, glossy orbs, abstract mesh | Real product UI, real photography, data visualization, commissioned illustration or a brand character tied to the product |
| Gradient headline + glass navbar + glowing card borders together | One signature effect only (§6) |
| Everything fades up 20px on scroll at one duration | One orchestrated load (stagger 40–80ms), scroll motion only where it explains something; reduced-motion path (`motion.md`) |
| Pure #000 dark mode with neon accents | Tinted near-black (L .13–.18) with 3–4 surface steps; lower accent chroma in dark |
| Generic copy ("Supercharge", "Seamless", "Unlock") and fake logo rows | Specific nouns, numbers and the user's job; real proof or no proof section |
| Only the happy path designed | Hover, focus, empty, loading, error and success states — missing states are the strongest "unreviewed AI" signal |

Prompt-side fixes when generating UI: name the catalog style and number, list 3 explicit bans (e.g. "no purple, no glass, no emoji"), give 2 reference URLs, and ask for 2–3 distinct directions before building one.

## 6. Mixing rules

- **Formula:** 1 base style + at most 1 accent technique + optionally 1 low-opacity texture. Never two accents.
- **The base owns** grid, type families, palette roles, radius scale, depth model, motion personality. **The accent owns** one effect or material applied to ≤2 component types or one hero moment, ≤1 occurrence per viewport, ≤15% of surface area. The accent takes its colors from the base palette.
- **One depth model per product:** flat-tonal, soft-shadow, hard-offset or translucent. Mixing two (e.g. hard brutal shadows on a page with glass cards) is the most common cause of mush.
- **≤2 type families** (+ mono for code/data), one icon set, one radius scale, 2–3 motion durations, 2 easings.

| Base | Accents that work | Clashes |
|---|---|---|
| Swiss 1 / Flat 2.0 7 | Kinetic type 15, grain 41, one Aurora 28 hero, Liquid-Glass-style nav 17 | Claymorphism, neumorphism |
| Editorial 3 | Collage 14, grain + duotone 41, hand-drawn notes 40 | Neon glow, glitch |
| Quiet luxury 2 | Grain 41, serif kinetic hero 15, subtle glass nav 17 | Dopamine color, hard shadows |
| Dark dev 25 | One Aurora glow 28, terminal motifs 26, bento 8 | Pastels, clay |
| Neo-brutal 10 | Dopamine palette 42, pixel 37, hand-drawn 40 | Glass, soft shadows |
| Organic 38 | Hand-drawn 40, grain 41, collage 14 | Chrome, cyberpunk |
| AI-native 29 | Editorial type 3, brand character, restrained Aurora 28 | Purple-blue mesh + sparkles everywhere |
| M3 Expressive 21 | Playful 3D 24 in empty states and onboarding | Glass on content surfaces |

**Consistency across pages**
- Marketing and product share tokens; marketing may run one loudness step higher; the app shell stays ≤2 whatever the brand.
- The signature move appears at fixed slots (hero, section break, CTA band) on every page, not randomly.
- Keep a vocabulary of 3–4 section layouts and reuse them; one image treatment rule (all duotone or none); dark-mode parity for every component.
- Drift test: screenshot 5 key pages at 25% zoom side by side. If one page looks like another brand, fix the tokens or the page, not the style statement.

## Pitfalls

- Glass text readable in the mockup, illegible in production → contrast checked on one screenshot → test over a white photo, a black photo and dense text; raise tint alpha or add a scrim.
- Reduce-transparency users on Safari still get glass → `prefers-reduced-transparency` unsupported in Safari (MDN BCD, 2026-10) → legible default plus an in-UI setting.
- Scroll jank on mid-range phones → many `backdrop-filter` layers re-sample every frame → ≤3 per viewport, never on list rows, never animate blur radius; check older Safari needs `-webkit-backdrop-filter` (unprefixed only from 18).
- Full-screen grain overlay stutters → fixed blended overlay repaints on scroll → limit to the hero, small tiled image, `pointer-events:none`, or bake grain into images.
- Gradient/chrome text disappears → `color:transparent` without a support check → solid `color` first, enhancement inside `@supports`.
- Neumorphic or glass buttons not recognized as buttons → depth is the only affordance → add fill, label or a ≥3:1 border.
- Kinetic type reads as "S T R E T C H" to screen readers or makes users ill → split spans exposed, no reduced-motion → `aria-hidden` spans plus a visually-hidden full string, and a `prefers-reduced-motion` path.
- Glitch effects trigger seizure risk → flashing >3 per second (WCAG 2.3.1) → slow or remove.
- Decorative foreign scripts (katakana in vaporwave, faux-Thai) read as nonsense to native readers → proofread with a speaker or drop.
- Style copied from the category leader → product indistinguishable → run the differentiation criterion in §1 before committing.

## Sources

- Brand personality: Aaker 1997, "Dimensions of Brand Personality" — https://gwern.net/doc/economics/1997-aaker.pdf
- Liquid Glass (Apple): Newsroom 2025-06-09 — https://www.apple.com/newsroom/2025/06/apple-introduces-a-delightful-and-elegant-new-software-design/ · HIG Materials — https://developer.apple.com/design/human-interface-guidelines/materials · SwiftUI `glassEffect(_:in:)` — https://developer.apple.com/documentation/swiftui/view/glasseffect(_:in:) · HIG Designing for visionOS — https://developer.apple.com/design/human-interface-guidelines/designing-for-visionos
- Liquid Glass critique and changes: NN/g "Liquid Glass Is Cracked" 2025-10-10 — https://www.nngroup.com/articles/liquid-glass/ · Infinum — https://infinum.com/blog/apples-ios-26-liquid-glass-sleek-shiny-and-questionably-accessible/ · Tom's Guide (iOS 26.1 Clear/Tinted) — https://www.tomsguide.com/phones/iphones/ios-26-1-lets-you-adjust-liquid-glass-transparency-on-your-iphone-heres-how-to-do-it · TechCrunch (WWDC 2026-06-08) — https://techcrunch.com/2026/06/08/apple-is-tweaking-its-controversial-liquid-glass-design/
- Translucency on the web and Windows: LogRocket "Liquid Glass effects with CSS and SVG" 2025-12-08 — https://blog.logrocket.com/how-create-liquid-glass-effects-css-and-svg/ · Microsoft Acrylic — https://learn.microsoft.com/en-us/windows/apps/design/style/acrylic · NN/g "Glassmorphism" 2024-06-07 — https://www.nngroup.com/articles/glassmorphism/
- Material 3 Expressive: Google Design research — https://design.google/library/expressive-material-design-google-research · Material Design 3 — https://m3.material.io/
- Style histories and recipes: NN/g "Brutalism and Antidesign" 2017 — https://www.nngroup.com/articles/brutalism-antidesign/ · Hype4 "Claymorphism in User Interfaces" — https://hype4.academy/articles/design/claymorphism-in-user-interfaces · Wikipedia Neumorphism — https://en.wikipedia.org/wiki/Neumorphism · Wikipedia Corporate Memphis — https://en.wikipedia.org/wiki/Corporate_Memphis · LogRocket "Linear design" 2025-06-07 — https://blog.logrocket.com/ux-design/linear-design · Webflow "Y2K aesthetic" — https://webflow.com/blog/y2k-aesthetic · CSS-Tricks "Grainy Gradients" 2021 — https://css-tricks.com/grainy-gradients/
- Trend reports: Figma "Top Web Design Trends for 2026" — https://www.figma.com/resource-library/web-design-trends/ · Adobe Express "Design trends for 2026" 2025-12-12 — https://www.adobe.com/express/learn/blog/design-trends-2026 · Creative Bloq 2026 graphic trends 2025-12-23 — https://www.creativebloq.com/design/graphic-design/texture-warmth-and-tactile-rebellion-the-big-graphic-design-trends-for-2026 · Mediaweek on Canva's 2026 report 2025-12-16 — https://www.mediaweek.com.au/why-designs-next-flex-is-being-imperfect · KOTA 2026 — https://kota.co.uk/blog/branding-inspiration-brand-design-trends-for-2026 · Webflow 2026 trends (summary) — https://www.plushcap.com/content/webflow/blog/webflow-8-web-design-trends-to-watch-in-2026 · Awwwards Igloo Inc case study — https://www.awwwards.com/igloo-inc-case-study.html
- Generic AI look: Anthropic "Improving frontend design through Skills" 2025-11-12 — https://claude.com/resources/articles/improving-frontend-design-through-skills · prg.sh "Why Your AI Keeps Building the Same Purple Gradient Website" 2025-10-26 — https://prg.sh/ramblings/Why-Your-AI-Keeps-Building-the-Same-Purple-Gradient-Website
- Implementation: AI SDK Generative UI — https://ai-sdk.dev/docs/ai-sdk-ui/generative-user-interfaces · daisyUI themes and trend pages — https://daisyui.com/docs/themes/ · https://trends.daisyui.com/trend/dopamine-design/ · https://trends.daisyui.com/trend/synthwave-outrun/ · MDN browser-compat-data (support facts as of 2026-10-10) — https://github.com/mdn/browser-compat-data
