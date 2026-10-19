# defect-loop — core lessons (every project)

> Read when: before every sweep (S0 in the workflow skill's `references/stages.md`), after the shared core lessons, and when a defect lesson might belong to every repo.

Defect-only rules from real sweeps: triage and reproduction. Rules that hold for both loops (finding work, safety, verifying, evidence, Jira, environment) live in the workflow skill's `references/core-lessons.md`.

## Triage
- Before calling something a bug, check the cited requirement in the spec's decision log for "Revised by / Reversed by". Requirement docs and QA packs lag the spec; when they do, it is by-design and the comment names the stale document.
- Before calling something structural, grep the backend: a missing button for an action the API already supports is a small web fix.
- Reproduce with the largest input the current build accepts and say so; report side bugs as separate proposals, not scope creep.
- Numeric overflow/truncation can differ by DB mode (strict errors vs silent clamp) → note the mode and fix at the API boundary so every mode returns a validation error.

## Reproducing (e2e)
- The red run must fail for the **reported** reason (the final expect), not a locator timeout, a login error or missing data. A red spec only proves the assertions it reached — list the ones never executed.
- Double-submit bugs need clicks with **no gap** (before the framework commits `disabled`); latency alone doesn't trigger them.
- Committed specs: no absolute or scratchpad paths (use `testInfo.outputPath`), no hard-coded personal test accounts (use the repo's user helpers + env overrides), no cleanup calls (use the repo's teardown and naming convention), check every request's status.
- Pass `--output` outside the repo when the repo commits anything under the default output folder.
- Text mixed with controls: assert on the container (`toContainText`), not `getByText(/^…/)`.
- Layout bugs: compare old vs new on the same data at several widths (e.g. 1024/1280/1440) and as every role that sees the screen; one viewport and one role miss regressions.
- Session/token changes: test two tabs (shared storage, stale-tab 401) and cacheable responses that carry auth headers.

## Sources

- Distilled from the author's own sweeps of a production Jira defect board (2026): each line is a rule that cost a retry, a wrong write or a user correction.
- Playwright locators and auto-waiting assertions (`toContainText`): https://playwright.dev/docs/test-assertions
- Playwright test output and `testInfo.outputPath`: https://playwright.dev/docs/api/class-testinfo
