"""Find added blocks that repeat code already in the repository (or elsewhere in the change).
Pure: callers supply the texts; nothing here reads files or runs git."""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from typing import Dict, FrozenSet, Iterable, List, Mapping, Tuple

_TRIVIAL = re.compile(r"^[\s{}()\[\];,.<>/*#-]*$")
_SKIP_PREFIX = ("import ", "from ", "use ", "require", "#include", "package ", "export *",
                "//", "#", "*", "/*", "<?php", "@")
_SKIP_EXACT = {"end", "else", "else {", "} else {", "return;", "break;", "continue;", "pass",
               "return", "default:", "});", "})", "]);", "</div>"}


@dataclass(frozen=True)
class Window:
    path: str
    lines: Tuple[int, ...]   # original line numbers of the meaningful lines in the window

    @property
    def start(self) -> int:
        return self.lines[0]

    @property
    def end(self) -> int:
        return self.lines[-1]


@dataclass(frozen=True)
class Duplicate:
    path: str
    start: int
    end: int
    other_path: str
    other_start: int


def _normalise(line: str) -> str:
    return re.sub(r"\s+", " ", line.strip())


def _opens_import_block(line: str) -> bool:
    """`import {` / `export {` / `from x import (` left open on this line."""
    if not line.startswith(("import ", "export {", "from ")):
        return False
    return line.count("{") > line.count("}") or line.count("(") > line.count(")")


def _closes_import_block(line: str) -> bool:
    """`} from 'x';`, `)`, or a last member that carries the closer (`c)`)."""
    return line.startswith(("}", ")")) or (line.endswith((")", "}", ");", "};")) and "," not in line)


def _meaningful(text: str) -> List[Tuple[int, str]]:
    """(line number, normalised line) for lines that carry logic."""
    out, in_import = [], False
    for n, raw in enumerate(text.splitlines(), start=1):
        line = _normalise(raw)
        if in_import:
            in_import = not _closes_import_block(line)
            continue
        if _opens_import_block(line):
            in_import = True
            continue
        if (len(line) < 4 or _TRIVIAL.match(line) or line in _SKIP_EXACT
                or line.startswith(_SKIP_PREFIX)):
            continue
        out.append((n, line))
    return out


def _windows(path: str, text: str, size: int) -> Iterable[Tuple[str, Window]]:
    rows = _meaningful(text)
    for i in range(len(rows) - size + 1):
        chunk = rows[i:i + size]
        digest = hashlib.sha1("\n".join(l for _, l in chunk).encode()).hexdigest()
        yield digest, Window(path, tuple(n for n, _ in chunk))


def find_duplicates(corpus: Mapping[str, str], added: Mapping[str, FrozenSet[int]],
                    size: int) -> List[Duplicate]:
    """corpus: path -> current text for every file to compare against (changed files included).
    added: path -> added line numbers. A window counts as added when all its lines are added."""
    index: Dict[str, List[Window]] = {}
    for path, text in corpus.items():
        for digest, window in _windows(path, text, size):
            index.setdefault(digest, []).append(window)

    hits: List[Duplicate] = []
    for windows in index.values():
        if len(windows) < 2:
            continue
        fresh = [w for w in windows if set(w.lines) <= added.get(w.path, frozenset())]
        if not fresh:
            continue
        origins = [w for w in windows if w not in fresh]
        # copied from existing code: report every fresh copy; copied within the change: all but the first
        source, copies = (origins[0], fresh) if origins else (fresh[0], fresh[1:])
        hits.extend(Duplicate(w.path, w.start, w.end, source.path, source.start) for w in copies)
    return _merge(hits)


def _merge(hits: List[Duplicate]) -> List[Duplicate]:
    """Collapse overlapping windows in one file into one finding per copied block."""
    merged: List[Duplicate] = []
    for h in sorted(hits, key=lambda d: (d.path, d.start)):
        last = merged[-1] if merged else None
        if last and last.path == h.path and h.start <= last.end + 1:
            merged[-1] = Duplicate(last.path, last.start, max(last.end, h.end),
                                   last.other_path, last.other_start)
        else:
            merged.append(h)
    return merged
