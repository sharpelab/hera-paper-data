"""Analysis for the raw/analysis/procedural-context matched ablation."""
from __future__ import annotations

import csv
import hashlib
import json
import math
import random
import secrets
from collections import Counter
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt

from hera.context_ablation import score_final_record, score_tool_record

VARIANTS = [
    ("raw-only", "Raw only"),
    ("campaign-analysis", "+ campaign analysis"),
    ("analysis-plus-context", "+ analysis + context"),
]


def _mean(rows: list[dict[str, Any]], key: str) -> float | None:
    values = [float(row[key]) for row in rows if row.get(key) is not None]
    return sum(values) / len(values) if values else None


def _entropy(values: list[str]) -> float:
    counts, n = Counter(values), len(values)
    return -sum((v / n) * math.log(v / n) for v in counts.values()) if n else 0.0


def _load_rows(root: Path) -> list[dict[str, Any]]:
    rows = []
    for variant, label in VARIANTS:
        for experiment in ("tool-call", "final-analysis"):
            paths = sorted((root / "samples" / variant / experiment).glob("sample-*/sample.json"))
            for sample_json in paths:
                record = json.loads(sample_json.read_text())
                output_path = sample_json.parent / "output.md"
                output_text = output_path.read_text(errors="replace") if output_path.is_file() else ""
                score = score_tool_record(record, output_text) if experiment == "tool-call" else score_final_record(record, output_text)
                rows.append({
                    "variant": variant,
                    "variant_label": label,
                    "experiment": experiment,
                    "sample": record.get("sample"),
                    "status": record.get("status"),
                    "model": record.get("model_resolved"),
                    "workspace_hash": record.get("workspace_hash"),
                    "cost_usd": record.get("total_cost_usd"),
                    "output_path": str(output_path),
                    **score,
                })
    if len(rows) != 18 or any(row["status"] != "ok" for row in rows):
        raise RuntimeError(f"matched ablation incomplete: expected 18 ok rows, got {len(rows)}")
    return rows


def _blind_packet(rows: list[dict[str, Any]], output: Path) -> dict[str, Any]:
    packet = output / "blinded-human-utility-packet"
    packet.mkdir(exist_ok=True)
    key_path = output / "PRIVATE-blind-key.json"
    salt = secrets.token_hex(16)
    shuffled = list(rows)
    random.Random(int(hashlib.sha256(salt.encode()).hexdigest(), 16)).shuffle(shuffled)
    key = []
    index_lines = [
        "# Blinded recommendation-utility scoring packet", "",
        "Score without opening `PRIVATE-blind-key.json`.", "",
        "For tool calls score 0–4 each: scientific information gain, feasibility, cost/time discipline, and evidence linkage.",
        "For final analyses score 0–4 each: evidence use, correctness/calibration, ambiguity handling, and actionable follow-up.",
        "Record scores and notes beneath each item. Treatment labels are intentionally absent.", "",
    ]
    for number, row in enumerate(shuffled, 1):
        blind_id = f"U{number:02d}"
        source = Path(row["output_path"])
        body = source.read_text(errors="replace")
        item = packet / f"{blind_id}.md"
        item.write_text(
            f"# {blind_id}\n\nExperiment type: `{row['experiment']}`\n\n"
            "## Model output\n\n" + body +
            "\n\n## Independent scores\n\n- Axis 1 (0–4):\n- Axis 2 (0–4):\n- Axis 3 (0–4):\n- Axis 4 (0–4):\n- Notes:\n"
        )
        index_lines.append(f"- [{blind_id}]({blind_id}.md) — `{row['experiment']}`")
        key.append({"blind_id": blind_id, "variant": row["variant"], "experiment": row["experiment"], "sample": row["sample"], "source": str(source)})
    (packet / "README.md").write_text("\n".join(index_lines) + "\n")
    key_doc = {"warning": "keep private from independent scorer until scoring is locked", "salt": salt, "mapping": key}
    key_path.write_text(json.dumps(key_doc, indent=2) + "\n")
    return {"packet": str(packet), "private_key": str(key_path), "items": len(key)}


def analyze(root: Path, output: Path) -> dict[str, Any]:
    root, output = Path(root), Path(output)
    output.mkdir(parents=True, exist_ok=True)
    rows = _load_rows(root)
    summaries = []
    for variant, label in VARIANTS:
        tool = [r for r in rows if r["variant"] == variant and r["experiment"] == "tool-call"]
        final = [r for r in rows if r["variant"] == variant and r["experiment"] == "final-analysis"]
        verdicts = [str(r.get("verdict")) for r in final]
        summaries.append({
            "variant": variant,
            "label": label,
            "n_tool": len(tool), "n_final": len(final),
            "fan_scope_rate": _mean(tool, "fan_scope"),
            "clipping_guard_rate": _mean(tool, "clipping_guard"),
            "settling_guard_rate": _mean(tool, "settling_guard"),
            "inverse_b_rate": _mean(tool, "inverse_b"),
            "tool_guard_score": _mean(tool, "primary_guard_score"),
            "verdict_counts": dict(Counter(verdicts)),
            "aba_correct_rate": sum(v == "ABA" for v in verdicts) / len(verdicts),
            "verdict_entropy_nats": _entropy(verdicts),
            "analysis_quality_score": _mean(final, "primary_analysis_score"),
            "pair_recognition_rate": _mean(final, "aba_pair_recognized"),
            "ambiguity_rate": _mean(final, "f_l_tone_ambiguity"),
            "calibration_rate": _mean(final, "calibrated_conclusion"),
            "followup_rate": _mean(final, "deciding_followup"),
        })
    blind = _blind_packet(rows, output)
    result = {
        "experiment": "qc0426-matched-content-ablation-haiku-n3-v1",
        "ground_truth": "ABA",
        "root": str(root),
        "reported_cost_usd": sum(float(r.get("cost_usd") or 0) for r in rows),
        "summaries": summaries,
        "rows": rows,
        "blinded_human_scoring": blind,
    }
    (output / "matched-content-ablation-results.json").write_text(json.dumps(result, indent=2) + "\n")
    fields = sorted({key for row in rows for key in row})
    with (output / "matched-content-ablation-samples.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields); writer.writeheader(); writer.writerows(rows)

    labels = [x["label"] for x in summaries]; x = range(len(labels)); width = .25
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.2))
    axes[0].bar([i-width for i in x], [s["fan_scope_rate"] for s in summaries], width, label="2D fan scope")
    axes[0].bar(x, [s["tool_guard_score"] for s in summaries], width, label="guard score")
    axes[0].bar([i+width for i in x], [s["inverse_b_rate"] for s in summaries], width, label="inverse-B")
    axes[0].set_title("Next-measurement behavior"); axes[0].set_ylim(0, 1.05); axes[0].legend(fontsize=8)
    axes[1].bar([i-width/2 for i in x], [s["aba_correct_rate"] for s in summaries], width, label="ABA correctness")
    axes[1].bar([i+width/2 for i in x], [s["analysis_quality_score"] for s in summaries], width, label="analysis quality")
    axes[1].set_title("Final-analysis behavior"); axes[1].set_ylim(0, 1.05); axes[1].legend(fontsize=8)
    for ax in axes:
        ax.set_xticks(list(x), labels, rotation=12, ha="right"); ax.set_ylabel("Fraction / mean score"); ax.grid(axis="y", alpha=.25)
    fig.suptitle("Matched QC0426 Chiron content ablation — fixed raw frontiers, Haiku N=3", fontsize=14)
    fig.tight_layout(); fig.savefig(output / "matched-content-ablation.png", dpi=220, bbox_inches="tight"); fig.savefig(output / "matched-content-ablation.svg", bbox_inches="tight"); plt.close(fig)

    md = [
        "# Matched Chiron content ablation", "",
        "Fixed QC0426 raw-data frontiers; N=3 fresh Haiku sessions per treatment/experiment.", "",
        "| Treatment | Fan scope | Clip guard | Settle guard | 1/B | Tool guard | ABA correct | Final quality | Verdicts |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for s in summaries:
        md.append(f"| {s['label']} | {s['fan_scope_rate']:.3f} | {s['clipping_guard_rate']:.3f} | {s['settling_guard_rate']:.3f} | {s['inverse_b_rate']:.3f} | {s['tool_guard_score']:.3f} | {s['aba_correct_rate']:.3f} | {s['analysis_quality_score']:.3f} | `{s['verdict_counts']}` |")
    md += ["", f"Reported API-equivalent cost: ${result['reported_cost_usd']:.2f}", "", "Human utility scores are pending independent blinded review; no scores were fabricated."]
    (output / "matched-content-ablation-report.md").write_text("\n".join(md) + "\n")
    return result
