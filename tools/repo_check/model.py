"""What every check shares: the finding type, the plugin's fixed paths, and how the repo's files are read."""
from __future__ import annotations

import glob
import json
import os
import re
from typing import Any, Dict, List, NamedTuple, Optional, Tuple

PLUGIN_NAME = "90north-develop"
PLUGIN = "plugins/" + PLUGIN_NAME
MANIFEST = PLUGIN + "/.claude-plugin/plugin.json"
CODE_SPAN = re.compile(r"`([^`\n]+)`")


class Finding(NamedTuple):
    """One line of the report: `level` is ERROR or WARN, `check` names the check that found it."""
    level: str
    check: str
    message: str


class Doc(NamedTuple):
    """One markdown file the text checks read; `skill` is its skill folder's name, None for a plugin agent."""
    rel: str
    skill: Optional[str]
    text: str


def error(check: str, message: str) -> Finding:
    """A finding that fails the run."""
    return Finding("ERROR", check, message)


def warn(check: str, message: str) -> Finding:
    """A finding that is printed and counted while the run still passes."""
    return Finding("WARN", check, message)


def read_text(repo: str, rel: str) -> Optional[str]:
    """The text of a file given by its path from the repo root, or None when it cannot be read."""
    try:
        with open(os.path.join(repo, rel), encoding="utf-8") as fh:
            return fh.read()
    except OSError:
        return None


def load_json(repo: str, rel: str) -> Optional[Dict[str, Any]]:
    """The file as a JSON object, or None when it is missing, malformed or not an object."""
    try:
        data = json.loads(read_text(repo, rel) or "")
    except ValueError:
        return None
    return data if isinstance(data, dict) else None


def skill_names(repo: str) -> List[str]:
    """Sorted names of the folders under skills/ that hold a SKILL.md."""
    found = glob.glob(os.path.join(repo, "skills", "*", "SKILL.md"))
    return sorted(os.path.basename(os.path.dirname(p)) for p in found)


def docs(repo: str) -> List[Doc]:
    """The markdown the text checks read: each skill's SKILL.md, references/*.md and templates/*.md,
    then the plugin's agents/*.md."""
    out: List[Tuple[str, Optional[str]]] = []
    for name in skill_names(repo):
        base = os.path.join(repo, "skills", name)
        paths = [os.path.join(base, "SKILL.md")]
        for sub in ("references", "templates"):
            paths += sorted(glob.glob(os.path.join(base, sub, "*.md")))
        out += [(os.path.relpath(p, repo), name) for p in paths]
    for p in sorted(glob.glob(os.path.join(repo, PLUGIN, "agents", "*.md"))):
        out.append((os.path.relpath(p, repo), None))
    return [Doc(rel, skill, read_text(repo, rel) or "") for rel, skill in out]


READMES = ("README.md", PLUGIN + "/README.md", PLUGIN + "/evals/README.md", "skills/n-dev/evals/README.md")


def readmes(repo: str) -> List[Doc]:
    """The READMEs a person follows: only their `file § Section` references are checked, because their prose also
    names old commands and example paths on purpose."""
    return [Doc(rel, None, read_text(repo, rel) or "") for rel in READMES if os.path.isfile(os.path.join(repo, rel))]


def prose_lines(text: str) -> List[str]:
    """The text's lines with fenced code blocks blanked, so line numbers stay true."""
    out: List[str] = []
    fence: Optional[str] = None
    for line in text.splitlines():
        marker = line.lstrip()[:3]
        if fence is None and marker in ("```", "~~~"):
            fence = marker
            out.append("")
        elif fence is not None:
            fence = None if marker == fence else fence
            out.append("")
        else:
            out.append(line)
    return out
