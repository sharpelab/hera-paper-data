"""Runs 6/7 (sdh-spot-check e/h sides): raw traces, per-tone onsets, FFT tone content.

Feeds the landau-fan design: B_lo (measured onset), tone set vs F_L, side choice.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_onset, sdh_fft, luttinger_frequency, SdhOnsetError

DIR = "/home/hera/measurements/zack/20260822-vti-02/data"
I_BIAS = 10e-9
FS_OHM = 50e-6 / I_BIAS  # 5 kOhm

runs = {}
for rid, side, n12 in ((6, "electron", 3.2e12 * 1e4), (7, "hole", -1.2e12 * 1e4)):
    run = open_run(f"{DIR}/{rid}")
    print(f"=== run {rid} ({side}) ===")
    print(run.cols)
    B = run.col("magnet_field")
    X = run.col("sr1_X")
    R = X / I_BIAS  # gain 1
    order = np.argsort(B)
    B, R = B[order], R[order]
    FL = luttinger_frequency(n12)
    print(f"n = {n12/1e4:+.2e} cm^-2, F_L = {FL:.1f} T, B {B.min():.2f}->{B.max():.2f} T, {len(B)} pts, R[B~min] {R[:5].mean():.1f} Ohm, Rmax {R.max():.1f}")
    try:
        on = sdh_onset(R, B, r_full_scale=FS_OHM)
        print("onset_b:", on.onset_b)
        for t in on.tones:
            print("  tone:", t)
        if getattr(on, "untracked", None):
            print("  untracked:", on.untracked)
        if getattr(on, "clip_high_b", None):
            print("  CLIP above:", on.clip_high_b)
        onset_b = on.onset_b
    except SdhOnsetError as e:
        print("SdhOnsetError:", e)
        onset_b = None
    runs[rid] = dict(B=B, R=R, FL=FL, onset=onset_b, side=side, n12=n12)

fig, axes = plt.subplots(2, 2, figsize=(13, 8))
for i, rid in enumerate((6, 7)):
    d = runs[rid]
    B, R, FL = d["B"], d["R"], d["FL"]
    ax = axes[i, 0]
    ax.plot(B, R, lw=0.6)
    if d["onset"]:
        ax.axvline(d["onset"], color="r", ls="--", label=f"onset {d['onset']:.2f} T")
        ax.legend()
    ax.set_xlabel("B (T)"); ax.set_ylabel("Rxx (Ohm)")
    ax.set_title(f"run {rid} ({d['side']}, n={d['n12']/1e4:+.1e} cm$^{{-2}}$) raw")
    # FFT above onset
    ax = axes[i, 1]
    blo = d["onset"] if d["onset"] else 1.5
    for b0, lab in ((blo, f"{blo:.2f}-{B.max():.0f} T"),):
        f, spec = sdh_fft(R[:, None], B, b_range=(b0, float(B.max())), nfft=4096, log=False)
        sp = spec[0]
        ax.plot(f, sp / sp.max(), label=lab)
        # top peaks
        from scipy.signal import find_peaks
        pk, props = find_peaks(sp, height=0.03 * sp.max(), distance=10)
        top = sorted(zip(sp[pk], f[pk]), reverse=True)[:8]
        print(f"run {rid} FFT window {b0:.2f}-{B.max():.1f} T, dF_res = {1/(1/b0 - 1/B.max()):.2f} T")
        for a, fr in top:
            print(f"   peak F = {fr:6.2f} T  amp {a/sp.max():.3f}  F/F_L = {fr/FL:.3f}")
    ax.axvline(FL, color="k", ls=":", label=f"F_L {FL:.1f} T")
    ax.set_xlim(0, 2.2 * FL); ax.set_xlabel("F (T)"); ax.set_ylabel("FFT amp (norm)")
    ax.set_title(f"run {rid} SdH FFT"); ax.legend(fontsize=8)
fig.tight_layout()
fig.savefig("/home/hera/measurements/zack/20260822-vti-02/hera_scratch/spot_checks.png", dpi=110)
print("saved spot_checks.png")
