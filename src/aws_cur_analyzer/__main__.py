"""Command-line interface for aws_cur_analyzer."""

from __future__ import annotations

import argparse
import gzip
import json
import sys
from collections.abc import Sequence

from .cur import read_cur
from .errors import CurError
from .summarize import render, summarize, tag_coverage


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point for the CLI.

    Args:
        argv: Command-line arguments (excluding program name). If ``None``,
            ``sys.argv[1:]`` is used.

    Returns:
        Exit code: 0 for success, 1 for data errors (``CurError``), 2 for
        usage or I/O errors.
    """
    parser = argparse.ArgumentParser(
        prog="aws-cur-analyzer",
        description="Analyze AWS Cost and Usage Report CSV exports.",
    )
    parser.add_argument("path", help="Path to a CUR CSV file (optionally .gz)")
    parser.add_argument(
        "--by",
        help="Comma-separated list of group fields, e.g. service,month",
    )
    parser.add_argument(
        "--basis",
        choices=["amortized", "unblended"],
        default="amortized",
        help="Cost basis (default: amortized)",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--tag-coverage",
        metavar="KEY",
        help="Show tag coverage for the given tag key instead of summary",
    )
    parser.exit_on_error = False
    try:
        args = parser.parse_args(argv)
    except argparse.ArgumentError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2

    if not args.tag_coverage and not args.by:
        print("Error: --by is required when not using --tag-coverage", file=sys.stderr)
        return 2

    try:
        with (
            gzip.open(args.path, "rt", encoding="utf-8")
            if args.path.endswith(".gz")
            else open(args.path, encoding="utf-8")
        ) as stream:
            items = read_cur(stream)
            if args.tag_coverage:
                cov = tag_coverage(items, args.tag_coverage, basis=args.basis)
                if args.format == "json":
                    out = json.dumps(
                        {
                            "tagged": str(cov.tagged),
                            "total": str(cov.total),
                            "percent": str(cov.percent),
                        }
                    )
                else:
                    out = f"{cov.tagged}\t{cov.total}\t{cov.percent}"
                print(out)
            else:
                by = [s.strip() for s in args.by.split(",") if s.strip()]
                rows = summarize(items, by=by, basis=args.basis)
                out = render(rows, args.format)
                print(out, end="")
        return 0
    except CurError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except (OSError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    except Exception as e:  # pragma: no cover - unexpected errors
        print(f"Error: {e}", file=sys.stderr)
        return 2
