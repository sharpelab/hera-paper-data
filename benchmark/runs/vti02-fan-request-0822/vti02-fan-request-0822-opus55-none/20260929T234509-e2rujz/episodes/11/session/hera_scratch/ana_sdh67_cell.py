# Runs 6-7 — SdH spot checks at D = 0 (run-5 calibration). Raw R(B) first, then the per-trace FFT + onset read.
from hera.analysis import resolve_channels, sdh_onset, SdhOnsetError
from scipy.signal import find_peaks
from scipy.ndimage import gaussian_filter1d
h_e = cst.h / cst.e
spots = {6: +3.2, 7: -1.2}          # run id -> n (1e12 cm^-2), D = 0
fig, ax = plt.subplots(2, 2, figsize=(13, 8))
for k, (rid, n12) in enumerate(spots.items()):
    r = run(rid); ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col("magnet_field"); I = r.col("sr0_X") / ch["sr0"].gain
    R = np.abs((r.col("sr1_X") / ch["sr1"].gain) / I)
    o = np.argsort(B); B, R = B[o], R[o]
    FL = float(luttinger_frequency(abs(n12) * 1e16))
    print(f"run {rid}: n = {n12:+.1f}e12, D = 0; B {B.min():.2f}-{B.max():.2f} T ({len(B)} pts); R(B_min) {R[:5].mean():.0f} Ohm, "
          f"R(10 T) {R[-5:].mean():.0f}, max {R.max():.0f} Ohm; T {r.col('T_sample').min():.3f}-{r.col('T_sample').max():.3f} K; "
          f"|I_tg| max {np.abs(r.col('k_2400_tg_curr')).max()*1e12:.0f} pA; F_L = {FL:.1f} T; interrupted={r.interrupted}")
    ax[0, k].plot(B, R, lw=0.8); ax[0, k].set_xlabel("B (T)"); ax[0, k].set_ylabel("|Rxx| B_1-B_2 (Ohm)")
    ax[0, k].set_title(f"run {rid} raw: n = {n12:+.1f}e12, D = 0, T = 1.2 K")
    for blo in (1.5, 2.5, 4.0):
        f, S = sdh_fft(R[:, None], B, b_range=(blo, B.max()), nfft=4096, bg_degree=5); S = S[0]
        lm = [i for i in range(1, len(S) - 1) if f[i] > 2 and S[i] > S[i-1] and S[i] >= S[i+1]]
        lm = sorted(lm, key=lambda i: -S[i])[:4]
        print(f"   FFT B > {blo} T (dF {1/(1/blo-1/B.max()):.1f} T): " + ", ".join(f"{f[i]:.1f} T ({S[i]/S[lm[0]]:.2f})" for i in lm))
        if blo == 1.5:
            ax[1, k].plot(f, S / S.max(), lw=1); ax[1, k].axvline(FL, color="r", ls="--", label=f"F_L = {FL:.1f} T")
            ax[1, k].set_xlim(0, 60); ax[1, k].set_xlabel("F (T)"); ax[1, k].set_ylabel("|FFT| (norm)"); ax[1, k].legend()
            ax[1, k].set_title(f"run {rid}: FFT in 1/B, B > {blo} T, log R, bg deg 5")
    try:
        print("  " + sdh_onset(R, B).summary().replace("\n", "\n  "))
    except SdhOnsetError as e:
        print("   sdh_onset:", e)
    m = B >= 2.0
    dR = R[m] - np.polyval(np.polyfit(B[m], R[m], 5), B[m]); sm = gaussian_filter1d(dR, 2)
    mins, _ = find_peaks(-sm, prominence=0.3 * np.std(sm)); Bm = B[m][mins][::-1]
    print("   Rxx minima (B > 2 T): " + ", ".join(f"{b:.2f} T (nu={abs(n12)*1e16*h_e/b:.1f})" for b in Bm[:12]))
fig.tight_layout(); plt.show()
