#!/bin/bash
# Print one issue as plain text: summary, status, created/updated, description, every comment, attachments.
#   jira-get.sh ABC-12
. "$(dirname "$0")/_env.sh"
jira_env
[ $# -eq 1 ] || { echo "usage: $0 <KEY>" >&2; exit 2; }
need_key "$1"
auth | curl -sS -K - "$JIRA_SITE/rest/api/3/issue/$1?fields=summary,status,issuetype,description,comment,attachment,created,updated,reporter&expand=renderedFields" | jira_fmt issue
