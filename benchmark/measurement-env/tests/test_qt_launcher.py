"""Headless smoke tests for the Qt rig launchers (QT_QPA_PLATFORM=offscreen).

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

from core.config import (
    InfluxConfig,
    PinkConfig,
    PinkHardware,
    ToploaderConfig,
    ToploaderHardware,
    VtiConfig,
    VtiHardware,
)
from gui.qt import base_launcher, jupyter_panel, toploader_launcher
from gui.qt.pink_launcher import PinkLauncher
from gui.qt.toploader_launcher import ToploaderLauncher
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
    assert [w.title() for w in launcher._workers] == [
        "Lakeshore 335 - sample/vaporizer", "AMI 1700 - He level",
        "Terranova 906A - probe pressure", "Lakeshore 218 - magnet/GM temps",
        "FAST-PS - magnet field",
    ]
    assert launcher._jupyter_panel is not None
    launcher._tick()
    # nothing started -> every worker reports "not running" -> red tier
    assert launcher._agg_label.text() == "Issues"
    assert "Lakeshore 335: not running" in launcher._issues_label.text()


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
    assert "Leiden FrontPanel: not running" in pink_launcher._issues_label.text()
    assert "AVS-47: not running" in pink_launcher._issues_label.text()
    assert "AMI 430: not running" in pink_launcher._issues_label.text()


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


# --- Toploader ------------------------------------------------------------------


def _toploader_config(qcs_board_num=-1):
    return ToploaderConfig(
        influxdb=InfluxConfig(url="http://localhost:9", token="t", org="o", bucket="b"),
        health={},  # no pollers -> no threads/network in tests
        hardware=ToploaderHardware(
            avs_fridge_gpib="x", avs_probe_gpib="x", ami430_addr="x",
            lc_logs_folder="/tmp", temperature_log_dir="/tmp",
            qcs_board_num=qcs_board_num,
        ),
    )


class _TestableToploaderLauncher(ToploaderLauncher):
    _qcs_board_num = -1

    def _load_config(self):
        return _toploader_config(self._qcs_board_num)


def _make_toploader(app, tmp_path, monkeypatch, qcs_board_num=-1):
    measurements = tmp_path / "measurements"
    (measurements / "aaron").mkdir(parents=True)
    (measurements / "zack").mkdir()
    (measurements / ".hidden").mkdir()
    monkeypatch.setattr(toploader_launcher, "MEASUREMENTS_DIR", measurements)
    monkeypatch.setattr(_TestableToploaderLauncher, "JUPYTER_DIR", measurements)
    monkeypatch.setattr(_TestableToploaderLauncher, "_qcs_board_num", qcs_board_num)
    return _TestableToploaderLauncher()


def _teardown(launcher):
    for w in launcher._workers:
        w.shutdown()
    if launcher._jupyter_panel is not None:
        launcher._jupyter_panel.shutdown()
    launcher._timer.stop()
    if launcher._ups_timer is not None:
        launcher._ups_timer.stop()
    launcher.deleteLater()


@pytest.fixture
def toploader(app, tmp_path, monkeypatch):
    launcher = _make_toploader(app, tmp_path, monkeypatch)
    yield launcher
    _teardown(launcher)


def test_toploader_construct_and_tick(toploader):
    assert [w.title() for w in toploader._workers] == [
        "AVS-47B probe - probe thermometry", "AVS-47B fridge - fridge thermometry",
        "AMI 430 - magnet field (read-only)", "LC FrontPanel - pressures/flow",
        "LC PulseTube - compressor log", "Thorlabs TSP01B - room temp/humidity",
    ]
    assert toploader._jupyter_panel is not None
    toploader._tick()
    assert toploader._agg_label.text() == "Issues"
    issues = toploader._issues_label.text()
    assert "AVS-47B probe: not running" in issues
    # Not Windows -> the UPS service check is N/A, never an issue.
    assert "UPS Monitor" not in issues
    assert toploader._ups_status.ok


def test_toploader_qcs_panel_appears_once_the_board_is_configured(
    app, tmp_path, monkeypatch,
):
    launcher = _make_toploader(app, tmp_path, monkeypatch, qcs_board_num=0)
    try:
        titles = [w.title() for w in launcher._workers]
        assert titles[2] == "Leiden QCS - heaters"
        assert launcher._workers[2]._cmd == [
            sys.executable, "-m", "workers.qcs_heater"]
    finally:
        _teardown(launcher)


def test_toploader_worker_cmds_and_jupyter_port(toploader):
    cmds = [w._get_cmd() for w in toploader._workers]
    assert cmds == [
        [sys.executable, "-m", "workers.avs_probe",
         "--probe", "1", "--channel", "3", "--excitation", "1"],
        [sys.executable, "-m", "workers.avs_fridge"],
        [sys.executable, "-m", "workers.magnet"],
        [sys.executable, "-m", "workers.lc_scraper", "--family", "FP"],
        [sys.executable, "-m", "workers.lc_scraper", "--family", "PT"],
        [sys.executable, "-m", "workers.thorlabs_thermo"],
    ]
    cmd = toploader._jupyter_panel._build_cmd()
    i = cmd.index("--port")
    assert cmd[i + 1] == "8888"
    i = cmd.index("--notebook-dir")
    assert cmd[i + 1] == str(toploader_launcher.MEASUREMENTS_DIR)


def test_probe_panel_dropdowns_drive_the_command_and_lock_while_running(
    toploader, monkeypatch,
):
    probe = toploader._workers[0]
    probe._probe_combo.setCurrentText("2")
    probe._channel_combo.setCurrentIndex(0)
    probe._exc_combo.setCurrentText("3")
    assert probe.selection == ("2", "0", "3")
    assert probe._channel_combo.currentText().startswith("0: ")
    assert probe._get_cmd()[-6:] == [
        "--probe", "2", "--channel", "0", "--excitation", "3"]

    launched = []
    monkeypatch.setattr(
        probe._proc, "start_with_output", lambda **kw: launched.append(kw["cmd"]))
    monkeypatch.setattr(probe._proc, "stop", lambda: None)
    probe.start()
    assert launched == [probe._get_cmd()]
    assert all(not c.isEnabled() for c in probe._combos)
    probe.stop()
    assert all(c.isEnabled() for c in probe._combos)


def test_new_run_lists_users_and_gates_create_on_jupyter(toploader, monkeypatch):
    assert [toploader._user_combo.itemText(i)
            for i in range(toploader._user_combo.count())] == ["aaron", "zack"]
    toploader._tick()
    assert not toploader._create_btn.isEnabled()

    monkeypatch.setattr(toploader._jupyter_panel, "_base_url", "http://x/lab?token=t")
    toploader._tick()
    assert toploader._create_btn.isEnabled()


def test_new_run_copies_dated_templates_and_the_rig_card(
    toploader, tmp_path, monkeypatch,
):
    templates = tmp_path / "templates"
    templates.mkdir()
    for name, _ in toploader_launcher.RUN_TEMPLATES:
        (templates / name).write_text("{}")
    rig_card = tmp_path / "toploader.md"
    rig_card.write_text("# rig")
    monkeypatch.setattr(toploader_launcher, "TEMPLATES_DIR", templates)
    monkeypatch.setattr(toploader_launcher, "RIG_CARD", rig_card)
    opened = []
    monkeypatch.setattr(toploader, "_open_notebook", opened.append)

    toploader._user_combo.setCurrentText("zack")
    toploader._name_edit.setText("dev-01")
    toploader._create_run()

    today = toploader_launcher.date.today().strftime("%Y%m%d")
    run_dir = toploader_launcher.MEASUREMENTS_DIR / "zack" / "dev-01"
    assert sorted(p.name for p in run_dir.iterdir()) == sorted([
        f"{today}_measure.ipynb", f"{today}_ana.ipynb",
        f"{today}_iris_scratch.ipynb", "rig_card.md",
    ])
    assert [p.name for p in opened] == [
        f"{today}_measure.ipynb", f"{today}_ana.ipynb", f"{today}_iris_scratch.ipynb"]
    assert toploader._run_msg.isVisible() or toploader._run_msg.text().startswith("Created")

    # Second create of the same run refuses rather than overwriting.
    toploader._create_run()
    assert "already exists" in toploader._run_msg.text()


def test_new_run_validates_user_and_name(toploader):
    toploader._user_combo.setCurrentText("")
    toploader._name_edit.setText("x")
    toploader._create_run()
    assert toploader._run_msg.text() == "Select a user."

    toploader._user_combo.setCurrentText("zack")
    toploader._name_edit.setText("  ")
    toploader._create_run()
    assert toploader._run_msg.text() == "Enter a run name."


def test_open_notebook_builds_the_lab_tree_url(toploader, monkeypatch):
    urls = []
    monkeypatch.setattr(toploader_launcher.webbrowser, "open", urls.append)
    monkeypatch.setattr(toploader_launcher.sys, "platform", "linux")
    monkeypatch.setattr(toploader._jupyter_panel, "_base_url",
                        "http://localhost:8888/lab?token=abc")

    nb = toploader_launcher.MEASUREMENTS_DIR / "zack" / "dev-01" / "20260902_measure.ipynb"
    toploader._open_notebook(nb)

    assert urls == ["http://localhost:8888/lab/tree/zack/dev-01/20260902_measure.ipynb?token=abc"]


def test_ups_state_maps_to_status(toploader):
    toploader._set_ups_state("SERVICE_RUNNING")
    assert toploader._ups_status.ok
    assert toploader._extra_issues() == []

    toploader._set_ups_state("SERVICE_STOPPED")
    assert toploader._ups_label.text() == "Stopped"
    assert toploader._extra_issues() == ["UPS Monitor: stopped"]

    toploader._set_ups_state("error: nssm not found")
    assert toploader._extra_issues() == ["UPS Monitor: error: nssm not found"]


def test_toploader_buttons_survive_signal_delivery(toploader, monkeypatch):
    """Same qFatal trap as the VTI test, for the toploader-only buttons."""
    caught = []
    monkeypatch.setattr(sys, "excepthook", lambda t, v, tb: caught.append(v))
    monkeypatch.setattr(toploader, "_create_run", lambda: None)
    for w in toploader._workers:
        monkeypatch.setattr(w._proc, "start_with_output", lambda *a, **k: None)
        monkeypatch.setattr(w._proc, "stop", lambda: None)
    buttons = [toploader._create_btn]
    for w in toploader._workers:
        buttons += [w._start_btn, w._stop_btn]
    for btn in buttons:
        btn.setEnabled(True)
        btn.click()
    assert caught == []
