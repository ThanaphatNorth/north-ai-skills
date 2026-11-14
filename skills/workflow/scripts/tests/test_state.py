"""Tests for _state.sh: tracker.env is read as text, never run, for both backends, through tracker.sh.

tracker.env is committed with the project, so a line in it must not be able to run anything on the machine of
whoever runs a loop: only the lines of the known settings are taken, and nothing inside a value is expanded.

  python3 -m unittest discover -s skills/workflow/scripts/tests -p 'test_*.py'
"""
import os
import subprocess
import tempfile
import unittest

from fakejira import SCRIPTS, SITE, calls, fake_project

TRACKER = os.path.join(SCRIPTS, "tracker.sh")
CARD = ("---\ntitle: one\ntype: bug\nstatus: todo\nlabels: ai-queue\npriority: high\nrank: 10\n"
        "created: 2026-11-10 09:00\nupdated: 2026-11-12 09:00\nlinks:\n---\n\n## Description\nx\n\n## Comments\n")
LISTING = """*) reply 200 '{"transitions":[{"id":"6","name":"Start","to":{"id":"3","statusCategory":{"key":"new"}}}]}' ;;"""
LISTED = "6 → Start (status 3, new)\n"
URL = SITE + "/rest/api/3/issue/ABC-7/transitions"


def door(args, root, env):
    return subprocess.run([TRACKER] + args, cwd=root, env=env, capture_output=True, text=True)


def write_env(root, text, folder="90north-develop"):
    with open(os.path.join(root, ".claude", folder, "tracker.env"), "w", encoding="utf-8") as fh:
        fh.write(text)


def local_project(env_text, board="board", folder="90north-develop"):
    """A project on the local board with one card, TASK-1. Returns (root, state folder, env)."""
    root = os.path.realpath(tempfile.mkdtemp())
    dl = os.path.join(root, ".claude", folder)
    os.makedirs(os.path.join(dl, board))
    write_env(root, env_text, folder)
    with open(os.path.join(dl, board, "TASK-1.md"), "w", encoding="utf-8") as fh:
        fh.write(CARD)
    env = dict(os.environ, HOME=root)
    for name in ("DEVELOP_DIR", "DEFECT_LOOP_DIR", "TRACKER", "LOCAL_BOARD", "LOCAL_STATUSES", "JIRA_SITE", "JIRA_ENV_FILE"):
        env.pop(name, None)
    return root, dl, env


def jira_project(env_text):
    """A project on the fake Jira; {creds} in env_text is the credentials file's path. Returns (root, env)."""
    root, env, _ = fake_project(LISTING)
    write_env(root, env_text.format(creds=os.path.join(root, "jira.env")))
    return root, env


def statuses(root, env):
    return door(["transition", "TASK-1", "--list"], root, env)


def listing(root, env):
    return door(["transition", "ABC-7", "--list"], root, env)


JIRA_LINES = "JIRA_SITE=" + SITE + "\nJIRA_ENV_FILE={creds}\n"


class NeverRun(unittest.TestCase):
    def test_a_command_line_in_tracker_env_is_not_run(self):
        root, env = jira_project("touch marker-jira\n" + JIRA_LINES + "touch marker-jira\n")
        r = listing(root, env)
        self.assertEqual((r.returncode, r.stdout, r.stderr), (0, LISTED, ""))
        root2, _, env2 = local_project("TRACKER=local\ntouch marker-local\n")
        r2 = statuses(root2, env2)
        self.assertEqual((r2.returncode, r2.stdout.splitlines()[0], r2.stderr), (0, "todo  ← now", ""))
        self.assertEqual([p for p in (os.path.join(root, "marker-jira"), os.path.join(root2, "marker-local"))
                          if os.path.exists(p)], [], "tracker.env was run as shell")

    def test_a_substitution_in_a_value_is_text(self):
        for form in ("$(touch marker-sub)", "`touch marker-sub`"):
            root, env = jira_project('JIRA_SITE="%s/%s"\nJIRA_ENV_FILE={creds}\n' % (SITE, form))
            r = listing(root, env)
            self.assertEqual(calls(root)[0]["url"], "%s/%s/rest/api/3/issue/ABC-7/transitions" % (SITE, form))
            self.assertFalse(os.path.exists(os.path.join(root, "marker-sub")), form)
            root, _, env = local_project('TRACKER=local\nLOCAL_BOARD="%s"\n' % form)
            r = statuses(root, env)
            self.assertEqual(r.returncode, 1)
            self.assertIn(form, r.stderr)
            self.assertFalse(os.path.exists(os.path.join(root, "marker-sub")), form)

    def test_a_variable_in_a_value_is_text(self):
        root, _, env = local_project('TRACKER=local\nLOCAL_STATUSES="$HOME,todo,${PATH}"\n')
        r = statuses(root, env)
        self.assertEqual((r.returncode, r.stdout), (0, "$HOME\ntodo  ← now\n${PATH}\n"), r.stderr)
        root, env = jira_project("JIRA_SITE=" + SITE + '\nJIRA_ENV_FILE="$HOME/jira.env"\n')
        r = listing(root, env)
        self.assertEqual((r.returncode, r.stdout), (2, ""))
        self.assertEqual(r.stderr, "missing credentials file $HOME/jira.env (JIRA_EMAIL, JIRA_TOKEN; chmod 600)\n")

    def test_a_setting_it_does_not_know_is_ignored(self):
        other = "PATH=/nowhere\nexport IFS=x\nHOME=/elsewhere\nBASH_ENV=/tmp/x\nJIRA_SITE_OLD=https://old.example.test\n"
        root, env = jira_project(other + JIRA_LINES + other)
        r = listing(root, env)
        self.assertEqual((r.returncode, r.stdout, r.stderr), (0, LISTED, ""))
        self.assertEqual(calls(root)[0]["url"], URL)
        root, _, env = local_project(other + "TRACKER=local\n" + other)
        r = statuses(root, env)
        self.assertEqual((r.returncode, r.stdout.splitlines()[0], r.stderr), (0, "todo  ← now", ""))

    def test_windows_line_ends_are_not_part_of_a_value(self):
        root, _, env = local_project("TRACKER=local\r\nLOCAL_STATUSES=todo,done\r\n")
        r = statuses(root, env)
        self.assertEqual((r.returncode, r.stdout), (0, "todo  ← now\ndone\n"), r.stderr)


class Parsed(unittest.TestCase):
    """What a tracker.env could already say, and still can."""

    def test_quoted_and_exported_values(self):
        root, env = jira_project('export TRACKER="jira"\nexport JIRA_SITE=\'%s/\'\nexport JIRA_ENV_FILE="{creds}"\n' % SITE)
        r = listing(root, env)
        self.assertEqual((r.returncode, r.stdout, r.stderr), (0, LISTED, ""))
        self.assertEqual(calls(root)[0]["url"], URL)
        root, _, env = local_project("export TRACKER='local'\nexport LOCAL_BOARD=\"my cards\"\n"
                                     "LOCAL_STATUSES='todo, in review ,done'\n", board="my cards")
        r = statuses(root, env)
        self.assertEqual((r.returncode, r.stdout, r.stderr), (0, "todo  ← now\nin review\ndone\n", ""))

    def test_comments_blank_lines_and_the_last_line_of_a_name(self):
        root, _, env = local_project("# the backend\n\n  TRACKER=jira\nTRACKER=local   # no Jira here\n\n"
                                     "# LOCAL_BOARD=elsewhere\nLOCAL_BOARD=cards            # relative to this folder\n"
                                     "LOCAL_STATUSES=todo,done", board="cards")
        r = statuses(root, env)
        self.assertEqual((r.returncode, r.stdout, r.stderr), (0, "todo  ← now\ndone\n", ""))

    def test_no_tracker_line_is_jira(self):
        root, env = jira_project(JIRA_LINES)
        self.assertEqual(listing(root, env).stdout, LISTED)

    def test_the_calling_shell_cannot_set_the_local_settings(self):
        root, _, env = local_project("TRACKER=local\n")
        r = statuses(root, dict(env, TRACKER="jira", LOCAL_BOARD="/elsewhere", LOCAL_STATUSES="a,b"))
        self.assertEqual((r.returncode, r.stdout.splitlines()[0], r.stderr), (0, "todo  ← now", ""))

    def test_the_calling_shell_cannot_choose_the_jira_site_or_the_credentials_file(self):
        """A site taken from the environment would send the token to whoever set that variable."""
        root, env = jira_project("TRACKER=jira\n")
        hostile = dict(env, JIRA_SITE="https://elsewhere.example", JIRA_ENV_FILE=os.path.join(root, "jira.env"))
        r = listing(root, hostile)
        self.assertEqual((r.returncode != 0, calls(root)), (True, []))  # refused, and no request went anywhere
        self.assertIn("JIRA_SITE missing in tracker.env", r.stderr)

    def test_a_board_under_the_home_folder(self):
        root, dl, env = local_project("TRACKER=local\nLOCAL_BOARD=~/.claude/90north-develop/board\n")
        r = statuses(root, env)  # HOME is the project root
        self.assertEqual((r.returncode, r.stdout.splitlines()[0], r.stderr), (0, "todo  ← now", ""))


class StateFolder(unittest.TestCase):
    def test_the_legacy_folder_is_found_with_a_note(self):
        root, dl, env = local_project("TRACKER=local\n", folder="defect-loop")
        r = statuses(root, env)
        self.assertEqual((r.returncode, r.stdout.splitlines()[0]), (0, "todo  ← now"))
        self.assertEqual(r.stderr, "note: legacy state folder %s — /90north-develop:develop-init migrates it\n" % dl)

    def test_develop_dir_or_the_legacy_variable_names_the_folder(self):
        root, dl, env = local_project("TRACKER=local\n")
        for name in ("DEVELOP_DIR", "DEFECT_LOOP_DIR"):
            r = door(["transition", "TASK-1", "--list"], tempfile.mkdtemp(), dict(env, **{name: dl}))
            self.assertEqual((r.returncode, r.stdout.splitlines()[0], r.stderr), (0, "todo  ← now", ""), name)

    def test_no_state_folder_is_exit_2(self):
        r = door(["search", "status=todo"], tempfile.mkdtemp(), local_project("TRACKER=local\n")[2])
        self.assertEqual(r.returncode, 2)
        self.assertIn("develop-init", r.stderr)

    def test_the_folder_is_found_from_a_subfolder(self):
        root, dl, env = local_project("TRACKER=local\n")
        deep = os.path.join(root, "src", "deep")
        os.makedirs(deep)
        r = door(["transition", "TASK-1", "--list"], deep, env)
        self.assertEqual((r.returncode, r.stdout.splitlines()[0], r.stderr), (0, "todo  ← now", ""))


if __name__ == "__main__":
    unittest.main()
