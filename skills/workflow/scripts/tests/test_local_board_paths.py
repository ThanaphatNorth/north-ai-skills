"""Path safety of the local board: no key, attachment name, link or ::video path reads or writes outside the board.

  python3 -m unittest discover -s skills/workflow/scripts/tests -p 'test_*.py'
"""
import os
import shutil
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test_local_board_failures import BoardCase  # noqa: E402
from test_tracker import card, local_project, read, run  # noqa: E402

LEAVES = "is a link that leaves the board folder"


class PathCase(BoardCase):
    """Adds a folder outside the board holding a card-shaped file and a secret."""

    def setUp(self):
        super().setUp()
        self.outside = os.path.join(self.root, "outside")
        os.makedirs(self.outside)
        self.secret = self.file(os.path.join("outside", "secret.txt"), "secret")
        self.foreign = self.file(os.path.join("outside", "foreign.md"), card("foreign"))
        self.out = os.path.join(self.root, "out")

    def in_board(self, *parts):
        return os.path.join(self.board, *parts)


class Keys(PathCase):
    def test_a_key_that_holds_a_path_is_refused_by_every_verb(self):
        md, clip = self.file("c.md", "x\n"), self.file("clip.mp4", b"12")
        for bad in ("../TASK-1", "/etc/passwd", "TASK-1/../TASK-2", "TASK-1\n"):
            for args in (["get", bad], ["card", bad], ["edit", bad, "--add-label", "x"], ["transition", bad, "todo"],
                         ["comment", bad, md], ["attach", bad, clip], ["download", bad, self.out]):
                self.refused(self.t(*args), "is not a card key like TASK-12", code=2)
        self.assertFalse(os.path.exists(self.out))
        self.assertEqual(sorted(os.listdir(self.board)), ["TASK-1.md", "TASK-2.md"])


class LinkedCards(PathCase):
    def test_a_card_that_links_out_of_the_board_is_never_read(self):
        os.symlink(self.foreign, self.in_board("TASK-7.md"))
        md = self.file("c.md", "x\n")
        for args in (["get", "TASK-7"], ["card", "TASK-7"], ["edit", "TASK-7", "--add-label", "x"],
                     ["transition", "TASK-7", "review"], ["comment", "TASK-7", md], ["download", "TASK-7", self.out]):
            r = self.t(*args)
            self.refused(r, "TASK-7.md " + LEAVES)
            self.assertNotIn("foreign", r.stdout)
        self.assertEqual(read(self.foreign), card("foreign"))
        self.assertTrue(os.path.islink(self.in_board("TASK-7.md")))

    def test_search_skips_a_card_that_links_out_of_the_board(self):
        os.symlink(self.foreign, self.in_board("TASK-7.md"))
        r = self.t("search", "status=todo")
        self.assertEqual([line.split(" | ")[0] for line in r.stdout.splitlines()], ["TASK-2", "TASK-1"])
        self.assertIn("WARN TASK-7.md skipped", r.stderr)

    def test_a_link_between_two_cards_of_the_board_still_reads(self):
        os.symlink("TASK-1.md", self.in_board("TASK-8.md"))
        self.assertEqual(self.t("card", "TASK-8").stdout.splitlines()[0], "TASK-8  [bug / todo]")

    def test_a_board_folder_that_is_itself_a_link_works(self):
        root, dl, env = local_project({}, env_lines="TRACKER=local\nLOCAL_BOARD=linked\n")
        self.addCleanup(shutil.rmtree, root, True)
        os.symlink(self.board, os.path.join(dl, "linked"))
        self.assertEqual(run(["edit", "TASK-1", "--add-label", "via-link"], root, env).returncode, 0)
        self.assertIn("labels: ai-queue, via-link\n", read(self.card_path("TASK-1")))


class LinkedAttachments(PathCase):
    def test_an_attachment_folder_that_links_out_is_not_listed_written_or_copied(self):
        os.symlink(self.outside, self.in_board("TASK-1"))
        for args in (["get", "TASK-1"], ["attach", "TASK-1", self.file("clip.mp4", b"12")],
                     ["download", "TASK-1", self.out]):
            r = self.t(*args)
            self.refused(r, "TASK-1 " + LEAVES)
            self.assertNotIn("secret.txt", r.stdout)
        self.assertEqual(sorted(os.listdir(self.outside)), ["foreign.md", "secret.txt"])
        self.assertFalse(os.path.exists(self.out))

    def test_attach_does_not_write_through_a_dangling_link(self):
        os.makedirs(self.in_board("TASK-1"))
        victim = os.path.join(self.outside, "victim.mp4")
        os.symlink(victim, self.in_board("TASK-1", "clip.mp4"))
        self.refused(self.t("attach", "TASK-1", self.file("clip.mp4", b"12")), "TASK-1/clip.mp4 exists")
        self.assertFalse(os.path.exists(victim))

    def test_download_does_not_copy_a_link_to_a_file_outside(self):
        os.makedirs(self.in_board("TASK-1"))
        os.symlink(self.secret, self.in_board("TASK-1", "leak.txt"))
        for names in ([], ["leak.txt"]):
            self.refused(self.t("download", "TASK-1", self.out, *names), "no attachment file TASK-1/leak.txt")
        self.assertFalse(os.path.exists(self.out))

    def test_download_names_cannot_climb_out_of_the_attachment_folder(self):
        os.makedirs(self.in_board("TASK-1"))
        self.file(os.path.join(".claude", "90north-develop", "board", "TASK-1", "a.txt"), "a")
        for name in ("../TASK-2.md", "../../tracker.env", self.secret):
            self.refused(self.t("download", "TASK-1", self.out, name), "no attachment file TASK-1/")
        self.assertFalse(os.path.exists(self.out))

    def test_attach_keeps_only_the_file_name_of_the_source(self):
        clip = self.file(os.path.join("outside", "clip.mp4"), b"12")
        r = self.t("attach", "TASK-1", os.path.join(self.outside, "..", "outside", "clip.mp4"))
        self.assertEqual(r.stdout.strip(), "attached clip.mp4 → TASK-1/clip.mp4 2 bytes")
        self.assertEqual(os.listdir(self.in_board("TASK-1")), ["clip.mp4"])
        self.assertTrue(os.path.exists(clip))


class VideoPaths(PathCase):
    def comment(self, path):
        return self.t("comment", "TASK-1", self.file("c.md", "proof\n::video %s\n" % path))

    def test_a_video_that_resolves_outside_the_board_is_refused(self):
        os.makedirs(self.in_board("TASK-1"))
        os.symlink(self.secret, self.in_board("TASK-1", "leak.mp4"))
        os.symlink(self.outside, self.in_board("TASK-1", "dir"))
        before = read(self.card_path("TASK-1"))
        for path in (self.secret, "../tracker.env", "TASK-1/../../tracker.env", "TASK-1/leak.mp4",
                     "TASK-1/dir/secret.txt", "."):
            self.refused(self.comment(path), "outside the board: " + path)
        self.assertEqual(read(self.card_path("TASK-1")), before)

    def test_a_video_anywhere_inside_the_board_is_accepted(self):
        os.makedirs(self.in_board("TASK-2"))
        self.file(os.path.join(".claude", "90north-develop", "board", "TASK-2", "clip.mp4"), b"12")
        os.symlink(os.path.join("TASK-2", "clip.mp4"), self.in_board("alias.mp4"))
        for n, path in enumerate(("TASK-2/clip.mp4", "alias.mp4"), 1):
            r = self.comment(path)
            self.assertEqual((r.returncode, r.stdout.strip()),
                             (0, "comment c%d on TASK-1 · videos 1 · missing none" % n), r.stderr)


if __name__ == "__main__":
    unittest.main()
