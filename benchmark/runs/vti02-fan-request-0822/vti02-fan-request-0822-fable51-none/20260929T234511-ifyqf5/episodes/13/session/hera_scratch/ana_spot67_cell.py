"""Runs 6 + 7 — sdh-spot-check at D = 0 (e side n = +3.2e12, h side n = -1.2e12; run-5 calibration).
Raw R(B) first, then R vs 1/B with the naive 4-fold LL fillings at the nominal n, then the SdH FFT + onset tracker."""
from hera.analysis import resolve_channels, sdh_onset, SdhOnsetError

fig, ax = plt.subplots(3, 2, figsize=(13, 11))
for j, (rid, n12) in enumerate([(6, 3.2), (7, -1.2)]):
    r = run(rid)
    ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col("magnet_field"); I = r.col("sr0_X") / ch["sr0"].gain
    R = (r.col("sr1_X") / ch["sr1"].gain) / I; T = r.col("T_sample")
    o = np.argsort(B); B, R, I, T = B[o], R[o], I[o], T[o]
    FL = luttinger_frequency(abs(n12) * 1e16)
    m = (B > 0.3) & (B < 1.0); noise = np.std(np.diff(R[m])) / np.sqrt(2)
    print(f"=== run {rid}: n = {n12:+.2f}e12 (F_L 4-fold = {FL:.1f} T; nu(10 T) = {abs(n12)*1e16*cst.h/(10*cst.e):.1f}); "
          f"T {T.min():.3f}-{T.max():.3f} K; I_drain {I.min()*1e9:.2f}-{I.max()*1e9:.2f} nA; R {R.min():.0f}..{R.max():.0f} Ohm; "
          f"pt-pt noise (0.3-1 T) {noise:.1f} Ohm; interrupted={r.interrupted}")
    ax[0, j].plot(B, R, lw=0.8); ax[0, j].set_title(f"run {rid}: n = {n12:+.1f}e12, D = 0 — raw Rxx (B_1-B_2)")
    ax[0, j].set_xlabel("B (T)"); ax[0, j].set_ylabel("R (Ohm)")
    mm = B > 1.0
    ax[1, j].plot(1 / B[mm], R[mm], lw=0.8); ax[1, j].set_xlabel("1/B (1/T)"); ax[1, j].set_ylabel("R (Ohm)")
    for nu in range(4, 100, 4):
        b = abs(n12) * 1e16 * cst.h / (nu * cst.e)
        if 1.0 < b < 10: ax[1, j].axvline(1 / b, color="0.8", lw=0.5)
    ax[1, j].set_title("vs 1/B; grey = nu = 4k at the nominal n (naive 4-fold, full density)")
    for b_lo in (1.5, 2.5):
        freqs, spec = sdh_fft(R[:, None], B, b_range=(b_lo, 10.0), nfft=2048, bg_degree=3, log=False)
        sp = spec[0]; fm = (freqs > 2) & (freqs < 120)
        pk = np.sort(freqs[fm][np.argsort(sp[fm])[::-1][:6]])
        print(f"  FFT {b_lo}-10 T (poly-3 bg, linear R): strongest peaks {np.round(pk, 1)} T")
        ax[2, j].plot(freqs, sp / sp[fm].max(), label=f"window {b_lo}-10 T")
    ax[2, j].axvline(FL, color="r", ls="--", label=f"F_L 4-fold {FL:.1f} T"); ax[2, j].axvline(FL / 2, color="r", ls=":", label="F_L/2 (8-fold)")
    ax[2, j].set_xlim(0, 80); ax[2, j].set_xlabel("F (T)"); ax[2, j].legend(fontsize=7); ax[2, j].set_title("SdH FFT in 1/B")
    try:
        so = sdh_onset(R, B, b_lo=1.0, r_full_scale=50e-6 / 10e-9, bg_degree=3); print(so.summary())
    except SdhOnsetError as e:
        print("  onset:", e)
fig.suptitle("vti-02 runs 6-7: sdh-spot-check at D = 0, T = 1.17-1.29 K, sr1 50 uV"); fig.tight_layout(); plt.show()
