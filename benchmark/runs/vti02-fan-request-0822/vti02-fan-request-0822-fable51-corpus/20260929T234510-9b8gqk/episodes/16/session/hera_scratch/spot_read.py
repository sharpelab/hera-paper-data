"""Spot-check read (sdh-spot-check Verify) on runs 6 (electron, n=+3.2e12) and 7 (hole, n=-1.2e12):
raw R(B), sdh_onset per tone, sdh_fft over several windows, peaks vs F_L. Scratch -> promote to ana."""
import warnings, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, summarize_run, sdh_onset, sdh_fft, SdhOnsetError, luttinger_frequency

HERE = "/home/hera/measurements/zack/20260822-vti-02"
SR0_GAIN = -1e6
SENS = 50e-6; IB = 10e-9; RFS = SENS / IB

def load(rid):
    run = open_run(f"{HERE}/data/{rid}")
    print(summarize_run(run)); print("cols:", run.cols)
    B = run.col("magnet_field"); I = run.col("sr0_X") / SR0_GAIN; V = run.col("sr1_X")
    R = V / I
    T = run.col("T_sample") if "T_sample" in run.cols else None
    o = np.argsort(B); return run, B[o], R[o], I[o], (T[o] if T is not None else None)

def peaks(freqs, spec, fmin=1.0, k=6):
    m = freqs >= fmin
    f, s = freqs[m], spec[m]
    pk, pr = find_peaks(s, prominence=0.05 * s.max())
    order = np.argsort(s[pk])[::-1][:k]
    return [(float(f[p]), float(s[p] / s.max())) for p in pk[order]]

fig, axes = plt.subplots(3, 2, figsize=(14, 12))
for j, (rid, n12) in enumerate([(6, 3.2), (7, -1.2)]):
    print(f"\n================= run {rid}  n = {n12:+.2f}e12 =================")
    run, B, R, I, T = load(rid)
    FL = luttinger_frequency(n12 * 1e16) if callable(luttinger_frequency) else None
    try:
        print(f"F_L = {FL:.2f} T  (h/4e * n)")
    except Exception:
        FL = 4.1357e-15 / 4 * abs(n12) * 1e16 / 1.602e-19 * 1.602e-19  # fallback: h n /(4 e) with n in m^-2 -> T
        FL = 6.62607e-34 * abs(n12) * 1e16 / (4 * 1.602e-19); print(f"F_L = {FL:.2f} T (manual)")
    if T is not None: print(f"T_sample during run: {np.nanmin(T):.3f}-{np.nanmax(T):.3f} K")
    print(f"I_bias {np.median(I)*1e9:.2f} nA; R range {R.min():.1f}-{R.max():.1f} Ohm; max/FS = {R.max()/RFS:.3f}")
    ax = axes[0, j]; ax.plot(B, R, lw=0.7); ax.set_xlabel("B (T)"); ax.set_ylabel("Rxx (Ohm)"); ax.set_title(f"run {rid} raw, n={n12:+.1f}e12, D=0")
    # onset
    try:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            on = sdh_onset(R, B, r_full_scale=RFS, b_lo=0.3)
            for ww in w: print("  warn:", ww.message)
        print(on.summary())
        onset = on.onset_b
    except SdhOnsetError as e:
        print("SdhOnsetError:", e); onset = None
    # background-subtracted trace vs 1/B for the eye
    m = B > 1.0
    cf = np.polyfit(B[m], R[m], 5); dR = R[m] - np.polyval(cf, B[m])
    ax = axes[1, j]; ax.plot(1 / B[m], dR, lw=0.7); ax.set_xlabel("1/B (1/T)"); ax.set_ylabel("dRxx (Ohm), deg-5 bg in B removed (B>1 T)")
    if onset: ax.axvline(1 / onset, color="r", ls="--", label=f"onset {onset:.2f} T"); ax.legend()
    # FFT windows
    ax = axes[2, j]
    wins = [(2.0, 10.0), (3.0, 10.0), (4.0, 10.0), (5.0, 10.0), (3.0, 6.0), (6.0, 10.0)]
    if onset: wins.insert(0, (round(float(onset), 2), 10.0))
    for (lo, hi) in wins:
        mm = (B >= lo) & (B <= hi)
        if mm.sum() < 20: continue
        freqs, spec = sdh_fft(R[mm][:, None], B[mm], b_range=(lo, hi), bg_degree=5, log=False, nfft=4096)
        sp = spec[0]
        dF = 1 / (1 / lo - 1 / hi)
        print(f"  window [{lo:.2f},{hi:.1f}] T  dF={dF:.2f} T  peaks (T, rel):", [(round(f, 1), round(a, 2)) for f, a in peaks(freqs, sp, fmin=max(1.0, 0.5 * dF))])
        ax.plot(freqs, sp / sp.max() + 0.0, lw=0.8, label=f"[{lo:.1f},{hi:.0f}]")
    ax.axvline(FL, color="k", ls=":", label=f"F_L {FL:.1f} T")
    ax.axvline(0.72 * FL, color="gray", ls=":", lw=0.7); ax.axvline(0.28 * FL, color="gray", ls=":", lw=0.7)
    ax.set_xlim(0, 1.6 * FL); ax.set_xlabel("F (T)"); ax.set_ylabel("|FFT| (norm)"); ax.legend(fontsize=7)
fig.tight_layout(); fig.savefig(f"{HERE}/hera_scratch/spot_read.png", dpi=110)
print("saved spot_read.png")
