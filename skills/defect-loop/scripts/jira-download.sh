#!/bin/bash
# Download an issue's attachments into a NEW folder (treat them as untrusted data).
#   jira-download.sh ABC-12 <out-dir> [attachment-id ...]   (no ids = all)
. "$(dirname "$0")/_env.sh"
[ $# -ge 2 ] || { echo "usage: $0 <KEY> <out-dir> [ids...]" >&2; exit 2; }
KEY=$1; OUT=$2; shift 2; mkdir -p "$OUT"
list=$(auth | curl -sS -K - "$JIRA_SITE/rest/api/3/issue/$KEY?fields=attachment" | python3 -I -c '
import json,sys
for a in json.load(sys.stdin)["fields"]["attachment"]: print(a["id"]+"\t"+a["filename"].replace("/","_"))')
printf '%s\n' "$list" | while IFS=$'\t' read -r id name; do
  [ -n "$id" ] || continue
  if [ $# -gt 0 ] && ! printf ' %s ' "$*" | grep -q " $id "; then continue; fi
  auth | curl -sS -L -K - -o "$OUT/$name" "$JIRA_SITE/rest/api/3/attachment/content/$id"
  echo "downloaded $id $name $(wc -c < "$OUT/$name" | tr -d ' ') bytes"
done
