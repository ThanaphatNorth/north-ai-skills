# Design brief: intake questionnaire

> Use before designing anything: a new product, feature, screen, landing page or redesign. Run it with the user, fill the summary block at the end, and keep the summary at the top of the design doc. Every later design decision should trace back to an answer here or to a listed assumption (`../references/user-research.md` §14).

## How to run it

- Ask in **2–3 short batches** (5 questions max per message), in the user's language. Batch 1: Q1–Q5 (product, people, jobs, context). Batch 2: Q6–Q10 (platform, data, brand, competitors, tone). Batch 3: Q11–Q15 (metrics, constraints, scope).
- If the user says "just design it" or can't answer: **proceed with the defaults below**, list every default in the Assumptions log as E0, and show that log with the first design. Don't block on unknowns, and don't present defaults as facts.
- Ask a follow-up only when the answer changes the design (platform, audience, main task, brand constraints). Skip questions the conversation or repo already answers (check `package.json`, existing design tokens, the README and screenshots first).
- One-message version for tiny tasks: ask Q1, Q2, Q3, Q6, Q8 only.

## Questions

**Q1. Product and goal.** What is it, what problem does it solve, and is this new or a redesign? What should be different after this work ships?
- *Why it matters:* defines "useful" (useful > usable > delightful). Redesigns carry existing users' habits and change aversion.
- *Default:* treat it as a new MVP of the most common product in the category; the goal is to let the primary user complete the core task end to end.

**Q2. Audience.** Who are the primary users? Secondary users? Who pays or approves (if different from the user)? Who is explicitly *not* the target?
- *Why it matters:* every design trade-off (density, vocabulary, guidance) depends on who uses it. Buyer ≠ user changes what the first screens must prove.
- *Default:* one primary proto-persona derived from the category (adult, smartphone-first, moderate digital skill, distracted context), labelled E0. Include older users when the product is for the general public.

**Q3. Jobs and top tasks.** What are the 3 most important things users come to do? Fill: "When ___, I want to ___, so I can ___." Which task happens most often, and which matters most when it fails?
- *Why it matters:* the design must make the top task the fastest and most obvious path. High-cost tasks (payment, medical, legal) need error prevention and confirmation.
- *Default:* derive 3 job stories from competitor reviews and the category (`user-research.md` §2), and mark them E0/E1.

**Q4. Context of use.** Where and when do people use it (on the move, at a desk, at a counter with a queue, at night)? How often (daily, monthly, once)? Interruptions? Lighting, noise, one-handed use, gloves? Connectivity?
- *Why it matters:* ISO usability is only defined in a context of use. Frequency decides learnability vs efficiency; mobile-in-motion decides target size, contrast and offline handling.
- *Default:* mobile, one-handed, interrupted sessions, variable connectivity; occasional use (optimize learnability over power features).

**Q5. Abilities, language and literacy.** Age range, digital skill, languages (TH/EN/other), accessibility needs, domain expertise?
- *Why it matters:* sets the copy level, type size, density and how much in-context help is needed.
- *Default:* WCAG 2.2 AA; body text at least 16 px; plain language (sentences ≤ 25 words); Thai + English if the market is Thailand; no gesture-only actions.

**Q6. Platforms and devices.** Web (which browsers), iOS, Android, desktop app, tablet, kiosk? Smallest and largest screen? Native or cross-platform? Dark mode?
- *Why it matters:* decides conventions (HIG vs Material vs web), navigation patterns and the layouts to produce (`platform-*.md`).
- *Default:* responsive web, mobile-first at 360–430 px wide, also laid out at 768 and 1280+; light and dark themes; latest two versions of major browsers.

**Q7. Existing evidence.** Is there analytics, research, support tickets, app-store reviews, sales feedback or a previous usability test? Can you share funnels or top search terms?
- *Why it matters:* behavioural data (E3) beats opinion. It tells you where users actually fail.
- *Default:* none available; run lean desk research (`user-research.md` §2) and list the analytics questions to answer later.

**Q8. Brand assets.** Logo (SVG preferred; light/dark variants), brand colours (hex/OKLCH), fonts and licences, brand guidelines, imagery and illustration style, icon set, an existing design system or component library, Figma files? **Product, people and place photography** (or 3D/CAD for products)? If there is none: may we generate photoreal images, and with what budget?
- *Why it matters:* reusing real assets avoids rework and off-brand output; licences decide which fonts you may ship. Without real photography a bold or cinematic page falls back to drawn placeholders that look fake — plan the imagery now (`ai-assets-higgsfield.md` "Photoreal stills pipeline": roughly 2–3 credits per 2K still).
- *Default:* text wordmark placeholder; neutral palette with one accent (`color.md`); a free, Thai-capable font pairing if Thai is needed (`typography-layout.md`); an open-source icon set; for imagery, list every image slot with a prompt and quote the generation cost before spending. Mark everything "placeholder brand".

**Q9. Competitors and references.** Which 2–4 products do users compare you with? 2–3 products or sites you love (and why)? Any you dislike (and why)?
- *Why it matters:* competitors set users' expectations (shared conventions = mental model). References show taste faster than adjectives.
- *Default:* pick the 2–3 category leaders from a search and tear them down (`user-research.md` §2, Step 2); use `inspiration.md` for references.

**Q10. Tone and personality.** Three adjectives for the brand voice. Formal or casual? Humour allowed? In Thai: polite particles (ค่ะ/ครับ) or neutral? Visual mood (calm, bold, playful, premium, clinical)?
- *Why it matters:* drives copy, colour, type, motion and imagery (`styles-catalog.md`, `motion.md`).
- *Default:* clear, warm, professional; no humour in errors or money flows; neutral Thai without gendered particles; visual intensity per Q10b.

**Q10b. Creative ambition.** How far should this go: calm (polished, conventional), bold (one unmistakable look + a couple of scroll set pieces) or cinematic (a scroll story with an intro, a signature mechanic and a payoff, award-site level)? Any sites you love the feel of? Do people arrive worried or in a hurry?
- *Why it matters:* sets the ambition dial and the context-of-use gate in `../references/creative-direction.md` §1; "make it beautiful" means different things at each level.
- *Default:* marketing, brand, launch, storefront and portfolio pages → **bold**; the user says creative / wow / อลัง / names an award site → **cinematic**; product UI, checkout, and any surface where people arrive in distress (health symptoms, emergencies, money or legal trouble) → **calm or gentle bold**, with the primary action in the first viewport.

**Q11. Success metrics.** How will we know it worked? One business KPI (conversion, retention, tickets) and one UX metric (task success, time on task, SEQ/SUS/UMUX-Lite). Current baseline and target?
- *Why it matters:* without a metric you can't prioritize or validate. HEART goals → signals → metrics (`ux-foundations.md` §11).
- *Default:* task success ≥ 80% for the top task in a 5-user test; SEQ ≥ 5.5; for live products, completion rate of the core funnel step, compared before and after.

**Q12. Constraints.** Tech stack and component library; deadline; budget; legal or regulatory requirements (PDPA consent, health/finance rules, accessibility law); content readiness; required integrations (LINE Login/OA, PromptPay/QR, payment gateway, maps, SSO).
- *Why it matters:* a design that can't be built, or that breaks the law, is waste. Integrations change flows (e.g. a QR payment needs a waiting/confirmation state).
- *Default:* React + TypeScript with an accessible headless component library; standard consent for personal data; real content still to come, so design with realistic-length placeholder copy in every language.

**Q13. Locale details.** Languages and the default language; date format (Buddhist Era years needed?), currency (฿), number, phone and address formats; right-to-left support needed?
- *Why it matters:* locale bugs are UX bugs (wrong year, truncated Thai labels, phone validation rejecting local numbers).
- *Default:* Thai and English UI with a language switch; DD/MM/YYYY in the Gregorian calendar unless the domain expects BE; ฿ with thousand separators; validation accepts spaces and dashes.

**Q14. Scope and deliverable.** Which flows and screens are in scope? Which states (empty, loading, error, offline, permission)? Fidelity (wireframe, high-fidelity, coded)? Output format (code, Figma, HTML prototype, spec)? Who reviews it?
- *Why it matters:* prevents both gold-plating and missing states.
- *Default:* the top task's flow, end to end, with every state from `ux-foundations.md` §7, as a coded responsive prototype plus a short spec.

**Q15. Risks and non-goals.** What must this design *not* do or change? What has failed before? What worries you most?
- *Why it matters:* surfaces political and technical landmines early, and lists the assumptions to test first.
- *Default:* non-goals = anything outside Q14 scope; top risk = the riskiest assumption in the assumption map.

## Output: brief summary (fill and keep at the top of the design doc)

```markdown
# Design brief — <product / feature> — <date>
Product & goal: …
Primary users (E-level): …            Secondary / buyer: …
Top jobs:
  J1 When …, I want to …, so I can …   (E?)
  J2 …
  J3 …
Context of use: device …, place …, frequency …, connectivity …
Abilities & language: …                Accessibility target: WCAG 2.2 AA
Platforms & breakpoints: …
Evidence available: …
Brand assets: logo … colours … fonts … DS …
Competitors / references: …
Voice (3 adjectives): …                 Visual mood: …
Success metrics: KPI … (baseline → target); UX metric … (target)
Constraints: stack … deadline … legal … integrations …
Locale: …
Scope & deliverable: …                 Non-goals: …

## Assumptions log
| ID | Assumption (default used) | Why we assumed it | E-level | How/when to validate |
|----|---------------------------|-------------------|---------|----------------------|
| A1 | … | user didn't know | E0 | … |
```

Then: pick the research steps (`../references/user-research.md` §1–2), draft proto-personas and job stories (`persona-jtbd.md`), and design.
