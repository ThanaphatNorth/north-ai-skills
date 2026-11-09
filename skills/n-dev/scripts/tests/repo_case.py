"""Shared fixture for end-to-end tests: a throwaway git repository and the real CLI."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "structure_check.py")
ENV = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t",
           GIT_COMMITTER_EMAIL="t@t", GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_NOSYSTEM="1")


def lines(prefix, n):
    return "".join("%s_%d = compute(%d, rate)\n" % (prefix, i, i) for i in range(n))


class RepoCase(unittest.TestCase):
    """Base repo on branch `feature` off `main`: src/app.py and src/pricing.py committed."""

    def setUp(self):
        self.repo = tempfile.mkdtemp(prefix="ndev-check-")
        self.git("init", "-q", "-b", "main")
        self.write("src/app.py", "from routes import ROUTES\n\n" + lines("base", 10))
        self.write("src/pricing.py", "def price(cart):\n" + "".join(
            "    total += line_%d.amount * line_%d.qty\n" % (i, i) for i in range(8)) + "    return total\n")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "base")
        self.git("checkout", "-q", "-b", "feature")

    def tearDown(self):
        shutil.rmtree(self.repo, ignore_errors=True)

    def git(self, *args):
        subprocess.run(["git", *args], cwd=self.repo, env=ENV, check=True, capture_output=True)

    def write(self, rel, text):
        path = os.path.join(self.repo, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as fh:
            fh.write(text)

    def append(self, rel, text):
        with open(os.path.join(self.repo, rel), "a") as fh:
            fh.write(text)

    def check(self, *args):
        proc = subprocess.run([sys.executable, "-I", SCRIPT, "--repo", self.repo, "--json", *args],
                              capture_output=True, text=True, env=ENV)
        data = json.loads(proc.stdout) if proc.stdout.strip().startswith("{") else None
        return proc.returncode, data, proc.stderr

    def check_text(self, *args):
        proc = subprocess.run([sys.executable, "-I", SCRIPT, "--repo", self.repo, *args],
                              capture_output=True, text=True, env=ENV)
        return proc.returncode, proc.stdout

    def kinds(self, data):
        return sorted((f["kind"], f["path"]) for f in data["findings"])

    def existing(self, data):
        return sorted((f["kind"], f["path"]) for f in data.get("existing") or [])

    def commit_file(self, rel, text):
        self.write(rel, text)
        self.git("add", "-A")
        self.git("commit", "-qm", "add " + rel)
