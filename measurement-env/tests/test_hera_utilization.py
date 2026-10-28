"""Synthetic-fixture tests for hera-utilization's court split.

Covers each row of the case table in hera/docs/hera-utilization-design.md:
serialized land, queue-ahead land, multiple lands (earliest wins), and the
empty gap. Times are small epoch integers for legibility.
"""
import json
from datetime import datetime, timezone

import pytest

from tools.hera_utilization import compute


def _write_sweep(session_dir, run_id, start, end, slug="test-slug"):
    d = session_dir / "data" / str(run_id)
    d.mkdir(parents=True)
    (d / "metadata.json").write_text(
        json.dumps({"start_time": start, "end_time": end, "comments": [slug]})
    )


def _write_notebook(session_dir, land_epochs):
    cells = []
    for t in land_epochs:
        stamp = datetime.fromtimestamp(t, tz=timezone.utc).isoformat()
        cells.append(
            {
                "cell_type": "code",
                "source": [],
                "metadata": {"hera": {"appended_at": stamp, "v": "v0"}},
                "outputs": [],
                "execution_count": None,
            }
        )
    (session_dir / "sim_measure.ipynb").write_text(json.dumps({"cells": cells}))


@pytest.fixture
def session(tmp_path):
    return tmp_path


def test_serialized_gap(session):
    # sweep0 [0,100], land at 130, sweep1 [160,200]
    # gap = 60: HERA court 100->130 (30), human court 130->160 (30)
    _write_sweep(session, 0, 0, 100)
    _write_sweep(session, 1, 160, 200)
    _write_notebook(session, [130])
    r = compute(str(session))
    assert r["hera_court_s"] == pytest.approx(30)
    assert r["human_court_s"] == pytest.approx(30)
    assert r["measuring_s"] == pytest.approx(140)
    assert r["span_s"] == pytest.approx(200)
    assert r["raw_utilization"] == pytest.approx(140 / 200)
    assert r["hil_utilization"] == pytest.approx(140 / 170)


def test_queue_ahead(session):
    # land at 50, during sweep0 [0,100] -> whole gap is human court
    _write_sweep(session, 0, 0, 100)
    _write_sweep(session, 1, 160, 200)
    _write_notebook(session, [50])
    r = compute(str(session))
    assert r["hera_court_s"] == pytest.approx(0)
    assert r["human_court_s"] == pytest.approx(60)


def test_multiple_lands_earliest_wins(session):
    # lands at 110, 140, 150 -> HERA charged only 100->110
    _write_sweep(session, 0, 0, 100)
    _write_sweep(session, 1, 160, 200)
    _write_notebook(session, [110, 140, 150])
    r = compute(str(session))
    assert r["hera_court_s"] == pytest.approx(10)
    assert r["human_court_s"] == pytest.approx(50)


def test_empty_gap_charged_to_hera(session):
    _write_sweep(session, 0, 0, 100)
    _write_sweep(session, 1, 160, 200)
    _write_notebook(session, [])
    r = compute(str(session))
    assert r["hera_court_s"] == pytest.approx(60)
    assert r["human_court_s"] == pytest.approx(0)
    assert r["hil_utilization"] == pytest.approx(r["raw_utilization"])


def test_no_notebook_raw_only(session):
    _write_sweep(session, 0, 0, 100)
    _write_sweep(session, 1, 160, 200)
    r = compute(str(session))
    assert r["n_lands"] == 0
    assert r["hera_court_s"] == pytest.approx(60)


def test_land_before_gap_sweep_ignored(session):
    # land during sweep0's *predecessor* window must not leak into gap 1:
    # pending resets OFF at each sweep start.
    _write_sweep(session, 0, 0, 100)
    _write_sweep(session, 1, 160, 200)
    _write_sweep(session, 2, 260, 300)
    # land at 50 covers gap0; nothing lands for gap1
    _write_notebook(session, [50])
    r = compute(str(session))
    g0, g1 = r["gaps"]
    assert g0["human_s"] == pytest.approx(60)
    assert g1["hera_s"] == pytest.approx(60)
    assert g1["human_s"] == pytest.approx(0)


def test_overlapping_sweeps_merged(session):
    _write_sweep(session, 0, 0, 100)
    _write_sweep(session, 1, 50, 120)  # overlaps sweep 0
    _write_sweep(session, 2, 150, 200)
    _write_notebook(session, [])
    r = compute(str(session))
    assert r["measuring_s"] == pytest.approx(170)  # [0,120] + [150,200]
    assert r["span_s"] == pytest.approx(200)


def test_end_bound_excludes_late_sweeps(session):
    _write_sweep(session, 0, 0, 100)
    _write_sweep(session, 1, 160, 200)
    _write_sweep(session, 2, 500, 600)  # post-session extension
    _write_notebook(session, [130])
    r = compute(str(session), end=300)
    assert r["n_sweeps"] == 2
    assert r["span_s"] == pytest.approx(200)
    assert r["human_court_s"] == pytest.approx(30)
