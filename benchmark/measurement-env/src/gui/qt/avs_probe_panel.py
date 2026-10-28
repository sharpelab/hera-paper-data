"""Qt panel for the AVS-47B probe worker (workers/avs_probe.py).

A WorkerPanel whose launch command is built from three dropdowns — probe,
channel, excitation — chosen before Start and locked while the worker runs
(the worker fixes them at launch). The channel list follows the selected
probe's sensor table.
"""

from __future__ import annotations

import sys

from PyQt5 import QtWidgets

from gui.qt.worker_panel import WorkerPanel
from gui.utils import main_thread_only
from workers.avs_calibration import SENSORS_PROBE1, SENSORS_PROBE2

_SENSORS = {"1": SENSORS_PROBE1, "2": SENSORS_PROBE2}
DEFAULT_PROBE = "1"
DEFAULT_CHANNEL = 3  # MixingCh_low
DEFAULT_EXCITATION = "1"


def channel_labels(probe: str) -> list[str]:
    """Dropdown entries for *probe*: "<index>: <sensor name>"."""
    return [f"{i}: {_SENSORS[probe][i][0]}" for i in range(6)]


class ProbeWorkerPanel(WorkerPanel):
    """AVS probe panel with probe / channel / excitation dropdowns."""

    def __init__(self, launcher, **kwargs) -> None:
        kwargs.setdefault("cmd", [])
        super().__init__(launcher, **kwargs)

    def _build_extra_controls(self, layout: QtWidgets.QVBoxLayout) -> None:
        row = QtWidgets.QHBoxLayout()

        row.addWidget(QtWidgets.QLabel("Probe:"))
        self._probe_combo = QtWidgets.QComboBox()
        self._probe_combo.addItems(sorted(_SENSORS))
        self._probe_combo.setCurrentText(DEFAULT_PROBE)
        self._probe_combo.currentTextChanged.connect(self._on_probe_changed)
        row.addWidget(self._probe_combo)

        row.addWidget(QtWidgets.QLabel("Channel:"))
        self._channel_combo = QtWidgets.QComboBox()
        self._channel_combo.addItems(channel_labels(DEFAULT_PROBE))
        self._channel_combo.setCurrentIndex(DEFAULT_CHANNEL)
        row.addWidget(self._channel_combo)

        row.addWidget(QtWidgets.QLabel("EXC:"))
        self._exc_combo = QtWidgets.QComboBox()
        self._exc_combo.addItems(["1", "2", "3"])
        self._exc_combo.setCurrentText(DEFAULT_EXCITATION)
        row.addWidget(self._exc_combo)

        row.addStretch(1)
        layout.addLayout(row)
        self._combos = [self._probe_combo, self._channel_combo, self._exc_combo]

    def _on_probe_changed(self, probe: str) -> None:
        """Re-label the channels for the selected probe, keeping the index."""
        index = self._channel_combo.currentIndex()
        self._channel_combo.clear()
        self._channel_combo.addItems(channel_labels(probe))
        self._channel_combo.setCurrentIndex(index)

    @property
    def selection(self) -> tuple[str, str, str]:
        """(probe, channel index, excitation) as the worker's CLI strings."""
        channel = self._channel_combo.currentText().split(":")[0]
        return (self._probe_combo.currentText(), channel,
                self._exc_combo.currentText())

    def _get_cmd(self) -> list[str]:
        probe, channel, excitation = self.selection
        return [
            sys.executable, "-m", "workers.avs_probe",
            "--probe", probe,
            "--channel", channel,
            "--excitation", excitation,
        ]

    @main_thread_only
    def _on_controls_activate(self) -> None:
        for c in self._combos:
            c.setEnabled(False)

    @main_thread_only
    def _on_controls_reset(self) -> None:
        for c in self._combos:
            c.setEnabled(True)
