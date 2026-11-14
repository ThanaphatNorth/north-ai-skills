"""End to end: when git, the repository or the process environment is broken, the CLI says so in one line
on stderr, prints nothing on stdout and exits 2: never a traceback, never the findings exit code."""
import contextlib
import io
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, ".."))

from failure_case import FailureCase  # noqa: E402
from repo_case import ENV, SCRIPT, lines  # noqa: E402


class BrokenSetup(FailureCase):
    def scratch(self):
        path = tempfile.mkdtemp(prefix="ndev-setup-")
        self.addCleanup(shutil.rmtree, path, ignore_errors=True)
        return path

    def test_git_missing_from_path_is_one_error_line(self):
        result = self.cli("--json", env=dict(ENV, PATH=self.scratch()))
        self.assert_error_line(result, "git", "PATH")

    def test_repo_that_does_not_exist_is_one_error_line(self):
        gone = os.path.join(self.scratch(), "nope")
        self.assert_error_line(self.cli("--json", repo=gone), gone, "not a directory")

    def test_repo_that_is_a_file_is_one_error_line(self):
        a_file = os.path.join(self.repo, "src", "app.py")
        self.assert_error_line(self.cli("--json", repo=a_file), a_file, "not a directory")

    def test_directory_outside_any_repository_is_one_error_line(self):
        self.assert_error_line(self.cli("--json", repo=self.scratch()), "not a git repository")

    def test_unknown_base_leaves_stdout_empty_under_json(self):
        self.assert_error_line(self.cli("--json", "--base", "no-such-ref"), "no-such-ref", "not a commit")

    def test_git_failure_with_several_lines_is_reported_on_one(self):
        """git refuses to diff a tree in which a tracked file became a FIFO, and says so on two lines."""
        os.remove(os.path.join(self.repo, "src", "app.py"))
        os.mkfifo(os.path.join(self.repo, "src", "app.py"))
        self.assert_error_line(self.cli("--json"), "git diff", "src/app.py")

    def test_current_directory_removed_under_a_relative_config_path(self):
        """The OS cannot resolve a relative --config when the shell's directory is gone."""
        gone = self.scratch()
        script = 'cd "$1" && rmdir "$1" && exec "$2" -I "$3" --repo "$4" --config draft.toml --json'
        proc = subprocess.run(["sh", "-c", script, "sh", gone, sys.executable, SCRIPT, self.repo],
                              capture_output=True, text=True, env=ENV, timeout=60)
        # An interpreter with startup hooks (a coverage .pth) may complain about the directory first;
        # what the CLI itself says is the last line, and no traceback runs through its code.
        self.assertEqual((proc.returncode, proc.stdout), (2, ""), proc.stderr[-400:])
        self.assertTrue(proc.stderr.strip().split("\n")[-1].startswith("error: "), proc.stderr[-400:])
        self.assertNotIn("structure_check.py", proc.stderr)

    def test_python_without_docstrings_still_runs(self):
        """`python -OO` strips docstrings; the parser's description comes from one."""
        self.write("src/big.py", lines("v", 320))
        code, out, err = self.cli("--json", interpreter=("-I", "-OO"))
        self.assertEqual((code, err), (1, ""))
        self.assertIn('"file-size"', out)


class RepositoryWithoutCommits(FailureCase):
    def setUp(self):
        super().setUp()
        self.fresh = tempfile.mkdtemp(prefix="ndev-fresh-")
        self.addCleanup(shutil.rmtree, self.fresh, ignore_errors=True)
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=self.fresh, env=ENV, check=True, capture_output=True)
        os.makedirs(os.path.join(self.fresh, "src"))
        with open(os.path.join(self.fresh, "src", "big.py"), "w") as fh:
            fh.write(lines("v", 320))

    def test_every_file_counts_as_new(self):
        code, out, err = self.cli("--json", repo=self.fresh)
        self.assertEqual((code, err), (1, ""))
        self.assertIn('"file-size"', out)
        self.assertIn("new file has 320 lines", out)

    def test_a_base_ref_cannot_resolve_and_is_one_error_line(self):
        self.assert_error_line(self.cli("--json", "--base", "HEAD", repo=self.fresh), "'HEAD'", "not a commit")


class BranchWithoutADefaultBranch(FailureCase):
    def test_base_falls_back_to_head_when_no_default_branch_exists(self):
        """No origin, no main or master: the change is what the working tree adds to HEAD."""
        self.git("branch", "-m", "feature", "trunk")
        self.git("branch", "-D", "main")
        self.append("src/app.py", lines("extra", 25))
        code, out, err = self.cli("--json")
        self.assertEqual((code, err), (1, ""))
        self.assertIn('"wiring"', out)
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=self.repo, env=ENV, capture_output=True, text=True)
        self.assertIn('"base": "%s"' % head.stdout.strip(), out)


class InternalError(FailureCase):
    def test_unexpected_exception_exits_2_not_the_findings_code(self):
        """An uncaught exception used to exit 1, which callers read as "findings"."""
        import structure_check
        out, err = io.StringIO(), io.StringIO()
        with mock.patch.object(structure_check, "run", side_effect=RuntimeError("boom")), \
                contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = structure_check.main(["--repo", self.repo, "--json"])
        self.assertEqual((code, out.getvalue()), (2, ""))
        self.assertIn("error: internal error (RuntimeError: boom)", err.getvalue().strip().split("\n")[-1])

    def test_main_returns_the_status_and_prints_to_the_stdout_it_is_given(self):
        """Called in-process (a wrapper, a test), stdout may be any text stream."""
        import structure_check
        self.write("src/big.py", lines("v", 320))
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = structure_check.main(["--repo", self.repo, "--no-config"])
        self.assertEqual(code, 1)
        self.assertIn("  src/big.py:1  new file has 320 lines", out.getvalue())
        self.assertTrue(out.getvalue().endswith("in the report\n"))


if __name__ == "__main__":
    unittest.main()
