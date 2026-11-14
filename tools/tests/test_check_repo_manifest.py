"""check_repo: versions, registered agents, plugin skill links and the README skill table."""
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from repo_tree import PLUGIN, RepoTree  # noqa: E402
from repo_check import runner as cr  # noqa: E402

MANIFEST = PLUGIN + "/.claude-plugin/plugin.json"
MARKET = ".claude-plugin/marketplace.json"


class Versions(RepoTree):
    def test_equal_versions_pass(self):
        self.assertEqual(self.found(cr.check_versions), [])

    def test_plugin_json_ahead_of_the_marketplace(self):
        self.set_json(MANIFEST, version="1.3.0")
        self.assertEqual(self.found(cr.check_versions), [
            "ERROR version: .claude-plugin/marketplace.json says 1.2.3, %s says 1.3.0" % MANIFEST])

    def test_plugin_missing_from_the_marketplace(self):
        self.write(MARKET, json.dumps({"plugins": [{"name": "other-plugin", "version": "1.2.3"}]}))
        self.assertEqual(self.found(cr.check_versions), [
            "ERROR version: .claude-plugin/marketplace.json has no plugin named 90north-develop"])

    def test_unreadable_manifest_is_a_finding_not_a_crash(self):
        self.write(MANIFEST, "{not json")
        self.assertEqual(self.found(cr.check_versions), ["ERROR version: cannot read %s as JSON" % MANIFEST])


class AgentsRegistered(RepoTree):
    def test_every_agent_file_registered_passes(self):
        self.assertEqual(self.found(cr.check_agents_registered), [])

    def test_agent_file_that_is_not_registered(self):
        self.write(PLUGIN + "/agents/risk-reviewer.md", "new agent\n")
        self.assertEqual(self.found(cr.check_agents_registered), [
            "ERROR agents: %s/agents/risk-reviewer.md is not in plugin.json's agents array, "
            "so the plugin does not load it" % PLUGIN])

    def test_registered_agent_without_a_file(self):
        os.remove(self.path(PLUGIN, "agents", "qa.md"))
        self.assertEqual(self.found(cr.check_agents_registered), [
            "ERROR agents: plugin.json registers ./agents/qa.md, which does not exist"])

    def test_entry_written_without_the_leading_dot_still_counts(self):
        self.set_json(MANIFEST, agents=["agents/dev-builder.md", "./agents/qa.md"])
        self.assertEqual(self.found(cr.check_agents_registered), [])

    def test_missing_agents_array(self):
        self.set_json(MANIFEST, agents=None)
        self.assertEqual(self.found(cr.check_agents_registered), [
            "ERROR agents: %s has no agents array" % MANIFEST,
            "ERROR agents: %s/agents/dev-builder.md is not in plugin.json's agents array, "
            "so the plugin does not load it" % PLUGIN,
            "ERROR agents: %s/agents/qa.md is not in plugin.json's agents array, "
            "so the plugin does not load it" % PLUGIN])


class PluginSkills(RepoTree):
    def unlink(self, name):
        os.remove(self.path(PLUGIN, "skills", name))

    def test_links_and_layout_list_pass(self):
        self.assertEqual(self.found(cr.check_plugin_skills), [])

    def test_copied_folder_instead_of_a_symlink(self):
        self.unlink("n-dev")
        self.write(PLUGIN + "/skills/n-dev/SKILL.md", "copy\n")
        self.assertEqual(self.found(cr.check_plugin_skills), [
            "ERROR plugin-skills: %s/skills/n-dev is not a symlink" % PLUGIN])

    def test_link_to_a_folder_that_does_not_exist(self):
        self.unlink("n-dev")
        self.link("n-dev", "../../../skills/n-devv")
        self.assertEqual(self.found(cr.check_plugin_skills), [
            "ERROR plugin-skills: %s/skills/n-dev -> ../../../skills/n-devv does not resolve to skills/n-dev/"
            % PLUGIN])

    def test_link_to_another_skill(self):
        self.unlink("n-dev")
        self.link("n-dev", "../../../skills/workflow")
        self.assertEqual(self.found(cr.check_plugin_skills), [
            "ERROR plugin-skills: %s/skills/n-dev -> ../../../skills/workflow does not resolve to skills/n-dev/"
            % PLUGIN])

    def test_linked_skill_without_skill_md(self):
        os.remove(self.path("skills", "n-dev", "SKILL.md"))
        self.assertEqual(self.found(cr.check_plugin_skills), [
            "ERROR plugin-skills: skills/n-dev/ has no SKILL.md"])

    def test_skill_in_the_readme_layout_but_not_linked(self):
        self.unlink("develop-init")
        self.assertEqual(self.found(cr.check_plugin_skills), [
            "ERROR plugin-skills: %s/README.md's layout names skills/develop-init, which is not in %s/skills/"
            % (PLUGIN, PLUGIN)])

    def test_readme_without_a_layout_list(self):
        self.write(PLUGIN + "/README.md", "# plugin\n")
        self.assertEqual(self.found(cr.check_plugin_skills), [
            "ERROR plugin-skills: %s/README.md has no layout list (lines like 'skills/<name> -> …')" % PLUGIN])


class ReadmeSkills(RepoTree):
    def test_every_skill_linked_passes(self):
        self.assertEqual(self.found(cr.check_readme_skills), [])

    def test_skill_missing_from_the_table(self):
        self.write("skills/n-arch/SKILL.md", "# n-arch\n")
        self.assertEqual(self.found(cr.check_readme_skills), [
            "ERROR readme: skills/n-arch/SKILL.md is not linked from README.md's skill table"])

    def test_link_outside_a_table_row_does_not_count(self):
        self.write("skills/n-arch/SKILL.md", "# n-arch\n")
        self.append("README.md", "\nSee also [n-arch](skills/n-arch/SKILL.md).\n")
        self.assertEqual(self.found(cr.check_readme_skills), [
            "ERROR readme: skills/n-arch/SKILL.md is not linked from README.md's skill table"])

    def test_folder_without_skill_md_is_not_a_skill(self):
        self.write("skills/drafts/notes.md", "wip\n")
        self.assertEqual(self.found(cr.check_readme_skills), [])


if __name__ == "__main__":
    unittest.main()
