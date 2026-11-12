"""Shared fixtures for HERA tests."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

NATHAN_DATASET = Path(
    os.environ.get(
        "HERA_DATASET",
        "/home/zack/sharpelab/measure4me/measure4me/dataset",
    )
)

ANNOTATED_SCANS = [
    "RPL19/18", "RPL19/21", "RPL19/134", "RPL19/953", "RPL19/1261",
    "RPL10/24", "RPL10/26", "RPL10/138", "RPL10/220", "RPL10/279",
]


@pytest.fixture(scope="session")
def nathan_dataset_root() -> Path:
    if not NATHAN_DATASET.exists():
        pytest.skip(f"Nathan's dataset not present at {NATHAN_DATASET}")
    return NATHAN_DATASET
