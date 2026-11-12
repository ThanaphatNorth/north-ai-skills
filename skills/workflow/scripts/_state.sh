#!/bin/bash
# Shared by every tracker script: finds the project's state folder and loads tracker.env. Sourced, never run.
# DEVELOP_DIR, else the legacy DEFECT_LOOP_DIR, else the nearest .claude/90north-develop/ (or legacy
# .claude/defect-loop/) above $PWD that holds tracker.env. A folder found inside a linked git worktree maps to the
# same path in the main checkout when that one has tracker.env too, so every worktree reads and writes one board.
# Leaves DEVELOP_DIR exported and TRACKER set (jira when tracker.env has no TRACKER line).
set -euo pipefail

DEVELOP_DIR=${DEVELOP_DIR:-${DEFECT_LOOP_DIR:-}}
if [ -z "$DEVELOP_DIR" ]; then
  d=$PWD
  while [ "$d" != "/" ] && [ -z "$DEVELOP_DIR" ]; do
    for sub in .claude/90north-develop .claude/defect-loop; do
      if [ -f "$d/$sub/tracker.env" ]; then DEVELOP_DIR="$d/$sub"; break; fi
    done
    d=$(dirname "$d")
  done
  [ -n "$DEVELOP_DIR" ] || { echo "no .claude/90north-develop/tracker.env above $PWD — run /90north-develop:develop-init, or set DEVELOP_DIR" >&2; exit 2; }
  case $DEVELOP_DIR in */.claude/defect-loop) echo "note: legacy state folder $DEVELOP_DIR — /90north-develop:develop-init migrates it" >&2 ;; esac
  DEVELOP_DIR=$(cd "$DEVELOP_DIR" && pwd -P)
  top=$(git -C "$DEVELOP_DIR" rev-parse --show-toplevel 2>/dev/null || true)
  common=$(git -C "$DEVELOP_DIR" rev-parse --path-format=absolute --git-common-dir 2>/dev/null || true)
  if [ -n "$top" ] && [ "${common##*/}" = ".git" ] && [ "${common%/.git}" != "$top" ]; then
    shared="${common%/.git}/${DEVELOP_DIR#"$top"/}"
    if [ -f "$shared/tracker.env" ]; then DEVELOP_DIR=$shared; fi
  fi
fi
export DEVELOP_DIR
# The backend and its settings come from tracker.env only, never from the calling shell.
# shellcheck disable=SC2034  # LOCAL_BOARD and LOCAL_STATUSES are read by tracker.sh, which sources this file
TRACKER="" LOCAL_BOARD="" LOCAL_STATUSES=""
# shellcheck disable=SC1091
. "$DEVELOP_DIR/tracker.env"
TRACKER=${TRACKER:-jira}
