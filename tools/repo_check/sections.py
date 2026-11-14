"""Check f: a `file § Section` reference points at a heading, or a bold lead, that the file really has."""
from __future__ import annotations

import os
import re
from typing import Dict, List, NamedTuple, Optional

from .model import Doc, Finding, docs, error, prose_lines, read_text, readmes, warn
from .paths import PLACEHOLDER_MARKS, is_target_path, resolve

# The owners a reference may name: "`stages.md` § Decision round", "n-dev § Questions", "config § Checks".
CONFIG_TEMPLATE = "skills/develop-init/templates/config.md"  # every repo's DC/config.md is written from it
CONFIG_NAMES = ("config", "Config", "config.md", "DC/config.md")
OWNER_ALIASES = dict({name: CONFIG_TEMPLATE for name in CONFIG_NAMES}, **{"n-dev": "skills/n-dev/SKILL.md"})
OWNER = re.compile(r"(?:(`[^`\n]+`)|([\w./-]+\.md)|\b(n-dev|[Cc]onfig))\s*$")
MENTION = re.compile(r"`[^`\s]+\.md`|\b(?:n-dev|[Cc]onfig)\b")  # an owner named earlier on a § reference's line
SECTION_WORDS = re.compile(r"\s*([A-Za-z].*)")  # "§ Words"; "§2" is a numbered section, not checked
PHRASE_END = re.compile(r"[)(;:|`›§<>\]\"*]|\.(?:\s|$)|\s[—–→]\s")  # where a reference's words surely stop
NUMBERING = re.compile(r"([A-Za-z]?\d+(?:\.\d+)*)[.)]?(?:\s+[·:—–-])?\s+(.*)")  # "S2 · Verify", "3. Steps"
TITLE_END = re.compile(r"\s+\(|\s+[—–·]\s+|:(?:\s|$)")  # "Auto mode (both loops)", "Questions: one round"
# A § may also point at a bold lead that opens a paragraph, a list item or a table row:
# "**By-design answers.** The decision…", "| **Input size and time** | …".
BOLD_LEAD = re.compile(r"\s*(?:[-*+]\s+|\d+[.)]\s+|\|\s*)?\*\*(.+?)\*\*")
# Section names the docs use on purpose although the config template no longer has them.
LEGACY_SECTIONS = (
    ["ai", "loop"],  # config's § Auto mode was § AI loop in 0.5–0.6; develop-init migrates it
)

Headings = Dict[str, List[List[str]]]  # file -> the word lists its headings and bold leads answer to


class SectionRef(NamedTuple):
    """A `§ words` reference: its line, the owner written just before it ("" when none is), the words
    as written, and every owner named earlier on the same line."""
    line: int
    owner: str
    phrase: str
    nearby: List[str]


def check_sections(repo: str) -> List[Finding]:
    """An error per `file § Words` reference (also `n-dev § …`, `config § …`) whose file has no such
    heading; a warning when the owner cannot be resolved, or is not named and no cited file matches."""
    headings: Headings = {}
    out = []
    for doc in docs(repo):
        out += _doc_sections(repo, doc, headings)
    for doc in readmes(repo):  # a README's references with a file named; its looser § mentions are left alone
        out += [finding for finding in _doc_sections(repo, doc, headings) if finding.level == "ERROR"]
    return out


def _doc_sections(repo: str, doc: Doc, headings: Headings) -> List[Finding]:
    """A § with no owner beside it is held against this file, the files the document cites with §,
    and the owners named earlier on its line; it can only warn."""
    out, cited, unowned = [], [doc.rel], []
    for ref in section_refs(doc.text):
        if _is_legacy(ref):
            continue
        if not ref.owner:
            unowned.append(ref)
            continue
        where = "%s:%d %s § %s" % (doc.rel, ref.line, ref.owner, ref.phrase)
        targets = owner_files(repo, doc, ref.owner)
        if targets is None:
            continue
        if len(targets) != 1:
            out.append(warn("sections", "%s: cannot resolve the owner file (%d candidates)" % (where, len(targets))))
            continue
        cited.append(targets[0])
        if not _has_heading(repo, targets[0], ref.phrase, headings):
            out.append(error("sections", "%s: no heading of %s starts with these words" % (where, targets[0])))
    for ref in unowned:
        named = [owner_files(repo, doc, owner) or [] for owner in ref.nearby]
        near = [files[0] for files in named if len(files) == 1]
        if not any(_has_heading(repo, rel, ref.phrase, headings) for rel in cited + near):
            out.append(warn("sections", "%s:%d § %s: no owner named, and no heading of this file or of a file "
                                        "it cites matches" % (doc.rel, ref.line, ref.phrase)))
    return out


def _is_legacy(ref: SectionRef) -> bool:
    """A config section (named, or with no owner) that the docs keep on purpose: see LEGACY_SECTIONS."""
    words = _words(ref.phrase)
    return ref.owner.strip("`") in ("",) + CONFIG_NAMES and any(
        words[:len(legacy)] == legacy for legacy in LEGACY_SECTIONS)


def section_refs(text: str) -> List[SectionRef]:
    """Every `§ words` reference in the prose, with the owner written just before it: a `.md` path
    (backticked or not), `n-dev` or `config`. Numbered references such as §2 are left out."""
    out, previous = [], ""
    for number, line in enumerate(prose_lines(text), 1):
        for sign in re.finditer("§", line):
            words = SECTION_WORDS.match(line[sign.end():])
            owner = _owner(line[:sign.start()] if line[:sign.start()].strip() else previous)
            phrase = PHRASE_END.split(words.group(1), 1)[0].strip() if words else ""
            if owner is not None and _words(phrase):
                out.append(SectionRef(number, owner, phrase, MENTION.findall(line[:sign.start()])))
        previous = line
    return out


def _owner(before: str) -> Optional[str]:
    """The owner at the end of the text before a §: "" when none is named, None for a placeholder."""
    m = OWNER.search(before)
    if not m:
        return ""
    span = m.group(1)
    if span is None:
        return str(m.group(2) or m.group(3))
    if any(mark in span for mark in PLACEHOLDER_MARKS):
        return None
    return str(span) if span.endswith(".md`") and " " not in span else ""


def owner_files(repo: str, doc: Doc, owner: str) -> Optional[List[str]]:
    """The repo files a § reference's owner may be: exactly one when it resolves, none or several when
    it does not. None for a target-project file, which this repo cannot check."""
    token = owner.strip("`")
    if token in OWNER_ALIASES:
        return [OWNER_ALIASES[token]]
    if is_target_path(token):
        return None
    return [os.path.relpath(path, repo) for path in resolve(repo, doc, token)]


def anchors(text: str) -> List[str]:
    """What a § may point at: each heading line, and each bold lead opening a paragraph, list item or table row."""
    out = []
    for line in prose_lines(text):
        lead = BOLD_LEAD.match(line)
        if re.match(r"#{1,6}\s", line):
            out.append(line)
        elif lead:
            out.append(lead.group(1))
    return out


def heading_keys(heading: str) -> List[List[str]]:
    """The word lists a § reference may match for one heading: its title (cut at " (", " — ", " · "
    or ":") and its whole text; behind numbering ("S2 ·", "3.") also the number alone and before each."""
    text = heading.lstrip("#").strip()
    m = NUMBERING.match(text)
    rest = m.group(2) if m else text
    keys = [_words(TITLE_END.split(rest, 1)[0]), _words(rest)]
    if m:
        number = _words(m.group(1))
        keys += [number] + [number + key for key in keys]
    return [key for key in keys if key]


def _has_heading(repo: str, rel: str, phrase: str, cache: Headings) -> bool:
    """True when a heading of the file starts with the phrase's words, or the phrase runs on past a
    whole heading title (a reference is followed by the rest of its sentence)."""
    if rel not in cache:
        cache[rel] = [key for anchor in anchors(read_text(repo, rel) or "") for key in heading_keys(anchor)]
    wanted = _words(phrase)
    return any(wanted[:len(key)] == key[:len(wanted)] for key in cache[rel])


def _words(text: str) -> List[str]:
    return re.findall(r"[a-z0-9]+", re.sub(r"['’]s\b", "", text.lower()))
