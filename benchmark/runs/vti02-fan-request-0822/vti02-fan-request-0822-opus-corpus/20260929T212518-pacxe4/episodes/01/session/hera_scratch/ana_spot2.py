"""Diagnostics: run 6 (electron) acquisition quality + the 7.5 T step; run 7 (hole) tone read."""
import json
from pathlib import Path
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_fft, luttinger_frequency

HERE = Path("/home/hera/measurements/zack/20260822-vti-02")

def load(rid):
    r = open_run(HERE / "data" / str(rid))
    B = r.col("magnet_field"); X = r.col("sr1_X")
    I = r.metadata["instruments"]["sr1"]["snapshot"]["parameters"]["amplitude"]["value"] / r.metadata["measurement_config"]["bias_resistor"]
    return r, B, np.abs(X) / I, X, I

r6, B6, R6, X6, I6 = load(6)
r7, B7, R7, X7, I7 = load(7)

print("=== run 6 digitization ===")
print(f"  sr1_X first 12 (V): {np.round(X6[:12]*1e6,4)} uV")
print(f"  unique X steps (sorted diffs of unique X), low-B B<2 T:")
x = np.unique(np.round(X6[B6 < 2], 12))
print(f"    n_unique={len(x)} over {np.sum(B6<2)} pts; min nonzero |dX| = {np.min(np.diff(x))*1e9:.4f} nV")
for lo, hi in [(0, 2), (2, 5), (5, 7.4), (7.6, 10)]:
    m = (B6 >= lo) & (B6 < hi)
    print(f"  B {lo}-{hi} T: R med {np.median(R6[m]):7.1f}  ptp {np.ptp(R6[m]):7.1f} Ohm   "
          f"X med {np.median(X6[m])*1e6:8.3f} uV  ({100*np.median(np.abs(X6[m]))/5e-5:.2f}% of 50uV FS)")
print("=== run 6: the step ===")
m = (B6 > 7.0) & (B6 < 8.2)
for b, rr, t, tg, bg, p in zip(B6[m], R6[m], r6.col("T_sample")[m], r6.col("k_2400_tg_curr")[m],
                               r6.col("k_2400_bg_curr")[m], r6.col("sr1_P")[m]):
    print(f"   B={b:6.3f}  R={rr:7.1f}  T={t:.3f}  I_tg={tg*1e12:+7.1f}pA I_bg={bg*1e12:+7.1f}pA  phase={p:+7.2f}")

print("\n=== run 7 tones ===")
n7 = -1.20e12; FL7 = luttinger_frequency(abs(n7) * 1e4)
ok = B7 > 0.3
fig, ax = plt.subplots(2, 2, figsize=(14, 8))
for cut, c in [(0.7, "C0"), (1.2, "C1"), (2.0, "C2")]:
    for deg, ls in [(3, ":"), (5, "-"), (7, "--")]:
        f, sp = sdh_fft(R7[ok][:, None], B7[ok], b_range=(cut, 10.0), bg_degree=deg, log=False, nfft=2048)
        s = sp[0] / sp[0][(f > 1.5)].max()
        ax[0, 0].plot(f, s, c, ls=ls, lw=0.8, label=f"cut{cut} deg{deg}")
        sel = (f > 1.5) & (f < 30)
        pk = [(f[sel][i], s[sel][i]) for i in np.argsort(s[sel])[::-1][:6]]
        pk = sorted(pk)
        print(f"  cut {cut} deg {deg}: peaks " + ", ".join(f"{a:.2f}T({b:.2f})" for a, b in pk)
              + f"   dF={1/(1/cut-1/10):.2f}")
for v, c, l in [(FL7, "k", "F_L"), (0.72 * FL7, "g", "0.72F_L"), (0.28 * FL7, "m", "0.28F_L")]:
    ax[0, 0].axvline(v, color=c, ls="--", lw=1, label=f"{l}={v:.1f}T")
ax[0, 0].set_xlim(0, 30); ax[0, 0].legend(fontsize=5, ncol=2); ax[0, 0].set_xlabel("F (T)")
ax[0, 0].set_title(f"run 7 (hole n={n7:+.2f}e12) FFT stability: cutoff x bg_degree")

# B-window split (F_L-tone origin test)
for (lo, hi), c in [((0.7, 2.2), "C0"), ((2.2, 10.0), "C3")]:
    f, sp = sdh_fft(R7[ok][:, None], B7[ok], b_range=(lo, hi), bg_degree=5, log=False, nfft=2048)
    s = sp[0] / sp[0][(f > 1.5)].max()
    ax[0, 1].plot(f, s, c, lw=1, label=f"B {lo}-{hi} T (dF={1/(1/lo-1/hi):.2f})")
ax[0, 1].axvline(FL7, color="k", ls="--", lw=1, label=f"F_L={FL7:.1f}")
ax[0, 1].set_xlim(0, 30); ax[0, 1].legend(fontsize=7); ax[0, 1].set_xlabel("F (T)")
ax[0, 1].set_title("run 7: low-B vs high-B halves")

ax[1, 0].plot(B6, R6, lw=0.6, label="run 6 (e, n=+3.2)")
ax[1, 0].plot(B7, R7, lw=0.6, label="run 7 (h, n=-1.2)")
ax[1, 0].set_xlabel("B (T)"); ax[1, 0].set_ylabel("Rxx (Ohm)"); ax[1, 0].legend(fontsize=7)
ax[1, 0].set_title("raw Rxx — run 6 sits at 1% of full scale below 7.5 T")
sel = (B7 > 0.7)
cf = np.polyfit(B7[sel], R7[sel], 5)
ax[1, 1].plot(1 / B7[sel], R7[sel] - np.polyval(cf, B7[sel]), lw=0.8)
ax[1, 1].set_xlabel("1/B (1/T)"); ax[1, 1].set_ylabel("dRxx (Ohm)")
ax[1, 1].set_title("run 7 bg-subtracted vs 1/B (deg 5, B>0.7 T)")
fig.tight_layout(); fig.savefig(HERE / "hera_scratch" / "spot_diag.png", dpi=110)
print("wrote spot_diag.png")
