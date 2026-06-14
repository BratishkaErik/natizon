# SPDX-FileCopyrightText: 2026 Eric Joldasov <bratishkaerik@landless-city.net>
#
# SPDX-License-Identifier: Apache-2.0

"""Exceptions for the ZON parser."""


class ZonError(Exception):
    """Base exception for all ZON-related errors."""


class ZonInternalError(ZonError, RuntimeError):
    """Raised when the ZON parser fails to initialize.

    Note: most likely this is a bug or corruption in the `natizon` package,
    not an error on the user side. Recommended to report to upstream,
    unless you know what you're doing.
    """


class ZonDecodeError(ZonError, ValueError):
    """Raised when a ZON string cannot be parsed.

    Similar to `json.JSONDecodeError`.

    Attributes:
        original_exc: The underlying exception caught during parsing or transformation.
        line: The line number where the error occurred, if available.
        column: The column number where the error occurred, if available.
    """

    original_exc: Exception
    line: int | None
    column: int | None

    def __init__(
        self,
        message: str,
        original_exc: Exception,
        line: int | None = None,
        column: int | None = None,
    ) -> None:
        """Initialize the ZON decode error.

        Args:
            message: A description of the decode error.
            original_exc: The underlying exception caught during parsing.
            line: The line number where the error occurred (1-indexed).
            column: The column number where the error occurred (1-indexed).
        """
        super().__init__(f"Failed to decode ZON: {message}")
        self.original_exc = original_exc
        self.line = line
        self.column = column
