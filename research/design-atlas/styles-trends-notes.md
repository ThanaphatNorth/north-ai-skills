# Raw notes — visual styles catalog & 2025–2026 trends

Provenance record for `skills/design-atlas/references/styles-catalog.md`. Collected 2026-10-10.
Method: WebSearch + WebFetch on primary sources where reachable; reference-site URLs checked with `curl -sL` (HTTP status + `<title>`) on 2026-10-10; browser support from MDN browser-compat-data (`main` branch, fetched 2026-10-10).
Note: the session's WebSearch budget ran out partway; the remaining checks used direct fetches of primary URLs only.

## Brand personality frameworks

- Aaker, J. (1997) "Dimensions of Brand Personality", *Journal of Marketing Research* 34(3): 347–356. Full text: https://gwern.net/doc/economics/1997-aaker.pdf (read via pdftotext)
  - 5 dimensions, 15 facets: Sincerity (down-to-earth, honest, wholesome, cheerful) · Excitement (daring, spirited, imaginative, up-to-date) · Competence (reliable, intelligent, successful) · Sophistication (upper class, charming) · Ruggedness (outdoorsy, tough).
  - "Sincerity and Excitement each had four facets, Competence had three, and Sophistication and Ruggedness each had two."
  - Exemplar brands in the paper: Hallmark (Sincerity), MTV (Excitement), Wall Street Journal (Competence), Guess jeans (Sophistication), Nike tennis shoes (Ruggedness).
  - Variance explained: Sincerity 26.5%, Excitement 25.1%, Competence 17.5%, Sophistication 11.9%, Ruggedness 8.8%.
  - Cross-cultural replication is mixed (Brazil study found credibility/joy/audacity/sophistication/sensitivity): https://www.scielo.br/j/bar/a/6s5ykMMb8HjfXym7SfjgHsr/?lang=en (search result only).
- 12 archetypes, Mark & Pearson, *The Hero and the Outlaw* (2001), from Jung: Innocent, Everyman (Regular Guy/Gal), Hero, Outlaw, Explorer, Creator, Ruler, Magician, Lover, Caregiver, Jester, Sage. Grouped by independence / belonging / stability / mastery. Example brands in practitioner guides (not the book): Coca-Cola (Innocent), IKEA (Everyman), Nike (Hero), Harley-Davidson (Outlaw), Jeep (Explorer), Lego (Creator), Rolex (Ruler), Disney (Magician). Source: search results incl. https://www.moonb.io/blog/brand-archetypes, https://uxdesign.cc/brand-archetypes-c09771774c1a (secondary).

## Apple Liquid Glass (iOS/iPadOS/macOS Tahoe/watchOS/tvOS 26)

- Apple Newsroom, 2025-06-09, "Apple introduces a delightful and elegant new software design": https://www.apple.com/newsroom/2025/06/apple-introduces-a-delightful-and-elegant-new-software-design/
  - Translucent material that reflects and refracts surroundings; specular highlights as it moves; color adapts to content and light/dark.
  - Used for small controls (buttons, switches, sliders, media controls) and larger navigation (tab bars, sidebars); Lock Screen, Home Screen, notifications, Control Center.
  - Controls/toolbars/navigation redesigned to be concentric with rounded hardware and window corners.
  - Aim: "bring greater focus to content"; controls recede on scroll, expand when needed. Alan Dye: "our broadest software design update ever."
- HIG Materials page exists (https://developer.apple.com/design/human-interface-guidelines/materials, HTTP 200) but renders client-side; body text not retrievable by fetch → regular/clear variants and dimming-layer guidance NOT verified from Apple text in this session.
- SwiftUI API `glassEffect(_:in:)` exists (doc page title confirmed): https://developer.apple.com/documentation/swiftui/view/glasseffect(_:in:)
- NN/g, Raluca Budiu, 2025-10-10, "Liquid Glass Is Cracked, and Usability Suffers in iOS 26": https://www.nngroup.com/articles/liquid-glass/
  - Problems: legibility/contrast ("text on top of text"), floating controls competing with content, distracting animation ("Motion for motion's sake is not usability."), crowded tap targets, unpredictability/weaker discoverability (controls appear/vanish, search moved, back labels removed). "Apple is prioritizing spectacle over usability".
- Infinum beta test measured contrast as low as 1.5:1 vs 4.5:1 requirement: https://infinum.com/blog/apples-ios-26-liquid-glass-sleek-shiny-and-questionably-accessible/ (via search excerpt; page HTTP 200).
- iOS 26.1 (Oct–Nov 2025): Settings > Display & Brightness > Liquid Glass → "Clear" vs "Tinted" (more opaque, higher contrast; applies to third-party apps too). macOS 26.1: System Settings > Appearance. https://www.tomsguide.com/phones/iphones/ios-26-1-lets-you-adjust-liquid-glass-transparency-on-your-iphone-heres-how-to-do-it ; 9to5Mac 2025-10-20 (search result).
- WWDC 2026 (2026-06-08), TechCrunch "Apple is tweaking its controversial Liquid Glass design": https://techcrunch.com/2026/06/08/apple-is-tweaking-its-controversial-liquid-glass-design/
  - Apple: "updating the foundations of how Liquid Glass is built to ensure exceptional readability"; diffuses "complex content" behind panels; new slider "anywhere from ultra clear to fully tinted"; redesigned app icons; customization works in third-party apps.
  - Status of final iOS 27 public release details not verified (coverage is from June betas).
- Web Designer Depot (2026-02-16, opinion) reported an iOS 26.2 "Opaque Mode", Alan Dye leaving for Meta late 2025, and a rumored "Solid Design" direction — unsourced/unconfirmed; NOT used in the reference file. https://webdesignerdepot.com/how-liquid-design-broke-the-iphone-and-forced-apples-great-reset/

### Liquid Glass on the web
- LogRocket, 2025-12-08, "How to create Liquid Glass effects with CSS and SVG": https://blog.logrocket.com/how-create-liquid-glass-effects-css-and-svg/
  - Pipeline: feGaussianBlur → feImage displacement map → feDisplacementMap (scale ~55) → feColorMatrix saturate → specular rim via feImage + feComposite.
  - `backdrop-filter: url(#glass-filter)` works in Chromium only; Safari and Firefox restrict backdrop-filter to built-in functions → need fallback.
  - Perf: GPU/compositing cost; limit to a few floating elements (toolbars, modals, nav bars, primary CTAs). Maps are size-specific.
  - A11y: use sparingly, darker/uniform base helps contrast more than extra blur; keep real `<button>` semantics.
- ekino (Medium): backdrop-filter has no refraction; feDisplacementMap approximates it in Chromium; elements can't refract beyond their own box. https://medium.com/ekino-france/liquid-glass-in-css-and-svg-839985fcb88d (search excerpt).
- Specular edge via inset box-shadow stack, e.g. `inset 0 1.5px 0 rgba(255,255,255,.85)` (search excerpt, dev.to).

### Browser support (MDN BCD, main, fetched 2026-10-10)
- `backdrop-filter`: Chrome 76, Edge 79 (17 prefixed), Firefox 103, Safari 18 unprefixed (9 with `-webkit-`).
- `@media (prefers-reduced-transparency)`: Chrome 118; Firefox 113 behind flag; Safari: not supported. MDN marks "Limited availability", experimental.
- `prefers-contrast`: Chrome 96, Firefox 101, Safari 14.1. `prefers-reduced-motion`: Chrome 74, Firefox 63, Safari 10.1. `forced-colors`: Chrome 89, Firefox 89, Safari 16.
- `animation-timeline` (scroll-driven animations): Chrome 115, Safari 26, Firefox preview only.
- `initial-letter`: Chrome 110, Safari 9 (`-webkit-`), Firefox no.

## Fluent (Microsoft) acrylic — model for responsible translucency
- https://learn.microsoft.com/en-us/windows/apps/design/style/acrylic (ms.date 2026-10-02)
  - Recipe layers: background, blur, exclusion blend, color/tint overlay, noise.
  - Use background acrylic for transient surfaces (context menus, flyouts, light-dismiss panes); in-app acrylic for supporting UI that overlaps content. Opaque background for vertical panes that section content.
  - Don'ts: desktop acrylic on large background surfaces; multiple acrylic panes side by side (visible seam); accent-colored text on acrylic (likely fails contrast at 14px); avoid hyperlinks over acrylic.
  - Falls back to solid color when Transparency effects off, Battery Saver, low-end hardware, High Contrast. "Rendering acrylic surfaces is GPU-intensive".
- Fluent 2 material page: https://fluent2.microsoft.design/material (HTTP 200).

## Glassmorphism
- NN/g, Megan Brown, 2024-06-07, "Glassmorphism: Definition and Best Practices": https://www.nngroup.com/articles/glassmorphism/
  - "visual-design style that utilizes different levels of translucency"; more background blur is better for busy backgrounds (compares 0/25/100px at 30% opacity); ensure text/graphics meet contrast; simple/single-color backgrounds where controllable; low-opacity stroke suggests thickness; "best when utilized sparingly"; give users control over contrast/transparency where feasible.
- Practitioner numbers (secondary, conflicting): 2–3 glass elements per screen; white fill 10–30% opacity vs. others saying keep 85–90% opacity for stability. Windows Aero hurt low-end performance (LogRocket "What is glassmorphism").

## Neumorphism / claymorphism / skeuomorphism
- Wikipedia "Neumorphism": https://en.wikipedia.org/wiki/Neumorphism — term coined by Jason Kelly 2019; concepts trace to Oleksandr (Alexander) Plyuto's Dribbble banking mockup; soft low-contrast look; criticized for poor accessibility/low contrast; adoption fell by 2021; glassmorphism replaced it.
- Accessibility critique roundup (search): gray-on-gray body text below 4.5:1; one commercial blog estimates neumorphic edges ~1.4:1 vs 3:1 non-text requirement (unverified measurement); states (pressed/disabled/default) indistinguishable; shadow-only focus rings invisible. Sources: https://uxdesign.cc/neumorphism-visual-accessibility-and-empathy-d1c5ed2a1f03 , https://builtin.com/design-ux/neumorphism-accessibility , https://www.setproduct.com/blog/neumorphism-design-guide
- Figma's 2026 trends list still includes neumorphism (see Trends).
- Claymorphism: Michał Malewicz / Hype4 (now SquarePlanet) "Claymorphism in User Interfaces": https://hype4.academy/articles/design/claymorphism-in-user-interfaces
  - "fluffy 3d", inflated neumorphism; one larger outer shadow (often offset on X) + two inner shadows (top-left lighter, bottom-right darker); corners rounded "usually beyond 50%"; fits playful/friendly, dark mode if shape not pure black, VR/AR; poor fit for utilitarian/serious (reads child-like); author says hard to do fully in CSS.
  - 2026 guide: claymorphism settled into niches (onboarding, kids' apps) (setproduct, secondary).
- Skeuomorphism comeback: Wikipedia Corporate Memphis cites Fast Company 2022 that companies returned to 3D-like skeuomorphism.

## Material 3 Expressive
- Google Design, "Expressive Design: Google's UX Research": https://design.google/library/expressive-material-design-google-research
  - 46 studies, hundreds of designs, 18,000+ participants; eye tracking, surveys, focus groups, experiments, usability tests.
  - Preference up to 87% among 18–24; key UI elements spotted up to 4× faster (Send button case); 45+ users found key elements about as fast as younger users across 10 apps; +32% subculture perception, +34% modernity, +30% rebelliousness.
  - Tactics: color, shape, size, containment, motion.
  - Caveats: "not a one-size-fits-all solution" (banking may not suit); breaking patterns (scattered album art instead of list) and removing labels hurt usability; a strong minority preferred calmer versions; "No amount of emotion can compensate for a lack of clarity."
- Launch: leaked early May 2025, official at Google I/O May 2025 (press coverage via search).
- M3 Expressive codelab (search excerpt): "new set of 35 shapes ... with built-in shape morph motion"; "Motion physics ... powered by tokens". https://codelabs.developers.google.com/codelabs/mdc-102-objc (as listed in results).
- Third-party Flutter package lists expressive spatial spring stiffness 380 / damping 0.73 — NOT verified against Google tokens; not used.
- m3.material.io pages render client-side; blog body not retrievable.

## Trend reports 2025–2026
- Figma, "Top Web Design Trends for 2026": https://www.figma.com/resource-library/web-design-trends/ — 13 trends: 3D & immersive; experimental navigation (radial menus, hidden drawers, maps, nonlinear); vibrant palettes (saturated, neon gradients, "dopamine design", Y2K nostalgia); bold typography (oversized, kinetic, variable fonts); dark mode as standard; motion design; gamified design; neumorphism; retrofuturism (neon, chrome, pixel art, sci-fi gradients); maximalism; collage (stickers, torn textures, cutouts, hand-drawn fonts); neo-brutalism ("anti-design"); sustainable web design. AI trends: chatbots/agentic, voice, progressive lead nurturing. No date shown.
- Adobe Express, 2025-12-12, "Design trends for 2026": https://www.adobe.com/express/learn/blog/design-trends-2026 — all senses to the max (tactile/squishy, sound, motion); exaggerated playful letters; immersive high-energy style; surreal/absurdist imagery; organic & imperfect (letterpress, sand/bark textures); freeform storytelling layouts (zine-like); warm personal style; local/cultural flavor; collage & layered; maximalist chaotic layouts. Adobe Creative Trends 2026 also frames pullback from slick hi-tech toward "organic, analog, realistic, human-centered".
- Canva Design Trends Report 2026 (3rd annual), via Mediaweek 2025-12-16: https://www.mediaweek.com.au/why-designs-next-flex-is-being-imperfect — theme "imperfect by design". Search-growth figures (Canva platform data): Reality warp (liminal/uncanny) +220%; Prompt playground (lo-fi) +527%; Explorecore (zine/Substack layouts) +85%; Texture check +30%; Notes app chic (DIY/collage) +90%; The opt-out era (clean layouts, serif fonts, simple branding) +54%; Drama club +27%; Zinegeist (brutalist type posters, Mexico) +77%.
- Creative Bloq, Tom May, 2025-12-23, "Texture, warmth and tactile rebellion: the big graphic design trends for 2026": https://www.creativebloq.com/design/graphic-design/texture-warmth-and-tactile-rebellion-the-big-graphic-design-trends-for-2026
  - 01 Anti-AI Crafting (Graham Sykes, Landor: "human-driven craft is coming sharply back into focus as the antidote to AI's hyper-slick visual language"); 02 AI gets crafty too (woodcut, stone carving, gothic type via gen tools — Wolff Olins); 03 Emotional colour (brighter colours, earthy calm; Pantone Cloud Dancer); 04 Multisensory identities (motion-driven, gradients, 3D, blurred type); 05 Return of brand characters (BUCK: mascots to give agentic AI a face; Notion AI character); 06 Type as design (Spotify Wrapped, Whitney Museum, Oatly); 07 Layered storytelling; 08 More from minimalism (bold minimalism persists, esp. beauty).
  - FutureBrand: "In 2025, we gave AI a visual identity with bold 3D forms and unapologetically digital aesthetics" → 2026 shift to human side; OpenAI ChatGPT campaign shot on 35mm film. Apple TV ident built with real hand-blown glass, shot in camera.
- KOTA, "Branding inspiration: design trends for 2026": https://kota.co.uk/blog/branding-inspiration-brand-design-trends-for-2026 — tactile/imperfect/"made by someone"; hyper-local folk & heritage; brands that move; modern gothic; colour/nostalgia; controlled chaos (anti-design, broken grids, zine); surveillance/CCTV aesthetic; AI as co-pilot; purpose/sustainability. Advice: keep precision where clarity matters (data viz, product UI, navigation, legal/regulated).
- Webflow, Leah Retta & Jose Ocando, 2025-12-23, "8 web design trends to watch in 2026" (webflow.com/blog/web-design-trends-2026 — direct fetch failed with header overflow; summary via https://www.plushcap.com/content/webflow/blog/webflow-8-web-design-trends-to-watch-in-2026): proprietary visual effects vs homogeneity; art merged with advanced UI (human craft); minimalist copy; TL;DR experiences; dynamic text treatments; full color systems instead of one accent (2 more not visible).
- Pantone Color of the Year 2026: Cloud Dancer, PANTONE 11-4201, "a lofty white neutral", announced 2025-12-04 (NBC/WDEF coverage via search). 2025: Mocha Mousse; 2024: Peach Fuzz.
- Awwwards Site of the Year: Igloo Inc (igloo.inc) shows "Site Of The Year 2024" in an Awwwards collection; case study https://www.awwwards.com/igloo-inc-case-study.html (landing page commissioned via Bureaux). 2025: Awwwards listing pages show SOTY 2025 badges on "Lando Norris" by OFF+BRAND. (landonorris.com) and "Messenger" by abeto (messenger.abeto.co); which is the overall winner was not confirmed.
- Linear-style: LogRocket, Daniel Schwarz, 2025-06-07, "Linear design: The SaaS design trend that's boring and bettering UI": https://blog.logrocket.com/ux-design/linear-design — dark mode, bold type, complex gradients, glassmorphism, monochrome + high contrast, linear one-dimensional scroll; 2025: Linear "significantly cut back on the amount of color" → black/white; Raycast dropped 2024 gradient, kept red, added noisy abstract visuals; GitHub 2025 leaned too much on glass; oversaturation makes copies "monotonous". Daryl Ginn coined "the Linear effect" (via search).
  - Verified on linear.app HTML (2026-10-10): background `#08090A`, font stack includes "Inter".
- Bento: origin disputed (Apple keynote/product videos vs Windows Phone Metro tiles); durable as layout convention; practitioner sweet spot 6–9 tiles; CSS Grid makes it trivial. https://www.freecodecamp.org/news/bento-grids-in-web-design/ , https://webdesignerdepot.com/what-is-the-bento-ui-trend-and-how-can-you-get-started (search).
- Brutalism: NN/g, Kate Moran, 2017-11-05, "Brutalism and Antidesign": https://www.nngroup.com/articles/brutalism-antidesign/ — brutalism "intentionally attempts to look raw, haphazard, or unadorned"; antidesign = "intentionally creating ugly, disorienting, or complex interfaces"; keep brutalism to visual layer, keep hierarchy/navigation; antidesign only for designer/artist audiences or entertainment where discoverability > efficiency; otherwise "an antidesign UI will backfire." Cites Adult Swim as usable brutalism.
- Neo-brutalism traits (practitioner): thick black borders, hard offset shadows (no blur), bright solid colors, large plain type; bad fit for finance/healthcare/banking (svgator).
  - Verified on gumroad.com HTML (2026-10-10): `shadow-[4px_4px_0_0_#000000]` ×102, `border-black` ×39, `#FF90E8` pink.
- Corporate Memphis: Wikipedia https://en.wikipedia.org/wiki/Corporate_Memphis — Facebook 2017 "Alegria" by BUCK; term by Mike Merrill; flat elements, solid colors, long elastic arms, small heads, bright purple/blue skin; criticism: "lazy" (Jack Hurley), small palette (David Rudnick); by 2022 Fast Company: return to 3D-like skeuomorphism; 2023 Creative Bloq: "uninspired design", oversaturation, "a form of parody". Protocol 2021 (via Slashdot): "safe and antiseptic"; illustration awarded to lowest bidder. AIGA Eye on Design counterpoint: flat art has a long history. https://eyeondesign.aiga.org/what-the-think-pieces-about-corporate-memphis-tell-us-about-the-state-of-illustration/
- Y2K: Webflow "Y2K aesthetic for web design projects": https://webflow.com/blog/y2k-aesthetic (HTTP 200; content via search excerpt) — glossy UI, chunky type, bubbles, metallics, neon glows; electric blue/teal, neon green, hot pink, silver. Practitioner recipe: gradient clipped to text + hard white band near 50% = chrome; starbursts via clip-path; pixel webfont over bitmap. Stills 2026 report: chrome textures, spiked type (search).
- Synthwave recipes: perspective floor `rotateX(~53–60deg)` + gradient grid lines; striped sun via mask (freefrontend/speckyboy via search). daisyUI trend page https://trends.daisyui.com/trend/synthwave-outrun/ ; daisyUI themes (verified list): synthwave, cyberpunk, retro, valentine, aqua, lofi, pastel, luxury, dracula, nord, coffee, wireframe, cmyk, caramellatte, silk, abyss, etc. https://daisyui.com/docs/themes/
- Dopamine design: daisyUI trend https://trends.daisyui.com/trend/dopamine-design/ — "saturated color clashes, bold patterns, playful shapes, cheerful icons, oversized type, energetic layering"; a popular label, not a theory.
- Kinetic type: Awwwards element collection https://www.awwwards.com/inspiration/type-transformation-kinetic-type-animation ; Apple product pages use word-by-word scroll reveals (studiomeyer blog, secondary).
- Scrapbook: Designmodo https://designmodo.com/scrapbook-website-design/ (warns it can look dated if not contemporary).
- Grain: CSS-Tricks, Jimmy Chion, 2021-09-13, "Grainy Gradients": https://css-tricks.com/grainy-gradients/ — feTurbulence `type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'`; `filter: contrast(170%) brightness(1000%)`; blend via `mix-blend-mode: multiply` inside `isolation: isolate`. Frontend Masters (now master.dev): noise hides banding on 8-bit displays; >~50% opacity reads as static; numOctaves rarely >3–4.

## Generic AI-looking UI
- Anthropic, 2025-11-12, "Improving frontend design through Skills": https://claude.com/blog/improving-frontend-design-through-skills (redirects to claude.com/resources/articles/...)
  - "distributional convergence": safe choices dominate training data; without direction models emit "Inter fonts, purple gradients on white backgrounds, and minimal animations".
  - Font suggestions: code — JetBrains Mono, Fira Code, Space Grotesk; editorial — Playfair Display, Crimson Pro; technical — IBM Plex, Source Sans 3; distinctive — Bricolage Grotesque, Newsreader. Pairings: display + mono, serif + geometric sans. Extreme weight contrast (100/200 vs 800/900), size jumps 3×+.
  - Color: commit to one cohesive aesthetic, CSS variables, dominant colors with sharp accents; inspiration from IDE themes, cultural aesthetics. Motion: one orchestrated page load with staggered reveals > scattered micro-interactions. Backgrounds: layered gradients, geometric patterns, contextual effects.
  - Caveat in the article: models still converge (e.g., on Space Grotesk) across generations.
- prg.sh, 2025-10-26, "Why Your AI Keeps Building the Same Purple Gradient Website": https://prg.sh/ramblings/Why-Your-AI-Keeps-Building-the-Same-Purple-Gradient-Website — Tailwind demo default `bg-indigo-500` copied into training data (Adam Wathan apology Aug 2025, secondary); tells: Inter/Roboto, purple/indigo on white/light gray, centered hero + CTA + "three features in boxes below, each with an icon", "Rounded corners on everything", "Subtle shadows (exactly 0.1 opacity)", missing validation/error states/a11y. Fixes: specify typography/color/motion/background, reference a named aesthetic, name defaults to avoid, ask for multiple directions, reference-driven workflow.
- Other: purple-to-blue gradients also trace to Notion/Linear/Vercel-era marketing (aihola, secondary). Made Good lists glossy 3D blobs as generic AI-default look (search).

## Reference-site URL checks (curl, 2026-10-10)
200 OK unless noted; final URL after redirects in brackets.
- Swiss: https://www.ibm.com/design/language/ · https://www.swissted.com/ · https://www.vitsoe.com/ [→ /rw]
- Quiet luxury: https://www.therow.com/ · https://www.kinfolk.com/ · aesop.com (403 bot wall — not cited)
- Editorial: https://pudding.cool/ · https://www.itsnicethat.com/ · https://www.theverge.com/ · nytimes.com (403)
- Neo-brutalism: https://gumroad.com/ · https://www.neobrutalism.dev/
- Raw brutalism: https://www.berkshirehathaway.com/ · https://brutalistwebsites.com/
- Glass: https://learn.microsoft.com/en-us/windows/apps/design/style/acrylic · https://www.nngroup.com/articles/glassmorphism/
- Liquid Glass: Apple newsroom + HIG materials (above)
- Neumorphism: https://neumorphism.io/ (CSS shadow generator)
- Claymorphism: https://hype4.academy/articles/design/claymorphism-in-user-interfaces (title now "SquarePlanet")
- Tactile: https://teenage.engineering/ · https://family.co/
- Flat 2.0: https://design-system.service.gov.uk/ · https://atlassian.design/ · https://www.gov.uk/
- M3E: https://m3.material.io/ · design.google research (above)
- Bento: https://www.apple.com/iphone/ · https://bentogrids.com/
- Dark dev: https://linear.app/ · https://www.raycast.com/ · https://vercel.com/
- Aurora: https://stripe.com/ [→ /th by geo; HTML contains many gradient definitions]
- Cyberpunk: https://www.cyberpunk.net/ [→ /th/en/]
- Vaporwave: https://en.wikipedia.org/wiki/Vaporwave (aesthetics.fandom.com 403)
- Memphis: https://www.memphis-milano.com/ [→ https://memphis.it/it/] · https://en.wikipedia.org/wiki/Memphis_Group
- Organic: https://www.patagonia.com/ · https://www.allbirds.com/
- Pastel: https://www.glossier.com/ · https://www.headspace.com/
- Playful 3D: https://spline.design/ · https://www.duolingo.com/
- Anti-design / maximal: https://mschf.com/
- Kinetic type: https://www.awwwards.com/inspiration/type-transformation-kinetic-type-animation · https://basement.studio/
- Monochrome: https://nothing.tech/ · https://vercel.com/
- Art Deco: https://blog.spoongraphics.co.uk/articles/showcase-30-art-deco-inspired-designs-artworks (gallery; no verified live Deco website found)
- Bauhaus: https://bauhauskooperation.de/ (institutional)
- Japanese minimal: https://www.ndc.co.jp/hara/en/ [→ https://hara.ndc.co.jp/] · muji.com (connection failed — not cited)
- Scandinavian: https://www.hay.dk/ [→ https://www.hay.com/] · https://www.muuto.com/
- Spatial: https://developer.apple.com/design/human-interface-guidelines/designing-for-visionos (client-rendered; numbers not extracted)
- Isometric: https://www.monumentvalleygame.com/
- Hand-drawn: https://excalidraw.com/ · https://www.tldraw.com/
- Collage: https://designmodo.com/scrapbook-website-design/
- Pixel: https://poolsuite.net/ · https://www.lexaloffle.com/pico-8.php
- Terminal: https://charm.sh/ [→ https://charm.land/]
- Cinematic WebGL: https://lusion.co/ · https://activetheory.net/ · https://www.igloo.inc/ · https://landonorris.com/ · https://messenger.abeto.co/
- Dopamine: https://www.duolingo.com/ · https://trends.daisyui.com/trend/dopamine-design/
- AI-native: https://ai-sdk.dev/docs/ai-sdk-ui/generative-user-interfaces · https://v0.app/ (perplexity.ai, claude.ai, chatgpt.com 403 to curl — not cited)
- Grain: https://css-tricks.com/grainy-gradients/ (grainy-gradients.vercel.app returned 402 — not cited)
- Y2K: https://webflow.com/blog/y2k-aesthetic

## AI SDK generative UI
- https://ai-sdk.dev/docs/ai-sdk-ui/generative-user-interfaces — LLM tool calls → React components; `useChat` client + `streamText` route; AI SDK 5 tool parts typed `tool-${toolName}`; states `input-available` (loading), `output-available` (render `part.output`), `output-error` (`part.errorText`).

## Could not verify / excluded
- Apple HIG body text (materials, visionOS target sizes) — client-rendered.
- M3 Expressive exact spring token values and shape-scale additions.
- Webflow 2026 article direct text (header overflow); 2 of 8 trends unknown.
- Dribbble 2026 trend report — none found (only "Best Shots of 2026" showcase).
- Awwwards' own trend article — not found.
- "73% of consumers can spot AI content" (Bigeye) — unsourced, excluded.
- Web Designer Depot claims about iOS 26.2 "Opaque Mode" and "Solid Design" — unconfirmed, excluded.
