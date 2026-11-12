"""Spot-check read: runs 6 (electron, n=+3.2e12) and 7 (hole, n=-1.2e12).

Onset (sdh_onset), tone content (sdh_fft), vs F_L. Feeds the fan design.
"""
import numpy as np
import scipy.constants as cst
import matplotlib.pyplot as plt
from hera.analysis import open_run, sdh_onset, sdh_fft, luttinger_frequency, SdhOnsetError

H, E = cst.h, cst.e


def rxx(run):
    mc = run.meta["measurement_config"]
    g_cur, g_v = mc["sr0_gain"], 1.0
    I = run.col("sr0_X") / g_cur
    V = run.col("sr1_X") / g_v
    B = run.col("magnet_field")
    return B, V / I, I


for rid, n12 in ((6, +3.2), (7, -1.2)):
    r = open_run(f"data/{rid}")
    B, R, I = rxx(r)
    o = np.argsort(B)
    B, R, I = B[o], R[o], I[o]
    n_m2 = abs(n12) * 1e12 * 1e4
    F_L = H / (4 * E) * n_m2
    print(f"\n=========== run {rid}: n = {n12:+.2f}e12 cm^-2, F_L = {F_L:.1f} T ===========")
    print(f"  B {B.min():.3f} -> {B.max():.3f} T, {len(B)} pts; |I_bias| med {np.median(np.abs(I))*1e9:.3f} nA")
    print(f"  R: min {np.min(R):.1f}  max {np.max(R):.1f}  @B=0-ish {R[0]:.1f} Ohm; T {r.col('T_sample').min():.3f}-{r.col('T_sample').max():.3f} K")
    print(f"  |I_tg| max {np.max(np.abs(r.col('k_2400_tg_curr')))*1e12:.0f} pA, |I_bg| max {np.max(np.abs(r.col('k_2400_bg_curr')))*1e12:.0f} pA")
    r_fs = 50e-6 / np.median(np.abs(I))
    print(f"  full scale R (50 uV / I_bias) = {r_fs:.0f} Ohm; max R / FS = {np.max(R)/r_fs:.2%}")

    try:
        on = sdh_onset(R, B, r_full_scale=r_fs)
        print(on.summary())
    except SdhOnsetError as e:
        print(f"  SdhOnsetError: {e}")
        on = None

    # FFT over a few cutoffs to check stability
    for cut in (1.0, 1.5, 2.0, 3.0):
        if cut >= B.max():
            continue
        f, spec = sdh_fft(R[:, None], B, b_range=(cut, B.max()), bg_degree=5, nfft=2048)
        s = spec[0]
        m = f > 2.0
        fi, si = f[m], s[m]
        # top 5 local maxima
        idx = [i for i in range(1, len(si) - 1) if si[i] > si[i - 1] and si[i] > si[i + 1]]
        idx.sort(key=lambda i: -si[i])
        top = [(fi[i], si[i]) for i in idx[:5]]
        dF = 1.0 / (1.0 / cut - 1.0 / B.max())
        print(f"  FFT cut {cut:.1f}-{B.max():.1f} T (dF={dF:.2f} T): "
              + ", ".join(f"{fq:.2f} T ({sv:.1f})" for fq, sv in top)
              + f"  | f/F_L: " + ", ".join(f"{fq/F_L:.3f}" for fq, _ in top))
