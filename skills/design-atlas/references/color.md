# Color

> Read when: choosing or generating a palette, turning a logo or brand hex into UI colors, building tonal scales or design tokens, setting up dark mode, picking semantic/state colors, writing gradients, choosing chart colors, checking contrast, or when a color choice must respect culture (incl. Thailand).

**Contents:** Defaults · Why OKLCH · Tonal scales · Harmony & proportion · Logo → palette method · Logo special cases · Semantic & state colors · Dark mode · Gradients · Data-viz color · Meaning: industry & culture · Example palettes · Tools · Pitfalls · Sources

Mechanics (extraction, scales, harmonies, tokens, WCAG + APCA report, CSS/Tailwind/DTCG export, HTML preview) live in the script: run `python3 scripts/palette.py --help`. This file is the method and the judgment.

## Defaults

- Structure for almost every UI: **one brand hue (11–12 step scale) + brand-tinted neutrals + at most one accent + 4 semantic colors** (success, warning, danger, info). NN/g: limit a palette to about three colors; reserve the accent for the primary action.
- Author every color in `oklch()`. Components consume **semantic tokens** only named as in `templates/tokens-starter.css` (`--bg`, `--surface`, `--text`, `--text-muted`, `--border`, `--primary`, `--primary-foreground`, `--focus-ring`…; Tailwind exposes them as `--color-*`). Raw scale steps (`--brand-600`) never appear in components; that is what makes theming and dark mode a token swap.
- Contrast floor = **WCAG 2.2 AA**: text 4.5:1; large text (≥24px, or ≥18.5px bold) 3:1; UI boundaries, focus indicators, icons, chart lines 3:1 (SC 1.4.11). Ratios are not rounded: 4.499:1 fails. Disabled controls and logotypes are exempt.
- Second opinion = **APCA** (Lc 90 preferred body, 75 minimum body, 60 other content text, 45 headlines, 30 placeholder/disabled, 15 dividers). APCA is *not* in WCAG 3: it was removed from the Working Draft in July 2023, and the April 2026 Editor's Draft still says the algorithm is "yet to be determined". Ship to WCAG 2; use APCA to catch the cases where WCAG 2 passes text that reads poorly.
- Rule of thumb, computed across hues at chroma 0.15: **white text reaches 4.5:1 at OKLCH L ≤ ≈0.55–0.59, black text at L ≥ ≈0.55–0.58.** Because white × black contrast always multiplies to 21, a fill at the crossover gives both only √21 ≈ 4.58:1. So: fills at **L ≤ 0.52 take white text, fills at L ≥ 0.65 take dark text**, and the band ≈0.53–0.64 is a low-margin zone. Avoid it for primary buttons.
- Never convey meaning by color alone (Apple HIG, WCAG 1.4.1). Pair color with an icon, label, pattern or position. Accessibility details: see `accessibility.md`.

## Why OKLCH

| Problem in HSL/hex | OKLCH behaviour |
|---|---|
| HSL `L` is not perceived lightness: `hsl(60 100% 50%)` yellow and `hsl(240 100% 50%)` blue both have "50%", but in OKLCH they are L 0.968 and L 0.452, and white text on them is 1.07:1 vs 8.6:1 | `L` is perceptual, so the same L gives similar contrast across hues. Scales and dark themes become predictable |
| Changing hue in HSL shifts contrast; LCH drifts in blues (≈270–330) | Hue rotates without moving lightness |
| hex/rgb/hsl can't express Display-P3 | the same function covers sRGB and P3 |

Syntax: `oklch(L C H / a)`, with L 0–1 (or %), C 0 (gray) to about 0.37, H in degrees. Rough hue anchors: red ≈25, orange ≈45, amber/yellow ≈85–110, green ≈145, teal ≈190, blue ≈250–265, violet ≈295, pink ≈340. Maximum chroma depends on L and H (at L 0.44 only blue reaches high chroma in sRGB). Chrome and Safari **clip** out-of-gamut colors, which can shift hue. Keep base values sRGB-safe and boost chroma for P3 screens:

```css
:root { --accent: oklch(0.70 0.20 145); }                 /* sRGB-safe */
@media (color-gamut: p3) { :root { --accent: oklch(0.70 0.29 145); } }
```

Support from MDN browser-compat-data, read 2026-10:

| Feature | Chrome | Firefox | Safari |
|---|---|---|---|
| `oklch()` / `oklab()` | 111 | 113 | 15.4 |
| `color-mix()` (Baseline since May 2023) | 111 | 113 | 16.2 |
| relative `oklch(from …)` | 122 | 128 | 18 |
| gradient `in oklch` / hue method | 111 | 127 | 16.2 |
| `light-dark()` | 123 | 120 | 17.5 |
| `contrast-color()` (returns black or white only, WCAG 2 math) | 147 | 146 | 26 |

Token recipes:

```css
:root {
  color-scheme: light dark;
  --brand: oklch(0.62 0.19 260);
  --brand-hover:  oklch(from var(--brand) calc(l - 0.05) c h);     /* no % inside calc */
  --brand-active: oklch(from var(--brand) calc(l - 0.09) c h);
  --brand-subtle: color-mix(in oklch, var(--brand) 12%, var(--bg));
  --focus-ring:   oklch(from var(--brand) l c h / 0.5);
  --complement:   oklch(from var(--brand) l c calc(h + 180));
  --bg: light-dark(oklch(0.985 0.004 260), oklch(0.17 0.01 260));
}
.btn { background: var(--brand); color: #fff; }
@supports (color: contrast-color(red)) {        /* the @supports test can't use var() */
  .btn { color: contrast-color(var(--brand)); } /* black/white, snaps at the threshold */
}
```

Older Safari needed `deg` in hue math. Guard it with `@supports (color: oklch(from red l c calc(h + 180deg)))`. Relative colors are not gamut-clamped, so lint them (for example with stylelint-gamut).

## Tonal scales

Pick a scale model to match the system you're feeding:

| System | Shape | Use it when |
|---|---|---|
| **Tailwind v4** | 11 steps 50–950 in OKLCH; 17 chromatic hues + 9 grays (v4.2 added `mauve`, `olive`, `mist`, `taupe`) | Tailwind projects; mapping brand hex to `--color-brand-*` via `@theme` |
| **Radix Colors** | 12 steps, each with a defined UI role; light + dark sets; alpha variants | Component libraries that need role clarity (bg → border → solid → text) |
| **Material 3 HCT** | Tonal palettes of 13 tones (0,10…90,95,99,100); 5 key colors; roles pick tones (primary = T40 light / T80 dark) | Android/Compose, "dynamic color", wallpaper/image-derived themes |
| **Adobe Leonardo** | Colors generated *from target contrast ratios* against a chosen background | When contrast guarantees per step matter more than even lightness spacing |

Tailwind's OKLCH lightness bands (across chromatic hues): 50 ≈0.97–0.99 · 100 ≈0.93–0.96 · 200 ≈0.88–0.92 · 300 ≈0.81–0.88 · 400 ≈0.70–0.83 · 500 ≈0.62–0.77 · 600 ≈0.55–0.67 · 700 ≈0.49–0.56 · 800 ≈0.42–0.47 · 900 ≈0.38–0.41 · 950 ≈0.26–0.28. Chroma peaks at 500–600 and tapers to both ends. Hue **drifts** across the scale (amber goes from H 95 at 50 to H 46 at 950) so dark yellows read as amber/brown, not olive.

Radix step roles (map any 12-step scale to these):

| Step | Role | Step | Role |
|---|---|---|---|
| 1 | App background | 7 | Interactive borders, focus rings |
| 2 | Subtle bg (cards, sidebar, code) | 8 | Hovered borders, strong focus |
| 3 | Component bg (default) | 9 | **Solid fill**, highest chroma ("purest") |
| 4 | Component bg (hover) | 10 | Solid fill (hover) |
| 5 | Component bg (active/selected) | 11 | Low-contrast text (APCA Lc 60 on step 2) |
| 6 | Subtle borders, separators | 12 | High-contrast text (APCA Lc 90 on step 2) |

Radix step 9 takes white text, except Sky, Mint, Lime, Yellow and Amber, which take dark text. That's the same lightness rule as in Defaults.

Material HCT facts worth reusing: a **tone difference of 40 guarantees ≥3:1 and 50 guarantees ≥4.5:1**. A tone-50 background with white text tops out at about 4.5:1. Scheme variants: *TonalSpot* (default, low-to-medium colorfulness), *Vibrant*, *Expressive* (detached from the source color), *Fidelity/Content* (put the exact source color in `primaryContainer`; **use these for brand work**), *Monochrome*, *Neutral*, and *Rainbow/FruitSalad* (the source hue doesn't appear at all).

Generic 11-step generator (the script implements this). It sets lightness targets per step, multiplies the brand's chroma by a per-step factor, keeps hue constant (or drifts yellows/oranges toward red as they darken), and gamut-maps by **reducing chroma, never clipping**:

| Step | 50 | 100 | 200 | 300 | 400 | 500 | 600 | 700 | 800 | 900 | 950 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| L target | .98 | .955 | .90 | .835 | .75 | .68 | .61 | .53 | .46 | .40 | .27 |
| C × brand C | .08 | .18 | .36 | .60 | .85 | 1 | 1 | .90 | .75 | .60 | .40 |
| Typical role | tint bg | subtle bg | hover bg / subtle border | border | strong border, icons on dark | brand solid (large) | solid / hover | **text-safe fill / links** | pressed, headings | text on tints | dark-mode tint surfaces |

## Harmony & proportion

| Scheme (OKLCH hue offsets) | UI use | Watch out |
|---|---|---|
| Monochrome (one hue, many L) | Enterprise, dashboards, editorial; the safest default | Needs strong lightness steps for hierarchy |
| Analogous (±30°) | Calm brands, gradients, illustration | Low contrast between hues; separate them by L |
| Complementary (+180°) | One CTA/accent that must pop against the brand | Use the complement at ≤10% area; equal L and high C side by side "vibrates" |
| Split-complementary (+150°/+210°) | Brand plus two accents (e.g. highlight + badge) | Lower C on one of them |
| Triadic (+120°/+240°) | Playful, kids, games | Pick one dominant, drop C on the other two |
| Tetradic (+90° steps or rectangle) | Illustration and data only | Too many competing hues for chrome |

- **Most UIs = one brand hue + tinted neutrals + one accent.** Semantic colors don't count toward the harmony; they're a fixed functional set.
- **60-30-10** (NN/g): about 60% dominant (neutral surfaces), 30% secondary (also relatively neutral, e.g. brand-tinted surfaces or dark sections), 10% accent (primary CTA, key highlights). If the brand color covers more than about 30% of a product UI, it stops signalling "clickable".
- Rotating hue keeps L and C, but not every hue reaches the same chroma at a given L (yellow at L 0.5 can't be vivid). After rotating, re-check gamut and contrast.
- NN/g's squint check: gray buttons can look disabled; a saturated non-CTA element steals the CTA's focus.

## Logo → palette method

Run steps 1–9 in order. The script automates extraction (2), contrast tests (4), scales (5), harmonies (6), neutrals (7), semantic colors (8), and dark tokens plus the report (9). Steps 1 and 3 need judgment.

1. **Get the cleanest source.** Best is brand guidelines with hex/Pantone, then SVG (read `fill`/`stop-color` values; they're exact), then transparent PNG, then a JPG or photo. Raster anti-aliasing creates fake in-between colors, so ignore pixels with alpha < 0.5 and clusters under ~2% area.
2. **Extract dominant colors.** Cluster in OKLab (k-means, k = 5–8). For each cluster report hex, OKLCH and % area, and split chromatic (C ≥ 0.04) from achromatic. Material's extractor works the same way: it quantizes, removes near-grays and rare colors, and scores by chroma (target ≈48 in HCT) and hue diversity.
3. **Pick the brand primary, the ink and the accent.** Score = area × chroma, so a small saturated mark beats a large gray wordmark. A dark, low-chroma logo color (navy/charcoal wordmark, OKLCH L < 0.40 and C < 0.10) is the **ink**: use it as the light-theme text color, not as an accent. The accent is the most chromatic remaining hue, even when it is a small dot (a 3% coral dot beats a 47% navy wordmark). The script prints a suggested role per extracted color; override with `--ink`, `--accent`. If two candidates score within ~20% of each other, or the brand team has a stated primary, ask the user. Record the exact hex as `--brand` and never alter it.
4. **Test the exact color for UI jobs:**

| Job | Pass condition | If it fails |
|---|---|---|
| Button fill + white text | ≥ 4.5:1 | Use a darker step (L ≤ 0.52) as `--primary`, keep the brand color for large brand moments |
| Button fill + dark text | ≥ 4.5:1 | Use it with near-black text (`--primary-foreground: var(--neutral-950)`) |
| Text/link on white bg | ≥ 4.5:1 | Links use the step at L ≤ 0.52 |
| Large display, icons, focus ring on bg | ≥ 3:1 | Use a darker step for rings/icons |
| On dark surface (L ≈ 0.17) | text ≥ 4.5:1 | Use a lighter step (L ≥ 0.70) |
| "Disliked" zone (Material: dark yellow-green, HCT hue 90–111, chroma > 16, tone < 65) | not in zone | Lighten to tone ≈70 for UI fills (keep the logo as is) |

5. **Derive the scale anchored on the exact brand color.** Put the brand at the step whose L target is nearest, generate the other steps around it, and keep the hue. Then assign roles: `--brand` (exact, for hero/illustration/large fills), `--primary` (button fill: the brand if it passes, else the nearest passing step), `--primary-hover/active` (±1–2 steps), `--link` (first step with ≥4.5:1 on bg), `--primary-subtle` (100–200).
   Worked example (actual `palette.py build --brand "#FF6A13"` output), a logo orange `#FF6A13` = `oklch(70.1% 0.200 44)`: white text 2.87:1 fails WCAG; black 7.32:1 passes WCAG but scores only APCA Lc 50 (white Lc 59). It pins to step 400. Scale: 50 `#fff4f0` · 100 `#ffe5da` · 200 `#ffcbb6` · 300 `#ffa681` · **400 `#ff6a13`** · 500 `#dd5800` (white 3.75, still fails) · **600 `#bc4900` (white 5.13:1, Lc −80)** · 700 `#9f3d00` · 800 `#853200` · 900 `#702900` · 950 `#441500`. When WCAG 2 and APCA disagree, pick a fill that passes both: the script sets `--primary` = 600 with white text, hover 700, `--link` = 600. Keep 400 for the logo, illustrations and large shapes. If the brand insists on the exact orange as a button, brand-400 with near-black text is WCAG-compliant (7.32:1) but weaker under APCA; say so to the user.
6. **Choose secondary/accent by harmony and personality.** Calm → analogous ±30–60°. Energetic CTA contrast → complementary or split. Strong single-color brand → no accent; use neutrals plus brand tints. Keep the accent's L/C in the same band as the primary, and keep it away from semantic hues (a red accent would read as "error").
7. **Tinted neutrals.** Use neutral hue = brand hue with C ≈ 0.005–0.02. Go lowest near white (≤0.006 at L > 0.95, so it doesn't look dirty) and highest in the mid/dark steps. Tailwind's tinted grays sit in the same range (mist and taupe ≤0.021, mauve ≤0.034, slate up to 0.046). For the orange brand (script default `--neutral-tint 0.015`): 50 `#fcf9f8` · 100 `#f7f3f1` · 200 `#eae4e1` · 300 `#dad2cf` · 400 `#aa9e99` · 500 `#7b716c` · 600 `#59504c` · 700 `#473e3a` · 800 `#2b2522` · 900 `#1b1613` · 950 `#0e0907`.
8. **Semantic colors harmonized to the brand.** Hue comes from convention; L and C come from the brand's working fill, so they look like one family. See next section.
9. **Dark-mode mapping, then verify.** Map tokens (see Dark mode), then run the contrast report on every text/bg, on-color/fill, border/bg and focus/bg pair in **both themes and all states**. Simulate protanopia, deuteranopia and tritanopia on charts and status UI. `python3 scripts/palette.py --help` shows the report and HTML-preview options.

## Logo special cases

| Case | Do this |
|---|---|
| **Multi-color logo** (3–5 hues) | Pick one as the UI primary (usually the most legible, or the one used in wordmark/app icon). Keep the others for illustration, category tags, onboarding art and data-viz. Never spread all of them across the chrome equally. A neutral UI plus colorful marks is the safest reading |
| **Black/white logo** | Color has to come from elsewhere: industry, competitors, mood board. Default to a monochrome UI with tinted neutrals and one accent chosen with the user. The logo stays black/white; tint neutrals toward the accent hue |
| **Neon / very saturated** (e.g. `#39FF14`: white text 1.36:1, black 15.5:1) | Keep the exact neon for large brand moments, preferably on dark surfaces. Derive UI fills with lower C and L. Never set neon text on white. On light themes use a darkened step for links/icons. Expect P3 vs sRGB differences |
| **Pastel / low-contrast brand** (e.g. `#7FD1C7`: white 1.77:1) | Use the pastel for surfaces, tints and illustration. Buttons and links use a deep step (L ≤ 0.52) of the same hue; dark text on the pastel itself is fine (11.9:1) |
| **Logo only available on a photo** | Ask for the vector. If impossible, crop to the mark, mask out the background, extract, and confirm the hex with the user. Never sample the photo's dominant colors as "brand" |
| **Gradient logo** | Use the two end colors as anchors. The UI primary is the more legible end, or the OKLCH midpoint. Reserve the gradient for hero, brand moments and the app icon, never behind body text |
| **Red brand** | Collides with danger. Make danger visually distinct (shift toward crimson/ruby, always add an icon and text) and don't use the brand red for destructive confirmations |
| **Green brand** | Collides with success. Move success toward teal/jade (H 165–175) or rely on icon + text |
| **Dark yellow / olive / brown brand** | It sits in Material's "disliked" zone. Use it as the brand mark; lighten to L ≈ 0.70 for UI fills, or pair with dark text |

## Semantic & state colors

- Hues by convention (Radix "Western" pairings): **danger** red/tomato/ruby/crimson (H ≈ 20–30), **warning** amber/yellow/orange (H ≈ 70–90), **success** green/teal/jade/grass (H ≈ 145–175), **info** blue/sky/cyan (H ≈ 230–250).
- Harmonize: set each semantic fill to the brand fill's L and C band. At L 0.55 / C 0.16 the computed fills are success `#02893D` (white 4.52:1), danger `#BD423A` (5.24), info `#0177BC` (4.81). Warning at L 0.55 turns ochre (`#986600`), so instead **use a light amber fill (L ≈ 0.80–0.88) with dark text**.
- Each semantic color needs: a solid fill, a subtle bg (step 100), a border (step 300) and a text step (L ≤ 0.50 on light). Pair every status with an icon.
- States in OKLCH, light theme: hover L −0.04…−0.06, pressed L −0.08…−0.10, selected bg = `color-mix(in oklch, var(--primary) 12–16%, var(--bg))`. Dark theme: hover L +0.04…+0.06.
- Disabled: neutral at reduced contrast (exempt from 1.4.3, but must still read as a control). Don't reuse the "secondary" style, or disabled and secondary become indistinguishable.
- Focus ring: ≥3:1 against adjacent colors (1.4.11), 2px+ outline with offset. Give it its own token so it can differ from the brand when the brand is low-contrast.
- Finance: up/down colors are cultural. Apple's Stocks app uses green = up in English and red = up in Chinese locales, so localize these tokens.

## Dark mode

Dark mode is a second token set, not an inversion. Apple: dark colors "aren't necessarily inversions"; the dark palette has "dimmer background colors and brighter foreground colors".

| Token | Light | Dark (OKLCH targets) |
|---|---|---|
| `--bg` | L 0.98–0.99, C ≤0.006 | **L 0.14–0.20**, brand-tinted C 0.005–0.015 (`#121212` = L 0.182) |
| `--surface` / raised / overlay | white or L 0.97 | **+0.03–0.05 L per elevation level** (e.g. 0.17 → 0.21 → 0.25 → 0.29) |
| `--border` | L 0.88–0.92 | L 0.30–0.36 |
| `--text` | L 0.20–0.25 | L 0.93–0.96 (not pure white) |
| `--text-muted` | L 0.50–0.55 | L 0.70–0.75 |
| `--primary` (fill) | brand step with ≥4.5:1 for its on-color | a lighter step (L 0.68–0.78) with **dark on-color**, chroma ×0.8–0.9 for large areas |

- Use near-black surfaces, not `#000`. Material's dark backgrounds are "dark grey instead of black, which increases visibility for shadows and also reduces eye strain for light text". Reserve pure black for explicit OLED "true black" modes and media viewers.
- Elevation reads through **lightness**, not shadows: shadows barely show on dark. Material replaced primary-tinted elevation overlays with tonal surface-container colors; Apple uses *base* (dimmer) and *elevated* (brighter) backgrounds for layered UI. Add 1px borders (L +0.08 over the surface) where surfaces meet.
- Desaturate: saturated brand colors vibrate and look neon on dark. Lower C by 10–25% for large fills, keep **hue identical** so the brand stays recognisable, and keep the exact brand color for the logo.
- Contrast: Apple asks for at least 4.5:1 and *strives for 7:1* for custom colors in small text. Test with Increase Contrast as well. Dim white-background images slightly so they don't glow.
- Worked dark tokens for the orange brand: bg `#130E0D` (L .17), surface `#1C1715` (.21), raised `#27201D` (.25), border `#3B3430` (.33), text `#F2EDEB` (16.5:1), muted `#ADA29E` (7.7:1), primary `#F97B40` (L .72, 7.2:1 vs bg; text on it = bg color).
- Implementation: `color-scheme: light dark`, tokens under `:root` plus `[data-theme="dark"]` and `@media (prefers-color-scheme: dark)`, or `light-dark()`. Respect the system setting; offer an override only as a convenience.

## Translucent and derived colours

Scrims, glows, tinted shadows and hover tints are tokens too: derive them from a token instead of writing raw `rgb(… / a)`.

```css
:root {
  --scrim:        oklch(from var(--neutral-950) l c h / 0.6);   /* keeps the tinted-neutral hue */
  --primary-glow: oklch(from var(--primary) l c h / 0.35);
  --accent-wash:  oklch(from var(--accent) calc(l + 0.1) c h / 0.12);
}
```

Prefer relative colour syntax (`oklch(from var(--x) l c h / a)`) for alpha. `color-mix(in oklch, <low-chroma colour> N%, transparent)` loses the hue: in Chrome (Oct 2026) `color-mix(in oklch, #fff8ee 80%, transparent)` computes to `oklch(0.98 0.015 none / 0.8)`, which renders with hue 0 and tints a cream header pink, while `oklch(from #fff8ee l c h / 0.8)` keeps hue 76.9. If you must use `color-mix` with `transparent`, mix `in srgb`.

## Gradients

- **Always state the interpolation space.** Gradients made only of legacy colors (hex/rgb/hsl) interpolate in sRGB for backward compatibility, and complementary pairs pass through gray. Blue→yellow midpoint: sRGB `#808080` (gray), `in oklab` `#6CABC7` (muted, C 0.08), `in oklch` `#08BAAE` (teal, keeps chroma). Use `in oklch` for vivid brand gradients, `in oklab` for subtle tonal ones, and `longer hue` for rainbows.
- Keep brand gradients within ~60° of hue (analogous) unless the brand is rainbow; keep both ends' L within ~0.15 so the gradient doesn't read as a lighting effect.
- Text over a gradient: WCAG tests the **least-contrasting area**. Put a scrim or solid surface behind body text.

```css
.hero   { background: linear-gradient(135deg in oklch, oklch(0.62 0.19 265), oklch(0.70 0.17 320)); }
.ribbon { background: linear-gradient(to right in oklch longer hue, oklch(0.75 0.15 0), oklch(0.75 0.15 0)); }
/* Mesh / aurora: layered radial gradients over a dark base, blurred and grained */
.aurora {
  position: relative; isolation: isolate;
  background:
    radial-gradient(60% 50% at 20% 25% in oklch, oklch(0.72 0.19 300 / .55), transparent 70%),
    radial-gradient(50% 60% at 80% 30% in oklch, oklch(0.80 0.13 200 / .50), transparent 70%),
    radial-gradient(70% 55% at 50% 100% in oklch, oklch(0.70 0.20 350 / .45), transparent 70%),
    oklch(0.16 0.03 285);
}
.aurora::after { content: ""; position: absolute; inset: 0; z-index: -1; opacity: .08; pointer-events: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160'%3E%3Cfilter id='n'%3E%3CfeTurbulence baseFrequency='.9'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E"); }
/* Animate hue with a registered property (Chrome 85, Firefox 128, Safari 16.4) */
@property --h { syntax: "<number>"; inherits: false; initial-value: 300; }
.glow { background: radial-gradient(circle in oklch, oklch(0.75 0.18 var(--h)), transparent 65%); animation: hue 12s linear infinite; }
@keyframes hue { to { --h: 660; } }
@media (prefers-reduced-motion: reduce) { .glow { animation: none; } }
```

- Gradient interpolation support: Chrome 111, Firefox 127, Safari 16.2. The grain overlay hides banding on large smooth gradients. For motion pacing see `motion.md`; for glass/aurora styles see `styles-catalog.md`.

## Data-viz color

Full method and a validated palette: use the **`dataviz` skill**. The rules that touch the brand palette:

- **Categorical**: ≤6–8 hues, distinct in hue *and* lightness. Use brand colors for the first one or two series, then a CVD-safe set. Okabe–Ito: `#E69F00` `#56B4E9` `#009E73` `#F0E442` `#0072B2` `#D55E00` `#CC79A7` `#000000`.
- **Sequential**: one hue, L from ≈0.95 (low) to ≈0.35 (high), chroma peaking mid-ramp. Light = less on light backgrounds.
- **Diverging**: two hues with equal L at the ends and a neutral midpoint at the meaningful zero. Avoid red/green; use blue/orange or purple/green.
- Color vision deficiency: about **1 in 12 men** (NEI). Okabe & Ito put red-green deficiency at ~8% of Caucasian, 5% of Asian and 4% of African males. Add direct labels, shapes or patterns; chart lines and slices need 3:1 against neighbours (1.4.11).
- Don't reuse semantic colors as categories (red series = "bad"), and don't reuse the CTA color in charts.

## Meaning: industry & culture

Treat color psychology as **convention, not science**. Elliot (2015) calls the research field "nascent" and advises caution in applying findings. Labrecque & Milne (2012) found that hue, saturation and value shift perceived brand personality, but effects depend on context. NN/g: assume interpretation varies by culture and validate with your users. Differentiation from competitors usually matters more than "what blue means".

| Domain | Common convention | Caveat / fresher move |
|---|---|---|
| Finance, insurance | Deep blue, navy, green; low chroma, high contrast | Blue is saturated in fintech; teal, deep green or ink-black differentiate |
| Health, care | Teal, blue, soft green; warm accent for humanity | Avoid alarm-red as brand; clinical white needs warm neutrals |
| Food, delivery | Red, orange, yellow, appetizing warm hues | Appetite claims are weakly evidenced; photos carry the color |
| Sustainability | Greens, earth, sand | Generic; use one unexpected accent (ochre, clay, sky) |
| Luxury, fashion | Black, ivory, gold, very low chroma | Restraint plus typography carries it (see `typography-layout.md`) |
| Tech, SaaS, AI | Blue/violet, dark UIs, gradients | Very crowded; distinct hue + neutral system stands out |
| Kids, education, games | High-chroma triadic | Keep the chrome neutral so content stays legible |
| Wellness, beauty | Sage, blush, lilac, muted pastels | Pastels fail as text/buttons; derive deep steps |

Cross-cultural facts to respect:
- Apple HIG: red signals danger in some cultures and positive things in others. In Chinese markets **red = up/gain**.
- White and black both carry mourning connotations in parts of Asia. Use them as neutrals, but avoid monochrome "funeral" compositions for celebratory moments.

**Thailand (ประเทศไทย)**:
- **Day colors** are widely known: Sun red, Mon yellow, Tue pink, Wed green (night grey), Thu orange, Fri light blue, Sat purple. Birthday/merit-making and personal "lucky color" features can use them.
- **Yellow** is strongly associated with the monarchy (Rama IX and Rama X were born on a Monday; their royal flags are yellow). Royal blue and purple flags follow other royals' birth days. Fine as a UI color, but treat royal-themed content with deference and never parody it.
- **Flag**: red = land and people (nation), white = religion, blue = monarchy (adopted 1917).
- **Mourning** = black, also white. During national mourning (e.g. 2016) brands switched to black/white/grey and muted palettes, so have a monochrome theme ready.
- **Never render a person's name in red.** Writing names in red ink is associated with death and bad luck (Chinese-rooted belief, still widespread). Error states on name fields: red border and icon, but keep the entered name text neutral.
- Red and yellow have also carried political connotations (red-shirt/yellow-shirt movements). Avoid pitting them against each other as "two sides" in civic or political UI.

## Example palettes

Light themes unless marked. All pairs computed: text/bg ≥ 13:1, muted/bg ≥ 4.5:1, and the primary-foreground (label) color shown with its ratio. The accent column shows which text works on the accent fill, or its role (link).

| Mood | Background | Text | Muted text | Primary (label color, ratio) | Accent (text on it) |
|---|---|---|---|---|---|
| Trust / fintech | `#F8FAFD` oklch(98.4% .005 258) | `#131B29` oklch(22.2% .030 261) | `#647080` | `#1E59CD` oklch(50% .190 262) (white 6.2) | `#F5AE39` oklch(80% .150 75) (dark 9.0) |
| Calm care / health | `#F6FBFB` oklch(98.4% .005 197) | `#0E262A` oklch(25.1% .031 210) | `#5E7374` | `#047879` oklch(51.9% .088 196) (white 5.3) | `#EA856B` oklch(72.1% .130 35) (dark 6.1) |
| Eco / natural | `#F9F7EE` oklch(97.5% .012 96) | `#17261A` oklch(25.1% .030 150) | `#696F5B` | `#1F6F3D` oklch(48.1% .110 152) (white 6.2) | `#CE9042` oklch(70% .120 70) (dark 5.8) |
| Luxury / premium | `#F9F6F1` oklch(97.4% .007 81) | `#15110D` oklch(18.1% .010 67) | `#6F6860` | `#1F1915` oklch(21.9% .012 56) (white 17.4) | `#C69E58` oklch(72.1% .100 80) (dark 7.5) |
| Playful / consumer | `#FBF9FF` oklch(98.5% .008 301) | `#221838` oklch(24% .060 296) | `#736C8C` | `#7838DB` oklch(52% .230 295) (white 6.2) | `#FBD530` oklch(88% .170 95) (dark 11.7) |
| Energetic / food & sport | `#FEF9F5` oklch(98.5% .008 61) | `#231814` oklch(22.2% .019 41) | `#78645B` | `#C93200` oklch(55% .193 35) (white 5.3) | `#B5E544` oklch(85.9% .190 125) (dark 11.8) |
| Editorial / news | `#FAF6EF` oklch(97.4% .010 82) | `#171613` oklch(20% .006 92) | `#66635D` | `#B7191C` oklch(50% .190 27) (white 6.6) | `#305880` oklch(45% .080 250) (link, 6.9 on bg) |
| Warm hospitality / café | `#FBF4EA` oklch(97% .015 77) | `#302017` oklch(26.1% .030 50) | `#776559` | `#AE5528` oklch(55.1% .130 45) (white 5.1) | `#677A44` oklch(55.1% .081 125) (white 4.7) |
| Wellness / spa | `#F4F8F3` oklch(97.5% .008 139) | `#202C25` oklch(27.9% .021 159) | `#646F66` | `#476E54` oklch(50.1% .061 154) (white 5.8) | `#BCA2D0` oklch(75% .071 310) (dark 6.4) |
| Enterprise / B2B | `#FBFCFD` oklch(99.1% .002 248) | `#15191D` oklch(21.1% .010 248) | `#666C75` | `#0E5CAF` oklch(48% .150 255) (white 6.6) | `#01BA87` oklch(69.9% .147 165) (dark 7.0) |
| Thai heritage / craft (lacquer & gold) | `#FAF5EA` oklch(97.1% .015 86) | `#271512` oklch(22% .030 30) | `#735E56` | `#A9231E` oklch(48% .171 28) (white 7.1) | `#D4AB4F` oklch(76.1% .120 85) (dark 8.1) |
| Dev tool (**dark**) | `#0D0F14` oklch(16.9% .011 268) | `#E4E8EF` oklch(93% .010 262) | `#989FAB` (7.2) | `#4ADD8C` oklch(80% .170 155) (bg-dark text 12.0) | `#2BBDF5` oklch(75% .140 230) (8.9 on bg) |
| AI / futuristic (**dark**) | `#0A0917` oklch(15% .030 286) | `#EDEDF8` oklch(94.9% .015 286) | `#A1A2BD` (7.9) | `#A37AFE` oklch(67.9% .189 295) (dark text 6.8; white needs `#7E4ED7`, 5.3) | `#34DDE5` oklch(82% .130 200) (11.9 on bg) |

Generate the full scales, neutrals, semantic set and dark tokens from any of these primaries with the script.

## Tools

| Tool | Use it for |
|---|---|
| oklch.com | Pick/convert OKLCH, see sRGB vs P3 gamut edges |
| Radix custom palette (radix-ui.com/colors/custom) | 12-step light+dark scales from accent + gray + background |
| uicolors.app | Tailwind 50–950 scales previewed on components |
| Leonardo (leonardocolor.io) | Contrast-ratio-targeted scales and themes |
| Realtime Colors | Preview text/bg/primary/secondary/accent + fonts on a real page, light/dark; export CSS/SCSS/Tailwind |
| Huemint | ML palette generation for brand/website/graphics |
| Coolors | Fast exploration, lock and shuffle |
| Khroma | AI that learns your preferred combinations |
| Adobe Color | Harmony wheel, extract from image, accessibility tools |
| Huetone | Oklab-based scale building with contrast checks |
| APCA calculator, WebAIM checker | Contrast checks (APCA and WCAG 2) |
| ColorBrewer | Sequential/diverging map palettes |

## Pitfalls

| Symptom | Cause | Fix |
|---|---|---|
| A translucent cream/neutral surface turns pinkish | `color-mix(in oklch, <low-chroma colour>, transparent)` makes the hue `none`, rendered as hue 0 | `oklch(from var(--x) l c h / a)`, or `color-mix(in srgb, …)` |
| Gradient has a muddy gray middle | sRGB interpolation of legacy colors | `linear-gradient(in oklch, …)` |
| Hover state shifts hue or gets chalky | Lightening in HSL or by mixing white in sRGB | Change OKLCH `l` only (`oklch(from … calc(l - .05) c h)`) |
| Brand button barely passes with either white or black text | Fill sits near the crossover (L ≈ 0.53–0.64), where the best possible is √21 ≈ 4.58:1 | Move the fill to L ≤ 0.52 (white text) or ≥ 0.65 (dark text); keep the exact brand for non-text use |
| Passes WCAG but looks hard to read (white on orange/teal) | WCAG 2 luminance math misjudges mid-tone warm colors | Check APCA too; choose a fill that passes both |
| Same token looks different on two screens; hue shifts in the vivid range | Out-of-gamut OKLCH clipped by the browser | sRGB-safe base value, P3 boost in `@media (color-gamut: p3)`; lint with stylelint-gamut |
| Neutrals look dirty, green or purple | Tint chroma too high near white, or hue in the olive zone | C ≤ 0.006 for L > 0.95; tint toward brand hue only |
| Dark mode looks neon and vibrates | Light-theme brand chroma reused on dark | Lighter step, C ×0.8–0.9, same hue |
| Dark cards disappear | Shadows used for elevation on dark | +0.03–0.05 L per level, 1px border |
| Extracted "brand colors" include odd browns/grays | Anti-aliasing and JPEG artifacts | Use SVG fills; drop alpha < 0.5 and clusters < 2% |
| `contrast-color()` flips text abruptly in animations/themes | It returns only black or white | Use it for static fills; set explicit on-colors for brand fills |
| Relative-color hue math ignored in older Safari | Old drafts required `deg` | `@supports` with a `deg` variant |
| Theming breaks in one component | Component used a raw step (`--brand-600`) | Components read semantic tokens only |

## Sources

- OKLCH in CSS (Evil Martians) — https://evilmartians.com/chronicles/oklch-in-css-why-quit-rgb-hsl
- MDN relative colors — https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_colors/Relative_colors
- MDN color-mix() — https://developer.mozilla.org/en-US/docs/Web/CSS/color_value/color-mix
- MDN color-interpolation-method — https://developer.mozilla.org/en-US/docs/Web/CSS/color-interpolation-method
- MDN browser-compat-data — https://github.com/mdn/browser-compat-data
- contrast-color() article (Smashing, May 2026) — https://smashingmagazine.com/2026/05/building-self-correcting-color-systems-contrast-color
- Tailwind CSS colors — https://tailwindcss.com/docs/colors ; v4.3 post (v4.2 neutrals) — https://tailwindcss.com/blog/tailwindcss-v4-3 ; theme.css — https://raw.githubusercontent.com/tailwindlabs/tailwindcss/main/packages/tailwindcss/theme.css
- Radix: understanding the scale — https://www.radix-ui.com/colors/docs/palette-composition/understanding-the-scale ; composing a palette — https://www.radix-ui.com/colors/docs/palette-composition/composing-a-palette ; custom — https://www.radix-ui.com/colors/custom
- Material Color Utilities (HCT, contrast, extraction, scheme variants, DislikeAnalyzer) — https://github.com/material-foundation/material-color-utilities
- Material Components Android, dark theme — https://github.com/material-components/material-components-android/blob/master/docs/theming/Dark.md
- Adobe Leonardo — https://github.com/adobe/leonardo
- WCAG 2.2 Understanding 1.4.3 — https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html ; 1.4.11 — https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html
- APCA in a Nutshell — https://git.apcacontrast.com/documentation/APCA_in_a_Nutshell
- WCAG3 contrast as of April 2026 (Roselli) — https://adrianroselli.com/2026/04/wcag3-contrast-as-of-april-2026.html
- Apple HIG Dark Mode — https://developer.apple.com/design/human-interface-guidelines/dark-mode ; Color — https://developer.apple.com/design/human-interface-guidelines/color
- NN/g color — https://www.nngroup.com/articles/color-enhance-design/ ; visual hierarchy — https://www.nngroup.com/articles/visual-hierarchy-ux-definition/
- Elliot 2015, Frontiers in Psychology — https://www.frontiersin.org/articles/10.3389/fpsyg.2015.00368/full
- Labrecque & Milne 2012 — https://colab.ws/articles/10.1007%2Fs11747-010-0245-y
- NEI color blindness — https://www.nei.nih.gov/learn-about-eye-health/eye-conditions-and-diseases/color-blindness ; Okabe & Ito, Color Universal Design — https://jfly.uni-koeln.de/color/
- Thai day colors — https://www.thethailandlife.com/color-day-thailand ; Flag of Thailand — https://en.wikipedia.org/wiki/Flag_of_Thailand ; red-ink belief (Thairath) — https://en.thairath.co.th/horoscope/belief/2947636 ; (USC Folklore Archive) — https://folklore.usc.edu/never-write-a-name-in-red-ink/ ; mourning guidance — https://www.thailandstarterkit.com/moving/what-to-do-during-the-mourning-period-in-thailand/
- Tools: https://oklch.com · https://www.realtimecolors.com · https://huemint.com · https://coolors.co · https://leonardocolor.io · https://uicolors.app · https://www.khroma.co · https://color.adobe.com · https://huetone.ardov.me · https://apcacontrast.com · https://webaim.org/resources/contrastchecker/ · https://colorbrewer2.org
