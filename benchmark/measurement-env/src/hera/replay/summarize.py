"""`hera-replay summarize <run-dir>`: one row per episode from episodes/*/episode.json,
written to summary.csv and printed."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from hera.replay.errors import CutError

COLUMNS = ("sample", "model", "status", "cost_usd", "turns", "tool_calls", "wall_s", "cells_appended", "stop_cell_sweeps", "stop")


def rows(run_dir: Path) -> list[dict]:
    run_dir = Path(run_dir)
    if not (run_dir / "run.json").is_file():
        raise CutError(f"not a run dir (no run.json): {run_dir}")
    out = []
    for ej in sorted(run_dir.glob("episodes/*/episode.json")):
        episode = json.loads(ej.read_text(encoding="utf-8"))
        r = episode.get("run")
        if r is None:
            raise CutError(f"{ej}: no run block (the episode did not finish)")
        out.append(row(r))
    if not out:
        raise CutError(f"{run_dir}: no finished episodes")
    return out


def row(r: dict) -> dict:
    """One episode's run block as a summary row."""
    stop = r["stop"]
    return {
        "sample": r["sample"],
        "model": ",".join(r["model"]["observed"]) or r["model"]["pinned"],
        "status": r["status"],
        "cost_usd": r["cost_usd"],
        "turns": r["turns"]["api_messages"],
        "tool_calls": r["turns"]["tool_calls"],
        "wall_s": r["wall_s"],
        "cells_appended": r["cells_appended"],
        "stop_cell_sweeps": r.get("stop_cell_sweeps"),
        "stop": "" if stop is None else stop["invocation"],
    }


def write_summary(run_dir: Path) -> Path:
    path = Path(run_dir) / "summary.csv"
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS, lineterminator="\n")
        w.writeheader()
        for r in rows(run_dir):
            w.writerow({k: ("" if r[k] is None else r[k]) for k in COLUMNS})
    return path


def render(run_dir: Path) -> str:
    rs = rows(run_dir)
    widths = {c: max(len(c), *(len(_cell(r[c])) for r in rs)) for c in COLUMNS}
    lines = ["  ".join(c.ljust(widths[c]) for c in COLUMNS)]
    for r in rs:
        lines.append("  ".join(_cell(r[c]).ljust(widths[c]) for c in COLUMNS))
    costs = [r["cost_usd"] for r in rs if r["cost_usd"] is not None]
    statuses = {}
    for r in rs:
        statuses[r["status"]] = statuses.get(r["status"], 0) + 1
    lines.append("")
    lines.append(f"{len(rs)} episodes: " + ", ".join(f"{k} {v}" for k, v in sorted(statuses.items())))
    lines.append(f"cost: ${sum(costs):.2f} over {len(costs)} priced episodes"
                 + (f" (mean ${sum(costs) / len(costs):.2f})" if costs else ""))
    lines.append(f"wall: mean {sum(r['wall_s'] for r in rs) / len(rs):.0f}s, max {max(r['wall_s'] for r in rs):.0f}s")
    return "\n".join(lines)


def _cell(v) -> str:
    if v is None:
        return "-"
    if isinstance(v, float):
        return f"{v:.2f}"
    return str(v)
