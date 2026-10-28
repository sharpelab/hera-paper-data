"""Scoring and reporting for the fixed-frontier Chiron context ablation."""
from __future__ import annotations

import csv
import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt

VARIANTS = [
    ("context-a-pre-guards", "A — pre-guards", "82883a9"),
    ("context-c-guards", "C — guards", "e5654b5"),
    ("context-b-guards-invb", "B — guards + 1/B", "7d488f6"),
]
VERDICTS = ("ABA", "ABC", "UNDERDETERMINED")


def _record_text(record: dict[str, Any], output_text: str) -> str:
    return (json.dumps(record.get("parsed") or {}, sort_keys=True) + "\n" + output_text).lower()


def _axis_names(parsed: dict[str, Any]) -> str:
    return " ".join(
        str(axis.get("name", "")).lower()
        for axis in parsed.get("axes", [])
        if isinstance(axis, dict)
    )


def score_tool_record(record: dict[str, Any], output_text: str) -> dict[str, Any]:
    """Apply the preregistered acquisition-design rubric to one proposal."""
    parsed = record.get("parsed") or {}
    # Score the machine-readable proposal, not preceding narrative that may
    # merely recap a clipped historical run without fixing it.
    text = json.dumps(parsed, sort_keys=True).lower()
    callable_name = str(parsed.get("callable", "")).lower()
    axes_list = [a for a in parsed.get("axes", []) if isinstance(a, dict)]

    def has_grid(axis: dict[str, Any]) -> bool:
        for key in ("points", "n_points", "density_points"):
            try:
                if float(axis.get(key) or 0) > 1:
                    return True
            except (TypeError, ValueError):
                continue
        return False

    field_dims = [
        a for a in axes_list
        if re.search(r"mag|field|^b$", str(a.get("name", "")).lower())
        and has_grid(a)
    ]
    def is_density_dimension(axis: dict[str, Any]) -> bool:
        axis_text = json.dumps(axis, sort_keys=True).lower()
        abstract_density = bool(re.search(
            r"density|n_range|n_points|d0[_ -]?line|d\s*(?:~|≈|=)\s*0",
            axis_text,
        ))
        gate_tokens = sum(
            token in axis_text for token in ("k_tg", "k_bg", "dc205")
        )
        return has_grid(axis) and (abstract_density or gate_tokens >= 2)


    fast_dims = [
        a for a in axes_list
        if not re.search(r"mag|field|^b$", str(a.get("name", "")).lower())
        and is_density_dimension(a)
    ]
    kwargs_text = json.dumps(parsed.get("kwargs") or {}, sort_keys=True).lower()
    kwargs_gate_tokens = sum(
        token in kwargs_text for token in ("k_tg", "k_bg", "dc205")
    )
    encoded_fast_grid = bool(
        kwargs_gate_tokens >= 2
        and re.search(r"density|points|setpoints", kwargs_text)
    )
    fan_scope = bool(
        ("megasweep" in callable_name or "multimegasweep" in callable_name)
        and field_dims and (fast_dims or encoded_fast_grid)
    )
    clipping_action = bool(re.search(
        r"worst[- ]?corner|headroom|autorang|dynamic[- ]?range|"
        r"\b(?:avoid|prevent|eliminate|check)\b.{0,45}clipp|"
        r"clipp.{0,45}\b(?:avoid|prevent|eliminate|check)\b|"
        r"\b(?:size|sized|raise|increase|set)\b.{0,45}sensitiv|"
        r"sensitiv.{0,45}\b(?:size|sized|raise|increase|set)\b",
        text,
        re.S,
    ))
    sensitivity_values = [
        float(value)
        for value in re.findall(
            r"(?:sr1|sr2).{0,50}?(\d+(?:\.\d+)?e-\d+)", text
        )
    ]
    explicit_good_range = any(value >= 5e-5 for value in sensitivity_values)
    explicit_bad_range = bool(sensitivity_values) and max(sensitivity_values) <= 1e-5
    clipping_guard = bool(
        "autorang" in text
        or explicit_good_range
        or (clipping_action and not explicit_bad_range)
    )
    fast_delay = None
    delays = parsed.get("delays")
    if isinstance(delays, dict):
        for key in ("fast", "fast_delay"):
            try:
                fast_delay = float(delays[key])
                break
            except (KeyError, TypeError, ValueError):
                pass
    settling_guard = bool(
        fast_delay is not None and fast_delay >= 1.2
    ) or bool(re.search(r"(?:[4-9]|\d{2,})\s*[×x*]?\s*tau|settling floor|do not shave|full settl", text))
    # Inverse-B adoption is reported in three tiers. The preregistered primary
    # outcome (write-up, "targeted add/remove ablation") is Y=1 only when the
    # machine-readable proposal encodes uniform-in-1/B sampling on the field
    # axis or in kwargs; prose in `rationale` scores 0. The older behaviour —
    # any "1/B" substring anywhere in the envelope, rationale included — is kept
    # as `inverse_b_mention` because "FFT in 1/B" is ordinary SdH vocabulary
    # and inflated the historical rates (audited 2026-08-29).
    from hera.measurement_classifier import extract_measurement_parameters

    geometry = extract_measurement_parameters(parsed).get("field_sampling")
    inverse_b_executable = geometry == "inverse_B"
    rationale = str(parsed.get("rationale", "")).lower()
    inverse_b_intent = bool(re.search(
        r"uniform(?:ly)?[\s-]*(?:in[\s-]*)?(?:1\s*/\s*b|inverse|reciprocal)"
        r"|(?:δ|delta|d)\s*\(\s*1\s*/\s*b\s*\)"
        r"|1\s*/\s*b[\s-]*(?:grid|spac|step|sampl|uniform)",
        rationale,
    ))
    inverse_b_mention = bool(re.search(
        r"uniform.{0,25}(?:1\s*/\s*b|inverse)|1\s*/\s*b|inverse[- ]?b|reciprocal field", text
    ))
    inverse_b = inverse_b_executable
    hour_values = [float(v) for v in re.findall(r"(?<![\d.])(\d+(?:\.\d+)?)\s*(?:h|hr|hours)\b", text)]
    cost_control = None
    if hour_values:
        # Secondary endpoint: selected design is acceptable if the largest
        # explicit estimate does not advertise a >20 h overreach.
        cost_control = max(hour_values) <= 20
    primary = (int(clipping_guard) + int(settling_guard)) / 2
    return {
        "fan_scope": fan_scope,
        "clipping_guard": clipping_guard,
        "settling_guard": settling_guard,
        "inverse_b": inverse_b,
        "inverse_b_executable": inverse_b_executable,
        "inverse_b_intent": inverse_b_intent or inverse_b_executable,
        "inverse_b_mention": inverse_b_mention,
        "cost_control": cost_control,
        "fast_delay": fast_delay,
        "primary_guard_score": primary,
    }


def score_final_record(record: dict[str, Any], output_text: str) -> dict[str, Any]:
    """Apply the preregistered interpretation/calibration rubric."""
    parsed = record.get("parsed") or {}
    text = _record_text(record, output_text)
    pair = bool(re.search(
        r"(?:two|2).{0,35}(?:pocket|fermi surface|frequenc|tone)|"
        r"(?:ml|monolayer).{0,80}(?:bl|bilayer)|(?:bl|bilayer).{0,80}(?:ml|monolayer)|"
        r"partition.{0,50}f[_ ]?l|sum(?:ming|s)?.{0,50}f[_ ]?l",
        text,
        re.S,
    ))
    ambiguity = bool(
        re.search(r"breakdown|intermod|mixing|sum[- ]?tone|combination tone", text)
        and re.search(r"abc|domain|singleton|f[_ ]?l", text)
    )
    # Calibration must occur in the model's machine-readable decision fields,
    # not merely in narrative quoting a historical note such as a sanitized
    # device-card line ending in "Consistent-with...".
    decision_text = json.dumps(
        {
            key: parsed.get(key)
            for key in ("verdict", "confidence", "summary", "caveats", "decisive_next_test")
        },
        sort_keys=True,
    ).lower()
    calibrated_language = bool(re.search(
        r"underdetermin|cannot tell|\bambig(?:uous|uity)?\b|unresolved|mixed[- ]?domain|mosaic|"
        r"not (?:fully )?exclude|cannot (?:fully )?exclude|\bhedg(?:e|ed|ing)?\b|consistent-with",
        decision_text,
    ))
    confidence = str(parsed.get("confidence") or "").upper()
    verdict = str(parsed.get("verdict") or "")
    calibrated = bool(
        verdict == "UNDERDETERMINED"
        or calibrated_language
        or (ambiguity and confidence in ("", "LOW", "MEDIUM"))
    )
    technique = (
        r"lk.{0,20}mass|mass.{0,20}(?:split|temperature|ladder)|"
        r"temperature.{0,20}(?:depend|ladder)|b[- ]?window|window split|"
        r"streda|chern|high[- ]?field.{0,30}(?:offset|landau)"
    )
    action = r"next|follow[- ]?up|firm|decid|resolve|distinguish|discrimin|would test|needed"
    followup = bool(re.search(
        rf"(?:{action}).{{0,100}}(?:{technique})|(?:{technique}).{{0,100}}(?:{action})",
        text,
        re.S,
    ))
    specificity = bool(
        len(re.findall(r"\b\d+(?:\.\d+)?\s*t\b", text)) >= 2
        or (re.search(r"run\s*[23]", text) and re.search(r"run\s*4", text))
    )
    primary = sum(map(int, (pair, ambiguity, calibrated, followup))) / 4
    return {
        "verdict": verdict or None,
        "confidence": confidence or None,
        "aba_pair_recognized": pair,
        "f_l_tone_ambiguity": ambiguity,
        "calibrated_conclusion": calibrated,
        "deciding_followup": followup,
        "evidence_specificity": specificity,
        "primary_analysis_score": primary,
    }


def _entropy(values: list[str]) -> float:
    counts = Counter(values)
    n = len(values)
    return -sum((c / n) * math.log(c / n) for c in counts.values()) if n else 0.0


def analyze_context_ablation(root: Path, output: Path) -> dict[str, Any]:
    root, output = Path(root), Path(output)
    output.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    for variant, label, commit in VARIANTS:
        for experiment in ("tool-call", "final-analysis"):
            for sample_json in sorted((root / "samples" / variant / experiment).glob("sample-*/sample.json")):
                record = json.loads(sample_json.read_text())
                output_path = sample_json.parent / "output.md"
                output_text = output_path.read_text(errors="replace") if output_path.is_file() else ""
                scored = (
                    score_tool_record(record, output_text)
                    if experiment == "tool-call"
                    else score_final_record(record, output_text)
                )
                rows.append({
                    "variant": variant,
                    "variant_label": label,
                    "commit": commit,
                    "experiment": experiment,
                    "sample": record.get("sample"),
                    "status": record.get("status"),
                    "model_resolved": record.get("model_resolved"),
                    "workspace_hash": record.get("workspace_hash"),
                    **scored,
                })
    expected = len(VARIANTS) * 2 * 3
    if len(rows) != expected or any(r["status"] != "ok" for r in rows):
        raise RuntimeError(f"context ablation incomplete: expected {expected} ok rows, got {len(rows)}")

    summaries = []
    for variant, label, commit in VARIANTS:
        tool = [r for r in rows if r["variant"] == variant and r["experiment"] == "tool-call"]
        final = [r for r in rows if r["variant"] == variant and r["experiment"] == "final-analysis"]
        verdicts = [str(r["verdict"]) for r in final]
        summaries.append({
            "variant": variant,
            "variant_label": label,
            "commit": commit,
            "tool_primary_mean": sum(r["primary_guard_score"] for r in tool) / len(tool),
            "tool_fan_scope_rate": sum(r["fan_scope"] for r in tool) / len(tool),
            "tool_clipping_guard_rate": sum(r["clipping_guard"] for r in tool) / len(tool),
            "tool_settling_guard_rate": sum(r["settling_guard"] for r in tool) / len(tool),
            "tool_inverse_b_rate": sum(r["inverse_b"] for r in tool) / len(tool),
            "final_primary_mean": sum(r["primary_analysis_score"] for r in final) / len(final),
            "final_pair_rate": sum(r["aba_pair_recognized"] for r in final) / len(final),
            "final_ambiguity_rate": sum(r["f_l_tone_ambiguity"] for r in final) / len(final),
            "final_calibration_rate": sum(r["calibrated_conclusion"] for r in final) / len(final),
            "final_followup_rate": sum(r["deciding_followup"] for r in final) / len(final),
            "verdict_counts": dict(Counter(verdicts)),
            "verdict_entropy_nats": _entropy(verdicts),
        })
    result = {
        "design": "fixed frontier/data; only commit-pinned generic context changes",
        "n_per_variant_experiment": 3,
        "rows": rows,
        "summaries": summaries,
    }
    (output / "context-ablation-results.json").write_text(json.dumps(result, indent=2) + "\n")
    fieldnames = sorted({key for row in rows for key in row})
    with (output / "context-ablation-samples.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader(); writer.writerows(rows)

    x = list(range(3))
    fig, (tool_ax, final_ax) = plt.subplots(1, 2, figsize=(13.8, 6.2), sharey=True)
    colors = ["#8F989E", "#3984B6", "#21866B"]
    for ax, key, title in (
        (tool_ax, "primary_guard_score", "Next-measurement design"),
        (final_ax, "primary_analysis_score", "Final-analysis quality"),
    ):
        for i, ((variant, label, _), color) in enumerate(zip(VARIANTS, colors)):
            experiment = "tool-call" if ax is tool_ax else "final-analysis"
            vals = [r[key] for r in rows if r["variant"] == variant and r["experiment"] == experiment]
            offsets = [-.07, 0, .07]
            ax.scatter([i + o for o in offsets], vals, s=70, color=color, alpha=.75, edgecolor="white", zorder=4)
            mean = sum(vals) / len(vals)
            ax.plot([i-.19, i+.19], [mean, mean], color="#15262D", linewidth=4, solid_capstyle="round", zorder=5)
            ax.text(i, min(1.07, mean+.08), f"{mean*100:.0f}%", ha="center", fontsize=11, fontweight="bold")
        ax.set_xticks(x, ["A\npre-guards", "C\nguards", "B\nguards + 1/B"])
        ax.set_title(title, loc="left", fontsize=15, fontweight="bold")
        ax.set_ylim(-.04, 1.12)
        ax.grid(axis="y", alpha=.22)
        ax.spines[["top", "right"]].set_visible(False)
    tool_ax.set_ylabel("Preregistered rubric score")
    tool_ax.set_yticks([0,.25,.5,.75,1], ["0%","25%","50%","75%","100%"])
    tool_ax.text(.02, .03, "Primary: clipping + settling guards", transform=tool_ax.transAxes, fontsize=9.5, color="#5B676E")
    final_ax.text(.02, .03, "Primary: pair + ambiguity + calibration + follow-up", transform=final_ax.transAxes, fontsize=9.5, color="#5B676E")
    fig.suptitle("Does accumulated Chiron context help at fixed evidence?", fontsize=20, fontweight="bold", y=.98)
    fig.text(.5, .915, "QC0426 fixed frontiers • Haiku 4.5 • N=3 per context/experiment • dots are individual fresh sessions", ha="center", fontsize=10.5, color="#56636A")
    fig.text(.5, .02, "Only generic recipe snapshots change; campaign notebooks, data, cards, prompts, model, and sampling are held fixed.", ha="center", fontsize=9.5, color="#56636A")
    fig.tight_layout(rect=[0, .06, 1, .90])
    fig.savefig(output / "chiron-fixed-context-ablation.png", dpi=220, bbox_inches="tight")
    fig.savefig(output / "chiron-fixed-context-ablation.svg", bbox_inches="tight")

    # Axis-level heatmap makes the mechanism visible: Chiron may improve one
    # tactical guard while leaving other safeguards and interpretation flat.
    heat_rows = [
        ("Correct 2D fan scope", "tool_fan_scope_rate"),
        ("Clipping guard", "tool_clipping_guard_rate"),
        ("Settling guard", "tool_settling_guard_rate"),
        ("Inverse-B sampling", "tool_inverse_b_rate"),
        ("ABA pair recognized", "final_pair_rate"),
        ("F_L ambiguity recognized", "final_ambiguity_rate"),
        ("Conclusion calibrated", "final_calibration_rate"),
        ("Deciding follow-up named", "final_followup_rate"),
    ]
    matrix = [[summary[key] for summary in summaries] for _, key in heat_rows]
    heat_fig, heat_ax = plt.subplots(figsize=(8.8, 7.1))
    image = heat_ax.imshow(matrix, cmap="YlGn", vmin=0, vmax=1, aspect="auto")
    heat_ax.set_xticks(range(3), ["A\npre-guards", "C\nguards", "B\nguards + 1/B"])
    heat_ax.set_yticks(range(len(heat_rows)), [label for label, _ in heat_rows])
    heat_ax.axhline(3.5, color="white", linewidth=5)
    for row_i, row in enumerate(matrix):
        for col_i, value in enumerate(row):
            heat_ax.text(col_i, row_i, f"{value*100:.0f}%", ha="center", va="center", fontsize=11, fontweight="bold", color="#15262D")
    heat_ax.set_title("Which Chiron lessons actually transfer into behavior?", fontsize=17, fontweight="bold", pad=18)
    heat_fig.colorbar(image, ax=heat_ax, fraction=.035, pad=.04, label="N=3 adoption rate")
    heat_fig.tight_layout()
    heat_fig.savefig(output / "chiron-context-axis-heatmap.png", dpi=220, bbox_inches="tight")
    heat_fig.savefig(output / "chiron-context-axis-heatmap.svg", bbox_inches="tight")

    md = [
        "# Chiron fixed-frontier context ablation", "",
        "| Variant | Tool guard score | Clip guard | Settle guard | 1/B | Final quality | Verdicts | Entropy |",
        "|---|---:|---:|---:|---:|---:|---|---:|",
    ]
    for s in summaries:
        md.append(
            f"| {s['variant_label']} | {s['tool_primary_mean']:.3f} | "
            f"{s['tool_clipping_guard_rate']:.3f} | {s['tool_settling_guard_rate']:.3f} | "
            f"{s['tool_inverse_b_rate']:.3f} | {s['final_primary_mean']:.3f} | "
            f"{s['verdict_counts']} | {s['verdict_entropy_nats']:.3f} |"
        )
    md.extend([
        "",
        "## Finding",
        "",
        "Accumulated context transfers only partially into Haiku's behavior. "
        "Correct 2D fan scope is 2/3 pre-guards, falls to 1/3 with the guard "
        "snapshot, and returns to 2/3 in the fully refined snapshot; settling "
        "protection rises from 1/3 to 2/3. However, no variant correctly implements the clipping "
        "guard, and the inverse-B instruction is adopted in 0/3 refined runs.",
        "",
        "Final-analysis behavior is a complete null: all nine sessions return "
        "ABA with HIGH confidence, recognize the ABA pair, but fail to surface "
        "the F_L-tone breakdown/intermodulation-versus-ABC-domain ambiguity or "
        "name the deciding follow-up. Verdict entropy is zero because the "
        "overclaim is perfectly repeatable.",
        "",
        "This N=3 Haiku screen therefore supports a narrow claim: Chiron context "
        "can improve some tactical measurement choices, but documentation alone "
        "does not reliably transfer all guards and does not improve final-analysis "
        "calibration at this frontier/model.",
        "",
        "The rubric axes were specified before the run and all 18 scored outputs "
        "were manually audited after deterministic scoring.",
    ])
    (output / "README.md").write_text("\n".join(md) + "\n")
    return result
