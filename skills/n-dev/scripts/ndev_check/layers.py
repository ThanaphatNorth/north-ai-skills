"""Judge the imports a change added against the repo's declared layers (`[layers.*]` in .ndev.toml). Pure.

A file belongs to the layer whose matching `paths` glob is the most specific (the longest part before the first
wildcard; ties go to the layer declared first). An import's target layer is found by:
1. relative specifiers (`./x`, `../x`, Python `.x` / `..x`) resolved against the importing file, then matched
   against each layer's `paths`;
2. otherwise the longest declared `imports` prefix (alias, package, namespace) the specifier starts with;
3. otherwise the specifier read as a path (`app.infra.db`, `App\\Infra`, `crate::infra` -> `app/infra/db`, ...)
   matched against `paths`.
Only imports on lines the change added count, and an import whose specifier the file already had at the base ref
is existing debt rather than a finding. Test files are exempt."""
from __future__ import annotations

import fnmatch
import posixpath
import re
from typing import Iterable, List, Mapping, Optional, Sequence, Tuple

from . import classify
from .imports import find_imports
from .model import ChangedFile, Finding, Layer

_BOUNDARY = "/.\\:"


def check_layers(files: Sequence[ChangedFile], layers: Sequence[Layer],
                 base_texts: Optional[Mapping[str, Optional[str]]] = None) -> List[Finding]:
    """`base_texts` maps a pre-existing file to its text at the base ref; its imports are not new."""
    if not layers:
        return []
    out: List[Finding] = []
    for f in files:
        own = None if classify.is_test(f.path) else _layer_of(f.path, layers)
        if own is None:
            continue
        for line, spec in _added_imports(f, (base_texts or {}).get(f.path)):
            target = _target(f.path, spec, layers)
            if target is None or target.name == own.name or target.name in own.may_import:
                continue
            allowed = ", ".join(own.may_import) or "nothing"
            out.append(Finding("layer", f.path, line, 0, 0, "imports '%s' from layer %s; %s may import: %s"
                               % (spec, target.name, own.name, allowed), related=target.name))
    return out


def _added_imports(f: ChangedFile, base_text: Optional[str]) -> List[Tuple[int, str]]:
    """(line, specifier) of the imports this change added: on an added line, and not a specifier the file
    already imported at the base ref."""
    had = {spec for _, spec in find_imports(f.path, base_text or "")}
    return [(line, spec) for line, spec in find_imports(f.path, f.text) if line in f.added and spec not in had]


def _layer_of(path: str, layers: Sequence[Layer], fold_case: bool = False) -> Optional[Layer]:
    """The layer whose most specific `paths` glob matches the path, or None when no layer claims it."""
    if fold_case:
        path = path.lower()
    return _most_specific((_fixed_prefix(g), layer) for layer in layers for g in layer.paths
                          if _matches(path, g.lower() if fold_case else g))


def _most_specific(scored: Iterable[Tuple[int, Layer]]) -> Optional[Layer]:
    """The layer with the highest score; the first one wins a tie."""
    best: Optional[Tuple[int, Layer]] = None
    for score, layer in scored:
        if best is None or score > best[0]:
            best = (score, layer)
    return best[1] if best else None


def _fixed_prefix(glob: str) -> int:
    """How specific a glob is: the number of characters before its first wildcard."""
    return len(re.split(r"[*?\[]", glob, maxsplit=1)[0])


def _matches(path: str, glob: str) -> bool:
    """`src/domain` (a directory or an index import) also belongs to `src/domain/**`."""
    return fnmatch.fnmatchcase(path, glob) or fnmatch.fnmatchcase(path + "/", glob)


def _target(path: str, spec: str, layers: Sequence[Layer]) -> Optional[Layer]:
    """The layer an import specifier refers to, or None when it refers to no declared layer."""
    resolved = _resolve_relative(path, spec)
    if resolved is not None:
        return _layer_of(resolved, layers)
    by_prefix = _most_specific((len(p), layer) for layer in layers for p in layer.imports if _starts_with(spec, p))
    # read as a path; namespaces and packages are often capitalised where folders are not (App\\Models -> app/Models)
    return by_prefix or _layer_of(re.sub(r"::|[.\\]", "/", spec), layers, fold_case=True)


def _starts_with(spec: str, prefix: str) -> bool:
    """True when the specifier is the prefix, or continues it at a separator (`@/infra` does not claim
    `@/infrared`)."""
    if spec == prefix:
        return True
    return spec.startswith(prefix) and (prefix[-1] in _BOUNDARY or spec[len(prefix)] in _BOUNDARY)


def _resolve_relative(path: str, spec: str) -> Optional[str]:
    """The repo path a relative specifier points at; None when the specifier is not relative."""
    here = posixpath.dirname(path)
    if spec in (".", "..") or spec.startswith(("./", "../")):
        return posixpath.normpath(posixpath.join(here, spec))
    if classify.extension(path) == ".py" and spec.startswith("."):
        dots = len(spec) - len(spec.lstrip("."))
        for _ in range(dots - 1):
            here = posixpath.dirname(here)
        rest = spec[dots:].replace(".", "/")
        return posixpath.normpath(posixpath.join(here, rest)) if rest else (here or ".")
    return None
