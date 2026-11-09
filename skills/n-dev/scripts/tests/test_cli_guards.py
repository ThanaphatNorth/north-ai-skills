"""End to end: test-weakening and new-dependency findings from a real git diff."""
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from repo_case import RepoCase  # noqa: E402

TEST = ("from src.pricing import price\n\n\ndef test_price():\n    assert price([]) == 0\n\n\n"
        "def test_total():\n    assert price([1]) == 1\n")


class TestWeakening(RepoCase):
    def setUp(self):
        super().setUp()
        self.commit_file("tests/test_pricing.py", TEST)

    def findings(self, kind):
        code, data, _ = self.check("--base", "HEAD")
        return code, [(f["path"], f["line"]) for f in data["findings"] if f["kind"] == kind]

    def test_removed_assertion_is_flagged(self):
        self.write("tests/test_pricing.py", TEST.replace("    assert price([1]) == 1\n", "    price([1])\n"))
        self.assertEqual(self.findings("test-weakened"), (1, [("tests/test_pricing.py", 9)]))

    def test_added_skip_marker_is_flagged(self):
        self.write("tests/test_pricing.py", TEST.replace("def test_total", "@pytest.mark.skip\ndef test_total"))
        self.assertEqual(self.findings("test-weakened"), (1, [("tests/test_pricing.py", 8)]))

    def test_deleted_test_file_is_flagged(self):
        os.remove(os.path.join(self.repo, "tests/test_pricing.py"))
        self.assertEqual(self.findings("test-weakened"), (1, [("tests/test_pricing.py", 0)]))

    def test_rewritten_snapshot_is_flagged_although_snapshots_are_noise_elsewhere(self):
        self.commit_file("src/__snapshots__/cart.test.ts.snap", "exports[`cart`] = `30`;\n")
        self.write("src/__snapshots__/cart.test.ts.snap", "exports[`cart`] = `25`;\n")
        self.assertEqual(self.findings("test-weakened"), (1, [("src/__snapshots__/cart.test.ts.snap", 1)]))

    def test_adding_tests_is_clean(self):
        self.append("tests/test_pricing.py", "\n\ndef test_more():\n    assert price([2]) == 2\n")
        self.assertEqual(self.findings("test-weakened"), (0, []))

    def test_renamed_test_file_is_not_a_deletion(self):
        self.git("mv", "tests/test_pricing.py", "tests/test_price_rules.py")
        self.assertEqual(self.findings("test-weakened"), (0, []))

    def test_audit_does_not_run_the_test_guard(self):
        self.commit_file("tests/test_later.py", "import pytest\n\n\n@pytest.mark.skip\ndef test_x():\n    assert 1\n")
        code, data, _ = self.check("--all")
        self.assertNotIn("test-weakened", [f["kind"] for f in data["findings"]])


class NewDependency(RepoCase):
    def test_package_json_dependency_added(self):
        pkg = {"name": "shop", "scripts": {"test": "node --test"}, "dependencies": {"zod": "^3.23.0"}}
        self.commit_file("package.json", json.dumps(pkg, indent=2) + "\n")
        pkg["dependencies"]["left-padder"] = "^1.0.0"
        pkg["scripts"]["lint"] = "eslint ."
        self.write("package.json", json.dumps(pkg, indent=2) + "\n")
        code, data, _ = self.check("--base", "HEAD")
        hit = [f for f in data["findings"] if f["kind"] == "new-dependency"]
        self.assertEqual(code, 1)
        self.assertEqual([f["path"] for f in hit], ["package.json"])
        self.assertIn("left-padder", hit[0]["message"])
        self.assertNotIn("lint", hit[0]["message"])

    def test_requirements_added(self):
        self.commit_file("requirements.txt", "requests==2.32.0\n")
        self.append("requirements.txt", "# http\nhttpx>=0.27\n")
        code, data, _ = self.check("--base", "HEAD")
        self.assertIn("httpx", " ".join(f["message"] for f in data["findings"]))

    def test_audit_skips_dependency_findings(self):
        self.commit_file("requirements.txt", "requests==2.32.0\n")
        code, data, _ = self.check("--all")
        self.assertNotIn("new-dependency", [f["kind"] for f in data["findings"]])


if __name__ == "__main__":
    unittest.main()
