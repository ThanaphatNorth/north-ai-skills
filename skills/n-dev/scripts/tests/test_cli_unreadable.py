"""End to end: a path the check cannot read is skipped with a note, not a crash."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from repo_case import RepoCase  # noqa: E402


class UnreadableUntrackedPath(RepoCase):
    """A symlink that points at itself cannot be opened by any user, root included."""

    def setUp(self):
        super().setUp()
        os.makedirs(os.path.join(self.repo, "cache"))
        os.symlink("credentials", os.path.join(self.repo, "cache", "credentials"))

    def test_unreadable_untracked_path_is_skipped_with_a_note(self):
        code, data, err = self.check("--base", "main")
        self.assertIsNotNone(data, "the check crashed: " + err[-300:])
        self.assertEqual((code, data["findings"]), (0, []))
        self.assertIn("skipped unreadable path cache/credentials", err)


if __name__ == "__main__":
    unittest.main()
