"""Headless tests for the QCS heater panel (QT_QPA_PLATFORM=offscreen).

The panel's contract: controls unlock only while the worker runs, lamps/state
come from [data] readback only, command results (incl. rejections) are shown,
and commands go out as name-addressed JSON lines.
"""

import json
import os

# Hard-set, not setdefault — see test_qt_launcher.py.
os.environ["QT_QPA_PLATFORM"] = "offscreen"

import pytest
from PyQt5 import QtWidgets

from core.config import (
    InfluxConfig,
    ToploaderConfig,
    ToploaderHardware,
)
from drivers.leiden_qcs import LeidenQcs
from gui.qt.qcs_panel import CHANNEL_NAMES, QcsHeaterPanel
from workers.qcs_heater import SIM_MAP, _SimIO, data_payload, handle_command


@pytest.fixture(scope="session")
def app():
    return QtWidgets.QApplication.instance() or QtWidgets.QApplication([])


class _FakeLauncher:
    @staticmethod
    def dispatch(cb):
        cb()


def _config():
    return ToploaderConfig(
        influxdb=InfluxConfig(url="http://localhost:9", token="t", org="o", bucket="b"),
        health={},  # no pollers -> no threads/network in tests
        hardware=ToploaderHardware(
            avs_fridge_gpib="x", avs_probe_gpib="x", ami430_addr="x",
            lc_logs_folder="/tmp", temperature_log_dir="/tmp",
            qcs_board_num=0,
        ),
    )


@pytest.fixture
def panel(app):
    p = QcsHeaterPanel(
        _FakeLauncher(), title="QCS Heaters", tag="qcs",
        cmd=["true"], health_key="qcs", health_measurement="QCS",
        status_name="QCS", config=_config(),
    )
    yield p
    p.shutdown()


def _sim_payload(commands=()):
    """Real worker payload from the sim stack, after running *commands*."""
    qcs = LeidenQcs(_SimIO(), SIM_MAP, {})
    last = None
    for c in commands:
        last = handle_command(qcs, json.dumps(c))
    return json.dumps(data_payload(qcs, last))


def _row(panel, name):
    return panel._rows[name]


def test_controls_locked_until_ready(panel):
    assert all(not _row(panel, n)["spin"].isEnabled() for n in CHANNEL_NAMES)
    panel._on_ready()
    assert all(_row(panel, n)["spin"].isEnabled() for n in CHANNEL_NAMES)
    for n in CHANNEL_NAMES:
        assert all(b.isEnabled() for b in _row(panel, n)["buttons"])
    panel._on_died(1)
    assert all(not _row(panel, n)["spin"].isEnabled() for n in CHANNEL_NAMES)


def test_lamps_follow_readback(panel):
    panel._on_ready()
    panel._on_data(_sim_payload([
        {"cmd": "set_current", "channel": "MC", "ua": 250},
        {"cmd": "set_on", "channel": "MC", "on": True},
    ]))
    mc = _row(panel, "MC")
    assert "orange" in mc["lamp"].styleSheet()
    assert "ON" in mc["now"].text() and "250" in mc["now"].text()
    still = _row(panel, "Still")
    assert "gray" in still["lamp"].styleSheet()
    assert "?" in still["now"].text()  # untouched: readback honestly unknown


def test_unknown_setpoint_shown_honestly(panel):
    panel._on_ready()
    panel._on_data(_sim_payload())
    assert "?" in _row(panel, "MC")["now"].text()  # DAC not readable at start


def test_command_rejection_surfaces_red(panel):
    panel._on_ready()
    panel._on_data(_sim_payload([
        {"cmd": "set_current", "channel": "Nope", "ua": 10},
    ]))
    assert not panel._cmd_result.isHidden()
    assert "red" in panel._cmd_result.styleSheet()


def test_clamped_command_surfaces_detail(panel):
    panel._on_ready()
    panel._on_data(_sim_payload([
        {"cmd": "set_current", "channel": "MC", "ua": 99999},
    ]))
    assert not panel._cmd_result.isHidden()
    assert "clamped" in panel._cmd_result.text()
    assert "red" not in panel._cmd_result.styleSheet()


def test_apply_sends_name_addressed_json(panel, monkeypatch):
    sent = []
    monkeypatch.setattr(panel._proc, "send_line", lambda s: (sent.append(s), True)[1])
    panel._on_ready()
    _row(panel, "Still")["spin"].setValue(1200)
    panel._apply("Still")
    panel._set_on("3K", False)
    assert json.loads(sent[0]) == {"cmd": "set_current", "channel": "Still", "ua": 1200}
    assert json.loads(sent[1]) == {"cmd": "set_on", "channel": "3K", "on": False}


def test_send_failure_reports_not_raises(panel, monkeypatch):
    monkeypatch.setattr(panel._proc, "send_line", lambda s: False)
    panel._on_ready()
    panel._apply("MC")
    assert not panel._cmd_result.isHidden()
    assert "not running" in panel._cmd_result.text()


def test_reset_clears_readback_display(panel):
    panel._on_ready()
    panel._on_data(_sim_payload([{"cmd": "set_on", "channel": "MC", "on": True}]))
    panel._on_died(1)
    mc = _row(panel, "MC")
    assert mc["now"].text() == "—"
    assert "gray" in mc["lamp"].styleSheet()
    assert panel._cmd_result.isHidden()
