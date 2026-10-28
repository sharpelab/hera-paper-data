"""LK mass read across the T ladder: per-run FFT amplitude of the light / heavy / sum tones in a fixed 1/B window,
T from the fp'd T_sample, fit A(T) = A0 * X/sinh(X), X = 14.69 m* T / B_eff.
Usage: menv python hera_scratch/lk_ana.py <run_id> [<run_id> ...]   (run 5 = base rung)
"""
import sys, warnings
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from scipy.optimize import curve_fit
from hera.analysis import open_run, sdh_fft

DATA = Path(__file__).resolve().parents[1] / "data"
ids = [int(a) for a in sys.argv[1:]]
B_LO, B_HI = 2.4, 10.0
B_EFF = 1.0 / (0.5 * (1 / B_LO + 1 / B_HI))
TONES = {"light": 6.6, "heavy": 22.5, "sum": 29.5}   # T, from runs 5/8 at this point (scale 0.93); +-3 T search window
rows = []
fig, axs = plt.subplots(1, 3, figsize=(17, 4.8))
for k, rid in enumerate(ids):
    r = open_run(DATA / str(rid)); mc = r.meta["measurement_config"]
    B = r.col("magnet_field"); I = r.col("sr0_X") / float(mc["sr0_gain"]); R = r.col("sr1_X") / I; T = r.col("T_sample")
    o = np.argsort(B); B, R, T = B[o], R[o], T[o]
    m = (B >= B_LO) & (B <= B_HI)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        freqs, spec = sdh_fft(R[m][:, None], B[m], b_range=(B_LO, B_HI), bg_degree=3, nfft=4096, log=False)
    sp = spec[0]
    amps = {}
    for name, f0 in TONES.items():
        w = (freqs > f0 - 3) & (freqs < f0 + 3); amps[name] = sp[w].max();
    Tm = float(np.nanmean(T[m])); Tsd = float(np.nanstd(T[m]))
    rows.append((rid, Tm, Tsd, amps))
    print(f"run {rid}: T {Tm:.2f} +- {Tsd:.2f} K ({np.nanmin(T):.2f}..{np.nanmax(T):.2f}); amps light {amps['light']:.3g} heavy {amps['heavy']:.3g} sum {amps['sum']:.3g}; R range {R[m].min():.0f}..{R[m].max():.0f}")
    axs[0].plot(freqs, sp, lw=0.8, label=f"{Tm:.1f} K");
axs[0].set_xlim(0, 45); axs[0].set_xlabel("F [T]"); axs[0].set_ylabel("FFT amp"); axs[0].legend(fontsize=7); axs[0].set_title(f"spectra, B {B_LO}-{B_HI} T")
Ts = np.array([r[1] for r in rows])
def lk(T, A0, m):
    X = 14.69 * m * T / B_EFF
    return A0 * X / np.sinh(X)
print(f"B_eff = {B_EFF:.2f} T")
for name in TONES:
    A = np.array([r[3][name] for r in rows])
    axs[1].semilogy(Ts, A / A[0], "o-", label=name)
    if len(Ts) >= 3:
        try:
            p, cov = curve_fit(lk, Ts, A, p0=(A[0], 0.05), bounds=([0, 0.005], [np.inf, 1.0]))
            err = np.sqrt(np.diag(cov))[1]
            Tf = np.linspace(0.5, Ts.max() * 1.1, 100); axs[2].plot(Tf, lk(Tf, *p) / p[0], "-", label=f"{name}: m* = {p[1]:.3f} +- {err:.3f} m_e")
            axs[2].plot(Ts, A / p[0], "o")
            print(f"LK {name:5s}: m* = {p[1]:.4f} +- {err:.4f} m_e (X at top rung {14.69*p[1]*Ts.max()/B_EFF:.2f})")
        except Exception as ex:
            print(f"LK {name}: fit failed: {ex}")
axs[1].set_xlabel("T [K]"); axs[1].set_ylabel("A(T)/A(base)"); axs[1].legend(); axs[2].set_xlabel("T [K]"); axs[2].set_ylabel("A/A0 (LK)"); axs[2].legend(fontsize=8)
plt.tight_layout(); out = Path(__file__).resolve().parent / "lk_ladder.png"; plt.savefig(out, dpi=90); print("saved", out)
