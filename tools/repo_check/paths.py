"""Check e: backticked repo paths in skills and agents resolve to files. Owns the target-project skip list."""
from __future__ import annotations

import fnmatch
import glob
import os
from typing import List, Optional, Set

from .model import CODE_SPAN, Doc, Finding, docs, error, prose_lines, skill_names, warn

# What makes a backticked word a repo path. `W/` is the loops' alias for `../workflow/`.
REPO_PREFIXES = ("references/", "templates/", "scripts/", "../", "W/")
REPO_SUFFIXES = (".md", ".py", ".sh", ".toml", ".json")
INTERPRETERS = ("python3", "python", "node", "bash", "sh")  # `python3 scripts/x.py …`: the program is word two
SEARCH_DIRS = ("", "references", "templates", "scripts", "scripts/tests")  # where a bare file name may live

# Skip list: paths that live in a target project, not in this repo. Explicit on purpose; a name that
# is neither found nor listed here is reported as a warning.
PLACEHOLDER_MARKS = ("<", ">", "{", "}", "…", "://")  # `<KEY>.md`, `{slug}.md`, a URL
TARGET_PREFIXES = (
    "docs/",     # the target repo's docs: architecture profile, feature docs
    ".claude/",  # the target repo's Claude folder: state, agents, launch.json
    "DL/",       # the loops' alias for <repo>/.90north-develop/, the working state
    "DC/",       # the loops' alias for <repo>/.claude/90north-develop/, the settings
    ".90north-develop/",  # the target repo's working-state folder
    "~/",        # the user's home
    "src/",      # the target repo's source
    "board/",    # the local board's cards
)
TARGET_NAMES = (  # bare names only: `templates/card.md` is checked, `card.md` is a run file
    # run files of one card, written to DL/runs/<date>/<KEY>/ or the scratchpad
    "triage.md", "card.md", "before.md", "build.md", "proof.md", "verify.md", "ship.md", "review*.md",
    "qa.md", "comment.md", "design-note.md",
    # run files of one pass, written to DL/runs/<date>/
    "run.md", "learn.md", "outcomes.md", "weekly.md",
    # per-repo files: config in DC/; lessons, the ledgers (legacy `ledger.md`, `ai-ledger.md`) and knowledge in DL/
    "config.md", "lessons.md", "ledger.md", "*-ledger.md", "code-map.md", "selectors.md", "calibration.md",
    # cards of a local board
    "_template.md", "TASK-*.md",
    # files of the target repo itself
    ".ndev.toml", "package.json", ".gitleaks.toml",
    # design-atlas: what palette.py writes into the user's folder, the DTCG file extensions, three.js's index
    "tokens.json", "palette-report.md", ".tokens.json", ".resolver.json", "files.json",
)


def check_paths(repo: str) -> List[Finding]:
    """An error per backticked references/, templates/, scripts/, ../ or W/ path that resolves to no
    file; a warning per other file-like name that is neither found nor on the target-project skip list."""
    return [finding for doc in docs(repo) for finding in _doc_paths(repo, doc)]


def _doc_paths(repo: str, doc: Doc) -> List[Finding]:
    """Each path is reported once per file, at its first line."""
    out = []
    seen: Set[str] = set()
    for number, line in enumerate(prose_lines(doc.text), 1):
        for token in (path_token(span) for span in CODE_SPAN.findall(line)):
            if token is None or token in seen or is_target_path(token):
                continue
            seen.add(token)
            where = "%s:%d `%s`" % (doc.rel, number, token)
            if resolve(repo, doc, token):
                continue
            if token.startswith(REPO_PREFIXES):
                out.append(error("paths", "%s does not exist" % where))
            else:
                out.append(warn("paths", "%s is not found in this repo and is not on the skip list" % where))
    return out


def path_token(span: str) -> Optional[str]:
    """The word of a code span that may name a repo file (the span itself, or the program of a
    command such as `python3 scripts/x.py --flag`); None when it does not look like one."""
    words = span.split()
    if len(words) > 1 and words[0] in INTERPRETERS:
        words = words[1:]
    if not words:
        return None
    token = words[0]
    named = token.startswith(REPO_PREFIXES) or (token.endswith(REPO_SUFFIXES) and token not in REPO_SUFFIXES)
    return token if named else None


def is_target_path(token: str) -> bool:
    """True for a placeholder, a URL, an absolute path, or a path on the target-project skip list."""
    if any(mark in token for mark in PLACEHOLDER_MARKS) or token.startswith("/"):
        return True
    if token.startswith(TARGET_PREFIXES):
        return True
    return "/" not in token and any(fnmatch.fnmatchcase(token, pattern) for pattern in TARGET_NAMES)


def resolve(repo: str, doc: Doc, token: str) -> List[str]:
    """Existing paths the token may name: one when the file's own skill, its folder, the repo root or
    skills/ holds it; else each other skill's file of that name (the prose names the owner)."""
    if token.startswith("W/"):
        return _existing([os.path.join(repo, "skills", "workflow", token[2:])])
    bare = "/" not in token
    near = [os.path.dirname(os.path.join(repo, doc.rel)), repo, os.path.join(repo, "skills")]
    if doc.skill:
        own = os.path.join(repo, "skills", doc.skill)
        near = [own] + near + ([os.path.join(own, sub) for sub in SEARCH_DIRS] if bare else [])
    hits = _existing([os.path.join(base, token) for base in near])
    if hits or token.startswith("../"):
        return hits[:1]
    far = []
    for name in skill_names(repo):
        if name != doc.skill:
            subs = SEARCH_DIRS if bare else ("",)
            far += _existing([os.path.join(repo, "skills", name, sub, token) for sub in subs])[:1]
    return far


def _existing(paths: List[str]) -> List[str]:
    out = []
    for path in (os.path.normpath(p) for p in paths):
        out += sorted(glob.glob(path))[:1] if "*" in path else [path] if os.path.exists(path) else []
    return out
