"""Amortized cost calculation."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from decimal import Decimal

from .columns import get_column_value
from .model import LineItem


def _to_decimal(value: str) -> Decimal:
    return Decimal("0") if value == "" else Decimal(value)


def _savings_plan_covered(item: LineItem) -> Decimal:
    return _to_decimal(get_column_value(item, "savings_plan_effective_cost"))


def _savings_plan_recurring(item: LineItem) -> Decimal:
    total = _to_decimal(get_column_value(item, "savings_plan_total_commitment_to_date"))
    used = _to_decimal(get_column_value(item, "savings_plan_used_commitment"))
    return total - used


def _zero(item: LineItem) -> Decimal:
    return Decimal("0")


def _discounted(item: LineItem) -> Decimal:
    return _to_decimal(get_column_value(item, "reservation_effective_cost"))


def _ri_fee(item: LineItem) -> Decimal:
    upfront = _to_decimal(get_column_value(item, "reservation_unused_amortized_upfront_fee"))
    recurring = _to_decimal(get_column_value(item, "reservation_unused_recurring_fee"))
    return upfront + recurring


def _fee(item: LineItem) -> Decimal:
    arn = get_column_value(item, "reservation_arn")
    if arn.strip():
        return Decimal("0")
    return item.unblended


AMORTIZATION_RULES: Mapping[str, Callable[[LineItem], Decimal]] = {
    "SavingsPlanCoveredUsage": _savings_plan_covered,
    "SavingsPlanRecurringFee": _savings_plan_recurring,
    "SavingsPlanNegation": _zero,
    "SavingsPlanUpfrontFee": _zero,
    "DiscountedUsage": _discounted,
    "RIFee": _ri_fee,
    "Fee": _fee,
}


def amortized_cost(item: LineItem) -> Decimal:
    """Return the amortized cost for a single line item.

    Follows the documented amortization formula from the AWS Data Exports
    User Guide. The mapping is stored in :data:`AMORTIZATION_RULES`, which
    can be overridden by reassigning that dictionary.

    Args:
        item: A parsed :class:`LineItem`.

    Returns:
        Amortized cost as a :class:`Decimal`, exact.
    """
    rule = AMORTIZATION_RULES.get(item.line_item_type)
    if rule is None:
        return item.unblended
    return rule(item)
