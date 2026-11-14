#!/bin/bash
# Upload files to an issue and print each one's media uuid (needed for an inline player).
#   jira-attach.sh ABC-12 ABC-12-before.mp4 ABC-12-after.mp4
# → "attached <name> id <attachment-id> <bytes> bytes media <uuid>"
# Exit 1 when Jira refused any of the files (the others are still uploaded), 2 when an argument is not a file.
. "$(dirname "$0")/_env.sh"
jira_env
[ $# -ge 2 ] || { echo "usage: $0 <KEY> <file>..." >&2; exit 2; }
KEY=$1; shift
need_key "$KEY"
for f in "$@"; do need_file "$f" file; done
resp=$(mktemp); trap 'rm -f "$resp"' EXIT
failed=0
for f in "$@"; do
  curl_quoted "$f"  # quoted, so a ; or , in the file name is not read as form syntax
  code=$(auth | curl -sS -K - -H "X-Atlassian-Token: no-check" -F "file=@\"$CURL_QUOTED\"" -o "$resp" -w '%{http_code}' "$JIRA_SITE/rest/api/3/issue/$KEY/attachments") || code=000
  if [ "$code" != "200" ]; then echo "FAILED $KEY $(basename "$f") HTTP $code: $(head -c 300 "$resp")" >&2; failed=1; continue; fi
  jira_fmt attachments < "$resp" | while IFS='|' read -r aid size name; do
    # the content endpoint 303-redirects to …/file/<uuid>/binary — that uuid is the media id
    loc=""
    if is_id "$aid"; then
      loc=$(auth | curl -sS -K - -o /dev/null -w '%{redirect_url}' "$JIRA_SITE/rest/api/3/attachment/content/$aid") || loc=""
    fi
    uuid=$(printf '%s' "$loc" | sed -nE 's#.*/file/([0-9a-f-]{36})/.*#\1#p')
    echo "attached $name id $aid $size bytes media ${uuid:-UNKNOWN}"
  done
done
exit "$failed"
