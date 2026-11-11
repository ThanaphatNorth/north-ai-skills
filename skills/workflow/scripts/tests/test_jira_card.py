"""Tests for jira-card.sh: the fields triage needs (labels, links, parent, config field ids) with a fake curl.

  python3 -m unittest discover -s skills/workflow/scripts/tests -p 'test_*.py'
"""
import json
import os
import subprocess
import unittest

from fakejira import TOKEN, fake_project

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


if __name__ == "__main__":
    unittest.main()
