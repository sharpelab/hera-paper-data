"""Calibrate the replay-episode graders against cells whose materialized sweep is known.

A wrapper over ``hera-grade``, not part of it: the truths are the fake rig's vectors
(Nathan's ``grade.json`` per sample), which the runner must not know about.

    calibrate_graders.py list
    calibrate_graders.py build [--only SUBSTR]                 # fixtures, no model calls
    calibrate_graders.py run --image TAG [--n N] [--parallel P] [--only SUBSTR]

``build`` writes one fixture per case in the episode shape under
``$HERA_DATA/frontier/calibration/cases/<name>/``: ``session/`` is the smoke fork with the
case's cell(s) appended to its measure notebook, ``truth.json`` beside it holds the fake
rig's field range, row count, density and verdict.  ``run`` grades every fixture through the
runner's pool and diffs each ``output.json`` against its ``truth.json``; the table goes to
``$HERA_DATA/frontier/calibration/<stamp>.csv``.

Cases on this machine (``$HERA_DATA/frontier``):
  smoke/ref43, smoke/vti01-sdh-m47, smoke/vti02-sdh-m39     reference cells (tool_call.py + grade.json)
  archive/results-rounds-1-9/qc0426-sdh-m41-opus5/*-fakerig/  ten Opus cells on the ref43 fork
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import shutil
import sys
import time
from pathlib import Path

from hera.grading import runner

HERA_DATA = Path(os.environ.get("HERA_DATA", "/data/sharpelab/hera-data"))
FRONTIER = HERA_DATA / "frontier"
CASES = FRONTIER / "calibration" / "cases"
OPUS_R7 = FRONTIER / "archive/results-rounds-1-9/qc0426-sdh-m41-opus5/20260916T011156-opus5-round7-clean-card-fakerig"
GRADER = "sdh-field-resolution"
TRUTH_KEYS = ("kind", "B_range_T", "B_rows", "n_cm2", "ok")


def _code_cell(src: str) -> dict:
    return {"cell_type": "code", "execution_count": None, "metadata": {"hera": {"appended": "calibration"}},
            "outputs": [], "source": src.splitlines(keepends=True)}


def cases(only: str | None = None) -> list[dict]:
    out = []

    def add(name, base, cells, grade_path):
        if only and only not in name:
            return
        truth = json.loads(grade_path.read_text(encoding="utf-8"))
        out.append({"name": name, "base": base, "cells": cells,
                    "truth": {**{k: truth.get(k) for k in TRUTH_KEYS}, "source": str(grade_path)}})

    for name, base in (("ref43", FRONTIER / "smoke/ref43"), ("vti01-ref49", FRONTIER / "smoke/vti01-sdh-m47"),
                       ("vti02-ref41", FRONTIER / "smoke/vti02-sdh-m39")):
        if (base / "tool_call.py").exists():
            add(name, base, [(base / "tool_call.py").read_text(encoding="utf-8")], base / "grade.json")
    if OPUS_R7.exists():
        for s in sorted(OPUS_R7.iterdir()):
            if not (s / "grade.json").exists():
                continue
            appended = json.loads((s / "appended_cells.json").read_text(encoding="utf-8"))
            cells = ["".join(c["source"]) for c in appended if c["cell_type"] == "code" and "".join(c["source"]).strip()]
            add("opus-r7-" + s.name.split("opus5-")[1].rsplit("-", 1)[0], FRONTIER / "smoke/ref43", cells, s / "grade.json")
    return out


def build_fixture(case: dict, dest: Path) -> Path:
    """``dest/session`` = the fork with the case's cells appended; ``dest/truth.json`` beside it."""
    base: Path = case["base"]
    if dest.exists():
        shutil.rmtree(dest)
    session = dest / "session"
    session.mkdir(parents=True)
    fork = json.loads((base / "fork.json").read_text(encoding="utf-8"))
    for p in base.iterdir():
        if p.name in ("grade.json", "tool_call.py", "fork.json", "grades") or p.suffix == ".py":
            continue
        (shutil.copytree if p.is_dir() else shutil.copy2)(p, session / p.name)
    nb_name = fork["notebooks"]["measure"]["file"]
    nb = json.loads((session / nb_name).read_text(encoding="utf-8"))
    nb["cells"].extend(_code_cell(src) for src in case["cells"])
    (session / nb_name).write_text(json.dumps(nb, indent=1), encoding="utf-8")
    (dest / "truth.json").write_text(json.dumps(case["truth"], indent=2) + "\n", encoding="utf-8")
    return dest


def compare(output: dict | None, truth: dict) -> dict:
    """Field range, row count and density of the extraction vs the fake rig's grade."""
    t_range, t_rows = truth.get("B_range_T"), truth.get("B_rows")
    t_n = (truth.get("n_cm2") or [None])[0]
    if output is None or output.get("status") != "extracted":
        return {"match": False, "status": (output or {}).get("status", "no_output")}
    if output.get("B_values") is not None:
        bv = output["B_values"]
        o_range, o_rows = [min(bv), max(bv)], len(bv)
    else:
        o_range, o_rows = [output.get("B_min_T"), output.get("B_max_T")], output.get("n_points")
    n = output.get("n_cm2")
    o_n = n[0] if isinstance(n, list) else n
    rng_ok = t_range is not None and o_range[0] is not None and all(abs(a - b) < 1e-3 for a, b in zip(o_range, t_range))
    rows_ok = t_rows == o_rows
    n_ok = t_n is not None and o_n is not None and abs(o_n - t_n) <= 0.02 * max(abs(t_n), 1e10)
    return {"match": bool(rng_ok and rows_ok and n_ok), "status": "extracted",
            "range": o_range, "range_truth": t_range, "rows": o_rows, "rows_truth": t_rows,
            "n": o_n, "n_truth": t_n, "range_ok": rng_ok, "rows_ok": rows_ok, "n_ok": bool(n_ok)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list")
    b = sub.add_parser("build")
    b.add_argument("--only", help="substring filter on case names")
    r = sub.add_parser("run")
    r.add_argument("--only", help="substring filter on case names")
    r.add_argument("--image", required=True)
    r.add_argument("--n", type=int, default=1)
    r.add_argument("--parallel", type=int, default=4)
    r.add_argument("--model", default="claude-opus-5")
    r.add_argument("--effort", default="medium", choices=runner.EFFORTS)
    a = ap.parse_args(argv)
    cs = cases(getattr(a, "only", None))
    if a.cmd == "list":
        for c in cs:
            t = c["truth"]
            print(f"{c['name']:28s} cells={len(c['cells'])} truth: {t.get('kind')} B={t.get('B_range_T')} "
                  f"rows={t.get('B_rows')} n={(t.get('n_cm2') or [None])[0]}  fixture={'yes' if (CASES / c['name'] / 'session').is_dir() else 'no'}")
        return 0
    if a.cmd == "build":
        for c in cs:
            print(f"built {build_fixture(c, CASES / c['name'])}")
        return 0
    dirs = [CASES / c["name"] for c in cs]
    missing = [d for d in dirs if not (d / "session").is_dir()]
    if missing:
        print("fixtures missing, run build first: " + ", ".join(d.name for d in missing), file=sys.stderr)
        return 2
    stamp = time.strftime("%Y%m%dT%H%M%S")
    jobs = runner.make_jobs(dirs, GRADER, n=a.n, image=a.image, model=a.model, effort=a.effort, stamp=stamp)
    records = runner.grade_many(jobs, parallel=a.parallel)
    print(runner.summarize(records))
    rows = []
    for job, rec in zip(jobs, records):
        truth = json.loads((job.episode_dir / "truth.json").read_text(encoding="utf-8"))
        out_path = job.run_dir / "output.json"
        output = json.loads(out_path.read_text(encoding="utf-8")) if out_path.exists() else None
        cmp = compare(output, truth)
        rows.append({"case": job.episode_dir.name, "run": job.run_dir.name, **cmp,
                     "score_status": rec["scores"].get("status"), "score_ok": rec["scores"].get("ok"), "truth_ok": truth.get("ok"),
                     "cost_usd": rec["claude"].get("cost_usd"), "turns": rec["claude"].get("turns"),
                     "wall_s": rec["claude"].get("wall_s"), "exit": rec["claude"].get("exit")})
    table = FRONTIER / "calibration" / f"{stamp}.csv"
    with table.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=sorted({k for r in rows for k in r}))
        w.writeheader()
        w.writerows(rows)
    n_match = sum(1 for r in rows if r["match"])
    print(f"\n{n_match}/{len(rows)} extractions match the fake-rig vectors; "
          f"${sum(r['cost_usd'] or 0 for r in rows):.2f} total; table: {table}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
