"""check_repo end to end: the real CLI on a fixture tree, its lines and its exit code."""
import os
import subprocess
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from repo_tree import PLUGIN, SCRIPT, TOOLS, RepoTree  # noqa: E402
import check_repo as cr  # noqa: E402

MANIFEST = PLUGIN + "/.claude-plugin/plugin.json"


class Cli(RepoTree):
    def cli(self, *args):
        proc = subprocess.run([sys.executable, "-I", SCRIPT, *(args or ("--repo", self.repo))],
                              capture_output=True, text=True)
        return proc.returncode, proc.stdout.splitlines()

    def test_consistent_tree_passes(self):
        self.assertEqual(self.cli(), (0, ["RESULT: PASS (0 errors, 0 warnings)"]))

    def test_errors_fail_the_run_and_follow_the_warnings(self):
        self.set_json(MANIFEST, version="1.3.0")
        self.append("skills/workflow/SKILL.md", "See `mystery.md` and `references/gone.md`.\n")
        self.append("skills/n-dev/SKILL.md", "Dispatch `90north-develop:ghost`.\n")
        self.assertEqual(self.cli(), (1, [
            "WARN  paths: skills/workflow/SKILL.md:11 `mystery.md` is not found in this repo and is not on the skip list",
            "ERROR version: .claude-plugin/marketplace.json says 1.2.3, %s says 1.3.0" % MANIFEST,
            "ERROR paths: skills/workflow/SKILL.md:11 `references/gone.md` does not exist",
            "ERROR agent-names: skills/n-dev/SKILL.md:6 names 90north-develop:ghost, "
            "but %s/agents/ghost.md does not exist" % PLUGIN,
            "RESULT: FAIL (3 errors, 1 warnings)"]))

    def test_warnings_alone_pass(self):
        self.append("skills/workflow/SKILL.md", "Then post § stale-lock.\n")
        code, lines = self.cli()
        self.assertEqual((code, lines[-1], len(lines)), (0, "RESULT: PASS (0 errors, 1 warnings)", 2))

    def test_every_check_runs(self):
        self.write("skills/n-arch/SKILL.md", "# n-arch\n")                      # d: not in the README table
        self.write(PLUGIN + "/agents/new.md", "new\n")                          # b: not registered
        os.remove(self.path(PLUGIN, "skills", "n-dev"))                          # c: layout names it
        self.append("skills/n-defect-loop/SKILL.md", "| x | `limbo` | - | - |\n")  # g: not a parked state
        self.append("skills/workflow/SKILL.md", "See `references/stages.md` § Nope.\n")  # f
        code, lines = self.cli()
        self.assertEqual(code, 1)
        self.assertEqual([line.split(":")[0] for line in lines[:-1]], [
            "ERROR agents", "ERROR plugin-skills", "ERROR readme", "ERROR sections", "ERROR ledger"])

    def test_default_repo_is_the_one_that_holds_the_script(self):
        self.assertEqual(cr.default_repo(), os.path.dirname(TOOLS))


if __name__ == "__main__":
    unittest.main()
