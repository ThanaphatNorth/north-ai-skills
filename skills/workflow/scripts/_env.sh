#!/bin/bash
# Shared by the Jira backend scripts (jira-*.sh, reached through tracker.sh). Sourced, never run. Sourcing it only
# defines functions; a script then calls `jira_env`, which loads tracker.env through _state.sh (JIRA_SITE,
# JIRA_ENV_FILE — no secrets) and reads the credentials file (JIRA_EMAIL, JIRA_TOKEN).
# The credentials file is parsed, never run as shell, and its two values stay plain shell variables: they are not
# exported, so no child process sees them. The token leaves this shell one way only, on curl's stdin, through
# `auth | curl -K -`; nothing here prints it.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# jira_fmt <command> [args…]: jira_fmt.py, which turns Jira's JSON into the text the scripts print.
jira_fmt() { python3 -I "$HERE/jira_fmt.py" "$@"; }

# ---- argument rules ----
# Each kind of value that reaches a URL has its one rule here. need_* ends the script with exit 2 and a message
# naming the argument, before any request is made; is_id only answers, for ids read from a response.

# matches <value> <extended regex>: with ASCII ranges, whatever the caller's locale
matches() { local LC_ALL=C; [[ $1 =~ $2 ]]; }
bad_arg() { echo "$(basename "$0"): $1" >&2; exit 2; }
is_id() { matches "$1" '^[0-9]+$'; }
# an issue key, the shape local_board.py accepts
need_key() { matches "$1" '^[A-Za-z][A-Za-z0-9_]*-[0-9]+$' || bad_arg "KEY must be an issue key like ABC-12, got '$1'"; }
# need_id <value> <argument name>: a comment, attachment or transition id
need_id() { is_id "$1" || bad_arg "$2 must be digits only, got '$1'"; }
need_field_ids() {
  matches "$1" '^[A-Za-z][A-Za-z0-9_]*(,[A-Za-z][A-Za-z0-9_]*)*$' ||
    bad_arg "field ids are comma-separated ids like customfield_10050, got '$1'"
}
# need_text <value> <argument name>: free text that curl URL-encodes or that travels in a body; only emptiness is refused
need_text() { matches "$1" '[^[:space:]]' || bad_arg "$2 must not be empty"; }
# need_file <path> <argument name>
need_file() { [ -f "$1" ] || bad_arg "$2 must be an existing file, got '$1'"; }

# curl_quoted <text>: the text as curl reads it back from inside double quotes (a -K parameter, a -F file name), in
# CURL_QUOTED. \ and " are escaped, so no value can end the quoted string early.
curl_quoted() { CURL_QUOTED=${1//\\/\\\\}; CURL_QUOTED=${CURL_QUOTED//\"/\\\"}; }

# ---- settings: tracker.env ----

jira_state() {
  # shellcheck source=_state.sh
  . "$HERE/_state.sh"
  [ "$TRACKER" = "jira" ] || { echo "tracker.env says TRACKER=$TRACKER: call scripts/tracker.sh <verb>, not $(basename "$0")" >&2; exit 2; }
  : "${JIRA_SITE:?JIRA_SITE missing in tracker.env}"
  : "${JIRA_ENV_FILE:?JIRA_ENV_FILE missing in tracker.env}"
  JIRA_SITE=${JIRA_SITE%/}
  JIRA_ENV_FILE=${JIRA_ENV_FILE/#\~/$HOME}
}

# ---- credentials ----

# read_credentials <file>: JIRA_EMAIL and JIRA_TOKEN from their lines, by _state.sh's read_settings (so jira_state
# comes first): the file is parsed like tracker.env, never run. Values in the calling environment are dropped first,
# so the file is the only source and the variables are never exported.
read_credentials() {
  unset JIRA_EMAIL JIRA_TOKEN
  read_settings "$1" JIRA_EMAIL JIRA_TOKEN
}

# credentials_text <email> <token>: the two lines read_credentials reads back to exactly these values (the
# double-quoted form of _setting_value in _state.sh).
credentials_text() {
  local name v
  for name in JIRA_EMAIL JIRA_TOKEN; do
    v=$1; shift
    v=${v//\\/\\\\}; v=${v//\"/\\\"}; v=${v//\$/\\\$}; v=${v//\`/\\\`}
    printf '%s="%s"\n' "$name" "$v"
  done
}

jira_credentials() {
  local perm
  [ -f "$JIRA_ENV_FILE" ] || { echo "missing credentials file $JIRA_ENV_FILE (JIRA_EMAIL, JIRA_TOKEN; chmod 600)" >&2; exit 2; }
  perm=$(stat -f %Lp "$JIRA_ENV_FILE" 2>/dev/null || stat -c %a "$JIRA_ENV_FILE")
  if [ "$perm" != "600" ] && [ "$perm" != "400" ]; then chmod 600 "$JIRA_ENV_FILE"; echo "note: tightened $JIRA_ENV_FILE to 600 (was $perm)" >&2; fi
  read_credentials "$JIRA_ENV_FILE"
  [ -n "${JIRA_EMAIL:-}" ] && [ -n "${JIRA_TOKEN:-}" ] || { echo "JIRA_EMAIL / JIRA_TOKEN not set in $JIRA_ENV_FILE" >&2; exit 2; }
}

# auth: the curl config line that carries the credentials, for `auth | curl -K -`. The value is quoted for curl, so
# a token cannot add another option to the config.
auth() { curl_quoted "$JIRA_EMAIL:$JIRA_TOKEN"; printf 'user = "%s"\n' "$CURL_QUOTED"; }

jira_env() { jira_state; jira_credentials; }
