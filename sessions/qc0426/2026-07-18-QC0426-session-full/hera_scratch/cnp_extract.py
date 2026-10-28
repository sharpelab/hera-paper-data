"""cnp-and-dline-calibration steps 0-3 on run 4 (scratch)."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
from hera.analysis import open_run, fan_grids, resistance_grids

run = open_run("data/4")
fg = fan_grids(run)
rg = resistance_grids(fg, channels=["sr1", "sr2"])
Vbg = fg.slow
Vtg = fg.grid("k_2400_tg_volt")[0]  # fast-axis setpoints, first row
print("slow (BG) axis:", Vbg[0], "->", Vbg[-1], len(Vbg))
print("fast (TG) axis:", Vtg[0], "->", Vtg[-1], len(Vtg))

fig, axes = plt.subplots(1, 2, figsize=(13, 5), sharey=True)
results = {}
for ax, ch in zip(axes, ("sr1", "sr2")):
    R = np.abs(rg.R[ch])          # (n_slow, n_fast)
    Rs = gaussian_filter1d(R, sigma=2, axis=1)
    idx = Rs.argmax(axis=1)
    ridge = Vtg[idx]
    peakR = Rs[np.arange(len(idx)), idx]
    # guard 1: edge-clipped rows (argmax at swept-window edge)
    edge = (idx <= 2) | (idx >= len(Vtg) - 3)
    # guard 3: iterative outlier rejection on the linear fit
    keep = ~edge
    for _ in range(5):
        p = np.polyfit(Vbg[keep], ridge[keep], 1)
        res = ridge - np.polyval(p, Vbg)
        sig = res[keep].std()
        new = ~edge & (np.abs(res) < 2 * sig)
        if (new == keep).all():
            break
        keep = new
    resid = ridge[keep] - np.polyval(p, Vbg[keep])
    results[ch] = dict(slope=p[0], intercept=p[1], rms=resid.std(),
                       nkept=keep.sum(), nedge=edge.sum(), peakR=peakR, keep=keep,
                       ridge=ridge)
    print(f"{ch}: slope={p[0]:+.4f}  intercept={p[1]:+.4f} V  rms={resid.std()*1e3:.1f} mV  "
          f"rows kept {keep.sum()}/101 (edge-clipped {edge.sum()})  "
          f"peak R range [{peakR[keep].min():.0f}, {peakR[keep].max():.0f}] Ohm")
    pc = ax.pcolormesh(Vtg, Vbg, R, shading="auto", cmap="inferno")
    ax.plot(ridge[keep], Vbg[keep], "c.", ms=3, label="ridge (kept)")
    ax.plot(ridge[~keep], Vbg[~keep], "w.", ms=2, alpha=0.5, label="excluded")
    ax.plot(np.polyval(p, Vbg), Vbg, "c--", lw=1, label=f"fit slope {p[0]:+.3f}")
    ax.set_xlim(Vtg[0], Vtg[-1])
    ax.set_xlabel("V_tg (V)  [fast]")
    ax.set_title(f"{ch} |R| (Ohm)")
    ax.legend(fontsize=7, loc="lower left")
    fig.colorbar(pc, ax=ax)
axes[0].set_ylabel("V_bg (V)  [slow]")
fig.suptitle("run 4 gate map: CNP ridge + linear fit (axis orientation: ridge V_tg fitted vs V_bg rows)")
fig.tight_layout()
fig.savefig("hera_scratch/cnp_ridge_fit.png", dpi=110)

# cross-channel + geometry sanity
s1, s2 = results["sr1"]["slope"], results["sr2"]["slope"]
print(f"\ncross-channel slope disagreement: {abs(s1-s2)/abs(s1)*100:.1f}%")
print(f"geometry prior ratio c_bg/c_tg = 15.6/12 = {15.6/12:.3f}; fitted -slope: sr1 {-s1:.3f}, sr2 {-s2:.3f}")

# peak R along ridge vs D proxy (gap opening?)
fig2, ax2 = plt.subplots(figsize=(7, 4))
for ch in ("sr1", "sr2"):
    r = results[ch]
    ax2.plot(Vbg[r["keep"]], r["peakR"][r["keep"]], ".-", label=f"{ch} ridge peak R")
ax2.set_xlabel("V_bg (V)  (|D| grows away from CNP-ridge center)")
ax2.set_ylabel("peak |R| (Ohm)"); ax2.set_yscale("log"); ax2.legend()
fig2.tight_layout(); fig2.savefig("hera_scratch/cnp_peakR_vs_bg.png", dpi=110)
