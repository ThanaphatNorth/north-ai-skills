# Extending existing code

> Read when: the change touches any file that existed before the task — to decide between extending beside it and editing in place, to find the repo's extension points, and to keep the original behaviour safe (steps 1, 3 and 4 of `SKILL.md`).

## The rule: extend beside, wire at a seam

New behaviour lives in new files. A pre-existing file receives only a **wiring diff** — the smallest change that lets the codebase reach the new module:

- an `import` (or `use`, `require`, DI binding);
- a registration line: a route, a handler in a map, a provider in a module, a listener, a menu item;
- a composition point: rendering a new component, wrapping an existing function, adding a middleware;
- a delegating branch: a new `case` that calls the new module and contains no logic of its own.

Budget: about 20 added lines per pre-existing source file (`--max-wiring` in `structure_check.py`; removed lines do not count, so moving code out is never penalised, and test files may grow freely). The Karpathy surgical test still applies to every one of those lines: each traces directly to the request.

Why: the original is already tested and in production, and other code depends on its exact behaviour (Hyrum's law: with enough users, every observable behaviour is depended on). Keeping new logic out of it limits the blast radius, keeps the review of old files small, and makes the new feature removable by deleting its files and its wiring. This is the open–closed principle in practice: open for extension, closed for modification.

## Decision: extend or edit in place

| Situation | Do |
|---|---|
| New behaviour that sits alongside existing behaviour | New module + wiring diff |
| A bug in the existing logic | Fix in place, surgically, with a regression test that was red first |
| The existing decision must change for everyone (the business rule itself changed) | Edit in place — the rule has one owner; a wrapper that overrides it would create two |
| New behaviour must alter an existing decision for some cases | If the decision is already a function or strategy: wrap or register a new strategy. If it is inline branching inside a long function: preparatory refactor (below), then extend |
| Extending would copy most of the original | Edit in place, or extract the shared core and call it from both — never fork a near-copy |
| The task needs a rename or move of existing code | Not part of the request: mention it, and do it only if the user agrees |
| Generated code, vendored code, lockfiles, migrations already applied | Never edit; extend through configuration, hooks, a new migration, or regeneration |

Each in-place edit is recorded in the design note's extension plan with its reason, and shown in the final report.

## Finding the repo's extension points

Orient records how *this* codebase adds things. The fastest source is its own history:

1. Find a recent commit that added something similar: `git log --oneline -- src/features/ | head`, or `git log -S "registerRoute" --oneline`.
2. Read that commit's diff (`git show <sha> --stat`, then the files). The pattern of new files plus small edits *is* the recipe.
3. List the seams it used. Common ones:
   - **Registries**: route tables, command maps, plugin or module lists, DI modules (NestJS `@Module`, Laravel service providers, Spring configuration, Angular providers).
   - **Events and hooks**: domain events, lifecycle hooks, signals, observers, webhooks, message consumers.
   - **Middleware and interceptors**: HTTP middleware, guards, pipes, Axios or fetch interceptors, Redux middleware.
   - **Composition in UI**: wrapping components, slots and children, custom hooks, route-level layouts.
   - **Strategies**: a map from key to implementation, a factory selected by config.
   - **Language features**: extension functions, protocol extensions, traits, mixins, module augmentation, partial classes.
4. If the codebase has no seam where the task needs one, the next step is a preparatory refactor, not an in-place feature.

## Translation table: one principle, many ecosystems

Examples only — use the mechanism the repo already uses.

| Need | JS / TS | React / React Native | Python | PHP / Laravel | Kotlin / Java | Swift | Go | C# |
|---|---|---|---|---|---|---|---|---|
| Add behaviour without editing the original | new module + wrapper function | new component composing the old one; custom hook | new module; decorator | new class; service provider binding | new class; Kotlin extension function | protocol extension; new type | new function taking the interface | extension method; new class |
| Add a handler | entry in a handler map / router | new route entry or screen in the navigator | entry in a dict registry; entry point | route file line; listener in `EventServiceProvider` | `@Component` bean; `when` branch delegating | new case delegating | `mux.Handle(...)` line | DI registration |
| Wrap existing behaviour | higher-order function | HOC or wrapper component | decorator; context manager | middleware; decorator class | decorator (delegation) | wrapper type | middleware func | decorator via DI |
| React to something | event emitter; observer | effect on a store subscription | signals; observer | events + listeners | Spring events; Flow collector | Combine / NotificationCenter | channel consumer | events; MediatR handlers |
| Extend a third-party type | module augmentation / declaration merging | same | subclass or adapter | macro (`Macroable`) | extension function | extension | wrapper type (embedding) | extension method |

Caveats:

- **Extension functions and methods** (Kotlin, Swift, C#) are statically dispatched and cannot reach private members. They suit helpers on a type; they do not override behaviour.
- **TypeScript module augmentation** changes types, not runtime behaviour; pair it with real code that implements what the types claim.
- **Subclassing** only where the repo already extends that class by inheritance; otherwise prefer composition.
- **Go embedding** promotes methods; it is composition, not inheritance, and the outer type can shadow a method — say so in the design note when you do it.

## Patterns in detail

**Wrapper (decorator).** The new behaviour takes the original and returns something with the same interface:

```ts
// new file: withAuditLog.ts
export const withAuditLog = (repo: OrderRepo, audit: Audit): OrderRepo => ({
  ...repo,
  async save(order) {
    const saved = await repo.save(order);
    await audit.record("order.saved", saved.id);
    return saved;
  },
});
// wiring diff in the composition root: orders: withAuditLog(makeOrderRepo(db), audit)
```

**Registry / strategy.** The original looks up an implementation by key; the extension adds a key:

```python
# new file: payments/promptpay.py
class PromptPay:
    def charge(self, order): ...

# wiring diff in payments/registry.py
PROVIDERS["promptpay"] = PromptPay
```

**Event listener.** The original emits; the extension listens. Nothing in the original changes except, at most, emitting an event it did not emit before (that line is the wiring diff).

**New component composing the old one.** `OrderSummaryWithCoupon` renders `OrderSummary` and adds the coupon block, instead of adding a `showCoupon` prop to `OrderSummary` — unless every user of `OrderSummary` should get it, in which case the component itself owns the change.

## Anti-patterns

- **Monkey-patching**: reassigning methods on imported objects, mutating prototypes, overriding modules at runtime. Behaviour changes with no trace at the call site.
- **Copy-and-modify**: `UserServiceV2` that duplicates 90 % of `UserService`. Two owners of the same rules drift apart.
- **Shadow files**: a file that re-exports everything from the original and changes one function — callers silently get different behaviour depending on which they import.
- **Reaching into internals**: an extension that depends on private fields or undocumented order of calls breaks on the next refactor of the original.
- **Permanent feature flags as forks**: a flag is a rollout tool with a removal date, not a way to keep two versions of a module.
- **Wiring that grows logic**: a "registration" line that slowly acquires conditions and mapping. Move that logic into the new module.

## Preparatory refactor: when the seam is missing

"Make the change easy, then make the easy change" (Kent Beck, via Martin Fowler). When the logic you must extend is buried inside a long function:

1. **Pin the current behaviour** with characterization tests: run the code, record what it actually does, assert exactly that (Michael Feathers). They must pass before and after.
2. **Extract the seam** with zero behaviour change: pull the decision into a function or strategy, as small as the task needs. Commit this separately, with its own message, so the review can check "no behaviour change" on its own.
3. **Extend** at the new seam with new files.
4. **Record it** in the extension plan and the report as an in-place edit with its reason. If the extraction would touch code paths the task does not use, or change a public interface, stop and ask (design-note stop rule).

## Keeping the original safe

- Run the existing tests that cover the touched files **before** you change anything; a red suite at the start is reported, not silently fixed.
- Keep the public interface of the original unchanged: names, signatures, return shapes, error types, timing guarantees.
- Read every changed line of every pre-existing file in the final diff (`git diff <base> -- <file>`), and list those files in the report.
- `structure_check.py` flags pre-existing files whose change exceeds the wiring budget; each one is fixed or carries a reason.

## Sources

- Bertrand Meyer's open–closed principle (overview): https://en.wikipedia.org/wiki/Open%E2%80%93closed_principle
- Hyrum's law: https://www.hyrumslaw.com/
- Martin Fowler, "An example of preparatory refactoring": https://martinfowler.com/articles/preparatory-refactoring-example.html
- Martin Fowler, "Strangler Fig Application": https://martinfowler.com/bliki/StranglerFigApplication.html
- Characterization test (Michael Feathers, *Working Effectively with Legacy Code*): https://en.wikipedia.org/wiki/Characterization_test
- Kotlin, "Extensions": https://kotlinlang.org/docs/extensions.html
- Swift, "Extensions": https://docs.swift.org/swift-book/documentation/the-swift-programming-language/extensions/
- C#, "Extension members": https://learn.microsoft.com/en-us/dotnet/csharp/programming-guide/classes-and-structs/extension-methods
- TypeScript, "Declaration Merging" (module augmentation): https://www.typescriptlang.org/docs/handbook/declaration-merging.html
- React, "Reusing Logic with Custom Hooks": https://react.dev/learn/reusing-logic-with-custom-hooks
- NestJS, "Modules": https://docs.nestjs.com/modules
- Laravel, "Service Providers": https://laravel.com/docs/12.x/providers
- Python, `functools.singledispatch`: https://docs.python.org/3/library/functools.html#functools.singledispatch
- Go, "Effective Go — Embedding": https://go.dev/doc/effective_go#embedding
