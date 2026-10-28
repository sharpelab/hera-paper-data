# Runs 6-7 — sdh-spot-check at D = 0 (run-5 cal): raw R(B) first, then background-subtracted trace + FFT + tone onsets.
from hera.analysis import resolve_channels, sdh_onset
fig, ax = plt.subplots(2, 2, figsize=(12, 7.5))
for j, (rid, n12) in enumerate(((6, 3.2), (7, -1.2))):
    r = run(rid); ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col("magnet_field"); R = np.abs((r.col("sr1_X") / ch["sr1"].gain) / (r.col("sr0_X") / ch["sr0"].gain))
    o = np.argsort(B); B, R = B[o], R[o]
    FL = float(luttinger_frequency(np.array([abs(n12) * 1e16]))[0])
    print(f"run {rid}: n = {n12:+.1f}e12 (run-5 cal, F_L = {FL:.1f} T); R {R.min():.0f}-{R.max():.0f} Ohm, "
          f"R(10 T) {np.median(R[B > 9.9]):.0f} Ohm; T {r.col('T_sample').min():.3f}-{r.col('T_sample').max():.3f} K; "
          f"|I_gate| max {max(np.abs(r.col('k_2400_tg_curr')).max(), np.abs(r.col('k_2400_bg_curr')).max())*1e12:.0f} pA")
    ax[0, j].plot(B, R, lw=0.8); ax[0, j].set_xlabel("B (T)"); ax[0, j].set_ylabel("|Rxx| B_1-B_2 (Ohm)")
    ax[0, j].set_title(f"run {rid} raw — n = {n12:+.1f}e12, D = 0")
    print(sdh_onset(R, B, r_full_scale=50e-6 / 10e-9).summary())
    f, sp = sdh_fft(R[:, None], B, b_range=(1.5, 10.0), nfft=4096, bg_degree=5)
    m = (f > 1) & (f < 3 * FL)
    ax[1, j].plot(f[m], sp[0][m] / sp[0][m].max())
    for x, l in ((FL, "F_L"), (FL / 3, "F_L/3")):
        ax[1, j].axvline(x, color="k", ls=":", lw=0.8); ax[1, j].text(x, 1.0, l, fontsize=8)
    ax[1, j].set_xlabel("F (T)"); ax[1, j].set_ylabel("|FFT| log R, 1.5-10 T (norm)"); ax[1, j].set_title(f"run {rid} SdH FFT")
fig.tight_layout(); plt.show()
