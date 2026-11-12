#!/bin/bash
# The loops' one door to the tracker:  tracker.sh <verb> [args…]
# Verbs: search get card edit transition comment attach download (arguments per backend: ../references/trackers.md).
# TRACKER in tracker.env picks the backend: jira (the default) runs jira-<verb>.sh unchanged; local runs
# local_board.py on the board folder (LOCAL_BOARD, LOCAL_STATUSES). Run it from inside the project.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
VERBS="search get card edit transition comment attach download"
usage() { echo "usage: $0 <verb> [args…]   verbs: $VERBS" >&2; exit 2; }
[ $# -ge 1 ] || usage
verb=$1; shift
case " $VERBS " in *" $verb "*) ;; *) echo "unknown verb '$verb'" >&2; usage ;; esac
# shellcheck source=_state.sh
. "$HERE/_state.sh"
case $TRACKER in
  jira) exec "$HERE/jira-$verb.sh" "$@" ;;
  local)
    export LOCAL_BOARD="${LOCAL_BOARD:-}" LOCAL_STATUSES="${LOCAL_STATUSES:-}"
    exec python3 -I "$HERE/local_board.py" "$verb" "$@" ;;
  *) echo "tracker.env: unknown TRACKER=$TRACKER (jira | local)" >&2; exit 2 ;;
esac
