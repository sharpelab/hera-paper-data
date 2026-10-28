"""Runs 6-7 - sdh-spot-check at D = 0 (run-5 cal): electron n = +3.2e12 (B 0->10 T), hole n = -1.2e12 (B 10->0.3 T).
Raw first, then onset (sdh_onset) and 1/B FFTs (sdh_fft) against F_L and the ABAB model lines."""
import sys, warnings
from hera.analysis import resolve_channels, sdh_onset
sys.path.insert(0, str(Path.home() / "measurement_env" / "hera" / "models" / "tetralayer_fs_count"))
import fs_count_b0 as FS

SPOTS = {6: dict(n=3.2, side="electron", onset_win=(0.3, 7.4), wins=[(0.9, 7.4), (1.3, 7.4), (2.0, 7.4)]),
         7: dict(n=-1.2, side="hole", onset_win=(0.3, 10.0), wins=[(0.7, 10.0), (0.7, 5.0), (2.0, 10.0)])}
fig, ax = plt.subplots(2, 2, figsize=(13, 8.5))
for j, (rid, sp) in enumerate(SPOTS.items()):
    r = run(rid)
    ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col("magnet_field"); I = r.col("sr0_X") / ch["sr0"].gain
    R = np.abs((r.col("sr1_X") / ch["sr1"].gain) / I)
    o = np.argsort(B); B, R, I = B[o], R[o], I[o]
    FL = float(luttinger_frequency(abs(sp["n"]) * 1e16))
    abab = sorted(float(f) for f, k in FS.abab_fs(sp["n"] * 1e16)[1])
    print(f"run {rid} ({sp['side']}, n = {sp['n']:+.1f}e12, D = 0): {len(B)} pts, B {B.min():.2f}-{B.max():.2f} T, "
          f"R {R.min():.0f}-{R.max():.0f} Ohm (5 kOhm FS -> max {R.max()/50:.0f}%), I_drain {I.min()*1e9:.2f}-{I.max()*1e9:.2f} nA, "
          f"T {r.col('T_sample').min():.2f}-{r.col('T_sample').max():.2f} K, interrupted={r.interrupted}")
    print(f"  F_L = {FL:.2f} T; ABAB model (scale 1) {[round(f, 2) for f in abab]} T; ABCA model = F_L (single pocket)")
    lo, hi = sp["onset_win"]; m = (B >= lo) & (B <= hi)
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        on = sdh_onset(R[m], B[m], r_full_scale=5000.0)
    print("  " + on.summary().replace("\n", "\n  "))
    ax[0, j].plot(B, R, lw=0.7)
    ax[0, j].set_xlabel("B (T)"); ax[0, j].set_ylabel("Rxx B_1-B_2 (Ohm)")
    ax[0, j].set_title(f"run {rid}: raw Rxx(B), {sp['side']} n = {sp['n']:+.1f}e12, D = 0")
    ax[0, j].axvline(on.onset_b, color="r", ls="--", lw=1, label=f"sdh_onset {on.onset_b:.2f} T")
    ax[0, j].legend(fontsize=8)
    for lo, hi in sp["wins"]:
        f, S = sdh_fft(R[:, None], B, b_range=(lo, hi), bg_degree=5, log=False, nfft=2048)
        s = S[0]
        pk = [i for i in range(2, len(f) - 1) if s[i] > s[i - 1] and s[i] > s[i + 1] and f[i] > 1.0]
        pk = sorted(pk, key=lambda i: -s[i])[:6]
        print(f"  FFT [{lo}, {hi}] T (dF {1/(1/lo-1/hi):.2f} T): " + ", ".join(f"{f[i]:.1f}({s[i]/s[pk[0]]:.2f})" for i in sorted(pk)))
        ax[1, j].plot(f, s / s.max(), lw=0.8, label=f"[{lo}, {hi}] T")
    ax[1, j].axvline(FL, color="k", ls="--", lw=1, label=f"F_L {FL:.1f} T")
    for fa in abab:
        ax[1, j].axvline(fa, color="C3", ls=":", lw=1)
    ax[1, j].set_xlim(0, 1.6 * FL); ax[1, j].set_xlabel("F (T)"); ax[1, j].set_ylabel("|FFT| (norm.)")
    ax[1, j].set_title(f"run {rid}: FFT in 1/B, poly-5-in-B bg (red dotted: ABAB model)"); ax[1, j].legend(fontsize=7)
fig.suptitle("vti-02 sdh-spot-check runs 6-7 (D = 0, T = 1.17-1.29 K, 10 nA, sr1 50 uV)")
fig.tight_layout(); plt.show()
