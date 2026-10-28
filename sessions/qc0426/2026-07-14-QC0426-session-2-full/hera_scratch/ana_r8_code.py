# Runs 5 + 8 (hole side, n = -6e12, D = 0): individual + co-added FFTs
from scipy.signal import find_peaks

I8 = 20e-9
recs = {}
for rid in (5, 8):
    r = run(rid)
    B = r.col("magnet_field"); o = np.argsort(B)
    recs[rid] = (B[o], {ch: (r.col_at(r.col_indices(f"{ch}_X")[-1]) / I8)[o] for ch in ("sr1", "sr2")})

F_Lh = 66.0  # Hall-pinned (run 5)
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
for ax, ch in zip(axes, ("sr1", "sr2")):
    stack = None
    for rid, ls in ((5, ":"), (8, "--")):
        B, R = recs[rid]
        fr, spec = sdh_fft(R[ch][:, None], B, b_range=(3.0, 8.0), bg_degree=4, log=False)
        mag = spec[0]
        ax.plot(fr, mag / mag.max(), ls, lw=0.8, label=f"run {rid}")
        stack = mag if stack is None else stack + mag
    ax.plot(fr, stack / stack.max(), "-", lw=1.4, label="co-added")
    pk, _ = find_peaks(stack, height=stack.max() * 0.15, distance=4)
    print(f"{ch} co-added peaks:", [f"{fr[p]:.1f} T ({stack[p]/stack.max():.2f})" for p in pk])
    ax.axvline(F_Lh, color="k", ls="--", lw=0.8, label="F_L 66 T")
    ax.set_xlim(0, 120); ax.set_xlabel("F (T)"); ax.set_title(f"{ch} hole side"); ax.legend(fontsize=8)
fig.suptitle("hole side: runs 5 + 8 co-added SdH FFT")
fig.tight_layout()
