"""Tests for command-line interface."""

from __future__ import annotations

import gzip
import io
import json
from contextlib import redirect_stdout
from pathlib import Path

from aws_cur_analyzer.__main__ import main

CSV_CONTENT = (
    "lineItem/LineItemType,lineItem/UsageStartDate,lineItem/UsageAccountId,"
    "lineItem/ProductCode,product/region,lineItem/UnblendedCost,"
    "savingsPlan/SavingsPlanEffectiveCost,savingsPlan/TotalCommitmentToDate,"
    "savingsPlan/UsedCommitment\n"
    "Usage,2026-10-01T00:00:00Z,111111111111,AmazonEC2,us-east-1,10.00,,,\n"
    "SavingsPlanCoveredUsage,2026-10-01T00:00:00Z,111111111111,AmazonEC2,"
    "us-east-1,5.00,3.20,,\n"
    "SavingsPlanNegation,2026-10-01T00:00:00Z,111111111111,AmazonEC2,"
    "us-east-1,-5.00,,,\n"
    "SavingsPlanRecurringFee,2026-10-01T00:00:00Z,111111111111,ComputeSavingsPlans,"
    "us-east-1,4.00,,4.00,3.20\n"
    "Tax,2026-10-01T00:00:00Z,111111111111,AmazonEC2,us-east-1,1.50,,,\n"
    "Credit,2026-10-01T00:00:00Z,111111111111,AmazonS3,us-east-1,-2.00,,,\n"
)


def _write_csv(tmp_path: Path, content: str = CSV_CONTENT) -> Path:
    p = tmp_path / "cur.csv"
    p.write_text(content, encoding="utf-8")
    return p


def test_main_summary_text(tmp_path: Path) -> None:
    csv_path = _write_csv(tmp_path)
    argv = [str(csv_path), "--by", "service", "--basis", "amortized"]
    f = io.StringIO()
    with redirect_stdout(f):
        result = main(argv)
    assert result == 0
    lines = f.getvalue().splitlines()
    assert lines[0] == "AmazonEC2\t14.70"


def test_main_summary_json(tmp_path: Path) -> None:
    csv_path = _write_csv(tmp_path)
    argv = [str(csv_path), "--by", "service", "--format", "json"]
    f = io.StringIO()
    with redirect_stdout(f):
        result = main(argv)
    assert result == 0
    data = json.loads(f.getvalue())
    assert data[0][0] == "AmazonEC2"
    assert data[0][1] == "14.70"


def test_main_tag_coverage(tmp_path: Path) -> None:
    content = (
        "lineItem/LineItemType,lineItem/UsageStartDate,lineItem/UsageAccountId,"
        "lineItem/ProductCode,product/region,lineItem/UnblendedCost,"
        "resourceTags/user:Team,savingsPlan/SavingsPlanEffectiveCost,"
        "savingsPlan/TotalCommitmentToDate,savingsPlan/UsedCommitment\n"
        "Usage,2026-10-01T00:00:00Z,111111111111,AmazonEC2,us-east-1,10.00,web,,,\n"
        "SavingsPlanCoveredUsage,2026-10-01T00:00:00Z,111111111111,AmazonEC2,"
        "us-east-1,5.00,,3.20,,\n"
        "SavingsPlanNegation,2026-10-01T00:00:00Z,111111111111,AmazonEC2,"
        "us-east-1,-5.00,,,,\n"
        "SavingsPlanRecurringFee,2026-10-01T00:00:00Z,111111111111,ComputeSavingsPlans,"
        "us-east-1,4.00,,,4.00,3.20\n"
        "Tax,2026-10-01T00:00:00Z,111111111111,AmazonEC2,us-east-1,1.50,,,,\n"
        "Credit,2026-10-01T00:00:00Z,111111111111,AmazonS3,us-east-1,-2.00,,,,\n"
    )
    csv_path = _write_csv(tmp_path, content)
    argv = [str(csv_path), "--tag-coverage", "Team"]
    f = io.StringIO()
    with redirect_stdout(f):
        result = main(argv)
    assert result == 0
    parts = f.getvalue().strip().split("\t")
    assert parts == ["10.00", "13.20", "75.76"]


def test_main_missing_file(tmp_path: Path) -> None:
    argv = [str(tmp_path / "nonexistent.csv"), "--by", "service"]
    result = main(argv)
    assert result == 2


def test_main_gzip(tmp_path: Path) -> None:
    csv_path = tmp_path / "cur.csv.gz"
    with gzip.open(csv_path, "wt", encoding="utf-8") as f:
        f.write(CSV_CONTENT)
    argv = [str(csv_path), "--by", "service"]
    result = main(argv)
    assert result == 0


def test_main_missing_by(tmp_path: Path) -> None:
    csv_path = _write_csv(tmp_path)
    argv = [str(csv_path)]
    result = main(argv)
    assert result == 2  # usage error: --by is required when not using --tag-coverage
