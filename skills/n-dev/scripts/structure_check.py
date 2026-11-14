#!/usr/bin/env python3
"""Check a change against the n-dev structural rules, from git, for any language.

Reports, for code changed since the base ref (committed, staged, unstaged and untracked):
  wiring         pre-existing files changed by more than a wiring diff
  file-size      new or grown files over the line budget
  function-size  functions written or touched by the change that are over budget
  long-line      added lines wider than the width budget (one finding per file)
  duplicate      added blocks that repeat code already in the repository
  layer          added imports that break a layer rule declared in .ndev.toml
  test-weakened  removed assertions, skip/focus markers, deleted tests, rewritten snapshots, lower coverage gates
  new-dependency packages a manifest gained (confirm each exists and is needed)

A file or function that was already over budget at the base ref is listed apart as existing debt:
informational, it does not fail the check (growth of it still trips the wiring budget).

  python3 structure_check.py                    # base = merge-base with the default branch
  python3 structure_check.py --base main --max-func 40 --json
  python3 structure_check.py --all              # audit the whole repository (debt map)

Budgets, excludes and layers come from .ndev.toml at the repo root when present; flags override it.

Exit status: 0 clean, 1 findings, 2 when the check could not run (usage, git, config, the OS): the reason
is one `error:` line on stderr and stdout stays empty. Needs Python 3.8+ and git.
"""
from __future__ import annotations

import argparse
import io
import os
import sys
import traceback
from typing import Optional, Sequence, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # also works under python3 -I

from ndev_check import config, gitdiff, report  # noqa: E402
from ndev_check.model import Budgets, printable  # noqa: E402
from ndev_check.runner import run  # noqa: E402


def parse_args(argv: Optional[Sequence[str]]) -> argparse.Namespace:
    """The flags as given. A budget flag left out is None, so the config file's value can apply."""
    d = Budgets()
    ap = argparse.ArgumentParser(description=(__doc__ or "").split("\n\n")[0])  # no docstring under -OO
    ap.add_argument("--repo", default=".", help="any directory inside the repository (default: cwd)")
    ap.add_argument("--base", help="ref to compare against (default: merge-base with the default branch)")
    ap.add_argument("--all", action="store_true", help="audit the whole repository instead of a change")
    cfg = ap.add_mutually_exclusive_group()
    cfg.add_argument("--config", metavar="PATH",
                     help="config file, relative to the current directory (default: .ndev.toml at the repo root)")
    cfg.add_argument("--no-config", action="store_true", help="ignore .ndev.toml")
    for flag, what in (("max-file", "source file lines"), ("max-test-file", "test file lines"),
                       ("max-func", "function lines"), ("max-wiring", "changed lines allowed in a pre-existing file"),
                       ("dup-lines", "meaningful lines that make a copied block"),
                       ("max-line", "characters per added line, 0 = off")):
        default = getattr(d, flag.replace("-", "_"))
        ap.add_argument("--" + flag, type=int, help="%s (%d, or the config's value)" % (what, default))
    ap.add_argument("--exclude", action="append", default=[], metavar="GLOB",
                    help="path glob to ignore; repeatable")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    return ap.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    """The exit status: 0 clean, 1 findings, 2 when the check could not run (one `error:` line says why)."""
    a = parse_args(argv)
    if a.all and a.base:
        return _error("--all audits the whole repository and takes no --base")
    try:
        status, text = _check(a)
        _emit(text)
    except (gitdiff.GitError, config.ConfigError, OSError) as e:
        return _error(str(e))
    except Exception as e:  # a bug in the check: keep its traceback, but exit 1 would read as "findings"
        traceback.print_exc()
        return _error("internal error (%s: %s)" % (type(e).__name__, e))
    return status


def _check(a: argparse.Namespace) -> Tuple[int, str]:
    """(exit status, rendered report) for the change the flags describe."""
    root = gitdiff.repo_root(a.repo)
    cfg = config.Config() if a.no_config else config.load(root, a.config and os.path.abspath(a.config))
    budgets = cfg.apply(Budgets(), {name: getattr(a, name) for name in Budgets.__dataclass_fields__})
    base = gitdiff.EMPTY_TREE if a.all else gitdiff.resolve_base(root, a.base)
    findings, existing = run(root, base, budgets, [*cfg.exclude, *a.exclude], cfg.layers, audit=a.all)
    render = report.as_json if a.json else report.as_text
    return (1 if findings else 0,
            render(findings, "(whole repository)" if a.all else base, budgets, existing, cfg.path))


def _emit(text: str) -> None:
    """Print the report. A character stdout cannot encode is written as an escape, and a reader that has
    closed the pipe ends the output quietly: neither changes the exit status. Any other write failure is
    raised as the OSError it is."""
    out = sys.stdout
    if out is None:  # started with stdout closed (`>&-`): there is nowhere to print
        return
    if isinstance(out, io.TextIOWrapper):
        out.reconfigure(errors="backslashreplace")
    try:
        print(text, file=out)
        out.flush()
    except OSError as e:
        # What is still buffered can never be written; drop it, or the interpreter fails again at exit.
        os.dup2(os.open(os.devnull, os.O_WRONLY), out.fileno())
        if not isinstance(e, BrokenPipeError):
            raise


def _error(reason: str) -> int:
    """Print the one `error:` line (control characters escaped) and give exit status 2."""
    print("error: %s" % printable(reason), file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
