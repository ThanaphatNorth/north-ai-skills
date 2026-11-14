"""Path classification: which language family a file is, and which files are tests or noise."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from ndev_check import classify  # noqa: E402


class Classify(unittest.TestCase):
    def test_function_style_per_language_family(self):
        styles = {"web/App.TSX": "brace", "pkg/main.go": "brace", "app/models.py": "indent",
                  "lib/tasks/seed.rb": "end", "README.md": None, "Makefile": None, "data.json": None}
        self.assertEqual({p: classify.function_style(p) for p in styles}, styles)

    def test_code_is_decided_by_extension_whatever_its_case(self):
        self.assertEqual([classify.is_code(p) for p in ("a.PY", "b.Kt", "c.txt", "Dockerfile", ".py")],
                         [True, True, False, False, False])
        self.assertEqual(classify.extension("src/Legacy.JSX"), ".jsx")

    def test_test_files_by_name_or_folder(self):
        tests = ("tests/helpers.py", "pkg/test_x.py", "pkg/x_test.go", "web/x.spec.ts", "web/__tests__/x.ts",
                 "app/src/androidTest/X.kt", "src/FooTest.java", "spec/models/user.rb", "Tests/FooTests.swift")
        sources = ("src/contest.py", "src/testing.ts", "src/latest/x.py", "src/Attest.java", "protest.rb")
        self.assertEqual([p for p in tests if not classify.is_test(p)], [])
        self.assertEqual([p for p in sources if classify.is_test(p)], [])

    def test_noise_is_lockfiles_generated_files_vendored_folders_and_extra_globs(self):
        noise = ("package-lock.json", "web/yarn.lock", "go.sum", "dist/app.js", "a/node_modules/x/i.js",
                 "api/user_pb2.py", "db/migrations/0001_init.py", "static/app.min.js", "lib/x.g.dart")
        self.assertEqual([p for p in noise if not classify.is_noise(p)], [])
        self.assertEqual([p for p in ("src/app.py", "src/builder/x.py", "outline/x.ts") if classify.is_noise(p)], [])
        self.assertTrue(classify.is_noise("legacy/old.py", ["legacy/**"]))
        self.assertFalse(classify.is_noise("src/legacy.py", ["legacy/**"]))


if __name__ == "__main__":
    unittest.main()
