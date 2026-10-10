# Design systems & design tokens: raw research notes

Collected 2026-10-10 for `skills/design-atlas/references/design-systems.md` and the templates
`skills/design-atlas/templates/tokens-starter.css` + `tailwind-theme.css`.
Each bullet carries its source. "npm" = `npm view <pkg> version/time` run on 2026-10-10.

## DTCG (W3C Design Tokens Community Group) format

- First stable version **2025.10**, announced **2025-10-28** on the W3C community blog.
  Features named: theming/multi-brand without file duplication, Display P3 + OKLCH + all CSS Color 4 spaces,
  aliases/inheritance/component-level references, one source -> iOS/Android/web/Flutter.
  Reference implementations named: Style Dictionary, Tokens Studio, Terrazzo. Supporting/implementing: Penpot,
  Figma, Sketch, Framer, Knapsack, Supernova, zeroheight ("10+ tools").
  https://www.w3.org/community/design-tokens/2025/10/28/design-tokens-specification-reaches-first-stable-version/
- designtokens.org: "First stable version 2025.10 now available". FAQ: "first stable version 1, aka v2025.10",
  safe to use, still in active development, **not on the W3C Standards Track** (Community Group report).
  https://www.designtokens.org/ · https://www.designtokens.org/faq/
- Spec = 3 modules: Format https://www.designtokens.org/TR/2025.10/format/ ,
  Color https://www.designtokens.org/TR/2025.10/color/ , Resolver https://www.designtokens.org/TR/2025.10/resolver/
- Format module facts (read from the spec page):
  - File extension `.tokens` (preferred) or `.tokens.json`; media type `application/design-tokens+json` SHOULD,
    `application/json` MAY; tools MUST support both.
  - Reserved props: `$value` (object with `$value` = token), `$type` (on token or group; tools MUST NOT infer type
    from value), `$description`, `$extensions` (vendor data, reverse-domain keys, tools MUST preserve unknown),
    `$deprecated` (true/false/string), `$root` (group's base token, referenced `{group.$root}`), `$extends`
    (group inheritance, deep merge, sugar for JSON-Schema `$ref`, MUST NOT reference a token),
    `$ref` (JSON Pointer RFC 6901, e.g. `"#/colors/blue/$value"`, can reach sub-values like `/components/0`).
  - Curly-brace alias `{group.token}` resolves to the whole `$value`.
  - Type resolution order: token `$type` -> referenced token's type -> nearest parent group `$type`; else invalid.
  - Types: primitive `color, dimension, fontFamily, fontWeight, duration, cubicBezier, number`;
    composite `strokeStyle, border, transition, shadow, gradient, typography`.
  - `dimension` = `{ "value": number, "unit": "px" | "rem" }` (unit required even for 0).
  - `duration` = `{ "value": number, "unit": "ms" | "s" }`.
  - `cubicBezier` = `[P1x, P1y, P2x, P2y]`, x in [0,1].
  - `fontWeight` = 1..1000 or aliases thin/hairline 100 ... black/heavy 900, extra-black/ultra-black 950.
  - `fontFamily` = string or array.
  - shadow example fields: color, offsetX, offsetY, blur, spread (array allowed for layered). `inset` not confirmed
    from the part of the page read.
  - border = color + width + style; transition = duration + delay + timingFunction.
- Color module: colorSpace ids `srgb, srgb-linear, hsl, hwb, lab, lch, oklab, oklch, display-p3, a98-rgb,
  prophoto-rgb, rec2020, xyz-d65, xyz-d50`. Value `{ colorSpace, components[], alpha?, hex? }`; `none` allowed as
  a component; `hex` optional fallback, MUST be 6-digit; alpha omitted = 1. Spec example:
  `{"colorSpace":"oklch","components":[0.7016,0.3225,328.363],"alpha":1,"hex":"#ff00ff"}`.
- Resolver module 2025.10: "Final Community Group Report", stable. Problem: contexts (light/dark, brand, density,
  a11y) cause combinatorial explosion. File `.resolver.json`, `application/json`. Root: `name?`, `version`
  (must be "2025.10"), `description?`, `sets`, `modifiers`, `resolutionOrder` (required), `$schema?`.
  Sets have `sources` (inline tokens or `{ "$ref": "#/sets/X" }`), later sources override.
  Modifiers have `contexts` map + optional `default`. Input example `{ "theme": "dark" }`.
  Resolution: input validation -> ordering -> alias resolution -> final.

## Style Dictionary / Tokens Studio / Terrazzo

- Style Dictionary v5 migration: "drop-in replacement for the majority of users"; refactor for performance on large
  sets with many references. Breaking: references must point to token nodes (no group/sub-property refs);
  reference syntax customisation removed (DTCG `{a.b}` fixed). **Node >= 22** (uses Set.prototype.union).
  https://styledictionary.com/versions/v5/migration/
- npm: style-dictionary 4.0.0 = 2024-06-28, 5.0.0 = 2025-05-16, latest 5.6.0 (2026-10-03); engines node >=22.
- Config: `usesDtcg` usually unnecessary, auto-detected; minimal config `source`, `platforms.css.transformGroup`,
  `buildPath` (trailing slash), `files[{destination, format:"css/variables", options:{outputReferences:true}}]`.
  https://styledictionary.com/reference/config/
- Tokens page: DTCG ($value/$type/$description) vs legacy (value/type/comment) cannot be mixed in one instance;
  Category/Type/Item (CTI) optional; `attribute/cti` transform. https://styledictionary.com/info/tokens/
- **Hands-on test (style-dictionary 5.6.0, this session)** with DTCG 2025.10 tokens:
  - `css` transformGroup = `attribute/cti name/kebab time/seconds html/icon size/rem color/css asset/url
    fontFamily/css cubicBezier/css strokeStyle/css/shorthand border/css/shorthand typography/css/shorthand
    transition/css/shorthand shadow/css/shorthand`.
  - `color/css` turned an oklch color object into **hex** (`#4068ca`); swapping in built-in `color/oklch` emits
    `oklch(0.5400 0.1600 265.00)`.
  - DTCG `duration` object `{value:100,unit:"ms"}` was emitted as **`[object Object]`**: built-in `time/seconds`
    filters `$type === 'time'` only (checked in lib/common/transforms.js). Fixed with a 6-line custom
    `duration/css` transform.
  - `$root` token emitted as `--color-primary-root` (name keeps "root").
  - dimension object `{value:4,unit:"px"}` -> `4px` (fine); shadow composite -> `0px 4px 12px 0px rgb(0% 0% 0% / 0.08)`.
  - `$deprecated` produced no output marker.
  - Available color transforms include `color/oklch color/oklab color/p3 color/lch color/ColorSwiftUI
    color/composeColor color/hex8flutter`.
- @tokens-studio/sd-transforms 2.0.3 peerDependency `style-dictionary ^5.0.0` (npm). README usage:
  `register(StyleDictionary)`, `preprocessors: ['tokens-studio']` (explicit since 0.16.0),
  `transformGroup: 'tokens-studio'`, `permutateThemes()` reads `$themes.json`. https://github.com/tokens-studio/sd-transforms
- Tokens Studio docs: plugin output needs sd-transforms; adds unofficial "text" type for Figma string variables;
  Themes (Pro) export to Figma Styles + Variables; variables export skips incompatible types, multi-value tokens,
  "AUTO", % values, >5000 variables per collection; sync to GitHub/GitLab/Bitbucket/Azure DevOps; multi-file.
  https://docs.tokens.studio/transform-tokens/style-dictionary (and search-result snippets of docs.tokens.studio)
- Terrazzo: "tools for token management and code generation", MIT. npm @terrazzo/cli 2.7.1 — "CLI for managing design
  tokens using the DTCG standard and generating code for any platform via plugins"; @terrazzo/plugin-css and
  @terrazzo/plugin-tailwind exist (2.7.1). https://terrazzo.app/
- zeroheight moved its tokens manager to Style Dictionary v5 with 2025.10 as base format (zeroheight help, via search).

## Figma Variables, modes, Dev Mode, Code Connect

- Help "Modes for variables": modes on Education/Professional/Organization/Enterprise; count per collection depends
  on plan; modes can be set on layers, frames, components, sections, groups, pages; default Auto = inherit parent;
  **export a mode or all modes ("Export modes") to JSON; import requires DTCG-format JSON**; import creates a
  variable only for tokens present in every imported file with supported, consistent type.
  https://help.figma.com/hc/en-us/articles/15343816063383
- Mode counts per plan (forum, not official docs): pinned reply says Pro 10, Org 20; Enterprise 40 historically.
  (unverified officially) https://forum.figma.com/suggest-a-feature-11/launched-all-plans-should-offer-more-than-4-variable-modes-13979/index17.html
- Extended collections (multi-brand): Enterprise-only per plugin API docs (`extend` throws "Cannot create extended
  collections outside of enterprise plan"). https://developers.figma.com/docs/plugins/api/VariableCollection
- Schema 2025 previewed native DTCG import/export + extended collections (forum thread summary via search).
- Code Connect docs: links repo components to Figma components so Dev Mode shows real snippets; also feeds the Figma
  MCP server. Two setups: CLI and Code Connect UI (in Figma, GitHub integration, one-to-many mappings). Template files
  (`Button.figma.ts`) recommended; framework parsers (React/RN, HTML/Web Components/Angular/Vue, SwiftUI, Compose)
  labelled legacy. Seat: Dev or Full seat on Organization/Enterprise. https://developers.figma.com/docs/code-connect
- Code Connect CHANGELOG: 1.5.0 (2026-07-29) parsers unsupported from 2026-08-17; templates can import local helpers;
  `migrate --delete`; `preview --inspect/--props/--all`. 2.0.0 (2026-08-18): parsers only usable by
  `figma connect migrate` / `unpublish`; stay on `@figma/code-connect@1` if needed. `publish --force`, `--file`.
  https://github.com/figma/code-connect/blob/main/CHANGELOG.md · npm @figma/code-connect 2.0.1.
- Figma report claims 98 min/week/dev saved with Code Connect (vendor, single org). https://www.figma.com/reports/bridging-design-and-code/ (seen in search only)

## Tailwind CSS v4 theme

- `@theme` namespaces -> utilities: `--color-* --font-* --text-* --font-weight-* --tracking-* --leading-*
  --tab-size-* --breakpoint-* --container-* --spacing-* --radius-* --shadow-* --inset-shadow-* --drop-shadow-*
  --blur-* --perspective-* --zoom-* --aspect-* --ease-* --animate-*`. No z-index or duration namespace.
  `@theme inline` for vars referencing vars; `--color-*: initial` resets a namespace, `--*: initial` all;
  `@theme static` emits all vars. https://tailwindcss.com/docs/theme
- Dark variant: `@custom-variant dark (&:where(.dark, .dark *));` or `(&:where([data-theme=dark], [data-theme=dark] *))`.
  https://tailwindcss.com/docs/dark-mode
- npm tailwindcss: 4.0.0 2025-01-21, 4.1.0 2025-04-01, 4.2.0 2026-02-18, 4.3.0 2026-05-08, latest 4.3.3.
- **Hands-on (tailwindcss 4.3.3)**: `@theme inline { --radius-md: var(--radius-md) }` emits the self-reference
  `--radius-md: var(--radius-md)` into `@layer theme` (works only because unlayered tokens win the cascade).
  `@theme inline reference { ... }` emits no variables; utilities still point at the token var
  (`.rounded-md{border-radius:var(--radius-md)}`, `.p-6{padding:calc(var(--space-1) * 6)}`). Block-form
  `@custom-variant dark { @media (...) { &:where(...) { @slot; } } &:where(...) { @slot; } }` compiles.
  `z-(--z-modal)` and `duration-(--duration-fast)` compile. After `--color-*: initial` etc., `bg-red-500`,
  `shadow-2xl`, `rounded-3xl`, `text-6xl` are no longer generated.

## shadcn/ui

- Theming vars: background/foreground, card, popover, primary, secondary, muted, accent (+ -foreground pairs),
  destructive, border, input, ring, chart-1..5, sidebar-*, radius; OKLCH values; `.dark` class;
  `@custom-variant dark (&:is(.dark *));` `@theme inline { --color-background: var(--background); }`.
  shadcn "accent" = subtle hover surface, not a brand accent. https://ui.shadcn.com/docs/theming
- Changelog headlines: Feb 2025 Tailwind v4; Jun 2025 radix-ui migration; Aug 2025 CLI 3.0 + MCP server;
  Dec 2025 `npx shadcn create`; Jan 2026 Base UI docs, RTL; Feb 2026 unified Radix package, blocks for Radix & Base UI;
  Mar 2026 CLI v4; Apr 2026 `shadcn apply`, presets; May 2026 `shadcn eject`; Jul 2026 **Base UI as the default**,
  **React Aria** base; Aug 2026 private GitHub registries. https://ui.shadcn.com/docs/changelog
- Base UI default (Jul 2026): `npx shadcn init` picks Base UI; keep Radix with `-b radix`; Radix not deprecated;
  reason: Base UI stable (1.6.0, 6M+ weekly downloads); migration via skill `pnpm dlx skills add shadcn/ui`.
  https://ui.shadcn.com/docs/changelog/2026-07-base-ui-default
- React Aria base: `pnpm dlx shadcn@latest init --base aria`; works with all eight styles.
  https://ui.shadcn.com/docs/changelog/2026-07-react-aria

## Component library landscape (npm versions 2026-10-10)

| package | latest | notes |
|---|---|---|
| shadcn (CLI) | 4.21.4 | 3.0.0 2025-08-27, 4.0.0 2026-03-06 |
| radix-ui | 1.7.0 | "A project by WorkOS"; "Unstyled, accessible, open source React primitives" https://www.radix-ui.com/primitives |
| @radix-ui/themes | 3.3.0 (2026-01-31) | |
| @base-ui/react | 1.9.0 | 1.0.0 = 2025-12-11; "From the creators of Radix, Floating UI, and Material UI"; unstyled https://base-ui.com/ ; old name @base-ui-components/react deprecated |
| react-aria-components | 1.22.1 | site moved to react-aria.adobe.com |
| @ark-ui/react | 5.39.3 | "headless library with 45+ accessible components", React/Solid/Vue/Svelte https://ark-ui.com/ |
| @headlessui/react | 2.2.10 (2026-04-13) | Tailwind Labs |
| @mui/material | 9.5.0 | v7 2025-03-26, v9 2026-04-07 (no v8; MUI X aligned majors); v9: a11y, sx perf, NumberField, Menubar; Chrome 117/Safari 17 targets https://mui.com/blog/introducing-mui-v9/ (search summary) |
| @mantine/core | 9.7.1 | v8 2025-05-05, v9 2026-03-31 |
| @chakra-ui/react | 3.37.0 | v3 2024-10-22 |
| @heroui/react | 3.2.6 | v3 stable 2026-03-21; React Aria Components + Tailwind v4 + CSS vars; no Framer Motion dep; Text renamed Typography https://heroui.com/docs/react/releases/v3-0-0 (search summary) |
| @park-ui/panda-preset | 0.43.1 (last publish 2024-11-22) | Ark UI + Panda/Tailwind; repo last push Apr 2026 (third-party tracker) |
| nativewind | 4.2.7 | v5 still `5.0.0-rc.0` on rc/preview tags; v4 targets Tailwind v3 |
| tamagui | 3.0.0 (published 2026-10-10) | 2.0.0 2026-05-23; v2 needs React 19+, RN 0.81+ New Arch (search summary of tamagui.dev upgrade guide) |
| @gluestack-ui/core | 5.0.15 | gluestack-ui v5 stable 2026-06-25: Tailwind v4, NativeWind v5 or Uniwind; dropped Next.js support (search summary of gluestack.io blog) |
| react-native-paper | 5.15.3 | Material Design 3 |
| antd | 6.6.5 | 6.0.0 2025-11-21; CSS variables by default; React 18+ |
| @primer/primitives | 11.10.0 | |
| @atlaskit/tokens | 20.4.1 | |
| @react-spectrum/s2 | 1.8.1 | Spectrum 2 React |
| @fluentui/react-components | 9.74.9 | |
| @carbon/react | 1.118.0 | |
| baseui (Uber Base Web) | 18.2.0 | https://baseweb.design/ |
| govuk-frontend | 6.5.1 | |
| @shopify/polaris | 13.9.5 | React lib deprecated; Polaris Web Components released 2025-10-01 (repo README quoted in search); github.com/Shopify/polaris-react redirects to polaris-react-archive |
| @salesforce-ux/design-system | 2.264.1 | |
| @material/web | 2.5.0 | |
| lucide-react | 1.55.0 | 1.0.0 = 2026-03-23 |
| @phosphor-icons/react | 2.1.10 (2025-05-22) | |
| @tabler/icons-react | 3.49.0 | |
| @figma/code-connect | 2.0.1 | |

## Material 3 token values (androidx Compose material3 token files, androidx-main)

- StateTokens (VERSION v0_210): Dragged 0.16, Focus 0.10, Hover 0.08, Pressed 0.10.
  (Older Flutter token file v0_137 had focus/pressed 0.12.)
  https://raw.githubusercontent.com/androidx/androidx/androidx-main/compose/material3/material3/src/commonMain/kotlin/androidx/compose/material3/tokens/StateTokens.kt
- ElevationTokens (v0_103): Level0..5 = 0, 1, 3, 6, 8, 12 dp. (ElevationTokens.kt, same dir)
- ShapeTokens (14_1_0): ExtraSmall 4, Small 8, Medium 12, Large 16, LargeIncreased 20, ExtraLarge 28,
  ExtraLargeIncreased 32, ExtraExtraLarge 48 dp, Full = CircleShape, None = Rectangle. (ShapeTokens.kt)
  ExtraExtraLarge annotated as Material 3 Expressive API (kotlinlang ShapeDefaults docs, search).
- MotionTokens (v0_103): durations Short1-4 = 50/100/150/200, Medium1-4 = 250/300/350/400, Long1-4 = 450/500/550/600,
  ExtraLong1-4 = 700/800/900/1000 ms. Easing: Emphasized (0.2,0,0,1), EmphasizedAccelerate (0.3,0,0.8,0.15),
  EmphasizedDecelerate (0.05,0.7,0.1,1), Standard (0.2,0,0,1), StandardAccelerate (0.3,0,1,1),
  StandardDecelerate (0,0,0,1), Legacy (0.4,0,0.2,1), Linear. (MotionTokens.kt)
- FilledButtonTokens (v0_11_0): DisabledContainerOpacity 0.1, DisabledLabelTextOpacity 0.38, DisabledIconOpacity 0.38.
- ColorSchemeKeyTokens: 48 roles incl. Surface, SurfaceDim, SurfaceBright, SurfaceContainerLowest/Low/(base)/High/
  Highest, On*, *Container, *Fixed/*FixedDim, Outline, OutlineVariant, InverseSurface, Scrim, SurfaceTint.
- Third-party table for M3 elevation tint % (5/8/11/12/14) — not confirmed on m3.material.io (JS-rendered; WebFetch got only the title).

## Reference design systems (URLs all returned HTTP 200 on 2026-10-10)

- Material 3 https://m3.material.io/ · Apple HIG https://developer.apple.com/design/human-interface-guidelines/
- Fluent 2: two token layers — global (context-agnostic raw values) and alias (semantic); "We name alias tokens so that
  their function is immediately recognizable." https://fluent2.microsoft.design/design-tokens
- IBM Carbon: 4 themes White (default), Gray 10, Gray 90, Gray 100; tokens `$background`, `$layer-01`, `$text-primary`,
  `$text-secondary`, `$border-strong`, `$icon-primary`, `$field-01`, `$interactive` (-> `$blue-60`); token names
  constant across themes, values change. https://www.carbondesignsystem.com/building-blocks/foundations/themes/overview
- Shopify Polaris: docs now at https://shopify.dev/docs/api/polaris ; web components at
  https://shopify.dev/docs/api/app-home/polaris-web-components (redirects to .../app-home/latest/web-components).
- Atlassian: name = foundation (color, elevation, space) + property (border, background, shadow, text, icon) +
  optional modifiers (role, emphasis, state); examples `color.text`, `color.icon.success`, `opacity.loading`.
  https://atlassian.design/foundations/tokens/design-tokens
- GitHub Primer primitives: base tokens (size, typography) + functional tokens (size, typography, themes);
  `--fgColor-default`; themes light, light tritanopia, light high contrast, light colorblind, dark, dark dimmed,
  dark high contrast, dark colorblind, dark tritanopia; select with `data-color-mode`, `data-light-theme`,
  `data-dark-theme` (underscore values e.g. `dark_dimmed`). https://primer.style/product/primitives/
- Adobe Spectrum: new docs home organised by platform; React and Web Components in beta; iOS/Android coming.
  https://spectrum.adobe.com/
- Salesforce SLDS 2: global styling hooks = CSS custom properties `--slds-g-*` (e.g. `--slds-g-color-surface-3`,
  `--slds-g-color-brand-base-40`, `--slds-g-color-neutral-100`); `--sds-*` deprecated; component hooks `--slds-c-*`;
  dark mode via hooks; SLDS Linter. https://trailhead.salesforce.com/content/learn/modules/salesforce-lightning-design-system-2-for-developers/explore-salesforce-lightning-design-system-2
  · https://www.lightningdesignsystem.com/
- GOV.UK Design System: patterns "Ask users for…" (addresses, bank details, dates, email, equality info, names,
  NI numbers, passwords, payment card details, phone numbers), "Help users to…" (check answers, complete multiple
  tasks, recover from validation errors, ...), "Pages" (confirmation, question, service unavailable ...).
  Contribution: check GitHub discussions community backlog, open a discussion with evidence of user need; community
  prioritises yearly; criteria page separate. https://design-system.service.gov.uk/patterns/ ·
  https://design-system.service.gov.uk/community/propose-a-component-or-pattern/
- Ant Design: Seed Token (colorPrimary, borderRadius, fontSize, controlHeight) -> Map Token (algorithm-derived:
  colorPrimaryBg, colorPrimaryHover, borderRadiusLG/SM) -> Alias Token (colorLink, margin, padding, boxShadow) +
  Component Token (`components: { Button: {...} }`, `algorithm: true` since 5.8.0); algorithms default/dark/compact,
  combinable. v6 (2025-11-21) pure CSS variables. https://ant.design/docs/react/customize-theme ·
  https://dev.to/zombiej/ant-design-60-is-released-bfa
- Uber Base: https://base.uber.com/ (page content not extractable; title only) · Base Web React https://baseweb.design/

## Token naming

- Nathan Curtis, "Naming Tokens in Design Systems" (2020): namespace (system, theme, domain) · object (group, component,
  element) · base (category, concept, property) · modifier (variant, state, scale, mode). Example
  `$color-action-text-secondary-focus`. (Substack page partial + secondary summaries)
  https://nathanacurtis.substack.com/p/naming-tokens-in-design-systems-9e86c7444676
- Style Dictionary CTI (category/type/item), community CTI+ adds subitem + state.
- Singapore GDS: namespace-object-base-modifier; Mozilla: Ecosystem/Object/Category/Modifier (search results).

## Iconography

- Lucide design principles: 24x24 canvas, >=1px padding, 2px stroke, round joins + caps, centered strokes,
  radius 2px for shapes >=8px (1px below), >=2px spacing between elements, optical centering, match circle/square
  reference weight. https://lucide.dev/contribute/icon-design-guide (redirects to /contribute/icons/design-principles)
  Site shows "Search 1877 icons".
- Tabler: 6238 icons (5184 outline, 1054 filled), 24x24 grid, 2px stroke (webfont also 1.5 and 1). https://github.com/tabler/tabler-icons
- Phosphor README: "1,248 icons and counting", 6 weights Thin/Light/Regular/Bold/Fill/Duotone, "Designed at 16 x 16px".
  https://github.com/phosphor-icons/homepage
- Material Symbols: variable axes opsz 20-48, wght 100-700 (default 400), FILL 0-1, GRAD -50..200, ROND 0-100 (from the
  Google Fonts CSS API URL on the page); preferred size 24px. https://developers.google.com/fonts/docs/material_symbols
- SF Symbols page: "over 7,000 symbols", nine weights, three scales, four rendering modes (monochrome, hierarchical,
  palette, multicolor) + optional gradient; Draw On/Off animations; Variable Draw; download SF-Symbols-27 (OS 27).
  https://developer.apple.com/sf-symbols/

## CSS Color 4

- Gamut mapping: "For the OkLCh color space, one JND is an OkLCh difference of 0.02"; algorithm reduces chroma in
  OkLCh with clipping when deltaEOK < JND. https://www.w3.org/TR/css-color-4/ (curl + text extract)

## Verification log for the templates (this session)

- `tokens-starter.css`: Lightning CSS strict parse OK (0 warnings); css-tree parse 0 errors.
- Contrast/gamut checker (Node, culori, own script): resolves vars for light / dark(media) / dark(attr); 36 pairs each
  (text, muted, link, borders, primary/accent/status fills, subtle chips, focus ring). All pass at default hue 265 and
  for brand hues 0-330 (15-30 deg steps) with chroma clamped like CSS gamut mapping. Weakest primary-foreground on
  primary = 4.73:1; border-strong on surface = 3.78:1.
- Max in-gamut `--brand-c` per hue for the 11-step ramp (multipliers .08/.16/.34/.6/.9/1/1/.85/.65/.5/.35):
  h0 .198, h15 .185, h30 .185, h45 .154, h60 .127, h75 .114, h90 .110, h105 .115, h120 .128, h135 .158, h150 .149,
  h165 .114, h180 .098, h195 .092, h210 .093, h225 .102, h240 .124, h255 .171, h270 .167, h285 .175, h300 .198,
  h315 .247, h330 .246, h345 .230.
- Headless Chrome (playwright-core, channel chrome): OS light/dark x data-theme none/light/dark all resolve correctly;
  scoped `[data-theme="dark"]` section gets dark values and dark shadows; `data-brand="ocean"` -> primary
  `oklch(0.54 0.1 220)`; `data-density="compact"` -> button 32px; reduced motion -> `--duration-fast: 0ms`;
  h1 `--font-size-4xl` = 36px at 360px viewport, 56px at 1400px.
- Bug found and fixed: scoped `[data-theme="dark"]` subtree kept the parent's computed `color` (dark heading on dark
  bg). Fix: `:root, [data-theme] { color: var(--text); background-color: var(--bg); }`.
- `tailwind-theme.css` compiled with tailwindcss 4.3.3; all mapped utilities generated; css-tree flags
  `--color-*: initial` lines (Tailwind-only syntax) as expected.
- Audit script tested identical output in sh, bash, zsh on a fixture (zsh does not word-split a `$G` string variable,
  so the recipe uses a function). Color clustering at deltaEOK < 0.02 grouped `#333 / #333333 / rgb(51,51,51)`.

## Could not verify

- Official Figma mode limits per plan (only forum posts: Pro 10, Org 20, Enterprise 40).
- m3.material.io page text (JS-rendered); used androidx token sources instead.
- Exact current Phosphor icon count (README says 1,248 "and counting").
- Whether Style Dictionary v5 implements the DTCG Resolver module; Tokens Studio 2026 release details.
- Atlassian CSS variable prefix in code; Nathan Curtis full essay text (403 on Medium; partial on Substack).
- Web search budget ran out mid-session; later facts came from direct page fetches and npm.

## Additional verification (recipes in the reference file)

- State-layer recipe (`::before` overlay with `background: currentColor`, parent `isolation: isolate`, child
  `z-index: -1`) measured in Chrome: rest 0, hover 0.08, focus-visible 0.1, pressed 0.1; label stays above the overlay.
  Nested radius `max(0px, calc(var(--r) - var(--pad)))` with 16px/8px -> 8px.
- lucide-react 1.55.0 type definitions include `absoluteStrokeWidth?: boolean` ("Whether to use absolute stroke
  width") and a `LucideProvider` for defaults (npm pack inspection).
- Project Wallace CSS Design Tokens Analyzer extracts colors, font sizes/families, line heights, shadows, radii,
  durations, easings from a URL or pasted CSS. https://www.projectwallace.com/design-tokens · CSS Stats https://cssstats.com/ (200).
- stylelint-declaration-strict-value 1.12.1 (npm) enforces variables/functions for chosen properties.
  https://github.com/AndyOGo/stylelint-declaration-strict-value
- Mantine home: "more than 120 customizable components and 70 hooks", "built with native CSS", "no runtime overhead".
  https://mantine.dev/ · npm @mantine/core 9.7.1 deps: clsx, @floating-ui/react, react-number-format, react-remove-scroll.
- npm @chakra-ui/react 3.37.0 deps include `@ark-ui/react` 5.39.0 and `@emotion/*` (Ark-based, Emotion runtime).
- Browser support from @mdn/browser-compat-data (npm, 2026-10-10): oklch() Chrome 111 / Firefox 113 / Safari 15.4;
  light-dark() 123 / 120 / 17.5; color-mix() 111 / 113 / 16.2; color-scheme 81 / 96 / 13; Popover API 114 / 125 /
  Safari 17 (iOS 18.3); dialog.showModal 37 / 98 / 15.4; linear() easing 113 / 112 / 17.2; @container 105 / 110 / 16;
  :focus-visible 86 / 85 / 15.4.
