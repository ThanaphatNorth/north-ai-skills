<!-- Loop markdown dialect → ADF via scripts/jira-comment.sh: **bold**, `code`, 1. / - lists, bare URLs, and `::video <uuid>` for an inline player.
     Write the file with a QUOTED heredoc (<<'EOF') or the Write tool — never <<EOF, which runs `backticks` as commands.
     Language: match the ticket (config.md § Comments). Three numbered sections, exactly. -->
**1. Can it be reproduced?**
<Yes / No / Partly> — <environment: local isolated stack on <base> @ <short sha> | dev site>, role <role>.
Steps: <numbered steps a QA person can follow on screen>
Result before fix: <what happened> — e2e `<path to defect spec>` failed: `<pasted failing assertion line>`
**Video (before):**
::video <media-uuid of KEY-before.mp4>

**2. Root cause**
<one or two plain sentences: what the code did and why it gave the wrong result>
Where: `<path>:<line>` (<function/component>)
<If useful: the condition / data case that triggers it, and why it was not caught before>

**3. Solution**
<what changed, in plain words, and why it fixes the cause rather than the symptom>
Files: `<path>` (+ regression test `<path>`)
Tests: `<command>` → `<pasted summary line>` (one line per suite run)
**Video (after)** (<what each held state shows>):
::video <media-uuid of KEY-after.mp4>
Branch / PR: <branch @ sha — local, awaiting push approval | PR link>
QA note: <what QA should re-test, incl. neighbouring cases>

<!-- Variants
- by-design / superseded: §1 "not reproducible as reported" + why (video of current behaviour), §2 the spec line / decision / commit, §3 "no code change — needs PO decision: close, or re-scope to <what>".
- structural: §1 + §2 as usual, §3 "proposed — waiting for a decision" with options A/B (cost, risk) and the questions for the PO.
- partial fix: §3 lists what this PR fixes and, separately, what still waits for a decision; the ticket stays in its lane. -->
