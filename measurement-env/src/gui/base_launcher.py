"""Shared launcher scaffolding for the per-rig measurement-env launchers.

`BaseLauncher` owns the rig-agnostic GUI: the aggregate status panel, the single
1s `_tick` loop, the issue roll-up, the tailing log viewer, Start-All, and the
close handshake. Per-rig launchers subclass it and supply config + workers via
the hooks below; the toploader additionally layers Jupyter/UPS/new-run panels
through `_build_pre_worker_panels` / `_build_post_worker_panels`.

Subclass surface:
    Class attrs: TITLE, MIN_SIZE, LOG_TAG, LOG_WINDOW_TITLE, START_ALL_TEXT
    Required:    _load_config(), _make_workers() -> list[WorkerPanel]
    Optional:    _init_state(), _build_pre_worker_panels(),
                 _build_post_worker_panels(), _extra_issues() -> list[str],
                 _ready_tier() -> (text, color), _running_extra() -> list[str],
                 _stop_extra()
"""

import os
import tkinter as tk
from tkinter import messagebox, ttk

from core import REPO_DIR
from gui.utils import LOG_PATH, _log

ICON_PATH = REPO_DIR / "assets" / "measurement-env.ico"


class BaseLauncher(tk.Tk):
    TITLE = "Launcher"
    MIN_SIZE = (300, 200)
    LOG_TAG = "launcher"
    LOG_WINDOW_TITLE = "Launcher Log"
    START_ALL_TEXT = "Start All"
    _LOG_TAIL_LINES = 200

    def __init__(self):
        super().__init__()
        self.title(self.TITLE)
        self.minsize(*self.MIN_SIZE)
        if ICON_PATH.exists():
            try:
                self.iconbitmap(str(ICON_PATH))
            except tk.TclError:
                pass

        self._log_window = None
        self._config = self._load_config()
        self._init_state()

        self._build_status_panel()
        self._build_pre_worker_panels()
        self._workers = self._make_workers()
        self._build_post_worker_panels()

        self.protocol("WM_DELETE_WINDOW", self._on_close)
        _log(self.LOG_TAG, "started")
        self._tick()

    # --- Subclass hooks -----------------------------------------------------

    def _load_config(self):
        """Return the rig config (e.g. load_config() / load_vti_config())."""
        raise NotImplementedError

    def _make_workers(self) -> list:
        """Return the rig's WorkerPanel list (panel order = UI order)."""
        raise NotImplementedError

    def _init_state(self) -> None:
        """Set subclass instance vars needed before panels/tick (e.g. Jupyter)."""

    def _build_pre_worker_panels(self) -> None:
        """Panels built between the status panel and the worker panels."""

    def _build_post_worker_panels(self) -> None:
        """Panels built after the worker panels."""

    def _extra_issues(self) -> list[str]:
        """Non-worker issue strings to fold into the red tier."""
        return []

    def _ready_tier(self) -> tuple[str, str]:
        """(label, color) shown when there are no issues. Override for yellow."""
        return ("Ready", "green")

    def _running_extra(self) -> list[str]:
        """Names of extra running processes for the close prompt."""
        return []

    def _stop_extra(self) -> None:
        """Stop the extra processes named by _running_extra()."""

    # --- Status panel (flash-safe: log button packed once) ------------------

    def _build_status_panel(self):
        frame = ttk.LabelFrame(self, text="Status", padding=10)
        frame.pack(fill="x", padx=10, pady=(10, 5), anchor="n")

        top_row = ttk.Frame(frame)
        top_row.pack(fill="x")

        self._agg_status_var = tk.StringVar(value="Starting...")
        self._agg_status_label = ttk.Label(
            top_row, textvariable=self._agg_status_var,
            foreground="orange", font=("TkDefaultFont", 10, "bold"),
        )
        self._agg_status_label.pack(side="left")

        self._start_all_btn = ttk.Button(
            top_row, text=self.START_ALL_TEXT, command=self._start_all,
        )
        self._start_all_btn.pack(side="right")

        self._issues_var = tk.StringVar()
        self._issues_label = ttk.Label(
            frame, textvariable=self._issues_var, foreground="red",
        )
        # Packed once; the issues label (when shown) inserts above it via
        # before=. Re-packing the button every tick is what made it flash.
        self._log_btn = ttk.Button(frame, text="Log", command=self._view_log)
        self._log_btn.pack(fill="x", pady=(5, 0))

    def _start_all(self):
        for w in self._workers:
            if not w.running:
                w.start()

    def _tick(self) -> None:
        """Single 1s timer driving all UI updates from background state."""
        for w in self._workers:
            w.refresh_ui()
        self._refresh_status()
        self.after(1000, self._tick)

    def _refresh_status(self):
        """Recompute aggregate status from worker + extra component health."""
        issues = []
        for w in self._workers:
            s = w.get_status()
            if not s.ok:
                issues.append(f"{w.name}: {s.message}")
        issues.extend(self._extra_issues())

        if issues:
            self._agg_status_var.set("Issues")
            self._agg_status_label.configure(foreground="red")
            self._issues_var.set("\n".join(issues))
            if not self._issues_label.winfo_ismapped():
                self._issues_label.pack(fill="x", pady=(5, 0), before=self._log_btn)
        else:
            text, color = self._ready_tier()
            self._agg_status_var.set(text)
            self._agg_status_label.configure(foreground=color)
            self._issues_var.set("")
            if self._issues_label.winfo_ismapped():
                self._issues_label.pack_forget()

        all_running = all(w.running for w in self._workers)
        self._start_all_btn.configure(
            state="disabled" if all_running else "normal",
        )

    # --- Log viewer ---------------------------------------------------------

    def _view_log(self):
        if self._log_window is not None and self._log_window.winfo_exists():
            self._log_window.lift()
            return

        win = tk.Toplevel(self)
        win.title(self.LOG_WINDOW_TITLE)
        win.geometry("600x400")
        self._log_window = win

        text = tk.Text(win, wrap="none")
        text.pack(fill="both", expand=True)

        last_size = [0]

        def refresh():
            try:
                size = LOG_PATH.stat().st_size
            except FileNotFoundError:
                text.configure(state="normal")
                text.delete("1.0", "end")
                text.insert("1.0", "(no log yet)")
                text.configure(state="disabled")
                if win.winfo_exists():
                    win.after(1000, refresh)
                return

            if size == last_size[0]:
                if win.winfo_exists():
                    win.after(1000, refresh)
                return
            last_size[0] = size

            try:
                with open(LOG_PATH, "rb") as f:
                    f.seek(0, os.SEEK_END)
                    remaining = self._LOG_TAIL_LINES
                    pos = f.tell()
                    while remaining > 0 and pos > 0:
                        pos = max(pos - 4096, 0)
                        f.seek(pos)
                        chunk = f.read(min(4096, f.tell() + 4096))
                        remaining -= chunk.count(b"\n")
                    f.seek(max(pos, 0))
                    tail = f.read().decode(errors="replace")
                    lines = tail.splitlines(keepends=True)
                    tail = "".join(lines[-self._LOG_TAIL_LINES:])
            except OSError:
                tail = "(error reading log)"

            text.configure(state="normal")
            text.delete("1.0", "end")
            text.insert("1.0", tail)
            text.configure(state="disabled")
            text.see("end")
            if win.winfo_exists():
                win.after(1000, refresh)

        refresh()

    # --- Close --------------------------------------------------------------

    def _on_close(self):
        running_names = self._running_extra() + [
            w.name for w in self._workers if w.running
        ]
        if running_names:
            if not messagebox.askokcancel(
                "Processes Running",
                f"{', '.join(running_names)} still running. Stop and close?",
                parent=self,
            ):
                return
            self._stop_extra()
        for w in self._workers:
            w.destroy()
        self.destroy()
