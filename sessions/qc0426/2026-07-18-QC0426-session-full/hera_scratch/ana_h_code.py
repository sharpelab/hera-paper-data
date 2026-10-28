# hole side: stitched raw + tone tables + FFT vs hole-scale F_L
import numpy as np
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_onset, sdh_fft

I_BIAS = 20e-9
r7, r8 = open_run("data/7"), open_run("data/8")
B7, B8 = r7.col_at(4), r8.col_at(4)
o7, o8 = np.argsort(B7), np.argsort(B8)

fig, axes = plt.subplots(2, 1, figsize=(11, 6), sharex=True)
for ax, ch in zip(axes, ("sr1", "sr2")):
    ax.plot(B8[o8], np.abs(r8.col(f"{ch}_X"))[o8] / I_BIAS, lw=0.5, label="run 8 (1-8 T)")
    ax.plot(B7[o7], np.abs(r7.col(f"{ch}_X"))[o7] / I_BIAS, lw=0.5, alpha=0.7, label="run 7 (0.5-2 T fine)")
    ax.set_ylabel(f"{ch} |R| (Ω)"); ax.legend(fontsize=8)
axes[-1].set_xlabel("B (T)")
fig.suptitle("hole n(−6e12 label) spot check, D = 0: raw records (runs 7+8)")
fig.tight_layout(); plt.show()

for ch, sens in (("sr1", 1e-5), ("sr2", 5e-6)):
    R = np.abs(r8.col(f"{ch}_X"))[o8] / I_BIAS
    on = sdh_onset(R, B8[o8], r_full_scale=sens / I_BIAS)
    print(f"=== {ch} (run 8) ===\n{on.summary()}\n")

fig2, ax2 = plt.subplots(figsize=(10, 4.5))
for ch, sens in (("sr1", 1e-5), ("sr2", 5e-6)):
    R = np.abs(r8.col(f"{ch}_X"))[o8] / I_BIAS
    on = sdh_onset(R, B8[o8], r_full_scale=sens / I_BIAS)
    b_hi = on.clip_high_b if on.clip_high_b else B8[o8].max()
    f, s = sdh_fft(R[:, None], B8[o8], b_range=(1.2, b_hi), nfft=4096)
    ax2.plot(f, s[0], lw=1, label=f"{ch} [1.2-{b_hi:.1f} T]")
ax2.axvline(65.6, color="k", ls="--", lw=0.8, label="F_L hole scale (65.6 T)")
ax2.set_xlim(0, 160); ax2.set_xlabel("F (T)"); ax2.set_ylabel("FFT amp"); ax2.legend(fontsize=8)
fig2.suptitle("run 8 FFT: hole-side pair {11, 54.5}, partition ≈ F_L(hole)")
fig2.tight_layout(); plt.show()
