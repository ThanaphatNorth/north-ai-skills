"""The seams of validate_skill.py: checks that return findings, and URL fetching passed in as an argument."""
import contextlib
import io
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from skill_case import SkillCase, reference  # noqa: E402
import validate_skill as vs  # noqa: E402

CITED = {"https://ok.dev/a": {"g.md"}, "https://blocked.dev/a": {"g.md"}, "https://slow.dev/a": {"g.md"},
         "https://botwall.dev/p": {"g.md", "h.md"}, "https://dead.dev/p": {"h.md"}}
ANSWERS = {"https://ok.dev/a": 200, "https://blocked.dev/a": 999, "https://slow.dev/a": "curl-fail",
           "https://botwall.dev/p": 404, "https://dead.dev/p": 404, "https://botwall.dev/": 503,
           "https://dead.dev/": 200}
UNREACHABLE = "unreachable from here (site blocks bots or times out) "


class InjectedFetchers(unittest.TestCase):
    def test_check_url_uses_the_fetchers_it_is_given(self):
        seen = []

        def primary(url):
            seen.append("primary " + url)
            return url, 403

        def retry(url):
            seen.append("retry " + url)
            return 200

        self.assertEqual(vs.check_url("https://a.dev/x", primary=primary, retry=retry), ("https://a.dev/x", 200))
        self.assertEqual(seen, ["primary https://a.dev/x", "retry https://a.dev/x"])


class ClassifyUrls(unittest.TestCase):
    def test_statuses_become_dead_errors_and_blocked_or_unreachable_warnings(self):
        probed = []

        def root_fails(url):
            probed.append(url)
            return "botwall" in url

        results = [(u, ANSWERS[u]) for u in sorted(CITED)]
        report = vs.classify_urls(results, CITED, root_fails)
        self.assertEqual(report.dead, ["404 https://dead.dev/p (in h.md)"])
        self.assertEqual(report.warnings, [
            "blocked 999 https://blocked.dev/a (in g.md)",
            UNREACHABLE + "404 https://botwall.dev/p (in g.md, h.md)",
            UNREACHABLE + "curl-fail https://slow.dev/a (in g.md)"])
        self.assertEqual(report.results, [
            ("https://blocked.dev/a", 999), ("https://botwall.dev/p", "unreachable:404"),
            ("https://dead.dev/p", 404), ("https://ok.dev/a", 200), ("https://slow.dev/a", "unreachable:curl-fail")])
        self.assertEqual(probed, ["https://botwall.dev/p", "https://dead.dev/p"])
        self.assertEqual(results[1], ("https://botwall.dev/p", 404), "the input list is not rewritten")


class CheckUrls(unittest.TestCase):
    def test_every_url_and_each_404_host_root_goes_through_the_fetcher(self):
        fetched = []

        def fetch(url):
            fetched.append(url)
            return url, ANSWERS[url]

        report = vs.check_urls(CITED, fetch)
        self.assertEqual(sorted(fetched), sorted(ANSWERS))
        self.assertEqual(report.dead, ["404 https://dead.dev/p (in h.md)"])
        self.assertEqual(vs.url_summary(report), "urls: 1 ok, 1 dead, 3 blocked/unreachable from here")


class CheckSkill(SkillCase):
    def test_findings_come_back_as_data(self):
        self.skill_md(front="name: other\ndescription: A demo skill.")
        self.write("references/guide.md", reference(lines=10, extra=["https://a.dev/x"]))
        self.write("references/extra.md", reference(extra=["https://a.dev/x", "https://b.dev/y"]))
        report = vs.check_skill(self.skill)
        self.assertEqual(report.findings.errors, ["SKILL.md: name 'other' != folder 'demo'"])
        self.assertEqual(report.findings.warnings, ["references/extra.md is not routed from SKILL.md",
                                                    "guide.md: 10 lines (expected 120-750)"])
        self.assertEqual(report.refs, ["extra.md", "guide.md"])
        self.assertEqual(report.urls, {"https://a.dev/x": {"extra.md", "guide.md"}, "https://b.dev/y": {"extra.md"}})

    def test_check_reference_reads_no_files(self):
        found = vs.check_reference("x.md", "no title\n`gone.md` `kept.md`", ["kept.md", "x.md"])
        self.assertEqual(found.errors, ["x.md: must start with '# Title'",
                                        "x.md: missing '> Read when:' line near the top",
                                        "x.md: missing '## Sources' section"])
        self.assertEqual(found.warnings, ["x.md: 2 lines (expected 120-750)",
                                          "x.md: cross-links missing sibling gone.md"])


class Run(SkillCase):
    def test_run_takes_arguments_and_a_fetcher_and_returns_the_exit_code(self):
        self.write("references/guide.md", reference(extra=["https://dead.dev/p"]))
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = vs.run([self.skill, "--urls"], fetch=lambda url: (url, ANSWERS[url]))
        self.assertEqual((code, out.getvalue().splitlines()), (1, [
            "references: 1 files, 1 distinct URLs", "urls: 0 ok, 1 dead, 0 blocked/unreachable from here",
            "ERROR dead url: 404 https://dead.dev/p (in guide.md)", "RESULT: FAIL (1 errors, 0 warnings)"]))


if __name__ == "__main__":
    unittest.main()
