#!/usr/bin/env python3
"""Repo-level consistency: the facts this repo repeats in more than one file still agree.

  python3 tools/check_repo.py [--repo PATH]

Prints one line per finding, then `RESULT: PASS|FAIL (N errors, M warnings)`; exits 1 on errors.
The checks live in the repo_check package beside this file, one module per concern.
"""
from __future__ import annotations

import argparse
import os
import sys
from typing import Sequence

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # also works under python3 -I

from repo_check.report import report_lines  # noqa: E402
from repo_check.runner import run_checks  # noqa: E402


def default_repo() -> str:
    """The repo this script lives in: the folder above tools/."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run(argv: Sequence[str]) -> int:
    """Checks the repo named by `--repo` in `argv` (this repo when omitted), prints the report and
    returns the exit code: 1 when there are errors."""
    ap = argparse.ArgumentParser(description="Repo-level consistency checks.")
    ap.add_argument("--repo", default=default_repo(), help="repo root to check (default: this repo)")
    findings = run_checks(ap.parse_args(argv).repo)
    for line in report_lines(findings):
        print(line)
    return 1 if any(f.level == "ERROR" for f in findings) else 0


def main() -> None:
    """Command-line entry: runs on `sys.argv` and exits with the result."""
    sys.exit(run(sys.argv[1:]))


if __name__ == "__main__":
    main()
