# SPDX-FileCopyrightText: 2026 Eric Joldasov <bratishkaerik@landless-city.net>
#
# SPDX-License-Identifier: Apache-2.0

"""Type definitions for the ZON parser."""

__all__ = ("ZonType",)

from enum import StrEnum
from typing import final

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


@final
class EmptyContainerMode(StrEnum):
    """Controls how empty ZON structures `.{}` are parsed.

    Attributes:
        DICT: Parses `.{}` as an empty dictionary `{}`.
        SEQUENCE: Parses `.{}` as an empty sequence (list `[]` or tuple `()`, depending on parser settings).
    """

    DICT = "dict"
    SEQUENCE = "sequence"
