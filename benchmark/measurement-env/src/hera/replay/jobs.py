"""Replay jobs: `hera-replay submit / wait / status / cancel / reap`, and the foreground
job under `run` and `grade`.

A job is one submission: a list of items, each the episodes of one cell (one run dir)
or the extractions over a run dir's finished, ungraded episodes. Every job is its own
process — detached under `systemd-run --user` for `submit`, the caller's for `run` and
`grade` — and holds an item's slots in the host-wide lock-file pools (`claude`,
`codex`, `host`) for the item's lifetime; a lock dies with its process. Each job's
dispatcher starts at most one item per tick, so live jobs share the pools.

Machine-local state (never `$HERA_DATA`, which is a Syncthing folder):
    ~/.config/hera/replay.toml                 pool sizes (claude, codex, host)
    ~/.local/state/hera/replay/jobs/<id>/      job.json (spec, lease, containers, items), job.log
    ~/.local/state/hera/replay/quota.jsonl     quota readings
    $XDG_RUNTIME_DIR/hera-replay/slots/<pool>/<k>.lock
"""

from __future__ import annotations

import fcntl
import hashlib
import json
import os
import random
import shutil
import signal
import socket
import subprocess
import sys
import threading
import time
import tomllib
import traceback
from collections import deque
from datetime import datetime, timezone
from pathlib import Path

import yaml

from hera.grading import runner
from hera.replay import codex, container, grade, quota, run, summarize
from hera.replay.case import EFFORTS, load_case
from hera.replay.errors import CutError

SCHEMA = "hera-replay-job/1"
DEFAULT_POOLS = {"claude": 8, "codex": 4, "host": 12}
ALL = -1  # a slot count meaning the whole pool
TICK_S = 0.25
LEASE_WAIT_S = 60.0
TERMINAL = ("done", "interrupted", "failed", "died")
REFRESH_MARGIN_S = 86400
GRADE_DEFAULTS = {"model": "claude-opus-5", "effort": "medium"}
EPISODE_KEYS = {"case", "n", "parallel", "model", "effort"}
GRADE_KEYS = {"grade", "grader", "n", "parallel", "model", "effort", "regrade"}
# Passed to a detached job by name: systemd-run reads the values from this environment,
# so no credential lands on a command line.
PASSED_ENV = ("HERA_DATA", "HERA_GRADERS", "HERA_GRADER_IMAGE", "CLAUDE_CODE_OAUTH_TOKEN", "ANTHROPIC_API_KEY",
              "CODEX_API_KEY", "CODEX_HOME", "XDG_CONFIG_HOME", "XDG_STATE_HOME", "XDG_RUNTIME_DIR", "PATH")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# ------------------------------------------------------------------ local state
def config_path() -> Path:
    return Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config") / "hera" / "replay.toml"


def state_dir() -> Path:
    return Path(os.environ.get("XDG_STATE_HOME") or Path.home() / ".local" / "state") / "hera" / "replay"


def jobs_dir() -> Path:
    return state_dir() / "jobs"


def quota_log_path() -> Path:
    return state_dir() / "quota.jsonl"


def slots_dir() -> Path:
    runtime = os.environ.get("XDG_RUNTIME_DIR") or f"/tmp/hera-replay-{os.getuid()}"
    return Path(runtime) / "hera-replay" / "slots"


def load_pools() -> dict[str, int]:
    pools = dict(DEFAULT_POOLS)
    path = config_path()
    if path.exists():
        conf = tomllib.loads(path.read_text(encoding="utf-8"))
        conf = conf.get("pools", conf)
        for k, v in conf.items():
            if k not in DEFAULT_POOLS or not isinstance(v, int) or v < 1:
                raise CutError(f"{path}: pools are {sorted(DEFAULT_POOLS)} with sizes >= 1, not {k} = {v!r}")
            pools[k] = v
    return pools


# ------------------------------------------------------------------ leases
def boot_id() -> str:
    return Path("/proc/sys/kernel/random/boot_id").read_text().strip()


def proc_start(pid: int) -> int | None:
    """The process's start time in clock ticks since boot: a reused pid differs."""
    try:
        stat = Path(f"/proc/{pid}/stat").read_text()
    except OSError:
        return None
    return int(stat.rsplit(")", 1)[1].split()[19])


def make_lease(unit: str | None) -> dict:
    pid = os.getpid()
    return {"pid": pid, "start": proc_start(pid), "boot_id": boot_id(), "host": socket.gethostname(), "unit": unit}


def lease_alive(lease: dict | None) -> bool:
    if not lease:
        return False
    return (lease.get("host") == socket.gethostname() and lease.get("boot_id") == boot_id()
            and proc_start(lease["pid"]) == lease.get("start"))


def job_live(rec: dict) -> bool:
    return rec.get("state") not in TERMINAL and lease_alive(rec.get("lease"))


# ------------------------------------------------------------------ slot pools
class Held:
    """Slot locks one item holds; released when the item ends or its process dies."""

    def __init__(self):
        self.fds: list[int] = []
        self.slots: dict[str, list[int]] = {}

    def release(self) -> None:
        for fd in self.fds:
            os.close(fd)
        self.fds.clear()


def try_acquire(needs: list[tuple[str, int]], sizes: dict[str, int]) -> Held | None:
    """Every slot `needs` names, or none: a non-blocking try that never deadlocks."""
    held = Held()
    for pool, count in needs:
        size = sizes[pool]
        want = size if count == ALL else count
        d = slots_dir() / pool
        d.mkdir(parents=True, exist_ok=True)
        got = []
        for k in random.sample(range(size), size):
            fd = os.open(d / f"{k}.lock", os.O_RDWR | os.O_CREAT, 0o600)
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                os.close(fd)
                continue
            held.fds.append(fd)
            got.append(k)
            if len(got) == want:
                break
        if len(got) < want:
            held.release()
            return None
        held.slots[pool] = sorted(got)
    return held


# ------------------------------------------------------------------ job records
def read_job(job_id: str) -> dict:
    path = jobs_dir() / job_id / "job.json"
    if not path.is_file():
        raise CutError(f"no job {job_id} (looked in {jobs_dir()})")
    return json.loads(path.read_text(encoding="utf-8"))


def list_jobs() -> list[dict]:
    out = []
    for path in sorted(jobs_dir().glob("*/job.json")):
        try:
            out.append(json.loads(path.read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError):
            continue
    return out


class Job:
    def __init__(self, record: dict):
        self.record = record
        self.dir = jobs_dir() / record["id"]
        self.stop = threading.Event()
        self.wake = threading.Event()
        self._lock = threading.RLock()

    @classmethod
    def create(cls, *, label: str | None, spec: dict | None, mode: str, parallel: int | None = None) -> "Job":
        job_id = container.stamp()
        d = jobs_dir() / job_id
        d.mkdir(parents=True)
        raw = json.dumps(spec, sort_keys=True).encode()
        job = cls({"schema": SCHEMA, "id": job_id, "label": label, "mode": mode, "state": "queued", "error": None,
                   "created_at": now_iso(), "started_at": None, "ended_at": None,
                   "submitter": {"cwd": os.getcwd(), "host": socket.gethostname()},
                   "spec": spec, "spec_sha256": hashlib.sha256(raw).hexdigest() if spec is not None else None,
                   "parallel": parallel, "pools": load_pools(), "lease": None, "harness": None,
                   "containers": [], "items": []})
        job.save()
        return job

    @classmethod
    def load(cls, job_id: str) -> "Job":
        return cls(read_job(job_id))

    @property
    def id(self) -> str:
        return self.record["id"]

    @property
    def log_path(self) -> Path:
        return self.dir / "job.log"

    def info(self) -> dict:
        return {"id": self.id, "label": self.record["label"], "host": socket.gethostname()}

    def save(self) -> None:
        with self._lock:
            tmp = self.dir / ".job.json.tmp"
            tmp.write_text(json.dumps(self.record, indent=2) + "\n", encoding="utf-8")
            os.replace(tmp, self.dir / "job.json")

    def update(self, **kw) -> None:
        with self._lock:
            self.record.update(kw)
            self.save()

    def add_containers(self, names: list[str]) -> None:
        """Listed before `docker run`, so the lease covers a container from its first moment."""
        with self._lock:
            self.record["containers"].extend(names)
            self.save()

    def log(self, msg: str) -> None:
        with self._lock, self.log_path.open("a", encoding="utf-8") as fh:
            fh.write(f"{now_iso()} {msg}\n")

    def sync(self, items: list) -> None:
        with self._lock:
            self.record["items"] = [it.summary() for it in items]
            self.save()


# ------------------------------------------------------------------ orphans
def orphans() -> list[str]:
    """Episode and extraction containers no live job lists: their harness is gone and
    an agent inside may still be spending quota."""
    names = container.replay_containers()
    if not names:
        return []
    owned = {n for rec in list_jobs() if job_live(rec) for n in rec.get("containers", [])}
    return [n for n in names if n not in owned]


def check_orphans() -> None:
    found = orphans()
    if found:
        raise CutError("containers from another run exist that no live job lists (its harness was killed): "
                       + ", ".join(found) + "\n    stop and remove them with: hera-replay reap")


# ------------------------------------------------------------------ items
class Item:
    """A queue of units (samples, extractions) sharing one cap and one set of slot needs."""

    kind = ""

    def __init__(self, parallel: int | None):
        self.cap = parallel
        self.queued: deque = deque()
        self.running: dict = {}  # unit -> slots held
        self.results: dict = {}  # unit -> status
        self.state = "queued"
        self.error: str | None = None
        self.exc: BaseException | None = None
        self.expanded = False
        self.job: Job | None = None

    # the dispatcher's interface
    def prepare(self, job: Job) -> None:
        self.job = job

    def expand(self) -> None:
        self.expanded = True

    def needs(self, unit) -> list[tuple[str, int]]:
        raise NotImplementedError

    def names(self, unit) -> list[str]:
        return []

    def run(self, unit) -> str:
        raise NotImplementedError

    def cancel(self, unit) -> None:
        self.results[unit] = "cancelled"

    def finish(self) -> None:
        pass

    def fail(self, err: BaseException) -> None:
        self.state = "failed"
        self.exc = err
        self.error = f"{type(err).__name__}: {err}"
        self.queued.clear()

    def summary(self) -> dict:
        counts: dict[str, int] = {}
        for st in self.results.values():
            counts[st] = counts.get(st, 0) + 1
        return {"kind": self.kind, "label": self.label(), "run_dir": self.run_dir_str(), "state": self.state,
                "error": self.error, "queued": len(self.queued), "running": len(self.running),
                "done": len(self.results), "statuses": counts,
                "slots": {str(u): s for u, s in self.running.items()}}

    def label(self) -> str:
        return ""

    def run_dir_str(self) -> str | None:
        return None


class EpisodeItem(Item):
    """N episodes of one cell into a new run dir."""

    kind = "episodes"

    def __init__(self, case, *, n: int | None = None, parallel: int | None = None, hera_data: Path | None = None,
                 model: str | None = None, effort: str | None = None):
        super().__init__(parallel)
        self.case, self.n, self.model, self.effort = case, n, model, effort
        self.hera_data = Path(hera_data) if hera_data else run.hera_data_root()
        self.ctx: dict = {}
        self.readings: dict[str, list[dict]] = {}

    def prepare(self, job: Job) -> None:
        super().prepare(job)
        self.ctx = run.prepare_run(self.case, n=self.n, parallel=self.cap, hera_data=self.hera_data, model=self.model,
                                   effort=self.effort, harness=job.record["harness"], job=job.info(), tee=job.log_path)
        self.ctx["stop"] = job.stop
        self.ctx["on_event"] = self._on_event
        self.queued.extend(self.ctx["ids"])
        self.expanded = True

    def label(self) -> str:
        return self.case.name + (f" @{self.model}" if self.model and self.model != self.case.model else "")

    def run_dir_str(self) -> str | None:
        return str(self.ctx["run_dir"]) if self.ctx else None

    def needs(self, sid) -> list[tuple[str, int]]:
        runner_pool = self.ctx["case"].runner
        if runner_pool == "codex" and codex_refresh_due():
            return [("codex", ALL), ("host", 1)]
        return [(runner_pool, 1), ("host", 1)]

    def names(self, sid) -> list[str]:
        return [run.container_name(self.ctx["case"], self.ctx["ts"], sid)]

    def _on_event(self, sid: str, ev: dict) -> None:
        r = quota.claude_reading(ev)
        if r:
            r["t"] = now_iso()
            self.readings.setdefault(sid, []).append(r)
            quota.append(quota_log_path(), quota.item_lines([r], runner="claude", model=None, cost_usd=None,
                                                             source=self._source(sid), job=self.job.id)[:1])

    def _source(self, sid: str) -> dict:
        return {"run_dir": str(self.ctx["run_dir"]), "sample": sid}

    def run(self, sid) -> str:
        status = run.run_episode(self.ctx, sid)
        self._record_quota(sid)
        return status

    def _record_quota(self, sid: str) -> None:
        try:
            ep = self.ctx["run_dir"] / "episodes" / sid
            rec = json.loads((ep / "episode.json").read_text(encoding="utf-8"))["run"]
            case = self.ctx["case"]
            if case.runner == "codex":
                rollout = (rec.get("rollout") or {}).get("path")
                readings = quota.codex_readings(ep / rollout) if rollout else []
                lines = quota.item_lines(readings, runner="codex", model=case.model, cost_usd=rec.get("cost_usd"),
                                         source=self._source(sid), job=self.job.id)
            else:
                # The readings are logged live; only the item line remains.
                lines = quota.item_lines(self.readings.get(sid, []), runner="claude", model=case.model,
                                         cost_usd=rec.get("cost_usd"), source=self._source(sid), job=self.job.id)[-1:]
            quota.append(quota_log_path(), lines)
        except (OSError, KeyError, ValueError) as err:
            self.job.log(f"quota readings for {self.case.name} [{sid}] not recorded: {err}")

    def cancel(self, sid) -> None:
        self.ctx["log"](f"[{sid}] cancelled")
        super().cancel(sid)

    def finish(self) -> None:
        if not self.ctx:
            return
        run.finish_run(self.ctx, {sid: self.results.get(sid, "cancelled") for sid in self.ctx["ids"]})


class ExtractionItem(Item):
    """Grader extractions over fixed `runner.Job`s; each takes a claude slot."""

    kind = "extractions"

    def __init__(self, jobs: list | None = None, *, parallel: int | None = None):
        super().__init__(parallel)
        self.jobs = list(jobs or [])
        self.shared: dict = {}
        self._records: dict[int, dict] = {}

    def label(self) -> str:
        return self.jobs[0].grader if self.jobs else ""

    def expand(self) -> None:
        self.shared = runner.prepare_shared(self.jobs)
        self.queued.extend(range(len(self.jobs)))
        self.expanded = True

    def needs(self, i) -> list[tuple[str, int]]:
        return [("claude", 1), ("host", 1)]

    def names(self, i) -> list[str]:
        return [self.jobs[i].name]

    def run(self, i) -> str:
        job = self.jobs[i]
        rec = runner.grade_job(job, self.shared, stop=self.job.stop)
        self._records[i] = rec
        self.job.log(f"[grade {job.episode_dir.name} {job.run_dir.name}] {rec['claude']['exit']} "
                     f"{rec['scores'].get('status')} cost={rec['claude'].get('cost_usd')}")
        lines = quota.item_lines(quota.claude_readings(job.run_dir / "transcript.jsonl"), runner="claude",
                                 model=job.model, cost_usd=rec["claude"].get("cost_usd"),
                                 source={"grade": str(job.run_dir)}, job=self.job.id)
        quota.append(quota_log_path(), lines)
        return rec["claude"]["exit"]

    def records(self) -> list[dict]:
        return [self._records[i] for i in sorted(self._records)]


class GradeItem(ExtractionItem):
    """A run dir's finished episodes that have no grade from the grader yet (all
    finished ones with `regrade`), chosen when the item is first dispatched."""

    kind = "grade"

    def __init__(self, run_dir: Path, *, grader: str | None = None, n: int = 1, regrade: bool = False,
                 parallel: int | None = None, **kw):
        super().__init__(parallel=parallel)
        self.run_dir, self.grader_arg, self.n, self.regrade, self.kw = Path(run_dir), grader, n, regrade, kw
        self.grader: str | None = None

    def label(self) -> str:
        return f"grade {self.grader or self.grader_arg or '?'}"

    def run_dir_str(self) -> str | None:
        return str(self.run_dir)

    def prepare(self, job: Job) -> None:
        super().prepare(job)
        self.grader = grade.run_grader(self.run_dir, self.grader_arg)

    def expand(self) -> None:
        eps = grade.select_episodes(self.run_dir, self.grader, regrade=self.regrade)
        try:
            self.jobs = runner.make_jobs(eps, self.grader, n=self.n, **self.kw)
        except runner.GradeError as err:
            raise CutError(str(err)) from None
        super().expand()

    def finish(self) -> None:
        if self.jobs and self._records:
            ran = sorted(self._records)
            grade.append_rows(self.run_dir, self.grader, [self.jobs[i] for i in ran], [self._records[i] for i in ran])


def codex_refresh_due() -> bool:
    """The harness login's access token expires within a day: its refresh must run alone."""
    if os.environ.get("CODEX_API_KEY") or not container.CODEX_AUTH_FILE.exists():
        return False
    exp = codex.access_expires_at(container.CODEX_AUTH_FILE.read_bytes())
    return exp is not None and exp - time.time() < REFRESH_MARGIN_S


# ------------------------------------------------------------------ the dispatcher
def execute(job: Job, items: list[Item]) -> None:
    """Start queued units as their slots free up — at most one per tick, rotating across
    the job's items — until every unit has ended. A stop cancels what is queued; the
    in-flight units see the same event and end as `interrupted`."""
    sizes = job.record["pools"]
    cap = job.record.get("parallel")
    lock = threading.Lock()
    threads: list[threading.Thread] = []
    rr = 0

    def body(item: Item, unit, held: Held) -> None:
        try:
            status = item.run(unit)
        except Exception:
            job.log(f"{item.label()} [{unit}] harness error: " + traceback.format_exc().rstrip())
            status = "error"
        finally:
            held.release()
        with lock:
            item.running.pop(unit, None)
            item.results[unit] = status
        job.sync(items)
        job.wake.set()

    while True:
        with lock:
            if job.stop.is_set():
                for item in items:
                    item.expanded = True  # an item not yet expanded has nothing to cancel
                    while item.queued:
                        item.cancel(item.queued.popleft())
            active = sum(len(it.running) for it in items)
            if active == 0 and not any(it.queued for it in items) and all(it.expanded or it.state == "failed" for it in items):
                break
        if not job.stop.is_set() and (cap is None or active < cap):
            for j in range(len(items)):
                item = items[(rr + j) % len(items)]
                if item.state == "failed":
                    continue
                if not item.expanded:
                    try:
                        item.expand()
                    except Exception as err:
                        item.fail(err)
                        job.log(f"{item.label()}: {item.error}")
                        job.sync(items)
                        continue
                    job.sync(items)
                if not item.queued or (item.cap is not None and len(item.running) >= item.cap):
                    continue
                held = try_acquire(item.needs(item.queued[0]), sizes)
                if held is None:
                    continue
                with lock:
                    unit = item.queued.popleft()
                    item.running[unit] = held.slots
                    item.state = "running"
                job.add_containers(item.names(unit))
                t = threading.Thread(target=body, args=(item, unit, held), daemon=True)
                t.start()
                threads.append(t)
                job.sync(items)
                rr = (rr + j + 1) % len(items)
                break
        job.wake.wait(TICK_S)
        job.wake.clear()
    for t in threads:
        t.join()
    for item in items:
        if item.state != "failed":
            try:
                item.finish()
            except Exception as err:
                item.fail(err)
            else:
                item.state = "interrupted" if job.stop.is_set() and (
                    "cancelled" in item.results.values() or "interrupted" in item.results.values()) else "done"
    job.sync(items)
    for i, item in enumerate(items):
        if isinstance(item, ExtractionItem):
            (job.dir / f"records-{i}.json").write_text(json.dumps(item.records(), indent=2) + "\n", encoding="utf-8")


def _begin(job: Job, unit: str | None) -> None:
    job.update(state="running", started_at=now_iso(), lease=make_lease(unit), harness=run.harness_provenance())


def _end(job: Job, items: list[Item]) -> str:
    state = ("failed" if any(it.state == "failed" for it in items)
             else "interrupted" if job.stop.is_set() else "done")
    job.update(state=state, ended_at=now_iso(),
               error=next((it.error for it in items if it.error), job.record.get("error")))
    job.log(f"job {state}")
    return state


def _prepare(job: Job, items: list[Item]) -> None:
    """Every item before any launch: a bad cut fails the job before anything is spent.
    A failure removes the run dirs this job prepared (they hold no episodes)."""
    try:
        for item in items:
            item.prepare(job)
            job.sync(items)
    except BaseException:
        for item in items:
            if isinstance(item, EpisodeItem) and item.ctx and not (item.ctx["run_dir"] / "episodes").exists():
                shutil.rmtree(item.ctx["run_dir"], ignore_errors=True)
        raise


def _stop_logger(items: list[Item], job: Job):
    def log(msg: str) -> None:
        job.log(msg)
        for item in items:
            if isinstance(item, EpisodeItem) and item.ctx:
                item.ctx["log"](msg)
    return log


def run_foreground(items: list[Item], *, label: str, parallel: int | None = None, check_orphans: bool = True) -> Job:
    """A job in this process (`run`, `grade`, `hera-grade`): same lease, pools and record
    as a submitted one. A preparation error, or an item that fails to expand, is raised
    to the caller after the job is recorded."""
    job = Job.create(label=label, spec=None, mode="foreground", parallel=parallel)
    _begin(job, None)
    try:
        if check_orphans:
            check_orphans_fn()
        _prepare(job, items)
        with run.stop_on_signal(job.stop, _stop_logger(items, job), wake=job.wake):
            execute(job, items)
    except BaseException as err:
        job.update(state="failed", ended_at=now_iso(), error=f"{type(err).__name__}: {err}")
        raise
    _end(job, items)
    failed = next((it.exc for it in items if it.exc is not None), None)
    if failed is not None:
        raise failed
    return job


check_orphans_fn = check_orphans


# ------------------------------------------------------------------ specs
def _abs(value: str, base: Path) -> Path:
    p = Path(os.path.expanduser(os.path.expandvars(str(value))))
    return p if p.is_absolute() else (base / p)


def normalize_spec(spec: dict, *, base: Path) -> dict:
    """Validate a spec and resolve its paths; what the job process runs."""
    if not isinstance(spec, dict) or not isinstance(spec.get("items"), list) or not spec["items"]:
        raise CutError("a spec is a mapping with a non-empty `items` list")
    unknown = set(spec) - {"label", "parallel", "items"}
    if unknown:
        raise CutError(f"spec: unknown keys {sorted(unknown)}")
    out = {"label": spec.get("label"), "parallel": _positive(spec.get("parallel"), "parallel"), "items": []}
    for i, it in enumerate(spec["items"]):
        where = f"spec item {i}"
        if not isinstance(it, dict) or ("case" in it) == ("grade" in it):
            raise CutError(f"{where}: each item names exactly one of `case` or `grade`")
        keys = EPISODE_KEYS if "case" in it else GRADE_KEYS
        if set(it) - keys:
            raise CutError(f"{where}: unknown keys {sorted(set(it) - keys)} (allowed: {sorted(keys)})")
        if it.get("effort") is not None and it["effort"] not in EFFORTS:
            raise CutError(f"{where}: effort must be one of {EFFORTS}, not {it['effort']!r}")
        norm = {k: v for k, v in it.items() if v is not None}
        for k in ("n", "parallel"):
            if k in norm:
                norm[k] = _positive(norm[k], f"{where}: {k}")
        if "case" in it:
            path = _abs(it["case"], base)
            load_case(path)
            norm["case"] = str(path)
        else:
            path = _abs(it["grade"], base)
            grade.run_grader(path, it.get("grader"))
            norm["grade"] = str(path)
            if "regrade" in norm and not isinstance(norm["regrade"], bool):
                raise CutError(f"{where}: regrade is true or false")
        out["items"].append(norm)
    return out


def _positive(v, what: str) -> int | None:
    if v is None:
        return None
    if not isinstance(v, int) or isinstance(v, bool) or v < 1:
        raise CutError(f"{what} must be an integer >= 1, not {v!r}")
    return v


def items_from_spec(spec: dict) -> list[Item]:
    items: list[Item] = []
    for it in spec["items"]:
        if "case" in it:
            items.append(EpisodeItem(load_case(Path(it["case"])), n=it.get("n"), parallel=it.get("parallel"),
                                     model=it.get("model"), effort=it.get("effort")))
        else:
            items.append(GradeItem(Path(it["grade"]), grader=it.get("grader"), n=it.get("n", 1),
                                   regrade=it.get("regrade", False), parallel=it.get("parallel"),
                                   model=it.get("model", GRADE_DEFAULTS["model"]),
                                   effort=it.get("effort", GRADE_DEFAULTS["effort"])))
    return items


def load_spec_file(path: Path) -> dict:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if isinstance(data, dict) and "case" in data and "items" not in data:
        raise CutError(f"{path} is a case file; submit it as `hera-replay submit {path} --n N`")
    return data


# ------------------------------------------------------------------ submit / the detached job
def unit_name(job_id: str) -> str:
    return f"hera-replay-job-{job_id}"


def submit(spec: dict, *, base: Path) -> str:
    """Validate, record, and start the job under `systemd-run --user`; returns its id."""
    spec = normalize_spec(spec, base=base)
    check_orphans_fn()
    job = Job.create(label=spec["label"], spec=spec, mode="detached", parallel=spec["parallel"])
    unit = unit_name(job.id)
    argv = ["systemd-run", "--user", "--quiet", "--collect", f"--unit={unit}",
            f"--working-directory={run.REPO_ROOT}",
            f"--property=StandardOutput=append:{job.dir / 'console.log'}",
            f"--property=StandardError=append:{job.dir / 'console.log'}",
            *(f"--setenv={k}" for k in PASSED_ENV if k in os.environ),
            sys.executable, "-m", "hera.replay", "_job", job.id]
    job.update(unit=unit, systemd_run=argv)
    proc = subprocess.run(argv, capture_output=True, text=True)
    if proc.returncode:
        job.update(state="failed", ended_at=now_iso(), error=f"systemd-run failed: {(proc.stderr or proc.stdout).strip()}")
        raise CutError(f"systemd-run failed ({proc.returncode}): {(proc.stderr or proc.stdout).strip()}")
    return job.id


def run_detached(job_id: str) -> int:
    """The job process `submit` starts."""
    job = Job.load(job_id)
    _begin(job, job.record.get("unit"))
    items = items_from_spec(job.record["spec"])
    try:
        check_orphans_fn()
        _prepare(job, items)
    except Exception as err:
        job.update(state="failed", ended_at=now_iso(), error=f"{type(err).__name__}: {err}")
        job.log(f"job failed before any launch: {type(err).__name__}: {err}")
        return 1
    with run.stop_on_signal(job.stop, _stop_logger(items, job), wake=job.wake):
        execute(job, items)
    return {"done": 0, "interrupted": 130}.get(_end(job, items), 1)


# ------------------------------------------------------------------ wait / status / cancel / reap
def _print(line: str) -> None:
    print(line, flush=True)


def wait(job_id: str, *, out=_print, poll_s: float = 2.0) -> int:
    """Stream the job's log until it ends, then its per-item summary. 0 done, 130
    interrupted, 1 otherwise."""
    rec = read_job(job_id)
    log = jobs_dir() / job_id / "job.log"
    offset = 0
    t0 = time.monotonic()
    while True:
        if log.exists():
            with log.open(encoding="utf-8") as fh:
                fh.seek(offset)
                chunk = fh.read()
                offset = fh.tell()
            if chunk:
                out(chunk.rstrip("\n"))
        rec = read_job(job_id)
        if rec["state"] in TERMINAL:
            break
        if rec.get("lease") and not lease_alive(rec["lease"]):
            rec["state"] = "died"
            break
        if rec.get("lease") is None and time.monotonic() - t0 > LEASE_WAIT_S:
            rec["state"], rec["error"] = "died", f"the job process never started ({rec.get('unit')})"
            break
        time.sleep(poll_s)
    out("")
    out(render_items(rec))
    out(f"job {job_id}: {rec['state']}" + (f" — {rec['error']}" if rec.get("error") else ""))
    return {"done": 0, "interrupted": 130}.get(rec["state"], 1)


def render_items(rec: dict) -> str:
    lines = []
    for i, it in enumerate(rec.get("items", [])):
        lines.append(f"[{i}] {it['kind']} {it['label']}: {it['state']}" + (f" — {it['error']}" if it.get("error") else ""))
        rd = Path(it["run_dir"]) if it.get("run_dir") else None
        if it["kind"] == "episodes" and rd and (rd / "summary.csv").exists():
            lines.append(summarize.render(rd))
            lines.append(f"run dir: {rd}")
        records = jobs_dir() / rec["id"] / f"records-{i}.json"
        if it["kind"] in ("grade", "extractions") and records.exists():
            recs = json.loads(records.read_text(encoding="utf-8"))
            if recs:
                lines.append(runner.summarize(recs))
            if it["kind"] == "grade":
                lines.append(f"table: {rd / 'grades.csv'}")
    return "\n".join(lines)


def _pool_use(recs: list[dict]) -> dict[str, int]:
    use = {k: 0 for k in DEFAULT_POOLS}
    for rec in recs:
        for it in rec.get("items", []):
            for slots in it.get("slots", {}).values():
                for pool, ks in slots.items():
                    use[pool] = use.get(pool, 0) + len(ks)
    return use


def status_text(job_id: str | None = None, *, recent: int = 5) -> str:
    if job_id:
        rec = read_job(job_id)
        live = job_live(rec)
        state = rec["state"] if live or rec["state"] in TERMINAL or rec.get("lease") is None else "died"
        lines = [f"job {rec['id']} ({rec.get('label') or '-'}): {state}, {rec['mode']}, created {rec['created_at']}"
                 + (f", unit {rec['unit']}" if rec.get("unit") else "")]
        for i, it in enumerate(rec.get("items", [])):
            st = ", ".join(f"{k} {v}" for k, v in sorted(it["statuses"].items())) or "-"
            slots = _fmt_slots(it.get("slots", {}))
            lines.append(f"  [{i}] {it['kind']:11s} {it['label']}: {it['state']}  launched {it['done'] + it['running']} "
                         f"done {it['done']} queued {it['queued']}  ({st})" + (f"  slots {slots}" if slots else ""))
            if it.get("run_dir"):
                lines.append(f"       {it['run_dir']}")
            if it.get("error"):
                lines.append(f"       error: {it['error']}")
        return "\n".join(lines)
    recs = list_jobs()
    pools = load_pools()
    live = [r for r in recs if job_live(r)]
    use = _pool_use(live)
    lines = ["pools: " + "  ".join(f"{p} {use.get(p, 0)}/{n}" for p, n in pools.items())]
    shown = live + [r for r in recs if r not in live][-recent:]
    if shown:
        lines.append(f"{'JOB':22s} {'STATE':11s} {'LABEL':28s} {'LAUNCHED':>8s} {'DONE':>5s} {'QUEUED':>6s}  SLOTS")
    for r in shown:
        state = r["state"] if r in live or r["state"] in TERMINAL or r.get("lease") is None else "died"
        its = r.get("items", [])
        slots = _fmt_slots({f"{i}/{k}": v for i, it in enumerate(its) for k, v in it.get("slots", {}).items()}) \
            if r in live else ""
        lines.append(f"{r['id']:22s} {state:11s} {(r.get('label') or '-')[:28]:28s} "
                     f"{sum(i['done'] + i['running'] for i in its):8d} {sum(i['done'] for i in its):5d} "
                     f"{sum(i['queued'] for i in its):6d}  {slots}")
    try:
        found = orphans()
    except container.DockerError as err:
        found = [f"(docker unavailable: {err})"]
    lines.append("orphans: " + (", ".join(found) if found else "none"))
    return "\n".join(lines)


def _fmt_slots(slots: dict) -> str:
    total: dict[str, int] = {}
    for held in slots.values():
        for pool, ks in held.items():
            total[pool] = total.get(pool, 0) + len(ks)
    return ", ".join(f"{p} {n}" for p, n in sorted(total.items()))


def cancel(job_id: str) -> str:
    rec = read_job(job_id)
    if rec["state"] in TERMINAL:
        return f"job {job_id} already {rec['state']}"
    lease = rec.get("lease")
    if lease_alive(lease):
        os.kill(lease["pid"], signal.SIGTERM)
        return f"job {job_id}: SIGTERM sent to pid {lease['pid']}; in-flight items are being stopped and recorded"
    if lease is None and rec.get("unit"):
        subprocess.run(["systemctl", "--user", "stop", rec["unit"]], capture_output=True, text=True)
        job = Job(rec)
        job.update(state="interrupted", ended_at=now_iso(), error="cancelled before it started")
        return f"job {job_id}: cancelled before it started"
    return f"job {job_id} is not running (its process is gone); `hera-replay reap` records it and removes its containers"


def reap() -> list[str]:
    """Stop and remove orphan containers; record dead jobs as `died`."""
    lines = []
    for name in orphans():
        container.stop_container(name)
        container.remove_container(name)
        lines.append(f"removed {name}")
    for rec in list_jobs():
        if rec["state"] not in TERMINAL and rec.get("lease") and not lease_alive(rec["lease"]):
            Job(rec).update(state="died", ended_at=now_iso(), error="the job process died")
            lines.append(f"job {rec['id']} ({rec.get('label') or '-'}) recorded as died")
    return lines or ["nothing to reap"]
