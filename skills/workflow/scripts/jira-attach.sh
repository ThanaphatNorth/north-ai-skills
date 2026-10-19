#!/bin/bash
# Upload files to an issue and print each one's media uuid (needed for an inline player).
#   jira-attach.sh ABC-12 ABC-12-before.mp4 ABC-12-after.mp4
# → "attached <name> id <attachment-id> <bytes> bytes media <uuid>"
. "$(dirname "$0")/_env.sh"
[ $# -ge 2 ] || { echo "usage: $0 <KEY> <file>..." >&2; exit 2; }
KEY=$1; shift
resp=$(mktemp); trap 'rm -f "$resp"' EXIT
for f in "$@"; do
  [ -f "$f" ] || { echo "skip (not a file): $f" >&2; continue; }
  code=$(auth | curl -sS -K - -H "X-Atlassian-Token: no-check" -F "file=@$f" -o "$resp" -w '%{http_code}' "$JIRA_SITE/rest/api/3/issue/$KEY/attachments") || code=000
  if [ "$code" != "200" ]; then echo "FAILED $KEY $(basename "$f") HTTP $code: $(head -c 300 "$resp")" >&2; continue; fi
  python3 -I -c 'import json,sys; [print(a["id"]+"|"+a["filename"]+"|"+str(a["size"])) for a in json.load(open(sys.argv[1]))]' "$resp" | while IFS='|' read -r aid name size; do
    # the content endpoint 303-redirects to …/file/<uuid>/binary — that uuid is the media id
    loc=$(auth | curl -sS -K - -o /dev/null -w '%{redirect_url}' "$JIRA_SITE/rest/api/3/attachment/content/$aid") || loc=""
    uuid=$(printf '%s' "$loc" | sed -nE 's#.*/file/([0-9a-f-]{36})/.*#\1#p')
    echo "attached $name id $aid $size bytes media ${uuid:-UNKNOWN}"
  done
done
