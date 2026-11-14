#!/bin/bash
# Moves a project's working state out of .claude/, once:   move-state.sh [--dry-run]
# A project set up before 0.12 keeps everything in .claude/90north-develop/. Claude Code treats .claude/ as
# sensitive, so a session that can ask nobody cannot write the loop's own files there. This script moves what a loop
# writes as it works (the ledgers, lessons.md, the board, knowledge/ and runs/) to .90north-develop/ beside the
# project. config.md and tracker.env stay where they are: they hold the push approval and the tracker's address, and
# keep the protection.
# Nothing is copied, overwritten or deleted. Files git tracks are moved with `git mv`, so they show as renames.
# --dry-run lists what would move and changes nothing. Run it from inside the project, with no pass running.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
dry=0
case ${1:-} in
  "") ;;
  --dry-run) dry=1 ;;
  *) echo "usage: $0 [--dry-run]" >&2; exit 2 ;;
esac
[ $# -le 1 ] || { echo "usage: $0 [--dry-run]" >&2; exit 2; }
# shellcheck source=_state.sh
. "$HERE/_state.sh"
case $DEVELOP_DIR in
  */.claude/90north-develop) ;;
  *) echo "move-state: $DEVELOP_DIR is not a .claude/90north-develop/ folder — run /90north-develop:develop-init first, which migrates a legacy setup" >&2; exit 2 ;;
esac
old=$DEVELOP_DIR
root=${old%/.claude/90north-develop}
new="$root/.90north-develop"

names=(dev-ledger.md defect-ledger.md ai-ledger.md lessons.md knowledge runs)
# the board: `board`, or the folder tracker.env names. A relative name moves with the rest; an absolute path stays
# where it is; a relative path that climbs out (..) would name another place after the move, so it is refused.
board=${LOCAL_BOARD:-board} kept_board=""
case $board in
  /*) kept_board=$board ;;
  *..*)
    echo "move-state: LOCAL_BOARD=$board climbs out of the state folder, so after the move the same words would name another place — write it as an absolute path in tracker.env, then run again" >&2
    exit 1 ;;
  *) names+=("$board") ;;
esac

if [ -e "$old/runs/.pass.lock" ]; then
  echo "move-state: a pass lock is at $old/runs/.pass.lock — wait for the pass to end (or remove a stale lock), then run again" >&2
  exit 1
fi
todo=() clash=()
for name in "${names[@]}"; do
  [ -e "$old/$name" ] || [ -L "$old/$name" ] || continue
  if [ -e "$new/$name" ] || [ -L "$new/$name" ]; then clash+=("$name"); else todo+=("$name"); fi
done
if [ ${#clash[@]} -gt 0 ]; then
  for name in "${clash[@]}"; do
    echo "move-state: $name exists in both $old and $new — nothing was moved; put the one you want to keep in one place" >&2
  done
  exit 1
fi
if [ ${#todo[@]} -eq 0 ]; then
  echo "move-state: nothing to move — the working state is not under $old"
  exit 0
fi
if [ "$dry" -eq 1 ]; then
  for name in "${todo[@]}"; do echo "would move $old/$name → $new/$name"; done
  echo "config.md and tracker.env stay in $old"
  exit 0
fi

mkdir -p "$new"
tracked() { [ -n "$(git -C "$root" ls-files -- "$1" 2>/dev/null | head -n 1)" ]; }
for name in "${todo[@]}"; do
  mkdir -p "$(dirname "$new/$name")"
  if tracked "$old/$name"; then
    git -C "$root" mv -- "$old/$name" "$new/$name"
  else
    mv -- "$old/$name" "$new/$name"
  fi
  echo "moved $name → $new/$name"
done
echo "config.md and tracker.env stay in $old"
if [ -n "$kept_board" ]; then echo "the board stays at $kept_board (tracker.env names it by an absolute path)"; fi
if [ -f "$root/.gitignore" ]; then
  lines=$(grep -n -F ".claude/90north-develop" "$root/.gitignore" || true)
  if [ -n "$lines" ]; then
    echo "these .gitignore lines still name the old place; change them to .90north-develop/ where they cover the files that moved:"
    echo "$lines"
  fi
fi
