"""sdh-spot-check read, runs 6 (electron, n = +3.2e12) and 7 (hole, n = -1.2e12), D = 0 (run-5 cal).
Raw MR first, then background-subtracted vs 1/B, sdh_onset per tone, windowed FFTs vs F_L and the ABAB model."""
import sys, warnings
from hera.analysis import sdh_onset, SdhOnsetError, resolve_channels
sys.path.insert(0, str(Path.home() / "measurement_env" / "hera" / "models" / "tetralayer_fs_count"))
import fs_count_b0 as FSM

spots = {6: dict(n=+3.2, wins=[(1.0, 10.0), (1.5, 10.0), (2.0, 10.0)]),
         7: dict(n=-1.2, wins=[(0.7, 10.0), (1.0, 10.0), (1.5, 10.0)])}
fig, ax = plt.subplots(3, 2, figsize=(13, 11))
for j, (rid, sp) in enumerate(spots.items()):
    r = run(rid); ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col("magnet_field"); I = r.col("sr0_X") / ch["sr0"].gain
    R = np.abs((r.col("sr1_X") / ch["sr1"].gain) / I); o = np.argsort(B); B, R, I = B[o], R[o], I[o]
    sens = 50e-6; FL = float(luttinger_frequency(sp["n"] * 1e16))
    ab = FSM.abab_mstar(sp["n"] * 1e16); Fa, ma = FSM.abca_mstar(sp["n"] * 1e16)
    print(f"=== run {rid}: n = {sp['n']:+.1f}e12, D = 0 | F_L = {FL:.1f} T | model ABAB " + ", ".join(f"{F:.1f} T (m* {m:.3f})" for F, m in ab)
          + f" | ABCA {Fa:.1f} T (m* {ma:.3f})")
    print(f"    B {B.min():.2f}-{B.max():.2f} T, {len(B)} pts; R {R.min():.0f}-{R.max():.0f} Ohm; I {np.median(I)*1e9:.2f} nA; "
          f"peak |sr1_X|/FS = {np.abs(r.col('sr1_X')).max()/sens:.2f}; T {r.col('T_sample').min():.3f}-{r.col('T_sample').max():.3f} K; "
          f"max |I_tg|, |I_bg| = {np.abs(r.col('k_2400_tg_curr')).max()*1e12:.0f}, {np.abs(r.col('k_2400_bg_curr')).max()*1e12:.0f} pA")
    ax[0, j].plot(B, R, lw=0.7); ax[0, j].set(xlabel="B (T)", ylabel="|Rxx| B_1-B_2 (Ohm)", title=f"run {rid} RAW, n = {sp['n']:+.1f}e12, D = 0")
    # onset on the adequately sampled record (run 6 is 50 mT-sampled below 1 T: Nyquist-blind to F > ~7 T there)
    blo = 1.0 if rid == 6 else 0.3
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        try:
            on = sdh_onset(R, B, b_lo=blo, r_full_scale=sens / np.median(I)); print(on.summary())
        except SdhOnsetError as e:
            on = None; print("SdhOnsetError:", e)
    for x in w: print("    note:", str(x.message)[:160])
    m = B > 0.7
    cf = np.polyfit(B[m], R[m], 7)
    ax[1, j].plot(1 / B[m], R[m] - np.polyval(cf, B[m]), lw=0.6)
    ax[1, j].set(xlabel="1/B (1/T)", ylabel="dR (Ohm), deg-7 bg in B", title=f"run {rid} background-subtracted (B > 0.7 T)")
    for lo, hi in sp["wins"]:
        f, S = sdh_fft(R[:, None], B, b_range=(lo, hi), bg_degree=5, log=False, nfft=1 << 14)
        s = S[0]; pk = [k for k in range(1, len(f) - 1) if s[k] > s[k - 1] and s[k] > s[k + 1] and f[k] > 1.5]
        pk = sorted(sorted(pk, key=lambda k: -s[k])[:6])
        print(f"    FFT {lo}-{hi} T (dF = {1/(1/lo-1/hi):.2f} T): " + ", ".join(f"{f[k]:.1f}({s[k]/max(s[pk]):.2f})" for k in pk))
        ax[2, j].plot(f, s / s[f > 1.5].max(), lw=0.9, label=f"{lo}-{hi} T")
    ax[2, j].axvline(FL, color="k", ls="--", label=f"F_L {FL:.1f} T")
    for F, _ in ab: ax[2, j].axvline(F, color="b", ls=":", lw=1)
    ax[2, j].set(xlim=(0, 2.2 * FL), xlabel="F (T)", ylabel="FFT (norm.)", title=f"run {rid} FFT (blue dotted: ABAB model, scale 1)")
    ax[2, j].legend(fontsize=7)
fig.tight_layout(); plt.show()
