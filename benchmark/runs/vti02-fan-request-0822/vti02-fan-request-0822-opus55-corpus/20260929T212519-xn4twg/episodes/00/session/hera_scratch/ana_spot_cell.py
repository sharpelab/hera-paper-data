"""Runs 6/7 — sdh-spot-check read. Raw MR first, then sdh_onset (10 mT record only) and 1/B FFTs vs F_L + the FS-count model."""
import sys, warnings
from hera.analysis import resolve_channels, sdh_onset
sys.path.insert(0, str(Path.home() / "measurement_env/hera/models/tetralayer_fs_count"))
import fs_count_b0 as fsm

def rxx(rid):
    r = run(rid); ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col("magnet_field"); I = r.col("sr0_X") / ch["sr0"].gain
    R = np.abs((r.col("sr1_X") / ch["sr1"].gain) / I); o = np.argsort(B)
    return r, B[o], R[o]

SPOT = {6: (+3.2, 1.0), 7: (-1.2, 0.3)}      # n (1e12), low edge of the adequately sampled record (run 6: 50 mT below 1 T under-samples a 7 T tone)
fig, ax = plt.subplots(2, 2, figsize=(13, 8))
for j, (rid, (n, bmin)) in enumerate(SPOT.items()):
    r, B, R = rxx(rid)
    FL = float(luttinger_frequency(n * 1e16)); ab = [f for f, _ in fsm.abab_fs(n * 1e16)[1]]
    print(f"== run {rid}: n = {n:+.1f}e12, D = 0; R {R.min():.0f}-{R.max():.0f} Ohm (5 kOhm FS -> max {R.max()/5000:.0%}); "
          f"T {np.nanmin(r.col('T_sample')):.3f}-{np.nanmax(r.col('T_sample')):.3f} K; interrupted={r.interrupted}")
    print(f"   F_L = {FL:.1f} T | model ABAB {', '.join(f'{f:.1f}' for f in ab)} T (sum {sum(ab):.1f}) | ABCA {FL:.1f} T")
    s = B >= bmin
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always"); on = sdh_onset(R[s], B[s], b_lo=bmin, r_full_scale=5000)
    print("   " + on.summary().replace("\n", "\n   ")); [print("   W:", x.message) for x in w]
    ax[0, j].plot(B, R, lw=0.7); ax[0, j].set(xlabel="B (T)", ylabel="Rxx B_1-B_2 (Ohm)", title=f"run {rid} raw, n = {n:+.1f}e12, D = 0")
    for br, c in [((max(bmin, 1.3), 7.4), "C0"), ((bmin, 4.0), "C1"), ((max(bmin, 1.3), 10.0), "C2")]:
        fr, sp = sdh_fft(R[:, None], B, b_range=br, bg_degree=5, nfft=4096); sp = sp[0]
        ax[1, j].plot(fr, sp / sp[fr > 1.5].max(), c, lw=0.9, label=f"B {br[0]:.1f}-{br[1]:.1f} T (dF {1/(1/br[0]-1/br[1]):.1f} T)")
    ax[1, j].axvline(FL, color="r", ls="--", lw=1, label="F_L (scale 1)"); [ax[1, j].axvline(f, color="g", ls=":", lw=1) for f in ab]
    ax[1, j].set(xlim=(0, 1.6 * FL), xlabel="F (T)", ylabel="FFT (norm.)", title="1/B FFT, log R, poly5-in-B bg; green = model ABAB pair")
    ax[1, j].legend(fontsize=7)
fig.suptitle("vti-02 sdh-spot-checks, runs 6 (electron) / 7 (hole), D = 0, T_sample 1.17-1.29 K"); fig.tight_layout(); plt.show()
