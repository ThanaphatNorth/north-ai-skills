"""End to end: the user's git configuration and locale never change what the check sees."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from failure_case import FailureCase  # noqa: E402
from repo_case import ENV, lines  # noqa: E402


class UserGitConfig(FailureCase):
    def wiring(self, *args):
        code, data, _ = self.check(*args)
        return code, [f["value"] for f in data["findings"] if f["kind"] == "wiring"]

    def test_forced_colour_does_not_hide_the_added_lines(self):
        """`color.ui = always` colours piped diffs too; the hunk headers then no longer parsed."""
        self.git("config", "color.ui", "always")
        self.append("src/app.py", lines("extra", 25))
        self.assertEqual(self.wiring(), (1, [25]))

    def test_external_diff_tool_is_not_used(self):
        self.git("config", "diff.external", "true")
        self.append("src/app.py", lines("extra", 25))
        self.assertEqual(self.wiring(), (1, [25]))

    def test_textconv_filter_does_not_move_the_line_numbers(self):
        """A `diff=<driver>` attribute with a textconv rewrites what `git diff` compares; `sed G` doubles it."""
        self.git("config", "diff.spaced.textconv", "sed G")
        self.write(".gitattributes", "*.py diff=spaced\n")
        self.append("src/app.py", lines("extra", 25))
        self.assertEqual(self.wiring(), (1, [25]))

    def test_inter_hunk_context_does_not_count_unchanged_lines_as_added(self):
        """With `diff.interHunkContext`, two edits are merged into one hunk that spans the lines between."""
        self.git("config", "diff.interHunkContext", "50")
        self.write("src/app.py", "from routes import ROUTES\nFIRST = 1\n\n" + lines("base", 10) + "LAST = 2\n")
        self.assertEqual(self.wiring("--max-wiring", "1"), (1, [2]))

    def test_non_ascii_path_is_checked_under_an_ascii_locale(self):
        """git names files in UTF-8 whatever the locale; decoding its output with the locale lost the file.
        Every machine has the C locale, and it is ASCII once Python is told not to upgrade it to UTF-8
        (two PYTHON* switches, which `-I` would ignore)."""
        self.write("src/ราคา.py", lines("v", 320))
        env = dict(ENV, LC_ALL="C", LANG="C", PYTHONCOERCECLOCALE="0", PYTHONUTF8="0")
        code, out, err = self.cli("--json", env=env, interpreter=())
        self.assertEqual((code, err), (1, ""))
        self.assertIn('"kind": "file-size"', out)

if __name__ == "__main__":
    unittest.main()
