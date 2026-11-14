"""Value types shared by every check. Plain data, no behaviour beyond formatting."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, FrozenSet, Optional, Tuple, Union

# Characters that end a line for a terminal or for `str.splitlines`, plus the other C0 controls and DEL.
# A tab stays: code quoted in a message may hold one, and it breaks no line.
_UNPRINTABLE = re.compile("[\x00-\x08\x0a-\x1f\x7f\x85\u2028\u2029]")


def count_lines(text: str) -> int:
    """Lines as an editor shows them: a trailing newline does not start a new line."""
    return text.count("\n") + (0 if text.endswith("\n") or not text else 1)


def printable(text: str) -> str:
    """The text with control characters written as escapes (a newline becomes `\\n`), so a path or message
    taken from the repository always stays on the one line a report gives it."""
    return _UNPRINTABLE.sub(lambda m: m.group().encode("unicode_escape").decode("ascii"), text)


@dataclass(frozen=True)
class Budgets:
    """Every threshold the checks use; the CLI is the only place that builds one."""
    max_file: int = 300
    max_test_file: int = 600
    max_func: int = 50
    max_wiring: int = 20
    dup_lines: int = 6
    max_line: int = 140          # characters per added line; 0 turns the check off


@dataclass(frozen=True)
class ChangedFile:
    """One text file the change added or modified: its current content and which lines the change touched."""
    path: str
    is_new: bool                 # did not exist at the base ref
    added: FrozenSet[int]        # 1-based line numbers added in the working tree
    removed_count: int           # lines removed relative to the base ref
    text: str                    # current working-tree content
    removed: Tuple[Tuple[int, str], ...] = ()   # (line number at the base ref, text) of removed lines

    @property
    def line_count(self) -> int:
        """Lines in the current content, counted as `count_lines` does."""
        return count_lines(self.text)


@dataclass(frozen=True)
class Layer:
    """One architectural layer from the repo's config: which files belong to it, which import
    specifiers refer to it, and which other layers its files may import."""
    name: str
    paths: Tuple[str, ...]       # globs of files in the layer
    imports: Tuple[str, ...]     # specifier prefixes that refer to it (aliases, packages, namespaces)
    may_import: Tuple[str, ...]  # names of the other layers it may depend on


@dataclass(frozen=True)
class Finding:
    """One thing the check reports: what kind, where, the measured value against its limit, and what to do."""
    kind: str                    # wiring | file-size | function-size | long-line | duplicate | layer
                                 # | test-weakened | new-dependency
    path: str
    line: int
    value: int
    limit: int
    message: str
    related: Optional[str] = field(default=None)

    def as_dict(self) -> Dict[str, Union[str, int]]:
        """The finding as the JSON report shows it: every field, `related` only when it is set."""
        return {k: v for k, v in self.__dict__.items() if v is not None}
