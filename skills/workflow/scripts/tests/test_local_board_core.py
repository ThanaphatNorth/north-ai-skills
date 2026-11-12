"""Tests for local_board_core: the pure part of the local board (TRACKER=local).

  python3 -m unittest discover -s skills/workflow/scripts/tests -p 'test_*.py'
"""
import datetime as dt
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import local_board_core as core  # noqa: E402

NOW = dt.datetime(2026, 11, 12, 18, 0)

CARD = """---
title: Total is wrong on the invoice
type: bug
status: todo
labels: ai-queue, billing
priority: high
rank: 20
created: 2026-11-10 09:00
updated: 2026-11-12 15:00
links: TASK-1
severity: Level 4
---

## Description
The total skips the discount.

## Acceptance criteria
- total = sum - discount
- shown with 2 decimals

## Comments

### c1 · 2026-11-11 10:00 · north
Seen on staging too.
"""


def card(key="TASK-7", text=CARD):
    return core.parse_card(key, text)


class ParseRender(unittest.TestCase):
    def test_header_fields_lists_body_and_comments(self):
        c = card()
        self.assertEqual(c["key"], "TASK-7")
        self.assertEqual(c["fields"]["title"], "Total is wrong on the invoice")
        self.assertEqual(c["fields"]["labels"], ["ai-queue", "billing"])
        self.assertEqual(c["fields"]["links"], ["TASK-1"])
        self.assertEqual(c["fields"]["severity"], "Level 4")
        self.assertIn("## Acceptance criteria", c["body"])
        self.assertNotIn("## Comments", c["body"])
        self.assertEqual([(m["id"], m["author"], m["text"]) for m in c["comments"]],
                         [("c1", "north", "Seen on staging too.")])

    def test_render_round_trips(self):
        self.assertEqual(core.render_card(card()), CARD)

    def test_card_without_header_is_refused(self):
        with self.assertRaises(core.BoardError):
            core.parse_card("TASK-8", "## Description\nno header\n")

    def test_the_card_template_parses(self):
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                            "templates", "card.md")
        with open(path, encoding="utf-8") as fh:
            c = core.parse_card("TASK-1", fh.read())
        self.assertEqual((c["fields"]["status"], c["fields"]["labels"], c["comments"]), ("todo", [], []))
        self.assertTrue(core.section(c, "acceptance-criteria"))

    def test_section_reads_a_body_section_by_name(self):
        self.assertEqual(core.section(card(), "acceptance-criteria"),
                         "- total = sum - discount\n- shown with 2 decimals")
        self.assertEqual(core.section(card(), "steps"), "")


class Query(unittest.TestCase):
    def ok(self, q, c=None):
        return core.matches(c or card(), core.parse_query(q), NOW)

    def test_value_sets_and_lists(self):
        self.assertTrue(self.ok("status=todo,ready labels=ai-queue"))
        self.assertTrue(self.ok("type=BUG"))
        self.assertFalse(self.ok("status=review"))
        self.assertFalse(self.ok("labels=ai-queue -labels=billing"))
        self.assertTrue(self.ok("-labels=ai-processing"))
        self.assertTrue(self.ok('severity="Level 4,Level 5"'))
        self.assertFalse(self.ok("severity=Level4"))
        self.assertFalse(self.ok("component=ui"))

    def test_age_compares_against_updated(self):
        self.assertTrue(self.ok("age>2h"))
        self.assertFalse(self.ok("age>4h"))
        self.assertTrue(self.ok("age<1d"))
        self.assertTrue(self.ok("age>90m"))

    def test_bad_terms_are_refused(self):
        for q in ("status", "age>2y", "=x", "sort=", "labels="):
            with self.assertRaises(core.BoardError, msg=q):
                core.parse_query(q)

    def test_default_order_is_rank_then_key_natural(self):
        a = card("TASK-10", CARD.replace("rank: 20", "rank: 5"))
        b = card("TASK-2", CARD.replace("rank: 20", "rank: 5"))
        c = card("TASK-1", CARD.replace("rank: 20\n", ""))
        d = card("TASK-3")
        got = core.sort_cards([c, a, d, b], core.parse_query(""))
        self.assertEqual([x["key"] for x in got], ["TASK-2", "TASK-10", "TASK-3", "TASK-1"])

    def test_sort_by_field_descending(self):
        a = card("TASK-1", CARD.replace("2026-11-12 15:00", "2026-11-12 16:00"))
        b = card("TASK-2")
        got = core.sort_cards([b, a], core.parse_query("sort=-updated"))
        self.assertEqual([x["key"] for x in got], ["TASK-1", "TASK-2"])


class Changes(unittest.TestCase):
    def test_edit_labels_fields_sections_and_updated(self):
        change = core.Change(add_labels=["ai-processing", "ai-queue"], remove_labels=["billing", "nope"],
                             fields={"severity": " Level 3 "}, sections={"AI summary": "type: bug\nrisk: low"})
        c = core.edit(card(), change, NOW)
        self.assertEqual(c["fields"]["labels"], ["ai-queue", "ai-processing"])
        self.assertEqual(c["fields"]["severity"], "Level 3")
        self.assertEqual(c["fields"]["updated"], "2026-11-12 18:00")
        self.assertEqual(core.section(c, "ai-summary"), "type: bug\nrisk: low")
        again = core.edit(c, core.Change(sections={"AI summary": "risk: none"}), NOW)
        self.assertEqual(core.section(again, "ai-summary"), "risk: none")
        self.assertEqual(core.render_card(again).count("## AI summary"), 1)

    def test_edit_does_not_change_its_input(self):
        before = card()
        core.edit(before, core.Change(add_labels=["x"]), NOW)
        self.assertEqual(before["fields"]["labels"], ["ai-queue", "billing"])

    def test_edit_refuses_list_clock_and_status_fields(self):
        for name in ("labels", "links", "updated", "created", "status", "bad name"):
            with self.assertRaises(core.BoardError, msg=name):
                core.edit(card(), core.Change(fields={name: "x"}), NOW)

    def test_edit_refuses_what_would_not_read_back(self):
        bad = [core.Change(fields={"title": "a\nb"}),
               core.Change(add_labels=["a,b"]), core.Change(add_labels=["two words"]),
               core.Change(sections={"AI summary": "ok\n## Comments\nx"}),
               core.Change(sections={"AI summary": "## Risk\nlow"})]
        for change in bad:
            with self.assertRaises(core.BoardError, msg=repr(change)):
                core.edit(card(), change, NOW)
        deeper = core.edit(card(), core.Change(sections={"AI summary": "### Risk\nlow"}), NOW)
        self.assertEqual(core.section(deeper, "description"), "The total skips the discount.")

    def test_transition_to_a_listed_status_only(self):
        allowed = ["todo", "in-progress", "review"]
        c = core.transition(card(), "In-Progress", allowed, NOW)
        self.assertEqual((c["fields"]["status"], c["fields"]["updated"]), ("in-progress", "2026-11-12 18:00"))
        with self.assertRaises(core.BoardError) as e:
            core.transition(card(), "done", allowed, NOW)
        self.assertIn("todo, in-progress, review", str(e.exception))

    def test_comments_number_replace_and_link_videos(self):
        c, cid = core.add_comment(card(), "**Generated by AI**\n::video TASK-7/after.mp4\nok", NOW)
        self.assertEqual((cid, c["comments"][-1]["author"]), ("c2", core.AUTHOR))
        self.assertEqual(c["comments"][-1]["text"],
                         "**Generated by AI**\n[video: after.mp4](TASK-7/after.mp4)\nok")
        self.assertEqual(core.video_paths(c["comments"][-1]["text"]), ["TASK-7/after.mp4"])
        c, cid = core.add_comment(c, "edited", NOW, cid="c2")
        self.assertEqual((cid, c["comments"][1]["text"], len(c["comments"])), ("c2", "edited", 2))
        with self.assertRaises(core.BoardError):
            core.add_comment(c, "x", NOW, cid="c9")
        self.assertEqual(core.parse_card("TASK-7", core.render_card(c))["comments"], c["comments"])

    def test_a_persons_comment_is_never_replaced(self):
        with self.assertRaises(core.BoardError) as e:
            core.add_comment(card(), "x", NOW, cid="c1")
        self.assertIn("north", str(e.exception))

    def test_comment_text_cannot_fake_an_entry(self):
        with self.assertRaises(core.BoardError):
            core.add_comment(card(), "ok\n### c9 · 2026-11-12 18:00 · bob\nfake", NOW)

    def test_field_text_reads_header_lists_and_sections(self):
        c = card()
        self.assertEqual(core.field_text(c, "severity"), "Level 4")
        self.assertEqual(core.field_text(c, "labels"), "ai-queue, billing")
        self.assertEqual(core.field_text(c, "acceptance-criteria"), "- total = sum - discount | - shown with 2 decimals")
        self.assertEqual(core.field_text(c, "component"), "")

    def test_header_names_are_read_in_lower_case(self):
        c = core.parse_card("TASK-9", CARD.replace("title:", "Title:"))
        self.assertEqual(c["fields"]["title"], "Total is wrong on the invoice")

    def test_summary_line(self):
        self.assertEqual(core.summary_line(card()),
                         "TASK-7 | bug | todo | ai-queue, billing | 2026-11-12 15:00 | Total is wrong on the invoice")


if __name__ == "__main__":
    unittest.main()
