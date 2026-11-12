from __future__ import annotations

import json
import os
import socket
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pytest
import yaml

from hera.experiment_scheduler import (
    LaneState,
    LockError,
    PlanError,
    Scheduler,
    SingletonLock,
    atomic_write_json,
    build_epoch_argv,
    classify_quota,
    expected_coordinates,
    load_plan,
    main,
    parse_reset_time,
    redact_message,
    scan_job_progress,
    select_job,
    unblock_lane,
)


def _write_manifest(path: Path, campaign_ids: tuple[str, ...] = ("c1",)) -> None:
    campaigns = []
    for index, campaign_id in enumerate(campaign_ids, 1):
        campaigns.append(
            {
                "id": campaign_id,
                "trial": index,
                "source": str(path.parent / f"source-{campaign_id}"),
                "experiments": {
                    "tool-call": {
                        "cut_index": 0,
                        "measure_notebook": "measure.ipynb",
                        "data_runs": [],
                    },
                    "final-analysis": {
                        "measure_notebook": "measure.ipynb",
                        "analysis_notebook": "ana.ipynb",
                        "data_runs": [],
                    },
                },
            }
        )
    path.write_text(
        yaml.safe_dump(
            {
                "version": 1,
                "experiment_id": "synthetic",
                "harness": {"kind": "fake"},
                "campaigns": campaigns,
            }
        ),
        encoding="utf-8",
    )


def _plan_doc(
    tmp_path: Path,
    *,
    lanes: dict[str, dict[str, Any]] | None = None,
    jobs: dict[str, dict[str, Any]] | None = None,
    global_workers: int = 4,
) -> tuple[Path, dict[str, Any]]:
    manifest = tmp_path / "manifest.yaml"
    _write_manifest(manifest, ("c1", "c2"))
    if lanes is None:
        lanes = {
            "provider-a": {
                "min_parallel": 1,
                "initial_parallel": 2,
                "max_parallel": 4,
                "additive_step": 1,
                "decrease_factor": 0.5,
                "rate_cooldown_s": 60,
                "hard_block_retry_s": 3600,
            }
        }
    if jobs is None:
        jobs = {
            "job-a": {
                "lane": "provider-a",
                "enabled": True,
                "priority": 10,
                "manifest": "manifest.yaml",
                "output": "outputs/job-a",
                "harness": "claude-p",
                "model": "claude-test-pinned",
                "thinking": "high",
                "samples": 2,
                "campaigns": ["c1"],
                "experiments": ["tool-call"],
            }
        }
    doc = {
        "version": 1,
        "state_dir": "state",
        "scheduler": {
            "global_max_workers": global_workers,
            "poll_interval_s": 0.01,
            "unknown_backoff_s": 0.05,
            "shutdown_grace_s": 0,
        },
        "lanes": lanes,
        "jobs": jobs,
    }
    plan_path = tmp_path / "plan.yaml"
    plan_path.write_text(yaml.safe_dump(doc, sort_keys=False), encoding="utf-8")
    return plan_path, doc


def _write_sample(
    output: Path,
    campaign: str,
    experiment: str,
    sample: int,
    status: str,
    **extra: Any,
) -> Path:
    sample_dir = output / "samples" / campaign / experiment / f"sample-{sample:02d}"
    sample_dir.mkdir(parents=True, exist_ok=True)
    record = {
        "campaign": campaign,
        "experiment": experiment,
        "sample": sample,
        "status": status,
        **extra,
    }
    sample_path = sample_dir / "sample.json"
    sample_path.write_text(json.dumps(record), encoding="utf-8")
    return sample_path


def test_load_plan_resolves_paths_filters_and_identity(tmp_path: Path) -> None:
    plan_path, _ = _plan_doc(tmp_path)

    plan = load_plan(plan_path)

    job = plan.jobs["job-a"]
    assert plan.state_dir == (tmp_path / "state").resolve()
    assert job.manifest == (tmp_path / "manifest.yaml").resolve()
    assert job.output == (tmp_path / "outputs/job-a").resolve()
    assert job.campaigns == ("c1",)
    assert job.experiments == ("tool-call",)
    assert len(plan.identity) == 64
    coordinates = expected_coordinates(plan, job)
    assert [(item.campaign, item.experiment, item.sample) for item in coordinates] == [
        ("c1", "tool-call", 1),
        ("c1", "tool-call", 2),
    ]


@pytest.mark.parametrize(
    ("mutate", "match"),
    [
        (lambda doc: doc.update(version=2), "unsupported plan version"),
        (
            lambda doc: doc["lanes"]["provider-a"].update(initial_parallel=8),
            "min_parallel <= initial_parallel <= max_parallel",
        ),
        (lambda doc: doc["jobs"]["job-a"].update(lane="absent"), "unknown lane"),
        (lambda doc: doc["jobs"]["job-a"].update(manifest="missing.yaml"), "manifest not found"),
        (lambda doc: doc["jobs"]["job-a"].update(campaigns=["absent"]), "unknown campaign"),
    ],
)
def test_load_plan_rejects_invalid_plans(
    tmp_path: Path, mutate: Any, match: str
) -> None:
    plan_path, doc = _plan_doc(tmp_path)
    mutate(doc)
    plan_path.write_text(yaml.safe_dump(doc, sort_keys=False), encoding="utf-8")

    with pytest.raises(PlanError, match=match):
        load_plan(plan_path)


def test_lane_minimum_cannot_exceed_global_budget(tmp_path: Path) -> None:
    plan_path, doc = _plan_doc(tmp_path)
    doc["lanes"]["provider-a"].update(
        min_parallel=5, initial_parallel=5, max_parallel=5
    )
    plan_path.write_text(yaml.safe_dump(doc, sort_keys=False), encoding="utf-8")
    with pytest.raises(PlanError, match="global_max_workers"):
        load_plan(plan_path)


def test_plan_rejects_duplicate_yaml_keys(tmp_path: Path) -> None:
    manifest = tmp_path / "manifest.yaml"
    _write_manifest(manifest)
    plan_path = tmp_path / "plan.yaml"
    plan_path.write_text(
        """version: 1
state_dir: state
scheduler:
  global_max_workers: 1
lanes:
  same: {min_parallel: 1, initial_parallel: 1, max_parallel: 1}
  same: {min_parallel: 1, initial_parallel: 1, max_parallel: 2}
jobs: {}
""",
        encoding="utf-8",
    )

    with pytest.raises(PlanError, match="duplicate YAML mapping key"):
        load_plan(plan_path)


def test_plan_rejects_nested_output_roots_and_unpinned_pi(tmp_path: Path) -> None:
    manifest = tmp_path / "manifest.yaml"
    _write_manifest(manifest)
    common = {
        "lane": "provider-a",
        "enabled": True,
        "manifest": "manifest.yaml",
        "harness": "claude-p",
        "model": "pinned",
        "thinking": "high",
        "samples": 1,
    }
    jobs = {
        "one": {**common, "output": "output"},
        "two": {**common, "output": "output/nested"},
    }
    plan_path, _ = _plan_doc(tmp_path, jobs=jobs)
    with pytest.raises(PlanError, match="overlapping output roots"):
        load_plan(plan_path)

    jobs = {
        "one": {
            **common,
            "output": "other",
            "harness": "not-a-harness",
        }
    }
    plan_path, _ = _plan_doc(tmp_path, jobs=jobs)
    with pytest.raises(PlanError, match="unsupported harness"):
        load_plan(plan_path)


def test_scan_progress_reuses_retained_and_counts_expected_only(tmp_path: Path) -> None:
    plan_path, _ = _plan_doc(tmp_path)
    plan = load_plan(plan_path)
    job = plan.jobs["job-a"]
    _write_sample(job.output, "c1", "tool-call", 1, "ok", total_cost_usd=0.25)
    error_path = _write_sample(
        job.output,
        "c1",
        "tool-call",
        2,
        "error",
        error="429 rate limited token=top-secret",
    )
    (error_path.parent / "stderr.txt").write_text("Bearer secret-value", encoding="utf-8")
    _write_sample(job.output, "c2", "tool-call", 1, "ok")

    progress = scan_job_progress(plan, job)

    assert progress.expected == 2
    assert progress.retained == 1
    assert progress.successful == 1
    assert progress.failed == 1
    assert progress.missing == 0
    assert progress.total_cost_usd == pytest.approx(0.25)
    evidence = next(iter(progress.errors.values()))
    assert "top-secret" not in evidence
    assert "secret-value" not in evidence


def test_unparseable_is_terminal_but_not_quality_success(tmp_path: Path) -> None:
    plan_path, _ = _plan_doc(tmp_path)
    plan = load_plan(plan_path)
    job = plan.jobs["job-a"]
    _write_sample(job.output, "c1", "tool-call", 1, "unparseable")
    _write_sample(job.output, "c1", "tool-call", 2, "ok")

    progress = scan_job_progress(plan, job)

    assert progress.complete
    assert progress.retained == 2
    assert progress.successful == 1
    assert progress.unparseable == 1


@pytest.mark.parametrize(
    ("message", "category"),
    [
        ("401 unauthorized: invalid api key", "authentication"),
        ("credit balance exhausted", "exhausted_balance"),
        ("You have no credits remaining", "exhausted_balance"),
        ("weekly usage limit reached", "weekly_limit"),
        ("session usage limit reached; resets 7:20pm (America/Chicago)", "session_window"),
        ("HTTP 429 too many requests", "rate_limit"),
        ("terminal model error: rate_limit_error", "rate_limit"),
        ("service unavailable: connection timed out", "timeout_transient"),
        ("provider emitted something novel", "unknown"),
    ],
)
def test_quota_classification(message: str, category: str) -> None:
    assert classify_quota(message).category == category


def test_reset_parsing_supports_retry_iso_and_named_zone() -> None:
    now = datetime(2025, 1, 2, 18, 0, tzinfo=timezone.utc).timestamp()
    assert parse_reset_time("retry-after 90 seconds", now) == pytest.approx(now + 90)
    iso = parse_reset_time("resets 2025-01-02T19:00:00Z", now)
    assert iso == datetime(2025, 1, 2, 19, 0, tzinfo=timezone.utc).timestamp()
    chicago = parse_reset_time("resets 7:20pm (America/Chicago)", now)
    assert chicago is not None
    assert chicago > now
    assert parse_reset_time("resets whenever the provider feels ready", now) is None
    assert parse_reset_time("resets 7:20pm (Not/AZone)", now) is None


def test_redaction_removes_common_credentials_and_truncates() -> None:
    message = "Authorization: Bearer abcdef api_key=secret-value sk-abcdefghijkl " + "x" * 100
    safe = redact_message(message, limit=80)
    assert "abcdef" not in safe
    assert "secret-value" not in safe
    assert "sk-abcdefghijkl" not in safe
    assert len(safe) == 80


def test_priority_then_round_robin_selection(tmp_path: Path) -> None:
    manifest = tmp_path / "manifest.yaml"
    _write_manifest(manifest)
    common = {
        "lane": "provider-a",
        "enabled": True,
        "manifest": "manifest.yaml",
        "harness": "claude-p",
        "model": "pinned",
        "thinking": "high",
        "samples": 1,
    }
    jobs = {
        "lower": {**common, "priority": 1, "output": "out/lower"},
        "alpha": {**common, "priority": 10, "output": "out/alpha"},
        "beta": {**common, "priority": 10, "output": "out/beta"},
    }
    plan_path, _ = _plan_doc(tmp_path, jobs=jobs)
    plan = load_plan(plan_path)
    progress = {job_id: scan_job_progress(plan, job) for job_id, job in plan.jobs.items()}
    state = LaneState(concurrency=1)

    assert select_job(plan, "provider-a", state, progress).id == "alpha"
    state.job_cursor = "alpha"
    assert select_job(plan, "provider-a", state, progress).id == "beta"
    state.job_cursor = "beta"
    assert select_job(plan, "provider-a", state, progress).id == "alpha"



def test_epoch_argv_is_bounded_and_fully_pinned(tmp_path: Path) -> None:
    plan_path, _ = _plan_doc(tmp_path)
    job = load_plan(plan_path).jobs["job-a"]

    argv = build_epoch_argv(job, 3)

    assert argv[:4] == [sys.executable, "-m", "hera.variance", "run"]
    assert argv[argv.index("--max-parallel") + 1] == "3"
    assert argv[argv.index("--max-tasks") + 1] == "3"
    assert argv[argv.index("--model") + 1] == "claude-test-pinned"
    assert argv[argv.index("--harness") + 1] == "claude-p"
    assert argv[argv.index("--thinking") + 1] == "high"
    assert "--force" not in argv


def test_atomic_json_and_singleton_dead_owner_recovery(tmp_path: Path) -> None:
    json_path = tmp_path / "state.json"
    atomic_write_json(json_path, {"value": 1})
    assert json.loads(json_path.read_text(encoding="utf-8")) == {"value": 1}
    assert not list(tmp_path.glob(".state.json.*.tmp"))

    lock_path = tmp_path / "scheduler.lock"
    lock_path.write_text(
        json.dumps({"pid": 999_999_999, "hostname": socket.gethostname()}),
        encoding="utf-8",
    )
    lock = SingletonLock(lock_path)
    lock.acquire()
    assert json.loads(lock_path.read_text(encoding="utf-8"))["pid"] == os.getpid()
    with pytest.raises(LockError, match="already running"):
        SingletonLock(lock_path).acquire()
    lock.release()
    assert not lock_path.exists()


class _SampleWritingProcess:
    next_pid = 40000

    def __init__(self, argv: list[str], calls: list[dict[str, Any]], **kwargs: Any):
        self.argv = argv
        self.kwargs = kwargs
        self.returncode: int | None = None
        self.pid = _SampleWritingProcess.next_pid
        _SampleWritingProcess.next_pid += 1
        self.calls = calls
        self.calls.append({"argv": argv, "kwargs": kwargs})

    def communicate(self) -> tuple[str, str]:
        output = Path(self.argv[self.argv.index("--output") + 1])
        campaigns = ["c1"]
        experiment = "tool-call"
        sample = 1
        _write_sample(output, campaigns[0], experiment, sample, "ok")
        self.returncode = 0
        return "run complete", ""

    def poll(self) -> int | None:
        return self.returncode

    def wait(self, timeout: float | None = None) -> int:
        self.returncode = 0 if self.returncode is None else self.returncode
        return self.returncode

    def terminate(self) -> None:
        self.returncode = -15

    def kill(self) -> None:
        self.returncode = -9


def test_once_supervisor_uses_safe_popen_and_persists_adaptation(tmp_path: Path) -> None:
    plan_path, doc = _plan_doc(tmp_path)
    doc["jobs"]["job-a"]["samples"] = 1
    plan_path.write_text(yaml.safe_dump(doc, sort_keys=False), encoding="utf-8")
    plan = load_plan(plan_path)
    calls: list[dict[str, Any]] = []

    def factory(argv: list[str], **kwargs: Any) -> _SampleWritingProcess:
        return _SampleWritingProcess(argv, calls, **kwargs)

    scheduler = Scheduler(plan, popen_factory=factory, sleeper=lambda delay: time.sleep(0.001))
    assert scheduler.run(once=True) == 0

    assert len(calls) == 1
    assert calls[0]["kwargs"]["shell"] is False
    assert calls[0]["kwargs"]["start_new_session"] is True
    argv = calls[0]["argv"]
    assert argv[argv.index("--max-parallel") + 1] == "2"
    assert argv[argv.index("--max-tasks") + 1] == "2"
    state = json.loads((plan.state_dir / "state.json").read_text(encoding="utf-8"))
    lane = state["lanes"]["provider-a"]
    assert lane["concurrency"] == 3
    assert lane["attempt_totals"]["job-a"] == 1
    status = json.loads((plan.state_dir / "status.json").read_text(encoding="utf-8"))
    assert status["lanes"]["provider-a"]["jobs"]["job-a"]["retained"] == 1
    assert not (plan.state_dir / "scheduler.lock").exists()


def test_dry_run_and_cli_validate_make_no_subprocess_calls(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    plan_path, _ = _plan_doc(tmp_path)
    assert main(["validate", "--plan", str(plan_path)]) == 0
    assert "identity:" in capsys.readouterr().out

    plan = load_plan(plan_path)

    def forbidden(*args: Any, **kwargs: Any) -> Any:
        raise AssertionError("dry-run attempted a subprocess")

    scheduler = Scheduler(plan, popen_factory=forbidden, sleeper=lambda delay: None)
    assert scheduler.run(once=True, dry_run=True) == 0
    assert "--max-tasks" in capsys.readouterr().out


def test_unblock_clears_persisted_lane_and_writes_request(tmp_path: Path) -> None:
    plan_path, _ = _plan_doc(tmp_path)
    plan = load_plan(plan_path)
    scheduler = Scheduler(plan)
    lane = scheduler.lane_states["provider-a"]
    lane.state = "blocked"
    lane.block_reason = "authentication"
    lane.classification = "authentication"
    lane.last_error = "bad credentials"
    lane.cooldown_until = time.time() + 1000
    scheduler.persist()

    unblock_lane(plan, "provider-a")

    state = json.loads((plan.state_dir / "state.json").read_text(encoding="utf-8"))
    cleared = state["lanes"]["provider-a"]
    assert cleared["state"] == "ready"
    assert cleared["block_reason"] is None
    assert cleared["cooldown_until"] is None
    assert list(plan.state_dir.glob("unblock-*.json"))
