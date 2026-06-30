# SPDX-FileCopyrightText: 2026 Eric Joldasov <bratishkaerik@landless-city.net>
#
# SPDX-License-Identifier: Apache-2.0

import ast
import re

# Maps exactly to the `_ESCAPE_UNICODE` rule in common_zig.lark
_UNICODE_ESCAPE_PATTERN = re.compile(r"\\u\{([0-9a-fA-F]+)}")


def unescape_zon_string(s: str) -> str:
    """Unescapes a ZON string or character literal into a raw Python string.

    This function handles the conversion of Zig escape sequences and
    Unicode sequences into their actual character values.

    Args:
        s: The input string containing the ZON string or character literal.
            Must include the opening and closing quotes (e.g., "content" or
            'c').

    Returns:
        The unescaped raw Python string.

    Note:
        Multiline string literals are processed via a separate pipeline in the
        transformer, as they involve line-prefix stripping rather than standard
        literal unescaping.
    """

    def _unicode_replacer(match: re.Match) -> str:
        hex_val = match.group(1)
        # Python's \U escape expects exactly 8 padded hex digits
        return f"\\U{hex_val.zfill(8)}"

    # Translate \u{XXXX} to \U0000XXXX
    s = _UNICODE_ESCAPE_PATTERN.sub(_unicode_replacer, s)
    return ast.literal_eval(s)


# Maps exactly to the `PLAIN_ID` rule in common_zig.lark
_PLAIN_ID_PATTERN = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")

# Pre-compiled translation table for str.translate() to optimize escaping performance.
# Maps integer codepoints to their escaped string representations for ZON/Zig.
_ZON_ESCAPE_TABLE = {
    ord("\\"): r"\\",
    ord('"'): r"\"",
    ord("\n"): r"\n",
    ord("\r"): r"\r",
    ord("\t"): r"\t",
}

# Populate the table with remaining non-printable ASCII control characters (0x00 - 0x1F)
_ASCII_CONTROL_MAX_EXCLUSIVE = 0x20
for codepoint in range(_ASCII_CONTROL_MAX_EXCLUSIVE):
    if codepoint not in _ZON_ESCAPE_TABLE:
        _ZON_ESCAPE_TABLE[codepoint] = f"\\x{codepoint:02x}"


def escape_zon_string(s: str) -> str:
    """Escapes a raw Python string for inclusion in a ZON string or character literal.

    This function applies the necessary escaping for quotes, backslashes,
    and non-printable ASCII characters.

    Args:
        s: The input raw Python string to be escaped.

    Returns:
        The escaped ZON string content, without surrounding quotes.

    Note:
        The resulting string is safe for inclusion as content within either
        a single-line or multiline ZON string.
    """
    return s.translate(_ZON_ESCAPE_TABLE)


# fmt: off
# https://codeberg.org/ziglang/zig-spec/src/commit/4680456aff4876ea595fee920dfcadc957b3caa4/grammar/grammar.peg
_KEYWORDS = frozenset({
    "addrspace", "align", "allowzero", "and", "anyframe",
    "anytype", "asm", "break", "callconv", "catch",
    "comptime", "const", "continue", "defer", "else",
    "enum", "errdefer", "error", "export", "extern",
    "fn", "for", "if", "inline", "linksection",
    "noalias", "noinline", "nosuspend", "opaque", "or",
    "orelse", "packed", "pub", "resume", "return",
    "struct", "suspend", "switch", "test", "threadlocal",
    "try", "union", "unreachable", "var", "volatile",
    "while"
})
# fmt: on


def can_be_plain_identifier(s: str) -> bool:
    """Checks if a string is a valid unquoted ZON identifier.

    This function determines whether the given string conforms to the syntax rules
    for plain identifiers in ZON.

    Returns:
        True if the string can be used without quotes. If False, the string
        must be represented as a quoted identifier (e.g., using the @"..." form).
    """
    return bool(_PLAIN_ID_PATTERN.match(s)) and s not in _KEYWORDS
