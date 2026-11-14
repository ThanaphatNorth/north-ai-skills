# Consistency review — the brief

`tools/check_repo.py` catches what a machine can see: a path or a `§` reference that no longer resolves, a ledger
state that is not parked, an agent that is not registered. It cannot see two files that now say different things.
That takes a reader. Run this brief after any change to a skill, an agent or a shared reference, before the commit,
and fix or answer every finding.

How to run it: give the text below to a subagent with a fresh context (it must not have seen why the change was
made), with the change list filled in. Check each finding against the files yourself before acting on it.

---

Read-only review. Do not edit, create or delete any file, and do not run tests or `claude` commands. You may run
`git diff`, `git show`, `grep`, `rg`, `sed -n` and `wc`.

Repo: `<absolute path>`. What changed: `<one line per changed file: what it now says that it did not say before>`.

Find places where the documents now contradict each other or point at something that no longer exists. Read the
full current text, not only the diff, of: every `skills/*/SKILL.md`, `skills/workflow/references/*.md`,
`skills/workflow/templates/*.md`, `skills/develop-init/templates/config.md`, `skills/n-dev/templates/design-note.md`,
`skills/n-dev/references/*.md`, both loops' `templates/jira-comment.md`, `plugins/90north-develop/agents/*.md`,
`plugins/90north-develop/README.md` and `README.md`.

Look for:
1. A rule stated two ways: one file says a thing always happens, another says it happens only sometimes, or in
   another order.
2. A sequence that cannot be followed: a step that needs what a later step produces, or a path through the steps
   that skips a gate every other path passes.
3. A state with no way out: an item parked in a ledger state that no rule ever resumes.
4. A word that means opposite things in two files.
5. A template with no place for something a rule says must be written into it.
6. Attended mode asking in more than one round, or stopping mid-run for a question.
7. `--auto` made looser than before the change: it must still park a card for any change to state shape, schema or
   a public interface, a trade-off, Large work and a forbidden area. Compare with `git show HEAD:<path>`.
8. A safety rule weakened: a push, force-push, merge, delete or data repair must still need the user's yes, and a
   yes given in the decision round must cover only that run's named branches.
9. A subagent's hard rule that `plugins/90north-develop/hooks/guard.py` does not enforce, or a guard rule no agent
   file states.

Trace before claiming: for each finding quote both lines with `path:line`. Leave out style, wording preferences, and
anything that was already so at HEAD and has nothing to do with this change. If a check is clean, say so in one line.

Return a numbered list, most serious first: `path:line` and the quoted text, `path:line` and the quoted text, and one
sentence on why they conflict. Then one line per check 1–9: "clean" or "see finding N". Under 600 words.
