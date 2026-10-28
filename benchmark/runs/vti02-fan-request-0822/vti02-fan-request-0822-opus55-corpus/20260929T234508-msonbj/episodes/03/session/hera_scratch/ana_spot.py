"""SdH spot checks runs 6 (e, n=+3.2e12) and 7 (h, n=-1.2e12): raw MR, onset, FFT vs F_L + model."""
import sys, warnings
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, resolve_channels, sdh_onset, sdh_fft, luttinger_frequency, SdhOnsetError

sys.path.insert(0, "/home/hera/measurement_env/hera/models/tetralayer_fs_count")
import fs_count_b0 as fs

D = "/home/hera/measurements/zack/20260822-vti-02/data"
spots = {6: +3.2, 7: -1.2}
fig, ax = plt.subplots(3, 2, figsize=(13, 11))
out = {}
for j, (rid, n12) in enumerate(spots.items()):
    r = open_run(f"{D}/{rid}")
    ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col("magnet_field")
    I = r.col("sr0_X") / ch["sr0"].gain
    V = r.col("sr1_X") / ch["sr1"].gain
    R = V / I
    o = np.argsort(B); B, R, I = B[o], R[o], I[o]
    T = r.col("T_sample")
    itg, ibg = r.col("k_2400_tg_curr"), r.col("k_2400_bg_curr")
    FL = float(luttinger_frequency(n12 * 1e16))
    print(f"\n=== run {rid}  n = {n12:+.2f}e12  F_L = {FL:.2f} T  pts {len(B)}  B {B.min():.3f}..{B.max():.3f}")
    print(f"R {R.min():.1f}..{R.max():.1f} Ohm; R(B~0) {R[B<0.35].mean():.1f}; I_drain {I.min()*1e9:.2f}..{I.max()*1e9:.2f} nA; "
          f"T {T.min():.3f}..{T.max():.3f} K; I_tg {itg.min()*1e12:+.0f}..{itg.max()*1e12:+.0f} pA; I_bg {ibg.min()*1e12:+.0f}..{ibg.max()*1e12:+.0f} pA")
    I_bias = 1.0 / 100e6
    rfs = 50e-6 / I_bias
    print(f"sr1 FS {rfs:.0f} Ohm; max/FS {np.abs(R).max()/rfs:.2f}")
    # model
    try:
        Ef, orb = fs.abab_fs(n12 * 1.0)
        print("ABAB orbits (F T):", [round(f, 2) for f, _ in orb], " m*:", [(round(f, 2), round(m, 3)) for f, m in fs.abab_mstar(n12)])
    except Exception as e:
        print("abab model err", e)
    try:
        a = fs.abca_fs(n12 * 1.0); print("ABCA:", a[1:], " m*", fs.abca_mstar(n12))
    except Exception as e:
        print("abca model err", e)
    try:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            on = sdh_onset(R, B, b_lo=0.3, r_full_scale=rfs)
            for x in w: print("WARN:", x.message)
        print(on.summary())
        out[rid] = on
    except SdhOnsetError as e:
        print("SdhOnsetError:", e); on = None
    ax[0, j].plot(B, R, lw=0.7); ax[0, j].set_title(f"run {rid} raw Rxx, n={n12:+.1f}e12"); ax[0, j].set_xlabel("B (T)"); ax[0, j].set_ylabel("Rxx (Ohm)")
    # bg-subtracted
    for lo in ([on.onset_b] if on else []) + [1.5, 2.5, 4.0]:
        m = (B >= lo)
        cf = np.polyfit(B[m], R[m], 5); dR = R[m] - np.polyval(cf, B[m])
        if lo == 2.5:
            ax[1, j].plot(1 / B[m], dR, lw=0.7); ax[1, j].set_xlabel("1/B"); ax[1, j].set_title(f"dR (deg5 bg, B>{lo})")
        f, s = sdh_fft(R[:, None], B, b_range=(lo, B.max()), bg_degree=5, log=False, nfft=4096)
        sp = s[0]; k = np.argsort(sp)[::-1]
        # top peaks (local maxima)
        from scipy.signal import find_peaks
        pk, _ = find_peaks(sp); pk = pk[np.argsort(sp[pk])[::-1]][:6]
        print(f"  FFT B>{lo:.2f}: dF={1/(1/lo-1/B.max()):.2f} T; peaks " + ", ".join(f"{f[p]:.2f}({sp[p]/sp[pk[0]]:.2f})" for p in sorted(pk)))
        ax[2, j].plot(f, sp / sp[pk[0]], lw=0.8, label=f"B>{lo:.2f}")
    ax[2, j].axvline(FL, color="k", ls="--", label="F_L")
    ax[2, j].set_xlim(0, 2.5 * FL); ax[2, j].legend(fontsize=7); ax[2, j].set_xlabel("F (T)")
fig.tight_layout(); fig.savefig("/home/hera/measurements/zack/20260822-vti-02/hera_scratch/spot_runs67.png", dpi=90)
