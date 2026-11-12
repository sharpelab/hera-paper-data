"""Sidecar JSON layout.

Default path: <image_dir>/hera/<image_stem>__<UTC-timestamp>.json
Override via --sidecar PATH at the CLI.
"""

from __future__ import annotations

import datetime as _dt
from pathlib import Path

from hera.models import Annotation, Provenance, Sidecar


def default_sidecar_path(image_path: Path, timestamp: str) -> Path:
    sidecar_dir = image_path.resolve().parent / "hera"
    return sidecar_dir / f"{image_path.stem}__{timestamp}.json"


def utc_timestamp() -> str:
    """ISO-8601 UTC timestamp safe for filenames (replace : with -)."""
    now = _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0)
    return now.isoformat().replace(":", "-").replace("+00-00", "Z")


def write_sidecar(path: Path, annotation: Annotation, provenance: Provenance) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    sidecar = Sidecar(annotation=annotation, provenance=provenance)
    path.write_text(sidecar.model_dump_json(indent=2))
