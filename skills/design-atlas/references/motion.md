# Motion design for UI

> Read when: adding or reviewing any animation, transition, hover or press effect, loading state, page/route transition, spring or easing choice, text animation, or motion tokens; choosing between CSS, WAAPI, Motion, GSAP, Lottie, Rive, Reanimated, SwiftUI or Compose; handling `prefers-reduced-motion`; or debugging janky animation. For scroll-linked effects and parallax, open `scroll-parallax.md`. For WebGL/3D, `3d-webgl.md`.

**Contents:** 1 Purpose and the noise rule · 2 Principles · 3 Durations · 4 Easing and springs · 5 Choreography and stagger · 6 Micro-interactions · 7 Loading and optimistic UI · 8 Page and route transitions · 9 Hover, magnetic and cursor effects · 10 Text animation · 11 Tool selection · 12 Reduced motion · 13 Performance · 14 Motion tokens · 15 Native mobile notes · Pitfalls · Sources

## 1. Purpose and the noise rule

Every animation must serve one of these purposes. Name it before you build it.

| Purpose | User question it answers | Typical example | Typical duration |
|---|---|---|---|
| Feedback | "Did my input register?" | button press scale, toggle knob slide, copy ✓ | 70–150 ms |
| Orientation / continuity | "Where did that come from / go?" | card expands into detail (container transform), sheet slides from its edge | 250–500 ms |
| Focus / attention | "What should I look at now?" | new item flashes in, error field shakes once | 150–400 ms |
| Hierarchy / relationship | "What belongs together, what came first?" | parent moves first, children follow (stagger) | +30–50 ms per step |
| Brand / delight | "What is this product like?" | onboarding illustration, success confetti | ≤ 1000 ms, rare |

**Noise rule.** Cut or shorten a motion when any of these is true:
- You cannot name its purpose from the table.
- It blocks input: the user must wait for it before acting (anything > 300 ms on a frequent action).
- It runs on a high-frequency action (typing, list navigation, tab switching) and lasts more than ~200 ms. The more often people see it, the shorter and subtler it must be (NN/g).
- It moves something next to text the user is reading.
- It loops or auto-plays for more than 5 s with no pause control (WCAG 2.2.2, Level A).
- It is "expressive" motion used on routine task UI. Reserve expressive motion for "occasional, important moments" (Carbon).

## 2. Principles

**Disney's 12, translated to UI** (IxDF mapping, condensed):

| Principle | UI use |
|---|---|
| Squash and stretch | Press state: scale 0.96–0.98 on `:active`; elastic pull on overscroll |
| Anticipation | Hover lift or icon nudge that previews what a click will do |
| Staging | One focal motion per moment; everything else still or subtle |
| Pose to pose | Define start/end states (tokens), let the engine tween; that is how component states work |
| Follow-through / overlap | Lead element moves first (image), title then body follow 30–60 ms later |
| Slow in / slow out | Always ease; linear only for progress, loops and scroll-scrubbed motion |
| Arcs | Large moves (FAB to sheet, item to cart) travel on a curve, not a straight diagonal |
| Secondary action | Confetti after a completed long flow; checkmark draw after the button morph |
| Timing | Duration carries meaning: bigger/farther = longer; upload animation tied to real progress |
| Exaggeration | Overshoot (spring bounce) only on playful, low-frequency moments |
| Solid drawing | Shadows and perspective stay physically consistent during motion |
| Appeal | Personality via mascots, Lottie/Rive illustrations, in brand surfaces only |

UX-in-Motion's 12 usability principles (Willenskomer) name the UI-specific tools: easing, offset and delay, parenting, transformation, value change, masking, overlay, cloning, obscuration, parallax, dimensionality, dolly and zoom. His blunt rule: "You want all motion to always ease."

**Material transition patterns.** Pick by the relationship between the two states:

| Pattern | Use when | Example |
|---|---|---|
| Container transform | One element with a visible container becomes another | card → detail page, FAB → sheet, search bar → search screen |
| Shared axis (x / y / z) | States have a spatial or navigational order | onboarding steps (x), stepper (y), parent → child (z, scale + fade) |
| Fade through | Destinations are unrelated | bottom-nav tabs, account switch |
| Fade | Element appears/disappears within the current screen | dialog, menu, snackbar, tooltip |

On the web, implement container transform and shared element with the View Transitions API (§8) or Motion `layoutId`; shared axis with translate ±30 px + opacity; fade through with old fades out fast, new fades in after it (sequential, not overlapping).

## 3. Durations

| Category | Duration | Examples |
|---|---|---|
| Micro feedback | 70–150 ms | press, toggle, checkbox, hover color |
| Small component change | 150–250 ms | tooltip, menu open, chip select, accordion of a few lines |
| Medium / partial screen | 250–400 ms | modal enter, bottom sheet, drawer, card expand |
| Large / full-screen | 400–500 ms (up to 600) | route transition, container transform to full screen |
| Ambient / brand | 700–1000 ms+ | background dimming, onboarding, ambient carousel |

Rules that change numbers:
- **Distance and area scale duration.** Something that travels across a large screen needs longer than a 40 px nudge, or it looks like a teleport (M3: "duration should increase as the area or traversal of an animation increases").
- **Enter longer than exit.** Example: popup 300 ms in, 200–250 ms out (NN/g). M1: enter 225 ms, exit 195 ms.
- **Device:** tablet ≈ +30% vs phone (300 → 390 ms); wearable ≈ −30% (300 → 210 ms); desktop faster and simpler, 150–200 ms for most UI transitions (Material, legacy guidance still valid as a rule of thumb).
- **Ceiling:** 400 ms is "very slow" for UI responding to input (NN/g); past 500 ms it feels like a drag. Prefer the shortest duration that is not jarring.
- **Scroll-linked motion has no duration.** Progress comes from scroll position (see `scroll-parallax.md`).

M3 duration tokens (ms): short1 50 · short2 100 · short3 150 · short4 200 · medium1 250 · medium2 300 · medium3 350 · medium4 400 · long1 450 · long2 500 · long3 550 · long4 600 · extra-long1 700 · extra-long2 800 · extra-long3 900 · extra-long4 1000. M3 examples: selection control 200 ms standard; FAB → sheet 400 ms emphasized; card → full screen 500 ms emphasized; ambient carousel 1000 ms.

## 4. Easing and springs

**Which curve:**
- Entering the screen → decelerate (fast start, soft landing).
- Leaving the screen → accelerate (soft start, fast exit). Exits can be shorter.
- Moving within the screen → standard (or emphasized for hero moments).
- Linear → only for progress bars, spinners, marquees, color cycling and anything scrubbed by scroll (`ease: "none"` in GSAP).
- Interruptible, gesture-driven or physical (drag release, sheet, toggle thumb) → spring.

**Material 3 easing (as of 2026; M3 now calls these "legacy" in favour of springs, but they remain the best web defaults):**

```css
/* Names = templates/tokens-starter.css (the single source of truth); M3 names in comments */
:root {
  --ease-standard:        cubic-bezier(0.2, 0, 0, 1);       /* standard */
  --ease-out:             cubic-bezier(0, 0, 0, 1);         /* standard-decelerate: entering */
  --ease-in:              cubic-bezier(0.3, 0, 1, 1);       /* standard-accelerate: exiting */
  --ease-emphasized-out:  cubic-bezier(0.05, 0.7, 0.1, 1);  /* emphasized-decelerate: hero entrances */
  --ease-emphasized-in:   cubic-bezier(0.3, 0, 0.8, 0.15);  /* emphasized-accelerate: emphasized exits */
  /* M3 "emphasized" is a path, not a cubic; use --ease-standard as its CSS fallback.
     M2 "standard" / FastOutSlowIn, if matching an older app: cubic-bezier(0.4, 0, 0.2, 1) */
}
```

Emphasized is a two-segment path (`M 0,0 C 0.05,0, 0.133333,0.06, 0.166666,0.4 C 0.208333,0.82, 0.25,1, 1,1`) with no single cubic-bezier. M3 says to use Standard as the CSS fallback. If you need the real shape, sample it into CSS `linear()` (Baseline, all browsers since Dec 2023).

Carbon alternative: productive standard `cubic-bezier(0.2, 0, 0.38, 0.9)`, expressive standard `cubic-bezier(0.4, 0.14, 0.3, 1)`.

**Springs.** A spring has no fixed duration; it settles. Prefer springs when motion can be interrupted mid-flight (a retarget keeps velocity) or follows a finger. Damping ratio ζ = damping / (2·√(stiffness·mass)): ζ = 1 is critically damped (no overshoot), ζ < 1 bounces.

M3 Expressive motion physics (announced 2025-05-13; Compose `MotionScheme`, Material3 1.5.0+). Two schemes × spatial/effects × three speeds. Spatial springs (position, size, rotation, corner radius) may overshoot; effects springs (color, opacity) never do.

| Token (dampingRatio / stiffness) | Expressive | Standard | Web equivalent (expressive) |
|---|---|---|---|
| fast spatial (switches, buttons) | 0.6 / 800 | 0.9 / 1400 | `cubic-bezier(0.42, 1.67, 0.21, 0.90)` 350 ms |
| default spatial (sheet, drawer) | 0.8 / 380 | 0.9 / 700 | `cubic-bezier(0.38, 1.21, 0.22, 1.00)` 500 ms |
| slow spatial (full screen) | 0.8 / 200 | 0.9 / 300 | `cubic-bezier(0.39, 1.29, 0.35, 0.98)` 650 ms |
| fast effects | 1.0 / 3800 | 1.0 / 3800 | `cubic-bezier(0.31, 0.94, 0.34, 1)` 150 ms |
| default effects | 1.0 / 1600 | 1.0 / 1600 | `cubic-bezier(0.34, 0.80, 0.34, 1)` 200 ms |
| slow effects | 1.0 / 800 | 1.0 / 800 | `cubic-bezier(0.34, 0.88, 0.34, 1)` 300 ms |

Standard-scheme spatial web curve: `cubic-bezier(0.27, 1.06, 0.18, 1)` at 350 / 500 / 750 ms.

Platform spring defaults (verify after upgrades, they change):

| Engine | Defaults / presets |
|---|---|
| SwiftUI | `.default` (iOS 17+) = spring response 0.55, dampingFraction 1.0 (was easeInOut before iOS 17). `spring(response: 0.5, dampingFraction: 0.825)`. `.smooth` bounce 0, `.snappy` bounce 0.15, `.bouncy` bounce 0.3 (all duration 0.5 s). `interactiveSpring` response 0.15, damping 0.86. `Spring(duration:bounce:)`: duration = perceived settle time; bounce 0 critical, < 0 overdamped |
| Compose | `spring()` = DampingRatioNoBouncy 1.0 + StiffnessMedium 1500. Damping: Low 0.75, Medium 0.5, High 0.2 bouncy. Stiffness: High 10000, Medium 1500, MediumLow 400, Low 200, VeryLow 50 |
| Motion (web, v14) | spring stiffness 100, damping 10, mass 1 (source). `{ type: "spring", visualDuration: 0.3, bounce: 0.25 }` is the readable form. When `type` is unset: transforms use spring (stiffness 500, damping 25), opacity/color use a 0.3 s tween |
| Reanimated 4 | `withSpring` damping 120, stiffness 900, mass 4 (v3 was 10 / 100 / 1, still exported as `Reanimated3DefaultSpringConfig`). `withTiming` 300 ms `Easing.inOut(Easing.quad)` |

Defaults for a product (pick once, put in tokens; ranges follow M3 standard vs expressive): UI controls ζ ≈ 0.9–1.0 (no visible bounce); playful/brand surfaces ζ ≈ 0.6–0.8; never bounce color or opacity.

CSS spring without JS: sample a real spring into `linear()` points (the values below only illustrate the shape: overshoot past 1, settle back):

```css
.sheet { transition: transform 500ms linear(0, 0.36 10%, 0.82 22%, 1.04 34%, 1.06 42%, 1.01 58%, 0.99 74%, 1); }
```

## 5. Choreography and stagger

- **One primary actor.** Decide what moves first and most; supporting elements move less, later or not at all.
- **Parent before children.** Container expands, then content fades in (offset 30–80 ms). Reverse order on exit, faster.
- **Stagger lists** at 20–50 ms per item and cap the total added delay at ~250 ms: stagger the first 6–8 visible items, show the rest together. A 30-item cascade is noise. (House rule, consistent with NN/g's 100–400 ms total budget.)
- **Shared direction.** Elements in one transition move along one axis; do not slide some up and some sideways.
- **Do not overlap two big motions** (a page slide while a modal scales). Sequence them or drop one.
- **Worked example** (Next.js view transitions guide, directional route change): old page fades out 150 ms ease-in while sliding 60 px over 400 ms ease-in-out; new page fades in 210 ms ease-out after a 150 ms delay while sliding the same 400 ms. Shared-element morph: 400 ms with a 3 px blur at 30% to hide interpolation artifacts.

## 6. Micro-interactions

Saffer's structure: **trigger → rules → feedback → loops and modes.** Spec each one in that order.

| Part | Decide | Example (bookmark button) |
|---|---|---|
| Trigger | Manual (tap, hover, keypress) or system (data arrives, time passes) | tap on icon, or `B` shortcut |
| Rules | What happens, what cannot happen, what state persists | toggles saved state; offline → queue and mark pending |
| Feedback | Visual, sound, haptic; also the absence of feedback | icon fills with 150 ms scale 0.9→1; count +1; haptic light on mobile |
| Loops and modes | Repetition over time, alternate modes | pending state pulses until synced; long-press opens "save to list" mode |

Recipes:

```css
/* Press feedback: instant, compositor-only, no layout shift */
.btn { transition: transform 120ms var(--ease-standard), background-color 150ms linear; }
.btn:active { transform: scale(0.97); }
@media (hover: hover) and (pointer: fine) {
  .btn:hover { background-color: var(--btn-hover); }
}
```

- Feedback must start in the same frame as the input (CSS `:active`, not after a fetch). Network results get their own, second feedback.
- Haptics (iOS `UIImpactFeedbackGenerator`, Android `HapticFeedbackConstants`) pair with the visual, never replace it.

## 7. Loading and optimistic UI

| Expected wait | Show |
|---|---|
| < 100 ms | Nothing; just the result |
| 100 ms – 1 s | Nothing new for the page; button-level busy state if the user is waiting on that button. Delay any spinner ~300 ms so fast responses never flash it (house rule) |
| 1–2 s | Inline spinner or skeleton for the affected region |
| 2–10 s | Skeleton for full-page/region loads; spinner for a single module (card, video) |
| > 10 s | Determinate progress bar with estimate and a cancel action; let people leave and get notified |

Sources: NN/g response-time limits (0.1 s / 1 s / 10 s) and skeleton-screen thresholds; the 1–2 s row and spinner delay are house rules filling the gap.

- **Skeleton** = static or gently pulsing blocks matching the final layout exactly (same heights, so no layout shift). Shimmer can distract; under reduced motion make it static. "Frame-only" skeletons (header + footer, empty body) read as broken.
- **Once shown, keep a spinner ≥ ~400 ms** to avoid a flicker (house rule).
- **Optimistic UI** for reversible, high-success actions (like, star, reorder, rename, toggle): apply instantly, reconcile on response, roll back with a visible message on failure. React 19: `useOptimistic`. Do not use it for payments, deletes or anything whose failure is likely or costly.
- **Determinate beats indeterminate** whenever you know progress. Never fake progress that stalls at 99%.

## 8. Page and route transitions (View Transitions API)

**Support (as of 2026-10):**

| Feature | Chrome/Edge | Safari | Firefox |
|---|---|---|---|
| Same-document `document.startViewTransition()` + `view-transition-name` | 111 | 18 | 144 (Baseline Newly available 2025-10-14) |
| Transition types + `view-transition-class` (used by React's integration) | 125 | recent versions | class: 144; types: not in 144's initial release |
| Cross-document `@view-transition { navigation: auto; }`, `pageswap`/`pagereveal` | 126 | 18.2 | partial since 144 (caniuse) |
| `<link rel="expect" blocking="render">` | 124 | no | no |

Firefox 144 also shipped `view-transition-name: match-element` and `:active-view-transition`; check MDN for the other engines before relying on `match-element`.

Cross-document transitions are an Interop 2026 focus area. Treat every view transition as progressive enhancement: without support, the DOM simply swaps.

**Same-document (SPA) helper:**

```ts
export function transition(update: () => void | Promise<void>) {
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (!document.startViewTransition || reduce) return void update();
  return document.startViewTransition(update);
}
```

```css
.card-thumb { view-transition-name: var(--vt-name); }  /* set a unique name per item, e.g. style="--vt-name: photo-42" */
::view-transition-group(*) { animation-duration: 300ms; animation-timing-function: var(--ease-standard); }
@media (prefers-reduced-motion: reduce) {
  ::view-transition-group(*), ::view-transition-old(*), ::view-transition-new(*) { animation: none !important; }
}
```

**Cross-document (MPA):** both pages, same origin:

```css
@view-transition { navigation: auto; }
.site-header { view-transition-name: site-header; }   /* persists instead of crossfading */
```

It does not run for URL-bar navigations, bookmarks or reloads, and Chrome skips it when the navigation takes > 4 s.

Rules:
- Each `view-transition-name` must be unique on the page at capture time; give names only to elements that should morph (thumbnail ↔ hero, header).
- Snapshots are images: a morph between different aspect ratios stretches. Wrap images in a box with fixed `aspect-ratio` and `object-fit: cover`.
- Named participants are not hit-testable during the transition; keep transitions ≤ 400 ms and avoid naming controls people click rapidly.

**Next.js (16.4, App Router) + React 19.3:** works without config. `import { ViewTransition } from 'react'`. Same `name` on thumbnail and hero = shared-element morph. It activates only for Transitions, `<Suspense>` reveals and `useDeferredValue`; route navigations are transitions, plain `setState` is not. Directional slides: `<Link href="/x" transitionTypes={['nav-forward']}>` plus a page-level `<ViewTransition enter={{ 'nav-forward': 'nav-forward', 'nav-back': 'nav-back', default: 'none' }} exit={{ … }} default="none">`. Put that wrapper in each `page.tsx`, not in a layout (layouts persist, so enter/exit never fire). For a named morph with `default="none"`, keep an explicit `share` prop or the morph silently stops. Never call `document.startViewTransition` yourself inside React.

**Astro:** add `<ClientRouter />` from `astro:transitions` for SPA-style navigation, or use plain `@view-transition` CSS for native MPA transitions with zero JS. Directives: `transition:name`, `transition:animate="fade|slide|initial|none"`, `transition:persist`. The router disables animations under reduced motion. Bundled scripts run once, so re-initialise GSAP/observers on `astro:page-load` and kill them on `astro:before-swap`.

## 9. Hover, magnetic and cursor effects

- Gate all hover effects: `@media (hover: hover) and (pointer: fine)`. Hover must never be the only way to reveal an action (touch has no hover).
- **Hover lift:** translateY −2 to −4 px + shadow change, 150–200 ms. Do not scale cards in dense grids (neighbours overlap).
- **Magnetic button** (house defaults): pull the element 20–35% of the pointer offset, capped at ~12 px, spring back on leave. Use only on 1–3 hero CTAs, never in forms, toolbars or lists.

```ts
import gsap from 'gsap';
export function magnetic(el: HTMLElement, strength = 0.3) {
  if (!matchMedia('(hover: hover) and (pointer: fine) and (prefers-reduced-motion: no-preference)').matches) return;
  const inner = el.firstElementChild as HTMLElement;             // animate a child, never the laid-out element
  const xTo = gsap.quickTo(inner, 'x', { duration: 0.4, ease: 'power3.out' });
  const yTo = gsap.quickTo(inner, 'y', { duration: 0.4, ease: 'power3.out' });
  el.addEventListener('pointermove', (e) => {
    const r = el.getBoundingClientRect();
    xTo(gsap.utils.clamp(-12, 12, (e.clientX - (r.left + r.width / 2)) * strength));
    yTo(gsap.utils.clamp(-12, 12, (e.clientY - (r.top + r.height / 2)) * strength));
  });
  el.addEventListener('pointerleave', () => { xTo(0); yTo(0); });
}
```

- **Custom cursor:** portfolio/brand sites only. Keep the native cursor (or `cursor: auto`) over text, inputs, links' focus outlines and anything in a form; never hide the system cursor without a same-position replacement updated every frame; disable on touch, coarse pointers and reduced motion; drive it with `transform: translate3d` from a rAF loop, not `left/top`.
- Skip all three on dashboards, productivity apps, checkout and settings.

## 10. Text animation

**GSAP is 100% free** since 3.13 (blog 2025-04-29), after Webflow acquired GreenSock in fall 2024: all former Club plugins (SplitText, MorphSVG, ScrollSmoother, etc.) ship in the public `gsap` package and are allowed in commercial work under GSAP's own no-charge licence (not MIT). Current: gsap 3.15.0 (2026-04-13, adds `easeReverse`, deprecates `yoyoEase`).

SplitText was rewritten in 3.13 (half the size): `mask` for clip reveals, `autoSplit` to re-split on font load and resize, `onSplit` to (re)create animations, `aria: "auto"` by default (aria-label on the parent, aria-hidden on pieces).

```ts
import gsap from 'gsap';
import { SplitText } from 'gsap/SplitText';
gsap.registerPlugin(SplitText);

SplitText.create('.headline', {
  type: 'lines',            // split only what you animate: lines < words < chars in cost
  mask: 'lines',            // overflow-clip wrapper per line
  autoSplit: true,          // re-split when fonts load or width changes
  onSplit: (self) =>        // return the tween so SplitText reverts/re-syncs it on re-split
    gsap.from(self.lines, { yPercent: 100, duration: 0.7, ease: 'expo.out', stagger: 0.08 }),
});
```

Rules:
- Animate headlines and short display text only. Never split body copy or anything users read while it moves.
- Wait for fonts (`autoSplit`, or `document.fonts.ready`) or line breaks will be wrong.
- `aria: "auto"` drops nested links/markup from the accessible name; for rich text use `aria: "none"` plus a visually hidden copy.
- **Thai / complex scripts:** never split Thai by `chars`: tone marks and above/below vowels (e.g. ่ ้ ิ ุ) are separate code points and will detach from their base consonant. Split Thai by words, and get word boundaries from `Intl.Segmenter('th', { granularity: 'word' })` (Thai has no spaces), then feed them to SplitText via `prepareText`/`wordDelimiter` or your own spans. Test with real copy.

## 11. Tool selection

| Tool (as of 2026-10) | Best for | Avoid for |
|---|---|---|
| CSS transitions / `@keyframes` | State changes, hover/press, enter animations, loops; `@starting-style` for enter-from-`display:none` | Sequences with runtime values, physics, interruption with velocity |
| CSS scroll-driven animations | Scroll-linked progress, reveals, parallax without JS (see `scroll-parallax.md`) | Firefox stable (needs fallback), pinning with complex timelines |
| WAAPI (`el.animate`) | JS-controlled tweens with promises (`.finished`), cancel/reverse, no library | Large choreographies |
| Motion (`motion` 14.x, formerly Framer Motion; `motion/react`) | React enter/exit (`AnimatePresence`), layout animations (`layout`, `layoutId`), gestures, springs, `useScroll` | Non-React projects needing heavy timelines (use GSAP) |
| GSAP 3.15 (+ ScrollTrigger, SplitText, Flip, MorphSVG, Draggable) | Complex timelines, scroll pinning/scrub, text splitting, SVG morphing, framework-agnostic | Simple hover/press states (CSS is enough) |
| Lottie (dotLottie, `@lottiefiles/dotlottie-web`) | Designer-made After Effects vector animations, mostly playback | Rich interactive state (Rive is stronger); heavy files (check size) |
| Rive (`@rive-app/*`) | Interactive, state-machine-driven animations with data binding; one file for web, iOS, Android, Flutter, RN, Unity | Plain one-shot icons where CSS/Lottie suffice |
| React Native Reanimated 4.x | RN UI-thread animations, gestures (with Gesture Handler), CSS-style animations/transitions API | Apps still on the old architecture (stay on 3.x) |
| SwiftUI animations | Native iOS/macOS state animations, springs, `matchedGeometryEffect`, `PhaseAnimator`, `KeyframeAnimator` | Pixel-scrubbed timelines |
| Jetpack Compose animation | `animate*AsState`, `AnimatedVisibility`, `updateTransition`, `SharedTransitionLayout`, M3 `MotionScheme` springs | — |

Default decision: CSS first; Motion if React needs enter/exit/layout; GSAP if there are timelines, scroll pinning or text splitting; Rive when designers own interactive animation.

## 12. Reduced motion

`prefers-reduced-motion: reduce` comes from OS settings (macOS/iOS Reduce Motion, Windows Animation effects off, Android Remove animations). Large scaling, zooming, panning, parallax and spinning are the vestibular triggers. WCAG 2.3.3 (AAA) asks that interaction-triggered motion can be disabled unless essential; parallax is the textbook non-essential case.

**Strategy: reduce or replace, keep the meaning.** Users with this setting still need feedback and orientation.

| Full motion | Reduced version |
|---|---|
| Slide / shared-axis page transition | Crossfade ≤ 200 ms, or instant |
| Zoom / container transform | Crossfade |
| Parallax, scroll-scrubbed zoom | Static layout, final state |
| Scroll-scrubbed video / image sequence | Poster frame + optional play button |
| Spring bounce | Critically damped, short |
| Stagger cascade | All at once, single fade |
| Auto-playing loop, marquee | Paused, with play control |
| Skeleton shimmer | Static blocks |
| Press scale, color change, focus ring | Keep (small, non-vestibular) |

```css
/* Prefer opt-in: motion only when allowed */
@media (prefers-reduced-motion: no-preference) {
  .toast { animation: toast-in var(--duration-moderate) var(--ease-emphasized-out); }
}
/* Safety net for third-party CSS: keep events firing, kill movement */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 1ms !important; animation-iteration-count: 1 !important;
    transition-duration: 1ms !important; scroll-behavior: auto !important;
  }
}
```

The safety net uses 1 ms instead of `none` so `animationend`/`transitionend` listeners still fire.

JS: `const mq = matchMedia('(prefers-reduced-motion: reduce)'); mq.addEventListener('change', …)`. GSAP: `gsap.matchMedia().add({ reduce: '(prefers-reduced-motion: reduce)' }, (ctx) => { … ctx.conditions.reduce … })`. Motion: `<MotionConfig reducedMotion="user">` (drops transform/layout animations, keeps opacity) or `useReducedMotion()`. Native: SwiftUI `@Environment(\.accessibilityReduceMotion)`, UIKit `UIAccessibility.isReduceMotionEnabled`, RN `AccessibilityInfo.isReduceMotionEnabled()` and Reanimated `useReducedMotion()`; on Android, "Remove animations" sets the animator duration scale to 0, which system animations obey.

Offer an in-app "Reduce motion" toggle on motion-heavy marketing sites (WCAG's own example of a site-wide control).

## 13. Performance

- **Animate only `transform` and `opacity`** (compositor). `filter` often composites but blur is expensive on large areas. Never animate `width`, `height`, `top`, `left`, `margin`, `padding` or `font-size`; use `scale` with a counter-scaled child, FLIP, or Motion `layout`.
- **`will-change` is a last resort:** add it just before a known animation, remove it after; never blanket-apply. It creates a stacking context (and a containing block for `position: fixed` children), which breaks fixed headers and ScrollTrigger pins inside it.
- **No layout thrash:** never read layout (`getBoundingClientRect`, `offsetHeight`) inside scroll/pointer handlers after writing styles. Measure once on resize/refresh, cache, then only write transforms. Use `IntersectionObserver`/`ResizeObserver` instead of scroll listeners.
- **High refresh rates (120 Hz ProMotion, 90–144 Hz Android/desktop):** drive JS animation by elapsed time, never by "+N px per frame". GSAP, Motion and WAAPI are time-based. Per the Lenis docs, rAF-driven motion in Safari is capped at 60 fps (30 fps in Low Power Mode), so judge smoothness there too.
- **INP (good ≤ 200 ms):** input feedback must not wait on JS. Start the visual response with CSS (`:active`, `:focus-visible`), and keep heavy work (DOM building, data parsing) off the frame that handles the click. JS animations on a busy main thread both stutter and delay input; CSS/WAAPI transform/opacity animations keep running on the compositor.
- **Pause what is off-screen:** stop rAF loops, canvas/WebGL renders, Lottie/Rive playback when hidden (`IntersectionObserver`, `visibilitychange`).
- **Measure:** DevTools Performance panel (look for Layout/Paint inside animation frames), Rendering → Paint flashing and frame rendering stats. Test on a mid-range Android phone with 4× CPU throttling.

## 14. Motion tokens

Put motion in the token system (format and DTCG details: `design-systems.md`). `templates/tokens-starter.css` already defines this set; use these names in every recipe so pasted code resolves:

```css
:root {
  /* duration (Material 3 bands) */
  --duration-instant: 50ms;   --duration-fast: 100ms;    /* press, hover */
  --duration-moderate: 200ms; --duration-slow: 300ms;    /* toggles, menus, accordions */
  --duration-slower: 500ms;                              /* page-level, large surfaces */
  /* easing by role */
  --ease-standard: cubic-bezier(0.2, 0, 0, 1);
  --ease-out: cubic-bezier(0, 0, 0, 1);                  /* enter */
  --ease-in: cubic-bezier(0.3, 0, 1, 1);                 /* exit */
  --ease-emphasized-out: cubic-bezier(0.05, 0.7, 0.1, 1); /* emphasized enter, scroll reveals */
  --ease-emphasized-in: cubic-bezier(0.3, 0, 0.8, 0.15);
  /* springs (consumed by JS: Motion / Reanimated / SwiftUI / Compose) */
  --spring-fast: 0.9 1400;     /* dampingRatio stiffness */
  --spring-default: 0.9 700;
  --spring-slow: 0.9 300;
}
@media (prefers-reduced-motion: reduce) {
  :root { --duration-moderate: 0ms; --duration-slow: 0ms; --duration-slower: 0ms; }
}
```

Scroll reveals and decorative entrances may run longer than the UI bands (500–800 ms with `--ease-emphasized-out`); write those as literal durations next to the effect, not as new global tokens.

Name tokens by role (enter, exit, standard, page), not by curve shape, so you can retune the whole product in one place. Map the same names to native: SwiftUI `Animation` extensions, Compose `MotionScheme` (expressive vs standard), RN shared config objects.

## 15. Native mobile notes

- **iOS:** springs are the default since iOS 17; use `.smooth` for UI, `.snappy` for quick controls, `.bouncy` sparingly. Gesture-driven transitions must be interruptible and follow the finger, then finish with the release velocity. HIG gives no numbers: be brief and precise, make motion optional, let people cancel it.
- **Android:** use Material3 `MotionScheme` (`expressive()` for brand-forward apps, `standard()` for utilitarian ones) instead of hand-picked tweens; spatial springs for movement, effects springs for color/alpha.
- **React Native:** Reanimated 4 changed `withSpring` defaults; after upgrading from 3.x, pin your spring config explicitly or every spring will feel different. Run animations on the UI thread (worklets), never by `setState` per frame.
- **Durations** on wearables run ~30% shorter, tablets ~30% longer than phone.
- Platform specifics (navigation transitions, sheets, predictive back): `platform-mobile.md`.

## Pitfalls

| Symptom | Cause | Fix |
|---|---|---|
| GSAP `from({ y: 28 })` reveal ends stuck at y = 28 | The target also has CSS `transition: transform`; the CSS transition fights every GSAP frame | Never put a CSS transform transition on a GSAP target; animate a wrapper |
| GSAP-animated element drifts after a resize | GSAP 3.12+ absorbed the element's CSS `translate` into its own px x/y, which never updates on media-query change | CSS positioning on an outer wrapper, GSAP on the inner element (details in `scroll-parallax.md`) |
| Motion `whileInView` never fires | Target is clipped to zero area (e.g. `clip-path: inset(0 0 100% 0)`) | Observe an unclipped wrapper, animate the child |
| Exit animation never plays in React | Component unmounts before animating | Wrap in Motion `<AnimatePresence>` with a stable `key` on the child |
| View transition does nothing / throws | Two elements share a `view-transition-name`, or the update callback threw | Unique names; feature-detect; catch `transition.finished` |
| E2E test passes but the element is invisible | Playwright `toBeVisible` passes at opacity 0; `page.clock.fastForward` desyncs `performance.now` from `document.timeline`, freezing WAAPI/Motion at frame 0 | Assert `toHaveCSS('opacity', '1')`; use `clock.setSystemTime` for wall-clock logic; `runFor` after mount; look at the screenshot |
| Animation "verified" in an agent browser pane but broken for users | A hidden tab/pane freezes rAF; pane screenshots lag | Verify in headless Chrome/Playwright with real input; screenshot after state is confirmed via JS |
| CSS change has no effect under `next dev` | Turbopack missed the edit and keeps serving the old CSS | Grep the served `/_next/static/**/*.css` for the new selector before trusting a visual check |
| Reduced-motion users get a broken UI | Global `animation: none` stopped `animationend` handlers that advance state | Use 1 ms durations, or branch logic on the media query |

## Sources

- NN/g, Executing UX Animations: Duration and Motion Characteristics — https://www.nngroup.com/articles/animation-duration/
- NN/g, Response Times: The 3 Important Limits — https://www.nngroup.com/articles/response-times-3-important-limits/
- NN/g, Skeleton Screens 101 — https://www.nngroup.com/articles/skeleton-screens/
- Material Design (M1), Duration & easing — https://m1.material.io/motion/duration-easing.html
- Material Components Android, Motion (easing, duration, springs, transition patterns) — https://raw.githubusercontent.com/material-components/material-components-android/master/docs/theming/Motion.md
- Material 3 motion overview / specs / tokens — https://m3.material.io/styles/motion/overview/how-it-works , https://m3.material.io/styles/motion/overview/specs , https://m3.material.io/styles/motion/easing-and-duration/tokens-specs
- Compose MotionScheme — https://developer.android.com/reference/kotlin/androidx/compose/material3/MotionScheme
- androidx ExpressiveMotionTokens.kt — https://raw.githubusercontent.com/androidx/androidx/androidx-main/compose/material3/material3/src/commonMain/kotlin/androidx/compose/material3/tokens/ExpressiveMotionTokens.kt
- Compose Spring — https://developer.android.com/reference/kotlin/androidx/compose/animation/core/Spring
- Google blog, Material 3 Expressive — https://blog.google/products/android/material-3-expressive-android-wearos-launch/
- SwiftUI spring APIs — https://developer.apple.com/documentation/swiftui/animation/spring(response:dampingfraction:blendduration:) , https://developer.apple.com/documentation/swiftui/spring
- Apple HIG, Motion — https://developer.apple.com/design/human-interface-guidelines/motion
- Carbon, Motion — https://carbondesignsystem.com/elements/motion/overview/
- IxDF, Disney's 12 principles in UI — https://ixdf.org/literature/article/ui-animation-how-to-apply-disney-s-12-principles-of-animation-to-ui-design
- UX Magazine, The UX in Motion Manifesto — https://uxmag.com/articles/creating-usability-with-motion-the-ux-in-motion-manifesto
- Microinteractions structure (Saffer, summarized) — https://cieden.com/book/sub-atomic/microinteractions/structure-of-microinteractions
- MDN, View Transition API — https://developer.mozilla.org/en-US/docs/Web/API/View_Transition_API
- web.dev, Same-document view transitions Baseline — https://web.dev/blog/same-document-view-transitions-are-now-baseline-newly-available
- Chrome, Cross-document view transitions — https://developer.chrome.com/docs/web-platform/view-transitions/cross-document
- caniuse, Cross-document view transitions — https://caniuse.com/cross-document-view-transitions
- web.dev, Interop 2026 — https://web.dev/blog/interop-2026
- React, `<ViewTransition>` — https://react.dev/reference/react/ViewTransition
- Next.js, View transitions guide (16.4) — https://nextjs.org/docs/app/guides/view-transitions
- Astro, View transitions — https://docs.astro.build/en/guides/view-transitions/
- GSAP 3.13 release (free) — https://gsap.com/blog/3-13/ ; Webflow announcement — https://webflow.com/updates/gsap-becomes-free
- GSAP SplitText docs — https://gsap.com/docs/v3/Plugins/SplitText/
- gsap.matchMedia() — https://gsap.com/docs/v3/GSAP/gsap.matchMedia()/
- Motion transitions — https://motion.dev/docs/react-transitions ; rename post — https://motion.dev/blog/framer-motion-is-now-independent-introducing-motion
- Reanimated withSpring / migration — https://docs.swmansion.com/react-native-reanimated/docs/animations/withSpring/ , https://docs.swmansion.com/react-native-reanimated/docs/guides/migration-from-3.x/
- Rive runtimes — https://rive.app/docs/runtimes/getting-started
- MDN, `linear()` easing — https://developer.mozilla.org/en-US/docs/Web/CSS/easing-function/linear
- MDN, prefers-reduced-motion — https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion
- WCAG 2.3.3 Animation from Interactions — https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html
- WCAG 2.2.2 Pause, Stop, Hide — https://www.w3.org/WAI/WCAG22/Understanding/pause-stop-hide.html
- web.dev, Animations guide — https://web.dev/articles/animations-guide
- MDN, will-change — https://developer.mozilla.org/en-US/docs/Web/CSS/will-change
- web.dev, INP — https://web.dev/articles/inp
- Lenis README (Safari frame cap) — https://github.com/darkroomengineering/lenis
