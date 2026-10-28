"""The vti-02 fan-design pre-registered analysis (hera/campaigns/vti02-fan-design/analysis.py): the
tracked span, dominance, Holm, the permutation test, the endings and the frontier gate, on synthetic
run dirs.  No model calls, nothing under $HERA_DATA."""
from __future__ import annotations

import importlib.util
import json
import math
from pathlib import Path

import numpy as np
import pytest

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "hera" / "campaigns" / "vti02-fan-design" / "analysis.py"
FRONTIER = "vti02-fan-request-0822"


def _load():
    spec = importlib.util.spec_from_file_location("vti02_fan_analysis", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


A = _load()

FAN = {"status": "extracted", "landed": "fan", "form": "2d_megasweep", "field_mode": "invB", "spacing": "invB",
       "B_min_T": 0.8, "B_max_T": 8.0, "n_B": 101, "n_min_cm2": 1.5e12, "n_max_cm2": 3.2e12, "n_columns": 35,
       "D": 0.0, "slow_axis": "B", "slow_delay_s": 2.0, "fast_delay_s": 1.2, "excitation_V": 1.0,
       "bias_resistor_ohm": 1e8, "n_fans": 1, "stated_wall_clock_h": 4.0, "flags": [], "notes": "",
       "gate_current_reads": [],
       "lockins": [{"name": "sr1", "sensitivity_V": 1e-4, "sensitivity_set_in_answer": True,
                    "time_constant_s": 0.3, "time_constant_set_in_answer": True}]}


def _run_dir(root: Path, case: str, episodes: list[dict], *, model="claude-opus-5", effort="high") -> Path:
    """A run dir as hera-replay writes it; each episode dict gives its run block overrides and `doc`."""
    rd = root / case / "20260929T000000-test"
    rd.mkdir(parents=True)
    (rd / "run.json").write_text(json.dumps({"case": {"case": case, "run": {"model": model, "effort": effort}}}))
    for i, e in enumerate(episodes):
        ep = rd / "episodes" / f"{i:02d}"
        (ep / "session").mkdir(parents=True)
        (ep / "session" / "device_card.md").write_text("# Device card — vti-02 (tetralayer graphene)\n")
        run = {"case": case, "model": {"pinned": model, "observed": [model]}, "effort": effort, "status": "ok",
               "stop_cell_sweeps": True, "sweep_cell_appended": True,
               "image": {"metadata": {"condition": "full" if case.endswith("-corpus") else "none"}},
               **e.get("run", {})}
        (ep / "episode.json").write_text(json.dumps({"run": run}))
        for stamp, doc in e.get("docs", {}).items():
            g = ep / "grades" / "fan-design" / stamp
            g.mkdir(parents=True)
            (g / "output.json").write_text(json.dumps(doc))
    return rd


def test_one_column_spans_half_a_bin_times_its_weight():
    W = 2.0
    for w in (1.0, 0.6):
        assert A.span_bins(np.array([w]), np.array([3.0]), W, A.box.SPACING / 2) == pytest.approx(A.box.SPACING * w)
    assert A.box.SPACING == 0.5
    assert A.span_bins(np.array([0.0]), np.array([3.0]), W, 0.25) == 0.0


def test_columns_closer_than_half_a_bin_do_not_double_count():
    W, h = 2.0, A.box.SPACING / 2
    same = A.span_bins(np.array([1.0, 0.5]), np.array([3.0, 3.0]), W, h)
    assert same == pytest.approx(0.5)  # coincident: the larger weight, once
    near = A.span_bins(np.array([1.0, 0.5]), np.array([3.0, 3.0 + 0.1 / W]), W, h)
    assert near == pytest.approx(0.5 + 0.1 * 0.5)  # the 0.1-bin overhang at the lesser weight
    apart = A.span_bins(np.array([1.0, 0.5]), np.array([3.0, 3.0 + 0.5 / W]), W, h)
    assert apart == pytest.approx(0.5 + 0.25)


def test_dominance_truth_table():
    d = A.dominates
    assert not d((0.5, 3.0), (0.5, 3.0))
    assert d((0.6, 3.0), (0.5, 3.0)) and d((0.5, 2.0), (0.5, 3.0)) and d((0.6, 2.0), (0.5, 3.0))
    assert not d((0.6, 4.0), (0.5, 3.0)) and not d((0.4, 2.0), (0.5, 3.0)) and not d((0.4, 4.0), (0.5, 3.0))
    floor = (0.0, math.inf)
    assert not d(floor, floor) and d((0.0, 5.0), floor) and not d(floor, (0.0, 5.0))
    M = A.dominance_matrix([(0.6, 2.0), (0.5, 3.0), (0.7, 5.0)])
    assert M.tolist() == [[0, 1, 0], [-1, 0, 0], [0, 0, 0]]


def test_holm_on_a_known_vector():
    assert A.holm([0.01, 0.04, 0.03, 0.005]) == pytest.approx([0.03, 0.06, 0.06, 0.02])
    assert A.holm([0.5, 0.4]) == pytest.approx([0.8, 0.8])
    adj = A.holm([0.01, math.nan, 0.02, 0.2])
    assert math.isnan(adj[1]) and adj[0] == pytest.approx(0.04) and adj[2] == pytest.approx(0.06)


def test_permutation_p_is_deterministic_and_counts_the_observed_labelling():
    # [1, 1 | 0, 0]: 2 of the 6 labellings reach |Δ| = 1, so p -> 1/3
    groups = [(np.array([1.0, 1.0, 0.0, 0.0]), 2)]
    obs, p = A.permutation_p(groups, "mean")
    assert obs == 1.0 and p == A.permutation_p(groups, "mean")[1] and abs(p - 1 / 3) < 0.02
    assert A.permutation_p([(np.array([0.3, 0.3]), 1)], "mean") == (0.0, 1.0)
    D = A.dominance_matrix([(0.9, 1.0), (0.1, 2.0)])
    assert A.permutation_p([(D, 1)], "dominance") == (1.0, 1.0)  # one pair each way: always |D| = 1
    assert all(math.isnan(v) for v in A.permutation_p([], "mean"))


def test_a_run_dir_of_another_frontier_is_refused(tmp_path):
    rd = _run_dir(tmp_path, "vti02-pre-fan-0822-opus-corpus", [{"docs": {"a": FAN}}])
    with pytest.raises(A.Refused, match="not of the frontier"):
        A.analyse([rd], FRONTIER)
    assert A.main([str(rd), "--out", str(tmp_path / "out")]) == 1
    with pytest.raises(A.Refused):
        A.arm_of(f"{FRONTIER}-corpus", FRONTIER)  # no model tag
    with pytest.raises(A.Refused):
        A.arm_of(f"{FRONTIER}-opus-full", FRONTIER)
    assert A.arm_of(f"{FRONTIER}-opus55-none", FRONTIER) == "none"


def test_endings_and_an_end_to_end_analysis(tmp_path):
    probe = {"status": "extracted", "landed": "field_probe", "form": "probe_only", "B_min_T": 0.0, "B_max_T": 9.0,
             "n_B": 100, "spacing": "B", "n_cm2": [3.0e12], "declared_columns_cm2": [], "flags": [], "notes": ""}
    b0 = {"status": "cannot_extract", "landed": "b0_cell", "form": "b0_cell", "flags": [], "notes": ""}
    untraced = {**FAN, "lockins": [{**FAN["lockins"][0], "time_constant_s": None}]}
    corpus = _run_dir(tmp_path, f"{FRONTIER}-opus-corpus", [
        {"docs": {"a": {**FAN, "B_min_T": 3.0}, "b": FAN}},                   # the latest extraction counts
        {"docs": {"a": probe}},
        {"run": {"sweep_cell_appended": False, "status": "stall"}},
        {"run": {"model": {"pinned": "claude-sonnet-5", "observed": ["claude-sonnet-5"]}}, "docs": {"a": FAN}},
        {"run": {"stop_cell_sweeps": False}, "docs": {"a": FAN}},
        {"run": {"status": "quota"}},
    ])
    none = _run_dir(tmp_path, f"{FRONTIER}-opus-none", [
        {"docs": {"a": {**FAN, "n_max_cm2": 2.0e12, "n_columns": 6}}},
        {"docs": {"a": b0}},
        {"docs": {"a": untraced}},
    ])
    a = A.analyse([corpus, none], FRONTIER)
    endings = {r["key"].split("/", 1)[0].rsplit("-", 1)[1] + "/" + r["key"][-2:]: r["ending"] for r in a["episodes"]}
    assert endings == {"corpus/00": "fan", "corpus/01": "spot_check", "corpus/02": "nothing_landed",
                       "corpus/03": "excluded", "corpus/04": "excluded", "corpus/05": "excluded",
                       "none/00": "fan", "none/01": "b0_cell", "none/02": "re_extract"}
    reasons = {r["key"][-2:]: r["reason"] for r in a["episodes"] if r["ending"] == "excluded"}
    assert reasons["03"].startswith("override run") and reasons["04"].startswith("prep-cell")
    assert reasons["05"] == "status quota"
    assert a["blocking"] == [r["key"] for r in a["episodes"] if r["ending"] == "re_extract"]
    fan_c = next(r for r in a["episodes"] if r["key"].endswith("corpus/20260929T000000-test/00"))
    assert fan_c["extraction"].endswith("/b/output.json") and 0 < fan_c["p_call"] <= 1 and fan_c["span"] > 0
    assert fan_c["span"] == min(fan_c["span_light"], fan_c["span_split"])
    r1 = a["results"]["p_call_8h"]
    assert r1["models"] == ["claude-opus-5"] and r1["statistic"] == pytest.approx(r1["per_model"]["claude-opus-5"])
    assert set(a["results"]) == set(A.METRICS) and all("p_holm" in v for v in a["results"].values())
    cz = next(s for s in a["sensitivities"] if s["axis"] == "censoring")
    fan_n = next(r for r in a["episodes"] if r["ending"] == "fan" and r["arm"] == "none")
    assert cz["statistic"] == pytest.approx(A.value(fan_c, "p_call_8h") / 3 - A.value(fan_n, "p_call_8h") / 2)
    assert A.main([str(corpus), str(none), "--out", str(tmp_path / "out")]) == 2
    floored = A.analyse([corpus, none], FRONTIER, floor_unscored=True)
    assert not floored["blocking"]
    (fl,) = [r for r in floored["episodes"] if r.get("floored")]
    assert fl["ending"] == "fan" and fl["p_call"] == fl["span"] == fl["rows_fl"] == 0.0 and fl["hours"] == math.inf
    assert A.main([str(corpus), str(none), "--floor-unscored", "--out", str(tmp_path / "out")]) == 0
    assert json.loads((tmp_path / "out" / "analysis.json").read_text())["frontier"] == FRONTIER
