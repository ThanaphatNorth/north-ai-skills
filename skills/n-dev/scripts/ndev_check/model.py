"""Value types shared by every check. Plain data, no behaviour beyond formatting."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import FrozenSet, Optional, Tuple


def count_lines(text: str) -> int:
    """Lines as an editor shows them: a trailing newline does not start a new line."""
    return text.count("\n") + (0 if text.endswith("\n") or not text else 1)


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
    path: str
    is_new: bool                 # did not exist at the base ref
    added: FrozenSet[int]        # 1-based line numbers added in the working tree
    removed_count: int           # lines removed relative to the base ref
    text: str                    # current working-tree content
    removed: Tuple[Tuple[int, str], ...] = ()   # (line number at the base ref, text) of removed lines

    @property
    def line_count(self) -> int:
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
    kind: str                    # wiring | file-size | function-size | long-line | duplicate | layer
                                 # | test-weakened | new-dependency
    path: str
    line: int
    value: int
    limit: int
    message: str
    related: Optional[str] = field(default=None)

    def as_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items() if v is not None}
