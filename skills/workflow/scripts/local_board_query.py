"""The query language of the local board's `search`: field terms, age limits and a sort order.

  status=todo,ready   -labels=ai-processing   severity="Level 4,Level 5"   age>2h   sort=-updated
Nothing here reads files or the clock: the caller passes the cards and the time."""
from __future__ import annotations

import datetime as dt
import re
import shlex
from typing import List, Optional, Sequence, Set, Tuple, TypedDict, Union

from local_board_card import MAX_DIGITS, TIME, BoardError, Card, header, is_name, number, split_list, values

_TERM = re.compile(r"(-?)([a-z][a-z0-9_-]*)=(.+)\Z", re.S)
_AGE = re.compile(r"age([<>])(\d+)([mhd])\Z")
_UNITS = {"m": 60, "h": 3600, "d": 86400}


class Query(TypedDict):
    """A parsed search: (negated, field, values) terms, (operator, seconds) ages, (field, descending) sort or None."""

    terms: List[Tuple[bool, str, Set[str]]]
    ages: List[Tuple[str, int]]
    sort: Optional[Tuple[str, bool]]


def parse_query(text: str) -> Query:
    """The query's terms, age limits and sort order; a BoardError names the first term that is not one of those."""
    try:
        tokens = shlex.split(text)
    except ValueError as e:
        raise BoardError("query: %s" % e)
    query: Query = {"terms": [], "ages": [], "sort": None}
    for t in tokens:
        age, term = _AGE.match(t), _TERM.match(t)
        if t.startswith("sort="):
            name = t[5:].lstrip("-")
            if not is_name(name):
                raise BoardError("query: sort=<field> or sort=-<field>, got %r" % t)
            query["sort"] = (name, t[5:].startswith("-"))
        elif age:
            query["ages"].append((age.group(1), number(age.group(2), "query age") * _UNITS[age.group(3)]))
        elif term and split_list(term.group(3)):
            query["terms"].append((term.group(1) == "-", term.group(2), {v.lower() for v in split_list(term.group(3))}))
        else:
            raise BoardError("query: bad term %r (use field=a,b  -field=a  age>2h  sort=-field)" % t)
    return query


def matches(card: Card, query: Query, now: dt.datetime) -> bool:
    """True when the card passes every term; an age term never passes a card whose `updated` is not a time."""
    for neg, name, wanted in query["terms"]:
        if bool(values(card, name) & wanted) == neg:
            return False
    if query["ages"]:
        try:
            age = (now - dt.datetime.strptime(header(card, "updated"), TIME)).total_seconds()
        except ValueError:
            return False
        if not all(age > limit if op == ">" else age < limit for op, limit in query["ages"]):
            return False
    return True


def _natural(value: str) -> List[Union[str, float]]:
    """A sort key that reads digit runs as numbers (TASK-2 before TASK-10); a run over MAX_DIGITS sorts last."""
    return [(int(p) if len(p) <= MAX_DIGITS else float("inf")) if n % 2 else p.lower()
            for n, p in enumerate(re.split(r"(\d+)", value))]


def sort_cards(cards: Sequence[Card], query: Query) -> List[Card]:
    """The cards in the query's order: its sort field, else rank (cards without one last), ties by key."""
    out = sorted(cards, key=lambda c: _natural(c["key"]))
    order = query["sort"]
    if order:
        name, desc = order
        out.sort(key=lambda c: _natural(", ".join(sorted(values(c, name)))), reverse=desc)
        return out
    return sorted(out, key=lambda c: (not header(c, "rank"), _natural(header(c, "rank"))))
