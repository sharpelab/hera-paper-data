#!/usr/bin/env python3
"""run_metrics.py — per-run metrics extraction for the HERA paper (`hera-metrics`).

Implements hera/docs/run-metrics-spec.md. The spec + this tool live in
measurement-env (inside the corpus freeze tag); the manifest and outputs live
with the paper in hera-paper/analysis/ (--paper-root, env HERA_PAPER).

Reads <paper>/analysis/runs.yaml, walks each run's archive, and writes:

  <paper>/analysis/metrics/<run_id>.json    full structured metrics
  <paper>/analysis/messages/<run_id>.csv    timestamped human messages (label col)
  <paper>/analysis/reports/<run_id>.md      rendered run report
  <paper>/analysis/runs.csv                 one headline row per extracted run

Usage:
  hera-metrics qc0426-r3                     # one manifest run
  hera-metrics --all                         # every manifest run
  hera-metrics --archive <fresh-archive>     # capture-at-close: draft a new run
"""
from __future__ import annotations

import argparse
import csv
import glob
import json
import os
import re
import sys
from datetime import datetime, timezone
from typing import Any, TypedDict

import yaml

from tools.hera_utilization import compute as _util_compute


class Sweep(TypedDict):
    id: str
    start: float
    end: float
    slug: str

# This tool's own repo (src/tools/run_metrics.py -> src/tools -> src -> repo).
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SHARPELAB = os.path.dirname(REPO)
# The measurement-env checkout is this repo (holds the archives referenced by
# the manifest's `measurement-env/...` paths).
MENV = REPO
# hera-paper — the manifest + outputs live here. --paper-root / HERA_PAPER
# override; default the sibling under ~/sharpelab.
DEFAULT_PAPER_ROOT = os.environ.get(
    "HERA_PAPER", os.path.join(SHARPELAB, "hera-paper")
)

# Time-of-run pricing, $/Mtok. Cache read = 0.1x input; cache write 1.25x (5m)
# and 2x (1h). Source: Anthropic list prices at the time of the runs (June and
# August 2026). The transcript's model field drops the "[1m]" context suffix;
# the 1M window carries no price premium on these models.
PRICING = {
    "claude-opus-5": {"in": 5.0, "out": 25.0, "cr": 0.5, "cw5": 6.25, "cw1h": 10.0},
    "claude-opus-4-8": {"in": 5.0, "out": 25.0, "cr": 0.5, "cw5": 6.25, "cw1h": 10.0},
    "claude-opus-4-7": {"in": 5.0, "out": 25.0, "cr": 0.5, "cw5": 6.25, "cw1h": 10.0},
    "claude-sonnet-4-6": {"in": 3.0, "out": 15.0, "cr": 0.3, "cw5": 3.75, "cw1h": 6.0},
    "claude-fable-5": {"in": 10.0, "out": 50.0, "cr": 1.0, "cw5": 12.5, "cw1h": 20.0},
}

# t_final_decision heuristic: latest HERA-landed markdown cell (or session_notes
# line) whose text hits one of these. HERA labels its call/closeout cells.
DECISION_RE = re.compile(
    r"final call|final decision|verdict|closeout|close-out|session close|"
    r"final determination|final write-?up",
    re.IGNORECASE,
)


def iso2ep(s: str) -> float:
    return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()


def ep2iso(t: float | None) -> str | None:
    if t is None:
        return None
    return datetime.fromtimestamp(t, tz=timezone.utc).isoformat(timespec="seconds")


def cell_text(cell: dict) -> str:
    src = cell.get("source", "")
    return "".join(src) if isinstance(src, list) else src


def hera_meta(cell: dict) -> dict:
    h = cell.get("metadata", {}).get("hera")
    return h if isinstance(h, dict) else {}


# --------------------------------------------------------------------- sweeps
def sweep_metrics(archive: str, end_epoch: float | None = None) -> dict:
    sweeps: list[Sweep] = []
    for path in glob.glob(os.path.join(archive, "data", "*", "metadata.json")):
        try:
            m = json.load(open(path, encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if m.get("start_time") is None or m.get("end_time") is None:
            continue
        comments = m.get("comments") or []
        sweeps.append(
            {
                "id": os.path.basename(os.path.dirname(path)),
                "start": float(m["start_time"]),
                "end": float(m["end_time"]),
                "slug": comments[0] if comments else "",
            }
        )
    if end_epoch is not None:
        sweeps = [s for s in sweeps if s["start"] < end_epoch]
    sweeps.sort(key=lambda s: s["start"])
    by_recipe: dict[str, list[Any]] = {}
    for s in sweeps:
        r = by_recipe.setdefault(s["slug"], [0, 0.0])
        r[0] += 1
        r[1] += (s["end"] - s["start"]) / 3600
    return {
        "n_sweeps": len(sweeps),
        "t_first_sweep": ep2iso(sweeps[0]["start"]) if sweeps else None,
        "t_last_sweep_end": ep2iso(max(s["end"] for s in sweeps)) if sweeps else None,
        "sweep_span_h": (max(s["end"] for s in sweeps) - sweeps[0]["start"]) / 3600
        if sweeps
        else None,
        "longest_sweep_h": max((s["end"] - s["start"]) for s in sweeps) / 3600
        if sweeps
        else None,
        "sweeps_by_recipe": {
            k: {"n": v[0], "hours": round(v[1], 3)} for k, v in sorted(by_recipe.items())
        },
        "_sweep_windows": [(s["start"], s["end"]) for s in sweeps],
    }


# ---------------------------------------------------------------- utilization
def utilization(archive: str, measure_nb: str | None, end_epoch: float | None = None) -> dict | None:
    # hera-utilization now lives in this same project — call compute() directly
    # (no nested `uv run` subprocess). It raises SystemExit when a session has
    # no in-window sweeps; callers already gate on n_sweeps, but guard anyway.
    try:
        return _util_compute(archive, measure_nb, end_epoch)
    except SystemExit as e:
        print(f"  ! hera-utilization: {e}", file=sys.stderr)
        return None


# ------------------------------------------------------------- corpus provenance
def corpus_provenance(archive: str) -> dict:
    """Read the corpus_provenance.json stamp hera-mksession writes at session
    creation. Absent for runs predating the stamp (all June runs) -> nulls."""
    path = os.path.join(archive, "corpus_provenance.json")
    if not os.path.exists(path):
        return {"corpus_commit": None, "corpus_dirty": None, "source": "unstamped"}
    try:
        d = json.load(open(path, encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"corpus_commit": None, "corpus_dirty": None, "source": "unreadable"}
    return {
        "corpus_commit": d.get("corpus_commit"),
        "corpus_dirty": d.get("corpus_dirty"),
        "source": "stamp",
    }


# ----------------------------------------------------------------- transcript
def classify_user_text(text: str, is_first: bool) -> str:
    if "Request interrupted" in text:
        return "interrupt"
    if text.startswith("# Autonomous loop") or text.startswith("Run the autonomous"):
        return "loop_tick"
    if text.startswith("<task-notification>"):
        return "task_notification"
    if text.startswith("Caveat: The messages below") or text.startswith("<command-"):
        return "admin"
    if is_first and text.startswith("#") and len(text) > 1500:
        return "admin"  # brief injection
    return "human"


def _file_cwds(path: str) -> set[str]:
    cwds = set()
    for line in open(path, encoding="utf-8", errors="replace"):
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            continue
        c = d.get("cwd")
        if c:
            cwds.add(os.path.basename(c.replace("\\", "/")))
    return cwds


def harness_session_totals(archive: str) -> dict | None:
    """The harness's own record of the session, when the archive carries one.

    Claude Code keeps a per-project entry in ~/.claude.json (lastSessionId,
    lastModelUsage, lastCost, lastDuration, ...) that outlives a deleted
    transcript. Archives whose transcript was lost store a copy at
    transcripts/recovered/claude-project-entry.json. The totals are the
    harness's accounting for the whole session window (every API call the
    session made, priced by the harness); they are reported beside, never
    folded into, the transcript-derived token counts.
    """
    path = os.path.join(archive, "transcripts", "recovered", "claude-project-entry.json")
    if not os.path.exists(path):
        return None
    e = json.load(open(path, encoding="utf-8"))
    entry = e.get("entry", e)
    usage = entry.get("lastModelUsage") or {}
    return {
        "source": "claude-project-entry.json",
        "project_dir": e.get("project_dir"),
        "session_id": entry.get("lastSessionId"),
        "harness_version": entry.get("lastVersionBase"),
        "graceful_shutdown": entry.get("lastGracefulShutdown"),
        "window_open_h": (entry["lastDuration"] / 3.6e6) if entry.get("lastDuration") else None,
        "api_time_h": (entry["lastAPIDuration"] / 3.6e6) if entry.get("lastAPIDuration") else None,
        "tokens_by_model": {
            m: {
                "in": u.get("inputTokens", 0),
                "out": u.get("outputTokens", 0),
                "cr": u.get("cacheReadInputTokens", 0),
                "cw": u.get("cacheCreationInputTokens", 0),
                "cost_usd": u.get("costUSD"),
            }
            for m, u in usage.items()
        },
        "cost_usd": entry.get("lastCost"),
    }


def transcript_metrics(archive: str, session_basename: str | None = None) -> dict:
    files = sorted(glob.glob(os.path.join(archive, "transcripts", "*.jsonl")))
    # include recovered/ partials
    files += sorted(glob.glob(os.path.join(archive, "transcripts", "recovered", "*.jsonl")))
    # Some archives carry extraneous transcripts (e.g. hera-session inits run
    # from the shared measurement_env dir, or a neighbour session's files).
    # Attribute by cwd: when the manifest names the rig session dir, only
    # files whose cwd matches it are the session's; the rest are counted as
    # extraneous and ignored, even when nothing matches (a lost transcript
    # must read as absent, not as whichever file is left in the archive).
    n_extraneous = 0
    if session_basename and files:
        matching = [f for f in files if session_basename in _file_cwds(f)]
        n_extraneous = len(files) - len(matching)
        files = matching
    usage: dict[str, dict] = {}
    tools: dict[str, int] = {}
    counts = {
        "human": 0, "loop_tick": 0, "task_notification": 0,
        "admin": 0, "interrupt": 0,
    }
    human_msgs: list[tuple[float, str]] = []
    n_assistant = n_user = n_sidechain = 0
    t_first = t_last = None
    seen_uuids: set[str] = set()
    # One API response is written as one assistant entry PER CONTENT BLOCK,
    # each repeating the same usage object — sum usage once per message.id.
    seen_msg_ids: set[str] = set()

    for f in files:
        first_text_seen = False
        for line in open(f, encoding="utf-8", errors="replace"):
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            uid = d.get("uuid")
            if uid:
                if uid in seen_uuids:
                    continue  # duplicated entries across recovered files
                seen_uuids.add(uid)
            ts = d.get("timestamp")
            ep = iso2ep(ts) if ts else None
            if ep is not None:
                t_first = ep if t_first is None else min(t_first, ep)
                t_last = ep if t_last is None else max(t_last, ep)
            typ = d.get("type")
            sidechain = bool(d.get("isSidechain"))
            if typ == "assistant":
                if sidechain:
                    n_sidechain += 1
                else:
                    n_assistant += 1
                msg = d.get("message", {})
                model = msg.get("model", "?")
                mid = msg.get("id")
                if mid not in seen_msg_ids:
                    if mid:
                        seen_msg_ids.add(mid)
                    u = msg.get("usage") or {}
                    agg = usage.setdefault(
                        model, {"in": 0, "out": 0, "cr": 0, "cw5": 0, "cw1h": 0, "n_requests": 0}
                    )
                    agg["n_requests"] += 1
                    agg["in"] += u.get("input_tokens", 0)
                    agg["out"] += u.get("output_tokens", 0)
                    agg["cr"] += u.get("cache_read_input_tokens", 0)
                    cc = u.get("cache_creation") or {}
                    agg["cw5"] += cc.get("ephemeral_5m_input_tokens", 0)
                    agg["cw1h"] += cc.get("ephemeral_1h_input_tokens", 0)
                for b in msg.get("content") or []:
                    if isinstance(b, dict) and b.get("type") == "tool_use":
                        name = b.get("name", "?")
                        if name == "Bash":
                            cmd = (b.get("input") or {}).get("command", "")
                            for probe in ("nb-collab", "hera-watch", "hera-notify", "nb "):
                                if probe in cmd:
                                    name = f"Bash[{probe.strip()}]"
                                    break
                        tools[name] = tools.get(name, 0) + 1
            elif typ == "user" and not sidechain:
                n_user += 1
                cont = d.get("message", {}).get("content")
                texts = (
                    [cont]
                    if isinstance(cont, str)
                    else [
                        x.get("text", "")
                        for x in cont or []
                        if isinstance(x, dict) and x.get("type") == "text"
                    ]
                )
                for t in texts:
                    cls = classify_user_text(t, not first_text_seen)
                    first_text_seen = True
                    counts[cls] += 1
                    if cls == "human" and ep is not None:
                        human_msgs.append((ep, t))

    human_msgs.sort()
    cost = 0.0
    cost_known = True
    for model, u in usage.items():
        if not any(u[k] for k in ("in", "out", "cr", "cw5", "cw1h")):
            continue  # e.g. <synthetic> harness messages
        p = PRICING.get(model)
        if not p:
            cost_known = False
            continue
        cost += (
            u["in"] * p["in"] + u["out"] * p["out"] + u["cr"] * p["cr"]
            + u["cw5"] * p["cw5"] + u["cw1h"] * p["cw1h"]
        ) / 1e6

    return {
        "n_transcript_files": len(files),
        "n_extraneous_transcripts": n_extraneous,
        "t_transcript_first": ep2iso(t_first),
        "t_transcript_last": ep2iso(t_last),
        "transcript_span_h": (t_last - t_first) / 3600
        if t_first is not None and t_last is not None
        else None,
        "n_assistant_entries": n_assistant,
        "n_api_requests": len(seen_msg_ids),
        "n_sidechain_turns": n_sidechain,
        "n_user_entries": n_user,
        "message_counts": counts,
        "tool_calls": dict(sorted(tools.items(), key=lambda kv: -kv[1])),
        "n_tool_calls": sum(tools.values()),
        "tokens_by_model": usage,
        "cost_usd_est": round(cost, 2) if usage else None,
        "cost_complete": cost_known,
        "_human_msgs": human_msgs,
        "_t_first": t_first,
        "_t_last": t_last,
    }


# ------------------------------------------------------------------ notebooks
def notebook_metrics(nb_dir: str) -> dict:
    measures = sorted(glob.glob(os.path.join(nb_dir, "*_measure.ipynb")))
    anas = sorted(glob.glob(os.path.join(nb_dir, "*_ana.ipynb")))
    out: dict = {
        "measure_notebook": measures[0] if measures else None,
        "ana_notebook": anas[0] if anas else None,
    }
    decision_candidates = []
    if measures:
        cells = json.load(open(measures[0], encoding="utf-8"))["cells"]
        n_hera = n_slot = n_exec = n_unexec = 0
        for c in cells:
            h = hera_meta(c)
            if h.get("slot") and not h.get("appended_at"):
                n_slot += 1
            if h.get("appended_at"):
                n_hera += 1
                if c["cell_type"] == "code":
                    ran = (
                        bool(c.get("outputs"))
                        or c.get("execution_count") is not None
                        or bool(c.get("metadata", {}).get("execution"))
                    )
                    n_exec += ran
                    n_unexec += not ran
                if c["cell_type"] == "markdown" and DECISION_RE.search(cell_text(c)):
                    decision_candidates.append(
                        {
                            "source": "measure-nb",
                            "t": h["appended_at"],
                            "excerpt": cell_text(c)[:160],
                        }
                    )
        out.update(
            n_cells=len(cells),
            n_hera_cells=n_hera,
            n_slot_cells=n_slot,
            n_human_cells=len(cells) - n_hera - n_slot,
            n_hera_executed=n_exec,
            n_hera_unexecuted=n_unexec,
        )
    if anas:
        cells = json.load(open(anas[0], encoding="utf-8"))["cells"]
        figs = sum(
            1
            for c in cells
            for o in c.get("outputs", [])
            if "image/png" in (o.get("data") or {})
        )
        out.update(n_ana_cells=len(cells), n_ana_figures=figs)
        for c in cells:
            h = hera_meta(c)
            if (
                c["cell_type"] == "markdown"
                and h.get("appended_at")
                and DECISION_RE.search(cell_text(c))
            ):
                decision_candidates.append(
                    {"source": "ana-nb", "t": h["appended_at"], "excerpt": cell_text(c)[:160]}
                )
    out["decision_candidates"] = sorted(decision_candidates, key=lambda d: d["t"])
    return out


def scratch_metrics(nb_dir: str) -> dict:
    root = os.path.join(nb_dir, "hera_scratch")
    ext: dict[str, int] = {}
    loc = figs = nbs = 0
    if os.path.isdir(root):
        for dirpath, _dirs, files in os.walk(root):
            for fn in files:
                p = os.path.join(dirpath, fn)
                e = os.path.splitext(fn)[1].lower() or "(none)"
                ext[e] = ext.get(e, 0) + 1
                try:
                    if e == ".py":
                        loc += sum(
                            1 for line in open(p, errors="replace") if line.strip()
                        )
                    elif e == ".png":
                        figs += 1
                    elif e == ".ipynb":
                        nbs += 1
                        j = json.load(open(p, encoding="utf-8"))
                        for c in j.get("cells", []):
                            if c["cell_type"] == "code":
                                loc += sum(1 for line in c["source"] if line.strip())
                            figs += sum(
                                1
                                for o in c.get("outputs", [])
                                if "image/png" in (o.get("data") or {})
                            )
                except (OSError, json.JSONDecodeError):
                    continue
    return {
        "n_scratch_files": sum(ext.values()),
        "scratch_by_ext": dict(sorted(ext.items())),
        "scratch_loc": loc,
        "n_scratch_figures": figs,
        "n_scratch_notebooks": nbs,
    }


# ----------------------------------------------------------------- assembly
def longest_unattended(
    human_msgs: list[tuple[float, str]],
    t_first: float | None,
    t_last: float | None,
    sweep_windows: list[tuple[float, float]],
) -> float | None:
    if t_first is None or t_last is None:
        return None
    marks = [t_first] + [t for t, _ in human_msgs] + [t_last]
    best = 0.0
    for a, b in zip(marks, marks[1:]):
        if b - a <= best:
            continue
        if any(a <= s0 < b for s0, _ in sweep_windows):
            best = b - a
    return best / 3600 if best else 0.0


def extract_run(run: dict, out_dirs: dict) -> dict:
    # archive paths are SHARPELAB-relative; route "measurement-env/..." through
    # MENV so HERA_MENV overrides pick up archives living on the same branch.
    rel = run["archive"]
    if rel.startswith("measurement-env/"):
        archive = os.path.join(MENV, rel[len("measurement-env/"):])
    else:
        archive = os.path.join(SHARPELAB, rel)
    nb_dir = os.path.join(archive, "artifacts") if run["layout"] == "artifacts" else archive
    print(f"== {run['run_id']}  ({archive})")

    # session_end_override (ISO ts): operator-ruled session boundary — e.g. a
    # deliverable-complete standby later extended by the operator; the
    # extension is post-session and counts as a (strong) intervention.
    end_iso = run.get("session_end_override")
    end_ep = iso2ep(str(end_iso)) if end_iso else None

    sw = sweep_metrics(archive, end_ep)
    nb = notebook_metrics(nb_dir)
    util = (
        utilization(archive, nb.get("measure_notebook"), end_ep)
        if sw["n_sweeps"]
        else None
    )
    tr = transcript_metrics(archive, os.path.basename(run.get("rig_session_dir", "")))
    # session_start_override (ISO ts): the measurement agent's launch time,
    # from the setup agent's transcript or the rig's file times, for archives
    # whose own transcript is missing or truncated at the start. Supplies the
    # anchor that decision_h, session_h and longest_unattended measure from.
    start_iso = run.get("session_start_override")
    if start_iso:
        tr["_t_first"] = iso2ep(str(start_iso))
        tr["t_transcript_first"] = tr["t_transcript_first"] or ep2iso(tr["_t_first"])
    tr["harness_session_totals"] = harness_session_totals(archive)
    sc = scratch_metrics(nb_dir)

    # corpus_commit: manifest override > stamp in the archive > null (unstamped).
    prov = corpus_provenance(archive)
    if run.get("corpus_commit"):
        prov = {"corpus_commit": run["corpus_commit"], "corpus_dirty": prov.get("corpus_dirty"), "source": "manifest"}

    # session_h: closeout counts (ruling 2026-07-06) -> transcript span,
    # unless the manifest overrides (post-session chat in the same transcript).
    # For lossy transcripts (partial/export-only) the transcript span
    # understates the session — fall back to the widest available envelope
    # (sweep span, HERA cell-stamp range).
    session_h = run.get("session_h_override") or tr["transcript_span_h"]
    if end_ep is not None and tr["_t_first"] is not None:
        session_h = (end_ep - tr["_t_first"]) / 3600
    elif run.get("transcript") != "full":
        stamps = [d["t"] for d in nb.get("decision_candidates", [])]
        candidates = [session_h or 0.0]
        if sw["sweep_span_h"]:
            candidates.append(sw["sweep_span_h"])
        if tr["_t_first"] is not None and stamps:
            candidates.append((iso2ep(stamps[-1]) - tr["_t_first"]) / 3600)
        session_h = max(candidates) or None
        # partial transcripts also make the cost a meaningless lower bound
        tr["cost_usd_est"] = None

    # t_final_decision: manifest override > latest decision-labeled HERA cell.
    t_dec = run.get("t_final_decision")
    dec_source = "manifest" if t_dec else None
    if not t_dec and nb.get("decision_candidates"):
        t_dec = nb["decision_candidates"][-1]["t"]
        dec_source = "heuristic:" + nb["decision_candidates"][-1]["source"]
    decision_h = None
    if t_dec and tr["_t_first"]:
        decision_h = (iso2ep(t_dec) - tr["_t_first"]) / 3600

    lu_end = end_ep if end_ep is not None else tr["_t_last"]
    # Without the session's own transcript the operator messages are unknown,
    # so the unattended stretch is unknown too (not "the whole session").
    lu = None if tr["n_transcript_files"] == 0 else longest_unattended(
        [(t, x) for t, x in tr["_human_msgs"] if lu_end is None or t <= lu_end],
        tr["_t_first"],
        lu_end,
        sw["_sweep_windows"],
    )

    metrics = {
        "run_id": run["run_id"],
        "manifest": {k: v for k, v in run.items() if not k.startswith("_")},
        "provenance": prov,
        "time": {
            "t_transcript_first": tr["t_transcript_first"],
            "t_transcript_last": tr["t_transcript_last"],
            "transcript_span_h": tr["transcript_span_h"],
            "session_h": session_h,
            "t_final_decision": t_dec,
            "t_final_decision_source": dec_source,
            "decision_h": decision_h,
            "t_first_sweep": sw["t_first_sweep"],
            "t_last_sweep_end": sw["t_last_sweep_end"],
            "sweep_span_h": sw["sweep_span_h"],
            "measuring_h": (util["measuring_s"] / 3600) if util else None,
            "longest_sweep_h": sw["longest_sweep_h"],
        },
        "sweeps": {
            "n_sweeps": sw["n_sweeps"],
            "by_recipe": sw["sweeps_by_recipe"],
        },
        "utilization": None
        if not util
        else {
            "raw": util["raw_utilization"],
            "hil": util["hil_utilization"],
            "frac_measuring": util["measuring_s"] / util["span_s"],
            "frac_hera_court": util["hera_court_s"] / util["span_s"],
            "frac_human_court": util["human_court_s"] / util["span_s"],
            "hera_court_h": util["hera_court_s"] / 3600,
            "human_court_h": util["human_court_s"] / 3600,
            "n_lands": util["n_lands"],
            "gaps": util["gaps"],
        },
        "messages": {
            k: tr[k]
            for k in (
                "n_transcript_files", "n_extraneous_transcripts",
                "n_assistant_entries", "n_api_requests",
                "n_sidechain_turns", "n_user_entries", "message_counts",
                "n_tool_calls", "tool_calls", "tokens_by_model",
                "cost_usd_est", "cost_complete", "harness_session_totals",
            )
        },
        "notebook": {k: v for k, v in nb.items() if k != "decision_candidates"},
        "decision_candidates": nb.get("decision_candidates", []),
        "scratch": sc,
        "autonomy": {
            "mode": run["mode"],
            "n_human_msgs": tr["message_counts"]["human"],
            "n_interrupts": tr["message_counts"]["interrupt"],
            "longest_unattended_h": lu,
            # confirmed count from the manifest (§5 counting rule); null until
            # the labeling review pass settles it.
            "n_interventions": run.get("n_interventions"),
        },
        "extracted_at": datetime.now(tz=timezone.utc).isoformat(timespec="seconds"),
    }

    # write metrics json
    mpath = os.path.join(out_dirs["metrics"], f"{run['run_id']}.json")
    json.dump(metrics, open(mpath, "w", encoding="utf-8"), indent=1, default=str)

    # write messages csv (label column blank -> draft-labeled -> reviewed);
    # re-extraction preserves labels already assigned (keyed on ts+text).
    cpath = os.path.join(out_dirs["messages"], f"{run['run_id']}.csv")
    existing: dict[tuple[str, str], str] = {}
    if os.path.exists(cpath):
        for row in csv.DictReader(open(cpath, encoding="utf-8")):
            if row.get("label"):
                existing[(row["timestamp_utc"], row["text"])] = row["label"]
    with open(cpath, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["timestamp_utc", "label", "text"])
        for ep, text in tr["_human_msgs"]:
            ts = ep2iso(ep) or ""  # ep is always a float here -> ts is str
            w.writerow([ts, existing.get((ts, text), ""), text])

    render_report(metrics, os.path.join(out_dirs["reports"], f"{run['run_id']}.md"))
    return metrics


# ------------------------------------------------------------------- report
def _f(x, fmt="{:.2f}", dash="—"):
    return fmt.format(x) if x is not None else dash


def render_report(m: dict, path: str) -> None:
    man, t, u, msg = m["manifest"], m["time"], m["utilization"], m["messages"]
    au, nb, sc = m["autonomy"], m["notebook"], m["scratch"]
    L = []
    L.append(f"# Run report — {m['run_id']} ({man['date']})")
    L.append("")
    L.append(f"*Generated {m['extracted_at']} by hera-metrics (measurement-env).*")
    L.append("")
    L.append("## Identity")
    L.append("")
    L.append("| field | value |")
    L.append("|---|---|")
    L.append(f"| device / rig | {man['device']} / {man['rig']} |")
    L.append(f"| mode | {man['mode']} |")
    L.append(f"| archive | `{man['archive']}` |")
    L.append(
        f"| transcript | {man['transcript']} ({msg['n_transcript_files']} file(s)"
        + (f"; {msg['n_extraneous_transcripts']} other-agent file(s) ignored"
           if msg.get("n_extraneous_transcripts") else "")
        + ") |"
    )
    L.append(f"| variability set | {man.get('variability_set', False)} |")
    if man.get("caveats"):
        L.append(f"| caveats | {', '.join(man['caveats'])} |")
    L.append("")
    L.append("## Time")
    L.append("")
    L.append("| metric | value |")
    L.append("|---|---|")
    if t["t_transcript_last"] is None:
        L.append(
            f"| transcript span | no session transcript; session start"
            f" {t['t_transcript_first'] or '—'} from the manifest override |"
        )
    else:
        L.append(
            f"| transcript span | {t['t_transcript_first']} → {t['t_transcript_last']}"
            f" = **{_f(t['transcript_span_h'])} h** |"
        )
    L.append(f"| session_h | **{_f(t['session_h'])} h** (closeout counts) |")
    L.append(
        f"| t_final_decision | {t['t_final_decision'] or '—'}"
        f" ({t['t_final_decision_source'] or 'none found'}) |"
    )
    L.append(f"| decision_h | **{_f(t['decision_h'])} h** |")
    L.append(f"| sweep span | {_f(t['sweep_span_h'])} h |")
    L.append(f"| measuring | **{_f(t['measuring_h'])} h** ({m['sweeps']['n_sweeps']} sweeps) |")
    L.append(f"| longest sweep | {_f(t['longest_sweep_h'])} h |")
    L.append("")
    L.append("Sweeps by recipe:")
    L.append("")
    L.append("| recipe | n | hours |")
    L.append("|---|---|---|")
    for slug, v in sorted(
        m["sweeps"]["by_recipe"].items(), key=lambda kv: -kv[1]["hours"]
    ):
        L.append(f"| {slug or '(none)'} | {v['n']} | {v['hours']:.2f} |")
    L.append("")
    L.append("## Utilization")
    L.append("")
    if u:
        L.append("| component | fraction | hours |")
        L.append("|---|---|---|")
        L.append(f"| measuring (active ops) | {u['frac_measuring']:.1%} | {_f(t['measuring_h'])} |")
        L.append(f"| HERA court (thinking) | {u['frac_hera_court']:.1%} | {_f(u['hera_court_h'])} |")
        L.append(f"| human court | {u['frac_human_court']:.1%} | {_f(u['human_court_h'])} |")
        L.append("")
        L.append(f"raw = **{u['raw']:.1%}** · HIL-adjusted = **{u['hil']:.1%}**"
                 f" · {u['n_lands']} cell lands · per-gap table in the run JSON")
    else:
        L.append("*(no sweep data — utilization unavailable)*")
    L.append("")
    L.append("## Messages & tokens")
    L.append("")
    c = msg["message_counts"]
    L.append("| class | n |")
    L.append("|---|---|")
    L.append(f"| human messages | **{c['human']}** |")
    L.append(f"| loop ticks | {c['loop_tick']} |")
    L.append(f"| task notifications | {c['task_notification']} |")
    L.append(f"| admin | {c['admin']} |")
    L.append(f"| interrupts | {c['interrupt']} |")
    L.append("")
    L.append(
        f"{msg['n_api_requests']} API requests ({msg['n_assistant_entries']} assistant entries"
        + (f", +{msg['n_sidechain_turns']} sidechain" if msg["n_sidechain_turns"] else "")
        + f") · {msg['n_tool_calls']} tool calls"
    )
    L.append("")
    top = list(msg["tool_calls"].items())[:12]
    L.append(" · ".join(f"{k} {v}" for k, v in top))
    L.append("")
    if msg["tokens_by_model"]:
        L.append("| model | in | out | cache read | cache write (5m/1h) |")
        L.append("|---|---|---|---|---|")
        for mod, uu in msg["tokens_by_model"].items():
            L.append(
                f"| {mod} | {uu['in']:,} | {uu['out']:,} | {uu['cr']:,} |"
                f" {uu['cw5']:,} / {uu['cw1h']:,} |"
            )
        L.append("")
        note = "" if msg["cost_complete"] else " (INCOMPLETE — unknown model in mix)"
        L.append(
            f"**cost ≈ ${_f(msg['cost_usd_est'])}** (API list-price equivalent;"
            f" sessions ran on subscription){note}"
        )
    else:
        L.append("*(no token data — transcript missing/export-only)*")
    hs = msg.get("harness_session_totals")
    if hs:
        L.append("")
        L.append(
            f"Harness record (`{hs['source']}`, session `{hs['session_id']}`, Claude Code"
            f" {hs['harness_version']}): window open {_f(hs['window_open_h'])} h ·"
            f" harness cost ${_f(hs['cost_usd'])} · "
            + " · ".join(
                f"{m}: in {u['in']:,} / out {u['out']:,} / cache read {u['cr']:,} /"
                f" cache write {u['cw']:,}"
                for m, u in hs["tokens_by_model"].items()
            )
        )
        L.append("")
        L.append(
            "The harness total covers every API call of the session window as the"
            " harness priced it, so it is not the per-response list-price figure above"
            " and is not entered in runs.csv."
        )
    L.append("")
    L.append("## Notebook & scratch")
    L.append("")
    if nb.get("n_cells") is not None:
        L.append(
            f"measure nb: {nb['n_cells']} cells — {nb['n_hera_cells']} HERA-landed"
            f" ({nb['n_hera_executed']} executed, {nb['n_hera_unexecuted']} never-executed),"
            f" {nb['n_slot_cells']} slot, {nb['n_human_cells']} human"
        )
    if nb.get("n_ana_cells") is not None:
        L.append(f"ana nb: {nb['n_ana_cells']} cells, {nb['n_ana_figures']} figures")
    L.append(
        f"hera_scratch: {sc['n_scratch_files']} files, {sc['scratch_loc']} LOC,"
        f" {sc['n_scratch_figures']} figures, {sc['n_scratch_notebooks']} notebooks"
    )
    L.append("")
    L.append("## Autonomy")
    L.append("")
    L.append("| metric | value |")
    L.append("|---|---|")
    L.append(f"| mode | {au['mode']} |")
    L.append(f"| human messages | {au['n_human_msgs']} |")
    L.append(f"| interrupts | {au['n_interrupts']} |")
    L.append(f"| longest unattended (sweeps running) | **{_f(au['longest_unattended_h'])} h** |")
    L.append(
        f"| n_interventions | {au['n_interventions'] if au['n_interventions'] is not None else '⟦pending label review⟧'} |"
    )
    L.append("")
    if m["decision_candidates"]:
        L.append("## Decision candidates (heuristic)")
        L.append("")
        for d in m["decision_candidates"][-5:]:
            L.append(f"- `{d['t']}` [{d['source']}] {d['excerpt'].strip()!r}")
        L.append("")
    L.append("## Expert evaluation — reserved")
    L.append("")
    L.append("quality_expert: ⟦pending⟧ · dossier: ⟦pending⟧")
    L.append("")
    open(path, "w", encoding="utf-8").write("\n".join(L))


def csv_row(m: dict) -> dict:
    """Headline runs.csv row from a per-run metrics dict."""
    t, u, msg, au = m["time"], m["utilization"], m["messages"], m["autonomy"]
    return {
        "run_id": m["run_id"],
        "device": m["manifest"]["device"],
        "date": m["manifest"]["date"],
        "mode": m["manifest"]["mode"],
        "corpus_commit": (m.get("provenance") or {}).get("corpus_commit"),
        "session_h": round(t["session_h"], 2) if t["session_h"] else None,
        "decision_h": round(t["decision_h"], 2) if t["decision_h"] else None,
        "measuring_h": round(t["measuring_h"], 2) if t["measuring_h"] else None,
        "n_sweeps": m["sweeps"]["n_sweeps"],
        "util_raw": round(u["raw"], 3) if u else None,
        "util_hil": round(u["hil"], 3) if u else None,
        "frac_hera_court": round(u["frac_hera_court"], 3) if u else None,
        "frac_human_court": round(u["frac_human_court"], 3) if u else None,
        "n_human_msgs": au["n_human_msgs"],
        "n_interventions": au["n_interventions"],
        "longest_unattended_h": round(au["longest_unattended_h"], 2)
        if au["longest_unattended_h"] is not None
        else None,
        "tokens_out": sum(v["out"] for v in msg["tokens_by_model"].values()) or None,
        "cost_usd_est": msg["cost_usd_est"],
        "quality_expert": None,
    }


def rebuild_runs_csv(metrics_dir: str, out_csv: str) -> None:
    rows = [
        csv_row(json.load(open(f, encoding="utf-8")))
        for f in sorted(glob.glob(os.path.join(metrics_dir, "*.json")))
    ]
    if not rows:
        return
    with open(out_csv, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


# --------------------------------------------------------- capture-at-close
def _detect_rig(archive: str) -> str | None:
    p = os.path.join(archive, "rig_card.md")
    if os.path.exists(p):
        head = open(p, encoding="utf-8", errors="replace").readline().lower()
        if "vti" in head:
            return "vti"
        if "toploader" in head:
            return "toploader"
    return None


def _detect_transcript(archive: str) -> str:
    if glob.glob(os.path.join(archive, "transcripts", "*.jsonl")):
        return "full"
    if glob.glob(os.path.join(archive, "transcripts", "recovered", "*.jsonl")):
        return "partial"
    if glob.glob(os.path.join(archive, "transcripts", "*.md")):
        return "export-only"
    return "full"


def _detect_mode(archive: str) -> str | None:
    p = os.path.join(archive, "hera_session.md")
    if not os.path.exists(p):
        return None
    txt = open(p, encoding="utf-8", errors="replace").read()
    m = re.search(r"\bE([01])\b", txt)
    return f"E{m.group(1)}" if m else None


def _parse_archive_name(archive: str) -> tuple[str | None, str | None]:
    base = os.path.basename(os.path.normpath(archive))
    m = re.match(r"(\d{4}-\d{2}-\d{2})-(.+)$", base)
    if not m:
        return None, None
    return m.group(1), m.group(2).split("-", 1)[0]


def _manifest_archive_path(archive: str) -> str:
    abs_a = os.path.abspath(archive)
    repo_a = os.path.abspath(REPO)
    if abs_a == repo_a or abs_a.startswith(repo_a + os.sep):
        return "measurement-env/" + os.path.relpath(abs_a, repo_a)
    return os.path.relpath(abs_a, SHARPELAB)


def draft_from_archive(archive: str, paper_root: str, rig: str | None,
                       device: str | None, mode: str | None) -> int:
    """Capture-at-close: extract a fresh archive not yet in the manifest, write
    draft outputs, and print a DRAFT manifest stanza + csv row. Mechanical fields
    are auto-derived; judgment fields print as HAND-CHECK, never auto-filled."""
    if not os.path.isdir(archive):
        raise SystemExit(f"not a directory: {archive}")

    date, dev = _parse_archive_name(archive)
    device = device or dev
    rig = rig or _detect_rig(archive)
    mode = mode or _detect_mode(archive)
    transcript = _detect_transcript(archive)
    prov = corpus_provenance(archive)
    run_id = f"{(device or 'device').lower()}-{date or 'DATE'}"  # provisional

    run = {
        "run_id": run_id,
        "device": device,
        "rig": rig,
        "date": date,
        "mode": mode or "E1",
        "archive": _manifest_archive_path(archive),
        "rig_session_dir": "",
        "layout": "root",
        "transcript": transcript,
        "variability_set": False,
        "corpus_commit": None,  # from the stamp via prov; kept null in manifest
        "t_final_decision": None,
        "n_interventions": None,
        "caveats": [],
    }

    out_dirs = {
        name: os.path.join(paper_root, "analysis", "drafts", name)
        for name in ("metrics", "messages", "reports")
    }
    for d in out_dirs.values():
        os.makedirs(d, exist_ok=True)
    metrics = extract_run(run, out_dirs)
    row = csv_row(metrics)

    dec = metrics["time"]["t_final_decision"]
    dec_src = metrics["time"]["t_final_decision_source"]
    dec_val = f'"{dec}"' if dec else "null"
    cc = prov["corpus_commit"]
    cc_note = "" if cc else f"  # HAND-CHECK: corpus {prov['source']} (no join key)"

    print("\n" + "=" * 70)
    print("DRAFT manifest stanza — review HAND-CHECK fields, then paste into runs.yaml:")
    print("=" * 70)
    stanza = [
        f"  - run_id: {run_id}           # HAND-CHECK: assign campaign ordinal",
        f"    device: {device or 'HAND-CHECK'}",
        f"    rig: {rig or 'HAND-CHECK'}",
        f"    date: {date}",
        f"    mode: {mode or 'HAND-CHECK'}          # HAND-CHECK: confirm from brief",
        f"    archive: {run['archive']}",
        f"    rig_session_dir: HAND-CHECK   # <user>/<session>",
        f"    layout: root",
        f"    transcript: {transcript}",
        f"    variability_set: false        # HAND-CHECK",
        f"    corpus_commit: {cc if cc else 'null'}{cc_note}",
        f"    t_final_decision: {dec_val}   # HAND-CHECK ({dec_src or 'no candidate'})",
        f"    n_interventions: null         # HAND-CHECK: apply §5 counting rule (labels in drafts/messages/{run_id}.csv)",
        f"    caveats: []                   # HAND-CHECK",
    ]
    print("\n".join(stanza))
    print("\nDraft csv row (headline):")
    print(",".join(str(row[k]) if row[k] is not None else "" for k in row))
    print(f"\nDraft outputs under {os.path.join(paper_root, 'analysis', 'drafts')}/")
    if prov["corpus_dirty"]:
        print("  ! corpus was DIRTY at deploy — corpus_commit join is approximate.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("run_ids", nargs="*", help="run ids from <paper>/analysis/runs.yaml")
    ap.add_argument("--all", action="store_true", help="every non-excluded manifest run")
    ap.add_argument("--archive", metavar="DIR",
                    help="capture-at-close: draft a new run from a fresh archive dir")
    ap.add_argument("--paper-root", default=DEFAULT_PAPER_ROOT,
                    help="hera-paper checkout holding analysis/ (env HERA_PAPER)")
    ap.add_argument("--rig", help="[--archive] override rig (else detect from rig_card)")
    ap.add_argument("--device", help="[--archive] override device (else from archive name)")
    ap.add_argument("--mode", help="[--archive] override E0/E1 (else from brief)")
    args = ap.parse_args()

    paper_root = os.path.abspath(os.path.expanduser(args.paper_root))

    if args.archive:
        return draft_from_archive(
            os.path.abspath(os.path.expanduser(args.archive)),
            paper_root, args.rig, args.device, args.mode,
        )

    manifest = yaml.safe_load(open(os.path.join(paper_root, "analysis", "runs.yaml")))
    runs = manifest["runs"]
    if args.all:
        runs = [r for r in runs if not r.get("exclude")]
    else:
        wanted = set(args.run_ids)
        runs = [r for r in runs if r["run_id"] in wanted]
        missing = wanted - {r["run_id"] for r in runs}
        if missing:
            raise SystemExit(f"unknown run ids: {sorted(missing)}")
    if not runs:
        raise SystemExit("nothing to do — pass run ids, --all, or --archive")

    out_dirs = {
        name: os.path.join(paper_root, "analysis", name)
        for name in ("metrics", "messages", "reports")
    }
    for d in out_dirs.values():
        os.makedirs(d, exist_ok=True)

    for run in runs:
        extract_run(run, out_dirs)

    rebuild_runs_csv(out_dirs["metrics"], os.path.join(paper_root, "analysis", "runs.csv"))
    print("runs.csv rebuilt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
