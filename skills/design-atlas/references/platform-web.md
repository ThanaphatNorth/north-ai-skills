# Platform: Web (sites, landing pages, web apps)

> Read when: building or reviewing anything that ships in a browser — responsive layout, site navigation, a landing/marketing page, CTAs, web forms, Core Web Vitals, PWA install, cookie banners, theme toggles, Thai/English or RTL pages, or deciding which modern CSS is safe to use in 2026.

**Contents:** Responsive strategy · Navigation patterns · Landing-page anatomy · CTA design · Web forms · Performance as UX · Perceived performance · PWA & installability · Cookie consent · Theme toggle · i18n (Thai, RTL) · Baseline CSS in 2026 · SEO-relevant UX · Pitfalls · Sources

Facts are as of 2026-10-10. Sibling files: `typography-layout.md` (type scale, grids), `accessibility.md` (WCAG), `motion.md` / `scroll-parallax.md` (animation), `3d-webgl.md`, `product-patterns.md` (onboarding, empty states, pricing tables), `platform-mobile.md` (native apps), `platform-desktop.md` (desktop-class web apps).

---

## Responsive strategy

**Rules**
1. **Mobile-first CSS.** Base styles = narrowest layout; add `@media (width >= …)` enhancements. Never ship a desktop layout and "fix" mobile with max-width overrides.
2. **Content-driven breakpoints.** Add a breakpoint where the content breaks (line length > ~75ch, cards squeeze below their minimum, nav wraps). When you have no content signal yet, start from Android's window classes — they are the only published, research-backed set:

| Class (width) | Range | Typical web layout |
|---|---|---|
| Compact | < 600px | 1 column, bottom/tab or collapsed nav, full-width CTAs |
| Medium | 600–839px | 1–2 columns, rail or visible top nav (≤5 items) |
| Expanded | 840–1199px | 2–3 columns, persistent sidebar possible |
| Large | 1200–1599px | max content width ~1200–1440px, side panels |
| Extra-large | ≥ 1600px | cap measure; add panes, not wider text |

3. **Page layout = viewport media queries; components = container queries.** Container queries are Baseline *Widely available* (since 2025-08-14) → use freely for cards, sidebars, widgets that appear in multiple slots.
4. **Fluid type and space** with `clamp()` between two viewport widths (e.g. 360px → 1280px). Body text: 16px floor on mobile (Safari zooms focused inputs below 16px), 16–18px desktop, line-height 1.5–1.7, measure 45–75ch. Details in `typography-layout.md`.
5. **Full-height sections:** use `min-height: 100svh` (small viewport, stable) for heroes; `100dvh` only for app shells that must track the URL bar. Viewport unit variants are Widely available (2025-06-05).
6. **Touch vs pointer:** branch on capability, not width: `@media (hover: hover) and (pointer: fine)` for hover-only affordances; `(pointer: coarse)` → targets ≥44×44px.

```css
/* Fluid scale (360px → 1280px). Tokens, not magic numbers. */
:root {
  --step-0: clamp(1rem, 0.951rem + 0.217vw, 1.125rem);   /* body 16→18px */
  --step-3: clamp(1.75rem, 1.359rem + 1.739vw, 2.75rem);  /* h1 28→44px */
  --space-m: clamp(1rem, 0.804rem + 0.87vw, 1.5rem);      /* 16→24px */
}
/* Component reacts to its slot, not the viewport */
.card-list { container-type: inline-size; }
@container (inline-size >= 36rem) {
  .card { display: grid; grid-template-columns: 12rem 1fr; gap: var(--space-m); }
}
```

## Navigation patterns

| Pattern | Use when | Rules |
|---|---|---|
| Visible top bar | ≤5–7 top-level sections, marketing/content sites | Logo left → home; current section marked (`aria-current="page"`); primary CTA right; make it sticky only if it is a single compact row |
| Mega menu | Large catalogs, universities, docs hubs | Open after **0.5 s** stationary hover, render within **0.1 s**, close after pointer is outside **0.5 s**; tolerate diagonal pointer paths; groups from card sorting; every top item also links to a real page; keep site search outside the menu (NN/g) |
| Sidebar | Web apps, docs, dashboards | ≤2 levels; collapsible to icon rail ≥840px; persist collapsed state |
| Hamburger / hidden nav | Mobile only, >4–5 sections | See evidence below. Label it "Menu", high contrast, not adjacent/confusable with logo |
| Combo nav | Mobile with 4–5 key sections | Show top 3–4 visibly (tabs/chips/bottom bar), rest under "More/Menu" |
| Breadcrumbs | ≥3 levels of hierarchy, e-commerce, docs | Hierarchy not history; "Home > … > Current" with current unlinked; one canonical path; show only last 1–2 levels on mobile, no wrapping (NN/g) |
| Search-first | Catalogs > ~100 items, docs, help centers, apps | Visible search *field* (not just an icon) on desktop; `/` or ⌘K/Ctrl+K to focus in apps; scoped suggestions + recent queries |

**Hamburger evidence (NN/g quantitative study):** desktop — navigation was used in 27% of tasks with hidden nav vs 48% visible / 50% combo, tasks ≥39% slower; mobile — 57% hidden vs 86% combo, 15% slower; discoverability dropped >20%. Rules that follow: **never hide primary nav on desktop**; on mobile show ≤4 top-level links visibly, hide only the rest.

## Landing-page anatomy

Order sections by the visitor's questions: *What is it? Is it for me? Can I trust it? How does it work? What does it cost? What if…? → Act.*

| # | Section | Must contain | Evidence / rule |
|---|---|---|---|
| 1 | **Hero** (above the fold) | H1 value proposition (what + for whom + outcome), 1–2 line subhead with the concrete mechanism, **one primary CTA**, a proof snippet (rating, customer count, logo strip), real product visual | NN/g 2018 eyetracking: 57% of viewing time above the fold, 74% in the first two screenfuls. CXL: value prop = headline + subhead + optional bullets answering what / what you can do / how it helps / why you over alternatives |
| 2 | Social proof | Real customer logos (5–8), named testimonials with photo + role + specific result | CXL: specific testimonials beat generic praise; photos aid recall; place proof right after the value prop and next to CTAs. NN/g: users discount curated on-site quotes and cross-check third-party reviews → link to G2/Trustpilot/App Store ratings |
| 3 | Problem → outcome | 3–6 features written as outcomes ("Close the books in 2 days"), each with a visual | Feature names alone fail the "so what" test |
| 4 | How it works | 3 numbered steps, ≤15 words each | Reduces perceived effort |
| 5 | Deeper proof | Case study numbers, security/compliance badges (SOC 2, ISO, PDPA/GDPR) for B2B | Proof only helps when uncertainty is high; irrelevant proof can hurt (CXL) |
| 6 | Pricing | 2–4 tiers, recommended tier highlighted, annual/monthly toggle, total cost visible | Baymard: 12% abandon when they can't see total cost up front; 40% over extra costs |
| 7 | FAQ | 5–8 real objections (cancel, data, migration, support), `<details>` accordions | Answers objections that block the CTA |
| 8 | Final CTA | Repeat headline promise + same primary CTA | Don't introduce a new offer here |

**Copy test:** run a 5-second test — a stranger must say what it is and who it's for. Lead with clarity over cleverness; if the headline is vague and the subhead is concrete, swap them.
**Hero media:** a static product shot or short muted loop beats a carousel. Carousels: ≤5 frames, never auto-advance on mobile, controls inside the frame, and every frame's content reachable elsewhere (NN/g).
**Avoid false floors:** if the hero fills exactly 100vh, let the next section peek (≥40–80px) so people scroll.

## CTA design

- **One primary CTA per viewport**, same label everywhere on the page; secondary actions as outline/text buttons.
- **Label = verb + outcome:** "Start free trial", "Get my quote", "ดูราคา" — never "Submit"/"Click here". Add risk-reducing microcopy beneath ("No credit card · Cancel anytime").
- **Size:** ≥44×44px (WCAG 2.5.8 AA floor is 24×24px; 44×44px is the comfortable touch target); full-width on compact screens; 48–56px tall for hero CTAs.
- **Contrast:** button fill vs background ≥3:1 (non-text contrast), label ≥4.5:1. See `color.md`.
- **Sticky mobile CTA bar** only on long product/pricing pages; 56–64px tall, respects `env(safe-area-inset-bottom)`, hides when the in-page CTA is visible.
- **States:** default, hover (pointer only), focus-visible ring ≥2px, pressed, loading (keep width, show spinner, disable double submit), disabled (explain why nearby).

## Web forms

| Field | Markup |
|---|---|
| Email (also username) | `type="email" autocomplete="email"` (sign-in: `autocomplete="username"`) |
| Password | `type="password" autocomplete="current-password"` / `new-password` on sign-up; show/hide toggle `type="button"` |
| Phone | `type="tel" autocomplete="tel"` |
| Full name | one field `autocomplete="name"` — Baymard: 42% of testers typed their full name into "First name" |
| Address | `street-address` / `address-line1`, `postal-code`, `country`; hide "Address line 2" behind a link |
| OTP | `type="text" inputmode="numeric" autocomplete="one-time-code" pattern="\d{6}"` — one input, not `type="number"` |
| Numbers (qty, amount) | `inputmode="decimal"` + `type="text"`; never `type="number"` for codes, card numbers, IDs |

**Rules**
- Single column; label above field; never placeholder-as-label; mark optional fields "(optional)" rather than starring required ones.
- Validate on blur and on submit, not on every keystroke; error text below the field, names the fix ("Enter a 10-digit phone number"), linked via `aria-describedby`; on submit, focus the first error and show a summary.
- Cut fields: Baymard 2024 — average checkout has 11.3 fields, most need 8; fixing checkout UX can lift conversion ~35%. Defer account creation to the confirmation step (18% abandon over forced accounts); keep guest checkout; billing = shipping by default; hide coupon field behind a link.
- Never ask users to retype email or password; rely on autofill and password managers. Support passkeys where you have auth.
- OTP via SMS: end the message with `@your.domain #123456` (origin-bound, ≤140 chars) so iOS/Android autofill and WebOTP pick it up.

```html
<label for="otp">รหัส OTP 6 หลัก / 6-digit code</label>
<input id="otp" name="otp" type="text" inputmode="numeric"
       autocomplete="one-time-code" pattern="\d{6}" maxlength="6" required>
```

## Performance as UX

**Core Web Vitals (stable, measured at the 75th percentile of real page loads, mobile and desktop separately):**

| Metric | Good | Needs improvement | Poor | Measures |
|---|---|---|---|---|
| LCP | ≤ 2.5 s | 2.5–4.0 s | > 4.0 s | When the main content renders |
| INP | ≤ 200 ms | 200–500 ms | > 500 ms | Worst-ish interaction latency (replaced FID in 2024) |
| CLS | ≤ 0.1 | 0.1–0.25 | > 0.25 | Unexpected layout movement |

LCP budget split (web.dev): TTFB ~40%, resource load delay <10%, resource load duration ~40%, render delay <10%.

**Design decisions that wreck the vitals → what to do instead**

| Decision | Breaks | Do instead |
|---|---|---|
| Autoplay hero video | LCP, data cost | Poster `<img>` is the LCP element (`fetchpriority="high"`); video `preload="none"`, starts after load, muted, short loop, no autoplay when `prefers-reduced-motion` or Save-Data |
| Lazy-loading the hero image | LCP | Never lazy-load the LCP image; `loading="lazy"` only below the fold |
| 3–4 web font families / weights | LCP, CLS | ≤2 families, variable fonts, WOFF2, subset + `unicode-range`; `font-display: optional` for body, `swap` for brand display; `size-adjust` on fallback face |
| Hero carousel / slider | LCP, CLS, INP | One static hero; if a slider is required, reserve height with `aspect-ratio`, first slide server-rendered |
| WebGL / 3D hero | LCP, INP, battery | Static poster first, init the canvas after LCP and on idle/visibility; cap DPR at 2; fallback for low-end devices (see `3d-webgl.md`) |
| Client-rendered hero text | LCP | Server-render/pre-render above-the-fold content |
| Late banners (cookie, promo, app-install) pushing content | CLS | Overlay with `position: fixed`; never insert above existing content |
| Ads/embeds/images without dimensions | CLS | `width`/`height` attributes or `aspect-ratio`; reserve slot min-height |
| Heavy JS on input (filters, search-as-you-type) | INP | Debounce, yield (`scheduler.yield()` where supported, else `setTimeout`), move work off the main thread, `content-visibility: auto` for long lists |

## Perceived performance

| Wait | Feedback (NN/g) |
|---|---|
| < 0.1 s | None needed; result is the feedback |
| 0.1–1 s | Subtle state change (pressed button, cursor); no spinner (<1 s spinners feel jarring) |
| 2–10 s | Skeleton for a full-page load (must mirror final layout); spinner for one module |
| > 10 s | Determinate progress bar + estimate + cancel; let users leave and notify on completion |

- **Optimistic UI** for low-risk writes (like, rename, reorder): update immediately, reconcile, roll back with an inline error.
- **View transitions** (same-document) are Baseline Newly available (2025-10-14): use for list→detail continuity; respect `prefers-reduced-motion`. Cross-document transitions are still Limited (no Firefox) → progressive enhancement only.
- **Prefetch on intent** (hover/`pointerdown` on a link) or Speculation Rules (Chromium-only, Limited) as an enhancement.

## PWA & installability

- **Chrome/Edge install prompt criteria:** HTTPS; manifest with `name` or `short_name`, icons **192px and 512px**, `start_url`, `display` = `standalone`/`fullscreen`/`minimal-ui`/`window-controls-overlay`; `prefer_related_applications` absent/false; user clicked once and spent ≥30 s. No service worker requirement is listed (web.dev, updated 2024-09-19) — still ship one for an offline page.
- **Safari 26 (iOS/iPadOS 26):** every site added to the Home Screen opens as a web app by default; no manifest or installability requirements. Still provide a manifest, an `apple-touch-icon`, and `theme-color`.
- **Install UX:** never prompt on first visit. Offer an "Install app" button in a menu or after a value moment (2nd session, completed task). Hide it when `matchMedia('(display-mode: standalone)')` matches.
- **Standalone mode needs its own chrome:** in-app back affordance, offline page, pull-to-refresh replacement, share via `navigator.share()`.

## Cookie consent (lawful, non-deceptive)

| Rule | Source |
|---|---|
| "Reject all" on the **first layer**, same size, colour, font and position weight as "Accept all" | CNIL; EDPB Cookie Banner Taskforce (most EU DPAs) |
| Reject must not be a text link while Accept is a button; no colour/contrast emphasis on Accept | EDPB taskforce |
| "Accept all" + "Settings" without reject = non-compliant (CNIL) | CNIL |
| No pre-ticked purposes; granular toggles on the second layer | GDPR consent; PDPA consent guidance (2022) |
| No cookie wall implying consent is required to use the site | EDPB |
| Withdrawal as easy as consent: persistent "Cookie settings" link in footer | GDPR / PDPA |
| Load no non-essential tags before consent | ePrivacy 5(3); PDPA prior consent (vendor guidance) |

UX shape: bottom-anchored overlay (`position: fixed`, max ~30% of viewport on mobile, no layout shift), plain-language purposes, buttons "Accept all" / "Reject all" / "Customize" in one row (stack equally on mobile). Do not re-ask after a refusal for ≥6 months (proposed in the EU Digital Omnibus; status as of mid-2026: under negotiation, browser-signal provision dropped by the Council — do not build on it yet). Thailand: PDPA requires explicit opt-in; use the same equal-weight pattern and Thai copy.

```html
<!-- Gate non-essential scripts until consent -->
<script type="text/plain" data-consent="analytics" src="https://example.com/analytics.js"></script>
<script>
  function enable(category) {
    document.querySelectorAll(`script[data-consent="${category}"]`).forEach(s => {
      const n = document.createElement('script'); n.src = s.src; document.body.append(n);
    });
  }
</script>
```

## Theme toggle (system / light / dark, no flash)

- Default to the OS setting; users expect sites to follow it and rarely look for an in-app toggle (NN/g). Offer a 3-state control — **System · Light · Dark** — as a segmented control or menu, in the header or settings. A 2-state switch loses the "follow system" state.
- Persist only an explicit choice. Apply it **before first paint** with a tiny inline script in `<head>` (not a deferred bundle).
- Declare `color-scheme` so form controls and scrollbars match. `light-dark()` is Baseline Newly available (2024-05-13; Widely ~2026-11) — fine with a fallback.
- Keep QR codes/barcodes black on white in dark mode; use PNG/SVG/WebP with transparency, not JPG.

```html
<head>
  <meta name="color-scheme" content="light dark">
  <meta name="theme-color" media="(prefers-color-scheme: light)" content="#ffffff">
  <meta name="theme-color" media="(prefers-color-scheme: dark)" content="#0b0b0f">
  <script>
    try {
      const t = localStorage.getItem('theme');           // 'light' | 'dark' | null (=system)
      if (t === 'light' || t === 'dark') document.documentElement.dataset.theme = t;
    } catch (_) {}
  </script>
  <style>
    :root { color-scheme: light dark; --bg: #fff; --fg: #111; }
    @media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { --bg: #0b0b0f; --fg: #eee; } }
    :root[data-theme="dark"] { color-scheme: dark; --bg: #0b0b0f; --fg: #eee; }
    :root[data-theme="light"] { color-scheme: light; }
    body { background: var(--bg); color: var(--fg); }
  </style>
</head>
```

## i18n: Thai + English, RTL basics

- **`lang` everywhere:** `<html lang="th">` (or `en`), and `lang` on inline runs in the other language. It drives fonts, line breaking, hyphenation and screen-reader voice.
- **Text expansion (IBM, English source):** ≤10 chars 200–300%, 11–20 180–200%, 21–30 160–180%, 31–50 140–160%, >70 ~130%. Buttons and tabs must grow (no fixed widths), labels may wrap to 2 lines.
- **Thai vertical space:** Thai needs ~150% of the vertical space of Latin text (W3C) because of stacked vowels and tone marks above and below. Use line-height ≥1.6 (1.7–1.8 for body), never clip with fixed heights or `overflow: hidden` on single-line labels; test with "ญี่ปุ่น", "ฎีกา", "ฤๅษี".
- **Thai line breaking:** no spaces between words; browsers break with a dictionary. Don't use `word-break: break-all`; insert `<wbr>` in long product names; `text-wrap: balance` (Newly available) helps headings.
- **Fonts:** pair a Thai face with matching x-height (e.g. Noto Sans Thai, IBM Plex Sans Thai, Sarabun, Anuphan) after the Latin face; subset Thai with `unicode-range: U+0E00-0E7F`. No letter-spacing or fake italics on Thai. Test looped (มีหัว) and loopless (ไม่มีหัว) styles with Thai readers; loopless faces read as modern UI, looped as formal/body.
- **Dates and numbers:** `Intl.DateTimeFormat('th-TH')` renders Buddhist Era years by default (2569 = 2026 CE); show BE to Thai users, store ISO. Currency `Intl.NumberFormat('th-TH', {style:'currency', currency:'THB'})` → ฿.
- **RTL:** `dir="rtl"` on `<html>`; use logical properties (`margin-inline-start`, `padding-inline`, `inset-inline-end`, `text-align: start`); mirror directional icons (back/forward arrows, progress) but not media-play icons, logos, or checkmarks.

## Baseline CSS in 2026 (what is safe)

Rule: **Widely available → use freely. Newly available → use if your audience allows (check analytics or a Browserslist Baseline query). Limited → only behind `@supports` with a working fallback.** Status from webstatus.dev on 2026-10-10.

| Feature | Status (date reached) | Guidance |
|---|---|---|
| Container size queries | Widely (2025-08-14) | Default for components |
| `:has()` | Widely (2026-06-19) | Parent/state styling, form validation states |
| CSS nesting | Widely (2026-06-11) | Use; keep ≤3 levels |
| `@layer` | Widely (2024-09-14) | reset < base < components < utilities |
| Subgrid | Widely (2026-03-15) | Card rows that align across columns |
| `svh/lvh/dvh` | Widely (2025-06-05) | `100svh` heroes |
| `oklch()` / `color-mix()` | Widely (2025-11-09) | Token math (`color.md`) |
| `<dialog>`, `inert` | Widely | Modals without libraries |
| Popover API | Newly (2025-01-27) | Menus, toasts, tooltips; light dismiss built in |
| `@starting-style` | Newly (2024-08-06) | Entry animations for popovers/dialogs |
| `light-dark()`, relative colour | Newly (2024) | Theme tokens |
| View transitions (same-document) | Newly (2025-10-14) | SPA route/list→detail transitions |
| `content-visibility` | Newly (2025-09-15) | Long pages/lists |
| Container style queries | Newly (2026-05-19) | Theme variants by container |
| `field-sizing: content` | Newly (2026-06-16) | Auto-growing textareas |
| Anchor positioning | **Limited** in web-features data (core shipped: Chrome 125, Safari 26, Firefox 147 on 2026-01-13) | Use for tooltips/menus with `@supports (anchor-name: --a)`; fallback = popover default placement |
| Scroll-driven animations | **Limited** (Chrome 115, Safari 26; Firefox still behind a flag in 152) | Decoration only, inside `@supports (animation-timeline: scroll())`; content must be visible without it |
| Cross-document view transitions | **Limited** (no Firefox) | Enhancement only |
| Customizable `<select>` (`appearance: base-select`) | **Limited** (Chrome 135, Safari 27) | Enhancement; native select fallback |
| `interpolate-size`, Speculation Rules | **Limited** (Chromium only) | Enhancement only |

```css
.menu-wrap { position: relative; }
.menu { position: absolute; inset-block-start: 100%; inset-inline-start: 0; }  /* fallback */
@supports (anchor-name: --a) {
  .trigger { anchor-name: --menu-btn; }
  .menu { position: fixed; inset: auto; position-anchor: --menu-btn;
          position-area: block-end span-inline-end; position-try-fallbacks: flip-block; }
}
@keyframes grow { from { scale: 0 1; } to { scale: 1 1; } }
@supports (animation-timeline: scroll()) {
  @media (prefers-reduced-motion: no-preference) {
    .progress { transform-origin: left; animation: grow linear both;
                animation-timeline: scroll(root); }
  }
}
```

## SEO-relevant UX

- One `<h1>` that states the page's topic; logical `h2`/`h3` outline; descriptive `<title>` (≤ ~60 chars) and meta description.
- Navigation and pagination as real `<a href>` links (crawlable, middle-click-able); avoid JS-only click handlers on links.
- Server-render or pre-render primary content; it also fixes LCP.
- Core Web Vitals are part of Google's page-experience assessment; treat them as UX targets first.
- Bilingual sites: separate URLs per language (`/th/`, `/en/`), `hreflang` alternates, a visible language switcher using language names in their own script ("ไทย", "English"), never flags alone.
- Don't block content behind interstitials on landing from search; banners must be dismissible and not cover the main content on mobile.

## Pitfalls

| Symptom | Cause | Fix |
|---|---|---|
| Page zooms when tapping an input on iPhone | Input font-size < 16px | `font-size: max(16px, 1rem)` on inputs |
| Theme flashes light then dark | Theme applied in a deferred bundle | Inline `<head>` script + `color-scheme` (recipe above) |
| LCP fine in lab, poor in field | Hero image discovered late (CSS background, JS-inserted) | `<img>` in HTML with `fetchpriority="high"` or `<link rel="preload">` |
| CLS from fonts | `font-display: swap` with mismatched fallback metrics | `size-adjust`/`ascent-override` on the fallback `@font-face`, or `optional` |
| Thai tone marks cut off in buttons/tabs | Fixed `height` + `overflow: hidden`, line-height ~1.2 | `min-height`, line-height ≥1.5 for UI labels, padding-block ≥0.5em |
| Mobile nav ignored | Hamburger hides everything | Combo nav: top 3–4 visible |
| Cookie banner pushes content down | Banner inserted in flow at top | `position: fixed` overlay, bottom-anchored |
| Scroll-linked effects missing in Firefox | Scroll-driven animations not shipped there | `@supports` guard; never hide content in the initial state |
| OTP autofill doesn't trigger | `type="number"` or 6 separate inputs without `autocomplete` | Single input with `autocomplete="one-time-code"` + origin-bound SMS |
| Sticky header covers anchor targets | Fixed header height | `scroll-padding-top: <header height>` on `html` |

## Sources

- Web Vitals — https://web.dev/articles/vitals
- How the CWV thresholds were defined — https://web.dev/articles/defining-core-web-vitals-thresholds
- Optimize LCP — https://web.dev/articles/optimize-lcp
- Font best practices — https://web.dev/articles/font-best-practices
- Baseline — https://web.dev/baseline
- webstatus.dev feature API (statuses, pulled 2026-10-10) — https://api.webstatus.dev/v1/features/container-queries
- Firefox 147 release notes — https://developer.mozilla.org/en-US/docs/Mozilla/Firefox/Releases/147
- Firefox 152 release notes — https://developer.mozilla.org/en-US/docs/Mozilla/Firefox/Releases/152
- WebKit features in Safari 26.0 — https://webkit.org/blog/17333/webkit-features-in-safari-26-0/
- Install criteria — https://web.dev/articles/install-criteria
- prefers-color-scheme — https://web.dev/articles/prefers-color-scheme
- SMS OTP form best practices — https://web.dev/articles/sms-otp-form
- Sign-in form best practices — https://web.dev/articles/sign-in-form-best-practices
- WCAG 2.2 Understanding 2.5.8 Target Size (Minimum) — https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html
- W3C i18n: Text size in translation — https://www.w3.org/International/articles/article-text-size
- NN/g: Hamburger menus and hidden navigation — https://www.nngroup.com/articles/hamburger-menus/
- NN/g: Finding navigation on mobile — https://www.nngroup.com/articles/find-navigation-mobile-even-hamburger/
- NN/g: Mega menus — https://www.nngroup.com/articles/mega-menus-work-well/
- NN/g: Breadcrumbs — https://www.nngroup.com/articles/breadcrumbs/
- NN/g: Scrolling and attention — https://www.nngroup.com/articles/scrolling-and-attention/
- NN/g: Designing effective carousels — https://www.nngroup.com/articles/designing-effective-carousels/
- NN/g: Response times — https://www.nngroup.com/articles/response-times-3-important-limits/
- NN/g: Skeleton screens — https://www.nngroup.com/articles/skeleton-screens/
- NN/g: Dark mode — https://www.nngroup.com/articles/dark-mode-users-issues/
- NN/g: Communicating trustworthiness — https://www.nngroup.com/articles/communicating-trustworthiness/
- CXL: High-converting landing page anatomy — https://cxl.com/blog/how-to-build-a-high-converting-landing-page/
- CXL: Social proof — https://cxl.com/blog/is-social-proof-really-that-important/
- Baymard: Cart abandonment rate — https://baymard.com/lists/cart-abandonment-rate
- Baymard: Checkout form fields — https://baymard.com/blog/checkout-flow-average-form-fields
- Smashing: Accessible tap target sizes — https://www.smashingmagazine.com/2023/04/accessible-tap-target-sizes-rage-taps-clicks/
- Android window size classes — https://developer.android.com/develop/ui/compose/layouts/adaptive/use-window-size-classes
- EDPB cookie banner taskforce (Hunton summary) — https://hunton.com/privacy-and-information-security-law/edpb-publishes-report-of-outcome-of-the-cookie-banner-taskforce
- EDPB Guidelines 03/2022 deceptive design patterns — https://www.edpb.europa.eu/our-work-tools/our-documents/guidelines/guidelines-032022-deceptive-design-patterns-social-media_en
- CNIL orders to comply (cookies) — https://www.cnil.fr/en/tag/Order+to+comply
- noyb on Digital Omnibus cookie provisions — https://noyb.eu/node/1654
- Tilleke & Gibbins: Thai PDPA consent guidelines — https://www.tilleke.com/insights/thailand-issues-guidelines-on-pdpa-consent-and-notification-requirements/5/
