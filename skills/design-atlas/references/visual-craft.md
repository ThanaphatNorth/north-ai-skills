# Visual craft: the finish layer

> Read when: a screen is correct but looks ordinary, flat, cheap or like a template; the user asks for more beautiful, premium, polished, refined or "designed"; setting the expression tokens (Step 5); finishing any UI on the calm dial, where craft is the whole signature (Step 6); running the beauty bar on screenshots (Step 7); critiquing a UI for visual quality.

**Contents:** 1 Where beauty comes from · 2 Light and depth · 3 Edges, corners, surfaces · 4 Type finish · 5 Colour finish · 6 Space, alignment, optical corrections · 7 Composition moves · 8 Interaction finish · 9 The beauty bar · Pitfalls · Sources

Token names are those of `templates/tokens-starter.css`. The recipes run in `examples/craft-finish/` (one page designed from its subject, light and dark, a scoped dark sheet, scroll and parallax with a job; checked in Chrome at 390 and 1280 px): open it before writing your own.

**Finish is not a style.** These recipes make a decided design exact; they do not decide it. Aura, grain, glow, pills and a serif accent word stacked on a page are themselves one of the looks people read as machine-made (`ai-tells.md` §2). Use a recipe only where the direction has a source for it, and leave the rest out. Concept, storyboard and scroll set pieces: `creative-direction.md`. Choosing a style: `styles-catalog.md`. Token architecture: `design-systems.md`.

## 1. Where beauty comes from

A screen reads as beautiful when three things are true at once: **restraint** (few decisions, repeated exactly), **precision** (every edge, gap and curve is on purpose) and **one idea** (a single thing the eye remembers). Effects add none of the three. Work in this order; each step is cheap to fix before the next one and expensive after it.

| # | Pass | Question it answers | Done when |
|---|---|---|---|
| 1 | Hierarchy in greyscale | What is the one thing this view is about? | Blurred 8 px and with colour removed, the primary element still wins |
| 2 | Space and alignment | What belongs together? | Every gap is a scale step; groups are visible without borders |
| 3 | Type | Does the text have a voice and a rhythm? | Size, weight, tracking and line-height are set per level (§4) |
| 4 | Colour | Where is the brand allowed to be loud? | Accent covers ≤ 10% of the view; neutrals carry the rest |
| 5 | Light and depth | What floats, what sits, what is cut in? | One light source, one depth model (§2) |
| 6 | Motion and detail | Does it answer the hand? | Press, focus, enter and exit feel deliberate (§8) |
| 7 | The signature | What will they remember? | One expression moment, spent on the primary idea |

**Expression budget per view.** The expression tokens are a budget, not a theme to apply everywhere.

| Carrier | Budget | Token |
|---|---|---|
| Display type moment | 1 | `--font-size-display` |
| Gradient surface | 1 | `--gradient-brand` or `--gradient-aura` |
| Glow | 1 (the primary action or the hero object) | `--glow-primary` |
| Accent colour | ≤ 10% of the area | `--accent`, `--primary` |
| Type families | ≤ 2 (+ mono) | `--font-display`, `--font-sans` |
| Depth model | 1 | `--shadow-*` or borders or tonal steps |
| Motion that plays unprompted | 1 orchestrated entrance | `--ease-emphasized-out` |

**By ambition dial** (`creative-direction.md` §1): **calm** = §2–6 and §8 done exactly, nothing else; this is where product UI gets its quality. **Bold** adds one composition move (§7) and spends the whole expression budget. **Cinematic** adds a concept and a scroll story on top of a calm, exact base.

## 2. Light and depth

**One light source for the whole product.** The starter's light sits straight above: shadows fall down (x = 0), top edges are lighter, wells are darker at their top edge. Pick a different angle once (Comeau's example keeps x : y at 1 : 2 on every shadow) and never mix angles.

| Rule | Value |
|---|---|
| Layer shadows | The same ink stacked with offset and blur doubling: 1, 2, 4, 8, 16 px. One layer of `0 6px 6px / .3` reads as a smudge; five layers at α ≈ 0.07 read as soft light |
| Tint the ink | Shadow colour = the surface behind it, darker and more saturated, never plain black. On a `hsl(220 100% 80%)` page Comeau's shadow is `hsl(220 60% 50% / α)`. The starter's `--shadow-ink` is tinted with the neutral hue |
| Higher = larger and softer | More layers, larger offset and blur; never a darker single layer |
| One level, one meaning | card 1 · hover lift 2 · popover 3 · dialog 4 · toast 5 (`design-systems.md` §8) |
| Edge ring instead of a border | `0 0 0 1px` ring as the first shadow layer: black at 6–8% in light, white at 8–9% in dark. It adapts to any background; a solid border colour does not |
| Lit top rim | `inset 0 1px 0 var(--highlight)` on filled buttons and raised dark surfaces |
| Cut-in surfaces | Inputs, tracks, wells: `inset 0 1px 2px var(--shadow-ink)` (Kennedy: light comes from the sky; inset for inputs and pressed controls, outset for cards) |
| Dark mode | Depth comes from lightness steps (`--bg` → `--surface` → `--surface-raised`) and the white edge ring. Shadows are for floating layers only |
| Glow | The element's own colour, one element per view, never grey |

```css
.card    { background: var(--surface); border-radius: var(--card-radius); box-shadow: var(--elevation-card); }
.popover { background: var(--surface-raised); border-radius: var(--radius-lg);
           box-shadow: var(--elevation-popover), inset 0 1px 0 var(--highlight); }  /* ring + stack + lit rim; no border */
.input   { background: var(--surface-sunken); box-shadow: inset 0 1px 2px var(--shadow-ink), 0 0 0 1px var(--border-strong); }
.btn-primary { background: var(--primary); color: var(--primary-foreground);
           box-shadow: var(--glow-primary), inset 0 1px 0 var(--highlight); }
@media (hover: hover) { .card.is-link { transition: box-shadow var(--duration-moderate) var(--ease-out); }
  .card.is-link:hover { box-shadow: var(--elevation-raised); } }
```

Animate a shadow by cross-fading `box-shadow` on small elements only. On large or many elements, fade the opacity of a pseudo-element that already holds the second shadow (`motion.md` §13).

## 3. Edges, corners, surfaces

- **Concentric corners.** Outer radius = inner radius + padding. Equal radii on a nested pair look pinched (`design-systems.md` §8 has the `calc()` recipe).
- **One corner personality.** `--shape-control` and `--shape-container` decide it for the product (sharp 0–4, soft 6–12, round 16+). Pills (`--shape-pill`) are for actions and tags, never for containers of text.
- **Hairlines that adapt.** On plain surfaces use `--border`. On tinted, gradient or photographic surfaces use an alpha hairline: `border: 1px solid color-mix(in oklch, currentColor 12%, transparent)`.
- **Outline every image and avatar**, so light images do not bleed into light pages: `outline: 1px solid light-dark(rgb(0 0 0 / .1), rgb(255 255 255 / .1)); outline-offset: -1px`.
- **Separate with the cheapest tool that works:** space first, then a tonal step, then a hairline. A border on every card plus a shadow plus a background change is three signals for one fact.
- **Clip the content, not the shadow.** A rounded card with media uses an inner wrapper with `overflow: clip` and the inner radius; the card itself keeps its shadow.
- **Texture.** Large flat or gradient areas get grain: it hides banding and gives the colour a surface. Heroes and feature panels only (a full-page fixed grain layer repaints on scroll).

```css
.panel { position: relative; isolation: isolate; background: var(--gradient-aura), var(--surface); }
.panel::after { content: ""; position: absolute; inset: 0; z-index: -1; border-radius: inherit; pointer-events: none;
  background-image: var(--grain); opacity: var(--grain-opacity); }
@supports (corner-shape: squircle) { .app-icon { corner-shape: squircle; } }  /* Chrome 139; enhancement only: tune the radius by eye */
```

- **Glass** belongs on chrome that floats over content (nav bars, sheets), not on content cards: ≤ 3 `backdrop-filter` layers per viewport, never on list rows (`styles-catalog.md` Pitfalls).

## 4. Type finish

| Detail | Rule |
|---|---|
| Tracking falls as size grows | Inter's published curve: `tracking(em) = −0.0223 + 0.185 · e^(−0.1745 · px)` → 12 px ≈ 0 · 14 px −0.006 · 16 px −0.011 · 20 px −0.017 · 24 px −0.019 · 32 px and up −0.022. Display faces go further (−0.02 to −0.04em: `--tracking-display`). Tight tracking is for Latin, Greek and Cyrillic only (`typography-layout.md`, Multi-script typography) |
| Line-height falls as size grows | Body 1.5–1.7 · headings 1.15–1.3 · display 0.95–1.1 (Butterick's range for text is 120–145%) |
| Hierarchy before size | Three text colours (`--text`, `--text-muted`, `--text-disabled`) and two weights do most of the work; add a size step last. Text weights ≥ 400; mid-size headings 500–600 |
| One display moment | `font: var(--font-weight-display) var(--font-size-display)/var(--line-height-display) var(--font-display); letter-spacing: var(--tracking-display)`. At least 3× the body size, once per view |
| Wrapping | `text-wrap: balance` on headings and captions (Chromium balances ≤ 6 lines, Firefox ≤ 10); `text-wrap: pretty` on paragraphs |
| Numbers | `font-variant-numeric: tabular-nums` on anything that changes or lines up: prices, timers, tables, counters |
| Real characters | Curly quotes (“ ” ‘ ’), an ellipsis (…) not three dots, an en dash for ranges, a non-breaking space between a number and its unit (`10 MB`) and inside shortcuts (`⌘ K`) |
| Optical size | `font-optical-sizing: auto`; use the display cut for headings when the family has one (Linear sets headings in Inter Display and everything else in Inter) |
| Optical centring | `text-box: trim-both cap alphabetic` on button and badge labels removes the font's built-in leading (Chrome 133, Safari 18.2; keep the padding fallback) |
| Hanging punctuation | `hanging-punctuation: first` on pull quotes (Safari only: enhancement) |

```css
h1, h2, h3 { text-wrap: balance; }
p, li { text-wrap: pretty; }
.display { font: var(--font-weight-display) var(--font-size-display)/var(--line-height-display) var(--font-display);
  letter-spacing: var(--tracking-display); font-optical-sizing: auto; }
.price, .timer, td.num { font-variant-numeric: tabular-nums; }
@supports (text-box: trim-both cap alphabetic) { .btn > span { text-box: trim-both cap alphabetic; } }
```

## 5. Colour finish

- **Greyscale first.** Hierarchy that works without colour survives every theme. Then add one brand hue; a second hue only when it has its own job (Kennedy: design in greyscale, add colour last).
- **Tint the neutrals** toward the brand hue (`--neutral-c` 0.004–0.012). Pure grey next to a saturated brand looks unrelated; pure `#000` and `#fff` in large areas look unfinished unless the style calls for them (`color.md`).
- **Proportion:** neutral 60–70% · secondary 20–30% · accent ≤ 10% (`styles-catalog.md` §5).
- **Use the ramp by job**, as Radix defines its 12 steps: 1–2 page and subtle backgrounds · 3–5 component backgrounds (rest, hover, active) · 6–8 borders · 9–10 solid fills (9 is the purest, highest-chroma step) · 11 low-contrast text · 12 high-contrast text. In the starter's 50–950 ramps that is roughly 50–100 · 100–300 · 200–500 · 500–600 · 700 · 900–950, already wired into the semantic roles.
- **Gradients:** interpolate `in oklch`, keep the two ends within about 60° of hue and 0.15 of lightness, add grain on large areas (`color.md`, Gradients). `--gradient-brand` is built that way for any brand (the brand hue to a hue 40° further round). A brand-to-accent gradient across distant hues goes muddy in the middle. A gradient is a surface, never a body-text background.
- **Text on a coloured surface** takes the surface's own hue at another lightness, or white/black with alpha. Neutral grey on colour looks dirty.
- **Dark mode is designed, not inverted:** tinted near-black (L 0.13–0.18), three or four surface steps, accent chroma lowered a little, shadows replaced by lightness (`color.md`, Dark mode).

## 6. Space, alignment, optical corrections

- **Only scale steps.** A value off the scale is a bug or a new token. Inside a group < between groups < between sections, at about 1 : 1.5–2 per level (`typography-layout.md`, Spacing system).
- **One strong edge per region.** Left-align text blocks to the same line; centre only short, symmetric blocks.
- **Optical beats mathematical:**
  - An icon beside a label gets slightly less padding on the icon's side, because the glyph has air inside its box (`padding-inline: var(--space-3) var(--space-4)`), or fix it inside the SVG.
  - Triangles and other pointed shapes look centred when shifted toward their point; circles and round glyphs overshoot their box a little.
  - A text-only button in a column aligns by its text, not its box: pull it out by its own padding (`margin-inline-start: calc(var(--control-padding-x-md) * -1)`).
  - A block that should look vertically centred sits slightly above the geometric centre (heuristic: give the bottom a little more space than the top).
- **Baseline, not box.** Label/value rows and mixed-size text align with `align-items: baseline`.
- **Hit area larger than the drawing.** Small icons keep their visual size and get a 44 px target:

```css
.icon-btn { position: relative; }
.icon-btn::after { content: ""; position: absolute; inset: 50% auto auto 50%; translate: -50% -50%;
  inline-size: max(100%, var(--target-min)); block-size: max(100%, var(--target-min)); }
```

- **Icons:** one set, one stroke width that matches the text weight beside it, sizes 16 / 20 / 24 (`design-systems.md` §10).

## 7. Composition moves

For the bold dial and above. A page of centred hero + three equal cards has no composition; pick one move per section and vary them down the page. These are practice heuristics: the research for this file found no primary source that gives numbers for them, so check each with the squint test.

| Move | How | Use for |
|---|---|---|
| Asymmetric split | 5/7 or 4/8 columns; text on the narrow side, the object on the wide side, bleeding off one edge | Product hero, feature sections |
| Scale contrast | One element far larger than everything else (display type ≥ 3× body, or a product shot at ≥ 60% of the viewport) | Hook and payoff |
| Breakout grid | A content column with named full-bleed lines; some children escape to the edges (`typography-layout.md`, Layout recipes #2) | Editorial pages, long-form marketing |
| Overlap | An image or card crosses a section boundary or sits under the headline (grid cells sharing an area, or a negative margin of one spacing step) | Depth without effects |
| Type-led hero | No image: display type plus one precise detail (a number, a live status, a small motion) | Brands with a strong voice, tools |
| Product as hero | The real UI, cropped, with the edge ring and a deep layered shadow; never a generic device frame | SaaS, apps |
| Rhythm | Alternate dense and nearly empty sections; one full-bleed band every two or three contained sections; `padding-block: var(--space-section)` | Every long page |
| One deliberate break | A single element off the grid that the subject itself would put there (a stamp, a handwritten note, a tag) | Warmth, personality; once per page |

```css
.split  { display: grid; grid-template-columns: minmax(0, 5fr) minmax(0, 7fr); gap: var(--space-gutter); align-items: center; }
.split > .object { margin-inline-end: calc(var(--space-gutter) * -1); }           /* bleeds off the edge */
.overlap { display: grid; } .overlap > * { grid-area: 1 / 1; }                    /* headline over image */
.overlap > .headline { align-self: end; padding: var(--space-gutter); z-index: 1; }
@media (width < 48rem) { .split { grid-template-columns: minmax(0, 1fr); } .split > .object { margin-inline-end: 0; } }
```

Hero archetypes and the tells of a generic layout: `styles-catalog.md` §5. Grids, bento and container queries: `typography-layout.md`.

## 8. Interaction finish

| Detail | Rule |
|---|---|
| Press feedback | `scale: var(--press-scale)` (0.97) on `:active` for buttons and small cards; never below about 0.9. Larger surfaces scale less |
| Enter | Never from `scale(0)`: start at 0.9 or higher with opacity 0 (Kowalski's example uses 0.93; Freiberg fades dialogs in from about 0.8) |
| Origin | A popover, menu or tooltip grows from its trigger: set `transform-origin` to it (Radix and Base UI expose it as a CSS variable) |
| Duration | Interface animation under 300 ms; 180 ms reads as crisp, 400 ms as sluggish. Decelerating curves for enter and exit |
| Frequency | The more often something is seen, the less it animates. Actions used hundreds of times a day (command palette, keyboard navigation) do not animate |
| Tooltips | The first one waits; while one is open its neighbours open at once. 125 ms, from opacity 0 and scale 0.97 |
| Movement vs colour | Springs for position, size and rotation (`--ease-spring`, `--ease-spring-bouncy`); `--ease-standard` or `--ease-out` for colour and opacity, which never overshoot |
| Transitions, not keyframes, for interactions | A transition retargets when interrupted; a keyframe animation restarts |
| Never `transition: all` | Name the properties; animate `transform` and `opacity`, not layout |
| Entrance | Default: none. The same fade-and-rise on every block is a tell of generated pages (`ai-tells.md` §3). If the concept has one arrival (a stamp landing, a curtain, a sheet being laid down), stage that single event; a generic stagger (each block from `translateY(8px)`, `blur(8px)`, opacity 0, 80–100 ms apart) is for app screens that load data, once |
| Scroll and parallax | On marketing and brand surfaces, movement taken from what the subject physically does, each effect with a job: reveal, depth, wayfinding, pacing, payoff (`ai-tells.md` §6; recipes in `scroll-parallax.md`) |
| Hover | Inside `@media (hover: hover)` so touch does not stick |
| Focus | `:focus-visible` ring, 2 px, 2 px offset, following the element's radius |
| Scroll and touch | `scroll-margin-top` on anchor targets = sticky header height; `touch-action: manipulation` on controls; `overscroll-behavior: contain` in modals and drawers |

```css
.btn { transition: scale var(--duration-spring-fast) var(--ease-spring-bouncy),
                   background-color var(--duration-fast) var(--ease-standard),
                   box-shadow var(--duration-moderate) var(--ease-out); }
.btn:active { scale: var(--press-scale); }
.menu { transform-origin: var(--transform-origin, top left); opacity: 0; scale: 0.94;    /* closed state = exit target */
  transition: opacity var(--duration-moderate) var(--ease-out), scale var(--duration-spring) var(--ease-spring),
              display var(--duration-moderate) allow-discrete, overlay var(--duration-moderate) allow-discrete; }
.menu:popover-open { opacity: 1; scale: 1; }
@starting-style { .menu:popover-open { opacity: 0; scale: 0.94; } }                      /* enter from here */
.enter > * { animation: enter 800ms var(--ease-emphasized-out) both; animation-delay: calc(sibling-index() * 90ms); }
@keyframes enter { from { opacity: 0; translate: 0 8px; filter: blur(8px); } }
@media (prefers-reduced-motion: reduce) { .enter > * { animation: none; } }
```

`sibling-index()` is Newly available (Chrome 138, Firefox 154, Safari 26.2); where it is missing the blocks enter together, which is an acceptable fallback. Reduced motion zeroes the spring durations and `--press-scale` in the starter.

## 9. The beauty bar

Run it on screenshots (`scripts/shoot.mjs`), at 390 and 1280 px, light and dark. Mark each line PASS or FIX with the selector. Lines 1–5 are gates: polish on top of a failed gate is wasted. Before the bar, run the four tests of `ai-tells.md` §8 (source, swap, sibling, tell count): a page that reads as machine-made fails whatever its finish.

| # | Check | Pass looks like |
|---|---|---|
| 1 | Focal point | Blurred 8 px, one element dominates each view; nothing unintended competes |
| 2 | Hierarchy | Three levels readable at a glance (what it is, what matters, what to do) |
| 3 | Space | Every gap on the scale; groups visible without boxes; sections breathe at `--space-section` |
| 4 | Alignment | One strong edge per region; icons and text optically aligned |
| 5 | Type | Tracking and line-height set per size; headings balanced; no stranded word in the hero; real quotes and ellipses |
| 6 | Colour | Accent ≤ 10%; neutrals tinted; no grey text on colour; dark mode designed |
| 7 | Depth | One light source, one depth model; shadows layered and tinted; no shadow on everything |
| 8 | Edges | Concentric corners; no double edges; images outlined; one corner personality |
| 9 | States | Hover, focus-visible, pressed, disabled, loading, empty and error are designed, not defaults |
| 10 | Motion | One entrance, press feedback, origins from triggers, under 300 ms, reduced-motion version |
| 11 | Identity | With the logo hidden, the page still says whose product this is, because its palette, type, shapes and movement come from the subject (`ai-tells.md` §4) |
| 12 | Stress | Longest real label, an empty list, 1,000 rows and a translated string all still look intended |

**Drift test** for more than one page: screenshot five key pages at 25% zoom side by side. A page that looks like another brand is a token problem or a page problem; fix that, not the style statement (`styles-catalog.md` §6).

## Pitfalls

| Symptom | Cause | Fix |
|---|---|---|
| Everything floats, so nothing does | A shadow on every card | Shadows for layers that really sit above; cards on a tonal step or a hairline |
| Shadow looks dirty on a coloured section | Black or neutral ink on a saturated surface | Ink = that surface's hue, darker and more saturated |
| Card corners look pinched | Same radius inside and outside | Inner = outer − padding |
| Double line around menus | CSS border plus the elevation token's edge ring | Remove the border |
| Premium look turns into noise | Gradient, glow, glass and grain together | One accent technique per view (budget in §1) |
| Headline feels loose and cheap | Display size with body tracking and line-height | `--tracking-display`, `--line-height-display` |
| Small text looks cramped or broken | Negative tracking below about 16 px, or on a script that has no use for it | Tracking 0 at small sizes and for non-Latin scripts |
| Button press makes the layout jump | Scaling an element that takes part in layout with `width`, or a large surface at 0.97 | Animate `scale`/`transform` only; scale large surfaces less |
| Popover appears to grow from nowhere | Default `transform-origin: center` | Origin at the trigger |
| Hover styles stick on phones | `:hover` outside a hover media query | `@media (hover: hover)` |
| Grain makes scrolling stutter | Full-page fixed, blended overlay | Limit to the hero or bake it into the image |
| Light image disappears into a light page | No edge | 1 px alpha outline with `outline-offset: -1px` |

## Sources

- Josh W. Comeau, Designing Beautiful Shadows in CSS — https://www.joshwcomeau.com/css/designing-shadows/
- Josh W. Comeau, Make Beautiful Gradients — https://www.joshwcomeau.com/css/make-beautiful-gradients/
- Jakub Krehel, Details that make interfaces feel better (shadow-as-border values, image outline, concentric radius, optical alignment, staged enter) — https://jakub.kr/writing/details-that-make-interfaces-feel-better
- Emil Kowalski, 7 Practical Animation Tips — https://emilkowal.ski/ui/7-practical-animation-tips ; Great Animations — https://emilkowal.ski/ui/great-animations
- Rauno Freiberg, Web Interface Guidelines — https://interfaces.rauno.me
- Vercel, Web Interface Guidelines (repository) — https://github.com/vercel-labs/web-interface-guidelines
- Erik D. Kennedy, 7 Rules for Creating Gorgeous UI, part 1 — https://www.learnui.design/blog/7-rules-for-creating-gorgeous-ui-part-1.html
- Inter dynamic metrics (tracking formula) — https://d.rsms.me/inter-website/v3/dynmetrics
- Matthew Butterick, Practical Typography: line spacing — https://practicaltypography.com/line-spacing.html
- Linear, How we redesigned the Linear UI — https://linear.app/now/how-we-redesigned-the-linear-ui
- Radix Colors, Understanding the scale — https://www.radix-ui.com/colors/docs/palette-composition/understanding-the-scale
- Chrome for Developers, text-box-trim — https://developer.chrome.com/blog/css-text-box-trim
- MDN, text-wrap-style — https://developer.mozilla.org/en-US/docs/Web/CSS/text-wrap-style ; hanging-punctuation — https://developer.mozilla.org/en-US/docs/Web/CSS/hanging-punctuation
- Cloud Four, Breaking out with CSS Grid layout — https://cloudfour.com/thinks/breaking-out-with-css-grid-layout/
- Every Layout — https://every-layout.dev/
- Browser versions — https://github.com/mdn/browser-compat-data · https://webstatus.dev/
