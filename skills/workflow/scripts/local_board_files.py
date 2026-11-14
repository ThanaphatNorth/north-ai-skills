"""File operations of the local board: find, read and write card files and attachment folders.

Every path is checked to lie inside the board folder with its links followed, and a card is written through a
temp file beside it and os.replace, so a failure leaves the old card whole."""
from __future__ import annotations

import os
import re
import sys
import tempfile
from typing import List

import local_board_core as core

KEY = re.compile(r"[A-Za-z][A-Za-z0-9_]*-[0-9]+\Z")
LEAVES = "%s is a link that leaves the board folder"


def inside(board: str, rel: str) -> bool:
    """True when `rel`, with every link followed, lies below the board folder (the folder itself does not)."""
    try:
        return os.path.realpath(os.path.join(board, rel)).startswith(os.path.realpath(board) + os.sep)
    except ValueError:  # a NUL byte in the path
        return False


def read_text(path: str, what: str) -> str:
    """The file's text; a file that is not UTF-8 is a BoardError that names it."""
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except UnicodeDecodeError:
        raise core.BoardError("%s %s is not UTF-8 text" % (what, path))


def card_path(board: str, key: str) -> str:
    """The path of the card's file; refuses a card that is absent or is a link leaving the board."""
    path = os.path.join(board, key + ".md")
    if not os.path.isfile(path):
        raise core.BoardError("no card %s at %s" % (key, path))
    if not inside(board, key + ".md"):
        raise core.BoardError(LEAVES % path)
    return path


def files_dir(board: str, key: str) -> str:
    """The path of the card's attachment folder, which may not exist yet; refuses a link leaving the board."""
    path = os.path.join(board, key)
    if os.path.lexists(path) and not inside(board, key):
        raise core.BoardError(LEAVES % path)
    return path


def load(board: str, key: str) -> core.Card:
    """The parsed card; a BoardError when its file is absent, not UTF-8 or not a card."""
    return core.parse_card(key, read_text(card_path(board, key), "card"))


def save(board: str, card: core.Card) -> None:
    """Write the card through a temp file beside it and os.replace, so a failure leaves the old card whole."""
    path = os.path.join(board, card["key"] + ".md")
    text = core.render_card(card)
    try:
        text.encode("utf-8")
    except UnicodeEncodeError:
        raise core.BoardError("%s: the change holds bytes that are not UTF-8 text; nothing was written" % card["key"])
    try:
        mode = os.stat(path).st_mode & 0o777 if os.path.exists(path) else 0o644
        fd, tmp = tempfile.mkstemp(prefix="." + card["key"] + ".", suffix=".tmp", dir=board)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                fh.write(text)
            os.chmod(tmp, mode)
            os.replace(tmp, path)
        except BaseException:
            os.unlink(tmp)
            raise
    except OSError as e:
        raise core.BoardError("cannot write %s (%s); the card is unchanged" % (path, e.strerror or e))


def all_cards(board: str) -> List[core.Card]:
    """Every readable card; an unreadable one is reported on stderr and skipped, so one bad file stops nothing."""
    cards = []
    for name in sorted(os.listdir(board)):
        if name.endswith(".md") and KEY.match(name[:-3]):
            try:
                cards.append(load(board, name[:-3]))
            except (core.BoardError, OSError) as e:
                print("WARN %s skipped: %s" % (name, e), file=sys.stderr)
    return cards
