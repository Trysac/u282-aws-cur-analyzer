# aws-cur-analyzer

[![PyPI version](https://img.shields.io/pypi/v/trysac-aws-cur-analyzer)](https://pypi.org/project/trysac-aws-cur-analyzer/)
[![License: MIT](https://img.shields.io/pypi/l/trysac-aws-cur-analyzer)](LICENSE)
[![CI](https://github.com/Trysac/u282-aws-cur-analyzer/actions/workflows/ci.yml/badge.svg)](https://github.com/Trysac/u282-aws-cur-analyzer/actions/workflows/ci.yml)

Analyze AWS Cost and Usage Report CSV exports: amortized and unblended cost by service, account, region, tag or line item type, with exact Decimal sums

## Problem

Describe in two or three sentences the concrete problem this utility solves, who hits it, and what
they do today without it. Replace this paragraph when the first real feature lands.

## Install

```sh
pip install trysac-aws-cur-analyzer
# or
uv add trysac-aws-cur-analyzer
```

Requires Python 3.10 or newer. No runtime dependencies.

## Usage

```python
import aws_cur_analyzer

# normalize() trims surrounding whitespace and lower-cases the text.
print(aws_cur_analyzer.normalize("  Hello World "))  # -> "hello world"

# Blank input is rejected explicitly instead of returning an empty string.
try:
    aws_cur_analyzer.normalize("   ")
except ValueError as exc:
    print(f"rejected: {exc}")
```

## Documentation

- [Architecture](docs/ARCHITECTURE.md) and [decisions](docs/decisions/)
- [Testing](docs/TESTING.md) and [security](docs/SECURITY.md)
- [Project record](docs/PROJECT.md) and [stack](docs/STACK.md)
- [Changelog](CHANGELOG.md) and [contributing guide](CONTRIBUTING.md)

## License

[MIT](LICENSE) (c) 2026 Miguel Gomez
