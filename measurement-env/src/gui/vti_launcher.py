"""Standalone VTI monitor launcher.

A trimmed launcher for the VTI rig: starts/stops the Lakeshore 335, VTI aux, and
magnet workers and shows their freshness/health. All scaffolding (status panel,
tick loop, log viewer, close handshake) comes from gui.base_launcher; this class
supplies only the rig config and the worker list.
"""

import sys

from core.config import load_vti_config
from gui.base_launcher import BaseLauncher
from gui.worker_panel import WorkerPanel


class VtiLauncher(BaseLauncher):
    TITLE = "VTI Monitor"
    MIN_SIZE = (300, 200)
    LOG_TAG = "vti-launcher"
    LOG_WINDOW_TITLE = "VTI Launcher Log"
    START_ALL_TEXT = "Start"

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
    VtiLauncher().mainloop()


if __name__ == "__main__":
    main()
