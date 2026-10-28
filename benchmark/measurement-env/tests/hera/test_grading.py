"""The grading harness and graders: the physics next to each grader, the graders' device table,
each grader's grade.py (check + score), submit_output, and the runner's prompt assembly.
No model calls."""
from __future__ import annotations

import csv
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from hera.grading import runner

REPO = Path(__file__).resolve().parents[2]
GRADERS = REPO / "hera" / "graders"
QC0426 = REPO / "hera/docs/notes/2026-06-19-QC0426-session-3"
VTI02 = REPO / "hera/docs/notes/2026-08-21-vti-02-session"
ZF1 = REPO / "hera/docs/notes/2026-06-22-zf1-session"


def _sibling(grader: str, module: str):
    """Import a module under graders/ the way a grade.py does (a file by path, not a package);
    grader "" is graders/ itself."""
    spec = importlib.util.spec_from_file_location(module, GRADERS / grader / f"{module}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def _grade(name: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(GRADERS / name / "grade.py"), *args], capture_output=True, text=True)


def _write(tmp_path: Path, doc: dict) -> Path:
    p = tmp_path / "output.json"
    p.write_text(json.dumps(doc), encoding="utf-8")
    return p


# ---------------------------------------------------------------- physics next to the graders
def test_s1_reproduces_the_archived_ref43_grade():
    s1 = _sibling("sdh-field-resolution", "s1")
    # 06-19 QC0426 cell 43: 501 rows 0-4 T at n = -5e12, strict window from 1.2 T -> pass, 351 rows in window
    ok, d = s1.field_resolution_ok(np.linspace(0, 4, 501), -5e12, kind="B", b_min=1.2, strict=True)
    assert ok and d["n_rows"] == 351
    assert d["columns"]["rows_per_period_min"][0] == pytest.approx(3.5051, abs=1e-3)
    assert d["columns"]["periods_usable"][0] == pytest.approx(30.156, abs=1e-2)


def test_sc_arc_reproduces_the_zf1_reference_survey():
    sc_arc = _sibling("sc-survey", "sc_arc")
    # 06-22 zf1 cell 31: 105 x 83 gate map -> 9 setpoints inside the arc (= archived run 2)
    T, G = np.meshgrid(np.linspace(-7.0, 6.0, 105), np.linspace(-4.0, 4.2, 83), indexing="ij")
    assert sc_arc.grade(T.ravel(), G.ravel()) == {"n_points": 105 * 83, "n_inside": 9, "pass": True}


# ---------------------------------------------------------------- devices
def test_device_of_reads_the_card_title():
    if not QC0426.exists():
        pytest.skip("QC0426 archive not present")
    devices = _sibling("", "devices")
    assert devices.device_of(QC0426) == "qc0426"
    assert devices.device_params(QC0426, "b_min_T")["b_min_T"] > 0
    if ZF1.exists():
        assert devices.device_of(ZF1) == "zf1"
        with pytest.raises(ValueError, match="lacks b_min_T"):
            devices.device_params(ZF1, "b_min_T")


# ---------------------------------------------------------------- sdh-field-resolution
FR = "sdh-field-resolution"
REF43 = {"status": "extracted", "B_min_T": 0.0, "B_max_T": 4.0, "n_points": 501, "spacing": "B",
         "n_cm2": -5.0e12, "flags": [], "notes": "cell 43"}


def test_spot_check_scores_the_reference_cell_like_the_fake_rig(tmp_path):
    if not QC0426.exists():
        pytest.skip("QC0426 archive not present")
    p = _write(tmp_path, REF43)
    assert _grade(FR, "check", str(p)).returncode == 0
    r = _grade(FR, "score", str(p), "--archive", str(QC0426), "-o", str(tmp_path / "scores.json"))
    assert r.returncode == 0, r.stderr
    s = json.loads((tmp_path / "scores.json").read_text())
    assert s["status"] == "graded" and s["ok"] is True and s["device"] == "qc0426" and s["kind"] == "spot"
    assert s["n_points"] == 501 and s["B_range_T"] == [0.0, 4.0] and s["n_cm2"] == [-5e12]
    assert s["s1"]["n_rows"] == 351 and s["params"]["b_min_T"] == 1.2


def test_cannot_extract_is_a_valid_result(tmp_path):
    if not QC0426.exists():
        pytest.skip("QC0426 archive not present")
    p = _write(tmp_path, {"status": "cannot_extract", "notes": "vector built by a feedback loop"})
    assert _grade(FR, "check", str(p)).returncode == 0
    s = json.loads(_grade(FR, "score", str(p), "--archive", str(QC0426)).stdout)
    assert s["status"] == "cannot_extract" and s["ok"] is None


@pytest.mark.parametrize("bad, needle", [
    ({**REF43, "n_cm2": None}, "give the density"),
    ({**REF43, "n_cm2": -5e16}, "units look like m^-2"),
    ({**REF43, "n_min_cm2": -1e12, "n_max_cm2": 1e12, "n_columns": 5}, "not both"),
    ({**REF43, "spacing": "invB"}, "B_min_T > 0"),
    ({**REF43, "n_points": 1}, "n_points"),
    ({**REF43, "status": "done"}, "status must be"),
    ({**REF43, "flags": ["oops"]}, "flags must be"),
])
def test_check_rejects_with_reasons(tmp_path, bad, needle):
    r = _grade(FR, "check", str(_write(tmp_path, bad)))
    assert r.returncode == 1 and needle in r.stdout, r.stdout


def test_fan_scores_a_1_over_B_fan_across_columns(tmp_path):
    if not QC0426.exists():
        pytest.skip("QC0426 archive not present")
    doc = {"status": "extracted", "B_min_T": 1.2, "B_max_T": 8.0, "n_points": 400, "spacing": "invB",
           "n_min_cm2": -6e12, "n_max_cm2": 6e12, "n_columns": 41, "flags": [], "notes": ""}
    p = _write(tmp_path, doc)
    assert _grade(FR, "check", str(p)).returncode == 0
    s = json.loads(_grade(FR, "score", str(p), "--archive", str(QC0426)).stdout)
    assert s["status"] == "graded" and s["ok"] is True and s["kind"] == "fan" and s["n_columns"] == 41
    assert s["s1"]["n_pass"] + s["s1"]["n_record_limited"] == 41
    # the same field axis at 4x the density under-samples the top columns
    p = _write(tmp_path, {**doc, "n_min_cm2": -2.4e13, "n_max_cm2": 2.4e13})
    s = json.loads(_grade(FR, "score", str(p), "--archive", str(QC0426)).stdout)
    assert s["ok"] is False and s["s1"]["n_sampling_fail"] > 0


def test_two_point_bundle_is_a_density_list(tmp_path):
    if not QC0426.exists():
        pytest.skip("QC0426 archive not present")
    p = _write(tmp_path, {**REF43, "B_max_T": 8.0, "n_points": 1001, "n_cm2": [-3e12, 3e12]})
    s = json.loads(_grade(FR, "score", str(p), "--archive", str(QC0426)).stdout)
    assert s["status"] == "graded" and s["n_columns"] == 2 and s["kind"] == "fan"


# ---------------------------------------------------------------- fan-design

FAN_A = {"status": "extracted", "landed": "fan", "form": "2d_megasweep", "B_min_T": 0.4, "B_max_T": 4.0, "n_B": 181, "spacing": "B",
         "n_min_cm2": 1e12, "n_max_cm2": 6e12, "n_columns": 31, "D": 0.0, "slow_axis": "B",
         "slow_delay_s": 2.0, "fast_delay_s": 2.2, "excitation_V": 0.5, "bias_resistor_ohm": 1e8,
         "n_fans": 1, "stated_wall_clock_h": 4.2, "flags": [], "notes": "", "gate_current_reads": [],
         "lockins": [{"name": "sr1", "sensitivity_V": 1e-5, "sensitivity_set_in_answer": True,
                      "time_constant_s": 0.3, "time_constant_set_in_answer": False}]}


def test_fan_resolution_orders_the_wiki_proposals_as_aaron_ruled():
    res = _sibling("fan-design", "resolution")
    kw = dict(b_cut=1.2)
    a = res.resolved_fraction(np.linspace(0.4, 4.0, 181), 1e12, 6e12, **kw)
    assert a < res.resolved_fraction(np.linspace(0.4, 4.0, 181), 1e12, 6e12, measure="B", **kw)  # low field weighs more
    b = res.resolved_fraction(np.linspace(0.0, 4.0, 151), 0.5e12, 8e12, **kw)
    c = res.resolved_fraction(np.linspace(1.0, 4.0, 376), 1e12, 5e12, **kw)
    assert b < a < c == 1.0
    # A's top column resolves only from about 2 T ("barely passes ... at the middle of the record")
    assert res.worst_column(np.linspace(0.4, 4.0, 181), 1e12, 6e12, **kw)["resolved_from_T"] == pytest.approx(1.92)


def test_fan_resolution_has_no_knife_edge_and_charges_a_high_start():
    res = _sibling("fan-design", "resolution")
    n_rows = int(round((1 / 1.2 - 1 / 4.0) * 3 * res.luttinger_frequency(6e12))) + 1
    exact3 = 1 / np.linspace(1 / 1.2, 1 / 4.0, n_rows)
    assert res.resolved_fraction(exact3, 1e12, 6e12, b_cut=1.2) == pytest.approx(1.0)
    # fine sampling from 2 T leaves 1.2 -> 2 T unresolved: (1/2 - 1/4) / (1/1.2 - 1/4)
    assert res.resolved_fraction(np.linspace(2.0, 4.0, 2001), 1e12, 6e12, b_cut=1.2) == pytest.approx(0.25 / (1 / 1.2 - 0.25))
    # rows under the cutoff are free
    assert (res.resolved_fraction(np.linspace(0.0, 4.0, 4001), 1e12, 6e12, b_cut=1.2)
            == pytest.approx(res.resolved_fraction(np.linspace(1.2, 4.0, 2801), 1e12, 6e12, b_cut=1.2)))


def test_fan_coverage_reads_the_density_range_against_the_window():
    res = _sibling("fan-design", "resolution")
    assert res.coverage(0.5e12, 3e12, 1e12, 4.5e12) == pytest.approx(
        {"covered_fraction": 2 / 3.5, "outside_fraction": 0.5 / 3.5})
    assert res.coverage(0.5e12, 8e12, 1e12, 4.5e12)["covered_fraction"] == 1.0


def test_fan_design_scores_a_fraction_and_no_verdict(tmp_path):
    if not QC0426.exists():
        pytest.skip("QC0426 archive not present")
    p = _write(tmp_path, FAN_A)
    assert _grade("fan-design", "check", str(p)).returncode == 0
    s = json.loads(_grade("fan-design", "score", str(p), "--archive", str(QC0426)).stdout)
    fr = s["scores"]["field_resolution"]
    assert s["status"] == "graded" and s["ok"] is None and s["params"]["m"] == 3.0
    assert s["device"] == "qc0426" and s["case"] == "qc0426-fan-design" and s["params"]["b_cut_T"] == 1.2
    assert fr["resolved_fraction"] < fr["resolved_fraction_B"] < 1.0
    assert fr["resolved_fraction"] < fr["resolved_fraction_recipe_floor"] < 1.0
    sc = s["scores"]
    assert sc["side_choice"] == {"favored": "electron", "favored_side_share": 1.0}
    assert sc["density_range"]["n_max_ratio"] == pytest.approx(6 / 3.5) and sc["field_reach"] == {"B_max_ratio": 1.0}

    def scores(**over):
        p = _write(tmp_path, {**FAN_A, **over})
        return json.loads(_grade("fan-design", "score", str(p), "--archive", str(QC0426)).stdout)["scores"]

    # drawing n_max in lifts the resolved fraction, and the ratio says why
    narrow = scores(n_max_cm2=3e12)
    assert narrow["field_resolution"]["resolved_fraction"] > fr["resolved_fraction"]
    assert narrow["density_range"]["n_max_ratio"] == pytest.approx(3 / 3.5)
    # the wrong side is its own score: the mirrored range reads the same against the window
    hole = scores(n_min_cm2=-6e12, n_max_cm2=-1e12)
    assert hole["side_choice"]["favored_side_share"] == 0.0
    assert hole["density_range"] == {**sc["density_range"], "mirrored": True}
    assert hole["field_resolution"] == sc["field_resolution"]
    both = scores(n_min_cm2=-2e12)
    assert both["side_choice"]["favored_side_share"] == pytest.approx(0.75) and not both["density_range"]["mirrored"]
    assert scores(B_max_T=2.0, n_B=81)["field_reach"]["B_max_ratio"] == 0.5


def test_fan_design_landed_gates_the_shape(tmp_path):
    def reasons(doc):
        return _grade("fan-design", "check", str(_write(tmp_path, doc))).stdout
    assert "landed must be" in reasons({k: v for k, v in FAN_A.items() if k != "landed"})
    assert "landed must be" in reasons({"status": "cannot_extract", "flags": [], "notes": ""})
    assert "cannot_extract" in reasons({**FAN_A, "landed": "b0_cell"})
    assert "field_mode must be" in reasons({**FAN_A, "field_mode": "spiral"})
    assert _grade("fan-design", "check", str(_write(tmp_path, {**FAN_A, "field_mode": "B"}))).returncode == 0
    # a field probe needs only the axes: one column is enough, no timing or lock-ins
    probe = {"status": "extracted", "landed": "field_probe", "form": "probe_only", "B_min_T": 0.0, "B_max_T": 9.984,
             "n_B": 417, "spacing": "B", "n_cm2": [3.0e12], "declared_columns_cm2": [], "flags": [], "notes": ""}
    assert _grade("fan-design", "check", str(_write(tmp_path, probe))).returncode == 0
    assert "a fan has columns" in reasons({**FAN_A, "n_min_cm2": None, "n_max_cm2": None, "n_columns": None, "n_cm2": [1e12]})


def test_fan_design_vti02_case_scores_the_live_fan_in_the_actual_frame(tmp_path):
    """The 08-21 live fan (run 8) as the extractor returns it: field_invB(10, 2.4, 36), n 1.5-3.4e12 in the
    session's calibration frame; the case scales by 0.92 and grades it in the box."""
    if not VTI02.exists():
        pytest.skip("vti-02 archive not present")
    fan = {**FAN_A, "field_mode": "invB", "B_min_T": 2.4, "B_max_T": 10.0, "n_B": 36, "spacing": "invB",
           "n_min_cm2": 1.5e12, "n_max_cm2": 3.4e12, "n_columns": 41}
    s = json.loads(_grade("fan-design", "score", str(_write(tmp_path, fan)), "--archive", str(VTI02)).stdout)
    assert s["status"] == "graded" and s["landed"] == "fan" and s["case"] == "vti02-live-0821"
    assert s["device"] == "vti-02" and s["params"]["scheme"] == "box" and s["params"]["n_scale"] == 0.92
    assert s["params"]["tone_model"] == "Halder_ABAB" and s["params"]["b_lo_light_T"] == 0.75
    assert set(s["scores"]) == {"box", "derived"}
    bx = s["scores"]["box"]
    # a 2.4 T start holds 1.5-3.5 light-tone periods only at its top densities: partial credit there, both parts
    for c in ("light", "split"):
        w = bx[c]
        assert w["columns_full"] == 0 and w["columns_weighted"] + w["not_weighted"]["periods_short"] == 41
        assert w["not_weighted"]["undersampled"] == 0 and 0 < w["score"] < 1
        assert all(1.5 < p < 3.5 for p in w["chosen_periods"])
    assert bx["quality"] == pytest.approx(bx["A"] * (bx["light"]["score"] + bx["split"]["score"]) / 14)
    assert 0 < bx["p_call"] < 0.1  # three partial points: little, and not nothing
    assert bx["windows"]["light"]["B_from_T"] == pytest.approx(2.4)
    # 5 nA at tau 0.3 s: the detection probability at x = 2.74
    assert bx["A"] == pytest.approx(_sibling("fan-design", "box").detection(5 * 0.3 ** 0.5)) and 0.3 < bx["A"] < 0.6
    assert bx["hours"] == s["scores"]["derived"]["cost"]["estimated_wall_h"]
    # a probe landing: sampling per column, no fan scores
    probe = {"status": "extracted", "landed": "field_probe", "form": "probe_only", "B_min_T": 0.0, "B_max_T": 9.984,
             "n_B": 417, "spacing": "B", "n_cm2": [3.0e12], "declared_columns_cm2": [], "flags": [], "notes": ""}
    s = json.loads(_grade("fan-design", "score", str(_write(tmp_path, probe)), "--archive", str(VTI02)).stdout)
    assert s["status"] == "graded" and s["landed"] == "field_probe" and set(s["scores"]) == {"sampling", "field_reach", "unscored"}
    (col,) = s["scores"]["sampling"]["columns"]
    assert col["n_cm2"] == pytest.approx(2.76e12) and col["periods_in_window"] == pytest.approx(28.5 * (1 / 2.0 - 1 / 9.984), rel=0.01)
    s = json.loads(_grade("fan-design", "score", str(_write(tmp_path, {"status": "cannot_extract", "landed": "b0_cell",
                                                                        "form": "b0_cell", "flags": [], "notes": ""})), "--archive", str(VTI02)).stdout)
    assert s == {**s, "status": "cannot_extract", "landed": "b0_cell", "form": "b0_cell", "tier": "none", "ok": None}


def test_fan_design_case_lookup_matches_an_arm_to_its_case(tmp_path):
    grade = _sibling("fan-design", "grade")
    session = tmp_path / "session"; session.mkdir()
    def case(name):
        (tmp_path / "episode.json").write_text(json.dumps({"run": {"case": name}}))
        return grade.case_of(session)
    prod, prod24 = case("vti02-pre-fan-0822-fable51-corpus"), case("vti02-pre-fan-0824-gpt6sol-none")
    assert prod["case"] == "vti02-pre-fan-0822" and prod24["case"] == "vti02-pre-fan-0824"
    assert prod24["n_scale"] == 0.90 and prod24["scheme"] == "box" and prod24["signal_lockin"] == "sr1"
    # the development frontiers grade as their production twins
    dev, dev24 = case("vti02-fan-design-fable-corpus"), case("vti02-probe-first-opus-none")
    assert {k: v for k, v in dev.items() if k != "case"} == {k: v for k, v in prod.items() if k != "case"}
    assert {k: v for k, v in dev24.items() if k != "case"} == {k: v for k, v in prod24.items() if k != "case"}
    request = case("vti02-fan-request-0822-astra-corpus")
    assert request["case"] == "vti02-fan-request-0822"
    assert {k: v for k, v in request.items() if k != "case"} == {k: v for k, v in prod.items() if k != "case"}
    with pytest.raises(ValueError, match="no claim rectangle"):
        case("vti02-no-such-cut-opus-none")


def test_fan_design_form_gates_the_shape(tmp_path):
    def reasons(doc):
        return _grade("fan-design", "check", str(_write(tmp_path, doc))).stdout
    assert "form must be" in reasons({k: v for k, v in FAN_A.items() if k != "form"})
    assert "does not go with landed" in reasons({**FAN_A, "form": "probe_only"})
    assert 'field_mode "ramp"' in reasons({**FAN_A, "form": "continuous_ramp"})
    probe = {"status": "extracted", "landed": "field_probe", "form": "column_series", "B_min_T": 1.2, "B_max_T": 10.0,
             "n_B": 367, "spacing": "B", "n_cm2": [2.5e12], "declared_columns_cm2": [], "flags": [], "notes": ""}
    assert "at least one density" in reasons(probe)
    assert 'is "column_series"' in reasons({**probe, "form": "probe_only", "declared_columns_cm2": [1.5e12]})
    ramp = {**FAN_A, "form": "continuous_ramp", "field_mode": "ramp", "B_ramp_start_T": 0.7, "B_ramp_target_T": 8.0,
            "ramp_rate_T_per_min": None, "n_rows_declared": 38}
    for k in ("B_min_T", "B_max_T", "n_B", "spacing"):
        ramp.pop(k)
    assert _grade("fan-design", "check", str(_write(tmp_path, ramp))).returncode == 0
    assert "n_rows_declared" in reasons({k: v for k, v in ramp.items() if k != "n_rows_declared"})


COLUMN_SERIES = {"status": "extracted", "landed": "field_probe", "form": "column_series", "B_min_T": 1.216,
                 "B_max_T": 10.0, "n_B": 367, "spacing": "B", "n_cm2": [2.5e12], "declared_columns_cm2": [1.5e12, 2.0e12],
                 "ladder_stated_h_per_column": 1.47, "D": 0.0, "slow_axis": "B", "slow_delay_s": 0.0, "fast_delay_s": 0.7,
                 "lockins": [{"name": "sr1", "sensitivity_V": 5e-5, "sensitivity_set_in_answer": True,
                              "time_constant_s": 0.1, "time_constant_set_in_answer": False}],
                 "excitation_V": 1.0, "bias_resistor_ohm": 1e8, "n_fans": 1, "stated_wall_clock_h": 1.47,
                 "flags": [], "notes": "", "gate_current_reads": []}


def test_fan_design_column_series_is_scored_as_a_fan_over_the_declared_ladder(tmp_path):
    """The Fable-none smoke: one 1D column at n = 2.5e12 with the plan naming 1.5 and 2.0e12 next.  The
    density axis is the union, on the landed field grid; the output says the ladder is declared."""
    if not VTI02.exists():
        pytest.skip("vti-02 archive not present")
    s = json.loads(_grade("fan-design", "score", str(_write(tmp_path, COLUMN_SERIES)), "--archive", str(VTI02)).stdout)
    assert s["status"] == "graded" and s["landed"] == "field_probe" and s["form"] == "column_series" and s["tier"] == "fan"
    assert s["design"]["declared_not_landed"] is True and s["design"]["declared_columns_cm2"] == [1.5e12, 2.0e12]
    sc = s["scores"]
    assert set(sc) == {"box", "derived"}
    assert sc["derived"]["n_columns"] == 3 and sc["derived"]["n_columns_landed"] == 1 and sc["derived"]["n_points"] == 367
    assert sc["derived"]["n_range_actual_cm2"] == pytest.approx([0.92 * 1.5e12, 0.92 * 2.5e12])
    assert sc["box"]["columns"] == 3 and sc["box"]["params"]["cap"] == 7
    assert sc["derived"]["cost"]["ladder"] == {"columns": 3, "estimated_wall_h": pytest.approx(3 * sc["derived"]["cost"]["estimated_wall_h"]),
                                               "stated_h_per_column": 1.47, "stated_wall_h": pytest.approx(4.41)}
    assert sc["box"]["hours"] == sc["derived"]["cost"]["ladder"]["estimated_wall_h"]
    # the plan priced a column at ~88 min from run 5's actual: the rig model lands within 10 %
    assert sc["derived"]["cost"]["estimated_wall_h"] == pytest.approx(1.47, rel=0.1)
    # the same column with no ladder is a probe: sampling only, the density axes unscored with a reason
    probe = {**COLUMN_SERIES, "form": "probe_only", "declared_columns_cm2": [], "ladder_stated_h_per_column": None}
    s = json.loads(_grade("fan-design", "score", str(_write(tmp_path, probe)), "--archive", str(VTI02)).stdout)
    assert s["tier"] == "probe" and set(s["scores"]) == {"field_reach", "sampling", "unscored", "derived"}
    assert set(s["scores"]["unscored"]) == {"side_choice", "field_resolution", "density_range"}


RAMP_0823 = {"status": "extracted", "landed": "fan", "form": "continuous_ramp", "field_mode": "ramp",
             "B_ramp_start_T": 0.71, "B_ramp_target_T": 8.0, "ramp_rate_T_per_min": 0.137, "n_rows_declared": 38,
             "n_min_cm2": -1.9e12, "n_max_cm2": 3.2e12, "n_columns": 122, "D": 0.0, "slow_axis": "B",
             "slow_delay_s": 0.0, "fast_delay_s": 0.5,
             "lockins": [{"name": "sr1", "sensitivity_V": None, "sensitivity_set_in_answer": False,
                          "time_constant_s": 0.1, "time_constant_set_in_answer": True}],
             "excitation_V": 1.0, "bias_resistor_ohm": 1e8, "n_fans": 1, "stated_wall_clock_h": 1.08,
             "flags": [], "notes": "", "gate_current_reads": []}


def test_fan_design_continuous_ramp_gets_effective_rows_from_the_rig_model(tmp_path):
    """08-23 run 6: 38 declared gate rows of 122 points at 0.5 s riding a 0.137 T/min ramp from 0.71 T.
    The data show 37 rows 0.201 T apart and one at the target; the model gives 0.204 T."""
    if not VTI02.exists():
        pytest.skip("vti-02 archive not present")
    grade = _sibling("fan-design", "grade")
    cost = {"ramp_T_per_min": 0.137, "field_settle_s": 3.0, "point_overhead_s": 0.2, "gate_read_s_per_plc": 0.045,
            "flyback_s": 4.0}
    rr = grade.ramp_rows(RAMP_0823, cost, 122)
    assert rr["dB_row_T"] == pytest.approx(0.204, abs=0.003) and rr["n_rows_effective"] == 37
    assert rr["B_range_T"] == [0.71, 8.0]  # 36 rows on the ramp, then the target
    # more declared rows than the ramp needs: the rest sit at the target and collapse to one row there
    rr = grade.ramp_rows({**RAMP_0823, "n_rows_declared": 60}, cost, 122)
    assert rr["n_rows_effective"] == 37 and rr["B_range_T"][1] == 8.0
    # the cell's rate wins over the case's; a descending ramp works
    rr = grade.ramp_rows({**RAMP_0823, "ramp_rate_T_per_min": 0.274, "B_ramp_start_T": 8.0, "B_ramp_target_T": 0.0,
                          "n_rows_declared": None}, cost, 122)
    assert rr["rate_source"] == "cell" and rr["dB_row_T"] == pytest.approx(0.408, abs=0.005) and rr["B_range_T"] == [0.0, 8.0]
    s = json.loads(_grade("fan-design", "score", str(_write(tmp_path, RAMP_0823)), "--archive", str(VTI02)).stdout)
    assert s["status"] == "graded" and s["form"] == "continuous_ramp" and s["tier"] == "fan"
    assert s["design"]["ramp"]["n_rows_effective"] == 37 and s["design"]["ramp"]["rate_source"] == "cell"
    sc = s["scores"]
    # linear in B: only the high-field intervals sample F_L, and they hold under 1.5 light-tone periods, so no
    # split; the far slower light tone is sampled over the whole record
    assert sc["box"]["split"]["score"] == 0 and sc["box"]["light"]["score"] > 1
    # the ramp's clock is the ramp: 7.29 T at 0.137 T/min = 53 min; the run took 55
    assert sc["derived"]["cost"]["estimated_wall_h"] == pytest.approx(0.89, abs=0.03)
    assert sc["box"]["hours"] == sc["derived"]["cost"]["estimated_wall_h"]


def test_fan_design_cost_model_reproduces_the_live_wall_clocks():
    """Each live vti-02 fan's wall clock from its metadata against the rig model, within 8 %."""
    grade = _sibling("fan-design", "grade")
    cost = {"ramp_T_per_min": 0.137, "field_settle_s": 3.0, "point_overhead_s": 0.2, "gate_read_s_per_plc": 0.045,
            "flyback_s": 4.0}
    live = [  # (B axis, n_fast, slow_delay, fast_delay, measured hours)
        (1 / np.linspace(1 / 2.4, 1 / 10.0, 36), 41, 2.0, 0.7, 1.32),       # 08-21 run 8
        (1 / np.linspace(1 / 1.0, 1 / 10.0, 101), 61, 3.0, 1.2, 3.53),      # 08-22 run 8
        (1 / np.linspace(1 / 0.75, 1 / 6.0, 40), 46, 1.0, 0.7, 1.23),       # 08-24 run 4
        (1 / np.linspace(1 / 1.0, 1 / 8.0, 101), 57, 2.5, 2.1, 4.60),       # 08-25 run 8
        (np.linspace(0.0, 10.0, 417), 1, 0.0, 0.7, 100 / 60),               # 08-21 run 5 (1D spot check, 100 min actual)
    ]
    for B, n_fast, sd, fd, hours in live:
        est = grade.estimated_wall_h(np.sort(B), n_fast, sd, fd, cost)["estimated_wall_h"]
        assert est == pytest.approx(hours, rel=0.08), (n_fast, est, hours)


def test_fan_design_cost_model_prices_the_gate_reads_nplc():
    """The vti-02 NPLC-10 leakage legs (two 2400 gate-current reads, one gate row at fixed field)
    within 8 % of their wall clocks; NPLC 1 leaves the overhead as fitted on the fans."""
    grade = _sibling("fan-design", "grade")
    cost = {"ramp_T_per_min": 0.137, "field_settle_s": 3.0, "point_overhead_s": 0.2, "gate_read_s_per_plc": 0.045,
            "flyback_s": 4.0}
    reads = lambda nplc: {"gate_current_reads": [{"name": g, "nplc": nplc, "nplc_set_in_answer": True}
                                                 for g in ("k_2400_tg_curr", "k_2400_bg_curr")]}
    legs = [(251, 1.0, 511.4), (101, 1.0, 216.9), (101, 1.0, 208.3), (151, 0.7, 265.2)]  # 08-21 r0, 08-22 r0/r1, 08-25 r0
    at10 = grade.design_cost(reads(10.0), cost)
    for n_fast, fd, seconds in legs:
        est = grade.estimated_wall_h(np.array([0.0]), n_fast, 0.0, fd, at10)["estimated_wall_h"]
        assert est * 3600 == pytest.approx(seconds, rel=0.08), (n_fast, est * 3600, seconds)
    assert grade.design_cost(reads(1.0), cost)["point_overhead_s"] == pytest.approx(0.2)
    assert grade.design_cost({"gate_current_reads": []}, cost)["point_overhead_s"] == pytest.approx(0.2)


def test_fan_design_check_reads_gate_current_nplc():
    """The prompt's worked examples pass check; a malformed gate_current_reads does not."""
    grade = _sibling("fan-design", "grade")
    text = (GRADERS / "fan-design" / "prompt.md").read_text()
    examples = [json.loads(b.split("```")[0]) for b in text.split("```json\n")[1:]]
    assert len(examples) == 4 and all(grade.check(d) == [] for d in examples)
    msgs = lambda gc: [m for m in grade.check({**examples[0], "gate_current_reads": gc}) if "gate_current_reads" in m]
    assert msgs([]) == [] and len(msgs(None)) == 1
    assert len(msgs([{"name": "k_2400_tg_curr", "nplc": None, "nplc_set_in_answer": True}, {"name": "", "nplc": 1.0}])) == 3
    assert msgs("NPLC 10") == ["gate_current_reads must be a list (possibly empty) of objects, one per recorded gate current"]


def _box_doc(I_A=1e-8, tau=0.3, delay=1.2, sens=1e-4):
    return {"excitation_V": I_A * 1e8, "bias_resistor_ohm": 1e8, "fast_delay_s": delay,
            "lockins": [{"name": "sr1", "sensitivity_V": sens, "time_constant_s": tau}]}


def _box(B, n12, doc, **kw):
    box = _sibling("fan-design", "box")
    kw = {"b_lo_light": 0.75, "b_lo_split": 1.0, "tone_model": "Halder_ABAB", "signal_lockin": "sr1", **kw}
    return box.score(np.asarray(B, float), np.asarray(n12, float) * 1e12, doc, **kw)


def test_box_best_spaced_is_exact():
    """The optimizer against brute force: the best <= cap columns whose f sit pairwise >= gap apart."""
    import itertools
    box = _sibling("fan-design", "box")
    rng = np.random.default_rng(7)
    for _ in range(400):
        N = int(rng.integers(0, 10))
        w, f = rng.random(N) * (rng.random(N) > 0.2), rng.random(N) * 3
        gap, cap = rng.random() * 1.2 + 0.05, int(rng.integers(1, 6))
        brute = max(sum(w[list(S)]) for r in range(min(cap, N) + 1) for S in itertools.combinations(range(N), r)
                    if all(abs(f[a] - f[b]) >= gap for a, b in itertools.combinations(S, 2)))
        total, chosen = box.best_spaced(w, f, gap, cap)
        assert total == pytest.approx(brute) and sum(w[chosen]) == pytest.approx(total) and len(chosen) <= cap
        assert all(abs(f[a] - f[b]) >= gap for a, b in itertools.combinations(chosen, 2))
    # columns exactly one bin apart may both count; identical tones never do
    assert box.best_spaced(np.array([1.0, 1.0, 1.0]), np.array([0.0, 0.3, 0.6]), 0.3, 5)[0] == 3.0
    assert box.best_spaced(np.array([1.0, 0.5]), np.array([2.0, 2.0]), 0.3, 5) == (1.0, [0])


def test_box_w_eff_counts_the_record_that_samples_the_tone():
    box = _sibling("fan-design", "box")
    du = np.array([0.01, 0.01, 0.1])
    # a 10 T tone: 10 rows per period in the fine intervals, 1 in the coarse one (aliased, not counted)
    assert box.w_eff(np.array([10.0]), du, box.M)[0] == pytest.approx(0.02)
    # 2.5 rows per period in the coarse interval counts half its length
    assert box.w_eff(np.array([4.0]), du, box.M)[0] == pytest.approx(0.02 + 0.05)
    assert box.w_eff(np.array([0.0, 1.0]), du, box.M).tolist() == [0.0, pytest.approx(0.12)]


def test_box_scores_the_reference_fan_by_hand():
    """08-25 r8: 1/B 8 -> 1 T x 101, n 1.20-3.05e12 actual x 57, 50 nA, tau 0.3 s, 7 tau.  Both windows
    start at 1.0 T and every interval holds >= 3.6 rows per F_L period, so W_eff = W and each column's
    weight is the period ramp alone."""
    box = _sibling("fan-design", "box")
    n = np.linspace(1.2, 3.05, 57)
    B = 1 / np.linspace(1 / 1.0, 1 / 8.0, 101)
    r = _box(B, n, _box_doc(I_A=5e-8, delay=2.1))
    W = 1 / 1.0 - 1 / 8.0
    fl = box.f_light(n, "Halder_ABAB")
    w = np.clip((fl * W - 1.5) / 2.0, 0, 1)
    assert r["windows"]["light"]["W_per_T"] == pytest.approx(W) and r["light"]["min_spacing_T"] == r["split"]["min_spacing_T"] == pytest.approx(0.5 / W)
    total, _ = box.best_spaced(w, fl, 0.5 / W, 7)
    for c in ("light", "split"):
        assert r[c]["score"] == pytest.approx(total)
        assert r[c]["chosen_periods"] == pytest.approx([fl[np.argmin(abs(n - x))] * W for x in r[c]["chosen_n_actual_1e12"]])
    assert r["quality"] == pytest.approx(total / 7) and 0.95 < r["quality"] <= 1
    # 50 nA: every spaced column is a near-certain detection, so four are all but guaranteed
    assert r["p_call"] > 0.99
    _, spread = box.best_spaced(w, fl, 0.5 / W, n.size)
    assert r["split"]["p_call"] == pytest.approx(box.p_call([r["A"] * w[j] for j in spread]))
    # dense columns add nothing: the same range at twice the density scores about the same
    assert _box(B, np.linspace(1.2, 3.05, 113), _box_doc(I_A=5e-8, delay=2.1))["split"]["score"] == pytest.approx(total, abs=0.1)
    # hard lines are a multiverse sensitivity
    hard = _box(B, n, _box_doc(I_A=5e-8, delay=2.1), m=(2.999, 3.0), k=(2.999, 3.0))
    assert set(hard["split"]["chosen_weights"]) == {1.0}


def test_box_p_at_least_is_the_poisson_binomial_tail():
    import itertools
    box = _sibling("fan-design", "box")
    ps = [0.9, 0.5, 0.2, 0.7]
    brute = sum(np.prod([p if b else 1 - p for p, b in zip(ps, bits)])
                for bits in itertools.product([0, 1], repeat=4) if sum(bits) >= 3)
    assert box.p_at_least(ps, 3) == pytest.approx(brute)
    assert box.p_at_least(ps, 0) == pytest.approx(1.0) and box.p_at_least([], 1) == 0.0


def test_box_p_call_counts_partial_lines_and_saturates_at_four():
    box = _sibling("fan-design", "box")
    assert [box.p_call([1.0] * k) for k in range(6)] == pytest.approx([0, 5 / 32, 0.5, 27 / 32, 1, 1])
    # uncertain detections: the expectation of the curve over the number detected
    ps = [0.9, 0.5, 0.2]
    d = box.detected(ps)
    assert d.sum() == pytest.approx(1.0) and d[3] == pytest.approx(0.9 * 0.5 * 0.2)
    assert box.p_call(ps) == pytest.approx(d[1] * 5 / 32 + d[2] * 0.5 + d[3] * 27 / 32)
    assert box.p_call([]) == 0.0


def test_box_split_window_charges_field_below_1_T_and_the_light_tone_does_not():
    """A fine 1/B grid from 0.5 T: columns whose light tone holds over 1.5 periods above 0.75 T but under 1.5
    above 1.0 T earn light credit and no split credit."""
    box = _sibling("fan-design", "box")
    B = 1 / np.linspace(1 / 0.5, 1 / 10.0, 4001)
    Wl, Ws = 1 / 0.75 - 1 / 10.0, 1 / 1.0 - 1 / 10.0
    grid = np.linspace(0.5, 3.5, 301)
    fl = box.f_light(grid, "Halder_ABAB")
    mid = grid[(fl * Wl > 1.6) & (fl * Ws < 1.45)]
    assert mid.size
    r = _box(B, mid, _box_doc())
    assert r["split"]["score"] == 0 and r["split"]["not_weighted"]["periods_short"] == mid.size
    assert r["light"]["columns_weighted"] == mid.size and r["light"]["score"] > 0
    # each part spaces its columns by half a bin of its own window
    assert r["light"]["min_spacing_T"] == pytest.approx(0.5 / r["windows"]["light"]["W_per_T"])
    assert r["split"]["min_spacing_T"] == pytest.approx(0.5 / r["windows"]["split"]["W_per_T"])
    assert r["split"]["min_spacing_T"] > r["light"]["min_spacing_T"]
    assert _box(B, mid, _box_doc(), b_lo_split=0.75)["split"]["score"] == pytest.approx(r["light"]["score"])


def test_box_credits_the_part_of_the_record_that_samples_each_tone():
    """A coarse 1/B grid undersamples F_L in every interval; the far slower light tone is sampled. A grid
    linear in B samples F_L only at high field, where the 1/B record is short."""
    r = _box(1 / np.linspace(1 / 1.0, 1 / 10.0, 25), [2.0, 2.4, 2.8], _box_doc())
    assert r["split"]["score"] == 0 and r["split"]["not_weighted"]["undersampled"] == 3
    assert r["light"]["score"] > 0
    lin = _box(np.linspace(0.5, 10, 39), [2.0, 2.5, 2.9], _box_doc())
    assert lin["split"]["score"] < lin["light"]["score"] and lin["light"]["score"] > 1


def test_box_p_call_is_the_lesser_part():
    """The fan has to do both. A coarse 1/B grid over many densities finds the light tone and cannot
    part F_L from the heavy tone, so it does not support the call."""
    n = np.linspace(1.4, 3.1, 41)
    coarse = _box(1 / np.linspace(1 / 1.0, 1 / 10.0, 25), n, _box_doc(I_A=5e-8))
    assert coarse["light"]["p_call"] > 0.9 and coarse["split"]["p_call"] == 0
    assert coarse["p_call"] == 0
    fine = _box(1 / np.linspace(1 / 0.75, 1 / 10.0, 181), n, _box_doc())
    assert 0 < fine["split"]["p_call"] < fine["light"]["p_call"]
    assert fine["p_call"] == fine["split"]["p_call"]


def test_box_leaves_out_holes_and_clipped_columns():
    B = 1 / np.linspace(1 / 1.0, 1 / 10.0, 181)
    r = _box(B, [-1.5, -0.9, 2.0, 2.5], _box_doc())
    assert r["hole_or_off_table"] == 2 and r["split"]["columns_full"] == 2
    # 10 nA on a 5 uV scale: I * max|R| crosses 95 % of it wherever the composite reads above 475 ohm
    clip = _box(B, [2.0, 2.5, 3.0], _box_doc(sens=5e-6))
    assert clip["clipped"] == 3 and clip["quality"] == 0


def test_box_acquisition_is_the_detection_probability():
    """A: the chance a tone's peak clears the detection threshold, 1 at 50 nA / 0.3 s."""
    box = _sibling("fan-design", "box")
    A = lambda **kw: box.acquisition(_box_doc(**kw), "sr1")["A"]
    assert A(I_A=5e-8, tau=0.3, delay=1.2) == pytest.approx(1.0)       # the reference, 08-25 r8
    assert A(tau=0.3, delay=1.2) == pytest.approx(0.82, abs=0.01)      # 10 nA: 08-22 r8's split plateau
    assert A(tau=0.1, delay=0.4) == pytest.approx(0.53, abs=0.01)
    # the rig noise model at short tau, not used in the fit
    assert A(tau=0.01, delay=0.04) == pytest.approx(0.04, abs=0.01)
    assert A(tau=0.03, delay=0.12) == pytest.approx(0.2, abs=0.02)
    assert A(I_A=5e-8, tau=1e-3, delay=0.01) == 0.0                    # the 2 f_ref ripple, any current
    assert A(tau=0.1, delay=0.1) == pytest.approx(0.75 * A(tau=0.1, delay=0.4))
    # the signal lock-in carries the tone, whatever the others record and in whatever order
    doc = {**_box_doc(), "lockins": [{"name": "sr0", "sensitivity_V": 0.2, "time_constant_s": 1.0},
                                     {"name": "sr1", "sensitivity_V": 1e-4, "time_constant_s": 0.1}]}
    acq = box.acquisition(doc, "sr1")
    assert acq["A"] == pytest.approx(A(tau=0.1)) and acq["sensitivity_V"] == 1e-4
    # quantized once the LSB reaches the per-point noise: above 0.49 mV at 0.3 s, 0.98 mV at 0.1 s
    q = lambda sens, tau: box.acquisition(_box_doc(sens=sens, tau=tau), "sr1")["quantized"]
    assert q(5e-4, 0.3) and not q(2e-4, 0.3) and q(1e-3, 0.1) and not q(5e-4, 0.1)


def test_box_scores_nothing_it_cannot_trace():
    """No signal lock-in: A = 0.  An untraced tau or drive: quality unscored, never full credit."""
    B, n = 1 / np.linspace(1 / 1.0, 1 / 10.0, 101), np.linspace(1.9, 2.9, 30)
    assert _box(B, n, _box_doc())["quality"] > 0.5
    other = _box(B, n, {**_box_doc(), "lockins": [{"name": "sr0", "sensitivity_V": 0.02, "time_constant_s": 0.3}]})
    assert other["quality"] == 0 and other["A"] == 0 and other["flags"] == ["sr1 not recorded: A = 0"]
    for doc in (_box_doc(tau=None), {**_box_doc(), "excitation_V": None}):
        r = _box(B, n, doc)
        assert r["quality"] is None and r["p_call"] is None and r["split"]["score"] > 0
        assert "tau or drive not extracted: quality not scored" in r["flags"]


def test_fan_design_case_base_inherits_the_frontier_table(tmp_path):
    grade = _sibling("fan-design", "grade")
    session = tmp_path / "session"; session.mkdir()
    (tmp_path / "episode.json").write_text(json.dumps({"run": {"case": "vti02-live-0822"}}))
    c = grade.case_of(session)
    assert c["case"] == "vti02-live-0822" and c["n_scale"] == 0.886 and c["b_cut_T"] == 2.0 and c["side"] == "electron"
    assert c["ramp_T_per_min"] == 0.137 and "base" not in c


# ---------------------------------------------------------------- sc-survey
def test_sc_survey_scores_the_zf1_reference_grid(tmp_path):
    if not ZF1.exists():
        pytest.skip("zf1 archive not present")
    doc = {"status": "extracted", "V_tg": {"min": -7.0, "max": 6.0, "n": 105}, "V_bg": {"min": -4.0, "max": 4.2, "n": 83},
           "points": None, "flags": [], "notes": "cell 31"}
    p = _write(tmp_path, doc)
    assert _grade("sc-survey", "check", str(p)).returncode == 0
    s = json.loads(_grade("sc-survey", "score", str(p), "--archive", str(ZF1)).stdout)
    assert s["status"] == "graded" and s["ok"] is True and s["n_inside"] == 9 and s["n_points"] == 105 * 83
    p = _write(tmp_path, {**doc, "V_tg": None, "V_bg": None, "points": [[-5.4, 4.0], [-5.45, 4.05], [-5.5, 4.1], [0, 0]]})
    s = json.loads(_grade("sc-survey", "score", str(p), "--archive", str(ZF1)).stdout)
    assert s["n_points"] == 4 and s["n_inside"] == 3 and s["ok"] is True


# ---------------------------------------------------------------- submit_output
def test_submit_output_checks_and_writes_the_sentinel(tmp_path):
    out = _write(tmp_path, REF43)
    env = {**os.environ, "HERA_GRADER_DIR": str(GRADERS / FR), "HERA_OUTPUT_PATH": str(out),
           "HERA_SENTINEL": str(tmp_path / "accepted")}
    r = subprocess.run([sys.executable, "-m", "hera.grading.submit"], env=env, capture_output=True, text=True)
    assert r.returncode == 0 and "accepted" in r.stdout and (tmp_path / "accepted").exists()
    out.write_text(json.dumps({**REF43, "n_points": 1}))
    (tmp_path / "accepted").unlink()
    r = subprocess.run([sys.executable, "-m", "hera.grading.submit"], env=env, capture_output=True, text=True)
    assert r.returncode == 1 and "rejected" in r.stdout and not (tmp_path / "accepted").exists()


# ---------------------------------------------------------------- runner
def test_prompt_assembly_substitutes_paths_and_keeps_both_parts():
    p = runner.build_prompt(FR, output_path="/x/output.json", scratch_dir="/x/scratch")
    assert p.startswith("# Grading a replay episode") and "# sdh-field-resolution" in p
    assert "/x/output.json" in p and "/x/scratch" in p and "{OUTPUT_PATH}" not in p and "{SCRATCH_DIR}" not in p
    assert "submit_output" in p and "nb summary" in p


def test_unknown_grader_is_an_error():
    with pytest.raises(runner.GradeError):
        runner.build_prompt("no-such-grader", output_path="/x", scratch_dir="/y")


def _episode(tmp_path: Path, name: str, *, claude_dir: bool = False, image: str | None = None) -> Path:
    ep = tmp_path / name
    (ep / "session").mkdir(parents=True)
    card = QC0426 / "device_card.md"
    (ep / "session" / "device_card.md").write_text(card.read_text() if card.exists() else "# QC0426\n")
    if claude_dir:
        (ep / "session" / ".claude").mkdir()
    if image:
        (ep / "episode.json").write_text(json.dumps({"run": {"image": {"tag": image, "id": "sha256:x"}}}))
    return ep


def _job(ep: Path, **kw) -> runner.Job:
    base = dict(episode_dir=ep, grader=FR, run_dir=ep / "grades" / FR / "s", name="hera-grade-s-000", image="hera-agent:abc-none",
                model="claude-opus-5", effort="medium", max_turns=40, timeout_s=900.0, stall_s=300.0)
    return runner.Job(**{**base, **kw})


def test_run_args_is_the_locked_down_layout(tmp_path):
    ep = _episode(tmp_path, "ep", claude_dir=True)
    args = runner.run_args(_job(ep), {"CLAUDE_CODE_OAUTH_TOKEN": "tok"})
    session = ep / "session"
    assert args[:3] == ["docker", "run", "--rm"] and "--network" not in args
    assert f"{session}:/episode:ro" in args
    assert "--user" in args and "-w" in args and args[args.index("-w") + 1] == "/episode"
    assert f"{runner.GRADING_SRC}:{runner.C_GRADING}:ro" in args        # over the image's own path
    assert f"{runner.GRADERS_ROOT}:/hera-graders:ro" in args
    assert f"{ep / 'grades' / FR / 's'}:/grade-run" in args
    assert "type=tmpfs,destination=/episode/.claude,readonly" in args    # the stop hook is masked
    assert "-e" in args and "HOME=/home/hera" in args and "CLAUDE_CODE_OAUTH_TOKEN=tok" in args
    assert "HERA_FAKETIME" not in " ".join(args)
    i = args.index("claude")
    assert args[i:i + 5] == ["claude", "-p", "--model", "claude-opus-5", "--effort"]
    assert args[-2] == "--allowedTools" and args[-1].startswith("Read,")
    # no .claude in the session -> no mask, since the mountpoint would not exist
    ep2 = _episode(tmp_path, "ep2")
    assert not any("destination=/episode/.claude" in a for a in runner.run_args(_job(ep2), {}))


def test_make_jobs_image_comes_from_the_episode_unless_overridden(tmp_path, monkeypatch):
    with_image = _episode(tmp_path, "a", image="hera-agent:8bf4e7d-full")
    fixture = _episode(tmp_path, "b")
    monkeypatch.delenv(runner.IMAGE_ENV, raising=False)
    jobs = runner.make_jobs([with_image], FR, n=2, stamp="S")
    assert [j.image for j in jobs] == ["hera-agent:8bf4e7d-full"] * 2
    assert [j.run_dir.name for j in jobs] == ["S-00", "S-01"] and [j.name for j in jobs] == ["hera-grade-S-000", "hera-grade-S-001"]
    with pytest.raises(runner.GradeError, match="--image"):
        runner.make_jobs([fixture], FR)
    assert runner.make_jobs([fixture, with_image], FR, image="hera-agent:x-none", stamp="T")[1].image == "hera-agent:x-none"
    monkeypatch.setenv(runner.IMAGE_ENV, "hera-agent:env-none")
    assert runner.make_jobs([fixture], FR, stamp="U")[0].image == "hera-agent:env-none"
    (fixture / "grades" / FR / "V").mkdir(parents=True)
    with pytest.raises(runner.GradeError, match="run dir exists"):
        runner.make_jobs([fixture], FR, stamp="V")
    with pytest.raises(runner.GradeError, match="not an episode dir"):
        runner.make_jobs([tmp_path / "nope"], FR, image="x")
    with pytest.raises(runner.GradeError, match="effort"):
        runner.make_jobs([fixture], FR, image="x", effort="turbo")


@pytest.fixture
def fake_docker(monkeypatch):
    """No docker: the image resolves, the credential is a fake token, and `stream_claude`
    is a scripted extractor keyed on the container name."""
    calls = {"removed": [], "stopped": [], "scripts": {}}
    monkeypatch.setattr(runner.container, "credential_env", lambda: {"CLAUDE_CODE_OAUTH_TOKEN": "sekrit"})
    monkeypatch.setattr(runner, "resolve_image", lambda tag: {"tag": tag, "id": "sha256:abc"})
    monkeypatch.setattr(runner.container, "image_metadata", lambda tag: {"corpus_sha": "abc"})
    monkeypatch.setattr(runner.container, "remove_container", lambda name: calls["removed"].append(name))
    monkeypatch.setattr(runner.container, "stop_container", lambda name: calls["stopped"].append(name))

    def stream(cmd, prompt, transcript, stderr, *, timeout_s, stall_s, on_guard, on_event=None, stop=None):
        name = cmd[cmd.index("--name") + 1]
        run_dir = Path(next(a for a in cmd if a.endswith(":/grade-run")).rsplit(":", 1)[0])
        assert "sekrit" in " ".join(cmd) and "# Grading a replay episode" in prompt
        return calls["scripts"][name](run_dir, on_guard)
    monkeypatch.setattr(runner.container, "stream_claude", stream)
    return calls


def _ok(doc):
    def script(run_dir, on_guard):
        (run_dir / "output.json").write_text(json.dumps(doc))
        (run_dir / "accepted").write_text("accepted\n")
        events = [{"type": "system", "subtype": "init", "claude_code_version": "2.1.273"},
                  {"type": "result", "is_error": False, "total_cost_usd": 0.45, "num_turns": 8, "modelUsage": {"claude-opus-5": {}}}]
        return {"events": events, "returncode": 0, "guard": None, "wall_s": 50.0}
    return script


def test_grade_many_scores_each_job_and_isolates_failures(tmp_path, fake_docker):
    if not QC0426.exists():
        pytest.skip("QC0426 archive not present")
    a, b, c, d = (_episode(tmp_path, n) for n in "abcd")
    jobs = runner.make_jobs([a, b, c, d], FR, image="hera-agent:abc-none", stamp="S")

    def boom(run_dir, on_guard):
        raise RuntimeError("docker fell over holding sekrit")

    def timeout(run_dir, on_guard):
        on_guard("timeout")
        return {"events": [], "returncode": 137, "guard": "timeout", "wall_s": 900.0}

    def rate_limited(run_dir, on_guard):
        return {"events": [{"type": "result", "is_error": True, "result": "Rate limit reached for this hour"}],
                "returncode": 1, "guard": None, "wall_s": 3.0}
    fake_docker["scripts"] = dict(zip([j.name for j in jobs], [_ok(REF43), boom, timeout, rate_limited]))
    recs = runner.grade_many(jobs, parallel=3)
    assert [r["claude"]["exit"] for r in recs] == ["ok", "harness_error", "timeout", "quota"]
    assert recs[0]["scores"]["status"] == "graded" and recs[0]["scores"]["ok"] is True and recs[0]["accepted"]
    assert recs[0]["claude"]["cost_usd"] == 0.45 and recs[0]["claude"]["version"] == "2.1.273"
    assert recs[0]["image"] == {"tag": "hera-agent:abc-none", "id": "sha256:abc", "metadata": {"corpus_sha": "abc"}}
    assert recs[0]["episode_image"] is None
    assert recs[0]["grading"]["code_hash"] and "CLAUDE_CODE_OAUTH_TOKEN=<redacted>" in recs[0]["docker"]
    assert "sekrit" not in json.dumps(recs)
    assert recs[1]["scores"]["status"] == "no_output" and "docker fell over" in recs[1]["claude"]["error"]
    assert recs[2]["scores"]["status"] == "no_output" and recs[3]["scores"]["status"] == "no_output"
    assert recs[3]["claude"]["quota"]["category"] == "rate_limit" and recs[0]["claude"]["quota"] is None
    assert fake_docker["stopped"] == [jobs[2].name] and sorted(fake_docker["removed"]) == sorted(j.name for j in jobs)
    for j in jobs:                       # every job leaves a record on disk, whatever happened
        rec = json.loads((j.run_dir / "run.json").read_text())
        assert rec["container"] == j.name and (j.run_dir / "scores.json").exists() and (j.run_dir / "prompt.md").exists()
    assert (jobs[0].run_dir / "bin" / "submit_output").read_text().startswith("#!/bin/sh")


def test_summarize_groups_by_episode_and_reports_agreement(tmp_path, fake_docker):
    if not QC0426.exists():
        pytest.skip("QC0426 archive not present")
    ep = _episode(tmp_path, "ep")
    jobs = runner.make_jobs([ep], FR, n=3, image="hera-agent:abc-none", stamp="S")
    fake_docker["scripts"] = {jobs[0].name: _ok(REF43), jobs[1].name: _ok(REF43), jobs[2].name: _ok({**REF43, "n_points": 51})}
    out = runner.summarize(runner.grade_many(jobs, parallel=1))
    assert out.count("graded") == 3 and "agreement: 2/3" in out and "3 extractions, $1.35" in out


def test_summarize_flags_a_tag_that_moved_since_the_episode(tmp_path, fake_docker):
    if not QC0426.exists():
        pytest.skip("QC0426 archive not present")
    ep = _episode(tmp_path, "ep", image="hera-agent:abc-none")
    (ep / "episode.json").write_text(json.dumps({"run": {"image": {"tag": "hera-agent:abc-none", "id": "sha256:old"}}}))
    jobs = runner.make_jobs([ep], FR, stamp="S")
    fake_docker["scripts"] = {jobs[0].name: _ok(REF43)}
    recs = runner.grade_many(jobs, parallel=1)
    assert recs[0]["episode_image"] == {"tag": "hera-agent:abc-none", "id": "sha256:old"}
    assert "the episode ran in sha256:old" in runner.summarize(recs)


# ---------------------------------------------------------------- hera-replay grade
def test_replay_grade_walks_finished_episodes_with_the_case_grader(tmp_path, fake_docker, capsys):
    if not QC0426.exists():
        pytest.skip("QC0426 archive not present")
    from hera.replay import main as replay_main
    from hera.replay.errors import CutError
    from hera.replay.grade import grade_run
    rd = tmp_path / "run"
    (rd / "episodes").mkdir(parents=True)
    (rd / "run.json").write_text(json.dumps({"case": {"case": "c", "grader": FR}}))
    for sid, finished in (("00", True), ("01", True), ("02", False)):
        ep = _episode(rd / "episodes", sid, claude_dir=True)
        ep.joinpath("episode.json").write_text(json.dumps(
            {"run": {"image": {"tag": "hera-agent:abc-full", "id": "sha256:abc"}}} if finished else {}))
    jobs_seen = {}

    def script_for(name):
        def script(run_dir, on_guard):
            jobs_seen[name] = run_dir
            return _ok(REF43)(run_dir, on_guard)
        return script
    fake_docker["scripts"] = {f"hera-grade-S-{i:03d}": script_for(f"hera-grade-S-{i:03d}") for i in range(2)}
    recs = grade_run(rd, stamp="S")
    assert len(recs) == 2 and all(r["scores"]["status"] == "graded" for r in recs)
    assert sorted(p.parent.parent.parent.name for p in jobs_seen.values()) == ["00", "01"]   # 02 never finished
    rows = list(csv.DictReader((rd / "grades.csv").open()))
    assert [r["sample"] for r in rows] == ["00", "01"] and rows[0]["status"] == "graded" and rows[0]["ok"] == "True"
    # the case's grader is required unless overridden
    (rd / "run.json").write_text(json.dumps({"case": {"case": "c", "grader": None}}))
    with pytest.raises(CutError, match="names no grader"):
        grade_run(rd, stamp="T")
    with pytest.raises(SystemExit, match="no run.json"):
        replay_main(["grade", str(tmp_path)])
