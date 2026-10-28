"""Qt panel for the QCS heater worker (workers/qcs_heater.py).

One row per heater channel: readback lamp + live state, µA setpoint entry,
Apply, On, Off. Lamps and the "now" text are driven purely by the worker's
[data] readback — never by what was last commanded. Command results
(clamped/rejected/failed) surface in a result line; rejections are never
silent. Controls unlock only while the worker is running.

Commands go to the worker as JSON lines over its piped stdin, addressed by
channel *name* so the panel stays decoupled from the hardware numbering.
"""

from __future__ import annotations

import json

from PyQt5 import QtWidgets

from gui.utils import main_thread_only
from gui.qt.worker_panel import WorkerPanel

# Display order; must match the worker map's channel names.
CHANNEL_NAMES = ("3K", "Still", "MC")
MAX_UA = 15000  # spinbox bound only — the driver enforces the real clamp


class QcsHeaterPanel(WorkerPanel):
    """WorkerPanel + per-channel heater controls over the stdin channel."""

    STDIN_PIPE = True

    def _build_extra_controls(self, layout: QtWidgets.QVBoxLayout) -> None:
        self._rows: dict[str, dict] = {}
        grid = QtWidgets.QGridLayout()
        grid.setColumnStretch(2, 1)
        for i, name in enumerate(CHANNEL_NAMES):
            lamp = QtWidgets.QLabel("●")
            lamp.setStyleSheet("color: gray;")
            now = QtWidgets.QLabel("—")
            now.setStyleSheet("color: gray;")
            spin = QtWidgets.QSpinBox()
            spin.setRange(0, MAX_UA)
            spin.setSuffix(" µA")
            spin.setSingleStep(100)
            apply_btn = QtWidgets.QPushButton("Apply")
            on_btn = QtWidgets.QPushButton("On")
            off_btn = QtWidgets.QPushButton("Off")
            # Zero-arg lambdas (see WorkerPanel start/stop buttons).
            apply_btn.clicked.connect(lambda _=False, n=name: self._apply(n))
            on_btn.clicked.connect(lambda _=False, n=name: self._set_on(n, True))
            off_btn.clicked.connect(lambda _=False, n=name: self._set_on(n, False))

            grid.addWidget(lamp, i, 0)
            grid.addWidget(QtWidgets.QLabel(name), i, 1)
            grid.addWidget(now, i, 2)
            grid.addWidget(spin, i, 3)
            grid.addWidget(apply_btn, i, 4)
            grid.addWidget(on_btn, i, 5)
            grid.addWidget(off_btn, i, 6)
            self._rows[name] = {
                "lamp": lamp, "now": now, "spin": spin,
                "buttons": (apply_btn, on_btn, off_btn),
            }
        layout.addLayout(grid)

        self._cmd_result = QtWidgets.QLabel("")
        self._cmd_result.setStyleSheet("color: gray;")
        self._cmd_result.setVisible(False)
        self._cmd_result.setWordWrap(True)
        layout.addWidget(self._cmd_result)

        self._set_controls_enabled(False)

    # -- control lock follows worker lifecycle --

    def _set_controls_enabled(self, enabled: bool) -> None:
        for row in self._rows.values():
            row["spin"].setEnabled(enabled)
            for btn in row["buttons"]:
                btn.setEnabled(enabled)

    @main_thread_only
    def _on_ready(self) -> None:
        super()._on_ready()
        self._set_controls_enabled(True)

    @main_thread_only
    def _on_controls_reset(self) -> None:
        self._set_controls_enabled(False)
        for row in self._rows.values():
            row["lamp"].setStyleSheet("color: gray;")
            row["now"].setText("—")
            row["now"].setStyleSheet("color: gray;")
        self._cmd_result.setVisible(False)

    # -- commands --

    def _send(self, cmd: dict) -> None:
        if not self._proc.send_line(json.dumps(cmd)):
            self._show_cmd_result("command not sent — worker not running", ok=False)

    def _apply(self, name: str) -> None:
        self._send({"cmd": "set_current", "channel": name,
                    "ua": self._rows[name]["spin"].value()})

    def _set_on(self, name: str, on: bool) -> None:
        self._send({"cmd": "set_on", "channel": name, "on": on})

    @main_thread_only
    def _show_cmd_result(self, text: str, *, ok: bool) -> None:
        self._cmd_result.setText(text)
        self._cmd_result.setStyleSheet(f"color: {'gray' if ok else 'red'};")
        self._cmd_result.setVisible(True)

    # -- readback display --

    @main_thread_only
    def _on_data(self, payload: str) -> None:
        super()._on_data(payload)
        try:
            data = json.loads(payload)
        except json.JSONDecodeError:
            return

        for name, ch in data.get("channels", {}).items():
            row = self._rows.get(name)
            if row is None:
                continue
            on = ch.get("on")  # readback: True / False / None (unknown)
            row["lamp"].setStyleSheet(f"color: {'orange' if on else 'gray'};")
            set_ua = ch.get("set_ua")
            set_str = "?" if set_ua is None else f"{set_ua:g} µA"
            rng = f" ({ch['range']})" if ch.get("range") else ""
            state = "ON" if on else ("off" if on is False else "?")
            row["now"].setText(f"{state} · {set_str}{rng}")
            # Palette default when on (readable on any theme), gray otherwise.
            row["now"].setStyleSheet("" if on else "color: gray;")

        last_cmd = data.get("last_cmd")
        if last_cmd is not None:
            ok = bool(last_cmd.get("ok"))
            self._show_cmd_result(
                f"{last_cmd.get('cmd')}: {last_cmd.get('detail', '')}", ok=ok
            )
