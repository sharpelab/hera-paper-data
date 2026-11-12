import json
from pathlib import Path

import pytest

from hera.context_ablation import score_final_record
from hera.matched_content_ablation import VARIANTS, analyze


def _write_sample(root: Path, variant: str, experiment: str, sample: int) -> None:
    directory = root / "samples" / variant / experiment / f"sample-{sample:02d}"
    directory.mkdir(parents=True)
    if experiment == "tool-call":
        parsed = {
            "callable": "s.megasweep",
            "axes": [
                {"name": "density D=0 line", "start": -2, "stop": 2, "points": 9},
                {"name": "magnet.field", "start": 1, "stop": 8, "points": 81},
            ],
            "delays": {"fast": 1.2},
            "kwargs": {"sr1_sensitivity": 5e-5},
            "rationale": "Use uniform inverse-B sampling with clipping headroom.",
        }
        output = json.dumps(parsed)
    else:
        parsed = {
            "verdict": "ABA",
            "confidence": "MEDIUM",
            "evidence": ["Two ML and BL tones partition F_L."],
            "caveats": ["A sum tone or ABC domain remains ambiguous."],
            "decisive_next_test": "Use an LK temperature mass ladder to resolve it.",
        }
        output = json.dumps(parsed)
    record = {
        "sample": sample,
        "status": "ok",
        "parsed": parsed,
        "model_resolved": "claude-haiku-4-5-20251001",
        "workspace_hash": f"{variant}-{experiment}",
        "total_cost_usd": 0.1,
    }
    (directory / "sample.json").write_text(json.dumps(record))
    (directory / "output.md").write_text(output)


def test_analyze_writes_results_and_blinded_packet(tmp_path: Path):
    root, output = tmp_path / "root", tmp_path / "analysis"
    for variant, _ in VARIANTS:
        for experiment in ("tool-call", "final-analysis"):
            for sample in range(1, 4):
                _write_sample(root, variant, experiment, sample)
    result = analyze(root, output)
    assert len(result["rows"]) == 18
    assert result["reported_cost_usd"] == pytest.approx(1.8)
    assert all(item["aba_correct_rate"] == 1 for item in result["summaries"])
    assert len(list((output / "blinded-human-utility-packet").glob("U*.md"))) == 18
    for name in (
        "matched-content-ablation-results.json",
        "matched-content-ablation-samples.csv",
        "matched-content-ablation-report.md",
        "matched-content-ablation.png",
        "matched-content-ablation.svg",
        "PRIVATE-blind-key.json",
    ):
        assert (output / name).is_file()


def test_quoted_consistent_with_is_not_decision_calibration():
    record = {
        "parsed": {
            "verdict": "ABA",
            "confidence": "HIGH",
            "summary": "The result is definitive.",
            "evidence": ["Two tones partition F_L."],
        }
    }
    score = score_final_record(
        record,
        'Device card says "Consistent-with..." [sanitized]. The answer is definitive.',
    )
    assert score["calibrated_conclusion"] is False


def test_analyze_rejects_incomplete_root(tmp_path: Path):
    with pytest.raises(RuntimeError, match="expected 18"):
        analyze(tmp_path / "empty", tmp_path / "out")
