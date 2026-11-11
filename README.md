# trysac-aws-cur-analyzer

Analyze AWS Cost and Usage Report (CUR) CSV exports: amortized and unblended cost by service, account, region, tag or line item type, with exact Decimal sums.

## Installation

```bash
pip install trysac-aws-cur-analyzer
```

## Usage

### Python API

```python
import io
from aws_cur_analyzer import read_cur, amortized_cost, summarize

csv_text = "lineItem/LineItemType,lineItem/UsageStartDate,lineItem/UsageAccountId,lineItem/ProductCode,product/region,lineItem/UnblendedCost,savingsPlan/SavingsPlanEffectiveCost\nSavingsPlanCoveredUsage,2026-10-01T00:00:00Z,111111111111,AmazonEC2,us-east-1,5.00,3.20\n"
items = list(read_cur(io.StringIO(csv_text)))
print(amortized_cost(items[0]))  # 3.20
print(summarize(items, by=["service"]))  # [('AmazonEC2', Decimal('3.20'))]
```

### Command Line

```bash
aws-cur-analyzer cur.csv --by service,month --basis amortized
aws-cur-analyzer cur.csv --tag-coverage Team --format json
```

## Public API

- `read_cur(stream, *, max_rows=10_000_000, max_field_chars=131_072)` yields `LineItem` objects. Raises `CurError` with codes `missing_column`, `invalid_number`, `invalid_date`, or `too_many_rows`.
- `amortized_cost(item)` returns a `Decimal` using `AMORTIZATION_RULES`; the module-level table can be reassigned.
- `summarize(items, *, by, basis='amortized', max_groups=100_000)` returns tuples of group values followed by the `Decimal` total. Group fields: `service`, `account`, `region`, `line_item_type`, `day`, `month`, `tag:<key>`. Raises `invalid_group` or `too_many_groups`.
- `tag_coverage(items, key, *, basis='amortized')` returns `Coverage(tagged, total, percent)` over `Usage`, `SavingsPlanCoveredUsage`, and `DiscountedUsage` only; `percent` is quantized to `0.01` with `ROUND_HALF_UP`.
- `render(rows, fmt)` returns tab-separated text or a JSON array; invalid `fmt` raises `invalid_group`.
- `LineItem` and `Coverage` are frozen dataclasses. `CurError.code` is one of `missing_column`, `invalid_number`, `invalid_date`, `too_many_rows`, `too_many_groups`, `invalid_group`; `str(error)` is `code: message`.

## Why not a FOCUS analyzer or Cost Explorer

Cost Explorer and FOCUS-based analyzers are online or aggregated services. This library reads raw CUR 1.0 and CUR 2.0 CSV offline, keeps the documented amortization rules in an explicit overridable table, and uses exact `Decimal` sums. It does not download from S3, read Parquet, use the CUR 2.0 `resource_tags` map, calculate net/discounted cost, or convert currency.

## Documentation

See [docs/SECURITY.md](docs/SECURITY.md) for the threat model and limits.

## License

MIT
