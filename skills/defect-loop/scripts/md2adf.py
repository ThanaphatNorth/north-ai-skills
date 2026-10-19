#!/usr/bin/env python3
"""Convert the loop's small markdown dialect to Atlassian Document Format (ADF) JSON on stdout.

  python3 -I md2adf.py comment.md <issue-id>

Blocks (separated by line type, not only blank lines):
  ::video <media-uuid>     inline video/image from an attachment of this issue (mediaSingle)
  1. item                  ordered list (consecutive lines)
  - item                   bullet list (consecutive lines)
  anything else            paragraph; consecutive lines join with hard breaks
Inline: **bold**, `code`, and bare http(s) links.
"""
import json
import re
import sys

INLINE = re.compile(r"(\*\*(.+?)\*\*|`([^`]+)`|(https?://[^\s)]+))")


def inline(text):
    out, pos = [], 0
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


def paragraph(lines):
    content = []
    for i, line in enumerate(lines):
        if i:
            content.append({"type": "hardBreak"})
        content.extend(inline(line))
    return {"type": "paragraph", "content": content}


def list_node(kind, items):
    return {"type": kind, "content": [{"type": "listItem", "content": [paragraph([t])]} for t in items]}


def convert(md, issue_id):
    blocks, para, items, kind = [], [], [], None

    def flush():
        nonlocal para, items, kind
        if para:
            blocks.append(paragraph(para))
            para = []
        if items:
            blocks.append(list_node(kind, items))
            items, kind = [], None

    for raw in md.splitlines():
        line = raw.rstrip()
        m_ol = re.match(r"^\d+\.\s+(.*)$", line)
        m_ul = re.match(r"^[-*]\s+(.*)$", line)
        m_vid = re.match(r"^::video\s+([0-9a-f-]{36})\s*$", line)
        if not line:
            flush()
        elif m_vid:
            flush()
            blocks.append({"type": "mediaSingle", "attrs": {"layout": "center"}, "content": [
                {"type": "media", "attrs": {"type": "file", "id": m_vid.group(1), "collection": f"jira-{issue_id}"}}]})
        elif m_ol or m_ul:
            k = "orderedList" if m_ol else "bulletList"
            if para or (kind and kind != k):
                flush()
            kind = k
            items.append((m_ol or m_ul).group(1))
        else:
            if items:
                flush()
            para.append(line)
    flush()
    return {"type": "doc", "version": 1, "content": blocks}


if __name__ == "__main__":
    md_path, issue_id = sys.argv[1], sys.argv[2]
    text = re.sub(r"<!--.*?-->\n?", "", open(md_path, encoding="utf-8").read(), flags=re.S)  # template notes never reach Jira
    print(json.dumps(convert(text, issue_id), ensure_ascii=False))
