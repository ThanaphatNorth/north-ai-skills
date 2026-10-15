# Structure: modular, functional, reusable

> Read when: deciding how to split a change into files and modules, whether to reuse, extract or inline, how large a file or function may grow, which way dependencies may point, or reviewing a diff for structure (steps 3, 5 and 6 of `SKILL.md`).

## Simple, not easy

Rich Hickey's distinction carries rule 1. **Simple** is the opposite of *complex* (entangled): one role, one concept, no braiding of unrelated concerns. **Easy** is the opposite of *hard*: near at hand, familiar. One long file is easy and complex; a few focused modules are less easy to type and simpler to change.

What this does **not** mean: more scope. The Karpathy scope rule stays whole — no feature, option, flag, setting or error branch the request did not ask for. Effort goes into the *shape* of the code that the request needs, never into code the request does not need.

| Easy (avoid) | Simple (prefer) |
|---|---|
| Add the feature inside the 800-line file that is already open | A new module with one job, wired in with two lines |
| Copy the similar function and change three lines | Reuse it, or pull the shared core out and call it from both |
| Fetch, decide, format and save in one function | A pure `decide()` plus a shell that fetches and saves |
| A boolean flag that makes one function behave two ways | Two functions that share a named helper |
| A `utils.ts` that collects anything | A module named for the concept it holds (`money.ts`, `dateRange.ts`) |

## Module shape: deep, one responsibility

A **module** is anything with an interface and an implementation: a function, a file, a class, a package. Aim for **deep** modules — much behaviour behind a small interface (Ousterhout).

Three tests for every module in the design note:

1. **Name test.** Its responsibility fits in one sentence without "and". "Calculates the shipping fee for a cart" passes; "loads the cart and calculates the fee and renders the summary" is three modules.
2. **Deletion test.** Imagine deleting it. If the complexity disappears with it, it was a pass-through — merge it into its caller. If the complexity reappears in every caller, it earns its place.
3. **Interface test.** A caller needs to learn little: few parameters, no required call order, errors in one consistent form. If a test has to reach past the interface to check behaviour, the module is the wrong shape.

Shallow traps that over-modularisation produces:

- **Pass-through wrappers** — `UserService.get()` that only calls `userRepo.get()`.
- **One-function-per-file shredding** — ten 8-line files that must be read together to understand anything. Keep things that change together in one module.
- **Interface + single implementation** — "one adapter is a hypothetical seam, two adapters is a real one". Introduce a port when a second implementation exists (production + test fake counts).
- **Layers for their own sake** — controller → service → manager → repository, where three of the four only forward.

## Functional core, imperative shell

Gary Bernhardt's split makes code modular and testable at once:

- The **core** is pure functions: input in, value out, no I/O, no clock, no randomness, no mutation of arguments. Business rules, calculations, validation, mapping and decisions live here.
- The **shell** is thin: it reads (HTTP, DB, files, time, env), calls the core, and writes the result. It has few branches.
- Dependencies are **passed in**, never created inside (`function charge(order, gateway)`, not `new StripeGateway()` in the body). The shell or the DI container wires them.
- Functions **return results** instead of mutating shared objects.

```ts
// core: pure, tested without mocks
export function shippingFee(cart: Cart, rules: FeeRules): Money { /* ... */ }

// shell: I/O only, tested once through its interface
export async function quoteShipping(cartId: string, deps: { carts: CartRepo; rules: RulesRepo }) {
  const [cart, rules] = await Promise.all([deps.carts.get(cartId), deps.rules.current()]);
  return shippingFee(cart, rules);
}
```

```python
# core
def shipping_fee(cart: Cart, rules: FeeRules) -> Money: ...

# shell
def quote_shipping(cart_id: str, carts: CartRepo, rules: RulesRepo) -> Money:
    return shipping_fee(carts.get(cart_id), rules.current())
```

The same split holds in any language: a reducer is a core, a React component that only renders props is a core, a NestJS provider that only calls the DB is a shell.

## Where code goes: features and dependency direction

- **Colocate by feature.** Code that changes together lives together (`features/checkout/` holds its UI, hooks, core and tests). A `shared/` or `lib/` module is for code with callers in two or more features.
- **Dependencies point inward**: UI and transport → application (use cases) → domain core. The core imports nothing from frameworks, transport or storage. This is the dependency rule of hexagonal (ports and adapters) and clean architecture.
- **No import cycles.** A cycle means two modules are one module in disguise, or a third concept wants extracting. Go refuses cycles; elsewhere, use what the repo already has: `import/no-cycle` or `eslint-plugin-boundaries`, dependency-cruiser or madge (JS/TS), import-linter (Python), Deptrac (PHP), ArchUnit (JVM).
- **Follow the repo's layout first.** If it is layered (`controllers/`, `services/`), add the new module in that layout rather than introducing feature folders beside it.

## Reuse: inventory first, extract on evidence

GitClear's analysis of 211 million changed lines (2020–2024) reports fourfold growth in code clones, and 2024 as the first year in which copy-pasted lines outnumbered moved (refactored) ones; it attributes part of this to assistants not surfacing existing functions. Its 2026 follow-up reports cross-file function calls — a sign of reuse — down 35 % and refactoring moves down 70 % against 2022. Vendor data on its own customer sample, so read the numbers as direction, not precision. The cheapest reuse is the code that already exists, which is why Orient builds a **reuse inventory**:

- Search the task's verbs and nouns (`grep -rn "formatMoney\|currency" src/`), the repo's `hooks/`, `utils/`, `lib/`, `services/`, `shared/` folders, and its dependencies (a date or validation library may already be installed).
- Read how the most recent similar feature was built and reuse its pieces.
- Record what was found, or "none found" with the search terms, in the design note.

When to **extract** a shared module:

- A **second real caller** exists now (the rule of three is a softer form: by the third copy, extract).
- The code names a **domain concept** or a policy that must stay consistent everywhere (rounding money, a permission rule) — extract even with one caller, because the name and the tests are the value.

When **not** to, or when to inline back (Sandi Metz, "the wrong abstraction"):

- The only caller is hypothetical.
- Merging two callers needs a flag or a mode parameter per caller — they are two behaviours; share only the part that is truly the same.
- An existing abstraction has grown a conditional for each caller: inline it back into the callers, then re-extract what is really shared.

## Size budgets (heuristics, not laws)

No study isolates file length as the cause of agent or human errors; the budgets below are review-size heuristics. They keep each piece readable in one sitting and keep diffs small enough to review (Google's guidance on small changes). The repo's lint config overrides them, looser or stricter.

| Thing | Default budget | `structure_check.py` flag |
|---|---|---|
| Source file | 300 lines | `--max-file` |
| Test file | 600 lines | `--max-test-file` |
| Function / method | 50 lines | `--max-func` |
| Wiring diff in a pre-existing source file | 20 added lines (removed lines and test files do not count) | `--max-wiring` |
| Copied block | 6 matching lines | `--dup-lines` |
| Parameters | 4 (beyond that, one options object) | — |
| Nesting depth | 3 (beyond that, early return or extract) | — |

UI components count as functions: a 90-line component usually holds two or three components (a form, a field group, a summary). Over budget means *split by responsibility*, never by line count. `orderForm.part2.ts` is not a split; `orderForm.validation.ts` beside `orderForm.ts` is.

## Interfaces, types and errors

- Give module interfaces explicit types; no `any`, untyped dicts or stringly-typed modes at a seam.
- **Parse, don't validate** (Alexis King): check untrusted input once, at the boundary, and turn it into a type that cannot be invalid. The core then trusts its inputs instead of re-checking them.
- One error style per layer, matching the repo: typed errors, result values, or exceptions mapped at the edge. Handle errors that can actually happen; the scope rule rules out branches for impossible ones.

## Naming

Name modules for what they hold (`invoiceTotals`, `seat_allocation`), functions for what they do (`allocateSeats`), and booleans as questions (`isPaid`). Avoid `helpers`, `misc`, `common`, `manager`, `new`, `v2` — they name a drawer, not a concept.

## Review checklist (step 6)

- [ ] Every new file passes the name test: one sentence, no "and".
- [ ] No module fails the deletion test (no pass-through wrapper).
- [ ] Decisions and calculations are in pure functions with tests that need no mocks.
- [ ] Dependencies are passed in at the shell; nothing in the core does I/O.
- [ ] Nothing from the reuse inventory was re-implemented; `structure_check.py` reports no copied block, or each one has a reason.
- [ ] No feature, option, flag or config beyond the request.
- [ ] Dependencies point inward; no new import cycle.
- [ ] Files and functions are within budget, or the report says why.
- [ ] Pre-existing files carry only a wiring diff, or the edit is a recorded exception (`extension.md`).
- [ ] Every fact has one owner and derived values are computed (`state.md`).
- [ ] Each success criterion has a test that was seen red and then green.

## Sources

- Rich Hickey, "Simple Made Easy" (Strange Loop 2011): https://www.infoq.com/presentations/Simple-Made-Easy/
- John Ousterhout, *A Philosophy of Software Design* (deep modules): https://web.stanford.edu/~ouster/cgi-bin/book.php
- Gary Bernhardt, "Functional Core, Imperative Shell": https://www.destroyallsoftware.com/screencasts/catalog/functional-core-imperative-shell
- Sandi Metz, "The Wrong Abstraction": https://sandimetz.com/blog/2016/1/20/the-wrong-abstraction
- Kent C. Dodds, "AHA Programming": https://kentcdodds.com/blog/aha-programming
- Kent C. Dodds, "Colocation": https://kentcdodds.com/blog/colocation
- Martin Fowler, "Yagni": https://martinfowler.com/bliki/Yagni.html
- Martin Fowler, "Function Length": https://martinfowler.com/bliki/FunctionLength.html
- Alistair Cockburn, "Hexagonal Architecture": https://alistair.cockburn.us/hexagonal-architecture/
- Alexis King, "Parse, don't validate": https://lexi-lambda.github.io/blog/2019/11/05/parse-don-t-validate/
- GitClear, "AI Copilot Code Quality" 2025 research: https://www.gitclear.com/ai_assistant_code_quality_2025_research
- GitClear, "The Maintainability Gap" 2026 research: https://www.gitclear.com/the_ai_code_quality_maintainability_gap
- Google Engineering Practices, "Small CLs": https://google.github.io/eng-practices/review/developer/small-cls.html
- dependency-cruiser: https://github.com/sverweij/dependency-cruiser
- import-linter: https://github.com/seddonym/import-linter
- Deptrac: https://github.com/deptrac/deptrac
