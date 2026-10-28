"""LK mass fit per tone from runs 10-15 (scratch)."""
import numpy as np


import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from hera.analysis import open_run, sdh_fft

I_BIAS = 20e-9
RUNS = [10, 11, 12, 13, 14, 15]
TONES = {"ML 13.4": 13.4, "BL 55.2": 55.2, "FL 66.3": 66.3}
kB, hbar, e_ch, me = 1.380649e-23, 1.0545718e-34, 1.602177e-19, 9.109384e-31

# harmonic-mean field of the 1/B window (LK amplitude evaluated at B_eff)
B_eff = 2.0 / (1 / 2.8 + 1 / 6.0)

amps = {ch: {k: [] for k in TONES} for ch in ("sr1", "sr2")}
Ts = []
for rid in RUNS:
    r = open_run(f"data/{rid}")
    B = r.col_at(4)
    o = np.argsort(B)
    Ts.append(float(np.mean(r.col("T_sample"))))
    for ch in ("sr1", "sr2"):
        R = np.abs(r.col(f"{ch}_X"))[o] / I_BIAS
        f, s = sdh_fft(R[:, None], B[o], b_range=(2.8, 6.0), nfft=4096, log=False)
        for k, F0 in TONES.items():
            m = (f > F0 - 3) & (f < F0 + 3)
            amps[ch][k].append(float(s[0][m].max()))
Ts = np.array(Ts)
print("rung temperatures:", np.round(Ts, 2))

def lk(T, A0, mstar, T0):
    Te = np.sqrt(T**2 + T0**2)
    X = 2 * np.pi**2 * kB * Te * (mstar * me) / (hbar * e_ch * B_eff)
    return A0 * X / np.sinh(X)

fig, axes = plt.subplots(1, 2, figsize=(12, 4.5), sharey=False)
print(f"B_eff = {B_eff:.2f} T")
results = {}
for ax, ch in zip(axes, ("sr1", "sr2")):
    for k in TONES:
        A = np.array(amps[ch][k])
        A = A / A[0]
        # (a) quadrature-T_e fit, all rungs, T0 free
        try:
            p, cov = curve_fit(lk, Ts, A, p0=[1.5, 0.05, 8.0],
                               bounds=([0.1, 0.005, 2.0], [20, 0.3, 15.0]), maxfev=20000)
            err = np.sqrt(np.diag(cov))
            ma, ma_e, T0 = p[1], err[1], p[2]
        except RuntimeError:
            ma, ma_e, T0 = np.nan, np.nan, np.nan
        # (b) lattice-T fit, rungs >= 13 K only
        hi = Ts >= 12.5
        try:
            pb, covb = curve_fit(lambda T, A0, m: lk(T, A0, m, 0.0), Ts[hi], A[hi],
                                 p0=[1.5, 0.05], bounds=([0.05, 0.005], [20, 0.3]), maxfev=20000)
            mb, mb_e = pb[1], np.sqrt(np.diag(covb))[1]
        except RuntimeError:
            mb, mb_e = np.nan, np.nan
        results[(ch, k)] = (ma, ma_e, T0, mb, mb_e)
        print(f"{ch} {k}: m*(quad,T0={T0:.1f}K) = {ma:.4f}+/-{ma_e:.4f}  |  m*(lattice,T>=13K) = {mb:.4f}+/-{mb_e:.4f}")
        ax.plot(Ts, A, "o", ms=5, label=f"{k}: m*={ma:.3f}")
        Tf = np.linspace(1, 26, 100)
        ax.plot(Tf, lk(Tf, *p), lw=0.8)
    ax.set_xlabel("T lattice (K)"); ax.set_title(ch); ax.legend(fontsize=8)
    ax.set_yscale("log")
axes[0].set_ylabel("FFT amp (norm. to base rung)")
fig.suptitle(f"LK per-tone mass fits, B_eff={B_eff:.2f} T (model: ML 0.018-0.05, BL 0.065, ABC 0.043; breakdown ~0.09)")
fig.tight_layout(); plt.show()

