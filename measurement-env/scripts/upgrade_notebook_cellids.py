#!/usr/bin/env python
"""Upgrade legacy notebooks to nbformat 4.5 with uuid cell IDs.

Cell-ID-less notebooks (nbformat < 4.5, or 4.5 with cells lacking an
``id``) trigger JupyterLab's "recreate all cells on out-of-band edit"
path — ``jupyter_ydoc``'s ID-keyed cell diff falls through to
delete-and-reinsert, bloating the YDoc room by the full notebook size on
every autosave/file-touch. This assigns a ``uuid4().hex`` ``id`` to every
ID-less cell and bumps ``nbformat_minor`` to 5, which lets the diff apply
a small delta instead. See ``hera/docs/iris-mining-followups.md`` and the
detector in ``src/tools/nb_collab.py`` (``_warn_if_legacy_format``).

Idempotent: a notebook that's already 4.5-with-IDs is left untouched.

IMPORTANT: stop JupyterLab before running this. It rewrites the .ipynb
on disk; doing that while JL holds the notebook open is itself an
out-of-band edit (the thing we're trying to stop hurting).

Usage:
    uv run python scripts/upgrade_notebook_cellids.py PATH [PATH ...]
    uv run python scripts/upgrade_notebook_cellids.py --dry-run DIR

PATH may be a .ipynb file or a directory (its top-level *.ipynb are
processed; not recursive). Writes preserve Jupyter's on-disk format
(UTF-8, indent=1) so unicode isn't escaped and the diff stays minimal.
"""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from pathlib import Path


def _iter_notebooks(paths: list[str]):
    for p in paths:
        path = Path(p).expanduser()
        if path.is_dir():
            yield from sorted(path.glob("*.ipynb"))
        else:
            yield path


def upgrade(path: Path, *, dry_run: bool) -> tuple[int, bool]:
    """Return (cells_assigned_ids, minor_bumped) for one notebook."""
    with path.open("r", encoding="utf-8") as f:
        nb = json.load(f)

    cells = nb.get("cells", [])
    assigned = 0
    for cell in cells:
        if "id" not in cell:
            cell["id"] = uuid.uuid4().hex
            assigned += 1

    bumped = nb.get("nbformat_minor", 0) < 5
    if bumped:
        nb["nbformat_minor"] = 5

    if (assigned or bumped) and not dry_run:
        # ensure_ascii=False + indent=1 matches nbformat's on-disk writer,
        # so we don't escape unicode or reflow the whole file.
        with path.open("w", encoding="utf-8") as f:
            json.dump(nb, f, indent=1, ensure_ascii=False)
            f.write("\n")

    return assigned, bumped


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Upgrade legacy notebooks to nbformat 4.5 with uuid cell IDs."
    )
    ap.add_argument("paths", nargs="+", help=".ipynb files or directories")
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="report what would change without writing",
    )
    args = ap.parse_args(argv)

    notebooks = list(_iter_notebooks(args.paths))
    if not notebooks:
        print("no .ipynb files found", file=sys.stderr)
        return 1

    any_changed = False
    for path in notebooks:
        try:
            assigned, bumped = upgrade(path, dry_run=args.dry_run)
        except (OSError, json.JSONDecodeError) as e:
            print(f"{path}: ERROR {e}", file=sys.stderr)
            continue

        if assigned or bumped:
            any_changed = True
            verb = "would assign" if args.dry_run else "assigned"
            bump_note = " + bumped to nbformat 4.5" if bumped else ""
            print(f"{path}: {verb} {assigned} cell ID(s){bump_note}")
        else:
            print(f"{path}: already 4.5 with IDs (no change)")

    if args.dry_run and any_changed:
        print("\n[dry-run] re-run without --dry-run to apply", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
