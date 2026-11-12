import json
import math
from pathlib import Path

import pytest

from hera.variance_compare import ComparisonError, compare_outputs


def make_summary(model="provider/model", hash_suffix="same"):
    trials = []
    probabilities = [0.8, 0.6, 0.4]
    for index, probability in enumerate(probabilities, start=1):
        campaign = f"campaign-{index}"
        common = {
            "samples_total": 5,
            "samples_ok": 5,
            "samples_unparseable": 0,
            "samples_failed": 0,
            "sample_records": [
                {
                    "model_resolved": model,
                    "workspace_hash": f"{campaign}-{hash_suffix}",
                    "total_cost_usd": 1.0,
                }
            ],
        }
        tool = {
            **common,
            "metrics": {
                "callable": {"entropy_nats": 0.5},
                "joint_call_signature": {"entropy_nats": math.log(5)},
            },
        }
        final = {
            **common,
            "metrics": {
                "verdict": {
                    "counts": {"ABA": index, "ABC": 5 - index},
                    "entropy_nats": 0.6,
                    "entropy_normalized": 0.55,
                },
                "ground_truth": {
                    "p_truth_jeffreys": probability,
                    "nll_jeffreys_alpha_0_5": -math.log(probability),
                },
            },
        }
        trials.append(
            {
                "trial": index,
                "campaign_id": campaign,
                "experiments": {"tool-call": tool, "final-analysis": final},
            }
        )
    return {"trials": trials}


def write_summary(root: Path, summary):
    root.mkdir()
    (root / "summary.json").write_text(json.dumps(summary))


def test_compare_outputs_writes_artifacts(tmp_path):
    first, second = tmp_path / "first", tmp_path / "second"
    write_summary(first, make_summary("alpha/model"))
    write_summary(second, make_summary("beta/model"))
    output = tmp_path / "comparison"
    result = compare_outputs([("Alpha", first), ("Beta", second)], output)
    expected = (0.8 * 0.6 * 0.4) ** (1 / 3)
    assert result["models"][0]["longitudinal"]["geometric_mean_p_truth"] == pytest.approx(expected)
    assert result["models"][0]["samples_total"] == 30
    assert result["models"][0]["reported_cost_usd"] == 6.0
    for name in (
        "model-comparison.json", "model-comparison.csv", "model-comparison.md",
        "model-comparison.png", "model-comparison.svg",
    ):
        assert (output / name).is_file()


def test_requires_two_outputs(tmp_path):
    with pytest.raises(ComparisonError, match="at least two"):
        compare_outputs([], tmp_path / "out")


def test_hash_mismatch_fails(tmp_path):
    first, second = tmp_path / "first", tmp_path / "second"
    write_summary(first, make_summary("alpha/model"))
    write_summary(second, make_summary("beta/model", hash_suffix="different"))
    with pytest.raises(ComparisonError, match="workspace hashes differ"):
        compare_outputs([("Alpha", first), ("Beta", second)], tmp_path / "out")


def test_failed_samples_fail_closed(tmp_path):
    first, second = tmp_path / "first", tmp_path / "second"
    bad = make_summary("alpha/model")
    bad["trials"][0]["experiments"]["tool-call"]["samples_failed"] = 1
    write_summary(first, bad)
    write_summary(second, make_summary("beta/model"))
    with pytest.raises(ComparisonError, match="failed sample"):
        compare_outputs([("Alpha", first), ("Beta", second)], tmp_path / "out")


def test_mixed_models_in_one_root_fail(tmp_path):
    first, second = tmp_path / "first", tmp_path / "second"
    mixed = make_summary("alpha/model")
    mixed["trials"][0]["experiments"]["tool-call"]["sample_records"].append(
        {
            "model_resolved": "other/model",
            "workspace_hash": "campaign-1-same",
            "total_cost_usd": 0,
        }
    )
    write_summary(first, mixed)
    write_summary(second, make_summary("beta/model"))
    with pytest.raises(ComparisonError, match="exactly one resolved model"):
        compare_outputs([("Alpha", first), ("Beta", second)], tmp_path / "out")
