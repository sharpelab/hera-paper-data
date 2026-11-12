"""Runs 6 (e, n=+3.2e12) and 7 (h, n=-1.2e12): raw MR, sdh_onset, sdh_fft vs F_L + model tones."""
import sys, warnings, numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from pathlib import Path
from hera.analysis import open_run, resolve_channels, sdh_onset, sdh_fft, luttinger_frequency, SdhOnsetError
sys.path.insert(0, str(Path.home()/"measurement_env/hera/models/tetralayer_fs_count"))
import fs_count_b0 as M
D = Path(__file__).resolve().parent.parent / "data"
out = {}
fig, ax = plt.subplots(2, 3, figsize=(16, 8))
for row, (rid, n) in enumerate([(6, 3.2), (7, -1.2)]):
    r = open_run(str(D / str(rid)))
    ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col("magnet_field"); I = r.col("sr0_X") / ch["sr0"].gain
    R = (r.col("sr1_X") / ch["sr1"].gain) / 10e-9       # R = V / I_bias (hera-watch convention)
    Rd = (r.col("sr1_X") / ch["sr1"].gain) / I
    Y = r.col("sr1_Y") if "sr1_Y" in r.cols else None
    o = np.argsort(B); B, R, Rd, I = B[o], R[o], Rd[o], I[o]
    print(f"\n=== run {rid} n={n:+.1f}e12  cols={r.cols}")
    print(f"B {B.min():.3f}-{B.max():.3f} T, N={len(B)}; R {R.min():.1f}..{R.max():.1f} Ohm; R(B<0.4)={np.median(R[B<0.4]):.1f}; I {I.min()*1e9:.3f}-{I.max()*1e9:.3f} nA; T {np.nanmin(r.col('T_sample')):.3f}-{np.nanmax(r.col('T_sample')):.3f} K")
    FL = luttinger_frequency(abs(n)*1e16) if True else None
    print(f"F_L = {FL}")
    rfs = 50e-6 / 10e-9
    try:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            on = sdh_onset(R, B, r_full_scale=rfs)
            for x in w: print("  warn:", x.message)
        print(on.summary())
        out[rid] = on
    except SdhOnsetError as e:
        print("SdhOnsetError:", e); on = None
    # model
    try:
        Ef, orb = M.abab_fs(n); ms = M.abab_mstar(n)
        print("ABAB orbits:", [(round(F,2)) for F, k in orb], "m*:", [(round(F,2), round(m,3)) for F, m in ms])
    except Exception as e: print("abab err", e)
    try:
        a = M.abca_fs(n); am = M.abca_mstar(n); print("ABCA:", a, "m*", am)
    except Exception as e: print("abca err", e)
    ax[row, 0].plot(B, R, lw=.7); ax[row, 0].set_title(f"run {rid} raw R (n={n:+.1f}e12)"); ax[row, 0].set_xlabel("B (T)")
    for k, blo in enumerate([1.5, 2.5] if rid == 6 else [1.0, 2.0]):
        fr, sp = sdh_fft(R[:, None], B, b_range=(blo, B.max()), bg_degree=5, log=False)
        ax[row, 1+k].plot(fr, sp[0]); ax[row, 1+k].set_xlim(0, 2.2*FL); ax[row, 1+k].axvline(FL, color="k", ls="--")
        ax[row, 1+k].set_title(f"FFT b_range ({blo}, {B.max():.1f})")
        pk = np.argsort(sp[0])[::-1]
        from scipy.signal import find_peaks
        p, _ = find_peaks(sp[0], prominence=0.05*sp[0].max())
        p = p[np.argsort(sp[0][p])[::-1]][:6]
        print(f"  FFT b_range=({blo},{B.max():.1f}): peaks (F T, rel amp): " + ", ".join(f"{fr[i]:.2f}:{sp[0][i]/sp[0][p[0]]:.2f}" for i in p) + f"  | F/F_L: " + ", ".join(f"{fr[i]/FL:.3f}" for i in p))
fig.tight_layout(); fig.savefig(Path(__file__).with_suffix(".png"), dpi=90)
