"""Import extraction per language, and layer rules judged on added imports."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from ndev_check.imports import find_imports  # noqa: E402
from ndev_check.layers import check_layers  # noqa: E402
from ndev_check.model import ChangedFile, Layer  # noqa: E402


def specs(path, text):
    return find_imports(path, text)


class FindImports(unittest.TestCase):
    def test_typescript_forms(self):
        text = ('import { a } from "./x";\n'
                "import {\n  b,\n} from '../domain/m';\n"
                "export * from './y';\n"
                'const z = require("z");\n'
                'const lazy = await import("./lazy");\n'
                'import "./side";\n'
                'import type { T } from "@/domain/t";\n')
        self.assertEqual(specs("src/a.ts", text), [
            (1, "./x"), (4, "../domain/m"), (5, "./y"), (6, "z"), (7, "./lazy"), (8, "./side"), (9, "@/domain/t")])

    def test_python_forms(self):
        text = ("import app.domain.money\n"
                "from app.domain import x\n"
                "from . import sibling\n"
                "from ..infra.db import session\n"
                "import os, json\n")
        self.assertEqual(specs("app/ui/view.py", text), [
            (1, "app.domain.money"), (2, "app.domain.x"), (3, ".sibling"), (4, "..infra.db.session"), (5, "os"),
            (5, "json")])

    def test_go_single_and_block(self):
        text = 'package ui\n\nimport "fmt"\n\nimport (\n\t"strings"\n\tdb "example.com/app/infra/db"\n)\n'
        self.assertEqual(specs("ui/h.go", text), [(3, "fmt"), (6, "strings"), (7, "example.com/app/infra/db")])

    def test_jvm_php_csharp_ruby_rust_dart(self):
        self.assertEqual(specs("A.kt", "import com.acme.domain.Money\n"), [(1, "com.acme.domain.Money")])
        self.assertEqual(specs("A.java", "import static com.acme.x.Y.z;\n"), [(1, "com.acme.x.Y.z")])
        self.assertEqual(specs("a.php", "<?php\nuse App\\Domain\\Money;\n"), [(2, "App\\Domain\\Money")])
        self.assertEqual(specs("A.cs", "using Acme.Domain;\n"), [(1, "Acme.Domain")])
        self.assertEqual(specs("a.rb", 'require_relative "../domain/money"\n'), [(1, "../domain/money")])
        self.assertEqual(specs("a.rs", "use crate::domain::money;\n"), [(1, "crate::domain::money")])
        self.assertEqual(specs("a.dart", "import 'package:app/domain/m.dart';\n"), [(1, "package:app/domain/m.dart")])

    def test_unknown_language_has_no_imports(self):
        self.assertEqual(specs("notes.md", "import x from 'y'\n"), [])


LAYERS = (
    Layer("domain", ("src/domain/**",), ("@/domain",), ()),
    Layer("application", ("src/app/**",), ("@/app",), ("domain",)),
    Layer("infra", ("src/infra/**",), ("@/infra",), ("domain", "application")),
    Layer("ui", ("src/ui/**",), (), ("application", "domain")),
)


def changed(path, text, added=None, is_new=True):
    n = text.count("\n")
    lines = frozenset(added if added is not None else range(1, n + 1))
    return ChangedFile(path, is_new, lines, 0, text)


class CheckLayers(unittest.TestCase):
    def kinds(self, files, layers=LAYERS):
        return [(f.path, f.line, f.related) for f in check_layers(files, layers)]

    def test_allowed_and_same_layer_imports_are_clean(self):
        f = changed("src/ui/cart.ts", 'import { q } from "@/app/quote";\nimport { M } from "../domain/money";\n'
                    'import { B } from "./button";\nimport React from "react";\n')
        self.assertEqual(self.kinds([f]), [])

    def test_prefix_import_into_a_forbidden_layer(self):
        f = changed("src/ui/cart.ts", 'import { db } from "@/infra/db";\n')
        found = check_layers([f], LAYERS)
        self.assertEqual([(x.kind, x.line, x.related) for x in found], [("layer", 1, "infra")])
        self.assertIn("ui may import: application, domain", found[0].message)

    def test_relative_import_is_resolved_to_its_layer(self):
        f = changed("src/domain/money.ts", 'import { log } from "../infra/log";\n')
        self.assertEqual(self.kinds([f]), [("src/domain/money.ts", 1, "infra")])

    def test_layer_that_may_import_nothing(self):
        f = changed("src/domain/money.ts", 'import { quote } from "@/app/quote";\n')
        found = check_layers([f], LAYERS)
        self.assertIn("domain may import: nothing", found[0].message)

    def test_python_dotted_import_matches_layer_paths(self):
        layers = (Layer("domain", ("app/domain/**",), (), ()), Layer("infra", ("app/infra/**",), (), ("domain",)))
        f = changed("app/domain/money.py", "from app.infra.db import session\nfrom ..infra import cache\n")
        self.assertEqual(self.kinds([f], layers), [("app/domain/money.py", 1, "infra"), ("app/domain/money.py", 2, "infra")])

    def test_only_added_lines_count(self):
        f = changed("src/ui/cart.ts", 'import { db } from "@/infra/db";\nimport { q } from "@/app/q";\n',
                    added=[2], is_new=False)
        self.assertEqual(self.kinds([f]), [])

    def test_tests_and_unlayered_files_are_skipped(self):
        files = [changed("src/ui/cart.test.ts", 'import { db } from "@/infra/db";\n'),
                 changed("scripts/seed.ts", 'import { db } from "@/infra/db";\n')]
        self.assertEqual(self.kinds(files), [])

    def test_prefix_must_end_at_a_boundary(self):
        f = changed("src/domain/money.ts", 'import { x } from "@/infrastructure-docs/x";\n')
        self.assertEqual(self.kinds([f]), [])

    def test_longest_import_prefix_wins_over_declaration_order(self):
        layers = (Layer("billing", ("src/modules/billing/**",), ("@/modules/billing",), ()),
                  Layer("billing-api", ("src/modules/billing/api/**",), ("@/modules/billing/api",), ()),
                  Layer("orders", ("src/modules/orders/**",), (), ("billing-api",)))
        ok = changed("src/modules/orders/place.ts", 'import { charge } from "@/modules/billing/api/charge";\n')
        bad = changed("src/modules/orders/refund.ts", 'import { ledger } from "@/modules/billing/ledger";\n')
        self.assertEqual(self.kinds([ok, bad], layers), [("src/modules/orders/refund.ts", 1, "billing")])

    def test_most_specific_path_glob_wins_over_declaration_order(self):
        layers = (Layer("billing", ("src/modules/billing/**",), (), ()),
                  Layer("billing-api", ("src/modules/billing/api/**",), (), ()),
                  Layer("orders", ("src/modules/orders/**",), (), ("billing-api",)))
        ok = changed("src/modules/orders/place.ts", 'import { charge } from "../billing/api/charge";\n')
        self.assertEqual(self.kinds([ok], layers), [])

    def test_namespace_read_as_path_ignores_case(self):
        layers = (Layer("model", ("app/Models/**",), (), ()), Layer("service", ("app/Services/**",), (), ("model",)))
        f = changed("app/Models/Order.php", "<?php\nuse App\\Services\\Billing;\n")
        self.assertEqual(self.kinds([f], layers), [("app/Models/Order.php", 2, "service")])

    def test_python_from_package_import_module(self):
        layers = (Layer("domain", ("app/domain/**",), (), ()), Layer("infra", ("app/infra/**",), (), ()))
        f = changed("app/domain/money.py", "from app import infra\nfrom .. import infra as i2\n")
        self.assertEqual(self.kinds([f], layers), [("app/domain/money.py", 1, "infra"), ("app/domain/money.py", 2, "infra")])

    def test_import_that_existed_at_the_base_is_not_new(self):
        text = 'import { memoryOrders, MAX } from "../infra/db";\n'
        f = changed("src/domain/order.ts", text, added=[1], is_new=False)
        base = {"src/domain/order.ts": 'import { memoryOrders } from "../infra/db";\n'}
        self.assertEqual([x.path for x in check_layers([f], LAYERS, base)], [])
        self.assertEqual([x.path for x in check_layers([f], LAYERS, {})], ["src/domain/order.ts"])

    def test_no_layers_no_findings(self):
        self.assertEqual(check_layers([changed("src/ui/a.ts", 'import "@/infra/db";\n')], ()), [])


if __name__ == "__main__":
    unittest.main()
