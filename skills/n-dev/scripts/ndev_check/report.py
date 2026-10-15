"""Render findings as text or JSON. Pure: returns strings."""
from __future__ import annotations

import json
from typing import List

from .model import Budgets, Finding

_TITLES = {
    "wiring": "Pre-existing files changed beyond a wiring diff",
    "file-size": "Files over budget",
    "function-size": "Functions over budget",
    "duplicate": "Blocks that repeat existing code",
}


def as_text(findings: List[Finding], base: str, budgets: Budgets) -> str:
    head = "n-dev structure check against %s (file %d, test file %d, function %d, wiring %d, dup %d lines)" % (
        base[:12], budgets.max_file, budgets.max_test_file, budgets.max_func,
        budgets.max_wiring, budgets.dup_lines)
    if not findings:
        return head + "\nRESULT: clean"
    out = [head]
    for kind, title in _TITLES.items():
        group = [f for f in findings if f.kind == kind]
        if not group:
            continue
        out.append("\n%s (%d)" % (title, len(group)))
        out.extend("  %s:%d  %s" % (f.path, f.line, f.message) for f in group)
    out.append("\nRESULT: %d finding(s) — fix each, or give a one-line reason in the report" % len(findings))
    return "\n".join(out)


def as_json(findings: List[Finding], base: str, budgets: Budgets) -> str:
    return json.dumps({"base": base, "budgets": budgets.__dict__,
                       "findings": [f.as_dict() for f in findings]}, indent=2)
