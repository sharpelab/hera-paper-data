import json
import math
from pathlib import Path

import pytest

from hera.tool_variance import (
    ToolVarianceError,
    pairwise_metrics,
    parameter_distance,
    summarize_root,
)


def call(name="s.megasweep", start=0.0, stop=8.0, points=81, delay=1.2):
    return {
        "callable": name,
        "axes": [{"name": "magnet.field", "start": start, "stop": stop, "points": points}],
        "delays": {"slow": delay},
        "kwargs": {"bias": 2.0},
    }


def record(sample, parsed, *, status="ok"):
    return {
        "sample": sample,
        "status": status,
        "parsed": parsed,
        "model_resolved": "claude-haiku-4-5-20251001",
        "workspace_hash": "abc",
        "total_cost_usd": 0.1,
    }


def test_parameter_distance_identity_and_bounds():
    assert parameter_distance(call(), call()) == 0.0
    value = parameter_distance(call(), call(start=4, stop=12, points=41, delay=2.4))
    assert 0 < value < 1
    assert parameter_distance(call(), call(start=100, stop=101)) <= 1


def test_pairwise_callable_mismatch_is_maximal():
    records = [
        record(1, call("s.megasweep")),
        record(2, call("s.sweep")),
        record(3, call("s.megasweep")),
    ]
    metrics = pairwise_metrics(records)
    assert metrics["pairs"] == 3
    assert metrics["callable_mismatch_pairs"] == 2
    assert metrics["callable_mismatch_rate"] == pytest.approx(2 / 3)
    assert metrics["parameter_disagreement_same_callable"] == 0
    assert metrics["tool_decision_disagreement"] == pytest.approx(2 / 3)


def write_summary(root: Path, *, failed=0):
    records = [
        record(1, call("s.megasweep")),
        record(2, call("megasweep")),
        record(3, call("s.sweep")),
    ]
    if failed:
        records[-1]["status"] = "error"
        records[-1]["parsed"] = None
    summary = {
        "experiment_id": "x",
        "trials": [
            {
                "trial": 1,
                "campaign_id": "20260610-qc0426",
                "experiments": {
                    "tool-call": {
                        "samples_total": 3,
                        "samples_failed": failed,
                        "samples_unparseable": 0,
                        "sample_records": records,
                    }
                },
            }
        ],
    }
    root.mkdir()
    (root / "summary.json").write_text(json.dumps(summary))


def test_summarize_root_writes_all_artifacts(tmp_path: Path):
    root, output = tmp_path / "root", tmp_path / "out"
    write_summary(root)
    result = summarize_root(root, output)
    item = result["campaigns"][0]
    expected_h = -(2 / 3 * math.log(2 / 3) + 1 / 3 * math.log(1 / 3))
    assert item["callable_entropy_nats"] == pytest.approx(expected_h)
    assert item["callable_counts"] == {"s.megasweep": 2, "s.sweep": 1}
    assert result["reported_cost_usd"] == pytest.approx(0.3)
    for name in (
        "tool-variance-longitudinal.json",
        "tool-variance-longitudinal.csv",
        "tool-variance-longitudinal.md",
        "tool-variance-longitudinal.png",
        "tool-variance-longitudinal.svg",
    ):
        assert (output / name).is_file()


def test_summarize_root_rejects_incomplete_samples(tmp_path: Path):
    root = tmp_path / "root"
    write_summary(root, failed=1)
    with pytest.raises(ToolVarianceError, match="incomplete"):
        summarize_root(root, tmp_path / "out")
