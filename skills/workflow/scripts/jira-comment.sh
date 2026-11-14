#!/bin/bash
# Post (or update) a comment written in the loop's markdown dialect, then verify it rendered.
#   jira-comment.sh ABC-12 comment.md              → new comment
#   jira-comment.sh ABC-12 comment.md 61260        → update comment 61260
# `::video <media-uuid>` lines become inline players. After posting it reads the comment back
# (renderedBody) and prints the player count, attachment ids and any `backtick` path that went missing.
. "$(dirname "$0")/_env.sh"
jira_env
[ $# -ge 2 ] || { echo "usage: $0 <KEY> <comment.md> [commentId]" >&2; exit 2; }
KEY=$1; MD=$2; CID=${3:-}
need_key "$KEY"
need_file "$MD" comment.md
[ -z "$CID" ] || need_id "$CID" "comment id"
resp=$(mktemp); body=$(mktemp); trap 'rm -f "$resp" "$body"' EXIT
code=$(auth | curl -sS -K - -o "$resp" -w '%{http_code}' "$JIRA_SITE/rest/api/3/issue/$KEY?fields=summary")
[ "$code" = "200" ] || { echo "FAILED reading $KEY: HTTP $code $(head -c 300 "$resp")" >&2; exit 1; }
ISSUE_ID=$(jira_fmt id < "$resp")
python3 -I "$HERE/md2adf.py" "$MD" "$ISSUE_ID" | jira_fmt comment-body > "$body"
if [ -n "$CID" ]; then
  code=$(auth | curl -sS -K - -X PUT -H 'Content-Type: application/json' --data-binary "@$body" -o "$resp" -w '%{http_code}' "$JIRA_SITE/rest/api/3/issue/$KEY/comment/$CID")
else
  code=$(auth | curl -sS -K - -X POST -H 'Content-Type: application/json' --data-binary "@$body" -o "$resp" -w '%{http_code}' "$JIRA_SITE/rest/api/3/issue/$KEY/comment")
fi
[ "$code" = "200" ] || [ "$code" = "201" ] || { echo "FAILED $KEY comment: HTTP $code $(head -c 400 "$resp")" >&2; exit 1; }
NEW=$(jira_fmt id < "$resp")
is_id "$NEW" || { echo "FAILED $KEY comment: Jira answered with comment id '$NEW', not a number" >&2; exit 1; }
auth | curl -sS -K - "$JIRA_SITE/rest/api/3/issue/$KEY/comment/$NEW?expand=renderedBody" | jira_fmt comment-check "$MD" "$CID"
