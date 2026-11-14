#!/bin/bash
# Print the fields triage needs that jira-get.sh does not: labels, priority, parent, issue links, and the custom
# fields config lists (severity, environment, steps, expected result, acceptance criteria, an AI status field…).
#   jira-card.sh ABC-12
#   jira-card.sh ABC-12 customfield_10050,customfield_10060
# Text fields print as one line, paragraphs joined by " | "; select fields print their value (and child value).
set -euo pipefail
[ $# -ge 1 ] && [ $# -le 2 ] || { echo "usage: $0 <KEY> [fieldId,fieldId…]" >&2; exit 2; }
KEY=$1; EXTRA=${2:-}
. "$(dirname "$0")/_env.sh"
need_key "$KEY"
[ -z "$EXTRA" ] || need_field_ids "$EXTRA"
jira_env
fields="summary,status,issuetype,priority,labels,parent,issuelinks${EXTRA:+,$EXTRA}"
auth | curl -sS -K - "$JIRA_SITE/rest/api/3/issue/$KEY?fields=$fields&expand=renderedFields,names" | jira_fmt card "$EXTRA"
