# Runs 6-7 — sdh-spot-check at D = 0 (run-5 calibration): electron n = +3.2e12 (B 0->10 T), hole n = -1.2e12 (B 10->0.3 T).
# Raw first (signed Rxx and sr1 phase vs B), then B-space deg-5 detrend vs 1/B, FFT (B >= 1.5 T), sdh_onset tone table.
import warnings
from hera.analysis import resolve_channels, sdh_onset
fig, ax = plt.subplots(3, 2, figsize=(13, 11))
for j, (rid, n12) in enumerate([(6, +3.2), (7, -1.2)]):
    r = run(rid); ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col("magnet_field"); o = np.argsort(B); B = B[o]
    R = ((r.col("sr1_X") / ch["sr1"].gain) / (r.col("sr0_X") / ch["sr0"].gain))[o]; P = r.col("sr1_P")[o]
    FL = luttinger_frequency(abs(n12) * 1e16)
    print(f"run {rid}: n = {n12:+.1f}e12, D = 0; F_L = {FL:.1f} T; B {B.min():.2f}-{B.max():.2f} T, {r.rows} pts; "
          f"signed R {R.min():+.1f}..{R.max():+.1f} Ohm ({100*np.mean(R<0):.0f} % of pts < 0); T {r.col('T_sample').min():.3f}-{r.col('T_sample').max():.3f} K")
    ax[0, j].plot(B, R, lw=.8); ax[0, j].axhline(0, color="k", lw=.5)
    ax[0, j].set_xlabel("B (T)"); ax[0, j].set_ylabel("signed Rxx B_1-B_2 (Ohm)"); ax[0, j].set_title(f"run {rid} raw — n = {n12:+.1f}e12, D = 0")
    a2 = ax[0, j].twinx(); a2.plot(B, P, "r-", lw=.4, alpha=.5); a2.set_ylabel("sr1 phase (deg)", color="r")
    m = B > 1.0; d = R[m] - np.polyval(np.polyfit(B[m], R[m], 5), B[m])
    ax[1, j].plot(1 / B[m], d, lw=.7); ax[1, j].set_xlabel("1/B (1/T)"); ax[1, j].set_ylabel("ΔRxx (Ohm)"); ax[1, j].set_title("detrended (deg-5 in B, B > 1 T)")
    m = B >= 1.5
    f, sp = sdh_fft(R[m][:, None], B[m], log=False, bg_degree=5, nfft=4096); sp = sp[0]
    ax[2, j].plot(f, sp / sp[(f > 2) & (f < 60)].max(), ".-", ms=3); ax[2, j].axvline(FL, color="k", ls=":", label=f"F_L = {FL:.1f} T")
    ax[2, j].set_xlim(0, 60); ax[2, j].set_xlabel("F (T)"); ax[2, j].set_ylabel("|FFT| (norm)"); ax[2, j].legend(); ax[2, j].set_title("FFT in 1/B, B ≥ 1.5 T (res ≈ 1.8 T)")
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        on = sdh_onset(R, B, r_full_scale=50e-6 / 10e-9)
    print(on.summary()); [print("   warn:", x.message) for x in w]
fig.suptitle("vti-02 runs 6-7: SdH spot checks at D = 0 (region-A calibration, run 5)"); fig.tight_layout(); plt.show()
