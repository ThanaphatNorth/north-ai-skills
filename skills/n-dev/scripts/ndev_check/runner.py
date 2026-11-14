"""Compose the checks: git facts in, findings out. The one place that wires the modules."""
from __future__ import annotations

from operator import attrgetter
from typing import Dict, List, Sequence, Tuple

from . import baseline, classify, gitdiff
from .budgets import check_all
from .deps import check_deps, is_manifest
from .duplicates import find_duplicates
from .layers import check_layers
from .model import Budgets, ChangedFile, Finding, Layer
from .testguard import check_tests, is_snapshot

MAX_CORPUS_BYTES = 512 * 1024


def run(root: str, base: str, budgets: Budgets, excludes: Sequence[str] = (), layers: Sequence[Layer] = (),
        audit: bool = False) -> Tuple[List[Finding], List[Finding]]:
    """(findings this change caused, debt that was already over budget at the base ref). `audit` means the
    base is the empty tree: every file counts as new, so change-only checks are skipped."""
    changed = gitdiff.changed_files(root, base)
    files = [f for f in changed if classify.is_code(f.path) and not classify.is_noise(f.path, excludes)]
    findings: List[Finding] = []
    for f in files:
        findings.extend(check_all(f, budgets))
    findings.extend(_duplicate_findings(root, files, budgets, excludes))
    findings.extend(check_layers(files, layers, {f.path: gitdiff.text_at(root, base, f.path)
                                                 for f in files if layers and not f.is_new}))
    if not audit:
        findings.extend(_change_only_findings(root, base, changed, excludes))
    new, existing = _apart_from_existing_debt(root, base, files, findings)
    key = attrgetter("kind", "path", "line")
    return sorted(new, key=key), sorted(existing, key=key)


def _change_only_findings(root: str, base: str, changed: Sequence[ChangedFile],
                          excludes: Sequence[str]) -> List[Finding]:
    """Weakened tests and added dependencies: both compare with the base ref, so an audit has none."""
    tests = check_tests([f for f in changed if _guarded(f.path, excludes)],
                        [p for p in gitdiff.deleted_paths(root, base) if _guarded(p, excludes)])
    manifests = [f for f in changed if is_manifest(f.path) and not classify.is_noise(f.path, excludes)]
    return tests + check_deps(manifests, {f.path: None if f.is_new else gitdiff.text_at(root, base, f.path)
                                          for f in manifests})


def _apart_from_existing_debt(root: str, base: str, files: Sequence[ChangedFile],
                              findings: List[Finding]) -> Tuple[List[Finding], List[Finding]]:
    """(caused by this change, already over budget at the base ref). Only flagged files are read at the base."""
    flagged = {x.path for x in findings}
    current = {f.path: f.text for f in files if f.path in flagged}
    was = {f.path: gitdiff.text_at(root, base, f.path) for f in files if f.path in flagged and not f.is_new}
    return baseline.split(findings, current, was)


def _guarded(path: str, excludes: Sequence[str]) -> bool:
    """Inputs of the test guard: everything but excluded paths and noise, except snapshots (noise elsewhere)."""
    return not classify.matches_any(path, excludes) and (is_snapshot(path) or not classify.is_noise(path))


def _duplicate_findings(root: str, files: List[ChangedFile], b: Budgets,
                        excludes: Sequence[str]) -> List[Finding]:
    """One finding per block a changed source file copied; test files may repeat themselves."""
    sources = [f for f in files if not classify.is_test(f.path)]
    if not sources:
        return []
    added = {f.path: f.added for f in sources}
    return [Finding("duplicate", d.path, d.start, d.end - d.start + 1, b.dup_lines,
                    "block repeats %s:%d; reuse or extract the shared part" % (d.other_path, d.other_start),
                    related="%s:%d" % (d.other_path, d.other_start))
            for d in find_duplicates(_corpus(root, sources, excludes), added, b.dup_lines)]


def _corpus(root: str, sources: Sequence[ChangedFile], excludes: Sequence[str]) -> Dict[str, str]:
    """path -> text of everything a copied block is searched in: the changed sources, then every tracked
    file in their languages that is not noise, not a test, readable and at most MAX_CORPUS_BYTES long."""
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
    return corpus
