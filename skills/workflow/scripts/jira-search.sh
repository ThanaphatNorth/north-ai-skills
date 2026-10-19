#!/bin/bash
# List issues for a JQL query, one per line: KEY | type | status (id) | sprint or BACKLOG | summary
#   jira-search.sh 'project = ABC AND issuetype = 10088 AND statusCategory != Done ORDER BY key'
. "$(dirname "$0")/_env.sh"
[ $# -ge 1 ] || { echo "usage: $0 '<JQL>' [extra,fields]" >&2; exit 2; }
fields="status,issuetype,summary,updated,customfield_10020${2:+,$2}"
start=""; total=0
while :; do
  resp=$(auth | curl -sS -K - -G "$JIRA_SITE/rest/api/3/search/jql" --data-urlencode "jql=$1" \
    --data-urlencode "fields=$fields" --data-urlencode "maxResults=100" ${start:+--data-urlencode "nextPageToken=$start"})
  out=$(printf '%s' "$resp" | python3 -I -c '
import json,sys
d=json.load(sys.stdin)
if "issues" not in d: print("ERROR "+json.dumps(d)[:300], file=sys.stderr); sys.exit(1)
for i in d["issues"]:
    f=i["fields"]; sp=f.get("customfield_10020") or []
    spn=",".join("%s(%s)"%(s.get("name",""),s.get("state","")) for s in sp) or "BACKLOG"
    print("%s | %s | %s (%s) | %s | %s | %s" % (i["key"], f["issuetype"]["name"], f["status"]["name"], f["status"]["id"], spn, f.get("updated","")[:16], f["summary"][:90]))
print("__NEXT__ " + ("" if d.get("isLast", True) else d.get("nextPageToken","")))')
  printf '%s\n' "$out" | grep -v '^__NEXT__'
  start=$(printf '%s\n' "$out" | sed -n 's/^__NEXT__ //p')
  total=$((total + $(printf '%s\n' "$out" | grep -vc '^__NEXT__' || true)))
  [ -n "$start" ] || break
done
echo "# $total issue(s)" >&2
