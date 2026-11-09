"""End to end: .ndev.toml (budgets, excludes, layers), its precedence under CLI flags, and --all audits."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from repo_case import RepoCase, lines  # noqa: E402

LAYERED = '''[budgets]
max-wiring = 40   # registries here are long

[check]
exclude = ["src/generated/**"]

[layers.domain]
paths = ["src/domain/**"]
imports = ["@/domain"]

[layers.infra]
paths = ["src/infra/**"]
imports = ["@/infra"]
may-import = ["domain"]
'''


class ConfigFile(RepoCase):
    def test_budgets_and_excludes_come_from_the_file(self):
        self.write(".ndev.toml", LAYERED)
        self.append("src/app.py", lines("extra", 25))
        self.write("src/generated/client.py", lines("g", 400))
        code, data, _ = self.check()
        self.assertEqual((code, data["findings"]), (0, []))
        self.assertEqual((data["config"], data["budgets"]["max_wiring"]), (".ndev.toml", 40))

    def test_flags_override_the_file(self):
        self.write(".ndev.toml", LAYERED)
        self.append("src/app.py", lines("extra", 25))
        code, data, _ = self.check("--max-wiring", "20")
        self.assertIn(("wiring", "src/app.py"), self.kinds(data))

    def test_no_config_ignores_the_file(self):
        self.write(".ndev.toml", LAYERED)
        self.append("src/app.py", lines("extra", 25))
        code, data, _ = self.check("--no-config")
        self.assertEqual((code, data["config"]), (1, None))

    def test_explicit_config_path(self):
        self.write("tools/ndev.toml", "[budgets]\nmax-file = 10\n")
        self.write("src/mid.py", lines("m", 20))
        code, data, _ = self.check("--config", os.path.join(self.repo, "tools/ndev.toml"))
        self.assertIn(("file-size", "src/mid.py"), self.kinds(data))

    def test_bad_config_is_a_usage_error_naming_the_key(self):
        self.write(".ndev.toml", "[budgets]\nmax-files = 1\n")
        code, data, err = self.check()
        self.assertEqual(code, 2)
        self.assertIn("max-files", err)

    def test_added_import_across_a_forbidden_layer(self):
        self.write(".ndev.toml", LAYERED)
        self.commit_file("src/infra/db.ts", "export const db = {};\n")
        self.write("src/domain/order.ts", 'import { db } from "@/infra/db";\nexport const save = () => db;\n')
        code, data, _ = self.check("--base", "HEAD")
        self.assertEqual(code, 1)
        hit = [f for f in data["findings"] if f["kind"] == "layer"]
        self.assertEqual([(f["path"], f["line"], f["related"]) for f in hit], [("src/domain/order.ts", 1, "infra")])

    def test_existing_violation_is_not_reported_when_untouched(self):
        self.write(".ndev.toml", LAYERED)
        self.commit_file("src/domain/order.ts", 'import { db } from "../infra/db";\nexport const a = 1;\n')
        self.append("src/domain/order.ts", "export const b = 2;\n")
        code, data, _ = self.check("--base", "HEAD")
        self.assertEqual((code, data["findings"]), (0, []))

    def test_text_report_names_the_config_and_the_layer_section(self):
        self.write(".ndev.toml", LAYERED)
        self.write("src/domain/order.ts", 'import { db } from "@/infra/db";\n')
        code, out = self.check_text()
        self.assertIn("config .ndev.toml", out)
        self.assertIn("Imports that cross a layer rule (1)", out)


    def test_relative_config_path_is_read_from_the_current_directory(self):
        import subprocess
        from repo_case import ENV, SCRIPT
        scratch = os.path.join(self.repo, "..", os.path.basename(self.repo) + "-scratch")
        os.makedirs(scratch, exist_ok=True)
        with open(os.path.join(scratch, "draft.toml"), "w") as fh:
            fh.write("[budgets]\nmax-file = 10\n")
        self.write("src/mid.py", lines("m", 20))
        proc = subprocess.run([sys.executable, "-I", SCRIPT, "--repo", self.repo, "--json", "--config", "draft.toml"],
                              capture_output=True, text=True, env=ENV, cwd=scratch)
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertIn("src/mid.py", proc.stdout)


class Audit(RepoCase):
    def test_all_reports_whole_repo_debt_as_findings(self):
        self.commit_file("src/legacy.py", lines("old", 320))
        code, data, _ = self.check("--all")
        self.assertEqual(code, 1)
        self.assertEqual(data["base"], "(whole repository)")
        self.assertIn(("file-size", "src/legacy.py"), self.kinds(data))
        self.assertEqual(data["existing"], [])

    def test_text_audit_says_new_means_present(self):
        self.commit_file("src/legacy.py", lines("old", 320))
        code, out = self.check_text("--all")
        self.assertIn("against (whole repository)", out)
        self.assertIn('read "new" and "added" below as "present"', out)

    def test_all_reports_existing_layer_violations(self):
        self.write(".ndev.toml", LAYERED)
        self.commit_file("src/domain/order.ts", 'import { db } from "../infra/db";\n')
        code, data, _ = self.check("--all")
        self.assertIn(("layer", "src/domain/order.ts"), self.kinds(data))

    def test_all_and_base_together_are_a_usage_error(self):
        code, data, err = self.check("--all", "--base", "HEAD")
        self.assertEqual(code, 2)


if __name__ == "__main__":
    unittest.main()
