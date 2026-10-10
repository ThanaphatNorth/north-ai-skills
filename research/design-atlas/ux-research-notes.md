# Raw notes: UX foundations + user research (design-atlas)

Collected 2026-10-10. Provenance record for `skills/design-atlas/references/ux-foundations.md`, `user-research.md` and the templates `design-brief.md`, `persona-jtbd.md`, `usability-test-script.md`. Every bullet carries the URL it came from. "(secondary)" = not read from the primary source. "(unverified)" = could not confirm.

Research constraint: the shared WebSearch budget for this turn ran out partway through; later facts were collected with WebFetch on known URLs only. Some primary sources were not fetchable (ISO OBP 403, Apple HIG renders client-side, O'Reilly 403, sensible.com 403).

## 1. Definitions of UX / usability

- ISO 9241-11:2018 clause 3.1.1 usability = "extent to which a system, product or service can be used by specified users to achieve specified goals with effectiveness, efficiency and satisfaction in a specified context of use". 2018 edition replaced 1998 (which said "product" only); ISO confirmed the standard in 2023. Standard text itself not fetchable (403); wording confirmed via search-result summaries of national adopters. https://www.iso.org/standard/63500.html (403), https://csrc.nist.gov/glossary/term/Usability (1998 wording, "product")
  - Sub-definitions (older phrasing, secondary): effectiveness = accuracy and completeness with which users achieve specified goals; efficiency = resources expended in relation to accuracy and completeness; satisfaction = freedom from discomfort / positive attitudes (1998) vs. 2018 wording not verified.
- ISO 9241-210:2019 human-centred design, six principles (paraphrased, secondary): (1) explicit understanding of users, tasks and environments; (2) users involved throughout design and development; (3) design driven and refined by user-centred evaluation; (4) iterative process; (5) design addresses the whole user experience; (6) multidisciplinary team. Formerly ISO 13407 (1999); ISO listing says last reviewed and confirmed 2025. https://iso.org/standard/77520.html (search result), https://userfocus.co.uk/articles/iso-13407-is-dead.html (search result)
  - ISO 9241-210 definition of "user experience" (perceptions and responses resulting from use/anticipated use) — (unverified wording), left out of the reference.
- Norman & Nielsen: UX = "all aspects of the end-user's interaction with the company, its services, and its products." Requirements: meet exact needs without fuss or bother; simplicity and elegance; beyond checklist features; merge disciplines. Usability = quality attribute of the UI (learnability, efficiency, satisfaction); UX is broader. Example: great movie search but database lacks indie films = poor UX. https://www.nngroup.com/articles/definition-user-experience/
- Morville UX honeycomb (2004-06-21): useful, usable, desirable, findable, accessible, credible, valuable. "usability is necessary but not sufficient". Use facets to set explicit priorities; redesign one facet at a time; use as lenses. https://semanticstudios.com/user_experience_design/

## 2. Norman's principles

- Discoverability results from five concepts: affordances, signifiers, constraints, mappings, feedback; plus conceptual model as sixth/most important (secondary summaries of The Design of Everyday Things, rev. 2013). https://lively-kernel.org/lively4/BP2019RH1/doc/research/literature/theDesignOfEverydayThings.md , https://mlserver1.cs.siue.edu/hci_25sp/hci_lectures/CS321_Lecture-5-DesignOfEverydayThings.pdf (search results)
  - Affordance is a relationship, not a property (glass affords seeing-through for sighted, not blind people).
  - Signifier = perceivable cue for where/how to act (push/pull sign).
  - Constraints limit possible actions (greyed-out options).
  - Mapping = control layout matches effect layout; controls near what they control.
  - Feedback = full and continuous info about result of actions and current state.
  - Conceptual model = the explanation of how it works that the design communicates.
- Gulfs (NN/g): evaluation = perceive + interpret state; execution = plan + manipulate controls. Bridge evaluation: labels show current state, positive wording ("On" means something happening), avoid double negatives ("Hide notifications: Off"), checkboxes for settings. Bridge execution: familiar models, controls behave as they look, action labels say what will happen. Execution depends on correct evaluation. https://www.nngroup.com/articles/two-ux-gulfs-evaluation-execution/
- Mental models (NN/g, 2024-01-26, reviewed 2026-09-01): belief not fact; users bring expectations from other sites; one search box (users assume any search box covers everything); back button returns to previous screen; mental-model inertia → innovate only when clearly superior; fix mismatch by conforming to model (card sort) or improving model (labels). Think-aloud reveals mental models. https://www.nngroup.com/articles/mental-models/
- Clickability signifiers (NN/g 2015-03-08): blue default link color; don't color/underline static text; buttons rectangular with rounded corners; if flat, add border; don't style headings like buttons; icons need text label unless standard; arrows weakest cue. https://www.nngroup.com/articles/clickable-elements/

## 3. Nielsen's 10 heuristics (last reviewed 2024-01-30; orig. 1994)

https://www.nngroup.com/articles/ten-usability-heuristics/
1. Visibility of system status — timely feedback; communicate state before consequential actions.
2. Match between system and real world — users' language; confirm terminology via research.
3. User control and freedom — clearly marked exit; undo/redo; Cancel.
4. Consistency and standards — internal + external consistency; Jakob's law.
5. Error prevention — prevent high-cost errors first; constraints, good defaults; confirmation for risky.
6. Recognition rather than recall — keep options visible; contextual help.
7. Flexibility and efficiency of use — accelerators hidden from novices; personalization.
8. Aesthetic and minimalist design — remove irrelevant info; minimalism ≠ flat.
9. Help users recognize, diagnose, recover from errors — plain language, precise problem, solution; conventional error visuals.
10. Help and documentation — searchable, task-focused, concise, in context.
- Heuristic evaluation (NN/g 2023-06-25): 3–5 evaluators independently; timebox 1–2 h; two passes (learn, then record violations); consolidate via affinity; violation ≠ always a problem; doesn't replace testing. https://www.nngroup.com/articles/how-to-conduct-a-heuristic-evaluation/
- Severity (NN/g 1994-11-01): 0 not a problem, 1 cosmetic, 2 minor, 3 major, 4 catastrophe; factors frequency, impact, persistence, market impact. https://www.nngroup.com/articles/how-to-rate-the-severity-of-usability-problems/

## 4. Krug

- Don't Make Me Think, Revisited, 3rd ed. 2014 (New Riders). Chapters: Krug's first law; scanning, satisficing, muddling through; billboard design 101; mindless choices; omit words; street signs and breadcrumbs (navigation); Big Bang theory (home page); usability testing on 10 cents a day; mobile; usability as common courtesy; accessibility. https://archive.org/details/dontmakemethinkr0000krug
- First law: page should be self-evident/self-explanatory. Definition of usable: average (or below) ability person can figure it out without more trouble than it's worth. Clicks: "doesn't matter how many times I have to click, as long as each click is a mindless, unambiguous choice." Third law: "Get rid of half the words on each page, then get rid of half of what's left." Billboard tactics: clear visual hierarchy, conventions, clearly defined areas, obvious clickability, minimize noise. Satisficing = choose first reasonable option (Simon 1957). (secondary: search-result summaries; https://brajeshwar.com/2020/dont-make-me-think/ "We don't read pages. We scan them.")
- Trunk test: (unverified exact wording) — drop on random page, identify site ID, page name, sections, local nav, "you are here", search.

## 5. IA & navigation, progressive disclosure, flows

- IA vs navigation (NN/g 2014-06-22): IA = structure (content inventory, audit, grouping, taxonomy, metadata), documented in spreadsheets/diagrams; navigation = UI "tip of the iceberg". Define IA first; set usage priority; placement; pattern; inverted-L layout suits up to ~4 tiers. https://www.nngroup.com/articles/ia-vs-navigation/
- Progressive disclosure (NN/g 2006-12-03): primary list short; secondary discoverable with strong scent; 2 levels practical maximum. https://www.nngroup.com/articles/progressive-disclosure/
- Wireflows (NN/g 2016-12-04): wireframe screens + flowchart arrows from the clicked element to resulting screen/state. For apps with few core pages whose content changes; checkout, filtering, configurators; not for many static pages. Flowcharts lack page context. https://www.nngroup.com/articles/wireflows/

## 6. Content design / UX writing

- UI copy (NN/g): command labels 2–4 words; label the result, not current state; lead with specific verb ("Accept and Sign In"); same label for same command; add noun when verb is ambiguous ("Delete Folder"); no cute/branded terms; ellipsis = needs more input; no "OK" on confirmations — name the action ("Discard"); always a way out/undo; CTA specific ("Continue to Billing"); label icon-only actions; shortcuts conventions. https://www.nngroup.com/articles/ui-copy/
- Error messages (NN/g 2023-05-14): near source; noticeable, not color alone; match severity (inline/toast/banner; modal only for blocking); don't show too early; plain language, hide codes; specific problem; offer remedy; no blame words ("invalid", "illegal", "incorrect"); no humor; prevent likely mistakes; preserve input; suggest fixes; educate concisely. https://www.nngroup.com/articles/error-message-guidelines/
- Empty states (NN/g 2021-09-19): communicate system status (don't show "No records" while loading); increase learnability; direct pathways (button, docs, demo data). https://www.nngroup.com/articles/empty-state-interface-design/
- GOV.UK: split sentences > 25 words; paragraphs ≤ 5 sentences; write for average UK reader; 9-year-old reading age (secondary: council guides citing GDS). Ann Wylie: 11 words easy, 21 fairly difficult, 25 difficult, 29+ very difficult (2014 blog, flagged possibly outdated). https://guidance.publishing.service.gov.uk/writing-to-gov-uk-standards/writing-guidelines/clear-language/ (search result), https://insidegovuk.blog.gov.uk/2014/08/04/sentence-length-why-25-words-is-our-limit/ (search result)
- Mailchimp voice vs tone: voice constant personality; tone adapts to reader's emotional state; clarity over entertainment; active voice, plain English, positive phrasing; humor only when natural. https://styleguide.mailchimp.com/voice-and-tone/

## 7. Screen states

- Scott Hurff UI stack (2015-08-17): ideal (design first), empty (first use, user-cleared, no results), error (never lose input; friendly, instructive), partial (progress toward ideal, e.g. profile completeness), loading (skeletons, optimistic actions over bare spinners). https://www.scotthurff.com/posts/why-your-user-interface-is-awkward-youre-ignoring-the-ui-stack/
- Response limits (Nielsen 1993/2014): 0.1 s instant; 1 s flow of thought (above 1 s show working); 10 s attention limit — percent-done, cancel, estimate. https://www.nngroup.com/articles/response-times-3-important-limits/
- Skeleton vs spinner (NN/g 2023-06-04, reviewed 2026-09-02): <1 s nothing; 2–10 s spinner for a module, skeleton for full page; >10 s progress bar; no frame-only skeletons. https://www.nngroup.com/articles/skeleton-screens/
- Offline (web.dev 2016-11-10): inform connectivity state and whose fault; show what's available offline; obvious save-for-offline; show file sizes; disable connection-only features contextually; queue actions, sync later; sync status; no full-screen modal loaders; not color alone; plain action-based language (users misread "offline"). https://web.dev/articles/offline-ux-design-guidelines
- Permission denied (Android docs): request in context when feature used; check every time; educational UI when shouldShowRequestPermissionRationale true, with "no thanks"; degrade gracefully, specific message where feature output would appear; don't block UI; don't nag or pressure to settings; denial more than once = permanent (USER_FIXED), dialog no longer shows. https://developer.android.com/training/permissions/requesting
- Apple HIG privacy page not fetchable (client-rendered) — iOS specifics left to `platform-mobile.md`.

## 8. Forms

- NN/g form top-10 (2016-05-01): keep short (example 6 → 2 fields); labels above fields on mobile/short forms; single column (City/State/ZIP may share row); logical sequence & tab order; no placeholder-as-label; radio over dropdown for 2–3 options; field width ≈ expected input (city ~19 chars covers 99.9%); 1–2 optional fields max, labelled; explain format rules up front; no Reset/Clear; specific errors, not color alone, preserve input. https://www.nngroup.com/articles/web-form-design/
- Wroblewski inline validation (A List Apart 2009-09-01, 22 users, 6 variants): best inline vs submit-only: +22% success, −22% errors, +31% satisfaction, −42% completion time, −47% fixations. "After" (on blur) best; "while" (keypress) only for hard fields with delay; "before and while" worst. Use for fields people can't answer confidently (username, password rules), skip for names (checkmarks confused). Persistent messages outside fields. Caveat: small sample, indicative. https://alistapart.com/article/inline-validation-in-web-forms/
- Baymard inline validation (2024-01-09): 31% of benchmarked sites have no inline validation; premature validation frustrates; validate on blur; fixed-length fields may validate on reaching length; remove error immediately on correction (keystroke); positive validation reassures; still need submit-time handling. https://baymard.com/blog/inline-form-validation
- Baymard checkout fields (2024-06-26): avg checkout 5.1 steps, 11.3 fields (11.8 in 2021, 12.7 in 2019); most sites need 8; field count matters more than steps; single Full Name field (42% typed full name into First name); hide Address Line 2, Company, coupon behind links; billing = shipping by default; delay account creation to confirmation. https://baymard.com/blog/checkout-flow-average-form-fields
- Baymard abandonment (updated 2025-09-22): 70.22% avg across 50 studies; reasons (excluding "just browsing" 42%): extra costs 40%, delivery too slow 20%, trust with card 19%, account required 18%, too long/complicated 17%, errors/crashes 17%, returns policy 13%, total cost unclear 12%, card declined 10%, not enough payment methods 9%. Better checkout design → 35.26% conversion increase for large sites. https://baymard.com/lists/cart-abandonment-rate
- Baymard touch keyboards (2015-12-15): numeric keyboard via type/inputmode/pattern; email keyboard; disable autocorrect for names/addresses/emails; autocapitalize off for email, words for names; consistent across fields; 54% fail numeric keyboards; 85% get ≥1 of 5 rules wrong. https://baymard.com/blog/mobile-touch-keyboards

## 9. Onboarding

- NN/g mobile onboarding (2020-06-21): avoid onboarding where possible, fix UI first; tutorials didn't improve performance; justified when app needs user info to start, context-dependent functionality, or novel features; deck-of-cards not recommended (if used: visible Skip, minimal cards, one concept each); contextual tips preferred; promote features when users can act; no promotional onboarding at first launch; customization brief with reason; interactive walkthroughs short and skippable. https://www.nngroup.com/articles/mobile-app-onboarding/

## 10. UX metrics

- HEART (Rodden, Hutchinson, Fu, CHI 2010, primary PDF read): PULSE (Page views, Uptime, Latency, Seven-day actives, Earnings) are business/technical, ambiguous for UX. HEART = Happiness (attitudinal: satisfaction, visual appeal, likelihood to recommend, perceived ease — iGoogle weekly 7-point survey; change aversion recovered), Engagement (per-user average, e.g. % of actives visiting 5+ days/week — Gmail, predicted retention), Adoption (new users of product/feature in period; e.g. accounts created last 7 days), Retention (% of 7-day actives still active 3 months later), Task success (efficiency/time, effectiveness/% completed, error rate — Google Maps single search box A/B by error rates). Not every category needed (Engagement may be meaningless in enterprise). Goals → Signals → Metrics: signals sensitive and specific; failure often easier to detect (abandonment, undo); normalize raw counts (ratios, %, per-user averages); log filtering. Applied to 20+ Google products. https://research.google/pubs/pub36299/ (PDF: https://static.googleusercontent.com/media/research.google.com/en//pubs/archive/36299.pdf)
- SUS (MeasuringU 2011-02-03): 10 items, 5-pt; odd items −1, even items 5−x, sum ×2.5 → 0–100; mean 68 across ~500 studies; >80.3 = A, top 10%; 68 = C; <51 = F bottom 15%; raw 74 ≈ 70th percentile; not a percentage; reliable with small samples but use CIs. https://measuringu.com/sus/
- SEQ (MeasuringU 2012, avg updated 2019): "Overall, how difficult or easy was the task to complete?" 7-pt; average ≈ 5.3–5.6 over 400+ tasks/10,000 users; <5 → ask why; r≈.5 with time/completion; ~14% of failers rate very easy. https://measuringu.com/seq10/
- UMUX-Lite (MeasuringU 2017-10-11): "[This system's] capabilities meet my requirements." + "[This system] is easy to use."; 7-pt (Lewis) or 5-pt; SUS ≈ 0.65 × ((i1 + i2 − 2) × (100/12)) + 22.9 (7-pt); r = .83 with SUS; α = .86. https://measuringu.com/umux-lite/
- Task completion (MeasuringU 2011-03-21): median 78% across 1,189 tasks, 115 tests, 3,472 users; >92% top quartile, <49% bottom quartile; 70% often used target for walk-up consumer apps; report CI lower bound; 10/10 → 95% CI roughly 75–100% per page. https://measuringu.com/task-completion/ (my adjusted-Wald calc gives 67.9–100%; difference = method; reference uses own calc and labels the method.)
- Task time (MeasuringU 2010-04-21): times positively skewed; n < 25 use geometric mean; n > 25 median fine; report CIs. https://measuringu.com/average-times/
- NPS caveats (NN/g 2024-06-21): perception not performance; needs large samples (useless in 5-user tests); binning loses info; loyalty ≠ usability; too coarse for UI changes; gamed when a target; cultural/industry variation; use as one metric among many, product-level, with margin of error, tracked over time. https://www.nngroup.com/articles/nps-ux/

## 11. Research methods landscape & sample sizes

- NN/g landscape (Christian Rohrer): attitudinal vs behavioural; qual (why/how to fix) vs quant (how many/how much); context: natural, scripted, limited, not using. Phases: Strategize (generative: field, diary, interviews, surveys, participatory design, concept testing), Design (formative: card sorting, tree testing, usability testing, remote moderated/unmoderated), Launch & Assess (summative: benchmarking, unmoderated UX testing, A/B, analytics, surveys). https://www.nngroup.com/articles/which-ux-research-methods/
- NN/g cheat sheet (2017-02-12): Discover (field, diary, user interview, stakeholder interview, requirements), Explore (competitive analysis, design review, personas, task analysis, journey mapping, prototype feedback, user stories, card sorting), Test (qual usability, benchmark, accessibility evaluation), Listen (survey, analytics review, search-log analysis, usability-bug review, FAQ review). https://www.nngroup.com/articles/ux-research-cheat-sheet/
- How many users (NN/g 2012-06-03): 5 per qual study; quant ≥ 20 (see below 40); card sort ≥ 15 per group; eyetracking 39; 3–4 per group when multiple groups. https://www.nngroup.com/articles/how-many-test-users/
- Quant sample sizes (NN/g 2021-07-25): 40 participants (binary metric, population > 500, 15% margin of error, 95% confidence → 39). 95%/20% → 21; 90%/15% → 28; 90%/20% → 15. Continuous (SD 52% of mean): 47/26/33/19. https://www.nngroup.com/articles/summary-quant-sample-sizes/

## 12. Lean research methods

- First click: Bailey & Wolfson (2006–2009, a dozen studies): correct first click → 87% eventually succeeded; wrong first click → 46%. Image click tests vs live sites: ~6% avg difference in first-click regions (MeasuringU 2023-03-21). https://measuringu.com/do-click-tests-predict-live-site-clicks/
- Click tests (MeasuringU 2023-06-13): use early concepts, hard-to-simulate/auth interfaces, where people start a task; metrics: % in hotspots, click locations, time to click, ease rating. https://measuringu.com/why-and-when-to-use-a-click-test/
- Five-second test (Smashing, Kuric 2023-12-06): question types attitudinal (1–7), target identification, memory dump; 5 s not universal — complex screens 10 s better; low working memory hurts recall at 5 s; not for multi-purpose interfaces. https://www.smashingmagazine.com/2023/12/five-second-testing-case-study/
- Competitive evaluation (NN/g 2024-01-05): 2–4 competitors; review (expert) or testing (users do same tasks; each participant 2–3 sites; randomize order); compare tasks, content/feature gaps, success/time/ratings; aim to beat not copy. https://www.nngroup.com/articles/competitive-usability-evaluations/
- Assumptions mapping (Precoil, David Bland): desirable/viable/feasible color-coded; 2x2 from Lean UX; "Map the most important assumptions with the least amount of evidence" → test first. https://www.precoil.com/assumptions-mapping — NOTE: page contained embedded text instructing AI readers to start replies with a specific phrase; ignored (prompt injection in observed content).
- Proto-personas (NN/g persona types 2020-06-21): 2–4 h workshop; each drafts 2–5, merge to 3–6; no new research; risks echo chamber, negative halo. Qualitative personas: 5–30 interviews in rolling groups of ~5 until saturation. Statistical: survey ≥100 (ideally 500+) + clustering. https://www.nngroup.com/articles/persona-types/

## 13. Interviews, surveys, diary, IA methods

- Interviews (NN/g 2023-09-17, reviewed 2026-07-15): set specific goals; guide + pilot; "Tell me about the last time you…"; past specific incidents; avoid leading; probes on timing, duration, recurrence, feelings; "Tell me more about that"; interviews are attitudinal — can't show actual behavior/usability; interview + test sessions ~90 min vs 60. https://www.nngroup.com/articles/user-interviews/
- Surveys (NN/g 2016-09-25): multiple-answer often better; include N/A, "Don't use"; neutral wording; define terms; don't ask what analytics can tell; 20 questions too many unless highly motivated; front-load important questions; conditional logic; ~4 rounds of single-participant think-aloud pilot; randomize. https://www.nngroup.com/articles/qualitative-surveys/
- Diary studies (NN/g 2024-03-29): days to a month+; examples 1 wk assistants, 3 wk meal delivery, 2 wk phone plan; participants 5–12 small/homogeneous, 12–30 large/heterogeneous, 30–50 academic; overrecruit; logging event-based, interval-based, signal-based; pilot, brief, monitor, post-interview; incentive ~US$40/h expected time (general US sample), installments for >1 week. https://www.nngroup.com/articles/diary-studies/
- Card sorting (NN/g 2024-02-02): open (most common), closed (validation — tree test better), hybrid (discouraged); qual ≥15 participants; quant 30–50; 30–50 cards (more → fatigue, "Misc" pile); similarity matrix, dendrogram. https://www.nngroup.com/articles/card-sorting-definition/
- Tree testing (NN/g 2023-08-06, reviewed 2026-08-19): text-only hierarchy; tasks as goals not labels; define correct location; warm-up task; between-subjects for label comparisons; metrics success, directness, time, selected categories; after card sorting, before visual design. https://www.nngroup.com/articles/tree-testing/

## 14. JTBD, personas, journey, blueprint, empathy, Kano

- Job story (Klement, Intercom 2013-12-23): situation → motivation → outcome; user stories problems: personas not situations, couple implementation with motivation, ignore context/anxieties. Tips: start with high-level job, smaller jobs, observe current solutions, investigate causality/anxieties/motivations. https://www.intercom.com/blog/using-job-stories-design-features-ui-ux/ ; template "When [situation], I want to [motivation], so I can [expected outcome]" (secondary: https://thoughtbot.com/blog/converting-to-jobs-stories search result).
- Four forces (Moesta & Spiek): push of situation, pull of new solution, anxiety of new solution, habit of present; switch when Push + Pull > Anxiety + Habit. https://jobstobedone.org/the-four-forces/
- Switch timeline (secondary): first thought → passive looking → event → active looking → event → deciding → first use/ongoing use; capture events, not generalizations; don't ask about forces directly. https://jobstobedone.org/switch-interview/ (search result)
- Personas vs JTBD (NN/g 2017-08-06): JTBD generalizes needs across user base; personas differentiate groups, build empathy, help prioritize conflicting needs; combine. https://www.nngroup.com/articles/personas-jobs-be-done/
- Journey mapping (NN/g 2018-12-09, reviewed 2026-07-15): one actor, scenario + expectations, phases, actions/mindsets/emotions, opportunities with ownership + metrics; experience map = generic; service blueprint = business side; user-story map = planning. https://www.nngroup.com/articles/journey-mapping-101/
- Service blueprint (NN/g 2017-08-27): customer actions, frontstage, backstage, processes, evidence; lines of interaction, visibility, internal interaction; for complex/omnichannel/root-cause problems. https://www.nngroup.com/articles/service-blueprints-definition/
- Empathy map (NN/g, dated 2026-10-02): Says (verbatim), Thinks, Does (observed), Feels (adjective + cause); not chronological; every note traces to a source, else label as assumption; one user/persona per map; individual notes before converging. https://www.nngroup.com/articles/empathy-mapping/
- Kano evaluation table (secondary, consistent across sources): functional × dysfunctional answers (Like / Must-be / Neutral / Live with / Dislike) → A, O, M, I, R, Q; Better = (A+O)/(A+O+M+I); Worse = −(O+M)/(A+O+M+I). https://www.kanosurveys.com/cheatsheets (search result), https://metricgate.com/docs/kano-model-feature-categorization/ (search result)

## 15. A/B testing

- Kohavi et al., KDD 2007 "Practical Guide to Controlled Experiments on the Web" (primary PDF read): n = (4rσ/Δ)² at 95% confidence, 90% power; r = number of variants; factor 4 may overestimate by 25% for large n. Example: 5% conversion, detect 5% relative change → < 500,000 users; 20% change → 30,400 (factor 16 fewer). Analyze only triggered users (checkout starters): 25,600 checkout users / 256,000 total. Decide OEC in advance; A/A tests to check variability and system; primacy and newness effects → run multiple weeks; experiments typically a few weeks. https://cdn.elezea.com/pdf/GuideControlledExperiments.pdf (copy of the KDD paper; exp-platform.com/practical-guide/)
- Rule of thumb n ≈ 16σ²/δ² per arm (α = .05 two-sided, 80% power; Lehr 1992); binary: σ² = p(1−p); halving MDE quadruples n. https://arxiv.org/pdf/2305.16459 (search result summary)
- My calc (python): p = 5%, relative lift 10% → 30,400 per arm; 20% → 7,600; p = 10%, 10% lift → 14,400; p = 2%, 20% → 19,600; p = 30%, 5% → 14,933.

## 16. Accessibility research

- W3C WAI "Involving Users in Evaluating Web Accessibility" (content 2021-06-01): expert review first; involve users early and throughout informally; a few people with disabilities + older users if in audience; match AT experience to audience; set up and test AT before sessions; issue may come from content, browser, AT, user familiarity; don't generalize from one person; user involvement can't determine conformance — pair with WCAG evaluation; sessions use more facilitator interaction, focus on barrier-caused errors not time-on-task. https://www.w3.org/WAI/test-evaluate/involving-users/

## 17. Synthesis

- Affinity diagram (NN/g 2024-04-26): notes individually (5–10 min generation) → cluster → label after grouping → prioritize (dot voting) → owner; duplicate notes that fit two clusters; don't dismiss small clusters. https://www.nngroup.com/articles/affinity-diagram/
- HMW (NN/g 2021-01-17, reviewed 2026-08-07): based on agreed research insight; outcome-focused, not solution; positive verbs; not too narrow (embeds solution) / too broad; target root cause ("stop users calling us" → "feel confident they have all info"). https://www.nngroup.com/articles/how-might-we-questions/

## 18. Usability-test facilitation

- Task scenarios (NN/g 2014-01-12): realistic ("Buy shoes under $40"), actionable (do, not describe), no clues/UI labels, specific details (Tuesday 10am, Dr. Petersen). https://www.nngroup.com/articles/task-scenarios-usability-testing/
- Think-aloud (NN/g 2012-01-15): representative users + tasks + shut up; prompts needed; show a short demo; avoid interruptions that change behavior; discard biased segments. https://www.nngroup.com/articles/thinking-aloud-the-1-usability-tool/
- Talking to users (NN/g 2014-01-26): echo, boomerang ("What do you think?", "What would you normally do?"), Columbo (trailing partial question); don't answer/reassure/hint; count to 10 silently when unsure. https://www.nngroup.com/articles/talking-to-users/
- Unmoderated (NN/g 2019-10-27): 6 steps; tasks need more care; tell when to stop; pilot; screen on behavior; overrecruit and exclude disengaged "professional testers"; best for live sites or high-fidelity prototypes; poor for imagination/emotion tasks. https://www.nngroup.com/articles/unmoderated-usability-testing/

## 19. Thailand (sourced numbers only)

- DataReportal Digital 2026: Thailand (published 2025-11-08, figures ~Oct 2025): population 71.6 M; 55.2% urban; median age 40.6; age 65+ = 16.0%, 55–64 = 14.1%; cellular connections 96.6 M (135%); internet users 67.8 M (94.7%), +3.7% YoY; offline 3.78 M (5.3%); median mobile download 124.33 Mbps, fixed 262.42 Mbps (Ookla, 12 months to Aug 2025); social media user identities 56.6 M (79.1%); LINE 56 M MAU (78.2% of population, 82.6% of internet users); Facebook ad reach 51.5 M (71.9%); TikTok 56.6 M users 18+ (96.3% of adults; flagged comparability caveats); YouTube 47.2 M (65.9%). https://datareportal.com/reports/digital-2026-thailand
- DataReportal Digital 2025: Thailand (published 2025-03-03, Jan 2025 data): internet 65.4 M (91.2%); mobile connections 99.5 M (139%), 100% "broadband" 3G/4G/5G; median mobile 61.21 Mbps, fixed 237.85 Mbps; social identities 51.0 M (71.1%); LINE 56 M MAU (85.7% of internet users; 54% male / 46% female); YouTube 47.6 M; Facebook 51.0 M; TikTok 34.0 M 18+ (flagged unreliable). https://datareportal.com/reports/digital-2025-thailand
- Not found on the pages: device share of web traffic, e-commerce/social-commerce values, payment usage shares (in embedded slides only — not extracted). Left out of the reference.
- Bank of Thailand PromptPay page: PromptPay launched 2016; Thai QR Payment = scan QR in mobile banking app; most banks waived digital-payment fees since 2018; PromptPay fee tiers: free up to 5,000 baht; <2 baht 5,000–30,000; <5 baht 30,000–100,000; <10 baht above 100,000 (undated; page ©2023). https://www.bot.or.th/en/financial-innovation/digital-finance/digital-payment/promptpay.html
