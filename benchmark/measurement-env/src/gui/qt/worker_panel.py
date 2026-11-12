"""Reusable Qt worker panel: Start/Stop buttons, live data, InfluxDB health.

Port of gui.worker_panel.WorkerPanel; reuses the toolkit-neutral
ManagedProcess (via the launcher's dispatch) and InfluxHealthPoller.
"""

from __future__ import annotations

import json

from PyQt5 import QtWidgets

from core.config import BaseConfig
from gui.influx_health import InfluxHealthPoller
from gui.managed_process import ManagedProcess
from gui.utils import ComponentStatus, _log, main_thread_only


class WorkerPanel(QtWidgets.QGroupBox):
    """Reusable worker panel: Start/Stop buttons, live data, InfluxDB health."""

    # Subclasses of command-taking workers set this to get a piped stdin
    # (then send lines via self._proc.send_line()).
    STDIN_PIPE = False

    def __init__(
        self,
        launcher,
        *,
        name: str,
        desc: str,
        tag: str,
        cmd: list[str],
        health_key: str,
        health_measurement: str,
        config: BaseConfig,
    ) -> None:
        super().__init__(f"{name} - {desc}")
        self._launcher = launcher
        self._proc = ManagedProcess(tag)
        self._cmd = cmd
        self._name = name
        self._process_status = ComponentStatus(ok=False, message="not running")

        layout = QtWidgets.QVBoxLayout(self)

        status_row = QtWidgets.QHBoxLayout()
        self._dot_label = QtWidgets.QLabel("●")
        self._dot_label.setStyleSheet("color: gray;")
        status_row.addWidget(self._dot_label)
        status_row.addWidget(QtWidgets.QLabel("Status:"))
        self._status_label = QtWidgets.QLabel("Stopped")
        self._status_label.setStyleSheet("color: gray;")
        status_row.addWidget(self._status_label)
        self._summary_label = QtWidgets.QLabel("")
        self._summary_label.setStyleSheet("color: gray;")
        self._summary_label.setVisible(False)
        status_row.addWidget(self._summary_label)
        status_row.addStretch(1)
        # Zero-arg lambdas: clicked emits a checked bool, and PyQt5 delivers
        # it to the @main_thread_only wrapper's *args — TypeError → qFatal.
        self._start_btn = QtWidgets.QPushButton("Start")
        self._start_btn.clicked.connect(lambda: self.start())
        status_row.addWidget(self._start_btn)
        self._stop_btn = QtWidgets.QPushButton("Stop")
        self._stop_btn.setEnabled(False)
        self._stop_btn.clicked.connect(lambda: self.stop())
        status_row.addWidget(self._stop_btn)
        layout.addLayout(status_row)

        self._build_extra_controls(layout)

        # Data disclosure — hidden until first [data]
        data_row = QtWidgets.QHBoxLayout()
        self._data_toggle_btn = QtWidgets.QPushButton("▶ Data")
        self._data_toggle_btn.setCheckable(True)
        self._data_toggle_btn.setVisible(False)
        self._data_toggle_btn.toggled.connect(self._toggle_data)
        data_row.addWidget(self._data_toggle_btn)
        data_row.addStretch(1)
        layout.addLayout(data_row)

        self._data_label = QtWidgets.QLabel("")
        self._data_label.setWordWrap(True)
        self._data_label.setVisible(False)
        layout.addWidget(self._data_label)

        influx_row = QtWidgets.QHBoxLayout()
        influx_row.addWidget(QtWidgets.QLabel("InfluxDB:"))
        self._influx_label = QtWidgets.QLabel("—")
        self._influx_label.setStyleSheet("color: gray;")
        influx_row.addWidget(self._influx_label)
        influx_row.addStretch(1)
        layout.addLayout(influx_row)

        self._poller = self._create_influx_health_poller(
            health_key, health_measurement, config,
        )
        if self._poller is not None:
            self._poller.start()

    def _create_influx_health_poller(
        self,
        health_key: str,
        health_measurement: str,
        config: BaseConfig,
    ) -> InfluxHealthPoller | None:
        """Create an InfluxDB poller from config, or None if health key not defined."""
        health_entry = config.health.get(health_key)
        if health_entry is None:
            self._influx_label.setText("not configured")
            _log("health", f"{health_key}: no [health.{health_key}] in config")
            return None

        influx = config.influxdb
        return InfluxHealthPoller(
            influx.url, influx.token, influx.org, influx.bucket,
            health_measurement, health_entry.metrics, health_entry.threshold,
        )

    @main_thread_only
    def _configure_influx_ui(self) -> None:
        """Update InfluxDB age label from poller state."""
        poller = self._poller
        if poller is None:
            return

        shown = poller.display()
        self._influx_label.setText(shown.text)
        self._influx_label.setStyleSheet(
            f"color: {'green' if shown.ok else 'red'};"
        )

    @main_thread_only
    def refresh_ui(self) -> None:
        """Called by the launcher tick to update UI from background state."""
        self._configure_influx_ui()

    def get_status(self) -> ComponentStatus:
        """Return combined process + InfluxDB health for aggregate roll-up."""
        if not self._process_status.ok:
            return self._process_status

        poller = self._poller
        if poller is None:
            return ComponentStatus(ok=False, message="influx not configured")

        shown = poller.display()
        if shown.ok:
            return ComponentStatus(ok=True)
        return ComponentStatus(ok=False, message=f"influx {shown.summary}")

    @main_thread_only
    def _set_status(self, text: str, color: str) -> None:
        self._status_label.setText(text)
        self._status_label.setStyleSheet(f"color: {color};")
        self._dot_label.setStyleSheet(f"color: {color};")

    def _get_cmd(self) -> list[str]:
        """Return the command to launch. Override for dynamic commands."""
        return self._cmd

    def _build_extra_controls(self, layout: QtWidgets.QVBoxLayout) -> None:
        """Hook for subclasses to add controls between status and data rows."""

    @main_thread_only
    def _on_controls_activate(self) -> None:
        """Hook called when worker starts — lock subclass controls."""

    @main_thread_only
    def _on_controls_reset(self) -> None:
        """Hook called when worker stops/fails/dies — unlock subclass controls."""

    @main_thread_only
    def start(self) -> None:
        self._on_controls_activate()
        self._start_btn.setEnabled(False)
        self._stop_btn.setEnabled(True)
        self._set_status("Starting...", "orange")

        self._proc.start_with_output(
            cmd=self._get_cmd(),
            dispatch=self._launcher.dispatch,
            on_ready=self._on_ready,
            on_failed=self._on_failed,
            on_died=self._on_died,
            on_waiting=self._on_waiting,
            on_data=self._on_data,
            stdin_pipe=self.STDIN_PIPE,
        )

    @main_thread_only
    def _on_waiting(self) -> None:
        self._set_status("Waiting for data...", "orange")
        self._process_status = ComponentStatus(ok=False, message="waiting for data")

    @main_thread_only
    def _on_ready(self) -> None:
        self._set_status("Running", "green")
        self._process_status = ComponentStatus(ok=True)

    @main_thread_only
    def _on_failed(self, rc: int | None) -> None:
        self._set_status(f"Failed to start (rc={rc})", "red")
        self._start_btn.setEnabled(True)
        self._stop_btn.setEnabled(False)
        self._on_controls_reset()
        self._process_status = ComponentStatus(ok=False, message=f"failed to start (rc={rc})")

    @main_thread_only
    def _on_died(self, rc: int | None) -> None:
        self._set_status(f"Died (rc={rc})", "red")
        self._start_btn.setEnabled(True)
        self._stop_btn.setEnabled(False)
        self._on_controls_reset()
        self._hide_data()
        self._process_status = ComponentStatus(ok=False, message=f"died (rc={rc})")

    @main_thread_only
    def _on_stopped(self) -> None:
        self._set_status("Stopped", "gray")
        self._start_btn.setEnabled(True)
        self._stop_btn.setEnabled(False)
        self._on_controls_reset()
        self._hide_data()
        self._process_status = ComponentStatus(ok=False, message="not running")

    @main_thread_only
    def _on_data(self, payload: str) -> None:
        try:
            data: dict[str, object] = json.loads(payload)
        except json.JSONDecodeError:
            return
        summary = data.pop("_summary", None)
        if summary is not None:
            self._summary_label.setText(f"— {summary}")
            self._summary_label.setVisible(True)
        parts = [f"{k}: {v}" for k, v in data.items()]
        self._data_label.setText("\n".join(parts))
        # Show disclosure button on first data
        if parts and not self._data_toggle_btn.isVisible():
            self._data_toggle_btn.setVisible(True)

    @main_thread_only
    def _toggle_data(self, expanded: bool) -> None:
        self._data_toggle_btn.setText("▼ Data" if expanded else "▶ Data")
        self._data_label.setVisible(expanded)

    @main_thread_only
    def _hide_data(self) -> None:
        self._data_toggle_btn.setChecked(False)
        self._data_toggle_btn.setVisible(False)
        self._data_label.setVisible(False)
        self._summary_label.setText("")
        self._summary_label.setVisible(False)

    @main_thread_only
    def stop(self) -> None:
        self._proc.stop()
        self._on_stopped()

    def shutdown(self) -> None:
        """Stop process and poller. Safe to call whether running or not.

        (Named shutdown, not destroy — QWidget.destroy() is taken.)
        """
        self._proc.stop()
        if self._poller is not None:
            self._poller.stop()

    @property
    def running(self) -> bool:
        return self._proc.running

    @property
    def name(self) -> str:
        return self._name
