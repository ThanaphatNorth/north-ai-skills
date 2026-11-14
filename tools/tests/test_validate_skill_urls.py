"""Characterization of the URL side of validate_skill.py, with the network replaced by fakes."""
import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from skill_case import SkillCase, reference  # noqa: E402
import validate_skill as vs  # noqa: E402


class ExtractUrls(unittest.TestCase):
    def test_prose_and_markdown_links(self):
        text = "See https://a.dev/x, and [b](https://b.dev/y). Also (https://c.dev/z)."
        self.assertEqual(vs.extract_urls(text), ["https://a.dev/x", "https://b.dev/y", "https://c.dev/z"])

    def test_balanced_parentheses_are_kept(self):
        text = ("- https://gsap.com/docs/v3/GSAP/gsap.matchMedia()\n"
                "- (https://developer.apple.com/documentation/swiftui/view/glasseffect(_:in:))")
        self.assertEqual(vs.extract_urls(text), [
            "https://gsap.com/docs/v3/GSAP/gsap.matchMedia()",
            "https://developer.apple.com/documentation/swiftui/view/glasseffect(_:in:)"])

    def test_trailing_punctuation_is_dropped(self):
        text = "https://a.dev/x. https://a.dev/y; https://a.dev/z: **https://a.dev/w** https://a.dev/v)."
        self.assertEqual(vs.extract_urls(text), [
            "https://a.dev/x", "https://a.dev/y", "https://a.dev/z", "https://a.dev/w", "https://a.dev/v"])

    def test_url_opening_a_code_span_is_skipped(self):
        self.assertEqual(vs.extract_urls("`https://api.dev/v1` but https://docs.dev/v1"), ["https://docs.dev/v1"])

    def test_url_later_in_a_code_span_is_still_read(self):
        self.assertEqual(vs.extract_urls("`curl https://api.dev/v1`"), ["https://api.dev/v1"])

    def test_placeholders_are_skipped(self):
        text = "https://example.com/a https://api.dev/users/{id} https://www.example.com"
        self.assertEqual(vs.extract_urls(text), [])

    def test_angle_placeholder_cuts_the_url_short(self):
        self.assertEqual(vs.extract_urls("https://api.dev/users/<id>/posts"), ["https://api.dev/users/"])

    def test_duplicates_and_table_cells(self):
        self.assertEqual(vs.extract_urls("| https://a.dev/x| https://a.dev/x |"), ["https://a.dev/x", "https://a.dev/x"])


class CheckUrl(unittest.TestCase):
    def status(self, first, retry=None):
        """check_url's status when urllib answers `first` and curl answers `retry` (None: curl must not run)."""
        curl = mock.Mock(return_value=retry)
        with mock.patch.object(vs, "_urllib_status", lambda url: (url, first)), \
                mock.patch.object(vs, "curl_status", curl):
            url, status = vs.check_url("https://a.dev/x")
        self.assertEqual(url, "https://a.dev/x")
        self.assertEqual(curl.call_count, 0 if retry is None else 1)
        return status

    def test_ok_answer_is_not_retried(self):
        self.assertEqual(self.status(200), 200)
        self.assertEqual(self.status(301), 301)

    def test_http_error_is_retried_and_the_lower_code_wins(self):
        self.assertEqual(self.status(403, retry=200), 200)
        self.assertEqual(self.status(404, retry=404), 404)
        self.assertEqual(self.status(404, retry=500), 404)

    def test_exception_is_retried_and_any_curl_code_wins(self):
        self.assertEqual(self.status("URLError", retry=200), 200)
        self.assertEqual(self.status("URLError", retry=503), 503)

    def test_failed_retry_keeps_the_first_status(self):
        self.assertEqual(self.status(403, retry="curl-fail"), 403)
        self.assertEqual(self.status("timeout", retry="curl-fail"), "timeout")
        self.assertEqual(self.status("URLError", retry="TimeoutExpired"), "URLError")


CITED = ["https://ok.dev/a", "https://dead.dev/gone", "https://blocked.dev/a", "https://limited.dev/a",
         "https://slow.dev/a", "https://botwall.dev/page", "https://broken.dev/a", "https://dns.dev/a"]
STATUSES = {
    "https://ok.dev/a": 200,
    "https://dead.dev/gone": 404, "https://dead.dev/": 200,
    "https://blocked.dev/a": 403,
    "https://limited.dev/a": 429,
    "https://slow.dev/a": "timeout",
    "https://botwall.dev/page": 404, "https://botwall.dev/": 403,
    "https://broken.dev/a": 500,
    "https://dns.dev/a": "URLError",
}
IN = " (in guide.md)"
UNREACHABLE = "WARN  unreachable from here (site blocks bots or times out) "


class UrlRun(SkillCase):
    def setUp(self):
        super().setUp()
        self.write("references/guide.md", reference(extra=CITED))

    def test_without_the_flag_nothing_is_fetched(self):
        self.assertEqual(self.run_main(statuses={}), (0, [
            "references: 1 files, 8 distinct URLs", "RESULT: PASS (0 errors, 0 warnings)"]))
        self.assertEqual(self.calls, [])

    def test_statuses_are_sorted_into_ok_dead_blocked_and_unreachable(self):
        code, lines = self.run_main("--urls", statuses=STATUSES)
        self.assertEqual(code, 1)
        self.assertEqual(lines, [
            "references: 1 files, 8 distinct URLs",
            "urls: 1 ok, 3 dead, 4 blocked/unreachable from here",
            "WARN  blocked 403 https://blocked.dev/a" + IN,
            UNREACHABLE + "404 https://botwall.dev/page" + IN,
            "WARN  blocked 429 https://limited.dev/a" + IN,
            UNREACHABLE + "timeout https://slow.dev/a" + IN,
            "ERROR dead url: 500 https://broken.dev/a" + IN,
            "ERROR dead url: 404 https://dead.dev/gone" + IN,
            "ERROR dead url: URLError https://dns.dev/a" + IN,
            "RESULT: FAIL (3 errors, 4 warnings)"])

    def test_host_root_is_probed_once_per_host_and_only_for_a_404(self):
        self.write("references/guide.md", reference(extra=[
            "https://botwall.dev/page", "https://botwall.dev/other", "https://ok.dev/a"]))
        statuses = dict(STATUSES, **{"https://botwall.dev/other": 404})
        code, lines = self.run_main("--urls", statuses=statuses)
        self.assertEqual((code, lines[1]), (0, "urls: 1 ok, 0 dead, 2 blocked/unreachable from here"))
        self.assertEqual(sorted(self.calls), ["https://botwall.dev/", "https://botwall.dev/other",
                                              "https://botwall.dev/page", "https://ok.dev/a"])

    def test_all_urls_ok(self):
        code, lines = self.run_main("--urls", statuses={u: 200 for u in CITED})
        self.assertEqual((code, lines), (0, [
            "references: 1 files, 8 distinct URLs", "urls: 8 ok, 0 dead, 0 blocked/unreachable from here",
            "RESULT: PASS (0 errors, 0 warnings)"]))

    def test_a_url_names_every_file_that_cites_it(self):
        self.write("references/also.md", reference(extra=["https://broken.dev/a"]))
        self.skill_md(body="`references/guide.md` `references/also.md`\n")
        code, lines = self.run_main("--urls", statuses=STATUSES)
        self.assertIn("ERROR dead url: 500 https://broken.dev/a (in also.md, guide.md)", lines)

    def test_report_lists_every_url_with_its_final_status(self):
        report = os.path.join(self.tmp, "out", "urls.tsv")
        self.run_main("--urls", "--report", report, statuses=STATUSES)
        with open(report) as fh:
            rows = fh.read().splitlines()
        self.assertEqual(rows, [
            "403\thttps://blocked.dev/a\tguide.md",
            "unreachable:404\thttps://botwall.dev/page\tguide.md",
            "500\thttps://broken.dev/a\tguide.md",
            "404\thttps://dead.dev/gone\tguide.md",
            "URLError\thttps://dns.dev/a\tguide.md",
            "429\thttps://limited.dev/a\tguide.md",
            "200\thttps://ok.dev/a\tguide.md",
            "unreachable:timeout\thttps://slow.dev/a\tguide.md"])

    def test_skill_without_urls_skips_the_url_step(self):
        self.write("references/guide.md", reference())
        self.assertEqual(self.run_main("--urls", statuses={}), (0, [
            "references: 1 files, 0 distinct URLs", "RESULT: PASS (0 errors, 0 warnings)"]))


if __name__ == "__main__":
    unittest.main()
