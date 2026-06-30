from collections import UserList, deque, namedtuple

import pytest

from natizon import dumps


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
