import pytest

from natizon import dumps


@pytest.mark.parametrize(
    "obj, expected",
    [
        (None, "null"),
        (True, "true"),
        (False, "false"),
        (42, "42"),
        (-99, "-99"),
        (3.14, "3.14"),
        (-0.001, "-0.001"),
    ],
    ids=["null", "true", "false", "pos_int", "neg_int", "pos_float", "neg_float"],
)
def test_dumps_primitives(obj, expected: str):
    """Test serialization of standard primitive types."""
    assert dumps(obj) == expected


@pytest.mark.parametrize(
    "obj, validation_fn",
    [
        (float("nan"), lambda s: s == "nan"),
        (float("inf"), lambda s: s == "inf"),
        (float("-inf"), lambda s: s == "-inf"),
    ],
    ids=["nan", "inf", "neg_inf"],
)
def test_dumps_special_floats(obj, validation_fn):
    """Test serialization of IEEE 754 special float values."""
    assert validation_fn(dumps(obj))


@pytest.mark.parametrize(
    "obj, expected",
    [
        ("", '""'),
        ("hello", '"hello"'),
        ("line\nbreak", r'"line\nbreak"'),
        ('quotes"inside', r'"quotes\"inside"'),
        ("tab\tspace", r'"tab\tspace"'),
    ],
    ids=["empty", "plain", "newline", "quotes", "tabs"],
)
def test_dumps_strings(obj: str, expected: str):
    """Test serialization and escaping of strings."""
    assert dumps(obj) == expected
