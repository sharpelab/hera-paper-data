"""Write the episode dir: from a Derivation, or around a hand-built session dir.

Layout (`session/`, the stubs and `claude-projects/` are what the container mounts):

    <dest>/episode.json
    <dest>/session/…                       the materialized frontier
    <dest>/session/.claude/settings.json   the stop hook
    <dest>/session/.claude/measure_cells.json   each measure notebook's cell ids as the episode starts (the hera-watch stub's baseline)
    <dest>/stubs/hera-notify, hera-watch, nb-collab    mounted over ~/.local/bin/<name> in the container
    <dest>/claude-projects/<slug>/<session-id>.jsonl   the transcript a resume continues; empty for a fresh start

Every file under session/ carries the cut timestamp as its mtime.
"""

from __future__ import annotations

import json
import uuid
import os
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path

from hera.replay.archive import AS_ARCHIVED, Archive
from hera.replay.derive import Derivation
from hera.replay.errors import CutError
from hera.replay.mask import Mask, apply_mask
from hera.replay.rewrite import ARCHIVED_READS, Corpus, CorpusReads, PathRewriter
from hera.replay.transcript import CONTAINER_HOME, jupyter_port, project_slug, walk_strings

HOOK_SOURCE = Path(__file__).with_name("episode_stop.py")
STUBS_DIR = Path(__file__).with_name("stubs")
STUBS = ("hera-notify", "hera-watch", "nb-collab")
SCHEMA = "hera-replay-episode/1"
DEFAULT_JUPYTER_PORT = 8888
MEASURE_SUFFIX = "_measure.ipynb"
MEASURE_CELLS = ".claude/measure_cells.json"
STOP_HOOK = {"settings": "session/.claude/settings.json", "script": "session/.claude/episode_stop.py", "marker": "session/episode-stop.json"}


def _settings() -> dict:
    return {
        "hooks": {
            "PreToolUse": [
                {
                    "matcher": "Bash|ScheduleWakeup|Monitor",
                    "hooks": [
                        {
                            "type": "command",
                            "command": 'python3 "$CLAUDE_PROJECT_DIR/.claude/episode_stop.py"',
                        }
                    ],
                }
            ]
        }
    }


BACKGROUND_TASK_KEYS = ("backgroundTaskId", "taskId")


def materialize(archive: Archive, d: Derivation, dest: Path, close: str | None = None,
                corpus: Corpus | None = None, stage_transcript: bool = True, mask: Mask | None = None) -> dict:
    """`close` is the synthetic assistant line written after the cut's tool_result
    so the transcript ends on an assistant turn: the CLI then resumes it cleanly
    instead of closing it with its own "Continue from where you left off" pair.
    `corpus` re-serves the pre-cut corpus reads from that sha; without it they stay
    as the session archived them. A fresh start stages no transcript: the session
    dir is the same cut, and `claude-projects/` starts empty. `mask` edits the
    materialized state after the cut (see `hera.replay.mask`)."""
    dest = Path(dest)
    if dest.exists():
        raise CutError(f"dest exists: {dest}")
    try:
        return _build(archive, d, dest, close, corpus, stage_transcript, mask)
    except BaseException:
        shutil.rmtree(dest, ignore_errors=True)
        raise


def bundle_session(src: Path, ts: datetime, user: str, dest: Path) -> dict:
    """The episode dir around a hand-built session dir: no transcript behind it, so
    nothing is derived — the dir is taken as it stands at `ts`."""
    src, dest = Path(src), Path(dest)
    if dest.exists():
        raise CutError(f"dest exists: {dest}")
    if not src.is_dir():
        raise CutError(f"session dir not found: {src}")
    for required in ("hera_session.md", "rig_card.md"):
        if not (src / required).is_file():
            raise CutError(f"{required} missing from {src}")
    if (src / ".claude").exists():
        raise CutError(f"{src}/.claude exists; the episode's stop hook goes there")
    try:
        session = dest / "session"
        shutil.copytree(src, session)
        _install_harness(dest, session, ts)
        (dest / "claude-projects").mkdir()
        session_dir = f"{CONTAINER_HOME}/measurements/{user}/{src.name}"
        episode = {
            "schema": SCHEMA,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "cut": {"source": str(src), "transcript": None, "timestamp": ts.isoformat()},
            "container": {"home": CONTAINER_HOME, "session_dir": session_dir, "projects_slug": project_slug(session_dir),
                          "transcript": None, "jupyter_port": DEFAULT_JUPYTER_PORT},
            "resume": None,
            "stop_hook": STOP_HOOK,
            "stubs": {name: f"stubs/{name}" for name in STUBS},
            "mtimes": {"session": ts.isoformat()},
        }
        (dest / "episode.json").write_text(json.dumps(episode, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return episode
    except BaseException:
        shutil.rmtree(dest, ignore_errors=True)
        raise


def write_measure_cells(session: Path) -> dict:
    """Each measure notebook's cell ids, the mask's appended ones included: the
    hera-watch stub arms once a code cell outside this set lands."""
    cells = {nb.name: [c["id"] for c in json.loads(nb.read_text(encoding="utf-8"))["cells"]]
             for nb in sorted(session.glob(f"*{MEASURE_SUFFIX}"))}
    (session / MEASURE_CELLS).write_text(json.dumps(cells, indent=2) + "\n", encoding="utf-8")
    return cells


def _install_harness(dest: Path, session: Path, ts: datetime) -> None:
    """The stop hook, the stubs, the measure-cell baseline, and the cut time as every
    session file's mtime."""
    claude_dir = session / ".claude"
    claude_dir.mkdir()
    shutil.copy2(HOOK_SOURCE, claude_dir / "episode_stop.py")
    (claude_dir / "settings.json").write_text(json.dumps(_settings(), indent=2) + "\n", encoding="utf-8")
    write_measure_cells(session)
    stubs = dest / "stubs"
    stubs.mkdir()
    for name in STUBS:
        shutil.copy2(STUBS_DIR / name, stubs / name)
        (stubs / name).chmod(0o755)
    epoch = ts.timestamp()
    for p in [session, *session.rglob("*")]:
        os.utime(p, (epoch, epoch))


def _synthetic_close(cut_raw: dict, cut_ts: datetime, text: str) -> dict:
    ts = (cut_ts + timedelta(seconds=1)).astimezone(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
    return {
        "parentUuid": cut_raw["uuid"], "isSidechain": False, "type": "assistant", "uuid": str(uuid.uuid4()), "timestamp": ts,
        "cwd": cut_raw.get("cwd"), "sessionId": cut_raw.get("sessionId"), "version": cut_raw.get("version"),
        "isApiErrorMessage": False, "userType": "external", "entrypoint": "cli",
        "message": {"id": "hera-replay-close", "model": "<synthetic>", "role": "assistant", "type": "message",
                    "stop_reason": "end_turn", "content": [{"type": "text", "text": text}],
                    "usage": {"input_tokens": 0, "output_tokens": 0}},
    }


def _build(archive: Archive, d: Derivation, dest: Path, close: str | None, corpus: Corpus | None,
           stage_transcript: bool, mask: Mask | None = None) -> dict:
    t = archive.transcript
    layout = t.layout
    session = dest / "session"
    session.mkdir(parents=True)
    materialized: set[str] = set()

    as_archived = []
    for name in AS_ARCHIVED:
        src = archive.root / name
        if src.is_file():
            shutil.copy2(src, session / name)
            as_archived.append(name)
            materialized.add(name)
    for required in ("hera_session.md", "rig_card.md"):
        if required not in as_archived:
            raise CutError(f"{required} missing from the archive")

    notebooks = {}
    for name, (nb, cut) in d.notebooks.items():
        (session / name).write_text(json.dumps(nb, indent=1, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
        materialized.add(name)
        notebooks[name] = {
            "cells_total": cut.cells_total,
            "cells_kept": cut.keep,
            "cut_cell": cut.cut_cell,
            "basis": cut.basis,
            "referenced_ids": cut.referenced,
            "code_cells_renumbered": cut.code_cells_renumbered,
            "outputs_stripped": cut.outputs_stripped,
        }

    for rid in d.runs.kept:
        src = archive.run_dirs[rid]
        shutil.copytree(src, session / "data" / str(rid))
        materialized.update(str(p.relative_to(archive.root)) for p in src.rglob("*") if p.is_file())

    files = {}
    for rel, st in d.files.items():
        entry = {"basis": st.basis, "ops": st.ops, "corroborated_by": st.corroborated_by}
        if st.blanked:
            entry["blanked"] = st.blanked
        if not st.materialized:
            entry["not_materialized"] = st.reason
            files[rel] = entry
            continue
        out = session / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(st.content, bytes):
            out.write_bytes(st.content)
        else:
            out.write_text(st.content, encoding="utf-8", newline="")
        entry["bytes"] = out.stat().st_size
        files[rel] = entry
        materialized.add(rel)

    if "device_card.md" not in materialized:
        raise CutError("device_card.md is not in the state: every session has one; the cut could not place it")

    not_materialized = {}
    for p in sorted(archive.root.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(archive.root).as_posix()
        if rel in materialized or rel.startswith((t.path.parent.name + "/",)):
            continue
        if rel in files:
            not_materialized[rel] = files[rel]["not_materialized"]
        elif rel.startswith("data/"):
            not_materialized[rel] = "run not observed before the cut" if rel.split("/")[1].isdigit() else "not a run dir"
        elif rel.startswith(".claude/"):
            not_materialized[rel] = "rig CLI state"
        else:
            not_materialized[rel] = "written after the cut, and no op before the cut"

    masked = apply_mask(mask, session, d.cut_ts) if mask is not None else None
    _install_harness(dest, session, d.cut_ts)
    # The episode's clock starts when the mask's appended work ended; those
    # notebooks were last written then, everything else at the cut.
    clock = datetime.fromisoformat(masked["clock"]) if masked else d.cut_ts
    mtimes = {"session": d.cut_ts.isoformat()}
    for name in sorted({a["notebook"] for a in masked["appended"]} if masked else ()):
        mtimes[name] = clock.isoformat()
        os.utime(session / name, (clock.timestamp(), clock.timestamp()))

    slug = layout.container_projects_slug
    (dest / "claude-projects").mkdir()
    staged = _stage_transcript(archive, d, dest, close, corpus) if stage_transcript else None
    targets = {
        "measurement_env": sorted(d.targets.measurement_env),
        "cli_task_outputs": sorted(d.targets.cli_task_outputs),
        "volatile": sorted(d.targets.volatile),
        "blanked": d.targets.blanked + [{"path": rel, "reason": st.blanked} for rel, st in d.files.items() if st.blanked],
    }

    episode = {
        "schema": SCHEMA,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "cut": {
            "source": str(archive.root),
            "transcript": t.path.relative_to(archive.root).as_posix(),
            "session_id": t.session_id,
            "uuid": d.cut.uuid,
            "index": d.cut.index,
            "timestamp": d.cut_ts.isoformat(),
            "tool": d.cut_call.name,
        },
        "rig": {"cwd": layout.cwd, "style": layout.style, "home": layout.home, "user": layout.user, "session": layout.session},
        "container": {
            "home": CONTAINER_HOME,
            "session_dir": layout.container_session_dir,
            "projects_slug": slug,
            "transcript": staged["path"] if staged else None,
            "jupyter_port": jupyter_port(t, d.cut.index),
        },
        "resume": {"close": close, "close_uuid": staged["close_uuid"],
                   "background_task_ids_stripped": staged["task_ids_stripped"]} if staged else None,
        "transcript": {
            "entries_total": len(t.entries),
            **({"entries_kept": staged["kept"], "rewrites": staged["rewrites"], "corpus_reads": staged["corpus_reads"]}
               if staged else {}),
            "targets": targets,
        },
        "notebooks": notebooks,
        "mask": masked,
        "runs": {
            "kept": d.runs.kept,
            "in_flight_dropped": d.runs.in_flight,
            "end_from_mtime": {str(k): v for k, v in sorted(d.runs.end_from_mtime.items())},
            "unobserved": d.runs.unobserved,
            "first_seen": {str(k): v for k, v in sorted(d.runs.first_seen.items())},
            "first_seen_in_notebook": {str(k): v for k, v in sorted(d.runs.first_seen_in_notebook.items())},
            "first_seen_in_text": {str(k): v for k, v in sorted(d.runs.first_seen_in_text.items())},
        },
        "files": {"as_archived": as_archived, "reconstructed": files},
        "not_materialized": not_materialized,
        "stop_hook": STOP_HOOK,
        "stubs": {name: f"stubs/{name}" for name in STUBS},
        "clock": {"start": clock.isoformat(), "after_cut_s": int((clock - d.cut_ts).total_seconds())},
        "mtimes": mtimes,
    }
    (dest / "episode.json").write_text(json.dumps(episode, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return episode


def _stage_transcript(archive: Archive, d: Derivation, dest: Path, close: str | None, corpus: Corpus | None) -> dict:
    """The transcript prefix up to the cut, in container paths, where the CLI resumes it from."""
    t = archive.transcript
    rewriter = PathRewriter(t.layout)
    corpus_reads = CorpusReads(t, d.cut.index, corpus) if corpus is not None else None
    proj = dest / "claude-projects" / t.layout.container_projects_slug
    proj.mkdir()
    jsonl = proj / f"{t.session_id}.jsonl"
    kept = 0
    task_ids_stripped = 0
    close_uuid = None
    with jsonl.open("w", encoding="utf-8") as fh:
        for e in t.entries:
            if e.index > d.cut.index:
                break
            raw = e.raw if corpus_reads is None else corpus_reads.apply(e.index, e.raw)
            raw = walk_strings(raw, rewriter)
            # The CLI reports every background task it finds in these records as
            # orphaned on resume; the visible tool-result text is untouched.
            tur = raw.get("toolUseResult")
            if isinstance(tur, dict):
                for key in BACKGROUND_TASK_KEYS:
                    if key in tur:
                        del tur[key]
                        task_ids_stripped += 1
            fh.write(json.dumps(raw, separators=(",", ":"), ensure_ascii=False) + "\n")
            kept += 1
            if e.index == d.cut.index and close:
                entry = _synthetic_close(raw, d.cut_ts, close)
                close_uuid = entry["uuid"]
                fh.write(json.dumps(entry, separators=(",", ":"), ensure_ascii=False) + "\n")

    return {"path": jsonl.relative_to(dest).as_posix(), "kept": kept, "close_uuid": close_uuid,
            "task_ids_stripped": task_ids_stripped, "rewrites": rewriter.tally.as_json(),
            "corpus_reads": ARCHIVED_READS if corpus_reads is None else corpus_reads.as_json()}
