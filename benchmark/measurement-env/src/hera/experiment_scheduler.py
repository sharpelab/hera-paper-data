"""Quota-aware supervisor for bounded HERA variance experiment epochs.

The scheduler is deliberately a coordination layer: scientific progress is
always reconstructed from ``sample.json`` records written by ``hera.variance``.
Importing this module does not read plans, create state, or start processes.
"""

from __future__ import annotations

import argparse
import errno
import hashlib
import json
import math
import os
import re
import signal
import socket
import subprocess
import sys
import tempfile
import threading
import time
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import yaml


STATE_VERSION = 1
PLAN_VERSION = 1
RETAINED_STATUSES = frozenset(("ok", "unparseable"))
QUALITY_STATUSES = frozenset(("ok",))
HARD_BLOCK_CATEGORIES = frozenset(("authentication", "exhausted_balance", "weekly_limit"))
RATE_CATEGORIES = frozenset(("session_window", "rate_limit"))
DEFAULT_MESSAGE_LIMIT = 500


class SchedulerError(Exception):
    """Base error for scheduler configuration and operation."""


class PlanError(SchedulerError):
    """A scheduler plan is invalid."""


class LockError(SchedulerError):
    """The scheduler plan is already owned by another supervisor."""


class _UniqueKeyLoader(yaml.SafeLoader):
    """Safe YAML loader that rejects duplicate mapping keys."""


def _construct_unique_mapping(
    loader: _UniqueKeyLoader, node: yaml.MappingNode, deep: bool = False
) -> dict[Any, Any]:
    loader.flatten_mapping(node)
    result: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        try:
            duplicate = key in result
        except TypeError as exc:
            raise PlanError("plan mapping contains an unhashable key") from exc
        if duplicate:
            raise PlanError(f"duplicate YAML mapping key: {key!r}")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


_UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_unique_mapping
)


@dataclass(frozen=True)
class SchedulerConfig:
    global_max_workers: int
    poll_interval_s: float = 30.0
    unknown_backoff_s: float = 300.0
    shutdown_grace_s: float = 15.0


@dataclass(frozen=True)
class LaneConfig:
    id: str
    min_parallel: int
    initial_parallel: int
    max_parallel: int
    additive_step: int = 1
    decrease_factor: float = 0.5
    rate_cooldown_s: float = 300.0
    hard_block_retry_s: float = 21600.0


@dataclass(frozen=True)
class JobConfig:
    id: str
    lane: str
    enabled: bool
    priority: int
    manifest: Path
    output: Path
    harness: str
    model: str
    thinking: str
    samples: int
    campaigns: tuple[str, ...] | None = None
    experiments: tuple[str, ...] | None = None
    max_attempts: int | None = None
    max_cost_usd: float | None = None


@dataclass(frozen=True)
class Plan:
    path: Path
    state_dir: Path
    scheduler: SchedulerConfig
    lanes: dict[str, LaneConfig]
    jobs: dict[str, JobConfig]
    manifests: dict[str, dict[str, Any]]
    identity: str
    digest: str

    def resolved_dict(self) -> dict[str, Any]:
        return {
            "version": PLAN_VERSION,
            "plan": str(self.path),
            "identity": self.identity,
            "digest": self.digest,
            "state_dir": str(self.state_dir),
            "scheduler": asdict(self.scheduler),
            "lanes": {key: asdict(value) for key, value in self.lanes.items()},
            "jobs": {
                key: {
                    **asdict(value),
                    "manifest": str(value.manifest),
                    "output": str(value.output),
                    "campaigns": list(value.campaigns) if value.campaigns else None,
                    "experiments": list(value.experiments) if value.experiments else None,
                }
                for key, value in self.jobs.items()
            },
        }


@dataclass(frozen=True, order=True)
class SampleCoordinate:
    campaign: str
    experiment: str
    sample: int


@dataclass
class JobProgress:
    expected: int
    retained: int
    successful: int
    failed: int
    missing: int
    unparseable: int
    total_cost_usd: float
    statuses: dict[SampleCoordinate, str] = field(default_factory=dict, repr=False)
    signatures: dict[SampleCoordinate, str] = field(default_factory=dict, repr=False)
    errors: dict[SampleCoordinate, str] = field(default_factory=dict, repr=False)

    @property
    def complete(self) -> bool:
        return self.expected > 0 and self.retained == self.expected

    def presentation(self) -> dict[str, Any]:
        return {
            "expected": self.expected,
            "retained": self.retained,
            "successful": self.successful,
            "failed": self.failed,
            "missing": self.missing,
            "unparseable": self.unparseable,
            "total_cost_usd": round(self.total_cost_usd, 8),
            "complete": self.complete,
        }


@dataclass(frozen=True)
class QuotaClassification:
    category: str
    message: str
    reset_at: float | None = None


@dataclass
class LaneState:
    concurrency: int
    state: str = "ready"
    cooldown_until: float | None = None
    block_reason: str | None = None
    classification: str | None = None
    job_cursor: str | None = None
    attempt_totals: dict[str, int] = field(default_factory=dict)
    epoch_total: int = 0
    retained_total: int = 0
    failed_total: int = 0
    last_error: str | None = None
    last_started_at: str | None = None
    last_completed_at: str | None = None
    active_pid: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class EpochResult:
    lane_id: str
    job_id: str
    concurrency: int
    returncode: int
    before: JobProgress
    after: JobProgress
    classifications: tuple[QuotaClassification, ...]
    child_error: str | None = None
    dry_run: bool = False


PopenFactory = Callable[..., subprocess.Popen[str]]
Clock = Callable[[], float]
Sleeper = Callable[[float], None]


def _require_mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise PlanError(f"{label} must be a mapping")
    return value


def _require_int(value: Any, label: str, minimum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise PlanError(f"{label} must be an integer")
    if minimum is not None and value < minimum:
        raise PlanError(f"{label} must be >= {minimum}")
    return value


def _require_number(value: Any, label: str, minimum: float = 0.0) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise PlanError(f"{label} must be a number")
    result = float(value)
    if not math.isfinite(result) or result < minimum:
        raise PlanError(f"{label} must be finite and >= {minimum}")
    return result


def _require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise PlanError(f"{label} must be a non-empty string")
    return value.strip()


def _optional_string_tuple(value: Any, label: str) -> tuple[str, ...] | None:
    if value is None:
        return None
    if not isinstance(value, list) or not value:
        raise PlanError(f"{label} must be a non-empty list of strings")
    result = tuple(_require_string(item, label) for item in value)
    if len(set(result)) != len(result):
        raise PlanError(f"{label} contains duplicates")
    return result


def _resolve_path(value: Any, label: str, base: Path | None = None) -> Path:
    raw = _require_string(value, label)
    path = Path(raw).expanduser()
    if not path.is_absolute() and base is not None:
        path = base / path
    return path.resolve(strict=False)


def _paths_overlap(left: Path, right: Path) -> bool:
    try:
        left.relative_to(right)
        return True
    except ValueError:
        pass
    try:
        right.relative_to(left)
        return True
    except ValueError:
        return False


def _load_yaml(path: Path) -> dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8")
        value = yaml.load(text, Loader=_UniqueKeyLoader)
    except (OSError, yaml.YAMLError) as exc:
        raise PlanError(f"cannot load YAML {path}: {exc}") from exc
    if value is None:
        value = {}
    return _require_mapping(value, str(path))


def _validate_manifest_for_job(
    job_id: str,
    manifest: dict[str, Any],
    campaigns: tuple[str, ...] | None,
    experiments: tuple[str, ...] | None,
) -> None:
    if manifest.get("version") != 1:
        raise PlanError(f"job {job_id}: unsupported manifest version {manifest.get('version')!r}")
    campaign_docs = manifest.get("campaigns")
    if not isinstance(campaign_docs, list) or not campaign_docs:
        raise PlanError(f"job {job_id}: manifest campaigns must be a non-empty list")
    seen: set[str] = set()
    available_experiments: set[str] = set()
    for campaign in campaign_docs:
        if not isinstance(campaign, dict):
            raise PlanError(f"job {job_id}: manifest campaign must be a mapping")
        campaign_id = _require_string(campaign.get("id"), f"job {job_id} campaign id")
        if campaign_id in seen:
            raise PlanError(f"job {job_id}: duplicate manifest campaign {campaign_id!r}")
        seen.add(campaign_id)
        experiment_docs = campaign.get("experiments")
        if not isinstance(experiment_docs, dict) or not experiment_docs:
            raise PlanError(f"job {job_id}: campaign {campaign_id} has no experiments")
        available_experiments.update(str(key) for key in experiment_docs)
    unknown_campaigns = set(campaigns or ()) - seen
    if unknown_campaigns:
        raise PlanError(
            f"job {job_id}: unknown campaign filter(s): {', '.join(sorted(unknown_campaigns))}"
        )
    unknown_experiments = set(experiments or ()) - available_experiments
    if unknown_experiments:
        raise PlanError(
            f"job {job_id}: unknown experiment filter(s): "
            f"{', '.join(sorted(unknown_experiments))}"
        )
    if not expected_coordinates_from_manifest(manifest, campaigns, experiments, 1):
        raise PlanError(f"job {job_id}: filters select no manifest experiments")


def load_plan(path: Path | str) -> Plan:
    """Load, resolve, and fully validate a version-1 scheduler plan."""
    plan_path = Path(path).expanduser().resolve(strict=False)
    doc = _load_yaml(plan_path)
    if doc.get("version") != PLAN_VERSION:
        raise PlanError(f"unsupported plan version: {doc.get('version')!r}")
    base = plan_path.parent
    state_dir = _resolve_path(doc.get("state_dir"), "state_dir", base)

    scheduler_doc = _require_mapping(doc.get("scheduler"), "scheduler")
    scheduler = SchedulerConfig(
        global_max_workers=_require_int(
            scheduler_doc.get("global_max_workers"), "scheduler.global_max_workers", 1
        ),
        poll_interval_s=_require_number(
            scheduler_doc.get("poll_interval_s", 30), "scheduler.poll_interval_s", 0.01
        ),
        unknown_backoff_s=_require_number(
            scheduler_doc.get("unknown_backoff_s", 300),
            "scheduler.unknown_backoff_s",
            0.01,
        ),
        shutdown_grace_s=_require_number(
            scheduler_doc.get("shutdown_grace_s", 15),
            "scheduler.shutdown_grace_s",
            0.0,
        ),
    )

    lanes_doc = _require_mapping(doc.get("lanes"), "lanes")
    if not lanes_doc:
        raise PlanError("lanes must not be empty")
    lanes: dict[str, LaneConfig] = {}
    for raw_id, raw_config in lanes_doc.items():
        lane_id = _require_string(raw_id, "lane id")
        if lane_id in lanes:
            raise PlanError(f"duplicate lane id after normalization: {lane_id!r}")
        config = _require_mapping(raw_config, f"lane {lane_id}")
        minimum = _require_int(config.get("min_parallel"), f"lane {lane_id}.min_parallel", 1)
        initial = _require_int(
            config.get("initial_parallel"), f"lane {lane_id}.initial_parallel", 1
        )
        maximum = _require_int(config.get("max_parallel"), f"lane {lane_id}.max_parallel", 1)
        if not minimum <= initial <= maximum:
            raise PlanError(
                f"lane {lane_id}: require min_parallel <= initial_parallel <= max_parallel"
            )
        decrease = _require_number(
            config.get("decrease_factor", 0.5), f"lane {lane_id}.decrease_factor", 0.0
        )
        if not 0.0 < decrease < 1.0:
            raise PlanError(f"lane {lane_id}.decrease_factor must be > 0 and < 1")
        if minimum > scheduler.global_max_workers:
            raise PlanError(
                f"lane {lane_id}.min_parallel exceeds scheduler.global_max_workers"
            )
        lanes[lane_id] = LaneConfig(
            id=lane_id,
            min_parallel=minimum,
            initial_parallel=initial,
            max_parallel=maximum,
            additive_step=_require_int(
                config.get("additive_step", 1), f"lane {lane_id}.additive_step", 1
            ),
            decrease_factor=decrease,
            rate_cooldown_s=_require_number(
                config.get("rate_cooldown_s", 300),
                f"lane {lane_id}.rate_cooldown_s",
                0.01,
            ),
            hard_block_retry_s=_require_number(
                config.get("hard_block_retry_s", 21600),
                f"lane {lane_id}.hard_block_retry_s",
                0.01,
            ),
        )

    jobs_doc = _require_mapping(doc.get("jobs"), "jobs")
    if not jobs_doc:
        raise PlanError("jobs must not be empty")
    jobs: dict[str, JobConfig] = {}
    manifests: dict[str, dict[str, Any]] = {}
    outputs: list[tuple[str, Path]] = []
    for raw_id, raw_config in jobs_doc.items():
        job_id = _require_string(raw_id, "job id")
        if job_id in jobs:
            raise PlanError(f"duplicate job id after normalization: {job_id!r}")
        config = _require_mapping(raw_config, f"job {job_id}")
        lane_id = _require_string(config.get("lane"), f"job {job_id}.lane")
        if lane_id not in lanes:
            raise PlanError(f"job {job_id}: unknown lane {lane_id!r}")
        enabled = config.get("enabled", True)
        if not isinstance(enabled, bool):
            raise PlanError(f"job {job_id}.enabled must be a boolean")
        priority = _require_int(config.get("priority", 0), f"job {job_id}.priority")
        manifest_path = _resolve_path(config.get("manifest"), f"job {job_id}.manifest", base)
        if not manifest_path.is_file():
            raise PlanError(f"job {job_id}: manifest not found: {manifest_path}")
        output = _resolve_path(config.get("output"), f"job {job_id}.output", base)
        for other_id, other_output in outputs:
            if _paths_overlap(output, other_output):
                raise PlanError(
                    f"jobs {other_id} and {job_id} have overlapping output roots: "
                    f"{other_output} and {output}"
                )
        outputs.append((job_id, output))
        harness = _require_string(config.get("harness"), f"job {job_id}.harness")
        if harness not in ("claude-p", "fake"):
            raise PlanError(f"job {job_id}: unsupported harness {harness!r}")
        model = _require_string(config.get("model"), f"job {job_id}.model")
        thinking = _require_string(config.get("thinking"), f"job {job_id}.thinking")
        samples = _require_int(config.get("samples"), f"job {job_id}.samples", 1)
        campaigns = _optional_string_tuple(config.get("campaigns"), f"job {job_id}.campaigns")
        experiments = _optional_string_tuple(
            config.get("experiments"), f"job {job_id}.experiments"
        )
        max_attempts_raw = config.get("max_attempts")
        max_attempts = (
            _require_int(max_attempts_raw, f"job {job_id}.max_attempts", 1)
            if max_attempts_raw is not None
            else None
        )
        max_cost_raw = config.get("max_cost_usd")
        max_cost = (
            _require_number(max_cost_raw, f"job {job_id}.max_cost_usd", 0.0)
            if max_cost_raw is not None
            else None
        )
        manifest = _load_yaml(manifest_path)
        _validate_manifest_for_job(job_id, manifest, campaigns, experiments)
        job = JobConfig(
            id=job_id,
            lane=lane_id,
            enabled=enabled,
            priority=priority,
            manifest=manifest_path,
            output=output,
            harness=harness,
            model=model,
            thinking=thinking,
            samples=samples,
            campaigns=campaigns,
            experiments=experiments,
            max_attempts=max_attempts,
            max_cost_usd=max_cost,
        )
        _validate_existing_output_identity(job, manifest)
        jobs[job_id] = job
        manifests[job_id] = manifest

    identity = hashlib.sha256(str(plan_path).encode("utf-8")).hexdigest()
    canonical = json.dumps(doc, sort_keys=True, default=str, separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return Plan(
        path=plan_path,
        state_dir=state_dir,
        scheduler=scheduler,
        lanes=lanes,
        jobs=jobs,
        manifests=manifests,
        identity=identity,
        digest=digest,
    )


def _validate_existing_output_identity(
    job: JobConfig, manifest: Mapping[str, Any]
) -> None:
    """Fail closed when a job output already identifies a different experiment."""
    experiment_path = job.output / "experiment.json"
    try:
        document = json.loads(experiment_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return
    except (OSError, json.JSONDecodeError) as exc:
        raise PlanError(f"job {job.id}: invalid existing {experiment_path}: {exc}") from exc
    if not isinstance(document, dict):
        raise PlanError(f"job {job.id}: existing {experiment_path} must be a JSON object")
    existing_experiment = document.get("experiment_id")
    if existing_experiment is not None and existing_experiment != manifest.get("experiment_id"):
        raise PlanError(
            f"job {job.id}: output experiment is {existing_experiment!r}, not manifest "
            f"{manifest.get('experiment_id')!r}"
        )
    harness = document.get("harness")
    if not isinstance(harness, dict):
        return
    existing_kind = harness.get("kind")
    existing_model = harness.get("model_requested")
    if existing_kind is not None and existing_kind != job.harness:
        raise PlanError(
            f"job {job.id}: output harness is {existing_kind!r}, not pinned {job.harness!r}"
        )
    if existing_model is not None and existing_model != job.model:
        raise PlanError(
            f"job {job.id}: output model is {existing_model!r}, not pinned {job.model!r}"
        )
    controls = harness.get("sampling_controls")
    if isinstance(controls, dict) and controls.get("thinking") not in (None, job.thinking):
        raise PlanError(
            f"job {job.id}: output thinking level is {controls.get('thinking')!r}, "
            f"not pinned {job.thinking!r}"
        )


def expected_coordinates_from_manifest(
    manifest: Mapping[str, Any],
    campaigns: Sequence[str] | None,
    experiments: Sequence[str] | None,
    samples: int,
) -> tuple[SampleCoordinate, ...]:
    """Return selected scientific coordinates in deterministic manifest order."""
    selected_campaigns = set(campaigns or ())
    selected_experiments = set(experiments or ())
    coordinates: list[SampleCoordinate] = []
    for campaign in manifest.get("campaigns", []):
        campaign_id = str(campaign.get("id", ""))
        if selected_campaigns and campaign_id not in selected_campaigns:
            continue
        for experiment in campaign.get("experiments", {}):
            experiment_id = str(experiment)
            if selected_experiments and experiment_id not in selected_experiments:
                continue
            coordinates.extend(
                SampleCoordinate(campaign_id, experiment_id, sample)
                for sample in range(1, samples + 1)
            )
    return tuple(coordinates)


def expected_coordinates(plan: Plan, job: JobConfig) -> tuple[SampleCoordinate, ...]:
    return expected_coordinates_from_manifest(
        plan.manifests[job.id], job.campaigns, job.experiments, job.samples
    )


def _sample_path(job: JobConfig, coordinate: SampleCoordinate) -> Path:
    return (
        job.output
        / "samples"
        / coordinate.campaign
        / coordinate.experiment
        / f"sample-{coordinate.sample:02d}"
        / "sample.json"
    )


def redact_message(message: Any, limit: int = DEFAULT_MESSAGE_LIMIT) -> str:
    """Remove common credential forms and bound persisted/logged error text."""
    text = str(message or "").replace("\x00", " ")
    substitutions = (
        (r"(?i)\b(bearer)\s+[A-Za-z0-9._~+/=-]+", r"\1 [REDACTED]"),
        (
            r"(?i)\b(api[_ -]?key|token|password|secret|authorization)\b"
            r"\s*[:=]\s*[^\s,;]+",
            r"\1=[REDACTED]",
        ),
        (r"\bsk-[A-Za-z0-9_-]{8,}\b", "[REDACTED_KEY]"),
        (r"(?i)(https?://)[^/@\s:]+:[^/@\s]+@", r"\1[REDACTED]@"),
    )
    for pattern, replacement in substitutions:
        text = re.sub(pattern, replacement, text)
    text = " ".join(text.split())
    if len(text) > limit:
        return text[: max(0, limit - 1)] + "…"
    return text


def scan_job_progress(plan: Plan, job: JobConfig) -> JobProgress:
    """Reconstruct job progress only from expected persisted sample records."""
    coordinates = expected_coordinates(plan, job)
    statuses: dict[SampleCoordinate, str] = {}
    signatures: dict[SampleCoordinate, str] = {}
    errors: dict[SampleCoordinate, str] = {}
    retained = successful = failed = unparseable = 0
    total_cost = 0.0
    for coordinate in coordinates:
        sample_path = _sample_path(job, coordinate)
        try:
            raw = sample_path.read_bytes()
            record = json.loads(raw)
        except (OSError, json.JSONDecodeError, UnicodeDecodeError):
            continue
        if not isinstance(record, dict):
            continue
        status = str(record.get("status", "unknown"))
        statuses[coordinate] = status
        signatures[coordinate] = hashlib.sha256(raw).hexdigest()
        if status in RETAINED_STATUSES:
            retained += 1
            if status in QUALITY_STATUSES:
                successful += 1
            else:
                unparseable += 1
        elif status == "error":
            failed += 1
            evidence: list[str] = []
            if record.get("error"):
                evidence.append(str(record["error"]))
            stderr_path = sample_path.parent / "stderr.txt"
            try:
                evidence.append(stderr_path.read_text(encoding="utf-8", errors="replace"))
            except OSError:
                pass
            errors[coordinate] = redact_message(" | ".join(evidence))
        cost = record.get("total_cost_usd")
        if isinstance(cost, (int, float)) and not isinstance(cost, bool) and math.isfinite(cost):
            total_cost += max(0.0, float(cost))
    expected = len(coordinates)
    return JobProgress(
        expected=expected,
        retained=retained,
        successful=successful,
        failed=failed,
        missing=expected - retained - failed,
        unparseable=unparseable,
        total_cost_usd=total_cost,
        statuses=statuses,
        signatures=signatures,
        errors=errors,
    )


def parse_reset_time(message: str, now: float | None = None) -> float | None:
    """Conservatively parse an explicit future provider reset time."""
    now_ts = time.time() if now is None else now
    now_utc = datetime.fromtimestamp(now_ts, timezone.utc)

    retry_match = re.search(
        r"(?i)\b(?:retry(?:-|\s*)after|resets?\s+in)\s*[:=]?\s*"
        r"(\d+(?:\.\d+)?)\s*(seconds?|secs?|s)\b",
        message,
    )
    if retry_match:
        seconds = float(retry_match.group(1))
        if math.isfinite(seconds) and seconds >= 0:
            return now_ts + seconds

    iso_match = re.search(
        r"\b(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2}(?:\.\d+)?)?"
        r"(?:Z|[+-]\d{2}:?\d{2}))\b",
        message,
    )
    if iso_match:
        iso_text = iso_match.group(1).replace("Z", "+00:00")
        try:
            parsed = datetime.fromisoformat(iso_text)
        except ValueError:
            parsed = None
        if parsed is not None and parsed.tzinfo is not None:
            timestamp = parsed.timestamp()
            if timestamp > now_ts:
                return timestamp

    clock_match = re.search(
        r"(?i)\bresets?\s+(?:at\s+)?(\d{1,2}):(\d{2})\s*([ap]m)?"
        r"\s*\(([A-Za-z_+\-/]+)\)",
        message,
    )
    if not clock_match:
        return None
    hour = int(clock_match.group(1))
    minute = int(clock_match.group(2))
    am_pm = (clock_match.group(3) or "").lower()
    zone_name = clock_match.group(4)
    if minute > 59 or (am_pm and not 1 <= hour <= 12) or (not am_pm and hour > 23):
        return None
    if am_pm:
        hour %= 12
        if am_pm == "pm":
            hour += 12
    try:
        zone = ZoneInfo(zone_name)
    except (ZoneInfoNotFoundError, ValueError):
        return None
    local_now = now_utc.astimezone(zone)
    candidate = local_now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if candidate <= local_now:
        candidate += timedelta(days=1)
    return candidate.timestamp()


def classify_quota(message: str, now: float | None = None) -> QuotaClassification:
    """Classify provider evidence using conservative, ordered signatures."""
    safe = redact_message(message)
    normalized = safe.lower()
    category = "unknown"
    patterns: tuple[tuple[str, tuple[str, ...]], ...] = (
        (
            "authentication",
            (
                r"\bauthentication\b",
                r"\bunauthori[sz]ed\b",
                r"\binvalid (?:api )?key\b",
                r"\bapi key.*(?:invalid|expired|missing)\b",
                r"\b(?:http )?(?:401|403)\b",
                r"\bforbidden\b",
                r"\bpermission denied.*credential",
            ),
        ),
        (
            "exhausted_balance",
            (
                r"\binsufficient[_ ]quota\b",
                r"\b(?:balance|credits?).*(?:exhausted|depleted|insufficient|empty|too low)\b",
                r"\b(?:exhausted|depleted|insufficient).*(?:balance|credits?)\b",
                r"\bno credits? remaining\b",
                r"\bbilling (?:limit|issue|problem)\b",
            ),
        ),
        (
            "weekly_limit",
            (
                r"\bweekly (?:usage )?(?:limit|quota)\b",
                r"\b(?:7|seven)[- ]day (?:limit|quota)\b",
                r"\bweek(?:ly)? limit reached\b",
            ),
        ),
        (
            "session_window",
            (
                r"\bsession(?:[- ]window)? (?:usage )?(?:limit|quota)\b",
                r"\b(?:3|5)[- ]hour (?:limit|window|quota)\b",
                r"\busage limit (?:reached)?.*\bresets?\b",
                r"\bhit (?:your|the) limit.*\bresets?\b",
                r"\blimit reached.*\([a-z_]+/[a-z_]+\)",
            ),
        ),
        (
            "rate_limit",
            (
                r"\brate[- _]limit(?:ed|ing|_error)?\b",
                r"\btoo many requests\b",
                r"\b(?:http )?429\b",
                r"\brequests per (?:minute|second)\b",
            ),
        ),
        (
            "timeout_transient",
            (
                r"\btimed? out\b",
                r"\btimeout\b",
                r"\btemporar(?:y|ily) unavailable\b",
                r"\boverloaded\b",
                r"\bconnection (?:error|reset|closed|refused)\b",
                r"\b(?:http )?5\d\d\b",
                r"\bservice unavailable\b",
            ),
        ),
    )
    for candidate, expressions in patterns:
        if any(re.search(expression, normalized) for expression in expressions):
            category = candidate
            break
    reset_at = parse_reset_time(safe, now=now) if category in RATE_CATEGORIES else None
    return QuotaClassification(category=category, message=safe, reset_at=reset_at)


def classify_evidence(
    messages: Iterable[str], now: float | None = None
) -> tuple[QuotaClassification, ...]:
    return tuple(classify_quota(message, now=now) for message in messages if message)


def _classification_rank(category: str) -> int:
    order = {
        "authentication": 0,
        "exhausted_balance": 1,
        "weekly_limit": 2,
        "session_window": 3,
        "rate_limit": 4,
        "timeout_transient": 5,
        "unknown": 6,
    }
    return order.get(category, 7)


def choose_classification(
    classifications: Sequence[QuotaClassification],
) -> QuotaClassification | None:
    if not classifications:
        return None
    return min(classifications, key=lambda item: _classification_rank(item.category))


def build_epoch_argv(job: JobConfig, concurrency: int) -> list[str]:
    """Build the exact bounded variance epoch argv; never invokes a shell."""
    if concurrency < 1:
        raise SchedulerError("epoch concurrency must be >= 1")
    argv = [
        sys.executable,
        "-m",
        "hera.variance",
        "run",
        "--manifest",
        str(job.manifest),
        "--output",
        str(job.output),
        "--samples",
        str(job.samples),
        "--model",
        job.model,
        "--harness",
        job.harness,
        "--thinking",
        job.thinking,
        "--max-parallel",
        str(concurrency),
        "--max-tasks",
        str(concurrency),
    ]
    if job.campaigns:
        argv.extend(("--campaigns", *job.campaigns))
    if job.experiments:
        argv.extend(("--experiments", *job.experiments))
    return argv


def atomic_write_json(path: Path, value: Any) -> None:
    """Durably replace a JSON file without exposing a partially written file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(value, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary, 0o600)
        os.replace(temporary, path)
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def _pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except OSError as exc:
        return exc.errno == errno.EPERM
    return True


class SingletonLock:
    """O_EXCL PID lock with conservative dead-local-owner recovery."""

    def __init__(self, path: Path):
        self.path = path
        self.owned = False
        self.metadata = {
            "pid": os.getpid(),
            "hostname": socket.gethostname(),
            "started_at": _timestamp(),
        }

    def acquire(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        encoded = (json.dumps(self.metadata, sort_keys=True) + "\n").encode("utf-8")
        for _attempt in range(3):
            try:
                descriptor = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            except FileExistsError:
                try:
                    existing_raw = self.path.read_bytes()
                except FileNotFoundError:
                    continue
                try:
                    existing = json.loads(existing_raw)
                    host = str(existing.get("hostname", ""))
                    pid = int(existing.get("pid", -1))
                except (json.JSONDecodeError, TypeError, ValueError) as exc:
                    raise LockError(f"invalid scheduler lock (refusing to break): {self.path}") from exc
                if host != socket.gethostname() or _pid_alive(pid):
                    raise LockError(f"scheduler already running as pid {pid} on {host}")
                try:
                    if self.path.read_bytes() != existing_raw:
                        continue
                    self.path.unlink()
                except FileNotFoundError:
                    continue
                continue
            try:
                os.write(descriptor, encoded)
                os.fsync(descriptor)
            finally:
                os.close(descriptor)
            self.owned = True
            return
        raise LockError(f"could not safely acquire scheduler lock: {self.path}")

    def release(self) -> None:
        if not self.owned:
            return
        try:
            current = json.loads(self.path.read_text(encoding="utf-8"))
            if current.get("pid") == self.metadata["pid"] and current.get("hostname") == self.metadata["hostname"]:
                self.path.unlink()
        except (OSError, json.JSONDecodeError):
            pass
        self.owned = False

    def __enter__(self) -> SingletonLock:
        self.acquire()
        return self

    def __exit__(self, exc_type: Any, exc: Any, traceback: Any) -> None:
        self.release()


def _timestamp(value: float | None = None) -> str:
    timestamp = time.time() if value is None else value
    return datetime.fromtimestamp(timestamp, timezone.utc).isoformat()


def _load_lane_states(plan: Plan) -> dict[str, LaneState]:
    state_path = plan.state_dir / "state.json"
    persisted: dict[str, Any] = {}
    try:
        raw = json.loads(state_path.read_text(encoding="utf-8"))
        if isinstance(raw, dict) and raw.get("plan_identity") == plan.identity:
            persisted = raw.get("lanes", {})
    except (OSError, json.JSONDecodeError):
        persisted = {}
    states: dict[str, LaneState] = {}
    allowed = set(LaneState.__dataclass_fields__)
    for lane_id, config in plan.lanes.items():
        lane_raw = persisted.get(lane_id, {}) if isinstance(persisted, dict) else {}
        if not isinstance(lane_raw, dict):
            lane_raw = {}
        values = {key: value for key, value in lane_raw.items() if key in allowed}
        try:
            concurrency = int(values.get("concurrency", config.initial_parallel))
            values["concurrency"] = min(
                config.max_parallel, max(config.min_parallel, concurrency)
            )
            state = LaneState(**values)
        except (TypeError, ValueError):
            state = LaneState(concurrency=config.initial_parallel)
        if not isinstance(state.attempt_totals, dict):
            state.attempt_totals = {}
        states[lane_id] = state
    return states


def _job_guard_reason(job: JobConfig, progress: JobProgress, attempts: int) -> str | None:
    if job.max_attempts is not None and attempts >= job.max_attempts:
        return f"attempt guard reached ({attempts}/{job.max_attempts})"
    if job.max_cost_usd is not None and progress.total_cost_usd >= job.max_cost_usd:
        return f"cost guard reached (${progress.total_cost_usd:.6g}/${job.max_cost_usd:.6g})"
    return None


def select_job(
    plan: Plan,
    lane_id: str,
    lane_state: LaneState,
    progress: Mapping[str, JobProgress],
) -> JobConfig | None:
    """Select the highest-priority runnable job, rotating ties by job id."""
    candidates = []
    for job in plan.jobs.values():
        if job.lane != lane_id or not job.enabled or progress[job.id].complete:
            continue
        attempts = int(lane_state.attempt_totals.get(job.id, 0))
        if _job_guard_reason(job, progress[job.id], attempts) is None:
            candidates.append(job)
    if not candidates:
        return None
    top_priority = max(job.priority for job in candidates)
    tied = sorted((job for job in candidates if job.priority == top_priority), key=lambda item: item.id)
    if lane_state.job_cursor is None:
        return tied[0]
    for job in tied:
        if job.id > lane_state.job_cursor:
            return job
    return tied[0]


class Scheduler:
    """Concurrent one-epoch-per-provider-lane supervisor."""

    def __init__(
        self,
        plan: Plan,
        *,
        popen_factory: PopenFactory = subprocess.Popen,
        clock: Clock = time.time,
        sleeper: Sleeper = time.sleep,
    ):
        self.plan = plan
        self.popen_factory = popen_factory
        self.clock = clock
        self.sleeper = sleeper
        self.lane_states = _load_lane_states(plan)
        self.stop_event = threading.Event()
        self._mutex = threading.RLock()
        self._processes: dict[str, subprocess.Popen[str]] = {}
        self._futures: dict[str, Future[EpochResult]] = {}
        self._assigned_workers: dict[str, int] = {}
        self._executor: ThreadPoolExecutor | None = None
        self._created_at = _timestamp(self.clock())

    def _scan_all(self) -> dict[str, JobProgress]:
        return {job_id: scan_job_progress(self.plan, job) for job_id, job in self.plan.jobs.items()}

    def _state_document(self) -> dict[str, Any]:
        return {
            "version": STATE_VERSION,
            "plan_identity": self.plan.identity,
            "plan_digest": self.plan.digest,
            "plan": str(self.plan.path),
            "created_at": self._created_at,
            "updated_at": _timestamp(self.clock()),
            "lanes": {lane_id: state.to_dict() for lane_id, state in self.lane_states.items()},
        }

    def _status_document(self, progress: Mapping[str, JobProgress]) -> dict[str, Any]:
        now = self.clock()
        lanes: dict[str, Any] = {}
        for lane_id, config in self.plan.lanes.items():
            state = self.lane_states[lane_id]
            jobs: dict[str, Any] = {}
            for job in self.plan.jobs.values():
                if job.lane != lane_id:
                    continue
                item = progress[job.id].presentation()
                item.update(
                    {
                        "enabled": job.enabled,
                        "priority": job.priority,
                        "model": job.model,
                        "harness": job.harness,
                        "output": str(job.output),
                        "attempts": int(state.attempt_totals.get(job.id, 0)),
                        "guard": _job_guard_reason(
                            job, progress[job.id], int(state.attempt_totals.get(job.id, 0))
                        ),
                    }
                )
                jobs[job.id] = item
            lanes[lane_id] = {
                "state": state.state,
                "concurrency": state.concurrency,
                "minimum": config.min_parallel,
                "maximum": config.max_parallel,
                "cooldown_until": state.cooldown_until,
                "cooldown_remaining_s": (
                    max(0.0, state.cooldown_until - now) if state.cooldown_until else None
                ),
                "block_reason": state.block_reason,
                "classification": state.classification,
                "last_error": state.last_error,
                "active_pid": state.active_pid,
                "jobs": jobs,
            }
        return {
            "version": STATE_VERSION,
            "plan_identity": self.plan.identity,
            "plan_digest": self.plan.digest,
            "plan": str(self.plan.path),
            "updated_at": _timestamp(now),
            "stopping": self.stop_event.is_set(),
            "lanes": lanes,
        }

    def persist(self, progress: Mapping[str, JobProgress] | None = None) -> None:
        with self._mutex:
            current = dict(progress) if progress is not None else self._scan_all()
            atomic_write_json(self.plan.state_dir / "state.json", self._state_document())
            atomic_write_json(
                self.plan.state_dir / "status.json", self._status_document(current)
            )

    def _consume_unblock_requests(self) -> bool:
        changed = False
        for lane_id in self.plan.lanes:
            if lane_id in self._futures:
                continue
            request_path = _unblock_request_path(self.plan.state_dir, lane_id)
            try:
                request_path.unlink()
            except FileNotFoundError:
                continue
            state = self.lane_states[lane_id]
            state.state = "ready"
            state.cooldown_until = None
            state.block_reason = None
            state.classification = None
            state.last_error = None
            changed = True
            print(f"lane {lane_id}: operator unblock applied", flush=True)
        return changed

    def _lane_ready(self, lane_id: str, now: float) -> bool:
        state = self.lane_states[lane_id]
        if lane_id in self._futures:
            return False
        if state.cooldown_until is not None and now < state.cooldown_until:
            return False
        if state.state in ("cooldown", "blocked"):
            state.state = "ready"
            state.cooldown_until = None
            state.block_reason = None
        return True

    def _new_error_messages(self, before: JobProgress, after: JobProgress) -> list[str]:
        messages: list[str] = []
        for coordinate, error in after.errors.items():
            if before.signatures.get(coordinate) != after.signatures.get(coordinate):
                messages.append(error)
        return messages

    def _run_epoch(
        self, lane_id: str, job: JobConfig, concurrency: int, dry_run: bool
    ) -> EpochResult:
        before = scan_job_progress(self.plan, job)
        argv = build_epoch_argv(job, concurrency)
        if dry_run:
            print(f"dry-run epoch {lane_id}/{job.id}: {json.dumps(argv)}", flush=True)
            return EpochResult(
                lane_id, job.id, concurrency, 0, before, before, (), dry_run=True
            )
        process: subprocess.Popen[str] | None = None
        child_error: str | None = None
        stdout = ""
        stderr = ""
        try:
            process = self.popen_factory(
                argv,
                shell=False,
                start_new_session=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            with self._mutex:
                self._processes[lane_id] = process
                state = self.lane_states[lane_id]
                state.active_pid = process.pid
                self.persist()
            stdout, stderr = process.communicate()
            returncode = int(process.returncode or 0)
        except OSError as exc:
            returncode = 127
            child_error = redact_message(exc)
            if process is not None:
                _terminate_and_wait(process, self.plan.scheduler.shutdown_grace_s)
        except Exception as exc:
            returncode = 127
            child_error = redact_message(exc)
            if process is not None:
                _terminate_and_wait(process, self.plan.scheduler.shutdown_grace_s)
        finally:
            with self._mutex:
                if process is not None and self._processes.get(lane_id) is process:
                    self._processes.pop(lane_id, None)
                self.lane_states[lane_id].active_pid = None
        after = scan_job_progress(self.plan, job)
        messages = self._new_error_messages(before, after)
        if not messages and returncode != 0:
            messages.append(stderr or child_error or f"epoch exited {returncode}")
        classifications = classify_evidence(messages, now=self.clock())
        if returncode != 0 and not child_error and stderr:
            child_error = redact_message(stderr)
        elif returncode != 0 and not child_error and stdout:
            child_error = redact_message(stdout)
        return EpochResult(
            lane_id=lane_id,
            job_id=job.id,
            concurrency=concurrency,
            returncode=returncode,
            before=before,
            after=after,
            classifications=classifications,
            child_error=child_error,
        )

    def _apply_epoch_result(self, result: EpochResult) -> None:
        state = self.lane_states[result.lane_id]
        config = self.plan.lanes[result.lane_id]
        state.active_pid = None
        state.last_completed_at = _timestamp(self.clock())
        if result.dry_run:
            state.state = "ready"
            return
        changed = sum(
            1
            for coordinate, signature in result.after.signatures.items()
            if result.before.signatures.get(coordinate) != signature
        )
        retained_delta = result.after.retained - result.before.retained
        failed_delta = max(0, result.after.failed - result.before.failed)
        state.epoch_total += 1
        state.attempt_totals[result.job_id] = int(state.attempt_totals.get(result.job_id, 0)) + changed
        state.retained_total += max(0, retained_delta)
        state.failed_total += failed_delta
        state.job_cursor = result.job_id
        selected = choose_classification(result.classifications)
        now = self.clock()
        if selected is not None:
            state.classification = selected.category
            state.last_error = selected.message
        if selected is not None and selected.category in HARD_BLOCK_CATEGORIES:
            state.state = "blocked"
            state.block_reason = selected.category
            state.cooldown_until = now + config.hard_block_retry_s
            print(
                f"lane {result.lane_id}: blocked ({selected.category}), "
                f"next probe {_timestamp(state.cooldown_until)}",
                flush=True,
            )
        elif selected is not None and selected.category in RATE_CATEGORIES:
            old = state.concurrency
            state.concurrency = max(
                config.min_parallel, math.floor(state.concurrency * config.decrease_factor)
            )
            state.state = "cooldown"
            state.block_reason = selected.category
            fallback = now + config.rate_cooldown_s
            state.cooldown_until = selected.reset_at if selected.reset_at and selected.reset_at > now else fallback
            print(
                f"lane {result.lane_id}: {selected.category}; concurrency "
                f"{old}->{state.concurrency}, next wake {_timestamp(state.cooldown_until)}",
                flush=True,
            )
        elif retained_delta > 0:
            old = state.concurrency
            if selected is None:
                state.classification = None
            state.concurrency = min(
                config.max_parallel, state.concurrency + config.additive_step
            )
            state.state = "ready"
            state.cooldown_until = None
            state.block_reason = None
            if old != state.concurrency:
                print(
                    f"lane {result.lane_id}: concurrency {old}->{state.concurrency}",
                    flush=True,
                )
        else:
            state.state = "cooldown"
            state.block_reason = selected.category if selected else "no_progress"
            state.cooldown_until = now + self.plan.scheduler.unknown_backoff_s
            if selected is None:
                state.classification = "unknown"
                state.last_error = result.child_error or "epoch made no scientific progress"
        print(
            f"epoch complete {result.lane_id}/{result.job_id}: rc={result.returncode} "
            f"valid_delta={retained_delta:+d} failed_delta={result.after.failed - result.before.failed:+d} "
            f"attempts={changed} classification={state.classification or 'none'}",
            flush=True,
        )

    def request_stop(self) -> None:
        if self.stop_event.is_set():
            return
        self.stop_event.set()
        with self._mutex:
            processes = list(self._processes.values())
        for process in processes:
            _terminate_process_group(process)

    def _finish_shutdown(self) -> None:
        deadline = time.monotonic() + self.plan.scheduler.shutdown_grace_s
        with self._mutex:
            processes = list(self._processes.values())
        for process in processes:
            _terminate_process_group(process)
        for process in processes:
            remaining = max(0.0, deadline - time.monotonic())
            try:
                process.wait(timeout=remaining)
            except subprocess.TimeoutExpired:
                _kill_process_group(process)

    def run(self, *, once: bool = False, dry_run: bool = False) -> int:
        """Run until drained/interrupted, or at most one epoch per lane with once."""
        self.plan.state_dir.mkdir(parents=True, exist_ok=True)
        lock = SingletonLock(self.plan.state_dir / "scheduler.lock")
        attempted_once: set[str] = set()
        lock.acquire()
        for state in self.lane_states.values():
            state.active_pid = None
            if state.state == "running":
                state.state = "ready"
        self._executor = ThreadPoolExecutor(max_workers=max(1, len(self.plan.lanes)))
        try:
            progress = self._scan_all()
            self.persist(progress)
            while not self.stop_event.is_set():
                completed = [
                    lane_id for lane_id, future in self._futures.items() if future.done()
                ]
                for lane_id in completed:
                    future = self._futures.pop(lane_id)
                    self._assigned_workers.pop(lane_id, None)
                    try:
                        result = future.result()
                    except Exception as exc:
                        state = self.lane_states[lane_id]
                        state.state = "cooldown"
                        state.classification = "unknown"
                        state.last_error = redact_message(exc)
                        state.cooldown_until = self.clock() + self.plan.scheduler.unknown_backoff_s
                    else:
                        self._apply_epoch_result(result)
                    self.persist()
                if self._consume_unblock_requests():
                    self.persist()

                progress = self._scan_all()
                enabled = [job for job in self.plan.jobs.values() if job.enabled]
                all_complete = bool(enabled) and all(progress[job.id].complete for job in enabled)
                if all_complete and not self._futures:
                    print("all enabled jobs complete", flush=True)
                    break

                used_workers = sum(self._assigned_workers.values())
                available = max(0, self.plan.scheduler.global_max_workers - used_workers)
                launched = False
                now = self.clock()
                for lane_id in self.plan.lanes:
                    if available <= 0 or self.stop_event.is_set():
                        break
                    if once and lane_id in attempted_once:
                        continue
                    if not self._lane_ready(lane_id, now):
                        continue
                    state = self.lane_states[lane_id]
                    job = select_job(self.plan, lane_id, state, progress)
                    if job is None:
                        continue
                    concurrency = min(state.concurrency, available)
                    if concurrency < 1:
                        continue
                    state.state = "running" if not dry_run else "dry_run"
                    state.last_started_at = _timestamp(now)
                    state.active_pid = None
                    attempted_once.add(lane_id)
                    print(
                        f"epoch start {lane_id}/{job.id}: concurrency={concurrency}",
                        flush=True,
                    )
                    self.persist(progress)
                    self._assigned_workers[lane_id] = concurrency
                    self._futures[lane_id] = self._executor.submit(
                        self._run_epoch, lane_id, job, concurrency, dry_run
                    )
                    available -= concurrency
                    launched = True

                if once and not self._futures:
                    break
                if not launched and not self._futures:
                    runnable_jobs = any(
                        job.enabled and not progress[job.id].complete
                        and _job_guard_reason(
                            job,
                            progress[job.id],
                            int(self.lane_states[job.lane].attempt_totals.get(job.id, 0)),
                        )
                        is None
                        for job in self.plan.jobs.values()
                    )
                    if not runnable_jobs:
                        print("no runnable jobs (disabled, complete, or guarded)", flush=True)
                        break
                    if once:
                        break
                self.sleeper(min(0.2, self.plan.scheduler.poll_interval_s) if self._futures else self.plan.scheduler.poll_interval_s)
            return 0
        finally:
            self.request_stop()
            self._finish_shutdown()
            if self._executor is not None:
                self._executor.shutdown(wait=True, cancel_futures=True)
            for lane_id, future in list(self._futures.items()):
                state = self.lane_states[lane_id]
                if future.cancelled():
                    state.state = "ready"
                    state.active_pid = None
                    continue
                try:
                    result = future.result()
                except Exception as exc:
                    state.state = "cooldown"
                    state.classification = "unknown"
                    state.last_error = redact_message(exc)
                    state.cooldown_until = self.clock() + self.plan.scheduler.unknown_backoff_s
                else:
                    self._apply_epoch_result(result)
            self._futures.clear()
            self._assigned_workers.clear()
            try:
                self.persist()
            finally:
                lock.release()


def _terminate_and_wait(process: subprocess.Popen[str], grace_s: float) -> None:
    _terminate_process_group(process)
    try:
        process.wait(timeout=grace_s)
    except subprocess.TimeoutExpired:
        _kill_process_group(process)


def _terminate_process_group(process: subprocess.Popen[str]) -> None:
    if process.poll() is not None:
        return
    try:
        if os.name == "posix":
            os.killpg(process.pid, signal.SIGTERM)
        else:
            process.terminate()
    except (OSError, ProcessLookupError):
        pass


def _kill_process_group(process: subprocess.Popen[str]) -> None:
    if process.poll() is not None:
        return
    try:
        if os.name == "posix":
            os.killpg(process.pid, signal.SIGKILL)
        else:
            process.kill()
    except (OSError, ProcessLookupError):
        pass


def build_status(plan: Plan) -> dict[str, Any]:
    """Build a current status snapshot without starting or locking a supervisor."""
    scheduler = Scheduler(plan)
    return scheduler._status_document(scheduler._scan_all())


def _unblock_request_path(state_dir: Path, lane_id: str) -> Path:
    suffix = hashlib.sha256(lane_id.encode("utf-8")).hexdigest()[:16]
    return state_dir / f"unblock-{suffix}.json"


def unblock_lane(plan: Plan, lane_id: str) -> None:
    """Clear persisted lane quota state and notify a live supervisor, if any."""
    if lane_id not in plan.lanes:
        raise SchedulerError(f"unknown lane: {lane_id}")
    plan.state_dir.mkdir(parents=True, exist_ok=True)
    request = _unblock_request_path(plan.state_dir, lane_id)
    atomic_write_json(request, {"lane": lane_id, "requested_at": _timestamp()})
    state_path = plan.state_dir / "state.json"
    try:
        state_doc = json.loads(state_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        state_doc = None
    if isinstance(state_doc, dict):
        lane_doc = state_doc.get("lanes", {}).get(lane_id)
        if isinstance(lane_doc, dict):
            lane_doc["state"] = "ready"
            lane_doc["cooldown_until"] = None
            lane_doc["block_reason"] = None
            lane_doc["classification"] = None
            lane_doc["last_error"] = None
            state_doc["updated_at"] = _timestamp()
            atomic_write_json(state_path, state_doc)
    status = build_status(plan)
    atomic_write_json(plan.state_dir / "status.json", status)


def _print_status(status: Mapping[str, Any]) -> None:
    print(f"plan: {status['plan']}")
    for lane_id, lane in status["lanes"].items():
        wake = lane.get("cooldown_until")
        print(
            f"lane {lane_id}: {lane['state']} C={lane['concurrency']} "
            f"pid={lane.get('active_pid') or '-'} reset={_timestamp(wake) if wake else '-'} "
            f"reason={lane.get('block_reason') or '-'}"
        )
        if lane.get("last_error"):
            print(f"  last_error: {lane['last_error']}")
        for job_id, job in lane["jobs"].items():
            print(
                f"  job {job_id}: {'enabled' if job['enabled'] else 'disabled'} "
                f"model={job['model']} retained={job['retained']}/{job['expected']} "
                f"ok={job['successful']} failures={job['failed']}"
            )


def _install_signal_handlers(scheduler: Scheduler) -> dict[int, Any]:
    previous: dict[int, Any] = {}

    def handle_signal(signum: int, frame: Any) -> None:
        print(f"received signal {signum}; stopping owned epochs", file=sys.stderr, flush=True)
        scheduler.request_stop()

    for signum in (signal.SIGINT, signal.SIGTERM):
        previous[signum] = signal.getsignal(signum)
        signal.signal(signum, handle_signal)
    return previous


def _restore_signal_handlers(previous: Mapping[int, Any]) -> None:
    for signum, handler in previous.items():
        signal.signal(signum, handler)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="hera-experiments",
        description="Quota-aware bounded HERA variance experiment scheduler.",
    )
    commands = parser.add_subparsers(dest="command", required=True)
    validate_parser = commands.add_parser("validate", help="validate and print a resolved plan")
    validate_parser.add_argument("--plan", required=True)
    run_parser = commands.add_parser("run", help="run bounded experiment epochs")
    run_parser.add_argument("--plan", required=True)
    run_parser.add_argument("--once", action="store_true")
    run_parser.add_argument("--dry-run", action="store_true")
    status_parser = commands.add_parser("status", help="show reconstructed lane/job status")
    status_parser.add_argument("--plan", required=True)
    status_parser.add_argument("--json", action="store_true", dest="as_json")
    unblock_parser = commands.add_parser("unblock", help="clear a provider lane block")
    unblock_parser.add_argument("--plan", required=True)
    unblock_parser.add_argument("--lane", required=True)
    args = parser.parse_args(argv)
    try:
        plan = load_plan(args.plan)
        if args.command == "validate":
            print(yaml.safe_dump(plan.resolved_dict(), sort_keys=False).rstrip())
            return 0
        if args.command == "status":
            status = build_status(plan)
            if args.as_json:
                print(json.dumps(status, indent=2, sort_keys=True))
            else:
                _print_status(status)
            return 0
        if args.command == "unblock":
            unblock_lane(plan, args.lane)
            print(f"lane {args.lane}: unblock requested")
            return 0
        scheduler = Scheduler(plan)
        previous = _install_signal_handlers(scheduler)
        try:
            return scheduler.run(once=args.once, dry_run=args.dry_run)
        finally:
            _restore_signal_handlers(previous)
    except (SchedulerError, OSError) as exc:
        print(f"error: {redact_message(exc)}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
