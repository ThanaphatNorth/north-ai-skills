#!/bin/bash
# Move an issue through one workflow transition (ids live in config.md).
#   jira-transition.sh ABC-12 6
#   jira-transition.sh ABC-12 9 '{"customfield_10138":{"id":"10051","child":{"id":"10061"}}}'
#   jira-transition.sh ABC-12 --list          (show the transitions offered now)
. "$(dirname "$0")/_env.sh"
[ $# -ge 2 ] || { echo "usage: $0 <KEY> <transition-id|--list> [fields-json]" >&2; exit 2; }
if [ "$2" = "--list" ]; then
  auth | curl -sS -K - "$JIRA_SITE/rest/api/3/issue/$1/transitions" | python3 -I -c '
import json,sys
for t in json.load(sys.stdin)["transitions"]: print("%s → %s (status %s, %s)" % (t["id"], t["name"], t["to"]["id"], t["to"]["statusCategory"]["key"]))'
  exit 0
fi
body=$(python3 -I -c 'import json,sys; b={"transition":{"id":sys.argv[1]}}; f=sys.argv[2] if len(sys.argv)>2 else ""; 
if f: b["fields"]=json.loads(f)
print(json.dumps(b))' "$2" "${3:-}")
code=$(auth | curl -sS -K - -o /dev/null -w '%{http_code}' -X POST -H 'Content-Type: application/json' -d "$body" "$JIRA_SITE/rest/api/3/issue/$1/transitions")
st=$(auth | curl -sS -K - "$JIRA_SITE/rest/api/3/issue/$1?fields=status" | python3 -I -c 'import json,sys; s=json.load(sys.stdin)["fields"]["status"]; print("%s (%s)"%(s["name"],s["id"]))')
echo "$1 transition $2 → HTTP $code · now $st"
[ "$code" = "204" ]
