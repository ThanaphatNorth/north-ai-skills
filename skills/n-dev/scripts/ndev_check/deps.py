"""Dependencies a manifest gained between the base ref and now. Pure: callers supply both texts.

An assistant can name a package from memory that does not exist, or one a squatter registered under the
name assistants tend to invent. The check runs offline and cannot ask the registry, so it makes every
addition visible instead: each one needs a reason in the report and a look at the registry and lockfile."""
from __future__ import annotations

import fnmatch
import json
import os
import re
from typing import Callable, List, Mapping, Optional, Sequence, Set, Tuple

from .literals import blank_strings
from .model import ChangedFile, Finding

Names = Set[str]
Extractor = Callable[[str], Names]

_SECTION = re.compile(r"^\s*\[+\s*([^\]]+?)\s*\]+")
_KEY = re.compile(r'^\s*["\']?([A-Za-z0-9_.-]+)["\']?\s*=')
_STR = re.compile(r'"([^"]*)"|\'([^\']*)\'')
_REQ_NAME = re.compile(r"\s*([A-Za-z0-9][A-Za-z0-9._-]*)")
_CARGO_TABLE = re.compile(r"^(?:target\..+\.)?(?:dev-|build-)?dependencies$")
_CARGO_SUBTABLE = re.compile(r"^(?:target\..+\.)?(?:dev-|build-)?dependencies\.([A-Za-z0-9_-]+)$")
_POETRY = re.compile(r"^tool\.poetry(?:\.group\.[^.]+)?\.(?:dev-)?dependencies$")
_GRADLE = re.compile(r"^\s*(?:implementation|api|compileOnly|runtimeOnly|testImplementation|testRuntimeOnly"
                     r"|androidTestImplementation|debugImplementation|kapt|ksp|annotationProcessor|classpath)"
                     r"\s*\(?\s*['\"]([^'\":]+:[^'\":]+)(?::[^'\"]*)?['\"]", re.M)


def _pep503(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def _requirement(spec: str) -> Optional[str]:
    m = _REQ_NAME.match(spec)
    return _pep503(m.group(1)) if m else None


def _strings(text: str) -> Names:
    return {n for n in (_requirement(a or b) for a, b in _STR.findall(text)) if n}


def _json_sections(*sections: str, skip: Callable[[str], bool] = lambda n: False) -> Extractor:
    def extract(text: str) -> Names:
        try:
            data = json.loads(text)
        except ValueError:
            return set()
        if not isinstance(data, dict):
            return set()
        return {n for s in sections if isinstance(data.get(s), dict) for n in data[s] if not skip(n)}
    return extract


def _regex(pattern: str) -> Extractor:
    compiled = re.compile(pattern, re.M)
    return lambda text: set(compiled.findall(text))


def _requirements(text: str) -> Names:
    rows = (row.split(" #", 1)[0].strip() for row in text.splitlines())
    return {n for n in (_requirement(r) for r in rows if r and not r.startswith(("#", "-"))) if n}


def _pyproject(text: str) -> Names:
    out: Names = set()
    section, in_array = "", False
    for row in text.splitlines():
        line = row.split("#", 1)[0]
        if in_array:
            out |= _strings(line)
            in_array = "]" not in blank_strings(line)
            continue
        header = _SECTION.match(line)
        if header:
            section = header.group(1)
            continue
        key = _KEY.match(line)
        if not key:
            continue
        if _POETRY.match(section):
            out |= {_pep503(key.group(1))} - {"python"}
        elif "[" in blank_strings(line) and ((section, key.group(1)) == ("project", "dependencies")
                                             or section in ("project.optional-dependencies", "dependency-groups")):
            start = blank_strings(line).index("[") + 1
            out |= _strings(line[start:])
            in_array = "]" not in blank_strings(line)[start:]
    return out


def _gomod(text: str) -> Names:
    out: Names = set()
    in_block = False
    for row in text.splitlines():
        line = row.split("//", 1)[0].strip()
        if in_block:
            in_block = not line.startswith(")")
            if in_block and line:
                out.add(line.split()[0])
        elif re.match(r"require\s*\($", line):
            in_block = True
        else:
            m = re.match(r"require\s+(\S+)\s+\S+", line)
            if m:
                out.add(m.group(1))
    return out


def _cargo(text: str) -> Names:
    out: Names = set()
    section = ""
    for row in text.splitlines():
        line = row.split("#", 1)[0]
        header = _SECTION.match(line)
        if header:
            section = header.group(1)
            sub = _CARGO_SUBTABLE.match(section)
            out |= {sub.group(1)} if sub else set()
        elif _CARGO_TABLE.match(section) and _KEY.match(line):
            out.add(_KEY.match(line).group(1))
    return out


def _pom(text: str) -> Names:
    out: Names = set()
    for block in re.findall(r"<dependency>(.*?)</dependency>", text, re.S):
        group = re.search(r"<groupId>\s*([^<\s]+)\s*</groupId>", block)
        artifact = re.search(r"<artifactId>\s*([^<\s]+)\s*</artifactId>", block)
        if group and artifact:
            out.add("%s:%s" % (group.group(1), artifact.group(1)))
    return out


def _pubspec(text: str) -> Names:
    out: Names = set()
    section = ""
    for row in text.splitlines():
        top = re.match(r"^([A-Za-z_]+):", row)
        if top:
            section = top.group(1)
            continue
        entry = re.match(r"^  ([A-Za-z0-9_]+):", row)
        if entry and section in ("dependencies", "dev_dependencies"):
            out.add(entry.group(1))
    return out


def _platform(name: str) -> bool:
    return name == "php" or name.startswith(("ext-", "lib-"))


_MANIFESTS: Sequence[Tuple[str, Extractor]] = (
    ("package.json", _json_sections("dependencies", "devDependencies", "peerDependencies", "optionalDependencies")),
    ("composer.json", _json_sections("require", "require-dev", skip=_platform)),
    ("requirements*.txt", _requirements),
    ("requirements*.in", _requirements),
    ("pyproject.toml", _pyproject),
    ("go.mod", _gomod),
    ("Cargo.toml", _cargo),
    ("Gemfile", _regex(r"""^\s*gem\s+['"]([^'"]+)['"]""")),
    ("Podfile", _regex(r"""^\s*pod\s+['"]([^'"]+)['"]""")),
    ("build.gradle", lambda t: set(_GRADLE.findall(t))),
    ("build.gradle.kts", lambda t: set(_GRADLE.findall(t))),
    ("pom.xml", _pom),
    ("*.csproj", _regex(r'<PackageReference\s+Include="([^"]+)"')),
    ("pubspec.yaml", _pubspec),
)


def _extractor(path: str) -> Optional[Extractor]:
    name = os.path.basename(path)
    return next((fn for glob, fn in _MANIFESTS if fnmatch.fnmatch(name, glob)), None)


def is_manifest(path: str) -> bool:
    return _extractor(path) is not None


def new_dependencies(path: str, before: Optional[str], after: str) -> List[str]:
    """Names declared in `after` and not in `before` (None = the manifest is new)."""
    extract = _extractor(path)
    if extract is None:
        return []
    return sorted(extract(after) - (extract(before) if before is not None else set()))


def check_deps(files: Sequence[ChangedFile], base_texts: Mapping[str, Optional[str]]) -> List[Finding]:
    out: List[Finding] = []
    for f in files:
        names = new_dependencies(f.path, base_texts.get(f.path), f.text)
        if names:
            out.append(Finding("new-dependency", f.path, _first_line(f, names), len(names), 0,
                               "adds %s; confirm each exists in its registry under this exact name, is maintained, "
                               "and nothing already installed does the job" % ", ".join(names)))
    return out


def _first_line(f: ChangedFile, names: Sequence[str]) -> int:
    rows = f.text.split("\n")
    wanted = [n.split(":")[-1].lower() for n in names]
    for n in sorted(f.added):
        if n <= len(rows) and any(w in rows[n - 1].lower() for w in wanted):
            return n
    return min(f.added, default=1)
