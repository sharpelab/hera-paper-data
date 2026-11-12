"""Spot-check read, runs 6 (e, n=+3.2e12) and 7 (h, n=-1.2e12): raw R(B), onset, 1/B FFT vs model tones."""
import sys, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, resolve_channels, sdh_onset, sdh_fft, luttinger_frequency
sys.path.insert(0, "/home/hera/measurement_env/hera/models/tetralayer_fs_count")
import fs_count_b0 as M

D = "/home/hera/measurements/zack/20260822-vti-02/data"
spots = {6: 3.2, 7: -1.2}
fig, ax = plt.subplots(3, 2, figsize=(13, 11))
for j, (rid, n) in enumerate(spots.items()):
    r = open_run(f"{D}/{rid}")
    ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col("magnet_field")
    I = r.col("sr0_X") / ch["sr0"].gain
    R = (r.col("sr1_X") / ch["sr1"].gain) / np.abs(I)
    o = np.argsort(B); B, R, I = B[o], R[o], I[o]
    T = r.col("T_sample")
    FL = float(luttinger_frequency(n*1e16))
    print(f"\n=== run {rid}: n = {n:+.1f}e12, interrupted={r.interrupted}, {len(B)} pts, B {B.min():.3f}..{B.max():.3f} T")
    print(f"R {R.min():.1f}..{R.max():.1f} Ohm; R(B<0.1)={np.median(R[B<0.1]):.1f}; R(9.5-10)={np.median(R[B>9.5]):.1f}; I {I.min()*1e9:.2f}..{I.max()*1e9:.2f} nA; T {T.min():.3f}..{T.max():.3f} K")
    fs_v = 50e-6 / (np.median(np.abs(I)))
    print(f"FS (50uV / I) = {fs_v:.0f} Ohm; max R fraction of FS = {np.abs(R).max()/fs_v:.2f};  F_L = {FL}")
    ms = M.abab_mstar(n*1e16)
    ca = M.abca_mstar(n*1e16)
    print("model ABAB orbits (F, m*):", [(round(f, 2), round(m, 3)) for f, m in ms], " ABCA:", (round(ca[0], 2), round(ca[1], 3)))
    ax[0, j].plot(B, R, lw=0.7); ax[0, j].set_title(f"run {rid} raw Rxx, n={n:+.1f}e12"); ax[0, j].set_xlabel("B (T)"); ax[0, j].set_ylabel("R (Ohm)")
    try:
        on = sdh_onset(R, B, r_full_scale=fs_v)
        print(on.summary())
        onset = on.onset_b
    except Exception as e:
        print("sdh_onset:", type(e).__name__, e); onset = None
    lo = max(onset or 1.5, 1.0)
    for bl, sty in ((lo, "-"), (lo + 1.0, "--"), (lo + 2.5, ":")):
        f, sp = sdh_fft(R[:, None], B, b_range=(bl, B.max()), bg_degree=5, log=False)
        s = sp[0]
        k = np.argsort(s)[::-1]
        # local maxima
        pk = [i for i in range(1, len(s) - 1) if s[i] > s[i - 1] and s[i] > s[i + 1] and f[i] > 2]
        pk = sorted(pk, key=lambda i: -s[i])[:6]
        print(f"  FFT window [{bl:.2f},{B.max():.1f}] T: dF={1/(1/bl-1/B.max()):.2f} T; peaks (F, amp rel): " +
              ", ".join(f"{f[i]:.1f}:{s[i]/s[pk[0]]:.2f}" for i in pk))
        ax[1, j].plot(f, s / s[pk[0]], sty, lw=0.8, label=f"from {bl:.2f} T")
    for fm, _ in ms:
        ax[1, j].axvline(fm, color="g", ls=":", lw=0.8)
    ax[1, j].axvline(abs(ca[0]), color="r", ls="--", lw=0.8)
    ax[1, j].set_xlim(0, 2.2 * abs(ca[0])); ax[1, j].legend(fontsize=7); ax[1, j].set_xlabel("F (T)")
    ax[1, j].set_title("FFT (green: ABAB model, red: F_L/ABCA)")
    # detrended trace vs 1/B
    m = B > lo
    cf = np.polyfit(B[m], R[m], 5); dR = R[m] - np.polyval(cf, B[m])
    ax[2, j].plot(1 / B[m], dR, lw=0.6); ax[2, j].set_xlabel("1/B (1/T)"); ax[2, j].set_ylabel("dR (Ohm)")
fig.tight_layout(); fig.savefig("/home/hera/measurements/zack/20260822-vti-02/hera_scratch/spots_67.png", dpi=90)
