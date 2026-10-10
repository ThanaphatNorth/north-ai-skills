# Accessibility (WCAG 2.2 AA and beyond)

> Read when: designing or reviewing any screen, component, form, animation or colour palette; building custom widgets (dialog, menu, tabs, combobox, disclosure); shipping to the EU, US public sector or Thai government; writing a11y acceptance criteria or a test plan; a user mentions screen readers, keyboard, zoom, contrast, reduced motion, colour blindness or legal compliance.

**Contents:** Defaults to apply without asking · WCAG 2.2 AA checklist by POUR · Contrast and APCA · Keyboard and focus (recipes) · Semantics and ARIA patterns · Forms and errors · Motion and media · Colour-blind-safe design · Text resizing, Dynamic Type, reflow · Mobile: screen readers and targets · Cognitive accessibility (COGA) · Legal landscape 2025–2026 · Thai notes · Testing workflow and tools · Pitfalls · Sources

Related: palette building and contrast tokens in `color.md`; type scale, Thai line-height in `typography-layout.md`; animation durations in `motion.md`; parallax and scroll effects in `scroll-parallax.md`; platform specifics in `platform-web.md`, `platform-mobile.md`, `platform-desktop.md`; cognitive load and plain-language psychology in `psychology.md`.

## Defaults to apply without asking

1. Target **WCAG 2.2 Level AA**. Content that conforms to 2.2 also conforms to 2.1 and 2.0, so it covers ADA Title II (2.1 AA), Section 508 (2.0 AA) and is the reference for EN 301 549 / EAA work. WCAG 2.2 is also ISO/IEC 40500:2025.
2. Native HTML elements first (`button`, `a href`, `input`, `select`, `dialog`, `details`); ARIA only to fill gaps. WebAIM Million 2026: pages using ARIA averaged 59.1 detected errors vs 42 without.
3. Text contrast ≥ 4.5:1, large text and UI boundaries/icons/focus rings ≥ 3:1.
4. Every interactive element: keyboard operable, visible `:focus-visible` ring, accessible name, target ≥ 24×24 CSS px (aim 44×44 on touch).
5. Never convey meaning by colour alone; never disable zoom; layout reflows at 320 CSS px.
6. Respect `prefers-reduced-motion`; no auto-playing motion > 5 s without a pause control.
7. Forms: visible labels, `autocomplete` tokens, errors in text with how-to-fix, paste allowed in all credential/OTP fields.
8. `<html lang>` set; one `h1`; logical heading levels; landmarks (`header`, `nav`, `main`, `footer`).

Real-world baseline (WebAIM Million, Feb 2026 crawl): 95.9% of home pages had detected failures; most common: low-contrast text 83.9%, missing alt 53.1%, missing form labels 51%, empty links 46.3%, empty buttons 30.6%, missing `lang` 13.5%. Fix these six first.

## WCAG 2.2 AA checklist by POUR

★ = new in WCAG 2.2. 4.1.1 Parsing was removed in 2.2. A + AA = 55 criteria.

**Perceivable**

| SC | Lvl | Rule |
|---|---|---|
| 1.1.1 Non-text content | A | Meaningful images/icons have alt text or an accessible name; decorative images `alt=""`; charts get a text summary or data table |
| 1.2.1–1.2.3 Prerecorded media | A | Transcript for audio-only; captions for video; audio description or full text alternative |
| 1.2.4 Captions (live) | AA | Live video with audio is captioned |
| 1.2.5 Audio description | AA | Visual-only information in prerecorded video is described (or narrated in the main track) |
| 1.3.1 Info and relationships | A | Structure is in markup: headings, lists, `th`, `label for`, `fieldset/legend`, landmarks |
| 1.3.2 Meaningful sequence | A | DOM order = reading order; CSS `order`/grid placement must not change meaning |
| 1.3.3 Sensory characteristics | A | Instructions don't rely only on shape, position or sound ("the round button on the right") |
| 1.3.4 Orientation | AA | Works in portrait and landscape unless essential |
| 1.3.5 Identify input purpose | AA | `autocomplete` tokens on personal-data fields (`name`, `email`, `tel`, `street-address`, `cc-number`…) |
| 1.4.1 Use of colour | A | Colour never the only cue: add icon, text, underline or pattern |
| 1.4.2 Audio control | A | Audio auto-playing > 3 s can be paused/stopped or its volume controlled |
| 1.4.3 Contrast (minimum) | AA | Text 4.5:1; large text (≥ 24 px, or ≥ 14 pt ≈ 18.7 px bold) 3:1; ratios are not rounded (4.499 fails) |
| 1.4.4 Resize text | AA | 200% text zoom without loss of content or function |
| 1.4.5 Images of text | AA | Real text, not pictures of text (logos excepted) |
| 1.4.10 Reflow | AA | No 2-D scrolling at 320 CSS px wide (= 1280 px at 400%) or 256 px tall; maps, data tables, toolbars excepted |
| 1.4.11 Non-text contrast | AA | 3:1 for input borders, icons, focus indicators, chart marks, selected/checked states vs adjacent colours |
| 1.4.12 Text spacing | AA | No clipping when users set line-height 1.5, paragraph spacing 2×, letter-spacing 0.12em, word-spacing 0.16em |
| 1.4.13 Content on hover or focus | AA | Tooltips/popovers: dismissible (Esc) without moving pointer, hoverable, persist until dismissed |

**Operable**

| SC | Lvl | Rule |
|---|---|---|
| 2.1.1 Keyboard | A | Every function works by keyboard; no hover-only or drag-only features |
| 2.1.2 No keyboard trap | A | Focus can always leave a component |
| 2.1.4 Character key shortcuts | A | Single-character shortcuts can be turned off, remapped, or only fire when the component is focused |
| 2.2.1 Timing adjustable | A | Session timeouts: warn and give ≥ 20 s to extend with a simple action (or no limit) |
| 2.2.2 Pause, stop, hide | A | Auto-starting movement lasting > 5 s alongside other content (carousels, tickers, auto-updating feeds) needs pause/stop/hide |
| 2.3.1 Three flashes | A | Nothing flashes more than 3 times per second |
| 2.4.1 Bypass blocks | A | Skip link and/or landmarks + headings |
| 2.4.2 Page titled | A | Unique `<title>` "Page – Section – Site"; SPAs update it on every route change |
| 2.4.3 Focus order | A | Tab order follows meaning; never positive `tabindex`; overlays move focus in and back out |
| 2.4.4 Link purpose (in context) | A | Link text states the destination; no bare "click here" / "read more" |
| 2.4.5 Multiple ways | AA | At least two ways to reach pages (nav + search, or sitemap) |
| 2.4.6 Headings and labels | AA | Headings and labels describe topic or purpose |
| 2.4.7 Focus visible | AA | Visible focus indicator on every focusable element |
| ★2.4.11 Focus not obscured (min) | AA | Focused element never *fully* hidden by sticky header/footer, cookie banner or chat widget; use `scroll-padding` |
| 2.5.1 Pointer gestures | A | Pinch, multi-finger and path gestures have a single-tap alternative |
| 2.5.2 Pointer cancellation | A | Activate on up-event (`click`), allow abort by sliding off |
| 2.5.3 Label in name | A | Accessible name contains the visible label text (voice-control users say what they see) |
| 2.5.4 Motion actuation | A | Shake/tilt features have a UI alternative and can be turned off |
| ★2.5.7 Dragging movements | AA | Every drag (reorder, slider, kanban, map pan) has a click/tap alternative; a keyboard alternative alone is not enough |
| ★2.5.8 Target size (min) | AA | Targets ≥ 24×24 CSS px, or a 24 px circle centred on each small target doesn't overlap another; inline text links exempt |

**Understandable**

| SC | Lvl | Rule |
|---|---|---|
| 3.1.1 Language of page | A | `<html lang="th">`, `lang="en"`, etc. |
| 3.1.2 Language of parts | AA | `lang` on phrases or passages in another language |
| 3.2.1 On focus | A | Focus never triggers navigation, submission or pop-ups |
| 3.2.2 On input | A | Changing a field doesn't auto-submit or navigate without prior warning |
| 3.2.3 Consistent navigation | AA | Repeated navigation in the same order across pages |
| 3.2.4 Consistent identification | AA | Same function → same label and icon everywhere |
| ★3.2.6 Consistent help | A | Help, contact, chat or FAQ links in the same relative order on every page that has them |
| 3.3.1 Error identification | A | Errors described in text, field identified |
| 3.3.2 Labels or instructions | A | Visible labels; format hints before the field |
| 3.3.3 Error suggestion | AA | Tell the user how to fix it ("Enter a date like 31/12/2026") |
| 3.3.4 Error prevention (legal, financial, data) | AA | Reversible, or validated, or a review-and-confirm step |
| ★3.3.7 Redundant entry | A | Don't make users re-enter info given earlier in the same process: prefill or "Same as shipping address" |
| ★3.3.8 Accessible authentication (min) | AA | No memorising, puzzles or transcribing: allow paste and password managers, passkeys/WebAuthn, email links, OAuth; OTP fields must accept paste/autofill. Object-recognition CAPTCHA passes AA only |

**Robust**

| SC | Lvl | Rule |
|---|---|---|
| 4.1.2 Name, role, value | A | Custom widgets expose role, name and state (`aria-expanded`, `aria-checked`, `aria-selected`) and keep them updated |
| 4.1.3 Status messages | AA | "Saved", "3 results", "Added to cart" announced via `role="status"` (polite) without moving focus; urgent errors `role="alert"` |

Cheap AAA wins worth adopting by default: 2.4.13 Focus appearance (indicator ≥ 2 CSS px perimeter, 3:1 change), 2.5.5 Target size 44×44 CSS px, 2.3.3 Animation from interactions (reduced-motion support), 1.4.6 contrast 7:1 for long-form reading.

## Contrast and APCA

WCAG 2 (the legal baseline):

| Element | Minimum | Notes |
|---|---|---|
| Body text, placeholder text, labels | 4.5:1 | Placeholder is text: if it conveys anything, it needs 4.5:1 (better: don't use placeholder as label) |
| Large text (≥ 24 px, or ≥ 18.7 px bold) | 3:1 | |
| UI component boundaries, icons, focus ring, chart marks, toggle/checkbox states | 3:1 against adjacent colours | 1.4.11 |
| Disabled controls, decoration, logotypes | exempt | Keep disabled text legible anyway; explain why it's disabled |
| Text over images/video | 4.5:1 against the worst-case pixel | Use a scrim or solid backing |

APCA status (as of 2026-10-10): WCAG 3 is still a Working Draft (updated March 2026); the April 2026 Editor's Draft says "The contrast algorithm used in WCAG 3 is yet to be determined." APCA was removed from WCAG 3 drafts in July 2023. The APCA project still calls itself a candidate method. Rule: **pass WCAG 2 contrast first**; use APCA only as an extra design check (dark mode, thin or small fonts), never as a substitute.

APCA Lc guidance (APCA in a Nutshell; reference font Helvetica/Arial):

| Lc | Use | Example minimum size/weight |
|---|---|---|
| 90 | Preferred for body text | 18 px/300 or 14 px/400 |
| 75 | Minimum for body text columns | 18 px/400, 16 px/500, 14 px/700 |
| 60 | Minimum for other readable content text | 24 px/400, 16 px/700 |
| 45 | Headlines, large text; fine-detail icons | 36 px/400 or 24 px/700 |
| 30 | Absolute minimum for incidental text: placeholder, disabled, copyright | — |
| 15 | Non-text that must be seen: dividers, thick focus outlines | ≥ 5 px thick |

Dark mode: WCAG 2's formula overstates contrast for dark colours, so in dark themes aim above the minimum (e.g. 7:1 body) and avoid pure white on pure black for long text (halation); see `color.md`.

## Keyboard and focus (recipes)

Rules:
- Tab reaches every interactive element in visual/reading order; arrow keys move *within* composite widgets (tabs, menus, listboxes, radio groups) — one Tab stop per widget ("roving tabindex" or `aria-activedescendant`).
- Esc closes the topmost overlay and returns focus to its trigger.
- Never remove outlines without a replacement. Focus ring: ≥ 2 px, ≥ 3:1 against the surrounding background, offset from the element's border. Sticky headers/footers: reserve scroll padding (2.4.11).
- Hidden content (closed menus, off-canvas drawers, inactive carousel slides) must not be focusable: `hidden`, `inert`, or `display:none`.

```css
/* Focus ring — :focus-visible is Baseline (widely available since March 2022) */
:root { --focus: oklch(55% 0.2 260); --focus-w: 3px; --header-h: 64px; }

:where(a, button, input, select, textarea, summary, [tabindex]):focus-visible {
  outline: var(--focus-w) solid var(--focus);
  outline-offset: 2px;
}
/* Two-tone ring for components that sit on unknown/photo backgrounds */
.on-media:focus-visible {
  outline: 2px solid #fff;
  box-shadow: 0 0 0 4px #000;           /* dark band outside the white outline */
}
/* If you draw rings with box-shadow only, keep a transparent outline so
   Windows forced-colors mode still shows focus */
.shadow-ring:focus-visible { outline: 2px solid transparent; box-shadow: 0 0 0 3px var(--focus); }
@media (forced-colors: active) { :focus-visible { outline-color: Highlight; } }

/* 2.4.11: keep focused elements clear of a sticky header */
html { scroll-padding-top: calc(var(--header-h) + 8px); }
```

Skip link (first focusable element on the page):

```html
<body>
  <a class="skip-link" href="#main">Skip to main content</a> <!-- th: ข้ามไปยังเนื้อหาหลัก -->
  <header>…</header>
  <main id="main" tabindex="-1">…</main>
</body>
```
```css
.skip-link {
  position: absolute; inset-inline-start: 1rem; top: 1rem; z-index: 1000;
  padding: .75rem 1rem; background: #000; color: #fff; border-radius: .25rem;
  transform: translateY(-200%);
}
.skip-link:focus { transform: none; }
```

Visually hidden (readable by screen readers, invisible on screen; becomes visible if focused):

```css
.visually-hidden:not(:focus):not(:active) {
  position: absolute !important; width: 1px !important; height: 1px !important;
  margin: -1px !important; padding: 0 !important; border: 0 !important;
  overflow: hidden !important; clip-path: inset(50%) !important; white-space: nowrap !important;
}
```

## Semantics and ARIA patterns

APG rule: "No ARIA is better than bad ARIA." A role is a promise: `role="button"` on a `div` gives no keyboard behaviour; you must add Enter/Space, focusability and states yourself — so use `<button>`.

Screen-reader users mostly navigate by headings (71.6% start that way, WebAIM 2024): one `h1`, no skipped levels for styling, headings that describe sections.

| Widget | Keyboard | Roles/states | Focus rules |
|---|---|---|---|
| Modal dialog | Tab/Shift+Tab cycle inside; Esc closes | `role="dialog"` (native `<dialog>` + `showModal()`), `aria-modal="true"`, `aria-labelledby` → title | On open focus first control, or the least destructive button for irreversible actions, or a `tabindex="-1"` heading for long content; on close return focus to the trigger |
| Menu button + menu (app-style command menus only) | Enter/Space/↓ open and focus first item; ↑/↓ move; Home/End; type-ahead; Esc closes → focus to button; Tab leaves and closes | button `aria-haspopup="menu"` + `aria-expanded`; `role="menu"` > `menuitem` / `menuitemcheckbox` / `menuitemradio` | Items are not Tab stops |
| Site navigation dropdown | Tab between links; Enter/Space toggles | Disclosure: `<button aria-expanded>` + list of links. APG's navigation example deliberately avoids `role="menu"` because it lacks the behaviour AT expects of a menu | |
| Tabs | Tab into the active tab; ←/→ (↑/↓ if vertical) move; Home/End; Space/Enter activates in manual mode | `tablist` > `tab` (`aria-selected`, `aria-controls`); `tabpanel` (`aria-labelledby`) | Auto-activate on arrow only if panels render instantly; panel gets `tabindex="0"` if it has no focusable content |
| Combobox (autocomplete) | ↓ opens/moves into list; ↑ optional; Enter accepts; Esc closes, second Esc may clear; Alt+↓ opens without moving | input `role="combobox"`, `aria-expanded`, `aria-controls` → `listbox`, `aria-activedescendant` → `option[aria-selected]`, `aria-autocomplete` | DOM focus stays in the input |
| Disclosure / accordion | Enter/Space toggle | `<button aria-expanded aria-controls>`; or native `<details><summary>` | Content follows the button in DOM order |

Modal dialog recipe (native `<dialog>`):

```html
<button type="button" id="del-open" aria-haspopup="dialog">Delete project</button>
<dialog id="del" aria-labelledby="del-title">
  <h2 id="del-title">Delete project?</h2>
  <p>This permanently removes 12 files.</p>
  <form method="dialog">
    <button value="cancel" autofocus>Cancel</button>  <!-- least destructive gets focus -->
    <button value="delete">Delete</button>
  </form>
</dialog>
<script>
  const dlg = document.getElementById('del'), trigger = document.getElementById('del-open');
  trigger.addEventListener('click', () => dlg.showModal());   // page behind becomes inert; Esc closes
  dlg.addEventListener('close', () => trigger.focus());        // always return focus explicitly
</script>
```

Status messages: render an empty `<div role="status">` at page load and change its text later; live regions inserted together with their content are often not announced.

## Forms and errors

- Visible `<label>` for every field; placeholder is an example, never the label. Group radios/checkboxes in `fieldset` + `legend`.
- Mark required fields in text ("required") or mark optional ones — be consistent. `required` attribute for AT.
- `autocomplete` tokens + correct `type`/`inputmode` (`email`, `tel`, `inputmode="numeric"` for codes).
- Validate on submit and on blur, not on every keystroke; never show an error before the user has had a chance to type.
- Error text: what's wrong + how to fix, next to the field, with an icon (not colour alone); `aria-invalid="true"` and `aria-describedby` → error id.
- On submit with errors: show an error summary at the top listing each error as a link to its field, and move focus to the summary.
- Keep the submit button enabled; disabled buttons give no reason and often fail contrast.
- 3.3.4: before legal/financial/data-deleting submits, show a review step or allow undo.
- 3.3.7: prefill data from earlier steps; offer "Same as shipping address".
- 3.3.8: allow paste in password and OTP fields; `autocomplete="current-password"` / `new-password` / `one-time-code`; support passkeys; no "type the 3rd and 5th character".
- Timeouts (2.2.1): warn before expiry with "Stay signed in" button and ≥ 20 s to respond; save form progress.

```html
<form novalidate>
  <div id="error-summary" class="error-summary" tabindex="-1" hidden>
    <h2>There is a problem</h2>
    <ul><li><a href="#email">Enter an email address like name@example.com</a></li></ul>
  </div>

  <label for="email">Email</label>
  <p id="email-hint" class="hint">We'll send your receipt here.</p>
  <input id="email" name="email" type="email" autocomplete="email" required
         aria-describedby="email-hint email-error" aria-invalid="true">
  <p id="email-error" class="field-error">
    <svg aria-hidden="true" width="16" height="16"><use href="#icon-alert"/></svg>
    Enter an email address like name@example.com
  </p>

  <label for="otp">Verification code</label>
  <input id="otp" name="otp" inputmode="numeric" autocomplete="one-time-code">
  <button type="submit">Continue</button>
</form>
<!-- On failed submit: unhide #error-summary, then errorSummary.focus() -->
```

## Motion and media

- Vestibular disorders: large-scale motion (parallax, zoom/scale of big areas, panning, spinning, scroll-jacking) can cause dizziness and nausea. `prefers-reduced-motion: reduce` means remove, reduce or replace motion — swap translate/scale for opacity fades, keep state changes instant or fade-only.
- 2.3.3 (AAA, but treat as default): motion triggered by interaction can be disabled. 2.2.2 (A): auto-starting movement > 5 s needs pause/stop/hide — carousels need a visible Pause button. 1.4.2: no auto-playing audio > 3 s without controls. 2.3.1: ≤ 3 flashes per second.
- Autoplay video: muted, with visible pause; no autoplay when reduced motion is on.
- Users set it in: iOS Settings > Accessibility > Motion; macOS 26 Tahoe System Settings > Accessibility > Motion; Windows 11 Settings > Accessibility > Visual effects > Animation effects; Android 9+ Settings > Accessibility > Remove animations.

```css
/* Opt-in motion: animate only when the user has not asked for less (Baseline since Jan 2020) */
@media (prefers-reduced-motion: no-preference) {
  html { scroll-behavior: smooth; }
  .card { transition: transform 250ms cubic-bezier(.2,.8,.2,1); }
  .card:hover { transform: translateY(-4px); }
  .reveal { animation: rise 400ms ease-out both; }
}
@media (prefers-reduced-motion: reduce) {
  .reveal { animation: fade 200ms ease-out both; }   /* replace, don't just delete feedback */
  .parallax-layer { transform: none !important; }
}
@keyframes rise { from { opacity: 0; transform: translateY(16px); } to { opacity: 1; transform: none; } }
@keyframes fade { from { opacity: 0; } to { opacity: 1; } }
```
```ts
// JS / GSAP / three.js: read the same preference and react to changes
const rm = window.matchMedia('(prefers-reduced-motion: reduce)');
export const reducedMotion = () => rm.matches;
rm.addEventListener('change', (e) => setMotionEnabled(!e.matches)); // your app's toggle
```
Legacy safety net (blunt; also freezes spinners after one cycle — prefer the opt-in pattern):
`@media (prefers-reduced-motion: reduce){*,*::before,*::after{animation-duration:.01ms!important;animation-iteration-count:1!important;transition-duration:.01ms!important;scroll-behavior:auto!important}}`

## Colour-blind-safe design

About 1 in 12 men have a colour vision deficiency, red-green most common (NEI).
- Pair every colour signal with a second cue: icon + text for status, underline for links in body text, patterns/markers/dashes for chart series, labels on map regions.
- Error = red border **and** icon **and** message. Success = green **and** check icon **and** text.
- Charts: label series directly on the lines/bars instead of a legend; use the Okabe–Ito palette for categorical data — `#E69F00` orange, `#56B4E9` sky blue, `#009E73` bluish green, `#F0E442` yellow, `#0072B2` blue, `#D55E00` vermilion, `#CC79A7` reddish purple, `#000000` black. Thin lines and small dots are harder to tell apart: increase stroke and marker size.
- Avoid red/green as the only pair; red text on dark backgrounds reads poorly.
- Check with a CVD simulator (Chrome DevTools Rendering → Emulate vision deficiencies; Stark in Figma). See `color.md` for palette tooling and `dataviz` guidance for charts.

## Text resizing, Dynamic Type, reflow

- Web: font sizes in `rem`, containers grow with content (no fixed heights on text boxes), `min-height` not `height`. Test 200% text zoom, 400% page zoom, 320 CSS px viewport, and the text-spacing override (1.4.12).
- Never ship `<meta name="viewport" content="maximum-scale=1, user-scalable=no">`; use `width=device-width, initial-scale=1`.
- Truncation: wrap instead of ellipsis for primary content; if truncated, make full text available.
- iOS: use Dynamic Type text styles (`.body`, `.headline`; UIKit `preferredFont(forTextStyle:)` + `adjustsFontForContentSizeCategory`). App Store "Larger Text" Accessibility Nutrition Label requires text to enlarge to ≥ 200% (or the system max) without overlap or unusable truncation; iOS Dynamic Type exceeds 200% at AX3. Stack side-by-side layouts at accessibility sizes; tab bars use the Large Content Viewer.
- Android: text in `sp`, layouts that wrap; test at the largest font and display size.
- Thai script needs vertical room for stacked vowels and tone marks: don't clip line boxes; see `typography-layout.md` for Thai line-height.

## Mobile: screen readers and targets

| Platform | Minimum target | Notes |
|---|---|---|
| Web (WCAG 2.5.8 AA) | 24×24 CSS px or spacing exception | 44×44 is AAA (2.5.5) and the better default for touch |
| iOS (Apple HIG) | 44×44 pt | visionOS 60×60 pt; hit area may exceed the visible glyph |
| Android (Material) | 48×48 dp, ~8 dp apart | Compose Material controls expand touch area automatically |

- Usage (WebAIM survey, Dec 2023–Jan 2024): mobile screen reader users — VoiceOver 70.6%, TalkBack 34.7%; test on both. Native: set `accessibilityLabel` (iOS) / `contentDescription` (Android) on icon-only buttons; expose traits/roles (button, header, selected); group related elements into one focus stop (card = one element with a combined label); announce async results; don't trap focus in custom sheets.
- Respect system settings: Reduce Motion, Bold Text, Increase Contrast / high-contrast text, Dark Mode, Dynamic Type/font scale.
- Provide alternatives for gestures (2.5.1 swipe-to-delete → also an Edit/Delete button; 2.5.4 shake-to-undo → also an Undo button; 2.5.7 drag-to-reorder → move up/down actions or accessibility custom actions).
- App Store Accessibility Nutrition Labels (declared per app): VoiceOver, Voice Control, Larger Text, Dark Interface, Differentiate Without Color Alone, Sufficient Contrast, Reduced Motion, Captions, Audio Descriptions. Only declare what common tasks fully support.

## Cognitive accessibility (COGA)

W3C "Making Content Usable for People with Cognitive and Learning Disabilities" (Working Group Note, 2021; supplemental, not required for conformance). Turn its 8 objectives into rules:
1. Make purpose and controls obvious: familiar layouts, consistent design, icons with text labels.
2. Help users find things: clear hierarchy, search, the most important actions visible without scrolling far.
3. Clear content: common words, short sentences, active voice, one idea per paragraph, summaries for long content, generous white space.
4. Prevent and fix mistakes: no unexpected movement, Back always works, undo, forms that prevent errors, clear labels, feedback after every action.
5. Help focus: limit interruptions (pop-ups, notifications), short critical paths, avoid excess content.
6. Don't rely on memory: login without memorised passwords or transcription (passkeys, magic links), no mental calculation, show needed info on the same screen.
7. Provide help: reachable human help, consistent help location (3.2.6), explain consequences before actions.
8. Support personalisation: user control over moving content, simplified modes, respect browser/OS settings.

## Legal landscape 2025–2026

As of 2026-10-10; not legal advice.

| Law | Who | Technical standard | Dates and notes |
|---|---|---|---|
| European Accessibility Act, Directive (EU) 2019/882 | Products placed on the EU market and services provided to EU consumers: e-commerce, consumer banking, e-books, electronic communications, audiovisual media access, passenger transport services, plus covered hardware (computers, smartphones, terminals). Applies to non-EU firms selling into the EU (secondary sources) | EN 301 549 (harmonised standard, built on WCAG; presumption of conformity) | Applies since **28 June 2025**. Microenterprises providing services (< 10 staff and ≤ EUR 2 million turnover or balance sheet) exempt. Transition up to 5 years for products already used in services; self-service terminals until end of economic life, max 20 years. Penalties set per member state |
| ADA Title II web rule (US state and local government) | Public entities' websites and mobile apps | WCAG 2.1 AA | DOJ interim final rule (20 April 2026) moved deadlines: populations ≥ 50,000 → **26 April 2027**; < 50,000 and special districts → **26 April 2028**. Title II obligations themselves still apply now |
| ADA Title III (US private businesses) | Public accommodations | No DOJ web rule; WCAG 2.x AA is the usual benchmark in litigation and settlements (general knowledge) | Lawsuit risk continues |
| Section 508 (US federal agencies and their ICT) | Federal ICT, procurement | WCAG 2.0 A + AA incorporated by reference (2017 rule), applied to non-web documents and software | Vendors selling to US government often supply an ACR/VPAT |
| ISO/IEC 40500:2025 | International | = WCAG 2.2 | Announced 21 Oct 2025; lets national standards adopt 2.2 |

Practical rule: build to WCAG 2.2 AA, publish an accessibility statement with a contact route, document known exceptions and fix dates.

## Thai notes

- Set `<html lang="th">`; wrap English terms in Thai pages with `lang="en"` (3.1.2) so screen readers switch voice and pronunciation. Thai VoiceOver is supported on iOS ("Thai (Thailand)"), and NVDA's interface is translated into Thai; quality of Thai word segmentation varies by screen reader and synthesizer (unverified this session) — test with real Thai content.
- Thai has no spaces between words, so avoid images of text and fake spacing with `&nbsp;`; use real text so AT and translation tools can segment it.
- Dates: Buddhist Era is common; give machines the ISO date: `<time datetime="2026-10-10">10 ต.ค. 2569</time>`.
- Standards in Thailand:
  - **มอก. 2565-2555 (TIS 2565-2555)**: Thai Industrial Standard adopting WCAG 2.0 (adopted 2013). NSTDA (สวทช.) is the W3C Lead Translation Organization for WCAG 2.2 Thai; a Thai authorized translation of WCAG 2.2 is published on NECTEC (dated 28 Dec 2025), and TISI plans to update the standard from ISO/IEC 40500:2025.
  - **TWCAG 2025** (แนวทางการพัฒนาเว็บที่ทุกคนเข้าถึงได้): by the Digital Council of Thailand (สภาดิจิทัลฯ) with the Thai Internet Foundation and ThaiHealth (สสส.); updates TWCAG 2022; based on WCAG 2.2; covers websites and mobile apps.
  - Government awards by สดช. (2023): judged by manual review, automated checks with zero errors, then testing by blind and deaf users. One blind judge flagged sites that embed their own "reading" widget, which clashes with users' own screen readers — don't add overlay/reader widgets; fix the markup.
- For Thai public-sector projects, state the target explicitly in requirements: "WCAG 2.2 AA (TWCAG 2025)".

## Testing workflow and tools

Automated tools find roughly 57% of issues by volume (Deque, axe-core, 13,000+ pages) — not 57% of criteria, and never conformance. A Lighthouse 100 only means the weighted automated audits passed; it excludes tab order and focus management.

| Stage | Tool | What it catches |
|---|---|---|
| Design | Stark (Figma/FigJam/Sketch plugins), contrast checkers, CVD simulators | Contrast, colour-only meaning; annotate focus order, headings, alt text and target sizes in the handoff |
| Code / CI | axe-core (`@axe-core/playwright`, jest-axe), eslint-plugin-jsx-a11y | Missing names, labels, alt, ARIA misuse, contrast on rendered pages |
| Browser | axe DevTools extension (incl. Intelligent Guided Tests), Accessibility Insights for Web FastPass (~50 automated checks + Tab-stops, < 5 min; Assessment for WCAG 2.1 AA), Lighthouse | Fast regression pass per page |
| Manual | Keyboard, zoom/reflow, reduced motion, forced colours, screen readers | Everything automation can't judge |
| People | Usability tests with disabled participants | Real barriers and workarounds |

```ts
// Playwright + axe-core: fail CI on detectable WCAG A/AA violations
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test('checkout has no detectable a11y violations', async ({ page }) => {
  await page.goto('/checkout');
  const { violations } = await new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa'])
    .analyze();
  expect(violations).toEqual([]);
});
```

Manual pass (≈ 15 min per key page):
1. **Keyboard**: unplug the mouse. Tab through: is focus always visible, never hidden by sticky UI, in logical order? Open/close every overlay with Enter/Esc; focus returns to the trigger. No traps.
2. **Zoom/reflow**: 200% text zoom; 400% page zoom at 1280 px (= 320 px) — no horizontal scroll, nothing clipped. Apply text-spacing override.
3. **Preferences**: reduced motion on (no parallax/zoom), Windows forced colours/high contrast (focus and borders still visible), dark mode contrast.
4. **Screen-reader smoke test** (NVDA + Chrome or Firefox on Windows — free; VoiceOver + Safari on macOS/iOS; TalkBack + Chrome on Android):
   - Page title announced on load and on SPA route change.
   - Headings list (NVDA: `Insert+F7` elements list, `H`/`1`–`6`; VoiceOver: rotor `VO+U`, or iOS two-finger rotate → Headings) shows a sensible outline with one h1.
   - Landmarks (NVDA `D`) include main and navigation.
   - Links list makes sense out of context (NVDA `K`).
   - Every form field announces label, required state, hint and error (NVDA `F`; Tab).
   - Buttons announce name and state (expanded/collapsed, pressed, selected).
   - Images: meaningful alt; decorative ones silent.
   - Dynamic updates (add to cart, validation, search results count) are announced without focus jumps.
   - Modals: focus moves in, background not reachable, Esc closes, focus returns.
   - Mobile: swipe right through the whole screen; double-tap activates every control; no unlabeled "button".
5. **Record** each issue with WCAG SC, severity, steps and screenshot; re-test after fix.

## Pitfalls

| Symptom | Cause | Fix |
|---|---|---|
| Focus ring vanishes on click and keyboard | `outline: none` reset | Style `:focus-visible`; keep a transparent outline for forced colours |
| Tabbing goes "behind" the sticky header | No scroll padding (fails 2.4.11) | `scroll-padding-top` = header height + gap |
| Screen reader reads hidden menu items | Off-canvas content only moved off-screen | `hidden`/`inert` when closed |
| `div role="button"` ignores Enter/Space | ARIA adds semantics, not behaviour | Use `<button>` |
| Site nav announced as "menu" with broken arrows | `role="menu"` on links | Disclosure pattern for navigation |
| Status toast never announced | Live region injected with its text | Keep an empty `role="status"` in the DOM, update its text |
| OTP field rejects paste; users locked out | Paste blocked "for security" (fails 3.3.8) | Allow paste, `autocomplete="one-time-code"` |
| Lighthouse 100 but blind users can't check out | Automated checks cover ~half the issues | Manual keyboard + screen-reader pass on key flows |
| Accessibility overlay widget installed, complaints rise | Overlays conflict with users' own AT (Thai judges flagged this) | Remove overlay; fix source markup |
| APCA-passing palette fails audit | APCA isn't the legal standard | Meet WCAG 2 ratios; use APCA only as an extra check |
| Layout breaks at iOS AX sizes | Fixed heights, side-by-side rows | Wrap/stack at accessibility sizes, allow multi-line labels |
| Carousel fails 2.2.2 | Auto-advance without pause | Visible Pause, no auto-advance under reduced motion |

## Sources

- W3C, What's New in WCAG 2.2 — https://www.w3.org/WAI/standards-guidelines/wcag/new-in-22/
- W3C, WCAG 2.2 approved as ISO/IEC 40500:2025 — https://www.w3.org/WAI/news/2025-10-21/wcag22-iso
- W3C Understanding docs: Target Size (Minimum) https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html · Focus Not Obscured https://www.w3.org/WAI/WCAG22/Understanding/focus-not-obscured-minimum.html · Dragging Movements https://www.w3.org/WAI/WCAG22/Understanding/dragging-movements.html · Accessible Authentication https://www.w3.org/WAI/WCAG22/Understanding/accessible-authentication-minimum.html · Pause, Stop, Hide https://www.w3.org/WAI/WCAG22/Understanding/pause-stop-hide.html · Animation from Interactions https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html · Reflow https://www.w3.org/WAI/WCAG22/Understanding/reflow.html · Contrast (Minimum) https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html
- W3C, WCAG 3 Working Draft March 2026 — https://www.w3.org/WAI/news/2026-03-03/wcag3
- Adrian Roselli, WCAG3 Contrast as of April 2026 — https://adrianroselli.com/2026/04/wcag3-contrast-as-of-april-2026.html
- APCA in a Nutshell — https://git.apcacontrast.com/documentation/APCA_in_a_Nutshell.html
- WAI-ARIA APG: Read Me First https://www.w3.org/WAI/ARIA/apg/practices/read-me-first/ · Dialog (Modal) https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/ · Tabs https://www.w3.org/WAI/ARIA/apg/patterns/tabs/ · Combobox https://www.w3.org/WAI/ARIA/apg/patterns/combobox/ · Menu Button https://www.w3.org/WAI/ARIA/apg/patterns/menu-button/ · Menu and Menubar https://www.w3.org/WAI/ARIA/apg/patterns/menubar/ · Disclosure https://www.w3.org/WAI/ARIA/apg/patterns/disclosure/ · Disclosure Navigation example https://www.w3.org/WAI/ARIA/apg/patterns/disclosure/examples/disclosure-navigation/
- W3C, Making Content Usable for People with Cognitive and Learning Disabilities — https://www.w3.org/TR/coga-usable/
- WebAIM Million (2026) — https://webaim.org/projects/million/
- WebAIM Screen Reader User Survey #10 — https://webaim.org/projects/screenreadersurvey10/ · WebAIM, Testing with Screen Readers — https://webaim.org/articles/screenreader_testing/
- NVDA User Guide — https://download.nvaccess.org/documentation/userGuide.html
- MDN, :focus-visible — https://developer.mozilla.org/en-US/docs/Web/CSS/:focus-visible · MDN, prefers-reduced-motion — https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion
- NEI, Color blindness — https://www.nei.nih.gov/learn-about-eye-health/eye-conditions-and-diseases/color-blindness
- Claus Wilke, Fundamentals of Data Visualization: color pitfalls (Okabe–Ito) — https://clauswilke.com/dataviz/color-pitfalls.html · Okabe & Ito, Color Universal Design — https://jfly.uni-koeln.de/color/
- Apple, UI Design Dos and Don'ts (44×44 pt) — https://developer.apple.com/design/tips/
- Apple, Larger Text evaluation criteria (Accessibility Nutrition Labels) — https://developer.apple.com/help/app-store-connect/manage-app-accessibility/larger-text-evaluation-criteria/
- Apple, iOS feature availability (VoiceOver languages) — https://www.apple.com/ios/feature-availability/
- Google, Android touch target size (48 dp) — https://support.google.com/accessibility/android/answer/7101858
- Directive (EU) 2019/882 (EAA) — https://eur-lex.europa.eu/eli/dir/2019/882/oj · European Commission EAA page — https://commission.europa.eu/strategy-and-policy/policies/justice-and-fundamental-rights/disability/union-equality-strategy-rights-persons-disabilities-2021-2030/european-accessibility-act_en
- Level Access, Is WCAG conformance enough for EAA — https://www.levelaccess.com/blog/is-wcag-conformance-enough-for-eaa-compliance/
- Federal Register, Extension of compliance dates (ADA Title II), 2026-04-20 — https://www.federalregister.gov/documents/2026/04/20/2026-07663/extension-of-compliance-dates-for-nondiscrimination-on-the-basis-of-disability-accessibility-of-web · JD Supra summary — https://www.jdsupra.com/legalnews/doj-extends-title-ii-ada-web-2176958/
- US Access Board, ICT (Revised 508 Standards) — https://www.access-board.gov/ict/
- W3C translators list, NSTDA WCAG 2.2 Thai (2025) — https://lists.w3.org/Archives/Public/w3c-translators/2025JulSep/0017.html · (2026) https://lists.w3.org/Archives/Public/w3c-translators/2026JanMar/0000.html
- NECTEC, WCAG 2.2 Thai translation — https://www.nectec.or.th/standard/WCAG/REC-WCAG22-20241212-TH/
- TWCAG 2025 (Digital Council of Thailand), hosted copy — https://digital.hcu.ac.th/wp-content/uploads/2025/05/Accessibility-Guideline-2025-V.3.1-Final.pdf
- Thai PBS, WCAG website awards (2023) — https://www.thaipbs.or.th/now/content/191
- Deque, Automated testing coverage — https://www.deque.com/automated-accessibility-testing-coverage/ · axe DevTools — https://www.deque.com/axe/devtools/
- Chrome, Lighthouse accessibility scoring — https://developer.chrome.com/docs/lighthouse/accessibility/scoring
- Accessibility Insights for Web — https://accessibilityinsights.io/docs/web/overview/ · Stark — https://www.getstark.co/
