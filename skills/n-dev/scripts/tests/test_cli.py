"""End to end: a throwaway git repository, the real CLI, its exit code and JSON."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from repo_case import RepoCase, lines  # noqa: E402


class StructureCheckCli(RepoCase):
    def test_small_wiring_diff_is_clean(self):
        self.append("src/app.py", "from coupons import register\nregister(ROUTES)\n")
        code, data, _ = self.check()
        self.assertEqual((code, data["findings"]), (0, []))

    def test_large_edit_to_pre_existing_file_is_flagged(self):
        self.append("src/app.py", lines("extra", 25))
        code, data, _ = self.check()
        self.assertEqual(code, 1)
        self.assertIn(("wiring", "src/app.py"), self.kinds(data))

    def test_tests_added_to_an_existing_test_file_are_not_a_wiring_breach(self):
        self.write("tests/test_app.py", "def test_a():\n    assert True\n")
        self.git("add", "-A")
        self.git("commit", "-qm", "test file")
        self.append("tests/test_app.py", "".join("def test_%d():\n    assert %d\n" % (i, i) for i in range(20)))
        code, data, _ = self.check("--base", "HEAD")
        self.assertEqual(data["findings"], [])

    def test_moving_code_out_of_a_file_is_not_a_wiring_breach(self):
        self.write("src/legacy.py", lines("old", 40))
        self.git("add", "-A")
        self.git("commit", "-qm", "legacy")
        self.write("src/legacy.py", "from legacy_parts import *\n")
        code, data, _ = self.check("--base", "HEAD")
        self.assertNotIn(("wiring", "src/legacy.py"), self.kinds(data))

    def test_committed_branch_changes_count_against_the_merge_base(self):
        self.append("src/app.py", lines("extra", 25))
        self.git("commit", "-qam", "feature work")
        code, data, _ = self.check()
        self.assertIn(("wiring", "src/app.py"), self.kinds(data))

    def test_new_untracked_file_over_budget(self):
        self.write("src/big.py", lines("v", 320))
        code, data, _ = self.check()
        self.assertIn(("file-size", "src/big.py"), self.kinds(data))

    def test_long_function_in_new_file(self):
        self.write("src/report.ts", "export function build() {\n" + "".join(
            "  const v%d = load(%d);\n" % (i, i) for i in range(60)) + "}\n")
        code, data, _ = self.check()
        self.assertIn(("function-size", "src/report.ts"), self.kinds(data))

    def test_test_files_are_exempt_from_function_budget(self):
        self.write("src/report.test.ts", "describe('x', () => {\n" + "".join(
            "  it('c%d', () => expect(f(%d)).toBe(%d));\n" % (i, i, i) for i in range(70)) + "});\n")
        code, data, _ = self.check()
        self.assertEqual(data["findings"], [])

    def test_copied_block_is_flagged_with_its_origin(self):
        src = open(os.path.join(self.repo, "src/pricing.py")).read()
        self.write("src/quote.py", src.replace("def price", "def quote"))
        code, data, _ = self.check()
        dup = [f for f in data["findings"] if f["kind"] == "duplicate"]
        self.assertEqual(len(dup), 1)
        self.assertEqual(dup[0]["path"], "src/quote.py")
        self.assertTrue(dup[0]["related"].startswith("src/pricing.py:"))

    def test_lockfiles_and_excluded_globs_are_ignored(self):
        self.write("package-lock.json", "{}\n" * 900)
        self.write("src/generated_client.py", lines("g", 400))
        code, data, _ = self.check("--exclude", "src/generated_*")
        self.assertEqual((code, data["findings"]), (0, []))

    def test_budgets_are_configurable(self):
        self.append("src/app.py", lines("extra", 25))
        code, data, _ = self.check("--max-wiring", "40")
        self.assertEqual(code, 0)

    def test_file_already_over_budget_is_listed_apart_and_does_not_fail(self):
        self.commit_file("src/legacy.py", lines("old", 320))
        self.append("src/legacy.py", lines("fix", 2))
        code, data, _ = self.check("--base", "HEAD")
        self.assertEqual((code, data["findings"]), (0, []))
        self.assertEqual(self.existing(data), [("file-size", "src/legacy.py")])

    def test_file_that_crosses_the_budget_in_this_change_is_a_finding(self):
        self.commit_file("src/grow.py", lines("old", 290))
        self.append("src/grow.py", lines("new", 15))
        code, data, _ = self.check("--base", "HEAD")
        self.assertEqual(code, 1)
        self.assertEqual(self.kinds(data), [("file-size", "src/grow.py")])
        self.assertEqual(data.get("existing"), [])

    def test_function_that_was_already_long_is_listed_apart(self):
        head = "export function build() {\n"
        body = "".join("  const v%d = load(%d);\n" % (i, i) for i in range(60)) + "}\n"
        self.commit_file("src/report.ts", head + body)
        self.write("src/report.ts", head + "  const extra = 1;\n" + body)
        code, data, _ = self.check("--base", "HEAD")
        self.assertEqual((code, data["findings"]), (0, []))
        self.assertEqual(self.existing(data), [("function-size", "src/report.ts")])

    def test_text_report_shows_the_existing_debt_in_its_own_section(self):
        self.commit_file("src/legacy.py", lines("old", 320))
        self.append("src/legacy.py", lines("fix", 2))
        code, out = self.check_text("--base", "HEAD")
        self.assertEqual(code, 0)
        self.assertIn("Already over budget at the base ref (1)", out)
        self.assertIn("src/legacy.py:1", out)
        self.assertIn("RESULT: clean", out)

    def test_long_added_lines_are_one_finding_per_file(self):
        long = "x = compute(" + ", ".join("arg%d" % i for i in range(40)) + ")\n"
        self.write("src/dense.py", long * 3)
        code, data, _ = self.check()
        hit = [f for f in data["findings"] if f["kind"] == "long-line"]
        self.assertEqual((code, [f["path"] for f in hit]), (1, ["src/dense.py"]))
        self.assertEqual((hit[0]["line"], hit[0]["limit"]), (1, 140))
        self.assertIn("3 added line", hit[0]["message"])

    def test_long_line_budget_is_configurable_and_off_at_zero(self):
        self.write("src/dense.py", "x = compute(" + ", ".join("arg%d" % i for i in range(40)) + ")\n")
        self.assertEqual(self.check("--max-line", "400")[0], 0)
        self.assertEqual(self.check("--max-line", "0")[0], 0)

    def test_only_added_lines_count_and_urls_and_tests_are_exempt(self):
        long = "x = compute(" + ", ".join("arg%d" % i for i in range(40)) + ")\n"
        self.commit_file("src/legacy.py", long)
        self.append("src/legacy.py", "y = 1\n")
        self.write("src/links.py", "URL = '" + "a" * 300 + "'\n")
        self.write("tests/test_dense.py", long)
        code, data, _ = self.check("--base", "HEAD")
        self.assertEqual((code, data["findings"]), (0, []))

    def test_unknown_base_is_a_usage_error(self):
        code, data, err = self.check("--base", "no-such-ref")
        self.assertEqual(code, 2)
        self.assertIn("not a commit", err)


if __name__ == "__main__":
    unittest.main()
