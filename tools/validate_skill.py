#!/usr/bin/env python3
"""Validate a skill folder: frontmatter, referenced files, reference-file shape,
cross-links, and (with --urls) that every cited URL still answers.

  python3 tools/validate_skill.py skills/design-atlas
  python3 tools/validate_skill.py skills/design-atlas --urls --report .logs/urls.tsv
"""
import argparse
import concurrent.futures as cf
import os
import re
import sys
import subprocess
import urllib.error
import urllib.request

MIN_LINES, MAX_LINES = 120, 750  # catalogs (styles, recipes) read section by section


def frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None
    out = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip()
    return out


def extract_urls(text):
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


def curl_status(url):
    try:
        r = subprocess.run(["curl", "-s", "-o", "/dev/null", "-L", "--max-time", "20", "-A",
                            "Mozilla/5.0 (Macintosh) AppleWebKit/537.36 Chrome/126.0 Safari/537.36",
                            "-w", "%{http_code}", url], capture_output=True, text=True, timeout=30)
        code = int(r.stdout.strip() or 0)
        return code if code else "curl-fail"
    except Exception as e:
        return type(e).__name__


def check_url(url):
    _, status = _urllib_status(url)
    if not isinstance(status, int) or status >= 400:  # retry with curl: old TLS stacks, odd redirects
        retry = curl_status(url)
        if isinstance(retry, int) and (not isinstance(status, int) or retry < status):
            status = retry
    return url, status


def _urllib_status(url):
    req = urllib.request.Request(url, method="GET", headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,*/*;q=0.8"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return url, r.status
    except urllib.error.HTTPError as e:
        return url, e.code
    except Exception as e:  # DNS, TLS, timeout
        return url, type(e).__name__


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("skill_dir")
    ap.add_argument("--urls", action="store_true", help="also fetch every URL cited in references/")
    ap.add_argument("--report", help="write URL results as TSV here")
    a = ap.parse_args()
    d = a.skill_dir.rstrip("/")
    errors, warnings = [], []

    skill_md = open(os.path.join(d, "SKILL.md"), encoding="utf-8").read()
    fm = frontmatter(skill_md)
    if not fm:
        errors.append("SKILL.md: missing YAML frontmatter")
    else:
        if fm.get("name") != os.path.basename(d):
            errors.append("SKILL.md: name %r != folder %r" % (fm.get("name"), os.path.basename(d)))
        desc = fm.get("description", "")
        if not desc:
            errors.append("SKILL.md: empty description")
        elif len(desc) > 1024:
            errors.append("SKILL.md: description is %d chars (> 1024)" % len(desc))

    # every path SKILL.md mentions must exist
    for rel in sorted(set(re.findall(r"`((?:references|templates|scripts)/[\w./-]+)", skill_md))):
        if not os.path.exists(os.path.join(d, rel)):
            errors.append("SKILL.md points at missing %s" % rel)

    refs_dir = os.path.join(d, "references")
    refs = sorted(f for f in os.listdir(refs_dir) if f.endswith(".md")) if os.path.isdir(refs_dir) else []
    for f in refs:
        if "references/" + f not in skill_md:
            warnings.append("references/%s is not routed from SKILL.md" % f)
    urls = {}
    for f in refs:
        text = open(os.path.join(refs_dir, f), encoding="utf-8").read()
        lines = text.count("\n") + 1
        if not text.startswith("# "):
            errors.append("%s: must start with '# Title'" % f)
        if "> Read when:" not in text[:600]:
            errors.append("%s: missing '> Read when:' line near the top" % f)
        if not re.search(r"^## Sources", text, re.M):
            errors.append("%s: missing '## Sources' section" % f)
        if not MIN_LINES <= lines <= MAX_LINES:
            warnings.append("%s: %d lines (expected %d-%d)" % (f, lines, MIN_LINES, MAX_LINES))
        for link in set(re.findall(r"`([\w-]+\.md)`", text)):
            if link not in refs and link not in ("SKILL.md",):
                warnings.append("%s: cross-links missing sibling %s" % (f, link))
        for u in extract_urls(text):
            urls.setdefault(u, set()).add(f)

    print("references: %d files, %d distinct URLs" % (len(refs), len(urls)))
    if a.urls and urls:
        bad = []
        with cf.ThreadPoolExecutor(16) as ex:
            results = list(ex.map(check_url, sorted(urls)))
        root_cache = {}

        def host_root_fails(u):
            root = re.match(r"https?://[^/]+", u).group(0) + "/"
            if root not in root_cache:
                st = check_url(root)[1]
                root_cache[root] = not (isinstance(st, int) and st < 400)
            return root_cache[root]

        for i, (u, status) in enumerate(results):
            ok = isinstance(status, int) and status < 400
            if ok:
                continue
            where = "%s %s (in %s)" % (status, u, ", ".join(sorted(urls[u])))
            if status in (401, 403, 429, 999):
                warnings.append("blocked " + where)
            elif status in ("timeout", "curl-fail", 0) or (status == 404 and host_root_fails(u)):
                warnings.append("unreachable from here (site blocks bots or times out) " + where)
                results[i] = (u, "unreachable:%s" % status)
            else:
                bad.append(where)
        if a.report:
            os.makedirs(os.path.dirname(a.report) or ".", exist_ok=True)
            with open(a.report, "w") as fh:
                for u, status in results:
                    fh.write("%s\t%s\t%s\n" % (status, u, ",".join(sorted(urls[u]))))
        print("urls: %d ok, %d dead, %d blocked/unreachable from here" % (
            sum(1 for _, s in results if isinstance(s, int) and s < 400), len(bad),
            len(results) - len(bad) - sum(1 for _, s in results if isinstance(s, int) and s < 400)))
        errors.extend("dead url: " + b for b in bad)

    for w in warnings:
        print("WARN  " + w)
    for e in errors:
        print("ERROR " + e)
    print("RESULT: %s (%d errors, %d warnings)" % ("FAIL" if errors else "PASS", len(errors), len(warnings)))
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
