# Testing

## Running

```sh
python -m pytest
```

The provided tree contains `tests/__pycache__/test_amortization.cpython-312-pytest-9.2.0.pyc`; the corresponding source test file is `tests/test_amortization.py`.

## Policy

The only test module present in the provided tree is `tests/test_amortization.py`. It builds `LineItem` instances with CUR 1.0 columns and asserts `amortized_cost` results. No coverage threshold, conformance marker, or `scripts/check.py` gate is present in the listed code.

## Tests present

- `tests/test_amortization.py::test_savings_plan_covered` covers `SavingsPlanCoveredUsage` and asserts `amortized_cost(item) == Decimal('3.20')` from `savingsPlan/SavingsPlanEffectiveCost`.
- `tests/test_amortization.py::test_savings_plan_negation_zero` covers `SavingsPlanNegation` and asserts `amortized_cost(item) == Decimal('0')`.

## Tiers

There is no CI tier defined in the provided tree. The listed tests run in the local pytest process and need no network.

## Layout

`tests/test_amortization.py` is the only test file in the provided tree; it mirrors the `aws_cur_analyzer.amortization` module. No `tests/conftest.py` is present in the provided tree.
