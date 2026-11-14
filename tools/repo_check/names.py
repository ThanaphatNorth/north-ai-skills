"""Check h: every plugin-qualified name in the skills and agents is an agent or a skill the plugin holds."""
from __future__ import annotations

import os
import re
from typing import List

from .model import PLUGIN, PLUGIN_NAME, Finding, docs, error

QUALIFIED_NAME = re.compile(r"(/?)%s:([A-Za-z0-9_-]+)" % re.escape(PLUGIN_NAME))  # a leading "/" = slash command


def check_agent_names(repo: str) -> List[Finding]:
    """An error per `90north-develop:<name>` in the skills or agents that is not a plugin agent,
    and per `/90north-develop:<name>` (a slash command) that is not a plugin skill."""
    out = []
    for doc in docs(repo):
        for number, line in enumerate(doc.text.splitlines(), 1):
            for slash, name in QUALIFIED_NAME.findall(line):
                owner = "%s/skills/%s" % (PLUGIN, name) if slash else "%s/agents/%s.md" % (PLUGIN, name)
                if not os.path.exists(os.path.join(repo, owner)):
                    out.append(error("agent-names", "%s:%d names %s%s:%s, but %s does not exist"
                                     % (doc.rel, number, slash, PLUGIN_NAME, name, owner)))
    return out
