# Inspiration Sources & Award-Site Catalog

> Read when: you need real-world references before designing (a landing page, app flow, motion idea, 3D scene, font or palette); a user asks "show me examples like…"; you must decide which gallery an agent can actually fetch; you want to reverse-engineer how an award-winning site was built.

**Contents:** Pick a source by need · Source directory · Agent access playbook · Curated 40 award sites by technique · Health and telemedicine product references · Commerce, streetwear and beauty product references · How to study a reference site · Pitfalls · Sources

All access results below were tested on **2026-10-10** with `curl` (desktop Chrome UA) and WebFetch. Galleries change owners, paywalls and bot protection often — re-test before relying on one. The full 76-site scrape with palettes, stack signals and HTTP status is in `research/design-atlas/patterns-inspiration-notes.md`.

## Pick a source by need

| Need | Go to first | Then |
|---|---|---|
| Cutting-edge web craft, motion, WebGL | Awwwards (SOTD/SOTM/SOTY), The FWA | CSS Design Awards, GSAP showcase, Recent (ex-Godly) |
| Landing-page structure / section ideas | SaaS Landing Page, Landingfolio, One Page Love | SaaSFrame, Navbar Gallery, Minimal Gallery |
| Real app screens & multi-step flows (onboarding, paywall, checkout) | Mobbin (account), Page Flows (paid) | Refero, ScreensDesign (ex-UI Sources) |
| Calm/minimal/editorial site aesthetics | Minimal Gallery, Httpster | SiteInspire (browser only), Dark Mode Design |
| Motion & creative-coding technique | GSAP showcase, three.js examples | Codrops & CodePen (browser only), Spline community |
| Shaders | three.js `webgl / tsl` + `webgpu` examples | Shadertoy (browser only) |
| Animated assets (icons, illustrations, state machines) | LottieFiles, Rive Marketplace | Spline community (3D) |
| Typefaces in real use / pairings | Fonts In Use, Typewolf | — |
| Palette tried on a real layout + token export | Realtime Colors | `color.md` |
| Component & design-system references | Component Gallery, Design Systems Repo | designsystems.surf, Adele |
| Regulated or commerce-heavy UX (telehealth, drops, beauty) — rare in award galleries | Live product references in this file (health; commerce, streetwear and beauty) | Mobbin flows (account) |

## Source directory

Access legend: **open** = server-rendered HTML, WebFetch/curl work · **SPA** = loads but content needs JS (use a browser tool) · **blocked** = Cloudflare/Vercel bot challenge (403/429) — use a real browser with the user's permission, never try to bypass · **account** = meaningful content behind login/paywall.

### Award galleries

| Source | URL | Best for | Agent access | How an agent uses it |
|---|---|---|---|---|
| Awwwards | https://www.awwwards.com/ | Daily/monthly/yearly juried winners; tags by category & technology; per-site palette HEX | open | Listing cards embed JSON (`slug`, `title`, `createdAt`, `tags`); `/sites/<slug>` gives agency, SOTD date, palette, tags, description and the "Visit Site" URL. Use `/websites/sites_of_the_month/`, `/websites/sites_of_the_year/`, `/annual-awards/hall-of-fame/<year>`. robots.txt disallows `/websites/?…` filters, `/gallery/`, `/search-websites` — don't scrape those. |
| The FWA | https://thefwa.com/ | Experimental, interactive, game-like and campaign work; FWA of the Day/Month/Year | SPA (public JSON) | The site loads `https://thefwa.com/api/timeline/?limit=20&offset=0` — items with `title` (award), `item.url` (live site), `item.categories`, `item.description`, `item.extraText` (case write-up with techniques). Page politely (≥1 s between requests). |
| CSS Design Awards | https://www.cssdesignawards.com/ | UI/UX/Innovation scores; WOTD needs judge average ≈ 8+; Special Kudos > 6 | open (WOTY page 403) | `/wotd-award-winners` lists name, external URL and judge score. |
| Recent (formerly Godly) | https://recent.design/ | Curated feed of sites plus motion studies, posters, app icons, App Store screenshots | SPA | `godly.website` now 301-redirects to `recent.design/?ref=godly`. Item pages are JS-rendered; browse in a browser tool. |

### Curated web galleries

| Source | URL | Best for | Agent access |
|---|---|---|---|
| One Page Love | https://onepagelove.com/ | Single-page sites, templates | open |
| Httpster | https://httpster.net/ | Hand-picked creative sites | open |
| Minimal Gallery | https://minimal.gallery/ | Minimal/modern sites; also sells Framer & Webflow templates | open |
| SaaS Landing Page | https://saaslandingpage.com/ | SaaS landing pages by section | open |
| Landingfolio | https://www.landingfolio.com/ | Landing pages, templates, components | open |
| SaaSFrame | https://www.saasframe.io/ | 5,000+ SaaS website, product UI and email examples | open |
| Navbar Gallery | https://www.navbar.gallery/ | Navigation bars only | open |
| Dark Mode Design | https://www.darkmodedesign.com/ | Dark-mode websites | open |
| Land-book | https://land-book.com/ | Landing-page gallery (contents not verifiable — blocked) | blocked (Cloudflare 403) |
| Lapa Ninja | https://www.lapa.ninja/ | Landing-page gallery (contents not verifiable — blocked) | blocked (Cloudflare 403) |
| SiteInspire | https://www.siteinspire.com/ | Curated website gallery (contents not verifiable — blocked) | blocked (Vercel checkpoint 429) |
| Collect UI | https://collectui.com/ | Daily curated UI designs and portfolios | open |
| Dribbble | https://dribbble.com/ | Concept shots, visual exploration (often unbuildable) | blocked (202 empty / challenge) |
| Behance | https://www.behance.net/ | Full case studies, branding systems | blocked (403) |

### App & product UI libraries

| Source | URL | Best for | Agent access |
|---|---|---|---|
| Mobbin | https://mobbin.com/ | 400,000+ searchable mobile & web screens, flows, patterns, website sections; copy to Figma | account — "A free account provides limited access"; paid plans unlock full library, flows, animations |
| Page Flows | https://pageflows.com/ | 100,000+ recorded user flows (iOS, Android, web, email) with annotations | account — paid (3-day trial $2.95; $39/quarter; $99/year; team $199/yr) |
| Refero | https://refero.design/ | Large web + iOS reference library with advanced search | SPA (4 KB shell) |
| ScreensDesign (ex-UI Sources) | https://screensdesign.com/ | iOS screens, onboarding, paywalls, "revenue-backed patterns" | open landing; `uisources.com` redirects here |
| Screenlane | — | — | **defunct** (domain parked) |

### Creative development, motion & 3D

| Source | URL | Best for | Agent access |
|---|---|---|---|
| GSAP showcase | https://gsap.com/showcase/ | Production sites by tool: Core, Scroll, SVG, UI, Text (ScrollTrigger, Flip, SplitText, MorphSVG…) | open |
| Codrops | https://tympanus.net/codrops/ | Tutorials + demos (WebGL, shaders, scroll, transitions) with source | blocked (Cloudflare 403, RSS too) |
| CodePen | https://codepen.io/ | Isolated CSS/JS/GLSL experiments | blocked (Cloudflare 403) |
| three.js examples | https://threejs.org/examples/ | 607 official examples incl. `webgpu`, `webgl / tsl`, postprocessing, physics, webxr | open — index at `https://threejs.org/examples/files.json`; source at `https://raw.githubusercontent.com/mrdoob/three.js/dev/examples/<name>.html` |
| Shadertoy | https://www.shadertoy.com/ | GLSL fragment-shader techniques (SDF, raymarching, noise) | blocked (403, API too) |
| Spline community | https://community.spline.design/ | Remixable 3D scenes (#MadeInSpline) | open landing; app community is SPA |
| Rive Marketplace | https://rive.app/marketplace/ | Interactive state-machine animations | open; old `rive.app/community/` is 404 |
| LottieFiles | https://lottiefiles.com/ | Lightweight Lottie animations, free library | open (heavy pages) |

### Typography, colour, components, design systems

| Source | URL | Best for | Agent access |
|---|---|---|---|
| Fonts In Use | https://fontsinuse.com/ | Archive of real typography by typeface, format, topic | open (some index pages 500'd at test) |
| Typewolf | https://www.typewolf.com/ | Trending web fonts, pairings in the wild | open |
| Realtime Colors | https://www.realtimecolors.com/ | 5-role palette (text, background, primary, secondary, accent) on a live mock site; AA/AAA indicator; heading/body fonts; type scale 1.067–1.618; export CSS/Tailwind/SCSS + shadcn/DaisyUI/MUI presets; copy as OKLCH | open (interactive app) |
| Component Gallery | https://component.gallery/ | One component across many design systems | open |
| Design Systems Repo | https://designsystemsrepo.com/ | Curated list of design systems, tools, articles | open |
| designsystems.surf | https://designsystems.surf/ | Browse real design systems & components | open |
| Adele (UXPin) | https://adele.uxpin.com/ | Design-system & pattern-library repository | open |
| "Design Systems Gallery" | — | name requested but `designsystemsgallery.com` did not respond; use the four above | — |

## Agent access playbook

1. **Prefer machine-readable endpoints** the site itself serves: Awwwards card JSON, FWA `/api/timeline/`, three.js `files.json` + GitHub raw. Parse, don't screenshot.
2. **Read robots.txt first** and stay on public listing/detail pages; ≥ 1 s between requests; identify the purpose in the task notes.
3. **Blocked (Cloudflare/Vercel challenge):** don't retry with spoofed headers or solve challenges. Either use an available browser tool with the user's go-ahead, or ask the user for screenshots/links, or switch to an open source in the same row of "Pick a source by need".
4. **Account/paywall (Mobbin, Page Flows):** never log in with credentials you were not given; ask the user to export screens or share collection links.
5. **Verify every URL you hand to a user** with `curl -sI -L -o /dev/null -w '%{http_code}'`, falling back to GET when HEAD ≠ 200 (some hosts 404 HEAD but serve GET). Campaign microsites die fast: 4 of the 45 FWA of the Month winners 2023–2026 were already dead (3) or bot-blocked (1) on 2026-10-10.
6. **Record provenance** (award, date, source page) next to each reference so the user can audit it.

## Curated 40 award sites by technique

Verified 200 on 2026-10-10. Award key: Awwwards SOTD/SOTM/SOTY, Dev SOTY = Developer Site of the Year, E-com = E-commerce of the Year; FWA FOTM/FOTY (dated by announcement), PCA = People's Choice. "Study" = what to extract (see method below).

### A. Playable 3D worlds & browser games (immersive)

| Site | URL | Award | Study |
|---|---|---|---|
| Bruno's Portfolio | https://bruno-simon.com | FWA FOTY + PCA (Jan 2026); Awwwards SOTM Jan 2026 | Drivable three.js world with WebGPU signature, multiplayer; keyboard/touch input mapping; load budget |
| Messenger (abeto) | https://messenger.abeto.co | Awwwards Dev SOTY 2025; FWA FOTM Nov 2025 | Tiny-planet three.js world, WebSockets multiplayer, pastel teal palette |
| Awards Racing | https://awards.racing | FWA FOTM Oct 2026; CSSDA WOTD | three.js + Bullet physics; whole scene in one draw call; object pooling; stage-based palette repaint |
| Food for Fish | https://foodforfish.org/ | FWA FOTY (Jan 2025) | WebGPU experiment — feature detection and fallback handling |
| Equinox | https://equinox.space | FWA FOTM May 2024 | First-person narrative with a dedicated touch-control mode for phones; original score |
| Haunted by Nostalgia | https://haunted.thedigitalpanda.com | FWA FOTM Nov 2023 | WebGL trivia game loop, sound design, short session structure |

### B. 3D product & brand heroes (expressive → immersive)

| Site | URL | Award | Study |
|---|---|---|---|
| Oryzo AI (Lusion) | https://oryzo.ai | Awwwards SOTM Apr 2026; FWA FOTM Apr 2026 | Cinematic product story for a cork coaster; three.js + post effects; dark brown/orange palette |
| Lando Norris | https://landonorris.com/ | Awwwards SOTY 2025 (+ Users' Choice) | WebGL 3D + GSAP built on Webflow + Lenis; 2-colour system #D2FF00 on #111112 |
| Igloo Inc | https://www.igloo.inc/ | Awwwards SOTY + Dev SOTY 2024; FWA FOTM Aug 2024 | Icy 3D scenes, infinite scroll, section transitions; cool-grey palette |
| Floema | https://floema.com/en | Awwwards SOTM May 2026 | WebGL + photography for a B2B furniture catalogue (Nuxt); lime #E9E778 on charcoal |
| Scout Motors | https://www.scoutmotors.com/ | Awwwards E-com 2025 | Automotive storytelling with photo/video (Astro + Lenis); orange-red #FF5432 |
| GQ & AP The Extraordinary Lab | https://www.gq.com/sponsored/story/the-extraordinary-lab | Awwwards SOTM Mar 2026 | Luxury watch in WebGL (Blender assets), gesture interaction inside a publisher page |

### C. Scroll storytelling & data narrative

| Site | URL | Award | Study |
|---|---|---|---|
| Tracing Art (Getty) | https://www.getty.edu/tracingart/ | Awwwards SOTM Jul 2025 | Provenance data visualisation as scrollytelling; content architecture |
| Sculpting Harmony (Getty) | https://gehry.getty.edu/ | FWA FOTM Dec 2023 | 150+ archival models/sketches with 3D; three.js + GSAP + Lenis (Nuxt) |
| Persepolis Reimagined | https://persepolis.getty.edu/ | Awwwards Dev SOTY 2022; FWA FOTY + PCA (Jan 2023) | WebGL reconstruction, 360 views, data viz, GSAP (Vue) |
| Why Zero | https://why.zero.university/ | Awwwards SOTM Sep 2026; FWA FOTM Aug 2026 | three.js + shaders + GSAP + sound for an education pitch; white + #01C654 |
| David Whyte Experience | https://davidwhyte.com/experience/ | Awwwards SOTM Dec 2024 | Watercolour landscapes driven by scroll; WordPress + Lenis |
| Terminal Industries | https://terminal-industries.com | Awwwards SOTM Sep 2025 | B2B SaaS story told with CSS animation + scroll (Nuxt + Lenis) |

### D. Illustration, comics & playful 2D

| Site | URL | Award | Study |
|---|---|---|---|
| Ponpon Mania | https://ponpon-mania.com/ | Awwwards SOTM Oct 2025 | Interactive comic: WebGL parallax layers, unusual navigation (Nuxt) |
| Santioni Spirits — Notturno | https://santionispirits.com/ | FWA FOTM Sep 2026; Awwwards SOTD Oct 2026 | Comic-book journey with WebGL and sound for a drinks brand |
| The Search for Work Happiness | https://www.findworkhappiness.com | FWA FOTM Jun 2023 | Drag-to-paint line art, masking chapter transitions, layered audio |
| MindMarket | https://mindmarket.com/ | Awwwards SOTM Dec 2025 | Flat illustration + GSAP; Swup page transitions; Rive (Astro) |
| Don't Board Me | https://dontboardme.com | Awwwards SOTY Users' Choice 2024 | Graphic storytelling for a service business; Lottie; red #E33529 + sky #AFD8FB |
| KPR | https://kprverse.com/ | Awwwards SOTY 2022; FWA FOTM Feb 2023 | Illustrated world, scroll storytelling (Nuxt + three.js + GSAP) |

### E. Agency & portfolio: transitions, type, signature interaction

| Site | URL | Award | Study |
|---|---|---|---|
| Lusion v3 | https://lusion.co/ | Awwwards SOTY + Dev SOTY 2023; FWA FOTY (Jan 2024) | Real-time 3D studio site (Astro); single electric-blue accent #1a2ffb |
| Immersive Garden | https://immersive-g.com/ | Awwwards SOTM Jan 2025; FWA FOTM Jan 2025; Agency of the Year 2025 | Dark monochrome 3D, project pages, gesture interaction (Nuxt + Lenis) |
| Locomotive | https://locomotive.ca/en | FWA FOTM May 2023; Awwwards Agency of the Year 2022–2024 | Smooth-scroll craft from the makers of Locomotive Scroll |
| Active Theory V6 | https://activetheory.net/ | FWA FOTM Feb 2024 | Portfolio with new rendering, AI chat and multiplayer |
| Inkfish | https://inkfishnyc.com/ | Awwwards SOTM May 2024 | Fullscreen video, parallax, typographic transitions (Next.js) |
| Siena Film Foundation | https://siena.film | Awwwards SOTM Mar 2025 | Infinite scroll gallery, filters/effects, copy-led design (Webflow); black on cream |
| The Line Studio | https://thelinestudio.com/ | Awwwards SOTM Nov 2024; FWA FOTM Dec 2024 | Animation-studio reel as site; red-orange #FF391E + off-white |

### F. Product, brand & commerce

| Site | URL | Award | Study |
|---|---|---|---|
| Mana Yerba Mate | https://en.manayerbamate.com/ | Awwwards E-com 2023 | Shopify store with 3D, illustration, custom 404 — commerce that still converts |
| Shopify Editions — The Renaissance Edition | https://www.shopify.com/editions/winter2026 | Awwwards SOTM Feb 2026; FWA FOTM Mar 2026 | 150+ release notes set in generative paintings + 3D; Spline/Rive signals |
| Dropbox Brand | https://brand.dropbox.com/ | Awwwards SOTM Feb 2025; FWA FOTM Feb 2025 | Brand guidelines as an interactive playground (Webflow + Spline + Lottie) |
| Anime.js | https://animejs.com | Awwwards SOTM May 2025 | Dev-tool landing where the product (animation) is the demo |

### G. Luxury hospitality & real estate

| Site | URL | Award | Study |
|---|---|---|---|
| Son Daven | https://sondaven.com/en | Awwwards SOTM Jun 2026 | Resort site: WebGL + GSAP on Webflow, Barba page transitions, earthy palette |
| ERA Residence | https://www.era-residence.com/ | Awwwards SOTM Aug 2026 | Real-estate parallax storytelling, pastel #B5CEDB/#F8BBCB (Webflow + GSAP + Barba) |
| Explore Primland | https://explore.ownprimland.com/ | FWA FOTM Feb 2026 | Immersive resort tour (Nuxt) — compare how booking stays reachable |

### H. AI-themed

| Site | URL | Award | Study |
|---|---|---|---|
| Kriss.ai | https://kriss.ai/ | Awwwards SOTM Oct 2024 | AI patient-care chatbot marketing: illustration, transitions, 3D (Svelte) |
| Little Red Riding Hood's Quest | https://ai-quest.lusion.co/ | FWA FOTM Aug 2023 | AI-driven storytelling game by Lusion |

Stack signals come from HTML only (e.g. `/_nuxt/`, `astro-island`, `lenis`, `barba`); bundled libraries are often invisible, so absence proves nothing.

## Health and telemedicine product references

Award galleries rarely cover regulated categories, so study live products instead (all URLs returned 200 on 2026-10-10). Use them to see how trust, credentials, pricing and booking are handled, then pair with `product-patterns.md` §6.

| Product | URL | Look at |
|---|---|---|
| Doctor Anywhere Thailand (incl. former Doctor Raksa) | https://www.doctoranywhere.co.th/ | Thai-language telehealth: service menu, pricing display, app-download vs web flow |
| Doctor Anywhere (regional) | https://www.doctoranywhere.com/ | How one brand presents teleconsult, house calls, clinics and screenings across SG/TH/MY/PH/ID |
| Halodoc (Indonesia) | https://www.halodoc.com/ | Southeast-Asian consult + pharmacy delivery flows |
| NHS App | https://www.nhs.uk/nhs-app/ | Plain-language public-health UX, accessibility-first content |
| One Medical | https://www.onemedical.com/ | Membership + booking presentation, clinician credibility |
| Teladoc Health | https://www.teladochealth.com/ | Enterprise telehealth positioning, service breadth without clutter |
| Maven Clinic | https://www.mavenclinic.com/ | Family/women's-health tone, employer-benefit messaging |
| Oscar Health | https://www.hioscar.com/ | Insurance explained in plain language, friendly illustration system |
| Headspace | https://www.headspace.com/ | Warm illustration and motion in a wellness product |

## Commerce, streetwear and beauty product references

Award galleries show drop campaigns and beauty brand films, rarely the launch mechanics or the ingredient and shade tools. Study these live products instead (every URL returned 200 to `curl -s -o /dev/null -L --max-time 20 -A 'Mozilla/5.0 (Macintosh) AppleWebKit/537.36 Chrome/126.0 Safari/537.36' -w '%{http_code}'` on 2026-10-10; "look at" items were read from the served pages that day). Pair with `product-patterns.md` §4 (limited drops) and §19 (beauty).

| Product | URL | Look at |
|---|---|---|
| Nike SNKRS (web) | https://www.nike.com/launch | Launch feed split into Feed / In Stock / Upcoming; draw entry → result flow (rules: https://www.nike.com/help/a/nike-snkrs-draw) |
| END. Launches | https://www.endclothing.com/gb/launches/all-launches | Launch calendar; each product carries a Unix release time and a countdown mode in its page data, the model for server-time countdowns |
| Limited Edt (Singapore) | https://limitededt.com/ | Southeast-Asian sneaker retail: launches and raffles announced by newsletter, "Sold out" kept visible on product cards |
| Aimé Leon Dore | https://www.aimeleondore.com/ | Photography-led streetwear store with seasonal "Delivery 1 / Delivery 2" drops, saved "My Sizes" and a "Hide sold out products" filter |
| The Ordinary (Thailand locale) | https://theordinary.com/en-th | Actives and % in product names; Shop by Concern; Regimen Builder, Layering Guide and Ingredient Glossary; shop by routine step; "Join the Waitlist" for coming-soon products |
| Paula's Choice Ingredient Dictionary | https://www.paulaschoice.com/ingredient-dictionary | Ingredient-level reference pages (benefits and safety) that a PDP's INCI list can link to |
| Fenty Beauty | https://fentybeauty.com/ | Selfie-based foundation shade finder with an undertone guide (https://fentybeauty.com/pages/fenty-face-shade-finder); shade count on product cards; "Refillables" category; "Shade Feedback" link |
| Rare Beauty | https://www.rarebeauty.com/ | Foundation Shade Finder in 4 steps; "Choose 2" free samples inside the cart; a dated launch teaser ("Coming soon \| 10.12") on the hero; berry brand colour + serif display |
| Le Labo | https://www.lelabofragrances.com/ | Fragrance discovery sets, refills, 50 ml / 100 ml size browsing, personalised label that defaults to "For: You." |
| Oriental Princess (Thailand) | https://www.orientalprincess.com/ | Thai-language navigation by skin problem (ปัญหาผิว) and product type; skin quiz with age bands 20s+ to 50s+; member promo with its dates and limits printed under the offer |
| PAÑPURI (Thailand) | https://panpuri.com/ | Spa and fragrance luxury: moody, earthy photography; skincare by skin type ("For Dry & Dehydrated Skin"); 10 ml / 50 ml sizes; refills; engraving service |
| Sunnies Face (Philippines) | https://sunniesface.com/ | "Find your shade"; shade descriptions with undertone ("light with cool undertones"); per-shade sold-out states |

Excluded on 2026-10-10: Aesop, Sephora Thailand, Carnival Bangkok and atmos Tokyo returned 403 (bot-blocked); erbasia.com redirected to an unrelated domain.

## How to study a reference site

Goal: extract **decisions** (grid, type scale, palette roles, motion timing, interaction model), not assets. Re-create; never copy code, models, fonts or images (licences).

**Checklist — write one line each:**
1. **Job & audience:** what is the page selling/doing, to whom; where is the primary CTA.
2. **Layout grid:** columns, gutters, max content width, section rhythm (vertical spacing scale), breakpoints. Use the Elements panel's grid/flex overlays and `getComputedStyle(el).gridTemplateColumns`.
3. **Type scale:** families, weights, sizes per level (h1…small), line-heights, letter-spacing, measure; ratio between steps (compare with `typography-layout.md`).
4. **Palette roles:** background, surface, text, muted text, accent, link, focus; count how few colours carry the design (Awwwards lists 1–2 key HEX values per winner; most in this catalog use just 2).
5. **Motion timing:** durations, easings, stagger, delays; what triggers motion (load, scroll, hover, click); whether it respects `prefers-reduced-motion`.
6. **Interaction model:** navigation pattern, scroll behaviour (native vs smooth-scroll library), page transitions, cursor effects, keyboard/touch support.
7. **Tech & performance:** framework, smooth-scroll/transition libs, WebGL/WebGPU, page weight, frame rate on a mid-range device.
8. **What to borrow vs avoid** for *this* product type (`product-patterns.md` motion level).

**Tools (Chrome DevTools, as of 2026):**
- **Animations panel** — captures CSS transitions, CSS animations, Web Animations and View Transitions (not `requestAnimationFrame`); reload with the panel open to catch load animations; slow down, scrub, replay; drag to read/change duration, delay and keyframe offsets. Easing is edited in Styles.
- **CSS Overview panel** — colours by type (with low-contrast text), fonts by size/weight/line-height, media queries. (Doc dates from Chrome 96 "preview"; check it is still in your build.)
- **Performance panel** — record a scroll to see long tasks and dropped frames.
- **Network → JS filter** — library names in chunk URLs (`three`, `gsap`, `lenis`, `barba`, `swup`, `rive`, `lottie`).

**Console snippet (paste on the reference page; read-only):**

```js
// Works in current Chromium/Firefox/Safari (2026). Prints fonts, type ramp, top colours, animations, libraries.
(async () => {
  await document.fonts.ready;
  const fonts = [...document.fonts].filter((f) => f.status === 'loaded')
    .map((f) => `${f.family} ${f.weight} ${f.style}`);
  const ramp = ['h1', 'h2', 'h3', 'p', 'a', 'button', 'small'].map((sel) => {
    const el = document.querySelector(sel); if (!el) return null;
    const cs = getComputedStyle(el);
    return { sel, family: cs.fontFamily.split(',')[0], size: cs.fontSize, lineHeight: cs.lineHeight,
             weight: cs.fontWeight, tracking: cs.letterSpacing };
  }).filter(Boolean);
  const counts = new Map();
  for (const el of document.querySelectorAll('body *')) {
    const r = el.getBoundingClientRect(); if (!r.width || !r.height) continue;
    const cs = getComputedStyle(el);
    for (const c of [cs.color, cs.backgroundColor]) {
      if (c === 'transparent' || /^rgba\([^)]*,\s*0\)$/.test(c) || /\/\s*0\)$/.test(c)) continue; // skip fully transparent
      counts.set(c, (counts.get(c) ?? 0) + 1);
    }
  }
  const palette = [...counts].sort((a, b) => b[1] - a[1]).slice(0, 10);
  const animations = document.getAnimations().slice(0, 25).map((a) => {
    const t = a.effect?.getTiming?.() ?? {};
    return { name: a.animationName ?? a.transitionProperty ?? a.id, duration: t.duration, delay: t.delay, easing: t.easing };
  });
  const libs = {
    three: window.__THREE__,            // three.js registers its revision here
    gsap: window.gsapVersions,          // GSAP pushes its version(s) here
    lenis: window.lenisVersion,         // Lenis smooth scroll sets this
    lenisClass: document.documentElement.classList.contains('lenis'),
  };
  console.log({ fonts, ramp, palette, animations, libs });
})();
```

**Worked example (run 2026-10-10 on https://landonorris.com/, Awwwards SOTY 2025):** fonts `Brier 700` (display) + `Mona Sans Variable 200–900`; top colours rgb(40,44,32), rgb(244,244,237), rgb(17,17,18) = #111112, rgb(210,255,0) = #D2FF00; libs: three.js r174, GSAP 3.13.0, Lenis 1.1.20 (`lenis` class on `<html>`); `document.getAnimations()` = 0 → all motion is rAF/GSAP-driven, so the Animations panel shows nothing. The ramp takes the *first* match per tag (here a tiny 8 px `h3`) — re-run with specific selectors for the hero.

Slow everything down to read timing: `document.getAnimations().forEach((a) => (a.playbackRate *= 0.25))` (CSS/WAAPI only). For GSAP-driven motion exposed as a global (CDN builds), `gsap.globalTimeline.timeScale(0.25)`; three.js/rAF loops can't be slowed from outside — use a screen recording at 0.25× instead.

**Record the result** as a 10-line spec: grid · type ramp · 2–5 palette roles · 3 motion tokens (duration/easing) · interaction model · tech notes · borrow/avoid. Feed it to `design-systems.md` tokens, not straight into components.

## Pitfalls

| Symptom | Cause | Fix |
|---|---|---|
| Agent returns "blocked" for Land-book/Codrops/CodePen/Shadertoy | Cloudflare/Vercel bot challenge | Use an open alternative from the same row, or a browser tool with the user's approval; never bypass challenges |
| Gallery link 301s somewhere unexpected | Rebrands: Godly → Recent, UI Sources → ScreensDesign; Screenlane parked; Rive community → Marketplace | Use the current URLs in this file; re-test before citing |
| Award site link is dead or shows a different product | Campaign microsites expire (LVMH Maison of All Victories, nvg8.io offline); products pivot (Opal Tadpole page → op.al home; Zentry repositioned) | `curl` status + read `<title>` before sharing; prefer studio portfolios/case studies for longevity |
| "Signature" effect can't be found in the Animations panel | Driven by `requestAnimationFrame` (GSAP ticker, three.js, Lenis) | Check `window.__THREE__`, `window.gsapVersions`, `window.lenisVersion`; record and step through video |
| Copied an award aesthetic into a banking/health/gov product | Motion level mismatch | Cap motion with `product-patterns.md`; borrow palette/type discipline, not the WebGL |
| Reference palette fails contrast when reused | Award sites optimise mood over AA | Re-derive roles in OKLCH and test (`color.md`, `accessibility.md`) |

## Sources

- Awwwards — home — https://www.awwwards.com/
- Awwwards — Sites of the Month — https://www.awwwards.com/websites/sites_of_the_month/
- Awwwards — Sites of the Year — https://www.awwwards.com/websites/sites_of_the_year/
- Awwwards — Annual Awards hall of fame — https://www.awwwards.com/annual-awards/hall-of-fame
- Awwwards — robots.txt — https://www.awwwards.com/robots.txt
- The FWA — https://thefwa.com/ (timeline JSON: https://thefwa.com/api/timeline/)
- CSS Design Awards — WOTD winners — https://www.cssdesignawards.com/wotd-award-winners
- CSS Design Awards — about the awards — https://www.cssdesignawards.com/awards/
- Recent (formerly Godly) — https://recent.design/
- One Page Love — https://onepagelove.com/
- Httpster — https://httpster.net/
- Minimal Gallery — https://minimal.gallery/
- SaaS Landing Page — https://saaslandingpage.com/
- Landingfolio — https://www.landingfolio.com/
- SaaSFrame — https://www.saasframe.io/
- Navbar Gallery — https://www.navbar.gallery/
- Dark Mode Design — https://www.darkmodedesign.com/
- Collect UI — https://collectui.com/
- Land-book — https://land-book.com/ ; Lapa Ninja — https://www.lapa.ninja/ ; SiteInspire — https://www.siteinspire.com/ (tested, bot-blocked)
- Dribbble — https://dribbble.com/ ; Behance — https://www.behance.net/ (tested, bot-blocked)
- Mobbin — https://mobbin.com/
- Page Flows — https://pageflows.com/
- Refero — https://refero.design/
- ScreensDesign (UI Sources redirect) — https://screensdesign.com/
- GSAP showcase — https://gsap.com/showcase/
- Codrops — https://tympanus.net/codrops/ ; CodePen — https://codepen.io/ ; Shadertoy — https://www.shadertoy.com/ (tested, bot-blocked)
- three.js examples — https://threejs.org/examples/ and https://threejs.org/examples/files.json
- Spline community — https://community.spline.design/
- Rive Marketplace — https://rive.app/marketplace/
- LottieFiles — https://lottiefiles.com/
- Fonts In Use — https://fontsinuse.com/
- Typewolf — https://www.typewolf.com/
- Realtime Colors — https://www.realtimecolors.com/
- Component Gallery — https://component.gallery/
- Design Systems Repo — https://designsystemsrepo.com/
- designsystems.surf — https://designsystems.surf/
- Adele by UXPin — https://adele.uxpin.com/
- Commerce, streetwear and beauty references — the 12 live sites in that section (curl 200, 2026-10-10); SNKRS Draw help — https://www.nike.com/help/a/nike-snkrs-draw ; Fenty shade finder — https://fentybeauty.com/pages/fenty-face-shade-finder
- Chrome DevTools — Inspect animations — https://developer.chrome.com/docs/devtools/css/animations
- Chrome DevTools — CSS Overview — https://developer.chrome.com/docs/devtools/css-overview
- MDN — Document.getAnimations() — https://developer.mozilla.org/en-US/docs/Web/API/Document/getAnimations
- MDN — Document.fonts — https://developer.mozilla.org/en-US/docs/Web/API/Document/fonts
- three.js build (window.__THREE__) — https://cdn.jsdelivr.net/npm/three@0.180.0/build/three.core.js
- GSAP build (gsapVersions) — https://cdn.jsdelivr.net/npm/gsap@3.13.0/dist/gsap.js
- Lenis build (lenisVersion, `lenis` class) — https://cdn.jsdelivr.net/npm/lenis@1.3.4/dist/lenis.mjs
