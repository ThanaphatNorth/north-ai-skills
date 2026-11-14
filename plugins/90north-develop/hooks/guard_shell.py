"""Read a shell line the way the guard needs it: one argv list per simple command. Pure, no rules in here."""
from __future__ import annotations

import os
import re
import shlex
from typing import List, Optional, Sequence

_SPLIT = set("();|&")
_ENV = re.compile(r"[A-Za-z_][A-Za-z0-9_]*=")
SHELLS = {"sh", "bash", "zsh", "dash", "ksh"}
_WRAPPERS = {"env", "command", "exec", "nohup", "time", "nice", "stdbuf", "timeout", "xargs", "caffeinate"}
RUNNERS = {"npx", "bunx", "pnpx"}
_HEREDOC = re.compile(r"<<-?\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\1")
_GIT_VALUE_OPTIONS = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path", "--super-prefix"}


def simple_commands(command: str) -> List[List[str]]:
    """Every simple command of a shell line as an argv list, split at operators, substitutions and new lines."""
    text = command.replace("\n", " ; ").replace("`", " ; ")
    try:
        lexer = shlex.shlex(text, posix=True, punctuation_chars=True)
        lexer.whitespace_split = True
        tokens = list(lexer)
    except ValueError:  # an unbalanced quote: fall back to a plain split, so the line is still checked
        tokens = re.sub(r"([();|&])", r" \1 ", text.replace('"', " ").replace("'", " ")).split()
    commands: List[List[str]] = [[]]
    for token in tokens:
        if token and set(token) <= _SPLIT:
            commands.append([])
        else:
            commands[-1].append(token)
    return [c for c in commands if c]


def unwrap(argv: Sequence[str]) -> List[str]:
    """argv without leading VAR=value assignments and wrappers such as env, timeout, xargs or exec."""
    args = list(argv)
    while args:
        head = os.path.basename(args[0])
        if _ENV.match(args[0]) or args[0] in ("$", "{", "}", "!"):
            args = args[1:]
        elif head in _WRAPPERS:
            args = args[1:]
            while args and (args[0].startswith("-") or _ENV.match(args[0]) or re.fullmatch(r"[0-9.]+[smhd]?", args[0])):
                args = args[1:]
        else:
            break
    return args


def git_subcommand(args: Sequence[str]) -> Optional[str]:
    """The git subcommand in `git [global options] <subcommand> …`, or None when there is none."""
    i = 1
    while i < len(args):
        if args[i] in _GIT_VALUE_OPTIONS:
            i += 2
        elif args[i].startswith("-"):
            i += 1
        else:
            return args[i]
    return None


def has_short(args: Sequence[str], letter: str) -> bool:
    return any(re.fullmatch(r"-[A-Za-z]*%s[A-Za-z]*" % letter, a) for a in args)


def positionals(args: Sequence[str]) -> List[str]:
    return [a for a in args if not a.startswith("-")]


def drop_heredoc_text(command: str) -> str:
    """The shell line without the text of its here-documents, which is data, unless a shell reads it as a script."""
    lines = command.split("\n")
    kept: List[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        kept.append(line)
        i += 1
        mark = _HEREDOC.search(line)
        if not mark:
            continue
        reader = unwrap(line.split())
        is_script = bool(reader) and os.path.basename(reader[0]) in SHELLS
        while i < len(lines) and lines[i].strip() != mark.group(2):
            if is_script:
                kept.append(lines[i])
            i += 1
        i += 1  # the line that ends the here-document
    return "\n".join(kept)
