"""The session-start line: one short line that sends a plain code request to n-dev, and names only real skills."""
import json
import os
import re
import subprocess
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
HOOKS = os.path.join(HERE, "..")
PLUGIN = os.path.join(HOOKS, "..")
LINE = os.path.join(HOOKS, "session-start.txt")


def line_text():
    with open(LINE, encoding="utf-8") as fh:
        return fh.read()


def session_start_commands():
    with open(os.path.join(HOOKS, "hooks.json"), encoding="utf-8") as fh:
        groups = json.load(fh)["hooks"]["SessionStart"]
    return [hook["command"] for group in groups for hook in group["hooks"]]


class TheLine(unittest.TestCase):
    def test_it_is_one_short_line(self):
        text = line_text()
        self.assertEqual(text.count("\n"), 1, "one line, ending in a newline")
        self.assertLessEqual(len(text), 400, "every session pays for this line: keep it short")

    def test_it_sends_a_code_change_to_n_dev_before_the_first_edit(self):
        text = line_text()
        self.assertIn("changes code or tests", text)
        self.assertIn("Skill tool", text)
        self.assertIn("90north-develop:n-dev,", text)
        self.assertIn("before the first file is read or edited", text)

    def test_it_leaves_board_work_to_the_loops(self):
        text = line_text()
        for loop in ("90north-develop:n-defect-loop", "90north-develop:n-develop-loop", "90north-develop:workflow"):
            self.assertIn(loop, text)
        self.assertIn("board key", text)

    def test_every_skill_it_names_is_in_the_plugin(self):
        named = set(re.findall(r"90north-develop:([a-z-]+)", line_text()))
        self.assertTrue(named)
        for skill in sorted(named):
            path = os.path.join(PLUGIN, "skills", skill, "SKILL.md")
            self.assertTrue(os.path.isfile(path), "session-start.txt names a skill the plugin does not have: " + skill)


class TheHook(unittest.TestCase):
    def test_the_hook_prints_the_line_the_way_claude_code_runs_it(self):
        commands = session_start_commands()
        self.assertEqual(len(commands), 1)
        env = dict(os.environ, CLAUDE_PLUGIN_ROOT=os.path.abspath(PLUGIN))
        proc = subprocess.run(["sh", "-c", commands[0]], capture_output=True, text=True, env=env)
        self.assertEqual((proc.returncode, proc.stderr), (0, ""))
        self.assertEqual(proc.stdout, line_text())

    def test_a_plugin_folder_with_spaces_in_its_path_still_works(self):
        command = session_start_commands()[0]
        self.assertIn('"${CLAUDE_PLUGIN_ROOT}/hooks/session-start.txt"', command)


if __name__ == "__main__":
    unittest.main()
