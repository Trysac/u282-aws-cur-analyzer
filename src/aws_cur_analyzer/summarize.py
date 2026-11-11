"""Aggregation and rendering of CUR line items."""

from __future__ import annotations

import json
from collections.abc import Iterable, Sequence
from datetime import timezone
from decimal import ROUND_HALF_UP, Decimal
from typing import Literal, cast

from .amortization import amortized_cost
from .errors import CurError
from .model import Coverage, LineItem

TAG_COLUMN_PREFIX = "resourceTags/user:"


def _get_tag_value(line: LineItem, key: str) -> str:
    col_name = f"{TAG_COLUMN_PREFIX}{key}"
    return line.columns.get(col_name, "") or ""


def _group_key(item: LineItem, field: str) -> str:
    if field in ("service", "account", "region", "line_item_type"):
        return str(getattr(item, field))
    if field == "day":
        return item.usage_start.astimezone(timezone.utc).strftime("%Y-%m-%d")
    if field == "month":
        return item.usage_start.astimezone(timezone.utc).strftime("%Y-%m")
    if field.startswith("tag:"):
        key = field[4:]
        val = _get_tag_value(item, key)
        return val if val else "(untagged)"
    raise CurError("invalid_group", f"Unknown group field: {field}")


def summarize(
    items: Iterable[LineItem],
    *,
    by: Sequence[str],
    basis: Literal["amortized", "unblended"] = "amortized",
    max_groups: int = 100_000,
) -> list[tuple[str | Decimal, ...]]:
    """Aggregate line items by the given fields.

    Args:
        items: Iterable of :class:`LineItem` objects.
        by: Sequence of group field names. Supported fields: ``service``,
            ``account``, ``region``, ``line_item_type``, ``day``,
            ``month``, or ``tag:<key>``.
        basis: Cost basis to aggregate; ``'amortized'`` or ``'unblended'``.
        max_groups: Maximum number of distinct groups; raises
            ``CurError('too_many_groups')`` if exceeded.

    Returns:
        A list of tuples where each tuple contains the group values (in the
        order of ``by``) followed by the total cost as the last element.
        The list is sorted by total descending, then by group values ascending.

    Raises:
        CurError: If ``basis`` or a group field is invalid, or if the number of
            groups exceeds ``max_groups``.
    """
    if basis not in ("amortized", "unblended"):
        raise CurError("invalid_group", f"Invalid basis: {basis}")
    if not by:
        raise CurError("invalid_group", "by must not be empty")
    if not isinstance(by, Sequence):
        raise CurError("invalid_group", "by must be a sequence of strings")

    groups: dict[tuple[str, ...], Decimal] = {}
    for item in items:
        key_values = []
        for field in by:
            key_values.append(_group_key(item, field))
        key = tuple(key_values)
        if key not in groups:
            if len(groups) >= max_groups:
                raise CurError(
                    "too_many_groups",
                    f"Number of groups exceeds max_groups ({max_groups})",
                )
            groups[key] = Decimal("0")
        cost = amortized_cost(item) if basis == "amortized" else item.unblended
        groups[key] += cost

    sorted_items = sorted(groups.items(), key=lambda kv: (-kv[1], kv[0]))
    result: list[tuple[str | Decimal, ...]] = [(*key, total) for key, total in sorted_items]
    return result


def tag_coverage(
    items: Iterable[LineItem],
    key: str,
    *,
    basis: Literal["amortized", "unblended"] = "amortized",
) -> Coverage:
    """Compute tag coverage for the given tag key.

    Only line items of type ``Usage``, ``SavingsPlanCoveredUsage``, and
    ``DiscountedUsage`` are included in the denominator.

    Args:
        items: Iterable of :class:`LineItem` objects.
        key: Tag key (without ``resourceTags/user:`` prefix).
        basis: Cost basis; ``'amortized'`` or ``'unblended'``.

    Returns:
        A :class:`Coverage` instance with ``tagged``, ``total``, and
        ``percent`` (quantized to 0.01, rounded half up).
    """
    tagged = Decimal("0")
    total = Decimal("0")
    relevant_types = {"Usage", "SavingsPlanCoveredUsage", "DiscountedUsage"}
    for item in items:
        if item.line_item_type not in relevant_types:
            continue
        cost = amortized_cost(item) if basis == "amortized" else item.unblended
        total += cost
        if _get_tag_value(item, key):
            tagged += cost
    if total == 0:
        percent = Decimal("0")
    else:
        percent = (tagged / total * 100).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return Coverage(tagged=tagged, total=total, percent=percent)


def render(
    rows: Sequence[tuple[str | Decimal, ...]],
    fmt: Literal["text", "json"],
) -> str:
    """Render aggregation rows as text or JSON.

    Args:
        rows: Sequence of tuples, where each tuple contains group values
            followed by a :class:`Decimal` total as the last element.
        fmt: ``'text'`` for tab-separated output (totals quantized to 0.01),
            ``'json'`` for a JSON array of arrays with amounts as strings.

    Returns:
        The rendered string.

    Raises:
        CurError: If ``fmt`` is invalid.
    """
    if fmt == "text":
        lines = []
        for row in rows:
            fields = [str(f) for f in row[:-1]]
            total = cast(Decimal, row[-1])
            quantized = total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            fields.append(str(quantized))
            lines.append("\t".join(fields))
        return "\n".join(lines) + ("\n" if lines else "")
    elif fmt == "json":
        json_rows = []
        for row in rows:
            json_rows.append([str(field) for field in row])
        return json.dumps(json_rows)
    else:
        raise CurError("invalid_group", f"Invalid format: {fmt}")
