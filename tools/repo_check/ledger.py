"""Check g: every ledger state a loop's Gates table names is a parked state of the shared stages."""
from __future__ import annotations

import re
from typing import List, Optional

from .model import CODE_SPAN, Finding, error, read_text

STAGES = "skills/workflow/references/stages.md"
GATE_FILES = ("skills/n-defect-loop/SKILL.md", "skills/n-develop-loop/SKILL.md")


def check_ledger_states(repo: str) -> List[Finding]:
    """An error per state in a loop's Gates table (`Ledger state` column) that the parked-state list
    of stages.md § S0 item 3 does not hold. `from-…` hand-off rows are exempt."""
    parked = parked_states(read_text(repo, STAGES) or "")
    if parked is None:
        return [error("ledger", "%s § S0 item 3 has no 'parked state (…)' list" % STAGES)]
    out = []
    for rel in GATE_FILES:
        states = gate_states(read_text(repo, rel) or "")
        if states is None:
            out.append(error("ledger", "%s has no Gates table with a 'Ledger state' column" % rel))
            continue
        out += [error("ledger", "%s § Gates: `%s` is not a parked state in %s § S0 item 3" % (rel, s, STAGES))
                for s in states if not s.startswith("from-") and not any(_state_matches(s, p) for p in parked)]
    return out


def parked_states(stages_text: str) -> Optional[List[str]]:
    """The backticked states of the `parked state (…)` list in item 3 of the S0 section; None without one."""
    in_s0 = False
    for line in stages_text.splitlines():
        if line.startswith("#"):
            in_s0 = re.match(r"#+\s*S0\b", line) is not None
        elif in_s0 and re.match(r"\s*3\.\s", line):
            m = re.search(r"parked state \(([^)]*)\)", line)
            return CODE_SPAN.findall(m.group(1)) if m else None
    return None


def gate_states(skill_text: str) -> Optional[List[str]]:
    """The backticked states in the `Ledger state` column of the table under the Gates heading;
    None when there is no such heading, table or column."""
    lines = skill_text.splitlines()
    starts = [i for i, line in enumerate(lines) if re.match(r"#+\s*Gates\b", line)]
    column: Optional[int] = None
    states: List[str] = []
    for line in lines[starts[0] + 1:] if starts else []:
        if line.startswith("#"):
            break
        if not line.lstrip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if column is None:
            if "Ledger state" not in cells:
                return None
            column = cells.index("Ledger state")
        elif column < len(cells):
            states += CODE_SPAN.findall(cells[column])
    return states if column is not None else None


def _state_matches(state: str, parked: str) -> bool:
    """`parked` may hold a placeholder, as in `handed-to-<loop>`."""
    pattern = "".join(".+" if part.startswith("<") else re.escape(part)
                      for part in re.split(r"(<[^>]*>)", parked))
    return re.fullmatch(pattern, state) is not None
