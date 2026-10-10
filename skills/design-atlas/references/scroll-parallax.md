# Scroll effects and parallax

> Read when: building or reviewing anything that moves with scroll: reveal-on-scroll, parallax, pinned/sticky scrollytelling, horizontal scroll sections, scroll-scrubbed video or image sequences (Apple-style), text reveal, progress bars, scroll-snap carousels, zoom-through or clip-path hero reveals, stacking cards, marquees, smooth scrolling (Lenis), a scroll-driven 3D camera; choosing between CSS scroll-driven animations, GSAP ScrollTrigger and Motion `useScroll`; fixing scroll jank, iOS address-bar jumps or elements that drift after resize. General timing, easing and reduced-motion policy live in `motion.md`; WebGL scenes in `3d-webgl.md`.

**Contents:** 1 When scroll effects earn their place · 2 Choosing the tech · 3 Browser support and `@supports` fallback · 4 Mobile viewport and scroll mechanics · 5 Recipe catalog (5.1–5.15) · 6 Example sites · 7 Verifying scroll work · Pitfalls · Sources

## 1. When scroll effects earn their place

| Page type | Scroll effects | Why |
|---|---|---|
| Product launch, brand, campaign, portfolio, data story | Yes: 1–3 signature moments + light reveals | Scroll is the narrative clock; people came to be shown something |
| Marketing landing / pricing | Light: reveals, one pinned demo, progress | Conversion content must stay readable and fast |
| Docs, blog, e-commerce listing, checkout | Progress bar, sticky TOC, snap carousels only | People scan and act; motion competes with reading |
| App UI, dashboards, forms, settings | None beyond native scroll and sticky headers | Scroll-linked motion slows task completion |

Rules: each effect must pace or explain content (feature reveal, sequence, cause → effect), else cut it. The final state is the default state: readable with JS off, before animations run and under `prefers-reduced-motion`. Never change scroll speed/direction on content pages; a pinned section stays ≤ ~3 viewports of scroll. At most one heavy effect (video scrub, image sequence, WebGL) above the fold; lazy-init the rest as they approach.

## 2. Choosing the tech

| Need | Use | Why |
|---|---|---|
| Fade/slide in once when visible | `IntersectionObserver` + CSS transition (or Motion `whileInView`) | Plays once, trivial, works everywhere |
| Progress tied to scroll (parallax, progress bar, scrubbed reveal) | CSS scroll-driven animations (`animation-timeline`) with `@supports` fallback | Runs off the main thread for transform/opacity; zero JS |
| Pinning with a multi-step timeline, scrub smoothing, snapping, video/canvas scrub, Firefox parity | GSAP ScrollTrigger (gsap 3.15, free) | Mature pinning, `scrub: n` smoothing, refresh handling |
| React component whose style follows scroll | Motion `useScroll` + `useTransform` | Declarative; can hardware-accelerate via ScrollTimeline |
| Native mobile app | Platform scroll offsets (SwiftUI `onScrollGeometryChange`/`scrollTransition`, Compose `LazyListState`, RN Reanimated `useAnimatedScrollHandler`) | Native scroll physics; never re-implement scrolling |
| 3D camera along a path | ScrollTrigger (or `useScroll`) → progress → render loop | See §5.14 and `3d-webgl.md` |

Do not mix two engines on the same element (e.g. CSS scroll-driven + GSAP on one node). One element, one owner.

## 3. Browser support and `@supports` fallback

CSS scroll-driven animations, as of 2026-10:

| Browser | Status |
|---|---|
| Chrome / Edge | 115+ (July 2023) |
| Safari (macOS, iOS) | 26.0+ (Sept 2025). 26.5 (May 2026) fixed the `scroll` range name and dynamic `animation-play-state: paused` |
| Firefox | Release builds: behind `layout.css.scroll-driven-animations.enabled` (on by default only in Nightly). caniuse lists support from Firefox 160 (a future release at time of writing). Interop 2026 focus area |

So every scroll-driven animation needs a fallback that still shows the final state. Pattern:

```css
.reveal { opacity: 1; transform: none; }   /* 1. final state is the default (no JS, Firefox, reduced motion) */
@supports (animation-timeline: view()) {    /* 2. enhance only where supported and allowed */
  @media (prefers-reduced-motion: no-preference) {
    .reveal { animation: reveal linear both; animation-timeline: view(); animation-range: entry 10% cover 30%; }
  }
}
@keyframes reveal { from { opacity: 0; transform: translateY(32px); } }
```

Need it in Firefox too: either accept the static fallback, add a JS path (IntersectionObserver/GSAP) inside `@supports not (animation-timeline: view())` logic (`CSS.supports('animation-timeline: view()')`), or load the flackr polyfill (`https://flackr.github.io/scroll-timeline/dist/scroll-timeline.js`; CSS must be same-origin or inline).

Cheat sheet:
- `scroll(root block)` = page scroll progress (`nearest`, `self` for other scrollers); `view()` = this element crossing its scrollport (`view(block 20%)` adds an inset).
- Named: `view-timeline: --scene block` on an ancestor, `animation-timeline: --scene` on descendants; `timeline-scope: --scene` on a common ancestor for non-descendants.
- `animation-range`: `cover` (first pixel enters → last leaves), `contain` (fully inside, or fully covering when taller than the viewport), `entry`, `exit`, `entry-crossing`, `exit-crossing`; e.g. `entry 0% entry 100%`. Ranges use the untransformed box, so animating the subject's own transform does not feed back.
- Use the shorthand `animation: name linear both` (duration `auto`) and shape motion with keyframe offsets, not easing.

## 4. Mobile viewport and scroll mechanics

- **Units:** `lvh` = toolbars retracted (largest), `svh` = toolbars shown (smallest), `dvh` = current (throttled updates as toolbars move). Size pinned stages and full-screen heroes with `100svh` (always fits) or `100lvh` (always covers). Avoid `dvh` inside scroll animations: it changes mid-scroll and re-lays-out the page. `100vh` only as a fallback line before `svh`.
- **iOS / Android address bar** shows and hides while scrolling and fires `resize`. ScrollTrigger refreshes on resize by default, recalculating every start/end → visible jumps. Fix in this order:
  1. `ScrollTrigger.config({ ignoreMobileResize: true })` (3.10+): skips refresh for vertical resizes of ~25% viewport height on touch-only devices. Trade-off: trigger positions near the page bottom can be slightly off. Opt-in.
  2. `ScrollTrigger.normalizeScroll(true)`: moves scrolling onto the JS thread, which stops the address bar toggling on most mobile browsers and removes pin jitter caused by threaded scrolling. Experimental and opt-in; it changes the native scroll feel, can break `position: fixed` UI, and hands control back during multi-touch. Use only on pages with heavy pinning that still jitter after step 1.
- **Pinned elements:** ScrollTrigger pins with `position: fixed` (or a transform when the scroller is not the document). An ancestor with `transform`, `filter` or `will-change` breaks fixed pinning; keep pinned sections' ancestors clean or use `pinReparent: true`.
- **Touch** has momentum and no hover: no hover effects, no expensive work per touchmove, native swipe carousels instead of vertical→horizontal hijacks.
- **Refresh after layout changes** (`ScrollTrigger.refresh()` after images/fonts/async content; set image `width`/`height`). Create triggers top to bottom, or set `refreshPriority`.
- **Remove `html { scroll-behavior: smooth }`** with ScrollTrigger (it breaks refresh measurements); use Lenis `anchors` or per-call `scrollIntoView({ behavior })`.

## 5. Recipe catalog

Each entry: what it is · when it earns its place · tech · recipe · mobile · accessibility and performance. All JS recipes assume:

```ts
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
gsap.registerPlugin(ScrollTrigger);
const mm = gsap.matchMedia();   // every scroll effect goes inside mm.add(...) so it reverts cleanly
```

In React use `useGSAP(() => { … }, { scope: ref })` from `@gsap/react` so everything is reverted on unmount; in Astro re-run on `astro:page-load`.

### 5.1 Reveal on scroll

**What:** content fades/slides in as it enters the viewport. **Earns its place:** long marketing pages, to pace sections. Not on docs or app UI. **Tech:** CSS scroll-driven (scrubbed, reverses when scrolling up) or IntersectionObserver (plays once). Prefer play-once for text.

```css
.js [data-reveal]:not(.is-in) { opacity: 0; transform: translateY(24px); }
.js [data-reveal] { transition: opacity 600ms var(--ease-emphasized-out), transform 600ms var(--ease-emphasized-out); }
@media (prefers-reduced-motion: reduce) { .js [data-reveal] { opacity: 1; transform: none; transition: none; } }
```

```ts
document.documentElement.classList.add('js');
const io = new IntersectionObserver((entries) => {
  for (const e of entries) if (e.isIntersecting) { e.target.classList.add('is-in'); io.unobserve(e.target); }
}, { rootMargin: '0px 0px -10% 0px', threshold: 0.15 });
document.querySelectorAll('[data-reveal]').forEach((el) => io.observe(el));
```

GSAP batch for grids (staggers whatever enters together):

```ts
mm.add('(prefers-reduced-motion: no-preference)', () => {
  gsap.set('[data-reveal]', { autoAlpha: 0, y: 24 });
  ScrollTrigger.batch('[data-reveal]', { start: 'top 85%', once: true,
    onEnter: (els) => gsap.to(els, { autoAlpha: 1, y: 0, stagger: 0.06, duration: 0.6, ease: 'power3.out', overwrite: true }) });
});
```

**Mobile:** use smaller travel (12–16 px) and lower thresholds; tall elements may never reach 15% visibility, so use `threshold: 0` + `rootMargin` for anything taller than the viewport. **A11y/perf:** only opacity/transform; keep text reveals ≤ 600 ms; never hide content behind a reveal that requires JS to undo (the `.js` class guard plus a reduced-motion override ensures this). Reveal each element once, not on every pass.

### 5.2 Parallax layers (three implementations)

**What:** layers move at different speeds to suggest depth. **Earns its place:** hero art, illustrated scenes, product imagery with foreground/background separation. Keep the speed difference small (±10–20% of scroll); large differences read as broken and are vestibular triggers. **Mobile:** reduce or disable layers below 768 px. **A11y:** disable under reduced motion (WCAG 2.3.3 names parallax as non-essential).

**A. CSS 3D (`perspective` + `translateZ`)** — no JS, compositor-only, but the parallax must live in its own scroll container:

```css
.parallax-scroller { height: 100svh; overflow-x: hidden; overflow-y: auto; perspective: 1px; perspective-origin: 0 0; }
.parallax-layer    { transform-origin: 0 0; }
.parallax-layer--back { transform: translateZ(-2px) scale(3); }   /* scale = (perspective - z) / perspective = (1 + 2) / 1 */
.parallax-layer--mid  { transform: translateZ(-1px) scale(2); }
```

Elements between scroller and layer need `transform-style: preserve-3d` or it flattens. It needs its own scroller, so `window.scrollY`, scroll restoration and ScrollTrigger defaults no longer apply. Technique dates from 2016; use it only for a self-contained decorative section and prefer B.

**B. CSS scroll-driven (recommended default):**

```css
.scene { position: relative; overflow: clip; view-timeline: --scene block; }
.scene__layer { position: absolute; inset: -15% 0; }          /* oversize so moving layers never show edges */
@supports (animation-timeline: view()) {
  @media (prefers-reduced-motion: no-preference) {
    .scene__layer { animation: parallax linear both; animation-timeline: --scene; animation-range: cover; }
  }
}
/* --depth: 0.15 = far (moves slower than scroll), 0 = with page, -0.1 = near (moves faster) */
@keyframes parallax { from { transform: translateY(calc(var(--depth) * -100svh)); } to { transform: translateY(calc(var(--depth) * 100svh)); } }
```

```html
<section class="scene"><img class="scene__layer" style="--depth: .15" src="sky.avif" alt="" />
  <img class="scene__layer" style="--depth: .06" src="hills.avif" alt="" /><h1 class="scene__title">…</h1></section>
```

**C. GSAP ScrollTrigger scrub** (works in Firefox; use when layers also take part in a pinned timeline):

```ts
mm.add('(prefers-reduced-motion: no-preference) and (min-width: 768px)', () => {
  gsap.utils.toArray<HTMLElement>('[data-depth]').forEach((layer) => {
    const depth = Number(layer.dataset.depth);                // 0.15 far … -0.1 near
    const scene = layer.closest('.scene')!;
    gsap.fromTo(layer,
      { y: () => -depth * window.innerHeight },
      { y: () => depth * window.innerHeight, ease: 'none',
        scrollTrigger: { trigger: scene, start: 'top bottom', end: 'bottom top', scrub: true, invalidateOnRefresh: true } });
  });
});
```

`[data-depth]` elements must have no CSS `translate`/`transform` of their own (see Pitfalls); position them with a wrapper. For layers that must stay aligned with each other, keep their static layout on whole pixels and move them only via transforms.

### 5.3 Pinned / sticky scrollytelling

**What:** a graphic stays fixed while text steps scroll past and change it. **Earns its place:** explaining a process, product walkthrough, data story. **Tech:** CSS `position: sticky` + IntersectionObserver for discrete steps (Scrollama-style, robust, accessible); GSAP pin + scrubbed timeline for continuous choreography.

```html
<section class="story"><div class="story__graphic">…</div>
  <div class="story__steps"><div class="story__step" data-step="1"><p>…</p></div> <!-- data-step 2, 3 … --></div></section>
```

```css
.story { display: grid; grid-template-columns: 1fr minmax(18rem, 28rem); gap: 4rem; }
.story__graphic { position: sticky; top: 0; height: 100svh; display: grid; place-items: center; }
.story__step { min-height: 80svh; display: grid; align-items: center; }
.story__steps { padding-block: 10svh; }   /* (100svh − step height) / 2, else the graphic is not yet pinned at step 1 */
@media (max-width: 767px) {   /* graphic on top, text cards scroll over it */
  .story { grid-template-columns: 1fr; } .story__graphic { height: 55svh; }
  .story__step { position: relative; z-index: 1; min-height: 70svh; } .story__step > * { background: var(--surface); padding: 1rem; border-radius: 12px; }
}
```

```ts
const graphic = document.querySelector<HTMLElement>('.story__graphic')!;
const io = new IntersectionObserver((entries) => {
  for (const e of entries) if (e.isIntersecting) graphic.dataset.step = (e.target as HTMLElement).dataset.step!;
}, { rootMargin: '-45% 0px -45% 0px' });                      // a step is "active" when it crosses the middle band
document.querySelectorAll('.story__step').forEach((s) => io.observe(s));
```

Continuous version (one ScrollTrigger owns the whole timeline):

```ts
mm.add('(prefers-reduced-motion: no-preference)', () => {
  const tl = gsap.timeline({ defaults: { ease: 'none' },
    scrollTrigger: { trigger: '.pin-scene', start: 'top top', end: () => '+=' + window.innerHeight * 3,
                     pin: true, scrub: 0.5, anticipatePin: 1, invalidateOnRefresh: true } });
  tl.to('.pin-scene .device-inner', { xPercent: -25 })
    .from('.pin-scene .caption-2', { autoAlpha: 0, y: 20 }, '<0.2')
    .to('.pin-scene .screen-a', { autoAlpha: 0 }, '+=0.2');
});
```

Rules: pin a wrapper and animate its children (never the pinned element itself); ~1 viewport of scroll per beat; one ScrollTrigger per timeline, never on child tweens. **A11y:** every step is real text in DOM order and conveys the information without the graphic; under reduced motion show the graphic states as static images next to their text.

### 5.4 Horizontal-scroll section

**What:** vertical scroll moves a horizontal strip while the section is pinned. **Earns its place:** galleries, timelines, case-study strips on desktop. On phones prefer a native swipeable scroll-snap row (§5.9).

```ts
mm.add('(min-width: 768px) and (prefers-reduced-motion: no-preference)', () => {
  const track = document.querySelector<HTMLElement>('.h-track')!;
  const distance = () => track.scrollWidth - document.documentElement.clientWidth;
  gsap.to(track, { x: () => -distance(), ease: 'none',
    scrollTrigger: { trigger: '.h-section', start: 'top top', end: () => '+=' + distance(), pin: true, scrub: 1, invalidateOnRefresh: true } });
});
```

CSS-only version (tall wrapper, sticky stage, named view timeline):

```css
.h-section { height: calc(var(--panels, 4) * 100svh); view-timeline: --h block; }
.h-stage { position: sticky; top: 0; height: 100svh; overflow: clip; container-type: inline-size; }
.h-track { display: flex; width: max-content; height: 100%; }
@supports (animation-timeline: view()) {
  .h-track { animation: h-move linear both; animation-timeline: --h; animation-range: contain 0% contain 100%; }
}
@keyframes h-move { to { transform: translateX(calc(-100% + 100cqi)); } }   /* cqi, not vw: vw includes a classic scrollbar */
@supports not (animation-timeline: view()) { .h-section { height: auto; } .h-stage { position: static; height: auto; overflow-x: auto; } }
```

**A11y:** focus moving into an off-screen panel does not scroll a transformed track into view: keep panels non-focusable, or on `focusin` scroll the page to `st.start + panelProgress * (st.end - st.start)`. Reduced motion gets the plain overflow-x row.

### 5.5 Scroll-scrubbed video

**What:** scrolling scrubs a video's `currentTime` (product rotates, object assembles). **Earns its place:** one hero product moment. **Tech:** `<video>` + ScrollTrigger progress; dense keyframes are mandatory because a seek lands on the nearest keyframe.

Encode (every frame a keyframe, sized to the box it renders in, audio stripped):

```bash
ffmpeg -i in.mov -vf scale=1280:-2 -r 30 -c:v libvpx-vp9 -crf 32 -b:v 0 -g 1 -pix_fmt yuv420p -an -row-mt 1 scrub.webm
ffmpeg -i in.mov -vf scale=1280:-2 -r 30 -c:v libx264 -crf 23 -g 1 -pix_fmt yuv420p -an -movflags +faststart scrub.mp4
```

Size grows sharply with keyframe density (one test: every 5th frame ≈ 5× every 100th; a 4 s test clip here: `-g 1` 2.7 MB vs `-g 100` 0.8 MB). If too heavy, try `-g 5`–`10` and judge on real devices. Serve both formats, WebM first: Firefox scrubs MP4 poorly, iOS Safari handles WebM poorly. The server must answer HTTP Range requests (206): without them Chrome cannot seek and the video stays on frame 0.

```html
<video class="scrub" muted playsinline preload="auto" poster="scrub-poster.avif"><source src="scrub.webm" type="video/webm" /><source src="scrub.mp4" type="video/mp4" /></video>
```

```ts
mm.add('(prefers-reduced-motion: no-preference)', () => {
  const v = document.querySelector<HTMLVideoElement>('.scrub')!;
  let target = 0;
  const st = ScrollTrigger.create({ trigger: '.scrub-scene', start: 'top top', end: '+=250%', pin: true,
                                    onUpdate: (self) => { target = self.progress * (v.duration || 0); } });
  const tick = () => {
    if (!Number.isFinite(v.duration) || v.seeking) return;          // never queue seeks while one is in flight
    const next = v.currentTime + (target - v.currentTime) * 0.25;   // light smoothing
    if (Math.abs(next - v.currentTime) > 1 / 60) v.currentTime = next;
  };
  gsap.ticker.add(tick);
  return () => { gsap.ticker.remove(tick); st.kill(); };
});
```

Never call `play()`. **Mobile:** `muted playsinline` required; keep the poster until `loadeddata` and test on a real iPhone (buffering before a user gesture varies by iOS version); smaller encode under 768 px. **A11y/perf:** reduced motion → poster (or a normal video with controls) plus a text equivalent; `preload="none"` until the section is ~1 viewport away, then `auto`.

### 5.6 Canvas image sequence (Apple AirPods-style)

**What:** pre-rendered frames drawn to a `<canvas>` by scroll progress; frame-accurate in every browser, unlike video seeking. Apple's product pages mix this, scrubbed video and keyframed scroll groups. **Earns its place:** 3D product turntables, exploded views.

Export frames (typical sequences: 60–180). Many ffmpeg builds lack libwebp, so go via PNG:

```bash
ffmpeg -i render.mov -vf "fps=30,scale=1600:-2" png/%04d.png
for f in png/*.png; do cwebp -quiet -q 75 "$f" -o "lg/$(basename "${f%.png}").webp"; done
```

**Memory:** a decoded frame costs width × height × 4 bytes: 1600×900 = 5.8 MB, so 150 frames ≈ 860 MB, which crashes phones. On mobile use ~960 px and every 2nd frame; keep `HTMLImageElement`s (the browser can evict decoded data), not a bulk `ImageBitmap` decode.
**Preloading:** frame 1 immediately (it is the poster); the rest when the section is ~2 viewports away, coarse-to-fine (every 16th, 8th, 4th, 2nd, then all); always draw the nearest loaded frame so scrubbing works before everything arrives.

```ts
mm.add('(prefers-reduced-motion: no-preference)', () => {
  const canvas = document.querySelector<HTMLCanvasElement>('canvas.seq')!, ctx = canvas.getContext('2d')!;
  const small = matchMedia('(max-width: 767px)').matches, N = small ? 60 : 120;
  const url = (i: number) => `/seq/${small ? 'sm' : 'lg'}/${String(i + 1).padStart(4, '0')}.webp`;
  const imgs: (HTMLImageElement | undefined)[] = [], requested = new Set<number>(), state = { frame: 0 };
  const load = (i: number) => {
    if (requested.has(i)) return; requested.add(i);
    const img = new Image(); img.src = url(i);
    img.decode().then(() => { imgs[i] = img; draw(); }, () => requested.delete(i));
  };
  const nearest = (i: number) => { for (let d = 0; d < N; d++) { if (imgs[i - d]) return imgs[i - d]; if (imgs[i + d]) return imgs[i + d]; } };
  function draw() {
    const img = nearest(Math.round(state.frame)); if (!img) return;
    const s = Math.max(canvas.width / img.naturalWidth, canvas.height / img.naturalHeight);   // cover-fit
    const w = img.naturalWidth * s, h = img.naturalHeight * s;
    ctx.drawImage(img, (canvas.width - w) / 2, (canvas.height - h) / 2, w, h);
  }
  const resize = () => { const dpr = Math.min(devicePixelRatio, 2);
    canvas.width = Math.round(canvas.clientWidth * dpr); canvas.height = Math.round(canvas.clientHeight * dpr); draw(); };
  const ro = new ResizeObserver(resize); ro.observe(canvas);
  load(0);
  ScrollTrigger.create({ trigger: '.seq-scene', start: 'top 200%', once: true,
    onEnter: () => { for (const step of [16, 8, 4, 2, 1]) for (let i = 0; i < N; i += step) load(i); } });
  gsap.to(state, { frame: N - 1, ease: 'none', onUpdate: draw,
    scrollTrigger: { trigger: '.seq-scene', start: 'top top', end: '+=250%', pin: true, scrub: 0.3 } });
  return () => ro.disconnect();
});
```

**A11y/perf:** the canvas gets `role="img"` and an `aria-label` describing the sequence; reduced motion shows 1–3 key frames as `<img>` with captions. Cap DPR at 2. Do not run a continuous rAF loop: draw only on progress change.

### 5.7 Text highlight / reveal on scroll

**Highlight sweep** (marker fills behind a phrase as it reaches mid-screen):

```css
.mark { background: linear-gradient(var(--mark, oklch(0.9 0.15 95)), var(--mark, oklch(0.9 0.15 95))) no-repeat 0 100% / 100% 100%; }
@supports (animation-timeline: view()) {
  @media (prefers-reduced-motion: no-preference) {
    .mark { background-size: 0% 100%; animation: mark linear both; animation-timeline: view(); animation-range: entry 100% cover 45%; }
  }
}
@keyframes mark { to { background-size: 100% 100%; } }
```

On a multi-line span the default `box-decoration-break: slice` makes the sweep travel line by line. `background-size` repaints: fine for a few phrases, not paragraphs.

**Word-by-word opacity reveal** (dim words brighten as you scroll):

```ts
import { SplitText } from 'gsap/SplitText';
gsap.registerPlugin(SplitText);
mm.add('(prefers-reduced-motion: no-preference)', () => {
  const split = SplitText.create('.reveal-text', { type: 'words' });   // aria: 'auto' keeps the sentence readable to AT
  gsap.from(split.words, { opacity: 0.2, stagger: 0.1, ease: 'none',
    scrollTrigger: { trigger: '.reveal-text', start: 'top 80%', end: 'center 45%', scrub: true } });
  return () => split.revert();
});
```

Rules: dimmed words fail contrast, so the reveal must complete before the text reaches the middle of the viewport (`end` ≤ `center 45%`) and only on display-size statements, never body copy. Thai and other scripts with combining marks: split by words (use `Intl.Segmenter`), never by characters (see `motion.md` §10).

### 5.8 Scroll progress indicators

```css
.progress { position: fixed; inset: 0 0 auto; height: 3px; z-index: 50; background: var(--accent); transform-origin: 0 50%; transform: scaleX(0); }
@supports (animation-timeline: scroll()) { .progress { animation: progress linear both; animation-timeline: scroll(root block); } }
@keyframes progress { to { transform: scaleX(1); } }
```

Fallback when `!CSS.supports('animation-timeline: scroll()')`: one passive `scroll` listener that schedules a single rAF and writes `transform: scaleX(scrollY / (scrollHeight - innerHeight))`; never read layout per frame beyond that. Article-only progress: `body { timeline-scope: --article; } article { view-timeline: --article block; } .progress { animation-timeline: --article; animation-range: contain 0% contain 100%; }`. Mark the bar `aria-hidden="true"` (decorative); if progress matters, show "6 min left" text. Under reduced motion a progress bar is fine to keep (it is not a vestibular trigger).

**Step track with a travelling marker** (a "how it works" timeline: the line fills and a dot rides it as the reader passes each step; tested in Chrome 2026-10-10 with real scrolling: fill scale and dot position tracked scroll 0→1 linearly). Subtle-level motion: it is a progress indicator, not storytelling.

```html
<div class="steps">
  <div class="steps__rail" aria-hidden="true"><span class="steps__fill"></span><span class="steps__dot"></span></div>
  <ol>…steps…</ol>
</div>
```
```css
.steps { position: relative; padding-left: 3rem; view-timeline: --steps block; view-timeline-inset: 45% 45%; } /* progress = reading line at mid-viewport */
.steps__rail { position: absolute; left: 1.25rem; top: .75rem; bottom: .75rem; width: 4px; border-radius: 2px;
  background: var(--border); container-type: size; }   /* 100cqh = rail height (also a stacking context, see Pitfalls) */
.steps__fill { position: absolute; inset: 0; border-radius: inherit; background: var(--primary); transform-origin: 50% 0; }
.steps__dot  { position: absolute; left: 50%; top: 0; width: 1rem; height: 1rem; border-radius: 50%; background: var(--accent);
  transform: translate(-50%, calc(100cqh - 50%)); }      /* final state = no-support and reduced-motion fallback */
@supports (animation-timeline: view()) {
  @media (prefers-reduced-motion: no-preference) {
    .steps__fill { animation: steps-fill linear both; animation-timeline: --steps; animation-range: cover 0% cover 100%; }
    .steps__dot  { animation: steps-dot  linear both; animation-timeline: --steps; animation-range: cover 0% cover 100%; }
  }
}
@keyframes steps-fill { from { transform: scaleY(0); } to { transform: scaleY(1); } }
@keyframes steps-dot  { from { transform: translate(-50%, -50%); } to { transform: translate(-50%, calc(100cqh - 50%)); } }
```

### 5.9 CSS scroll-snap carousels

**What:** native horizontal scroller that settles on items. **Earns its place:** product cards, image galleries, onboarding; best default on mobile. No JS needed for swiping.

```css
.carousel { display: grid; grid-auto-flow: column; grid-auto-columns: min(85%, 22rem); gap: 1rem; overflow-x: auto;
  overscroll-behavior-x: contain; scroll-snap-type: x mandatory; padding-inline: 1rem; scroll-padding-inline: 1rem; }
.carousel > * { scroll-snap-align: start; }
.carousel--one-at-a-time > * { scroll-snap-stop: always; }
@media (prefers-reduced-motion: no-preference) { .carousel { scroll-behavior: smooth; } }
```

Prev/next buttons: `carousel.scrollBy({ left: dir * carousel.clientWidth * 0.9 })` (smoothness follows the media query above). Show a peek of the next card (the 85% column); keep the scrollbar or buttons on desktop. `mandatory` only for horizontal rows of short items; vertical full-page `mandatory` snapping traps content taller than the screen (use `proximity`). **A11y:** container `role="region"` + `aria-label`, slides labelled "3 of 8", no autoplay (if you must, pause on hover/focus and provide a pause button: WCAG 2.2.2). CSS `::scroll-button()` / `::scroll-marker` carousels are still experimental and not Baseline: progressive enhancement only.

### 5.10 Hero zoom-through and mask / clip-path reveals

**Zoom-through:** a word or shape mask scales up until its hole fills the screen and reveals the next scene. **Earns its place:** one brand moment per site, at the top.

```ts
mm.add('(prefers-reduced-motion: no-preference)', () => {
  gsap.timeline({ scrollTrigger: { trigger: '.zoom-hero', start: 'top top', end: '+=150%', pin: true, scrub: 0.5 } })
    .fromTo('.zoom-hero__mask', { scale: 1 }, { scale: 24, ease: 'power2.in' })
    .to('.zoom-hero__next', { autoAlpha: 1, ease: 'none' }, '-=0.25');
});
```

Make the mask an SVG (`<mask>` or a path with `fill-rule: evenodd`) so it stays sharp at 24×. Scaled HTML text is rasterized at layer creation and blurs when scaled up; if you must scale text, author it at the final size and scale it down from a small start value, and do not leave `will-change: transform` on it.

**Clip-path reveal** (image wipes open as it enters):

```css
@supports (animation-timeline: view()) {
  @media (prefers-reduced-motion: no-preference) {
    .wipe { animation: wipe linear both; animation-timeline: view(); animation-range: entry 0% cover 40%; }
  }
}
@keyframes wipe { from { clip-path: inset(0 0 100% 0); } to { clip-path: inset(0 0 0 0); } }
```

`clip-path` is not one of the compositor-safe properties (transform/opacity): keep a few on screen at once and test on mid-range Android. If you trigger it with an observer instead (Motion `whileInView`, IntersectionObserver), observe an unclipped wrapper, never the clipped element.

### 5.11 Stacking sticky cards

**What:** cards stick one after another and earlier cards shrink back as the next one covers them. **Earns its place:** 3–6 feature or case-study cards.

```html
<div class="cards" style="--n: 4"><article class="card" style="--i: 0"><div class="card__inner">…</div></article> <!-- --i: 1, 2, 3 --></div>
```

```css
.cards { display: grid; gap: 2rem; padding-bottom: 10svh; view-timeline: --cards block; }
.card  { position: sticky; top: calc(4rem + var(--i) * 1rem); }      /* each card sticks a little lower */
.card__inner { min-height: 60svh; transform-origin: 50% 0; border-radius: 24px; }
@supports (animation-timeline: view()) {
  @media (prefers-reduced-motion: no-preference) {
    .card__inner { animation: recede linear forwards; animation-timeline: --cards;   /* card i shrinks during its 1/n slice */
      animation-range: exit-crossing calc(var(--i) / var(--n) * 100%) exit-crossing calc((var(--i) + 1) / var(--n) * 100%); }
  }
}
@keyframes recede { to { transform: scale(calc(1 - (var(--n) - 1 - var(--i)) * 0.05)); } }
```

The last card does not shrink (factor 0). Pattern adapted from the scroll-driven-animations.style stacking-cards demo. **Mobile:** works as is; reduce `top` offsets. **A11y:** plain sticky stacking is fine under reduced motion; just drop the scale.

### 5.12 Infinite marquee

```html
<div class="marquee" style="--gap: 3rem; --dur: 40s">
  <ul class="marquee__track"><li>Logo A</li><li>Logo B</li><li>Logo C</li><li aria-hidden="true">Logo A</li><li aria-hidden="true">Logo B</li><li aria-hidden="true">Logo C</li></ul>
  <button class="marquee__toggle" aria-pressed="false">Pause</button></div>
```

```css
.marquee { overflow: clip; mask-image: linear-gradient(90deg, transparent, #000 8%, #000 92%, transparent); }
.marquee__track { display: flex; gap: var(--gap); width: max-content; list-style: none; margin: 0; padding: 0; }
.marquee__track > li { flex: none; }
@media (prefers-reduced-motion: no-preference) {
  .marquee__track { animation: marquee var(--dur) linear infinite; }
  .marquee:hover .marquee__track, .marquee:focus-within .marquee__track,
  .marquee[data-paused] .marquee__track { animation-play-state: paused; }
}
/* the second half starts one gap after the first: shift by 50% plus half a gap */
@keyframes marquee { to { transform: translateX(calc(-50% - var(--gap) / 2)); } }
@media (prefers-reduced-motion: reduce) { .marquee { overflow-x: auto; } }
```

The two halves must be identical. Duration should scale with content width (aim for ~40–80 px/s). It runs longer than 5 s, so WCAG 2.2.2 requires a pause control (the button toggles `data-paused`); hover-pause alone does not cover touch or keyboard. A scroll-velocity marquee (speeds up with scroll) is GSAP territory: `ScrollTrigger.create({ onUpdate: (s) => tween.timeScale(1 + Math.abs(s.getVelocity()) / 500) })`, easing back to 1 afterwards.

### 5.13 Smooth scrolling with Lenis

**What:** Lenis (1.3.x as of 2026-09) interpolates wheel scrolling toward the native scroll position; scrollbars, keyboard and `position: sticky` keep working because the document still scrolls natively. **Earns its place:** immersive brand sites where scrubbed/pinned animation must feel continuous with wheel input.

```ts
import Lenis from 'lenis';
import 'lenis/dist/lenis.css';
const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
if (!reduce) {
  const lenis = new Lenis({ lerp: 0.1, anchors: true });     // touch is not smoothed by default (syncTouch: false): keep it that way
  lenis.on('scroll', ScrollTrigger.update);
  gsap.ticker.add((time) => lenis.raf(time * 1000));         // one clock for Lenis and GSAP
  gsap.ticker.lagSmoothing(0);
}
```

Without GSAP: `new Lenis({ autoRaf: true })`. Mark modals, dropdowns, code blocks and any nested scroller with `data-lenis-prevent` (or `-wheel`/`-touch`/`-vertical`/`-horizontal` variants); Netflix Careers does this in production.

**Do not use Lenis when:** the page is docs, content, e-commerce or an app (people expect their OS scroll feel and speed); reduced motion is on; the page relies on CSS scroll-snap (use `lenis/snap` or skip Lenis); there are iframes people scroll over (wheel events stop there); you are only trying to fix jank (fix the jank). Known limits from its docs: Safari caps it at 60 fps (30 fps in Low Power Mode); `position: fixed` can lag on pre-M1 macOS Safari; `syncTouch` is unstable on iOS < 16. Remove `scroll-behavior: smooth` from CSS when using it.

### 5.14 Scroll-linked 3D camera

**What:** scroll moves a WebGL camera along a path through a scene. **Earns its place:** product or world exploration on brand sites (Igloo Inc, Atelier San Rita, Lando Norris). Scene, loading and GPU budgets: `3d-webgl.md`.

```ts
// three.js; `curve` = CatmullRomCurve3 through authored camera points
const cam = { p: 0 };
mm.add('(prefers-reduced-motion: no-preference)', () => {
  gsap.to(cam, { p: 1, ease: 'none',
    scrollTrigger: { trigger: '.scene3d', start: 'top top', end: '+=400%', pin: true, scrub: 1 } });
});
let last = -1;
renderer.setAnimationLoop(() => {
  if (Math.abs(cam.p - last) < 1e-4) return;                 // render on demand: idle page = idle GPU
  last = cam.p;
  camera.position.copy(curve.getPointAt(cam.p));
  camera.lookAt(curve.getPointAt(Math.min(cam.p + 0.01, 1)));
  renderer.render(scene, camera);
});
```

Reset `last = -1` after a resize so the new size renders. Keep HTML text sections in the DOM over the canvas so content and SEO do not depend on WebGL; pause the loop when the canvas is off-screen; reduced motion → a still render per section.

### 5.15 React: Motion `useScroll` / `useTransform`

```tsx
'use client';
import { useRef } from 'react';
import { motion, useScroll, useTransform, useReducedMotion } from 'motion/react';

export function ParallaxFigure({ src, alt }: { src: string; alt: string }) {
  const ref = useRef<HTMLElement>(null);
  const reduce = useReducedMotion();
  const { scrollYProgress } = useScroll({ target: ref, offset: ['start end', 'end start'] }); // 0 = entering, 1 = gone
  const y = useTransform(scrollYProgress, [0, 1], ['-10%', '10%']);
  const opacity = useTransform(scrollYProgress, [0, 0.2, 0.8, 1], [0, 1, 1, 0]);
  return (
    <figure ref={ref} style={{ position: 'relative', overflow: 'clip', aspectRatio: '16 / 9' }}>
      <motion.img src={src} alt={alt}
        style={{ y: reduce ? 0 : y, opacity: reduce ? 1 : opacity, scale: 1.2, width: '100%', height: '100%', objectFit: 'cover' }} />
    </figure>
  );
}
```

Reading progress: `const { scrollYProgress } = useScroll();` then `<motion.div aria-hidden style={{ scaleX: scrollYProgress, transformOrigin: '0 50%' }} />` on a fixed 3 px bar.

`useScroll` can hand opacity/transform animations to the browser's ScrollTimeline (hardware-accelerated); wrapping progress in `useSpring` adds lag-smoothing but moves the work back to JS. `offset` pairs read "target edge, container edge": `['start end', 'end start']` = from target top meeting viewport bottom to target bottom meeting viewport top. For `whileInView` reveals, put the observer on an unclipped wrapper.

## 6. Example sites (verified live 2026-10-10)

| Site | What to learn |
|---|---|
| Apple AirPods Pro — https://www.apple.com/airpods-pro/ | Scroll-scrubbed hero (`VideoScrub`), parallax images, per-section scroll groups with staggered fades |
| Apple MacBook Pro — https://www.apple.com/macbook-pro/ | Keyframed scroll groups over sticky stages; restraint between big moments |
| GSAP forum, AirPods image sequence — https://gsap.com/community/forums/topic/25188-airpods-image-sequence-animation-using-scrolltrigger/ | Canvas frame tween with ScrollTrigger, WebP frames, one master timeline for frames + text |
| Lando Norris — https://landonorris.com/ | ScrollTrigger + Lenis driving WebGL sections (Awwwards SOTD 2025-11-17) |
| Igloo Inc — https://www.igloo.inc/ | Infinite scroll through a 3D world with scene transitions (Awwwards SOTD 2024-07-23) |
| Atelier San Rita — https://sanrita.ca/ | One persistent R3F scene, scroll mapped to camera, Lenis (Awwwards case study) |
| Floema — https://floema.com | Lenis + GSAP + Rive + Three.js; render loop stops when idle |
| A Cosmic Scroll Journey (Wix Studio) — https://www.wix.com/studio/design/inspiration/space | Layered parallax scrollytelling with sticky scenes |
| Vizcom — https://vizcom.com/ | GSAP-scrubbed scrollytelling with canvas and Lenis |
| Telescope — https://telescope.fyi/ | Zoom-through intro with parallax |
| Lenis — https://lenis.dev/ | Smooth scroll done right; showcase of production users |
| Netflix Careers — https://jobs.netflix.com/ | Lenis on a content site with `data-lenis-prevent` on nested scrollers |
| Stacking Cards (CSS) — https://scroll-driven-animations.style/demos/stacking-cards/css/ | Sticky stacking with view timelines, zero JS |
| Horizontal Section (CSS) — https://scroll-driven-animations.style/demos/horizontal-section/css/ | Vertical → horizontal scroll in pure CSS |
| Image Reveal — https://scroll-driven-animations.style/demos/image-reveal/css/ | View-timeline ranges for reveals |
| Codrops, Sticky Grid Scroll (2026) — https://tympanus.net/codrops/2026/03/02/sticky-grid-scroll-building-a-scroll-driven-animated-grid/ | Tall wrapper + sticky stage + scrubbed timeline + Lenis on the GSAP ticker |
| Codrops, 3D scroll-driven text (2025) — https://tympanus.net/codrops/2025/11/04/creating-3d-scroll-driven-text-animations-with-css-and-gsap/ | CSS 3D transforms driven by ScrollTrigger, no 3D library |
| Codrops, cinematic 3D scroll (2025) — https://tympanus.net/codrops/2025/11/19/how-to-build-cinematic-3d-scroll-experiences-with-gsap/ | GSAP + Three.js camera pacing |
| Firewatch — https://www.firewatchgame.com/ | Classic layered key-art parallax (per-layer speed attributes) |
| NYT "Snow Fall" (2012) — https://www.nytimes.com/projects/2012/snow-fall/index.html | The original scrollytelling reference: chapters, scroll-triggered video |
| The Pudding, scrollytelling guide — https://pudding.cool/process/how-to-implement-scrollytelling/ | Sticky graphic + text steps; compares libraries (Scrollama originated here) |

Codrops rows were confirmed from search results (the site blocks fetchers); everything else was opened.

## 7. Verifying scroll work

All recipes except 5.2 A and 5.14 were run in headless Chrome (desktop and 390 px) with real wheel input on 2026-10-10 (gsap 3.15.0, lenis 1.3.26, motion 14.1.0, React 19.3, TypeScript 7 strict): positions, ranges, the marquee loop seam, pin alignment after a mid-scroll reload and a resize, video/sequence frames and reduced-motion states matched the comments. Safari, Firefox and real phones were not tested. Check your own pages the same way:
- **Real browser, real input.** A hidden tab or backgrounded agent browser pane freezes `requestAnimationFrame`, so scroll animation "verified" there proves nothing. Use headless Chrome/Playwright with `page.mouse.wheel`, assert numbers via JS (`gsap.getProperty`, `getComputedStyle(...).transform`), then look at screenshots.
- **`toBeVisible()` passes at opacity 0:** assert `toHaveCSS('opacity', '1')`. Under Playwright `page.clock`, WAAPI/Motion animations can stall at frame 0 (fast-forward moves `performance.now`, not `document.timeline`): `runFor` after mounting, or skip the fake clock.
- **Reload mid-scroll and resize desktop ↔ mobile** at least once; they catch most ScrollTrigger measurement bugs.
- **Under `next dev` (Turbopack)** a CSS edit can silently not be served: grep the served `/_next/static/**/*.css` for the new selector before judging a visual.
- **Paint:** for "scrolled but nothing changed", check `document.elementsFromPoint(x, y)` and two fresh screenshots; DevTools Rendering → Paint flashing.
- Emulate `prefers-reduced-motion: reduce` and confirm every section shows its final, readable state.

## Pitfalls

| Symptom | Cause | Fix |
|---|---|---|
| A marker or overlay inside a `container-type` element can't rise above sibling content however high its `z-index` | `container-type: size` **and** `inline-size` create a stacking context (MDN), so children's z-index only counts inside the container | Put the z-index on the container itself, or move the overlay out of the container (a separate rail), and remember this when adding container queries to cards with dropdowns/tooltips |
| GSAP-animated element drifts off its spot after a resize; reloading mid-page throws it thousands of px away | GSAP 3.12+ parses the element's CSS `translate` (e.g. `translate: 0 -54%`) into its own px `x/y` the first time it animates it; that px value never updates when media queries change. Targets measured with `getBoundingClientRect()` against the viewport while scrolled are also wrong | Put CSS positioning (`left/top/translate`) on an outer wrapper and animate only the inner element. Measure positions relative to the pinned container (`rect − pinRect`), subtract the current GSAP `x/y/scale`, use function values + `invalidateOnRefresh: true`. Test by reloading mid-scroll and resizing desktop ↔ mobile |
| `gsap.from({ y: 28 })` reveal ends stuck at y = 28 (opacity fine), overlapping the next block on mobile | The element also has CSS `transition: transform`, which re-animates every value GSAP writes | Never put a CSS transform transition on a GSAP target, or reveal a wrapper instead |
| A scrubbed color like `rgb(from var(--bg) r g b / var(--frame))` does not repaint in Chrome (computed value changes, pixels do not) | Chrome may skip repainting a relative color driven by a custom property updated per frame | Animate `opacity`/`transform` of a `::before` overlay instead; verify paint with `elementsFromPoint` + two screenshots |
| Motion `whileInView` (or an IntersectionObserver) never fires | Target clipped to zero area, e.g. `clip-path: inset(0 0 100% 0)` | Observe an unclipped wrapper, animate a child |
| Layers that should line up drift by a pixel; loops show a seam; 3D planes slice through each other | Fractional `left/top` snaps to whole pixels at different moments; layers sharing one `preserve-3d` stage intersect in 3D space | Integer static layout, move only via `translate3d`, give each object its own `perspective()` instead of one shared 3D stage |
| Pinned section jumps when the iOS address bar hides/shows | Resize → ScrollTrigger refresh → start/end recalculated | `ScrollTrigger.config({ ignoreMobileResize: true })`; size stages with `svh`/`lvh`, not `dvh`; `normalizeScroll(true)` as a last resort |
| Pin flickers or jumps at its start on fast scroll | Threaded scrolling moves the page before JS applies the pin | `anticipatePin: 1`; for persistent cases `normalizeScroll(true)` |
| Pinned element scrolls away or is offset | Ancestor has `transform`, `filter` or `will-change` (fixed positioning becomes relative to it) | Remove it from ancestors, or `pinReparent: true` |
| Triggers fire at the wrong place after images/fonts load or after SPA navigation | Stale measurements; triggers from the old route still alive | Set image dimensions; `ScrollTrigger.refresh()` after layout changes; revert `gsap.matchMedia()`/`useGSAP` contexts on unmount (Astro: `astro:before-swap`) |
| Scrubbed video stutters or lags far behind scroll | Sparse keyframes force seeks to the nearest keyframe; seeks queued while `seeking` | Encode with `-g 1` (or ≤ 10), skip writes while `video.seeking`, smooth the target |
| Scrubbed video never leaves frame 0 in Chrome although `seeking` events fire (seen 2026-10-10 under `python3 -m http.server`) | The server ignores `Range` headers (no 206), so the media is not seekable | Serve video from a Range-capable server/CDN; check `curl -H 'Range: bytes=0-99' -I <url>` returns 206 |
| Image-sequence page crashes on iPhone | Hundreds of large decoded frames in memory | Smaller frames and fewer of them on mobile, nearest-loaded drawing, no bulk `ImageBitmap` decode |
| Scroll animation works in Chrome and Safari, does nothing in Firefox | CSS scroll-driven animations are still flagged in Firefox release | `@supports` fallback showing the final state, or a JS path |

## Sources

- MDN, Stacking context (container-type size/inline-size creates one) — https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_positioned_layout/Stacking_context
- Chrome for Developers, Scroll-driven animations — https://developer.chrome.com/docs/css-ui/scroll-driven-animations
- WebKit, Safari 26.0 features — https://webkit.org/blog/17333/webkit-features-in-safari-26-0/ ; Safari 26.5 notes — https://developer.apple.com/documentation/safari-release-notes/safari-26_5-release-notes
- caniuse, animation-timeline — https://caniuse.com/mdn-css_properties_animation-timeline
- MDN, Firefox experimental features — https://developer.mozilla.org/Firefox/Experimental_features
- BuildMVPFast, CSS scroll-driven animations go cross-browser (Firefox 152 status) — https://www.buildmvpfast.com/blog/css-scroll-driven-animations-replace-js-2026
- web.dev, Interop 2026 — https://web.dev/blog/interop-2026
- flackr, scroll-timeline polyfill — https://github.com/flackr/scroll-timeline
- scroll-driven-animations.style demos (Bramus) — https://scroll-driven-animations.style/demos/stacking-cards/css/
- web.dev, Large, small and dynamic viewport units — https://web.dev/blog/viewport-units
- GSAP docs: ScrollTrigger — https://gsap.com/docs/v3/Plugins/ScrollTrigger/ ; config() — https://gsap.com/docs/v3/Plugins/ScrollTrigger/static.config() ; normalizeScroll() — https://gsap.com/docs/v3/Plugins/ScrollTrigger/static.normalizeScroll() ; matchMedia() — https://gsap.com/docs/v3/GSAP/gsap.matchMedia()/ ; SplitText — https://gsap.com/docs/v3/Plugins/SplitText/
- GSAP: 3.10 release — https://gsap.com/blog/3-10/ ; common ScrollTrigger mistakes — https://gsap.com/resources/st-mistakes/ ; 3.13 (all plugins free) — https://gsap.com/blog/3-13/
- Lenis README — https://github.com/darkroomengineering/lenis
- Motion: useScroll — https://motion.dev/docs/react-use-scroll ; useTransform — https://motion.dev/docs/react-use-transform
- Chrome, Performant parallaxing (2016) — https://developer.chrome.com/blog/performant-parallaxing
- Video scrubbing: muffinman.io — https://muffinman.io/blog/scrubbing-videos-using-javascript/ ; Hon Tran — https://www.hontran.dev/blog/scroll-scrubbed-video-stutters-fix
- CSS-Tricks, Apple-style scrolling image sequence — https://css-tricks.com/?p=308477
- MDN, ::scroll-button() — https://developer.mozilla.org/en-US/docs/Web/CSS/::scroll-button
- WCAG 2.3.3 — https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html ; 2.2.2 — https://www.w3.org/WAI/WCAG22/Understanding/pause-stop-hide.html
- Awwwards pages for the example sites — https://www.awwwards.com/sites/lando-norris , https://www.awwwards.com/sites/igloo-inc , https://www.awwwards.com/mapping-the-uncharted-the-san-rita-project.html , https://www.awwwards.com/floema-spaces-for-people-made-for-life.html , https://www.awwwards.com/sites/a-cosmic-scroll-journey , https://www.awwwards.com/inspiration/scrollytelling-vizcom , https://www.awwwards.com/inspiration/zoom-scroll-intro-telescope , https://www.awwwards.com/sites/lenis-2
- GSAP showcase — https://gsap.com/showcase/
- The Pudding, How to implement scrollytelling — https://pudding.cool/process/how-to-implement-scrollytelling/
