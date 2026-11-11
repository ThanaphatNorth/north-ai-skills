"""A throwaway project for the Jira script tests: tracker.env, a 600 credentials file, and a fake curl on PATH.

The fake curl drops its stdin (the credentials arrive there via `curl -K -`), logs its argv, and answers with
whatever the test's bash `case` body prints.
"""
import os
import stat
import tempfile
import textwrap

TOKEN = "tok-SECRET-123"


def fake_project(responder):
    """responder: bash `case " $* " in … esac` arms that print the response. Returns (root, env, log path)."""
    root = tempfile.mkdtemp()
    dl = os.path.join(root, ".claude", "90north-develop")
    os.makedirs(dl)
    creds = os.path.join(root, "jira.env")
    with open(creds, "w") as fh:
        fh.write("JIRA_EMAIL=bot@example.test\nJIRA_TOKEN=%s\n" % TOKEN)
    os.chmod(creds, 0o600)
    with open(os.path.join(dl, "tracker.env"), "w") as fh:
        fh.write("JIRA_SITE=https://site.example.test/\nJIRA_ENV_FILE=%s\n" % creds)
    bindir = os.path.join(root, "bin")
    os.makedirs(bindir)
    log = os.path.join(root, "curl.log")
    fake = os.path.join(bindir, "curl")
    with open(fake, "w") as fh:
        fh.write("#!/bin/bash\ncat > /dev/null\necho \"$*\" >> \"%s\"\ncase \" $* \" in\n%s\nesac\n"
                 % (log, textwrap.indent(textwrap.dedent(responder).strip("\n"), "  ")))
    os.chmod(fake, os.stat(fake).st_mode | stat.S_IXUSR)
    env = dict(os.environ, PATH=bindir + os.pathsep + os.environ["PATH"])
    env.pop("DEVELOP_DIR", None)
    env.pop("DEFECT_LOOP_DIR", None)
    return root, env, log
