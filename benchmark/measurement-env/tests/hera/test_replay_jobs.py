"""Replay jobs (`hera.replay.jobs`, `hera.replay.cell`): slot pools shared across jobs,
leases and orphans, reap, cancel, specs, submit, grade selection, pooling run dirs.
Docker and the agent are the fakes of `test_replay_run`."""

from __future__ import annotations

import base64
import json
import os
import re
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path

import pytest
import yaml

from hera.replay import cell, container, grade, jobs, main
from hera.replay.errors import CutError
from tests.hera.test_replay_run import install_agent, run_dir_of, setup, stream  # noqa: F401  (setup is a fixture)


def pools(tmp_config: dict) -> None:
    path = jobs.config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(f"{k} = {v}\n" for k, v in tmp_config.items()))


class Probe(jobs.Item):
    """Units that sleep while holding their slots, recording what ran at once."""

    kind = "probe"
    lock = threading.Lock()

    def __init__(self, name: str, units: int, *, log: list, live: list, pool: str = "claude", hold_s: float = 0.15):
        super().__init__(parallel=None)
        self.name, self.log, self.live, self.pool, self.hold_s = name, log, live, pool, hold_s
        self.queued.extend(range(units))
        self.expanded = True

    def label(self):
        return self.name

    def needs(self, unit):
        return [(self.pool, 1), ("host", 1)]

    def run(self, unit):
        with Probe.lock:
            self.live.append(self.name)
            self.log.append(list(self.live))
        time.sleep(self.hold_s)
        with Probe.lock:
            self.live.remove(self.name)
        return "ok"


def test_stamps_carry_a_random_tag_and_sort_by_time():
    stamps = {container.stamp() for _ in range(200)}
    assert len(stamps) == 200
    assert all(re.fullmatch(r"\d{8}T\d{6}-[a-z0-9]{6}", s) for s in stamps)


def test_two_jobs_share_the_pools_and_neither_waits_for_the_other():
    pools({"claude": 2, "codex": 1, "host": 12})
    log, live = [], []
    a, b = Probe("a", 4, log=log, live=live), Probe("b", 4, log=log, live=live)
    ts = [threading.Thread(target=jobs.run_foreground, args=([it],), kwargs={"label": it.name, "check_orphans": False})
          for it in (a, b)]
    for t in ts:
        t.start()
    for t in ts:
        t.join(timeout=30)
    assert max(len(snap) for snap in log) == 2                       # the claude pool is the cap across jobs
    assert any(set(snap) == {"a", "b"} for snap in log)              # both jobs ran at once
    assert a.results == b.results == {i: "ok" for i in range(4)}
    recs = jobs.list_jobs()
    assert sorted(r["label"] for r in recs) == ["a", "b"] and all(r["state"] == "done" for r in recs)


def test_extractions_take_claude_slots_so_an_episode_waits_for_them():
    pools({"claude": 1, "codex": 1, "host": 12})
    assert jobs.ExtractionItem([]).needs(0) == [("claude", 1), ("host", 1)]
    held = jobs.try_acquire(jobs.ExtractionItem([]).needs(0), jobs.load_pools())
    assert held is not None and held.slots == {"claude": [0], "host": held.slots["host"]}
    assert jobs.try_acquire([("claude", 1), ("host", 1)], jobs.load_pools()) is None
    held.release()
    assert jobs.try_acquire([("claude", 1), ("host", 1)], jobs.load_pools()) is not None


def test_acquisition_is_all_or_nothing():
    sizes = {"claude": 2, "codex": 1, "host": 1}
    host = jobs.try_acquire([("host", 1)], sizes)
    assert jobs.try_acquire([("claude", 1), ("host", 1)], sizes) is None
    both = jobs.try_acquire([("claude", jobs.ALL)], sizes)          # the failed try released its claude slot
    assert both is not None and both.slots == {"claude": [0, 1]}
    host.release()
    both.release()


def test_a_codex_episode_takes_the_whole_codex_pool_while_the_token_is_near_expiry(tmp_path, monkeypatch):
    def auth(exp):
        payload = base64.urlsafe_b64encode(json.dumps({"exp": exp}).encode()).decode().rstrip("=")
        return json.dumps({"tokens": {"access_token": f"h.{payload}.s", "refresh_token": "r"}}).encode()

    f = tmp_path / "auth.json"
    monkeypatch.setattr(container, "CODEX_AUTH_FILE", f)
    monkeypatch.delenv("CODEX_API_KEY", raising=False)
    f.write_bytes(auth(time.time() + 3600))
    assert jobs.codex_refresh_due()
    f.write_bytes(auth(time.time() + 5 * 86400))
    assert not jobs.codex_refresh_due()
    monkeypatch.setenv("CODEX_API_KEY", "k")
    assert not jobs.codex_refresh_due()


def test_a_run_is_a_foreground_job_with_a_lease_and_its_containers_listed(setup):
    install_agent(setup, lines=stream())
    assert main(["run", str(setup["case"]), "--n", "2", "--parallel", "2"]) == 0
    rd = run_dir_of(setup)
    assert re.fullmatch(r"\d{8}T\d{6}-[a-z0-9]{6}", rd.name)
    run = json.loads((rd / "run.json").read_text())
    (rec,) = jobs.list_jobs()
    assert run["job"] == {"id": rec["id"], "label": "run dev-fan", "host": rec["lease"]["host"]}
    assert rec["state"] == "done" and rec["mode"] == "foreground" and rec["lease"]["pid"] == os.getpid()
    assert sorted(rec["containers"]) == [f"hera-replay-dev-fan-{rd.name}-{s}" for s in ("00", "01")]
    (item,) = rec["items"]
    assert item["kind"] == "episodes" and item["statuses"] == {"ok": 2} and item["run_dir"] == str(rd)
    assert "[00] ok" in (jobs.jobs_dir() / rec["id"] / "job.log").read_text()
    assert rec["harness"]["code_hash"] == run["harness"]["code_hash"]


def dead_lease() -> dict:
    proc = subprocess.Popen(["true"])
    proc.wait()
    return {**jobs.make_lease(None), "pid": proc.pid, "start": 1}


def fake_job(lease, containers, state="running", label="other") -> dict:
    job = jobs.Job.create(label=label, spec=None, mode="detached")
    job.update(state=state, lease=lease, containers=containers)
    return job.record


def test_a_killed_jobs_containers_are_orphans_and_a_live_jobs_are_not(setup):
    install_agent(setup, lines=stream())
    fake_job(dead_lease(), ["hera-replay-x-1-00"], label="killed")
    live = fake_job(jobs.make_lease(None), ["hera-grade-y-000"], label="live")
    setup["docker"].leftovers = ("hera-grade-y-000", "hera-replay-x-1-00")
    assert jobs.orphans() == ["hera-replay-x-1-00"]
    with pytest.raises(SystemExit, match=r"no live job lists .*hera-replay-x-1-00"):
        main(["run", str(setup["case"])])
    assert not (setup["hera_data"] / "replay" / "runs").exists()
    # A reboot kills every lease: same pid and start, another boot.
    assert not jobs.lease_alive({**live["lease"], "boot_id": "other"})
    setup["docker"].leftovers = ("hera-grade-y-000",)
    assert main(["run", str(setup["case"]), "--n", "1"]) == 0


def test_reap_removes_only_orphans_and_records_the_dead_job(setup, capsys):
    dead = fake_job(dead_lease(), ["hera-replay-x-1-00"], label="killed")
    live = fake_job(jobs.make_lease(None), ["hera-replay-y-2-00"], label="live")
    setup["docker"].leftovers = ("hera-replay-x-1-00", "hera-replay-y-2-00", "hera-grade-z-000")
    assert main(["reap"]) == 0
    out = capsys.readouterr().out
    assert "removed hera-replay-x-1-00" in out and "removed hera-grade-z-000" in out and "hera-replay-y-2-00" not in out
    assert ["rm", "-f", "hera-replay-y-2-00"] not in setup["docker"].of("rm")
    assert jobs.read_job(dead["id"])["state"] == "died" and jobs.read_job(live["id"])["state"] == "running"


def test_cancel_signals_that_job_only():
    procs = [subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"]) for _ in range(2)]
    try:
        time.sleep(0.2)
        recs = [fake_job({**jobs.make_lease(None), "pid": p.pid, "start": jobs.proc_start(p.pid)}, []) for p in procs]
        assert "SIGTERM sent" in jobs.cancel(recs[0]["id"])
        assert procs[0].wait(timeout=10) == -signal.SIGTERM
        assert procs[1].poll() is None
        done = fake_job(None, [], state="done")
        assert "already done" in jobs.cancel(done["id"])
    finally:
        for p in procs:
            p.kill()


def test_spec_validation(setup, tmp_path):
    case = str(setup["case"])
    bad = [
        ({"items": []}, "non-empty"),
        ({"items": [{"case": case}], "priority": 1}, "unknown keys"),
        ({"items": [{"case": case, "grade": "x"}]}, "exactly one"),
        ({"items": [{"case": case, "n": 0}]}, "n must be an integer"),
        ({"items": [{"case": case, "grader": "g"}]}, "unknown keys"),
        ({"items": [{"case": case, "effort": "turbo"}]}, "effort must be one of"),
        ({"items": [{"case": str(tmp_path / "nope.yaml")}]}, "nope.yaml"),
        ({"items": [{"grade": str(tmp_path)}]}, "no run.json"),
    ]
    for spec, msg in bad:
        with pytest.raises((CutError, FileNotFoundError, OSError), match=msg):
            jobs.normalize_spec(spec, base=tmp_path)
    ok = jobs.normalize_spec({"label": "L", "items": [{"case": os.path.relpath(case, tmp_path), "n": 2, "model": None}]},
                             base=tmp_path)
    assert ok == {"label": "L", "parallel": None, "items": [{"case": str(Path(case)), "n": 2}]}


def test_submit_starts_a_transient_unit_with_credentials_passed_by_name(setup, monkeypatch):
    seen = {}
    monkeypatch.setattr(jobs.subprocess, "run", lambda argv, **kw: seen.setdefault("argv", argv) and
                        subprocess.CompletedProcess(argv, 0, "", ""))
    job_id = jobs.submit({"label": "G", "items": [{"case": str(setup["case"]), "n": 1}]}, base=Path.cwd())
    argv = seen["argv"]
    assert argv[:3] == ["systemd-run", "--user", "--quiet"] and f"--unit=hera-replay-job-{job_id}" in argv
    assert argv[-5:] == [sys.executable, "-m", "hera.replay", "_job", job_id]
    assert "--setenv=CLAUDE_CODE_OAUTH_TOKEN" in argv and "tok-secret" not in " ".join(argv)
    rec = jobs.read_job(job_id)
    assert rec["state"] == "queued" and rec["unit"] == f"hera-replay-job-{job_id}" and rec["spec"]["label"] == "G"


def second_case(setup, name="dev-fan2") -> Path:
    path = setup["case"].with_name(f"{name}.yaml")
    path.write_text(yaml.safe_dump({**yaml.safe_load(setup["case"].read_text()), "case": name}))
    return path


def test_the_job_process_runs_its_spec_and_wait_reports_it(setup, capsys):
    install_agent(setup, lines=stream())
    spec = jobs.normalize_spec({"label": "two-items", "items": [{"case": str(setup["case"]), "n": 1},
                                                              {"case": str(second_case(setup)), "n": 2, "parallel": 2}]},
                               base=Path.cwd())
    job = jobs.Job.create(label="two-items", spec=spec, mode="detached")
    assert jobs.run_detached(job.id) == 0
    rec = jobs.read_job(job.id)
    assert rec["state"] == "done" and [it["statuses"] for it in rec["items"]] == [{"ok": 1}, {"ok": 2}]
    rds = sorted(setup["hera_data"].glob("replay/runs/dev-fan*/*"))
    assert len(rds) == 2 and {json.loads((d / "run.json").read_text())["job"]["id"] for d in rds} == {job.id}
    capsys.readouterr()
    assert main(["wait", job.id]) == 0
    out = capsys.readouterr().out
    assert out.count("run dir:") == 2 and f"job {job.id}: done" in out and "[00] ok" in out
    assert main(["status"]) == 0 and job.id in capsys.readouterr().out
    assert main(["status", job.id]) == 0 and "launched 2 done 2 queued 0" in capsys.readouterr().out


def test_a_bad_cut_fails_the_job_before_anything_launches(setup, tmp_path):
    install_agent(setup, lines=stream())
    broken = yaml.safe_load(setup["case"].read_text())
    broken["cut"]["at"] = "00000000-0000-0000-0000-000000000000"
    bad = tmp_path / "cases" / "dev-bad.yaml"
    bad.write_text(yaml.safe_dump({**broken, "case": "dev-bad"}))
    spec = jobs.normalize_spec({"items": [{"case": str(setup["case"]), "n": 1}, {"case": str(bad), "n": 1}]}, base=Path.cwd())
    job = jobs.Job.create(label=None, spec=spec, mode="detached")
    assert jobs.run_detached(job.id) == 1
    assert jobs.read_job(job.id)["state"] == "failed"
    assert not list(setup["hera_data"].glob("replay/runs/*/*"))       # the good item's run dir went too
    assert not [a for a in setup["docker"].of("run") if a[:2] == ["run", "-d"]]   # no episode container


def test_a_dead_job_makes_wait_exit_1(capsys):
    rec = fake_job(dead_lease(), [])
    assert jobs.wait(rec["id"], out=lambda s: None, poll_s=0.01) == 1


def _grade_dir(ep: Path, grader: str, stamp: str, exit_: str | None) -> None:
    d = ep / "grades" / grader / stamp
    d.mkdir(parents=True)
    if exit_:
        (d / "run.json").write_text(json.dumps({"claude": {"exit": exit_}}))


def test_a_grade_item_takes_finished_ungraded_episodes(tmp_path):
    rd = tmp_path / "run"
    (rd / "episodes").mkdir(parents=True)
    (rd / "run.json").write_text(json.dumps({"case": {"case": "c", "grader": "g"}}))
    for sid, finished in (("00", 1), ("01", 1), ("02", 0), ("03", 1), ("04", 1)):
        (rd / "episodes" / sid).mkdir()
        (rd / "episodes" / sid / "episode.json").write_text(json.dumps({"run": {}} if finished else {}))
    _grade_dir(rd / "episodes" / "00", "g", "A", "ok")          # graded
    _grade_dir(rd / "episodes" / "03", "g", "A", "quota")       # an infrastructure ending is no grade
    _grade_dir(rd / "episodes" / "04", "g", "A", None)          # in flight
    _grade_dir(rd / "episodes" / "01", "other", "A", "ok")      # another grader's
    assert [p.name for p in grade.select_episodes(rd, "g")] == ["01", "03"]
    assert [p.name for p in grade.select_episodes(rd, "g", regrade=True)] == ["00", "01", "03", "04"]
    assert grade.run_grader(rd, None) == "g" and grade.run_grader(rd, "x") == "x"
    for sid in ("01", "03"):
        _grade_dir(rd / "episodes" / sid, "g", "B", "no_output")
    with pytest.raises(CutError, match="--regrade"):
        grade.select_episodes(rd, "g")


def test_cell_pools_run_dirs_with_one_key_and_splits_the_rest(setup, capsys):
    install_agent(setup, lines=stream())
    for argv in (["--n", "1"], ["--n", "2"], ["--n", "1", "--model", "claude-opus-5"]):
        assert main(["run", str(setup["case"]), *argv]) == 0
    rds = [d for d in sorted(setup["hera_data"].glob("replay/runs/dev-fan/*"))
           if "override" not in json.loads((d / "run.json").read_text())]
    # A code change between run dirs is reported, not a split.
    run = json.loads((rds[1] / "run.json").read_text())
    run["harness"]["code_hash"] = "0" * 64
    (rds[1] / "run.json").write_text(json.dumps(run))
    groups = cell.pools(setup["hera_data"], "dev-fan")
    by_runs = sorted(len(g["runs"]) for g in groups)
    assert by_runs == [1, 2]
    pooled = next(g for g in groups if len(g["runs"]) == 2)
    assert len(pooled["rows"]) == 3 and pooled["override"] is None and len(pooled["code_hashes"]) == 2
    # A different first message (another brief) never pools.
    run["start"]["first_message"]["sha256"] = "f" * 64
    (rds[1] / "run.json").write_text(json.dumps(run))
    assert sorted(len(g["runs"]) for g in cell.pools(setup["hera_data"], "dev-fan")) == [1, 1, 1]
    run["start"]["first_message"]["sha256"] = json.loads((rds[0] / "run.json").read_text())["start"]["first_message"]["sha256"]
    (rds[1] / "run.json").write_text(json.dumps(run))
    assert main(["cell", str(setup["case"])]) == 0
    out = capsys.readouterr().out
    assert "3 run dirs in 2 pool(s)" in out and "code_hash differs" in out
    written = setup["hera_data"] / "replay" / "cells" / "dev-fan" / pooled["id"] / "summary.csv"
    lines = written.read_text().splitlines()
    assert lines[0].startswith("run,sample,model,status") and len(lines) == 4


def test_cut_digest_ignores_what_each_materialization_mints(tmp_path):
    a = tmp_path / "a"
    (a / "session").mkdir(parents=True)
    (a / "session" / "x.md").write_text("x")
    (a / "t.jsonl").write_text('{"uuid": "c1"}\n')
    (a / "episode.json").write_text(json.dumps({"created_at": "1", "resume": {"close_uuid": "c1"}}))
    d = cell.cut_digest(a)
    (a / "t.jsonl").write_text('{"uuid": "c2"}\n')
    (a / "episode.json").write_text(json.dumps({"created_at": "2", "resume": {"close_uuid": "c2"}}))
    assert cell.cut_digest(a) == d
    (a / "session" / "x.md").write_text("y")
    assert cell.cut_digest(a) != d


def test_a_stop_before_an_item_expands_ends_the_job():
    class Lazy(jobs.Item):
        kind = "lazy"

        def expand(self):
            raise AssertionError("a stopped job expands nothing")

    job = jobs.Job.create(label="stopped", spec=None, mode="foreground")
    job.stop.set()
    item = Lazy(parallel=None)
    t = threading.Thread(target=jobs.execute, args=(job, [item]))
    t.start()
    t.join(timeout=5)
    assert not t.is_alive() and item.state == "done" and item.results == {}
