# Use explicit column mapping and Decimal arithmetic for CUR analysis

Status: accepted (generated, pending human review)

## Context

AWS CUR CSV files exist in two versions with different header naming conventions. Amortized cost calculation involves multiple line item types and exact money values.

## Decision

Implement an explicit mapping between logical column names and CUR 1.0 / CUR 2.0 headers; use Python's Decimal for all monetary calculations; provide overridable amortization rules via a module-level dictionary.

## Consequences

Column handling is clear and maintainable. Decimal arithmetic avoids floating-point errors. Overriding rules enables customization. The library has no external dependencies.
