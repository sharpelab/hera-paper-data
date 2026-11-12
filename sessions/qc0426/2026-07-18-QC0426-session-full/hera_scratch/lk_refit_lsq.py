"""Ladder v1 refit: multi-cosine least-squares amplitudes (leakage-proof) -> LK masses."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from hera.analysis import open_run

I_BIAS = 20e-9
RUNS = [10, 11, 12, 13, 14, 15]
FREQS = {"ML": 13.4, "BL": 55.2, "FL": 66.3}
kB, hbar, e_ch, me = 1.380649e-23, 1.0545718e-34, 1.602177e-19, 9.109384e-31
B_eff = 2.0 / (1 / 2.8 + 1 / 6.0)

def tone_amps(B, R, freqs, bg_deg=5):
    """LSQ: R(B) = poly(B) + sum_i [a_i cos(2pi F_i/B) + b_i sin(2pi F_i/B)]."""
    x = 1.0 / B
    cols = [B**k for k in range(bg_deg + 1)]
    for F in freqs:
        cols += [np.cos(2 * np.pi * F * x), np.sin(2 * np.pi * F * x)]
    M = np.vstack(cols).T
    coef, *_ = np.linalg.lstsq(M, R, rcond=None)
    out = []
    for i in range(len(freqs)):
        a, b = coef[bg_deg + 1 + 2 * i], coef[bg_deg + 2 + 2 * i]
        out.append(np.hypot(a, b))
    return out

amps = {ch: {k: [] for k in FREQS} for ch in ("sr1", "sr2")}
Ts = []
for rid in RUNS:
    r = open_run(f"data/{rid}")
    B = r.col_at(4)
    o = np.argsort(B)
    Ts.append(float(np.mean(r.col("T_sample"))))
    for ch in ("sr1", "sr2"):
        R = np.abs(r.col(f"{ch}_X"))[o] / I_BIAS
        A = tone_amps(B[o], R, list(FREQS.values()))
        for k, a in zip(FREQS, A):
            amps[ch][k].append(a)
Ts = np.array(Ts)

def lk(T, A0, mstar):
    X = 2 * np.pi**2 * kB * T * (mstar * me) / (hbar * e_ch * B_eff)
    return A0 * X / np.sinh(X)

print(f"B_eff={B_eff:.2f}; rungs {np.round(Ts,2)}")
print("multi-cosine LSQ amplitudes (leakage-proof) -> lattice-T LK fits (rungs >= 13 K):")
hi = Ts >= 12.5
for ch in ("sr1", "sr2"):
    for k in FREQS:
        A = np.array(amps[ch][k]) / amps[ch][k][0]
        try:
            p, cov = curve_fit(lk, Ts[hi], A[hi], p0=[1.5, 0.05],
                               bounds=([0.05, 0.005], [30, 0.3]), maxfev=20000)
            print(f"  {ch} {k}: m* = {p[1]:.4f} +/- {np.sqrt(np.diag(cov))[1]:.4f}   "
                  f"amps(norm) {np.round(A,3)}")
        except RuntimeError:
            print(f"  {ch} {k}: fit failed; amps {np.round(A,3)}")
