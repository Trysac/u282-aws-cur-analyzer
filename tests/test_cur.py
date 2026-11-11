"""Tests for cur.read_cur."""

from __future__ import annotations

import io
from decimal import Decimal

import pytest

from aws_cur_analyzer import CurError, read_cur


def _csv_with_cur1(rows: list[str], extra_header: str = "") -> str:
    header = [
        "lineItem/LineItemType",
        "lineItem/UsageStartDate",
        "lineItem/UsageAccountId",
        "lineItem/ProductCode",
        "product/region",
        "lineItem/UnblendedCost",
    ]
    if extra_header:
        header.append(extra_header)
    lines = [",".join(header)]
    for row in rows:
        parts = row.split(",")
        if len(parts) < len(header):
            parts += [""] * (len(header) - len(parts))
        lines.append(",".join(parts))
    return "\n".join(lines) + "\n"


def test_read_cur_basic() -> None:
    csv_text = _csv_with_cur1(
        [
            "Usage,2026-10-01T00:00:00Z,111111111111,AmazonEC2,us-east-1,10.00",
            "SavingsPlanCoveredUsage,2026-10-01T00:00:00Z,111111111111,AmazonEC2,us-east-1,5.00",
        ]
    )
    items = list(read_cur(io.StringIO(csv_text)))
    assert len(items) == 2
    first = items[0]
    assert first.line_item_type == "Usage"
    assert first.account == "111111111111"
    assert first.service == "AmazonEC2"
    assert first.region == "us-east-1"
    assert first.unblended == Decimal("10.00")
    assert first.usage_start.isoformat() == "2026-10-01T00:00:00+00:00"
    assert "lineItem/UnblendedCost" in first.columns


def test_read_cur_bom_and_crlf() -> None:
    header = "\ufefflineItem/LineItemType,lineItem/UsageStartDate,lineItem/UsageAccountId,lineItem/ProductCode,product/region,lineItem/UnblendedCost"
    row = "Usage,2026-10-01T00:00:00Z,111111111111,AmazonEC2,us-east-1,10.00"
    csv_text = header + "\r\n" + row + "\r\n"
    items = list(read_cur(io.StringIO(csv_text)))
    assert len(items) == 1
    assert items[0].line_item_type == "Usage"


def test_read_cur_missing_column() -> None:
    csv_text = "lineItem/LineItemType,lineItem/UsageStartDate,lineItem/UsageAccountId,lineItem/ProductCode,product/region\n"
    csv_text += "Usage,2026-10-01T00:00:00Z,111111111111,AmazonEC2,us-east-1\n"
    with pytest.raises(CurError) as exc_info:
        list(read_cur(io.StringIO(csv_text)))
    assert exc_info.value.code == "missing_column"


def test_read_cur_invalid_number() -> None:
    csv_text = _csv_with_cur1(["Usage,2026-10-01T00:00:00Z,111111111111,AmazonEC2,us-east-1,abc"])
    with pytest.raises(CurError) as exc_info:
        list(read_cur(io.StringIO(csv_text)))
    assert exc_info.value.code == "invalid_number"
    assert "row 1" in exc_info.value.message  # first data row is row 1


def test_read_cur_invalid_number_names_row_three() -> None:
    csv_text = _csv_with_cur1(
        [
            "Usage,2026-10-01T00:00:00Z,111111111111,AmazonEC2,us-east-1,10.00",
            "Usage,2026-10-01T00:00:00Z,111111111111,AmazonEC2,us-east-1,20.00",
            "Usage,2026-10-01T00:00:00Z,111111111111,AmazonEC2,us-east-1,abc",
        ]
    )
    with pytest.raises(CurError) as exc_info:
        list(read_cur(io.StringIO(csv_text)))
    assert exc_info.value.code == "invalid_number"
    assert "row 3" in exc_info.value.message


def test_read_cur_accepts_scientific_notation() -> None:
    csv_text = _csv_with_cur1(["Usage,2026-10-01T00:00:00Z,111111111111,AmazonEC2,us-east-1,1E-7"])
    items = list(read_cur(io.StringIO(csv_text)))
    assert items[0].unblended == Decimal("1E-7")


def test_read_cur_invalid_date() -> None:
    csv_text = _csv_with_cur1(["Usage,not-a-date,111111111111,AmazonEC2,us-east-1,10.00"])
    with pytest.raises(CurError) as exc_info:
        list(read_cur(io.StringIO(csv_text)))
    assert exc_info.value.code == "invalid_date"


def test_read_cur_too_many_rows() -> None:
    csv_text = _csv_with_cur1(
        [
            "Usage,2026-10-01T00:00:00Z,111111111111,AmazonEC2,us-east-1,10.00",
            "Usage,2026-10-01T00:00:00Z,111111111111,AmazonEC2,us-east-1,20.00",
        ]
    )
    with pytest.raises(CurError) as exc_info:
        list(read_cur(io.StringIO(csv_text), max_rows=1))
    assert exc_info.value.code == "too_many_rows"


def test_read_cur_cur2_headers() -> None:
    csv_text = (
        "line_item_line_item_type,line_item_usage_start_date,line_item_usage_account_id,"
        "line_item_product_code,product_region_code,line_item_unblended_cost\n"
        "Usage,2026-10-01T00:00:00Z,111111111111,AmazonEC2,us-east-1,10.00\n"
    )
    items = list(read_cur(io.StringIO(csv_text)))
    assert len(items) == 1
    assert items[0].service == "AmazonEC2"


def test_read_cur_empty_file() -> None:
    with pytest.raises(CurError) as exc_info:
        list(read_cur(io.StringIO("")))
    assert exc_info.value.code == "missing_column"


def test_read_cur_optional_numeric_invalid() -> None:
    csv_text = _csv_with_cur1(
        ["SavingsPlanCoveredUsage,2026-10-01T00:00:00Z,111111111111,AmazonEC2,us-east-1,5.00,abc"],
        extra_header="savingsPlan/SavingsPlanEffectiveCost",
    )
    with pytest.raises(CurError) as exc_info:
        list(read_cur(io.StringIO(csv_text)))
    assert exc_info.value.code == "invalid_number"
