"""Tests for _env.sh: where the Jira scripts get their settings, and how the credentials reach curl.

The credentials file is parsed (JIRA_EMAIL= and JIRA_TOKEN= lines only), never run as shell, and its values are
never exported: the only way out is `auth | curl -K -`.

  python3 -m unittest discover -s skills/workflow/scripts/tests -p 'test_*.py'
"""
import os
import stat
import unittest

from fakejira import EMAIL, SCRIPTS, TOKEN, calls, fake_project, real_curl, run_script

LISTING = """*) reply 200 '{"transitions":[]}' ;;"""
TRICKY = 'to"k\\en $HOME `id` #x'


def listing(root, env):
    """Any authenticated call will do: `transition --list` prints nothing for an empty list."""
    return run_script("jira-transition.sh", ["ABC-7", "--list"], root, env)


def tracker_env(root, text):
    with open(os.path.join(root, ".claude", "90north-develop", "tracker.env"), "w") as fh:
        fh.write(text)


class Pinned(unittest.TestCase):
    """Behaviour _env.sh had before the credentials file was parsed instead of sourced."""

    def assertAuthenticated(self, creds, token=TOKEN):
        root, env, _ = fake_project(LISTING, creds=creds, token=token)
        r = listing(root, env)
        self.assertEqual((r.returncode, r.stdout, r.stderr), (0, "", ""), creds)
        self.assertEqual([c["auth"] for c in calls(root)], [True], creds)

    def test_plain_quoted_and_exported_values(self):
        for creds in (
            "JIRA_EMAIL=%s\nJIRA_TOKEN=%s\n" % (EMAIL, TOKEN),
            'JIRA_EMAIL="%s"\nJIRA_TOKEN="%s"\n' % (EMAIL, TOKEN),
            "JIRA_EMAIL='%s'\nJIRA_TOKEN='%s'\n" % (EMAIL, TOKEN),
            'export JIRA_EMAIL=%s\nexport JIRA_TOKEN="%s"\n' % (EMAIL, TOKEN),
            "# the bot account\n\n  JIRA_EMAIL=%s\n\n# its token\nJIRA_TOKEN=%s" % (EMAIL, TOKEN),
            "JIRA_EMAIL=%s   # the bot\nJIRA_TOKEN='%s' # rotated in May\n" % (EMAIL, TOKEN),
            "JIRA_TOKEN=old\nJIRA_EMAIL=%s\nJIRA_TOKEN=%s\n" % (EMAIL, TOKEN),
        ):
            self.assertAuthenticated(creds)

    def test_a_quoted_value_keeps_its_spaces_and_hashes(self):
        self.assertAuthenticated('JIRA_EMAIL=%s\nJIRA_TOKEN="a b #c"\n' % EMAIL, token="a b #c")
        self.assertAuthenticated("JIRA_EMAIL=%s\nJIRA_TOKEN='a b #c'\n" % EMAIL, token="a b #c")

    def test_missing_credentials_file(self):
        root, env, _ = fake_project(LISTING)
        path = os.path.join(root, "jira.env")
        os.remove(path)
        r = listing(root, env)
        self.assertEqual((r.returncode, r.stdout), (2, ""))
        self.assertEqual(r.stderr, "missing credentials file %s (JIRA_EMAIL, JIRA_TOKEN; chmod 600)\n" % path)
        self.assertEqual(calls(root), [])

    def test_a_readable_by_others_file_is_tightened_to_600(self):
        root, env, _ = fake_project(LISTING)
        path = os.path.join(root, "jira.env")
        os.chmod(path, 0o644)
        r = listing(root, env)
        self.assertEqual((r.returncode, r.stderr), (0, "note: tightened %s to 600 (was 644)\n" % path))
        self.assertEqual(stat.S_IMODE(os.stat(path).st_mode), 0o600)

    def test_a_400_file_is_left_alone(self):
        root, env, _ = fake_project(LISTING)
        path = os.path.join(root, "jira.env")
        os.chmod(path, 0o400)
        r = listing(root, env)
        self.assertEqual((r.returncode, r.stderr), (0, ""))
        self.assertEqual(stat.S_IMODE(os.stat(path).st_mode), 0o400)

    def test_a_missing_or_empty_value_is_exit_2_with_the_file_named(self):
        for creds in ("JIRA_EMAIL=%s\n" % EMAIL, "JIRA_TOKEN=%s\n" % TOKEN, "JIRA_EMAIL=%s\nJIRA_TOKEN=\n" % EMAIL,
                      'JIRA_EMAIL=""\nJIRA_TOKEN=%s\n' % TOKEN, "", "# nothing yet\n"):
            root, env, _ = fake_project(LISTING, creds=creds)
            r = listing(root, env)
            self.assertEqual((r.returncode, r.stdout), (2, ""), creds)
            self.assertEqual(r.stderr, "JIRA_EMAIL / JIRA_TOKEN not set in %s\n" % os.path.join(root, "jira.env"))
            self.assertEqual(calls(root), [])

    def test_a_local_tracker_is_pointed_to_the_door(self):
        root, env, _ = fake_project(LISTING)
        tracker_env(root, "TRACKER=local\n")
        r = listing(root, env)
        self.assertEqual((r.returncode, r.stdout), (2, ""))
        self.assertEqual(r.stderr, "tracker.env says TRACKER=local: call scripts/tracker.sh <verb>, "
                                   "not jira-transition.sh\n")

    def test_site_and_credentials_path_must_be_in_tracker_env(self):
        root, env, _ = fake_project(LISTING)
        path = os.path.join(root, "jira.env")
        for text, missing in (("JIRA_ENV_FILE=%s\n" % path, "JIRA_SITE missing in tracker.env"),
                              ("JIRA_SITE=https://site.example.test\n", "JIRA_ENV_FILE missing in tracker.env")):
            tracker_env(root, text)
            r = listing(root, env)
            self.assertNotEqual(r.returncode, 0)
            self.assertIn(missing, r.stderr)
        self.assertEqual(calls(root), [])

    def test_a_tilde_in_the_credentials_path_is_home(self):
        root, env, _ = fake_project(LISTING)  # HOME is the project root
        tracker_env(root, "JIRA_SITE=https://site.example.test\nJIRA_ENV_FILE=~/jira.env\n")
        r = listing(root, env)
        self.assertEqual((r.returncode, r.stderr), (0, ""))
        self.assertEqual(calls(root)[0]["url"], "https://site.example.test/rest/api/3/issue/ABC-7/transitions")

    def test_no_state_folder_names_develop_init(self):
        root, env, _ = fake_project(LISTING)
        os.remove(os.path.join(root, ".claude", "90north-develop", "tracker.env"))
        r = listing(root, env)
        self.assertEqual(r.returncode, 2)
        self.assertIn("develop-init", r.stderr)


class ParsedNotExecuted(unittest.TestCase):
    def test_a_command_line_in_the_file_is_not_run(self):
        root, env, _ = fake_project(LISTING, creds="JIRA_EMAIL=%s\ntouch %s\nJIRA_TOKEN=%s\n"
                                    % (EMAIL, "marker-line", TOKEN))
        r = listing(root, env)
        self.assertEqual((r.returncode, r.stderr), (0, ""))
        self.assertFalse(os.path.exists(os.path.join(root, "marker-line")), "the credentials file was run as shell")
        self.assertEqual([c["auth"] for c in calls(root)], [True])

    def test_a_substitution_inside_a_value_is_not_run(self):
        for form in ("JIRA_TOKEN=$(touch marker-sub)", 'JIRA_TOKEN="$(touch marker-sub)"', "JIRA_TOKEN=`touch marker-sub`"):
            root, env, _ = fake_project(LISTING, creds="JIRA_EMAIL=%s\n%s\n" % (EMAIL, form))
            listing(root, env)
            self.assertFalse(os.path.exists(os.path.join(root, "marker-sub")), form)

    def test_a_double_quoted_value_is_literal_text(self):
        root, env, _ = fake_project(LISTING, creds='JIRA_EMAIL=%s\nJIRA_TOKEN="a$HOME-b"\n' % EMAIL, token="a$HOME-b")
        r = listing(root, env)
        self.assertEqual((r.returncode, [c["auth"] for c in calls(root)]), (0, [True]), r.stderr)

    def test_other_assignments_never_reach_the_environment(self):
        root, env, _ = fake_project(LISTING, creds="JIRA_EMAIL=%s\nJIRA_TOKEN=%s\nexport PATH=/nowhere\nFOO=%s\n"
                                    % (EMAIL, TOKEN, TOKEN))
        r = listing(root, env)
        self.assertEqual((r.returncode, r.stderr), (0, ""))
        self.assertEqual(calls(root)[0]["leaks"], [])


class NotExported(unittest.TestCase):
    def test_a_child_process_does_not_see_the_credentials(self):
        root, env, _ = fake_project(LISTING)
        r = listing(root, env)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(calls(root)[0]["leaks"], [], "JIRA_EMAIL / JIRA_TOKEN must not be in a child's environment")

    def test_credentials_exported_by_the_calling_shell_are_dropped_not_used(self):
        root, env, _ = fake_project(LISTING)
        r = listing(root, dict(env, JIRA_EMAIL="someone@else.test", JIRA_TOKEN="shell-token-999"))
        self.assertEqual(r.returncode, 0, r.stderr)
        call = calls(root)[0]
        self.assertTrue(call["auth"], "the file's values are the ones sent")
        self.assertEqual(call["leaks"], [])

    def test_the_file_is_the_only_source_of_the_credentials(self):
        root, env, _ = fake_project(LISTING, creds="JIRA_EMAIL=%s\n" % EMAIL)
        r = listing(root, dict(env, JIRA_TOKEN=TOKEN))
        self.assertEqual(r.returncode, 2)
        self.assertEqual(r.stderr, "JIRA_EMAIL / JIRA_TOKEN not set in %s\n" % os.path.join(root, "jira.env"))
        self.assertEqual(calls(root), [])


class QuotesAndBackslashes(unittest.TestCase):
    FORMS = (
        "JIRA_TOKEN='%s'" % TRICKY,  # single quotes: every character is itself
        'JIRA_TOKEN="%s"' % TRICKY.replace("\\", "\\\\").replace('"', '\\"').replace("$", "\\$").replace("`", "\\`"),
    )

    def test_a_token_with_a_quote_and_a_backslash_still_authenticates(self):
        for form in self.FORMS:
            root, env, _ = fake_project(LISTING, creds="JIRA_EMAIL=%s\n%s\n" % (EMAIL, form), token=TRICKY)
            r = listing(root, env)
            self.assertEqual(calls(root)[0]["config"], [["user", EMAIL + ":" + TRICKY]], form)
            self.assertEqual((r.returncode, r.stderr), (0, ""), form)

    def test_a_quote_in_the_token_cannot_add_a_curl_option(self):
        hostile = 'x"\nurl = "https://evil.example.test'
        for token in ('x" --next -o "/tmp/owned', 'x\\', hostile.replace("\n", " ")):
            root, env, _ = fake_project(LISTING, creds="JIRA_EMAIL=%s\nJIRA_TOKEN='%s'\n" % (EMAIL, token), token=token)
            listing(root, env)
            self.assertEqual(calls(root)[0]["config"], [["user", EMAIL + ":" + token]], token)

    def test_the_real_curl_reads_the_same_user_back(self):
        # the real curl parses what auth() wrote; file:// keeps it off the network and --libcurl shows what it understood
        wrapper = ('#!/bin/bash\nROOT="$(cd "$(dirname "$0")/.." && pwd)"\n'
                   'exec "%s" -sS -K - --libcurl "$ROOT/libcurl.c" -o /dev/null "file:///dev/null"\n' % real_curl(self))
        root, env, _ = fake_project("", creds="JIRA_EMAIL=%s\n%s\n" % (EMAIL, self.FORMS[0]), token=TRICKY, curl=wrapper)
        listing(root, env)
        with open(os.path.join(root, "libcurl.c")) as fh:
            source = fh.read()
        c_string = (EMAIL + ":" + TRICKY).replace("\\", "\\\\").replace('"', '\\"')
        self.assertIn('CURLOPT_USERPWD, "%s");' % c_string, source)
        self.assertEqual(source.count("curl_easy_setopt(hnd, CURLOPT_URL"), 1)


class Sourcing(unittest.TestCase):
    def test_every_jira_script_is_executable_so_the_door_can_run_it(self):
        scripts = sorted(n for n in os.listdir(SCRIPTS) if n.startswith("jira-") and n.endswith(".sh"))
        self.assertEqual([n for n in scripts if not os.access(os.path.join(SCRIPTS, n), os.X_OK)], [])


if __name__ == "__main__":
    unittest.main()
