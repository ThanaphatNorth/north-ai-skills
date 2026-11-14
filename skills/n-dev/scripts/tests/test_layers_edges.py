"""Layer rules at the edges: import forms the scanners only half read, and ties between layers."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from ndev_check.imports import find_imports  # noqa: E402
from ndev_check.layers import check_layers  # noqa: E402
from ndev_check.model import ChangedFile, Layer  # noqa: E402


def new_file(path, text):
    return ChangedFile(path, True, frozenset(range(1, text.count("\n") + 2)), 0, text)


def crossings(files, layers):
    return [(f.path, f.line, f.related) for f in check_layers(files, layers)]


class ImportForms(unittest.TestCase):
    def test_python_parenthesised_import_with_names_on_later_lines_is_the_module(self):
        text = "from app.infra import (\n    db,\n    cache,\n)\nfrom . import (\n    sibling,\n)\n"
        self.assertEqual(find_imports("app/domain/order.py", text), [(1, "app.infra"), (5, ".")])

    def test_go_import_block_skips_blank_lines_and_comments(self):
        text = 'import (\n\t"fmt"\n\n\t// storage\n\tdb "app/infra/db"\n)\n\nvar x = "not/an/import"\n'
        self.assertEqual(find_imports("domain/order.go", text), [(2, "fmt"), (5, "app/infra/db")])


class LayerTies(unittest.TestCase):
    def test_file_matched_equally_by_two_layers_belongs_to_the_one_declared_first(self):
        strict = Layer("strict", ("src/**",), (), ())
        loose = Layer("loose", ("src/**",), (), ("infra",))
        infra = Layer("infra", ("lib/infra/**",), ("@/infra",), ())
        f = new_file("src/order.ts", 'import { db } from "@/infra/db";\n')
        self.assertEqual(crossings([f], [strict, loose, infra]), [("src/order.ts", 1, "infra")])
        self.assertEqual(crossings([f], [loose, strict, infra]), [])

    def test_less_specific_glob_declared_later_does_not_take_the_file(self):
        domain = Layer("domain", ("src/domain/**",), (), ())
        everything = Layer("everything", ("src/**",), (), ("infra",))
        infra = Layer("infra", ("lib/infra/**",), ("@/infra",), ())
        f = new_file("src/domain/order.ts", 'import { db } from "@/infra/db";\n')
        self.assertEqual(crossings([f], [domain, everything, infra]), [("src/domain/order.ts", 1, "infra")])

    def test_specifier_equal_to_a_declared_prefix_refers_to_that_layer(self):
        domain = Layer("domain", ("src/domain/**",), ("@/domain",), ())
        infra = Layer("infra", ("src/infra/**",), ("@/infra",), ())
        f = new_file("src/domain/order.ts", 'import infra from "@/infra";\nimport near from "@/infrared";\n')
        self.assertEqual(crossings([f], [domain, infra]), [("src/domain/order.ts", 1, "infra")])

    def test_python_relative_import_of_the_package_itself(self):
        domain = Layer("domain", ("app/domain/**",), (), ())
        infra = Layer("infra", ("app/infra/**",), (), ())
        f = new_file("app/infra/db.py", "from .. import domain\nfrom . import pool\n")
        self.assertEqual(crossings([f], [domain, infra]), [("app/infra/db.py", 1, "domain")])


if __name__ == "__main__":
    unittest.main()
