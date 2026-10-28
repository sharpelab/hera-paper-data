"""Cross-model aggregation for completed HERA variance output roots."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt

plt.switch_backend("Agg")


class ComparisonError(RuntimeError):
    """Raised when output roots cannot be compared safely."""


def _metric(trial: dict[str, Any], kind: str, *path: str) -> Any:
    node: Any = trial.get("experiments", {}).get(kind, {}).get("metrics", {})
    for key in path:
        if not isinstance(node, dict) or key not in node:
            return None
        node = node[key]
    return node


def _model_id(summary: dict[str, Any]) -> str:
    models: set[str] = set()
    for trial in summary.get("trials", []):
        for experiment in trial.get("experiments", {}).values():
            for record in experiment.get("sample_records", []):
                model = record.get("model_resolved")
                if model:
                    models.add(str(model))
    if len(models) != 1:
        raise ComparisonError(
            f"expected exactly one resolved model in output, found {sorted(models)}"
        )
    return next(iter(models))


def _frontier_hashes(summary: dict[str, Any]) -> dict[tuple[str, str], str]:
    hashes: dict[tuple[str, str], str] = {}
    for trial in summary.get("trials", []):
        campaign = trial["campaign_id"]
        for kind, experiment in trial.get("experiments", {}).items():
            observed = {
                record.get("workspace_hash")
                for record in experiment.get("sample_records", [])
                if record.get("workspace_hash")
            }
            if len(observed) != 1:
                raise ComparisonError(
                    f"{campaign}/{kind}: expected one workspace hash, "
                    f"found {sorted(observed)}"
                )
            hashes[(campaign, kind)] = next(iter(observed))
    return hashes


def _validate_complete(summary: dict[str, Any]) -> None:
    for trial in summary.get("trials", []):
        for kind, experiment in trial.get("experiments", {}).items():
            if experiment.get("samples_failed"):
                raise ComparisonError(
                    f"{trial['campaign_id']}/{kind}: "
                    f"{experiment['samples_failed']} failed sample(s)"
                )
            if not experiment.get("samples_total"):
                raise ComparisonError(
                    f"{trial['campaign_id']}/{kind}: no samples"
                )


def _summarize_model(label: str, root: Path, summary: dict[str, Any]) -> dict[str, Any]:
    trials: list[dict[str, Any]] = []
    nlls: list[float] = []
    probabilities: list[float] = []
    total_samples = 0
    reported_cost = 0.0
    for trial in summary["trials"]:
        experiments = trial.get("experiments", {})
        for experiment in experiments.values():
            total_samples += int(experiment.get("samples_total") or 0)
            reported_cost += sum(
                float(record.get("total_cost_usd") or 0)
                for record in experiment.get("sample_records", [])
            )
        probability = _metric(
            trial, "final-analysis", "ground_truth", "p_truth_jeffreys"
        )
        nll = _metric(
            trial, "final-analysis", "ground_truth", "nll_jeffreys_alpha_0_5"
        )
        if probability is not None and nll is not None:
            probabilities.append(float(probability))
            nlls.append(float(nll))
        trials.append(
            {
                "trial": trial["trial"],
                "campaign_id": trial["campaign_id"],
                "tool_samples": experiments.get("tool-call", {}).get("samples_total"),
                "final_samples": experiments.get("final-analysis", {}).get("samples_total"),
                "callable_entropy_nats": _metric(
                    trial, "tool-call", "callable", "entropy_nats"
                ),
                "joint_signature_entropy_nats": _metric(
                    trial, "tool-call", "joint_call_signature", "entropy_nats"
                ),
                "verdict_counts": _metric(
                    trial, "final-analysis", "verdict", "counts"
                ),
                "verdict_entropy_nats": _metric(
                    trial, "final-analysis", "verdict", "entropy_nats"
                ),
                "verdict_entropy_normalized": _metric(
                    trial, "final-analysis", "verdict", "entropy_normalized"
                ),
                "p_truth_jeffreys": probability,
                "nll_jeffreys": nll,
            }
        )
    if not nlls:
        raise ComparisonError(f"{label}: no final-analysis ground-truth metrics")
    mean_nll = sum(nlls) / len(nlls)
    return {
        "label": label,
        "model_resolved": _model_id(summary),
        "output_root": str(root),
        "samples_total": total_samples,
        "reported_cost_usd": reported_cost,
        "trials": trials,
        "longitudinal": {
            "campaigns_scored": len(nlls),
            "mean_nll_jeffreys": mean_nll,
            "geometric_mean_p_truth": math.exp(-mean_nll),
            "latest_p_truth_jeffreys": probabilities[-1],
            "latest_nll_jeffreys": nlls[-1],
        },
    }


def _write_csv(output: Path, comparison: dict[str, Any]) -> None:
    fields = [
        "label", "model_resolved", "trial", "campaign_id", "tool_samples",
        "final_samples", "callable_entropy_nats", "joint_signature_entropy_nats",
        "verdict_counts", "verdict_entropy_nats", "verdict_entropy_normalized",
        "p_truth_jeffreys", "nll_jeffreys", "longitudinal_geomean_p_truth",
        "longitudinal_mean_nll", "reported_cost_usd",
    ]
    with (output / "model-comparison.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        for model in comparison["models"]:
            for trial in model["trials"]:
                writer.writerow(
                    {
                        **{key: trial.get(key) for key in fields},
                        "label": model["label"],
                        "model_resolved": model["model_resolved"],
                        "verdict_counts": json.dumps(
                            trial.get("verdict_counts"), sort_keys=True
                        ),
                        "longitudinal_geomean_p_truth": model["longitudinal"][
                            "geometric_mean_p_truth"
                        ],
                        "longitudinal_mean_nll": model["longitudinal"][
                            "mean_nll_jeffreys"
                        ],
                        "reported_cost_usd": model["reported_cost_usd"],
                    }
                )


def _write_report(output: Path, comparison: dict[str, Any]) -> None:
    lines = [
        "# HERA replay-variance model comparison",
        "",
        "> Reported cost is harness telemetry. For Claude Max it is an API-equivalent, "
        "not necessarily billed spend.",
        "",
        "## Longitudinal score",
        "",
        "| Label | Resolved model | N total | Geomean p(truth) | Mean NLL | "
        "Latest p(truth) | Reported cost |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for model in comparison["models"]:
        score = model["longitudinal"]
        lines.append(
            f"| {model['label']} | `{model['model_resolved']}` | "
            f"{model['samples_total']} | {score['geometric_mean_p_truth']:.3f} | "
            f"{score['mean_nll_jeffreys']:.3f} | "
            f"{score['latest_p_truth_jeffreys']:.3f} | "
            f"${model['reported_cost_usd']:.2f} |"
        )
    lines.extend(["", "## Per campaign", ""])
    for model in comparison["models"]:
        lines.extend(
            [
                f"### {model['label']} — `{model['model_resolved']}`",
                "",
                "| Trial | Campaign | N tool/final | Callable H | Verdicts | "
                "Verdict H | p(truth) | NLL |",
                "|---:|---|---:|---:|---|---:|---:|---:|",
            ]
        )
        for trial in model["trials"]:
            counts = ", ".join(
                f"{key}×{value}"
                for key, value in sorted((trial.get("verdict_counts") or {}).items())
            )
            lines.append(
                f"| {trial['trial']} | {trial['campaign_id']} | "
                f"{trial['tool_samples']}/{trial['final_samples']} | "
                f"{float(trial['callable_entropy_nats']):.3f} | {counts} | "
                f"{float(trial['verdict_entropy_nats']):.3f} | "
                f"{float(trial['p_truth_jeffreys']):.3f} | "
                f"{float(trial['nll_jeffreys']):.3f} |"
            )
        lines.append("")
    (output / "model-comparison.md").write_text("\n".join(lines) + "\n")


def _write_plot(output: Path, comparison: dict[str, Any]) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(16, 5), constrained_layout=True)
    for model in comparison["models"]:
        x = [trial["trial"] for trial in model["trials"]]
        axes[0].plot(
            x, [trial["p_truth_jeffreys"] for trial in model["trials"]],
            "o-", label=model["label"],
        )
        axes[1].plot(
            x, [trial["nll_jeffreys"] for trial in model["trials"]],
            "o-", label=model["label"],
        )
        axes[2].plot(
            x, [trial["callable_entropy_nats"] for trial in model["trials"]],
            "o-", label=model["label"],
        )
    axes[0].set_title("Correct-answer probability")
    axes[0].set_ylabel("Jeffreys-smoothed p(ABA)")
    axes[0].set_ylim(0, 1)
    axes[1].set_title("Ground-truth loss")
    axes[1].set_ylabel("NLL (lower is better)")
    axes[2].set_title("Next-tool repeatability")
    axes[2].set_ylabel("Callable entropy (nats)")
    for axis in axes:
        axis.set_xlabel("chronological campaign trial")
        axis.set_xticks(comparison["trials"])
        axis.grid(alpha=0.2)
    axes[0].legend(fontsize=8)
    fig.suptitle("Same-device QC0426 replay comparison (N shown in report)")
    for suffix in ("png", "svg"):
        fig.savefig(output / f"model-comparison.{suffix}", dpi=150)
    plt.close(fig)


def compare_outputs(
    specifications: list[tuple[str, Path]], output: Path
) -> dict[str, Any]:
    """Validate and aggregate completed per-model summary roots."""
    if len(specifications) < 2:
        raise ComparisonError("at least two model outputs are required")
    loaded: list[tuple[str, Path, dict[str, Any]]] = []
    for label, root in specifications:
        summary_path = root / "summary.json"
        if not summary_path.is_file():
            raise ComparisonError(f"{label}: missing {summary_path}")
        summary = json.loads(summary_path.read_text())
        _validate_complete(summary)
        loaded.append((label, root, summary))

    campaign_layout = [
        (trial["trial"], trial["campaign_id"])
        for trial in loaded[0][2].get("trials", [])
    ]
    reference_hashes = _frontier_hashes(loaded[0][2])
    for label, _, summary in loaded[1:]:
        layout = [
            (trial["trial"], trial["campaign_id"])
            for trial in summary.get("trials", [])
        ]
        if layout != campaign_layout:
            raise ComparisonError(f"{label}: campaign/trial layout differs")
        if _frontier_hashes(summary) != reference_hashes:
            raise ComparisonError(f"{label}: frontier workspace hashes differ")

    comparison = {
        "score_definition": "exp(-mean Jeffreys-smoothed ground-truth NLL)",
        "cost_semantics": "reported harness telemetry; billing depends on provider",
        "trials": [trial for trial, _ in campaign_layout],
        "frontier_hashes": {
            f"{campaign}/{kind}": value
            for (campaign, kind), value in sorted(reference_hashes.items())
        },
        "models": [
            _summarize_model(label, root, summary)
            for label, root, summary in loaded
        ],
    }
    output.mkdir(parents=True, exist_ok=True)
    (output / "model-comparison.json").write_text(json.dumps(comparison, indent=2))
    _write_csv(output, comparison)
    _write_report(output, comparison)
    _write_plot(output, comparison)
    return comparison
