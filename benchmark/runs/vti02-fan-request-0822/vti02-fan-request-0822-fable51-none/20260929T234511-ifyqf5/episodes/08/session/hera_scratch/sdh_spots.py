"""Runs 6 (e-side, n=+3.2e12, 0->10 T) and 7 (h-side, n=-1.2e12, 10->0.3 T): raw R(B), sdh_onset, sdh_fft."""
import numpy as np, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from hera.analysis import open_run, resolve_channels, sdh_onset, sdh_fft, SdhOnsetError, luttinger_frequency
D = Path("data")
fig, ax = plt.subplots(2, 3, figsize=(16, 8))
for k, (rid, lab) in enumerate([(6, "e n=+3.2e12"), (7, "h n=-1.2e12")]):
    r = open_run(D / str(rid)); ch = {c.cid: c for c in resolve_channels(r.meta)}
    B = r.col("magnet_field"); I = r.col("sr0_X") / ch["sr0"].gain
    R = (r.col("sr1_X") / ch["sr1"].gain) / I
    o = np.argsort(B); B, R, I = B[o], R[o], I[o]
    T = r.col("T_sample")[o]
    print(f"\n=== run {rid} {lab}: {len(B)} pts, B {B.min():.2f}-{B.max():.2f} T, R {R.min():.1f}..{R.max():.1f} Ohm, I {I.mean()*1e9:.2f} nA, T {T.min():.3f}-{T.max():.3f} K, interrupted={r.interrupted}")
    ax[k, 0].plot(B, R, lw=0.7); ax[k, 0].set_xlabel("B (T)"); ax[k, 0].set_ylabel("Rxx (Ohm)"); ax[k, 0].set_title(f"run {rid} {lab} raw")
    fs = 50e-6 / 10e-9
    try:
        so = sdh_onset(R, B, b_lo=1.0, r_full_scale=fs)
        print(so.summary())
    except SdhOnsetError as e:
        print("sdh_onset:", e)
    for blo, bhi in [(1.5, 10.0), (3.0, 10.0)]:
        m = (B >= blo) & (B <= bhi)
        f, sp = sdh_fft(R[m][:, None], B[m], b_range=None, bg_degree=5, log=False, nfft=2048)
        sp = sp[0]; sel = (f > 2) & (f < 120)
        pk = f[sel][np.argsort(sp[sel])[::-1][:6]]
        print(f"  FFT {blo}-{bhi} T top peaks (T): {np.round(np.sort(pk),1)}")
        ax[k, 2].plot(f, sp / sp[sel].max(), lw=0.8, label=f"{blo}-{bhi} T")
    ax[k, 2].set_xlim(0, 120); ax[k, 2].set_xlabel("F (T)"); ax[k, 2].legend(); ax[k, 2].set_title("SdH FFT (1/B), bg deg 5")
    # detrended vs 1/B
    m = B >= 1.5
    bg = np.polyval(np.polyfit(B[m], R[m], 5), B[m])
    ax[k, 1].plot(1 / B[m], R[m] - bg, lw=0.7); ax[k, 1].set_xlabel("1/B (1/T)"); ax[k, 1].set_ylabel("dR (Ohm)"); ax[k, 1].set_title("detrended, B>1.5 T")
    n = abs(float(lab.split("=")[1].replace("e12", ""))) * 1e16
    print(f"  F_L(full n, 4-fold) = {luttinger_frequency(n):.1f} T")
fig.tight_layout(); fig.savefig("hera_scratch/sdh_spots.png", dpi=110)
