"""SdH spot-check read: runs 6 (electron, n=+3.2e12) and 7 (hole, n=-1.2e12).

Per sdh-spot-check Verify: raw trace first, then onset (sdh_onset), then FFT
(sdh_fft) with tone read vs F_L and the fs_count_b0 model tables.
"""
import json
import sys

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from hera.analysis import open_run, sdh_fft, sdh_onset, luttinger_frequency, SdhOnsetError

BASE = "/home/hera/measurements/zack/20260822-vti-02"
SENS = 50e-6  # sr1 sensitivity, V (both runs)

runs = {
    6: dict(n=+3.2e12, label="electron n=+3.2e12"),
    7: dict(n=-1.2e12, label="hole n=-1.2e12"),
}

fig, axes = plt.subplots(2, 2, figsize=(13, 8))

out = {}
for i, (rid, info) in enumerate(runs.items()):
    r = open_run(f"{BASE}/data/{rid}")
    B = r.col("magnet_field")
    # R = V / I with measured drain current: I = sr0_X / sr0_gain (gain -1e6 V/A),
    # sr1 unity gain (device card Notes).
    I = r.col("sr0_X") / (-1e6)
    Rxx = r.col("sr1_X") / I

    order = np.argsort(B)
    Bs, Rs = B[order], Rxx[order]

    ax = axes[0, i]
    ax.plot(Bs, Rs, lw=0.6)
    ax.set_xlabel("B (T)")
    ax.set_ylabel("Rxx (Ohm)")
    ax.set_title(f"run {rid} raw — {info['label']}")

    FL = float(luttinger_frequency(info["n"] * 1e4))  # cm^-2 -> m^-2
    # full-scale R for clip detection: sensitivity / median measured current
    r_fs = SENS / np.median(np.abs(I))
    try:
        onset = sdh_onset(Rs, Bs, r_full_scale=r_fs)
        out[rid] = dict(onset_b=float(onset.onset_b))
        print(f"run {rid}: onset_b = {onset.onset_b:.3f} T")
        for t in onset.tones:
            print("   tone:", t)
    except SdhOnsetError as e:
        print(f"run {rid}: SdhOnsetError: {e}")
        out[rid] = dict(onset_b=None)
        onset = None

    b_lo = out[rid]["onset_b"] or 1.0
    freqs, spec = sdh_fft(Rs.reshape(-1, 1), Bs, b_range=(max(b_lo, 1.0), Bs.max()), nfft=4096)
    sp = spec[0]
    ax2 = axes[1, i]
    ax2.plot(freqs, sp, lw=0.8)
    ax2.axvline(FL, color="k", ls="--", label=f"F_L={FL:.1f} T")
    ax2.axvline(0.72 * FL, color="r", ls=":", label="0.72 F_L")
    ax2.axvline(0.28 * FL, color="g", ls=":", label="0.28 F_L")
    ax2.set_xlim(0, 1.6 * FL)
    ax2.set_xlabel("F (T)")
    ax2.set_ylabel("|FFT|")
    ax2.set_title(f"run {rid} FFT, B in [{max(b_lo,1.0):.2f}, {Bs.max():.1f}] T")
    ax2.legend(fontsize=8)

    # peak list: local maxima above floor
    from scipy.signal import find_peaks
    pk, props = find_peaks(sp, height=np.median(sp) + 4 * sp.std() / 2, distance=8)
    peaks = sorted(zip(freqs[pk], sp[pk]), key=lambda t: -t[1])[:8]
    out[rid]["peaks"] = [(float(f), float(a)) for f, a in peaks]
    out[rid]["F_L"] = FL
    print(f"run {rid}: F_L = {FL:.2f} T; top peaks (F, amp):")
    for f, a in peaks:
        print(f"   {f:7.2f} T   {a:8.3f}   f/F_L = {f/FL:.3f}")

fig.tight_layout()
fig.savefig(f"{BASE}/hera_scratch/spots_read.png", dpi=110)
print(json.dumps(out, indent=1))
