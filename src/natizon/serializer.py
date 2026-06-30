# SPDX-FileCopyrightText: 2026 Eric Joldasov <bratishkaerik@landless-city.net>
#
# SPDX-License-Identifier: Apache-2.0

"""ZON serializer."""

__all__ = (
    "dumps",
    "validate_zon_serializable",
)

import math
from collections.abc import Mapping, Sequence
from enum import Enum, Flag
from typing import Final, cast, final

from ._strings import can_be_plain_identifier, escape_zon_string
from .types import ZonSerializable


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
    def _format_identifier(name: str) -> str:
        if can_be_plain_identifier(name):
            return f".{name}"
        escaped = escape_zon_string(name)
        return f'.@"{escaped}"'

    @staticmethod
    def _format_float(val: float) -> str:
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

    def _format_sequence(self, seq: Sequence[ZonSerializable], level: int) -> str:
        if not seq:
            return ".{}"

        lines = [self.dump(item, level + 1) for item in seq]
        return self._braces(lines, level)

    def _format_mapping(self, d: Mapping[str, ZonSerializable], level: int) -> str:
        if not d:
            return ".{}"

        items = sorted(d.items()) if self.sort_keys else list(d.items())
        lines = [
            f"{self._format_identifier(k)} = {self.dump(v, level + 1)}"
            for k, v in items
        ]
        return self._braces(lines, level)

    def dump(self, current_obj: ZonSerializable, level: int = 0) -> str:
        """Recursively serialize an object based on its type."""
        result: str
        match current_obj:
            case None:
                result = "null"
            case bool():
                result = "true" if current_obj else "false"
            case Flag():
                obj_type = type(current_obj).__name__
                msg = f"Object of type {obj_type!r}  is not ZON serializable (Flag/IntFlag serialization is ambiguous)"
                raise TypeError(msg)
            case Enum():
                result = self._format_identifier(current_obj.name)
            case int():
                result = str(current_obj)
            case float():
                result = self._format_float(current_obj)
            case str():
                result = f'"{escape_zon_string(current_obj)}"'
            case Mapping() as d:
                result = self._format_mapping(d, level)
            case Sequence() as seq:
                result = self._format_sequence(seq, level)
            case _:
                obj_type = type(current_obj).__name__
                msg = f"object of type {obj_type!r} is not ZON serializable"
                raise TypeError(msg)

        return result


def _validate_zon_serializable_impl(obj: object, seen_ids: set[int]) -> None:
    match obj:
        case Flag():
            obj_type = type(obj).__name__
            msg = f"Object of type {obj_type!r}  is not ZON serializable (Flag/IntFlag serialization is ambiguous)"
            raise TypeError(msg)

        case None | Enum() | str() | int() | float() | bool():
            return

        case Mapping():
            obj_id = id(obj)
            if obj_id in seen_ids:
                msg = "circular reference detected in ZON dictionary"
                raise ValueError(msg)
            seen_ids.add(obj_id)

            try:
                for k, v in obj.items():
                    if not isinstance(k, str):
                        k_type = type(k).__name__
                        msg = f"ZON dictionary keys must be strings, found {k_type!r}"
                        raise TypeError(msg)
                    _validate_zon_serializable_impl(v, seen_ids)
            finally:
                seen_ids.remove(obj_id)

        case Sequence():
            obj_id = id(obj)
            if obj_id in seen_ids:
                msg = "circular reference detected in ZON sequence"
                raise ValueError(msg)
            seen_ids.add(obj_id)

            try:
                for item in obj:
                    _validate_zon_serializable_impl(item, seen_ids)
            finally:
                seen_ids.remove(obj_id)

        case _:
            obj_type = type(obj).__name__
            msg = f"object of type {obj_type!r} is not ZON serializable"
            raise TypeError(msg)


def validate_zon_serializable(obj: object, /) -> None:
    """Recursively validate that an object can be serialized with `dumps` function to ZON.

    Raises:
        TypeError: If the object or any nested element is not serializable to ZON.
        ValueError: If a circular reference is detected.
    """
    _validate_zon_serializable_impl(obj, set())


def dumps(
    obj: object,
    /,
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
        ValueError: If indent is a negative integer, or a circular reference is detected.
    """
    validate_zon_serializable(obj)
    serializable_obj = cast(ZonSerializable, obj)

    indent_str = ""
    is_pretty = indent is not None

    if isinstance(indent, int):
        if indent < 0:
            msg = f"indent must be a non-negative integer, got {indent!r}"
            raise ValueError(msg)
        indent_str = " " * indent
    elif isinstance(indent, str):
        indent_str = indent

    serializer = _ZonSerializer(
        indent_str=indent_str,
        is_pretty=is_pretty,
        sort_keys=sort_keys,
    )
    return serializer.dump(serializable_obj)
