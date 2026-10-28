"""Shared Qt launcher scaffolding for the per-rig measurement-env launchers.

`BaseLauncher(QMainWindow)` owns the rig-agnostic GUI: the aggregate status
panel, the single 1s `QTimer` tick, the issue roll-up, the tailing log viewer,
Start-All, the opt-in JupyterLab panel, and the quit handshake — plus the three
wins the Qt migration exists for (docs/plans/LAUNCHER_QT_PLAN.md):

- **Single-instance guard**: `run()` connects to a per-rig `QLocalServer` name;
  if something answers, the running instance is asked to show itself and this
  process exits. A second launch can never spawn a colliding second worker set.
- **Tray icon**: the launcher lives in the system tray (with a health-colored
  status dot); the tray menu is the only Quit surface.
- **Close = hide**: the window's X hides to the tray instead of tearing down
  workers. Where no tray host exists (Linux dev), X falls back to the
  conventional confirm-and-quit handshake.

Subclass surface:
    Class attrs: TITLE, MIN_SIZE, LOG_TAG, LOG_WINDOW_TITLE, START_ALL_TEXT,
                 INSTANCE_NAME (required), JUPYTER_DIR/JUPYTER_PORT (opt-in)
    Required:    _load_config(), _make_workers() -> list[WorkerPanel]
    Optional:    _init_state(), _build_pre_worker_panels(),
                 _build_post_worker_panels(), _extra_issues() -> list[str],
                 _ready_tier() -> (text, color), _running_extra() -> list[str],
                 _stop_extra()
"""

import ctypes
import sys

from PyQt5 import QtCore, QtGui, QtNetwork, QtWidgets

from core import REPO_DIR
from gui.qt.jupyter_panel import JupyterPanel
from gui.utils import LOG_PATH, _log, tail_lines

ICON_PATH = REPO_DIR / "assets" / "measurement-env.png"

_TICK_MS = 1000
_INSTANCE_CONNECT_TIMEOUT_MS = 500


class _Dispatcher(QtCore.QObject):
    """Marshals callables onto the GUI thread via a queued signal.

    Passed to ManagedProcess as its `dispatch` callable: emitting from a
    daemon reader thread queues the slot onto the thread this object lives
    in (the GUI thread) — the Qt replacement for tk's `after(0, cb)`.
    """

    _fire = QtCore.pyqtSignal(object)

    def __init__(self, parent: QtCore.QObject) -> None:
        super().__init__(parent)
        self._fire.connect(self._run)

    def __call__(self, cb) -> None:
        self._fire.emit(cb)

    @staticmethod
    def _run(cb) -> None:
        cb()


def _existing_instance(name: str) -> bool:
    """True if a live launcher already listens on the local socket *name*.

    Connecting is itself the "show yourself" signal — there is only one
    message, so no byte protocol is needed.
    """
    sock = QtNetwork.QLocalSocket()
    sock.connectToServer(name)
    if sock.waitForConnected(_INSTANCE_CONNECT_TIMEOUT_MS):
        sock.disconnectFromServer()
        return True
    return False


def _listen(name: str) -> QtNetwork.QLocalServer | None:
    """Claim the single-instance socket *name*; None on (unexpected) failure."""
    # A hard-killed prior instance can leave a stale socket/name behind.
    QtNetwork.QLocalServer.removeServer(name)
    server = QtNetwork.QLocalServer()
    if not server.listen(name):
        _log("launcher", f"single-instance listen failed: {server.errorString()}")
        return None
    return server


class BaseLauncher(QtWidgets.QMainWindow):
    TITLE = "Launcher"
    MIN_SIZE = (300, 200)
    LOG_TAG = "launcher"
    LOG_WINDOW_TITLE = "Launcher Log"
    START_ALL_TEXT = "Start All"
    INSTANCE_NAME: str = ""  # per-rig QLocalServer name — subclasses must set
    JUPYTER_DIR = None  # Path → build the shared JupyterLab panel
    JUPYTER_PORT: int | None = None
    _LOG_TAIL_LINES = 200

    def __init__(self, instance_server: QtNetwork.QLocalServer | None = None):
        super().__init__()
        self.setWindowTitle(self.TITLE)
        self.setMinimumSize(*self.MIN_SIZE)
        if ICON_PATH.exists():
            self.setWindowIcon(QtGui.QIcon(str(ICON_PATH)))

        self.dispatch = _Dispatcher(self)
        self._log_dialog = None
        self._config = self._load_config()
        self._init_state()

        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        self._panel_layout = QtWidgets.QVBoxLayout(central)
        # Track content: open at content size, auto-grow when panels expand
        # (data disclosure, issues list), never shrinkable into overlap.
        window_layout = self.layout()
        assert window_layout is not None
        window_layout.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetMinimumSize)

        self._build_status_panel()
        self._jupyter_panel = None
        if self.JUPYTER_DIR is not None:
            assert self.JUPYTER_PORT is not None, "JUPYTER_PORT required with JUPYTER_DIR"
            self._jupyter_panel = JupyterPanel(
                self, notebook_dir=self.JUPYTER_DIR, port=self.JUPYTER_PORT,
            )
            self._panel_layout.addWidget(self._jupyter_panel)
        self._build_pre_worker_panels()
        self._workers = self._make_workers()
        for w in self._workers:
            self._panel_layout.addWidget(w)
        self._build_post_worker_panels()
        self._panel_layout.addStretch(1)

        self._instance_server = instance_server
        if instance_server is not None:
            instance_server.setParent(self)
            instance_server.newConnection.connect(self._on_instance_ping)

        self._tray = self._build_tray()
        self._tray_color = None
        self._tray_notice_shown = False

        _log(self.LOG_TAG, "started")
        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(_TICK_MS)
        self._tick()

    @classmethod
    def run(cls) -> int:
        """Entry point: single-instance guard, then the Qt event loop."""
        assert cls.INSTANCE_NAME, f"{cls.__name__}.INSTANCE_NAME not set"
        if sys.platform == "win32":
            # Own app identity for the taskbar/notification area instead of
            # being lumped under "Python" (the host interpreter's identity).
            # Must be set before any window or tray icon is created.
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                f"SharpeLab.{cls.INSTANCE_NAME}"
            )
        app = QtWidgets.QApplication(sys.argv)
        # The window hides to tray; quitting is always explicit.
        app.setQuitOnLastWindowClosed(False)
        if _existing_instance(cls.INSTANCE_NAME):
            _log(cls.LOG_TAG, "already running — asked the live instance to show")
            return 0
        # On listen failure run unguarded rather than not at all.
        window = cls(instance_server=_listen(cls.INSTANCE_NAME))
        window.show()
        return app.exec_()

    # --- Subclass hooks -----------------------------------------------------

    def _load_config(self):
        """Return the rig config (e.g. load_config() / load_vti_config())."""
        raise NotImplementedError

    def _make_workers(self) -> list:
        """Return the rig's WorkerPanel list (panel order = UI order)."""
        raise NotImplementedError

    def _init_state(self) -> None:
        """Set subclass instance vars needed before panels/tick."""

    def _build_pre_worker_panels(self) -> None:
        """Panels added between the Jupyter panel and the worker panels."""

    def _build_post_worker_panels(self) -> None:
        """Panels added after the worker panels."""

    def _extra_issues(self) -> list[str]:
        """Non-worker issue strings to fold into the red tier."""
        return []

    def _ready_tier(self) -> tuple[str, str]:
        """(text, color) shown when there are no issues."""
        if self._jupyter_panel is not None and not self._jupyter_panel.get_status().ok:
            return ("Ready (Jupyter stopped)", "#DAA520")
        return ("Ready", "green")

    def _running_extra(self) -> list[str]:
        """Names of extra running processes for the quit prompt."""
        return []

    def _stop_extra(self) -> None:
        """Stop the extra processes named by _running_extra()."""

    # --- Status panel ---------------------------------------------------------

    def _build_status_panel(self) -> None:
        box = QtWidgets.QGroupBox("Status")
        layout = QtWidgets.QVBoxLayout(box)

        top_row = QtWidgets.QHBoxLayout()
        self._agg_label = QtWidgets.QLabel("Starting...")
        self._agg_label.setStyleSheet("color: orange; font-weight: bold;")
        top_row.addWidget(self._agg_label)
        top_row.addStretch(1)
        self._start_all_btn = QtWidgets.QPushButton(self.START_ALL_TEXT)
        self._start_all_btn.clicked.connect(self._start_all)
        top_row.addWidget(self._start_all_btn)
        layout.addLayout(top_row)

        self._issues_label = QtWidgets.QLabel("")
        self._issues_label.setStyleSheet("color: red;")
        self._issues_label.setWordWrap(True)
        self._issues_label.setVisible(False)
        layout.addWidget(self._issues_label)

        log_btn = QtWidgets.QPushButton("Log")
        log_btn.clicked.connect(self._view_log)
        layout.addWidget(log_btn)

        self._panel_layout.addWidget(box)

    def _start_all(self) -> None:
        for w in self._workers:
            if not w.running:
                w.start()

    def _tick(self) -> None:
        """Single 1s timer driving all UI updates from background state."""
        for w in self._workers:
            w.refresh_ui()
        self._refresh_status()

    def _refresh_status(self) -> None:
        """Recompute aggregate status from worker + extra component health."""
        issues = []
        for w in self._workers:
            s = w.get_status()
            if not s.ok:
                issues.append(f"{w.name}: {s.message}")
        issues.extend(self._extra_issues())

        if issues:
            text, color = "Issues", "red"
            self._issues_label.setText("\n".join(issues))
            self._issues_label.setVisible(True)
        else:
            text, color = self._ready_tier()
            self._issues_label.setVisible(False)
        self._agg_label.setText(text)
        self._agg_label.setStyleSheet(f"color: {color}; font-weight: bold;")

        all_running = all(w.running for w in self._workers)
        self._start_all_btn.setEnabled(not all_running)

        tooltip = f"{self.TITLE} — {text}"
        if issues:
            tooltip += "\n" + "\n".join(issues)
        self._update_tray(color, tooltip)

    # --- Tray -----------------------------------------------------------------

    def _build_tray(self) -> QtWidgets.QSystemTrayIcon | None:
        if not QtWidgets.QSystemTrayIcon.isSystemTrayAvailable():
            _log(self.LOG_TAG, "no system tray available — close will quit")
            return None
        tray = QtWidgets.QSystemTrayIcon(QtGui.QIcon(str(ICON_PATH)), self)
        menu = QtWidgets.QMenu(self)
        menu.addAction("Show", self._show_window)
        menu.addAction("Quit", self._quit)
        tray.setContextMenu(menu)
        tray.activated.connect(self._on_tray_activated)
        tray.setToolTip(self.TITLE)
        tray.show()
        return tray

    def _on_tray_activated(self, reason) -> None:
        if reason in (
            QtWidgets.QSystemTrayIcon.ActivationReason.Trigger,
            QtWidgets.QSystemTrayIcon.ActivationReason.DoubleClick,
        ):
            self._show_window()

    def _update_tray(self, color: str, tooltip: str) -> None:
        """Refresh the tray tooltip and the health-colored status dot."""
        if self._tray is None:
            return
        self._tray.setToolTip(tooltip)
        if color == self._tray_color:
            return
        self._tray_color = color
        pixmap = QtGui.QPixmap(str(ICON_PATH)).scaled(
            64, 64,
            QtCore.Qt.AspectRatioMode.KeepAspectRatio,
            QtCore.Qt.TransformationMode.SmoothTransformation,
        )
        if pixmap.isNull():
            return
        painter = QtGui.QPainter(pixmap)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        painter.setBrush(QtGui.QColor(color))
        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        d = pixmap.width() * 0.42
        painter.drawEllipse(QtCore.QRectF(
            pixmap.width() - d, pixmap.height() - d, d, d,
        ))
        painter.end()
        self._tray.setIcon(QtGui.QIcon(pixmap))

    def _show_window(self) -> None:
        self.showNormal()
        self.raise_()
        self.activateWindow()

    def _on_instance_ping(self) -> None:
        """A second launch connected to our socket: show the window."""
        while True:
            sock = self._instance_server.nextPendingConnection()
            if sock is None:
                break
            sock.deleteLater()
        _log(self.LOG_TAG, "second launch detected — showing window")
        self._show_window()

    # --- Log viewer -------------------------------------------------------------

    def _view_log(self) -> None:
        if self._log_dialog is not None and self._log_dialog.isVisible():
            self._log_dialog.raise_()
            self._log_dialog.activateWindow()
            return

        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle(self.LOG_WINDOW_TITLE)
        dialog.resize(600, 400)
        text = QtWidgets.QPlainTextEdit(dialog)
        text.setReadOnly(True)
        text.setLineWrapMode(QtWidgets.QPlainTextEdit.LineWrapMode.NoWrap)
        layout = QtWidgets.QVBoxLayout(dialog)
        layout.addWidget(text)

        last_size = [-1]

        def refresh():
            try:
                size = LOG_PATH.stat().st_size
            except FileNotFoundError:
                text.setPlainText("(no log yet)")
                return
            if size == last_size[0]:
                return
            last_size[0] = size
            try:
                tail = tail_lines(LOG_PATH, self._LOG_TAIL_LINES)
            except OSError:
                tail = "(error reading log)"
            text.setPlainText(tail)
            scrollbar = text.verticalScrollBar()
            assert scrollbar is not None
            scrollbar.setValue(scrollbar.maximum())

        timer = QtCore.QTimer(dialog)
        timer.timeout.connect(refresh)
        timer.start(_TICK_MS)
        refresh()

        self._log_dialog = dialog
        dialog.show()

    # --- Close / quit -----------------------------------------------------------

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        """X button: hide to tray. Without a tray, conventional confirm-quit."""
        if self._tray is not None:
            event.ignore()
            self.hide()
            if not self._tray_notice_shown:
                self._tray_notice_shown = True
                self._tray.showMessage(
                    self.TITLE,
                    "Still running in the tray. "
                    "Click the tray icon to show, right-click to quit.",
                )
            return
        if self._confirm_and_stop():
            event.accept()
            QtWidgets.QApplication.quit()
        else:
            event.ignore()

    def _quit(self) -> None:
        """Tray-menu Quit: the deliberate teardown path."""
        if not self._confirm_and_stop():
            return
        if self._tray is not None:
            self._tray.hide()
        QtWidgets.QApplication.quit()

    def _confirm_and_stop(self) -> bool:
        """The close handshake: confirm if anything runs, then stop everything."""
        running_names = []
        if self._jupyter_panel is not None and self._jupyter_panel.running:
            running_names.append("JupyterLab")
        running_names += self._running_extra()
        running_names += [w.name for w in self._workers if w.running]
        if running_names:
            buttons = QtWidgets.QMessageBox.StandardButton
            resp = QtWidgets.QMessageBox.question(
                self,
                "Processes Running",
                f"{', '.join(running_names)} still running. Stop and quit?",
                buttons.Ok | buttons.Cancel,
                buttons.Ok,
            )
            if resp != buttons.Ok:
                return False
            self._stop_extra()
        if self._jupyter_panel is not None:
            self._jupyter_panel.shutdown()
        for w in self._workers:
            w.shutdown()
        _log(self.LOG_TAG, "quit")
        return True
