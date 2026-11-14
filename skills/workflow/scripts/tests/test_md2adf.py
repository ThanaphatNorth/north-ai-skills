"""Tests for md2adf: the loop's markdown dialect to ADF, and its command line.

  python3 -m unittest discover -s skills/workflow/scripts/tests -p 'test_*.py'
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SCRIPTS)
import md2adf  # noqa: E402

MD2ADF = os.path.join(SCRIPTS, "md2adf.py")
UUID = "0f1e2d3c-4b5a-6978-8796-a5b4c3d2e1f0"
BLOCKS = {"paragraph", "orderedList", "bulletList", "mediaSingle"}


def text(value, *marks):
    node = {"type": "text", "text": value}
    if marks:
        node["marks"] = [m if isinstance(m, dict) else {"type": m} for m in marks]
    return node


def para(*content):
    return {"type": "paragraph", "content": list(content)}


def blocks(md):
    return md2adf.convert(md, "10042")["content"]


def texts(node):
    """Every piece of text in the document, in order."""
    return [node["text"]] if node["type"] == "text" else [t for c in node.get("content", []) for t in texts(c)]


def problems(node, top=True):
    """What Jira would reject: an unknown block, a text node with no text, a node that is not plain JSON."""
    found = [] if json.loads(json.dumps(node)) == node else ["not JSON: %r" % node]
    if top and node["type"] != "doc":
        found.append("top is %s" % node["type"])
    if node["type"] == "text" and not node["text"]:
        found.append("empty text node")
    for child in node.get("content", []):
        if node["type"] == "doc" and child["type"] not in BLOCKS:
            found.append("block %s" % child["type"])
        found += problems(child, top=False)
    return found


class Inline(unittest.TestCase):
    def test_bold_code_and_links_keep_the_text_around_them(self):
        self.assertEqual(md2adf.inline("see **this** and `that` at https://x.test/a?b=1 ok"), [
            text("see "), text("this", "strong"), text(" and "), text("that", "code"), text(" at "),
            text("https://x.test/a?b=1", {"type": "link", "attrs": {"href": "https://x.test/a?b=1"}}), text(" ok")])

    def test_a_link_stops_at_a_space_or_a_closing_bracket(self):
        self.assertEqual(md2adf.inline("(http://x.test/p)"), [
            text("("), text("http://x.test/p", {"type": "link", "attrs": {"href": "http://x.test/p"}}), text(")")])

    def test_marks_that_never_close_stay_plain_text(self):
        for line in ("an `unclosed span", "an **unclosed bold", "``", "****", "a ` b ** c", "```python"):
            self.assertEqual(md2adf.inline(line), [text(line)], line)

    def test_an_empty_line_has_no_nodes(self):
        self.assertEqual(md2adf.inline(""), [])


class Blocks(unittest.TestCase):
    def test_lines_of_one_paragraph_join_with_hard_breaks_and_a_blank_line_starts_a_new_one(self):
        self.assertEqual(blocks("one\ntwo\n\nthree\n"), [
            para(text("one"), {"type": "hardBreak"}, text("two")), para(text("three"))])

    def test_a_video_line_becomes_a_media_block_of_this_issue(self):
        self.assertEqual(blocks("before\n::video %s  \nafter" % UUID), [
            para(text("before")),
            {"type": "mediaSingle", "attrs": {"layout": "center"}, "content": [
                {"type": "media", "attrs": {"type": "file", "id": UUID, "collection": "jira-10042"}}]},
            para(text("after"))])

    def test_ordered_and_bullet_lists_split_where_the_marker_changes(self):
        got = blocks("intro\n1. one\n2. **two**\n- a\n* b\noutro")
        self.assertEqual([b["type"] for b in got], ["paragraph", "orderedList", "bulletList", "paragraph"])
        self.assertEqual(got[1]["content"][1], {"type": "listItem", "content": [para(text("two", "strong"))]})
        self.assertEqual([texts(item) for item in got[2]["content"]], [["a"], ["b"]])
        self.assertEqual(texts(got[3]), ["outro"])

    def test_two_lists_of_one_kind_split_by_a_blank_line_stay_two(self):
        self.assertEqual([len(b["content"]) for b in blocks("- a\n- b\n\n- c")], [2, 1])


class Unusual(unittest.TestCase):
    """Markdown outside the dialect: nothing is lost, nothing raises, and the result is still a document."""

    CASES = {
        "empty": "",
        "only blank lines": "\n\n  \n\t\n",
        "unclosed code span": "run `npm test\nthen wait",
        "unclosed fence": "```python\nprint('**x**')\nno closing fence",
        "ragged table": "| a | b |\n|---|\n| 1 | 2 | 3 |\n| only one",
        "nested lists": "- top\n  - child\n    1. deep\n- back",
        "video with no value": "::video\n::video   \n::video not-a-uuid",
        "marker with no item": "-\n1.\n*",
        "windows line endings": "one\r\n- a\r\n\r\ntwo\r\n",
        "control characters": "bell\x07 nul\x00 esc\x1b form\x0cfeed",
        "thai and emoji": "ทดสอบ **ตัวหนา** 🙂 `โค้ด`",
    }

    def test_every_unusual_input_gives_a_document_jira_would_take(self):
        for name, md in self.CASES.items():
            doc = md2adf.convert(md, "1")
            self.assertEqual((doc["type"], doc["version"], problems(doc)), ("doc", 1, []), name)

    def test_no_word_is_lost(self):
        for name, md in self.CASES.items():
            kept = "".join(texts(md2adf.convert(md, "1")))
            for word in md.replace("**", " ").replace("`", " ").split():
                if word not in ("-", "*", "1."):  # the list markers themselves become structure
                    self.assertIn(word, kept, name)

    def test_empty_input_is_an_empty_document(self):
        self.assertEqual(md2adf.convert("", "1"), {"type": "doc", "version": 1, "content": []})

    def test_a_video_line_without_a_media_id_stays_text(self):
        self.assertEqual(blocks("::video\n::video not-a-uuid"), [
            para(text("::video"), {"type": "hardBreak"}, text("::video not-a-uuid"))])

    def test_a_nested_item_stays_a_line_of_text_after_its_list(self):
        got = blocks("- top\n  - child\n- back")
        self.assertEqual([b["type"] for b in got], ["bulletList", "paragraph", "bulletList"])
        self.assertEqual(texts(got[1]), ["  - child"])

    def test_a_very_long_line_converts_whole(self):
        million = 10 ** 6
        for line, kept in (("word " * 400000, ("word " * 400000).rstrip()), ("`" * million, "`" * million),
                           ("**" + "a" * million, "**" + "a" * million), ("1" * million + ". item", "item"),
                           ("https://x.test/" + "a" * million, "https://x.test/" + "a" * million)):
            doc = md2adf.convert(line, "1")
            self.assertEqual((problems(doc), "".join(texts(doc)) == kept), ([], True), line[:20])


class CommandLine(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def file(self, data):
        path = os.path.join(self.tmp, "comment.md")
        with open(path, "wb") as fh:
            fh.write(data if isinstance(data, bytes) else data.encode("utf-8"))
        return path

    def run_it(self, *args, **env):
        return subprocess.run([sys.executable] + ([] if env else ["-I"]) + [MD2ADF] + list(args),
                              env=dict(os.environ, **env), capture_output=True)

    def refused(self, r, says, code):
        err = r.stderr.decode("utf-8")
        self.assertEqual((r.returncode, r.stdout), (code, b""), err)
        self.assertNotIn("Traceback", err)
        self.assertEqual(len(err.strip().splitlines()), 1, err)
        self.assertIn(says, err)

    def test_a_file_becomes_one_line_of_json_without_its_template_notes(self):
        note = "<!-- delete this note -->\n**Generated by AI** ทดสอบ\n<!-- two\nlines -->- a\n"
        r = self.run_it(self.file(note), "10042", "an extra argument is ignored")
        self.assertEqual((r.returncode, r.stderr), (0, b""))
        self.assertEqual(r.stdout.count(b"\n"), 1)
        self.assertEqual(json.loads(r.stdout.decode("utf-8"))["content"], [
            para(text("Generated by AI", "strong"), text(" ทดสอบ")),
            {"type": "bulletList", "content": [{"type": "listItem", "content": [para(text("a"))]}]}])

    def test_an_empty_file_is_an_empty_document(self):
        r = self.run_it(self.file(""), "1")
        self.assertEqual((r.returncode, json.loads(r.stdout.decode("utf-8"))),
                         (0, {"type": "doc", "version": 1, "content": []}))

    def test_missing_arguments_print_the_usage(self):
        self.refused(self.run_it(), "usage: md2adf.py <comment.md> <issue-id>", 2)
        self.refused(self.run_it(self.file("x")), "usage: md2adf.py <comment.md> <issue-id>", 2)

    def test_a_file_that_is_missing_a_folder_or_not_utf8_is_one_line(self):
        missing = os.path.join(self.tmp, "nope.md")
        self.refused(self.run_it(missing, "1"), "md2adf.py: cannot read %s: No such file or directory" % missing, 1)
        self.refused(self.run_it(self.tmp, "1"), "md2adf.py: cannot read %s: Is a directory" % self.tmp, 1)
        bad = self.file(b"caf\xe9\n")
        self.refused(self.run_it(bad, "1"), "md2adf.py: %s is not UTF-8 text" % bad, 1)

    def test_a_line_break_in_the_file_name_never_adds_a_second_error_line(self):
        self.refused(self.run_it(os.path.join(self.tmp, "nope\nmd2adf.py: fake"), "1"), "nope\\nmd2adf.py: fake", 1)

    def test_a_reader_that_left_is_one_line(self):
        path = self.file("word " * 60000)
        for read_first in (0, 10):
            p = subprocess.Popen([sys.executable, "-I", MD2ADF, path, "1"],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if read_first:
                p.stdout.read(read_first)
            p.stdout.close()
            err = p.stderr.read().decode("utf-8")
            p.stderr.close()
            self.assertEqual((p.wait(), err), (1, "md2adf.py: cannot write the document: Broken pipe\n"), read_first)

    def test_a_stdout_that_cannot_hold_the_text_gets_the_same_document_escaped(self):
        path = self.file("ทดสอบ → **ok**\n")
        plain = self.run_it(path, "1", PYTHONIOENCODING="utf-8")
        ascii_only = self.run_it(path, "1", PYTHONIOENCODING="ascii")
        self.assertEqual((ascii_only.returncode, ascii_only.stderr), (0, b""))
        self.assertEqual(json.loads(ascii_only.stdout.decode("ascii")), json.loads(plain.stdout.decode("utf-8")))
        self.assertIn("ทดสอบ".encode("utf-8"), plain.stdout)


if __name__ == "__main__":
    unittest.main()
