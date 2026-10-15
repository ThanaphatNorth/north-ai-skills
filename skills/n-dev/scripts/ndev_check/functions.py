"""Find function spans in source text. Heuristic and language-light: good enough to flag
long functions for review, not a parser. Pure functions only."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional

_CONTROL = {"if", "for", "while", "switch", "catch", "with", "return", "else", "do", "try",
            "using", "lock", "foreach", "elseif", "match", "when", "guard", "defer", "select"}

_BRACE_START = [
    re.compile(r"\bfunction\b\s*\*?\s*([\w$]*)\s*\("),                       # JS, PHP
    re.compile(r"\b(?:fun|func|fn)\b\s*(?:\([^)]*\)\s*)?(?:<[^>]*>\s*)?([\w$.]+)?\s*[(<]"),  # Kotlin, Go, Swift, Rust
    re.compile(r"(?:const|let|var|readonly)?\s*([\w$]+)\s*[:=][^=;]*=>\s*\{"),   # arrow with a body
    re.compile(r"^\s*(?:(?:public|private|protected|internal|static|async|override|abstract|final|"
               r"open|suspend|inline|virtual|sealed|synchronized|export|default|get|set|"
               r"[\w$<>\[\],.?]+)\s+)*([\w$]+)\s*\([^;]*\)\s*(?:[:\-]>?[^{;]*)?(?:throws [^{]*)?\{?\s*$"),  # methods
]
_PY_DEF = re.compile(r"^(\s*)(?:async\s+)?def\s+(\w+)")
_RB_DEF = re.compile(r"^(\s*)def\s+([\w.?!=]+)")
_STRINGS = re.compile(r"\"(?:\\.|[^\"\\])*\"|'(?:\\.|[^'\\])*'|`(?:\\.|[^`\\])*`")


@dataclass(frozen=True)
class Span:
    name: str
    start: int   # 1-based, inclusive
    end: int     # 1-based, inclusive

    @property
    def length(self) -> int:
        return self.end - self.start + 1


def find_spans(text: str, style: Optional[str]) -> List[Span]:
    if style == "brace":
        return _brace_spans(text.splitlines())
    if style == "indent":
        return _indent_spans(text.splitlines())
    if style == "end":
        return _end_spans(text.splitlines())
    return []


def _code_only(lines: List[str]) -> List[str]:
    """Strip string literals and comments so braces inside them are not counted."""
    out, in_block = [], False
    for line in lines:
        line = _STRINGS.sub('""', line)
        buf, i = [], 0
        while i < len(line):
            if in_block:
                end = line.find("*/", i)
                if end < 0:
                    i = len(line)
                    continue
                in_block, i = False, end + 2
            elif line.startswith("/*", i):
                in_block, i = True, i + 2
            elif line.startswith("//", i) or (line.startswith("#", i) and not line.strip().startswith("#[")):
                break
            else:
                buf.append(line[i])
                i += 1
        out.append("".join(buf))
    return out


def _signature_name(line: str) -> Optional[str]:
    for pattern in _BRACE_START:
        m = pattern.search(line)
        if m:
            name = (m.group(1) or "").split(".")[-1] or "anonymous"
            return None if name in _CONTROL else name
    return None


def _brace_spans(raw: List[str]) -> List[Span]:
    lines = _code_only(raw)
    spans: List[Span] = []
    for i, line in enumerate(lines):
        name = _signature_name(line)
        if name is None:
            continue
        open_at = _find_open_brace(lines, i)
        if open_at is None:
            continue
        end = _matching_close(lines, open_at)
        if end is not None:
            spans.append(Span(name, i + 1, end + 1))
    return spans


def _find_open_brace(lines: List[str], start: int, lookahead: int = 8) -> Optional[int]:
    """Index of the line holding the body's opening brace, or None for declarations."""
    for j in range(start, min(start + lookahead, len(lines))):
        segment = lines[j]
        brace, semi = segment.find("{"), segment.find(";")
        if brace >= 0 and (semi < 0 or brace < semi):
            return j
        if semi >= 0:
            return None
    return None


def _matching_close(lines: List[str], open_at: int) -> Optional[int]:
    depth = 0
    for j in range(open_at, len(lines)):
        for ch in lines[j]:
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return j
    return None


def _indent(line: str) -> int:
    return len(line) - len(line.lstrip(" \t"))


def _indent_spans(lines: List[str]) -> List[Span]:
    spans: List[Span] = []
    for i, line in enumerate(lines):
        m = _PY_DEF.match(line)
        if not m:
            continue
        base, last = len(m.group(1)), i
        for j in range(i + 1, len(lines)):
            if not lines[j].strip():
                continue
            if _indent(lines[j]) <= base and not lines[j].lstrip().startswith(")"):
                break
            last = j
        spans.append(Span(m.group(2), i + 1, last + 1))
    return spans


def _end_spans(lines: List[str]) -> List[Span]:
    spans: List[Span] = []
    for i, line in enumerate(lines):
        m = _RB_DEF.match(line)
        if not m or ";" in line or re.search(r"\)\s*=|\w\s*=\s*\S", line[m.end():]):
            continue  # one-line or endless method
        closer = re.compile(r"^%send\b" % re.escape(m.group(1)))
        for j in range(i + 1, len(lines)):
            if closer.match(lines[j]):
                spans.append(Span(m.group(2), i + 1, j + 1))
                break
    return spans
