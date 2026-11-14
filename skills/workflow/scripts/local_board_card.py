"""The card format of the local board (TRACKER=local): one markdown file per card, as text and as a Card.

A card is a header of `name: value` lines between `---` lines, a markdown body of `## ` sections, and a
`## Comments` section whose entries start `### c<n> · <YYYY-MM-DD HH:MM> · <author>`. Nothing here reads files
or the clock."""
from __future__ import annotations

import re
from typing import Dict, List, Set, Tuple, TypedDict, Union

TIME = "%Y-%m-%d %H:%M"
COMMENTS = "## Comments"
LISTS = ("labels", "links")
MAX_DIGITS = 4300  # the longest digit run Python 3.11+ reads or prints as an int; see number, and the query's sort
ENTRY = re.compile(r"### (c\d+) · (.+?) · (.+)\Z")  # the line that starts a comment
Value = Union[str, List[str]]
_NAME = re.compile(r"[a-z][a-z0-9_-]*\Z")


class BoardError(ValueError):
    """A card, query or change the board refuses; its message is the one line the caller prints."""


class Comment(TypedDict):
    """One entry under `## Comments`: its id (c<n>), time, author and markdown text."""

    id: str
    when: str
    author: str
    text: str


class Card(TypedDict):
    """One card: its key, header fields in file order (labels and links as lists), body and comments."""

    key: str
    fields: Dict[str, Value]
    body: str
    comments: List[Comment]


def slug(name: str) -> str:
    """`name` as a section is asked for: lower case, every other run one dash ("AI summary" → ai-summary)."""
    return re.sub(r"[^a-z0-9]+", "-", name.strip().lower()).strip("-")


def is_name(name: str) -> bool:
    """True when `name` can name a header field: lower case, starting with a letter."""
    return bool(_NAME.match(name))


def _as_list(value: Value) -> List[str]:
    return value if isinstance(value, list) else [value]


def header(card: Card, name: str) -> str:
    """The header field as text: a list joined by ", ", and "" when the card has no such field."""
    return ", ".join(_as_list(card["fields"].get(name, "")))


def listed(card: Card, name: str) -> List[str]:
    """The header field as a new list: [] when the card has no such field, one item for a plain value."""
    return list(_as_list(card["fields"].get(name, [])))


def values(card: Card, name: str) -> Set[str]:
    """The header field's values in lower case; the one value "" when the card has no such field."""
    return {x.lower() for x in _as_list(card["fields"].get(name, ""))}


def split_list(value: str) -> List[str]:
    """The items of a comma-separated value, trimmed, without the empty ones."""
    return [v.strip() for v in value.split(",") if v.strip()]


def number(digits: str, what: str) -> int:
    """int(digits), or a BoardError from MAX_DIGITS digits on: beyond it int() raises, and at it n + 1 cannot print."""
    if len(digits) >= MAX_DIGITS:
        raise BoardError("%s: a number of %d digits is too long" % (what, len(digits)))
    return int(digits)


# -- card text <-> card -------------------------------------------------------------------------------------------
def parse_card(key: str, text: str) -> Card:
    """The card that `text` holds; a BoardError says what is wrong when the header or the comments do not parse."""
    lines = text.split("\n")
    if lines[0] != "---" or "---" not in lines[1:]:
        raise BoardError("%s: a card starts with a --- header block" % key)
    end = lines.index("---", 1)
    fields: Dict[str, Value] = {}
    for n, line in enumerate(lines[1:end], 2):
        name, sep, value = line.partition(":")
        name = name.strip().lower()
        if not sep or not _NAME.match(name):
            raise BoardError("%s line %d: expected 'name: value', got %r" % (key, n, line))
        fields[name] = split_list(value.strip()) if name in LISTS else value.strip()
    rest = lines[end + 1:]
    cut = rest.index(COMMENTS) if COMMENTS in rest else len(rest)
    return {"key": key, "fields": fields, "body": "\n".join(rest[:cut]).strip("\n"),
            "comments": _parse_comments(key, rest[cut + 1:])}


def _parse_comments(key: str, lines: List[str]) -> List[Comment]:
    first = next((n for n, line in enumerate(lines) if ENTRY.match(line)), len(lines))
    if re.sub(r"<!--.*?-->", "", "\n".join(lines[:first]), flags=re.S).strip():
        raise BoardError("%s: text under %s before the first '### c<n> · …' entry" % (key, COMMENTS))
    comments: List[Comment] = []
    texts: List[List[str]] = []
    for line in lines[first:]:
        m = ENTRY.match(line)
        if m:
            comments.append({"id": m.group(1), "when": m.group(2), "author": m.group(3), "text": ""})
            texts.append([])
        else:
            texts[-1].append(line)
    for c, text in zip(comments, texts):
        c["text"] = "\n".join(text).strip("\n")
    return comments


def render_card(card: Card) -> str:
    """The text of the card's file; parse_card reads it back as the same card."""
    head = ["%s: %s" % (k, ", ".join(_as_list(v))) for k, v in card["fields"].items()]
    out = "---\n%s\n---\n\n%s\n\n%s\n" % ("\n".join(h.rstrip() for h in head), card["body"], COMMENTS)
    for c in card["comments"]:
        out += "\n### %s · %s · %s\n%s\n" % (c["id"], c["when"], c["author"], c["text"])
    return out


# -- body sections ------------------------------------------------------------------------------------------------
def _sections(body: str) -> Tuple[List[str], List[Tuple[str, int, int]]]:
    """The body's lines, and (heading, start line, end line) for each of its `## ` sections."""
    lines = body.split("\n")
    starts = [i for i, line in enumerate(lines) if line.startswith("## ")]
    return lines, [(lines[s][3:].strip(), s, (starts + [len(lines)])[n + 1]) for n, s in enumerate(starts)]


def section(card: Card, name: str) -> str:
    """The text under the body heading whose slug is slug(name), or "" when there is no such section."""
    lines, spans = _sections(card["body"])
    for heading, start, end in spans:
        if slug(heading) == slug(name):
            return "\n".join(lines[start + 1:end]).strip("\n")
    return ""


def set_section(body: str, heading: str, text: str) -> str:
    """The body with that section's text replaced, or with the section added at the end when it has none."""
    lines, spans = _sections(body)
    for name, start, end in spans:
        if slug(name) == slug(heading):
            tail = lines[end:]
            return "\n".join(lines[:start + 1] + text.strip("\n").split("\n") + ([""] + tail if tail else []))
    return (body.rstrip("\n") + "\n\n" if body.strip() else "") + "## %s\n%s" % (heading, text.strip("\n"))


# -- one-line views -----------------------------------------------------------------------------------------------
def field_text(card: Card, name: str) -> str:
    """A header field (lists joined by ", "), else a body section on one line (" | " between lines), else ""."""
    value = card["fields"].get(name)
    if value:
        return ", ".join(_as_list(value))
    return " | ".join(line for line in section(card, name).split("\n") if line.strip())


def summary_line(card: Card) -> str:
    """The one line `search` prints for a card: key | type | status | labels | updated | title."""
    return " | ".join([card["key"]] + [header(card, n) for n in ("type", "status", "labels", "updated", "title")])
