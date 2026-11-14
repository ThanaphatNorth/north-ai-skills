"""Characterization: the exit code and exact output lines of validate_skill.py for one skill folder."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from skill_case import PASS, SkillCase, reference  # noqa: E402

ONE_REF = "references: 1 files, 0 distinct URLs"


class ValidSkill(SkillCase):
    def test_valid_skill_passes(self):
        self.assertEqual(self.cli(), (0, [ONE_REF, PASS]))

    def test_trailing_slash_on_the_folder_is_ignored(self):
        self.assertEqual(self.cli(skill=self.skill + "/"), (0, [ONE_REF, PASS]))

    def test_skill_without_references_folder(self):
        os.remove(os.path.join(self.skill, "references", "guide.md"))
        os.rmdir(os.path.join(self.skill, "references"))
        self.skill_md(body="No references.\n")
        self.assertEqual(self.cli(), (0, ["references: 0 files, 0 distinct URLs", PASS]))

    def test_only_markdown_files_count_as_references(self):
        self.write("references/data.json", "{}")
        self.assertEqual(self.cli(), (0, [ONE_REF, PASS]))


class Frontmatter(SkillCase):
    def fails_with(self, *errors):
        self.assertEqual(self.cli(), (1, [ONE_REF] + ["ERROR " + e for e in errors] + [
            "RESULT: FAIL (%d errors, 0 warnings)" % len(errors)]))

    def test_missing_frontmatter(self):
        self.skill_md(front=None)
        self.fails_with("SKILL.md: missing YAML frontmatter")

    def test_name_differs_from_folder(self):
        self.skill_md(front="name: other\ndescription: A demo skill.")
        self.fails_with("SKILL.md: name 'other' != folder 'demo'")

    def test_name_missing(self):
        self.skill_md(front="description: A demo skill.")
        self.fails_with("SKILL.md: name None != folder 'demo'")

    def test_empty_description(self):
        self.skill_md(front="name: demo\ndescription:")
        self.fails_with("SKILL.md: empty description")

    def test_description_key_missing(self):
        self.skill_md(front="name: demo")
        self.fails_with("SKILL.md: empty description")

    def test_description_over_1024_chars(self):
        self.skill_md(front="name: demo\ndescription: " + "d" * 1025)
        self.fails_with("SKILL.md: description is 1025 chars (> 1024)")

    def test_description_of_exactly_1024_chars_passes(self):
        self.skill_md(front="name: demo\ndescription: " + "d" * 1024)
        self.assertEqual(self.cli(), (0, [ONE_REF, PASS]))

    def test_name_and_description_errors_together(self):
        self.skill_md(front="name: other")
        self.fails_with("SKILL.md: name 'other' != folder 'demo'", "SKILL.md: empty description")


class RoutedPaths(SkillCase):
    def test_skill_md_points_at_a_missing_file(self):
        self.skill_md(body="Open `references/guide.md`, then `references/gone.md`.\n")
        self.assertEqual(self.cli(), (1, [ONE_REF, "ERROR SKILL.md points at missing references/gone.md",
                                          "RESULT: FAIL (1 errors, 0 warnings)"]))

    def test_missing_templates_and_scripts_are_reported_sorted_and_once(self):
        self.skill_md(body="`references/guide.md` `templates/t.md` `scripts/run.py build` `scripts/run.py`\n")
        self.assertEqual(self.cli(), (1, [ONE_REF, "ERROR SKILL.md points at missing scripts/run.py",
                                          "ERROR SKILL.md points at missing templates/t.md",
                                          "RESULT: FAIL (2 errors, 0 warnings)"]))

    def test_existing_template_and_script_pass(self):
        self.write("templates/t.md", "x")
        self.write("scripts/run.py", "x")
        self.skill_md(body="`references/guide.md` `templates/t.md` `scripts/run.py build`\n")
        self.assertEqual(self.cli(), (0, [ONE_REF, PASS]))

    def test_reference_not_routed_from_skill_md_is_a_warning(self):
        self.write("references/extra.md", reference())
        self.assertEqual(self.cli(), (0, ["references: 2 files, 0 distinct URLs",
                                          "WARN  references/extra.md is not routed from SKILL.md",
                                          "RESULT: PASS (0 errors, 1 warnings)"]))


class ReferenceShape(SkillCase):
    def result(self, text):
        self.write("references/guide.md", text)
        return self.cli()

    def test_missing_title(self):
        self.assertEqual(self.result(reference(title="Guide")), (1, [
            ONE_REF, "ERROR guide.md: must start with '# Title'", "RESULT: FAIL (1 errors, 0 warnings)"]))

    def test_missing_read_when(self):
        self.assertEqual(self.result(reference(read_when="A plain intro.")), (1, [
            ONE_REF, "ERROR guide.md: missing '> Read when:' line near the top",
            "RESULT: FAIL (1 errors, 0 warnings)"]))

    def test_read_when_after_the_first_600_chars_does_not_count(self):
        text = reference(read_when="x" * 600, extra=["> Read when: too late."])
        self.assertEqual(self.result(text), (1, [
            ONE_REF, "ERROR guide.md: missing '> Read when:' line near the top",
            "RESULT: FAIL (1 errors, 0 warnings)"]))

    def test_missing_sources(self):
        self.assertEqual(self.result(reference(sources=None)), (1, [
            ONE_REF, "ERROR guide.md: missing '## Sources' section", "RESULT: FAIL (1 errors, 0 warnings)"]))

    def test_all_three_shape_errors_in_order(self):
        self.assertEqual(self.result("\n".join("line %d" % i for i in range(130))), (1, [
            ONE_REF, "ERROR guide.md: must start with '# Title'",
            "ERROR guide.md: missing '> Read when:' line near the top",
            "ERROR guide.md: missing '## Sources' section", "RESULT: FAIL (3 errors, 0 warnings)"]))

    def test_too_short_is_a_warning(self):
        self.assertEqual(self.result(reference(lines=119)), (0, [
            ONE_REF, "WARN  guide.md: 119 lines (expected 120-750)", "RESULT: PASS (0 errors, 1 warnings)"]))

    def test_too_long_is_a_warning(self):
        self.assertEqual(self.result(reference(lines=751)), (0, [
            ONE_REF, "WARN  guide.md: 751 lines (expected 120-750)", "RESULT: PASS (0 errors, 1 warnings)"]))

    def test_range_bounds_are_inclusive(self):
        self.assertEqual(self.result(reference(lines=120)), (0, [ONE_REF, PASS]))
        self.assertEqual(self.result(reference(lines=750)), (0, [ONE_REF, PASS]))

    def test_a_final_newline_counts_as_one_more_line(self):
        self.assertEqual(self.result(reference(lines=119) + "\n"), (0, [ONE_REF, PASS]))

    def test_cross_link_to_a_missing_sibling_is_a_warning(self):
        text = reference(extra=["See `other.md` for more."])
        self.assertEqual(self.result(text), (0, [
            ONE_REF, "WARN  guide.md: cross-links missing sibling other.md",
            "RESULT: PASS (0 errors, 1 warnings)"]))

    def test_cross_link_to_a_sibling_or_to_skill_md_is_fine(self):
        self.write("references/other.md", reference())
        self.skill_md(body="`references/guide.md` and `references/other.md`\n")
        text = reference(extra=["See `other.md` and `SKILL.md`; `sub/dir.md` is not a sibling name."])
        self.assertEqual(self.result(text), (0, ["references: 2 files, 0 distinct URLs", PASS]))

    def test_each_missing_sibling_is_reported_once(self):
        text = reference(extra=["`b.md` `a.md` `b.md`"])
        code, lines = self.result(text)
        self.assertEqual((code, lines[0], lines[-1]), (0, ONE_REF, "RESULT: PASS (0 errors, 2 warnings)"))
        self.assertEqual(sorted(lines[1:-1]), ["WARN  guide.md: cross-links missing sibling a.md",
                                               "WARN  guide.md: cross-links missing sibling b.md"])

    def test_urls_are_counted_distinct_across_files(self):
        self.write("references/other.md", reference(extra=["https://a.dev/x and https://b.dev/y"]))
        self.skill_md(body="`references/guide.md` and `references/other.md`\n")
        text = reference(extra=["https://a.dev/x twice https://a.dev/x"])
        self.assertEqual(self.result(text), (0, ["references: 2 files, 2 distinct URLs", PASS]))


class OutputOrder(SkillCase):
    def test_warnings_then_errors_each_in_file_order(self):
        self.skill_md(front="name: other\ndescription: A demo skill.", body="`references/gone.md`\n")
        self.write("references/a.md", reference(lines=10, title="A"))
        self.write("references/guide.md", reference(sources=None, extra=["`zz.md`"]))
        self.assertEqual(self.cli(), (1, [
            "references: 2 files, 0 distinct URLs",
            "WARN  references/a.md is not routed from SKILL.md",
            "WARN  references/guide.md is not routed from SKILL.md",
            "WARN  a.md: 10 lines (expected 120-750)",
            "WARN  guide.md: cross-links missing sibling zz.md",
            "ERROR SKILL.md: name 'other' != folder 'demo'",
            "ERROR SKILL.md points at missing references/gone.md",
            "ERROR a.md: must start with '# Title'",
            "ERROR guide.md: missing '## Sources' section",
            "RESULT: FAIL (4 errors, 4 warnings)"]))


if __name__ == "__main__":
    unittest.main()
