"""`hera-replay cell <case>`: a cell's sample is the union of its run dirs.

Run dirs pool when their pool key matches: the case as run (run.json's parsed case
block, path aside, plus any override), the image id, the first message's sha256, and
the cut digest (the materialized episode, less what each materialization mints:
`created_at` and a resume cut's synthetic close-line uuid). A
differing `harness.code_hash` is reported, never a split. Each pool's rows are written
to `$HERA_DATA/replay/cells/<case>/<key12>/{summary,grades}.csv` with a `run` column.
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

from hera.replay import summarize
from hera.replay.errors import CutError

KEY_PARTS = ("case", "image", "first_message", "cut")


def _sha(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def cut_digest(cut: Path) -> str | None:
    cut = Path(cut)
    if not (cut / "episode.json").is_file():
        return None
    h = hashlib.sha256()
    episode = json.loads((cut / "episode.json").read_text(encoding="utf-8"))
    episode.pop("created_at", None)
    close = (episode.get("resume") or {}).pop("close_uuid", None)
    h.update(_sha(episode).encode())
    for p in sorted(cut.rglob("*")):
        if p.is_file() and p != cut / "episode.json":
            data = p.read_bytes()
            if close:
                data = data.replace(close.encode(), b"<close>")
            h.update(p.relative_to(cut).as_posix().encode() + b"\0" + data + b"\0")
    return h.hexdigest()


def pool_key(run: dict) -> dict:
    case = {k: v for k, v in run["case"].items() if k != "path"}
    return {"case": _sha({"case": case, "override": run.get("override")}),
            "image": (run.get("image") or {}).get("id"),
            "first_message": ((run.get("start") or {}).get("first_message") or {}).get("sha256"),
            "cut": cut_digest(Path(run["episode_source"]["dir"]))}


def run_dirs(hera_data: Path, case_name: str) -> list[Path]:
    return sorted(p for p in (Path(hera_data) / "replay" / "runs" / case_name).glob("*") if (p / "run.json").is_file())


def pools(hera_data: Path, case_name: str) -> list[dict]:
    """Pools of one case's run dirs, newest pool first; each with its run dirs, rows and grades."""
    groups: dict[str, dict] = {}
    for rd in run_dirs(hera_data, case_name):
        run = json.loads((rd / "run.json").read_text(encoding="utf-8"))
        key = pool_key(run)
        g = groups.setdefault(_sha(key), {"key": key, "id": _sha(key)[:12], "runs": [], "rows": [], "grades": [],
                                          "in_flight": 0, "code_hashes": set(), "override": run.get("override")})
        g["runs"].append(rd)
        g["code_hashes"].add((run.get("harness") or {}).get("code_hash"))
        for ej in sorted(rd.glob("episodes/*/episode.json")):
            r = json.loads(ej.read_text(encoding="utf-8")).get("run")
            if r is None:
                g["in_flight"] += 1
            else:
                g["rows"].append({"run": rd.name, **summarize.row(r)})
        if (rd / "grades.csv").exists():
            with (rd / "grades.csv").open(encoding="utf-8", newline="") as fh:
                g["grades"].extend({"run": rd.name, **row} for row in csv.DictReader(fh))
    return sorted(groups.values(), key=lambda g: g["runs"][-1].name, reverse=True)


def write(hera_data: Path, case_name: str, group: dict) -> Path:
    out = Path(hera_data) / "replay" / "cells" / case_name / group["id"]
    out.mkdir(parents=True, exist_ok=True)
    with (out / "summary.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=("run", *summarize.COLUMNS), lineterminator="\n")
        w.writeheader()
        for r in group["rows"]:
            w.writerow({k: ("" if r[k] is None else r[k]) for k in ("run", *summarize.COLUMNS)})
    if group["grades"]:
        with (out / "grades.csv").open("w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(group["grades"][0]), lineterminator="\n", extrasaction="ignore")
            w.writeheader()
            w.writerows(group["grades"])
    (out / "key.json").write_text(json.dumps({"case": case_name, "key": group["key"],
                                              "runs": [p.name for p in group["runs"]]}, indent=2) + "\n", encoding="utf-8")
    return out


def render(hera_data: Path, case_name: str) -> str:
    groups = pools(hera_data, case_name)
    if not groups:
        raise CutError(f"no run dirs for {case_name} under {Path(hera_data) / 'replay' / 'runs'}")
    lines = [f"{case_name}: {sum(len(g['runs']) for g in groups)} run dirs in {len(groups)} pool(s)"]
    for g in groups:
        k = g["key"]
        lines.append("")
        lines.append(f"pool {g['id']}: " + "  ".join(f"{p} {str(k[p])[:19] if k[p] else '-'}" for p in KEY_PARTS)
                     + (f"  override {g['override']}" if g["override"] else ""))
        for rd in g["runs"]:
            n = sum(1 for r in g["rows"] if r["run"] == rd.name)
            lines.append(f"    {rd.name}  {n} finished")
        statuses: dict[str, int] = {}
        for r in g["rows"]:
            statuses[r["status"]] = statuses.get(r["status"], 0) + 1
        costs = [r["cost_usd"] for r in g["rows"] if r["cost_usd"] is not None]
        lines.append(f"  episodes {len(g['rows'])}: " + (", ".join(f"{s} {c}" for s, c in sorted(statuses.items())) or "-")
                     + (f"; {g['in_flight']} unfinished" if g["in_flight"] else "")
                     + f"; cost ${sum(costs):.2f}")
        if g["grades"]:
            by: dict[str, int] = {}
            for r in g["grades"]:
                key = f"{r.get('grader')} {r.get('status')}"
                by[key] = by.get(key, 0) + 1
            lines.append("  grades: " + ", ".join(f"{s} {c}" for s, c in sorted(by.items())))
        if len(g["code_hashes"]) > 1:
            lines.append(f"  harness code_hash differs across the pool: {len(g['code_hashes'])} values")
        lines.append(f"  written: {write(hera_data, case_name, g)}")
    return "\n".join(lines)
