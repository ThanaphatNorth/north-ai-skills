# User research: learn the target group's behaviour before designing

> Read when: starting any new product, feature or redesign; the user can't say who the audience is or what they struggle with; you have no direct access to users and must research from the desk; choosing a research method or sample size; writing an interview guide or survey; building personas, job stories or journey maps; prioritizing features (Kano); planning card sorts, tree tests or A/B tests; including disabled or older users; synthesizing findings and tracing them to design decisions; designing for Thai users.

**Contents:** 1 Choose a method · 2 Lean research without user access · 3 Interviews · 4 Surveys · 5 Jobs to be done · 6 Personas vs JTBD vs segments · 7 Journey maps & service blueprints · 8 Kano · 9 Card sorting & tree testing · 10 Diary studies · 11 A/B testing · 12 Accessibility research · 13 Synthesis · 14 Traceability · 15 Thailand · Pitfalls · Sources

Related: what "good" means and how to measure it → `ux-foundations.md`; biases that distort answers → `psychology.md`; WCAG → `accessibility.md`. Templates: intake `../templates/design-brief.md`, personas/job stories/journey/empathy map `../templates/persona-jtbd.md`, test script `../templates/usability-test-script.md`.

**Default sequence for an agent:** run the design brief → lean research (§2, always possible) → write proto-personas + job stories flagged as assumptions → design → test the riskiest flow (5 users, or a first-click/5-second test if no lab access) → iterate. Never present an assumption as a finding.

## 1. Choose a method by the question you need answered

Three dimensions (NN/g landscape): **attitudinal** (what people say) vs **behavioural** (what they do); **qualitative** (why, how to fix) vs **quantitative** (how many, how much); **context of use**: natural, scripted, limited (a partial product), or not using. When the stakes are high, prefer behavioural evidence over attitudinal.

| Your question | Method | Say / Do | Qual / Quant | Sample | Cost · speed |
|---|---|---|---|---|---|
| Who are the users, what are they trying to do, in what context? | Field study / contextual inquiry; interviews | Do / Say | Qual | 5–30, in rolling groups of ~5 until no new themes | $$ · weeks |
| Why do people switch to or away from a product? | JTBD switch interview (§5) | Say (about past events) | Qual | Same as interviews; recent switchers only | $$ · weeks |
| How does behaviour unfold over days or weeks? | Diary study (§10) | Do + Say | Qual | 5–12 (homogeneous) to 12–30 (varied) | $$ · weeks |
| How do users group and name our content? | Open card sort (§9) | Say | Qual→Quant | ≥ 15 per group (qual); 30–50 (quant) | $ · days |
| Can users find X in our structure? | Tree test (§9) | Do | Quant | ~40 per tree (binary-metric rule below) | $ · days |
| Where would users click first? Does the page communicate its purpose? | First-click test; 5-second test (§2) | Do / Say | Quant-ish | ~40 for numbers; 5–10 for a quick read | $ · hours |
| Can users complete the task with this design, and where do they struggle? | Qualitative usability test (moderated or unmoderated) | Do | Qual | 5 per round; 3–4 per group if several groups | $ · days |
| How usable is it compared with last release or competitors? | Benchmark test; competitive test | Do | Quant | ~40 per variant (±15%, 95% confidence) | $$ · weeks |
| How many users do X, and where do they drop out? | Analytics, funnels, search logs | Do | Quant | All traffic | $ · hours (if instrumented) |
| Which live variant performs better? | A/B test (§11) | Do | Quant | Thousands per arm (formula) | $$ · weeks |
| How common is an attitude? Which features matter? | Survey (§4); Kano (§8) | Say | Quant | ~100 for ±10%, ~385 for ±5% (95%) | $ · days |
| What do users complain about and what words do they use? | Review/ticket/forum mining (§2) | Say | Qual→Quant | Until saturation | $ · hours |
| Does it work with assistive technology? | Expert review + testing with disabled users (§12) | Do | Qual | A few per disability type in scope | $$ · days |

By phase (NN/g): **Strategize** (generative: field, diary, interviews, surveys, concept tests) → **Design** (formative: card sort, tree test, usability tests) → **Launch & assess** (summative: benchmarks, A/B, analytics, surveys).

Sample-size anchors (NN/g): 5 users per qualitative round finds most problems; quantitative studies with a binary metric need **40** (95% confidence, ±15%), 21 (95%, ±20%), 28 (90%, ±15%) or 15 (90%, ±20%); for continuous metrics such as time, use 47 / 26 / 33 / 19. Survey margin of error: n = z²·p(1−p)/e², so 385 for ±5% and 97 for ±10% at 95% confidence.

## 2. Lean research when the agent has no direct access to users

You can almost always do this from the desk in 1–3 hours. Label every output with an **evidence level**:
**E3** observed behaviour of real users (analytics, tests) · **E2** self-report from real users (reviews, interviews, surveys) · **E1** secondary (market data, competitor patterns, published research) · **E0** assumption (team belief, proto-persona).

**Step 1. Desk research (E1).** Collect the context of use: market size and demographics, device and connectivity mix, dominant platforms and payment habits, regulation, accessibility needs of the population. Prefer primary sources (government statistics, DataReportal/Kepios, regulators, platform docs), and record the date and source for each fact. For Thailand, start with §15.

**Step 2. Competitor teardown (E1).** Choose 2–4 products: direct competitors, the product users most likely compare you with, and one with outstanding UX outside the category. For each, walk the core task end to end and fill in:

| Product | Entry → first value (steps) | Fields to sign up | Price/fees visible before commitment? | Terms users see | States handled (empty/error/offline) | Heuristic violations (#, severity) | Pattern worth adopting | Pattern to avoid |
|---|---|---|---|---|---|---|---|---|

Screenshot every state. The aim is to beat the competitors, not copy them. Conventions shared by all of them are users' expectations (Jakob's law, `psychology.md`).

**Step 3. Review and forum mining with a coding scheme (E2).** Sources: App Store and Google Play reviews (yours and competitors'), G2/Capterra/TrustRadius (B2B), Reddit, product communities, Facebook groups, Pantip (Thai). Sample both the most recent reviews (current version) and the most helpful ones, across 1–2★ and 4–5★. Code each review into a spreadsheet row:

| Field | Values |
|---|---|
| source, date, rating, product, version | — |
| quote | verbatim, with personal data removed |
| JOB | what they hired the product for ("track spending with my partner") |
| PAIN | the problem, plus journey phase: discover / sign up / first use / core task / pay / support / leave |
| WORKAROUND | what they do instead (spreadsheets, screenshots, LINE chat) |
| SWITCH | from/to which product, and why (feeds the §5 forces) |
| DELIGHT | what they praise |
| REQUEST | feature asked for (translate it into the underlying need) |
| VOCAB | the users' own words for things (use them in labels) |
| SEGMENT | role, device, context, experience level if stated |

Stop when about 20 more reviews add no new codes (rule of thumb). Output: code frequencies by journey phase, 3–5 quotes per top code, and a vocabulary list. Caveat: reviews over-represent extremes, power users and the latest update. Use them to generate hypotheses and wording, not to estimate prevalence.

**Step 4. Analytics questions to ask the client (E3 if answered).**
1. Top 10 tasks or pages by volume; the entry pages and channels for each.
2. Funnel for the core task: step-by-step drop-off; where people exit or retry.
3. Device, OS, browser, screen-width and app-version mix; share on slow networks if known.
4. New vs returning users; retention curve (week 1, 4, 12).
5. Site/app search: top queries, zero-result queries, refinements.
6. Error logs and failed validations by field.
7. Support tickets and chat: top 10 categories, and the screens they mention.
8. Language/locale split; accessibility settings (font scaling, screen reader) if collected.
9. Payment and sign-in method mix; abandoned-payment reasons.
10. Time-of-day and location patterns (commute? at work? at home?).
If none exist, specify the events to instrument (HEART, `ux-foundations.md` §11) as part of the design.

**Step 5. Assumption mapping (E0 → test plan).** List every belief the design depends on, tagged **desirability** (users want it), **viability** (the business works), **feasibility** (we can build it). Plot importance (high/low) × evidence (have/none). Test first the assumptions that are most important and have the least evidence. Give each its cheapest test:

| ID | Assumption | Type | Importance | Evidence (E-level + source) | Cheapest test | Pass criterion |
|---|---|---|---|---|---|---|
| A1 | Shoppers will pay by PromptPay QR rather than card | Desirability | High | E1: BOT PromptPay info | Analytics on payment mix; fake-door test | ≥ X% choose QR |

**Step 6. Proto-personas and job stories, flagged as assumptions (E0).** Use `../templates/persona-jtbd.md`. Each attribute carries its evidence level. Proto-personas are cheap (a 2–4 h workshop, 3–6 personas) and good for aligning a team, but they can turn into an echo chamber of wrong guesses. Replace them with research as soon as possible.

**Step 7. Fast unmoderated tests the client can run in a day** (tools: Lyssna, Maze, Optimal Workshop, UserTesting, or a Google Form with images):
- **First-click test**: one task per screen ("Where would you click to change your delivery address?"). Users whose first click was on the right path eventually succeeded 87% of the time, against 46% after a wrong first click (Bailey & Wolfson, via MeasuringU). First clicks on static images closely track clicks on live sites. Metrics: % in the target hotspot, time to first click.
- **5-second test**: show the screen for 5 s (10 s for complex screens), then ask "What is this page for?", "What can you do here?", "Who is it for?" and a 1–7 attitude scale. It tests message clarity, hierarchy and the CTA, not usability. Don't use it on multi-purpose dashboards.
- **Tree test** of the proposed navigation (§9).
- **Unmoderated task test** on a clickable prototype (`../templates/usability-test-script.md` part B).

Staff (support, sales) can stand in as proxy users for generating hypotheses; they are never validation. Their knowledge of the product inflates success.

## 3. Interviews

Use them for context, motivations, workflows and vocabulary. Interviews can't tell you whether a design is usable or what people will do in future; use a usability test for that.

**60-minute guide**
| Min | Block | Prompts |
|---|---|---|
| 0–5 | Intro, consent to record | "No right answers; we're learning, not testing you." |
| 5–10 | Warm-up | Role, typical day, tools they use for [domain] |
| 10–40 | Last-time story (core) | "Tell me about the last time you [did the job]." → "What happened just before?" → "What did you do next?" → "What was hard?" → "What did you try instead?" |
| 40–50 | Forces (if switching) | "What made you start looking?" (push) · "What did you hope would be different?" (pull) · "What worried you?" (anxiety) · "What almost kept you with the old way?" (habit) |
| 50–55 | Artefacts | "Can you show me the spreadsheet / chat / screenshot you used?" |
| 55–60 | Wrap-up | "What should I have asked?" · permission to follow up |

Rules: ask about specific past events, not generalities or hypotheticals ("Would you use…?" predicts nothing). One question at a time, open-ended, neutral. Follow up on timing, frequency, workarounds and feelings with "Tell me more about that" or by echoing the user's last words, then stay silent. Treat feature requests as clues to a need. Interview 5 at a time, synthesize, and continue until a round adds few new themes (typically 5–30 people in total). Pilot the guide once and keep the goals fixed.

## 4. Surveys

Use them to **quantify** something qualitative work has already surfaced, never to discover the unknown.
- Keep well under 20 questions (NN/g calls 20 too many unless respondents are highly motivated). Put the most important questions first, and use conditional logic so people only see items that apply to them.
- Ask about one thing per question (no "fast and reliable"). Use neutral wording, balanced scales, and include "Not applicable" / "Don't use".
- Prefer multiple-answer questions where several answers are true. Randomize option order (except ordinal scales).
- Ask about past behaviour ("In the last 7 days, how many times…") rather than predictions or preferences. Don't ask what analytics can already measure.
- Screen on behaviour ("Ordered food delivery in the last month"), not demographics alone.
- Pilot: about 4 rounds of single-participant think-aloud, revising between rounds; then check the exported data.
- Standard instruments beat home-made ones: SUS, UMUX-Lite, SEQ (`ux-foundations.md` §11), Kano pairs (§8).

## 5. Jobs to be done (JTBD)

A **job** is the progress a person wants to make in a given situation; they "hire" a product to make it. Capture the functional dimension (get it done), the emotional one (feel confident) and the social one (look competent to the boss).

**Job story (Klement):** `When [situation + trigger], I want to [motivation], so I can [expected outcome].`
- Situation carries the context: time, place, device, emotional state, other people.
- No persona, no UI or solution: "When I'm at the till with a queue behind me, I want to confirm the payment arrived, so I can hand over the goods without awkwardness." Not: "As a merchant I want a notification bell."
- One job story → one or more design responses; verify each one against the outcome.

**Switch interview (Moesta & Spiek):** interview people who recently switched products, while they still remember the details. Reconstruct the timeline from events: **first thought → passive looking → (event) → active looking → (event) → deciding → first use → ongoing use**. Don't ask about the forces directly; they emerge from the events.

**Forces of progress:** a switch happens when **Push + Pull > Anxiety + Habit**.

| Force | What it is | Design response |
|---|---|---|
| Push of the situation | Pain with the current way ("the spreadsheet broke at 20 people") | Name that pain in messaging and onboarding |
| Pull of the new solution | The better future they picture | Show the outcome early: demo data, previews, examples |
| Anxiety of the new solution | Fear it won't work, looks foolish, loses data, costs too much | Free trial, undo, previews, transparent pricing, guarantees, social proof, security signals |
| Habit of the present | Comfort with the old way | Import/migration, familiar patterns and terms, gradual adoption, keep the old export formats |

## 6. Personas vs JTBD vs behavioural segments

| Tool | What it captures | Built from | Best for | Risk |
|---|---|---|---|---|
| Proto-persona | The team's assumptions about a user type | 2–4 h workshop, no research | Aligning a team and exposing assumptions | Echo chamber; must be labelled E0 |
| Qualitative persona | Goals, behaviours, attitudes, context of a user group | 5–30 interviews, coded into themes | Empathy; prioritizing between groups with conflicting needs | Can't show what share of users each represents |
| Statistical persona | Same, with prevalence | Survey of ≥ 100 (ideally 500+) + clustering | Sizing segments | Costly; clusters may not be design-relevant |
| Job story (JTBD) | The progress wanted in a situation, independent of who | Switch interviews, reviews, support data | Scoping features; finding non-obvious competitors; messaging | Thin on empathy and context of use |
| Behavioural segment | Groups defined by what they do (frequency, intent, channel, plan) | Analytics, CRM | Targeting, experiments, measuring by segment | Says what, not why |

Use them together: segments size the groups, personas explain them, job stories drive features. A persona should list the jobs it hires the product for. Demographics alone (age, gender, income) are not a persona; include them only when they change the design (for example, older users needing larger targets).

## 7. Journey maps and service blueprints

**Journey map:** one actor, one scenario with its expectations, then phases (e.g. discover → try → buy → use → get support) with rows for actions, mindsets (quotes), an emotion line, pain points and opportunities. Each opportunity gets an owner and a metric. Base it on research; if it rests on assumptions, label it as an assumption map. Template: `../templates/persona-jtbd.md`.
**Service blueprint:** extends a journey downward with frontstage (staff or UI the customer sees), backstage (invisible staff actions), support processes (systems, policies) and evidence (emails, receipts, signage), separated by the lines of interaction, visibility and internal interaction. Use it when the problem crosses channels or departments (delivery, refunds, clinic booking) or when the root cause is operational, not the UI.
**Experience map:** a generic, product-agnostic version; **user-story map:** a planning tool for releases, not a discovery tool.

## 8. Kano: which features are must-haves, which delight

For each feature, ask a pair of questions on the same 5-point scale (*I like it · I expect it · I'm neutral · I can tolerate it · I dislike it*):
- Functional: "If [product] had [feature], how would you feel?"
- Dysfunctional: "If [product] did NOT have [feature], how would you feel?"

| Functional \ Dysfunctional | Like | Expect | Neutral | Tolerate | Dislike |
|---|---|---|---|---|---|
| **Like** | Q | A | A | A | O |
| **Expect** | R | I | I | I | M |
| **Neutral** | R | I | I | I | M |
| **Tolerate** | R | I | I | I | M |
| **Dislike** | R | R | R | R | Q |

M must-be · O one-dimensional (performance) · A attractive (delighter) · I indifferent · R reverse · Q questionable (discard).
Tally per feature and check the spread, not just the mode. Satisfaction coefficients: **Better = (A+O)/(A+O+M+I)**, **Worse = −(O+M)/(A+O+M+I)**.
Use: ship all M first (their absence causes dissatisfaction, their presence earns nothing); compete on O; differentiate with a few A; cut I; make R optional. Describe features as user outcomes, not UI ("see delivery time before paying", not "ETA widget"). Re-run periodically, because expectations rise over time.

## 9. Card sorting and tree testing

**Card sort** (generative: how users group and name content). Open sort is the default; closed sorts are better done as tree tests; avoid hybrid sorts (predefined groups bias results). Use 30–50 cards; more causes fatigue and "Misc" piles. Recruit ≥ 15 per user group for qualitative insight (moderated, think-aloud) or 30–50 for quantitative patterns. Read the similarity matrix and dendrogram, then run a few moderated sessions to learn *why*.
**Tree test** (evaluative: can they find it in a named hierarchy, without visual design). Write tasks as goals without the label's words ("You want to stop getting promo emails", not "Find Notification settings"). Define the correct node(s), start with an easy warm-up task, and use between-subjects designs when comparing label options. Metrics: success, directness (no backtracking), time, and the wrong first choices (which reveal confusing labels). Pilot qualitatively first. Order: card sort → draft tree → tree test → wireframes.

## 10. Diary studies

Use them for habits, behaviour that recurs over time, multi-touchpoint journeys and learnability. Length follows the behaviour (examples: 1 week for intelligent assistants, 2 weeks for buying a phone plan, 3 weeks for meal delivery). Logging can be event-based (log each occurrence), interval-based (daily) or signal-based (log when pinged). Recruit 5–12 for small homogeneous studies and 12–30 for varied users, and over-recruit for drop-out. Run a pilot, a kickoff brief, mid-study follow-ups while memories are fresh, and an exit interview. Pay more than for a usability session, in instalments for studies longer than a week.

## 11. A/B testing basics

Use it when the product is live, traffic is high, and one primary metric (the "overall evaluation criterion") can decide. With low traffic, run qualitative tests instead.
- Decide the primary metric, the minimum detectable effect (MDE) and the sample size **before** starting. Stop only at the planned sample, not at the first significant result.
- Run A/A tests to check variability and instrumentation. Run whole weeks to cover weekday cycles; run longer when primacy effects (experienced users slower on new UI) or newness effects (novelty clicks) are likely.
- Analyze only triggered users (those who reached the changed step). This cuts noise: Kohavi's checkout example halved the traffic needed.
- A/B tests tell you *which*, not *why*; pair them with usability tests.

**Sample-size rule of thumb** (two-sided α = 0.05, 80% power, per arm): **n ≈ 16·σ²/δ²**; for conversion rates σ² = p(1−p). Halving the MDE quadruples n.

| Baseline conversion p | Relative lift to detect | Absolute δ | n per arm |
|---|---|---|---|
| 5% | 10% | 0.5 pt | 30,400 |
| 5% | 20% | 1.0 pt | 7,600 |
| 10% | 10% | 1.0 pt | 14,400 |
| 2% | 20% | 0.4 pt | 19,600 |
| 30% | 5% | 1.5 pt | ~14,900 |

Kohavi et al. (KDD 2007) give the more conservative n = (4rσ/Δ)² (95% confidence, 90% power, r = number of variants). Their example: 5% conversion with a 5% relative change needs just under 500,000 users; a 20% change needs 30,400.

## 12. Accessibility research with disabled users

1. Do an expert review against WCAG first (`accessibility.md`) so sessions aren't spent on obvious barriers.
2. Recruit a few participants per disability type in scope: blind screen-reader users, low-vision users with magnification, motor (keyboard/switch/voice), cognitive, Deaf/hard of hearing for media, and older users if they are in the audience. Match their assistive-technology expertise to your audience (novices for public services, experts for specialist tools). Use recruiters who specialize in disabled participants, and pay at least standard rates.
3. Make logistics accessible: an accessible venue or remote session; participants use their own devices and assistive technology configured their way; accessible consent forms; extra time.
4. Pilot the setup with the assistive technology. When something fails, find the source: content, browser, assistive technology, or the user's familiarity with it.
5. Facilitate with more interaction than usual, focus on barriers and errors rather than time-on-task, and never generalize from one person to "all blind users".
6. Report the scope, the methods and the participants' assistive technology. User sessions cannot establish WCAG conformance, so pair them with an audit.

## 13. Synthesis: from notes to insights

1. Debrief right after each session. Write **atomic notes**: one observation per note, tagged with participant ID, task, and whether it was observed or said.
2. **Affinity map:** generate notes individually first (5–10 min), then cluster silently, then name the clusters (after grouping, not before). Duplicate notes that fit two clusters, and keep small or outlier clusters. Dot-vote priorities and assign an owner to each.
3. Turn clusters into **insight statements**:
   `[Who] [does/feels/struggles with what] because [underlying reason], so [consequence for the product]. Evidence: [n/N participants, sources, E-level]. Confidence: H/M/L.`
   Example: "First-time sellers abandon listing at the photo step because they think they need professional photos, so listings and supply drop. Evidence: 4/6 interview participants, 31 coded reviews (E2). Confidence: M."
4. Turn each insight into **How might we** questions: outcome-focused, positively phrased, without a built-in solution, and neither too broad nor too narrow. "HMW make new sellers confident their phone photos are good enough?" (not "HMW add a photo tutorial?", which embeds a solution, nor "HMW improve listing?", which is too broad). Target the root cause, not the symptom.
5. Separate **findings** (what happened), **insights** (why, with evidence) and **recommendations** (what to do). Severity-rate usability findings 0–4 (`ux-foundations.md` §3).

## 14. Traceability: insight → design decision

Every non-trivial design decision should point to an insight or to a named assumption. Keep one table in the design doc:

| Decision ID | Design decision | Because (Insight / Assumption ID) | Evidence level | Success metric | Validation plan |
|---|---|---|---|---|---|
| D1 | Single "Full name" field at checkout | I3: users type full name into "First name" (Baymard) | E1 | Checkout field errors ↓ | Funnel step errors before/after |
| D2 | QR payment as default on mobile | A1 (assumption) | E0 | % QR payments; payment completion | Fake-door test, then A/B |

Rules: E0 decisions must have a validation plan and a review date. When a test refutes an insight, update the table and every decision that cites it. In a handoff, cite IDs ("D2 per A1") so reviewers can audit the reasoning.

## 15. Thailand (ไทย): context facts and design implications

Sourced from DataReportal *Digital 2026: Thailand* (published 8 Nov 2025, data around Oct 2025) unless noted.

| Fact | Value |
|---|---|
| Population · median age | 71.6 M · 40.6 years |
| Age 55–64 · 65+ | 14.1% · 16.0% of population |
| Urban share | 55.2% |
| Internet users | 67.8 M (94.7%); about 3.78 M (5.3%) offline |
| Cellular connections | 96.6 M (135% of population) |
| Median download speed (Ookla, 12 months to Aug 2025) | Mobile 124.33 Mbps · fixed 262.42 Mbps (early 2025: mobile 61.21 Mbps) |
| Social media user identities | 56.6 M (79.1%) |
| LINE monthly active users | 56 M (78.2% of population, 82.6% of internet users) |
| Facebook ad reach | 51.5 M (71.9%) |
| YouTube ad reach | 47.2 M (65.9%) |
| TikTok ad reach | 56.6 M users aged 18+ (DataReportal warns about comparability across years) |
| PromptPay (Bank of Thailand) | Launched 2016; Thai QR Payment = scan a QR in a mobile banking app; PromptPay transfers free up to 5,000 baht; most banks waived digital-payment fees since 2018 |

Design implications:
- **Mobile-first is the default** for consumer products: connections exceed the population and speeds are high. Still design for interrupted sessions and the offline state (`ux-foundations.md` §7). B2B and back-office tools are often used on desktop; verify with analytics (brief Q7).
- **LINE is the default messaging layer:** consider LINE Login, share-to-LINE, LINE Official Account notifications and hand-off to chat support. Ask the client which ones they use, and keep phone/email alternatives.
- **QR / PromptPay belongs in payment flows** alongside cards. Show the amount, payee name and expiry next to the QR. When the user pays on the same phone, add a "Save QR image" action so they can open it in their banking app, and keep the order page polling for confirmation.
- **Older users are a large group** (16% aged 65+): use larger default text and targets, strong contrast, labelled icons, no gesture-only actions, forgiving forms and phone support paths (`accessibility.md`).
- **Bilingual TH/EN:** test the Thai copy length and line breaking (`typography-layout.md`), use the Thai vocabulary found in reviews and Pantip threads, and set date, number and currency formats (฿, Buddhist Era years where the domain expects them, such as government or health documents) per product decision.
- Review mining in Thai: Google Play/App Store TH reviews, Pantip, Facebook groups. Code them with the same scheme as §2 and keep the Thai quotes verbatim.

## Pitfalls

| Symptom | Cause | Fix |
|---|---|---|
| Research "confirms" the team's idea | Leading questions, hypotheticals ("Would you use…?"), recruiting fans | Ask about past behaviour; neutral prompts; recruit by behaviour from outside the fan base |
| Personas everyone ignores | Demographic fluff, no jobs, no evidence, or made-up details presented as fact | Behaviour + jobs + evidence levels; label proto-personas E0 |
| Survey results contradict usage data | Self-report bias; asking for predictions | Trust behavioural data for "what"; use the survey for "why" and attitudes only |
| Feature list from interviews becomes the roadmap | Treating requests as needs | Translate each request into the job and the force behind it; validate with Kano or tests |
| A/B "winner" disappears after launch | Peeking/stopping early, underpowered test, novelty effect | Fix the sample size in advance, run whole weeks, check new vs returning users |
| Card sort used as the final navigation | Card sorts are generative and one-level | Follow up with a tree test of the full hierarchy |
| Unmoderated test full of junk sessions | "Professional testers", unclear tasks | Screen on behaviour, add a warm-up/attention task, over-recruit, pilot |
| Accessibility "validated" by one blind tester | Generalizing from one person; no audit | Several participants per disability, plus a WCAG audit |
| Review mining overstates a problem | Reviews skew to angry users and recent releases | Treat as hypotheses; size the problem with analytics or a survey |
| Insights deck forgotten after a week | No link from insights to decisions | Traceability table (§14) inside the design doc |

## Sources

- NN/g, When to Use Which User-Experience Research Methods — https://www.nngroup.com/articles/which-ux-research-methods/
- NN/g, UX Research Cheat Sheet — https://www.nngroup.com/articles/ux-research-cheat-sheet/
- NN/g, How Many Test Users in a Usability Study? — https://www.nngroup.com/articles/how-many-test-users/
- NN/g, Summary of Quantitative Sample Sizes — https://www.nngroup.com/articles/summary-quant-sample-sizes/
- NN/g, Competitive Usability Evaluations — https://www.nngroup.com/articles/competitive-usability-evaluations/
- Precoil (David Bland), Assumptions Mapping — https://www.precoil.com/assumptions-mapping
- NN/g, 3 Persona Types: Lightweight, Qualitative, and Statistical — https://www.nngroup.com/articles/persona-types/
- MeasuringU, Do Click Tests Predict Live-Site Clicks? — https://measuringu.com/do-click-tests-predict-live-site-clicks/
- MeasuringU, When and Why to Use a Click Test — https://measuringu.com/why-and-when-to-use-a-click-test/
- Smashing Magazine (Kuric), Five-Second Testing case study — https://www.smashingmagazine.com/2023/12/five-second-testing-case-study/
- NN/g, User Interviews 101 — https://www.nngroup.com/articles/user-interviews/
- NN/g, Talking with Participants During a Usability Test — https://www.nngroup.com/articles/talking-to-users/
- NN/g, Qualitative Surveys — https://www.nngroup.com/articles/qualitative-surveys/
- Intercom (Klement), Designing Features Using Job Stories — https://www.intercom.com/blog/using-job-stories-design-features-ui-ux/
- jobstobedone.org (Moesta & Spiek), The Four Forces — https://jobstobedone.org/the-four-forces/
- NN/g, Personas vs. Jobs-to-Be-Done — https://www.nngroup.com/articles/personas-jobs-be-done/
- NN/g, Journey Mapping 101 — https://www.nngroup.com/articles/journey-mapping-101/
- NN/g, Service Blueprints: Definition — https://www.nngroup.com/articles/service-blueprints-definition/
- NN/g, Empathy Mapping — https://www.nngroup.com/articles/empathy-mapping/
- Kano evaluation table and coefficients (practitioner cheat sheet) — https://www.kanosurveys.com/cheatsheets
- NN/g, Card Sorting: Uncover Users' Mental Models — https://www.nngroup.com/articles/card-sorting-definition/
- NN/g, Tree Testing — https://www.nngroup.com/articles/tree-testing/
- NN/g, Diary Studies — https://www.nngroup.com/articles/diary-studies/
- Kohavi, Henne, Sommerfield, Practical Guide to Controlled Experiments on the Web (KDD 2007) — https://cdn.elezea.com/pdf/GuideControlledExperiments.pdf
- All about sample-size calculations for A/B testing (arXiv 2305.16459) — https://arxiv.org/pdf/2305.16459
- W3C WAI, Involving Users in Evaluating Web Accessibility — https://www.w3.org/WAI/test-evaluate/involving-users/
- NN/g, Affinity Diagramming — https://www.nngroup.com/articles/affinity-diagram/
- NN/g, Using "How Might We" Questions — https://www.nngroup.com/articles/how-might-we-questions/
- DataReportal, Digital 2026: Thailand — https://datareportal.com/reports/digital-2026-thailand
- DataReportal, Digital 2025: Thailand — https://datareportal.com/reports/digital-2025-thailand
- Bank of Thailand, PromptPay — https://www.bot.or.th/en/financial-innovation/digital-finance/digital-payment/promptpay.html
