#!/bin/bash
# Move an issue through one workflow transition (ids live in config.md).
#   jira-transition.sh ABC-12 6
#   jira-transition.sh ABC-12 9 '{"customfield_10138":{"id":"10051","child":{"id":"10061"}}}'
#   jira-transition.sh ABC-12 --list          (show the transitions offered now)
. "$(dirname "$0")/_env.sh"
jira_env
[ $# -ge 2 ] || { echo "usage: $0 <KEY> <transition-id|--list> [fields-json]" >&2; exit 2; }
need_key "$1"
if [ "$2" = "--list" ]; then
  auth | curl -sS -K - "$JIRA_SITE/rest/api/3/issue/$1/transitions" | jira_fmt transitions
  exit 0
fi
need_id "$2" "transition id"
body=$(jira_fmt transition-body "$2" "${3:-}") || exit 2
code=$(auth | curl -sS -K - -o /dev/null -w '%{http_code}' -X POST -H 'Content-Type: application/json' -d "$body" "$JIRA_SITE/rest/api/3/issue/$1/transitions")
st=$(auth | curl -sS -K - "$JIRA_SITE/rest/api/3/issue/$1?fields=status" | jira_fmt status)
echo "$1 transition $2 → HTTP $code · now $st"
[ "$code" = "204" ]
