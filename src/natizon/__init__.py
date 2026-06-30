# SPDX-FileCopyrightText: 2026 Eric Joldasov <bratishkaerik@landless-city.net>
#
# SPDX-License-Identifier: Apache-2.0

"""ZON (Zig Object Notation) native Python parser and serializer.

This package provides a `json`-like interface for both decoding ZON strings
into standard, native Python data structures (dicts, lists, primitives),
and encoding Python objects back into ZON-formatted strings.
"""

__all__ = (
    "dumps",
    "EmptyContainerMode",
    "loads",
    "validate_zon_serializable",
    "ZonDecodeError",
    "ZonEncodable",
    "ZonError",
    "ZonInternalError",
    "ZonSerializable",
    "ZonType",
)

from .exceptions import ZonDecodeError, ZonError, ZonInternalError
from .parser import EmptyContainerMode, loads
from .serializer import dumps, validate_zon_serializable
from .types import ZonEncodable, ZonSerializable, ZonType
