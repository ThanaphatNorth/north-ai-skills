import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from ndev_check.functions import find_spans  # noqa: E402


def body(n):
    return "\n".join("  x%d = %d;" % (i, i) for i in range(n))


class BraceLanguages(unittest.TestCase):
    def spans(self, text):
        return [(s.name, s.start, s.end) for s in find_spans(text, "brace")]

    def test_function_declaration(self):
        text = "function total(a, b) {\n%s\n}\n" % body(3)
        self.assertEqual(self.spans(text), [("total", 1, 5)])

    def test_arrow_with_body(self):
        text = "export const total = (a: number) => {\n%s\n};\n" % body(2)
        self.assertEqual(self.spans(text), [("total", 1, 4)])

    def test_class_method_and_control_flow_is_not_a_function(self):
        text = "class A {\n  run(x) {\n    if (x) {\n      go();\n    }\n  }\n}\n"
        self.assertEqual(self.spans(text), [("run", 2, 6)])

    def test_braces_inside_strings_and_comments_are_ignored(self):
        text = 'function f() {\n  const s = "}}}";\n  // }\n  /* { */\n  return s;\n}\n'
        self.assertEqual(self.spans(text), [("f", 1, 6)])

    def test_declaration_without_body_is_skipped(self):
        self.assertEqual(self.spans("function f(a: string): void;\n"), [])

    def test_kotlin_and_go(self):
        kt = "fun price(cart: Cart): Money {\n  return cart.total\n}\n"
        go = "func (s *Svc) Price(c Cart) Money {\n\treturn c.Total\n}\n"
        self.assertEqual(self.spans(kt), [("price", 1, 3)])
        self.assertEqual(self.spans(go), [("Price", 1, 3)])

    def test_signature_spanning_lines(self):
        text = "function f(\n  a,\n  b,\n) {\n  return a;\n}\n"
        self.assertEqual(self.spans(text), [("f", 1, 6)])


class OtherLanguages(unittest.TestCase):
    def test_python_def_ends_at_dedent(self):
        text = "def a(x):\n    y = x\n\n    return y\n\ndef b():\n    pass\n"
        spans = [(s.name, s.start, s.end) for s in find_spans(text, "indent")]
        self.assertEqual(spans, [("a", 1, 4), ("b", 6, 7)])

    def test_python_method_and_multiline_signature(self):
        text = "class C:\n    def m(\n        self,\n    ):\n        return 1\n"
        spans = [(s.name, s.start, s.end) for s in find_spans(text, "indent")]
        self.assertEqual(spans, [("m", 2, 5)])

    def test_ruby_def_end(self):
        text = "class C\n  def total\n    1\n  end\n  def one = 1\nend\n"
        spans = [(s.name, s.start, s.end) for s in find_spans(text, "end")]
        self.assertEqual(spans, [("total", 2, 4)])

    def test_unsupported_style(self):
        self.assertEqual(find_spans("anything", None), [])


if __name__ == "__main__":
    unittest.main()
