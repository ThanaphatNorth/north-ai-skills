<!-- Loop markdown dialect → ADF via the workflow skill's scripts/jira-comment.sh: **bold**, `code`, 1. / - lists, bare URLs, and `::video <uuid>` for an inline player.
     Write the file with a QUOTED heredoc (<<'EOF') or the Write tool — never <<EOF, which runs `backticks` as commands.
     Language: config.md § Comments. Three numbered sections, exactly. -->
**1. What was built**
<one or two plain sentences: what a user can now do, in the ticket's words>
Acceptance criteria:
- AC-1 <criterion> — <done | partly: what is missing | not in this PR: why>
- AC-2 …
Not included (proposals, not built): <extra options or side findings, or "none">

**2. How it works**
<plain words: the new pieces and how they fit into what was there>
New: `<path>` — <one-line responsibility> (one line per new module)
Changed existing files: `<path>` — <wiring: registers / imports … | reason from the design note>
Data / API: <schema change, new endpoint or contract change — or "none">
Decisions: <each decision taken, and who approved it (design gate date) — or "none">

**3. Verification**
Acceptance: `<spec path>` — red before (`<pasted failing line>`), green now: `<pasted summary line>` (run twice)
Tests: `<command>` → `<pasted summary line>` (one line per suite run)
Structure check: `<result line>`
Review + QA: <rounds, and what they changed>
**Demo** (<what each held state shows, AC by AC>):
::video <media-uuid of KEY-demo.mp4>
Branch / PR: <branch @ sha — local, awaiting push approval | PR link>
QA note: <what to test by hand, incl. neighbouring screens and roles>

<!-- Variants
- design gate (Large / always-ask): only when config § Dev flow says to post designs — §1 the AC list, §2 the proposed design with options A/B (cost, risk) and the question, §3 "not built yet — waiting for a decision".
- partial: §1 marks each AC done / not in this PR; the item stays in its lane until the rest is decided. -->
