"""Standalone VTI monitor launcher (Qt).

A trimmed launcher for the VTI rig: starts/stops the Lakeshore 335, VTI aux,
and magnet workers plus the rig's JupyterLab, and shows their freshness/health.
All scaffolding (status panel, tick loop, log viewer, tray, single-instance,
quit handshake, Jupyter panel) comes from gui.qt.base_launcher; this class
supplies only the rig config, the worker list, and the per-rig knobs.

JupyterLab: rooted at ~/VTI_local_data on port 8890 — the rig's standard JL
port, taken over from the retired foreign (system-Python) server. See
"Phase -1" in docs/plans/LAUNCHER_QT_PLAN.md.
"""

import sys
from pathlib import Path

from core.config import load_vti_config
from gui.qt.base_launcher import BaseLauncher
from gui.qt.worker_panel import WorkerPanel


class VtiLauncher(BaseLauncher):
    TITLE = "VTI Monitor"
    MIN_SIZE = (300, 200)
    LOG_TAG = "vti-launcher"
    LOG_WINDOW_TITLE = "VTI Launcher Log"
    START_ALL_TEXT = "Start"
    INSTANCE_NAME = "measurement-env-vti"
    JUPYTER_DIR = Path.home() / "VTI_local_data"
    JUPYTER_PORT = 8890

    def _load_config(self):
        return load_vti_config()

    def _make_workers(self):
        cfg = self._config
        return [
            WorkerPanel(
                self, title="Lakeshore 335", tag="lakeshore",
                cmd=[sys.executable, "-m", "workers.lakeshore"],
                health_key="lakeshore", health_measurement="vti",
                status_name="Lakeshore", config=cfg,
            ),
            WorkerPanel(
                self, title="VTI Aux", tag="vti_aux",
                cmd=[sys.executable, "-m", "workers.vti_aux"],
                health_key="vti_aux", health_measurement="vti",
                status_name="VTI Aux", config=cfg,
            ),
            WorkerPanel(
                self, title="Magnet", tag="vti_magnet",
                cmd=[sys.executable, "-m", "workers.vti_magnet"],
                health_key="magnet", health_measurement="vti",
                status_name="Magnet", config=cfg,
            ),
        ]


def main():
    sys.exit(VtiLauncher.run())


if __name__ == "__main__":
    main()
