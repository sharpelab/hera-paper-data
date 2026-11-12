"""Runs 6-7 (sdh-spot-check, D = 0): raw R(B) first, then background-subtracted dR vs 1/B, sdh_onset tone tables,
and 1/B FFTs in three high-B windows. R = (sr1_X/gain)/(sr0_X/gain_cur) per point (measured drain current)."""
import warnings
from hera.analysis import resolve_channels, sdh_onset, SdhOnsetError

spots = {6: ("electron", +3.2), 7: ("hole", -1.2)}
fig, ax = plt.subplots(3, 2, figsize=(14, 11))
for j, (rid, (side, n12)) in enumerate(spots.items()):
    r = run(rid); ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col("magnet_field"); I = r.col("sr0_X") / ch["sr0"].gain
    R = (r.col("sr1_X") / ch["sr1"].gain) / I; T = r.col("T_sample")
    o = np.argsort(B); B, R, I, T = B[o], R[o], I[o], T[o]
    FL = luttinger_frequency(abs(n12) * 1e16)
    print(f"=== run {rid} ({side}, n = {n12:+.1f}e12 prior scale, D = 0): {r.rows} pts, B {B.min():.2f}-{B.max():.2f} T, "
          f"T {T.min():.3f}-{T.max():.3f} K, R {R.min():.0f}..{R.max():.0f} Ohm, I_drain {I.min()*1e9:.2f}-{I.max()*1e9:.2f} nA, "
          f"interrupted={r.interrupted}; F_L(full n, 4-fold) = {FL:.1f} T")
    ax[0, j].plot(B, R, lw=0.7); ax[0, j].set_title(f"run {rid} raw Rxx(B) — {side}, n = {n12:+.1f}e12, D = 0")
    ax[0, j].set_xlabel("B (T)"); ax[0, j].set_ylabel("Rxx B_1-B_2 (Ohm)"); ax[0, j].axhline(0, color="k", lw=0.5)
    m = B >= 1.5; cf = np.polyfit(B[m], R[m], 5); dR = R[m] - np.polyval(cf, B[m])
    ax[1, j].plot(1 / B[m], dR, lw=0.7); ax[1, j].set_xlabel("1/B (1/T)"); ax[1, j].set_ylabel("R - poly5(B) (Ohm)")
    ax[1, j].set_title("oscillatory part, B > 1.5 T")
    for blo in (1.0, 2.0):
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                on = sdh_onset(np.abs(R), B, b_lo=blo, r_full_scale=50e-6 / 10e-9)
            print(f"-- sdh_onset, window from {blo} T:\n" + on.summary())
        except SdhOnsetError as e:
            print(f"-- sdh_onset (b_lo={blo}) failed: {e}")
    for k, (b1, b2) in enumerate([(1.5, 10.0), (3.0, 10.0), (5.0, 10.0)]):
        mm = (B >= b1) & (B <= b2)
        f, sp = sdh_fft(np.abs(R[mm])[:, None], B[mm], nfft=2048, bg_degree=5, log=False); sp = sp[0]
        sel = (f > 2) & (f < 120)
        ax[2, j].plot(f[sel], sp[sel] / sp[sel].max() + 1.1 * k, label=f"{b1}-{b2} T (bin {1/(1/b1-1/b2):.1f} T)")
    ax[2, j].axvline(FL, color="k", ls=":", label=f"F_L = {FL:.1f} T"); ax[2, j].legend(fontsize=8)
    ax[2, j].set_xlabel("F (T)"); ax[2, j].set_ylabel("|FFT| (norm., offset)"); ax[2, j].set_title("1/B FFT, poly5(B) background removed")
fig.suptitle("vti-02 sdh-spot-check runs 6-7: D = 0, T = 1.17-1.29 K, sr1 50 uV, I = 10 nA"); fig.tight_layout(); plt.show()
