#!/usr/bin/env python3
"""sc-survey: how many of the proposed gate setpoints land in zf1's superconducting arc?

    grade.py check <output.json>                         # shape + sanity; exit 1 with reasons; no score
    grade.py score <output.json> --archive <dir> -o scores.json

Scorer: sc_arc.py (next to this file) -- Aaron's fixed quadrilateral in (V_tg, V_bg), pass when at
least K_MIN setpoints fall inside.  Gate space only: no (n, D) calibration, no resistance
threshold.  A grid comes as {min, max, n} per gate (outer product); anything else as points.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sc_arc  # noqa: E402  - sibling module: Aaron's arc, K_MIN, the benchmark

GRADER = "sc-survey"
MAX_POINTS = 2_000_000


def _num(x) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool) and np.isfinite(x)


def _axis_ok(a) -> bool:
    return (isinstance(a, dict) and _num(a.get("min")) and _num(a.get("max")) and a["min"] <= a["max"]
            and isinstance(a.get("n"), int) and not isinstance(a["n"], bool) and 1 <= a["n"] <= 100_000)


def check(doc: dict) -> list[str]:
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
    grid = doc.get("V_tg") is not None or doc.get("V_bg") is not None
    pts = doc.get("points") is not None
    if grid == pts:
        r.append("give either V_tg and V_bg as {min, max, n} (a grid) or points as [[V_tg, V_bg], ...]")
    if grid:
        if not (_axis_ok(doc.get("V_tg")) and _axis_ok(doc.get("V_bg"))):
            r.append("V_tg and V_bg must each be {min, max, n} with finite volts, min <= max, integer n >= 1")
        elif doc["V_tg"]["n"] * doc["V_bg"]["n"] > MAX_POINTS:
            r.append(f"grid has more than {MAX_POINTS} points")
    if pts:
        p = doc["points"]
        if not (isinstance(p, list) and 1 <= len(p) <= MAX_POINTS
                and all(isinstance(q, list) and len(q) == 2 and _num(q[0]) and _num(q[1]) for q in p)):
            r.append(f"points must be a list of 1..{MAX_POINTS} [V_tg, V_bg] pairs")
    return r


def setpoints(doc: dict) -> tuple[np.ndarray, np.ndarray]:
    if doc.get("points") is not None:
        p = np.asarray(doc["points"], float)
        return p[:, 0], p[:, 1]
    t, b = doc["V_tg"], doc["V_bg"]
    T, G = np.meshgrid(np.linspace(t["min"], t["max"], t["n"]), np.linspace(b["min"], b["max"], b["n"]), indexing="ij")
    return T.ravel(), G.ravel()


def score(doc: dict, archive: Path) -> dict:
    out = {"grader": GRADER, "flags": doc.get("flags", []), "notes": doc.get("notes", ""),
           "versions": {"sc_arc": "zf1 SC-arc quadrilateral 2026-09-14"}}
    if doc["status"] == "cannot_extract":
        return {**out, "status": "cannot_extract", "ok": None}
    vtg, vbg = setpoints(doc)
    g = sc_arc.grade(vtg, vbg)
    return {**out, "status": "graded", "ok": bool(g["pass"]),
            "n_points": g["n_points"], "n_inside": g["n_inside"],
            "V_tg_range": [float(vtg.min()), float(vtg.max())], "V_bg_range": [float(vbg.min()), float(vbg.max())],
            "params": {"k_min": sc_arc.K_MIN, "region": sc_arc.REGION}}


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
