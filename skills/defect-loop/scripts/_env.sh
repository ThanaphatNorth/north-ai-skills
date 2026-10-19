#!/bin/bash
# Shared setup for the defect-loop Jira scripts. Sourced, never run.
# Finds the project's .claude/defect-loop/ (DEFECT_LOOP_DIR, or walk up from $PWD),
# reads tracker.env (JIRA_SITE, JIRA_ENV_FILE — no secrets), then loads the
# credentials file (JIRA_EMAIL, JIRA_TOKEN). The token only ever reaches curl on
# stdin via `auth | curl -K -`; nothing here prints it.
set -euo pipefail

if [ -z "${DEFECT_LOOP_DIR:-}" ]; then
  d=$PWD
  while [ "$d" != "/" ] && [ ! -f "$d/.claude/defect-loop/tracker.env" ]; do d=$(dirname "$d"); done
  [ -f "$d/.claude/defect-loop/tracker.env" ] || { echo "no .claude/defect-loop/tracker.env above $PWD — run /90north-develop:defect-loop-init, or set DEFECT_LOOP_DIR" >&2; exit 2; }
  DEFECT_LOOP_DIR="$d/.claude/defect-loop"
fi
# shellcheck disable=SC1091
. "$DEFECT_LOOP_DIR/tracker.env"
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
