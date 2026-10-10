# Design systems and design tokens

> Read when: starting a product's visual foundation, creating or refactoring tokens / theming (light-dark, multi-brand, density), choosing a component library, writing a component spec, syncing Figma variables with code, auditing an inconsistent UI, or setting up design-system docs, versioning and handoff.

**Contents:** 1 Scope · 2 Token architecture · 3 Naming · 4 DTCG format 2025.10 · 5 Token pipeline · 6 Figma variables → code · 7 Multi-brand and modes · 8 Foundation scales · 9 Component spec and states · 10 Iconography · 11 Component libraries 2026 · 12 Reference systems · 13 Bootstrap a minimal system · 14 Audit an existing UI · 15 Docs, versioning, governance, handoff · Pitfalls · Sources

Templates: `templates/tokens-starter.css` (complete token set, light/dark, brand, density) and `templates/tailwind-theme.css` (Tailwind v4 mapping). Color theory and palette generation: `color.md`. Type scale choice: `typography-layout.md`. Motion usage: `motion.md`. Contrast rules: `accessibility.md`.

## 1. Scope

| Part | What it contains | Minimum viable version |
|---|---|---|
| Tokens | Named design decisions: color, type, space, radius, elevation, motion, z-index | One CSS file + DTCG JSON (if multi-platform) |
| Components | Coded, accessible building blocks with variants, sizes, states | 12-15 components (§13) |
| Patterns | Multi-component solutions: forms + validation, empty/loading/error, navigation, tables | 4-6 documented patterns |
| Content guidelines | Voice, casing, labels, error-message formula, date/number formats | One page |
| Governance | Ownership, contribution path, versioning, deprecation | CODEOWNERS + semver + changelog |

Build tokens first, then components, then patterns. A team of 1-3 shipping one product needs tokens + a themed off-the-shelf library, not a bespoke component library. Bespoke components pay off when 2+ products or platforms share them.

## 2. Token architecture

Three tiers; each tier references only the tier below.

| Tier | Purpose | Example | Who changes it |
|---|---|---|---|
| Primitive (global, base, "option") | Raw palette and scales, no meaning | `--brand-600`, `--space-4`, `--radius-md` | Brand/foundation work only |
| Semantic (alias, "decision") | Role in the UI; the theming seam | `--primary`, `--text-muted`, `--surface-raised`, `--danger-subtle` | Theme and brand modes remap these |
| Component | One component's deviation or override hook | `--control-height-md`, `--card-padding` | Component owners |

Rules:
- Components consume semantic (or component) tokens only. A primitive in component code = lint error.
- Name semantics by role, never by value: `--danger`, not `--red`; `--surface-raised`, not `--white`.
- Every fill token gets a `-foreground` partner that passes 4.5:1 on it (`--primary` / `--primary-foreground`).
- A theme remaps semantic → primitive; semantic names stay identical across light, dark and brands (Carbon: "tokens stay the same across themes, only values change").
- Add a component token only when the component deviates from the semantic default or needs a public override; keep them under ~15% of the set (heuristic).
- Mint a new token when a value encodes a decision reused in 3+ places; one-offs stay local.
- Theme-dependent component tokens belong on the component selector (`.btn { --btn-bg: var(--primary) }`), not on `:root`, or scoped themes freeze (see Pitfalls).

## 3. Naming

Order: `[namespace]-[category]-[concept/property]-[variant]-[state]`, dropping empty parts.
Examples: `color-bg-primary-hover`, `space-inset-md`, `ds-color-text-danger`. Nathan Curtis's taxonomy names the parts namespace (system/theme/domain) · object (component/element) · base (category, concept, property) · modifier (variant, state, scale, mode); his example `$color-action-text-secondary-focus`. Style Dictionary's CTI (category/type/item) is the same idea, optional in v4+.

| Scale kind | Convention | Example |
|---|---|---|
| Color ramps | 50-950 by lightness (Tailwind-style) | `--brand-50` … `--brand-950` |
| Spacing | number = multiples of 4px | `--space-4` = 16px |
| Sizes with few steps | t-shirt | `--radius-sm/md/lg/xl`, `--shadow-xs…xl` |
| States | `hover, active (pressed), focus, disabled, selected, checked, invalid, readonly` | `--primary-hover` |
| Emphasis | `subtle < default < strong` (or `bold`) | `--border`, `--border-strong` |

- CSS: kebab-case custom properties. DTCG JSON: nested groups (`color.primary.hover`), aliases `{color.brand.600}`. Generated per platform: JS `colorPrimaryHover`, Android `color_primary_hover`, Swift `colorPrimaryHover`.
- Prefix a namespace (`--ds-`, Salesforce `--slds-g-`) when tokens ship to apps you do not control or share a page with third-party CSS.
- Atlassian pattern for semantic color: foundation + property + modifiers, e.g. `color.text`, `color.icon.success`.

## 4. DTCG format 2025.10

Status (verified 2026-10-10): the W3C Design Tokens Community Group published the **first stable version, 2025.10, on 2025-10-28**. It is a Community Group report, not on the W3C Standards Track; the FAQ calls it safe to use while refinement continues. Three modules: **Format**, **Color**, **Resolver** (themes/modes). Named implementers: Style Dictionary, Tokens Studio, Terrazzo (reference implementations), plus Figma, Penpot, Sketch, Framer, Knapsack, Supernova, zeroheight.

Format essentials:
- Files `.tokens` or `.tokens.json`; media type `application/design-tokens+json`.
- A token is any object with `$value`. Groups are plain objects. `$type` may sit on a group and is inherited; tools must not infer type from value.
- Reserved: `$description`, `$deprecated` (bool or reason string), `$extensions` (vendor data, reverse-domain keys, preserved by tools), `$root` (a group's own base token, referenced `{color.primary.$root}`), `$extends` (inherit a group).
- Aliases: `"{group.token}"` (whole value) or `{ "$ref": "#/color/brand/600/$value/components/0" }` (JSON Pointer into sub-values).
- Types: `color, dimension, fontFamily, fontWeight, duration, cubicBezier, number` + composites `strokeStyle, border, transition, shadow, gradient, typography`.
- `dimension` = `{ "value": 16, "unit": "px" | "rem" }`; `duration` = `{ "value": 100, "unit": "ms" | "s" }`; color = `{ "colorSpace", "components", "alpha"?, "hex"? }` with spaces incl. `srgb, display-p3, oklch, oklab, lab, lch, hsl, hwb, rec2020` (+ `none` components).

```json
{
  "color": {
    "$type": "color",
    "brand": {
      "600": { "$value": { "colorSpace": "oklch", "components": [0.54, 0.16, 265], "hex": "#4068ca" } }
    },
    "neutral": { "0": { "$value": { "colorSpace": "srgb", "components": [1, 1, 1], "hex": "#ffffff" } } },
    "primary": {
      "$root": { "$value": "{color.brand.600}", "$description": "Main action fill" },
      "foreground": { "$value": "{color.neutral.0}" }
    },
    "link": { "$value": "{color.brand.600}", "$deprecated": "Use color.primary" }
  },
  "space": { "$type": "dimension", "4": { "$value": { "value": 16, "unit": "px" } } },
  "duration": { "$type": "duration", "fast": { "$value": { "value": 100, "unit": "ms" } } },
  "easing": { "$type": "cubicBezier", "standard": { "$value": [0.2, 0, 0, 1] } },
  "shadow": {
    "popover": { "$type": "shadow", "$value": [{
      "color": { "colorSpace": "srgb", "components": [0, 0, 0], "alpha": 0.08 },
      "offsetX": { "value": 0, "unit": "px" }, "offsetY": { "value": 4, "unit": "px" },
      "blur": { "value": 12, "unit": "px" }, "spread": { "value": 0, "unit": "px" } }] }
  },
  "button": { "padding-x": { "$type": "dimension", "$value": "{space.4}",
    "$extensions": { "com.example.figma": { "scopes": ["GAP"] } } } }
}
```

Resolver module (`.resolver.json`, `"version": "2025.10"`): `sets` (always applied), `modifiers` (pick one context per input, e.g. `{ "theme": "dark" }`), `resolutionOrder` (later wins). Context values are arrays of sources (inline tokens or `$ref`); file refs are optional for tools, same-document refs are mandatory.

```json
{
  "version": "2025.10",
  "sets": { "foundation": { "sources": [{ "$ref": "./primitives.tokens.json" }] } },
  "modifiers": {
    "theme": { "default": "light", "contexts": {
      "light": [{ "$ref": "./theme-light.tokens.json" }],
      "dark":  [{ "$ref": "./theme-dark.tokens.json" }] } },
    "brand": { "default": "acme", "contexts": {
      "acme":  [{ "$ref": "./brand-acme.tokens.json" }],
      "ocean": [{ "$ref": "./brand-ocean.tokens.json" }] } }
  },
  "resolutionOrder": [{ "$ref": "#/sets/foundation" }, { "$ref": "#/modifiers/brand" }, { "$ref": "#/modifiers/theme" }]
}
```

## 5. Token pipeline

Source of truth: DTCG JSON in git (multi-platform) or the CSS file itself (web-only, one app). Flow: Figma variables ⇄ JSON (Tokens Studio sync or Figma native export/import) → PR review → Style Dictionary / Terrazzo build → CSS vars + Tailwind theme + Swift/Kotlin/Flutter constants → published package.

| Tool (2026-10) | Role | Notes |
|---|---|---|
| Style Dictionary 5.x (5.6.0) | Build JSON → any platform | v5.0.0 2025-05-16; Node ≥ 22; DTCG auto-detected; refs must target tokens, not groups |
| Tokens Studio + `@tokens-studio/sd-transforms` 2.x | Figma plugin, git sync, themes (Pro) | sd-transforms 2.x peer-requires Style Dictionary ^5; `preprocessors: ['tokens-studio']` |
| Terrazzo (`@terrazzo/cli` 2.7) | DTCG-native CLI with CSS/Tailwind plugins | Reference implementation of 2025.10 |
| Figma native | Export one mode or all modes to JSON; import requires DTCG JSON | Right-click collection → Export modes; only tokens present in every imported file become variables |

Style Dictionary 5 recipe for 2025.10 tokens (tested with 5.6.0). The stock `css` group turns OKLCH into hex and prints DTCG `duration` objects as `[object Object]` (`time/seconds` only matches `$type: "time"`); this fixes both:

```js
// build.mjs — node build.mjs
import StyleDictionary from 'style-dictionary';
StyleDictionary.registerTransform({
  name: 'duration/css', type: 'value',
  filter: (t) => t.$type === 'duration',
  transform: (t) => (typeof t.$value === 'object' ? `${t.$value.value}${t.$value.unit}` : t.$value),
});
const transforms = StyleDictionary.hooks.transformGroups.css
  .filter((n) => n !== 'color/css').concat(['color/oklch', 'duration/css']);
await new StyleDictionary({
  source: ['tokens/**/*.tokens.json'],
  platforms: { css: { transforms, buildPath: 'build/', files: [
    { destination: 'tokens.css', format: 'css/variables', options: { outputReferences: true } }] } },
}).buildAllPlatforms();
```

Output keeps aliases (`--color-primary-foreground: var(--color-neutral-0);`). Note `$root` tokens come out as `--color-primary-root`; rename in a name transform if you want `--color-primary`.

## 6. Figma variables → code

| Figma | Code | Rule |
|---|---|---|
| Collection "Primitives" (1 mode, hidden from publishing) | primitive tier | Designers pick only from semantic collections |
| Collection "Theme" with modes Light / Dark | semantic tier; CSS `:root` / `[data-theme="dark"]`; resolver `theme` modifier | Same variable names in every mode |
| Collection "Brand" modes or extended collections | `[data-brand]`; resolver `brand` modifier | Extended collections are Enterprise-only (plugin API) |
| Collection "Density" (Compact / Default / Comfortable) or "Breakpoint" (Mobile / Desktop) | `[data-density]`; media/container queries | Number variables for heights, padding, type sizes |
| Variable alias | `var(--x)` / `{x}` | Never hard-code a hex in a semantic variable |
| Variable scopes | which property pickers show the variable | Scope fills vs strokes vs gap so designers cannot misuse |
| Code syntax (Web / iOS / Android) | what Dev Mode prints | Set Web syntax to `var(--primary)` so handoff shows the real token |

Modes inherit from the parent frame (Auto). Mode count per collection depends on plan; forum reports Pro 10, Org 20, Enterprise 40 (not in official docs; verify in the file). Figma types are color/number/string/boolean: typography and shadow composites live in Styles (or Tokens Studio), not variables.

## 7. Multi-brand and modes

Strategies, cheapest first:
1. **Hue swap**: brands differ only in brand/accent hue + chroma; ramps are generated (`tokens-starter.css` §1: change `--brand-h`, `--brand-c`). Same contrast everywhere because lightness per step is fixed.
2. **Semantic remap per brand**: brand file overrides 5-20 semantic tokens (primary, accent, radius, font-display).
3. **Full brand primitives + shared semantic layer**: each brand ships its own palette, type and radius primitives; semantic names identical.
4. **Brand × theme matrix** via the DTCG resolver (`brand` and `theme` modifiers) or Figma extended collections.

Rules: semantic and component names never vary by brand; test every brand × theme × density combination for contrast (n × m runs, automate it); keep brand switching on `<html>` (derived CSS vars are computed where declared, see Pitfalls). Ant Design's model is a good mental template: seed tokens (`colorPrimary`, `borderRadius`) → algorithm → map tokens → alias tokens, with `darkAlgorithm` and `compactAlgorithm` composable.

Modes worth supporting: light/dark (always), high contrast (`@media (prefers-contrast: more)` → stronger borders and text), density (compact for data-heavy pro tools), reduced motion (durations → 0). Alternative to duplicated dark blocks: `light-dark()` in each token plus `color-scheme` (Chrome 123, Firefox 120, Safari 17.5); keep the duplicated blocks when older Safari matters.

## 8. Foundation scales

**Spacing** (4px base): 0, 2, 4, 6, 8, 12, 16, 20, 24, 32, 40, 48, 64, 80, 96, 128. Inner padding ≤ gap between siblings ≤ gap between groups (proximity). Controls pad 8-16 px; cards 16-32; page sections 48-96 desktop, 32-64 mobile.

**Radius**: 0, 2, 4, 8, 12, 16, 24, full. Pick one "personality" (sharp 0-4, soft 6-12, round 16+) and apply it to control radius; cards one step larger. **Nested radius rule: outer = inner + padding.** Inner children of a rounded container:
```css
.card { --r: var(--radius-xl); --pad: var(--space-2); border-radius: var(--r); padding: var(--pad); }
.card > .media { border-radius: max(0px, calc(var(--r) - var(--pad))); } /* 16 - 8 = 8px */
```
When padding ≥ outer radius, the inner corner becomes square; pick a smaller padding or larger outer radius instead of keeping equal radii (equal radii look pinched).

Material 3 shape scale (dp): extra-small 4, small 8, medium 12, large 16, large-increased 20, extra-large 28, extra-large-increased 32, extra-extra-large 48, full (extra-extra-large is annotated as an M3 Expressive API).

**Elevation**

| Level | Use | Token (starter) | M3 level (dp) |
|---|---|---|---|
| 0 | page, flat cards, table | none + `--border` | 0 |
| 1 | resting card, raised button | `--elevation-card` (`--shadow-xs`) | 1 |
| 2 | hover lift, sticky header, scrolled app bar | `--elevation-raised` | 3 |
| 3 | menu, popover, combobox list | `--elevation-popover` | 6 |
| 4 | dialog, drawer, sheet | `--elevation-dialog` | 8 |
| 5 | toast, drag preview | `--elevation-toast` | 12 |

Shadows: two layers (tight contact + soft ambient), neutral-tinted, alpha ≤ 0.16 in light mode. In dark mode shadows barely read: raise surface lightness per level (`--surface` → `--surface-raised`), as M3 does with surface-container tones (`surfaceContainerLowest … Highest`).

**Z-index**: named layers with gaps; never raw numbers in components.

| Token | Value | Token | Value |
|---|---|---|---|
| `--z-base` | 0 | `--z-overlay` | 1300 |
| `--z-raised` | 1 | `--z-modal` | 1400 |
| `--z-dropdown` | 1000 | `--z-popover` | 1500 (above modal: popovers open from dialogs) |
| `--z-sticky` | 1100 | `--z-toast` | 1600 |
| `--z-header` | 1200 | `--z-tooltip` | 1700 |

`<dialog>.showModal()` (Safari 15.4+) and the Popover API (`popover` attribute; Chrome 114, Firefox 125, Safari 17, iOS Safari 18.3) render in the top layer, above every z-index; prefer them over z-index wars.

**Motion tokens** (details and usage in `motion.md`): durations 100 (hover/press), 200 (small UI), 300 (menus, accordions), 500 ms (large surfaces); Material 3 curves standard `cubic-bezier(0.2, 0, 0, 1)`, standard-decelerate `(0, 0, 0, 1)`, standard-accelerate `(0.3, 0, 1, 1)`, emphasized-decelerate `(0.05, 0.7, 0.1, 1)`, emphasized-accelerate `(0.3, 0, 0.8, 0.15)`; M3 duration tokens run 50-1000 ms in 50/100 ms steps. Reduced motion: zero durations or swap movement for opacity.

**Density**: control heights sm/md/lg = 32/40/48 px default; compact 28/32/40 (tables, pro tools); comfortable/touch 44/56. Touch targets ≥ 44 px (Apple), 48 dp (Material); WCAG 2.2 AA floor 24 px.

## 9. Component spec and states

Spec template (one page per component):
1. **Purpose** and when not to use it (point to the alternative).
2. **Anatomy**: numbered parts (container, label, leading icon, trailing icon, indicator) with the token each uses.
3. **Variants** by emphasis: primary (one per view) · secondary · tertiary/ghost · destructive · link.
4. **Sizes**: sm/md/lg → height, padding-x, font size, icon size (16/16/20), gap.
5. **States** (matrix below) for every variant.
6. **Behaviour**: keyboard map, focus management, ARIA pattern (APG name), touch target.
7. **Content**: label rules (verb first, ≤ 3 words, sentence case), truncation, room for text expansion (German, Finnish) and scripts without word spaces (Thai). In flex/inline-flex components (buttons, chips, list rows with icons) wrap the label in **one** element — `<button><svg/><span>จองคิว<span class="nw">วันนี้</span></span></button>` — because every bare text run and span inside a flex container becomes its own flex item and Thai words wrap out of order (`typography-layout.md`).
8. **Density / responsive** behaviour; RTL mirroring.
9. **Accessibility acceptance**: contrast numbers, name/role/state, axe clean.
10. **Tokens table** and **Do / Don't** with images.

| State | Trigger | Visual | Implementation |
|---|---|---|---|
| default | — | base tokens | — |
| hover | pointer over | state layer 8% of content color | wrap in `@media (hover: hover)` so touch does not stick |
| focus-visible | keyboard focus | 2 px ring, 2 px offset, ≥ 3:1 vs adjacent colors | `:focus-visible`; never remove outline without replacement |
| active / pressed | pointer down, Enter/Space | state layer 10%; optional scale 0.98 | `:active`; toggle buttons expose `aria-pressed` |
| disabled | not available | 50% opacity, or M3: content 38%, container 10%; no hover | `disabled` attr; use `aria-disabled="true"` when it must stay focusable to explain why |
| loading | async action running | spinner replaces/precedes label, width locked | `aria-busy="true"`, block double submit, keep focus |
| error / invalid | validation failed | `--danger` border + icon + message text (never color alone) | `aria-invalid="true"` + `aria-describedby` → message |
| selected / checked | chosen item | filled/tonal bg, check icon, bold label | `aria-selected` (options/tabs), `aria-checked`, `aria-current="page"` (nav) |
| read-only | viewable, not editable | no border emphasis, normal text color, copyable | `readonly` attr (stays focusable, submitted) — not `disabled` |
| dragged | being moved | state layer 16% + `--elevation-toast` | announce via live region |

**State layers** (Material 3, androidx tokens v0_210): hover 0.08, focus 0.10, pressed 0.10, dragged 0.16, overlaid in the content (`on-*`) color. One rule set works for every variant (verified in Chrome):
```css
.btn { position: relative; isolation: isolate; }
.btn::before { content: ""; position: absolute; inset: 0; z-index: -1; border-radius: inherit;
  background: currentColor; opacity: 0; pointer-events: none;
  transition: opacity var(--duration-fast) var(--ease-standard); }
@media (hover: hover) { .btn:hover::before { opacity: var(--state-hover); } }
.btn:focus-visible { outline: var(--focus-ring-width) solid var(--focus-ring); outline-offset: var(--focus-ring-offset); }
.btn:focus-visible::before { opacity: var(--state-focus); }
.btn:active::before { opacity: var(--state-pressed); }
```

## 10. Iconography

| Set (2026-10) | Size / grid | Styles | Pick when |
|---|---|---|---|
| Lucide (`lucide-react` 1.x) | 24 grid, 2 px stroke, round caps/joins, ≥ 1 px padding | outline; ~1,900 icons | Default for shadcn/Tailwind products; `absoluteStrokeWidth` keeps 2 px at any size |
| Phosphor | designed at 16 × 16 | 6 weights: thin, light, regular, bold, fill, duotone | Need weight-matching to type, or duotone illustrations |
| Tabler | 24 grid, 2 px stroke | 6,238 icons (5,184 outline, 1,054 filled) | Largest free outline set; admin/data tools |
| Material Symbols | variable font: `opsz` 20-48, `wght` 100-700, `FILL` 0-1, `GRAD` -50..200 | Outlined, Rounded, Sharp | Android/M3 products; animate fill on selection |
| SF Symbols | 9 weights, 3 scales, 4 rendering modes; > 7,000 symbols | monochrome, hierarchical, palette, multicolor | Apple platforms only; aligns with San Francisco text automatically |

Rules: one family per product; sizes 16 (dense UI, inline with 12-14 px text), 20 (default with 14-16 px text), 24 (navigation, touch); stroke weight visually matches the text weight beside it; outline for rest, filled for selected/active (tab bars); center icons optically, not mathematically (play triangles shift right, circles draw slightly larger); align with text via flex `align-items: center` and a gap of 4-8 px; icon-only buttons need an accessible name and a 44 px target; decorative icons get `aria-hidden="true"`.

## 11. Component libraries 2026

Web (versions from npm, 2026-10-10):

| Library | Kind | Pick when |
|---|---|---|
| shadcn/ui (CLI 4.x) | Copy-in components, Tailwind v4, OKLCH CSS vars; base = Base UI (default since Jul 2026), Radix (`-b radix`) or React Aria (`--base aria`) | You own the code and the look; most new React/Next apps |
| Base UI (`@base-ui/react` 1.9; 1.0 Dec 2025) | Unstyled primitives from the Radix, Floating UI and MUI teams | Building your own styled system on React; combobox/autocomplete-heavy UIs |
| Radix Primitives (`radix-ui` 1.7, WorkOS) | Unstyled primitives, unified package | Existing Radix/shadcn codebases; not deprecated |
| React Aria Components (1.22, Adobe) | Unstyled, hooks + components, strongest i18n/a11y (dates, RTL, touch) | Accessibility-critical, international, date/number-heavy apps |
| Ark UI (5.x, Chakra team) | Headless, 45+ components, React/Solid/Vue/Svelte | Multi-framework or non-React design systems |
| Headless UI (2.2, Tailwind Labs) | Small unstyled set, React/Vue | A few accessible widgets in a Tailwind site |
| MUI Material UI (v9, Apr 2026) | Styled, huge catalog, MUI X grids/pickers | Enterprise/admin, data grid, fast delivery over brand distinctness |
| Mantine (v9, Mar 2026) | Styled, 120+ components, 70+ hooks, native CSS (no runtime) | Internal tools and dashboards with batteries included |
| Chakra UI v3 | Styled, built on Ark UI (+ Emotion runtime), recipes/tokens | Prop-styling teams already on Chakra |
| HeroUI v3 (Mar 2026) | Styled, React Aria + Tailwind v4, no Framer Motion | Polished Tailwind look with React Aria a11y |
| Park UI | Styled Ark UI recipes for Panda/Tailwind | Ark UI users wanting defaults (slow release cadence: preset last published 2024-11) |

Mobile and native:

| Option | Pick when |
|---|---|
| NativeWind (4.2 stable on Tailwind v3; v5 = Tailwind v4, still `rc`) | RN team sharing Tailwind vocabulary with web |
| gluestack-ui v5 (Jun 2026) | Copy-in RN components on Tailwind v4 via NativeWind v5 or Uniwind (Expo-only); dropped Next.js |
| Tamagui (v2 May 2026; 3.0.0 published 2026-10-10) | One codebase RN + web with an optimizing compiler and typed themes |
| React Native Paper 5.x | Material Design 3 look on RN, Android-first |
| Flutter Material 3 / Cupertino | Flutter: `ThemeData(colorScheme: ColorScheme.fromSeed(seedColor: …))`; Cupertino widgets for iOS-faithful screens |
| SwiftUI | System components + semantic colors (`.primary`, `.secondary`, asset-catalog colors with Any/Dark), Dynamic Type text styles; see `platform-mobile.md` |
| Jetpack Compose Material 3 | `MaterialTheme(colorScheme, typography, shapes)`; map tokens to `ColorScheme` roles (`primary`, `onPrimary`, `surfaceContainer*`) |

Selection rule: product-brand-led consumer app → shadcn (Base UI) or own system on Base UI/React Aria; enterprise CRUD → MUI or Mantine; a11y/i18n-critical → React Aria; multi-framework → Ark UI. Whatever you pick, map its theme to your semantic tokens instead of editing component styles one by one. shadcn's `--accent` is a neutral hover surface, not a brand accent: map your accent to a different name.

## 12. Reference systems

| System | Best to learn | URL |
|---|---|---|
| Material 3 | Color roles, state layers, shape/elevation/motion token tables, Expressive | https://m3.material.io/ |
| Apple HIG | Platform conventions, SF Symbols, Dynamic Type, Liquid Glass materials | https://developer.apple.com/design/human-interface-guidelines/ |
| Fluent 2 | Two-tier global → alias tokens across Windows/web/iOS/Android | https://fluent2.microsoft.design/design-tokens |
| IBM Carbon | Theme switching (White, Gray 10/90/100) with constant names; layer tokens | https://carbondesignsystem.com/ |
| Shopify Polaris | Content and merchant-UX guidance; React lib deprecated for Polaris Web Components (Oct 2025) | https://shopify.dev/docs/api/polaris |
| Atlassian | Semantic color naming (foundation.property.modifier), tokens migration | https://atlassian.design/foundations/tokens/design-tokens |
| GitHub Primer | Base vs functional tokens; 9 themes incl. colorblind/tritanopia/high-contrast | https://primer.style/product/primitives/ |
| Adobe Spectrum (S2) | Platform-organised docs, React Spectrum S2 + React Aria | https://spectrum.adobe.com/ |
| Salesforce SLDS 2 | Global styling hooks (`--slds-g-*`) as public theming API, dark mode via hooks | https://www.lightningdesignsystem.com/ |
| GOV.UK | Research-backed patterns ("Ask users for…", "Help users to…"), plain content, public contribution backlog | https://design-system.service.gov.uk/ |
| Ant Design (v6) | Seed → map → alias token algorithms, dense enterprise components | https://ant.design/ |
| Uber Base | Cross-platform system; Base Web React implementation | https://base.uber.com/ |

## 13. Bootstrap a minimal design system

1. **Inputs.** Brand hue(s), typeface, product type (consumer / pro tool), platforms. Done when: written in `docs/design-system.md`.
2. **Tokens.** Copy `templates/tokens-starter.css`; set `--brand-h/-c`, `--accent-h/-c`, fonts; keep `--brand-c` within the per-hue limit in the file header. With a logo or exact brand hex, run `scripts/palette.py build` instead and let its `tokens.css` replace the template's color section: its ramps are anchored on the exact brand color (the template's are generated from hue + chroma) and its semantic color names match the template's. Done when: contrast check passes for light and dark, screenshots of both reviewed.
3. **Library + mapping.** Choose per §11; map its theme to semantic tokens (`templates/tailwind-theme.css` for Tailwind v4). Done when: no raw hex/px in app code; `bg-red-500`-style defaults removed.
4. **Guardrails.** Lint raw values (`stylelint-declaration-strict-value` for color/z-index/shadow; CI grep for Tailwind arbitrary values `-[`). Done when: CI fails on a planted raw hex.
5. **Core components (12-15):** Button, IconButton, Link, TextField/Textarea, Select/Combobox, Checkbox, Radio, Switch, Dialog, Menu/Popover, Tooltip, Toast, Tabs, Card, Badge. Done when: each has every state of §9 in Storybook, keyboard walkthrough passes, axe reports 0 violations.
6. **Patterns:** form layout + validation, empty/loading/error states, page shell/navigation, data table. Done when: one real screen per pattern built only from system parts.
7. **Docs.** Storybook (or zeroheight/Supernova) with foundations, components, patterns, content guide. Done when: a new dev can build a form screen without asking.
8. **Design parity.** Figma variables mirror token names with Web code syntax; Code Connect on core components. Done when: Dev Mode shows `var(--primary)` and real component snippets.
9. **Release.** `0.1.0`, changelog, owners. Done when: one product consumes the package from a registry.

## 14. Audit an existing UI

Count distinct raw values; every cluster becomes a token or gets deleted. Script (sh/bash/zsh, tested):
```sh
# sh audit.sh [dir] — distinct raw values per category (more distinct = more drift)
D="${1:-src}"
g() { grep -rhoEI --include='*.css' --include='*.scss' --include='*.less' --include='*.ts' \
  --include='*.tsx' --include='*.js' --include='*.jsx' --include='*.vue' --include='*.svelte' \
  --include='*.html' --exclude-dir=node_modules --exclude-dir=dist --exclude-dir=build \
  --exclude-dir=.next "$@" "$D"; }
val() { sed -E 's/^[^:]*:[[:space:]]*//; s/[[:space:]]+$//'; }
count() { sort | uniq -c | sort -rn; }
echo "== colors";        g -i -e '#([0-9a-f]{8}|[0-9a-f]{6}|[0-9a-f]{3,4})\b|(rgb|hsl)a?\([^)]*\)|okl(ch|ab)\([^)]*\)' | tr 'A-F' 'a-f' | count
echo "== font-size";     g -e '(font-size|fontSize)"?:[[:space:]]*[^;,}"]+' | val | count
echo "== font-weight";   g -e '(font-weight|fontWeight)"?:[[:space:]]*[^;,}"]+' | val | count
echo "== line-height";   g -e '(line-height|lineHeight)"?:[[:space:]]*[^;,}"]+' | val | count
echo "== border-radius"; g -e '(border-radius|borderRadius)"?:[[:space:]]*[^;,}"]+' | val | count
echo "== box-shadow";    g -e '(box-shadow|boxShadow)"?:[[:space:]]*[^;}"]+' | val | count
echo "== z-index";       g -e '(z-index|zIndex)"?:[[:space:]]*-?[0-9]+' | val | count
echo "== px off the 4px grid"; g -e '[0-9]+px' | sed 's/px$//' | awk '$1 % 4 != 0 && $1 > 2 {print $1 "px"}' | count
echo "== Tailwind arbitrary values"; g -e '[a-z-]+-\[[^]]+\]' | count
```
Then:
1. Merge perceptual duplicates: colors closer than ΔEOK 0.02 (one JND per CSS Color 4) are the same color (`#333`, `#333333`, `rgb(51,51,51)`). Group with `culori`'s `differenceEuclidean('oklab')` (ignores alpha) or paste the CSS into Project Wallace's CSS Design Tokens Analyzer (https://www.projectwallace.com/design-tokens) or CSS Stats (https://cssstats.com/) for a live URL.
2. Targets after cleanup (heuristic): ≤ 10 font sizes, ≤ 4 weights, ≤ 6 radii, ≤ 6 shadows, z-index only from the named scale, spacing on the 4 px grid, 0 arbitrary values outside one-off art.
3. Map each surviving cluster to a semantic token; replace with a codemod (sed/ast-grep) per category in separate commits; screenshot-diff key screens.
4. Lock it: lint rule + the script in CI with a budget (fail if a count grows).

## 15. Docs, versioning, governance, handoff

Docs structure: Getting started (install, theming, tokens package) · Foundations (color, type, space, radius, elevation, motion, icons, with token tables generated from source) · Components (one page each: spec §9, live examples, props table, a11y notes, do/don't) · Patterns · Content guidelines · Changelog + migration guides · Contribution guide. Generate token tables from the build output, never by hand.

Versioning (semver on the package):
- **Major**: remove/rename a token or prop, change a token's meaning, drop a component, raise peer deps. Ship codemods + a migration guide.
- **Minor**: new tokens/components/variants, new optional props; visual tweaks within the same meaning.
- **Patch**: bug fixes, a11y fixes that do not change API.
- Deprecate before removing: mark `$deprecated` (DTCG) / `@deprecated` (TS), keep the old token as an alias for ≥ 1 minor release, log usage, remove in the next major. Salesforce's rule: keep old and new hooks side by side until both are tested.

Governance: name an owner team (or rotating owners for small orgs) with CODEOWNERS on tokens and components; contributions start as an issue/discussion with evidence of need (GOV.UK model: community backlog, evidence of user need, yearly prioritisation); decide "core vs local": a component used by one product stays in that product until a second consumer appears. Review checklist per PR: tokens only, all states, keyboard, contrast, docs page, changelog entry.

Handoff:
- **Figma Dev Mode**: mark frames "Ready for dev"; variables with Web code syntax print token names instead of hex; annotate interactions and states.
- **Code Connect** (Dev or Full seat, Organization/Enterprise): maps Figma components to repo components so Dev Mode and the Figma MCP server show real usage. Set up via Code Connect UI (GitHub link, one design component → many implementations) or CLI with template files (`Button.figma.ts`). 2.0.0 (2026-08-18) ended framework parsers: migrate with `figma connect migrate`, publish with `figma connect publish`.
- Developers implement from tokens and components; if a design uses a value with no token, raise it before coding.

## Pitfalls

| Symptom | Cause | Fix |
|---|---|---|
| A `[data-theme="dark"]` section shows dark text on dark background | `color` inherits as an already-computed value from the light parent | Re-declare `color: var(--text); background-color: var(--bg)` on every theme scope (the starter does) |
| Child with `data-brand` or new `--brand-h` keeps the old brand color | Custom properties resolve `var()` where declared, then inherit fixed values; ramps declared on `:root` do not recompute | Switch brand on `<html>`, or re-declare the derived ramp + semantic tokens on the scoped selector |
| Component tokens on `:root` ignore a scoped dark section | `:root { --btn-bg: var(--primary) }` froze the light value | Declare theme-dependent component tokens on the component selector |
| Shadows look identical in scoped dark | Shadow tokens built from `--shadow-color` on `:root` only | Declare shadow tokens on `:root, [data-theme]` (starter does) |
| Tailwind output contains `--radius-md: var(--radius-md)`; tokens break when loaded inside a layer before `theme` | `@theme inline` re-emits same-name mappings as self-references | Use `@theme inline reference` (emits nothing, utilities still point at the token; tested 4.3.3) |
| `[object Object]` or hex instead of OKLCH in Style Dictionary output | 2025.10 `duration` objects unsupported by `time/seconds`; `color/css` converts to hex | Custom `duration/css` transform + `color/oklch` (§5) |
| Ramp steps look different on sRGB vs P3 screens, or two steps look identical | OKLCH chroma beyond sRGB: P3 screens show it, sRGB screens gamut-map it | Keep `--brand-c` under the per-hue limit in the starter header (yellow ~0.11, cyan ~0.09) |
| Hover style sticks after tap on phones | `:hover` applies on touch | Wrap hover in `@media (hover: hover)` |
| Disabled button can't explain itself | `disabled` removes it from focus order and tooltips | `aria-disabled="true"` + prevent action, or show the reason inline |
| Dialog under a sticky header | z-index arms race | Native `<dialog>`/popover top layer; named z scale for the rest |
| Tokens Studio → Figma variables silently skip tokens | Variables reject multi-value tokens, "AUTO", %, > 5,000 per collection | Keep composites in Styles; split collections |

## Sources

- Design Tokens spec first stable version (W3C CG blog, 2025-10-28) — https://www.w3.org/community/design-tokens/2025/10/28/design-tokens-specification-reaches-first-stable-version/
- designtokens.org (home, FAQ) — https://www.designtokens.org/ · https://www.designtokens.org/faq/
- DTCG Format 2025.10 — https://www.designtokens.org/TR/2025.10/format/
- DTCG Color 2025.10 — https://www.designtokens.org/TR/2025.10/color/
- DTCG Resolver 2025.10 — https://www.designtokens.org/TR/2025.10/resolver/
- Style Dictionary v5 migration — https://styledictionary.com/versions/v5/migration/
- Style Dictionary config / tokens — https://styledictionary.com/reference/config/ · https://styledictionary.com/info/tokens/
- Tokens Studio sd-transforms — https://github.com/tokens-studio/sd-transforms · https://docs.tokens.studio/transform-tokens/style-dictionary
- Terrazzo — https://terrazzo.app/
- Figma: Modes for variables — https://help.figma.com/hc/en-us/articles/15343816063383
- Figma plugin API VariableCollection (extended collections) — https://developers.figma.com/docs/plugins/api/VariableCollection
- Figma Code Connect docs and changelog — https://developers.figma.com/docs/code-connect · https://github.com/figma/code-connect/blob/main/CHANGELOG.md
- Figma Dev Mode — https://www.figma.com/dev-mode/
- Tailwind CSS theme variables / dark mode — https://tailwindcss.com/docs/theme · https://tailwindcss.com/docs/dark-mode
- shadcn/ui theming and changelog — https://ui.shadcn.com/docs/theming · https://ui.shadcn.com/docs/changelog/2026-07-base-ui-default · https://ui.shadcn.com/docs/changelog/2026-07-react-aria
- Base UI — https://base-ui.com/ · Radix Primitives — https://www.radix-ui.com/primitives · Ark UI — https://ark-ui.com/
- React Aria — https://react-aria.adobe.com/ · Headless UI — https://headlessui.com/
- MUI v9 — https://mui.com/blog/introducing-mui-v9/ · Mantine — https://mantine.dev/ · Chakra UI — https://chakra-ui.com/
- HeroUI v3 release — https://heroui.com/docs/react/releases/v3-0-0 · Park UI — https://park-ui.com/
- NativeWind — https://www.nativewind.dev/ · gluestack-ui v5 — https://gluestack.io/blogs/gluestack-ui-v5-stable-release
- Tamagui v2 — https://tamagui.dev/blog/version-two · React Native Paper — https://callstack.github.io/react-native-paper/
- Flutter Material — https://docs.flutter.dev/ui/design/material · Compose Material 3 — https://developer.android.com/develop/ui/compose/designsystems/material3
- androidx Material 3 token sources (StateTokens, ElevationTokens, ShapeTokens, MotionTokens) — https://github.com/androidx/androidx/tree/androidx-main/compose/material3/material3/src/commonMain/kotlin/androidx/compose/material3/tokens
- Material 3 — https://m3.material.io/ · Apple HIG — https://developer.apple.com/design/human-interface-guidelines/
- Fluent 2 design tokens — https://fluent2.microsoft.design/design-tokens
- Carbon themes — https://www.carbondesignsystem.com/building-blocks/foundations/themes/overview
- Polaris — https://shopify.dev/docs/api/polaris · Atlassian tokens — https://atlassian.design/foundations/tokens/design-tokens
- Primer primitives — https://primer.style/product/primitives/ · Spectrum — https://spectrum.adobe.com/
- SLDS 2 styling hooks (Trailhead) — https://trailhead.salesforce.com/content/learn/modules/salesforce-lightning-design-system-2-for-developers/explore-salesforce-lightning-design-system-2
- GOV.UK patterns and contribution — https://design-system.service.gov.uk/patterns/ · https://design-system.service.gov.uk/community/propose-a-component-or-pattern/
- Ant Design theme customisation — https://ant.design/docs/react/customize-theme · Uber Base — https://base.uber.com/ · https://baseweb.design/
- Nathan Curtis, Naming Tokens in Design Systems — https://nathanacurtis.substack.com/p/naming-tokens-in-design-systems-9e86c7444676
- Lucide design principles — https://lucide.dev/contribute/icon-design-guide · Tabler Icons — https://github.com/tabler/tabler-icons
- Phosphor — https://github.com/phosphor-icons/homepage · Material Symbols — https://developers.google.com/fonts/docs/material_symbols · SF Symbols — https://developer.apple.com/sf-symbols/
- CSS Color 4 (gamut mapping, JND 0.02) — https://www.w3.org/TR/css-color-4/
- Project Wallace tokens analyzer — https://www.projectwallace.com/design-tokens · CSS Stats — https://cssstats.com/
- stylelint-declaration-strict-value — https://github.com/AndyOGo/stylelint-declaration-strict-value
