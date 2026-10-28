"""Run 6 (electron) FFT stability sweep: windows and bg_degree, against F_L = 33.1 T.
The degree-5 background over the full 0.3-10 T window does not capture the 8-9 T peak
(see spot_runs67.png) -- redo on restricted windows."""
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_fft, luttinger_frequency

I_BIAS = 10.0e-9
n_cm2 = 3.20e12
F_L = float(luttinger_frequency(n_cm2 * 1e4))
r = open_run("data/6")
B = r.col("magnet_field"); R = r.col("sr1_X") / I_BIAS
o = np.argsort(B); B, R = B[o], R[o]

WINDOWS = [(0.8, 7.0), (1.0, 7.0), (1.5, 7.0), (1.0, 5.0), (1.0, 10.0), (2.0, 10.0)]
fig, axes = plt.subplots(2, 3, figsize=(15, 7.5), sharex=True)
print(f"F_L = {F_L:.1f} T;  ABAB template 0.72/0.28 -> {0.72*F_L:.1f} / {0.28*F_L:.1f} T")
for ax, (lo, hi) in zip(axes.ravel(), WINDOWS):
    dF = 1.0 / (1.0 / lo - 1.0 / hi)
    for deg, sty in ((3, ":"), (5, "-"), (7, "--")):
        f, spec = sdh_fft(R[:, None], B, b_range=(lo, hi), bg_degree=deg, nfft=4096, log=False)
        s = spec[0]; k = (f > 2.5) & (f < 45)
        ax.plot(f[k], s[k] / s[k].max(), sty, lw=0.9, label=f"deg {deg}")
        # local maxima
        ss = s[k]; ff = f[k]
        pk = [i for i in range(1, len(ss) - 1) if ss[i] > ss[i-1] and ss[i] > ss[i+1] and ss[i] > 0.15 * ss.max()]
        pk = sorted(pk, key=lambda i: -ss[i])[:5]
        print(f"  win {lo:.1f}-{hi:.1f} T (dF {dF:.2f} T) deg{deg}: "
              + ", ".join(f"{ff[i]:.1f}T[{ss[i]/ss.max():.2f}, {ff[i]/F_L:.2f}FL]" for i in pk))
    ax.axvline(F_L, color="k", ls=":"); ax.axvline(0.72*F_L, color="r", ls=":", lw=0.8)
    ax.axvline(0.28*F_L, color="r", ls=":", lw=0.8)
    ax.set_title(f"B {lo}-{hi} T   $\\delta F$ = {dF:.2f} T", fontsize=9)
    ax.set_xlim(0, 45); ax.legend(fontsize=6)
    ax.set_xlabel("F (T)")
    print()
fig.suptitle(f"run 6 electron n=+3.2e12, FFT stability (black $F_L$={F_L:.1f} T, red ABAB 0.72/0.28)", fontsize=10)
fig.tight_layout()
fig.savefig("hera_scratch/spot_run6_stability.png", dpi=110)
print("wrote hera_scratch/spot_run6_stability.png")
