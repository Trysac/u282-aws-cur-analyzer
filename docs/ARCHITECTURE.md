# Architecture

## Overview

The `aws_cur_analyzer` package reads AWS Cost and Usage Report (CUR) CSV files
and provides amortized cost calculation and aggregation. It supports both CUR
1.0 and CUR 2.0 column names through an explicit mapping, never relying on
case-conversion rules.

## Components

- **`columns.py`**: Central mapping between logical column names and their
  CUR 1.0 / CUR 2.0 header strings.
- **`cur.py`**: CSV reader that validates required columns, parses dates and
  numbers, and yields `LineItem` objects. It temporarily adjusts
  `csv.field_size_limit` to handle large fields.
- **`model.py`**: Frozen dataclasses `LineItem` and `Coverage`.
- **`amortization.py`**: Implements the amortized cost formula using a
  data-driven rule table (`AMORTIZATION_RULES`), which can be overridden by
  users.
- **`summarize.py`**: Aggregation (`summarize`), tag coverage
  (`tag_coverage`), and rendering (`render`) in text or JSON.
- **`errors.py`**: Single `CurError` exception with machine-readable `code`.
- **`__main__.py`**: Command-line interface.

## Design Decisions

- **Exact arithmetic**: All monetary values are `Decimal`; no floating point.
- **Column mapping**: Explicit tables for CUR 1.0 and CUR 2.0 avoid brittle
  string transformations.
- **Validation limits**: `max_rows` (default 10 million), `max_field_chars`
  (default 131072), and `max_groups` (default 100000) prevent resource
  exhaustion.
- **Overridable rules**: `AMORTIZATION_RULES` is a module-level dictionary that
  can be reassigned for custom amortization logic.
- **No runtime dependencies**: Uses only Python standard library.

## Threat Model

Input is untrusted CSV data. The library enforces size limits and validates
all numeric and date fields. It never executes code from input. See
`docs/SECURITY.md` for details.
