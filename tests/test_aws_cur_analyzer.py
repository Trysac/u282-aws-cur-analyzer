"""Behavior tests for the public API of aws_cur_analyzer."""

from __future__ import annotations

import aws_cur_analyzer


def test_version_is_semver() -> None:
    parts = aws_cur_analyzer.__version__.split(".")
    assert len(parts) == 3
    assert all(part.isdigit() for part in parts)
