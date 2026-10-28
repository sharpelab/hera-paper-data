"""Sweep progress in a standalone Qt window (out of the notebook cell).

``QtProgress`` is a tqdm-shaped progress factory for ``sweep.set_progress``: the
sweep core calls it to wrap each setpoint loop, and it renders the bars in a
separate Qt process instead of the notebook output — the same out-of-kernel
model as ``sweep``'s live ``.plot()`` window.

One persistent child process hosts the window, with a bar per loop *position*
(0 = outer/slow, 1 = inner/fast). The window is reused across sweeps and
relaunched if the operator closed it. Progress is cosmetic: every IPC failure
is swallowed so a dead or closed window can never interrupt a measurement.
"""

from __future__ import annotations

import enum
import multiprocessing
import multiprocessing.connection
import signal
import time
from typing import Any, Iterable, Iterator

from PyQt5 import QtCore, QtWidgets

_TICK_MS = 40  # child pipe-drain / repaint cadence
_SEND_INTERVAL = 0.1  # parent update throttle (s)
_RUNNING = "#1976d2"
_DONE = "#4caf50"
_ABORTED = "#f44336"


class _Action(enum.Enum):
    START = "start"
    UPDATE = "update"
    DONE = "done"
    SHUTDOWN = "shutdown"


def _fmt_time(seconds: float) -> str:
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


# ---------------------------------------------------------------------------
# Child process: the Qt window
# ---------------------------------------------------------------------------


class _RowState:
    def __init__(self) -> None:
        self.total: int | None = None
        self.n: int = 0
        self.start: float = 0.0
        self.dirty: bool = False


class _Window(QtWidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Sweep progress")
        layout = QtWidgets.QVBoxLayout(self)
        layout.addStretch(1)
        self._bars: dict[int, QtWidgets.QProgressBar] = {}
        self._stats: dict[int, QtWidgets.QLabel] = {}
        self._containers: dict[int, QtWidgets.QWidget] = {}
        self._rows: dict[int, _RowState] = {}
        for position in (0, 1):
            container = QtWidgets.QWidget()
            hbox = QtWidgets.QHBoxLayout(container)
            hbox.setContentsMargins(0, 0, 0, 0)
            bar = QtWidgets.QProgressBar()
            bar.setMinimumWidth(280)
            stats = QtWidgets.QLabel()
            stats.setStyleSheet("font-family: monospace;")
            hbox.addWidget(bar)
            hbox.addWidget(stats)
            layout.addWidget(container)
            container.setVisible(position == 0)
            self._bars[position] = bar
            self._stats[position] = stats
            self._containers[position] = container
            self._rows[position] = _RowState()
        layout.addStretch(1)
        self.resize(440, 90)

    def apply(self, msg: dict[str, Any]) -> None:
        action = msg["action"]
        position = msg.get("position", 0)
        if action is _Action.START:
            row = self._rows[position]
            row.total = msg["total"]
            row.n = 0
            row.start = time.monotonic()
            row.dirty = True
            bar = self._bars[position]
            bar.setRange(0, row.total or 0)
            bar.setValue(0)
            self._color(position, _RUNNING)
            self._containers[position].setVisible(True)
        elif action is _Action.UPDATE:
            row = self._rows[position]
            row.n = msg["n"]
            row.dirty = True
        elif action is _Action.DONE:
            if msg.get("leave", True):
                self._color(position, _DONE if msg.get("completed") else _ABORTED)
                self._rows[position].dirty = True
            else:
                self._containers[position].setVisible(False)
        elif action is _Action.SHUTDOWN:
            QtWidgets.QApplication.quit()

    def refresh(self) -> None:
        for position, row in self._rows.items():
            if not row.dirty:
                continue
            row.dirty = False
            bar = self._bars[position]
            if row.total:
                bar.setRange(0, row.total)
                bar.setValue(min(row.n, row.total))
            elapsed = time.monotonic() - row.start
            rate = row.n / elapsed if elapsed > 0 else 0.0
            eta = (row.total - row.n) / rate if rate > 0 and row.total else 0.0
            count = f"{row.n}/{row.total}" if row.total else str(row.n)
            rate_s = f"{rate:.2f}it/s" if rate < 100 else f"{rate:.0f}it/s"
            self._stats[position].setText(
                f"{count} [{_fmt_time(elapsed)}<{_fmt_time(eta)}, {rate_s}]"
            )

    def _color(self, position: int, color: str) -> None:
        self._bars[position].setStyleSheet(
            "QProgressBar { color: #102a43; font-weight: 600; text-align: center; }"
            f"QProgressBar::chunk {{ background-color: {color}; }}"
        )


def _progress_loop(conn: multiprocessing.connection.Connection) -> None:
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    window = _Window()
    window.show()

    def drain() -> None:
        try:
            while conn.poll():
                window.apply(conn.recv())
        except (EOFError, OSError):
            app.quit()
            return
        window.refresh()

    timer = QtCore.QTimer()
    timer.timeout.connect(drain)
    timer.start(_TICK_MS)
    app.exec_()


# ---------------------------------------------------------------------------
# Parent (kernel) side: the tqdm-shaped factory
# ---------------------------------------------------------------------------


class QtProgress:
    """A ``sweep.set_progress`` factory that draws bars in a popup Qt window."""

    def __init__(self) -> None:
        self._ctx = multiprocessing.get_context("spawn")
        self._proc: multiprocessing.process.BaseProcess | None = None
        self._pipe: multiprocessing.connection.Connection | None = None
        # Bars currently in flight (position -> {total, leave, n}), replayed
        # onto a fresh window after a relaunch so an interrupted/closed window
        # comes back coherent instead of blank.
        self._active: dict[int, dict[str, Any]] = {}

    def _ensure(self) -> None:
        """Spawn the window process, or relaunch it if it was closed."""
        if self._proc is not None and self._proc.is_alive():
            return
        parent, child = self._ctx.Pipe()
        self._proc = self._ctx.Process(
            target=_progress_loop, args=(child,), daemon=True
        )
        self._proc.start()
        self._pipe = parent
        for pos, st in self._active.items():
            self._send(
                {
                    "action": _Action.START,
                    "position": pos,
                    "total": st["total"],
                    "leave": st["leave"],
                }
            )
            if st["n"]:
                self._send(
                    {"action": _Action.UPDATE, "position": pos, "n": st["n"]}
                )

    def _send(self, msg: dict[str, Any]) -> None:
        if self._pipe is None:
            return
        try:
            self._pipe.send(msg)
        except (BrokenPipeError, OSError, EOFError, ValueError):
            # Window gone (closed/crashed). Drop the handle so the next sweep
            # relaunches; never let a cosmetic failure reach the measurement.
            self._proc = None
            self._pipe = None

    def __call__(
        self,
        iterable: Iterable[Any],
        *,
        total: int | None = None,
        position: int = 0,
        leave: bool = True,
        **kwargs: Any,
    ) -> Iterator[Any]:
        self._ensure()
        if total is None:
            try:
                total = len(iterable)  # type: ignore[arg-type]
            except TypeError:
                total = None
        self._active[position] = {"total": total, "leave": leave, "n": 0}
        self._send(
            {
                "action": _Action.START,
                "position": position,
                "total": total,
                "leave": leave,
            }
        )
        n = 0
        last = 0.0
        completed = False
        try:
            for item in iterable:
                yield item
                n += 1
                self._active[position]["n"] = n
                now = time.monotonic()
                if now - last >= _SEND_INTERVAL:
                    self._ensure()  # relaunch + replay if the window was closed
                    self._send(
                        {"action": _Action.UPDATE, "position": position, "n": n}
                    )
                    last = now
            completed = True
        finally:
            self._active.pop(position, None)
            self._send({"action": _Action.UPDATE, "position": position, "n": n})
            self._send(
                {
                    "action": _Action.DONE,
                    "position": position,
                    "completed": completed,
                    "leave": leave,
                }
            )
