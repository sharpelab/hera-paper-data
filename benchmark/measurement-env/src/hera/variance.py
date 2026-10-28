"""HERA replay-variance experiment runner.

Narrow, standalone CLI for replay-variance experiments:

    curated frontier manifest
        -> leak-checked, hash-verified materialized workspaces (read-only on source)
        -> N fresh headless agent sessions per (campaign, experiment)
        -> raw + parsed sample records (resumable)
        -> deterministic entropy / spread / ground-truth-NLL statistics
        -> cross-campaign JSON/CSV/Markdown summaries + PNG/SVG plots

Variance metrics measure *repeatability*, never correctness. Ground-truth NLL
is reported separately for verdict experiments. Across-trial trends are
observational: campaigns differ in acquired evidence and context, so they do
not by themselves identify causal changes.

Owned surfaces: this module, tests/hera/test_variance.py,
hera/experiments/qc0426-aba-vs-abc-variance.yaml, and the `hera-variance`
script entry. Outputs go under $HERA_DATA/variance (or ~/.hera/variance),
never under the source campaigns.
"""

from __future__ import annotations

import argparse
import copy
import csv
import gzip
import hashlib
import json
import math
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import yaml

from hera.tool_variance import ToolVarianceError, summarize_root as summarize_tool_variance
from hera.variance_compare import ComparisonError, compare_outputs

plt.switch_backend("Agg")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

EXPERIMENT_KINDS = ("tool-call", "final-analysis")
VERDICTS = ("ABA", "ABC", "UNDERDETERMINED")
CONFIDENCES = ("LOW", "MEDIUM", "HIGH")
ALWAYS_EXCLUDED = (
    "session_notes.md",
    ".transcripts/",
    "hera_scratch/",
    ".ipynb_checkpoints/",
    "corpus_provenance.json",
)
NLL_ALPHA = 0.5  # Jeffreys smoothing prior for ground-truth NLL at finite N

TOOL_CALL_LEAK_TERMS = [
    "STACKING CALL",
    "THE CALL",
    "Primary goal met",
    "QC0426 is",
    "QC0426 =",
    "final Step-7",
    "ABA confirmed",
    "ABA (strong)",
    "ABA \u2014 strong",
    "not ABC",
    "ABC excluded",
    "ABA (Bernal), strong",
]

FINAL_ANALYSIS_LEAK_TERMS = [
    "ABA",
    "ABC",
    "STACKING CALL",
    "THE CALL",
    "stacking call",
    "Primary goal met",
    "final Step-7",
    "QC0426 is",
    "QC0426 =",
    "ABA confirmed",
]

# The campaign-goal line of the session brief poses the question; it is the
# only place bare ABA/ABC is legitimate in a final-analysis workspace.
BRIEF_QUESTION_ALLOWED = [r"ABA \(Bernal\) vs ABC \(rhombohedral\)"]

SANITIZE_LINE_PLACEHOLDER = "# [line removed by hera-variance sanitizer]"
SANITIZE_OUTPUT_PLACEHOLDER = "[output removed by hera-variance sanitizer]\n"
SANITIZE_JSON_PLACEHOLDER = "[text removed by hera-variance sanitizer]"


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


class VarianceError(Exception):
    """Base error for the variance runner."""


class ManifestError(VarianceError):
    """Manifest failed validation."""


class LeakError(VarianceError):
    """Verdict leakage detected in a model-visible workspace (fail closed)."""


# ---------------------------------------------------------------------------
# Manifest loading / validation
# ---------------------------------------------------------------------------


def validate_manifest(doc: Any) -> None:
    if not isinstance(doc, dict):
        raise ManifestError("manifest must be a YAML mapping")
    for key in ("version", "experiment_id", "harness", "campaigns"):
        if key not in doc:
            raise ManifestError(f"manifest missing required key: {key}")
    if doc["version"] != 1:
        raise ManifestError(f"unsupported manifest version: {doc['version']!r}")
    harness = doc["harness"]
    if not isinstance(harness, dict):
        raise ManifestError("harness must be a mapping")
    if harness.get("kind") not in ("claude-p", "fake"):
        raise ManifestError(
            f"harness.kind must be 'claude-p' or 'fake', got {harness.get('kind')!r}"
        )
    campaigns = doc["campaigns"]
    if not isinstance(campaigns, list) or not campaigns:
        raise ManifestError("campaigns must be a non-empty list")
    seen_ids: set[str] = set()
    for camp in campaigns:
        if not isinstance(camp, dict):
            raise ManifestError("each campaign must be a mapping")
        for key in ("id", "trial", "source", "experiments"):
            if key not in camp:
                raise ManifestError(f"campaign missing required key: {key}")
        if camp["id"] in seen_ids:
            raise ManifestError(f"duplicate campaign id: {camp['id']}")
        seen_ids.add(camp["id"])
        if not isinstance(camp["trial"], int) or camp["trial"] < 1:
            raise ManifestError(f"campaign {camp['id']}: trial must be int >= 1")
        src = Path(camp["source"]).expanduser()
        if not src.is_dir():
            raise ManifestError(f"campaign {camp['id']}: source dir not found: {src}")
        exps = camp.get("experiments")
        if not isinstance(exps, dict) or not exps:
            raise ManifestError(f"campaign {camp['id']}: experiments must be a mapping")
        gt = camp.get("ground_truth")
        verdict_supports = [
            tuple(cfg.get("verdict_support", VERDICTS))
            for kind, cfg in exps.items()
            if kind == "final-analysis" and isinstance(cfg, dict)
        ]
        allowed_truths = set().union(*verdict_supports) if verdict_supports else set(VERDICTS)
        if gt is not None and gt not in allowed_truths:
            raise ManifestError(
                f"campaign {camp['id']}: ground_truth {gt!r} is not in final-analysis "
                f"verdict support {sorted(allowed_truths)}"
            )
        for kind, cfg in exps.items():
            if kind not in EXPERIMENT_KINDS:
                raise ManifestError(
                    f"campaign {camp['id']}: unknown experiment kind {kind!r}"
                )
            if not isinstance(cfg, dict):
                raise ManifestError(f"campaign {camp['id']}.{kind}: must be a mapping")
            if kind == "tool-call":
                for key in ("cut_index", "measure_notebook", "data_runs"):
                    if key not in cfg:
                        raise ManifestError(
                            f"campaign {camp['id']}.tool-call missing required key: {key}"
                        )
            else:
                for key in ("measure_notebook", "analysis_notebook", "data_runs"):
                    if key not in cfg:
                        raise ManifestError(
                            f"campaign {camp['id']}.final-analysis missing required key: {key}"
                        )
                support = cfg.get("verdict_support", VERDICTS)
                if (not isinstance(support, (list, tuple)) or len(support) < 2
                        or not all(isinstance(v, str) and v for v in support)
                        or len(set(support)) != len(support)):
                    raise ManifestError(
                        f"campaign {camp['id']}.final-analysis verdict_support must "
                        "contain at least two unique non-empty strings"
                    )
                if "analysis_task" in cfg and not isinstance(cfg["analysis_task"], str):
                    raise ManifestError(
                        f"campaign {camp['id']}.final-analysis analysis_task must be a string"
                    )


def load_manifest(path: Path) -> dict:
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    doc = yaml.safe_load(text) or {}
    validate_manifest(doc)
    return doc


def experiment_defaults(cfg: dict) -> dict:
    """Fill per-experiment defaults; returns a new dict."""
    out = dict(cfg)
    out.setdefault("include", [])
    out.setdefault("leak_terms", [])
    out.setdefault("allowed_patterns", [])
    out.setdefault("allowed_in", [])
    out.setdefault("samples", 5)
    out.setdefault("sanitize", False)
    out.setdefault("verdict_support", list(VERDICTS))
    return out


# ---------------------------------------------------------------------------
# Notebook processing
# ---------------------------------------------------------------------------


def load_nb(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def dump_nb(nb: dict) -> str:
    return json.dumps(nb, indent=1)


def crop_nb(nb: dict, cut_index: int) -> dict:
    """Keep cells [0..cut_index] inclusive (sources + outputs)."""
    out = dict(nb)
    out["cells"] = nb.get("cells", [])[: cut_index + 1]
    return out


def _cell_text_matches(cell: dict, terms: list[str]) -> bool:
    def any_term(text: str) -> bool:
        return any(t in text for t in terms)

    if any_term("".join(cell.get("source", []))):
        return True
    for out in cell.get("outputs", []):
        otype = out.get("output_type")
        if otype == "stream":
            if any_term("".join(out.get("text", []))):
                return True
        elif otype in ("execute_result", "display_data"):
            data = out.get("data", {})
            if "text/plain" in data and any_term(" ".join(data["text/plain"])):
                return True
        elif otype == "error":
            if any_term("\n".join(out.get("traceback", []))):
                return True
    return False


def sanitize_nb(nb: dict, leak_terms: list[str]) -> tuple[dict, dict]:
    """Final-analysis sanitization.

    Drops narrative markdown cells entirely; for code cells strips source
    lines and textual outputs containing any leak term (numeric/image outputs
    are preserved). Returns (sanitized notebook, per-cell report).
    """
    report: dict[str, Any] = {}
    kept: list[dict] = []
    for idx, cell in enumerate(nb.get("cells", [])):
        if cell.get("cell_type") == "markdown":
            report[str(idx)] = {"action": "dropped-markdown"}
            continue
        new = copy.deepcopy(cell)
        lines_removed = 0
        if "source" in new:
            src = []
            for line in new["source"]:
                for piece in line.splitlines(keepends=True) or [line]:
                    if any(t in piece for t in leak_terms):
                        src.append(SANITIZE_LINE_PLACEHOLDER + "\n")
                        lines_removed += 1
                    else:
                        src.append(piece)
            new["source"] = src
        outputs_removed = 0
        for out in new.get("outputs", []):
            otype = out.get("output_type")
            if otype == "stream":
                text = "".join(out.get("text", []))
                if any(t in text for t in leak_terms):
                    out["text"] = [SANITIZE_OUTPUT_PLACEHOLDER]
                    outputs_removed += 1
            elif otype in ("execute_result", "display_data"):
                data = out.get("data", {})
                if "text/plain" in data and any(
                    t in " ".join(data["text/plain"]) for t in leak_terms
                ):
                    data["text/plain"] = [SANITIZE_OUTPUT_PLACEHOLDER.strip()]
                    outputs_removed += 1
            elif otype == "error":
                tb = "\n".join(out.get("traceback", []))
                if any(t in tb for t in leak_terms):
                    out["traceback"] = [SANITIZE_OUTPUT_PLACEHOLDER.strip()]
                    outputs_removed += 1
        if lines_removed or outputs_removed:
            report[str(idx)] = {
                "action": "sanitized-code-cell",
                "lines_removed": lines_removed,
                "outputs_removed": outputs_removed,
            }
        kept.append(new)
    out = dict(nb)
    out["cells"] = kept
    return out, report


# ---------------------------------------------------------------------------
# Leak scanning
# ---------------------------------------------------------------------------


def iter_scan_text(path: Path) -> str | None:
    """Decode a file for leak scanning; None if binary/undecodable.

    Notebooks are scanned as *visible cell text* (sources + textual outputs),
    not raw JSON — base64-encoded image outputs would otherwise produce
    spurious hits on short terms like ABA/ABC.
    """
    data = path.read_bytes()
    if path.suffix == ".ipynb":
        try:
            nb = json.loads(data.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return None
        parts: list[str] = []
        for cell in nb.get("cells", []):
            parts.append("".join(cell.get("source", [])))
            for out in cell.get("outputs", []):
                otype = out.get("output_type")
                if otype == "stream":
                    parts.append("".join(out.get("text", [])))
                elif otype in ("execute_result", "display_data"):
                    if "text/plain" in out.get("data", {}):
                        parts.append(" ".join(out["data"]["text/plain"]))
                elif otype == "error":
                    parts.append("\n".join(out.get("traceback", [])))
        return "\n".join(parts)
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        pass
    try:
        return gzip.decompress(data).decode("utf-8", errors="strict")
    except (OSError, UnicodeDecodeError):
        return None


def scan_leaks(
    root: Path,
    terms: list[str],
    allowed_patterns: list[str] | None = None,
    allowed_in: list[str] | None = None,
) -> dict:
    """Scan every model-visible text file under root for configured leak terms.

    Fail-closed: any hit is returned in the report; callers raise LeakError.
    ``allowed_patterns`` (regexes) are masked out of files whose basename is
    in ``allowed_in`` before term matching (used for the brief's question
    line, the only legitimate ABA/ABC mention in final-analysis workspaces).
    """
    terms = [t for t in terms if t]
    allowed_patterns = allowed_patterns or []
    allowed_in = set(allowed_in or [])
    hits: list[dict] = []
    files_scanned = 0
    files_binary = 0
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        text = iter_scan_text(path)
        if text is None:
            files_binary += 1
            continue
        files_scanned += 1
        if path.name in allowed_in and allowed_patterns:
            for pat in allowed_patterns:
                text = re.sub(pat, "", text)
        for term in terms:
            idx = text.find(term)
            if idx == -1:
                continue
            contexts = []
            while idx != -1 and len(contexts) < 3:
                s = max(0, idx - 60)
                e = min(len(text), idx + len(term) + 60)
                contexts.append(" ".join(text[s:e].split()))
                idx = text.find(term, idx + 1)
            hits.append(
                {
                    "file": str(path.relative_to(root)),
                    "term": term,
                    "count": text.count(term),
                    "contexts": contexts,
                }
            )
    return {
        "status": "pass" if not hits else "FAIL",
        "terms": terms,
        "allowed_patterns": allowed_patterns,
        "allowed_in": sorted(allowed_in),
        "files_scanned": files_scanned,
        "files_skipped_binary": files_binary,
        "hits": hits,
    }


# ---------------------------------------------------------------------------
# Hashing
# ---------------------------------------------------------------------------


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def workspace_hash(root: Path) -> str:
    """Deterministic content hash: sorted (relpath, file sha256) pairs."""
    h = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        if path.is_file():
            rel = path.relative_to(root).as_posix()
            h.update(hashlib.sha256(rel.encode()).digest())
            h.update(bytes.fromhex(file_sha256(path)))
    return h.hexdigest()


# ---------------------------------------------------------------------------
# Source immutability guard
# ---------------------------------------------------------------------------


class SourceGuard:
    """Snapshot (size, mtime_ns) of files read from source; verify unchanged."""

    def __init__(self, root: Path):
        self.root = Path(root)
        self.snapshot: dict[str, tuple[int, int]] = {}

    def record(self, rel: str) -> None:
        p = self.root / rel
        if p.is_file():
            st = p.stat()
            self.snapshot[rel] = (st.st_size, st.st_mtime_ns)

    def verify(self) -> None:
        for rel, (size, mtime_ns) in self.snapshot.items():
            p = self.root / rel
            st = p.stat()
            if (st.st_size, st.st_mtime_ns) != (size, mtime_ns):
                raise VarianceError(
                    f"source file changed during materialization: {p} "
                    f"({(size, mtime_ns)} -> {(st.st_size, st.st_mtime_ns)})"
                )


# ---------------------------------------------------------------------------
# Materialization
# ---------------------------------------------------------------------------


def _copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def _copy_tree(src: Path, dst: Path) -> None:
    shutil.copytree(src, dst)


def sanitize_json_strings(value: Any, leak_terms: list[str]) -> tuple[Any, int]:
    """Replace leaking JSON string values without changing keys or numbers."""
    if isinstance(value, dict):
        cleaned: dict[Any, Any] = {}
        removed = 0
        for key, item in value.items():
            cleaned_item, count = sanitize_json_strings(item, leak_terms)
            cleaned[key] = cleaned_item
            removed += count
        return cleaned, removed
    if isinstance(value, list):
        cleaned_items = []
        removed = 0
        for item in value:
            cleaned_item, count = sanitize_json_strings(item, leak_terms)
            cleaned_items.append(cleaned_item)
            removed += count
        return cleaned_items, removed
    if isinstance(value, str) and any(term in value for term in leak_terms):
        return SANITIZE_JSON_PLACEHOLDER, 1
    return value, 0


def materialize(
    camp: dict,
    kind: str,
    cfg: dict,
    dest: Path,
) -> dict:
    """Build one leak-checked materialized workspace. Never writes to source."""
    src = Path(camp["source"])
    dest.mkdir(parents=True, exist_ok=True)
    if any(dest.iterdir()):
        raise VarianceError(f"materialization destination not empty: {dest}")
    guard = SourceGuard(src)
    manifest: dict[str, Any] = {
        "campaign": camp["id"],
        "experiment": kind,
        "source": str(src),
        "files": [],
        "excluded_present": [],
        "notebooks": {},
    }
    manifest_path = dest.parent / "materialization.json"

    # Explicitly included files (cards + brief)
    include_sanitize_report: dict[str, int] = {}
    for rel in cfg.get("include", []):
        s, d = src / rel, dest / rel
        if not s.is_file():
            raise VarianceError(f"{camp['id']}.{kind}: include names {rel} but it does not exist")
        guard.record(rel)
        _copy_file(s, d)
        manifest["files"].append(
            {"path": rel, "sha256": file_sha256(d), "bytes": d.stat().st_size}
        )
        # Line-level sanitization of included text files: verdict-carrying
        # lines are replaced (device cards are written to *after* the
        # session call; the brief's goal line is protected by
        # allowed_patterns).
        if d.suffix in (".md", ".txt") and cfg.get("leak_terms"):
            allowed = (
                cfg.get("allowed_patterns", [])
                if d.name in set(cfg.get("allowed_in", []))
                else []
            )
            lines = d.read_text(encoding="utf-8").splitlines(keepends=True)
            out, stripped = [], 0
            for line in lines:
                if any(t in line for t in cfg["leak_terms"]) and not any(
                    re.search(p, line) for p in allowed
                ):
                    out.append(SANITIZE_LINE_PLACEHOLDER + "\n")
                    stripped += 1
                else:
                    out.append(line)
            if stripped:
                d.write_text("".join(out), encoding="utf-8")
                include_sanitize_report[rel] = stripped
    if include_sanitize_report:
        manifest["include_sanitize_report"] = include_sanitize_report

    # Measurement notebook: crop (tool-call) or sanitize (final-analysis)
    mnb = cfg["measure_notebook"]
    guard.record(mnb)
    nb = load_nb(src / mnb)
    manifest["notebooks"]["measure"] = {
        "source": mnb,
        "cells_total": len(nb.get("cells", [])),
        "sha256_source": file_sha256(src / mnb),
    }
    if cfg.get("sanitize"):
        nb_s, report = sanitize_nb(nb, cfg.get("leak_terms", []))
        manifest["notebooks"]["measure"]["mode"] = "sanitize"
        manifest["notebooks"]["measure"]["sanitize_report"] = report
    else:
        cut = cfg["cut_index"]
        nb_s, report = crop_nb(nb, cut), None
        manifest["notebooks"]["measure"]["mode"] = "crop"
        manifest["notebooks"]["measure"]["cut_index"] = cut
    manifest["notebooks"]["measure"]["cells_kept"] = len(nb_s.get("cells", []))
    (dest / mnb).write_text(dump_nb(nb_s), encoding="utf-8")

    # Analysis notebook (optional for tool-call; required for final-analysis)
    anb = cfg.get("analysis_notebook")
    if anb:
        guard.record(anb)
        a = load_nb(src / anb)
        manifest["notebooks"]["analysis"] = {
            "source": anb,
            "cells_total": len(a.get("cells", [])),
            "sha256_source": file_sha256(src / anb),
        }
        if cfg.get("sanitize"):
            a_s, arep = sanitize_nb(a, cfg.get("leak_terms", []))
            manifest["notebooks"]["analysis"]["mode"] = "sanitize"
            manifest["notebooks"]["analysis"]["sanitize_report"] = arep
        else:
            cut = cfg.get("analysis_cut_index")
            if cut is None:
                raise VarianceError(
                    f"{camp['id']}.{kind}: analysis_notebook declared but "
                    "analysis_cut_index missing (tool-call)"
                )
            a_s, arep = crop_nb(a, cut), None
            manifest["notebooks"]["analysis"]["mode"] = "crop"
            manifest["notebooks"]["analysis"]["cut_index"] = cut
        manifest["notebooks"]["analysis"]["cells_kept"] = len(a_s.get("cells", []))
        (dest / anb).write_text(dump_nb(a_s), encoding="utf-8")

    # Data runs (allowlist only). Final-analysis metadata can contain
    # post-hoc human comments written after the verdict; sanitize only copied
    # JSON string values while preserving numeric acquisition metadata.
    (dest / "data").mkdir(exist_ok=True)
    data_sanitize_report: dict[str, int] = {}
    for did in cfg.get("data_runs", []):
        rel = f"data/{did}"
        s = src / rel
        if not s.is_dir():
            raise VarianceError(
                f"{camp['id']}.{kind}: data_runs names {rel} but it does not exist"
            )
        _copy_tree(s, dest / rel)
        if cfg.get("sanitize") and cfg.get("leak_terms"):
            for metadata_path in sorted((dest / rel).rglob("metadata.json")):
                try:
                    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    continue  # fail-closed text leak scan below remains authoritative
                cleaned, removed = sanitize_json_strings(
                    metadata, cfg.get("leak_terms", [])
                )
                if removed:
                    metadata_path.write_text(
                        json.dumps(cleaned, indent=2) + "\n", encoding="utf-8"
                    )
                    data_sanitize_report[
                        metadata_path.relative_to(dest).as_posix()
                    ] = removed
    if data_sanitize_report:
        manifest["data_sanitize_report"] = data_sanitize_report

    # Record explicitly excluded artifacts that exist at source (visibility)
    for rel in ALWAYS_EXCLUDED:
        if (src / rel).exists():
            manifest["excluded_present"].append(rel)

    # Leak scan over everything model-visible — fail closed on any hit
    scan = scan_leaks(
        dest,
        terms=cfg.get("leak_terms", []),
        allowed_patterns=cfg.get("allowed_patterns", []),
        allowed_in=cfg.get("allowed_in", []),
    )
    manifest["leak_scan"] = scan
    for f in sorted(dest.rglob("*")):
        if f.is_file():
            rel = f.relative_to(dest).as_posix()
            manifest["files"].append(
                {"path": rel, "sha256": file_sha256(f), "bytes": f.stat().st_size}
            )
    manifest["workspace_sha256"] = workspace_hash(dest)
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    guard.verify()
    if scan["hits"]:
        (dest.parent / "LEAK-SCAN-FAILED.txt").write_text(
            json.dumps(scan, indent=2), encoding="utf-8"
        )
        raise LeakError(
            f"{camp['id']}.{kind}: leak scan found {len(scan['hits'])} hit(s) — "
            f"see {dest.parent / 'LEAK-SCAN-FAILED.txt'}"
        )
    return manifest


# ---------------------------------------------------------------------------
# Harness
# ---------------------------------------------------------------------------


@dataclass
class HarnessResult:
    raw_stdout: str = ""
    stderr: str = ""
    returncode: int = -1
    duration_s: float = 0.0
    model_resolved: str | None = None
    usage: dict | None = None
    total_cost_usd: float | None = None
    session_id: str | None = None
    error: str | None = None


def _result_obj(parsed: Any) -> dict:
    if isinstance(parsed, dict):
        return parsed
    if isinstance(parsed, list):
        for item in reversed(parsed):
            if isinstance(item, dict) and item.get("type") == "result":
                return item
        for item in reversed(parsed):
            if isinstance(item, dict):
                return item
    return {}


class ClaudePHarness:
    """Fresh `claude -p` session per call (current HERA replay harness)."""

    kind = "claude-p"

    def __init__(self, model: str | None = None, timeout_s: int = 1800,
                 allowed_tools: tuple[str, ...] = ("Read", "Glob", "Grep")):
        self.model = model
        self.timeout_s = timeout_s
        self.allowed_tools = allowed_tools

    def build_cmd(self, prompt: str, workdir: Path) -> list[str]:
        cmd = ["claude", "-p", prompt, "--add-dir", str(workdir),
               "--output-format", "json"]
        for tool in self.allowed_tools:
            cmd += ["--allowedTools", tool]
        if self.model:
            cmd += ["--model", self.model]
        return cmd

    def run(self, prompt: str, workdir: Path) -> HarnessResult:
        cmd = self.build_cmd(prompt, workdir)
        t0 = time.monotonic()
        try:
            res = subprocess.run(
                cmd, cwd=workdir, capture_output=True, text=True,
                timeout=self.timeout_s,
            )
        except subprocess.TimeoutExpired:
            return HarnessResult(
                stderr=f"claude -p timed out after {self.timeout_s}s",
                error="timeout",
                duration_s=time.monotonic() - t0,
            )
        result = HarnessResult(
            raw_stdout=res.stdout,
            stderr=res.stderr,
            returncode=res.returncode,
            duration_s=time.monotonic() - t0,
        )
        try:
            data = _result_obj(json.loads(res.stdout))
        except json.JSONDecodeError as exc:
            if res.returncode != 0:
                detail = res.stderr.strip() or f"stdout is not JSON: {exc}"
                result.error = f"claude -p exited {res.returncode}: {detail[:400]}"
            else:
                result.error = f"claude -p stdout is not JSON: {exc}"
            return result
        result.model_resolved = data.get("model")
        if not result.model_resolved:
            mu = data.get("modelUsage")
            if isinstance(mu, dict) and mu:
                result.model_resolved = ",".join(mu.keys())
        result.usage = data.get("usage")
        result.total_cost_usd = data.get("total_cost_usd")
        result.session_id = data.get("session_id")
        if res.returncode != 0 or data.get("is_error"):
            detail = str(data.get("result") or res.stderr.strip() or "unknown error")
            result.error = (
                f"claude -p exited {res.returncode}; "
                f"api_error_status={data.get('api_error_status')}: {detail[:400]}"
            )
        return result


class FakeHarness:
    """Scripted harness for tests. Pops (stdout, stderr, rc) from a queue."""

    kind = "fake"

    def __init__(self, script: list[tuple[str, str, int]]):
        self.script = list(script)
        self.calls: list[str] = []

    def run(self, prompt: str, workdir: Path) -> HarnessResult:
        self.calls.append(prompt)
        if not self.script:
            return HarnessResult(
                stderr="fake harness queue exhausted", error="queue exhausted"
            )
        stdout, stderr, rc = self.script.pop(0)
        return HarnessResult(
            raw_stdout=stdout, stderr=stderr, returncode=rc,
            duration_s=0.01, model_resolved="fake-model-1",
            error=(f"fake harness exited {rc}: {stderr}" if rc != 0 else None),
        )


def build_harness(
    harness_cfg: dict,
    model_override: str | None,
    timeout_override: int | None,
    kind_override: str | None = None,
    thinking_override: str | None = None,
) -> Any:
    kind = kind_override or harness_cfg.get("kind", "claude-p")
    if kind == "fake":
        script = []
        for item in harness_cfg.get("script", []):
            script.append((item.get("stdout", ""), item.get("stderr", ""),
                           item.get("rc", 0)))
        return FakeHarness(script)
    timeout = timeout_override or int(harness_cfg.get("timeout_s", 1800))
    model = model_override or harness_cfg.get("model") or None
    if kind != "claude-p":
        raise VarianceError(f"unsupported harness kind: {kind!r}")
    return ClaudePHarness(model=model, timeout_s=timeout)


# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------

TOOL_CALL_PROMPT_TEMPLATE = """\
# HERA offline replay — next-measurement decision (tool-call variance experiment)

You are the HERA tactical agent replaying a measurement session on the Sharpe
Lab VTI cryostat, at a frozen frontier. This is an **offline replay**: the
workspace is a read-only snapshot of everything the session knew so far.
There is no live kernel, no live notebook, no instrument access — do not
propose nb-collab cells and do not attempt to execute anything. Your job is
judgment, not actions.

## Campaign brief
Read `hera_session.md` and `device_card.md`; if `rig_card.md` is present,
read it too. Campaign goal:
determine the stacking order of QC0426 (ABA Bernal vs ABC rhombohedral),
evidence-cited and region-resolved.

## Where you are
- `{measure_nb}` — measurement notebook, cropped to exactly what has run so
  far (cells + outputs preserved). Notebook outputs can be large: use
  targeted reads, not whole-file dumps.
- `{ana_note}`
- `data/<id>/` — every landed sweep (`metadata.json` + TSV + `plot.png`).

## Task
Decide the single best **next measurement**. Give the concrete sweep call you
would land next, in the `s.<call>(...)` form used by this rig (the API is
shown by the sweep cells already in the measurement notebook), with explicit
axes/ranges/point counts, delays/dwell, remaining keyword arguments, and a
concise rationale tied to the campaign goal and to what the data so far does
or does not yet show.

## Output (machine-readable — exactly one JSON object, nothing else after it)

```json
{{
  "callable": "s.megasweep",
  "axes": [{{"name": "mag.field", "start": 8.0, "stop": 0.77, "points": 141}}],
  "delays": {{"fast": 0.05, "slow": 1.2}},
  "kwargs": {{}},
  "rationale": "..."
}}
```
"""

FINAL_ANALYSIS_PROMPT_TEMPLATE = """\
# HERA offline replay — fresh final analysis (variance experiment)

You are an expert condensed-matter analyst in a **fresh session**. A completed
measurement campaign on trilayer graphene device QC0426 sits in the workspace.
Your job: independently determine the stacking order from the data and return
a verdict. No prior session's reasoning or conclusion is available to you —
work it out from the workspace yourself.

## Campaign brief
Read `hera_session.md` and `device_card.md`; if `rig_card.md` is present,
read it too. Campaign goal: determine the stacking order of QC0426:
ABA (Bernal) vs ABC (rhombohedral), evidence-cited and region-resolved.

## Workspace (all read-only)
- `{measure_nb}` — every measurement cell that ran, code + non-verdict outputs
  (narrative/session-history cells and any verdict text have been removed by
  the experiment materializer).
- `{ana_nb}` — analysis cells, code + numeric/image outputs (verdict text
  removed).
- `data/<id>/` — every sweep's raw TSV (`metadata.json` + `plot.png`).

Notebook outputs can be large: use targeted reads, not whole-file dumps. You
have Read/Glob/Grep only (no execution) — analyze from the visible artifacts,
which retain the numeric analysis results produced during the campaign.

## Output (machine-readable — exactly one JSON object, nothing else after it)

```json
{{
  "verdict": "ABA",
  "confidence": "HIGH",
  "evidence": ["one concise evidence point", "another"],
  "summary": "one or two sentences"
}}
```

`verdict` must be one of "ABA", "ABC", "UNDERDETERMINED"; `confidence` one of
"LOW", "MEDIUM", "HIGH" (optional). `evidence` is a short list of the
strongest data/analysis points behind the verdict.
"""


def build_prompt(kind: str, cfg: dict, camp: dict) -> str:
    ana_note = ""
    if cfg.get("analysis_notebook"):
        ana_note = (
            f"- `{cfg['analysis_notebook']}` — analysis notebook so far "
            "(cells + outputs preserved; targeted reads).\n"
        )
    if kind == "tool-call":
        return TOOL_CALL_PROMPT_TEMPLATE.format(
            measure_nb=cfg["measure_notebook"], ana_note=ana_note
        )
    if cfg.get("analysis_task"):
        support = list(cfg.get("verdict_support", VERDICTS))
        example = support[0]
        return f"""# HERA offline replay — fresh final analysis (variance experiment)

You are an expert condensed-matter analyst in a **fresh session**. Independently
answer the scientific task below from the model-visible workspace. No prior
session reasoning or conclusion is available; derive every claim from evidence.

## Scientific task
{cfg['analysis_task']}

## Workspace (all read-only)
- `{cfg['measure_notebook']}` — executed measurement code and non-verdict outputs.
- `{cfg.get('analysis_notebook', '')}` — analysis code plus numeric/image outputs.
- `data/<id>/` — raw sweep artifacts.
- Read `hera_session.md`, `device_card.md`, `rig_card.md`, and any supplied
  commit-pinned procedural context.

Use targeted Read/Glob/Grep calls; do not attempt execution. Return atomic,
evidence-cited claims suitable for blinded expert grading.

## Output (exactly one JSON object, nothing else after it)

```json
{{
  "verdict": "{example}",
  "confidence": "HIGH",
  "claims": [
    {{"claim": "one independently gradable scientific claim", "evidence": ["data/run or notebook reference"]}}
  ],
  "summary": "one or two sentences"
}}
```

`verdict` must be one of {json.dumps(support)}. `confidence` is optional and
must be LOW, MEDIUM, or HIGH. Keep claims atomic: one factual assertion each.
"""
    return FINAL_ANALYSIS_PROMPT_TEMPLATE.format(
        measure_nb=cfg["measure_notebook"],
        ana_nb=cfg.get("analysis_notebook", ""),
    )


# ---------------------------------------------------------------------------
# Parsers (never execute model output)
# ---------------------------------------------------------------------------


_TUPLE_RE = re.compile(r"\(([^()\"']+)\)")


def _normalize_py_tuples(text: str) -> str:
    """Conservative fix for models emitting Python tuple syntax in JSON
    (e.g. [(-1.5, -4.3), ...]). Only ever applied as a fallback when strict
    parsing failed; nothing is executed."""
    out = text
    for _ in range(8):
        new = _TUPLE_RE.sub(r"[\1]", out)
        if new == out:
            break
        out = new
    return out


def _close_unbalanced_json(text: str) -> str:
    """Append only missing closing delimiters to a model's JSON fragment."""
    stack: list[str] = []
    in_str = False
    esc = False
    pairs = {"{": "}", "[": "]"}
    for char in text:
        if in_str:
            if esc:
                esc = False
            elif char == "\\":
                esc = True
            elif char == '"':
                in_str = False
            continue
        if char == '"':
            in_str = True
        elif char in pairs:
            stack.append(pairs[char])
        elif char in ("}", "]"):
            if not stack or stack[-1] != char:
                return text
            stack.pop()
    if in_str:
        return text
    return text + "".join(reversed(stack))


def _load_model_json(text: str) -> tuple[Any, str | None] | None:
    """Parse strict JSON, then conservative syntax-only repairs."""
    try:
        return json.loads(text), None
    except json.JSONDecodeError:
        pass

    closed = _close_unbalanced_json(text)
    if closed != text:
        try:
            return json.loads(closed), "missing closing JSON delimiters appended"
        except json.JSONDecodeError:
            pass

    tuples = _normalize_py_tuples(text)
    if tuples != text:
        try:
            return json.loads(tuples), "python tuple syntax normalized to JSON lists"
        except json.JSONDecodeError:
            closed_tuples = _close_unbalanced_json(tuples)
            if closed_tuples != tuples:
                try:
                    return (
                        json.loads(closed_tuples),
                        "python tuple syntax normalized and missing closing JSON "
                        "delimiters appended",
                    )
                except json.JSONDecodeError:
                    pass
    return None


def _extract_json_objects(text: str) -> list[tuple[Any, str | None]]:
    """Parse fenced JSON blocks, then balanced object spans.

    Each result carries an optional conservative-repair note. No model text is
    executed.
    """
    found: list[tuple[Any, str | None]] = []
    for m in re.finditer(r"```(?:json)?\s*(.*?)```", text, re.S):
        loaded = _load_model_json(m.group(1))
        if loaded is not None:
            found.append(loaded)
    i = 0
    while i < len(text):
        start = text.find("{", i)
        if start == -1:
            break
        depth = 0
        in_str = False
        esc = False
        for j in range(start, len(text)):
            ch = text[j]
            if in_str:
                if esc:
                    esc = False
                elif ch == "\\":
                    esc = True
                elif ch == '"':
                    in_str = False
                continue
            if ch == '"':
                in_str = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    span = text[start : j + 1]
                    loaded = _load_model_json(span)
                    if loaded is not None:
                        found.append(loaded)
                    i = j + 1
                    break
        else:
            break
        continue
    return found


def parse_tool_call(text: str) -> tuple[dict | None, str | None]:
    """Strict envelope first; conservative fallback: single `s.<call>(...)`."""
    for obj, repair_note in _extract_json_objects(text):
        if isinstance(obj, dict) and "callable" in obj:
            parsed = dict(obj)
            parsed["parse_mode"] = "envelope"
            if repair_note:
                parsed["parse_note"] = repair_note
            if not isinstance(parsed.get("callable"), str):
                return None, "envelope 'callable' is not a string"
            return parsed, None
    m = re.search(r"\bs\.([A-Za-z_]\w*)\((.*)\)", text, re.S)
    if m:
        name, args = m.group(1), m.group(2)
        kwargs: dict[str, Any] = {}
        positionals: list[str] = []
        for part in _split_top_level(args):
            part = part.strip()
            if not part:
                continue
            if "=" in part:
                k, _, v = part.partition("=")
                k, v = k.strip(), v.strip()
                try:
                    val: Any = json.loads(v)
                except json.JSONDecodeError:
                    try:
                        val = float(v)
                    except ValueError:
                        val = v.strip("'\"")
                kwargs[k] = val
            else:
                positionals.append(part)
        parsed = {
            "callable": f"s.{name}",
            "axes": [],
            "delays": {},
            "kwargs": kwargs,
            "positionals": positionals,
            "rationale": None,
            "parse_mode": "fallback-single-call",
            "parse_note": "single Python s.<call>(...) expression; arguments "
                          "captured verbatim, axes not extracted",
        }
        return parsed, None
    return None, "no JSON envelope with 'callable' and no single s.<call>(...) expression found"


def parse_verdict(
    text: str, verdict_support: list[str] | tuple[str, ...] = VERDICTS
) -> tuple[dict | None, str | None]:
    support = tuple(verdict_support)
    for obj, repair_note in _extract_json_objects(text):
        if isinstance(obj, dict) and obj.get("verdict") in support:
            parsed = dict(obj)
            parsed["parse_mode"] = "envelope"
            if repair_note:
                parsed["parse_note"] = repair_note
            conf = parsed.get("confidence")
            if conf is not None and conf not in CONFIDENCES:
                return None, f"envelope confidence {conf!r} not in {CONFIDENCES}"
            return parsed, None
    distinct: set[str] = set()
    for value in support:
        escaped = re.escape(value)
        if re.search(
            rf"verdict[^A-Za-z]{{0,10}}{escaped}\b|"
            rf"\b{escaped}\b(?=[^\n]*(?:verdict|conclusion))",
            text,
        ):
            distinct.add(value)
    if len(distinct) == 1:
        return {"verdict": distinct.pop(), "parse_mode": "fallback-text"}, None
    if len(distinct) > 1:
        return None, f"ambiguous verdict mentions in fallback: {sorted(distinct)}"
    return None, "no verdict envelope and no unambiguous verdict mention found"


def _split_top_level(s: str) -> list[str]:
    parts, depth, in_str, esc, start = [], 0, False, False, 0
    for i, ch in enumerate(s):
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        elif ch == "," and depth == 0:
            parts.append(s[start:i])
            start = i + 1
    parts.append(s[start:])
    return parts


# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------


def categorical_stats(values: list[Any], support: list[str] | None = None) -> dict:
    counts = Counter(str(v) for v in values)
    n = sum(counts.values())
    k_observed = len(counts)
    # Declared support: normalized entropy and smoothing use the full
    # category support (e.g. ABA/ABC/UNDERDETERMINED), not only observed
    # bins — a verdict set missing a category must not look "certain".
    k = len(support) if support is not None else k_observed
    h = 0.0
    if n:
        h = -sum((c / n) * math.log(c / n) for c in counts.values() if c)
    h_norm = h / math.log(k) if k > 1 else 0.0
    return {
        "counts": dict(sorted(counts.items())),
        "n": n,
        "k": k,
        "k_observed": k_observed,
        "entropy_nats": h,
        "entropy_normalized": h_norm,
    }


def numeric_stats(values: list[float]) -> dict:
    vals = sorted(float(v) for v in values)
    n = len(vals)
    if n == 0:
        return {"n": 0}
    mean = sum(vals) / n
    var = sum((v - mean) ** 2 for v in vals) / (n - 1) if n > 1 else None
    mid = n // 2
    median = vals[mid] if n % 2 else (vals[mid - 1] + vals[mid]) / 2

    def q(p: float) -> float:
        idx = p * (n - 1)
        lo = int(math.floor(idx))
        hi = int(math.ceil(idx))
        if lo == hi:
            return vals[lo]
        return vals[lo] + (vals[hi] - vals[lo]) * (idx - lo)

    q25, q75 = q(0.25), q(0.75)
    return {
        "n": n,
        "values": vals,
        "mean": mean,
        "variance_ddof1": var,
        "median": median,
        "q25": q25,
        "q75": q75,
        "iqr": q75 - q25,
        "min": vals[0],
        "max": vals[-1],
    }


def truth_metrics(counts: dict, truth: str, alpha: float = NLL_ALPHA,
                  support: list[str] | None = None) -> dict:
    n = sum(counts.values())
    k_observed = len(counts)
    k = len(support) if support is not None else k_observed
    n_truth = counts.get(truth, 0)
    if n == 0:
        return {"n": 0, "k": k, "k_observed": k_observed,
                "ground_truth": truth, "alpha": alpha}
    p = n_truth / n
    p_smooth = (n_truth + alpha) / (n + alpha * k)
    return {
        "n": n,
        "k": k,
        "k_observed": k_observed,
        "ground_truth": truth,
        "n_truth": n_truth,
        "p_truth": p,
        "p_truth_jeffreys": p_smooth,
        "nll_unsmoothed": -math.log(p) if p > 0 else float("inf"),
        "nll_jeffreys_alpha_0_5": -math.log(p_smooth),
        "alpha": alpha,
    }


def _jsonable(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {str(k): _jsonable(v) for k, v in sorted(obj.items(), key=lambda kv: str(kv[0]))}
    if isinstance(obj, (list, tuple)):
        return [_jsonable(v) for v in obj]
    if isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj
    return str(obj)


def normalize_callable(value: Any) -> str:
    """Canonicalize model spelling without conflating different functions."""
    raw = str(value).strip()
    match = re.match(r"^(?:s\.)?([A-Za-z_]\w*)", raw)
    return f"s.{match.group(1)}" if match else raw


def _flatten_tool_axes(value: Any) -> list[dict]:
    """Return axis dictionaries from flat or nested model-emitted axis groups."""
    if isinstance(value, dict):
        return [value]
    if isinstance(value, (list, tuple)):
        return [axis for item in value for axis in _flatten_tool_axes(item)]
    return []


def _tool_delays(parsed: dict) -> dict[str, Any]:
    value = parsed.get("delays", {})
    if isinstance(value, dict):
        return {str(k): v for k, v in value.items()}
    if isinstance(value, (int, float)) and math.isfinite(float(value)):
        return {"delay": float(value)}
    return {}


def canonical_tool_signature(parsed: dict) -> dict:
    axes = []
    for a in _flatten_tool_axes(parsed.get("axes", [])):
        entry = {"name": a.get("name")}
        for key in ("start", "stop", "points"):
            v = a.get(key)
            try:
                entry[key] = float(v) if key in ("start", "stop") else int(v)
            except (TypeError, ValueError):
                entry[key] = v
        axes.append(entry)
    axes.sort(key=lambda a: str(a.get("name")))
    delays = {
        str(k): v for k, v in sorted(_tool_delays(parsed).items(), key=lambda kv: str(kv[0]))
    }
    kwargs = parsed.get("kwargs", {})
    if not isinstance(kwargs, dict):
        kwargs = {}
    return {
        "callable": normalize_callable(parsed.get("callable")),
        "axes": axes,
        "delays": delays,
        "kwargs": _jsonable(kwargs),
    }


def tool_call_metrics(records: list[dict]) -> dict:
    """Categorical entropy + numeric spread + joint-signature entropy."""
    callables = [normalize_callable(r["parsed"].get("callable")) for r in records]
    axes_sigs = [
        ",".join(sorted(str(a.get("name"))
                        for a in _flatten_tool_axes(r["parsed"].get("axes", []))))
        for r in records
    ]
    delay_keys = [
        ",".join(sorted(_tool_delays(r["parsed"])))
        for r in records
    ]
    sigs = [json.dumps(canonical_tool_signature(r["parsed"]), sort_keys=True)
            for r in records]
    metrics: dict[str, Any] = {
        "callable": categorical_stats(callables),
        "axes_names_signature": categorical_stats(axes_sigs),
        "delay_keys_signature": categorical_stats(delay_keys),
        "joint_call_signature": categorical_stats(sigs),
        "joint_signatures": [
            {"sample": r["sample"], "signature": canonical_tool_signature(r["parsed"])}
            for r in records
        ],
        "numeric": {},
    }
    # Numeric spreads per axis name and per delay key
    axes_by_name: dict[str, list[dict]] = {}
    for r in records:
        for a in _flatten_tool_axes(r["parsed"].get("axes", [])):
            if a.get("name") is not None:
                axes_by_name.setdefault(str(a["name"]), []).append(a)
    for name, axs in axes_by_name.items():
        entry: dict[str, Any] = {}
        for key in ("start", "stop", "points"):
            vals = []
            for a in axs:
                v = a.get(key)
                try:
                    vals.append(float(v))
                except (TypeError, ValueError):
                    pass
            entry[key] = numeric_stats(vals)
        spans, densities = [], []
        for a in axs:
            try:
                start, stop = float(a["start"]), float(a["stop"])
                points = float(a["points"])
                spans.append(stop - start)
                if stop != start:
                    densities.append(points / abs(stop - start))
            except (TypeError, ValueError, KeyError):
                pass
        entry["span"] = numeric_stats(spans)
        entry["points_per_unit"] = numeric_stats(densities)
        metrics["numeric"][f"axis:{name}"] = entry
    delays_by_key: dict[str, list[float]] = {}
    for r in records:
        for k, v in _tool_delays(r["parsed"]).items():
            try:
                delays_by_key.setdefault(str(k), []).append(float(v))
            except (TypeError, ValueError):
                pass
    for k, vals in delays_by_key.items():
        metrics["numeric"][f"delay:{k}"] = numeric_stats(vals)
    return metrics


def verdict_metrics(
    records: list[dict], ground_truth: str | None,
    verdict_support: list[str] | tuple[str, ...] = VERDICTS,
) -> dict:
    support = list(verdict_support)
    verdicts = [r["parsed"].get("verdict") for r in records]
    confs = [r["parsed"].get("confidence") for r in records if r["parsed"].get("confidence")]
    counts = Counter(str(v) for v in verdicts)
    metrics: dict[str, Any] = {
        "verdict": categorical_stats(verdicts, support=support),
    }
    if confs:
        metrics["confidence"] = categorical_stats(confs)
    if ground_truth:
        metrics["ground_truth"] = truth_metrics(
            dict(counts), ground_truth, support=support
        )
    metrics["verdicts_by_sample"] = [
        {"sample": r["sample"], "verdict": r["parsed"].get("verdict")} for r in records
    ]
    return metrics


# ---------------------------------------------------------------------------
# Sample execution
# ---------------------------------------------------------------------------


def _sample_dir(out_root: Path, camp_id: str, kind: str, i: int) -> Path:
    return out_root / "samples" / camp_id / kind / f"sample-{i:02d}"


def _load_sample(sample_json: Path) -> dict | None:
    try:
        return json.loads(sample_json.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _pid_is_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def _claim_sample_lease(lease_path: Path) -> str | None:
    """Atomically claim a sample, reclaiming only a dead same-host owner."""
    token = f"{os.getpid()}-{time.time_ns()}"
    payload = json.dumps(
        {
            "pid": os.getpid(),
            "host": socket.gethostname(),
            "token": token,
            "claimed_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        },
        indent=2,
    ).encode()
    for attempt in range(2):
        try:
            fd = os.open(lease_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError:
            if attempt:
                return None
            try:
                current = json.loads(lease_path.read_text(encoding="utf-8"))
                same_host = current.get("host") == socket.gethostname()
                owner_pid = int(current.get("pid", -1))
            except (OSError, ValueError, TypeError, json.JSONDecodeError):
                return None
            if not same_host or _pid_is_alive(owner_pid):
                return None
            try:
                lease_path.unlink()
            except FileNotFoundError:
                pass
            continue
        try:
            os.write(fd, payload)
        finally:
            os.close(fd)
        return token
    return None


def _release_sample_lease(lease_path: Path, token: str) -> None:
    """Release only the lease claimed by this caller."""
    try:
        current = json.loads(lease_path.read_text(encoding="utf-8"))
        if current.get("token") == token:
            lease_path.unlink()
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        pass


def _run_one_sample(task: dict) -> dict:
    """One sample: atomically claim, copy workspace, and invoke harness."""
    out_root = task["out_root"]
    camp_id, kind = task["camp_id"], task["kind"]
    dest = _sample_dir(out_root, camp_id, kind, task["sample"])
    dest.mkdir(parents=True, exist_ok=True)
    sample_json = dest / "sample.json"

    if not task["force"]:
        prev = _load_sample(sample_json)
        if prev and prev.get("status") in ("ok", "unparseable"):
            prev["reused"] = True
            prev["reused_from"] = str(sample_json)
            tmp = dest / "sample.json.tmp"
            tmp.write_text(json.dumps(prev, indent=2), encoding="utf-8")
            tmp.replace(sample_json)
            return prev

    lease_path = dest / "sample.lock"
    lease_token = _claim_sample_lease(lease_path)
    if lease_token is None:
        return {
            "campaign": camp_id,
            "experiment": kind,
            "sample": task["sample"],
            "status": "busy",
            "error": f"sample lease is held: {lease_path}",
        }
    try:
        return _run_claimed_sample(task, dest, sample_json)
    finally:
        _release_sample_lease(lease_path, lease_token)


def _run_claimed_sample(task: dict, dest: Path, sample_json: Path) -> dict:
    """Execute an already-leased sample attempt."""
    harness = task["harness"]
    camp_id, kind = task["camp_id"], task["kind"]
    ws = dest / "workspace"
    if ws.exists():
        shutil.rmtree(ws)
    shutil.copytree(task["template"], ws)

    ws_hash = workspace_hash(ws)
    if ws_hash != task["template_hash"]:
        return {
            "campaign": camp_id, "experiment": kind, "sample": task["sample"],
            "status": "error",
            "error": f"sample workspace hash {ws_hash[:16]}… != template "
                     f"{task['template_hash'][:16]}… (visible state not byte-identical)",
        }

    prompt = task["prompt"]
    (dest / "prompt.md").write_text(prompt, encoding="utf-8")
    record = {
        "campaign": camp_id,
        "experiment": kind,
        "sample": task["sample"],
        "status": "ok",
        "model_requested": task.get("model_requested"),
        "sampling_controls": task.get("sampling_controls"),
        "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
        "workspace_hash": ws_hash,
        "workspace": str(ws),
        "harness_kind": getattr(harness, "kind", "unknown"),
        "harness_command": task.get("harness_command"),
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    }

    result = harness.run(prompt, ws)
    (dest / "raw.txt").write_text(result.raw_stdout, encoding="utf-8")
    if result.stderr:
        (dest / "stderr.txt").write_text(result.stderr, encoding="utf-8")
    record.update(
        {
            "duration_s": round(result.duration_s, 3),
            "returncode": result.returncode,
            "model_resolved": result.model_resolved,
            "usage": result.usage,
            "total_cost_usd": result.total_cost_usd,
            "session_id": result.session_id,
            "raw_file": "raw.txt",
            "stderr_file": "stderr.txt" if result.stderr else None,
        }
    )

    if result.error:
        record["status"] = "error"
        record["error"] = result.error
    else:
        output_text = getattr(result, "output_text", None)
        if output_text is None:
            output_text = result.raw_stdout
            try:
                data = _result_obj(json.loads(result.raw_stdout))
                output_text = data.get("result", result.raw_stdout)
            except json.JSONDecodeError:
                pass
        (dest / "output.md").write_text(output_text, encoding="utf-8")
        record["output_file"] = "output.md"

        if kind == "tool-call":
            parsed, err = parse_tool_call(output_text)
        else:
            parsed, err = parse_verdict(
                output_text, task.get("verdict_support", VERDICTS)
            )
        record["parsed"] = parsed
        record["parse_error"] = err
        if parsed is None:
            record["status"] = "unparseable"

    record["sample_json"] = str(sample_json)
    tmp = dest / "sample.json.tmp"
    tmp.write_text(json.dumps(record, indent=2), encoding="utf-8")
    tmp.replace(sample_json)
    return record


def run_experiments(
    manifest: dict,
    out_root: Path,
    *,
    samples_override: int | None = None,
    model_override: str | None = None,
    timeout_override: int | None = None,
    harness_override: str | None = None,
    thinking_override: str | None = None,
    max_parallel: int = 1,
    force: bool = False,
    campaigns: list[str] | None = None,
    experiments: list[str] | None = None,
    max_tasks: int | None = None,
) -> int:
    out_root.mkdir(parents=True, exist_ok=True)
    harness_cfg = manifest["harness"]
    harness = build_harness(
        harness_cfg,
        model_override,
        timeout_override,
        kind_override=harness_override,
        thinking_override=thinking_override,
    )
    actual_kind = harness_override or harness_cfg.get("kind", "claude-p")
    sampling_controls = harness_cfg.get("sampling_controls") or {
        "temperature": "not exposed by harness",
        "note": "claude -p does not expose temperature/top_p/top_k; each "
                "invocation is a fresh session",
    }
    resolved = {
        "experiment_id": manifest["experiment_id"],
        "harness": {
            "kind": actual_kind,
            "model_requested": model_override or harness_cfg.get("model"),
            "sampling_controls": sampling_controls,
        },
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    }
    (out_root / "experiment.json").write_text(
        json.dumps(resolved, indent=2), encoding="utf-8"
    )

    # Materialize one immutable template per (campaign, experiment)
    templates: dict[tuple[str, str], Path] = {}
    for camp in manifest["campaigns"]:
        if campaigns and camp["id"] not in campaigns:
            continue
        for kind, cfg_raw in camp["experiments"].items():
            if experiments and kind not in experiments:
                continue
            cfg = experiment_defaults(cfg_raw)
            tpl = out_root / "materializations" / camp["id"] / kind / "workspace"
            mj = tpl.parent / "materialization.json"
            if force and tpl.exists():
                shutil.rmtree(tpl)
            if mj.exists() and tpl.is_dir():
                print(f"reusing materialization {camp['id']}/{kind} "
                      f"({mj})")
            else:
                print(f"materializing {camp['id']}/{kind} -> {tpl}")
                materialize(camp, kind, cfg, tpl)
            templates[(camp["id"], kind)] = tpl

    # Build tasks
    tasks: list[dict] = []
    for (camp_id, kind), tpl in templates.items():
        camp = next(c for c in manifest["campaigns"] if c["id"] == camp_id)
        cfg = experiment_defaults(camp["experiments"][kind])
        n = samples_override or int(cfg.get("samples", 5))
        prompt = build_prompt(kind, cfg, camp)
        for i in range(1, n + 1):
            tasks.append(
                {
                    "harness": harness,
                    "out_root": out_root,
                    "camp_id": camp_id,
                    "kind": kind,
                    "sample": i,
                    "template": tpl,
                    "template_hash": json.loads(
                        (tpl.parent / "materialization.json").read_text()
                    )["workspace_sha256"],
                    "prompt": prompt,
                    "model_requested": model_override or harness_cfg.get("model"),
                    "sampling_controls": sampling_controls,
                    "verdict_support": cfg.get("verdict_support", list(VERDICTS)),
                    "force": force,
                    "harness_command": (
                        " ".join(harness.build_cmd("<prompt>", Path("<workspace>")))
                        if hasattr(harness, "build_cmd") else "fake"
                    ),
                }
            )

    if max_tasks is not None:
        if max_tasks < 1:
            raise VarianceError("max_tasks must be at least 1")
        pending: list[dict] = []
        for task in tasks:
            sample_dir = _sample_dir(
                out_root, task["camp_id"], task["kind"], task["sample"]
            )
            previous = _load_sample(sample_dir / "sample.json")
            retained = previous and previous.get("status") in ("ok", "unparseable")
            if not force and retained:
                continue
            pending.append(task)
        tasks = pending[:max_tasks]

    print(f"\n{len(tasks)} sample task(s) queued "
          f"(parallelism={max(1, max_parallel)})\n")
    results: list[dict] = []
    if max_parallel <= 1:
        for task in tasks:
            rec = _run_one_sample(task)
            results.append(rec)
            state = rec.get("status")
            extra = f" ({rec.get('error')})" if rec.get("error") else ""
            print(
                f"  [{state:>12}] {rec['campaign']}/{rec['experiment']} "
                f"sample {rec['sample']} "
                f"model={rec.get('model_resolved')} "
                f"cost=${rec.get('total_cost_usd')}{extra}"
            )
    else:
        with ThreadPoolExecutor(max_workers=max(1, max_parallel)) as ex:
            futs = [ex.submit(_run_one_sample, t) for t in tasks]
            for fut in as_completed(futs):
                rec = fut.result()
                results.append(rec)
                print(
                    f"  [{rec.get('status'):>12}] {rec['campaign']}/{rec['experiment']} "
                    f"sample {rec['sample']}"
                )

    summarize(out_root, manifest)
    failed = [r for r in results if r.get("status") == "error"]
    print(f"\nrun complete: {len(results)} samples, {len(failed)} failed "
          f"-> {out_root}")
    return 1 if failed else 0


# ---------------------------------------------------------------------------
# Summaries
# ---------------------------------------------------------------------------


def _load_samples(out_root: Path) -> dict[tuple[str, str], list[dict]]:
    by_key: dict[tuple[str, str], list[dict]] = {}
    for sj in sorted((out_root / "samples").glob("*/*/sample-*/sample.json")):
        rec = json.loads(sj.read_text(encoding="utf-8"))
        by_key.setdefault((rec["campaign"], rec["experiment"]), []).append(rec)
    for key in by_key:
        by_key[key].sort(key=lambda r: r["sample"])
    return by_key


def summarize(out_root: Path, manifest: dict | None = None) -> dict:
    out_root = Path(out_root)
    exp_json = out_root / "experiment.json"
    if manifest is None:
        if not exp_json.exists():
            raise VarianceError(
                f"{out_root}: no experiment.json and no --manifest given"
            )
        manifest = {
            "experiment_id": json.loads(exp_json.read_text())["experiment_id"],
            "campaigns": [],
        }
        # Reconstruct per-campaign metadata from materialization.json
        camps: dict[str, dict] = {}
        for mj in sorted((out_root / "materializations").glob("*/*/materialization.json")):
            m = json.loads(mj.read_text())
            camp = camps.setdefault(
                m["campaign"],
                {
                    "id": m["campaign"],
                    "source": m.get("source"),
                    "experiments": {},
                },
            )
            camp["experiments"][m["experiment"]] = {}
        manifest["campaigns"] = [camps[k] for k in sorted(camps)]
        for i, camp in enumerate(manifest["campaigns"], start=1):
            camp["trial"] = i
            camp["ground_truth"] = None
            camp["fidelity"] = "filesystem-only"

    by_key = _load_samples(out_root)
    trials: list[dict] = []
    for camp in manifest["campaigns"]:
        if not isinstance(camp.get("experiments"), dict):
            continue
        entry: dict[str, Any] = {
            "trial": camp["trial"],
            "campaign_id": camp["id"],
            "source": camp.get("source"),
            "ground_truth": camp.get("ground_truth"),
            "original_verdict": camp.get("original_verdict"),
            "fidelity": camp.get("fidelity", "filesystem-only"),
            "experiments": {},
        }
        for kind in camp["experiments"]:
            records = by_key.get((camp["id"], kind), [])
            parsed_records = [
                r for r in records
                if r.get("status") in ("ok", "unparseable") and r.get("parsed")
            ]
            exp_entry: dict[str, Any] = {
                "samples_total": len(records),
                "samples_ok": sum(1 for r in records if r.get("status") == "ok"),
                "samples_unparseable": sum(
                    1 for r in records if r.get("status") == "unparseable"
                ),
                "samples_failed": sum(1 for r in records if r.get("status") == "error"),
                "samples_reused": sum(1 for r in records if r.get("reused")),
                "sample_records": [
                    {
                        "sample": r["sample"],
                        "status": r.get("status"),
                        "model_resolved": r.get("model_resolved"),
                        "prompt_sha256": r.get("prompt_sha256"),
                        "workspace_hash": r.get("workspace_hash"),
                        "duration_s": r.get("duration_s"),
                        "total_cost_usd": r.get("total_cost_usd"),
                        "parsed": r.get("parsed"),
                        "parse_error": r.get("parse_error"),
                        "error": r.get("error"),
                        "sample_dir": str(
                            Path(r["sample_json"]).parent.relative_to(out_root)
                        ),
                    }
                    for r in records
                ],
            }
            if kind == "tool-call":
                exp_entry["metrics"] = tool_call_metrics(parsed_records)
            else:
                exp_entry["metrics"] = verdict_metrics(
                    parsed_records, camp.get("ground_truth"),
                    experiment_defaults(camp["experiments"][kind])["verdict_support"],
                )
            entry["experiments"][kind] = exp_entry
        trials.append(entry)
    trials.sort(key=lambda t: t["trial"])

    summary = {
        "experiment_id": manifest["experiment_id"],
        "harness": json.loads(exp_json.read_text()).get("harness"),
        "trials": trials,
    }
    (out_root / "summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    write_csv(out_root, summary)
    write_report(out_root, summary)
    plots_dir = out_root / "plots"
    plots_dir.mkdir(exist_ok=True)
    write_plots(out_root, summary, plots_dir)
    return summary


def _csv_rows(summary: dict) -> list[dict]:
    rows: list[dict] = []
    for t in summary["trials"]:
        for kind, exp in t["experiments"].items():
            base = {
                "trial": t["trial"],
                "campaign_id": t["campaign_id"],
                "experiment": kind,
            }
            if t.get("original_verdict"):
                rows.append({**base, "metric": "original_verdict",
                             "value": t["original_verdict"]})
            if kind == "tool-call":
                m = exp["metrics"]
                for field in ("callable", "axes_names_signature",
                              "delay_keys_signature", "joint_call_signature"):
                    s = m[field]
                    for metric in ("n", "k", "entropy_nats", "entropy_normalized"):
                        rows.append({**base, "metric": f"{field}.{metric}",
                                     "value": s.get(metric)})
                    for v, c in s["counts"].items():
                        rows.append({**base, "metric": f"{field}.count",
                                     "value": c, "detail": v})
                for name, stats in m["numeric"].items():
                    if "values" in stats:  # flat numeric_stats
                        for metric in ("n", "mean", "variance_ddof1", "median",
                                       "iqr", "min", "max"):
                            rows.append({**base, "metric": f"{name}.{metric}",
                                         "value": stats.get(metric)})
                    else:  # nested per-subfield (axis:*/delay:*)
                        for sub, st in stats.items():
                            for metric in ("n", "mean", "variance_ddof1",
                                           "median", "iqr", "min", "max"):
                                rows.append(
                                    {**base, "metric": f"{name}.{sub}.{metric}",
                                     "value": st.get(metric)}
                                )
            else:
                m = exp["metrics"]
                v = m.get("verdict", {})
                for metric in ("n", "k", "entropy_nats", "entropy_normalized"):
                    rows.append({**base, "metric": f"verdict.{metric}",
                                 "value": v.get(metric)})
                for val, c in v.get("counts", {}).items():
                    rows.append({**base, "metric": "verdict.count",
                                 "value": c, "detail": val})
                gt = m.get("ground_truth")
                if gt:
                    for metric in ("n_truth", "p_truth", "p_truth_jeffreys",
                                   "nll_unsmoothed", "nll_jeffreys_alpha_0_5"):
                        rows.append({**base, "metric": f"ground_truth.{metric}",
                                     "value": gt.get(metric)})
            rows.append({**base, "metric": "samples_total",
                         "value": exp["samples_total"]})
            rows.append({**base, "metric": "samples_ok",
                         "value": exp["samples_ok"]})
            rows.append({**base, "metric": "samples_unparseable",
                         "value": exp["samples_unparseable"]})
            rows.append({**base, "metric": "samples_failed",
                         "value": exp["samples_failed"]})
    return rows


def write_csv(out_root: Path, summary: dict) -> None:
    rows = _csv_rows(summary)
    with open(out_root / "summary.csv", "w", newline="") as fh:
        writer = csv.DictWriter(
            fh, fieldnames=["trial", "campaign_id", "experiment", "metric",
                            "value", "detail"]
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    # Per-sample tidy CSV
    sample_rows = []
    for t in summary["trials"]:
        for kind, exp in t["experiments"].items():
            for r in exp["sample_records"]:
                sample_rows.append(
                    {
                        "trial": t["trial"],
                        "campaign_id": t["campaign_id"],
                        "experiment": kind,
                        "sample": r["sample"],
                        "status": r["status"],
                        "model_resolved": r["model_resolved"],
                        "prompt_sha256": r["prompt_sha256"],
                        "workspace_hash": r["workspace_hash"],
                        "duration_s": r["duration_s"],
                        "total_cost_usd": r["total_cost_usd"],
                        "sample_dir": r["sample_dir"],
                        "parse_error": r.get("parse_error"),
                        "error": r.get("error"),
                    }
                )
    with open(out_root / "samples.csv", "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(sample_rows[0].keys()))
        writer.writeheader()
        for row in sample_rows:
            writer.writerow(row)


def write_report(out_root: Path, summary: dict) -> None:
    lines: list[str] = []
    lines.append(f"# HERA replay-variance — {summary['experiment_id']}")
    lines.append("")
    harness = summary.get("harness") or {}
    lines.append("- **Harness:** "
                 f"{harness.get('kind')} (model requested: "
                 f"{harness.get('model_requested') or '(harness default)'})")
    lines.append(f"- **Sampling controls:** "
                 f"{harness.get('sampling_controls', {}).get('temperature', 'not exposed')}"
                 f" — {harness.get('sampling_controls', {}).get('note', '')}")
    lines.append(f"- **Output root:** `{out_root}`")
    lines.append("")
    lines.append("> Entropy measures **repeatability, not correctness**; "
                 "ground-truth NLL is reported separately for verdicts. "
                 "The across-trial trend is **observational**: historical "
                 "campaigns differ in acquired evidence and context, so it "
                 "does not by itself identify causal changes.")
    lines.append("")
    for t in summary["trials"]:
        lines.append(f"## Trial {t['trial']} — `{t['campaign_id']}`")
        lines.append("")
        lines.append(f"- source: `{t.get('source')}`")
        lines.append(f"- ground truth: `{t.get('ground_truth')}` · fidelity: "
                     f"`{t.get('fidelity', 'filesystem-only')}`")
        if t.get("original_verdict"):
            lines.append(f"- original (historical) verdict: `{t['original_verdict']}`")
        lines.append("")
        for kind, exp in t["experiments"].items():
            lines.append(f"### {kind}")
            lines.append("")
            lines.append(
                f"- samples: {exp['samples_total']} total / {exp['samples_ok']} ok / "
                f"{exp['samples_unparseable']} unparseable / {exp['samples_failed']} failed"
            )
            m = exp["metrics"]
            if kind == "tool-call":
                call = m["callable"]
                lines.append("- callable counts: "
                             + ", ".join(f"`{v}`×{c}" for v, c in call["counts"].items())
                             + f"  (H={call['entropy_nats']:.3f} nats, "
                             f"H/lnK={call['entropy_normalized']:.3f}, K={call['k']})")
                joint = m["joint_call_signature"]
                lines.append(f"- joint call-signature: K={joint['k']} distinct, "
                             f"H={joint['entropy_nats']:.3f} nats "
                             f"(descriptive — continuous parameters may make every "
                             f"signature unique)")
                for name, stats in m["numeric"].items():
                    def _fmt(st: dict) -> str:
                        return (
                            f"median={st['median']}, "
                            f"IQR=[{st['q25']}, {st['q75']}], "
                            f"min={st['min']}, max={st['max']} "
                            f"(n={st['n']}, var={st['variance_ddof1']})"
                        )
                    if "values" in stats:
                        if stats.get("n"):
                            lines.append(f"- `{name}`: {_fmt(stats)}")
                    else:
                        for sub, st in stats.items():
                            if st.get("n"):
                                lines.append(f"- `{name}.{sub}`: {_fmt(st)}")
            else:
                v = m["verdict"]
                lines.append("- verdict histogram: "
                             + ", ".join(f"`{val}`×{c}" for val, c in v["counts"].items())
                             + f"  (H={v['entropy_nats']:.3f} nats, "
                             f"H/lnK={v['entropy_normalized']:.3f}, K={v['k']})")
                gt = m.get("ground_truth")
                if gt and "p_truth" in gt:
                    lines.append(
                        f"- ground truth `{gt['ground_truth']}`: p_truth="
                        f"{gt['p_truth']:.3f}, NLL_unsmoothed="
                        f"{gt['nll_unsmoothed']:.3f}, NLL_Jeffreys(α=0.5)="
                        f"{gt['nll_jeffreys_alpha_0_5']:.3f}"
                    )
            lines.append("")
            lines.append("| # | status | model | parsed → | cost | dir |")
            lines.append("|---|---|---|---|---|---|")
            for r in exp["sample_records"]:
                parsed = ""
                if isinstance(r.get("parsed"), dict):
                    if kind == "tool-call":
                        parsed = f"`{r['parsed'].get('callable')}`"
                    else:
                        parsed = f"`{r['parsed'].get('verdict')}`"
                if r.get("parse_error"):
                    parsed = f"*unparseable* ({r['parse_error'][:60]})"
                if r.get("error"):
                    parsed = f"*failed* ({r['error'][:60]})"
                lines.append(
                    f"| {r['sample']} | {r['status']} | {r.get('model_resolved')} | "
                    f"{parsed} | {r.get('total_cost_usd')} | "
                    f"[{r['sample_dir']}]({r['sample_dir']}/sample.json) |"
                )
            lines.append("")
        lines.append("")
    (out_root / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_plots(out_root: Path, summary: dict, plots_dir: Path) -> None:
    trials = [t["trial"] for t in summary["trials"]]
    labels = [t["campaign_id"] for t in summary["trials"]]
    short_labels = []
    for trial, label in zip(trials, labels):
        stamp = label.removesuffix("-qc0426").replace("d2", ".2")
        if len(stamp) >= 8 and stamp[:8].isdigit():
            stamp = f"{stamp[4:6]}-{stamp[6:8]}{stamp[8:]}"
        short_labels.append(f"Trial {trial}\n{stamp}")

    def get(t: dict, kind: str, *path: str):
        node = t["experiments"].get(kind)
        if not node:
            return None
        node = node.get("metrics")
        for key in path:
            if not isinstance(node, dict) or key not in node:
                return None
            node = node[key]
        return node

    tool_joint = [get(t, "tool-call", "joint_call_signature", "entropy_nats")
                  for t in summary["trials"]]
    tool_callable = [get(t, "tool-call", "callable", "entropy_nats")
                     for t in summary["trials"]]
    verdict_h = [get(t, "final-analysis", "verdict", "entropy_nats")
                 for t in summary["trials"]]
    nll_smooth = [get(t, "final-analysis", "ground_truth",
                      "nll_jeffreys_alpha_0_5") for t in summary["trials"]]
    nll_unsmooth = [get(t, "final-analysis", "ground_truth", "nll_unsmoothed")
                    for t in summary["trials"]]

    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5), constrained_layout=True)
    ax = axes[0]
    if any(v is not None for v in tool_joint):
        ax.plot(trials, tool_joint, "s-", label="tool-call joint signature H")
    if any(v is not None for v in tool_callable):
        ax.plot(trials, tool_callable, "o--", label="tool-call callable H")
    if any(v is not None for v in verdict_h):
        ax.plot(trials, verdict_h, "^-.", label="final-analysis verdict H")
    ax.set_xlabel("campaign trial (chronological)")
    ax.set_ylabel("Shannon entropy (nats)")
    ax.set_xticks(trials)
    ax.set_xticklabels(short_labels, fontsize=8)
    handles, _ = ax.get_legend_handles_labels()
    if handles:
        ax.legend(fontsize=7)
    ax.set_title("Entropy vs campaign trial")

    ax = axes[1]
    if any(v is not None for v in nll_smooth):
        ax.plot(trials, nll_smooth, "o-", label="NLL (Jeffreys α=0.5)")
    if any(v is not None for v in nll_unsmooth):
        ax.plot(trials, nll_unsmooth, "s--", label="NLL (unsmoothed)")
    ax.set_xlabel("campaign trial (chronological)")
    ax.set_ylabel("-ln p(ground truth)")
    ax.set_xticks(trials)
    ax.set_xticklabels(short_labels, fontsize=8)
    handles, _ = ax.get_legend_handles_labels()
    if handles:
        ax.legend(fontsize=7)
    ax.set_title("Ground-truth NLL vs campaign trial (final analysis)")

    fig.suptitle(
        "Observational trend across chronological campaign trials "
        "(context/evidence differ — NOT causal)",
        fontsize=9,
    )
    for ext in ("png", "svg"):
        fig.savefig(plots_dir / f"entropy-vs-campaign-trial.{ext}", dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _default_out_root(manifest: dict, output: str | None) -> Path:
    if output:
        return Path(output).expanduser()
    base = os.environ.get("HERA_DATA")
    if base:
        root = Path(base) / "variance"
    else:
        root = Path.home() / ".hera" / "variance"
    ts = time.strftime("%Y%m%d-%H%M%S")
    return root / manifest["experiment_id"] / ts


def cmd_inspect(manifest: dict) -> int:
    print(f"# inspect — {manifest['experiment_id']}")
    print(f"harness: {manifest['harness'].get('kind')} "
          f"(model: {manifest['harness'].get('model') or '(default)'}, "
          f"timeout {manifest['harness'].get('timeout_s', 1800)}s)")
    for camp in manifest["campaigns"]:
        src = Path(camp["source"])
        print(f"\n## trial {camp['trial']} — {camp['id']}")
        print(f"  source: {src}")
        print(f"  ground_truth: {camp.get('ground_truth')}  "
              f"fidelity: {camp.get('fidelity', 'filesystem-only')}")
        print(f"  transcript: {camp.get('transcript') or 'none'}")
        for kind, cfg_raw in camp["experiments"].items():
            cfg = experiment_defaults(cfg_raw)
            print(f"  [{kind}]")
            nb = load_nb(src / cfg["measure_notebook"])
            print(f"    measure_notebook={cfg['measure_notebook']} "
                  f"({len(nb['cells'])} cells)"
                  + (f" cut_index={cfg['cut_index']}" if not cfg.get("sanitize")
                     else " sanitize"))
            if cfg.get("analysis_notebook"):
                anb = load_nb(src / cfg["analysis_notebook"])
                print(f"    analysis_notebook={cfg['analysis_notebook']} "
                      f"({len(anb['cells'])} cells)"
                      + (f" cut_index={cfg['analysis_cut_index']}"
                         if not cfg.get("sanitize") else " sanitize"))
            missing = [d for d in cfg["data_runs"] if not (src / "data" / str(d)).is_dir()]
            print(f"    data_runs={cfg['data_runs']} "
                  f"({'ALL PRESENT' if not missing else 'MISSING: ' + str(missing)})")
            for rel in cfg.get("include", []):
                print(f"    include {rel}: {'ok' if (src / rel).is_file() else 'MISSING'}")
            # Dry-run leak scan on an in-memory crop so curation errors surface here
            with tempfile.TemporaryDirectory() as td:
                try:
                    materialize(camp, kind, cfg, Path(td) / "ws")
                    print("    leak-scan: PASS")
                except LeakError as exc:
                    print(f"    leak-scan: FAIL — {exc}")
            print(f"    samples={cfg.get('samples', 5)}")
    return 0


def cmd_materialize(manifest: dict, output: str, campaigns: list[str] | None,
                    experiments: list[str] | None) -> int:
    out = _default_out_root(manifest, output)
    for camp in manifest["campaigns"]:
        if campaigns and camp["id"] not in campaigns:
            continue
        for kind, cfg_raw in camp["experiments"].items():
            if experiments and kind not in experiments:
                continue
            cfg = experiment_defaults(cfg_raw)
            dest = out / "materializations" / camp["id"] / kind / "workspace"
            materialize(camp, kind, cfg, dest)
            m = json.loads((dest.parent / "materialization.json").read_text())
            print(f"{camp['id']}/{kind}: leak-scan {m['leak_scan']['status']}, "
                  f"{len(m['files'])} files, "
                  f"workspace_sha256={m['workspace_sha256'][:16]}…")
    print(f"\nmaterialized -> {out}")
    return 0


def cmd_run(
    manifest: dict,
    output: str,
    samples: int | None,
    model: str | None,
    timeout: int | None,
    harness: str | None,
    thinking: str | None,
    max_parallel: int,
    force: bool,
    campaigns: list[str] | None,
    experiments: list[str] | None,
    max_tasks: int | None,
) -> int:
    out = _default_out_root(manifest, output)
    return run_experiments(
        manifest, out,
        samples_override=samples,
        model_override=model,
        timeout_override=timeout,
        harness_override=harness,
        thinking_override=thinking,
        max_parallel=max_parallel,
        force=force,
        campaigns=campaigns,
        experiments=experiments,
        max_tasks=max_tasks,
    )


def cmd_compare(inputs: list[str], output: str) -> int:
    specifications: list[tuple[str, Path]] = []
    for value in inputs:
        if "=" not in value:
            raise ComparisonError(
                f"comparison input must be LABEL=OUTPUT_DIR, got {value!r}"
            )
        label, path = value.split("=", 1)
        if not label or not path:
            raise ComparisonError(
                f"comparison input must be LABEL=OUTPUT_DIR, got {value!r}"
            )
        specifications.append((label, Path(path).expanduser()))
    result = compare_outputs(specifications, Path(output).expanduser())
    print(f"compared {len(result['models'])} model(s) -> {output}")
    return 0


def cmd_tool_longitudinal(input_root: str, output: str) -> int:
    result = summarize_tool_variance(
        Path(input_root).expanduser(), Path(output).expanduser()
    )
    print(
        f"summarized {len(result['campaigns'])} tool-call campaign(s) -> {output}"
    )
    return 0


def cmd_summarize(output: str, manifest_path: str | None) -> int:
    out = Path(output).expanduser()
    if not out.is_dir():
        print(f"error: output dir not found: {out}", file=sys.stderr)
        return 2
    manifest = load_manifest(Path(manifest_path)) if manifest_path else None
    summary = summarize(out, manifest)
    n_trials = len(summary["trials"])
    print(f"summarized {n_trials} trial(s) -> {out}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="hera-variance",
        description="HERA replay-variance experiments (curated frontiers, "
                    "leak-checked materialization, N fresh samples, "
                    "entropy/spread/NLL summaries).",
    )
    sub = ap.add_subparsers(dest="command", required=True)

    p_ins = sub.add_parser("inspect", help="validate manifest + describe frontiers")
    p_ins.add_argument("--manifest", required=True)

    p_mat = sub.add_parser("materialize", help="build frontiers + leak checks, no model calls")
    p_mat.add_argument("--manifest", required=True)
    p_mat.add_argument("--output", default=None)
    p_mat.add_argument("--campaigns", nargs="*", default=None)
    p_mat.add_argument("--experiments", nargs="*", default=None)

    p_run = sub.add_parser("run", help="execute selected experiments")
    p_run.add_argument("--manifest", required=True)
    p_run.add_argument("--output", default=None)
    p_run.add_argument("--samples", type=int, default=None)
    p_run.add_argument("--model", default=None)
    p_run.add_argument(
        "--harness", choices=("claude-p", "fake"), default=None
    )
    p_run.add_argument("--thinking", default=None)
    p_run.add_argument("--timeout", type=int, default=None)
    p_run.add_argument("--max-parallel", type=int, default=1)
    p_run.add_argument(
        "--max-tasks", type=int, default=None,
        help="attempt at most this many pending samples (for scheduler epochs)",
    )
    p_run.add_argument("--force", action="store_true")
    p_run.add_argument("--campaigns", nargs="*", default=None)
    p_run.add_argument("--experiments", nargs="*", default=None)

    p_sum = sub.add_parser("summarize", help="recompute metrics/plots from captured samples")
    p_sum.add_argument("--output", required=True)
    p_sum.add_argument("--manifest", default=None)

    p_cmp = sub.add_parser("compare", help="compare completed per-model output roots")
    p_cmp.add_argument(
        "--input", action="append", required=True, metavar="LABEL=OUTPUT_DIR"
    )
    p_cmp.add_argument("--output", required=True)

    p_tool = sub.add_parser(
        "tool-longitudinal",
        help="build longitudinal tool-call entropy/disagreement artifacts",
    )
    p_tool.add_argument("--input", required=True)
    p_tool.add_argument("--output", required=True)

    args = ap.parse_args(argv)
    try:
        if args.command == "summarize":
            return cmd_summarize(args.output, args.manifest)
        if args.command == "compare":
            return cmd_compare(args.input, args.output)
        if args.command == "tool-longitudinal":
            return cmd_tool_longitudinal(args.input, args.output)
        manifest = load_manifest(Path(args.manifest))
        if args.command == "inspect":
            return cmd_inspect(manifest)
        if args.command == "materialize":
            return cmd_materialize(manifest, args.output, args.campaigns,
                                   args.experiments)
        if args.command == "run":
            return cmd_run(
                manifest, args.output, args.samples, args.model, args.timeout,
                args.harness, args.thinking, args.max_parallel, args.force,
                args.campaigns, args.experiments, args.max_tasks,
            )
    except (VarianceError, ComparisonError, ToolVarianceError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
