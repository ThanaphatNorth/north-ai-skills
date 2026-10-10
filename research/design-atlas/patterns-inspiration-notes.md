# Research notes — product patterns + inspiration catalog (design-atlas)

Collected 2026-10-10. Provenance record for `skills/design-atlas/references/product-patterns.md` and `skills/design-atlas/references/inspiration.md`.
Session note: the shared WebSearch budget ran out after 2 queries, so everything below came from direct WebFetch / `curl` of primary pages (no search-engine scraping). Public listing pages only, no logins; robots.txt read for each award site before scraping.

## 1. Scrape method (repeatable)

- **Awwwards** (robots.txt allows `/websites/sites_of_the_month/`, `/websites/sites_of_the_year/`, `/sites/<slug>`; disallows `/websites/?` query filters, `/gallery/`, `/search-websites`, `/vote/`).
  - Listing pages embed JSON per card: `"slug":"…","title":"…","createdAt":<unix>,"tags":[…]` (parse after HTML-unescaping).
  - Site pages `/sites/<slug>` expose: agency ("by …"), "Site of the Day - <date>", palette HEX values, "Technologies & Tools" tags, description, and the external URL on the "Visit Site" link.
  - Annual winners: `https://www.awwwards.com/annual-awards/hall-of-fame/<year>` has `data-category="…"` + `data-link="/sites/<slug>"` (server-rendered). The per-year `/annual-awards-2024/...` pages now 404; `/annual-awards/winners` shows the latest year only.
  - Developer Award listing is behind the disallowed `/websites/?award=…` filter → not scraped (respect robots). Dev SOTY winners taken from hall of fame instead.
- **The FWA** (SPA). The page's own public JSON feed: `https://thefwa.com/api/timeline/?limit=100&offset=N` (items `type:"awards"`, `title` ∈ FWA of the Day / FWA of the Month / FWA of the Year / People's Choice Award; `item.url` = live site, `item.categories`, `item.description`, `item.extraText` = case write-up). Paged 15×100 items back to 2023-01-13 (1,366 FOTD, 45 FOTM, 4 FOTY, 4 PCA).
- **CSS Design Awards**: `https://www.cssdesignawards.com/wotd-award-winners` is server-rendered (site name, external URL, JPANEL score, WOTD). `/woty/` returns 403 to curl → WOTY not scraped. CSSDA awards page: WOTD needs judge avg above ~8.00; Special Kudos above 6; public UI/UX/INN awards need >20 votes + judge avg >6; WOTM + select WOTD enter WOTY; DOTY in Solo / Studio (2–10) / Agency (10+) (https://www.cssdesignawards.com/awards/).
- **Godly**: `https://godly.website/` now **301-redirects to `https://recent.design/?ref=godly`** ("Recent — Design Inspiration"); feed is client-rendered (items like `/i/<id>-<slug>`, media on `cdn.recent.design`), external URLs not in HTML → not scraped.
- **Codrops**: every path (`/codrops/`, `/feed/`, category pages) returns a Cloudflare challenge (403) to curl and WebFetch → not scraped.
- **URL verification**: `curl -sI -L -o /dev/null -w '%{http_code}'` (HEAD) then GET fallback when HEAD ≠ 200 (kprverse.com returns 404 to HEAD but 200 to GET). Then GET each homepage to record final URL, `<title>`, and stack signatures (regex over HTML: `/_next/`, `/_nuxt/`, `astro-island`, `webflow`, `cdn.shopify`, `wp-content`, `three`, `gsap|ScrollTrigger`, `lenis`, `barba`, `swup`, `spline`, `@rive-app`, `lottie`, `navigator.gpu`). Signatures are a lower bound: bundled libraries often don't appear in HTML.

## 2. Awwwards annual winners (hall of fame, fetched 2026-10-10)

| Year | Site of the Year | Developer SOTY | E-commerce of the Year | Agency | Studio | Independent | Users' Choice |
|---|---|---|---|---|---|---|---|
| 2025 | Lando Norris (OFF+BRAND.) | Messenger (abeto) | Scout Motors (Locomotive) | Immersive Garden | Malvah | Louis Paquet | Lando Norris |
| 2024 | Igloo Inc (abeto / Bureaux) | Igloo Inc | Opal Tadpole (Claudio Guglieri) | Locomotive | Immersive Garden | Jesper Landberg | Don't Board Me |
| 2023 | Lusion v3 (Lusion) | Lusion v3 | Mana Yerba Mate (Louis Paquet) | Locomotive | Obys | Aristide Benoist | Noomo Agency |
| 2022 | KPR (Resn) | Persepolis Reimagined | Mr Pops | Locomotive | Synchronized Studio | Jesper Landberg | The Other Side of Truth |

Sources: https://www.awwwards.com/annual-awards/hall-of-fame (2025), https://www.awwwards.com/annual-awards/hall-of-fame/2024, /2023, /2022; https://www.awwwards.com/annual-awards/winners (vote counts 2025: SOTY 43 jury votes, Users' Choice 596 votes).
How SOTY is picked (search snippet of Wikipedia mirror): jury chooses from the 12 Sites of the Month + 3 extra SOTD nominees; Developer SOTY chosen by the developer jury from Developer Award winners (https://en.wikipedia.org/wiki/Awwwards).

## 3. Awwwards Sites of the Month (raw, `/websites/sites_of_the_month/`, month = award month)

- 2026-09 — Why Zero — tags: Culture & Education, Technology, Single page, Sound-Audio, Storytelling, GSAP, Three.js, 3D, Gestures / Interaction, Filters and Effects, Startups, Blender
- 2026-08 — ERA Residence — tags: Architecture, Parallax, Storytelling, GSAP, Real Estate, Photo & Video, Webflow, Luxury
- 2026-07 — Lama Lama — tags: Design Agencies, E-Commerce, Web & Interactive, Animation, Graphic design, WebGL, GSAP, Javascript
- 2026-06 — Son Daven — tags: E-Commerce, Food & Drink, Hotel / Restaurant, Animation, Scrolling, WebGL, Storytelling, GSAP, UI design, Microinteractions, Webflow
- 2026-05 — Floema — tags: Business & Corporate, E-Commerce, Promotional, Photographic, WebGL, Storytelling, GSAP, 3D, Header Design, Nuxt.js
- 2026-04 — Oryzo AI — tags: Art & Illustration, Design Agencies, Web & Interactive, WebGL, Transitions, Storytelling, GSAP, Three.js, 3D, Filters and Effects
- 2026-03 — GQ & AP The Extraordinary Lab — tags: Fashion, Web & Interactive, Responsive Design, WebGL, Experimental, 3D, Gestures / Interaction, Nuxt.js, Blender
- 2026-02 — The Renaissance Edition — tags: E-Commerce, Technology, Web & Interactive, Animation, Parallax, WebGL, Transitions, Shopify, 3D, Gestures / Interaction, Interaction Design, Blender
- 2026-01 — Bruno's Portfolio — tags: Games & Entertainment, Web & Interactive, WebGL, GSAP, Three.js, 3D
- 2025-12 — MindMarket — tags: Art & Illustration, Culture & Education, Promotional, Animation, Colorful, Flat Design, Scrolling, Illustration, Storytelling, GSAP, Figma, DatoCMS
- 2025-11 — Lando Norris — tags: Promotional, Sports, Web & Interactive, Colorful, WebGL, GSAP, 3D, Gestures / Interaction, Webflow
- 2025-10 — Ponpon Mania — tags: Art & Illustration, Games & Entertainment, Web & Interactive, Parallax, Unusual Navigation, WebGL, Illustration, Storytelling, GSAP, 3D, Microinteractions, Nuxt.js
- 2025-09 — Terminal Industries — tags: Business & Corporate, Technology, Animation, CSS, Scrolling, Storytelling, Interaction Design, Vue.js, Startups, Vercel
- 2025-08 — Cartier Watches & Wonders 2025 — tags: Web & Interactive, Animation, Responsive Design, Scrolling, WebGL, Experimental, 3D, Gestures / Interaction, UI design, Motion, Luxury
- 2025-07 — Tracing Art — tags: Art & Illustration, Culture & Education, Institutions, Big Background Images, Clean, Colorful, Scrolling, Data Visualization, Content architecture
- 2025-06 — Montfort — tags: Business & Corporate, Web & Interactive, Scrolling, Responsive, 3D, Gestures / Interaction, UI design
- 2025-05 — Anime.js — tags: Technology, Web & Interactive, Animation, Scrolling, 3D
- 2025-04 — Navigate — tags: Games & Entertainment, Technology, Animation, Colorful, Scrolling, Illustration, Data Visualization, Storytelling, Startups
- 2025-03 — Siena Film Foundation — tags: Design Agencies, Film & TV, Institutions, Infinite Scroll, Navigation Menu, Transitions, Filters and Effects, Copy design, Microinteractions
- 2025-02 — Dropbox Brand — tags: Design Agencies, Animation, Colorful, Navigation Menu, Scrolling, Storytelling, Microinteractions
- 2025-01 — Immersive Garden website — tags: Web & Interactive, Animation, Experimental, 3D, Gestures / Interaction, UI design, Project Page, Contentful
- 2024-12 — David Whyte Experience — tags: Art & Illustration, Culture & Education, Animation, Colorful, Scrolling, Experimental, Storytelling, Gestures / Interaction, WooCommerce
- 2024-11 — The Line Studio — tags: Art & Illustration, Games & Entertainment, Animation, Graphic design, Typography, Startups
- 2024-10 — Kriss.ai — tags: Business & Corporate, Technology, Illustration, Transitions, Storytelling, 3D, Interaction Design, Startups
- 2024-09 — Watson — tags: Art & Illustration, Design Agencies, Web & Interactive, Responsive Design, Content architecture, Interaction Design, UI design, Project Page
- 2024-08 — Zentry — tags: Games & Entertainment, Web & Interactive, Colorful, Scrolling, Responsive, Sound-Audio, Storytelling, UI design, Startups
- 2024-07 — Igloo Inc — tags: Web & Interactive, Animation, Infinite Scroll, Transitions, 3D
- 2024-06 — Slosh Seltzer — tags: Design Agencies, Food & Drink, Web & Interactive, Colorful, Graphic design, Transitions, Microinteractions
- 2024-05 — Inkfish — tags: Design Agencies, Film & TV, Web & Interactive, Fullscreen, Parallax, Typography, Transitions, UI design, Microinteractions
- 2024-04 — Akaru — tags: Design Agencies, E-Commerce, Web & Interactive, Animation, Colorful, Unusual Navigation, Filters and Effects, UI design, About Page
- 2024-03 — Bennett & Clive — tags: Fashion, Film & TV, Flat Design, Minimal, Typography, Photography, Photo & Video, About Page, Footer Design

## 4. FWA of the Month / Year / People's Choice (raw, from `thefwa.com/api/timeline/`, 2023-01 → 2026-10)

- FOTM 2026-10 — Awards Racing — https://awards.racing — by Ecofuture — cats: Animation, Fun & Playable, Game
- FOTM 2026-09 — Santioni Spirits: The Notturno Experience — https://santionispirits.com/ — by Active Theory, Plan8 — cats: Commercial/Corporate, Food & Drink
- FOTM 2026-08 — Why Zero — https://why.zero.university/ — by Sindhur Dutta, Zero Design — cats: Educational, Experimental, Promotional
- FOTM 2026-07 — Lacoste Ace Breaker — https://members-play.lacoste.com/ace-breaker-rg — by Merci-Michel — cats: Fashion, Fun & Playable, Game
- FOTM 2026-06 — IVRESS SPIN A TALE — https://brand.ivress.co.jp/ — by Laugh Mind, Utsubo — cats: Animation
- FOTM 2026-05 — Shader Development Studio — https://www.shader.se — by Shader Development Studio, Andreas Antonsson — cats: Design/Production Studios, Experimental, Promotional
- FOTM 2026-04 — Oryzo AI — https://oryzo.ai/ — by Lusion — cats: Design/Production Studios, Fun & Playable, AI
- FOTM 2026-03 — The Renaissance Edition — https://www.shopify.com/editions/winter2026 — by Shopify Design — cats: Commercial/Corporate, Promotional, Resource & Community
- FOTM 2026-02 — Explore Primland — https://explore.ownprimland.com/ — by Outpost, Ingamana, Robert Borghesi, Robbin Cenijn — cats: Travel & Tourism
- FOTY 2026-01; FWA PCA 2026-01; FOTM 2026-01 — Bruno's Portfolio — https://bruno-simon.com — by Bruno Simon — cats: Fun & Playable, Game, Personal/Portfolio
- FOTM 2025-12 — The Monolith Project — https://themonolithproject.net/ — by Kehan Fan, Ethan Chiu, Fabian Tjoe-A-On, Nando Correa — cats: Various & Other
- FOTM 2025-11 — Messenger — https://messenger.abeto.co — by abeto — cats: Game, Metaverse
- FOTM 2025-10 — Gen-02 SMSY Portfolio — http://samsy.ninja — by Samsy — cats: Personal/Portfolio, Metaverse
- FOTM 2025-09 — Welcome to Berk — https://powster.com/case-study/welcome-to-berk/ — by POWSTER, Rogier de Boevé — cats: Experimental, Film/Movies, Mobile
- FOTM 2025-08 — Yamê — The Molazone — https://mola-zone.com/ — by Studio9p, Hugo Maury — cats: Fun & Playable, Music & Sound, Promotional
- FOTM 2025-07 — Arina's Story — https://arinastory.com — by ISD Group, United24, Microsoft, SENSORAMA LAB — cats: Animation, Art, Illustration & Exhibition, Experimental
- FOTM 2025-06 — Jordan's Portofolio — https://jordan-delcros.com/ — by Jordan Delcros — cats: Animation, Fun & Playable, Personal/Portfolio
- FOTM 2025-05 — Navigate — https://nvg8.io/ — by Resn — cats: Animation, Game, Resource & Community
- FOTM 2025-04 — Elimar — https://elimar.lmigroupintl.com/ — by OddCommon — cats: Architecture & Design, Art, Illustration & Exhibition, Educational
- FOTM 2025-03 — Lacoste Members Experience — https://membersexperience-create.lacoste.com/ — by Merci-Michel — cats: Art, Illustration & Exhibition, Fashion, Promotional
- FOTM 2025-02 — Dropbox Brand Guidelines — https://brand.dropbox.com/ — by Daybreak Studio — cats: Animation, Design/Production Studios
- FOTY 2025-01; FOTM 2024-06 — Food for Fish — https://foodforfish.org/ — by Kris Temmerman — cats: Experimental, Game
- FWA PCA 2025-01; FOTM 2024-11 — Hatom — https://www.hatom.com/ — by Immersive Garden — cats: Animation, Experimental, NFT
- FOTM 2025-01 — Immersive Garden website — https://immersive-g.com/ — by Immersive Garden — cats: Design/Production Studios, Experimental, Personal/Portfolio
- FOTM 2024-12 — The Line Studio — https://thelinestudio.com/ — by Thomas Aufresne, Isaac Powell, The Line Studio — cats: Animation, Commercial/Corporate, Design/Production Studios
- FOTM 2024-10 — Following Wildfire — https://followingwildfire.com/ — by Reflektor Digital, Dentsu Canada — cats: Animation, Resource & Community, AI
- FOTM 2024-09 — The Maison of All Victories — https://the-maison-of-all-victories.lvmh.com/en — by Cosmic Shelter, Michaël Garcia, LVMH, Bertrand Breton — cats: Fashion, Fun & Playable, Sports & Leisure
- FOTM 2024-08 — Igloo Inc — https://www.igloo.inc/ — by Bureaux — cats: Animation, Commercial/Corporate, Experimental
- FOTM 2024-07 — Kaizen — https://kaizen.makemepulse.com — by makemepulse, Press Play On Tape — cats: Experimental, Fun & Playable
- FOTM 2024-05 — Equinox — https://equinox.space — by Little Workshop — cats: Fun & Playable, Game, Mobile
- FOTM 2024-04 — BOUCHERON - Quatre 20th Anniversary — https://quatre.merci-michel.com/ — by Merci-Michel — cats: Fashion, Fun & Playable, Game
- FOTM 2024-03 — Casa di Solare — https://casadisolare.com — by Unseen Studio®, Jesper landberg — cats: Art, Illustration & Exhibition, Design/Production Studios, Personal/Portfolio
- FOTM 2024-02 — Active Theory V6 — https://activetheory.net/ — by Active Theory — cats: Art, Illustration & Exhibition, Design/Production Studios, Personal/Portfolio
- FOTY 2024-01; FOTM 2023-10 — Lusion v3 — https://lusion.co/ — by Lusion — cats: Animation, Personal/Portfolio, Promotional
- FWA PCA 2024-01; FOTM 2023-03 — Loewe x Howl's Moving Castle — https://howls.loewe.com/ — by Stink Studios, LOEWE — cats: Art, Illustration & Exhibition, Fashion, Film/Movies
- FOTM 2024-01 — The Fabulous Cartier Journey — https://www.cartier.com/thefabulouscartierjourney — by Merci-Michel — cats: Fashion, Fun & Playable, Game
- FOTM 2023-12 — Sculpting Harmony — https://gehry.getty.edu/ — by Resn, The Getty — cats: Architecture & Design, Educational, Music & Sound
- FOTM 2023-11 — Haunted by Nostalgia — https://haunted.thedigitalpanda.com — by The Digital Panda — cats: Experimental, Film/Movies, Fun & Playable
- FOTM 2023-09 — Önnu Jónu Son — https://onnujonuson.com/clip/almost-over-you — by Robbin Cenijn, Aristide Benoist, Ueno — cats: Animation, Music & Sound, Promotional
- FOTM 2023-08 — Little Red Riding Hood's Quest — https://ai-quest.lusion.co/ — by Lusion — cats: Animation, Game, AI
- FOTM 2023-07 — Aten7 — https://www.aten7.com/ — by Immersive Garden — cats: Experimental, Fun & Playable, Game
- FOTM 2023-06 — The Search for Work Happiness — https://www.findworkhappiness.com — by David Lubofsky, Bryan James, Jesper landberg, Dave Ellis — cats: Animation, Art, Illustration & Exhibition, Fun & Playable
- FOTM 2023-05 — Locomotive® — https://locomotive.ca — by Locomotive — cats: Commercial/Corporate, Design/Production Studios, Promotional
- FOTM 2023-04 — Curious & Company — https://curious.co — by Curious & Company — cats: Design/Production Studios, Personal/Portfolio, Promotional
- FOTM 2023-02 — KPR — https://kprverse.com/ — by Resn — cats: Art, Illustration & Exhibition, NFT, Metaverse
- FOTY 2023-01; FWA PCA 2023-01 — Getty Villa: Persepolis Reimagined — http://www.getty.edu/persepolis — by The Getty, Monks — cats: Architecture & Design, Art, Illustration & Exhibition, Educational

## 5. CSS Design Awards — recent WOTD winners (raw, `/wotd-award-winners`, page as of 2026-10-10; JPANEL = judges score)

- Wonder Vision — https://www.wonder-vision.com/ — 8.13
- 1367 Studio — https://www.1367studio.com/ — 8.42
- EddyOS — Eddy Naboulet — https://eddy-naboulet.dev/ — 8.30
- Bulles — https://experience.projetbulles.com/ — 8.58
- Agrumea Farm — https://www.agrumeafarm.it/en — 8.37
- Sobha Privy Collection — https://sobha-privy-collection.com/ — 8.40
- STUDIO seitaro — https://seitaroyamazaki.com/ — 8.01
- La Revoltosa — https://larevoltosa.es/ — 8.01
- A24 (Ravi Klaassens concept) — https://a24.raviklaassens.com/ — 8.44
- Safeer (Webflow template) — https://safeertemplate.webflow.io/ — 8.09
- EASYSELLER — https://www.easyseller.it/ — 8.14
- ZIRKA Interceptor — https://www.zrk.technology/ — 8.27
- The Ride — https://arunnm.com/ — 8.31
- Viru — https://www.virugroup.com/en/ — 8.01
- Juan Mora Romero — https://www.juanmoraromero.com/ — 8.04
- Awards Racing — https://awards.racing — 8.44
- Catskills — https://catskills-showcase.pages.dev/ — 8.26
- Emotion Agency — https://emotion-agency.com — 8.48

## 6. Inspiration sources — reachability test (2026-10-10, curl with desktop Chrome UA, then WebFetch where noted)

| Source | URL tested | Result | Final URL / note |
|---|---|---|---|
| Awwwards | https://www.awwwards.com/ | 200, server-rendered | JSON in cards; robots disallows query filters |
| The FWA | https://thefwa.com/ | 200 SPA shell | data via public `/api/timeline/`, `/api/hof` |
| CSS Design Awards | https://www.cssdesignawards.com/ | 200 | `/woty/` 403; `/wotd-award-winners` OK |
| Godly | https://godly.website/ | 200 after 301 | → https://recent.design/?ref=godly ("Recent — Design Inspiration"), client-rendered feed of sites, motion studies, posters, app icons, App Store screenshots |
| Land-book | https://land-book.com/ | 403 Cloudflare ("Just a moment...") | WebFetch also 403 |
| Lapa Ninja | https://www.lapa.ninja/ | 403 Cloudflare | |
| SiteInspire | https://www.siteinspire.com/ | 429 "Vercel Security Checkpoint" | |
| One Page Love | https://onepagelove.com/ | 200 | "One Page website design gallery … templates and resources" |
| Httpster | https://httpster.net/ | 200 | |
| Minimal Gallery | https://minimal.gallery/ | 200 | also sells Framer & Webflow templates |
| Mobbin | https://mobbin.com/ | 200 marketing page | meta: "400,000+ fully searchable mobile & web app screenshots"; WebFetch: "A free account provides limited access." / "Paid plans unlock the full library, search, flows, animations…"; screens, flows, patterns/elements, website sections; copy to Figma on eligible plans |
| Page Flows | https://pageflows.com/ | 200 | meta: "100,000+ recorded user flows"; paid: 3-day trial $2.95, $39/quarter, $99/year, team $199/yr (3–10 users); iOS, Android, Web, Email |
| Refero | https://refero.design/ | 200 but 4 KB SPA shell | meta: "largest collection of UI/UX references … for web and iOS" |
| Screenlane | https://screenlane.com/ | https fails (000); http → parked-domain lander | **defunct** |
| UI Sources | https://www.uisources.com/ | 200 after redirect | → https://screensdesign.com/ ("ScreensDesign: App Design Library & AI Screen Generator"; iOS screens, onboarding, paywalls) |
| Dribbble | https://dribbble.com/ | 202, empty body (bot challenge); WebFetch of /shots/popular/web-design returned empty | |
| Behance | https://www.behance.net/ | 403 | |
| Codrops | https://tympanus.net/codrops/ | 403 Cloudflare (curl + WebFetch; RSS feed too) | |
| CodePen | https://codepen.io/ | 403 Cloudflare | |
| GSAP showcase | https://gsap.com/showcase/ | 200 | filters by tool: Core, Scroll, SVG, UI, Text; plugin groups listed (ScrollTrigger, ScrollSmoother, ScrollTo, DrawSVG, MorphSVG, MotionPath, Flip, Draggable, Inertia, Observer, SplitText, ScrambleText, Physics2D, PhysicsProps, GSDevTools); recent entries incl. A24 (Ravi Klaassens), Illoca (Unseen Studio), David Lubofsky, Jesper Landberg |
| Spline community | https://community.spline.design/ | 200 | "discover, remix, and showcase 3D creations #MadeInSpline"; app.spline.design/community also 200 (SPA) |
| three.js examples | https://threejs.org/examples/ | 200 | machine-readable index https://threejs.org/examples/files.json — 607 examples in categories webgl, webgl / postprocessing, webgl / advanced, webgl / tsl, webgpu, webaudio, webxr, games, physics, misc, css2d, css3d, svg, tests; raw source fetchable from raw.githubusercontent.com/mrdoob/three.js/dev/examples/<name>.html |
| Shadertoy | https://www.shadertoy.com/ | 403 Cloudflare (WebFetch too); /api/v1/shaders 403 | |
| Rive community | https://rive.app/community/ | 404 | https://rive.app/community/files/ and https://rive.app/marketplace/ → "Rive - Marketplace" |
| LottieFiles | https://lottiefiles.com/ | 200 | /free-animations 200 |
| Fonts In Use | https://fontsinuse.com/ | 200 | "searchable archive of typographic design, indexed by typeface, format, and topic"; /typefaces returned 500 at test time |
| Typewolf | https://www.typewolf.com/ | 200 | fonts in the wild, recommendations |
| Realtime Colors | https://www.realtimecolors.com/ | 200 | 5 roles (Text, Background, Primary, Secondary, Accent), AA/AAA indicator, schemes, Alt+T dark/light, heading/body Google Fonts, type scale 1.067–1.618, export CSS/Tailwind/SCSS + presets (shadcn, DaisyUI, MUI, Chakra, Bootstrap, Flutter…), copy as HEX/RGB/HSL/OKLAB/OKLCH, share link |
| Collect UI | https://collectui.com/ | 200 | daily UI shots (Dribbble-sourced) |
| Navbar Gallery | https://www.navbar.gallery/ | 200 | navigation designs |
| SaaS Landing Page | https://saaslandingpage.com/ | 200 | SaaS landing pages |
| Dark Mode Design | https://www.darkmodedesign.com/ | 200 | dark-mode sites |
| Design Systems Repo | https://designsystemsrepo.com/ | 200 | /design-systems/ list 200 |
| Component Gallery | https://component.gallery/ | 200 | components across design systems |
| Design Systems Surf | https://designsystems.surf/ | 200 | browse real design systems |
| "Design Systems Gallery" | https://www.designsystemsgallery.com/ | no response (000) | name not verifiable; use Design Systems Repo / Component Gallery / designsystems.surf / Adele |
| Adele (UXPin) | https://adele.uxpin.com/ | 200 | "Design Systems and Pattern Libraries Repository" |
| SaaSFrame | https://www.saasframe.io/ | 200 | "5,000+ real-world UX & UI design examples" for SaaS |
| Landingfolio | https://www.landingfolio.com/ | 200 | landing pages, templates, components |
| Web Design Museum | https://www.webdesignmuseum.org/ | 403 Cloudflare | |
| Figma Community | https://www.figma.com/community | 200 | |

## 7. Product-pattern research notes (by sub-topic)

### Response time / loading
- NN/g response-time limits: 0.1 s feels instantaneous; 1 s keeps flow (show working state, e.g. cursor) ; 10 s attention limit → percent-done indicator + clear way to interrupt. https://www.nngroup.com/articles/response-times-3-important-limits/
- NN/g progress indicators (Katie Sherwin, 2014-10-26): any action >~1 s needs an indicator; looped spinner for ~2–10 s (conclusion says 2–9 s); percent-done for ≥10 s or record series ("Updating address 3 of 50"); avoid static "Loading…"; offer stop for long actions. https://www.nngroup.com/articles/progress-indicators/
- NN/g skeleton screens (2023-06-04, reviewed 2026-09-02): skeletons for full-page loads <10 s; spinners for single modules 2–10 s; progress bars >10 s; skip all indicators for <1 s loads; avoid frame-display skeletons (header/footer only); animated shimmer use with care (a11y). https://www.nngroup.com/articles/skeleton-screens/
- Doherty threshold 400 ms (Doherty & Thadani 1982, IBM Systems Journal): give feedback within 400 ms; perceived-performance techniques; deliberate delay can increase perceived value. https://lawsofux.com/doherty-threshold/
- NN/g animation duration (2020-02-09): most UI animations 100–500 ms; simple feedback ~100 ms; substantial screen changes (modal in) 200–300 ms; 400 ms "a very slow animation"; 500 ms "start[s] to feel like a real drag". https://www.nngroup.com/articles/animation-duration/
- WCAG 2.2 SC 2.3.3 Animation from Interactions (AAA): motion triggered by interaction can be disabled unless essential; parallax cited as common non-essential motion; vestibular triggers. https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html

### E-commerce (Baymard)
- Cart abandonment average 70.22% from 50 studies (list updated 2025-09-22; page titled 2026). Reasons (excl. "just browsing" = 42% of US shoppers): extra costs too high 40%; delivery too slow 20%; didn't trust site with card 19%; forced account 18%; too long/complicated checkout 17%; site errors/crash 17%; returns policy 13%; couldn't see total up-front 12%; card declined 10%; not enough payment methods 9%. Better checkout design → 35.26% conversion increase for large sites. Avg US checkout shows 23.48 form elements by default / 14.88 form fields. https://baymard.com/lists/cart-abandonment-rate
- Checkout benchmark: 344 top US/EU sites — 65% "mediocre" or worse, 2% "good"; avg site has 32 checkout improvements to make; 110+ checkout guidelines. https://baymard.com/research/checkout-usability
- Avg checkout 11.3 form fields (2024); most sites need only 8. (2024-06-26) https://baymard.com/research-articles/checkout-flow-average-form-fields
- Guest checkout (2023-01-17): 47% of sites with guest checkout fail to make it the most prominent option; 24% of US shoppers abandoned a cart in past quarter solely due to forced account creation. Recommendation: button (not link) at top of account-selection step, labelled "Guest", explicit option. https://baymard.com/research-articles/make-guest-checkout-prominent
- Delivery date (2023-06-27): 41% of sites don't show estimated delivery date at shipping selection; show a date (or date range ≤ ~5–7 days wide) per option next to cost; use carrier API with fallback. https://baymard.com/research-articles/shipping-speed-vs-delivery-date
- Shipping cost on PDP (2017-06-20): 21% abandoned for not seeing total cost up-front (older survey); 64% looked for shipping cost on PDP before add-to-cart; 43% of sites show none on PDP; 16% not even in cart. https://baymard.com/research-articles/show-shipping-costs-on-product-pages
- PDP benchmark: only 49% of sites "decent"/"good"; 51% mediocre or worse; 110+ PDP guidelines; User Reviews topic has the most guidelines (19). https://baymard.com/research/product-page
- Horizontal tabs (published 2018-10-17, updated 2026-07-08): still used by 29% of sites; users repeatedly overlook tab content; desktop → expanded sections; mobile → collapsed sections (long pages) or expanded (short); ~2–3 tabs practical max on mobile. https://baymard.com/research-articles/avoid-horizontal-tabs
- In-scale images (2017-05-30): 28% of sites lacked "In Scale" images; 42% of users try to gauge size from images; 56% start by exploring images. https://baymard.com/research-articles/in-scale-product-images
- Product lists: mediocre list usability → 67–90% abandonment vs 17–33% with slightly optimized toolset; 36% of sites have severe flaws; avg site needs 35 changes. https://baymard.com/research/ecommerce-product-lists
- 5 essential filters (2020-08-18): price (12% lack), user rating (53% lack), color (10%), size (15%), brand (27%); 57% of sites lack at least one. https://baymard.com/research-articles/5-essential-filters
- Baymard "load more" blog URL resolves but content not readable by WebFetch → pagination/load-more recommendation NOT captured (left out of reference).
- Trust (Baymard 2011 article): polished design, recent activity, real people, social proof, speed, conventions, payment/partner logos & seals, About page, real address; 47% expect load ≤ 2 s (old stat). https://baymard.com/research-articles/ways-to-instill-trust
- Food delivery & takeout benchmark (2026-08-13): 8 apps/sites (Just Eat, KFC, Uber Eats, Domino's, DoorDash, McDonald's, Deliveroo, Burger King), 366 page designs, 390+ parameters; all "poor" to "mediocre", none "decent". Recs: route to past orders/reorder from homepage; dietary + category filters; describe customisation on item page; scope markers, breadcrumbs, back paths; clear delivery timing + tipping. https://baymard.com/research-articles/food-delivery-and-takeout-ux-benchmark-2026

### Dashboards / tables / charts (NN/g)
- Dashboards (2017-06-18): operational (time-sensitive, live) vs analytical; single screen; length & 2D position most accurate; color has no inherent order → not for magnitude; avoid 3D; pie/donut/treemap/radial gauges least accurate; sort bars. https://www.nngroup.com/articles/dashboards-preattentive/
- Data tables (2022-04-03): sticky header + frozen first column; zebra/borders/hover for row tracking; human-readable first column; important columns first; discoverable filters with active indicator; easy sort; column hide/reorder not only via drag; edit in place for narrow tables, non-modal side panel for wide; batch actions with checkboxes + Select All. https://www.nngroup.com/articles/data-tables/
- Chart choice (2022-01-30): bars for comparison (horizontal for long labels), paired bars, line for time, scatter for correlation; prefer series of bar charts over stacked bars; avoid pie, bubble, mosaic, waffle, Sankey, dendrogram, stacked area unless clear value. https://www.nngroup.com/articles/choosing-chart-types/
- Complex apps (2020-11-08): 8 guidelines — learning by doing; nudge efficient methods; flexible pathways; help track actions/notes; coordinate across tools (export); reduce clutter without reducing capability; ease primary↔secondary info (tooltips/panels); make important info salient by removing noise. https://www.nngroup.com/articles/complex-application-design/

### AI products
- Apple HIG Generative AI (new 2025-06-09; updated 2026-06-08 "Added guidance for letting people refine results and providing feedback during content generation, and updated guidance for choosing a model type"): keep people in control (dismiss, revert, retry); identify where AI is used; never imply human authorship; set expectations + curated suggestions; on-device vs server model privacy trade-off; ask permission for personal data; minimise hallucination impact, avoid AI where a hallucination could harm; confirm before irreversible actions (deleting, purchasing); Edit/Undo/Retry/Adjust near output and acknowledge corrections; coach people when blocked ("Unable to use that description"); design for latency — loading experience or background generation; specific progress copy ("Summarizing key themes from your notes" not "Processing…"); offer alternate versions; voluntary thumbs up/down feedback; non-AI fallback. JSON source: https://developer.apple.com/tutorials/data/design/human-interface-guidelines/generative-ai.json (page https://developer.apple.com/design/human-interface-guidelines/generative-ai)
- Microsoft HAX 18 guidelines (G1 Make clear what the system can do … G18 Notify users about changes), grouped: initially / during interaction / when wrong / over time. https://www.microsoft.com/en-us/haxtoolkit/library/ , https://www.microsoft.com/en-us/haxtoolkit/ai-guidelines/
- Shape of AI catalog: Wayfinders (example gallery, follow up, initial CTA, nudges, prompt details, randomize, suggestions, templates); Prompt actions (auto-fill, chained action, describe, expand, inline action, inpainting, madlibs, open input, regenerate, restructure, restyle, summary, synthesis, transform); Tuners (attachments, connectors, filters, model management, modes, parameters, preset styles, prompt enhancer, saved styles, voice and tone); Governors (action plan, branches, citations, controls, cost estimates, draft mode, memory, references, sample response, shared vision, stream of thought, variations, verification); Trust builders (caveat, consent, data ownership, disclosure, footprints, incognito mode, watermark); Identifiers (avatar, color, iconography, name, personality). https://www.shapeof.ai/
- Vercel AI SDK 5 generative UI: tools (Zod inputSchema + execute) → typed message parts `tool-${toolName}`; render by state `input-available` (loading), `output-available` (component with part.output), `output-error` (part.errorText). https://ai-sdk.dev/docs/ai-sdk-ui/generative-user-interfaces
- PAIR Guidebook (https://pair.withgoogle.com/guidebook/) is client-rendered; content not captured.

### Government / plain language / health
- GOV.UK Government Design Principles (updated 2025-04-02): 1 Start with user needs … 11 Minimise environmental impact. https://www.gov.uk/guidance/government-design-principles
- GOV.UK question pages: one thing per page; heading = legend/label; Back link at top; "Continue" button left-aligned; progress indicator optional ("Question 3 of 9"); ask only what you need; reuse answers; allow "I do not know"; mark optional with "(optional)", never asterisks. https://design-system.service.gov.uk/patterns/question-pages/
- GOV.UK clear language: plain English mandatory; 80% preferred clear English; specialists prefer it more; paragraphs ≤ 5 sentences; split sentences > 25 words; explain specialist terms on first use; active voice. https://guidance.publishing.service.gov.uk/writing-to-gov-uk-standards/writing-guidelines/clear-language/
- NHS service manual: reading age 9–11 (medical info: ensure 11–14-year-old can understand); sentences ≤ ~20 words; paragraphs ≤ ~3 sentences; plain term first then medical term "piles (haemorrhoids)"; active voice; neutral. https://service-manual.nhs.uk/content/how-we-write
- HIPAA (Wikipedia): PHI = info held by covered entity about health status, care, payment linkable to individual; covered entities (plans, clearinghouses, providers) + business associates; minimum necessary; Security Rule administrative/physical/technical safeguards. https://en.wikipedia.org/wiki/Health_Insurance_Portability_and_Accountability_Act (hhs.gov and ecfr.gov returned 403/bot wall to automated fetch).
- GDPR Art. 9: health data, genetic, biometric (for unique ID), sex life/orientation, racial/ethnic origin, political, religious, trade union = special categories. https://gdpr-info.eu/art-9-gdpr/
- Thailand PDPA: regulator site https://www.pdpc.or.th/ (สคส., Personal Data Protection Committee office) reachable but landing page only showed a cookie banner; PDPA specifics (B.E. 2562 / 2019, sensitive data incl. health needs explicit consent) NOT verified from a fetched source in this pass → marked (unverified) in reference.

### Gaming
- Xbox Accessibility Guidelines v3.2 published 2023-06-08 (doc updated 2026-08-18); each XAG: goal, overview, scoping questions, key areas, implementation guidelines, examples, player impact. https://learn.microsoft.com/en-us/xbox/accessibility/guidelines
- https://gameaccessibilityguidelines.com/ (200).

### Studying reference sites (tools)
- Chrome DevTools Animations panel (doc updated 2024-04-16): captures CSS transitions, CSS animations, Web Animations, View Transitions; **not** requestAnimationFrame; reload with panel open for load animations; scrub, slow down, replay; drag to change duration/delay/keyframe offsets; easing edited in Styles. https://developer.chrome.com/docs/devtools/css/animations
- CSS Overview panel: colors (by type, low-contrast text), font info by size/weight/line-height, unused declarations, media queries (doc 2021-10-21, "preview feature in Chrome 96"; current availability not confirmed). https://developer.chrome.com/docs/devtools/css-overview
- `document.getAnimations()` returns CSS Animations, CSS Transitions, Web Animations; Baseline widely available since Sept 2020; example halves playbackRate. https://developer.mozilla.org/en-US/docs/Web/API/Document/getAnimations
- `document.fonts` → FontFaceSet; iterate after `document.fonts.ready`; only fonts used/loaded appear. https://developer.mozilla.org/en-US/docs/Web/API/Document/fonts
- three.js sets `window.__THREE__ = REVISION` (verified in three@0.180.0 build/three.core.js line ~58767); GSAP pushes into `window.gsapVersions` (gsap@3.13.0 dist/gsap.js). Both from jsDelivr builds.

## 8. Facts sibling files should know
- Godly → Recent (recent.design) rebrand/redirect; UI Sources → ScreensDesign; Screenlane parked; Rive community → Rive Marketplace (/marketplace/).
- Award-winning sites 2024–2026 lean heavily on Nuxt/Astro + Lenis smooth scroll + GSAP; Barba/Swup for page transitions; Webflow common for luxury/real-estate builds; WebGPU now appearing in FOTY-level work (Food for Fish FOTY 2024, Bruno Simon portfolio FOTY 2025 with WebGPU signature).
- Apple HIG Generative AI updated 2026-06-08 (refine results + feedback during generation).
- NN/g skeleton screens article reviewed 2026-09-02; Baymard horizontal tabs article updated 2026-07-08; Baymard food-delivery benchmark 2026-08-13.

## 9. Full scraped catalog (76 live sites, verified 2026-10-10)

Award abbreviations: SOTD/SOTM/SOTY = Awwwards Site of the Day/Month/Year; Dev SOTY = Awwwards Developer Site of the Year; FOTM/FOTY = FWA of the Month/Year; FWA PCA = FWA People's Choice; CSSDA WOTD = Website of the Day. FWA dates are the timeline award dates (FOTY/PCA are dated mid-January, inferred to honour the previous year). "Techniques" come only from Awwwards tags, FWA case text, or HTML signatures; "(not assessed)" = no evidence collected.

| # | Site | URL | Award(s) | Category | Techniques (evidence) | Style tags | Stack signals in HTML | Palette (Awwwards) | HTTP |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Akaru | https://akaru.fr/ (→ https://www.akaru.fr/) | Awwwards SOTM 2024-04; SOTD Apr 1, 2024 | agency | page transitions, filters/effects, unusual navigation | colorful, warm off-white + ink | Nuxt | #F1EFEB #0E0E0E | 200 |
| 2 | Anime.js | https://animejs.com | Awwwards SOTM 2025-05; SOTD May 6, 2025 | dev tool / library site | scroll-driven demos, 3D, live animation as product proof | dark neutral, technical |  | #252423 #DAD5D0 | 200 |
| 3 | Bennett & Clive | https://bennettandclive.com | Awwwards SOTM 2024-03; SOTD Mar 12, 2024 | production agency | typography-led layout, photo & video | monochrome, minimal, editorial | Nuxt | #000000 #ffffff | 200 |
| 4 | Bruno's Portfolio | https://bruno-simon.com | Awwwards SOTM 2026-01; SOTD Jan 21, 2026; FWA FOTY 2026-01; FWA PCA 2026-01; FWA FOTM 2026-01 | portfolio / game | drivable 3D world (three.js), WebGPU renderer, multiplayer | toy-like 3D, playful | three.js, WebGPU |  | 200 |
| 5 | Cartier Watches & Wonders 2025 | https://cartier-waw-0225.dev.60fps.fr/ | Awwwards SOTM 2025-08; SOTD Aug 18, 2025 | luxury campaign | WebGL 3D, gesture interaction, scroll | luxury, cinematic |  |  | 200 |
| 6 | David Whyte Experience | https://davidwhyte.com/experience/ | Awwwards SOTM 2024-12; SOTD Dec 31, 2024 | culture / poetry | watercolour landscapes, scroll storytelling, gestures | painterly, soft grey | WordPress, Lenis | #E1E1E1 #000000 | 200 |
| 7 | Don't Board Me | https://dontboardme.com | Awwwards SOTY Users' Choice 2024; SOTD Mar 11, 2024 | service (pet care) | scroll storytelling, graphic illustration, custom 404 | bold red + sky blue, illustrative | Nuxt, Lenis, Lottie | #E33529 #AFD8FB | 200 |
| 8 | Dropbox Brand | https://brand.dropbox.com/ | Awwwards SOTM 2025-02; SOTD Feb 12, 2025; FWA FOTM 2025-02 | brand guidelines | interactive brand playground, kinetic type, animated illustration | colorful, brand blue | Webflow, Spline, Lottie | #0061FE #1A1918 | 200 |
| 9 | ERA Residence | https://www.era-residence.com/ | Awwwards SOTM 2026-08; SOTD Aug 31, 2026 | real estate | parallax, scroll storytelling, video, page transitions (Barba) | pastel, luxury | Webflow, GSAP, Lenis, Barba, Lottie | #B5CEDB #F8BBCB | 200 |
| 10 | Floema | https://www.floema.com/en (→ https://floema.com/en) | Awwwards SOTM 2026-05; SOTD May 13, 2026 | B2B product / catalogue | WebGL, 3D product, photographic storytelling | lime-yellow on charcoal, photographic | Nuxt | #E9E778 #241F21 | 200 |
| 11 | GQ & AP The Extraordinary Lab | https://www.gq.com/sponsored/story/the-extraordinary-lab | Awwwards SOTM 2026-03; SOTD Mar 26, 2026 | luxury editorial campaign | WebGL 3D (Blender assets), gesture interaction | luxury, dark | Nuxt, three.js, Lenis |  | 200 |
| 12 | Igloo Inc | https://www.igloo.inc/ | Awwwards SOTY 2024 + Dev SOTY 2024; Awwwards SOTM 2024-07; SOTD Jul 23, 2024; FWA FOTM 2024-08 | corporate (web3) | 3D scenes, infinite scroll, transitions | icy cool grey, tech |  | #b6bac5 #383e4e | 200 |
| 13 | Immersive Garden website | https://immersive-g.com/ | Awwwards SOTM 2025-01; SOTD Jan 7, 2025; FWA FOTM 2025-01 | agency | 3D, experimental gestures, project pages | dark monochrome | Nuxt, Lenis, Lottie | #000000 #c2c2c2 | 200 |
| 14 | Inkfish | https://inkfishnyc.com/ | Awwwards SOTM 2024-05; SOTD May 23, 2024 | production agency | fullscreen video, parallax, typography, transitions | black/white, cinematic | Next.js | #000000 #FFFFFF | 200 |
| 15 | Kriss.ai | https://kriss.ai/ | Awwwards SOTM 2024-10; SOTD Oct 24, 2024 | AI health startup | illustration, transitions, scroll storytelling, 3D | muted neutral on near-black | SvelteKit | #D1CACC #0F0F0F | 200 |
| 16 | Lama Lama | https://lamalama.com/ | Awwwards SOTM 2026-07; SOTD Jul 20, 2026 | agency | WebGL, GSAP, page transitions (Swup) | cream + ink, bold graphic | WordPress, Swup | #F9F4EB #1A1C1C | 200 |
| 17 | Lando Norris | https://landonorris.com/ | Awwwards SOTY 2025 + Users' Choice 2025; Awwwards SOTM 2025-11; SOTD Nov 17, 2025 | athlete promo | WebGL 3D, GSAP, gesture interaction | neon lime on near-black, sporty | Webflow, GSAP, Lenis | #D2FF00 #111112 | 200 |
| 18 | Lusion v3 | https://lusion.co/ | Awwwards SOTY 2023 + Dev SOTY 2023; SOTD Oct 2, 2023; FWA FOTY 2024-01; FWA FOTM 2023-10 | agency portfolio | real-time 3D, animation | electric blue + white, clean | Astro | #1a2ffb #f0f1fa | 200 |
| 19 | Mana Yerba Mate | https://en.manayerbamate.com/ | Awwwards E-commerce of the Year 2023; SOTD Mar 13, 2023 | e-commerce (Shopify) | 3D, illustration, custom 404 | warm yellow/orange, colorful | Shopify, Lottie | #FFD372 #F15B40 | 200 |
| 20 | Messenger | https://messenger.abeto.co | Awwwards Dev SOTY 2025; SOTD Nov 10, 2025; FWA FOTM 2025-11 | game / art | three.js tiny-planet world, WebSockets multiplayer | pastel teal/sage, toy-like |  | #81BFBC #C9D5C3 | 200 |
| 21 | MindMarket | https://mindmarket.com/ | Awwwards SOTM 2025-12; SOTD Dec 29, 2025 | research agency | illustration, scroll storytelling, GSAP, page transitions (Swup) | lime/yellow, flat colourful | Astro, Lenis, Swup | #8ED462 #F5E211 | 200 |
| 22 | Montfort | https://mont-fort.com/ | Awwwards SOTM 2025-06; SOTD Jun 23, 2025 | corporate (trading) | 3D, scroll, gestures | corporate blue + white, clean | Astro | #29648e #f4f6f8 | 200 |
| 23 | Noomo Agency | https://noomoagency.com | Awwwards SOTY Users' Choice 2023; SOTD Sep 21, 2023 | agency | 3D scroll storytelling | pale blue, immersive | Nuxt, three.js, GSAP, WebGPU | #DEE7F1 | 200 |
| 24 | Opal Tadpole | https://www.opalcamera.com/opal-tadpole (→ https://op.al/) | Awwwards E-commerce of the Year 2024; SOTD Jan 11, 2024 | e-commerce product | 3D product, photography, microinteractions, single page | yellow + white, product-photo | Next.js | #FFDB01 #ffffff | 200 |
| 25 | Oryzo AI | https://oryzo.ai | Awwwards SOTM 2026-04; SOTD Apr 13, 2026; FWA FOTM 2026-04 | brand / product story | WebGL (three.js), cinematic product story, filters/effects | dark brown + orange, cinematic | Astro | #100904 #FF8539 | 200 |
| 26 | Ponpon Mania | https://ponpon-mania.com/ | Awwwards SOTM 2025-10; SOTD Oct 22, 2025 | interactive comic | WebGL, parallax, unusual navigation, illustration | periwinkle + pink, playful | Nuxt | #7E7EFF #F894C0 | 200 |
| 27 | Scout Motors | https://www.scoutmotors.com/ | Awwwards E-commerce of the Year 2025; SOTD Jan 16, 2025 | automotive product / commerce | storytelling, photo & video, interaction | orange-red + warm grey, rugged | Astro, Lenis | #FF5432 #D7D4D3 | 200 |
| 28 | Siena Film Foundation | https://siena.film | Awwwards SOTM 2025-03; SOTD Mar 18, 2025 | film production | infinite scroll, transitions, filters/effects, copy design | black on cream, editorial | Webflow | #000000 #FAF7EF | 200 |
| 29 | Slosh Seltzer | https://sloshseltzer.com/ | Awwwards SOTM 2024-06; SOTD Jun 5, 2024 | beverage brand concept | maximalist graphics, transitions, microinteractions | pink, maximalist |  | #ffc1ff | 200 |
| 30 | Son Daven | https://sondaven.com/en | Awwwards SOTM 2026-06; SOTD Jun 5, 2026 | hospitality | WebGL, scroll storytelling, GSAP, page transitions (Barba) | earthy brown/beige, luxury | Webflow, GSAP, Lenis, Barba | #A89474 #2C2824 | 200 |
| 31 | Terminal Industries | https://terminal-industries.com | Awwwards SOTM 2025-09; SOTD Sep 3, 2025 | B2B SaaS (logistics) | CSS animation, scroll storytelling | industrial tech | Nuxt, Lenis |  | 200 |
| 32 | The Renaissance Edition | https://www.shopify.com/editions/winter2026 | Awwwards SOTM 2026-02; SOTD Feb 9, 2026; FWA FOTM 2026-03 | product release notes (Shopify Editions) | generative paintings + 3D (Blender), parallax, transitions | parchment + olive-black, painterly | Shopify, Lenis, Spline | #F7F7EE #292919 | 200 |
| 33 | The Line Studio | https://thelinestudio.com/ | Awwwards SOTM 2024-11; SOTD Nov 5, 2024; FWA FOTM 2024-12 | animation studio | 2D/3D animation reel, typography, graphic design | red-orange + off-white | Nuxt, Lenis | #FF391E #F8F8F8 | 200 |
| 34 | Tracing Art | https://www.getty.edu/tracingart/ | Awwwards SOTM 2025-07; SOTD Jul 22, 2025 | museum / data story | data visualization, scroll storytelling, content architecture | white, clean, museum | Nuxt, Lenis | #FFFFFF #DAE2E8 | 200 |
| 35 | Watson | https://watson.la/ | Awwwards SOTM 2024-09; SOTD Sep 12, 2024 | agency | content architecture, project pages | black/white | three.js | #000000 #FFFFFF | 200 |
| 36 | Why Zero | https://why.zero.university/ | Awwwards SOTM 2026-09; SOTD Sep 7, 2026; FWA FOTM 2026-08 | education | three.js, GSAP, shaders, sound, scroll story | white + green |  | #ffffff #01C654 | 200 |
| 37 | Zentry | https://zentry.com/ | Awwwards SOTM 2024-08; SOTD Aug 28, 2024 | gaming / platform | scroll storytelling, sound, bold UI | black, bold colour | Nuxt, three.js, GSAP, Lenis, Spline | #000000 | 200 |
| 38 | Awards Racing | https://awards.racing | FWA FOTM 2026-10; CSSDA WOTD 2026 | browser game | three.js + Bullet physics, single draw call, object pooling, beat-synced characters | arcade | Nuxt, three.js, GSAP |  | 200 |
| 39 | Santioni Spirits: The Notturno Experience | https://santionispirits.com/ | FWA FOTM 2026-09; Awwwards SOTD 2026-10 | drinks brand | comic-book illustrated journey, WebGL, sound | comic, illustrated | Lottie |  | 200 |
| 40 | Lacoste Ace Breaker | https://members-play.lacoste.com/ace-breaker-rg | FWA FOTM 2026-07 | branded game | brick-breaker game with prizes | sporty |  |  | 200 |
| 41 | IVRESS SPIN A TALE | https://brand.ivress.co.jp/ | FWA FOTM 2026-06 | brand story (JP) | animation-led storytelling | (not assessed) | Astro |  | 200 |
| 42 | Shader Development Studio | https://www.shader.se | FWA FOTM 2026-05 | studio | interactive 3D | experimental | Next.js |  | 200 |
| 43 | Explore Primland | https://explore.ownprimland.com/ | FWA FOTM 2026-02 | travel / hospitality | immersive digital tour of a resort | nature, immersive | Nuxt |  | 200 |
| 44 | The Monolith Project | https://themonolithproject.net/ | FWA FOTM 2025-12 | experiment | touch-driven sci-fi scene | sci-fi |  |  | 200 |
| 45 | Gen-02 SMSY Portfolio | http://samsy.ninja (→ https://samsy.ninja/) | FWA FOTM 2025-10 | portfolio | explorable 3D world, WebGPU | sci-fi | three.js, WebGPU |  | 200 |
| 46 | Welcome to Berk | https://powster.com/case-study/welcome-to-berk/ | FWA FOTM 2025-09 | film promo (case study) | WebGL 3D island, real-time weather from user location/time | cinematic |  |  | 200 |
| 47 | Yamê — The Molazone | https://mola-zone.com/ | FWA FOTM 2025-08 | music promo | explorable universe + mini-game | (not assessed) | Nuxt |  | 200 |
| 48 | Arina's Story | https://arinastory.com | FWA FOTM 2025-07 | fundraising / documentary | Unreal Engine via cloud Pixel Streaming, cinematic fallback when servers busy | documentary |  |  | 200 |
| 49 | Jordan's Portofolio | https://jordan-delcros.com/ | FWA FOTM 2025-06 | portfolio | WebGL, animation | (not assessed) |  |  | 200 |
| 50 | Elimar | https://elimar.lmigroupintl.com/ | FWA FOTM 2025-04 | art / education | immersive story of a painting | (not assessed) | Next.js, Lottie |  | 200 |
| 51 | Lacoste Members Experience | https://membersexperience-create.lacoste.com/ | FWA FOTM 2025-03 | fashion co-creation | members design products, winning designs produced | (not assessed) | WordPress |  | 200 |
| 52 | Food for Fish | https://foodforfish.org/ | FWA FOTY 2025-01; FWA FOTM 2024-06 | experiment | WebGPU | experimental | Next.js, WebGPU |  | 200 |
| 53 | Hatom | https://www.hatom.com/ | FWA PCA 2025-01; FWA FOTM 2024-11 | DeFi protocol | 3D creature-transformation story | dark, cinematic | Nuxt, Lenis |  | 200 |
| 54 | Following Wildfire | https://followingwildfire.com/ | FWA FOTM 2024-10 | social cause / AI | AI-powered early wildfire detection campaign, animation | (not assessed) | Next.js |  | 200 |
| 55 | Kaizen | https://kaizen.makemepulse.com | FWA FOTM 2024-07 | studio experiment | poetic immersive journey | (not assessed) |  |  | 200 |
| 56 | Equinox | https://equinox.space | FWA FOTM 2024-05 | narrative game | first-person story, touch control mode for mobile, original music | space, cinematic |  |  | 200 |
| 57 | BOUCHERON - Quatre 20th Anniversary | https://quatre.merci-michel.com/ | FWA FOTM 2024-04 | luxury campaign | 10+ chained mini-games | luxury, playful |  |  | 200 |
| 58 | Casa di Solare | https://casadisolare.com | FWA FOTM 2024-03 | type foundry microsite | typeface showcase, sun motif | typographic | Nuxt |  | 200 |
| 59 | Active Theory V6 | https://activetheory.net/ | FWA FOTM 2024-02 | agency | new rendering, AI chat, multiplayer | dark, immersive |  |  | 200 |
| 60 | Loewe x Howl's Moving Castle | https://howls.loewe.com/ | FWA PCA 2024-01; FWA FOTM 2023-03 | fashion x film | mobile-first interactive story | Ghibli illustrative |  |  | 200 |
| 61 | Sculpting Harmony | https://gehry.getty.edu/ | FWA FOTM 2023-12 | museum exhibition | 3D models, 150+ sketches/models, scroll | architectural, museum | Nuxt, three.js, GSAP, Lenis |  | 200 |
| 62 | Haunted by Nostalgia | https://haunted.thedigitalpanda.com | FWA FOTM 2023-11 | game | WebGL 3D trivia, sound | spooky, 3D |  |  | 200 |
| 63 | Little Red Riding Hood's Quest | https://ai-quest.lusion.co/ | FWA FOTM 2023-08 | AI story game | AI-driven storytelling challenges | storybook | Lottie |  | 200 |
| 64 | Aten7 | https://www.aten7.com/ (→ https://www.aten7.com/intro) | FWA FOTM 2023-07 | experimental brand world | immersive archive exploration | (not assessed) | Nuxt |  | 200 |
| 65 | The Search for Work Happiness | https://www.findworkhappiness.com | FWA FOTM 2023-06 | book promo | drag-to-paint illustration, masking chapter transitions, layered audio | Wimmelbilderbuch illustration | Nuxt |  | 200 |
| 66 | Locomotive® | https://locomotive.ca (→ https://locomotive.ca/en) | FWA FOTM 2023-05 | agency | smooth scroll (Locomotive Scroll), case studies | (not assessed) | Locomotive Scroll |  | 200 |
| 67 | Curious & Company | https://curious.co | FWA FOTM 2023-04 | agency | 3D, playful usability | mystic, 3D | SvelteKit |  | 200 |
| 68 | KPR | https://kprverse.com/ | Awwwards SOTY 2022 (hall of fame 2022); FWA FOTM 2023-02 | NFT / web3 world | illustration, scroll storytelling, experimental | colourful illustrated | Nuxt, three.js, GSAP, Spline |  | 200 |
| 69 | Getty Villa: Persepolis Reimagined | http://www.getty.edu/persepolis (→ https://persepolis.getty.edu/) | Awwwards Dev SOTY 2022; FWA FOTY 2023-01; FWA PCA 2023-01 | museum | WebGL 3D reconstruction, 360, data viz, GSAP | archaeological, warm |  |  | 200 |
| 70 | Bulles | https://experience.projetbulles.com/ | CSSDA WOTD 2026 | education / social cause | creative worlds of autistic students | (not assessed) | Nuxt |  | 200 |
| 71 | 1367 Studio | https://www.1367studio.com/ | CSSDA WOTD 2026 | agency | page transitions (Barba) | (not assessed) | Astro, Barba |  | 200 |
| 72 | A24 (fan concept) | https://a24.raviklaassens.com/ | CSSDA WOTD 2026 | film (concept) | page transitions (Barba) | (not assessed) | Astro, Barba |  | 200 |
| 73 | EddyOS — Eddy Naboulet | https://eddy-naboulet.dev/ | CSSDA WOTD 2026 | portfolio | OS metaphor, WebGL | (not assessed) | Astro, three.js, GSAP, Lenis, Lottie |  | 200 |
| 74 | Sobha Privy Collection | https://sobha-privy-collection.com/ | CSSDA WOTD 2026; Awwwards SOTD 2026-09 | real estate | parallax, WebGL (three.js), 3D | luxury | Barba |  | 200 |
| 75 | Agrumea Farm | https://www.agrumeafarm.it/en | CSSDA WOTD 2026 | e-commerce food | smooth scroll | (not assessed) | Nuxt, Lenis |  | 200 |
| 76 | Wonder Vision | https://www.wonder-vision.com/ | CSSDA WOTD 2026 | CGI studio | CGI/VFX reel | (not assessed) | WordPress |  | 200 |

### Dropped (dead or blocked at verification)

| Site | URL | Award(s) | HTTP | Why dropped |
|---|---|---|---|---|
| Navigate | https://nvg8.io/ | Awwwards SOTM 2025-04; SOTD Apr 16, 2025; FWA FOTM 2025-05 | 525 | Cloudflare 525 (origin SSL handshake failed) on HEAD and GET |
| The Maison of All Victories | https://the-maison-of-all-victories.lvmh.com/en | FWA FOTM 2024-09 | 000 | no HTTP response (campaign site offline) |
| The Fabulous Cartier Journey | https://www.cartier.com/thefabulouscartierjourney | FWA FOTM 2024-01 | 403 | "Access Denied" to curl (bot wall); not verifiable, so excluded |
| Önnu Jónu Son | https://onnujonuson.com/clip/almost-over-you | FWA FOTM 2023-09 | 000 | no HTTP response (campaign site offline) |

Notes on live entries: Opal Tadpole product URL now redirects to the op.al homepage (product page retired). Cartier Watches & Wonders 2025 is linked by Awwwards to a staging host (60fps.fr dev domain) that still resolved. Welcome to Berk URL is the Powster case-study page (campaign site welcometoberk.com not tested). Zentry homepage title now reads "Human-Agentic OS…" (product repositioned since its 2024 award).

## 10. Live verification of the study snippet (Browser pane, 2026-10-10)

- Ran the inspiration.md console snippet on https://landonorris.com/ : fonts Brier 700 + Mona Sans Variable 200 900; palette top-6 rgb(40,44,32) 256 hits, rgb(244,244,237) 253, rgb(17,17,18) 91, rgb(210,255,0) 88, rgb(83,84,80) 61, rgb(180,184,165) 41 — matches Awwwards palette #D2FF00 / #111112; `window.__THREE__` = "174", `window.gsapVersions` = ["3.13.0"], `window.lenisVersion` = "1.1.20", `<html class~=lenis>` true; `document.getAnimations().length` = 0 (motion is rAF-driven). First-match `h3` was an 8 px element → ramp needs targeted selectors.
- Lenis sets `window.lenisVersion = version` and adds class `lenis` (+ `lenis-smooth`, `lenis-scrolling`, `lenis-stopped`) — verified in lenis@1.3.4 dist/lenis.mjs.
