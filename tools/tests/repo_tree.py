"""Shared fixture: a small, consistent copy of this repo's layout in a temp folder."""
import json
import os
import shutil
import sys
import tempfile
import unittest

TOOLS = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SCRIPT = os.path.join(TOOLS, "check_repo.py")
sys.path.insert(0, TOOLS)

from repo_check.report import format_finding  # noqa: E402

PLUGIN = "plugins/90north-develop"
SKILLS = ("workflow", "n-dev", "develop-init", "n-defect-loop", "n-develop-loop")
GATES = """## Gates — where a card waits

| Gate | Ledger state | Attended | Auto |
|---|---|---|---|
| missing information | `needs-info` | a comment | a question |
| change request | `handed-to-n-develop-loop` | hand-off row | hand-off label |
| PR open | `ready-for-qa` (auto: `in-review`) | a person reviews | the same |
"""
STAGES = """# Shared stages

## S0 · Before every run (cheap, mandatory)

1. No `DL/config.md` → stop.
2. Read the lessons.
3. Read the ledger. A work item whose last row is a parked state (`ready-for-qa`, `in-review`, `needs-info`, `handed-to-<loop>`, and auto mode's `stopped`) is skipped unless the tracker changed (`gh pr view N`).

## Decision round · every question once (attended)

Ask once.

## S2 · Verify — review and QA in parallel

Review it.

## Never (every loop)

- Push without a yes.
"""
FILES = {
    ".claude-plugin/marketplace.json": json.dumps({"plugins": [
        {"name": "other-plugin", "version": "9.9.9"}, {"name": "90north-develop", "version": "1.2.3"}]}),
    PLUGIN + "/.claude-plugin/plugin.json": json.dumps({
        "name": "90north-develop", "version": "1.2.3", "agents": ["./agents/dev-builder.md", "./agents/qa.md"]}),
    PLUGIN + "/agents/dev-builder.md": "Read the n-dev skill: its `SKILL.md` and `references/extension.md`.\n",
    PLUGIN + "/agents/qa.md": "Runs the checks in config § Checks.\n",
    PLUGIN + "/README.md": "# plugin\n\n## Layout\n\n```\n" + "".join(
        "  skills/%-14s -> ../../../skills/%s\n" % (s, s) for s in SKILLS) + "```\n",
    "README.md": "# skills\n\n| Skill | What |\n|---|---|\n" + "".join(
        "| [`%s`](skills/%s/SKILL.md) | does things |\n" % (s, s) for s in SKILLS),
    "skills/workflow/SKILL.md": "# workflow\n\n## Route the work\n\nSee `references/stages.md` § Decision round.\n"
                                "Run `scripts/tracker.sh get KEY`.\n\n## Handoffs between the loops\n\nOne owner.\n",
    "skills/workflow/references/stages.md": STAGES,
    "skills/workflow/templates/auto-comments.md": "# Comments\n\n## Proof comment\n\nText.\n\n## hand-off\n\nText.\n",
    "skills/workflow/scripts/tracker.sh": "#!/usr/bin/env bash\n",
    "skills/n-dev/SKILL.md": "# n-dev\n\n## Questions: one round, before the first edit\n\nSee `references/extension.md`.\n",
    "skills/n-dev/references/extension.md": "# Extension\n\n## Anti-patterns\n\nNone.\n",
    "skills/develop-init/SKILL.md": "# develop-init\n\nWrites `DL/config.md` from `templates/config.md`.\n",
    "skills/develop-init/templates/config.md": "# config\n\n## Checks (QA runs all)\n\n## Dev flow (n-develop-loop)\n\n"
                                               "## Auto mode (both loops)\n",
    "skills/n-defect-loop/SKILL.md": "# n-defect-loop\n\n`W = ../workflow/`. Read `W/references/stages.md` § S0 and "
                                     "`stages.md` § Never. Dispatch `90north-develop:dev-builder`.\n\n" + GATES,
    "skills/n-develop-loop/SKILL.md": "# n-develop-loop\n\nRoute with `W/SKILL.md` § Route the work; ask per "
                                      "n-dev § Questions. Run `/90north-develop:develop-init` first.\n\n"
                                      + GATES.replace("handed-to-n-develop-loop", "handed-to-n-defect-loop"),
}


class RepoTree(unittest.TestCase):
    """A consistent tree; each test breaks one thing and reads the findings of one check."""

    def setUp(self):
        self.repo = tempfile.mkdtemp(prefix="check-repo-")
        for rel, text in FILES.items():
            self.write(rel, text)
        os.makedirs(self.path(PLUGIN, "skills"))
        for name in SKILLS:
            self.link(name)

    def tearDown(self):
        shutil.rmtree(self.repo, ignore_errors=True)

    def path(self, *parts):
        return os.path.join(self.repo, *parts)

    def write(self, rel, text):
        os.makedirs(os.path.dirname(self.path(rel)), exist_ok=True)
        with open(self.path(rel), "w", encoding="utf-8") as fh:
            fh.write(text)

    def read(self, rel):
        with open(self.path(rel), encoding="utf-8") as fh:
            return fh.read()

    def edit(self, rel, old, new):
        text = self.read(rel)
        self.assertIn(old, text)
        self.write(rel, text.replace(old, new))

    def append(self, rel, text):
        self.write(rel, self.read(rel) + text)

    def link(self, name, target=None):
        os.symlink(target or os.path.join("..", "..", "..", "skills", name), self.path(PLUGIN, "skills", name))

    def set_json(self, rel, **changes):
        data = json.loads(self.read(rel))
        data.update(changes)
        self.write(rel, json.dumps(data))

    def found(self, check):
        """The findings of one check as printed lines."""
        return [format_finding(f) for f in check(self.repo)]
