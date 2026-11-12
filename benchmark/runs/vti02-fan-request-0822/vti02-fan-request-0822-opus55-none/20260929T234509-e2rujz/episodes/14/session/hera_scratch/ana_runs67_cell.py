# Runs 6-7 — SdH spot checks at D = 0 (region-A cal, run 5). Raw first, then 1/B FFT + per-tone onsets.
import warnings
from hera.analysis import resolve_channels, sdh_onset
spots = {6: +3.2, 7: -1.2}                      # run id -> n (1e12 cm^-2), D = 0
fig, ax = plt.subplots(3, 2, figsize=(13, 11))
for k, (rid, n12) in enumerate(spots.items()):
    r = run(rid); ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col_at(r.col_indices("magnet_field")[-1])           # last magnet_field column
    R = (r.col("sr1_X") / ch["sr1"].gain) / (r.col("sr0_X") / ch["sr0"].gain)
    o = np.argsort(B); B, R = B[o], R[o]
    FL = float(luttinger_frequency(abs(n12) * 1e16))
    print(f"run {rid}: n = {n12:+.1f}e12, D = 0 | F_L = {FL:.1f} T | {len(B)} pts, B {B.min():.2f}-{B.max():.2f} T | "
          f"R(B<0.4) = {np.median(R[B < 0.4]):.0f} Ohm, R(B>9.6) = {np.median(R[B > 9.6]):.0f} Ohm | "
          f"T {r.col('T_sample').min():.3f}-{r.col('T_sample').max():.3f} K | interrupted={r.interrupted}")
    ax[0, k].plot(B, R, lw=0.7); ax[0, k].set(xlabel="B (T)", ylabel="Rxx B_1-B_2 (Ohm)", title=f"run {rid} raw: n = {n12:+.1f}e12, D = 0")
    ax[1, k].plot(1 / B[B > 0.8], R[B > 0.8], lw=0.7); ax[1, k].set(xlabel="1/B (1/T)", ylabel="Rxx (Ohm)")
    for lo, ls in ((1.0, "-"), (2.0, "--")):
        f, s = sdh_fft(R[:, None], B, b_range=(lo, 10), nfft=4096, bg_degree=5, log=False)
        ax[2, k].plot(f, s[0] / s[0][f > 2].max(), ls, lw=1, label=f"FFT B {lo}-10 T (dF {1/(1/lo-0.1):.1f} T)")
    ax[2, k].axvline(FL, color="r", ls="--", lw=1, label=f"F_L = {FL:.1f} T")
    ax[2, k].set(xlim=(0, 45), ylim=(0, 1.1), xlabel="F (T)", ylabel="|FFT| (norm)"); ax[2, k].legend(fontsize=7)
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        on = sdh_onset(R, B, r_full_scale=50e-6 / 10e-9)
    print(on.summary()); [print("   warn:", str(x.message)[:160]) for x in w]
fig.suptitle("vti-02 runs 6-7: SdH spot checks at D = 0 (sr1 50 uV, 10 nA, T = 1.17-1.29 K)")
fig.tight_layout(); plt.show()
