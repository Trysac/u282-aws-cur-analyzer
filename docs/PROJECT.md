# Project record

## Objective

Analyze AWS Cost and Usage Report (CUR) CSV exports: amortized and unblended cost by service, account, region, tag or line item type, with exact Decimal sums. The library reads CUR 1.0 and CUR 2.0 column names and applies the documented amortized-cost formula.

## Scope

In scope:
- `read_cur` streaming CSV reader for CUR 1.0 and CUR 2.0 headers, with `max_rows` and `max_field_chars`.
- `LineItem` and `Coverage` frozen dataclasses.
- `amortized_cost` with the `AMORTIZATION_RULES` table for Savings Plans, Reservations, Fee, and fallback to unblended cost.
- `summarize` by `service`, `account`, `region`, `line_item_type`, `day`, `month`, and `tag:<key>`.
- `tag_coverage` for Usage, SavingsPlanCoveredUsage, DiscountedUsage.
- `render` as tab-separated text or JSON.
- CLI in `aws_cur_analyzer.__main__` with `--by`, `--basis`, `--format`, `--tag-coverage`, and `.gz` input.

Out of scope:
- CUR 2.0 `resource_tags` map column.
- Parquet input.
- Downloading reports from S3.
- Net (discounted) cost columns.
- Currency conversion.

## Timeline

| Date | Event |
|---|---|
| 2026-11-09 | Column mappings and amortization formula checked against the named AWS documentation URLs in the specification. |

## Effort metrics

Measured values only; a value that has not been measured stays pending measurement.

| Metric | Value |
|---|---|
| Tokens (input / output) | 1488096 / 132122 |
| Hours (human) | pending measurement |
| Cost (USD) | 0.3182 |

## Factory run u282 (measured from API usage)

| Date (UTC) | Phase | Model | Batch | Input | Output | Cache write | Cache read | Cost (USD) |
|---|---|---|---|---|---|---|---|---|
| 2026-11-11 | generation | deepseek-v4-pro | yes | 2317 | 29529 | 0 | 3328 | 0.0601 |
| 2026-11-11 | fix-1 | deepseek-v4-pro | no | 23528 | 42164 | 0 | 534272 | 0.1108 |
| 2026-11-11 | fix-2 | deepseek-v4-pro | no | 26562 | 28123 | 0 | 173440 | 0.0770 |
| 2026-11-11 | fix-3 | deepseek-v4-pro | no | 14246 | 1740 | 0 | 75392 | 0.0145 |
| 2026-11-11 | audit | deepseek-flash | no | 23345 | 17035 | 0 | 234112 | 0.0144 |
| 2026-11-11 | fix-4 | deepseek-v4-pro | no | 16345 | 3810 | 0 | 288640 | 0.0247 |
| 2026-11-11 | docs | deepseek-flash | no | 72313 | 9721 | 0 | 256 | 0.0167 |

Total: $0.3182. Prices: deepseek line, as measured by its adapter. Providers serve the current version of each model id, so the date tells which version answered; versions, launch stages and price sources per line are in the factory's model register (docs/MODELS.md).
