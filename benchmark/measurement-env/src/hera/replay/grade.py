"""`hera-replay grade <run-dir>`: grade a run's finished episodes with the case's grader,
each in the image it ran in, as a foreground job's grade item (`hera.replay.jobs`).

An episode counts as graded once it has an extraction dir from that grader whose record
is not an infrastructure ending (quota, interrupted, harness_error), or one still in
flight; `regrade` adds a repeat anyway. Grades land in
`episodes/<id>/grades/<grader>/<stamp>/` (see `hera.grading.runner`); `grades.csv` in
the run dir has one row per extraction, appended under a lock.
"""

from __future__ import annotations

import csv
import fcntl
import json
from pathlib import Path

# `runner` imports `hera.replay.container`, which runs this package's init, which imports
# this module: attributes of `runner` and `jobs` are therefore looked up at call time, never here.
from hera.grading import runner
from hera.replay import jobs
from hera.replay.errors import CutError

COLUMNS = ("sample", "grader", "stamp", "status", "ok", "cost_usd", "turns", "wall_s", "exit")
UNGRADED_EXITS = frozenset(("quota", "interrupted", "harness_error"))


def finished_episodes(run_dir: Path) -> list[Path]:
    run_dir = Path(run_dir)
    if not (run_dir / "run.json").is_file():
        raise CutError(f"not a run dir (no run.json): {run_dir}")
    eps = []
    for ej in sorted(run_dir.glob("episodes/*/episode.json")):
        if "run" in json.loads(ej.read_text(encoding="utf-8")):
            eps.append(ej.parent)
    if not eps:
        raise CutError(f"{run_dir}: no finished episodes")
    return eps


def run_grader(run_dir: Path, grader: str | None) -> str:
    """The grader a grade item uses: the override, else the case's."""
    run_dir = Path(run_dir)
    if not (run_dir / "run.json").is_file():
        raise CutError(f"not a run dir (no run.json): {run_dir}")
    case = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))["case"]
    grader = grader or case.get("grader")
    if not grader:
        raise CutError(f"{run_dir}: the case {case.get('case')!r} names no grader (grader: null); pass --grader to override")
    return grader


def graded(episode_dir: Path, grader: str) -> bool:
    for d in sorted((Path(episode_dir) / "grades" / grader).glob("*")):
        rec = d / "run.json"
        if not rec.exists():
            return True
        try:
            if (json.loads(rec.read_text(encoding="utf-8")).get("claude") or {}).get("exit") not in UNGRADED_EXITS:
                return True
        except json.JSONDecodeError:
            return True
    return False


def select_episodes(run_dir: Path, grader: str, *, regrade: bool = False) -> list[Path]:
    eps = finished_episodes(run_dir)
    if regrade:
        return eps
    todo = [ep for ep in eps if not graded(ep, grader)]
    if not todo:
        raise CutError(f"{run_dir}: every finished episode has a {grader} grade; --regrade adds a repeat")
    return todo


def grade_run(run_dir: Path, *, n: int = 1, parallel: int = 4, grader: str | None = None, regrade: bool = False,
              **kw) -> list[dict]:
    run_dir = Path(run_dir)
    grader = run_grader(run_dir, grader)
    select_episodes(run_dir, grader, regrade=regrade)
    item = jobs.GradeItem(run_dir, grader=grader, n=n, regrade=regrade, parallel=parallel, **kw)
    jobs.run_foreground([item], label=f"grade {run_dir.parent.name}/{run_dir.name}", check_orphans=False)
    return item.records()


def append_rows(run_dir: Path, grader: str, graded_jobs: list, records: list[dict]) -> None:
    with (Path(run_dir) / "grades.csv").open("a", encoding="utf-8", newline="") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        w = csv.DictWriter(fh, fieldnames=COLUMNS, lineterminator="\n")
        fh.seek(0, 2)
        if fh.tell() == 0:
            w.writeheader()
        for job, rec in zip(graded_jobs, records):
            s, c = rec["scores"], rec["claude"]
            w.writerow({"sample": job.episode_dir.name, "grader": grader, "stamp": job.run_dir.name,
                        "status": s.get("status"), "ok": "" if s.get("ok") is None else s["ok"],
                        "cost_usd": "" if c.get("cost_usd") is None else c["cost_usd"], "turns": c.get("turns") or "",
                        "wall_s": c.get("wall_s") or "", "exit": c.get("exit")})


def render(records: list[dict]) -> str:
    return runner.summarize(records)
