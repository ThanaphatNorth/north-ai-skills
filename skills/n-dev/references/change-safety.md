# Change safety: contracts, data, rollout, failure, signals

> Read when: the change is Large, or it touches something another party depends on — an HTTP/RPC API, an event or
> queue message, a shared table or schema, a migration, a cache key, a config or env var other services read, a
> job schedule, or the way the code is deployed (step 3 of `SKILL.md`, and the step 6 pass over the diff).

Small, verified code can still break production when the world around it moves at a different speed: an old
client still calls the old shape, a consumer still reads yesterday's event, a rollback runs old code on a new
schema. This file is the minimum a Large change answers in its design note. If the `inv-nfr` skill is installed,
run it for the full non-functional pass (performance, security, operability); this file does not repeat it.

Every row is a question answered with a test, a command, or a line in the design note — not with an opinion.

## 1. Contracts: the other side has not deployed yet

A **contract** is any shape another process reads or writes: request and response bodies, status codes and error
shapes, event payloads and topic names, table columns read by another service, file formats, CLI flags, env vars.

| Ask | Safe move | Unsafe move |
|---|---|---|
| Is the change additive? | add an optional field, a new endpoint, a new event type, a new topic | rename, remove, retype, or make a field required |
| Do readers tolerate it? | readers ignore unknown fields (tolerant reader) | readers that fail on extra fields, or exhaustive enums without a default |
| Is meaning stable? | a new field for a new meaning | the same field reused for a new meaning |
| Is a breaking change unavoidable? | a new version beside the old (`/v2`, `order.created.v2`), both live until the last consumer moves | changing the shape in place and "deploying everything together" |
| Who are the consumers? | named in the design note, from code search, the API gateway, topic subscriptions, the schema registry | "probably nobody" |

- Breaking changes go through **expand, migrate, contract** (parallel change): add the new shape, move every
  reader and writer to it, then remove the old shape in a later change once nothing uses it.
- Pin the contract with a test at the seam: a schema or snapshot test of the response or event, or a
  consumer-driven contract test (Pact or the repo's equivalent) when the consumer lives in another repo.
- Error shapes are part of the contract. A new error code is additive; a changed status code is breaking.
- Protobuf, Avro, JSON Schema and OpenAPI have their own compatibility rules: follow the registry or the linter the
  repo already runs, and never reuse a removed field number or name.

## 2. Data: the migration runs before, during and after the code

| Ask | Answer with |
|---|---|
| Does the old code still run against the new schema? (it will, during the deploy and after a rollback) | the migration is additive in this change; destructive steps come later |
| Does the new code run against the old schema? (it may, if the code ships first) | a guard, or a deploy order written in the design note |
| Is the migration safe to run twice, and safe to stop halfway? | idempotent statements; backfills in batches with a resume point |
| Does it lock a large table? | the database's online form (`CONCURRENTLY`, online DDL, batched updates); timing measured on a copy |
| Is anything deleted or overwritten? | never inside a migration: a separate, reviewed cleanup with a dry run and a backup or archive first |
| Where was it tested? | on a copy of the target data, not only an empty test database |

- Expand and contract applies to data too: add the new column (nullable or with a default), write both, backfill,
  read the new one, stop writing the old, then drop the old column in a later release.
- Generated columns, views and selectors are derived values (`state.md`); they need no backfill.
- A migration that has run in any shared environment is never edited; a fix is a new migration.

## 3. Rollout and rollback

| Ask | Answer with |
|---|---|
| How is the change turned on? | at deploy, or behind a flag with an owner and a removal date |
| How is it turned off in minutes? | flag off, or redeploy the previous build — and that build works with the new schema (section 2) |
| Who sees it first? | a dark launch, an internal cohort, a canary, or a percentage; the design note names the first audience |
| What says "roll back now"? | the signal from section 5 and its threshold, written down before the rollout |

- A flag is a rollout tool, not a fork (`extension.md` § Anti-patterns): the change that adds it names the change
  that removes it.
- Jobs and consumers deploy too: a new consumer reading an old topic, a cron that runs during the deploy, a queue
  that still holds messages in the old shape — each gets a line in the plan.
- Long requests and in-flight work need a drain time at deploy; a platform default of zero cuts them off.

## 4. Failure modes at every new seam

For each new call to something outside the process (HTTP, database, queue, cache, file system, another service):

| Ask | Default |
|---|---|
| Timeout? | every outbound call has one, shorter than the caller's own deadline |
| Retry? | only idempotent operations; capped, with exponential backoff and jitter; never retry a 4xx that will fail again |
| Idempotent? | writes that can be retried carry an idempotency key, or are naturally idempotent (upsert by business key) |
| Delivered twice? | message consumers are at-least-once: a second delivery is a no-op, tested |
| Partial failure? | a multi-step write is one transaction, or an outbox/saga with a compensating step |
| Dependency down? | the behaviour is decided (fail fast, degrade, queue) and tested with the dependency stubbed to fail |
| Unbounded? | queries paginated, bodies and uploads size-limited, loops bounded (`security.md` § Input size and time) |
| Client went away? | long work is not tied to the client's connection signal unless cancelling it is the intent |

## 5. Signals: how you will know it works in production

- **Logs**: one structured line at each decision the new code makes, with the correlation or request id; no secrets,
  no personal data beyond what the repo already logs.
- **Metrics**: a counter for the new path's outcomes (success, each failure reason) and a latency histogram for any new
  outbound call.
- **Traces**: the new outbound calls appear as spans, if the repo traces at all.
- **Alerts**: page on user impact (error rate, latency, a stuck queue), not on a single log line; classify client
  faults by their exact message so a user's cancelled request does not page anyone.
- The design note names the one signal that says "it works" and the one that says "roll back".

## 6. Data access cost

- Every new query states its index: the `WHERE` and `ORDER BY` columns exist in an index, or the table is small and
  says so.
- No query in a loop (N+1): load by a set of ids, or join.
- Reads of large or JSON-heavy rows are paged, with a page size, and memory measured on realistic data.
- A transaction that waits on locks has a timeout sized to the work, and its failure maps to a retryable error.

## Checklist for the design note (Large)

- [ ] Every contract the change touches is listed with its consumers, and each change is additive or versioned.
- [ ] Each breaking change has its expand, migrate and contract steps, and this change is only the first.
- [ ] The migration is additive, idempotent, online, tested on a copy, and deletes nothing.
- [ ] The previous build runs against the new schema (rollback works).
- [ ] The rollout names its first audience, its off switch, and the flag's removal date.
- [ ] Each new outbound call has a timeout, a retry rule, and a tested failure behaviour.
- [ ] Consumers are idempotent, with a test for the second delivery.
- [ ] The success signal and the rollback signal are named.
- [ ] Each new query has its index, and nothing loads unbounded rows.

## When it does not apply

A Standard change that touches no contract, schema, deploy setting or outbound call says so in one line in the
report: "no contract, data or rollout impact". A Tiny change skips this file.

## Sources

- Martin Fowler / Danilo Sato, "Parallel Change" (expand and contract): https://martinfowler.com/bliki/ParallelChange.html
- Martin Fowler, "Tolerant Reader": https://martinfowler.com/bliki/TolerantReader.html
- Pete Hodgson, "Feature Toggles (aka Feature Flags)": https://martinfowler.com/articles/feature-toggles.html
- Pact, consumer-driven contract testing: https://docs.pact.io/
- Protocol Buffers, "Updating A Message Type": https://protobuf.dev/programming-guides/proto3/#updating
- Semantic Versioning 2.0.0: https://semver.org/
- AWS Builders' Library, "Timeouts, retries, and backoff with jitter": https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/
- AWS Builders' Library, "Making retries safe with idempotent APIs": https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/
- Stripe, "Designing robust and predictable APIs with idempotency": https://stripe.com/blog/idempotency
- Chris Richardson, "Pattern: Transactional outbox": https://microservices.io/patterns/data/transactional-outbox.html
- Google SRE Book, "Addressing Cascading Failures": https://sre.google/sre-book/addressing-cascading-failures/
- Google SRE Book, "Monitoring Distributed Systems" (the four golden signals): https://sre.google/sre-book/monitoring-distributed-systems/
- OpenTelemetry, "Traces": https://opentelemetry.io/docs/concepts/signals/traces/
- The Twelve-Factor App, "Disposability": https://12factor.net/disposability
- PostgreSQL, "CREATE INDEX — Building Indexes Concurrently": https://www.postgresql.org/docs/current/sql-createindex.html#SQL-CREATEINDEX-CONCURRENTLY
