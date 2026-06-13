"""ZON (Zig Object Notation) native Python parser.

This package provides a `json`-like interface
for decoding ZON strings directly into standard, native
Python data structures (dicts, lists, primitives).
"""

from .exceptions import ZonDecodeError, ZonError, ZonInternalError
from .parser import EmptyContainerMode, loads
from .types import ZonType

__all__ = (
    "EmptyContainerMode",
    "ZonDecodeError",
    "ZonError",
    "ZonInternalError",
    "ZonType",
    "loads",
)
