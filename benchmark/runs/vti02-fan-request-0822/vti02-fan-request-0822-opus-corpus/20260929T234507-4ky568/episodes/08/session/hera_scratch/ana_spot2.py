"""Spot-check read part 2: raw Rxx(B), onset, FFT vs F_L for runs 6 and 7."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from hera.analysis import (open_run, resolve_channels, sdh_onset, sdh_fft,
                           luttinger_frequency, SdhOnsetError)

D = Path("/home/hera/measurements/zack/20260822-vti-02/data")
OUT = Path("/home/hera/measurements/zack/20260822-vti-02/hera_scratch")

SENS = 50e-6          # sr1 sensitivity, V, both runs (from the measure cells)
runs = [(6, +3.20, "electron"), (7, -1.20, "hole")]

fig, axes = plt.subplots(2, 3, figsize=(16, 8))
res = {}

for k, (rid, nspot, side) in enumerate(runs):
    r = open_run(D / str(rid))
    B = r.col("magnet_field")
    chans = {c.cid: c for c in resolve_channels(r.meta)}
    I = r.col("sr0_X") / chans["sr0"].gain
    V = r.col("sr1_X") / chans["sr1"].gain
    R = np.abs(V / I)
    o = np.argsort(B)
    B, R, I = B[o], R[o], I[o]
    n_si = nspot * 1e12 * 1e4     # cm^-2 -> m^-2
    F_L = float(luttinger_frequency(n_si))
    r_fs = SENS / np.median(np.abs(I))
    print("=" * 70)
    print(f"RUN {rid} ({side}) n={nspot:+.2f}e12  F_L = {F_L:.2f} T")
    print(f"  I_bias median = {np.median(np.abs(I))*1e9:.3f} nA   "
          f"R full-scale = {r_fs:.0f} Ohm")
    print(f"  R range {R.min():.1f} - {R.max():.1f} Ohm   R(B_lo)={R[0]:.1f}  R(B_hi)={R[-1]:.1f}")
    print(f"  clip fraction (R > 0.95 FS): {np.mean(R > 0.95*r_fs):.4f}")
    print(f"  T_sample {r.col('T_sample').min():.3f} - {r.col('T_sample').max():.3f} K")
    itg, ibg = r.col("k_2400_tg_curr"), r.col("k_2400_bg_curr")
    print(f"  |I_tg| max {np.abs(itg).max()*1e12:.1f} pA   |I_bg| max {np.abs(ibg).max()*1e12:.1f} pA")

    ax = axes[k, 0]
    ax.plot(B, R, lw=0.7)
    ax.set_xlabel("B (T)"); ax.set_ylabel("Rxx (Ohm)")
    ax.set_title(f"run {rid} raw: {side} n={nspot:+.2f}e12")

    # onset
    try:
        on = sdh_onset(R, B, r_full_scale=r_fs, b_lo=float(B.min()))
        print("  --- sdh_onset ---")
        print("  " + on.summary().replace("\n", "\n  "))
        onset_b = on.onset_b
    except SdhOnsetError as e:
        print("  SdhOnsetError:", e)
        on, onset_b = None, None

    # background-subtracted trace
    m = B > (onset_b if onset_b else 1.0) * 0.5
    p = np.polyfit(B[m], R[m], 5)
    dR = R[m] - np.polyval(p, B[m])
    ax = axes[k, 1]
    ax.plot(1.0 / B[m], dR, lw=0.7)
    ax.set_xlabel("1/B (1/T)"); ax.set_ylabel("dRxx (Ohm)")
    ax.set_title(f"run {rid} bg-subtracted (deg 5)")

    # FFT over a few cutoffs
    ax = axes[k, 2]
    for cut in (1.0, 1.5, 2.0, 3.0):
        if cut < B.min():
            continue
        fr, sp = sdh_fft(R[:, None], B, b_range=(cut, B.max()), bg_degree=5, log=False)
        s = sp[0]
        ax.plot(fr, s / s.max(), lw=0.8, label=f"cut {cut} T")
        pk = fr[np.argsort(s)[::-1][:6]]
        print(f"  FFT cut {cut}-{B.max():.1f} T: dF = {1/(1/cut - 1/B.max()):.2f} T; "
              f"top peaks (T): {np.round(np.sort(pk[pk>3]), 2)}")
    ax.axvline(F_L, color="k", ls="--", lw=1, label=f"F_L={F_L:.1f} T")
    ax.axvline(0.72 * F_L, color="r", ls=":", lw=1)
    ax.axvline(0.28 * F_L, color="r", ls=":", lw=1)
    ax.set_xlim(0, max(60, 1.4 * F_L)); ax.set_xlabel("F (T)")
    ax.set_title(f"run {rid} FFT  F_L={F_L:.1f} T"); ax.legend(fontsize=7)
    res[rid] = dict(B=B, R=R, F_L=F_L, onset=onset_b, on=on, r_fs=r_fs)

plt.tight_layout()
plt.savefig(OUT / "spot_checks.png", dpi=110)
print("saved", OUT / "spot_checks.png")
