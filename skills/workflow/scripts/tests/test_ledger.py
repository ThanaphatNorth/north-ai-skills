"""Tests for ledger.sh: the one way a loop writes a ledger row.

The ledgers live in .90north-develop/ beside the project (in .claude/90north-develop/ for a project that has not
moved its state yet). The script is the door: it checks the row, stamps it and appends it to the ledger of the main
checkout.

  python3 -m unittest discover -s skills/workflow/scripts/tests -p 'test_*.py'
"""
import os
import re
import shutil
import subprocess
import tempfile
import unittest

SCRIPTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
LEDGER = os.path.join(SCRIPTS, "ledger.sh")
HEAD = ("# dev ledger\n\n| date time | KEY | state | branch @ sha | worktree · ports · DB | evidence | next |\n"
        "|--|--|--|--|--|--|--|\n")
ROW = ["dev", "TASK-1", "awaiting-push", "feat/TASK-1-x @ 347ff39", "../pricing-task-1 · no ports · no DB",
       "test output in comment", "push yes, then PR"]
ENV = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t",
           GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_NOSYSTEM="1")
ENV.pop("DEVELOP_DIR", None)
ENV.pop("DEVELOP_STATE_DIR", None)
ENV.pop("DEFECT_LOOP_DIR", None)


class LedgerCase(unittest.TestCase):
    def setUp(self):
        self.root = os.path.realpath(tempfile.mkdtemp(prefix="ledger-"))
        self.settings = os.path.join(self.root, ".claude", "90north-develop")
        self.state = os.path.join(self.root, ".90north-develop")
        os.makedirs(self.settings)
        os.makedirs(self.state)
        with open(os.path.join(self.settings, "tracker.env"), "w", encoding="utf-8") as fh:
            fh.write("TRACKER=local\n")
        self.put("dev-ledger.md", HEAD)
        self.put("defect-ledger.md", HEAD.replace("dev ledger", "defect ledger"))

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def put(self, name, text):
        with open(os.path.join(self.state, name), "w", encoding="utf-8") as fh:
            fh.write(text)

    def read(self, name="dev-ledger.md"):
        with open(os.path.join(self.state, name), encoding="utf-8") as fh:
            return fh.read()

    def run_ledger(self, args, cwd=None):
        proc = subprocess.run([LEDGER] + list(args), cwd=cwd or self.root, env=ENV, capture_output=True, text=True)
        return proc.returncode, proc.stdout, proc.stderr


class Appends(LedgerCase):
    def test_one_stamped_row_with_seven_cells(self):
        code, out, err = self.run_ledger(ROW)
        self.assertEqual((code, err), (0, ""))
        self.assertEqual(out, "ledger: dev TASK-1 → awaiting-push\n")
        last = self.read().splitlines()[-1]
        self.assertRegex(last, r"^\| \d{4}-\d\d-\d\d \d\d:\d\d \| TASK-1 \| awaiting-push \| feat/TASK-1-x @ 347ff39 \| "
                               r"\.\./pricing-task-1 · no ports · no DB \| test output in comment \| push yes, then PR \|$")
        self.assertEqual(self.read()[:len(HEAD)], HEAD)  # what was there stays as it was

    def test_the_other_flow_has_its_own_file(self):
        self.assertEqual(self.run_ledger(["defect", "ABC-12", "ready-for-qa"] + ROW[3:])[0], 0)
        self.assertIn("| ABC-12 | ready-for-qa |", self.read("defect-ledger.md"))
        self.assertEqual(self.read(), HEAD)

    def test_a_file_that_does_not_end_in_a_newline_gets_one_first(self):
        self.put("dev-ledger.md", HEAD + "| 2026-11-13 10:00 | TASK-0 | in-review | b @ 1 | w | e | n |")
        self.assertEqual(self.run_ledger(ROW)[0], 0)
        lines = self.read().splitlines()
        self.assertTrue(lines[-2].startswith("| 2026-11-13 10:00 | TASK-0 |"))
        self.assertIn("| TASK-1 | awaiting-push |", lines[-1])

    def test_a_bar_inside_a_cell_is_escaped_so_the_row_keeps_its_columns(self):
        row = ROW[:5] + ["red | green output", "next"]
        self.assertEqual(self.run_ledger(row)[0], 0)
        last = self.read().splitlines()[-1]
        self.assertIn(r"red \| green output", last)
        self.assertEqual(len(re.findall(r"(?<!\\)\|", last)), 8)

    def test_an_untracked_item_and_an_empty_cell_are_fine(self):
        code, _, err = self.run_ledger(["dev", "LOCAL-add-coupon", "in-progress", "feat/LOCAL-add-coupon @ 1a2b3c4", "", "", "build"])
        self.assertEqual((code, err), (0, ""))
        self.assertIn("| LOCAL-add-coupon | in-progress | feat/LOCAL-add-coupon @ 1a2b3c4 |  |  | build |", self.read())

    def test_from_a_linked_worktree_the_row_lands_in_the_main_checkout(self):
        git = lambda *a, cwd=self.root: subprocess.run(["git", *a], cwd=cwd, env=ENV, check=True, capture_output=True)
        git("init", "-q", "-b", "main")
        git("add", "-A")
        git("commit", "-q", "-m", "base")
        tree = self.root + "-wt"
        self.addCleanup(shutil.rmtree, tree, True)
        git("worktree", "add", "-q", "-b", "feat/x", tree)
        code, _, err = self.run_ledger(ROW, cwd=tree)
        self.assertEqual((code, err), (0, ""))
        self.assertIn("| TASK-1 | awaiting-push |", self.read())
        with open(os.path.join(tree, ".90north-develop", "dev-ledger.md"), encoding="utf-8") as fh:
            self.assertEqual(fh.read(), HEAD)  # the worktree's own copy is not the ledger


class NotMovedYet(LedgerCase):
    """A project set up before the working state moved out of .claude/ keeps its ledgers where they are."""

    def setUp(self):
        super().setUp()
        for name in ("dev-ledger.md", "defect-ledger.md"):
            os.rename(os.path.join(self.state, name), os.path.join(self.settings, name))
        os.rmdir(self.state)

    def test_the_row_goes_to_the_ledger_under_claude_with_a_note_on_how_to_move(self):
        code, out, err = self.run_ledger(ROW)
        self.assertEqual((code, out), (0, "ledger: dev TASK-1 → awaiting-push\n"))
        self.assertIn("move-state.sh", err)
        with open(os.path.join(self.settings, "dev-ledger.md"), encoding="utf-8") as fh:
            self.assertIn("| TASK-1 | awaiting-push |", fh.read())
        self.assertFalse(os.path.exists(self.state))  # writing a row does not move anything


    def test_a_stray_new_folder_does_not_take_the_row_away_from_the_old_ledger(self):
        os.makedirs(os.path.join(self.state, "runs", "2026-11-14"))
        code, _, err = self.run_ledger(ROW)
        self.assertEqual(code, 0, err)
        with open(os.path.join(self.settings, "dev-ledger.md"), encoding="utf-8") as fh:
            self.assertIn("| TASK-1 | awaiting-push |", fh.read())


class LegacyFolder(LedgerCase):
    """The single-loop setup before 0.3: .claude/defect-loop/, whose ledger.md is the defect ledger."""

    def setUp(self):
        super().setUp()
        self.legacy = os.path.join(self.root, ".claude", "defect-loop")
        os.rename(self.settings, self.legacy)
        shutil.rmtree(self.state)
        with open(os.path.join(self.legacy, "ledger.md"), "w", encoding="utf-8") as fh:
            fh.write(HEAD)

    def test_a_defect_row_goes_to_its_ledger_md(self):
        code, out, _ = self.run_ledger(["defect", "ABC-12", "ready-for-qa"] + ROW[3:])
        self.assertEqual((code, out), (0, "ledger: defect ABC-12 → ready-for-qa\n"))
        with open(os.path.join(self.legacy, "ledger.md"), encoding="utf-8") as fh:
            self.assertIn("| ABC-12 | ready-for-qa |", fh.read())

    def test_a_dev_row_needs_develop_init_first(self):
        code, out, err = self.run_ledger(ROW)
        self.assertEqual((code, out), (2, ""))
        self.assertIn("develop-init", err)


class Refuses(LedgerCase):
    def refused(self, args, word, cwd=None):
        code, out, err = self.run_ledger(args, cwd)
        self.assertEqual((code, out), (2, ""), err)
        self.assertIn(word, err)
        self.assertEqual(self.read(), HEAD)
        self.assertEqual(self.read("defect-ledger.md"), HEAD.replace("dev ledger", "defect ledger"))

    def test_a_flow_it_does_not_know(self):
        self.refused(["develop"] + ROW[1:], "dev or defect")
        self.refused(["../dev"] + ROW[1:], "dev or defect")

    def test_a_key_that_is_not_a_key(self):
        for key in ("", "TASK 2", "../../etc", "TASK-2|x", "-TASK", "TASK_2"):
            self.refused(["dev", key] + ROW[2:], "KEY")

    def test_a_state_that_is_not_one_word(self):
        for state in ("", "Awaiting Push", "in|review", "ready for qa"):
            self.refused(["dev", "TASK-1", state] + ROW[3:], "state")

    def test_a_cell_with_a_line_break(self):
        self.refused(ROW[:6] + ["push yes\n| 2026 | FAKE-1 | done |"], "one line")
        self.refused(ROW[:3] + ["a\rb"] + ROW[4:], "one line")
        self.refused(["dev", "TASK-2\n| x"] + ROW[2:], "one line")  # a forged second row inside the key

    def test_too_few_or_too_many_cells(self):
        self.refused(ROW[:6], "usage")
        self.refused(ROW + ["extra"], "usage")

    def test_a_folder_that_was_never_set_up(self):
        bare = tempfile.mkdtemp(prefix="ledger-bare-")
        self.addCleanup(shutil.rmtree, bare, True)
        self.refused(ROW, "develop-init", cwd=bare)

    def test_a_missing_ledger_file(self):
        os.remove(os.path.join(self.state, "dev-ledger.md"))
        code, out, err = self.run_ledger(ROW)
        self.assertEqual((code, out), (2, ""))
        self.assertIn("develop-init", err)
        self.assertFalse(os.path.exists(os.path.join(self.state, "dev-ledger.md")))

    def test_a_ledger_that_is_a_link_to_somewhere_else(self):
        outside = os.path.join(self.root, "outside.md")
        with open(outside, "w", encoding="utf-8") as fh:
            fh.write("keep\n")
        os.remove(os.path.join(self.state, "dev-ledger.md"))
        os.symlink(outside, os.path.join(self.state, "dev-ledger.md"))
        code, out, err = self.run_ledger(ROW)
        self.assertEqual((code, out), (2, ""))
        self.assertIn("link", err)
        with open(outside, encoding="utf-8") as fh:
            self.assertEqual(fh.read(), "keep\n")


if __name__ == "__main__":
    unittest.main()
