#!/usr/bin/env python3
"""Convert the loop's small markdown dialect to Atlassian Document Format (ADF) JSON on stdout.

  python3 -I md2adf.py comment.md <issue-id>

Blocks (separated by line type, not only blank lines):
  ::video <media-uuid>     inline video/image from an attachment of this issue (mediaSingle)
  1. item                  ordered list (consecutive lines)
  - item                   bullet list (consecutive lines)
  anything else            paragraph; consecutive lines join with hard breaks
Inline: **bold**, `code`, and bare http(s) links.
Markdown outside the dialect (a fence, a table, a nested item, a mark that never closes) stays text.
A file that cannot be read is one line on stderr and exit 1; missing arguments are exit 2.
"""
from __future__ import annotations

import json
import os
import re
import sys
from typing import Dict, List, TypedDict

INLINE = re.compile(r"(\*\*(.+?)\*\*|`([^`]+)`|(https?://[^\s)]+))")


class Mark(TypedDict, total=False):
    """An inline mark: its type (strong, code, link) and, for a link, the href in attrs."""

    type: str
    attrs: Dict[str, str]


class Node(TypedDict, total=False):
    """One ADF node; `type` is always set, the other keys depend on it."""

    type: str
    version: int
    text: str
    marks: List[Mark]
    attrs: Dict[str, str]
    content: List[Node]


def inline(text: str) -> List[Node]:
    """The text nodes of one line: bold, code and link marks where they close, plain text for the rest."""
    out: List[Node] = []
    pos = 0
    for m in INLINE.finditer(text):
        if m.start() > pos:
            out.append({"type": "text", "text": text[pos:m.start()]})
        if m.group(2) is not None:
            out.append({"type": "text", "text": m.group(2), "marks": [{"type": "strong"}]})
        elif m.group(3) is not None:
            out.append({"type": "text", "text": m.group(3), "marks": [{"type": "code"}]})
        else:
            url = m.group(4)
            out.append({"type": "text", "text": url, "marks": [{"type": "link", "attrs": {"href": url}}]})
        pos = m.end()
    if pos < len(text):
        out.append({"type": "text", "text": text[pos:]})
    return out


def paragraph(lines: List[str]) -> Node:
    """One paragraph node whose lines are joined by hard breaks."""
    content: List[Node] = []
    for i, line in enumerate(lines):
        if i:
            content.append({"type": "hardBreak"})
        content.extend(inline(line))
    return {"type": "paragraph", "content": content}


def list_node(kind: str, items: List[str]) -> Node:
    """A list node of `kind` (orderedList or bulletList) with one single-paragraph item per string."""
    return {"type": kind, "content": [{"type": "listItem", "content": [paragraph([t])]} for t in items]}


def convert(md: str, issue_id: str) -> Node:
    """The ADF document for the markdown; media nodes point at the attachment collection of `issue_id`."""
    blocks: List[Node] = []
    para: List[str] = []
    items: List[str] = []
    kind = ""

    def flush() -> None:
        nonlocal para, items, kind
        if para:
            blocks.append(paragraph(para))
            para = []
        if items:
            blocks.append(list_node(kind, items))
            items, kind = [], ""

    for raw in md.splitlines():
        line = raw.rstrip()
        m_ol = re.match(r"^\d+\.\s+(.*)$", line)
        item = m_ol or re.match(r"^[-*]\s+(.*)$", line)
        m_vid = re.match(r"^::video\s+([0-9a-f-]{36})\s*$", line)
        if not line:
            flush()
        elif m_vid:
            flush()
            blocks.append({"type": "mediaSingle", "attrs": {"layout": "center"}, "content": [
                {"type": "media", "attrs": {"type": "file", "id": m_vid.group(1), "collection": f"jira-{issue_id}"}}]})
        elif item:
            k = "orderedList" if m_ol else "bulletList"
            if para or (kind and kind != k):
                flush()
            kind = k
            items.append(item.group(1))
        else:
            if items:
                flush()
            para.append(line)
    flush()
    return {"type": "doc", "version": 1, "content": blocks}


def _fail(message: str) -> int:
    """Print the message as one stderr line (a line break in a file name shows as \\n); returns exit code 1."""
    print("md2adf.py: " + "\\n".join(message.splitlines()), file=sys.stderr)
    return 1


def main(argv: List[str]) -> int:
    """Print the ADF JSON for file argv[0] and issue argv[1]; returns 0, 1 for a failed read or write, 2 for usage."""
    if len(argv) < 2:
        print("usage: md2adf.py <comment.md> <issue-id>", file=sys.stderr)
        return 2
    try:
        with open(argv[0], encoding="utf-8") as fh:
            text = fh.read()
    except OSError as e:
        return _fail("cannot read %s: %s" % (argv[0], e.strerror))
    except UnicodeDecodeError:
        return _fail("%s is not UTF-8 text" % argv[0])
    doc = convert(re.sub(r"<!--.*?-->\n?", "", text, flags=re.S), argv[1])  # template notes never reach Jira
    try:
        try:
            print(json.dumps(doc, ensure_ascii=False), flush=True)
        except UnicodeEncodeError:  # a stdout that cannot hold the text gets the same document with \u escapes
            print(json.dumps(doc), flush=True)
    except OSError as e:  # the reader left or the disk is full: drop what is buffered, so the exit stays quiet
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        return _fail("cannot write the document: %s" % e.strerror)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
