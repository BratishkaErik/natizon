"""Conformance tests against the official Zig ZON parser.

Verifies that the ZON strings produced by `natizon.dumps()` are accepted
by `zig ast-check --zon`. This ensures the serializer emits valid ZON
according to the reference implementation.

These tests are skipped if the `zig` executable is not found in PATH.
"""

import shutil
import subprocess
from enum import Enum

import pytest

from natizon import dumps

# Helpers


def _zig_available() -> bool:
    """Return True if a `zig` executable can be found."""
    return shutil.which("zig") is not None


def _check_zon_with_zig(zon_str: str) -> None:
    """Assert that the given ZON string passes `zig ast-check --zon`.

    Raises:
        AssertionError: If zig exits with a non-zero code.
    """
    result = subprocess.run(
        ["zig", "ast-check", "--zon", "--color", "off"],
        input=zon_str,
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        msg = (
            f"Zig rejected the ZON output (rc={result.returncode})\n"
            f"Input:\n{zon_str}\n"
            f"stderr:\n{result.stderr.strip()}"
        )
        raise AssertionError(msg)


pytestmark = [
    pytest.mark.requires_zig,
    pytest.mark.skipif(
        not _zig_available(),
        reason="zig compiler not found in PATH",
    ),
]

# Test cases – output acceptance


@pytest.mark.parametrize(
    "obj",
    [
        None,
        True,
        False,
        42,
        -7,
        3.14,
        -0.001,
        "hello",
        "line\nbreak",
        'quotes"inside',
        "tab\there",
        [],
        {},
        [1, 2, 3],
        {"a": 1, "b": 2},
        {"complex-key!": 42},
        {"space key": True},
        {"nested": {"x": 1}},
        {"inf": 1, "nan": 2},  # reserved float keywords as keys
        {"if": 1, "fn": 2, "const": 3},  # Zig keywords as keys
    ],
    ids=[
        "null",
        "true",
        "false",
        "pos_int",
        "neg_int",
        "pos_float",
        "neg_float",
        "string_plain",
        "string_newline",
        "string_quote",
        "string_tab",
        "empty_list",
        "empty_dict",
        "array_ints",
        "struct_simple",
        "struct_quoted_special",
        "struct_quoted_space",
        "struct_nested",
        "struct_inf_nan_keys",
        "struct_keywords_keys",
    ],
)
def test_dumps_output_accepted_by_zig(obj):
    """Serialized output must be valid ZON according to the Zig reference parser."""
    zon_str = dumps(obj)
    _check_zon_with_zig(zon_str)


@pytest.mark.parametrize(
    "obj",
    [
        float("nan"),
        float("inf"),
        float("-inf"),
    ],
    ids=["nan", "inf", "neg_inf"],
)
def test_special_floats_accepted(obj):
    """ZON special float literals must be accepted by Zig."""
    zon_str = dumps(obj)
    _check_zon_with_zig(zon_str)


# Enum values are serialized as .inf / .nan identifiers.
# Verify that Zig accepts those as valid enum literals inside a struct.
def test_enum_literal_inf_nan_accepted():
    """Enum members named inf/nan become ZON enum literals accepted by Zig."""

    class Special(Enum):
        inf = 1
        nan = 2

    zon_str = dumps({"limit": Special.inf, "quiet": Special.nan})
    _check_zon_with_zig(zon_str)


def test_pretty_output_accepted():
    """Pretty-printed (indented) ZON must also be accepted by Zig."""
    obj = {
        "name": "natizon",
        "version": "1.0",
        "deps": ["lark"],
    }
    zon_str = dumps(obj, indent=2)
    _check_zon_with_zig(zon_str)


@pytest.mark.parametrize(
    "invalid_zon",
    [
        "not valid zon",  # bare word
        "{ }",  # missing leading dot
        ".{ .x = }",  # missing value
        ".{ 1, 2, .x = 3 }",  # mixed array and struct
    ],
    ids=["bare_word", "no_leading_dot", "missing_value", "mixed_struct"],
)
def test_zig_rejects_invalid_zon(invalid_zon: str):
    """Zig must reject clearly invalid ZON, confirming it is actually checking."""
    with pytest.raises(AssertionError, match="Zig rejected"):
        _check_zon_with_zig(invalid_zon)
