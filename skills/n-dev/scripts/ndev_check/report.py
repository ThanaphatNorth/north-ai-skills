"""Render findings as text or JSON. Pure: returns strings."""
from __future__ import annotations

import json
from typing import List, Sequence

from .model import Budgets, Finding

_TITLES = {
    "wiring": "Pre-existing files changed beyond a wiring diff",
    "file-size": "Files over budget",
    "function-size": "Functions over budget",
    "duplicate": "Blocks that repeat existing code",
}
_EXISTING_TITLE = ("Already over budget at the base ref (%d) — not caused by this change; "
                   "mention it, refactor it only if the task asks")


def as_text(findings: List[Finding], base: str, budgets: Budgets, existing: Sequence[Finding] = ()) -> str:
    head = "n-dev structure check against %s (file %d, test file %d, function %d, wiring %d, dup %d lines)" % (
        base[:12], budgets.max_file, budgets.max_test_file, budgets.max_func,
        budgets.max_wiring, budgets.dup_lines)
    out = [head]
    for kind, title in _TITLES.items():
        group = [f for f in findings if f.kind == kind]
        if not group:
            continue
        out.append("\n%s (%d)" % (title, len(group)))
        out.extend("  %s:%d  %s" % (f.path, f.line, f.message) for f in group)
    if existing:
        out.append("\n" + _EXISTING_TITLE % len(existing))
        out.extend("  %s:%d  %s" % (f.path, f.line, f.message) for f in existing)
    result = ("%d finding(s) — fix each, or give a one-line reason in the report" % len(findings)
              if findings else "clean")
    note = "; %d already over budget at the base ref (informational)" % len(existing) if existing else ""
    out.append("%sRESULT: %s%s" % ("\n" if len(out) > 1 else "", result, note))
    return "\n".join(out)


def as_json(findings: List[Finding], base: str, budgets: Budgets, existing: Sequence[Finding] = ()) -> str:
    return json.dumps({"base": base, "budgets": budgets.__dict__,
                       "findings": [f.as_dict() for f in findings],
                       "existing": [f.as_dict() for f in existing]}, indent=2)
