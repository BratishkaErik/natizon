# SPDX-FileCopyrightText: 2026 Eric Joldasov <bratishkaerik@landless-city.net>
#
# SPDX-License-Identifier: Apache-2.0

"""ZON serializer."""

__all__ = ("dumps",)

import math
from typing import Any, Final, final

from ._strings import can_be_plain_identifier, escape_zon_string
from .types import ZonType


@final
class _ZonSerializer:
    """Internal stateful serializer for ZON data."""

    indent_str: Final[str]
    is_pretty: Final[bool]
    sort_keys: Final[bool]

    def __init__(self, indent_str: str, is_pretty: bool, sort_keys: bool) -> None:
        self.indent_str = indent_str
        self.is_pretty = is_pretty
        self.sort_keys = sort_keys

    @staticmethod
    def _format_key(key: str) -> str:
        if can_be_plain_identifier(key):
            return f".{key}"
        escaped = escape_zon_string(key)
        return f'.@"{escaped}"'

    @staticmethod
    def _dump_float(val: float) -> str:
        if math.isnan(val):
            return "nan"
        if math.isinf(val):
            return "-inf" if val < 0 else "inf"
        return str(val)

    def _braces(self, lines: list[str], level: int) -> str:
        if not lines:
            return ".{}"

        if self.is_pretty:
            inner = self.indent_str * (level + 1)
            indent = self.indent_str * level
            body = ",\n".join(f"{inner}{line}" for line in lines)
            return f".{{\n{body},\n{indent}}}"

        return f".{{ {', '.join(lines)} }}"

    def _dump_sequence(
        self, seq: list[ZonType] | tuple[ZonType, ...], level: int
    ) -> str:
        if not seq:
            return ".{}"

        lines = [self.dump(item, level + 1) for item in seq]
        return self._braces(lines, level)

    def _dump_dict(self, d: dict[str, ZonType], level: int) -> str:
        if not d:
            return ".{}"

        items = sorted(d.items()) if self.sort_keys else list(d.items())
        lines = [f"{self._format_key(k)} = {self.dump(v, level + 1)}" for k, v in items]
        return self._braces(lines, level)

    def dump(self, current_obj: ZonType, level: int = 0) -> str:
        """Recursively serialize an object based on its type."""
        result: str
        match current_obj:
            case None:
                result = "null"
            case bool():
                result = "true" if current_obj else "false"
            case int():
                result = str(current_obj)
            case float():
                result = self._dump_float(current_obj)
            case str():
                result = f'"{escape_zon_string(current_obj)}"'
            case list() | tuple() as seq:
                result = self._dump_sequence(seq, level)
            case dict() as d:
                result = self._dump_dict(d, level)
            case _:
                obj_type = type(current_obj).__name__
                msg = f"Object of type {obj_type} is not ZON serializable"
                raise TypeError(msg)

        return result


def dumps(
    obj: Any,
    *,
    indent: int | str | None = None,
    sort_keys: bool = False,
) -> str:
    r"""Serialize a Python object to a ZON formatted string.

    Similar to `json.dumps()`.

    Args:
        obj: The Python object to serialize.
        indent: If a non-negative integer, indents with that many spaces per level.
                If a string (like "\t"), uses that string to indent each level.
                If None, outputs a compact, single-line representation.
        sort_keys: If True, dictionary keys are output in sorted order.

    Returns:
        The ZON string representation.

    Raises:
        TypeError: If the object is not serializable to ZON.
        ValueError: If indent is a negative integer.
    """
    indent_str = ""
    is_pretty = indent is not None

    if isinstance(indent, int):
        if indent < 0:
            msg = "indent must be a non-negative integer"
            raise ValueError(msg)
        indent_str = " " * indent
    elif isinstance(indent, str):
        indent_str = indent

    serializer = _ZonSerializer(
        indent_str=indent_str,
        is_pretty=is_pretty,
        sort_keys=sort_keys,
    )
    return serializer.dump(obj)
