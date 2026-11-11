"""Column name mappings for CUR 1.0 and CUR 2.0."""

from __future__ import annotations

from .model import LineItem

CUR1_COLUMNS: dict[str, str] = {
    "lineItem/LineItemType": "lineItem/LineItemType",
    "lineItem/UsageStartDate": "lineItem/UsageStartDate",
    "lineItem/UsageAccountId": "lineItem/UsageAccountId",
    "lineItem/ProductCode": "lineItem/ProductCode",
    "product/region": "product/region",
    "lineItem/UnblendedCost": "lineItem/UnblendedCost",
    "savingsPlan/SavingsPlanEffectiveCost": "savingsPlan/SavingsPlanEffectiveCost",
    "savingsPlan/TotalCommitmentToDate": "savingsPlan/TotalCommitmentToDate",
    "savingsPlan/UsedCommitment": "savingsPlan/UsedCommitment",
    "reservation/EffectiveCost": "reservation/EffectiveCost",
    "reservation/UnusedAmortizedUpfrontFeeForBillingPeriod": (
        "reservation/UnusedAmortizedUpfrontFeeForBillingPeriod"
    ),
    "reservation/UnusedRecurringFee": "reservation/UnusedRecurringFee",
    "reservation/ReservationARN": "reservation/ReservationARN",
}

CUR2_COLUMNS: dict[str, str] = {
    "line_item_line_item_type": "line_item_line_item_type",
    "line_item_usage_start_date": "line_item_usage_start_date",
    "line_item_usage_account_id": "line_item_usage_account_id",
    "line_item_product_code": "line_item_product_code",
    "product_region_code": "product_region_code",
    "line_item_unblended_cost": "line_item_unblended_cost",
    "savings_plan_savings_plan_effective_cost": "savings_plan_savings_plan_effective_cost",
    "savings_plan_total_commitment_to_date": "savings_plan_total_commitment_to_date",
    "savings_plan_used_commitment": "savings_plan_used_commitment",
    "reservation_effective_cost": "reservation_effective_cost",
    "reservation_unused_amortized_upfront_fee_for_billing_period": (
        "reservation_unused_amortized_upfront_fee_for_billing_period"
    ),
    "reservation_unused_recurring_fee": "reservation_unused_recurring_fee",
    "reservation_reservation_a_r_n": "reservation_reservation_a_r_n",
}

COLUMN_ALIASES: dict[str, tuple[str, str]] = {
    "line_item_type": ("lineItem/LineItemType", "line_item_line_item_type"),
    "usage_start_date": ("lineItem/UsageStartDate", "line_item_usage_start_date"),
    "usage_account_id": ("lineItem/UsageAccountId", "line_item_usage_account_id"),
    "product_code": ("lineItem/ProductCode", "line_item_product_code"),
    "region": ("product/region", "product_region_code"),
    "unblended_cost": ("lineItem/UnblendedCost", "line_item_unblended_cost"),
    "savings_plan_effective_cost": (
        "savingsPlan/SavingsPlanEffectiveCost",
        "savings_plan_savings_plan_effective_cost",
    ),
    "savings_plan_total_commitment_to_date": (
        "savingsPlan/TotalCommitmentToDate",
        "savings_plan_total_commitment_to_date",
    ),
    "savings_plan_used_commitment": (
        "savingsPlan/UsedCommitment",
        "savings_plan_used_commitment",
    ),
    "reservation_effective_cost": (
        "reservation/EffectiveCost",
        "reservation_effective_cost",
    ),
    "reservation_unused_amortized_upfront_fee": (
        "reservation/UnusedAmortizedUpfrontFeeForBillingPeriod",
        "reservation_unused_amortized_upfront_fee_for_billing_period",
    ),
    "reservation_unused_recurring_fee": (
        "reservation/UnusedRecurringFee",
        "reservation_unused_recurring_fee",
    ),
    "reservation_arn": ("reservation/ReservationARN", "reservation_reservation_a_r_n"),
}


def get_column_value(line: LineItem, logical_name: str) -> str:
    """Return the raw value for a logical column from a LineItem's columns.

    Args:
        line: A ``LineItem`` instance.
        logical_name: One of the keys in ``COLUMN_ALIASES``.

    Returns:
        The string value from either the CUR 1.0 or CUR 2.0 header, or ``''``
        if neither is present.
    """
    for alias in COLUMN_ALIASES[logical_name]:
        if alias in line.columns:
            return line.columns[alias]
    return ""
