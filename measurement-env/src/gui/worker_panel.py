"""Reusable worker panel: Start/Stop buttons, live data, InfluxDB health."""

from __future__ import annotations

import json
import sys
import tkinter as tk
from datetime import datetime, timezone
from tkinter import ttk

from workers.avs_calibration import SENSORS_PROBE1

from core.config import BaseConfig

from .influx_health import InfluxHealthPoller
from .managed_process import ManagedProcess
from .utils import ComponentStatus, _log, main_thread_only


def _age_str(seconds: float) -> str:
    """Format an age in seconds as a human-readable string."""
    if seconds < 60:
        return f"{int(seconds)}s ago"
    if seconds < 3600:
        return f"{int(seconds // 60)}m ago"
    return f"{int(seconds // 3600)}h ago"


class WorkerPanel:
    """Reusable worker panel: Start/Stop buttons, live data, InfluxDB health."""

    def __init__(
        self,
        parent: tk.Misc,
        *,
        title: str,
        tag: str,
        cmd: list[str],
        health_key: str,
        health_measurement: str,
        status_name: str,
        config: BaseConfig,
    ) -> None:
        self._parent = parent
        self._proc = ManagedProcess(tag)
        self._cmd = cmd
        self._status_name = status_name
        self._process_status = ComponentStatus(ok=False, message="not running")

        # Build UI — dot+title as labelwidget, buttons placed at top-right
        title_frame = ttk.Frame(parent)
        self._dot_label = ttk.Label(title_frame, text="\u25cf", foreground="gray")
        self._dot_label.pack(side="left")
        ttk.Label(title_frame, text=f" {title} ").pack(side="left")

        frame = ttk.LabelFrame(parent, labelwidget=title_frame, padding=10)
        frame.pack(fill="x", padx=10, pady=(5, 5), anchor="n")

        # Right-aligned buttons placed on the border
        btn_frame = ttk.Frame(frame)
        self._stop_btn = ttk.Button(
            btn_frame, text="Stop", command=self.stop, state="disabled", width=5,
        )
        self._stop_btn.pack(side="right")
        self._start_btn = ttk.Button(
            btn_frame, text="Start", command=self.start, width=5,
        )
        self._start_btn.pack(side="right", padx=(0, 2))
        btn_frame.place(relx=1.0, y=-30, x=-5, anchor="ne")

        status_row = ttk.Frame(frame)
        status_row.pack(fill="x")

        ttk.Label(status_row, text="Status:").pack(side="left")
        self._status_var = tk.StringVar(value="Stopped")
        self._status_label = ttk.Label(
            status_row, textvariable=self._status_var, foreground="gray",
        )
        self._status_label.pack(side="left", padx=(5, 0))

        self._summary_var = tk.StringVar()
        self._summary_label = ttk.Label(
            status_row, textvariable=self._summary_var, foreground="gray",
        )
        # Packed on first _summary data

        self._build_extra_controls(frame)

        self._data_row = ttk.Frame(frame)
        # Hidden until first [data]; not packed yet

        self._data_expanded = False
        self._data_toggle_btn = ttk.Button(
            self._data_row, text="\u25b6 Data", width=8,
            command=self._toggle_data,
        )
        self._data_toggle_btn.pack(side="left")

        self._data_var = tk.StringVar()
        self._data_label = ttk.Label(
            frame, textvariable=self._data_var, justify="left", wraplength=280,
        )

        influx_row = ttk.Frame(frame)
        influx_row.pack(fill="x", pady=(5, 0))

        ttk.Label(influx_row, text="InfluxDB:").pack(side="left")
        self._influx_var = tk.StringVar(value="\u2014")
        self._influx_label = ttk.Label(
            influx_row, textvariable=self._influx_var, foreground="gray",
        )
        self._influx_label.pack(side="left", padx=(5, 0))

        # InfluxDB health poller
        self._poller = self._create_influx_health_poller(health_key, health_measurement, config)
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
            self._influx_var.set("not configured")
            _log("health", f"{health_key}: no [health.{health_key}] in config")
            return None

        influx = config.influxdb
        return InfluxHealthPoller(
            influx.url, influx.token, influx.org, influx.bucket,
            health_measurement, health_entry.metric, health_entry.threshold,
        )

    @main_thread_only
    def _configure_influx_ui(self) -> None:
        """Update InfluxDB age label from poller state."""
        poller = self._poller
        if poller is None:
            return

        lw = poller.last_write
        if lw is not None:
            local = lw.astimezone()
            age = (datetime.now(timezone.utc) - lw).total_seconds()
            self._influx_var.set(f"{local.strftime('%H:%M:%S')} ({_age_str(age)})")
            self._influx_label.configure(
                foreground="green" if poller.fresh else "red",
            )
        elif poller.error is not None:
            self._influx_var.set("error")
            self._influx_label.configure(foreground="red")
        else:
            self._influx_var.set("no data")
            self._influx_label.configure(foreground="red")

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

        lw = poller.last_write
        if lw is None:
            if poller.error is not None:
                return ComponentStatus(ok=False, message="influx error")
            return ComponentStatus(ok=False, message="influx no data")

        if poller.fresh:
            return ComponentStatus(ok=True)

        age = (datetime.now(timezone.utc) - lw).total_seconds()
        return ComponentStatus(ok=False, message=f"influx stale ({_age_str(age)})")

    @main_thread_only
    def _set_status(self, text: str, color: str) -> None:
        self._status_var.set(text)
        self._status_label.configure(foreground=color)
        self._dot_label.configure(foreground=color)

    def _get_cmd(self) -> list[str]:
        """Return the command to launch. Override for dynamic commands."""
        return self._cmd

    def _build_extra_controls(self, frame: ttk.LabelFrame) -> None:
        """Hook for subclasses to add controls between status and buttons."""

    @main_thread_only
    def _on_controls_activate(self) -> None:
        """Hook called when worker starts — lock subclass controls."""

    @main_thread_only
    def _on_controls_reset(self) -> None:
        """Hook called when worker stops/fails/dies — unlock subclass controls."""

    @main_thread_only
    def start(self) -> None:
        self._on_controls_activate()
        self._start_btn.configure(state="disabled")
        self._stop_btn.configure(state="normal")
        self._set_status("Starting...", "orange")

        root = self._parent.winfo_toplevel()
        self._proc.start_with_output(
            cmd=self._get_cmd(),
            dispatch=lambda cb: root.after(0, cb),
            on_ready=self._on_ready,
            on_failed=self._on_failed,
            on_died=self._on_died,
            on_waiting=self._on_waiting,
            on_data=self._on_data,
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
        self._start_btn.configure(state="normal")
        self._stop_btn.configure(state="disabled")
        self._on_controls_reset()
        self._process_status = ComponentStatus(ok=False, message=f"failed to start (rc={rc})")

    @main_thread_only
    def _on_died(self, rc: int | None) -> None:
        self._set_status(f"Died (rc={rc})", "red")
        self._start_btn.configure(state="normal")
        self._stop_btn.configure(state="disabled")
        self._on_controls_reset()
        self._hide_data()
        self._process_status = ComponentStatus(ok=False, message=f"died (rc={rc})")

    @main_thread_only
    def _on_stopped(self) -> None:
        self._set_status("Stopped", "gray")
        self._start_btn.configure(state="normal")
        self._stop_btn.configure(state="disabled")
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
            self._summary_var.set(f"\u2014 {summary}")
            if not self._summary_label.winfo_ismapped():
                self._summary_label.pack(side="left", padx=(5, 0))
        parts = [f"{k}: {v}" for k, v in data.items()]
        self._data_var.set("\n".join(parts))
        # Show disclosure row on first data
        if parts and not self._data_row.winfo_ismapped():
            self._data_row.pack(fill="x", pady=(5, 0))

    @main_thread_only
    def _toggle_data(self) -> None:
        self._data_expanded = not self._data_expanded
        if self._data_expanded:
            self._data_toggle_btn.configure(text="\u25bc Data")
            self._data_label.pack(fill="x", pady=(2, 0))
        else:
            self._data_toggle_btn.configure(text="\u25b6 Data")
            self._data_label.pack_forget()

    @main_thread_only
    def _hide_data(self) -> None:
        self._data_expanded = False
        self._data_toggle_btn.configure(text="\u25b6 Data")
        self._data_label.pack_forget()
        self._data_row.pack_forget()
        self._summary_var.set("")
        self._summary_label.pack_forget()

    @main_thread_only
    def stop(self) -> None:
        self._proc.stop()
        self._on_stopped()

    def destroy(self) -> None:
        """Stop process and poller. Safe to call whether running or not."""
        self._proc.stop()
        if self._poller is not None:
            self._poller.stop()

    @property
    def running(self) -> bool:
        return self._proc.running

    @property
    def name(self) -> str:
        return self._status_name


class ProbeWorkerPanel(WorkerPanel):
    """AVS probe panel with parameter dropdowns."""

    _CHANNELS: list[str] = [f"{i}: {SENSORS_PROBE1[i][0]}" for i in range(6)]

    def __init__(self, parent: tk.Misc, **kwargs: object) -> None:
        self._probe_var = tk.StringVar(value="1")
        self._channel_var = tk.StringVar(value="3: MixingCh_low")
        self._exc_var = tk.StringVar(value="1")

        kwargs.setdefault("cmd", [])
        super().__init__(parent, **kwargs)  # type: ignore[arg-type]

    def _build_extra_controls(self, frame: ttk.LabelFrame) -> None:
        row = ttk.Frame(frame)
        row.pack(fill="x", pady=(5, 0))

        ttk.Label(row, text="Probe:").pack(side="left")
        self._probe_combo = ttk.Combobox(
            row, textvariable=self._probe_var,
            values=["1", "2"], width=3, state="readonly",
        )
        self._probe_combo.pack(side="left", padx=(2, 10))

        ttk.Label(row, text="Channel:").pack(side="left")
        self._channel_combo = ttk.Combobox(
            row, textvariable=self._channel_var,
            values=self._CHANNELS, width=16, state="readonly",
        )
        self._channel_combo.pack(side="left", padx=(2, 10))

        ttk.Label(row, text="EXC:").pack(side="left")
        self._exc_combo = ttk.Combobox(
            row, textvariable=self._exc_var,
            values=["1", "2", "3"], width=3, state="readonly",
        )
        self._exc_combo.pack(side="left", padx=(2, 0))

        self._combos = [self._probe_combo, self._channel_combo, self._exc_combo]

    def _get_cmd(self) -> list[str]:
        ch = self._channel_var.get().split(":")[0]
        return [
            sys.executable, "-m", "workers.avs_probe",
            "--probe", self._probe_var.get(),
            "--channel", ch,
            "--excitation", self._exc_var.get(),
        ]

    def _on_controls_activate(self) -> None:
        super()._on_controls_activate()
        for c in self._combos:
            c.configure(state="disabled")

    def _on_controls_reset(self) -> None:
        super()._on_controls_reset()
        for c in self._combos:
            c.configure(state="readonly")
