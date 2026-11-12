# <Area name>

verified-at: <merge-base sha of the PR that last checked this doc> · <YYYY-MM-DD>
coverage: partial — rules recorded as changes touch them
Code: `<path or glob>`, `<path or glob>` · Profile: <link to the architecture profile row, if any>

## What it does
<Two or three sentences: what a user or another system can do here, and who uses it.>

## Rules
<!-- One row per business rule. Ids are stable: never renumber; a rule that no longer holds is marked
     "retired: <date> <KEY>" and kept. Values that live in code or config are named by file, not copied. -->
- **R-1** <the rule, in plain words> — source: <ticket key | decision id | spec link>
- **R-2** …

## Behaviour
<Only what a reader cannot see quickly in the code: the flow, the states and their transitions, edge cases,
what happens on failure. Delete this section when there is nothing to add.>

## Rules → tests
| Rule | Test (name, file) |
|---|---|
| R-1 | `<test name>` in `<test file>` |
| R-2 | no test yet |

## Decisions
<!-- Why the area is built this way, including confirmed "by-design" answers. Cite the decision record when
     one exists instead of restating it. -->
- <YYYY-MM-DD> <decision> — because <reason> (<ticket or decision id>)

## Known limits
- <what it does not do, on purpose or not yet, and where that is tracked>
