# Cinematic recipes, batch a

Five copy-ready signature effects for `design-atlas`. They are about **light and passage**: a torch in the dark, a lighthouse sweep over type, a point of light that opens into the page, a pinned word-and-picture swap, and a camera that flies through a window. Each is one self-contained HTML file at `skills/design-atlas/examples/<slug>/index.html`, 16–22 KB, with no build step and no image files (all scenes are CSS or inline SVG). Four are vanilla JS; `word-swap-hero` uses GSAP 3.13 ScrollTrigger plus optional Lenis 1.3.4. Every file opens with a header comment covering what it is, the story it serves, when to use and avoid it, ambition, knobs, perf and a11y.

How each recipe was tested (2026-10-10):
- Served over `python3 -m http.server 8791` from the repo root and shot with `skills/design-atlas/scripts/shoot.mjs`: viewport-only jobs at 5–9 positions through the effect, at 1440×900 and 390×844, plus a reduced-motion job at each width. Pointer recipes used `eval` to dispatch synthetic `pointermove`/`pointerdown`. The intro was shot at fixed times after `lumenIntro.replay()`.
- The shots went into Pillow contact sheets, which I reviewed by eye. I iterated on each recipe 2–3 times (fixes are listed under "Gotchas").
- Perf: a CDP script auto-scrolled the page for 2 s with rAF (or swept the pointer, or idled through the intro). It recorded frame intervals and **main-thread ms per frame** (`Performance.getMetrics` TaskDuration delta ÷ frames).

**Probe status.** No final run had console errors, horizontal overflow (`overflowX` = 0 at 390 px), small targets, missing `lang`, or anything other than exactly one h1. The overflow "offenders" listed in the JSON are decorative layers clipped by an `overflow:hidden` stage: the blueprint/beam/land/shaft layers, SVG slices, and the card while it scales to full-bleed. Two recipes report "content still invisible" **by design**:
- intro-iris: hero text waits for its entrance while the curtain is still black. These are frames shot during the intro.
- zoom-through: the near h1 fades out as the camera passes it, and the far h2 is transparent before the camera reaches it.

Both texts stay in the DOM and the accessibility tree.

**Reading the perf numbers.** Four other agents were rendering at the same time. Load average ran from about 30 to over 700 during this session, and under that load headless Chrome drops to 30 fps or worse. The final matrix below was therefore run by `tools-a/perf-all.sh`, which waits until the 1-minute load average is under 40. It ran at a 1-minute load of 21–38, with the 5-minute average still around 300, so the rare single-frame hitches are most likely the machine, not the page.

The frame-interval columns are vsync-quantised and only show that no frames were dropped at 60 fps. The more useful figure is main-thread ms per frame (2 s of auto-scroll, a pointer sweep, or the intro). Raster and compositing happen off the main thread and are not counted, which matters for the spotlight/light-text gradient repaints on low-end GPUs. All numbers are indicative; none were measured on a real phone.

| Recipe | Ambition | Palette / type | Tech | Main thread ms/frame 1440 / 390 | Interval median / p95 |
|---|---|---|---|---|---|
| spotlight-reveal | bold / cinematic | midnight navy + brass + lume green · Cormorant Garamond + Trirong | vanilla, radial-gradient on custom props, lerp | 0.44 / 0.44 | 16.7 / 16.8 (pointer sweep) · 16.7 / 16.7 (390 auto-light), 0 frames > 20 ms |
| light-text | cinematic | night sea + lamp gold + ember · Bricolage Grotesque + Kanit | vanilla, background-clip:text per line, beam wedge, bloom copy | 0.75 / 0.58 (re-run 0.64) | 16.7 / 16.8 · 16.7 / 16.7; one 100 ms hitch in 1 of 3 runs |
| intro-iris | cinematic | bone + terracotta + ink, dusk sky · Instrument Serif + IBM Plex Sans Thai | vanilla, WAAPI on `@property --iris`, clip-path circle | 0.47 / 0.46 | 16.7 / 16.7–16.8; a 180–330 ms one-frame hitch in 3 of 12 runs, with or without the grain layer (machine load) |
| word-swap-hero | bold | cream + ink + cobalt, 4 scene palettes · Archivo (wdth) + Anuphan | GSAP ScrollTrigger pin + scrub, optional Lenis | 0.46 / 0.45 | 16.7 / 16.7–16.8; 1–2 frames > 20 ms per run (max 100–167 ms) |
| zoom-through | cinematic | forest interior + peach dawn + mist · Fraunces + Noto Sans Thai | vanilla sticky + lerp, box-shadow hole, 5 depth layers | 0.54 / 0.54 | 16.7 / 16.8, 0 frames > 20 ms |

Raw outputs: probe JSON in `…/scratchpad/recipes/logs/<slug>-shoot.json`, perf lines in `…/scratchpad/recipes/logs/perf-a.jsonl`. Tools are in `…/scratchpad/recipes/tools-a/` (`perf.mjs`, `probe.mjs`, `sheet.py`, `run.sh`). Here `…` is `/private/tmp/claude-501/-Users-thanaphatnorth-Desktop-ai-skills-north-ai-skills/b3acc423-6456-4200-b4ca-c215c443d2cc`.

**Strongest:** zoom-through and intro-iris look the most "award-site" (cinematic, with a clear story), and spotlight-reveal is the most distinctive. light-text is the most reusable for a type-led brand. word-swap-hero is the most commercially useful (SaaS/multi-vertical).

---

## 1. Spotlight reveal · `spotlight-reveal`

- **Feeling / story:** discovery and intimacy; "the secret is in the details". The fictional brand is Kāla Atelier, a Bangkok watchmaker. In near-total darkness the pointer is a soft torch. It reveals the headline, an illustrated watch dial, a blueprint drawn behind the dial (Ø 38.0 MM, PLATE 3/7), and four engraved notes in the corners (guilloché, calibre, moon phase, Nº 017/100) that are only legible inside the beam. Luminous hour markers glow faintly above the dark, so the page is never empty.
- **Use when:** one hero moment with few words and a product with details worth hunting for (watches, perfume, jewellery, a gallery opening, a teaser, a night bar or hotel).
- **Avoid when:** the page must be scanned fast (pricing, docs, forms), or the hero holds information users need right away.
- **Ambition:** bold / cinematic.
- **Tech:** vanilla. A `.dark` overlay paints `radial-gradient(circle at var(--x) var(--y) …)` with color stops in multiples of `--r`. JS lerps `--x/--y` toward the target each frame, frame-rate independently. A second SVG (`.lume`) sits **above** the darkness (z-index 3) so the lume glows in the dark. Static SVG grain uses `mix-blend-mode: overlay`.
- **Perf budget:** < 4 ms per frame on a mid laptop: one full-stage gradient repaint while the light moves. Measured: see table. The loop stops when the pointer light settles, when the stage is offscreen (IntersectionObserver), or when the lights are on.
- **Key code** (the parts an agent must get right):

```css
.dark{position:absolute;inset:0;z-index:2;pointer-events:none;
  background:radial-gradient(circle at var(--x) var(--y),
    rgba(255,214,160,.07) 0,rgba(6,7,11,0) calc(var(--r)*.22),     /* warm, clear core */
    rgba(6,7,11,.38) calc(var(--r)*.55),rgba(6,7,11,.82) var(--r), /* soft penumbra */
    rgba(6,7,11,var(--ambient)) calc(var(--r)*1.9));               /* ambient: never pitch black */
  transition:opacity 1.1s var(--ease-standard)}
.stage.is-lit .dark{opacity:0}                 /* "Turn on the lights" */
.lume{z-index:3}                               /* glows above the dark */
```
```js
function frame(now) {
  raf = 0;
  const dt = Math.min(64, last ? now - last : 16.7); last = now;
  const wandering = now - userAt > (hold || CFG.idle);
  if (wandering) {   // auto-light for touch / no pointer: Lissajous path inside the VISIBLE part of the stage
    const t = now / 1000, v0 = Math.max(0, scrollY - top), v1 = Math.min(H, scrollY - top + innerHeight);
    tx = W * (0.52 + 0.3 * Math.sin(t * 0.21)); ty = v0 + (v1 - v0) * (0.5 + 0.26 * Math.sin(t * 0.33 + 1.2));
  }
  const k = 1 - Math.pow(1 - CFG.follow, dt / 16.7);          // frame-rate independent lerp
  x += (tx - x) * k; y += (ty - y) * k;
  put(x, y, R * (1 + CFG.breathe * Math.sin(now / 820)));
  const settled = !wandering && Math.abs(tx - x) < 0.4 && Math.abs(ty - y) < 0.4;
  if (onScreen && !lit && !settled) raf = requestAnimationFrame(frame); else last = 0;
}
addEventListener('pointermove', (e) => { if (e.pointerType !== 'touch') aim(e.clientX, e.clientY, 0); }, { passive: true });
stage.addEventListener('pointerdown', (e) => { if (e.pointerType === 'touch') aim(e.clientX, e.clientY, CFG.holdTap); });
stage.addEventListener('focusin', (e) => { const r = e.target.getBoundingClientRect(); aim(r.left + r.width / 2, r.top + r.height / 2, 4000); });
```
- **Knobs:** CSS `--ambient` (0–1 darkness outside the beam), `--night/--brass/--cream/--lume`. JS `CFG.follow` (lerp), `idle` (ms before the auto-light wanders again), `holdTap`, `rMin/rMax` (radius clamp, 0.34 × the smaller stage side), and `breathe`.
- **Reduced motion:** no loop. The light is static on the dial with 1.45× radius and `--ambient` drops to 0.55, so everything reads. This is a composed still, and the lights toggle still works.
- **Mobile / touch:** the auto-light wanders slowly through the visible part of the stage. A tap aims it and holds for 2.6 s. The hint text switches to "Tap to aim the light · แตะเพื่อส่องไฟ". Notes become a 2-column grid under the dial, and the blueprint is trimmed so nothing overflows.
- **A11y:** real text in DOM order. "Turn on the lights" button (`aria-pressed`, also the L key). Keyboard focus pulls the light to the focused control. Decorative SVG is `aria-hidden`.
- **Gotchas hit:**
  - Headless Chrome fires no `focus`/`focusin` when the page isn't focused (`document.hasFocus()` = false), so the focus-follow looked broken in shots. The page was fine. The shot job now dispatches `FocusEvent('focusin')` after `.focus()`; the alternative is CDP `Emulation.setFocusEmulationEnabled`.
  - Notes wrapped mid-phrase ("YRS." alone on a line), fixed by widening them to 17em.
  - The blueprint label "R 19.0" collided with a Thai note, so I removed it.
  - The first auto-light wandered below the fold on mobile (the stage is taller than the viewport). The path is now clamped to the visible slice.
- **Contact sheet:** `…/scratchpad/recipes/spotlight-reveal/sheet.png`

## 2. Light text · `light-text`

- **Feeling / story:** guidance, arrival, "a light left on for you". The fictional brand is Phare Lanta, six rooms in a working lighthouse. The four-line headline "Light finds / its way home. / แสงนำทางคุณ / กลับบ้านเสมอ" is dark until a lighthouse beam sweeps across it line by line. Lit lines keep a warm afterglow, and the sequence ends on a fully lit headline.
- **Use when:** the headline IS the hero, in 2–5 short lines at display size (≥ ~48 px).
- **Avoid when:** long copy, small type, pages people must scan, or any information users need before the light arrives.
- **Ambition:** cinematic.
- **Tech:** vanilla. Each `.ln` is `display:block; width:fit-content` and painted with `background: var(--light) no-repeat, var(--base)` plus `background-clip:text`. JS sets per-line `--x/--y` (the shared light point converted to that line's box), `--rad` and `--base` (unlit → ember afterglow). A rotating `.beam` wedge (clip-path triangle, `mix-blend-mode:screen`) runs from the lamp to the hot spot, alongside a `.halo` blob and a blurred aria-hidden copy of the lines (bloom). Scroll drives a pinned sticky stage (`height:(lines+1.4)×100vh`). Add `?time` for a time-driven loop instead (no pin).
- **Perf budget:** ≤ 6 ms per frame on a mid laptop: per-line gradient repaints plus a blurred bloom copy, with beam and halo transform-only. If you need headroom, turn bloom off first (it is already off under 700 px).
- **Key code** (condensed from the file; see `render()` there for the full final-phase lerp):

```css
.ln{--rad:240px;--x:-9999px;--y:50%;--base:var(--unlit);display:block;width:fit-content;
  padding:.1em .06em .12em;margin:-.1em -.06em -.12em;          /* glyphs must stay INSIDE the box */
  --light:radial-gradient(circle var(--rad) at var(--x) var(--y),#fff8e8 0,#ffd88f calc(var(--rad)*.16),
          #f39a3c calc(var(--rad)*.42),rgba(190,90,30,0) var(--rad));
  color:transparent;background:var(--light) no-repeat,var(--base);-webkit-background-clip:text;background-clip:text}
.ln:lang(th){line-height:1.08;padding-top:.16em;padding-bottom:.14em}   /* Thai marks above/below */
.bloom{position:absolute;inset:0;filter:blur(16px);opacity:.8;mix-blend-mode:screen;pointer-events:none}
.bloom .ln{background:var(--light) no-repeat;-webkit-background-clip:text;background-clip:text}
@supports not ((background-clip:text) or (-webkit-background-clip:text)){.ln{color:var(--gold)}.bloom{display:none}}
```
```js
function render(p, now) {                         // p = smoothed scroll progress 0..1
  const N = L.length, A = 0.07, B = 0.84; let hx, hy, r = R, inten = 1, q;
  if (p < A) { q = 0; hx = L[0].x - R * 0.45; hy = L[0].y + L[0].h * 0.55; inten = smooth(p / A); }   // light arrives
  else if (p < B) {                               // sweep line i left -> right; dims at the ends ("beam turns away")
    q = (p - A) / (B - A) * N; const i = Math.min(N - 1, Math.floor(q)), e = smooth(q - i), l = L[i];
    hx = l.x - R * 0.45 + (l.w + R * 0.9) * e; hy = l.y + l.h * 0.55; inten = Math.min(1, 0.35 + Math.sin(Math.PI * e) * 0.9);
  } else {                                        // park on the headline centre and open up: composed final state
    const e = smooth((p - B) / (1 - B)), l = L[N - 1]; q = N; /* lerp hx,hy to centre */ r = R * (1 + 2.4 * e); inten = 1 - 0.3 * e;
  }
  r *= Math.max(0.004, inten);
  L.forEach((l, j) => {
    const g = Math.min(1, Math.max(0, (q - j - 0.7) / 0.5));          // afterglow once passed
    for (const el of [l.el, l.b]) { el.style.setProperty('--x', hx - l.x + 'px'); el.style.setProperty('--y', hy - l.y + 'px'); el.style.setProperty('--rad', r + 'px'); }
    l.el.style.setProperty('--base', `rgb(${mix(UNLIT, EMBER, g)})`);
  });
  beam.style.transform = `translate(${lamp[0]}px,${lamp[1] - beam.offsetHeight / 2}px) rotate(${Math.atan2(hy - lamp[1], hx - lamp[0])}rad) scaleX(…)`;
}
```
- **Knobs:** CSS `--unlit/--ember/--gold/--night` and `--lines` (pin length). JS `CFG.drive` (`'scroll'` or `'time'`, also set by `?time`), `smooth`, `period` (time mode), `bloom`, and `radius` (× font size).
- **Reduced motion:** no pin and no sweep. The section is one viewport showing `render(1)`: the headline fully lit in warm gold with a static beam from the lamp.
- **Mobile:** the same sweep with bloom off. The lighthouse stands bottom-right on a headland and the beam angles steeply up to the type. Font size is `min(12.6vw, 15.5vh)`.
- **Gotchas hit:**
  - With `background-clip:text`, anything outside the element box is not painted. Thai tone marks and English descenders would vanish, so every line gets padding with an equal negative margin, and Thai lines get extra padding.
  - At progress 0 the gradient was already lighting the "L", because intensity only drove the beam and not the text light. The text radius is now multiplied by intensity.
  - Four lines at 12.6vw overflowed a 900 px viewport; size by `min(vw, vh)`.
  - The sea reflection sat on land, so I removed it. The horizon line cut through the Thai line, so I moved it to 84%.
  - `background-attachment:fixed` would avoid per-line coordinates, but it is unreliable on iOS, so I didn't use it.
- **Contact sheet:** `…/scratchpad/recipes/light-text/sheet.png`

## 3. Intro iris · `intro-iris`

- **Feeling / story:** arrival, "let there be light", a curtain rising. The fictional brand is Atelier Lumen, an architecture studio. Black screen → one breathing point of light → the point opens into an iris with a glowing rim → the page is a sunlit arched room, and the point of light **lands on the sun** in the arch, so the intro belongs to the story instead of being a loader. A drafting annotation ("06:12 · first light") ties the sun to the brand.
- **Use when:** brand-led landing pages people open on purpose, with a natural light source you can put at the viewport centre.
- **Avoid when:** task pages, search/ad landing pages, return visits, or anything people open many times a day.
- **Ambition:** cinematic.
- **Tech:** vanilla. An inline `<head>` script decides before first paint, from sessionStorage, `?intro` and reduced motion. `@property --iris {syntax:'<length>'; inherits:false}` lets WAAPI animate one length on two elements: the page's `clip-path: circle(var(--iris) at var(--cx) var(--cy))` and the rim's radial-gradient ring. The hero staggers in with a CSS keyframe `rise` driven by `--i`.
- **Rules kept:**
  - The intro plays once per session.
  - A visible **Skip** button (and Esc) is always available.
  - The first wheel, touch, key or click opens the iris at once; a second one plays it at 2× speed instead of jumping.
  - Scroll is locked only until the iris finishes and never longer than `CFG.maxLock` (2.5 s). There is a hard `finish()` cap at 3.7 s.
  - A CSS-only safety net covers the case where the main script never runs: after 2.6 s, keyframes set `overflow:visible` on html and `clip-path:none` on the page, and hide the curtain. On the normal path the iris has already finished by then, so the net changes nothing. To test it, I killed every timer right after `replay()`: the page was locked at 2.3 s and visible and scrollable at 4.6 s.
  - With reduced motion or no JS, the page shows immediately.
- **Perf budget:** ~1.25 s of clip-path plus one full-screen gradient repaint per frame. Nothing runs afterwards. Measured: see table.
- **Key code:**

```html
<script>/* in <head>: decide before first paint so returning visitors never see a black flash */
(function () { var d = document.documentElement, seen = null;
  try { seen = sessionStorage.getItem('lumen-intro'); } catch (e) {}
  if ((/[?&]intro\b/.test(location.search) || !seen) && !matchMedia('(prefers-reduced-motion: reduce)').matches)
    d.classList.add('has-intro', 'lock'); })();
</script>
<style>
@property --iris{syntax:'<length>';inherits:false;initial-value:0px}
html.lock{overflow:hidden} html{scrollbar-gutter:stable}
.has-intro body{background:#000}
.has-intro .page{clip-path:circle(var(--iris) at var(--cx,50vw) var(--cy,50vh))}
.rim{background:radial-gradient(circle at 50% 50%,rgba(255,240,215,0) calc(var(--iris) - 2px),
  rgba(255,244,224,.95) var(--iris),rgba(255,196,130,.32) calc(var(--iris) + 12px),rgba(255,180,110,0) calc(var(--iris) + 110px))}
.has-intro [data-in]{opacity:0}
.has-intro.play [data-in]{animation:rise 1s var(--ease-emphasized-out) both;animation-delay:calc(260ms + var(--i,0) * 90ms)}
</style>
<script>
function open() {                                   // auto at 1.2 s or on first interaction
  const R = Math.hypot(innerWidth, innerHeight) / 2 + 60;
  page.style.setProperty('--cy', scrollY + innerHeight / 2 + 'px');   // circle centre is in PAGE coordinates
  root.classList.add('play');
  const t = { duration: 1250, fill: 'forwards' }, k = (r, o, x) => Object.assign({ '--iris': r + 'px', offset: o }, x);
  // emphasized = emphasized-in for 40 % (the iris is SEEN growing), then emphasized-out (it bursts open)
  anims.push(page.animate([k(0, 0, { easing: easeIn }), k(R * 0.16, 0.4, { easing: easeOut }), k(R, 1)], t));
  anims.push(rim.animate([k(0, 0, { easing: easeIn, opacity: 1 }), k(R * 0.16, 0.4, { easing: easeOut, opacity: 1 }), k(R, 1, { opacity: 0 })], t));
  anims[0].finished.then(() => later(finish, 900));
  later(unlock, 1250);
}
// start(): sessionStorage.setItem; later(open, 1200); later(unlock, 2500 /* maxLock */); later(finish, 3700);
// window.lumenIntro = { replay(), skip() }  — for design review and tests
</script>
```
- **Knobs:** `CFG.autoOpen` (1200 ms), `irisMs` (1250), `maxLock` (2500), `storageKey`. Add `?intro` to force a replay, or call `lumenIntro.replay()` / `.skip()`. CSS `--arch-top` / `--arch-w` keep the sun at the viewport centre, and `--bone/--clay/--ink` set the palette.
- **Reduced motion:** the head script never adds `has-intro`, so the page is there at first paint. Verified: `<html>` class is empty under reduce.
- **Mobile:** the same intro. The headline sits above the arch; the Thai copy and CTA sit on the floor band.
- **Fallback:** without `CSS.registerProperty`, the curtain is black from the start and simply fades out.
- **Gotchas hit:**
  - With `--ease-emphasized-out` alone, the iris was 90% open within 180 ms and nobody saw an iris. Splitting the curve into the two emphasized halves fixed it.
  - `circle(… at 50% 50%)` on a tall page is relative to the page box, not the viewport. Centre it at `scrollY + innerHeight/2` in px.
  - Replay needs a style flush (`void el.offsetWidth`) between removing and re-adding the class, or canceled CSS animations don't restart.
  - The desktop headline wrapped to 3 lines in the side column. I narrowed the arch to 22vw and sized the h1 at 5.6vw.
  - Probe "invisible" in the timed intro frames is expected.
- **Contact sheet:** `…/scratchpad/recipes/intro-iris/sheet.png` (row 1: t = 120, 600, 1000, 1450 ms; row 2: 1700, 1900, 2300, 3600 ms; then early-wheel and page frames)

## 4. Word-swap hero · `word-swap-hero`

- **Feeling / story:** "this was made for you, whoever you are". The fictional brand is nadd., a booking SaaS, in the style of jongque.com. A big "Your ___." headline sits over a framed image card, and scrolling swaps **studio → clinic → salon → café**. Each swap brings a bottom-up wipe of the scene, a Thai subline swap (ระบบจองคิวออนไลน์สำหรับ…ของคุณ), and a booking chip per scene ("Reformer · 07:30 · จองแล้ว 8 จาก 10 ที่"). Side widgets (today's queue, −62% no-shows) drift at their own depth. The card then scales to full-bleed and the dark next section slides over it.
- **Use when:** 3–5 audiences or variants share one promise and each has a strong picture.
- **Avoid when:** there is one audience (just say it), or the variants need explaining (use tabs or cards).
- **Ambition:** bold.
- **Tech:** GSAP 3.13 ScrollTrigger: `pin: .stage`, `scrub: 0.8`, `end: +=400vh`, `invalidateOnRefresh`, inside `gsap.matchMedia()`. Lenis 1.3.4 is optional: skipped with `?nolenis`, `navigator.webdriver` or reduced motion. The scenes are inline SVG with `preserveAspectRatio="xMidYMid slice"`, so the same art crops to 5:4 on desktop and 4:5 on mobile. The next section uses `margin-top:-100vh; z-index` so it slides over during the final 25% hold.
- **Perf budget:** < 4 ms main thread per frame: transforms, plus one clip-path inset on one card.
- **Key code:**

```js
// geometry from UNTRANSFORMED boxes, relative to the pinned stage (lesson gsap-absorbs-css-translate)
function geo() {
  const s = stage.getBoundingClientRect(), c = cardpos.getBoundingClientRect(), inset = 10;
  const scale = Math.max(s.width / (c.width - inset * 2), s.height / (c.height - inset * 2)) * 1.04;
  return { dx: s.width / 2 - (c.left - s.left + c.width / 2), dy: s.height / 2 - (c.top - s.top + c.height / 2), scale };
}
// keep the visible line centred when words differ in width: shift the whole line, never animate width
const shift = (l, i) => { const w = l.words.map((e) => e.offsetWidth), max = Math.max(...w); return (max - w[i]) / 2; };
mm.add('(prefers-reduced-motion: no-preference)', () => {
  gsap.set(scenes.slice(1), { clipPath: 'inset(100% 0% 0% 0%)' });
  const tl = gsap.timeline({ defaults: { ease: 'power2.inOut', duration: 1 },
    scrollTrigger: { trigger: '.hero', start: 'top top', end: () => '+=' + innerHeight * 4, pin: stage, scrub: 0.8, invalidateOnRefresh: true } });
  tl.to({}, { duration: 0.5 });
  for (let i = 1; i < N; i++) {
    const at = tl.duration();
    // the word rolls in the middle third of the wipe, so a paused scroll almost always rests on a whole word
    lines.forEach((l) => tl.to(l.track, { yPercent: -100 * i / N, duration: 0.36, ease: 'power3.inOut' }, at + 0.32)
                           .to(l.line, { x: () => shift(l, i), duration: 0.36, ease: 'power3.inOut' }, at + 0.32));
    tl.fromTo(scenes[i], { clipPath: 'inset(100% 0% 0% 0%)' }, { clipPath: 'inset(0% 0% 0% 0%)', ease: 'power3.inOut' }, at)
      .to(arts[i - 1], { scale: 1.1, yPercent: -5, ease: 'power1.in' }, at)          // old scene recedes
      .fromTo(arts[i], { scale: 1.12 }, { scale: 1, ease: 'power2.out' }, at)        // new scene settles
      .to(chips[i - 1], { autoAlpha: 0, y: -16, duration: 0.4 }, at)
      .to(chips[i], { autoAlpha: 1, y: 0, duration: 0.5, ease: 'power2.out' }, at + 0.55)
      .to({}, { duration: 0.5 });                                                     // rest on the word
  }
  const z = tl.duration();
  tl.to('.headwrap', { y: () => -innerHeight * 0.22, autoAlpha: 0, duration: 0.8, ease: 'power2.in' }, z)
    .to(cardzoom, { x: () => geo().dx, y: () => geo().dy, scale: () => geo().scale, duration: 1.4, ease: 'power3.inOut' }, z)
    .to(frame, { autoAlpha: 0, duration: 0.5 }, z + 0.7)
    .to(scenesBox, { borderRadius: 0, duration: 0.5 }, z + 0.9)
    .to({}, { duration: 2.2 });            // full-bleed hold = the last 25 % of the pin, while .next (margin-top:-100vh) slides over
});
```
- **Knobs:** the words, scenes and chips in the markup (keep the EN track, TH track, scenes and chips the same length). `CFG.pinVh`, `scrub`, `holdEnd`, `lenis`. CSS `--card-w` / `--card-ar` and the palette.
- **Reduced motion / no JS / GSAP failed:** the head script adds `.motion` only when motion is allowed, and every static rule is `html:not(.motion) …`. The static view shows the full sentence "Your studio, clinic, salon or café." (the h1's screen-reader text, now visible), the Thai sentence, and all four scenes in a 2×2 grid (1 column on mobile).
- **Mobile:** the same pinned sequence with a 4:5 card, side widgets hidden, and `font-stretch:100%` so "clinic." fits at 390 px.
- **Gotchas hit:**
  - I followed the user's lesson. `.cardpos` is positioned by flex and measured; the tween target is the inner `.cardzoom`; nothing animated has CSS `translate` or `transition:transform`.
  - A centred headline with a fixed-width word slot sits off-centre for short words. I shifted the whole line by `(max − w)/2` with a transform, which avoids animating width.
  - A scrubbed word roll leaves half-words when the user stops mid-way. The roll now happens only in the middle third of each wipe.
  - `navigator.webdriver` is **false** in `shoot.mjs`'s headless Chrome, so tests must pass `?nolenis`. A check with Lenis on still drove the timeline from `scrollTo` (scene 2 revealed, track at −25%).
  - "ลด / การเบี้ยวนัด" broke mid-phrase in a narrow widget, so the Thai went on its own line.
  - The lesson's resize/reload test was run over CDP:
    - Reload at 80% progress: the full-bleed card still covers the stage (card −51…1491 × −167…1067 on 1440×900).
    - Resize to 390×844, then scroll back to 80%: it still covers (−173…563 × −38…882).
    - Resize back to 1440: identical to the first measurement.

    Note that a viewport resize resets `scrollY` in headless mobile emulation, so re-scroll before you assert.
- **Contact sheet:** `…/scratchpad/recipes/word-swap-hero/sheet.png`

## 5. Zoom-through · `zoom-through`

- **Feeling / story:** step into the picture; escape and arrival. The fictional brand is Doi Mok Retreat, misty mountain cabins in Chiang Mai. A dark timber interior with a pendant lamp looks through an arched window at a dawn sea of mist. Scrolling flies the camera through the window:
  - the wall scales around the window centre until it leaves the frame;
  - the plant and steaming cup on the sill pass under the camera;
  - five landscape layers scale and sink at their own depths;
  - the near h1 "Step into the mist." rushes past faster than the wall;
  - the far h2 "Where the clouds come to rest." settles into the sky.
- **Use when:** the next section IS a place or a world and the pin is the doorway between two sections (travel, retreats, real estate with a view, a film or game world, a museum collection).
- **Avoid when:** content-dense pages, frequent visits, or a destination that isn't visual.
- **Ambition:** cinematic.
- **Tech:** vanilla `position:sticky` inside a 400vh section, with one lerped rAF loop that writes transform/opacity on 8 layers. The wall is the **box-shadow of the window hole** (`0 0 0 160vmax var(--wall)`), so one element scaled with `transform-origin` at the hole centre is the whole "mask". The inset shadow gives the window depth and a `::after` glass streak passes the camera. Mist bands drift on a CSS animation (compositor), paused offscreen. Header text turns dark only when both header corners are inside the scaled arched opening.
- **Perf budget:** < 3 ms per frame, transform/opacity only. The wall raster is scaled up to 10× (slightly soft, invisible in motion).
- **Key code:**

```css
.hole{position:absolute;left:calc(var(--hx) - var(--hw) / 2);top:calc(var(--hy) - var(--hh) / 2);
  width:var(--hw);height:var(--hh);border-radius:999px 999px 4px 4px;            /* arched opening */
  box-shadow:inset 0 18px 40px rgba(10,16,14,.35),0 0 0 3px #2a1b10,0 0 0 15px var(--timber),
             0 0 0 17px #2a1b10,0 0 0 160vmax var(--wall)}                         /* frame + the whole wall */
```
```js
function measure() {
  const s = stage.getBoundingClientRect(), r = hole.getBoundingClientRect();
  const cx = r.left - s.left + r.width / 2, cy = r.top - s.top + r.height / 2, W = s.width; H = s.height;
  const straight = r.height - r.width / 2;          // the arch top doesn't count: cover with the straight part
  exitScale = Math.max((2 * Math.max(cx, W - cx)) / r.width, (2 * Math.max(cy, H - cy)) / straight) * 1.25;
  const origin = `${cx}px ${cy}px`; room.style.transformOrigin = origin; layers.forEach((l) => (l.style.transformOrigin = origin));
}
function render(p) {                                 // p = lerped progress of the 300vh pin
  const w = inCubic(clamp(p / CFG.wallExit));        // wall: slow start, then rushes past the camera
  room.style.transform = `scale(${1 + (exitScale - 1) * w})`;
  room.style.opacity = p >= CFG.wallExit ? 0 : 1;
  const d = inOut(clamp(p / 0.95));                  // depth: sky 0.05 … foreground 1.6, plus sink
  layers.forEach((l, i) => (l.style.transform = `translate3d(0,${CFG.sink[i] * d * H}px,0) scale(${1 + CFG.depth[i] * d})`));
  const n = clamp((p - 0.02) / 0.3);                 // near headline: faster than the wall
  near.style.opacity = 1 - out(n);
  near.style.transform = `translate3d(${-n * 9}vw,${-n * 7}vh,0) scale(${1 + n * 0.7})`;
  const f = clamp((p - 0.58) / 0.27);                // far headline: slow, deep in the scene
  far.style.opacity = out(f);
  far.style.transform = `translate3d(0,${(1 - out(f)) * 4}vh,0) scale(${0.92 + 0.08 * out(f)})`;
}
```
- **Knobs:** `CFG.smooth`, `wallExit` (0.6), `depth[]`, `sink[]`; CSS `--hx/--hy/--hw` (window centre and width), `--wall`, `--timber`, palette; mist speed in `@keyframes drift`; pin length in `.zoom{height:400vh}`.
- **Reduced motion:** no pin and no zoom. The composed window view is shown with both headlines on the wall (the far line moves under the h1 in cream), and the mist stands still.
- **Mobile:** the window is centred at 57% height with 56vw width. The headline sits above it, and the pendant and lamp glow are hidden. The flythrough is the same, and the sill objects pass under the camera very visibly.
- **Gotchas hit:**
  - The lamp glow was invisible because it came before the hole in the DOM, so the hole's box-shadow wall painted over it. Order matters with box-shadow walls.
  - Cream header text on the peach sky was unreadable. A threshold on progress was wrong per viewport, so I replaced it with a point-in-scaled-arch test.
  - The probe flags the cross-faded headlines (deliberate).
- **Contact sheet:** `…/scratchpad/recipes/zoom-through/sheet.png`

---

## Cross-recipe notes for the skill

- The test hooks are worth copying into every recipe: `?intro`, `?time`, `?nolenis`, and `window.<name>.replay()/skip()`. They made deterministic shots possible and also serve design review.
- In `shoot.mjs` jobs, programmatic `.focus()` does not fire focus events (the page has no focus). Dispatch `FocusEvent('focusin')` or use focus emulation.
- When several agents share a machine, frame intervals stop telling you anything. Report main-thread ms/frame next to them.
- The shared scratchpad `recipes/tools/` was overwritten by a parallel batch (and briefly by me). Each batch should use its own tools folder (this batch used `tools-a/`).
