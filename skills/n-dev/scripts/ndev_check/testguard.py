"""Find changes that make tests pass by asking less of them. Pure: callers supply the changed files.

An assistant under pressure to reach green can edit the test instead of the code. Each pattern below is a
legitimate move sometimes (the rule really changed, a platform-only test), so every finding asks for a
one-line reason rather than forbidding the change:
  - an assertion removed or rewritten in a test file that existed before the change;
  - a skip or focus marker added in any test file (a skipped or focused test verifies nothing else);
  - a test file deleted;
  - a snapshot that existed before rewritten;
  - a coverage threshold lowered, or `passWithNoTests` added, in a test or CI config."""
from __future__ import annotations

import fnmatch
import os
import re
from typing import Dict, Iterable, List, Sequence, Tuple

from . import classify
from .literals import blank_strings
from .model import ChangedFile, Finding

KIND = "test-weakened"

_ASSERTION = re.compile(
    r"\bassert|\bexpect\s*\(|\.should\b|\bshould\.|XCTAssert|\bt\.(?:Error|Errorf|Fatal|Fatalf|Fail|FailNow)\b"
    r"|\brequire\.[A-Z]\w*\(|\bverify\s*\(|\bAssert\.|\.(?:not\.)?to(?:Be|Equal|StrictEqual|Match|Contain|Have|Throw"
    r"|Satisfy|Reject|Resolve)\w*\(|\braises\s*\(|\b(?:EXPECT|ASSERT)_[A-Z_]+\(")
_SKIP = re.compile(
    r"\b(?:it|test|describe|context|suite|specify)\.(?:skip|only|todo)(?:If)?\b"
    r"|(?<![\w.$])(?:xit|xtest|xdescribe|xcontext|xspecify|fit|fdescribe|ftest)\s*\("
    r"|@pytest\.mark\.(?:skip|skipif|xfail)\b|\bpytest\.skip\(|@unittest\.(?:skip|expectedFailure)|\.skipTest\("
    r"|@(?:Disabled|Ignore)\b|\bt\.Skip(?:f|Now)?\(|\bmarkTest(?:Skipped|Incomplete)\("
    r"|\[(?:Fact|Theory)\(\s*Skip\b|\[Ignore\]|\bXCTSkip|\bpending\s*[(\"']")
_THRESHOLD = re.compile(  # a coverage key, not part of a longer one such as max-branches or max-lines
    r"(?:--(cov-fail-under)|(?<![\w-])(fail[_-]under|branches|functions|lines|statements|minimum|threshold))"
    r"[\"'>]?\s*[:=]?\s*[\"']?(\d+(?:\.\d+)?)")
_COVERAGE_FILES = ("jest.config.*", "vitest.config.*", "vite.config.*", "karma.conf.*", ".nycrc*", ".c8rc*",
                   "package.json", "pyproject.toml", "setup.cfg", ".coveragerc", "tox.ini", "pytest.ini",
                   "codecov.yml", ".codecov.yml", "phpunit.xml*", "build.gradle*", "pom.xml", "Makefile",
                   ".gitlab-ci.yml", "Jenkinsfile", "bitbucket-pipelines.yml")
_CI_DIRS = (".github/workflows/", ".circleci/")


def check_tests(files: Sequence[ChangedFile], deleted: Iterable[str]) -> List[Finding]:
    out: List[Finding] = [Finding(KIND, p, 0, 0, 0, "test file deleted; name the behaviour it covered and the "
                                  "test that covers it now") for p in deleted if _is_test_code(p)]
    for f in files:
        if _is_test_code(f.path):
            out.extend(_removed_assertions(f) + _skip_markers(f))
        elif is_snapshot(f.path) and not f.is_new and (f.added or f.removed):
            out.append(Finding(KIND, f.path, min(f.added, default=1), 0, 0,
                               "snapshot rewritten; check every changed line is the output the task asked for"))
        elif _is_coverage_config(f.path):
            out.extend(_coverage(f))
    return out


def is_snapshot(path: str) -> bool:
    name = os.path.basename(path)
    return (name.endswith((".snap", ".ambr")) or "__snapshots__/" in path or ".approved." in name
            or ".verified." in name)


def _is_test_code(path: str) -> bool:
    return classify.is_test(path) and classify.is_code(path)


def _is_coverage_config(path: str) -> bool:
    name = os.path.basename(path)
    return any(fnmatch.fnmatch(name, g) for g in _COVERAGE_FILES) or path.startswith(_CI_DIRS)


def _added_rows(f: ChangedFile) -> List[Tuple[int, str]]:
    rows = f.text.split("\n")
    return [(n, rows[n - 1]) for n in sorted(f.added) if n <= len(rows)]


def _removed_assertions(f: ChangedFile) -> List[Finding]:
    if f.is_new:
        return []
    kept = {text.strip() for _, text in _added_rows(f)}
    lost = [(n, text) for n, text in f.removed if _ASSERTION.search(text) and text.strip() not in kept]
    if not lost:
        return []
    first_line, first_text = lost[0]
    return [Finding(KIND, f.path, first_line, len(lost), 0,
                    "%d assertion line(s) removed or rewritten (first at base line %d: `%s`); change a test only "
                    "when the behaviour it pins was asked to change" % (len(lost), first_line, first_text.strip()[:80]))]


def _skip_markers(f: ChangedFile) -> List[Finding]:
    hits = [n for n, text in _added_rows(f) if _SKIP.search(blank_strings(text))]
    if not hits:
        return []
    return [Finding(KIND, f.path, hits[0], len(hits), 0,
                    "%d skip/focus marker(s) added; a skipped or focused test verifies nothing else" % len(hits))]


def _thresholds(text: str) -> Dict[str, float]:
    return {flag or key: float(value) for flag, key, value in _THRESHOLD.findall(text)}


def _coverage(f: ChangedFile) -> List[Finding]:
    before: Dict[str, float] = {}
    for _, text in f.removed:
        before.update(_thresholds(text))
    notes, lines, kept = [], [], set()
    for n, text in _added_rows(f):
        for key, value in _thresholds(text).items():
            kept.add(key)
            if key in before and value < before[key]:
                notes.append("%s %s -> %s" % (key, _num(before[key]), _num(value)))
                lines.append(n)
        if "passWithNoTests" in text:
            notes.append("passWithNoTests added")
            lines.append(n)
    for key in sorted(set(before) - kept):
        notes.append("%s %s removed" % (key, _num(before[key])))
        lines.append(min(f.added, default=1))
    if not notes:
        return []
    return [Finding(KIND, f.path, lines[0], len(notes), 0,
                    "coverage gate weakened (%s); keep the gate, or say why it moved" % "; ".join(notes))]


def _num(value: float) -> str:
    return str(int(value)) if value == int(value) else str(value)
