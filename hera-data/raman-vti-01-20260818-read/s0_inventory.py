#!/usr/bin/env python3
"""Step 0 — inventory the vti-01.wip WITec project: every data item,
its type, shape, and full measurement metadata. No spectral analysis here."""
import json
import sys
from pathlib import Path

import numpy as np
import witio

WIP = Path(__file__).parent / "inputs" / "vti-01.wip"

proj = witio.read(str(WIP))
print(f"project: {WIP}")
print(f"n data items: {len(proj.data)}")
print()

for k, d in enumerate(proj.data):
    print(f"=== item {k}: caption={d.caption!r} type={type(d).__name__}")
    try:
        arr = np.asarray(d.array())
        print(f"    array shape: {arr.shape} dtype={arr.dtype}")
    except Exception as e:
        print(f"    array: <unavailable: {e}>")
    try:
        xa = d.x_axis()
        if isinstance(xa, tuple):
            for i, x in enumerate(xa):
                x = np.asarray(x)
                print(f"    x_axis[{i}]: shape={x.shape} "
                      f"range {x.min():.2f}..{x.max():.2f}")
        else:
            x = np.asarray(xa)
            print(f"    x_axis: shape={x.shape} range {x.min():.2f}..{x.max():.2f}")
    except Exception as e:
        print(f"    x_axis: <unavailable: {e}>")
    try:
        meta = d.measurement_metadata
        meta = meta() if callable(meta) else meta
        if meta:
            print("    metadata:")
            print(json.dumps(meta, indent=6, default=str))
        else:
            print("    metadata: (none)")
    except Exception as e:
        print(f"    metadata: <error: {e}>")
    # dump any other attributes that look informative
    for attr in dir(d):
        if attr.startswith("_") or attr in ("array", "x_axis", "caption",
                                            "measurement_metadata"):
            continue
        try:
            v = getattr(d, attr)
            if callable(v):
                continue
            s = repr(v)
            if len(s) > 300:
                s = s[:300] + "..."
            print(f"    .{attr} = {s}")
        except Exception:
            pass
    print()
