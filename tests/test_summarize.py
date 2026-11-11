"""Tests for summarize, tag_coverage, and render."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

import pytest

from aws_cur_analyzer import CurError, LineItem, render, summarize, tag_coverage


# Savings Plan fixture per spec
def _make_savings_plan_fixture() -> list[LineItem]:
    common = {
        "usage_start": datetime(2026, 10, 1, tzinfo=timezone.utc),
        "account": "111111111111",
        "region": "us-east-1",
    }
    rows = [
        ("Usage", "10.00", "AmazonEC2", "10.00", {}, {"resourceTags/user:Team": "web"}),
        (
            "SavingsPlanCoveredUsage",
            "5.00",
            "AmazonEC2",
            "5.00",
            {"savingsPlan/SavingsPlanEffectiveCost": "3.20"},
            {},
        ),
        ("SavingsPlanNegation", "-5.00", "AmazonEC2", "-5.00", {}, {}),
        (
            "SavingsPlanRecurringFee",
            "4.00",
            "ComputeSavingsPlans",
            "4.00",
            {
                "savingsPlan/TotalCommitmentToDate": "4.00",
                "savingsPlan/UsedCommitment": "3.20",
            },
            {},
        ),
        ("Tax", "1.50", "AmazonEC2", "1.50", {}, {}),
        ("Credit", "-2.00", "AmazonS3", "-2.00", {}, {}),
    ]
    items = []
    for line_type, unblended, service, _unblended2, extra_cols, tag_cols in rows:
        columns = {
            "lineItem/LineItemType": line_type,
            "lineItem/UsageStartDate": "2026-10-01T00:00:00Z",
            "lineItem/UsageAccountId": common["account"],
            "lineItem/ProductCode": service,
            "product/region": common["region"],
            "lineItem/UnblendedCost": unblended,
        }
        columns.update(extra_cols)
        columns.update(tag_cols)
        items.append(
            LineItem(
                line_item_type=line_type,
                usage_start=common["usage_start"],
                account=common["account"],
                service=service,
                region=common["region"],
                unblended=Decimal(unblended),
                columns=columns,
            )
        )
    return items


def test_summarize_amortized_savings_plan_fixture() -> None:
    items = _make_savings_plan_fixture()
    result = summarize(items, by=["service"], basis="amortized")
    expected = [
        ("AmazonEC2", Decimal("14.70")),
        ("ComputeSavingsPlans", Decimal("0.80")),
        ("AmazonS3", Decimal("-2.00")),
    ]
    assert result == expected


def test_summarize_unblended_savings_plan_fixture() -> None:
    items = _make_savings_plan_fixture()
    result = summarize(items, by=["service"], basis="unblended")
    assert result == [
        ("AmazonEC2", Decimal("11.50")),
        ("ComputeSavingsPlans", Decimal("4.00")),
        ("AmazonS3", Decimal("-2.00")),
    ]
    assert sum(row[-1] for row in result) == Decimal("13.50")

    amortized = summarize(items, by=["service"], basis="amortized")
    assert sum(row[-1] for row in amortized) == Decimal("13.50")


def test_summarize_cur2_headers_equal_results() -> None:
    # Build a CUR2 fixture with equivalent data
    items = []
    common = {
        "usage_start": datetime(2026, 10, 1, tzinfo=timezone.utc),
        "account": "111111111111",
        "region": "us-east-1",
    }
    rows = [
        ("Usage", "10.00", "AmazonEC2", "10.00", {}, {}),
        (
            "SavingsPlanCoveredUsage",
            "5.00",
            "AmazonEC2",
            "5.00",
            {"savings_plan_savings_plan_effective_cost": "3.20"},
            {},
        ),
        ("SavingsPlanNegation", "-5.00", "AmazonEC2", "-5.00", {}, {}),
        (
            "SavingsPlanRecurringFee",
            "4.00",
            "ComputeSavingsPlans",
            "4.00",
            {
                "savings_plan_total_commitment_to_date": "4.00",
                "savings_plan_used_commitment": "3.20",
            },
            {},
        ),
        ("Tax", "1.50", "AmazonEC2", "1.50", {}, {}),
        ("Credit", "-2.00", "AmazonS3", "-2.00", {}, {}),
    ]
    for line_type, unblended, service, _unblended2, extra_cols, _tag_cols in rows:
        columns = {
            "line_item_line_item_type": line_type,
            "line_item_usage_start_date": "2026-10-01T00:00:00Z",
            "line_item_usage_account_id": common["account"],
            "line_item_product_code": service,
            "product_region_code": common["region"],
            "line_item_unblended_cost": unblended,
        }
        columns.update(extra_cols)
        items.append(
            LineItem(
                line_item_type=line_type,
                usage_start=common["usage_start"],
                account=common["account"],
                service=service,
                region=common["region"],
                unblended=Decimal(unblended),
                columns=columns,
            )
        )
    result = summarize(items, by=["service"], basis="amortized")
    assert result == [
        ("AmazonEC2", Decimal("14.70")),
        ("ComputeSavingsPlans", Decimal("0.80")),
        ("AmazonS3", Decimal("-2.00")),
    ]


def test_tag_coverage() -> None:
    items = _make_savings_plan_fixture()
    cov = tag_coverage(items, "Team", basis="amortized")
    assert cov.tagged == Decimal("10.00")
    assert cov.total == Decimal("13.20")  # 10 + 3.20 + 0 (Discounted none)
    assert cov.percent == Decimal("75.76")


def test_tag_coverage_zero_total() -> None:
    # No relevant types -> total 0
    items = [
        LineItem(
            line_item_type="Tax",
            usage_start=datetime(2026, 10, 1, tzinfo=timezone.utc),
            account="1",
            service="s",
            region="r",
            unblended=Decimal("5"),
            columns={},
        )
    ]
    cov = tag_coverage(items, "Team")
    assert cov.total == Decimal("0")
    assert cov.percent == Decimal("0")


def test_summarize_by_month_and_day() -> None:
    items = [
        LineItem(
            line_item_type="Usage",
            usage_start=datetime(2026, 10, 1, tzinfo=timezone.utc),
            account="1",
            service="s",
            region="r",
            unblended=Decimal("10"),
            columns={},
        ),
        LineItem(
            line_item_type="Usage",
            usage_start=datetime(2026, 10, 31, 23, 0, tzinfo=timezone.utc),
            account="1",
            service="s",
            region="r",
            unblended=Decimal("20"),
            columns={},
        ),
        LineItem(
            line_item_type="Usage",
            usage_start=datetime(2026, 11, 1, tzinfo=timezone.utc),
            account="1",
            service="s",
            region="r",
            unblended=Decimal("30"),
            columns={},
        ),
    ]
    result = summarize(items, by=["month"])
    assert result == [("2026-10", Decimal("30")), ("2026-11", Decimal("30"))]
    result_day = summarize(items, by=["day"])
    assert result_day == [
        ("2026-11-01", Decimal("30")),
        ("2026-10-31", Decimal("20")),
        ("2026-10-01", Decimal("10")),
    ]


def test_summarize_month_boundary_from_cur_date_strings() -> None:
    def _parse_z(value: str) -> datetime:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))

    items = [
        LineItem(
            line_item_type="Usage",
            usage_start=_parse_z("2026-10-31T23:00:00Z"),
            account="1",
            service="s",
            region="r",
            unblended=Decimal("20"),
            columns={},
        ),
        LineItem(
            line_item_type="Usage",
            usage_start=_parse_z("2026-11-01T00:00:00Z"),
            account="1",
            service="s",
            region="r",
            unblended=Decimal("30"),
            columns={},
        ),
    ]
    result = summarize(items, by=["month"])
    assert result == [("2026-11", Decimal("30")), ("2026-10", Decimal("20"))]


def test_summarize_by_tag() -> None:
    items = _make_savings_plan_fixture()
    # Only Usage line has tag Team=web; others untagged
    result = summarize(items, by=["tag:Team"])
    assert len(result) == 2
    # tagged=10 (web) sorts first; untagged = 13.50 - 10 = 3.50
    assert result[0][0] == "web"
    assert result[0][1] == Decimal("10.00")
    assert result[1][0] == "(untagged)"
    assert result[1][1] == Decimal("3.50")


def test_summarize_invalid_basis() -> None:
    items = _make_savings_plan_fixture()
    with pytest.raises(CurError):
        summarize(items, by=["service"], basis="invalid")  # type: ignore[arg-type]


def test_summarize_invalid_group_field() -> None:
    items = _make_savings_plan_fixture()
    with pytest.raises(CurError) as exc_info:
        summarize(items, by=["nonexistent"])
    assert exc_info.value.code == "invalid_group"


def test_summarize_too_many_groups() -> None:
    items = _make_savings_plan_fixture()
    with pytest.raises(CurError) as exc_info:
        summarize(items, by=["line_item_type"], max_groups=2)
    assert exc_info.value.code == "too_many_groups"


def test_render_text() -> None:
    rows = [("AmazonEC2", Decimal("14.70")), ("ComputeSavingsPlans", Decimal("0.80"))]
    text = render(rows, "text")
    assert text == "AmazonEC2\t14.70\nComputeSavingsPlans\t0.80\n"


def test_render_json() -> None:
    rows = [("AmazonEC2", Decimal("14.70"))]
    json_str = render(rows, "json")
    assert json_str == '[["AmazonEC2", "14.70"]]'


def test_render_invalid_format() -> None:
    rows = [("a", Decimal("1"))]
    with pytest.raises(CurError):
        render(rows, "xml")  # type: ignore[arg-type]
