"""Local board backend (TRACKER=local), reached through tracker.sh: the file shell around local_board_core.

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
pass lock keeps it so."""
from __future__ import annotations

import datetime as dt
import os
import re
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import local_board_core as core  # noqa: E402

STATUSES = "todo,in-progress,need-info,review,ready-for-qa,reopened,done"
KEY = re.compile(r"[A-Za-z][A-Za-z0-9_]*-[0-9]+\Z")


class Usage(Exception):
    pass


def usage(form):
    return Usage("usage: tracker.sh " + form)


def board_dir():
    dl = os.environ["DEVELOP_DIR"]
    board = os.environ.get("LOCAL_BOARD") or os.path.join(dl, "board")
    board = os.path.join(dl, board)
    if not os.path.isdir(board):
        raise core.BoardError("no board folder at %s (LOCAL_BOARD in tracker.env)" % board)
    return board


def statuses():
    return [s.strip() for s in (os.environ.get("LOCAL_STATUSES") or STATUSES).split(",") if s.strip()]


def now():
    return dt.datetime.now().replace(second=0, microsecond=0)


def key_arg(key):
    if not KEY.match(key):
        raise Usage("%r is not a card key like TASK-12" % key)
    return key


def load(board, key):
    path = os.path.join(board, key + ".md")
    if not os.path.isfile(path):
        raise core.BoardError("no card %s at %s" % (key, path))
    with open(path, encoding="utf-8") as fh:
        return core.parse_card(key, fh.read())


def save(board, card):
    path = os.path.join(board, card["key"] + ".md")
    mode = os.stat(path).st_mode & 0o777 if os.path.exists(path) else 0o644
    fd, tmp = tempfile.mkstemp(prefix="." + card["key"] + ".", suffix=".tmp", dir=board)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(core.render_card(card))
        os.chmod(tmp, mode)
        os.replace(tmp, path)
    except BaseException:
        os.unlink(tmp)
        raise


def all_cards(board):
    """Every readable card; an unreadable one is reported on stderr and skipped, so one bad file stops nothing."""
    cards = []
    for name in sorted(os.listdir(board)):
        if name.endswith(".md") and KEY.match(name[:-3]):
            try:
                cards.append(load(board, name[:-3]))
            except core.BoardError as e:
                print("WARN %s skipped: %s" % (name, e), file=sys.stderr)
    return cards


def inside(board, rel):
    real = os.path.realpath(board)
    return os.path.realpath(os.path.join(board, rel)).startswith(real + os.sep)


def names_arg(args, at):
    if len(args) <= at:
        return []
    names = args[at].split(",")
    if not all(core.is_name(n) for n in names):
        raise Usage("field names are comma-separated, like severity,acceptance-criteria")
    return names


# -- verbs --------------------------------------------------------------------------------------------------------
def cmd_search(board, args):
    if len(args) not in (1, 2):
        raise usage("search '<query>' [name,…]")
    query, extra = core.parse_query(args[0]), names_arg(args, 1)
    hits = core.sort_cards([c for c in all_cards(board) if core.matches(c, query, now())], query)
    for c in hits:
        print(core.summary_line(c) + "".join(" | %s=%s" % (n, core.field_text(c, n)) for n in extra))
    print("# %d issue(s)" % len(hits), file=sys.stderr)


def cmd_get(board, args):
    if len(args) != 1:
        raise usage("get KEY")
    key = key_arg(args[0])
    load(board, key)
    with open(os.path.join(board, key + ".md"), encoding="utf-8") as fh:
        sys.stdout.write(fh.read())
    files = os.path.join(board, key)
    names = sorted(os.listdir(files)) if os.path.isdir(files) else []
    print("ATTACHMENTS: " + (", ".join("%s/%s" % (key, n) for n in names) or "(none)"))


def cmd_card(board, args):
    if len(args) not in (1, 2):
        raise usage("card KEY [name,…]")
    c = load(board, key_arg(args[0]))
    f = c["fields"]
    print("%s  [%s / %s]" % (c["key"], f.get("type", ""), f.get("status", "")))
    print("LABELS: " + (", ".join(f.get("labels", [])) or "(none)"))
    for link in f.get("links", []):
        if KEY.match(link) and os.path.isfile(os.path.join(board, link + ".md")):
            other = load(board, link)["fields"]
            print("LINK: %s [%s] %s" % (link, other.get("status", "?"), other.get("title", "")))
        else:
            print("LINK: %s [?] (no card)" % link)
    for name in names_arg(args, 1):
        print("FIELD %s: %s" % (name, core.field_text(c, name) or "(empty)"))


EDIT_FORM = "edit KEY [--dry-run] (--add-label L | --remove-label L | --field N=V | --field-md H=FILE)…"


def edit_change(rest):
    """The edit flags, in pairs, as one core.Change."""
    if not rest or len(rest) % 2:
        raise usage(EDIT_FORM)
    add, remove, fields, sections = [], [], {}, {}
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
            with open(val, encoding="utf-8") as fh:
                sections[name.strip()] = fh.read()
    return core.Change(add, remove, fields, sections)


def cmd_edit(board, args):
    if not args:
        raise usage(EDIT_FORM)
    key, dry = key_arg(args[0]), "--dry-run" in args[1:]
    new = core.edit(load(board, key), edit_change([a for a in args[1:] if a != "--dry-run"]), now())
    if dry:
        sys.stdout.write(core.render_card(new))
        return
    save(board, new)
    print(core.summary_line(new))


def cmd_transition(board, args):
    if len(args) != 2:
        raise usage("transition KEY STATUS | transition KEY --list")
    c = load(board, key_arg(args[0]))
    if args[1] == "--list":
        current = c["fields"].get("status", "").lower()
        for s in statuses():
            print(s + ("  ← now" if s.lower() == current else ""))
        return
    new = core.transition(c, args[1], statuses(), now())
    save(board, new)
    print("%s: %s → %s" % (c["key"], c["fields"].get("status", ""), new["fields"]["status"]))


def cmd_comment(board, args):
    if len(args) not in (2, 3):
        raise usage("comment KEY comment.md [cN]")
    key = key_arg(args[0])
    with open(args[1], encoding="utf-8") as fh:
        text = fh.read()
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


def cmd_attach(board, args):
    if len(args) < 2:
        raise usage("attach KEY FILE…")
    key = key_arg(args[0])
    load(board, key)
    dest = os.path.join(board, key)
    os.makedirs(dest, exist_ok=True)
    for src in args[1:]:
        name = os.path.basename(src)
        if os.path.exists(os.path.join(dest, name)):
            raise core.BoardError("%s/%s exists: attach under a new name, a take is never overwritten" % (key, name))
        shutil.copy2(src, os.path.join(dest, name))
        print("attached %s → %s/%s %d bytes" % (name, key, name, os.path.getsize(os.path.join(dest, name))))


def cmd_download(board, args):
    if len(args) < 2:
        raise usage("download KEY NEW-DIR [NAME…]")
    key, out = key_arg(args[0]), args[1]
    src = os.path.join(board, key)
    if os.path.isdir(out) and os.listdir(out):
        raise core.BoardError("%s is not empty: download into a new folder" % out)
    names = [os.path.basename(n) for n in args[2:]] or (sorted(os.listdir(src)) if os.path.isdir(src) else [])
    os.makedirs(out, exist_ok=True)
    for name in names:
        shutil.copy2(os.path.join(src, name), os.path.join(out, name))
        print("downloaded %s/%s → %s" % (key, name, os.path.join(out, name)))


VERBS = {"search": cmd_search, "get": cmd_get, "card": cmd_card, "edit": cmd_edit, "transition": cmd_transition,
         "comment": cmd_comment, "attach": cmd_attach, "download": cmd_download}


def main(argv):
    if not argv or argv[0] not in VERBS:
        print("usage: tracker.sh <%s> …" % "|".join(VERBS), file=sys.stderr)
        return 2
    try:
        VERBS[argv[0]](board_dir(), argv[1:])
    except Usage as e:
        print(e, file=sys.stderr)
        return 2
    except (core.BoardError, OSError) as e:
        print("error: %s" % e, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
