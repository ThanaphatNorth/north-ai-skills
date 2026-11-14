"""Edge inputs of local_board_core: every malformed card, query or change is a BoardError, never another exception.

  python3 -m unittest discover -s skills/workflow/scripts/tests -p 'test_*.py'
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test_local_board_core import CARD, NOW, card, core  # noqa: E402

HUGE = "9" * 5000  # longer than Python's limit for turning a string into an int (4300 digits since 3.11)
AT_LIMIT = "9" * 4300  # int() takes it, but one more than it has 4301 digits and can no longer be printed


class Parse(unittest.TestCase):
    def test_a_header_line_without_a_name_is_refused_with_its_line_number(self):
        for line in ("no colon here", ": value", "two words: x"):
            with self.assertRaises(core.BoardError) as e:
                core.parse_card("TASK-8", "---\ntitle: ok\n%s\n---\n" % line)
            self.assertIn("TASK-8 line 3: expected 'name: value', got %r" % line, str(e.exception))

    def test_text_under_comments_before_the_first_entry_is_refused(self):
        with self.assertRaises(core.BoardError) as e:
            core.parse_card("TASK-8", CARD.replace("## Comments\n", "## Comments\nloose words\n"))
        self.assertIn("before the first '### c<n>", str(e.exception))

    def test_a_template_note_under_comments_is_not_text(self):
        noted = core.parse_card("TASK-8", CARD.replace("## Comments\n", "## Comments\n<!-- how to\ncomment -->\n"))
        self.assertEqual([c["id"] for c in noted["comments"]], ["c1"])

    def test_a_card_with_only_a_header_has_an_empty_body_and_no_comments(self):
        bare = core.parse_card("TASK-8", "---\ntitle: bare\n---\n")
        self.assertEqual((bare["fields"], bare["body"], bare["comments"]), ({"title": "bare"}, "", []))
        self.assertEqual(core.summary_line(bare), "TASK-8 |  |  |  |  | bare")

    def test_header_reads_a_field_as_text_and_listed_as_a_list(self):
        c = card()
        self.assertEqual((core.header(c, "labels"), core.header(c, "title"), core.header(c, "nope")),
                         ("ai-queue, billing", "Total is wrong on the invoice", ""))
        self.assertEqual((core.listed(c, "links"), core.listed(c, "severity"), core.listed(c, "nope")),
                         (["TASK-1"], ["Level 4"], []))


class Query(unittest.TestCase):
    def test_an_unbalanced_quote_is_a_board_error(self):
        with self.assertRaises(core.BoardError) as e:
            core.parse_query('title="no end')
        self.assertIn("query: No closing quotation", str(e.exception))

    def test_an_age_term_never_matches_a_card_without_a_readable_updated(self):
        for updated in ("yesterday", "2026-13-45 99:99", ""):
            c = card(text=CARD.replace("updated: 2026-11-12 15:00", "updated: " + updated))
            self.assertFalse(core.matches(c, core.parse_query("age>1m"), NOW), updated)
            self.assertFalse(core.matches(c, core.parse_query("age<9d"), NOW), updated)
            self.assertTrue(core.matches(c, core.parse_query("status=todo"), NOW), updated)

    def test_an_age_too_long_to_be_a_number_is_a_board_error(self):
        for digits in (HUGE, AT_LIMIT):
            with self.assertRaises(core.BoardError) as e:
                core.parse_query("age>%sd" % digits)
            self.assertIn("%d digits" % len(digits), str(e.exception))
        self.assertEqual(core.parse_query("age<%sm" % ("9" * 4299))["ages"], [("<", int("9" * 4299) * 60)])

    def test_a_number_too_long_to_be_one_sorts_last_and_stops_no_search(self):
        huge = card("TASK-1", CARD.replace("rank: 20", "rank: " + HUGE))
        got = core.sort_cards([huge, card("TASK-2"), card("TASK-3", CARD.replace("rank: 20", "rank: 3"))],
                              core.parse_query(""))
        self.assertEqual([c["key"] for c in got], ["TASK-3", "TASK-2", "TASK-1"])
        by_field = core.sort_cards([huge, card("TASK-2")], core.parse_query("sort=-rank"))
        self.assertEqual([c["key"] for c in by_field], ["TASK-1", "TASK-2"])

    def test_sort_ascending_by_a_list_field_and_cards_without_it_first(self):
        a = card("TASK-1", CARD.replace("labels: ai-queue, billing", "labels: zeta"))
        b = card("TASK-2", CARD.replace("labels: ai-queue, billing\n", ""))
        got = core.sort_cards([a, card("TASK-3"), b], core.parse_query("sort=labels"))
        self.assertEqual([c["key"] for c in got], ["TASK-2", "TASK-3", "TASK-1"])


class Changes(unittest.TestCase):
    def test_a_section_heading_with_a_line_break_is_refused(self):
        for heading in ("Notes\nmore", "Notes\r", "A\n## Comments"):
            with self.assertRaises(core.BoardError) as e:
                core.edit(card(), core.Change(sections={heading: "text"}), NOW)
            self.assertIn("one line", str(e.exception))

    def test_an_empty_last_section_is_refused_because_it_would_not_read_back(self):
        with self.assertRaises(core.BoardError) as e:
            core.edit(card(), core.Change(sections={"Notes": "\n"}), NOW)
        self.assertIn("would not read back the same; nothing was written", str(e.exception))

    def test_a_section_in_the_middle_is_replaced_and_its_neighbours_kept(self):
        c = core.edit(card(), core.Change(sections={"description": "New text."}), NOW)
        self.assertEqual(c["body"], "## Description\nNew text.\n\n## Acceptance criteria\n"
                                    "- total = sum - discount\n- shown with 2 decimals")

    def test_a_first_section_on_a_card_with_an_empty_body(self):
        c = core.edit(core.parse_card("TASK-8", "---\ntitle: bare\n---\n"), core.Change(sections={"Notes": "n"}), NOW)
        self.assertEqual((c["body"], c["fields"]["labels"]), ("## Notes\nn", []))

    def test_a_video_path_the_link_cannot_hold_is_refused(self):
        for path in ("TASK-7/a]b.mp4", "TASK-7/a(b).mp4", "../[x].mp4"):
            with self.assertRaises(core.BoardError) as e:
                core.add_comment(card(), "proof\n::video %s" % path, NOW)
            self.assertIn("::video " + path, str(e.exception))

    def test_a_bracket_the_link_can_hold_is_no_reason_to_refuse_a_video(self):
        for path in ("TASK-7/take[1.mp4", "TASK-7/[final]/x.mp4", "TASK-7/take(1.mp4"):
            c, _ = core.add_comment(card(), "::video %s" % path, NOW)
            self.assertEqual(core.video_paths(c["comments"][-1]["text"]), [path])

    def test_a_comment_id_too_long_to_be_a_number_is_a_board_error(self):
        for digits in (HUGE, AT_LIMIT):
            long_id = core.parse_card("TASK-8", CARD + "\n### c%s · 2026-11-12 09:00 · bob\nhi\n" % digits)
            with self.assertRaises(core.BoardError) as e:
                core.add_comment(long_id, "next", NOW)
            self.assertIn("%d digits" % len(digits), str(e.exception))

    def test_the_first_comment_on_a_card_is_c1(self):
        c, cid = core.add_comment(core.parse_card("TASK-8", "---\ntitle: bare\n---\n"), "\n\nhello\n\n", NOW)
        self.assertEqual((cid, c["comments"][0]["text"], c["fields"]["updated"]), ("c1", "hello", "2026-11-12 18:00"))

    def test_change_defaults_ask_for_nothing_but_the_timestamp(self):
        c = core.edit(card(), core.Change(), NOW)
        self.assertEqual({k: v for k, v in c["fields"].items() if k != "updated"},
                         {k: v for k, v in card()["fields"].items() if k != "updated"})
        self.assertEqual((c["body"], c["comments"]), (card()["body"], card()["comments"]))


if __name__ == "__main__":
    unittest.main()
