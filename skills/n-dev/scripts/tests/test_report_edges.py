"""The text report keeps one finding on one row, whatever the path or the quoted code contains."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from ndev_check.model import Budgets, Finding, printable  # noqa: E402
from ndev_check.report import as_json, as_text  # noqa: E402


class OneRowPerFinding(unittest.TestCase):
    def test_line_breaks_and_terminal_controls_are_escaped_and_tabs_and_other_scripts_kept(self):
        self.assertEqual(printable("a\nb\rc\x1b[2Jd\x7fe\u2028f\x85g\x00h"), "a\\nb\\rc\\x1b[2Jd\\x7fe\\u2028f\\x85g\\x00h")
        self.assertEqual(printable("expect(x)\t// ราคา 😀 \\n"), "expect(x)\t// ราคา 😀 \\n")

    def test_finding_and_existing_debt_rows_stay_on_one_line(self):
        new = Finding("test-weakened", "t/a\nb.test.ts", 3, 1, 0, "1 assertion line(s) removed (first: `x\x1b[0m`)")
        old = Finding("file-size", "src/x\rRESULT: clean.py", 1, 400, 300, "file had 350 lines at the base ref, 400 now")
        rows = as_text([new], "0123456789abcdef", Budgets(), [old]).split("\n")
        self.assertIn("  t/a\\nb.test.ts:3  1 assertion line(s) removed (first: `x\\x1b[0m`)", rows)
        self.assertIn("  src/x\\rRESULT: clean.py:1  file had 350 lines at the base ref, 400 now", rows)
        self.assertEqual(len([r for r in rows if r.startswith("RESULT:")]), 1)
        self.assertEqual(len("\n".join(rows).splitlines()), len(rows))

    def test_json_report_carries_the_path_unchanged(self):
        import json
        f = Finding("file-size", "src/a\nb.py", 1, 400, 300, "msg")
        self.assertEqual(json.loads(as_json([f], "abc", Budgets()))["findings"][0]["path"], "src/a\nb.py")


if __name__ == "__main__":
    unittest.main()
