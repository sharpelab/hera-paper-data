# Runs 6-7 raw: gain-divided Rxx(B), no background removal.
import numpy as np
import matplotlib.pyplot as plt
from hera.analysis import open_run

spots = {}
fig, ax = plt.subplots(1, 2, figsize=(12, 4))
for j, (fid, lab, FL) in enumerate(((6, "electron n = +3.2e12", 33.1),
                                    (7, "hole n = -1.2e12", 12.4))):
    r = open_run(f"data/{fid}")
    B = r.col("magnet_field")
    i_med = np.median(np.abs(r.col("sr0_X") / -1e6))          # drain current, Ithaco -1e6
    Rxx = r.col("sr1_X") / i_med
    o = np.argsort(B)
    spots[fid] = (B[o], Rxx[o], i_med, lab, FL)
    ax[j].plot(B[o], Rxx[o], lw=0.6)
    ax[j].set_title(f"run {fid} — {lab} (I = {i_med*1e9:.1f} nA)")
    ax[j].set_xlabel("B (T)"); ax[j].set_ylabel("Rxx (Ω)")
    print(f"run {fid}: complete={not r.interrupted}, T {r.col('T_sample').min():.3f}-{r.col('T_sample').max():.3f} K, "
          f"|I_tg|max {np.abs(r.col('k_2400_tg_curr')).max()*1e12:.0f} pA, "
          f"|I_bg|max {np.abs(r.col('k_2400_bg_curr')).max()*1e12:.0f} pA, "
          f"sr1 |X|max {np.abs(r.col('sr1_X')).max()*1e6:.1f} of 50 uV FS")
fig.tight_layout()
