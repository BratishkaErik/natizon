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
