# Signature mechanics catalog (draft)

Draft for `skills/design-atlas`, collected 2026-10-10. Companion to `creative-deconstruction-notes.md`, which holds the evidence for every "seen on" URL below.

**How to read a row:** *Mechanic* · *Feeling* (what the viewer feels) · *Story use* (which concept it suits) · *Tech* · *Cost* · *Static state* (what reduced-motion and no-JS users get) · *Example* (a URL where I saw it, or a tutorial/doc URL).

**Cost:**
- **low** = CSS/SVG plus a little JS; no 3D assets; safe on low-end phones.
- **med** = canvas, a heavy GSAP timeline, or produced video/illustration assets.
- **high** = WebGL/WebGPU scene, custom shaders or 3D assets; needs a performance budget and a non-WebGL fallback.

**Rule for every row:** the static state must still tell the story in one frame, and the CTA must work without the mechanic.

Example URLs marked "seen" were observed in my probe (see the notes). Tutorial and doc URLs returned 200 on 2026-10-10. Codrops URLs were read through archive.org because Codrops returns 403 to fetchers.

## A. Light and darkness

| # | Mechanic | Feeling | Story use | Tech | Cost | Static state | Example |
|---|---|---|---|---|---|---|---|
| 1 | **Single point of light in darkness** (a page that opens almost black; one warm dot or spotlight; content exists only where light falls) | intimacy, suspense, "someone is here" | night, care, guidance, discovery, safety | CSS `radial-gradient` mask driven by CSS vars (pointer or scroll), or canvas | low | page lit normally; the dot becomes a static accent | technique: https://developer.mozilla.org/en-US/docs/Web/CSS/mask-image ; dark-field opening seen: https://bruno-simon.com/ |
| 2 | **Loader as a ring of light that closes**, then the world appears inside it | anticipation → arrival | energy, completion, membership, "your world is ready" | SVG circle `stroke-dashoffset` with a glow, or WebGL emissive torus | low (SVG) / high (WebGL) | the full ring, drawn | seen: https://bruno-simon.com/ |
| 3 | **Selective bloom**: only the meaningful object glows; everything else stays clean | importance, magic, energy | product core, AI, energy, "the one thing" | three.js bloom layer + mix pass; SVG `feGaussianBlur`; CSS `drop-shadow` | med (WebGL) / low (SVG/CSS) | the glow baked into a still | https://threejs.org/examples/webgl_postprocessing_unreal_bloom_selective.html ; ring glow seen: https://www.igloo.inc/ |
| 4 | **Screen-edge aura** (a soft multicolour glow around the viewport) | "the system is alive or thinking" | AI, listening, live status (also parody) | CSS blurred conic gradient on a fixed frame, or shader | low | a faint static border tint | seen: https://oryzo.ai/ |
| 5 | **Iridescent light rings or streaks as the visual of an invisible thing** (sound, silence, signal) | wonder, precision | audio, connectivity, sensors, health signals | pre-rendered video or PNG sequence, or shader | med | one still ring | seen: https://www.apple.com/airpods-pro/ |
| 6 | **Single key light on a product in a dark stage** (rim light that turns with the object) | luxury, seriousness, craft | premium product, hero object | WebGL PBR + HDR, or pre-rendered scroll-scrubbed video | high (WebGL) / med (video) | one lit hero photo | seen: https://oryzo.ai/ |
| 7 | **Volumetric beam / god rays through particles** | revelation, the sacred, a search | discovery, "finding", spiritual, lab | WebGL post (godrays) or a pre-rendered loop | high | still frame | seen: https://activetheory.net/ ; https://threejs.org/examples/webgl_postprocessing_godrays.html |
| 8 | **Lens streak / flare on highlights** | cinematic, camera-made | film, automotive, night city | WebGL post pass (`HydraLensStreak` in Active Theory's bundle) | high | none | seen: https://activetheory.net/ |
| 9 | **Light-temperature arc across acts** (dawn → noon → night, or cold → warm) | time passing, emotional change | "a day with us", healing, hospitality, recovery | CSS custom properties interpolated on scroll (`color-mix`, scroll-driven animation) or shader uniforms | low (CSS) | a mid-state palette | idea from Bruno's day–night cycle (case study): https://www.awwwards.com/brunos-portfolio-case-study.html ; CSS: https://developer.mozilla.org/en-US/docs/Web/CSS/animation-timeline |

## B. Line and path

| # | Mechanic | Feeling | Story use | Tech | Cost | Static state | Example |
|---|---|---|---|---|---|---|---|
| 10 | **Scroll-drawn path with a glowing dot riding the tip, camera following** | progress, journey, "you're getting closer" | routes, delivery, care pathways, onboarding steps, history | SVG + GSAP DrawSVG + MotionPath + `quickTo` camera; or CSS `stroke-dashoffset` + `animation-timeline` | low | the full path with the end marker | https://tympanus.net/codrops/2026/05/21/creating-scroll-driven-svg-map-animations-with-gsap/ |
| 11 | **Handwritten signature or scribble draws itself** | personal, authentic, "signed by a human" | founder letters, personal brands, promises | SVG stroke dash (DrawSVG) | low | the finished signature | seen (stroke): https://landonorris.com/ ; https://gsap.com/docs/v3/Plugins/DrawSVGPlugin/ |
| 12 | **Horizon hairline** (a 1 px line expands edge to edge between beats) | calm, order, a "cut" in a film | separating intro beats, minimal luxury | CSS `scaleX` transform | low | a static rule | seen: https://www.jongque.com/ (`intro-line`) |
| 13 | **Construction-drawing loader** (guides, Bézier handles and anchors build the product's outline) | craft, precision, "designed" | design studios, engineering, architecture | SVG; progress = a filling arc | low | the finished outline | seen: https://oryzo.ai/ |
| 14 | **Topographic contour background** | terrain, speed, mastery of a course | sport, outdoors, mapping, data | SVG pattern or a shader isoline | low | the same pattern, still | seen: https://landonorris.com/ |
| 15 | **Light trails** (thousands of streaks flowing to a vanishing point) | speed, flow, city at night | mobility, logistics, networks, "always moving" | WebGL instanced tubes, time-based motion, shader distortion | med–high | a long-exposure photo | https://tympanus.net/codrops/2019/11/13/high-speed-light-trails-in-three-js/ |
| 16 | **Animated ribbons / mesh lines** (thick lines that draw in 3D) | energy, aurora, data flow | energy, science, AI, wellness | THREE.MeshLine or `Line2` (fat lines) with a dash-offset uniform | med | still render | https://tympanus.net/codrops/2019/01/08/animated-mesh-lines/ ; https://threejs.org/examples/webgl_lines_fat.html |
| 17 | **One continuous 3D tube threading through sections, carrying content** | one shot, continuity | pipelines, journeys, "end to end" | WebGL TubeGeometry along CatmullRom; or one long SVG path across sections | high (3D) / low (SVG) | per-section static segments | seen: https://lusion.co/ ; 3D path: https://threejs.org/examples/webgl_geometry_extrude_splines.html |
| 18 | **User-drawn gesture line** (the user draws a symbol to continue) | agency, ritual, play | brand-name symbols, education, commitment moments | pointer events + canvas stroke + loose shape check; **always** with a button alternative | med | the button | seen: https://why.zero.university/ ("DRAW A ZERO" + "Continue to next stage" button) |
| 19 | **Responsive curved motion path between layout anchors** (an element flies along a computed S-curve as you scroll) | flow, elegance | linking hero to section, product travelling to its slot | GSAP MotionPath with control points computed from measured rects; `invalidateOnRefresh` | low–med | the element in its final slot | https://tympanus.net/codrops/2025/12/17/building-responsive-scroll-triggered-curved-path-animations-with-gsap/ |
| 20 | **Path that emits particles / sparks** (sample points along a path) | ignition, a fuse, things in motion | launches, countdowns, energy | `getPointAtLength()` + canvas or DOM dots | low–med | the path only | https://tympanus.net/codrops/2022/01/19/animate-anything-along-an-svg-path/ |

## C. Particles

| # | Mechanic | Feeling | Story use | Tech | Cost | Static state | Example |
|---|---|---|---|---|---|---|---|
| 21 | **Depth dust field** (slow particles at several depths) | atmosphere, scale, "inside something" | labs, space, underwater, memory | WebGL points, or a canvas with 2–3 parallax layers | med | a soft noise background | seen: https://activetheory.net/ |
| 22 | **Particle core inside a structure** (a bright swarm at the centre of a ring) | a heart, energy, a living centre | the core of a product, community, a "brain" | WebGL points + bloom | med–high | a bright still core | seen: https://www.igloo.inc/ |
| 23 | **Assemble from fragments** (pieces fly together into a logo, ring or object) | building, collaboration, "it comes together" | platforms, communities, B2B integration | WebGL instanced meshes, or DOM/SVG pieces with GSAP | med (2D) / high (3D) | the assembled object | seen: https://www.igloo.inc/ (ice blocks → rings) |
| 24 | **GPU particles reacting to the cursor** | alive, responsive, "it notices you" | AI, nature, data | WebGPU compute or GPGPU textures | high | still frame | https://threejs.org/examples/webgpu_compute_particles.html |
| 25 | **Crystal or frost growth** (a texture spreads from an edge as progress) | time, cold → state change, transformation | before/after, "unfreezing", preservation | shader noise threshold, or a masked video | med | final state | seen: https://why.zero.university/ (loader) ; https://www.igloo.inc/ (opening crack) |
| 26 | **Wave field of points** (a grid of dots rippling) | calm signal, data at scale | health monitoring, finance, sensors | WebGL points, or canvas | med | flat dot grid | https://threejs.org/examples/webgl_points_waves.html |

## D. Type

| # | Mechanic | Feeling | Story use | Tech | Cost | Static state | Example |
|---|---|---|---|---|---|---|---|
| 27 | **Text scramble / decode** (random glyphs resolve into words) | intelligence, signal locking in | tech, security, agencies, AI | GSAP ScrambleText or a small JS loop; in WebGL, an SDF texture offset | low | final text | seen: https://locomotive.ca/en ; https://gsap.com/docs/v3/Plugins/ScrambleTextPlugin/ |
| 28 | **Word-slot cycler** ("Your ___" cycles audiences, each with its own photo) | "this is for me" recognition | multi-segment products, marketplaces | CSS/GSAP vertical slot + crossfading image card | low | the generic word ("business") | seen: https://www.jongque.com/ |
| 29 | **Scroll-filled manifesto** (words light up or recolour as you read) | conviction, reading as an act | mission statements, founder voice | SplitText + ScrollTrigger, or CSS `view()` timeline per word | low | fully coloured text | seen (two-colour words): https://landonorris.com/ ; https://gsap.com/docs/v3/Plugins/SplitText/ |
| 30 | **Inline pictograms in type** (a rebus) | wit, a house style | agencies, editorial, culture brands | icon font or inline SVG sized in `em` | low | same (static by nature) | seen: https://locomotive.ca/en |
| 31 | **Image inside the line on hover** (a list row opens a window between words) | elegance, curiosity | portfolios, menus, product lists | CSS width/clip transition on an inline element | low | no image; row links still work | seen: https://locomotive.ca/en (featured work) |
| 32 | **Split headline around a play button that becomes the video** | invitation, a reveal | reels, product films | CSS/FLIP (GSAP Flip) | low | button + poster | seen: https://lusion.co/ ("PLAY ◉ REEL") ; https://gsap.com/docs/v3/Plugins/Flip/ |
| 33 | **Embossed or relief type in a material** | permanence, tactility, luxury | heritage, architecture, art | WebGL normal/height maps, or CSS layered text-shadows for a light version | high (WebGL) / low (CSS) | flat type | seen: https://immersive-g.com/ |
| 34 | **Giant single number as the release beat** (it scales up and fills the screen) | clarity, punchline | pricing truth (0%), stats, records | CSS scale with a scroll-driven animation, or ScrollTrigger scrub | low | the big number | seen: https://www.jongque.com/ ("0%") ; https://www.apple.com/airpods-pro/ ("2x / 4x") |

## E. Camera and depth

| # | Mechanic | Feeling | Story use | Tech | Cost | Static state | Example |
|---|---|---|---|---|---|---|---|
| 35 | **Scroll dolly into the scene** (the camera descends or dives with scroll) | immersion, going deeper | "inside the product", origin stories, exploration | WebGL camera on a scroll timeline | high | a sequence of stills per act | seen: https://www.igloo.inc/ |
| 36 | **Tiny-planet zoom** (the world arrives from far away) | wholeness, "a small world" | communities, games, local services | WebGL (or a scaled illustration for a 2D version) | high / low | full planet still | seen: https://messenger.abeto.co/ |
| 37 | **Pinned product demo scrubbed by scroll** (a UI state machine; two synced devices) | proof, "watch it work" | SaaS, apps, any workflow product | CSS `position: sticky` + scroll-scrubbed timeline with `onUpdate` steps | low–med | a static grid of the states | seen: https://www.jongque.com/ |
| 38 | **Scroll-scrubbed product video / exploded view** | engineering, inner beauty | hardware, devices, "what's inside" | video `currentTime` or an image sequence on scroll | med | key still frames | seen: https://www.apple.com/airpods-pro/ |
| 39 | **Floating glass panels in 3D space** (projects as artefacts) | a museum, a lab | portfolios, case-study galleries | WebGL with video textures | high | a standard card grid | seen: https://activetheory.net/ |
| 40 | **Mouse-parallax float of mock-ups** | lightness, depth | SaaS hero, app showcases | `gsap.quickTo` x/y per layer, fine pointer only | low | still layout | seen: https://www.jongque.com/ |
| 41 | **Desk-to-studio camera change** (top-down work surface → dramatic product stage) | "from idea to object" | design, manufacturing, craft brands | photo/WebGL scene switch on scroll | med–high | two stills | seen: https://oryzo.ai/ |

## F. Transitions

| # | Mechanic | Feeling | Story use | Tech | Cost | Static state | Example |
|---|---|---|---|---|---|---|---|
| 42 | **Logo as a window** (the monogram is a cut-out that scales up to become the hero) | identity becomes the world | personal brands, launches | CSS `mask-image`/`clip-path` scale | low | the hero, no mask | seen: https://landonorris.com/ ; https://developer.mozilla.org/en-US/docs/Web/CSS/clip-path |
| 43 | **Intro image lands inside the product UI** (a FLIP from full-bleed to a slot in the mock-up) | "this is real, and it's yours" | SaaS, booking, marketplaces | GSAP Flip, or a manual rect-to-rect tween | low | the hero with the image already in place | seen: https://www.jongque.com/ |
| 44 | **Brand-colour pixel-block wipe** | energy, digital, punchy | sports, gaming, youth brands | Rive, canvas, or a CSS grid of blocks | low–med | instant cut | seen: https://landonorris.com/ (Rive runtime) ; https://rive.app/ |
| 45 | **Diagonal colour wipe** (a page or envelope-flap turn) | a page turning, delivery | storybooks, messaging, editorial | CSS `clip-path: polygon()` | low | instant cut | seen: https://messenger.abeto.co/ |
| 46 | **Material transition** (frost, chromatic aberration, displacement between scenes) | crossing a threshold | world-switching, chapters | WebGL post-processing | high | crossfade | Igloo case study: https://www.awwwards.com/igloo-inc-case-study.html |
| 47 | **Full-screen WebGL page-transition overlay** | continuity between pages | multi-page immersive sites | a second fixed canvas over the DOM (Lusion), or the View Transitions API | med–high (WebGL) / low (VT) | normal navigation | seen: https://lusion.co/ ; https://developer.mozilla.org/en-US/docs/Web/API/View_Transition_API |

## G. Material and texture

| # | Mechanic | Feeling | Story use | Tech | Cost | Static state | Example |
|---|---|---|---|---|---|---|---|
| 48 | **Single-material world** (everything is ice, plaster or cork) | coherence, an "art-directed universe" | any brand with one physical truth | WebGL PBR, or photographed material plates for a 2D version | high / med | photographed material | seen: https://www.igloo.inc/ (ice), https://immersive-g.com/ (plaster), https://oryzo.ai/ (cork) |
| 49 | **Monochrome world; colour only in content windows** | the work as light through a wall | portfolios, galleries, luxury retail | CSS grayscale plus colour media, or a WebGL scene | low (CSS) / high | same | seen: https://immersive-g.com/ |
| 50 | **Hand-drawn texture on 3D** | warmth, storybook, human | games, kids, small-town, community | illustrated textures on low-poly meshes | high | an illustration poster | seen: https://messenger.abeto.co/ |
| 51 | **Glass / thin-film iridescence on the mark** | premium tech, futurism | AI, fintech, studios | WebGL transmission + iridescence material | high | a rendered PNG | seen: https://activetheory.net/ |
| 52 | **Soft-toy physics objects** (squishy shapes that bump) | playful, tactile, approachable | creative studios, kids, consumer apps | WebGL + physics (or 2D physics in canvas) | high / med | still render | seen: https://lusion.co/ |

## H. Interaction and cursor

| # | Mechanic | Feeling | Story use | Tech | Cost | Static state | Example |
|---|---|---|---|---|---|---|---|
| 53 | **Cursor-following highlight on the key card** (`radial-gradient` at `--px/--py`) | "this one is for you", focus | pricing, the recommended plan | CSS vars from `pointermove` | low | a static subtle glow | seen: https://www.jongque.com/ (popular plan) |
| 54 | **Custom ring cursor that steps aside for overlays** | crafted, calm | premium brands | CSS + JS, fine pointer only; hide on banners and modals | low | system cursor | seen: https://www.jongque.com/ |
| 55 | **Hover easter egg that delivers the joke** | delight, shareability | satire, launches, brand voice | CSS/WebGL hover state | low–med | caption text | seen: https://oryzo.ai/ ("Try to hover hand… it heard six") |
| 56 | **Play the site** (drive or walk to reach content) | ownership, a memory | portfolios, games, kids, events | WebGL + physics + multi-input | high | an HTML menu of the same links (Bruno keeps one) | seen: https://bruno-simon.com/ |
| 57 | **Intent router inside the spectacle** ("What are you looking for?" + AI chat) | guided, efficient | agencies, B2B, complex offerings | DOM list + chat | low | same | seen: https://activetheory.net/ |
| 58 | **Binary split choice** (two halves of the screen, two paths) | identity, decision | dual audiences (ON / OFF track; patient / doctor) | CSS layout + hover expand | low | two links | seen: https://landonorris.com/ |

## I. Sound

| # | Mechanic | Feeling | Story use | Tech | Cost | Static state | Example |
|---|---|---|---|---|---|---|---|
| 59 | **Sound off by default with a visible, labelled toggle** | respect, a premium feel | every immersive site | Web Audio / HTMLAudio + `aria-pressed` toggle | low | silent | seen: https://www.igloo.inc/ ("Sound: OFF"), https://immersive-g.com/ ("Click to enable sound") |
| 60 | **Dual entry: "Enter" / "Enter without sound"** | choice, control | narrative sites, books, films | two buttons at the gate | low | same | seen: https://www.findworkhappiness.com/ |
| 61 | **Sound synced to motion** (particles or steps trigger tones) | satisfaction, a tactile UI | links sections, playful UI | Web Audio scheduling tied to animation events | med | none | Igloo case study: https://www.awwwards.com/igloo-inc-case-study.html ; https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API |
| 62 | **Spatialised object sounds** | presence, a world | games, explorable worlds | Web Audio `PannerNode` | med | none | Bruno case study: https://www.awwwards.com/brunos-portfolio-case-study.html |
| 63 | **Ambient music player as a scene control** ("Song — Artist") | a lounge, a mood | studios, hospitality, fashion | an audio element + minimal controls | low | hidden | seen: https://activetheory.net/ |

## J. Intro and preloader

| # | Mechanic | Feeling | Story use | Tech | Cost | Static state | Example |
|---|---|---|---|---|---|---|---|
| 64 | **Brand-logic countdown** (counts toward the brand's number: 99 → 0) | tension toward a promise | brands named for a number or goal | DOM counter tied to real load progress | low | skipped | seen: https://why.zero.university/ |
| 65 | **Odometer / serif counter** (big rolling digits) | precision, studio confidence | agencies, finance | CSS translate digits | low | skipped | seen: https://lusion.co/ , https://immersive-g.com/ |
| 66 | **Logo mark draws, then a horizon line, then the first word** (a 3-beat title sequence) | film titles, calm confidence | SaaS that wants warmth, hospitality | SVG stroke + CSS transforms | low | logo + hero at once | seen: https://www.jongque.com/ |
| 67 | **Loader drawn in the story's own hand** (envelope icon, handwritten "loading") | the fiction starts now | illustrated worlds, games, kids | SVG/PNG + CSS | low | same | seen: https://messenger.abeto.co/ |
| 68 | **Numbers spelled as words** ("EIGHTY SIX…") | literary, human | books, publishers, poetry | JS number-to-words | low | skipped | seen: https://www.findworkhappiness.com/ |
| 69 | **Skippable intro that auto-skips** on reduced motion, deep link (`scrollY > 10`) or `?reduced`, with a static fallback if the motion chunk fails | trust, no penalty for returning visitors | every intro longer than 1.5 s | `matchMedia`, URL param, dynamic `import()` with `.catch` → `motion-failed` class | low | the hero immediately | seen: https://www.jongque.com/ (code) ; https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion |
| 70 | **Click-to-start gate that unlocks audio and commits the user** | ritual, consent | games, worlds, audio-led stories | a button that starts the AudioContext | low | a direct link to content | seen: https://bruno-simon.com/ ("CLICK TO START"), https://messenger.abeto.co/ ("BEGIN") |

Total: 70 mechanics.

---

## Concept → mechanic: 12 worked examples

Method used in every example: **brand truth** (one sentence the brand can prove) → **metaphor** (a physical image of that truth) → **signature mechanic** (one, maybe two, from the catalog) → **acts** (what changes per act) → **conversion anchor** (where the CTA lives) → **budget version** (low-cost build).

1. **Telemedicine at night**
   - **Truth:** a doctor answers at 2 a.m.
   - **Metaphor:** "a light reaching you in the dark".
   - **Mechanics:** #1 single point of light + #10 scroll-drawn path with a glowing tip + #9 cold → warm light arc.
   - **Acts:**
     - 0: black page, one warm dot breathing, "It's 2:14 a.m."
     - I: on scroll, the dot draws a line from a phone in a dark bedroom.
     - II: the line runs across the city map to a lit window (the doctor).
     - III: back home, rooms light up one by one (prescription, follow-up, pharmacy).
     - IV: daylight palette, with price and trust facts.
   - **Anchor:** a "Talk to a doctor now" pill always visible; the path ends *on* the button, so the light becomes the CTA.
   - **Budget:** SVG + CSS `stroke-dashoffset` with `animation-timeline`; static state = the full drawn path on a dusk-to-day gradient.
2. **Shop-owned booking SaaS** (JongQue-style)
   - **Truth:** every booking and every baht stays with the shop.
   - **Metaphor:** "two screens that breathe together".
   - **Mechanics:** #43 intro image lands in the product UI + #37 pinned demo with two synced devices + #34 giant "0%".
   - **Acts:** title sequence (#66) → the customer phone and shop dashboard sync on scroll → AI setup → customisation → "0%" release → industries.
   - **Anchor:** header CTA + LINE chat.
   - **Budget:** already low-cost (GSAP + sticky).
3. **Pharmacy delivery**
   - **Truth:** medicine reaches you within the hour.
   - **Metaphor:** "a route that finds your door".
   - **Mechanics:** #10 route drawing with a camera follow + #34 an ETA number that counts down.
   - **Acts:** the order pin pulses → the path draws through streets → a rider icon rides the tip → "38 min" scales up → the door opens to the medicine.
   - **Anchor:** an address field in the sticky header ("Check delivery to my area").
   - **Budget:** SVG map + GSAP (the Codrops map recipe).
4. **Mental-health / therapy app**
   - **Truth:** therapy steadies you over weeks.
   - **Metaphor:** "a tangled line slowly becomes a calm wave".
   - **Mechanics:** #16 ribbon or SVG path morph (`MorphSVGPlugin` or interpolated path points) + soft Lenis inertia + #59 sound off by default.
   - **Acts:** a chaotic scribble (week 1) → the scribble loosens (week 4) → a smooth breathing sine (week 12) → testimonials, each with its own line.
   - **Anchor:** "Book a free 15-minute match" in the nav and at each act's end.
   - **Budget:** SVG `d` interpolation; reduced motion shows three static lines side by side (a before/after).
5. **Savings app for first jobbers**
   - **Truth:** tiny daily deposits become something real.
   - **Metaphor:** "grains of light gathering into a shape".
   - **Mechanics:** #23 assemble from fragments + #34 a big number.
   - **Acts:** a single glowing dot (฿20) → dots accumulate per scroll step into a house/bike outline → "฿7,300 in a year" fills the screen.
   - **Anchor:** "Open an account in 5 minutes" sticky pill.
   - **Budget:** SVG circles placed with `getPointAtLength` (#20); WebGL only as an enhancement.
6. **Specialty coffee roaster**
   - **Truth:** fire decides the flavour.
   - **Metaphor:** "heat is light".
   - **Mechanics:** #6 single key light on the bean + #9 colour-temperature arc + #21 ember dust.
   - **Acts:** a green bean in the cold → the roast curve draws (#10) while the bean darkens and the light warms → crack sound (opt-in) → the cup → shop.
   - **Anchor:** "Shop this roast" beside every act.
   - **Budget:** a scroll-scrubbed photo sequence (#38).
7. **Law firm**
   - **Truth:** we turn complexity into one clear path.
   - **Metaphor:** "a knot becomes a straight line".
   - **Mechanics:** #10 path + #29 scroll-filled manifesto, monochrome.
   - **Acts:** a knotted line → each practice area pulls one strand straight → one straight line becomes the underline of the contact heading.
   - **Anchor:** "Book a consultation" in the header.
   - **Budget:** SVG only.
8. **Freight and logistics**
   - **Truth:** the chain never breaks.
   - **Metaphor:** "one unbroken line from factory to doorstep".
   - **Mechanics:** #17 one continuous line threading every section (SVG version) + #15 light trails in the hero.
   - **Acts:** port → ship → warehouse → truck → door; the same line carries a parcel through each act.
   - **Anchor:** "Get a quote" form in the last act, mirrored in the header.
   - **Budget:** SVG line across sections; trails as a short video loop.
9. **EV charging network**
   - **Truth:** energy flows in faster than you expect.
   - **Metaphor:** "a ring of light closing".
   - **Mechanics:** #2 loader ring + #3 bloom on the charge ring + #34 "10→80% in 18 min".
   - **Acts:** an empty ring in the dark → the ring fills as you scroll (the charge) → a map of stations lights up dot by dot (#26 style) → pricing.
   - **Anchor:** "Find a charger" (the map) always visible.
   - **Budget:** SVG ring + CSS glow.
10. **Kindergarten / early-years school**
    - **Truth:** children learn by making marks.
    - **Metaphor:** "your child's first line".
    - **Mechanics:** #18 user-drawn gesture (draw a sun to begin) + #50 hand-drawn textures.
    - **Acts:** a blank paper → the visitor draws (or presses "Start") → the drawing becomes the school's illustrated world → day-in-the-life acts.
    - **Anchor:** "Book a visit".
    - **Budget:** canvas stroke + illustrations; the button alternative is mandatory.
11. **Insurance**
    - **Truth:** protection is invisible until the storm.
    - **Metaphor:** "glass that appears when the rain starts".
    - **Mechanics:** rain particles (#21) + a glass dome (#51 or CSS `backdrop-filter`) + #9 calm → storm → calm.
    - **Acts:** a sunny home → a storm builds on scroll → a shield appears and the drops slide off → the claim is paid (a big number).
    - **Anchor:** a "Get my price" form pinned at the side on desktop and at the bottom on mobile.
    - **Budget:** canvas rain + CSS glass.
12. **Boutique resort**
    - **Truth:** the light here at golden hour.
    - **Metaphor:** "one day, from dawn to night, in one scroll".
    - **Mechanics:** #9 light-temperature arc + #42 logo-window reveal + #59 opt-in ambience.
    - **Acts:** dawn (arrival) → noon (pool) → golden hour (villa, hero beat) → night (dinner under lanterns, points of light, #1).
    - **Anchor:** a booking bar (dates + guests) pinned throughout; Apple-style "price on every beat".
    - **Budget:** photo sequences + CSS colour variables.

## Draft rules for inventing a concept (for SKILL.md)

1. Write the brand truth as one provable sentence before choosing any effect.
2. Turn it into one physical image (light, line, material, place). If two images compete, choose one.
3. Pick **one** signature mechanic (two at most) that makes the image move. Everything else stays quiet.
4. Script acts as "what changes" (light, distance, material, density), not "what section comes next".
5. Make the preloader Act 0 of the same image, and make the intro end inside the first real content.
6. Design the static frame of every act first (reduced motion, no JS, slow device), then add motion.
7. Keep the CTA visible in every act, and let the final act's motion land on it.
