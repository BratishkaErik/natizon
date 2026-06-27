# SPDX-FileCopyrightText: 2026 Eric Joldasov <bratishkaerik@landless-city.net>
#
# SPDX-License-Identifier: Apache-2.0

"""ZON parser."""

__all__ = (
    "EmptyContainerMode",
    "loads",
)

import logging
from collections.abc import Mapping
from functools import lru_cache
from typing import Final, Self, final

from lark import Lark
from lark.exceptions import GrammarError, UnexpectedInput, VisitError

from ._transformer import ZonTransformer, _ZonTransformer
from .exceptions import ZonDecodeError, ZonInternalError
from .types import EmptyContainerMode, ZonType

log = logging.getLogger(__name__)


type _TransformerMap = Mapping[tuple[bool, EmptyContainerMode], _ZonTransformer]


@final
class _ZonParserImpl:
    """Cache Lark parser and stateless transformers."""

    parser: Final[Lark]
    _transformers: Final[_TransformerMap]

    def __init__(self):
        log.debug("Initializing Lark ZON parser...")

        options = {
            "parser": "lalr",
            "cache": True,
        }

        current_package = __package__ or "natizon"

        try:
            self.parser = Lark.open_from_package(
                package=current_package,
                search_paths=("grammar",),
                grammar_path="zon.lark",
                **options,
            )
        except (OSError, GrammarError, ImportError) as e:
            raise ZonInternalError(
                "Failed to load ZON grammar. The package may be corrupted."
            ) from e

        self._transformers = {
            (False, EmptyContainerMode.DICT): ZonTransformer(
                use_tuples=False, empty_mode=EmptyContainerMode.DICT
            ),
            (False, EmptyContainerMode.SEQUENCE): ZonTransformer(
                use_tuples=False, empty_mode=EmptyContainerMode.SEQUENCE
            ),
            (True, EmptyContainerMode.DICT): ZonTransformer(
                use_tuples=True, empty_mode=EmptyContainerMode.DICT
            ),
            (True, EmptyContainerMode.SEQUENCE): ZonTransformer(
                use_tuples=True, empty_mode=EmptyContainerMode.SEQUENCE
            ),
        }

    @classmethod
    @lru_cache(maxsize=1)
    def get_instance(cls) -> Self:
        return cls()

    def parse(
        self, text: str, use_tuples: bool, empty_mode: EmptyContainerMode
    ) -> ZonType:
        try:
            tree = self.parser.parse(text)
            transformer = self._transformers[(use_tuples, empty_mode)]
            return transformer.transform(tree)
        except UnexpectedInput as e:
            # Lark's UnexpectedEOF uses -1. UnexpectedToken can use '?'.
            # We normalize any non-positive integer to None.
            line = e.line if isinstance(e.line, int) and e.line > 0 else None
            column = e.column if isinstance(e.column, int) and e.column > 0 else None

            raise ZonDecodeError(
                "Syntax error in ZON text",
                original_exc=e,
                line=line,
                column=column,
            ) from e
        except VisitError as e:
            raise ZonDecodeError(
                f"Data transformation failed: {e.orig_exc!s}",
                original_exc=e.orig_exc,
            ) from e


def loads(
    text: str,
    *,
    use_tuples: bool = False,
    empty_mode: EmptyContainerMode = EmptyContainerMode.DICT,
) -> ZonType:
    """Parses a ZON string into standard Python data structures.

    Similar to `json.loads()`.

    Args:
        text: The ZON string to parse.
        use_tuples: If True, parses "ZON arrays" as tuples instead of lists.
        empty_mode: Controls whether an empty structure `.{}`
                    becomes a "dict", or a "list/tuple".

    Returns:
        ZonType: The parsed Python data structure.

    Raises:
        ZonDecodeError: If the ZON string contains invalid syntax or cannot be transformed.
        ZonInternalError: If the parser's internal grammar fails to load.
    """
    return _ZonParserImpl.get_instance().parse(
        text, use_tuples=use_tuples, empty_mode=empty_mode
    )
