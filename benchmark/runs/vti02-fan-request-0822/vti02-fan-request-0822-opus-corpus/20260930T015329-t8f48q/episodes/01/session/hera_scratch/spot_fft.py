"""Spot-check read: runs 6 (electron n=+3.2e12) and 7 (hole n=-1.2e12).
Onset (hera.analysis.sdh_onset) + 1/B FFT vs F_L. Feeds the landau-fan design."""
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_onset, sdh_fft, luttinger_frequency, SdhOnsetError

I_BIAS = 1.0 / 100e6      # drive 1.0 V through 100 MOhm = 10 nA
SR1_GAIN = 1.0            # device card
SENS = 50e-6

def load(fid):
    r = open_run(f"data/{fid}")
    B = r.col("magnet_field")
    Rxx = np.abs(r.col("sr1_X") / SR1_GAIN / I_BIAS)
    Imeas = r.col("sr0_X") / r.meta["measurement_config"]["sr0_gain"]
    return r, B, Rxx, Imeas

cases = [(6, +3.20e12, "electron"), (7, -1.20e12, "hole")]
fig, axes = plt.subplots(2, 3, figsize=(16, 8))

for k, (fid, n_cm2, side) in enumerate(cases):
    r, B, R, Imeas = load(fid)
    FL = luttinger_frequency(abs(n_cm2) * 1e4)   # cm^-2 -> m^-2
    print(f"\n===== run {fid} ({side}, n = {n_cm2:+.2e} cm^-2) =====")
    print(f"  N = {len(B)}, B {B.min():.3f} -> {B.max():.3f} T; "
          f"R {R.min():.1f} / {np.median(R):.1f} / {R.max():.1f} Ohm (min/med/max)")
    print(f"  F_L = {float(FL):.2f} T; R_full_scale = {SENS/I_BIAS:.0f} Ohm "
          f"(R_max = {100*R.max()/(SENS/I_BIAS):.1f} % FS)")
    print(f"  I_meas {Imeas.min():.3e} .. {Imeas.max():.3e} A; T {r.col('T_sample').min():.3f}-{r.col('T_sample').max():.3f} K")
    print(f"  |I_tg| max {np.abs(r.col('k_2400_tg_curr')).max():.2e} A, "
          f"|I_bg| max {np.abs(r.col('k_2400_bg_curr')).max():.2e} A")

    # --- onset
    try:
        on = sdh_onset(R, B, r_full_scale=SENS / I_BIAS)
        print(on.summary())
    except SdhOnsetError as e:
        on = None
        print(f"  SdhOnsetError: {e}")

    # --- raw + background-subtracted
    ax = axes[k, 0]
    ax.plot(B, R, lw=0.8)
    ax.set_xlabel("B (T)"); ax.set_ylabel("Rxx (Ohm)")
    ax.set_title(f"run {fid} raw ({side}, n={n_cm2:+.2f}e12)")
    if on is not None:
        ax.axvline(on.onset_b, color="r", ls="--", lw=0.8)

    ax = axes[k, 1]
    lo = on.onset_b if on is not None else 1.0
    m = (B >= max(lo, 0.5))
    p = np.polyfit(B[m], R[m], 5)
    ax.plot(1.0 / B[m], R[m] - np.polyval(p, B[m]), lw=0.8)
    ax.set_xlabel("1/B (1/T)"); ax.set_ylabel("dRxx (Ohm)")
    ax.set_title(f"run {fid} bg-removed (deg 5, B>{max(lo,0.5):.2f} T)")

    # --- FFT, several windows (stability sweep)
    ax = axes[k, 2]
    b_lo0 = max(lo, 0.5)
    for b_lo, b_hi, style in [(b_lo0, B.max(), "-"),
                              (b_lo0 * 1.5, B.max(), "--"),
                              (b_lo0, B.max() * 0.6, ":")]:
        if b_lo >= b_hi:
            continue
        f, spec = sdh_fft(R[:, None], B, b_range=(b_lo, b_hi), bg_degree=5, log=False)
        s = spec[0]
        ax.plot(f, s / s.max(), style, lw=0.9, label=f"{b_lo:.2f}-{b_hi:.2f} T")
        if style == "-":
            sel = (f > 2) & (f < 3 * float(FL))
            fs, ss = f[sel], s[sel]
            idx = [i for i in range(1, len(ss) - 1) if ss[i] > ss[i-1] and ss[i] > ss[i+1]]
            idx.sort(key=lambda i: -ss[i])
            print("  FFT peaks (main window):")
            for i in idx[:6]:
                print(f"    f = {fs[i]:7.2f} T  amp {ss[i]/ss.max():.3f}  f/F_L = {fs[i]/float(FL):.3f}")
            dF = 1.0 / (1.0 / b_lo - 1.0 / b_hi)
            print(f"  delta_F (record {b_lo:.2f}-{b_hi:.2f} T) = {dF:.2f} T")
    ax.axvline(float(FL), color="k", lw=0.8)
    ax.axvline(0.72 * float(FL), color="g", ls="--", lw=0.8)
    ax.axvline(0.28 * float(FL), color="g", ls="--", lw=0.8)
    ax.set_xlim(0, 2.0 * float(FL))
    ax.set_xlabel("F (T)"); ax.set_ylabel("|FFT| (norm)")
    ax.set_title(f"run {fid} FFT; F_L = {float(FL):.1f} T")
    ax.legend(fontsize=7)

plt.tight_layout()
plt.savefig("hera_scratch/spot_fft.png", dpi=110)
print("\nwrote hera_scratch/spot_fft.png")
