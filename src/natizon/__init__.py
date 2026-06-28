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
    "ZonDecodeError",
    "ZonError",
    "ZonInternalError",
    "ZonType",
    "loads",
)

from .exceptions import ZonDecodeError, ZonError, ZonInternalError
from .parser import EmptyContainerMode, loads
from .serializer import dumps
from .types import ZonType
