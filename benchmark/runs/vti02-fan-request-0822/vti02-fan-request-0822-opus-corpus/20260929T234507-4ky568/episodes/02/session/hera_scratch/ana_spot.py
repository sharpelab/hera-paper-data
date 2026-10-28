"""Spot-check read: runs 6 (electron n=+3.2e12) and 7 (hole n=-1.2e12).
Onset + FFT tones vs F_L. Sizes the Landau fan."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, resolve_channels, sdh_onset, sdh_fft, luttinger_frequency

N_SPOT = {6: +3.20e12, 7: -1.20e12}   # cm^-2
SENS = 50e-6   # V, sr1 sensitivity both runs

def load(fid):
    r = open_run(f"data/{fid}")
    B = r.col("magnet_field")
    chans = resolve_channels(r.meta)
    by = {c.cid: c for c in chans}
    cur = by["sr0"]
    I = r.col("sr0_X") / cur.gain
    V = r.col("sr1_X") / by["sr1"].gain
    R = V / I
    o = np.argsort(B)
    return r, B[o], R[o], np.abs(np.median(I))

fig, axes = plt.subplots(2, 3, figsize=(16, 8))
out = {}
for k, fid in enumerate((6, 7)):
    r, B, R, Ibias = load(fid)
    n_cm2 = N_SPOT[fid]
    FL = luttinger_frequency(abs(n_cm2) * 1e4)   # n in m^-2
    r_fs = SENS / Ibias
    print(f"\n{'='*70}\nrun {fid}: n = {n_cm2:+.2e} cm^-2, I_bias = {Ibias*1e9:.3f} nA, "
          f"R_fullscale = {r_fs:.0f} Ohm, F_L = {float(FL):.2f} T")
    print(f"  R range {R.min():.1f} .. {R.max():.1f} Ohm; B {B.min():.3f}..{B.max():.3f} T, N={len(B)}")

    ax = axes[k, 0]
    ax.plot(B, R, lw=0.7)
    ax.set_xlabel("B (T)"); ax.set_ylabel("Rxx (Ohm)"); ax.set_title(f"run {fid} raw  n={n_cm2:+.2e}")

    try:
        on = sdh_onset(R, B, r_full_scale=r_fs)
        print(on.summary())
        out[fid] = on
    except Exception as e:
        print("  sdh_onset FAILED:", type(e).__name__, e)
        on = None

    # FFT over a few low-B cutoffs
    ax = axes[k, 1]
    cutoffs = [0.5, 1.0, 1.5, 2.0, 3.0]
    for c in cutoffs:
        if c >= B.max():
            continue
        f, spec = sdh_fft(R[:, None], B, b_range=(c, B.max()), bg_degree=5, log=False)
        s = spec[0]
        ax.plot(f, s / s.max(), lw=0.9, label=f"cut {c} T")
    ax.axvline(float(FL), color="k", ls="--", lw=1, label=f"F_L={float(FL):.1f}")
    ax.set_xlim(0, float(FL) * 2.2)
    ax.set_xlabel("F (T)"); ax.set_ylabel("|FFT| (norm)"); ax.legend(fontsize=7)
    ax.set_title(f"run {fid} FFT vs low-B cutoff")

    # background-subtracted oscillation vs 1/B
    ax = axes[k, 2]
    m = B > 0.4
    p = np.polyfit(B[m], R[m], 5)
    dR = R[m] - np.polyval(p, B[m])
    ax.plot(1 / B[m], dR, lw=0.7)
    ax.set_xlabel("1/B (1/T)"); ax.set_ylabel("dRxx (Ohm)")
    ax.set_title(f"run {fid} bg-subtracted (deg5)")

plt.tight_layout()
plt.savefig("hera_scratch/spot_read.png", dpi=110)
print("\nsaved hera_scratch/spot_read.png")
