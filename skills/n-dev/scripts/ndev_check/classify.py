"""Path classification: which files are code, tests, or noise. Pure functions on paths."""
from __future__ import annotations

import fnmatch
import os
import re
from typing import Iterable, Optional

BRACE_LANGS = {
    ".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx", ".mts", ".cts", ".vue", ".svelte",
    ".java", ".kt", ".kts", ".scala", ".groovy", ".swift", ".go", ".rs", ".php",
    ".cs", ".dart", ".c", ".h", ".cc", ".cpp", ".hpp", ".m", ".mm",
}
INDENT_LANGS = {".py"}
END_LANGS = {".rb"}
CODE_EXTS = BRACE_LANGS | INDENT_LANGS | END_LANGS

NOISE_GLOBS = (
    "*.lock", "*-lock.json", "*.lock.json", "pnpm-lock.yaml", "go.sum", "*.min.*", "*.map",
    "*.snap", "*.pb.go", "*_pb2.py", "*.g.dart", "*.freezed.dart", "*.generated.*",
)
NOISE_DIRS = ("node_modules/", "vendor/", "dist/", "build/", "out/", ".next/", "coverage/",
              "Pods/", "generated/", "__generated__/", "migrations/")

_TEST_NAME = re.compile(
    r"(^|/)(test_[^/]+\.py|[^/]+_test\.(py|go|rb|dart)|[^/]+\.(test|spec)\.[^/]+|"
    r"[^/]+(Test|Tests|Spec)\.(java|kt|kts|swift|cs|scala|php))$"
)
_TEST_DIR = re.compile(r"(^|/)(tests?|__tests__|spec|specs|androidTest|testFixtures)/")


def extension(path: str) -> str:
    return os.path.splitext(path)[1].lower()


def is_code(path: str) -> bool:
    return extension(path) in CODE_EXTS


def is_test(path: str) -> bool:
    return bool(_TEST_NAME.search(path) or _TEST_DIR.search(path))


def is_noise(path: str, extra_globs: Iterable[str] = ()) -> bool:
    name = os.path.basename(path)
    if any(fnmatch.fnmatch(name, g) for g in NOISE_GLOBS):
        return True
    if any(fnmatch.fnmatch(path, g) for g in extra_globs):
        return True
    padded = "/" + path
    return any("/" + d in padded for d in NOISE_DIRS)


def function_style(path: str) -> Optional[str]:
    """How function bodies are delimited in this file's language, or None if unsupported."""
    ext = extension(path)
    if ext in BRACE_LANGS:
        return "brace"
    if ext in INDENT_LANGS:
        return "indent"
    if ext in END_LANGS:
        return "end"
    return None
