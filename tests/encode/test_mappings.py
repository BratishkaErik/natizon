from collections import ChainMap, Counter, UserDict
from types import MappingProxyType

import pytest

from natizon import dumps, loads


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
