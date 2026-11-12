"""Spot-check read: runs 6 (electron, n=+3.2e12) and 7 (hole, n=-1.2e12).
Onset via sdh_onset, tones via sdh_fft; F_L overlay. Scratch pass."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_onset, sdh_fft, SdhOnsetError, luttinger_frequency

BASE = "/home/hera/measurements/zack/20260822-vti-02/data"
SENS = 50e-6
IBIAS = 10e-9
RFS = SENS / IBIAS  # 5 kOhm

for rid, nn, tag in ((6, 3.2e12, "electron"), (7, -1.2e12, "hole")):
    run = open_run(f"{BASE}/{rid}")
    B = run.col("magnet_field")
    R = run.col("sr1_X") / IBIAS  # gain 1
    # sort ascending in B (run 7 descends)
    idx = np.argsort(B)
    B, R = B[idx], R[idx]
    FL = luttinger_frequency(abs(nn))
    print(f"=== run {rid} ({tag}, n={nn:+.2e}) F_L = {FL:.1f} T ===")
    print(f"B: {B.min():.3f} -> {B.max():.3f} T, {len(B)} pts; R range {R.min():.1f} .. {R.max():.1f} Ohm")
    try:
        on = sdh_onset(R, B, r_full_scale=RFS)
        print(on.summary())
        onset = on.onset_b
    except SdhOnsetError as e:
        print("SdhOnsetError:", e)
        onset = None
    if onset is not None:
        for cut in (onset, onset * 1.3, onset * 1.6):
            freqs, spec = sdh_fft(R[:, None], B, b_range=(cut, B.max()))
            s = spec[0]
            # peak picking: local maxima above median+3*mad in the log spec
            from scipy.signal import find_peaks
            pk, props = find_peaks(s, prominence=(np.nanmax(s) - np.nanmedian(s)) * 0.08)
            top = sorted(pk, key=lambda i: s[i], reverse=True)[:8]
            names = ", ".join(f"{freqs[i]:.1f}T(h{s[i]:.1f})" for i in sorted(top, key=lambda i: freqs[i]))
            print(f"  FFT cut {cut:.2f} T: peaks {names}")
    print()
