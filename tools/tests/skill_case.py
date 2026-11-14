"""Shared fixture: a throwaway skill folder, the real validate_skill CLI, and an in-process run."""
import contextlib
import io
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

TOOLS = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SCRIPT = os.path.join(TOOLS, "validate_skill.py")
sys.path.insert(0, TOOLS)

import validate_skill  # noqa: E402

PASS = "RESULT: PASS (0 errors, 0 warnings)"


def reference(lines=130, title="# Guide", read_when="> Read when: the test needs a reference.",
              sources="## Sources", extra=()):
    """A reference file of exactly `lines` lines by the validator's own count (no trailing newline)."""
    head = [x for x in (title, "", read_when, "") if x is not None]
    tail = list(extra) + ([sources, "- none"] if sources else [])
    filler = ["filler %d" % i for i in range(lines - len(head) - len(tail))]
    return "\n".join(head + filler + tail)


class SkillCase(unittest.TestCase):
    """A valid skill `demo` with one routed reference; each test breaks one thing."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="validate-skill-")
        self.skill = os.path.join(self.tmp, "demo")
        self.skill_md()
        self.write("references/guide.md", reference())

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def write(self, rel, text):
        path = os.path.join(self.skill, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)

    def skill_md(self, front="name: demo\ndescription: A demo skill.", body="Open `references/guide.md` first.\n"):
        self.write("SKILL.md", ("---\n%s\n---\n\n" % front if front is not None else "") + "# demo\n\n" + body)

    def cli(self, *args, skill=None):
        """Exit code and stdout lines of the real script in a subprocess."""
        proc = subprocess.run([sys.executable, "-I", SCRIPT, skill or self.skill, *args],
                              capture_output=True, text=True)
        return proc.returncode, proc.stdout.splitlines()

    def run_main(self, *args, statuses=None):
        """Exit code and stdout lines of main() in this process; `statuses` (url → status) replaces the network."""
        calls = []

        def fake_check_url(url):
            calls.append(url)
            return url, statuses[url]

        out = io.StringIO()
        with mock.patch.object(sys, "argv", ["validate_skill.py", self.skill, *args]), \
                mock.patch.object(validate_skill, "check_url", fake_check_url), \
                contextlib.redirect_stdout(out), self.assertRaises(SystemExit) as stop:
            validate_skill.main()
        self.calls = calls
        return stop.exception.code, out.getvalue().splitlines()
