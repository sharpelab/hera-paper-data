"""SdH spot checks: run 6 (electron, n=+3.2e12) and run 7 (hole, n=-1.2e12).
Raw R(B), onset, FFT in 1/B, tones vs F_L. Scratch workbench."""
import json
import warnings
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from hera.analysis import open_run, summarize_run, sdh_onset, sdh_fft, luttinger_frequency

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data"

I_BIAS = 10.0e-9          # sr1 drive / 100 MOhm (hera-watch header)
SENS = 50e-6              # sr1 sensitivity both runs
R_FS = SENS / I_BIAS      # 5 kOhm full scale

SPOTS = {6: dict(n=+3.2e12, label="electron"),
         7: dict(n=-1.2e12, label="hole")}

summary = {}
fig, axes = plt.subplots(3, 2, figsize=(14, 11))

for col, rid in enumerate([6, 7]):
    r = open_run(DATA / str(rid))
    n_cm2 = SPOTS[rid]["n"]
    lab = SPOTS[rid]["label"]
    B = np.asarray(r.col("magnet_field"), float)
    R = np.asarray(r.col("sr1_X"), float) / 1.0 / I_BIAS   # gain 1
    T = np.asarray(r.col("T_sample"), float)
    o = np.argsort(B)
    B, R, T = B[o], R[o], T[o]

    F_L = float(luttinger_frequency(abs(n_cm2) * 1e4))     # n in m^-2 -> Tesla
    print(f"\n===== run {rid} ({lab}, n={n_cm2:+.2e} cm^-2) =====")
    print(summarize_run(r))
    print(f"F_L = {F_L:.2f} T ; T_sample {T.min():.3f}-{T.max():.3f} K ; "
          f"R {np.nanmin(R):.1f}..{np.nanmax(R):.1f} Ohm ; fs_max {np.nanmax(np.abs(R))/R_FS:.3f}")

    # --- raw ---
    ax = axes[0, col]
    ax.plot(B, R, lw=0.7)
    ax.set_xlabel("B (T)"); ax.set_ylabel(r"$R_{xx}$ ($\Omega$)")
    ax.set_title(f"run {rid} — raw {lab}, n={n_cm2/1e12:+.1f}e12, D=0")

    # --- onset ---
    on = None
    try:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            on = sdh_onset(R, B, b_lo=max(0.3, B.min()), r_full_scale=R_FS)
        for ww in w:
            print("  warn:", ww.message)
        print(on.summary())
    except Exception as e:
        print(f"  sdh_onset FAILED: {type(e).__name__}: {e}")

    # --- background-subtracted trace in 1/B ---
    b_cut = on.onset_b if on is not None else 2.0
    b_hi = B.max()
    m = (B >= b_cut) & (B <= b_hi)
    p = np.polyfit(B[m], R[m], 5)
    dR = R[m] - np.polyval(p, B[m])
    ax = axes[1, col]
    ax.plot(1.0 / B[m], dR, lw=0.8)
    ax.set_xlabel("1/B (1/T)"); ax.set_ylabel(r"$\Delta R_{xx}$ ($\Omega$)")
    ax.set_title(f"run {rid} — bg-subtracted (deg 5), B {b_cut:.2f}-{b_hi:.1f} T")

    # --- FFT, a few cutoffs (stability sweep) ---
    ax = axes[2, col]
    peaks = {}
    for cut in sorted({round(b_cut, 2), 2.0, 3.0, 4.0}):
        if cut >= b_hi - 1:
            continue
        f, spec = sdh_fft(R[:, None], B, b_range=(cut, b_hi), bg_degree=5, log=False, nfft=2048)
        s = spec[0]
        ax.plot(f, s / s.max(), lw=0.9, label=f"cut {cut:.2f} T")
        # peak list
        idx = [i for i in range(2, len(f) - 2)
               if s[i] > s[i-1] and s[i] > s[i+1] and s[i] > 0.12 * s.max() and f[i] > 2]
        peaks[cut] = [(round(float(f[i]), 2), round(float(s[i] / s.max()), 3)) for i in idx]
    ax.axvline(F_L, color="k", ls="--", lw=1, label=f"$F_L$={F_L:.1f} T")
    ax.axvline(0.72 * F_L, color="r", ls=":", lw=1, label="0.72/0.28 $F_L$")
    ax.axvline(0.28 * F_L, color="r", ls=":", lw=1)
    ax.set_xlim(0, max(60, 1.6 * F_L)); ax.set_xlabel("F (T)"); ax.set_ylabel("|FFT| (norm)")
    ax.legend(fontsize=7); ax.set_title(f"run {rid} — 1/B FFT vs $F_L$")
    print("  peaks (F [T], rel amp) by low-B cutoff:")
    for cut, pk in peaks.items():
        print(f"    cut {cut:>5.2f} T: {pk}")
        print(f"        as fraction of F_L: {[round(p0/F_L, 3) for p0, _ in pk]}")

    summary[rid] = dict(label=lab, n=n_cm2, F_L=F_L,
                        onset_b=float(on.onset_b) if on is not None else None,
                        peaks={str(k): v for k, v in peaks.items()},
                        R_range=[float(np.nanmin(R)), float(np.nanmax(R))],
                        fs_max=float(np.nanmax(np.abs(R)) / R_FS),
                        T=[float(T.min()), float(T.max())])
    if on is not None:
        summary[rid]["tones"] = [dict(freq=float(t.freq), onset_b=float(t.onset_b),
                                      censored=bool(t.censored), marginal=bool(t.marginal),
                                      harmonic_of=(float(t.harmonic_of) if t.harmonic_of else None),
                                      delta_f=float(t.delta_f(B.max())))
                                 for t in on.tones]

plt.tight_layout()
plt.savefig(HERE / "spot_checks.png", dpi=110)
print("\n\n=== JSON ===")
print(json.dumps(summary, indent=1))
(HERE / "spot_summary.json").write_text(json.dumps(summary, indent=1))
