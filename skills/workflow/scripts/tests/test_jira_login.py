"""Tests for jira-login.sh: it asks for the email and the API token and writes the credentials file itself.

The token is typed on the terminal (or piped on stdin when there is none), so it is never in a chat, an argv or
the environment; the file is 600, replaced only with --force, and checked with one GET /rest/api/3/myself.

  python3 -m unittest discover -s skills/workflow/scripts/tests -p 'test_*.py'
"""
import os
import pty
import select
import stat
import termios
import time
import unittest

from fakejira import EMAIL, SCRIPTS, SITE, TOKEN, calls, fake_project, requests, run_script

LOGIN = os.path.join(SCRIPTS, "jira-login.sh")
MYSELF = """
    *"/rest/api/3/myself "*) reply 200 '{"accountId":"5b10","displayName":"Bot User"}' ;;
    *) reply 200 '{"transitions":[]}' ;;
"""
TRICKY = ('to"k\\en $HOME `id` #x', "it's", "a b  c", "=x=", "'quoted'", '"quoted"', "back\\", "ก-โทเคน")


def project(arms=MYSELF, token=TOKEN, existing=None, **kwargs):
    """A fake project whose credentials file does not exist yet (or holds `existing`)."""
    root, env, _ = fake_project(arms, token=token, creds=existing, **kwargs)
    path = os.path.join(root, "jira.env")
    if existing is None:
        os.remove(path)
    return root, env, path


def mode(path):
    return stat.S_IMODE(os.stat(path).st_mode)


def typed(email=EMAIL, token=TOKEN):
    return "%s\n%s\n" % (email, token)


class Login(unittest.TestCase):
    def test_writes_the_file_600_checks_it_and_prints_only_ok(self):
        root, env, path = project()
        r = run_script("jira-login.sh", [], root, env, stdin=typed())
        self.assertEqual((r.returncode, r.stdout, r.stderr), (0, "OK Bot User\n", ""))
        self.assertEqual(mode(path), 0o600)
        self.assertEqual(requests(root), ["GET " + SITE + "/rest/api/3/myself"])
        self.assertEqual([c["config"] for c in calls(root)], [[["user", EMAIL + ":" + TOKEN]]])
        self.assertEqual([n for n in os.listdir(root) if n.startswith(".jira-login")], [],
                         "no temp file is left beside the credentials file")

    def test_any_token_stays_out_of_output_argv_and_environment_and_reads_back(self):
        for token in (TOKEN,) + TRICKY:
            root, env, path = project(token=token)
            r = run_script("jira-login.sh", [], root, env, stdin=typed(token=token))
            self.assertEqual((r.returncode, r.stdout), (0, "OK Bot User\n"), token)
            self.assertNotIn(token, r.stdout + r.stderr)
            # the file it wrote is read back by the parser every other script uses
            r = run_script("jira-transition.sh", ["ABC-7", "--list"], root, env)
            self.assertEqual((r.returncode, r.stderr), (0, ""), token)
            self.assertEqual([(c["auth"], c["leaks"]) for c in calls(root)], [(True, []), (True, [])], token)
            with open(os.path.join(root, "curl.log"), encoding="utf-8") as fh:
                self.assertNotIn(token, fh.read())

    def test_blanks_and_a_carriage_return_around_a_typed_value_are_dropped(self):
        root, env, path = project()
        r = run_script("jira-login.sh", [], root, env, stdin="  %s \r\n\t%s \r\n" % (EMAIL, TOKEN))
        self.assertEqual((r.returncode, r.stdout), (0, "OK Bot User\n"), r.stderr)

    def test_a_last_line_without_a_newline_is_still_read(self):
        root, env, path = project()
        r = run_script("jira-login.sh", [], root, env, stdin="%s\n%s" % (EMAIL, TOKEN))
        self.assertEqual((r.returncode, r.stdout), (0, "OK Bot User\n"), r.stderr)


class Overwrite(unittest.TestCase):
    OLD = "JIRA_EMAIL=old@example.test\nJIRA_TOKEN=old-token\n"

    def test_an_existing_file_is_not_replaced_without_force(self):
        root, env, path = project(existing=self.OLD)
        os.chmod(path, 0o400)
        r = run_script("jira-login.sh", [], root, env, stdin=typed())
        self.assertEqual((r.returncode, r.stdout), (2, ""))
        self.assertEqual(r.stderr, "jira-login.sh: %s already exists; pass --force to replace it\n" % path)
        with open(path) as fh:
            self.assertEqual(fh.read(), self.OLD)
        self.assertEqual(mode(path), 0o400)
        self.assertEqual(calls(root), [])

    def test_a_dangling_link_counts_as_existing(self):
        root, env, path = project()
        os.symlink(os.path.join(root, "elsewhere.env"), path)
        r = run_script("jira-login.sh", [], root, env, stdin=typed())
        self.assertEqual(r.returncode, 2)
        self.assertFalse(os.path.exists(os.path.join(root, "elsewhere.env")))

    def test_force_replaces_it_and_the_new_file_is_600(self):
        root, env, path = project(existing=self.OLD)
        os.chmod(path, 0o644)
        for args in (["--force"], ["--force", path], [path, "--force"]):
            r = run_script("jira-login.sh", args, root, env, stdin=typed())
            self.assertEqual((r.returncode, r.stdout, r.stderr), (0, "OK Bot User\n", ""), args)
            self.assertEqual(mode(path), 0o600)
        with open(path) as fh:
            self.assertNotIn("old-token", fh.read())

    def test_force_replaces_a_link_itself_not_the_file_it_points_to(self):
        root, env, path = project()
        other = os.path.join(root, "elsewhere.env")
        with open(other, "w") as fh:
            fh.write("untouched\n")
        os.symlink(other, path)
        r = run_script("jira-login.sh", ["--force"], root, env, stdin=typed())
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertFalse(os.path.islink(path))
        with open(other) as fh:
            self.assertEqual(fh.read(), "untouched\n")


class PathArgument(unittest.TestCase):
    def test_a_path_is_written_instead_of_the_one_in_tracker_env(self):
        root, env, default = project()
        r = run_script("jira-login.sh", ["secrets/team jira.env"], root, env, stdin=typed())
        self.assertEqual((r.returncode, r.stdout, r.stderr), (0, "OK Bot User\n", ""))
        path = os.path.join(root, "secrets", "team jira.env")
        self.assertEqual((mode(path), mode(os.path.dirname(path))), (0o600, 0o700))
        self.assertFalse(os.path.exists(default))
        self.assertEqual([c["auth"] for c in calls(root)], [True])

    def test_a_folder_is_refused_even_with_force(self):
        root, env, _ = project()
        os.mkdir(os.path.join(root, "secrets"))
        r = run_script("jira-login.sh", ["--force", "secrets"], root, env, stdin=typed())
        self.assertEqual((r.returncode, r.stdout), (2, ""))
        self.assertEqual(os.listdir(os.path.join(root, "secrets")), [])

    def test_usage(self):
        root, env, path = project()
        for args in (["--bogus"], ["-f"], ["a.env", "b.env"]):
            r = run_script("jira-login.sh", args, root, env, stdin=typed())
            self.assertEqual((r.returncode, r.stdout, r.stderr), (2, "", "usage: %s [--force] [path]\n" % LOGIN), args)
        self.assertFalse(os.path.exists(path))
        self.assertEqual(calls(root), [])


class Refused(unittest.TestCase):
    def test_an_empty_or_odd_email_or_an_empty_token_writes_nothing(self):
        for stdin, says in (("", "email"), ("\n\n", "email"), ("not-an-email\n%s\n" % TOKEN, "email"),
                            ("a@b:c\n%s\n" % TOKEN, "email"), ("a b@c\n%s\n" % TOKEN, "email"),
                            (EMAIL + "\n", "API token"), (EMAIL + "\n   \n", "API token")):
            root, env, path = project()
            r = run_script("jira-login.sh", [], root, env, stdin=stdin)
            self.assertEqual((r.returncode, r.stdout), (2, ""), stdin)
            self.assertIn(says, r.stderr)
            self.assertNotIn(TOKEN, r.stderr)
            self.assertFalse(os.path.exists(path), stdin)
            self.assertEqual(calls(root), [])
            self.assertEqual([n for n in os.listdir(root) if n.startswith(".jira-login")], [])

    def test_a_repo_on_the_local_board_has_nothing_to_log_in_to(self):
        root, env, path = project()
        with open(os.path.join(root, ".claude", "90north-develop", "tracker.env"), "w") as fh:
            fh.write("TRACKER=local\n")
        r = run_script("jira-login.sh", [], root, env, stdin=typed())
        self.assertEqual(r.returncode, 2)
        self.assertIn("TRACKER=local", r.stderr)
        self.assertFalse(os.path.exists(path))


class Check(unittest.TestCase):
    def test_a_refused_token_prints_only_failed_and_the_code(self):
        root, env, path = project()
        r = run_script("jira-login.sh", [], root, env, stdin=typed(token="wrong-token"))
        self.assertEqual((r.returncode, r.stdout, r.stderr), (1, "FAILED HTTP 401\n", ""))
        self.assertEqual(mode(path), 0o600)

    def test_no_answer_from_the_site_is_http_000(self):
        root, env, path = project(curl="#!/bin/bash\ncat > /dev/null\nprintf 000\nexit 7\n")
        r = run_script("jira-login.sh", [], root, env, stdin=typed())
        self.assertEqual((r.returncode, r.stdout), (1, "FAILED HTTP 000\n"))

    def test_a_200_that_is_not_the_account_is_failed_too(self):
        root, env, path = project("*) reply 200 '<html>Log in to continue</html>' ;;")
        r = run_script("jira-login.sh", [], root, env, stdin=typed())
        self.assertEqual((r.returncode, r.stdout), (1, "FAILED HTTP 200\n"))
        self.assertEqual(r.stderr, "ERROR expected JSON, got: <html>Log in to continue</html>\n")


class OnATerminal(unittest.TestCase):
    """With a terminal, the questions are asked there and the token is not echoed."""

    def run_on_a_terminal(self, root, env, answers):
        pid, fd = pty.fork()
        if pid == 0:
            os.chdir(root)
            os.execve("/bin/bash", ["bash", LOGIN], env)
        seen, deadline, answers = b"", time.time() + 30, list(answers)
        while time.time() < deadline:
            if select.select([fd], [], [], 0.05)[0]:
                try:
                    chunk = os.read(fd, 4096)
                except OSError:
                    break
                if not chunk:
                    break
                seen += chunk
            if answers and answers[0][0] in seen and (answers[0][2] or not termios.tcgetattr(fd)[3] & termios.ECHO):
                os.write(fd, answers.pop(0)[1])
        status = os.waitpid(pid, 0)[1]
        os.close(fd)
        return os.WEXITSTATUS(status), seen.decode("utf-8", "replace")

    def test_the_token_typed_on_the_terminal_is_not_echoed(self):
        root, env, path = project()
        # (wait for this prompt, type this, echo expected); the token is typed only once echo is off
        code, screen = self.run_on_a_terminal(root, env, [(b"Jira email", (EMAIL + "\n").encode(), True),
                                                          (b"API token", (TOKEN + "\n").encode(), False)])
        self.assertEqual(code, 0, screen)
        self.assertIn("Jira email for %s: " % SITE, screen)
        self.assertIn(EMAIL, screen)
        self.assertNotIn(TOKEN, screen)
        self.assertTrue(screen.rstrip().endswith("OK Bot User"), screen)
        self.assertEqual(mode(path), 0o600)
        self.assertEqual([c["auth"] for c in calls(root)], [True])


if __name__ == "__main__":
    unittest.main()
