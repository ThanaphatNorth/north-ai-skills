#!/usr/bin/env python3
"""Turn Jira's JSON into the text the jira-*.sh scripts print, and build their request bodies.

  python3 -I jira_fmt.py <command> [args…]        JSON on stdin, text on stdout; the commands are in COMMANDS

This file is only the command line: it reads, calls one pure function and prints. jira_read.py holds the functions
that format what Jira answered, jira_write.py the ones that build what is sent. Exit 1 with one `ERROR …` line for a
body that cannot be formatted (BodyError), exit 2 for a value that cannot go into a request body (ArgError).
"""
from __future__ import annotations

import importlib.util
import os
import re
import sys
from typing import Any, Callable, Dict, List, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # -I leaves this folder off the path
from jira_read import (BodyError, attachment_rows, card_text, comment_check, display_name,  # noqa: E402
                       download_rows, issue_text, labels_text, object_id, search_page, status_text, transitions_text)
from jira_write import ArgError, comment_body, edit_body, transition_body  # noqa: E402


def _stdin() -> str:
    return sys.stdin.buffer.read().decode("utf-8", "replace")


def _markdown_file_to_adf(path: str) -> Any:
    """The ADF document for a markdown file (template comments removed), converted by md2adf.py beside this file."""
    source = os.path.join(os.path.dirname(os.path.abspath(__file__)), "md2adf.py")
    spec = importlib.util.spec_from_file_location("md2adf", source)
    if spec is None or spec.loader is None:
        raise OSError("cannot load %s" % source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    with open(path, encoding="utf-8") as fh:
        text = re.sub(r"<!--.*?-->\n?", "", fh.read(), flags=re.S)
    return module.convert(text, "0")


def _comment_check(args: List[str]) -> str:
    with open(args[0], encoding="utf-8") as fh:
        line, warnings = comment_check(_stdin(), fh.read(), bool(args[1]))
    sys.stdout.write(line)
    sys.stdout.flush()
    sys.stderr.write("".join(warning + "\n" for warning in warnings))
    return ""


# command → (arguments it needs, handler that returns the text for stdout)
COMMANDS: Dict[str, Tuple[int, Callable[[List[str]], str]]] = {
    "issue": (0, lambda args: issue_text(_stdin())),
    "card": (1, lambda args: card_text(_stdin(), args[0])),
    "search-page": (0, lambda args: search_page(_stdin())),
    "transitions": (0, lambda args: transitions_text(_stdin())),
    "transition-body": (2, lambda args: transition_body(args[0], args[1])),
    "status": (0, lambda args: status_text(_stdin())),
    "labels": (0, lambda args: labels_text(_stdin())),
    "edit-body": (0, lambda args: edit_body(args, _markdown_file_to_adf)),
    "id": (0, lambda args: object_id(_stdin())),
    "comment-body": (0, lambda args: comment_body(_stdin())),
    "comment-check": (2, _comment_check),
    "attachments": (0, lambda args: attachment_rows(_stdin())),
    "downloads": (0, lambda args: download_rows(_stdin())),
    "display-name": (0, lambda args: display_name(_stdin())),
}
OWNER = {"edit-body": "jira-edit.sh", "transition-body": "jira-transition.sh"}  # whose argument an ArgError is about


def main(argv: List[str]) -> int:
    """Run one command and return the exit code: 0; 1 for a body that cannot be formatted (one ERROR line);
    2 for a refused argument or a call that names no command."""
    name, args = (argv[1] if len(argv) > 1 else ""), argv[2:]
    if name not in COMMANDS or len(args) < COMMANDS[name][0]:
        print("usage: jira_fmt.py <%s> [args…]" % " | ".join(COMMANDS), file=sys.stderr)
        return 2
    try:
        sys.stdout.write(COMMANDS[name][1](args))
    except BodyError as e:
        print(e.line, file=sys.stdout if e.stdout else sys.stderr)
        return 1
    except ArgError as e:
        print("%s: %s" % (OWNER.get(name, "jira_fmt.py"), e), file=sys.stderr)
        return 2
    except (KeyError, IndexError, TypeError, AttributeError) as e:  # an object without a part the text needs
        print("ERROR unexpected response shape: %r" % (e,), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
