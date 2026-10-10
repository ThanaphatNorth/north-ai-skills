# Raw notes: psychology of interfaces and accessibility (design-atlas)

Collected 2026-10-10 for `skills/design-atlas/references/psychology.md` and `accessibility.md`.
Each bullet carries the URL it came from. "(secondary)" = law firm, vendor or blog summary, not the primary text.
"(general knowledge)" = well-known academic citation not re-opened this session; no URL is claimed for it.

Research limits: the shared WebSearch budget ran out mid-session (limit 200 per turn across agents). After that, only WebFetch on known URLs was used. Topics hit by the cut-off: NN/g Gestalt article, NN/g emotional design, HONcode status, Zeigarnik replication meta-analysis, Thai screen-reader products beyond NVDA/VoiceOver.

---

## 1. Laws of UX (lawsofux.com), full list as of 2026-10-10

Source: https://lawsofux.com/ (30 entries)

1. Aesthetic-Usability Effect: attractive design is perceived as more usable.
2. Choice Overload: people get overwhelmed by many options.
3. Chunking: break information into meaningful groups.
4. Cognitive Bias: systematic errors of thinking that shape perception and decisions.
5. Cognitive Load: mental resources needed to understand and use an interface.
6. Doherty Threshold: productivity rises when system and user interact under 400 ms.
7. Fitts's Law: time to acquire a target depends on its distance and size.
8. Flow: energised focus and full immersion in an activity.
9. Goal-Gradient Effect: the drive toward a goal increases with proximity to it.
10. Hick's Law: decision time grows with the number and complexity of choices.
11. Jakob's Law: users expect your site to work like the sites they already know.
12. Law of Common Region: elements inside a clearly bounded area are grouped.
13. Law of Proximity: near objects are grouped.
14. Law of Prägnanz: ambiguous images are read in their simplest form.
15. Law of Similarity: similar elements are grouped even when separated.
16. Law of Uniform Connectedness: visually connected elements are seen as more related.
17. Mental Model: a compressed model of how we think a system works.
18. Miller's Law: average working memory holds 7 (±2) items.
19. Occam's Razor: prefer the hypothesis with the fewest assumptions.
20. Paradox of the Active User: users never read manuals, they start using the software at once.
21. Pareto Principle: about 80% of effects come from 20% of causes.
22. Parkinson's Law: a task inflates until all available time is spent.
23. Peak-End Rule: experiences are judged by the peak and the end.
24. Postel's Law: be liberal in what you accept, conservative in what you send.
25. Selective Attention: we focus only on stimuli tied to our goals.
26. Serial Position Effect: first and last items in a series are best remembered.
27. Tesler's Law: every system has irreducible complexity that can only be shifted.
28. Von Restorff Effect: the item that differs is most likely to be remembered.
29. Working Memory: system that temporarily holds and manipulates task information.
30. Zeigarnik Effect: uncompleted or interrupted tasks are remembered better.

Detail pages read:
- Miller's Law (https://lawsofux.com/millers-law/): Miller 1956. Takeaway: don't use "magical number seven" to justify unnecessary limits; chunk; capacity varies by person and context.
- Working Memory (https://lawsofux.com/working-memory/): holds about 4 to 7 chunks; each fades after about 20 to 30 s. Recognition beats recall. Mark visited links, breadcrumbs, carry critical info across screens (comparison tables).
- Doherty Threshold (https://lawsofux.com/doherty-threshold/): Doherty & Thadani, IBM Systems Journal 1982; set requirement at 400 ms replacing the 2 s standard. Takeaways: feedback within 400 ms, perceived performance, progress bars help even when inaccurate, a deliberate delay can raise perceived value.
- Zeigarnik (https://lawsofux.com/zeigarnik-effect/): Bluma Zeigarnik, 1920s. Takeaways: signal more content exists, artificial progress, clear progress indicators.
- Goal-Gradient (https://lawsofux.com/goal-gradient-effect/): Clark Hull 1932 (rats 1934). Page notes it is mostly studied in animals; human implications less explored. Further reading: Kivetz, Urminsky & Zheng, "The Goal-Gradient Hypothesis Resurrected".
- Aesthetic-Usability (https://lawsofux.com/aesthetic-usability-effect/): Kurosu & Kashimura, Hitachi, 1995; 26 ATM layouts, 252 participants; appeal correlated more with perceived than actual ease of use.
- Hick's Law (https://lawsofux.com/hicks-law/): Hick & Hyman 1952. Takeaways: minimise choices when speed matters, break tasks into steps, highlight recommended options, progressive onboarding. Caveat: "Be careful not to simplify to the point of abstraction."
- Fitts's Law (https://lawsofux.com/fittss-law/): Paul Fitts 1954; speed-accuracy trade-off. Large targets, spacing, reachable placement.
- Tesler's Law (https://lawsofux.com/teslers-law/): Larry Tesler, Xerox PARC, mid-1980s; "spend an extra week" rather than make millions spend an extra minute. Absorb complexity; contextual help.

## 2. Gestalt

- IxDF Gestalt topic (https://ixdf.org/literature/topics/gestalt-principles): proximity, similarity, closure, continuity, figure/ground, common region, common fate, symmetry & order, prägnanz (also emergence, multistability, invariance). Uniform connectedness is on lawsofux.com, not on that IxDF page.

## 3. Cognitive load

- NN/g, Whitenton, 2013-12-22 (https://www.nngroup.com/articles/minimize-cognitive-load/): intrinsic load (taking in new info, tracking goals) vs extraneous load (processing that does not help understanding, e.g. meaningless font styles). Tips: avoid visual clutter, build on existing mental models, offload tasks (pictures instead of text, re-display entered info, smart defaults).
- Germane load (schema building) is from Sweller's cognitive load theory (general knowledge).

## 4. Reading patterns, attention, banner blindness

- NN/g Pernice 2019-08-25, "Text Scanning Patterns: Eyetracking Evidence" (https://www.nngroup.com/articles/text-scanning-patterns-eyetracking/): F-pattern (least effective), spotted, layer-cake (most effective scanning short of reading), commitment (full reading). Zigzag and exhaustive review mentioned for image-heavy pages. F-pattern heatmap n=47.
- NN/g "F-Shaped Pattern of Reading on the Web: Misunderstood, But Still Relevant" (https://www.nngroup.com/articles/f-shaped-pattern-reading-web-content/): first found 2006; 2017 study found it on desktop and mobile; mirrored in RTL. Conditions: unformatted text, user wants efficiency, not committed. Fixes: important points in first two paragraphs; headings front-loaded so first two words carry the gist; group with borders/background; bold key phrases; descriptive links; bullets; cut content.
- NN/g Pernice 2018-04-22 "Banner Blindness Revisited" (https://www.nngroup.com/articles/banner-blindness-old-and-new-findings/): first documented 1997, replicated 2007, 2018. Triggers: location (top banner, right rail), ad-like look incl. animation, proximity to ads ("hot potato"). Mobile: large images mistaken for ads. Guidelines: don't make content look like ads; test whether users see top/right-rail content; don't mix ads and content.
- NN/g response-time limits (https://www.nngroup.com/articles/response-times-3-important-limits/): 0.1 s instantaneous; 1 s flow of thought; 10 s attention limit. >10 s percent-done with cancel; 2–10 s busy indicator; unknown total → show item names; spinner last resort. Origin Miller 1968, Card et al. 1991, Nielsen 1993.

## 5. Behaviour models

### Fogg Behavior Model
- https://behaviormodel.org/ : B=MAP, "Behavior happens when Motivation, Ability, and a Prompt come together at the same time."
- https://behaviormodel.org/prompts/ : three prompt types Facilitator, Spark, Signal; "Prompts tell people to 'do it now!'"; "Without a Prompt, the target behavior will not happen."; "Simplicity changes behavior."
- https://behaviormodel.org/ability/ : simplicity depends on scarcest resource at that moment; three ways to increase ability: train (hardest), give a tool, scale back the behavior (Tiny Habits). "designers ... often assume people have more ability than they really do."
- https://behaviormodel.org/motivation/ : core motivators sensation (pleasure/pain), anticipation (hope/fear), belonging (acceptance/rejection). High motivation → people can do hard things; low → only easy things.
- (secondary) Spark = high ability/low motivation; Facilitator = high motivation/low ability; Signal = both high. Action line is a curve. Six simplicity factors: time, money, physical effort, brain cycles, social deviance, non-routine. https://www.thebehavioralscientist.com/?p=3058 , https://www.northbeam.io/blog/fogg-behavior-model-motivation-ability-and-prompts
- Tiny Habits ABC recipe: "After I [anchor], I will [tiny behavior]", then celebrate within seconds (secondary: https://themeaningmovement.com/tiny-habits , https://www.shu.ac.uk/-/media/home/disabled-student-support/peers-support-2026/resources/tiny-habits-recipe-card.docx).

### Hooked (Nir Eyal, 2014)
- (secondary) Trigger (external → internal), Action, Variable reward (tribe, hunt, self), Investment. Manipulation Matrix: would you use it yourself, does it materially improve users' lives. Eyal concedes it is a "recipe for manipulation" if misused. Critique: Per Axbom https://axbom.com/nir-eyal-habit-danger/ (gambling mechanics). Summary: https://www.supersummary.com/hooked/background/

### Self-Determination Theory
- https://selfdeterminationtheory.org/theory/ : intrinsic = behaving for its own sake; extrinsic = instrumental; internalisation continuum external → introjected → identified → integrated; autonomy, competence, relatedness needs.
- Overjustification: Deci, Koestner & Ryan 1999 meta-analysis, Psychological Bulletin 125(6) (general knowledge; PubMed/APA pages did not render).

### Cialdini
- Seven principles: reciprocity, liking, social proof, authority, commitment & consistency, scarcity, unity (added 2016, book "Pre-Suasion"). (secondary: https://conversionxl.com/cialdini-unity/)
- ASU W. P. Carey blog 2025-04-22 (https://blogs.wpcarey.asu.edu/20250422-gentle-science-persuasion-part-seven-unity): unity = "sharing an identity, sense of partnership, or set of goals"; Cialdini: use only connections that really exist — "I wasn't counterfeiting our connection: I just pointed it out."

## 6. Biases and evidence

- Choice overload: Scheibehenne, Greifeneder & Todd 2010, JCR, 63 conditions / 50 experiments / N=5,036, mean effect "virtually zero" with high variance (https://ideas.repec.org/a/oup/jconrs/v37y2010i3p409-425.html). Chernev, Böckenholt & Goodman 2015, J. Consumer Psychology, 99 observations / N=7,202; overload significant once moderators included: choice-set complexity, decision-task difficulty, preference uncertainty, effort-minimising goal (https://www.kellogg.northwestern.edu/faculty/research/detail/2015/when-product-assortment-leads-to-choice-overload-a-conceptual).
- Endowed progress: Nunes & Drèze 2006, JCR 32:504–512; car wash: 8-stamp empty card vs 10-stamp card with 2 pre-stamped; 34% vs 19% redemption over 9 months (secondary: https://thinkinsights.net/consulting/endowed-progress-effect). Effect stronger when a reason is given for the endowment.
- Labour illusion: Buell & Norton 2011, Management Science 57(9):1564–1579 (https://pubsonline.informs.org/doi/fpi/10.1287/mnsc.1110.1376); showing work (e.g. each airline being searched) raised perceived value even with waits up to ~60 s.
- IKEA effect: Norton, Mochon & Ariely 2012, JCP 22(3):453–460 (https://dash.harvard.edu/handle/1/12136084). Effect dissipates when the build fails or is destroyed — labour → love only on successful completion.
- Defaults: Johnson & Goldstein 2003 "Do defaults save lives?" Science; opt-out countries near-universal effective consent vs opt-in far lower (secondary: https://thedecisionlab.com/insights/health/can-defaults-save-lives-the-power-of-default-options-on-life-saving-decisions). Caveat: graph shows registration not actual donation (https://marginalrevolution.com/marginalrevolution/2018/08/presumed-consent-wales-falls-short.html).
- Anchoring (Tversky & Kahneman 1974), framing (Tversky & Kahneman 1981), decoy/asymmetric dominance (Huber, Payne & Puto 1982), loss aversion (Kahneman & Tversky 1979; contested by Gal & Rucker 2018): general knowledge, no URL.
- Aesthetic-usability: NN/g Moran, 2024-02-03, reviewed 2026-09-01 (https://www.nngroup.com/articles/aesthetic-usability-effect/): users forgive minor not major issues; masks problems in tests; compare what they do vs say.
- Peak-end: NN/g Kane 2018-12-30 (https://www.nngroup.com/articles/peak-end-rule/): Kahneman & Fredrickson 1993 cold water; 80% chose the longer trial with the warmer ending. Design positive peaks, minimise negative peaks, end well, avoid "please don't go" pop-ups, handle errors well.

## 7. Emotional design, delight

- Norman, Emotional Design 2004 — IxDF (https://ixdf.org/literature/article/norman-s-three-levels-of-design): visceral (appearance, first impression), behavioural (pleasure and effectiveness of use), reflective (meaning, self-image; can offset behavioural flaws).
- NN/g Fessenden 2017-03-05 "A Theory of User Delight" (https://www.nngroup.com/articles/theory-user-delight/): surface delight (animations, microcopy, imagery, sounds) vs deep delight (functionality → reliability → usability → pleasure, flow). Forced surface delight can feel non-genuine for serious brands; delight fades if basic tasks are hard; negativity bias.

## 8. Trust and credibility

- Stanford Web Credibility Guidelines, B.J. Fogg, May 2002 (https://credibility.stanford.edu/guidelines/index.html): 1 verify accuracy (citations); 2 real organisation (address); 3 expertise (credentials); 4 honest people (bios); 5 easy contact; 6 professional/appropriate look; 7 easy to use and useful; 8 update often / show reviewed; 9 restraint with promotional content; 10 avoid errors of all types (typos, broken links).
- Baymard (https://baymard.com/blog/perceived-security-of-payment-form): 19% of US shoppers abandoned a checkout in last 3 months because they "didn't trust the site with their credit card information" (2025 survey, n=1,026). Earlier wave 25% (2024, n=1,012, secondary). Recommendations: visually enclose card fields (unique styling), 1–2 seals inside the enclosure, padlock + reassuring microcopy, recognisable seal brand (Norton ranked highest in 2023 test; homemade seal beat most SSL seals), fix layout glitches (look like phishing), A/B test.

## 9. Colour psychology evidence

- Elliot & Maier 2014 Annual Review of Psychology "Color psychology" (abstract only, https://www.doi.org/10.1146/ANNUREV-PSYCH-010213-115035): methodological issues hampered earlier work; colour can affect affect/cognition/behaviour.
- Elliot 2015 Frontiers review (https://www.frontiersin.org/articles/10.3389/fpsyg.2015.00368/full): field at early stage; "important weaknesses" must be addressed.
- Holcombe 2019 critique, Meta-Psychology (https://open.lnu.se/index.php/metapsychology/article/view/1652): most claims (blue calms, red lowers test scores) tested one or a few hues; generalisation unwarranted.
- Thorstenson, Pazda & Elliot 2015 "sadness impairs colour perception" was retracted (https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4979646/).

## 10. Deceptive patterns and law

- deceptive.design types (https://www.deceptive.design/types), 18 as of 2026-10-10: sneaking, forced action, hard to cancel, preselection, obstruction, hidden subscription, hidden costs, trick wording, visual interference, fake social proof, fake urgency, nagging, fake scarcity, disguised ads, confirmshaming, comparison prevention, addictive design, currency confusion.
- FTC staff report "Bringing Dark Patterns to Light", Sept 2022 (https://www.ftc.gov/reports/bringing-dark-patterns-light).
- FTC Click-to-Cancel (amended Negative Option Rule) vacated by 8th Circuit 2025-07-08, before 2025-07-14 effective date, procedural ground (no preliminary regulatory analysis) (secondary: https://www.gtlaw.com/en/insights/2025/7/eighth-circuit-vacates-ftcs-click-to-cancel-rule). ROSCA still in force: clear disclosure before billing info, express informed consent, simple way to stop. FTC ANPRM to restart Negative Option rulemaking 2026-03-11, comments due 2026-04-13 (secondary: https://www.gtlaw.com/en/insights/2026/3/ftc-seeks-comment-on-potential-updates-to-negative-option-rule , https://www.gibsondunn.com/ftc-restarts-negative-option-rulemaking-after-eighth-circuit-vacatur-enforcement-under-rosca-continues/). California has its own click-to-cancel law (secondary).
- EU DSA Art. 25 (OJ L 277, 27.10.2022) (https://www.springlex.eu/en/packages/dsa/dsa-regulation/article-25/): online platforms shall not design, organise or operate interfaces that deceive or manipulate or materially distort free and informed decisions; carve-out for practices covered by UCPD or GDPR; Commission may issue guidelines on (a) giving more prominence to certain choices, (b) repeatedly requesting a choice already made, (c) making termination harder than subscribing. Amsterdam court Bits of Freedom v Meta (Oct 2025): resetting feed to profiled ranking = dark pattern (https://www.dlapiper.com/insights/blogs/mse-today/2025/the-amsterdam-court-putting-the-dsa-into-practice).
- EU DMA Art. 13(4) and 13(6): gatekeepers may not circumvent via behavioural techniques or interface design; no non-neutral presentation of choices (secondary: https://streamlex.eu/articles/dma-en-art-13/ , https://www.glademichelwirtz.com/en/blog/scare-screens-and-dark-patterns-the-prohibition-on-circumvention-pursuant-to-article-134-dma/).
- GDPR Art. 7(3) (https://gdpr-info.eu/art-7-gdpr/): "It shall be as easy to withdraw as to give consent." Art 7(2) consent request clearly distinguishable, plain language. Art 7(4) consent not freely given if service conditional on unnecessary processing.
- EDPB Guidelines 03/2022 on deceptive design patterns in social media interfaces, v2.0 adopted 2023-02-14: categories Overloading, Skipping, Stirring, Obstructing, Fickle, Left in the Dark (secondary: https://activemind.legal/guides/dark-patterns).
- EU Digital Fairness Act: Commission work programme 2026 lists it for Q4 2026; MLex 2026-09-23 expects a proposal in November 2026; would cover dark patterns, addictive design, influencer marketing, subscriptions (secondary: https://www.europarl.europa.eu/legislative-train/theme-protecting-our-democracy-upholding-our-values/file-digital-fairness-act). Not yet proposed as of 2026-10-10 (per sources found).

## 11. Gamification

- Octalysis (https://yukaichou.com/gamification-examples/octalysis-complete-gamification-framework/): 8 core drives; white hat (Epic Meaning, Development & Accomplishment, Empowerment of Creativity & Feedback) vs black hat (Scarcity & Impatience, Unpredictability & Curiosity, Loss & Avoidance); Ownership and Social Influence neither.

---

## 12. WCAG 2.2

- New in 2.2 (https://www.w3.org/WAI/standards-guidelines/wcag/new-in-22/): Recommendation 2023-10-05. New SC: 2.4.11 Focus Not Obscured (Min) AA; 2.4.12 (Enhanced) AAA; 2.4.13 Focus Appearance AAA (2 CSS px perimeter, 3:1 change); 2.5.7 Dragging Movements AA; 2.5.8 Target Size (Min) AA 24×24 CSS px; 3.2.6 Consistent Help A; 3.3.7 Redundant Entry A; 3.3.8 Accessible Authentication (Min) AA; 3.3.9 (Enhanced) AAA. 4.1.1 Parsing removed.
- WCAG 2.2 updated 2024-12-12; approved as ISO/IEC 40500:2025, W3C announcement 2025-10-21 (https://www.w3.org/WAI/news/2025-10-21/wcag22-iso).
- 2.5.8 (https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html): exceptions spacing (24 px diameter circle test), equivalent, inline, user agent control, essential.
- 2.4.11 (https://www.w3.org/WAI/WCAG22/Understanding/focus-not-obscured-minimum.html): failure F110 sticky header/footer/cookie banner fully covering focus; technique C43 CSS scroll-padding.
- 2.5.7 (https://www.w3.org/WAI/WCAG22/Understanding/dragging-movements.html): single-pointer alternatives (up/down buttons, tap track, choose column from menu); keyboard alternative alone does not satisfy.
- 3.3.8 (https://www.w3.org/WAI/WCAG22/Understanding/accessible-authentication-minimum.html): pass = password manager autofill + paste allowed, WebAuthn/passkeys, email link, OAuth, object-recognition CAPTCHA (AA only). Fail = blocking paste, "enter 3rd and 5th character" (F109), puzzles/math CAPTCHA without alternative. "A service that requires manual transcription of a verification code is not compliant" unless paste/autofill allowed.
- 2.2.2 (https://www.w3.org/WAI/WCAG22/Understanding/pause-stop-hide.html): auto-start + >5 s + in parallel with other content → pause/stop/hide. Auto-updating: any duration.
- 2.3.3 (https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html): AAA; vestibular; technique C39 prefers-reduced-motion.
- 1.4.10 (https://www.w3.org/WAI/WCAG22/Understanding/reflow.html): 320 CSS px wide (= 1280 px at 400%), 256 CSS px tall; exceptions maps, diagrams, video, games, presentations, data tables, toolbars.
- 1.4.3 (https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html): 4.5:1; large 3:1; large = 18 pt (24 px) or 14 pt bold (~18.5 px); no rounding (4.499 fails); exceptions incidental, logotypes.

## 13. WCAG 3 and APCA (as of 2026-10-10)

- W3C news 2026-03-03 (https://www.w3.org/WAI/news/2026-03-03/wcag3): WCAG 3 Working Draft updated March 2026; still a draft.
- Roselli 2026-04 (https://adrianroselli.com/2026/04/wcag3-contrast-as-of-april-2026.html): Editor's Draft 2026-04-08 says "The contrast algorithm used in WCAG 3 is yet to be determined." APCA removed from the July 2023 WD (exploratory content without WG support within 6 months is removed). WCAG 3 "years away", perhaps 2030 earliest. Advice: meet WCAG 2 first; if using APCA, also pass WCAG 2.
- APCA in a Nutshell (https://git.apcacontrast.com/documentation/APCA_in_a_Nutshell.html): Lc 90 preferred body; Lc 75 minimum body columns; Lc 60 minimum other content text; Lc 45 headlines / large text; Lc 30 absolute minimum for spot text, placeholder, disabled; Lc 15 minimum for non-semantic non-text (dividers, focus outlines). Sizes e.g. Lc 75 body needs 18px/400 or 16px/500 or 14px/700; Lc 60 needs 24px/400 or 16px/700. Page self-describes as "candidate contrast method for the future WCAG 3" (conflicts with W3C draft state).

## 14. ARIA APG

- Read Me First (https://www.w3.org/WAI/ARIA/apg/practices/read-me-first/): "No ARIA is better than bad ARIA"; a role is a promise; ARIA doesn't add keyboard behaviour.
- Dialog (modal) (https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/): Tab/Shift+Tab wrap inside; Esc closes; initial focus first focusable (or tabindex=-1 heading for long content; least destructive button for irreversible); return focus to invoker. role=dialog, aria-modal=true, aria-labelledby/aria-label, optional aria-describedby.
- Tabs (https://www.w3.org/WAI/ARIA/apg/patterns/tabs/): Tab into active tab; arrows move; Home/End optional; automatic activation only if panels render without latency; tablist/tab/tabpanel; aria-selected; aria-controls; panel aria-labelledby; tabpanel tabindex=0 if no focusable content.
- Combobox (https://www.w3.org/WAI/ARIA/apg/patterns/combobox/): DOM focus stays on input; aria-activedescendant; Down opens/moves; Enter accepts; Esc closes then optionally clears; Alt+Down opens; role=combobox, aria-expanded, aria-controls, listbox/option, aria-selected, aria-autocomplete.
- Menu button (https://www.w3.org/WAI/ARIA/apg/patterns/menu-button/): Enter/Space open + focus first item; Down/Up optional; aria-haspopup, aria-expanded, aria-controls optional.
- Menu/menubar (https://www.w3.org/WAI/ARIA/apg/patterns/menubar/): Up/Down, Right/Left submenus, Enter, Home/End, typeahead, Esc closes and returns focus, Tab leaves and closes all menus.
- Disclosure (https://www.w3.org/WAI/ARIA/apg/patterns/disclosure/): button + aria-expanded (+ optional aria-controls); Enter/Space.
- Disclosure navigation example (https://www.w3.org/WAI/ARIA/apg/patterns/disclosure/examples/disclosure-navigation/): site nav "does not use the menu role because it does not provide the complex functionality that assistive technologies expect".

## 15. Data on real-world accessibility

- WebAIM Million 2026 (Feb 2026 crawl) (https://webaim.org/projects/million/): 95.9% of home pages with detected WCAG failures (94.8% in 2025); avg 56.1 errors (51 in 2025). Low contrast text 83.9%, missing alt 53.1%, missing form labels 51%, empty links 46.3%, empty buttons 30.6%, missing document language 13.5%. Pages with ARIA averaged 59.1 errors vs 42 without; >133 ARIA attributes per page avg.
- WebAIM Screen Reader Survey #10 (Dec 2023–Jan 2024) (https://webaim.org/projects/screenreadersurvey10/): desktop primary JAWS 40.5%, NVDA 37.7%, VoiceOver 9.7%; mobile VoiceOver 70.6%, TalkBack 34.7%; combos JAWS+Chrome 24.7%, NVDA+Chrome 21.3%, JAWS+Edge 11.4%, NVDA+Firefox 10.0%, VO+Safari 7.0%; 71.6% start by navigating headings.
- Deque coverage study (https://www.deque.com/automated-accessibility-testing-coverage/): 57.38% of issues by volume found by automated axe-core tests (13,000+ pages, ~300k issues); measured by issue volume, not SC count.

## 16. Platform targets, mobile

- Apple: 44×44 pt minimum hit target (https://developer.apple.com/design/tips/ ; forum https://developer.apple.com/forums/thread/739201 quoting HIG: 60×60 pt on visionOS).
- Android/Material: 48×48 dp, ~8 dp spacing (https://support.google.com/accessibility/android/answer/7101858). Compose Material controls auto-expand touch targets to 48 dp (https://kotlinlang.org/api/compose-multiplatform/material3/androidx.compose.material3/minimum-interactive-component-size.html).
- App Store Accessibility Nutrition Labels — Larger Text criteria (https://developer.apple.com/help/app-store-connect/manage-app-accessibility/larger-text-evaluation-criteria/): at least 200% or system max; iOS Dynamic Type >200% at AX3, >300% body at AX5; no overlap, avoid truncation; Zoom/Hover Text don't count; tab bars use Large Content Viewer. Other labels: VoiceOver, Voice Control, Dark Interface, Differentiate Without Color Alone, Sufficient Contrast, Reduced Motion, Captions, Audio Descriptions.
- iOS VoiceOver supports "Thai (Thailand)" (https://www.apple.com/ios/feature-availability/).

## 17. CSS references

- :focus-visible (https://developer.mozilla.org/en-US/docs/Web/CSS/:focus-visible): Baseline widely available since March 2022; fallback with @supports not selector(:focus-visible).
- prefers-reduced-motion (https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion): Baseline since January 2020; reduce = remove, reduce or replace motion; scaling/panning large objects = vestibular triggers. OS paths: Windows 11 Settings > Accessibility > Visual Effects > Animation Effects; macOS 26 Tahoe System Settings > Accessibility > Motion > Reduce motion (earlier: Display); iOS Settings > Accessibility > Motion; Android 9+ Settings > Accessibility > Remove animations.

## 18. Colour vision

- NEI (https://www.nei.nih.gov/learn-about-eye-health/eye-conditions-and-diseases/color-blindness): about 1 in 12 men; red-green most common; blue-yellow; complete rare.
- Okabe & Ito palette (https://clauswilke.com/dataviz/color-pitfalls.html): orange #E69F00, sky blue #56B4E9, bluish green #009E73, yellow #F0E442, blue #0072B2, vermilion #D55E00, reddish purple #CC79A7, black #000000. Run a CVD simulator; thin elements are hard to distinguish.
- jfly Color Universal Design (https://jfly.uni-koeln.de/color/): 3(+1) principles: schemes all can identify, use shapes/positions/line types not just colour, state colour names, aim for beauty; label graph lines directly.

## 19. COGA

- W3C "Making Content Usable for People with Cognitive and Learning Disabilities", WG Note 2021-04-29 (https://www.w3.org/TR/coga-usable/): 8 objectives: understand what things are; find what they need; clear content; avoid mistakes and correct them; help users focus; processes don't rely on memory; help and support; adaptation and personalisation. Not required for conformance.

## 20. Law

- EAA, Directive (EU) 2019/882 (https://eur-lex.europa.eu/eli/dir/2019/882/oj): applies to products placed on market and services provided to consumers after 28 June 2025; microenterprise = <10 persons and turnover or balance sheet ≤ EUR 2 million; microenterprises providing services exempt (Art 4(5)). Recital 101: 5-year transition for products used in services; self-service terminals until end of economic life, max 20 years. Services: electronic communications, audiovisual media access, passenger transport elements, consumer banking, e-books, e-commerce (https://commission.europa.eu/strategy-and-policy/policies/justice-and-fundamental-rights/disability/union-equality-strategy-rights-persons-disabilities-2021-2030/european-accessibility-act_en).
- EN 301 549 is the presumed route to conformity; national penalties vary (secondary: https://www.levelaccess.com/blog/is-wcag-conformance-enough-for-eaa-compliance/).
- ADA Title II web rule: DOJ interim final rule published 2026-04-20 (91 FR 20902) extends compliance: ≥50,000 population 2026-04-24 → 2027-04-26; <50,000 and special districts 2027-04-26 → 2028-04-26. Standard unchanged WCAG 2.1 AA. Comments closed 2026-06-22. (https://www.federalregister.gov/documents/2026/04/20/2026-07663/extension-of-compliance-dates-for-nondiscrimination-on-the-basis-of-disability-accessibility-of-web seen in search results, page blocked to fetch; secondary: https://www.jdsupra.com/legalnews/doj-extends-title-ii-ada-web-2176958/ , https://www.levelaccess.com/blog/the-ada-title-ii-extension-what-it-doesnt-change/)
- Section 508 (https://www.access-board.gov/ict/): Revised 508 Standards (final rule 2017-01-18) incorporate WCAG 2.0 A and AA (E205.4); applied to non-web documents and software with 4 SC excluded (2.4.1, 2.4.5, 3.2.3, 3.2.4); legacy ICT safe harbour for ICT unchanged since 2018-01-18.

## 21. Thailand

- TIS 2565-2555 = Thai Industrial Standard adopting WCAG 2.0 (adopted 2013). NSTDA is W3C Lead Translation Organization for WCAG 2.2 Thai (approved 2025-07-23); TISI update planned based on ISO/IEC 40500:2025 (https://lists.w3.org/Archives/Public/w3c-translators/2025JulSep/0017.html).
- Thai WCAG 2.2 translation published at NECTEC, dated 28 Dec 2025 (https://www.nectec.or.th/standard/WCAG/REC-WCAG22-20241212-TH/); both versions ready for review 2026-01-08 (https://lists.w3.org/Archives/Public/w3c-translators/2026JanMar/0000.html).
- TWCAG 2025 (Thai Web Content Accessibility Guidelines 2025), by Digital Council of Thailand (สภาดิจิทัลฯ) with Thai Internet Foundation (มูลนิธิอินเทอร์เน็ตร่วมพัฒนาไทย) and ThaiHealth (สสส.); updates TWCAG 2022; based on WCAG 2.2; for websites and mobile apps (PDF hosted at https://digital.hcu.ac.th/wp-content/uploads/2025/05/Accessibility-Guideline-2025-V.3.1-Final.pdf; official copy expected at www.dct.or.th — not verified).
- สดช. (ONDE) WCAG award for government sites, May 2023: 121 agencies entered, 50 passed; judging = manual 13-item review + automated (achecker, W3C validator, zero errors) + testing by blind and deaf users (https://www.thaipbs.or.th/now/content/191). Judge: some sites embed their own reader → audio conflicts with users' screen readers.
- NVDA translated into Thai (https://download.nvaccess.org/documentation/userGuide.html, Internationalization list). VoiceOver supports Thai.
- Not verified: any Thai-built screen reader; quality of Thai word segmentation in each screen reader.

## 22. Tools

- axe DevTools (https://www.deque.com/axe/devtools/): extension, Intelligent Guided Tests, linter, CI; axe-core open source; Lighthouse uses axe-core since 2017.
- Lighthouse scoring (https://developer.chrome.com/docs/lighthouse/accessibility/scoring): weighted average of pass/fail audits (weights 3–10 from axe impact); excludes manual checks (tab order, focus management).
- Accessibility Insights for Web (https://accessibilityinsights.io/docs/web/overview/): FastPass (~50 automated checks + Tab stops) under 5 min; Assessment for WCAG 2.1 AA (~50 automated + ~20 manual assisted tests). Also Windows.
- Stark (https://www.getstark.co/): Figma/FigJam/Sketch plugins, browser extensions, scanning, compliance center.
- WebAIM screen reader testing (https://webaim.org/articles/screenreader_testing/): title, reading order, pronunciation, alt, headings, landmarks, links list, Tab, form labels, table headers, dynamic content.
- NVDA keys (userGuide): modifier Insert; h heading, 1–6 levels, d landmark, k link, f form field, l list, t table; NVDA+F7 elements list.
