# Run 4 raw + CNP ridge extraction/fit (cnp-and-dline-calibration steps 1-2)
from scipy.ndimage import gaussian_filter1d

fan = fan_grids(run(4))
rg = resistance_grids(fan)
vbg = fan.slow
vtg = fan.grid("k_2400_tg_volt")[0]

fits = {}
fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=True)
for ax, cid in zip(axes, ("sr1", "sr2")):
    R = np.abs(rg.R[cid])
    ridge_v, ridge_bg, clipped = [], [], 0
    for i in range(fan.nrows):
        j = int(np.argmax(gaussian_filter1d(R[i], 2)))
        if j < 3 or j > fan.nfast - 4:
            clipped += 1
            continue
        ridge_v.append(vtg[j]); ridge_bg.append(vbg[i])
    ridge_v, ridge_bg = np.array(ridge_v), np.array(ridge_bg)
    keep = np.ones(len(ridge_v), bool)
    for _ in range(5):
        p = np.polyfit(ridge_bg[keep], ridge_v[keep], 1)
        resid = ridge_v - np.polyval(p, ridge_bg)
        sig = resid[keep].std()
        new = np.abs(resid) < max(2 * sig, 1e-3)
        if (new == keep).all():
            break
        keep = new
    fits[cid] = (p, sig, int(keep.sum()), clipped)
    print(f"{cid}: slope {p[0]:+.4f} (c_bg/c_tg {-p[0]:.4f}), intercept {p[1]*1e3:+.1f} mV, "
          f"sigma {sig*1e3:.1f} mV, rows {keep.sum()}/{fan.nrows} (clipped {clipped})")
    ax.pcolormesh(vtg, vbg[:fan.nrows], np.log10(np.clip(R, 1, None)), shading="auto")
    ax.plot(ridge_v[keep], ridge_bg[keep], "wo", ms=3)
    bb = np.linspace(vbg.min(), vbg.max(), 10)
    ax.plot(np.polyval(p, bb), bb, "w--", lw=1)
    ax.set_xlabel("V_tg (V)"); ax.set_title(f"{cid}: log10 R (Ω), fit {p[0]:+.4f}")
axes[0].set_ylabel("V_bg (V)")
fig.suptitle("Run 4 — CNP ridge + per-channel linear fit")
fig.tight_layout()
