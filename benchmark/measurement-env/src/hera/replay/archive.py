"""An archived HERA session dir and its one tactical transcript."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from hera.replay.errors import CutError
from hera.replay.transcript import Transcript

AS_ARCHIVED = ("hera_session.md", "rig_card.md", "corpus_provenance.json")
RUN_DIR = re.compile(r"^\d+$")


@dataclass
class Archive:
    root: Path
    transcript: Transcript

    @property
    def notebooks(self) -> dict[str, Path]:
        return {p.name: p for p in sorted(self.root.glob("*.ipynb"))}

    @property
    def run_dirs(self) -> dict[int, Path]:
        data = self.root / "data"
        if not data.is_dir():
            return {}
        return {int(p.name): p for p in data.iterdir() if p.is_dir() and RUN_DIR.match(p.name)}

    def load_notebook(self, name: str) -> dict:
        return json.loads(self.notebooks[name].read_text(encoding="utf-8"))


def _first_cwd(path: Path) -> str | None:
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            cwd = json.loads(line).get("cwd")
            if cwd:
                return cwd
    return None


def _is_init_transcript(cwd: str) -> bool:
    """hera-session runs from the corpus checkout, tactical from the session dir."""
    return re.split(r"[\\/]+", cwd.rstrip("\\/"))[-1] == "measurement_env"


def open_archive(root: Path) -> Archive:
    root = Path(root).resolve()
    if not root.is_dir():
        raise CutError(f"archive dir not found: {root}")
    tdir = root / "transcripts"
    if not tdir.is_dir():
        raise CutError(f"{root}: no transcripts/ dir; replay cuts from an archive, not a rig session dir")
    tactical = []
    for p in sorted(tdir.glob("*.jsonl")):
        cwd = _first_cwd(p)
        if cwd is None:
            raise CutError(f"{p.name}: no entry carries a cwd")
        if not _is_init_transcript(cwd):
            tactical.append(p)
    if len(tactical) != 1:
        names = ", ".join(p.name for p in tactical) or "none"
        raise CutError(f"{root.name}: expected exactly one tactical transcript, found {len(tactical)}: {names}")
    return Archive(root=root, transcript=Transcript(tactical[0]))
