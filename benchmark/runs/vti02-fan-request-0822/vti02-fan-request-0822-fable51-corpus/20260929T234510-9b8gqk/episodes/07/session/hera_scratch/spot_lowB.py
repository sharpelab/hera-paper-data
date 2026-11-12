"""Low-field envelope of the light tone: where does it die? Runs 6 (e) and 7 (h)."""
import numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_onset
fig, axs = plt.subplots(2, 2, figsize=(14, 8))
for j, (rid, lo) in enumerate([(6, 0.3), (7, 0.3)]):
    r = open_run(f"data/{rid}"); B = r.col("magnet_field"); R = (r.col("sr1_X")) / (r.col("sr0_X") / -1e6)
    o = np.argsort(B); B, R = B[o], R[o]
    m = (B >= 0.3) & (B <= 3.0); cf = np.polyfit(B[m], R[m], 4); dR = R[m] - np.polyval(cf, B[m])
    axs[0, j].plot(B[m], dR, ".-", ms=3, lw=0.7); axs[0, j].axvline(1.0, color="r", ls=":"); axs[0, j].set_title(f"run {rid}: dR (deg-4 bg over 0.3-3 T) vs B"); axs[0, j].set_xlabel("B (T)")
    axs[1, j].plot(1/B[m], dR, ".-", ms=3, lw=0.7); axs[1, j].set_xlabel("1/B (1/T)"); axs[1, j].set_xlim(0.3, 1/0.3)
    # per-window pk-pk amplitude and noise estimate (diff-based) in 0.1 T bins
    print(f"run {rid}: B-bin  pk-pk dR   dB step   Δ(1/B)")
    for b0 in np.arange(0.4, 2.01, 0.1):
        s = (B >= b0) & (B < b0 + 0.1)
        if s.sum() < 3: continue
        step = np.median(np.diff(B[s])) if s.sum() > 1 else np.nan
        print(f"   {b0:.1f}-{b0+0.1:.1f} T: {np.ptp(dR[s[m]]):6.2f} Ohm  {step*1e3:4.0f} mT  {step/b0**2:.3f} 1/T  (n={s.sum()})")
    try:
        on = sdh_onset(R, B, r_full_scale=5000, b_lo=lo, b_hi=4.0); print(on.summary())
    except Exception as e: print("onset(0.3-4):", e)
fig.tight_layout(); fig.savefig("hera_scratch/spot_lowB.png", dpi=110)
