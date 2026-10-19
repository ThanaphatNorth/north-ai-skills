#!/bin/bash
# Print one issue as plain text: summary, status, created/updated, description, every comment, attachments.
#   jira-get.sh ABC-12
. "$(dirname "$0")/_env.sh"
[ $# -eq 1 ] || { echo "usage: $0 <KEY>" >&2; exit 2; }
auth | curl -sS -K - "$JIRA_SITE/rest/api/3/issue/$1?fields=summary,status,issuetype,description,comment,attachment,created,updated,reporter&expand=renderedFields" | python3 -I -c '
import json,sys,re,html
d=json.load(sys.stdin)
if "fields" not in d: print("ERROR", json.dumps(d)[:300]); sys.exit(1)
f=d["fields"]; r=d.get("renderedFields") or {}
txt=lambda h: html.unescape(re.sub(r"[ \t]+"," ",re.sub(r"<br ?/?>|</p>|</li>|</tr>","\n",re.sub(r"<(?!br|/p|/li|/tr)[^>]+>","",h or "")))).strip()
print("%s  [%s / %s (%s)]  id=%s" % (d["key"], f["issuetype"]["name"], f["status"]["name"], f["status"]["id"], d["id"]))
print("created %s · updated %s · reporter %s" % (f["created"][:16], f["updated"][:16], (f.get("reporter") or {}).get("displayName","?")))
print("SUMMARY:", f["summary"]); print("DESCRIPTION:\n" + txt(r.get("description")))
cs=(r.get("comment") or {}).get("comments") or []
for c, raw in zip(cs, f["comment"]["comments"]):
    print("--- comment %s by %s at %s\n%s" % (raw["id"], raw["author"]["displayName"], raw["created"][:16], txt(c.get("body"))))
for a in f.get("attachment") or []: print("ATTACHMENT %s  %s  %s bytes  %s" % (a["id"], a["filename"], a["size"], a["mimeType"]))'
