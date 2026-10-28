# Runs 6-7 — SdH spot checks at D = 0 (sdh-spot-check). Raw R(B) first, then FFT windows + per-tone onsets.
from hera.analysis import resolve_channels, sdh_fft, sdh_onset
h_e = cst.h / cst.e
fig, ax = plt.subplots(2, 2, figsize=(13, 7.5))
for k, (rid, n_nom) in enumerate([(6, 3.2), (7, -1.2)]):
    r = run(rid); ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col("magnet_field"); I = r.col("sr0_X") / ch["sr0"].gain
    R = np.abs((r.col("sr1_X") / ch["sr1"].gain) / I)
    o = np.argsort(B); B, R = B[o], R[o]
    nuF = abs(n_nom) * 1e16 * h_e          # nu = nuF / B at the nominal (run-5, prior-anchored) density
    print(f"run {rid}: n_nom {n_nom:+.1f}e12 (F_L nominal {nuF/4:.1f} T); B {B.min():.2f}-{B.max():.2f} T, R {R.min():.0f}-{R.max():.0f} Ohm "
          f"(sr1 50 uV = 5 kOhm FS -> max {R.max()/5000:.0%}), T {r.col('T_sample').min():.3f}-{r.col('T_sample').max():.3f} K")
    ax[k, 0].plot(B, R, lw=0.7); ax[k, 0].set_xlabel("B (T)"); ax[k, 0].set_ylabel("Rxx B_1-B_2 (Ohm)")
    for b_ in (2, 4, 6, 8, 10): ax[k, 0].text(b_, R.max() * 1.02, f"nu {nuF/b_:.0f}", fontsize=7, ha="center")
    ax[k, 0].set_title(f"run {rid} raw, n_nom {n_nom:+.1f}e12, D = 0")
    for lo, hi in [(1.0, 4.0), (1.5, 6.0), (1.0, 10.0)]:
        f, S = sdh_fft(R[:, None], B, b_range=(lo, hi), nfft=1024, bg_degree=3, log=False)
        sel = (f > 2) & (f < 60); ax[k, 1].plot(f[sel], S[0, sel] / S[0, sel].max(), lw=0.9, label=f"B [{lo}, {hi}] T  dF {1/(1/lo-1/hi):.1f} T")
    ax[k, 1].axvline(nuF / 4, color="k", ls=":", label="F_L nominal"); ax[k, 1].set_xlabel("F (T)"); ax[k, 1].legend(fontsize=7)
    ax[k, 1].set_title(f"run {rid} sdh_fft (linear R, deg-3 B-space bg)")
    try:
        print(sdh_onset(R, B, b_lo=0.3, r_full_scale=5000).summary())
    except Exception as e:
        print("sdh_onset:", e)
fig.tight_layout(); plt.show()
