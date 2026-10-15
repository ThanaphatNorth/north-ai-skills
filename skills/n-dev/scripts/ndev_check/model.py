"""Value types shared by every check. Plain data, no behaviour beyond formatting."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import FrozenSet, Optional


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


@dataclass(frozen=True)
class ChangedFile:
    path: str
    is_new: bool                 # did not exist at the base ref
    added: FrozenSet[int]        # 1-based line numbers added in the working tree
    removed_count: int           # lines removed relative to the base ref
    text: str                    # current working-tree content

    @property
    def line_count(self) -> int:
        return count_lines(self.text)


@dataclass(frozen=True)
class Finding:
    kind: str                    # wiring | file-size | function-size | duplicate
    path: str
    line: int
    value: int
    limit: int
    message: str
    related: Optional[str] = field(default=None)

    def as_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items() if v is not None}
