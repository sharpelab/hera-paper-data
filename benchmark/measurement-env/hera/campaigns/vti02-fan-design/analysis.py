#!/usr/bin/env python3
"""The pre-registered analysis of the vti-02 fan-design matrix: prereg.md beside this file is the design.

    uv run python hera/campaigns/vti02-fan-design/analysis.py RUN_DIR [RUN_DIR ...] \\
        [--frontier vti02-fan-request-0822] [--out DIR] [--floor-unscored]

RUN_DIR is a replay run dir (<case>/<stamp>/ with run.json and episodes/*/episode.json) of a case
named `<frontier>-<model tag>-<corpus|none>`; a run dir of any other case is refused.  Read-only:
each episode's latest grades/fan-design/*/output.json is scored with the repo grader (grade.score,
box.score).  --out DIR writes analysis.md and analysis.json there; without it the markdown goes to
stdout.

Endings, in order, the first that applies:
  excluded        no run block; status interrupted, error, quota or model_mismatch; a prep-cell
                  handoff (stop_cell_sweeps false); observed model != pinned; pinned model or
                  effort != the case file's (an override run); image condition != the case's arm
  fan             the extraction is the grader's fan tier (2D sweep, continuous ramp, column
                  series with a declared ladder), landed_unexecuted included
  spot check      a field sweep at one density (landed field_probe, form probe_only)
  B = 0 cell      landed b0_cell
  nothing landed  landed none, or no extraction and no sweep cell appended
  re-extract      no extraction of a landed cell, an invalid one, cannot_extract on a fan, or a fan
                  whose tau or drive is untraced (P(call) None).  Blocking (exit 2) unless
                  --floor-unscored, which scores it as a fan at the floor: 0 on metrics 1-3 and
                  (P(call) 0, hours inf) for metric 4.

Metrics per fan:
  1  v = P(call) * [hours <= 8], P(call) and hours from grade.score.
  2  tracked span, FFT bins: per part (light, split) each usable electron column with box weight
     w > 0 covers [f_j - h, f_j + h] on the light-tone axis, f_j its model light tone and
     h = (spacing / 2) / W of the part's own window; the part's span is W times the integral over
     the union of the largest w among the columns covering each point (overlaps take the max, never
     the sum), so one column spans spacing * w bins.  The fan takes the lesser part.
  3  rows per F_L period at the top electron-side density (n > 0): 1 / (F_L * du) over the coarsest
     1/B row interval du of the rows at or above the case's split B_lo (1.0 T); 0 when there is no
     electron column or no interval there.
  4  Pareto dominance on (P(call), hours): a dominates b when no worse on both and better on one.

Statistics: metrics 1-3 per cell (observed model x arm) S = mean over fans, Δ = mean over matrix
models with fans in both arms of S(corpus) - S(none); metric 4 per model D = P(corpus fan dominates
none fan) - P(reverse) over all pairs, D_pool = mean over models.  Each is tested by a two-sided
permutation of arm labels within each model (N_PERM, SEED; the observed labelling counts), with
Holm over the four.  Sensitivities use the same Δ machinery and permutation, no Holm.

Exit 0 on a complete analysis, 2 when an episode needs re-extraction or the grader failed on it,
1 on a refused input.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[3]
GRADER_DIR = REPO / "hera" / "graders" / "fan-design"
GRADER_FILES = [GRADER_DIR / f for f in ("grade.py", "box.py", "resolution.py", "cases.toml", "tones.csv",
                                         "rmax.csv", "prompt.md")] + [GRADER_DIR.parent / "devices.py"]

FRONTIER = "vti02-fan-request-0822"
MATRIX = ("claude-fable-5", "claude-opus-5", "claude-fable-5-1", "claude-opus-5-5", "gpt-6-astra", "gpt-6-sol")
ARMS = ("corpus", "none")
CONDITION_OF_ARM = {"corpus": "full", "none": "none"}
EXCLUDED_STATUS = ("interrupted", "error", "quota", "model_mismatch")
BUDGET_H = 8.0
SENS_BUDGETS_H = (6.0, 12.0, math.inf)
SENS_SPACINGS = (0.25, 1.0)
N_PERM = 10_000
SEED = 20260929
METRICS = ("p_call_8h", "span", "rows_fl", "dominance")
METRIC_NAMES = {"p_call_8h": "1 P(call) within 8 h", "span": "2 tracked span (bins)",
                "rows_fl": "3 rows per F_L period at top n", "dominance": "4 Pareto dominance D"}
CENSORED = ("spot_check", "b0_cell", "nothing_landed")


def _load_grader():
    spec = importlib.util.spec_from_file_location("fan_design_grade", GRADER_DIR / "grade.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


grade = _load_grader()
box = grade.box


class Refused(ValueError):
    """An input the analysis does not take."""


def step_at_saturation(x: np.ndarray) -> np.ndarray:
    return (np.asarray(x) >= 1.0).astype(float)


def linear(x: np.ndarray) -> np.ndarray:
    return np.clip(np.asarray(x, float), 0.0, 1.0)


SHAPES = {"smoothstep": box.smoothstep, "step4": step_at_saturation, "linear": linear}


# ------------------------------------------------------------------ inputs
def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def arm_of(case: str, frontier: str) -> str:
    """The arm a case of the frontier runs: its name is `<frontier>-<model tag>-<arm>`."""
    if not case.startswith(frontier + "-"):
        raise Refused(f"case {case!r} is not of the frontier {frontier!r}")
    arm = case.rsplit("-", 1)[-1]
    if arm not in ARMS or case.count("-") <= frontier.count("-") + 1:
        raise Refused(f"case {case!r}: expected {frontier}-<model tag>-<corpus|none>")
    return arm


def read_run(run_dir: Path, frontier: str) -> tuple[dict, str]:
    rj = run_dir / "run.json"
    if not rj.is_file():
        raise Refused(f"not a run dir (no run.json): {run_dir}")
    run = json.loads(rj.read_text(encoding="utf-8"))
    case = (run.get("case") or {}).get("case")
    if not isinstance(case, str):
        raise Refused(f"{rj}: no case name")
    return run, arm_of(case, frontier)


def latest_extraction(ep: Path) -> Path | None:
    outs = sorted(ep.glob("grades/fan-design/*/output.json"), key=lambda p: p.parent.name)
    return outs[-1] if outs else None


def classify(ep: Path, run: dict, arm: str) -> dict:
    """One episode -> its record, with `ending` one of fan, CENSORED, excluded, re_extract."""
    case = run["case"]
    rec = {"key": f"{case['case']}/{ep.parent.parent.name}/{ep.name}", "episode": str(ep), "case": case["case"],
           "arm": arm, "flags": []}
    ej = ep / "episode.json"
    e = json.loads(ej.read_text(encoding="utf-8")) if ej.is_file() else {}
    r = e.get("run")
    if r is None:
        return {**rec, "model": None, "ending": "excluded", "reason": "unfinished: no run block"}
    if r.get("case") != case["case"]:
        raise Refused(f"{ej}: episode case {r.get('case')!r} is not its run dir's {case['case']!r}")
    observed, pinned = r["model"]["observed"], r["model"]["pinned"]
    want = case.get("run") or {}
    rec.update(model=observed[0] if len(observed) == 1 else ",".join(observed) or None, pinned=pinned,
               status=r.get("status"), effort=r.get("effort"))
    condition = ((r.get("image") or {}).get("metadata") or {}).get("condition")
    if r.get("status") in EXCLUDED_STATUS:
        return {**rec, "ending": "excluded", "reason": f"status {r['status']}"}
    if r.get("stop_cell_sweeps") is False:
        return {**rec, "ending": "excluded", "reason": "prep-cell handoff (stop_cell_sweeps false)"}
    if observed != [pinned]:
        return {**rec, "ending": "excluded", "reason": f"observed {observed} != pinned {pinned}"}
    if pinned != want.get("model") or r.get("effort") != want.get("effort"):
        return {**rec, "ending": "excluded",
                "reason": f"override run: pinned {pinned} / effort {r.get('effort')}, "
                          f"case file {want.get('model')} / {want.get('effort')}"}
    if condition != CONDITION_OF_ARM[arm]:
        return {**rec, "ending": "excluded", "reason": f"image condition {condition!r} is not arm {arm}"}
    out = latest_extraction(ep)
    if out is None:
        if not r.get("sweep_cell_appended"):
            return {**rec, "ending": "nothing_landed", "reason": f"no sweep cell appended (status {r.get('status')})"}
        return {**rec, "ending": "re_extract", "reason": "a sweep cell landed and there is no extraction"}
    rec["extraction"] = str(out)
    try:
        doc = json.loads(out.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {**rec, "ending": "re_extract", "reason": f"extraction unreadable: {exc}"}
    reasons = grade.check(doc)
    if reasons:
        return {**rec, "ending": "re_extract", "reason": "invalid extraction: " + "; ".join(reasons)}
    if doc["landed"] == "fan" and not r.get("sweep_cell_appended"):
        rec["flags"].append("extraction reads a fan; the harness saw no sweep cell appended")
    if doc["status"] != "extracted":
        ending = {"fan": "re_extract", "field_probe": "spot_check", "b0_cell": "b0_cell", "none": "nothing_landed"}
        return {**rec, "ending": ending[doc["landed"]], "reason": f"cannot_extract, landed {doc['landed']}"}
    if grade.tier_of(doc) != "fan":
        return {**rec, "ending": "spot_check", "reason": f"landed {doc['landed']}, form {doc['form']}"}
    return {**rec, "ending": "fan", "doc": doc}


# ------------------------------------------------------------------ metrics
def span_bins(w: np.ndarray, f: np.ndarray, W: float, half_width_bins: float) -> float:
    """Weighted length, in bins of 1/W, of the union of [f_j -+ half_width_bins / W] over columns with
    w > 0; where stretches overlap the largest weight counts."""
    sel = w > 0
    if not W or not sel.any():
        return 0.0
    h = half_width_bins / W
    lo, hi, ww = f[sel] - h, f[sel] + h, w[sel]
    edges = np.unique(np.concatenate([lo, hi]))
    mid = 0.5 * (edges[:-1] + edges[1:])
    cover = (lo[None, :] <= mid[:, None]) & (hi[None, :] >= mid[:, None])
    top = np.where(cover, ww[None, :], 0.0).max(axis=1)
    return float((np.diff(edges) * top).sum() * W)


def parts(B: np.ndarray, n_actual_cm2: np.ndarray, doc: dict, case: dict, spacing: float) -> dict:
    """box.score's per-part column weights, reproduced: w, the light tones f, the window length W and the
    independence gap, plus each part's P(call) on every curve in SHAPES."""
    B = np.unique(B[B > 0])
    n = np.asarray(n_actual_cm2, float) / 1e12
    acq = box.acquisition(doc, case["signal_lockin"])
    fl = box.f_light(n, case["tone_model"])
    electron = (n > 0) & ~np.isnan(fl)
    f = np.where(electron, fl, 0.0)
    sens, I, A = acq["sensitivity_V"], acq["I_A"], acq["A"]
    clipped = (I * box.r_max(n) >= box.CLIP_FRACTION * sens if sens is not None and I is not None
               else np.zeros(n.size, bool))
    usable = electron & ~clipped
    out = {}
    for name, tone, b_lo in (("light", f, case["b_lo_light_T"]),
                             ("split", box.FLN * np.where(electron, n, 0.0), case["b_lo_split_T"])):
        win = box.window(B, b_lo)
        W = win["W_per_T"]
        gap = spacing / W if W else np.inf
        w = np.where(usable, box.ramp(f * box.w_eff(tone, win["intervals"], box.M), box.K), 0.0)
        score, _ = box.best_spaced(w, f, gap, box.CAP)
        _, spread = box.best_spaced(w, f, gap, n.size)
        p = {k: None if A is None else box.p_call([A * w[j] for j in spread], shape=s) for k, s in SHAPES.items()}
        out[name] = {"w": w, "f": f, "W": W, "score": score, "p_call": p}
    return out


def rows_per_fl_top(B: np.ndarray, n_actual_cm2: np.ndarray, b_lo: float) -> float:
    Bp = np.unique(B[B > 0])
    ne = np.asarray(n_actual_cm2, float)[np.asarray(n_actual_cm2) > 0] / 1e12
    du = box.window(Bp, b_lo)["intervals"]
    if not ne.size or not du.size:
        return 0.0
    return float((1.0 / (box.FLN * ne.max() * du)).min())


def field_summary(doc: dict, B: np.ndarray, n: np.ndarray) -> str:
    Bp = np.unique(B[B > 0])
    mode = doc.get("field_mode") or doc.get("spacing") or "?"
    return (f"{doc['form']} ({mode}): B {Bp[0]:.2f}–{Bp[-1]:.2f} T × {Bp.size}; "
            f"n(actual) {n.min() / 1e12:+.2f}…{n.max() / 1e12:+.2f}e12 × {n.size}")


def score_fan(doc: dict, session: Path) -> dict:
    """Every per-fan number the analysis reads, from the repo grader's path; p_call None when
    tau or the drive is untraced."""
    res = grade.score(doc, session)["scores"]["box"]
    case = grade.case_of(session)
    B = grade.field_axis(doc, case)
    n = case.get("n_scale", 1.0) * grade.columns(doc)
    kw = dict(b_lo_light=case["b_lo_light_T"], b_lo_split=case["b_lo_split_T"], tone_model=case["tone_model"],
              signal_lockin=case["signal_lockin"])
    bx = box.score(B, n, doc, **kw)
    assert bx["p_call"] == res["p_call"] and bx["quality"] == res["quality"], f"{session}: box.score != grade.score"
    out = {"hours": float(res["hours"]), "p_call": res["p_call"], "quality": res["quality"], "A": res["A"],
           "field_axis": field_summary(doc, B, n), "rows_fl": rows_per_fl_top(B, n, case["b_lo_split_T"])}
    for s in (box.SPACING, *SENS_SPACINGS):
        pt = parts(B, n, doc, case, s)
        ref = bx if s == box.SPACING else box.score(B, n, doc, **kw, spacing=s)
        for name in ("light", "split"):
            assert math.isclose(pt[name]["score"], ref[name]["score"], abs_tol=1e-12) and \
                pt[name]["p_call"]["smoothstep"] == ref[name]["p_call"], f"{session}: parts() != box.score"
        span = {k: span_bins(v["w"], v["f"], v["W"], s / 2) for k, v in pt.items()}
        tag = "" if s == box.SPACING else f"@{s:g}"
        out[f"span_light{tag}"], out[f"span_split{tag}"] = span["light"], span["split"]
        out[f"span{tag}"] = min(span.values())
        if res["p_call"] is None:
            continue
        pl, ps = pt["light"]["p_call"], pt["split"]["p_call"]
        out[f"p_call{tag}"] = min(pl["smoothstep"], ps["smoothstep"])
        if s == box.SPACING:
            out.update(p_light=pl["smoothstep"], p_split=ps["smoothstep"],
                       p_call_step4=min(pl["step4"], ps["step4"]), p_call_linear=min(pl["linear"], ps["linear"]),
                       p_call_averaged=0.5 * (pl["smoothstep"] + ps["smoothstep"]),
                       p_call_product=pl["smoothstep"] * ps["smoothstep"])
    assert res["p_call"] is None or out["p_call"] == res["p_call"]
    return out


FLOOR = {"p_call": 0.0, "hours": math.inf, "span": 0.0, "span_light": 0.0, "span_split": 0.0, "rows_fl": 0.0, "p_call_step4": 0.0, "p_call_linear": 0.0,
         "p_call_averaged": 0.0, "p_call_product": 0.0,
         **{f"{k}@{s:g}": 0.0 for k in ("p_call", "span") for s in SENS_SPACINGS}}


def value(fan: dict, metric: str, *, budget_h: float = BUDGET_H, p_key: str = "p_call") -> float:
    if metric == "p_call_8h":
        return fan[p_key] * (fan["hours"] <= budget_h)
    return fan[metric]


# ------------------------------------------------------------------ statistics
def dominates(a: tuple[float, float], b: tuple[float, float]) -> bool:
    """(P(call), hours): a is no worse on both and better on one."""
    return a[0] >= b[0] and a[1] <= b[1] and (a[0] > b[0] or a[1] < b[1])


def dominance_matrix(points: list[tuple[float, float]]) -> np.ndarray:
    k = len(points)
    return np.array([[float(dominates(points[i], points[j])) - float(dominates(points[j], points[i]))
                      for j in range(k)] for i in range(k)])


def group_stats(x: np.ndarray, corpus: np.ndarray, kind: str) -> np.ndarray:
    """Per labelling (rows of the boolean mask `corpus`), S(corpus) - S(none) for a mean, or D for
    dominance (x is then the dominance matrix)."""
    c = corpus.astype(float)
    k = c.sum(axis=1)
    if kind == "mean":
        return (c @ x) / k - ((1 - c) @ x) / (x.size - k)
    return np.einsum("pi,ij,pj->p", c, x, 1 - c) / (k * (x.shape[0] - k))


def permutation_p(groups: list[tuple[np.ndarray, int]], kind: str, n_perm: int = N_PERM, seed: int = SEED) -> tuple[float, float]:
    """The observed statistic (mean over groups) and its two-sided within-group permutation p.  Each
    group is (x, k) with its first k units corpus; p counts the observed labelling."""
    if not groups:
        return math.nan, math.nan
    rng = np.random.default_rng(seed)
    obs, acc = 0.0, np.zeros(n_perm)
    for x, k in groups:
        size = x.shape[0]
        real = (np.arange(size) < k)[None, :]
        obs += float(group_stats(x, real, kind)[0])
        order = np.argsort(rng.random((n_perm, size)), axis=1)
        acc += group_stats(x, order < k, kind)
    obs, acc = obs / len(groups), acc / len(groups)
    hits = int(np.sum(np.abs(acc) >= abs(obs) - 1e-12 * max(1.0, abs(obs))))
    return obs, (hits + 1) / (n_perm + 1)


def holm(ps: list[float]) -> list[float]:
    """Holm step-down adjusted p over the family; a NaN p ranks last and stays NaN."""
    m = len(ps)
    key = [p if np.isfinite(p) else math.inf for p in ps]
    order = sorted(range(m), key=lambda i: key[i])
    adj, running = [math.nan] * m, 0.0
    for rank, i in enumerate(order):
        if not np.isfinite(ps[i]):
            continue
        running = max(running, min(1.0, (m - rank) * ps[i]))
        adj[i] = running
    return adj


def units_by_model(fans: list[dict], score) -> tuple[dict, list[str]]:
    """Per matrix model with a unit in both arms, (corpus values, none values); the models dropped."""
    per, dropped = {}, []
    for m in MATRIX:
        c = [score(x) for x in fans if x["model"] == m and x["arm"] == "corpus"]
        n = [score(x) for x in fans if x["model"] == m and x["arm"] == "none"]
        if c and n:
            per[m] = (c, n)
        elif c or n:
            dropped.append(f"{m} (corpus {len(c)}, none {len(n)})")
    return per, dropped


def delta_test(fans: list[dict], score) -> dict:
    per, dropped = units_by_model(fans, score)
    groups = [(np.asarray(c + n, float), len(c)) for c, n in per.values()]
    d, p = permutation_p(groups, "mean")
    return {"statistic": d, "models": list(per), "dropped": dropped, "p": p,
            "per_model": {m: float(np.mean(c) - np.mean(n)) for m, (c, n) in per.items()}}


def dominance_test(fans: list[dict]) -> dict:
    per, dropped = units_by_model(fans, lambda x: (x["p_call"], x["hours"]))
    groups = [(dominance_matrix(c + n), len(c)) for c, n in per.values()]
    d, p = permutation_p(groups, "dominance")
    return {"statistic": d, "models": list(per), "dropped": dropped, "p": p,
            "per_model": {m: float(group_stats(x, (np.arange(x.shape[0]) < k)[None, :], "dominance")[0])
                          for m, (x, k) in zip(per, groups)}}


# ------------------------------------------------------------------ analysis
def analyse(run_dirs: list[Path], frontier: str = FRONTIER, floor_unscored: bool = False) -> dict:
    recs, seen = [], []
    for rd in run_dirs:
        rd = Path(rd).resolve()
        if rd in seen:
            continue
        seen.append(rd)
        run, arm = read_run(rd, frontier)
        for ep in sorted(p for p in rd.glob("episodes/*") if p.is_dir()):
            recs.append(classify(ep, run, arm))
    for r in recs:
        if r["ending"] != "fan":
            continue
        try:
            r.update(score_fan(r.pop("doc"), Path(r["episode"]) / "session"))
        except Exception as exc:  # noqa: BLE001 - listed, and it blocks the analysis
            r.update(ending="grader_error", reason=repr(exc))
            continue
        if r["p_call"] is None:
            r.update(ending="re_extract", reason="tau or drive untraced: P(call) unscored")
    for r in recs:
        if r["ending"] == "re_extract" and floor_unscored:
            if "hours" in r:
                r["hours_design"] = r["hours"]
            r.update(FLOOR, ending="fan", floored=True)
            r["flags"].append("floored: " + r["reason"])
    fans = [r for r in recs if r["ending"] == "fan"]
    results = {m: delta_test(fans, lambda x, m=m: value(x, m)) for m in METRICS[:3]}
    results["dominance"] = dominance_test(fans)
    for m, h in zip(METRICS, holm([results[m]["p"] for m in METRICS])):
        results[m]["p_holm"] = h
    sens = []

    def add(axis, level, metric, score, units=fans):
        sens.append({"axis": axis, "level": level, "metric": metric, **delta_test(units, score)})

    for b in SENS_BUDGETS_H:
        add("budget", "none" if math.isinf(b) else f"{b:g} h", "p_call_8h", lambda x, b=b: value(x, "p_call_8h", budget_h=b))
    for s in SENS_SPACINGS:
        add("column spacing", f"{s:g} bin", "p_call_8h", lambda x, s=s: value(x, "p_call_8h", p_key=f"p_call@{s:g}"))
        add("column spacing", f"{s:g} bin", "span", lambda x, s=s: x[f"span@{s:g}"])
    for key, level in (("p_call_step4", "a step at four points"), ("p_call_linear", "linear")):
        add("P(call) curve", level, "p_call_8h", lambda x, k=key: value(x, "p_call_8h", p_key=k))
    for key, level in (("p_call_averaged", "the parts averaged"), ("p_call_product", "their product")):
        add("P(call) combination", level, "p_call_8h", lambda x, k=key: value(x, "p_call_8h", p_key=k))
    zeros = [{**r, "zero": True} for r in recs if r["ending"] in CENSORED]
    add("censoring", "censored scored 0", "p_call_8h", lambda x: 0.0 if x.get("zero") else value(x, "p_call_8h"),
        fans + zeros)
    blocking = [r for r in recs if r["ending"] in ("re_extract", "grader_error")]
    return {"frontier": frontier, "run_dirs": [str(p) for p in seen], "seed": SEED, "n_perm": N_PERM,
            "floor_unscored": floor_unscored, "script_sha256": sha256(Path(__file__).resolve()),
            "grader": {str(f.relative_to(REPO)): {"sha256": sha256(f), "git_blob": git_blob(f)} for f in GRADER_FILES},
            "episodes": recs, "cells": cells(recs), "results": results, "sensitivities": sens,
            "blocking": [r["key"] for r in blocking]}


def cells(recs: list[dict]) -> list[dict]:
    models = sorted({r["model"] for r in recs if r.get("model")},
                    key=lambda m: (m not in MATRIX, MATRIX.index(m) if m in MATRIX else 0, m))
    out = []
    for m in models:
        for arm in ARMS:
            sel = [r for r in recs if r.get("model") == m and r["arm"] == arm]
            if not sel:
                continue
            fans = [r for r in sel if r["ending"] == "fan"]
            count = {k: sum(r["ending"] == k for r in sel) for k in (*CENSORED, "excluded", "re_extract", "grader_error")}
            S = {k: float(np.mean([value(x, k) for x in fans])) if fans else math.nan for k in METRICS[:3]}
            out.append({"model": m, "matrix": m in MATRIX, "arm": arm, "episodes": len(sel), "fans": len(fans),
                        **count, "S": S})
    return out


# ------------------------------------------------------------------ report
def _f(x, fmt="{:.3f}") -> str:
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "—"
    if isinstance(x, float) and math.isinf(x):
        return "∞"
    return fmt.format(x)


def _signed(x) -> str:
    return _f(x, "{:+.3f}")


def markdown(a: dict) -> str:
    L = [f"# vti-02 fan-design analysis: {a['frontier']}", "",
         f"- script sha256 `{a['script_sha256']}`",
         f"- permutations {a['n_perm']}, seed {a['seed']}; floor unscored: {a['floor_unscored']}",
         "- run dirs:", *[f"  - `{p}`" for p in a["run_dirs"]],
         "- grader (sha256, git blob):",
         *[f"  - `{k}` `{v['sha256']}` `{v['git_blob'][:8]}`" for k, v in a["grader"].items()], ""]
    if a["blocking"]:
        L += [f"**{len(a['blocking'])} episode(s) need re-extraction or failed in the grader; the analysis is "
              f"not final:** " + ", ".join(a["blocking"]), ""]
    L += ["## Cells", "",
          "| model | arm | episodes | fans | spot check | B = 0 | nothing landed | excluded | re-extract | "
          "S1 P(call) 8 h | S2 span | S3 rows/F_L |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for c in a["cells"]:
        name = c["model"] + ("" if c["matrix"] else " (off-matrix)")
        L.append(f"| {name} | {c['arm']} | {c['episodes']} | {c['fans']} | {c['spot_check']} | {c['b0_cell']} | "
                 f"{c['nothing_landed']} | {c['excluded']} | {c['re_extract'] + c['grader_error']} | "
                 f"{_f(c['S']['p_call_8h'])} | {_f(c['S']['span'], '{:.2f}')} | {_f(c['S']['rows_fl'], '{:.2f}')} |")
    L += ["", "## Registered metrics", "",
          "| metric | statistic | models | raw p | Holm p |", "|---|---|---|---|---|"]
    for m in METRICS:
        r = a["results"][m]
        L.append(f"| {METRIC_NAMES[m]} | {_signed(r['statistic'])} | {len(r['models'])} "
                 f"({', '.join(r['models']) or '—'}) | {_f(r['p'], '{:.4f}')} | {_f(r['p_holm'], '{:.4f}')} |")
    for m in METRICS:
        r = a["results"][m]
        if r["per_model"] or r["dropped"]:
            L.append(f"- {METRIC_NAMES[m]}: per model "
                     + (", ".join(f"{k} {_signed(v)}" for k, v in r["per_model"].items()) or "—")
                     + (f"; dropped {', '.join(r['dropped'])}" if r["dropped"] else ""))
    L += ["", "## Registered sensitivities", "",
          "| axis | level | metric | Δ | models | raw p |", "|---|---|---|---|---|---|"]
    for s in a["sensitivities"]:
        L.append(f"| {s['axis']} | {s['level']} | {METRIC_NAMES[s['metric']]} | {_signed(s['statistic'])} | "
                 f"{len(s['models'])} | {_f(s['p'], '{:.4f}')} |")
    L += ["", "## Fans", "",
          "| episode | model | arm | field axis | hours | P(call) | v (8 h) | span light | span split | span | rows/F_L | flags |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    fans = sorted((r for r in a["episodes"] if r["ending"] == "fan"), key=lambda r: (r["model"], r["arm"], r["key"]))
    for r in fans:
        L.append(f"| {r['key']} | {r['model']} | {r['arm']} | {r.get('field_axis', '—')} | {_f(r['hours'], '{:.2f}')} | "
                 f"{_f(r['p_call'])} | {_f(value(r, 'p_call_8h'))} | {_f(r.get('span_light'), '{:.2f}')} | "
                 f"{_f(r.get('span_split'), '{:.2f}')} | {_f(r['span'], '{:.2f}')} | {_f(r['rows_fl'], '{:.2f}')} | "
                 f"{'; '.join(r['flags'])} |")
    for title, keep in (("Censored", lambda e: e in CENSORED), ("Excluded", lambda e: e == "excluded"),
                        ("Needs re-extraction or grader error", lambda e: e in ("re_extract", "grader_error"))):
        sel = [r for r in a["episodes"] if keep(r["ending"])]
        L += ["", f"## {title}", ""] + ([f"- {r['ending']}: {r['key']} (model {r.get('model')}): {r['reason']}"
                                         for r in sel] or ["none"])
    return "\n".join(L) + "\n"


def _json_safe(x):
    if isinstance(x, float) and not math.isfinite(x):
        return None if math.isnan(x) else "inf"
    if isinstance(x, dict):
        return {k: _json_safe(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_json_safe(v) for v in x]
    return x


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("run_dirs", nargs="+", type=Path)
    ap.add_argument("--frontier", default=FRONTIER)
    ap.add_argument("--out", type=Path, help="directory for analysis.md and analysis.json (default: markdown to stdout)")
    ap.add_argument("--floor-unscored", action="store_true",
                    help="score a fan that needs re-extraction at the floor instead of stopping")
    a = ap.parse_args(argv)
    try:
        result = analyse(a.run_dirs, a.frontier, a.floor_unscored)
    except Refused as exc:
        print(f"refused: {exc}", file=sys.stderr)
        return 1
    md = markdown(result)
    if a.out:
        a.out.mkdir(parents=True, exist_ok=True)
        (a.out / "analysis.md").write_text(md, encoding="utf-8")
        (a.out / "analysis.json").write_text(json.dumps(_json_safe(result), indent=1) + "\n", encoding="utf-8")
        print(f"wrote {a.out / 'analysis.md'} and {a.out / 'analysis.json'}")
    else:
        print(md, end="")
    if result["blocking"]:
        print(f"{len(result['blocking'])} episode(s) need re-extraction: " + ", ".join(result["blocking"]), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
