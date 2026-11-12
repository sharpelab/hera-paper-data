"""Raw look at SdH spot checks runs 6 (e-side, 0->10 T) and 7 (h-side, 10->0.3 T): R(B), R(1/B), stats."""
import numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from hera.analysis import open_run, summarize_run, resolve_channels
fig, ax = plt.subplots(2, 2, figsize=(13, 8))
for k, rid in enumerate((6, 7)):
    r = open_run(f"data/{rid}")
    print(summarize_run(r))
    ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col("magnet_field"); I = r.col("sr0_X") / ch["sr0"].gain
    R = (r.col("sr1_X") / ch["sr1"].gain) / I
    T = r.col("T_sample")
    o = np.argsort(B); B, R, I, T = B[o], R[o], I[o], T[o]
    print(f"run {rid}: {len(B)} pts, B {B.min():.3f}..{B.max():.3f}, dB med {np.median(np.diff(B))*1e3:.1f} mT; R {R.min():.1f}..{R.max():.1f} Ohm; "
          f"R(B<0.1)={np.median(R[B<0.35]):.1f}; I {I.min()*1e9:.2f}..{I.max()*1e9:.2f} nA; T {T.min():.3f}..{T.max():.3f} K; interrupted {r.interrupted}")
    ax[k, 0].plot(B, R, "-", lw=0.8); ax[k, 0].set_xlabel("B (T)"); ax[k, 0].set_ylabel("Rxx B_1-B_2 (Ohm)"); ax[k, 0].set_title(f"run {rid} raw R(B)")
    m = B > 1.0
    ax[k, 1].plot(1 / B[m], R[m], "-", lw=0.8); ax[k, 1].set_xlabel("1/B (1/T)"); ax[k, 1].set_ylabel("Rxx (Ohm)"); ax[k, 1].set_title(f"run {rid} R(1/B), B>1 T")
fig.tight_layout(); fig.savefig("hera_scratch/raw_spot_6_7.png", dpi=100); print("saved")
