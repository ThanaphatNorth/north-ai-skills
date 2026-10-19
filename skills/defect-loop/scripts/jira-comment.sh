#!/bin/bash
# Post (or update) a comment written in the loop's markdown dialect, then verify it rendered.
#   jira-comment.sh ABC-12 comment.md              → new comment
#   jira-comment.sh ABC-12 comment.md 61260        → update comment 61260
# `::video <media-uuid>` lines become inline players. After posting it reads the comment back
# (renderedBody) and prints the player count, attachment ids and any `backtick` path that went missing.
. "$(dirname "$0")/_env.sh"
[ $# -ge 2 ] || { echo "usage: $0 <KEY> <comment.md> [commentId]" >&2; exit 2; }
KEY=$1; MD=$2; CID=${3:-}
resp=$(mktemp); body=$(mktemp); trap 'rm -f "$resp" "$body"' EXIT
code=$(auth | curl -sS -K - -o "$resp" -w '%{http_code}' "$JIRA_SITE/rest/api/3/issue/$KEY?fields=summary")
[ "$code" = "200" ] || { echo "FAILED reading $KEY: HTTP $code $(head -c 300 "$resp")" >&2; exit 1; }
ISSUE_ID=$(python3 -I -c 'import json,sys; print(json.load(open(sys.argv[1]))["id"])' "$resp")
python3 -I "$HERE/md2adf.py" "$MD" "$ISSUE_ID" | python3 -I -c 'import json,sys; print(json.dumps({"body": json.load(sys.stdin)}, ensure_ascii=False))' > "$body"
if [ -n "$CID" ]; then
  code=$(auth | curl -sS -K - -X PUT -H 'Content-Type: application/json' --data-binary "@$body" -o "$resp" -w '%{http_code}' "$JIRA_SITE/rest/api/3/issue/$KEY/comment/$CID")
else
  code=$(auth | curl -sS -K - -X POST -H 'Content-Type: application/json' --data-binary "@$body" -o "$resp" -w '%{http_code}' "$JIRA_SITE/rest/api/3/issue/$KEY/comment")
fi
[ "$code" = "200" ] || [ "$code" = "201" ] || { echo "FAILED $KEY comment: HTTP $code $(head -c 400 "$resp")" >&2; exit 1; }
NEW=$(python3 -I -c 'import json,sys; print(json.load(open(sys.argv[1]))["id"])' "$resp")
auth | curl -sS -K - "$JIRA_SITE/rest/api/3/issue/$KEY/comment/$NEW?expand=renderedBody" | python3 -I -c '
import json,sys,re
c=json.load(sys.stdin); b=c.get("renderedBody","")
md=open(sys.argv[1],encoding="utf-8").read()
want=len(re.findall(r"^::video ", md, re.M))
players=len(re.findall(r"type=\"video/mp4\"", b))
ids=sorted(set(re.findall(r"attachment/content/(\d+)", b)))
paths=[p for p in re.findall(r"`([^`]*[/.][^`]*)`", md) if p not in b]
print("comment %s %s · videos in md %d · players rendered %d · attachment ids %s" % (c["id"], "updated" if sys.argv[2] else "created", want, players, ids))
if want and not ids: print("WARNING: no inline player rendered — check the media uuids", file=sys.stderr)
if paths: print("WARNING: these `code` spans are missing from the rendered comment (unquoted heredoc?): %s" % paths, file=sys.stderr)
' "$MD" "$CID"
