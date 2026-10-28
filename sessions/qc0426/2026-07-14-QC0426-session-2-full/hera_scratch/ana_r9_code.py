# Run 9 vs run 6 — collection-scheme head-to-head at the same (n, D)
from scipy.signal import find_peaks

I9 = 20e-9
d = {}
for rid in (6, 9):
    r = run(rid)
    B = r.col("magnet_field"); o = np.argsort(B)
    d[rid] = (B[o], {ch: (r.col_at(r.col_indices(f"{ch}_X")[-1]) / I9)[o] for ch in ("sr1", "sr2")})

F_L9 = 66.6
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
for ax, ch in zip(axes, ("sr1", "sr2")):
    for rid, lbl, ls in ((6, "run 6 (uniform 1/B)", ":"), (9, "run 9 (uniform B)", "-")):
        B, R = d[rid]
        fr, spec = sdh_fft(R[ch][:, None], B, b_range=(3.0, 8.0), bg_degree=4, log=False)
        mag = spec[0]
        ax.plot(fr, mag / mag.max(), ls, lw=1.0, label=lbl)
        pk, _ = find_peaks(mag, height=mag.max() * 0.12, distance=4)
        print(f"{ch} run {rid}:", [f"{fr[p]:.1f}({mag[p]/mag.max():.2f})" for p in pk])
    ax.axvline(F_L9, color="k", ls="--", lw=0.8, label="F_L 66.6 T")
    ax.set_xlim(0, 120); ax.set_xlabel("F (T)"); ax.set_title(f"{ch}, electron n=+6e12"); ax.legend(fontsize=8)
fig.suptitle("collection head-to-head: uniform-B (run 9) vs uniform-1/B (run 6)")
fig.tight_layout()
