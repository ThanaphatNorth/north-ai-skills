#!/bin/bash
# Create the Jira credentials file by asking for the email and the API token, so the token never passes through a
# chat, a command line or the process list.
#   jira-login.sh [--force] [path]        path defaults to JIRA_ENV_FILE in tracker.env
# It asks on the terminal (the token is not echoed), or reads two lines from stdin when there is no terminal. The
# file is written whole with mode 600 and replaces an existing one only with --force; one GET /rest/api/3/myself
# then checks it.
# → "OK <display name>", or "FAILED HTTP <code>" and exit 1 (the file stays: fix and run again with --force)
. "$(dirname "$0")/_env.sh"
umask 077
usage() { echo "usage: $0 [--force] [path]" >&2; exit 2; }
force=0; target=""
for a in "$@"; do
  case $a in
    --force) force=1 ;;
    -*) usage ;;
    *) [ -z "$target" ] || usage; target=$a ;;
  esac
done
jira_state
target=${target:-$JIRA_ENV_FILE}
keep_existing() {
  [ ! -d "$target" ] || bad_arg "path must be a file, got the folder $target"
  if [ "$force" = 0 ] && { [ -e "$target" ] || [ -L "$target" ]; }; then
    bad_arg "$target already exists; pass --force to replace it"
  fi
}
keep_existing

# ask <prompt> [-s]: one line from the terminal when there is one, else from stdin, without the blanks around it,
# in ANSWER. read shows the prompt, and -s hides the typing, only on a terminal.
ask() {
  local line=""
  if [ "${2:-}" = "-s" ]; then
    IFS= read -r -s -u 3 -p "$1" line || true
  else
    IFS= read -r -u 3 -p "$1" line || true
  fi
  if [ -n "${2:-}" ] && [ -t 3 ]; then echo >&2; fi
  line=${line#"${line%%[![:space:]]*}"}
  ANSWER=${line%"${line##*[![:space:]]}"}
}
if { : < /dev/tty; } 2>/dev/null; then exec 3< /dev/tty; else exec 3<&0; fi
ask "Jira email for $JIRA_SITE: "; email=$ANSWER
ask "API token (not shown): " -s; token=$ANSWER
exec 3<&-
unset ANSWER
matches "$email" '^[^[:space:]:]+@[^[:space:]:]+$' || bad_arg "email must look like name@example.com"
[ -n "$token" ] || bad_arg "API token must not be empty"

# written beside the target, then moved over it: the file is never there half-written or with a wider mode
mkdir -p "$(dirname "$target")"
tmp=$(mktemp "$(dirname "$target")/.jira-login.XXXXXX"); resp=""
trap 'rm -f "$tmp" ${resp:+"$resp"}' EXIT
credentials_text "$email" "$token" > "$tmp"
unset email token
chmod 600 "$tmp"
keep_existing
mv -f "$tmp" "$target"

JIRA_ENV_FILE=$target
jira_credentials
resp=$(mktemp)
code=$(auth | curl -sS -K - -o "$resp" -w '%{http_code}' "$JIRA_SITE/rest/api/3/myself") || code=000
if [ "$code" = "200" ] && name=$(jira_fmt display-name < "$resp"); then echo "OK $name"; exit 0; fi
echo "FAILED HTTP $code"
exit 1
