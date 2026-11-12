"""Spot checks run 6 (e, n=+3.2e12) and run 7 (h, n=-1.2e12): raw R(B), onset, FFT vs F_L + model."""
import sys, warnings
import numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from hera.analysis import open_run, resolve_channels, sdh_onset, sdh_fft, luttinger_frequency
sys.path.insert(0, "/home/hera/measurement_env/hera/models/tetralayer_fs_count")
import fs_count_b0 as M
D = "/home/hera/measurements/zack/20260822-vti-02/data"
out = {}
fig, ax = plt.subplots(3, 2, figsize=(13, 11))
for j, (rid, n) in enumerate([(6, 3.2), (7, -1.2)]):
    r = open_run(f"{D}/{rid}")
    ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col("magnet_field"); I = r.col("sr0_X") / ch["sr0"].gain
    V = r.col("sr1_X") / ch["sr1"].gain
    R = np.abs(V / I)
    o = np.argsort(B); B, R, I, V = B[o], R[o], I[o], V[o]
    T = r.col("T_sample"); itg = r.col("k_2400_tg_curr"); ibg = r.col("k_2400_bg_curr")
    Ib = np.median(np.abs(I))
    rfs = 50e-6 / Ib
    FL = luttinger_frequency(abs(n)*1e16) if True else None
    print(f"\n=== run {rid} n={n:+.2f}e12: {len(B)} pts B {B.min():.3f}-{B.max():.3f}; R {R.min():.1f}-{R.max():.1f} Ohm (FS {rfs:.0f}); "
          f"I {np.abs(I).min()*1e9:.2f}-{np.abs(I).max()*1e9:.2f} nA; T {T.min():.3f}-{T.max():.3f}; I_tg {itg.min()*1e12:+.0f}..{itg.max()*1e12:+.0f} pA; "
          f"I_bg {ibg.min()*1e12:+.0f}..{ibg.max()*1e12:+.0f} pA; interrupted={r.interrupted}; F_L = {FL:.2f} T")
    print(f"max |sr1_X|/sens = {np.abs(V).max()/50e-6:.3f}")
    try:
        ab = M.abab_fs(n); am = M.abab_mstar(n); ac = M.abca_fs(n); acm = M.abca_mstar(n)
        print("model ABAB F:", [round(f, 2) for f, _ in ab[1]], "m*:", [(round(f,2), round(m,3)) for f, m in am])
        print("model ABCA:", ac, "m*", acm)
    except Exception as e: print("model err", e)
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        try:
            on = sdh_onset(R, B, r_full_scale=rfs, b_lo=max(0.3, B.min()))
            print(on.summary())
            out[rid] = on
        except Exception as e:
            print("SdhOnsetError:", e); on = None
        for x in w: print("warn:", x.message)
    ax[0, j].plot(B, R, lw=0.7); ax[0, j].set_title(f"run {rid} raw R(B), n={n:+.1f}e12 D=0"); ax[0, j].set_xlabel("B (T)"); ax[0, j].set_ylabel("R (Ohm)")
    # background subtracted
    for lo in ([1.0, 2.0, 3.0] if rid == 6 else [1.0, 2.0, 3.0]):
        m = B >= lo
        p = np.polyfit(B[m], R[m], 5); dR = R[m] - np.polyval(p, B[m])
        ax[1, j].plot(1/B[m], dR + 0*lo, lw=0.6, label=f"bg deg5 from {lo} T")
        freqs, spec = sdh_fft(R[m][:, None], B[m], b_range=(lo, B.max()), bg_degree=5, log=False)
        s = spec[0]
        ax[2, j].plot(freqs, s / s[freqs > 1].max(), lw=0.8, label=f"{lo}-{B.max():.0f} T")
        k = np.argsort(s * (freqs > 1.5))[::-1]
        # peak list
        from scipy.signal import find_peaks
        pk, _ = find_peaks(s, prominence=0.05 * s[freqs > 1].max())
        pk = [p_ for p_ in pk if freqs[p_] > 1.5]
        pk = sorted(pk, key=lambda p_: -s[p_])[:6]
        print(f"  FFT {lo}-{B.max():.1f} T: dF={1/(1/lo-1/B.max()):.2f} T; peaks (F, rel amp): " + ", ".join(f"{freqs[p_]:.2f}:{s[p_]/s[pk[0]]:.2f}" for p_ in pk))
    ax[1, j].set_xlabel("1/B"); ax[1, j].legend(fontsize=7)
    ax[2, j].axvline(FL, color="k", ls="--", label="F_L")
    try:
        for f, _ in M.abab_fs(n)[1]: ax[2, j].axvline(f, color="b", ls=":", lw=1)
    except Exception: pass
    ax[2, j].set_xlim(0, 2.2 * FL); ax[2, j].set_xlabel("F (T)"); ax[2, j].legend(fontsize=7)
fig.tight_layout(); fig.savefig("/home/hera/measurements/zack/20260822-vti-02/hera_scratch/spot_runs67.png", dpi=90)
