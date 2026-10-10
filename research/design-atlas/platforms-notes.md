# Platforms research notes (web, mobile, desktop)

Provenance record for `platform-web.md`, `platform-mobile.md`, `platform-desktop.md`.
Collected 2026-10-10. Every bullet carries the URL it came from. "(secondary)" = not a primary source.
Note: the shared WebSearch budget ran out mid-session; later facts come from direct WebFetch of primary URLs.

## Web: Core Web Vitals and loading

- Good thresholds: LCP ≤ 2.5 s, INP ≤ 200 ms, CLS ≤ 0.1; measured at the 75th percentile of page loads, split by mobile and desktop. All three listed "Stable"; stable metrics "won't change more than once per year". INP replaced FID in 2024. — https://web.dev/articles/vitals
- Poor thresholds LCP > 4 s, INP > 500 ms, CLS > 0.25 (from search snippet of the web.dev thresholds page; the vitals page shows these only as images). — https://web.dev/articles/defining-core-web-vitals-thresholds
- LCP sub-parts, recommended share: TTFB ~40%, resource load delay <10%, resource load duration ~40%, element render delay <10%. `fetchpriority="high"` on the LCP image (not more than 1–2 images); never lazy-load the LCP image; preload LCP resources discovered only from CSS/JS; avoid client-side-only rendering for the LCP element. — https://web.dev/articles/optimize-lcp
- Fonts: preconnect (+ `crossorigin` for font files); WOFF2 only; subset + `unicode-range`; fewer fonts / variable fonts / `system-ui`; `font-display: optional` best for CLS (~100 ms block, no swap); `swap` shows fallback then swaps (visible shift); `fallback` ~100 ms block + 3 s swap; `block` hides 2–3 s; combine `swap` for brand + `optional` for body; replace icon fonts with SVG; use `size-adjust` on the fallback face. — https://web.dev/articles/font-best-practices

## Web: perceived performance

- 0.1 s feels instantaneous; 1 s keeps flow of thought (show some indicator past 1 s); 10 s keeps attention (needs percent-done + way to interrupt). — https://www.nngroup.com/articles/response-times-3-important-limits/
- <1 s: no skeleton or spinner. 2–10 s: spinner (module) or skeleton (full page, used "exclusively for full-page loads"). >10 s: progress bar with estimate. Skeleton must mirror the final layout; frame-only skeletons read as broken; shimmer can distract. — https://www.nngroup.com/articles/skeleton-screens/

## Web: Baseline (webstatus.dev API pulled 2026-10-10)

Definition: Newly available = supported in all core browsers (Chrome desktop+Android, Edge, Firefox desktop+Android, Safari macOS+iOS); Widely available = 30 months after newly date; Baseline year targets (e.g. Baseline 2025); Browserslist and ESLint support Baseline queries. — https://web.dev/baseline

Raw statuses from `https://api.webstatus.dev/v1/features/<id>`:

| feature id | status | newly (low) | widely (high) | notes |
|---|---|---|---|---|
| container-queries | widely | 2023-02-14 | 2025-08-14 | |
| has | widely | 2023-12-19 | 2026-06-19 | |
| nesting | widely | 2023-12-11 | 2026-06-11 | |
| cascade-layers | widely | 2022-03-14 | 2024-09-14 | |
| subgrid | widely | 2023-09-15 | 2026-03-15 | |
| viewport-unit-variants (svh/lvh/dvh) | widely | 2022-12-05 | 2025-06-05 | |
| color-mix | widely | 2023-05-09 | 2025-11-09 | |
| oklab (oklab/oklch) | widely | 2023-05-09 | 2025-11-09 | |
| dialog | widely | 2022-03-14 | 2024-09-14 | |
| inert | widely | 2023-04-11 | 2025-10-11 | |
| color-scheme | widely | 2022-02-03 | 2024-08-03 | |
| prefers-color-scheme / prefers-reduced-motion | widely | 2020-01-15 | 2022-07-15 | |
| scroll-snap, font-display | widely | | | |
| view-transitions (same-document) | newly | 2025-10-14 | — | Firefox 144 |
| popover | newly | 2025-01-27 | — | |
| starting-style | newly | 2024-08-06 | — | |
| light-dark | newly | 2024-05-13 | — | |
| relative-color | newly | 2024-09-16 | — | |
| text-wrap-balance | newly | 2024-05-13 | — | |
| scrollbar-gutter | newly | 2024-12-11 | — | |
| fetch-priority | newly | 2024-10-29 | — | |
| content-visibility | newly | 2025-09-15 | — | Safari 26 |
| scrollend | newly | 2025-12-12 | — | Safari 26.2 |
| container-style-queries | newly | 2026-05-19 | — | Firefox 151 |
| field-sizing | newly | 2026-06-16 | — | Firefox 152 |
| overflow-anchor | newly | 2026-09-14 | — | Safari 27 |
| anchor-positioning | limited | — | — | web-features lists only Safari 27 as full; Chrome 125+/Firefox 147+ ship the core (see below) |
| anchor-positioning-animations | limited | | | Chrome 125, Safari 26 |
| cross-document-view-transitions | limited | | | Chrome 126, Safari 18.2, no Firefox |
| scroll-driven-animations | limited | | | Chrome 115, Safari 26; Firefox flag |
| customizable-select | limited | | | Chrome 135, Safari 27 |
| interpolate-size | limited | | | Chromium only |
| speculation-rules | limited | | | Chromium only |

- Firefox 147 (released 2026-01-13): "CSS anchor positioning is now enabled by default"; also `anchor-center`, `position-anchor: none`, view transition types (same-document only). — https://developer.mozilla.org/en-US/docs/Mozilla/Firefox/Releases/147
- Firefox 152 (2026-06-16): `field-sizing` enabled; scroll-driven animations still behind `layout.css.scroll-driven-animations.enabled`. — https://developer.mozilla.org/en-US/docs/Mozilla/Firefox/Releases/152
- Safari 26: anchor positioning (`position-area`, `anchor()`, `position-try`), scroll-driven animations (`animation-timeline: view()`, `animation-range`), `text-wrap: pretty`, `contrast-color()`, `progress()`, `margin-trim`. "By default, every website added to the Home Screen opens as a web app"; "there are now zero requirements for 'installability' in Safari"; manifest no longer required. — https://webkit.org/blog/17333/webkit-features-in-safari-26-0/
- (secondary, search summary) anchor positioning: Chrome/Edge 125 (2024), Safari 26 (Sept 2025), Firefox 147 (Jan 2026). — https://www.refontelearning.com/blog/css-anchor-positioning-reaches-baseline

## Web: navigation

- Hamburger study: navigation used in tasks — desktop hidden 27%, visible 48%, combo 50%; mobile hidden 57%, combo 86%. Time to nav: desktop hidden ~31 s vs 23 s combo / 26 s visible; mobile 26 vs 24 s. Discoverability >20% drop with hidden nav. Task difficulty (1–7): hidden 2.6, combo 2.3, visible 2.1. Task time: desktop ≥39% slower with hidden nav; mobile 15% slower vs combo. "Do not use hidden navigation (such as hamburger icons) in desktop user interfaces." Mobile: ≤4 top-level links → show them visibly. — https://www.nngroup.com/articles/hamburger-menus/
- Mobile hidden-nav study: SupermarketHQ (combo) 89% nav use; Bloomberg (hidden) 44%. Recommendations: visible nav for ~4–5 options or combo; bigger footprint; sticky; if hidden: prominent, distinct from logo, signifiers, text label. — https://www.nngroup.com/articles/find-navigation-mobile-even-hamburger/
- Mega menus: hover delay 0.5 s before showing; display within 0.1 s; close after pointer outside 0.5 s; handle diagonal movement; group via card sorting; don't hide search inside the menu; top-level items should link to real pages for accessibility. — https://www.nngroup.com/articles/mega-menus-work-well/
- Breadcrumbs: hierarchy not history; supplement nav; top below global nav; ">" separator; current page last, unlinked; start with Home; only link real pages; one canonical path; skip on flat sites; don't wrap on mobile; ≥1 cm tap targets; show last 1–2 levels on mobile. — https://www.nngroup.com/articles/breadcrumbs/

## Web: landing pages and conversion

- Eyetracking 2018: 57% of page-viewing time above the fold; 74% in the first two screenfuls (up to 2160 px). Keep primary CTA visible without scrolling; avoid false floors. — https://www.nngroup.com/articles/scrolling-and-attention/
- Carousels: auto-forward only if timed for reading (~3 words/second); never auto-forward on mobile; ≤5 frames; controls inside the carousel; show frame count/position; dots are weak cues; important content must exist elsewhere; animated ads looked at 27% of the time. — https://www.nngroup.com/articles/designing-effective-carousels/
- CXL (via search summary of cxl.com articles): value proposition = headline + sub-headline + maybe bullets that answer what it is, what you can do, how it helps, why choose you over alternatives (Peep Laja); flip vague headline with concrete subheadline (Oli Gardner, Unbounce); specific testimonials beat generic praise; place proof right after the value proposition, before pricing, near CTA; testimonials with photos more memorable than without, logos and numbers less so; social proof helps only when uncertainty is high, weak/irrelevant proof can hurt; Copyhackers: testimonials have not beaten regular headline copy in their tests. — https://cxl.com/blog/how-to-build-a-high-converting-landing-page/ , https://cxl.com/blog/is-social-proof-really-that-important/ , https://cxl.com/blog/saas-homepage-optimization/ (pages returned 403 to fetch; content from search summaries)
- NN/g trust: users suspect on-site testimonials are curated but still read them and cross-check third-party review sites; testimonials from external sites trusted more; B2B testimonials that move from doubt to confidence resonate; readers look at author's job title/affiliation. — https://www.nngroup.com/articles/communicating-trustworthiness/ , https://www.nngroup.com/articles/b2b-trust-from-b2c/ , https://www.nngroup.com/articles/social-proof-ux/ (from search summary)
- Baymard cart abandonment: average 70.22% from 50 studies (updated 2025-09-22). Reasons excluding "just browsing" (42%): extra costs 40%, delivery too slow 20%, didn't trust site with card 19%, forced account 18%, checkout too long/complicated 17%, errors/crashes 17%, returns policy 13%, couldn't see total up front 12%, card declined 10%, not enough payment methods 9%. Fixing checkout UX could lift conversion 35.26% for large e-commerce sites. Average US checkout shows 23.48 form elements (14.88 fields); ideal 12–14 elements (7–8 fields). — https://baymard.com/lists/cart-abandonment-rate
- Baymard 2024 benchmark: 11.3 fields average (11.8 in 2021, 12.7 in 2019); 8 fields enough for most; 5.1 steps avg. Single "Full Name" field (42% of testers typed full name into "First Name"); hide Address Line 2 behind link (30% stopped there); hide coupon field; billing = shipping by default; delay account creation to confirmation step; hide optional fields. — https://baymard.com/blog/checkout-flow-average-form-fields

## Web: forms

- OTP field: single `<input type="text" inputmode="numeric" autocomplete="one-time-code" pattern="\d{6}" required>`; avoid `type="number"`; origin-bound SMS last line `@example.com #123456`, ≤140 chars; WebOTP (`navigator.credentials.get({otp:{transport:['sms']}})`) on Chrome Android, HTTPS only. — https://web.dev/articles/sms-otp-form
- Sign-in forms: `autocomplete="username"` on email, `current-password` / `new-password`; stable name/id; visible labels, not placeholders; `<button>` with action label ("Sign in"); `type="button"` for show-password; no double entry of email/password; targets ≥44×44 CSS px; ~15 px padding mobile, ~10 px desktop; ~20 px text on mobile suggested. — https://web.dev/articles/sign-in-form-best-practices
- WCAG 2.2 SC 2.5.8 (AA): targets ≥24×24 CSS px or spaced so 24 px circles don't intersect; exceptions: equivalent, inline, UA control, essential. — https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html
- Smashing (Hoober book): 11 mm (31 pt / 42 px) top, 12 mm (34 pt / 46 px) bottom, as low as 7 mm (20 pt / 27 px) center; includes padding. Sticky bars 44–46 px. — https://www.smashingmagazine.com/2023/04/accessible-tap-target-sizes-rage-taps-clicks/

## Web: PWA, theme, i18n, consent

- Chrome install criteria: not installed; user clicked/tapped once and ≥30 s on page; HTTPS; manifest with `name`/`short_name`, icons 192 px and 512 px, `start_url`, `display` (fullscreen/standalone/minimal-ui/window-controls-overlay), `prefer_related_applications` absent/false. No service worker requirement listed (page updated 2024-09-19). — https://web.dev/articles/install-criteria
- Dark mode: `:root { color-scheme: light dark; }`; avoid FOUC via `Sec-CH-Prefers-Color-Scheme` client hint or hide until stylesheet loads; theme vars in light/dark stylesheets. — https://web.dev/articles/prefers-color-scheme
- NN/g dark mode: users ~1/3 dark, 1/3 light, 1/3 mixed (115 mobile users); mirror OS setting by default; in-app toggle OK but rarely sought (exceptions: readers, video); don't make users enable twice; OLED battery savings only (67% at full brightness → 14% at 30%); keep QR/barcodes black on white; use PNG/SVG/WebP not JPG for transparent graphics. — https://www.nngroup.com/articles/dark-mode-users-issues/
- Text expansion (IBM): ≤10 chars 200–300%, 11–20 180–200%, 21–30 160–180%, 31–50 140–160%, 51–70 151–170%, >70 130%. Thai text consumes ~150% of the vertical space of Latin text. — https://www.w3.org/International/articles/article-text-size
- CNIL: if "Accept all" exists, "Reject all" at same level and format; "Continue without accepting" link acceptable; "Accept all" + "Settings" alone insufficient; ~60 orders since May 2021; 2025 penalties €486,839,500 total (secondary summaries). EDPB cookie banner taskforce: majority of DPAs require reject on first layer; reject-only-as-link and colour/contrast highlighting of accept = deceptive; ideally same size/colour/font/contrast. EDPB Guidelines 03/2022 (final 24 Feb 2023) on deceptive design in social media. — https://www.cnil.fr/en/tag/Order+to+comply , https://hunton.com/privacy-and-information-security-law/edpb-publishes-report-of-outcome-of-the-cookie-banner-taskforce , https://www.edpb.europa.eu/our-work-tools/our-documents/guidelines/guidelines-032022-deceptive-design-patterns-social-media_en
- EU Digital Omnibus (COM(2025) 837, 19 Nov 2025): proposes moving cookie consent into GDPR Art. 88a (single-click refusal, 6-month no-reask) and browser signal Art. 88b; Council 5th compromise (June 2026) dropped 88b; not adopted as of late June 2026 (secondary: noyb, law firms). — https://noyb.eu/node/1654 , https://technologyquotient.freshfields.com/post/102m196/how-the-eu-commissions-digital-omnibus-could-reshape-cookie-compliance-in-europe
- Thailand PDPA: PDPC consent and notification guidelines issued 7 Sep 2022; cookies not named in PDPA but cookie data is personal data; vendors describe prior explicit opt-in, granular purposes, easy withdrawal (vendor recommendations, not PDPC text). PDPC consultation on new guidelines March 2026 (outcome unknown). — https://www.tilleke.com/insights/thailand-issues-guidelines-on-pdpa-consent-and-notification-requirements/5/ , https://cookiechimp.com/guides/regulations/th_pdpa

## Mobile: iOS 26 / iOS 27 and Liquid Glass

- WWDC25 "Build a SwiftUI app with the new design" (session 323): NavigationSplitView sidebar floats as Liquid Glass; `backgroundExtensionEffect()`; `inspector(isPresented:)`; iPhone tab bar floats; `tabBarMinimizeBehavior(.onScrollDown)`; `tabViewBottomAccessory {}` + `\.tabViewBottomAccessoryPlacement` (`.inline`); sheets `presentationDetents([.height(180), .medium, .large])`, partial sheets inset glass, opaque at full height, remove custom `presentationBackground`; zoom transition `matchedTransitionSource(id:in:)` + `navigationTransition(.zoom(sourceID:in:))`; toolbars grouped automatically; `ToolbarSpacer(.fixed)` / `ToolbarSpacer(.flexible, placement: .bottomBar)`; `DefaultToolbarItem(kind: .search, placement: .bottomBar)`; `sharedBackgroundVisibility(.hidden)`; `badge(_:)`; monochrome icons, tint only for meaning; scroll edge effect auto; `scrollEdgeEffectStyle(.hard, for: .top)`; search at bottom on iPhone, top-trailing on iPad/Mac; `searchToolbarBehavior(.minimize)`; `Tab(role: .search)`; bordered buttons capsule by default; macOS mini/small/medium rounded rect; `.buttonStyle(.glass)` / `.glassProminent`; slider ticks, `neutralValue`; `.rect(corner: .containerConcentric)`; `glassEffect()` (capsule default), `.regular.tint()`, `.regular.interactive()`, `GlassEffectContainer`, `glassEffectID(_:in:)`. — https://developer.apple.com/videos/play/wwdc2025/323/
- WWDC25 "Get to know the new design system" (356): typography bolder and left-aligned; fixed / capsule / concentric shapes; macOS mini/small/medium rounded-rect, large capsule, new X-Large uses glass; group bar items by function/frequency; don't group symbols with text; primary action (Done) separate and tinted; action sheets spring from source; modal tasks: glass + dimming; sheet dragged up becomes more opaque; scroll edge effect soft (iOS default) vs hard (macOS, pinned headers), one per view; sidebars inset glass; same symbols across devices. — https://developer.apple.com/videos/play/wwdc2025/356/
- HIG Tab bars: navigation not actions; avoid More overflow tab; ≤5 tabs default when customizable (iPadOS); single-word labels; filled SF Symbols; keep visible (modal may cover); don't hide/disable tabs; badges only critical; iOS tab bar floats on glass; minimize with accessory; exit by tapping tab or scrolling to top; search tab at trailing end; iPadOS tab bar near top, `sidebarAdaptable`; tvOS tab bar height 68 pt, 46 pt from top. Change log: Liquid Glass guidance 2025-07-28, updated 2025-12-16, terminology 2026-06-08. — https://developer.apple.com/design/human-interface-guidelines/tab-bars
- HIG Toolbars: ≤3 groups; title <15 chars, not app name; one primary action, `.prominent`, trailing; standard Back/Close symbols not text; macOS: every toolbar item also a menu bar command; leading items non-customizable. — https://developer.apple.com/design/human-interface-guidelines/toolbars
- HIG Sheets: medium ≈ half height, large full; custom detents; grabber in resizable sheets; Cancel leading, Done trailing; always pair Done with Cancel/Back; multi-step: Back replaces Cancel; swipe-down dismiss, confirm if unsaved; one sheet at a time; macOS: sheets always modal; change 2026-03-24 button placement. — https://developer.apple.com/design/human-interface-guidelines/sheets
- HIG Layout: base layouts on size classes, not device; extend background under bars; scroll edge effect instead of opaque bar backgrounds; change log 2026-09-09 "Updated guidance to reflect current best practices". — https://developer.apple.com/design/human-interface-guidelines/layout
- HIG Typography: iOS Large: Large Title 34/41, Title1 28/34, Title2 22/28, Title3 20/25, Headline 17/22 semibold, Body 17/22, Callout 16/21, Subhead 15/20, Footnote 13/18, Caption1 12/16, Caption2 11/13. xSmall Body 14/19, Large Title 31/38; AX1 Body 28/34; AX5 Body 53/62, Large Title 60/70. macOS: Large Title 26/32, Title1 22/26, Title2 17/22, Title3 15/20, Headline 13/16 bold, Body 13/16, Callout 12/15, Subheadline 11/14, Footnote 10/13, Caption1 10/13, Caption2 10/13. Default/min: iOS 17/11, macOS 13/10, tvOS 29/23, visionOS 17/12, watchOS 16/12. macOS has no Dynamic Type. Avoid Ultralight/Thin/Light. SF Pro 17 pt tracking −0.43 pt. — https://developer.apple.com/design/human-interface-guidelines/typography
- HIG Accessibility: control size default/min — iOS/iPadOS 44×44 / 28×28 pt; macOS 28×28 / 20×20; tvOS 66/56; visionOS 60/28; watchOS 44/28. Padding ~12 pt around bezeled elements, ~24 pt around non-bezeled. Text enlargeable ≥200%. Contrast 4.5:1 up to 17 pt, 3:1 at 18 pt or bold. — https://developer.apple.com/design/human-interface-guidelines/accessibility
- HIG Materials: Liquid Glass only in functional layer, not content; sparingly; Regular vs Clear; Clear only over visually rich backgrounds; add 35% dark dimming layer under clear glass if content is bright; appearance changes with Reduce Transparency / Increase Contrast and user's preferred glass look. — https://developer.apple.com/design/human-interface-guidelines/materials
- HIG App icons: layered (background + foregrounds), Icon Composer (in Xcode, developer.apple.com/icon-composer); 1024×1024 px iOS/iPadOS/macOS (watchOS 1088); appearances default, dark, clear light/dark, tinted light/dark; system generates missing; provide unmasked layers; vector (SVG/PDF); text only if essential; change 2026-06-08 "Refined guidance for Liquid Glass". — https://developer.apple.com/design/human-interface-guidelines/app-icons
- HIG Gestures: standard tap, swipe, drag, touch and hold, double tap, zoom, rotate; 3-finger swipe undo/redo; shake undo; custom gestures only as shortcuts, never only way; don't conflict with system edge gestures. — https://developer.apple.com/design/human-interface-guidelines/gestures
- HIG Haptics: system controls already play haptics; Notification (success/warning/error), Impact (light/medium/heavy/rigid/soft), Selection; use for documented meanings; optional; don't overuse. — https://developer.apple.com/design/human-interface-guidelines/playing-haptics
- HIG Widgets: iPhone small 170×170, medium 364×170, large 364×382 pt; accessory circular 76×76, rectangular 172×76; margins 16 pt (11 pt tight); text ≥11 pt; buttons/toggles act without launching; refresh is budgeted; appearances light/dark/clear/tinted; rendering full color / accented / vibrant. — https://developer.apple.com/design/human-interface-guidelines/widgets
- HIG Live Activities: ≤8 hours; compact / minimal (36.67–45 pt detached) / expanded (408×84–160 pt on 430-pt-wide iPhones; 371 on 393-pt) / Lock Screen (14 pt margin); Dynamic Island corner radius 44 pt; animations ≤2 s; custom dismissal 15–30 min, stays ≤4 h on Lock Screen; no ads; ideally one button or toggle; medium weight or heavier text. — https://developer.apple.com/design/human-interface-guidelines/live-activities
- HIG Onboarding: after launch, brief, optional, interactive; prefer contextual tips (TipKit); permissions in onboarding only if app can't function without; defer nonessential setup; optional tutorial not auto-reshown. — https://developer.apple.com/design/human-interface-guidelines/onboarding
- HIG Launching: launch screen nearly identical to first screen, no text, no logo unless part of first screen; splash (if any) at start of onboarding; restore previous state. — https://developer.apple.com/design/human-interface-guidelines/launching
- HIG Privacy: ask when feature first used; purpose strings active and specific ("The app records during the night to detect snoring sounds."); pre-alert screen: one button, not labelled "Allow" ("Continue"/"Next"), no Cancel; ATT: no incentives, no imitation alerts. — https://developer.apple.com/design/human-interface-guidelines/privacy
- HIG Managing notifications: interruption levels passive / active (default) / time sensitive (within the hour; breaks Focus) / critical (entitlement); marketing needs explicit opt-in; never time-sensitive for marketing; in-app settings for choice. — https://developer.apple.com/design/human-interface-guidelines/managing-notifications
- iOS 27 (WWDC 2026-06-08): Liquid Glass "foundations" updated for readability; user slider from "ultra clear to fully tinted"; refreshed app icons; customizations apply in third-party apps at launch. — https://techcrunch.com/2026/06/08/apple-is-tweaking-its-controversial-liquid-glass-design
- `UIDesignRequiresCompatibility` ignored when linking against iOS 27 SDK (Xcode 27); honored for apps linked against iOS 26 SDK even on iOS 27 devices (Apple DTS reply). — https://developer.apple.com/forums/thread/832543
- Developer report: tab bar glass may not refresh after tab switch until scroll (forum, unconfirmed by Apple). — https://developer.apple.com/forums/thread/834761

## Mobile: Android 15/16, Material 3 Expressive

- Android 16 (API 36) behavior changes: `windowOptOutEdgeToEdgeEnforcement` disabled; predictive back system animations on by default, `onBackPressed` not called, `KEYCODE_BACK` not dispatched (temporary opt-out `android:enableOnBackInvokedCallback="false"`); on sw ≥600dp orientation/resizability/aspect-ratio restrictions ignored (games exempt; temporary opt-out `PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY`, gone at API 37); `elegantTextHeight` ignored — adapt layouts for Arabic, Lao, Myanmar, Tamil, Gujarati, Kannada, Malayalam, Odia, Telugu, **Thai**. — https://developer.android.com/about/versions/16/behavior-changes-16
- Google Play: from 2026-08-31 new apps and updates must target API 36 (extension to 2026-11-01). — https://developer.android.com/google/play/requirements/target-sdk
- Insets: Android 15 + targetSdk 35 = edge-to-edge enforced; `WindowInsets.safeDrawing` (most common), `safeGestures`, `safeContent`; Scaffold helps. — https://developer.android.com/develop/ui/compose/system/insets
- Window size classes (width dp): compact <600, medium 600–839, expanded 840–1199, large 1200–1599, extra-large ≥1600; height compact <480, medium 480–899, expanded ≥900; `currentWindowAdaptiveInfo(supportLargeAndXLargeWidth = true)`. — https://developer.android.com/develop/ui/compose/layouts/adaptive/use-window-size-classes
- NavigationSuiteScaffold: navigation bar if width or height compact or tabletop posture; rail otherwise; override with `layoutType` (e.g. NavigationDrawer at expanded). — https://developer.android.com/develop/ui/compose/layouts/adaptive/build-adaptive-navigation
- Touch targets 48dp minimum; Material components pad to 48dp when interactive; `sizeIn(minWidth = 48.dp, minHeight = 48.dp)`; `onClickLabel` changes TalkBack hint. — https://developer.android.com/develop/ui/compose/accessibility/api-defaults
- Dynamic color Android 12+; `dynamicLightColorScheme(context)` / `dynamicDarkColorScheme`; fallback custom schemes. — https://developer.android.com/develop/ui/compose/designsystems/material3
- compose-material3: latest stable 1.4.0, 1.5.0-beta01 in beta (as of fetch); FloatingActionButtonMenu graduated 1.5.0-alpha19 (2026-05-06); SplitButton alpha20 (2026-05-19); ButtonGroup + HorizontalFloatingToolbar alpha22 (2026-06-17); TopAppBar/FlexibleBottomAppBar alpha23 (2026-07-01); LoadingIndicator/MaterialShapes stable promotion reverted at one point. — https://developer.android.com/jetpack/androidx/releases/compose-material3
- M3 Expressive (9to5Google): new — button groups, FAB menu, loading indicators, split button, toolbars; updated — app bars, carousel, common buttons, extended FAB, FABs, icon buttons, navigation bar, navigation rail, progress indicators (listed 14 though "fifteen" claimed); 35 new shapes + shape morph; motion physics with spatial springs and effects springs. — https://9to5google.com/?p=671907
- Spring token values from community implementation (not official; unverified): expressive spatial default stiffness 380 damping 0.8, fast 800/0.6, slow 200/0.8; standard spatial default 700/0.9, fast 1400/0.9, slow 300/0.9; standard effects default 1600/1, fast 3800/1, slow 800/1. — https://pub.dev/documentation/m3e_slider/0.0.2/common_m3e_common/M3EMotion-class.html (secondary)
- MDC-Android docs: nav bar 80dp (M3) / 64dp (Expressive); 3–5 items; icon 24dp; indicator 56×32dp; Expressive selected label not bold, active label colour secondary; ≥600dp horizontal item layout. — https://raw.githubusercontent.com/material-components/material-components-android/master/docs/components/BottomNavigation.md
- Nav rail: 80dp → 96dp Expressive; 3–7 items collapsed; expanded rail replaces nav drawer in Expressive. — https://raw.githubusercontent.com/material-components/material-components-android/master/docs/components/NavigationRail.md
- FAB: standard 56dp, large 96dp, medium added in Expressive (recommended for most), small (40dp) deprecated; 16dp margin example. — https://raw.githubusercontent.com/material-components/material-components-android/master/docs/components/FloatingActionButton.md
- Floating toolbar: horizontal or vertical; standard (surfaceContainer) or vibrant (primaryContainer); pairs with FAB; `HideViewOnScrollBehavior` (disabled when TalkBack on). — https://raw.githubusercontent.com/material-components/material-components-android/master/docs/components/FloatingToolbar.md
- Top app bar: medium/large deprecated → medium flexible / large flexible with subtitle; scroll flags. — https://raw.githubusercontent.com/material-components/material-components-android/master/docs/components/TopAppBar.md
- Splash screen API: branded image 200×80dp; icon with background 240×240dp (in 160dp circle); without background 288×288dp (in 192dp circle); AVD 432dp; animation ≤1000 ms; not shown on hot start; dismiss only when visually stable. — https://developer.android.com/develop/ui/views/launch/splash-screen
- Android 14 nonlinear font scaling to 200%; use sp for text and lineHeight; not for padding; `TypedValue.applyDimension` / `deriveDimension`. — https://developer.android.com/about/versions/14/features
- POST_NOTIFICATIONS: ask from a user action or after 3rd–4th launch; show rationale only when `shouldShowRequestPermissionRationale()` true; check `areNotificationsEnabled()`. — https://developer.android.com/develop/ui/views/notifications/notification-permission
- Runtime permissions: "if the user taps Deny for a specific permission more than once ... the user will no longer see the system permissions dialog". — https://developer.android.com/training/permissions/requesting

## Mobile: cross-platform

- Flutter auto adaptations: page transitions, back (Android button / iOS edge swipe), scroll physics, scrollbars, typography, icons (`Icons.adaptive`), haptics, text editing. `.adaptive()` constructors: Switch, Slider, CircularProgressIndicator, RefreshIndicator, Checkbox, Radio, AlertDialog. — https://docs.flutter.dev/ui/adaptive-responsive/platform-adaptations
- Expo: SDK 53 edge-to-edge default for new projects; SDK 54 default for all; SDK 54 apps on Android 16 always edge-to-edge; use KeyboardAvoidingView or react-native-keyboard-controller; built-in Modal needs `statusBarTranslucent` + `navigationBarTranslucent`. — https://expo.dev/blog/edge-to-edge-display-now-streamlined-for-android
- React Native core `SafeAreaView` deprecated → react-native-safe-area-context. — https://reactnative.dev/docs/safeareaview

## Mobile: ergonomics (Hoober)

- 1,333 observations, 780 touching: one-handed 49%, cradled 36%, two-handed 15%; one-handed right thumb 67%; cradled thumb 72%; two-handed portrait 90%. — https://www.uxmatters.com/mt/archives/2013/02/how-do-users-really-hold-mobile-devices.php
- Centre most accurate: targets spaced as close as 7 mm on centre; top/bottom edges 10–12 mm; users shift grip to reach; thumb-sweep charts don't correlate with accuracy data. — http://www.uxmatters.com/mt/archives/2013/11/design-for-fingers-and-thumbs-instead-of-touch.php
- People change grip by task; not tablets; Hoober calls it non-scientific (secondary). — https://mobiforge.com/design-development/designing-touch-thumb-and-finger-sized-design

## Mobile: Thai market

- LINE Login: OAuth 2.0 + OpenID Connect (v2.1); auto login for users logged in to LINE on device (no login screen); email/password, QR code, SSO "Continue as"; SDKs iOS, Android, Unity, Flutter. — https://developers.line.biz/en/docs/line-login/overview/
- PromptPay (BOT): launched 2016; identifiers citizen ID, mobile number, bank account; one phone number → one account; Thai QR Payment scanned in mobile banking apps; fees free ≤5,000 THB; most banks waived digital fees since 2018. — https://www.bot.or.th/en/financial-innovation/digital-finance/digital-payment/promptpay.html

## Desktop: macOS

- Menu bar order App, File, Edit, Format, View, app-specific, Window, Help; disable rather than hide unavailable items; App menu: About, Settings…, Services, Hide, Hide Others, Show All, Quit; Edit: Undo/Redo name the target ("Undo Paste"); View: Show/Hide Tab Bar, Toolbar, Sidebar, Enter Full Screen (title reflects state); Window menu even with one window; commands left out of menus can't have shortcuts and are less accessible; menu bar extras: menu bar height 24 pt, show a menu not popover, user opt-in, also Dock menu; iPadOS menu bar (added 2025-06-09). — https://developer.apple.com/design/human-interface-guidelines/the-menu-bar
- Keyboards: full standard shortcut table (⌘, settings, ⌘. cancel, ⌘? help, ⌃⌘F full screen, ⌥⌘I inspector, ⌥⌘T toolbar, ⌘` window cycle, ⇧⌘Z redo, ⌘E use selection for find, ⌘J scroll to selection …); modifier order Control, Option, Shift, Command; prefer Command; avoid Control; system localizes/mirrors shortcuts. — https://developer.apple.com/design/human-interface-guidelines/keyboards
- Windows: main/key/inactive states; avoid custom frames; bottom bars rare. — https://developer.apple.com/design/human-interface-guidelines/windows
- Settings: App menu Settings… ⌘,; toolbar pane switcher, noncustomizable; title = pane name (or "App Name Settings"); reopen last pane; dim minimize/maximize; window sizes to pane; don't duplicate system settings. — https://developer.apple.com/design/human-interface-guidelines/settings
- Sidebars: ≤2 levels; don't hide by default; macOS row sizes small/medium/large set in General settings; icons use accent colour; sidebars float in Liquid Glass; extend content beneath with `backgroundExtensionEffect()`; change 2026-06-08 icon colours. — https://developer.apple.com/design/human-interface-guidelines/sidebars
- Split views: 2–3 panes; persistent selection highlight; set min/max pane sizes; multiple ways to reveal hidden panes; thin 1 pt divider preferred. — https://developer.apple.com/design/human-interface-guidelines/split-views

## Desktop: Windows 11 / Fluent

- Mica: opaque, wallpaper-tinted backdrop for long-lived windows; samples wallpaper once; base layer, visible in title bar; Mica Alt for tabbed title bars (WinAppSDK 1.1+, Windows 11 22000+); solid fallback when transparency off, battery saver, low-end hardware, inactive window, Windows < 22000; apply backdrop once; content layer `LayerFillColorDefaultBrush`. — https://learn.microsoft.com/en-us/windows/apps/design/style/mica
- Acrylic: background acrylic for transient light-dismiss surfaces (context menus, flyouts); in-app acrylic for supporting overlapping panes; not on large backgrounds; no adjacent acrylic panes (seam); no accent-coloured text over acrylic; GPU-intensive, off in Battery Saver. — https://learn.microsoft.com/en-us/windows/apps/design/style/acrylic
- Title bar: standard 32 px; 48 px when it holds a search box or person picture; icon 16×16 at 16 px from edge; title 16 px from icon, caption style; empty space draggable; double-click maximize/restore; right-click → system menu; inactive = semi-transparent; caption glyphs E921/E922/E923/E8BB. — https://learn.microsoft.com/en-us/windows/apps/design/basics/titlebar-design
- Type ramp (Segoe UI Variable): Caption 12/16, Body 14/20, Body Strong 14/20 semibold, Body Large 18/24, Subtitle 20/28, Title 28/36, Title Large 40/52, Display 68/92 epx; min 14 px semibold / 12 px regular; sentence case; no bold/italic in ramp (use semibold); 50–60 characters per line; Thai UI font Leelawadee UI. — https://learn.microsoft.com/en-us/windows/apps/design/signature-experiences/typography
- Spacing: 8 epx between buttons, button↔flyout, control↔header; 12 epx control↔label and between content areas; 16 epx surface edge↔text; 48 epx indent inside expander; 32 epx icons in multi-line lists. — https://learn.microsoft.com/en-us/windows/apps/design/basics/content-basics
- Geometry: 8 px windows, flyouts, dialogs; 4 px controls and bars (ToolTip 4 px); 0 px when maximized/snapped or touching edges; `ControlCornerRadius` 4, `OverlayCornerRadius` 8. — https://learn.microsoft.com/en-us/windows/apps/design/signature-experiences/geometry
- NavigationView: Top for ≤5 equally important categories; Auto = Left ≥1008 px, LeftCompact 641–1007, LeftMinimal ≤640. — https://learn.microsoft.com/en-us/windows/apps/develop/ui/controls/navigationview
- CommandBar: primary commands in importance order, dynamic overflow; ≤4 primary at 320 epx; icons 20 px primary / 16 px overflow; labels right on large windows; Accept/Yes/OK left of Reject/No/Cancel; avoid sticky. — https://learn.microsoft.com/en-us/windows/apps/design/controls/command-bar

## Desktop: GNOME, frameworks, patterns

- GNOME header bars: start = primary actions (new, add, back); centre = title or view switcher; end = menus; few controls; leave drag space; tooltips. — https://developer.gnome.org/hig/patterns/containers/header-bars.html
- GNOME adaptive: support 1024×600 px desktop minimum; phone-capable apps scale down to 360×294 px. — https://developer.gnome.org/hig/guidelines/adaptive.html
- GNOME menus: primary menu `open-menu-symbolic` at end of header bar, tooltip "Main Menu"; standard items Preferences, Keyboard Shortcuts, Help, About App (always); no Close/Quit; menus 3–12 items, submenus 3–6, no nesting. — https://developer.gnome.org/hig/patterns/controls/menus.html
- Electron title bar: `titleBarStyle` hidden / hiddenInset / customButtonsOnHover; `trafficLightPosition`; `titleBarOverlay` {color, symbolColor, height} on Windows/Linux; `app-region: drag`. — https://www.electronjs.org/docs/latest/tutorial/custom-title-bar
- Electron nativeTheme: `themeSource` system/light/dark drives renderer `prefers-color-scheme`; `shouldUseHighContrastColors`; `prefersReducedTransparency`; `updated` event. — https://www.electronjs.org/docs/latest/api/native-theme
- Electron updates: Squirrel autoUpdater; update.electronjs.org (public GitHub, macOS code signing required); update-electron-app checks at startup and every 10 min, background download, restart dialog; on `update-downloaded` show "Restart"/"Later"; skip in dev (`app.isPackaged`). — https://www.electronjs.org/docs/latest/tutorial/updates
- Tauri 2: `decorations: false` + `data-tauri-drag-region` (child elements need their own) + window permissions; macOS transparent title bar via `TitleBarStyle::Transparent` keeps native behaviours. — https://v2.tauri.app/learn/window-customization/
- Command palette (Superhuman): one global shortcut (⌘K), works everywhere, toggles and restores focus; every action has a command; icons; fuzzy search with typo tolerance; synonyms showing preferred title; relevance ranking + usage; context-aware. — https://blog.superhuman.com/how-to-build-a-remarkable-command-palette/
- Figma keyboard shortcuts panel: Control Shift ? (Mac) / Ctrl Shift ? (Windows). — https://help.figma.com/hc/en-us/articles/360040328653-Use-shortcuts-and-quick-actions

## Could not verify (left out or marked)
- Official m3.material.io spring token values (only community packages).
- Exact WinUI compact-density control heights (doc URL 404).
- Linear / Notion specific shortcuts and sync architecture (docs fetch 404 / no mention).
- Bank of Thailand anti-scam app rules (search budget exhausted).
- Final adoption of EU Digital Omnibus cookie provisions.
