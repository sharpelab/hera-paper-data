"""sdh-spot-check read, runs 6 (electron, n = +3.2e12) and 7 (hole, n = -1.2e12), D = 0 (run-5 cal).
Raw first, then background-subtracted vs 1/B, then onset (sdh_onset) + windowed FFTs (sdh_fft, linear R —
the electron trace reaches R ~ 0 at QH minima, so the log path's floor would clip it)."""
import warnings
from hera.analysis import sdh_onset

I_BIAS, SENS = 1.0 / 100e6, 50e-6            # 1 V / 100 MOhm; sr1 50 uV both runs
spots = {6: dict(n=+3.2, b_lo=1.0), 7: dict(n=-1.2, b_lo=0.5)}   # run 6 is 50 mT-sampled below 1 T -> onset search from 1.0 T
fig, ax = plt.subplots(3, 2, figsize=(13, 11))
for k, (rid, sp) in enumerate(spots.items()):
    r = run(rid); B = r.col("magnet_field"); R = r.col("sr1_X") / I_BIAS
    o = np.argsort(B); B, R = B[o], R[o]
    FL = float(luttinger_frequency(sp["n"] * 1e16))
    # raw
    ax[0, k].plot(B, R, lw=0.7); ax[0, k].set_xlabel("B (T)"); ax[0, k].set_ylabel("Rxx (Ohm)")
    ax[0, k].set_title(f"run {rid} RAW: n = {sp['n']:+.1f}e12, D = 0 (F_L = {FL:.1f} T nominal)")
    # bg-subtracted vs 1/B
    m = B > 1.0; dR = R[m] - np.polyval(np.polyfit(B[m], R[m], 5), B[m])
    ax[1, k].plot(1 / B[m], dR, lw=0.7); ax[1, k].set_xlabel("1/B (1/T)"); ax[1, k].set_ylabel("dRxx, deg-5 bg in B (Ohm)")
    # onset
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        on = sdh_onset(R, B, b_lo=sp["b_lo"], r_full_scale=SENS / I_BIAS)
    print(f"=== run {rid}  n = {sp['n']:+.1f}e12  F_L = {FL:.1f} T  R {R.min():.0f}..{R.max():.0f} Ohm (fs max {R.max()*I_BIAS/SENS:.2f}) ===")
    print(on.summary()); [print("  note:", x.message) for x in w]
    # FFT windows
    for (lo, hi), c in [((1.5, 10), "C0"), ((1.0, 5.5), "C2"), ((2.5, 10), "C1")]:
        f, s = sdh_fft(R[:, None], B, b_range=(lo, hi), log=False, bg_degree=5, nfft=4096)
        sp_ = s[0]; ok = (f > 2) & (f < 3 * FL)
        ax[2, k].plot(f, sp_ / sp_[ok].max(), c, lw=0.8, label=f"{lo}-{hi} T (dF {1/(1/lo-1/hi):.1f} T)")
        pk = [i for i in range(1, len(f) - 1) if ok[i] and sp_[i] > sp_[i - 1] and sp_[i] > sp_[i + 1]]
        pk = sorted(pk, key=lambda i: -sp_[i])[:5]
        print(f"  FFT {lo}-{hi} T peaks F(rel): " + ", ".join(f"{f[i]:.1f}({sp_[i]/sp_[pk[0]]:.2f})" for i in pk))
    ax[2, k].axvline(FL, color="k", ls="--", lw=0.8, label="F_L nominal")
    ax[2, k].set_xlim(0, 2.2 * FL); ax[2, k].set_xlabel("F (T)"); ax[2, k].legend(fontsize=7)
fig.tight_layout(); plt.show()
