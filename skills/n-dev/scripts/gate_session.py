#!/usr/bin/env python3
"""What a session did, read from its transcript and from git: the facts n-dev's gates judge (finish_gate.py).

Claude Code writes one JSON object per line. A tool call is a `tool_use` block and its answer a `tool_result`
block with the same id. A subagent that runs in the background answers later, in a `<task-notification>` that
names the call's id: a user message when the session was waiting, a queued attachment when it was busy. Lines
carry an ISO `timestamp`; a transcript without them still works, by line order.

Which files the session changed comes from git and the file system, not from the tool that wrote them: an agent
writes files with a shell here-document as often as with an edit tool.
"""
from __future__ import annotations

import datetime
import json
import os
import re
import subprocess
from typing import Dict, List, NamedTuple, Optional, Sequence, Set, Tuple

FILE_TOOLS = {"Edit", "Write", "NotebookEdit", "MultiEdit"}
SUBAGENT_TOOLS = {"Agent", "Task"}
_DOCUMENT = re.compile(r"\.(md|mdx|txt|rst)$", re.I)
_TEST = re.compile(r"(^|/)(tests?|__tests__|specs?|e2e)/|(^|/)test_[^/]*$|[._-](test|spec)\.[^/.]+$|_test\.[^/.]+$")
# a shell line that writes a file: a here-document, a redirect to a real file, tee, sed -i, git apply, patch.
# A redirect stands after a space: the `>` that closes an address in a commit message is not one.
_SHELL_WRITE = re.compile(r"<<|(?<=\s)>{1,2}\s*(?!/dev/null|&)[\w./\"'${~-]|\btee\b|\bsed\s+-i|\bgit\s+apply\b|\bpatch\b")
_PATH_WORD = re.compile(r"[\w./~+-]+")
_FINISHED = re.compile(r"<tool-use-id>([^<]+)</tool-use-id>.*?<status>completed</status>", re.S)
_BACKGROUND = ("Async agent launched", "working in the background")
_REVIEW_WORD = re.compile(r"review|lens", re.I)
_MAKER = re.compile(r"builder|fixer|repro", re.I)  # agent types that write code or specs


class Call(NamedTuple):
    """One tool call of the main conversation."""
    name: str
    input: Dict[str, object]
    id: str
    time: Optional[float]


class Session(NamedTuple):
    calls: List[Call]
    answers: Dict[str, Tuple[str, Optional[float]]]  # call id -> (answer text, when it arrived)
    finished: Set[str]                               # background calls a task notification reported as completed
    started: Optional[float]                         # the first timestamp in the transcript


def _epoch(stamp: object) -> Optional[float]:
    """Seconds since 1970 for an ISO timestamp such as 2026-11-13T23:03:19.785Z, or None."""
    if not isinstance(stamp, str):
        return None
    try:
        return datetime.datetime.fromisoformat(stamp.replace("Z", "+00:00")).timestamp()
    except ValueError:
        return None


def _text(content: object) -> str:
    """A tool result's content as plain text: it is a string, or a list of text blocks."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(str(block.get("text", "")) for block in content if isinstance(block, dict))
    return ""


def _read_line(line: Dict[str, object], session: Session, seen: Set[str]) -> None:
    """Add the tool calls, answers and task notifications of one transcript line to the session."""
    when = _epoch(line.get("timestamp"))
    message = line.get("message")
    content = message.get("content") if isinstance(message, dict) else None
    if line.get("type") == "user":
        session.finished.update(_FINISHED.findall(_text(content)))
    queued = line.get("attachment")  # a notification that arrived mid-turn is queued and written as an attachment
    if isinstance(queued, dict) and queued.get("type") == "queued_command":
        session.finished.update(_FINISHED.findall(str(queued.get("prompt", ""))))
    for block in content if isinstance(content, list) else []:
        if not isinstance(block, dict):
            continue
        kind, tool_input = block.get("type"), block.get("input")
        if kind == "tool_use" and isinstance(block.get("name"), str) and isinstance(tool_input, dict):
            call_id = str(block.get("id") or "call-%d" % len(session.calls))
            if call_id not in seen:  # the same call can be written more than once
                seen.add(call_id)
                session.calls.append(Call(str(block["name"]), tool_input, call_id, when))
        elif kind == "tool_result" and isinstance(block.get("tool_use_id"), str):
            session.answers.setdefault(block["tool_use_id"], (_text(block.get("content")), when))


def read_session(transcript_path: str) -> Session:
    """Every tool call of the main conversation in a transcript, in order, with its answer."""
    session, seen = Session([], {}, set(), None), set()  # type: Session, Set[str]
    with open(transcript_path, encoding="utf-8", errors="replace") as fh:
        for raw in fh:
            try:
                line = json.loads(raw)
            except ValueError:
                continue
            if not isinstance(line, dict) or line.get("isSidechain"):
                continue  # a subagent's own calls are not the session's
            if session.started is None:
                session = session._replace(started=_epoch(line.get("timestamp")))
            _read_line(line, session, seen)
    return session


def _git(repo: str, args: Sequence[str]) -> Optional[str]:
    """git's output in this repository, or None when the command fails or git is missing."""
    try:
        proc = subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, errors="replace")
    except OSError:
        return None
    return proc.stdout if proc.returncode == 0 else None


def repo_root(cwd: str) -> Optional[str]:
    """The top folder of the git work tree that holds cwd, or None outside one."""
    top = _git(cwd, ["rev-parse", "--show-toplevel"]) if os.path.isdir(cwd) else None
    return os.path.realpath(top.strip()) if top and top.strip() else None


def is_test(path: str) -> bool:
    return bool(_TEST.search(path))


def _is_code(root: str, rel: str) -> bool:
    """A file the gates care about: inside the repo, not git's own, not a document, not ignored."""
    if rel.startswith(("../", ".git/")) or _DOCUMENT.search(rel):
        return False
    return _git(root, ["check-ignore", "-q", "--", rel]) is None


def file_tool_edits(session: Session, root: str) -> List[Tuple[int, str]]:
    """(position in the session, path inside the repo) for every code file written with a file tool."""
    edits: List[Tuple[int, str]] = []
    for position, call in enumerate(session.calls):
        target = call.input.get("file_path") or call.input.get("notebook_path")
        if call.name not in FILE_TOOLS or not isinstance(target, str) or not target:
            continue
        full = os.path.realpath(target if os.path.isabs(target) else os.path.join(root, target))
        rel = os.path.relpath(full, root).replace(os.sep, "/")
        if _is_code(root, rel):
            edits.append((position, rel))
    return edits


def _status(root: str) -> List[Tuple[str, bool]]:
    """(path, untracked) for every path git shows as changed or untracked (the new name of a renamed file)."""
    status = _git(root, ["status", "--porcelain", "--untracked-files=all"]) or ""
    return [(line[3:].split(" -> ")[-1].strip().strip('"'), line.startswith("??"))
            for line in status.splitlines() if len(line) > 3]


def _named(session: Session) -> Set[str]:
    """Every path-like word in the session's tool calls, and the file name each one ends in."""
    words: Set[str] = set()
    for call in session.calls:
        for value in call.input.values():
            for word in _PATH_WORD.findall(value) if isinstance(value, str) else []:
                words.update((word, word.rsplit("/", 1)[-1]))
    return words


def _is_named(rel: str, named: Set[str]) -> bool:
    """True when a tool call named this file: by its path, or by its file name when that has an extension."""
    name = rel.rsplit("/", 1)[-1]
    return rel in named or ("." in name.lstrip(".") and name in named)


def _committed_since(root: str, started: float) -> List[str]:
    """Paths in the commits on HEAD that were made after the session started."""
    log = _git(root, ["log", "-n", "200", "--format=%x00%ct", "--name-only"]) or ""
    paths: List[str] = []
    for entry in log.split("\0")[1:]:
        lines = entry.splitlines()
        if lines and lines[0].isdigit() and int(lines[0]) >= int(started):
            paths += [line for line in lines[1:] if line]
    return paths


def _mtime(root: str, rel: str) -> Optional[float]:
    try:
        return os.path.getmtime(os.path.join(root, rel))
    except OSError:
        return None


def changed_code(session: Session, root: str) -> List[str]:
    """Code files this session changed: written with a file tool, committed since it started, or still
    uncommitted and written since it started. A file that was already dirty is not the session's, and neither is
    a new file no tool call named: tools leave caches and settings behind as they run."""
    paths = {rel for _, rel in file_tool_edits(session, root)}
    if session.started is not None:
        start, named = session.started, _named(session)
        fresh = [rel for rel, untracked in _status(root)
                 if (not untracked or _is_named(rel, named)) and (_mtime(root, rel) or 0.0) >= start]
        paths.update(rel for rel in fresh + _committed_since(root, start) if _is_code(root, rel))
    return sorted(paths)


def uncommitted(root: str, paths: Sequence[str]) -> List[str]:
    """Those of the given paths that git still shows as changed or untracked."""
    changed = {rel for rel, _ in _status(root)}
    return [path for path in paths if path in changed]


def newest_write(root: str, paths: Sequence[str]) -> Optional[float]:
    """When the most recently written of these files was written, or None when none of them exists."""
    times = [when for when in (_mtime(root, rel) for rel in paths) if when is not None]
    return max(times) if times else None


def first_write(session: Session, root: str) -> int:
    """Position of the first call that wrote a code file (a file tool, or a shell line that writes); -1 if unknown."""
    tool = [position for position, _ in file_tool_edits(session, root)]
    shell = [position for position, call in enumerate(session.calls)
             if call.name == "Bash" and _SHELL_WRITE.search(str(call.input.get("command", "")))]
    return min(tool + shell) if tool or shell else -1


def _is_reviewer(call: Call) -> bool:
    """True for a subagent call whose type, description or prompt says it reviews. A search helper is a subagent
    too and is not the review; neither is a builder, fixer or reproducer, even when its brief quotes review findings."""
    kind = str(call.input.get("subagent_type", ""))
    if call.name not in SUBAGENT_TOOLS or _MAKER.search(kind):
        return False
    words = " ".join(str(call.input.get(key, "")) for key in ("subagent_type", "description", "prompt"))
    return bool(_REVIEW_WORD.search(words))


def subagent_state(session: Session, after: int) -> str:
    """none | pending | answered: whether a reviewer subagent started after position `after` has given its answer.
    An answer that only says the agent runs in the background is not one; its task notification is."""
    state = "none"
    for position, call in enumerate(session.calls):
        if position <= after or not _is_reviewer(call):
            continue
        answer = session.answers.get(call.id)
        background = answer is not None and any(mark in answer[0][:400] for mark in _BACKGROUND)
        if call.id in session.finished or (answer is not None and not background):
            return "answered"
        state = "pending"
    return state
