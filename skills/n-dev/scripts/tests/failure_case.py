"""Shared fixture for failure tests: the real CLI on a hostile input, and how it is allowed to fail."""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from repo_case import ENV, SCRIPT, RepoCase  # noqa: E402


class FailureCase(RepoCase):
    def cli(self, *args, repo=None, env=None, interpreter=("-I",), cwd=None, timeout=60):
        """(exit code, stdout, stderr) of the CLI against `repo` (default: the fixture repo); a run past
        `timeout` fails the test."""
        cmd = [sys.executable, *interpreter, SCRIPT, "--repo", repo or self.repo, *args]
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, env=env or ENV, cwd=cwd, timeout=timeout)
        except subprocess.TimeoutExpired:
            self.fail("the check was still running after %d s" % timeout)
        return proc.returncode, proc.stdout, proc.stderr

    def assert_error_line(self, result, *needles):
        """A setup failure: exit 2, nothing on stdout (so --json readers see no half document), and exactly
        one `error:` line on stderr that contains every needle."""
        code, out, err = result
        self.assertNotIn("Traceback", err)
        self.assertEqual((code, out), (2, ""), err[-400:])
        rows = err.strip().split("\n")
        self.assertEqual(len(rows), 1, err)
        self.assertTrue(rows[0].startswith("error: "), err)
        for needle in needles:
            self.assertIn(needle, rows[0])

    def write_bytes(self, rel, data):
        path = os.path.join(self.repo, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as fh:
            fh.write(data)

    def link(self, target, rel):
        path = os.path.join(self.repo, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        os.symlink(target, path)
