"""sdh-spot-check runs 6 (electron, n=+3.2e12, D=0, 0->10 T) and 7 (hole, n=-1.2e12, D=0, 10->0.3 T).
Raw first (R = (sr1_X/gain)/I_drain), then sdh_onset tone census + sdh_fft in three windows, vs F_L."""
from hera.analysis import resolve_channels, sdh_onset
from scipy.signal import find_peaks
import warnings

SENS = 50e-6
fig, ax = plt.subplots(2, 2, figsize=(13, 8))
for col, (rid, lab, n12) in enumerate([(6, "electron", 3.2), (7, "hole", -1.2)]):
    r = run(rid); ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col("magnet_field"); I = r.col("sr0_X") / ch["sr0"].gain
    R = np.abs((r.col("sr1_X") / ch["sr1"].gain) / I)
    o = np.argsort(B); B, R = B[o], R[o]
    FL = float(luttinger_frequency(abs(n12) * 1e16))
    print(f"--- run {rid} ({lab}, n = {n12:+.1f}e12, D = 0): {len(B)} pts, R {R.min():.1f}-{R.max():.1f} Ohm "
          f"(max {R.max()/(SENS/10e-9):.2f} FS), I_drain {I.min()*1e9:.2f}-{I.max()*1e9:.2f} nA, "
          f"T {r.col('T_sample').min():.3f}-{r.col('T_sample').max():.3f} K; F_L = {FL:.1f} T")
    ax[0, col].plot(B, R, lw=0.7); ax[0, col].set_xlabel("B (T)"); ax[0, col].set_ylabel("|Rxx| B_1-B_2 (Ohm)")
    ax[0, col].set_title(f"run {rid} raw — {lab} n = {n12:+.1f}e12, D = 0")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        on = sdh_onset(R, B, b_lo=0.5, r_full_scale=SENS / 10e-9)
    print(on.summary())
    for (blo, bhi), ls in [((1.5, 10), "-"), ((3, 10), "--")]:
        f, sp = sdh_fft(R[:, None], B, b_range=(blo, bhi), nfft=4096, bg_degree=5); sp = sp[0]
        sel = f > 2.5; pk, _ = find_peaks(sp[sel], prominence=0.08 * sp[sel].max())
        ff, aa = f[sel][pk], sp[sel][pk] / sp[sel].max(); j = np.argsort(-aa)[:5]
        print(f"   sdh_fft {blo}-{bhi} T (dF ~ {1/(1/blo-1/bhi):.1f} T): " + ", ".join(f"{ff[k]:.1f} T ({aa[k]:.2f})" for k in j))
        ax[1, col].plot(f, sp / sp[sel].max(), ls, lw=0.9, label=f"FFT {blo}-{bhi} T")
    ax[1, col].axvline(FL, color="k", ls=":", label=f"F_L {FL:.1f} T")
    ax[1, col].set_xlim(0, 50 if n12 > 0 else 30); ax[1, col].set_xlabel("F (T)"); ax[1, col].set_ylabel("|FFT| (norm.)")
    ax[1, col].legend(fontsize=8)
fig.suptitle("vti-02 SdH spot checks, D = 0 (run-5 calibration), T_sample 1.17-1.29 K"); fig.tight_layout(); plt.show()
