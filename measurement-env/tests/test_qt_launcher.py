"""Headless smoke tests for the Qt VTI launcher (QT_QPA_PLATFORM=offscreen).

Covers what CI can cover without a display or hardware: construction + tick,
status tiers, close-to-tray vs close-quits, the single-instance socket, and
the JupyterLab launch command (the venv-pinning gotcha). Tray/visibility
behavior on a real desktop stays on the manual test matrix in
docs/plans/LAUNCHER_QT_PLAN.md.
"""

import os
import sys

# Hard-set, not setdefault: a desktop session exporting QT_QPA_PLATFORM
# (e.g. "wayland") would otherwise put these tests on the real display —
# flashing windows and tray icons every run. Tests are headless, always.
os.environ["QT_QPA_PLATFORM"] = "offscreen"

import pytest
from PyQt5 import QtWidgets

from core.config import InfluxConfig, PinkConfig, PinkHardware, VtiConfig, VtiHardware
from gui.qt import base_launcher, jupyter_panel
from gui.qt.pink_launcher import PinkLauncher
from gui.qt.vti_launcher import VtiLauncher
from gui.utils import ComponentStatus


@pytest.fixture(scope="session")
def app():
    return QtWidgets.QApplication.instance() or QtWidgets.QApplication([])


def _fake_config():
    return VtiConfig(
        influxdb=InfluxConfig(url="http://localhost:9", token="t", org="o", bucket="b"),
        health={},  # no pollers -> no threads/network in tests
        hardware=VtiHardware(
            lakeshore_gpib="GPIB0::10::INSTR",
            temperature_log_dir="/tmp",
            ami1700_addr="x", terranova_addr="x",
            lakeshore218_gpib="x", fastbi_host="x",
        ),
    )


class _TestableLauncher(VtiLauncher):
    def _load_config(self):
        return _fake_config()


class _StubTray:
    def __init__(self):
        self.messages = []
        self.tooltip = ""
        self.hidden = False

    def showMessage(self, *args, **kwargs):
        self.messages.append(args)

    def setToolTip(self, text):
        self.tooltip = text

    def setIcon(self, icon):
        pass

    def hide(self):
        self.hidden = True


@pytest.fixture
def launcher(app):
    launcher = _TestableLauncher()
    yield launcher
    for w in launcher._workers:
        w.shutdown()
    if launcher._jupyter_panel is not None:
        launcher._jupyter_panel.shutdown()
    launcher._timer.stop()
    launcher.deleteLater()


def test_construct_and_tick(launcher):
    assert len(launcher._workers) == 3
    assert launcher._jupyter_panel is not None
    launcher._tick()
    # nothing started -> every worker reports "not running" -> red tier
    assert launcher._agg_label.text() == "Issues"
    assert "Lakeshore: not running" in launcher._issues_label.text()


def test_ready_tiers(launcher, monkeypatch):
    for w in launcher._workers:
        monkeypatch.setattr(w, "get_status", lambda: ComponentStatus(ok=True))
    launcher._tick()
    assert launcher._agg_label.text() == "Ready (Jupyter stopped)"

    monkeypatch.setattr(
        launcher._jupyter_panel, "get_status", lambda: ComponentStatus(ok=True)
    )
    launcher._tick()
    assert launcher._agg_label.text() == "Ready"


def test_close_hides_to_tray(launcher):
    tray = _StubTray()
    launcher._tray = tray
    launcher.show()
    assert launcher.isVisible()

    launcher.close()

    assert not launcher.isVisible()  # hidden, not torn down
    assert len(tray.messages) == 1  # one-time balloon
    launcher.close()
    assert len(tray.messages) == 1

    launcher._show_window()
    assert launcher.isVisible()


def test_close_without_tray_quits(launcher):
    # No tray host (e.g. bare Linux dev session) -> conventional close path.
    launcher._tray = None
    launcher.show()
    closed = launcher.close()
    assert closed  # nothing running -> no dialog, handshake accepts


def test_tray_tooltip_and_quit_teardown(launcher):
    tray = _StubTray()
    launcher._tray = tray
    launcher._tick()
    assert "VTI Monitor" in tray.tooltip
    assert "Issues" in tray.tooltip

    launcher._quit()  # nothing running -> no dialog
    assert tray.hidden


def test_single_instance_socket(app):
    name = f"me-qt-test-{os.getpid()}"
    assert not base_launcher._existing_instance(name)

    server = base_launcher._listen(name)
    assert server is not None
    try:
        assert base_launcher._existing_instance(name)
    finally:
        server.close()
        base_launcher.QtNetwork.QLocalServer.removeServer(name)

    assert not base_launcher._existing_instance(name)


def test_instance_ping_shows_window(launcher, app):
    name = f"me-qt-ping-{os.getpid()}"
    server = base_launcher._listen(name)
    assert server is not None
    launcher._instance_server = server
    server.newConnection.connect(launcher._on_instance_ping)
    try:
        assert not launcher.isVisible()
        assert base_launcher._existing_instance(name)  # the "show" ping
        for _ in range(100):
            app.processEvents()
            if launcher.isVisible():
                break
        assert launcher.isVisible()
    finally:
        server.close()
        base_launcher.QtNetwork.QLocalServer.removeServer(name)


def test_jupyter_launch_cmd_pins_venv(launcher):
    """The 2026-07-14 gotcha: never dispatch through `-m jupyter` (PATH)."""
    cmd = launcher._jupyter_panel._build_cmd()
    assert cmd[:3] == [base_launcher.sys.executable, "-m", "jupyterlab"]
    assert "jupyter" not in cmd[cmd.index("-m") + 1 :][1:]  # no dispatcher hop
    assert "--collaborative" in cmd
    assert "--ServerApp.port_retries=0" in cmd
    assert "--no-browser" in cmd  # the Open button is the only way in
    i = cmd.index("--port")
    assert cmd[i + 1] == "8890"


def test_server_python_avoids_pythonw(monkeypatch, tmp_path):
    """The console-flash fix: a pythonw server has no console, so node/npm
    grandchildren each pop a visible console window. On Windows the server
    must run under the sibling python.exe (hidden via CREATE_NO_WINDOW)."""
    pythonw = tmp_path / "pythonw.exe"
    pythonw.touch()

    # Not Windows -> untouched, whatever the name
    monkeypatch.setattr(jupyter_panel.sys, "platform", "linux")
    assert jupyter_panel._server_python(str(pythonw)) == str(pythonw)

    # Windows but no console sibling -> fall back to what we have
    monkeypatch.setattr(jupyter_panel.sys, "platform", "win32")
    assert jupyter_panel._server_python(str(pythonw)) == str(pythonw)

    # Windows with the sibling present -> swap to python.exe
    console = tmp_path / "python.exe"
    console.touch()
    assert jupyter_panel._server_python(str(pythonw)) == str(console)

    # Already a console python -> untouched
    assert jupyter_panel._server_python(str(console)) == str(console)


def test_window_grows_with_content(launcher, app):
    """The 2026-07-15 VTI report: expanding a worker's Data disclosure must
    grow the window, and the default layout must open at content size."""
    launcher.show()
    app.processEvents()
    assert launcher.height() >= launcher.sizeHint().height()

    before = launcher.height()
    w = launcher._workers[0]
    w._on_data('{"_summary": "23.4C", "temp_C": 23.4, "humidity_pct": 41.2}')
    w._data_toggle_btn.setChecked(True)
    app.processEvents()
    assert launcher.height() > before
    assert launcher.height() >= launcher.sizeHint().height()


def test_buttons_survive_signal_delivery(launcher, monkeypatch):
    """The 2026-07-14 VTI crash: clicked emits a checked bool, and PyQt5
    delivers it into the @main_thread_only wrapper's *args — a slot connected
    without a zero-arg lambda then TypeErrors, which PyQt5 escalates to
    qFatal() and the whole GUI aborts. Click every button through the real
    signal (btn.click()), never by calling the slot directly.
    """
    # PyQt5 routes slot exceptions to sys.excepthook and only qFatal()s under
    # the default hook — a custom hook turns the abort into a test failure.
    caught = []
    monkeypatch.setattr(sys, "excepthook", lambda t, v, tb: caught.append(v))

    jp = launcher._jupyter_panel
    monkeypatch.setattr(jp._proc, "start", lambda *a, **k: None)
    monkeypatch.setattr(jp._proc, "stop", lambda: None)
    buttons = [jp._start_btn, jp._stop_btn, jp._open_btn]
    for w in launcher._workers:
        monkeypatch.setattr(w._proc, "start_with_output", lambda *a, **k: None)
        monkeypatch.setattr(w._proc, "stop", lambda: None)
        buttons += [w._start_btn, w._stop_btn, w._data_toggle_btn]

    for btn in buttons:
        btn.setEnabled(True)  # click() on a disabled button is a no-op
        btn.click()

    assert caught == []


class _TestablePinkLauncher(PinkLauncher):
    def _load_config(self):
        return PinkConfig(
            influxdb=InfluxConfig(url="http://localhost:9", token="t", org="o", bucket="b"),
            health={},  # no pollers -> no threads/network in tests
            hardware=PinkHardware(lc_logs_folder="/tmp", ami430_addr="x"),
        )


@pytest.fixture
def pink_launcher(app):
    launcher = _TestablePinkLauncher()
    yield launcher
    for w in launcher._workers:
        w.shutdown()
    if launcher._jupyter_panel is not None:
        launcher._jupyter_panel.shutdown()
    launcher._timer.stop()
    launcher.deleteLater()


def test_pink_construct_and_tick(pink_launcher):
    assert len(pink_launcher._workers) == 3
    assert pink_launcher._jupyter_panel is not None
    pink_launcher._tick()
    assert pink_launcher._agg_label.text() == "Issues"
    assert "LC FP: not running" in pink_launcher._issues_label.text()
    assert "AVS TC: not running" in pink_launcher._issues_label.text()
    assert "Magnet: not running" in pink_launcher._issues_label.text()


def test_pink_worker_cmds_and_jupyter_port(pink_launcher):
    cmds = [w._cmd for w in pink_launcher._workers]
    assert cmds == [
        [sys.executable, "-m", "workers.pink_scraper", "--family", "FP"],
        [sys.executable, "-m", "workers.pink_scraper", "--family", "TC"],
        [sys.executable, "-m", "workers.magnet", "--rig", "pink"],
    ]
    cmd = pink_launcher._jupyter_panel._build_cmd()
    i = cmd.index("--port")
    assert cmd[i + 1] == "8890"


def test_jupyter_env_layers_repo_config(launcher, monkeypatch):
    monkeypatch.delenv("JUPYTER_CONFIG_PATH", raising=False)
    env = launcher._jupyter_panel._build_env()
    assert env["JUPYTER_CONFIG_PATH"].endswith("jupyter-config")

    monkeypatch.setenv("JUPYTER_CONFIG_PATH", "/elsewhere")
    env = launcher._jupyter_panel._build_env()
    first, rest = env["JUPYTER_CONFIG_PATH"].split(os.pathsep, 1)
    assert first.endswith("jupyter-config")
    assert rest == "/elsewhere"
