# CNP ridge extraction + fit on run 4 (coarse-BG gatemap), per channel.
# cnp-and-dline-calibration steps 1-3. Works on partial data (whole rows only).
import numpy as np
from scipy.ndimage import gaussian_filter1d
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, fan_grids, resistance_grids

fan = fan_grids(open_run("data/4"))
rg = resistance_grids(fan)
vbg = fan.slow                      # slow axis: V_bg rows
vtg = fan.grid("k_2400_tg_volt")[0]  # fast axis vector (planned setpoints, row 0)
print(f"rows complete: {fan.nrows}/25, fast pts {fan.nfast}")

fits = {}
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
for ax, cid in zip(axes[:2], ("sr1", "sr2")):
    R = np.abs(rg.R[cid])
    ridge_v, ridge_bg, clipped = [], [], 0
    for i in range(fan.nrows):
        prof = gaussian_filter1d(R[i], 2)
        j = int(np.argmax(prof))
        if j < 3 or j > fan.nfast - 4:   # edge-clipped row: CNP not located
            clipped += 1
            continue
        ridge_v.append(vtg[j]); ridge_bg.append(vbg[i])
    ridge_v, ridge_bg = np.array(ridge_v), np.array(ridge_bg)
    if len(ridge_v) < 4:
        print(f"{cid}: only {len(ridge_v)} unclipped ridge rows — too few to fit yet")
        continue
    # robust fit: iterative 2-sigma rejection
    keep = np.ones(len(ridge_v), bool)
    for _ in range(5):
        if keep.sum() < 3:
            break
        p = np.polyfit(ridge_bg[keep], ridge_v[keep], 1)
        resid = ridge_v - np.polyval(p, ridge_bg)
        sig = resid[keep].std()
        new = np.abs(resid) < max(2 * sig, 1e-3)
        if (new == keep).all():
            break
        keep = new
    fits[cid] = dict(slope=p[0], intercept=p[1], sigma=sig,
                     n_used=int(keep.sum()), n_clipped=clipped,
                     ridge=(ridge_bg, ridge_v, keep))
    print(f"{cid}: slope {p[0]:+.4f} (c_bg/c_tg = {-p[0]:.4f}), intercept {p[1]:+.4f} V, "
          f"resid sigma {sig*1e3:.1f} mV, rows used {keep.sum()}/{fan.nrows} (clipped {clipped})")
    # overlay
    ax.pcolormesh(vtg, vbg[:fan.nrows], np.log10(np.clip(R, 1, None)), shading="auto")
    ax.plot(ridge_v[keep], ridge_bg[keep], "wo", ms=3)
    ax.plot(ridge_v[~keep], ridge_bg[~keep], "rx", ms=4)
    bb = np.linspace(vbg.min(), vbg.max(), 10)
    ax.plot(np.polyval(p, bb), bb, "w--", lw=1)
    ax.set_xlabel("V_tg (V)"); ax.set_ylabel("V_bg (V)")
    ax.set_title(f"{cid}: log10 R, slope {p[0]:+.3f}")

# geometry-sanity: prior ratio = t_tg/t_bg = 1.3
print(f"\ngeometry prior c_bg/c_tg = 15.6/12 = {15.6/12:.3f}")

# cross-channel + closure check happens once both fits exist
if len(fits) == 2:
    s1, s2 = fits["sr1"]["slope"], fits["sr2"]["slope"]
    print(f"cross-channel slope disagreement: {abs(s1-s2)/abs((s1+s2)/2)*100:.2f}%")

axes[2].axis("off")
txt = "\n".join(f"{c}: slope {f['slope']:+.4f}, b {f['intercept']:+.4f} V, "
                f"sig {f['sigma']*1e3:.0f} mV, used {f['n_used']}" for c, f in fits.items())
axes[2].text(0.05, 0.6, txt, fontsize=10, family="monospace")
fig.tight_layout()
fig.savefig("hera_scratch/cnp_fit.png", dpi=120)
print("saved hera_scratch/cnp_fit.png")
