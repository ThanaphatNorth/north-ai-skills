# Platform: Mobile (iOS, Android, cross-platform)

> Read when: designing or reviewing an iPhone/iPad or Android phone/tablet/foldable app (native, React Native/Expo, Flutter, SwiftUI, Compose) — navigation, bars, sheets, gestures, thumb reach, onboarding and permission prompts, push, mobile forms/OTP, splash, size classes, Dynamic Type/font scaling, or Thai-market specifics (LINE Login, PromptPay, Thai text).

**Contents:** Platform snapshot · iOS (Liquid Glass) · Android (Material 3 Expressive) · Cross-platform strategy · Thumb reach & ergonomics · Gestures · Onboarding & permissions · Push notifications · Mobile forms · Empty, offline, loading · Launch & splash · Tablets & foldables · Accessibility · Thai market · HTML mockups of app screens · Pitfalls · Sources

Siblings: `platform-web.md` (mobile web, PWA), `accessibility.md`, `motion.md`, `typography-layout.md`, `product-patterns.md` (onboarding flows, empty states), `design-systems.md` (tokens across platforms).

---

## Platform snapshot (as of 2026-10-10)

| Platform | Current state | What it forces on you |
|---|---|---|
| iOS 26 (Sept 2025) | Liquid Glass design language: floating glass bars, tab bar that minimizes, inset glass sheets, layered app icons | Rebuild with Xcode 26 → standard controls adopt it automatically; remove custom bar/sheet backgrounds |
| iOS 27 (announced WWDC 2026-06-08) | Liquid Glass refined for readability; user setting from "ultra clear" to "fully tinted"; refreshed app icons | Apps **linked against the iOS 27 SDK ignore `UIDesignRequiresCompatibility`** → no more opting out of Liquid Glass (Apple DTS). Test every screen at both glass extremes |
| Android 16 (API 36) | Google Play requires targetSdk 36 for new apps/updates from **2026-08-31** (extension to 2026-11-01) | Edge-to-edge with no opt-out; predictive back on by default (`onBackPressed` not called); orientation/resizability locks ignored on ≥600dp screens; `elegantTextHeight` ignored (affects **Thai**) |
| Material 3 Expressive | New components + springs + shape morph; Compose `material3` 1.4.0 stable, Expressive APIs graduating in 1.5.0 (beta as of this date) | Opt-in per component; check `@ExperimentalMaterial3ExpressiveApi` on your version |

---

## iOS (HIG, Liquid Glass)

### Liquid Glass rules
1. Glass is the **functional layer only** (tab bars, toolbars, sidebars, sheets, floating controls). Never put it on content (cards, list rows, backgrounds).
2. **Regular** glass by default (blurs + adjusts luminosity, legible text). **Clear** glass only over rich media (photos, video); if the media is bright add a dark dimming layer at **35% opacity** behind it.
3. Use it sparingly on custom controls; system components adopt it automatically. Delete custom bar backgrounds, darkening gradients and `presentationBackground` overrides — they fight the scroll edge effect.
4. Hierarchy through layout and grouping, not decoration. Monochrome bar icons; tint only to carry meaning (the one primary action).
5. **Concentric corners:** nested shapes use `.rect(corner: .containerConcentric)`; capsules near device edges on iPhone. Bordered buttons are capsules by default.
6. Scroll edge effect replaces dividers: **soft** (default, iOS) for buttons/inputs; **hard** for dense UIs, pinned headers, text-only controls. One per view; don't stack.
7. Glass appearance changes with Reduce Transparency, Increase Contrast and (iOS 27) the user's glass setting — never rely on what shows through.

### Bars and navigation

| Element | Rules (HIG + WWDC25) |
|---|---|
| **Tab bar** (iPhone, bottom, floating) | Navigation only, never actions. ≤5 tabs; single-word labels; filled SF Symbols. Keep visible on every top-level screen (a modal may cover it). Don't hide or disable tabs — explain empty states instead. Badges only for critical info. Optional minimize on scroll + bottom accessory (mini-player); dedicated **search tab at the trailing end** |
| Tab bar (iPad) | Sits near the top; `.sidebarAdaptable` lets it convert to a sidebar; let users customize |
| **Toolbar / nav bar** | ≤3 item groups; title <15 characters, not the app name; one primary action, `.prominent` style, **trailing**; standard Back/Close *symbols*, not "Back"/"Close" text; large title collapses on scroll |
| **Navigation stack** | Push for hierarchy; edge-swipe-back must always work; large title on top-level screens |
| **Sheets** | Detents: `.medium` (~half) and `.large`; custom heights allowed. Show the grabber on resizable sheets. **Cancel leading, Done trailing**; never Done alone. Multi-step: Back replaces Cancel, Done activates on last step. Swipe-down dismiss; confirm only if there are unsaved changes. One sheet at a time. Partial-height sheets render as inset glass; full height turns opaque |
| **Search** | iPhone: bottom of screen in the toolbar; iPad/Mac: top trailing. Make search a tab when it is central |
| Alerts / action sheets | Action sheets now spring from their source control; keep alerts for critical decisions |

### SF Pro and Dynamic Type (iOS default "Large" size)

| Style | pt / leading | Style | pt / leading |
|---|---|---|---|
| Large Title | 34 / 41 | Callout | 16 / 21 |
| Title 1 | 28 / 34 | Subheadline | 15 / 20 |
| Title 2 | 22 / 28 | Footnote | 13 / 18 |
| Title 3 | 20 / 25 | Caption 1 | 12 / 16 |
| Headline (semibold) | 17 / 22 | Caption 2 | 11 / 13 |
| Body | 17 / 22 | | |

- Body scales from 14pt (xSmall) to 53pt (AX5); Large Title to 60pt at AX5. Default body 17pt, absolute minimum 11pt. Support ≥200% enlargement; at accessibility sizes, stack horizontal rows vertically and let cells grow.
- Avoid Ultralight/Thin/Light weights. Use text styles (`.font(.body)`), never fixed sizes.

### Sizes and spacing
- Hit targets **44×44pt** default, 28×28pt absolute minimum; ~12pt padding around bezeled controls, ~24pt around borderless ones.
- Respect safe areas for controls; extend backgrounds under bars (`backgroundExtensionEffect()` mirrors + blurs imagery under sidebars/bars).
- Base layouts on **size classes** (compact/regular per axis), not on device model or orientation.

### App icons (iOS 26+)
- Layered: one background + 1–3 foreground layers, built in **Icon Composer** (ships with Xcode). Master 1024×1024px; provide unmasked square layers, vector (SVG/PDF) where possible.
- Appearances: default, dark, clear (light/dark), tinted (light/dark); the system generates any you omit — check them. Keep the same silhouette across variants; no text unless essential; no photos or UI screenshots.

### Widgets, Live Activities, haptics

| Surface | Numbers and rules |
|---|---|
| Widgets (iPhone) | Small 170×170pt, medium 364×170pt, large 364×382pt; Lock Screen circular 76×76pt, rectangular 172×76pt. Margins 16pt (11pt tight). Text ≥11pt. Buttons/toggles act without opening the app; tap elsewhere deep-links to the relevant screen. Refresh is budgeted — show "Updated 10:42" when data can be stale. Support light/dark/clear/tinted rendering |
| Live Activities | Tasks with a clear start and end, ≤8 hours. Presentations: compact (Dynamic Island, two sides), minimal (36.67–45pt), expanded (408×84–160pt on 430pt-wide phones), Lock Screen (14pt margin). Animations ≤2 s. End immediately when done (dismiss after 15–30 min). One button or toggle max. No ads. Medium weight or heavier text |
| Haptics | Standard controls already vibrate. Notification: success/warning/error; Impact: light/medium/heavy/rigid/soft; Selection: value changes. One meaning per pattern; make optional; never during camera/mic use |

### SwiftUI recipe (iOS 26+)

```swift
TabView {
    Tab("Home", systemImage: "house.fill") { HomeView() }
    Tab("Orders", systemImage: "bag.fill") { OrdersView() }
        .badge(orders.unreadCount)
    Tab(role: .search) { SearchView() }               // trailing search tab
}
.tabBarMinimizeBehavior(.onScrollDown)               // shrinks while reading
.tabViewBottomAccessory { NowPlayingBar() }          // optional persistent control

// Sheet with detents, glass by default (no custom background)
.sheet(isPresented: $showFilters) {
    FiltersView()
        .presentationDetents([.medium, .large])
        .presentationDragIndicator(.visible)
}

// Custom floating control: glass only on the functional layer
Button("Start ride") { start() }
    .buttonStyle(.glassProminent)                    // the one tinted primary action
```

---

## Android (Material 3 Expressive)

### What changed in 2025 (M3 Expressive)
- **New components:** button groups, FAB menu, loading indicator (shape-morphing), split button, toolbars (docked and floating, horizontal or vertical).
- **Updated:** app bars (flexible medium/large with subtitle), carousel, buttons, extended FAB, FABs, icon buttons, navigation bar (shorter), navigation rail (wider, expandable — replaces the drawer), progress indicators (wavy).
- **Shape:** library of 35 shapes + built-in shape morphing (e.g. pressed buttons, selection indicators).
- **Motion physics:** springs instead of duration/easing; *spatial* springs (position, size, shape — may overshoot) and *effects* springs (colour, opacity — no bounce). Two motion schemes: **expressive** (bouncier, default for Expressive) and **standard** (calmer, utilitarian screens). Respect "Remove animations".
- Use Expressive for consumer/emotional surfaces (media, social, onboarding); keep standard motion and denser components for productivity and finance flows.

### Component numbers (MDC-Android docs)

| Component | M3 | M3 Expressive |
|---|---|---|
| Navigation bar height | 80dp | 64dp; 3–5 destinations; icon 24dp; active indicator 56×32dp; selected label no longer bold; ≥600dp items lay out horizontally |
| Navigation rail width | 80dp | 96dp collapsed; 3–7 items; expanded rail (non-modal) replaces the navigation drawer |
| FAB | 56dp standard, 96dp large | **Medium FAB** added and recommended for most screens; small (40dp) deprecated; 16dp edge margin |
| Floating toolbar | — | 50% rounded; standard (surface container) or vibrant (primary container); hides on scroll (not while TalkBack is on) |
| Touch target | 48×48dp minimum (Material components pad themselves when interactive) | same |

### Edge-to-edge and back
- **Edge-to-edge:** enforced for targetSdk 35 on Android 15; **cannot opt out** at targetSdk 36 on Android 16. Draw behind status and navigation bars; pad interactive content with insets: `WindowInsets.safeDrawing` (most UIs), `safeGestures` (carousels, sheets, games), `imePadding()` for the keyboard. Material 3 `Scaffold` passes `innerPadding`.
- **Predictive back:** at targetSdk 36 on Android 16 the back-to-home, cross-task and cross-activity animations run by default; `onBackPressed()` is never called and `KEYCODE_BACK` isn't dispatched. Use `OnBackPressedCallback` / Compose `BackHandler` / `PredictiveBackHandler`. The manifest opt-out `android:enableOnBackInvokedCallback="false"` is temporary.
- Never intercept back to show "Are you sure you want to exit?" — only to close an open sheet, drawer, search or unsaved editor.

### Navigation by window size class (width)

| Class | Width | Navigation | Layout |
|---|---|---|---|
| Compact | < 600dp | Navigation bar (3–5) | Single pane |
| Medium | 600–839dp | Navigation rail | Single pane or list-detail |
| Expanded | 840–1199dp | Rail (expanded rail or permanent drawer for many sections) | List-detail / supporting pane |
| Large / XL | 1200–1599 / ≥1600dp | Expanded rail / drawer | 2–3 panes |

`NavigationSuiteScaffold` picks a bar when width *or* height is compact (or tabletop posture), otherwise a rail; override with `layoutType`.

### Dynamic color
Android 12+ supplies `dynamicLightColorScheme(context)` / `dynamicDarkColorScheme(context)` from the wallpaper. Use it for system-feel apps (utilities, launchers, notes); keep a brand scheme for brand-led apps (banking, commerce) and fall back to it below Android 12. Either way, generate all roles from tokens (see `color.md`).

### Compose recipe (material3 1.4+/1.5; Expressive APIs may need opt-in on your version)

```kotlin
class MainActivity : ComponentActivity() {
  override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    enableEdgeToEdge()                                    // before setContent
    setContent {
      val dark = isSystemInDarkTheme()
      val colors = if (Build.VERSION.SDK_INT >= 31)
        (if (dark) dynamicDarkColorScheme(this) else dynamicLightColorScheme(this))
        else (if (dark) BrandDark else BrandLight)
      @OptIn(ExperimentalMaterial3ExpressiveApi::class)
      MaterialExpressiveTheme(colorScheme = colors, motionScheme = MotionScheme.expressive()) {
        var dest by rememberSaveable { mutableStateOf(Dest.Home) }
        NavigationSuiteScaffold(navigationSuiteItems = {
          Dest.entries.forEach { d ->
            item(selected = d == dest, onClick = { dest = d },
                 icon = { Icon(d.icon, null) }, label = { Text(stringResource(d.label)) })
          }
        }) { Screen(dest) }                               // screens use Scaffold innerPadding
      }
    }
  }
}
```

---

## Cross-platform strategy

| Approach | Choose when | Cost |
|---|---|---|
| Platform-native per OS (SwiftUI + Compose) | Platform features matter (widgets, Live Activities, glass, predictive back), team can afford two UIs | Highest build cost, best fidelity |
| **Platform-adaptive** single codebase (Flutter, React Native/Expo, KMP + Compose Multiplatform) | Most product apps | Shared logic + brand; native chrome per OS |
| Brand-unified (same UI everywhere) | Games, media players, kiosk/POS, highly branded content apps | Risks "feels foreign"; still must keep the must-be-native list below |

**Must feel native on each OS (never brand these):** navigation and back (iOS edge swipe + top-left back; Android predictive back), tab/bottom bars' placement and behaviour, date/time pickers, share sheet, text input (keyboard types, autofill, selection menu, OTP), alerts/confirmations, switches/checkboxes, pull-to-refresh, scroll physics and overscroll, permission prompts, system fonts and text scaling, haptics.
**Safe to unify:** colour, illustration, iconography style inside content, cards, empty states, onboarding art, custom hero components, charts.

| Stack | Native-feel essentials |
|---|---|
| Flutter | Automatic: page transitions, back gestures, scroll physics, typography, haptics, text selection. Use `.adaptive()` constructors (`Switch`, `Slider`, `Checkbox`, `Radio`, `CircularProgressIndicator`, `RefreshIndicator`, `AlertDialog`) and `Icons.adaptive` |
| React Native / Expo | Native stack navigator (real UINavigationController/Fragment transitions); `react-native-safe-area-context` (core `SafeAreaView` is deprecated); Expo SDK 54+ is edge-to-edge by default and always on Android 16; keyboard via `KeyboardAvoidingView` or `react-native-keyboard-controller`; native `Modal` needs `statusBarTranslucent` + `navigationBarTranslucent` |
| SwiftUI / Compose | Mostly automatic; avoid hard-coded backgrounds on bars and fixed font sizes |

---

## Thumb reach & ergonomics

**Steven Hoober's field data (1,333 observations, 780 people touching the screen):** 49% one-handed, 36% cradled (one hand holds, other taps), 15% two-handed; ≈75% of touches are by a thumb; 67% of one-handed users use the right thumb; people change grip by task. Tablets were not included.
**Accuracy beats reach:** the centre of the screen is most accurate (targets can sit 7mm apart on centre); top and bottom edges need 10–12mm (≈11mm/31pt top, 12mm/34pt bottom, 7mm/20pt centre). Users stretch or re-grip to reach corners, so corner placement is a frequency question, not impossibility.

| Zone | Put here |
|---|---|
| Bottom-centre / lower third | Primary navigation (tab/nav bar), primary action (FAB, bottom CTA), frequent controls |
| Middle | Content, list rows (most accurate taps) |
| Top | Titles, infrequent actions (settings, filters, profile), back (iOS) — still reachable via edge swipe |
| Edges/corners | Nothing tiny; destructive actions away from frequent ones |

- Bottom edge also hosts the home indicator / gesture bar: keep controls inside the safe area and don't place swipe-up gestures there.
- One-handed large phones: offer bottom search (iOS 26 does this by default), bottom sheets for filters, reachable "Done" in sheets via detents.

## Gestures
- Standard gestures only for standard meanings: tap, swipe (reveal actions, dismiss, scroll), drag, long-press (context menu/preview), pinch zoom, rotate; iOS 3-finger swipe/shake = undo.
- **A custom gesture is a shortcut, never the only path** (HIG). Pair swipe-to-delete with an Edit mode or menu item; long-press menus with a visible "⋯" button.
- Never claim screen-edge gestures (iOS back swipe, Android back/home gestures). Horizontal carousels must start inset from the left edge or use `safeGestures` insets.
- Teach custom gestures in context (first-use hint, animated affordance), not in a tutorial carousel.

## Onboarding & permissions
1. **Value first.** Let people use the core feature before an account; ask to sign up at a value moment (saving, syncing, purchasing). Onboarding happens after launch, is brief, optional and interactive; prefer contextual tips (TipKit on iOS) over a slide deck.
2. **Ask for permissions in context**, when the feature that needs it is first used. Request at launch only if the app can't function at all without it.
3. **Pre-permission (priming) screen** only when the context doesn't already explain the request. Apple rules: **one button** labelled "Continue"/"Next" (never "Allow"), no Cancel, no imitation of the system alert. Android: show your rationale UI only when `shouldShowRequestPermissionRationale()` is true; include "No thanks".
4. **Purpose strings:** one active, specific sentence — "The app records during the night to detect snoring sounds." not "Microphone access is needed for a better experience."
5. **Two strikes on Android:** if the user denies the same permission more than once, the system dialog never appears again → degrade gracefully and offer a deep link to Settings.
6. App Tracking Transparency: no incentives, no fake alerts, no blocking features until "Allow".

## Push notifications
- **When to ask:** iOS — after the user does something that implies wanting updates (follows an order, subscribes). Android 13+ (`POST_NOTIFICATIONS`): trigger from a user action (bell icon, "Notify me") or after the 3rd–4th launch; check `areNotificationsEnabled()` before relying on push.
- **iOS interruption levels:** passive (no sound, digest-friendly), active (default), time-sensitive (relevant now or within the hour; breaks Focus), critical (entitlement; health/safety). Never use time-sensitive for marketing.
- Marketing pushes need separate, explicit opt-in with an in-app settings screen to change it. Provide per-category toggles (orders, messages, promos).
- Content: lead with the outcome ("Your order #4821 is out for delivery"), no clickbait; tapping opens the exact screen.

## Mobile forms

| Need | iOS (SwiftUI/UIKit) | Android (Compose/Views) | Web/RN |
|---|---|---|---|
| Email | `.keyboardType(.emailAddress)` `.textContentType(.emailAddress)` | `KeyboardType.Email`, autofill `ContentType.EmailAddress` | `type="email" autocomplete="email"` |
| Phone | `.phonePad`, `.telephoneNumber` | `KeyboardType.Phone` | `type="tel" autocomplete="tel"` |
| OTP | `.textContentType(.oneTimeCode)` | SMS Retriever / User Consent API | `autocomplete="one-time-code"` + SMS last line `@domain #123456` |
| Password | `.password` / `.newPassword` (strong-password suggestion) | autofill hints `password` / `newPassword` | `current-password` / `new-password` |

- **OTP:** one field with autofill support. If the design demands 6 boxes, back them with a single hidden input so paste and autofill still work. Auto-advance to submit when complete; offer "Resend in 0:30" and "Change number".
- **Keyboard avoidance:** focused field and primary button stay visible above the keyboard (SwiftUI does this by default; Compose `imePadding()` + edge-to-edge; RN `react-native-keyboard-controller`). Set the return key to "Next" between fields and "Done/Go" on the last.
- One column, labels above, input height ≥44pt / 48dp, 16px+ text on web inputs, show password toggle, never disable paste.

## Empty, offline, loading
- Every list has four states designed up front: first-use empty (explain + primary action), no results (echo query, suggest fixes), error (what happened + Retry), offline (see below). Details in `product-patterns.md`.
- **Offline:** show cached content with "Updated 10:42" instead of a blank screen; queue writes and mark them "Pending"; a non-blocking banner, not a modal; auto-retry on reconnect.
- Loading: skeletons for full screens, inline spinners for components, no spinner under ~1 s (see `platform-web.md` perceived performance).

## Launch & splash
- **iOS:** launch screen = a near-copy of the first screen (bars, background colour), **no text, no logo** unless the first screen has it. A branded splash, if any, belongs at the start of onboarding. Restore the previous state (tab, scroll position) on relaunch.
- **Android:** use the SplashScreen API (core-splashscreen for API 23+). Icon with background: 240×240dp inside a 160dp circle; without background: 288×288dp inside 192dp; optional branding image 200×80dp; animated icon ≤1,000 ms. Shown on cold/warm start, never on hot start. Dismiss only when the first screen is visually stable — no second spinner screen after it.
- Never add an artificial delay to "show the brand".

## Tablets & foldables
- iPad: size classes; tab bar at top convertible to a sidebar; split views (sidebar–list–detail); support pointer + keyboard shortcuts (see `platform-desktop.md`); iPadOS windowed mode means any width.
- Android: design for all width classes; **at targetSdk 36, orientation and resizability locks are ignored on screens ≥600dp** (games exempt; temporary opt-out ends at API 37) → no portrait-only tablet layouts. Save UI state for configuration changes.
- Canonical layouts: list-detail (mail, chat), supporting pane (editor + properties), feed (grid). Fold/hinge: never put content or controls across the hinge; tabletop posture = content top, controls bottom.

## Accessibility (mobile specifics; general rules in `accessibility.md`)
- **Text scaling:** iOS Dynamic Type up to AX5 (body 53pt); Android nonlinear font scaling up to 200% (Android 14+). Use text styles / `sp` for text **and** line height; never `sp` for padding. Test the largest size on the smallest phone.
- **Screen readers:** every icon-only control gets a label (`accessibilityLabel`, Compose `contentDescription`); group row content into one element; describe actions (`onClickLabel` → "Double tap to open article"); custom actions instead of swipe-only gestures.
- **Contrast:** 4.5:1 for text up to 17pt, 3:1 for ≥18pt or bold (Apple's thresholds). Verify over Liquid Glass with Increase Contrast and Reduce Transparency on.
- **Motion:** honour Reduce Motion / Remove animations — replace springs and parallax with fades.

## Thai market
- **LINE Login** is the expected social sign-in in Thailand: OAuth 2.0 + OpenID Connect (v2.1), native SDKs for iOS, Android, Flutter; users already logged in to LINE on the device are signed in to web apps automatically. Offer it beside Sign in with Apple / Google and phone OTP; check App Review Guideline 4.8 for when Sign in with Apple must accompany third-party logins (unverified this session).
- **PromptPay** (Bank of Thailand, since 2016): pay by phone number, citizen ID or account via Thai QR Payment scanned in a banking app; free up to 5,000 THB. UX: show the QR large with amount and payee name, "Save QR" to Photos (users scan from gallery in their bank app), countdown for expiry, and auto-detect payment completion instead of asking for a slip upload where the gateway allows.
- **Thai text:** needs ~150% of Latin vertical space; Android 16 ignores `elegantTextHeight` for apps targeting it and Google explicitly lists Thai among scripts whose layouts must be re-checked → test tall marks (ฎ ฐ ญ, ปี่ ฟื้น) for clipping in buttons, chips, tabs, single-line text fields. Let labels grow and wrap; don't size Thai UI from English strings.
- Dates: show Buddhist Era (พ.ศ.) when the user's calendar is Buddhist; store ISO/Gregorian.

## HTML mockups of app screens

When the deliverable is an app screen built as HTML (for review, a pitch or a usability test):
- **Real app at phone width, framed on desktop.** Below ~480 px the page *is* the app (full-bleed, safe-area padding via `env(safe-area-inset-*)`); above it, centre a 390×844 device frame and put a review panel beside it. Never ship the frame to phones.
- **Every state is addressable**: `?state=ideal|loading|empty|offline|error|permission-denied` and `?theme=light|dark` render that state directly (deep-linkable for reviews and for `scripts/shoot.mjs` jobs via `"query"`); the review panel only sets the same parameters.
- **Platform chrome is real**: status-bar spacing, a tab bar for top-level navigation only (create actions go to a FAB or a header button, per this file's navigation rules), sheets that trap focus and close on Esc/back, 44pt/48dp targets.
- **Fake data looks real**: real-length Thai names, dish/product names and counts; empty and very long variants; demo data labelled as such in the spec.
- **QA** at 390×844, 375×667 and 320×568 (short phones break first), light and dark, reduced motion.

## Pitfalls

| Symptom | Cause | Fix |
|---|---|---|
| iOS bars look muddy/double-blurred | Custom background or gradient behind toolbar/tab bar | Remove it; rely on scroll edge effect |
| Swipe-back stops working on iOS | Custom back button / hidden nav bar or a full-width horizontal gesture at the left edge | Use the system back button; inset horizontal gestures |
| Android app content under status/nav bar after targetSdk bump | Edge-to-edge enforced (35) / opt-out removed (36) | `enableEdgeToEdge()` + `safeDrawing`/Scaffold `innerPadding`, test 3-button and gesture nav |
| Back handling silently broken on Android 16 | Logic in `onBackPressed()` | Move to `OnBackPressedCallback`/`BackHandler` |
| Tablet shows stretched phone UI | Relied on portrait lock (ignored ≥600dp at API 36) | Adaptive layouts by window size class |
| Thai tone marks clipped on Android 16 | `elegantTextHeight` no longer honoured, tight fixed heights | `minHeight`, line height in sp, no fixed single-line heights |
| Permission dialog never shows again | User denied twice on Android | Detect, explain, deep-link to Settings |
| OTP autofill fails | Six separate inputs, wrong content type, SMS without origin line | Single input with one-time-code type + origin-bound SMS |
| Glass control unreadable over photo | Clear glass over bright media without dimming | Regular glass, or 35% dark dimming layer |
| Push opt-in rate collapses | Asked at first launch with no context | Ask after an intent signal; priming screen with one "Continue" button |

## Sources

- WWDC25 Build a SwiftUI app with the new design — https://developer.apple.com/videos/play/wwdc2025/323/
- WWDC25 Get to know the new design system — https://developer.apple.com/videos/play/wwdc2025/356/
- HIG Tab bars — https://developer.apple.com/design/human-interface-guidelines/tab-bars
- HIG Toolbars — https://developer.apple.com/design/human-interface-guidelines/toolbars
- HIG Sheets — https://developer.apple.com/design/human-interface-guidelines/sheets
- HIG Layout — https://developer.apple.com/design/human-interface-guidelines/layout
- HIG Typography — https://developer.apple.com/design/human-interface-guidelines/typography
- HIG Accessibility — https://developer.apple.com/design/human-interface-guidelines/accessibility
- HIG Materials — https://developer.apple.com/design/human-interface-guidelines/materials
- HIG App icons — https://developer.apple.com/design/human-interface-guidelines/app-icons
- HIG Gestures — https://developer.apple.com/design/human-interface-guidelines/gestures
- HIG Playing haptics — https://developer.apple.com/design/human-interface-guidelines/playing-haptics
- HIG Widgets — https://developer.apple.com/design/human-interface-guidelines/widgets
- HIG Live Activities — https://developer.apple.com/design/human-interface-guidelines/live-activities
- HIG Onboarding — https://developer.apple.com/design/human-interface-guidelines/onboarding
- HIG Launching — https://developer.apple.com/design/human-interface-guidelines/launching
- HIG Privacy — https://developer.apple.com/design/human-interface-guidelines/privacy
- HIG Managing notifications — https://developer.apple.com/design/human-interface-guidelines/managing-notifications
- TechCrunch: Apple tweaks Liquid Glass (WWDC 2026) — https://techcrunch.com/2026/06/08/apple-is-tweaking-its-controversial-liquid-glass-design
- Apple Developer Forums: UIDesignRequiresCompatibility and the iOS 27 SDK — https://developer.apple.com/forums/thread/832543
- Android 16 behavior changes — https://developer.android.com/about/versions/16/behavior-changes-16
- Google Play target API requirements — https://developer.android.com/google/play/requirements/target-sdk
- Compose window insets — https://developer.android.com/develop/ui/compose/system/insets
- Window size classes — https://developer.android.com/develop/ui/compose/layouts/adaptive/use-window-size-classes
- Build adaptive navigation — https://developer.android.com/develop/ui/compose/layouts/adaptive/build-adaptive-navigation
- Compose accessibility defaults (48dp) — https://developer.android.com/develop/ui/compose/accessibility/api-defaults
- Material 3 in Compose (dynamic color) — https://developer.android.com/develop/ui/compose/designsystems/material3
- Compose Material3 release notes — https://developer.android.com/jetpack/androidx/releases/compose-material3
- MDC-Android Navigation bar — https://raw.githubusercontent.com/material-components/material-components-android/master/docs/components/BottomNavigation.md
- MDC-Android Navigation rail — https://raw.githubusercontent.com/material-components/material-components-android/master/docs/components/NavigationRail.md
- MDC-Android FAB — https://raw.githubusercontent.com/material-components/material-components-android/master/docs/components/FloatingActionButton.md
- MDC-Android Floating toolbar — https://raw.githubusercontent.com/material-components/material-components-android/master/docs/components/FloatingToolbar.md
- 9to5Google: Material 3 Expressive components — https://9to5google.com/?p=671907
- Splash screens — https://developer.android.com/develop/ui/views/launch/splash-screen
- Android 14 features (nonlinear font scaling) — https://developer.android.com/about/versions/14/features
- Notification runtime permission — https://developer.android.com/develop/ui/views/notifications/notification-permission
- Request runtime permissions — https://developer.android.com/training/permissions/requesting
- Flutter automatic platform adaptations — https://docs.flutter.dev/ui/adaptive-responsive/platform-adaptations
- Expo: edge-to-edge on Android — https://expo.dev/blog/edge-to-edge-display-now-streamlined-for-android
- React Native SafeAreaView (deprecated) — https://reactnative.dev/docs/safeareaview
- Hoober: How do users really hold mobile devices? — https://www.uxmatters.com/mt/archives/2013/02/how-do-users-really-hold-mobile-devices.php
- Hoober: Design for fingers and thumbs instead of touch — http://www.uxmatters.com/mt/archives/2013/11/design-for-fingers-and-thumbs-instead-of-touch.php
- Smashing: Accessible tap target sizes — https://www.smashingmagazine.com/2023/04/accessible-tap-target-sizes-rage-taps-clicks/
- web.dev SMS OTP form — https://web.dev/articles/sms-otp-form
- W3C i18n text size in translation (Thai vertical space) — https://www.w3.org/International/articles/article-text-size
- LINE Login overview — https://developers.line.biz/en/docs/line-login/overview/
- Bank of Thailand: PromptPay — https://www.bot.or.th/en/financial-innovation/digital-finance/digital-payment/promptpay.html
