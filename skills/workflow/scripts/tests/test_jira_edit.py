"""Tests for jira-edit.sh: request body (--dry-run, no credentials) and the PUT path with a fake curl.

  python3 -m unittest discover -s skills/workflow/scripts/tests -p 'test_*.py'
"""
import json
import os
import subprocess
import tempfile
import unittest

from fakejira import SITE, TOKEN, calls, fake_project, requests, run_script

SCRIPTS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EDIT = os.path.join(SCRIPTS, "jira-edit.sh")


def run(args, cwd=None, env=None):
    return subprocess.run(["bash", EDIT] + args, capture_output=True, text=True, cwd=cwd, env=env)


class DryRunBody(unittest.TestCase):
    def setUp(self):
        self.cwd = tempfile.mkdtemp()  # no .claude/90north-develop above it: dry-run must not need one

    def body(self, *opts):
        r = run(["ABC-1", "--dry-run", *opts], cwd=self.cwd)
        self.assertEqual(r.returncode, 0, r.stderr)
        return json.loads(r.stdout)

    def test_labels_add_and_remove_in_order(self):
        b = self.body("--remove-label", "ai-processing", "--add-label", "ai-do-now")
        self.assertEqual(b, {"update": {"labels": [{"remove": "ai-processing"}, {"add": "ai-do-now"}]}})

    def test_field_value_is_json(self):
        b = self.body("--field", 'customfield_10050={"value":"Level 4"}')
        self.assertEqual(b, {"fields": {"customfield_10050": {"value": "Level 4"}}})

    def test_field_md_becomes_adf(self):
        md = os.path.join(self.cwd, "summary.md")
        with open(md, "w", encoding="utf-8") as fh:
            fh.write("<!-- note -->\n**Type:** bug\n- `web/src/a.ts:12`\n")
        doc = self.body("--field-md", "customfield_10100=" + md)["fields"]["customfield_10100"]
        self.assertEqual(doc["type"], "doc")
        self.assertEqual([n["type"] for n in doc["content"]], ["paragraph", "bulletList"])
        self.assertNotIn("note", json.dumps(doc))
        self.assertEqual(doc["content"][0]["content"][0]["marks"], [{"type": "strong"}])

    def test_labels_and_fields_together(self):
        b = self.body("--add-label", "ai-need-dev", "--field", 'customfield_1="x"')
        self.assertEqual(set(b), {"update", "fields"})


class Rejects(unittest.TestCase):
    def assertRejected(self, *args, says):
        r = run(["ABC-1", "--dry-run", *args], cwd=tempfile.mkdtemp())
        self.assertEqual(r.returncode, 2, r.stdout)
        self.assertIn(says, r.stderr)
        self.assertEqual(r.stdout, "")

    def test_no_operation(self):
        r = run(["ABC-1"])
        self.assertEqual(r.returncode, 2)
        self.assertIn("usage", r.stderr)

    def test_unknown_option(self):
        self.assertRejected("--set", "x", says="unknown option")

    def test_missing_value(self):
        self.assertRejected("--add-label", says="needs a value")

    def test_label_with_space(self):
        self.assertRejected("--add-label", "ai do now", says="no spaces")

    def test_bad_json(self):
        self.assertRejected("--field", "customfield_1={oops", says="not JSON")

    def test_bad_field_id(self):
        self.assertRejected("--field", 'custom field="x"', says="field id")

    def test_labels_twice(self):
        self.assertRejected("--add-label", "a", "--field", 'labels=["b"]', says="labels")


class PutWithFakeCurl(unittest.TestCase):
    def setUp(self):
        self.root, self.env, self.log = fake_project("""
            *" PUT "*) printf '204' ;;
            *) printf '{"fields":{"labels":["ai-do-now","ai-queue"]}}' ;;
        """)

    def test_put_then_read_back_without_printing_the_token(self):
        r = run(["ABC-1", "--add-label", "ai-do-now"], cwd=self.root, env=self.env)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("HTTP 204", r.stdout)
        self.assertIn("ai-do-now,ai-queue", r.stdout)
        self.assertNotIn(TOKEN, r.stdout + r.stderr)
        calls = open(self.log).read().splitlines()
        self.assertTrue(any("PUT" in c and c.endswith("https://site.example.test/rest/api/3/issue/ABC-1") for c in calls), calls)
        self.assertFalse(any(TOKEN in c for c in calls), "token must reach curl on stdin, never in argv")


class Pinned(unittest.TestCase):
    """The exact stdout, stderr and exit code of jira-edit.sh before the scripts were hardened."""

    USAGE = ("usage: %s <KEY> [--dry-run] (--add-label L | --remove-label L | --field ID=JSON | --field-md ID=FILE)"
             "...\n" % EDIT)
    URL = SITE + "/rest/api/3/issue/ABC-1"

    def project(self, put_code="204", labels='{"fields":{"labels":["ai-do-now","ai-queue"]}}'):
        return fake_project("""
            *" PUT "*) reply %s ;;
            *) reply 200 '%s' ;;
        """ % (put_code, labels))[:2]

    def test_put_then_the_labels_read_back(self):
        root, env = self.project()
        r = run_script("jira-edit.sh", ["ABC-1", "--add-label", "ai-do-now", "--field", 'customfield_1="ก"'], root, env)
        self.assertEqual((r.returncode, r.stdout, r.stderr),
                         (0, "ABC-1 edit → HTTP 204 · labels now: ai-do-now,ai-queue\n", ""))
        self.assertEqual(requests(root), ["PUT " + self.URL, "GET " + self.URL + "?fields=labels"])
        put = calls(root)[0]
        self.assertEqual(put["data"], ['{"update": {"labels": [{"add": "ai-do-now"}]}, "fields": {"customfield_1": "ก"}}'])
        self.assertIn("Content-Type: application/json", put["argv"])

    def test_a_refused_edit_prints_the_code_and_exits_1(self):
        root, env = self.project(put_code="400")
        r = run_script("jira-edit.sh", ["ABC-1", "--add-label", "x"], root, env)
        self.assertEqual((r.returncode, r.stdout, r.stderr),
                         (1, "ABC-1 edit → HTTP 400 · labels now: ai-do-now,ai-queue\n", ""))

    def test_no_label_left_prints_none(self):
        root, env = self.project(labels='{"fields":{"labels":[]}}')
        r = run_script("jira-edit.sh", ["ABC-1", "--remove-label", "x"], root, env)
        self.assertEqual((r.returncode, r.stdout, r.stderr), (0, "ABC-1 edit → HTTP 204 · labels now: none\n", ""))

    def test_labels_that_cannot_be_read_back_print_a_question_mark(self):
        root, env = self.project(put_code="404", labels='{"errorMessages":["Issue does not exist"]}')
        r = run_script("jira-edit.sh", ["ABC-1", "--add-label", "x"], root, env)
        self.assertEqual((r.returncode, r.stdout), (1, "ABC-1 edit → HTTP 404 · labels now: ?\n"))

    def test_dry_run_prints_the_body_and_sends_nothing(self):
        root, env = self.project()
        r = run_script("jira-edit.sh", ["ABC-1", "--add-label", "x", "--dry-run", "--field", 'customfield_1={"value":"ก"}'],
                       root, env)
        self.assertEqual((r.returncode, r.stderr), (0, ""))
        self.assertEqual(r.stdout, '{"update": {"labels": [{"add": "x"}]}, "fields": {"customfield_1": {"value": "ก"}}}\n')
        self.assertEqual(calls(root), [])

    def test_exact_refusals(self):
        root, env = self.project()
        for args, message in (
            (["--set", "x"], "jira-edit.sh: unknown option --set\n"),
            (["--add-label"], "jira-edit.sh: --add-label needs a value\n"),
            (["--add-label", "ai do now"], "jira-edit.sh: label 'ai do now': Jira labels have no spaces\n"),
            (["--field", "customfield_1={oops"],
             "jira-edit.sh: --field customfield_1: value is not JSON (quote strings: customfield_1='\"text\"')\n"),
            (["--field", 'custom field="x"'],
             "jira-edit.sh: --field 'custom field=\"x\"': expected <field id>=<value>, field id like customfield_10100\n"),
            (["--field-md", "customfield_1=" + os.path.join(root, "missing.md")],
             "jira-edit.sh: --field-md customfield_1: [Errno 2] No such file or directory: '%s'\n"
             % os.path.join(root, "missing.md")),
            (["--add-label", "a", "--field", 'labels=["b"]'],
             "jira-edit.sh: labels: use --add-label / --remove-label or --field labels=[...], not both\n"),
        ):
            r = run_script("jira-edit.sh", ["ABC-1"] + args, root, env)
            self.assertEqual((r.returncode, r.stdout, r.stderr), (2, "", message), args)
        self.assertEqual(calls(root), [])

    def test_usage_needs_no_project(self):
        for args in ([], ["ABC-1"], ["ABC-1", "--dry-run"]):
            r = run(args, cwd=tempfile.mkdtemp())
            self.assertEqual((r.returncode, r.stdout, r.stderr), (2, "", self.USAGE), args)

    def test_keys_the_old_check_refused_stay_refused_before_any_request(self):
        root, env = self.project()
        for bad in ("-x", "ABC/1", "../ABC-1"):
            r = run_script("jira-edit.sh", [bad, "--add-label", "x"], root, env)
            self.assertEqual((r.returncode, r.stdout), (2, ""), bad)
        self.assertEqual(calls(root), [])


if __name__ == "__main__":
    unittest.main()
