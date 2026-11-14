"""The JSON bodies the jira-*.sh scripts send to Jira, built from their arguments (reached through jira_fmt.py).

Each function is pure: argument values in, the body text out. A value that cannot go into a body raises ArgError.
"""
from __future__ import annotations

import json
import re
from typing import Any, Callable, Dict, List, Sequence, Tuple

from jira_read import parse_json

FIELD_ID = r"[A-Za-z][A-Za-z0-9_]*"  # the same rule as need_field_ids in _env.sh (a test keeps the two equal)
EDIT_OPTIONS = ("--add-label", "--remove-label", "--field", "--field-md")


class ArgError(Exception):
    """A command-line value that cannot go into a request body."""


def transition_body(transition_id: str, fields: str) -> str:
    """Return the JSON body of a transition request; fields is "" or a JSON object of field values."""
    body: Dict[str, Any] = {"transition": {"id": transition_id}}
    if fields:
        try:
            value = json.loads(fields)
        except ValueError:
            value = None
        if not isinstance(value, dict):
            raise ArgError("fields-json must be a JSON object, got '%s'" % fields)
        body["fields"] = value
    return json.dumps(body) + "\n"


def _field_pair(option: str, value: str) -> Tuple[str, str]:
    fid, sep, rest = value.partition("=")
    if not sep or not re.fullmatch(FIELD_ID, fid):
        raise ArgError("%s %r: expected <field id>=<value>, field id like customfield_10100" % (option, value))
    return fid, rest


def edit_body(args: Sequence[str], to_adf: Callable[[str], Any]) -> str:
    """Return the JSON body of an issue edit, built from jira-edit's options; to_adf maps a markdown file's path
    to its ADF document."""
    labels: List[Dict[str, str]] = []
    fields: Dict[str, Any] = {}
    for i in range(0, len(args), 2):
        option = args[i]
        if option not in EDIT_OPTIONS:
            raise ArgError("unknown option %s" % option)
        if i + 1 >= len(args):
            raise ArgError("%s needs a value" % option)
        value = args[i + 1]
        if option in ("--add-label", "--remove-label"):
            if not value or re.search(r"\s", value):
                raise ArgError("label %r: Jira labels have no spaces" % value)
            labels.append({"add" if option == "--add-label" else "remove": value})
            continue
        fid, rest = _field_pair(option, value)
        try:
            fields[fid] = json.loads(rest) if option == "--field" else to_adf(rest)
        except ValueError:
            raise ArgError("--field %s: value is not JSON (quote strings: %s='\"text\"')" % (fid, fid)) from None
        except OSError as e:
            raise ArgError("--field-md %s: %s" % (fid, e)) from None
    if labels and "labels" in fields:
        raise ArgError("labels: use --add-label / --remove-label or --field labels=[...], not both")
    body: Dict[str, Any] = {}
    if labels:
        body["update"] = {"labels": labels}
    if fields:
        body["fields"] = fields
    return json.dumps(body, ensure_ascii=False) + "\n"


def comment_body(adf: str) -> str:
    """Return the JSON body of a comment request around an ADF document."""
    return json.dumps({"body": parse_json(adf)}, ensure_ascii=False) + "\n"
