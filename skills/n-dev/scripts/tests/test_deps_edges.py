"""Manifests at the edges: files that are not what their name promises, and entries that only look like
dependencies."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from ndev_check.deps import check_deps, new_dependencies  # noqa: E402
from ndev_check.model import ChangedFile  # noqa: E402


def change(path, text, added):
    return ChangedFile(path, False, frozenset(added), 0, text)


class OddManifests(unittest.TestCase):
    def test_json_manifest_that_is_not_an_object_has_no_dependencies(self):
        self.assertEqual(new_dependencies("package.json", None, '["dependencies", "axios"]'), [])
        self.assertEqual(new_dependencies("composer.json", None, '"require"'), [])

    def test_json_manifest_nested_past_the_decoder_limit_is_skipped(self):
        self.assertEqual(new_dependencies("package.json", None, "[" * 200000), [])
        self.assertEqual(new_dependencies("package.json", '{"dependencies": {"a": "1"}}', "[" * 200000), [])

    def test_path_that_is_no_manifest_has_no_dependencies(self):
        self.assertEqual(new_dependencies("docs/requirements.md", None, "requests\n"), [])

    def test_pyproject_lines_that_are_neither_header_nor_key_are_ignored(self):
        text = ("\n[project]\nname = \"x\"\n\nstray words\ndependencies = [\n  \"httpx>=0.27\",\n]\n"
                "\n[tool.poetry.dependencies]\n\npython = \"^3.12\"\n: not a key\nrich = \"*\"\n")
        self.assertEqual(new_dependencies("pyproject.toml", None, text), ["httpx", "rich"])

    def test_pom_dependency_without_both_coordinates_is_ignored(self):
        text = ("<dependencies>\n"
                "<dependency><groupId>org.acme</groupId></dependency>\n"
                "<dependency><artifactId>orphan</artifactId></dependency>\n"
                "<dependency><groupId> org.acme </groupId><artifactId>lib</artifactId></dependency>\n"
                "</dependencies>\n")
        self.assertEqual(new_dependencies("pom.xml", None, text), ["org.acme:lib"])

    def test_pubspec_entries_outside_the_dependency_sections_are_not_dependencies(self):
        text = ("name: shop\nenvironment:\n  sdk: ^3.4.0\ndependencies:\n  http: ^1.2.0\n    nested: 1\n"
                "dev_dependencies:\n  lints: ^4.0.0\nflutter:\n  uses_material_design: true\n")
        self.assertEqual(new_dependencies("pubspec.yaml", None, text), ["http", "lints"])

    def test_indented_entries_after_blank_lines_are_found(self):
        self.assertEqual(new_dependencies("Gemfile", None, "source 'x'\n\n\n  gem 'rails'\n\tgem \"pg\"\n"),
                         ["pg", "rails"])
        self.assertEqual(new_dependencies("Podfile", None, "target 'App' do\n\n  pod 'Alamofire'\nend\n"), ["Alamofire"])
        gradle = "dependencies {\n\n    implementation 'com.acme:lib:1.0'\n\n\tapi(\"org.x:y:2\")\n}\n"
        self.assertEqual(new_dependencies("app/build.gradle", None, gradle), ["com.acme:lib", "org.x:y"])


class FindingLine(unittest.TestCase):
    def test_falls_back_to_the_first_added_line_when_none_spells_the_name(self):
        """requirements names are normalised (Flask_SQLAlchemy -> flask-sqlalchemy), so no line matches."""
        f = change("requirements.txt", "requests\n\nFlask_SQLAlchemy==3.1\n", added=[3])
        found = check_deps([f], {"requirements.txt": "requests\n"})
        self.assertEqual([(x.line, x.value) for x in found], [(3, 1)])
        self.assertIn("flask-sqlalchemy", found[0].message)

    def test_is_line_1_when_the_change_added_no_line(self):
        f = change("requirements.txt", "requests\nhttpx\n", added=[])
        self.assertEqual([x.line for x in check_deps([f], {"requirements.txt": "requests\n"})], [1])


if __name__ == "__main__":
    unittest.main()
