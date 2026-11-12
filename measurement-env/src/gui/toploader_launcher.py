"""Toploader measurement environment launcher GUI.

Extends gui.base_launcher.BaseLauncher with the toploader-specific panels:
JupyterLab control + new-run creation, the UPS monitor, and the
Jupyter-stopped yellow status tier.
"""

import os
import shutil
import subprocess
import sys
import threading
import tkinter as tk
import webbrowser
from datetime import date
from pathlib import Path
from tkinter import ttk

from core import REPO_DIR
from core.config import load_config
from gui.base_launcher import BaseLauncher
from gui.jupyter_discovery import find_server_url
from gui.managed_process import ManagedProcess, _NO_WINDOW
from gui.utils import JUPYTER_LOG_PATH, ComponentStatus, _log
from gui.worker_panel import ProbeWorkerPanel, WorkerPanel

MEASUREMENTS_DIR = Path.home() / "measurements"
TEMPLATES_DIR = REPO_DIR / "templates"


class ToploaderLauncher(BaseLauncher):
    TITLE = "Measurement Env"
    MIN_SIZE = (300, 250)
    LOG_TAG = "launcher"
    LOG_WINDOW_TITLE = "Launcher Log"

    # --- BaseLauncher hooks ---

    def _load_config(self):
        return load_config()

    def _init_state(self):
        self._jupyter = ManagedProcess("jupyter")
        self._jupyter_base_url = None
        self._jupyter_status = ComponentStatus(ok=False, message="not running")
        self._ups_status = ComponentStatus(ok=False, message="checking...")

    def _make_workers(self):
        cfg = self._config
        return [
            ProbeWorkerPanel(
                self, title="AVS Probe", tag="avs_probe",
                health_key="avs_probe", health_measurement="AVS_bridge",
                status_name="AVS Probe", config=cfg,
            ),
            WorkerPanel(
                self, title="AVS Fridge", tag="avs_fridge",
                cmd=[sys.executable, "-m", "workers.avs_fridge"],
                health_key="avs_fridge", health_measurement="AVS_bridge",
                status_name="AVS Fridge", config=cfg,
            ),
            WorkerPanel(
                self, title="Magnet", tag="magnet",
                cmd=[sys.executable, "-m", "workers.magnet"],
                health_key="magnet", health_measurement="AVS_bridge",
                status_name="Magnet", config=cfg,
            ),
            WorkerPanel(
                self, title="LC Front Panel", tag="lc_scraper_fp",
                cmd=[sys.executable, "-m", "workers.lc_scraper", "--family", "FP"],
                health_key="lc_scrapper_fp", health_measurement="LC_scrapper",
                status_name="LC Front Panel", config=cfg,
            ),
            WorkerPanel(
                self, title="LC Pulse Tube", tag="lc_scraper_pt",
                cmd=[sys.executable, "-m", "workers.lc_scraper", "--family", "PT"],
                health_key="lc_scrapper_pt", health_measurement="LC_scrapper",
                status_name="LC Pulse Tube", config=cfg,
            ),
            WorkerPanel(
                self, title="Thorlabs Thermo", tag="thorlabs_thermo",
                cmd=[sys.executable, "-m", "workers.thorlabs_thermo"],
                health_key="thorlabs_thermo", health_measurement="thorlabs_thermo",
                status_name="Thorlabs Thermo", config=cfg,
            ),
        ]

    def _build_pre_worker_panels(self):
        self._build_run_panel()
        self._build_jupyter_panel()

    def _build_post_worker_panels(self):
        self._build_ups_panel()

    def _extra_issues(self):
        if not self._ups_status.ok:
            return [f"UPS Monitor: {self._ups_status.message}"]
        return []

    def _ready_tier(self):
        if not self._jupyter_status.ok:
            return ("Ready (Jupyter stopped)", "#DAA520")
        return ("Ready", "green")

    def _running_extra(self):
        return ["JupyterLab"] if self._jupyter.running else []

    def _stop_extra(self):
        self._jupyter.stop()

    # --- Jupyter panel ---

    def _build_jupyter_panel(self):
        frame = ttk.LabelFrame(self, text="JupyterLab", padding=10)
        frame.pack(fill="x", padx=10, pady=(10, 5), anchor="n")

        status_row = ttk.Frame(frame)
        status_row.pack(fill="x")

        ttk.Label(status_row, text="Status:").pack(side="left")
        self._status_var = tk.StringVar(value="Stopped")
        self._status_label = ttk.Label(
            status_row, textvariable=self._status_var, foreground="gray"
        )
        self._status_label.pack(side="left", padx=(5, 0))

        btn_row = ttk.Frame(frame)
        btn_row.pack(fill="x", pady=(10, 0))

        self._start_btn = ttk.Button(btn_row, text="Start", command=self._start)
        self._start_btn.pack(side="left", expand=True, fill="x", padx=(0, 5))

        self._stop_btn = ttk.Button(
            btn_row, text="Stop", command=self._stop, state="disabled"
        )
        self._stop_btn.pack(side="left", expand=True, fill="x")

    _UPS_POLL_INTERVAL_MS = 10_000

    def _build_ups_panel(self):
        frame = ttk.LabelFrame(self, text="UPS Monitor", padding=10)
        frame.pack(fill="x", padx=10, pady=(5, 5), anchor="n")

        status_row = ttk.Frame(frame)
        status_row.pack(fill="x")

        ttk.Label(status_row, text="Status:").pack(side="left")
        ups_var = tk.StringVar(value="checking...")
        ups_label = ttk.Label(
            status_row, textvariable=ups_var, foreground="gray",
        )
        ups_label.pack(side="left", padx=(5, 0))

        if sys.platform != "win32":
            ups_var.set("N/A (Windows only)")
            self._ups_status = ComponentStatus(ok=True)
            return

        def poll():
            def do_check():
                try:
                    result = subprocess.run(
                        ["nssm", "status", "ups-monitor"],
                        capture_output=True, text=True, timeout=5,
                        creationflags=_NO_WINDOW,
                    )
                    state = result.stdout.strip()
                except Exception as e:
                    state = f"error: {e}"
                self.after(0, lambda: _update(state))

            threading.Thread(target=do_check, daemon=True).start()
            self.after(self._UPS_POLL_INTERVAL_MS, poll)

        def _update(state):
            if state == "SERVICE_RUNNING":
                ups_var.set("Running")
                ups_label.configure(foreground="green")
                self._ups_status = ComponentStatus(ok=True)
            else:
                display = state.removeprefix("SERVICE_").replace("_", " ").title()
                ups_var.set(display)
                ups_label.configure(foreground="red")
                self._ups_status = ComponentStatus(
                    ok=False, message=display.lower(),
                )

        poll()

    # --- New Run panel + logic ---

    def _build_run_panel(self):
        frame = ttk.LabelFrame(self, text="New Run", padding=10)
        frame.pack(fill="x", padx=10, pady=(5, 5), anchor="n")

        ttk.Label(frame, text="User:").grid(row=0, column=0, sticky="w")
        self._user_combo = ttk.Combobox(
            frame, values=self._list_users(), width=20
        )
        self._user_combo.grid(row=0, column=1, sticky="ew", padx=(5, 0))

        ttk.Label(frame, text="Name:").grid(row=1, column=0, sticky="w", pady=(5, 0))
        self._name_entry = ttk.Entry(frame, width=23)
        self._name_entry.grid(row=1, column=1, sticky="ew", padx=(5, 0), pady=(5, 0))

        self._create_btn = ttk.Button(
            frame, text="Create", command=self._create_run, state="disabled"
        )
        self._create_btn.grid(row=2, column=0, columnspan=2, pady=(10, 0), sticky="ew")

        self._run_msg_var = tk.StringVar()
        self._run_msg_label = ttk.Label(
            frame, textvariable=self._run_msg_var, wraplength=250
        )
        # Gridded on demand by _run_msg(); hidden while empty.

        frame.columnconfigure(1, weight=1)

    @staticmethod
    def _list_users():
        if not MEASUREMENTS_DIR.exists():
            return []
        return sorted(
            d.name
            for d in MEASUREMENTS_DIR.iterdir()
            if d.is_dir() and not d.name.startswith(".")
        )

    def _create_run(self):
        user = self._user_combo.get().strip()
        name = self._name_entry.get().strip()

        if not user:
            self._run_msg("Select a user.", "red")
            return
        if not name:
            self._run_msg("Enter a run name.", "red")
            return

        today = date.today().strftime("%Y%m%d")
        run_dir = MEASUREMENTS_DIR / user / name

        measure_name = f"{today}_measure.ipynb"
        ana_name = f"{today}_ana.ipynb"
        scratch_name = f"{today}_iris_scratch.ipynb"

        if (run_dir / measure_name).exists():
            self._run_msg(f"{measure_name} already exists.", "red")
            return

        run_dir.mkdir(parents=True, exist_ok=True)

        created = []

        measure_tmpl = TEMPLATES_DIR / "toploader_measure.ipynb"
        if measure_tmpl.exists():
            dest = run_dir / measure_name
            shutil.copy2(measure_tmpl, dest)
            created.append(dest)

        ana_tmpl = TEMPLATES_DIR / "toploader_ana.ipynb"
        if ana_tmpl.exists():
            dest = run_dir / ana_name
            shutil.copy2(ana_tmpl, dest)
            created.append(dest)

        scratch_tmpl = TEMPLATES_DIR / "iris_scratch.ipynb"
        if scratch_tmpl.exists():
            dest = run_dir / scratch_name
            shutil.copy2(scratch_tmpl, dest)
            created.append(dest)

        # Rig card: repo-canonical, deployed copy refreshed on every run
        # creation (agents read it, never edit it).
        rig_card = REPO_DIR / "hera" / "rig-cards" / "toploader.md"
        if rig_card.exists():
            shutil.copy2(rig_card, run_dir / "rig_card.md")

        self._run_msg(f"Created {user}/{name}/{today}_*.ipynb", "green")

        for nb in created:
            self._open_notebook(nb)

    def _open_notebook(self, nb_path):
        """Open a notebook in the running JupyterLab via browser URL."""
        if self._jupyter_base_url is None:
            return
        try:
            rel = nb_path.relative_to(MEASUREMENTS_DIR)
        except ValueError:
            return
        # Convert Windows backslashes to forward slashes for URL
        rel_posix = rel.as_posix()
        url = self._jupyter_base_url.replace("/lab?", f"/lab/tree/{rel_posix}?")
        if sys.platform == "win32":
            os.startfile(url)
        else:
            webbrowser.open(url)

    def _run_msg(self, text, color):
        self._run_msg_var.set(text)
        self._run_msg_label.configure(foreground=color)
        self._run_msg_label.grid(row=3, column=0, columnspan=2, pady=(5, 0))

    # --- JupyterLab logic ---

    def _set_status(self, text, color):
        self._status_var.set(text)
        self._status_label.configure(foreground=color)

    def _jupyter_set_running(self, url):
        """Set UI to Running with the given server URL."""
        self._jupyter_base_url = url
        self._set_status("Running", "green")
        self._start_btn.configure(state="disabled")
        self._stop_btn.configure(state="normal")
        self._create_btn.configure(state="normal")
        self._jupyter_status = ComponentStatus(ok=True)

    def _jupyter_on_stopped(self):
        self._jupyter_base_url = None
        self._set_status("Stopped", "gray")
        self._start_btn.configure(state="normal")
        self._stop_btn.configure(state="disabled")
        self._create_btn.configure(state="disabled")
        self._jupyter_status = ComponentStatus(ok=False, message="not running")

    def _start(self):
        self._start_btn.configure(state="disabled")
        self._stop_btn.configure(state="normal")
        self._set_status("Starting...", "orange")

        measurements_str = str(MEASUREMENTS_DIR)
        # Prepend the repo's labconfig dir so the server picks up
        # recordTiming (executed cells get metadata.execution timing). It's
        # repo-side, so it survives env rebuilds; see jupyter-config/README.md.
        jl_env = dict(os.environ)
        config_path = str(REPO_DIR / "jupyter-config")
        existing = jl_env.get("JUPYTER_CONFIG_PATH", "")
        jl_env["JUPYTER_CONFIG_PATH"] = (
            f"{config_path}{os.pathsep}{existing}" if existing else config_path
        )
        self._jupyter.start(
            cmd=[
                sys.executable, "-m", "jupyter", "lab",
                "--notebook-dir", measurements_str,
                "--collaborative",
                # nb-collab's HTTP preflight to /api/collaboration/session/ doesn't
                # carry the token, so XSRF rejects POST/PUT with 403. Local-only JL.
                "--ServerApp.disable_check_xsrf=True",
            ],
            ready_check=lambda: find_server_url(measurements_str),
            dispatch=lambda cb: self.after(0, cb),
            on_ready=self._jupyter_set_running,
            on_stopped=self._jupyter_on_stopped,
            log_path=JUPYTER_LOG_PATH,
            env=jl_env,
        )

    def _stop(self):
        self._set_status("Stopping...", "orange")
        self._jupyter.stop()
        self._jupyter_on_stopped()


def main():
    ToploaderLauncher().mainloop()


if __name__ == "__main__":
    main()
