"""Spot checks runs 6 (electron, n=+3.2e12) and 7 (hole, n=-1.2e12): raw, onset, FFT, model overlay."""
import sys, json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_onset, sdh_fft, luttinger_frequency, SdhOnsetError

sys.path.insert(0, str(Path.home() / "measurement_env/hera/models/tetralayer_fs_count"))
import fs_count_b0 as M

D = Path(__file__).resolve().parent.parent / "data"
OUT = Path(__file__).resolve().parent
spots = {6: +3.2, 7: -1.2}
res = {}
fig, axs = plt.subplots(3, 2, figsize=(13, 11))
for j, (rid, n12) in enumerate(spots.items()):
    r = open_run(D / str(rid))
    B = r.col("magnet_field"); X1 = r.col("sr1_X"); X0 = r.col("sr0_X")
    I = X0 / -1e6
    R = X1 / I
    o = np.argsort(B); B, R = B[o], R[o]
    FL = float(luttinger_frequency(n12 * 1e16))
    fs = 50e-6 / 10e-9
    print(f"=== run {rid}: n = {n12:+.2f}e12, F_L = {FL:.2f} T; B {B.min():.2f}-{B.max():.2f}, R {R.min():.1f}..{R.max():.1f} Ohm (FS {fs:.0f})")
    # model tones
    ab = M.abab_fs(n12 * 1e16); abm = M.abab_mstar(n12 * 1e16)
    ac = M.abca_fs(n12 * 1e16); acm = M.abca_mstar(n12 * 1e16)
    print("  model ABAB:", [(round(F, 2), round(m, 3)) for F, m in abm], " ABCA:", round(float(ac[4]), 2), ac[1], "m*", round(float(acm[1]), 3))
    try:
        on = sdh_onset(R, B, r_full_scale=fs, b_lo=0.3)
        print(on.summary())
        onset = on.onset_b
        tones = [(t.freq, t.onset_b, float(np.nanmax(t.snr))) for t in on.tones]
    except SdhOnsetError as e:
        print("  SdhOnsetError:", e); onset = None; tones = []
    ax = axs[0, j]; ax.plot(B, R, lw=0.7); ax.set_title(f"run {rid} raw R(B), n={n12:+.1f}e12"); ax.set_xlabel("B (T)"); ax.set_ylabel("R (Ohm)")
    if onset: ax.axvline(onset, color="r", ls="--", lw=0.8)
    specs = {}
    for lo in ([max(onset or 1.0, 1.0), 2.0, 3.0] if n12 > 0 else [max(onset or 1.0, 1.0), 1.5, 2.5]):
        for deg in (3, 5, 7):
            f, s = sdh_fft(R[:, None], B, b_range=(lo, B.max()), bg_degree=deg, nfft=4096, log=False)
            specs[(lo, deg)] = (f, s[0])
    ax = axs[1, j]
    for (lo, deg), (f, s) in specs.items():
        if deg == 5: ax.plot(f, s / s.max(), lw=0.8, label=f"b_lo {lo:.2f} deg {deg}")
    for F, m in abm: ax.axvline(F, color="g", ls=":", lw=1)
    ax.axvline(FL, color="k", ls="--", lw=1, label=f"F_L {FL:.1f}")
    ax.set_xlim(0, 2.2 * FL); ax.set_xlabel("F (T)"); ax.legend(fontsize=7); ax.set_title(f"run {rid} FFT (green: ABAB model; black: F_L = ABCA)")
    # peaks of the deg-5 lowest-lo spectrum
    from scipy.signal import find_peaks
    peaks_by = {}
    for key, (f, s) in specs.items():
        pk, pr = find_peaks(s, prominence=0.05 * s.max())
        top = sorted(pk, key=lambda p: -s[p])[:6]
        peaks_by[key] = sorted([(round(float(f[p]), 2), round(float(s[p] / s.max()), 2)) for p in top])
        print(f"  FFT b_lo {key[0]:.2f} deg {key[1]}: peaks (F, rel amp) {peaks_by[key]}")
    # background-subtracted trace vs 1/B
    ax = axs[2, j]
    lo = max(onset or 1.0, 1.0); m_ = B >= lo
    cf = np.polyfit(B[m_], R[m_], 5); dR = R[m_] - np.polyval(cf, B[m_])
    ax.plot(1 / B[m_], dR, lw=0.7); ax.set_xlabel("1/B (1/T)"); ax.set_ylabel("dR (Ohm)"); ax.set_title(f"run {rid} bg-sub (deg 5, B>{lo:.2f})")
    res[rid] = dict(n12=n12, FL=FL, onset=onset, tones=tones, peaks={f"{k[0]:.2f}/{k[1]}": v for k, v in peaks_by.items()},
                    abab=[(float(F), float(m)) for F, m in abm], abca=(float(ac[4]), float(acm[1])),
                    Rmin=float(R.min()), Rmax=float(R.max()), R_lowB=float(np.median(R[B < 0.6])))
fig.tight_layout(); fig.savefig(OUT / "spots_67.png", dpi=90)
json.dump(res, open(OUT / "spots_67.json", "w"), indent=1, default=float)
