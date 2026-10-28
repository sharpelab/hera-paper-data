"""Spot-check read v2 — restricted to the properly-sampled sub-record.

Runs 6/7 used a coarse low-field leg (50 / 20 mT below 1 T) whose 1/B Nyquist
ceiling is 1.0-2.7 T (run 6) / 2.4-6.5 T (run 7). Every tone the v1 read called
'censored at the 0.30 T edge' lives in that aliased band. Re-read above 1 T,
where d(1/B) <= 0.01-0.02 (Nyquist >= 25 T).
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from hera.analysis import open_run, resolve_channels, sdh_onset, sdh_fft, luttinger_frequency

N_SPOT = {6: +3.20e12, 7: -1.20e12}
SENS = 50e-6

def load(fid):
    r = open_run(f"data/{fid}")
    B = r.col("magnet_field")
    by = {c.cid: c for c in resolve_channels(r.meta)}
    I = r.col("sr0_X") / by["sr0"].gain
    R = (r.col("sr1_X") / by["sr1"].gain) / I
    o = np.argsort(B)
    return B[o], R[o], np.abs(np.median(I))

fig, axes = plt.subplots(2, 2, figsize=(13, 8))
for k, fid in enumerate((6, 7)):
    B, R, Ib = load(fid)
    FL = float(luttinger_frequency(abs(N_SPOT[fid]) * 1e4))
    m = B >= 1.0
    Bw, Rw = B[m], R[m]
    print(f"\n{'='*72}\nrun {fid}  n={N_SPOT[fid]:+.2e}  F_L={FL:.2f} T   "
          f"well-sampled record B=[{Bw.min():.2f},{Bw.max():.2f}] T, N={len(Bw)}")
    try:
        on = sdh_onset(Rw, Bw, b_lo=1.0, r_full_scale=SENS / Ib)
        print(on.summary())
    except Exception as e:
        print("  sdh_onset:", type(e).__name__, e)

    ax = axes[k, 0]
    for c in (1.0, 1.5, 2.0, 2.5, 3.0):
        f, sp = sdh_fft(Rw[:, None], Bw, b_range=(c, 10.0), bg_degree=5, log=False)
        dF = 1.0 / (1.0 / c - 1.0 / 10.0)
        ax.plot(f, sp[0] / sp[0].max(), lw=1.0, label=f"cut {c} T (dF={dF:.1f})")
    ax.axvline(FL, color="k", ls="--", label=f"F_L={FL:.1f} T")
    for frac, lab in ((0.724, "0.72 F_L"), (0.276, "0.28 F_L")):
        ax.axvline(FL * frac, color="r", ls=":", lw=1)
    ax.set_xlim(0, FL * 1.8); ax.set_xlabel("F (T)"); ax.set_ylabel("|FFT| norm")
    ax.legend(fontsize=7); ax.set_title(f"run {fid}: FFT on B>=1 T record")

    # B-window split: low half vs high half in 1/B
    ax = axes[k, 1]
    for lab, br in (("low-B half 1.0-2.0 T", (1.0, 2.0)), ("mid 2-4 T", (2.0, 4.0)),
                    ("high-B half 4-10 T", (4.0, 10.0))):
        f, sp = sdh_fft(Rw[:, None], Bw, b_range=br, bg_degree=3, log=False)
        ax.plot(f, sp[0] / sp[0].max(), lw=1.0, label=lab)
    ax.axvline(FL, color="k", ls="--")
    ax.set_xlim(0, FL * 1.8); ax.set_xlabel("F (T)"); ax.legend(fontsize=7)
    ax.set_title(f"run {fid}: B-window split")

plt.tight_layout(); plt.savefig("hera_scratch/spot_read2.png", dpi=110)
print("\nsaved hera_scratch/spot_read2.png")
