# SPDX-FileCopyrightText: 2026 Eric Joldasov <bratishkaerik@landless-city.net>
#
# SPDX-License-Identifier: Apache-2.0

"""ZON (Zig Object Notation) native Python parser.

This package provides a `json`-like interface
for decoding ZON strings directly into standard, native
Python data structures (dicts, lists, primitives).
"""

__all__ = (
    "EmptyContainerMode",
    "ZonDecodeError",
    "ZonError",
    "ZonInternalError",
    "ZonType",
    "loads",
)

from .exceptions import ZonDecodeError, ZonError, ZonInternalError
from .parser import EmptyContainerMode, loads
from .types import ZonType
