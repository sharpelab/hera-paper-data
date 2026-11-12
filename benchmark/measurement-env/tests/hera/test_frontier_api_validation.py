from __future__ import annotations

import sys
from pathlib import Path

import pytest

FRONTIER = Path(__file__).resolve().parents[2] / "hera/evaluations/frontier"
sys.path.insert(0, str(FRONTIER))

import stubs  # noqa: E402

FIXTURE = "qc0426_handbuilt"  # hand-built QC0426 rig: fast, rig-agnostic API probes


def test_real_measureme_call_and_notebook_bindings_execute_offline():
    result = stubs.run_cell(
        """
s = async_station(meas_config)
s.add_comment("sdh-spot-check")
s.fp(sr1.X)
s.plot(magnet.mag, sr1.X)
s.ramp(k_bg.volt, -1.0)
s.ramp(dc205_volt, -1.0)
s.sweep(magnet.mag, np.linspace(0, 4, 101), delay=1.0)
""",
        fixture=FIXTURE,
    )

    assert result["status"] == "executed"
    assert [event["op"] for event in result["log"]] == ["set", "set", "sweep"]
    assert result["log"][-1]["params"] == ["magnet.mag"]


@pytest.mark.parametrize(
    ("source", "error"),
    [
        ("s = async_station(meas_config)\ns.runnow()", "no attribute 'runnow'"),
        ("magnet.fake_api(1)", "no attribute 'fake_api'"),
        (
            "s = async_station(meas_config)\ns.sweep(magnet.mag, [0, 1], bogus=True)",
            "unexpected keyword argument 'bogus'",
        ),
        ("dc205.ramp_voltage(1, rate=2)", "unexpected keyword argument 'rate'"),
        ("from sweep.station import field_invB", "No module named 'sweep.station'"),
    ],
)
def test_nonexistent_or_invalid_apis_fail_and_are_repairable(source, error):
    result = stubs.run_cell(source, fixture=FIXTURE)

    assert result["status"] == "unexecutable"
    assert error in result["error"]
    assert result["repairable"] is True


def test_real_unadapted_api_is_a_signature_checked_hardware_free_mock():
    valid = stubs.run_cell("s = async_station(meas_config)\ns.watch(delay=1)", fixture=FIXTURE)
    invalid = stubs.run_cell("s = async_station(meas_config)\ns.watch(bogus=True)", fixture=FIXTURE)

    assert valid["status"] == "executed"
    assert valid["log"] == []
    assert invalid["status"] == "unexecutable"
    assert "unexpected keyword argument 'bogus'" in invalid["error"]
    assert invalid["repairable"] is True


def test_worker_allows_real_pure_stdlib_used_by_measurement_cells():
    result = stubs.run_cell("import json\nprint(json.dumps({'ok': True}))", fixture=FIXTURE)

    assert result["status"] == "executed"
    assert result["stdout"].strip() == '{"ok": true}'


def test_worker_allows_normal_imports_while_os_sandbox_blocks_network_and_devices():
    for module in ("socket", "pyvisa"):
        result = stubs.run_cell(f"import {module}", fixture=FIXTURE)
        assert result["status"] == "executed"

