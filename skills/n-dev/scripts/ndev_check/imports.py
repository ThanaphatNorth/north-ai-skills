"""Find import specifiers, with their line numbers, in source text. Pure; one small scanner per language family.

Comments and strings are not parsed, so an import-looking line inside a block comment counts. That is good
enough for judging a change: the finding shows the line, and a reader can dismiss it in a second."""
from __future__ import annotations

import re
from typing import Callable, Dict, List, Pattern, Sequence, Tuple

from .classify import extension

Imports = List[Tuple[int, str]]
_Q = r"""["']([^"'\n]+)["']"""


def _regex_scanner(patterns: Sequence[Pattern[str]]) -> Callable[[str], Imports]:
    """Every match of every pattern, in line order, then position order within a line."""
    def scan(text: str) -> Imports:
        out: Imports = []
        for n, row in enumerate(text.split("\n"), start=1):
            hits = sorted((m.start(), m.group(1)) for p in patterns for m in p.finditer(row))
            out.extend((n, spec) for _, spec in hits)
        return out
    return scan


def _python(text: str) -> Imports:
    out: Imports = []
    for n, row in enumerate(text.split("\n"), start=1):
        m = re.match(r"\s*from\s+(\.+[\w.]*|[\w.]+)\s+import\s+\(?\s*([\w\s,]*)", row)
        if m:
            out.extend((n, spec) for spec in _from_import(m.group(1), m.group(2)))
            continue
        m = re.match(r"\s*import\s+([\w.]+(?:\s+as\s+\w+)?(?:\s*,\s*[\w.]+(?:\s+as\s+\w+)?)*)", row)
        if m:
            out.extend((n, part.split()[0]) for part in m.group(1).split(","))
    return out


def _from_import(module: str, names: str) -> List[str]:
    """`from app import infra` imports app.infra (a module, or a name inside app: either way at least as specific as
    app); `from . import x` imports .x. Names on later lines of a parenthesised list fall back to the module."""
    picked = [part.split()[0] for part in names.split(",") if part.split()]
    if not picked:
        return [module]
    joiner = "" if module.strip(".") == "" else "."
    return [module + joiner + name for name in picked]


_GO_SPEC = re.compile(r'\s*(?:[\w.]+\s+)?"([^"]+)"')


def _go(text: str) -> Imports:
    out: Imports = []
    in_block = False
    for n, row in enumerate(text.split("\n"), start=1):
        if in_block:
            if row.strip().startswith(")"):
                in_block = False
                continue
            m = _GO_SPEC.match(row)
            if m:
                out.append((n, m.group(1)))
        elif re.match(r"\s*import\s*\(\s*(//.*)?$", row):
            in_block = True
        else:
            m = re.match(r'\s*import\s+(?:[\w.]+\s+)?"([^"]+)"', row)
            if m:
                out.append((n, m.group(1)))
    return out


def _rust(text: str) -> Imports:
    scan = _regex_scanner([re.compile(r"^\s*(?:pub(?:\([^)]*\))?\s+)?use\s+([\w:]+)")])
    return [(n, spec.rstrip(":")) for n, spec in scan(text)]


_JS = _regex_scanner([
    re.compile(r"^\s*(?:import|export)\b.*?\bfrom\s+" + _Q),
    re.compile(r"^\s*}\s*from\s+" + _Q),
    re.compile(r"^\s*import\s+" + _Q),
    re.compile(r"\brequire\(\s*" + _Q + r"\s*\)"),
    re.compile(r"\bimport\(\s*" + _Q + r"\s*\)"),
])
_JVM = _regex_scanner([re.compile(r"^\s*import\s+(?:static\s+)?([\w.]+(?:\.\*)?)")])
_PHP = _regex_scanner([re.compile(r"^\s*use\s+(?:function\s+|const\s+)?\\?([\w\\]+)")])
_CSHARP = _regex_scanner([re.compile(r"^\s*(?:global\s+)?using\s+(?:static\s+)?(?:\w+\s*=\s*)?([\w.]+)\s*;")])
_RUBY = _regex_scanner([re.compile(r"^\s*require(?:_relative)?\s*\(?\s*" + _Q)])
_DART = _regex_scanner([re.compile(r"^\s*(?:import|export)\s+" + _Q)])
_SWIFT = _regex_scanner([re.compile(r"^\s*(?:@\w+\s+)?import\s+(?:(?:struct|class|enum|protocol|func|var|let)\s+)?([\w.]+)")])
_C = _regex_scanner([re.compile(r'^\s*#\s*(?:include|import)\s*[<"]([^>"]+)[>"]')])

_BY_EXTENSION: Dict[str, Callable[[str], Imports]] = {
    **{e: _JS for e in (".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx", ".mts", ".cts", ".vue", ".svelte")},
    **{e: _JVM for e in (".java", ".kt", ".kts", ".scala", ".groovy")},
    **{e: _C for e in (".c", ".h", ".cc", ".cpp", ".hpp", ".m", ".mm")},
    ".py": _python, ".go": _go, ".rs": _rust, ".php": _PHP, ".cs": _CSHARP, ".rb": _RUBY,
    ".dart": _DART, ".swift": _SWIFT,
}


def find_imports(path: str, text: str) -> Imports:
    """[(1-based line, specifier as written)] for a supported language; [] otherwise."""
    scan = _BY_EXTENSION.get(extension(path))
    return scan(text) if scan else []
