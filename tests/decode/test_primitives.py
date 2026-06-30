import math

import pytest

from natizon import loads


@pytest.mark.parametrize(
    "zon_expr, expected",
    [
        ("true", True),
        ("false", False),
        ("null", None),
    ],
    ids=["true_keyword", "false_keyword", "null_keyword"],
)
def test_keywords(zon_expr: str, expected: bool | None):
    assert loads(zon_expr) is expected


@pytest.mark.parametrize(
    "zon_expr, expected_codepoint",
    [
        ("'z'", 122),
        (r"'\t'", 9),
        (r"'\x7F'", 127),
        (r"'\u{2605}'", 9733),
    ],
    ids=["standard_char", "tab_escape", "hex_escape", "unicode_star_escape"],
)
def test_character_codepoints(zon_expr: str, expected_codepoint: int):
    assert loads(zon_expr) == expected_codepoint


@pytest.mark.parametrize(
    "zon_expr, expected_int",
    [
        ("0", 0),
        ("8675309", 8675309),
        ("-404", -404),
        ("99_999_999", 99999999),
        ("0xCAFE_BABE", 3405691582),
        ("-0X1A", -26),
        ("0o644", 420),
        ("-0O7", -7),
        ("0b1100_1100", 204),
        ("-0B1", -1),
    ],
    ids=[
        "zero",
        "positive_dec",
        "negative_dec",
        "underscores_dec",
        "positive_hex",
        "negative_hex",
        "positive_oct",
        "negative_oct",
        "positive_bin",
        "negative_bin",
    ],
)
def test_integers(zon_expr: str, expected_int: int):
    assert loads(zon_expr) == expected_int


@pytest.mark.parametrize(
    "zon_expr, expected_float",
    [
        ("0.0", 0.0),
        ("98.6", 98.6),
        ("-0.001", -0.001),
        ("1e-5", 0.00001),
        ("-3.14E+2", -314.0),
        ("0x1.fP3", 15.5),
        ("-0X0.1p-2", -0.015625),
    ],
    ids=[
        "zero",
        "positive_float",
        "negative_float",
        "sci_notation_small",
        "sci_notation_large",
        "hex_float_positive",
        "hex_float_negative",
    ],
)
def test_floats(zon_expr: str, expected_float: float):
    result = loads(zon_expr)
    assert isinstance(result, float), f"Expected float, got {type(result).__name__}"
    assert math.isclose(result, expected_float)


@pytest.mark.parametrize(
    "zon_expr, validation_fn",
    [
        ("inf", math.isinf),
        ("-inf", lambda x: math.isinf(x) and x < 0),
        ("nan", math.isnan),
    ],
    ids=["positive_infinity", "negative_infinity", "not_a_number"],
)
def test_special_float_constants(zon_expr: str, validation_fn):
    assert validation_fn(loads(zon_expr))


@pytest.mark.parametrize(
    "zon_expr, expected_str",
    [
        (r'""', ""),
        (r'"Greeting System"', "Greeting System"),
        (r'"Contains \"Quotes\""', 'Contains "Quotes"'),
        (r'"\x41\x42\x43"', "ABC"),
        (r'"\u{1F30D} Global"', "🌍 Global"),
        (r'"ab\x00c"', "ab\x00c"),
    ],
    ids=[
        "empty",
        "standard",
        "escaped_quotes",
        "hex_escapes",
        "unicode_escapes",
        "embedded_null",
    ],
)
def test_single_line_strings(zon_expr: str, expected_str: str):
    assert loads(zon_expr) == expected_str


def test_multiline_strings():
    zon_expr = r"""\\First line of text
\\Second line of text
\\    Indented third line
\\"""
    expected_str = "First line of text\nSecond line of text\n    Indented third line\n"
    assert loads(zon_expr) == expected_str


@pytest.mark.parametrize(
    "zon_expr, expected_str",
    [
        (".build_mode", "build_mode"),
        (".ReleaseFast", "ReleaseFast"),
        (r'.@"kebab-case-enum"', "kebab-case-enum"),
        (r'.@"enum with spaces"', "enum with spaces"),
    ],
    ids=["standard", "capitalized", "quoted_kebab", "quoted_spaces"],
)
def test_enum_literals(zon_expr, expected_str):
    assert loads(zon_expr) == expected_str
