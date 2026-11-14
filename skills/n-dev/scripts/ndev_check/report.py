"""Render findings as text or JSON. Pure: returns strings."""
from __future__ import annotations

import json
from typing import List, Optional, Sequence

from .model import Budgets, Finding, printable

_TITLES = {
    "wiring": "Pre-existing files changed beyond a wiring diff",
    "file-size": "Files over budget",
    "function-size": "Functions over budget",
    "long-line": "Added lines over the width budget",
    "duplicate": "Blocks that repeat existing code",
    "layer": "Imports that cross a layer rule",
    "test-weakened": "Changes that weaken tests",
    "new-dependency": "Dependencies added",
}
_EXISTING_TITLE = ("Already over budget at the base ref (%d) — not caused by this change; "
                   "mention it, refactor it only if the task asks")


def as_text(findings: List[Finding], base: str, budgets: Budgets, existing: Sequence[Finding] = (),
            config: Optional[str] = None) -> str:
    """The report people read: a header, findings grouped by kind, existing debt apart, and a last line
    that starts `RESULT:`."""
    head = "n-dev structure check against %s (file %d, test file %d, function %d, wiring %d, dup %d lines, line %d)" % (
        base if base.startswith("(") else base[:12], budgets.max_file, budgets.max_test_file, budgets.max_func,
        budgets.max_wiring, budgets.dup_lines, budgets.max_line)
    out = [head + (", config %s" % config if config else "")]
    if base.startswith("("):
        out.append("Audit: every file counts as new, so read \"new\" and \"added\" below as \"present\".")
    for kind, title in _TITLES.items():
        group = [f for f in findings if f.kind == kind]
        if not group:
            continue
        out.append("\n%s (%d)" % (title, len(group)))
        out.extend(_row(f) for f in group)
    if existing:
        out.append("\n" + _EXISTING_TITLE % len(existing))
        out.extend(_row(f) for f in existing)
    result = ("%d finding(s) — fix each, or give a one-line reason in the report" % len(findings)
              if findings else "clean")
    note = "; %d already over budget at the base ref (informational)" % len(existing) if existing else ""
    out.append("%sRESULT: %s%s" % ("\n" if len(out) > 1 else "", result, note))
    return "\n".join(out)


def _row(f: Finding) -> str:
    """One finding on one line, whatever characters its path or the code it quotes contains."""
    return "  %s:%d  %s" % (printable(f.path), f.line, printable(f.message))


def as_json(findings: List[Finding], base: str, budgets: Budgets, existing: Sequence[Finding] = (),
            config: Optional[str] = None) -> str:
    """The same report as one JSON object: base, config, budgets, findings, existing."""
    return json.dumps({"base": base, "config": config, "budgets": budgets.__dict__,
                       "findings": [f.as_dict() for f in findings],
                       "existing": [f.as_dict() for f in existing]}, indent=2)
