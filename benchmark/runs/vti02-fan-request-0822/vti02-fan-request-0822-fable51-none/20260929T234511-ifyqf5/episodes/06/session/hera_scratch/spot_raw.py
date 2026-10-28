import numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from pathlib import Path
from hera.analysis import open_run, resolve_channels, summarize_run
fig, ax = plt.subplots(2, 2, figsize=(13, 8))
for k, rid in enumerate([6, 7]):
    r = open_run(Path("data") / str(rid))
    print(summarize_run(r))
    ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col("magnet_field"); I = r.col("sr0_X") / ch["sr0"].gain
    R = (r.col("sr1_X") / ch["sr1"].gain) / I
    T = r.col("T_sample")
    print(f"run {rid}: B {B.min():.2f}-{B.max():.2f}, R {R.min():.1f}..{R.max():.1f} Ohm, R(Bmin)={R[np.argmin(B)]:.1f}, I {I.min()*1e9:.2f}-{I.max()*1e9:.2f} nA, T {T.min():.3f}-{T.max():.3f} K, npts {len(B)}")
    o = np.argsort(B)
    ax[0, k].plot(B[o], R[o], "-", lw=0.7); ax[0, k].set_xlabel("B (T)"); ax[0, k].set_ylabel("Rxx (Ohm)"); ax[0, k].set_title(f"run {rid}: {r.meta['comments'][1][:60]}")
    m = B > 1.5
    ax[1, k].plot(1 / B[o][m[o]], R[o][m[o]], "-", lw=0.7); ax[1, k].set_xlabel("1/B (1/T)"); ax[1, k].set_ylabel("Rxx (Ohm)")
    np.save(f"hera_scratch/run{rid}_BR.npy", np.vstack([B[o], R[o]]))
fig.tight_layout(); fig.savefig("hera_scratch/spot_raw.png", dpi=110)
