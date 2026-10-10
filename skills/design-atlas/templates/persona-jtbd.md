# Persona, job story, journey map and empathy map templates

> Use after the design brief and lean research (`../references/user-research.md` §2) to turn what you know (and what you only assume) into artifacts that drive design. Every line carries an evidence level: **E3** observed behaviour · **E2** self-report from real users · **E1** secondary/desk · **E0** assumption. Untraceable content is E0 by definition.

Contents: 1 Proto-persona · 2 Job stories · 3 Forces of progress worksheet · 4 Journey map · 5 Empathy map · 6 Quality checks

## 1. Proto-persona (assumption-based)

> **WARNING: PROTO-PERSONA — ASSUMPTIONS, NOT RESEARCH.** Built from <workshop / desk research / reviews> on <date>. Replace with research-based content as evidence arrives. Do not quote it as user data.

```markdown
### <Short descriptive name: role + defining behaviour>   e.g. "Busy stall owner who sells on LINE"
Evidence summary: E0 x items · E1 x items · E2 x items   Last updated: <date>   Owner: <name>

| Attribute | Content | E-level | Source / note |
|---|---|---|---|
| Role & situation | … | E0 | |
| Jobs they hire us for | J1, J2 (see job stories) | E1 | reviews coded 2026-10 |
| Context of use | device, place, time, frequency, interruptions | E0 | |
| Current solution / workarounds | … | E2 | 12 reviews mention screenshots of transfers |
| Pains (top 3) | … | | |
| Desired outcomes (top 3) | … | | |
| Anxieties about switching | … | | |
| Digital skill & abilities | … (include vision, motor, literacy if relevant) | | |
| Language & vocabulary | words they use for key concepts | E2 | review VOCAB codes |
| What would make them leave | … | | |
| Design implications | 3–5 bullets ("must work one-handed at the counter") | | |

Open questions to validate (highest risk first):
1. … → test: …
2. … → test: …
```

Rules: 3–6 personas maximum, each differing in *behaviour or jobs*, not just demographics. Include age, gender or income only if they change the design. One primary persona per product area, and design for the primary first.

## 2. Job stories (JTBD)

Format: **When** [situation + trigger + context], **I want to** [motivation / progress], **so I can** [expected outcome, functional + emotional].

```markdown
| ID | Job story | Dimension | Frequency | Cost of failure | E-level | Source |
|---|---|---|---|---|---|---|
| J1 | When …, I want to …, so I can … | functional / emotional / social | daily/weekly/once | low/med/high | E? | |
```

Worked examples (illustrative, E0):
- J1: When a customer at my stall says they've paid by QR and a queue is waiting, I want to see the payment confirmed within seconds, so I can hand over the goods without awkwardness or loss.
- J2: When my child's fever is still high at night, I want to know quickly whether to go to the hospital, so I can act without panicking or wasting a trip.
- J3: When month-end close is two days away, I want to see which invoices are still unmatched, so I can finish reconciliation without working the weekend.

Checks for a good job story:
- [ ] The situation is concrete (when, where, trigger, emotional state, other people).
- [ ] No persona label ("As a user…") and no UI or feature in it.
- [ ] The outcome is verifiable: you could tell whether the design delivered it.
- [ ] Small enough for one flow; big jobs are split into sub-jobs.
- [ ] Traced to evidence, or marked E0 with a validation plan.

Job → design mapping (fill in for each job):

```markdown
| Job | Design response (screen/flow/feature) | Success signal | Metric |
|---|---|---|---|
| J1 | Full-screen "Paid ฿___" confirmation with sound + haptic, visible from 1 m | Merchant hands over goods without checking the bank app | Time from scan to confirmation; % of payments with a manual check |
```

## 3. Forces of progress worksheet (per job, from switch interviews or reviews)

```markdown
Job: J_
| Force | Evidence (quote / code, E-level) | Design response |
|---|---|---|
| PUSH: what's wrong with today's way | | message it; target it in onboarding |
| PULL: the better future they imagine | | show the outcome early (demo data, preview) |
| ANXIETY: fear about the new way | | trial, undo, transparent price, guarantees, proof |
| HABIT: comfort with the current way | | import/migrate, familiar terms and patterns |
Switch happens when PUSH + PULL > ANXIETY + HABIT. Biggest blocker for this job: <force>.
```

## 4. Journey map

One actor, one scenario, one goal per map. Columns are phases; adapt names to the scenario.

```markdown
### Journey: <persona> — <scenario> — goal: <outcome>     Evidence: <E-levels + sources>   Date: <…>
Expectations: <what they expect going in>

| | 1. Trigger / discover | 2. Evaluate / sign up | 3. First use | 4. Core task | 5. Pay / complete | 6. Support / return |
|---|---|---|---|---|---|---|
| Doing (actions) | | | | | | |
| Touchpoints / channel | search, LINE, store page… | | | | | |
| Thinking (quotes) | "…" | | | | | |
| Feeling (−2 … +2) | 0 | −1 | | | | |
| Pain points | | | | | | |
| Opportunities | | | | | | |
| Owner | | | | | | |
| Metric | | | | | | |
```

Rules: actions are narrative summaries, not click logs. Mindsets come from quotes where possible. The emotion row is a single line of highs and lows. Every opportunity gets an owner and a metric. If the map crosses departments or backstage systems, extend it into a service blueprint with rows for **Frontstage**, **Backstage**, **Support processes** and **Evidence** below the line of visibility (`../references/user-research.md` §7).

## 5. Empathy map

One user or persona at a time; captures a mindset at a moment (no sequence). Fill notes individually first, then cluster.

```markdown
### Empathy map — <persona / participant> — context: <scenario>   Date: <…>  Version: <…>

| SAYS (verbatim quotes) | THINKS (unspoken beliefs, worries) |
|---|---|
| "…" (P3, interview) | … (inferred from P2, P5 — E2) |

| DOES (observed behaviour) | FEELS (adjective + cause) |
|---|---|
| … (P1, usability test task 2 — E3) | anxious that the transfer went to the wrong account (P4) |

Goals (optional): …
Gaps / open questions: …
```

Every note cites a source (participant ID, review ID, ticket ID). Notes without a source go in a separate "Assumptions" list. Contradictions between SAYS and DOES are insights; log them in synthesis (`../references/user-research.md` §13).

## 6. Quality checks before using these artifacts in design

- [ ] Each persona and journey states its evidence mix; any E0-heavy artifact is labelled as an assumption at the top.
- [ ] Each persona lists the job stories it hires the product for.
- [ ] Each top job has a forces worksheet or a note on why it doesn't need one.
- [ ] Each journey opportunity has an owner and a metric, and links to a design decision ID (traceability table).
- [ ] Validation plans exist for the three riskiest E0 assumptions.
