"""Core utilities shared across workers and launcher."""

from enum import StrEnum
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent.parent.parent


class Tag(StrEnum):
    INIT = "init"
    WAITING = "waiting"
    READY = "ready"
    DATA = "data"
    ERROR = "error"


def emit(tag: Tag, payload: str = "") -> None:
    """Emit a stdout protocol line: [tag] payload"""
    line = f"[{tag}] {payload}" if payload else f"[{tag}]"
    print(line, flush=True)
