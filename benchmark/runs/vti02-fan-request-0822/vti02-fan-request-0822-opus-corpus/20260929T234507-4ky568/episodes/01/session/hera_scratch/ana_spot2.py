"""Careful FFT of spot checks 6/7: log=False, well-sampled B windows only, window ladder."""
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_fft, luttinger_frequency

def load(rid):
    run = open_run(f"data/{rid}")
    inst = run.meta["instruments"]["sr1"]["snapshot"]["parameters"]
    I = inst["amplitude"]["value"] / run.meta["measurement_config"]["bias_resistor"]
    B = run.col("magnet_field"); R = run.col("sr1_X") / I
    o = np.argsort(B)
    return B[o], R[o], I

RUNS = {6: ("electron", +3.2), 7: ("hole", -1.2)}
fig, axes = plt.subplots(2, 3, figsize=(16, 8))
for k, (rid, (side, n12)) in enumerate(RUNS.items()):
    B, R, I = load(rid)
    F_L = luttinger_frequency(abs(n12) * 1e16)
    dB = np.diff(B)
    print(f"===== run {rid} {side} n={n12:+.2f}e12  F_L={F_L:.2f} T =====")
    print(f"  dB steps: {np.unique(np.round(dB,4))}")
    # 1/B Nyquist of the actual grid, per field
    for b in (0.5, 1.0, 2.0, 5.0, 10.0):
        i = np.argmin(abs(B - b)); step = dB[min(i, len(dB) - 1)]
        print(f"    B={b:4.1f}: dB={step:.3f} -> d(1/B)={step/b**2:.5f} -> f_Nyq={b**2/(2*step):7.1f} T")

    # ---- window ladder, all inside the 10 mT (B>1 T) region ----
    ax = axes[k, 0]
    for (lo, hi) in [(1.0, 10.0), (1.0, 7.5), (2.0, 7.5), (3.0, 10.0), (1.5, 5.0)]:
        f, s = sdh_fft(R[:, None], B, b_range=(lo, hi), bg_degree=5, log=False, nfft=4096)
        m = f <= 2.0 * F_L
        ax.plot(f[m], s[0][m] / s[0][m].max(), lw=0.9, label=f"{lo}-{hi} T")
    ax.axvline(F_L, color="r", ls="--"); ax.axvline(0.72*F_L, color="g", ls=":"); ax.axvline(0.28*F_L, color="b", ls=":")
    ax.set_title(f"run {rid} FFT window ladder (F_L={F_L:.1f} T dashed)"); ax.set_xlabel("F (T)"); ax.legend(fontsize=6)

    # ---- bg_degree stability on one window ----
    ax = axes[k, 1]
    lo, hi = (1.0, 7.5) if rid == 6 else (1.0, 8.5)
    for bg in (3, 5, 7, 9):
        f, s = sdh_fft(R[:, None], B, b_range=(lo, hi), bg_degree=bg, log=False, nfft=4096)
        m = f <= 2.0 * F_L
        ax.plot(f[m], s[0][m] / s[0][m].max(), lw=0.9, label=f"bg{bg}")
    ax.axvline(F_L, color="r", ls="--")
    ax.set_title(f"run {rid} bg_degree ladder, {lo}-{hi} T"); ax.set_xlabel("F (T)"); ax.legend(fontsize=6)

    # peak table on the reference window
    f, s = sdh_fft(R[:, None], B, b_range=(lo, hi), bg_degree=5, log=False, nfft=4096)
    s = s[0]; m = (f > 1.0) & (f <= 2.5 * F_L)
    from scipy.signal import find_peaks
    pk, props = find_peaks(s[m], height=0.05 * s[m].max(), distance=8)
    fm, sm = f[m], s[m]
    print(f"  --- peaks on {lo}-{hi} T (dF={1/(1/lo-1/hi):.2f} T) ---")
    for p in sorted(pk, key=lambda i: -sm[i])[:10]:
        print(f"    F={fm[p]:7.2f} T  amp={sm[p]/sm.max():5.3f}  F/F_L={fm[p]/F_L:6.3f}  n_implied={fm[p]*4*1.602176634e-19/6.62607015e-34/1e16:+6.3f}e12")

    # ---- raw zoom of the oscillating region ----
    ax = axes[k, 2]
    mm = (B >= 0.8)
    c = np.polyfit(B[mm], R[mm], 5)
    ax.plot(1 / B[mm], R[mm] - np.polyval(c, B[mm]), lw=0.8)
    ax.set_xlabel("1/B (1/T)"); ax.set_ylabel("dR (Ohm)"); ax.set_title(f"run {rid} bg-sub vs 1/B (B>0.8 T)")

fig.tight_layout(); fig.savefig("hera_scratch/spot_fft2.png", dpi=110)
print("saved hera_scratch/spot_fft2.png")
