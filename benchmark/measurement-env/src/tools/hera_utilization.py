#!/usr/bin/env python3
"""hera-utilization — fridge-utilization scoring for a HERA session dir.

Implements hera/docs/hera-utilization-design.md: raw utilization
(measuring / span) plus the HIL-adjusted split that partitions idle time
into HERA court (thinking) and human court (a landed-but-not-yet-consumed
HERA proposal was waiting on the operator).

Read-only. Inputs are data/<id>/metadata.json sweep windows and
metadata.hera.appended_at cell-landing stamps in the measure notebook.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys
from datetime import datetime, timezone


def _load_sweeps(session_dir: str) -> list[dict]:
    sweeps = []
    for path in glob.glob(os.path.join(session_dir, "data", "*", "metadata.json")):
        run_id = os.path.basename(os.path.dirname(path))
        try:
            meta = json.load(open(path, encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        start, end = meta.get("start_time"), meta.get("end_time")
        if start is None or end is None:
            continue
        comments = meta.get("comments") or []
        sweeps.append(
            {
                "id": int(run_id) if run_id.isdigit() else run_id,
                "start": float(start),
                "end": float(end),
                "slug": comments[0] if comments else "",
            }
        )
    sweeps.sort(key=lambda s: (s["start"], s["end"]))
    return sweeps


def _find_measure_notebook(session_dir: str) -> str | None:
    hits = sorted(glob.glob(os.path.join(session_dir, "*_measure.ipynb")))
    if len(hits) == 1:
        return hits[0]
    if len(hits) > 1:
        raise SystemExit(
            f"ambiguous measure notebook ({len(hits)} matches) -- pass --measure-notebook"
        )
    return None


def _load_lands(notebook_path: str) -> list[float]:
    nb = json.load(open(notebook_path, encoding="utf-8"))
    lands = []
    for cell in nb.get("cells", []):
        hera = cell.get("metadata", {}).get("hera")
        if not isinstance(hera, dict):
            continue
        stamp = hera.get("appended_at")
        if not stamp:
            continue
        lands.append(datetime.fromisoformat(stamp).timestamp())
    lands.sort()
    return lands


def _merged_measuring(sweeps: list[dict]) -> float:
    total = 0.0
    cur_start = cur_end = None
    for s in sweeps:
        if cur_end is None:
            cur_start, cur_end = s["start"], s["end"]
        elif s["start"] <= cur_end:
            cur_end = max(cur_end, s["end"])
        else:
            total += cur_end - cur_start
            cur_start, cur_end = s["start"], s["end"]
    if cur_end is not None:
        total += cur_end - cur_start
    return total


def compute(
    session_dir: str,
    measure_notebook: str | None = None,
    end: float | None = None,
) -> dict:
    """Walk the per-gap court split; return the structured result.

    `end` (epoch) bounds the session: sweeps starting at/after it are
    excluded (e.g. a post-deliverable extension ruled outside the session).
    """
    sweeps = _load_sweeps(session_dir)
    if end is not None:
        sweeps = [s for s in sweeps if s["start"] < end]
    if not sweeps:
        raise SystemExit(f"no sweeps under {session_dir}/data/*/metadata.json")

    nb_path = measure_notebook or _find_measure_notebook(session_dir)
    lands = _load_lands(nb_path) if nb_path else []

    span_start = sweeps[0]["start"]
    span_end = max(s["end"] for s in sweeps)
    span = span_end - span_start
    measuring = _merged_measuring(sweeps)

    gaps = []
    human_court = hera_court = 0.0
    for i in range(len(sweeps) - 1):
        end_i = sweeps[i]["end"]
        start_next = sweeps[i + 1]["start"]
        if start_next <= end_i:
            continue  # overlapping/back-to-back: no idle gap
        # lands in the open interval (start_i, start_next) — includes
        # queue-ahead lands made during sweep i; earliest one matters.
        window = [t for t in lands if sweeps[i]["start"] < t < start_next]
        if window:
            first_land = window[0]
            g_human = start_next - max(end_i, first_land)
            g_hera = max(0.0, first_land - end_i)
        else:
            first_land = None
            g_human = 0.0
            g_hera = start_next - end_i
        human_court += g_human
        hera_court += g_hera
        gaps.append(
            {
                "after_sweep": sweeps[i]["id"],
                "idle_s": start_next - end_i,
                "hera_s": g_hera,
                "human_s": g_human,
                "land": first_land,
                "next_slug": sweeps[i + 1]["slug"],
            }
        )

    result = {
        "session_dir": os.path.abspath(session_dir),
        "measure_notebook": nb_path,
        "n_sweeps": len(sweeps),
        "n_lands": len(lands),
        "span_start": span_start,
        "span_end": span_end,
        "span_s": span,
        "measuring_s": measuring,
        "idle_s": span - measuring,
        "hera_court_s": hera_court,
        "human_court_s": human_court,
        "raw_utilization": measuring / span if span > 0 else None,
        "hil_utilization": measuring / (span - human_court)
        if span - human_court > 0
        else None,
        "gaps": gaps,
    }
    return result


def _fmt_clock(epoch: float) -> str:
    return datetime.fromtimestamp(epoch, tz=timezone.utc).strftime("%H:%M:%S")


def _print_table(r: dict) -> None:
    m = r["measuring_s"] / 60
    sp = r["span_s"] / 60
    idle = r["idle_s"] / 60
    print(f"session: {r['session_dir']}")
    print(f"measure nb: {r['measure_notebook'] or '(none found)'}")
    print(f"span {sp:.1f}m | measuring {m:.1f}m | idle {idle:.1f}m")
    print()
    print(f" RAW fridge utilization   {r['raw_utilization']:6.1%}   ({m:.1f} / {sp:.1f} m)")
    if r["n_lands"]:
        print(f" HIL-adjusted             {r['hil_utilization']:6.1%}")
    else:
        print(" HIL-adjusted             --     (no agent-landed proposals in this dir)")
    print()
    print(" gap  after-sweep  end(UTC)     idle    HERA   human   slug(next)")
    for i, g in enumerate(r["gaps"]):
        mark = "" if g["land"] else "   [empty]"
        print(
            f" {i:3d}  {str(g['after_sweep']):>11s}  {_fmt_clock(g['land'] or 0) if g['land'] else '   --   ':>9s}"
            f"  {g['idle_s'] / 60:6.1f}m {g['hera_s'] / 60:6.1f}m {g['human_s'] / 60:6.1f}m"
            f"   {g['next_slug']}{mark}"
        )
    print()
    print(
        f" human court = {r['human_court_s'] / 60:.1f}m | HERA court = {r['hera_court_s'] / 60:.1f}m"
    )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="hera-utilization -- fridge-utilization scoring for a HERA session dir"
    )
    ap.add_argument("session_dir", help="run dir containing data/ and the notebooks")
    ap.add_argument("--measure-notebook", help="override *_measure.ipynb autodiscovery")
    ap.add_argument(
        "--end",
        help="session end bound (ISO timestamp or epoch); sweeps starting after it are excluded",
    )
    ap.add_argument("--json", action="store_true", help="emit structured JSON")
    args = ap.parse_args(argv)

    end = None
    if args.end:
        try:
            end = float(args.end)
        except ValueError:
            end = datetime.fromisoformat(args.end).timestamp()
    result = compute(args.session_dir, args.measure_notebook, end)
    if args.json:
        json.dump(result, sys.stdout, indent=1)
        print()
    else:
        _print_table(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
