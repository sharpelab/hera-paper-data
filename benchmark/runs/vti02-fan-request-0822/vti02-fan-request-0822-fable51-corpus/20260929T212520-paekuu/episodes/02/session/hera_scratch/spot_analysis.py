"""sdh-spot-check read on runs 6 (electron, n=+3.2e12) and 7 (hole, n=-1.2e12).
Raw R(B) -> sdh_onset -> sdh_fft, with F_L and model tones overlaid.
"""
import sys, json, warnings
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_onset, sdh_fft, luttinger_frequency, SdhOnsetError

SENS = 50e-6
RUNS = {6: dict(n=3.2e12 * 1e4, label="e-side n=+3.2e12"), 7: dict(n=-1.2e12 * 1e4, label="h-side n=-1.2e12")}
# model tones (1e12 cm^-2 -> T), from the prior instance's Step-2 read (recomputed below by model_tones.py)
MODEL = {6: dict(abab=(7.5, 25.6), abca=33.1), 7: dict(abab=(5.3, 7.1), abca=12.4)}

out = {}
fig, axes = plt.subplots(3, 2, figsize=(13, 11))
for j, (fid, info) in enumerate(RUNS.items()):
    r = open_run(f"data/{fid}")
    B = r.col("magnet_field"); I = r.col("sr0_X") / -1e6; R = r.col("sr1_X") / I
    o = np.argsort(B); B, R, I = B[o], R[o], I[o]
    FL = float(luttinger_frequency(info["n"]))
    rfs = SENS / np.median(np.abs(I))
    ax = axes[0, j]; ax.plot(B, R, lw=0.6); ax.set_title(f"run {fid} raw R(B) — {info['label']}  (FS {rfs:.0f} Ω)"); ax.set_xlabel("B (T)"); ax.set_ylabel("Rxx (Ω)")
    res = dict(FL=FL, rfs=rfs, Rmax=float(R.max()), R0=float(R[np.argmin(abs(B - 0.3))]))
    # onset
    try:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            on = sdh_onset(R, B, r_full_scale=rfs)
        print(f"\n===== run {fid} — {info['label']}  F_L = {FL:.1f} T")
        print(on.summary())
        for ww in w: print("  WARN:", ww.message)
        res["onset_b"] = float(on.onset_b); res["clip_high_b"] = on.clip_high_b
        res["tones"] = [dict(freq=float(t.freq), onset_b=float(t.onset_b), censored=bool(t.censored), marginal=bool(t.marginal),
                             harmonic_of=t.harmonic_of, near_residual=getattr(t, "near_residual", None)) for t in on.tones]
        onset = on.onset_b
    except SdhOnsetError as e:
        print(f"\n===== run {fid}: SdhOnsetError: {e}"); res["onset_error"] = str(e); onset = None
    # bg-subtracted trace (deg-5 in B above 1 T) for the eye
    m = B >= 1.0
    p = np.polyfit(B[m], R[m], 5); dR = R[m] - np.polyval(p, B[m])
    ax = axes[1, j]; ax.plot(1 / B[m], dR, lw=0.6); ax.set_xlabel("1/B (1/T)"); ax.set_ylabel("ΔRxx (Ω), deg-5 bg in B, B≥1 T")
    if onset: ax.axvline(1 / onset, color="r", ls="--", label=f"onset {onset:.2f} T"); ax.legend()
    # FFT over several windows (stability sweep)
    ax = axes[2, j]
    for lo, deg in [((onset or 1.5), 5), ((onset or 1.5) + 0.5, 5), ((onset or 1.5), 3), (max((onset or 1.5), 3.0), 5)]:
        f, sp = sdh_fft(R[:, None], B, b_range=(lo, B.max()), bg_degree=deg, log=False)
        ax.plot(f, sp[0] / sp[0][f > 2].max(), lw=0.8, label=f"B≥{lo:.2f}, deg{deg}")
        if lo == (onset or 1.5) and deg == 5:
            sel = f > 2; pk = f[sel][np.argsort(sp[0][sel])[::-1][:6]]; res["fft_top_peaks_T"] = [float(x) for x in pk]
    for x, c, lab in [(FL, "k", "F_L"), (MODEL[fid]["abab"][0], "g", "ABAB light"), (MODEL[fid]["abab"][1], "g", "ABAB heavy"), (MODEL[fid]["abca"], "m", "ABCA")]:
        ax.axvline(x, color=c, ls=":", lw=1); ax.text(x, 1.02, lab, color=c, fontsize=7, rotation=90, va="bottom")
    ax.set_xlim(0, 1.5 * FL); ax.set_xlabel("F (T)"); ax.set_ylabel("|FFT| (norm)"); ax.legend(fontsize=7)
    # B-window split
    if onset:
        mid = 2 / (1 / onset + 1 / B.max())
        for lo, hi, tag in [(onset, mid, "lowB"), (mid, B.max(), "highB")]:
            f, sp = sdh_fft(R[:, None], B, b_range=(lo, hi), bg_degree=5, log=False)
            sel = f > 2; pk = f[sel][np.argsort(sp[0][sel])[::-1][:4]]
            res[f"split_{tag}"] = dict(win=(float(lo), float(hi)), peaks=[float(x) for x in pk], dF=float(1 / (1 / lo - 1 / hi)))
    out[fid] = res
fig.tight_layout(); fig.savefig("hera_scratch/spot_checks_6_7.png", dpi=110)
json.dump(out, open("hera_scratch/spot_read.json", "w"), indent=1, default=str)
print("\n" + json.dumps(out, indent=1, default=str))
