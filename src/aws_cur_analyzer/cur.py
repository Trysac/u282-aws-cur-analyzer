"""CSV reader for CUR files."""

from __future__ import annotations

import csv
from collections.abc import Iterator
from datetime import datetime, timezone
from decimal import Decimal
from typing import TextIO

from .columns import COLUMN_ALIASES
from .errors import CurError
from .model import LineItem

REQUIRED_LOGICAL: list[str] = [
    "line_item_type",
    "usage_start_date",
    "usage_account_id",
    "product_code",
    "region",
    "unblended_cost",
]

NUMERIC_LOGICAL: list[str] = [
    "unblended_cost",
    "savings_plan_effective_cost",
    "savings_plan_total_commitment_to_date",
    "savings_plan_used_commitment",
    "reservation_effective_cost",
    "reservation_unused_amortized_upfront_fee",
    "reservation_unused_recurring_fee",
]


def _get_actual_header(logical_name: str, header: list[str]) -> str | None:
    for alias in COLUMN_ALIASES[logical_name]:
        if alias in header:
            return alias
    return None


def _parse_usage_start(value: str, row: int, header_name: str) -> datetime:
    if not value:
        raise CurError("missing_column", f"row {row}: missing value for column '{header_name}'")
    try:
        if value.endswith("Z"):
            value = value[:-1] + "+00:00"
        dt = datetime.fromisoformat(value)
        dt = dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt.astimezone(timezone.utc)
        return dt
    except (ValueError, TypeError) as e:
        snippet = value[:50] + ("..." if len(value) > 50 else "")
        raise CurError(
            "invalid_date",
            f"row {row}: invalid date for column '{header_name}': {snippet}",
        ) from e


def _parse_decimal_or_zero(
    value: str, row: int, header_name: str, required: bool = False
) -> Decimal:
    if value == "":
        if required:
            raise CurError(
                "missing_column",
                f"row {row}: missing value for required column '{header_name}'",
            )
        return Decimal("0")
    try:
        return Decimal(value)
    except Exception as e:
        snippet = value[:50] + ("..." if len(value) > 50 else "")
        raise CurError(
            "invalid_number",
            f"row {row}: invalid number for column '{header_name}': {snippet}",
        ) from e


def read_cur(
    stream: TextIO,
    *,
    max_rows: int = 10_000_000,
    max_field_chars: int = 131_072,
) -> Iterator[LineItem]:
    """Parse a CUR CSV stream and yield :class:`LineItem` objects.

    Args:
        stream: A text stream (e.g., open file) containing CSV data.
        max_rows: Maximum number of data rows to process. Raises
            ``CurError('too_many_rows')`` if exceeded.
        max_field_chars: Maximum field size for the CSV parser. The global
            ``csv.field_size_limit`` is temporarily set to this value and
            restored when the generator is closed.

    Yields:
        One :class:`LineItem` per CSV data row.

    Raises:
        CurError: With appropriate code if required columns are missing,
            numbers are invalid, dates are invalid, or row limit is exceeded.
    """
    old_limit = csv.field_size_limit()
    csv.field_size_limit(max_field_chars)
    try:
        reader = csv.reader(stream)
        try:
            header = next(reader)
        except StopIteration:
            raise CurError("missing_column", "CSV file is empty (no header row)") from None
        if header and header[0].startswith("\ufeff"):
            header[0] = header[0][1:]
        header = [h.strip() for h in header]

        required_actual: dict[str, str] = {}
        missing: list[str] = []
        for logical in REQUIRED_LOGICAL:
            actual = _get_actual_header(logical, header)
            if actual is None:
                missing.append(logical)
            else:
                required_actual[logical] = actual
        if missing:
            raise CurError("missing_column", f"Missing required column(s): {', '.join(missing)}")

        numeric_actual: dict[str, str] = {}
        for logical in NUMERIC_LOGICAL:
            actual = _get_actual_header(logical, header)
            if actual is not None:
                numeric_actual[logical] = actual

        row_count = 0
        for row in reader:
            row_count += 1
            if row_count > max_rows:
                raise CurError("too_many_rows", f"Exceeded max_rows={max_rows} at row {row_count}")
            if len(row) < len(header):
                row = list(row) + [""] * (len(header) - len(row))
            elif len(row) > len(header):
                row = row[: len(header)]
            columns = dict(zip(header, row, strict=False))

            line_item_type = columns.get(required_actual["line_item_type"], "")
            if not line_item_type:
                raise CurError(
                    "missing_column",
                    f"row {row_count}: missing value for required column "
                    f"'{required_actual['line_item_type']}'",
                )

            usage_start_str = columns.get(required_actual["usage_start_date"], "")
            usage_start = _parse_usage_start(
                usage_start_str, row_count, required_actual["usage_start_date"]
            )

            account = columns.get(required_actual["usage_account_id"], "")
            if not account:
                raise CurError(
                    "missing_column",
                    f"row {row_count}: missing value for required column "
                    f"'{required_actual['usage_account_id']}'",
                )

            service = columns.get(required_actual["product_code"], "")
            if not service:
                raise CurError(
                    "missing_column",
                    f"row {row_count}: missing value for required column "
                    f"'{required_actual['product_code']}'",
                )

            region = columns.get(required_actual["region"], "")
            if not region:
                raise CurError(
                    "missing_column",
                    f"row {row_count}: missing value for required column "
                    f"'{required_actual['region']}'",
                )

            unblended_str = columns.get(required_actual["unblended_cost"], "")
            unblended = _parse_decimal_or_zero(
                unblended_str, row_count, required_actual["unblended_cost"], required=True
            )

            for logical, header_name in numeric_actual.items():
                if logical == "unblended_cost":
                    continue
                raw = columns.get(header_name, "")
                if raw != "":
                    try:
                        Decimal(raw)
                    except Exception as e:
                        snippet = raw[:50] + ("..." if len(raw) > 50 else "")
                        raise CurError(
                            "invalid_number",
                            f"row {row_count}: invalid number for column "
                            f"'{header_name}': {snippet}",
                        ) from e

            yield LineItem(
                line_item_type=line_item_type,
                usage_start=usage_start,
                account=account,
                service=service,
                region=region,
                unblended=unblended,
                columns=columns,
            )
    finally:
        csv.field_size_limit(old_limit)
