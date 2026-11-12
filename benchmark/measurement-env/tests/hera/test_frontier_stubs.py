"""The frontier validator: real venv + faked instruments, isolated by bubblewrap.

Runs the frozen QC0426 reference cells and a set of invented-API / limit /
isolation probes through stubs.run_cell and grade.grade_cell.
"""
from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

import pytest

FRONTIER = Path(__file__).resolve().parents[2] / "hera/evaluations/frontier"
SESSION = Path.home() / "sandbox/sharpelab/measurement-env/hera/docs/notes/2026-06-19-QC0426-session-3"
sys.path.insert(0, str(FRONTIER))

import grade  # noqa: E402
import stubs  # noqa: E402

pytestmark = pytest.mark.skipif(shutil.which("bwrap") is None, reason="bubblewrap not installed")

CAL = {"c_tg_F_per_m2": 1.7027e-3, "c_bg_F_per_m2": 2.2004e-3, "n_offset_cm2": -1.581e11,
       "top_gate_params": ["dc205_volt", "DC_bias", "dc205.voltage", "dc205.volt", "k_tg.volt"],
       "back_gate_params": ["k_2400.volt", "k_bg.volt"], "magnet_params": ["magnet.mag", "magnet.field"]}


def reference_cell(index: int) -> str:
    if not SESSION.exists():
        pytest.skip("frozen QC0426 session not on this machine")
    nb = json.loads((SESSION / "20260619_measure.ipynb").read_text())
    return "".join(nb["cells"][index]["source"])


FIXTURE = "qc0426_handbuilt"  # fixtures/qc0426_handbuilt.py: the hand-built rig for rig-agnostic worker probes


def run(src: str, **kw) -> dict:
    return stubs.run_cell(src, cwd=SESSION if SESSION.exists() else None, fixture=FIXTURE, **kw)


# ---------------------------------------------------------------- worker probes (hand-built fixture)
def test_own_assert_is_recorded_and_the_cell_is_graded_anyway():
    r = run("assert abs(magnet.mag() - 4) < 0.1, 'not at 4 T'\ns = async_station(meas_config)\n"
            "s.ramp(k_bg.volt, -1.0); s.sweep(magnet.mag, np.linspace(0, 1, 5), delay=1)")
    assert r["status"] == "unexecutable" and r["own_assert"].startswith("AssertionError: not at 4 T")
    assert r["log"] == []  # the run as written stopped at the assert
    assert r["assert_free"]["status"] == "executed"
    assert [e["op"] for e in r["assert_free"]["log"]] == ["set", "sweep"]
    r = run("assert True\nk_bg.volt(7e14)")  # a real rig limit still fails, assert or not
    assert r["status"] == "unexecutable" and r["repairable"] is True


# ---------------------------------------------------------------- real python, faked rig
def test_real_imports_open_and_sleep_work():
    r = run("import json, time\nfrom scipy.optimize import curve_fit\n"
            "from sharpelab_nb.gates import calc_gate_voltages\nfrom hera.analysis import field_invB\n"
            "import sweep.raster, sweep.db\n"
            "txt = open('hera_session.md').read() if __import__('os').path.exists('hera_session.md') else 'x'\n"
            "time.sleep(600); interruptible_sleep(600)\n"
            "vt, vb = calc_gate_voltages(-5.0, 0.0, 1.7027e-3, 2.2004e-3, n_offset=-0.1581)\n"
            "s = async_station(meas_config); s.ramp(k_bg.volt, vb); s.ramp(dc205_volt, vt)\n"
            "s.sweep(magnet.mag, field_invB(0.3, 4.0, 300), delay=1)\nprint(round(float(vt), 3))")
    assert r["status"] == "executed", r["error"]
    assert r["stdout"].strip().endswith("-2.278")
    assert [e["op"] for e in r["log"]] == ["set", "set", "sweep"]
    assert len(r["log"][-1]["vectors"][0]) == 300


def test_plot_accepts_any_string_axis_like_the_real_plotter():
    r = run("s = async_station(meas_config)\ns.plot('B_field', sr1.X); s.plot('time', k_2400.curr); s.plot(magnet.mag, [sr1.X, sr2.X])\n"
            "s.sweep(magnet.mag, np.linspace(0, 1, 3), delay=0.1)")
    assert r["status"] == "executed", r["error"]


def test_agent_defined_qcodes_parameters_are_accepted_and_attributed():
    r = run("B_meas = qcodes.Parameter('B_meas', unit='T', get_cmd=magnet.mag)\n"
            "B_set = qcodes.Parameter('B_set', unit='T', get_cmd=magnet.mag, set_cmd=magnet.mag)\n"
            "s = async_station(meas_config); s.fp(B_meas); s.plot(B_meas, sr1.X)\n"
            "s.ramp(k_bg.volt, -1.0)\ns.sweep(B_set, np.linspace(0, 1, 5), delay=0.1)")
    assert r["status"] == "executed", r["error"]
    ev = r["log"][-1]
    assert ev["op"] == "sweep" and ev["params"] == ["magnet.mag"] and len(ev["vectors"][0]) == 5
    r = run("B_ro = qcodes.Parameter('B_ro', get_cmd=magnet.mag)\ns = async_station(meas_config)\n"
            "s.sweep(B_ro, np.linspace(0, 1, 5), delay=0.1)")
    assert r["status"] == "unexecutable"  # read-only wrapper cannot be swept, on the rig either


def test_from_sweep_import_and_megasweep_record_axes():
    r = run("from sweep import AsyncStation\ns = AsyncStation(meas_config)\n"
            "s.megasweep(k_bg.volt, np.linspace(-1, 1, 3), dc205_volt, np.linspace(-1, 1, 5), slow_delay=1, fast_delay=0.5)")
    assert r["status"] == "executed", r["error"]
    ev = r["log"][-1]
    assert ev["op"] == "megasweep" and ev["slow_params"] == ["k_2400.volt"] and ev["fast_params"] == ["dc205_volt"]
    assert ev["kwargs"] == {"slow_delay": 1.0, "fast_delay": 0.5}


@pytest.mark.parametrize("src, needle", [
    ("s = async_station(meas_config)\ns.runnow()", "no attribute 'runnow'"),
    ("s = sweep.AsyncStation(meas_config)\ns.sweep(magnet.mag, np.linspace(0, 1, 11), 1.0, 2.0)", "TypeError"),
    ("s = sweep.AsyncStation(meas_config, 1, 2, 3, 4)", "TypeError"),
    ("from sharpelab_nb.gates import GateCalibration", "cannot import name 'GateCalibration'"),
    ("cal.calc_gate_voltages(1, 2)", "no attribute 'calc_gate_voltages'"),
    ("x = 3 × 4", "SyntaxError"),
    ("undefined_helper(1)", "NameError"),
])
def test_invented_api_is_unexecutable_and_repairable(src, needle):
    r = run(src)
    assert r["status"] == "unexecutable"
    assert needle in r["error"], r["error"]
    assert r["repairable"] is True


@pytest.mark.parametrize("src, needle", [
    ("SR830('x', 'GPIB0::1::INSTR')", "already constructed"),
    ("raise SystemExit(0)", "SystemExit"),
    ("np.linspace(0, 1, 2.5)", "cannot be interpreted as an integer"),
])
def test_any_cell_exception_is_unexecutable_and_repairable(src, needle):
    # everything the operator would see in a traceback is pasted back; only worker failures are final
    r = run(src)
    assert r["status"] == "unexecutable"
    assert needle in r["error"], r["error"]
    assert r["repairable"] is True


@pytest.mark.parametrize("imp", ["from drivers.async_station import async_station", "from drivers import async_station"])
def test_legacy_async_station_import_from_frozen_notebook_resolves(imp):
    r = run(f"{imp}\ns = async_station(meas_config)\ns.sweep(magnet.mag, np.linspace(0, 1, 3), delay=0.1)")
    assert r["status"] == "executed", r["error"]
    assert r["log"][-1]["params"] == ["magnet.mag"]


# ---------------------------------------------------------------- isolation
def test_worker_has_no_network_and_readonly_cwd():
    r = run("import socket\n"
            "try:\n    socket.create_connection(('1.1.1.1', 53), timeout=2); print('NET OK')\n"
            "except OSError:\n    print('blocked')\n"
            "try:\n    open('should_fail.txt', 'w').write('x'); print('WROTE')\n"
            "except OSError:\n    print('readonly')")
    assert r["status"] == "executed", r["error"]
    assert "blocked" in r["stdout"] and "readonly" in r["stdout"]
    assert not (SESSION / "should_fail.txt").exists()


def test_runaway_cell_is_killed_by_timeout():
    r = stubs.run_cell("while True:\n    pass", timeout_s=5, fixture=FIXTURE)
    assert r["status"] == "unexecutable" and "ValidationWorkerError" in r["error"]


def test_gate_parking_after_the_sweep_does_not_change_the_graded_density():
    r = run("s = async_station(meas_config)\ns.ramp(k_bg.volt, -1.763); s.ramp(dc205_volt, -2.278)\n"
            "s.sweep(magnet.mag, np.linspace(0, 4, 501), delay=1)\n"
            "k_bg.volt(0.0); dc205_volt(0.0); s.ramp(k_bg.volt, 0.0)")
    ex = grade.extract(r["log"], CAL)
    assert ex["V_tg"] == pytest.approx(-2.278) and ex["V_bg"] == pytest.approx(-1.763)
    assert ex["n_cm2"][0] == pytest.approx(-5e12, rel=1e-3)


# ---------------------------------------------------------------- notebook-built namespace (fakerig)
def _setup_cells(cut: int) -> list[str]:
    if not SESSION.exists():
        pytest.skip("frozen QC0426 session not on this machine")
    nb = json.loads((SESSION / "20260619_measure.ipynb").read_text())
    return ["".join(c["source"]) for c in nb["cells"][: cut + 1] if c["cell_type"] == "code"]


RIG = {"drive": "sr1.amplitude", "bias_resistor": 100e6,
       "channels": {"sr0": {"gain": -1e6}, "sr1": {"R": 60.0}, "sr2": {"R": 60.0}, "sr3": {"R": 0.5}},
       "readings": {"l335_3.sample_temperature": 1.17, "k_2400.curr": 1e-11, "k_2410.curr": 1e-11},
       "defaults": {"sr1.amplitude": 2.0}, "compat": {"magnet.mag": "magnet.field"}}


def test_fakerig_builds_the_notebook_namespace_with_real_driver_classes():
    g = grade.grade_cell(reference_cell(43), CAL, cwd=SESSION, setup=_setup_cells(41), rig=RIG)
    assert g["status"] == "graded" and g["ok"] is True, g.get("exec_error")
    assert g["n_cm2"][0] == pytest.approx(-5e12, rel=1e-6) and g["B_rows"] == 501
    rig = g["rig"]
    assert rig["setup_cells"] == 23
    assert rig["instruments"] == {"magnet": "FastBi1K5", "l335_3": "Lakeshore_335", "sr0": "SR830", "sr1": "SR830",
                                  "sr2": "SR830", "sr3": "SR830", "k_2400": "Keithley_2400", "k_2410": "Keithley_2400",
                                  "dc205": "SRS_DC205", "qswitch": "QSwitch"}
    assert rig["aliases"] == ["magnet.mag -> magnet.field"]
    assert rig["setup_errors"] == []
    # the notebook's own end state is the frontier state: gates parked, magnet at 0
    assert rig["state_after_setup"] == {"magnet.field": 0.0, "k_2400.volt": 0.0, "k_2410.volt": 0.0, "dc205.voltage": 0.0}


def test_fakerig_reference_fan_and_electron_spot_check():
    g = grade.grade_cell(reference_cell(47), CAL, cwd=SESSION, setup=_setup_cells(41), rig=RIG)
    assert g["status"] == "graded" and g["ok"] is True and g["kind"] == "fan" and g["n_columns"] == 41
    g = grade.grade_cell(reference_cell(45), CAL, cwd=SESSION, setup=_setup_cells(41), rig=RIG)
    assert g["status"] == "graded" and g["ok"] is True and g["own_assert"].startswith("AssertionError")


def test_fakerig_real_driver_internals_and_readings_follow_the_drive():
    src = ("SENS = sorted(type(sr0)._VOLT_TO_N)            # real SR830 class constant\n"
           "sr1.input_config('a-b'); assert sr1.input_config() == 'a-b'\n"
           "assert abs(sr0.X()/abs(meas_config['sr0_gain']) - 20e-9) < 1e-12   # 2 V / 100 MOhm\n"
           "sr1.amplitude(0.5); assert abs(sr1.X() - 60*5e-9) < 1e-15\n"
           "print(magnet._status()['output_enabled'], heater.sample_temperature(), len(SENS))\n"
           "s = async_station(meas_config); s.ramp(k_bg.volt, -1.0); s.ramp(dc205_volt, -2.0)\n"
           "s.sweep(magnet.mag, np.linspace(0, 1, 11), delay=1)")
    r = stubs.run_cell(src, cwd=SESSION, setup_cells=_setup_cells(41), rig=RIG)
    assert r["status"] == "executed", r["error"]
    assert r["stdout"].strip().endswith("True 1.17 27")
    ex = grade.extract(r["log"], CAL)
    assert ex["V_bg"] == -1.0 and ex["V_tg"] == pytest.approx(-2.0) and ex["B_T"].size == 11


def test_fakerig_rig_limits_still_apply():
    r = stubs.run_cell("k_bg.volt(10.0)", cwd=SESSION, setup_cells=_setup_cells(41), rig=RIG)
    assert r["status"] == "unexecutable" and "must be between -4.5 and 4.5" in r["error"]
    r = stubs.run_cell("magnet.mag(9.0)", cwd=SESSION, setup_cells=_setup_cells(41), rig=RIG)
    assert r["status"] == "unexecutable" and "must be between -8" in r["error"]


# ---------------------------------------------------------------- vti frontiers (need the titan mount)
VTI = Path(os.environ.get("HERA_TITAN", str(Path.home() / "mnt_titan/measurements"))) / "vti/zack"
FRONTIER_DIR = Path(__file__).resolve().parents[2] / "hera/evaluations/frontier"


def _vti_case(session: str, nb: str, cut: int, ref: int, exp_yaml: str):
    if not (VTI / session / nb).exists():
        pytest.skip("titan measurements mount not available")
    import yaml
    exp = yaml.safe_load((FRONTIER_DIR / "experiments" / exp_yaml).read_text())
    cells = json.loads((VTI / session / nb).read_text(encoding="utf-8"))["cells"]
    setup = ["".join(c["source"]) for c in cells[: cut + 1] if c["cell_type"] == "code"]
    return "".join(cells[ref]["source"]), setup, exp


def test_fakerig_vti01_reference_spot_check_passes():
    src, setup, exp = _vti_case("20260818-vti-01", "20260818_measure.ipynb", 47, 49, "vti01-sdh-m47.yaml")
    g = grade.grade_cell(src, exp["calibration"], cwd=VTI / "20260818-vti-01", setup=setup, rig=exp["rig"])
    assert g["status"] == "graded" and g["ok"] is True, g.get("exec_error")
    assert g["n_cm2"][0] == pytest.approx(-1.8e12, rel=1e-6) and g["B_rows"] == 746 and g["B_range_T"] == [0.8, 9.0]
    assert set(g["rig"]["instruments"]) >= {"magnet", "l335_3", "sr0", "sr1", "sr2", "sr3", "k_2400_tg", "k_2400_bg", "dc205", "ami_he"}
    assert g["rig"]["setup_errors"] == []


def test_fakerig_vti02_reference_spot_check_passes():
    src, setup, exp = _vti_case("20260821-vti-02", "20260821_measure.ipynb", 39, 41, "vti02-sdh-m39.yaml")
    g = grade.grade_cell(src, exp["calibration"], cwd=VTI / "20260821-vti-02", setup=setup, rig=exp["rig"])
    assert g["status"] == "graded" and g["ok"] is True, g.get("exec_error")
    assert g["n_cm2"][0] == pytest.approx(3.0e12, rel=1e-6) and g["B_rows"] == 417
    # faithful to the real session: notebook cell 35 raised this exact RuntimeError on the rig
    # (rangei reads back 1.05e-6) and the operator re-ran with rangei=1.05e-6 in cell 37
    errs = g["rig"]["setup_errors"]
    assert len(errs) == 1 and "rangei = 1.05e-06 (want 1e-06)" in errs[0]["error"]


# ---------------------------------------------------------------- zf1 toploader frontier + SC-arc grader
ZF1 = Path(__file__).resolve().parents[2] / "hera/docs/notes/2026-06-22-zf1-session"


def test_fakerig_zf1_reference_survey_gatemap_passes_the_sc_cut_grader():
    if not (ZF1 / "20260622_measure.ipynb").exists():
        pytest.skip("zf1 session archive not present")
    import yaml
    exp = yaml.safe_load((FRONTIER_DIR / "experiments/zf1-sc-s3-m29.yaml").read_text())
    cells = json.loads((ZF1 / "20260622_measure.ipynb").read_text(encoding="utf-8"))["cells"]
    setup = ["".join(c["source"]) for c in cells[:30] if c["cell_type"] == "code"]
    g = grade.grade_cell("".join(cells[31]["source"]), exp["calibration"], cwd=ZF1, setup=setup, rig=exp["rig"],
                         grader=exp["grader"], exp=exp)
    assert g["status"] == "graded" and g["ok"] is True, g.get("exec_error")
    assert g["grader"] == "sc_cut" and g["gate_points"] == 105 * 83 and g["gate_points_inside"] == 9  # = archived run 2
    assert g["rig"]["instruments"]["magnet"] == "AMIModel430" and len(g["rig"]["instruments"]) == 14
