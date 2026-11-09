"""Changes that weaken tests: removed assertions, skip/focus markers, deleted tests, rewritten snapshots,
lowered coverage thresholds."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from ndev_check.model import ChangedFile  # noqa: E402
from ndev_check.testguard import check_tests  # noqa: E402


def change(path, text, added=(), removed=(), is_new=False):
    return ChangedFile(path, is_new, frozenset(added), len(removed), text, tuple(removed))


def summary(findings):
    return [(f.kind, f.path, f.line) for f in findings]


class RemovedAssertions(unittest.TestCase):
    def test_removed_assertion_in_existing_test_is_flagged_with_its_base_line(self):
        f = change("src/cart.test.ts", "it('x', () => {\n});\n", removed=[(2, "  expect(total(cart)).toBe(30);")])
        found = check_tests([f], [])
        self.assertEqual(summary(found), [("test-weakened", "src/cart.test.ts", 2)])
        self.assertIn("1 assertion line(s) removed or rewritten", found[0].message)
        self.assertIn("base line 2", found[0].message)

    def test_rewritten_assertion_counts(self):
        f = change("tests/test_price.py", "def test_p():\n    assert price(2) == 25\n",
                   added=[2], removed=[(2, "    assert price(2) == 20")])
        self.assertEqual(len(check_tests([f], [])), 1)

    def test_moved_or_reindented_assertion_is_not_flagged(self):
        f = change("tests/test_price.py", "class T:\n    def test_p(self):\n        assert price(2) == 20\n",
                   added=[1, 2, 3], removed=[(1, "def test_p():"), (2, "    assert price(2) == 20")])
        self.assertEqual(check_tests([f], []), [])

    def test_removed_non_assertion_lines_and_source_files_are_ignored(self):
        files = [change("tests/test_a.py", "x = 1\n", removed=[(3, "    total = 0")]),
                 change("src/cart.ts", "x\n", removed=[(1, "assert(cart)")])]
        self.assertEqual(check_tests(files, []), [])

    def test_many_languages_count_as_assertions(self):
        for line in ("assertEquals(3, sum)", "XCTAssertEqual(a, b)", "t.Fatalf(\"bad\")", "require.NoError(t, err)",
                     "self.assertEqual(a, b)", "$this->assertSame(1, $x);", "assertThat(x).isEqualTo(1);",
                     "    .toHaveBeenCalledWith(1)", "EXPECT_EQ(a, b);", "with pytest.raises(ValueError):"):
            f = change("tests/test_x.py", "", removed=[(1, line)])
            self.assertEqual(len(check_tests([f], [])), 1, line)


class SkipMarkers(unittest.TestCase):
    def test_added_skip_and_focus_markers_are_flagged_once_per_file(self):
        text = "it.skip('a', () => {});\nfit('b', () => {});\nit('c', () => {});\n"
        found = check_tests([change("src/a.test.ts", text, added=[1, 2, 3], is_new=True)], [])
        self.assertEqual(summary(found), [("test-weakened", "src/a.test.ts", 1)])
        self.assertIn("2 skip/focus marker(s)", found[0].message)

    def test_python_go_jvm_dotnet_markers(self):
        for text in ("@pytest.mark.skip(reason='later')\n", "    t.Skip(\"flaky\")\n", "@Disabled\n",
                     "[Fact(Skip = \"later\")]\n", "        self.skipTest('x')\n", "@unittest.skip('x')\n"):
            found = check_tests([change("tests/test_y.py", text, added=[1])], [])
            self.assertEqual(len(found), 1, text)

    def test_markers_inside_string_literals_are_test_data_not_markers(self):
        text = ('cases = ("@pytest.mark.skip(reason=\'x\')", \'it.skip("a")\')\n'
                'write("t.py", src.replace("def t", "@unittest.skip\\ndef t"))\n')
        self.assertEqual(check_tests([change("tests/test_z.py", text, added=[1, 2])], []), [])

    def test_markers_on_unchanged_lines_are_not_flagged(self):
        self.assertEqual(check_tests([change("src/a.test.ts", "it.skip('a', () => {});\nx\n", added=[2])], []), [])


class OtherWeakening(unittest.TestCase):
    def test_deleted_test_file(self):
        found = check_tests([], ["tests/test_orders.py", "src/old.py"])
        self.assertEqual(summary(found), [("test-weakened", "tests/test_orders.py", 0)])

    def test_rewritten_snapshot(self):
        found = check_tests([change("src/__snapshots__/cart.test.ts.snap", "exports[`x`] = `1`;\n",
                                    added=[1], removed=[(1, "exports[`x`] = `2`;")])], [])
        self.assertEqual(summary(found), [("test-weakened", "src/__snapshots__/cart.test.ts.snap", 1)])

    def test_new_snapshot_is_fine(self):
        self.assertEqual(check_tests([change("src/__snapshots__/a.snap", "x\n", added=[1], is_new=True)], []), [])

    def test_lowered_coverage_threshold(self):
        f = change("jest.config.js", "  coverageThreshold: { global: { lines: 70 } },\n",
                   added=[1], removed=[(1, "  coverageThreshold: { global: { lines: 85 } },")])
        found = check_tests([f], [])
        self.assertEqual(summary(found), [("test-weakened", "jest.config.js", 1)])
        self.assertIn("lines 85 -> 70", found[0].message)

    def test_raised_threshold_and_unrelated_numbers_are_fine(self):
        files = [change("pyproject.toml", "fail_under = 90\n", added=[1], removed=[(1, "fail_under = 80")]),
                 change("src/config.ts", "lines: 10\n", added=[1], removed=[(1, "lines: 50")])]
        self.assertEqual(check_tests(files, []), [])

    def test_cov_fail_under_flag_in_ci_and_pass_with_no_tests(self):
        files = [change(".github/workflows/ci.yml", "run: pytest --cov-fail-under=60\n", added=[1],
                        removed=[(1, "run: pytest --cov-fail-under=80")]),
                 change("package.json", '  "test": "jest --passWithNoTests",\n', added=[1],
                        removed=[(1, '  "test": "jest",')])]
        self.assertEqual(sorted(f.path for f in check_tests(files, [])), [".github/workflows/ci.yml", "package.json"])



class ReviewFindings(unittest.TestCase):
    def test_deleted_coverage_gate_is_flagged(self):
        files = [change("pyproject.toml", "[tool.coverage.report]\n", added=[], removed=[(2, "fail_under = 90")]),
                 change(".github/workflows/ci.yml", "run: pytest\n", added=[1],
                        removed=[(1, "run: pytest --cov-fail-under=85")])]
        found = check_tests(files, [])
        self.assertEqual(sorted(f.path for f in found), [".github/workflows/ci.yml", "pyproject.toml"])
        self.assertIn("fail_under 90 removed", " ".join(f.message for f in found))

    def test_lint_limits_are_not_coverage_gates(self):
        files = [change("pyproject.toml", "max-branches = 12\n", added=[1], removed=[(1, "max-branches = 15")]),
                 change("package.json", '  "max-lines": 200,\n', added=[1], removed=[(1, '  "max-lines": 300,')])]
        self.assertEqual(check_tests(files, []), [])

    def test_ordinary_setup_calls_are_not_assertions(self):
        f = change("src/a.test.ts", "x\n", removed=[(3, "  const at = new Date(0).toISOString();"),
                                                      (4, "  const name = raw.toUpperCase();"),
                                                      (5, "  const p = require.resolve('./fixture');")])
        self.assertEqual(check_tests([f], []), [])

    def test_expected_failure_and_skip_if_are_markers(self):
        for text in ("    @unittest.expectedFailure\n", "test.skipIf(isWindows)('x', () => {});\n"):
            self.assertEqual(len(check_tests([change("tests/test_q.py", text, added=[1])], [])), 1, text)

if __name__ == "__main__":
    unittest.main()
