# AI tells: design that reads as made by a person

> Read when: starting any direction (Step 4) or signature (Step 6); the user says a design looks AI-made, generated, vibe-coded, like a template or "like every other site"; before delivery, for the tell audit on screenshots (Step 7); you notice you are about to "fix" a generic look by swapping in a different stock look.

**Contents:** 1 Why machine-made design looks machine-made · 2 The replacement trap · 3 The tells · 4 Design from the subject · 5 Where to look for source material · 6 Motion and scroll from the subject · 7 Copy · 8 The audit · 9 Worked example · Pitfalls · Sources

Related: choosing a style `styles-catalog.md`; concept and storyboard `creative-direction.md`; finish `visual-craft.md`; scroll recipes `scroll-parallax.md`. The tested example is `examples/craft-finish/`.

## 1. Why machine-made design looks machine-made

A model without direction samples the most probable page: the centre of what it was trained on. Anthropic calls this distributional convergence. The centre is made of popular templates and component kits (the indigo of early Tailwind UI examples became "the" button colour because tutorials copied it, and pages generated from those tutorials are now training data too), so the default page is nobody's page in particular. It is also guessing: nobody told it what this brand looks like, and often it never looks at the rendered result.

People spot the result in a second because nothing on the page depends on the subject. Swap the logo and the copy for a competitor's, or for a product in another trade, and the page still works. That is the property to remove. Polish does not remove it.

## 2. The replacement trap

Banning a default does not produce a design. The next most probable choice takes its place, and that one becomes a tell in turn. The sequence so far:

| Wave | Reads as | How it came about |
|---|---|---|
| The default kit | Inter or a system font, purple-to-blue gradient on white, centred hero, three icon cards, grey shadows, one radius | The centre of the training data |
| The tasteful swap | Warm cream background, high-contrast serif display with one word in italic or in the accent colour, terracotta or forest accent, pill buttons, an uppercase tracked label above every heading | "Avoid the generic look" answered with the same alternative every time |
| The serious swap | Near-black with a single acid-green or vermilion accent; or a broadsheet look of hairline rules, zero radius and a monospace face for small labels | The alternative to the alternative |

Anthropic's own frontend-design skill lists the last two rows as where generated design clusters now, and names its own brand accent among them. So a list of banned looks is a moving target. The only stable rule is positive: **every visible decision has a source in the subject** (§4). A hairline rule is a tell on a marketing page and correct on a printed form; cream paper is a tell as a default and correct for a stationer. The source decides, never the list.

## 3. The tells

Use these to audit, not to design. One or two prove nothing. Three or more from one group and the page reads as generated.

| Group | Tells | Replace with |
|---|---|---|
| Colour | Purple or indigo gradients; gradient headline text; large coloured glows; cream plus terracotta; near-black plus one acid accent; a tinted near-black "premium" band | A palette lifted from the subject's own materials (§5), used by function |
| Type | Inter, Roboto or a system font on everything; the Space Grotesk / Instrument Serif / Geist rotation; one accented word in a headline (italic, bold or coloured); a serif-italic word in a sans page; a monospace face for small labels | The typography the subject already uses in the world; hierarchy by size and weight, not by a decorated word |
| Labels and chrome | An uppercase tracked eyebrow above every heading; a badge or "NEW" pill above the h1; middle-dot strings (A · B · C); "→" on every link; 01 / 02 / 03 on things that are not a sequence; pulsing "Live" dots on things that are not live | Labels only where the content needs one; numbering only for real sequences |
| Components | Identical rounded cards with one radius and one grey shadow; a thick coloured border on one side of a card; emoji or generic line icons (bolt for speed, shield for security); big number over small label stat rows; screenshots in fake browser frames; glassy blobs | Rules, tables, lists and real artefacts; a picture of the actual thing; numbers inside sentences that say what they mean |
| Structure | Hero, logo row, three features, testimonials, three-column pricing, gradient call-to-action band, in that order; every section the same height and padding; everything centred | Sections whose shape comes from their content; unequal emphasis; an order that follows the argument |
| Motion | The same fade-and-rise on every block; hover transitions on every card; hover states that do nothing | Motion taken from what the subject physically does (§6), or none |
| Imagery | Stock people at laptops; abstract 3D shapes; smooth generated illustration | The product, the place, the material, photographed or rendered as itself |
| States | Only the happy path; dark-theme body text below AA | Empty, loading, error and success written in plain words (`ux-foundations.md`) |
| Honesty | Invented ratings, client logos, counters | Real proof or no proof section (`psychology.md`) |

## 4. Design from the subject

1. **Collect the subject's own artefacts** before any design gallery: ten real things from the trade (§5). Photograph, screenshot or describe each one in a line.
2. **Name the vernacular**: its grid, its type, its colours, its marks, its materials, the way it moves. Write them down as facts ("carbonless copies are white, pink, yellow", "the serial number is printed in red by a numbering machine").
3. **One concept the whole page enacts** (`creative-direction.md` §2): what the page *is*, in the subject's own terms. Not "a landing page about invoicing" but "the page is the invoice book".
4. **A source line for every decision.** In the expression tokens and next to each component, a comment naming where the choice comes from. A decision with no source is a default that got through: delete it or find its source.
5. **Spend the boldness once.** One memorable element carries the concept; everything else is quiet and exact (`visual-craft.md` §1).
6. **Real content only**: the product's real words, numbers, names and pictures. Layout follows the shape of the content, so sections stop matching each other.
7. **Check against the sibling.** Ask what you would have produced for any similar product. Whatever is the same in both is not yet designed.

## 5. Where to look for source material

Starting points, not answers. The specific client always has better material than the category.

| Subject | Artefacts worth collecting |
|---|---|
| Money, accounting, invoicing | Ledgers, invoice books, cheques, receipts, bank statements, stamps, share certificates |
| Health, care | Prescription labels, appointment cards, ward signage, pharmacy packaging, anatomical plates |
| Food, restaurants | Menus, order pads, market signs, packaging, kitchen tickets, the tableware itself |
| Developer tools | Terminals, man pages, RFCs, schematics, test output, the tool's own logs |
| Travel, transport | Tickets, timetables, departure boards, maps, luggage tags, wayfinding signs |
| Education | Textbooks, exam papers, library cards, blackboards, lab notebooks |
| Fashion, craft | Garment labels, pattern paper, swatch cards, lookbooks, workshop tools |
| Music, events | Record sleeves, gig posters, setlists, ticket stubs, tape labels |
| Property, building | Floor plans, elevation drawings, site signs, key tags, survey maps |
| Any brand | Its archive: old packaging, signage, letterheads, the founder's handwriting, the building |

From each artefact take structure before surface: how it divides space, what is printed and what is filled in, what is repeated, what is stamped or signed, what wears out.

## 6. Motion and scroll from the subject

Scroll effects and parallax belong in the design when they have a job, and the job comes from the subject: ask what the object does in the hand. Paper is pulled out from under paper. A door opens. A liquid pours. A drawer slides. A stamp comes down. A map unfolds. That movement is the mechanic; scroll is how the visitor performs it.

| Job | Scroll technique | Example of a sourced version |
|---|---|---|
| Reveal the next thing | Element tucked under the previous one slides out as it enters (`animation-timeline: view()`) | Copies pulled from under the sheet above |
| Depth | Layers further from the eye move less (`animation-timeline: scroll()`); two or three depths | Old stamp impressions on the desk blotter drift slower than the paper |
| Wayfinding and progress | A fixed index that follows the section in view | Index tabs on the edge of the book |
| Pacing a sequence | A pinned stage scrubbed by scroll, at most about three viewports | Pouring, assembling, drawing a route (`scroll-parallax.md` §5.3) |
| Payoff | One event the visitor triggers | The stamp landing when the invoice is paid |

Rules: every effect names its job or is cut. Native scroll only, no change of scroll distance. The page is complete without the effect (no support, reduced motion, slow device). One mechanic choreographed across the page beats five different ones. Recipes and support tables: `scroll-parallax.md`.

## 7. Copy

- A headline only this product could carry: a specific noun, number, day or place ("Get paid Thursday"), never a category promise ("Build the future of work", "The all-in-one platform for modern teams").
- No "Empower", "Unlock", "Seamless", "Supercharge", "best-in-class", "cutting-edge". No hedging ("may help you").
- Generated text over-uses some shapes. Pangram measures them per 10,000 words against human writing: em dashes about 10 times, groups of three about 4 times, "not just X but Y" about 3 times. Write plain sentences; keep lists the length the facts are.
- Test from 925studios: would the founder say this sentence aloud to a customer?
- Use the customer's own words from reviews and interviews (`user-research.md`).

## 8. The audit

Run on screenshots at 390 and 1280 px before delivery. All four must pass.

| Test | How | Pass |
|---|---|---|
| Source | List every visible decision (palette, type, shapes, layout idea, each effect) with its source in the subject | No decision without a source |
| Swap | Replace the logo and nouns with a competitor in another trade | The page stops making sense |
| Sibling | Compare with what you would produce for any similar product | The concept, the palette and the main element differ |
| Tell count | Mark every tell from §3 | No group with three or more; none at all from the Honesty group |

Then ask one person who has not seen the brief: "who made this, and for whom?" If the answer is "an AI" or "a template", go back to §4, not to the palette.

## 9. Worked example

`examples/craft-finish/` is an invoicing product. Its first version was cream paper, a serif headline with one italic green word, pill buttons, a soft gradient glow, six equal cards and a dark band: the tasteful swap, complete. The second version replaced it with hairline rules, square corners and monospace uppercase labels: the serious swap. Both were answers to "avoid the last look", and both were rejected for the same reason: nothing in them was about invoices.

The third version started from the object. An invoice book has a white original over a pink and a yellow carbonless copy; rules and labels are printed, entries are typed, the serial number is red, a clerk stamps it PAID, the slip at the bottom is perforated, and it lies on a green desk blotter. The page is that book: the offer is written as an invoice to the visitor, the client's view is the pink duplicate, the change log is the carbon (a dark sheet for a reason), the notes on how the page is made are the conditions on the yellow copy. Scrolling pulls each copy out from under the one above; old impressions on the blotter move more slowly than the paper; paying the duplicate brings the stamp down. Every rule, colour and movement has a line in the source comment at the top of the file.

## Pitfalls

| Symptom | Cause | Fix |
|---|---|---|
| A "distinctive" redesign still reads as generated | One stock look was swapped for another | Start from the subject's artefacts (§4), not from a different style |
| Checked against a ban list, passes, still generic | The list is always one wave behind | The source test and the swap test (§8) |
| Every project ends up with the same "distinctive" fonts and palette | The model's second-favourite choices | A source line per decision; never reuse the previous project's set |
| The concept is specific but the chrome is template | Eyebrows, badges, arrows and stat blocks added out of habit | Remove every label and marker the content does not need |
| Subject-derived look turns into costume | Texture and props piled on (paper grain, coffee rings, drawn objects) | Take structure, colour and behaviour from the artefact; keep surfaces flat and the count of devices low |
| Scroll effects feel bolted on | Chosen from a catalogue | Take the movement from what the subject does (§6) |
| Authentic source, unusable page | The metaphor was put before the task | Usability ladder first (`SKILL.md`): the primary action, contrast, real text and states do not bend to the concept |

## Sources

- Anthropic, Prompting for frontend aesthetics (distributional convergence, purple-gradient default) — https://platform.claude.com/cookbook/coding-prompting-for-frontend-aesthetics
- Anthropic, Improving frontend design through skills — https://claude.com/blog/improving-frontend-design-through-skills
- Anthropic, frontend-design skill (where generated design clusters now; design from the subject's materials and vernacular; the sibling check) — https://github.com/anthropics/skills/blob/main/skills/frontend-design/SKILL.md
- Alan West, Why every AI-built website looks the same (indigo-500) — https://dev.to/alanwest/why-every-ai-built-website-looks-the-same-blame-tailwinds-indigo-500-3h2p
- prg.sh, Why your AI keeps building the same purple gradient website — https://prg.sh/ramblings/Why-Your-AI-Keeps-Building-the-Same-Purple-Gradient-Website
- DevelopersDigest, AI design slop and how to spot it — https://www.developersdigest.tech/blog/ai-design-slop-and-how-to-spot-it
- Noqta, AI design slop: overused UI patterns (2026) — https://noqta.tn/blog/ai-design-slop-overused-ui-patterns-fix-2026
- 925studios, AI slop web design guide — https://www.925studios.co/blog/ai-slop-web-design-guide
- Filip Wojda (regards), Make a website look less vibe-coded — https://www.regards.design/blog/make-website-look-less-vibe-coded
- Velox Themes, How to vibe code a website — https://veloxthemes.com/blog/how-to-vibe-code-a-website
- Codemyspec, Vibe-coded websites look the same (ban one default and the next takes its place) — https://codemyspec.com/blog/vibe-coded-websites-look-the-same
- Kosta Canatselis, Spot the slop: a UI designer's guide to fixing AI defaults — https://world.hey.com/kostac/spot-the-slop-a-ui-designer-s-guide-to-fixing-ai-defaults-4c448c9c
- Pangram, Signs of AI writing (rates per 10,000 words) — https://www.pangram.com/signs-of-ai-writing
- vibecoded-design-tells (tells mined from forum posts; self-reported) — https://github.com/JCarterJohnson/vibecoded-design-tells
