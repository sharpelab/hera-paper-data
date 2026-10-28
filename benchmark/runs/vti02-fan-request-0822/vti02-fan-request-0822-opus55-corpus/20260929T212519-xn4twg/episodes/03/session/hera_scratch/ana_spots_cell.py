# Runs 6 + 7 — sdh-spot-check, electron (n = +3.2e12) and hole (n = -1.2e12) at D = 0. Raw first, then onset + FFT vs F_L and the model.
import sys, warnings
from hera.analysis import sdh_onset
sys.path.insert(0, str(Path.home() / "measurement_env" / "hera" / "models" / "tetralayer_fs_count"))
import fs_count_b0 as fsm

def spot(rid):
    r = run(rid); B = r.col("magnet_field"); R = r.col("sr1_X") / (r.col("sr0_X") / -1e6)   # R = (sr1_X/1)/(sr0_X/-1e6)
    o = np.argsort(B); return r, B[o], R[o]

fig, ax = plt.subplots(3, 2, figsize=(13, 11))
for k, (rid, n12, b_lo, wins) in enumerate([(6, +3.2, 1.0, [(1.0, 10), (1.5, 10), (2.5, 10), (4.0, 10)]),
                                            (7, -1.2, 0.5, [(0.5, 10), (1.0, 10), (2.0, 10), (3.0, 10)])]):
    r, B, R = spot(rid)
    FL = float(luttinger_frequency(n12 * 1e16)); ab = fsm.abab_fs(n12 * 1e16)[1]; ca = fsm.abca_fs(n12 * 1e16)[4]
    print(f"run {rid}: n = {n12:+}e12, D = 0 | B {B.min():.2f}-{B.max():.2f} T, {len(B)} pts | R {R.min():.0f}..{R.max():.0f} Ohm | "
          f"T {r.col('T_sample').min():.3f}-{r.col('T_sample').max():.3f} K | F_L = {FL:.1f} T; model ABAB {[round(f, 1) for f, _ in ab]} T, ABCA {ca:.1f} T")
    ax[0, k].plot(B, R, lw=0.7); ax[0, k].set(xlabel="B (T)", ylabel="Rxx B_1-B_2 (Ohm)", title=f"run {rid} raw, n = {n12:+}e12, D = 0")
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always"); on = sdh_onset(R, B, b_lo=b_lo, r_full_scale=50e-6 / 10e-9)
    print(on.summary()); [print("  note:", str(x.message)[:160]) for x in w]
    m = B >= wins[1][0]; dR = R[m] - np.polyval(np.polyfit(B[m], R[m], 5), B[m])
    ax[1, k].plot(1 / B[m], dR, lw=0.7); ax[1, k].set(xlabel="1/B (1/T)", ylabel="dR (Ohm)", title=f"deg-5 B-space background removed, B > {wins[1][0]} T")
    for lo, hi in wins:
        f, sp = sdh_fft(R[:, None], B, b_range=(lo, hi), bg_degree=5, nfft=4096, log=False); s = sp[0] / sp[0].max()
        pk = [i for i in range(1, len(s) - 1) if s[i] > s[i - 1] and s[i] > s[i + 1] and s[i] > 0.12 and f[i] > 1.5]
        print(f"  FFT B {lo}-{hi} T (dF = {1/(1/lo-1/hi):.2f} T): " + ", ".join(f"{f[i]:.1f} ({s[i]:.2f})" for i in pk[:8]))
        ax[2, k].plot(f, s, lw=0.8, label=f"B {lo}-{hi} T")
    ax[2, k].axvline(FL, color="k", ls="--", label="F_L")
    for fa, _ in ab: ax[2, k].axvline(fa, color="C3", ls=":", lw=1)
    ax[2, k].set(xlim=(0, 2.2 * FL), xlabel="F (T)", ylabel="|FFT| (norm.)", title="FFT in 1/B (red dotted: model ABAB pair; black: F_L = ABCA)"); ax[2, k].legend(fontsize=7)
fig.tight_layout(); plt.show()
