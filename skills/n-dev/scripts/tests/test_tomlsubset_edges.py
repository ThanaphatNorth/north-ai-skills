"""The TOML subset at its edges: unusual but legal documents parse as tomllib parses them, and every
document outside the subset is a TomlError that names the line."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from ndev_check.tomlsubset import MAX_DEPTH, TomlError, loads  # noqa: E402

LEGAL = {
    "crlf line endings": ('# note\r\n[a]\r\nk = 1 # why\r\nxs = [\r\n  "p",\r\n]\r\n',
                          {"a": {"k": 1, "xs": ["p"]}}),
    "no newline at the end": ("[a]\nk = true", {"a": {"k": True}}),
    "comment as the last line": ("k = 1\n# end", {"k": 1}),
    "empty document": ("", {}),
    "only blank lines and comments": ("\n\t \n# nothing\n", {}),
    "quoted keys": ('"a b" = 1\n\'c.d\' = 2\n["t u".\'v\']\nk = 3\n', {"a b": 1, "c.d": 2, "t u": {"v": {"k": 3}}}),
    "parent table after its child": ("[a.b]\nk = 1\n[a]\nj = 2\n", {"a": {"b": {"k": 1}, "j": 2}}),
    "spaces around a header's dots": ("[ a . b ]\nk = 1\n", {"a": {"b": {"k": 1}}}),
    "signed and grouped integers": ("a = +1_000\nb = -5\nc = 0\n", {"a": 1000, "b": -5, "c": 0}),
    "the 64-bit limits": ("lo = -9223372036854775808\nhi = 9223372036854775807\n",
                          {"lo": -2 ** 63, "hi": 2 ** 63 - 1}),
    "escapes": ('k = "tab\\there \\u00e9 \\U0001F600 \\b\\f\\n\\r"\n', {"k": "tab\there \u00e9 \U0001F600 \b\f\n\r"}),
    "literal string keeps backslashes": ("k = 'C:\\dir\\n'\n", {"k": "C:\\dir\\n"}),
    "tab inside strings and comments": ('k = "a\tb" #\tc\n', {"k": "a\tb"}),
    "nested and mixed arrays": ('k = [[1, 2], ["a"], [], [true,],]\n', {"k": [[1, 2], ["a"], [], [True]]}),
    "array nested to the limit": ("k = " + "[" * MAX_DEPTH + "]" * MAX_DEPTH + "\n", None),
}

ILLEGAL = {
    "text after a value": ("k = 1\nj = 2 3\n", "line 2: unexpected text after the value"),
    "text after a header": ("[a] b\n", "line 1: unexpected text after the value"),
    "table defined twice": ("[a]\nk = 1\n[b]\n[a]\n", "line 4: table [a] is defined twice"),
    "header through a value": ("[a]\nb = 1\n[a.b]\n", "line 3: 'b' is a value, not a table"),
    "key that is already a table": ("[a.b]\n[a]\nb = 1\n", "line 3: key 'b' is defined twice"),
    "dotted key": ("a.b = 1\n", "line 1: dotted keys are not supported"),
    "missing equals sign": ("[t]\nkey value\n", "line 2: expected = after the key 'key'"),
    "missing key": ("= 1\n", "line 1: expected a key"),
    "byte order mark": ("\ufeffk = 1\n", "line 1: expected a key"),
    "header left open": ("[a\nk = 1\n", "line 1: expected ] to close the table header"),
    "array of tables": ("k = 1\n[[a]]\n", "line 2: arrays of tables"),
    "inline table": ("k = { a = 1 }\n", "line 1: unsupported value"),
    "float": ("k = 1.5\n", "line 1: unsupported value '1.5'"),
    "leading zero": ("k = 007\n", "line 1: unsupported value '007'"),
    "bare word": ("k = yes\n", "line 1: unsupported value 'yes'"),
    "missing value": ("k =\n", "line 1: unsupported value"),
    "integer one past the 64-bit limit": ("ok = 1\nk = 9223372036854775808\n", "line 2: integer is outside the 64-bit range"),
    "integer of a thousand digits": ("k = -" + "9" * 1000 + "\n", "line 1: integer is outside the 64-bit range"),
    "basic string left open": ('a = 1\nk = "abc\n', "line 2: unterminated string"),
    "basic string open at the end": ('k = "abc', "line 1: unterminated string"),
    "literal string left open": ("a = 1\nk = 'abc\nj = 2\n", "line 2: unterminated string"),
    "control character in a literal string": ("k = 'a\x01b'\n", "line 1: control character U+0001 in a string"),
    "unknown escape": ('k = "a\\qb"\n', "line 1: unsupported escape \\q"),
    "escape cut short": ('k = "\\u12"\n', "line 1: bad unicode escape"),
    "escape beyond unicode": ('k = "\\UFFFFFFFF"\n', "line 1: bad unicode escape"),
    "multi-line string": ("a = 1\nk = '''x'''\n", "line 2: multi-line strings are not supported"),
    "array left open after an item": ("a = 1\nk = [1,\n  2\n", "line 2: unterminated array"),
    "array left open at once": ("k = [", "line 1: unterminated array"),
    "array items without a comma": ("k = [1 2]\n", "line 1: expected , or ] in the array"),
    "array nested past the limit": ("a = 1\nk = " + "[" * (MAX_DEPTH + 1) + "\n", "line 2: arrays are nested more than"),
    "array nested a hundred thousand deep": ("k = " + "[" * 100000 + "\n", "line 1: arrays are nested more than"),
}


class Legal(unittest.TestCase):
    def test_unusual_but_legal_documents(self):
        for label, (text, expected) in LEGAL.items():
            with self.subTest(label):
                data = loads(text)
                if expected is not None:
                    self.assertEqual(data, expected)

    def test_array_at_the_depth_limit_keeps_every_level(self):
        data, depth = loads(LEGAL["array nested to the limit"][0])["k"], 1
        while data:
            data, depth = data[0], depth + 1
        self.assertEqual(depth, MAX_DEPTH)

    def test_legal_documents_match_tomllib(self):
        try:
            import tomllib
        except ImportError:
            self.skipTest("tomllib needs Python 3.11+")
        for label, (text, _) in LEGAL.items():
            with self.subTest(label):
                self.assertEqual(loads(text), tomllib.loads(text.replace("\r\n", "\n")))


class Illegal(unittest.TestCase):
    def test_every_rejection_names_the_line_and_the_reason(self):
        for label, (text, message) in ILLEGAL.items():
            with self.subTest(label):
                with self.assertRaises(TomlError) as ctx:
                    loads(text)
                self.assertTrue(str(ctx.exception).startswith(message), str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
