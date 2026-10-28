"""Toploader launcher (Qt).

The toploader's launcher: the hardware workers (AVS probe/fridge bridges,
Leiden QCS heaters, AMI 430 magnet, LC log scrapers, Thorlabs thermo) plus
the rig's JupyterLab, new-run creation from the dated templates, and the UPS
monitor service check. All scaffolding (status panel, tick loop, log viewer,
tray, single-instance, quit handshake, Jupyter panel) comes from
gui.qt.base_launcher; this class supplies the rig config, the worker list,
and the two toploader-only panels.

JupyterLab: rooted at ~/measurements on port 8888 — the port the rig's
notebook bookmarks and the legacy launcher's server used.

The QCS heater panel appears only once `hardware.qcs_board_num` is set in
toploader.toml (the Phase B bring-up in docs/plans/QCS_HEATER_CONTROL.md);
until then the launcher has no heater surface and DR TempControl stays the
heater UI.
"""

import os
import shutil
import subprocess
import sys
import threading
import webbrowser
from datetime import date
from pathlib import Path

from PyQt5 import QtCore, QtWidgets

from core import REPO_DIR
from core.config import load_config
from gui.managed_process import _NO_WINDOW
from gui.qt.avs_probe_panel import ProbeWorkerPanel
from gui.qt.base_launcher import BaseLauncher
from gui.qt.qcs_panel import QcsHeaterPanel
from gui.qt.worker_panel import WorkerPanel
from gui.utils import ComponentStatus, _log, main_thread_only

MEASUREMENTS_DIR = Path.home() / "measurements"
TEMPLATES_DIR = REPO_DIR / "templates"
RIG_CARD = REPO_DIR / "hera" / "rig-cards" / "toploader.md"

# (template name, dated file suffix) copied into a new run directory
RUN_TEMPLATES = (
    ("toploader_measure.ipynb", "measure"),
    ("toploader_ana.ipynb", "ana"),
    ("iris_scratch.ipynb", "iris_scratch"),
)

_UPS_SERVICE = "ups-monitor"
_UPS_POLL_MS = 10_000


class ToploaderLauncher(BaseLauncher):
    TITLE = "Toploader Monitor"
    MIN_SIZE = (300, 250)
    LOG_TAG = "toploader-launcher"
    LOG_WINDOW_TITLE = "Toploader Launcher Log"
    START_ALL_TEXT = "Start All"
    INSTANCE_NAME = "measurement-env-toploader"
    JUPYTER_DIR = MEASUREMENTS_DIR
    JUPYTER_PORT = 8888

    # --- BaseLauncher hooks ---------------------------------------------------

    def _load_config(self):
        return load_config()

    def _init_state(self) -> None:
        self._ups_status = ComponentStatus(ok=False, message="checking...")
        self._ups_timer = None

    def _make_workers(self) -> list:
        cfg = self._config
        workers = [
            ProbeWorkerPanel(
                self, name="AVS-47B probe", desc="probe thermometry", tag="avs_probe",
                health_key="avs_probe", health_measurement="AVS_bridge",
                config=cfg,
            ),
            WorkerPanel(
                self, name="AVS-47B fridge", desc="fridge thermometry", tag="avs_fridge",
                cmd=[sys.executable, "-m", "workers.avs_fridge"],
                health_key="avs_fridge", health_measurement="AVS_bridge",
                config=cfg,
            ),
        ]
        if cfg.hardware.qcs_board_num >= 0:
            workers.append(QcsHeaterPanel(
                self, name="Leiden QCS", desc="heaters", tag="qcs_heater",
                cmd=[sys.executable, "-m", "workers.qcs_heater"],
                health_key="qcs", health_measurement="QCS",
                config=cfg,
            ))
        workers += [
            WorkerPanel(
                self, name="AMI 430", desc="magnet field (read-only)", tag="magnet",
                cmd=[sys.executable, "-m", "workers.magnet"],
                health_key="magnet", health_measurement="AVS_bridge",
                config=cfg,
            ),
            WorkerPanel(
                self, name="LC FrontPanel", desc="pressures/flow", tag="lc_scraper_fp",
                cmd=[sys.executable, "-m", "workers.lc_scraper", "--family", "FP"],
                health_key="lc_scrapper_fp", health_measurement="LC_scrapper",
                config=cfg,
            ),
            WorkerPanel(
                self, name="LC PulseTube", desc="compressor log", tag="lc_scraper_pt",
                cmd=[sys.executable, "-m", "workers.lc_scraper", "--family", "PT"],
                health_key="lc_scrapper_pt", health_measurement="LC_scrapper",
                config=cfg,
            ),
            WorkerPanel(
                self, name="Thorlabs TSP01B", desc="room temp/humidity", tag="thorlabs_thermo",
                cmd=[sys.executable, "-m", "workers.thorlabs_thermo"],
                health_key="thorlabs_thermo", health_measurement="thorlabs_thermo",
                config=cfg,
            ),
        ]
        return workers

    def _build_pre_worker_panels(self) -> None:
        self._build_run_panel()

    def _build_post_worker_panels(self) -> None:
        self._build_ups_panel()

    def _extra_issues(self) -> list[str]:
        if not self._ups_status.ok:
            return [f"UPS Monitor: {self._ups_status.message}"]
        return []

    def _tick(self) -> None:
        super()._tick()
        # Runs are created into the live JupyterLab so the notebooks open.
        self._create_btn.setEnabled(self._jupyter_panel.base_url is not None)

    # --- New Run panel ------------------------------------------------------------

    def _build_run_panel(self) -> None:
        box = QtWidgets.QGroupBox("New Run")
        grid = QtWidgets.QGridLayout(box)

        grid.addWidget(QtWidgets.QLabel("User:"), 0, 0)
        self._user_combo = QtWidgets.QComboBox()
        self._user_combo.setEditable(True)
        self._user_combo.addItems(self._list_users())
        self._user_combo.setCurrentText("")
        grid.addWidget(self._user_combo, 0, 1)

        grid.addWidget(QtWidgets.QLabel("Name:"), 1, 0)
        self._name_edit = QtWidgets.QLineEdit()
        grid.addWidget(self._name_edit, 1, 1)

        # Zero-arg lambda: see WorkerPanel's Start/Stop buttons.
        self._create_btn = QtWidgets.QPushButton("Create")
        self._create_btn.setEnabled(False)
        self._create_btn.clicked.connect(lambda: self._create_run())
        grid.addWidget(self._create_btn, 2, 0, 1, 2)

        self._run_msg = QtWidgets.QLabel("")
        self._run_msg.setWordWrap(True)
        self._run_msg.setVisible(False)
        grid.addWidget(self._run_msg, 3, 0, 1, 2)

        grid.setColumnStretch(1, 1)
        self._panel_layout.addWidget(box)

    @staticmethod
    def _list_users() -> list[str]:
        if not MEASUREMENTS_DIR.exists():
            return []
        return sorted(
            d.name
            for d in MEASUREMENTS_DIR.iterdir()
            if d.is_dir() and not d.name.startswith(".")
        )

    @main_thread_only
    def _create_run(self) -> None:
        user = self._user_combo.currentText().strip()
        name = self._name_edit.text().strip()

        if not user:
            self._show_run_msg("Select a user.", "red")
            return
        if not name:
            self._show_run_msg("Enter a run name.", "red")
            return

        today = date.today().strftime("%Y%m%d")
        run_dir = MEASUREMENTS_DIR / user / name
        measure_name = f"{today}_measure.ipynb"
        if (run_dir / measure_name).exists():
            self._show_run_msg(f"{measure_name} already exists.", "red")
            return

        run_dir.mkdir(parents=True, exist_ok=True)
        created = []
        for template, suffix in RUN_TEMPLATES:
            src = TEMPLATES_DIR / template
            if src.exists():
                dest = run_dir / f"{today}_{suffix}.ipynb"
                shutil.copy2(src, dest)
                created.append(dest)

        # Rig card: repo-canonical, deployed copy refreshed on every run
        # creation (agents read it, never edit it).
        if RIG_CARD.exists():
            shutil.copy2(RIG_CARD, run_dir / "rig_card.md")

        _log(self.LOG_TAG, f"created run {user}/{name} ({len(created)} notebooks)")
        self._show_run_msg(f"Created {user}/{name}/{today}_*.ipynb", "green")
        for nb in created:
            self._open_notebook(nb)

    def _open_notebook(self, nb_path: Path) -> None:
        """Open a notebook in the running JupyterLab via its /lab/tree URL."""
        base_url = self._jupyter_panel.base_url
        if base_url is None:
            return
        try:
            rel = nb_path.relative_to(MEASUREMENTS_DIR)
        except ValueError:
            return
        url = base_url.replace("/lab?", f"/lab/tree/{rel.as_posix()}?")
        if sys.platform == "win32":
            os.startfile(url)
        else:
            webbrowser.open(url)

    @main_thread_only
    def _show_run_msg(self, text: str, color: str) -> None:
        self._run_msg.setText(text)
        self._run_msg.setStyleSheet(f"color: {color};")
        self._run_msg.setVisible(True)

    # --- UPS panel ------------------------------------------------------------------

    def _build_ups_panel(self) -> None:
        box = QtWidgets.QGroupBox("UPS Monitor")
        row = QtWidgets.QHBoxLayout(box)
        row.addWidget(QtWidgets.QLabel("Status:"))
        self._ups_label = QtWidgets.QLabel("checking...")
        self._ups_label.setStyleSheet("color: gray;")
        row.addWidget(self._ups_label)
        row.addStretch(1)
        self._panel_layout.addWidget(box)

        if sys.platform != "win32":
            self._ups_label.setText("N/A (Windows only)")
            self._ups_status = ComponentStatus(ok=True)
            return

        self._ups_timer = QtCore.QTimer(self)
        self._ups_timer.timeout.connect(self._poll_ups)
        self._ups_timer.start(_UPS_POLL_MS)
        self._poll_ups()

    def _poll_ups(self) -> None:
        """Ask nssm for the service state off the GUI thread; deliver via dispatch."""

        def check():
            try:
                result = subprocess.run(
                    ["nssm", "status", _UPS_SERVICE],
                    capture_output=True, text=True, timeout=5,
                    creationflags=_NO_WINDOW,
                )
                state = result.stdout.strip()
            except Exception as e:
                state = f"error: {e}"
            self.dispatch(lambda: self._set_ups_state(state))

        threading.Thread(target=check, daemon=True).start()

    @main_thread_only
    def _set_ups_state(self, state: str) -> None:
        if state == "SERVICE_RUNNING":
            self._ups_label.setText("Running")
            self._ups_label.setStyleSheet("color: green;")
            self._ups_status = ComponentStatus(ok=True)
            return
        display = state.removeprefix("SERVICE_").replace("_", " ").title()
        self._ups_label.setText(display)
        self._ups_label.setStyleSheet("color: red;")
        self._ups_status = ComponentStatus(ok=False, message=display.lower())


def main():
    sys.exit(ToploaderLauncher.run())


if __name__ == "__main__":
    main()
