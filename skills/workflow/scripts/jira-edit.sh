#!/bin/bash
# Change labels and fields of one issue: auto mode's lock, verdict, class and hand-off labels, and its summary field.
# Ids and label names live in config.md § Auto mode.
#   jira-edit.sh ABC-12 --add-label ai-processing
#   jira-edit.sh ABC-12 --remove-label ai-processing --remove-label ai-queue --add-label ai-do-now
#   jira-edit.sh ABC-12 --field customfield_10050='{"value":"Level 4"}'     value is JSON
#   jira-edit.sh ABC-12 --field-md customfield_10100=summary.md            markdown file → ADF (multi-line text fields)
#   jira-edit.sh ABC-12 --dry-run --add-label x                            print the request body only; needs no credentials
set -euo pipefail
usage() { echo "usage: $0 <KEY> [--dry-run] (--add-label L | --remove-label L | --field ID=JSON | --field-md ID=FILE)..." >&2; exit 2; }
[ $# -ge 2 ] || usage
KEY=$1; shift
. "$(dirname "$0")/_env.sh"
need_key "$KEY"
DRY=0; ops=()
for a in "$@"; do
  if [ "$a" = "--dry-run" ]; then DRY=1; else ops+=("$a"); fi
done
[ ${#ops[@]} -gt 0 ] || usage
body=$(jira_fmt edit-body "${ops[@]}") || exit 2

if [ "$DRY" = 1 ]; then printf '%s\n' "$body"; exit 0; fi

jira_env
code=$(auth | curl -sS -K - -o /dev/null -w '%{http_code}' -X PUT -H 'Content-Type: application/json' --data-binary "$body" "$JIRA_SITE/rest/api/3/issue/$KEY")
labels=$(auth | curl -sS -K - "$JIRA_SITE/rest/api/3/issue/$KEY?fields=labels" | jira_fmt labels || echo "?")
echo "$KEY edit → HTTP $code · labels now: ${labels:-none}"
[ "$code" = "204" ]
