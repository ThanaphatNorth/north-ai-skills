#!/usr/bin/env python3
"""Validate a skill folder: frontmatter, referenced files, reference-file shape,
cross-links, and (with --urls) that every cited URL still answers.

  python3 tools/validate_skill.py skills/design-atlas
  python3 tools/validate_skill.py skills/design-atlas --urls --report .logs/urls.tsv
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from typing import Callable, Dict, List, NamedTuple, Optional, Sequence, Set, Tuple, Union

MIN_LINES, MAX_LINES = 120, 750  # catalogs (styles, recipes) read section by section
BLOCKED = (401, 403, 429, 999)  # the site answers, but not to a script
NO_ANSWER = ("timeout", "curl-fail", 0)

Status = Union[int, str]  # an HTTP code, or the name of what went wrong
Fetched = Tuple[str, Status]
Fetch = Callable[[str], Fetched]
Cited = Dict[str, Set[str]]  # url -> the reference files that cite it


class Findings(NamedTuple):
    """Errors fail the run; warnings are printed and counted."""
    errors: List[str]
    warnings: List[str]


class SkillReport(NamedTuple):
    """What the static checks found in one skill folder."""
    findings: Findings
    refs: List[str]
    urls: Cited


class UrlReport(NamedTuple):
    """Fetched statuses (unreachable ones rewritten as `unreachable:<status>`), sorted into dead and warned."""
    results: List[Fetched]
    dead: List[str]
    warnings: List[str]


def frontmatter(text: str) -> Optional[Dict[str, str]]:
    """The `key: value` pairs of the leading `---` block, or None when the text has no such block."""
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None
    out = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip()
    return out


def extract_urls(text: str) -> List[str]:
    """URLs in prose and markdown links; keeps balanced parentheses such as
    gsap.matchMedia() or glassEffect(_:in:), drops code placeholders."""
    out = []
    for m in re.finditer(r"https?://[^\s<>`\"'|\]]+", text):
        if m.start() > 0 and text[m.start() - 1] == "`":
            continue  # a URL in a code span is an example or endpoint, not a citation
        u = m.group(0).rstrip(".,;:*")
        while u.endswith(")") and u.count("(") < u.count(")"):
            u = u[:-1].rstrip(".,;:*")
        if "example.com" in u or "<" in u or "{" in u:
            continue
        out.append(u)
    return out


def curl_status(url: str) -> Status:
    """The HTTP code curl ends on after redirects, or `curl-fail` / the exception's name."""
    try:
        r = subprocess.run(["curl", "-s", "-o", "/dev/null", "-L", "--max-time", "20", "-A",
                            "Mozilla/5.0 (Macintosh) AppleWebKit/537.36 Chrome/126.0 Safari/537.36",
                            "-w", "%{http_code}", url], capture_output=True, text=True, timeout=30)
        code = int(r.stdout.strip() or 0)
        return code if code else "curl-fail"
    except Exception as e:
        return type(e).__name__


def check_url(url: str, primary: Optional[Fetch] = None,
              retry: Optional[Callable[[str], Status]] = None) -> Fetched:
    """`(url, status)` from `primary` (urllib when omitted); an error answer is asked again
    through `retry` (curl when omitted) and the lower HTTP code wins."""
    _, status = (primary or _urllib_status)(url)
    if not isinstance(status, int) or status >= 400:  # retry with curl: old TLS stacks, odd redirects
        again = (retry or curl_status)(url)
        if isinstance(again, int) and (not isinstance(status, int) or again < status):
            status = again
    return url, status


def _urllib_status(url: str) -> Fetched:
    req = urllib.request.Request(url, method="GET", headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,*/*;q=0.8"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return url, int(r.status)
    except urllib.error.HTTPError as e:
        return url, e.code
    except Exception as e:  # DNS, TLS, timeout
        return url, type(e).__name__


def check_frontmatter(skill_md: str, folder: str) -> List[str]:
    """Errors in SKILL.md's frontmatter: no block, a name that is not the folder's, a description empty or too long."""
    fm = frontmatter(skill_md)
    if not fm:
        return ["SKILL.md: missing YAML frontmatter"]
    errors = []
    if fm.get("name") != folder:
        errors.append("SKILL.md: name %r != folder %r" % (fm.get("name"), folder))
    desc = fm.get("description", "")
    if not desc:
        errors.append("SKILL.md: empty description")
    elif len(desc) > 1024:
        errors.append("SKILL.md: description is %d chars (> 1024)" % len(desc))
    return errors


def check_mentioned_paths(skill_md: str, skill_dir: str) -> List[str]:
    """One error per references/, templates/ or scripts/ path SKILL.md mentions that is not in the folder."""
    mentioned = sorted(set(re.findall(r"`((?:references|templates|scripts)/[\w./-]+)", skill_md)))
    return ["SKILL.md points at missing %s" % rel for rel in mentioned
            if not os.path.exists(os.path.join(skill_dir, rel))]


def reference_names(skill_dir: str) -> List[str]:
    """Sorted names of the markdown files in the skill's references/ folder; empty without the folder."""
    refs_dir = os.path.join(skill_dir, "references")
    if not os.path.isdir(refs_dir):
        return []
    return sorted(f for f in os.listdir(refs_dir) if f.endswith(".md"))


def check_routing(refs: Sequence[str], skill_md: str) -> List[str]:
    """One warning per reference file that SKILL.md never names."""
    return ["references/%s is not routed from SKILL.md" % f for f in refs if "references/" + f not in skill_md]


def check_reference(name: str, text: str, refs: Sequence[str]) -> Findings:
    """Shape findings for one reference file: title, Read-when line, Sources section, length, cross-links."""
    errors, warnings = [], []
    lines = text.count("\n") + 1
    if not text.startswith("# "):
        errors.append("%s: must start with '# Title'" % name)
    if "> Read when:" not in text[:600]:
        errors.append("%s: missing '> Read when:' line near the top" % name)
    if not re.search(r"^## Sources", text, re.M):
        errors.append("%s: missing '## Sources' section" % name)
    if not MIN_LINES <= lines <= MAX_LINES:
        warnings.append("%s: %d lines (expected %d-%d)" % (name, lines, MIN_LINES, MAX_LINES))
    for link in sorted(set(re.findall(r"`([\w-]+\.md)`", text))):
        if link not in refs and link not in ("SKILL.md",):
            warnings.append("%s: cross-links missing sibling %s" % (name, link))
    return Findings(errors, warnings)


def check_skill(skill_dir: str) -> SkillReport:
    """Every static finding for a skill folder, with its reference names and the URLs they cite."""
    skill_md = _read(os.path.join(skill_dir, "SKILL.md"))
    refs = reference_names(skill_dir)
    errors = check_frontmatter(skill_md, os.path.basename(skill_dir)) + check_mentioned_paths(skill_md, skill_dir)
    warnings = check_routing(refs, skill_md)
    urls: Cited = {}
    for name in refs:
        text = _read(os.path.join(skill_dir, "references", name))
        found = check_reference(name, text, refs)
        errors.extend(found.errors)
        warnings.extend(found.warnings)
        for u in extract_urls(text):
            urls.setdefault(u, set()).add(name)
    return SkillReport(Findings(errors, warnings), refs, urls)


def is_ok(status: Status) -> bool:
    """True when the status is an HTTP code below 400."""
    return isinstance(status, int) and status < 400


def classify_urls(results: Sequence[Fetched], cited: Cited, root_fails: Callable[[str], bool]) -> UrlReport:
    """Sorts fetched statuses into dead URLs and blocked or unreachable warnings. `root_fails(url)`
    says whether the URL's host root fails too; it is asked only for a 404."""
    final, dead, warnings = list(results), [], []
    for i, (u, status) in enumerate(results):
        if is_ok(status):
            continue
        where = "%s %s (in %s)" % (status, u, ", ".join(sorted(cited[u])))
        if status in BLOCKED:
            warnings.append("blocked " + where)
        elif status in NO_ANSWER or (status == 404 and root_fails(u)):
            warnings.append("unreachable from here (site blocks bots or times out) " + where)
            final[i] = (u, "unreachable:%s" % status)
        else:
            dead.append(where)
    return UrlReport(final, dead, warnings)


def host_root_probe(fetch: Fetch) -> Callable[[str], bool]:
    """A function saying whether a URL's host root fails through `fetch`; each host is fetched once."""
    cache: Dict[str, bool] = {}

    def root_fails(url: str) -> bool:
        m = re.match(r"https?://[^/]+", url)
        root = (m.group(0) if m else url) + "/"
        if root not in cache:
            cache[root] = not is_ok(fetch(root)[1])
        return cache[root]

    return root_fails


def check_urls(cited: Cited, fetch: Fetch) -> UrlReport:
    """Fetches every cited URL through `fetch`, 16 at a time, and classifies the answers."""
    with cf.ThreadPoolExecutor(16) as ex:
        results = list(ex.map(fetch, sorted(cited)))
    return classify_urls(results, cited, host_root_probe(fetch))


def url_summary(report: UrlReport) -> str:
    """The `urls: N ok, N dead, N blocked/unreachable from here` line."""
    ok = sum(1 for _, s in report.results if is_ok(s))
    return "urls: %d ok, %d dead, %d blocked/unreachable from here" % (
        ok, len(report.dead), len(report.results) - len(report.dead) - ok)


def write_report(path: str, results: Sequence[Fetched], cited: Cited) -> None:
    """Writes one `status<TAB>url<TAB>files` row per URL to `path`, creating its folder."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w") as fh:
        for u, status in results:
            fh.write("%s\t%s\t%s\n" % (status, u, ",".join(sorted(cited[u]))))


def result_lines(errors: Sequence[str], warnings: Sequence[str]) -> List[str]:
    """The WARN lines, the ERROR lines and the closing RESULT line."""
    return (["WARN  " + w for w in warnings] + ["ERROR " + e for e in errors] + [
        "RESULT: %s (%d errors, %d warnings)" % ("FAIL" if errors else "PASS", len(errors), len(warnings))])


def run(argv: Sequence[str], fetch: Optional[Fetch] = None) -> int:
    """Validates the skill folder named in `argv`, prints the report and returns the exit code.
    `fetch` replaces `check_url` for `--urls`."""
    ap = argparse.ArgumentParser()
    ap.add_argument("skill_dir")
    ap.add_argument("--urls", action="store_true", help="also fetch every URL cited in references/")
    ap.add_argument("--report", help="write URL results as TSV here")
    a = ap.parse_args(argv)
    report = check_skill(a.skill_dir.rstrip("/"))
    errors, warnings = list(report.findings.errors), list(report.findings.warnings)
    print("references: %d files, %d distinct URLs" % (len(report.refs), len(report.urls)))
    if a.urls and report.urls:
        checked = check_urls(report.urls, fetch or check_url)
        if a.report:
            write_report(a.report, checked.results, report.urls)
        print(url_summary(checked))
        warnings.extend(checked.warnings)
        errors.extend("dead url: " + d for d in checked.dead)
    for line in result_lines(errors, warnings):
        print(line)
    return 1 if errors else 0


def main() -> None:
    """Command-line entry: runs on `sys.argv` and exits 1 when there are errors."""
    sys.exit(run(sys.argv[1:]))


def _read(path: str) -> str:
    with open(path, encoding="utf-8") as fh:
        return fh.read()


if __name__ == "__main__":
    main()
