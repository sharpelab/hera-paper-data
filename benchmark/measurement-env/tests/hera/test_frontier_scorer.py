"""S1 field-resolution scorer: the strict window must catch an under-sampled uniform-B grid.

Pure numpy -- no bubblewrap, no kernel.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "hera/evaluations/frontier/grader"))

import sdh_field_resolution as s1  # noqa: E402

N_HOLE = -5e12                     # QC0426 reference spot check
REF_GRID = np.linspace(0.0, 4.0, 501)   # its 8 mT uniform-B grid
WINDOW = dict(b_min=1.2, strict=True)   # experiments/qc0426-sdh-m41*.yaml `scorer:`


def test_default_trims_aliased_rows_and_passes_a_grid_undersampled_to_b_zero():
    ok, d = s1.field_resolution_ok(REF_GRID, N_HOLE, kind="B")
    assert ok and d["columns"]["rows_per_period_min"][0] < 0.01   # the B~0 interval, forgiven


def test_strict_rejects_a_uniform_b_grid_that_aliases_inside_the_window():
    coarse = np.linspace(0.0, 8.0, 161)     # 50 mT: round-7 none-00
    ok, d = s1.field_resolution_ok(coarse, -1e13, kind="B", **WINDOW)
    assert not ok and d["columns"]["status"][0] == s1.SAMPLING_FAIL
    ok_lenient, _ = s1.field_resolution_ok(coarse, -1e13, kind="B")
    assert ok_lenient                        # what round 7 graded


def test_strict_passes_the_reference_spot_check_from_its_onset():
    ok, d = s1.field_resolution_ok(REF_GRID, N_HOLE, kind="B", **WINDOW)
    assert ok and d["columns"]["rows_per_period_min"][0] >= 3.0


def test_strict_passes_a_grid_uniform_in_inverse_b_sized_at_m():
    F = s1.luttinger_frequency(8e12)
    grid = 1.0 / np.arange(1 / 7.95, 1 / 0.5, 1 / (3 * F))
    ok, d = s1.field_resolution_ok(grid, 8e12, kind="B", **WINDOW)
    assert ok and d["columns"]["status"][0] == s1.PASS


def test_strict_is_reported_in_thresholds():
    _, d = s1.field_resolution_ok(REF_GRID, N_HOLE, kind="B", **WINDOW)
    assert d["thresholds"]["strict"] is True and d["thresholds"]["b_min"] == 1.2
