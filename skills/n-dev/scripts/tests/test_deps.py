"""Dependencies a manifest gained between the base ref and now, per ecosystem."""
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from ndev_check.deps import check_deps, is_manifest, new_dependencies  # noqa: E402
from ndev_check.model import ChangedFile  # noqa: E402


class NewDependencies(unittest.TestCase):
    def test_package_json_sections_only(self):
        before = json.dumps({"dependencies": {"zod": "1"}, "scripts": {"test": "x"}})
        after = json.dumps({"dependencies": {"zod": "2", "axios": "1"}, "devDependencies": {"vitest": "1"},
                            "scripts": {"test": "x", "lint": "eslint"}})
        self.assertEqual(new_dependencies("web/package.json", before, after), ["axios", "vitest"])

    def test_new_manifest_counts_everything(self):
        self.assertEqual(new_dependencies("package.json", None, json.dumps({"dependencies": {"a": "1"}})), ["a"])

    def test_invalid_json_is_skipped(self):
        self.assertEqual(new_dependencies("package.json", None, "{ not json"), [])

    def test_composer_skips_platform_packages(self):
        after = json.dumps({"require": {"php": "^8.2", "ext-json": "*", "guzzlehttp/guzzle": "^7"}})
        self.assertEqual(new_dependencies("composer.json", "{}", after), ["guzzlehttp/guzzle"])

    def test_requirements_names_are_normalised(self):
        before = "Requests==2.0\n"
        after = "requests==2.1\n# comment\n-r base.txt\nhttpx[http2]>=0.27 ; python_version>'3.8'\nPy_Yaml\n"
        self.assertEqual(new_dependencies("requirements-dev.txt", before, after), ["httpx", "py-yaml"])

    def test_pyproject_pep621_poetry_and_groups(self):
        before = '[project]\nname = "x"\ndependencies = ["fastapi>=0.110"]\n'
        after = ('[project]\nname = "x"\ndependencies = [\n  "fastapi>=0.111",\n  "pydantic>=2",\n]\n'
                 '[project.optional-dependencies]\ntest = ["pytest>=8"]\n'
                 '[tool.poetry.dependencies]\npython = "^3.12"\nrich = "^13"\n'
                 '[dependency-groups]\ndev = ["ruff"]\n')
        self.assertEqual(new_dependencies("pyproject.toml", before, after), ["pydantic", "pytest", "rich", "ruff"])

    def test_go_mod_single_and_block(self):
        before = "module x\n\nrequire github.com/a/b v1.0.0\n"
        after = "module x\n\nrequire github.com/a/b v1.1.0\n\nrequire (\n\tgithub.com/c/d v0.1.0 // indirect\n)\n"
        self.assertEqual(new_dependencies("go.mod", before, after), ["github.com/c/d"])

    def test_cargo_gemfile_gradle_maven_csproj_pubspec_podfile(self):
        cases = [
            ("Cargo.toml", "[dependencies]\nserde = \"1\"\n",
             "[dependencies]\nserde = \"1\"\ntokio = { version = \"1\" }\n[dev-dependencies.proptest]\nversion = \"1\"\n",
             ["proptest", "tokio"]),
            ("Gemfile", "gem 'rails'\n", "gem 'rails'\ngem \"sidekiq\", \"~> 7\"\n", ["sidekiq"]),
            ("app/build.gradle.kts", 'implementation("a:b:1")\n',
             'implementation("a:b:2")\ntestImplementation "io.mockk:mockk:1.13"\n', ["io.mockk:mockk"]),
            ("pom.xml", "", "<dependency><groupId>org.x</groupId>\n<artifactId>y</artifactId></dependency>\n", ["org.x:y"]),
            ("Api.csproj", "", '<PackageReference Include="Polly" Version="8" />\n', ["Polly"]),
            ("pubspec.yaml", "name: a\ndependencies:\n  http: ^1.0.0\n",
             "name: a\ndependencies:\n  http: ^1.0.0\n  dio: ^5.0.0\ndev_dependencies:\n  mocktail: ^1.0.0\n",
             ["dio", "mocktail"]),
            ("ios/Podfile", "pod 'Alamofire'\n", "pod 'Alamofire'\n  pod \"Kingfisher\", '~> 7'\n", ["Kingfisher"]),
        ]
        for path, before, after, expected in cases:
            self.assertEqual(new_dependencies(path, before, after), expected, path)

    def test_manifest_detection(self):
        self.assertTrue(all(is_manifest(p) for p in ("a/package.json", "requirements.txt", "reqs/requirements-dev.in",
                                                      "go.mod", "Cargo.toml", "pyproject.toml", "X.csproj")))
        self.assertFalse(any(is_manifest(p) for p in ("package-lock.json", "src/app.py", "go.sum", "tsconfig.json")))


class ReviewFindings(unittest.TestCase):
    def test_pyproject_extras_bracket_does_not_close_the_array(self):
        before = '[project]\ndependencies = [\n  "uvicorn[standard]",\n]\n'
        after = '[project]\ndependencies = [\n  "uvicorn[standard]",\n  "fastapi",\n  "reqeusts",\n]\n'
        self.assertEqual(new_dependencies("pyproject.toml", before, after), ["fastapi", "reqeusts"])


class CheckDeps(unittest.TestCase):
    def test_finding_points_at_the_line_that_adds_it(self):
        text = "requests==2.1\nhttpx>=0.27\n"
        f = ChangedFile("requirements.txt", False, frozenset([2]), 0, text)
        found = check_deps([f], {"requirements.txt": "requests==2.1\n"})
        self.assertEqual([(x.kind, x.path, x.line, x.value) for x in found], [("new-dependency", "requirements.txt", 2, 1)])
        self.assertIn("httpx", found[0].message)

    def test_unchanged_dependency_set_is_clean(self):
        f = ChangedFile("requirements.txt", False, frozenset([1]), 1, "requests==2.2\n")
        self.assertEqual(check_deps([f], {"requirements.txt": "requests==2.1\n"}), [])


if __name__ == "__main__":
    unittest.main()
