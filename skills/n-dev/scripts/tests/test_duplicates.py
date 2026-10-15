import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from ndev_check.duplicates import find_duplicates  # noqa: E402

BLOCK = "\n".join("total = total + item_%d.price * item_%d.qty" % (i, i) for i in range(8))


def all_lines(text):
    return frozenset(range(1, text.count("\n") + 2))


class FindDuplicates(unittest.TestCase):
    def test_block_copied_from_existing_file(self):
        new = "def f():\n" + BLOCK + "\n"
        corpus = {"old.py": BLOCK + "\n", "new.py": new}
        hits = find_duplicates(corpus, {"new.py": all_lines(new)}, 6)
        self.assertEqual(len(hits), 1)
        self.assertEqual((hits[0].path, hits[0].start, hits[0].end), ("new.py", 2, 9))
        self.assertEqual((hits[0].other_path, hits[0].other_start), ("old.py", 1))

    def test_existing_duplication_is_not_reported(self):
        corpus = {"a.py": BLOCK, "b.py": BLOCK}
        self.assertEqual(find_duplicates(corpus, {}, 6), [])

    def test_copy_within_the_change_reports_only_the_second(self):
        a, b = BLOCK, "x = 1\n" + BLOCK
        hits = find_duplicates({"a.py": a, "b.py": b}, {"a.py": all_lines(a), "b.py": all_lines(b)}, 6)
        self.assertEqual([(h.path, h.other_path) for h in hits], [("b.py", "a.py")])

    def test_trivial_lines_do_not_make_a_block(self):
        trivial = "\n".join(["}", "", "import os", "// note", ")", "end", "else"] * 3)
        corpus = {"a.js": trivial, "b.js": trivial}
        self.assertEqual(find_duplicates(corpus, {"b.js": all_lines(trivial)}, 6), [])

    def test_multiline_import_blocks_are_not_code(self):
        ts = "import {\n" + "".join("  Member%d,\n" % i for i in range(10)) + "} from '@lib/core';\n"
        py = "from pkg import (\n" + "".join("    name_%d,\n" % i for i in range(10)) + ")\n"
        corpus = {"a.ts": ts, "b.ts": ts, "a.py": py, "b.py": py}
        added = {"b.ts": all_lines(ts), "b.py": all_lines(py)}
        self.assertEqual(find_duplicates(corpus, added, 6), [])

    def test_short_shared_run_is_below_threshold(self):
        short = "\n".join(BLOCK.splitlines()[:5])
        corpus = {"a.py": short, "b.py": short}
        self.assertEqual(find_duplicates(corpus, {"b.py": all_lines(short)}, 6), [])


if __name__ == "__main__":
    unittest.main()
