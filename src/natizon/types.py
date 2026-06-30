# SPDX-FileCopyrightText: 2026 Eric Joldasov <bratishkaerik@landless-city.net>
#
# SPDX-License-Identifier: Apache-2.0

"""Type definitions for the ZON parser and serializer."""

from collections.abc import Mapping, Sequence

__all__ = (
    "ZonEncodable",
    "ZonSerializable",
    "ZonType",
)

from enum import Enum, StrEnum
from typing import Protocol, final, runtime_checkable

# Represents any valid ZON value, including recursive collections.
type ZonType = (
    # Atomics
    None
    | str
    | int
    | float
    | bool
    # Containers
    | dict[str, ZonType]
    | list[ZonType]
    | tuple[ZonType, ...]
)

# Represents any value that can be serialized to ZON.
type ZonSerializable = (
    # Atomics
    None
    | str
    | int
    | float
    | bool
    | Enum
    # Custom types
    | ZonEncodable
    # Containers
    | Sequence[ZonSerializable]
    | Mapping[str, ZonSerializable]
)


@runtime_checkable
class ZonEncodable(Protocol):
    """Protocol for types that can be serialized to ZON."""

    def to_zon(self) -> ZonSerializable:
        """Transform the object into a ZON-serializable type."""
        ...


@final
class EmptyContainerMode(StrEnum):
    """Controls how empty ZON structures `.{}` are parsed.

    Attributes:
        DICT: Parses `.{}` as an empty dictionary `{}`.
        SEQUENCE: Parses `.{}` as an empty sequence (list `[]` or tuple `()`, depending on parser settings).
    """

    DICT = "dict"
    SEQUENCE = "sequence"
