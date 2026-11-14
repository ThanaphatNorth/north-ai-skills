"""End to end: odd paths in the tree. A file whose name needs quoting is still checked; a path that is not a
readable regular file is skipped (with a note on stderr when it is neither absent nor a directory) and the
rest of the check still reports."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from failure_case import FailureCase  # noqa: E402
from repo_case import ENV, lines  # noqa: E402

QUOTED_BY_GIT = {"double quote": 'src/we"ird.py', "newline": "src/new\nline.py", "tab": "src/ta\tb.py",
                 "backslash": "src/back\\slash.py"}
PLAIN_TO_GIT = {"space": "src/my file.py", "single quote": "src/it's.py", "thai": "src/ราคา.py",
                "emoji": "src/😀.py", "leading dash": "-rf.py", "brackets": "src/[id].py"}


class FileNames(FailureCase):
    def assert_checked(self, names):
        """Each name, as a new file over budget and then as a committed file that grows, is reported by name."""
        for n, (label, name) in enumerate(names.items()):
            with self.subTest(name=label, state="untracked"):
                self.write(name, lines("new%d" % n, 320))
                code, data, err = self.check("--base", "HEAD")
                self.assertEqual((code, err), (1, ""))
                self.assertEqual(self.kinds(data), [("file-size", name)])
            self.git("add", "-A")
            self.git("commit", "-qm", "add")
            with self.subTest(name=label, state="modified"):
                self.append(name, lines("grown%d" % n, 30))
                code, data, err = self.check("--base", "HEAD")
                self.assertEqual((self.kinds(data), self.existing(data)), ([("wiring", name)], [("file-size", name)]))
            self.git("commit", "-qam", "grow")

    def test_names_git_would_quote_are_still_checked(self):
        self.assert_checked(QUOTED_BY_GIT)

    def test_names_with_spaces_and_non_ascii_are_checked(self):
        self.assert_checked(PLAIN_TO_GIT)

    def test_name_with_glob_characters_is_not_read_as_a_pattern(self):
        """`[id].py` as a git pathspec also matches `i.py`, whose added lines then counted against both."""
        self.commit_file("src/[id].py", lines("a", 5))
        self.commit_file("src/i.py", lines("b", 5))
        self.append("src/[id].py", "x = 1\n")
        self.append("src/i.py", lines("c", 25))
        code, data, _ = self.check("--base", "HEAD")
        self.assertEqual(self.kinds(data), [("wiring", "src/i.py")])

    def test_text_report_keeps_a_name_with_a_newline_on_one_line(self):
        self.write("src/x\nRESULT: clean.py", lines("v", 320))
        code, out, _ = self.cli()
        self.assertEqual(code, 1)
        self.assertIn("Files over budget (1)", out)
        self.assertIn("  src/x\\nRESULT: clean.py:1  new file has 320 lines", out)
        self.assertEqual([row for row in out.split("\n") if row.startswith("RESULT:")],
                         ["RESULT: 1 finding(s) — fix each, or give a one-line reason in the report"])


class NotARegularFile(FailureCase):
    def checked(self, *args):
        """(exit code, findings, stderr) with the run capped, so a blocked read fails instead of hanging."""
        code, out, err = self.cli("--json", *args)
        self.assertNotIn("Traceback", err)
        return code, self.kinds(json.loads(out)), err

    def test_directory_broken_symlink_and_symlink_to_a_directory_are_skipped(self):
        """Untracked first, then committed and seen through the diff."""
        self.write("pkg.py/inner.txt", "a folder with a code-like name\n")
        self.link("nowhere.py", "src/broken.py")
        self.link("src", "linked.py")
        self.write("src/big.py", lines("v", 320))
        self.assertEqual(self.checked(), (1, [("file-size", "src/big.py")], ""))
        self.git("add", "-A")
        self.git("commit", "-qm", "odd paths")
        os.remove(os.path.join(self.repo, "src", "pricing.py"))
        self.write("src/pricing.py/part.txt", "a tracked file that became a folder\n")
        self.assertEqual(self.checked("--base", "main"), (1, [("file-size", "src/big.py")], ""))

    def test_folder_replaced_by_a_file_is_a_plain_deletion(self):
        """The files git still lists under it are gone, not unreadable: no note."""
        self.commit_file("src/util/helpers.py", lines("h", 5))
        shutil.rmtree(os.path.join(self.repo, "src", "util"))
        self.write("src/util", "now a file\n")
        self.write("src/big.py", lines("v", 320))
        self.assertEqual(self.checked("--base", "HEAD"), (1, [("file-size", "src/big.py")], ""))

    def test_symlink_to_a_fifo_is_skipped_with_a_note_instead_of_blocking(self):
        os.mkfifo(os.path.join(self.repo, "events.fifo"))
        self.link("../events.fifo", "src/events.py")
        self.write("src/big.py", lines("v", 320))
        code, kinds, err = self.checked()
        self.assertEqual((code, kinds), (1, [("file-size", "src/big.py")]))
        self.assertEqual(err.strip(), "note: skipped unreadable path src/events.py (not a regular file)")

    def test_symlink_to_a_device_is_skipped_with_a_note_instead_of_read(self):
        self.link("/dev/null", "src/sink.py")
        code, kinds, err = self.checked()
        self.assertEqual((code, kinds), (0, []))
        self.assertEqual(err.strip(), "note: skipped unreadable path src/sink.py (not a regular file)")

    def test_submodule_and_nested_repository_are_skipped(self):
        other = tempfile.mkdtemp(prefix="ndev-sub-")
        self.addCleanup(shutil.rmtree, other, ignore_errors=True)
        for cmd in (["init", "-q", "-b", "main"], ["commit", "-q", "--allow-empty", "-m", "base"]):
            subprocess.run(["git", *cmd], cwd=other, env=ENV, check=True, capture_output=True)
        self.git("-c", "protocol.file.allow=always", "submodule", "add", "-q", other, "vendor_sub.py")
        shutil.copytree(other, os.path.join(self.repo, "nested.py"))
        self.assertEqual(self.checked(), (0, [], ""))
        self.git("commit", "-qm", "submodule")
        self.assertEqual(self.checked("--base", "main"), (0, [], ""))
        self.assertEqual(self.checked("--all"), (0, [], ""))

    def test_tracked_file_missing_from_the_working_tree_is_skipped_as_a_duplicate_source(self):
        """`git ls-files` still lists it, as it would a file deleted between the listing and the read."""
        os.remove(os.path.join(self.repo, "src", "pricing.py"))
        self.write("src/big.py", lines("v", 320))
        self.assertEqual(self.checked(), (1, [("file-size", "src/big.py")], ""))


class FileContent(FailureCase):
    def test_file_that_is_not_utf8_is_checked_and_a_binary_one_is_skipped(self):
        self.write_bytes("src/latin.py", ("# caf\xe9\n" + lines("v", 320)).encode("latin-1"))
        self.write_bytes("src/wide.py", lines("v", 320).encode("utf-16"))
        self.write_bytes("src/blob.py", b"\x00\x01" + lines("v", 320).encode())
        code, data, err = self.check()
        self.assertEqual((code, err, self.kinds(data)), (1, "", [("file-size", "src/latin.py")]))

    def test_tracked_file_that_turned_binary_is_skipped(self):
        self.commit_file("src/table.py", lines("v", 10))
        self.write_bytes("src/table.py", b"\x00" + lines("v", 320).encode())
        code, data, err = self.check("--base", "HEAD")
        self.assertEqual((code, err, data["findings"]), (0, "", []))

    def test_branch_without_changes_is_clean_in_both_formats(self):
        code, data, err = self.check()
        self.assertEqual((code, err, data["findings"], data["existing"]), (0, "", [], []))
        code, out, err = self.cli()
        self.assertEqual((code, err, out.strip().split("\n")[-1]), (0, "", "RESULT: clean"))

    def test_megabyte_line_is_one_long_line_finding(self):
        self.write("src/wide.py", "x = " + " + ".join("a%d" % i for i in range(150000)) + "\n")
        code, data, err = self.check()
        self.assertEqual((code, err, self.kinds(data)), (1, "", [("long-line", "src/wide.py")]))
        self.assertGreater(data["findings"][0]["value"], 1000000)

    def test_file_too_large_to_compare_is_not_a_duplicate_source(self):
        """Tracked files over 512 KB are left out of the duplicate search."""
        block = open(os.path.join(self.repo, "src", "pricing.py")).read()
        self.commit_file("src/huge.py", block.replace("def price", "def huge") + "# pad\n" * 100000)
        os.remove(os.path.join(self.repo, "src", "pricing.py"))
        self.write("src/quote.py", block.replace("def price", "def quote"))
        code, data, _ = self.check("--base", "HEAD")
        self.assertEqual([f for f in data["findings"] if f["kind"] == "duplicate"], [])


if __name__ == "__main__":
    unittest.main()
