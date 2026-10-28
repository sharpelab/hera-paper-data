"""`hera-replay run`: start N copies of one episode in containers — the archived
transcript resumed, or a fresh instance given the brief — and archive what each
agent does next.

Run dir: $HERA_DATA/replay/runs/<case>/<ts>/ with run.json, cut/ (the episode
as materialized, when the case cuts), episodes/<id>/ (one consumed copy per
sample, completed in place, with the container's /tmp as tmp/), harness.log,
summary.csv.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import signal
import socket
import subprocess
import threading
import traceback
import uuid
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

from hera.replay import codex, container, jobs, quota
from hera.replay.archive import open_archive
from hera.replay.mask import load_mask
from hera.replay.case import EFFORTS, Case
from hera.replay.derive import derive
from hera.replay.errors import CutError
from hera.replay.materialize import MEASURE_CELLS, SCHEMA as EPISODE_SCHEMA, STUBS, bundle_session, materialize, write_measure_cells
from hera.replay.rewrite import ARCHIVED_READS, REPO_ROOT, Corpus
from hera.replay.summarize import write_summary

RUN_SCHEMA = "hera-replay-run/1"
MEASURE_SUFFIX = "_measure.ipynb"
HARNESS_PATHS = ("src/hera/replay", "hera/docker")
BRIEF_NAME = "hera_session.md"
UNFINISHED = frozenset(("stall", "timeout", "max_turns"))
ACQUIRES = re.compile(r"\.(?:multi)?(?:mega)?sweep\(|\.watch\(")
TOKEN_KEYS = {
    "input": "input_tokens",
    "cache_creation": "cache_creation_input_tokens",
    "cache_read": "cache_read_input_tokens",
    "output": "output_tokens",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Log:
    """Timestamped lines to a file and to the console; safe from worker threads;
    never carries a credential."""

    def __init__(self, path: Path, secrets: list[str], tee: Path | None = None):
        self.path = path
        self.secrets = secrets
        self.tee = tee
        self._lock = threading.Lock()

    def __call__(self, msg: str) -> None:
        line = f"{now_iso()} {container.redact_text(msg, self.secrets)}"
        with self._lock:
            for path in (self.path, self.tee):
                if path is not None:
                    with path.open("a", encoding="utf-8") as fh:
                        fh.write(line + "\n")
            print(line, flush=True)


# ------------------------------------------------------------------ provenance
def harness_provenance() -> dict:
    """What code ran: the git head, whether the harness paths are dirty, and a hash
    of their contents (the hash is what a dirty tree is compared by)."""
    h = hashlib.sha256()
    for rel in HARNESS_PATHS:
        for p in sorted((REPO_ROOT / rel).rglob("*")):
            if p.is_file() and "__pycache__" not in p.parts:
                h.update(p.relative_to(REPO_ROOT).as_posix().encode())
                h.update(b"\0")
                h.update(p.read_bytes())
                h.update(b"\0")
    head = subprocess.run(["git", "-C", str(REPO_ROOT), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    dirty = subprocess.run(["git", "-C", str(REPO_ROOT), "status", "--porcelain", "--", *HARNESS_PATHS],
                           capture_output=True, text=True, check=True).stdout.splitlines()
    return {"git_head": head, "dirty": dirty, "code_hash": h.hexdigest(), "paths": list(HARNESS_PATHS)}


# ------------------------------------------------------------------ the run
def hera_data_root() -> Path:
    return Path(os.environ.get("HERA_DATA", "/data/sharpelab/hera-data"))


def container_name(case: Case, ts: str, sid: str) -> str:
    return f"hera-replay-{case.name}-{ts}-{sid}"


def run_case(case: Case, *, n: int | None, parallel: int, hera_data: Path, model: str | None = None,
             effort: str | None = None) -> Path:
    """One cell's episodes as a foreground job: `prepare_run`, the episodes on the
    host's slot pools under `parallel`, `finish_run`."""
    item = jobs.EpisodeItem(case, n=n, parallel=parallel, hera_data=hera_data, model=model, effort=effort)
    jobs.run_foreground([item], label=f"run {case.name}")
    return item.ctx["run_dir"]


def prepare_run(case: Case, *, n: int | None, parallel: int | None, hera_data: Path, model: str | None = None,
                effort: str | None = None, harness: dict | None = None, job: dict | None = None,
                tee: Path | None = None) -> dict:
    """Validate the case, resolve its image, materialize its cut and write run.json.
    Returns the context `run_episode` takes; nothing has been launched."""
    n = case.n if n is None else n
    if n < 1 or (parallel is not None and parallel < 1):
        raise CutError(f"n and parallel must be >= 1 (n={n}, parallel={parallel})")
    if effort is not None and effort not in EFFORTS:
        raise CutError(f"effort must be one of {EFFORTS}, not {effort!r}")
    override = {k: v for k, v in (("model", model), ("effort", effort)) if v is not None}
    # Substituted into the case so every consumer — container argv, the pinned
    # model each episode is judged against, the log — sees one model.
    case = replace(case, **override) if override else case
    ts = container.stamp()
    run_dir = Path(hera_data) / "replay" / "runs" / case.name / ts
    if run_dir.exists():
        raise CutError(f"run dir exists: {run_dir}")

    image = container.resolve_image(case.harness_sha or case.corpus_sha, case.condition,
                                    corpus_sha=case.corpus_sha if case.harness_sha else None,
                                    corpus_prompt=case.prompt_source == "corpus")
    meta = container.image_metadata(image["tag"])
    if not meta.get("corpus_sha", "").startswith(case.corpus_sha) or meta.get("condition") != case.condition:
        raise CutError(f"{image['tag']} was built for {meta.get('corpus_sha')}/{meta.get('condition')}, "
                       f"case pins {case.corpus_sha}/{case.condition}")
    # An image with no corpus overlay records its single sha under corpus_sha alone.
    built_harness = meta.get("harness_sha") or meta.get("corpus_sha", "")
    built_prompt = meta.get("prompt_source", "harness")
    if not built_harness.startswith(case.harness_sha or case.corpus_sha) or built_prompt != case.prompt_source:
        raise CutError(f"{image['tag']} was built on harness {built_harness} with {built_prompt} prompts, "
                       f"case pins {case.harness_sha or case.corpus_sha}/{case.prompt_source}")
    credential = container.credential_env(case.runner)
    docker_version = container.docker_version()
    harness = harness_provenance() if harness is None else harness
    archive = episode = None
    if case.source is not None:
        archive = open_archive(case.source)
        if archive.transcript.path.name != case.cut_transcript:
            raise CutError(f"{case.path.name}: cut.transcript is {case.cut_transcript}, the archive's tactical transcript is "
                           f"{archive.transcript.path.name}")
    elif case.episode is not None:
        episode_src = case.episode
        episode = _load_episode(episode_src, case)
        if "jupyter_port" not in episode["container"]:
            raise CutError(f"{episode_src}/episode.json has no container.jupyter_port; re-cut it")
        if case.read_source == "corpus":
            raise CutError(f"{case.path.name}: corpus.reads applies at cut time; a pre-cut episode carries the "
                           f"reads it was cut with ({_corpus_reads(episode)['mode']})")

    run_dir.mkdir(parents=True)
    secrets = list(credential.values())
    log = Log(run_dir / "harness.log", secrets, tee=tee)
    log(f"run {case.name} {ts}: n={n} parallel={parallel} image={image['tag']} ({image['id'][:19]}) model={case.model}"
        + (f" override={override}" if override else "") + (f" job={job['id']}" if job else ""))
    if episode is None:
        episode_src = run_dir / "cut"
        try:
            if archive is not None:
                corpus = Corpus(case.corpus_sha, case.condition) if case.read_source == "corpus" else None
                episode = materialize(archive, derive(archive, case.cut_at), episode_src, close=case.resume_close,
                                      corpus=corpus, stage_transcript=case.start == "resume",
                                      mask=load_mask(case.mask_path) if case.mask_path else None)
            else:
                episode = bundle_session(case.session, case.session_ts, case.session_user, episode_src)
        except BaseException:
            shutil.rmtree(run_dir, ignore_errors=True)
            raise
    mode = "cut" if archive is not None else "precut" if case.episode is not None else "session"
    where = (f"line {episode['cut']['index']} {episode['cut']['uuid']} " if "uuid" in episode["cut"] else "") + episode["cut"]["timestamp"]
    clock = episode.get("clock") or {}
    log(f"{mode}: {where} -> {episode_src}" + (f"; clock starts {clock['start']} ({clock['after_cut_s']} s after the cut)" if clock.get("after_cut_s") else ""))
    first_message = _first_message(case)
    log(f"start: {case.start}, first message from {first_message['source']} ({first_message['lines']} lines)")

    run = {
        "schema": RUN_SCHEMA,
        "case": {"path": str(case.path), **case.raw},
        # The case block is the file verbatim, so what the CLI ran instead is recorded beside it.
        **({"override": override} if override else {}),
        "started_at": now_iso(),
        "n": n,
        "parallel": parallel,
        "start": {"mode": case.start, "first_message": first_message},
        **({"prompt": case.resume_prompt, "resume": {"close": case.resume_close, "prompt": case.resume_prompt}}
           if case.start == "resume" else {}),
        "episode_source": {"mode": mode, "dir": str(episode_src), "cut": episode["cut"],
                           **({"corpus_reads": _corpus_reads(episode)} if case.start == "resume" else {})},
        "image": {**image, "metadata": meta},
        "docker": docker_version,
        "hostname": socket.gethostname(),
        "credential": next(iter(credential)),
        "runner": case.runner,
        "harness": harness,
        **({"job": job} if job else {}),
    }
    (run_dir / "run.json").write_text(json.dumps(run, indent=2) + "\n", encoding="utf-8")
    return {"case": case, "run_dir": run_dir, "ts": ts, "episode_src": episode_src, "run": run, "credential": credential,
            "secrets": secrets, "log": log, "stop": threading.Event(), "ids": [f"{i:02d}" for i in range(n)]}


def finish_run(ctx: dict, statuses: dict[str, str]) -> None:
    run, run_dir, stop = ctx["run"], ctx["run_dir"], ctx["stop"]
    run["ended_at"] = now_iso()
    run["interrupted"] = stop.is_set()
    run["statuses"] = {sid: statuses[sid] for sid in ctx["ids"]}
    (run_dir / "run.json").write_text(json.dumps(run, indent=2) + "\n", encoding="utf-8")
    if any(st != "cancelled" for st in statuses.values()):
        write_summary(run_dir)
    ctx["log"](f"{'interrupted' if stop.is_set() else 'done'}: {run['statuses']}")


class stop_on_signal:
    """SIGINT (Ctrl-C) and SIGTERM (a task kill, `hera-replay cancel`) set the job's stop
    event: in-flight items end as `interrupted` with their containers stopped and
    removed, queued ones are `cancelled`, and every run is recorded. The handlers are
    restored on exit; off the main thread none are installed."""

    SIGNALS = (signal.SIGINT, signal.SIGTERM)

    def __init__(self, stop: threading.Event, log, wake: threading.Event | None = None):
        self.stop = stop
        self.log = log
        self.wake = wake
        self.previous: dict = {}

    def __enter__(self):
        def handler(signum, _frame):
            if not self.stop.is_set():
                self.log(f"{signal.Signals(signum).name}: stopping the run (in-flight episodes are being stopped and recorded)")
            self.stop.set()
            if self.wake is not None:
                self.wake.set()

        if threading.current_thread() is threading.main_thread():
            for sig in self.SIGNALS:
                self.previous[sig] = signal.signal(sig, handler)
        return self

    def __exit__(self, *exc):
        for sig, prev in self.previous.items():
            signal.signal(sig, prev)
        return False


def _first_message(case: Case) -> dict:
    """What the agent is sent on stdin, and where it came from."""
    text = case.resume_prompt if case.start == "resume" else case.brief_text
    return {"source": "resume.prompt" if case.start == "resume" else str(case.brief_path),
            "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(), "lines": len(text.splitlines())}


def _corpus_reads(episode: dict) -> dict:
    return episode.get("transcript", {}).get("corpus_reads", ARCHIVED_READS)


def _load_episode(episode_dir: Path, case: Case) -> dict:
    ej = Path(episode_dir) / "episode.json"
    if not ej.is_file():
        raise CutError(f"not an episode dir (no episode.json): {episode_dir}")
    episode = json.loads(ej.read_text(encoding="utf-8"))
    if episode.get("schema") != EPISODE_SCHEMA:
        raise CutError(f"{ej}: schema {episode.get('schema')!r}, expected {EPISODE_SCHEMA!r}")
    if "run" in episode:
        raise CutError(f"{ej}: already consumed by a run")
    for rel in ("session", "claude-projects", *(f"stubs/{s}" for s in STUBS)):
        if not (Path(episode_dir) / rel).exists():
            raise CutError(f"{episode_dir}: missing {rel}")
    if case.start == "resume" and not episode["container"].get("transcript"):
        raise CutError(f"{episode_dir}: no transcript is staged, so there is nothing to resume; the case needs a fresh start")
    return episode


# ------------------------------------------------------------------ one episode
def run_episode(ctx: dict, sid: str) -> str:
    """Copy the episode, run it, complete its episode.json in place. Returns the status."""
    case: Case = ctx["case"]
    if ctx["stop"].is_set():
        ctx["log"](f"[{sid}] cancelled")
        return "cancelled"
    ep = ctx["run_dir"] / "episodes" / sid
    ep.parent.mkdir(exist_ok=True)
    shutil.copytree(ctx["episode_src"], ep, symlinks=True)
    (ep / "mnt").mkdir()
    (ep / "tmp").mkdir()
    codex_runner = case.runner == "codex"
    if codex_runner:
        (ep / "codex-home").mkdir()
    episode = json.loads((ep / "episode.json").read_text(encoding="utf-8"))
    fresh = case.start == "fresh"
    if fresh:
        # The brief the agent is sent is the brief on disk, and the archived agent's
        # transcript is nowhere the new instance can read it.
        (ep / "session" / BRIEF_NAME).write_text(case.brief_text, encoding="utf-8", newline="")
        shutil.rmtree(ep / "claude-projects")
        (ep / "claude-projects").mkdir()
    # The clock starts where the mask's appended work ended (the cut with none);
    # the mtimes are the cut's, except the files that work wrote.
    clock_epoch = datetime.fromisoformat((episode.get("clock") or {}).get("start") or episode["cut"]["timestamp"]).timestamp()
    mtimes = episode.get("mtimes") or {}
    session_epoch = datetime.fromisoformat(mtimes.get("session") or episode["cut"]["timestamp"]).timestamp()
    session = ep / "session"
    if not (session / MEASURE_CELLS).exists():
        # An episode dir materialized before the hera-watch stub needed a baseline.
        write_measure_cells(session)
    for p in [session, *session.rglob("*")]:
        os.utime(p, (session_epoch, session_epoch))
    for rel, iso in mtimes.items():
        if rel != "session":
            epoch = datetime.fromisoformat(iso).timestamp()
            os.utime(session / rel, (epoch, epoch))
    log = Log(ep / "harness.log", ctx["secrets"])
    rlog = ctx["log"]
    credential = ctx["credential"]
    if codex_runner:
        # Re-read per episode: an earlier episode may have written back a rotated token.
        try:
            credential = container.credential_env(case.runner)
        except container.DockerError as err:
            rlog(f"[{sid}] credential re-read failed, using the run's: {err}")
        ctx["secrets"].extend(v for v in credential.values() if v not in ctx["secrets"])
    name = container_name(case, ctx["ts"], sid)
    session_dir = episode["container"]["session_dir"]
    port = episode["container"]["jupyter_port"]
    session_id = str(uuid.uuid4()) if fresh else episode["cut"]["session_id"]
    jsonl = ep / (f"claude-projects/{episode['container']['projects_slug']}/{session_id}.jsonl" if fresh
                  else episode["container"]["transcript"])
    entries_before = 0 if fresh else _count_lines(jsonl)
    prompt = case.brief_text if fresh else case.resume_prompt
    started = datetime.now(timezone.utc)
    faketime_s = int(started.timestamp() - clock_epoch)
    run_argv = container.run_args(name, ctx["run"]["image"]["tag"], ep, session_dir=session_dir,
                                  stubs={s: ep / "stubs" / s for s in STUBS}, faketime_s=faketime_s,
                                  jupyter_port=port, credential=credential,
                                  codex_home=ep / "codex-home" if codex_runner else None)
    if codex_runner:
        exec_argv = codex.exec_args(container.DOCKER, name, session_dir=session_dir, model=case.model, effort=case.effort)
    else:
        exec_argv = container.exec_args(name, session_dir=session_dir, resume=not fresh, session_id=session_id,
                                        model=case.model, effort=case.effort, max_turns=case.max_turns or 0,
                                        allowed_tools=list(case.allowed_tools or ()), faketime_s=faketime_s)
    meta = ctx["run"]["image"]["metadata"]
    stderr_name = f"{case.runner}-stderr.txt"
    rec: dict = {
        "case": case.name, "run_dir": str(ctx["run_dir"]), "sample": sid, "container": name,
        "started_at": started.isoformat(timespec="seconds"),
        "start": {"mode": case.start, "session_id": session_id, "first_message": ctx["run"]["start"]["first_message"]},
        **({} if fresh else {"prompt": prompt}),
        "model": {"pinned": case.model, "observed": []},
        "runner": case.runner,
        "effort": case.effort, "max_turns": case.max_turns,
        "allowed_tools": None if case.allowed_tools is None else list(case.allowed_tools),
        "timeout_s": case.timeout_s, "stall_s": case.stall_s, "faketime_s": faketime_s,
        "docker": {"run": [container.DOCKER, *container.redact(run_argv)], "exec": exec_argv, "version": ctx["run"]["docker"],
                   "hostname": ctx["run"]["hostname"]},
        "image": ctx["run"]["image"],
        **({"codex_version": {"image": meta.get("codex_version"), "observed": None}} if codex_runner
           else {"claude_version": {"image": meta.get("claude_version"), "observed": None}}),
        "harness": ctx["run"]["harness"],
        "status": None, "guard": None, "returncode": None, "error": None,
        # Filled by _collect; seeded so a collection failure still yields a summary row.
        "result": None, "stop": None, "stop_cell_sweeps": None, "sweep_cell_appended": None, "cost_usd": None,
        "cells_appended": None, "quota": None,
        "turns": {"num_turns": None, "api_messages": 0, "assistant_events": 0, "tool_calls": 0, "events": 0},
    }
    outcome = {"events": [], "returncode": None, "guard": None, "wall_s": None}
    try:
        log(f"docker run: {' '.join(rec['docker']['run'])}")
        container.start_container(run_argv)
        rec["jupyter_ready_s"] = container.wait_for_jupyter(name, port, stop=ctx["stop"])
        if fresh:
            rel = session_dir.removeprefix(container.MEASUREMENTS_ROOT + "/")
            container.open_notebook_sessions(name, port, [f"{rel}/{nb.name}" for nb in sorted(session.glob("*.ipynb"))])
        log(f"jupyterlab ready after {rec['jupyter_ready_s']}s; faketime {-faketime_s}s; exec: {' '.join(exec_argv)}")
        rlog(f"[{sid}] started ({name})")

        def on_guard(which: str) -> None:
            log(f"guard: {which}; stopping {name}")
            container.stop_container(name)

        outcome = container.stream_claude(exec_argv, prompt, ep / "transcript.jsonl", ep / stderr_name,
                                          timeout_s=case.timeout_s, stall_s=case.stall_s,
                                          on_guard=on_guard, on_event=lambda ev: _on_event(ctx, sid, log, ev), stop=ctx["stop"],
                                          extra_guard=codex.marker_guard(session / "episode-stop.json") if codex_runner else None)
        log(f"{case.runner} exit {outcome['returncode']} after {outcome['wall_s']}s (guard: {outcome['guard']})")
    except Exception as err:
        _record_failure(rec, log, err, ctx["secrets"])
        if ctx["stop"].is_set():
            outcome["guard"] = "interrupted"
    finally:
        container.stop_container(name)
        container.remove_container(name)
    ended = datetime.now(timezone.utc)
    rec.update({
        "ended_at": ended.isoformat(timespec="seconds"),
        "wall_s": round((ended - started).total_seconds(), 1),
        "guard": outcome["guard"], "returncode": outcome["returncode"],
    })
    try:
        if codex_runner:
            try:
                rec["auth_writeback"] = codex.write_back_auth(ep, credential, container.CODEX_AUTH_FILE)
            except OSError as err:
                rec["auth_writeback"] = f"failed: {err}"
            if rec["auth_writeback"] not in (None, "unchanged", "written"):
                log(f"auth: the CLI's rotated token did not reach {container.CODEX_AUTH_FILE} ({rec['auth_writeback']})")
            rec["secrets_removed"] = codex.scrub_secrets(ep)
            collected = _collect_codex(ep, ctx["episode_src"], outcome["events"], case.model, meta.get("codex_version"),
                                       stderr_name)
        else:
            collected = _collect(ep, ctx["episode_src"], outcome["events"], case.model, jsonl, entries_before)
            rec["claude_version"]["observed"] = collected.pop("claude_version")["observed"]
        rec.update(collected)
    except Exception as err:
        _record_failure(rec, log, err, ctx["secrets"])
    rec["status"] = quota.status(_landed(_status(rec), rec), rec["quota"])
    episode["run"] = rec
    (ep / "episode.json").write_text(json.dumps(episode, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    log(f"status {rec['status']}: cost {rec['cost_usd']}, {rec['turns']['api_messages']} api messages, "
        f"{rec['turns']['tool_calls']} tool calls, {rec['cells_appended']} measure cells appended")
    rlog(f"[{sid}] {rec['status']} cost={rec['cost_usd']} wall={rec['wall_s']}s cells={rec['cells_appended']}")
    return rec["status"]


def _record_failure(rec: dict, log: Log, err: Exception, secrets: list[str]) -> None:
    """The episode is recorded with its failure; the run goes on."""
    rec["error"] = container.redact_text(f"{type(err).__name__}: {err}", secrets)
    log("error: " + traceback.format_exc().rstrip())


def _on_event(ctx: dict, sid: str, log: Log, ev: dict) -> None:
    _log_event(log, ev)
    if ctx.get("on_event"):
        ctx["on_event"](sid, ev)


def _log_event(log: Log, ev: dict) -> None:
    t = ev.get("type")
    if t == "assistant":
        for b in ev.get("message", {}).get("content", []):
            if b.get("type") == "text":
                log("TEXT: " + b["text"][:300].replace("\n", " "))
            elif b.get("type") == "tool_use":
                log(f"TOOL {b['name']}: " + json.dumps(b.get("input"))[:200])
    elif t == "user":
        for b in ev.get("message", {}).get("content") or []:
            if isinstance(b, dict) and b.get("type") == "tool_result":
                log("RESULT: " + str(b.get("content"))[:200].replace("\n", " "))
    elif t == "result":
        log("RESULT-EVENT: " + json.dumps({k: ev.get(k) for k in ("subtype", "is_error", "num_turns", "duration_ms", "total_cost_usd")}))
    # Codex's stream: one item per command or message.
    elif t in ("item.started", "item.completed"):
        item = ev.get("item") or {}
        kind = item.get("type")
        if kind == "command_execution" and t == "item.started":
            log("TOOL Bash: " + str(item.get("command"))[:200].replace("\n", " "))
        elif kind == "command_execution":
            log(f"RESULT (exit {item.get('exit_code')}): " + str(item.get("aggregated_output"))[:200].replace("\n", " "))
        elif kind == "agent_message":
            log("TEXT: " + str(item.get("text"))[:300].replace("\n", " "))
        elif kind == "error":
            log("STREAM-ERROR: " + str(item.get("message"))[:300])
    elif t in ("turn.completed", "turn.failed"):
        log("RESULT-EVENT: " + json.dumps({"subtype": t, "usage": ev.get("usage"), "error": ev.get("error")}))


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def _count_lines(path: Path) -> int:
    with path.open("rb") as fh:
        return sum(1 for line in fh if line.strip())


# ------------------------------------------------------------------ what the run produced
def _collect(ep: Path, src: Path, events: list[dict], pinned: str, jsonl: Path, entries_before: int) -> dict:
    init = next((e for e in events if e.get("type") == "system" and e.get("subtype") == "init"), None)
    result = next((e for e in reversed(events) if e.get("type") == "result"), None)
    messages: dict[str, dict] = {}
    tool_calls = 0
    assistant_events = 0
    for e in events:
        if e.get("type") != "assistant":
            continue
        assistant_events += 1
        m = e.get("message", {})
        messages[m.get("id")] = m
        tool_calls += sum(1 for b in m.get("content", []) if b.get("type") == "tool_use")
    tokens = tokens_of(result, messages)
    if not jsonl.exists():
        # A fresh instance writes its own session jsonl; the CLI picks the project slug.
        jsonl = next(iter(sorted((ep / "claude-projects").glob(f"*/{jsonl.name}"))), None)
    return {
        "model": {"pinned": pinned, "observed": sorted({m.get("model") for m in messages.values() if m.get("model")})},
        "claude_version": {"observed": init.get("claude_code_version") if init else None},
        "result": None if result is None else {k: result.get(k) for k in
                                                ("subtype", "is_error", "num_turns", "duration_ms", "duration_api_ms",
                                                 "total_cost_usd", "stop_reason", "modelUsage", "usage")},
        **_collect_session(ep, src),
        "turns": {"num_turns": result.get("num_turns") if result else None, "api_messages": len(messages),
                  "assistant_events": assistant_events, "tool_calls": tool_calls, "events": len(events)},
        "tokens": tokens,
        "tokens_source": "result" if result else "assistant_events",
        "cost_usd": result.get("total_cost_usd") if result else None,
        "session_jsonl": {"path": jsonl.relative_to(ep).as_posix() if jsonl else None, "entries_before": entries_before,
                          "entries_after": _count_lines(jsonl) if jsonl else 0},
        "outputs": _outputs("claude-stderr.txt"),
        "quota": quota.evidence(events, stderr=_read(ep / "claude-stderr.txt")),
    }


def _collect_codex(ep: Path, src: Path, events: list, pinned: str, image_version: str | None, stderr_name: str) -> dict:
    """The codex runner's record: the session-derived fields as for claude, the rest from
    the stream and the rollout (`hera.replay.codex.collect`)."""
    return {
        **codex.collect(ep, events, pinned_model=pinned, image_version=image_version),
        **_collect_session(ep, src),
        "outputs": {**_outputs(stderr_name), "rollout": "codex-home", "hook_log": "codex-home/hook-log.jsonl"},
    }


def _collect_session(ep: Path, src: Path) -> dict:
    """What the session dir says after the run, whichever runner wrote it: the stop
    marker, the notebook diff (appended cells written out), the notifications."""
    marker_path = ep / "session" / "episode-stop.json"
    stop = json.loads(marker_path.read_text(encoding="utf-8")) if marker_path.exists() else None
    notebooks, appended = _notebook_diff(src / "session", ep / "session")
    (ep / "appended_cells.json").write_text(json.dumps(appended, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    notifications = ep / "session" / "notifications.jsonl"
    return {
        "stop": stop,
        "stop_cell_sweeps": _stop_cell_sweeps(stop, appended),
        "sweep_cell_appended": _stop_cell_sweeps({"cell_ids": []}, appended) is True,
        "notebooks": notebooks,
        "cells_appended": sum(len(v["appended"]) for k, v in notebooks.items() if k.endswith(MEASURE_SUFFIX)),
        "notifications": _count_lines(notifications) if notifications.exists() else 0,
    }


def _outputs(stderr_name: str) -> dict:
    return {"transcript": "transcript.jsonl", "stderr": stderr_name, "harness_log": "harness.log",
            "appended_cells": "appended_cells.json", "tmp": "tmp", "marker": "session/episode-stop.json",
            "notifications": "session/notifications.jsonl"}


def _stop_cell_sweeps(stop: dict | None, appended: dict) -> bool | None:
    """Whether the handoff that ended the episode was an acquisition: the measure cells
    the stop marker names (every appended one when it names none) call a sweep or a
    watch. False is a prep cell handed off first — the episode ended before its
    measurement landed. None when there is no such cell to read."""
    if stop is None:
        return None
    cells = [c for name, d in appended.items() if name.endswith(MEASURE_SUFFIX)
             for c in d["appended"] if c.get("cell_type") == "code"]
    named = [c for c in cells if c["id"] in stop.get("cell_ids", [])] if stop.get("cell_ids") else cells
    if not named:
        return None
    return any(ACQUIRES.search(c["source"] if isinstance(c["source"], str) else "".join(c["source"])) for c in named)


def tokens_of(result: dict | None, messages: dict[str, dict]) -> dict:
    """Tokens by type. The result event's usage is the session total; the streamed
    assistant events carry each message's usage as it stood when the event was
    emitted (output_tokens still counting), so they are only the fallback when
    the session ended without a result."""
    if result is not None:
        usage = result.get("usage") or {}
        return {k: int(usage.get(src_key) or 0) for k, src_key in TOKEN_KEYS.items()}
    return {k: sum(int((m.get("usage") or {}).get(src_key) or 0) for m in messages.values()) for k, src_key in TOKEN_KEYS.items()}


def _notebook_diff(before_dir: Path, after_dir: Path) -> tuple[dict, dict]:
    """Per notebook: ids appended and sources changed since the cut; the appended
    cells verbatim for appended_cells.json."""
    summary: dict = {}
    detail: dict = {}
    for nb_path in sorted(before_dir.glob("*.ipynb")):
        name = nb_path.name
        before = {c["id"]: c for c in json.loads(nb_path.read_text(encoding="utf-8"))["cells"]}
        after_path = after_dir / name
        if not after_path.exists():
            raise CutError(f"{name} is gone from the session after the run")
        after_cells = json.loads(after_path.read_text(encoding="utf-8"))["cells"]
        appended = [c for c in after_cells if c["id"] not in before]
        modified = [{"id": c["id"], "before": before[c["id"]]["source"], "after": c["source"]}
                    for c in after_cells if c["id"] in before and c["source"] != before[c["id"]]["source"]]
        summary[name] = {"cells_before": len(before), "cells_after": len(after_cells),
                         "appended": [c["id"] for c in appended], "modified": [m["id"] for m in modified]}
        detail[name] = {"appended": appended, "modified": modified}
    return summary, detail


def _landed(status: str, rec: dict) -> str:
    """An episode that ran past a landed sweep cell without a handoff is scored, not
    excluded: the design is in the notebook, only the execute is missing."""
    return "landed_unexecuted" if status in UNFINISHED and rec.get("sweep_cell_appended") else status


def _status(rec: dict) -> str:
    if rec["guard"] == "interrupted":
        return "interrupted"
    if rec["error"]:
        return "error"
    if set(rec["model"]["observed"]) - {rec["model"]["pinned"]}:
        return "model_mismatch"
    if rec.get("runner") == "codex":
        return codex.status(rec)
    if rec["guard"]:
        return rec["guard"]
    result = rec["result"]
    if result is None:
        rec["error"] = f"claude exited {rec['returncode']} without a result event"
        return "error"
    if result["subtype"] == "error_max_turns":
        return "max_turns"
    if result["is_error"] or rec["returncode"] != 0:
        rec["error"] = f"result {result['subtype']}, exit {rec['returncode']}"
        return "error"
    return "ok" if rec["stop"] else "no_stop"
