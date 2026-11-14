"""gitdiff against a real repository: what a file's text at the base ref is."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from failure_case import FailureCase  # noqa: E402
from ndev_check import gitdiff  # noqa: E402

NL, CR, FF = "\n", "\r", "\x0c"
MARKER = "\\ No newline at end of file"


class TextAtBase(FailureCase):
    def test_text_of_a_tracked_file_and_none_for_a_missing_or_binary_one(self):
        self.write_bytes("src/blob.py", b"x = 1\n\x00\x01")
        self.write_bytes("src/latin.py", b"# caf\xe9\n")
        self.write('src/we"ird name.py', "y = 2\n")
        self.git("add", "-A")
        self.git("commit", "-qm", "more")
        self.write("src/app.py", "rewritten after the commit\n")
        self.assertEqual(gitdiff.text_at(self.repo, "HEAD", 'src/we"ird name.py'), "y = 2\n")
        self.assertTrue(gitdiff.text_at(self.repo, "HEAD", "src/app.py").startswith("from routes import ROUTES\n"))
        self.assertEqual(gitdiff.text_at(self.repo, "HEAD", "src/latin.py"), "# caf\ufffd\n")
        self.assertIsNone(gitdiff.text_at(self.repo, "HEAD", "src/blob.py"))
        self.assertIsNone(gitdiff.text_at(self.repo, "HEAD", "src/never.py"))
        self.assertIsNone(gitdiff.text_at(self.repo, "main", 'src/we"ird name.py'))
        self.assertIsNone(gitdiff.text_at(self.repo, gitdiff.EMPTY_TREE, "src/app.py"))

    def test_repo_root_from_a_subdirectory_and_tracked_files_as_stored(self):
        self.commit_file("docs/a b/ราคา.md", "x\n")
        inside = os.path.join(self.repo, "docs", "a b")
        self.assertEqual(os.path.realpath(gitdiff.repo_root(inside)), os.path.realpath(self.repo))
        self.assertEqual(gitdiff.tracked_files(self.repo), ["docs/a b/ราคา.md", "src/app.py", "src/pricing.py"])
        with self.assertRaises(gitdiff.GitError) as ctx:
            gitdiff.repo_root(os.path.join(self.repo, "src", "app.py"))
        self.assertIn("is not a directory", str(ctx.exception))


PATCH = """diff --git a/q.sql b/q.sql
index 1111111..2222222 100644
--- a/q.sql
+++ b/q.sql
@@ -2,3 +1,0 @@ select 1
--- drop the audit rows
-- a list item
-assert total == 3
@@ -9 +7,2 @@
---strict
+++verbose
+@@ -40 +40,50 @@ text that only looks like a hunk header
"""


class PatchParsing(unittest.TestCase):
    """The hunk headers say which rows are content; a row is never judged by how its own text starts."""

    def test_removed_lines_that_start_with_dashes_are_kept_and_the_file_header_is_not_one(self):
        self.assertEqual(gitdiff._removed_lines(PATCH), [(2, "-- drop the audit rows"), (3, "- a list item"),
                                                         (4, "assert total == 3"), (9, "--strict")])

    def test_added_line_that_looks_like_a_header_adds_no_lines_of_its_own(self):
        self.assertEqual(gitdiff._added_lines(PATCH), [7, 8])
        form_feed = "@@ -1 +1 @@" + NL + "-old" + NL + "+page" + FF + "@@ -1 +5,50 @@ still the same added line" + NL
        self.assertEqual((gitdiff._added_lines(form_feed), gitdiff._removed_lines(form_feed)), ([1], [(1, "old")]))

    def test_missing_final_newline_marker_is_not_content(self):
        patch = NL.join(["--- a/x", "+++ b/x", "@@ -3 +3,2 @@", "-old end", MARKER, "+new", "+new end", MARKER,
                         "@@ -8 +9 @@", "-a" + CR, "+b" + CR, ""])
        self.assertEqual(gitdiff._removed_lines(patch), [(3, "old end"), (8, "a")])
        self.assertEqual(gitdiff._added_lines(patch), [3, 4, 9])


class RemovedDashLines(FailureCase):
    def test_snapshot_that_only_lost_a_line_starting_with_dashes_is_reported(self):
        """Seen from the diff alone, `--- note` was a file header and the snapshot looked untouched."""
        self.commit_file("tests/__snapshots__/report.approved.sql", "select 1\n-- audit rows stay\nfrom t\n")
        self.write("tests/__snapshots__/report.approved.sql", "select 1\nfrom t\n")
        code, data, _ = self.check("--base", "HEAD")
        self.assertEqual((code, self.kinds(data)), (1, [("test-weakened", "tests/__snapshots__/report.approved.sql")]))

    def test_lowered_gate_on_a_line_starting_with_dashes_is_reported(self):
        self.commit_file("pytest.ini", "[pytest]\naddopts =\n--cov-fail-under=90\n")
        self.write("pytest.ini", "[pytest]\naddopts =\n--cov-fail-under=50\n")
        code, data, _ = self.check("--base", "HEAD")
        self.assertEqual(code, 1)
        self.assertIn("cov-fail-under 90 -> 50", data["findings"][0]["message"])


class LargeBinaryInTheWorktree(FailureCase):
    def reads(self):
        """Sizes of the reads made through fileio while the block runs (git's pipes are read there too)."""
        from test_fileio import counted_reads
        return counted_reads()

    def test_untracked_binary_is_judged_by_its_first_8_kb_and_never_loaded(self):
        self.write_bytes("media/dump.sqlite", b"SQLite format 3\x00" + b"\x07" * (4 << 20))
        with self.reads() as sizes:
            self.assertIsNone(gitdiff.read_text(self.repo, "media/dump.sqlite"))
        self.assertEqual(sum(sizes), 8192)
        with self.reads() as sizes:
            changed = gitdiff.changed_files(self.repo, "HEAD")
        self.assertEqual([f.path for f in changed], [])
        self.assertLess(sum(sizes), 64 * 1024)

    def test_text_file_with_a_nul_only_past_the_first_8_kb_is_still_text(self):
        data = b"x = 1\n" * 2000 + b"\x00\n"
        self.write_bytes("src/long.py", data)
        with self.reads() as sizes:
            self.assertEqual(gitdiff.read_text(self.repo, "src/long.py"), data.decode())
        self.assertEqual(sum(sizes), len(data))


if __name__ == "__main__":
    unittest.main()
