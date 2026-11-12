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


@pytest.fixture(autouse=True)
def _replay_local_state(tmp_path_factory, monkeypatch):
    """Replay jobs keep machine-local state (pools, job records, slot locks); tests get their own."""
    root = tmp_path_factory.mktemp("replay-local")
    for var in ("XDG_CONFIG_HOME", "XDG_STATE_HOME", "XDG_RUNTIME_DIR"):
        (root / var).mkdir()
        monkeypatch.setenv(var, str(root / var))
