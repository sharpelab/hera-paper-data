"""Spot checks, Nyquist-clean redo.

Both records contain a coarse low-B leg that is badly undersampled for the
tones in play; the first pass FFT'd through it and the peak set wandered with
the cutoff. Here: restrict each record to the field range where the *grid*
Nyquist-resolves F_L, then read onset / tones / stability there.

  run 6 (e, n=+3.2e12): 50 mT below 1 T, 10 mT above -> use B >= 1.0 T
  run 7 (h, n=-1.2e12): 20 mT uniform -> Nyquist on F_L=12.4 T needs
        d(1/B)=dB/B^2 <= 1/(2*12.4) -> B >= sqrt(0.02*2*12.4) = 0.70 T
"""
import json
import warnings
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from hera.analysis import open_run, sdh_onset, sdh_fft, luttinger_frequency

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data"
I_BIAS = 10.0e-9
R_FS = 50e-6 / I_BIAS

CASES = {6: dict(n=+3.2e12, label="electron", b_valid=1.0),
         7: dict(n=-1.2e12, label="hole", b_valid=0.70)}

res = {}
fig, axes = plt.subplots(3, 2, figsize=(15, 12))

for col, rid in enumerate([6, 7]):
    c = CASES[rid]
    r = open_run(DATA / str(rid))
    B = np.asarray(r.col("magnet_field"), float)
    R = np.asarray(r.col("sr1_X"), float) / I_BIAS
    o = np.argsort(B); B, R = B[o], R[o]
    F_L = float(luttinger_frequency(abs(c["n"]) * 1e4))

    keep = B >= c["b_valid"]
    Bv, Rv = B[keep], R[keep]
    dB = np.median(np.diff(Bv))
    nyq_at_lo = 1.0 / (2 * (dB / Bv[0] ** 2))     # max resolvable F at the low edge
    print(f"\n########## run {rid} — {c['label']}  n={c['n']/1e12:+.2f}e12  F_L={F_L:.2f} T")
    print(f"  valid window B >= {c['b_valid']} T: {len(Bv)} pts, dB={dB*1e3:.0f} mT, "
          f"d(1/B)@lo = {dB/Bv[0]**2:.4f} 1/T -> Nyquist F_max = {nyq_at_lo:.1f} T "
          f"({'OK' if nyq_at_lo > F_L else 'UNDERSAMPLED'} vs F_L)")
    print(f"  R range in window: {Rv.min():.1f} .. {Rv.max():.1f} Ohm (fs {np.abs(Rv).max()/R_FS:.3f})")

    # ---- onset on the valid window ----
    try:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            on = sdh_onset(Rv, Bv, b_lo=c["b_valid"], r_full_scale=R_FS)
        for ww in w:
            print("  warn:", ww.message)
        print("  " + on.summary().replace("\n", "\n  "))
    except Exception as e:
        on = None
        print(f"  sdh_onset FAILED: {type(e).__name__}: {e}")

    # ---- raw ----
    ax = axes[0, col]
    ax.plot(B, R, lw=0.6, color="0.6", label="full record")
    ax.plot(Bv, Rv, lw=0.7, color="C0", label=f"Nyquist-valid B>={c['b_valid']} T")
    ax.set_xlabel("B (T)"); ax.set_ylabel(r"$R_{xx}\ (\Omega)$"); ax.legend(fontsize=7)
    ax.set_title(f"run {rid} raw — {c['label']}, n={c['n']/1e12:+.1f}e12, D=0, T=1.2 K")

    # ---- bg-subtracted vs 1/B ----
    ax = axes[1, col]
    p = np.polyfit(Bv, Rv, 5)
    ax.plot(1 / Bv, Rv - np.polyval(p, Bv), lw=0.8)
    ax.set_xlabel("1/B (1/T)"); ax.set_ylabel(r"$\Delta R_{xx}\ (\Omega)$")
    ax.set_title(f"run {rid} — deg-5 B-space background removed")

    # ---- FFT stability sweep: cutoff x bg_degree ----
    ax = axes[2, col]
    peak_tbl = {}
    for cut in [c["b_valid"], max(c["b_valid"], 1.5), 2.0, 3.0]:
        for deg in (3, 5, 7):
            if cut >= Bv.max() - 1:
                continue
            f, spec = sdh_fft(Rv[:, None], Bv, b_range=(cut, Bv.max()),
                              bg_degree=deg, log=False, nfft=4096)
            s = spec[0]
            if deg == 5:
                ax.plot(f, s / s.max(), lw=0.9, label=f"cut {cut:.2f} T (deg 5)")
            idx = [i for i in range(2, len(f) - 2)
                   if s[i] > s[i-1] and s[i] > s[i+1] and s[i] > 0.15 * s.max() and f[i] > 2]
            peak_tbl[f"cut{cut:.2f}_deg{deg}"] = [
                (round(float(f[i]), 2), round(float(f[i] / F_L), 3), round(float(s[i] / s.max()), 2))
                for i in idx]
    ax.axvline(F_L, color="k", ls="--", lw=1.2, label=f"$F_L$ = {F_L:.1f} T")
    for frac, cc in ((0.72, "r"), (0.28, "r")):
        ax.axvline(frac * F_L, color=cc, ls=":", lw=1)
    ax.set_xlim(0, 1.8 * F_L); ax.set_xlabel("F (T)"); ax.set_ylabel("|FFT| norm")
    ax.legend(fontsize=7); ax.set_title(f"run {rid} — 1/B FFT (dashed $F_L$, dotted 0.28/0.72 $F_L$)")

    print("  FFT peaks  (F [T], F/F_L, rel amp):")
    for k, v in peak_tbl.items():
        print(f"    {k:>16}: {v}")

    res[rid] = dict(label=c["label"], n=c["n"], F_L=F_L, b_valid=c["b_valid"],
                    onset_b=float(on.onset_b) if on else None,
                    peaks=peak_tbl,
                    tones=[dict(freq=float(t.freq), onset_b=float(t.onset_b),
                                censored=bool(t.censored), marginal=bool(t.marginal),
                                harmonic_of=(float(t.harmonic_of) if t.harmonic_of else None),
                                snr=float(np.nanmax(t.snr)) if getattr(t, "snr", None) is not None else None,
                                delta_f=float(t.delta_f(Bv.max())))
                           for t in on.tones] if on else [])

plt.tight_layout()
plt.savefig(HERE / "spot_checks2.png", dpi=110)
(HERE / "spot_summary2.json").write_text(json.dumps(res, indent=1))
print("\nwrote spot_checks2.png")
