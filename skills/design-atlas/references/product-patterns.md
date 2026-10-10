# Product Patterns by Type

> Read when: starting a product or page and you need to know what *this kind* of product must have; choosing how much motion/3D a product can carry; reviewing a design for a specific industry (e-commerce, limited drops, beauty, fintech, health, AI, gov, dashboards…); a user says "make it feel like a real X app".

**Contents:** How to use · Motion intensity scale · Cross-cutting rules · 1 Marketing landing · 2 B2B SaaS · 3 Dashboards · 4 E-commerce (+ limited drops, raffles, launches) · 5 Fintech/crypto · 6 Health/wellness · 7 Education · 8 Social/community · 9 Content/editorial · 10 Portfolio/agency · 11 Booking/travel · 12 Food delivery/marketplace · 13 Real estate · 14 Gaming/streaming · 15 Productivity/dev tools · 16 AI products · 17 Internal enterprise · 18 Government · 19 Beauty & personal care · Summary table · Pitfalls · Sources

## How to use

1. Find the product type below (hybrids: take the *stricter* trust/motion rules of the two, e.g. a health marketplace = health trust + marketplace patterns). The motion level here is the default per surface; the ambition dial and the context-of-use gate in `creative-direction.md` §1 can raise it for marketing/brand surfaces when the user asks for a creative or cinematic experience, but never for surfaces where people arrive in distress. In regulated categories (health and finance advertising, cosmetics claims — §5, §6, §19) a raised dial changes the visuals, never the claims: copy, before/after imagery and testimonials still follow that category's advertising rules.
2. Copy its **core jobs** into the brief; design **key screens** first, decoration last.
3. Set motion with the **intensity scale**; it caps every later animation decision (`motion.md`, `scroll-parallax.md`, `3d-webgl.md`).
4. Pick style + palette from the listed directions (definitions in `styles-catalog.md`, palette mechanics in `color.md`, type in `typography-layout.md`).
5. Run the type's pitfalls + global `## Pitfalls` before shipping. Award-site examples per type live in `inspiration.md`.

## Motion intensity scale

| Level | What is allowed | Typical budget | Fallback |
|---|---|---|---|
| **none** | State feedback only: focus rings, pressed/hover colour, validation, progress. No decorative motion. | ≤ ~100 ms state changes | n/a |
| **subtle** | Functional transitions: expand/collapse, toasts, drawers, list reorder, skeletons for full-page loads, number tweening on KPI refresh. | 100–300 ms; modals/sheets 200–300 ms (NN/g) | `prefers-reduced-motion` → fades or instant |
| **expressive** | Branded motion: scroll-triggered reveals, page transitions, Lottie/Rive illustrations, kinetic type, a lazy-loaded 3D hero with a static poster. | UI parts still 100–400 ms; hero sequences may be longer but never block input | static image/poster; skip intro animations |
| **immersive** | Motion/3D *is* the content: WebGL/WebGPU scenes, scroll-driven storytelling, sound, game mechanics. | Interaction feedback still < 100 ms; first meaningful frame fast; loader with real progress | "lite"/2D mode, captions, skip-intro, keyboard path |

Rules that apply at every level:
- NN/g: most UI animation 100–500 ms; simple feedback ~100 ms; substantial screen changes 200–300 ms; 400 ms already "very slow"; 500 ms feels like a drag.
- WCAG 2.3.3 (AAA): interaction-triggered motion must be disable-able unless essential; parallax is the cited example of non-essential motion (vestibular triggers). Honour `prefers-reduced-motion` from **subtle** upward (`accessibility.md`).
- Raise the level only when motion carries meaning the user came for (brand story, product form, play). Task products (money, health, forms, admin) stay at none/subtle no matter how "premium" the brief sounds.

## Cross-cutting rules (all product types)

- **Response time:** 0.1 s feels instant; 1 s keeps flow (show working state); 10 s is the attention limit → percent-done + a way to cancel (NN/g). Give feedback within 400 ms (Doherty threshold).
- **Loading indicator by wait:** < 1 s: nothing (flashing placeholders feel broken) · full-page load < 10 s: skeleton with real layout (never header/footer-only "frame" skeletons) · single module 2–10 s: spinner + specific text ("Loading comments…") · > 10 s or record batches: progress bar/"3 of 50" + cancel (NN/g progress indicators, skeleton screens).
- **Forms:** ask only what you need; reuse earlier answers; mark optional fields "(optional)" instead of asterisks; one question per page for long or high-stakes flows (GOV.UK).
- **Trust baseline:** real company identity (address, people), conventions over novelty, fast load, visible policies near the action, payment/security marks only where the decision happens (Baymard trust).
- **States:** every list/table/feed ships empty, loading, error, partial and "no permission" states; every destructive action has confirm or undo.

---

## 1. Marketing landing page (product/SaaS/app/campaign)

- **Mindset:** skimming, sceptical, decides within seconds whether to stay (Baymard's trust article puts it at the first ~15 s); arrives from an ad/search/social with one question ("is this for me?").
- **Core jobs:** understand what it is → believe it works → see price/effort → take one action (sign up, demo, buy, download).
- **Key screens/sections:** hero (who it's for + outcome + primary CTA + product visual) → social proof strip → 3–5 benefit/feature blocks with real UI → how it works → pricing or "starts at" → objections/FAQ → final CTA → footer with legal/company.
- **Must-have patterns:** one primary CTA repeated (same label everywhere); real product screenshots/video, not abstract blobs; logo wall or numbers with source; sticky header CTA after hero scrolls out; mobile hero fits CTA above the fold.
- **Conversion levers:** specific headline (outcome + audience); reduce CTA anxiety copy ("No card required", "Cancel anytime" only if true); demo/video near hero; pricing transparency; testimonials with name/role/photo; A/B test headline + hero visual first.
- **Trust:** company identity, security/compliance badges only if earned, privacy link by every form, no fake counters or scarcity.
- **Style & palette:** Swiss/minimal or bento grid for SaaS; editorial for B2B thought-leadership; bold/maximal or neo-brutalist for consumer & creator tools; dark luxury for premium hardware. One brand accent + neutrals; accent reserved for CTAs (`color.md`).
- **Motion/3D: expressive** (campaign/hardware launch: **immersive** allowed). Motion sells the product's character; the page has one job and no repeated-task fatigue. Keep CTA and copy readable without JS/WebGL.
- **Examples:** Oryzo AI (Lusion), Terminal Industries, Anime.js, Lando Norris (see `inspiration.md`).
- **Pitfalls:** feature-list hero with no audience; auto-rotating carousel hero (the message depends on timing the user doesn't control); scroll-jacked storytelling that hides pricing; multi-megabyte autoplay hero video on mobile data.

## 2. B2B SaaS app (logged-in product)

- **Mindset:** at work, goal-driven, repeated daily use; evaluator during trial, power user once habits form; many roles (admin, member, viewer, billing owner).
- **Core jobs:** set up workspace → import/connect data → do the core task fast → collaborate/share → administer (seats, roles, billing, SSO, audit).
- **Key screens:** onboarding checklist, home (recent + next actions), core object list + detail, create/edit, search/command palette, settings (workspace, members & roles, billing, integrations, API keys, security), notifications.
- **Must-have patterns:** left nav + top bar; list ↔ detail split; command palette (⌘K); bulk actions; inline edit; autosave with "Saved" state; undo toasts; role-based empty states ("Ask an admin to…"); keyboard shortcuts with discoverable cheat sheet; import with field mapping + dry-run preview.
- **Retention levers:** time-to-first-value checklist (keep it to a handful of steps — heuristic); templates/sample data; integrations that make it the system of record; collaboration invites at the moment of value (share result), not on day 1; usage-based nudges in-product, not only email.
- **Trust:** SSO/SAML, audit log, data export, status page link, clear permission model ("Who can see this?" on share dialogs), billing previews before plan changes.
- **Style & palette:** Swiss/minimal, neutral greys + one brand accent; semantic colours (success/warning/danger/info) as tokens; density modes (comfortable/compact). See `design-systems.md`.
- **Motion/3D: subtle.** Used for hours a day; motion must explain state changes (panel opens, row moves), never decorate. 3D only inside the marketing site.
- **Pitfalls:** modal-on-modal; settings scattered across 3 menus; destructive actions without undo; onboarding tour that blocks the UI (use checklists + contextual hints instead).

## 3. Admin / analytics dashboard

- **Mindset:** monitoring (operational: "is something wrong right now?") or analysing (analytical: "why did it change?"). Decide which before layout — NN/g treats them as different dashboard types.
- **Core jobs:** spot anomalies at a glance → drill into the cause → filter/segment → export/share → act (assign, fix, alert).
- **Key screens:** overview (KPI row + 2–4 primary charts), drill-down/detail, data table, filter/segment builder, alerts config, report export/scheduling.
- **Data density rules:**
  - One screen, one task (NN/g); most important KPI top-left; heuristic: ≤ 4–6 KPI cards in the first row.
  - KPI card = label · value · delta vs explicit period ("vs last 7 days") · sparkline; never a delta without the comparison window.
  - Use length and 2D position (bars, lines, dots) for quantities; colour only for grouping/highlight — colour has no inherent order (NN/g). No 3D charts, no radial gauges for KPIs.
- **Chart choice (NN/g):**

| Question | Chart |
|---|---|
| Compare categories | bar (horizontal when labels are long); sort bars |
| Two groups / before–after | paired bars |
| Change over time | line (data-point markers show when data was collected) |
| Relationship between two measures | scatterplot |
| Part-to-whole | series of bars beats stacked bars; pie only when the disparity is very large |
| Avoid by default | pie/donut, bubble, mosaic, waffle, Sankey, dendrogram, stacked area, treemap (exploration only) |

- **Tables (NN/g data tables):** sticky header + frozen first column; human-readable first column (name, not ID); most important columns left; zebra/borders/hover for row tracking; visible "filters active" indicator; sort on every column; column hide/reorder without drag-only; batch actions via checkboxes + Select All above the table; edit in place for narrow tables, non-modal side panel for wide ones. Right-align numbers with tabular figures (`font-variant-numeric: tabular-nums`).
- **Filters:** global filter bar (date range first) that applies to every widget; show applied filters as removable chips; persist filters in the URL so views are shareable.
- **Trust:** "Last updated 09:42" + data source on every widget; explain metric definitions in a tooltip; empty vs zero vs "no data" must look different.
- **Style & palette:** utilitarian/data-dense Swiss; neutral canvas, one categorical palette tested for colour-blindness, reserved red/green with icons/signs (`color.md`; the `dataviz` skill if present). Dark mode for NOC/trading screens.
- **Motion/3D: subtle.** Animate data updates (tween numbers, transition bars) ≤ 300 ms so changes are noticed; never loop or pulse decoratively — operational dashboards are watched for real anomalies.
- **Pitfalls:** 12 KPI cards of equal weight; dual-axis charts that imply false correlation; colour as the only signal for good/bad; auto-refresh that resets scroll/filters.

## 4. E-commerce (DTC store, retailer, marketplace storefront)

- **Mindset:** comparing, price- and delivery-sensitive, risk-averse about fit/quality/returns; often mobile, often interrupted.
- **Core jobs:** find (search/browse/filter) → evaluate (images, specs, reviews, total cost, delivery date) → decide (variant, quantity) → pay quickly → track/return.
- **Key screens:** home/category, product list (PLP) with filters/sort, product page (PDP), cart, checkout (account choice → address → delivery → payment → review), confirmation, order tracking, returns, account.

**Baymard findings to design against (sourced):**
- **Abandonment:** documented average cart abandonment 70.22% (50 studies, list updated 2025-09-22). Top reasons (excluding "just browsing"): extra costs too high 40%, delivery too slow 20%, didn't trust site with card 19%, forced account creation 18%, checkout too long/complicated 17%, site errors 17%, returns policy 13%, couldn't see total up-front 12%. Better checkout design: +35.26% conversion potential for large sites.
- **Product list & filters:** mediocre list usability → 67–90% abandonment vs 17–33% with a slightly optimised toolset; 36% of benchmarked sites have severe list flaws. The 5 essential filters: price, user-rating average, colour, size, brand — 57% of sites lack at least one (53% lack a rating filter). Allow multiple values per filter.
- **Product page:** only 49% of large sites reach "decent/good" PDP UX. Avoid horizontal tabs (still on 29% of sites; users overlook tab content) → expanded sections on desktop, collapsed sections on long mobile PDPs. Provide at least one "In Scale" image (42% of users judge size from images; 56% start a PDP by exploring images). Show a shipping-cost estimate on the PDP (64% looked for it before add-to-cart; 43% of sites show none).
- **Checkout:** average checkout has 11.3 form fields (2024) where 8 is enough for most sites; average US flow shows 23.48 form elements by default. Make guest checkout the most prominent option — a button labelled "Guest" at the top of the account step (47% of sites with guest checkout fail this; 24% of US shoppers abandoned solely over forced account creation). Show an estimated delivery **date** (or a range ≤ ~5–7 days wide) per shipping option next to its cost (41% of sites don't).
- **Checkout benchmark:** 65% of 344 top US/EU sites are "mediocre" or worse; the average site has 32 checkout improvements to make.

- **Must-have patterns:** search with autocomplete + typo tolerance; filter chips with counts; sticky add-to-cart on mobile PDP; variant buttons (not dropdowns) for size/colour with out-of-stock shown not hidden; total cost (tax, shipping, fees) visible before payment step; address autocomplete; express wallets (Apple Pay/Google Pay; Thai market: PromptPay QR and mobile-banking deep links); order-status page that works without login.
- **Conversion/retention levers:** free-shipping threshold progress in cart; delivery date promises; reviews with photos + filter by rating; back-in-stock alerts; saved carts; reorder; post-purchase tracking emails linking to a branded tracking page.
- **Trust:** returns policy linked from PDP and cart; reviews you don't curate away; secure-payment cue at the card form; real contact + company address in footer.
- **Style & palette:** product-first, photography-led minimal (neutral backgrounds so product colour is true); maximal/colourful for food & lifestyle DTC; luxury = generous whitespace, serif display, restrained palette. Sale/price colour must still meet contrast.
- **Motion/3D: expressive on browse/PDP, subtle in cart/checkout.** 3D/AR viewer for products where form matters (furniture, eyewear, devices) with photo fallback; checkout gets zero decorative motion — it is a form and the 17%-too-complicated reason lives there.
- **Examples:** Mana Yerba Mate (Awwwards E-commerce of the Year 2023), Opal Tadpole (2024), Scout Motors (2025), Shopify Renaissance Edition.
- **Pitfalls:** shipping cost revealed only at payment; "Create account" as the default path; infinite scroll with footer links unreachable; filters that reset on back navigation.

**Limited drops, raffles and launches** (sneakers, streetwear, collaborations, limited beauty launches). Demand exceeds stock on purpose, so fairness *is* the UX and every state must be true. Pick the allocation model first and name it on the product page:

| Model | Flow | Use when | Real example (checked 2026-10-10) |
|---|---|---|---|
| Draw / raffle | entry window → random pick **per size** → result to every entrant → charge winners | demand ≫ stock; bots and fast fingers must not matter | Nike SNKRS Draw: one entry per Member per draw; size can't be changed after submit; card pre-authorised, charged only if selected; selected and not-selected entrants emailed within 24 h after the countdown ends. UK rules: winners picked by random drawing per size, duplicate registrations for the same style void, charge taken at dispatch |
| Registration + timed queue | register size → purchase link at drop → first-come queue → short checkout hold → reallocate | moderate demand, fixed date | END. Launches (2019 explainer): link emailed to all registrants at the drop; 5 minutes to pay, then the pair goes to the next person in the queue |
| Waiting room, random admission | arrivals before the start wait in a pre-queue, shuffled at start time, admitted as capacity frees | flash sales; protecting the origin | Cloudflare Waiting Room: `Random` queueing is recommended "to distribute products or services more equitably"; pre-queue + `shuffle_at_event_start` |
| Notify me / waitlist | opt in → one message when it becomes buyable | unknown date, restocks | The Ordinary "Join the Waitlist" on a coming-soon product |

- **Honest countdowns run on server time.** Ship the release instant as an absolute UTC timestamp (END.'s launch listing carries a Unix release time and a countdown mode per product in its page data) and count down against server time (take the offset once from your API response), never the device clock. Print the absolute local time beside it ("Opens Sat 11 Oct, 10:00 ICT"). The timer never restarts on reload, on a new device or for a new visitor; at zero the server flips the state and the client re-fetches. Keep the ticking digits `aria-hidden` and expose one `<time datetime>` plus announcements at milestones only.
- **Per-account limits, stated up front.** "1 entry per person · 1 pair per order" next to the entry button, enforced on the server; a second attempt shows the existing entry, not an error.
- **Entry → confirmation → result.** A review step before submit (Nike entries can't change size afterwards) → confirmation screen and email repeating size, masked payment method, closing time and when results arrive → a way to withdraw until the draw closes (END. allowed cancelling entries before close, per a 2021 review) → a result for winners **and** non-winners (Nike notifies both) → winners get the order confirmation, others "Not selected" plus the next relevant drop. Say how money moves: "We'll place a temporary hold of ฿X; you're charged only if selected."
- **Size first.** On a launch PDP the size picker is the primary control, because the entry *is* a size. Remember the user's sizes (Aimé Leon Dore: "My Sizes" plus a "Hide sold out products" filter), show every size with unavailable ones disabled, not hidden, and never show invented odds: the draw runs per size, so odds depend on entries and stock in that size (Nike UK rules).
- **Queue and bot protection.** The waiting page names the drop, shows an honest position or estimate, and says what refreshing does: a FIFO room keeps order with a cookie timestamp, a random room has no order to keep ("you'll be let in at random; refreshing won't help or hurt"). Once admitted, show the checkout hold as a visible timer. Put the bot rule in the terms and act on it (Nike bans bots, scripts and automated entry and may refuse sale or cancel winning entries). Prefer invisible, risk-based checks over puzzles; any challenge needs an accessible alternative (`accessibility.md`).
- **Distinct states:** Upcoming (date + Notify me) → Open (Enter / Buy) → Closed, results pending ("Results by 11 Oct, 10:00") → Selected / Not selected → Sold out → Restocked. Nike's SNKRS web feed is split into Feed / In Stock / Upcoming. Offer "Notify me if restocked" only when a restock can happen; otherwise "Sold out. This release won't restock."
- **Stock counts only when true.** "Low stock" or "3 left" only from live inventory for that variant at render time; no viewer counts, no invented queue sizes.
- **What fake urgency and scarcity look like here:** a countdown that restarts per visit or device (deceptive.design cites a timer that reset on every new device or browser) or keeps running after the sale ends; "only 2 left" that isn't inventory; "1,284 people in the queue" that isn't measured; calling a first-come release a "draw"; "last chance" on a product that restocks weekly. These are the fake-urgency and fake-scarcity deceptive patterns (`psychology.md` "Deceptive patterns and the law").

## 5. Fintech, banking, crypto

- **Mindset:** anxious about money, error-averse, checks balances often in short sessions; crypto users additionally irreversibility-aware and volatility-driven.
- **Core jobs:** check balance/positions → move money (pay, transfer, top-up, withdraw) → understand spending/returns → manage cards/limits/security → get help fast.
- **Key screens:** home (balance + recent activity + primary actions), transfer/pay flow, transaction list + detail, card controls (freeze, limits), statements/tax docs, security (devices, 2FA), onboarding/KYC, support.
- **Must-have patterns:** amount-first transfer with recipient confirmation screen (name, masked account, amount, fee, arrival time) before submit; biometric re-auth for sensitive actions; receipts with reference IDs; freeze card in one tap; pending vs settled visually distinct; search + filter transactions; human-readable merchant names. Crypto: network selector with fee + time, address paste with checksum validation and first/last-chars confirmation, test-amount suggestion, explicit "irreversible" copy before broadcasting.
- **Retention levers:** insights (spend categories, upcoming bills), goals/savings pots, instant notifications for every transaction (security + habit), referral rewards with clear terms.
- **Trust:** licence/regulator statement and deposit protection where applicable; fees shown before confirmation, never after; consistent number formatting (currency symbol, thousands separators, tabular figures); never auto-play marketing inside money flows; session timeouts with warning; plain-language error with next step ("Transfer not sent. Your balance hasn't changed.").
- **Style & palette:** Swiss/minimal or soft-modern; deep navy/ink or near-black + one confident accent; gains/losses use green/red **plus** sign (+/−) and arrow icons; avoid alarming red as the brand colour. Crypto/trading UIs often default to dark; keep contrast AA.
- **Motion/3D: subtle.** Motion confirms state (sent ✓, card frozen) and must never delay a money action; 3D/immersive belongs on the marketing site only (e.g. Hatom, a DeFi protocol, went immersive on its brand site — FWA People's Choice).
- **Pitfalls:** fee or FX rate appearing on the final screen; ambiguous "Pending"; balance hidden behind a carousel; confetti on a transfer that later fails.

## 6. Healthcare, telemedicine, wellness

- **Mindset:** worried, sometimes unwell or in pain, often older or caring for someone; low tolerance for jargon; privacy-sensitive.
- **Core jobs:** find the right care (symptom → service → clinician) → book/reschedule/cancel → attend (video visit, check-in) → get results/prescriptions → pay/claim → message the care team.
- **Key screens:** find care/search, clinician profile, availability + booking, intake/consent forms, appointment details (time, place/link, prep), waiting room + video call, results viewer with plain-language explanation, medications/refills, messages, billing, profile + proxy/caregiver access.
- **Booking flow:** choose service/reason → location or video → clinician (optional "first available") → date/time slots grouped by day with time zone shown → patient details (prefill) → review (who, what, when, where, cost/coverage, cancellation policy) → confirm → add to calendar + reminders (SMS/email/push) → reschedule/cancel link in every reminder.
- **Must-have patterns:** plain language — NHS writes for reading age 9–11 (medical info: understandable by 11–14), sentences ≤ ~20 words, plain term first then medical term ("piles (haemorrhoids)"); one question per page for intake (GOV.UK pattern); large tap targets and ≥ 16 px body (older users; `accessibility.md`); readable results with reference ranges and "what this means / what to do next"; emergency disclaimer + emergency number on symptom tools; proxy access for caregivers.
- **Retention levers:** reminders, care plans with progress, easy refills, follow-up booking from the visit summary; wellness: streaks and gentle goals, never shame language.
- **Trust & privacy:** health data is regulated — US HIPAA protects PHI held by covered entities and their business associates, with a "minimum necessary" disclosure rule and administrative/physical/technical safeguards; under GDPR, health data is a special category (Art. 9); Thailand's PDPA (B.E. 2562/2019, regulator PDPC) §26 lists health, disability, genetic and biometric data as sensitive personal data that needs explicit consent unless a listed exception applies (Tilleke & Gibbins analysis; confirm the medical-treatment exceptions with counsel). Design consequences: no PHI in push-notification previews, emails, URLs or analytics events; explicit, granular consent screens; visible clinician credentials; "who can see this" on shared records.
- **Style & palette:** calm, soft-minimal; blues/teals/greens with warm neutrals; avoid clinical pure white + red alarm aesthetics; illustrations of diverse people over stock photos. Strong focus states and AA+ contrast (`color.md`).
- **Motion/3D: subtle (none in clinical flows).** Breathing/meditation apps may go **expressive** for guided exercises (slow, user-paced, reduced-motion alternative). Never animate results, dosages or alerts.
- **Pitfalls:** medical jargon in buttons ("Initiate consult"); time slots without time zone; reminder SMS containing diagnosis; forcing account creation before showing availability.

## 7. Education / e-learning

- **Mindset:** motivated at start, motivation decays; learners fit study into short sessions; parents/teachers/admins are separate audiences.
- **Core jobs:** pick a course/level → learn (watch/read/practice) → check understanding → track progress → get credential; teachers: assign, monitor, give feedback.
- **Key screens:** catalog/placement, course home (syllabus + progress + next lesson), lesson player (video + transcript + notes), practice/quiz with feedback, progress dashboard, certificate, teacher/class dashboard.
- **Must-have patterns:** "Continue where you left off" as the primary home action; lessons chunked to minutes with a visible length; immediate, specific feedback on answers; captions + transcripts + adjustable playback speed; offline/download for mobile; spaced review.
- **Retention levers:** streaks with forgiveness (freeze/repair), reminders at the learner's chosen time, visible mastery not just completion, cohort/community, certificates shareable to LinkedIn.
- **Trust:** instructor credentials, syllabus before payment, refund policy; for minors, parental consent and no public profiles by default.
- **Style & palette:** friendly, rounded, high-contrast; playful/illustrative for kids and language apps; editorial/minimal for professional courses. Distinct colours per subject/track as wayfinding.
- **Motion/3D: expressive** for rewards, feedback and explanations (animated diagrams, Rive/Lottie characters); **subtle** inside reading/quiz content so motion never competes with the concept. Example: Why Zero (education, Awwwards SOTM Sep 2026) uses immersive storytelling for marketing, not for lessons.
- **Pitfalls:** gamification that rewards streaks over learning; autoplay next video; quiz feedback that only says "Wrong".

## 8. Social / community

- **Mindset:** browsing for connection, status and novelty; fast thumb scrolling; two modes — creating and reading — design both.
- **Core jobs:** consume feed → react/comment → post/create → find people/groups → manage notifications, privacy and safety.
- **Key screens:** feed, post detail + thread, composer (text/media), profile, group/community home, search/explore, notifications, DMs, settings (privacy, blocking, muting, reporting).
- **Must-have patterns:** optimistic UI for likes/posts with rollback on failure; draft autosave; media upload progress; threaded replies with "show more"; mention/tag autocomplete; block/mute/report reachable from every post's and profile's overflow menu; content warnings; chronological option where possible; edit history indicator.
- **Retention levers:** first-week follow suggestions tied to interests; notifications that bring people back to *people* (replies, mentions) rather than generic engagement bait; creator analytics.
- **Trust & safety:** clear community rules at join; visible moderation outcomes; age-appropriate defaults; privacy controls per post; no dark patterns in notification permissions.
- **Style & palette:** content-first neutral chrome so user media dominates; brand colour on actions only; dark mode required.
- **Motion/3D: subtle–expressive.** Micro-interactions (like burst, pull-to-refresh) add delight; feed scrolling itself must stay 60 fps with no scroll-linked effects.
- **Pitfalls:** infinite feed with no "you're caught up"; notification badges inflated by low-value events; report flow that ends without confirmation.

## 9. Content / news / blog / editorial

- **Mindset:** reading, scanning headlines, arriving deep-linked from search/social on mobile; ad and paywall fatigue.
- **Core jobs:** scan what's new/important → read an article comfortably → go deeper (related, topics, authors) → subscribe/save/share.
- **Key screens:** front page (hierarchy by importance), section pages, article, author page, topic/tag page, search, newsletter/subscribe, paywall/meter, account/saved.
- **Must-have patterns:** body ≥ 16 px (long reads often 18–20 px) with 45–75 ch measure (`typography-layout.md`); clear dateline + updated time + byline; table of contents for long reads; accessible figures with captions/credits; reading progress optional; related links at the end, not mid-paragraph clutter; fast pages with no ad-driven layout shift (Core Web Vitals, `platform-web.md`).
- **Conversion levers:** newsletter sign-up after value (end of article), metered paywall with clear count, gift links, topic follows.
- **Trust:** corrections policy, sourcing/links, author bios, clear labelling of sponsored and AI-assisted content.
- **Style & palette:** editorial (serif display + sans UI or vice versa), strong grid, near-black on off-white, one accent for links/sections.
- **Motion/3D: none–subtle** for daily news; **immersive** scrollytelling for flagship features and data stories (e.g. Getty "Tracing Art", Awwwards SOTM Jul 2025; "Sculpting Harmony", FWA FOTM Dec 2023) — always with a plain-article fallback.
- **Pitfalls:** interstitials before the first paragraph; layout shift from late ads; parallax on body text.

## 10. Portfolio / agency / creative studio

- **Mindset:** prospective clients and recruits judging craft in seconds; awards juries; peers. Novelty is the product.
- **Core jobs:** feel the studio's craft immediately → browse selected work → read a case study (problem, role, outcome) → contact/hire.
- **Key screens:** intro/hero (often a loader + signature interaction), work index (grid/list toggle), case study, about/team, services, contact, careers.
- **Must-have patterns:** work index reachable in one click from anywhere; case studies with outcomes and credits; contact email visible (not only a form); page transitions that preserve context; a fast path for recruiters/clients who skip the show (skip-intro, plain list view).
- **Conversion levers:** clear services + location + availability; case studies with metrics; "start a project" form with budget/timeline ranges.
- **Trust:** client logos with permission, awards, team faces.
- **Style & palette:** anything distinctive — typographic minimal (Bennett & Clive), dark monochrome (Immersive Garden), electric single accent (Lusion #1a2ffb), playful 3D (Bruno Simon). Consistency within the site matters more than the direction.
- **Motion/3D: immersive.** This is the one category where motion is the portfolio; Awwwards Site + Developer Site of the Year 2023 was a studio site (Lusion v3), and the FWA of the Year announced Jan 2026 is a playable 3D portfolio (Bruno Simon).
- **Pitfalls:** long preloader with no real progress; custom cursor that hides the real one and breaks text selection; unreadable case-study text over video; no keyboard navigation.

## 11. Booking / travel / hospitality

- **Mindset:** planning (inspiration, flexible dates) vs booking (precise, price-comparing); high anxiety about total price, cancellation and location.
- **Core jobs:** search (where, when, who) → compare options → inspect (photos, map, reviews, policies) → book + pay → manage trip (change, cancel, check-in, documents).
- **Key screens:** search with date picker + guests, results (list + map), property/flight/experience detail, room/fare selection, checkout, confirmation/itinerary, manage booking, trips list.
- **Must-have patterns:** date-range picker showing nights count and prices per date where possible; flexible-date option; results map ↔ list sync; total price including taxes/fees from the results page onward; cancellation policy in plain words beside the price ("Free cancellation until 12 Mar"); photo galleries by room/area; reviews filtered by traveller type; offline-accessible itinerary/QR.
- **Conversion levers:** price calendars, saved searches/price alerts, "pay later"/deposit options, loyalty status visible at checkout.
- **Trust:** verified reviews, clear host/operator identity, secure payment, 24/7 support contact on the itinerary.
- **Style & palette:** photography-led; luxury hospitality = editorial serif, earthy/neutral palette, slow pacing (Son Daven, Awwwards SOTM Jun 2026); OTAs = utilitarian minimal with one accent.
- **Motion/3D: expressive for brand/hotel sites, subtle for search/booking engines.** Hotel/resort brand sites may use immersive tours (Explore Primland, FWA FOTM Feb 2026) but the booking widget must be one tap away and motion-free.
- **Pitfalls:** price that grows at checkout (resort/cleaning fees); date picker that loses dates on back; map-only results on mobile.

## 12. Food delivery / marketplace (two- or three-sided)

- **Mindset:** hungry and impatient (food), or bargain/discovery-driven (goods marketplaces); repeat behaviour dominates.
- **Core jobs:** choose store/seller → choose items + customise → see fees/ETA → pay → track live → rate/reorder/report problems. Sellers/couriers have their own apps (orders, availability, payouts).
- **Key screens:** address/location gate, home (reorder, nearby, categories), store/seller page with menu/catalog, item customisation sheet, cart with fee breakdown, checkout, live tracking, order history, help/refund, ratings.
- **Baymard food & takeout benchmark (2026-08-13):** 8 leading apps/sites (incl. Uber Eats, DoorDash, Deliveroo, Just Eat, Domino's, McDonald's) all scored "poor" to "mediocre". Fix first: a route to past orders/reorder from the homepage; dietary and category filters; customisation options described on the item page (allergies); scope markers, breadcrumbs and back paths at every step; delivery timing and tipping clear enough to commit.
- **Must-have patterns:** fee breakdown (delivery, service, small-order, tip) before checkout; ETA range that updates; substitutions policy for grocery; map + status timeline tracking; one-tap reorder; refund flow by item with photo upload.
- **Retention levers:** reorder, scheduled orders, membership with free delivery threshold, favourites, live-tracking push updates.
- **Trust:** seller ratings with count, hygiene/verification badges where real, transparent fees, courier identity in tracking.
- **Style & palette:** appetising photography, warm saturated accents (reds/oranges/greens) on neutral UI; marketplaces: neutral chrome so listings carry colour.
- **Motion/3D: subtle–expressive.** Live-tracking animation and add-to-cart feedback help; never animate menus or prices.
- **Pitfalls:** location gate that blocks browsing; customisation hidden until checkout; tip pre-selected at a high %.

## 13. Real estate

- **Mindset:** long, high-stakes, research-heavy journey; renters move fast, buyers deliberate for months; agents are a third audience.
- **Core jobs:** search by area/price/beds → compare listings → view (photos, floor plan, virtual tour, neighbourhood) → estimate affordability → contact agent/book viewing → save & get alerts.
- **Key screens:** search with map, results list ↔ map split, listing detail, gallery/floor plan/tour, mortgage/affordability calculator, compare, saved homes + alerts, agent profile, enquiry/booking form; developer project microsites.
- **Must-have patterns:** draw-on-map/area search; filters (price, beds, baths, type, size, amenities, pets) with counts; price history and days on market; floor plan and m²/ft² prominently; neighbourhood data (transport, schools) with sources; sticky contact/booking CTA; saved search alerts.
- **Trust:** verified listings, agent licence, last-updated date, no bait listings; disclose fees.
- **Style & palette:** listings portals = utilitarian minimal; luxury developments = editorial/luxury (ERA Residence, Sobha Privy Collection — pastel or dark, generous whitespace, serif display).
- **Motion/3D: subtle for portals; expressive–immersive for luxury project microsites** (3D massing, scroll-driven tours) with fast access to floor plans and price list PDFs.
- **Pitfalls:** map pins that don't match the listing district; galleries without floor plans; enquiry forms asking for income up front.

## 14. Gaming / entertainment / streaming

- **Mindset:** leisure, mood-driven, lean-back (TV) or lean-in (games); fandom; frequently on TV remotes, consoles and phones.
- **Core jobs (streaming):** pick something fast → resume → manage profiles/watchlist → control playback (subtitles, audio, quality). **(Games/launch sites):** feel the world → watch trailer → wishlist/pre-order/play.
- **Key screens:** profile picker, home rows (continue watching first), title detail, player with controls, search, downloads, settings (subtitles, parental controls); game sites: hero/trailer, world/lore, characters, media, buy/wishlist, news, community.
- **Must-have patterns:** continue-watching row; preview on focus with muted autoplay that can be disabled; skip intro/recap; subtitle styling options; 10-foot UI focus states for remote navigation (`platform-desktop.md`/TV); age ratings visible.
- **Accessibility:** follow the Xbox Accessibility Guidelines (v3.2; per-guideline goal, scoping questions, implementation guidelines) and gameaccessibilityguidelines.com for remappable controls, subtitles, colour-blind modes, difficulty options.
- **Retention levers:** personalised rows, new-episode notifications, cross-device resume; games: seasons, events, social features.
- **Style & palette:** dark, cinematic, poster-art-led; key art defines palette per title; neon/gradient accents for games.
- **Motion/3D: immersive for game & film launch sites** (Welcome to Berk WebGL island, FWA FOTM Sep 2025; Haunted by Nostalgia WebGL trivia) — **expressive** for streaming browse UIs (focus zoom, row transitions), **subtle** inside the player.
- **Pitfalls:** autoplay with sound; focus lost after closing a modal on TV; heavy WebGL hero never tested on TV/console browsers.

## 15. Productivity / developer tools

- **Mindset:** expert, keyboard-first, flow-protective; judges tools by speed and reliability; reads docs before marketing.
- **Core jobs:** get started (install/CLI/API key) → do the core task with minimal friction → integrate into existing workflow → debug/troubleshoot → collaborate.
- **Key screens:** quickstart/docs, dashboard/project list, editor/workspace, command palette, logs/runs/history, settings (tokens, env vars, webhooks), billing/usage.
- **Must-have patterns:** command palette + full keyboard shortcuts; copy-to-clipboard on every code block, ID and key; code samples in the user's language (tabs remembered); search across docs; logs with filtering, live tail, timestamps with time zone; deep links to any object; status/incident banner; CLI parity with UI.
- **Retention levers:** fast time-to-first-success (a working "Hello world" from the quickstart in minutes), templates, integrations (GitHub, Slack), generous free tier with visible usage.
- **Trust:** transparent pricing + usage meters, uptime/status page, changelog, security/compliance page, data export.
- **Style & palette:** Swiss/minimal or terminal-inspired; dark mode first-class; monospace for code/IDs only; syntax highlighting palette with AA contrast.
- **Motion/3D: subtle in product, expressive on the marketing site** (Anime.js — Awwwards SOTM May 2025 — demonstrates the library *as* the landing page).
- **Pitfalls:** docs behind login; API keys shown once without copy button; marketing animation on docs pages.

## 16. AI products (assistants, copilots, generators, agents)

- **Mindset:** curious but unsure what the system can do; trust is uncalibrated (over-trust or dismiss); waiting is felt more because output streams.
- **Core jobs:** state intent → get a useful draft/answer/action → verify it → refine → use it elsewhere (copy, insert, export, apply) → stay in control of data and actions.
- **Key screens/surfaces:** chat/thread view, inline assist in an existing editor (selection → action), generation canvas (images/video/docs), agent run view (plan → steps → approvals → result), history, settings (memory, data use, model choice).
- **Chat UI anatomy:** composer docked at bottom (multiline, attachments, model/mode picker, send ↔ stop); thread with user/AI turns visually distinct; per-message actions (copy, regenerate, edit prompt, feedback 👍/👎, share); starter suggestions on empty state; conversation list with search and rename.
- **Streaming states (map to UI):** AI SDK 5 `useChat` exposes `status`: `submitted` (show "thinking" indicator within 400 ms) → `streaming` (render tokens; swap Send for **Stop**, which calls `stop()`) → `ready` (show actions, enable regenerate via `regenerate()`) → `error` (inline error + Retry; `resumeStream()` after network drops). Keep the viewport pinned to the bottom only while the user hasn't scrolled up.
- **Latency patterns:** specific progress copy ("Summarizing key themes from your notes", not "Processing…" — Apple HIG); show plan/steps for agent runs; background generation with notification for long jobs; skeleton of the expected artefact (table, image frame) when the shape is known; percent/steps for > 10 s jobs with cancel (NN/g).
- **Citations & grounding:** inline numbered citations linked to a sources panel; show retrieved document titles/dates; distinguish "from your files" vs "from the web" vs "model knowledge"; let users open the exact passage.
- **Editable outputs:** render drafts in an editor, not a frozen bubble; Edit / Undo / Retry / Adjust next to output and acknowledge when a correction took effect (Apple HIG, 2026-06-08 update); offer variations to choose from; diff view when AI edits user content; "Insert"/"Replace"/"Copy" as explicit actions.
- **Generative UI:** let tools render components instead of prose (weather card, booking form, chart). In AI SDK 5, tool calls arrive as typed message parts `tool-<name>`; render by state — `input-available` → loading card, `output-available` → component with `part.output`, `output-error` → `part.errorText` + retry. Human-in-the-loop approvals via `addToolApprovalResponse`.
- **Trust & control (HAX 18 guidelines, Apple HIG):** make clear what the system can do and how well (G1–G2); support efficient invocation, dismissal and correction (G7–G9); scope services when in doubt (G10); explain why it did something (G11); global controls and notify about changes (G17–G18); disclose AI-generated content; never pretend to be human; ask permission before using personal data and say whether it trains models; confirm before irreversible actions (delete, purchase, send) — show an action plan and require approval for agents.
- **Error / hallucination UX:** state limitations up front; avoid AI where a hallucination could harm (Apple HIG); "can't help with that" responses that coach a better request; confidence cues only if calibrated; easy report-a-problem on every output; fallback to a non-AI path.
- **Pattern vocabulary (Shape of AI):** Wayfinders (suggestions, templates, example gallery), Prompt actions (inline action, regenerate, expand, restyle), Tuners (attachments, connectors, modes, parameters), Governors (action plan, citations, branches, variations, verification, memory), Trust builders (disclosure, caveat, consent, data ownership, incognito, watermark), Identifiers (name, avatar, colour, iconography).
- **Style & palette:** neutral, content-first; one AI identifier colour/icon used consistently to mark AI content and actions; avoid "sparkle everywhere".
- **Motion/3D: subtle.** Motion communicates progress (typing/streaming indicators, step completion) and must not be mistaken for content; marketing sites for AI products can be expressive–immersive (Oryzo AI, Kriss.ai, Active Theory V6 with AI chat).

```tsx
// AI SDK 5 (@ai-sdk/react) — status-driven composer + generative UI parts.
// CardSkeleton, BookingCard (+ BookingProps), InlineError, Composer are your own components.
import { useChat } from '@ai-sdk/react';

export function Chat() {
  const { messages, sendMessage, status, stop, regenerate, error } = useChat();
  const busy = status === 'submitted' || status === 'streaming';
  return (
    <>
      {messages.map((m) => (
        <article key={m.id} data-role={m.role}>
          {m.parts.map((p, i) => {
            if (p.type === 'text') return <p key={i}>{p.text}</p>;
            if (p.type === 'tool-showBooking') {
              if (p.state === 'input-available') return <CardSkeleton key={i} />;
              if (p.state === 'output-available') return <BookingCard key={i} {...(p.output as BookingProps)} />;
              if (p.state === 'output-error') return <InlineError key={i} text={p.errorText} />;
            }
            return null;
          })}
        </article>
      ))}
      {status === 'submitted' && <p role="status">Searching your calendar…</p>}
      {error && <InlineError text="Something went wrong." onRetry={() => regenerate()} />}
      <Composer disabled={busy} onSend={(text) => sendMessage({ text })} onStop={busy ? stop : undefined} />
    </>
  );
}
```

- **Pitfalls:** blank chat box with no examples; Stop button missing during streaming; auto-scroll that yanks users who scrolled up; citations that link to a homepage not the passage; agents executing purchases/deletes without a confirm step.

## 17. Internal enterprise tools (back-office, ERP, CRM, ops, clinical/HIS admin)

- **Mindset:** trained, repetitive, high-volume, often on desktop with large monitors; errors are costly; users can't choose the tool.
- **Core jobs:** find a record → view/edit many fields → process queues (approve, assign, triage) → report → hand off.
- **Key screens:** search/lookup, queue/worklist, record detail with tabs/sections, bulk edit, approval flows, audit/history, reports.
- **Must-have patterns (NN/g complex apps):** learning by doing without losing work (drafts, undo); nudges toward efficient methods (shortcuts shown in tooltips); flexible non-linear pathways; notes/history so users resume after interruptions; export/copy to other tools; progressive disclosure of advanced options; secondary info in side panels/tooltips instead of navigation away; salience by removing noise. Plus: dense tables (see §3), keyboard-only operation, saved views, field-level validation with server messages mapped to fields, optimistic locking warnings ("Edited by Somchai 2 min ago").
- **Trust:** role-based access, audit trail visible on records, confirmation for bulk changes with count ("Update 248 records?").
- **Style & palette:** utilitarian Swiss; compact density option; status colours as tokens with text labels; no brand flourishes.
- **Motion/3D: none–subtle.** Users repeat actions thousands of times; keep feedback on frequent actions near the ~100 ms "simple feedback" end of NN/g's range — longer animations become friction.
- **Pitfalls:** wizard for a task experts do 50×/day; pagination that loses selection; modals that hide the record being referenced.

## 18. Government / public services

- **Mindset:** obligated, not choosing; any age, ability, device, literacy and language; often stressed (benefits, tax, immigration).
- **Core jobs:** find the right service → check eligibility → apply/submit → pay → track status → get a decision/document.
- **Key screens:** start page (what you need, how long it takes), eligibility questions, question pages, check-your-answers, confirmation with reference number, status tracker, accessible PDFs/alternatives.
- **Must-have patterns (GOV.UK):** one thing per page; the question is the page heading (label/legend); Back link at top; left-aligned "Continue" button; ask only what you need, reuse answers, allow "I do not know"; "(optional)" not asterisks; check-your-answers before submit; error summary at the top of `main` (below Back link, above `<h1>`) linking to each field, receiving focus on load; progress indicator only if testing shows need.
- **Plain language:** plain English mandatory on GOV.UK (80% of people preferred clear English, specialists even more); paragraphs ≤ 5 sentences; split sentences > 25 words; explain unavoidable legal terms at first use; active voice. Provide translations where the population needs them (e.g. Thai + English for Thai public services, with Thai-appropriate line-height — `typography-layout.md`).
- **Principles:** start with user needs; do less; design with data; do the hard work to make it simple; iterate; this is for everyone; understand context; build services not websites; be consistent not uniform; make things open; minimise environmental impact (Government Design Principles, updated 2 Apr 2025).
- **Trust:** official domain and identity, no third-party trackers without consent, data-use statement at each data request, reference numbers + email/SMS receipts.
- **Style & palette:** GOV.UK-style plainness — neutral sans, black on white, one link colour, high-visibility focus (GOV.UK uses a yellow background/outline with a thick black bar), no imagery unless it carries information; WCAG 2.2 AA minimum.
- **Motion/3D: none.** Motion adds risk (vestibular, cognitive load, old devices) and no information.
- **Pitfalls:** PDF-only forms; CAPTCHA without accessible alternative; session timeouts without warning or save; marketing hero banners on transactional services.

## 19. Beauty & personal care (skincare, cosmetics, fragrance)

- **Mindset:** part research ("will this suit *my* skin?", ingredients, reviews), part desire (texture, colour, scent); worried about reactions, the wrong shade and wasted money. Colour and scent can't be tried online, so confidence comes from information, samples and easy swaps.
- **Core jobs:** describe my skin, concern or undertone → find products for it → check ingredients and suitability → see how it fits the routine I already have → try small (sample, mini, discovery set) → buy, refill, reorder → review.
- **Key screens:** shop by concern / skin type / routine step; PDP (claims, key actives, full ingredient list, how to use, warnings, sizes, reviews); shade finder (quiz or selfie match + manual swatches); regimen builder; ingredient glossary; samples and discovery sets; refill/subscription management; reviews with reviewer profile; consultation or store booking.
- **Must-have patterns:**
  - *Ingredient transparency:* key actives with their % when the formula states one (The Ordinary names products by active and %, e.g. "Lacto-PDRN 4% + B9 Eye Cream"); the full INCI list as selectable text in label order, never an image, with each ingredient linked to a glossary entry (Paula's Choice Ingredient Dictionary covers benefits and safety of thousands of ingredients); fragrance, alcohol and essential oils called out for sensitive skin. Thai labels must carry the full ingredient list (ChemLinked), so the PDP should match the pack word for word.
  - *Skin-type and concern filters:* skin type (dry, oily, combination, sensitive) × concern (acne-prone, dullness, uneven tone, signs of ageing, dehydration) as multi-select filters with counts. Thai shops navigate by ปัญหาผิว (Oriental Princess) and by skin type (PAÑPURI "For Dry & Dehydrated Skin").
  - *Regimen / "use with":* step order (cleanse → treat → moisturise → SPF), AM/PM, what pairs well and what not to layer (The Ordinary: Regimen Builder, Layering Guide, shop by "Step 1: Prep / Step 2: Treat"). "Complete the routine" beats a generic "You may also like".
  - *Patch test & sensitive skin:* warnings and "patch test first" next to Add to bag and in How to use, not buried in an accordion; start-slow guidance for strong actives (acids, retinoids); "if irritation occurs, stop use" as plain text.
  - *Shade finder (colour cosmetics):* a selfie match **and** a manual path (Fenty's shade finder matches from a phone selfie and adds a guide to formulas and undertones; Rare Beauty's foundation finder takes 4 steps); shade names that carry depth + undertone (Sunnies Face: "light with cool undertones"); swatches on several skin tones in daylight; the swap policy beside the picker. Say where a selfie goes and when it is deleted; process on-device when you can.
  - *Sizes, samples, refills:* unit price (per ml/g) on every size; minis and travel sizes; sample choice in the cart (Rare Beauty: "Choose 2" free samples); discovery sets for fragrance (Le Labo); refills and refillable packs (Le Labo refills, Fenty "Refillables", PAÑPURI refills) linked from the original PDP.
  - *Reviews by skin type and age:* every review shows the reviewer's skin type, concerns, age range and shade bought, and each is a filter; photo reviews; reaction reports stay visible (E-commerce rule: reviews you don't curate away).
  - *Before/after honesty:* same light, angle, distance, camera and expression; no retouching or filters on the "after"; caption the product(s), routine and time between shots, and how many people a study covered; label paid or gifted creators.
- **Conversion/retention levers:** shade-match swaps, samples with orders, replenishment reminders timed to the size bought, refill subscriptions that are as easy to skip or cancel as to start, routine bundles, consultations (in store or video), gift personalisation (Le Labo's label defaults to "For: You."; PAÑPURI offers engraving).
- **Trust requirements:** only claims you can substantiate, with the evidence kept on file (Thailand requires claim evidence available for inspection — ChemLinked); "dermatologist-tested" or "clinically proven" only with the test named and dated; ingredient list identical to the pack; batch, expiry and period-after-opening; a returns rule for opened products.
- **Thailand: claims and labels (Thai FDA / อย.).** Not legal advice; confirm wording with Thai regulatory counsel.
  - *What counts as a cosmetic:* the Cosmetic Act B.E. 2558 (2015) covers products applied to the outside of the body (including teeth and the mouth's mucosa) for cleanliness, beauty, changing appearance, deodorising or keeping it in good condition (definition reproduced in the Thai FDA notification manual). Claims to treat, alleviate or cure disease, or to change body structure or function, leave that scope: the product is regarded as a drug under the Drug Act (ChemLinked), and the FDA can revoke the product's notification (Tilleke & Gibbins). Copy rule: appearance words ("looks", "visibly", "helps skin feel"), never medical verbs ("treats", "cures", "heals", "therapy").
  - *Prohibited advertising statements* (Act §41, as summarised by ChemLinked): false or exaggerated; causing serious misunderstanding, including misleading scientific data or statistics; medical claims or a non-cosmetic purpose; enhancing libido or sexual performance; promoting crime or immorality; causing public disunity. A ministerial regulation of 22 Nov 2024 adds claims implying use inside the body (except tampons and oral/dental products) and claims implying injection or use with devices that enter the body or push substances deeper than the epidermis.
  - *No advertising licence, but truthful claims:* the Thai FDA (8 Sep 2025) says cosmetic ads need no licence but must be "fair, truthful, and not misleading" and must not imply therapeutic or disease-curing properties; it points to its 2024 updated Cosmetic Advertising Guidelines, and on 25 Aug 2026 it published *Examples of Inappropriate Texts for Cosmetic Advertising* (guidance only, judged case by case). A formal FDA opinion on an ad can be requested (MOPH notification 2018; statutory time 60 days).
  - *Notification number:* a cosmetic must be notified before it is made or imported for sale; the receipt is valid 3 years. The Thai-language label lists the notification receipt number (เลขที่ใบรับจดแจ้ง) among its required items, and the FDA tells consumers to check notification on fda.moph.go.th or LINE @FDAThai. Show the number as text on the PDP near the ingredients. Whether online listings are legally required to display it: **not confirmed**.
  - *Whitening:* the Thai FDA's *Guidelines for Notification and Claims of Cosmetic Products with Specific Efficacy: Ingredient Claims (Issue No. 1/2026)*, early Sep 2026, sets acceptable ingredients and claim wording for whitening and anti-acne cosmetics and prohibits claims implying therapeutic effects or changes to natural skin characteristics (ChemLinked summary; full text **not verified**). Tie brightening claims to the notified ingredients, describe appearance effects only, and avoid "lighter is better" framing.
  - *Before/after imagery:* **no specific Thai rule confirmed.** Treat each image as a claim under the rules above: truthful, not exaggerated, substantiated, and never implying treatment or a change of body structure.
  - *Sunscreen labels:* SPF above 50 is shown as "SPF 50+", and SPF/PA++++ values need test evidence at notification (Thai FDA notification manual).
- **Style & palette moods** (seen on the live sites, 2026-10-10): clinical-minimal for ingredient-led brands (greys, black sans type, product names that read like data — The Ordinary); luxury editorial serif for fragrance and prestige skincare (generous whitespace, serif display; Thai + Latin luxury serif pairings in `typography-layout.md`); moody, earthy photography with restrained type for spa and fragrance (PAÑPURI); one saturated brand colour with a serif display for colour cosmetics (Rare Beauty's berry); bright promo palettes for mass-market Thai brands (Oriental Princess: teal brand bar, pastel campaign art), kept away from ingredient and warning areas. Product shots on neutral backgrounds so swatch colour stays true.
- **Motion/3D: expressive on brand and PDP media, subtle in tools, none on claims and warnings.** Beauty sells through the senses — texture loops, swatch swipes and a 360° bottle earn their place on the PDP — but shade finders, regimen builders, cart and checkout are decisions that need precision, and nothing may animate over a swatch (tints and gradients falsify colour) or make a warning or ingredient list harder to read.
- **Examples:** The Ordinary, Paula's Choice, Fenty Beauty, Rare Beauty, Le Labo, Oriental Princess, PAÑPURI, Sunnies Face (`inspiration.md` "Commerce, streetwear and beauty product references").
- **Pitfalls:** ingredient list as an image; "suitable for all skin types" with no sensitive-skin guidance; a shade finder that requires the camera; swatches shot only under warm light; retouched before/after; medical verbs in copy ("cures melasma", "heals eczema"); "permanent whitening"; reviews that can't be filtered by skin type; countdown banners on a "limited" palette that restocks (see §4 drops).

---

## Summary table

| Product type | Motion / 3D | Typical style (see `styles-catalog.md`) | Primary KPI |
|---|---|---|---|
| Marketing landing | expressive (campaign: immersive) | Swiss/minimal, bento, bold/maximal | visitor → signup/demo conversion |
| B2B SaaS app | subtle | Swiss/minimal, neutral + 1 accent | activation rate, weekly active teams, net retention |
| Admin/analytics dashboard | subtle | utilitarian data-dense | time-to-insight, report usage, alert response time |
| E-commerce | expressive (browse/PDP) · subtle (checkout) | photo-led minimal, maximal DTC, luxury | conversion rate, AOV, cart abandonment |
| Fintech/banking/crypto | subtle | soft-modern/minimal, dark for trading | successful transactions, MAU, support contacts per user |
| Health/telemedicine/wellness | subtle (clinical: none) | calm soft-minimal | booked & attended appointments, task completion |
| Education/e-learning | expressive (feedback) · subtle (content) | friendly rounded / editorial | lesson completion, D30 retention, mastery |
| Social/community | subtle–expressive | content-first neutral, dark mode | DAU/MAU, posts per active user |
| Content/news/editorial | none–subtle (features: immersive) | editorial serif/sans | engaged time, subscriptions, return visits |
| Portfolio/agency/studio | immersive | distinctive (typographic, dark mono, playful 3D) | qualified enquiries, awards |
| Booking/travel/hospitality | expressive (brand) · subtle (booking) | photo-led editorial, utilitarian OTA | search → book conversion, cancellation rate |
| Food delivery/marketplace | subtle–expressive | appetising photo + warm accents | orders per user, reorder rate, delivery-time NPS |
| Real estate | subtle (portal) · expressive–immersive (luxury project) | utilitarian / luxury editorial | qualified leads, viewings booked |
| Gaming/entertainment/streaming | immersive (launch) · expressive (browse) · subtle (player) | dark cinematic | watch/play time, wishlists, churn |
| Productivity/dev tools | subtle (product) · expressive (marketing) | Swiss or terminal-inspired, dark | time-to-first-success, weekly active, paid conversion |
| AI products | subtle (product) · expressive–immersive (marketing) | neutral + AI identifier colour | task success, accepted-output rate, retention |
| Internal enterprise | none–subtle | utilitarian compact | task time, error rate |
| Government/public | none | GOV.UK-style plain | completion rate, digital take-up, cost per transaction |
| Beauty & personal care | expressive (brand, PDP media) · subtle (shade finder, regimen, checkout) · none (claims, warnings) | clinical-minimal, luxury editorial serif, botanical spa, playful colour | conversion, shade-swap/return rate, repeat and refill purchase rate |

## Pitfalls

| Symptom | Cause | Fix |
|---|---|---|
| Users miss specs/reviews on PDP | Content hidden in horizontal tabs | Expanded sections (desktop), collapsed sections (mobile) — Baymard |
| Checkout abandonment spikes at payment step | Shipping/fees revealed late | Show cost estimate on PDP and total in cart; delivery date per option |
| Dashboard "looks busy" but nobody acts | All KPIs same weight, no comparison window, colour-only status | 4–6 KPIs, explicit "vs period", icons/signs + colour, sort bars |
| Page feels broken on fast networks | Skeleton/spinner flashes for < 1 s loads | Delay indicator ~1 s or skip; skeleton only for full-page loads |
| Users report nausea / leave story pages | Parallax and scroll-linked motion with no off switch | Respect `prefers-reduced-motion`; provide static version (WCAG 2.3.3) |
| AI answers trusted blindly or dismissed | No citations, no limitation statement, uncalibrated confidence | Inline citations to passages, upfront caveat, verification step for actions |
| Users can't stop a runaway generation | Send button not swapped to Stop during `submitted`/`streaming` | Bind Stop to `stop()`; keep partial output with Retry |
| Health reminders leak sensitive info | PHI in SMS/push preview | Generic text ("You have a new message") + authenticated deep link |
| Gov form abandoned midway | Multi-question pages, asterisks, timeout without save | One thing per page, "(optional)" labels, save-and-return, timeout warning |
| Immersive site unusable on mid-range phones | 3D scene loaded at full quality for every device | Device-tier detection, lite 2D mode, poster fallback (`3d-webgl.md`) |
| Drop-day complaints: "the timer was wrong", "I lost my place", "bots got everything" | Countdown from the device clock; queue state held only in the client; allocation model not stated | Server-time countdown + absolute time; server-held entry/queue state; draw or random waiting room with per-account limits stated up front (§4 drops) |
| Beauty ad pulled or notification at risk (Thailand) | Medical verbs (treat, cure, heal), internal-use or injection claims, unsubstantiated before/after | Appearance wording only, evidence file per claim, Thai FDA advertising guidelines, counsel review (§19) |

## Sources

- Tilleke & Gibbins — Thailand: operationalising PDPA lawful basis, sensitive personal data and safeguards — https://www.tilleke.com/insights/thailand-operationalising-pdpa-lawful-basis-sensitive-personal-data-and-data-processing-safeguards/
- NN/g — Response Times: The 3 Important Limits — https://www.nngroup.com/articles/response-times-3-important-limits/
- NN/g — Progress Indicators Make a Slow System Less Insufferable — https://www.nngroup.com/articles/progress-indicators/
- NN/g — Skeleton Screens 101 — https://www.nngroup.com/articles/skeleton-screens/
- NN/g — Executing UX Animations: Duration and Motion Characteristics — https://www.nngroup.com/articles/animation-duration/
- NN/g — Dashboards: Making Charts and Graphs Easier to Understand — https://www.nngroup.com/articles/dashboards-preattentive/
- NN/g — Data Tables: Four Major User Tasks — https://www.nngroup.com/articles/data-tables/
- NN/g — Choosing Chart Types — https://www.nngroup.com/articles/choosing-chart-types/
- NN/g — 8 Design Guidelines for Complex Applications — https://www.nngroup.com/articles/complex-application-design/
- Laws of UX — Doherty Threshold — https://lawsofux.com/doherty-threshold/
- W3C — Understanding SC 2.3.3 Animation from Interactions — https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html
- Baymard — Cart Abandonment Rate statistics — https://baymard.com/lists/cart-abandonment-rate
- Baymard — Cart & Checkout UX research — https://baymard.com/research/checkout-usability
- Baymard — Checkout flow average form fields — https://baymard.com/research-articles/checkout-flow-average-form-fields
- Baymard — Make guest checkout prominent — https://baymard.com/research-articles/make-guest-checkout-prominent
- Baymard — Shipping speed vs delivery date — https://baymard.com/research-articles/shipping-speed-vs-delivery-date
- Baymard — Show shipping costs on product pages — https://baymard.com/research-articles/show-shipping-costs-on-product-pages
- Baymard — Product page UX research — https://baymard.com/research/product-page
- Baymard — Avoid horizontal tabs — https://baymard.com/research-articles/avoid-horizontal-tabs
- Baymard — In-scale product images — https://baymard.com/research-articles/in-scale-product-images
- Baymard — Product lists & filtering research — https://baymard.com/research/ecommerce-product-lists
- Baymard — 5 essential filters — https://baymard.com/research-articles/5-essential-filters
- Baymard — Ways to instill trust — https://baymard.com/research-articles/ways-to-instill-trust
- Baymard — Food delivery & takeout UX benchmark 2026 — https://baymard.com/research-articles/food-delivery-and-takeout-ux-benchmark-2026
- Apple HIG — Generative AI (change log 2025-06-09, 2026-06-08) — https://developer.apple.com/design/human-interface-guidelines/generative-ai
- Microsoft HAX Toolkit — Guidelines for Human-AI Interaction — https://www.microsoft.com/en-us/haxtoolkit/library/
- Shape of AI — AI UX pattern catalog — https://www.shapeof.ai/
- AI SDK — Generative User Interfaces — https://ai-sdk.dev/docs/ai-sdk-ui/generative-user-interfaces
- AI SDK — useChat reference — https://ai-sdk.dev/docs/reference/ai-sdk-ui/use-chat
- GOV.UK — Government Design Principles — https://www.gov.uk/guidance/government-design-principles
- GOV.UK Design System — Question pages — https://design-system.service.gov.uk/patterns/question-pages/
- GOV.UK Design System — Error summary — https://design-system.service.gov.uk/components/error-summary/
- GOV.UK Design System — Check answers — https://design-system.service.gov.uk/patterns/check-answers/
- GOV.UK Design System — Focus states — https://design-system.service.gov.uk/get-started/focus-states/
- GOV.UK — Use clear language — https://guidance.publishing.service.gov.uk/writing-to-gov-uk-standards/writing-guidelines/clear-language/
- NHS digital service manual — How we write — https://service-manual.nhs.uk/content/how-we-write
- Wikipedia — Health Insurance Portability and Accountability Act — https://en.wikipedia.org/wiki/Health_Insurance_Portability_and_Accountability_Act
- GDPR Art. 9 — Processing of special categories of personal data — https://gdpr-info.eu/art-9-gdpr/
- Thailand PDPC office — https://www.pdpc.or.th/
- Microsoft — Xbox Accessibility Guidelines — https://learn.microsoft.com/en-us/xbox/accessibility/guidelines
- Game Accessibility Guidelines — https://gameaccessibilityguidelines.com/
- Awwwards — Annual Awards hall of fame (2022–2025 winners) — https://www.awwwards.com/annual-awards/hall-of-fame
- The FWA — awards timeline (public JSON used by thefwa.com) — https://thefwa.com/
- Nike — How can I join a SNKRS Draw? — https://www.nike.com/help/a/nike-snkrs-draw
- Nike — SNKRS Draw rules and terms (UK) — https://www.nike.com/gb/help/a/nike-launch-drawing
- Nike — SNKRS web feed (Feed / In Stock / Upcoming) — https://www.nike.com/launch
- END. — Proudly introducing END. Launches (10 Apr 2019) — https://www.endclothing.com/us/features/proudly-introducing-end-launches
- END. — All launches (release timestamps in page data, checked 2026-10-10) — https://www.endclothing.com/gb/launches/all-launches
- Sole Retriever — END. raffle review (22 Jul 2021) — https://www.soleretriever.com/news/articles/end-raffle-review
- Cloudflare — Waiting Room queueing methods — https://developers.cloudflare.com/waiting-room/reference/queueing-methods/
- Cloudflare — Waiting Room events (pre-queue, shuffle at event start) — https://developers.cloudflare.com/waiting-room/additional-options/create-events/
- deceptive.design — Fake urgency — https://deceptive.design/types/fake-urgency/ ; Fake scarcity — https://deceptive.design/types/fake-scarcity/
- Aimé Leon Dore — store ("My Sizes", "Hide sold out products") — https://www.aimeleondore.com/
- Thai FDA — No advertising licence required for cosmetics, but truthful and lawful claims are a must (8 Sep 2025) — https://en.fda.moph.go.th/news/thai-fda-reminds-no-advertising-license-required-for-cosmetics-but-truthful-and-lawful-claims-are
- Thai FDA — Citizen's manual: requesting an opinion on cosmetic advertising (Thai PDF) — https://cms-media.fda.moph.go.th/461117737616416768/2023/03/5BE7vSiP09ihs53mk4vmOYez.pdf
- Thai FDA — Automated cosmetic notification manual (Thai PDF: Act definitions, Thai label, PIF, SPF 50+) — https://cms-media.fda.moph.go.th/461117737616416768/2023/03/SRjK3RexrQvvzHsCZe0AvxNS.pdf
- Thai FDA regional office — Q&A cosmetic notification 2567 (Thai PDF: receipts valid 3 years) — https://ccowgroup.moph.go.th/fda8riew/wp-content/uploads/2026/02/FAQ-จดแจ้งเครื่องสำอาง.pdf
- Tilleke & Gibbins — Amendments to Cosmetics Act introduce renewal requirements and fees (5 Oct 2015) — https://www.tilleke.com/insights/amendments-cosmetics-act-introduce-renewal-requirements-and-fees/
- ChemLinked — Thailand expands rules on unacceptable cosmetic advertising claims (3 Dec 2024) — https://cosmetic.chemlinked.com/news/cosmetic-news/thailand-expands-rules-on-unacceptable-cosmetic-advertising-claims
- ChemLinked — Thailand issues guidance on inappropriate cosmetic advertising claims (26 Aug 2026; details behind free login) — https://cosmetic.chemlinked.com/news/cosmetic-news/thailand-issues-guidance-on-inappropriate-cosmetic-advertising-claims
- ChemLinked — Thai FDA guidance on notification and claims for whitening and anti-acne products (9 Sep 2026; details behind free login) — https://cosmetic.chemlinked.com/news/cosmetic-news/thailand-fda-issues-guidance-on-cosmetic-notification-and-claims-for-whitening-and-anti-acne-products
- ChemLinked Cosmepedia — Thailand cosmetic regulation (label elements, claim evidence, updated 21 Aug 2026) — https://cosmetic.chemlinked.com/cosmepedia/thailand-cosmetic-regulation
- Beauty product examples checked 2026-10-10 (The Ordinary, Paula's Choice, Fenty Beauty, Rare Beauty, Le Labo, Oriental Princess, PAÑPURI, Sunnies Face) — URLs in `inspiration.md` "Commerce, streetwear and beauty product references"
