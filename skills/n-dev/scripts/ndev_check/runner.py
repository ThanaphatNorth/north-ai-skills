"""Compose the checks: git facts in, findings out. The one place that wires the modules."""
from __future__ import annotations

from operator import attrgetter
from typing import Dict, List, Sequence, Tuple

from . import baseline, classify, gitdiff
from .budgets import check_all
from .duplicates import find_duplicates
from .model import Budgets, ChangedFile, Finding

MAX_CORPUS_BYTES = 512 * 1024


def run(root: str, base: str, budgets: Budgets,
        excludes: Sequence[str] = ()) -> Tuple[List[Finding], List[Finding]]:
    """(findings this change caused, debt that was already over budget at the base ref)."""
    files = [f for f in gitdiff.changed_files(root, base)
             if classify.is_code(f.path) and not classify.is_noise(f.path, excludes)]
    findings: List[Finding] = []
    for f in files:
        findings.extend(check_all(f, budgets))
    findings.extend(_duplicate_findings(root, files, budgets, excludes))
    flagged = {x.path for x in findings}
    current = {f.path: f.text for f in files if f.path in flagged}
    was = {f.path: gitdiff.text_at(root, base, f.path) for f in files if f.path in flagged and not f.is_new}
    new, existing = baseline.split(findings, current, was)
    key = attrgetter("kind", "path", "line")
    return sorted(new, key=key), sorted(existing, key=key)


def _duplicate_findings(root: str, files: List[ChangedFile], b: Budgets,
                        excludes: Sequence[str]) -> List[Finding]:
    sources = [f for f in files if not classify.is_test(f.path)]
    if not sources:
        return []
    exts = {classify.extension(f.path) for f in sources}
    corpus: Dict[str, str] = {f.path: f.text for f in sources}
    for path in gitdiff.tracked_files(root):
        if path in corpus or classify.extension(path) not in exts:
            continue
        if classify.is_noise(path, excludes) or classify.is_test(path):
            continue
        text = gitdiff.read_text(root, path)
        if text is not None and len(text) <= MAX_CORPUS_BYTES:
            corpus[path] = text
    added = {f.path: f.added for f in sources}
    return [Finding("duplicate", d.path, d.start, d.end - d.start + 1, b.dup_lines,
                    "block repeats %s:%d; reuse or extract the shared part" % (d.other_path, d.other_start),
                    related="%s:%d" % (d.other_path, d.other_start))
            for d in find_duplicates(corpus, added, b.dup_lines)]
