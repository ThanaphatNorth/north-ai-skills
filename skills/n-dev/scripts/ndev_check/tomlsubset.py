"""A strict parser for the TOML subset `.ndev.toml` uses, so the check runs on any Python 3.8+ (tomllib is 3.11+).

Supported: comments; `[table]` and `[dotted."quoted".table]` headers; `key = value` with bare or quoted keys;
values that are "basic" strings (with escapes), 'literal' strings, integers, booleans, or arrays of those
(multi-line, trailing comma, comments inside). Anything else raises TomlError naming the line, so a file
never silently means something other than what it says: that includes an integer outside the 64-bit range
TOML promises, and arrays nested deeper than `MAX_DEPTH`. Pure."""
from __future__ import annotations

import re
from typing import Any, Dict, List, NoReturn, Set, Tuple

_BARE = re.compile(r"[A-Za-z0-9_-]+")
_TOKEN = re.compile(r"[+-]?[0-9A-Za-z_.:-]+")
_INT = re.compile(r"[+-]?(0|[1-9](_?[0-9])*)")
_ESCAPES = {'"': '"', "\\": "\\", "n": "\n", "t": "\t", "r": "\r", "b": "\b", "f": "\f"}
MAX_DEPTH = 32          # arrays inside arrays: far more than a config needs, far less than the stack holds
_INT64_DIGITS = 19      # a longer run of digits cannot fit; checked first because int() refuses huge strings


class TomlError(ValueError):
    """The text is not in the supported subset; the message starts with `line N:`."""


def _is_control(c: str) -> bool:
    """Characters TOML forbids inside strings and comments: C0 controls except tab, and DEL."""
    return (ord(c) < 0x20 and c != "\t") or c == "\x7f"


def _is_scalar(code: int) -> bool:
    """True for a Unicode scalar value: in range and not a surrogate."""
    return code <= 0x10FFFF and not 0xD800 <= code <= 0xDFFF


def loads(text: str) -> Dict[str, Any]:
    """The document as nested dicts, as `tomllib.loads` gives for the same text. TomlError otherwise."""
    return _Parser(text).document()


class _Parser:
    """A cursor over the text. Each method reads one construct at the cursor, leaves the cursor after it
    and returns its value, or raises TomlError for the cursor's line."""

    def __init__(self, text: str) -> None:
        self.s = text
        self.i = 0

    # -- position helpers ---------------------------------------------------------------------
    def line(self) -> int:
        return self.s.count("\n", 0, self.i) + 1

    def fail(self, what: str) -> NoReturn:
        """Raise TomlError for the line the cursor is on."""
        raise TomlError("line %d: %s" % (self.line(), what))

    def peek(self) -> str:
        return self.s[self.i] if self.i < len(self.s) else ""

    def skip_spaces(self) -> None:
        while self.peek() in (" ", "\t"):
            self.i += 1

    def skip_comment(self) -> None:
        while self.peek() not in ("\n", ""):
            c = self.peek()
            if c == "\r" and self.s.startswith("\r\n", self.i):
                return
            if _is_control(c):
                self.fail("control character U+%04X in a comment" % ord(c))
            self.i += 1

    def skip_blank(self) -> None:
        """Whitespace, newlines and comments: between statements and inside arrays."""
        while True:
            c = self.peek()
            if c in (" ", "\t", "\n", "\r"):
                self.i += 1
            elif c == "#":
                self.skip_comment()
            else:
                return

    def end_of_line(self) -> None:
        """Consume the rest of the line; anything on it but spaces and a comment is an error."""
        self.skip_spaces()
        if self.peek() == "#":
            self.skip_comment()
        if self.peek() == "\r":
            self.i += 1
        if self.peek() not in ("\n", ""):
            self.fail("unexpected text after the value")
        self.i += 1 if self.peek() == "\n" else 0

    # -- statements ---------------------------------------------------------------------------
    def document(self) -> Dict[str, Any]:
        """The whole document as nested dicts."""
        root: Dict[str, Any] = {}
        table = root
        seen: Set[Tuple[str, ...]] = set()
        while True:
            self.skip_blank()
            if not self.peek():
                return root
            table = self.header(root, seen) if self.peek() == "[" else self.key_value(table)

    def header(self, root: Dict[str, Any], seen: Set[Tuple[str, ...]]) -> Dict[str, Any]:
        """The table a `[a.b]` header opens, created under `root` when it is new."""
        self.i += 1
        if self.peek() == "[":
            self.fail("arrays of tables ([[...]]) are not supported")
        keys = [self.key()]
        self.skip_spaces()
        while self.peek() == ".":
            self.i += 1
            keys.append(self.key())
            self.skip_spaces()
        if self.peek() != "]":
            self.fail("expected ] to close the table header")
        self.i += 1
        if tuple(keys) in seen:   # judged before the line ends, so the error names the header's own line
            self.fail("table [%s] is defined twice" % ".".join(keys))
        seen.add(tuple(keys))
        table = root
        for k in keys:
            table = table.setdefault(k, {})
            if not isinstance(table, dict):
                self.fail("%r is a value, not a table" % k)
        self.end_of_line()
        return table

    def key_value(self, table: Dict[str, Any]) -> Dict[str, Any]:
        """Store one `key = value` in `table`, and return that table for the next statement."""
        line = self.line()
        k = self.key()
        self.skip_spaces()
        if self.peek() == ".":
            self.fail("dotted keys are not supported; use a [table] header")
        if self.peek() != "=":
            self.fail("expected = after the key %r" % k)
        self.i += 1
        self.skip_spaces()
        value = self.value()
        if k in table:
            raise TomlError("line %d: key %r is defined twice" % (line, k))
        table[k] = value
        self.end_of_line()
        return table

    # -- keys and values ----------------------------------------------------------------------
    def key(self) -> str:
        self.skip_spaces()
        c = self.peek()
        if c == '"':
            return self.basic_string()
        if c == "'":
            return self.literal_string()
        m = _BARE.match(self.s, self.i)
        if not m:
            self.fail("expected a key")
        self.i = m.end()
        return m.group(0)

    def value(self, depth: int = 0) -> Any:
        """The value at the cursor; `depth` counts the arrays it is already inside."""
        if self.s.startswith('"""', self.i) or self.s.startswith("'''", self.i):
            self.fail("multi-line strings are not supported")
        c = self.peek()
        if c == '"':
            return self.basic_string()
        if c == "'":
            return self.literal_string()
        if c == "[":
            return self.array(depth + 1)
        m = _TOKEN.match(self.s, self.i)
        token = m.group(0) if m else ""
        if token in ("true", "false"):
            self.i += len(token)
            return token == "true"
        if _INT.fullmatch(token):
            return self.integer(token)
        self.fail("unsupported value %r: use a string, integer, boolean or array" % (token or c))

    def integer(self, token: str) -> int:
        """The token as an int. An error outside the 64-bit range TOML promises, on every Python."""
        digits = token.replace("_", "")
        number = int(digits) if len(digits.lstrip("+-")) <= _INT64_DIGITS else None
        if number is None or not -2 ** 63 <= number < 2 ** 63:
            self.fail("integer is outside the 64-bit range")
        self.i += len(token)
        return number

    def basic_string(self) -> str:
        self.i += 1
        out: List[str] = []
        while True:
            c = self.peek()
            if c in ("", "\n"):
                self.fail("unterminated string")
            self.i += 1
            if c == '"':
                return "".join(out)
            if _is_control(c):
                self.fail("control character U+%04X in a string" % ord(c))
            if c != "\\":
                out.append(c)
                continue
            e = self.peek()
            self.i += 1
            if e in _ESCAPES:
                out.append(_ESCAPES[e])
            elif e in ("u", "U"):
                n = 4 if e == "u" else 8
                digits = self.s[self.i:self.i + n]
                if not re.fullmatch(r"[0-9A-Fa-f]{%d}" % n, digits) or not _is_scalar(int(digits, 16)):
                    self.fail("bad unicode escape")
                out.append(chr(int(digits, 16)))
                self.i += n
            else:
                self.fail("unsupported escape \\%s" % e)

    def literal_string(self) -> str:
        self.i += 1
        end = self.i
        while end < len(self.s) and self.s[end] not in ("'", "\n"):
            end += 1
        if end >= len(self.s) or self.s[end] != "'":
            self.fail("unterminated string")
        bad = next((c for c in self.s[self.i:end] if _is_control(c)), None)
        if bad:
            self.fail("control character U+%04X in a string" % ord(bad))
        text, self.i = self.s[self.i:end], end + 1
        return text

    def array(self, depth: int) -> List[Any]:
        """The items of the array at the cursor, which is `depth` arrays deep."""
        if depth > MAX_DEPTH:
            self.fail("arrays are nested more than %d deep" % MAX_DEPTH)
        start = self.line()
        self.i += 1
        items: List[Any] = []
        while True:
            self.skip_blank()
            if not self.peek():
                raise TomlError("line %d: unterminated array" % start)
            if self.peek() == "]":
                self.i += 1
                return items
            items.append(self.value(depth))
            self.skip_blank()
            if self.peek() == ",":
                self.i += 1
            elif self.peek() == "]":
                self.i += 1
                return items
            elif not self.peek():
                raise TomlError("line %d: unterminated array" % start)
            else:
                self.fail("expected , or ] in the array")
