"""Tests for _state.sh and where.sh: which place a project's working state is read from, and when the door refuses.

The two folders are absolute, physical paths however they were named. A ledger decides which place is in use, then
cards on the board; state in both places, or under .claude/ by any name or link, stops an unattended pass.

  python3 -m unittest discover -s skills/workflow/scripts/tests -p 'test_*.py'
"""
import os
import subprocess
import sys
import tempfile
import unittest

from fakejira import SCRIPTS
from test_state import CARD, door, local_project, moved_project, statuses, where, write_env


def put(path, text=""):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


def settings_only():
    """A project that has its settings and nothing else. Returns (root, settings folder, folder beside, env)."""
    root = os.path.realpath(tempfile.mkdtemp())
    old = os.path.join(root, ".claude", "90north-develop")
    os.makedirs(old)
    write_env(root, "TRACKER=local\n")
    return root, old, os.path.join(root, ".90north-develop"), moved_project()[2]


class ResolvedPaths(unittest.TestCase):
    """Both folders are printed absolute and physical, however they were named, so the door reads the path a pass
    would really write to: a relative name, a link or a trailing slash cannot take a pass under .claude/."""

    def refused(self, r, dl):
        self.assertEqual((r.returncode, r.stdout.splitlines()[1:2]), (3, ["DL=" + dl]), r.stdout + r.stderr)
        self.assertEqual(len([line for line in r.stderr.splitlines() if line.startswith("where:")]), 1, r.stderr)

    def test_a_relative_working_state_under_claude_is_refused(self):
        root, dl, env = local_project("TRACKER=local\n")
        self.refused(where(root, dict(env, DEVELOP_STATE_DIR=".claude/90north-develop"), "--auto"), dl)

    def test_a_link_into_claude_is_refused(self):
        root, _, env = moved_project()
        target = os.path.join(root, ".claude", "st")
        os.makedirs(target)
        os.symlink(target, os.path.join(root, "st"))
        self.refused(where(root, dict(env, DEVELOP_STATE_DIR=os.path.join(root, "st")), "--auto"), target)

    def test_the_claude_folder_itself_is_refused(self):
        root, _, env = moved_project()
        named = os.path.join(root, ".claude")
        self.refused(where(root, dict(env, DEVELOP_STATE_DIR=named), "--auto"), named)

    def test_a_folder_under_claude_that_does_not_exist_yet_is_refused(self):
        root, _, env = moved_project()
        named = os.path.join(root, ".claude", "later", "state")
        self.refused(where(root, dict(env, DEVELOP_STATE_DIR=named + "/"), "--auto"), named)

    def test_the_name_is_matched_in_any_letter_case(self):
        """On a disk that ignores case, .Claude is .claude."""
        root, _, env = moved_project()
        r = where(root, dict(env, DEVELOP_STATE_DIR=os.path.join(root, ".Claude", "state")), "--auto")
        self.assertEqual(r.returncode, 3, r.stdout + r.stderr)

    def test_a_relative_develop_dir_is_the_same_project(self):
        root, dl, env = local_project("TRACKER=local\n")
        r = where(root, dict(env, DEVELOP_DIR=".claude/90north-develop"), "--auto")
        self.assertEqual((r.returncode, r.stdout.splitlines()[:2]), (3, ["DC=" + dl, "DL=" + dl]), r.stderr)

    def test_a_trailing_slash_on_develop_dir_changes_nothing(self):
        root, state, env = moved_project()
        dc = os.path.join(root, ".claude", "90north-develop")
        r = where(root, dict(env, DEVELOP_DIR=dc + "/"))
        self.assertEqual((r.returncode, r.stdout, r.stderr), (0, "DC=%s\nDL=%s\n" % (dc, state), ""))

    def test_a_folder_beside_the_project_that_is_a_link_into_claude_is_refused(self):
        root, _, beside, env = settings_only()
        target = os.path.join(root, ".claude", "st")
        put(os.path.join(target, "dev-ledger.md"), "| 2026-11-10 09:00 | TASK-1 | in-review |\n")
        os.symlink(target, beside)
        self.refused(where(root, env, "--auto"), target)

    def test_a_working_state_outside_claude_may_start_also_through_a_link(self):
        root, state, env = moved_project()
        elsewhere = os.path.join(root, "kept-elsewhere")
        os.rename(state, elsewhere)
        os.symlink(elsewhere, os.path.join(root, "link"))
        r = where(root, dict(env, DEVELOP_STATE_DIR=os.path.join(root, "link")), "--auto")
        self.assertEqual((r.returncode, r.stdout.splitlines()[1], r.stderr), (0, "DL=" + elsewhere, ""))

    def test_a_project_that_itself_sits_under_a_claude_folder_is_told_so(self):
        """Refused like any path under .claude/, with the reason that applies and the way out that works."""
        root = os.path.join(os.path.realpath(tempfile.mkdtemp()), ".claude", "proj")
        os.makedirs(os.path.join(root, ".claude", "90north-develop"))
        write_env(root, "TRACKER=local\n")
        put(os.path.join(root, ".90north-develop", "dev-ledger.md"), LEDGER_ROW)
        r = where(root, moved_project()[2], "--auto")
        refusal = [line for line in r.stderr.splitlines() if line.startswith("where:")]
        self.assertEqual((r.returncode, len(refusal)), (3, 1), r.stdout + r.stderr)
        self.assertIn("the project itself", refusal[0])
        self.assertIn("DEVELOP_STATE_DIR", refusal[0])
        self.assertNotIn("link", refusal[0])

    def test_develop_dir_naming_a_folder_with_no_settings_is_exit_2(self):
        root, _, env = moved_project()
        r = where(root, dict(env, DEVELOP_DIR=os.path.join(root, "nope")), "--auto")
        self.assertEqual((r.returncode, r.stdout), (2, ""), r.stderr)
        self.assertEqual(len(r.stderr.splitlines()), 1, r.stderr)
        self.assertIn("DEVELOP_DIR", r.stderr)


LEDGER_ROW = "| 2026-11-10 09:00 | TASK-1 | in-review | fix/task-1 @ abc1234 | - | - | - |\n"


class WhichPlace(unittest.TestCase):
    """A ledger decides which place is in use; with no ledger anywhere, a board that holds cards does. A folder that
    only looks like state (a board holding a README or a keep file, one that cannot be listed) decides nothing."""

    def old_with_a_ledger(self):
        root, dl, env = local_project("TRACKER=local\n")
        put(os.path.join(dl, "dev-ledger.md"), LEDGER_ROW)
        return root, dl, env

    def stays_under_claude(self, root, dl, env):
        r = where(root, env)
        self.assertEqual(r.stdout.splitlines()[:2], ["DC=" + dl, "DL=" + dl], r.stderr)
        self.assertEqual(where(root, env, "--auto").returncode, 3)

    def test_a_board_beside_that_holds_only_a_keep_file(self):
        root, dl, env = self.old_with_a_ledger()
        put(os.path.join(root, ".90north-develop", "board", ".gitkeep"))
        self.stays_under_claude(root, dl, env)

    def test_a_board_beside_that_holds_only_a_readme(self):
        root, dl, env = self.old_with_a_ledger()
        put(os.path.join(root, ".90north-develop", "board", "README.md"), "# cards go here\n")
        self.stays_under_claude(root, dl, env)

    def test_a_board_beside_that_cannot_be_listed(self):
        self.assertFalse(hasattr(os, "geteuid") and os.geteuid() == 0,
                         "run this suite as a normal user: root lists a folder of mode 000")
        root, dl, env = self.old_with_a_ledger()
        board = os.path.join(root, ".90north-develop", "board")
        os.makedirs(board)
        self.addCleanup(os.chmod, board, 0o755)
        os.chmod(board, 0)
        self.stays_under_claude(root, dl, env)

    def test_with_no_ledger_a_board_without_cards_beside_does_not_hide_the_cards_under_claude(self):
        root, dl, env = local_project("TRACKER=local\n")
        put(os.path.join(root, ".90north-develop", "board", "README.md"), "# cards go here\n")
        self.stays_under_claude(root, dl, env)

    def test_a_ledger_under_claude_outranks_cards_beside(self):
        """What a move that stopped before the ledgers leaves: the pass must still be refused."""
        root, _, env = moved_project()
        dl = os.path.join(root, ".claude", "90north-develop")
        put(os.path.join(dl, "defect-ledger.md"), LEDGER_ROW)
        self.stays_under_claude(root, dl, env)

    def test_a_card_is_what_the_local_board_calls_a_card(self):
        """_state.sh and local_board_files.KEY name the same files as cards, so the two cannot drift apart."""
        sys.path.insert(0, SCRIPTS)
        import local_board_files
        for name in ("TASK-1.md", "abc_d-22.md", "a-0.md", "README.md", "notes.md", "TASK-1.txt", "TASK-x.md", "-1.md",
                     ".TASK-1.md", "1A-2.md", "TASK-1.md.bak", "TASK-1-2.md", "TASK 1-2.md"):
            root, old, beside, env = settings_only()
            put(os.path.join(old, "lessons.md"), "kept under .claude\n")
            put(os.path.join(beside, "board", name), CARD)
            is_card = name.endswith(".md") and local_board_files.KEY.match(name[:-3]) is not None
            self.assertEqual(where(root, env).stdout.splitlines()[1], "DL=" + (beside if is_card else old), name)


class TwoPlaces(unittest.TestCase):
    """A ledger (or, with no ledger, cards) in both places is a person's call: the new place is still the one read,
    the note names both, and an unattended pass does not start."""

    def in_two_places(self, root, state, env):
        old = os.path.join(root, ".claude", "90north-develop")
        plain = where(root, env)
        lines = plain.stdout.splitlines()
        self.assertEqual((plain.returncode, lines[:2], len(lines)), (0, ["DC=" + old, "DL=" + state], 3), plain.stderr)
        self.assertTrue(lines[2].startswith("NOTE="), lines)
        for part in ("two places", old, state, os.path.join(SCRIPTS, "move-state.sh") + " --dry-run"):
            self.assertIn(part, lines[2])
        auto = where(root, env, "--auto")
        refusal = [line for line in auto.stderr.splitlines() if line.strip()]
        self.assertEqual((auto.returncode, len(refusal)), (3, 1), auto.stderr)
        self.assertIn("unattended", refusal[0])
        self.assertIn("two places", refusal[0])

    def test_a_ledger_in_both_places(self):
        root, state, env = moved_project()
        put(os.path.join(state, "dev-ledger.md"), LEDGER_ROW)
        put(os.path.join(root, ".claude", "90north-develop", "dev-ledger.md"), LEDGER_ROW)
        self.in_two_places(root, state, env)

    def test_one_ledger_in_each_place(self):
        """What a move that stopped between the two ledgers leaves."""
        root, state, env = moved_project()
        put(os.path.join(state, "dev-ledger.md"), LEDGER_ROW)
        put(os.path.join(root, ".claude", "90north-develop", "defect-ledger.md"), LEDGER_ROW)
        self.in_two_places(root, state, env)

    def test_cards_in_both_places_and_no_ledger(self):
        root, state, env = moved_project()
        put(os.path.join(root, ".claude", "90north-develop", "board", "TASK-9.md"), CARD)
        self.in_two_places(root, state, env)
        self.assertEqual(statuses(root, env).stdout.splitlines()[0], "todo  ← now")  # the board beside is the one read

    def test_a_ledger_beside_and_cards_still_under_claude(self):
        """What a move that took the ledgers first and then stopped leaves: an empty board would be read."""
        root, old, beside, env = settings_only()
        put(os.path.join(beside, "dev-ledger.md"), LEDGER_ROW)
        os.makedirs(os.path.join(beside, "board"))
        put(os.path.join(old, "board", "TASK-9.md"), CARD)
        self.in_two_places(root, beside, env)

    def test_a_ledger_beside_and_lessons_or_knowledge_still_under_claude(self):
        for kept in ("lessons.md", os.path.join("knowledge", "code-map.md"), "ai-ledger.md"):
            root, old, beside, env = settings_only()
            put(os.path.join(beside, "defect-ledger.md"), LEDGER_ROW)
            put(os.path.join(old, kept), "what a loop learned here\n")
            self.in_two_places(root, beside, env)

    def test_cards_beside_and_lessons_still_under_claude(self):
        root, state, env = moved_project()
        put(os.path.join(root, ".claude", "90north-develop", "lessons.md"), "what a loop learned here\n")
        self.in_two_places(root, state, env)

    def test_records_kept_deep_in_the_knowledge_folder_count(self):
        root, state, env = moved_project()
        put(os.path.join(root, ".claude", "90north-develop", "knowledge", "proposals", "2026-11-14.md"), "a proposal\n")
        self.in_two_places(root, state, env)

    def test_records_behind_a_link_count(self):
        for linked in ("the folder", "one file"):
            root, state, env = moved_project()
            old = os.path.join(root, ".claude", "90north-develop")
            kept = os.path.join(root, "kept")
            put(os.path.join(kept, "code-map.md"), "where things are\n")
            if linked == "the folder":
                os.symlink(kept, os.path.join(old, "knowledge"))
            else:
                os.makedirs(os.path.join(old, "knowledge"))
                os.symlink(os.path.join(kept, "code-map.md"), os.path.join(old, "knowledge", "code-map.md"))
            self.in_two_places(root, state, env)

    def test_a_folder_that_cannot_be_looked_into_counts(self):
        """Nothing shows it is empty, so it is not treated as a leftover."""
        self.assertFalse(hasattr(os, "geteuid") and os.geteuid() == 0,
                         "run this suite as a normal user: root reads a folder whatever its mode")
        for locked, mode in (("knowledge", 0o444), (os.path.join("knowledge", "sub"), 0)):
            root, state, env = moved_project()
            old = os.path.join(root, ".claude", "90north-develop")
            put(os.path.join(old, locked, "code-map.md"), "where things are\n")
            self.addCleanup(os.chmod, os.path.join(old, locked), 0o755)
            os.chmod(os.path.join(old, locked), mode)
            self.in_two_places(root, state, env)

    def test_empty_folders_and_empty_files_under_claude_are_leftovers(self):
        """git never removes an empty folder it does not track, so a teammate's clone keeps one after the move."""
        for leftover in ("knowledge/proposals/", "knowledge/code-map.md", "knowledge/a/b/c/", "runs/2026-11-14/"):
            root, state, env = moved_project()
            old = os.path.join(root, ".claude", "90north-develop")
            put(os.path.join(state, "dev-ledger.md"), LEDGER_ROW)
            if leftover.endswith("/"):
                os.makedirs(os.path.join(old, leftover))
            else:
                put(os.path.join(old, leftover))
            r = where(root, env, "--auto")
            self.assertEqual((r.returncode, r.stdout, r.stderr), (0, "DC=%s\nDL=%s\n" % (old, state), ""), leftover)

    def test_folders_that_hold_only_empty_folders_do_not_keep_a_new_project_under_claude(self):
        root, old, beside, env = settings_only()
        os.makedirs(os.path.join(old, "runs", "2026-11-14"))
        os.makedirs(os.path.join(old, "knowledge", "proposals"))
        self.assertEqual(where(root, env).stdout, "DC=%s\nDL=%s\n" % (old, beside))

    def test_a_ledger_beside_and_only_leftovers_under_claude_is_one_place(self):
        root, state, env = moved_project()
        old = os.path.join(root, ".claude", "90north-develop")
        put(os.path.join(state, "dev-ledger.md"), LEDGER_ROW)
        put(os.path.join(old, "runs", "2026-11-14", "run.md"), "a pass on the old plugin wrote this\n")
        put(os.path.join(old, "board", "README.md"), "# cards went beside the project\n")
        r = where(root, env, "--auto")
        self.assertEqual((r.returncode, r.stdout, r.stderr), (0, "DC=%s\nDL=%s\n" % (old, state), ""))


class NotSetUp(unittest.TestCase):
    """An unattended pass needs the working state folder develop-init writes: ledger.sh only appends to a ledger
    that is there, so a pass that started without the folder would do work it cannot record."""

    def not_set_up(self, r, names):
        said = [line for line in r.stderr.splitlines() if line.strip()]
        self.assertEqual((r.returncode, len(said)), (2, 1), r.stdout + r.stderr)
        self.assertTrue(said[0].startswith("where:"), said)
        for part in ("unattended", "/90north-develop:develop-init", names):
            self.assertIn(part, said[0])

    def test_a_project_with_settings_only(self):
        root, _, beside, env = settings_only()
        self.not_set_up(where(root, env, "--auto"), beside)
        self.assertEqual(where(root, env).returncode, 0)  # asked plainly, the two folders are still printed

    def test_a_working_state_named_by_a_path_that_is_not_there(self):
        root, _, env = moved_project()
        named = os.path.join(root, "typo", ".90north-develop")
        self.not_set_up(where(root, dict(env, DEVELOP_STATE_DIR=named), "--auto"), named)

    def test_a_working_state_named_through_a_file(self):
        root, _, env = moved_project()
        put(os.path.join(root, "f"), "a file\n")
        named = os.path.join(root, "f", "sub")
        self.not_set_up(where(root, dict(env, DEVELOP_STATE_DIR=named), "--auto"), named)


class WorktreeSettings(unittest.TestCase):
    def test_a_linked_worktree_finds_settings_git_does_not_track(self):
        """tracker.env is not always committed: a worktree outside the main checkout then has no copy of it."""
        root, state, env = moved_project()
        env.update(GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@x", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@x",
                   GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_NOSYSTEM="1")
        put(os.path.join(root, ".gitignore"), ".claude/\n.90north-develop/\n")
        put(os.path.join(root, "src", "app.py"), "x = 1\n")
        git = lambda *a: subprocess.run(["git", "-C", root] + list(a), env=env, capture_output=True, check=True)
        git("init", "-q", "-b", "main")
        git("add", "-A")
        git("commit", "-qm", "base")
        tree = os.path.join(os.path.realpath(tempfile.mkdtemp()), "wt")
        git("worktree", "add", "-q", tree)
        self.assertFalse(os.path.exists(os.path.join(tree, ".claude")))
        for cwd in (tree, os.path.join(tree, "src")):
            r = door(["transition", "TASK-1", "--list"], cwd, env)
            self.assertEqual((r.returncode, r.stdout.splitlines()[:1], r.stderr), (0, ["todo  ← now"], ""), cwd)
        self.assertEqual(where(tree, env).stdout, "DC=%s\nDL=%s\n" % (os.path.join(root, ".claude", "90north-develop"), state))


if __name__ == "__main__":
    unittest.main()
