"""UPS-triggered graceful shutdown for measurements.

Usage in a notebook::

    from sharpelab_nb.ups import start_ups_monitor

    def safe_shutdown():
        for name, inst in gate_instruments.items():
            inst.volt(0)
        mag.field(0)

    monitor = start_ups_monitor(safe_shutdown)

    # Later:
    monitor.stop()
"""

import logging
import threading
import time
from typing import Callable

import sweep
from measurebot.ups import UPSReader
from measurebot.ups_monitor import (
    EventsConfig,
    MonitorConfig,
    ThresholdConfig,
    UPSMonitor,
)

log = logging.getLogger(__name__)


class UPSShutdownMonitor:
    """Handle returned by start_ups_monitor. Call .stop() to tear down."""

    def __init__(self, reader: UPSReader, thread: threading.Thread) -> None:
        self._reader = reader
        self._thread = thread
        self._stopped = threading.Event()

    def stop(self) -> None:
        """Stop the monitor thread and close the UPS reader."""
        self._stopped.set()
        self._thread.join(timeout=15)
        self._reader.close()
        print("UPS monitor stopped.")

    @property
    def running(self) -> bool:
        return self._thread.is_alive()


def start_ups_monitor(
    shutdown_fn: Callable[[], None],
    battery_threshold: int = 50,
    poll_interval: float = 10,
) -> UPSShutdownMonitor:
    """Start a background UPS monitor that triggers graceful shutdown.

    Parameters
    ----------
    shutdown_fn:
        Called after the active sweep exits (or immediately if idle).
        Should ramp instruments to safe state.
    battery_threshold:
        Battery percentage at which to trigger shutdown.
    poll_interval:
        Seconds between UPS polls.
    """
    # Wrap the user's shutdown function with logging
    def wrapped_shutdown() -> None:
        print(f"UPS SHUTDOWN: executing safe shutdown...")
        try:
            shutdown_fn()
            print("UPS SHUTDOWN: complete.")
        except Exception:
            log.exception("UPS SHUTDOWN: error during shutdown")
            print("UPS SHUTDOWN: error (see log).")

    sweep.set_shutdown_handler(wrapped_shutdown)

    reader = UPSReader()
    reader.open()
    print(f"UPS connected: {reader.product} (S/N: {reader.serial})")

    shutdown_triggered = False

    def on_event(event: str, status, message: str) -> None:
        nonlocal shutdown_triggered
        print(f"UPS [{event}]: {message}")
        if event == "battery_warn" and not shutdown_triggered:
            shutdown_triggered = True
            print(f"UPS: battery at {status.charge_pct}% — requesting shutdown...")
            sweep.request_shutdown()

    config = MonitorConfig(
        poll_interval=poll_interval,
        events=EventsConfig(
            power_lost=True,
            power_restored=True,
            battery_update=60,
            warn=ThresholdConfig(battery_pct=battery_threshold),
        ),
    )
    monitor = UPSMonitor(reader, config, on_event=on_event)

    # Do an initial read so _prev_ac is set (avoids false trigger on first poll)
    monitor.check()

    handle = UPSShutdownMonitor(reader, threading.Thread())

    def poll_loop() -> None:
        while not handle._stopped.is_set():
            try:
                monitor.check()
            except Exception:
                log.exception("UPS read failed")
            handle._stopped.wait(poll_interval)

    thread = threading.Thread(target=poll_loop, daemon=True)
    handle._thread = thread
    thread.start()

    print(
        f"UPS monitor started (shutdown at {battery_threshold}%, "
        f"polling every {poll_interval:.0f}s)"
    )
    return handle
