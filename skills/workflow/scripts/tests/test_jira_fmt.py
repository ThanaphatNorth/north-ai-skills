"""Tests for jira_fmt: the pure functions that turn Jira's JSON into the text the jira-*.sh scripts print.

  python3 -m unittest discover -s skills/workflow/scripts/tests -p 'test_*.py'
"""
import contextlib
import io
import json
import os
import subprocess
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import jira_fmt as fmt  # noqa: E402
import jira_read  # noqa: E402
import jira_write  # noqa: E402

FMT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "jira_fmt.py")
JIRA_ERROR = '{"errorMessages":["Issue does not exist"],"errors":{}}'
ERROR_LINE = 'ERROR {"errorMessages": ["Issue does not exist"], "errors": {}}'
NOT_JSON = "<html>\n<h1>502 Bad\tGateway</h1></html>"

ISSUE = {
    "key": "ABC-7", "id": "10077",
    "names": {"customfield_10050": "Severity", "customfield_10060": "Expected result"},
    "fields": {
        "summary": "Total is wrong", "issuetype": {"name": "Bug"}, "status": {"name": "To Do", "id": "10001"},
        "priority": {"name": "Medium"}, "labels": ["ai-queue", "billing"],
        "created": "2026-11-10T09:00:00.000+0700", "updated": "2026-11-12T15:30:00.000+0700",
        "reporter": {"displayName": "Ann QA"},
        "parent": {"key": "ABC-1", "fields": {"summary": "Billing epic"}},
        "issuelinks": [{"type": {"outward": "blocks", "inward": "is blocked by"},
                        "inwardIssue": {"key": "ABC-3", "fields": {"summary": "Spec", "status": {"name": "Done"}}}}],
        "comment": {"comments": [{"id": "61260", "author": {"displayName": "Bob Dev"},
                                  "created": "2026-11-11T10:00:00.000+0700"}]},
        "attachment": [{"id": "501", "filename": "before.mp4", "size": 1234, "mimeType": "video/mp4"}],
        "customfield_10050": {"value": "Level 4", "child": {"value": "Minor"}},
        "customfield_10060": {"type": "doc"},
    },
    "renderedFields": {
        "description": "<p>Shows <b>100.00</b></p><ul><li>for 2 &amp; 3   items</li></ul>",
        "comment": {"comments": [{"body": "<p>Looking<br/>into it</p>"}]},
        "customfield_10060": "<h2>Expected</h2><p>Shows 100.00</p><p>for <b>2</b> items</p>",
    },
}


def without(*names):
    issue = json.loads(json.dumps(ISSUE))
    for name in names:
        issue["fields"].pop(name, None)
    return issue


class ErrorBodies(unittest.TestCase):
    """Every formatter answers Jira's error object, and a body that is not JSON, with one ERROR line."""

    READERS = (
        ("issue_text", lambda b: fmt.issue_text(b)), ("card_text", lambda b: fmt.card_text(b, "")),
        ("search_page", lambda b: fmt.search_page(b)), ("transitions_text", lambda b: fmt.transitions_text(b)),
        ("status_text", lambda b: fmt.status_text(b)), ("labels_text", lambda b: fmt.labels_text(b)),
        ("object_id", lambda b: fmt.object_id(b)), ("comment_check", lambda b: fmt.comment_check(b, "", False)),
        ("attachment_rows", lambda b: fmt.attachment_rows(b)), ("download_rows", lambda b: fmt.download_rows(b)),
        ("display_name", lambda b: fmt.display_name(b)),
    )

    def test_a_jira_error_object(self):
        for name, read in self.READERS:
            with self.assertRaises(fmt.BodyError, msg=name) as caught:
                read(JIRA_ERROR)
            self.assertEqual(caught.exception.line, ERROR_LINE, name)

    def test_only_get_and_card_print_the_error_line_on_stdout(self):
        for name, read in self.READERS:
            with self.assertRaises(fmt.BodyError) as caught:
                read(JIRA_ERROR)
            self.assertEqual(caught.exception.stdout, name in ("issue_text", "card_text"), name)

    def test_a_body_that_is_not_json_is_one_line(self):
        for name, read in self.READERS + (("comment_body", lambda b: fmt.comment_body(b)),):
            for body, line in ((NOT_JSON, "ERROR expected JSON, got: <html> <h1>502 Bad Gateway</h1></html>"),
                               ("", "ERROR expected JSON, got: (nothing)")):
                with self.assertRaises(fmt.BodyError, msg=name) as caught:
                    read(body)
                self.assertEqual((caught.exception.line, caught.exception.stdout), (line, False), name)

    def test_a_long_body_is_cut(self):
        with self.assertRaises(fmt.BodyError) as caught:
            fmt.issue_text("x" * 5000)
        self.assertEqual(len(caught.exception.line), len("ERROR expected JSON, got: ") + 120)
        with self.assertRaises(fmt.BodyError) as caught:
            fmt.issue_text(json.dumps({"errorMessages": ["y" * 5000]}))
        self.assertEqual(len(caught.exception.line), len("ERROR ") + 300)

    def test_json_of_the_wrong_kind(self):
        for body in ("[]", '"fields"', "5", "null", "true"):
            for name, read in self.READERS:
                if name == "attachment_rows" and body == "[]":
                    continue  # an empty list is a valid attachment answer
                with self.assertRaises(fmt.BodyError, msg=(name, body)) as caught:
                    read(body)
                self.assertEqual(caught.exception.line, "ERROR " + body, (name, body))


class IssueText(unittest.TestCase):
    def test_the_whole_issue(self):
        self.assertEqual(fmt.issue_text(json.dumps(ISSUE)), "\n".join([
            "ABC-7  [Bug / To Do (10001)]  id=10077",
            "created 2026-11-10T09:00 · updated 2026-11-12T15:30 · reporter Ann QA",
            "SUMMARY: Total is wrong",
            "DESCRIPTION:",
            "Shows 100.00",
            "for 2 & 3 items",
            "--- comment 61260 by Bob Dev at 2026-11-11T10:00",
            "Looking",
            "into it",
            "ATTACHMENT 501  before.mp4  1234 bytes  video/mp4",
        ]) + "\n")

    def test_optional_parts_may_be_missing_or_empty(self):
        tail = "SUMMARY: Total is wrong\nDESCRIPTION:\n\n"
        for issue in (without("reporter", "comment", "attachment"),
                      dict(without(), fields=dict(ISSUE["fields"], reporter=None, comment=None, attachment=None)),
                      dict(without(), fields=dict(ISSUE["fields"], comment={"comments": []}, attachment=[]))):
            issue["renderedFields"] = None
            text = fmt.issue_text(json.dumps(issue))
            self.assertTrue(text.endswith(tail), text)
            self.assertNotIn("--- comment", text)
            self.assertNotIn("ATTACHMENT", text)
        self.assertIn("reporter ?\n", fmt.issue_text(json.dumps(without("reporter"))))

    def test_rendered_comments_without_their_raw_twin_are_not_printed(self):
        text = fmt.issue_text(json.dumps(without("comment")))
        self.assertNotIn("--- comment", text)
        self.assertIn("ATTACHMENT 501", text)


class CardText(unittest.TestCase):
    def test_the_whole_card(self):
        self.assertEqual(fmt.card_text(json.dumps(ISSUE), "customfield_10050,,customfield_10060,customfield_1"), "\n".join([
            "ABC-7  [Bug / To Do (10001)]  id=10077  priority Medium",
            "LABELS: ai-queue, billing",
            "PARENT: ABC-1 Billing epic",
            "LINK: is blocked by ABC-3 [Done] Spec",
            "FIELD customfield_10050 (Severity): Level 4 / Minor",
            "FIELD customfield_10060 (Expected result): Expected | Shows 100.00 | for 2 items",
            "FIELD customfield_1 (customfield_1): (empty)",
        ]) + "\n")

    def test_optional_parts_may_be_missing_or_empty(self):
        for issue in (without("priority", "labels", "parent", "issuelinks"),
                      dict(without(), fields=dict(ISSUE["fields"], priority=None, labels=None, parent=None, issuelinks=None)),
                      dict(without(), fields=dict(ISSUE["fields"], priority={}, labels=[], parent=None, issuelinks=[]))):
            issue.pop("names")
            issue.pop("renderedFields")
            self.assertEqual(fmt.card_text(json.dumps(issue), ""),
                             "ABC-7  [Bug / To Do (10001)]  id=10077\nLABELS: (none)\n")

    def test_a_link_without_its_issue_fields(self):
        issue = without()
        issue["fields"]["parent"] = {"key": "ABC-1"}
        issue["fields"]["issuelinks"] = [{"type": {"outward": "blocks"}, "outwardIssue": {"key": "ABC-9"}}]
        text = fmt.card_text(json.dumps(issue), "")
        self.assertIn("PARENT: ABC-1 \n", text)
        self.assertIn("LINK: blocks ABC-9 [?] \n", text)

    def test_field_values_of_every_kind(self):
        def shown(value, rendered=None):
            issue = {"key": "K-1", "id": "1", "fields": {"issuetype": {"name": "T"}, "status": {"name": "S", "id": "2"},
                                                        "f": value}, "renderedFields": {"f": rendered}}
            return fmt.card_text(json.dumps(issue), "f").splitlines()[-1][len("FIELD f (f): "):]

        self.assertEqual(shown(None), "(empty)")
        self.assertEqual(shown([]), "(empty)")
        self.assertEqual(shown(""), "(empty)")
        self.assertEqual(shown(0), "0")
        self.assertEqual(shown(3.5), "3.5")
        self.assertEqual(shown("plain"), "plain")
        self.assertEqual(shown([{"value": "QA"}, {"name": "Dev"}, "x", None]), "QA, Dev, x, (empty)")
        self.assertEqual(shown({"displayName": "Ann"}), "Ann")
        self.assertEqual(shown({"key": "ABC-2"}), "ABC-2")
        self.assertEqual(shown({"value": "A", "child": {"value": "B", "child": {"value": "C"}}}), "A / B / C")
        self.assertEqual(shown({"type": "doc", "text": "ก"}), '{"type": "doc", "text": "ก"}')
        self.assertEqual(len(shown({"type": "x" * 500})), 200)
        self.assertEqual(shown({"type": "doc"}, rendered="<p>one</p><p> </p><p>two&nbsp;&lt;3</p>"), "one | two\xa0<3")
        self.assertEqual(shown("raw", rendered="   "), "raw")
        self.assertEqual(shown(None, rendered="<p></p>"), "(empty)")


class SearchPage(unittest.TestCase):
    def issue(self, key, **fields):
        base = {"issuetype": {"name": "Bug"}, "status": {"name": "To Do", "id": "1"}, "summary": "S"}
        return {"key": key, "fields": dict(base, **fields)}

    def test_rows_then_the_next_page_token(self):
        page = {"isLast": False, "nextPageToken": "tok2", "issues": [
            self.issue("A-1", updated="2026-11-12T15:30:00.000+0700", summary="x" * 95,
                       customfield_10020=[{"name": "Sprint 4", "state": "active"}, {"id": 3}]),
            self.issue("A-2", customfield_10020=None)]}
        self.assertEqual(fmt.search_page(json.dumps(page)),
                         "A-1 | Bug | To Do (1) | Sprint 4(active),() | 2026-11-12T15:30 | " + "x" * 90 + "\n"
                         "A-2 | Bug | To Do (1) | BACKLOG |  | S\n"
                         "__NEXT__ tok2\n")

    def test_the_last_page_and_an_empty_page_have_no_token(self):
        self.assertEqual(fmt.search_page('{"issues":[],"isLast":true,"nextPageToken":"ignored"}'), "__NEXT__ \n")
        self.assertEqual(fmt.search_page('{"issues":[]}'), "__NEXT__ \n")
        self.assertEqual(fmt.search_page('{"issues":[],"isLast":false}'), "__NEXT__ \n")


class Transitions(unittest.TestCase):
    def test_one_line_per_transition(self):
        body = {"transitions": [{"id": "6", "name": "Start", "to": {"id": "3", "statusCategory": {"key": "indeterminate"}}}]}
        self.assertEqual(fmt.transitions_text(json.dumps(body)), "6 → Start (status 3, indeterminate)\n")
        self.assertEqual(fmt.transitions_text('{"transitions":[]}'), "")

    def test_the_request_body(self):
        self.assertEqual(fmt.transition_body("6", ""), '{"transition": {"id": "6"}}\n')
        self.assertEqual(fmt.transition_body("9", '{"customfield_1":{"value":"ก"}}'),
                         '{"transition": {"id": "9"}, "fields": {"customfield_1": {"value": "\\u0e01"}}}\n')
        self.assertEqual(fmt.transition_body("9", "{}"), '{"transition": {"id": "9"}, "fields": {}}\n')

    def test_fields_that_are_not_a_json_object_are_refused(self):
        for bad in ("{oops", "[1]", '"text"', "5", "null"):
            with self.assertRaises(fmt.ArgError, msg=bad) as caught:
                fmt.transition_body("6", bad)
            self.assertEqual(str(caught.exception), "fields-json must be a JSON object, got '%s'" % bad)

    def test_status(self):
        self.assertEqual(fmt.status_text('{"fields":{"status":{"name":"In Progress","id":"3"}}}'), "In Progress (3)\n")


class Labels(unittest.TestCase):
    def test_comma_joined(self):
        self.assertEqual(fmt.labels_text('{"fields":{"labels":["a","b"]}}'), "a,b\n")

    def test_none_is_an_empty_line(self):
        for body in ('{"fields":{"labels":[]}}', '{"fields":{"labels":null}}', '{"fields":{}}'):
            self.assertEqual(fmt.labels_text(body), "\n")


class EditBody(unittest.TestCase):
    def body(self, *args, **kwargs):
        return json.loads(fmt.edit_body(list(args), kwargs.get("to_adf", lambda path: {"adf": path})))

    def refused(self, *args, **kwargs):
        with self.assertRaises(fmt.ArgError) as caught:
            self.body(*args, **kwargs)
        return str(caught.exception)

    def test_labels_fields_and_markdown_fields(self):
        self.assertEqual(self.body("--remove-label", "a", "--field", 'customfield_1={"value":"=x="}', "--add-label", "b",
                                   "--field-md", "customfield_2=notes/a=b.md"),
                         {"update": {"labels": [{"remove": "a"}, {"add": "b"}]},
                          "fields": {"customfield_1": {"value": "=x="}, "customfield_2": {"adf": "notes/a=b.md"}}})
        self.assertEqual(fmt.edit_body(["--field", 'summary="ก"'], lambda path: {}), '{"fields": {"summary": "ก"}}\n')
        self.assertEqual(fmt.edit_body([], lambda path: {}), "{}\n")

    def test_refusals(self):
        self.assertEqual(self.refused("--set", "x"), "unknown option --set")
        self.assertEqual(self.refused("--add-label"), "--add-label needs a value")
        self.assertEqual(self.refused("--add-label", "a b"), "label 'a b': Jira labels have no spaces")
        self.assertEqual(self.refused("--remove-label", ""), "label '': Jira labels have no spaces")
        self.assertEqual(self.refused("--field", "customfield_1={oops"),
                         "--field customfield_1: value is not JSON (quote strings: customfield_1='\"text\"')")
        self.assertEqual(self.refused("--field", "customfield_1"),
                         "--field 'customfield_1': expected <field id>=<value>, field id like customfield_10100")
        self.assertEqual(self.refused("--field-md", "1x=a.md"),
                         "--field-md '1x=a.md': expected <field id>=<value>, field id like customfield_10100")
        self.assertEqual(self.refused("--add-label", "a", "--field", 'labels=["b"]'),
                         "labels: use --add-label / --remove-label or --field labels=[...], not both")

    def test_a_markdown_file_that_cannot_be_read(self):
        def missing(path):
            raise FileNotFoundError(2, "No such file or directory", path)

        self.assertEqual(self.refused("--field-md", "customfield_2=nope.md", to_adf=missing),
                         "--field-md customfield_2: [Errno 2] No such file or directory: 'nope.md'")


class Comments(unittest.TestCase):
    MD = "**Fixed** in `web/src/a.ts:12` and `plain`\n::video 0a1b2c3d-1111-2222-3333-444455556666\n::video x\n"

    def test_the_id_of_an_object(self):
        self.assertEqual(fmt.object_id('{"id":"10077","self":"x"}'), "10077\n")
        self.assertEqual(fmt.object_id('{"id":61300}'), "61300\n")

    def test_the_adf_is_wrapped_as_the_comment_body(self):
        self.assertEqual(fmt.comment_body('{"type":"doc","content":[{"text":"ก"}]}'),
                         '{"body": {"type": "doc", "content": [{"text": "ก"}]}}\n')

    def test_the_read_back_counts_players_and_attachment_ids(self):
        rendered = ('<code>web/src/a.ts:12</code><source type="video/mp4" src="/attachment/content/502"/>'
                    '<source type="video/mp4" src="/attachment/content/501"/><a href="/attachment/content/501">')
        body = json.dumps({"id": "61300", "renderedBody": rendered})
        self.assertEqual(fmt.comment_check(body, self.MD, False),
                         ("comment 61300 created · videos in md 2 · players rendered 2 · attachment ids ['501', '502']\n", []))
        self.assertEqual(fmt.comment_check(body, self.MD, True)[0][:22], "comment 61300 updated ")

    def test_it_warns_about_a_missing_player_and_missing_code_spans(self):
        for body in ('{"id":"61300","renderedBody":"<p>Fixed</p>"}', '{"id":"61300","renderedBody":null}', '{"id":"61300"}'):
            line, warnings = fmt.comment_check(body, self.MD, False)
            self.assertEqual(line, "comment 61300 created · videos in md 2 · players rendered 0 · attachment ids []\n")
            self.assertEqual(warnings, [
                "WARNING: no inline player rendered — check the media uuids",
                "WARNING: these `code` spans are missing from the rendered comment (unquoted heredoc?): "
                "['web/src/a.ts:12']"])

    def test_a_comment_with_no_video_and_no_path_has_no_warning(self):
        self.assertEqual(fmt.comment_check('{"id":"1","renderedBody":""}', "just `words`\n", False),
                         ("comment 1 created · videos in md 0 · players rendered 0 · attachment ids []\n", []))


class Attachments(unittest.TestCase):
    def test_rows_for_attach(self):
        self.assertEqual(fmt.attachment_rows('[{"id":"501","filename":"a b.mp4","size":6},{"id":"502","filename":"c","size":0}]'),
                         "501|6|a b.mp4\n502|0|c\n")
        self.assertEqual(fmt.attachment_rows("[]"), "")

    def test_a_file_name_cannot_start_a_new_row_or_shift_the_columns(self):
        self.assertEqual(fmt.attachment_rows(json.dumps([{"id": "501", "filename": "a|b\n999|1|x.mp4", "size": 6}])),
                         "501|6|a|b_999|1|x.mp4\n")
        body = json.dumps({"fields": {"attachment": [{"id": "501", "filename": "a\n999\tb\r.mp4"}]}})
        self.assertEqual(fmt.download_rows(body), "501\ta_999_b_.mp4\n")

    def test_rows_for_download_never_hold_a_slash(self):
        body = '{"fields":{"attachment":[{"id":"501","filename":"a.mp4"},{"id":"502","filename":"../logs/app.log"}]}}'
        self.assertEqual(fmt.download_rows(body), "501\ta.mp4\n502\t.._logs_app.log\n")

    def test_no_attachment(self):
        for body in ('{"fields":{"attachment":[]}}', '{"fields":{"attachment":null}}', '{"fields":{}}'):
            self.assertEqual(fmt.download_rows(body), "")


class Myself(unittest.TestCase):
    def test_display_name(self):
        self.assertEqual(fmt.display_name('{"accountId":"1","displayName":"Bot ก"}'), "Bot ก\n")


class Main(unittest.TestCase):
    def run_main(self, args, stdin=""):
        out, err = io.StringIO(), io.StringIO()
        old = sys.stdin
        sys.stdin = io.TextIOWrapper(io.BytesIO(stdin.encode("utf-8")), encoding="utf-8")
        try:
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = fmt.main(["jira_fmt.py"] + args)
        finally:
            sys.stdin = old
        return code, out.getvalue(), err.getvalue()

    def test_a_command_prints_its_text(self):
        self.assertEqual(self.run_main(["labels"], '{"fields":{"labels":["ก","b"]}}'), (0, "ก,b\n", ""))
        self.assertEqual(self.run_main(["transition-body", "6", ""]), (0, '{"transition": {"id": "6"}}\n', ""))

    def test_get_and_card_keep_their_error_line_on_stdout(self):
        self.assertEqual(self.run_main(["issue"], JIRA_ERROR), (1, ERROR_LINE + "\n", ""))
        self.assertEqual(self.run_main(["card", ""], JIRA_ERROR), (1, ERROR_LINE + "\n", ""))
        self.assertEqual(self.run_main(["search-page"], JIRA_ERROR), (1, "", ERROR_LINE + "\n"))

    def test_not_json_is_one_line_on_stderr_and_exit_1(self):
        for command in (["issue"], ["card", ""], ["search-page"], ["transitions"], ["status"], ["labels"], ["downloads"],
                        ["comment-body"], ["display-name"]):
            self.assertEqual(self.run_main(command, NOT_JSON),
                             (1, "", "ERROR expected JSON, got: <html> <h1>502 Bad Gateway</h1></html>\n"), command)

    def test_an_object_missing_a_needed_part_is_one_line_too(self):
        code, out, err = self.run_main(["issue"], '{"key":"A-1","id":"1","fields":{"summary":"x"}}')
        self.assertEqual((code, out), (1, ""))
        self.assertEqual(err, "ERROR unexpected response shape: KeyError('issuetype')\n")
        code, out, err = self.run_main(["transitions"], '{"transitions":[{"id":"6","name":"x","to":null}]}')
        self.assertEqual((code, out, err.count("\n")), (1, "", 1))

    def test_a_refused_argument_names_its_script_and_exits_2(self):
        self.assertEqual(self.run_main(["edit-body", "--set", "x"]), (2, "", "jira-edit.sh: unknown option --set\n"))
        self.assertEqual(self.run_main(["transition-body", "6", "[1]"]),
                         (2, "", "jira-transition.sh: fields-json must be a JSON object, got '[1]'\n"))

    def test_an_unknown_command_or_a_missing_argument_is_usage(self):
        for args in ([], ["nope"], ["card"], ["transition-body", "6"], ["comment-check", "a.md"]):
            code, out, err = self.run_main(args)
            self.assertEqual((code, out), (2, ""), args)
            self.assertTrue(err.startswith("usage: jira_fmt.py "), err)

    def test_it_runs_isolated_the_way_the_scripts_call_it(self):
        r = subprocess.run([sys.executable, "-I", FMT, "status"], input='{"fields":{"status":{"name":"ทำอยู่","id":"3"}}}',
                           capture_output=True, text=True, encoding="utf-8", env={"LC_ALL": "C"})
        self.assertEqual((r.returncode, r.stdout, r.stderr), (0, "ทำอยู่ (3)\n", ""))
        r = subprocess.run([sys.executable, "-I", FMT, "status"], input=NOT_JSON, capture_output=True, text=True)
        self.assertEqual((r.returncode, r.stdout, "Traceback" in r.stderr, r.stderr.count("\n")), (1, "", False, 1))


class Docstrings(unittest.TestCase):
    def test_every_public_function_says_what_it_returns(self):
        public = [f for module in (fmt, jira_read, jira_write) for n, f in vars(module).items()
                  if callable(f) and not n.startswith("_") and not isinstance(f, type)
                  and getattr(f, "__module__", "") == module.__name__]
        self.assertGreaterEqual(len(public), 16)
        self.assertEqual([f.__name__ for f in public if not (f.__doc__ or "").strip()], [])


if __name__ == "__main__":
    unittest.main()
