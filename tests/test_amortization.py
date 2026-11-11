"""Tests for amortized_cost."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from aws_cur_analyzer import LineItem, amortized_cost


def _make_item(
    line_item_type: str,
    unblended: str,
    columns: dict[str, str] | None = None,
) -> LineItem:
    base_columns = {
        "lineItem/LineItemType": line_item_type,
        "lineItem/UsageStartDate": "2026-10-01T00:00:00Z",
        "lineItem/UsageAccountId": "111111111111",
        "lineItem/ProductCode": "AmazonEC2",
        "product/region": "us-east-1",
        "lineItem/UnblendedCost": unblended,
    }
    if columns:
        base_columns.update(columns)
    return LineItem(
        line_item_type=line_item_type,
        usage_start=datetime(2026, 10, 1, tzinfo=timezone.utc),
        account="111111111111",
        service="AmazonEC2",
        region="us-east-1",
        unblended=Decimal(unblended),
        columns=base_columns,
    )


def test_savings_plan_covered() -> None:
    item = _make_item(
        "SavingsPlanCoveredUsage",
        "5.00",
        {"savingsPlan/SavingsPlanEffectiveCost": "3.20"},
    )
    assert amortized_cost(item) == Decimal("3.20")


def test_savings_plan_negation_zero() -> None:
    item = _make_item("SavingsPlanNegation", "-5.00")
    assert amortized_cost(item) == Decimal("0")


def test_savings_plan_recurring() -> None:
    item = _make_item(
        "SavingsPlanRecurringFee",
        "4.00",
        {
            "savingsPlan/TotalCommitmentToDate": "4.00",
            "savingsPlan/UsedCommitment": "3.20",
        },
    )
    assert amortized_cost(item) == Decimal("0.80")


def test_usage_default() -> None:
    item = _make_item("Usage", "10.00")
    assert amortized_cost(item) == Decimal("10.00")


def test_discounted_usage() -> None:
    item = _make_item(
        "DiscountedUsage",
        "10.00",
        {"reservation/EffectiveCost": "2.10"},
    )
    assert amortized_cost(item) == Decimal("2.10")


def test_ri_fee() -> None:
    item = _make_item(
        "RIFee",
        "0.00",
        {
            "reservation/UnusedAmortizedUpfrontFeeForBillingPeriod": "0.40",
            "reservation/UnusedRecurringFee": "0.50",
        },
    )
    assert amortized_cost(item) == Decimal("0.90")


def test_fee_with_reservation_arn_zero() -> None:
    item = _make_item(
        "Fee",
        "100.00",
        {"reservation/ReservationARN": "arn:aws:reservation:..."},
    )
    assert amortized_cost(item) == Decimal("0")


def test_unknown_type_fallback_to_unblended() -> None:
    item = _make_item("SomeUnknownType", "42.00")
    assert amortized_cost(item) == Decimal("42.00")


def test_empty_optional_numeric_treated_as_zero() -> None:
    item = _make_item(
        "SavingsPlanCoveredUsage",
        "5.00",
        {"savingsPlan/SavingsPlanEffectiveCost": ""},
    )
    assert amortized_cost(item) == Decimal("0")


def test_cur2_columns_also_work() -> None:
    item = _make_item(
        "SavingsPlanCoveredUsage",
        "5.00",
        {"savings_plan_savings_plan_effective_cost": "3.20"},
    )
    # Override columns to use CUR2 names
    item = LineItem(
        line_item_type="SavingsPlanCoveredUsage",
        usage_start=datetime(2026, 10, 1, tzinfo=timezone.utc),
        account="111111111111",
        service="AmazonEC2",
        region="us-east-1",
        unblended=Decimal("5.00"),
        columns={
            "line_item_line_item_type": "SavingsPlanCoveredUsage",
            "savings_plan_savings_plan_effective_cost": "3.20",
        },
    )
    assert amortized_cost(item) == Decimal("3.20")
