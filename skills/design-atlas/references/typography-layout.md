# Typography & Layout

> Read when: choosing fonts or a font pairing, setting a type scale or fluid type, defining type tokens, setting text in more than one script or language (CJK, Arabic, Indic and Southeast Asian scripts, RTL, translated UI), fixing font loading/CLS, choosing spacing or grid systems and breakpoints, writing CSS Grid / container-query layouts, or fixing weak visual hierarchy, density, alignment or image cropping.

**Contents:** Defaults · Type scales · Fluid type · Hierarchy tokens · Line-height, measure, tracking · Font pairing · Pairings catalog · Multi-script typography (script groups, pairing across scripts, vertical space, line breaking, text expansion) · Font loading · Spacing system · Grids & breakpoints · Layout recipes · Visual hierarchy & composition · Responsive images · Pitfalls · Sources

## Defaults

- **Body**: 16–18px on web (≥16px for form inputs, because iOS Safari zooms into focused inputs below 16px). Line-height 1.5–1.7 for Latin, Greek and Cyrillic and **1.6–1.8 for scripts with stacked marks or dense glyphs** (Multi-script typography). Measure **45–75ch**: Baymard recommends 50–75 characters, Butterick 45–90, and WCAG 1.4.8 (AAA) caps lines at 80 characters (40 for CJK).
- **Families**: one workhorse family for UI and body, plus at most one display family and one mono. 3–4 weights in total. Check the **script coverage first**, before falling in love with a face. Pages in two scripts count families per script (see "Font budget across scripts").
- **Sizes in `rem`**. Fluid sizes use `clamp(min-rem, rem + vw, max-rem)` with **max ≤ 2.5 × min** so text still reaches 200% under browser zoom (WCAG 1.4.4; the rule is Barvian's, published in Smashing).
- **Hierarchy**: ≤3 distinct sizes per view on simple pages (NN/g), and ≥1.2× between adjacent levels so they read as different.
- **Space** on a 4px base with 8px rhythm; layout via CSS Grid + container queries; breakpoints where the content breaks.
- **Never fix heights on text containers.** WCAG 1.4.12 requires layouts to survive line-height 1.5, paragraph spacing 2×, letter-spacing 0.12em and word-spacing 0.16em without clipping, and scripts with stacked marks need the room anyway.

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
:lang(hi), :lang(ar), :lang(ja) { --text-body: 400 var(--step-0)/1.75 var(--font-sans); } /* tall and dense scripts: list the languages you ship */
```

Body text in an app is usually 14–16px; marketing and reading pages use 16–20px. Keep labels and captions ≥12px. M3's smallest token (label-small, 11px) is for non-essential metadata only; scripts with stacked marks or dense strokes should not go below 14px.

## Line-height, measure, tracking

| Text | Line-height (Latin, Greek, Cyrillic) | Line-height (tall or dense scripts) | Measure | Tracking |
|---|---|---|---|---|
| Body / long-form | 1.5–1.7 | 1.6–1.8 | 45–75ch (target ~65) | 0 |
| UI text, labels (single line) | 1.2–1.4 | ≥1.5 | n/a | 0 to +0.01em; ALL CAPS +0.05–0.12em |
| Headings 24–40px | 1.15–1.3 | 1.3–1.45 | ≤ 20–35ch, `text-wrap: balance` | −0.01 to −0.02em (Latin, Greek, Cyrillic only) |
| Display ≥48px | 1.0–1.1 | 1.2–1.35 | short | −0.02 to −0.04em (Latin, Greek, Cyrillic only) |
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
3. **Superfamilies are the safe shortcut**: IBM Plex (Sans/Serif/Mono, with Arabic, Devanagari, Hebrew, Thai, JP, KR and Chinese siblings), Noto (Sans/Serif for nearly every script), Source (Serif 4/Sans 3), Red Hat (Display/Text), Instrument (Sans/Serif), Geist (Sans/Mono), Roboto Flex/Serif, Funnel (Display/Sans), Mona/Hubot Sans.
4. **Roles**: display face for headings and hero only; workhorse for body, UI and labels; mono for code and data.
5. **Overused defaults**: Google Fonts' popularity ranks (metadata, Oct 2026) put Roboto at 2, Open Sans 3, Inter 5, Montserrat 7, Poppins 8, Lato 9 and Playfair Display 24. They're fine for neutral product UI, but they read as "template" for a brand. Use a fresher face from the table, or keep Inter for UI and give the brand a distinctive display face.

## Pairings catalog

All families verified on Google Fonts (2026-10). "var" = variable axes.

| Mood / product | Headings | Body / UI | Extra | Notes |
|---|---|---|---|---|
| Neutral product UI (fresh) | Geist | Geist | Geist Mono | var wght 100–900; Inter alternative without the ubiquity |
| Neutral product UI (classic) | Inter Tight | Inter | JetBrains Mono | Inter var opsz 14–32 |
| Technical / enterprise | IBM Plex Sans | IBM Plex Sans | IBM Plex Mono | Plex Sans var wdth/wght; siblings for many scripts |
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

Pairing a Latin face with another script: see next section.

## Multi-script typography

A type system tuned on English breaks quietly in other scripts: marks get clipped, words split in the wrong place, all-caps labels lose their meaning, translated labels overflow. Decide the languages in the brief (`templates/design-brief.md`), then apply the group's rules.

**Script groups and what changes**

| Group | Examples | Line-height | Case, italics, tracking | Line breaking |
|---|---|---|---|---|
| English-like | Latin (except Vietnamese), Greek, Cyrillic | Body 1.5–1.7 | Case and italics exist; negative tracking on display | At spaces; `hyphens: auto` with `lang` |
| Tall: stacked or deep marks | Arabic, Persian, Urdu, Devanagari and other Indic scripts, Thai, Lao, Khmer, Burmese, Tibetan, Vietnamese | Body 1.6–1.8; UI ≥ 1.5 | Mostly no case; no negative tracking; no letter-spacing at all on joined scripts (Arabic, Devanagari) | Arabic and Indic scripts at spaces; Thai, Lao, Khmer, Burmese have **no word spaces** and break by dictionary |
| Dense | Chinese, Japanese, Korean | Body 1.7–1.8; display 1.2–1.35 | No case; no true italics (use weight, colour or `text-emphasis`) | Between almost any two characters (Chinese, Japanese); Korean at spaces with `word-break: keep-all` |
| Right-to-left | Arabic, Hebrew, Persian, Urdu | Per the group above | — | `dir` in the markup; logical properties (`platform-web.md`, i18n) |

Material's language support uses the same three categories (English-like, tall, dense) and says tall and dense scripts need extra line height; W3C measured Thai at about 150% of the vertical space of Latin, and lists Arabic (especially Nastaliq), Devanagari, Tibetan and CJK among the scripts that need more height. The line-heights above are this file's working values: confirm them on real copy with a native reader.

**Choosing and pairing fonts across scripts**
- **Coverage before character.** List every script the product ships, then shortlist families that cover them or have a sibling for each (Noto, IBM Plex, Source Han / Noto CJK). A face with no sibling needs a partner per script.
- **Match the partner on three things:** apparent size (the second script's main body height against the Latin x-height), stroke contrast (a high-contrast Latin serif with a modulated partner, a monoline sans with a monoline partner) and terminals (round with round, flat with flat). A mismatched partner looks like a font that failed to load.
- **Stack order: brand face first, script face second.** Font selection runs one character at a time, so Latin glyphs come from the first family and the other script falls through to the second. Subset with `unicode-range` so each visitor downloads only the scripts on the page.
- **Fix size mismatch on the `@font-face`** with `size-adjust` (Chrome 92, Firefox 92, Safari 17), or with `font-size-adjust` on the text (Baseline since 2024-07). `size-adjust` only works on an `@font-face` you write yourself; with a hosted CSS API, wrap the second script in a `:lang()` rule and tune `font-size` there.

```css
/* One family name, two files split by unicode-range: the browser fetches only what the page uses */
@font-face { font-family: "App Sans"; src: url(/fonts/brand-latin-var.woff2) format("woff2");
  font-weight: 100 900; font-display: swap; unicode-range: U+0000-024F, U+2000-206F, U+20AC, U+2122; }
@font-face { font-family: "App Sans"; src: url(/fonts/partner-script-var.woff2) format("woff2");
  font-weight: 100 900; font-display: swap; size-adjust: 104%;  /* tune by eye on a mixed sentence */
  unicode-range: U+0900-097F; }                                 /* the partner script's block (here Devanagari) */
html { font-family: "App Sans", system-ui, sans-serif; }
```

**Font budget across scripts.** Count families per script: ≤ 2 per script (one display, one text). Prefer a text family that ships both scripts, so one family carries body and UI everywhere. Keep the WOFF2 files the first viewport fetches to ≤ 4 (each family × weight range × script subset is a file) and preload ≤ 2 (Font loading). CJK fonts are large: use the system stack or a service that slices them into many `unicode-range` subsets.

**Vertical space and clipping**
- Tall scripts stack marks above and below the base letter. Body and UI text never below line-height 1.5; headings follow the table in "Line-height, measure, tracking". Check that marks on a wrapped second line do not touch the line above.
- No fixed `height` on buttons, inputs, chips, tabs or table rows: padding plus `min-height`.
- `overflow: hidden`, `-webkit-line-clamp` and `text-overflow: ellipsis` clip marks when line-height is tight. Give clamped text line-height ≥ 1.6 plus 2–4 px **`padding-top` only**. Bottom padding sits inside the clip box, so the upper marks of the next, clamped-away line show through as stray marks along the bottom edge (reproduced in headless Chrome, 2026-10-10).
- `background-clip: text` paints nothing outside the element box: give lines padding with an equal negative margin so ascenders, descenders and marks survive.

**Line breaking**
- **Set `lang`** on `<html>` and on every run in another language. Segmentation, hyphenation, font fallback, `:lang()` rules and screen-reader voices depend on it.
- **Scripts without word spaces** (Thai, Lao, Khmer, Burmese): spaces separate phrases, and browsers find word boundaries by dictionary. Dictionaries miss names, brand terms, compounds and transliterations, which then break mid-word. Look at every heading, lead and button label at 320, 390 and 768 px with a native reader, and pass the phrases they flag to `scripts/shoot.mjs --keep-words`.
- **Chinese and Japanese** break between most characters; `line-break: strict` keeps small kana and punctuation off line starts. `word-break: auto-phrase` breaks Japanese at phrase boundaries (Chrome 119 only: enhancement for headings). `text-autospace` adds the small gap between CJK and Latin runs (Limited). **Korean** reads better with `word-break: keep-all` (breaks at spaces).
- `word-break: keep-all` affects CJK only. `word-break: break-all` breaks every script anywhere: remove it (it often comes from a global reset). Keep `overflow-wrap: anywhere` only as a safety net for URLs and long codes.
- **Protect short phrases, hint long ones.** `<span style="white-space:nowrap">` is for a word or two (a compound, a brand name, "New York"). A long protected phrase cannot wrap and will overflow at tablet width: there, add `<wbr>` at the real boundaries instead (it adds a break opportunity and no character to copied text; `&shy;` adds a hyphen when the break is used).
- **Inside a flex container** (a `display: flex` list item with an icon, a chip row) every bare text run and every span becomes its own flex item, so a nowrap span is pulled out of the sentence and the words wrap out of order. Wrap the whole label in one element so only that wrapper is the flex item.
- `text-wrap: balance` balances with the browser's break opportunities; in space-less scripts combine it with `<wbr>` hints.
- **Justification:** left-align (start-align) body text in UI. Justified text needs hyphenation or script-specific stretching (kashida, inter-character spacing) that browsers do unevenly.
- **Truncate and split by grapheme or word with `Intl.Segmenter`** (Baseline April 2024), never `str.slice()` or per character: a slice can separate a base letter from its mark, an emoji from its modifier or a flag from its second half.

```ts
const locale = document.documentElement.lang || "en";
const graphemes = new Intl.Segmenter(locale, { granularity: "grapheme" });
const words = new Intl.Segmenter(locale, { granularity: "word" });
export const truncate = (s: string, n: number) => {
  const g = Array.from(graphemes.segment(s), (x) => x.segment);
  return g.length > n ? g.slice(0, n).join("") + "…" : s;
};
// Word-level units for kinetic type, SVG/canvas text or <wbr> hints in space-less scripts
export const wordUnits = (s: string) => Array.from(words.segment(s), (w) => w.segment);
```

**Case, emphasis and tracking**
- **Most scripts have no case.** A style whose signature is UPPERCASE with wide tracking needs a substitute device (weight, size, colour, a rule) in those scripts; `text-transform: uppercase` silently does nothing there.
- **No synthetic italics or bold.** Scripts without an italic tradition get slanted fakes: set `font-synthesis: none` and emphasise with weight or colour (`text-emphasis` marks in CJK).
- **Tracking:** none on joined scripts (letter-spacing breaks Arabic joining and disables optional ligatures; reset with `:lang(ar) { letter-spacing: normal }`), none negative on scripts with stacked marks. Positive tracking on CJK display text is conventional and safe.
- **Numerals:** show the numerals the locale expects through `Intl.NumberFormat`; keep `tabular-nums` for columns.

**Text expansion.** Translated UI is longer than English, and short strings grow the most (W3C, from IBM's table):

| English length | Room to allow |
|---|---|
| up to 10 characters | 200–300% |
| 11–20 | 180–200% |
| 21–30 | 160–180% |
| 31–50 | 140–160% |
| 51–70 | about 150–170% |
| over 70 | 130% |

Design every label, tab and button to hold twice its English length: let controls grow, wrap to two lines or shorten the source copy. Never fix the width of a text container. Test with the longest locale you ship, or a pseudo-locale, before translations arrive.

## Font loading

- **Format and size**: WOFF2 only (about 30% smaller than WOFF). Use variable fonts when you need 3+ weights. Subset with `unicode-range` (Latin fonts carry 100–1,000 glyphs; most alphabetic scripts are small subsets and cheap to preload, CJK is not).
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
| Marks above or below letters are cut off in buttons, chips, clamped text | Tight line-height plus `overflow:hidden` / line-clamp / fixed height | line-height ≥1.6, `min-height` + padding, 2–4px `padding-top` on clamped blocks |
| Stray marks along the bottom edge of clamped text | `padding-block` (bottom padding) reveals the top of the clamped-away next line | `padding-top` only on clamped blocks |
| Names, brand words or compounds split across lines | The line breaker's dictionary doesn't know the word, or the phrase should stay together | `white-space:nowrap` span for short phrases; `<wbr>` at real boundaries for longer ones; check 320, 390 and 768px; `shoot.mjs --keep-words` |
| Heading overflows its column at tablet width (768px) | A long phrase wrapped in a `nowrap` span can't break | Replace the span with `<wbr>` hints at word boundaries |
| Words in a flex list item wrap out of order | A nowrap span (or bare text next to a span) inside `display:flex` becomes a separate flex item | Put the whole label in one wrapper element; style children with `.x > span`, not `.x span` |
| Text breaks at random characters | `word-break: break-all` (often from a global reset) | Remove it; `overflow-wrap:anywhere` only for URLs/codes |
| "keep-all" has no effect outside CJK | `keep-all` only changes CJK; other scripts behave as normal | Use `nowrap` spans or `<wbr>` |
| Truncated text shows a floating mark, a dotted circle or half an emoji | `slice()` split a grapheme cluster | `Intl.Segmenter` grapheme truncation |
| A script renders in a different font than designed | Missing `lang`, or that script's subset wasn't loaded | `lang`, load the subset, composite `@font-face` |
| Uppercase, tracked labels look unstyled in another language | The script has no case; tracking was reset for it | A second device for emphasis: weight, colour, size or a rule |
| Translated button text overflows or is cut | Width fixed for the English label | Let the control grow or wrap; allow 200% for short labels |
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
- MDN font-family (font selection is per character) — https://developer.mozilla.org/en-US/docs/Web/CSS/font-family ; letter-spacing — https://developer.mozilla.org/en-US/docs/Web/CSS/letter-spacing ; text-autospace — https://developer.mozilla.org/en-US/docs/Web/CSS/text-autospace
- W3C Internationalization: text size in translation (expansion table, vertical space) — https://www.w3.org/International/articles/article-text-size ; approaches to line breaking — https://www.w3.org/International/articles/typography/linebreak ; structural markup and right-to-left text — https://www.w3.org/International/questions/qa-html-dir ; personal names around the world — https://www.w3.org/International/questions/qa-personal-names
- W3C layout requirements: Japanese — https://www.w3.org/TR/jlreq/ ; Chinese — https://www.w3.org/TR/clreq/ ; Arabic script — https://www.w3.org/TR/alreq/
- Material Design typography, language support (English-like, tall, dense; mirror of the M2 page) — https://zavoloklom.dev/material-design-typography/
- web.dev font best practices — https://web.dev/articles/font-best-practices ; CSS size-adjust — https://web.dev/articles/css-size-adjust ; fetchpriority — https://web.dev/articles/fetch-priority ; container queries stable — https://web.dev/blog/cq-stable
- Next.js font module — https://nextjs.org/docs/app/api-reference/components/font ; Capsize — https://seek-oss.github.io/capsize/ ; fontaine — https://github.com/unjs/fontaine
- 8-point grid (spec.fm) — https://spec.fm/specifics/8-pt-grid
- Android window size classes — https://developer.android.com/develop/ui/compose/layouts/adaptive/use-window-size-classes
- MDN container queries — https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_containment/Container_queries ; subgrid — https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_grid_layout/Subgrid ; responsive images — https://developer.mozilla.org/en-US/docs/Web/HTML/Guides/Responsive_images
- NN/g visual hierarchy — https://www.nngroup.com/articles/visual-hierarchy-ux-definition/
