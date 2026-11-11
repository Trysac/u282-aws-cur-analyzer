"""Behavior tests for the public API of aws_cur_analyzer."""

from __future__ import annotations

import pytest

import aws_cur_analyzer


def test_normalize_trims_and_lowercases() -> None:
    assert aws_cur_analyzer.normalize("  Hello World ") == "hello world"


@pytest.mark.parametrize("value", ["", "   ", "\t\n"])
def test_normalize_rejects_blank_input(value: str) -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        aws_cur_analyzer.normalize(value)


def test_version_is_semver() -> None:
    parts = aws_cur_analyzer.__version__.split(".")
    assert len(parts) == 3
    assert all(part.isdigit() for part in parts)
