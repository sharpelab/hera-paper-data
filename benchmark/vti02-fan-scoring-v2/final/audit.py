#!/usr/bin/env python3
"""Post-hoc extraction audit of the vti-02 fan-design matrix: audit.md beside this file is the write-up.

    cd ~/sharpelab/measurement-env && uv run python /data/sharpelab/hera-data/vti02-fan-scoring-v2/final/audit.py

Re-scores eleven fans whose saved extraction misdescribes the landed cell, with the frozen grader and
the registered analysis code unchanged: six field grids that the extraction flattened to a uniform
grid (the actual vectors below are transcribed from the landed code), and five Astra fans whose 3 s
dwell sits in a before-point hook while the sweep call says fast_delay=0. Nothing under the run dirs
or the registered output is modified; the corrected numbers are printed and written to audit.json.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = Path.home() / "sharpelab" / "measurement-env"
RUNS = Path("/data/sharpelab/hera-data/replay/runs")
PREFIX = "vti02-fan-request-0822-"

spec = importlib.util.spec_from_file_location("vti02_fan_analysis", REPO / "hera/campaigns/vti02-fan-design/analysis.py")
an = importlib.util.module_from_spec(spec)
sys.modules["vti02_fan_analysis"] = an
spec.loader.exec_module(an)


def grid_4kxt1o_14() -> np.ndarray:
    B_LO, B_HI, D_INV, DB_MAX = 0.7, 10.0, 0.0105, 0.40
    b = [B_LO]
    while b[-1] < B_HI - 1e-9:
        nxt = 1.0 / (1.0 / b[-1] - D_INV) if (1.0 / b[-1] - D_INV) > 0 else B_HI
        b.append(min(nxt, b[-1] + DB_MAX, B_HI))
    return np.round(np.array(b), 4)


# The landed field vector, transcribed from each episode's appended cell (appended_cells.json).
FIELD_GRIDS = {
    "gpt6sol-none/20260929T234513-e9946u/00": np.r_[np.round(np.arange(1.5, 10.0, 0.2), 4), 10.0],
    "gpt6sol-none/20260929T234513-e9946u/14": np.round(np.r_[np.arange(0.50, 3.001, 0.05), np.arange(3.20, 10.001, 0.20)], 4),
    "opus55-none/20260929T234509-e2rujz/06": np.unique(np.round(np.hstack((1.0 / np.linspace(1.0, 1.0 / 4.0, 64), np.arange(4.2, 9.0001, 0.2))), 4)),
    "opus55-none/20260929T234509-e2rujz/11": np.unique(np.round(np.hstack((1 / np.arange(2.0, 1.0 - 1e-9, -0.05), 1 / np.arange(1.0, 0.2 - 1e-9, -0.01),
                                                                            np.arange(5.25, 10.0 + 1e-9, 0.25))), 4)),
    "opus-none/20260929T212518-7hk80x/02": np.hstack(([0.0], an.grade.field_axis({"spacing": "invB", "B_min_T": 1.0, "B_max_T": 10.0, "n_B": 109}))),
    "opus-none/20260929T234508-4kxt1o/14": grid_4kxt1o_14(),
}

# fast_delay=0 in the sweep call, interruptible_sleep(3.0) in the registered before-point hook.
HOOK_DWELL_S = {
    "astra-corpus/20260929T212521-qy46wv/03": 3.0,
    "astra-corpus/20260929T234511-d9dmed/15": 3.0,
    "astra-corpus/20260930T015331-xmv9jb/04": 3.0,
    "astra-none/20260929T234512-7x4jav/03": 3.0,
    "astra-none/20260929T234512-7x4jav/09": 3.0,
}

METRICS = {"p_call_8h": "1 P(call) within 8 h", "span": "2 tracked span (bins)", "rows_fl": "3 rows per F_L period at top n"}


def episode_dir(key: str) -> Path:
    case, stamp, nn = key.split("/")
    return RUNS / (PREFIX + case) / stamp / "episodes" / nn


def rescore(key: str, patch) -> tuple[dict, dict]:
    ep = episode_dir(key)
    doc = json.load(open(an.latest_extraction(ep)))
    before = an.score_fan(dict(doc), ep / "session")
    patched = patch(dict(doc))
    after = an.score_fan(patched, ep / "session")
    return before, after


def tests(fans: list[dict]) -> dict:
    out = {}
    for m in METRICS:
        r = an.delta_test(fans, lambda x, m=m: an.value(x, m))
        out[m] = {"statistic": r["statistic"], "per_model": r["per_model"]}
    r = an.dominance_test(fans)
    out["dominance"] = {"statistic": r["statistic"], "per_model": r["per_model"]}
    return out


def main() -> None:
    final = json.load(open(HERE / "analysis.json"))
    fans = [dict(e) for e in final["episodes"] if e["ending"] == "fan"]
    by_key = {f["key"].removeprefix(PREFIX): f for f in fans}
    rows = []

    def apply(key: str, what: str, patch) -> None:
        before, after = rescore(key, patch)
        rec = by_key[key]
        for k in ("hours", "p_call", "span", "rows_fl", "p_light", "p_split"):
            assert abs(float(before[k]) - float(rec[k])) < 1e-9, (key, k, before[k], rec[k])
        rows.append({"key": key, "what": what, "hours": (before["hours"], after["hours"]), "p_call": (before["p_call"], after["p_call"]),
                     "v8h": (an.value(before, "p_call_8h"), an.value(after, "p_call_8h")), "span": (before["span"], after["span"]),
                     "rows_fl": (before["rows_fl"], after["rows_fl"]), "field_axis": (before["field_axis"], after["field_axis"])})
        rec.update({k: after[k] for k in after})

    baseline = tests([dict(f) for f in fans])
    for key, B in FIELD_GRIDS.items():
        apply(key, "field grid", lambda d, B=B: {**d, "B_values": [float(b) for b in B], "n_B": int(B.size),
                                                  "B_min_T": float(B.min()), "B_max_T": float(B.max())})
    grids_only = tests([dict(f) for f in fans])
    for key, dwell in HOOK_DWELL_S.items():
        apply(key, "hook dwell", lambda d, dwell=dwell: {**d, "fast_delay_s": dwell})
    both = tests([dict(f) for f in fans])

    print(f"{'fan':45s} {'what':10s} {'hours':>15s} {'P(call)':>15s} {'v(8 h)':>13s} {'span':>13s} {'rows/F_L':>13s}")
    for r in rows:
        f = lambda t, w=6, p=3: f"{t[0]:{w}.{p}f} → {t[1]:{w}.{p}f}"
        print(f"{r['key']:45s} {r['what']:10s} {f(r['hours'],6,2):>15s} {f(r['p_call']):>15s} {f(r['v8h']):>13s} {f(r['span'],5,2):>13s} {f(r['rows_fl'],5,2):>13s}")
    print()
    print(f"{'statistic':36s} {'registered':>11s} {'six grids':>11s} {'grids + hook dwell':>19s}")
    for m, lab in {**METRICS, "dominance": "4 Pareto dominance D"}.items():
        print(f"{lab:36s} {baseline[m]['statistic']:+11.4f} {grids_only[m]['statistic']:+11.4f} {both[m]['statistic']:+19.4f}")
    for m in ("p_call_8h", "span", "rows_fl", "dominance"):
        print(f"  per model, {m}: " + ", ".join(f"{k.removeprefix('claude-')} {baseline[m]['per_model'][k]:+.3f}→{both[m]['per_model'][k]:+.3f}"
                                                  for k in baseline[m]["per_model"]))
    json.dump({"fans": rows, "registered": baseline, "six_grids": grids_only, "grids_and_hook_dwell": both},
              open(HERE / "audit.json", "w"), indent=1, default=float)
    print(f"\nwrote {HERE / 'audit.json'}")


if __name__ == "__main__":
    main()
