"""check_repo: ledger states of the Gates tables, and plugin-qualified agent and skill names."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from repo_tree import PLUGIN, RepoTree  # noqa: E402
from repo_check import runner as cr  # noqa: E402

DEFECT = "skills/n-defect-loop/SKILL.md"
DEVELOP = "skills/n-develop-loop/SKILL.md"
STAGES = "skills/workflow/references/stages.md"
NOT_PARKED = "ERROR ledger: %s § Gates: `%s` is not a parked state in " + STAGES + " § S0 item 3"


class LedgerStates(RepoTree):
    def add_gate(self, rel, cell, attended="waits"):
        self.append(rel, "| extra gate | %s | %s | waits |\n" % (cell, attended))

    def test_states_in_the_parked_list_pass(self):
        self.assertEqual(self.found(cr.check_ledger_states), [])

    def test_state_missing_from_the_parked_list(self):
        self.add_gate(DEFECT, "`awaiting-push`")
        self.assertEqual(self.found(cr.check_ledger_states), [NOT_PARKED % (DEFECT, "awaiting-push")])

    def test_both_loops_and_every_state_in_a_cell_are_checked(self):
        self.add_gate(DEVELOP, "`blocked-needs-human` / `stopped` (auto: `solution-posted`)")
        self.assertEqual(self.found(cr.check_ledger_states), [
            NOT_PARKED % (DEVELOP, "blocked-needs-human"), NOT_PARKED % (DEVELOP, "solution-posted")])

    def test_placeholder_in_the_parked_list_matches_any_loop(self):
        self.add_gate(DEFECT, "`handed-to-some-new-loop`")
        self.assertEqual(self.found(cr.check_ledger_states), [])

    def test_from_hand_off_rows_are_exempt(self):
        self.add_gate(DEFECT, "`from-n-develop-loop`")
        self.assertEqual(self.found(cr.check_ledger_states), [])

    def test_code_in_other_columns_is_not_a_state(self):
        self.add_gate(DEFECT, "`needs-info`", attended="run `gh pr view N`")
        self.assertEqual(self.found(cr.check_ledger_states), [])

    def test_state_named_elsewhere_in_stages_is_still_not_parked(self):
        self.append(STAGES, "\nA card may sit in `awaiting-push`.\n")
        self.add_gate(DEFECT, "`awaiting-push`")
        self.assertEqual(self.found(cr.check_ledger_states), [NOT_PARKED % (DEFECT, "awaiting-push")])

    def test_missing_gates_table(self):
        self.edit(DEFECT, "| Gate | Ledger state |", "| Gate | State |")
        self.assertEqual(self.found(cr.check_ledger_states), [
            "ERROR ledger: %s has no Gates table with a 'Ledger state' column" % DEFECT])

    def test_missing_parked_list(self):
        self.edit(STAGES, "is a parked state (", "is parked (")
        self.assertEqual(self.found(cr.check_ledger_states), [
            "ERROR ledger: %s § S0 item 3 has no 'parked state (…)' list" % STAGES])


class AgentNames(RepoTree):
    def test_known_agent_and_skill_command_pass(self):
        self.assertEqual(self.found(cr.check_agent_names), [])

    def test_agent_that_does_not_exist(self):
        self.append("skills/workflow/SKILL.md", "\nDispatch `90north-develop:ghost` twice.\n")
        self.assertEqual(self.found(cr.check_agent_names), [
            "ERROR agent-names: skills/workflow/SKILL.md:12 names 90north-develop:ghost, "
            "but %s/agents/ghost.md does not exist" % PLUGIN])

    def test_names_in_agents_references_and_templates_are_read_too(self):
        self.append(PLUGIN + "/agents/qa.md", "Hand over to 90north-develop:nobody.\n")
        self.append("skills/workflow/references/stages.md", "Use `90north-develop:missing-a`.\n")
        self.append("skills/workflow/templates/auto-comments.md", "By 90north-develop:missing-b\n")
        self.assertEqual([line.split(" names ")[1].split(",")[0] for line in self.found(cr.check_agent_names)], [
            "90north-develop:missing-a", "90north-develop:missing-b", "90north-develop:nobody"])

    def test_slash_command_must_be_a_plugin_skill(self):
        self.append("skills/n-dev/SKILL.md", "\nRun `/90north-develop:n-arch` and `/90north-develop:workflow`.\n")
        self.assertEqual(self.found(cr.check_agent_names), [
            "ERROR agent-names: skills/n-dev/SKILL.md:7 names /90north-develop:n-arch, "
            "but %s/skills/n-arch does not exist" % PLUGIN])

    def test_skill_name_without_the_slash_is_not_an_agent(self):
        self.append("skills/n-dev/SKILL.md", "\nDispatch `90north-develop:workflow`.\n")
        self.assertEqual(self.found(cr.check_agent_names), [
            "ERROR agent-names: skills/n-dev/SKILL.md:7 names 90north-develop:workflow, "
            "but %s/agents/workflow.md does not exist" % PLUGIN])

    def test_placeholders_are_skipped(self):
        self.append("skills/n-dev/SKILL.md", "\n`/loop 30m /90north-develop:<loop>` or `90north-develop:<name>`\n")
        self.assertEqual(self.found(cr.check_agent_names), [])


if __name__ == "__main__":
    unittest.main()
