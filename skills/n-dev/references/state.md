# State with one owner

> Read when: the change adds, moves, copies or caches any state — UI state, server data on the client, forms, URL parameters, sessions, caches, configuration, database rows or files (steps 1 and 3 of `SKILL.md`).

## The rule: every fact has exactly one owner

Vocabulary used in the design note:

- **Fact** — one piece of information the system holds: "the cart's items", "the selected tab", "the user's locale", "the order's status".
- **Owner** — the single place where that fact is stored and authoritative. If two places disagree, the owner is right by definition.
- **Writer** — the one module allowed to change it. Every change goes through it, so its invariants hold.
- **Reader** — anything that reads it, through a selector, query or getter the owner exposes.
- **Derived value** — anything computable from owned facts (totals, counts, `isEmpty`, filtered lists, "can submit"). It is computed, never stored.
- **Copy** — a stored duplicate of a fact owned elsewhere. Allowed only as a cache with a named invalidation rule.

The aim is the Redux principle ("a single source of truth") applied everywhere, not a single global store: each fact has one home, and different facts can live in different homes.

## The state ownership table

Every Standard or Large task fills this table in the design note:

| Fact | Owner | Writer | Readers | Derived from it | Copies + invalidation |
|---|---|---|---|---|---|
| Cart items | server (`carts` table), cached by the query layer under `["cart", id]` | `cartApi.updateItems` mutation | `CartPage`, `CheckoutSummary` via `useCart(id)` | `subtotal`, `itemCount` in `cartSelectors.ts` | query cache, invalidated on mutation success |
| Selected tab | URL `?tab=` | `useTabParam().setTab` | `OrdersTabs` | — | — |
| Coupon draft | coupon form state | the form | `CouponField` | `isValid` from the schema | — |

*Done* means: every fact appears once in the Fact column; every Owner cell names one place; every derived value names its function; every copy names its invalidation trigger.

## Where each kind of state lives

| Kind of fact | Owner | Typical mechanism | Anti-pattern |
|---|---|---|---|
| Persistent business data | the database of the service that owns it | tables + constraints; one service writes its tables | another service writing the same table; a second copy in another DB without an event feed |
| Server data shown on a client | the server, cached by a server-state layer | TanStack Query, SWR, RTK Query, Apollo, Laravel/Inertia props | copying query results into a global store or `useState` and keeping them in sync by hand |
| Shareable UI position (filters, search, sort, page, tab, selected id) | the URL | router search params | the same value in a store *and* the URL |
| Form drafts | the form | form library state or the form component | mirroring each field into a global store |
| Local, ephemeral UI (open, hover, focus) | the component | local state | lifting it into a global store "in case" |
| Cross-cutting client state (session, theme, offline queue) | one store module per concern | Zustand / Redux slice / context / Pinia; native secure storage for tokens | several modules each keeping their own copy of the session |
| Configuration and environment | one config module, validated at startup | typed settings object built from env | `process.env.X` / `env('X')` read all over the codebase |
| Derived values | the function that computes them | selector, memoized computation, SQL view, generated column | a stored `total` beside the items it sums |

## Model the shape so wrong states cannot exist

"Make impossible states impossible" (Richard Feldman):

- Replace boolean clusters with a **discriminated union** (sealed class, enum with payload). Three booleans allow eight combinations, and most are nonsense.

  ```ts
  type Load<T> =
    | { status: "idle" }
    | { status: "loading" }
    | { status: "success"; data: T }
    | { status: "error"; error: AppError };
  ```

  ```kotlin
  sealed interface Load<out T> {
      data object Idle : Load<Nothing>
      data object Loading : Load<Nothing>
      data class Success<T>(val data: T) : Load<T>
      data class Error(val error: AppError) : Load<Nothing>
  }
  ```

- For a flow with steps (checkout, upload, sign-in, approval), write an explicit **state machine**: the states, the events, and a pure `transition(state, event) → state`. A library (XState and others) is optional; the pure function is the essential part, and it belongs to the functional core.
- **Normalize** collections: store entities once, keyed by id, and refer to them by id. A list of objects plus a "selected object" duplicates that object; a list plus a `selectedId` does not.
- Use **ids, not array indexes**, to point at things that can be reordered or removed.
- Store **raw facts**, format at the edge: amounts in minor units with a currency, timestamps in UTC; formatting is derived.

## One way in: writes go through one module

- The owner exposes named operations (`addItem`, `applyCoupon`, `markPaid`). Callers never mutate the stored structure directly.
- Invariants (quantity ≥ 1, status transitions allowed) are enforced in the writer, once, and tested there.
- On the backend, the domain service that owns a table is its only writer; database constraints (unique, foreign key, check) back up the invariants the writer enforces.
- Multi-step writes that must agree happen in one transaction or one command; a client never sequences several writes that leave the system inconsistent if one fails.

## Reads: selectors and derivation

- Readers get data through selectors or hooks that live beside the owner (`cartSelectors.ts`, `useCart`). The owner can then change its storage shape without touching readers.
- Derived values are computed on read. Memoize when a measurement shows the cost matters (`useMemo`, `createSelector`, a cached property), and keep the memoization inside the selector, not in the caller.
- In React, adjusting state from props or other state inside an effect usually means the value is derived: compute it during render instead ("You Might Not Need an Effect").

## When a copy is unavoidable

Sometimes a copy is the design: an offline cache, a read model in another service, an optimistic update. Then the design note names, for each copy:

- **Owner** of the original, and the copy's **key**.
- **Invalidation trigger**: mutation success, an event, a TTL, a version or ETag check.
- **Conflict rule**: which side wins and how a rejected optimistic change rolls back.
- **Direction**: data flows owner → copy only. A copy never writes back except through the owner's writer.

## Server, cache and data layers

- **HTTP caches and CDNs**: the response is a copy; cache headers are its invalidation rule.
- **Application caches** (Redis, in-memory): key naming, TTL and the event that evicts — in one module next to the owner's writer, so a write and its eviction cannot be separated.
- **Read models and projections** in other services: fed by events from the owner, rebuilt from them, never edited by hand.
- **Files and blobs**: the database row that references the file is the owner of "which file is current"; the storage bucket holds bytes, not truth.

## Checklist

- [ ] Every fact the change touches appears once in the ownership table.
- [ ] No value is stored that can be computed from stored values.
- [ ] Server data is not copied into client state outside the server-state layer.
- [ ] URL-worthy UI state lives in the URL only.
- [ ] Status fields are unions or state machines, not boolean clusters.
- [ ] Writes go through one named module per owner; invariants are tested there.
- [ ] Every copy names its invalidation trigger and conflict rule.
- [ ] Configuration is read through one validated module.

## Sources

- Redux, "Three Principles" (single source of truth): https://redux.js.org/understanding/thinking-in-redux/three-principles
- Redux, "Normalizing State Shape": https://redux.js.org/usage/structuring-reducers/normalizing-state-shape
- React, "Choosing the State Structure": https://react.dev/learn/choosing-the-state-structure
- React, "You Might Not Need an Effect": https://react.dev/learn/you-might-not-need-an-effect
- TanStack Query, "Does TanStack Query replace Redux, MobX or other global state managers?": https://tanstack.com/query/latest/docs/framework/react/guides/does-this-replace-client-state
- Richard Feldman, "Making Impossible States Impossible" (elm-conf 2016): https://www.youtube.com/watch?v=IcgmSRJHu_8
- Stately, "State machines and statecharts": https://stately.ai/docs/state-machines-and-statecharts
- The Twelve-Factor App, "Config": https://12factor.net/config
- Martin Fowler, "CQRS": https://martinfowler.com/bliki/CQRS.html
- MDN, "HTTP caching": https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching
