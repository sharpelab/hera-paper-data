"""Spot-check read: runs 6 (electron, n=+3.2e12) and 7 (hole, n=-1.2e12).
Onset, tone frequencies vs F_L, resolution delta-F. Inputs to the fan design."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from hera.analysis import (open_run, summarize_run, resolve_channels,
                           sdh_onset, sdh_fft, luttinger_frequency, SdhOnsetError)

D = Path("/home/hera/measurements/zack/20260822-vti-02/data")

CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)

for rid, nspot in ((6, +3.20), (7, -1.20)):
    r = open_run(D / str(rid))
    print("=" * 70)
    print(f"RUN {rid}  n = {nspot:+.2f}e12 cm^-2")
    print(summarize_run(r))
    print("cols:", r.cols)
    chans = resolve_channels(r.meta)
    for c in chans:
        print("  chan:", c)
    mc = r.meta["measurement_config"]
    print("meas_config:", {k: v for k, v in mc.items() if "gain" in str(k).lower()
                           or "sens" in str(k).lower() or "amp" in str(k).lower()
                           or "curr" in str(k).lower()})
    print("mc keys:", list(mc.keys()))
print("done")
