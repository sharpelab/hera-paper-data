#!/usr/bin/env python3
"""fan-design: how good is the Landau fan the agent designed?

    grade.py check <output.json>                         # shape + sanity; exit 1 with reasons; no score
    grade.py score <output.json> --archive <dir> -o scores.json

Two tiers.  `landed` (on every output file) says what the agent's trailing cells do: a
fan, a field probe (a spot check or onset sweep), a B = 0 cell, or nothing gradeable; `form`
says how the field axis is acquired (2D megasweep, continuous ramp, column series, probe
only).  The fan tier -- a 2D megasweep, a continuous ramp, or a 1D column with a declared
ladder -- gets four scores, one per design decision, none with a pass threshold (`ok` is null):

  side_choice       the share of the fan's density range on the carrier side the case's spot
                    checks favour (cases.toml).
  field_resolution  Aaron's ruling (resolution.py, next to this file): the fraction of the
                    fan's own (n, 1/B) area, above the case's low-field cutoff (cases.toml),
                    sampled at M rows per Luttinger period.
  density_range     the fan's top density over the top of the case's density window
                    (cases.toml), how much of the window its columns span, and how much of
                    the fan lies outside it.  A fan wholly on the other side is mirrored
                    first: the side is already scored.
  field_reach       the fan's top field over the field the case's claim needs (cases.toml).

Forms.  A **column series** is a 1D field sweep whose cell, markdown or plan names further
densities of the same sweep: the density axis is the landed column plus the declared ones
(`declared_not_landed` marks the score), every column on the landed field grid.  A
**continuous ramp** has no setpoint vector; its effective rows are uniform in field,
one per gate row: dB_row = rate * t_row with t_row from the cost model below, from the ramp's
start to its target, truncated to the rows the cell declares.  A **probe only** landing gets
`sampling` per column and `field_reach`; the density axes are unscored, with the reason.

field_resolution rises when the fan's density range or top field is drawn in; density_range
and field_reach are where that shows.  `sampling` reads one column at a time -- rows per
period at the thinnest interval above the cutoff, and the periods the record holds there --
at the top of the case's window (a number the fan's own range cannot improve) and at the
fan's own top density.

Reported next to them: the resolved fraction in B measure and at the recipe's Nyquist floor,
the design's derived quantities (steps, point count, delay over time constant, bias current,
dwell time), and the cost: an estimated wall clock from the rig model in cases.toml -- per
field row, the ramp to it at the magnet's rate plus its settle, then the gate points at their
delay plus a per-point overhead that grows with the gate-current reads' NPLC, plus a flyback --
next to the time the agent stated.  For a
column series the ladder's cost is the per-column estimate times the ladder.  Nothing in the
cost is scored.

Cases with `scheme = "box"` (vti-02) replace the four scores with one, `box` (box.py next to this
file; the scheme is hera/docs/fan-design-grader.md): how well the fan's columns resolve the light
tone and split F_L from the heavy tone in the (n, F) box of the case's tone model, times an
acquisition factor, next to the estimated hours.  The case's side, window, cutoff and reach are not read.

Densities are scored in the frame the tones live in: the extracted (calibration-frame)
values times the case's `n_scale`, where the archive measured one.  The window is stated in
that frame; `derived` reports both.

Not scored: settling, dynamic range, cost floor -- no ruling yet.
"""
from __future__ import annotations

import argparse
import json
import sys
import tomllib
from pathlib import Path

import numpy as np

sys.path[:0] = [str(Path(__file__).resolve().parent), str(Path(__file__).resolve().parents[1])]
import box  # noqa: E402  - sibling module
import resolution  # noqa: E402  - sibling module
from devices import device_of  # noqa: E402  - graders/devices.py

GRADER = "fan-design"
SCORER_VERSION = "field resolution: wiki Fan-design scorer rev 108 (2026-09-19); forms + cost model 2026-09-22; vti-02 box 2026-09-26; NPLC in the cost 2026-09-26"
G = 4                # LL degeneracy: unbroken spin x valley
M = 3.0              # rows per period Aaron requires
M_RECIPE_FLOOR = 2.0  # landau-fan.md's Nyquist floor, reported for comparison
CASES = Path(__file__).resolve().with_name("cases.toml")
LANDED = ("fan", "field_probe", "b0_cell", "none")
FORMS = ("2d_megasweep", "continuous_ramp", "column_series", "probe_only", "b0_cell", "none", "other")
FORMS_OF = {"fan": ("2d_megasweep", "continuous_ramp", "other"), "field_probe": ("column_series", "probe_only"),
            "b0_cell": ("b0_cell",), "none": ("none",)}
FIELD_MODES = ("invB", "B", "stitched", "ramp", "other")
FAN_TIER = ("2d_megasweep", "continuous_ramp", "column_series", "other")
COST_KEYS = ("ramp_T_per_min", "field_settle_s", "point_overhead_s", "gate_read_s_per_plc", "flyback_s")

MAX_B = 200_000
MAX_COLUMNS = 2000
MAX_ROWS = 10_000


def _num(x) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool) and np.isfinite(x)


def _opt_num(x, *, positive=False) -> bool:
    return x is None or (_num(x) and (x > 0 if positive else True))


def _int(x, lo, hi) -> bool:
    return isinstance(x, int) and not isinstance(x, bool) and lo <= x <= hi


def is_ramp(doc: dict) -> bool:
    return doc.get("form") == "continuous_ramp" or doc.get("field_mode") == "ramp"


def check(doc: dict) -> list[str]:
    """Reasons the file is unusable; empty means accepted."""
    r: list[str] = []
    if not isinstance(doc, dict):
        return ["top level must be a JSON object"]
    if doc.get("status") not in ("extracted", "cannot_extract"):
        r.append('status must be "extracted" or "cannot_extract"')
    if not isinstance(doc.get("flags", []), list) or not all(
            isinstance(f, dict) and {"kind", "severity", "note"} <= set(f) for f in doc.get("flags", [])):
        r.append("flags must be a list of {kind, severity, note} objects")
    if not isinstance(doc.get("notes", ""), str):
        r.append("notes must be a string")
    landed, form = doc.get("landed"), doc.get("form")
    if landed not in LANDED:
        r.append(f"landed must be one of {', '.join(LANDED)}")
    if form not in FORMS:
        r.append(f"form must be one of {', '.join(FORMS)}")
    elif landed in FORMS_OF and form not in FORMS_OF[landed]:
        r.append(f'form {form!r} does not go with landed {landed!r} (expected one of {", ".join(FORMS_OF[landed])})')
    if doc.get("status") != "extracted":
        return r
    if landed not in ("fan", "field_probe"):
        r.append('status "extracted" needs landed "fan" or "field_probe"; a B = 0 cell or nothing is cannot_extract')
        return r
    fan = landed == "fan"
    if "field_mode" in doc and doc["field_mode"] not in FIELD_MODES:
        r.append(f"field_mode must be one of {', '.join(FIELD_MODES)}")
    if fan and (form == "continuous_ramp") != (doc.get("field_mode") == "ramp"):
        r.append('a continuous ramp is form "continuous_ramp" with field_mode "ramp", and only then')

    if is_ramp(doc):
        lo, hi = doc.get("B_ramp_start_T"), doc.get("B_ramp_target_T")
        if not (_num(lo) and _num(hi) and lo >= 0 and hi >= 0 and lo != hi):
            r.append("B_ramp_start_T and B_ramp_target_T must be finite nonnegative tesla, start != target")
        if not _opt_num(doc.get("ramp_rate_T_per_min"), positive=True):
            r.append("ramp_rate_T_per_min must be a positive number (T/min) or null")
        if "n_rows_declared" not in doc or not (doc["n_rows_declared"] is None or _int(doc["n_rows_declared"], 1, MAX_ROWS)):
            r.append(f"n_rows_declared must be an integer in 1..{MAX_ROWS} or null")
    elif doc.get("B_values") is not None:
        bv = doc["B_values"]
        if not (isinstance(bv, list) and 2 <= len(bv) <= MAX_B and all(_num(v) and v >= 0 for v in bv)):
            r.append(f"B_values must be a list of 2..{MAX_B} finite nonnegative numbers (tesla)")
    else:
        lo, hi, n, sp = doc.get("B_min_T"), doc.get("B_max_T"), doc.get("n_B"), doc.get("spacing")
        if not (_num(lo) and _num(hi) and 0 <= lo < hi):
            r.append("B_min_T and B_max_T must be finite tesla with 0 <= B_min_T < B_max_T")
        if not _int(n, 2, MAX_B):
            r.append(f"n_B must be an integer in 2..{MAX_B}")
        if sp not in ("B", "invB"):
            r.append('spacing must be "B" or "invB"')
        elif sp == "invB" and _num(lo) and lo <= 0:
            r.append("spacing invB needs B_min_T > 0 (1/B is undefined at zero)")

    forms = []
    min_cols = 2 if fan else 1
    if doc.get("n_cm2") is not None:
        forms.append("n_cm2")
        vals = doc["n_cm2"]
        if not (isinstance(vals, list) and min_cols <= len(vals) <= MAX_COLUMNS and all(_num(v) for v in vals)):
            r.append(f"n_cm2 must be a list of {min_cols}..{MAX_COLUMNS} finite numbers (cm^-2)"
                     + ("; a fan has columns" if fan else ""))
        elif max(abs(v) for v in vals) > 1e14:
            r.append("n_cm2 above 1e14 cm^-2: units look like m^-2 (1 m^-2 = 1e-4 cm^-2)")
    if any(doc.get(k) is not None for k in ("n_min_cm2", "n_max_cm2", "n_columns")):
        forms.append("range")
        lo, hi, k = doc.get("n_min_cm2"), doc.get("n_max_cm2"), doc.get("n_columns")
        if not (_num(lo) and _num(hi) and lo < hi):
            r.append("n_min_cm2 and n_max_cm2 must be finite with n_min_cm2 < n_max_cm2")
        elif max(abs(lo), abs(hi)) > 1e14:
            r.append("density range above 1e14 cm^-2: units look like m^-2")
        if not _int(k, 2, MAX_COLUMNS):
            r.append(f"n_columns must be an integer in 2..{MAX_COLUMNS}")
    if len(forms) != 1:
        r.append("give the density axis as n_min_cm2, n_max_cm2, n_columns or as the n_cm2 list"
                 + (" -- not both" if len(forms) > 1 else ""))

    if not fan:
        dc = doc.get("declared_columns_cm2")
        if not (isinstance(dc, list) and len(dc) <= MAX_COLUMNS and all(_num(v) and abs(v) <= 1e14 for v in dc)):
            r.append("declared_columns_cm2 must be a list (possibly empty) of finite densities in cm^-2")
        elif form == "column_series" and not dc:
            r.append('form "column_series" needs at least one density in declared_columns_cm2; with none it is "probe_only"')
        elif form == "probe_only" and dc:
            r.append('form "probe_only" with declared_columns_cm2 non-empty: a declared ladder is "column_series"')
        if "ladder_stated_h_per_column" in doc and not _opt_num(doc["ladder_stated_h_per_column"], positive=True):
            r.append("ladder_stated_h_per_column must be a positive number of hours or null")
        if form == "probe_only" and not any(k in doc for k in ("slow_axis", "lockins", "fast_delay_s")):
            return r  # the design block is optional for a bare probe

    if "D" not in doc or not _opt_num(doc["D"]):
        r.append("D must be a finite number or null (second gate held fixed)")
    if doc.get("slow_axis") not in ("B", "n"):
        r.append('slow_axis must be "B" or "n"')
    for k in ("slow_delay_s", "fast_delay_s"):
        if not (_num(doc.get(k)) and 0 <= doc[k] <= 3600):
            r.append(f"{k} must be seconds in 0..3600 (the sweep call's value, or its default)")

    li = doc.get("lockins")
    if not (isinstance(li, list) and 1 <= len(li) <= 16 and all(isinstance(x, dict) for x in li)):
        r.append("lockins must be a list of 1..16 objects, one per recorded lock-in")
    else:
        for i, x in enumerate(li):
            if not (isinstance(x.get("name"), str) and x["name"]):
                r.append(f"lockins[{i}].name must be a non-empty string")
            for k, hi in (("sensitivity_V", 10.0), ("time_constant_s", 3e4)):
                if k not in x or not _opt_num(x[k], positive=True) or (x[k] is not None and x[k] > hi):
                    r.append(f"lockins[{i}].{k} must be a positive number <= {hi:g} or null (SI units: V, s)")
                if not isinstance(x.get(f"{k.rsplit('_', 1)[0]}_set_in_answer"), bool):
                    r.append(f"lockins[{i}].{k.rsplit('_', 1)[0]}_set_in_answer must be true or false")

    gc = doc.get("gate_current_reads")
    if not (isinstance(gc, list) and len(gc) <= 16 and all(isinstance(x, dict) for x in gc)):
        r.append("gate_current_reads must be a list (possibly empty) of objects, one per recorded gate current")
    else:
        for i, x in enumerate(gc):
            if not (isinstance(x.get("name"), str) and x["name"]):
                r.append(f"gate_current_reads[{i}].name must be a non-empty string")
            if not (_num(x.get("nplc")) and 0 < x["nplc"] <= 100):
                r.append(f"gate_current_reads[{i}].nplc must be a number in (0, 100]")
            if not isinstance(x.get("nplc_set_in_answer"), bool):
                r.append(f"gate_current_reads[{i}].nplc_set_in_answer must be true or false")

    for k in ("excitation_V", "bias_resistor_ohm", "stated_wall_clock_h"):
        if k not in doc or not _opt_num(doc[k], positive=True):
            r.append(f"{k} must be a positive number or null")
    if not _int(doc.get("n_fans"), 1, 20):
        r.append("n_fans must be an integer >= 1 (distinct fans issued or offered)")
    return r


# ------------------------------------------------------------------ axes
def cost_model(case: dict) -> dict | None:
    """The rig's cost constants, or None when the case states none (the cost is then not reported)."""
    present = [k for k in COST_KEYS if k in case]
    if present and len(present) < len(COST_KEYS):
        raise ValueError(f"case {case['case']!r} states only {', '.join(present)} of the cost model in {CASES}")
    return {k: float(case[k]) for k in COST_KEYS} if present else None


def design_cost(doc: dict, cost: dict) -> dict:
    """The rig model at the design's gate-current NPLC: `point_overhead_s` is the overhead at NPLC 1,
    and each recorded gate-current read adds its integration beyond 1 PLC."""
    extra = sum(r["nplc"] - 1.0 for r in doc["gate_current_reads"])
    return {**cost, "point_overhead_s": cost["point_overhead_s"] + cost["gate_read_s_per_plc"] * extra}


def row_time_s(n_fast: int, fast_delay_s: float, cost: dict) -> float:
    """Gate points of one field row at their delay plus the per-point overhead, plus a flyback
    (none for a single point: a 1D field sweep has no gate row to return along)."""
    return n_fast * (fast_delay_s + cost["point_overhead_s"]) + (cost["flyback_s"] if n_fast > 1 else 0.0)


def ramp_rows(doc: dict, cost: dict, n_fast: int) -> dict:
    """Effective field rows of a continuous ramp: one per gate row, uniform in B at the field the
    magnet advances during a row, from the ramp's start to its target, truncated to the rows the
    cell declares.  Rows the ramp has finished before (the magnet at the target) collapse to one."""
    cost = design_cost(doc, cost)
    rate = doc.get("ramp_rate_T_per_min") or cost["ramp_T_per_min"]
    start, target = float(doc["B_ramp_start_T"]), float(doc["B_ramp_target_T"])
    t_row = row_time_s(n_fast, float(doc["fast_delay_s"]), cost)
    d_row = rate / 60.0 * t_row
    sign = 1.0 if target > start else -1.0
    k = np.arange(0, int(abs(target - start) / d_row) + 1)
    B = start + sign * k * d_row
    if not np.isclose(B[-1], target):
        B = np.append(B, target)
    declared = doc.get("n_rows_declared")
    if declared is not None and declared < B.size:
        B = B[:declared]
    return {"B": B, "rate_T_per_min": rate, "rate_source": "cell" if doc.get("ramp_rate_T_per_min") else "case",
            "row_time_s": t_row, "dB_row_T": d_row, "n_rows_effective": int(B.size), "n_rows_declared": declared,
            "B_range_T": [float(B.min()), float(B.max())]}


def field_axis(doc: dict, case: dict | None = None) -> np.ndarray:
    if is_ramp(doc):
        cost = cost_model(case) if case is not None else None
        if cost is None:
            raise ValueError("a continuous ramp needs the case's cost model for its effective rows")
        return np.sort(ramp_rows(doc, cost, landed_columns(doc).size)["B"])
    if doc.get("B_values") is not None:
        return np.sort(np.asarray(doc["B_values"], float))
    lo, hi, n = float(doc["B_min_T"]), float(doc["B_max_T"]), int(doc["n_B"])
    if doc["spacing"] == "invB":
        return np.sort(1.0 / np.linspace(1.0 / lo, 1.0 / hi, n))
    return np.linspace(lo, hi, n)


def landed_columns(doc: dict) -> np.ndarray:
    if doc.get("n_cm2") is not None:
        return np.sort(np.asarray(doc["n_cm2"], float))
    return np.linspace(float(doc["n_min_cm2"]), float(doc["n_max_cm2"]), int(doc["n_columns"]))


def columns(doc: dict) -> np.ndarray:
    """The density axis the design covers: the landed columns plus, for a column series, the
    declared ones."""
    n = landed_columns(doc)
    if doc["form"] == "column_series":
        n = np.union1d(n, np.asarray(doc["declared_columns_cm2"], float))
    return n


def tier_of(doc: dict) -> str:
    if doc["status"] != "extracted":
        return "none"
    return "fan" if doc["form"] in FAN_TIER else "probe"


# ------------------------------------------------------------------ derived
def has_design(doc: dict) -> bool:
    return all(k in doc for k in ("slow_axis", "slow_delay_s", "fast_delay_s", "lockins"))


def estimated_wall_h(B: np.ndarray, n_fast: int, slow_delay_s: float, fast_delay_s: float, cost: dict,
                     *, ramp: bool = False) -> dict:
    """Wall clock of one sweep from the rig model: each field row is a ramp to it at the magnet's
    rate plus its settle (a continuous ramp has neither: the rows ride the ramp), the sweep's
    slow delay, then its gate points at their delay plus the per-point overhead, plus a flyback."""
    B = np.asarray(B, float)
    span = float(abs(B[-1] - B[0]))
    if ramp:
        traverse_s, settle_s = span / cost["ramp_T_per_min"] * 60.0, 0.0
        rows_s = B.size * (slow_delay_s + row_time_s(n_fast, fast_delay_s, cost))
        total_s = max(traverse_s, rows_s)  # rows ride the ramp; whichever is longer holds the clock
    else:
        traverse_s = span / cost["ramp_T_per_min"] * 60.0
        settle_s = B.size * cost["field_settle_s"]
        rows_s = B.size * (slow_delay_s + row_time_s(n_fast, fast_delay_s, cost))
        total_s = traverse_s + settle_s + rows_s
    return {"traverse_h": traverse_s / 3600.0, "settle_h": settle_s / 3600.0, "rows_h": rows_s / 3600.0,
            "estimated_wall_h": total_s / 3600.0}


def derived(doc: dict, B: np.ndarray, n: np.ndarray, scale: float, cost: dict | None) -> dict:
    """Arithmetic on the extracted design; nothing here is a judgement."""
    n_landed = landed_columns(doc)
    n_act = scale * n
    dB, dn = np.diff(B), np.diff(n)
    ramp = is_ramp(doc)
    if doc["slow_axis"] == "B" or ramp:
        n_fast, n_slow = n_landed.size, B.size
    else:
        n_fast, n_slow = B.size, n_landed.size
    dwell_h = (n_slow * n_fast * doc["fast_delay_s"] + n_slow * doc["slow_delay_s"]) / 3600.0
    exc, rb, stated = doc["excitation_V"], doc["bias_resistor_ohm"], doc["stated_wall_clock_h"]
    out = {
        "n_B": int(B.size), "n_columns": int(n.size), "n_columns_landed": int(n_landed.size),
        "n_points": int(B.size * n_landed.size),
        "B_range_T": [float(B[0]), float(B[-1])], "dB_T": [float(dB.min()), float(dB.max())],
        "n_range_cm2": [float(n[0]), float(n[-1])],
        "dn_cm2": [float(dn.min()), float(dn.max())] if dn.size else None,
        "n_range_actual_cm2": [float(n_act[0]), float(n_act[-1])],
        "fast_delay_over_tau": {x["name"]: (doc["fast_delay_s"] / x["time_constant_s"]
                                            if x["time_constant_s"] else None) for x in doc["lockins"]},
        "I_bias_A": exc / rb if exc and rb else None,
        "dwell_h": dwell_h,  # delays only: no ramp, traverse or per-point overhead
        "stated_over_dwell": stated / dwell_h if stated and dwell_h else None,
    }
    if cost is None:
        return out
    cost = design_cost(doc, cost)
    if doc["slow_axis"] == "B" or ramp:
        est = estimated_wall_h(B, n_fast, doc["slow_delay_s"], doc["fast_delay_s"], cost, ramp=ramp)
    else:  # field is the fast axis: every column is its own field traverse
        one = estimated_wall_h(B, 1, 0.0, doc["fast_delay_s"], cost)
        est = {k: v * n_slow for k, v in one.items()}
        est["settle_h"] += n_slow * doc["slow_delay_s"] / 3600.0
        est["estimated_wall_h"] += n_slow * doc["slow_delay_s"] / 3600.0
    out["cost"] = {**est, "stated_wall_clock_h": stated,
                   "stated_over_estimated": stated / est["estimated_wall_h"] if stated else None,
                   "model": cost}
    if doc["form"] == "column_series":
        k = 1 + len(doc["declared_columns_cm2"])
        per = doc.get("ladder_stated_h_per_column")
        out["cost"]["ladder"] = {"columns": k, "estimated_wall_h": est["estimated_wall_h"] * k,
                                 "stated_h_per_column": per, "stated_wall_h": per * k if per else None}
    return out


# ------------------------------------------------------------------ cases
def case_of(archive: Path) -> dict:
    """The case's table: by the case name in the episode's episode.json (an arm named
    `<case>-<model>-<condition>` matches its case as the longest key prefix), else by archive dir
    name.  A table with `base = "<case>"` takes that case's values under its own."""
    cases = tomllib.loads(CASES.read_text(encoding="utf-8"))
    ej = Path(archive).resolve().parent / "episode.json"
    name = json.loads(ej.read_text(encoding="utf-8")).get("run", {}).get("case") if ej.is_file() else None
    if name is not None and name not in cases:
        name = max((k for k in cases if name == k or name.startswith(k + "-")), key=len, default=name)
    if name is None:
        name = next((k for k, v in cases.items() if v.get("source") == Path(archive).resolve().name), None)
    if name not in cases:
        raise ValueError(f"no claim rectangle for {name or Path(archive).resolve().name!r} in {CASES}")
    table, seen = dict(cases[name]), [name]
    while "base" in table:
        base = table.pop("base")
        if base not in cases or base in seen:
            raise ValueError(f"case {name!r}: base {base!r} is not a case in {CASES}")
        seen.append(base)
        table = {**cases[base], **table}
    return {"case": name, **table}


# ------------------------------------------------------------------ scores
def side_choice(n: np.ndarray, favored: str) -> dict:
    sign = {"electron": 1.0, "hole": -1.0}[favored]
    lo, hi = sorted((sign * n[0], sign * n[-1]))
    return {"favored": favored, "favored_side_share": float((max(hi, 0.0) - max(lo, 0.0)) / (hi - lo))}


def _on_favored_side(n: np.ndarray, favored: str) -> tuple[float, float, bool]:
    """The fan's density range, mirrored when it lies wholly on the other side."""
    mirrored = side_choice(n, favored)["favored_side_share"] == 0.0
    return (-n[-1], -n[0], True) if mirrored else (n[0], n[-1], False)


def density_range(n: np.ndarray, window: tuple[float, float], favored: str) -> dict:
    lo, hi, mirrored = _on_favored_side(n, favored)
    sign = {"electron": 1.0, "hole": -1.0}[favored]
    return {"n_max_ratio": float(max(sign * lo, sign * hi) / max(sign * w for w in window)),
            **resolution.coverage(lo, hi, *window), "mirrored": mirrored}


def field_resolution(B: np.ndarray, n: np.ndarray, b_cut: float) -> dict:
    kw = dict(b_cut=b_cut, g=G)

    def frac(**k) -> float:
        return resolution.resolved_fraction(B, n[0], n[-1], **kw, **k)

    return {"resolved_fraction": frac(m=M),
            "resolved_fraction_B": frac(m=M, measure="B"),
            "resolved_fraction_recipe_floor": frac(m=M_RECIPE_FLOOR),
            "unsampled_below_B_min_T": max(0.0, float(B[0]) - b_cut),
            "worst_column": resolution.worst_column(B, n[0], n[-1], m=M, **kw)}


def column_sampling(B: np.ndarray, n_cm2: float, b_cut: float) -> dict:
    """One density column on this field axis: the thinnest sampling above the cutoff and the
    periods the record holds between the cutoff (or the axis's first row above it) and its top."""
    B = np.unique(B)
    F = float(resolution.luttinger_frequency(abs(n_cm2), G))
    lo = max(b_cut, float(B[0]))
    periods = F * (1.0 / lo - 1.0 / float(B[-1])) if B[-1] > lo and F > 0 else 0.0
    return {"n_cm2": float(n_cm2), **resolution.worst_column(B, n_cm2, n_cm2, b_cut=b_cut, g=G, m=M),
            "periods_in_window": float(periods)}


def score(doc: dict, archive: Path) -> dict:
    out = {"grader": GRADER, "landed": doc["landed"], "form": doc["form"], "tier": tier_of(doc),
           "flags": doc.get("flags", []), "notes": doc.get("notes", ""), "versions": {"scorer": SCORER_VERSION}}
    if doc["status"] == "cannot_extract":
        return {**out, "status": "cannot_extract", "ok": None}
    case = case_of(archive)
    window, b_cut, b_hi = tuple(case["n_window_cm2"]), case["b_cut_T"], case["B_hi_T"]
    scale = case.get("n_scale", 1.0)
    cost = cost_model(case)
    B, n = field_axis(doc, case), scale * columns(doc)
    out.update(status="graded", ok=None, device=device_of(archive), case=case["case"],
               params={"g": G, "m": M, "m_recipe_floor": M_RECIPE_FLOOR, "b_cut_T": b_cut,
                       "b_cut_note": case["b_cut_note"], "n_window_cm2": list(window), "B_hi_T": b_hi,
                       "n_scale": scale, "n_scale_note": case.get("n_scale_note"),
                       "window_note": case["note"], "side_note": case["side_note"], "cost_model": cost})
    design = {k: doc.get(k) for k in (
        "spacing", "field_mode", "D", "slow_axis", "slow_delay_s", "fast_delay_s", "lockins", "gate_current_reads", "excitation_V",
        "bias_resistor_ohm", "n_fans", "stated_wall_clock_h")}
    if is_ramp(doc):
        rr = ramp_rows(doc, cost, landed_columns(doc).size)
        design["ramp"] = {k: v for k, v in rr.items() if k != "B"}
    if doc["form"] == "column_series":
        design["declared_not_landed"] = True
        design["declared_columns_cm2"] = list(doc["declared_columns_cm2"])
        design["declared_columns_actual_cm2"] = [scale * v for v in design["declared_columns_cm2"]]
    scores: dict = {"field_reach": {"B_max_ratio": float(B[-1] / b_hi)}}
    if out["tier"] == "probe":
        scores["sampling"] = {"columns": [column_sampling(B, x, b_cut) for x in n]}
        scores["unscored"] = {k: "probe only: no ladder declared, so the design has no density range"
                              for k in ("side_choice", "field_resolution", "density_range")}
        if has_design(doc):
            scores["derived"] = derived(doc, B, columns(doc), scale, cost)
        return {**out, "design": design, "scores": scores}
    if case.get("scheme") == "box":
        out["params"].update(scheme="box", tone_model=case["tone_model"], signal_lockin=case["signal_lockin"],
                             b_lo_light_T=case["b_lo_light_T"], b_lo_split_T=case["b_lo_split_T"])
        d = derived(doc, B, columns(doc), scale, cost)
        hours = d["cost"].get("ladder", d["cost"])["estimated_wall_h"]
        bx = box.score(B, n, doc, b_lo_light=case["b_lo_light_T"], b_lo_split=case["b_lo_split_T"],
                       tone_model=case["tone_model"], signal_lockin=case["signal_lockin"])
        return {**out, "design": design, "scores": {"box": {**bx, "hours": hours}, "derived": d}}
    scores.update({"side_choice": side_choice(n, case["side"]),
                   "field_resolution": field_resolution(B, n, b_cut),
                   "sampling": {"at_window_top": column_sampling(B, max(abs(w) for w in window), b_cut),
                                "at_fan_n_max": column_sampling(B, max(abs(n[0]), abs(n[-1])), b_cut)},
                   "density_range": density_range(n, window, case["side"]),
                   "derived": derived(doc, B, columns(doc), scale, cost)})
    return {**out, "design": design, "scores": scores}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check"); c.add_argument("output", type=Path)
    s = sub.add_parser("score"); s.add_argument("output", type=Path)
    s.add_argument("--archive", type=Path, required=True); s.add_argument("-o", "--out", type=Path)
    a = ap.parse_args(argv)
    try:
        doc = json.loads(a.output.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        print(f"rejected: cannot read {a.output}: {e}")
        return 1
    reasons = check(doc)
    if a.cmd == "check":
        print("accepted" if not reasons else "rejected:\n  " + "\n  ".join(reasons))
        return 0 if not reasons else 1
    result = ({"grader": GRADER, "status": "invalid", "ok": None, "reasons": reasons} if reasons
              else score(doc, a.archive))
    text = json.dumps(result, indent=2)
    if a.out:
        a.out.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
