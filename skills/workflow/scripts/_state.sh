#!/bin/bash
# Shared by every tracker script: finds the project's two folders and reads tracker.env. Sourced, never run.
# Settings (config.md, tracker.env): DEVELOP_DIR, else the legacy DEFECT_LOOP_DIR, else the nearest
# .claude/90north-develop/ (or legacy .claude/defect-loop/) above $PWD that holds tracker.env. A folder found inside
# a linked git worktree maps to the same path in the main checkout when that one has tracker.env too, so every
# worktree reads and writes one board; a worktree with no copy of the settings (git does not track them) finds
# them in the main checkout.
# Working state (ledgers, lessons, board, knowledge, runs): DEVELOP_STATE_DIR, else .90north-develop/ beside the
# project's .claude/. It sits outside .claude/ because a session that can ask nobody may not write there.
# A project set up before 0.12 (or a legacy one) still has it in the settings folder, and is read there until
# move-state.sh has run: the folder that holds a ledger (or, with no ledger, cards on the board) is the one in
# use, so a stray file written to the other place, or a leftover there, never hides the real state.
# Both folders are absolute, physical paths, however they were named. where.sh prints them.
# Leaves DEVELOP_DIR, DEVELOP_STATE_DIR and DEVELOP_STATE_SPLIT (the old place, when it still keeps a record)
# exported, and TRACKER set (jira when tracker.env has no TRACKER line).
# tracker.env is committed with the project, so it is read as text and never run: read_settings takes the lines of
# the settings it is asked for and nothing else. _env.sh reads the credentials file with the same function.
set -euo pipefail

# _setting_value <text after NAME=>: the value, in SETTING_VALUE. 'single quoted' is taken as it is;
# "double quoted" turns \\ \" \$ \` back into the character (the shell's rule, with nothing expanded);
# a bare value ends at the first blank. Whatever follows the value on the line is ignored.
_setting_value() {
  local s=$1 c out=""
  case $s in
    \'*) s=${s#\'}; out=${s%%\'*} ;;
    \"*)
      s=${s#\"}
      while [ -n "$s" ]; do
        c=${s:0:1}; s=${s:1}
        case $c in
          \") break ;;
          \\) case ${s:0:1} in \\ | \" | \$ | \`) c=${s:0:1}; s=${s:1} ;; esac ;;
        esac
        out+=$c
      done ;;
    *) out=${s%%[[:space:]]*} ;;
  esac
  SETTING_VALUE=$out
}

# read_settings <file> <NAME>…: sets each named variable from its `NAME=value` line (an `export ` prefix is allowed,
# the last line of a name wins) and leaves a name the file does not set as it was. Every other line is skipped; no
# line is run and nothing in a value is expanded: $(…), $VAR and ~ stay text.
read_settings() {
  local file=$1 line name
  shift
  while IFS= read -r line || [ -n "$line" ]; do
    line=${line#"${line%%[![:space:]]*}"}
    case $line in export[[:space:]]*) line=${line#export}; line=${line#"${line%%[![:space:]]*}"} ;; esac
    for name in "$@"; do
      case $line in
        "$name="*) _setting_value "${line#"$name="}"; printf -v "$name" '%s' "$SETTING_VALUE" ;;
      esac
    done
  done < "$file"
  unset SETTING_VALUE
}

# _phys <path>: the path made absolute and physical, in PHYS. Links are followed and a trailing slash is dropped for
# the part that exists; a part that does not exist yet is kept as it was written. Both folders go through it, so a
# relative name, a link or a trailing slash never changes which place is in use or hides a folder under .claude/.
_phys() {
  local p=$1 rest="" here
  case $p in /*) ;; *) p=$PWD/$p ;; esac
  while :; do
    while [ "$p" != "/" ] && [ "${p%/}" != "$p" ]; do p=${p%/}; done
    if here=$(cd -P -- "$p" 2>/dev/null && pwd -P); then break; fi
    rest=/${p##*/}$rest
    p=${p%/*}
    [ -n "$p" ] || p=/
  done
  [ "$here" != "/" ] || here=""
  PHYS=$here$rest
  [ -n "$PHYS" ] || PHYS=/
}

# _under_claude <path>: true when one of its folders is named .claude, in any letter case (a disk may ignore case)
_under_claude() {
  local lower
  lower=$(printf '%s' "$1" | tr '[:upper:]' '[:lower:]')
  case $lower in */.claude | */.claude/*) return 0 ;; esac
  return 1
}

# _settings_above <folder>: the nearest settings folder at or above it, in DEVELOP_DIR (left empty when none is)
_settings_above() {
  local d=$1 sub
  while [ "$d" != "/" ] && [ -z "$DEVELOP_DIR" ]; do
    for sub in .claude/90north-develop .claude/defect-loop; do
      if [ -f "$d/$sub/tracker.env" ]; then DEVELOP_DIR="$d/$sub"; break; fi
    done
    d=$(dirname "$d")
  done
}

DEVELOP_DIR=${DEVELOP_DIR:-${DEFECT_LOOP_DIR:-}}
if [ -n "$DEVELOP_DIR" ]; then
  [ -f "$DEVELOP_DIR/tracker.env" ] || { echo "DEVELOP_DIR names $DEVELOP_DIR, which holds no tracker.env — name the project's .claude/90north-develop/ folder, or run /90north-develop:develop-init" >&2; exit 2; }
  _phys "$DEVELOP_DIR"
  DEVELOP_DIR=$PHYS
else
  _settings_above "$PWD"
  if [ -z "$DEVELOP_DIR" ]; then
    # settings git does not track are not in a linked worktree: look from the same folder of the main checkout
    top=$(git rev-parse --show-toplevel 2>/dev/null || true)
    common=$(git rev-parse --path-format=absolute --git-common-dir 2>/dev/null || true)
    if [ -n "$top" ] && [ "${common##*/}" = ".git" ] && [ "${common%/.git}" != "$top" ]; then
      here=$(pwd -P)
      _settings_above "${common%/.git}${here#"$top"}"
    fi
  fi
  [ -n "$DEVELOP_DIR" ] || { echo "no .claude/90north-develop/tracker.env above $PWD — run /90north-develop:develop-init, or set DEVELOP_DIR" >&2; exit 2; }
  case $DEVELOP_DIR in */.claude/defect-loop) echo "note: legacy state folder $DEVELOP_DIR — /90north-develop:develop-init migrates it" >&2 ;; esac
  DEVELOP_DIR=$(cd "$DEVELOP_DIR" && pwd -P)
  top=$(git -C "$DEVELOP_DIR" rev-parse --show-toplevel 2>/dev/null || true)
  common=$(git -C "$DEVELOP_DIR" rev-parse --path-format=absolute --git-common-dir 2>/dev/null || true)
  if [ -n "$top" ] && [ "${common##*/}" = ".git" ] && [ "${common%/.git}" != "$top" ]; then
    shared="${common%/.git}/${DEVELOP_DIR#"$top"/}"
    if [ -f "$shared/tracker.env" ]; then DEVELOP_DIR=$shared; fi
  fi
fi
export DEVELOP_DIR
# The backend and its settings come from tracker.env only, never from the calling shell.
# A site taken from the environment would send the token to whoever set that variable.
# shellcheck disable=SC2034  # read by tracker.sh and _env.sh, which source this file
TRACKER="" LOCAL_BOARD="" LOCAL_STATUSES="" JIRA_SITE="" JIRA_ENV_FILE=""
read_settings "$DEVELOP_DIR/tracker.env" TRACKER JIRA_SITE JIRA_ENV_FILE LOCAL_BOARD LOCAL_STATUSES
TRACKER=${TRACKER:-jira}
# a board under the home folder: the one expansion a path setting keeps (jira_state does it for JIRA_ENV_FILE)
case $LOCAL_BOARD in \~/*) LOCAL_BOARD=$HOME/${LOCAL_BOARD#\~/} ;; esac

# _holds <folder> <name>…: true when the folder holds one of the names with something in it: a file that is not
# empty, or a folder with such a file anywhere inside, links followed. A folder that cannot be looked into all the
# way counts too (find says so on stderr), since nothing shows it is empty. An empty file, an empty folder or
# folders that hold only empty folders are leftovers, not state: git leaves an untracked empty folder behind in
# every clone when the rest moves, and it must never decide anything.
_holds() {
  local folder=$1 name path
  shift
  for name in "$@"; do
    path=$folder/$name
    if [ -d "$path" ]; then
      if [ ! -r "$path" ] || [ -n "$(find -L "$path" -type f -size +0c -print 2>&1 | head -n 1)" ]; then return 0; fi
    elif [ -s "$path" ]; then
      return 0
    fi
  done
  return 1
}
# _ledger <folder>: true when it holds a ledger with something in it
_ledger() { [ -s "$1/dev-ledger.md" ] || [ -s "$1/defect-ledger.md" ]; }

# _cards <board folder>: true when it holds a card, by the local board's own rule for a card's file name
# (local_board_files.KEY owns it; tests/test_state.py holds the two to the same names). A README, a keep file or
# a folder that cannot be listed is not a card.
_cards() {
  local LC_ALL=C path name
  for path in "$1"/*-*.md; do
    name=${path##*/}
    if [ -f "$path" ] && [[ $name =~ ^[A-Za-z][A-Za-z0-9_]*-[0-9]+\.md$ ]]; then return 0; fi
  done
  return 1
}

# _kept <old folder> <board>: true when a record a loop keeps is there: a ledger, cards, lessons or knowledge.
# Run files are hand-offs between passes, not records, and a stray run folder is a leftover.
_kept() { _ledger "$1" || _cards "$1/$2" || _holds "$1" ai-ledger.md lessons.md knowledge; }

# Which place is in use. A ledger decides; with no ledger anywhere, a board that holds cards does; with neither,
# the old place only when something else is kept there (a new project has nothing, and starts beside the project).
# When the new place is the one read and the old one still keeps a record, DEVELOP_STATE_SPLIT names the old one:
# where.sh says so and refuses an unattended pass, since a pass would miss those records or write past them.
DEVELOP_STATE_SPLIT=""
if [ -n "${DEVELOP_STATE_DIR:-}" ]; then
  _phys "$DEVELOP_STATE_DIR"
  DEVELOP_STATE_DIR=$PHYS
else
  DEVELOP_STATE_DIR=$DEVELOP_DIR
  case $DEVELOP_DIR in
    */.claude/90north-develop)
      beside="${DEVELOP_DIR%/.claude/90north-develop}/.90north-develop"
      board=board
      case $LOCAL_BOARD in "" | /* | *..*) ;; *) board=$LOCAL_BOARD ;; esac
      if _ledger "$beside"; then
        DEVELOP_STATE_DIR=$beside
        if _kept "$DEVELOP_DIR" "$board"; then DEVELOP_STATE_SPLIT=$DEVELOP_DIR; fi
      elif _ledger "$DEVELOP_DIR"; then
        :
      elif _cards "$beside/$board"; then
        DEVELOP_STATE_DIR=$beside
        if _kept "$DEVELOP_DIR" "$board"; then DEVELOP_STATE_SPLIT=$DEVELOP_DIR; fi
      elif _cards "$DEVELOP_DIR/$board"; then
        :
      elif ! _holds "$DEVELOP_DIR" ai-ledger.md lessons.md knowledge runs "$board"; then
        DEVELOP_STATE_DIR=$beside
      fi
      # a folder beside the project may itself be a link: the door reads where it really leads
      _phys "$DEVELOP_STATE_DIR"
      DEVELOP_STATE_DIR=$PHYS ;;
  esac
fi
export DEVELOP_STATE_DIR DEVELOP_STATE_SPLIT
