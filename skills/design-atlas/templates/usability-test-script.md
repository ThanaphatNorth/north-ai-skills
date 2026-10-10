# Usability test script: moderated and unmoderated

> Use to test a prototype or live product with real users, or to hand a ready-to-run test plan to the user/client when the agent can't run sessions itself. Part A is a moderated think-aloud script; Part B adapts it for unmoderated tools (Maze, Lyssna, UserTesting, Useberry, etc.). Metrics and formulas: `../references/ux-foundations.md` §11. Method choice and sample sizes: `../references/user-research.md` §1.

Contents: 0 Plan · Task-writing rules · A Moderated script · B Unmoderated script · C Scoring · D Findings log and report

## 0. Plan (fill before recruiting)

```markdown
Product / prototype: <link, version>          Fidelity: paper / clickable / coded / live
Research questions (3 max): 1. Can first-time users … ? 2. Where do they … ? 3. Do they understand … ?
Participants: 5 per round (qualitative) · ~40 per variant if you need metrics with ±15% at 95% confidence
  User groups: <group A: n>, <group B: n> (3–4 per group if several groups)
Screener (behaviour first): e.g. "In the last month, how did you <do the job>?" [options incl. the target behaviour]
  Exclude: employees, UX/market-research professionals, people who took part in the last 6 months
Devices: <phone model / OS / browser>; participants' own device preferred for mobile
Session: 45–60 min moderated · 15–20 min unmoderated
Roles: facilitator (talks), note-taker (silent), observers (silent, separate channel)
Metrics: task success (binary, predefined), SEQ per task, time on task, errors, SUS or UMUX-Lite at end
Incentive: <amount>; accessibility accommodations: <AT, captions, extra time>
Pilot: 1 session with a colleague + 1 with a real participant; fix tasks before the full run
```

Task table (one row per task, ordered easy → hard; 5–8 tasks per 60 min):

```markdown
| # | Scenario as read to the participant | Starting screen | Success criteria (observable end state) | Max time | Research question |
|---|---|---|---|---|---|
| 1 | Warm-up: "Have a look at this page and tell me what you think it's for." | Home | n/a (first impression) | 2 min | RQ3 |
| 2 | "You ordered a phone case yesterday. Find out when it will arrive." | Home | Order detail with delivery date visible and stated aloud | 3 min | RQ1 |
```

## Task-writing rules

1. **Realistic:** something this participant would actually do, with a plausible motivation ("buy shoes under ฿1,500 for running", not "buy the orange Nike runners").
2. **Actionable:** ask them to *do* it, not to describe what they would do.
3. **No clues:** never use the UI's labels, menu names or steps. Describe the goal in the user's words ("get news about upcoming events by email", not "sign up for the newsletter").
4. **Specific enough:** give every detail they need (name, date, amount, account) so they don't have to invent or ask.
5. **One goal per task** with an **observable end state**, so success is unambiguous; write the success criteria before testing.
6. **Independent tasks:** a failure in task 2 must not block task 3; reset state or provide a starting link.
7. **Order easy → hard**, with the riskiest flow tested while attention is fresh (by task 2 or 3).
8. **Unmoderated extra:** say explicitly when to stop ("When you've found the delivery date, click 'Done'"), and add a verification question ("What date did you find?").

## A. Moderated think-aloud script (read verbatim, adapt the wording)

**A1. Welcome and consent (3 min)**
> "Thanks for joining. I'm <name>. Today we're trying out a design for <product> to see where it works and where it's confusing. **We're testing the design, not you.** You can't do anything wrong, and if something is hard, that's exactly what we need to know.
> I didn't design this, so you won't hurt my feelings; please be honest.
> With your permission I'll record the screen and audio. The recording is only used by the team to improve the product and is stored <where>, deleted after <period>. Is that OK? [get explicit yes / signed consent]
> You can stop or take a break at any time, and you'll receive <incentive> regardless.
> Some things may not work, because it's a prototype. If that happens, I'll tell you."

**A2. Think-aloud instructions + practice (3 min)**
> "As you work, please **think out loud**: say what you're looking at, what you're trying to do, and what you expect will happen. For example, if you were setting an alarm on your phone you might say: 'I'm looking for the clock app… I expect alarms to be in here… that plus is probably to add one.'
> Let's practise: please think aloud while you <neutral practice task on an unrelated site or the phone's settings>."

**A3. Warm-up questions (5 min)** about their context, not the product:
- "Tell me about the last time you <did the job>." · "What did you use?" · "What was annoying about it?"

**A4. Tasks (30–40 min).** For each task:
1. Read the scenario aloud and give it as a card or in chat. Ask them to read it back if the task is complex.
2. Observe silently. Note: path, hesitations (> 5 s), wrong clicks, recoveries, quotes, emotional reactions, and whether success criteria were met.
3. After the task, ask the **SEQ**: "Overall, how difficult or easy was the task to complete? 1 = very difficult, 7 = very easy." If below 5: "What made it difficult?"
4. Optional probes, after the task only: "What did you expect to happen when you clicked ___?" · "You paused on this screen; what were you thinking?" · "How did you know you were done?"

**Neutral prompts during tasks**

| Situation | Say |
|---|---|
| Silent for ~10 s | "What are you thinking right now?" / "What are you looking for?" |
| They ask "Should I click this?" (boomerang) | "What do you think?" / "What would you do if I weren't here?" |
| They say "Hmm, that's weird" (echo) | "That's weird…?" (repeat their words with rising tone, then wait) |
| You need the reason (Columbo) | "And that was because…?" (trail off; let them finish) |
| They're stuck past the max time | "Thanks, that's really useful. Let's move on." (mark as fail; never imply it was their fault) |
| They ask if they did it right | "You're doing great at showing us how this works." |

Never say: "Click the ___" · "Try the menu" · "Good!/Correct!" · "Most people find this easy" · "Are you sure?" · any explanation of how the design works (except to recover from a broken prototype; then mark the task as assisted). When unsure whether to speak, count to 10 silently.

**A5. Post-test (7 min)**
- Questionnaire: **SUS** (10 items) for an overall product score, or **UMUX-Lite** (2 items) when time is short. Use the same instrument every round.
- "What was the most frustrating part?" · "What did you like?" · "If you could change one thing, what would it be?" · "Is there anything you expected to see that wasn't there?"
- Thank them, give the incentive, stop the recording.

**A6. Debrief right away (10 min, team only):** top 3 observations, surprises, any task wording to fix before the next session. Write atomic notes: one observation per note, with participant ID and task.

**SUS items** (Brooke; answer 1 = strongly disagree … 5 = strongly agree)
1. I think that I would like to use this system frequently.
2. I found the system unnecessarily complex.
3. I thought the system was easy to use.
4. I think that I would need the support of a technical person to be able to use this system.
5. I found the various functions in this system were well integrated.
6. I thought there was too much inconsistency in this system.
7. I would imagine that most people would learn to use this system very quickly.
8. I found the system very cumbersome to use.
9. I felt very confident using the system.
10. I needed to learn a lot of things before I could get going with this system.

**UMUX-Lite** (1 = strongly disagree … 7 = strongly agree): "<Product>'s capabilities meet my requirements." · "<Product> is easy to use."

Translations: use a validated translation of SUS/SEQ if one exists for the language. Otherwise translate carefully, pilot it, and label scores as not directly comparable with the English benchmarks.

## B. Unmoderated script (paste into the testing tool)

**Intro screen**
> "You'll try a design for <product> and complete <n> short tasks. There are no right or wrong answers; we're testing the design, not you. Please **think aloud** as you go: say what you're looking at, what you're trying to do, and what you expect to happen. It takes about <15> minutes. Some parts may not work because this is a prototype."

**Screener and attention check**: 2–3 behaviour questions + one simple warm-up task with a known answer ("What is the name of the shop on this page?"). Exclude anyone who fails it.

**Per task (repeat)**
1. Scenario text (rules above) + "When you've <end state>, click 'Done'. If you get stuck, click 'Give up'."
2. Verification question (multiple choice or short text) that only someone who reached the end state can answer.
3. SEQ (1–7) + "Why did you give that rating?" (optional open text).

**End**: SUS or UMUX-Lite → "What, if anything, was confusing?" → "Anything else you'd like to tell us?"

**Unmoderated checklist**
- [ ] Prototype links tested on the target devices; hotspots cover the full tappable area; no dead ends.
- [ ] Every task has an explicit stop condition and a verification question.
- [ ] Pilot with 1–2 participants; read their recordings before launching.
- [ ] Over-recruit by ~20–30% (rule of thumb) and set exclusion rules in advance (failed attention check, under X seconds total, no audio when think-aloud was required).
- [ ] Use for live products or high-fidelity prototypes; use moderated sessions for early concepts or emotional and imaginative tasks.

## C. Scoring

| Metric | How to compute | Report |
|---|---|---|
| Task success | 1 = end state reached without help; 0 = fail, gave up, timed out or assisted (log assists separately) | Rate per task + 95% adjusted-Wald CI; compare the **lower bound** with the target (e.g. 70–80% for consumer tasks; ≈100% for payments/medical) |
| SEQ | Mean of 1–7 per task | Flag tasks with mean < 5.5; quote the "why" answers |
| Time on task | Successful attempts only, seconds | **Geometric mean** when n < 25; median when larger; show the range |
| Errors | Count of wrong paths / slips per task, with the step | Most common error per task |
| SUS | Odd items: answer − 1; even items: 5 − answer; sum × 2.5 | Mean + CI; 68 = average, ≥ 80.3 = A; never call it a % |
| UMUX-Lite | Mean of the two items; SUS-equivalent ≈ 0.65 × ((i1 + i2 − 2) × 100/12) + 22.9 | Track trend across rounds |

Quick CI reference (95%, adjusted Wald): 5/5 → 51–100% · 4/5 → 36–98% · 8/10 → 48–95% · 10/10 → 68–100% · 15/20 → 53–89% · 30/40 → 60–86%. With 5 users, metrics are directional only; the value of a small test is the problems found, not the numbers.

```ts
// TS 5.x helpers (same as ux-foundations.md §11)
const sus = (r: number[]) => 2.5 * r.reduce((s, v, i) => s + (i % 2 === 0 ? v - 1 : 5 - v), 0);
const geoMean = (xs: number[]) => Math.exp(xs.reduce((s, x) => s + Math.log(x), 0) / xs.length);
function adjustedWald(x: number, n: number, z = 1.96) {
  const p = (x + z * z / 2) / (n + z * z), h = z * Math.sqrt(p * (1 - p) / (n + z * z));
  return [Math.max(0, p - h), Math.min(1, p + h)] as const;
}
```

## D. Findings log and report

Log every issue as it is observed (one row per issue, not per participant):

```markdown
| ID | Task | Observation (what happened) | Participants (n/N) | Evidence (quote / timestamp) | Heuristic # | Severity 0–4 | Likely cause | Recommendation | Insight / Decision ID |
|---|---|---|---|---|---|---|---|---|---|
| F1 | 2 | Looked for delivery date under "Account" first, not "Orders" | 3/5 | P2 08:14 "I thought my stuff would be in my account" | 2 | 3 | Label mismatch with users' model | Add the latest order + status to Home; rename "Orders" to "My orders" | I4 → D7 |
```

Severity: 0 not a problem · 1 cosmetic · 2 minor · 3 major (fix before release if possible) · 4 catastrophe (blocks release). Rate on frequency × impact × persistence.

**Report (1 page first, details after)**
1. What we tested, with whom (n, groups), when, prototype version.
2. Scorecard: per task — success (CI), SEQ, median/geometric time; SUS/UMUX-Lite.
3. Top 5 issues by severity, each with evidence, a clip or screenshot, and a recommendation.
4. What worked well (keep these during fixes).
5. Next steps: fixes → re-test plan (another 5 users on the changed flows), open questions → method.
6. Traceability: link each issue to an insight ID and the design decision it changes (`../references/user-research.md` §14).
