"""What Jira answered, as the text the jira-*.sh scripts print (reached through jira_fmt.py).

Each function is pure: the response body in, the printed text out, newlines included. A body that is not the JSON
a function expects, Jira's error object included, raises BodyError: one `ERROR …` line for the caller to print.
"""
from __future__ import annotations

import html
import json
import re
from typing import Any, Dict, Iterable, List, Optional, Tuple


class BodyError(Exception):
    """A body a command cannot format. `line` is what to print; `stdout` is true where that line was always on stdout."""

    def __init__(self, line: str, stdout: bool = False) -> None:
        super().__init__(line)
        self.line = line
        self.stdout = stdout


def parse_json(body: str) -> Any:
    """Return the value the JSON text holds; text that is not JSON is a BodyError."""
    try:
        return json.loads(body)
    except ValueError:
        raise BodyError("ERROR expected JSON, got: " + (" ".join(body.split())[:120] or "(nothing)")) from None


def _object(body: str, key: str, stdout: bool = False) -> Dict[str, Any]:
    """The JSON object in body, which must hold key; anything else, Jira's error object included, is a BodyError."""
    data = parse_json(body)
    if not isinstance(data, dict) or key not in data:
        raise BodyError("ERROR " + json.dumps(data)[:300], stdout)
    return data


def _text(lines: Iterable[str]) -> str:
    return "".join(line + "\n" for line in lines)


def _plain(markup: Optional[str]) -> str:
    """Rendered HTML as plain text, one line per paragraph, list item or table row."""
    kept = re.sub(r"<(?!br|/p|/li|/tr)[^>]+>", "", markup or "")
    return html.unescape(re.sub(r"[ \t]+", " ", re.sub(r"<br ?/?>|</p>|</li>|</tr>", "\n", kept))).strip()


def _one_line(markup: str) -> str:
    """Rendered HTML as one line, its paragraphs joined by ' | '."""
    broken = re.sub(r"<br ?/?>|</p>|</li>|</tr>|</h[1-6]>", "\n", markup)
    lines = (html.unescape(re.sub(r"<[^>]+>", "", line)).strip() for line in broken.splitlines())
    return " | ".join(line for line in lines if line)


def _value(value: Any) -> str:
    """A field's raw value as text: a select's value (and child), a user's or issue's name, a list joined by ', '."""
    if value is None or value == [] or value == "":
        return "(empty)"
    if isinstance(value, list):
        return ", ".join(_value(item) for item in value)
    if isinstance(value, dict):
        for key in ("value", "name", "displayName", "key"):
            if key in value:
                child = value.get("child")
                return str(value[key]) + (" / " + _value(child) if child else "")
        return json.dumps(value, ensure_ascii=False)[:200]
    return str(value)


def _head(issue: Dict[str, Any]) -> str:
    fields = issue["fields"]
    return "%s  [%s / %s (%s)]  id=%s" % (issue["key"], fields["issuetype"]["name"], fields["status"]["name"],
                                          fields["status"]["id"], issue["id"])


def issue_text(body: str) -> str:
    """Return jira-get's text: head line, dates and reporter, SUMMARY, DESCRIPTION, each comment, each ATTACHMENT."""
    issue = _object(body, "fields", stdout=True)
    fields, rendered = issue["fields"], issue.get("renderedFields") or {}
    lines = [_head(issue),
             "created %s · updated %s · reporter %s" % (fields["created"][:16], fields["updated"][:16],
                                                        (fields.get("reporter") or {}).get("displayName", "?")),
             "SUMMARY: %s" % (fields["summary"],),
             "DESCRIPTION:\n" + _plain(rendered.get("description"))]
    shown = (rendered.get("comment") or {}).get("comments") or []
    for comment, raw in zip(shown, (fields.get("comment") or {}).get("comments") or []):
        lines.append("--- comment %s by %s at %s\n%s" % (raw["id"], raw["author"]["displayName"], raw["created"][:16],
                                                         _plain(comment.get("body"))))
    for a in fields.get("attachment") or []:
        lines.append("ATTACHMENT %s  %s  %s bytes  %s" % (a["id"], a["filename"], a["size"], a["mimeType"]))
    return _text(lines)


def card_text(body: str, extra: str) -> str:
    """Return jira-card's text: head line with priority, LABELS, PARENT, a LINK per link, a FIELD per id in extra."""
    issue = _object(body, "fields", stdout=True)
    fields, rendered, names = issue["fields"], issue.get("renderedFields") or {}, issue.get("names") or {}
    priority = (fields.get("priority") or {}).get("name")
    lines = [_head(issue) + ("  priority " + priority if priority else ""),
             "LABELS: " + (", ".join(fields.get("labels") or []) or "(none)")]
    parent = fields.get("parent")
    if parent:
        lines.append("PARENT: %s %s" % (parent["key"], (parent.get("fields") or {}).get("summary", "")))
    for link in fields.get("issuelinks") or []:
        side, verb = ("outwardIssue", "outward") if "outwardIssue" in link else ("inwardIssue", "inward")
        other = link[side]
        other_fields = other.get("fields") or {}
        lines.append("LINK: %s %s [%s] %s" % (link["type"][verb], other["key"],
                                              (other_fields.get("status") or {}).get("name", "?"),
                                              other_fields.get("summary", "")))
    for fid in (part for part in extra.split(",") if part):
        markup = rendered.get(fid)
        shown = _one_line(markup) if isinstance(markup, str) and markup.strip() else _value(fields.get(fid))
        lines.append("FIELD %s (%s): %s" % (fid, names.get(fid, fid), shown or "(empty)"))
    return _text(lines)


def search_page(body: str) -> str:
    """Return a `KEY | type | status (id) | sprints or BACKLOG | updated | summary` line per issue of one result
    page, then `__NEXT__ <token>` (no token on the last page)."""
    page = _object(body, "issues")
    lines = []
    for issue in page["issues"]:
        f = issue["fields"]
        sprints = ",".join("%s(%s)" % (s.get("name", ""), s.get("state", "")) for s in f.get("customfield_10020") or [])
        lines.append("%s | %s | %s (%s) | %s | %s | %s" % (issue["key"], f["issuetype"]["name"], f["status"]["name"],
                                                           f["status"]["id"], sprints or "BACKLOG",
                                                           f.get("updated", "")[:16], f["summary"][:90]))
    lines.append("__NEXT__ " + ("" if page.get("isLast", True) else page.get("nextPageToken", "")))
    return _text(lines)


def transitions_text(body: str) -> str:
    """Return an `id → name (status id, category)` line per transition the issue offers now."""
    return _text("%s → %s (status %s, %s)" % (t["id"], t["name"], t["to"]["id"], t["to"]["statusCategory"]["key"])
                 for t in _object(body, "transitions")["transitions"])


def status_text(body: str) -> str:
    """Return `name (id)` for the status of an issue."""
    status = _object(body, "fields")["fields"]["status"]
    return "%s (%s)\n" % (status["name"], status["id"])


def labels_text(body: str) -> str:
    """Return an issue's labels joined by commas (an empty line when it has none)."""
    return ",".join(_object(body, "fields")["fields"].get("labels") or []) + "\n"


def object_id(body: str) -> str:
    """Return the `id` of the object Jira answered with (an issue, a comment)."""
    return "%s\n" % (_object(body, "id")["id"],)


def comment_check(body: str, markdown: str, updated: bool) -> Tuple[str, List[str]]:
    """Return the read-back line for a posted comment (videos wanted, players and attachment ids rendered) and the
    warnings: no player rendered, or a `code` path of the markdown missing from the rendered comment."""
    comment = _object(body, "id")
    rendered = comment.get("renderedBody") or ""
    wanted = len(re.findall(r"^::video ", markdown, re.M))
    players = len(re.findall(r"type=\"video/mp4\"", rendered))
    ids = sorted(set(re.findall(r"attachment/content/(\d+)", rendered)))
    missing = [path for path in re.findall(r"`([^`]*[/.][^`]*)`", markdown) if path not in rendered]
    warnings = []
    if wanted and not ids:
        warnings.append("WARNING: no inline player rendered — check the media uuids")
    if missing:
        warnings.append("WARNING: these `code` spans are missing from the rendered comment (unquoted heredoc?): %s" % missing)
    return ("comment %s %s · videos in md %d · players rendered %d · attachment ids %s\n"
            % (comment["id"], "updated" if updated else "created", wanted, players, ids), warnings)


def attachment_rows(body: str) -> str:
    """Return an `id|size|filename` line per attachment of an upload answer (the name last: it may hold a `|`)."""
    rows = parse_json(body)
    if not isinstance(rows, list):
        raise BodyError("ERROR " + json.dumps(rows)[:300])
    return _text("%s|%s|%s" % (a["id"], a["size"], re.sub(r"[\x00-\x1f]", "_", a["filename"])) for a in rows)


def download_rows(body: str) -> str:
    """Return an `id<TAB>filename` line per attachment of an issue; a `/` or control character in a name becomes
    `_`, so a name is always one path segment on one line."""
    attachments = _object(body, "fields")["fields"].get("attachment") or []
    return _text(a["id"] + "\t" + re.sub(r"[/\x00-\x1f]", "_", a["filename"]) for a in attachments)


def display_name(body: str) -> str:
    """Return the display name of the account Jira's /myself describes."""
    return "%s\n" % (_object(body, "displayName")["displayName"],)
