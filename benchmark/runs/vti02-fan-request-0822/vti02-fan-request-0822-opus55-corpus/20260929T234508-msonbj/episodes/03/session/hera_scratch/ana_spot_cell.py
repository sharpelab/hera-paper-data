"""Runs 6 (electron, n=+3.2e12) + 7 (hole, n=-1.2e12) — sdh-spot-check read. Raw first, then onset + 1/B FFT vs F_L and the model."""
import sys, warnings
from hera.analysis import resolve_channels, sdh_onset
sys.path.insert(0, str(Path.home() / "measurement_env/hera/models/tetralayer_fs_count"))
import fs_count_b0 as fsm

spots = {6: (+3.2, 1.0), 7: (-1.2, 0.3)}   # n (1e12), b_lo for onset = low edge of the uniformly-sampled record
def trace(i):
    r = run(i); ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col("magnet_field"); R = (r.col("sr1_X") / ch["sr1"].gain) / (r.col("sr0_X") / ch["sr0"].gain)
    o = np.argsort(B); return r, B[o], R[o]

fig, ax = plt.subplots(2, 2, figsize=(13, 8))
for j, (rid, (n12, blo)) in enumerate(spots.items()):
    r, B, R = trace(rid)
    FL = float(luttinger_frequency(n12 * 1e16))
    ab = fsm.abab_fs(n12 * 1e16)[1]
    print(f"--- run {rid}: n = {n12:+.1f}e12, D = 0; F_L = {FL:.2f} T; model ABAB orbits {[round(f, 2) for f, _ in ab]} T, ABCA {FL:.2f} T; "
          f"T {r.col('T_sample').min():.3f}-{r.col('T_sample').max():.3f} K; R {R.min():.0f}..{R.max():.0f} Ohm (FS 5000)")
    ax[0, j].plot(B, R, lw=0.7); ax[0, j].set_xlabel("B (T)"); ax[0, j].set_ylabel("Rxx B_1-B_2 (Ohm)")
    ax[0, j].set_title(f"run {rid} raw: n = {n12:+.1f}e12, D = 0")
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        on = sdh_onset(R, B, b_lo=blo, r_full_scale=5000.0)
    for x in w: print("  warn:", x.message)
    print(on.summary())
    for lo, hi in ((max(blo, 1.0), 5.0), (1.4, 10.0)):
        f, sp = sdh_fft(R[:, None], B, b_range=(lo, hi), bg_degree=5, log=False, nfft=4096)
        ax[1, j].plot(f, sp[0] / sp[0][f > 2].max(), lw=0.8, label=f"B {lo:.1f}-{hi:.0f} T (dF {1/(1/lo-1/hi):.2f} T)")
    ax[1, j].axvline(FL, color="k", ls="--", lw=1, label="F_L (scale 1)")
    for fa, _ in ab: ax[1, j].axvline(fa, color="C3", ls=":", lw=1)
    ax[1, j].plot([], [], "C3:", label="ABAB model (scale 1)")
    ax[1, j].set_xlim(0, 2.2 * FL); ax[1, j].set_ylim(0, 1.1); ax[1, j].set_xlabel("F (T)"); ax[1, j].legend(fontsize=7)
fig.suptitle("sdh-spot-check runs 6/7 (sr1 B_1-B_2, 10 nA, T = 1.17-1.29 K)"); fig.tight_layout(); plt.show()
