"""sdh-spot-check read, runs 6 (electron, n_cal = +3.2e12) and 7 (hole, n_cal = -1.2e12), D = 0.
Raw first (Rxx vs B), then B-space poly5 background removal, FFT in 1/B (sdh_fft) vs F_L,
per-tone onsets (sdh_onset), and the QH-minimum density-scale anchor on the electron record."""
import warnings
from scipy.signal import find_peaks
from hera.analysis import sdh_onset, SdhOnsetError, resolve_channels

H_E = cst.h / cst.e
SPOTS = {6: 3.2, 7: -1.2}          # n_cal, 1e12 cm^-2 (run-5 calibration)
fig, ax = plt.subplots(3, 2, figsize=(12, 11))
for j, (rid, n_cal) in enumerate(SPOTS.items()):
    r = run(rid)
    ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col("magnet_field"); I = r.col("sr0_X") / ch["sr0"].gain
    R = (r.col("sr1_X") / ch["sr1"].gain) / I
    o = np.argsort(B); B, R = B[o], R[o]
    FL = float(luttinger_frequency(n_cal * 1e16))
    print(f"=== run {rid}: n_cal = {n_cal:+.2f}e12, F_L(cal) = {FL:.2f} T, B {B.min():.2f}-{B.max():.2f} T, {len(B)} pts, "
          f"R(B0) {R[0]:.0f} Ohm, R max {R.max():.0f} Ohm @ {B[R.argmax()]:.2f} T (FS 5 kOhm), T {r.col('T_sample').min():.3f}-{r.col('T_sample').max():.3f} K, "
          f"|I_tg|,|I_bg| max {np.abs(r.col('k_2400_tg_curr')).max()*1e12:.0f}, {np.abs(r.col('k_2400_bg_curr')).max()*1e12:.0f} pA")
    # onset on the adequately sampled record only (run 6 below 1 T was a 50 mT grid: under Nyquist for F_L there)
    b_lo = 1.0 if rid == 6 else 0.3
    m = B >= b_lo - 1e-6
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        try:
            on = sdh_onset(R[m], B[m], b_lo=b_lo, r_full_scale=50e-6 / 1e-8)
            print(on.summary())
        except SdhOnsetError as e:
            print("SdhOnsetError:", e)
        for ww in w:
            print("  warn:", ww.message)
    ax[0, j].plot(B, R, lw=0.8)
    ax[0, j].set(title=f"run {rid} raw Rxx (B_1-B_2), n_cal = {n_cal:+.1f}e12, D = 0", xlabel="B (T)", ylabel="Rxx (Ohm)")
    mb = B > 1.0
    dR = R[mb] - np.polyval(np.polyfit(B[mb], R[mb], 5), B[mb])
    ax[1, j].plot(1 / B[mb], dR, lw=0.7)
    ax[1, j].set(xlabel="1/B (1/T)", ylabel="dRxx (Ohm), poly5-in-B removed, B > 1 T")
    for lo in (1.0, 1.4, 2.0):
        f, S = sdh_fft(R[:, None], B, b_range=(lo, B.max()), bg_degree=5, log=False, nfft=4096)
        S = S[0]; sel = (f > 2) & (f < 1.6 * FL)
        ii, _ = find_peaks(S[sel], prominence=0.08 * S[sel].max())
        top = sorted(zip(S[sel][ii], f[sel][ii]), reverse=True)[:5]
        print(f"  FFT [{lo}, {B.max():.0f}] T: " + ", ".join(f"{fp:.1f} T ({sp/top[0][0]:.2f})" for sp, fp in top))
        ax[2, j].plot(f, S / S[sel].max(), lw=0.8, label=f"B >= {lo} T")
    ax[2, j].axvline(FL, c="k", ls="--", label="F_L (cal)")
    if rid == 6:
        ax[2, j].axvline(0.906 * FL, c="r", ls=":", label="F_L x 0.906 (QH scale)")
    ax[2, j].set(xlim=(0, 1.6 * FL), ylim=(0, 1.2), xlabel="F (T)", ylabel="FFT |.| (norm)"); ax[2, j].legend(fontsize=7)
    if rid == 6:   # QH minima -> density scale (model-independent: B_nu = n h / (nu e))
        mq = B > 4
        ii, _ = find_peaks(-R[mq], prominence=40)
        Bm = B[mq][ii]; nu_cal = n_cal * 1e16 * H_E / Bm
        print("  QH Rxx minima B = " + ", ".join(f"{b:.2f}" for b in Bm) + " T -> nu_cal = " + ", ".join(f"{v:.1f}" for v in nu_cal))
        nu_int = [28, 24, 20, 16]; S_qh = np.array(nu_int) / nu_cal[:4]
        print(f"  assign nu = {nu_int} (4-fold steps): S = n_true/n_cal = {S_qh.round(3).tolist()}; "
              f"nu = 28/24/20 mean {S_qh[:3].mean():.3f} (nu = 16 sits on the flank of the 8.8 T peak, shifted low)"
              f" -> F_L,true = {S_qh[:3].mean()*FL:.1f} T")
fig.suptitle("sdh-spot-check runs 6 (electron) / 7 (hole), D = 0, T = 1.17-1.29 K"); fig.tight_layout(); plt.show()
