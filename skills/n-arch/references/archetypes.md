# Architecture shapes: signals, layers, seams

> Read when: classifying a repository in step 2 of `SKILL.md`, and drafting its `.ndev.toml` in step 3.

These are structural shapes, not stacks: the same shape appears in NestJS, Laravel, Spring, Go or Django. Pick
by the **signals** you can point at in the repo, not by the framework's name. Real repositories combine shapes
(a monorepo whose services are each hexagonal; a modular monolith with a feature-sliced web client): record each
part with its own shape, and give each part its own layers in `.ndev.toml`, prefixed by its path.

Each entry gives: signals, the usual layers and allowed directions, where the extension seams are, who owns state,
what the contracts are, and what to watch for. The `.ndev.toml` sketch is a starting point to measure (step 3),
never a rule to impose without the count.

## 1. Layered (n-tier)

- **Signals:** top-level folders by technical role — `controllers/`, `services/`, `repositories/`, `models/`; one
  deployable; framework conventions decide most placement.
- **Layers:** presentation → service → data access → model. Services do not import controllers; repositories do not
  import services.
- **Seams:** route files and controller registration; service container bindings; model events and observers.
- **State:** the database through repositories or the ORM; request-scoped state in the framework.
- **Contracts:** the HTTP API, the schema.
- **Watch for:** fat services that hold every rule (deep layering with shallow modules); controllers that query the
  ORM directly; helpers folders that every layer imports.

```toml
[layers.presentation]
paths = ["app/Http/**", "src/controllers/**"]
imports = ["App\\Http"]
may-import = ["service", "model"]
[layers.service]
paths = ["app/Services/**", "src/services/**"]
imports = ["App\\Services"]
may-import = ["data", "model"]
[layers.data]
paths = ["app/Repositories/**", "src/repositories/**"]
imports = ["App\\Repositories"]
may-import = ["model"]
[layers.model]
paths = ["app/Models/**", "src/models/**"]
imports = ["App\\Models"]
```

## 2. Hexagonal, clean, onion (ports and adapters)

- **Signals:** `domain/` (or `core/`, `entities/`) with no framework imports; `application/` or `usecases/`;
  `adapters/`, `infrastructure/`, `ports/`; interfaces declared inside, implemented outside.
- **Layers:** domain ← application ← adapters (inbound: HTTP, CLI, consumers; outbound: DB, queues, other services).
  The domain imports nothing outside itself; adapters may import everything inward.
- **Seams:** a new adapter implementing an existing port; a new use case registered in the composition root.
- **State:** repositories behind ports; the domain holds no I/O.
- **Contracts:** inbound adapters' APIs and messages; outbound adapters' expectations of other systems.
- **Watch for:** ports with a single implementation and no test fake (a hypothetical seam); domain types leaking
  ORM annotations; use cases that only forward to a repository.

```toml
[layers.domain]
paths = ["src/domain/**"]
imports = ["@/domain"]
[layers.application]
paths = ["src/application/**"]
imports = ["@/application"]
may-import = ["domain"]
[layers.adapters]
paths = ["src/adapters/**", "src/infrastructure/**"]
may-import = ["application", "domain"]
```

## 3. Feature-sliced, vertical slices

- **Signals:** `features/<name>/` (or `modules/`, `slices/`) each holding its own UI, handlers, state and tests; a
  small `shared/` or `lib/`; often an `app/` or `pages/` layer that composes features.
- **Layers:** app → pages or routes → features → entities → shared. A feature does not import another feature; it
  goes through an entity, a shared module, or an event.
- **Seams:** a new slice folder plus one registration in the router or the app composition.
- **State:** each slice owns its state; cross-slice state lives in an entity or the server.
- **Contracts:** each slice's public entry file (`index.ts`); deep imports into another slice are the violation.
- **Watch for:** `shared/` growing into a second monolith; slices importing each other's internals.

```toml
[layers.app]
paths = ["src/app/**", "src/pages/**"]
may-import = ["features", "entities", "shared"]
[layers.features]
paths = ["src/features/**"]
may-import = ["entities", "shared"]
[layers.entities]
paths = ["src/entities/**"]
may-import = ["shared"]
[layers.shared]
paths = ["src/shared/**"]
```

Cross-feature imports are same-layer imports, which `.ndev.toml` allows: when they matter, give each feature its
own layer, or keep the repo's lint boundary rule as the authority and say so in the profile.

## 4. Modular monolith

- **Signals:** one deployable, several `modules/<bounded-context>/` each with its own domain, persistence and a
  public API file or facade; modules talk through that API or in-process events.
- **Layers:** per module, often hexagonal; between modules, only the public API.
- **Seams:** in-process events between modules; a module's facade; module registration in the host.
- **State:** each module owns its tables (a schema or a table prefix); no module writes another's tables.
- **Contracts:** each module's facade and events — the future service boundary.
- **Watch for:** joins across module tables; a "common" module every module depends on.

```toml
[layers.orders]
paths = ["src/modules/orders/**"]
imports = ["@/modules/orders"]
may-import = ["shared-kernel"]
[layers.billing]
paths = ["src/modules/billing/**"]
imports = ["@/modules/billing"]
may-import = ["shared-kernel"]
[layers.shared-kernel]
paths = ["src/shared/**"]
```

A module that must call another goes through its facade: give the facade its own layer
(`paths = ["src/modules/billing/api/**"]`, `imports = ["@/modules/billing/api"]`) and allow only that. The most
specific glob and the longest import prefix win, so the facade layer takes precedence over the module around it.

## 5. Services with a backend-for-frontend and events

- **Signals:** several deployables per business area, e.g. a BFF or API gateway service (HTTP edge, no database) and
  one or more domain services (persistence), talking over a broker (Kafka, RabbitMQ, SQS) or RPC; topic naming
  conventions; per-service migrations.
- **Layers:** inside each service, usually hexagonal. Across services: the edge calls domain services through
  messages or RPC only; it never imports their code or reads their database.
- **Seams:** a new message handler or consumer; a new route in the edge that publishes a command; a new topic.
- **State:** each service owns its schema; read models in other services are fed by events (n-dev `../n-dev/references/state.md`).
- **Contracts:** HTTP at the edge, message schemas and topic names between services, permission checks at both ends.
- **Watch for:** shared database access across services; synchronous chains of calls; events without versioning;
  authorization only at the edge.

When the services live in one repo, give each service its own layers, prefixed by its folder; when they live in
separate repos, each repo gets its own profile, and the profile's Contracts table names the others.

## 6. Micro-frontends

- **Signals:** a shell app that loads remotes at runtime (module federation, import maps, single-spa); each remote a
  separate build; a shared design system package.
- **Layers:** shell → remotes' exposed modules → design system and shared contracts. A remote never imports the
  shell or another remote's source.
- **Seams:** a new exposed module in a remote plus one entry in the shell's remote map; routes owned by remotes.
- **State:** each remote owns its UI state; shared session or user context comes from the shell through one
  documented interface; server data through each remote's own query layer.
- **Contracts:** exposed module names and props, shared events, the versions of shared singletons.
- **Watch for:** duplicated singletons (two copies of the router or the design system); remotes reaching into the
  shell's store.

## 7. Monorepo of packages

- **Signals:** workspace file (`pnpm-workspace.yaml`, `package.json` workspaces, `go.work`, Cargo workspace, Nx or
  Turborepo config); `apps/*` and `packages/*` (or `libs/*`).
- **Layers:** apps → feature libraries → domain and utility libraries. Libraries never import apps; a package
  imports another only through its declared public entry and its manifest dependency.
- **Seams:** a new package with its own manifest; a new app composing existing packages.
- **State:** per app; packages stay stateless or own a well-named store module.
- **Contracts:** each package's public entry and version; build and test targets.
- **Watch for:** deep imports into another package's `src/`; circular package dependencies; an internal package
  used by one app only (it may belong inside that app).

```toml
[layers.apps]
paths = ["apps/**"]
may-import = ["libs"]
[layers.libs]
paths = ["packages/**", "libs/**"]
imports = ["@acme/"]
```

## 8. Mobile app

- **Signals:** `ios/` and `android/` folders or a cross-platform project; `screens/`, `navigation/`, `components/`,
  `services/` or `api/`, native modules.
- **Layers:** screens → feature hooks or view models → domain logic and API clients → platform services (storage,
  push, native modules). Components below screens import no API client.
- **Seams:** a new screen registered in the navigator; a new native module behind a JS or Kotlin/Swift interface; a
  deep-link route.
- **State:** server data in a query layer, offline queue and secure storage in one module each, navigation state in
  the navigator.
- **Contracts:** the backend API version the build expects (old app versions stay installed), deep-link URLs, push
  payloads.
- **Watch for:** API calls inside components; an app that breaks when the backend adds a field; platform branches
  scattered instead of one adapter.

## 9. Framework-routed web app (server and client code in one tree)

- **Signals:** file-system routing (`app/` or `pages/` directories), server components or loaders, server actions or
  API routes beside UI files.
- **Layers:** routes → feature modules → domain and data access. Client-only modules never import server-only modules
  (database, secrets); the framework's server/client markers are the boundary.
- **Seams:** a new route segment; a server action in a feature module; a new data-access function.
- **State:** server data in server components or a query cache; URL search params for shareable UI state; forms in
  the form library.
- **Contracts:** route URLs and their params, server action inputs, public API routes.
- **Watch for:** data access inside route files; secrets reachable from client bundles; route files over budget.

```toml
[layers.routes]
paths = ["app/**", "src/app/**"]
may-import = ["features", "server", "ui"]
[layers.features]
paths = ["src/features/**"]
imports = ["@/features"]
may-import = ["server", "ui"]
[layers.server]
paths = ["src/server/**"]
imports = ["@/server"]
[layers.ui]
paths = ["src/components/**"]
imports = ["@/components"]
```

## 10. Library, CLI, scripts

- **Signals:** a published package or a `bin/` entry; no server; tests next to the public API.
- **Layers:** public API (entry file, CLI parser) → core → I/O adapters (file system, network, process). The core
  is pure; the CLI is a thin shell.
- **Seams:** a new command registered in the CLI's command map; a new pure function exported from the entry.
- **State:** none between runs, or one state file written atomically (n-dev `../n-dev/references/security.md`).
- **Contracts:** the public API and its semantic version; CLI flags, exit codes and output formats.
- **Watch for:** breaking the public API in a minor release; `print` and `exit` inside the core.

## 11. Jobs, functions and data pipelines

- **Signals:** handlers per trigger (HTTP, schedule, queue, storage event); DAG or pipeline definitions; transforms.
- **Layers:** trigger handler → pure transform or use case → sinks and sources. Handlers stay thin.
- **Seams:** a new handler with its trigger declared in infrastructure config; a new pipeline step.
- **State:** external stores only; idempotency keys or checkpoints for reruns.
- **Contracts:** event and file schemas, output table shapes, schedules other teams rely on.
- **Watch for:** non-idempotent handlers under at-least-once delivery; transforms that read the clock or the network.

## Measuring a candidate rule

The structure check judges only the lines a change adds, so an existing violation never fails a change. In step 3
the `--all` audit counts every import as added, which makes it the measure of how far the code is from the rule:

Zero findings has two meanings: the code follows the rule, or the check cannot see the imports (an alias, package,
namespace or module path with no `imports` prefix declared, so nothing resolves to the layer). Before reading 0 as
"follows", **prove the rule can fire**: in a scratch copy of the repo, add one import that breaks it, run the check
without `--all`, and see the `layer` finding. No finding means the globs or prefixes are wrong.

| `layer` findings for the rule | Meaning | Do |
|---|---|---|
| 0, and the rule fired on a planted violation | the rule describes the code | enforce it |
| a few, in one or two files | known exceptions | enforce it; list the files as debt in the profile |
| many, spread out | the rule is a target, or the globs are wrong | check the globs; if right, it is a target: step 5's rule settles it |

## Sources

- Martin Fowler, "Presentation Domain Data Layering": https://martinfowler.com/bliki/PresentationDomainDataLayering.html
- Alistair Cockburn, "Hexagonal Architecture": https://alistair.cockburn.us/hexagonal-architecture/
- Jimmy Bogard, "Vertical Slice Architecture": https://www.jimmybogard.com/vertical-slice-architecture/
- Feature-Sliced Design: https://feature-sliced.design/
- Kamil Grzybek, "Modular Monolith: A Primer": https://www.kamilgrzybek.com/blog/posts/modular-monolith-primer
- Martin Fowler and James Lewis, "Microservices": https://martinfowler.com/articles/microservices.html
- Sam Newman, "Backends For Frontends": https://samnewman.io/patterns/architectural/bff/
- Cam Jackson, "Micro Frontends": https://martinfowler.com/articles/micro-frontends.html
- Nx, "Enforce Module Boundaries": https://nx.dev/features/enforce-module-boundaries
- Simon Brown, "The C4 model": https://c4model.com/
- Michael Nygard, "Documenting Architecture Decisions": https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions
- Neal Ford, Rebecca Parsons, Patrick Kua, *Building Evolutionary Architectures* (fitness functions): https://www.oreilly.com/library/view/building-evolutionary-architectures/9781492097532/
- Adam Tornhill, *Your Code as a Crime Scene* (hot spots: change frequency × complexity): https://pragprog.com/titles/atcrime2/your-code-as-a-crime-scene-second-edition/
- dependency-cruiser: https://github.com/sverweij/dependency-cruiser
- import-linter: https://github.com/seddonym/import-linter
- ArchUnit: https://www.archunit.org/
