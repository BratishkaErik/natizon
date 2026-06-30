import pytest

from natizon import dumps


@pytest.mark.parametrize(
    "indent_val, expected",
    [
        (None, ".{ .a = 1, .b = 2 }"),
        (0, ".{\n.a = 1,\n.b = 2,\n}"),
        (2, ".{\n  .a = 1,\n  .b = 2,\n}"),
        ("\t", ".{\n\t.a = 1,\n\t.b = 2,\n}"),
    ],
    ids=["compact", "zero_spaces", "two_spaces", "tab"],
)
def test_dumps_indentation_modes(indent_val, expected: str):
    """Test all indentation formatting modes on a flat dictionary."""
    obj = {"a": 1, "b": 2}
    assert dumps(obj, indent=indent_val) == expected


@pytest.mark.parametrize(
    "sort_keys, expected",
    [
        (False, ".{ .z = 1, .a = 2 }"),
        (True, ".{ .a = 2, .z = 1 }"),
    ],
    ids=["unsorted", "sorted"],
)
def test_dumps_dict_sorting(sort_keys: bool, expected: str):
    """Test dictionary serialization with and without key sorting."""
    obj = {"z": 1, "a": 2}
    assert dumps(obj, sort_keys=sort_keys) == expected
