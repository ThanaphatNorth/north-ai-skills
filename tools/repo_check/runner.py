"""The list of checks, in report order, and the one function that runs them all."""
from __future__ import annotations

from typing import List

from .layout import check_plugin_skills, check_readme_skills
from .ledger import check_ledger_states
from .manifests import check_agents_registered, check_versions
from .model import Finding
from .names import check_agent_names
from .paths import check_paths
from .sections import check_sections

__all__ = ["CHECKS", "run_checks", "check_versions", "check_agents_registered", "check_plugin_skills",
           "check_readme_skills", "check_paths", "check_sections", "check_ledger_states", "check_agent_names"]

CHECKS = (check_versions, check_agents_registered, check_plugin_skills, check_readme_skills,
          check_paths, check_sections, check_ledger_states, check_agent_names)


def run_checks(repo: str) -> List[Finding]:
    """The findings of every check over the repo root, in check order."""
    return [finding for check in CHECKS for finding in check(repo)]
