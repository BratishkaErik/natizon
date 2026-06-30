import pytest

from natizon import dumps


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
