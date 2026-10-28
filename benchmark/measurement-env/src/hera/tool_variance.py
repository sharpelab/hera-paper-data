"""Longitudinal metrics for HERA tool-call replay variance."""

from __future__ import annotations

import csv
import json
import math
import random
from collections import Counter
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt

plt.switch_backend("Agg")


class ToolVarianceError(RuntimeError):
    pass


def normalize_callable(value: Any) -> str:
    import re

    raw = str(value).strip()
    match = re.match(r"^(?:s\.)?([A-Za-z_]\w*)", raw)
    return f"s.{match.group(1)}" if match else raw


def _entropy(values: list[str]) -> float:
    if not values:
        return 0.0
    counts = Counter(values)
    n = len(values)
    return -sum((count / n) * math.log(count / n) for count in counts.values())


def _sym_relative(a: Any, b: Any) -> float:
    try:
        x, y = float(a), float(b)
    except (TypeError, ValueError):
        return 0.0 if str(a) == str(b) else 1.0
    if not math.isfinite(x) or not math.isfinite(y):
        return 0.0 if x == y else 1.0
    scale = abs(x) + abs(y)
    return abs(x - y) / scale if scale else 0.0


def _set_distance(a: set[str], b: set[str]) -> float:
    union = a | b
    return 0.0 if not union else 1.0 - len(a & b) / len(union)


def _interval_distance(a: dict[str, Any], b: dict[str, Any]) -> float:
    try:
        a0, a1 = sorted((float(a["start"]), float(a["stop"])))
        b0, b1 = sorted((float(b["start"]), float(b["stop"])))
    except (KeyError, TypeError, ValueError):
        return (_sym_relative(a.get("start"), b.get("start"))
                + _sym_relative(a.get("stop"), b.get("stop"))) / 2
    union = max(a1, b1) - min(a0, b0)
    if union == 0:
        return 0.0
    overlap = max(0.0, min(a1, b1) - max(a0, b0))
    return 1.0 - overlap / union


def _flatten(value: Any, prefix: str = "") -> dict[str, Any]:
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for key, item in value.items():
            name = f"{prefix}.{key}" if prefix else str(key)
            out.update(_flatten(item, name))
        return out
    if isinstance(value, (list, tuple)):
        out = {}
        for index, item in enumerate(value):
            name = f"{prefix}[{index}]"
            out.update(_flatten(item, name))
        return out
    return {prefix or "value": value}


def _mapping_distance(a: Any, b: Any) -> float:
    left, right = _flatten(a if isinstance(a, dict) else {}), _flatten(
        b if isinstance(b, dict) else {}
    )
    keys = set(left) | set(right)
    if not keys:
        return 0.0
    distances = []
    for key in sorted(keys):
        if key not in left or key not in right:
            distances.append(1.0)
        else:
            distances.append(_sym_relative(left[key], right[key]))
    return sum(distances) / len(distances)


def parameter_distance(left: dict[str, Any], right: dict[str, Any]) -> float:
    """Bounded schema-aware distance for two calls to the same callable."""
    axes_a = {
        str(axis.get("name")): axis
        for axis in left.get("axes", [])
        if isinstance(axis, dict) and axis.get("name") is not None
    }
    axes_b = {
        str(axis.get("name")): axis
        for axis in right.get("axes", [])
        if isinstance(axis, dict) and axis.get("name") is not None
    }
    components = [_set_distance(set(axes_a), set(axes_b))]
    for name in sorted(set(axes_a) | set(axes_b)):
        if name not in axes_a or name not in axes_b:
            components.extend((1.0, 1.0))
        else:
            components.append(_interval_distance(axes_a[name], axes_b[name]))
            components.append(
                _sym_relative(axes_a[name].get("points"), axes_b[name].get("points"))
            )

    delays_a = left.get("delays") if isinstance(left.get("delays"), dict) else {}
    delays_b = right.get("delays") if isinstance(right.get("delays"), dict) else {}
    components.append(_set_distance(set(delays_a), set(delays_b)))
    for key in sorted(set(delays_a) | set(delays_b)):
        if key not in delays_a or key not in delays_b:
            components.append(1.0)
        else:
            components.append(_sym_relative(delays_a[key], delays_b[key]))
    components.append(_mapping_distance(left.get("kwargs"), right.get("kwargs")))
    return min(1.0, max(0.0, sum(components) / len(components)))


def pairwise_metrics(records: list[dict[str, Any]]) -> dict[str, Any]:
    parsed = [record["parsed"] for record in records]
    calls = [normalize_callable(item.get("callable")) for item in parsed]
    pair_distances: list[float] = []
    parameter_distances: list[float] = []
    callable_mismatches = 0
    for i in range(len(parsed)):
        for j in range(i + 1, len(parsed)):
            if calls[i] != calls[j]:
                callable_mismatches += 1
                pair_distances.append(1.0)
            else:
                distance = parameter_distance(parsed[i], parsed[j])
                parameter_distances.append(distance)
                pair_distances.append(distance)
    pairs = len(pair_distances)
    return {
        "pairs": pairs,
        "callable_mismatch_pairs": callable_mismatches,
        "callable_mismatch_rate": callable_mismatches / pairs if pairs else None,
        "tool_decision_disagreement": (
            sum(pair_distances) / pairs if pairs else None
        ),
        "parameter_disagreement_same_callable": (
            sum(parameter_distances) / len(parameter_distances)
            if parameter_distances else None
        ),
        "same_callable_pairs": len(parameter_distances),
        "pair_distances": pair_distances,
        "same_callable_parameter_distances": parameter_distances,
    }


def _percentile(values: list[float], probability: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return float("nan")
    index = probability * (len(ordered) - 1)
    lo, hi = math.floor(index), math.ceil(index)
    if lo == hi:
        return ordered[lo]
    return ordered[lo] + (ordered[hi] - ordered[lo]) * (index - lo)


def bootstrap_intervals(
    records: list[dict[str, Any]], *, iterations: int = 2000, seed: int = 0
) -> dict[str, list[float] | None]:
    if len(records) < 2:
        return {"callable_entropy_nats_90": None, "tool_disagreement_90": None}
    rng = random.Random(seed)
    entropy_values: list[float] = []
    distance_values: list[float] = []
    for _ in range(iterations):
        sampled = [rng.choice(records) for _ in records]
        entropy_values.append(
            _entropy([normalize_callable(r["parsed"].get("callable")) for r in sampled])
        )
        value = pairwise_metrics(sampled)["tool_decision_disagreement"]
        if value is not None:
            distance_values.append(value)
    return {
        "callable_entropy_nats_90": [
            _percentile(entropy_values, 0.05), _percentile(entropy_values, 0.95)
        ],
        "tool_disagreement_90": [
            _percentile(distance_values, 0.05), _percentile(distance_values, 0.95)
        ],
    }


def summarize_root(root: Path, output: Path) -> dict[str, Any]:
    summary_path = root / "summary.json"
    if not summary_path.is_file():
        raise ToolVarianceError(f"missing {summary_path}")
    summary = json.loads(summary_path.read_text())
    campaigns = []
    total_cost = 0.0
    model_ids: set[str] = set()
    for trial in summary.get("trials", []):
        experiment = trial.get("experiments", {}).get("tool-call")
        if not experiment:
            raise ToolVarianceError(f"{trial['campaign_id']}: no tool-call experiment")
        failed = int(experiment.get("samples_failed") or 0)
        unparseable = int(experiment.get("samples_unparseable") or 0)
        records = [
            record for record in experiment.get("sample_records", [])
            if record.get("status") == "ok" and isinstance(record.get("parsed"), dict)
        ]
        if failed or unparseable or len(records) != int(experiment.get("samples_total") or 0):
            raise ToolVarianceError(
                f"{trial['campaign_id']}: incomplete samples "
                f"(ok={len(records)}, failed={failed}, unparseable={unparseable})"
            )
        calls = [normalize_callable(r["parsed"].get("callable")) for r in records]
        entropy = _entropy(calls)
        pairwise = pairwise_metrics(records)
        intervals = bootstrap_intervals(records, seed=int(trial["trial"]))
        for record in records:
            if record.get("model_resolved"):
                model_ids.add(record["model_resolved"])
            total_cost += float(record.get("total_cost_usd") or 0)
        campaigns.append({
            "trial": trial["trial"],
            "campaign_id": trial["campaign_id"],
            "n": len(records),
            "callable_counts": dict(sorted(Counter(calls).items())),
            "callable_entropy_nats": entropy,
            "callable_entropy_normalized_ln_n": (
                entropy / math.log(len(records)) if len(records) > 1 else 0.0
            ),
            "effective_callable_count": math.exp(entropy),
            **pairwise,
            "bootstrap": intervals,
            "samples": [
                {
                    "sample": record["sample"],
                    "callable": normalize_callable(record["parsed"].get("callable")),
                    "parsed": record["parsed"],
                    "workspace_hash": record.get("workspace_hash"),
                }
                for record in records
            ],
        })
    if len(model_ids) != 1:
        raise ToolVarianceError(f"expected one resolved model, found {sorted(model_ids)}")
    result = {
        "experiment_id": summary.get("experiment_id"),
        "model_resolved": next(iter(model_ids)),
        "samples_per_campaign": sorted({item["n"] for item in campaigns}),
        "campaigns": campaigns,
        "reported_cost_usd": total_cost,
        "metric_note": (
            "Tool disagreement is mean unordered-pair distance: callable mismatch=1; "
            "same-callable pairs use schema-aware bounded parameter distance."
        ),
        "causal_note": "Chronological observational trend; campaign evidence/frontiers differ.",
    }
    output.mkdir(parents=True, exist_ok=True)
    (output / "tool-variance-longitudinal.json").write_text(
        json.dumps(result, indent=2) + "\n"
    )
    _write_csv(output, campaigns)
    _write_markdown(output, result)
    _write_plot(output, result)
    return result


def _write_csv(output: Path, campaigns: list[dict[str, Any]]) -> None:
    fields = [
        "trial", "campaign_id", "n", "callable_counts", "callable_entropy_nats",
        "callable_entropy_normalized_ln_n", "effective_callable_count",
        "callable_mismatch_rate", "parameter_disagreement_same_callable",
        "tool_decision_disagreement",
    ]
    with (output / "tool-variance-longitudinal.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for campaign in campaigns:
            row = {field: campaign.get(field) for field in fields}
            row["callable_counts"] = json.dumps(row["callable_counts"], sort_keys=True)
            writer.writerow(row)


def _write_markdown(output: Path, result: dict[str, Any]) -> None:
    lines = [
        "# Longitudinal Haiku tool-call variance", "",
        f"Model: `{result['model_resolved']}`", "",
        "| Trial | Campaign | N | Callable counts | H (nats) | exp(H) | Callable mismatch | Parameter disagreement | Tool disagreement |",
        "|---:|---|---:|---|---:|---:|---:|---:|---:|",
    ]
    for item in result["campaigns"]:
        counts = ", ".join(f"`{key}`×{value}" for key, value in item["callable_counts"].items())
        parameter = item["parameter_disagreement_same_callable"]
        lines.append(
            f"| {item['trial']} | {item['campaign_id']} | {item['n']} | {counts} | "
            f"{item['callable_entropy_nats']:.3f} | {item['effective_callable_count']:.2f} | "
            f"{item['callable_mismatch_rate']:.3f} | "
            f"{parameter:.3f} | {item['tool_decision_disagreement']:.3f} |"
            if parameter is not None else
            f"| {item['trial']} | {item['campaign_id']} | {item['n']} | {counts} | "
            f"{item['callable_entropy_nats']:.3f} | {item['effective_callable_count']:.2f} | "
            f"{item['callable_mismatch_rate']:.3f} | — | {item['tool_decision_disagreement']:.3f} |"
        )
    lines.extend([
        "", f"Reported API-equivalent cost: ${result['reported_cost_usd']:.2f}", "",
        result["metric_note"], "", result["causal_note"], "",
        "N=3 is an exploratory cheap iteration; bootstrap intervals are correspondingly discrete and wide.",
    ])
    (output / "tool-variance-longitudinal.md").write_text("\n".join(lines) + "\n")


def _short_label(campaign_id: str, trial: int) -> str:
    stamp = campaign_id.split("-")[0].replace("d2", ".2").replace("d3", ".3")
    if len(stamp) >= 8 and stamp[:8].isdigit():
        stamp = f"{stamp[4:6]}/{stamp[6:8]}{stamp[8:]}"
    return f"{trial}\n{stamp}"


def _write_plot(output: Path, result: dict[str, Any]) -> None:
    campaigns = result["campaigns"]
    x = [item["trial"] for item in campaigns]
    labels = [_short_label(item["campaign_id"], item["trial"]) for item in campaigns]
    entropy = [item["callable_entropy_nats"] for item in campaigns]
    disagreement = [item["tool_decision_disagreement"] for item in campaigns]
    parameter = [item["parameter_disagreement_same_callable"] for item in campaigns]

    fig, axes = plt.subplots(2, 1, figsize=(13.5, 8.5), sharex=True, constrained_layout=True)
    ax = axes[0]
    low = [value - item["bootstrap"]["callable_entropy_nats_90"][0]
           for value, item in zip(entropy, campaigns)]
    high = [item["bootstrap"]["callable_entropy_nats_90"][1] - value
            for value, item in zip(entropy, campaigns)]
    ax.errorbar(x, entropy, yerr=[low, high], color="#315F9B", marker="o", linewidth=2,
                capsize=4, label="callable entropy")
    ax.set_ylabel("Callable entropy H (nats)")
    ax.set_ylim(bottom=-0.04)
    ax.grid(alpha=.25)
    ax.legend(loc="upper left")

    ax = axes[1]
    ax.plot(x, disagreement, "o-", color="#C95C3D", linewidth=2,
            label="total tool-decision disagreement")
    valid = [(xi, value) for xi, value in zip(x, parameter) if value is not None]
    if valid:
        ax.plot([v[0] for v in valid], [v[1] for v in valid], "s--", color="#218A70",
                linewidth=1.8, label="parameter disagreement | same callable")
    ax.set_ylabel("Bounded pairwise disagreement (0–1)")
    ax.set_xlabel("Chronological campaign trial and date")
    ax.set_ylim(-0.04, 1.04)
    ax.set_xticks(x, labels, fontsize=8)
    ax.grid(alpha=.25)
    ax.legend(loc="upper left")

    fig.suptitle(
        f"Haiku tool-call variance across QC0426 campaign history (N={campaigns[0]['n']})\n"
        "Exploratory observational trend — no monotonic decrease assumed",
        fontsize=14,
    )
    for extension in ("png", "svg"):
        fig.savefig(output / f"tool-variance-longitudinal.{extension}", dpi=180)
    plt.close(fig)
