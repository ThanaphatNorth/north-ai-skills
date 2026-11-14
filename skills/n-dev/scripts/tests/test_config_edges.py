"""Config at the edges: shapes a typo produces, and files `load` is handed that are not readable TOML."""
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from ndev_check.baseline import split  # noqa: E402
from ndev_check.config import ConfigError, from_dict, load  # noqa: E402
from ndev_check.model import Finding  # noqa: E402


class WrongShapes(unittest.TestCase):
    def assert_rejected(self, data, message):
        with self.assertRaises(ConfigError) as ctx:
            from_dict(data)
        self.assertEqual(str(ctx.exception), message)

    def test_layer_that_is_a_value_instead_of_a_table(self):
        self.assert_rejected({"layers": {"domain": "src/domain/**"}}, "[layers.domain] must be a table")

    def test_section_that_is_a_value_instead_of_a_table(self):
        self.assert_rejected({"check": ["legacy/**"]}, "[check] must be a table")

    def test_boolean_is_not_a_budget(self):
        self.assert_rejected({"budgets": {"max-line": True}}, "[budgets] max-line must be a whole number >= 0")

    def test_unknown_key_in_a_layer_lists_the_known_ones(self):
        self.assert_rejected({"layers": {"ui": {"paths": ["src/ui/**"], "may_import": []}}},
                             "[layers.ui] has unknown key(s): may_import (known: paths, imports, may-import)")


class LoadFailures(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="ndev-config-")
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)

    def put(self, data, name=".ndev.toml"):
        with open(os.path.join(self.root, name), "wb") as fh:
            fh.write(data)

    def assert_rejected(self, message, path=None):
        with self.assertRaises(ConfigError) as ctx:
            load(self.root, path)
        self.assertEqual(str(ctx.exception), message)

    def test_bytes_that_are_not_utf8_name_the_file_and_their_line(self):
        self.put(b"[budgets]\n# r\xe9sum\xe9\nmax-file = 10\n")
        self.assert_rejected(".ndev.toml: line 2: not valid UTF-8")
        self.put(b"\xff[budgets]\n", "first.toml")
        self.assert_rejected("first.toml: line 1: not valid UTF-8", "first.toml")

    def test_directory_and_dangling_symlink_are_errors_not_no_config(self):
        os.makedirs(os.path.join(self.root, "conf.toml"))
        self.assert_rejected("cannot read config file conf.toml: Is a directory", "conf.toml")
        os.symlink("gone.toml", os.path.join(self.root, ".ndev.toml"))
        self.assert_rejected("config file .ndev.toml is a symlink to a missing file")

    def test_old_mac_and_windows_line_endings_read_as_newlines(self):
        self.put(b"[budgets]\rmax-file = 10\r\nmax-func = 20\r")
        self.assertEqual(load(self.root, None).budgets, {"max_file": 10, "max_func": 20})

    def test_parse_error_carries_the_file_and_the_line(self):
        self.put(b"[budgets]\nmax-file = 10\n\n[budgets]\n")
        self.assert_rejected(".ndev.toml: line 4: table [budgets] is defined twice")


class FindingWithoutAFunction(unittest.TestCase):
    def test_function_size_finding_that_matches_no_function_stays_new(self):
        """`split` is total: a finding whose line starts no function in the text has no earlier self."""
        text = "function build() {\n  a();\n}\n"
        f = Finding("function-size", "r.ts", 2, 60, 50, "msg")
        self.assertEqual(split([f], {"r.ts": text}, {"r.ts": text}), ([f], []))


if __name__ == "__main__":
    unittest.main()
