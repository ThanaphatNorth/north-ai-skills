"""check_repo: backticked repo paths in skills and agents resolve to files."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from repo_tree import PLUGIN, RepoTree  # noqa: E402
from repo_check import paths as cr  # noqa: E402

WORKFLOW = "skills/workflow/SKILL.md"
MISSING = "ERROR paths: %s:%d `%s` does not exist"
UNKNOWN = "WARN  paths: %s:%d `%s` is not found in this repo and is not on the skip list"


class Paths(RepoTree):
    def say(self, rel, sentence):
        """Appends one line to a file and returns its line number."""
        self.append(rel, sentence + "\n")
        return len(self.read(rel).splitlines())

    def paths(self):
        return self.found(cr.check_paths)

    def test_consistent_tree_passes(self):
        self.assertEqual(self.paths(), [])

    def test_missing_file_named_in_a_skill_md(self):
        n = self.say(WORKFLOW, "Then open `references/gone.md`.")
        self.assertEqual(self.paths(), [MISSING % (WORKFLOW, n, "references/gone.md")])

    def test_references_templates_and_agents_are_read_too(self):
        a = self.say("skills/workflow/references/stages.md", "See `templates/gone.md`.")
        b = self.say("skills/workflow/templates/auto-comments.md", "See `scripts/gone.sh`.")
        c = self.say(PLUGIN + "/agents/qa.md", "Read `references/nowhere.md`.")
        self.assertEqual(self.paths(), [
            MISSING % ("skills/workflow/references/stages.md", a, "templates/gone.md"),
            MISSING % ("skills/workflow/templates/auto-comments.md", b, "scripts/gone.sh"),
            MISSING % (PLUGIN + "/agents/qa.md", c, "references/nowhere.md")])

    def test_w_alias_resolves_to_the_workflow_skill(self):
        rel = "skills/n-defect-loop/SKILL.md"
        self.say(rel, "`W/templates/auto-comments.md` and `W/scripts/tracker.sh` and `W/../n-dev/`")
        n = self.say(rel, "`W/references/gone.md`")
        self.assertEqual(self.paths(), [MISSING % (rel, n, "W/references/gone.md")])

    def test_parent_paths_resolve_from_the_skill_folder_or_the_file(self):
        self.say(WORKFLOW, "`../n-dev/SKILL.md`, `../n-dev/` and `../develop-init/templates/config.md`")
        self.say("skills/workflow/templates/auto-comments.md", "`../references/stages.md`")
        n = self.say(WORKFLOW, "`../n-dev/references/gone.md`")
        self.assertEqual(self.paths(), [MISSING % (WORKFLOW, n, "../n-dev/references/gone.md")])

    def test_bare_name_is_looked_up_beside_the_file_and_inside_the_skill(self):
        self.write("skills/workflow/references/trackers.md", "# Trackers\n\n`stages.md`, `tracker.sh`, `SKILL.md`\n")
        self.say(WORKFLOW, "`stages.md` and `auto-comments.md` and `tracker.sh`")
        self.assertEqual(self.paths(), [])

    def test_bare_name_found_nowhere_is_a_warning(self):
        n = self.say(WORKFLOW, "`mystery.md` and `helper.py --fast`")
        self.assertEqual(self.paths(), [UNKNOWN % (WORKFLOW, n, "mystery.md"), UNKNOWN % (WORKFLOW, n, "helper.py")])

    def test_another_skills_file_named_by_its_folder_path(self):
        rel = "skills/develop-init/SKILL.md"
        self.say(rel, "rows: n-dev's `references/extension.md`; the tracker: `tracker.sh card`")
        n = self.say(rel, "the workflow skill's `references/trackers.md`")
        self.assertEqual(self.paths(), [MISSING % (rel, n, "references/trackers.md")])

    def test_paths_from_the_repo_root_and_the_skills_folder(self):
        self.write("research/notes.md", "notes\n")
        self.say(WORKFLOW, "`research/notes.md` and `n-dev/references/extension.md` and `skills/n-dev/SKILL.md`")
        self.assertEqual(self.paths(), [])

    def test_program_of_a_backticked_command_is_checked(self):
        self.say(WORKFLOW, "`bash W/scripts/tracker.sh get <KEY>` and `scripts/tracker.sh search 'x'`")
        n = self.say(WORKFLOW, "`python3 scripts/gone.py --all`")
        self.assertEqual(self.paths(), [MISSING % (WORKFLOW, n, "scripts/gone.py")])

    def test_later_words_of_a_command_are_not_paths(self):
        self.say(WORKFLOW, "`comment KEY comment.md [id]` and `W = ../workflow/` and `git add scripts/gone.py`")
        self.assertEqual(self.paths(), [])

    def test_glob_must_match_something(self):
        self.say(WORKFLOW, "`references/*.md` and `stage*.md`")
        n = self.say(WORKFLOW, "`references/zz-*.md`")
        self.assertEqual(self.paths(), [MISSING % (WORKFLOW, n, "references/zz-*.md")])

    def test_each_path_is_reported_once_per_file(self):
        n = self.say(WORKFLOW, "`references/gone.md` twice `references/gone.md`")
        self.say(WORKFLOW, "and again `references/gone.md`")
        self.assertEqual(self.paths(), [MISSING % (WORKFLOW, n, "references/gone.md")])

    def test_fenced_code_blocks_are_not_read(self):
        self.say(WORKFLOW, "```bash\npython3 `scripts/gone.py`\n```\n~~~\n`references/gone.md`\n~~~")
        self.assertEqual(self.paths(), [])


class TargetProjectPaths(RepoTree):
    def clean(self, sentence):
        self.append("skills/workflow/SKILL.md", sentence + "\n")
        self.assertEqual(self.found(cr.check_paths), [])

    def test_placeholders_and_urls(self):
        self.clean("`<scratchpad>/<KEY>/qa.md` `references/<name>.md` `scripts/{tool}.py` `https://x.dev/files.json`")

    def test_target_project_folders(self):
        self.clean("`docs/features/billing.md` `.claude/launch.json` `DL/lessons.md` `~/notes.md` `src/app.py` "
                   "`board/TASK-1.md` `/etc/hosts.json`")

    def test_run_files_and_state_files_by_bare_name(self):
        self.clean("`triage.md` `card.md` `before.md` `build.md` `proof.md` `verify.md` `ship.md` `review.md` "
                   "`review-security.md` `qa.md` `comment.md` `design-note.md` `config.md` `lessons.md`")

    def test_pass_files_ledgers_knowledge_and_board_cards_by_bare_name(self):
        self.clean("`run.md` `learn.md` `outcomes.md` `weekly.md` `ledger.md` `dev-ledger.md` `defect-ledger.md` "
                   "`ai-ledger.md` `code-map.md` `selectors.md` `calibration.md` `_template.md` `TASK-1.md`")

    def test_files_of_the_target_repo_and_of_design_tools_by_bare_name(self):
        self.clean("`.ndev.toml` `package.json` `.gitleaks.toml` `tokens.json` `palette-report.md` "
                   "`.tokens.json` `.resolver.json` `files.json`")

    def test_run_file_name_under_templates_is_checked(self):
        self.append("skills/workflow/SKILL.md", "`templates/card.md`\n")
        self.assertEqual(self.found(cr.check_paths), [
            MISSING % ("skills/workflow/SKILL.md", 11, "templates/card.md")])


if __name__ == "__main__":
    unittest.main()
