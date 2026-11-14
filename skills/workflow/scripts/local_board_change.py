"""Changes to a card of the local board: an edit, a transition, a comment. Each returns a new card.

Nothing here reads files or the clock: the caller passes the time and writes the result. A change is kept only
when the card it renders reads back as the same card."""
from __future__ import annotations

import copy
import datetime as dt
import os
import re
from typing import List, Mapping, NamedTuple, Optional, Sequence, Tuple

from local_board_card import (ENTRY, LISTS, TIME, BoardError, Card, Comment, is_name, listed, number, parse_card,
                              render_card, set_section)

AUTHOR = "90north-develop"
FIXED = LISTS + ("created", "updated", "status")
_LABEL = re.compile(r"[A-Za-z0-9_.:/-]+\Z")
_LINK = re.compile(r"\[video: [^\]]*\]\(([^)]+)\)")
_VIDEO = re.compile(r"^::video[ \t]+(\S+)[ \t]*$", re.M)
_SECTION = re.compile(r"## ")


class Change(NamedTuple):
    """What one edit asks for: labels to add and to remove, header fields to set, body sections to write."""

    add_labels: Sequence[str] = ()
    remove_labels: Sequence[str] = ()
    fields: Optional[Mapping[str, str]] = None
    sections: Optional[Mapping[str, str]] = None


def _stamped(card: Card, now: dt.datetime) -> Card:
    new = copy.deepcopy(card)
    new["fields"]["updated"] = now.strftime(TIME)
    return new


def _refuse_lines(text: str, pattern: re.Pattern[str], why: str) -> None:
    for n, line in enumerate(text.split("\n"), 1):
        if pattern.match(line):
            raise BoardError("line %d %r: %s" % (n, line, why))


def _readable(new: Card) -> Card:
    """The last guard: a change is kept only if the card it renders reads back as the same card."""
    if parse_card(new["key"], render_card(new)) != new:
        raise BoardError("%s: the change would not read back the same; nothing was written" % new["key"])
    return new


def edit(card: Card, change: Change, now: dt.datetime) -> Card:
    """The card after the change, stamped `now`; a BoardError when a label, field or section cannot be stored."""
    new = _stamped(card, now)
    for label in change.add_labels:
        if not _LABEL.match(label):
            raise BoardError("label %r: one word of letters, digits and . _ : / -" % label)
    labels = listed(new, "labels")
    labels.extend(lb for lb in dict.fromkeys(change.add_labels) if lb not in labels)
    new["fields"]["labels"] = [lb for lb in labels if lb not in set(change.remove_labels)]
    for name, value in (change.fields or {}).items():
        if not is_name(name) or name in FIXED:
            raise BoardError("field %r cannot be set (labels via --add-label/--remove-label, status via transition; "
                             "%s are kept by the board)" % (name, ", ".join(FIXED)))
        if "\n" in value or "\r" in value:
            raise BoardError("field %r: one line only; put longer text in a section with --field-md" % name)
        new["fields"][name] = value.strip()
    for heading, text in (change.sections or {}).items():
        if "\n" in heading or "\r" in heading:
            raise BoardError("section heading %r: one line only" % heading)
        _refuse_lines(text, _SECTION, "a section cannot hold a '## ' heading; use ### or deeper")
        new["body"] = set_section(new["body"], heading, text)
    return _readable(new)


def transition(card: Card, status: str, allowed: Sequence[str], now: dt.datetime) -> Card:
    """The card moved to `status`, spelled as in `allowed`; a BoardError when the status is not listed there."""
    canon = {s.lower(): s for s in allowed}
    if status.lower() not in canon:
        raise BoardError("status %r is not in LOCAL_STATUSES: %s" % (status, ", ".join(allowed)))
    new = _stamped(card, now)
    new["fields"]["status"] = canon[status.lower()]
    return new


def _video_link(found: re.Match[str]) -> str:
    """The markdown link one `::video <path>` line becomes; a BoardError when it would not read back as that path."""
    path = found.group(1)
    link = "[video: %s](%s)" % (os.path.basename(path), path)
    if video_paths(link) != [path]:
        raise BoardError("::video %s: a ')' in the path or a ']' in the file name breaks the link; rename it" % path)
    return link


def add_comment(card: Card, text: str, now: dt.datetime, cid: Optional[str] = None) -> Tuple[Card, str]:
    """Append the loop's comment, or replace the loop's own comment `cid`; a person's comment is never replaced.

    Returns the new card and the comment's id."""
    text = _VIDEO.sub(_video_link, text.strip("\n"))
    _refuse_lines(text, ENTRY, "a comment cannot start another '### c<n> · …' entry")
    new = _stamped(card, now)
    spot = [n for n, c in enumerate(new["comments"]) if c["id"] == cid]
    if cid is None:
        ids = [number(c["id"][1:], "%s comment id" % card["key"]) for c in new["comments"]]
        cid = "c%d" % (max(ids or [0]) + 1)
    elif not spot:
        raise BoardError("%s has no comment %s" % (card["key"], cid))
    elif new["comments"][spot[0]]["author"] != AUTHOR:
        raise BoardError("%s %s was written by %s; the loop replaces only its own comments"
                         % (card["key"], cid, new["comments"][spot[0]]["author"]))
    entry: Comment = {"id": cid, "when": now.strftime(TIME), "author": AUTHOR, "text": text}
    if spot:
        new["comments"][spot[0]] = entry
    else:
        new["comments"].append(entry)
    return _readable(new), cid


def video_paths(text: str) -> List[str]:
    """The file paths of the video links add_comment wrote into a comment."""
    return _LINK.findall(text)
