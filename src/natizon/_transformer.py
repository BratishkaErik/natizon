# SPDX-FileCopyrightText: 2026 Eric Joldasov <bratishkaerik@landless-city.net>
#
# SPDX-License-Identifier: Apache-2.0

from typing import Final, assert_never, final

from lark import Token, Transformer, v_args

from ._strings import unescape_zon_string
from .types import EmptyContainerMode, ZonType


# Stop warnings, functions are used at runtime by Lark:
# noinspection PyMethodMayBeStatic
# ruff: noqa: PLR6301, PLR0904
@final
class _ZonTransformer(Transformer):
    """Transforms the parsed Lark Tree directly into Python data structures."""

    use_tuples: Final[bool]
    empty_mode: Final[EmptyContainerMode]

    def __init__(self, use_tuples: bool, empty_mode: EmptyContainerMode) -> None:
        super().__init__(visit_tokens=True)
        self.use_tuples = use_tuples
        self.empty_mode = empty_mode

    def plain_id(self, token: Token) -> str:
        return str(token)

    def quoted_id(self, token: Token) -> str:
        # Slices off the '@' prefix before evaluating the string literal
        val = unescape_zon_string(token.value[1:])
        if "\x00" in val:
            msg = "Identifier cannot contain null bytes"
            raise ValueError(msg)
        return val

    def single_string(self, token: Token) -> str:
        return unescape_zon_string(token.value)

    def multiline_string(self, *tokens: Token) -> str:
        cleaned_lines = (
            # Strip prefix and normalize line endings
            t.value.removeprefix("\\\\").rstrip("\r")
            for t in tokens
        )
        return "\n".join(cleaned_lines)

    def float_val(self, token: Token) -> float:
        val = token.value.replace("_", "")
        # Safely handle python's limitation with standard float(0x1.0p) via float.fromhex
        if val.lower().startswith("0x"):
            return float.fromhex(val)
        return float(val)

    def neg_float_val(self, token: Token) -> float:
        # Lark filters anonymous "-" literal; only FLOAT_LIT token is passed
        return -self.float_val(token)

    def int_val(self, token: Token) -> int:
        return int(token.value.replace("_", ""), 0)

    def neg_int_val(self, token: Token) -> int:
        val = self.int_val(token)
        if val == 0:
            msg = "Integer literal '-0' is ambiguous"
            raise ValueError(msg)
        return -val

    def nan_val(self, _: Token) -> float:
        return float("nan")

    def inf_val(self, _: Token) -> float:
        return float("inf")

    def neg_inf_val(self, _: Token) -> float:
        return float("-inf")

    def true_val(self, _: Token) -> bool:
        return True

    def false_val(self, _: Token) -> bool:
        return False

    def null_val(self, _: Token) -> None:
        return None

    def char_val(self, token: Token) -> int:
        evaluated_char = unescape_zon_string(token.value)
        return ord(evaluated_char)

    def field_init(self, identifier: str, value: ZonType) -> tuple[str, ZonType]:
        return identifier, value

    def enum_literal(self, identifier: str) -> str:
        return identifier

    def keyed_struct(self, *items: tuple[str, ZonType]) -> dict[str, ZonType]:
        result = dict(items)

        if len(result) != len(items):
            seen = set()

            for k, _ in items:
                if k in seen:
                    msg = f"Duplicate struct field name: '{k}'"
                    raise ValueError(msg)
                seen.add(k)

        return result

    def array_struct(self, *items: ZonType) -> list[ZonType] | tuple[ZonType, ...]:
        return items if self.use_tuples else list(items)

    def populated_struct(self, body: ZonType) -> ZonType:
        return body

    def empty_struct(self) -> dict[str, ZonType] | list[ZonType] | tuple[ZonType, ...]:
        match self.empty_mode:
            case EmptyContainerMode.DICT:
                return {}
            case EmptyContainerMode.SEQUENCE:
                return self.array_struct()
            case _ as unreachable:
                assert_never(unreachable)


ZonTransformer = v_args(inline=True)(_ZonTransformer)
