#!/bin/bash
# Print the fields triage needs that jira-get.sh does not: labels, priority, parent, issue links, and the custom
# fields config lists (severity, environment, steps, expected result, acceptance criteria, an AI status field…).
#   jira-card.sh ABC-12
#   jira-card.sh ABC-12 customfield_10050,customfield_10060
# Text fields print as one line, paragraphs joined by " | "; select fields print their value (and child value).
set -euo pipefail
[ $# -ge 1 ] && [ $# -le 2 ] || { echo "usage: $0 <KEY> [fieldId,fieldId…]" >&2; exit 2; }
KEY=$1; EXTRA=${2:-}
case $KEY in -*|*/*|*\?*) echo "usage: $0 <KEY> [fieldId,fieldId…]" >&2; exit 2 ;; esac
if [ -n "$EXTRA" ] && ! printf '%s' "$EXTRA" | grep -Eq '^[A-Za-z0-9_]+(,[A-Za-z0-9_]+)*$'; then
  echo "jira-card.sh: field ids are comma-separated ids like customfield_10050, got '$EXTRA'" >&2; exit 2
fi
. "$(dirname "$0")/_env.sh"
fields="summary,status,issuetype,priority,labels,parent,issuelinks${EXTRA:+,$EXTRA}"
auth | curl -sS -K - "$JIRA_SITE/rest/api/3/issue/$KEY?fields=$fields&expand=renderedFields,names" | python3 -I -c '
import html, json, re, sys
d = json.load(sys.stdin)
if "fields" not in d:
    print("ERROR " + json.dumps(d)[:300]); sys.exit(1)
f, r, names = d["fields"], d.get("renderedFields") or {}, d.get("names") or {}
extra = [x for x in sys.argv[1].split(",") if x]

def text(h):
    h = re.sub(r"<br ?/?>|</p>|</li>|</tr>|</h[1-6]>", "\n", h)
    lines = (html.unescape(re.sub(r"<[^>]+>", "", line)).strip() for line in h.splitlines())
    return " | ".join(line for line in lines if line)

def value(v):
    if v is None or v == [] or v == "":
        return "(empty)"
    if isinstance(v, list):
        return ", ".join(value(x) for x in v)
    if isinstance(v, dict):
        for k in ("value", "name", "displayName", "key"):
            if k in v:
                child = v.get("child")
                return str(v[k]) + (" / " + value(child) if child else "")
        return json.dumps(v, ensure_ascii=False)[:200]
    return str(v)

pr = (f.get("priority") or {}).get("name")
print("%s  [%s / %s (%s)]  id=%s%s" % (d["key"], f["issuetype"]["name"], f["status"]["name"], f["status"]["id"], d["id"],
                                       "  priority " + pr if pr else ""))
print("LABELS: " + (", ".join(f.get("labels") or []) or "(none)"))
p = f.get("parent")
if p:
    print("PARENT: %s %s" % (p["key"], (p.get("fields") or {}).get("summary", "")))
for link in f.get("issuelinks") or []:
    side, verb = ("outwardIssue", "outward") if "outwardIssue" in link else ("inwardIssue", "inward")
    i = link[side]; lf = i.get("fields") or {}
    print("LINK: %s %s [%s] %s" % (link["type"][verb], i["key"], (lf.get("status") or {}).get("name", "?"), lf.get("summary", "")))
for fid in extra:
    shown = text(r[fid]) if isinstance(r.get(fid), str) and r[fid].strip() else value(f.get(fid))
    print("FIELD %s (%s): %s" % (fid, names.get(fid, fid), shown or "(empty)"))
' "$EXTRA"
