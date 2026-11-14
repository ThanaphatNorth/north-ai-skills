"""Budget checks on changed files: wiring diff size, file size, function size. Pure."""
from __future__ import annotations

from typing import List

from . import classify
from .functions import find_spans
from .model import Budgets, ChangedFile, Finding


def check_wiring(f: ChangedFile, b: Budgets) -> List[Finding]:
    """A pre-existing source file should only gain a wiring diff (rule 2). Added lines count;
    removed ones do not, so moving code out into a new module is never penalised. Test files
    are exempt: adding cases to an existing suite is the expected way to grow it."""
    if f.is_new or classify.is_test(f.path) or len(f.added) <= b.max_wiring:
        return []
    return [Finding("wiring", f.path, min(f.added), len(f.added), b.max_wiring,
                    "pre-existing file gained %d lines (-%d removed); move new logic into a new "
                    "module, or record the in-place reason" % (len(f.added), f.removed_count))]


def check_file_size(f: ChangedFile, b: Budgets) -> List[Finding]:
    """A finding when a new file, or one this change added lines to, is over its line budget
    (test files have their own, larger one)."""
    limit = b.max_test_file if classify.is_test(f.path) else b.max_file
    n = f.line_count
    if n <= limit or not (f.is_new or f.added):
        return []
    grown = "new file" if f.is_new else "file grew in this change"
    return [Finding("file-size", f.path, 1, n, limit,
                    "%s has %d lines; split by responsibility" % (grown, n))]


def check_function_size(f: ChangedFile, b: Budgets) -> List[Finding]:
    """Long functions that this change wrote or touched. Test files are exempt."""
    if classify.is_test(f.path):
        return []
    out: List[Finding] = []
    for span in find_spans(f.text, classify.function_style(f.path)):
        touched = any(span.start <= n <= span.end for n in f.added)
        if span.length > b.max_func and touched:
            out.append(Finding("function-size", f.path, span.start, span.length, b.max_func,
                               "function %s is %d lines; extract named steps" % (span.name, span.length)))
    return out


def _breakable(line: str, limit: int) -> bool:
    """False when one unbreakable token (URL, hash, long string) makes the line long: a formatter cannot split it."""
    longest = max((len(t) for t in line.split()), default=0)
    return len(line) - longest >= limit // 2


def check_line_length(f: ChangedFile, b: Budgets) -> List[Finding]:
    """Added lines over the width budget, one finding per file (first line, count, longest). Only lines
    this change wrote count, so existing dense code is never reported. Test files are exempt."""
    if not b.max_line or classify.is_test(f.path):
        return []
    rows = f.text.split("\n")
    long = [n for n in sorted(f.added) if n <= len(rows) and len(rows[n - 1]) > b.max_line
            and _breakable(rows[n - 1], b.max_line)]
    if not long:
        return []
    widest = max(len(rows[n - 1]) for n in long)
    return [Finding("long-line", f.path, long[0], widest, b.max_line,
                    "%d added line(s) wider than %d characters (longest %d); break them up or run the "
                    "repo's formatter" % (len(long), b.max_line, widest))]


def check_all(f: ChangedFile, b: Budgets) -> List[Finding]:
    """Every budget finding for one changed file: wiring, file size, function size, line width."""
    return (check_wiring(f, b) + check_file_size(f, b) + check_function_size(f, b)
            + check_line_length(f, b))
