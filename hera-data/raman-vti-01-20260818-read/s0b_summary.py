#!/usr/bin/env python3
"""Step 0 (condensed) — one-line table of all project items; full metadata
for spectral TDGraph items; transformation params for video images (µm
registration); no spectral analysis."""
import json
from pathlib import Path

import numpy as np
import witio

WIP = Path(__file__).parent / "inputs" / "vti-01.wip"
proj = witio.read(str(WIP))

print("== one-line table ==")
for k, d in enumerate(proj.data):
    shape = ""
    try:
        shape = str(np.asarray(d.array()).shape)
    except Exception:
        pass
    print(f"{k:3d}  id={d.id:<4} {d.class_name:<28} {shape:<20} {d.caption}")

print()
print("== TDGraph (spectral) items: full metadata ==")
for k, d in enumerate(proj.data):
    if d.class_name != "TDGraph":
        continue
    meta = d.measurement_metadata
    meta = meta() if callable(meta) else meta
    arr = np.asarray(d.array())
    xa = d.x_axis()
    x = np.asarray(xa[0] if isinstance(xa, tuple) else xa, float).ravel()
    print(f"--- item {k}: {d.caption!r} shape={arr.shape} "
          f"x-range {x.min():.1f}..{x.max():.1f} n_x={x.size}")
    print(json.dumps(meta or {}, indent=2, default=str))
    print()

print("== TDSpaceTransformation payloads (registration) ==")
def walk(tag, depth=0):
    val = ""
    if tag.data is not None:
        s = repr(tag.data)
        val = s if len(s) < 120 else s[:120] + "..."
    print("  " * depth + f"{tag.name}: {val}")
    for c in tag.children:
        walk(c, depth + 1)

for k, d in enumerate(proj.data):
    if d.class_name != "TDSpaceTransformation":
        continue
    print(f"--- item {k}: {d.caption!r}")
    walk(d.payload, 1)
    print()
