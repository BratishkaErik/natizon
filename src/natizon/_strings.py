# SPDX-FileCopyrightText: 2026 Eric Joldasov <bratishkaerik@landless-city.net>
#
# SPDX-License-Identifier: Apache-2.0

import ast
import re

# Maps exactly to the `_ESCAPE_UNICODE` rule in common_zig.lark
_UNICODE_ESCAPE_PATTERN = re.compile(r"\\u\{([0-9a-fA-F]+)}")


def decode_zig_string(s: str) -> str:
    """Decodes a valid Zig string into a native Python string."""

    def _unicode_replacer(match: re.Match) -> str:
        hex_val = match.group(1)
        # Python's \U escape expects exactly 8 padded hex digits
        return f"\\U{hex_val.zfill(8)}"

    # Translate \u{XXXX} to \U0000XXXX
    s = _UNICODE_ESCAPE_PATTERN.sub(_unicode_replacer, s)
    return ast.literal_eval(s)
