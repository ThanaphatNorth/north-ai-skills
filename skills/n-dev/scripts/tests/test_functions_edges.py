"""Function spans at the edges: comments that hold braces, bodies that never close, lines too long to be a
signature."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from ndev_check.functions import find_spans  # noqa: E402


def spans(text, style="brace"):
    return [(s.name, s.start, s.end) for s in find_spans(text, style)]


class BraceEdges(unittest.TestCase):
    def test_braces_inside_a_comment_that_spans_lines_are_ignored(self):
        text = ("function f() {\n"
                "  /* a brace { opens here\n"
                "     } } and more close here\n"
                "  */ g();\n"
                "  return 1;\n"
                "}\n")
        self.assertEqual(spans(text), [("f", 1, 6)])

    def test_function_whose_body_never_closes_is_not_reported(self):
        self.assertEqual(spans("function f() {\n  g();\n  if (x) {\n    h();\n"), [])

    def test_signature_with_no_body_within_eight_lines_is_not_a_function(self):
        params = "".join("    p%d: Int,\n" % i for i in range(9))
        self.assertEqual(spans("fun build(\n" + params + ") {\n    run()\n}\n"), [])
        self.assertEqual(spans("fun build(\n" + "    p: Int,\n" * 3 + ") {\n    run()\n}\n"), [("build", 1, 7)])

    def test_line_longer_than_a_signature_can_be_is_not_searched(self):
        data = "const table = {" + ",".join("k%d:%d" % (i, i) for i in range(400)) + "};"
        minified = "function packed(){" + "a();" * 300 + "}"
        text = data + "\n" + minified + "\nfunction after() {\n  run();\n}\n"
        self.assertGreater(min(len(data), len(minified)), 1000)
        self.assertEqual(spans(text), [("after", 3, 5)])

    def test_string_contents_do_not_count_towards_the_length_of_a_signature_line(self):
        text = 'function describe() { return "' + "x" * 2000 + '";\n}\n'
        self.assertEqual(spans(text), [("describe", 1, 2)])


class OtherStyles(unittest.TestCase):
    def test_ruby_one_line_and_endless_methods_have_no_span(self):
        text = "def a; 1; end\ndef b() = 2\ndef c\n  3\nend\n"
        self.assertEqual(spans(text, "end"), [("c", 3, 5)])

    def test_python_closing_parenthesis_at_the_def_indent_stays_in_the_function(self):
        text = "def f(\n    a,\n):\n    return a\n\n\nx = 1\n"
        self.assertEqual(spans(text, "indent"), [("f", 1, 4)])


if __name__ == "__main__":
    unittest.main()
