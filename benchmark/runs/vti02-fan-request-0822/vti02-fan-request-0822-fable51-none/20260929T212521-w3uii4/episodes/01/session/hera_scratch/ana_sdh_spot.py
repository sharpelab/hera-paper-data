"""sdh-spot-check read on runs 6 (electron, n=+3.2e12) and 7 (hole, n=-1.2e12), D = 0 (run-5 cal): raw R(B), noise,
Rxx-zero list vs 1/B, sdh_onset tone table, 1/B FFT against F_L = n h/(4e)."""
from scipy.signal import find_peaks, savgol_filter
from hera.analysis import resolve_channels, sdh_onset, SdhOnsetError
CAL = dict(c_tg=2.796e-03, c_bg=2.161e-03, n_offset=-0.0894, D_offset=-0.013)
spots = {6: dict(n=3.2, side="electron"), 7: dict(n=-1.2, side="hole")}
fig, axes = plt.subplots(3, 2, figsize=(14, 12))
for j, (rid, info) in enumerate(spots.items()):
    r = run(rid); ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col("magnet_field"); I = r.col("sr0_X") / ch["sr0"].gain
    Rs = (r.col("sr1_X") / ch["sr1"].gain) / I; T = r.col("T_sample")
    o = np.argsort(B); B, Rs, T, I = B[o], Rs[o], T[o], I[o]; R = np.abs(Rs)
    sens = r.meta["instruments"]["sr1"]["sensitivity"]
    lo = (B > 0.3) & (B < 1.5); noise = np.std(Rs[lo] - savgol_filter(Rs[lo], 11, 3))
    F_L = float(luttinger_frequency(info["n"] * 1e16))
    print(f"=== run {rid} ({info['side']}, n = {info['n']:+.2f}e12, D = 0): {len(B)} pts, B {B.min():.2f}-{B.max():.2f} T, "
          f"T {T.min():.3f}-{T.max():.3f} K, I {I.min()*1e9:.2f}-{I.max()*1e9:.2f} nA, sr1 sens {sens*1e6:.0f} uV (FS {sens/10e-9/1e3:.0f} kOhm), max fs {R.max()/(sens/10e-9):.2f}")
    print(f"  R(0.3 T) = {R[np.argmin(abs(B-0.3))]:.0f} Ohm, R max {R.max():.0f} at {B[np.argmax(R)]:.2f} T, noise (0.3-1.5 T) {noise:.1f} Ohm rms; F_L(g=4) = {F_L:.1f} T, n h/e = {4*F_L:.1f} T")
    sm = savgol_filter(R, 7, 2); sel = B > 1.5
    mins, _ = find_peaks(-sm[sel], prominence=8); Bm, Rm = B[sel][mins], sm[sel][mins]
    deep = Rm < 10
    print("  Rxx minima > 1.5 T (B [T], R [Ohm], 1/B [1/T], nu if n = n_cal): " +
          "; ".join(f"{b:.2f}/{rm:.0f}/{1/b:.3f}/{4*F_L/b:.1f}" for b, rm in zip(Bm, Rm)))
    print(f"  deep zeros (R<10): {np.round(Bm[deep], 2).tolist()} T; consecutive d(1/B): {np.round(-np.diff(1/Bm[deep]), 4).tolist()} (single 4-fold ladder would be {1/F_L:.4f})")
    try:
        on = sdh_onset(R, B, b_lo=0.3, r_full_scale=sens / 10e-9); print(on.summary())
    except SdhOnsetError as e:
        print("  sdh_onset:", e)
    for (b0, b1) in [(1.5, 10.0), (2.0, 6.0)]:
        f, sp = sdh_fft(R[:, None], B, b_range=(b0, b1), nfft=4096, bg_degree=5, log=False); sp = sp[0]; m = f > 2
        pk, _ = find_peaks(sp[m], prominence=0.1 * sp[m].max()); top = sorted(zip(sp[m][pk], f[m][pk]), reverse=True)[:6]
        print(f"  FFT {b0}-{b1} T: F [T] (rel amp) = " + ", ".join(f"{ff:.1f} ({a/top[0][0]:.2f})" for a, ff in top))
    f, sp = sdh_fft(R[:, None], B, b_range=(1.5, 10.0), nfft=4096, bg_degree=5, log=False); sp = sp[0]
    ax = axes[0, j]; ax.plot(B, Rs, lw=0.7); ax.axhline(0, color="k", lw=0.5)
    for b in Bm[deep]: ax.axvline(b, color="r", lw=0.4, alpha=0.6)
    ax.set_xlabel("B (T)"); ax.set_ylabel("Rxx signed (Ohm)"); ax.set_title(f"run {rid} {info['side']} n = {info['n']:+.1f}e12, D = 0 — raw R(B); red = zeros")
    ax = axes[1, j]; s1 = B > 1.0; ax.plot(1 / B[s1], R[s1], lw=0.7); ax.set_xlabel("1/B (1/T)"); ax.set_ylabel("|Rxx| (Ohm)"); ax.set_title("vs 1/B (B > 1 T)")
    ax = axes[2, j]; ax.plot(f, sp / sp[f > 2].max()); ax.set_xlim(0, 100); ax.set_xlabel("F (T)"); ax.set_ylabel("FFT |R| 1.5-10 T (norm)")
    ax.axvline(F_L, color="g", ls="--", label=f"F_L(g=4) = {F_L:.1f} T"); ax.axvline(2 * F_L, color="g", ls=":", label="2 F_L"); ax.legend()
    ax.set_title("SdH FFT in 1/B, 1.5-10 T, deg-5 B-space background")
fig.tight_layout(); plt.show()
