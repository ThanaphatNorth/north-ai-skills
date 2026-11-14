"""What each subagent of the plugin may not run or write. Each rule mirrors a hard rule in the agent's own file
(agents/*.md). Pure: argv in, the reason out."""
from __future__ import annotations

import fnmatch
import os
import re
from typing import Dict, Optional, Sequence, Set

from guard_shell import SHELLS, git_subcommand, has_short, positionals

WRITERS: Set[str] = {"dev-builder", "defect-fixer", "defect-repro"}
READERS: Set[str] = {"risk-reviewer", "loop-verifier", "loop-learner"}
_PKG = {"npm", "pnpm", "yarn", "bun"}
_TRACKER_SCRIPTS = ("tracker.sh", "local_board.py", "jira-*.sh")
_SYSTEM_INSTALLERS = {"apt", "apt-get", "dnf", "yum", "pacman", "apk", "port", "pipx", "gem"}
_DB_CLIENTS = {"psql", "mysql", "mariadb", "mongosh", "mongo", "redis-cli", "sqlcmd", "sqlite3", "pg_dump",
               "pg_dumpall", "pg_restore", "mysqldump", "mongodump", "mongorestore", "createdb", "dropdb",
               "flyway", "liquibase"}
_SERVERS = {"uvicorn", "gunicorn", "hypercorn", "daphne", "nodemon", "http-server", "live-server", "serve"}
_BOOT_SCRIPTS = {"dev", "start", "serve", "preview", "develop", "start:dev", "start:prod", "start:debug"}
_GH_WRITES: Dict[str, Set[str]] = {
    "pr": {"create", "merge", "close", "reopen", "edit", "comment", "review", "ready"},
    "issue": {"create", "close", "reopen", "edit", "comment", "delete", "transfer"},
    "repo": {"create", "delete", "edit", "fork", "rename", "archive"},
    "release": {"create", "delete", "edit", "upload"},
}
_GH_API_WRITE_FLAGS = {"-X", "--method", "-f", "-F", "--field", "--raw-field", "--input"}
_GIT_READS = {"diff", "log", "show", "blame", "rev-parse", "status", "ls-files", "ls-tree", "cat-file", "merge-base",
              "describe", "shortlog", "grep", "for-each-ref", "name-rev", "rev-list", "diff-tree", "show-ref",
              "whatchanged", "count-objects", "check-ignore", "version"}
_READER_DENIED = {
    "npm", "pnpm", "yarn", "bun", "npx", "bunx", "pnpx", "node", "deno", "ts-node", "tsx", "pytest", "jest", "vitest",
    "playwright", "cypress", "make", "cmake", "cargo", "go", "mvn", "gradle", "gradlew", "tsc", "eslint", "prettier",
    "ruff", "mypy", "php", "composer", "bundle", "rake", "rails", "ruby", "dotnet", "swift", "xcodebuild", "pod",
    "flutter", "dart", "docker", "docker-compose", "kubectl", "terraform", "ansible", "pip", "pip3", "uv", "brew",
    "curl", "wget", "ssh", "scp", "sftp", "rsync", "nc", "ncat", "telnet", "ftp", "gh",
    "rm", "rmdir", "mv", "chmod", "chown", "chgrp", "ln", "dd", "truncate", "tee", "patch",
    "kill", "pkill", "killall", "launchctl", "crontab", "open", "osascript",
}
_OWN_FILES = {
    "risk-reviewer": "review.md or review-<lens>.md",
    "loop-verifier": "verify.md",
    "loop-learner": "knowledge/, lessons.md, learn.md or weekly.md",
}


def _names_tracker_script(args: Sequence[str]) -> bool:
    return any(fnmatch.fnmatch(os.path.basename(a), pattern) for a in args for pattern in _TRACKER_SCRIPTS)


def common_rule(args: Sequence[str]) -> Optional[str]:
    """The rule every plugin subagent breaks with this command: a push, or a call to the tracker."""
    name = os.path.basename(args[0])
    if name == "git" and git_subcommand(args) == "push":
        return "no-push: a subagent never pushes; the orchestrator ships after the user's yes"
    if name in SHELLS | {"python", "python3"} or _names_tracker_script(args[:1]):
        if _names_tracker_script(args):
            return "no-tracker: only the orchestrator reads and writes the tracker"
    return None


def _git_rule(args: Sequence[str]) -> Optional[str]:
    sub = git_subcommand(args)
    rest = list(args[args.index(sub) + 1:]) if sub in args else []
    if sub == "merge":
        return "no-merge: merging is a person's decision"
    if sub == "branch" and (has_short(rest, "[dD]") or "--delete" in rest):
        return "no-delete: a subagent never deletes a branch"
    if sub == "worktree" and rest[:1] and rest[0] in ("remove", "prune"):
        return "no-delete: a subagent never deletes a worktree"
    if sub in ("tag", "update-ref") and has_short(rest, "d"):
        return "no-delete: a subagent never deletes a ref"
    if sub in ("commit", "merge") and ("--no-verify" in rest or (sub == "commit" and has_short(rest, "n"))):
        return "no-skip-hooks: commit hooks are part of the checks"
    if (sub == "reset" and "--hard" in rest) or (sub == "clean" and (has_short(rest, "f") or "--force" in rest)):
        return "no-discard: this would destroy uncommitted work in the worktree"
    if sub in ("filter-branch", "filter-repo"):
        return "no-discard: rewriting history is not a builder's job"
    if sub == "remote" and rest[:1] and rest[0] in ("add", "set-url", "remove", "rm", "rename"):
        return "no-remote-change: the remotes belong to the project"
    if sub == "config" and ("--global" in rest or "--system" in rest):
        return "no-global-config: never change git config outside the worktree"
    return None


def _gh_rule(args: Sequence[str]) -> Optional[str]:
    words = positionals(args[1:])
    if len(words) >= 2 and words[1] in _GH_WRITES.get(words[0], set()):
        return "no-tracker: only the orchestrator writes to the remote (gh %s %s)" % (words[0], words[1])
    if words[:1] == ["api"] and any(a.split("=", 1)[0] in _GH_API_WRITE_FLAGS for a in args):
        return "no-tracker: only the orchestrator writes to the remote (gh api with a body or a method)"
    return None


def _install_rule(name: str, args: Sequence[str]) -> Optional[str]:
    words = positionals(args[1:])
    reason = "no-install: never install tools, browsers or a new dependency; report the gap"
    if name == "sudo" or name in _SYSTEM_INSTALLERS:
        return reason
    if name == "brew" and words[:1] and words[0] in ("install", "upgrade", "reinstall", "uninstall", "tap"):
        return reason
    if name in _PKG:
        if "-g" in args or "--global" in args or words[:1] == ["global"]:
            return reason
        if words[:1] and words[0] in ("install", "i", "add") and len(words) > 1:
            return reason
    if name == "playwright" and words[:1] == ["install"]:
        return reason
    if name in ("pip", "pip3", "uv", "cargo", "go") and "install" in words[:2]:
        return reason
    if name in ("python", "python3") and "-m" in args and "pip" in args and "install" in args:
        return reason
    return None


def _boot_rule(name: str, args: Sequence[str]) -> Optional[str]:
    words = positionals(args[1:])
    reason = "no-boot: never start an app, API or container; use the running stack named in the brief"
    if name in _PKG:
        script = words[1] if words[:1] == ["run"] and len(words) > 1 else (words[0] if words else "")
        if script in _BOOT_SCRIPTS:
            return reason
    if name in _SERVERS or (name == "pm2" and words[:1] and words[0] in ("start", "restart", "reload")):
        return reason
    if name == "next" and words[:1] and words[0] in ("dev", "start"):
        return reason
    if name == "vite" and (not words or words[0] in ("dev", "serve", "preview")):
        return reason
    if (name, tuple(words[:1])) in (("nest", ("start",)), ("flask", ("run",)), ("rails", ("s",)), ("rails", ("server",))):
        return reason
    if name in ("php", "python", "python3") and ("serve" in words or "runserver" in words):
        return reason
    if name in ("docker", "docker-compose"):
        verbs = [w for w in words if w != "compose"]
        if verbs[:1] and verbs[0] in ("up", "run", "start", "restart"):
            return reason
    return None


def _database_rule(name: str, args: Sequence[str]) -> Optional[str]:
    words = positionals(args[1:])
    reason = "no-database: never point a client or a migration at a database"
    if name in _DB_CLIENTS:
        return reason
    if name == "prisma" and words[:1] and words[0] in ("migrate", "db"):
        return reason
    if name in ("rails", "rake", "sequelize", "sequelize-cli", "typeorm", "knex", "php", "python", "python3"):
        if any(re.match(r"(db|migrate|migration|seed)[:\s]|^(migrate|flush|loaddata)$", w + " ") for w in words):
            return reason
    if name == "alembic" and words[:1] and words[0] in ("upgrade", "downgrade"):
        return reason
    if name == "drizzle-kit" and words[:1] and words[0] in ("push", "migrate"):
        return reason
    return None


def writer_rule(args: Sequence[str]) -> Optional[str]:
    """The rule a builder, fixer or reproducer breaks with this command, or None."""
    name = os.path.basename(args[0])
    if name == "git":
        return _git_rule(args)
    if name == "gh":
        return _gh_rule(args)
    return _install_rule(name, args) or _boot_rule(name, args) or _database_rule(name, args)


def reader_rule(args: Sequence[str]) -> Optional[str]:
    """The rule a reviewer, verifier or learner breaks with this command, or None: they only read."""
    name = os.path.basename(args[0])
    reason = "read-only: this agent reads and reports; `%s` builds, runs, reaches the network or changes files" % name
    if name in _READER_DENIED:
        return reason
    if name == "git":
        sub = git_subcommand(args)
        rest = positionals(args[args.index(sub) + 1:]) if sub in args else []
        listing = (sub in ("worktree", "tag", "remote", "branch") and not rest) or (
            sub in ("stash", "worktree", "remote") and rest[:1] in (["list"], ["show"], ["get-url"]))
        if sub is not None and sub not in _GIT_READS and not listing:
            return "read-only: `git %s` changes the repository" % sub
    if name in ("python", "python3") and "-I" not in args[1:2]:
        return "read-only: only `python3 -I` for counting"
    if name in ("sed", "perl") and any(re.match(r"-[A-Za-z]*i", a) for a in args[1:]):
        return "read-only: an in-place edit changes a file"
    if name == "find" and any(a in ("-delete", "-exec", "-execdir", "-ok") for a in args):
        return "read-only: `find` with an action changes files"
    return None


def write_verdict(agent: str, path: str) -> Optional[str]:
    """Why this agent may not write this file, or None when it may."""
    base = os.path.basename(path)
    parts = path.replace("\\", "/").split("/")
    if agent in WRITERS:
        if base == ".ndev.toml" or path.replace("\\", "/").endswith("docs/architecture/profile.md"):
            return "own-file: n-arch owns the architecture profile and .ndev.toml"
        return None
    allowed = {
        "risk-reviewer": bool(re.fullmatch(r"review(-[a-z]+)?\.md", base)),
        "loop-verifier": base == "verify.md",
        "loop-learner": "knowledge" in parts[:-1] or base in ("lessons.md", "learn.md", "weekly.md"),
    }[agent]
    return None if allowed else "own-file: %s writes only %s" % (agent, _OWN_FILES[agent])
