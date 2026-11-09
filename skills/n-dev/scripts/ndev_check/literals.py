"""Blank out string-literal contents in one line of code, so a scan sees only code. Pure."""
from __future__ import annotations


def blank_strings(line: str) -> str:
    """The line with the characters inside '...', "..." and `...` replaced by spaces (quotes kept).
    Escapes are honoured; a literal left open runs to the end of the line."""
    out, quote, escaped = [], "", False
    for c in line:
        if quote:
            closing = c == quote and not escaped
            out.append(c if closing else " ")
            quote = "" if closing else quote
            escaped = c == "\\" and not escaped
        else:
            out.append(c)
            quote = c if c in "\"'`" else ""
    return "".join(out)
