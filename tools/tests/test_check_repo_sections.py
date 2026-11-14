"""check_repo: `file § Section` references point at a heading that exists."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from repo_tree import PLUGIN, RepoTree  # noqa: E402
from repo_check import sections as cr  # noqa: E402

WORKFLOW = "skills/workflow/SKILL.md"
DEFECT = "skills/n-defect-loop/SKILL.md"
STAGES = "skills/workflow/references/stages.md"
CONFIG = "skills/develop-init/templates/config.md"
NDEV = "skills/n-dev/SKILL.md"
MISS = "ERROR sections: %s:%d %s § %s: no heading of %s starts with these words"
NO_OWNER = "WARN  sections: %s:%d § %s: no owner named, and no heading of this file or of a file it cites matches"


class SectionCase(RepoTree):
    def say(self, rel, sentence):
        self.append(rel, sentence + "\n")
        return len(self.read(rel).splitlines())

    def sections(self):
        return self.found(cr.check_sections)

    def passes(self, rel, sentence):
        self.say(rel, sentence)
        self.assertEqual(self.sections(), [])


class Readmes(SectionCase):
    """The READMEs point at sections too: a reader follows them the same way."""
    README = PLUGIN + "/README.md"
    EVALS = PLUGIN + "/evals/README.md"

    def setUp(self):
        super().setUp()
        self.write(self.README, "# Plugin\n")
        self.write(self.EVALS, "# Evals\n\n## Run\n\nHow to run.\n")

    def test_a_readme_reference_to_a_missing_section_is_an_error(self):
        n = self.say(self.README, "The numbers are in `evals/README.md` § Routing.")
        self.assertEqual(self.sections(), [MISS % (self.README, n, "`evals/README.md`", "Routing", self.EVALS)])

    def test_a_readme_reference_to_a_section_that_exists_passes(self):
        self.passes(self.README, "See `evals/README.md` § Run.")

    def test_the_root_readme_is_read_too(self):
        self.write("README.md", "# Repo\n")
        n = self.say("README.md", "Ask once: `skills/workflow/references/stages.md` § Decision gate.")
        self.assertEqual(self.sections(), [MISS % ("README.md", n, "`skills/workflow/references/stages.md`", "Decision gate", STAGES)])

    def test_a_readme_section_with_no_owner_named_is_left_alone(self):
        self.say(self.README, "Old names (§ Renamed commands) are listed below.")
        self.assertEqual(self.sections(), [])


class NamedFile(SectionCase):
    def test_consistent_tree_passes(self):
        self.assertEqual(self.sections(), [])

    def test_heading_that_does_not_exist(self):
        n = self.say(WORKFLOW, "Ask in `references/stages.md` § Decision gate, once.")
        self.assertEqual(self.sections(), [MISS % (WORKFLOW, n, "`references/stages.md`", "Decision gate, once", STAGES)])

    def test_case_punctuation_and_leading_numbering_are_ignored(self):
        self.passes(WORKFLOW, "`references/stages.md` § decision ROUND; `references/stages.md` § Verify, "
                              "`references/stages.md` § S2 and `references/stages.md` § S2 · Verify.")

    def test_reference_may_stop_before_the_heading_ends(self):
        self.passes(WORKFLOW, "`references/stages.md` § Before every run) and `references/stages.md` § Before.")

    def test_reference_may_run_on_into_the_sentence(self):
        self.passes(WORKFLOW, "Run `references/stages.md` § Decision round after steps 1–3 for every card")

    def test_words_after_the_heading_must_not_replace_it(self):
        n = self.say(WORKFLOW, "Run `references/stages.md` § Decision table after steps 1–3")
        self.assertEqual(self.sections(), [
            MISS % (WORKFLOW, n, "`references/stages.md`", "Decision table after steps 1–3", STAGES)])

    def test_file_named_with_the_w_alias_a_bare_name_or_without_backticks(self):
        self.passes(DEFECT, "`W/references/stages.md` § Never, `stages.md` § S0 (W/references/stages.md § Never)")

    def test_section_sign_wrapped_onto_the_next_line(self):
        self.passes(WORKFLOW, "the round (`references/stages.md`\n§ Decision round) comes first")
        n = self.say(WORKFLOW, "the gate (`references/stages.md`\n  § Decision gate) comes first")
        self.assertEqual(self.sections(), [MISS % (WORKFLOW, n, "`references/stages.md`", "Decision gate", STAGES)])

    def test_file_of_another_skill_named_from_an_agent(self):
        rel = PLUGIN + "/agents/qa.md"
        self.say(rel, "the n-dev skill's `references/extension.md` § Anti-patterns")
        n = self.say(rel, "the n-dev skill's `references/extension.md` § Patterns")
        self.assertEqual(self.sections(), [
            MISS % (rel, n, "`references/extension.md`", "Patterns", "skills/n-dev/references/extension.md")])

    def test_headings_inside_fenced_code_do_not_count(self):
        self.append(STAGES, "\n```\n## Ghost section\n```\n")
        n = self.say(WORKFLOW, "`references/stages.md` § Ghost section")
        self.assertEqual(self.sections(), [MISS % (WORKFLOW, n, "`references/stages.md`", "Ghost section", STAGES)])


class OwnerAliases(SectionCase):
    def test_n_dev_alias(self):
        self.passes(WORKFLOW, "Sort each unknown with n-dev § Questions: a fact is looked up.")
        n = self.say(WORKFLOW, "stricter than n-dev § Answers.")
        self.assertEqual(self.sections(), [MISS % (WORKFLOW, n, "n-dev", "Answers", NDEV)])

    def test_config_alias_in_every_spelling(self):
        self.passes(WORKFLOW, "config § Checks e2e lines; Config § Auto mode › never-touch; `DC/config.md` § "
                              "Dev flow's ready query (config.md § Checks) <config § Auto mode>")
        n = self.say(WORKFLOW, "Push per config § Push policy, or ask.")
        self.assertEqual(self.sections(), [MISS % (WORKFLOW, n, "config", "Push policy, or ask", CONFIG)])

    def test_w_skill_md_is_the_workflow_skill(self):
        n = self.say(DEFECT, "`W/SKILL.md` § Handoffs; then `W/SKILL.md` § Tracker.")
        self.assertEqual(self.sections(), [MISS % (DEFECT, n, "`W/SKILL.md`", "Tracker", WORKFLOW)])

    def test_skill_md_inside_a_skills_own_reference(self):
        rel = "skills/n-dev/references/extension.md"
        self.say(rel, "a decision for the round (`SKILL.md` § Questions)")
        n = self.say(rel, "see `SKILL.md` § Steps")
        self.assertEqual(self.sections(), [MISS % (rel, n, "`SKILL.md`", "Steps", NDEV)])


class NoOwner(SectionCase):
    def test_heading_of_the_same_file(self):
        self.passes(WORKFLOW, "One owner at a time (§ Handoffs).")

    def test_owner_carried_from_a_reference_the_document_makes_elsewhere(self):
        self.say(DEFECT, "Adjust it as `W/templates/auto-comments.md` § Proof comment says.")
        self.passes(DEFECT, "Then post § hand-off; config § Checks and § Dev flow apply.")

    def test_no_matching_heading_anywhere_is_a_warning(self):
        n = self.say(WORKFLOW, "Then post § stale-lock and wait.")
        self.assertEqual(self.sections(), [NO_OWNER % (WORKFLOW, n, "stale-lock and wait")])


class RealCorpusShapes(SectionCase):
    """Shapes the first run on this repo reported although the target exists."""

    def test_owner_named_earlier_on_the_same_line(self):
        self.passes(WORKFLOW, "| `config.md` | every project fact: checks, team, § Dev flow, § Auto mode | init |")
        self.passes(STAGES, "- n-dev scope dial and § Questions (what counts as a decision): `../n-dev/SKILL.md`")

    def test_owner_named_on_another_line_does_not_count(self):
        self.say(WORKFLOW, "Read `templates/auto-comments.md` first.")
        n = self.say(WORKFLOW, "Then post § hand-off.")
        self.assertEqual(self.sections(), [NO_OWNER % (WORKFLOW, n, "hand-off")])

    def test_bold_lead_of_a_paragraph_list_item_or_table_row_is_an_anchor(self):
        self.append(STAGES, "\n**By-design answers.** Not final.\n\n- **Wording rule**: plain words.\n\n"
                            "| **Input size and time** | bounded? |\n")
        self.passes(WORKFLOW, "(`references/stages.md` § By-design answers), `references/stages.md` § Wording rule "
                              "and (`references/stages.md` § Input size and time)")

    def test_bold_inside_a_sentence_is_not_an_anchor(self):
        self.append(STAGES, "\nThe **Hidden rule** applies.\n")
        n = self.say(WORKFLOW, "`references/stages.md` § Hidden rule")
        self.assertEqual(self.sections(), [MISS % (WORKFLOW, n, "`references/stages.md`", "Hidden rule", STAGES)])

    def test_legacy_name_of_a_config_section_is_not_reported(self):
        self.passes(WORKFLOW, "a 0.5–0.6 config § AI loop becomes § Auto mode (a legacy § AI loop is migrated)")


class Unresolved(SectionCase):
    def test_file_that_cannot_be_found_is_a_warning(self):
        n = self.say(WORKFLOW, "See `nowhere.md` § Thing.")
        self.assertEqual(self.sections(), [
            "WARN  sections: %s:%d `nowhere.md` § Thing: cannot resolve the owner file (0 candidates)" % (WORKFLOW, n)])

    def test_name_that_several_skills_hold_is_a_warning(self):
        rel = PLUGIN + "/agents/qa.md"
        n = self.say(rel, "Its `SKILL.md` § Questions decides.")
        self.assertEqual(self.sections(), [
            "WARN  sections: %s:%d `SKILL.md` § Questions decides: cannot resolve the owner file (5 candidates)" % (rel, n)])


class NotChecked(SectionCase):
    def test_target_project_files_and_placeholders(self):
        self.passes(WORKFLOW, "`DL/lessons.md` § Rules, `docs/features/<area>.md` § Rules, `<doc>` § Anything")

    def test_numbered_sections(self):
        self.passes(WORKFLOW, "`references/stages.md` §1, §2–6 and §5.16; the comment's §3 carries it")

    def test_fenced_code(self):
        self.passes(WORKFLOW, "```\n`references/stages.md` § Nothing here\n```")


if __name__ == "__main__":
    unittest.main()
