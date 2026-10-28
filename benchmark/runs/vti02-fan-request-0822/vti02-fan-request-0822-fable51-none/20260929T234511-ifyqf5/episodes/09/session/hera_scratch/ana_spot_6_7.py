"""Runs 6 (e-side, n = +3.2e12) and 7 (h-side, n = -1.2e12) — sdh-spot-check at D = 0. Raw Rxx(B) first, then the
1/B FFT (three windows) and per-tone onsets (sdh_onset); F_L = |n| h / 4e from the run-5 calibration for reference."""
import warnings
from hera.analysis import resolve_channels, sdh_onset, SdhOnsetError

spots = [(6, 3.2), (7, -1.2)]
fig, ax = plt.subplots(3, 2, figsize=(13, 11))
for j, (rid, n12) in enumerate(spots):
    r = run(rid)
    ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col("magnet_field"); I = r.col("sr0_X") / ch["sr0"].gain
    R = (r.col("sr1_X") / ch["sr1"].gain) / I; T = r.col("T_sample")
    o = np.argsort(B); B, R, I, T = B[o], R[o], I[o], T[o]
    FL = luttinger_frequency(abs(n12) * 1e16)
    print(f"=== run {rid}: n = {n12:+.2f}e12 (run-5 cal), D = 0; F_L(4-fold, full n) = {FL:.2f} T; T {T.min():.3f}-{T.max():.3f} K; "
          f"I_drain {I.min()*1e9:.2f}-{I.max()*1e9:.2f} nA; Rxx {R.min():.0f}..{R.max():.0f} Ohm; complete={r.complete}")
    # raw
    ax[0, j].plot(B, R, lw=0.8); ax[0, j].axhline(0, color="k", lw=0.5)
    ax[0, j].set_title(f"run {rid}: n = {n12:+.2f}e12, D = 0 — raw Rxx(B), sr1 = B_1-B_2"); ax[0, j].set_xlabel("B (T)"); ax[0, j].set_ylabel("Rxx (Ohm)")
    # FFT in 1/B, three windows
    for lo, hi, col in [(1.5, 10.0, "C0"), (3.0, 10.0, "C1"), (1.5, 5.0, "C2")]:
        m = (B >= lo) & (B <= hi)
        f, sp = sdh_fft(R[m][:, None], B[m], nfft=2048, bg_degree=5, log=False); sp = sp[0]
        sel = (f > 1) & (f < 150)
        ax[1, j].plot(f[sel], sp[sel] / sp[sel].max(), color=col, lw=0.9, label=f"B {lo}-{hi} T")
        pk = np.sort(f[sel][np.argsort(sp[sel])[::-1][:6]])
        print(f"  FFT {lo}-{hi} T, top-6 freqs: {np.round(pk, 1)} T")
    for k in (1, 2, 4): ax[1, j].axvline(FL / k, color="gray", ls=":", lw=0.8)
    ax[1, j].set_xlim(0, 80); ax[1, j].set_xlabel("F (T)"); ax[1, j].set_ylabel("|FFT| (norm)"); ax[1, j].legend(fontsize=7)
    ax[1, j].set_title(f"1/B FFT — dotted F_L, F_L/2, F_L/4 = {FL:.1f} / {FL/2:.1f} / {FL/4:.1f} T")
    # oscillatory part vs 1/B
    m = B >= 1.0; dR = R[m] - np.polyval(np.polyfit(B[m], R[m], 5), B[m])
    ax[2, j].plot(1 / B[m], dR, lw=0.7); ax[2, j].set_xlabel("1/B (1/T)"); ax[2, j].set_ylabel("dRxx (Ohm), poly5(B) removed"); ax[2, j].set_title("oscillatory part vs 1/B (B >= 1 T)")
    # tone onsets
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            on = sdh_onset(R, B, b_lo=0.3, r_full_scale=50e-6 / 10e-9)
        print(on.summary())
    except SdhOnsetError as e:
        print("  sdh_onset:", e)
fig.tight_layout(); plt.show()
