# Psychology of people using interfaces

> Read when: choosing layout, hierarchy, defaults, copy, onboarding, pricing, checkout, retention or engagement mechanics; justifying a design decision with a named principle; reviewing a flow for cognitive load, persuasion ethics, deceptive patterns or trust; deciding whether a "growth tactic" is legal and fair.

**Contents:** Laws of UX catalog · Gestalt grouping · Cognitive load · Attention, hierarchy and reading patterns · Behaviour models (Fogg, Tiny Habits, Hooked, SDT) · Persuasion (Cialdini) used ethically · Cognitive biases designers use · Emotional design and delight · Trust and credibility · Colour psychology, with caveats · Deceptive patterns and the law · Gamification that respects users · Goal → principle → tactic map · Pitfalls · Sources

Related: accessibility rules are in `accessibility.md`; colour systems in `color.md`; type and spacing scales in `typography-layout.md`; flows and IA in `ux-foundations.md`; testing these claims with users in `user-research.md`; motion timing in `motion.md`; onboarding/pricing/checkout patterns in `product-patterns.md`.

Evidence grading used below: **[strong]** replicated, large effects · **[mixed]** real but moderated or contested · **[heuristic]** useful rule of thumb, weak lab evidence. Treat every principle as a hypothesis to test in your product, not a guarantee.

## Laws of UX catalog

All 30 entries on lawsofux.com as of 2026-10-10.

| Law | What it means | UI tactic |
|---|---|---|
| Aesthetic-usability effect | Attractive UIs are *perceived* as easier; users forgive minor (not major) problems. Kurosu & Kashimura 1995 | Polish the primary flow first. In tests, score what users *do*, not their praise of visuals |
| Choice overload [mixed] | Many options can cause deferral and regret, mainly when options are complex, the task is hard, preferences are unclear, or the user wants low effort | When users don't know what they want: 3–5 curated options + "Recommended" + compare. Large catalogues are fine when search and filters are strong |
| Chunking | Grouping items into meaningful units | Format codes `4242 4242 4242 4242`, phone `081 234 5678`; split long forms into titled sections; group nav into labelled clusters |
| Cognitive bias | Systematic errors in judgement | Design defaults and framing deliberately (see biases section); review every bias-based tactic against the deceptive-patterns list |
| Cognitive load | Mental resources needed to use the UI | Cut extraneous load (see Cognitive load section) |
| Doherty threshold | Interaction stays productive when the system responds in under 400 ms (Doherty & Thadani 1982) | Pressed state < 100 ms, result or skeleton < 400 ms, optimistic UI for likely-success writes, progress indicator past ~1 s |
| Fitts's law | Time to hit a target grows with distance, shrinks with size | Primary action big and near the thumb/pointer; targets ≥ 24×24 CSS px (WCAG AA), 44×44 pt iOS, 48×48 dp Android; keep destructive actions away from frequent ones |
| Flow | Absorbed focus when challenge matches skill | Remove interruptions from the core task; give immediate feedback; defer upsell modals until after task completion |
| Goal-gradient effect | Effort rises as the goal gets closer | Step indicator "Step 2 of 3"; start progress above zero; show "1 more to unlock" |
| Hick's law | Decision time grows with number and complexity of choices | One visually recommended option; progressive disclosure; split into steps. Don't simplify into ambiguity (icon-only nav) |
| Jakob's law | Users expect your product to work like the ones they already use | Logo → home top-left, cart/account top-right, magnifier = search, swipe-back on iOS. Innovate in value, not in navigation. After a redesign, offer a temporary "old version" toggle or guided tour |
| Common region | Items inside one boundary read as a group | Cards and tinted panels for related controls; enclose payment card fields in their own panel |
| Proximity | Near items read as a group | Within-group gap clearly smaller than between-group gap (e.g. 8 vs 24 px); label sits closer to its own input than to the previous field |
| Prägnanz | Ambiguous shapes are read in their simplest form | Simple, closed icon silhouettes; avoid overlapping shapes that can parse two ways |
| Similarity | Items that look alike are assumed to act alike | One style per behaviour: every link one style, every primary button one style; never style static text like a link |
| Uniform connectedness | Visually connected items read as most related | Connector lines in steppers and timelines; active tab visually joined to its panel |
| Mental model | Users' compressed belief of how the system works | Use users' vocabulary (card sort, interviews); keep the same model across web and mobile |
| Miller's law [heuristic] | ~7±2 items in short-term memory (Miller 1956) | Chunk; do **not** use "7" as a hard cap on nav or options |
| Occam's razor | Prefer the simplest solution that works | Remove elements until the task breaks, then add the last one back; one way to do each thing |
| Paradox of the active user | People skip manuals and start using at once | Contextual tips at the point of need, teaching empty states, no mandatory tour |
| Pareto principle | ~80% of effects from ~20% of causes | Find the 20% of features in 80% of sessions (analytics) and optimise those first |
| Parkinson's law | Work expands to fill the time available | Show honest effort estimates ("about 2 min"); autofill to shorten tasks; never fake countdowns |
| Peak-end rule [strong] | Experiences are remembered by their most intense moment and their end | Design the success screen and the worst moment (errors, payment failure) on purpose; no "please don't go" guilt on cancel |
| Postel's law | Accept liberally, output conservatively | Accept `081-234-5678`, `0812345678`, `+66 81 234 5678`; trim spaces; parse dates in several formats; display one canonical format |
| Selective attention | People attend to goal-relevant stimuli and skip the rest | Never make real content look like an ad; put critical info in the task path; animate or highlight changes users must notice |
| Serial position effect | First and last items are remembered best | Put key nav items at the ends of tab bars and menus; key facts at the start and end of lists |
| Tesler's law | Irreducible complexity: the system or the user must carry it | Detect card brand from digits, city from postcode, timezone from device; smart defaults |
| Von Restorff effect | The item that differs is remembered | Exactly one high-emphasis CTA per view; signal difference with shape/size/label too, not colour alone |
| Working memory | Holds ~4–7 chunks for ~20–30 s | Recognition over recall: keep order summary visible, comparison tables, visited-link styles, breadcrumbs |
| Zeigarnik effect [heuristic] | Unfinished tasks stay on the mind (1920s study; replication evidence mixed, unverified this session) | Resume-where-you-left-off, saved drafts, profile completeness. Don't invent fake incompleteness to nag |

## Gestalt grouping

When cues conflict, explicit connection (lines, shared containers) usually overrides proximity, and proximity usually overrides similarity (Palmer's grouping studies; not re-verified this session). To fix ambiguous grouping, add a container or connector rather than nudging colours.

| Principle | Use it to | Check |
|---|---|---|
| Proximity | Group label+field, icon+caption, card content | Squint test: do clusters match meaning? |
| Similarity | Signal same behaviour (all links, all chips) | Does anything look clickable that isn't? |
| Common region | Group controls into cards, panels, table rows | Are borders/backgrounds doing grouping that spacing could do more quietly? |
| Uniform connectedness | Steps, timelines, flows, tab-to-panel | Lines connect only related items |
| Closure | Minimal icons, partially visible carousel item (signals "scroll for more") | Shape still reads at 16 px |
| Continuity | Align items on one axis so the eye follows | Ragged left edges break scanning |
| Figure/ground | Modals and sheets over a dimmed page | Scrim strong enough to separate layers; see `accessibility.md` for contrast |
| Common fate | Items that move together belong together (drag a group, list reorder) | Respect reduced-motion |
| Symmetry/order | Calm, trustworthy layouts (finance, health) | Asymmetry used only for emphasis |
| Prägnanz | Simple shapes are processed fastest | Icons tested without labels for recognition |

## Cognitive load

Three types (Sweller's cognitive load theory): **intrinsic** = complexity of the task itself (can't remove, can sequence); **extraneous** = effort spent on the interface, not the goal (remove); **germane** = effort spent learning a reusable model (support it, e.g. worked examples in onboarding).

Cut extraneous load:
1. Remove decoration that carries no meaning (font-style variety, gratuitous icons, redundant links).
2. Build on existing mental models: standard labels ("Sign in", "Cart"), platform components.
3. Offload work to the system: smart defaults, autofill (`autocomplete` tokens), re-display what the user entered, derive what you can (Tesler).
4. Recognition over recall: show options, recent items, previous values; never make users copy a code from one screen to another (also WCAG 3.3.7/3.3.8, see `accessibility.md`).
5. One primary decision per screen in high-stakes flows (checkout, consent, medical).
6. Sequence intrinsic load: progressive disclosure, "Advanced" sections, step-by-step wizards for rare complex tasks; single page for frequent short tasks.
7. Plain language: short sentences, common words, active voice; define jargon inline.
8. Stable layout: no shifting content, no auto-advancing carousels during reading.

Quick audit: count, per screen, (a) things the user must remember from earlier screens, (b) distinct visual styles for the same role, (c) decisions required. Drive (a) to 0 and (c) to 1 for core flows.

## Attention, hierarchy and reading patterns

Visual hierarchy levers, strongest first: size → contrast/colour weight → position (top/left in LTR) → whitespace isolation → motion (use sparingly; it also triggers banner blindness and vestibular issues). Rule: one focal point per view, at most three emphasis levels (primary / secondary / tertiary).

NN/g eyetracking scanning patterns (2019 synthesis):

| Pattern | When it happens | Design response |
|---|---|---|
| F-pattern (worst) | Wall of unformatted text, user wants speed, low commitment | Put key points in the first two paragraphs; front-load headings so the first 2 words carry meaning; bold key phrases; bullets; cut text |
| Spotted | User hunts for a specific thing (number, name, link) | Make targets visually distinct: descriptive link text, numbers as digits, bold key terms |
| Layer-cake (best scanning) | Strong headings and subheadings exist | Write headings that answer "is this section for me?"; one idea per section |
| Commitment | Motivated user reads everything | Still chunk; motivation comes from trust and relevance |

"Z-pattern" is a designer heuristic for sparse pages (logo → nav → hero → CTA), not one of NN/g's eyetracking findings; use it only for low-text landing layouts. RTL languages mirror these patterns.

Banner blindness (NN/g 1997, 2007, 2018): users ignore anything that looks like an ad — top banners, right rails, animated boxes, items near ads, and on mobile large images. Do: style announcements like content, place them inline in the task path, test that users actually see them. Avoid: making important notices flashy to "stand out" — that makes them look like ads.

Response-time limits (Nielsen): 0.1 s feels instant; 1 s keeps flow; 10 s keeps attention. Over ~10 s show percent-done plus Cancel; 2–10 s a busy indicator; unknown duration → show what is being processed.

## Behaviour models

### Fogg Behavior Model: B = MAP
Behaviour happens when **Motivation**, **Ability** and a **Prompt** converge at the same moment. If a behaviour isn't happening, diagnose which is missing.
- Motivation core motivators: sensation (pleasure/pain), anticipation (hope/fear), belonging (acceptance/rejection). Motivation fluctuates, so **raise ability first**.
- Ability = simplicity, limited by the scarcest resource now: time, money, physical effort, brain cycles, social deviance, non-routine.
- Prompt type must match the state: **Spark** (able, not motivated) → prompt + reason/benefit; **Facilitator** (motivated, finds it hard) → prompt + easier path (one-tap, prefilled); **Signal** (both present) → plain reminder.
- Diagnostic: user abandons at a step → ability problem (simplify). User never starts → motivation or prompt problem. Reminder ignored → wrong prompt type or bad timing.

### Tiny Habits recipe (for habit features)
"After I **[existing anchor]**, I will **[tiny behaviour < 30 s]**, then I celebrate." In product: attach prompts to an existing routine (after morning alarm, after logging a meal), make the first version tiny (log one glass of water, not a full diary), and give instant positive feedback within seconds.

### Hooked model (Eyal) — use with an ethics gate
Trigger (external → internal) → Action (easy) → Variable reward (tribe, hunt, self) → Investment (data, content, reputation that improves the next loop).
Ethics gate before shipping any loop: (1) Would you use it yourself? (2) Does it materially improve the user's life (Eyal's Manipulation Matrix)? (3) Would the user endorse the loop if shown how it works? (4) Is there a natural stopping point? Variable rewards borrow gambling mechanics; avoid them in products for minors, health, finance and anything compulsive. The EU's planned Digital Fairness Act targets "addictive design" (see law table).
Ethical alternatives: predictable rewards tied to real progress; investment that benefits the user (their own data, portable/exportable); internal triggers tied to genuine need ("check my blood pressure log") not boredom.

### Self-Determination Theory for engagement
Durable engagement comes from satisfying three needs; extrinsic rewards that feel controlling can undermine intrinsic motivation (overjustification; Deci, Koestner & Ryan 1999 meta-analysis).

| Need | Design for it | Undermines it |
|---|---|---|
| Autonomy | Real choices, skippable steps, user-set goals and reminder times, easy opt-out | Forced flows, guilt copy, streak shaming, defaults the user can't find |
| Competence | Clear feedback, optimal challenge, visible mastery (skills unlocked, "you've improved 12%") | Points for mere presence, opaque scores, punishing errors |
| Relatedness | Real people, shared goals, helpful community, caring tone | Fake social activity, leaderboards that rank strangers against beginners |

## Persuasion (Cialdini) used ethically

Rule: a principle is ethical when the underlying fact is **true**, the user would **endorse** the influence if they saw it, and the choice stays **reversible**.

| Principle | Ethical UI use | Crosses the line when |
|---|---|---|
| Reciprocity | Give real value first: free tier, useful tool, template, content without a wall | The "gift" creates obligation through guilt or hides a charge |
| Commitment & consistency | Start with a small, genuine step (pick a goal) that leads into the larger one; show the user their own stated goal later | Pre-ticked commitments; "You said yes earlier" traps |
| Social proof | Real counts, verified reviews with negatives visible, "popular with teams like yours" | Fabricated activity ("12 people viewing"), cherry-picked or bought reviews |
| Authority | Real credentials, reviewer names with qualifications, standards met | Fake badges, actors in lab coats, implied endorsements |
| Liking | Friendly, human tone; photos of the real team | Flattery used to push an upsell |
| Scarcity | Truthful stock or capacity limits, real deadlines | Fake timers that reset, invented "only 2 left" |
| Unity | Shared identity that actually exists ("built by nurses for nurses") | Counterfeit belonging; "people like us buy this" |

## Cognitive biases designers actually use

| Bias | Evidence | Ethical tactic | Manipulative version (avoid) |
|---|---|---|---|
| Default effect | [strong] Johnson & Goldstein 2003: opt-out vs opt-in organ-donor registration differed massively | Default to the option most users would choose and that protects them (privacy-on, auto-save on, cheapest adequate plan) | Pre-ticked marketing consent (invalid under GDPR), default add-ons |
| Anchoring | [strong] Tversky & Kahneman 1974 | Show the reference price that is real; show plans high-to-low only if that is the honest comparison | Inflated "was" prices never charged |
| Framing | [strong] | Frame for comprehension: "9 in 10 patients" and "1 in 10" side by side for health risk; absolute numbers over relative | One-sided framing of risk to sell |
| Loss aversion | [mixed] Kahneman & Tversky 1979; size contested (Gal & Rucker 2018) | Remind users what they would lose by not saving work | "You'll lose everything" cancel flows, confirmshaming |
| Decoy / asymmetric dominance | [mixed] Huber, Payne & Puto 1982 | Present a genuinely useful middle plan; label "Most popular" only if true | Fake third plan that exists only to push the target |
| Choice overload | [mixed] pooled effect near zero (Scheibehenne 2010), significant under complexity, unclear preferences (Chernev 2015) | Curate when users are novices; allow full catalogue + filters for experts | Hiding the cheapest option to "reduce choice" |
| Endowed progress | [mixed] Nunes & Drèze 2006: card with 2 of 10 pre-stamped → 34% redemption vs 19% for empty 8-stamp card | Credit real completed steps ("Account created ✓" as step 1 of 4) | Fake progress that resets |
| Goal-gradient | [mixed] mostly animal evidence (Hull 1932) plus loyalty studies | Visible progress, "1 step left" | Moving the goal post |
| IKEA effect | [strong] Norton, Mochon & Ariely 2012; only when the build succeeds | Let users customise and assemble (templates, dashboards) with guaranteed success | Making users work so they feel locked in |
| Labour illusion | [mixed] Buell & Norton 2011: showing work done raised perceived value even with ~60 s waits | For genuinely slow work, show real steps ("Checking 12 airlines…") | Adding fake delays to fast operations |
| Social proof | [strong] | Real numbers, recent real reviews | Fabricated counters |
| Commitment/consistency | [strong] | Let users state a goal, then remind them of it | Using a past "yes" to justify a new charge |

## Emotional design and delight

Norman's three levels (Emotional Design, 2004):
- **Visceral** (first impression, < 1 s): colour, imagery, type, polish. Sets trust and expectation.
- **Behavioural** (use): speed, feedback, control, error recovery. Most of the experience lives here.
- **Reflective** (meaning): identity, story, status, values. Can make users tolerate behavioural flaws, but not forever.

Delight (NN/g 2017): **deep delight** comes only after functionality → reliability → usability are solid; **surface delight** (animation, witty microcopy, illustrations, sounds) on a broken foundation reads as fake.
- Delight goes in success states, empty states, first-run, milestones. Keep it out of errors involving money, health, data loss, or anything the user is anxious about.
- Repeated delight decays into annoyance: a celebration that plays every time becomes friction. Show elaborate celebrations once (first time, milestones), make repeats short and subtle (sub-second, no blocking), and let users turn sounds/animations off.
- Serious domains (bank, hospital, government): delight = speed, clarity, reassurance, not jokes.

## Trust and credibility

Stanford Web Credibility Guidelines (Fogg, 2002), as a checklist: (1) verifiable claims with citations; (2) show a real organisation (address, registration); (3) show expertise (credentials); (4) show honest people (real bios/photos); (5) easy contact (phone, email, address); (6) professional design appropriate to purpose; (7) easy to use and useful; (8) fresh content or "last reviewed" dates; (9) restraint with ads and promos, clearly labelled; (10) zero typos, broken links, layout glitches.

Checkout (Baymard 2025: 19% of US shoppers abandoned a checkout in the last 3 months because they didn't trust the site with card details):
- Enclose card fields in a visually distinct panel used only for payment; 1–2 recognisable seals and a padlock *inside* that panel; reassuring microcopy ("Encrypted. We never store your full card number" — only if true).
- Show total cost incl. shipping and tax before the payment step; no surprise fees (also a deceptive pattern).
- Fix visual bugs: a broken layout at payment looks like phishing.
- Show return policy, delivery date and contact options near the pay button.

Health: named clinical reviewer with credentials and "Medically reviewed on <date>"; sources linked; clear "not a substitute for professional advice" placed where decisions happen; explicit data-use statement before collecting health data; no fear-based urgency.

Finance: regulator/licence identifiers where applicable; fee tables in plain numbers; consistent figures across screens; confirm before irreversible transfers with a summary (also WCAG 3.3.4); never animate balances in a way that hides the value.

## Colour psychology, with caveats

Evidence is weak and context-bound. Reviews (Elliot & Maier 2014; Elliot 2015) describe an early-stage field with methodological weaknesses; many findings ("blue calms", "red lowers test scores") were tested on one or two hues (Holcombe 2019), and at least one high-profile colour-perception paper was retracted (2015). Rules:
- Choose colour for **contrast, consistency and convention**, not claimed emotional effects. A/B test any "colour boosts conversion" claim in your own product; the winning button usually won by contrast and isolation, not hue.
- Learned conventions are stronger than innate effects: red = error/destructive, green = success, amber = warning in most software; keep them, and pair with icons and text (colour-blind users; see `accessibility.md`).
- Culture changes meaning (general knowledge, not sourced this session): white is associated with mourning in parts of East and South Asia, red with luck and celebration in Chinese contexts; in Thailand colours carry day-of-week and political associations. Check locale meanings with local users before brand decisions.
- Finance/stock UIs: the red = down / green = up convention is reversed in some East Asian markets (e.g. mainland China, South Korea show red = up; unverified this session) — confirm for the target market and always add arrows/signs.
- Brand fit beats "psychology": pick the hue that differentiates in the category, then build the palette in `color.md`.

## Deceptive patterns and the law

Taxonomy from deceptive.design (18 types, 2026-10-10), each with the fair alternative:

| Pattern | Fair alternative |
|---|---|
| Sneaking (info hidden or delayed) | Show material terms before commitment |
| Forced action | Let users finish the task; make extras optional |
| Hard to cancel | Cancel in the same channel and number of steps as sign-up |
| Preselection | Unticked boxes for optional extras and consent; neutral defaults |
| Obstruction | Shortest path to the user's goal, including leaving |
| Hidden subscription | Label recurring charges, amount, frequency and renewal date at the CTA |
| Hidden costs | All-in price from the first price shown |
| Trick wording | One question, one meaning; no double negatives ("Uncheck to not receive") |
| Visual interference | Equal visual weight for "Accept" and "Reject" choices |
| Fake social proof | Only real, verifiable activity and reviews |
| Fake urgency | Real deadlines only; timers that don't reset |
| Nagging | Ask once; respect "No" for a meaningful period; offer "Don't ask again" |
| Fake scarcity | Real inventory only |
| Disguised ads | Label sponsored content clearly |
| Confirmshaming | Neutral decline copy: "No thanks" |
| Comparison prevention | Comparable units, side-by-side plan tables |
| Addictive design | Natural stopping points, usage summaries, off-by-default autoplay |
| Currency confusion | Show real-money equivalents next to virtual currency |

Legal landscape (as of 2026-10-10; not legal advice — escalate to counsel):

| Jurisdiction | Rule | Design implication |
|---|---|---|
| EU GDPR Art. 7 | Consent request clearly distinguishable, plain language; "as easy to withdraw as to give consent"; service can't be conditional on unnecessary processing | Reject button as prominent as Accept; withdrawal reachable in the same number of clicks; no pre-ticked boxes |
| EU EDPB Guidelines 03/2022 (v2.0, Feb 2023) | Categories of deceptive patterns in social media: overloading, skipping, stirring, obstructing, fickle, left in the dark | Use as a review checklist for any privacy flow |
| EU DSA Art. 25 | Online platforms must not design interfaces that deceive, manipulate or materially distort free decisions; guidance targets undue prominence, repeated requests, cancellation harder than sign-up | A Dutch court (Oct 2025) treated resetting a non-profiled feed choice on reopen as a dark pattern: persist user choices |
| EU DMA Art. 13 | Gatekeepers may not circumvent obligations via interface design or non-neutral choice presentation | Neutral choice screens |
| EU Digital Fairness Act | Proposal expected Q4 2026 (reported for November 2026); aims at dark patterns, addictive design, subscriptions | Design for it now: easy cancel, no fake urgency |
| US FTC | 2024 "click-to-cancel" rule vacated by the 8th Circuit on 8 July 2025 (procedural); FTC restarted rulemaking (ANPRM 11 March 2026). ROSCA still requires clear disclosure before billing info, express informed consent, simple cancellation; FTC continues enforcement. Some states (e.g. California) have their own click-to-cancel laws | Build to the stricter standard: online cancel as easy as sign-up, consent checkbox for recurring charges |

## Gamification that respects users

Use game elements to make **real progress visible**, not to manufacture compulsion.
- Map each mechanic to an SDT need: progress bars and levels → competence; choice of goals, quests, avatar → autonomy; teams and shared goals → relatedness.
- Octalysis "white hat" drives (meaning, accomplishment, creativity/feedback) build durable motivation; "black hat" drives (scarcity, unpredictability, loss avoidance) create urgency and burnout. Use black-hat drives sparingly, briefly and honestly, never as the core loop.
- Streaks: add streak freezes or "rest days", show longest streak not just current, never shame on break. Health apps: never streak medication or calorie restriction.
- Leaderboards: default to friends or personal bests; let users opt out of public ranking; bracket by level so beginners aren't last forever.
- Rewards: reward mastery and outcomes, not attendance; avoid expected tangible rewards for activities users already enjoy (overjustification).
- Badges must mean something a user would tell someone about; drop badges nobody views (check analytics).
- No loot boxes, random paid rewards or virtual currency that hides real cost (currency confusion).

## Goal → principle → tactic map

| Goal | Principles | Tactics |
|---|---|---|
| Increase sign-up completion | Fogg ability, Hick, Tesler, endowed progress, commitment | Social sign-in and passkeys; ask only email first, rest later; progress "Step 1 of 3" starting from a completed step; inline validation; show value before the form |
| Reduce errors | Postel, Fitts, recognition over recall, Jakob | Forgiving input parsing; large spaced targets; pickers over free text for constrained values; undo instead of confirm for reversible actions; confirm with summary for irreversible ones |
| Build trust | Stanford guidelines, aesthetic-usability, peak-end | Real people and credentials; all-in price early; secure-looking payment panel; polished, bug-free checkout; clear confirmation and receipt |
| Increase retention | SDT, Tiny Habits, Zeigarnik, peak-end | Anchor reminders to user routines with user-set times; show progress toward user-chosen goals; resume where they left off; strong, honest milestone moments |
| Speed decisions | Hick, choice overload, defaults, von Restorff | One recommended option highlighted; comparison table with 3–5 rows that matter; sensible default; filters for experts |
| Increase feature adoption | Paradox of the active user, Fogg prompts, selective attention | Contextual prompt at the moment of need (facilitator); in-flow hints, not tours; avoid ad-like banners |
| Reduce support load | Mental models, cognitive load, COGA | Users' vocabulary in labels; help in the same place on every page (WCAG 3.2.6); error messages that say how to fix |
| Raise perceived speed | Doherty, labour illusion, goal-gradient | Skeletons < 400 ms, optimistic UI; for long jobs, real step-by-step progress with cancel |
| Ethical upsell | Reciprocity, timing (flow), peak-end | Offer after success, not mid-task; one clear dismiss; remember "no" |

## Pitfalls

| Symptom | Cause | Fix |
|---|---|---|
| A/B "win" from red button disappears next quarter | Novelty and contrast, not hue psychology | Test contrast/isolation; re-run before generalising |
| Users praise the redesign but task success fell | Aesthetic-usability effect masks problems | Judge by task metrics and observation, not post-task ratings |
| Big catalogue cut to 6 items, conversion dropped | Choice overload assumed, but users knew what they wanted | Restore range, add search/filters, curate only for novices |
| Announcement banner nobody sees | Banner blindness: placement and ad-like styling | Inline in task flow, content styling, verify with tests |
| Nav cut to exactly 7 items "because Miller" | Misused 7±2 | Size nav from task analysis and card sorting |
| Engagement up, complaints and churn up later | Black-hat loops, guilt copy, nagging | Run the ethics gate; measure retention at 90 days, not clicks |
| Legal flags on consent flow | Unequal Accept/Reject, pre-ticked boxes, hard withdrawal | Equal-weight buttons, opt-in, withdraw in same number of steps |
| Fake progress or delay noticed by users | Labour illusion faked | Only show real work; never slow down fast operations |
| Streak feature causes anxiety reviews | Loss aversion as core loop | Streak freezes, rest days, no shaming |

## Sources

- Laws of UX — https://lawsofux.com/
- Laws of UX detail pages: Miller's law https://lawsofux.com/millers-law/ · Working memory https://lawsofux.com/working-memory/ · Doherty threshold https://lawsofux.com/doherty-threshold/ · Zeigarnik https://lawsofux.com/zeigarnik-effect/ · Goal-gradient https://lawsofux.com/goal-gradient-effect/ · Aesthetic-usability https://lawsofux.com/aesthetic-usability-effect/ · Hick's law https://lawsofux.com/hicks-law/ · Fitts's law https://lawsofux.com/fittss-law/ · Tesler's law https://lawsofux.com/teslers-law/
- IxDF, Gestalt principles — https://ixdf.org/literature/topics/gestalt-principles
- NN/g, Minimize Cognitive Load (2013) — https://www.nngroup.com/articles/minimize-cognitive-load/
- NN/g, Text Scanning Patterns: Eyetracking Evidence (2019) — https://www.nngroup.com/articles/text-scanning-patterns-eyetracking/
- NN/g, F-Shaped Pattern of Reading on the Web — https://www.nngroup.com/articles/f-shaped-pattern-reading-web-content/
- NN/g, Banner Blindness Revisited (2018) — https://www.nngroup.com/articles/banner-blindness-old-and-new-findings/
- NN/g, Response Times: The 3 Important Limits — https://www.nngroup.com/articles/response-times-3-important-limits/
- NN/g, Aesthetic-Usability Effect (2024, reviewed 2026) — https://www.nngroup.com/articles/aesthetic-usability-effect/
- NN/g, The Peak–End Rule (2018) — https://www.nngroup.com/articles/peak-end-rule/
- NN/g, A Theory of User Delight (2017) — https://www.nngroup.com/articles/theory-user-delight/
- Fogg Behavior Model — https://behaviormodel.org/ · prompts https://behaviormodel.org/prompts/ · ability https://behaviormodel.org/ability/ · motivation https://behaviormodel.org/motivation/
- BJ Fogg, Fogg Behavior Model: Ability (simplicity factors) — https://www.behaviormodel.org/ability
- Tiny Habits examples — https://themeaningmovement.com/tiny-habits
- Hooked summary — https://www.supersummary.com/hooked/background/ · critique, Per Axbom — https://axbom.com/nir-eyal-habit-danger/
- Self-Determination Theory — https://selfdeterminationtheory.org/theory/
- Cialdini unity and ethics (ASU, 2025) — https://blogs.wpcarey.asu.edu/20250422-gentle-science-persuasion-part-seven-unity · CXL on unity — https://conversionxl.com/cialdini-unity/
- Scheibehenne et al. 2010, choice overload meta-analysis — https://ideas.repec.org/a/oup/jconrs/v37y2010i3p409-425.html
- Chernev et al. 2015, choice overload moderators — https://www.kellogg.northwestern.edu/faculty/research/detail/2015/when-product-assortment-leads-to-choice-overload-a-conceptual
- Nunes & Drèze (2006), The Endowed Progress Effect, J. Consumer Research 32(4) 504–512, doi:10.1086/500480 — https://ideas.repec.org/a/oup/jconrs/v32y2006i4p504-512.html
- Buell & Norton 2011, labour illusion — https://pubsonline.informs.org/doi/fpi/10.1287/mnsc.1110.1376
- Norton, Mochon & Ariely 2012, IKEA effect — https://dash.harvard.edu/handle/1/12136084
- Defaults and organ donation — https://thedecisionlab.com/insights/health/can-defaults-save-lives-the-power-of-default-options-on-life-saving-decisions · caveat https://marginalrevolution.com/marginalrevolution/2018/08/presumed-consent-wales-falls-short.html
- Norman's three levels — https://ixdf.org/literature/article/norman-s-three-levels-of-design
- Stanford Guidelines for Web Credibility — https://credibility.stanford.edu/guidelines/index.html
- Baymard, Perceived security of payment form — https://baymard.com/blog/perceived-security-of-payment-form
- Elliot & Maier 2014, Color psychology — https://www.doi.org/10.1146/ANNUREV-PSYCH-010213-115035 · Elliot 2015 review — https://www.frontiersin.org/articles/10.3389/fpsyg.2015.00368/full · Holcombe critique — https://open.lnu.se/index.php/metapsychology/article/view/1652 · retraction discussion — https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4979646/
- Deceptive.design types — https://www.deceptive.design/types
- FTC, Bringing Dark Patterns to Light (2022) — https://www.ftc.gov/reports/bringing-dark-patterns-light
- Greenberg Traurig, 8th Circuit vacates click-to-cancel (2025) — https://www.gtlaw.com/en/insights/2025/7/eighth-circuit-vacates-ftcs-click-to-cancel-rule
- Gibson Dunn, FTC restarts negative option rulemaking (2026) — https://www.gibsondunn.com/ftc-restarts-negative-option-rulemaking-after-eighth-circuit-vacatur-enforcement-under-rosca-continues/
- GDPR Art. 7 — https://gdpr-info.eu/art-7-gdpr/
- DSA Art. 25 — https://www.springlex.eu/en/packages/dsa/dsa-regulation/article-25/ · Amsterdam court commentary (DLA Piper) — https://www.dlapiper.com/insights/blogs/mse-today/2025/the-amsterdam-court-putting-the-dsa-into-practice
- DMA Art. 13 — https://streamlex.eu/articles/dma-en-art-13/
- EDPB 03/2022 summary — https://activemind.legal/guides/dark-patterns
- European Parliament Legislative Train, Digital Fairness Act — https://www.europarl.europa.eu/legislative-train/theme-protecting-our-democracy-upholding-our-values/file-digital-fairness-act
- Octalysis framework — https://yukaichou.com/gamification-examples/octalysis-complete-gamification-framework/
