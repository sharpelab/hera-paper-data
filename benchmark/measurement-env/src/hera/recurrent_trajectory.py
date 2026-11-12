"""Teacher-forced recurrent evaluation on an abstracted historical campaign."""
from __future__ import annotations

import argparse
import concurrent.futures
import csv
import hashlib
import json
import math
import os
import re
import subprocess
import time
import uuid
from pathlib import Path
from typing import Any

import yaml

STATE_KEYS = ("aba", "abc", "aba_dominant_fl_fork", "unresolved")
SYSTEM_INSTRUCTION = """You are evaluating a historical condensed-matter campaign one evidence packet at a time. This is a teacher-forced replay: recommend the scientifically best next action, but the evaluator will reveal the same archived next observation regardless of your recommendation. Retain and revise your beliefs across turns. Do not assume a clean homogeneous device. Distinguish an ABA pair summing to F_L from a tone at F_L, whose origin may remain ambiguous between an ABC pocket and ABA magnetic-breakdown/intermodulation. Be explicit about acquisition faults and whether a conclusion must be retracted. You have no tools and must use only the generic context and evidence provided.

Return exactly one JSON object, without markdown, with this shape:
{
  "belief": {"aba": 0.0, "abc": 0.0, "aba_dominant_fl_fork": 0.0, "unresolved": 1.0},
  "confidence": 0.0,
  "current_read": "...",
  "evidence_used": ["..."],
  "ambiguities": ["..."],
  "next_action": {"class": "gate_map|sdh_spot_check|rerange_and_repeat|density_fan|temperature_ladder|audit_or_refit|corrected_temperature_ladder|streda_or_report_caveat|other", "rationale": "...", "critical_parameters": ["..."]},
  "guards": {"clipping": null, "settling": null, "explicit_sensitivity": null, "frequency_separation": null, "cost_control": null},
  "correction": {"retracted_prior": false, "what_changed": "..."}
}
Probabilities must be numeric, nonnegative, and sum to 1. Confidence is 0 to 1. Keep the entire response under 1,200 words, use at most four short strings per array, and JSON-escape every string; never place a literal newline or an unescaped quotation mark inside a JSON string.
"""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def tree_hash(path: Path) -> str:
    if path.is_file():
        return sha256_file(path)
    h = hashlib.sha256()
    for child in sorted(item for item in path.rglob("*") if item.is_file()):
        h.update(child.relative_to(path).as_posix().encode())
        h.update(b"\0")
        h.update(bytes.fromhex(sha256_file(child)))
    return h.hexdigest()


def load_manifest(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text())
    if data.get("version") != 1:
        raise ValueError("unsupported recurrent-trajectory manifest version")
    if tuple(data.get("states", [])) != STATE_KEYS:
        raise ValueError(f"states must be {STATE_KEYS}")
    for step in data.get("steps", []):
        target = step.get("target", {})
        if set(target) != set(STATE_KEYS) or not math.isclose(sum(target.values()), 1.0):
            raise ValueError(f"invalid target distribution for {step.get('id')}")
    return data


def git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", "-C", str(repo), *args], check=check, capture_output=True
    )


def prepare(manifest_path: Path, output: Path, repo: Path) -> dict[str, Any]:
    manifest = load_manifest(manifest_path)
    if output.exists():
        raise FileExistsError(f"refusing to overwrite immutable preparation: {output}")
    output.mkdir(parents=True)
    contexts_dir = output / "contexts"
    contexts_dir.mkdir()
    context_records: dict[str, Any] = {}
    for context_id, spec in manifest["contexts"].items():
        commit = git(repo, "rev-parse", spec["commit"]).stdout.decode().strip()
        parts: list[str] = []
        files: list[dict[str, Any]] = []
        for rel in manifest["context_files"]:
            probe = git(repo, "cat-file", "-e", f"{commit}:{rel}", check=False)
            if probe.returncode:
                files.append({"path": rel, "status": "absent"})
                continue
            content = git(repo, "show", f"{commit}:{rel}").stdout
            blob = git(repo, "rev-parse", f"{commit}:{rel}").stdout.decode().strip()
            text = content.decode("utf-8", errors="replace")
            parts.append(f"\n===== GENERIC CONTEXT: {rel} =====\n{text.rstrip()}\n")
            files.append({
                "path": rel,
                "status": "included",
                "git_blob": blob,
                "sha256": sha256_bytes(content),
            })
        combined = "".join(parts).lstrip()
        context_path = contexts_dir / f"{context_id}.md"
        context_path.write_text(combined)
        context_records[context_id] = {
            "label": spec["label"],
            "commit_requested": spec["commit"],
            "commit_resolved": commit,
            "combined_sha256": sha256_bytes(combined.encode()),
            "files": files,
        }
    source_root = Path(manifest["source_root"])
    packet_records = []
    for index, step in enumerate(manifest["steps"]):
        sources = []
        for rel in step["sources"]:
            source = source_root / rel
            if not source.exists():
                raise FileNotFoundError(source)
            sources.append({
                "path": rel,
                "kind": "directory" if source.is_dir() else "file",
                "sha256": tree_hash(source),
            })
        packet_records.append({
            "index": index,
            "id": step["id"],
            "label": step["label"],
            "evidence_sha256": sha256_bytes(step["evidence"].encode()),
            "sources": sources,
        })
    provenance = {
        "status": "immutable recurrent trajectory prepared",
        "manifest": str(manifest_path.resolve()),
        "manifest_sha256": sha256_file(manifest_path),
        "source_root": str(source_root),
        "contexts": context_records,
        "packets": packet_records,
        "source_policy": "read-only; hashes only; no source files copied into model workspace",
    }
    (output / "provenance.json").write_text(json.dumps(provenance, indent=2) + "\n")
    (output / "empty-mcp.json").write_text('{"mcpServers": {}}\n')
    return provenance


def extract_json(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", cleaned, flags=re.I | re.S)
    decoder = json.JSONDecoder()
    for pos, char in enumerate(cleaned):
        if char != "{":
            continue
        try:
            value, _ = decoder.raw_decode(cleaned[pos:])
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict) and "belief" in value:
            return value
    raise ValueError("no JSON object in model result")


def validate_response(parsed: dict[str, Any]) -> None:
    belief = parsed.get("belief")
    if not isinstance(belief, dict) or set(belief) != set(STATE_KEYS):
        raise ValueError("belief has wrong keys")
    values = [float(belief[key]) for key in STATE_KEYS]
    if any(not math.isfinite(value) or value < 0 for value in values):
        raise ValueError("belief values must be finite and nonnegative")
    if not math.isclose(sum(values), 1.0, abs_tol=0.02):
        raise ValueError("belief does not sum to one")
    confidence = float(parsed.get("confidence"))
    if not 0 <= confidence <= 1:
        raise ValueError("confidence outside [0,1]")
    if not isinstance(parsed.get("next_action"), dict):
        raise ValueError("next_action missing")


def build_turn_prompt(
    step: dict[str, Any], index: int, total: int, context_text: str | None = None
) -> str:
    parts = []
    if context_text is not None:
        parts.extend([
            SYSTEM_INSTRUCTION,
            "\nThe following is the complete generic Chiron context snapshot for this trajectory. It contains no campaign result:\n",
            context_text,
        ])
    parts.extend([
        f"\nHISTORICAL EVIDENCE PACKET {index + 1}/{total} — {step['label']}\n",
        step["evidence"].strip(),
        "\nUpdate your state and return the required JSON object. Do not quote or anticipate future packets.",
    ])
    return "\n".join(parts)


def claude_command(
    *, prompt: str, model: str, session_id: str, first: bool, mcp_config: Path
) -> list[str]:
    command = [
        "claude", "-p", prompt,
        "--output-format", "json",
        "--model", model,
        "--tools", "",
        "--disable-slash-commands",
        "--strict-mcp-config",
        "--mcp-config", str(mcp_config),
        "--setting-sources", "",
    ]
    command += ["--session-id", session_id] if first else ["--resume", session_id]
    return command


def _run_one_trajectory(
    *, manifest_path: Path, prepared: Path, run_root: Path,
    context_id: str, sample: int,
) -> dict[str, Any]:
    manifest = load_manifest(manifest_path)
    provenance = json.loads((prepared / "provenance.json").read_text())
    context_text = (prepared / "contexts" / f"{context_id}.md").read_text()
    trajectory_dir = run_root / "trajectories" / context_id / f"sample-{sample:02d}"
    trajectory_dir.mkdir(parents=True, exist_ok=True)
    session_file = trajectory_dir / "session.json"
    if session_file.exists():
        session_meta = json.loads(session_file.read_text())
        session_id = session_meta["session_id"]
    else:
        session_id = str(uuid.uuid4())
        session_meta = {
            "session_id": session_id,
            "context": context_id,
            "context_sha256": provenance["contexts"][context_id]["combined_sha256"],
            "sample": sample,
            "model_requested": manifest["model"],
        }
        session_file.write_text(json.dumps(session_meta, indent=2) + "\n")
    completed = 0
    for index, step in enumerate(manifest["steps"]):
        step_dir = trajectory_dir / f"step-{index:02d}-{step['id']}"
        record_path = step_dir / "turn.json"
        retry_status = None
        if record_path.exists():
            try:
                prior_record = json.loads(record_path.read_text())
                if prior_record.get("status") == "ok":
                    completed += 1
                    continue
                retry_status = prior_record.get("status")
            except json.JSONDecodeError:
                retry_status = "corrupt_record"
        if completed != index:
            return {"context": context_id, "sample": sample, "status": "blocked", "completed": completed}
        step_dir.mkdir(parents=True, exist_ok=True)
        if retry_status:
            attempts = step_dir / "failed-attempts"
            attempts.mkdir(exist_ok=True)
            attempt_number = len(list(attempts.glob("attempt-*-turn.json"))) + 1
            for name in ("prompt.txt", "stdout.json", "stderr.txt", "response.txt", "turn.json"):
                source = step_dir / name
                if source.exists():
                    source.rename(attempts / f"attempt-{attempt_number:02d}-{name}")
        if retry_status == "parse_error":
            prompt = (
                "Your previous response to the current historical packet was not valid JSON. "
                "Keep the same scientific assessment and return only a corrected JSON object "
                "with the required schema. The evidence is already in this conversation."
            )
        else:
            prompt = build_turn_prompt(
                step, index, len(manifest["steps"]), context_text if index == 0 else None
            )
        (step_dir / "prompt.txt").write_text(prompt)
        command = claude_command(
            prompt=prompt,
            model=manifest["model"],
            session_id=session_id,
            first=index == 0 and retry_status is None,
            mcp_config=prepared / "empty-mcp.json",
        )
        started = time.monotonic()
        proc = subprocess.run(
            command,
            cwd=trajectory_dir,
            capture_output=True,
            text=True,
            timeout=int(manifest["timeout_s"]),
            env={**os.environ, "NO_COLOR": "1"},
        )
        duration = time.monotonic() - started
        (step_dir / "stdout.json").write_text(proc.stdout)
        (step_dir / "stderr.txt").write_text(proc.stderr)
        record: dict[str, Any] = {
            "context": context_id,
            "sample": sample,
            "step_index": index,
            "step_id": step["id"],
            "session_id": session_id,
            "prompt_sha256": sha256_bytes(prompt.encode()),
            "packet_sha256": sha256_bytes(step["evidence"].encode()),
            "context_sha256": provenance["contexts"][context_id]["combined_sha256"],
            "returncode": proc.returncode,
            "duration_s": duration,
        }
        try:
            envelope = json.loads(proc.stdout)
            result_text = envelope.get("result", "")
            parsed = extract_json(result_text)
            validate_response(parsed)
            record.update({
                "status": "ok" if proc.returncode == 0 else "nonzero",
                "parsed": parsed,
                "model_resolved": envelope.get("model") or manifest["model"],
                "usage": envelope.get("usage"),
                "model_usage": envelope.get("modelUsage"),
                "total_cost_usd": envelope.get("total_cost_usd"),
                "num_turns": envelope.get("num_turns"),
            })
            (step_dir / "response.txt").write_text(result_text)
        except Exception as exc:
            record.update({"status": "parse_error", "error": f"{type(exc).__name__}: {exc}"})
        record_path.write_text(json.dumps(record, indent=2) + "\n")
        if record["status"] != "ok":
            return {"context": context_id, "sample": sample, "status": record["status"], "completed": completed}
        completed += 1
    return {"context": context_id, "sample": sample, "status": "ok", "completed": completed}


def run(
    manifest_path: Path, prepared: Path, run_root: Path, workers: int = 3
) -> list[dict[str, Any]]:
    manifest = load_manifest(manifest_path)
    run_root.mkdir(parents=True, exist_ok=True)
    metadata = {
        "manifest": str(manifest_path.resolve()),
        "manifest_sha256": sha256_file(manifest_path),
        "prepared": str(prepared.resolve()),
        "prepared_provenance_sha256": sha256_file(prepared / "provenance.json"),
        "design": "persistent-session teacher-forced historical trajectory",
    }
    (run_root / "run.json").write_text(json.dumps(metadata, indent=2) + "\n")
    jobs = [
        {"manifest_path": manifest_path, "prepared": prepared, "run_root": run_root,
         "context_id": context_id, "sample": sample}
        for context_id in manifest["contexts"]
        for sample in range(1, int(manifest["samples"]) + 1)
    ]
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(_run_one_trajectory, **job) for job in jobs]
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            results.append(result)
            print(json.dumps(result), flush=True)
    return results


def score_turn(record: dict[str, Any], step: dict[str, Any]) -> dict[str, Any]:
    parsed = record["parsed"]
    belief = {key: float(parsed["belief"][key]) for key in STATE_KEYS}
    total = sum(belief.values())
    belief = {key: value / total for key, value in belief.items()}
    target = {key: float(step["target"][key]) for key in STATE_KEYS}
    cross_entropy = -sum(target[key] * math.log(max(belief[key], 1e-9)) for key in STATE_KEYS)
    target_entropy = -sum(
        target[key] * math.log(target[key]) for key in STATE_KEYS if target[key] > 0
    )
    expert_loss = cross_entropy - target_entropy
    brier = sum((belief[key] - target[key]) ** 2 for key in STATE_KEYS)
    dominant_target = max(target, key=target.get)
    action_class = str((parsed.get("next_action") or {}).get("class", "other"))
    text = json.dumps(parsed, sort_keys=True).lower()
    fork_segments = [str(parsed.get("current_read", ""))] + [
        str(item) for item in (parsed.get("ambiguities") or [])
    ]
    fork_pattern = re.compile(
        r"minority.{0,20}abc|abc.{0,20}minority|"
        r"(?:f_l|m_fl).{0,100}(?:ambigu|fork|unresolved|cannot distinguish|possible|versus)|"
        r"(?:breakdown|intermod).{0,100}(?:ambigu|fork|unresolved|cannot|possible|versus)",
        re.I | re.S,
    )
    closure_pattern = re.compile(
        r"(?:breakdown|intermod).{0,80}(?:excluded|ruled out|not a)|"
        r"resolv(?:e|ed|es|ing).{0,50}(?:fork|toward)|"
        r"fork.{0,30}resolv(?:e|ed|es|ing)",
        re.I | re.S,
    )
    open_fork_in_text = any(
        fork_pattern.search(segment) and not closure_pattern.search(segment)
        for segment in fork_segments
    )
    fork_recognized = belief["aba_dominant_fl_fork"] >= 0.30 or open_fork_in_text
    correction = parsed.get("correction") or {}
    correction_text = str(correction.get("what_changed", "")).lower()
    corrected = bool(correction.get("retracted_prior")) or bool(re.search(
        r"retract|revise|demot|no longer|inconclusive|cannot distinguish",
        correction_text,
    ))
    evidence_specificity = min(
        1.0,
        (len(parsed.get("evidence_used") or []) / 3)
        + (0.25 if re.search(r"\d", text) else 0),
    )
    confidence = float(parsed["confidence"])
    max_state = max(belief, key=belief.get)
    unsupported_confidence = bool(
        confidence >= 0.8
        and (
            step["id"] in {"initial", "map"}
            or (max_state in {"aba", "abc"} and target["aba_dominant_fl_fork"] >= 0.65)
        )
    )
    return {
        "cross_entropy": cross_entropy,
        "target_entropy": target_entropy,
        "expert_loss_kl": expert_loss,
        "brier": brier,
        "dominant_target": dominant_target,
        "target_state_mass": belief[dominant_target],
        "belief": belief,
        "confidence": confidence,
        "action_class": action_class,
        "action_quality": action_class in step["acceptable_actions"],
        "fork_recognized": fork_recognized,
        "correction_recognized": corrected,
        "evidence_specificity": evidence_specificity,
        "unsupported_confidence": unsupported_confidence,
        "guards": parsed.get("guards") or {},
    }


def collect_scores(manifest_path: Path, run_root: Path) -> list[dict[str, Any]]:
    manifest = load_manifest(manifest_path)
    rows = []
    for path in sorted(run_root.glob("trajectories/*/sample-*/step-*/turn.json")):
        record = json.loads(path.read_text())
        if record.get("status") != "ok":
            continue
        step = manifest["steps"][int(record["step_index"])]
        score = score_turn(record, step)
        rows.append({
            "context": record["context"],
            "sample": record["sample"],
            "step_index": record["step_index"],
            "step_id": record["step_id"],
            "step_label": step["label"],
            **score,
        })
    by_trajectory: dict[tuple[str, int], list[dict[str, Any]]] = {}
    for row in rows:
        by_trajectory.setdefault((row["context"], row["sample"]), []).append(row)
    for trajectory in by_trajectory.values():
        trajectory.sort(key=lambda item: item["step_index"])
        previous = None
        fork_seen = False
        for row in trajectory:
            row["loss_regression"] = bool(
                previous is not None
                and row["expert_loss_kl"] > previous["expert_loss_kl"] + 0.05
            )
            row["fork_dropped"] = bool(fork_seen and not row["fork_recognized"])
            fork_seen = fork_seen or row["fork_recognized"]
            previous = row
    return rows


def analyze(manifest_path: Path, run_root: Path, output: Path) -> dict[str, Any]:
    import matplotlib.pyplot as plt
    import numpy as np

    manifest = load_manifest(manifest_path)
    rows = collect_scores(manifest_path, run_root)
    expected = len(manifest["contexts"]) * int(manifest["samples"]) * len(manifest["steps"])
    if len(rows) != expected:
        raise RuntimeError(f"analysis requires {expected} valid turns, found {len(rows)}")
    output.mkdir(parents=True, exist_ok=True)
    serializable = []
    for row in rows:
        flattened = dict(row)
        flattened["belief"] = json.dumps(row["belief"], sort_keys=True)
        flattened["guards"] = json.dumps(row["guards"], sort_keys=True)
        serializable.append(flattened)
    with (output / "trajectory-scores.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(serializable[0]))
        writer.writeheader()
        writer.writerows(serializable)

    labels = [step["label"] for step in manifest["steps"]]
    colors = {"early": "#8A98A0", "guarded": "#398AB9", "mature": "#169873"}
    fig, axes = plt.subplots(2, 1, figsize=(14, 9), sharex=True, gridspec_kw={"hspace": .10})
    xs = np.arange(len(labels))
    summaries = {}
    for context_id, context_spec in manifest["contexts"].items():
        context_rows = [row for row in rows if row["context"] == context_id]
        trajectories = []
        for sample in range(1, int(manifest["samples"]) + 1):
            trajectory = sorted(
                [row for row in context_rows if row["sample"] == sample],
                key=lambda row: row["step_index"],
            )
            forks = [float(row["fork_recognized"]) for row in trajectory]
            confidences = [row["confidence"] for row in trajectory]
            trajectories.append(trajectory)
            axes[0].plot(xs, forks, color=colors[context_id], alpha=.25, linewidth=1.4)
            axes[1].plot(xs, confidences, color=colors[context_id], alpha=.25, linewidth=1.4)
        mean_fork = np.mean([[float(row["fork_recognized"]) for row in tr] for tr in trajectories], axis=0)
        mean_confidence = np.mean([[row["confidence"] for row in tr] for tr in trajectories], axis=0)
        mean_loss = np.mean([[row["expert_loss_kl"] for row in tr] for tr in trajectories], axis=0)
        mean_brier = np.mean([[row["brier"] for row in tr] for tr in trajectories], axis=0)
        mean_fork_mass = np.mean([[row["belief"]["aba_dominant_fl_fork"] for row in tr] for tr in trajectories], axis=0)
        axes[0].plot(xs, mean_fork, color=colors[context_id], linewidth=3, marker="o", label=context_spec["label"])
        axes[1].plot(xs, mean_confidence, color=colors[context_id], linewidth=3, marker="o", label=context_spec["label"])
        summaries[context_id] = {
            "label": context_spec["label"],
            "mean_expert_loss_kl_by_step": mean_loss.tolist(),
            "mean_brier_by_step": mean_brier.tolist(),
            "mean_fork_mass_by_step": mean_fork_mass.tolist(),
            "fork_recognition_rate_by_step": mean_fork.tolist(),
            "mean_confidence_by_step": mean_confidence.tolist(),
            "trajectory_mean_expert_loss_kl": [float(np.mean([row["expert_loss_kl"] for row in tr])) for tr in trajectories],
            "action_quality_rate": float(np.mean([row["action_quality"] for row in context_rows])),
            "fork_recognition_rate": float(np.mean([row["fork_recognized"] for row in context_rows])),
            "loss_regression_rate": float(np.mean([row["loss_regression"] for row in context_rows])),
        }
    axes[0].axvspan(4.65, 5.35, color="#F4C95D", alpha=.15)
    axes[0].annotate(
        "Before the operator audit — no monotonic context gain:\n"
        f"early {summaries['early']['fork_recognition_rate_by_step'][5] * 3:.0f}/3; "
        f"guarded {summaries['guarded']['fork_recognition_rate_by_step'][5] * 3:.0f}/3; "
        f"mature {summaries['mature']['fork_recognition_rate_by_step'][5] * 3:.0f}/3",
        xy=(5, 1.0), xytext=(3.65, .78),
        arrowprops={"arrowstyle": "->", "color": "#4B555A"},
        fontsize=10.5, fontweight="bold",
    )
    axes[0].set_ylabel("Explicit F_L-origin fork recognition")
    axes[0].set_ylim(-.05, 1.08)
    axes[0].set_title("Context changes the path — but every recurrent state collapses the open fork", fontsize=17, fontweight="bold")
    axes[0].legend(frameon=False, ncol=3, loc="lower right")
    axes[0].grid(axis="y", alpha=.2)
    axes[1].set_ylabel("Self-reported confidence")
    axes[1].set_ylim(-.03, 1.03)
    axes[1].grid(axis="y", alpha=.2)
    axes[1].set_xticks(xs, labels, rotation=25, ha="right")
    fig.text(.5, .01, "QC0426 July 18 historical evidence • persistent Haiku sessions • N=3/context • thin lines are trajectories", ha="center", color="#56636A")
    fig.tight_layout(rect=[0, .04, 1, 1])
    fig.savefig(output / "chiron-recurrent-trajectories.png", dpi=220, bbox_inches="tight")
    fig.savefig(output / "chiron-recurrent-trajectories.svg", bbox_inches="tight")

    # Direct RNN-style state plot: no rubric compression, just the belief vector
    # emitted by each persistent session after each historical observation.
    state_colors = {
        "aba": "#2878B5",
        "abc": "#D97732",
        "aba_dominant_fl_fork": "#169873",
        "unresolved": "#8A98A0",
    }
    state_labels = {
        "aba": "ABA only",
        "abc": "ABC only",
        "aba_dominant_fl_fork": "ABA-dominant + F_L fork",
        "unresolved": "Unresolved",
    }
    belief_fig, belief_axes = plt.subplots(3, 1, figsize=(14, 11), sharex=True)
    target_fork = np.array([
        float(step["target"]["aba_dominant_fl_fork"]) for step in manifest["steps"]
    ])
    for axis, (context_id, context_spec) in zip(belief_axes, manifest["contexts"].items()):
        context_rows = [row for row in rows if row["context"] == context_id]
        for state in STATE_KEYS:
            values = np.array([
                [
                    row["belief"][state]
                    for row in sorted(
                        [item for item in context_rows if item["sample"] == sample],
                        key=lambda item: item["step_index"],
                    )
                ]
                for sample in range(1, int(manifest["samples"]) + 1)
            ])
            axis.fill_between(
                xs, values.min(axis=0), values.max(axis=0),
                color=state_colors[state], alpha=.10,
            )
            axis.plot(
                xs, values.mean(axis=0), marker="o", linewidth=2.5,
                color=state_colors[state], label=state_labels[state],
            )
        axis.plot(xs, target_fork, color="#20282C", linestyle="--", linewidth=1.5,
                  label="Expert fork-state corridor" if context_id == "early" else None)
        axis.axvline(6, color="#F1B83B", linewidth=1.5, alpha=.8)
        axis.set_ylim(-.03, 1.03)
        axis.set_ylabel(context_spec["label"], fontweight="bold")
        axis.grid(axis="y", alpha=.18)
    belief_axes[0].set_title(
        "Same historical evidence, different recurrent belief paths",
        fontsize=18, fontweight="bold",
    )
    belief_axes[0].legend(frameon=False, ncol=5, loc="upper center", bbox_to_anchor=(.5, 1.02))
    belief_axes[-1].set_xticks(xs, labels, rotation=25, ha="right")
    belief_fig.text(.79, .49, "operator audit →", color="#9C6D00", fontweight="bold")
    belief_fig.text(.5, .01, "Lines are N=3 means; bands span individual persistent sessions. Dashed line is the preregistered expert fork-state mass.", ha="center", color="#56636A")
    belief_fig.tight_layout(rect=[0, .04, 1, .98])
    belief_fig.savefig(output / "chiron-belief-trajectories.png", dpi=220, bbox_inches="tight")
    belief_fig.savefig(output / "chiron-belief-trajectories.svg", bbox_inches="tight")

    ordered = []
    matrix = []
    for context_id in manifest["contexts"]:
        for sample in range(1, int(manifest["samples"]) + 1):
            trajectory = sorted(
                [row for row in rows if row["context"] == context_id and row["sample"] == sample],
                key=lambda row: row["step_index"],
            )
            ordered.append(f"{context_id} {sample}")
            matrix.append([
                int(row["loss_regression"]) + int(row["fork_dropped"]) for row in trajectory[1:]
            ])
    heat_fig, heat_ax = plt.subplots(figsize=(12, 5.8))
    image = heat_ax.imshow(matrix, cmap="YlOrRd", vmin=0, vmax=2, aspect="auto")
    heat_ax.set_yticks(range(len(ordered)), ordered)
    heat_ax.set_xticks(range(len(labels) - 1), [f"→ {label}" for label in labels[1:]], rotation=25, ha="right")
    heat_ax.set_title("Trajectory regressions: loss increase and forgotten fork", fontsize=16, fontweight="bold")
    for i, row in enumerate(matrix):
        for j, value in enumerate(row):
            heat_ax.text(j, i, str(value), ha="center", va="center", fontweight="bold")
    heat_fig.colorbar(image, ax=heat_ax, label="0 none • 1 one regression • 2 both")
    heat_fig.tight_layout()
    heat_fig.savefig(output / "chiron-trajectory-regressions.png", dpi=220, bbox_inches="tight")
    heat_fig.savefig(output / "chiron-trajectory-regressions.svg", bbox_inches="tight")

    result = {
        "design": "recurrent teacher-forced historical replay",
        "valid_turns": len(rows),
        "expected_turns": expected,
        "summaries": summaries,
        "rows": rows,
    }
    (output / "trajectory-results.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    prepare_parser = sub.add_parser("prepare")
    prepare_parser.add_argument("--manifest", type=Path, required=True)
    prepare_parser.add_argument("--output", type=Path, required=True)
    prepare_parser.add_argument("--repo", type=Path, default=Path.cwd())
    run_parser = sub.add_parser("run")
    run_parser.add_argument("--manifest", type=Path, required=True)
    run_parser.add_argument("--prepared", type=Path, required=True)
    run_parser.add_argument("--output", type=Path, required=True)
    run_parser.add_argument("--workers", type=int, default=3)
    analyze_parser = sub.add_parser("analyze")
    analyze_parser.add_argument("--manifest", type=Path, required=True)
    analyze_parser.add_argument("--run", type=Path, required=True)
    analyze_parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.command == "prepare":
        print(json.dumps(prepare(args.manifest, args.output, args.repo), indent=2))
    elif args.command == "run":
        run(args.manifest, args.prepared, args.output, args.workers)
    else:
        print(json.dumps(analyze(args.manifest, args.run, args.output)["summaries"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
