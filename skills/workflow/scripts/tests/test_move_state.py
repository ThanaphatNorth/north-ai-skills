"""Tests for move-state.sh: a project set up before 0.12 moves its working state out of .claude/, once.

Settings (config.md, tracker.env) stay in .claude/90north-develop/. Ledgers, lessons, the board, knowledge and runs
move to .90north-develop/ beside the project. Nothing is copied, overwritten or deleted.

  python3 -m unittest discover -s skills/workflow/scripts/tests -p 'test_*.py'
"""
import os
import shutil
import subprocess
import tempfile
import unittest

SCRIPTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
MOVE = os.path.join(SCRIPTS, "move-state.sh")
TRACKER = os.path.join(SCRIPTS, "tracker.sh")
CARD = ("---\ntitle: one\ntype: bug\nstatus: todo\nlabels:\npriority: high\nrank: 1\n"
        "created: 2026-11-10 09:00\nupdated: 2026-11-10 09:00\nlinks:\n---\n\n## Description\nx\n\n## Comments\n")
ENV = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t",
           GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_NOSYSTEM="1")
for _name in ("DEVELOP_DIR", "DEVELOP_STATE_DIR", "DEFECT_LOOP_DIR"):
    ENV.pop(_name, None)
WORKING = ("dev-ledger.md", "defect-ledger.md", "lessons.md", "board/TASK-1.md", "knowledge/code-map.md",
           "runs/2026-11-13/run.md")
SETTINGS = ("config.md", "tracker.env")


class MoveCase(unittest.TestCase):
    """A project in the old layout: everything under .claude/90north-develop/."""

    def setUp(self):
        self.root = os.path.realpath(tempfile.mkdtemp(prefix="move-state-"))
        self.old = os.path.join(self.root, ".claude", "90north-develop")
        self.new = os.path.join(self.root, ".90north-develop")
        self.put("tracker.env", "TRACKER=local\n")
        self.put("config.md", "# config\n")
        self.put("board/TASK-1.md", CARD)
        for name in WORKING:
            if not name.startswith("board/"):
                self.put(name, name + "\n")

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def put(self, rel, text, base=None):
        path = os.path.join(base or self.old, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)

    def move(self, *args, cwd=None):
        proc = subprocess.run([MOVE] + list(args), cwd=cwd or self.root, env=ENV, capture_output=True, text=True)
        return proc.returncode, proc.stdout, proc.stderr

    def git(self, *args):
        return subprocess.run(["git", "-C", self.root] + list(args), env=ENV, capture_output=True, text=True, check=True).stdout

    def tree(self, base):
        found = []
        for folder, _, files in os.walk(base):
            found += [os.path.relpath(os.path.join(folder, name), base) for name in files]
        return sorted(found)

    def assert_nothing_moved(self):
        self.assertEqual(self.tree(self.old), sorted(WORKING + SETTINGS))


class Moves(MoveCase):
    def test_the_working_state_moves_and_the_settings_stay(self):
        code, out, err = self.move()
        self.assertEqual((code, err), (0, ""))
        self.assertEqual(self.tree(self.new), sorted(WORKING))
        self.assertEqual(self.tree(self.old), sorted(SETTINGS))
        for name in ("dev-ledger.md", "defect-ledger.md", "lessons.md", "board", "knowledge", "runs"):
            self.assertIn(name, out)
        self.assertIn("config.md and tracker.env stay", out)

    def test_a_file_keeps_its_text(self):
        self.move()
        with open(os.path.join(self.new, "board", "TASK-1.md"), encoding="utf-8") as fh:
            self.assertEqual(fh.read(), CARD)

    def test_the_tracker_reads_the_board_from_its_new_place(self):
        self.move()
        proc = subprocess.run([TRACKER, "search", "status=todo"], cwd=self.root, env=ENV, capture_output=True, text=True)
        self.assertEqual((proc.returncode, proc.stderr), (0, "# 1 issue(s)\n"))  # the count goes to stderr
        self.assertTrue(proc.stdout.startswith("TASK-1 | bug | todo"), proc.stdout)

    def test_files_git_tracks_are_moved_as_renames(self):
        self.git("init", "-q", "-b", "main")
        self.git("add", "--", ".claude/90north-develop/board", ".claude/90north-develop/config.md",
                 ".claude/90north-develop/tracker.env")
        self.git("commit", "-q", "-m", "board")
        self.assertEqual(self.move()[0], 0)
        status = self.git("status", "--porcelain")
        self.assertIn("R  .claude/90north-develop/board/TASK-1.md -> .90north-develop/board/TASK-1.md", status)
        self.assertNotIn("config.md", status)  # the settings did not move
        self.assertTrue(os.path.isfile(os.path.join(self.new, "dev-ledger.md")))  # an untracked ledger moved too

    def test_a_board_named_in_tracker_env_moves_too(self):
        self.put("tracker.env", "TRACKER=local\nLOCAL_BOARD=cards\n")
        os.rename(os.path.join(self.old, "board"), os.path.join(self.old, "cards"))
        self.assertEqual(self.move()[0], 0)
        self.assertTrue(os.path.isfile(os.path.join(self.new, "cards", "TASK-1.md")))
        proc = subprocess.run([TRACKER, "search", "status=todo"], cwd=self.root, env=ENV, capture_output=True, text=True)
        self.assertIn("TASK-1", proc.stdout)

    def test_a_board_in_a_nested_folder_moves_with_its_parent_made(self):
        self.put("tracker.env", "TRACKER=local\nLOCAL_BOARD=boards/team\n")
        os.makedirs(os.path.join(self.old, "boards"))
        os.rename(os.path.join(self.old, "board"), os.path.join(self.old, "boards", "team"))
        code, _, err = self.move()
        self.assertEqual((code, err), (0, ""))
        self.assertTrue(os.path.isfile(os.path.join(self.new, "boards", "team", "TASK-1.md")))
        self.assertTrue(os.path.isfile(os.path.join(self.new, "dev-ledger.md")))  # nothing was left half moved

    def test_a_board_kept_elsewhere_by_an_absolute_path_stays_and_the_rest_moves(self):
        elsewhere = os.path.join(self.root, "shared-board")
        os.rename(os.path.join(self.old, "board"), elsewhere)
        self.put("tracker.env", "TRACKER=local\nLOCAL_BOARD=%s\n" % elsewhere)
        code, out, err = self.move()
        self.assertEqual((code, err), (0, ""))
        self.assertTrue(os.path.isfile(os.path.join(elsewhere, "TASK-1.md")))
        self.assertTrue(os.path.isfile(os.path.join(self.new, "dev-ledger.md")))
        self.assertIn("the board stays at " + elsewhere, out)

    def test_a_second_run_has_nothing_to_move(self):
        self.move()
        code, out, err = self.move()
        self.assertEqual((code, err), (0, ""))
        self.assertIn("nothing to move", out)
        self.assertEqual(self.tree(self.new), sorted(WORKING))

    def test_gitignore_lines_that_name_the_old_place_are_pointed_out_not_edited(self):
        self.put(".gitignore", ".claude/90north-develop/runs/\nnode_modules/\n", base=self.root)
        code, out, _ = self.move()
        self.assertEqual(code, 0)
        self.assertIn(".gitignore", out)
        self.assertIn(".claude/90north-develop/runs/", out)
        with open(os.path.join(self.root, ".gitignore"), encoding="utf-8") as fh:
            self.assertEqual(fh.read(), ".claude/90north-develop/runs/\nnode_modules/\n")


class DryRun(MoveCase):
    def test_it_lists_what_would_move_and_changes_nothing(self):
        code, out, err = self.move("--dry-run")
        self.assertEqual((code, err), (0, ""))
        for name in ("dev-ledger.md", "lessons.md", "board", "knowledge", "runs"):
            self.assertIn("would move", out)
            self.assertIn(name, out)
        self.assert_nothing_moved()
        self.assertFalse(os.path.exists(self.new))


class Refuses(MoveCase):
    def test_a_name_that_already_exists_in_the_new_place(self):
        self.put("dev-ledger.md", "newer\n", base=self.new)
        code, out, err = self.move()
        self.assertEqual((code, out), (1, ""))
        self.assertIn("dev-ledger.md", err)
        self.assertIn("exists in both", err)
        self.assert_nothing_moved()
        with open(os.path.join(self.new, "dev-ledger.md"), encoding="utf-8") as fh:
            self.assertEqual(fh.read(), "newer\n")

    def test_a_pass_that_may_be_running(self):
        self.put("runs/.pass.lock", "2026-11-14T05:56:33Z\n")
        code, out, err = self.move()
        self.assertEqual((code, out), (1, ""))
        self.assertIn("pass lock", err)
        self.assertEqual(self.tree(self.old), sorted(WORKING + SETTINGS + ("runs/.pass.lock",)))

    def test_a_board_reached_by_a_path_that_climbs_out_of_the_folder(self):
        self.put("tracker.env", "TRACKER=local\nLOCAL_BOARD=../../shared-board\n")
        os.rename(os.path.join(self.old, "board"), os.path.join(self.root, "shared-board"))
        code, out, err = self.move()
        self.assertEqual((code, out), (1, ""))
        self.assertIn("LOCAL_BOARD", err)
        self.assertIn("absolute", err)
        self.assertTrue(os.path.isfile(os.path.join(self.old, "dev-ledger.md")))  # nothing moved: the path would change meaning
        self.assertFalse(os.path.exists(self.new))

    def test_an_argument_it_does_not_know(self):
        code, _, err = self.move("--force")
        self.assertEqual(code, 2)
        self.assertIn("usage", err)
        self.assert_nothing_moved()

    def test_the_legacy_single_loop_folder(self):
        os.rename(self.old, os.path.join(self.root, ".claude", "defect-loop"))
        code, _, err = self.move()
        self.assertEqual(code, 2)
        self.assertIn("develop-init", err)

    def test_a_folder_that_was_never_set_up(self):
        bare = tempfile.mkdtemp(prefix="move-bare-")
        self.addCleanup(shutil.rmtree, bare, True)
        code, _, err = self.move(cwd=bare)
        self.assertEqual(code, 2)
        self.assertIn("develop-init", err)


if __name__ == "__main__":
    unittest.main()
