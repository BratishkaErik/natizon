from enum import Enum, Flag, IntEnum, StrEnum

import pytest

from natizon import dumps


class Color(Enum):
    RED = 1
    BLUE = 2


class Status(IntEnum):
    ACTIVE = 1
    INACTIVE = 0


class Mode(StrEnum):
    PROD = "prod"
    DEV = "dev"


class ReservedName(Enum):
    comptime = 1


@pytest.mark.parametrize(
    "obj, expected",
    [
        (Color.RED, ".RED"),
        (Status.ACTIVE, ".ACTIVE"),
        (Mode.PROD, ".PROD"),
        (ReservedName.comptime, '.@"comptime"'),
    ],
    ids=["standard_enum", "int_enum", "str_enum", "quoted_identifier"],
)
def test_dumps_enums(obj, expected: str):
    assert dumps(obj) == expected


def test_dumps_flags_raises():
    class Permissions(Flag):
        READ = 1
        WRITE = 2

    with pytest.raises(TypeError, match="serialization is ambiguous"):
        dumps(Permissions.READ)


class SpecialFloatEnum(Enum):
    inf = 1
    nan = 2


@pytest.mark.parametrize(
    "member, expected",
    [
        (SpecialFloatEnum.inf, ".inf"),
        (SpecialFloatEnum.nan, ".nan"),
    ],
    ids=["enum_inf", "enum_nan"],
)
def test_dumps_enum_special_float_keywords(member, expected: str):
    """Test that enum members named inf and nan are serialized as ZON enum literals."""
    assert dumps(member) == expected
