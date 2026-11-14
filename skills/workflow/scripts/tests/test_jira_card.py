"""Tests for jira-card.sh: the fields triage needs (labels, links, parent, config field ids) with a fake curl.

  python3 -m unittest discover -s skills/workflow/scripts/tests -p 'test_*.py'
"""
import json
import os
import subprocess
import unittest

from fakejira import SITE, TOKEN, calls, fake_project, requests, run_script

SCRIPTS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CARD = os.path.join(SCRIPTS, "jira-card.sh")

ISSUE = {
    "key": "ABC-7", "id": "10077",
    "names": {"customfield_10050": "Severity", "customfield_10060": "Expected result",
              "customfield_10070": "Environments", "customfield_10080": "Empty one"},
    "fields": {
        "summary": "Total is wrong", "issuetype": {"name": "Bug"},
        "status": {"name": "To Do", "id": "10001"}, "priority": {"name": "Medium"},
        "labels": ["ai-queue", "ai-needs-review"],
        "parent": {"key": "ABC-1", "fields": {"summary": "Billing epic"}},
        "issuelinks": [
            {"type": {"outward": "blocks", "inward": "is blocked by"},
             "outwardIssue": {"key": "ABC-9", "fields": {"summary": "Rounding", "status": {"name": "Done"}}}},
            {"type": {"outward": "relates to", "inward": "relates to"},
             "inwardIssue": {"key": "ABC-3", "fields": {"summary": "Spec page", "status": {"name": "To Do"}}}},
        ],
        "customfield_10050": {"value": "Level 4", "child": {"value": "Minor"}},
        "customfield_10060": {"type": "doc"},
        "customfield_10070": [{"value": "QA"}, {"value": "Dev"}],
        "customfield_10080": None,
    },
    "renderedFields": {"customfield_10060": "<p>Shows 100.00</p><p>for <b>2</b> items</p>"},
}


class Card(unittest.TestCase):
    def setUp(self):
        body = json.dumps(ISSUE)
        assert "'" not in body  # it goes inside single quotes in the fake curl
        self.root, self.env, self.log = fake_project("""
            *) printf '%%s' '%s' ;;
        """ % body)

    def run_card(self, *args):
        return subprocess.run(["bash", CARD, *args], capture_output=True, text=True, cwd=self.root, env=self.env)

    def test_prints_labels_links_parent_and_fields(self):
        r = self.run_card("ABC-7", "customfield_10050,customfield_10060,customfield_10070,customfield_10080")
        self.assertEqual(r.returncode, 0, r.stderr)
        out = r.stdout.splitlines()
        self.assertEqual(out[0], "ABC-7  [Bug / To Do (10001)]  id=10077  priority Medium")
        self.assertIn("LABELS: ai-queue, ai-needs-review", out)
        self.assertIn("PARENT: ABC-1 Billing epic", out)
        self.assertIn("LINK: blocks ABC-9 [Done] Rounding", out)
        self.assertIn("LINK: relates to ABC-3 [To Do] Spec page", out)
        self.assertIn("FIELD customfield_10050 (Severity): Level 4 / Minor", out)
        self.assertIn("FIELD customfield_10060 (Expected result): Shows 100.00 | for 2 items", out)
        self.assertIn("FIELD customfield_10070 (Environments): QA, Dev", out)
        self.assertIn("FIELD customfield_10080 (Empty one): (empty)", out)

    def test_requests_the_listed_fields_and_never_prints_the_token(self):
        r = self.run_card("ABC-7", "customfield_10050")
        self.assertEqual(r.returncode, 0, r.stderr)
        call = open(self.log).read()
        self.assertIn("/rest/api/3/issue/ABC-7?fields=summary,status,issuetype,priority,labels,parent,issuelinks,customfield_10050&expand=renderedFields,names", call)
        self.assertNotIn(TOKEN, r.stdout + r.stderr + call)

    def test_no_field_list_still_prints_labels(self):
        r = self.run_card("ABC-7")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("LABELS: ai-queue, ai-needs-review", r.stdout)
        self.assertNotIn("FIELD ", r.stdout)

    def test_rejects_bad_field_list(self):
        r = self.run_card("ABC-7", "customfield_1;rm")
        self.assertEqual(r.returncode, 2)
        self.assertIn("field ids", r.stderr)


class CardErrors(unittest.TestCase):
    def test_usage(self):
        r = subprocess.run(["bash", CARD], capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)
        self.assertIn("usage", r.stderr)

    def test_jira_error_is_reported(self):
        root, env, _ = fake_project("""
            *) printf '{"errorMessages":["Issue does not exist"]}' ;;
        """)
        r = subprocess.run(["bash", CARD, "ABC-404"], capture_output=True, text=True, cwd=root, env=env)
        self.assertEqual(r.returncode, 1)
        self.assertIn("Issue does not exist", r.stdout + r.stderr)


class Pinned(unittest.TestCase):
    """The exact stdout, stderr and exit code of jira-card.sh before the scripts were hardened."""

    USAGE = "usage: %s <KEY> [fieldId,fieldId…]\n" % CARD

    def test_the_whole_card(self):
        root, env, _ = fake_project('*) reply 200 "$(cat "$B/issue.json")" ;;', bodies={"issue.json": ISSUE})
        r = run_script("jira-card.sh", ["ABC-7", "customfield_10050,customfield_10060,customfield_10099"], root, env)
        self.assertEqual((r.returncode, r.stderr), (0, ""))
        self.assertEqual(r.stdout, "\n".join([
            "ABC-7  [Bug / To Do (10001)]  id=10077  priority Medium",
            "LABELS: ai-queue, ai-needs-review",
            "PARENT: ABC-1 Billing epic",
            "LINK: blocks ABC-9 [Done] Rounding",
            "LINK: relates to ABC-3 [To Do] Spec page",
            "FIELD customfield_10050 (Severity): Level 4 / Minor",
            "FIELD customfield_10060 (Expected result): Shows 100.00 | for 2 items",
            "FIELD customfield_10099 (customfield_10099): (empty)",
        ]) + "\n")
        self.assertEqual(requests(root), [
            "GET " + SITE + "/rest/api/3/issue/ABC-7?fields=summary,status,issuetype,priority,labels,parent,"
            "issuelinks,customfield_10050,customfield_10060,customfield_10099&expand=renderedFields,names"])

    def test_a_card_with_no_priority_labels_parent_or_links(self):
        bare = {"key": "ABC-8", "id": "10078", "fields": {
            "summary": "Bare", "issuetype": {"name": "Task"}, "status": {"name": "Done", "id": "3"},
            "priority": None, "labels": [], "issuelinks": []}}
        root, env, _ = fake_project('*) reply 200 "$(cat "$B/issue.json")" ;;', bodies={"issue.json": bare})
        r = run_script("jira-card.sh", ["ABC-8"], root, env)
        self.assertEqual((r.returncode, r.stdout, r.stderr),
                         (0, "ABC-8  [Task / Done (3)]  id=10078\nLABELS: (none)\n", ""))

    def test_jira_error_body_is_one_error_line_on_stdout_and_exit_1(self):
        root, env, _ = fake_project("""*) reply 404 '{"errorMessages":["Issue does not exist"],"errors":{}}' ;;""")
        r = run_script("jira-card.sh", ["ABC-404"], root, env)
        self.assertEqual((r.returncode, r.stdout, r.stderr),
                         (1, 'ERROR {"errorMessages": ["Issue does not exist"], "errors": {}}\n', ""))

    def test_a_body_that_is_not_json_exits_1_with_nothing_on_stdout(self):
        root, env, _ = fake_project("*) reply 502 '<html>Bad gateway</html>' ;;")
        r = run_script("jira-card.sh", ["ABC-7"], root, env)
        self.assertEqual((r.returncode, r.stdout), (1, ""))

    def test_usage_needs_no_project(self):
        for args in ([], ["ABC-7", "customfield_1", "more"]):
            r = subprocess.run(["bash", CARD] + args, capture_output=True, text=True, cwd=os.path.dirname(CARD))
            self.assertEqual((r.returncode, r.stdout, r.stderr), (2, "", self.USAGE))

    def test_a_bad_field_list_is_refused_before_any_request(self):
        root, env, _ = fake_project("*) reply 200 '{}' ;;")
        r = run_script("jira-card.sh", ["ABC-7", "customfield_1;rm"], root, env)
        self.assertEqual((r.returncode, r.stdout), (2, ""))
        self.assertEqual(r.stderr, "jira-card.sh: field ids are comma-separated ids like customfield_10050, "
                                   "got 'customfield_1;rm'\n")
        self.assertEqual(calls(root), [])

    def test_keys_the_old_check_refused_stay_refused_before_any_request(self):
        root, env, _ = fake_project("*) reply 200 '{}' ;;")
        for bad in ("-x", "ABC/7", "../ABC-7", "ABC-7?expand=changelog"):
            r = run_script("jira-card.sh", [bad], root, env)
            self.assertEqual((r.returncode, r.stdout), (2, ""), bad)
        self.assertEqual(calls(root), [])


if __name__ == "__main__":
    unittest.main()
