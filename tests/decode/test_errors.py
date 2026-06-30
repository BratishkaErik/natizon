import pytest

from natizon import ZonDecodeError, loads


@pytest.mark.parametrize(
    "bad_syntax",
    [
        "-nan",
        ".{ .key = }",
        ".{ 1, 2, .key = 3 }",
        ".{ .key = 3, 1, 2 }",
        '"unclosed string',
        "0xg",
        r"'\x7'",
        r"'\u{G}'",
        "undefined",
        "-0",
        ".{ .x = 1, .x = 2 }",
        r'.@"\x00"',
        "{}",
    ],
    ids=[
        "implicit_negative_nan",  # Grammar lacks a `-nan` branch explicitly
        "missing_assignment_value",  # Key assigned to nothing
        "array_then_keyed_mix",  # Grammar correctly forces either array_struct OR keyed_struct
        "keyed_then_array_mix",  # Mixed structs (keys first)
        "unclosed_string_quote",  # Missing closing double quote
        "invalid_hex_char",  # 'g' is not a valid hex character
        "incomplete_hex_escape",  # Hex escape sequence is too short
        "invalid_unicode_hex",  # Unicode escape contains invalid character
        "unrecognized_keyword",  # 'undefined' is not recognized in ZON
        "negative_zero_integer",  # -0 is ambigious for Zig
        "duplicate_field",  # Two or more container fields with same name
        "null_in_quoted_identifier",  # \x00 is not allowed in identifiers, only in strings
        "missing_leading_dot_for_struct",  # Structs must start with a dot
    ],
)
def test_parser_rejects_invalid_syntax(bad_syntax: str):
    """Ensures that the grammar securely catches bad syntax and throws ZonDecodeError."""
    with pytest.raises(ZonDecodeError):
        loads(bad_syntax)
