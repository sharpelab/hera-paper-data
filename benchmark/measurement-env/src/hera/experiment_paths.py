"""Shared filesystem roots for replay-variance analyses.

Experiment outputs live outside the repository. Analyses resolve the tree
through one function so a different machine or archive location only needs
$HERA_RESULTS set.
"""
from __future__ import annotations

import os
from pathlib import Path


def results_root() -> Path:
    """Root of the replay-variance results tree ($HERA_RESULTS overrides)."""
    override = os.environ.get("HERA_RESULTS")
    if override:
        return Path(override).expanduser()
    return Path.home() / "docs/hera-replay-variance-results"
