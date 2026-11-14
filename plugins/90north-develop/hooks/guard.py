#!/usr/bin/env python3
"""PreToolUse guard for the 90north-develop subagents.

Claude Code runs this before every Bash, Write and Edit call (hooks/hooks.json). When the call comes from one of
this plugin's own subagents it blocks, with exit 2 and the reason on stderr, what that agent's hard rules forbid:
a push, a merge, an install, booting the app, a database client, the tracker, and for the read-only agents anything
that builds, tests or changes files. Every other caller, the main conversation included, passes untouched.

It reads command text, so it is a second lock behind the agents' instructions, not a sandbox: a command hidden in a
variable or a file it runs is not seen.
"""
from __future__ import annotations

import json
import os
import re
import sys
from typing import Dict, Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # `python3 -I` leaves the script's folder off the path

from guard_rules import READERS, WRITERS, common_rule, reader_rule, write_verdict, writer_rule  # noqa: E402
from guard_shell import RUNNERS, SHELLS, drop_heredoc_text, simple_commands, unwrap  # noqa: E402

__all__ = ["READERS", "WRITERS", "agent_name", "bash_verdict", "main", "ours", "verdict"]

PLUGIN = "90north-develop"
_PIPE_TO_SHELL = re.compile(r"\b(curl|wget)\b[^|;&\n]*\|\s*(sudo\s+)?(ba|z|da|k)?sh\b")
_TRACKER_HOST = re.compile(r"\b(curl|wget)\b.*atlassian\.net")


def agent_name(agent_type: str) -> str:
    """The agent's own name: `90north-develop:dev-builder` and `dev-builder` both give `dev-builder`."""
    return agent_type.rsplit(":", 1)[-1]


def ours(agent_type: object) -> Optional[str]:
    """The name of this plugin's subagent making the call, or None for every other caller."""
    if not isinstance(agent_type, str) or not agent_type:
        return None
    if ":" in agent_type and agent_type.rsplit(":", 1)[0] != PLUGIN:
        return None
    name = agent_name(agent_type)
    return name if name in WRITERS or name in READERS else None


def bash_verdict(agent: str, command: str) -> Optional[str]:
    """Why this agent may not run this shell line, or None when it may."""
    command = drop_heredoc_text(command)
    if _PIPE_TO_SHELL.search(command):
        return "no-install: never pipe a download into a shell"
    if _TRACKER_HOST.search(command):
        return "no-tracker: only the orchestrator talks to the tracker"
    commands = [args for args in (unwrap(argv) for argv in simple_commands(command)) if args]
    for args in commands:  # the rules every subagent shares are named first, whatever else the line holds
        shared = common_rule(args)
        if shared:
            return shared
    for args in commands:
        name = os.path.basename(args[0])
        if name in SHELLS and "-c" in "".join(a for a in args[1:3] if a.startswith("-")):
            script = next((a for a in args[1:] if not a.startswith("-")), "")
            inner = bash_verdict(agent, script)
            if inner:
                return inner
        if name == "eval":
            inner = bash_verdict(agent, " ".join(args[1:]))
            if inner:
                return inner
        if name in RUNNERS:
            args = [a for a in args[1:] if not a.startswith("-")] or args
            if agent in READERS:
                return "read-only: this agent reads and reports; a package runner executes code"
        own = writer_rule(args) if agent in WRITERS else reader_rule(args)
        if own:
            return own
    return None


def verdict(agent: str, tool: str, tool_input: Dict[str, object]) -> Optional[str]:
    """Why this tool call is blocked for this plugin subagent, or None when it may run."""
    if tool == "Bash":
        command = tool_input.get("command")
        if not isinstance(command, str):
            raise ValueError("no command text")
        return bash_verdict(agent, command)
    if tool in ("Write", "Edit", "NotebookEdit"):
        path = tool_input.get("file_path") or tool_input.get("notebook_path")
        if not isinstance(path, str):
            raise ValueError("no file path")
        return write_verdict(agent, path)
    return None


def main(stdin_text: str) -> int:
    """Exit code for one hook call: 0 lets it run, 2 blocks it with the reason on stderr."""
    try:
        data = json.loads(stdin_text)
        agent = ours(data.get("agent_type")) if isinstance(data, dict) else None
    except ValueError:
        return 0  # not a call this guard can attribute to one of its agents
    if agent is None:
        return 0
    try:
        tool_input = data.get("tool_input")
        reason = verdict(agent, str(data.get("tool_name")), tool_input if isinstance(tool_input, dict) else {})
    except Exception as err:  # a call by one of our agents that cannot be read is blocked, not waved through
        reason = "guard could not read this call (%s)" % err
    if reason is None:
        return 0
    sys.stderr.write("90north-develop guard: %s may not do this. %s. Do not work around it: report it as a gap or "
                     "NEEDS-DECISION.\n" % (agent, reason))
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.stdin.read()))
