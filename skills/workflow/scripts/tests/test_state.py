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


def moved_project(env_text="TRACKER=local\n", board="board"):
    """A project whose working state sits beside it, outside .claude/: settings in .claude/90north-develop/,
    the board in .90north-develop/. Returns (root, working state folder, env)."""
    root = os.path.realpath(tempfile.mkdtemp())
    os.makedirs(os.path.join(root, ".claude", "90north-develop"))
    state = os.path.join(root, ".90north-develop")
    os.makedirs(os.path.join(state, board))
    write_env(root, env_text)
    with open(os.path.join(state, board, "TASK-1.md"), "w", encoding="utf-8") as fh:
        fh.write(CARD)
    env = dict(os.environ, HOME=root)
    for name in ("DEVELOP_DIR", "DEVELOP_STATE_DIR", "DEFECT_LOOP_DIR", "TRACKER", "LOCAL_BOARD", "LOCAL_STATUSES",
                 "JIRA_SITE", "JIRA_ENV_FILE"):
        env.pop(name, None)
    return root, state, env


class WorkingState(unittest.TestCase):
    """Settings stay in .claude/90north-develop/. What a loop writes as it works (board, ledgers, runs) lives in
    .90north-develop/ beside the project, where a session that can ask nobody may still write."""

    def test_the_board_is_read_from_the_folder_beside_the_project(self):
        root, _, env = moved_project()
        r = statuses(root, env)
        self.assertEqual((r.returncode, r.stdout.splitlines()[0], r.stderr), (0, "todo  ← now", ""))

    def test_it_wins_over_a_board_left_behind_under_claude(self):
        root, _, env = moved_project()
        old = os.path.join(root, ".claude", "90north-develop", "board")
        os.makedirs(old)
        with open(os.path.join(old, "TASK-1.md"), "w", encoding="utf-8") as fh:
            fh.write(CARD.replace("status: todo", "status: review"))
        self.assertEqual(statuses(root, env).stdout.splitlines()[0], "todo  ← now")

    def test_a_board_named_in_tracker_env_is_relative_to_the_working_state(self):
        root, _, env = moved_project("TRACKER=local\nLOCAL_BOARD=cards\n", board="cards")
        r = statuses(root, env)
        self.assertEqual((r.returncode, r.stdout.splitlines()[0], r.stderr), (0, "todo  ← now", ""))

    def test_develop_state_dir_names_the_folder(self):
        root, state, env = moved_project()
        elsewhere = os.path.join(root, "kept-elsewhere")
        os.rename(state, elsewhere)
        r = statuses(root, dict(env, DEVELOP_STATE_DIR=elsewhere))
        self.assertEqual((r.returncode, r.stdout.splitlines()[0], r.stderr), (0, "todo  ← now", ""))

    def test_a_project_not_moved_yet_still_reads_its_board_under_claude(self):
        root, _, env = local_project("TRACKER=local\n")
        r = statuses(root, env)
        self.assertEqual((r.returncode, r.stdout.splitlines()[0]), (0, "todo  ← now"))

    def test_a_linked_worktree_uses_the_main_checkouts_working_state(self):
        root, state, env = moved_project()
        env.update(GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@x", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@x",
                   GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_NOSYSTEM="1")
        git = lambda *a: subprocess.run(["git", "-C", root] + list(a), env=env, capture_output=True, check=True)
        git("init", "-q", "-b", "main")
        git("add", "-A")
        git("commit", "-qm", "base")
        tree = os.path.join(root, "wt")
        git("worktree", "add", "-q", tree)
        r = door(["edit", "TASK-1", "--add-label", "seen"], tree, env)
        self.assertEqual(r.returncode, 0, r.stderr)
        with open(os.path.join(state, "board", "TASK-1.md"), encoding="utf-8") as fh:
            self.assertIn("seen", fh.read())
        with open(os.path.join(tree, ".90north-develop", "board", "TASK-1.md"), encoding="utf-8") as fh:
            self.assertNotIn("seen", fh.read())  # the worktree's own copy is not the board


class NotMovedYet(unittest.TestCase):
    """A project whose board and ledgers are still under .claude/ is read there until move-state.sh has run,
    whatever else has appeared beside it."""

    def test_a_stray_new_folder_does_not_hide_a_board_still_under_claude(self):
        root, _, env = local_project("TRACKER=local\n")
        os.makedirs(os.path.join(root, ".90north-develop", "runs", "2026-11-14"))
        with open(os.path.join(root, ".90north-develop", "runs", "2026-11-14", "run.md"), "w") as fh:
            fh.write("a pass wrote this before the move\n")
        r = statuses(root, env)
        self.assertEqual((r.returncode, r.stdout.splitlines()[0]), (0, "todo  ← now"), r.stderr)

    def test_a_stray_folder_under_claude_does_not_hide_a_moved_board(self):
        root, _, env = moved_project()
        os.makedirs(os.path.join(root, ".claude", "90north-develop", "runs", "2026-11-14"))
        r = statuses(root, env)
        self.assertEqual((r.returncode, r.stdout.splitlines()[0], r.stderr), (0, "todo  ← now", ""))

    def found(self, root, env):
        """The search finds the one card, wherever the working state is."""
        r = door(["search", "status=todo"], root, env)
        self.assertEqual((r.returncode, [line.split(" | ")[0] for line in r.stdout.splitlines()]), (0, ["TASK-1"]), r.stderr)

    def test_an_empty_board_folder_beside_does_not_hide_the_board_under_claude(self):
        root, dl, env = local_project("TRACKER=local\n")
        os.makedirs(os.path.join(root, ".90north-develop", "board"))
        self.found(root, env)
        self.assertEqual(where(root, env).stdout.splitlines()[1], "DL=" + dl)
        self.assertEqual(where(root, env, "--auto").returncode, 3)

    def test_an_empty_ledger_file_beside_does_not_hide_the_board_under_claude(self):
        root, dl, env = local_project("TRACKER=local\n")
        os.makedirs(os.path.join(root, ".90north-develop"))
        for name in ("dev-ledger.md", "defect-ledger.md"):
            with open(os.path.join(root, ".90north-develop", name), "w"):
                pass
        self.found(root, env)
        self.assertEqual(where(root, env).stdout.splitlines()[1], "DL=" + dl)

    def test_empty_leftovers_under_claude_do_not_hide_a_moved_board(self):
        root, state, env = moved_project()
        old = os.path.join(root, ".claude", "90north-develop")
        os.makedirs(os.path.join(old, "board"))
        with open(os.path.join(old, "dev-ledger.md"), "w"):
            pass
        self.found(root, env)
        self.assertEqual(where(root, env).stdout.splitlines(), ["DC=" + old, "DL=" + state])

    def test_only_empty_leftovers_anywhere_is_a_project_with_settings_only(self):
        """Nothing to keep in either place: the working state belongs beside the project."""
        root = os.path.realpath(tempfile.mkdtemp())
        old = os.path.join(root, ".claude", "90north-develop")
        os.makedirs(os.path.join(old, "runs"))
        os.makedirs(os.path.join(old, "board"))
        write_env(root, "TRACKER=local\n")
        r = where(root, moved_project()[2])
        self.assertEqual((r.returncode, r.stdout.splitlines()), (0, ["DC=" + old, "DL=" + os.path.join(root, ".90north-develop")]))


WHERE = os.path.join(SCRIPTS, "where.sh")


def where(root, env, *args):
    return subprocess.run([WHERE] + list(args), cwd=root, env=env, capture_output=True, text=True)


class Where(unittest.TestCase):
    """where.sh is how a loop learns the two folders: it never builds the paths by hand."""

    def test_a_moved_project(self):
        root, state, env = moved_project()
        r = where(root, env)
        self.assertEqual((r.returncode, r.stderr), (0, ""))
        self.assertEqual(r.stdout, "DC=%s\nDL=%s\n" % (os.path.join(root, ".claude", "90north-develop"), state))

    def test_a_project_not_moved_yet_names_one_folder_twice_and_says_how_to_move(self):
        root, dl, env = local_project("TRACKER=local\n")
        r = where(root, env)
        lines = r.stdout.splitlines()
        self.assertEqual((r.returncode, lines[:2]), (0, ["DC=" + dl, "DL=" + dl]))
        self.assertIn("move-state.sh", lines[2])
        self.assertTrue(lines[2].startswith("NOTE="))

    def test_a_project_with_settings_only_points_at_the_new_folder(self):
        root = os.path.realpath(tempfile.mkdtemp())
        os.makedirs(os.path.join(root, ".claude", "90north-develop"))
        write_env(root, "TRACKER=local\n")
        env = moved_project()[2]
        r = where(root, env)
        self.assertEqual((r.returncode, r.stdout.splitlines()),
                         (0, ["DC=" + os.path.join(root, ".claude", "90north-develop"), "DL=" + os.path.join(root, ".90north-develop")]))

    def test_from_a_subfolder_and_with_no_setup(self):
        root, state, env = moved_project()
        os.makedirs(os.path.join(root, "src", "deep"))
        self.assertIn("DL=" + state, where(os.path.join(root, "src", "deep"), env).stdout)
        r = where(tempfile.mkdtemp(), env)
        self.assertEqual(r.returncode, 2)
        self.assertIn("develop-init", r.stderr)


class WhereUnattended(unittest.TestCase):
    """`where.sh --auto` is the door of an unattended pass. Under .claude/ such a session can write some files and
    not others, and cannot remove its own pass lock, so the pass is refused before it starts."""

    def test_a_project_not_moved_yet_is_refused_with_exit_3(self):
        root, dl, env = local_project("TRACKER=local\n")
        r = where(root, env, "--auto")
        self.assertEqual(r.returncode, 3, r.stderr)
        said = [line for line in r.stderr.splitlines() if line.strip()]
        self.assertEqual(len(said), 1, r.stderr)
        self.assertIn(os.path.join(SCRIPTS, "move-state.sh"), said[0])
        self.assertIn("unattended", said[0])
        self.assertEqual(r.stdout.splitlines()[:2], ["DC=" + dl, "DL=" + dl])

    def test_a_moved_project_answers_as_usual(self):
        root, _, env = moved_project()
        plain, auto = where(root, env), where(root, env, "--auto")
        self.assertEqual((auto.returncode, auto.stderr, auto.stdout), (0, "", plain.stdout))

    def test_a_project_with_settings_only_is_not_set_up_for_a_pass(self):
        """Nothing is under .claude/ to refuse, but there is no working state folder either: develop-init writes it."""
        root = os.path.realpath(tempfile.mkdtemp())
        os.makedirs(os.path.join(root, ".claude", "90north-develop"))
        write_env(root, "TRACKER=local\n")
        r = where(root, moved_project()[2], "--auto")
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn("/90north-develop:develop-init", r.stderr)

    def test_a_legacy_folder_is_refused_and_points_at_develop_init(self):
        """.claude/defect-loop/ is under .claude/ too, and move-state.sh does not take it: develop-init does."""
        root, dl, env = local_project("TRACKER=local\n", folder="defect-loop")
        r = where(root, env, "--auto")
        self.assertEqual(r.returncode, 3, r.stderr)
        self.assertEqual(r.stdout.splitlines()[:2], ["DC=" + dl, "DL=" + dl])
        refusal = [line for line in r.stderr.splitlines() if line.startswith("where:")]
        self.assertEqual(len(refusal), 1, r.stderr)
        self.assertIn("unattended", refusal[0])
        self.assertIn("/90north-develop:develop-init", refusal[0])
        self.assertNotIn("move-state.sh", refusal[0])

    def test_a_legacy_folder_asked_plainly_gets_the_note(self):
        root, dl, env = local_project("TRACKER=local\n", folder="defect-loop")
        r = where(root, env)
        lines = r.stdout.splitlines()
        self.assertEqual((r.returncode, lines[:2]), (0, ["DC=" + dl, "DL=" + dl]))
        self.assertTrue(lines[2].startswith("NOTE="), lines)
        self.assertIn("/90north-develop:develop-init", lines[2])

    def test_a_working_state_named_under_claude_is_refused(self):
        """DEVELOP_STATE_DIR can name any folder; one under .claude/ has the same problem as the old layout."""
        root, _, env = moved_project()
        named = os.path.join(root, ".claude", "state")
        os.makedirs(named)
        r = where(root, dict(env, DEVELOP_STATE_DIR=named), "--auto")
        self.assertEqual((r.returncode, r.stdout.splitlines()[1]), (3, "DL=" + named), r.stderr)

    def test_any_other_argument_is_a_usage_error(self):
        root, _, env = moved_project()
        for args in (["--unattended"], ["--auto", "more"]):
            r = where(root, env, *args)
            self.assertEqual((r.returncode, r.stdout), (2, ""), args)
            self.assertIn("usage:", r.stderr)


if __name__ == "__main__":
    unittest.main()
