"""Split findings into debt this change caused and debt that was already there at the base ref. Pure.

Only the size checks measure a whole file or function, so only they can report debt the change merely
touched. A size finding is existing debt when the same file, or the same function (matched by name
and order of appearance), was already over the limit at the base ref; growth of such debt is still
caught by the wiring check. Every other finding describes the change itself and stays new."""
from __future__ import annotations

from typing import List, Mapping, Optional, Tuple

from . import classify
from .functions import Span, find_spans
from .model import Finding, count_lines

Texts = Mapping[str, Optional[str]]


def split(findings: List[Finding], current_texts: Texts,
          base_texts: Texts) -> Tuple[List[Finding], List[Finding]]:
    """(new, existing). `base_texts` maps a path to its text at the base ref, None when it did not exist."""
    new: List[Finding] = []
    existing: List[Finding] = []
    for f in findings:
        old = _existing(f, current_texts.get(f.path), base_texts.get(f.path))
        (existing if old else new).append(old or f)
    return new, existing


def _existing(f: Finding, now: Optional[str], was: Optional[str]) -> Optional[Finding]:
    """The finding re-worded as existing debt when the same file or function was already over the limit
    at the base ref; None when this change caused it."""
    if was is None or now is None:
        return None
    if f.kind == "file-size":
        size = count_lines(was)
        message = "file had %d lines at the base ref, %d now" % (size, f.value)
    elif f.kind == "function-size":
        match = _same_function(f, now, was)
        if match is None:
            return None
        size = match.length
        message = "function %s had %d lines at the base ref, %d now" % (match.name, size, f.value)
    else:
        return None
    if size <= f.limit:
        return None
    return Finding(f.kind, f.path, f.line, f.value, f.limit, message, f.related)


def _same_function(f: Finding, now: str, was: str) -> Optional[Span]:
    """The function the finding is about, as it was at the base ref: same name, same position among
    the functions of that name. None when it was not there."""
    style = classify.function_style(f.path)
    current = find_spans(now, style)
    span = next((s for s in current if s.start == f.line), None)
    if span is None:
        return None
    nth = [s for s in current if s.name == span.name].index(span)
    before = [s for s in find_spans(was, style) if s.name == span.name]
    return before[nth] if nth < len(before) else None
