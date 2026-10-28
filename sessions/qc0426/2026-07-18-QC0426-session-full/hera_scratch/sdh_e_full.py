"""Electron side full read: run 6 (2-8 T, unclipped) + run 5 (0.5-2.4 T fine).
FFT stability sweep + harmonic screen + Luttinger scale pin (scratch)."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_onset, sdh_fft, SdhOnsetError

I_BIAS = 20e-9
r5, r6 = open_run("data/5"), open_run("data/6")
B5, B6 = r5.col_at(4), r6.col_at(4)
o6 = np.argsort(B6)  # run 6 acquired descending

fig, axes = plt.subplots(2, 1, figsize=(11, 6), sharex=True)
for ax, ch, sens6 in ((axes[0], "sr1", 1e-5), (axes[1], "sr2", 5e-6)):
    R6 = np.abs(r6.col(f"{ch}_X"))[o6] / I_BIAS
    ax.plot(B6[o6], R6, lw=0.5, label=f"run 6 ({ch})")
    R5 = np.abs(r5.col(f"{ch}_X")) / I_BIAS
    m5 = B5 < 2.3
    ax.plot(B5[m5], R5[m5], lw=0.5, alpha=0.7, label="run 5 (fine, unclipped part)")
    ax.set_ylabel(f"{ch} |R| (Ohm)"); ax.legend(fontsize=8)
axes[-1].set_xlabel("B (T)")
fig.suptitle("electron n=+6e12 D=0: stitched record (runs 5+6)")
fig.tight_layout(); fig.savefig("hera_scratch/sdh_e_stitch.png", dpi=110)

# onset objects on run 6 (full quality, 2-8 T)
print("========== run 6 (2-8 T, unclipped) ==========")
tones6 = {}
for ch, sens in (("sr1", 1e-5), ("sr2", 5e-6)):
    R6 = np.abs(r6.col(f"{ch}_X"))[o6] / I_BIAS
    try:
        on = sdh_onset(R6, B6[o6], r_full_scale=sens / I_BIAS)
        tones6[ch] = on
        print(f"=== {ch} ===\n{on.summary()}")
    except SdhOnsetError as e:
        print(f"=== {ch} === {e}")

# FFT stability: vary bg_degree and window length per channel
print("\n========== FFT stability sweep (run 6) ==========")
for ch in ("sr1", "sr2"):
    R6 = np.abs(r6.col(f"{ch}_X"))[o6] / I_BIAS
    for bg_deg in (3, 5, 7):
        for brange in ((2.0, 8.0), (2.5, 8.0), (2.0, 6.0)):
            freqs, spec = sdh_fft(R6[:, None], B6[o6], b_range=brange, bg_degree=bg_deg, nfft=4096)
            pk = []
            sp = spec[0]
            for i in range(2, len(freqs) - 2):
                if sp[i] == max(sp[max(0, i-8):i+9]) and sp[i] > 0.30 * sp[freqs < 150].max() and 3 < freqs[i] < 150:
                    pk.append(round(float(freqs[i]), 1))
            print(f"{ch} deg={bg_deg} B={brange}: peaks {pk[:8]}")

# headline FFT figure
fig2, ax2 = plt.subplots(figsize=(10, 4.5))
for ch in ("sr1", "sr2"):
    R6 = np.abs(r6.col(f"{ch}_X"))[o6] / I_BIAS
    freqs, spec = sdh_fft(R6[:, None], B6[o6], b_range=(2.0, 8.0), nfft=4096)
    ax2.plot(freqs, spec[0], lw=1, label=f"{ch} run6 [2-8 T]")
ax2.axvline(62.0, color="k", ls="--", lw=0.8, label="F_L geometry scale (62 T)")
ax2.axvline(68.2, color="r", ls=":", lw=0.8, label="F_L Hall scale (68 T)")
ax2.set_xlim(0, 160); ax2.set_xlabel("F (T)"); ax2.set_ylabel("FFT amp"); ax2.legend(fontsize=8)
fig2.suptitle("electron SdH FFT, unclipped 2-8 T record (dF ~ 2.7 T; with run 5: dF ~ 1.4 T)")
fig2.tight_layout(); fig2.savefig("hera_scratch/sdh_e_fft_full.png", dpi=110)
print("saved figs")
