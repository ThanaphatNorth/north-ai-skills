# Typography & Layout

> Read when: choosing fonts or a font pairing, setting a type scale or fluid type, defining type tokens, setting Thai (or Thai + Latin) text, fixing font loading/CLS, choosing spacing or grid systems and breakpoints, writing CSS Grid / container-query layouts, or fixing weak visual hierarchy, density, alignment or image cropping.

**Contents:** Defaults · Type scales · Fluid type · Hierarchy tokens · Line-height, measure, tracking · Font pairing · Pairings catalog · Thai typography (incl. Thai + Latin luxury serifs, font budget) · Font loading · Spacing system · Grids & breakpoints · Layout recipes · Visual hierarchy & composition · Responsive images · Pitfalls · Sources

## Defaults

- **Body**: 16–18px on web (≥16px for form inputs, because iOS Safari zooms into focused inputs below 16px). Line-height 1.5–1.7 for Latin and **1.6–1.8 for Thai**. Measure **45–75ch**: Baymard recommends 50–75 characters, Butterick 45–90, and WCAG 1.4.8 (AAA) caps lines at 80 characters (40 for CJK).
- **Families**: one workhorse family for UI and body, plus at most one display family and one mono. 3–4 weights in total. Check the **script coverage first** (Thai!) before falling in love with a face. Thai + Latin pages count families per script (see "Font budget for Thai + Latin").
- **Sizes in `rem`**. Fluid sizes use `clamp(min-rem, rem + vw, max-rem)` with **max ≤ 2.5 × min** so text still reaches 200% under browser zoom (WCAG 1.4.4; the rule is Barvian's, published in Smashing).
- **Hierarchy**: ≤3 distinct sizes per view on simple pages (NN/g), and ≥1.2× between adjacent levels so they read as different.
- **Space** on a 4px base with 8px rhythm; layout via CSS Grid + container queries; breakpoints where the content breaks.
- **Never fix heights on text containers.** WCAG 1.4.12 requires layouts to survive line-height 1.5, paragraph spacing 2×, letter-spacing 0.12em and word-spacing 0.16em without clipping, and Thai stacked marks need the room anyway.

## Type scales

Modular scale = base × ratio^step. Values at a 16px base:

| Ratio | Name | Steps −1 … 5 (px) | Use |
|---|---|---|---|
| 1.125 | Major second | 14.2 · **16** · 18 · 20.2 · 22.8 · 25.6 · 28.8 | Dense UI: dashboards, admin, data tables, mobile apps |
| 1.2 | Minor third | 13.3 · **16** · 19.2 · 23 · 27.6 · 33.2 · 39.8 | Product UI default |
| 1.25 | Major third | 12.8 · **16** · 20 · 25 · 31.2 · 39.1 · 48.8 | General web, docs, SaaS marketing |
| 1.333 | Perfect fourth | 12 · **16** · 21.3 · 28.4 · 37.9 · 50.5 · 67.3 | Marketing, blogs |
| 1.5 | Perfect fifth | 10.7 · **16** · 24 · 36 · 54 · 81 · 121.5 | Display-led landing pages, editorial |
| 1.618 | Golden | 9.9 · **16** · 25.9 · 41.9 · 67.8 · 109.7 · 177.4 | Posters and hero-only display; too steep for UI |

Use a small ratio on small screens and a larger one on large screens; that's what fluid type does. Round to whole or half pixels, and snap line-heights to the 4px grid.

## Fluid type

Utopia method: (1) define a type scale for a small viewport, (2) define one for a large viewport, (3) let the browser interpolate by viewport width. Math for one step:

```
slope     = (maxSize − minSize) / (maxViewport − minViewport)
intercept = minSize − slope × minViewport
font-size: clamp(minSize, intercept + slope × 100vw, maxSize)   /* express sizes in rem */
```

Ready-made token set (computed: 360→1280px, base 16→18px, ratio 1.2→1.25):

```css
:root {
  --step--2: clamp(0.6944rem, 0.6844rem + 0.0444vw, 0.7200rem); /* 11.1→11.5px  captions, legal */
  --step--1: clamp(0.8333rem, 0.8072rem + 0.1159vw, 0.9000rem); /* 13.3→14.4px  labels, meta */
  --step-0:  clamp(1.0000rem, 0.9511rem + 0.2174vw, 1.1250rem); /* 16→18px      body */
  --step-1:  clamp(1.2000rem, 1.1193rem + 0.3587vw, 1.4062rem); /* 19.2→22.5px  title */
  --step-2:  clamp(1.4400rem, 1.3156rem + 0.5527vw, 1.7578rem); /* 23→28.1px    h3 */
  --step-3:  clamp(1.7280rem, 1.5444rem + 0.8161vw, 2.1973rem); /* 27.6→35.2px  h2 */
  --step-4:  clamp(2.0736rem, 1.8103rem + 1.1704vw, 2.7466rem); /* 33.2→43.9px  h1 */
  --step-5:  clamp(2.4883rem, 2.1186rem + 1.6433vw, 3.4332rem); /* 39.8→54.9px  display */
}
```

- Body barely moves (16→18); display grows most. That's correct.
- Generate other ranges with utopia.fyi/type/calculator; its `utopia-core` package flags steps that fail 1.4.4.
- **Fluid space** (Utopia): derive space from step 0 (= S) with multipliers 0.25 / 0.5 / 0.75 / 1 / 1.5 / 2 / 3 / 4 / 6 (3XS…4XL), plus pairs such as `--space-s-l` that interpolate between two sizes (≈18→44px). Use pairs for section padding and grid gaps.
- Component-relative sizing: inside a `container-type: inline-size` element, `font-size: clamp(1.25rem, 1rem + 2cqi, 2rem)` scales with the card instead of the viewport.
- Never use bare `vw` for font size: it ignores zoom.

## Hierarchy tokens

Five roles × three sizes, the Material 3 model. M3 values (size/line-height px, weight, tracking) come from the material-web tokens:

| Role | Large | Medium | Small | Weight | Tracking |
|---|---|---|---|---|---|
| Display (hero numbers, landing) | 57/64 | 45/52 | 36/44 | 400 | L −0.25px, M/S 0 |
| Headline (page/section titles) | 32/40 | 28/36 | 24/32 | 400 | 0 |
| Title (cards, dialogs, app bar) | 22/28 | 16/24 | 14/20 | 400 / 500 / 500 | 0 / +0.15px / +0.1px |
| Body (reading, descriptions) | 16/24 | 14/20 | 12/16 | 400 | +0.5 / +0.25 / +0.4px |
| Label (buttons, chips, tabs, meta) | 14/20 | 12/16 | 11/16 | 500 | +0.1 / +0.5 / +0.5px |

Web token set built on it (map these to the fluid steps above):

```css
:root {
  --font-sans: "Geist", system-ui, sans-serif;  --font-display: var(--font-sans);
  --font-mono: "Geist Mono", ui-monospace, monospace;
  --text-display: 600 var(--step-5)/1.05 var(--font-display);
  --text-h1: 600 var(--step-4)/1.1 var(--font-display);
  --text-h2: 600 var(--step-3)/1.2 var(--font-sans);
  --text-h3: 600 var(--step-2)/1.25 var(--font-sans);
  --text-title: 500 var(--step-1)/1.3 var(--font-sans);
  --text-body: 400 var(--step-0)/1.6 var(--font-sans);
  --text-label: 500 var(--step--1)/1.35 var(--font-sans);
  --text-caption: 400 var(--step--2)/1.4 var(--font-sans);
}
h1 { font: var(--text-h1); letter-spacing: -0.02em; text-wrap: balance; }
p  { font: var(--text-body); max-width: 68ch; text-wrap: pretty; }
:lang(th) { --text-body: 400 var(--step-0)/1.75 var(--font-sans); } /* Thai needs taller lines */
```

Body text in an app is usually 14–16px; marketing and reading pages use 16–20px. Keep labels and captions ≥12px. M3's smallest token (label-small, 11px) is for non-essential metadata only, and Thai text should not go below 14px.

## Line-height, measure, tracking

| Text | Line-height (Latin) | Line-height (Thai) | Measure | Tracking |
|---|---|---|---|---|
| Body / long-form | 1.5–1.7 | 1.6–1.8 | 45–75ch (target ~65) | 0 |
| UI text, labels (single line) | 1.2–1.4 | ≥1.5 | n/a | 0 to +0.01em; ALL CAPS +0.05–0.12em |
| Headings 24–40px | 1.15–1.3 | 1.3–1.45 | ≤ 20–35ch, `text-wrap: balance` | −0.01 to −0.02em (Latin only) |
| Display ≥48px | 1.0–1.1 | 1.2–1.35 | short | −0.02 to −0.04em (Latin only) |
| Small text ≤12px | 1.4–1.5 | ≥1.6 | n/a | +0.01–0.03em |

- Positive tracking for small sizes and negative for large display matches Material's tokens (body +0.5px, display-large −0.25px). Variable fonts with an `opsz` axis (Inter, Fraunces, Newsreader, Bricolage Grotesque, Source Serif 4, Literata, Bodoni Moda) do part of this automatically with `font-optical-sizing: auto`.
- Use `font-variant-numeric: tabular-nums` for tables, prices, timers and changing numbers; `lining-nums` in UI and `oldstyle-nums` in prose serif text if the font has them.
- `text-wrap: balance` for headings, captions and short blocks (Chromium balances ≤6 lines, Firefox ≤10; support Chrome 114, Firefox 121, Safari 17.5). `text-wrap: pretty` for body to avoid orphans (Chrome 117, Safari 26; no Firefox, so it degrades gracefully).
- Space with `lh`/`rlh` units (`margin-block: 1lh`) to keep vertical rhythm (lh: Chrome 109, Firefox 120, Safari 16.4).
- `text-box: trim-both cap alphabetic` trims the font's built-in leading for optically centred buttons/badges (Chrome 133, Safari 18.2, Firefox 154). Keep a padding fallback.
- Paragraph spacing ≈ 0.75–1× the line-height; space above a heading ≈ 2× the space below it, so the heading binds to its content.

## Font pairing

Principles:
1. **Start from the workhorse.** It must be legible at 14–16px, have 4+ weights (ideally variable), and cover every script you ship. Many brands need only this one family.
2. **Add a second family only for contrast on one axis**: serif vs sans, geometric vs humanist, wide vs condensed, or soft vs sharp. Keep **x-height, proportions and mood** compatible. Two similar sans faces look like a mistake.
3. **Superfamilies are the safe shortcut**: IBM Plex (Sans/Serif/Mono/Thai), Noto (Sans/Serif/Thai), Source (Serif 4/Sans 3), Red Hat (Display/Text), Instrument (Sans/Serif), Geist (Sans/Mono), Roboto Flex/Serif, Funnel (Display/Sans), Mona/Hubot Sans.
4. **Roles**: display face for headings and hero only; workhorse for body, UI and labels; mono for code and data.
5. **Overused defaults**: Google Fonts' popularity ranks (metadata, Oct 2026) put Roboto at 2, Open Sans 3, Inter 5, Montserrat 7, Poppins 8, Lato 9 and Playfair Display 24. They're fine for neutral product UI, but they read as "template" for a brand. Use a fresher face from the table, or keep Inter for UI and give the brand a distinctive display face.

## Pairings catalog

All families verified on Google Fonts (2026-10). "var" = variable axes.

| Mood / product | Headings | Body / UI | Extra | Notes |
|---|---|---|---|---|
| Neutral product UI (fresh) | Geist | Geist | Geist Mono | var wght 100–900; Inter alternative without the ubiquity |
| Neutral product UI (classic) | Inter Tight | Inter | JetBrains Mono | Inter var opsz 14–32 |
| Technical / enterprise | IBM Plex Sans | IBM Plex Sans | IBM Plex Mono | Plex Sans var wdth/wght; has Thai siblings |
| Corporate, approachable | Red Hat Display | Red Hat Text | — | Display/Text optical pair |
| Friendly consumer app | Plus Jakarta Sans | Figtree | — | Both warm geometric; Jakarta for headings only |
| Fintech, trust | Schibsted Grotesk | Public Sans | — | Sturdy grotesk + neutral, highly legible body |
| Bold startup / marketing | Bricolage Grotesque | DM Sans | — | Bricolage var opsz/wdth/wght: characterful at display sizes |
| Developer / brutalist | Space Grotesk | Inter | JetBrains Mono | Space Grotesk quirky at size; keep body neutral |
| AI / futuristic | Unbounded | Manrope | Geist Mono | Wide display + calm body |
| Avant-garde / creative tech | Syne | Hanken Grotesk | — | Syne at ≥32px only |
| Editorial, literary | Fraunces | Source Serif 4 | — | Fraunces SOFT/WONK/opsz axes; serif body with opsz |
| News / long-form | Newsreader | Newsreader | Public Sans (UI chrome) | Newsreader var opsz 6–72 covers headline to caption |
| Studio / portfolio | Instrument Serif | Instrument Sans | — | Serif (italic) for big display only (static, one weight) |
| Luxury / fashion | Bodoni Moda | Jost | — | High-contrast didone needs ≥28px; opsz 6–96 |
| Elegant hospitality | Cormorant Garamond | Albert Sans | — | Cormorant is fragile below 20px |
| Warm craft / food | Young Serif | Figtree | — | Chunky serif headings, friendly body |
| Soft wellness | Gloock | Instrument Sans | — | Gloock display only |
| Academic, institutional | Source Serif 4 | Source Sans 3 | — | Same-designer superfamily |
| Reading app / ebooks | Literata | Literata | Lexend (UI) | Literata var opsz 7–72 |
| Civic, accessibility-first | Atkinson Hyperlegible Next | Atkinson Hyperlegible Next | — | Designed for low vision; var wght 200–800 |
| Playful / kids | Fredoka | Nunito | — | Rounded; avoid long paragraphs in Fredoka |
| Sports / energetic | Big Shoulders | Archivo | — | Condensed display; Archivo var wdth 62–125 |
| Impact headlines | Anton | Archivo | — | All-caps display, tracking +0.02em |
| GitHub-style product | Mona Sans | Mona Sans | Hubot Sans | var wdth 75–125: width for hierarchy |
| Expressive variable system | Roboto Flex | Roboto Serif | — | 13 axes; tune width/grade per role |
| Modern design-led startup | Funnel Display | Funnel Sans | — | 2024 superfamily |

Thai + Latin pairings, including luxury/editorial serifs: see next section.

## Thai typography

**Thai fonts (Google Fonts unless noted)**

| Family | Style | Weights / axes | Best for | Notes |
|---|---|---|---|---|
| Noto Sans Thai Looped | Looped | var wdth 62.5–100, wght 100–900 | Body, forms, long UI text | "Suitable for all texts"; pairs with Noto Sans |
| Noto Sans Thai | **Loopless** | var wdth/wght | Headlines, packaging, ads | Google: "mainly suitable for headlines, packaging and advertising" |
| Noto Serif Thai | Modulated (serif) | var wdth/wght | Editorial, long reading | Pair with a Latin serif |
| IBM Plex Sans Thai Looped | Looped (formal) | 100–700 static | Body in Plex-based systems | Same family as IBM Plex Sans/Serif/Mono |
| IBM Plex Sans Thai | Loopless (informal) | 100–700 static | UI headings, labels | |
| Anuphan | Loopless | **var wght 100–700**, own Latin | Modern UI, startup, dashboards | Cadson Demak; Thai drawn from IBM Plex Sans Latin |
| Sarabun | Looped | 100–800 + italics | Government, formal documents, long text | = TH Sarabun New (national font); used in the Government Gazette |
| Kanit | Loopless (formal) | 100–900 + italics | Headlines, modern brands | Flat terminals; tight spacing |
| Prompt | Loopless | 100–900 + italics | Marketing, posters, headlines | Wide; similar glyphs (ก ถ ภ, บ ป, ข ช) confusable in very short texts |
| Mitr | Loopless, rounded | 200–700 | Casual, friendly, cards | |
| Bai Jamjuree | Square sans | 200–700 + italics | Headings, short passages, tech | Eurostyle-inspired |
| Chakra Petch | **Looped**, square | 300–700 + italics | Gaming, tech, automotive | Tapered corners |
| Google Sans | Includes Thai | var wght 400–700 | Android/Google-style UI | Added to Google Fonts Dec 2025 |
| Playpen Sans Thai | Handwriting-style | var wght 100–800 | Kids, education | 2025 |
| LINE Seed Sans TH (seed.line.me, **not** on Google Fonts) | Rounded, simplified | Thin–Heavy | Friendly consumer brands | OFL 1.1, self-host; check loop style before body use |

More Cadson Demak Thai+Latin families on Google Fonts: Athiti, K2D, Krub, Niramit, Mali, Taviraj, Trirong, Pridi, Maitree, Chonburi, Charm, Itim, Sriracha, Thasadith, Pattaya.

**Looped vs loopless: when to use which.** The 2024 Typotheque study (180 native readers, run at Chulalongkorn University) found:
- Looped text gave a small but significant **speed advantage for paragraph reading**, at all ages.
- Looped was rated more readable and "formal/classical"; loopless read as "modern".
- Younger readers preferred loopless only for short text.
- At a distance, older readers struggled with loopless and younger readers with looped.

Rules:
- **Body, forms, long UI copy, older or general audiences, government/health/finance → looped.**
- **Headlines, short labels, branding, youth-oriented marketing → loopless is fine.**
- A common, defensible system: loopless headings + looped body, e.g. Noto Sans Thai + Noto Sans Thai Looped, or IBM Plex Sans Thai + IBM Plex Sans Thai Looped.

**Thai + Latin pairings**

| Use | Latin | Thai | Why |
|---|---|---|---|
| Product UI (one system) | IBM Plex Sans (+ Mono) | IBM Plex Sans Thai Looped (body) / IBM Plex Sans Thai (headings) | Designed together |
| Modern startup UI | Anuphan's own Latin, or Inter | Anuphan | Variable; Plex-like proportions |
| Google-ecosystem / max coverage | Noto Sans | Noto Sans Thai Looped / Noto Sans Thai | Coordinated with Noto Latin designs |
| Government, documents | Sarabun (Latin incl.) | Sarabun | Official look; looped |
| Marketing site | Kanit or Prompt (headings) | + Sarabun or Noto Sans Thai Looped (body) | Loopless voice, looped reading |
| Editorial | Newsreader / Source Serif 4 | Noto Serif Thai | Modulated pair |
| Tech / gaming | Chakra Petch (Latin incl.) | Chakra Petch | Square, looped |

**Matching Latin + Thai.** Thai consonant height should visually match the Latin **x-height**, and stroke weight and terminals (round vs flat) should agree. Wide Thai faces (Prompt, Kanit) want wide geometric Latin. Fix size mismatch with `size-adjust` on the Thai `@font-face` (Chrome 92, Firefox 92, Safari 17) or with `font-size-adjust` (Chrome 127, Firefox 3, Safari 16.4); tune by eye on a mixed sentence.

```css
/* One family name, two files split by unicode-range (Google's Thai subset range) */
@font-face { font-family: "App Sans"; src: url(/fonts/inter-var.woff2) format("woff2");
  font-weight: 100 900; font-display: swap;
  unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD; }
@font-face { font-family: "App Sans"; src: url(/fonts/anuphan-var.woff2) format("woff2");
  font-weight: 100 700; font-display: swap; size-adjust: 104%;   /* tune by eye */
  unicode-range: U+02D7, U+0303, U+0331, U+0E01-0E5B, U+200C-200D, U+25CC; }
html { font-family: "App Sans", "Noto Sans Thai Looped", system-ui, sans-serif; }
:lang(th) { line-height: 1.75; }
```

With next/font use `Anuphan({ subsets: ['thai', 'latin'], display: 'swap' })` so both subsets preload.

**Thai + Latin luxury / editorial serif pairings** (fashion, fragrance, beauty, hospitality, magazines). Every family returned HTTP 200 from `https://fonts.googleapis.com/css2?family=<Family+Name>` on 2026-10-10; the Thai faces listed a Thai `unicode-range` (`U+0E01-0E5B`), the Latin faces did not. Weights and axes from Google Fonts metadata; style notes from Google's family descriptions.

| Mood | Latin display | Thai display | Body / UI (both scripts) | Why it works | Watch |
|---|---|---|---|---|---|
| Fashion, fragrance (didone) | Bodoni Moda (var opsz 6–96, wght 400–900) | Trirong (100–900 + italics; looped, thick–thin, narrow and tall) | Noto Sans Thai Looped or Sarabun | High stroke contrast in both; Trirong's tall, narrow build echoes the didone's verticals | Google warns ก ถ ภ ฤ ฦ and ฎ ฏ look alike in very short texts; Bodoni Moda ≥ 28 px |
| Classic luxury, hotels | Playfair Display (var wght 400–900) | Taviraj (100–900 + italics; wide, looped, thick–thin, formal) | IBM Plex Sans Thai Looped or Sarabun | Formal transitional contrast, airy loops | Taviraj is wide: set Thai a little smaller (start at 0.9em) or give it a wider measure |
| Delicate beauty, spa | Cormorant Garamond (var wght 300–700) | Taviraj or Trirong at 300–400 | Noto Sans Thai Looped | Light, high-contrast, quiet | Cormorant is fragile below 20 px; light Thai weights lose loop detail, so Thai display ≥ 24 px |
| Editorial magazine, long reads | Fraunces (var opsz 9–144, wght 100–900, SOFT, WONK) | Noto Serif Thai (var wdth 62.5–100, wght 100–900; modulated) | Noto Serif Thai (reading) + Noto Sans Thai Looped (UI) | Two variable families: match Thai width and weight to Fraunces' optical size | Google lists Noto Serif Thai at 140 glyphs, a Thai-focused design: keep the Latin face first in the stack |
| Bold editorial display, campaigns | DM Serif Display (400 + italic) | Chonburi (400 only; formal looped + serif, display) | Sarabun | Both are single-weight, heavy display serifs | One weight each: build hierarchy with size, set `font-synthesis: none` |
| Warm, approachable (wellness, food) | Pridi's own Latin, or Fraunces with SOFT 100 | Pridi (200–700; slab-serif Latin + looped Thai, body and display) | Pridi | One family covers both scripts and both roles | Slab Latin: pair only with soft, sturdy display faces |
| Script accent (one word, signature line) | — | Charmonman (400/700; Thai + Latin, Zapfino-inspired; a Handwriting face, not a serif) | — | Adds a signed, ceremonial note to a luxury layout | Never for body, UI or buttons; tall ascenders need line-height ≥ 1.6 |

Bai Jamjuree (square sans, 200–700 + italics, Thai + Latin) is the label/UI companion when a didone headline needs a technical counterpoint (watches, automotive). It is not a serif.

**Matching a Latin didone and a Thai serif in one headline.**
1. **x-height to consonant height:** Thai consonants should sit at the Latin x-height. Didones have small x-heights, so the Thai usually needs to come *down* in size, not up.
2. **Stroke contrast:** high-contrast Latin (Bodoni Moda, Playfair Display, DM Serif Display) → thick–thin looped Thai (Trirong, Taviraj, Chonburi); slab Latin → Pridi; modulated text serif → Noto Serif Thai. A loopless sans Thai next to a didone looks like a font that failed to load.
3. **Weight:** start the Thai one step lighter than the Latin (Bodoni Moda 500 + Trirong 400) and compare stem thickness at the final size; stacked marks add ink to Thai lines.
4. **Size: `size-adjust` only works on an `@font-face` you write yourself** (self-hosted files, recipe above). The Google Fonts CSS API writes the `@font-face` rules for you, so use a stack with the **Latin face first and the Thai face second**: font selection runs one character at a time (MDN), so Latin glyphs come from the Latin face and Thai glyphs fall through to the Thai face. Because Google splits each family into `unicode-range` subsets, the Thai face's Latin file is never downloaded (headless Chrome, 2026-10-10: only Bodoni Moda Latin and Trirong Thai loaded for the headline below). Then tune the Thai with a Thai-scoped wrapper class.

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bodoni+Moda:ital,opsz,wght@0,6..96,400..700;1,6..96,400..700&family=Trirong:wght@300;400;600&family=Noto+Sans+Thai+Looped:wght@400;600&display=swap">
<h1 class="display">Rituals of Light <span lang="th" class="th">พิธีกรรมแห่งแสง</span></h1>
```

```css
.display { font: 500 var(--step-5)/1.3 "Bodoni Moda", "Trirong", serif; letter-spacing: -0.02em; }
.display .th { font-weight: 400; font-size: 0.9em; letter-spacing: 0; } /* Thai-only tuning; negative tracking collides marks */
body { font-family: "Noto Sans Thai Looped", sans-serif; }               /* one body family for both scripts */
```

The 0.9em and the weight step were tuned by eye in that render; re-tune on your real words at the final size, and give a headline that contains Thai the Thai display line-height (1.2–1.35) on the heading itself.

**Font budget for Thai + Latin.**
- **Count families per script.** `platform-web.md`'s "≤2 families" means ≤ 2 per script (one display + one text). A Thai + Latin page may load **3 families in total when one of them is a Thai body face that also covers Latin**, e.g. Bodoni Moda (Latin display) + Trirong (Thai display) + Noto Sans Thai Looped (Thai and Latin body/UI): Latin uses 2, Thai uses 2. A fourth family (a script accent counts) means dropping one.
- **Prefer a Thai family that ships Latin** for body and UI. Anuphan, IBM Plex Sans Thai (Looped), Noto Sans Thai (Looped), Sarabun, Pridi and Trirong all include Latin subsets on Google Fonts, so one family can carry body text in both scripts.
- **Keep critical font files ≤ 4.** Count the WOFF2 files the first viewport fetches: each family × weight (one file per variable range) × script subset is a file. The stack above fetched four (Bodoni Moda Latin, Trirong Thai 400, Noto Sans Thai Looped Thai and Latin). Preload ≤ 2 of them (Font loading).

**Vertical space and clipping.** Thai stacks vowels and tone marks above the consonant and vowels below it, so a cluster can surround its base on three sides. Thai needs more interline space than Latin (r12a).
- Body line-height 1.6–1.8; body and UI text (labels, buttons, chips) never below 1.5. Headings follow the table above (24–40px: 1.3–1.45; display ≥48px: 1.2–1.35) because the absolute gap is already large; check that tone marks on a wrapped second line don't touch the line above.
- No fixed `height` on buttons, inputs, chips or table rows; use padding plus `min-height`.
- `overflow: hidden`, `-webkit-line-clamp` and `text-overflow: ellipsis` clip marks when line-height is tight. Give clamped Thai text line-height ≥1.6 plus 2–4px **`padding-top` only**. Not `padding-block`: bottom padding sits inside the clip box, so the upper vowels and tone marks of the next, clamped-away line show through as stray marks along the bottom edge (reproduced in headless Chrome, 2026-10-10).
- Test string: `ปั้น ที่ กุ้ง ญี่ปุ่น ฎีกา ฤๅษี ผู้ใหญ่ น้ำ`.

**Line breaking: Thai has no spaces between words.** Spaces separate phrases and sentences. Browsers find word breaks with dictionary heuristics and wrap on grapheme-cluster boundaries. Dictionaries miss proper names, brand terms, compounds and transliterations, which then break mid-word.
- Set `lang="th"` on `<html>` (or on Thai islands in mixed pages). Segmentation, font fallback and `:lang()` rules depend on it.
- `word-break: keep-all` does **not** help: it only affects CJK, and Thai behaves as `normal`. `word-break: break-all` breaks Thai anywhere (bad). Keep `overflow-wrap: anywhere` only as a safety net for URLs and long codes. `hyphens` doesn't apply to Thai.
- Chrome's dictionary also splits **common** compounds, not only names. Seen in Chrome (Oct 2026) at 320–390px: วิดีโอ|คอล, มือ|ถือ, โรง|พยาบาล, ตัว|เอง, ใบ|อนุญาต, วัน|เดียวกัน, ส่วน|บุคคล, รอ|คิว. Look at every heading, lead and button label at **320, 390 and 768px** and protect the ones that split.
- `<span style="white-space:nowrap">` is for **short compounds and names only** (a word or two: มือถือ, a brand name). A longer protected phrase can't wrap at all, and in testing it overflowed its column at 768px. For longer phrases add `<wbr>` hints at the real word boundaries instead (they add break opportunities, they don't remove the dictionary's), and wrap only the short compound that actually splits in a nowrap span. **Inside a flex container** (a `display:flex` `li` with an icon, a chip row) each bare text run and each span becomes its own flex item, so a nowrap span gets pulled out of the sentence and the words wrap out of order ("ท้อง อาหารเป็นพิษ / เสีย"). Wrap the whole label in one element (`<li><svg/><span>ท้องเสีย <span class=nowrap>อาหารเป็นพิษ</span></span></li>`) so only that wrapper is the flex item. Add break hints in headlines with `<wbr>` (it adds no character to copied text). U+200B ZWSP also adds a break and U+2060 WJ prevents one; misplaced ZWSPs pollute search and copy, so prefer `<wbr>` in HTML.
- `text-wrap: balance` balances using the browser's break opportunities. For Thai headings, combine it with `<wbr>` hints.
- Left-align Thai body text. Thai justification stretches the spaces between phrases (and characters in narrow columns), which browsers do poorly; avoid `text-align: justify`.
- Truncate and segment with `Intl.Segmenter` (Baseline April 2024), never `str.slice()`, which can split a consonant from its tone mark:

```tsx
import { Fragment } from "react"; // React 18/19
const graphemes = new Intl.Segmenter("th", { granularity: "grapheme" });
const words = new Intl.Segmenter("th", { granularity: "word" });
export const truncateTh = (s: string, n: number) => {
  const g = Array.from(graphemes.segment(s), x => x.segment);
  return g.length > n ? g.slice(0, n).join("") + "…" : s;
};
// Word-break hints for headings, SVG/canvas text or PDF layout
export const ThaiBreaks = ({ text }: { text: string }) => (
  <>{Array.from(words.segment(text), (w, i) => <Fragment key={i}>{i > 0 && <wbr />}{w.segment}</Fragment>)}</>
);
```

- **Tracking**: don't letter-space Thai body. Negative tracking collides stacked marks. If you track Thai display text, check ำ (U+0E33), which must split from its ring when spaced (r12a).
- Use Arabic numerals in UI; Thai digits (๐–๙) only where the document convention requires them.

## Font loading

- **Format and size**: WOFF2 only (about 30% smaller than WOFF). Use variable fonts when you need 3+ weights. Subset with `unicode-range` (Latin fonts carry 100–1,000 glyphs; a Thai subset is small, so it's cheap to preload).
- **Hosting**: self-host on a CDN with HTTP/2, or let the framework do it (next/font downloads Google Fonts at build time and the browser never calls Google). If you use the Google CDN: `preconnect` to `fonts.googleapis.com` and `fonts.gstatic.com` (`crossorigin`).
- **Preload** only the 1–2 files used above the fold (body regular, plus the hero display face) with `<link rel="preload" as="font" type="font/woff2" crossorigin>`. Preload ignores `unicode-range` and competes with the LCP image.
- **font-display**:

| Value | Block | Swap | Use |
|---|---|---|---|
| `swap` | 0ms | infinite | Brand/heading fonts that must show (risk: layout shift) |
| `optional` | ~100ms | none | Body text when CLS matters most; repeat visits get the font |
| `fallback` | ~100ms | ~3s | Compromise |
| `block` | 2–3s | infinite | Icon fonts only (prefer SVG icons) |

  Chromium and Firefox block up to 3s by default and Safari indefinitely, so always set `font-display`.
- **Kill CLS with metric-matched fallbacks**. `size-adjust` works everywhere (Chrome 92, Firefox 92, Safari 17). `ascent-override` / `descent-override` / `line-gap-override` work in Chrome 87 and Firefox 89 but **not in Safari stable**, so expect a small shift there. Tools: next/font `adjustFontFallback` (on by default for Google fonts), fontaine, Capsize.

```css
/* Placeholder values: paste the numbers Capsize / fontaine / next-font compute for YOUR font pair */
@font-face { font-family: "Brand Fallback"; src: local("Arial"), local("Arimo");
  size-adjust: 100%; ascent-override: 100%; descent-override: 0%; line-gap-override: 0%; }
body { font-family: "Brand", "Brand Fallback", system-ui, sans-serif; }
```

- Load only the weights you use; set `font-synthesis: none` to stop faux bold and italic when a style is missing.

## Spacing system

- 4px base unit, 8px rhythm: "use multiples of 8 to define dimensions, padding, and margin" (8pt grid), with a 4px half-step for tight UI and type baselines. In Figma, set the nudge to 8.
- Token scale: `4 · 8 · 12 · 16 · 24 · 32 · 48 · 64 · 96 · 128` (px), i.e. `--space-1 … --space-10` = `.25 .5 .75 1 1.5 2 3 4 6 8rem`.
- **Proximity**: space inside a group < space between groups, at roughly 1 : 1.5–2 (e.g. 8 inside a field group, 16 between fields, 32–48 between sections). Equal spacing everywhere destroys grouping.
- Component padding: buttons 8–12 × 16–24px; cards 16–24px (mobile) / 24–32px (desktop); page sections 48–96px vertical on desktop, 32–64px on mobile (or the fluid `--space-l-2xl` pair).
- Density modes for data-heavy UI: compact / comfortable / spacious, e.g. table rows 32 / 40 / 48px. Expose density as a setting rather than shrinking type.
- Touch targets: WCAG 2.2 SC 2.5.8 sets a 24×24 CSS px minimum; platforms ask for 44pt (Apple) and 48dp (Material). See `platform-mobile.md`.

## Grids & breakpoints

Window size classes (Android/Material): compact <600dp · medium 600–839 · expanded 840–1199 · large 1200–1599 · extra-large ≥1600. Starting grid per class (this file's recommendation; tune to the content):

| Class | Columns | Outer margin | Gutter | Typical layout |
|---|---|---|---|---|
| Compact (<600) | 4 | 16px | 16px | Single column, bottom nav |
| Medium (600–839) | 8 | 24px | 24px | 2-up cards, nav rail |
| Expanded (840–1199) | 12 | 32px | 24px | Sidebar + content, list-detail |
| Large (1200–1599) | 12 | 40–64px | 24–32px | Content max-width 1200–1280 |
| Extra-large (≥1600) | 12 inside max-width 1280–1440, centered | auto | 32px | Don't stretch text; add side panels |

- 12 columns divide into 2, 3, 4 and 6. Text columns stay inside the 45–75ch measure whatever the grid.
- **Content-first breakpoints**: add a breakpoint where the content breaks (line length passes ~75ch, cards drop below their min width, nav items wrap), not at device widths. Prefer intrinsic layouts (`auto-fit`/`minmax`, `flex-wrap`, `clamp`) and container queries so most components need no breakpoints at all.
- Viewport queries for page shells (nav rail ↔ bottom bar); **container queries for components**. Container queries have worked in all engines since Feb 2023 (Chrome 105, Firefox 110, Safari 16). Container units `cqi`/`cqb` fall back to small-viewport units when there is no container.

## Layout recipes

```css
/* 1. Responsive card grid, no media queries (min() avoids overflow on tiny screens) */
.cards { display: grid; gap: var(--space-5); grid-template-columns: repeat(auto-fit, minmax(min(100%, 18rem), 1fr)); }
/* auto-fit collapses empty tracks (items stretch); auto-fill keeps them (items keep max width) */

/* 2. Content grid with full-bleed escape hatch */
.page { display: grid; grid-template-columns:
  [full-start] minmax(1rem, 1fr) [content-start] min(68ch, 100% - 2rem) [content-end] minmax(1rem, 1fr) [full-end]; }
.page > * { grid-column: content; }
.page > .full-bleed { grid-column: full; }

/* 3. Sidebar layout that never blows out (minmax(0,1fr) lets long words/code shrink) */
.shell { display: grid; grid-template-columns: 16rem minmax(0, 1fr); }
@media (width < 840px) { .shell { grid-template-columns: minmax(0, 1fr); } }

/* 4. Aligned card internals with subgrid (Baseline Sept 2023) */
.plans { display: grid; grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr)); gap: 1.5rem; }
.plan  { display: grid; grid-row: span 4; grid-template-rows: subgrid; row-gap: .75rem; } /* title, price, features, CTA line up */

/* 5. Component that adapts to its container */
.card-wrap { container: card / inline-size; }
.card { display: grid; gap: 1rem; }
@container card (width > 32rem) { .card { grid-template-columns: 12rem 1fr; align-items: start; } }

/* 6. Bento grid */
.bento-wrap { container-type: inline-size; }
.bento { display: grid; gap: 1rem; grid-template-columns: repeat(4, 1fr); grid-auto-rows: minmax(11rem, auto); }
.bento .hero { grid-column: span 2; grid-row: span 2; }
.bento .wide { grid-column: span 2; }
.bento .tall { grid-row: span 2; }
@container (width < 44rem) { .bento { grid-template-columns: repeat(2, 1fr); } .bento .hero { grid-row: span 1; } }
@container (width < 26rem) { .bento { grid-template-columns: 1fr; } .bento > * { grid-column: auto; grid-row: auto; } }
```

Bento rules: one hero tile (2×2) per grid, 1–2 wide tiles, the rest 1×1. Use the same radius (12–24px), gap and padding everywhere. Each tile carries one idea (number, visual or short claim). Avoid `grid-auto-flow: dense` when tile order matters: it makes the visual order differ from the DOM/focus order (WCAG 1.3.2, 2.4.3).

## Visual hierarchy & composition

| Lever | How to use it | Guardrail |
|---|---|---|
| Size | Adjacent levels ≥1.2× apart; one dominant element per view | NN/g: ≤3 sizes on simple pages (web body ~14–16px, subheads 18–22, headers to ~32 in content UI); ≤2 large elements |
| Weight | 400 body / 500 UI labels / 600–700 headings | ≤3 weights; bold body text loses its signal |
| Color & contrast | Primary text darkest, secondary text muted (still ≥4.5:1); brand color only for interactive or key elements | NN/g: ≤3 contrast variations; reserve bright warm colors for warnings/errors (see `color.md`) |
| Spacing | More space isolates and elevates; tight space groups | Space above a heading ≈ 2× below |
| Position | Primary content and actions top-left (LTR) and near the related content; primary CTA where the eye ends a section | Reading patterns: see `psychology.md` / `ux-foundations.md` |
| Grouping | Proximity first, then shared background (card), then border | NN/g: use borders/backgrounds only when whitespace isn't enough |
| Alignment | One strong left edge per region; align to the grid; numbers right-aligned with tabular figures | Center only short, symmetric blocks (hero, empty states) |

- **Squint/blur test**: blur the screen 5–10px (NN/g). The intended primary element should still dominate. At 20px blur, check for unintended focal points such as photos or saturated badges.
- **Composition**: one focal point per viewport. Place hero subjects and focal text on rule-of-thirds lines rather than dead center for dynamic layouts; use asymmetric splits (5/7, 4/8 columns) for editorial and marketing, and symmetric layouts for calm or formal content. Lead the eye with the subject's gaze or direction toward the headline/CTA.
- **Whitespace and density**: marketing pages breathe (sections 64–128px); tools are dense but grouped (8–16px). Density is a product decision; set it once in tokens. See `styles-catalog.md` for style-specific density, and `product-patterns.md` for dashboards and tables.

## Responsive images

```html
<!-- Resolution switching: browser picks the smallest file ≥ slot width × DPR -->
<img src="card-800.avif" srcset="card-400.avif 400w, card-800.avif 800w, card-1600.avif 1600w"
     sizes="(width < 600px) 100vw, (width < 1200px) 50vw, 400px"
     width="800" height="500" alt="…" loading="lazy" decoding="async">

<!-- Art direction: different crop per layout; the <img> fallback is required -->
<picture>
  <source media="(width < 800px)" srcset="hero-portrait.avif" type="image/avif">
  <source media="(width >= 800px)" srcset="hero-wide.avif" type="image/avif">
  <img src="hero-wide.jpg" width="1600" height="900" alt="…" fetchpriority="high">
</picture>
```

- Always set `width`/`height` (or CSS `aspect-ratio`) to reserve space and avoid CLS. Use `object-fit: cover` plus `object-position: 30% 40%` to keep the focal point in cropped frames.
- LCP hero: `fetchpriority="high"` (Chrome 102, Firefox 132, Safari 17.2; in a Google Flights test LCP fell from 2.6s to 1.9s). **Never `loading="lazy"` on the LCP image**; lazy-load everything below the fold.
- Art-direct when the subject would be too small or cut off in a narrow frame. Use `srcset`/`sizes` when only resolution changes. Don't put media conditions in `sizes` when using `<source media>`.
- Text over images needs a scrim or a solid panel behind it to meet contrast. Test the lightest part of the image (`color.md`).

## Pitfalls

| Symptom | Cause | Fix |
|---|---|---|
| Thai tone marks or top vowels cut off in buttons, chips, clamped text | Tight line-height plus `overflow:hidden` / line-clamp / fixed height | line-height ≥1.6, `min-height` + padding, 2–4px `padding-top` on clamped blocks |
| Stray tone marks along the bottom edge of clamped Thai text | `padding-block` (bottom padding) reveals the top of the clamped-away next line | `padding-top` only on clamped blocks |
| Thai names or brand words split across lines | Dictionary doesn't know the word | `white-space:nowrap` span for short compounds/names; `<wbr>` at real boundaries for longer phrases; check 320, 390 and 768px |
| Heading overflows its column at tablet width (768px) | A long phrase wrapped in a `nowrap` span can't break | Replace the span with `<wbr>` hints at word boundaries |
| Words in a flex list item wrap out of order | A nowrap span (or bare text next to a span) inside `display:flex` becomes a separate flex item | Put the whole label in one wrapper element; style children with `.x > span`, not `.x span` |
| Thai breaks at random characters | `word-break: break-all` (often from a global reset) | Remove it; `overflow-wrap:anywhere` only for URLs/codes |
| "keep-all" added for Thai has no effect | `keep-all` only changes CJK; non-CJK behaves as normal | Use `nowrap` spans or `<wbr>` |
| Truncated Thai shows a floating tone mark or dotted circle | `slice()` split a grapheme cluster | `Intl.Segmenter` grapheme truncation |
| Thai renders in a different font than designed | Missing `lang="th"` or the Thai subset wasn't loaded | `lang`, include the `thai` subset, composite `@font-face` |
| Text can't reach 200% zoom | `vw`-only sizes or clamp max > 2.5× min | rem-based clamp, max ≤ 2.5 × min |
| Layout jumps when the web font loads (CLS) | Fallback metrics differ | Metric-matched fallback `@font-face` (size-adjust plus overrides); `font-display: optional` for body |
| Invisible text for seconds on slow networks (Safari) | No `font-display`; Safari blocks indefinitely | Set `font-display` on every `@font-face` |
| LCP regressed after adding fonts | Too many preloads competing with the hero image | Preload ≤2 critical fonts; subset |
| Fake bold or slanted text | Weight/style not loaded, browser synthesizes it | Load real styles; `font-synthesis: none` |
| One-word last line on headings | Default greedy wrapping | `text-wrap: balance` (headings), `pretty` (body) |
| Grid column overflows with long URLs/code | `1fr` = `minmax(auto, 1fr)` respects min-content | `minmax(0, 1fr)` and `min-width: 0` on flex/grid children |
| Card grid leaves a lonely stretched card | `auto-fit` stretches remaining items | `auto-fill`, or cap item `max-width` |
| Keyboard focus jumps around a bento grid | `grid-auto-flow: dense` reorders visually | Order the DOM as displayed; drop `dense` |
| Layout breaks under user text-spacing overrides | Fixed heights, `overflow:hidden` on text | Intrinsic sizing (WCAG 1.4.12) |

## Sources

- Utopia: designing with fluid type scales — https://utopia.fyi/blog/designing-with-fluid-type-scales/ ; clamp math — https://utopia.fyi/blog/clamp/ ; fluid space — https://utopia.fyi/blog/painting-with-a-fluid-space-palette/ ; calculator — https://utopia.fyi/type/calculator
- Addressing accessibility concerns with fluid type (Barvian, Smashing 2023) — https://smashingmagazine.com/2023/11/addressing-accessibility-concerns-fluid-type
- Material 3 type scale tokens (material-web) — https://github.com/material-components/material-web/blob/main/tokens/versions/v0_192/_md-sys-typescale.scss
- Baymard, line length — https://baymard.com/blog/line-length-readability ; Butterick, line length — https://practicaltypography.com/line-length.html
- WCAG 2.2 Understanding 1.4.12 Text Spacing — https://www.w3.org/WAI/WCAG22/Understanding/text-spacing.html
- MDN text-wrap — https://developer.mozilla.org/en-US/docs/Web/CSS/text-wrap ; word-break — https://developer.mozilla.org/en-US/docs/Web/CSS/word-break ; Intl.Segmenter — https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl/Segmenter
- MDN browser-compat-data (versions) — https://github.com/mdn/browser-compat-data
- Google Fonts metadata (families, axes, subsets, popularity) — https://fonts.google.com/metadata/fonts ; Google Fonts family descriptions (google/fonts repo) — https://github.com/google/fonts
- Thai serif descriptions (google/fonts) — Trirong https://raw.githubusercontent.com/google/fonts/main/ofl/trirong/DESCRIPTION.en_us.html ; Taviraj https://raw.githubusercontent.com/google/fonts/main/ofl/taviraj/DESCRIPTION.en_us.html ; Pridi https://raw.githubusercontent.com/google/fonts/main/ofl/pridi/DESCRIPTION.en_us.html ; Chonburi https://raw.githubusercontent.com/google/fonts/main/ofl/chonburi/DESCRIPTION.en_us.html ; Charmonman https://raw.githubusercontent.com/google/fonts/main/ofl/charmonman/DESCRIPTION.en_us.html ; Noto Serif Thai https://raw.githubusercontent.com/google/fonts/main/ofl/notoserifthai/DESCRIPTION.en_us.html
- Google Fonts CSS API v2 (each pairing family checked for HTTP 200 + Thai `unicode-range`, 2026-10-10), e.g. https://fonts.googleapis.com/css2?family=Trirong
- MDN font-family (font selection is per character) — https://developer.mozilla.org/en-US/docs/Web/CSS/font-family
- Typotheque, effects of loops in Thai — https://www.typotheque.com/research/effects-of-loops-in-thai
- r12a Thai orthography notes — https://r12a.github.io/scripts/thai/th ; W3C Thai layout resources — https://w3c.github.io/sealreq/thai/
- LINE Seed TH — https://seed.line.me/index_th.html
- web.dev font best practices — https://web.dev/articles/font-best-practices ; CSS size-adjust — https://web.dev/articles/css-size-adjust ; fetchpriority — https://web.dev/articles/fetch-priority ; container queries stable — https://web.dev/blog/cq-stable
- Next.js font module — https://nextjs.org/docs/app/api-reference/components/font ; Capsize — https://seek-oss.github.io/capsize/ ; fontaine — https://github.com/unjs/fontaine
- 8-point grid (spec.fm) — https://spec.fm/specifics/8-pt-grid
- Android window size classes — https://developer.android.com/develop/ui/compose/layouts/adaptive/use-window-size-classes
- MDN container queries — https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_containment/Container_queries ; subgrid — https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_grid_layout/Subgrid ; responsive images — https://developer.mozilla.org/en-US/docs/Web/HTML/Guides/Responsive_images
- NN/g visual hierarchy — https://www.nngroup.com/articles/visual-hierarchy-ux-definition/
