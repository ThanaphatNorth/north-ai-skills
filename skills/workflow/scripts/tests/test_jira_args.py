"""Every argument of a jira-*.sh script that reaches a URL has one rule (_env.sh: need_key, need_id, …).

A value that breaks its rule ends the script with exit 2 and a message naming the argument, before any HTTP
request; free text (the JQL) is URL-encoded by curl, and ids that come back from Jira are checked before they
are put into the next URL.

  python3 -m unittest discover -s skills/workflow/scripts/tests -p 'test_*.py'
"""
import json
import os
import subprocess
import sys
import unittest

from fakejira import SCRIPTS, SITE, calls, fake_project, real_curl, requests, run_script

sys.path.insert(0, SCRIPTS)
import jira_fmt  # noqa: E402

API = SITE + "/rest/api/3"
BAD_KEYS = ("", "ABC", "12", "ABC-", "-7", "-x", "ABC-7/..", "../ABC-7", "ABC/7", "ABC-7?expand=changelog", "ABC-7#f",
            "ABC 7", "ABC-7 ", " ABC-7", "ABC-7\n", "ABC-7%2F..", "A-B-7", "ÀBC-7", "ABC-７", "ABC-7;id", "$(id)-7")
# script → the arguments that follow a key and are valid themselves
AFTER_KEY = {
    "jira-get.sh": [],
    "jira-card.sh": ["customfield_10050"],
    "jira-edit.sh": ["--add-label", "x"],
    "jira-transition.sh": ["6"],
    "jira-comment.sh": ["comment.md"],
    "jira-attach.sh": ["before.mp4"],
    "jira-download.sh": ["out"],
}
ANY = """
    *" -X PUT "*|*" POST "*) reply 204 ;;
    *) reply 200 '{}' ;;
"""


def project(arms=ANY, **kwargs):
    root, env, _ = fake_project(arms, **kwargs)
    for name in ("comment.md", "before.mp4"):
        with open(os.path.join(root, name), "w") as fh:
            fh.write("text\n")
    return root, env


class Keys(unittest.TestCase):
    def test_a_key_that_is_not_an_issue_key_is_refused_by_every_script(self):
        root, env = project()
        for script, rest in sorted(AFTER_KEY.items()):
            # the rule is one function: every bad shape against one script, a few against each of the others
            for bad in BAD_KEYS if script == "jira-get.sh" else BAD_KEYS[:1] + BAD_KEYS[6:10]:
                r = run_script(script, [bad] + rest, root, env)
                self.assertEqual((r.returncode, r.stdout), (2, ""), (script, bad))
                self.assertEqual(r.stderr, "%s: KEY must be an issue key like ABC-12, got '%s'\n" % (script, bad))
        self.assertEqual(calls(root), [], "a refused key must not reach Jira")
        self.assertFalse(os.path.exists(os.path.join(root, "out")), "nothing is created for a refused key")

    def test_the_dry_run_of_edit_checks_the_key_too(self):
        root, env = project()
        r = run_script("jira-edit.sh", ["ABC-1?x=1", "--dry-run", "--add-label", "x"], root, env)
        self.assertEqual((r.returncode, r.stdout), (2, ""))
        self.assertIn("KEY", r.stderr)

    def test_keys_of_the_shape_the_local_board_accepts_go_through(self):
        root, env = project()
        for key in ("ABC-7", "abc-7", "A1_b-120"):
            r = run_script("jira-transition.sh", [key, "6"], root, env)
            self.assertNotEqual(r.returncode, 2, r.stderr)
        self.assertEqual(requests(root)[0::2], ["POST %s/issue/%s/transitions" % (API, k)
                                                for k in ("ABC-7", "abc-7", "A1_b-120")])


class Ids(unittest.TestCase):
    BAD_IDS = ("61260/../../../2/issue/ABC-1", "61260?expand=x", "c12", "12 13", "-1", "1.5", "١٢", "12\n")

    def refused(self, script, args, bad, name):
        root, env = project()
        r = run_script(script, args, root, env)
        self.assertEqual((r.returncode, r.stdout), (2, ""), (script, bad))
        self.assertEqual(r.stderr, "%s: %s must be digits only, got '%s'\n" % (script, name, bad))
        self.assertEqual(calls(root), [], (script, bad))

    def test_comment_id(self):
        for bad in self.BAD_IDS:
            self.refused("jira-comment.sh", ["ABC-7", "comment.md", bad], bad, "comment id")

    def test_transition_id(self):
        for bad in self.BAD_IDS + ("Done", "--List"):
            self.refused("jira-transition.sh", ["ABC-7", bad], bad, "transition id")

    def test_attachment_ids_of_download(self):
        for bad in self.BAD_IDS:
            self.refused("jira-download.sh", ["ABC-7", "out", "501", bad], bad, "attachment id")

    def test_an_empty_comment_id_still_means_a_new_comment(self):
        root, env, _ = fake_project("""
            *"?fields=summary "*) reply 200 '{"id":"10077"}' ;;
            *" POST "*) reply 201 '{"id":"61300"}' ;;
            *) reply 200 '{"id":"61300","renderedBody":""}' ;;
        """)
        with open(os.path.join(root, "comment.md"), "w") as fh:
            fh.write("text\n")
        r = run_script("jira-comment.sh", ["ABC-7", "comment.md", ""], root, env)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(requests(root)[1], "POST " + API + "/issue/ABC-7/comment")


class FieldIds(unittest.TestCase):
    BAD = ("customfield_1;rm", "a b", "summary,", ",summary", "summary,,labels", "*all", "-comment", "summary&expand=x",
           "10050", "_x", "summary\n")

    def test_the_field_list_of_card_and_search(self):
        for script, first in (("jira-card.sh", "ABC-7"), ("jira-search.sh", "project = ABC")):
            for bad in self.BAD:
                root, env = project()
                r = run_script(script, [first, bad], root, env)
                self.assertEqual((r.returncode, r.stdout), (2, ""), (script, bad))
                self.assertEqual(r.stderr, "%s: field ids are comma-separated ids like customfield_10050, got '%s'\n"
                                 % (script, bad))
                self.assertEqual(calls(root), [], (script, bad))

    def test_bash_and_the_edit_body_agree_on_what_a_field_id_is(self):
        # one rule, written once in bash (the URL) and once in jira_fmt (the request body): keep them the same
        root, env = project()
        for fid in ("summary", "customfield_10050", "Labels", "a1_", "10050", "_x", "a-b", "a b", "a.b", ""):
            bash = run_script("jira-card.sh", ["ABC-7", fid], root, env).returncode != 2 if fid else False
            try:
                jira_fmt.edit_body(["--field", fid + "=1"], lambda path: {})
                python = True
            except jira_fmt.ArgError:
                python = False
            self.assertEqual(bash, python, fid)


class FreeText(unittest.TestCase):
    def test_an_empty_jql_is_refused(self):
        for bad in ("", "   ", "\n"):
            root, env = project()
            r = run_script("jira-search.sh", [bad], root, env)
            self.assertEqual((r.returncode, r.stdout, r.stderr), (2, "", "jira-search.sh: JQL must not be empty\n"))
            self.assertEqual(calls(root), [])

    def test_the_jql_is_handed_to_curl_to_encode_never_put_in_the_url(self):
        jql = 'summary ~ "a&b=c" AND text ~ "x#y?z" OR key = ABC-1 &maxResults=0 OR summary ~ "ทดสอบ"'
        root, env, _ = fake_project("""*) reply 200 '{"issues":[],"isLast":true}' ;;""")
        r = run_script("jira-search.sh", [jql], root, env)
        self.assertEqual(r.returncode, 0, r.stderr)
        call = calls(root)[0]
        self.assertEqual(call["url"], API + "/search/jql")
        self.assertEqual(call["query"][0], "jql=" + jql)
        self.assertEqual([a for a in call["argv"] if "maxResults=0" in a], ["jql=" + jql])

    def test_the_fields_of_a_transition_must_be_a_json_object(self):
        for bad in ("{oops", "[1]", '"text"', "5", "null"):
            root, env = project()
            r = run_script("jira-transition.sh", ["ABC-7", "6", bad], root, env)
            self.assertEqual((r.returncode, r.stdout), (2, ""), bad)
            self.assertEqual(r.stderr, "jira-transition.sh: fields-json must be a JSON object, got '%s'\n" % bad)
            self.assertEqual(calls(root), [], bad)

    def test_a_comment_file_that_does_not_exist_is_refused_before_any_request(self):
        root, env = project()
        r = run_script("jira-comment.sh", ["ABC-7", "nope.md"], root, env)
        self.assertEqual((r.returncode, r.stdout), (2, ""))
        self.assertEqual(r.stderr, "jira-comment.sh: comment.md must be an existing file, got 'nope.md'\n")
        self.assertEqual(calls(root), [])


class IdsFromJira(unittest.TestCase):
    """An id read from a response is checked before it is put into the next URL."""

    def test_attach_does_not_follow_an_attachment_id_that_is_not_a_number(self):
        root, env = project("""
            *"file=@"*) reply 200 '[{"id":"501/../../../2/issue/ABC-1","filename":"before.mp4","size":5}]' ;;
            *) reply 303 '' 'https://api.media.example.test/file/0a1b2c3d-1111-2222-3333-444455556666/binary' ;;
        """)
        r = run_script("jira-attach.sh", ["ABC-7", "before.mp4"], root, env)
        self.assertEqual(requests(root), ["POST " + API + "/issue/ABC-7/attachments"])
        self.assertEqual(r.stdout, "attached before.mp4 id 501/../../../2/issue/ABC-1 5 bytes media UNKNOWN\n")

    def test_download_skips_an_attachment_id_that_is_not_a_number(self):
        root, env = project("""
            *"?fields=attachment "*) reply 200 '{"fields":{"attachment":[{"id":"9?x=1","filename":"a"},{"id":"502","filename":"b"}]}}' ;;
            *) reply 200 'data' ;;
        """)
        r = run_script("jira-download.sh", ["ABC-7", "out"], root, env)
        self.assertEqual(requests(root), ["GET " + API + "/issue/ABC-7?fields=attachment",
                                          "GET " + API + "/attachment/content/502"])
        self.assertEqual((r.returncode, r.stdout), (0, "downloaded 502 b 4 bytes\n"))
        self.assertEqual(r.stderr, "skip (attachment id is not a number): 9?x=1\n")

    def test_comment_does_not_read_back_a_comment_id_that_is_not_a_number(self):
        root, env = project("""
            *"?fields=summary "*) reply 200 '{"id":"10077"}' ;;
            *" POST "*) reply 201 '{"id":"1/../../x"}' ;;
            *) reply 200 '{"id":"61300","renderedBody":""}' ;;
        """)
        r = run_script("jira-comment.sh", ["ABC-7", "comment.md"], root, env)
        self.assertEqual(len(calls(root)), 2)
        self.assertEqual((r.returncode, r.stdout), (1, ""))
        self.assertEqual(r.stderr, "FAILED ABC-7 comment: Jira answered with comment id '1/../../x', not a number\n")


class AttachedFileNames(unittest.TestCase):
    NAMES = ("a;type=text.mp4", "one,two.mp4", 'we"ird.mp4', "back\\slash.mp4", "plain name.mp4")

    def test_a_file_name_cannot_change_the_upload_form(self):
        root, env = project("""*) reply 200 '[]' ;;""")
        for name in self.NAMES:
            with open(os.path.join(root, name), "w") as fh:
                fh.write("x")
            run_script("jira-attach.sh", ["ABC-7", name], root, env)
        forms = [c["argv"][c["argv"].index("-F") + 1] for c in calls(root)]
        self.assertEqual(forms, ['file=@"%s"' % n.replace("\\", "\\\\").replace('"', '\\"') for n in self.NAMES])

    def test_the_real_curl_opens_exactly_that_file(self):
        # file:// keeps the real curl off the network; --libcurl shows which file it would upload
        wrapper = ('#!/bin/bash\nROOT="$(cd "$(dirname "$0")/.." && pwd)"\nform=""\n'
                   'while [ $# -gt 0 ]; do [ "$1" = "-F" ] && form=$2; shift; done\n'
                   'exec "%s" -sS -K - -F "$form" --libcurl "$ROOT/libcurl.c" -o /dev/null "file:///dev/null"\n'
                   % real_curl(self))
        for name in self.NAMES:
            root, env, _ = fake_project("", curl=wrapper)
            with open(os.path.join(root, name), "w") as fh:
                fh.write("x")
            run_script("jira-attach.sh", ["ABC-7", name], root, env)
            with open(os.path.join(root, "libcurl.c")) as fh:
                source = fh.read()
            self.assertIn('curl_mime_filedata(part1, "%s");' % name.replace("\\", "\\\\").replace('"', '\\"'), source)
            self.assertNotIn("curl_mime_type", source, name)


class RuleFunctions(unittest.TestCase):
    """The rules themselves, sourced from _env.sh without loading any project."""

    def check(self, call):
        r = subprocess.run(["bash", "-c", '. "$1/_env.sh"; shift; "$@"', "rules", SCRIPTS] + call,
                           capture_output=True, text=True, env={"PATH": os.environ["PATH"], "LC_ALL": "en_US.UTF-8"})
        return r.returncode, r.stderr

    def test_need_key(self):
        self.assertEqual(self.check(["need_key", "ABC-12"]), (0, ""))
        self.assertEqual(self.check(["need_key", "ÀBC-12"])[0], 2)

    def test_need_id(self):
        self.assertEqual(self.check(["need_id", "0012", "comment id"]), (0, ""))
        self.assertEqual(self.check(["need_id", "", "comment id"]), (2, "rules: comment id must be digits only, got ''\n"))

    def test_is_id_answers_without_exiting(self):
        self.assertEqual(self.check(["is_id", "501"]), (0, ""))
        self.assertEqual(self.check(["is_id", "501x"]), (1, ""))

    def test_need_field_ids(self):
        self.assertEqual(self.check(["need_field_ids", "summary,customfield_10050"]), (0, ""))
        self.assertEqual(self.check(["need_field_ids", "summary,"])[0], 2)

    def test_sourcing_loads_no_project_and_no_credentials(self):
        r = subprocess.run(["bash", "-c", '. "$1/_env.sh"; echo "site=${JIRA_SITE:-} token=${JIRA_TOKEN:-}"', "x", SCRIPTS],
                           capture_output=True, text=True, cwd="/", env={"PATH": os.environ["PATH"]})
        self.assertEqual((r.returncode, r.stdout, r.stderr), (0, "site= token=\n", ""))


class EditBodyStillValidates(unittest.TestCase):
    def test_labels_and_field_ids_go_into_the_body_not_the_url(self):
        root, env = project()
        r = run_script("jira-edit.sh", ["ABC-7", "--add-label", "a/b?c=d", "--field", 'summary="x&y"'], root, env)
        self.assertEqual(r.returncode, 0, r.stderr)
        put = calls(root)[0]
        self.assertEqual(put["url"], API + "/issue/ABC-7")
        self.assertEqual(json.loads(put["data"][0]), {"update": {"labels": [{"add": "a/b?c=d"}]},
                                                      "fields": {"summary": "x&y"}})


if __name__ == "__main__":
    unittest.main()
