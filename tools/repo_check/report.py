"""How findings print: one line each, then the RESULT line."""
from __future__ import annotations

from typing import List, Sequence

from .model import Finding


def format_finding(finding: Finding) -> str:
    """The finding as one report line, `ERROR <check>: <message>` or `WARN  <check>: <message>`."""
    return "%-5s %s: %s" % (finding.level, finding.check, finding.message)


def report_lines(findings: Sequence[Finding]) -> List[str]:
    """One line per finding, warnings before errors, then the RESULT line."""
    warnings = [f for f in findings if f.level != "ERROR"]
    errors = [f for f in findings if f.level == "ERROR"]
    return [format_finding(f) for f in warnings + errors] + [
        "RESULT: %s (%d errors, %d warnings)" % ("FAIL" if errors else "PASS", len(errors), len(warnings))]
