"""When Jira answers with something a script cannot format, the script says so in one line, never a traceback.

Covers a body that is not JSON, Jira's error object where another object was expected, and optional parts that
are missing — for every jira-*.sh, through jira_fmt.py.

  python3 -m unittest discover -s skills/workflow/scripts/tests -p 'test_*.py'
"""
import os
import unittest

from fakejira import calls, fake_project, run_script

HTML = "<html>Bad gateway</html>"
NOT_JSON_LINE = "ERROR expected JSON, got: <html>Bad gateway</html>\n"
JIRA_ERROR = '{"errorMessages":["Issue does not exist"],"errors":{}}'
JIRA_ERROR_LINE = 'ERROR {"errorMessages": ["Issue does not exist"], "errors": {}}\n'
ISSUE_ID = """*"?fields=summary "*) reply 200 '{"id":"10077"}' ;;"""


def project(arms):
    root, env, _ = fake_project(arms)
    for name in ("comment.md", "before.mp4"):
        with open(os.path.join(root, name), "w") as fh:
            fh.write("text\n")
    return root, env


class OneLine(unittest.TestCase):
    def failed(self, arms, script, args, stderr, stdout="", code=1):
        root, env = project(arms)
        r = run_script(script, args, root, env)
        self.assertNotIn("Traceback", r.stderr, (script, args))
        self.assertEqual((r.returncode, r.stdout, r.stderr), (code, stdout, stderr), (script, args))
        return root

    def both(self, arms, script, args, **kwargs):
        """The same call answered with HTML, then with Jira's error object (%s in arms is the body)."""
        self.failed(arms % HTML, script, args, NOT_JSON_LINE, **kwargs)
        self.failed(arms % JIRA_ERROR, script, args, JIRA_ERROR_LINE, **kwargs)

    def test_get_and_card(self):
        for script in ("jira-get.sh", "jira-card.sh"):
            self.failed("*) reply 502 '%s' ;;" % HTML, script, ["ABC-7"], NOT_JSON_LINE)

    def test_search(self):
        self.failed("*) reply 502 '%s' ;;" % HTML, "jira-search.sh", ["project = ABC"], NOT_JSON_LINE)

    def test_transition(self):
        self.both("*) reply 404 '%s' ;;", "jira-transition.sh", ["ABC-7", "--list"])
        self.both("""
            *" POST "*) reply 204 ;;
            *) reply 404 '%s' ;;
        """, "jira-transition.sh", ["ABC-7", "6"])

    def test_edit_still_prints_its_line_when_the_labels_cannot_be_read_back(self):
        self.both("""
            *" PUT "*) reply 204 ;;
            *) reply 500 '%s' ;;
        """, "jira-edit.sh", ["ABC-7", "--add-label", "x"], stdout="ABC-7 edit → HTTP 204 · labels now: ?\n", code=0)

    def test_comment(self):
        self.both("*) reply 200 '%s' ;;", "jira-comment.sh", ["ABC-7", "comment.md"])
        root = self.failed(ISSUE_ID + "\n*) reply 201 '%s' ;;" % HTML, "jira-comment.sh", ["ABC-7", "comment.md"], NOT_JSON_LINE)
        self.assertEqual(len(calls(root)), 2)
        self.both(ISSUE_ID + """
            *" POST "*) reply 201 '{"id":"61300"}' ;;
            *) reply 404 '%s' ;;
        """, "jira-comment.sh", ["ABC-7", "comment.md"])

    def test_attach(self):
        self.both("*) reply 200 '%s' ;;", "jira-attach.sh", ["ABC-7", "before.mp4"])

    def test_download(self):
        self.both("*) reply 404 '%s' ;;", "jira-download.sh", ["ABC-7", "out"])

    def test_an_object_without_a_needed_part(self):
        self.failed("""*) reply 200 '{"key":"ABC-7","id":"1","fields":{"summary":"x"}}' ;;""", "jira-get.sh", ["ABC-7"],
                    "ERROR unexpected response shape: KeyError('issuetype')\n")


class OptionalParts(unittest.TestCase):
    BARE = ('{"key":"ABC-7","id":"1","fields":{"summary":"x","issuetype":{"name":"Bug"},"status":{"name":"To Do","id":"2"},'
            '"created":"2026-11-10T09:00:00.000+0700","updated":"2026-11-10T09:00:00.000+0700"}}')

    def test_get_prints_an_issue_that_has_no_comment_part(self):
        root, env = project("*) reply 200 '%s' ;;" % self.BARE)
        r = run_script("jira-get.sh", ["ABC-7"], root, env)
        self.assertEqual((r.returncode, r.stderr), (0, ""))
        self.assertEqual(r.stdout, "ABC-7  [Bug / To Do (2)]  id=1\ncreated 2026-11-10T09:00 · updated 2026-11-10T09:00 · "
                                   "reporter ?\nSUMMARY: x\nDESCRIPTION:\n\n")

    def test_download_of_an_issue_that_has_no_attachment_part(self):
        root, env = project("""*) reply 200 '{"fields":{}}' ;;""")
        r = run_script("jira-download.sh", ["ABC-7", "out"], root, env)
        self.assertEqual((r.returncode, r.stdout, r.stderr), (0, "", ""))

    def test_attach_prints_a_file_name_that_holds_a_bar(self):
        root, env = project("""
            *"file=@"*) reply 200 '[{"id":"501","filename":"a|b.mp4","size":5}]' ;;
            *) reply 303 '' '' ;;
        """)
        with open(os.path.join(root, "a|b.mp4"), "w") as fh:
            fh.write("video")
        r = run_script("jira-attach.sh", ["ABC-7", "a|b.mp4"], root, env)
        self.assertEqual((r.returncode, r.stdout), (0, "attached a|b.mp4 id 501 5 bytes media UNKNOWN\n"))


if __name__ == "__main__":
    unittest.main()
