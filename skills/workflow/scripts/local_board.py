"""Local board backend (TRACKER=local), reached through tracker.sh: the command line over the core and the file module.

  tracker.sh search '<query>' [name,…]   KEY | type | status | labels | updated | title (count on stderr)
  tracker.sh get KEY                     the card file, then ATTACHMENTS
  tracker.sh card KEY [name,…]           KEY [type / status], LABELS, LINK …, FIELD name: value
  tracker.sh edit KEY [--dry-run] (--add-label L | --remove-label L | --field NAME=VALUE | --field-md HEADING=FILE)…
  tracker.sh transition KEY STATUS | --list
  tracker.sh comment KEY comment.md [cN] appends (or replaces the loop's cN), reads it back; exit 1 on a bad video
  tracker.sh attach KEY FILE…            copies into <board>/KEY/ and prints the path for `::video <path>`
  tracker.sh download KEY NEW-DIR [NAME…]
Board: LOCAL_BOARD (absolute, or relative to DEVELOP_DIR), else <DEVELOP_DIR>/board.
Statuses: LOCAL_STATUSES, else todo,in-progress,need-info,review,ready-for-qa,reopened,done.
Writes are atomic (a fresh temp file, then rename) and keep the card's file mode. One writer at a time: the loops'
pass lock keeps it so. A card, an attachment or a video that is a link leaving the board folder is refused.
A refused call prints one line on stderr and exits 1, or 2 for wrong usage."""
from __future__ import annotations

import datetime as dt
import io
import os
import shutil
import sys
from typing import Callable, Dict, List

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import local_board_core as core  # noqa: E402
from local_board_files import KEY, all_cards, card_path, files_dir, inside, load, read_text, save  # noqa: E402

STATUSES = "todo,in-progress,need-info,review,ready-for-qa,reopened,done"


class Usage(Exception):
    """A call with the wrong arguments; main prints its message and exits 2."""


def usage(form: str) -> Usage:
    """The Usage error that shows one verb's argument form."""
    return Usage("usage: tracker.sh " + form)


def board_dir() -> str:
    """The board folder from DEVELOP_DIR and LOCAL_BOARD; refuses one that is absent or cannot be read."""
    dl = os.environ.get("DEVELOP_DIR")
    if not dl:
        raise Usage("DEVELOP_DIR is not set: call tracker.sh, which finds the project's state folder")
    board = os.path.join(dl, os.environ.get("LOCAL_BOARD") or "board")
    if not os.path.isdir(board):
        raise core.BoardError("no board folder at %s (LOCAL_BOARD in tracker.env)" % board)
    if not os.access(board, os.R_OK | os.X_OK):
        raise core.BoardError("board folder %s is not readable: check its permissions" % board)
    return board


def statuses() -> List[str]:
    """The statuses `transition` accepts: LOCAL_STATUSES, or the default list when that is empty."""
    return [s.strip() for s in (os.environ.get("LOCAL_STATUSES") or STATUSES).split(",") if s.strip()]


def now() -> dt.datetime:
    """The local time cut to the minute, the precision a card stores."""
    return dt.datetime.now().replace(second=0, microsecond=0)


def key_arg(key: str) -> str:
    """`key` when it has the shape TASK-12, which cannot hold a path; a Usage error otherwise."""
    if not KEY.match(key):
        raise Usage("%r is not a card key like TASK-12" % key)
    return key


def names_arg(args: List[str], at: int) -> List[str]:
    """The field names in the optional argument `at` ([] when it is not given); a Usage error for a bad name."""
    if len(args) <= at:
        return []
    names = args[at].split(",")
    if not all(core.is_name(n) for n in names):
        raise Usage("field names are comma-separated, like severity,acceptance-criteria")
    return names


# -- verbs --------------------------------------------------------------------------------------------------------
def cmd_search(board: str, args: List[str]) -> None:
    """Print one summary line per matching card, in the query's order, and the count on stderr."""
    if len(args) not in (1, 2):
        raise usage("search '<query>' [name,…]")
    query, extra = core.parse_query(args[0]), names_arg(args, 1)
    hits = core.sort_cards([c for c in all_cards(board) if core.matches(c, query, now())], query)
    for c in hits:
        print(core.summary_line(c) + "".join(" | %s=%s" % (n, core.field_text(c, n)) for n in extra))
    print("# %d issue(s)" % len(hits), file=sys.stderr)


def cmd_get(board: str, args: List[str]) -> None:
    """Print the card's text, then the ATTACHMENTS line; nothing is printed for a card that does not parse."""
    if len(args) != 1:
        raise usage("get KEY")
    key = key_arg(args[0])
    text = read_text(card_path(board, key), "card")
    core.parse_card(key, text)
    files = files_dir(board, key)
    names = sorted(os.listdir(files)) if os.path.isdir(files) else []
    print(text, end="")
    print("ATTACHMENTS: " + (", ".join("%s/%s" % (key, n) for n in names) or "(none)"))


def cmd_card(board: str, args: List[str]) -> None:
    """Print the card's type, status and labels, each linked card's status and title, then the named fields."""
    if len(args) not in (1, 2):
        raise usage("card KEY [name,…]")
    key, names = key_arg(args[0]), names_arg(args, 1)
    c = load(board, key)
    print("%s  [%s / %s]" % (c["key"], core.header(c, "type"), core.header(c, "status")))
    print("LABELS: " + (core.header(c, "labels") or "(none)"))
    for link in core.listed(c, "links"):
        if KEY.match(link) and os.path.isfile(os.path.join(board, link + ".md")):
            other = load(board, link)
            status = core.header(other, "status") if "status" in other["fields"] else "?"
            print("LINK: %s [%s] %s" % (link, status, core.header(other, "title")))
        else:
            print("LINK: %s [?] (no card)" % link)
    for name in names:
        print("FIELD %s: %s" % (name, core.field_text(c, name) or "(empty)"))


EDIT_FORM = "edit KEY [--dry-run] (--add-label L | --remove-label L | --field N=V | --field-md H=FILE)…"


def edit_change(rest: List[str]) -> core.Change:
    """The edit flags, in pairs, as one core.Change."""
    if not rest or len(rest) % 2:
        raise usage(EDIT_FORM)
    add: List[str] = []
    remove: List[str] = []
    fields: Dict[str, str] = {}
    sections: Dict[str, str] = {}
    for flag, value in zip(rest[::2], rest[1::2]):
        if flag in ("--add-label", "--remove-label"):
            (add if flag == "--add-label" else remove).append(value)
            continue
        name, sep, val = value.partition("=")
        if flag not in ("--field", "--field-md") or not sep or not name.strip():
            raise usage(EDIT_FORM)
        if flag == "--field":
            fields[name.strip()] = val
        else:
            sections[name.strip()] = read_text(val, "--field-md file")
    return core.Change(add, remove, fields, sections)


def cmd_edit(board: str, args: List[str]) -> None:
    """Apply the edit flags and print the card's summary line; with --dry-run print the new card, write nothing."""
    if not args:
        raise usage(EDIT_FORM)
    key, dry = key_arg(args[0]), "--dry-run" in args[1:]
    new = core.edit(load(board, key), edit_change([a for a in args[1:] if a != "--dry-run"]), now())
    if dry:
        print(core.render_card(new), end="")
        return
    save(board, new)
    print(core.summary_line(new))


def cmd_transition(board: str, args: List[str]) -> None:
    """Move the card to a listed status and print `KEY: old → new`; with --list print the statuses instead."""
    if len(args) != 2:
        raise usage("transition KEY STATUS | transition KEY --list")
    c = load(board, key_arg(args[0]))
    if args[1] == "--list":
        current = core.header(c, "status").lower()
        for s in statuses():
            print(s + ("  ← now" if s.lower() == current else ""))
        return
    new = core.transition(c, args[1], statuses(), now())
    save(board, new)
    print("%s: %s → %s" % (c["key"], core.header(c, "status"), core.header(new, "status")))


def cmd_comment(board: str, args: List[str]) -> None:
    """Append or replace the loop's comment and print its id; nothing is written when a video is missing or outside."""
    if len(args) not in (2, 3):
        raise usage("comment KEY comment.md [cN]")
    key = key_arg(args[0])
    text = read_text(args[1], "comment file")
    new, cid = core.add_comment(load(board, key), text, now(), args[2] if len(args) == 3 else None)
    videos = core.video_paths([c for c in new["comments"] if c["id"] == cid][0]["text"])
    outside = [p for p in videos if not inside(board, p)]
    missing = [p for p in videos if p not in outside and not os.path.isfile(os.path.join(board, p))]
    if outside or missing:
        problems = (["missing " + ", ".join(missing)] if missing else []) + \
                   (["outside the board: " + ", ".join(outside)] if outside else [])
        raise core.BoardError("nothing written (%s): `tracker.sh attach %s FILE` and use the path it prints"
                              % ("; ".join(problems), key))
    save(board, new)
    posted = [c for c in load(board, key)["comments"] if c["id"] == cid][0]["text"]
    print("comment %s on %s · videos %d · missing none" % (cid, key, len(core.video_paths(posted))))


def cmd_attach(board: str, args: List[str]) -> None:
    """Copy the files into <board>/KEY/ and print each new path; every file is checked before the first is copied."""
    if len(args) < 2:
        raise usage("attach KEY FILE…")
    key = key_arg(args[0])
    load(board, key)
    dest = files_dir(board, key)
    names = [os.path.basename(src) for src in args[1:]]
    taken = "%s/%s exists: attach under a new name, a take is never overwritten"
    for src, name in zip(args[1:], names):
        if os.path.isdir(src) or not os.access(src, os.R_OK):
            raise core.BoardError("%s is not a file this user can read: nothing was attached" % src)
        if names.count(name) > 1:
            raise core.BoardError("%s is given twice: attach each take under its own name" % name)
        if os.path.lexists(os.path.join(dest, name)):
            raise core.BoardError(taken % (key, name))
    os.makedirs(dest, exist_ok=True)
    for src, name in zip(args[1:], names):
        target = os.path.join(dest, name)
        if os.path.lexists(target):  # a name the volume folds onto one just copied (case, accents)
            raise core.BoardError(taken % (key, name))
        try:
            shutil.copy2(src, target)
        except OSError:
            if os.path.lexists(target):
                os.unlink(target)  # half a take would answer "exists" to the retry
            raise
        print("attached %s → %s/%s %d bytes" % (name, key, name, os.path.getsize(target)))


def cmd_download(board: str, args: List[str]) -> None:
    """Copy the card's attachments (all, or the named ones) into a new or empty folder and print each path."""
    if len(args) < 2:
        raise usage("download KEY NEW-DIR [NAME…]")
    key, out = key_arg(args[0]), args[1]
    src = files_dir(board, key)
    if not os.path.isdir(src):
        card_path(board, key)  # a card with no attachments gives an empty folder; a key with neither is refused
    if os.path.isdir(out) and os.listdir(out):
        raise core.BoardError("%s is not empty: download into a new folder" % out)
    names = [os.path.basename(n) for n in args[2:]] or (sorted(os.listdir(src)) if os.path.isdir(src) else [])
    for name in names:
        if not os.path.isfile(os.path.join(src, name)) or not inside(board, os.path.join(key, name)):
            raise core.BoardError("no attachment file %s/%s: nothing was downloaded" % (key, name))
    os.makedirs(out, exist_ok=True)
    for name in names:
        shutil.copy2(os.path.join(src, name), os.path.join(out, name))
        print("downloaded %s/%s → %s" % (key, name, os.path.join(out, name)))


VERBS: Dict[str, Callable[[str, List[str]], None]] = {
    "search": cmd_search, "get": cmd_get, "card": cmd_card, "edit": cmd_edit, "transition": cmd_transition,
    "comment": cmd_comment, "attach": cmd_attach, "download": cmd_download}


def main(argv: List[str]) -> int:
    """Run one verb; returns the exit code: 0 done, 1 refused or failed (one line on stderr), 2 wrong usage."""
    out = sys.stdout
    if isinstance(out, io.TextIOWrapper) and out.errors == "strict":
        out.reconfigure(errors="backslashreplace")  # a character this stdout cannot encode prints as an escape
    if not argv or argv[0] not in VERBS:
        print("usage: tracker.sh <%s> …" % "|".join(VERBS), file=sys.stderr)
        return 2
    code, said = 0, ""
    try:
        VERBS[argv[0]](board_dir(), argv[1:])
    except Usage as e:
        code, said = 2, str(e)
    except (core.BoardError, OSError) as e:
        code, said = 1, "error: " + "\\n".join(str(e).splitlines())  # echoed input cannot add a line
    try:
        print(end="", flush=True)  # here, so a stdout that fails is one line and not the interpreter's at exit
    except OSError as e:
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())  # drop what is still buffered
        if not code:
            code, said = 1, "error: %s finished, but its output could not be written: %s" % (argv[0], e.strerror)
    try:
        if said:
            print(said, file=sys.stderr)
    except OSError:  # nobody reads stderr either: drop the line and what that stream still holds
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stderr.fileno())
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
