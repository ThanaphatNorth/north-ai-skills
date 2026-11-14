"""End to end: a config file that cannot be used is one error line naming the file (and the line, when the
content is at fault), exit 2: it never crashes and never silently falls back to the default budgets."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from failure_case import FailureCase  # noqa: E402
from repo_case import lines  # noqa: E402


class UnusableConfig(FailureCase):
    def test_unreadable_config_names_the_file_and_the_reason(self):
        """A symlink that points at itself cannot be opened by any user, root included."""
        self.link(".ndev.toml", ".ndev.toml")
        self.assert_error_line(self.cli("--json"), "cannot read config file .ndev.toml", "symbolic links")

    def test_config_that_is_not_utf8_names_the_file_and_the_line(self):
        self.write_bytes(".ndev.toml", b"[budgets]\nmax-file = 10\n# caf\xe9\n")
        self.assert_error_line(self.cli("--json"), ".ndev.toml: line 3", "UTF-8")

    def test_default_config_that_is_a_directory_is_an_error_not_no_config(self):
        os.makedirs(os.path.join(self.repo, ".ndev.toml"))
        self.assert_error_line(self.cli("--json"), ".ndev.toml", "directory")

    def test_default_config_that_is_a_broken_symlink_is_an_error_not_no_config(self):
        self.link("moved-away.toml", ".ndev.toml")
        self.assert_error_line(self.cli("--json"), ".ndev.toml", "symlink")

    def test_default_config_that_is_a_fifo_is_an_error_and_does_not_block(self):
        os.mkfifo(os.path.join(self.repo, ".ndev.toml"))
        self.assert_error_line(self.cli("--json"), ".ndev.toml", "not a regular file")

    def test_explicit_config_that_is_missing_or_a_directory(self):
        missing = os.path.join(self.repo, "tools", "nope.toml")
        self.assert_error_line(self.cli("--json", "--config", missing), missing, "not found")
        folder = os.path.join(self.repo, "src")
        self.assert_error_line(self.cli("--json", "--config", folder), folder, "directory")

    def test_syntax_outside_the_subset_names_the_file_and_the_line(self):
        self.write(".ndev.toml", "[budgets]\nmax-file = 300\nreleased = 1979-05-27\n")
        self.assert_error_line(self.cli("--json"), ".ndev.toml: line 3", "1979-05-27")

    def test_arrays_nested_past_the_limit_name_the_file_and_the_line(self):
        self.write(".ndev.toml", "[check]\nexclude = " + "[" * 3000 + "]" * 3000 + "\n")
        self.assert_error_line(self.cli("--json"), ".ndev.toml: line 2", "nested")

    def test_integer_that_does_not_fit_64_bits_names_the_file_and_the_line(self):
        self.write(".ndev.toml", "[budgets]\nmax-file = " + "9" * 5000 + "\n")
        self.assert_error_line(self.cli("--json"), ".ndev.toml: line 2", "64-bit")

    def test_wrong_shape_names_the_file_and_the_table(self):
        self.write(".ndev.toml", "budgets = 300\n")
        self.assert_error_line(self.cli("--json"), ".ndev.toml", "[budgets] must be a table")


class UsableConfig(FailureCase):
    def test_profile_path_that_does_not_exist_is_not_the_checks_business(self):
        """n-arch owns the profile; the check accepts the key and never opens the file."""
        self.write(".ndev.toml", '[profile]\npath = "docs/architecture/missing.md"\n\n[budgets]\nmax-file = 10\n')
        self.write("src/mid.py", lines("m", 20))
        code, data, err = self.check()
        self.assertEqual((code, err, data["config"]), (1, "", ".ndev.toml"))
        self.assertEqual(self.kinds(data), [("file-size", "src/mid.py")])

    def test_crlf_line_endings_and_an_empty_file_are_valid(self):
        self.write_bytes(".ndev.toml", b"[budgets]\r\nmax-file = 10\r\n")
        self.write("src/mid.py", lines("m", 20))
        code, data, _ = self.check()
        self.assertEqual((code, data["budgets"]["max_file"]), (1, 10))
        self.write(".ndev.toml", "")
        code, data, _ = self.check()
        self.assertEqual((code, data["config"], data["budgets"]["max_file"]), (0, ".ndev.toml", 300))


if __name__ == "__main__":
    unittest.main()
