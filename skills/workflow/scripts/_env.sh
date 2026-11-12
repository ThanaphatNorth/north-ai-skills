#!/bin/bash
# Shared setup for the Jira backend scripts (jira-*.sh, reached through tracker.sh). Sourced, never run.
# _state.sh finds the state folder and reads tracker.env (JIRA_SITE, JIRA_ENV_FILE — no secrets); this file then
# loads the credentials file (JIRA_EMAIL, JIRA_TOKEN). The token only ever reaches curl on stdin via
# `auth | curl -K -`; nothing here prints it.
set -euo pipefail

# shellcheck source=_state.sh
. "$(dirname "${BASH_SOURCE[0]}")/_state.sh"
[ "$TRACKER" = "jira" ] || { echo "tracker.env says TRACKER=$TRACKER: call scripts/tracker.sh <verb>, not $(basename "$0")" >&2; exit 2; }
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
