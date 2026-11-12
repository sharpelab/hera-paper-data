"""Runs 6 + 7 — sdh-spot-check read for the ana notebook: raw first, then onset + FFT ladder + B-window split vs F_L and the model templates.
Ana-notebook body (uses the ana preamble: run(), sdh_fft, luttinger_frequency, np, plt). Executed here standalone for the scratch check."""
import numpy as np, matplotlib.pyplot as plt
from scipy.signal import find_peaks
from hera.analysis import open_run, sdh_onset, sdh_fft, luttinger_frequency
from pathlib import Path

try:
    run  # ana preamble
except NameError:
    _here = Path(__file__).resolve().parent.parent if "__file__" in globals() else Path.cwd()
    def run(i): return open_run(_here / "data" / str(i))

FS_OHM = 50e-6 / 10e-9   # sr1 50 uV / 10 nA = 5 kOhm full scale (both runs)
SPOTS = {6: ("electron", +3.2), 7: ("hole", -1.2)}
# model templates (hera/models/tetralayer_fs_count, u_D = 0): F in T, m*/m_e
MODEL = {6: dict(ABAB=[(7.31, 0.027), (25.78, 0.061)], ABCA=[(33.08, 0.074)]),
         7: dict(ABAB=[(5.86, 0.074), (6.54, 0.032)], ABCA=[(12.41, 1.12)])}

def rxx(r):
    B = r.col("magnet_field"); R = r.col("sr1_X") / (r.col("sr0_X") / -1e6)
    o = np.argsort(B); return B[o], R[o]

def top_peaks(freqs, sp, fmax, k=6):
    m = (freqs > 0.5) & (freqs <= fmax); f, s = freqs[m], sp[m] / sp[m].max()
    pk, _ = find_peaks(s, prominence=0.05)
    return [(round(float(f[i]), 1), round(float(s[i]), 2)) for i in sorted(pk, key=lambda i: -s[i])[:k]]

# ---- 0. raw view, both runs ----
fig, ax = plt.subplots(2, 2, figsize=(13, 7))
for j, rid in enumerate(SPOTS):
    r = run(rid); B, R = rxx(r); side, n12 = SPOTS[rid]
    I = r.col("sr0_X") / -1e6; T = r.col("T_sample")
    ax[0, j].plot(B, R, lw=0.6); ax[0, j].set_title(f"run {rid} raw Rxx — {side} n = {n12:+.1f}e12, D = 0 (sr1 50 uV, {len(B)} pts)")
    ax[0, j].set_xlabel("B (T)"); ax[0, j].set_ylabel("Rxx (Ohm)")
    ax[1, j].plot(B, I * 1e9, lw=0.6, label="I_drain (nA)"); ax[1, j].set_xlabel("B (T)"); ax[1, j].set_ylabel("I (nA)")
    a2 = ax[1, j].twinx(); a2.plot(B, r.col("T_sample"), "r", lw=0.5); a2.set_ylabel("T_sample (K)", color="r")
    print(f"run {rid}: {side} n = {n12:+.1f}e12; B {B.min():.2f}-{B.max():.2f} T; R {R.min():.0f}..{R.max():.0f} Ohm (max {R.max()/FS_OHM:.2f} FS); "
          f"I {I.mean()*1e9:.2f} nA; T {T.min():.3f}-{T.max():.3f} K; TG/BG current med {np.median(r.col('k_2400_tg_curr'))*1e12:+.0f}/{np.median(r.col('k_2400_bg_curr'))*1e12:+.0f} pA")
fig.tight_layout(); plt.show()

# ---- 1. onset + FFT ladder + B-window split ----
fig, ax = plt.subplots(2, 2, figsize=(13, 8))
for j, rid in enumerate(SPOTS):
    r = run(rid); B, R = rxx(r); side, n12 = SPOTS[rid]
    FL = float(luttinger_frequency(abs(n12) * 1e16))
    b_lo = 1.0 if rid == 6 else 0.7          # run 6: 10 mT leg only (the 50 mT leg under-samples the 7 T tone below ~0.85 T)
    on = sdh_onset(R, B, b_lo=b_lo, r_full_scale=FS_OHM)
    print(f"\n=== run {rid} ({side}, n = {n12:+.1f}e12): F_L = {FL:.2f} T; model ABAB {MODEL[rid]['ABAB']}, ABCA {MODEL[rid]['ABCA']} ===")
    print(on.summary())
    m = B >= b_lo; bg = np.polyval(np.polyfit(B[m], R[m], 5), B[m])
    ax[0, j].plot(1 / B[m], R[m] - bg, lw=0.6); ax[0, j].set_xlabel("1/B (1/T)"); ax[0, j].set_ylabel("dRxx (Ohm)")
    ax[0, j].set_title(f"run {rid}: bg-subtracted (deg 5, B > {b_lo} T) vs 1/B")
    wins = [(1.5, 10), (2.0, 10), (3.0, 10), (1.5, 4.0), (4.0, 10)] if rid == 6 else [(1.0, 10), (2.0, 10), (3.0, 10), (1.0, 4.0), (4.0, 10)]
    for lo, hi in wins:
        fr, sp = sdh_fft(R[:, None], B, b_range=(lo, hi), bg_degree=5, nfft=4096)
        dF = 1 / (1 / lo - 1 / hi)
        print(f"  FFT [{lo},{hi}] T  dF = {dF:.2f} T: {top_peaks(fr, sp[0], 2.0 * FL)}")
        if hi == 10: ax[1, j].plot(fr, sp[0] / sp[0].max(), lw=0.8, label=f"[{lo}, {hi}] T, dF {dF:.1f}")
    ax[1, j].axvline(FL, color="k", ls="--", label=f"F_L = {FL:.1f} T")
    for f, _ in MODEL[rid]["ABAB"]: ax[1, j].axvline(f, color="tab:blue", ls=":", lw=1)
    ax[1, j].axvline(MODEL[rid]["ABCA"][0][0], color="tab:red", ls=":", lw=1)
    ax[1, j].set_xlim(0, 2.0 * FL); ax[1, j].set_xlabel("F (T)"); ax[1, j].set_ylabel("|FFT| (norm)"); ax[1, j].legend(fontsize=7)
    ax[1, j].set_title(f"run {rid} FFT ladder — dotted: model ABAB (blue) / ABCA (red)")
fig.tight_layout(); plt.show()
