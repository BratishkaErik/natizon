from collections import ChainMap, Counter, UserDict, UserList, deque, namedtuple
from types import MappingProxyType

import pytest

from natizon import dumps, loads


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


@pytest.mark.parametrize(
    "obj, expected",
    [
        ([], ".{}"),
        ((), ".{}"),
        (deque(), ".{}"),
        (UserList(), ".{}"),
        ([1, 2, 3], ".{ 1, 2, 3 }"),
        ((True, False, None), ".{ true, false, null }"),
        (deque([1, 2]), ".{ 1, 2 }"),
        (UserList([3, 4]), ".{ 3, 4 }"),
        (range(1, 4), ".{ 1, 2, 3 }"),
        (bytearray([5, 6]), ".{ 5, 6 }"),
        (namedtuple("Point", ["x", "y"])(1, 2), ".{ 1, 2 }"),
    ],
    ids=[
        "empty_list",
        "empty_tuple",
        "empty_deque",
        "empty_userlist",
        "flat_list",
        "flat_tuple",
        "flat_deque",
        "flat_userlist",
        "lazy_range",
        "bytearray_sequence",
        "named_tuple",
    ],
)
def test_dumps_sequences(obj, expected: str):
    """Test serialization of various Sequence implementations."""
    assert dumps(obj) == expected


@pytest.mark.parametrize(
    "obj, expected",
    [
        ({}, ".{}"),
        (UserDict(), ".{}"),
        ({"key": "value"}, '.{ .key = "value" }'),
        ({"complex-key!": 42}, '.{ .@"complex-key!" = 42 }'),
        ({"space key": True}, '.{ .@"space key" = true }'),
        ({"nested": {"x": 1}}, ".{ .nested = .{ .x = 1 } }"),
        (MappingProxyType({"immutable": True}), ".{ .immutable = true }"),
        (ChainMap({"a": 1}, {"b": 2}), ".{ .b = 2, .a = 1 }"),
        (Counter(a=1), ".{ .a = 1 }"),
    ],
    ids=[
        "empty",
        "empty_userdict",
        "plain_id",
        "quoted_special",
        "quoted_space",
        "nested",
        "mapping_proxy",
        "chain_map",
        "counter_map",
    ],
)
def test_dumps_dicts(obj, expected: str):
    """Test serialization of various Mapping implementations."""
    assert dumps(obj) == expected


def test_integration_sanity():
    """Test that unambiguous dumped native structures can be parsed back.

    Note: Empty sequences ([]) serialize to `.{}`. Under default loads()
    settings (EmptyContainerMode.DICT), `.{}` parses back as `{}`.
    We intentionally do not guarantee strict roundtripping for ambiguous ZON structures.
    """
    original = {
        "name": "natizon",
        "version": 1.5,
        "features": ["parsing", "serializing"],
        "metadata": {
            "complex-key!": True,
            "empty_dict": {},
        },
    }

    # Dump to ZON string, then load back to Python dict
    zon_string = dumps(original)
    restored = loads(zon_string)

    assert original == restored


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


def test_dumps_indent_negative_raises():
    """Ensure negative indent integers trigger a ValueError."""
    with pytest.raises(ValueError):
        dumps({"a": 1}, indent=-1)


def test_dumps_unserializable_types():
    """Ensure TypeError is raised for unsupported types."""

    class CustomObj:
        pass

    with pytest.raises(TypeError, match="is not ZON serializable"):
        dumps(CustomObj())


def test_dumps_unserializable_values():
    """Test that circular references raise ValueError."""
    # Cyclic sequence
    cyclic_list: list[object] = []
    cyclic_list.append(cyclic_list)
    with pytest.raises(ValueError, match="circular reference detected in ZON sequence"):
        dumps(cyclic_list)

    # Cyclic mapping
    cyclic_dict: dict[str, object] = {"a": 1}
    cyclic_dict["self"] = cyclic_dict
    with pytest.raises(
        ValueError, match="circular reference detected in ZON dictionary"
    ):
        dumps(cyclic_dict)

    # Safe duplicate references
    shared_obj = {"shared": "data"}
    safe_nested = [shared_obj, shared_obj]
    assert dumps(safe_nested) == '.{ .{ .shared = "data" }, .{ .shared = "data" } }'
