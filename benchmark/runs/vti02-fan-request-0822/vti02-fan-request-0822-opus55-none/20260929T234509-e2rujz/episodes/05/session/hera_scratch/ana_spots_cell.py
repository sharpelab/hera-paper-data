# Runs 6/7 — sdh-spot-check at D = 0 (run-5 cal): raw R(B) first, then tones + Rxx-minimum filling factors.
from hera.analysis import resolve_channels, sdh_onset
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks
spots = {6: +3.2, 7: -1.2}   # n in 1e12 cm^-2 (run-5 geometry-scale cal)
fig, ax = plt.subplots(2, 2, figsize=(13, 8))
for k, (rid, n12) in enumerate(spots.items()):
    r = run(rid); ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col("magnet_field"); R = np.abs((r.col("sr1_X") / ch["sr1"].gain) / (r.col("sr0_X") / ch["sr0"].gain))
    o = np.argsort(B); B, R = B[o], R[o]
    FL = float(luttinger_frequency(abs(n12) * 1e16))
    print(f"=== run {rid}: n = {n12:+.1f}e12 (cal), F_L = {FL:.1f} T; R(B~0) {R[0]:.0f} Ohm, R(10 T) {R[-1]:.0f}; "
          f"T {r.col('T_sample').min():.3f}-{r.col('T_sample').max():.3f} K; |I_g| max {1e12*max(abs(r.col('k_2400_tg_curr')).max(), abs(r.col('k_2400_bg_curr')).max()):.0f} pA")
    print(sdh_onset(R, B, r_full_scale=50e-6 / 10e-9).summary())
    Rs = gaussian_filter1d(R, 3 if rid == 6 else 1.5); m = B > 0.8
    pk, _ = find_peaks(-Rs[m], prominence=8); Bm = B[m][pk]
    print("Rxx minima B (T):", np.round(Bm, 2), "| nu at cal scale:", np.round(4 * FL / Bm, 1))
    ax[0, k].plot(B, R, lw=0.7); ax[0, k].plot(Bm, Rs[m][pk], "rv", ms=5)
    ax[0, k].set_title(f"run {rid} raw Rxx(B), n = {n12:+.1f}e12, D = 0"); ax[0, k].set_xlabel("B (T)"); ax[0, k].set_ylabel("Rxx B_1-B_2 (Ohm)")
    mm = B > 1.5
    f, sp = sdh_fft(R[mm][:, None], B[mm], nfft=4096, bg_degree=5); ok = (f > 2) & (f < 2.5 * FL)
    ax[1, k].plot(f[ok], sp[0][ok] / sp[0][ok].max(), lw=1); ax[1, k].axvline(FL, color="k", ls="--", label=f"F_L (cal) {FL:.1f} T")
    ax[1, k].set_xlabel("F (T)"); ax[1, k].set_ylabel("|FFT| (norm)"); ax[1, k].set_title(f"run {rid} FFT of log Rxx, B > 1.5 T"); ax[1, k].legend()
fig.tight_layout(); plt.show()
