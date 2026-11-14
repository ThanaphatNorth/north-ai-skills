#!/bin/bash
# Prints a project's two folders, one per line:   where.sh [--auto]
#   DC=<settings: config.md, tracker.env>
#   DL=<working state: the ledgers, lessons.md, the board, knowledge/, runs/>
# and a NOTE= line when the working state is under .claude/ (not moved yet, or a legacy folder).
# A loop reads the folders from here and never builds the paths by hand: a project set up before 0.12 has both in
# one place until move-state.sh has run, and writing to the other place would split its state in two.
# --auto is how an unattended pass asks. Under .claude/ a session that can ask nobody writes some files and is
# refused others, and cannot remove its own pass lock, so a pass that starts there ends half done. With --auto a
# project whose working state is under .claude/ is refused: the folders are still printed, the reason goes to
# stderr, exit 3.
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
# how the working state gets out of .claude/: the script for a 0.11 layout, develop-init for anything else there
# (the legacy .claude/defect-loop/, or a DEVELOP_STATE_DIR that names a folder under .claude/)
case $DEVELOP_STATE_DIR in
  */.claude/90north-develop) how="$HERE/move-state.sh moves it, once (--dry-run shows what would move)" ;;
  */.claude/*) how="/90north-develop:develop-init sets up the folder outside .claude/ (it migrates a legacy .claude/defect-loop/)" ;;
  *) exit 0 ;;
esac
if [ "$auto" -eq 1 ]; then
  echo "where: an unattended pass is refused here — the working state is under .claude/, where a session that can ask nobody cannot write every file or remove its pass lock. $how" >&2
  exit 3
fi
echo "NOTE=the working state is still under .claude/, where a session that can ask nobody cannot write: $how"
