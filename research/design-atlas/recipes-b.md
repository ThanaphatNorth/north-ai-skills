# Cinematic recipes, batch b

Five copy-ready signature effects for `design-atlas`. Each is one self-contained HTML file under `skills/design-atlas/examples/<slug>/index.html`, with no build step and no image files. They are vanilla JS (no GSAP, no Lenis, no three.js) and run 17–25 KB each. Every file opens with a header comment covering what it is, the story it serves, when to use and avoid it, ambition, knobs and perf.

How each recipe was tested (2026-10-10):
- Served over `python3 -m http.server` and shot with `skills/design-atlas/scripts/shoot.mjs`: viewport-only jobs at 8 scroll positions, at 1440×900 and 390×844, plus reduced-motion jobs.
- The shots were compiled into Pillow contact sheets and reviewed by eye, and the recipe was iterated until it looked right.
- The perf pass auto-scrolled each recipe for 2 s with rAF while reading `Performance.getMetrics` (glow-cursor-cta used synthetic pointer motion instead of scrolling).
- Keyboard focus paths were checked over CDP with focus emulation on.

Every shoot.mjs probe passed in the final runs: no console errors, no page overflow, no small targets and no invisible content. Some overflow "offenders" are listed (`.fallback`, `.mq`, `.blade`, `.glow`), but they are decorative layers clipped by an `overflow: hidden/clip` parent. The page's `overflowX` was 0 at 390 px.

**Reading the perf numbers.** Headless Chrome on this Mac caps rAF at 30 fps, even with the real GPU (ANGLE Metal, Apple M3). Every frame-interval median is therefore 33.3 ms, and all that number proves is that no frames were dropped at 30 fps. The useful figure is **main-thread ms per frame**: the `TaskDuration` delta divided by frames. All numbers are indicative only; none were measured on a real mid-range phone.

| Recipe | Ambition | Palette / type | Main thread ms/frame, 1440×900 | Main thread ms/frame, 390×844 @2x | Interval median / p95 (capped) |
|---|---|---|---|---|---|
| particle-constellation | cinematic | midnight navy + starlight gold · Cormorant Garamond + Noto Serif Thai | 5.7 (3000 particles) | 2.4–3.0 (1200 particles, DPR 1.5) | 33.3 / 33.4 |
| aurora-shader | bold → cinematic | teal → violet → dawn rose on near-black · Unbounded + Anuphan | 0.64 (GPU time not measured) | 0.56 | 33.3 / 33.4 |
| velocity-gallery | bold | paper cream + ink + vermilion (light theme) · Big Shoulders Display + Instrument Serif + IBM Plex Sans Thai | 1.0 | 0.4 (native swipe) | 33.3 / 33.4 |
| glow-cursor-cta | bold | obsidian + ember orange → hot pink · Chakra Petch + JetBrains Mono | 1.3 (pointer moving) | 1.4 | 33.3 / 33.4 (one 117 ms hitch) |
| mask-transitions | bold → cinematic | velvet wine / moon ivory / spotlight saffron / river teal + brass · Chonburi + Sarabun | 0.7 | 0.9 | 33.3 / 33.4 |

Raw perf output is at `/private/tmp/claude-501/-Users-thanaphatnorth-Desktop-ai-skills-north-ai-skills/b3acc423-6456-4200-b4ca-c215c443d2cc/scratchpad/recipes/perf-final.jsonl`. The scratchpad holds the contact sheets, raw shots and tools (`tools/mkjobs.py`, `tools/sheet.py`, `tools/perf.mjs`, `tools/evaljs.mjs`).

---

## 1. Particle constellation · `particle-constellation`

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

## 2. Aurora shader · `aurora-shader`

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

## 3. Velocity gallery · `velocity-gallery`

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

## 4. Glow cursor CTA · `glow-cursor-cta`

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

## 5. Mask transitions · `mask-transitions`

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

---

## Testing notes for the next agent

- **CDP focus:** focus and focusin events don't fire in headless Chrome unless you call `Emulation.setFocusEmulationEnabled({ enabled: true })`. Without it, `el.focus()` handlers look broken. shoot.mjs does not enable it; `:focus-visible` CSS still matches.
- **rAF cap:** headless rAF is capped at 30 fps here, so median and p95 frame intervals only show 33.3 ms. Use `Performance.getMetrics` (`TaskDuration` delta ÷ frames) for cost per frame. With `--disable-gpu-vsync --disable-frame-rate-limit`, rAF runs uncapped, but the intervals then stop meaning "frames shown".
- **Hover:** synthetic `PointerEvent`s don't trigger `:hover`, so pointer effects should compute their hot state in JS. Use `Input.dispatchMouseEvent` when you need real hover.
- **Mobile emulation:** CDP mobile emulation (`mobile: true`) does not switch `(hover)` / `(pointer)` media queries. Test touch mode with a URL flag (`?touch`) or touch emulation.
- **shoot.mjs hard stop:** shoot.mjs stops at 180 s per run. WebGL pages with 20+ jobs, or several Chrome instances in parallel, hit it. Split the job files.
