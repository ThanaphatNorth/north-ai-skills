import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from ndev_check.baseline import split  # noqa: E402
from ndev_check.model import Budgets, Finding  # noqa: E402

B = Budgets(max_file=10, max_test_file=20, max_func=5)


def text(n):
    return "".join("x%d = %d\n" % (i, i) for i in range(n))


def ts_fn(name, n):
    """A brace-language function of n body lines; its span is n + 2 lines."""
    return "function %s() {\n%s}\n" % (name, "".join("  v%d();\n" % i for i in range(n)))


def file_size(path, now, limit=B.max_file):
    return Finding("file-size", path, 1, now, limit, "msg")


def func_size(path, line, length):
    return Finding("function-size", path, line, length, B.max_func, "msg")


class FileSize(unittest.TestCase):
    def test_new_file_over_budget_is_new(self):
        f = file_size("a.py", 12)
        self.assertEqual(split([f], {"a.py": text(12)}, {"a.py": None}), ([f], []))

    def test_file_that_crossed_the_budget_in_this_change_is_new(self):
        f = file_size("a.py", 12)
        self.assertEqual(split([f], {"a.py": text(12)}, {"a.py": text(9)}), ([f], []))

    def test_file_already_over_budget_is_existing_with_both_sizes(self):
        new, existing = split([file_size("a.py", 14)], {"a.py": text(14)}, {"a.py": text(12)})
        self.assertEqual(new, [])
        self.assertEqual([(e.kind, e.path, e.value) for e in existing], [("file-size", "a.py", 14)])
        self.assertIn("12", existing[0].message)
        self.assertIn("14", existing[0].message)

    def test_test_file_is_judged_against_its_own_budget(self):
        f = file_size("a.test.ts", 22, B.max_test_file)
        new, existing = split([f], {"a.test.ts": text(22)}, {"a.test.ts": text(21)})
        self.assertEqual((new, len(existing)), ([], 1))


class FunctionSize(unittest.TestCase):
    def test_function_already_long_at_the_base_is_existing(self):
        new, existing = split([func_size("r.ts", 1, 10)], {"r.ts": ts_fn("build", 8)},
                              {"r.ts": ts_fn("build", 7)})
        self.assertEqual(new, [])
        self.assertIn("build", existing[0].message)
        self.assertIn("9", existing[0].message)

    def test_function_that_grew_past_the_budget_is_new(self):
        f = func_size("r.ts", 1, 10)
        self.assertEqual(split([f], {"r.ts": ts_fn("build", 8)}, {"r.ts": ts_fn("build", 2)}), ([f], []))

    def test_new_function_in_an_old_file_is_new(self):
        f = func_size("r.ts", 4, 10)
        now = ts_fn("old", 1) + ts_fn("added", 8)
        self.assertEqual(split([f], {"r.ts": now}, {"r.ts": ts_fn("old", 1)}), ([f], []))

    def test_same_named_functions_are_matched_in_order(self):
        was = ts_fn("run", 8) + ts_fn("run", 2)
        now = ts_fn("run", 8) + ts_fn("run", 8)
        first, second = func_size("r.ts", 1, 10), func_size("r.ts", 11, 10)
        new, existing = split([first, second], {"r.ts": now}, {"r.ts": was})
        self.assertEqual(new, [second])
        self.assertEqual([e.line for e in existing], [1])


class OtherKinds(unittest.TestCase):
    def test_wiring_and_duplicates_are_always_new(self):
        found = [Finding("wiring", "a.py", 3, 30, 20, "msg"), Finding("duplicate", "a.py", 5, 6, 6, "msg")]
        self.assertEqual(split(found, {"a.py": text(40)}, {"a.py": text(40)}), (found, []))


if __name__ == "__main__":
    unittest.main()
