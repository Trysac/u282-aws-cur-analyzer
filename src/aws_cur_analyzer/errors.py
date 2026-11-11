"""Exception types for aws_cur_analyzer."""

from __future__ import annotations

from typing import Literal, TypeAlias

ErrorCode: TypeAlias = Literal[
    "missing_column",
    "invalid_number",
    "invalid_date",
    "too_many_rows",
    "too_many_groups",
    "invalid_group",
]


class CurError(Exception):
    """Base exception for all CUR analyzer errors.

    Attributes:
        code: Machine-readable error code, one of the values in ``ErrorCode``.
        message: Human-readable message containing row and column context.
    """

    def __init__(self, code: ErrorCode, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(message)

    def __str__(self) -> str:
        return f"{self.code}: {self.message}"
