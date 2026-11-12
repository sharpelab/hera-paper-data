# === Runs 6 & 7 — RAW: gain-divided R_xx(B), no background removal ===
import numpy as np, matplotlib.pyplot as plt
from hera.analysis import open_run, resolve_channels, current_channel

def spot_trace(rid):
    run = open_run(f"data/{rid}")
    ch = resolve_channels(run.meta, include=["sr0", "sr1"])
    cur = current_channel(ch)
    v = [c for c in ch if c is not cur][0]
    B = np.asarray(run.col("magnet_field"), float)
    I = np.abs(np.asarray(run.col(cur.col), float) / cur.gain)
    R = np.abs(np.asarray(run.col(v.col), float) / v.gain) / I
    o = np.argsort(B)
    return B[o], R[o], float(np.median(I))

fig, ax = plt.subplots(1, 2, figsize=(12, 4))
for a, (rid, lab) in zip(ax, [(6, "run 6 — electron, n = +3.2e12"),
                              (7, "run 7 — hole, n = -1.2e12")]):
    B, R, Imed = spot_trace(rid)
    a.plot(B, R, lw=0.6)
    a.set(xlabel="B (T)", ylabel="R_xx sr1 (Ohm)", title=f"{lab}  (I = {Imed*1e9:.1f} nA)")
    print(f"run {rid}: R({B.min():.2f} T) = {R[0]:.0f} Ohm, R_max = {R.max():.0f} Ohm at {B[np.argmax(R)]:.2f} T")
fig.tight_layout()
