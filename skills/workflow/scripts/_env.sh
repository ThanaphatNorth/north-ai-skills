#!/bin/bash
# Shared setup for the 90north-develop Jira scripts (dev-loop and defect-loop). Sourced, never run.
# Finds the project's state folder: DEVELOP_DIR, else the legacy DEFECT_LOOP_DIR, else walk up
# from $PWD to .claude/90north-develop/ (or the legacy .claude/defect-loop/). Reads tracker.env
# (JIRA_SITE, JIRA_ENV_FILE — no secrets), then loads the credentials file (JIRA_EMAIL,
# JIRA_TOKEN). The token only ever reaches curl on stdin via `auth | curl -K -`; nothing here prints it.
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
fi
# shellcheck disable=SC1091
. "$DEVELOP_DIR/tracker.env"
: "${JIRA_SITE:?JIRA_SITE missing in tracker.env}"
: "${JIRA_ENV_FILE:?JIRA_ENV_FILE missing in tracker.env}"
JIRA_SITE=${JIRA_SITE%/}
JIRA_ENV_FILE=${JIRA_ENV_FILE/#\~/$HOME}
[ -f "$JIRA_ENV_FILE" ] || { echo "missing credentials file $JIRA_ENV_FILE (JIRA_EMAIL, JIRA_TOKEN; chmod 600)" >&2; exit 2; }
perm=$(stat -f %Lp "$JIRA_ENV_FILE" 2>/dev/null || stat -c %a "$JIRA_ENV_FILE")
if [ "$perm" != "600" ] && [ "$perm" != "400" ]; then chmod 600 "$JIRA_ENV_FILE"; echo "note: tightened $JIRA_ENV_FILE to 600 (was $perm)" >&2; fi
set -a
# shellcheck disable=SC1090
. "$JIRA_ENV_FILE"
set +a
[ -n "${JIRA_EMAIL:-}" ] && [ -n "${JIRA_TOKEN:-}" ] || { echo "JIRA_EMAIL / JIRA_TOKEN not set in $JIRA_ENV_FILE" >&2; exit 2; }
auth() { printf 'user = "%s:%s"\n' "$JIRA_EMAIL" "$JIRA_TOKEN"; }
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
