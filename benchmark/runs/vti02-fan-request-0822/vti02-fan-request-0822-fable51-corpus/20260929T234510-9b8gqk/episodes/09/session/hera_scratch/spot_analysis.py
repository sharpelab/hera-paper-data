"""sdh-spot-check read on runs 6 (electron, n=+3.2e12) and 7 (hole, n=-1.2e12): raw R(B), onset, FFT tones vs F_L."""
import sys, json, warnings
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from hera.analysis import open_run, summarize_run, sdh_onset, sdh_fft, SdhOnsetError, luttinger_frequency

here = Path(__file__).resolve().parent
data = here.parent / "data"
out = {}
fig, axes = plt.subplots(2, 3, figsize=(17, 8))
for row, (rid, n12, sens) in enumerate([(6, 3.2, 50e-6), (7, -1.2, 50e-6)]):
    r = open_run(data / str(rid))
    print(f"\n===== run {rid} =====")
    print(summarize_run(r))
    print("cols:", r.cols)
    B = r.col("magnet_field")
    I = r.col("sr0_X") / -1e6
    R = r.col("sr1_X") / 1.0 / I
    Ib = float(np.nanmedian(I))
    fs = sens / abs(Ib)
    order = np.argsort(B); B, R = B[order], R[order]
    print(f"I_bias med {Ib*1e9:.3f} nA; R range {R.min():.1f} .. {R.max():.1f} Ohm; full-scale R {fs:.0f} Ohm; max frac {np.abs(R).max()/fs:.3f}")
    T = r.col("T_sample"); print(f"T_sample {T.min():.3f}-{T.max():.3f} K")
    try:
        FL = luttinger_frequency(n12 * 1e16)
    except Exception as e:
        FL = 4.1356677e-15 / 4 * abs(n12) * 1e16 / 1  # h/(4e) * n  -> h/e = 4.1357e-15 T m^2
        print("luttinger_frequency fallback:", e)
    print(f"F_L(g=4) = {FL:.2f} T")
    ax = axes[row, 0]; ax.plot(B, R, lw=0.7); ax.set_xlabel("B (T)"); ax.set_ylabel("Rxx sr1 (Ohm)"); ax.set_title(f"run {rid} raw, n={n12:+.1f}e12")
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        try:
            on = sdh_onset(R, B, r_full_scale=fs)
            print(on.summary())
            out[rid] = dict(onset_b=float(on.onset_b), clip_high_b=None if on.clip_high_b is None else float(on.clip_high_b),
                            tones=[dict(freq=float(t.freq), onset_b=float(t.onset_b), censored=bool(t.censored), marginal=bool(t.marginal),
                                        harmonic_of=(None if t.harmonic_of is None else float(t.harmonic_of))) for t in on.tones])
            onset = on.onset_b
        except SdhOnsetError as e:
            print("SdhOnsetError:", e); onset = None; out[rid] = dict(error=str(e))
        for ww in w: print("WARN:", ww.message)
    # FFT at a few cutoffs (stability): onset, onset+0.5, 2.0 T ; also B-window split halves
    bmax = float(B.max())
    cut0 = max(onset or 1.0, float(B.min()) + 0.05)
    ax = axes[row, 1]
    for cut, deg in [(cut0, 5), (cut0 + 0.5, 5), (cut0 + 1.0, 5), (cut0, 3), (cut0, 7)]:
        if cut >= bmax - 1.5: continue
        f, s = sdh_fft(R[:, None], B, b_range=(cut, bmax), bg_degree=deg, log=False, nfft=4096)
        s = s[0] / s[0].max()
        ax.plot(f, s, lw=0.8, label=f"cut {cut:.2f} T deg {deg}")
        pk = f[(s > 0.15) & (np.r_[True, s[1:] > s[:-1]] & np.r_[s[:-1] > s[1:], True])]
        print(f"FFT cut {cut:.2f} deg {deg}: peaks(>15%) at {np.round(pk[pk<3*FL],2)} T ; dF = {1/(1/cut-1/bmax):.2f} T")
    for k, lab in [(1, "F_L"), (0.72, "0.72 F_L"), (0.28, "0.28 F_L")]:
        ax.axvline(k * FL, color="k", ls=":", lw=0.8); ax.text(k * FL, 0.95, lab, rotation=90, fontsize=7, va="top")
    ax.set_xlim(0, 1.6 * FL); ax.set_xlabel("F (T)"); ax.set_title("FFT (norm), stability sweep"); ax.legend(fontsize=6)
    # B-window split
    ax = axes[row, 2]
    mid = 2 / (1 / cut0 + 1 / bmax)  # midpoint in 1/B
    for (a, b, lab) in [(cut0, mid, "low-B half"), (mid, bmax, "high-B half")]:
        f, s = sdh_fft(R[:, None], B, b_range=(a, b), bg_degree=5, log=False, nfft=4096)
        s = s[0] / s[0].max(); ax.plot(f, s, lw=0.8, label=f"{lab} [{a:.2f},{b:.2f}] T")
    for k in (1, 0.72, 0.28): ax.axvline(k * FL, color="k", ls=":", lw=0.8)
    ax.set_xlim(0, 1.6 * FL); ax.set_xlabel("F (T)"); ax.set_title("B-window split (1/B midpoint)"); ax.legend(fontsize=6)
fig.tight_layout(); fig.savefig(here / "spot_67.png", dpi=110)
json.dump(out, open(here / "spot_67.json", "w"), indent=1)
print("\nsaved", here / "spot_67.png")
