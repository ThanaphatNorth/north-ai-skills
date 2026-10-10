# Creative direction: from brief to a cinematic concept

> Read when: the user asks for something creative, different, "wow", "สวยอลัง", award-level, immersive or "like <award site>"; any landing, brand, campaign, launch or portfolio page; a design came out "ordinary"; Step 4 (direction) and Step 6 (signature experience) of the design process.

**Contents:** 1 Ambition dial (+ context-of-use gate) · 2 Concept before style · 3 The safe / bold / wild ladder · 4 Storyboard the scroll like film · 5 Art direction for cinematic web · 6 Signature mechanics → recipes · 7 Why it looks ordinary (and the move for each) · 8 Keep it usable and fast · 9 QA for cinematic pages · Pitfalls · Sources

## 1. Ambition dial

Set it in the brief and write it down; every later choice follows it.

| Dial | What it means | Motion level (`product-patterns.md`) | Typical surfaces |
|---|---|---|---|
| **calm** | Polished, conventional, fast. Craft lives in type, spacing, states. | none / subtle | Product UI, dashboards, checkout, settings, admin |
| **bold** | Strong art direction (one unmistakable look), kinetic type, 1–2 scroll set pieces, rich hover/press. | expressive | Marketing sites, e-commerce storefronts, SaaS landing |
| **cinematic** | One concept carried through a scroll story with acts, an intro sequence, a signature mechanic the user drives, a payoff reveal. | immersive | Launches, brand stories, campaigns, portfolios, flagship landing pages |

Defaults:
- Marketing, brand, launch, portfolio, campaign, storefront home: **bold at minimum**. A plain hero + three cards is a failure for these, not a safe choice.
- The user says creative / wow / อลัง / แตกต่าง / "like jongque.com, Lusion, Apple" / immersive → **cinematic**.
- Inside one site the dial can differ by surface: cinematic home, bold product pages, calm checkout.

**Context-of-use gate (overrides the defaults above).** Before raising the dial, answer three questions about the most urgent persona:
1. *Do people arrive in distress or in a hurry?* (symptoms, a sick child, an emergency, debt or money trouble, legal trouble, a broken device, a missed flight). If yes, the surfaces they land on — home, service, booking, pricing — stay **calm or a gentle bold**: the primary action is in the first viewport, nothing is scrubbed or pinned before it, motion is subtle, no intro sequence.
2. *Does the mood match their emotional state?* Anxious people need reassurance: light backgrounds or soft warm palettes, clarity, human faces, plain words. Darkness, mystery, drama and heavy motion read as luxury, tech, entertainment — or as ominous. A health, finance or government brand that wants "wow" gets it from warmth, light, craft and gentle motion, not from darkness.
3. *Is the user unwell or less able?* Illness, nausea, age, low vision and slow phones all lower the tolerance for motion, low contrast and long pages.

**Excited hurry** (a limited drop at 20:00, a flash sale, ticket release, a live event) is not distress: keep the dial, but the primary action (buy, enter the raffle, set a reminder) and the honest countdown sit in the first viewport, and a small persistent pill carries the action through the story.

Cinematic storytelling can still serve these brands on **secondary** surfaces people choose to explore without urgency — a brand campaign, the "about us" story, an annual report, recruitment — with the primary CTA and nav reachable from the first screen. Fear-based story beats ("2 AM, a fever…") need care in regulated categories: health and finance advertising is regulated in most markets (Thailand included); confirm claims and tone with the client's legal team.

## 2. Concept before style

A style is how it looks; a **concept** is the idea the whole page enacts. Award-level sites start from the idea. Run these five steps and write each answer in one line.

1. **Brand truth** — what the audience feels, from the Step 2 insights. "At 2 AM a child has a fever and nobody is awake."
2. **Change** — the before → after the product creates: dark → light, chaos → order, alone → together, dull → radiant, raw → refined, closed → open, small → vast, noise → signal.
3. **Metaphor** — a physical image of that change. A light reaching you in the dark; ingredients assembling into a jar; a thread weaving a garment; a lens pulling focus; water rising; a city waking; a seed becoming a forest.
4. **Signature mechanic** — the one interaction that *enacts* the metaphor and that the user drives: scrolling draws the light; scrolling assembles the product; the cursor is a torch; dragging stirs the liquid. The user's own input causes the transformation — that is what makes it memorable.
5. **Payoff** — the moment the change completes and the call to action appears inside it (the dawn floods the screen and says "ไม่ต้องรอเช้า"; the jar closes and becomes the buy button).

**Done when** the five lines fit in a tweet, a stranger could sketch the hero from them, and the mechanic would make no sense for a competitor.

**Mine the brand's own assets first.** The rows below are examples, not answers — copying a row makes every serum page the same. In tests, the strongest mechanics came from the logo's own shapes: a lime slash became long-exposure light streaks (sneakers), a drop and a ring became a falling serum drop and its ripples (beauty), an orange dome and eight cells became a rice pot with eight dishes gathering round (social cooking), a squircle and a dot became a path that closes into the logo (clinic). Look at the logo, the product's physical form, the moment of use and the culture ("กินข้าวยัง?") before reaching for the table.

| Product | Truth → change | Metaphor | Signature mechanic | Payoff |
|---|---|---|---|---|
| Home solar + battery | a dark street in a power cut → a home that stays lit | a line of light finding its way home | one breathing point of light; scroll draws its path past the copy, lights up neighbouring homes (stars), traces a house, switches on the window (`examples/light-trail/`) | the window's light floods the screen as dawn; CTA inside the dawn |
| Telemedicine (gate applies: users may be sick and in a hurry) | worried at night → reassured | a warm lamp left on for you | **calm-bold**: soft warm-light palette, a gently glowing "doctors available now" status with real numbers, CTA in the first viewport; a short lamp-light reveal only on the brand-story page | the booking card itself, one tap away |
| Skincare serum | dull, tired skin → luminous | a drop of light spreading on skin | macro drop (WebGL/video) that ripples; scroll diffuses it across a face/skin texture, ingredients orbit in | skin glows; "shop the serum" sits in the glow |
| Fashion e-commerce | scrolling past clothes → wanting a look | a runway / a garment being woven | full-bleed looks that zoom-through from one outfit into the next; thread line stitches the sections | the final look freezes into a shoppable hotspot grid |
| Social platform | lonely scrolling → belonging | constellations / a crowd forming | particles (people) drift, then gather into shapes of shared interests as you scroll (`examples/particle-constellation/`) | the constellation spells the community name; join CTA |
| Specialty coffee | rushed mornings → a ritual | the pour: water through grounds | scroll controls the pour (image sequence or shader liquid); steam rises with the copy | the cup is full; order button on the saucer |
| Savings / fintech | money scattered → growing | a seed becoming a tree | scroll grows branches (SVG path drawing) where each branch is a goal | the tree in full leaf with the user's goal number |
| EV / mobility | noise → silence | a line of light on a night road | headlights draw the road as you scroll; car revealed by light sweep | the car parked, lit; book a test drive |
| Online course | confusion → clarity | a lens pulling focus | blurred, noisy type sharpens as you progress (filter + mask) | crisp certificate and enrol button |
| Real estate | listings → a home | a door opening into light | zoom-through the door into the interior (`examples/zoom-through/`) | the room at golden hour; book a viewing |
| Dev tool | chaos → flow | tangled wires straightening | knotted SVG lines untangle into parallel tracks on scroll | clean pipeline diagram; install command |
| Thai restaurant | hunger → warmth | the kitchen fire | darkness, a flame; scroll fans the fire, dishes appear in its light | table set; reserve button |
| Booking platform (jongque) | business at the mercy of apps → owning its bookings | a storefront that becomes yours | pinned hero swaps "Your ___." words and images per business type, then the card becomes the full storefront (`examples/word-swap-hero/`) | your storefront, live; start free trial |

## 3. The safe / bold / wild ladder

Step 4 proposes exactly three directions on this ladder, never three variants of one style:

- **Safe** — category-conventional, beautifully executed (what a strong in-house team ships). Calm or bold dial.
- **Bold** — one unmistakable art direction + one or two set pieces (kinetic type hero, horizontal gallery, mask transitions).
- **Wild** — the concept from §2 at cinematic level, with storyboard.

When the logo fixes the palette, the three directions may share it and differ in concept, type, composition and motion. Recommend one using the dial; when the user asked for wow, recommend **Wild** and show how Safe-level calm survives in checkout/forms. **When the §1 gate applies** (people arrive worried or in a hurry) and the user still asks for wow on that surface, the gate wins and you recommend **Wild, gated**: a calm hero with the primary action, prices and any emergency information in the first viewport; the story as an optional section *after* the action (or its own brand-story page), with a skip link and the CTA reachable throughout; no intro sequence. Say in one sentence why (the most urgent user must not wait for the art), and offer the separate story page as the place for the full cinematic version. Each direction states: concept line, palette (from the logo via `scripts/palette.py`), type pair, mechanic, motion level, and what it deliberately avoids.

## 4. Storyboard the scroll like film

A cinematic page is a short film the user scrubs. Structure it in acts:

| Act | Scroll share | Job | Rules |
|---|---|---|---|
| **Hook** | 0–8% | The first frame and the first motion within 1 s | One focal element on near-empty space. Something alive before any scroll (breathing light, drifting particles, a word assembling). A quiet cue to scroll. |
| **Rise** | 8–55% | Story beats lit or carried by the mechanic | One idea per viewport; headline ≤ 10 words; the mechanic reveals each beat (light passes the words, product assembles). |
| **Turn** | 55–80% | The transformation | The mechanic changes state (line becomes a house, particles become a word, darkness becomes colour). Hold here a little longer (pin). |
| **Payoff** | 80–100% | Release + the call to action | Palette flips (dark → dawn), space opens, CTA inside the payoff, never after a dead end. |
| **Aftermath** | after the story | Proof, details, pricing, FAQ | Ordinary calm scrolling; fast; scannable. |

Pacing rules:
- Budget ~100–140vh of scroll per beat; a 5-beat brand or launch story ≈ 600–800vh. Longer feels like a chore; shorter feels like a glitch. Keep each single pinned section ≤ ~3 viewports and let the page scroll freely between pins (`scroll-parallax.md` §1).
- **Commerce cinematic** (store homes, product launches): the Hook is a shoppable hero (product, price, primary action, honest drop countdown), then a 3–4-viewport story, then the shop as the Aftermath, with a persistent action pill throughout.
- Ambient hook motion (breathing light, drifting particles) settles within 5 s or offers a pause control — WCAG 2.2.2 applies to anything that moves on its own for more than 5 s.
- CTA placement: the payoff CTA is the primary placement; a short closing band after the Aftermath may repeat it with the same label (that band is `platform-web.md`'s "final CTA").
- Alternate dense and empty: after a busy beat, give one nearly empty viewport.
- Scrub, don't autoplay: the user's scroll drives time; add inertia (lerp toward the scroll target with ~120–160 ms time constant) so it feels weighty without hijacking scroll.
- The preloader is **Act 0 of the same image**, never a spinner (a ring of light closing, the product outline drawing, a countdown to the name), and the intro **ends inside the product**: its last frame is the first frame of real content, in one continuous move (an image lands in the product mock-up, a mask grows into the hero).
- Intro sequences: ≤ 2.5 s before the user can act, once per session, visible skip, auto-skipped for reduced motion, deep links and returning visitors; the hero text exists in the HTML from the start (it is your LCP element).
- Every spectacular beat **ends on a fact or a working demo** (a number, a live product state): spectacle earns attention, proof earns the sale.
- One neutral world + one accent (lime on black, emerald on white, colour only inside the "windows"); light marks importance — only the meaningful thing glows.
- Text over effects: keep a clean zone for copy, or make the effect recede behind it (the light-trail's old trail cools to embers so it never fights the words).
- Portrait is a different storyboard, not a shrunk one: move copy below the drawing, simplify paths, fewer particles.

Storyboard template (fill one row per beat and keep it in the spec):

| Beat | Scroll % | Visual | Motion (what moves, easing) | Copy (TH / EN) | Reduced-motion frame | Mobile change |
|---|---|---|---|---|---|---|

## 5. Art direction for cinematic web

**Light.** Darkness only works with a light source. Build glow from layers: a hot white core (1–2 px), a warm soft stroke (6 px, ~45% opacity), a wide blurred halo (20 px + `filter: blur(12–16px)` on a twin layer), then additive blending (`globalCompositeOperation = 'lighter'`, `mix-blend-mode: screen`) for sparks and orbs. Warm light (#ffcf96 → #ff9f6e) reads human; cool (#9ad7ff → #6f7bff) reads technical. Let light *illuminate* other things: text lit by a radial gradient centred on the light (`background-clip: text`), surfaces brightening by distance.

**Depth.** 3–5 planes moving at different rates; far planes blurred and darker; a vignette (radial dark edges) to focus the eye; 6–8% film grain overlay to kill gradient banding and add a filmic surface. When the payoff turns light, fade the vignette and grain out with it, or the corners look dirty.

**Type as image.** One display size that is genuinely huge (12–20vw) for the hook or payoff; kinetic reveals by word (split Thai with `Intl.Segmenter`, never per character — tone marks detach); Latin display tracking −0.02 to −0.04em, Thai tracking 0.

**Colour.** One atmosphere colour + one light colour for most of the story; the payoff flips the palette (dark → dawn, monochrome → full colour) — the release is felt through colour.

**Imagery — photographic, never clip-art.** At bold and cinematic levels every real-world thing on the page (product, food, person, place, material) is photographic: the brand's own photography first, then photoreal 3D renders, then photoreal AI generation (`ai-assets-higgsfield.md` "Photoreal stills pipeline"). Vector/CSS drawings of real objects are placeholders: label them PLACEHOLDER in the spec with the slot's prompt, and never call the page done while they remain. Logo, icons, UI mock-ups, light lines and data stay graphic. Make photos belong to the scene: one light direction across plates and cut-outs, contact shadows under objects, a rim light in the brand accent, a grade toward the palette, edge fades or vignettes into the page background, and token-derived scrims so copy over photos passes 4.5:1. Tested tactics: put every cut-out of a family in one shared frame with a common ground line so swaps never jump; give objects believable scale against the plate (dishes at ~1:1 with the table, not toy-sized on a runner); put multiply shadows outside transformed groups so they blend with the surface; let drawn light sit on top with `mix-blend-mode: screen` so it adds like real light; carry objects in slightly larger with a softer shadow and "set them down"; on dark stories lift photo blacks to the night token so plates melt into the stage instead of sitting on it as boxes. Measure contrast on the rendered pixels behind each text box (darkest/brightest 5%), not on the token pair. No stock blobs, no generic 3D shapes floating without meaning.

**Sound (optional).** Ambient bed + 2–3 interaction sounds; off by default with a visible toggle; never autoplay with sound.

## 6. Signature mechanics → recipes

Tested, copy-ready demos live in `examples/` (one self-contained `index.html` each, with reduced-motion and mobile behaviour). `cinematic-recipes.md` documents each one's key code, knobs, costs and gotchas.

| Mechanic | Feeling | Example |
|---|---|---|
| Point of light → scroll-drawn glowing path, comet trail cooling to embers, payoff flood | hope, guidance, homecoming | `examples/light-trail/` |
| Darkness + torch cursor revealing the scene | discovery, mystery, luxury | `examples/spotlight-reveal/` |
| Headline lit letter by letter by a passing light | drama, reverence | `examples/light-text/` |
| Black → breathing point → iris opens onto the page | arrival, premiere | `examples/intro-iris/` |
| Pinned hero, word + image swap per audience, card grows to full screen | "this is for you", versatility | `examples/word-swap-hero/` |
| Fly through a window/mask into the next scene | entering, transformation | `examples/zoom-through/` |
| Particles gather into words/logos and disperse | community, data, magic | `examples/particle-constellation/` |
| Living aurora / flowing-light shader background | calm energy, premium tech | `examples/aurora-shader/` |
| Horizontal gallery with velocity skew and inner parallax | momentum, fashion, portfolio | `examples/velocity-gallery/` |
| Magnetic glowing CTA + comet cursor | playfulness, invitation | `examples/glow-cursor-cta/` |
| Curtain / iris / diagonal mask transitions between sections | chapters, editorial rhythm | `examples/mask-transitions/` |

When no demo matches the mechanic (dishes gathering round a pot, a path closing into a logo), build it on the skeleton in `cinematic-recipes.md` ("Build your own story"): sticky stage, `data-story`, `.rm` static composition, one guarded rAF loop, capture hook, snap on re-entry — then write only the `render(progress)` that is your mechanic.

More techniques: `scroll-parallax.md` (pinning, image sequences, step tracks, horizontal sections), `3d-webgl.md` (scroll-linked camera, shaders, particles in three.js), `motion.md` (view transitions, text animation), `ai-assets-higgsfield.md` (hero video, layered fake-3D plates). `mechanics-catalog.md` lists 70 mechanics seen on award-level sites (light, line, particles, type, camera, transitions, material, cursor, sound, intro) with feeling, story fit, cost, static state and example URLs, plus 12 worked concept examples.

## 7. Why it looks ordinary (and the move for each)

| Tell | Move |
|---|---|
| Centred hero + subhead + two buttons + three feature cards | Start from the concept's first frame: one focal element, asymmetric, with the mechanic alive in it |
| Effects sprinkled (fade-up on every block) | One mechanic choreographed across the story; everything else still |
| Even lighting, flat colours, no atmosphere | A light source, falloff, vignette, grain; one atmosphere colour |
| Type at safe sizes everywhere | One display moment at 12–20vw; hierarchy jumps of ≥ 2× |
| Symmetric 12-column grid in every section | Break the grid for the hook and payoff; full-bleed, overlap, off-centre |
| Products, food or people drawn as vector clip-art | Photography or photoreal renders/generations of those exact objects, lit like the scene |
| Stock photos / generic 3D blobs | Generated plates in the scene's light, or no imagery — light and type are enough |
| Copy as features ("Fast. Secure. Easy.") | Copy as story beats that the mechanic reveals ("ตีสอง ลูกตัวร้อน") |
| Same pace top to bottom | Acts with pins, holds and empty viewports |
| The CTA appears in a footer band | The CTA lives inside the payoff moment |

## 8. Keep it usable and fast

Non-negotiables for a cinematic page:
- **Content is real DOM text** in reading order; decorative canvas/SVG/WebGL is `aria-hidden`; one `h1`; a skip link past the story.
- **Native scroll** drives the story (scrub + inertia). No scroll-jacking that changes scroll distance or blocks the wheel; smooth-scroll libraries optional and off for tests.
- **Reduced motion** (`prefers-reduced-motion: reduce`) and no-JS get the *finished composition* plus the copy as a normal page — design that frame on purpose (it is also your print and share image).
- **Always an exit**: nav and the primary CTA reachable at every point (a small pinned CTA pill through every act, and the payoff's motion lands on it), skip for intros, a plain button for every gesture gate ("drag to start"), nothing traps focus.
- **Fail static**: load the effect code as a separate chunk; if it fails or the device is weak, the page stays the composed static layout. Smooth-scroll libraries only on desktop with a mouse.
- **Performance budget**: LCP ≤ 2.5 s (the hero text is in the HTML, not injected); effect JS ≤ ~60 KB gzipped without three.js, ≤ ~250 KB with; one rAF loop that sleeps when idle or offscreen; canvas DPR ≤ 2; particle caps by screen size; 60 fps on a mid-range phone with 4× CPU throttle.
- **Contrast survives the effect**: text that is "lit" must still pass 4.5:1 in its unlit state (the light-trail's unlit text is #9aa0ae on #04050a = 7.7:1).
- **Fit the user's state** (§1 gate): never put a story between a distressed user and the action they came for.
- **Trust paths stay calm**: pricing, forms, checkout, medical/financial facts are static and instant.
- **Self-themed sections own their colours**: a story with its own night/dawn palette uses primitives or local custom properties, not semantic tokens (`--primary`, `--text-muted`) that flip with the OS dark theme — otherwise dark mode repaints the story.
- **Demo data is labelled**: live-looking numbers in a prototype ("14 doctors online") are marked as demo data in the spec and bound to the real API before launch; never ship simulated counters (`psychology.md`, deceptive patterns).

## 9. QA for cinematic pages

- Add a capture hook to every scroll story: `?capture` disables smoothing and the rAF loop and exposes `window.__frame(dtMs)` so frames are deterministic. Guard every loop start with the reduced-motion check (a stray `kick()` after `fonts.ready` or `resize` restarts the frame loop and hides the copy), and snap progress when the story re-enters the viewport.
- Mark the story container with `data-story`: its off-beat copy is hidden by design, so `shoot.mjs` skips it in the "invisible" probe. Full-page shots of a pinned story show a frozen stage over an empty runway — check stories with viewport-only jobs instead.
- Contact sheet: `node scripts/shoot.mjs "<url>?capture" <dir> --jobs jobs.json` with 10–14 viewport-only (`"full": false`) `scrollTo` jobs through the story (desktop and 390 px), `eval` stepping `__frame` a few times; build a sheet with Pillow and look at it beat by beat.
- Film: `node scripts/scrollfilm.mjs "<url>?capture" <dir> --size 1280x800 --seconds 18 --story "#story" --mp4 film.mp4 --scan scan.png` (colour scheme pinned to light; `--scheme dark`, `--reduced` for the other films). Look at the scan before sending the film.
- Frame cost: a job with `"throttle": 4` and `"report": "(()=>{const t=performance.now(); for(let i=0;i<60;i++) __frame(16.7); return (performance.now()-t)/60})()"` gives main-thread ms per frame at mid-range-phone speed. rAF intervals measure neither raster nor GPU cost, and headless Chrome runs rAF at 30 or 60 Hz depending on the machine, so report ms per frame, not fps; confirm smoothness on a real phone.
- Check: copy never overlapped by bright effects; every beat readable at its peak; payoff CTA visible and focusable; reduced-motion frame composed; portrait storyboard works; console clean; frame times measured.

## Pitfalls

| Symptom | Cause | Fix |
|---|---|---|
| A later subpath (e.g. a window square) appears fully drawn from the start of a stroke-dash draw | Chrome restarts the dash pattern at each subpath of a `<path>` | One continuous subpath per drawn element; draw extra shapes as separate paths with their own progress |
| Old parts of a long drawn line clutter the copy | The whole path stays at full brightness | Bright "fresh" segment via dash window (`dasharray: tail, len+2·tail; dashoffset: tail − drawn`) over a dim ember copy of the full path |
| Reveal "pops" as a hard white disc | `clip-path: circle()` has a hard edge | Feathered `mask-image: radial-gradient(circle at x y, #000 r, transparent r+feather)` |
| Story stutters or races on fast wheels | Rendering straight from `scrollY` | Lerp the progress toward the scroll target with a time-constant (frame-rate independent `1 − e^(−dt/τ)`) |
| Headless screenshots show the wrong scene | Smoothing, smooth-scroll libraries, or a frozen rAF in hidden tabs | Capture mode: no smoothing, no rAF, `window.__frame(dt)` stepped by the harness |
| Thai headline breaks mid-word over the scene | Browser dictionary splits compounds | `<span class="nw">โรงพยาบาล</span>`, check every beat at 390 px (`typography-layout.md`) |

## Sources

- Awwwards — Sites of the Year (2024 Igloo Inc; 2025 Lando Norris) — https://www.awwwards.com/websites/sites_of_the_year/
- NN/g — Scrolljacking 101 — https://www.nngroup.com/articles/scrolljacking-101/
- web.dev — Largest Contentful Paint — https://web.dev/articles/lcp
- MDN — prefers-reduced-motion — https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion
- MDN — stroke-dashoffset — https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute/stroke-dashoffset
- MDN — mask-image — https://developer.mozilla.org/en-US/docs/Web/CSS/mask-image
- MDN — CanvasRenderingContext2D.globalCompositeOperation — https://developer.mozilla.org/en-US/docs/Web/API/CanvasRenderingContext2D/globalCompositeOperation
- MDN — Intl.Segmenter — https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl/Segmenter
- jongque.com (user reference: ~10 s intro ending inside the product mock-up, pinned hero playing a real booking, GSAP 3.15 + Lenis, static fallback when the animation chunk fails) — https://www.jongque.com/
- Bruno Simon portfolio (opens dark; a ring of light draws itself, then the world appears inside it; FWA of the Year) — https://bruno-simon.com/
- Lando Norris (Awwwards Site of the Year 2025) — https://landonorris.com/
- Apple AirPods Pro (scroll-scrubbed product storytelling) — https://www.apple.com/airpods-pro/
