# Runs 6-7 — sdh-spot-check at D = 0: e-side n = +3.2e12 (0 -> 10 T), h-side n = -1.2e12 (10 -> 0.3 T).
# Raw first (R = |sr1_X/1| / |sr0_X/-1e6|), then per-tone onsets (sdh_onset) and FFT in 1/B (sdh_fft) vs F_L.
from hera.analysis import resolve_channels, sdh_onset
from scipy.signal import find_peaks

spots = [(6, +3.2), (7, -1.2)]
fig, ax = plt.subplots(3, 2, figsize=(13, 10.5))
for k, (rid, n12) in enumerate(spots):
    r = run(rid); ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col("magnet_field"); I = r.col("sr0_X") / ch["sr0"].gain
    R = np.abs((r.col("sr1_X") / ch["sr1"].gain) / I); o = np.argsort(B); B, R = B[o], R[o]
    FL = float(luttinger_frequency(abs(n12) * 1e16))
    t = np.sort(r.col("time")); dB = np.median(np.abs(np.diff(B)))
    print(f"=== run {rid}: n = {n12:+.1f}e12, D = 0, F_L = {FL:.1f} T | R(0) {R[:3].mean():.0f} Ohm, max {R.max():.0f} Ohm @ {B[R.argmax()]:.2f} T "
          f"(FS 5000) | I_drain {I.min()*1e9:.2f}-{I.max()*1e9:.2f} nA | T {r.col('T_sample').min():.3f}-{r.col('T_sample').max():.3f} K | "
          f"{np.median(np.diff(t)):.2f} s/pt at dB = {dB*1e3:.0f} mT")
    ax[0, k].plot(B, R, lw=0.7); ax[0, k].set_xlabel("B (T)"); ax[0, k].set_ylabel("|Rxx| B_1-B_2 (Ohm)")
    ax[0, k].set_title(f"run {rid} raw — n = {n12:+.1f}e12, D = 0")
    so = sdh_onset(R, B, b_lo=0.5, r_full_scale=50e-6 / 10e-9); print(so.summary())
    for j, (lo, hi) in enumerate([(2.0, 10.0), (4.0, 10.0)]):
        f, S = sdh_fft(R[:, None], B, b_range=(lo, hi), nfft=4096, bg_degree=5); S = S[0]; m = f < 3 * FL
        p, _ = find_peaks(S[m], prominence=0.08 * S[m].max()); p = sorted(sorted(p, key=lambda i: -S[m][i])[:6])
        print(f"  FFT {lo:.0f}-{hi:.0f} T (dF ~ {1/(1/lo-1/hi):.1f} T): " + ", ".join(f"{f[m][i]:.1f} T [{f[m][i]/FL:.2f} F_L, {S[m][i]/S[m].max():.2f}]" for i in p))
        a = ax[1 + j, k]; a.plot(f[m], S[m]); a.axvline(FL, color="r", ls="--", lw=0.8, label=f"F_L = {FL:.1f} T")
        a.set_xlabel("F (T)"); a.set_ylabel("|FFT| log R"); a.set_title(f"run {rid}: FFT in 1/B, {lo:.0f}-{hi:.0f} T"); a.legend()
fig.suptitle("vti-02 sdh-spot-check, runs 6 (e) / 7 (h), D = 0, T = 1.17-1.29 K, sr1 50 uV")
fig.tight_layout(); plt.show()
