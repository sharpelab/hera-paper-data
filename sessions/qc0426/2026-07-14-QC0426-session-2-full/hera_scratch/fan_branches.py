"""Run 7 — branch tracing: f_s(n), f_B(n), f_top(n); partition + Onsager overlay."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from scipy.constants import h, e as qe
from hera.analysis import open_run, fan_grids, resistance_grids, sdh_fft

run = open_run("data/7")
fg = fan_grids(run)
rg = resistance_grids(fg)
B = np.asarray(fg.slow)
ns_true = np.linspace(2.0, 6.3, 51) * 1.07
F_L = (h / (4 * qe)) * ns_true * 1e16

fr, spec1 = sdh_fft(np.asarray(rg.R["sr1"]), B, b_range=(1.4, 8.0), bg_degree=5, log=False)
_, spec2 = sdh_fft(np.asarray(rg.R["sr2"]), B, b_range=(1.4, 8.0), bg_degree=5, log=False)

def trace(spec):
    fs, fB, ftop = np.full(51, np.nan), np.full(51, np.nan), np.full(51, np.nan)
    for i in range(51):
        mag = spec[i]
        pk, _ = find_peaks(mag, height=mag.max() * 0.12, distance=3)
        pf, pm = fr[pk], mag[pk]
        # f_s: strongest peak in [3, 0.35*F_L]
        m = (pf >= 3) & (pf <= max(6, 0.35 * F_L[i]))
        if m.any(): fs[i] = pf[m][np.argmax(pm[m])]
        # f_B: strongest in [0.55, 0.93]*F_L
        m = (pf >= 0.55 * F_L[i]) & (pf <= 0.93 * F_L[i])
        if m.any(): fB[i] = pf[m][np.argmax(pm[m])]
        # f_top: strongest in [0.93, 1.12]*F_L
        m = (pf > 0.93 * F_L[i]) & (pf <= 1.12 * F_L[i])
        if m.any(): ftop[i] = pf[m][np.argmax(pm[m])]
    return fs, fB, ftop

t1, t2 = trace(spec1), trace(spec2)

# ABA model (fs_count_b0, Datta params, D=0): n[1e12] -> (F_ML, F_BL)
model_n = np.array([1.0, 1.5, 2.0, 3.0])
model_ML = np.array([0.0, 0.2, 0.5, 1.5])
model_BL = np.array([10.3, 15.3, 20.2, 29.5])

fig, axes = plt.subplots(1, 3, figsize=(17, 5.2))
for ax, (fs, fB, ftop), nm in ((axes[0], t1, "sr1"), (axes[1], t2, "sr2")):
    ax.plot(ns_true, F_L, "k--", lw=1, label="F_L(n)")
    ax.plot(ns_true, fs, "o", ms=3, label="f_s (low)")
    ax.plot(ns_true, fB, "s", ms=3, label="f_B (main)")
    ax.plot(ns_true, ftop, "^", ms=3, label="f_top (~F_L)")
    ax.plot(ns_true, fB + fs, "r.", ms=4, label="f_B + f_s")
    ax.plot(model_n, model_BL, "g-", lw=1, label="ABA BL (model, <=3.5)")
    ax.plot(model_n, model_ML, "g:", lw=1, label="ABA ML (model)")
    ax.set_xlabel("n_true (1e12 cm^-2)"); ax.set_title(nm); ax.legend(fontsize=7)
    ax.set_ylim(0, 90)
axes[0].set_ylabel("F (T)")

# partition residual where both tones resolved
ax = axes[2]
for (fs, fB, _), nm, c in ((t1, "sr1", "C0"), (t2, "sr2", "C1")):
    ok = np.isfinite(fs) & np.isfinite(fB)
    ax.plot(ns_true[ok], (fB + fs - F_L)[ok], "o-", ms=3, color=c, lw=0.7, label=nm)
    print(f"{nm}: partition resolved on {ok.sum()}/51 cols; "
          f"median (f_B+f_s-F_L) = {np.nanmedian((fB+fs-F_L)[ok]):+.2f} T, "
          f"rms = {np.nanstd((fB+fs-F_L)[ok]):.2f} T")
ax.axhline(0, color="k", lw=0.8); ax.axhspan(-1.6, 1.6, color="gray", alpha=0.2)
ax.set_xlabel("n_true"); ax.set_ylabel("f_B + f_s - F_L (T)")
ax.set_title("Luttinger partition residual (grey: dF resolution)")
ax.legend()
fig.suptitle("run 7 - branch traces vs F_L, ABA model overlay, partition test")
fig.tight_layout(); fig.savefig("hera_scratch/fan_branches.png", dpi=110)
print("saved")
