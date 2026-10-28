"""Standalone pink fridge monitor launcher (Qt).

A trimmed launcher for the pink fridge: starts/stops the two LC log
scraper workers (FP pressures/gauges, TC AVS thermometry) plus the
rig's JupyterLab, and shows their freshness/health. All scaffolding
(status panel, tick loop, log viewer, tray, single-instance, quit
handshake, Jupyter panel) comes from gui.qt.base_launcher; this class
supplies only the rig config, the worker list, and the per-rig knobs.

JupyterLab: rooted at ~/Documents/measurements (the Syncthing-synced
measurement tree) on port 8890 — 8888/8889 belong to the legacy
system-Python servers still in use on the rig.
"""

import sys
from pathlib import Path

from core.config import load_pink_config
from gui.qt.base_launcher import BaseLauncher
from gui.qt.worker_panel import WorkerPanel


class PinkLauncher(BaseLauncher):
    TITLE = "Pink Monitor"
    MIN_SIZE = (300, 200)
    LOG_TAG = "pink-launcher"
    LOG_WINDOW_TITLE = "Pink Launcher Log"
    START_ALL_TEXT = "Start"
    INSTANCE_NAME = "measurement-env-pink"
    JUPYTER_DIR = Path.home() / "Documents" / "measurements"
    JUPYTER_PORT = 8890

    def _load_config(self):
        return load_pink_config()

    def _make_workers(self):
        cfg = self._config
        return [
            WorkerPanel(
                self, name="Leiden FrontPanel", desc="pressures/flow", tag="lc_fp",
                cmd=[sys.executable, "-m", "workers.pink_scraper", "--family", "FP"],
                health_key="lc_scrapper_fp", health_measurement="LC_scrapper",
                config=cfg,
            ),
            WorkerPanel(
                self, name="AVS-47", desc="thermometry (log)", tag="lc_tc",
                cmd=[sys.executable, "-m", "workers.pink_scraper", "--family", "TC"],
                health_key="lc_scrapper_tc", health_measurement="LC_scrapper",
                config=cfg,
            ),
            WorkerPanel(
                self, name="AMI 430", desc="magnet field (read-only)", tag="magnet",
                cmd=[sys.executable, "-m", "workers.magnet", "--rig", "pink"],
                health_key="magnet", health_measurement="AMI430",
                config=cfg,
            ),
        ]


def main():
    sys.exit(PinkLauncher.run())


if __name__ == "__main__":
    main()
