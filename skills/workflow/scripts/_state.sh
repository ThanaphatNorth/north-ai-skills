#!/bin/bash
# Shared by every tracker script: finds the project's state folder and reads tracker.env. Sourced, never run.
# DEVELOP_DIR, else the legacy DEFECT_LOOP_DIR, else the nearest .claude/90north-develop/ (or legacy
# .claude/defect-loop/) above $PWD that holds tracker.env. A folder found inside a linked git worktree maps to the
# same path in the main checkout when that one has tracker.env too, so every worktree reads and writes one board.
# Leaves DEVELOP_DIR exported and TRACKER set (jira when tracker.env has no TRACKER line).
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

DEVELOP_DIR=${DEVELOP_DIR:-${DEFECT_LOOP_DIR:-}}
if [ -z "$DEVELOP_DIR" ]; then
  d=$PWD
  while [ "$d" != "/" ] && [ -z "$DEVELOP_DIR" ]; do
    for sub in .claude/90north-develop .claude/defect-loop; do
      if [ -f "$d/$sub/tracker.env" ]; then DEVELOP_DIR="$d/$sub"; break; fi
    done
    d=$(dirname "$d")
  done
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
