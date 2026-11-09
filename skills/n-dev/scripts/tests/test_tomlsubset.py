"""The TOML subset parser used when tomllib is missing (Python < 3.11)."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from ndev_check.tomlsubset import TomlError, loads  # noqa: E402

SAMPLE = '''# budgets agreed with the team, 2026-11
[budgets]
max-file = 400      # services run long here
max-func = 60
max-line = 0

[check]
exclude = [
  "legacy/**",   # frozen, replaced in Q2
  "scripts/vendor/**",
]

[layers.domain]
paths = ["src/domain/**"]
imports = ["@/domain", 'app.domain']
may-import = []

[layers."ui-web"]
paths = ["src/ui/**"]
may-import = ["domain"]
strict = true
'''


class TomlSubset(unittest.TestCase):
    def test_parses_tables_scalars_and_arrays(self):
        data = loads(SAMPLE)
        self.assertEqual(data["budgets"], {"max-file": 400, "max-func": 60, "max-line": 0})
        self.assertEqual(data["check"]["exclude"], ["legacy/**", "scripts/vendor/**"])
        self.assertEqual(data["layers"]["domain"]["imports"], ["@/domain", "app.domain"])
        self.assertEqual(data["layers"]["domain"]["may-import"], [])
        self.assertEqual(data["layers"]["ui-web"], {"paths": ["src/ui/**"], "may-import": ["domain"], "strict": True})

    def test_hash_inside_a_string_is_not_a_comment(self):
        self.assertEqual(loads('[a]\nk = "x # y"\n'), {"a": {"k": "x # y"}})

    def test_escapes_in_basic_strings(self):
        self.assertEqual(loads('k = "a\\"b\\\\c"\n'), {"k": 'a"b\\c'})

    def test_matches_tomllib_when_available(self):
        try:
            import tomllib  # type: ignore
        except ImportError:
            self.skipTest("tomllib needs Python 3.11+")
        self.assertEqual(loads(SAMPLE), tomllib.loads(SAMPLE))

    def test_unsupported_syntax_names_the_line(self):
        for bad in ('k = { a = 1 }\n', 'k = 1979-05-27\n', '[[arr]]\n', 'k = """x"""\n', 'k = [1, "a"\n'):
            with self.assertRaises(TomlError) as ctx:
                loads("[t]\nok = 1\n" + bad)
            self.assertIn("line 3", str(ctx.exception))

    def test_control_characters_and_lone_surrogates_are_errors(self):
        for bad in ('k = "a\x01b"\n', 'k = "\\uD800"\n', "# note\x7f\nk = 1\n", "# a\rb\nk = 1\n"):
            with self.assertRaises(TomlError, msg=repr(bad)):
                loads(bad)

    def test_duplicate_key_is_an_error(self):
        with self.assertRaises(TomlError):
            loads("[t]\nk = 1\nk = 2\n")


if __name__ == "__main__":
    unittest.main()
