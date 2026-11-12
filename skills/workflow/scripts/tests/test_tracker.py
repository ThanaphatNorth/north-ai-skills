"""Tests for tracker.sh: the loops' one door to the tracker, its Jira pass-through and its local board backend.

  python3 -m unittest discover -s skills/workflow/scripts/tests -p 'test_*.py'
"""
import os
import shutil
import stat
import subprocess
import tempfile
import unittest

SCRIPTS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRACKER = os.path.join(SCRIPTS, "tracker.sh")


def card(title, status="todo", labels="ai-queue", rank="10", extra="", body="## Description\nx\n"):
    return ("---\ntitle: %s\ntype: bug\nstatus: %s\nlabels: %s\npriority: high\nrank: %s\n"
            "created: 2026-11-10 09:00\nupdated: 2026-11-12 09:00\nlinks:\n%s---\n\n%s\n## Comments\n"
            % (title, status, labels, rank, extra, body))


def local_project(cards, env_lines="TRACKER=local\n"):
    root = os.path.realpath(tempfile.mkdtemp())
    dl = os.path.join(root, ".claude", "90north-develop")
    os.makedirs(os.path.join(dl, "board"))
    with open(os.path.join(dl, "tracker.env"), "w") as fh:
        fh.write(env_lines)
    for key, text in cards.items():
        with open(os.path.join(dl, "board", key + ".md"), "w") as fh:
            fh.write(text)
    env = dict(os.environ)
    env.pop("DEVELOP_DIR", None)
    env.pop("DEFECT_LOOP_DIR", None)
    return root, dl, env


def run(args, cwd, env, script=TRACKER):
    return subprocess.run([script] + args, cwd=cwd, env=env, capture_output=True, text=True)


def read(path):
    with open(path) as fh:
        return fh.read()


class Door(unittest.TestCase):
    def test_unknown_verb_lists_the_verbs(self):
        root, _, env = local_project({})
        r = run(["delete", "TASK-1"], root, env)
        self.assertEqual(r.returncode, 2)
        self.assertIn("search get card edit transition comment attach download", r.stderr)

    def test_no_tracker_line_means_jira_with_the_same_arguments(self):
        tmp = tempfile.mkdtemp()
        for f in ("tracker.sh", "_state.sh"):
            shutil.copy(os.path.join(SCRIPTS, f), tmp)
        fake = os.path.join(tmp, "jira-get.sh")
        with open(fake, "w") as fh:
            fh.write('#!/bin/bash\necho "JIRA get $* in $DEVELOP_DIR"\n')
        os.chmod(fake, os.stat(fake).st_mode | stat.S_IXUSR)
        root, dl, env = local_project({}, env_lines="JIRA_SITE=https://x.test\nJIRA_ENV_FILE=/nope\n")
        r = run(["get", "ABC-1", "two words"], root, env, script=os.path.join(tmp, "tracker.sh"))
        self.assertEqual((r.returncode, r.stdout.strip()), (0, "JIRA get ABC-1 two words in %s" % dl))

    def test_tracker_comes_from_tracker_env_only(self):
        tmp = tempfile.mkdtemp()
        for f in ("tracker.sh", "_state.sh"):
            shutil.copy(os.path.join(SCRIPTS, f), tmp)
        fake = os.path.join(tmp, "jira-search.sh")
        with open(fake, "w") as fh:
            fh.write('#!/bin/bash\necho "JIRA search"\n')
        os.chmod(fake, os.stat(fake).st_mode | stat.S_IXUSR)
        root, _, env = local_project({}, env_lines="JIRA_SITE=https://x.test\nJIRA_ENV_FILE=/nope\n")
        env.update(TRACKER="local", LOCAL_BOARD="/elsewhere")
        r = run(["search", "x"], root, env, script=os.path.join(tmp, "tracker.sh"))
        self.assertEqual(r.stdout.strip(), "JIRA search", r.stderr)

    def test_unknown_backend_is_refused(self):
        root, _, env = local_project({}, env_lines="TRACKER=trello\n")
        r = run(["search", "status=todo"], root, env)
        self.assertEqual(r.returncode, 2)
        self.assertIn("TRACKER=trello", r.stderr)

    def test_a_jira_script_points_a_local_repo_to_the_door(self):
        root, _, env = local_project({})
        r = run(["TASK-1"], root, env, script=os.path.join(SCRIPTS, "jira-get.sh"))
        self.assertEqual(r.returncode, 2)
        self.assertIn("tracker.sh", r.stderr)

    def test_keys_that_are_not_card_keys_are_refused(self):
        root, _, env = local_project({"TASK-1": card("one")})
        for bad in ("../TASK-1", "TASK", "-x"):
            self.assertEqual(run(["get", bad], root, env).returncode, 2, bad)


class LocalVerbs(unittest.TestCase):
    def setUp(self):
        self.root, self.dl, self.env = local_project({
            "TASK-1": card("first", rank="20", extra="severity: Level 4\n",
                           body="## Description\nx\n\n## Acceptance criteria\n- a\n- b\n"),
            "TASK-2": card("second", rank="5", labels="ai-queue, ai-processing"),
            "TASK-3": card("third", status="review", rank="1"),
            "TASK-10": card("tenth", rank="5"),
        })
        self.board = os.path.join(self.dl, "board")
        os.makedirs(os.path.join(self.root, "src", "deep"))

    def t(self, *args):
        return run(list(args), os.path.join(self.root, "src", "deep"), self.env)

    def test_search_filters_orders_and_counts(self):
        r = self.t("search", "status=todo labels=ai-queue -labels=ai-processing")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual([line.split(" | ")[0] for line in r.stdout.splitlines()], ["TASK-10", "TASK-1"])
        self.assertIn("# 2 issue(s)", r.stderr)

    def test_get_prints_the_card_and_its_attachments(self):
        os.makedirs(os.path.join(self.board, "TASK-1"))
        open(os.path.join(self.board, "TASK-1", "shot.png"), "w").close()
        r = self.t("get", "TASK-1")
        self.assertIn("title: first", r.stdout)
        self.assertIn("ATTACHMENTS: TASK-1/shot.png", r.stdout)

    def test_card_prints_labels_links_and_named_fields(self):
        with open(os.path.join(self.board, "TASK-2.md"), "w") as fh:
            fh.write(card("second", extra="").replace("links:\n", "links: TASK-3, TASK-99\n"))
        r = self.t("card", "TASK-2", "severity,acceptance-criteria")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.splitlines()[:4], [
            "TASK-2  [bug / todo]", "LABELS: ai-queue", "LINK: TASK-3 [review] third", "LINK: TASK-99 [?] (no card)"])
        self.assertIn("FIELD severity: (empty)", r.stdout)
        self.assertEqual(self.t("card", "TASK-1", "severity,acceptance-criteria").stdout.splitlines()[-2:],
                         ["FIELD severity: Level 4", "FIELD acceptance-criteria: - a | - b"])

    def test_edit_dry_run_then_write_without_leftovers(self):
        before = read(os.path.join(self.board, "TASK-1.md"))
        md = os.path.join(self.root, "summary.md")
        with open(md, "w") as fh:
            fh.write("type: bug\nrisk: low\n")
        args = ["edit", "TASK-1", "--add-label", "ai-do-now", "--remove-label", "ai-queue",
                "--field", "severity=Level 3", "--field-md", "AI summary=" + md]
        dry = self.t(*(args + ["--dry-run"]))
        self.assertIn("labels: ai-do-now", dry.stdout)
        self.assertEqual(read(os.path.join(self.board, "TASK-1.md")), before)
        self.assertEqual(self.t(*args).returncode, 0)
        after = read(os.path.join(self.board, "TASK-1.md"))
        for want in ("labels: ai-do-now", "severity: Level 3", "## AI summary\ntype: bug\nrisk: low"):
            self.assertIn(want, after)
        self.assertEqual(sorted(os.listdir(self.board)), ["TASK-1.md", "TASK-10.md", "TASK-2.md", "TASK-3.md"])

    def test_transition_lists_and_moves_within_local_statuses(self):
        self.assertIn("todo  ← now", self.t("transition", "TASK-1", "--list").stdout)
        self.assertEqual(self.t("transition", "TASK-1", "in-progress").returncode, 0)
        self.assertIn("status: in-progress", read(os.path.join(self.board, "TASK-1.md")))
        bad = self.t("transition", "TASK-1", "shipped")
        self.assertEqual(bad.returncode, 1)
        self.assertIn("todo, in-progress, need-info, review, ready-for-qa, reopened, done", bad.stderr)

    def test_attach_comment_with_video_and_read_back(self):
        clip = os.path.join(self.root, "TASK-1-after.mp4")
        with open(clip, "wb") as fh:
            fh.write(b"\0" * 10)
        a = self.t("attach", "TASK-1", clip)
        self.assertIn("attached TASK-1-after.mp4 → TASK-1/TASK-1-after.mp4 10 bytes", a.stdout)
        self.assertEqual(self.t("attach", "TASK-1", clip).returncode, 1)
        md = os.path.join(self.root, "c.md")
        with open(md, "w") as fh:
            fh.write("**Generated by AI**\n::video TASK-1/TASK-1-after.mp4\n")
        r = self.t("comment", "TASK-1", md)
        self.assertEqual((r.returncode, r.stdout.strip()), (0, "comment c1 on TASK-1 · videos 1 · missing none"))
        with open(md, "w") as fh:
            fh.write("::video TASK-1/gone.mp4\n")
        r = self.t("comment", "TASK-1", md, "c1")
        self.assertEqual(r.returncode, 1)
        self.assertIn("missing TASK-1/gone.mp4", r.stdout + r.stderr)
        self.assertEqual(read(os.path.join(self.board, "TASK-1.md")).count("### c"), 1)

    def test_search_skips_an_unreadable_card_and_says_so(self):
        with open(os.path.join(self.board, "TASK-3.md"), "w") as fh:
            fh.write("no header here\n")
        r = self.t("search", "status=todo")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual([line.split(" | ")[0] for line in r.stdout.splitlines()], ["TASK-2", "TASK-10", "TASK-1"])
        self.assertIn("TASK-3.md", r.stderr)
        self.assertIn("skipped", r.stderr)
        self.assertEqual(self.t("get", "TASK-3").returncode, 1)

    def test_a_video_outside_the_board_fails_the_read_back(self):
        for path in ("/etc/hosts", "../tracker.env"):
            md = os.path.join(self.root, "c.md")
            with open(md, "w") as fh:
                fh.write("::video %s\n" % path)
            r = self.t("comment", "TASK-1", md)
            self.assertEqual(r.returncode, 1, path)
            self.assertIn("outside the board", r.stdout + r.stderr)

    def test_writes_keep_the_card_readable_by_others(self):
        path = os.path.join(self.board, "TASK-1.md")
        os.chmod(path, 0o644)
        self.assertEqual(self.t("edit", "TASK-1", "--add-label", "x").returncode, 0)
        self.assertEqual(stat.S_IMODE(os.stat(path).st_mode), 0o644)
        self.assertEqual(self.t("edit", "TASK-1", "--field", "title=a\nb").returncode, 1)
        self.assertIn("title: first", read(path))

    def test_download_into_a_new_folder_only(self):
        os.makedirs(os.path.join(self.board, "TASK-1"))
        with open(os.path.join(self.board, "TASK-1", "log.txt"), "w") as fh:
            fh.write("boom")
        out = os.path.join(self.root, "dl")
        self.assertEqual(self.t("download", "TASK-1", out).returncode, 0)
        self.assertEqual(read(os.path.join(out, "log.txt")), "boom")
        self.assertEqual(self.t("download", "TASK-1", out).returncode, 1)


class BoardLocation(unittest.TestCase):
    def test_a_relative_local_board_starts_at_the_state_folder(self):
        root, dl, env = local_project({}, env_lines="TRACKER=local\nLOCAL_BOARD=cards\n")
        os.makedirs(os.path.join(dl, "cards"))
        with open(os.path.join(dl, "cards", "TASK-5.md"), "w") as fh:
            fh.write(card("five"))
        r = run(["search", "status=todo"], root, env)
        self.assertEqual((r.returncode, r.stdout.split(" | ")[0]), (0, "TASK-5"), r.stderr)


class SharedBoard(unittest.TestCase):
    def test_a_worktree_reads_and_writes_the_main_checkouts_board(self):
        root, dl, env = local_project({"TASK-1": card("one")})
        env.update(GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@x", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@x")
        git = lambda *a: subprocess.run(["git", "-C", root] + list(a), env=env, capture_output=True, check=True)
        git("init", "-q", "-b", "main")
        git("add", "-A")
        git("commit", "-qm", "board")
        wt = os.path.join(root, "wt")
        git("worktree", "add", "-q", wt)
        main_card = os.path.join(dl, "board", "TASK-1.md")
        with open(main_card, "w") as fh:
            fh.write(card("one", status="review"))
        r = run(["search", "status=review"], wt, env)
        self.assertEqual((r.returncode, r.stdout.split(" | ")[0]), (0, "TASK-1"), r.stderr)
        self.assertEqual(run(["edit", "TASK-1", "--add-label", "seen"], wt, env).returncode, 0)
        self.assertIn("seen", read(main_card))
        self.assertNotIn("seen", read(os.path.join(wt, ".claude", "90north-develop", "board", "TASK-1.md")))


class Lifecycle(unittest.TestCase):
    def test_one_card_from_queue_to_review_lane(self):
        root, dl, env = local_project({"TASK-4": card("export button", labels="ai-queue")})
        t = lambda *a: run(list(a), root, env)
        q = "labels=ai-queue -labels=ai-processing status=todo"
        self.assertEqual(t("search", q).stdout.split(" | ")[0], "TASK-4")
        self.assertEqual(t("edit", "TASK-4", "--add-label", "ai-processing").returncode, 0)
        self.assertEqual(t("search", q).stdout, "")
        self.assertEqual(t("edit", "TASK-4", "--add-label", "ai-do-now").returncode, 0)
        for status in ("in-progress", "review"):
            self.assertEqual(t("transition", "TASK-4", status).returncode, 0)
        clip = os.path.join(root, "TASK-4-after.mp4")
        open(clip, "wb").close()
        self.assertEqual(t("attach", "TASK-4", clip).returncode, 0)
        md = os.path.join(root, "proof.md")
        with open(md, "w") as fh:
            fh.write("**Generated by AI**\n::video TASK-4/TASK-4-after.mp4\nspec green twice\n")
        self.assertEqual(t("comment", "TASK-4", md).returncode, 0)
        self.assertEqual(t("edit", "TASK-4", "--remove-label", "ai-processing", "--remove-label", "ai-queue").returncode, 0)
        final = t("card", "TASK-4").stdout.splitlines()
        self.assertEqual(final[:2], ["TASK-4  [bug / review]", "LABELS: ai-do-now"])
        self.assertIn("[video: TASK-4-after.mp4](TASK-4/TASK-4-after.mp4)", t("get", "TASK-4").stdout)


if __name__ == "__main__":
    unittest.main()
