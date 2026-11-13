"""The only module that talks to git: resolve the base ref and describe what changed since it."""
from __future__ import annotations

import os
import re
import subprocess
import sys
from typing import List, Optional, Sequence, Tuple

from .model import ChangedFile, count_lines

EMPTY_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"
_HUNK = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")
_OLD_START = re.compile(r"^@@ -(\d+)")


class GitError(RuntimeError):
    pass


def _git(root: str, args: Sequence[str], check: bool = True) -> str:
    proc = subprocess.run(["git", "-c", "core.quotepath=off", *args], cwd=root,
                          capture_output=True, text=True, errors="replace")
    if check and proc.returncode != 0:
        raise GitError("git %s failed: %s" % (" ".join(args), proc.stderr.strip()))
    return proc.stdout if proc.returncode == 0 else ""


def repo_root(start: str) -> str:
    return _git(start, ["rev-parse", "--show-toplevel"]).strip()


def resolve_base(root: str, requested: Optional[str]) -> str:
    """The ref to diff against: the requested one, else the merge-base with the default branch."""
    if requested:
        sha = _git(root, ["rev-parse", "--verify", "--quiet", requested + "^{commit}"], check=False).strip()
        if not sha:
            raise GitError("base ref %r is not a commit" % requested)
        return sha
    if not _git(root, ["rev-parse", "--verify", "--quiet", "HEAD"], check=False).strip():
        return EMPTY_TREE  # repository without commits: everything is new
    for candidate in ("origin/HEAD", "origin/main", "origin/master", "main", "master"):
        sha = _git(root, ["merge-base", "HEAD", candidate], check=False).strip()
        if sha:
            return sha
    return _git(root, ["rev-parse", "HEAD"]).strip()


def _existed_at(root: str, base: str, path: str) -> bool:
    if base == EMPTY_TREE:
        return False
    return subprocess.run(["git", "cat-file", "-e", "%s:%s" % (base, path)], cwd=root,
                          capture_output=True).returncode == 0


def _added_lines(diff_text: str) -> List[int]:
    lines: List[int] = []
    for row in diff_text.splitlines():
        m = _HUNK.match(row)
        if m:
            start, count = int(m.group(1)), int(m.group(2) or "1")
            lines.extend(range(start, start + count))
    return lines


def _removed_lines(diff_text: str) -> List[Tuple[int, str]]:
    """(line number at the base ref, text) of every removed line in a -U0 diff."""
    out: List[Tuple[int, str]] = []
    line = 0
    for row in diff_text.splitlines():
        m = _OLD_START.match(row)
        if m:
            line = int(m.group(1))
        elif row.startswith("-") and not row.startswith("---"):
            out.append((line, row[1:]))
            line += 1
    return out


def _read(root: str, path: str) -> Optional[str]:
    full = os.path.join(root, path)
    try:
        with open(full, "rb") as fh:
            data = fh.read()
    except (FileNotFoundError, IsADirectoryError):
        return None
    except OSError as err:  # no permission, a sandbox block: skip it and say so, never crash the check
        print("note: skipped unreadable path %s (%s)" % (path, err.strerror or err), file=sys.stderr)
        return None
    if b"\0" in data[:8192]:
        return None  # binary
    return data.decode("utf-8", errors="replace")


def changed_files(root: str, base: str) -> List[ChangedFile]:
    """Every text file added or modified between base and the working tree, untracked included."""
    out: List[ChangedFile] = []
    for row in _git(root, ["diff", "--numstat", "--no-renames", base]).splitlines():
        added, removed, path = row.split("\t", 2)
        if added == "-":
            continue  # binary
        text = _read(root, path)
        if text is None:
            continue  # deleted
        if _existed_at(root, base, path):
            hunks = _git(root, ["diff", "-U0", "--no-renames", base, "--", path])
            out.append(ChangedFile(path, False, frozenset(_added_lines(hunks)), int(removed), text,
                                   tuple(_removed_lines(hunks))))
        else:
            out.append(_whole_file(path, text))
    for path in _git(root, ["ls-files", "--others", "--exclude-standard"]).splitlines():
        text = _read(root, path)
        if text is not None:
            out.append(_whole_file(path, text))
    return out


def _whole_file(path: str, text: str) -> ChangedFile:
    return ChangedFile(path, True, frozenset(range(1, count_lines(text) + 1)), 0, text)


def deleted_paths(root: str, base: str) -> List[str]:
    """Files that existed at the base ref and are gone from the working tree."""
    if base == EMPTY_TREE:
        return []
    return _git(root, ["diff", "--name-only", "-M", "--diff-filter=D", base]).splitlines()  # a rename is not a deletion


def tracked_files(root: str) -> List[str]:
    return _git(root, ["ls-files"]).splitlines()


def read_text(root: str, path: str) -> Optional[str]:
    return _read(root, path)


def text_at(root: str, base: str, path: str) -> Optional[str]:
    """The file's text at the base ref, or None when it did not exist there or is binary."""
    if base == EMPTY_TREE:
        return None
    proc = subprocess.run(["git", "show", "%s:%s" % (base, path)], cwd=root, capture_output=True)
    if proc.returncode != 0 or b"\0" in proc.stdout[:8192]:
        return None
    return proc.stdout.decode("utf-8", errors="replace")
