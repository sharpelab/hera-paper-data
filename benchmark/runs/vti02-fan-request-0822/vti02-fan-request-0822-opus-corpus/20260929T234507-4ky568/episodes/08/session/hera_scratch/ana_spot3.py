"""Spot checks, careful read: onset (b_lo>0), windowed FFT with peak finding."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from pathlib import Path
from hera.analysis import (open_run, resolve_channels, sdh_onset, sdh_fft,
                           luttinger_frequency, SdhOnsetError)

D = Path("/home/hera/measurements/zack/20260822-vti-02/data")
OUT = Path("/home/hera/measurements/zack/20260822-vti-02/hera_scratch")
SENS = 50e-6


def load(rid):
    r = open_run(D / str(rid))
    B = r.col("magnet_field")
    ch = {c.cid: c for c in resolve_channels(r.meta)}
    I = r.col("sr0_X") / ch["sr0"].gain
    R = np.abs((r.col("sr1_X") / ch["sr1"].gain) / I)
    o = np.argsort(B)
    return B[o], R[o], np.median(np.abs(I))


def peaks(fr, sp, fmin=3.0, top=6):
    idx, _ = find_peaks(sp, height=0.06 * sp.max())
    idx = idx[fr[idx] > fmin]
    idx = idx[np.argsort(sp[idx])[::-1][:top]]
    return sorted(zip(np.round(fr[idx], 1), np.round(sp[idx] / sp.max(), 2)))


for rid, nspot, side in ((6, +3.20, "electron"), (7, -1.20, "hole")):
    B, R, Ib = load(rid)
    F_L = float(luttinger_frequency(nspot * 1e16))
    r_fs = SENS / Ib
    print("=" * 74)
    print(f"RUN {rid} ({side})  n = {nspot:+.2f}e12   F_L = {F_L:.2f} T   R_fs = {r_fs:.0f} Ohm")
    for b_lo in (0.3, 0.5):
        if B.min() > b_lo:
            continue
        try:
            on = sdh_onset(R, B, b_lo=b_lo, r_full_scale=r_fs)
            print(f"  [b_lo={b_lo}] " + on.summary().replace("\n", "\n  "))
        except SdhOnsetError as e:
            print(f"  [b_lo={b_lo}] SdhOnsetError: {str(e)[:200]}")
    print("  --- windowed FFT (bg_degree=5, linear) ---")
    for lo, hi in ((1.0, 7.5), (1.5, 7.5), (2.0, 7.5), (3.0, 7.5),
                   (1.5, 10.0), (3.0, 10.0), (4.0, 10.0), (5.0, 10.0)):
        if lo < B.min() or hi > B.max():
            continue
        fr, sp = sdh_fft(R[:, None], B, b_range=(lo, hi), bg_degree=5, log=False, nfft=2048)
        dF = 1 / (1 / lo - 1 / hi)
        print(f"   {lo:4.1f}-{hi:4.1f} T  dF={dF:5.2f} T  peaks(F,rel): {peaks(fr, sp[0])}")
    print(f"  templates: F_L={F_L:.1f}  ABAB 0.72/0.28 -> {0.72*F_L:.1f}/{0.28*F_L:.1f}")
