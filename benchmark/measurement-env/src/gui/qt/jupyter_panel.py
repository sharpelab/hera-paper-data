"""Shared JupyterLab panel — opt-in via BaseLauncher.JUPYTER_DIR/JUPYTER_PORT.

Two deliberate choices, both from the 2026-07-14 VTI session
(docs/plans/LAUNCHER_QT_PLAN.md):

- Launches ``sys.executable -m jupyterlab`` — NOT ``-m jupyter lab``. The
  ``jupyter`` dispatcher resolves the ``jupyter-lab`` subcommand executable
  via PATH, so a foreign Python that shadows the venv starts the wrong
  server (which then dies on ``--collaborative``). ``jupyterlab.__main__``
  runs the LabApp in the launcher's own interpreter; PATH is never consulted.
- Pins the port with ``--ServerApp.port_retries=0``: a silent fallback port
  would mean two collaborative servers rooted at the same directory,
  contending for one ``.jupyter_ystore.db``.
"""

import os
import sys
import webbrowser
from pathlib import Path

from PyQt5 import QtWidgets

from core import REPO_DIR
from gui.jupyter_discovery import find_server_url
from gui.managed_process import ManagedProcess
from gui.utils import JUPYTER_LOG_PATH, ComponentStatus, main_thread_only


def _server_python(executable: str = sys.executable) -> str:
    """Interpreter for the server: the console python.exe, never pythonw.

    Under pythonw the server has no console, so every console-subsystem
    descendant (node/npm from jupyterlab's build check and jupyter_lsp,
    kernels, git, ...) allocates its own console — a visible window flash
    per spawn. ManagedProcess launches with CREATE_NO_WINDOW, so a console
    python gets one *hidden* console the whole process tree inherits.
    """
    exe = Path(executable)
    if sys.platform == "win32" and exe.name.lower() == "pythonw.exe":
        console = exe.with_name("python.exe")
        if console.exists():
            return str(console)
    return executable


class JupyterPanel(QtWidgets.QGroupBox):
    """JupyterLab start/stop panel with server-URL discovery and Open button."""

    def __init__(self, launcher, *, notebook_dir, port: int) -> None:
        super().__init__("JupyterLab")
        self._launcher = launcher
        self._notebook_dir = notebook_dir
        self._port = port
        self._proc = ManagedProcess("jupyter")
        self._base_url = None
        self._status = ComponentStatus(ok=False, message="not running")

        layout = QtWidgets.QVBoxLayout(self)

        status_row = QtWidgets.QHBoxLayout()
        status_row.addWidget(QtWidgets.QLabel("Status:"))
        self._status_label = QtWidgets.QLabel("Stopped")
        self._status_label.setStyleSheet("color: gray;")
        status_row.addWidget(self._status_label)
        status_row.addStretch(1)
        layout.addLayout(status_row)

        btn_row = QtWidgets.QHBoxLayout()
        # Zero-arg lambdas: clicked emits a checked bool, and PyQt5 delivers
        # it to the @main_thread_only wrapper's *args — TypeError → qFatal.
        self._start_btn = QtWidgets.QPushButton("Start")
        self._start_btn.clicked.connect(lambda: self._start())
        btn_row.addWidget(self._start_btn)
        self._stop_btn = QtWidgets.QPushButton("Stop")
        self._stop_btn.setEnabled(False)
        self._stop_btn.clicked.connect(lambda: self._stop())
        btn_row.addWidget(self._stop_btn)
        # The server URL carries the auth token, so a browser can only reach
        # it through us — Open is the user's way in, not a convenience.
        self._open_btn = QtWidgets.QPushButton("Open")
        self._open_btn.setEnabled(False)
        self._open_btn.clicked.connect(lambda: self._open())
        btn_row.addWidget(self._open_btn)
        layout.addLayout(btn_row)

    # --- Launch -------------------------------------------------------------

    def _build_cmd(self) -> list[str]:
        return [
            _server_python(), "-m", "jupyterlab",
            "--notebook-dir", str(self._notebook_dir),
            "--port", str(self._port),
            "--ServerApp.port_retries=0",
            # The Open button is the only way in — no surprise browser tab.
            "--no-browser",
            "--collaborative",
            # nb-collab's HTTP preflight to /api/collaboration/session/ doesn't
            # carry the token, so XSRF rejects POST/PUT with 403. Local-only JL.
            "--ServerApp.disable_check_xsrf=True",
        ]

    @staticmethod
    def _build_env() -> dict:
        """os.environ with the repo's jupyter-config/ prepended to the config path.

        Repo-side so it survives env rebuilds; adds recordTiming (executed
        cells get metadata.execution timing). See jupyter-config/README.md.
        """
        jl_env = dict(os.environ)
        config_path = str(REPO_DIR / "jupyter-config")
        existing = jl_env.get("JUPYTER_CONFIG_PATH", "")
        jl_env["JUPYTER_CONFIG_PATH"] = (
            f"{config_path}{os.pathsep}{existing}" if existing else config_path
        )
        return jl_env

    @main_thread_only
    def _start(self) -> None:
        self._start_btn.setEnabled(False)
        self._stop_btn.setEnabled(True)
        self._set_status("Starting...", "orange")

        notebook_dir_str = str(self._notebook_dir)
        self._proc.start(
            cmd=self._build_cmd(),
            ready_check=lambda: find_server_url(notebook_dir_str),
            dispatch=self._launcher.dispatch,
            on_ready=self._on_ready,
            on_stopped=self._on_stopped,
            log_path=JUPYTER_LOG_PATH,
            env=self._build_env(),
        )

    @main_thread_only
    def _stop(self) -> None:
        self._set_status("Stopping...", "orange")
        self._proc.stop()
        self._on_stopped()

    @main_thread_only
    def _open(self) -> None:
        if self._base_url is None:
            return
        if sys.platform == "win32":
            os.startfile(self._base_url)
        else:
            webbrowser.open(self._base_url)

    # --- State --------------------------------------------------------------

    @main_thread_only
    def _set_status(self, text: str, color: str) -> None:
        self._status_label.setText(text)
        self._status_label.setStyleSheet(f"color: {color};")

    @main_thread_only
    def _on_ready(self, url) -> None:
        self._base_url = url
        self._set_status("Running", "green")
        self._start_btn.setEnabled(False)
        self._stop_btn.setEnabled(True)
        self._open_btn.setEnabled(url is not None)
        self._status = ComponentStatus(ok=True)

    @main_thread_only
    def _on_stopped(self) -> None:
        self._base_url = None
        self._set_status("Stopped", "gray")
        self._start_btn.setEnabled(True)
        self._stop_btn.setEnabled(False)
        self._open_btn.setEnabled(False)
        self._status = ComponentStatus(ok=False, message="not running")

    def get_status(self) -> ComponentStatus:
        return self._status

    @property
    def base_url(self):
        """Server /lab?token= URL while running, else None."""
        return self._base_url

    @property
    def running(self) -> bool:
        return self._proc.running

    def shutdown(self) -> None:
        """Stop the server. Safe to call whether running or not."""
        self._proc.stop()
