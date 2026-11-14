"""The only module that talks to git: resolve the base ref and describe what changed since it.

git is run as plumbing, so the answer does not depend on the user's configuration or locale: paths come
NUL-separated (never quoted) and are decoded as the file system does, a path is never read as a glob, and
the patch that gives the changed line numbers is uncoloured, never handed to an external tool or a
textconv filter, and has one hunk per edit."""
from __future__ import annotations

import os
import re
import subprocess
import sys
from typing import Iterator, List, NamedTuple, Optional, Sequence, Tuple

from .fileio import HEAD_BYTES, read_unless_head
from .model import ChangedFile, count_lines, printable

EMPTY_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"
_GIT = ("git", "--literal-pathspecs")
_PATCH = ("diff", "-U0", "--no-renames", "--no-color", "--no-ext-diff", "--no-textconv", "--inter-hunk-context=0")
_HUNK = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")


class GitError(RuntimeError):
    """git could not be run, the path is not in a repository, or a command the check depends on failed."""


def _run(root: str, args: Sequence[str]) -> subprocess.CompletedProcess[bytes]:
    """The finished git process, run in `root`. GitError when git cannot be started at all."""
    try:
        return subprocess.run([*_GIT, *args], cwd=root, capture_output=True)
    except OSError as err:
        raise GitError("cannot run git (%s); is git installed and on PATH?" % (err.strerror or err)) from None


def _git(root: str, args: Sequence[str], check: bool = True) -> bytes:
    """git's stdout. A command that fails raises GitError, or gives b"" when `check` is off."""
    proc = _run(root, args)
    if proc.returncode == 0:
        return proc.stdout
    if check:
        reason = " ".join(_text(proc.stderr).split())   # git can explain itself on several lines
        raise GitError("git %s failed: %s" % (" ".join(args), reason))
    return b""


def _text(data: bytes) -> str:
    return data.decode("utf-8", errors="replace")


def _records(listing: bytes) -> List[str]:
    """The entries of a `-z` listing: paths exactly as git stores them, usable to open the file."""
    return [os.fsdecode(entry) for entry in listing.split(b"\0") if entry]


def _commit(root: str, args: Sequence[str], check: bool = False) -> str:
    """The commit id the command prints, or "" when it names none."""
    return _text(_git(root, args, check)).strip()


def repo_root(start: str) -> str:
    """The top-level directory of the repository that `start` is in. GitError when it is in none."""
    if not os.path.isdir(start):
        raise GitError("%s is not a directory" % start)
    return os.fsdecode(_git(start, ["rev-parse", "--show-toplevel"])).rstrip("\r\n")


def resolve_base(root: str, requested: Optional[str]) -> str:
    """The ref to diff against: the requested one, else the merge-base with the default branch."""
    if requested:
        sha = _commit(root, ["rev-parse", "--verify", "--quiet", requested + "^{commit}"])
        if not sha:
            raise GitError("base ref %r is not a commit" % requested)
        return sha
    if not _commit(root, ["rev-parse", "--verify", "--quiet", "HEAD"]):
        return EMPTY_TREE  # repository without commits: everything is new
    for candidate in ("origin/HEAD", "origin/main", "origin/master", "main", "master"):
        sha = _commit(root, ["merge-base", "HEAD", candidate])
        if sha:
            return sha
    return _commit(root, ["rev-parse", "HEAD"], check=True)


def _existed_at(root: str, base: str, path: str) -> bool:
    if base == EMPTY_TREE:
        return False
    return _run(root, ["cat-file", "-e", "%s:%s" % (base, path)]).returncode == 0


class _Hunk(NamedTuple):
    """One edit of a -U0 diff: the lines it removes, and where the lines it adds are in the working tree."""
    old_start: int           # line number at the base ref of the first removed line
    removed: List[str]       # text of each removed line, without the leading `-`
    new_start: int           # line number in the working tree of the first added line
    new_count: int


def _hunks(diff_text: str) -> Iterator[_Hunk]:
    """The hunks of a -U0 diff. A header's counts say which rows that follow are content, so a row is never
    judged by how its own text starts: a removed `-- note` is not a `---` file header, and an added line
    that looks like `@@ -1 +1 @@` opens no hunk."""
    rows = diff_text.split("\n")   # git ends rows with \n only; form feeds and the like are content
    i = 0
    while i < len(rows):
        m = _HUNK.match(rows[i])
        i += 1
        if not m:
            continue  # the file header: diff --git, index, ---, +++
        old_count, new_count = (int(m.group(n) or "1") for n in (2, 4))
        removed = [row[1:].rstrip("\r") for row in rows[i:i + old_count]]
        i += old_count
        i += _marker_rows(rows, i)
        i += new_count
        i += _marker_rows(rows, i)
        yield _Hunk(int(m.group(1)), removed, int(m.group(3)), new_count)


def _marker_rows(rows: Sequence[str], i: int) -> int:
    """1 when row `i` is git's `\\ No newline at end of file`, which may follow a side's last line; else 0."""
    return 1 if i < len(rows) and rows[i].startswith("\\") else 0


def _added_lines(diff_text: str) -> List[int]:
    """Line numbers in the working tree of every line a -U0 diff adds."""
    return [n for h in _hunks(diff_text) for n in range(h.new_start, h.new_start + h.new_count)]


def _removed_lines(diff_text: str) -> List[Tuple[int, str]]:
    """(line number at the base ref, text) of every removed line in a -U0 diff."""
    return [(h.old_start + n, text) for h in _hunks(diff_text) for n, text in enumerate(h.removed)]


def _is_binary(head: bytes) -> bool:
    """git's own rule of thumb: a NUL byte near the start (`head` is the first HEAD_BYTES)."""
    return b"\0" in head


def _read(root: str, path: str) -> Optional[str]:
    """The file's text, or None when there is nothing to check: the path is gone, a directory or binary,
    or cannot be read (no permission, a FIFO or device behind a symlink), which is noted on stderr."""
    try:
        data = read_unless_head(os.path.join(root, path), _is_binary)
    except (FileNotFoundError, NotADirectoryError, IsADirectoryError):
        return None
    except OSError as err:  # skip it and say so, never crash the check
        print("note: skipped unreadable path %s (%s)" % (printable(path), err.strerror or err), file=sys.stderr)
        return None
    return None if data is None else _text(data)


def changed_files(root: str, base: str) -> List[ChangedFile]:
    """Every text file added or modified between base and the working tree, untracked included."""
    out: List[ChangedFile] = []
    for row in _records(_git(root, ["diff", "--numstat", "--no-renames", "-z", base])):
        added, removed, path = row.split("\t", 2)
        if added == "-":
            continue  # binary
        text = _read(root, path)
        if text is None:
            continue  # deleted
        if _existed_at(root, base, path):
            hunks = _text(_git(root, [*_PATCH, base, "--", path]))
            out.append(ChangedFile(path, False, frozenset(_added_lines(hunks)), int(removed), text,
                                   tuple(_removed_lines(hunks))))
        else:
            out.append(_whole_file(path, text))
    for path in _records(_git(root, ["ls-files", "--others", "--exclude-standard", "-z"])):
        text = _read(root, path)
        if text is not None:
            out.append(_whole_file(path, text))
    return out


def _whole_file(path: str, text: str) -> ChangedFile:
    """A file with no version at the base ref: every line counts as added."""
    return ChangedFile(path, True, frozenset(range(1, count_lines(text) + 1)), 0, text)


def deleted_paths(root: str, base: str) -> List[str]:
    """Files that existed at the base ref and are gone from the working tree."""
    if base == EMPTY_TREE:
        return []
    # -M: a rename is not a deletion
    return _records(_git(root, ["diff", "--name-only", "-M", "--diff-filter=D", "-z", base]))


def tracked_files(root: str) -> List[str]:
    """Every path in the index, whether or not it is still in the working tree."""
    return _records(_git(root, ["ls-files", "-z"]))


def read_text(root: str, path: str) -> Optional[str]:
    """The working-tree text of a path, or None when it is gone, binary or unreadable."""
    return _read(root, path)


def text_at(root: str, base: str, path: str) -> Optional[str]:
    """The file's text at the base ref, or None when it did not exist there or is binary."""
    proc = _run(root, ["show", "%s:%s" % (base, path)])
    if proc.returncode != 0 or _is_binary(proc.stdout[:HEAD_BYTES]):
        return None
    return _text(proc.stdout)
