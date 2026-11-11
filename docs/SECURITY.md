# Security notes

## Threat model

Input is untrusted CUR CSV data. The library is a pure Python package with no runtime dependencies and no network, S3, Parquet, or code execution paths.

Defended:
- Missing required headers raise `CurError('missing_column')`; missing values for required columns also raise `missing_column`.
- Invalid numbers raise `CurError('invalid_number')`; invalid dates raise `CurError('invalid_date')`.
- `read_cur` enforces `max_rows` (default 10_000_000) with `CurError('too_many_rows')` and sets `csv.field_size_limit` to `max_field_chars` (default 131_072), restoring the previous limit in `finally`.
- `summarize` enforces `max_groups` (default 100_000) with `CurError('too_many_groups')`.
- Errors are `CurError(code, message)`; messages name the row and column. Cell content included in a message is truncated to 50 characters plus `...`.
- The CSV parser strips a UTF-8 BOM from the first header and strips whitespace around header names.
- Column lookup uses the explicit `COLUMN_ALIASES` table for CUR 1.0 and CUR 2.0; it does not evaluate input or deserialize untrusted data.

Not defended:
- Authentication, authorization, tenant isolation, or sandboxing. The caller controls the process and file paths.
- Gzip decompression bombs or total input size beyond `max_rows` and `max_field_chars`; the CLI reads `.gz` with `gzip.open`.
- Concurrent use of `csv.field_size_limit`: `read_cur` changes a process-global CSV limit temporarily and restores it, but concurrent readers can see the changed value.
- CUR 2.0 `resource_tags` map column, Parquet, S3 download, net/discounted cost, and currency conversion; these are out of scope.
- Memory use for many distinct groups in `summarize` is bounded only by `max_groups`; line items are streamed by `read_cur`.

## Publishing

The listed code does not contain release automation or a publishing token. To report a vulnerability, use the repository's security reporting channel.
