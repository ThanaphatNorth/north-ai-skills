"""End to end: input sizes that used to take quadratic time or exhaust the stack finish, with a result."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from failure_case import FailureCase  # noqa: E402

LIMIT = 60   # seconds, for a loaded machine; each of these took minutes before, under a second now


class LongInput(FailureCase):
    def test_minified_object_on_one_line_finishes(self):
        """600 KB of `key:value,` pairs: the arrow-function pattern rescanned the line from every key."""
        self.write("src/data.js", "var d={" + ",".join("k%d:%d" % (i, i) for i in range(50000)) + "};\n")
        code, out, err = self.cli("--json", timeout=LIMIT)
        self.assertEqual((code, err), (0, ""))   # one unbreakable token: not a long-line finding either
        self.assertIn('"findings": []', out)

    def test_function_after_a_minified_line_is_still_measured(self):
        body = "".join("  const v%d = load(%d);\n" % (i, i) for i in range(60))
        self.write("src/report.ts", "var d={" + ",".join("k%d:%d" % (i, i) for i in range(50000)) + "};\n"
                   "export function build() {\n" + body + "}\n")
        code, out, _ = self.cli("--json", "--max-line", "0", timeout=LIMIT)
        self.assertEqual(code, 1)
        self.assertIn("function build is 62 lines", out)

    def test_manifest_with_a_long_run_of_blank_lines_finishes(self):
        """The per-line patterns let leading whitespace run across lines, and rescanned the run from each one."""
        for name, rows, dependency in (
                ("Gemfile", "source 'https://rubygems.org'\ngem 'rails'\n", "rails"),
                ("build.gradle", "dependencies {\n    implementation 'com.acme:lib:1.0'\n}\n", "com.acme:lib")):
            with self.subTest(manifest=name):
                self.write(name, "\n" * 400000 + rows)
                code, out, err = self.cli("--json", timeout=LIMIT)
                self.assertEqual((code, err), (1, ""))
                self.assertIn("adds %s;" % dependency, out)
                os.remove(os.path.join(self.repo, name))

    def test_manifest_nested_past_the_json_decoder_limit_is_skipped(self):
        self.write("package.json", "[" * 200000)
        code, out, err = self.cli("--json", timeout=LIMIT)
        self.assertEqual((code, err), (0, ""))
        self.assertIn('"findings": []', out)


if __name__ == "__main__":
    unittest.main()
