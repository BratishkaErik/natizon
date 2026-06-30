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
