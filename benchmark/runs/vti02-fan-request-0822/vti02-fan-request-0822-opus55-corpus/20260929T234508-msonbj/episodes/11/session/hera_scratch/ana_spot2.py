"""Spot checks 6/7, second pass: model F(n)/m*(n) table over the fan-candidate windows; zero-padded FFT
(sdh_fft, nfft large) with windows above onset; the low-B part of run 6 is 50 mT-sampled (Nyquist-limited)."""
import sys, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from hera.analysis import open_run, sdh_fft, luttinger_frequency
sys.path.insert(0, str(Path.home() / "measurement_env/hera/models/tetralayer_fs_count"))
import fs_count_b0 as M

print("model table (u_D = 0):  n[1e12]  F_L | ABAB tones (m*) | ABCA F (m*)")
for n in (-1.27, -1.0, -0.7, -0.4, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.27):
    ab = M.abab_mstar(n * 1e16); Fa, ma = M.abca_mstar(n * 1e16)
    print(f"  {n:+5.2f}  {float(luttinger_frequency(n*1e16)):5.1f} | " + ", ".join(f"{F:.2f}({m:.3f})" for F, m in ab)
          + f" | {Fa:.2f} ({ma:.3f})")

D = Path(__file__).resolve().parent.parent / "data"
fig, ax = plt.subplots(2, 2, figsize=(13, 8))
for j, (rid, n12, wins) in enumerate([(6, 3.2, [(1.0, 10), (1.5, 10), (2.0, 10), (1.0, 5.0), (5.0, 10)]),
                                     (7, -1.2, [(0.7, 10), (1.0, 10), (1.5, 10), (0.7, 3.0), (3.0, 10)])]):
    r = open_run(D / str(rid)); B = r.col("magnet_field"); R = np.abs(r.col("sr1_X") / (r.col("sr0_X") / -1e6))
    o = np.argsort(B); B, R = B[o], R[o]
    FL = float(luttinger_frequency(n12 * 1e16))
    for lo, hi in wins:
        f, sp = sdh_fft(R[:, None], B, b_range=(lo, hi), bg_degree=5, log=False, nfft=1 << 15)
        s = sp[0]; sel = f > 1.5
        pk = [k for k in range(1, len(f) - 1) if s[k] > s[k - 1] and s[k] > s[k + 1] and f[k] > 1.5]
        pk = sorted(pk, key=lambda k: -s[k])[:7]
        print(f"run {rid} F_L={FL:.1f}  window {lo}-{hi} T (dF {1/(1/lo-1/hi):.2f} T): "
              + ", ".join(f"{f[k]:.2f}({s[k]/s[pk[0]]:.2f})" for k in sorted(pk)))
        if hi == 10:
            ax[0, j].plot(f, s / s[sel].max(), lw=0.8, label=f"{lo}-{hi} T")
    ax[0, j].axvline(FL, color="k", ls="--", label="F_L")
    for F, _ in M.abab_fs(n12 * 1e16)[1]: ax[0, j].axvline(F, color="b", ls=":", lw=1)
    ax[0, j].set_xlim(0, 2.5 * FL); ax[0, j].legend(fontsize=7); ax[0, j].set_title(f"run {rid} FFT (blue: ABAB model, k: F_L)")
    m = B > 0.7
    cf = np.polyfit(B[m], R[m], 7); ax[1, j].plot(1 / B[m], R[m] - np.polyval(cf, B[m]), lw=0.6)
    ax[1, j].set_xlabel("1/B"); ax[1, j].set_title(f"run {rid} dR (deg-7 bg in B, B>0.7 T)")
fig.tight_layout(); fig.savefig(Path(__file__).parent / "spot_runs67_fft.png", dpi=90)
# noise floor of run 6 at low B (1-2 T), residual rms
r = open_run(D / "6"); B = r.col("magnet_field"); R = np.abs(r.col("sr1_X") / (r.col("sr0_X") / -1e6))
m = (B > 1.0) & (B < 2.0); d = np.diff(R[m])
print(f"run 6 point-to-point noise 1-2 T: rms dR/sqrt2 = {np.std(d)/np.sqrt(2):.1f} Ohm; mean R {R[m].mean():.1f}")
r = open_run(D / "7"); B = r.col("magnet_field"); R = np.abs(r.col("sr1_X") / (r.col("sr0_X") / -1e6))
m = (B > 1.0) & (B < 2.0); d = np.diff(R[np.argsort(B)][np.sort(B) > 0][(np.sort(B) > 1) & (np.sort(B) < 2)])
print(f"run 7 point-to-point noise 1-2 T: rms dR/sqrt2 = {np.std(d)/np.sqrt(2):.1f} Ohm")
