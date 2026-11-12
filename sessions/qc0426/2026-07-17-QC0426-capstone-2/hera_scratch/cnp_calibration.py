# cnp-and-dline-calibration — steps 0-4 on gatemap run 4 (scratch iteration)
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import gaussian_filter1d
from hera.analysis import open_run
from sharpelab_nb.gates import stack_capacitance, calc_nD, calc_gate_voltages

I_BIAS = 5e-9
r = open_run("data/4")
vbg = r.col("k_2400_bg_volt")   # slow (setpoint instance, index 1)
vtg_raw = r.col_at(2)            # fast setpoint column
n_slow, n_fast = 101, 101
VBG = vbg.reshape(n_slow, n_fast)[:, 0]
VTG = vtg_raw.reshape(n_slow, n_fast)[0, :]

# step 0: prior capacitances (F/m^2)
c_tg = stack_capacitance([(15.6, 3)])
c_bg = stack_capacitance([(12, 3), (0, 3.9)])
print(f"prior: c_tg={c_tg:.4e}, c_bg={c_bg:.4e}, ratio c_bg/c_tg={c_bg/c_tg:.4f}")

# step 1: per-channel ridge extraction (argmax along fast axis, smoothed)
results = {}
fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharex=True, sharey=True)
for ax, ch in zip(axes, ("sr1_X", "sr2_X", "sr3_X")):
    R = (r.col(ch) / I_BIAS).reshape(n_slow, n_fast)
    if ch == "sr3_X":  # Hall channel at B=0 — no CNP ridge; plot only
        ax.pcolormesh(VTG, VBG, R, shading="auto")
        ax.set_title(f"{ch} (Hall, no ridge fit)")
        continue
    Rs = gaussian_filter1d(R, 2, axis=1)
    idx = np.argmax(Rs, axis=1)
    ridge_v = VTG[idx]
    peak_R = Rs[np.arange(n_slow), idx]
    # guards: edge-clipped rows + weak-peak rows (ridge not in window)
    good = (idx > 2) & (idx < n_fast - 3) & (peak_R > 5 * np.median(Rs, axis=1))
    # robust linear fit with 2-sigma iterative rejection
    g = good.copy()
    for _ in range(4):
        p = np.polyfit(VBG[g], ridge_v[g], 1)
        res = ridge_v - np.polyval(p, VBG)
        s = np.std(res[g])
        g_new = good & (np.abs(res) < 2 * s)
        if (g_new == g).all():
            break
        g = g_new
    results[ch] = dict(slope=p[0], intercept=p[1], nrows=g.sum(), resid=np.std(res[g]),
                       ridge_v=ridge_v, good=g, peak_R=peak_R)
    print(f"{ch}: slope={p[0]:+.4f}, intercept={p[1]:+.4f} V, rows used {g.sum()}/{n_slow}, "
          f"resid {np.std(res[g])*1e3:.1f} mV")
    pm = ax.pcolormesh(VTG, VBG, np.log10(np.clip(R, 1, None)), shading="auto")
    ax.plot(ridge_v[g], VBG[g], "r.", ms=3)
    ax.plot(np.polyval(p, VBG), VBG, "w--", lw=1)
    ax.set_title(f"{ch}: slope {p[0]:+.3f}")
    plt.colorbar(pm, ax=ax, label="log10 R (Ohm)")
for ax in axes:
    ax.set_xlabel("V_tg (V)")
axes[0].set_ylabel("V_bg (V)")
fig.suptitle("run 4 gatemap: log10 R with per-channel CNP ridge + fit")
fig.tight_layout()
fig.savefig("hera_scratch/cnp_fit.png", dpi=110)

# step 3: conversion update (anchor c_tg = simple single-dielectric prior)
sl = np.mean([results["sr1_X"]["slope"], results["sr2_X"]["slope"]])
ratio_fit = -sl
c_bg_cal = c_tg * ratio_fit
b = np.mean([results[ch]["intercept"] for ch in ("sr1_X", "sr2_X")])
n_off = -calc_nD(b, 0, c_tg, c_bg_cal)[0]
print(f"\nfit ratio c_bg/c_tg = {ratio_fit:.4f} (geometry prior {c_bg/c_tg:.4f}, "
      f"delta {100*(ratio_fit/(c_bg/c_tg)-1):+.1f}%)")
print(f"V_tg intercept at V_bg=0: {b:+.4f} V -> n_offset = {n_off:+.4f} e12 cm^-2")

# closure: n along fitted ridge ~ 0 (units: 1e12 cm^-2)
vt_line = np.polyval([sl, b], VBG)
n_resid = np.array([calc_nD(vt, vb, c_tg, c_bg_cal, n_offset=n_off)[0]
                    for vt, vb in zip(vt_line, VBG)])
print(f"closure: max |n| residual along ridge = {np.abs(n_resid).max():.4f} e12 cm^-2")

# D=0 locator: R_CNP(V_bg) minimum along the ridge (physical D=0 feature)
for ch in ("sr1_X", "sr2_X"):
    d = results[ch]
    gg = d["good"]
    vb_min = VBG[gg][np.argmin(d["peak_R"][gg])]
    print(f"{ch}: R_CNP min at V_bg = {vb_min:+.3f} V (peak_R there "
          f"{d['peak_R'][gg].min():.0f} Ohm; max on ridge {d['peak_R'][gg].max():.0f} Ohm)")

# R_CNP vs V_bg plot (gap systematics teaser)
fig2, ax2 = plt.subplots(figsize=(6, 4))
for ch in ("sr1_X", "sr2_X"):
    d = results[ch]
    ax2.plot(VBG[d["good"]], d["peak_R"][d["good"]], ".-", label=ch)
ax2.set_xlabel("V_bg (V) along CNP ridge")
ax2.set_ylabel("peak R (Ohm)")
ax2.set_yscale("log")
ax2.legend()
ax2.set_title("run 4: CNP peak R along ridge (D=0 at the minimum)")
fig2.tight_layout()
fig2.savefig("hera_scratch/cnp_peakR.png", dpi=110)
print("saved hera_scratch/cnp_fit.png, cnp_peakR.png")
