"""Pure core of the local board (TRACKER=local): one markdown file per card.

A card is a header of `name: value` lines between `---` lines, a markdown body of `## ` sections, and a
`## Comments` section whose entries start `### c<n> · <YYYY-MM-DD HH:MM> · <author>`. Nothing here reads files
or the clock: local_board.py passes them in. Every change returns a new card and leaves its input alone."""
from __future__ import annotations

import collections
import copy
import datetime as dt
import os
import re
import shlex

TIME = "%Y-%m-%d %H:%M"
COMMENTS = "## Comments"
AUTHOR = "90north-develop"
LISTS = ("labels", "links")
FIXED = LISTS + ("created", "updated", "status")
Change = collections.namedtuple("Change", "add_labels remove_labels fields sections", defaults=((), (), None, None))
_NAME = re.compile(r"[a-z][a-z0-9_-]*\Z")
_LABEL = re.compile(r"[A-Za-z0-9_.:/-]+\Z")
_LINK = re.compile(r"\[video: [^\]]*\]\(([^)]+)\)")
_TERM = re.compile(r"(-?)([a-z][a-z0-9_-]*)=(.+)\Z", re.S)
_AGE = re.compile(r"age([<>])(\d+)([mhd])\Z")
_ENTRY = re.compile(r"### (c\d+) · (.+?) · (.+)\Z")
_VIDEO = re.compile(r"^::video[ \t]+(\S+)[ \t]*$", re.M)
_UNITS = {"m": 60, "h": 3600, "d": 86400}


class BoardError(ValueError):
    pass


def slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.strip().lower()).strip("-")


def is_name(name):
    return bool(_NAME.match(name))


def _as_list(value):
    return value if isinstance(value, list) else [value]


# -- card text <-> card -------------------------------------------------------------------------------------------
def parse_card(key, text):
    lines = text.split("\n")
    if lines[0] != "---" or "---" not in lines[1:]:
        raise BoardError("%s: a card starts with a --- header block" % key)
    end = lines.index("---", 1)
    fields = {}
    for n, line in enumerate(lines[1:end], 2):
        name, sep, value = line.partition(":")
        name = name.strip().lower()
        if not sep or not _NAME.match(name):
            raise BoardError("%s line %d: expected 'name: value', got %r" % (key, n, line))
        fields[name] = _split(value.strip()) if name in LISTS else value.strip()
    rest = lines[end + 1:]
    cut = rest.index(COMMENTS) if COMMENTS in rest else len(rest)
    return {"key": key, "fields": fields, "body": "\n".join(rest[:cut]).strip("\n"),
            "comments": _parse_comments(key, rest[cut + 1:])}


def _split(value):
    return [v.strip() for v in value.split(",") if v.strip()]


def _parse_comments(key, lines):
    first = next((n for n, line in enumerate(lines) if _ENTRY.match(line)), len(lines))
    if re.sub(r"<!--.*?-->", "", "\n".join(lines[:first]), flags=re.S).strip():
        raise BoardError("%s: text under %s before the first '### c<n> · …' entry" % (key, COMMENTS))
    comments = []
    for line in lines[first:]:
        m = _ENTRY.match(line)
        if m:
            comments.append({"id": m.group(1), "when": m.group(2), "author": m.group(3), "lines": []})
        else:
            comments[-1]["lines"].append(line)
    for c in comments:
        c["text"] = "\n".join(c.pop("lines")).strip("\n")
    return comments


def render_card(card):
    head = ["%s: %s" % (k, ", ".join(_as_list(v))) for k, v in card["fields"].items()]
    out = "---\n%s\n---\n\n%s\n\n%s\n" % ("\n".join(h.rstrip() for h in head), card["body"], COMMENTS)
    for c in card["comments"]:
        out += "\n### %s · %s · %s\n%s\n" % (c["id"], c["when"], c["author"], c["text"])
    return out


# -- body sections ------------------------------------------------------------------------------------------------
def _sections(body):
    """[(heading or None, start line, end line)] for the body's `## ` sections."""
    lines = body.split("\n")
    starts = [i for i, line in enumerate(lines) if line.startswith("## ")]
    return lines, [(lines[s][3:].strip(), s, (starts + [len(lines)])[n + 1]) for n, s in enumerate(starts)]


def section(card, name):
    lines, spans = _sections(card["body"])
    for heading, start, end in spans:
        if slug(heading) == slug(name):
            return "\n".join(lines[start + 1:end]).strip("\n")
    return ""


def _set_section(body, heading, text):
    lines, spans = _sections(body)
    for name, start, end in spans:
        if slug(name) == slug(heading):
            tail = lines[end:]
            return "\n".join(lines[:start + 1] + text.strip("\n").split("\n") + ([""] + tail if tail else []))
    return (body.rstrip("\n") + "\n\n" if body.strip() else "") + "## %s\n%s" % (heading, text.strip("\n"))


# -- queries ------------------------------------------------------------------------------------------------------
def parse_query(text):
    try:
        tokens = shlex.split(text)
    except ValueError as e:
        raise BoardError("query: %s" % e)
    query = {"terms": [], "ages": [], "sort": None}
    for t in tokens:
        if t.startswith("sort="):
            name = t[5:].lstrip("-")
            if not _NAME.match(name):
                raise BoardError("query: sort=<field> or sort=-<field>, got %r" % t)
            query["sort"] = (name, t[5:].startswith("-"))
        elif _AGE.match(t):
            op, n, unit = _AGE.match(t).groups()
            query["ages"].append((op, int(n) * _UNITS[unit]))
        elif _TERM.match(t) and _split(_TERM.match(t).group(3)):
            neg, name, values = _TERM.match(t).groups()
            query["terms"].append((neg == "-", name, {v.lower() for v in _split(values)}))
        else:
            raise BoardError("query: bad term %r (use field=a,b  -field=a  age>2h  sort=-field)" % t)
    return query


def _values(card, name):
    return {x.lower() for x in _as_list(card["fields"].get(name, ""))}


def matches(card, query, now):
    for neg, name, values in query["terms"]:
        if bool(_values(card, name) & values) == neg:
            return False
    if query["ages"]:
        try:
            age = (now - dt.datetime.strptime(card["fields"].get("updated", ""), TIME)).total_seconds()
        except ValueError:
            return False
        if not all(age > limit if op == ">" else age < limit for op, limit in query["ages"]):
            return False
    return True


def _natural(value):
    return [int(p) if n % 2 else p.lower() for n, p in enumerate(re.split(r"(\d+)", value))]


def sort_cards(cards, query):
    out = sorted(cards, key=lambda c: _natural(c["key"]))
    if query["sort"]:
        name, desc = query["sort"]
        out.sort(key=lambda c: _natural(", ".join(sorted(_values(c, name)))), reverse=desc)
        return out
    return sorted(out, key=lambda c: ("rank" not in c["fields"] or not c["fields"]["rank"],
                                      _natural(c["fields"].get("rank", ""))))


# -- changes ------------------------------------------------------------------------------------------------------
def _stamped(card, now):
    new = copy.deepcopy(card)
    new["fields"]["updated"] = now.strftime(TIME)
    return new


def _refuse_lines(text, pattern, why):
    for n, line in enumerate(text.split("\n"), 1):
        if pattern.match(line):
            raise BoardError("line %d %r: %s" % (n, line, why))


def _readable(new):
    """The last guard: a change is kept only if the card it renders reads back as the same card."""
    if parse_card(new["key"], render_card(new)) != new:
        raise BoardError("%s: the change would not read back the same; nothing was written" % new["key"])
    return new


def edit(card, change, now):
    new = _stamped(card, now)
    for label in change.add_labels:
        if not _LABEL.match(label):
            raise BoardError("label %r: one word of letters, digits and . _ : / -" % label)
    labels = new["fields"].setdefault("labels", [])
    labels.extend(lb for lb in dict.fromkeys(change.add_labels) if lb not in labels)
    new["fields"]["labels"] = [lb for lb in labels if lb not in set(change.remove_labels)]
    for name, value in (change.fields or {}).items():
        if not _NAME.match(name) or name in FIXED:
            raise BoardError("field %r cannot be set (labels via --add-label/--remove-label, status via transition; "
                             "%s are kept by the board)" % (name, ", ".join(FIXED)))
        if "\n" in value or "\r" in value:
            raise BoardError("field %r: one line only; put longer text in a section with --field-md" % name)
        new["fields"][name] = value.strip()
    for heading, text in (change.sections or {}).items():
        _refuse_lines(text, re.compile(r"## "), "a section cannot hold a '## ' heading; use ### or deeper")
        new["body"] = _set_section(new["body"], heading, text)
    return _readable(new)


def transition(card, status, allowed, now):
    canon = {s.lower(): s for s in allowed}
    if status.lower() not in canon:
        raise BoardError("status %r is not in LOCAL_STATUSES: %s" % (status, ", ".join(allowed)))
    new = _stamped(card, now)
    new["fields"]["status"] = canon[status.lower()]
    return new


def add_comment(card, text, now, cid=None):
    """Append the loop's comment, or replace the loop's own comment `cid`; a person's comment is never replaced."""
    text = _VIDEO.sub(lambda m: "[video: %s](%s)" % (os.path.basename(m.group(1)), m.group(1)), text.strip("\n"))
    _refuse_lines(text, _ENTRY, "a comment cannot start another '### c<n> · …' entry")
    new = _stamped(card, now)
    entry = {"id": cid, "when": now.strftime(TIME), "author": AUTHOR, "text": text}
    if cid is None:
        entry["id"] = "c%d" % (max([int(c["id"][1:]) for c in new["comments"]] or [0]) + 1)
        new["comments"].append(entry)
    else:
        spot = [n for n, c in enumerate(new["comments"]) if c["id"] == cid]
        if not spot:
            raise BoardError("%s has no comment %s" % (card["key"], cid))
        if new["comments"][spot[0]]["author"] != AUTHOR:
            raise BoardError("%s %s was written by %s; the loop replaces only its own comments"
                             % (card["key"], cid, new["comments"][spot[0]]["author"]))
        new["comments"][spot[0]] = entry
    return _readable(new), entry["id"]


def video_paths(text):
    """The file paths of the video links add_comment wrote into a comment."""
    return _LINK.findall(text)


def field_text(card, name):
    """A header field (lists joined by ", "), else a body section on one line (" | " between lines), else ""."""
    value = card["fields"].get(name)
    if value:
        return ", ".join(_as_list(value))
    return " | ".join(line for line in section(card, name).split("\n") if line.strip())


def summary_line(card):
    f = card["fields"]
    return " | ".join([card["key"], f.get("type", ""), f.get("status", ""), ", ".join(f.get("labels", [])),
                       f.get("updated", ""), f.get("title", "")])
