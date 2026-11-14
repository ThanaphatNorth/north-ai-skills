#!/bin/bash
# Prints a project's two folders, one per line:   where.sh [--auto]
#   DC=<settings: config.md, tracker.env>
#   DL=<working state: the ledgers, lessons.md, the board, knowledge/, runs/>
# and a NOTE= line when the working state is under .claude/ (not moved yet, a legacy folder, a name or link that
# leads there, or a project that itself sits under a folder named .claude) or is in two places (it is read beside
# the project while a ledger, cards, lessons or knowledge are still under .claude/).
# Both are absolute, physical paths: what is printed is where a write really lands.
# A loop reads the folders from here and never builds the paths by hand: a project set up before 0.12 has both in
# one place until move-state.sh has run, and writing to the other place would split its state in two.
# --auto is how an unattended pass asks. Under .claude/ a session that can ask nobody writes some files and is
# refused others, and cannot remove its own pass lock, so a pass that starts there ends half done; with the state
# in two places it would miss the records left behind. With --auto either project is refused: the folders are
# still printed, the reason goes to stderr, exit 3. A working state folder that does not exist is exit 2 with
# --auto: develop-init has not written it (or DEVELOP_STATE_DIR names nothing), and ledger.sh only appends to a
# ledger that is there, so the pass could not record its work.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
auto=0
case ${1:-} in
  "") ;;
  --auto) auto=1 ;;
  *) echo "usage: $0 [--auto]" >&2; exit 2 ;;
esac
[ $# -le 1 ] || { echo "usage: $0 [--auto]" >&2; exit 2; }
# shellcheck source=_state.sh
. "$HERE/_state.sh"
echo "DC=$DEVELOP_DIR"
echo "DL=$DEVELOP_STATE_DIR"
why="" how=""
if [ -n "$DEVELOP_STATE_SPLIT" ]; then
  why="the working state is in two places: $DEVELOP_STATE_DIR is the one read, and $DEVELOP_STATE_SPLIT still holds a ledger, cards, lessons or knowledge, which a run would miss or write past"
  how="$HERE/move-state.sh --dry-run names what is in both places, or lists what it would move when no name is; keep each file in one place, then run it without the flag"
elif _under_claude "$DEVELOP_STATE_DIR"; then
  why="the working state is under .claude/, where a session that can ask nobody cannot write every file or remove its pass lock"
  # how it gets out: the script for a 0.11 layout, develop-init for the legacy folder, the person for anything else
  case $DEVELOP_STATE_DIR in
    */.claude/90north-develop) how="$HERE/move-state.sh moves it, once (--dry-run shows what would move)" ;;
    */.claude/defect-loop) how="/90north-develop:develop-init sets up the folder outside .claude/ (it migrates a legacy .claude/defect-loop/)" ;;
    "${DEVELOP_DIR%/.claude/90north-develop}/.90north-develop") how="the project itself sits under a folder named .claude: set DEVELOP_STATE_DIR to a folder outside it" ;;
    *) how="DEVELOP_STATE_DIR or a link leads there: name a folder outside .claude/" ;;
  esac
fi
if [ -n "$why" ]; then
  if [ "$auto" -eq 1 ]; then
    echo "where: an unattended pass is refused here — $why. $how" >&2
    exit 3
  fi
  echo "NOTE=$why: $how"
elif [ "$auto" -eq 1 ] && [ ! -d "$DEVELOP_STATE_DIR" ]; then
  echo "where: an unattended pass is refused here — the working state folder $DEVELOP_STATE_DIR does not exist, so the pass could not record its work. /90north-develop:develop-init writes it; a DEVELOP_STATE_DIR must name a folder that is there" >&2
  exit 2
fi
