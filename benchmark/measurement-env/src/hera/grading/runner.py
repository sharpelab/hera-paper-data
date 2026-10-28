"""``hera-grade <episode-dir>... --grader <name>``: run one grader over episode archives.

The unit is an episode dir: ``session/`` inside (the notebooks with outputs, ``data/``, the
cards), everything else beside it.  A replay run's ``episodes/<id>/`` is one; a calibration
fixture is one.  The extractor is ``claude -p`` with ``BASE.md`` + the grader's ``prompt.md`` on
stdin, run in the corpus image the episode ran in, with ``session/`` read-only at ``/episode``
as its working directory, ``nb`` and the venv on PATH, and ``submit_output`` wired to the
grader's ``grade.py check``.  When the container exits, ``grade.py score`` runs on the host.
Everything lands in ``<episode-dir>/grades/<grader>/<stamp>[-NN]/``:

    prompt.md          the prompt as sent
    output.json        what the agent wrote (absent -> status no_output)
    scores.json        grade.py's verdict
    transcript.jsonl   the stream-json events
    claude-stderr.txt
    claude-projects/   the container's session jsonl
    run.json           image, provenance, the docker argv (token redacted), cost, turns, wall, exit

One container per extraction; every (episode, repeat) pair is one foreground job's item
under ``--parallel``, on the host's ``claude`` slot pool (``hera.replay.jobs``).  ``--n K`` runs K independent repeats (calibration; production is 1).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import threading
import time
import traceback
from dataclasses import dataclass
from pathlib import Path

from hera.replay import container, jobs as replay_jobs, quota

REPO = Path(__file__).resolve().parents[3]
GRADERS_ROOT = Path(os.environ.get("HERA_GRADERS", REPO / "hera" / "graders"))
GRADING_SRC = Path(__file__).resolve().parent
IMAGE_ENV = "HERA_GRADER_IMAGE"
NAME_PREFIX = container.GRADE_PREFIX
EFFORTS = ("low", "medium", "high", "xhigh", "max")

ALLOWED_TOOLS = ["Read", "Glob", "Grep", "LS", "Write", "Edit",
                 "Bash(nb:*)", "Bash(submit_output:*)", "Bash(python:*)", "Bash(python3:*)", "Bash(uv run:*)",
                 "Bash(ls:*)", "Bash(cat:*)", "Bash(head:*)", "Bash(tail:*)", "Bash(wc:*)", "Bash(grep:*)",
                 "Bash(find:*)", "Bash(sed:*)", "Bash(pwd)", "Bash(mkdir:*)"]

# Container paths.  The grading package mounts over the image's own copy of its path: the
# venv's editable install resolves ``hera.grading`` there while ``hera.analysis`` stays the
# image's, i.e. the corpus the episode's cells were written against.
C_EPISODE, C_GRADERS, C_RUN = "/episode", "/hera-graders", "/grade-run"
C_GRADING = f"{container.CONTAINER_REPO}/src/hera/grading"
C_VENV_BIN = f"{container.CONTAINER_REPO}/.venv/bin"
C_PATH = ":".join([f"{C_RUN}/bin", C_VENV_BIN, f"{container.CONTAINER_HOME}/.local/bin",
                   "/usr/local/bin", "/usr/bin", "/bin"])
LIMITS = ("--memory", "3g", "--cpus", "2", "--pids-limit", "512")


class GradeError(RuntimeError):
    pass


@dataclass(frozen=True)
class Job:
    episode_dir: Path
    grader: str
    run_dir: Path
    name: str          # container name
    image: str
    model: str
    effort: str
    max_turns: int
    timeout_s: float
    stall_s: float


# ------------------------------------------------------------------ graders and prompts
def grader_dir(name: str) -> Path:
    d = GRADERS_ROOT / name
    if not (d / "prompt.md").exists() or not (d / "grade.py").exists():
        raise GradeError(f"no grader {name!r} under {GRADERS_ROOT} (needs prompt.md and grade.py)")
    return d


def build_prompt(name: str, *, output_path: str, scratch_dir: str) -> str:
    base = (GRADERS_ROOT / "BASE.md").read_text(encoding="utf-8")
    body = (grader_dir(name) / "prompt.md").read_text(encoding="utf-8")
    return (base + "\n" + body).replace("{OUTPUT_PATH}", output_path).replace("{SCRATCH_DIR}", scratch_dir)


def _write_submit_shim(bin_dir: Path) -> None:
    bin_dir.mkdir(parents=True, exist_ok=True)
    shim = bin_dir / "submit_output"
    shim.write_text(f'#!/bin/sh\nexec "{C_VENV_BIN}/python" -m hera.grading.submit "$@"\n', encoding="utf-8")
    shim.chmod(0o755)


# ------------------------------------------------------------------ episodes and images
def session_dir(episode_dir: Path) -> Path:
    s = Path(episode_dir) / "session"
    if not s.is_dir():
        raise GradeError(f"not an episode dir (no session/): {episode_dir}")
    return s


def episode_image(episode_dir: Path) -> dict | None:
    """The image (tag + id) the episode ran in, when it is a replay episode."""
    ej = Path(episode_dir) / "episode.json"
    if not ej.is_file():
        return None
    try:
        img = json.loads(ej.read_text(encoding="utf-8"))["run"]["image"]
        return {"tag": img["tag"], "id": img.get("id")}
    except (KeyError, TypeError, json.JSONDecodeError):
        return None


def resolve_image(tag: str) -> dict:
    proc = container._docker(["image", "inspect", "--format", "{{.Id}}", tag], check=False, timeout=60)
    if proc.returncode:
        raise GradeError(f"image {tag} is not built ({container.BUILD_SCRIPT} builds hera-agent:<sha7>-<condition>)")
    return {"tag": tag, "id": proc.stdout.strip()}


def grading_provenance(grader: str) -> dict:
    """What grading code ran: git head, dirty paths, and a content hash of the harness
    package plus the grader's dir, BASE.md and the device table (the hash is what a dirty tree
    is compared by)."""
    paths = [GRADING_SRC, *(GRADERS_ROOT / f for f in ("BASE.md", "devices.py", "devices.toml")),
             grader_dir(grader)]
    h = hashlib.sha256()
    for root in paths:
        files = [root] if root.is_file() else sorted(p for p in root.rglob("*") if p.is_file())
        for p in files:
            if "__pycache__" in p.parts:
                continue
            h.update(str(p.relative_to(REPO) if p.is_relative_to(REPO) else p).encode())
            h.update(b"\0")
            h.update(p.read_bytes())
            h.update(b"\0")
    git = lambda *a: subprocess.run(["git", "-C", str(REPO), *a], capture_output=True, text=True)  # noqa: E731
    head = git("rev-parse", "HEAD")
    dirty = git("status", "--porcelain", "--", *[str(p) for p in paths])
    return {"git_head": head.stdout.strip() if head.returncode == 0 else None,
            "dirty": dirty.stdout.splitlines() if dirty.returncode == 0 else None,
            "code_hash": h.hexdigest(), "paths": [str(p) for p in paths]}


# ------------------------------------------------------------------ the container
def run_args(job: Job, credential: dict[str, str]) -> list[str]:
    """The full ``docker run`` argv for one extraction (prompt goes on stdin)."""
    session = session_dir(job.episode_dir)
    gdir_c = f"{C_GRADERS}/{job.grader}"
    env = {"HOME": container.CONTAINER_HOME, "PATH": C_PATH,
           "HERA_GRADER_DIR": gdir_c, "HERA_OUTPUT_PATH": f"{C_RUN}/output.json", "HERA_SENTINEL": f"{C_RUN}/accepted",
           "MPLBACKEND": "Agg", "MPLCONFIGDIR": "/tmp/mpl", "PYTHONDONTWRITEBYTECODE": "1", **credential}
    args = [container.DOCKER, "run", "--rm", "-i", "--name", job.name, "--user", container._user_spec(), *LIMITS,
            "-v", f"{session}:{C_EPISODE}:ro",
            "-v", f"{GRADING_SRC}:{C_GRADING}:ro",
            "-v", f"{GRADERS_ROOT}:{C_GRADERS}:ro",
            "-v", f"{job.run_dir}:{C_RUN}",
            "-v", f"{job.run_dir / 'claude-projects'}:{container.CONTAINER_HOME}/.claude/projects",
            "--tmpfs", "/tmp"]
    if (session / ".claude").is_dir():
        # A replay episode carries its stop hook, which ends every Bash call once the
        # stop marker exists; the extractor must not see the project settings.
        args += ["--mount", f"type=tmpfs,destination={C_EPISODE}/.claude,readonly"]
    for k, v in env.items():
        args += ["-e", f"{k}={v}"]
    # --allowedTools is variadic and goes last; the prompt goes on stdin.
    args += ["-w", C_EPISODE, job.image,
             "claude", "-p", "--model", job.model, "--effort", job.effort, "--output-format", "stream-json", "--verbose",
             "--max-turns", str(job.max_turns), "--allowedTools", ",".join(ALLOWED_TOOLS)]
    return args


def _exit_status(outcome: dict | None, result: dict | None) -> tuple[str, str | None]:
    if outcome is None:
        return "harness_error", None
    if outcome["guard"]:
        return outcome["guard"], f"guard {outcome['guard']}"
    if result is None:
        return "error", f"claude -p exited {outcome['returncode']} without a result event"
    if result.get("is_error"):
        return "error", str(result.get("result", ""))[:500]
    if outcome["returncode"] != 0:
        return "error", f"claude -p exited {outcome['returncode']}"
    return "ok", None


def grade_once(job: Job, *, credential: dict[str, str], image: dict, provenance: dict,
               stop: threading.Event | None = None) -> dict:
    """One extraction + score into job.run_dir.  Returns the run.json record.  ``stop``
    ends the extraction as ``interrupted``."""
    run_dir = job.run_dir
    run_dir.mkdir(parents=True, exist_ok=False)
    (run_dir / "scratch").mkdir()
    (run_dir / "claude-projects").mkdir()
    _write_submit_shim(run_dir / "bin")
    gdir = grader_dir(job.grader)
    session = session_dir(job.episode_dir)
    prompt = build_prompt(job.grader, output_path=f"{C_RUN}/output.json", scratch_dir=f"{C_RUN}/scratch")
    (run_dir / "prompt.md").write_text(prompt, encoding="utf-8")
    argv = run_args(job, credential)
    secrets = list(credential.values())
    # A tag can move under an episode (rebuilt image, same sha); the record keeps both ids.
    record: dict = {"episode": str(job.episode_dir), "grader": job.grader, "model": job.model, "effort": job.effort,
                    "max_turns": job.max_turns, "timeout_s": job.timeout_s, "stall_s": job.stall_s,
                    "container": job.name, "image": image, "episode_image": episode_image(job.episode_dir),
                    "grading": provenance,
                    "docker": container.redact(argv), "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    outcome = None
    error = None
    try:
        outcome = container.stream_claude(argv, prompt, run_dir / "transcript.jsonl", run_dir / "claude-stderr.txt",
                                          timeout_s=job.timeout_s, stall_s=job.stall_s,
                                          on_guard=lambda which: container.stop_container(job.name),
                                          **({"stop": stop} if stop is not None else {}))
    except Exception as err:  # the pool goes on; the record says what happened
        error = container.redact_text(f"{type(err).__name__}: {err}\n{traceback.format_exc()}", secrets)[-2000:]
    finally:
        container.remove_container(job.name)
    events = outcome["events"] if outcome else []
    result = next((e for e in reversed(events) if e.get("type") == "result"), None)
    init = next((e for e in events if e.get("type") == "system" and e.get("subtype") == "init"), None)
    exit_status, detail = _exit_status(outcome, result)
    stderr = run_dir / "claude-stderr.txt"
    quota_block = quota.evidence(events, stderr=stderr.read_text(encoding="utf-8", errors="replace") if stderr.exists() else "")
    exit_status = quota.status(exit_status, quota_block)
    record["claude"] = {
        "exit": exit_status, "error": error or detail, "rc": outcome["returncode"] if outcome else None,
        "wall_s": outcome["wall_s"] if outcome else None,
        "cost_usd": result.get("total_cost_usd") if result else None,
        "turns": result.get("num_turns") if result else None,
        "models": sorted((result.get("modelUsage") or {}).keys()) if result else None,
        "version": init.get("claude_code_version") if init else None,
        "quota": quota_block,
    }
    record["accepted"] = (run_dir / "accepted").exists()
    output = run_dir / "output.json"
    scores_path = run_dir / "scores.json"
    if output.exists():
        proc = subprocess.run([sys.executable, str(gdir / "grade.py"), "score", str(output),
                               "--archive", str(session), "-o", str(scores_path)], capture_output=True, text=True)
        if proc.returncode != 0:
            scores_path.write_text(json.dumps(
                {"grader": job.grader, "status": "invalid", "ok": None, "reasons": [proc.stderr[-2000:]]}, indent=2) + "\n")
    else:
        scores_path.write_text(json.dumps(
            {"grader": job.grader, "status": "no_output", "ok": None, "reasons": [record["claude"]["error"] or "no output file"]},
            indent=2) + "\n")
    record["scores"] = json.loads(scores_path.read_text(encoding="utf-8"))
    (run_dir / "run.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return record


# ------------------------------------------------------------------ the pool
def prepare_shared(jobs: list[Job]) -> dict:
    """What every extraction of a batch shares: the credential, each image with its
    build stamp, each grader's provenance."""
    credential = container.credential_env()
    images = {j.image: resolve_image(j.image) for j in jobs}
    for tag, img in images.items():
        img["metadata"] = container.image_metadata(tag)
    return {"credential": credential, "images": images,
            "provenance": {g: grading_provenance(g) for g in {j.grader for j in jobs}}}


def grade_job(job: Job, shared: dict, stop: threading.Event | None = None) -> dict:
    """``grade_once``; a job that fails before it can write its record still yields
    one, with ``exit: harness_error``."""
    try:
        return grade_once(job, credential=shared["credential"], image=shared["images"][job.image],
                          provenance=shared["provenance"][job.grader], stop=stop)
    except Exception as err:
        msg = container.redact_text(f"{type(err).__name__}: {err}", list(shared["credential"].values()))
        return {"episode": str(job.episode_dir), "grader": job.grader, "container": job.name,
                "claude": {"exit": "harness_error", "error": msg, "cost_usd": None, "turns": None, "wall_s": None},
                "scores": {"grader": job.grader, "status": "no_output", "ok": None, "reasons": [msg]}}


def grade_many(jobs: list[Job], *, parallel: int = 4) -> list[dict]:
    """Every job as one foreground job's item; records in job order, one per extraction
    that ran (an interrupt cancels the queued ones)."""
    if not jobs:
        return []
    item = replay_jobs.ExtractionItem(jobs, parallel=parallel)
    replay_jobs.run_foreground([item], label=f"grade {jobs[0].grader}", check_orphans=False)
    return item.records()


def make_jobs(episode_dirs: list[Path], grader: str, *, n: int = 1, image: str | None = None,
              model: str = "claude-opus-5", effort: str = "medium", max_turns: int = 40,
              timeout_s: float = 900.0, stall_s: float = 300.0, stamp: str | None = None) -> list[Job]:
    """(episode, repeat) jobs.  The image is the episode's own unless overridden."""
    if effort not in EFFORTS:
        raise GradeError(f"effort must be one of {EFFORTS}, not {effort!r}")
    stamp = stamp or container.stamp()
    grader_dir(grader)
    jobs = []
    for d in episode_dirs:
        d = Path(d).resolve()
        session_dir(d)
        own = episode_image(d)
        tag = image or (own and own["tag"]) or os.environ.get(IMAGE_ENV)
        if not tag:
            raise GradeError(f"{d}: no episode.json image; pass --image (or set {IMAGE_ENV})")
        for i in range(n):
            run_dir = d / "grades" / grader / (stamp if n == 1 else f"{stamp}-{i:02d}")
            if run_dir.exists():
                raise GradeError(f"run dir exists: {run_dir}")
            jobs.append(Job(d, grader, run_dir, f"{NAME_PREFIX}{stamp}-{len(jobs):03d}", tag, model, effort,
                            max_turns, timeout_s, stall_s))
    return jobs


def summarize(records: list[dict]) -> str:
    """One line per extraction, grouped by episode; agreement per episode when n > 1."""
    lines = []
    by_episode: dict[str, list[dict]] = {}
    for r in records:
        by_episode.setdefault(r["episode"], []).append(r)
    for episode, recs in by_episode.items():
        lines.append(f"== {episode}")
        own = recs[0].get("episode_image")
        if own and own.get("id") and recs[0].get("image", {}).get("id") not in (None, own["id"]):
            lines.append(f"   image {recs[0]['image']['tag']} is {recs[0]['image']['id'][:19]}, the episode ran in {own['id'][:19]}")
        for r in recs:
            s, c = r["scores"], r["claude"]
            lines.append(f"   {s.get('status'):15s} ok={s.get('ok')!s:5s} cost=${(c.get('cost_usd') or 0):.2f} "
                         f"turns={c.get('turns')} wall={c.get('wall_s')}s exit={c.get('exit')}")
        if len(recs) > 1:
            keys = [json.dumps({k: v for k, v in r["scores"].items() if k not in ("notes", "flags", "versions")}, sort_keys=True)
                    for r in recs]
            lines.append(f"   agreement: {keys.count(max(set(keys), key=keys.count))}/{len(keys)} identical score sets")
    costs = [r["claude"].get("cost_usd") for r in records if r["claude"].get("cost_usd") is not None]
    lines.append(f"{len(records)} extractions, ${sum(costs):.2f} over {len(costs)} priced")
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("episode_dirs", nargs="+", type=Path, metavar="episode-dir")
    ap.add_argument("--grader", required=True)
    ap.add_argument("--n", type=int, default=1)
    ap.add_argument("--image", help=f"image tag; default: the episode's own, then ${IMAGE_ENV}")
    ap.add_argument("--parallel", type=int, default=4)
    ap.add_argument("--model", default="claude-opus-5")
    ap.add_argument("--effort", default="medium", choices=EFFORTS)
    ap.add_argument("--max-turns", type=int, default=40)
    ap.add_argument("--timeout", type=float, default=900.0)
    ap.add_argument("--stall", type=float, default=300.0)
    a = ap.parse_args(argv)
    try:
        jobs = make_jobs(a.episode_dirs, a.grader, n=a.n, image=a.image, model=a.model, effort=a.effort,
                         max_turns=a.max_turns, timeout_s=a.timeout, stall_s=a.stall)
        records = grade_many(jobs, parallel=a.parallel)
    except (GradeError, container.DockerError) as err:
        print(f"hera-grade: {err}", file=sys.stderr)
        return 2
    print(summarize(records))
    return 0


if __name__ == "__main__":
    sys.exit(main())
