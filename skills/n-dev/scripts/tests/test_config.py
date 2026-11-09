"""Config: a parsed .ndev.toml becomes budgets, excludes and layer rules."""
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from ndev_check.config import ConfigError, from_dict, load  # noqa: E402
from ndev_check.model import Budgets, Layer  # noqa: E402


class FromDict(unittest.TestCase):
    def test_empty_config_keeps_defaults(self):
        c = from_dict({})
        self.assertEqual((c.budgets, c.exclude, c.layers), ({}, (), ()))

    def test_budgets_excludes_and_layers(self):
        c = from_dict({
            "budgets": {"max-file": 400, "max-line": 0},
            "check": {"exclude": ["legacy/**"]},
            "layers": {
                "domain": {"paths": ["src/domain/**"], "imports": ["@/domain"], "may-import": []},
                "ui": {"paths": ["src/ui/**"], "may-import": ["domain"]},
            },
        })
        self.assertEqual(c.budgets, {"max_file": 400, "max_line": 0})
        self.assertEqual(c.exclude, ("legacy/**",))
        self.assertEqual(c.layers, (
            Layer("domain", ("src/domain/**",), ("@/domain",), ()),
            Layer("ui", ("src/ui/**",), (), ("domain",)),
        ))

    def test_unknown_keys_and_bad_types_are_errors(self):
        for bad in ({"budgets": {"max-files": 1}}, {"budgets": {"max-file": "300"}},
                    {"budgets": {"max-file": -1}}, {"surprise": {}}, {"check": {"exclude": "x"}},
                    {"layers": {"a": {"paths": ["x/**"], "may-import": ["nope"]}}},
                    {"layers": {"a": {"may-import": []}}}):
            with self.assertRaises(ConfigError, msg=repr(bad)):
                from_dict(bad)

    def test_profile_key_is_accepted(self):
        self.assertEqual(from_dict({"profile": {"path": "docs/architecture/profile.md"}}).budgets, {})


class Load(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="ndev-config-")

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def test_missing_default_file_is_no_config(self):
        c = load(self.root, None)
        self.assertIsNone(c.path)
        self.assertEqual(c.budgets, {})

    def test_reads_ndev_toml_at_the_root(self):
        with open(os.path.join(self.root, ".ndev.toml"), "w") as fh:
            fh.write("[budgets]\nmax-func = 40\n")
        c = load(self.root, None)
        self.assertEqual((c.path, c.budgets), (".ndev.toml", {"max_func": 40}))

    def test_explicit_missing_file_is_an_error(self):
        with self.assertRaises(ConfigError):
            load(self.root, "nope.toml")

    def test_parse_error_names_the_file(self):
        with open(os.path.join(self.root, ".ndev.toml"), "w") as fh:
            fh.write("[budgets\n")
        with self.assertRaises(ConfigError) as ctx:
            load(self.root, None)
        self.assertIn(".ndev.toml", str(ctx.exception))

    def test_n_arch_template_is_a_valid_config(self):
        template = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "n-arch",
                                "templates", "ndev.toml")
        if not os.path.isfile(template):
            self.skipTest("n-arch is not installed beside n-dev")
        c = load(self.root, os.path.abspath(template))
        self.assertEqual([layer.name for layer in c.layers], ["domain", "application", "infrastructure", "interface"])
        self.assertEqual(c.apply(Budgets(), {}), Budgets())

    def test_merge_order_is_defaults_then_file_then_flags(self):
        c = from_dict({"budgets": {"max-file": 400, "max-func": 60}})
        b = c.apply(Budgets(), {"max_func": 30})
        self.assertEqual((b.max_file, b.max_func, b.max_wiring), (400, 30, 20))


if __name__ == "__main__":
    unittest.main()
