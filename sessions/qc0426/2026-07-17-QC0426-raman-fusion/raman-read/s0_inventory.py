import sys, json
import numpy as np
sys.path.insert(0, "/home/zack/sharpelab/measurement-env/.worktrees/raman_stacking_lit/hera/models/raman_stacking")
from raman_io import load_wip

WIP = "/data/sharpelab/hera-data/raman-qc0426/06_3LGr-device.wip"
ds = load_wip(WIP)
for d in ds:
    print("="*70)
    print("caption:", d["caption"])
    print("nx,ny:", d["nx"], d["ny"], " n_wn:", d["wn"].size,
          " wn range: %.1f..%.1f" % (d["wn"].min(), d["wn"].max()))
    meta = d["meta"]
    print("meta keys:", sorted(meta.keys()) if isinstance(meta, dict) else type(meta))
    if isinstance(meta, dict):
        for k, v in sorted(meta.items()):
            s = str(v)
            if len(s) > 200: s = s[:200] + "..."
            print("  %s = %s" % (k, s))
