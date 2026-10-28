"""Reads devices.toml (next to this file) for the device an archive was taken on."""
from __future__ import annotations

import re
import tomllib
from pathlib import Path

TABLE = Path(__file__).resolve().with_name("devices.toml")

_TITLE_RE = re.compile(r"^#\s*Device card\s*[—-]+\s*([A-Za-z0-9_-]+)", re.IGNORECASE)


def device_of(archive: str | Path) -> str:
    """Device key from the archive's device card title line (``# Device card — QC0426 (...)``)."""
    card = Path(archive) / "device_card.md"
    first = card.read_text(encoding="utf-8").splitlines()[0] if card.exists() else ""
    m = _TITLE_RE.match(first)
    if not m:
        raise ValueError(f"cannot read a device name from {card}: {first!r}")
    return m.group(1).lower()


def device_params(archive: str | Path, *required: str) -> dict:
    """The device's table, with every key in ``required`` present."""
    key = device_of(archive)
    table = tomllib.loads(TABLE.read_text(encoding="utf-8"))
    if key not in table:
        raise ValueError(f"device {key!r} has no table in {TABLE}")
    missing = [k for k in required if k not in table[key]]
    if missing:
        raise ValueError(f"device {key!r} lacks {', '.join(missing)} in {TABLE}")
    return {"device": key, **table[key]}
