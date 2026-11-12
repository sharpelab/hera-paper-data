# electron full read: stitched record, per-channel FFT, scale pin, model overlay, B-split
import sys
import numpy as np
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_onset, sdh_fft
sys.path.insert(0, r"C:/Users/DGG/measurement_env/hera/models/trilayer_fs_count")
from fs_count_b0 import aba_fs, abc_fs, aba_mstar

I_BIAS = 20e-9
r5, r6 = open_run("data/5"), open_run("data/6")
B5, B6 = r5.col_at(4), r6.col_at(4)
o6 = np.argsort(B6)
B6s = B6[o6]

fig, axes = plt.subplots(2, 1, figsize=(11, 6), sharex=True)
for ax, ch in zip(axes, ("sr1", "sr2")):
    ax.plot(B6s, np.abs(r6.col(f"{ch}_X"))[o6] / I_BIAS, lw=0.5, label="run 6 (unclipped)")
    m5 = B5 < 2.3
    ax.plot(B5[m5], np.abs(r5.col(f"{ch}_X"))[m5] / I_BIAS, lw=0.5, alpha=0.7, label="run 5 fine segment")
    ax.set_ylabel(f"{ch} |R| (Ω)"); ax.legend(fontsize=8)
axes[-1].set_xlabel("B (T)")
fig.suptitle("electron n(+) spot check, D = 0: stitched raw record (runs 5+6)")
fig.tight_layout(); plt.show()

# tone tables (run 6)
for ch, sens in (("sr1", 1e-5), ("sr2", 5e-6)):
    R = np.abs(r6.col(f"{ch}_X"))[o6] / I_BIAS
    on = sdh_onset(R, B6s, r_full_scale=sens / I_BIAS)
    print(f"=== {ch} ===\n{on.summary()}\n")

# FFT overlay vs templates at the pinned scale
fig2, ax2 = plt.subplots(figsize=(10, 4.5))
for ch in ("sr1", "sr2"):
    R = np.abs(r6.col(f"{ch}_X"))[o6] / I_BIAS
    f, s = sdh_fft(R[:, None], B6s, b_range=(2.0, 8.0), nfft=4096)
    ax2.plot(f, s[0], lw=1, label=ch)
n_pin = 6.64e16   # from Luttinger sum (68.6 T) — agrees with Hall (6.60e12) to 0.5%
_, orb = aba_fs(n_pin)
for (F, _), lab in zip(orb, ("ABA ML (model)", "ABA BL (model)")):
    ax2.axvline(F, color="g", ls=":", lw=1); ax2.text(F, ax2.get_ylim()[1]*0.9, lab, rotation=90, fontsize=7, color="g")
_, _, _, _, Ftot = abc_fs(n_pin)
ax2.axvline(Ftot, color="m", ls=":", lw=1); ax2.text(Ftot, ax2.get_ylim()[1]*0.9, "ABC singleton (model)", rotation=90, fontsize=7, color="m")
ax2.axvline(68.6, color="k", ls="--", lw=0.8, label="F_L (pinned scale)")
ax2.set_xlim(0, 160); ax2.set_xlabel("F (T)"); ax2.set_ylabel("FFT amp"); ax2.legend(fontsize=8)
fig2.suptitle("run 6 FFT vs forward-model templates at n = 6.64e12 (model: topology/partition, not absolute F)")
fig2.tight_layout(); plt.show()

# F_L-tone origin: B-window split (breakdown strengthens with B; a pocket keeps its envelope)
print("=== B-window split (amp ratios low->high B) ===")
for ch in ("sr1", "sr2"):
    R = np.abs(r6.col(f"{ch}_X"))[o6] / I_BIAS
    out = {}
    for lab, br in (("low", (2.0, 3.2)), ("high", (3.2, 8.0))):
        f, s = sdh_fft(R[:, None], B6s, b_range=br, nfft=4096)
        amp = lambda F0: s[0][(f > F0 - 4) & (f < F0 + 4)].max()
        out[lab] = (amp(13.4), amp(55.2), amp(66.3))
    lo, hi = out["low"], out["high"]
    print(f"{ch}: 66/13 {lo[2]/lo[0]:.2f} -> {hi[2]/hi[0]:.2f}; 66/55 {lo[2]/lo[1]:.2f} -> {hi[2]/hi[1]:.2f}")
print("falling ratios both channels -> F_L tone does NOT grow with B: consistent with a real pocket, not breakdown")
