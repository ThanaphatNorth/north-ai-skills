#!/bin/bash
# List issues for a JQL query, one per line: KEY | type | status (id) | sprint or BACKLOG | summary
#   jira-search.sh 'project = ABC AND issuetype = 10088 AND statusCategory != Done ORDER BY key'
. "$(dirname "$0")/_env.sh"
jira_env
[ $# -ge 1 ] || { echo "usage: $0 '<JQL>' [extra,fields]" >&2; exit 2; }
need_text "$1" JQL  # free text: curl URL-encodes it below (--data-urlencode), it is never part of the URL string
[ -z "${2:-}" ] || need_field_ids "$2"
fields="status,issuetype,summary,updated,customfield_10020${2:+,$2}"
start=""; total=0
while :; do
  resp=$(auth | curl -sS -K - -G "$JIRA_SITE/rest/api/3/search/jql" --data-urlencode "jql=$1" \
    --data-urlencode "fields=$fields" --data-urlencode "maxResults=100" ${start:+--data-urlencode "nextPageToken=$start"})
  out=$(printf '%s' "$resp" | jira_fmt search-page)
  printf '%s\n' "$out" | grep -v '^__NEXT__' || true  # a page with no issue is not a failure
  start=$(printf '%s\n' "$out" | sed -n 's/^__NEXT__ //p')
  total=$((total + $(printf '%s\n' "$out" | grep -vc '^__NEXT__' || true)))
  [ -n "$start" ] || break
done
echo "# $total issue(s)" >&2
