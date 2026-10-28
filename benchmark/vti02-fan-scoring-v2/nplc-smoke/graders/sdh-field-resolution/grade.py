#!/usr/bin/env python3
"""sdh-field-resolution: does the field axis resolve SdH at the density column(s) it is taken at?

    grade.py check <output.json>                         # shape + sanity; exit 1 with reasons; no score
    grade.py score <output.json> --archive <dir> -o scores.json

A spot check is a one-column fan.  Scorer: Aaron's S1 field-resolution check (s1.py, next to
this file) per column, fan binary (a fraction f of the resolvable columns must pass), strict
window from the device's b_min (../devices.toml).  Columns come from the output file in
density: one value or a short list (n_cm2), or a uniform range (n_min_cm2, n_max_cm2,
n_columns).  The extractor converts gate voltages to density itself, from the card.

Not scripted yet: the fan design checks from hera/docs/benchmark-rubrics.md (dynamic range
vs the worst corner, cost floor).  They join this file when the rubric is settled.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path[:0] = [str(Path(__file__).resolve().parent), str(Path(__file__).resolve().parents[1])]
import s1  # noqa: E402  - sibling module, Aaron's scorer verbatim
from devices import device_params  # noqa: E402  - graders/devices.py

GRADER = "sdh-field-resolution"
S1_KW = dict(g=4, margin=1.0, m=3.0, p_min=5.0, f=0.8, strict=True)
S1_VERSION = "S1 wiki 2026-09-13; margin 1.0; strict window"
MAX_POINTS = 200_000
MAX_COLUMNS = 2000


def _num(x) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool) and np.isfinite(x)


def _int(x, lo, hi) -> bool:
    return isinstance(x, int) and not isinstance(x, bool) and lo <= x <= hi


def check(doc: dict) -> list[str]:
    """Reasons the file is unusable; empty means accepted."""
    r: list[str] = []
    if not isinstance(doc, dict):
        return ["top level must be a JSON object"]
    if doc.get("status") not in ("extracted", "cannot_extract"):
        r.append('status must be "extracted" or "cannot_extract"')
    if not isinstance(doc.get("flags", []), list) or not all(
            isinstance(f, dict) and {"kind", "severity", "note"} <= set(f) for f in doc.get("flags", [])):
        r.append("flags must be a list of {kind, severity, note} objects")
    if not isinstance(doc.get("notes", ""), str):
        r.append("notes must be a string")
    if doc.get("status") != "extracted":
        return r
    # field axis
    if doc.get("B_values") is not None:
        bv = doc["B_values"]
        if not (isinstance(bv, list) and 2 <= len(bv) <= MAX_POINTS and all(_num(v) and v >= 0 for v in bv)):
            r.append(f"B_values must be a list of 2..{MAX_POINTS} finite nonnegative numbers (tesla)")
    else:
        lo, hi, n, sp = doc.get("B_min_T"), doc.get("B_max_T"), doc.get("n_points"), doc.get("spacing")
        if not (_num(lo) and _num(hi) and lo >= 0 and lo < hi):
            r.append("B_min_T and B_max_T must be finite tesla with 0 <= B_min_T < B_max_T")
        if not _int(n, 2, MAX_POINTS):
            r.append(f"n_points must be an integer in 2..{MAX_POINTS}")
        if sp not in ("B", "invB"):
            r.append('spacing must be "B" or "invB"')
        elif sp == "invB" and _num(lo) and lo <= 0:
            r.append("spacing invB needs B_min_T > 0 (1/B is undefined at zero)")
    # density column(s): a value / short list, or a uniform range
    forms = []
    n = doc.get("n_cm2")
    if n is not None:
        forms.append("n_cm2")
        vals = n if isinstance(n, list) else [n]
        if not (1 <= len(vals) <= 64 and all(_num(v) for v in vals)):
            r.append("n_cm2 must be a finite number or a list of 1..64 finite numbers (cm^-2)")
        elif max(abs(v) for v in vals) > 1e14:
            r.append("n_cm2 above 1e14 cm^-2: units look like m^-2 (1 m^-2 = 1e-4 cm^-2)")
    if any(doc.get(k) is not None for k in ("n_min_cm2", "n_max_cm2", "n_columns")):
        forms.append("n_min_cm2/n_max_cm2/n_columns")
        lo, hi, k = doc.get("n_min_cm2"), doc.get("n_max_cm2"), doc.get("n_columns")
        if not (_num(lo) and _num(hi) and lo < hi):
            r.append("n_min_cm2 and n_max_cm2 must be finite with n_min_cm2 < n_max_cm2")
        elif max(abs(lo), abs(hi)) > 1e14:
            r.append("density range above 1e14 cm^-2: units look like m^-2")
        if not _int(k, 2, MAX_COLUMNS):
            r.append(f"n_columns must be an integer in 2..{MAX_COLUMNS}")
    if len(forms) != 1:
        r.append("give the density as n_cm2 (a number or a short list) or as n_min_cm2, n_max_cm2, n_columns"
                 + (" -- not both" if len(forms) > 1 else ""))
    return r


def field_axis(doc: dict) -> np.ndarray:
    if doc.get("B_values") is not None:
        return np.asarray(doc["B_values"], float)
    lo, hi, n = float(doc["B_min_T"]), float(doc["B_max_T"]), int(doc["n_points"])
    if doc["spacing"] == "invB":
        return 1.0 / np.linspace(1.0 / lo, 1.0 / hi, n)
    return np.linspace(lo, hi, n)


def columns(doc: dict) -> np.ndarray:
    if doc.get("n_cm2") is not None:
        return np.atleast_1d(np.asarray(doc["n_cm2"], float))
    return np.linspace(float(doc["n_min_cm2"]), float(doc["n_max_cm2"]), int(doc["n_columns"]))


def score(doc: dict, archive: Path) -> dict:
    out = {"grader": GRADER, "flags": doc.get("flags", []), "notes": doc.get("notes", ""),
           "versions": {"s1": S1_VERSION}}
    if doc["status"] == "cannot_extract":
        return {**out, "status": "cannot_extract", "ok": None}
    dev_cfg = device_params(archive, "b_min_T", "b_min_note")
    B = field_axis(doc)
    n = columns(doc)
    ok, diag = s1.field_resolution_ok(B, n, kind="B", b_min=dev_cfg["b_min_T"], **S1_KW)
    return {**out, "status": "graded", "ok": bool(ok), "device": dev_cfg["device"], "kind": "spot" if n.size == 1 else "fan",
            "n_points": int(B.size), "B_range_T": [float(B.min()), float(B.max())],
            "n_columns": int(n.size), "n_cm2": n.tolist() if n.size <= 64 else [float(n.min()), float(n.max())],
            "s1": _jsonable(diag),
            "params": {**S1_KW, "b_min_T": dev_cfg["b_min_T"], "b_min_note": dev_cfg["b_min_note"]}}


def _jsonable(x):
    if isinstance(x, dict):
        return {k: _jsonable(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_jsonable(v) for v in x]
    if isinstance(x, np.ndarray):
        return _jsonable(x.tolist())
    if isinstance(x, (np.floating, np.integer, np.bool_)):
        return x.item()
    if isinstance(x, float) and not np.isfinite(x):
        return str(x)
    return x


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check"); c.add_argument("output", type=Path)
    s = sub.add_parser("score"); s.add_argument("output", type=Path)
    s.add_argument("--archive", type=Path, required=True); s.add_argument("-o", "--out", type=Path)
    a = ap.parse_args(argv)
    try:
        doc = json.loads(a.output.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        print(f"rejected: cannot read {a.output}: {e}")
        return 1
    reasons = check(doc)
    if a.cmd == "check":
        print("accepted" if not reasons else "rejected:\n  " + "\n  ".join(reasons))
        return 0 if not reasons else 1
    if reasons:
        result = {"grader": GRADER, "status": "invalid", "ok": None, "reasons": reasons}
    else:
        result = score(doc, a.archive)
    text = json.dumps(result, indent=2)
    if a.out:
        a.out.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
