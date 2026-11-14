#!/usr/bin/env bash
# Types and coverage for every script in this repo, as one repeatable check.
#
#   tools/quality.sh            mypy --strict on the scripts, shellcheck on the shell scripts, then the four test
#                               suites under branch coverage
#   tools/quality.sh --types    mypy only
#
# Exit 1 when mypy or shellcheck reports anything, a test fails, or coverage is under the floor below.
#
# The scripts themselves need nothing but the standard library. This check needs two tools, mypy and coverage, and
# keeps them out of the repo's way: the first run builds .venv-tools/ (git-ignored) with uv, or with python3 -m venv
# when uv is not installed, and downloads the two pinned packages from PyPI. Delete the folder to start over.
set -euo pipefail

FLOOR=97            # percent of branches and statements, all suites together; raise it when the number rises
MYPY=1.14.1         # the last line that can check against Python 3.8, which the README promises
COVERAGE=7.6.1      # the last line that still installs on Python 3.8

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VENV="$ROOT/.venv-tools"
PY="$VENV/bin/python"

if [ ! -x "$PY" ]; then
  echo "quality: building $VENV (downloads mypy $MYPY and coverage $COVERAGE from PyPI)" >&2
  if command -v uv >/dev/null 2>&1; then
    uv venv -q "$VENV"
    uv pip install -q --python "$PY" "mypy==$MYPY" "coverage==$COVERAGE"
  else
    python3 -m venv "$VENV"
    "$PY" -m pip install -q "mypy==$MYPY" "coverage==$COVERAGE"
  fi
  # the tests start the scripts as child processes: this line makes each child report its own coverage
  site="$("$PY" -c 'import site; print(site.getsitepackages()[0])')"
  echo "import coverage; coverage.process_startup()" > "$site/zz_coverage_subprocess.pth"
fi

cd "$ROOT"
failed=0
types() { # types <folder> [package…]: every script in the folder, plus the packages named
  local dir=$1; shift
  # shellcheck disable=SC2046  # the file list is meant to split into words
  ( cd "$dir" && "$PY" -m mypy --python-version 3.8 --strict --no-incremental --cache-dir=/dev/null $(ls ./*.py) "$@" ) || failed=1
}
echo "== types (mypy --strict, Python 3.8)"
types skills/n-dev/scripts ndev_check
types skills/workflow/scripts
types tools repo_check
types plugins/90north-develop/hooks
if [ "${1:-}" = "--types" ]; then exit "$failed"; fi

echo "== shell lint (shellcheck -x)"
if command -v shellcheck >/dev/null 2>&1; then
  ( cd skills/workflow/scripts && shellcheck -x ./*.sh ) && shellcheck -x tools/quality.sh && echo "clean" || failed=1
else
  echo "SKIPPED: shellcheck is not installed on this machine, so the shell scripts were not linted"
fi

DATA="$(mktemp -d)"
# on the way out, remove only what this run put in its own temp folder
trap 'find "$DATA" -maxdepth 1 -type f \( -name ".coverage*" -o -name rc \) -exec rm -f {} + 2>/dev/null; rmdir "$DATA" 2>/dev/null || true' EXIT
cat > "$DATA/rc" <<EOF
[run]
branch = True
parallel = True
data_file = $DATA/.coverage
source =
    $ROOT/skills/n-dev/scripts
    $ROOT/skills/workflow/scripts
    $ROOT/tools
    $ROOT/plugins/90north-develop/hooks
omit =
    */tests/*
[report]
skip_empty = True
show_missing = True
fail_under = $FLOOR
EOF
export COVERAGE_PROCESS_START="$DATA/rc" PATH="$VENV/bin:$PATH" PYTHONDONTWRITEBYTECODE=1
echo "== tests under coverage"
for suite in skills/n-dev/scripts/tests skills/workflow/scripts/tests tools/tests plugins/90north-develop/hooks/tests; do
  echo "-- $suite"
  "$PY" -m unittest discover -s "$suite" -p 'test_*.py' 2>&1 | tail -3
  [ "${PIPESTATUS[0]}" -eq 0 ] || failed=1
done
"$PY" -m coverage combine --rcfile="$DATA/rc" -q
echo "== coverage (branch), floor $FLOOR%"
"$PY" -m coverage report --rcfile="$DATA/rc" || failed=1
exit "$failed"
