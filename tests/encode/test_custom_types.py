from enum import Enum

import pytest

from natizon import dumps, validate_zon_serializable


class SimpleEncodable:
    def __init__(self, name: str):
        self.name = name

    def to_zon(self):
        return {"name": self.name}


class RecursiveEncodable:
    def to_zon(self):
        _ = self
        return {"a": [1, 2]}


class CircularEncodable:
    def to_zon(self):
        return self


def test_dumps_encodable_simple():
    obj = SimpleEncodable("natizon")
    assert dumps(obj) == '.{ .name = "natizon" }'


def test_dumps_encodable_recursive():
    obj = RecursiveEncodable()
    assert dumps(obj) == ".{ .a = .{ 1, 2 } }"


def test_validate_encodable_circular():
    obj = CircularEncodable()
    with pytest.raises(ValueError, match="circular reference"):
        validate_zon_serializable(obj)


# Priority tests: ZonEncodable trumps built-in types


class StrWithZon(str):
    """A str subclass that also implements ZonEncodable."""

    def to_zon(self):
        return {"type": "custom_str", "value": str(self)}


class IntWithZon(int):
    """An int subclass that also implements ZonEncodable."""

    def to_zon(self):
        return {"type": "custom_int", "value": int(self)}


class EnumWithZon(Enum):
    A = 1

    def to_zon(self):
        return {"type": "custom_enum", "name": self.name}


def test_zon_encodable_overrides_str():
    """ZonEncodable takes precedence over built-in str serialization."""
    obj = StrWithZon("hello")
    assert dumps(obj) == '.{ .type = "custom_str", .value = "hello" }'


def test_zon_encodable_overrides_int():
    """ZonEncodable takes precedence over built-in int serialization."""
    obj = IntWithZon(42)
    assert dumps(obj) == '.{ .type = "custom_int", .value = 42 }'


def test_zon_encodable_overrides_enum():
    """ZonEncodable takes precedence over built-in enum literal serialization."""
    assert dumps(EnumWithZon.A) == '.{ .type = "custom_enum", .name = "A" }'
