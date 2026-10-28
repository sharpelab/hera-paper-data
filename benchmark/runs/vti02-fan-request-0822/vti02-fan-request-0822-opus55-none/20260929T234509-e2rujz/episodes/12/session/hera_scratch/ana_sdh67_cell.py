# Runs 6-7 (sdh-spot-check): raw R(B) first, then 1/B FFT + onset + minima indexing at the nominal (prior-scale) density.
from hera.analysis import resolve_channels, sdh_onset
from scipy.signal import find_peaks
from scipy.ndimage import gaussian_filter1d
h_, e_ = cst.h, cst.e
fig, ax = plt.subplots(2, 2, figsize=(12, 7.5))
for j, (rid, n12) in enumerate([(6, 3.2), (7, -1.2)]):
    r = run(rid); ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col_at(1); o = np.argsort(B); B = B[o]
    I = (r.col("sr0_X") / ch["sr0"].gain)[o]
    R = np.abs((r.col("sr1_X")[o] / ch["sr1"].gain) / I)
    print(f"run {rid} n_nom {n12:+.1f}e12: B {B.min():.2f}-{B.max():.2f} T, R {R.min():.1f}-{R.max():.1f} Ohm, "
          f"max|sr1_X| {np.abs(r.col('sr1_X')).max()*1e6:.1f} uV of 50 uV FS, I {I.min()*1e9:.2f}-{I.max()*1e9:.2f} nA, "
          f"T {r.col('T_sample').min():.3f}-{r.col('T_sample').max():.3f} K, interrupted={r.interrupted}")
    ax[0, j].plot(B, R, lw=0.7); ax[0, j].set(xlabel="B (T)", ylabel="|Rxx| B_1-B_2 (Ohm)", title=f"run {rid} raw, n_nom {n12:+.1f}e12, D = 0")
    Rs = gaussian_filter1d(R, 2); m = B > 0.8
    pk, _ = find_peaks(-Rs[m], prominence=8); Bm = B[m][pk]
    print("  minima B (T):", np.round(Bm, 2), "\n  nu_nom = n h/(eB):", np.round(abs(n12) * 1e16 * h_ / (e_ * Bm), 1))
    for blo in (1.5, 2.0, 4.0):
        f, sp = sdh_fft(R[:, None], B, b_range=(blo, B.max()), nfft=4096); sp = sp[0]
        k = (f > 2) & (f < 80); pp, _ = find_peaks(sp[k], prominence=sp[k].max() * 0.08)
        top = sorted(pp, key=lambda p: -sp[k][p])[:5]
        print(f"  FFT B>{blo} T (dF ~ {1/(1/blo-1/B.max()):.1f} T): " + ", ".join(f"{f[k][p]:.1f} T ({sp[k][p]/sp[k].max():.2f})" for p in top))
        if blo == 1.5: ax[1, j].plot(f, sp / sp[k].max(), lw=0.8, label=f"B > {blo} T")
    FL = abs(n12) * 1e16 * h_ / (4 * e_); ax[1, j].axvline(FL, color="r", ls="--", lw=0.8, label=f"F_L(n_nom) = {FL:.1f} T")
    ax[1, j].set(xlim=(0, 70), xlabel="F (T)", ylabel="FFT |.| (norm.)"); ax[1, j].legend(fontsize=8)
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore"); print("  " + sdh_onset(R, B, r_full_scale=50e-6 / 10e-9).summary().replace("\n", "\n  "))
fig.suptitle("vti-02 SdH spot checks, runs 6 (e, 0->10 T) and 7 (h, 10->0.3 T); T = 1.17-1.29 K"); fig.tight_layout(); plt.show()
