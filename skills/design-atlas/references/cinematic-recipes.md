# Cinematic recipes (tested demos in `examples/`)

> Read when: building the signature experience of a bold or cinematic page (Step 6); you need a light, darkness, line, particle, shader, kinetic-type or transition effect that works on phones, respects reduced motion and has been checked frame by frame; adapting an effect to a new concept from `creative-direction.md`.

**Contents:** Choosing between them · How to use these · Conventions · Build your own story · Light trail · Spotlight reveal · Light text · Intro iris · Word-swap hero · Zoom-through · Particle constellation · Aurora shader · Velocity gallery · Glow cursor CTA · Mask transitions · Testing notes · Pitfalls · Sources

## Choosing between them

| Demo | Concept it enacts | Ambition | Libraries | Main-thread cost (headless) | Light / dark |
|---|---|---|---|---|---|
| `light-trail` | dark → light, lost → home, off → on | cinematic | none | < 1 ms | dark → dawn |
| `spotlight-reveal` | discovery, craft hidden in the dark | bold → cinematic | none | < 1 ms | dark |
| `light-text` | reverence, a beam finding the words | bold | none | < 1 ms | dark |
| `intro-iris` | arrival, a premiere | bold → cinematic | none | < 1 ms | dark → page |
| `word-swap-hero` | "this is for you" across audiences | bold | GSAP 3.13 (+ optional Lenis) | < 1 ms | light |
| `zoom-through` | entering a place, transformation | cinematic | none | < 1 ms | dusk → sunrise |
| `particle-constellation` | scattered → gathered, a community, a name made of stars | cinematic | none | 2.4–5.7 ms | dark |
| `aurora-shader` | calm energy, sleep, premium tech | bold | none (raw WebGL) | < 1 ms CPU | dark |
| `velocity-gallery` | momentum, collections, portfolio | bold | none | 0.4–1 ms | light |
| `glow-cursor-cta` | invitation, playfulness, events | bold | none | ~1.3 ms | dark |
| `mask-transitions` | chapters, acts, editorial rhythm | bold → cinematic | none | < 1 ms | mixed |

Light-themed brands (beauty, health, retail) adapt best from `word-swap-hero`, `velocity-gallery`, `zoom-through` and `mask-transitions`; the dark light-and-particle demos suit night, energy, perfume, entertainment, tech. Every demo's reduced-motion composition is designed, not a fallback afterthought.

## How to use these

1. Pick the mechanic that enacts your concept (`creative-direction.md` §2, §6). The effect serves the metaphor; never pick an effect first and invent a story for it.
2. Copy `examples/<slug>/index.html` into the project, keep its structure (sticky stage, capture hook, reduced-motion composition), then change the art direction: palette from `scripts/palette.py`, type pair, copy beats, path or shape data, CONFIG knobs.
3. Re-run the QA in `creative-direction.md` §9 on *your* version: contact sheet at 1440 and 390 px, film + frame scan, reduced-motion frame, probes clean.
4. Port to the project's framework only after it looks right as a standalone page (React: keep the effect in one component that owns its rAF loop and cleans up on unmount; `useEffect` + refs, no per-frame React state).

## Conventions

Shared by every demo: one self-contained `index.html`, vanilla JS or pinned CDN libraries (GSAP 3.13, Lenis 1.3.4, three.js r170 via jsdelivr), Thai + English copy and a fictional brand; a designed `prefers-reduced-motion` composition; copy as real DOM text with art `aria-hidden` and one `h1`; one rAF loop that sleeps when idle, offscreen or in a hidden tab; canvas DPR ≤ 2.

Test hooks differ per demo (each section below lists its own): `light-trail` has the full capture convention (`?capture` + `window.__frame(dt)`, `<html class="rm">` static-first, `data-story`); `intro-iris` has `?intro` and `lumenIntro.replay()/skip()`; `light-text` has `?time`; `aurora-shader` has `?nogl`; `glow-cursor-cta` has `?touch`; `word-swap-hero` has `?nolenis`. When you adapt a scroll story for a client, add the capture convention from the skeleton below so `scripts/shoot.mjs --story` and `scripts/scrollfilm.mjs` give deterministic frames.

Progress smoothing in the scroll stories lerps toward the scroll target with a frame-rate-independent factor `1 − e^(−dt/τ)` (τ ≈ 120–160 ms): weight without scroll-jacking.

## Build your own story (skeleton)

For a mechanic no demo covers, start here and write only `render(p)` and `renderFinal()`:

```html
<html lang="th" class="rm">                       <!-- static composition until JS allows motion -->
<section class="story" id="story" data-story style="height: 600vh">
  <div class="stage" style="position: sticky; top: 0; height: 100svh; overflow: hidden">
    <!-- art layers (aria-hidden) + copy beats as real text -->
  </div>
</section>
<script>
(() => {
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const capture = /[?&]capture\b/.test(location.search);
  const story = document.getElementById('story');
  const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
  const target = () => { const r = story.getBoundingClientRect(), len = story.offsetHeight - innerHeight;
    return len > 0 ? clamp(-r.top / len) : 0; };
  function render(p, dt) { /* your mechanic: transforms, opacity, canvas, from progress p (0..1) */ return false; }
  function renderFinal() { /* the composed static frame for reduced motion and no-JS */ }
  if (reduce) { renderFinal(); return; }           // never start the loop under reduced motion
  document.documentElement.classList.remove('rm');
  let P = 0, running = false, visible = true, last = 0;
  function frame(dt) {
    const p = target();
    P = capture ? p : P + (p - P) * (1 - Math.exp(-dt / 140));
    const busy = render(P, dt);                    // return true while particles/trails are still alive
    return busy || Math.abs(p - P) > 0.0004;
  }
  function loop(now) { const dt = Math.min(50, now - (last || now)); last = now;
    running = frame(dt) && visible; if (running) requestAnimationFrame(loop); else last = 0; }
  const kick = () => { if (capture || running || !visible) return; running = true; requestAnimationFrame(loop); };
  new IntersectionObserver(([e]) => { if (e.isIntersecting && !visible) P = target(); // snap on re-entry
    visible = e.isIntersecting; kick(); }).observe(story);
  addEventListener('scroll', kick, { passive: true });
  addEventListener('resize', () => { /* re-measure geometry */ kick(); });
  document.addEventListener('visibilitychange', () => { visible = !document.hidden; kick(); });
  if (capture) window.__frame = (dt = 33.3) => frame(dt); else kick();
})();
</script>
```

Then: storyboard the beats (`creative-direction.md` §4), keep copy readable at every beat, QA with `node scripts/shoot.mjs "<url>?capture" <dir> --story "#story" --at 0,.1,…,1 --widths 390,1280 --sheet sheet.png` and a film.

## Light trail — `examples/light-trail/`

**Concept it serves:** dark → light, lost → home, off → on. Demo brand: Baan Saeng (home solar + battery): a power cut on a storm night → a home that keeps its light.
**Story (760vh sticky stage):** hook — darkness and one breathing point of light with a quiet "scroll slowly" cue · rise — scroll draws a glowing line past each copy beat and lights the headline letters as it passes; neighbouring homes appear as stars with threads to the light · turn — the line traces a house, then its window, and the light flies into the window · payoff — the window blooms and a feathered dawn floods the screen; the CTA sits inside the dawn · aftermath — a calm light section.
**Ambition:** cinematic. **Avoid** on surfaces where people arrive worried or in a hurry (`creative-direction.md` §1 gate).
**Tech:** vanilla JS; SVG paths drawn with `stroke-dashoffset` in two layers (a CSS-blurred glow SVG and a core SVG with soft + hot strokes); canvas 2D with additive blending for sparks and stars; CSS `mask-image` radial gradient for the dawn; `background-clip: text` lighting on headlines.
**Cost:** one rAF loop, ~220 sparks max, three `getPointAtLength` calls per frame at most; 25 KB, no libraries.
**Verified (2026-10-10, Chrome headless):** 14 desktop + 6 mobile scroll positions, probes clean (no overflow, no console errors, one h1), 18 s scroll film frame-scanned.

The parts an agent must get right:

```js
// 1. The bright "fresh" segment is a dash window; the full path is a dim ember copy underneath.
//    tail = bright length; len = drawn length so far.
fresh.style.strokeDasharray  = `${tail} ${curveLen + tail * 2}`;
fresh.style.strokeDashoffset = `${tail - len}`;        // shows [len - tail, len]
ember.style.strokeDasharray  = `${curveLen} ${curveLen}`;
ember.style.strokeDashoffset = `${curveLen - len}`;    // shows [0, len] at ~28% opacity

// 2. One continuous subpath per drawn element (Chrome restarts dashes at every subpath):
//    the night curve, the house outline and the window are three separate <path>s with their own progress.

// 3. Lit headline: the light's position relative to each text block drives a radial gradient.
beat.style.setProperty('--lx', `${head.x - beat.ox}px`);
beat.style.setProperty('--ly', `${head.y - beat.oy}px`);
/* css */ .beat h2 { background: radial-gradient(circle at var(--lx) var(--ly), #fff 0, #ffe9cc 70px,
          #ffc28a 150px, var(--dim-text) 330px); -webkit-background-clip: text; background-clip: text;
          -webkit-text-fill-color: transparent; }   /* --dim-text must pass 4.5:1 on the night colour */

// 4. Feathered reveal instead of a hard clip-path circle.
const m = `radial-gradient(circle at ${x}px ${y}px, #000 ${r}px, transparent ${r + feather}px)`;
dawn.style.webkitMaskImage = m; dawn.style.maskImage = m;

// 5. Weighty scrub without hijacking scroll.
P = capture ? p : P + (p - P) * (1 - Math.exp(-dt / 140));
```

**Knobs (`CONFIG`):** act boundaries (`lineStart`, `curveEnd`, `houseEnd`, `winEnd`, `windowOn`, `dawn`), beat ranges, `tail` (bright trail length in short-side multiples), star count and timing, `sparkCap`, `smoothingMs`, `dawnFeather`; path waypoints per orientation in `build()` (portrait has its own path and puts copy below the drawing).
**Reduced motion:** the finished drawing (ember path at 55%, house and window lit, stars static) above the copy as a normal page; no orb, sparks or dawn.
**Mobile:** portrait waypoints and a larger house, copy anchored at the bottom, Thai compounds protected with `.nw` spans.

## Spotlight reveal — `examples/spotlight-reveal/`

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

## Light text — `examples/light-text/`

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

## Intro iris — `examples/intro-iris/`

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

## Word-swap hero — `examples/word-swap-hero/`

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

## Zoom-through — `examples/zoom-through/`

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

## Particle constellation — `examples/particle-constellation/`

- **Feeling / story:** scattered stars find their form. A brand name assembles out of the night sky. The fictional brand is Naksat (นักษัตร), a Bangkok night-perfume atelier. The sky gathers into **นักษัตร**, bursts, regathers as **NAKSAT**, then forms the mark (a crescent holding a four-point star inside an orbit ring).
- **Use when:** you have one name or mark reveal near the top of a landing page, a short word (≤ 8 glyphs), a bold, simple mark, and dark art direction.
- **Avoid when:** words are long or logos thin and detailed (they sample into mush), the theme is light (additive glow needs a dark ground), or the page is a task page.
- **Ambition:** cinematic.
- **Tech:**
  - Canvas 2D with `globalCompositeOperation = 'lighter'` and pre-rendered radial "glow sprites" drawn with `drawImage` (much cheaper than `arc` + `shadowBlur`).
  - Targets come from glyph pixels. Each shape is drawn on an offscreen canvas (`fillText` for words, a path for the mark) and sampled with `getImageData` on a grid, then sampled with replacement plus jitter.
  - Particles are stored as a struct of `Float32Array`s.
  - The timeline is scroll-scrubbed: segments hold sky → move → hold shape 1 → … → outro. Per-particle stagger, a burst offset of `sin(πp)` and a swirl around the stage centre make the mid-transition look like a galaxy.
  - Light streaks come from fading the previous frame with `destination-out` instead of clearing it. The canvas stays transparent, so the CSS nebula behind it shows through.
- **Perf budget:** ≤ 6 ms main thread per frame on a laptop and ≤ 4 ms on phones.
  - Measured: 5.7 ms/frame at 1440×900 with 3000 particles, and 2.4–3.0 ms/frame at 390×844@2x with 1200 particles at DPR 1.5. Before the phone DPR cap it was 5.8 ms and included a 93 ms long task.
  - The particle count scales with screen area: area ÷ 210 px², capped at 3000 desktop and 1200 mobile, ×0.7 on ≤ 4 cores.
  - The loop pauses offscreen (IntersectionObserver), on a hidden tab, and after 8 s idle once settled.
- **Key code** (glyph → targets; the part to get right):

```js
async function init() {           // sample only after the exact font is loaded, or you sample the fallback face
  await document.fonts.load('700 100px "Noto Serif Thai"', 'นักษัตร');
}
function sampleShape(shape, n) {   // returns n target points (stage px) for one word or mark
  const bw = Math.round(W * fit), bh = Math.round(Math.min(H * 0.42, bw * 0.5));
  const c = document.createElement('canvas'); c.width = bw; c.height = bh;
  const g = c.getContext('2d', { willReadFrequently: true }); g.fillStyle = '#fff';
  g.font = shape.font;                                   // '700 100px "Noto Serif Thai"'
  const m = g.measureText(shape.text);                   // actualBoundingBox* includes Thai upper vowels/tone marks
  const k = Math.min(bw / m.width, bh / (m.actualBoundingBoxAscent + m.actualBoundingBoxDescent)) * 0.96;
  g.font = shape.font.replace('100px', 100 * k + 'px'); g.textAlign = 'center';
  g.fillText(shape.text, bw / 2, bh / 2 + (m.actualBoundingBoxAscent - m.actualBoundingBoxDescent) * k / 2);
  const data = g.getImageData(0, 0, bw, bh).data, pts = [];
  const step = Math.max(1, Math.round(Math.sqrt(bw * bh / (n * 3.2))));   // grid ≈ 3.2n cells → enough hits
  for (let y = 0; y < bh; y += step) for (let x = 0; x < bw; x += step)
    if (data[(y * bw + x) * 4 + 3] > 140) pts.push(x, y);
  const out = new Float32Array(n * 2), cnt = pts.length / 2, ox = (W - bw) / 2, oy = H * 0.42 - bh / 2;
  for (let i = 0; i < n; i++) { const j = (Math.random() * cnt) | 0;     // with replacement + jitter
    out[i * 2] = ox + pts[j * 2] + (Math.random() - 0.5) * step; out[i * 2 + 1] = oy + pts[j * 2 + 1] + (Math.random() - 0.5) * step; }
  return out;
}
// per frame, particle i moving from shape a to shape b at segment progress e (scroll-driven):
let p = ease(clamp((e - delay[i]) / (1 - DELAY)));
const s = Math.sin(Math.PI * p) * burst;                 // fly out mid-way, land exactly at p = 1
x = ax + (bx - ax) * p + dirX[i] * s;  y = ay + (by - ay) * p + dirY[i] * s;
const sw = Math.sin(Math.PI * p) * CONFIG.swirl;         // galaxy spin around the stage centre
// rotate (x, y) around (cx, cy) by sw … then ctx.drawImage(sprite, x - r, y - r, 2r, 2r) with 'lighter'
```

- **Knobs:**
  - `CONFIG` fields: `shapes[]` (text, font, fit, fitMobile, tracking, or `type: 'mark'`), `areaPerParticle`, `maxParticles`, `freeShare` (stars that stay in the sky), `timeline` (intro/move/hold/outro), `burst`, `swirl`, `trail`, `smooth`, `idleMs` and `maxDpr`.
  - CSS custom properties: `--sky`, `--star`, `--story-len`.
- **Reduced motion:** no loop and no scrubbing. One still frame of the finished mark is drawn, and every caption sits in normal flow under it, in reading order. No JS gives the same static layout.
- **Mobile:** fewer particles (≤ 1200) and canvas DPR capped at 1.5. Shapes fit 86–90 % of the width. Resize ignores URL-bar height jitter of under 160 px, so the targets don't rebuild mid-scroll.
- **Gotchas hit:**
  1. Captions positioned with `top: 50%` / `bottom:` inside a zero-height container resolved against 0 and rendered off-screen. Fix: `.caps { position: absolute; inset: 0 }`. The reduced-motion layout has to undo that.
  2. A plain random gather made a flat oval blob mid-transition. Adding a swirl, scaled by depth, turned it into a galaxy.
  3. The intro caption over a dense starfield lost contrast. Each caption now gets a `closest-side` dark radial vignette (`::before`).
  4. Captions must not use `visibility: hidden` when faded out, or the CTA becomes unfocusable. They use opacity only, and a `focusin` handler scrolls to the shape where the caption is shown (verified: focus → scrollY 4714, caption opacity 1).
  5. `ctx.letterSpacing` is a no-op where unsupported. Tracking then degrades gracefully.
- **Contact sheet:** `/private/tmp/claude-501/-Users-thanaphatnorth-Desktop-ai-skills-north-ai-skills/b3acc423-6456-4200-b4ca-c215c443d2cc/scratchpad/recipes/particle-constellation/sheet.png`

## Aurora shader — `examples/aurora-shader/`

- **Feeling / story:** calm awe; the sky is alive. The fictional brand is Saeng (แสงเหนือ), a spatial-sound sleep app. The aurora's colours follow the night as you scroll: midnight teal, deep violet, then dawn gold, rose and lilac. Each colour matches the chapter on screen.
- **Use when:** the hero needs atmosphere, the copy is short, and the scroll moves through moods or chapters.
- **Avoid when:** the page is content-dense, the brand colours have low contrast behind long text, or there is already another WebGL scene on the screen.
- **Ambition:** bold → cinematic.
- **Tech:**
  - Raw WebGL1: one oversized triangle and one fragment shader.
  - The shader runs fbm value noise with two-level domain warping (`q`, `r`). Ribbon 1 is a warped line with light hanging above it in fbm "rays" and brighter folds. Ribbon 2 is fainter, uses the third colour, and adds haze.
  - The frame finishes with a vignette, a soft exp tone map and a per-frame hash film grain (which also dithers banding).
  - The three colours are uniforms. JS mixes them from a palette list by scroll progress through the `.sky` wrapper, with smoothstep, then eases them toward the target each frame.
  - The canvas sits in a `position: sticky; height: 100lvh; margin-bottom: -100lvh` layer, so it stays behind several sections.
- **Perf budget:** ≤ 2 ms main thread. GPU work is bounded by the render scale (0.6× desktop, 0.45× mobile, of the DPR-2-clamped size) and a 30 fps cap on mobile. An adaptive loop drops the scale by 20 % after 45 slow frames.
  - Measured main thread: 0.64 / 0.56 ms per frame. GPU time was not measured.
  - The loop pauses when the wrapper is offscreen (IntersectionObserver on `.sky`) and on `visibilitychange`.
- **Key code:**

```glsl
void main(){
  vec2 p=(gl_FragCoord.xy-.5*uRes)/uRes.y, uv=gl_FragCoord.xy/uRes; float t=uTime;
  vec2 q=vec2(fbm(p*1.3+vec2(0.,t)), fbm(p*1.3+vec2(5.2,1.3)-t));                 // warp 1
  vec2 r=vec2(fbm(p*1.7+2.8*q+vec2(1.7,9.2)+.6*t), fbm(p*1.7+2.8*q+vec2(8.3,2.8)-.4*t)); // warp 2
  float f=fbm(p*1.1+2.2*r);
  float y0=.12+.2*sin(p.x*1.1+t*1.3+r.x*2.4)+.07*sin(p.x*2.7-t*.9), d=p.y-y0;     // ribbon line
  float rays=.35+.65*fbm(vec2(p.x*8.+r.y*3.,t*.8));                                  // vertical rays
  float fold=.55+.45*sin(p.x*3.1+r.x*4.+t*1.7);
  float cur=exp(-max(d,0.)*2.6)*smoothstep(-.1,.015,d)*rays*fold;                    // light hangs ABOVE the line
  vec3 col=mix(uA,uB,clamp(d*1.5+f*.7-.2,0.,1.))*cur*1.25;
  col+=mix(uB,uC,q.x)*pow(f,3.)*.42;                                                 // flowing haze
  col*=.3+.7*pow(16.*uv.x*uv.y*(1.-uv.x)*(1.-uv.y),.22);                              // vignette
  col=1.-exp(-col*1.7);                                                              // tone map
  col+=(hash(gl_FragCoord.xy+fract(uTime*13.)*97.)-.5)*uGrain;                        // grain + dither
  gl_FragColor=vec4(col+vec3(.014,.016,.032),1.);
}
```
```js
// JS: render small, upscale; palette follows scroll; sleep offscreen
canvas.width = r.width * Math.min(2, devicePixelRatio) * scale;   // scale 0.6 desktop / 0.45 mobile
const want = paletteAt(progress()), k = 1 - Math.pow(0.92, dt / 16.7);
cur = cur.map((c, i) => mix(c, want[i], k));                      // ease colours, never jump
canvas.addEventListener('webglcontextlost', (e) => { e.preventDefault(); fallback(); });
```

- **Knobs:** `CONFIG` fields: `palettes` (CSS var names, 3 colours each), `renderScale`, `fpsCap`, `flow`, `grain` and `adaptive`. CSS custom properties: `--mood-Na/b/c`. `?nogl` forces the CSS fallback, for testing.
- **Reduced motion:** no shader and no scroll-linked colour. Each chapter (hero and the three moods) gets its own static radial-gradient background in its mood colours, so the three moods still read.
- **No WebGL / context lost:** a CSS fallback paints three radial gradients from `--a/--b/--c`. JS updates those custom properties on scroll, and a 28 s transform drift runs. An SVG-noise overlay replaces the shader grain. Shot as `?nogl`; sheet below.
- **Mobile:** render scale 0.45, 30 fps cap. The layout is unchanged; chapters go left-aligned below 768 px.
- **Gotchas hit:**
  1. Dim orange/yellow light on a dark base reads as mud or khaki. The first dawn palette (`#ff9d5c / #ff4f7a / #ffd27a`) looked brown. The fix was to keep warm hues only in the bright core and put pink and lilac in the dim areas (`#ffb46a / #ff4f8b / #b48cff`).
  2. The Thai headline broke as "ฟังแสง ที่ / เคลื่อนไหว". It is now explicit line spans: `ฟังแสง` / `ที่เคลื่อนไหว`.
  3. Small text over bright curtains needed `text-shadow: 0 1px 28px #04060b99` on sections.
  4. WebGL jobs shoot slowly. Twenty-two jobs with three Chrome instances in parallel hit shoot.mjs's 180 s hard stop. Splitting them into two job files fixed it.
- **Contact sheets:** `/private/tmp/claude-501/-Users-thanaphatnorth-Desktop-ai-skills-north-ai-skills/b3acc423-6456-4200-b4ca-c215c443d2cc/scratchpad/recipes/aurora-shader/sheet.png` and the fallback sheet at `/private/tmp/claude-501/-Users-thanaphatnorth-Desktop-ai-skills-north-ai-skills/b3acc423-6456-4200-b4ca-c215c443d2cc/scratchpad/recipes/aurora-shader-nogl/sheet.png`

## Velocity gallery — `examples/velocity-gallery/`

- **Feeling / story:** walking past a wall of work that answers your pace. The fictional gallery is Sala, showing the exhibition "แสงมรสุม / Monsoon Light": seven CSS-gradient "paintings" with SVG grain, plus a "Book a viewing" end card.
- **Use when:** you have 5–10 visuals of similar weight, the page is about browsing, and it's for a portfolio, exhibition, lookbook or product range.
- **Avoid when:** items need side-by-side comparison, captions are long, or there are more than 12 items. Keep the pinned distance honest for wheel-mouse users.
- **Ambition:** bold. This is the only light theme in the batch.
- **Tech:**
  - Vanilla pinned horizontal scroll. The section height is set to `trackWidth − vw + vh`, with a sticky 100vh `.pin` inside.
  - The row's x is lerped toward `−progress × distance`. Velocity is the per-frame change of the smoothed x, in px per 60 fps frame, and drives the skew.
  - **Skew:** `skewX` follows velocity, clamped to ±6°. It pivots at the bottom of the row.
  - **Parallax inside each frame:** the painting layer is 128 % wide and translates against the card's offset from the viewport centre, using exactly the bleed it has.
  - **Marquee:** a giant outlined title (`-webkit-text-stroke`) runs as a compositor CSS animation for the base drift. JS adds a velocity-driven offset on an outer wrapper, wrapped modulo one copy, so scrolling forward pushes it and scrolling back reverses it.
- **Perf budget:** ≤ 2 ms main thread. The loop does transform-only writes, with geometry cached on resize and no layout reads per frame. Measured: 1.0 ms/frame at 1440, 0.4 ms at 390 (native mode). The loop sleeps after settling plus 1.2 s and when the gallery is offscreen.
- **Key code:**

```js
function frame(now) {
  const dt = Math.min(50, last ? now - last : 16.7); last = now;
  const p = Math.min(1, Math.max(0, (scrollY - top0) / dist));        // top0, dist cached in layout()
  const k = 1 - Math.pow(1 - CONFIG.smooth, dt / 16.7), px = x;
  x += (-p * dist - x) * k;
  const vel = (x - px) / (dt / 16.7);                                  // px per 60 fps frame
  const target = Math.max(-CONFIG.maxSkew, Math.min(CONFIG.maxSkew, vel * CONFIG.skewPerPx));
  skew += (target - skew) * Math.min(1, 0.18 * dt / 16.7);
  track.style.transform = `translate3d(${x}px,0,0) skewX(${skew}deg)`;  // ONE transform for the whole row
  for (let i = 0; i < geo.length; i++) {                               // inner parallax uses exactly the bleed
    const off = geo[i].c + x - vw / 2; if (Math.abs(off) > vw) continue;
    const s = Math.max(-1, Math.min(1, off / (vw / 2))) * geo[i].bleed * CONFIG.parallax;
    paints[i].style.transform = `translate3d(${-s}px,0,0)`;
  }
  mqOff = (((mqOff + vel * CONFIG.marqueeBoost) % mqSeg) - mqSeg) % mqSeg; // keep in (-seg, 0]; 3 copies → no gap
  mq.style.transform = `translate3d(${mqOff}px,0,0)`;
  const settled = Math.abs(-p * dist - x) < 0.05 && Math.abs(skew) < 0.005;
  if (!visible || (settled && now - lastScroll > CONFIG.idleMs)) { raf = 0; last = 0; return; }
  raf = requestAnimationFrame(frame);
}
// keyboard: map a focused item to the page scroll that centres it (the pin uses overflow: clip, so focus can't scroll it)
track.addEventListener('focusin', (e) => { const li = e.target.closest('li');
  scrollTo({ top: top0 + clamp((li.offsetLeft + li.offsetWidth / 2 - vw / 2) / dist) * dist }); });
```

- **Knobs:** `CONFIG` fields: `maxSkew`, `skewPerPx`, `parallax`, `smooth`, `marqueeBoost` and `idleMs`. CSS custom properties: `--card-h`, `--gap`, `--mq-speed`, `--paper/--ink/--accent`. Per card: `--ar` (aspect ratio) and `--hs` (height share).
- **Reduced motion:** no pin, skew or parallax, and a static marquee. On desktop the row becomes a wrapped grid, because horizontal scrolling is hostile to wheel mice. Below 768 px it is a native swipe.
- **Mobile (< 768 px):** no pin and no JS motion. The row is a native horizontal scroller with `scroll-snap-type: x mandatory`, `scroll-snap-align: center` and `overscroll-behavior-x: contain`, and it gets `tabindex="0"` so keyboard users can scroll it. The CSS marquee still drifts.
- **Gotchas hit:**
  1. With alternating top/bottom-aligned frames, the outlined marquee was invisible because every band was covered. Fix: bottom-align the row with varied frame heights and run the title band across the top 30 %, with the tallest frames overlapping its foot.
  2. Use `overflow: clip` (fallback `hidden`) on the pin, so focusing an offscreen card can't scroll the pinned container sideways. Then map focus to page scroll; verified: focusing the end link scrolls to y = 3749 and the link is in view.
  3. Keep the outline stroke at about 40 % ink. At 26 % it vanished on cream.
- **Contact sheet:** `/private/tmp/claude-501/-Users-thanaphatnorth-Desktop-ai-skills-north-ai-skills/b3acc423-6456-4200-b4ca-c215c443d2cc/scratchpad/recipes/velocity-gallery/sheet.png`. It includes `d08-motion-fwd` and `d09-motion-back`, captured mid-scroll to show the skew.

## Glow cursor CTA — `examples/glow-cursor-cta/`

- **Feeling / story:** ignition; one action matters here. The fictional event is Ember/26, a creative-tech summit. The comet cursor sweeps toward "จองที่นั่ง / Reserve a seat". The button leans toward the comet, blooms, squashes on press, and springs back with a ring and sparks.
- **Use when:** the page has one primary action on a dark, energetic brand, with ≥ 160 px of clear space around the CTA.
- **Avoid when:** there are forms or dense UI (a hidden native cursor costs precision), several competing CTAs, a light theme, or a quiet or clinical brand.
- **Ambition:** bold.
- **Tech:**
  - A fixed full-viewport 2D canvas with `mix-blend-mode: screen`. Trail points come from `pointermove`, using `getCoalescedEvents`, and live 650 ms.
  - The core is drawn as opaque `source-over` segments faded by *darkening*: on a screen-blended canvas, black is invisible. The glow pass is drawn at 1/4 resolution and upscaled, which is a free blur, and composited with `lighter`.
  - The magnet follows `pull × offset × smoothstep(nearness)` inside `radius + half the button size`, so there is no jump at the edge of the field. The label moves 18 % further, for depth.
  - The press uses a damped spring: k 520, c 20, damping ratio ≈ 0.44.
  - The bloom is a pre-blurred sibling *behind* the button. Its opacity and scale come from `--near`, and the `.is-hot` class handles hover and focus. A one-shot sheen sweeps across the surface on hover or focus.
  - The comet head is the cursor inside the hero (native cursor hidden there only), with a ring when over the CTA.
- **Perf budget:** ≤ 2 ms per frame while moving, then sleep. Measured: 1.3 ms/frame at 1440 and 1.4 ms at 390, with the pointer moving continuously. The canvas loop sleeps when there is no trail, no sparks and a settled spring.
- **Key code:**

```js
// trail: no beads, soft glow, fade by darkness (canvas is mix-blend-mode: screen → black = transparent)
ctx.clearRect(0, 0, W, H); ctx.globalCompositeOperation = 'source-over'; ctx.lineCap = 'round';
gx.setTransform(1, 0, 0, 1, 0, 0); gx.clearRect(0, 0, gc.width, gc.height); gx.setTransform(GS, 0, 0, GS, 0, 0);
for (let i = 1; i < pts.length; i++) {
  const a = pts[i - 1], b = pts[i], life = 1 - (now - b.t) / CONFIG.trailMs; if (life <= 0) continue;
  const w = CONFIG.trailWidth * Math.pow(life, 1.3);
  ctx.strokeStyle = `hsl(${22 + life * 24}, 100%, ${life * (58 + life * 34)}%)`;   // hot core → dark tail
  ctx.lineWidth = w; ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y); ctx.stroke();
  gx.strokeStyle = `hsl(${345 + life * 35}, 100%, ${life * 42}%)`; gx.lineWidth = w * 4;  // glow at 1/4 size
  gx.beginPath(); gx.moveTo(a.x, a.y); gx.lineTo(b.x, b.y); gx.stroke();
}
ctx.globalCompositeOperation = 'lighter'; ctx.drawImage(gc, 0, 0, W, H);   // upscale = blur
// magnet: continuous at the field edge
const dx = px - box.cx, dy = py - box.cy, R = CONFIG.radius + Math.max(box.hw, box.hh);
const near = Math.max(0, 1 - Math.hypot(dx, dy) / R), e = near * near * (3 - 2 * near);
m.tx = dx * CONFIG.pull * e; m.ty = dy * CONFIG.pull * e;
// press spring (semi-implicit Euler), then compose ONE transform on the button (no CSS transition on it)
m.v += ((m.st - m.s) * CONFIG.spring.k - m.v * CONFIG.spring.c) * dt; m.s += m.v * dt;
cta.style.transform = `translate3d(${m.x}px,${m.y}px,0) scale(${m.s})`;
glowWrap.style.transform = `translate3d(${m.x}px,${m.y}px,0)`;           // bloom sibling follows, BEHIND the button
```

- **Knobs:** `CONFIG` fields: `trailMs`, `trailWidth`, `radius`, `pull`, `labelPull`, `spring.k/c`, `sparks` and `hideCursor`. CSS custom properties: `--ember-1..3`, `--pulse-ms`. `?touch` forces touch mode, for tests.
- **Keyboard:** `:focus-visible` and the JS `focus` handler give the same bloom, sheen and arrow turn as hover (verified: `.is-hot` and `:focus-visible` true after focus). Enter key-down squashes and key-up springs back with a ring and sparks from the button centre (verified: scale 0.93 → 1.02 overshoot → 1). Activating the link scrolls to the ticket section and moves focus to its heading.
- **Touch** (`(hover: none)` or `(pointer: coarse)`)**:** no canvas, no custom cursor and no magnet. The bloom breathes on a 2.8 s CSS loop (opacity and scale), and the press still squashes and springs.
- **Reduced motion:** no trail, magnet, sheen, pulse or spring. Bloom on hover and focus becomes an instant state change.
- **Gotchas hit:**
  1. A `::before` glow with `z-index: -1` on a button that has `will-change: transform` paints **over** the button's background, because the button is its own stacking context. The bloom moved to a sibling `.glow-wrap` behind the button, translated by the same JS.
  2. Additive (`lighter`) round-capped segments double up where the caps overlap, so the comet looked like a bead chain. The fix is the source-over core plus the low-res glow layer above.
  3. Synthetic `PointerEvent`s don't set `:hover`, so the hot state is computed in JS from the pointer position (`.is-hot`), with CSS `:hover` kept as an enhancement. This is also how the state is testable.
  4. Avoid global `scroll-behavior: smooth`: it would smooth every programmatic `scrollTo`, including tests and other scripts. Smooth only the CTA's own `scrollIntoView`.
  5. A test-path bug made the effect look broken. The synthetic path ended at `sin(1.4π) × 120` px below the target, so the "hover" shot showed the comet under the button. Measuring the rects (`magnet` 555–651, `cta` 561–645) proved the page was right.
- **Contact sheet:** `/private/tmp/claude-501/-Users-thanaphatnorth-Desktop-ai-skills-north-ai-skills/b3acc423-6456-4200-b4ca-c215c443d2cc/scratchpad/recipes/glow-cursor-cta/sheet.png` (pointer and `?touch` runs). A close-up of the near, hover, press and release states is at `/private/tmp/claude-501/-Users-thanaphatnorth-Desktop-ai-skills-north-ai-skills/b3acc423-6456-4200-b4ca-c215c443d2cc/scratchpad/recipes/glow-cursor-cta/crop-cta.png`.

## Mask transitions — `examples/mask-transitions/`

- **Feeling / story:** "and now the scene changes". The fictional theatre is Moonlight Playhouse (โรงละครแสงจันทร์), staging three acts in one night:
  - The velvet curtain **parts from the centre line** to reveal Act I, Moonrise, on ivory.
  - Act II, a single spotlight on black, **grows as a circle out of Act I's moon** (it reads as an eclipse).
  - Act III, reflections in river teal with brass, **slices in diagonally**, with a bright blade riding the edge.

  Each act's lines slide up from behind their own masks after the wipe lands.
- **Use when:** you have 3–5 sections with strongly different colour worlds and short copy, and the change of scene is part of the message: chapters, seasons, case studies, product "acts".
- **Avoid when:** the page is long-form reading, forms or comparison content. Use no more than one wipe per screen of scroll and no more than three wipe shapes per page.
- **Ambition:** bold → cinematic.
- **Tech:**
  - One sticky stage holds the absolutely stacked acts.
  - Scroll is converted to viewport-height units and smoothed, with a timeline of intro → [wipe 0.75 + hold 0.45] × 3.
  - Each act's eased wipe progress writes one `clip-path`:
    - curtain: `inset(0 g% 0 g%)`;
    - circle: `circle(Rpx at x y)`, with the origin measured from a `data-origin` element;
    - diagonal: `polygon()` with a sloped edge.
  - `clip-path: none` is applied once the wipe is complete.
  - Content reveal is a class toggle with hysteresis: in at ≥ 0.985, out below 0.55. It drives CSS transitions of `clip-path` and `translateY` on each line, with `--i` stagger. It does not use opacity, so the text is always present.
  - Fallback: `CSS.supports('clip-path', 'circle(1px at 0 0)')` → an opacity crossfade.
- **Perf budget:** ≤ 2 ms main thread. Clip-path repaints the moving layer, so keep act layers to gradients, text and small SVG. Measured 0.7 ms/frame at 1440 and 0.9 ms at 390.
  - Two of the earlier desktop runs showed a one-off 180–320 ms compositor hitch at the first scroll, with no main-thread long task. It did not recur in the final run.
- **Key code:**

```js
function clip(act, p) {                       // p = eased wipe progress 0..1 for this act
  if (!clipOK) { act.style.opacity = p; return; }
  if (p >= 1) { act.style.clipPath = 'none'; return; }
  const kind = act.dataset.wipe;
  if (kind === 'curtain') { const g = 50 - 50 * p; act.style.clipPath = `inset(0 ${g}% 0 ${g}%)`; }
  else if (kind === 'circle') {               // grows from a point in the PREVIOUS scene (data-origin=".moon")
    const [x, y] = origins[acts.indexOf(act)], R = Math.hypot(Math.max(x, W - x), Math.max(y, H - y));
    act.style.clipPath = `circle(${p * R}px at ${x}px ${y}px)`;
  } else {                                    // diagonal: edge from (a%, 0) to (a - s %, 100%)
    const s = CONFIG.slope * 100, a = (1 - p) * (100 + s), b = a - s;
    act.style.clipPath = `polygon(${a}% 0, 100% 0, 100% 100%, ${b}% 100%)`;
  }
}
// content reveal with hysteresis — never visibility:hidden on unrevealed acts (their links must stay focusable)
if (p >= CONFIG.revealAt) act.classList.add('is-in'); else if (p < CONFIG.hideAt) act.classList.remove('is-in');
// blade on the diagonal edge
const x = (1 - p) * (1 + CONFIG.slope) * W, run = CONFIG.slope * W;
blade.style.width = Math.hypot(run, H) + 'px';
blade.style.transform = `translate3d(${x}px,0,0) rotate(${Math.atan2(H, -run) * 180 / Math.PI}deg)`;
blade.style.opacity = Math.sin(Math.PI * p);
```
```css
.js-wipes .act:not(.is-in) .rv { clip-path: inset(0 0 100% 0); }          /* line hidden behind its own mask */
.js-wipes .act:not(.is-in) .rv > span { transform: translateY(70%); }
.js-wipes .rv { transition: clip-path .9s var(--ease-emphasized-out) calc(var(--i) * 90ms); }
```

- **Knobs:**
  - `CONFIG` fields: `intro`, `wipe`, `hold`, `smooth`, `slope`, `revealAt` and `hideAt`.
  - Per act: `data-wipe="curtain|circle|diagonal"` and `data-origin="<selector>"`.
  - CSS custom properties: `--velvet`, `--ivory`, `--saffron`, `--teal`, `--brass`.
- **Reduced motion and no JS:** no pin and no clip. The acts are stacked full-height sections with all content visible, and the blade is hidden.
- **Mobile:** same mechanism; clip-path is cheap at phone size, and the stage uses `100svh`. Act III goes left-aligned. The Thai h1 uses nowrap phrase spans (`สามองก์` / `ในคืนเดียว`).
- **Gotchas hit:**
  1. **`visibility: hidden` on not-yet-revealed acts made their links unfocusable.** Tab skipped "Book seats" entirely: `focus()` left `activeElement` unchanged. Fix: rely on the zero-area clip, and add a `focusin` handler that scrolls to the act's reveal point. Verified: focus → scrollY 3195, act revealed, button in view.
  2. Chrome split "ในคืนเดียว" at 390 px. Fixed with nowrap spans; matches the existing lesson html-deck-css-gotchas.
  3. Revealing with opacity would leave invisible text at some scroll positions. Clip and translate keep the text "present" and look more like the wipe itself.
- **Contact sheet:** `/private/tmp/claude-501/-Users-thanaphatnorth-Desktop-ai-skills-north-ai-skills/b3acc423-6456-4200-b4ca-c215c443d2cc/scratchpad/recipes/mask-transitions/sheet.png`

## Testing notes (headless Chrome)

- `scripts/shoot.mjs` enables focus emulation (focus/focusin handlers fire), moves the real mouse for `hover` jobs (synthetic PointerEvents don't trigger `:hover`), and scales its time limit with the job count (`--timeout` to override; partial results print on timeout).
- Measure cost as main-thread ms per frame (`report` + `throttle` jobs, or `Performance.getMetrics` TaskDuration ÷ frames). Headless rAF runs at 30 or 60 Hz depending on the machine and never shows raster/GPU cost; on a shared, loaded machine even ms/frame drifts — re-measure when load is low.
- CDP mobile emulation doesn't switch `(hover)` / `(pointer)` media queries: test touch modes with a URL flag (`?touch`) or touch emulation.
- Parallel agents: give each its own tools/output folder and its own server port; kill only your own processes by PID.

## Pitfalls

Scroll-story pitfalls shared with every concept (dash per subpath, glaring trails, hard-edged reveals, headless timing) are in `creative-direction.md` Pitfalls; each demo's own gotchas are in its section above.

| Symptom | Cause | Fix |
|---|---|---|
| Lit headline unreadable before the light arrives | Unlit colour too dark | Unlit colour ≥ 4.5:1 on the background (`#9aa0ae` on `#04050a` = 7.8:1) |

## Sources

- MDN — stroke-dasharray — https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute/stroke-dasharray
- MDN — SVGGeometryElement.getPointAtLength() — https://developer.mozilla.org/en-US/docs/Web/API/SVGGeometryElement/getPointAtLength
- MDN — background-clip — https://developer.mozilla.org/en-US/docs/Web/CSS/background-clip
- MDN — mask-image — https://developer.mozilla.org/en-US/docs/Web/CSS/mask-image
- MDN — globalCompositeOperation — https://developer.mozilla.org/en-US/docs/Web/API/CanvasRenderingContext2D/globalCompositeOperation
