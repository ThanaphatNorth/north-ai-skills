# Raw research notes — color, typography & layout (design-atlas)

Collected 2026-10-10. Provenance record for `skills/design-atlas/references/color.md` and `typography-layout.md`.
"Computed" = calculated in this session with a local OKLCH/WCAG/APCA script (sRGB, CSS Color 4 OKLab matrices, WCAG 2 relative luminance, APCA 0.0.98G constants; sanity-checked: #888 on white = Lc 63.1, black/white = 21:1).

## OKLCH / CSS Color 4–5

- OKLCH L is perceived lightness; HSL L varies by hue so contrast shifts when hue changes. Syntax `oklch(L C H / a)`; L 0–1 or %, C ≥ 0 and below ~0.37 for sRGB+P3, H degrees (approx anchors red 20, yellow 90, green 140, blue 220, purple 320). Use decimals not % inside `calc()` in relative colors. Max chroma depends on L and H. Out-of-gamut colors: Chrome & Safari clip (hue may shift). Recommend sRGB value in base + P3 value under `@media (color-gamut: p3)`. Example `oklch(0.7 0.2 145)` → P3 `oklch(0.7 0.29 145)`. For user-supplied colors keep hue, fix L/C (article uses L 0.87 C 0.06; black text works on L ≥ 87%). Huetone uses Oklab. — https://evilmartians.com/chronicles/oklch-in-css-why-quit-rgb-hsl
- Relative color syntax: `oklch(from var(--x) calc(l + 0.1) c h)`; channel keywords resolve to numbers (no `%` in calc); hue math unitless, older Safari needed `deg` → `@supports (color: oklch(from red l c calc(h + 180deg)))`; output not gamut-clamped; `@supports` test must not use var(). — https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_colors/Relative_colors
- `color-mix()` default space oklab; polar default `shorter hue`; percentages normalise; sum <100% adds transparency. Baseline widely available since May 2023. — https://developer.mozilla.org/en-US/docs/Web/CSS/color_value/color-mix
- `<color-interpolation-method>`: `in <rectangular>` or `in <polar> [shorter|longer|increasing|decreasing hue]`; MDN: default interpolation space Oklab. Examples `linear-gradient(in oklch longer hue to right, blue, red)`. — https://developer.mozilla.org/en-US/docs/Web/CSS/color-interpolation-method
- Browser versions from MDN browser-compat-data (main branch, read 2026-10-10; https://github.com/mdn/browser-compat-data):
  - oklch()/oklab(): Chrome 111, Firefox 113, Safari 15.4
  - color-mix(): Chrome 111, Firefox 113, Safari 16.2 (variadic args: Firefox 150, Safari 27, Chrome no)
  - oklch relative syntax: Chrome 122, Firefox 128, Safari 18 (lab relative Safari 16.4)
  - gradient interpolation color space / hue method (linear/radial/conic): Chrome 111, Firefox 127, Safari 16.2
  - light-dark(): Chrome 123, Firefox 120, Safari 17.5
  - contrast-color(): Chrome 147, Firefox 146, Safari 26
  - text-wrap balance: Chrome 114, Firefox 121, Safari 17.5; pretty: Chrome 117, Safari 26, Firefox no
  - word-break auto-phrase: Chrome 119 only; keep-all Chrome 44, Firefox 15, Safari 9
  - @font-face size-adjust: Chrome 92, Firefox 92, Safari 17; ascent/descent/line-gap-override: Chrome 87, Firefox 89, Safari "preview" (not stable)
  - text-box / text-box-trim: Chrome 133, Firefox 154, Safari 18.2
  - font-size-adjust: Chrome 127, Firefox 3, Safari 16.4
  - @container + cq units: Chrome 105, Firefox 110, Safari 16; subgrid: Chrome 117, Firefox 71, Safari 16
  - lh unit: Chrome 109, Firefox 120, Safari 16.4; rlh: Chrome 111, Firefox 120, Safari 16.4; cap unit: Chrome 118, Firefox 97, Safari 17.2
  - @property: Chrome 85, Firefox 128, Safari 16.4
- `contrast-color()` (CSS Color 5): returns black or white, algorithm UA-defined but all engines use WCAG 2 luminance; tie → white; Baseline newly available April 2026; Level 6 to add candidate lists/targets (WD). Fallback pattern with `@supports (color: contrast-color(red))`. Recipes: `oklch(from contrast-color(var(--bg)) l 0.05 var(--bg-hue))`, `color-mix(in oklch, contrast-color(var(--bg)) 80%, var(--bg))`. Cites #2277d3 as WCAG-pass-but-poor example. — https://smashingmagazine.com/2026/05/building-self-correcting-color-systems-contrast-color

## Tonal scales

- Tailwind v4 palette defined in OKLCH; 11 steps 50–950; chromatic: red, orange, amber, yellow, lime, green, emerald, teal, cyan, sky, blue, indigo, violet, purple, fuchsia, pink, rose; grays: slate, gray, zinc, neutral, stone, taupe, mauve, mist, olive. `@theme { --color-x: … }`, `--color-*: initial` to reset, `--alpha()` function, opacity modifiers `bg-sky-500/10`. — https://tailwindcss.com/docs/colors
- Tailwind v4.2 added mauve, olive, mist, taupe ("neutral-ish palettes … still behaves like gray, but has a little more personality"); v4.3 (May 8 2026) added no colors. v4.0 Jan 22 2025. — https://tailwindcss.com/blog/tailwindcss-v4-3 , https://tailwindcss.com/blog
- Tailwind theme.css values (https://github.com/tailwindlabs/tailwindcss/blob/main/packages/tailwindcss/theme.css):
  - blue: 50 97%/.014/254.6 · 100 93.2/.032 · 200 88.2/.059 · 300 80.9/.105 · 400 70.7/.165 · 500 62.3/.214/259.8 · 600 54.6/.245/262.9 · 700 48.8/.243 · 800 42.4/.199 · 900 37.9/.146 · 950 28.2/.091/267.9
  - orange: 50 98/.016/73.7 … 500 70.5/.213/47.6 · 600 64.6/.222/41.1 · 700 55.3/.195/38.4 · 950 26.6/.079/36.3
  - amber hue drift: 50 H95.3 → 500 H70.1 → 700 H49 → 950 H45.6
  - red: 500 63.7/.237/25.3, 600 57.7/.245/27.3
  - green: 500 72.3/.219/149.6, 600 62.7/.194/149.2
  - slate chroma 0.003 (50) → 0.046 (500) → 0.042 (950); neutral C 0; mauve C ≤0.034; olive ≤0.031; mist ≤0.021; taupe ≤0.021.
  - Lightness bands across chromatic hues: 50 ≈97–98.7, 100 ≈93–96, 200 ≈88–92.5, 300 ≈81–88, 400 ≈70–83, 500 ≈62–77, 600 ≈55–67, 700 ≈49–56, 800 ≈42–47, 900 ≈38–41, 950 ≈26–28.
- Radix Colors 12-step scale: 1 app background; 2 subtle background; 3 UI element bg; 4 hovered UI element bg; 5 active/selected bg; 6 subtle borders/separators; 7 UI element border & focus rings; 8 hovered border; 9 solid backgrounds (highest chroma, "purest"); 10 hovered solid; 11 low-contrast text; 12 high-contrast text. Steps 11/12 guaranteed APCA Lc 60 / Lc 90 on step 2. Step 9 meant for white text except Sky, Mint, Lime, Yellow, Amber (dark text). — https://www.radix-ui.com/colors/docs/palette-composition/understanding-the-scale
- Radix composing: pair accent with gray "saturated with the hue closest to your accent hue" (mauve=purple, slate=blue, sage=green, olive=lime, sand=yellow) or pure gray; semantic pairings "work well in Western culture": error red/ruby/tomato/crimson; success green/teal/jade/grass/mint; warning yellow/amber/orange; info blue/indigo/sky/cyan. Text: accent 11/12 for marketing, gray 11/12 for apps. — https://www.radix-ui.com/colors/docs/palette-composition/composing-a-palette
- Radix custom palette generator (accent, gray, background, light/dark → 12-step scales). — https://www.radix-ui.com/colors/custom
- Material Color Utilities (https://github.com/material-foundation/material-color-utilities):
  - HCT: hue 0–360, chroma 0 to ~120 max, tone 0 (black) – 100 (white). Source color → 4 more key colors → 5 tonal palettes of 13 tones (0,10,20,30,40,50,60,70,80,90,95,99,100). (concepts/dynamic_color_scheme.md)
  - "a difference of 40 in tone guarantees a WCAG contrast ratio ≥ 3.0; a difference of 50 in tone guarantees a contrast ratio ≥ 4.5". Default contrast: 4.5:1 all text/icons, 3:1 required non-text; medium: discretionary 7:1; high: 7:1 text, 4.5:1 non-text. T50 background + white tops out ≈4.5:1. (concepts/contrast_for_accessibility.md, scheme_generation.md)
  - primary = tone 40 light / tone 80 dark (scheme_generation.md).
  - Scheme variants (typescript/scheme/*.ts): TonalSpot "low to medium colorfulness… default Material You theme on Android 12 and 13"; Vibrant "maxes out colorfulness"; Expressive "intentionally detached from the source color"; Fidelity & Content "place the source color in primaryContainer… constant appearance in light and dark"; Rainbow & FruitSalad "source color's hue does not appear"; Monochrome; Neutral.
  - Extraction: quantize (Celebi = Wu + WSMeans), score favoring chroma near 48 and hue diversity (30° neighbourhoods), filter near-gray and rare colors. (concepts/color_extraction.md)
  - DislikeAnalyzer: disliked if hue 90–111, chroma >16, tone <65 (dark yellow-green, Palmer & Schloss 2010) → fix by tone 70. (typescript/dislike/dislike_analyzer.ts)
- Adobe Leonardo: generate colors from target contrast ratios against a background; npm `@adobe/leonardo-contrast-colors`, `generateContrastColors()`, outputs often slightly above target. — https://github.com/adobe/leonardo , https://leonardocolor.io

## Contrast standards

- WCAG 2.2 1.4.3: 4.5:1 text, 3:1 large (18pt=24px, or 14pt bold ≈18.5px bold); no rounding (4.499 fails); exceptions: disabled, decorative, logotypes (not when logo is a control). — https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html
- 1.4.11: 3:1 for UI component visuals needed to identify/operate, states, focus indicators, icons, graph lines, pie slices; gradients tested at least-contrasting area; hover change not required to hit 3:1 vs default. — https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html
- 1.4.12 text spacing: line-height 1.5, paragraph spacing 2×, letter 0.12em, word 0.16em overrides must not clip/overlap; scripts that don't use a property (e.g. word spacing without spaces) conform with those they use. — https://www.w3.org/WAI/WCAG22/Understanding/text-spacing.html
- APCA Lc: 90 preferred body (≥18px/300 or 14px/400); 75 min body columns (24px/300, 18px/400, 16px/500, 14px/700); 60 min other content text (48/200, 36/300, 24/400, 16/700); 45 headlines (36px/400, 24px bold) & detailed pictograms; 30 absolute min any text (placeholder, disabled), solid icons; 15 non-semantic non-text (dividers), "anything below this level as invisible". — https://git.apcacontrast.com/documentation/APCA_in_a_Nutshell
- WCAG 3: APCA removed from WD July 2023 (marked Jan 30 2023); April 8 2026 Editor's Draft: "The contrast algorithm used in WCAG 3 is yet to be determined"; WCAG 2 remains baseline; final ~2030+. — https://adrianroselli.com/2026/04/wcag3-contrast-as-of-april-2026.html ; WD Sept 2025 notice https://www.w3.org/WAI/news/2025-09-04/wcag3
- Apple HIG dark mode: contrast "no lower than 4.5:1"; custom colors "strive for 7:1, especially in small text"; base (dimmer) vs elevated (brighter) backgrounds; dark palette "dimmer background colors and brighter foreground colors"; "aren't necessarily inversions"; soften white image backgrounds. — https://developer.apple.com/design/human-interface-guidelines/dark-mode
- Apple HIG color: don't rely solely on color; red = danger in some cultures, positive in others; Stocks app green = up (English) vs red = up (Chinese); use color sparingly on Liquid Glass. — https://developer.apple.com/design/human-interface-guidelines/color
- Material (Android) dark theme: backgrounds "dark grey instead of black, which increases visibility for shadows and also reduces eye strain for light text"; elevation overlays (primary at alpha by elevation) replaced by tonal surface colors. — https://github.com/material-components/material-components-android/blob/master/docs/theming/Dark.md

## Computed (this session)

- HSL both L=50%: yellow #FFFF00 = oklch(96.8% .211 110), white text 1.07:1; blue #0000FF = oklch(45.2% .313 264), white text 8.6:1.
- White × black contrast always multiplies to 21 (1.05/(Y+.05) × (Y+.05)/.05), so at the crossover both are √21 ≈ 4.58:1 — a fill can never fail 4.5:1 with both.
- WCAG 4.5:1 thresholds vs OKLCH L at C 0.15: white text passes at L ≤ 0.554 (green) … 0.587 (pink); black text passes at L ≥ 0.545 (green) … 0.579 (pink); gray: white ≤0.567, black ≥0.561. → rule of thumb: L ≤ 0.55 white text, L ≥ 0.60 dark text.
- Blue→yellow midpoint: sRGB #808080 (gray); Oklab #6CABC7 (C 0.077); OKLCH shorter hue #08BAAE oklch(71.1% .123 187).
- Sample logo colors: #FF6A13 oklch(70.1% .200 44): white 2.87:1, black 7.32:1, APCA white-on Lc 59 vs black-on Lc 50 (WCAG2/APCA disagree). #7FD1C7 pastel teal: white 1.77:1, black 11.85:1. #39FF14 neon green: white 1.36:1, black 15.5:1. #FFC600: white 1.58, black 13.3. #E4002B: white 4.85, black 4.33.
- Anchored scale for #FF6A13 (L targets .98/.955/.90/.835/.75/.68/.61/.53/.46/.40/.27, chroma multipliers .08/.18/.36/.6/.85/1/1/.9/.75/.6/.4, brand pinned at nearest step 500): 50 #FFF6F3, 100 #FEECE4, 200 #FFD3C1, 300 #FFB596, 400 #FF8954, 500 #FF6A13, 600 #D65500 (white 4.07), 700 #B14501 (white 5.64), 800 #923700 (7.58), 900 #782C00, 950 #441600.
- Same method for #2F6BFF lands brand at 600 (white 4.50 exactly — fragile).
- Brand-tinted neutrals (H 44): 50 #FDF9F8 … 500 #7C706C … 950 #0C0908 (C .004–.016).
- Semantic at L .55 C .16: success #02893D (white 4.52), warning #986600 (white 4.96, looks ochre), danger #BD423A (5.24), info #0177BC (4.81).
- Dark tokens for orange brand: bg #130E0D (L .17), surface #1C1715 (.21), raised #27201D (.25), border #3B3430 (.33), text #F2EDEB (.95, 16.5:1), muted #ADA29E (.72, 7.7:1), primary #F97B40 (L .72 C .17, 7.2:1 vs bg, use bg-colored text on it).
- #121212 = oklch(18.2% 0 —); #1C1C1E = oklch(22.7% .004 286).
- 13 mood palettes generated and checked (see color.md table); adjustments: energetic primary L .55 (#C93200, white 5.33; L .57 #D33500 gave only 4.91); AI primary for white-text buttons L .55 (#7E4ED7, 5.3).

## Harmony, proportion, psychology, culture

- NN/g: limit palette to ~3 colors; harmonies analogous/complementary/triadic/split-complementary/monochromatic; 60-30-10 (dominant & secondary relatively neutral); reserve accent for primary CTA; gray buttons can look disabled; "safest to assume that color interpretation will vary from culture to culture"; validate with users. — https://www.nngroup.com/articles/color-enhance-design/
- NN/g visual hierarchy: color/contrast, scale, grouping; simple designs ≤ 2 primary + 2 secondary colors; ≤3 contrast variations; ≤3 sizes (web body ~14–16px, subheads 18–22, headers ≤32); ≤2 large elements; bright warm colors for warnings; squint/blur test (5–10px blur). — https://www.nngroup.com/articles/visual-hierarchy-ux-definition/
- Elliot (2015) Frontiers in Psychology 6:368 mini review: color & psychological functioning research at "nascent stage", caution on conclusions and application. — https://www.frontiersin.org/articles/10.3389/fpsyg.2015.00368/full
- Labrecque & Milne (2012) "Exciting red and competent blue", J. Academy of Marketing Science 40(5) 711–727: hue/saturation/value relate to brand personality perceptions (4 studies). (abstract-level only) — https://colab.ws/articles/10.1007%2Fs11747-010-0245-y
- Thailand:
  - Day colors: Sun red, Mon yellow, Tue pink, Wed green (night grey), Thu orange, Fri (light) blue, Sat purple; Monday yellow linked to Rama IX & Rama X (born Monday); yellow "most associated with royalty"; royal flags of Rama X and Rama IX are yellow; Queen Sirikit (Friday) blue, Queen Suthida (Saturday) purple. — https://www.thethailandlife.com/color-day-thailand ; also https://iamkohchang.com/blog/colors-of-the-day-thailand.html (search result)
  - Flag (1917): "red for the land and people, white for religions and blue for the monarchy". — https://en.wikipedia.org/wiki/Flag_of_Thailand
  - Red ink for names: bad luck / associated with the dead (Chinese-rooted, persists in Thai society). — Thairath (search result, page timed out): https://en.thairath.co.th/horoscope/belief/2947636 ; USC folklore archive https://folklore.usc.edu/chinese-red-ink-superstition/
  - Mourning: black main, white also; 2016 national mourning: black/white for 30 days, civil servants a year; visitors advised muted (black, white, grey, dark blue), avoid loud colors. — https://www.thailandstarterkit.com/moving/what-to-do-during-the-mourning-period-in-thailand/ ; https://my.trip.com/guide/info/thailand-national-mourning.html (search results)
  - Red-shirt/yellow-shirt political colors noted in culture-guide search results (not opened in detail; treat as background).
- Color vision deficiency: "About 1 in 12 men"; red-green most common (NEI) — https://www.nei.nih.gov/learn-about-eye-health/eye-conditions-and-diseases/color-blindness ; Okabe & Ito: 8% Caucasian, 5% Asian, 4% African males red-green — https://jfly.uni-koeln.de/color/
- Okabe–Ito palette hex (consistent across secondary sources; Wong 2011 Nature Methods 8:441): #E69F00 orange, #56B4E9 sky blue, #009E73 bluish green, #F0E442 yellow, #0072B2 blue, #D55E00 vermillion, #CC79A7 reddish purple, #000000. — https://rdrr.io/cran/factoextra/man/factoextra_palette.html (search result)

## Tools (URLs resolved 200 on 2026-10-10)

- Realtime Colors https://www.realtimecolors.com — preview text/bg/primary/secondary/accent + fonts on a realistic site, light/dark, export CSS/SCSS/Tailwind.
- Huemint https://huemint.com — ML palettes for brand, website, graphics.
- Coolors https://coolors.co ; Leonardo https://leonardocolor.io ; Radix custom https://www.radix-ui.com/colors/custom ; uicolors.app https://uicolors.app (Tailwind scale generator, previews on components) ; oklch.com https://oklch.com (picker/converter) ; Khroma https://www.khroma.co (AI, learns preferences) ; Adobe Color https://color.adobe.com ; Huetone https://huetone.ardov.me ; APCA calculator https://apcacontrast.com ; WebAIM checker https://webaim.org/resources/contrastchecker/ ; ColorBrewer https://colorbrewer2.org ; Utopia https://utopia.fyi/type/calculator ; Capsize https://seek-oss.github.io/capsize/ ; fontaine https://github.com/unjs/fontaine ; Josh Comeau gradient generator https://www.joshwcomeau.com/gradient-generator/

## Typography

- Utopia: define type scale at small viewport and large viewport, interpolate; example 1.2 @320px → 1.333 @1500px. — https://utopia.fyi/blog/designing-with-fluid-type-scales/
- Utopia clamp math: slope = (max−min)/(maxW−minW); intercept = −minW·slope + min; `clamp(min, intercept + slope·100vw, max)`; example 1rem@320 → 2rem@1440 = `clamp(1rem, 0.7143rem + 1.4286vw, 2rem)`. — https://utopia.fyi/blog/clamp/
- utopia-core npm README example: 320–1240px, 18→20px base, 1.2→1.25, step 5 = `clamp(2.7994rem, 2.4461rem + 1.7663vw, 3.815rem)`; WCAG 1.4.4 flag per step. — https://npmjs.com/utopia-core (search result)
- Utopia space: step 0 = S; multipliers 0.25/0.5/0.75 below, 1.5/2/3/4/6 above; t-shirt names 3XS…3XL; pairs like s-l interpolate (example 18px→44px). — https://utopia.fyi/blog/painting-with-a-fluid-space-palette/
- Fluid type & WCAG 1.4.4: "The maximum value must be less than or equal to 2.5 times the minimum value" (viewport units don't scale with zoom; 500% max zoom). — https://smashingmagazine.com/2023/11/addressing-accessibility-concerns-fluid-type
- Computed fluid scale (this session) 360→1280px, 16→18px, 1.2→1.25: step-2 0.6944→0.72rem; step-1 0.8333→0.9; step0 `clamp(1rem, 0.9511rem + 0.2174vw, 1.125rem)`; step1 `clamp(1.2rem, 1.1193rem + 0.3587vw, 1.4062rem)`; step2 `clamp(1.44rem, 1.3156rem + 0.5527vw, 1.7578rem)`; step3 `clamp(1.728rem, 1.5444rem + 0.8161vw, 2.1973rem)`; step4 `clamp(2.0736rem, 1.8103rem + 1.1704vw, 2.7466rem)`; step5 `clamp(2.4883rem, 2.1186rem + 1.6433vw, 3.4332rem)`.
- Material 3 type scale tokens (material-web v0_192 `_md-sys-typescale.scss`, https://github.com/material-components/material-web/blob/main/tokens/versions/v0_192/_md-sys-typescale.scss): display L 3.5625rem/4rem (57/64) tracking −0.015625rem; display M 45/52; display S 36/44; headline L 32/40, M 28/36, S 24/32; title L 22/28 (400), M 16/24 (500, +0.009375rem), S 14/20 (500, +0.00625rem); body L 16/24 (+0.03125rem), M 14/20 (+0.015625rem), S 12/16 (+0.025rem); label L 14/20 (500, +0.00625rem), M 12/16 (500, +0.03125rem), S 11/16 (500, +0.03125rem). Weights regular 400 / medium 500 / bold 700.
- Line length: Baymard 50–75 chars body (Ruder 50–60), ≤80 (WCAG 1.4.8; CJK ≤40); users fatigue at 100+; CSS max-width ~70ch/34em. — https://baymard.com/blog/line-length-readability ; Butterick "Aim for an average line length of 45–90 characters, including spaces" — https://practicaltypography.com/line-length.html
- text-wrap: balance for ≤6 lines (Chromium) / ≤10 (Firefox); pretty for body (perf cost); text-wrap Baseline widely available since March 2024. — https://developer.mozilla.org/en-US/docs/Web/CSS/text-wrap
- Font loading (web.dev): preconnect fonts.googleapis.com + fonts.gstatic.com (crossorigin); inline @font-face; preload carefully (ignores unicode-range, one format); WOFF2 ~30% smaller than WOFF; Latin fonts 100–1,000 glyphs vs CJK 10,000+; self-host only with CDN + HTTP/2; variable fonts larger but replace many files; font-display block (2–3s block, infinite swap), swap (0ms, infinite), fallback (100ms, 3s), optional (100ms, no swap); Chromium & Firefox block up to 3s, Safari indefinitely; combine swap for branding + optional for body. — https://web.dev/articles/font-best-practices
- size-adjust/ascent-override/descent-override/line-gap-override examples (size-adjust 86% Arial; Roboto → Arial 100.06%); Malte Ubl's calculator. — https://web.dev/articles/css-size-adjust
- next/font: self-hosts Google Fonts at build, no browser requests to Google; display default 'swap'; preload default true per subsets; adjustFontFallback default true (google) / 'Arial' (local); `declarations` for ascent-override etc. (docs v16.4.0, updated 2026-09-24). — https://nextjs.org/docs/app/api-reference/components/font

## Google Fonts metadata (https://fonts.google.com/metadata/fonts, fetched 2026-10-10)

Existence checked via css2 API (HTTP 200) for every family named in the references. Not on Google Fonts: "LINE Seed Sans TH" (LINE Seed JP is, added 2026-01-21).
Popularity rank (lower = more used): Roboto 2, Open Sans 3, Inter 5, Montserrat 7, Poppins 8, Lato 9, Roboto Mono 17, Oswald 18, DM Sans 21, Raleway 23, Playfair Display 24, Nunito 25, Manrope 30, Outfit 33, Plus Jakarta Sans 36, Figtree 41, Space Grotesk 59, Bricolage Grotesque 63, Instrument Serif 83, Fraunces 84, Geist 94, Newsreader 125, Gloock 524, Young Serif 628.
Axes (selected): Inter opsz14–32 wght100–900; Geist wght100–900; Bricolage Grotesque opsz12–96 wdth75–100 wght200–800; Fraunces SOFT/WONK/opsz9–144/wght100–900; Newsreader opsz6–72 wght200–800; Source Serif 4 opsz8–60 wght200–900; Literata opsz7–72 wght200–900; Bodoni Moda opsz6–96 wght400–900; Archivo wdth62–125 wght100–900; Mona Sans/Hubot Sans wdth75–125 wght200–900; Big Shoulders opsz10–72 wght100–900; Roboto Flex 13 axes; Instrument Sans wdth75–100 wght400–700; Instrument Serif static; DM Sans opsz9–40 wght100–1000; Red Hat Display wght300–900 / Text 300–700; Public Sans wght100–900; Atkinson Hyperlegible Next wght200–800 (added 2025-01-06); Google Sans Flex (2025-11-12) 6 axes, no Thai.

Thai families (subsets / axes / weights / designer / added):
- Noto Sans Thai — thai+latin; wdth62.5–100, wght100–900; Google; loopless, "mainly suitable for headlines, packaging and advertising" (google/fonts ofl/notosansthai DESCRIPTION)
- Noto Sans Thai Looped — same axes; looped, "suitable for all texts"
- Noto Serif Thai — same axes; modulated serif
- IBM Plex Sans Thai — static 100–700 (7); Mike Abbink, Bold Monday; loopless ("informal", released 2018-10-15 per Wikipedia IBM Plex)
- IBM Plex Sans Thai Looped — static 100–700; looped ("formal", 2019-04-05)
- Anuphan — wght100–700 variable; Cadson Demak; loopless; Thai drawn from IBM Plex Sans Latin by Mint Tantisuwanna; includes Latin + Vietnamese
- Sarabun — 100–800 + italics; Suppakit Chalermlarp; = "TH Sarabun New" (national fonts), used in the Government Gazette
- Prompt — 100–900 + italics; Cadson Demak; loopless Thai + geometric Latin; similar glyphs ก ถ ภ ฤ ฦ, ฎ ฏ, บ ป, ข ช may confuse in very short texts
- Kanit — 100–900 + italics; Cadson Demak; formal loopless, humanist + capsulated geometric, flat terminals
- Mitr — 200–700; Cadson Demak; loopless, rounded terminals, casual
- Bai Jamjuree — 200–700 + italics; Cadson Demak; square sans (Eurostyle-inspired), headings & small passages
- Chakra Petch — 300–700 + italics; Cadson Demak; looped square sans with tapered corners
- Google Sans — thai subset; wght400–700, GRAD, opsz17–18; added 2025-12-09
- Playpen Sans Thai — wght100–800; TypeTogether et al.; added 2025-05-12
- Other Cadson Demak Thai+Latin on GF: Athiti, K2D, Krub, Niramit, Mali, Taviraj, Trirong, Pridi, Maitree, Chonburi, Charm, Itim, Sriracha, Thasadith, Pattaya (and KoHo, Kodchasan, Fahkwang, Srisakdi exist on GF).
- Google Fonts thai subset unicode-range: `U+02D7, U+0303, U+0331, U+0E01-0E5B, U+200C-200D, U+25CC`.
- LINE Seed Sans TH: download from https://seed.line.me/index_th.html, "All fonts are released under the SIL Open Font License, Version1.1"; weights listed Thin/Regular/Bold/ExtraBold/Heavy; simple shapes, rounded corners from the LINE logo. Loop style not stated.

## Thai typography research

- Typotheque (Héctor Mangas), Bangkok early 2024, approved by Chulalongkorn University; 180 native readers; Exp1 distance reading N=41: looped easier overall, younger struggled more with looped / older with loopless; Exp2 continuous reading (300–350 chars) N=38: looped "small significant" speed advantage, no age effect, comprehension equal; Exp3 survey N=139 (ages 20–70): looped = "classical", "formal"; loopless = "modern", "unusual"; looped preferred for more text at all ages; loopless preferred only by younger participants for less text. Recommendation: looped for paragraph reading; for distance reading consider age. — https://www.typotheque.com/research/effects-of-loops-in-thai
- Loopless style introduced in the 1970s; looped/loopless ≠ serif/sans (Granshan article, search result) — https://granshan.com/insights/bridging-cultures-through-letters-typotheques-typographic-journey-in-thailand
- IBM Plex Thai (Fontpad): looped familiar to older readers; loopless more relaxed; reduced stroke weight at junctions for even texture. — https://www.fontpad.co.uk/?p=1772 (search result)
- r12a Thai orthography notes: Gecko/WebKit/Blink wrap on grapheme cluster boundaries; dictionary-based word lookup fails for compounds & proper names; spaces separate phrases; ZWSP U+200B adds break, WJ U+2060 prevents; wrong ZWSP insertion causes problems; opening punctuation not at line end, ๆ not at line start; Thai uses alphabetic baseline; marks stack; "Thai tends to adds more interline spacing than Latin text does"; justification adjusts spaces between phrases, inter-character in narrow columns; letter-spacing must split ำ (U+0E33). — https://r12a.github.io/scripts/thai/th
- W3C Thai layout requirements (draft hub): "Spaces separate phrases, rather than words"; clusters surround base on up to 3 sides. — https://w3c.github.io/sealreq/thai/
- MDN word-break: keep-all "Word breaks should not be used for CJK text. Non-CJK text behavior is the same as for normal"; auto-phrase experimental (Chrome 119). — https://developer.mozilla.org/en-US/docs/Web/CSS/word-break
- Intl.Segmenter granularity grapheme/word/sentence, isWordLike; Baseline 2024 (April 2024). — https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl/Segmenter
- Clipping: tight line-height (1.1em) + overflow:hidden clipped Thai/Vietnamese marks in Discourse title bar (2017). — https://meta.discourse.org/t/in-title-bar-n-and-similar-diacriticals-are-clipped-in-linux/67303 (search result)

## Layout

- spec.fm 8-point grid: "Use multiples of 8 to define dimensions, padding, and margin"; 4pt baseline for type; hard vs soft grid; nudge 8; 16px root → .5rem steps. — https://spec.fm/specifics/8-pt-grid
- Android/Material window size classes: compact <600dp; medium 600–839; expanded 840–1199; large 1200–1599; extra-large ≥1600 (large/XL via `supportLargeAndXLargeWidth = true`); heights compact <480, medium 480–899, expanded ≥900 (page updated 2026-09-22). — https://developer.android.com/develop/ui/compose/layouts/adaptive/use-window-size-classes
- Container queries stable in all engines ~Feb 14 2023 (Chrome/Edge 105, Firefox 110, Safari 16). — https://web.dev/blog/cq-stable ; syntax & cq units (cqw/cqh/cqi/cqb/cqmin/cqmax; fallback to small viewport units) — https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_containment/Container_queries
- Subgrid: Baseline widely available since Sept 2023; card `grid-row: span 3; grid-template-rows: subgrid`; gaps inherited. — https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_grid_layout/Subgrid
- Responsive images: srcset w + sizes (first matching condition), x descriptors, `<picture><source media>` for art direction; `<img>` required; don't put media in sizes when art-directing. — https://developer.mozilla.org/en-US/docs/Web/HTML/Guides/Responsive_images
- fetchpriority="high" for LCP image (hint); Google Flights LCP 2.6s → 1.9s; support Chrome 102, Firefox 132, Safari 17.2. — https://web.dev/articles/fetch-priority

## Could not verify / gaps

- Inter dynamic-metrics tracking formula page is 404 (archived only) — not used.
- Material 2 dark-theme numbers (#121212, overlay %) not fetchable (JS site); only the Android doc's qualitative statement used.
- iOS dark systemBackground hex values not in fetched HIG text — not stated.
- LINE Seed Sans TH loop style; whether Thailand's stock apps use red-up or green-up — not verified, omitted.
- Thai line-height 1.6–1.8: practice guideline (r12a confirms Thai needs more interline space than Latin, gives no number).
