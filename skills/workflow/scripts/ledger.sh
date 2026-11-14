#!/bin/bash
# The loops' one way to write a ledger row:
#   ledger.sh <dev|defect> <KEY> <state> <branch @ sha> <worktree · ports · DB> <evidence> <next>
# Appends one row, stamped with the local date and time, to <working state>/<flow>-ledger.md of the main checkout
# (also when run from a linked worktree): .90north-develop/ beside the project, or .claude/90north-develop/ in a
# project that has not moved its state yet. Every ledger row goes through here, so each one is checked and stamped
# the same way, and a project not moved yet can still record a row in a session that can ask nobody.
# A cell is one line of text; a `|` inside it is written `\|` so the row keeps its seven columns.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
refuse() { echo "ledger: $1" >&2; exit 2; }
[ $# -eq 7 ] || refuse "usage: $0 <dev|defect> <KEY> <state> <branch @ sha> <worktree · ports · DB> <evidence> <next>"
flow=$1 key=$2 state=$3
case $flow in dev | defect) ;; *) refuse "the flow is dev or defect, not '$flow'" ;; esac
for cell in "$@"; do
  case $cell in *$'\n'* | *$'\r'*) refuse "every cell is one line of text" ;; esac
done
[[ $key =~ ^[A-Za-z][A-Za-z0-9]*-[A-Za-z0-9][A-Za-z0-9-]*$ ]] || refuse "KEY looks like TASK-2, ABC-123 or LOCAL-add-coupon, not '$key'"
[[ $state =~ ^[a-z][a-z0-9-]*$ ]] || refuse "the state is one lower-case word such as in-review or awaiting-push, not '$state'"
# shellcheck source=_state.sh
. "$HERE/_state.sh"
name="$flow-ledger.md"
case $DEVELOP_DIR in
  */.claude/defect-loop) # the single-loop setup: its ledger.md is the defect ledger, and it has no development loop
    [ "$flow" = defect ] || refuse "this project still has the legacy .claude/defect-loop/ folder — run /90north-develop:develop-init before the development loop"
    name=ledger.md ;;
esac
file="$DEVELOP_STATE_DIR/$name"
case $DEVELOP_STATE_DIR in
  */.claude/90north-develop) echo "note: this project's working state is still under .claude/ — $HERE/move-state.sh moves it beside the project" >&2 ;;
esac
[ ! -L "$file" ] || refuse "$file is a link; a ledger is a plain file in the state folder"
[ -f "$file" ] || refuse "$file is missing — run /90north-develop:develop-init"
row="| $(date '+%Y-%m-%d %H:%M') | $key | $state"
for cell in "$4" "$5" "$6" "$7"; do
  row+=" | ${cell//|/\\|}"
done
row+=" |"
# start on a fresh line when the last row has no line end
if [ -s "$file" ] && [ -n "$(tail -c 1 "$file")" ]; then printf '\n' >> "$file"; fi
printf '%s\n' "$row" >> "$file"
echo "ledger: $flow $key → $state"
