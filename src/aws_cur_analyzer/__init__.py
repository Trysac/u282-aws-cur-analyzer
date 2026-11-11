"""Analyze AWS Cost and Usage Report CSV exports.

This package reads CUR 1.0 and CUR 2.0 CSV files and applies the documented
amortized cost formula using exact Decimal arithmetic.
"""

from __future__ import annotations

import logging

from .amortization import amortized_cost
from .cur import read_cur
from .errors import CurError, ErrorCode
from .model import Coverage, LineItem
from .summarize import render, summarize, tag_coverage

__all__ = [
    "Coverage",
    "CurError",
    "ErrorCode",
    "LineItem",
    "amortized_cost",
    "read_cur",
    "render",
    "summarize",
    "tag_coverage",
]

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

__version__ = "0.1.0"
