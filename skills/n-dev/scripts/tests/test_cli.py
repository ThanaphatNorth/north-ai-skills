"""End to end: a throwaway git repository, the real CLI, its exit code and JSON."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "structure_check.py")
ENV = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t",
           GIT_COMMITTER_EMAIL="t@t", GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_NOSYSTEM="1")


def lines(prefix, n):
    return "".join("%s_%d = compute(%d, rate)\n" % (prefix, i, i) for i in range(n))


class StructureCheckCli(unittest.TestCase):
    def setUp(self):
        self.repo = tempfile.mkdtemp(prefix="ndev-check-")
        self.git("init", "-q", "-b", "main")
        self.write("src/app.py", "from routes import ROUTES\n\n" + lines("base", 10))
        self.write("src/pricing.py", "def price(cart):\n" + "".join(
            "    total += line_%d.amount * line_%d.qty\n" % (i, i) for i in range(8)) + "    return total\n")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "base")
        self.git("checkout", "-q", "-b", "feature")

    def tearDown(self):
        shutil.rmtree(self.repo, ignore_errors=True)

    def git(self, *args):
        subprocess.run(["git", *args], cwd=self.repo, env=ENV, check=True, capture_output=True)

    def write(self, rel, text):
        path = os.path.join(self.repo, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as fh:
            fh.write(text)

    def append(self, rel, text):
        with open(os.path.join(self.repo, rel), "a") as fh:
            fh.write(text)

    def check(self, *args):
        proc = subprocess.run([sys.executable, "-I", SCRIPT, "--repo", self.repo, "--json", *args],
                              capture_output=True, text=True, env=ENV)
        data = json.loads(proc.stdout) if proc.stdout.strip().startswith("{") else None
        return proc.returncode, data, proc.stderr

    def kinds(self, data):
        return sorted((f["kind"], f["path"]) for f in data["findings"])

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

    def test_unknown_base_is_a_usage_error(self):
        code, data, err = self.check("--base", "no-such-ref")
        self.assertEqual(code, 2)
        self.assertIn("not a commit", err)


if __name__ == "__main__":
    unittest.main()
