"""Spot-check read: runs 6 (electron, n=+3.2e12) and 7 (hole, n=-1.2e12), D=0.
Onset, tone set vs F_L, cleaner side -> fan design inputs."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import (open_run, resolve_channels, current_channel,
                           sdh_onset, sdh_fft, luttinger_frequency, SdhOnsetError)

BASE = "/home/hera/measurements/zack/20260822-vti-02/data"

def read(fid, n_e12, sens=50e-6):
    run = open_run(f"{BASE}/{fid}")
    chans = resolve_channels(run.meta)
    cur = current_channel(chans)
    I = np.median(run.col(cur.col) / cur.gain)
    v1 = [c for c in chans if c.col.startswith("sr1")][0]
    print(f"== run {fid}: channels {[c.col for c in chans]}, I (sr0 median) = {I:.3e} A")
    B = run.col("magnet_field")
    R = (run.col(v1.col) / v1.gain) / I
    order = np.argsort(B)
    B, R = B[order], R[order]
    FL = luttinger_frequency(n_e12)
    print(f"n = {n_e12:+.2f}e12 -> F_L = {FL:.1f} T")
    try:
        on = sdh_onset(R, B, r_full_scale=(sens / v1.gain) / I)
        print(on.summary())
    except SdhOnsetError as e:
        print(f"SdhOnsetError: {e}")
        on = None
    return run, B, R, FL, on

r6 = read(6, +3.2)
print()
r7 = read(7, -1.2)

# FFT reads
fig, ax = plt.subplots(2, 3, figsize=(15, 7))
for row, (fid, (run, B, R, FL, on)) in enumerate({6: r6, 7: r7}.items()):
    ax[row, 0].plot(B, R, lw=0.5)
    ax[row, 0].set_title(f"run {fid} raw R_xx(B)")
    ax[row, 0].set_xlabel("B (T)"); ax[row, 0].set_ylabel("R (Ohm)")
    if on is None:
        continue
    cut = on.onset_b
    # background-subtracted view
    m = B >= cut
    p = np.polyfit(B[m], R[m], 5)
    dR = R[m] - np.polyval(p, B[m])
    ax[row, 1].plot(1/B[m], dR, lw=0.5)
    ax[row, 1].set_title(f"run {fid} dR vs 1/B (cut {cut:.2f} T)")
    ax[row, 1].set_xlabel("1/B (1/T)")
    for cutf in (cut, cut*1.2, cut*1.5):
        try:
            freqs, spec = sdh_fft(R[:, None], B, b_range=(cutf, B.max()), bg_degree=5)
            ax[row, 2].plot(freqs, spec[0]/spec[0].max(), lw=0.8, label=f"cut {cutf:.2f} T")
        except Exception as e:
            print(f"run {fid} fft cut {cutf:.2f}: {e}")
    ax[row, 2].axvline(FL, color='k', ls='--', label=f"F_L {FL:.1f} T")
    ax[row, 2].set_xlim(0, 1.6*FL); ax[row, 2].legend(fontsize=7)
    ax[row, 2].set_title(f"run {fid} FFT (norm)")
    ax[row, 2].set_xlabel("F (T)")
fig.tight_layout()
fig.savefig("/home/hera/measurements/zack/20260822-vti-02/hera_scratch/spots_67.png", dpi=110)
print("saved spots_67.png")
