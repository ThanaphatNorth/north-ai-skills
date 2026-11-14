"""What jira-get, -search, -transition, -comment, -attach and -download print and return, against the fake Jira.

These pin stdout, stderr and the exit code of each script as they were before the scripts were hardened
(jira-card.sh and jira-edit.sh are pinned in their own test files).

  python3 -m unittest discover -s skills/workflow/scripts/tests -p 'test_*.py'
"""
import json
import os
import unittest

from fakejira import SCRIPTS, SITE, TOKEN, calls, fake_project, requests, run_script

API = SITE + "/rest/api/3"
NOT_FOUND = '{"errorMessages":["Issue does not exist or you do not have permission to see it."],"errors":{}}'
NOT_FOUND_LINE = ('ERROR {"errorMessages": ["Issue does not exist or you do not have permission to see it."], '
                  '"errors": {}}\n')
UUID = "0a1b2c3d-1111-2222-3333-444455556666"

ISSUE = {
    "key": "ABC-7", "id": "10077",
    "fields": {
        "summary": "Total is wrong", "issuetype": {"name": "Bug"}, "status": {"name": "To Do", "id": "10001"},
        "created": "2026-11-10T09:00:00.000+0700", "updated": "2026-11-12T15:30:00.000+0700",
        "reporter": {"displayName": "Ann QA"}, "description": {"type": "doc"},
        "comment": {"comments": [{"id": "61260", "author": {"displayName": "Bob Dev"},
                                  "created": "2026-11-11T10:00:00.000+0700"}]},
        "attachment": [{"id": "501", "filename": "before.mp4", "size": 1234, "mimeType": "video/mp4"}],
    },
    "renderedFields": {
        "description": "<p>Shows <b>100.00</b></p><p>for 2 &amp; 3   items</p>",
        "comment": {"comments": [{"body": "<p>Looking<br/>into it</p>"}]},
    },
}


def usage(script, rest):
    return "usage: %s %s\n" % (os.path.join(SCRIPTS, script), rest)


class Get(unittest.TestCase):
    def test_prints_the_issue_its_comments_and_attachments(self):
        root, env, _ = fake_project('*) reply 200 "$(cat "$B/issue.json")" ;;', bodies={"issue.json": ISSUE})
        r = run_script("jira-get.sh", ["ABC-7"], root, env)
        self.assertEqual((r.returncode, r.stderr), (0, ""))
        self.assertEqual(r.stdout, "\n".join([
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
        self.assertEqual(requests(root), [
            "GET " + API + "/issue/ABC-7?fields=summary,status,issuetype,description,comment,attachment,created,"
            "updated,reporter&expand=renderedFields"])

    def test_an_issue_with_no_description_comments_or_attachments(self):
        bare = {"key": "ABC-8", "id": "10078", "fields": {
            "summary": "Bare", "issuetype": {"name": "Task"}, "status": {"name": "Done", "id": "3"},
            "created": "2026-11-10T09:00:00.000+0700", "updated": "2026-11-10T09:00:00.000+0700",
            "reporter": None, "description": None, "comment": {"comments": []}, "attachment": []}}
        root, env, _ = fake_project('*) reply 200 "$(cat "$B/issue.json")" ;;', bodies={"issue.json": bare})
        r = run_script("jira-get.sh", ["ABC-8"], root, env)
        self.assertEqual((r.returncode, r.stderr), (0, ""))
        self.assertEqual(r.stdout, "ABC-8  [Task / Done (3)]  id=10078\n"
                                   "created 2026-11-10T09:00 · updated 2026-11-10T09:00 · reporter ?\n"
                                   "SUMMARY: Bare\nDESCRIPTION:\n\n")

    def test_jira_error_body_is_one_error_line_and_exit_1(self):
        root, env, _ = fake_project("*) reply 404 '%s' ;;" % NOT_FOUND)
        r = run_script("jira-get.sh", ["ABC-404"], root, env)
        self.assertEqual((r.returncode, r.stdout, r.stderr), (1, NOT_FOUND_LINE, ""))

    def test_a_body_that_is_not_json_exits_1_with_nothing_on_stdout(self):
        root, env, _ = fake_project("*) reply 502 '<html>Bad gateway</html>' ;;")
        r = run_script("jira-get.sh", ["ABC-7"], root, env)
        self.assertEqual((r.returncode, r.stdout), (1, ""))

    def test_usage(self):
        root, env, _ = fake_project("*) reply 200 '{}' ;;")
        for args in ([], ["ABC-7", "extra"]):
            r = run_script("jira-get.sh", args, root, env)
            self.assertEqual((r.returncode, r.stdout, r.stderr), (2, "", usage("jira-get.sh", "<KEY>")))
        self.assertEqual(calls(root), [])


def found(key, summary, sprints=None, updated="2026-11-12T15:30:00.000+0700"):
    return {"key": key, "fields": {"issuetype": {"name": "Bug"}, "status": {"name": "To Do", "id": "10001"},
                                   "summary": summary, "updated": updated, "customfield_10020": sprints}}


class Search(unittest.TestCase):
    PAGES = {
        "page1.json": {"isLast": False, "nextPageToken": "tok2", "issues": [
            found("ABC-1", "First", [{"name": "Sprint 4", "state": "active"}, {"name": "Sprint 3", "state": "closed"}]),
            found("ABC-2", "S" * 100)]},
        "page2.json": {"isLast": True, "issues": [found("ABC-3", "Third")]},
    }
    ARMS = """
        *"nextPageToken=tok2"*) reply 200 "$(cat "$B/page2.json")" ;;
        *) reply 200 "$(cat "$B/page1.json")" ;;
    """

    def test_lists_every_page_and_counts_on_stderr(self):
        root, env, _ = fake_project(self.ARMS, bodies=self.PAGES)
        r = run_script("jira-search.sh", ["project = ABC AND labels = \"ai queue\" ORDER BY key"], root, env)
        self.assertEqual((r.returncode, r.stderr), (0, "# 3 issue(s)\n"))
        self.assertEqual(r.stdout, "\n".join([
            "ABC-1 | Bug | To Do (10001) | Sprint 4(active),Sprint 3(closed) | 2026-11-12T15:30 | First",
            "ABC-2 | Bug | To Do (10001) | BACKLOG | 2026-11-12T15:30 | " + "S" * 90,
            "ABC-3 | Bug | To Do (10001) | BACKLOG | 2026-11-12T15:30 | Third",
        ]) + "\n")
        first, second = calls(root)
        self.assertEqual((first["method"], first["url"]), ("GET", API + "/search/jql"))
        self.assertIn("-G", first["argv"])
        self.assertEqual(first["query"], ['jql=project = ABC AND labels = "ai queue" ORDER BY key',
                                          "fields=status,issuetype,summary,updated,customfield_10020",
                                          "maxResults=100"])
        self.assertEqual(second["query"][-1], "nextPageToken=tok2")

    def test_no_issue_found_is_a_zero_count_not_a_failure(self):
        root, env, _ = fake_project("""*) reply 200 '{"issues":[],"isLast":true}' ;;""")
        r = run_script("jira-search.sh", ["project = ABC AND labels = ai-queue"], root, env)
        self.assertEqual((r.returncode, r.stdout, r.stderr), (0, "", "# 0 issue(s)\n"))

    def test_extra_fields_are_added_to_the_field_list(self):
        root, env, _ = fake_project(self.ARMS, bodies=self.PAGES)
        r = run_script("jira-search.sh", ["project = ABC", "labels,customfield_10050"], root, env)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(calls(root)[0]["query"][1],
                         "fields=status,issuetype,summary,updated,customfield_10020,labels,customfield_10050")

    def test_jira_error_body_goes_to_stderr_and_exit_1(self):
        root, env, _ = fake_project("""*) reply 400 '{"errorMessages":["Error in the JQL Query"]}' ;;""")
        r = run_script("jira-search.sh", ["project ="], root, env)
        self.assertEqual((r.returncode, r.stdout, r.stderr),
                         (1, "", 'ERROR {"errorMessages": ["Error in the JQL Query"]}\n'))

    def test_usage(self):
        root, env, _ = fake_project("*) reply 200 '{}' ;;")
        r = run_script("jira-search.sh", [], root, env)
        self.assertEqual((r.returncode, r.stdout, r.stderr),
                         (2, "", usage("jira-search.sh", "'<JQL>' [extra,fields]")))
        self.assertEqual(calls(root), [])


class Transition(unittest.TestCase):
    STATUS = '{"fields":{"status":{"name":"In Progress","id":"3"}}}'

    def project(self, post_code="204"):
        return fake_project("""
            *" POST "*) reply %s ;;
            *"/transitions "*) reply 200 "$(cat "$B/transitions.json")" ;;
            *) reply 200 '%s' ;;
        """ % (post_code, self.STATUS), bodies={"transitions.json": {"transitions": [
            {"id": "6", "name": "Start", "to": {"id": "3", "statusCategory": {"key": "indeterminate"}}},
            {"id": "9", "name": "Close", "to": {"id": "10002", "statusCategory": {"key": "done"}}}]}})

    def test_moves_the_issue_and_reads_the_status_back(self):
        root, env, _ = self.project()
        r = run_script("jira-transition.sh", ["ABC-7", "6"], root, env)
        self.assertEqual((r.returncode, r.stdout, r.stderr),
                         (0, "ABC-7 transition 6 → HTTP 204 · now In Progress (3)\n", ""))
        post, read = calls(root)
        self.assertEqual((post["method"], post["url"]), ("POST", API + "/issue/ABC-7/transitions"))
        self.assertEqual(json.loads(post["data"][0]), {"transition": {"id": "6"}})
        self.assertEqual((read["method"], read["url"]), ("GET", API + "/issue/ABC-7?fields=status"))

    def test_fields_json_goes_into_the_body(self):
        root, env, _ = self.project()
        r = run_script("jira-transition.sh", ["ABC-7", "9", '{"customfield_10138":{"id":"10051"}}'], root, env)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads(calls(root)[0]["data"][0]),
                         {"transition": {"id": "9"}, "fields": {"customfield_10138": {"id": "10051"}}})

    def test_a_refused_transition_prints_the_code_and_exits_1(self):
        root, env, _ = self.project(post_code="400")
        r = run_script("jira-transition.sh", ["ABC-7", "6"], root, env)
        self.assertEqual((r.returncode, r.stdout, r.stderr),
                         (1, "ABC-7 transition 6 → HTTP 400 · now In Progress (3)\n", ""))

    def test_list_shows_the_transitions_offered(self):
        root, env, _ = self.project()
        r = run_script("jira-transition.sh", ["ABC-7", "--list"], root, env)
        self.assertEqual((r.returncode, r.stderr), (0, ""))
        self.assertEqual(r.stdout, "6 → Start (status 3, indeterminate)\n9 → Close (status 10002, done)\n")
        self.assertEqual(requests(root), ["GET " + API + "/issue/ABC-7/transitions"])

    def test_list_on_a_jira_error_body_exits_1_with_nothing_on_stdout(self):
        root, env, _ = fake_project("*) reply 404 '%s' ;;" % NOT_FOUND)
        r = run_script("jira-transition.sh", ["ABC-404", "--list"], root, env)
        self.assertEqual((r.returncode, r.stdout), (1, ""))

    def test_usage(self):
        root, env, _ = self.project()
        r = run_script("jira-transition.sh", ["ABC-7"], root, env)
        self.assertEqual((r.returncode, r.stdout, r.stderr),
                         (2, "", usage("jira-transition.sh", "<KEY> <transition-id|--list> [fields-json]")))
        self.assertEqual(calls(root), [])


class Comment(unittest.TestCase):
    MD = "<!-- template note -->\n**Fixed** in `web/src/a.ts:12`\n\n::video %s\n\n- one\n- two\n" % UUID
    RENDERED = ('<p><b>Fixed</b> in <code>web/src/a.ts:12</code></p><video><source type="video/mp4" '
                'src="/rest/api/3/attachment/content/501"/></video>')

    def project(self, rendered=None, read_code="200", write_code="201", md=None):
        root, env, _ = fake_project("""
            *"?fields=summary "*) reply %s '{"id":"10077"}' ;;
            *" POST "*) reply %s '{"id":"61300"}' ;;
            *" PUT "*) reply 200 '{"id":"61260"}' ;;
            *"/comment/61260?expand=renderedBody "*) reply 200 "$(cat "$B/updated.json")" ;;
            *) reply 200 "$(cat "$B/created.json")" ;;
        """ % (read_code, write_code), bodies={
            "created.json": {"id": "61300", "renderedBody": self.RENDERED if rendered is None else rendered},
            "updated.json": {"id": "61260", "renderedBody": self.RENDERED}})
        with open(os.path.join(root, "comment.md"), "w", encoding="utf-8") as fh:
            fh.write(self.MD if md is None else md)
        return root, env

    def test_posts_the_comment_as_adf_and_reads_it_back(self):
        root, env = self.project()
        r = run_script("jira-comment.sh", ["ABC-7", "comment.md"], root, env)
        self.assertEqual((r.returncode, r.stderr), (0, ""))
        self.assertEqual(r.stdout,
                         "comment 61300 created · videos in md 1 · players rendered 1 · attachment ids ['501']\n")
        self.assertEqual(requests(root), ["GET " + API + "/issue/ABC-7?fields=summary",
                                          "POST " + API + "/issue/ABC-7/comment",
                                          "GET " + API + "/issue/ABC-7/comment/61300?expand=renderedBody"])
        body = json.loads(calls(root)[1]["data"][0])["body"]
        self.assertEqual([n["type"] for n in body["content"]], ["paragraph", "mediaSingle", "bulletList"])
        self.assertEqual(body["content"][1]["content"][0]["attrs"],
                         {"type": "file", "id": UUID, "collection": "jira-10077"})
        self.assertNotIn("template note", json.dumps(body))

    def test_a_comment_id_updates_that_comment(self):
        root, env = self.project()
        r = run_script("jira-comment.sh", ["ABC-7", "comment.md", "61260"], root, env)
        self.assertEqual((r.returncode, r.stderr), (0, ""))
        self.assertEqual(r.stdout,
                         "comment 61260 updated · videos in md 1 · players rendered 1 · attachment ids ['501']\n")
        self.assertEqual(requests(root)[1:], ["PUT " + API + "/issue/ABC-7/comment/61260",
                                              "GET " + API + "/issue/ABC-7/comment/61260?expand=renderedBody"])

    def test_warns_when_the_player_or_a_code_span_did_not_render(self):
        root, env = self.project(rendered="<p>Fixed in web/src/other.ts</p>")
        r = run_script("jira-comment.sh", ["ABC-7", "comment.md"], root, env)
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stdout, "comment 61300 created · videos in md 1 · players rendered 0 · attachment ids []\n")
        self.assertEqual(r.stderr, "WARNING: no inline player rendered — check the media uuids\n"
                                   "WARNING: these `code` spans are missing from the rendered comment "
                                   "(unquoted heredoc?): ['web/src/a.ts:12']\n")

    def test_an_issue_that_cannot_be_read_fails_before_posting(self):
        root, env = self.project(read_code="404")
        r = run_script("jira-comment.sh", ["ABC-7", "comment.md"], root, env)
        self.assertEqual((r.returncode, r.stdout, r.stderr),
                         (1, "", 'FAILED reading ABC-7: HTTP 404 {"id":"10077"}\n'))
        self.assertEqual(len(calls(root)), 1)

    def test_a_refused_comment_fails_with_the_code_and_body(self):
        root, env = self.project(write_code="400")
        r = run_script("jira-comment.sh", ["ABC-7", "comment.md"], root, env)
        self.assertEqual((r.returncode, r.stdout, r.stderr),
                         (1, "", 'FAILED ABC-7 comment: HTTP 400 {"id":"61300"}\n'))
        self.assertEqual(len(calls(root)), 2)

    def test_usage(self):
        root, env = self.project()
        r = run_script("jira-comment.sh", ["ABC-7"], root, env)
        self.assertEqual((r.returncode, r.stdout, r.stderr),
                         (2, "", usage("jira-comment.sh", "<KEY> <comment.md> [commentId]")))
        self.assertEqual(calls(root), [])


class Attach(unittest.TestCase):
    def project(self, post_code="200"):
        root, env, _ = fake_project("""
            *"file=@"*"before.mp4"*) reply %s '[{"id":"501","filename":"before.mp4","size":6}]' ;;
            *"file=@"*) reply 200 '[{"id":"502","filename":"after.mp4","size":5}]' ;;
            *"/attachment/content/501 "*) reply 303 '' 'https://api.media.example.test/file/%s/binary?token=x' ;;
            *) reply 404 '' '' ;;
        """ % (post_code, UUID))
        for name, text in (("before.mp4", "before"), ("after.mp4", "after")):
            with open(os.path.join(root, name), "w") as fh:
                fh.write(text)
        return root, env

    def test_uploads_each_file_and_prints_its_media_uuid(self):
        root, env = self.project()
        r = run_script("jira-attach.sh", ["ABC-7", "before.mp4", "after.mp4"], root, env)
        self.assertEqual((r.returncode, r.stderr), (0, ""))
        self.assertEqual(r.stdout, "attached before.mp4 id 501 6 bytes media %s\n"
                                   "attached after.mp4 id 502 5 bytes media UNKNOWN\n" % UUID)
        self.assertEqual(requests(root), ["POST " + API + "/issue/ABC-7/attachments",
                                          "GET " + API + "/attachment/content/501",
                                          "POST " + API + "/issue/ABC-7/attachments",
                                          "GET " + API + "/attachment/content/502"])
        self.assertIn("X-Atlassian-Token: no-check", calls(root)[0]["argv"])

    def test_a_path_that_is_not_a_file_is_exit_2_before_any_upload(self):
        # pinned exit 0 with "skip (not a file)" until a caller needed the exit code: now a refused argument
        root, env = self.project()
        for args in (["before.mp4", "missing.mp4"], ["missing.mp4", "before.mp4"], [root]):
            r = run_script("jira-attach.sh", ["ABC-7"] + args, root, env)
            bad = [a for a in args if a != "before.mp4"][0]
            self.assertEqual((r.returncode, r.stdout), (2, ""), args)
            self.assertEqual(r.stderr, "jira-attach.sh: file must be an existing file, got '%s'\n" % bad)
        self.assertEqual(calls(root), [])

    def test_a_refused_upload_is_exit_1_and_the_next_file_still_goes(self):
        # pinned exit 0 until a caller needed the exit code: a refused upload is now exit 1
        root, env = self.project(post_code="413")
        failed = 'FAILED ABC-7 before.mp4 HTTP 413: [{"id":"501","filename":"before.mp4","size":6}]\n'
        r = run_script("jira-attach.sh", ["ABC-7", "before.mp4", "after.mp4"], root, env)
        self.assertEqual((r.returncode, r.stderr), (1, failed))
        self.assertEqual(r.stdout, "attached after.mp4 id 502 5 bytes media UNKNOWN\n")
        self.assertEqual(len(calls(root)), 3, "the second file is still uploaded and looked up")

    def test_a_refused_last_upload_is_exit_1_too(self):
        root, env = self.project(post_code="413")
        r = run_script("jira-attach.sh", ["ABC-7", "after.mp4", "before.mp4"], root, env)
        self.assertEqual(r.returncode, 1)
        self.assertEqual(r.stdout, "attached after.mp4 id 502 5 bytes media UNKNOWN\n")
        r = run_script("jira-attach.sh", ["ABC-7", "before.mp4"], root, env)
        self.assertEqual((r.returncode, r.stdout), (1, ""))

    def test_no_answer_from_jira_is_a_failed_upload(self):
        root, env, _ = fake_project("", curl="#!/bin/bash\ncat > /dev/null\nexit 7\n")
        with open(os.path.join(root, "before.mp4"), "w") as fh:
            fh.write("before")
        r = run_script("jira-attach.sh", ["ABC-7", "before.mp4"], root, env)
        self.assertEqual((r.returncode, r.stdout, r.stderr), (1, "", "FAILED ABC-7 before.mp4 HTTP 000: \n"))

    def test_usage(self):
        root, env = self.project()
        r = run_script("jira-attach.sh", ["ABC-7"], root, env)
        self.assertEqual((r.returncode, r.stdout, r.stderr), (2, "", usage("jira-attach.sh", "<KEY> <file>...")))
        self.assertEqual(calls(root), [])


class Download(unittest.TestCase):
    LIST = {"fields": {"attachment": [{"id": "501", "filename": "before.mp4"},
                                      {"id": "502", "filename": "logs/app.log"}]}}

    def project(self, listing=None):
        return fake_project("""
            *"?fields=attachment "*) reply 200 "$(cat "$B/list.json")" ;;
            *"/attachment/content/501 "*) reply 200 'video' ;;
            *"/attachment/content/502 "*) reply 200 'log line' ;;
        """, bodies={"list.json": self.LIST if listing is None else listing})[:2]

    def test_downloads_every_attachment_into_the_folder(self):
        root, env = self.project()
        r = run_script("jira-download.sh", ["ABC-7", "out"], root, env)
        self.assertEqual((r.returncode, r.stderr), (0, ""))
        self.assertEqual(r.stdout, "downloaded 501 before.mp4 5 bytes\ndownloaded 502 logs_app.log 8 bytes\n")
        self.assertEqual(sorted(os.listdir(os.path.join(root, "out"))), ["before.mp4", "logs_app.log"])
        with open(os.path.join(root, "out", "logs_app.log")) as fh:
            self.assertEqual(fh.read(), "log line")
        self.assertEqual(requests(root), ["GET " + API + "/issue/ABC-7?fields=attachment",
                                          "GET " + API + "/attachment/content/501",
                                          "GET " + API + "/attachment/content/502"])
        self.assertIn("-L", calls(root)[1]["argv"])

    def test_ids_pick_which_attachments_to_download(self):
        root, env = self.project()
        r = run_script("jira-download.sh", ["ABC-7", "out", "502"], root, env)
        self.assertEqual((r.returncode, r.stdout, r.stderr), (0, "downloaded 502 logs_app.log 8 bytes\n", ""))
        self.assertEqual(os.listdir(os.path.join(root, "out")), ["logs_app.log"])

    def test_an_issue_with_no_attachment_downloads_nothing(self):
        root, env = self.project(listing={"fields": {"attachment": []}})
        r = run_script("jira-download.sh", ["ABC-7", "out"], root, env)
        self.assertEqual((r.returncode, r.stdout, r.stderr), (0, "", ""))
        self.assertEqual(len(calls(root)), 1)

    def test_a_jira_error_body_exits_1_with_nothing_on_stdout(self):
        root, env, _ = fake_project("*) reply 404 '%s' ;;" % NOT_FOUND)
        r = run_script("jira-download.sh", ["ABC-404", "out"], root, env)
        self.assertEqual((r.returncode, r.stdout), (1, ""))
        self.assertEqual(len(calls(root)), 1)

    def test_usage(self):
        root, env = self.project()
        r = run_script("jira-download.sh", ["ABC-7"], root, env)
        self.assertEqual((r.returncode, r.stdout, r.stderr),
                         (2, "", usage("jira-download.sh", "<KEY> <out-dir> [ids...]")))
        self.assertEqual(calls(root), [])


class NoSecretAnywhere(unittest.TestCase):
    def test_the_token_reaches_curl_on_stdin_only(self):
        root, env, log = fake_project('*) reply 200 "$(cat "$B/issue.json")" ;;', bodies={"issue.json": ISSUE})
        r = run_script("jira-get.sh", ["ABC-7"], root, env)
        self.assertEqual(r.returncode, 0, r.stderr)
        with open(log) as fh:
            self.assertNotIn(TOKEN, r.stdout + r.stderr + fh.read())
        self.assertTrue(calls(root)[0]["auth"])


if __name__ == "__main__":
    unittest.main()
