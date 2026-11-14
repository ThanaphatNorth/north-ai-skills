"""End to end: the report reaches stdout whatever stdout can encode, and a reader that leaves early does
not turn the exit code into a crash."""
import os
import subprocess
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from failure_case import FailureCase  # noqa: E402
from repo_case import ENV, SCRIPT, lines  # noqa: E402


class Stdout(FailureCase):
    def test_text_report_on_an_ascii_stdout_escapes_what_it_cannot_encode(self):
        """The result line carries an em dash and paths may be in any script."""
        self.write("src/ราคา.py", lines("v", 320))
        code, out, err = self.cli(env=dict(ENV, PYTHONIOENCODING="ascii"), interpreter=())
        self.assertEqual((code, err), (1, ""))
        self.assertIn("  src/\\u0e23\\u0e32\\u0e04\\u0e32.py:1  new file has 320 lines", out)
        self.assertIn("RESULT: 1 finding(s) \\u2014 fix each", out)

    def test_json_report_is_ascii_whatever_the_paths_are(self):
        self.write("src/ราคา.py", lines("v", 320))
        code, out, err = self.cli("--json", env=dict(ENV, PYTHONIOENCODING="ascii"), interpreter=())
        self.assertEqual((code, err, out.isascii() if hasattr(out, "isascii") else True), (1, "", True))

    def test_reader_that_closed_the_pipe_gets_the_findings_exit_code_and_no_traceback(self):
        self.write("src/big.py", lines("v", 320))
        for flags in ([], ["--json"]):
            with self.subTest(flags=flags):
                proc = subprocess.Popen([sys.executable, "-I", SCRIPT, "--repo", self.repo, *flags],
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=ENV)
                proc.stdout.close()
                err = proc.stderr.read().decode()
                proc.stderr.close()
                self.assertEqual((proc.wait(timeout=60), err), (1, ""))

    def test_stdout_that_cannot_be_written_is_one_error_line(self):
        """`1</dev/null` hands the CLI a stdout that is open for reading only."""
        self.write("src/big.py", lines("v", 320))
        script = 'exec "$1" -I "$2" --repo "$3" 1</dev/null'
        proc = subprocess.run(["sh", "-c", script, "sh", sys.executable, SCRIPT, self.repo],
                              capture_output=True, text=True, env=ENV, timeout=60)
        self.assert_error_line((proc.returncode, "", proc.stderr), "Bad file descriptor")

    def test_stdout_closed_before_the_start_keeps_the_exit_code(self):
        """`>&-`: Python then has no stdout at all; there is nowhere to print, and nothing to crash on."""
        self.write("src/big.py", lines("v", 320))
        script = 'exec "$1" -I "$2" --repo "$3" >&-'
        proc = subprocess.run(["sh", "-c", script, "sh", sys.executable, SCRIPT, self.repo],
                              capture_output=True, text=True, env=ENV, timeout=60)
        self.assertEqual((proc.returncode, proc.stderr), (1, ""))


if __name__ == "__main__":
    unittest.main()
