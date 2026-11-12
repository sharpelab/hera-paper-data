"""Run 6 (electron) — per-tone SNR-vs-B tracks, to see how far below 1 T the
dominant tones would survive. Run 6's B grid is 50 mT below 1 T (Nyquist in 1/B
at 0.8 T = 6.4 T), so the fast tones (22.9 / 29.9 T) are ALIASED there: the
electron onset is unmeasured below 1 T, not merely untracked.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_onset

run = open_run("/home/hera/measurements/zack/20260822-vti-02/data/6")
mc = run.meta["measurement_config"]
B = run.col("magnet_field")
R = np.abs((run.col("sr1_X") / 1.0) / (run.col("sr0_X") / mc["sr0_gain"]))
k = B > 0.05
B, R = B[k], R[k]
o = np.argsort(B); B, R = B[o], R[o]

# Nyquist of the two sampling legs
for Bx, dB in ((0.5, 0.05), (0.8, 0.05), (1.0, 0.01), (2.0, 0.01)):
    print(f"  at B={Bx} T, dB={dB*1e3:.0f} mT -> d(1/B)={dB/Bx**2:.5f} /T, f_Nyq={Bx**2/(2*dB):.1f} T")

on = sdh_onset(R, B, b_lo=1.0, r_full_scale=5050.0)
print("\n" + on.summary())

fig, ax = plt.subplots(1, 2, figsize=(12, 4.5))
for t in on.tones:
    if t.freq < 2 or t.snr is None:
        continue
    ax[0].semilogy(t.b_centers, t.snr, "o-", ms=3, label=f"{t.freq:.1f} T")
ax[0].axhline(5, ls="--", c="k", label="SNR = 5")
ax[0].set(xlabel="B window centre (T)", ylabel="tone SNR",
          title="run 6 per-tone SNR vs B (b_lo = 1.0 T)")
ax[0].legend(fontsize=7, ncol=2)

# Dingle extrapolation: ln(amp) vs 1/B, linear fit on the tracked windows
print("\n-- Dingle extrapolation: ln(amp) ~ a - b/B; B where SNR crosses 5 --")
for t in on.tones:
    if t.freq < 5 or t.snr is None or len(t.b_centers) < 4:
        continue
    bc, sn = np.asarray(t.b_centers), np.asarray(t.snr)
    m = np.isfinite(sn) & (sn > 0)
    if m.sum() < 4:
        continue
    p = np.polyfit(1.0 / bc[m], np.log(sn[m]), 1)
    b_cross = -p[0] / (np.log(5.0) - p[1]) if (np.log(5.0) - p[1]) != 0 else np.nan
    b_cross = p[0] / (np.log(5.0) - p[1])
    ax[1].plot(1.0 / bc[m], np.log(sn[m]), "o", ms=3, label=f"{t.freq:.1f} T")
    xx = np.linspace(0.1, 2.2, 50)
    ax[1].plot(xx, np.polyval(p, xx), lw=0.7)
    print(f"  tone {t.freq:6.1f} T: slope {p[0]:+8.2f} (1/T), SNR=5 at B = "
          f"{1.0/((np.log(5.0)-p[1])/p[0]) if p[0] else float('nan'):.2f} T")
ax[1].axhline(np.log(5), ls="--", c="k")
ax[1].set(xlabel="1/B (1/T)", ylabel="ln SNR", title="Dingle extrapolation")
ax[1].legend(fontsize=7, ncol=2)
plt.tight_layout()
plt.savefig("/home/hera/measurements/zack/20260822-vti-02/hera_scratch/spot6_onset.png", dpi=110)
print("\nwrote spot6_onset.png")
