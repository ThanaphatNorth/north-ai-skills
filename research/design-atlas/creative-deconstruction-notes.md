# Creative deconstruction — how award-level sites build a cinematic experience

Research for `skills/design-atlas` (goal: teach an agent to *invent* cinematic concepts, not copy them). Collected 2026-10-10.

## Method and evidence tags

- Each site was loaded in headless Chrome (1440×900, DPR 1) with a research-only CDP probe (scratch tool, not committed). It took viewport frames at fixed times after navigation (0.3–15 s), then sent **real `mouseWheel` input events** (300 px each), so Lenis and virtual-scroll sites move too. It also read runtime globals (`window.__THREE__`, `window.gsapVersions`, `window.lenisVersion`, `<html>` classes), canvases, DOM headings and text, loaded fonts, and counted `prefers-reduced-motion` rules in same-origin stylesheets. JS bundles were fetched with curl and grepped.
- Screenshots and contact sheets: `/private/tmp/claude-501/-Users-thanaphatnorth-Desktop-ai-skills-north-ai-skills/b3acc423-6456-4200-b4ca-c215c443d2cc/scratchpad/deconstruct/shots/` (scratch, temporary).
- Tags: **[obs]** seen in my frames or the runtime probe · **[code]** found in HTML/JS/CSS I downloaded · **[cs]** stated in a published case study · **[int]** my interpretation (a reading, not a fact) · **(unverified)** could not confirm.
- Caveats: every site's 0.3 s frame was black. That is headless pre-paint, not a design choice, and I ignored it. Bundle string counts prove a library or loader is *present*, not that it is used on the page. A missing `prefers-reduced-motion` string in the bundles I fetched does not prove the site lacks handling, because other chunks may have it.
- Prompt-injection check: I grepped the fetched pages for text aimed at AI agents and found none. The only hits were false positives: a street name "Claude Vellefaux" on immersive-g.com, and base64 tokens and "Installments" on apple.com.
- Award facts come from `skills/design-atlas/references/inspiration.md`, which was verified 2026-10-10 by an earlier pass. They were not re-verified here.

## Cross-site findings (read this first)

1. **The preloader is Act 0 of the story, never a spinner.** In 11 of 13 sites the loading screen already speaks the concept:
   - Lando: the logo is a window onto his face.
   - Bruno: a ring of light closes.
   - Oryzo: a vector construction drawing of the product fills like a pie.
   - Messenger: a hand-drawn envelope.
   - Igloo: frost crystallises.
   - Why Zero: a countdown from 99 while ice spreads.
   - Lusion: an odometer, and the logo draws.
   - Locomotive: a text scramble.
   - Immersive Garden: a counter in a serif line.
   - JongQue: the logo tick draws, then a horizon line.
   - Work Happiness: numbers spelled as words beside the book.
   [obs]
2. **The intro hands off into content in one continuous move (a FLIP), not a cut.**
   - JongQue: the intro photo animates into the cover image of the product mock-up [code].
   - Lando: the logo-mask scales past the frame to become the hero [obs].
   - Bruno: the loading ring becomes the glowing rim of the world's floor [obs].
3. **One controlling metaphor sets the material, transitions and type.** Igloo uses ice everywhere: the loader is frost, transitions mix frost and chromatic aberration [cs], and projects are frozen sculptures. Immersive Garden uses plaster everywhere: the type is embossed and the decor is relief. Oryzo is "a luxury product film for a cork coaster".
4. **Colour discipline.** Most sites run one neutral world plus one accent:
   - Lando: lime #D2FF00 on #111112.
   - JongQue: one emerald accent on white.
   - Lusion: electric blue.
   - Immersive Garden: a grey world where colour appears only inside project windows.
   - Igloo: monochrome cool grey plus white glow.
5. **Light is the most-used storytelling material.** Examples:
   - glowing rings: Bruno, Igloo, Apple, Why Zero's gesture stroke
   - edge glow: Oryzo
   - bloom and lens streaks: Active Theory [code]
   - a warm key light in a dark stage: Oryzo
   - iridescent streaks for sound: Apple
6. **Conversion never leaves the screen.** A CTA pill is pinned top-right on almost every commercial site, through every act:
   - STORE (Lando)
   - LET'S TALK (Lusion)
   - Let's talk (Locomotive)
   - Buy plus the price in the hero and sticky local nav (Apple)
   - คุยกับเรา "Talk to us" (JongQue)
   - Contact (Active Theory, Oryzo)
   [obs]
7. **Sound is opt-in, with the toggle visible.** Examples: Igloo "Sound: OFF", Immersive Garden "Click to enable sound", Work Happiness "Enter without sound", Lusion PLAY/MUTE, and toggles on Active Theory and Bruno [obs].
8. **Accessibility is weakest where the whole UI is drawn in WebGL.** On Igloo and Messenger the probe found no DOM headings and no body text 12 s after load [obs]. Only JongQue showed a complete reduced-motion path [code + obs]. Apple references `prefersReducedMotion` throughout its animation code [code]. Locomotive gates some transitions behind `prefers-reduced-motion: no-preference` [code]. Why Zero uses the media query only to stop an audio-wave animation [code].
9. **Scroll ownership splits two ways:**
   - **Native document scroll**, smoothed by Lenis or not: JongQue, Lando, Locomotive, Apple, Oryzo. Search, deep links and the browser scrollbar keep working.
   - **Virtual scroll** (document height = viewport; the wheel drives a timeline): Igloo, Lusion, Active Theory, Immersive Garden, Why Zero, Bruno, Messenger. More cinematic control, but no native scrollbar or anchor links.
   [obs: docHeight, scrollY]
10. **Pacing is tension and release.** An empty, slow opening (one element on a plain field) is followed by a dense proof section, then a breath, often a full-bleed image or a giant single number or word (JongQue "0%", Apple "2x / 4x"), then density again.

---

## 1. JongQue — the user's reference

- URL: https://www.jongque.com/ — `<title>`: "JongQue · ระบบจองคิวที่ร้านเป็นเจ้าของ ไม่หักค่าคอมมิชชัน" ("a booking system the shop owns, no commission"). No award listed. This is a commercial SaaS, which makes it the most relevant model for "cinematic and still converts".
- **Concept** [int]: "Your business, your bookings". The page tells one booking's life, from a customer tapping a slot to the money landing in the shop's own PromptPay. Every act proves one promise: ownership, automation, zero commission.
- **Opening** [obs, dense frames]:
  - 0.2 s: white page with a tiny tracked-caps tag, "YOUR BUSINESS, YOUR BOOKINGS.", and a small "Tap to skip" label at the bottom left (Thai: แตะเพื่อข้าม) [code].
  - 0.7 s: a green dot.
  - 1.1 s: a green check-mark draws and the "JongQue" wordmark rises out of a mask.
  - 2.6 s: the logo leaves and a 1 px hairline spans the full width (`intro-line`).
  - 3.2–6.5 s: a word slot cycles "Your nail bar. / spa. / barbershop. / pilates class … / business,". Each word has a matching shop photo card, and the second word is set grey.
  - 8.5 s: the salon photo grows to full-bleed.
  - ~11 s: the hero, "Your business, / your bookings." (grey second line, emerald full stop), with a phone mock-up and a CTA pill.
  - Code: the intro window starts at full viewport and animates into the rect of the shop-front mock's cover image (`.intro-window` → `.ah-object .sf-cover`) [code]. The last frame of the intro *is* the product's first frame.
- **Acts.** Section classes are literally `act aiset`, `act flow`, `act ind`, `act zero` [code], and eyebrow labels use Roman numerals (II, V) [obs]:
  - I. **Pinned hero demo**, about 0–3,200 px [obs]. The phone (customer) and the dashboard (shop) sit side by side. On scroll: pick 14:00 → PromptPay QR deposit → the dashboard row "รอตรวจสลิป" (waiting for slip check) → slip verified ✓ → revenue ฿1,600 → ฿1,800 → confirmation sent. A GSAP timeline scrubs at `scrub: .8` and steps through UI states in `onUpdate` [code].
  - II. **AI setup.** Paste your Facebook / LINE OA text and the AI drafts services, hours and team. The copy states the AI leaves unknown prices blank and saves nothing until you confirm.
  - III. **Storefront customisation.** A sticky list 01–08 (layout, header style, colour, font, arrangement, services, gallery, motion) restyles a live phone-and-web preview.
  - IV. **"Customers book in 3 steps"**: three phones.
  - V. **"0%"**: a giant zero scrubs from scale .55 / opacity .2 to 1 [code]. Copy: "commission per booking, every plan, forever".
  - VI. **Industries**: a horizontal track of business photos.
  - Then a real Thai demo video, pricing (14-day trial, no card), FAQ, PDPA, and a contact form with a LINE QR code.
- **Signature mechanics:**
  - an intro that FLIPs into the product UI
  - a scroll-scrubbed product state machine (two synced devices)
  - a word-slot cycler with matching photos
  - a giant-number release beat
  - a cursor-following radial highlight on the popular pricing card (`radial-gradient(… at var(--px) var(--py) …)`) [code]
  - device mock-ups that float with the mouse (`gsap.quickTo` on `.asm-web-float` / `.asm-phone-float`, fine pointer only) [code]
- **Art direction:**
  - white canvas, ink rgb(15,23,42), one emerald accent (`#10b981` appears in the CSS)
  - Inter Tight with Kanit / Noto Sans Thai / Prompt
  - warm interior photography
  - long soft device shadows (`0 50px 90px -50px`)
  - a custom ring cursor (`has-atelier-cursor`) [obs/code]
- **Pacing:** the intro is nearly empty and slow (one element at a time); the hero is dense product proof; "0%" is the release; industries is a relaxed marquee.
- **Usability** [code unless noted]:
  - intro skippable
  - intro skipped automatically when `scrollY > 10` (reload or deep link), under `prefers-reduced-motion: reduce`, or with `?reduced` in the URL
  - motion code lives in a dynamically imported `motion-*.js` chunk; if it fails, the `<html>` gets `motion-failed` and pinned sections fall back to static layout (`.motion-failed .ah--pinned {height:auto}`)
  - Lenis only on `(min-width:1024px) and (pointer:fine)`, with `lerp .085`
  - the cursor hides while the cookie banner is open
  - a skip-to-content link ("ข้ามไปที่เนื้อหา") is the first DOM text
  - nav with the "คุยกับเรา" CTA and a TH/EN switch always visible [obs]
  - with reduced motion emulated, the hero was static at 1.5 s and the pinned demo became a plain grid [obs]
- **Tech:** React SPA (Vite asset names), GSAP 3.15.0, Lenis 1.3.25 [obs runtime]. No three.js and no canvas [obs].
- **Transferable rule: The intro must end inside the product. The animation's last frame is the hero's first frame, and the hero is a working demo of the core promise scrubbed by scroll.**

## 2. Lando Norris — Awwwards SOTY 2025

- URL: https://landonorris.com/ — agency OFF+BRAND [code: script host `itsoffbrand.io`].
- **Concept** [int]: a driver's personal archive. Racing-helmet graphics, track topography and his own handwriting make it feel signed by him, not by a brand.
- **Opening** [obs]: solid lime #D2FF00 with a tiny "LOAD NORRIS" label. By 2 s the LN monogram is a cut-out window showing his eyes. By 4 s the window has scaled past the frame and becomes the hero. At 7 s, the hero: portrait on off-white with faint topographic contour lines, a WebGL helmet over his head, a stacked "LANDO NORRIS" logotype, a lime STORE pill and a menu, and a "Next race: Singapore GP" widget.
- **Acts** (observed to ~7,200 of 13,579 px; the rest is from the DOM outline):
  - I. Portrait and helmet.
  - II. "Message from Lando": a dark olive section, giant marquee type behind, and his **signature as a lime stroke** over a greyscale photo. I captured only the finished stroke; DrawSVGPlugin is in the bundle, so a draw-on animation is likely (unverified).
  - III. Manifesto, "REDEFINING LIMITS, FIGHTING FOR WINS…", in mixed serif and sans with some words lime (scroll-linked recolouring likely; progression unverified), then a **lime pixel-block wipe** to the next act.
  - IV. A photo diary: captioned photos (Qatar 2024, Miami GP 2024…) scattered on the contour background, with a serif quote.
  - V. "ON TRACK / OFF TRACK", a binary choice with a hand-scribbled "on".
  - VI. Helmets (Discoball, Dark Glitter, Porcelain, Japan, Chrome…), Hall of Fame, World Drivers' Champion, partners & campaigns, socials, and a sign-off line, "Always bringing the fight."
- **Signature mechanics:**
  - logo-as-window mask reveal
  - a handwritten signature stroke (draw-on likely)
  - a two-colour manifesto
  - pixel-block brand-colour wipes; Rive runtime `@rive-app/canvas-lite` in a separate `transitions-rive-isolate.js` [code]
  - a responsive curved motion path in the hero; the Codrops tutorial by Ross Anderson (2025-12-17) says it was built for this site
- **Art direction:**
  - colours: lime #D2FF00, #111112, olive rgb(40,44,32), off-white rgb(244,244,237)
  - type: Brier 700 plus Mona Sans Variable 200–900 [obs fonts]
  - texture: contour lines and handwriting
  - photography: editorial, mixed colour and greyscale
- **Pacing:** fast cuts between dense collage acts, separated by single-statement acts (the signature, the manifesto).
- **Usability:** STORE and the menu stay visible top-right [obs]. No `prefers-reduced-motion` string in the three bundles fetched; emulated reduced motion still showed the lime preloader at 5 s, so I could not confirm a reduced path (unverified).
- **Tech:** Webflow plus external bundles; three.js r174, GSAP 3.13.0, Lenis 1.1.20 [obs runtime]. GSAP plugin strings in the bundles: ScrollTrigger, Observer, Flip, SplitText, CustomEase, DrawSVGPlugin, MorphSVGPlugin, InertiaPlugin [code]. KTX2/Draco/meshopt loader strings are present (usage unverified).
- **Transferable rule: Two colours and one human mark (a signature, a scribble, a handwritten word) carry more personality than any 3D effect. Spend the craft on the person's gesture.**

## 3. Igloo Inc — Awwwards SOTY + Dev SOTY 2024

- URL: https://www.igloo.inc/ — abeto + Bureaux. Meta description: "create the largest onchain community, driving the consumer crypto revolution."
- **Concept:** an igloo as shelter and community, with projects shown as objects encased in ice [cs]. The case study names no single metaphor beyond this.
- **Opening** [obs]: 1.5–3 s, a cool-grey field with a tiny monospace glyph progress bar. 5 s: a faint frost crack crystallises at the centre. 8 s: the camera finds an igloo of glowing ice bricks in snowy mountains. 12 s: a WebGL UI fades in (IGLOO logotype, mono copyright and manifesto text, "Scroll down to discover", "Sound: OFF"). The case study says the intro is real-time and in-engine, not a pre-rendered video.
- **Acts** (virtual scroll; the page never scrolls, the wheel drives the camera) [obs]:
  - I. The igloo exterior.
  - II. The camera dives into fog; a raw ice boulder tumbles past data glyphs.
  - III. Ice blocks fly together into concentric rings around a glowing particle core.
  - IV. Each project is a frozen sculpture on a pedestal ringed by light.
  - The case study describes three sections, each project as a unique ice block, and transitions mixing chromatic aberration, "tech" displacement and frost.
- **Signature mechanics:**
  - a scroll-driven camera dive
  - blocks assembling into a ring portal
  - selective glow on rings and core
  - a procedural ice material
  - SDF text scramble without style recalculation [cs]
  - music and SFX synced to particle movement in the links section [cs]
- **Art direction:** monochrome cool grey (#A0A5B1 field), white emissive glow, volumetric fog, small mono UI text, a slow descending dolly camera.
- **Pacing:** slow, meditative, one object per beat, long fog transitions between beats.
- **Usability:** "Scroll down to discover" hint; sound off by default with a visible toggle [obs]. The UI is rendered in WebGL [cs]: at 12 s the probe found no DOM headings or text [obs], so screen readers and search likely get almost nothing (unverified beyond the probe). The case study mentions no accessibility fallback.
- **Tech:** three.js r165, GSAP 3.12.5 [obs runtime]. The case study names Svelte, Vite, three-mesh-bvh, Houdini and Blender, a custom VDB volume exporter, a custom geometry exporter, and shaders compiled in the background.
- **Transferable rule: Choose one material and make everything from it (loader, transitions, cards, type glitches). The world then needs no explanation.**

## 4. Lusion v3 — Awwwards SOTY + Dev SOTY 2023

- URL: https://lusion.co/ — the studio's own site.
- **Concept** [int]: "a toy box of 3D craft". Soft, physical, playful objects that prove the studio can make anything tangible in a browser.
- **Opening** [obs]: 1–2 s, black with a thin white progress bar and a large odometer counter at the bottom left (004 → 006, digits rolling). 3 s: 100, and a large "L" mark appears. 5 s: a light lavender-white page with the hero window, where soft blue, black and white 3D "cross" blobs settle with physics. Header with a "LET'S TALK" pill and MENU; "SCROLL TO EXPLORE" between + markers.
- **Acts** (virtual scroll):
  - I. Hero window.
  - II. "Bold Ideas, Brought to Life" in big type, while a thick blue 3D tube snakes across the page carrying phone screens.
  - III. "PLAY ◉ REEL": the headline splits around a play button and the reel window expands to full width.
  - IV. "Featured Work", a two-column grid (Oryzo AI, Atlas Motion, Devin AI, Of The Oak, Porsche: Dream Machine, Synthetic Human, Meta: Spatial Fusion, Spaace, DDD 2024, Choo Choo World, Soda Experience…), then "See all projects".
- **Signature mechanics:** cursor-pushed physics objects; one continuous 3D tube threading through sections; a split headline that becomes a video; a full-screen WebGL page-transition overlay (a second fixed canvas, `#transition-overlay`) [obs].
- **Art direction:** white and lavender (body text rgb(240,241,250) on a white background), electric blue, black. Aeonik plus IBM Plex Mono plus a custom "LusionMono" [obs fonts]. Toy-like soft materials, studio lighting.
- **Pacing:** a playful hero, a calm type beat, the reel as the peak, then a dense grid.
- **Usability:** LET'S TALK and MENU are always visible; PLAY / MUTE controls [obs]. No reduced-motion string in the fetched bundle [code] (unverified handling).
- **Tech:** Astro; three.js r158 [obs runtime]. Virtual scroll (docHeight = 900, scrollY stays 0 while content moves) [obs]. `.ogg` audio, `isMobile` branches [code].
- **Transferable rule: Let one continuous object (a tube, a line, a ribbon) travel through every section, so the page reads as one camera shot instead of stacked slides.**

## 5. Messenger (abeto) — Awwwards Dev SOTY 2025

- URL: https://messenger.abeto.co/ — meta description: "It's a small planet, but someone's gotta make the deliveries." Awwwards tags: 3D, WebGL, WebSockets, Three.js, Storytelling (per `3d-ai-assets-notes.md`).
- **Concept:** you are a postman on a tiny shared planet (multiplayer). Delivery stands for connection [int].
- **Opening** [obs]: white with a hand-drawn envelope icon and a handwritten "LOADING" (1.5–5 s). By 8 s a teal plane wipes diagonally up over the white, like a page or envelope flap. By 12 s a tiny planet zooms in from far away and fills the frame, with "MESSENGER" in blocky 3D letters standing on its surface and a yellow "BEGIN" button.
- **Acts:** not observed. The click on BEGIN landed while the scene was still loading in headless Chrome. The game itself (deliveries, multiplayer) is described from metadata only (unverified by me).
- **Signature mechanics:** a loader drawn in the brand's own illustration hand; a diagonal colour wipe; a tiny-planet zoom; a title standing *on* the world as 3D objects.
- **Art direction:** pastel teal, hand-drawn textures on low-poly buildings, cream title, one yellow CTA.
- **Usability:** a single obvious BEGIN button. No DOM text or headings found at 12 s [obs]; the WebGL UI is likely invisible to assistive tech (unverified).
- **Tech:** three.js r180 [obs runtime], Svelte, KTX2/Draco/meshopt and WebGPU strings [code].
- **Transferable rule: Make loading part of the fiction. The first icon the user sees should already belong to the story's world (an envelope for a messenger).**

## 6. Bruno Simon — FWA FOTY + PCA (Jan 2026), Awwwards SOTM Jan 2026

- URL: https://bruno-simon.com/
- **Concept:** a drivable island portfolio with weather, seasons and a day–night cycle; projects live inside the world; light multiplayer (whispers, a cookie counter, a lap leaderboard) [cs].
- **Opening** [obs]. This is **closest to the user's "one point of light in darkness" brief**:
  - 1.5–3 s: an empty deep purple-black frame.
  - 6 s: a thin **glowing ring of light is half drawn** on a dark grid floor dotted with faint × markers.
  - 10 s: the ring is closed.
  - 15 s: the island scene has appeared *inside* the ring (red car, pink trees, lamp, bench), warmly lit. The ring is now the glowing rim of the world's floor, with a handwritten "CLICK TO START" and a sound icon.
  - The case study does not describe the ring; it mentions only a GarageBand-made intro sound.
- **Acts:** a free-roam game, not a linear scroll. Not driven in this test.
- **Signature mechanics:** loading progress drawn as a closing ring of light that then becomes the world's boundary; a click-to-start gate that also unlocks audio; spatialised object sounds [cs]; an interface made of 3D models instead of HTML UI [cs].
- **Art direction:** dusk purple, pink foliage, warm orange ground, emissive ring; Amatic SC handwriting plus Nunito [obs fonts]; toy scale.
- **Usability:** sound toggle, Restart, and "Start chatting" buttons, plus an HTML menu with headings (Three.js Journey, Devlogs, Source code, Musics, Some more links) in the DOM [obs]. Keyboard, mouse, touch and gamepad input; a mobile quality preset turns off water blur and depth of field and lowers shadow resolution [cs]. `<html>` class `is-server-offline` at test time [obs].
- **Tech:** three.js r183 with TSL, WebGPU when available [cs]. GSAP 3.12.5 [obs runtime]. `palette.ktx`, `stars.ktx` and a compressed `.glb` are preloaded in the HTML [code]. ~78k grass blades merged into one geometry, instancing, frustum culling, ETC1S/UASTC textures [cs]. `Howl` strings suggest Howler.js (unverified).
- **Transferable rule: Draw the loader as light that closes a shape. When the shape is complete, reveal the world inside it, so waiting becomes the first scene.**

## 7. Active Theory — FWA FOTM Feb 2024

- URL: https://activetheory.net/
- **Concept** [int]: a dark lab or cavern where the studio's work floats as glowing artefacts and you can talk to it (an AI chat).
- **Opening** [obs]: 1.5 s black. 3 s: a tiny hatched arc and a "/30" counter. 5 s: a sun-like burst of thin blue light strokes around a circular "/75" counter between bracket shapes. 8 s: black (transition). 12 s: an iridescent glass ring logo floating in darkness with falling dust particles, and a top-right pill "WORK —— CONTACT".
- **Acts** (virtual scroll):
  - I. The glass logo in the dark.
  - II. The camera travels through a particle forest with a volumetric light beam and lens streaks.
  - III. "CREATIVE DIGITAL EXPERIENCES" in mono display type, with "Founded in 2012…".
  - IV. Projects as floating glass panels with video textures (20 Years of Xbox, Million Piece Mission, Google Racer…) in a coral-like particle cavern. Left rail: "WHAT ARE YOU LOOKING FOR? → websites / installations / XR/VR/AI / multiplayer / games" and "ASK ME ANYTHING". Bottom: a music player ("Song — Artist", ‹‹ ››).
- **Signature mechanics:** a light-burst loader; a particle volume with god rays; glass and iridescence; bloom and lens streak (`HydraBloom`, `HydraLensStreak` in the bundle) [code]; an intent router and AI chat inside the spectacle.
- **Art direction:** near-black, teal and violet iridescence, dust particles, mono display font "nbarchitekt" [obs fonts].
- **Usability:** Work and Contact are always visible; the intent list gives a direct route; audio toggle [obs]. Browsers without optional chaining are redirected to `unsupported.html` [code].
- **Tech:** in-house "Hydra" framework (114 `Hydra` strings, HydraCSS, HydraObject); Worker and OffscreenCanvas strings; KTX2/Draco; WebSocket (multiplayer); `openai` strings [code]. No global three/GSAP/Lenis [obs]. The canvas renders at 2160×1350 for 1440×900 CSS px at DPR 1, a 1.5× render scale [obs] (the reason is unverified).
- **Transferable rule: Put an intent shortcut inside the spectacle (a 5-item "what are you looking for?" list, or "ask me anything") so wonder and lead capture share one screen.**

## 8. Locomotive — FWA FOTM May 2023; Awwwards Agency of the Year 2022–2024

- URL: https://locomotive.ca/en
- **Concept** [int]: a typographic dynasty. "Seven Years Running 2018–2024 · The dynasty", with a championship ring as the emblem. The type itself carries the brand's wit.
- **Opening** [obs]: 1–2 s, black with a small "Locomotive®" logo and glyph icons. 3.5 s: a **text scramble** resolves "Digital-First Agency / Based in Montreal, Canada" out of random characters. 6 s: a full-bleed red-lit video portrait, with the large logotype "Locomotive® Digital-first Design Agency" carrying inline pictogram glyphs (OPS / DES / DEV).
- **Acts** (native scroll, 6,598 px):
  - I. Video hero.
  - II. "Seven Years Running 2018–2024" with a slowly rotating 3D ring between the words (`data-module-ring`, three.js canvas) [code/obs].
  - III. "Featured work" as huge serif lines separated by hairlines (Lightship, Wolverine Worldwide, The Drake Hotel, Dulcedo, Scout Motors). On hover, an image opens *inside* the line between words [obs: blurred image between "The" and "Drake Hotel"].
  - IV. A manifesto paragraph with inline glyphs.
  - V. Extras (13), articles, culture trips, store.
  - VI. A footer address set as a rebus (pictograms between words).
- **Signature mechanics:** text-scramble preloader; image-in-line hover; inline pictogram font; a ring as the trophy.
- **Art direction:** black and white; "LocomotiveNew" display plus Helvetica Now Display [obs fonts]; hairline rules; colour comes only from video and photos.
- **Usability:** a persistent header (Work, Agency, Careers, Store, Let's talk); native scroll; a non-blocking cookie card [obs]. CSS gates some transitions behind `prefers-reduced-motion: no-preference` [code].
- **Tech:** GSAP 3.14.2, Lenis 1.1.9, three.js r165 [obs runtime]. `@barba/core` (page transitions) and modular `data-module-*` components [code].
- **Transferable rule: Typography can be the spectacle. A custom glyph set, a scramble and an image-inside-the-line hover can beat a 3D scene when the brand sells taste.**

## 9. Apple — AirPods Pro 3 (scroll storytelling reference)

- URL: https://www.apple.com/airpods-pro/ (title "AirPods Pro 3 - Apple").
- **Concept** [int]: sound made visible. Silence and audio are drawn as iridescent light rings and streaks around black silhouettes.
- **Opening** [obs]: 2 s, the hero text "AirPods Pro 3 / The world's best in-ear Active Noise Cancellation." at the bottom left, with $249 and a Buy pill. 4 s: the earbuds rotate in (hero video `…/anim/hero/large.mp4`) [obs videos]. A pause button sits top-right.
- **Acts** (native scroll, ~29,000 px; heading outline from the HTML):
  - Highlights (films).
  - "Take a closer look" (an interactive viewer with a timeline).
  - Intelligent noise control: "The best thing you've never heard." inside concentric iridescent light rings.
  - Stats "2x more / 4x more".
  - Feature carousel (microphones, Voice Isolation, Adaptive Audio, Conversation Awareness).
  - "The sound of science." A scroll-scrubbed exploded view: bud → transparent shell → driver and H2 chip.
  - "For your ears only." (silhouette with a light streak).
  - A black feature band with an iridescent streak.
  - Fitness: heart-rate sensing, IP57.
  - Hearing Health, battery ("They're workin' 9 to 5."), Find My.
  - Why buy from Apple, Ways to Buy.
- **Signature mechanics:** scroll-scrubbed video and exploded views; light rings as the visual of noise cancelling; white/black act alternation; every beat closes on a number or fact.
- **Art direction:** white / #F5F5F7 and black acts; SF Pro Display and Text [obs fonts]; the product as the single hero object; iridescent light as the only decoration.
- **Usability:** sticky local nav with a Buy pill; price in the hero; pause controls on autoplay media; footnotes; a full buying section at the end [obs]. The `<html>` class `no-reduced-motion` is set at runtime; the main bundle references `prefersReducedMotion` 14× and `reduced-motion` 26× [code].
- **Tech:** in-house "AnimSystem" with keyframe controllers; inline-media videos scrubbed through `currentTime`; HLS (`.m3u8`) and WebM sources [code]. No three.js, GSAP or Lenis [obs].
- **Transferable rule: End every cinematic beat on a fact. Headline → one visual metaphor → a number. The spectacle earns attention; the number earns the sale.**

## 10. Oryzo AI (Lusion) — Awwwards SOTM Apr 2026; FWA FOTM Apr 2026

- URL: https://oryzo.ai/ — meta description: "A physical product, reimagined for the AI era…". Final heading: "We caught your attention with a non-existent product. If we can sell a coaster, imagine wha[t…]" [code].
- **Concept:** satire as a sales demo. Luxury product-film grammar and AI-hype copy applied to a cork coaster, to prove Lusion's craft.
- **Opening** [obs]: 1.5 s, a flat olive-green field. 3–8 s: a **vector construction drawing** of the coaster (dashed guide circles, orange Bézier handles and anchors, as in a design tool), with a translucent ring filling clockwise as the progress bar. On scroll: a top-down shot of the coaster on a green cutting mat with pencil, eraser and cutter (the designer's desk), then a cut to a dark brown stage.
- **Acts** (native scroll, 49,967 px):
  - I. The coaster turns in 3D under a warm key light: "ISN'T JUST A COASTER."
  - II. "Powered by AI*" (the footnote says the asterisk means Adobe Illustrator), with a hand holding the coaster. "Try to hover hand: AI fills in the gaps. We said high five. It heard six."
  - III. A rainbow **screen-edge glow** parodies AI-product aesthetics [obs].
  - IV. From the DOM text: "so portable it's wearable", a magazine-cover gag, "AI slop ideas", an "ORYZO-1 open-weight model" joke, feature acts (Thermodynamic stability, Now 37.9% More Circular, Smart flip encryption, Grip-locked Antislip), sustainability, testimonials, the reveal line, and contact hello@lusion.co.
- **Signature mechanics:** a construction-drawing loader; a desk-to-studio camera change; a dark stage with a single key light; a hover easter egg (six fingers); edge glow as parody.
- **Art direction:** cork orange on chocolate brown, cream text rgb(255,237,215); halyard-display plus Literata serif plus DM Mono [obs fonts]; dramatic rim lighting; deadpan copy.
- **Usability:** nav (Intro / Features / Product / Contact) always visible [obs]; native scroll.
- **Tech:** three.js r178 "modified by Lusion" [obs runtime]; `isMobile` and `devicePixelRatio` handling [code].
- **Transferable rule: Give a small truth full production value. Cinematic lighting and pacing on a humble object makes the craft itself the message, and humour keeps it from feeling pompous.**

## 11. Why Zero (zero.university) — Awwwards SOTM Sep 2026; FWA FOTM Aug 2026

- URL: https://why.zero.university/ — `<title>`: "Zero — Human Infrastructure to Get Hired".
- **Concept** [int]: getting to zero, a frozen starting state that thaws as you take part. The brand name becomes the gesture.
- **Opening** [obs]: a teal gradient with a huge counter at the bottom left that counts *down* (99 at 1.5–3 s, 69 at 5 s, 51 at 8 s) while a frost texture spreads from the top edge. Then an ice-sheet scene with a green landmass, and the instruction **"DRAW A ZERO"** pinned at the cursor. A white light stroke circles as a hint. DOM labels "SCROLL" and a scale "-100 BZ … 0 BZ" are present [obs].
- **Acts:** staged ("stage2_glass", "stage3_money" assets) [code]. Not progressed in this test: the gesture was not performed, and the button's coordinates resolved to 0,0.
- **Signature mechanics:** a countdown loader toward the brand number; a **user-drawn gesture gate** ("DRAW A ZERO") whose stroke is a line of light. An accessible alternative exists: a `next-stage-btn` with `aria-label="Continue to next stage"` and a circular SVG progress ring [code].
- **Art direction:** teal and mint, ice and frost textures, white light strokes, Supply Sans plus PP Supply Mono [obs fonts].
- **Usability:** a button alternative to the gesture and an audio toggle [code/obs]. `prefers-reduced-motion` is used only to stop the audio-wave animation [code].
- **Tech:** three.js r160, GSAP 3.15.0 [obs runtime]; KTX2/Draco; `Howl` strings (probably Howler.js, unverified); per-device stage videos (`stage2_background_video-desktop.mp4`) [obs].
- **Transferable rule: Turn the brand's name or symbol into the user's first gesture (draw the zero, close the ring), and always pair the gesture with a plain button.**

## 12. Immersive Garden — Awwwards SOTM Jan 2025; FWA FOTM Jan 2025; Agency of the Year 2025

- URL: https://immersive-g.com/
- **Concept** [int]: a garden carved in plaster. Everything is white relief, and colour appears only where the studio's work shows through.
- **Opening** [obs]: 1.5–3 s, an empty off-white field (#E8E8E8). 5–8 s: one thin line (logo at left, "Innovative digital experiences studio" centred, a serif counter at right climbing to 100). Then the headline "Transcend anything seen or felt before by crafting unparalleled experiences for ambitious brands." emerges **embossed in plaster**, with "Click to enable sound Off / On".
- **Acts** (virtual scroll):
  - Plaster reliefs of flowers, birds and hands drift past.
  - Project windows open in the plaster: a dark greenhouse showroom, "Our approach", Louis Vuitton VIA, David Whyte's poetry journey, Cartier "Above the Clouds" (a gold bracelet in sky).
  - Then "Our mission".
- **Signature mechanics:** embossed type in a 3D material; a monochrome world with colour-only content windows; floating relief ornaments; an odometer loader.
- **Art direction:** warm-grey plaster with soft raking light; PSTimes serif plus Helvetica Neue [obs fonts]; luxury editorial restraint.
- **Usability:** Menu and "See all projects" stay visible; sound is opt-in [obs].
- **Tech:** Nuxt (`/_payload.json`, `data-v-*`); three.js r151, GSAP 3.12.5, Lenis 1.1.14 [obs runtime]; virtual scroll (docHeight = viewport) [obs].
- **Transferable rule: Remove colour from the world so that colour means "the work". A monochrome material makes every content window feel like light coming through.**

## 13. The Search for Work Happiness (partial)

- URL: https://www.findworkhappiness.com — FWA FOTM Jun 2023 (per inspiration.md).
- Observed: the loader counts in **words** ("EIGHTY SIX", "FOURTY TWO", spelled as shown) beside the book cover, with "Loading Chapters"; then an isometric illustrated city, a title card with the author's signature, a yellow enter arrow, "Enter without sound", and an audio synopsis player (3:34). three.js r152dev, GSAP 3.11.5 [obs runtime].
- Not observed: the inner chapters. The click target sat outside the headless viewport. The "drag-to-paint line art, masking chapter transitions, layered audio" claim in inspiration.md comes from the FWA write-up and is **unverified by me**.

---

## Tutorials: light trails, glowing lines, scroll-drawn paths, bloom

Codrops returns 403 to curl and WebFetch. Articles were read from Internet Archive snapshots (`web.archive.org/web/2026id_/…`). Summaries are paraphrased; no code is copied.

1. **High-speed Light Trails in Three.js**, Daniel Velasquez, Codrops, 2019-11-13. https://tympanus.net/codrops/2019/11/13/high-speed-light-trails-in-three-js/
   - Inspired by an "Akira" poster of traffic time-lapse light.
   - Each light is a unit-length tube instanced thousands of times in **one draw call**; per-instance length and radius are applied in the vertex shader.
   - Lights loop infinitely along a road plane.
   - A "speed-up" mode is made **frame-rate independent** (scaled by delta time, not a flat amount per frame).
   - Road curvature comes from modular **distortion functions** in the shader, so new road shapes are cheap.
   - Back faces are skipped because the tubes are small and fast.
   - Lesson: light trails = instanced emissive geometry + time-based motion + additive feel.
2. **Creating Scroll-Driven SVG Map Animations with GSAP**, Tom Miller, Codrops, 2026-05-21. https://tympanus.net/codrops/2026/05/21/creating-scroll-driven-svg-map-animations-with-gsap/
   - One SVG holds a map image, a route path, start and end dots, and two nested groups that act as a "camera".
   - The SVG is pinned while a scroll-**scrubbed** timeline runs two concurrent tweens: DrawSVG draws the stroke while MotionPath carries the end dot along the same path.
   - The camera keeps the moving dot centred: the inner group is offset by the dot's inverse x/y using `quickTo` (built for per-frame updates), and the outer group scales for zoom.
   - The article suggests the same rig for other stories (nutrient flow in a plant, a squiggle through travel photos) and lists a reduced-motion variant among its extra demos.
   - **This is the direct recipe for "a point of light draws a path as you scroll"; add a glow.**
3. **Building Responsive, Scroll-Triggered Curved Path Animations with GSAP**, Ross Anderson, Codrops, 2025-12-17. https://tympanus.net/codrops/2025/12/17/building-responsive-scroll-triggered-curved-path-animations-with-gsap/
   - Made for a Lando Norris hero concept: an element travels a smooth S-curve between three layout anchors and resizes between them.
   - The control points are **computed from measured element positions** (multipliers of the vertical distance, clamped on huge screens), so the curve survives every breakpoint.
   - Settings: `scrub: true`, `invalidateOnRefresh: true`, linear ease.
   - A drag-the-control-points configurator was used to tune the curve.
   - Lesson: never hard-code a decorative path; derive it from the layout.
4. **Animate Anything Along an SVG Path**, Louis Hoebregts, Codrops, 2022-01-19. https://tympanus.net/codrops/2022/01/19/animate-anything-along-an-svg-path/
   - Uses `getTotalLength()` and `getPointAtLength()` as *data*: sample points along a path and place anything there (dots, particles, a fuse that sparks).
   - MotionPathPlugin is noted as the simpler choice for one element.
   - Lesson: a path can emit particles; light can leave sparks behind.
5. **Animated Mesh Lines**, Jérémie Boulay, Codrops, 2019-01-08. https://tympanus.net/codrops/2019/01/08/animated-mesh-lines/
   - THREE.MeshLine builds billboarded triangle strips because native WebGL lines have no width.
   - Dash ratio, array and offset uniforms animate the *drawing* of a line in the shader, the SVG stroke-dash trick moved to WebGL.
   - Curves are smoothed with SplineCurve (2D, cheaper) or CatmullRomCurve3 (3D).
   - Lines can be raycast onto a mesh so they wrap an object.
   - Lesson: thick glowing ribbons in 3D = MeshLine (or three.js `Line2` / "fat lines") + dash animation.
6. **Creating a Glowing Text Marquee Animation**, Kaploom®, Codrops, 2024-06-26. https://tympanus.net/codrops/2024/06/26/creating-a-glowing-text-marquee-animation/
   - The glow is made **without filters**: tiny (about 50 px wide) pre-blurred images of the products sit behind an SVG text mask (`clip-path` with an `objectBoundingBox` path), while a CSS marquee moves the text.
   - Lesson: cheap glow = pre-blurred bitmaps behind a mask, which costs far less than live `blur()`.
7. **three.js official examples, selective bloom**: https://threejs.org/examples/webgl_postprocessing_unreal_bloom_selective.html (source `mrdoob/three.js/dev/examples/webgl_postprocessing_unreal_bloom_selective.html`)
   - Objects that should glow get a "bloom layer".
   - Pass one temporarily swaps every other mesh to a black material and renders bloom only (threshold, strength and radius parameters).
   - Pass two renders the normal scene and mixes the bloom texture in with a shader pass.
   - Lesson: **only the meaningful thing glows**, and the darkness stays clean.
   - Related examples that exist (files.json): `webgl_postprocessing_unreal_bloom`, `webgpu_postprocessing_bloom_selective`, `webgl_lines_fat`, `webgl_postprocessing_godrays`, `webgpu_compute_particles`.
8. **CSS-only path drawing (no tutorial fetched):** the classic technique sets `stroke-dasharray` to the path length and animates `stroke-dashoffset` (CSS-Tricks, https://css-tricks.com/svg-line-animation-works/). With CSS scroll-driven animations (`animation-timeline: scroll()` / `view()`), the drawing can be tied to scroll without JS. Support status and fallbacks are in `research/design-atlas/motion-scroll-notes.md` and `references/scroll-parallax.md` (Chrome/Edge 115+, Safari 26+, Firefox flagged).

## What I could not verify

- Messenger past BEGIN, Bruno past CLICK TO START, Why Zero past "DRAW A ZERO", Work Happiness past the enter screen, and any page transitions (only the home pages were probed).
- Lando from ~7,200 px to the end (taken from the DOM heading outline only), and whether Lando, Lusion, Igloo, Oryzo, Immersive Garden or Active Theory handle `prefers-reduced-motion` in chunks I did not fetch.
- Mobile behaviour of every site except JongQue's code-level gating; no phone-width probes were run.
- Whether loader strings found in bundles (KTX2, Draco, meshopt, Howler `Howl`) are used at runtime.
- The exact colour HEX values beyond those read from computed styles (body background and text) or listed in inspiration.md.
- Codrops pages were read from archive snapshots dated 2025-12 to 2026-08, not the live site (403).

## Sources

- Sites: https://www.jongque.com/ · https://landonorris.com/ · https://www.igloo.inc/ · https://lusion.co/ · https://messenger.abeto.co/ · https://bruno-simon.com/ · https://activetheory.net/ · https://locomotive.ca/en · https://www.apple.com/airpods-pro/ · https://oryzo.ai/ · https://why.zero.university/ · https://immersive-g.com/ · https://www.findworkhappiness.com/
- Case studies: https://www.awwwards.com/igloo-inc-case-study.html · https://www.awwwards.com/brunos-portfolio-case-study.html · https://www.awwwards.com/sites/messenger · https://www.awwwards.com/sites/lando-norris
- Tutorials: listed in the tutorials section above, plus https://threejs.org/examples/files.json
- Prior notes reused: `skills/design-atlas/references/inspiration.md`, `research/design-atlas/3d-ai-assets-notes.md`, `research/design-atlas/motion-scroll-notes.md`
