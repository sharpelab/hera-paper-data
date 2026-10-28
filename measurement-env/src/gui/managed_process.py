"""ManagedProcess — subprocess lifecycle with async readiness polling."""

import os
import signal
import subprocess
import sys
import threading
import time
from collections.abc import Callable
from pathlib import Path

from core import Tag
from gui.utils import LOG_PATH, _log

_NO_WINDOW = 0x08000000 if sys.platform == "win32" else 0


def _kill_process_tree(pid):
    """Kill a process and all its children."""
    _log("process", f"kill_tree pid={pid}")
    if sys.platform == "win32":
        result = subprocess.run(
            ["taskkill", "/T", "/F", "/PID", str(pid)],
            capture_output=True,
            text=True,
            creationflags=_NO_WINDOW,
        )
        _log("process", f"taskkill rc={result.returncode} stdout={result.stdout.strip()!r} stderr={result.stderr.strip()!r}")
    else:
        try:
            os.killpg(os.getpgid(pid), signal.SIGTERM)
            _log("process", "killpg SIGTERM sent")
        except (ProcessLookupError, PermissionError) as e:
            _log("process", f"killpg failed: {e}")


class ManagedProcess:
    """Lifecycle wrapper for a subprocess with async readiness polling.

    Two start modes:

    start() — poll-based readiness (e.g. Jupyter server file check).
        Launches with stdout/stderr suppressed.

    start_with_output() — stdout protocol readiness (e.g. worker scripts).
        Reads stdout line by line, parses [tag] prefix, routes lines:
        - [init]    → _log + on_init callback
        - [waiting] → _log + on_waiting callback (init done, polling for data)
        - [ready]   → fires on_ready
        - [data]    → on_data callback (silent, no log)
        - [error]   → _log + on_error callback
        - other     → _log
    """

    def __init__(self, tag: str) -> None:
        self._tag = tag
        self._proc: subprocess.Popen | None = None
        self._cancel = threading.Event()

    def _launch(
        self,
        cmd,
        *,
        capture_stdout: bool = False,
        stdin_pipe: bool = False,
        log_path: Path | None = None,
        env: dict | None = None,
    ) -> tuple[subprocess.Popen | None, bool]:
        """Launch subprocess. Returns (proc, started).

        If capture_stdout is True, stdout is piped (for [tag] protocol reading).
        Otherwise, stdout+stderr are appended to log_path if given, else DEVNULL.
        If stdin_pipe is True, stdin is piped for send_line(); otherwise the
        child gets DEVNULL (workers must not inherit the launcher's stdin).
        If env is given, it replaces the child's environment (callers pass a
        full os.environ-derived dict, not a delta).
        """
        if self._proc is not None:
            return self._proc, False
        self._cancel.clear()

        kwargs: dict = {}
        if sys.platform == "win32":
            kwargs["creationflags"] = _NO_WINDOW
        else:
            kwargs["start_new_session"] = True
        if env is not None:
            kwargs["env"] = env

        _log(self._tag, f"launching: {cmd}")

        log_file = None
        if capture_stdout:
            stdout = subprocess.PIPE
            stderr = subprocess.STDOUT
        elif log_path is not None:
            log_file = open(log_path, "ab")
            log_file.write(
                f"\n===== {time.strftime('%Y-%m-%d %H:%M:%S')} {self._tag} launching =====\n".encode()
            )
            log_file.flush()
            stdout = log_file
            stderr = subprocess.STDOUT
        else:
            stdout = subprocess.DEVNULL
            stderr = subprocess.DEVNULL

        try:
            self._proc = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE if stdin_pipe else subprocess.DEVNULL,
                stdout=stdout,
                stderr=stderr,
                text=capture_stdout,
                **kwargs,
            )
        finally:
            if log_file is not None:
                # Child has its own duplicated fd; we don't need ours.
                log_file.close()
        _log(self._tag, f"pid={self._proc.pid}")
        return self._proc, True

    def start(
        self,
        cmd: list[str],
        ready_check,
        dispatch: Callable[[Callable[[], None]], object],
        on_ready,
        on_stopped,
        *,
        poll_attempts: int = 60,
        poll_interval: float = 0.5,
        log_path: Path | None = None,
        env: dict | None = None,
    ) -> None:
        """Launch *cmd* and poll *ready_check* in a background thread.

        ready_check() should return a truthy result when the process is
        ready, or None/falsy to keep polling. *dispatch(cb)* must run the
        zero-arg *cb* on the GUI thread (tk: `after(0, cb)`; Qt: a queued
        signal emit); *on_ready(result)* and *on_stopped()* are delivered
        through it.

        If *log_path* is given, the subprocess's stdout+stderr are appended
        to that file; otherwise they go to DEVNULL. If *env* is given, it
        replaces the child's environment.
        """
        try:
            proc, started = self._launch(cmd, log_path=log_path, env=env)
        except Exception as e:
            _log(self._tag, f"launch failed: {e}")
            dispatch(on_stopped)
            return
        if not started:
            return
        assert proc is not None

        cancel = self._cancel  # local ref for the closure

        def poll():
            for _ in range(poll_attempts):
                if cancel.is_set():
                    _log(self._tag, "startup cancelled")
                    return
                result = ready_check()
                if result:
                    dispatch(
                        lambda r=result: on_ready(r) if not cancel.is_set() else None,
                    )
                    return
                time.sleep(poll_interval)
            _log(self._tag, "startup timed out")
            dispatch(on_stopped)

        threading.Thread(target=poll, daemon=True).start()

    def start_with_output(
        self,
        cmd: list[str],
        dispatch: Callable[[Callable[[], None]], object],
        on_ready,
        on_failed,
        on_died,
        *,
        on_waiting=None,
        on_data=None,
        stdin_pipe: bool = False,
    ) -> None:
        """Launch *cmd* and read stdout for [tag] protocol lines.

        All non-[data] lines are logged via _log(). Callbacks are delivered
        on the GUI thread via *dispatch* (see start()).

        on_waiting()  — [waiting] received, init done but no data yet
        on_failed(rc) — process exited before [ready]
        on_died(rc)   — process exited after [ready] unexpectedly

        With stdin_pipe=True the child's stdin is piped and send_line() can
        deliver command lines to it.
        """
        try:
            proc, started = self._launch(cmd, capture_stdout=True, stdin_pipe=stdin_pipe)
        except Exception as e:
            _log(self._tag, f"launch failed: {e}")
            dispatch(lambda: on_failed(None))
            return
        if not started:
            return
        assert proc is not None

        cancel = self._cancel
        tag = self._tag
        ready_fired = False

        def reader():
            nonlocal ready_fired
            try:
                for raw_line in proc.stdout:
                    if cancel.is_set():
                        break
                    line = raw_line.rstrip("\n\r")
                    if not line:
                        continue

                    # Parse [tag] payload
                    if line.startswith("[") and "]" in line:
                        bracket_end = line.index("]")
                        line_tag = line[1:bracket_end]
                        payload = line[bracket_end + 1:].lstrip()
                    else:
                        line_tag, payload = "", line

                    if line_tag == Tag.DATA:
                        if on_data and not cancel.is_set():
                            dispatch(lambda p=payload: on_data(p))
                    elif line_tag == Tag.READY:
                        _log(tag, "ready")
                        if not ready_fired and not cancel.is_set():
                            ready_fired = True
                            dispatch(
                                lambda: on_ready() if not cancel.is_set() else None,
                            )
                    elif line_tag == Tag.WAITING:
                        _log(tag, "waiting for data")
                        if on_waiting and not cancel.is_set():
                            dispatch(on_waiting)
                    elif line_tag == Tag.INIT:
                        _log(tag, payload)
                    elif line_tag == Tag.ERROR:
                        _log(tag, f"ERROR: {payload}")
                    else:
                        _log(tag, line)
            except ValueError:
                # Pipe closed during read — process was killed
                pass

            # Process exited or was killed
            if not cancel.is_set():
                rc = proc.poll()
                self._proc = None
                _log(tag, f"exited rc={rc}")
                if not ready_fired:
                    dispatch(lambda: on_failed(rc))
                else:
                    dispatch(lambda: on_died(rc))

        threading.Thread(target=reader, daemon=True).start()

    def send_line(self, line: str) -> bool:
        """Write one line to the child's stdin (requires stdin_pipe=True).

        Returns False (and logs) if the child is gone or its stdin is not
        piped — the child can die between the caller's check and the write,
        so failures here must never raise into the GUI thread.
        """
        proc = self._proc
        if proc is None or proc.stdin is None or proc.poll() is not None:
            _log(self._tag, f"send_line dropped (not running): {line!r}")
            return False
        try:
            proc.stdin.write(line + "\n")
            proc.stdin.flush()
            return True
        except (BrokenPipeError, OSError, ValueError) as e:
            _log(self._tag, f"send_line failed: {e}")
            return False

    def stop(self) -> None:
        """Kill the process and cancel any pending startup poll."""
        self._cancel.set()
        proc = self._proc
        if proc is None:
            return
        alive = proc.poll() is None
        _log(self._tag, f"stop: pid={proc.pid} alive={alive}")
        if alive:
            _kill_process_tree(proc.pid)
        else:
            _log(self._tag, f"stop: already exited rc={proc.returncode}")
        self._proc = None

    @property
    def running(self) -> bool:
        return self._proc is not None and self._proc.poll() is None
