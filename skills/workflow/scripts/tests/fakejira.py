"""A throwaway project for the Jira script tests: tracker.env, a 600 credentials file, and a fake curl on PATH.

The fake curl never touches the network. It reads the `curl -K -` config from stdin the way curl does and answers
401 unless that config is exactly the expected `user`; it logs its argv (curl.log, one line per call) and one JSON
record per call (see calls()), then answers with whatever the test's bash `case` body prints. Inside the arms,
`reply <http-code> [body] [redirect-url]` acts as curl would for the call's -o and -w, and $B is the folder that
holds the files given as `bodies`.
"""
import json
import os
import shutil
import stat
import subprocess
import tempfile
import textwrap

SCRIPTS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://site.example.test"
EMAIL = "bot@example.test"
TOKEN = "tok-SECRET-123"

FAKE_CURL = r'''#!/usr/bin/env python3
"""Fake curl for the Jira script tests: logs the call, checks the -K config from stdin, runs the responder."""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
argv = sys.argv[1:]


def unslashquote(text):
    """curl's quoted-parameter rule: ends at the first bare double quote; a backslash escapes the next character."""
    out, i = [], 0
    while i < len(text) and text[i] != '"':
        if text[i] == "\\":
            i += 1
            if i >= len(text):
                break
            out.append({"t": "\t", "n": "\n", "r": "\r", "v": "\v"}.get(text[i], text[i]))
        else:
            out.append(text[i])
        i += 1
    return "".join(out)


def parse_config(text):
    """[option, parameter] pairs, the way curl reads a -K file (tool_parsecfg.c)."""
    pairs = []
    for line in text.split("\n"):
        line = line.lstrip(" \t")
        if not line or line[0] in "#/\r*":
            continue
        i = 0
        while i < len(line) and not (line[i].isspace() or line[i] in "=:"):
            i += 1
        option, rest = line[:i], line[i:].lstrip(" \t\r=:")
        if rest.startswith('"'):
            param = unslashquote(rest[1:])
        else:
            param = rest.split()[0] if rest.split() else ""
        pairs.append([option, param])
    return pairs


def after(flag):
    return argv[argv.index(flag) + 1] if flag in argv[:-1] else ""


def data_of(value):
    if value.startswith("@"):
        with open(value[1:], encoding="utf-8") as fh:
            return fh.read()
    return value


with open(os.path.join(ROOT, "expect.json"), encoding="utf-8") as fh:
    expect = json.load(fh)
config = sys.stdin.read() if after("-K") == "-" else ""
pairs = parse_config(config)
auth = pairs == [["user", expect["email"] + ":" + expect["token"]]]
data = [data_of(argv[i + 1]) for i, a in enumerate(argv[:-1]) if a in ("-d", "--data-binary")]
call = {
    "argv": argv,
    "method": after("-X") or ("POST" if data or "-F" in argv else "GET"),
    "url": next((a for a in argv if a.startswith("http")), ""),
    "query": [argv[i + 1] for i, a in enumerate(argv[:-1]) if a == "--data-urlencode"],
    "data": data,
    "config": pairs,
    "auth": auth,
    # names only: what a child process of the script could read the credentials from
    "leaks": sorted({k for k, v in os.environ.items() if expect["token"] in v or k in ("JIRA_EMAIL", "JIRA_TOKEN")}
                    | ({"argv"} if any(expect["token"] in a for a in argv) else set())),
}
with open(os.path.join(ROOT, "curl.log"), "a", encoding="utf-8") as fh:
    fh.write(" ".join(argv) + "\n")
with open(os.path.join(ROOT, "curl.calls"), "a", encoding="utf-8") as fh:
    fh.write(json.dumps(call) + "\n")
env = dict(os.environ, FAKE_AUTH="ok" if auth else "bad", FAKE_O=after("-o"), FAKE_W=after("-w"),
           B=os.path.join(ROOT, "bodies"))
os.execve("/bin/bash", ["bash", os.path.join(ROOT, "bin", "responder.sh")] + argv, env)
'''

RESPONDER = r'''#!/bin/bash
reply() {  # reply <http-code> [body] [redirect-url]
  if [ -n "$FAKE_O" ]; then printf '%%s' "${2:-}" > "$FAKE_O"; else printf '%%s' "${2:-}"; fi
  case $FAKE_W in
    '%%{http_code}') printf '%%s' "$1" ;;
    '%%{redirect_url}') printf '%%s' "${3:-}" ;;
  esac
}
[ "$FAKE_AUTH" = ok ] || { reply 401 '{"errorMessages":["Client must be authenticated to access this resource."]}'; exit 0; }
case " $* " in
%s
esac
'''


def _real_curl():
    """(path of the real curl, "") when it has --libcurl, else (None, why not)."""
    path = shutil.which("curl")
    if not path:
        return None, "no curl on PATH: the Jira scripts cannot run without it"
    with tempfile.TemporaryDirectory() as tmp:
        probe = os.path.join(tmp, "probe.c")
        subprocess.run([path, "-sS", "--libcurl", probe, "-o", os.devnull, "file:///dev/null"], capture_output=True)
        if os.path.exists(probe):
            return path, ""
    return None, "%s has no --libcurl, the only way to see what curl understood without sending anything" % path


REAL_CURL, NO_REAL_CURL = _real_curl()


def real_curl(test):
    """The real curl, for a test of how curl itself reads a value (on file:// only, never the network).

    The fake curl copies curl's parsing rules, so only the real one can show the two agree. Without it the test
    fails with the reason: a skip would report the escaping as checked when nothing looked at it.
    """
    if REAL_CURL is None:
        test.fail("this test needs the real curl: " + NO_REAL_CURL)
    return REAL_CURL


def _executable(path, text):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    os.chmod(path, os.stat(path).st_mode | stat.S_IXUSR)


def fake_project(responder, creds=None, email=EMAIL, token=TOKEN, bodies=None, curl=None):
    """responder: bash `case " $* " in … esac` arms that print the response. Returns (root, env, log path).

    creds: the credentials file's text (default: plain JIRA_EMAIL= / JIRA_TOKEN= lines for email and token);
    email, token: what the fake accepts; bodies: {file name: text or JSON-able} written under $B;
    curl: a whole replacement for the fake curl script.
    """
    root = os.path.realpath(tempfile.mkdtemp())
    dl = os.path.join(root, ".claude", "90north-develop")
    os.makedirs(dl)
    path = os.path.join(root, "jira.env")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("JIRA_EMAIL=%s\nJIRA_TOKEN=%s\n" % (email, token) if creds is None else creds)
    os.chmod(path, 0o600)
    with open(os.path.join(dl, "tracker.env"), "w", encoding="utf-8") as fh:
        fh.write("JIRA_SITE=%s/\nJIRA_ENV_FILE=%s\n" % (SITE, path))
    with open(os.path.join(root, "expect.json"), "w", encoding="utf-8") as fh:
        json.dump({"email": email, "token": token}, fh)
    os.makedirs(os.path.join(root, "bodies"))
    for name, body in (bodies or {}).items():
        with open(os.path.join(root, "bodies", name), "w", encoding="utf-8") as fh:
            fh.write(body if isinstance(body, str) else json.dumps(body))
    bindir = os.path.join(root, "bin")
    os.makedirs(bindir)
    log = os.path.join(root, "curl.log")
    _executable(os.path.join(bindir, "responder.sh"),
                RESPONDER % textwrap.indent(textwrap.dedent(responder).strip("\n"), "  "))
    _executable(os.path.join(bindir, "curl"), FAKE_CURL if curl is None else curl)
    # HOME is the throwaway folder too, so nothing here can reach a real credentials file
    env = dict(os.environ, PATH=bindir + os.pathsep + os.environ["PATH"], HOME=root)
    for name in ("DEVELOP_DIR", "DEFECT_LOOP_DIR", "TRACKER", "JIRA_SITE", "JIRA_ENV_FILE", "JIRA_EMAIL", "JIRA_TOKEN"):
        env.pop(name, None)
    return root, env, log


def run_script(name, args, root, env, stdin=""):
    """Run one of the scripts from inside the fake project, in its own session (no terminal), stdin from a pipe."""
    return subprocess.run(["bash", os.path.join(SCRIPTS, name)] + list(args), capture_output=True, text=True,
                          cwd=root, env=env, input=stdin, start_new_session=True)


def calls(root):
    """One dict per fake-curl call, in order: argv, method, url, query, data, config, auth, leaks."""
    path = os.path.join(root, "curl.calls")
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh]


def requests(root):
    """["METHOD url", …] for every call the fake curl received."""
    return ["%s %s" % (c["method"], c["url"]) for c in calls(root)]
