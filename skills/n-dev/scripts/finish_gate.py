#!/usr/bin/env python3
"""Hook for n-dev's review gate and finish gate (SKILL.md, steps 5 to 7).

Claude Code runs this in a session that used the skill, at two moments, and it reads what the session really did
from its transcript and from git (gate_session.py):

  before a `git commit`   more than one source file changed (Standard work) and no reviewer subagent has answered:
                          the commit is held once, with the reason on stderr
  when a turn would end   code changed, and the structure check, the review or the commit is missing: the turn is
                          held once, with the missing steps on stderr

  code changed     a code file was written with a file tool, committed since the session started, or is
                   uncommitted and was written since it started; documents and git-ignored files do not count
  structure check  a command naming structure_check.py finished after the last of those files was written
  review           a reviewer subagent (its type, description or prompt says review) started after the first
                   write, and it has answered
  commit           none of those files is still uncommitted

Each reminder comes once, a turn that ends while the reviewer is still reading is left alone, a subagent's own
commit is never held, and a failure of this hook always lets the session go on.
"""
from __future__ import annotations

import json
import os
import re
import sys
from typing import Dict, List, Optional, Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import gate_session as gs  # noqa: E402

REVIEW_MARK = "n-dev review gate:"
_COMMIT = re.compile(r"(^|[;&|(\s])git\s+(-C\s+\S+\s+|-c\s+\S+\s+)*commit\b")


def checked(session: gs.Session, root: str, files: Sequence[str]) -> bool:
    """True when a structure check finished after the last write to the session's files. A transcript without
    timestamps is judged by order: the check came after the last file-tool edit."""
    newest = gs.newest_write(root, files)
    last_edit = max((position for position, _ in gs.file_tool_edits(session, root)), default=-1)
    for position, call in enumerate(session.calls):
        if call.name != "Bash" or "structure_check.py" not in str(call.input.get("command", "")):
            continue
        finished = session.answers.get(call.id, ("", None))[1]
        if finished is None or newest is None:
            if position > last_edit:
                return True
        elif finished >= newest:
            return True
    return False


def review_state(session: gs.Session, root: str, files: Sequence[str]) -> str:
    """not-needed | none | pending | answered: where the review of this session's change stands."""
    if len([path for path in files if not gs.is_test(path)]) <= 1:
        return "not-needed"  # one source file is Tiny work
    return gs.subagent_state(session, gs.first_write(session, root))


def missing_steps(session: gs.Session, root: str) -> List[str]:
    """The gate steps this session still owes, each as one instruction; empty when the turn may end."""
    files = gs.changed_code(session, root)
    review = review_state(session, root, files) if files else "not-needed"
    if not files or review == "pending":
        return []  # nothing changed, or the turn ends to wait for the reviewer
    missing: List[str] = []
    if not checked(session, root, files):
        missing.append("Run the structure check on the final diff (step 5) and quote its RESULT line in the report.")
    if review == "none":
        sources = len([path for path in files if not gs.is_test(path)])
        missing.append("Start the reviewer subagent on the diff (step 6): %d source files changed, so this is Standard "
                       "work. Step 6 says how many reviewers a diff of its size gets; every lens is read." % sources)
    left = gs.uncommitted(root, files)
    if left:
        missing.append("Commit your change on a feature branch, staging only your own files (not yet committed: %s)."
                       % ", ".join(left[:6]))
    return missing


def commit_hold(event: Dict[str, object], session: gs.Session, root: str) -> Optional[str]:
    """Why this `git commit` must wait for the review, or None when it may run."""
    if any(REVIEW_MARK in answer for answer, _ in session.answers.values()):
        return None  # held once already
    state = review_state(session, root, gs.changed_code(session, root))
    if state == "none":
        return ("more than one source file changed, so this is Standard work, and no reviewer subagent has read the "
                "diff. Start one with the Agent or Task tool (step 6), wait for its answer, fix what it finds, then "
                "commit.")
    if state == "pending":
        return "the reviewer subagent has not answered yet. End the turn and wait for it; commit when it has."
    return None


def _is_commit(event: Dict[str, object]) -> bool:
    """True for the main conversation's own `git commit` call."""
    tool_input = event.get("tool_input")
    command = str(tool_input.get("command", "")) if isinstance(tool_input, dict) else ""
    return event.get("tool_name") == "Bash" and not event.get("agent_type") and bool(_COMMIT.search(command))


def _held(lines: List[str]) -> int:
    sys.stderr.write("\n".join(lines) + "\n")
    return 2


def main(stdin_text: str) -> int:
    """Exit code for one hook event: 0 lets it go on, 2 holds it once with the reason on stderr."""
    try:
        event = json.loads(stdin_text)
        before_tool = isinstance(event, dict) and event.get("hook_event_name") == "PreToolUse"
        if not isinstance(event, dict) or event.get("stop_hook_active") or (before_tool and not _is_commit(event)):
            return 0
        root = gs.repo_root(str(event.get("cwd") or ""))
        if root is None:
            return 0
        session = gs.read_session(str(event.get("transcript_path") or ""))
        hold = commit_hold(event, session, root) if before_tool else None
        missing = [] if before_tool else missing_steps(session, root)
    except Exception:  # a reminder must never be the reason a session cannot go on
        return 0
    if hold:
        return _held([REVIEW_MARK + " " + hold, "If no subagent tool exists here, commit again and say so in the "
                      "report. This reminder comes once."])
    if not missing:
        return 0
    lines = ["n-dev finish gate: code changed in this session, and before the turn ends this is still owed:"]
    lines += ["  %d. %s" % (number, step) for number, step in enumerate(missing, 1)]
    lines.append("When they are done, write the report again in full: the last message is the one that is read. "
                 "If a step cannot run here, say why in the report instead. This reminder comes once.")
    return _held(lines)


if __name__ == "__main__":
    sys.exit(main(sys.stdin.read()))
