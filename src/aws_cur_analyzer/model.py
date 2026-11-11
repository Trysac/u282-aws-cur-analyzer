"""Data models for CUR analysis."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True)
class LineItem:
    """A single line item from a CUR CSV file.

    Attributes:
        line_item_type: Value of ``lineItem/LineItemType`` (CUR 1.0) or
            ``line_item_line_item_type`` (CUR 2.0).
        usage_start: Parsed usage start date/time, normalized to UTC.
        account: Payer or linked account ID.
        service: Service code (``lineItem/ProductCode``).
        region: Region code (``product/region`` or ``product_region_code``).
        unblended: Unblended cost, parsed as ``Decimal``.
        columns: Raw column mapping from original header names to string values.
    """

    line_item_type: str
    usage_start: datetime
    account: str
    service: str
    region: str
    unblended: Decimal
    columns: Mapping[str, str]


@dataclass(frozen=True)
class Coverage:
    """Tag coverage statistics.

    Attributes:
        tagged: Total cost of items with the tag.
        total: Total cost of eligible items.
        percent: Percentage = tagged / total * 100, quantized to 0.01.
    """

    tagged: Decimal
    total: Decimal
    percent: Decimal
