"""Checks c and d: where skills are linked from — the plugin's symlinks and layout list, the root README's table."""
from __future__ import annotations

import os
import re
from typing import List

from .model import PLUGIN, Finding, error, read_text, skill_names

LAYOUT_LINE = re.compile(r"^\s*skills/([\w.-]+)\s+->\s+\S+", re.M)  # "  skills/n-dev  -> ../../../skills/n-dev"


def check_plugin_skills(repo: str) -> List[Finding]:
    """Errors for a plugin skill entry that is not a symlink to skills/<name>/ with a SKILL.md,
    and for a skill the plugin README's layout list names that the plugin does not hold."""
    base = os.path.join(repo, PLUGIN, "skills")
    names = sorted(n for n in os.listdir(base) if not n.startswith(".")) if os.path.isdir(base) else []
    out = []
    for name in names:
        out.extend(_plugin_skill_link(repo, name))
    readme = PLUGIN + "/README.md"
    listed = LAYOUT_LINE.findall(read_text(repo, readme) or "")
    if not listed:
        out.append(error("plugin-skills", "%s has no layout list (lines like 'skills/<name> -> …')" % readme))
    for name in listed:
        if name not in names:
            out.append(error("plugin-skills", "%s's layout names skills/%s, which is not in %s/skills/"
                             % (readme, name, PLUGIN)))
    return out


def _plugin_skill_link(repo: str, name: str) -> List[Finding]:
    rel = "%s/skills/%s" % (PLUGIN, name)
    link, target = os.path.join(repo, rel), os.path.join(repo, "skills", name)
    if not os.path.islink(link):
        return [error("plugin-skills", "%s is not a symlink" % rel)]
    if not os.path.isdir(target) or os.path.realpath(link) != os.path.realpath(target):
        return [error("plugin-skills", "%s -> %s does not resolve to skills/%s/" % (rel, os.readlink(link), name))]
    if not os.path.isfile(os.path.join(target, "SKILL.md")):
        return [error("plugin-skills", "skills/%s/ has no SKILL.md" % name)]
    return []


def check_readme_skills(repo: str) -> List[Finding]:
    """An error per skills/<name>/SKILL.md that no row of the root README's skill table links."""
    rows = [line for line in (read_text(repo, "README.md") or "").splitlines() if line.lstrip().startswith("|")]
    return [error("readme", "skills/%s/SKILL.md is not linked from README.md's skill table" % name)
            for name in skill_names(repo)
            if not any("(skills/%s/SKILL.md)" % name in row for row in rows)]
