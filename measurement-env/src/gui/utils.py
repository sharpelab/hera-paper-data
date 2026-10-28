"""GUI utilities — thread safety helpers, logging, and shared types."""

import functools
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import ParamSpec, TypeVar

from core import REPO_DIR

LOG_PATH = REPO_DIR / "launcher.log"
JUPYTER_LOG_PATH = REPO_DIR / "jupyter.log"
_log_lock = threading.Lock()


def _log(tag: str, msg: str) -> None:
    """Append a timestamped line to launcher.log."""
    try:
        with _log_lock, open(LOG_PATH, "a") as f:
            f.write(f"{time.strftime('%H:%M:%S')} [{tag}] {msg}\n")
    except OSError:
        pass

_TAIL_MAX_BYTES = 262_144


def tail_lines(path: Path, n: int) -> str:
    """Return the last *n* lines of *path* (reads at most the trailing 256 KiB)."""
    with open(path, "rb") as f:
        f.seek(0, 2)  # SEEK_END
        size = f.tell()
        f.seek(max(0, size - _TAIL_MAX_BYTES))
        data = f.read()
    lines = data.decode(errors="replace").splitlines(keepends=True)
    return "".join(lines[-n:])


_MAIN_THREAD_ID = threading.main_thread().ident

P = ParamSpec("P")
T = TypeVar("T")


def main_thread_only(fn: Callable[P, T]) -> Callable[P, T]:
    """Decorator that asserts the function runs on the main thread."""
    @functools.wraps(fn)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        assert threading.current_thread().ident == _MAIN_THREAD_ID, (
            f"{fn.__qualname__} must be called from the main thread, "
            f"got {threading.current_thread().name}"
        )
        return fn(*args, **kwargs)
    return wrapper


@dataclass
class ComponentStatus:
    """Health state of a single monitored component."""
    ok: bool = True
    message: str = ""
