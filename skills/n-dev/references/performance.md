# Performance: cost that grows with data, users or input

> Read when: the change reads or writes stored data, loops over input or stored records, calls the network or
> another process, adds a cache, changes what a response or the client bundle carries, or migrates data
> (steps 3 and 6 of SKILL.md).

Every row is a question to answer with a line of code or a test, not with an opinion. A "yes, and here is the line"
goes in the report; a "no" is a finding.

| Area | Ask | Typical failure | Check |
|---|---|---|---|
| **Queries per request** | Does the number of database or API calls stay the same as the data grows? | a query inside a loop; a lazy relation loaded per row (N+1) | A test that counts queries or calls for 1 row and for 20 rows and sees the same number |
| **Unbounded reads** | Is every list, search, scan and export paged or limited, and every file or stream read in chunks? | `findMany()` or `SELECT *` with no limit on a table that grows; a whole upload read into memory | A test with more rows than the page size that gets one page; the limit named in one place in code or config |
| **Indexes** | Does every new filter, sort or join on a large table have an index, or a stated reason? | a new `WHERE` or `ORDER BY` column on a table with millions of rows | The schema or a migration has an index covering the filter, join and sort columns, or the design note says why none is needed. (`EXPLAIN` on small seed data proves nothing: the planner picks a full scan on small tables) |
| **Work in loops** | Is anything costly (I/O, parsing, regex build, sort, a search through an array) repeated per item where once would do? | `list.find` inside `map` over two input-sized lists (n²); a regex compiled per row | A test at the size the project reaches, counting operations or calls, not time |
| **Blocking the hot path** | Does a request, render or event handler wait on work it could stream, batch or hand to a job? | sync file reads, large JSON parse, image work or email sending inside the request | The slow work moves to a job or stream; a test that the request returns before the job runs |
| **Outbound calls** | Does every network and database call have a timeout, and is concurrency bounded? | `Promise.all` over an unbounded list; no timeout, so requests pile up behind a slow service | A test with a slow fake that sees the timeout; a concurrency limit named in code |
| **Caches** | Does every cache have a size bound, an expiry and one owner that invalidates it on write? | a module-level map that grows forever; stale data after an update | A test that writes and then reads fresh data; the bound in code (see `state.md`) |
| **Payload size** | Do responses send only the fields the caller needs, and do large lists page or stream? | whole rows with blobs or nested relations; megabytes of JSON for one screen | A test that the response holds only the named fields; the size on seed data in the report |
| **Client bundle and renders** | Does the change pull a large library into the client, re-render or re-fetch in a loop, or render a long list at once? | importing a whole utility or date library for one function; an effect whose dependency changes every render; thousands of rows in the DOM | The repo's bundle-size check; a render or fetch count in a component test; a virtualized or paged list |
| **Migrations and backfills** | Does a migration or data job lock a large table, or touch every row in one transaction? | an `ALTER` that rewrites a big table; one `UPDATE` over all rows | Batched and online, tested on a copy of real-sized data (see `change-safety.md`) |

## When it applies

- **Tiny** change: only the rows the change touches.
- **Standard / Large**: walk the whole table once in step 3 for the paths the design note lists, and again over the
  diff in step 6.
- A change that reads no stored data, loops over no input, calls nothing and changes no bundle says so in one line
  in the report ("no performance-relevant path").

## Rules

- A finding names the size at which it hurts: rows, users, items or bytes, taken from the architecture profile, the
  project's config, seed data or the ticket. "Could be slow" with no size is not a finding. When no size is known,
  the finding is marked `size unknown`, is at most a should-fix, and the report names the size that would settle it.
- A fix starts with a test that measures what scales (queries, calls, items processed, bytes, renders) and is seen
  red before the fix. Wall-clock limits in tests are flaky: use them only through the repo's own benchmark harness.
- A finding in code you did not touch is reported, not fixed, unless the task asks (same rule as existing debt).
- Never trade correctness or security for speed silently: a cache, a denormalised field or a skipped check is a
  design decision, written in the design note.

## Sources

- Markus Winand, Use The Index, Luke (SQL indexing and query cost): https://use-the-index-luke.com/
- PostgreSQL documentation, Using EXPLAIN: https://www.postgresql.org/docs/current/using-explain.html
- Rails Guides, Active Record Query Interface, eager loading and the N+1 problem:
  https://guides.rubyonrails.org/active_record_querying.html#eager-loading-associations
- Node.js, Don't Block the Event Loop: https://nodejs.org/en/learn/asynchronous-work/dont-block-the-event-loop
- React, You Might Not Need an Effect: https://react.dev/learn/you-might-not-need-an-effect
