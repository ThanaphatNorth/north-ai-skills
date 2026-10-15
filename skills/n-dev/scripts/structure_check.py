#!/usr/bin/env python3
"""Check a change against the n-dev structural rules, from git, for any language.

Reports, for code changed since the base ref (committed, staged, unstaged and untracked):
  wiring         pre-existing files changed by more than a wiring diff
  file-size      new or grown files over the line budget
  function-size  functions written or touched by the change that are over budget
  duplicate      added blocks that repeat code already in the repository

  python3 structure_check.py                     # base = merge-base with the default branch
  python3 structure_check.py --base main --max-func 40 --json

Exit status: 0 clean, 1 findings, 2 usage or git error. Needs Python 3.8+ and git.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # also works under python3 -I

from ndev_check import gitdiff, report  # noqa: E402
from ndev_check.model import Budgets  # noqa: E402
from ndev_check.runner import run  # noqa: E402


def parse_args(argv):
    d = Budgets()
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--repo", default=".", help="any path inside the repository (default: cwd)")
    ap.add_argument("--base", help="ref to compare against (default: merge-base with the default branch)")
    ap.add_argument("--max-file", type=int, default=d.max_file, help="source file lines (%(default)s)")
    ap.add_argument("--max-test-file", type=int, default=d.max_test_file, help="test file lines (%(default)s)")
    ap.add_argument("--max-func", type=int, default=d.max_func, help="function lines (%(default)s)")
    ap.add_argument("--max-wiring", type=int, default=d.max_wiring,
                    help="changed lines allowed in a pre-existing file (%(default)s)")
    ap.add_argument("--dup-lines", type=int, default=d.dup_lines,
                    help="meaningful lines that make a copied block (%(default)s)")
    ap.add_argument("--exclude", action="append", default=[], metavar="GLOB",
                    help="path glob to ignore; repeatable")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    return ap.parse_args(argv)


def main(argv=None):
    a = parse_args(argv)
    budgets = Budgets(a.max_file, a.max_test_file, a.max_func, a.max_wiring, a.dup_lines)
    try:
        root = gitdiff.repo_root(a.repo)
        base = gitdiff.resolve_base(root, a.base)
        findings = run(root, base, budgets, a.exclude)
    except gitdiff.GitError as e:
        print("error: %s" % e, file=sys.stderr)
        return 2
    render = report.as_json if a.json else report.as_text
    print(render(findings, base, budgets))
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
