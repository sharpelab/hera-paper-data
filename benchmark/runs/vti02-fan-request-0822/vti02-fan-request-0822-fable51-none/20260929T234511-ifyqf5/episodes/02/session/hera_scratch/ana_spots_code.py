# Runs 6-7 (sdh-spot-check): raw |Rxx|(B), vs 1/B, and the SdH FFT / tone tracking. R = (sr1_X/gain)/(sr0_X/gain_I) per point.
from hera.analysis import resolve_channels, sdh_onset, SdhOnsetError
from scipy.signal import find_peaks
from scipy.ndimage import gaussian_filter1d

fig, ax = plt.subplots(3, 2, figsize=(14, 11))
for j, (rid, n12) in enumerate(((6, 3.2), (7, -1.2))):
    r = run(rid)
    ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col("magnet_field"); I = r.col("sr0_X") / ch["sr0"].gain
    R = (r.col("sr1_X") / ch["sr1"].gain) / I
    o = np.argsort(B); B, R, I = B[o], R[o], I[o]; Rs = np.abs(R)
    FL = luttinger_frequency(abs(n12) * 1e16)
    print(f"\n=== run {rid}: n = {n12:+.1f}e12, F_L = {FL:.1f} T; R {R.min():.1f}..{R.max():.1f} Ohm; I {I.mean()*1e9:.2f} nA; "
          f"T {r.col('T_sample').mean():.3f} K; I_tg/I_bg max {np.abs(r.col('k_2400_tg_curr')).max()*1e12:.0f}/{np.abs(r.col('k_2400_bg_curr')).max()*1e12:.0f} pA; interrupted={r.interrupted}")
    ax[0, j].plot(B, Rs, ".-", ms=2, lw=0.7); ax[0, j].set_xlabel("B (T)"); ax[0, j].set_ylabel("|Rxx| B_1-B_2 (Ohm)")
    ax[0, j].set_title(f"run {rid}: n = {n12:+.1f}e12, D = 0 — raw")
    m = B > 1.5; sm = gaussian_filter1d(Rs[m], 1.5)
    mins, _ = find_peaks(-sm, prominence=5); maxs, _ = find_peaks(sm, prominence=5)
    print("Rxx minima B =", np.round(B[m][mins], 2), "-> nu = 4 F_L/B =", np.round(4 * FL / B[m][mins], 1))
    ax[0, j].plot(B[m][mins], Rs[m][mins], "rv", ms=5); ax[0, j].plot(B[m][maxs], Rs[m][maxs], "g^", ms=5)
    ax[1, j].plot(1 / B[m], Rs[m], ".-", ms=2, lw=0.7); ax[1, j].set_xlabel("1/B (1/T)"); ax[1, j].set_ylabel("|Rxx| (Ohm)")
    ax[1, j].set_title("vs 1/B (B > 1.5 T); grey = nu multiple of 4 for F_L")
    for k in range(1, 40):
        x = k / FL
        if 0.1 < x < 1 / 1.5: ax[1, j].axvline(x, color="gray", lw=0.4, alpha=0.5)
    try:
        on = sdh_onset(Rs, B, b_hi=10.0, b_lo=1.0, r_full_scale=50e-6 / 10e-9); print(on.summary())
    except SdhOnsetError as e:
        print("sdh_onset:", e)
    for lo, hi, col in ((1.5, 10.0, "k"), (1.5, 5.0, "C0"), (3.0, 10.0, "C1")):
        f, sp = sdh_fft(Rs[:, None], B, b_range=(lo, hi), nfft=2048, bg_degree=5, log=False)
        sp = sp[0]; sel = (f > 2) & (f < 120)
        ax[2, j].plot(f[sel], sp[sel] / sp[sel].max(), col, lw=1, label=f"B {lo}-{hi} T")
        pk, _ = find_peaks(sp[sel], prominence=0.1 * sp[sel].max())
        print(f"FFT {lo}-{hi} T peaks (T): {np.round(f[sel][pk], 1)} rel amp {np.round(sp[sel][pk]/sp[sel].max(), 2)}")
    ax[2, j].axvline(FL, color="r", ls="--", lw=1, label=f"F_L = {FL:.1f} T (4-fold, all carriers)")
    ax[2, j].axvline(FL / 2, color="r", ls=":", lw=1, label="F_L/2 (8-fold)"); ax[2, j].axvline(FL / 4, color="m", ls=":", lw=1, label="F_L/4 (16-fold)")
    ax[2, j].set_xlabel("F (T)"); ax[2, j].set_ylabel("FFT amp (norm)"); ax[2, j].legend(fontsize=7); ax[2, j].set_title("SdH FFT in 1/B (B-poly5 background removed)")
fig.tight_layout(); plt.show()
